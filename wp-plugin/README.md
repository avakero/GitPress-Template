# GitPress Editor プラグイン

WordPress 用の「DevTools 風」ビジュアル編集プラグイン。ページ上の要素を直接クリックし、Google Gemini に指示を出してコンテンツを書き換えます。

## このディレクトリの中身

| ファイル | 用途 |
|---|---|
| `gitpress-editor-0.7.0.zip` | WordPress にアップロードするプラグイン本体 |
| `docs/INSTALL.md` | インストール手順と設定ガイド |
| `docs/USAGE.md` | 使い方 (デスクトップ/モバイル) |

## 必要要件

- WordPress 5.6 以上
- PHP 7.4 以上 (DOM 拡張が有効)
- Administrator または Editor 権限
- ページ HTML に `data-edit` 属性が付与されていること

## クイックスタート

1. `gitpress-editor-0.7.0.zip` をダウンロード
2. WordPress 管理画面 → **プラグイン → 新規追加 → プラグインのアップロード**
3. zip を選択して **今すぐインストール → 有効化**
4. **設定 → GitPress Editor** で Gemini API キーを設定 (任意)
5. サイトのフロントエンドにアクセスし、右下の鉛筆ボタンをタップ

詳しい手順は [docs/INSTALL.md](./docs/INSTALL.md) を参照。

## 編集できる要素

プラグインは HTML 内の `data-edit` 属性を持つ要素だけを編集対象とします:

```html
<h1 data-edit="home.hero.title">ようこそ</h1>
```

属性がない要素はクリックしても選択できません。これは「編集可能な場所を事前に決めておく」設計で、AI が意図せずページ構造を壊すのを防ぎます。

## 編集ルール (マニフェスト)

各 `data-edit` パスには「何を変更してよいか」を定義したマニフェスト (JSON) が紐づきます。プラグインは 2 層の優先順位でマニフェストを読み込みます:

1. **バンドル baseline** — zip 内 `manifests/*.json` (参照サイト `pixelcraft` 用)
2. **サイト固有オーバーライド** — `wp-content/uploads/gitpress-manifests/*.json`

自サイトの構造が pixelcraft と異なる場合は、レイヤ 2 に自サイト用の JSON を配置することで、AI に「このパスでは色だけ変えてよい」などの細かい制限をかけられます。

### サイト用マニフェストの作り方

リポジトリルートのスクリプトを使います:

```bash
# 依存関係を入れる
pip install -r scripts/requirements.txt

# (1) あなたのサイトの HTML から data-edit を走査し、YAML を生成
python scripts/generate_manifest.py --html-dir path/to/your-site

# (2) HTML と YAML の整合性を検証
python scripts/validate_editables.py --html-dir path/to/your-site --yaml-dir path/to/your-site/editables

# (3) YAML を JSON に変換 (デプロイ用)
python scripts/deploy_manifest.py --yaml-dir path/to/your-site/editables --out-dir ./dist-manifests
```

生成された `dist-manifests/*.json` を WordPress の `wp-content/uploads/gitpress-manifests/` に FTP/SSH 等で配置。プラグインが次回ページ読み込み時に自動検出します (キャッシュ TTL 15 分)。

### 配置場所を変更したい場合

テーマの `functions.php` に:

```php
add_filter( 'gitpress_editor_site_manifests_dir', function () {
    return ABSPATH . 'wp-content/my-custom-manifests';
} );
```

空文字を返すとサイト固有マニフェストの読み込みが無効になります。

## プラグインと Git 同期の関係

このテンプレートリポジトリ全体は、**Git を信頼ソースとする WordPress 運用**を前提にしています。プラグインで行った編集は:

1. WordPress DB に保存
2. GitHub にもコミット (`[skip ci]` 付きで循環を防止)

これにより「ブラウザで編集 → Git に自動反映」の双方向同期が成立します。詳しくはリポジトリ直下の [README.md](../README.md) を参照。

## ライセンス

MIT
