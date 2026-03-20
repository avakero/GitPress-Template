# GitPress ワークフロー & ベストプラクティス

## 推奨ワークフロー

GitPress を複数人で安全に運用するためのワークフローです。

```
                   ┌─────────────────┐
                   │   main branch   │ (本番・自動同期)
                   │  (Protected)    │
                   └────────┬────────┘
                            ▲
                            │
                      (Pull Request)
                            │
                   ┌────────┴────────┐
                   │   develop       │ (開発・統合)
                   │   (Merge base)  │
                   └────────┬────────┘
                            ▲
                            │
                      (Pull Request)
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼────┐        ┌────▼────┐       ┌────▼────┐
    │ feature/ │        │ feature/│       │  hotfix/│
    │ new-post │        │ update  │       │  urgent │
    │ (削除可) │        │ (削除可) │      │ (削除可) │
    └──────────┘        └─────────┘       └─────────┘

    各開発者がブランチを切って作業
    ↓
    Pull Request で develop にマージ
    ↓
    develop で統合テスト
    ↓
    Pull Request で main にマージ
    ↓
    自動的に WordPress に同期（GitHub Actions）
```

## ブランチ戦略

### main ブランチ（本番）

- **保護ルール有効**
- 常に本番環境と同期
- Pull Request なしで直接 push は不可
- Squash & Merge または Rebase & Merge を使用
- マージ後、自動的に GitHub Actions が実行

```bash
# main への直接 commit は不可
git commit main  # ❌ 不可

# Pull Request 経由でのみ可能
git push origin feature/new-post
# → GitHub で Pull Request を作成
# → Approve されたら Merge
```

### develop ブランチ（統合ブランチ）

- 複数の feature を統合
- main への PR の base ブランチ
- 定期的に main とマージ

### feature ブランチ（個別作業）

命名規則：`feature/描述的なタイトル`

```bash
# develop から切る
git checkout develop
git pull origin develop
git checkout -b feature/new-post

# 作業
echo "新しい記事の内容" > content/post/new-post.html
git add content/post/new-post.html
git commit -m "feat: Add new blog post about GitPress"

# Push
git push origin feature/new-post

# GitHub で Pull Request を create
# → Review される
# → develop にマージ
```

### hotfix ブランチ（緊急修正）

命名規則：`hotfix/描述的なタイトル`

```bash
# main から直接切る（develop ではなく）
git checkout main
git pull origin main
git checkout -b hotfix/fix-typo

# 修正
git add content/post/some-post.html
git commit -m "fix: Correct typo in published post"

# main と develop の両方にマージ
git push origin hotfix/fix-typo
```

## Pull Request テンプレート

`.github/pull_request_template.md` を作成して、PR を統一化：

```markdown
## 変更内容

<!-- 何を変更したか、簡潔に説明 -->

- [ ] 新しい投稿を追加
- [ ] 既存投稿を更新
- [ ] 固定ページを修正

## 関連する Issue

Closes #123

## 変更内容の詳細

<!-- 詳しい説明 -->

## チェックリスト

- [ ] Front Matter が正しい（post_id, title, slug 等）
- [ ] HTML が正しくフォーマットされている
- [ ] タイポやリンク切れがないか確認した
- [ ] ローカルで `python scripts/sync_wp_content.py --dry-run` で確認した

## スクリーンショット（必要に応じて）

<!-- 画像を添付 -->
```

## PR レビューチェックリスト

レビュー時は以下を確認：

### Front Matter の確認

- [ ] `post_id` は null （新規）または正の整数（既存）
- [ ] `post_type` は `post` または `page`
- [ ] `slug` は英数字とハイフンのみ（スペース・日本語なし）
- [ ] `title` が空でない
- [ ] `status` は `publish`, `draft`, `private` いずれか
- [ ] `date` は ISO 8601 フォーマット

### HTML コンテンツの確認

- [ ] 閉じタグが正しい（`<p>` に `</p>` など）
- [ ] 特殊文字は HTML エスケープされている（`&` → `&amp;` など）
- [ ] リンク URL が正しい
- [ ] 画像パスが正しい

### 機能確認

- [ ] `--dry-run` で問題なし
- [ ] WordPress と競合がないか確認
- [ ] カテゴリ・タグが存在するか（なければ自動作成される）

## コミットメッセージ規約

```
<type>: <subject>

<body>

<footer>
```

### Type

- `feat:` 新機能・新規投稿
- `fix:` バグ修正
- `docs:` ドキュメント更新
- `refactor:` 構造の変更（機能変更なし）
- `style:` フォーマット・HTMLタグの調整

### Subject（主語）

- 動詞で始める
- 命令形（Add, Fix, Remove など）
- 英語または日本語で統一

### Body（説明）

```
feat: Add blog post about Git workflow

Added a comprehensive guide to GitPress workflow with:
- Branch strategy (main, develop, feature)
- PR review process
- Commit message conventions

Closes #42
```

## 日常の使用パターン

### パターン 1: 新しい記事を追加

```bash
# develop から feature ブランチを作成
git checkout develop
git pull origin develop
git checkout -b feature/add-gitpress-guide

# 記事ファイルを作成
cat > content/post/gitpress-guide.html << 'EOF'
---
post_id: null
post_type: post
slug: "gitpress-guide"
title: "GitPress ガイド"
status: "publish"
...
---
<h2>本文</h2>
EOF

# コミット
git add content/post/gitpress-guide.html
git commit -m "feat: Add GitPress workflow guide"

# Push & PR
git push origin feature/add-gitpress-guide
# GitHub で PR 作成 → develop へ
# → develop で Approve → Merge
```

### パターン 2: 既存の記事を更新

```bash
# develop から feature ブランチを作成
git checkout develop
git pull origin develop
git checkout -b feature/update-gitpress-guide

# 記事を編集
vim content/post/gitpress-guide.html

# 変更を確認（--dry-run）
python scripts/sync_wp_content.py --dry-run

# コミット
git add content/post/gitpress-guide.html
git commit -m "fix: Correct information in GitPress guide"

# Push & PR
git push origin feature/update-gitpress-guide
```

### パターン 3: 緊急修正（本番投稿の typo など）

```bash
# main から直接 hotfix ブランチを作成
git checkout main
git pull origin main
git checkout -b hotfix/fix-typo-in-guide

# 修正
vim content/post/gitpress-guide.html

# コミット & Push
git add content/post/gitpress-guide.html
git commit -m "fix: Fix typo in GitPress guide"
git push origin hotfix/fix-typo-in-guide

# 2つの PR を作成
# 1. main へのマージ（緊急）→ 本番に反映
# 2. develop へのマージ（同期用） → 開発ブランチ同期
```

## GitHub Branch Protection Rules（推奨）

main ブランチを保護する設定：

1. GitHub リポジトリ → **Settings** → **Branches**
2. **Add rule** をクリック
3. Branch name pattern: `main`
4. 以下を有効化：
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require code reviews before merging (1+ approvals)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks: **Sync WordPress Content** (GitHub Actions)

## Tips

### 複数の変更をまとめて commit したい場合

```bash
git add content/post/post1.html
git add content/post/post2.html
git commit -m "feat: Add two new blog posts"
```

### 前のコミットを修正したい場合

```bash
git add content/post/post.html
git commit --amend --no-edit
```

### リモートの最新を取得

```bash
git fetch origin
git rebase origin/develop
```

### ローカルの変更を破棄してリモートに合わせる

```bash
git reset --hard origin/develop
```
