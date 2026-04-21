#!/usr/bin/env python3
"""
validate_editables.py — data-edit 属性と YAML マニフェストの整合性チェック

Usage:
    # デフォルト (pixelcraft + config/editables) を検証
    python scripts/validate_editables.py

    # 指定ページのみ
    python scripts/validate_editables.py index

    # 任意サイトを検証 (スキル生成サイトのチェックに使用)
    python scripts/validate_editables.py --html-dir my-site --yaml-dir my-site/editables

Exit codes:
    0 = 全チェック合格
    1 = 不整合あり
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML が必要です → pip install pyyaml")
    sys.exit(1)

# ── 設定 ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

# デフォルトターゲット: プラグインバンドルの pixelcraft ベースライン
DEFAULT_PAGES = {
    "index":   {"html": "pixelcraft/index.html",   "yaml": "config/editables/index.yaml",   "prefix": "home."},
    "service": {"html": "pixelcraft/service.html",  "yaml": "config/editables/service.yaml",  "prefix": "service."},
    "blog":    {"html": "pixelcraft/blog.html",     "yaml": "config/editables/blog.yaml",     "prefix": "blog."},
    "contact": {"html": "pixelcraft/contact.html",  "yaml": "config/editables/contact.yaml",  "prefix": "contact."},
}

VALID_TYPES = {"text", "html", "number", "icon-class", "image", "link"}

# クラス名の命名規則(英字始まり、英数/ハイフン/アンダースコアのみ)
CLASS_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")

# CSSプロパティ名の簡易検証(kebab-case)
CSS_PROP_RE = re.compile(r"^-?[a-z][a-z0-9-]*$")

# ── ヘルパー ──────────────────────────────────────────
def extract_data_edits(html_path: Path) -> list[str]:
    """HTML から data-edit 値をすべて抽出"""
    content = html_path.read_text(encoding="utf-8")
    return re.findall(r'data-edit="([^"]+)"', content)

def load_yaml(yaml_path: Path) -> dict:
    """YAML をパースして dict を返す"""
    return yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

# ── 検証ロジック ──────────────────────────────────────
def validate_page(name: str, cfg: dict) -> list[str]:
    """1ページ分の検証を実行し、エラーメッセージのリストを返す"""
    errors = []
    html_path = ROOT / cfg["html"]
    yaml_path = ROOT / cfg["yaml"]
    prefix = cfg["prefix"]

    # ファイル存在チェック
    if not html_path.exists():
        errors.append(f"HTML not found: {html_path}")
        return errors
    if not yaml_path.exists():
        errors.append(f"YAML not found: {yaml_path}")
        return errors

    # HTML 解析
    html_keys = extract_data_edits(html_path)
    html_set = set(html_keys)

    # 1) 重複チェック
    duplicates = [k for k in html_set if html_keys.count(k) > 1]
    if duplicates:
        errors.append(f"Duplicate data-edit in HTML: {duplicates}")

    # 2) プレフィックスチェック
    bad_prefix = [k for k in html_set if not k.startswith(prefix)]
    if bad_prefix:
        errors.append(f"Wrong prefix (expected '{prefix}'): {bad_prefix}")

    # YAML 解析
    try:
        yaml_data = load_yaml(yaml_path)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
        return errors

    yaml_keys = set(yaml_data.keys())

    # 3) 件数チェック
    if len(html_set) != len(yaml_keys):
        errors.append(f"Count mismatch: HTML={len(html_set)} YAML={len(yaml_keys)}")

    # 4) 1:1 対応チェック
    in_html_only = html_set - yaml_keys
    in_yaml_only = yaml_keys - html_set
    if in_html_only:
        errors.append(f"In HTML but missing from YAML: {sorted(in_html_only)}")
    if in_yaml_only:
        errors.append(f"In YAML but missing from HTML: {sorted(in_yaml_only)}")

    # 5) YAML type 値 / label / allowed_styles / allowed_classes チェック
    for key, entry in yaml_data.items():
        if not isinstance(entry, dict):
            errors.append(f"YAML entry '{key}' is not a mapping")
            continue
        t = entry.get("type")
        if t not in VALID_TYPES:
            errors.append(f"Invalid type '{t}' for '{key}' (valid: {VALID_TYPES})")
        if "label" not in entry:
            errors.append(f"Missing 'label' for '{key}'")

        # allowed_styles: missing OK (defaults to "*"), string "*" OK, or list of CSS props
        if "allowed_styles" in entry:
            val = entry["allowed_styles"]
            if val == "*":
                pass
            elif isinstance(val, list):
                for s in val:
                    if not isinstance(s, str) or not CSS_PROP_RE.match(s):
                        errors.append(f"Invalid CSS property in allowed_styles for '{key}': {s!r}")
            else:
                errors.append(f"allowed_styles for '{key}' must be '*' or a list, got {type(val).__name__}")

        # allowed_classes: missing OK (defaults to []), must be list of valid class names
        if "allowed_classes" in entry:
            val = entry["allowed_classes"]
            if not isinstance(val, list):
                errors.append(f"allowed_classes for '{key}' must be a list, got {type(val).__name__}")
            else:
                for c in val:
                    if not isinstance(c, str) or not CLASS_NAME_RE.match(c):
                        errors.append(f"Invalid class name in allowed_classes for '{key}': {c!r}")

    return errors

# ── 任意サイト向けの自動マッピング ──────────────────────
def discover_pages(html_dir: Path, yaml_dir: Path) -> dict:
    """任意ディレクトリから (HTML, YAML) ペアを検出してPAGESと同じ形の辞書を返す。

    プレフィックスは各HTML内で最初に見つかった data-edit 値の先頭セグメントから推定。
    YAMLファイル名は原則としてHTMLの stem を使う (index.html → index.yaml)。
    """
    pages: dict = {}
    if not html_dir.is_dir():
        print(f"ERROR: HTMLディレクトリが見つかりません: {html_dir}")
        sys.exit(1)
    if not yaml_dir.is_dir():
        print(f"ERROR: YAMLディレクトリが見つかりません: {yaml_dir}")
        sys.exit(1)

    for html_file in sorted(html_dir.glob("*.html")):
        keys = extract_data_edits(html_file)
        if not keys:
            continue
        # data-edit の先頭セグメントからプレフィックスを推定
        first_segments = {k.split(".", 1)[0] for k in keys}
        if len(first_segments) != 1:
            print(f"WARN: {html_file.name} は複数のプレフィックスが混在 ({first_segments}) — スキップ")
            continue
        prefix = f"{first_segments.pop()}."
        # YAMLファイル名は <stem>.yaml、なければ <prefix名>.yaml を探す
        stem = html_file.stem
        candidates = [yaml_dir / f"{stem}.yaml", yaml_dir / f"{prefix.rstrip('.')}.yaml"]
        yaml_file = next((c for c in candidates if c.exists()), candidates[0])
        pages[stem] = {
            "html": str(html_file.relative_to(ROOT)) if html_file.is_relative_to(ROOT) else str(html_file),
            "yaml": str(yaml_file.relative_to(ROOT)) if yaml_file.is_relative_to(ROOT) else str(yaml_file),
            "prefix": prefix,
        }
    return pages

# ── メイン ────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pages", nargs="*", help="検証するページ名 (省略時は全ページ)")
    parser.add_argument("--html-dir", type=Path, default=None,
                        help="HTMLディレクトリ (省略時は pixelcraft/ を使う)")
    parser.add_argument("--yaml-dir", type=Path, default=None,
                        help="YAMLディレクトリ (省略時は config/editables/ を使う)")
    args = parser.parse_args()

    # 任意サイトモード: 両方のディレクトリが指定された場合は自動検出
    if args.html_dir is not None or args.yaml_dir is not None:
        if args.html_dir is None or args.yaml_dir is None:
            print("ERROR: --html-dir と --yaml-dir は両方指定してください")
            sys.exit(1)
        pages = discover_pages(args.html_dir.resolve(), args.yaml_dir.resolve())
        if not pages:
            print(f"ERROR: {args.html_dir} に data-edit 付きHTMLが見つかりません")
            sys.exit(1)
    else:
        pages = DEFAULT_PAGES

    targets = args.pages if args.pages else list(pages.keys())

    for t in targets:
        if t not in pages:
            print(f"ERROR: Unknown page '{t}'. Valid: {list(pages.keys())}")
            sys.exit(1)

    total_errors = 0
    total_elements = 0

    for name in targets:
        cfg = pages[name]
        html_path = (ROOT / cfg["html"]) if not Path(cfg["html"]).is_absolute() else Path(cfg["html"])

        errors = validate_page_with_paths(name, cfg)
        count = len(extract_data_edits(html_path)) if html_path.exists() else 0
        total_elements += count

        if errors:
            print(f"\n  FAIL  {name} ({count} elements)")
            for e in errors:
                print(f"        - {e}")
            total_errors += len(errors)
        else:
            print(f"  PASS  {name} ({count} elements)")

    # サマリー
    print(f"\n{'=' * 50}")
    print(f"  Pages: {len(targets)}  |  Elements: {total_elements}  |  Errors: {total_errors}")
    print(f"{'=' * 50}")

    if total_errors > 0:
        print("\n  VALIDATION FAILED")
        sys.exit(1)
    else:
        print("\n  ALL CHECKS PASSED")
        sys.exit(0)


def validate_page_with_paths(name: str, cfg: dict) -> list[str]:
    """validate_page のラッパ。絶対パス/相対パスのどちらも受け付ける。"""
    # cfg の html/yaml が絶対パスで来てもROOTを前置しないよう調整
    from pathlib import Path as _P
    if _P(cfg["html"]).is_absolute() and _P(cfg["yaml"]).is_absolute():
        # 絶対パス同士の時は一時的にROOTからの相対に見せかけて既存関数を使う
        return _validate_absolute(name, cfg)
    return validate_page(name, cfg)


def _validate_absolute(name: str, cfg: dict) -> list[str]:
    """validate_page を絶対パス対応にした複製版。"""
    from pathlib import Path as _P
    errors: list[str] = []
    html_path = _P(cfg["html"])
    yaml_path = _P(cfg["yaml"])
    prefix = cfg["prefix"]

    if not html_path.exists():
        errors.append(f"HTML not found: {html_path}")
        return errors
    if not yaml_path.exists():
        errors.append(f"YAML not found: {yaml_path}")
        return errors

    html_keys = extract_data_edits(html_path)
    html_set = set(html_keys)
    duplicates = [k for k in html_set if html_keys.count(k) > 1]
    if duplicates:
        errors.append(f"Duplicate data-edit in HTML: {duplicates}")
    bad_prefix = [k for k in html_set if not k.startswith(prefix)]
    if bad_prefix:
        errors.append(f"Wrong prefix (expected '{prefix}'): {bad_prefix}")

    try:
        yaml_data = load_yaml(yaml_path)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
        return errors

    yaml_keys = set(yaml_data.keys())
    if len(html_set) != len(yaml_keys):
        errors.append(f"Count mismatch: HTML={len(html_set)} YAML={len(yaml_keys)}")
    in_html_only = html_set - yaml_keys
    in_yaml_only = yaml_keys - html_set
    if in_html_only:
        errors.append(f"In HTML but missing from YAML: {sorted(in_html_only)}")
    if in_yaml_only:
        errors.append(f"In YAML but missing from HTML: {sorted(in_yaml_only)}")

    for key, entry in yaml_data.items():
        if not isinstance(entry, dict):
            errors.append(f"YAML entry '{key}' is not a mapping")
            continue
        t = entry.get("type")
        if t not in VALID_TYPES:
            errors.append(f"Invalid type '{t}' for '{key}' (valid: {VALID_TYPES})")
        if "label" not in entry:
            errors.append(f"Missing 'label' for '{key}'")
        if "allowed_styles" in entry:
            val = entry["allowed_styles"]
            if val == "*":
                pass
            elif isinstance(val, list):
                for s in val:
                    if not isinstance(s, str) or not CSS_PROP_RE.match(s):
                        errors.append(f"Invalid CSS property in allowed_styles for '{key}': {s!r}")
            else:
                errors.append(f"allowed_styles for '{key}' must be '*' or a list, got {type(val).__name__}")
        if "allowed_classes" in entry:
            val = entry["allowed_classes"]
            if not isinstance(val, list):
                errors.append(f"allowed_classes for '{key}' must be a list, got {type(val).__name__}")
            else:
                for c in val:
                    if not isinstance(c, str) or not CLASS_NAME_RE.match(c):
                        errors.append(f"Invalid class name in allowed_classes for '{key}': {c!r}")

    return errors


if __name__ == "__main__":
    main()
