"""Offline CPU fitting command for existing synthetic shards; no torch or GPU."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from greekocr.annotate.font import train_font_classifier


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shards', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--styles', type=Path, help='JSON mapping of exact factory font ids to style classes')
    parser.add_argument('--max-lines', type=int)
    args = parser.parse_args()
    try:
        styles = json.loads(args.styles.read_text(encoding='utf-8')) if args.styles else None
        data = train_font_classifier(args.shards, args.out, styles=styles, max_lines=args.max_lines)
        print(json.dumps({k: data[k] for k in ('model_id', 'families', 'counts')}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, ImportError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
