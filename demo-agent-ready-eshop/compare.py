"""Porovná dva audity (audit.json) a vypíše Markdown report zo šablóny templates/compare.md.

Použitie:
    python compare.py out/v1/audit.json out/v2/audit.json -o out/compare-v1-v2.md
"""

import argparse
import json
from pathlib import Path

from eshop.snapshot import SCHEMA_VERSION, render_compare


def load(path: str) -> dict:
    snap = json.loads(Path(path).read_text(encoding="utf-8"))
    if snap.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(f"{path}: nepodporovaná verzia snímky {snap.get('schema_version')} (očakávaná {SCHEMA_VERSION})")
    return snap


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("old")
    parser.add_argument("new")
    parser.add_argument("-o", "--output", help="kam uložiť Markdown (inak stdout)")
    args = parser.parse_args()
    md = render_compare(load(args.old), load(args.new))
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"📄 {args.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()
