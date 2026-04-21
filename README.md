# GitPress - WordPress Git Sync System

Git リポジトリを WordPress コンテンツの唯一の信頼ソース（Source of Truth）とするシステムです。
記事や固定ページを HTML ファイルで管理し、`git push` するだけで WordPress に自動反映されます。

## 特徴

- **Git で一元管理** — 記事・固定ページを HTML + YAML Front Matter で管理
- **自動同期** — `main` ブランチへの push で GitHub Actions が WordPress を自動更新
- **逆方向エクスポート** — WordPress の既存コンテンツを Git にエクスポート可能
- **統一デザイン** — CSS セレクタルールにより全ページのデザインを一括管理
- **ビジュアル AI 編集** — 同梱のプラグイン [GitPress Editor](./wp-plugin/) を入れれば、ブラウザ上で要素をクリックして AI に編集指示できる (DevTools 風)
- **安全運用** — Dry-run モード、競合検知、リトライ機構を搭載

## ディレクトリ構成

```
GitPress-Template/
├── .github/workflows/
│   ├── sync-wordpress.yml      # Git → WordPress 自動同期
│   └── export-wordpress.yml    # WordPress → Git エクスポート
├── content/
│   ├── post/
│   │   └── _template-post.html # 投稿テンプレート
│   └── page/
│       └── _template-page.html # 固定ページテンプレート
├── scripts/
│   ├── sync_wp_content.py      # 同期スクリプト
│   ├── export_wp_content.py    # エクスポートスクリプト
│   ├── generate_manifest.py    # data-edit → YAML マニフェスト生成 (プラグイン用)
│   ├── validate_editables.py   # HTML と YAML の整合性チェック
│   ├── deploy_manifest.py      # YAML → JSON 変換 (プラグイン用)
│   └── requirements.txt
├── config/
│   ├── post_types.yaml         # 投稿タイプ定義
│   └── taxonomies.yaml         # タクソノミー定義
├── wp-plugin/                  # GitPress Editor プラグイン
│   ├── gitpress-editor-*.zip   # WordPress にアップロードする zip
│   ├── README.md               # プラグイン概要
│   └── docs/                   # インストール・使い方
├── docs/                       # 各種ガイド
├── .env.example                # 環境変数テンプレート
└── README.md
```

---

## セットアップ（3ステップ）

### 1. リポジトリを作成

「**Use this template**」ボタンからリポジトリを作成するか、クローンしてください。

```bash
git clone <your-repo-url>
cd GitPress
pip install -r scripts/requirements.txt
```

### 2. WordPress でアプリケーションパスワードを発行

1. WordPress 管理画面 → **ユーザー** → **プロフィール**
2. 「**アプリケーションパスワード**」セクションで名前を入力（例: `GitPress`）
3. 「**新しいアプリケーションパスワードを追加**」をクリック
4. 表示されたパスワードを控える（再表示されません）

> 詳細は [docs/GITHUB_SETUP.md](./docs/GITHUB_SETUP.md) を参照

### 3. GitHub Secrets を設定

GitHub リポジトリの **Settings** → **Secrets and variables** → **Actions** に以下を追加：

| Secret 名 | 値 |
|-----------|-----|
| `WP_BASE_URL` | WordPress サイトの URL（例: `https://example.com`） |
| `WP_USERNAME` | WordPress 管理ユーザー名 |
| `WP_APP_PASSWORD` | 手順2で発行したアプリケーションパスワード |

これで `main` ブランチに push するたびに WordPress が自動更新されます。

---

## 既存 WordPress からの移行

WordPress に既存コンテンツがある場合は、まずエクスポートしてください。

```bash
# 環境変数を設定
cp .env.example .env
# .env を編集して WP_BASE_URL, WP_USERNAME, WP_APP_PASSWORD を入力

# 全コンテンツをエクスポート
python scripts/export_wp_content.py --post-type all

# Git にコミット
git add content/
git commit -m "Import existing WordPress content"
git push origin main
```

---

## 記事の作成・編集

### 新しい投稿を作成

1. `content/post/_template-post.html` をコピーしてリネーム

```bash
cp content/post/_template-post.html content/post/my-new-post.html
```

2. Front Matter とHTML本文を編集

