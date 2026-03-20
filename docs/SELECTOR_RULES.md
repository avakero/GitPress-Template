# GitPress セレクタ命名ルール仕様書

## 📌 概要

GitPress では、すべての投稿・固定ページで統一されたセレクタ命名ルールを採用します。

このルールに従うことで：
- ✅ デザインの統一性を保証
- ✅ CSS で全体デザインを一括管理
- ✅ 記事追加時に自動的に統一されたスタイルが適用
- ✅ テーマカスタマイズ時に全投稿に反映

---

## 🎨 セレクタ命名ルール

### 基本形式

```
.gp-[コンテンツタイプ]-[要素種別]
```

#### コンテンツタイプ
- `post` = ブログ投稿
- `page` = 固定ページ

#### 要素種別
- `h1`, `h2`, `h3`, `h4` = 見出し
- `p` = 段落
- `intro` = 導入段落
- `featured-box` = 強調ボックス
- `code` = コード
- `list` = リスト
- `blockquote` = 引用

---

## 📋 投稿用セレクタ（Post）

### 見出し

| セレクタ | HTML | 用途 |
|---------|------|------|
| `.gp-post-h1` | `<h1>` | 投稿タイトル（通常は title で自動） |
| `.gp-post-h2` | `<h2>` | 第一階層の見出し |
| `.gp-post-h3` | `<h3>` | 第二階層の見出し |
| `.gp-post-h4` | `<h4>` | 第三階層の見出し |

### 本文要素

| セレクタ | HTML | 用途 |
|---------|------|------|
| `.gp-post-p` | `<p>` | 通常の段落テキスト |
| `.gp-post-intro` | `<p class="gp-post-intro">` | 導入段落（太字・大きめ） |
| `.gp-post-featured-box` | `<section class="gp-post-featured-box">` | 強調・抜き出しボックス |
| `.gp-post-code` | `<pre><code class="gp-post-code">` | コード表示 |
| `.gp-post-blockquote` | `<blockquote class="gp-post-blockquote">` | 引用 |
| `.gp-post-list` | `<ul class="gp-post-list">` or `<ol>` | リスト（全般） |

### 画像

| セレクタ | HTML | 用途 |
|---------|------|------|
| `.gp-post-img` | `<img class="gp-post-img">` | 投稿内画像 |
| `.gp-post-img-large` | `<img class="gp-post-img gp-post-img-large">` | 大きめ表示 |

---

## 📄 固定ページ用セレクタ（Page）

### 見出し

| セレクタ | HTML | 用途 |
|---------|------|------|
| `.gp-page-h1` | `<h1>` | ページタイトル |
| `.gp-page-h2` | `<h2>` | 第一階層 |
| `.gp-page-h3` | `<h3>` | 第二階層 |

### 本文要素

| セレクタ | HTML | 用途 |
|---------|------|------|
| `.gp-page-p` | `<p>` | 通常段落 |
| `.gp-page-intro` | `<p class="gp-page-intro">` | 導入段落 |
| `.gp-page-featured-box` | `<section class="gp-page-featured-box">` | 情報ボックス |
| `.gp-page-cta` | `<div class="gp-page-cta">` | Call-to-Action |
| `.gp-page-list` | `<ul class="gp-page-list">` | リスト |

---

## 📝 HTML テンプレート例

### 投稿の HTML

```html
---
post_id: null
post_type: post
slug: "example-post"
title: "例の投稿"
status: "publish"
date: "2026-03-20T10:00:00+09:00"
---

<article class="gp-post-content">
  <h2 class="gp-post-h2">第一章：導入</h2>

  <p class="gp-post-intro">
    これは導入段落です。通常の段落より目立つスタイルが適用されます。
  </p>

  <p class="gp-post-p">
    通常の段落テキスト。本文のメインコンテンツはこのクラスを使用します。
  </p>

  <section class="gp-post-featured-box">
    <h3 class="gp-post-h3">重要なポイント</h3>
    <p class="gp-post-p">このセクションは強調されます。注目すべき情報をここに記載します。</p>
  </section>

  <h2 class="gp-post-h2">第二章：詳細</h2>

  <p class="gp-post-p">さらに詳しい説明。</p>

  <h3 class="gp-post-h3">コード例</h3>

  <pre><code class="gp-post-code">git add content/post/
git commit -m "Add post"
git push origin main
</code></pre>

  <blockquote class="gp-post-blockquote">
    <p>引用文はこのセレクタで囲みます。</p>
  </blockquote>

  <h3 class="gp-post-h3">リスト例</h3>

  <ul class="gp-post-list">
    <li>項目1</li>
    <li>項目2</li>
    <li>項目3</li>
  </ul>

  <img src="https://example.com/image.jpg" alt="説明" class="gp-post-img">
</article>
```

### 固定ページの HTML

