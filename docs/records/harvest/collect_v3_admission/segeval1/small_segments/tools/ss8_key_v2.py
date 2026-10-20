"""Append supplied gate flags while preserving the exact serialized v1 row prefix."""
import gzip
import json
from pathlib import Path
from ss1_q1 import read_rows

SS = Path(__file__).resolve().parents[1]

def gate_flag(row_id, foreign, mixed):
    f, m = row_id in foreign, row_id in mixed
    return {'gate_failed': f or m, 'gate_reason': 'both' if f and m else 'foreign' if f else 'mixed' if m else None}

def build(foreign, mixed, source=SS/'small_population_key.jsonl.gz', target=SS/'small_population_key.v2.jsonl.gz'):
    count = 0
    with gzip.open(source, 'rb') as src, target.open('xb') as raw:
        with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as dst:
            for line in src:
                row = json.loads(line)
                assert not {'gate_failed', 'gate_reason'} & row.keys()
                # Keep every original field's JSON bytes, including float spelling and order.
                prefix = line.rstrip(b'\r\n')
                assert prefix.endswith(b'}')
                flags = json.dumps(gate_flag(row['row_id'], foreign, mixed)).encode()
                dst.write(prefix[:-1] + b', ' + flags[1:] + b'\n')
                count += 1
    verify(source, target, foreign, mixed)
    return count

def verify(source, target, foreign, mixed):
    from itertools import zip_longest
    count = 0
    with gzip.open(source, 'rb') as a, gzip.open(target, 'rb') as b:
        for old, new in zip_longest(a, b):
            assert old is not None and new is not None
            v1, v2 = json.loads(old), json.loads(new)
            assert {k:v for k,v in v2.items() if k not in ('gate_failed','gate_reason')} == v1
            assert {k:v2[k] for k in ('gate_failed','gate_reason')} == gate_flag(v1['row_id'],foreign,mixed)
            assert new.startswith(old.rstrip(b'\r\n')[:-1] + b', "gate_failed": ')
            assert list(v2) == list(v1) + ['gate_failed','gate_reason']
            count += 1
    assert target.read_bytes()[4:8] == b'\0\0\0\0'
    return count

if __name__ == '__main__':
    ids=json.loads((SS/'gate_recheck/foreign_mixed_ids_20261019.json').read_text())
    print(build(set(ids['foreign']),set(ids['mixed'])))