```yaml
---
post_id: null
post_type: post
slug: "my-new-post"
title: "投稿タイトル"
status: "publish"
date: "2026-03-20T10:00:00+09:00"
taxonomies:
  category:
    - "カテゴリ名"
  post_tag:
    - "タグ1"
    - "タグ2"
custom_fields:
  seo_title: "SEOタイトル"
  seo_description: "SEOディスクリプション"
---

<article class="gp-post-content">
  <h2 class="gp-post-h2">見出し</h2>
  <p class="gp-post-p">本文を書きます。</p>
</article>
```

3. コミットして push

```bash
git add content/post/my-new-post.html
git commit -m "Add: 新しい投稿"
git push origin main
```

### 固定ページを作成

`content/page/_template-page.html` をコピーして同様に作成します。

### 投稿ステータスの変更

Front Matter の `status` を変更するだけです。

```yaml
status: "draft"    # 下書き
status: "publish"  # 公開
status: "private"  # 非公開
```

---

## Front Matter フィールド一覧

| フィールド | 説明 | 必須 | 例 |
|----------|------|:----:|-----|
| `post_id` | WordPress 投稿ID（新規は `null`） | ○ | `123` |
| `post_type` | 投稿タイプ | ○ | `post`, `page` |
| `slug` | URL スラッグ | ○ | `"my-post"` |
| `title` | タイトル | ○ | `"記事タイトル"` |
| `status` | ステータス | ○ | `"publish"`, `"draft"` |
| `date` | 公開日時 | ○ | `"2026-03-20T10:00:00+09:00"` |
| `taxonomies` | カテゴリ・タグ | - | 下記参照 |
| `featured_image` | アイキャッチ画像 | - | `source_url: "..."` |
| `custom_fields` | カスタムフィールド（SEO等） | - | `seo_title: "..."` |

---

## CSS セレクタルール

GitPress では統一された CSS セレクタ命名規則を採用しています。
WordPress テーマの CSS にこれらのセレクタを定義することで、全記事に統一デザインが自動適用されます。

### 命名規則

```
.gp-[コンテンツタイプ]-[要素種別]
```

- コンテンツタイプ: `post`（投稿）、`page`（固定ページ）
- 要素種別: `h2`, `p`, `intro`, `featured-box` など

### 投稿用セレクタ（`.gp-post-*`）

| セレクタ | 用途 | HTML例 |
|---------|------|--------|
| `.gp-post-h2` | 第1階層見出し | `<h2 class="gp-post-h2">` |
| `.gp-post-h3` | 第2階層見出し | `<h3 class="gp-post-h3">` |
| `.gp-post-h4` | 第3階層見出し | `<h4 class="gp-post-h4">` |
| `.gp-post-p` | 通常段落 | `<p class="gp-post-p">` |
| `.gp-post-intro` | 導入段落（強調表示） | `<p class="gp-post-intro">` |
| `.gp-post-featured-box` | 強調ボックス | `<section class="gp-post-featured-box">` |
| `.gp-post-list` | リスト | `<ul class="gp-post-list">` |
| `.gp-post-blockquote` | 引用 | `<blockquote class="gp-post-blockquote">` |
| `.gp-post-code` | コードブロック | `<pre><code class="gp-post-code">` |
| `.gp-post-img` | 画像 | `<img class="gp-post-img">` |

### 固定ページ用セレクタ（`.gp-page-*`）

| セレクタ | 用途 | HTML例 |
|---------|------|--------|
| `.gp-page-h1` | ページタイトル | `<h1 class="gp-page-h1">` |
| `.gp-page-h2` | セクション見出し | `<h2 class="gp-page-h2">` |
| `.gp-page-h3` | サブ見出し | `<h3 class="gp-page-h3">` |
| `.gp-page-p` | 通常段落 | `<p class="gp-page-p">` |
| `.gp-page-intro` | 導入段落（強調表示） | `<p class="gp-page-intro">` |
| `.gp-page-featured-box` | 情報ボックス | `<section class="gp-page-featured-box">` |
| `.gp-page-cta` | 行動喚起（CTA） | `<div class="gp-page-cta">` |
| `.gp-page-list` | リスト | `<ul class="gp-page-list">` |

### ネストルール

ボックス内の子要素にはルールがあります：

