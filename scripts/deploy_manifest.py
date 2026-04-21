#!/usr/bin/env python3
"""
deploy_manifest.py — YAML マニフェストを JSON に変換してデプロイ用に出力

GitPress Editor プラグインは実行時に `wp-content/uploads/gitpress-manifests/*.json`
を読み込む。本スクリプトはサイト側の YAML マニフェストをその配置に適したJSONに変換する。

使い方:
    # YAMLをJSONに変換し、指定ディレクトリにコピー
    python scripts/deploy_manifest.py --yaml-dir my-site/editables --out-dir ./dist-manifests

    # pixelcraft のベースラインをデプロイ用に変換
    python scripts/deploy_manifest.py --yaml-dir config/editables --out-dir ./dist-manifests

生成された JSON は、WordPress ホストの wp-content/uploads/gitpress-manifests/ に
FTP/SSH/rsync などで配置してください。プラグインは次回ページ読み込み時 (またはキャッシュ
TTL 15分後) に自動検出します。キャッシュを即座に破棄するには、GitPress Editor 設定
ページを一度保存してください。
"""

import argparse
import json
import pathlib
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML が必要です → pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def convert_file(yaml_file: pathlib.Path, out_dir: pathlib.Path) -> int:
    try:
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"ERROR: {yaml_file.name} のパースに失敗: {e}", file=sys.stderr)
        return 0
    if not isinstance(data, dict):
        print(f"WARN: {yaml_file.name} はマッピング形式ではありません — スキップ", file=sys.stderr)
        return 0
    out_file = out_dir / f"{yaml_file.stem}.json"
    out_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--yaml-dir", required=True, type=pathlib.Path,
                        help="変換対象のYAMLディレクトリ")
    parser.add_argument("--out-dir", required=True, type=pathlib.Path,
                        help="JSONの出力先ディレクトリ")
    args = parser.parse_args()

    yaml_dir = args.yaml_dir.resolve()
    out_dir = args.out_dir.resolve()

    if not yaml_dir.is_dir():
        print(f"ERROR: ディレクトリが見つかりません: {yaml_dir}", file=sys.stderr)
        sys.exit(1)

    yaml_files = sorted(yaml_dir.glob("*.yaml"))
    if not yaml_files:
        print(f"ERROR: YAMLが見つかりません: {yaml_dir}", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"==> 入力: {yaml_dir}")
    print(f"==> 出力: {out_dir}")

    total_entries = 0
    for yaml_file in yaml_files:
        n = convert_file(yaml_file, out_dir)
        total_entries += n
        print(f"  {yaml_file.name} -> {yaml_file.stem}.json ({n} エントリ)")

    print(f"==> 完了: {len(yaml_files)} ファイル / {total_entries} エントリ")
    print("")
    print("次のステップ:")
    print("  生成されたJSONを WordPress の wp-content/uploads/gitpress-manifests/ に")
    print("  配置してください。プラグインが自動検出します。")


if __name__ == "__main__":
    main()
