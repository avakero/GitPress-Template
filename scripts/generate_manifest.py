#!/usr/bin/env python3
"""
generate_manifest.py — HTML内の data-edit 属性から YAML マニフェストを生成

任意のサイトディレクトリを入力に取り、GitPress Editor プラグインが読み込める
形式のマニフェスト (YAML) を出力する。スキルが生成したサイトに対しても
そのまま使える。

使い方:
    # 基本: HTMLのあるディレクトリを指定すると、同じディレクトリの
    # editables/ サブディレクトリに YAML を書き出す
    python scripts/generate_manifest.py --html-dir pixelcraft

    # 出力先を指定
    python scripts/generate_manifest.py --html-dir my-site --out-dir my-site/editables

    # 1ページだけ
    python scripts/generate_manifest.py --html-dir my-site --page index

ページ名とプレフィックスの対応は、HTML内の data-edit 属性の先頭セグメント
から自動検出する。例: `home.hero.title` があれば index.html → home.yaml。

出力形式は config/editables/*.yaml と同じ。
"""

import argparse
import pathlib
import re
import sys
from collections import defaultdict

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML が必要です → pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# プラグインにバンドルされているプリセットクラス
# assets/css/presets.css および includes/class-manifest-loader.php と同期
PRESET_CLASSES = [
    "gp-text-rainbow",
    "gp-text-gradient-brand",
    "gp-text-gradient-warm",
    "gp-text-gradient-cool",
    "gp-text-gradient-sunset",
    "gp-text-marker-yellow",
    "gp-text-marker-pink",
    "gp-text-marker-cyan",
    "gp-text-glow",
    "gp-text-glow-warm",
    "gp-text-outline",
    "gp-text-bold",
    "gp-text-semibold",
    "gp-text-normal",
    "gp-text-italic",
    "gp-text-underline",
    "gp-text-strike",
    "gp-text-uppercase",
    "gp-text-primary",
    "gp-text-secondary",
    "gp-text-accent",
    "gp-text-success",
    "gp-text-danger",
    "gp-text-muted",
    "gp-text-white",
    "gp-text-black",
    "gp-text-xs", "gp-text-sm", "gp-text-md", "gp-text-lg",
    "gp-text-xl", "gp-text-2xl", "gp-text-3xl", "gp-text-4xl",
    "gp-text-left", "gp-text-center", "gp-text-right",
]

# data-edit 属性つきの開始タグを抽出 (タグ名も一緒に取る)
TAG_RE = re.compile(
    r"<(?P<tag>[a-zA-Z][a-zA-Z0-9]*)\b[^>]*?\bdata-edit=\"(?P<path>[^\"]+)\"[^>]*?>",
    re.IGNORECASE,
)


def classify(tag: str) -> str:
    """HTMLタグ名から要素タイプを決める。"""
    tag = tag.lower()
    if tag == "img":
        return "image"
    if tag == "i":
        return "icon-class"
    if tag == "a":
        return "link"
    return "html"


def label_from_path(path: str) -> str:
    """"home.hero.title" → "title" を日本語風に整形。"""
    return path.rsplit(".", 1)[-1].replace("-", " ")


def build_entry(tag: str, path: str) -> dict:
    t = classify(tag)
    entry = {
        "type": t,
        "label": label_from_path(path),
    }
    if t in ("image", "icon-class"):
        # 画像・アイコンはクラスやスタイルで直接いじらない方針
        entry["allowed_styles"] = []
        entry["allowed_classes"] = []
    else:
        entry["allowed_styles"] = "*"
        entry["allowed_classes"] = list(PRESET_CLASSES)
    return entry


def scan_html(html_text: str) -> list[tuple[str, str]]:
    """HTMLから (tag, path) のペアをユニークに抽出。"""
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for m in TAG_RE.finditer(html_text):
        path = m.group("path")
        if path in seen:
            continue
        seen.add(path)
        result.append((m.group("tag"), path))
    return result


def group_by_prefix(entries: list[tuple[str, str]]) -> dict[str, dict]:
    """[(tag, path), ...] を data-edit パスの先頭セグメントでグループ化。"""
    by_prefix: dict[str, dict] = defaultdict(dict)
    for tag, path in entries:
        prefix = path.split(".", 1)[0]
        by_prefix[prefix][path] = build_entry(tag, path)
    return dict(by_prefix)


def page_name_for_prefix(html_file: pathlib.Path, prefix: str) -> str:
    """出力YAMLのファイル名を決める。

    慣例:
      - HTMLが index.html で prefix が "home" → index.yaml
      - それ以外は prefix 名をそのまま使う (service.html の prefix="service" → service.yaml)
    """
    stem = html_file.stem
    if stem == "index" and prefix == "home":
        return "index"
    return prefix


def process_html(html_file: pathlib.Path, out_dir: pathlib.Path, verbose: bool = True) -> int:
    """1つのHTMLファイルを処理して、必要なだけYAMLを書き出す。"""
    html = html_file.read_text(encoding="utf-8")
    entries = scan_html(html)
    if not entries:
        if verbose:
            print(f"  {html_file.name}: data-edit なし — スキップ")
        return 0

    grouped = group_by_prefix(entries)
    total = 0
    for prefix, manifest in grouped.items():
        name = page_name_for_prefix(html_file, prefix)
        out_file = out_dir / f"{name}.yaml"
        with open(out_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(manifest, f, allow_unicode=True, sort_keys=False, width=1000)
        total += len(manifest)
        if verbose:
            print(f"  {html_file.name} → {out_file.relative_to(out_dir.parent)}: {len(manifest)} エントリ (prefix={prefix})")
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--html-dir", required=True, type=pathlib.Path,
                        help="HTMLファイルが置かれたディレクトリ")
    parser.add_argument("--out-dir", type=pathlib.Path, default=None,
                        help="YAML出力先 (省略時は <html-dir>/editables/)")
    parser.add_argument("--page", action="append", default=None,
                        help="特定のページのみ処理 (例: --page index --page contact)。省略時は全HTML")
    parser.add_argument("--quiet", action="store_true", help="進捗を抑制")
    args = parser.parse_args()

    html_dir = args.html_dir.resolve()
    if not html_dir.is_dir():
        print(f"ERROR: ディレクトリが見つかりません: {html_dir}", file=sys.stderr)
        sys.exit(1)

    out_dir = (args.out_dir or (html_dir / "editables")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.page:
        html_files = [html_dir / f"{p}.html" for p in args.page]
        for f in html_files:
            if not f.is_file():
                print(f"ERROR: ファイルなし: {f}", file=sys.stderr)
                sys.exit(1)
    else:
        html_files = sorted(html_dir.glob("*.html"))

    if not html_files:
        print(f"ERROR: HTMLが見つかりません: {html_dir}", file=sys.stderr)
        sys.exit(1)

    verbose = not args.quiet
    if verbose:
        print(f"==> 入力: {html_dir}")
        print(f"==> 出力: {out_dir}")

    total_entries = 0
    for html_file in html_files:
        total_entries += process_html(html_file, out_dir, verbose=verbose)

    if verbose:
        print(f"==> 完了: {total_entries} エントリ")


if __name__ == "__main__":
    main()
