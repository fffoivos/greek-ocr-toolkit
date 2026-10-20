"""Independent local readback checks for the SX1b deliverables; no network."""
import collections
import hashlib
import json
from pathlib import Path

root = Path('artifacts/sx1')
receipt = json.loads((root / 'RECEIPT_v2.json').read_text())
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(receipt['extract']['path']) == receipt['extract']['sha256']
assert digest(receipt['script']['path']) == receipt['script']['sha256']
assert digest(receipt['truth_input']['local_path']) == receipt['truth_input']['sha256']
for path, expected in receipt['v1_preservation']['files'].items():
    assert digest(path) == expected, path
rows = [json.loads(line) for line in Path(receipt['extract']['path']).read_text().splitlines()]
old = [json.loads(line) for line in (root / 'sf6_release_extract_lqb.jsonl').read_text().splitlines()]
assert len(rows) == len({r['line_id'] for r in rows}) == 101
assert [{**r, 'modes': {m: v for m, v in r['modes'].items() if m != 'ENSEMBLE_AB'}} for r in rows] == old
for row in rows:
    assert set(row['modes']) == {'PRESENCE', 'FULL', 'ENSEMBLE_AB'}
    for mode in row['modes'].values():
        if mode['status'] == 'HOLD':
            assert mode['label'] is None and mode['hold_reasons']
        else:
            assert mode['status'] in ('released-corrected', 'released-unchanged')
            assert isinstance(mode['label'], str) and not mode['hold_reasons']
for name, counts in receipt['counts_by_truth_set'].items():
    subset = [r for r in rows if name in r['truth_sets']]
    assert len(subset) == counts['in_selection']
    for mode, expected in counts['modes'].items():
        statuses = collections.Counter(r['modes'][mode]['status'] for r in subset)
        assert expected == dict(released=len(subset)-statuses['HOLD'], held=statuses['HOLD'],
                                released_corrected=statuses['released-corrected'],
                                released_unchanged=statuses['released-unchanged'])
audit = [r for r in rows if 'audit100' in r['truth_sets']]
assert len(audit) == 99
assert all(r['modes']['ENSEMBLE_AB']['status'] == 'released-corrected' for r in audit)
assert all(v['receipt_sha_verified'] and len(v['sha256']) == 64
           and v['scanned_lines'] == 124669 for v in receipt['remote']['overlays'].values())
print('PASS: v2 readback, all per-set mode counts, audit100 99 corrected releases, v1 unchanged')
