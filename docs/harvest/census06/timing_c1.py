"""Measured CENSUS06 projection; no scheduler or network operations."""
import argparse
import json
import math
from pathlib import Path

FULL_ROWS = 592466
BASELINE_SECONDS = 9112
BASELINE_SF7_ROWS = 258629
PARTITION_MAX_SECONDS = 43200


def hms(seconds):
    seconds = math.ceil(seconds)
    return f'{seconds//3600:02d}:{seconds//60%60:02d}:{seconds%60:02d}'


def seconds(value):
    import re
    if not re.fullmatch(r'\d{2,}:\d{2}:\d{2}', value):
        raise ValueError('time must be HH:MM:SS')
    h, m, s = map(int, value.split(':'))
    if m > 59 or s > 59 or h*3600+m*60+s <= 0:
        raise ValueError('invalid time')
    return h*3600+m*60+s


def projection(timing):
    load, decisions, lookup = (timing[k] for k in ('sf7_load', 'decisions', 'sf7_lookup'))
    if load['records'] <= 0 or load['seconds'] <= 0 or decisions['rows'] <= 0 or decisions['seconds'] <= 0:
        raise ValueError('missing positive smoke measurements')
    if lookup['calls'] <= 0 or lookup['seconds'] <= 0:
        raise ValueError('no measured sf7 lookups; cannot project lookup cost')
    # Use census_05 routed rows rather than extrapolating the first-40 route mix.
    lookup_per_row = lookup['seconds'] / lookup['calls']
    projected = math.ceil(BASELINE_SECONDS + load['seconds'] + BASELINE_SF7_ROWS*lookup_per_row)
    suggested = min(math.ceil(projected*1.5), PARTITION_MAX_SECONDS)
    return dict(projected_full_seconds=projected, suggested_limit=hms(suggested),
                partition_max=hms(PARTITION_MAX_SECONDS), formula='9112 + measured sf7 load seconds + 258629 * sf7 lookup seconds / measured sf7 lookup calls',
                row_mix_representative=False, timing=timing)


def timing_line(p):
    t = p['timing']; a, d = t['sf7_load'], t['decisions']
    return (f"CENSUS TIMING: sf7 load {a['records']} rec in {a['seconds']:.6f} s ({a['records']/a['seconds']:.3f} rec/s); "
            f"decisions {d['rows']} in {d['seconds']:.6f} s ({d['rows']/d['seconds']:.3f} rows/s); "
            f"projected full {hms(p['projected_full_seconds'])} (full sf7 files loaded; smoke rate not representative: first 40/parent, native work and route mix differ; "
            f"census_05 non-sf7 measured total {BASELINE_SECONDS} s for 592466 rows + measured sf7 load + 258629 census_05 routed rows × measured sf7 lookup seconds/call {t['sf7_lookup']['seconds']/t['sf7_lookup']['calls']:.9f}; "
            f"census_05 fixed overhead included, not separately measured); suggested limit ×1.5 = {p['suggested_limit']} (partition max {p['partition_max']})")


def guard(readout, limit):
    p = json.loads(Path(readout).read_text())['census_timing'] if readout else None
    if p and p['projected_full_seconds'] > 14400 and not limit:
        raise ValueError('projection exceeds 04:00:00; explicit full limit required')
    if limit and seconds(limit) > PARTITION_MAX_SECONDS:
        raise ValueError('full limit exceeds normal partition max 12:00:00')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempts', type=Path); parser.add_argument('--smoke-readout'); parser.add_argument('--full-time', default='')
    args = parser.parse_args()
    readout = args.smoke_readout
    if not readout and args.attempts:
        candidates = list(args.attempts.glob('smoke*.readout/readout.json'))
        if candidates:
            readout = max(candidates, key=lambda p: p.stat().st_mtime)
    guard(readout, args.full_time)
