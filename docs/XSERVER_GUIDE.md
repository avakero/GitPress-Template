# Xserver × GitPress セットアップガイド

Xserver の WordPress を GitPress で管理するための詳細ガイドです。

## Xserver の特徴と対応

Xserver の WordPress は以下の特徴があります：

- **管理画面**: `https://example.com/wp-admin/`
- **REST API**: `https://example.com/wp-json/wp/v2/`
- **セキュリティ**: SSL 対応、自動バックアップ

## ステップ 1: Xserver の管理画面にアクセス

### URL

```
https://www.xserver.ne.jp/
```

### ログイン

1. **Xserver アカウント** でログイン
2. **サーバーパネル** をクリック

## ステップ 2: WordPress の REST API を有効化

Xserver の WordPress はデフォルトで REST API が有効ですが、確認しましょう。

### 確認方法

```bash
# ブラウザで以下にアクセス
https://example.com/wp-json/wp/v2/posts?per_page=1
```

JSON が返されれば REST API は有効です。

### REST API が応答しない場合

1. WordPress 管理画面 → **設定** → **パーマリンク**
2. **デフォルト** 以外を選択（例：**投稿名**）
3. **変更を保存** をクリック

## ステップ 3: アプリケーションパスワードを生成

### 手順

1. WordPress 管理画面（`https://example.com/wp-admin/`）にログイン
2. **ユーザー** メニューから **あなたのプロフィール** をクリック
3. ページを下にスクロールして **アプリケーション** セクションを探す
4. **アプリケーション名** に `GitPress` と入力
5. **新規アプリケーションパスワードを生成** をクリック
6. 生成されたパスワードをコピー

⚠️ **重要**：
- このパスワードは二度と表示されません
- GitHub Secrets に登録する前にメモ帳にコピー
- 他人に見られないように注意

## ステップ 4: GitHub Secrets を設定

### Settings 画面を開く

1. GitHub リポジトリの **Settings** をクリック
2. 左メニューから **Secrets and variables** → **Actions** をクリック

### Secret を追加

**Secret 1: WP_BASE_URL**
- Name: `WP_BASE_URL`
- Value: `https://example.com` （Xserver のドメイン）

例：
```
https://example.com
https://blog.example.com
https://example.jp
```

末尾にスラッシュは付けません。

**Secret 2: WP_USERNAME**
- Name: `WP_USERNAME`
- Value: Xserver の WordPress 管理ユーザー名

通常は `admin` ですが、セキュリティ強化のため異なる場合があります。

**Secret 3: WP_APP_PASSWORD**
- Name: `WP_APP_PASSWORD`
- Value: ステップ 3 で生成したパスワード

例：
```
abc1 def2 ghi3 jkl4 mno5
```

## ステップ 5: 接続テスト

### ローカルでテスト

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/GitPress.git
cd GitPress

# Python 環境をセットアップ
pip install -r scripts/requirements.txt

# .env ファイルを作成
cp .env.example .env

# .env を編集（GitHub Secrets と同じ値）
# WP_BASE_URL=https://example.com
# WP_USERNAME=admin
# WP_APP_PASSWORD=abc1 def2 ghi3 jkl4 mno5
```

### 接続を確認

```bash
python -c "
import requests
import os
from dotenv import load_dotenv

load_dotenv()
base_url = os.getenv('WP_BASE_URL')
username = os.getenv('WP_USERNAME')
app_password = os.getenv('WP_APP_PASSWORD')

url = f'{base_url}/wp-json/wp/v2/posts?per_page=1'
response = requests.get(url, auth=(username, app_password), timeout=10)

print(f'Status Code: {response.status_code}')
if response.status_code == 200:
    print('✓ 接続成功！')
else:
    print(f'✗ エラー: {response.text}')
"
```

成功すれば以下が表示されます：
```
Status Code: 200
✓ 接続成功！
```

## ステップ 6: GitHub Actions を実行

### 初期実行

```bash
# 既存の WordPress 投稿をエクスポート
python scripts/export_wp_content.py --post-type all

# コミット & Push
git add content/
git commit -m "Initialize: Export existing WordPress content"
git push origin main
```

### GitHub Actions の動作確認

1. GitHub リポジトリの **Actions** タブをクリック
2. **Sync WordPress Content** ワークフローを確認
3. 緑色のチェックマークが表示されれば成功

## よくあるトラブル

### エラー：401 Unauthorized

```
error: Got response code 401 when accessing https://example.com/wp-json/...
```

**原因**：認証情報が間違っている

**対策**：
1. `WP_USERNAME` を確認（通常は `admin`）
2. `WP_APP_PASSWORD` が正しくコピーされているか確認
3. パスワード内の空白が削除されていないか確認（`abc1 def2 ghi3...` のスペースは必要）

### エラー：Connection timeout

```
error: Connection timeout while connecting to https://example.com/wp-json/...
```

**原因**：Xserver の WordPress が応答していない

**対策**：
1. WordPress 管理画面が開けるか確認
2. WP_BASE_URL が正しいか確認（`https://` で始まる、末尾に `/` なし）
3. Xserver の SSL 設定を確認

### エラー：404 Not Found

```
error: 404 Not Found: /wp-json/wp/v2/posts
```

**原因**：REST API が有効になっていない

**対策**：
1. WordPress 管理画面 → **設定** → **パーマリンク**
2. **デフォルト** 以外を選択（例：**投稿名**）
3. **変更を保存** をクリック
4. 再度テスト

## Xserver 管理画面での確認

同期後、WordPress に記事が反映されているか確認：

1. **Xserver サーバーパネル** にアクセス
2. **WordPress 簡単インストール** をクリック
3. 該当のドメイン右側の **管理画面 URL** をクリック
4. WordPress 管理画面で投稿を確認

または直接 URL でアクセス：
```
https://example.com/wp-admin/
```

## セキュリティ設定（推奨）

### IP アドレス制限

GitHub Actions は以下のレンジから実行されます：
```
*.github.com (AWS IP range)
```

Xserver の IP 制限機能を利用する場合：
1. サーバーパネル → **アクセス制限** → **.htaccess 編集**
2. GitHub Actions の IP を許可（または制限を外す）

### SSL 証明書

Xserver は自動的に Let's Encrypt の SSL 証明書をインストールします。
WP_BASE_URL は必ず **https://** で始まるようにしてください。

### ファイアウォール

WordPress には `wp-json/` 配下のアクセス制限を避けてください。
GitPress は REST API を使用しているため、ブロックするとエラーになります。

## バックアップ

Xserver は自動バックアップ機能を提供しています：

1. サーバーパネル → **自動バックアップ**
2. バックアップ周期を確認（デフォルト：毎日）
3. 必要に応じて手動バックアップを実行

**推奨**：GitPress 導入前に手動バックアップを実行

```
サーバーパネル → 自動バックアップ → バックアップ
```

## サポート

### Xserver サポート

- **電話サポート**: 24時間対応（有料プランのみ）
- **メールサポート**: 24時間以内に返信
- **チャットサポート**: 営業時間中のみ

### GitPress サポート

- GitHub Issues で問題を報告
- README.md のトラブルシューティングを参照
