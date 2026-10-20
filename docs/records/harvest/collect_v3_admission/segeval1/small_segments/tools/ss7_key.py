"""Metadata-only SS7 population join. Run with the supplied Python and -B."""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import io
import json
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ss1_q1 import output_type, rotation, wave_group, reason_category

SS = Path(__file__).resolve().parents[1]
BASE = SS.parent
CENSUS = BASE / 'cells/population_cells.jsonl.gz'
EXPECTED = {'numeric': 38221, 'nonnumeric': 19481, 'mixed': 1300}
CENSUS_SHA256 = '65dd922629c9e81d05c3cf419f5a623837d55a1820e89811bbd8b74511956dfc'


def key_row(row):
    geometry = rotation(row['width_px'], row['height_px'])
    if row['characters'] > 8 or geometry['A'] > 6:
        return None
    match = re.match(r'^(.+--[0-9a-f]{16})--', row['row_id'])
    if not match or not match[1].startswith(row['source'] + '--'):
        raise ValueError('invalid book prefix: ' + row['row_id'])
    return dict(row_id=row['row_id'], chars=row['characters'],
                text_characters=row['text_characters'], width_px=row['width_px'],
                height_px=row['height_px'], L=geometry['L'], S=geometry['S'],
                A=round(geometry['A'], 4), rotated=geometry['rotated'],
                output_type=output_type(row['raw_text'], row['is_numeric_output']),
                source=row['source'], book=match[1], primary_class=row['primary_class'],
                script_class=row['script_class'], wave=row['wave'],
                verdict_05=row['verdict_05'],
                reason_category=reason_category(row['verdict_05'], row['reason_05']),
                crop_sha256=row['crop_sha256'])


def reconcile(rows, census_n):
    receipt = json.loads((SS / 'q1/SS1_RECEIPT.json').read_text())
    q1 = json.loads((SS / 'q1/q1.json').read_text())
    counts = dict(Counter(r['output_type'] for r in rows))
    inside = [r for r in q1['tables']['T4']
              if r['candidate'] == 'C7_chars_le_8_A_le_6' and r['side'] == 'inside']
    ss1_counts = {r['group']: r['n'] for r in inside if r['section'] == 'capture_output_type'}
    totals = [r['n'] for r in inside if r['section'] == 'census' and r['group'] == 'all']
    waves = Counter(wave_group(r['wave']) for r in rows)
    if (len(rows) != 59002 or counts != EXPECTED or ss1_counts != EXPECTED
            or totals != [59002] or census_n != 592466
            or census_n != receipt['census_rows_read'] or census_n != q1['metadata']['census_n']
            or any(waves[r['group']] != r['n'] for r in inside
                   if r['section'] == 'capture_wave_group')):
        raise ValueError(f'SS1 reconciliation mismatch: rows={len(rows)}, types={counts}, census={census_n}')
    return dict(census_rows_read=census_n, row_count=len(rows), by_output_type=counts,
                by_source=dict(sorted(Counter(r['source'] for r in rows).items())),
                by_wave_group=dict(sorted(waves.items())), ss1_reconciled=True)


def write_gzip(rows, fileobj):
    # Empty header filename prevents the destination name from affecting bytes.
    with gzip.GzipFile(filename='', mode='wb', fileobj=fileobj, mtime=0) as zipped:
        for row in rows:
            zipped.write((json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8'))


def build(out=SS / 'small_population_key.jsonl.gz'):
    rows, census_n = [], 0
    with gzip.open(CENSUS, 'rt', encoding='utf-8') as census:
        for line in census:
            census_n += 1
            row = key_row(json.loads(line))
            if row is not None:
                rows.append(row)
    rows.sort(key=lambda r: r['row_id'])
    if len({r['row_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate population row_id')
    stats = reconcile(rows, census_n)
    with Path(out).open('wb') as stream:
        write_gzip(rows, stream)
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', nargs='?', type=Path, default=SS / 'small_population_key.jsonl.gz')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.out), ensure_ascii=False))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'SS7 FAILED: {exc}\n')


if __name__ == '__main__':
    main()
