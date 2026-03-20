#!/usr/bin/env python3
"""
WordPress Content Export Script
WordPressの既存投稿をGit形式（HTML + Front Matter）にエクスポート
初期導入時に一度実行して、既存コンテンツをGit管理下に置く
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin
import html

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

class WordPressExporter:
    """WordPressからコンテンツをエクスポート"""

    def __init__(self):
        """初期化：環境変数からWordPress接続情報を取得"""
        self.base_url = os.getenv('WP_BASE_URL', '').rstrip('/')
        self.username = os.getenv('WP_USERNAME', '')
        self.app_password = os.getenv('WP_APP_PASSWORD', '')
        self.timeout = int(os.getenv('WP_TIMEOUT', '30'))

        if not all([self.base_url, self.username, self.app_password]):
            logger.error("Error: WP_BASE_URL, WP_USERNAME, WP_APP_PASSWORD are required")
            sys.exit(1)

        self.session = requests.Session()
        self.session.auth = (self.username, self.app_password)
        self.session.headers.update({'User-Agent': 'GitPress/1.0'})

    def api_request(self, endpoint: str, params: Dict = None) -> Optional[List[Dict]]:
        """WordPress REST API でコンテンツを取得"""
        url = urljoin(self.base_url, f'/wp-json/wp/v2/{endpoint}')
        all_items = []

        page = 1
        while True:
            try:
                query_params = {'per_page': 100, 'page': page}
                if params:
                    query_params.update(params)

                response = self.session.get(url, params=query_params, timeout=self.timeout)
                response.raise_for_status()

                items = response.json()
                if not items:
                    break

                all_items.extend(items)

                # ページネーション情報をチェック
                total_pages = response.headers.get('X-WP-TotalPages')
                if total_pages:
                    total_pages = int(total_pages)
                    if page >= total_pages:
                        break
                else:
                    # ヘッダーがない場合、少ないアイテム数 = 最後のページ
                    if len(items) < query_params['per_page']:
                        break

                page += 1

            except requests.RequestException as e:
                logger.error(f"Request Error: {e}")
                return None

        return all_items

    def get_taxonomy_terms(self, post_id: int, post_type: str) -> Dict[str, List[str]]:
        """投稿のタクソノミー情報を取得"""
        taxonomies = {}

        # カテゴリを取得
        categories = self.api_request(
            'categories',
            {'post': post_id, 'hide_empty': False}
        )
        if categories:
            category_names = [cat.get('name') for cat in categories if 'name' in cat]
            if category_names:
                taxonomies['category'] = category_names

        # タグを取得
        if post_type == 'post':
            tags = self.api_request(
                'tags',
                {'post': post_id, 'hide_empty': False}
            )
            if tags:
                tag_names = [tag.get('name') for tag in tags if 'name' in tag]
                if tag_names:
                    taxonomies['post_tag'] = tag_names

        return taxonomies

    def get_custom_fields(self, post_id: int) -> Dict:
        """投稿のカスタムフィールド（meta）を取得"""
        custom_fields = {}

        try:
            meta_response = self.session.get(
                urljoin(self.base_url, f'/wp-json/wp/v2/posts/{post_id}?_fields=meta'),
                timeout=self.timeout
            )

            if meta_response.status_code == 200:
                meta_data = meta_response.json().get('meta', {})
                if meta_data:
                    custom_fields = meta_data

        except requests.RequestException as e:
            logger.warning(f"Failed to get custom fields for post {post_id}: {e}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Invalid JSON in custom fields response for post {post_id}: {e}")

        return custom_fields

    def get_featured_image_info(self, featured_media_id: int) -> Optional[Dict]:
        """アイキャッチ画像の情報を取得"""
        if not featured_media_id:
            return None

        try:
            # api_request() returns List[Dict], but single-item endpoint returns one object
            # Use direct request for single media item
            response = self.session.get(
                urljoin(self.base_url, f'/wp-json/wp/v2/media/{featured_media_id}'),
                timeout=self.timeout
            )

            if response.status_code == 200:
                media = response.json()
                if media and isinstance(media, dict):
                    return {
                        'source_url': media.get('source_url', ''),
                        'alt_text': media.get('alt_text', '')
                    }
        except requests.RequestException as e:
            logger.warning(f"Failed to get featured image {featured_media_id}: {e}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Invalid JSON in media response for {featured_media_id}: {e}")

        return None

    def export_post(self, post: Dict, post_type: str, output_dir: Path) -> bool:
        """単一の投稿をHTML + Front Matter 形式でエクスポート"""
        try:
            post_id = post['id']
            slug = post.get('slug', f'post-{post_id}')

            # ファイル名を生成（slugまたはIDベース）
            filename = f"{slug}.html"
            file_path = output_dir / filename

            # Front Matter を構築
            front_matter_dict = {
                'post_id': post_id,
                'post_type': post_type,
                'slug': slug,
                'title': html.unescape(post.get('title', {}).get('rendered', 'Untitled')),
                'status': post.get('status', 'publish'),
                'date': post.get('date', datetime.now().isoformat()),
                'modified': post.get('modified', datetime.now().isoformat()),
            }

            # タクソノミーを追加
            taxonomies = self.get_taxonomy_terms(post_id, post_type)
            if taxonomies:
                front_matter_dict['taxonomies'] = taxonomies
            else:
                front_matter_dict['taxonomies'] = {}

            # アイキャッチを追加
            featured_media_id = post.get('featured_media')
            if featured_media_id:
                featured_image_info = self.get_featured_image_info(featured_media_id)
                if featured_image_info:
                    front_matter_dict['featured_image'] = featured_image_info

            # カスタムフィールドを追加
            custom_fields = self.get_custom_fields(post_id)
            if custom_fields:
                front_matter_dict['custom_fields'] = custom_fields

            # HTML 本文を抽出
            html_content = post.get('content', {}).get('rendered', '')

            # frontmatter オブジェクトを作成して保存
            post_obj = frontmatter.Post(html_content)
            post_obj.metadata = front_matter_dict

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post_obj))

            logger.info(f"Exported: {filename} (post_id={post_id})")
            return True

        except (IOError, OSError) as e:
            logger.error(f"File write error exporting post {post.get('id')}: {e}")
            return False
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Data error exporting post {post.get('id')}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error exporting post {post.get('id')}: {e}", exc_info=True)
            return False

    def run(self, post_type: str = 'post'):
        """指定の投稿タイプをすべてエクスポート"""
        # 出力ディレクトリを作成
        output_dir = Path(__file__).parent.parent / 'content' / post_type
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Fetching {post_type} posts from WordPress...")

        # WordPressから投稿を取得
        # REST API エンドポイントは複数形を使用
        endpoint = f"{post_type}s" if not post_type.endswith('s') else post_type
        posts = self.api_request(
            endpoint,
            {'per_page': 100, 'status': 'any'}
        )

        if not posts:
            logger.warning(f"No {post_type} posts found or API error")
            return False

        success_count = 0
        error_count = 0

        logger.info(f"Exporting {len(posts)} {post_type} posts...")

        for post in posts:
            if self.export_post(post, post_type, output_dir):
                success_count += 1
            else:
                error_count += 1

        logger.info(f"\n--- Export Summary ({post_type}) ---")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {error_count}")
        logger.info(f"Output directory: {output_dir}")

        return error_count == 0

def main():
    """メインエントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Export WordPress content to Git format (HTML + Front Matter)'
    )
    parser.add_argument(
        '--post-type',
        default='post',
        help='Post type to export (default: post, use "page" or "all")'
    )

    args = parser.parse_args()

    exporter = WordPressExporter()

    if args.post_type == 'all':
        # post と page の両方をエクスポート
        success = True
        for pt in ['post', 'page']:
            logger.info(f"\n{'='*50}")
            logger.info(f"Exporting {pt}...")
            logger.info(f"{'='*50}")
            success = exporter.run(pt) and success
        sys.exit(0 if success else 1)
    else:
        success = exporter.run(args.post_type)
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
