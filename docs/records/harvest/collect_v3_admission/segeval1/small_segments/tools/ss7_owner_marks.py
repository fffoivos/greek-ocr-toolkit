"""Refresh owner marks: ss7_owner_marks.py <dump_dir> <out> (metadata only)."""
from pathlib import Path
from collections import Counter
import argparse
import json

SS = Path(__file__).resolve().parents[1]
MANIFEST = SS / 'sheet/card_manifest.json'
SHEET = 'small_segments (417, Q3 typology)'


def collect_marks(dump_dir, manifest=MANIFEST):
    dump_dir = Path(dump_dir)
    # Accept either the timestamped dump directory or its notes directory.
    notes = dump_dir / 'notes' if (dump_dir / 'notes').is_dir() else dump_dir
    if not notes.is_dir():
        raise ValueError(f'dump directory missing: {notes}')
    cards = {r['line_id']: r['doc_id'] for r in json.loads(Path(manifest).read_text(encoding='utf-8'))}
    rows, seen = [], set()
    for path in sorted(notes.glob('*.json')):
        mark = json.loads(path.read_text(encoding='utf-8'))
        line_id = mark['line_id']
        if line_id in seen:
            raise ValueError(f'duplicate line_id: {line_id}')
        seen.add(line_id)
        if path.stem != 'smallseg:' + line_id:
            raise ValueError(f'filename doc_id mismatch: {path.name}')
        if line_id not in cards or cards[line_id] != 'smallseg:' + line_id:
            raise ValueError(f'line_id not a manifest card: {line_id}')
        if mark['verdict'] not in ('KEEP', 'DROP'):
            raise ValueError(f'invalid verdict: {mark["verdict"]}')
        rows.append(dict(sheet=SHEET, line_id=line_id, owner_mark=mark['verdict'],
                         note=mark['note'], updated=mark['updated']))
    return sorted(rows, key=lambda r: r['line_id'])


def build(dump_dir, out, manifest=MANIFEST):
    rows = collect_marks(dump_dir, manifest)
    # No destination is opened until every input has passed validation.
    payload = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    Path(out).write_text(payload, encoding='utf-8')
    counts = Counter(r['owner_mark'] for r in rows)
    return dict(row_count=len(rows), KEEP=counts['KEEP'], DROP=counts['DROP'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump_dir', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    try:
        counts = build(args.dump_dir, args.out)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'SS7 FAILED: {exc}\n')
    print(f"owner marks {counts['row_count']} (KEEP {counts['KEEP']} / DROP {counts['DROP']})")


if __name__ == '__main__':
    main()
