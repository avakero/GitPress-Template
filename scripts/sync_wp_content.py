#!/usr/bin/env python3
"""
WordPress Content Sync Script
Git上のHTML+Front Matterファイルを自動的にWordPressに同期
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from io import BytesIO

import requests
import frontmatter
from dotenv import load_dotenv

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数をロード
load_dotenv()


def pluralize_post_type(post_type: str) -> str:
    """投稿タイプをREST APIエンドポイント用の複数形に変換"""
    if post_type.endswith('s'):
        return post_type
    return f"{post_type}s"


class WordPressSync:
    """WordPress REST API との同期を管理するクラス"""

    def __init__(self, dry_run: bool = False, skip_new: bool = False):
        """初期化：環境変数からWordPress接続情報を取得"""
        self.base_url = os.getenv('WP_BASE_URL', '').rstrip('/')
        self.username = os.getenv('WP_USERNAME', '')
        self.app_password = os.getenv('WP_APP_PASSWORD', '')
        self.timeout = int(os.getenv('WP_TIMEOUT', '30'))
        self.retries = int(os.getenv('WP_RETRIES', '3'))
        self.dry_run = dry_run
        self.skip_new = skip_new

        if not all([self.base_url, self.username, self.app_password]):
            logger.error("Error: WP_BASE_URL, WP_USERNAME, WP_APP_PASSWORD are required")
            sys.exit(1)

        self.session = requests.Session()
        self.session.auth = (self.username, self.app_password)
        self.session.headers.update({'User-Agent': 'GitPress/1.0'})

        # タクソノミーIDキャッシュ
        self.taxonomy_cache = {}

        # メディアURLキャッシュ（重複アップロード防止）
        self.media_cache = {}

        # WordPress ドメイン（SSRF防止用）
        self._wp_domain = urlparse(self.base_url).netloc

    def api_request(self, method: str, endpoint: str, **kwargs) -> Optional[Any]:
        """WordPress REST API へのリクエスト"""
        url = urljoin(self.base_url, f'/wp-json/wp/v2/{endpoint}')

        # Dry run モードでは書き込み系は実行しない
        if self.dry_run and method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            logger.info(f"[DRY RUN] {method} {endpoint} would be executed (not actually sent)")
            return {'id': 0, 'dry_run': True}

        for attempt in range(self.retries):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                if response.status_code >= 400:
                    logger.error(f"API Error ({response.status_code}): {response.text[:500]}")
                    if attempt < self.retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None

                try:
                    return response.json()
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Invalid JSON response from {endpoint}: {e}")
                    return None

            except requests.Timeout:
                logger.error(f"Request timeout (attempt {attempt+1}/{self.retries}): {url}")
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except requests.ConnectionError as e:
                logger.error(f"Connection error (attempt {attempt+1}/{self.retries}): {e}")
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except requests.RequestException as e:
                logger.error(f"Request error (attempt {attempt+1}/{self.retries}): {e}")
                return None

        return None

    def get_post_by_slug(self, post_type: str, slug: str) -> Optional[Dict]:
        """スラッグから投稿を取得"""
        endpoint = pluralize_post_type(post_type)
        result = self.api_request(
            'GET',
            endpoint,
            params={'slug': slug, 'per_page': 1, 'status': 'any'}
        )

        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        return None

    def get_post_by_id(self, post_type: str, post_id: int) -> Optional[Dict]:
        """IDから投稿を取得"""
        endpoint = pluralize_post_type(post_type)
        return self.api_request('GET', f'{endpoint}/{post_id}')

    def get_existing_post(self, post_type: str, front_matter: Dict) -> Optional[Dict]:
        """既存投稿を取得（post_id優先、なければslug）"""
        post_id = front_matter.get('post_id')

        if post_id:
            return self.get_post_by_id(post_type, post_id)

        slug = front_matter.get('slug')
        if slug:
            return self.get_post_by_slug(post_type, slug)

        return None

    def check_conflict(self, existing_post: Dict, front_matter: Dict) -> bool:
        """WP側の変更による競合をチェック（警告ログを出力）"""
        if not existing_post or 'modified_gmt' not in existing_post:
            return False

        wp_modified = datetime.fromisoformat(
            existing_post['modified_gmt'].replace('Z', '+00:00')
        )

        git_modified_str = front_matter.get('modified')
        if not git_modified_str:
            return False

        try:
            git_modified = datetime.fromisoformat(git_modified_str)
        except ValueError:
            return False

        # タイムゾーン情報を統一（naive → UTC aware）
        if wp_modified.tzinfo is None:
            wp_modified = wp_modified.replace(tzinfo=timezone.utc)
        if git_modified.tzinfo is None:
            git_modified = git_modified.replace(tzinfo=timezone.utc)

        if wp_modified > git_modified:
            logger.warning(
                f"[WARN] Possible conflict on post_id={existing_post.get('id')} "
                f"(slug={existing_post.get('slug')}):\n"
                f"  WP modified: {existing_post['modified_gmt']}\n"
                f"  Git modified: {git_modified_str}\n"
                f"  → Git の内容で上書きします。WP側の変更が失われている可能性があります。"
            )
            return True

        return False

    def _taxonomy_endpoint(self, taxonomy_slug: str) -> str:
        """タクソノミースラッグをREST APIエンドポイントに変換"""
        mapping = {
            'category': 'categories',
            'post_tag': 'tags',
        }
        return mapping.get(taxonomy_slug, taxonomy_slug)

    def resolve_taxonomy_ids(self, post_type: str, taxonomies: Dict[str, List[str]]) -> Dict[str, List[int]]:
        """タクソノミーの名前をIDに解決"""
        result = {}

        for taxonomy_slug, terms in taxonomies.items():
            ids = []
            endpoint = self._taxonomy_endpoint(taxonomy_slug)

            for term_name in terms:
                cache_key = f"{taxonomy_slug}:{term_name}"
                if cache_key in self.taxonomy_cache:
                    ids.append(self.taxonomy_cache[cache_key])
                    continue

                # WP側でタームを検索
                term_data = self.api_request(
                    'GET',
                    endpoint,
                    params={'search': term_name, 'per_page': 100}
                )

                term_id = None
                if term_data and isinstance(term_data, list):
                    for term in term_data:
                        if term.get('name') == term_name or term.get('slug') == term_name:
                            term_id = term['id']
                            break

                # タームが見つからなければ作成
                if not term_id:
                    created = self.api_request(
                        'POST',
                        endpoint,
                        json={'name': term_name}
                    )
                    if created and 'id' in created:
                        term_id = created['id']
                        logger.info(f"Created taxonomy term: {taxonomy_slug}/{term_name} (ID={term_id})")

                if term_id:
                    ids.append(term_id)
                    self.taxonomy_cache[cache_key] = term_id

            # タクソノミーキーをWP REST API 形式に
            if taxonomy_slug == 'category':
                result['categories'] = ids
            elif taxonomy_slug == 'post_tag':
                result['tags'] = ids
            else:
                result[taxonomy_slug] = ids

        return result

    def upload_featured_image(self, image_url: str, alt_text: str = '') -> Optional[int]:
        """画像をWPメディアにアップロードしてIDを返す"""
        if image_url in self.media_cache:
            return self.media_cache[image_url]

        # Dry run モードではアップロードしない
        if self.dry_run:
            logger.info(f"[DRY RUN] Would upload featured image: {image_url}")
            return 0

        # SSRF防止: WordPressドメインのURLのみ許可
        parsed = urlparse(image_url)
        if parsed.netloc and parsed.netloc != self._wp_domain:
            logger.warning(f"Skipping image from external domain: {parsed.netloc} (only {self._wp_domain} allowed)")
            return None

        try:
            response = self.session.get(image_url, timeout=self.timeout)
            response.raise_for_status()

            filename = image_url.split('/')[-1] or 'image.jpg'

            files = {
                'file': (filename, BytesIO(response.content), response.headers.get('content-type', 'image/jpeg'))
            }

            media_response = self.session.post(
                urljoin(self.base_url, '/wp-json/wp/v2/media'),
                files=files,
                headers={'Alt-Text': alt_text} if alt_text else {},
                timeout=self.timeout
            )

            if media_response.status_code >= 400:
                logger.error(f"Failed to upload image: {media_response.text[:300]}")
                return None

            media_data = media_response.json()
            media_id = media_data.get('id')

            if media_id:
                self.media_cache[image_url] = media_id
                logger.info(f"Uploaded featured image: {filename} (ID={media_id})")
                return media_id

        except requests.RequestException as e:
            logger.error(f"Error uploading image {image_url}: {e}")

        return None

    def sync_post(self, file_path: Path, post_type: str) -> bool:
        """単一の投稿ファイルを同期"""
        # テンプレートファイルはスキップ
        if file_path.name.startswith('_'):
            logger.info(f"Skipping template file: {file_path.name}")
            return True

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            front_matter = post.metadata
            html_content = post.content

            # Front Matter バリデーション
            required_fields = ['title', 'slug', 'status']
            for field in required_fields:
                if field not in front_matter:
                    logger.error(f"Missing required field '{field}' in {file_path}")
                    return False

            # 既存投稿を検索
            post_id = front_matter.get('post_id')
            slug = front_matter.get('slug')
            existing_post = None

            if not post_id:
                existing_post = self.get_post_by_slug(post_type, slug)
                if not existing_post and self.skip_new:
                    logger.warning(
                        f"[SKIP] New post {file_path.name} (slug={slug}) skipped due to --skip-new flag."
                    )
                    return True
            else:
                existing_post = self.get_post_by_id(post_type, post_id)

            # 競合チェック
            if existing_post:
                self.check_conflict(existing_post, front_matter)

            # タクソノミーを解決
            taxonomies = front_matter.get('taxonomies', {})
            taxonomy_ids = self.resolve_taxonomy_ids(post_type, taxonomies)

            # アイキャッチ画像を処理
            featured_media = None
            featured_image_meta = front_matter.get('featured_image', {})
            if featured_image_meta and featured_image_meta.get('source_url'):
                media_id = self.upload_featured_image(
                    featured_image_meta['source_url'],
                    featured_image_meta.get('alt_text', '')
                )
                if media_id:
                    featured_media = media_id

            # 投稿データを構築
            post_data = {
                'title': front_matter['title'],
                'slug': front_matter['slug'],
                'content': html_content,
                'status': front_matter.get('status', 'publish'),
            }

            # date は新規作成時のみ設定（更新時はWP側の値を維持）
            if front_matter.get('date') and not existing_post:
                post_data['date'] = front_matter['date']

            post_data.update(taxonomy_ids)

            if featured_media:
                post_data['featured_media'] = featured_media

            custom_fields = front_matter.get('custom_fields', {})
            if custom_fields:
                post_data['meta'] = custom_fields

            # 投稿を作成または更新
            endpoint = pluralize_post_type(post_type)
            if existing_post:
                existing_id = existing_post['id']
                # 既存投稿の更新にはPOSTを使用（WP REST APIはPOST/{id}で更新をサポート）
                result = self.api_request('POST', f'{endpoint}/{existing_id}', json=post_data)
                action = "updated"
            else:
                result = self.api_request('POST', endpoint, json=post_data)
                action = "created"

            if result and 'id' in result:
                logger.info(f"Post {action}: {file_path.name} (ID={result['id']}, slug={front_matter['slug']})")
                return True
            else:
                logger.error(f"Failed to {action} post: {file_path.name}")
                return False

        except (IOError, OSError) as e:
            logger.error(f"File read error {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error syncing {file_path}: {e}", exc_info=True)
            return False

    def run(self, files: Optional[List[str]] = None):
        """コンテンツファイルを同期（filesが指定されていればそのファイルのみ）"""
        content_dir = Path(__file__).parent.parent / 'content'

        if not content_dir.exists():
            logger.error(f"Content directory not found: {content_dir}")
            sys.exit(1)

        success_count = 0
        error_count = 0

        if files:
            # 指定ファイルのみ同期
            logger.info(f"Incremental sync: {len(files)} file(s)")
            repo_root = Path(__file__).parent.parent
            for file_rel in files:
                file_path = repo_root / file_rel
                if not file_path.exists() or not file_path.suffix == '.html':
                    logger.warning(f"Skipping non-existent or non-HTML file: {file_rel}")
                    continue
                # content/<post_type>/<file>.html からpost_typeを取得
                try:
                    post_type = file_path.relative_to(content_dir).parts[0]
                except (ValueError, IndexError):
                    logger.warning(f"Skipping file outside content dir: {file_rel}")
                    continue

                logger.info(f"Processing: {file_path.relative_to(content_dir)}")
                if self.sync_post(file_path, post_type):
                    success_count += 1
                else:
                    error_count += 1
        else:
            # 全ファイル同期（フォールバック）
            logger.info("Full sync: processing all content files")
            for post_type_dir in content_dir.iterdir():
                if not post_type_dir.is_dir():
                    continue

                post_type = post_type_dir.name

                for html_file in sorted(post_type_dir.rglob('*.html')):
                    logger.info(f"Processing: {html_file.relative_to(content_dir)}")

                    if self.sync_post(html_file, post_type):
                        success_count += 1
                    else:
                        error_count += 1

        logger.info(f"\n--- Summary ---")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {error_count}")

        return error_count == 0


def main():
    """メインエントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Sync Git content to WordPress'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without actually updating WordPress'
    )
    parser.add_argument(
        '--skip-new',
        action='store_true',
        help='Skip new posts (only update existing ones). Useful for initial verification.'
    )
    parser.add_argument(
        '--files',
        nargs='*',
        help='Specific files to sync (e.g. content/post/my-post.html). If omitted, syncs all.'
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No changes will be made to WordPress")
        logger.info("=" * 60)

    sync = WordPressSync(dry_run=args.dry_run, skip_new=args.skip_new)
    success = sync.run(files=args.files if args.files else None)

    if args.dry_run:
        logger.info("\n" + "=" * 60)
        logger.info("DRY RUN COMPLETE - Review the output above")
        logger.info("=" * 60)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