```html
<!-- featured-box 内 → クラスを明示する -->
<section class="gp-post-featured-box">
  <h3 class="gp-post-h3">見出し</h3>
  <p class="gp-post-p">説明文</p>
</section>

<!-- blockquote 内 → 素の <p> でOK（CSSコンテキストセレクタで適用） -->
<blockquote class="gp-post-blockquote">
  <p>引用テキスト</p>
</blockquote>

<!-- list 内 → 素の <li> でOK -->
<ul class="gp-post-list">
  <li>項目1</li>
  <li>項目2</li>
</ul>
```

### CSS 実装例（WordPress テーマに追加）

```css
/* ── 共通ベース ── */
.gp-post-content,
.gp-page-content {
  max-width: 780px;
  margin: 0 auto;
  font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", sans-serif;
  line-height: 1.8;
  color: #2d3748;
}

/* ── 投稿：見出し ── */
.gp-post-h2 {
  font-size: 1.6rem;
  font-weight: 700;
  color: #2b6cb0;
  border-bottom: 3px solid #4299e1;
  padding-bottom: 0.4rem;
  margin: 2.5rem 0 1.2rem;
}

.gp-post-h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c5282;
  border-left: 4px solid #4299e1;
  padding-left: 0.8rem;
  margin: 2rem 0 1rem;
}

/* ── 投稿：本文 ── */
.gp-post-p {
  margin: 1rem 0;
  font-size: 1rem;
}

.gp-post-intro {
  font-size: 1.1rem;
  color: #4a5568;
  background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
  border-radius: 8px;
  padding: 1.2rem 1.5rem;
  margin: 1.5rem 0;
}

/* ── 投稿：強調ボックス ── */
.gp-post-featured-box {
  background: linear-gradient(135deg, #ebf8ff 0%, #e2e8f0 100%);
  border-left: 5px solid #4299e1;
  border-radius: 8px;
  padding: 1.5rem;
  margin: 2rem 0;
}

/* ── 投稿：引用 ── */
.gp-post-blockquote {
  border-left: 4px solid #a0aec0;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  background: #f7fafc;
  font-style: italic;
  color: #4a5568;
}

/* ── 固定ページ：見出し ── */
.gp-page-h2 {
  font-size: 1.6rem;
  font-weight: 700;
  color: #276749;
  border-bottom: 3px solid #48bb78;
  padding-bottom: 0.4rem;
  margin: 2.5rem 0 1.2rem;
}

/* ── 固定ページ：CTA ── */
.gp-page-cta {
  background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
  border: 2px solid #48bb78;
  border-radius: 12px;
  padding: 2rem;
  margin: 2rem 0;
  text-align: center;
}

/* ── レスポンシブ ── */
@media (max-width: 768px) {
  .gp-post-content,
  .gp-page-content {
    padding: 0 1rem;
  }
  .gp-post-h2, .gp-page-h2 { font-size: 1.3rem; }
  .gp-post-h3, .gp-page-h3 { font-size: 1.1rem; }
}
```

上記 CSS を WordPress テーマの「**追加CSS**」またはテーマの `style.css` に貼り付けると、GitPress で作成した全記事に統一デザインが適用されます。

> 完全な CSS 仕様は [docs/SELECTOR_RULES.md](./docs/SELECTOR_RULES.md) を参照してください。

---

## ビジュアル AI 編集 (GitPress Editor プラグイン)

Git 管理の利便性を保ちつつ、**ブラウザから直接コンテンツを編集**したい場合は同梱プラグインをインストールします。Chrome DevTools のように要素をクリックし、Google Gemini に「赤くして」「もっと元気な文面に」と指示するだけで、変更が WordPress DB と Git の両方に反映されます。

### 仕組み

- HTML 内の `data-edit` 属性を持つ要素だけが編集対象 (AI の暴走を構造的に防止)
- 編集ルール (許可 CSS / 許可クラス) は YAML マニフェストで宣言
- プラグインは 2 層でマニフェストを読み込む:
  1. **バンドル baseline** — 参照サイト `pixelcraft` 用、zip に同梱
  2. **サイト固有オーバーライド** — `wp-content/uploads/gitpress-manifests/*.json`

自サイトの HTML 構造に合わせてマニフェストを自動生成するためのツール群を `scripts/` に同梱しています。

### インストールと導入手順