```html
---
post_id: null
post_type: page
slug: "about"
title: "このサイトについて"
status: "publish"
---

<section class="gp-page-content">
  <h1 class="gp-page-h1">このサイトについて</h1>

  <p class="gp-page-intro">
    サイト概要を簡潔に説明します。
  </p>

  <h2 class="gp-page-h2">セクション1</h2>

  <p class="gp-page-p">本文テキスト。</p>

  <section class="gp-page-featured-box">
    <h3 class="gp-page-h3">情報ボックス</h3>
    <p class="gp-page-p">重要な情報をハイライト。</p>
  </section>

  <h2 class="gp-page-h2">セクション2</h2>

  <p class="gp-page-p">続きのテキスト。</p>

  <ul class="gp-page-list">
    <li>項目A</li>
    <li>項目B</li>
    <li>項目C</li>
  </ul>

  <div class="gp-page-cta">
    <h3 class="gp-page-h3">アクション</h3>
    <p class="gp-page-p">何かアクションを促すセクション。</p>
  </div>
</section>
```

---

## 🎨 CSS の実装例

### WordPress カスタム CSS（管理画面）

WordPress **外観** → **カスタマイズ** → **追加 CSS** に以下を記述：

```css
/* ========================================
   GitPress セレクタ定義 - グローバルスタイル
   v2.0 - Modern & Clean Design
   ======================================== */

/* ----------------------------------------
   共通ベース
   ---------------------------------------- */
.gp-post-content,
.gp-page-content {
  max-width: 780px;
  margin: 0 auto;
  padding: 0 20px;
  font-family: "Noto Sans JP", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
  color: #2d3748;
  word-break: break-word;
}

/* ========================================
   投稿用スタイル (.gp-post-*)
   ======================================== */

/* --- 見出し --- */
.gp-post-h2 {
  font-size: 1.625rem;
  font-weight: 700;
  color: #1a202c;
  margin: 48px 0 20px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #ebf4ff 0%, #f0f7ff 100%);
  border-left: 4px solid #4299e1;
  border-radius: 0 6px 6px 0;
  line-height: 1.4;
}

.gp-post-h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2d3748;
  margin: 36px 0 14px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
  line-height: 1.4;
}

.gp-post-h4 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #4a5568;
  margin: 28px 0 10px;
  padding-left: 12px;
  border-left: 3px solid #cbd5e0;
  line-height: 1.4;
}

/* --- 本文 --- */
.gp-post-p {
  font-size: 1rem;
  line-height: 1.9;
  color: #2d3748;
  margin-bottom: 20px;
  letter-spacing: 0.02em;
}

.gp-post-intro {
  font-size: 1.1rem;
  font-weight: 500;
  line-height: 1.9;
  color: #2d3748;
  background-color: #f7fafc;
  padding: 20px 24px;
  border-left: 4px solid #4299e1;
  border-radius: 0 8px 8px 0;
  margin: 24px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

/* --- 強調ボックス --- */
.gp-post-featured-box {
  background: linear-gradient(135deg, #fff5f5 0%, #fffaf0 100%);
  border: 1px solid #fed7d7;
  border-left: 5px solid #fc8181;
  padding: 24px 28px;
  margin: 32px 0;
  border-radius: 0 10px 10px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.gp-post-featured-box .gp-post-h3 {
  color: #c53030;
  margin-top: 0;
  padding-bottom: 10px;
  border-bottom-color: #feb2b2;
}

.gp-post-featured-box .gp-post-p:last-child {
  margin-bottom: 0;
}

/* --- コード --- */
.gp-post-code {
  display: block;
  background-color: #1a202c;
  color: #e2e8f0;
  padding: 20px 24px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: "JetBrains Mono", "Fira Code", "Source Code Pro", "Menlo", monospace;
  font-size: 0.875rem;
  line-height: 1.7;
  tab-size: 2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  margin: 8px 0 24px;
}

/* pre のリセット（コードブロックの余白を統一） */
pre:has(.gp-post-code) {
  margin: 24px 0;
  padding: 0;
  background: none;
}

/* --- 引用 --- */
.gp-post-blockquote {
  border-left: 4px solid #a0aec0;
  background-color: #f7fafc;
  padding: 20px 24px;
  margin: 28px 0;
  border-radius: 0 8px 8px 0;
  font-style: normal;
  color: #4a5568;
  position: relative;
}

.gp-post-blockquote::before {
  content: "\201C";
  font-size: 3rem;
  color: #cbd5e0;
  position: absolute;
  top: -8px;
  left: 12px;
  line-height: 1;
}

.gp-post-blockquote p {
  margin: 0;
  padding-left: 20px;
  line-height: 1.8;
}

/* --- リスト --- */
.gp-post-list {
  margin: 20px 0;
  padding-left: 0;
  list-style: none;
}

.gp-post-list li {
  position: relative;
  padding-left: 24px;
  margin-bottom: 10px;
  line-height: 1.8;
  color: #2d3748;
}

.gp-post-list li::before {
  content: "";
  position: absolute;
  left: 4px;
  top: 11px;
  width: 8px;
  height: 8px;
  background-color: #4299e1;
  border-radius: 50%;
}

ol.gp-post-list {
  counter-reset: gp-counter;
}

ol.gp-post-list li::before {
  content: counter(gp-counter);
  counter-increment: gp-counter;
  background-color: #4299e1;
  color: #fff;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 5px;
  left: 0;
}

ol.gp-post-list li {
  padding-left: 32px;
}

/* --- 画像 --- */
.gp-post-img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 28px 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.gp-post-img:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
}

.gp-post-img-large {
  width: 100%;
}


/* ========================================
   固定ページ用スタイル (.gp-page-*)
   ======================================== */

/* --- 見出し --- */
.gp-page-h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 3px solid #48bb78;
  line-height: 1.3;
}

.gp-page-h2 {
  font-size: 1.625rem;
  font-weight: 700;
  color: #1a202c;
  margin: 48px 0 20px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #f0fff4 0%, #f0fff4 100%);
  border-left: 4px solid #48bb78;
  border-radius: 0 6px 6px 0;
  line-height: 1.4;
}

.gp-page-h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2d3748;
  margin: 32px 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
  line-height: 1.4;
}

/* --- 本文 --- */
.gp-page-p {
  font-size: 1rem;
  line-height: 1.9;
  color: #2d3748;
  margin-bottom: 20px;
  letter-spacing: 0.02em;
}

.gp-page-intro {
  font-size: 1.1rem;
  font-weight: 500;
  line-height: 1.9;
  color: #2d3748;
  background-color: #f0fff4;
  padding: 20px 24px;
  border-left: 4px solid #48bb78;
  border-radius: 0 8px 8px 0;
  margin: 24px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

/* --- 情報ボックス --- */
.gp-page-featured-box {
  background: linear-gradient(135deg, #f0fff4 0%, #f7fafc 100%);
  border: 1px solid #c6f6d5;
  border-left: 5px solid #48bb78;
  padding: 24px 28px;
  margin: 32px 0;
  border-radius: 0 10px 10px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.gp-page-featured-box .gp-page-h3 {
  margin-top: 0;
  color: #276749;
  border-bottom-color: #9ae6b4;
}

.gp-page-featured-box .gp-page-p:last-child {
  margin-bottom: 0;
}

/* --- CTA --- */
.gp-page-cta {
  background: linear-gradient(135deg, #4299e1 0%, #667eea 50%, #9f7aea 100%);
  color: #fff;
  padding: 40px 36px;
  border-radius: 12px;
  margin: 40px 0;
  text-align: center;
  box-shadow: 0 8px 24px rgba(66, 153, 225, 0.25);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.gp-page-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(66, 153, 225, 0.3);
}

.gp-page-cta .gp-page-h3 {
  color: #fff;
  margin-top: 0;
  font-size: 1.4rem;
  border-bottom: none;
  padding-bottom: 0;
}

.gp-page-cta .gp-page-p {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0;
}

/* --- リスト --- */
.gp-page-list {
  margin: 20px 0;
  padding-left: 0;
  list-style: none;
}

.gp-page-list li {
  position: relative;
  padding-left: 24px;
  margin-bottom: 12px;
  line-height: 1.8;
  color: #2d3748;
}

.gp-page-list li::before {
  content: "";
  position: absolute;
  left: 4px;
  top: 11px;
  width: 8px;
  height: 8px;
  background-color: #48bb78;
  border-radius: 50%;
}

/* ========================================
   レスポンシブ対応
   ======================================== */
@media (max-width: 768px) {
  .gp-post-content,
  .gp-page-content {
    padding: 0 16px;
  }

  .gp-post-h2,
  .gp-page-h2 {
    font-size: 1.375rem;
    padding: 12px 14px;
    margin-top: 36px;
  }

  .gp-post-h3,
  .gp-page-h3 {
    font-size: 1.15rem;
  }

  .gp-page-h1 {
    font-size: 1.625rem;
  }

  .gp-post-featured-box,
  .gp-page-featured-box {
    padding: 18px 20px;
  }

  .gp-page-cta {
    padding: 28px 24px;
  }

  .gp-post-code {
    padding: 16px 18px;
    font-size: 0.8rem;
  }
}
```

