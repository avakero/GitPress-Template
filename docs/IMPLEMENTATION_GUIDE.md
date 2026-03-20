# GitPress セレクタルール実装ガイド

## 🎯 概要

GitPress では、統一されたセレクタルールを使用して、**CSS で全体デザインを一元管理**します。

```
投稿・ページ作成 → セレクタルール適用 → Git管理 → 自動同期 → 統一デザイン
```

---

## 📋 実装フロー

### ステップ 1: テンプレートから開始

```bash
# 新規投稿の場合
cp content/post/_template-post.html content/post/my-new-post.html

# または固定ページの場合
cp content/page/_template-page.html content/page/my-new-page.html
```

### ステップ 2: Front Matter を編集

```yaml
---
post_id: null
post_type: post
slug: "unique-slug"          # URL に使用される
title: "投稿のタイトル"      # WordPress に表示
status: "publish"            # publish / draft / private
date: "2026-03-20T10:00:00+09:00"
taxonomies:
  category:
    - "カテゴリ名"
  post_tag:
    - "タグ1"
---
```

### ステップ 3: セレクタルールに従って HTML を記述

**投稿の例:**

```html
<h2 class="gp-post-h2">見出し</h2>
<p class="gp-post-p">本文段落</p>
<p class="gp-post-intro">導入段落</p>
<section class="gp-post-featured-box">
  <h3 class="gp-post-h3">強調ボックス</h3>
</section>
```

**固定ページの例:**

```html
<h1 class="gp-page-h1">ページタイトル</h1>
<h2 class="gp-page-h2">セクション</h2>
<div class="gp-page-cta">
  <h3 class="gp-page-h3">アクション</h3>
</div>
```

### ステップ 4: Git にコミット＆プッシュ

```bash
git add content/post/my-new-post.html
git commit -m "Add: New blog post title"
git push origin main
```

### ステップ 5: WordPress に自動同期

✅ GitHub Actions が自動実行
✅ WordPress に投稿が作成
✅ セレクタに対応した CSS が自動適用

---

## 🎨 セレクタ一覧（クイックリファレンス）

### 投稿（`.gp-post-*`）

| セレクタ | HTML要素 | 説明 |
|---------|---------|------|
| `.gp-post-h2` | `<h2>` | メインセクション見出し |
| `.gp-post-h3` | `<h3>` | サブセクション見出し |
| `.gp-post-h4` | `<h4>` | 小見出し |
| `.gp-post-p` | `<p>` | 通常の段落 |
| `.gp-post-intro` | `<p class="...">` | 導入段落（大きく目立つ） |
| `.gp-post-featured-box` | `<section class="...">` | 強調・注目ボックス |
| `.gp-post-list` | `<ul>` / `<ol>` | リスト |
| `.gp-post-code` | `<code>` | コード表示 |
| `.gp-post-blockquote` | `<blockquote>` | 引用 |
| `.gp-post-img` | `<img>` | 画像 |

### 固定ページ（`.gp-page-*`）

| セレクタ | HTML要素 | 説明 |
|---------|---------|------|
| `.gp-page-h1` | `<h1>` | ページタイトル |
| `.gp-page-h2` | `<h2>` | セクション見出し |
| `.gp-page-h3` | `<h3>` | サブ見出し |
| `.gp-page-p` | `<p>` | 通常段落 |
| `.gp-page-intro` | `<p class="...">` | 導入段落 |
| `.gp-page-featured-box` | `<section class="...">` | 情報ボックス |
| `.gp-page-cta` | `<div class="...">` | Call-To-Action |
| `.gp-page-list` | `<ul>` / `<ol>` | リスト |

詳細は **[SELECTOR_RULES.md](./SELECTOR_RULES.md)** を参照

---

## 🖼️ 実装例

### 例1: ブログ投稿