```bash
# (1) プラグインを WordPress にインストール
#     wp-plugin/gitpress-editor-0.7.0.zip を管理画面からアップロード
#     → docs/INSTALL.md 参照

# (2) 自サイトの HTML に data-edit 属性を付与
#     例: <h1 data-edit="home.hero.title">ようこそ</h1>

# (3) HTML からマニフェスト (YAML) を自動生成
pip install -r scripts/requirements.txt
python scripts/generate_manifest.py --html-dir content/page

# (4) 整合性チェック
python scripts/validate_editables.py --html-dir content/page --yaml-dir content/page/editables

# (5) YAML を JSON に変換
python scripts/deploy_manifest.py --yaml-dir content/page/editables --out-dir ./dist-manifests

# (6) 生成された JSON を WordPress の wp-content/uploads/gitpress-manifests/ に配置
#     (FTP / SSH / rsync など)
```

導入後は、WP 管理者または編集者でログインし、任意のページを開いて右下の鉛筆ボタンをタップすれば編集開始できます。

詳しくは:

- [wp-plugin/README.md](./wp-plugin/README.md) — プラグイン概要
- [wp-plugin/docs/INSTALL.md](./wp-plugin/docs/INSTALL.md) — インストール詳細
- [wp-plugin/docs/USAGE.md](./wp-plugin/docs/USAGE.md) — 操作方法

---

## スクリプト

### sync_wp_content.py — Git → WordPress 同期

```bash
python scripts/sync_wp_content.py              # 全コンテンツを同期
python scripts/sync_wp_content.py --dry-run    # プレビューのみ（変更なし）
python scripts/sync_wp_content.py --skip-new   # 既存投稿のみ更新
```

### export_wp_content.py — WordPress → Git エクスポート

```bash
python scripts/export_wp_content.py --post-type all    # 全て
python scripts/export_wp_content.py --post-type post   # 投稿のみ
python scripts/export_wp_content.py --post-type page   # 固定ページのみ
```

### generate_manifest.py — マニフェスト生成 (プラグイン用)

```bash
# 指定ディレクトリ内の *.html を走査し、data-edit 属性から YAML を生成
python scripts/generate_manifest.py --html-dir content/page

# 出力先を明示
python scripts/generate_manifest.py --html-dir my-site --out-dir my-site/editables
```

### validate_editables.py — 整合性チェック

```bash
# 任意サイトの HTML と YAML の 1:1 対応を検証
python scripts/validate_editables.py --html-dir content/page --yaml-dir content/page/editables
```

### deploy_manifest.py — YAML → JSON 変換

```bash
python scripts/deploy_manifest.py --yaml-dir content/page/editables --out-dir ./dist-manifests
```

生成された JSON を WordPress の `wp-content/uploads/gitpress-manifests/` に配置すると、プラグインが次回ページ読み込み時に自動検出します。

---

## 安全な運用のために

- **Dry-run を活用** — 本番反映前に `--dry-run` で変更内容を必ず確認
- **WordPress 側の直接編集は避ける** — Git が唯一の信頼ソースです。WP側の編集は次回同期で上書きされます
- **ブランチ戦略を活用** — 大きな変更は feature ブランチで作業し、PR レビュー後に main へマージ

> 詳しいワークフローは [docs/WORKFLOW.md](./docs/WORKFLOW.md) を参照

---

## ドキュメント

| ガイド | 内容 |
|-------|------|
| [GitHub セットアップ](./docs/GITHUB_SETUP.md) | Secrets 設定、Actions の確認方法 |
| [セレクタルール仕様](./docs/SELECTOR_RULES.md) | CSS セレクタの完全な一覧と実装例 |
| [実装ガイド](./docs/IMPLEMENTATION_GUIDE.md) | 記事作成の詳細手順とチェックリスト |
| [ワークフロー](./docs/WORKFLOW.md) | ブランチ戦略、PR レビュー、チーム運用 |
| [Xserver ガイド](./docs/XSERVER_GUIDE.md) | Xserver 環境での設定手順 |

---

## トラブルシューティング

| エラー | 原因と対処 |
|-------|-----------|
| `WP_BASE_URL ... are required` | `.env` または GitHub Secrets が未設定 |
| `API Error (401)` | アプリケーションパスワードが不正。WP管理画面で再発行 |
| `API Error (404)` | WP_BASE_URL が間違っている、または REST API が無効 |
| `[WARN] Possible conflict` | WP側で直接編集あり。Git の内容で上書きされます |

---

## ライセンス

MIT