---

## 🔄 実装フロー

```
1. 投稿ファイル作成
   ↓
2. セレクタルールに従ったHTMLを記述
   ↓
3. Git commit & push
   ↓
4. GitHub Actions で WordPress に同期
   ↓
5. WordPress のカスタム CSS が自動適用
   ↓
6. 統一されたデザインで表示 ✨
```

---

## 📌 セレクタ一覧（クイックリファレンス）

### 投稿
```
.gp-post-h2, .gp-post-h3, .gp-post-h4
.gp-post-p, .gp-post-intro
.gp-post-featured-box
.gp-post-code, .gp-post-blockquote, .gp-post-list
.gp-post-img, .gp-post-img-large
```

### 固定ページ
```
.gp-page-h1, .gp-page-h2, .gp-page-h3
.gp-page-p, .gp-page-intro
.gp-page-featured-box, .gp-page-cta
.gp-page-list
```

---

## 🎯 カスタマイズ例

### パターン A：シンプルスタイル
`gp-post-h2` を小さく、色をシンプルに

### パターン B：モダンスタイル
グラデーション、シャドウを追加

### パターン C：企業サイト向け
フォーマルな色合い、広いスペーシング

全て CSS を修正するだけで全投稿に反映！

---

**このルールに従って投稿を作成していきます！** 🚀