```html
---
post_id: null
post_type: post
slug: "docker-basics"
title: "Docker 入門ガイド"
status: "publish"
date: "2026-03-20T15:00:00+09:00"
taxonomies:
  category:
    - "技術"
  post_tag:
    - "Docker"
    - "コンテナ"
---

<article class="gp-post-content">
  <h2 class="gp-post-h2">Docker とは</h2>

  <p class="gp-post-intro">
    Docker はコンテナ化技術です。アプリケーションを独立した環境で実行できます。
  </p>

  <p class="gp-post-p">
    Docker を使うことで、開発環境と本番環境の差異をなくせます。
  </p>

  <section class="gp-post-featured-box">
    <h3 class="gp-post-h3">Docker の主な利点</h3>
    <ul class="gp-post-list">
      <li>環境の再現性が高い</li>
      <li>デプロイが簡単</li>
      <li>スケーリングが容易</li>
    </ul>
  </section>

  <h2 class="gp-post-h2">インストール方法</h2>

  <h3 class="gp-post-h3">Windows / Mac</h3>

  <p class="gp-post-p">
    Docker Desktop をダウンロードしてインストールします。
  </p>

  <pre><code class="gp-post-code">
docker --version
Docker version 20.10.0, build abc123
  </code></pre>

  <h3 class="gp-post-h3">Linux</h3>

  <p class="gp-post-p">
    ターミナルからコマンドでインストールできます。
  </p>

  <h2 class="gp-post-h2">まとめ</h2>

  <p class="gp-post-p">
    Docker は現代的なアプリケーション開発に必須のツールです。
  </p>
</article>
```

### 例2: 企業の「会社概要」ページ

```html
---
post_id: null
post_type: page
slug: "about-company"
title: "会社概要"
status: "publish"
date: "2026-03-20T10:00:00+09:00"
---

<section class="gp-page-content">
  <h1 class="gp-page-h1">会社概要</h1>

  <p class="gp-page-intro">
    弊社は 2020 年に設立された、デジタルソリューション企業です。
  </p>

  <h2 class="gp-page-h2">企業情報</h2>

  <section class="gp-page-featured-box">
    <h3 class="gp-page-h3">基本情報</h3>
    <ul class="gp-page-list">
      <li>会社名: XX株式会社</li>
      <li>設立: 2020年4月</li>
      <li>本社: 東京都渋谷区</li>
      <li>従業員数: 50名</li>
    </ul>
  </section>

  <h2 class="gp-page-h2">私たちのミッション</h2>

  <p class="gp-page-p">
    デジタル技術を通じて、社会に価値を提供することです。
  </p>

  <h2 class="gp-page-h2">サービス</h2>

  <h3 class="gp-page-h3">Web 開発</h3>
  <p class="gp-page-p">カスタム Web アプリケーション開発。</p>

  <h3 class="gp-page-h3">コンサルティング</h3>
  <p class="gp-page-p">デジタル変革のアドバイス。</p>

  <h2 class="gp-page-h2">お問い合わせ</h2>

  <div class="gp-page-cta">
    <h3 class="gp-page-h3">ご相談ください</h3>
    <p class="gp-page-p">
      サービスについてのご質問やご相談は、お気軽にお問い合わせください。
    </p>
  </div>
</section>
```

---

## 🎨 CSS カスタマイズ例

### WordPress カスタム CSS で一括変更

**例1: 見出しの色を変更**

```css
/* すべての投稿の h2 を赤に */
.gp-post-h2 {
  color: #e74c3c !important;
  border-bottom-color: #e74c3c !important;
}
```

**例2: フォントサイズを全体的に大きく**

```css
.gp-post-p, .gp-page-p {
  font-size: 18px !important;
}

.gp-post-h2, .gp-page-h2 {
  font-size: 32px !important;
}
```

**例3: ダーク モード対応**

```css
body.dark-mode .gp-post-p {
  color: #e0e0e0;
  background-color: #1a1a1a;
}
```

---

## ✅ チェックリスト

新規投稿を作成する際の確認事項：

- [ ] テンプレートから開始
- [ ] Front Matter（post_id, slug, title 等）を記入
- [ ] タクソノミー（カテゴリ・タグ）を設定
- [ ] セレクタルールに従った HTML を記述
- [ ] 見出しは `.gp-post-h2`, `.gp-post-h3` など正しいクラスを使用
- [ ] 本文は `.gp-post-p` で囲んだ
- [ ] 強調内容は `.gp-post-featured-box` を使用
- [ ] Git add / commit / push を実行
- [ ] GitHub Actions で同期完了を確認
- [ ] WordPress で表示を確認

---

## 🚀 次のステップ

1. **WordPress でカスタム CSS を設定**
   - 外観 → カスタマイズ → 追加 CSS
   - [SELECTOR_RULES.md](./SELECTOR_RULES.md) の CSS 例を参考に

2. **投稿・ページの作成開始**
   - テンプレートを使用
   - セレクタルール に従う

3. **デザイン調整**
   - CSS を修正するだけで全投稿が更新
   - リアルタイムで変更を確認

---

**セレクタルールに従って、統一されたデザインの投稿を作成していきましょう！** 🎨✨
