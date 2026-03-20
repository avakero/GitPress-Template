# GitHub リポジトリセットアップガイド

このガイドでは、GitPress を GitHub から自動実行する手順を説明します。

## 前提条件

- GitHub にリポジトリを作成済み
- WordPress REST API が有効
- WordPress 管理ユーザーが存在

## ステップ 1: WordPress アプリケーションパスワードを生成

WordPress 管理画面で REST API 用の安全なパスワードを生成します。

### 手順

1. WordPress 管理画面にログイン
2. **ユーザー** → **あなたのプロフィール** へ移動
3. ページ下部の **アプリケーション** セクションに移動
4. **アプリケーション名** に `GitPress` と入力
5. **新規アプリケーションパスワードを生成** をクリック
6. 生成されたパスワード（例：`abc1 def2 ghi3 jkl4 mno5`）をコピー

⚠️ **重要**：このパスワードは一度だけ表示されます。必ずコピーして安全に保管してください。

## ステップ 2: GitHub Repository Secrets を設定

GitPress の自動同期に必要な認証情報を GitHub Secrets に登録します。

### 手順

1. GitHub リポジトリを開く
2. **Settings** → **Secrets and variables** → **Actions** をクリック
3. **New repository secret** をクリック
4. 以下の 3 つの Secret を追加：

### Secret 1: WP_BASE_URL

| 項目 | 値 |
|------|-----|
| **Name** | `WP_BASE_URL` |
| **Value** | `https://example.com` |

例：
- ✅ `https://example.com`
- ✅ `https://blog.example.com`
- ❌ `https://example.com/` （末尾のスラッシュなし）

### Secret 2: WP_USERNAME

| 項目 | 値 |
|------|-----|
| **Name** | `WP_USERNAME` |
| **Value** | WordPress の管理ユーザー名 |

例：
- ✅ `admin`
- ✅ `wordpress_user`

### Secret 3: WP_APP_PASSWORD

| 項目 | 値 |
|------|-----|
| **Name** | `WP_APP_PASSWORD` |
| **Value** | ステップ 1 で生成したパスワード |

例：
- ✅ `abc1 def2 ghi3 jkl4 mno5`

---

## ステップ 3: リポジトリをセットアップ

```bash
cd GitPress

# リポジトリの初期化
git init

# GitHub をリモートとして追加
git remote add origin https://github.com/YOUR_USERNAME/GitPress.git

# main ブランチを作成
git branch -m main

# すべてのファイルをステージング
git add .

# 初期コミット
git commit -m "Initialize GitPress"

# main ブランチに push
git push -u origin main
```

---

## ステップ 4: 動作確認

### 自動実行の確認

1. GitHub リポジトリを開く
2. **Actions** タブをクリック
3. **Sync WordPress Content** ワークフローを確認
4. 緑色のチェックマークが表示されれば成功

### 失敗した場合

1. ワークフロー実行をクリック
2. **Sync WordPress Content** ジョブを展開
3. エラーメッセージを確認

**よくあるエラー：**

| エラー | 対策 |
|--------|------|
| `401 Unauthorized` | WP_USERNAME または WP_APP_PASSWORD が間違っている |
| `Failed to connect to WordPress API` | WP_BASE_URL が間違っている、または REST API が無効 |
| `Connection timeout` | WordPress サーバーが応答していない |

---

## ステップ 5: ローカル動作確認（オプション）

```bash
# .env ファイルを作成
cp .env.example .env

# .env を編集（GitHub Secrets と同じ値を入力）
# WP_BASE_URL=https://example.com
# WP_USERNAME=admin
# WP_APP_PASSWORD=abc1 def2 ghi3 jkl4 mno5

# 依存ライブラリをインストール
pip install -r scripts/requirements.txt

# Dry run で確認
python scripts/sync_wp_content.py --dry-run

# 本番実行
python scripts/sync_wp_content.py
```

---

## セキュリティベストプラクティス

### ✅ 推奨事項

- **アプリケーションパスワード** を使用（汎用パスワードではなく）
- **Secrets** は絶対に Git にコミットしない
- **定期的にパスワードをローテーション**
- **ログを監視** して不正アクセスがないか確認

### ❌ してはいけないこと

- パスワードやトークンを `.env` にコミット
- 認証情報を コード内に硬コードする
- Secrets を出力ログに表示
- 複数人で汎用パスワードを共有

---

## トラブルシューティング

### REST API が見つからない

```
error: REST API endpoint /wp-json/wp/v2/posts not found
```

**対策：**

1. WordPress 管理画面 → **設定** → **パーマリンク** を開く
2. **カスタム構造** を選択してから保存
3. REST API を確認：`https://example.com/wp-json/wp/v2/posts`

### アプリケーションパスワードが作成できない

WordPress 5.6 以降が必要です。バージョンを確認してください。

```
WordPress バージョン: 設定 → サイトヘルス → テスト → WordPress Version
```

### GitHub Actions が実行されない

1. `.github/workflows/sync-wordpress.yml` が `main` ブランチに存在するか確認
2. ファイルのシンタックスが正しいか確認（YAML フォーマット）
3. GitHub Actions が有効になっているか確認（Settings → Actions）

---

## 高度な設定

### 自動実行スケジュール（毎日実行など）

`.github/workflows/sync-wordpress.yml` を編集：

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # 毎日 9:00 UTC に実行
  push:
    branches: [main]
```

### 特定のパスのみ同期

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'content/post/**'  # post ディレクトリのみ
```

### 複数の WordPress サイトに同期

複数の `.env` ファイルを作成し、ワークフローで切り替え：

```yaml
strategy:
  matrix:
    site: [site1, site2]
env:
  WP_BASE_URL: ${{ secrets[format('WP_BASE_URL_{0}', matrix.site)] }}
  WP_USERNAME: ${{ secrets[format('WP_USERNAME_{0}', matrix.site)] }}
  WP_APP_PASSWORD: ${{ secrets[format('WP_APP_PASSWORD_{0}', matrix.site)] }}
```

---

## サポート

問題が発生した場合：

1. GitHub Actions のログを確認
2. ローカルで `python scripts/sync_wp_content.py` を実行して再現
3. エラーメッセージをネットで検索
4. リポジトリの Issues で報告
