# SEAL02E guarded commit handoff

Only these four paths are in scope; exclude every other working-tree change,
the supplied brief, and all `scaling_w3/` files. No staging or commit was performed.
The deployed manifest remains unchanged; its SEAL02.md SHA binds the pre-deployment
snapshot. Do not use the historical broader COMMIT_LIST or guard_commit.py for this
new documentation-only handoff.

- `docs/harvest/collect_v3_admission/seal02/SEAL02.md`
- `docs/harvest/collect_v3_admission/seal02/SEAL02E_RECEIPT.json`
- `docs/harvest/collect_v3_admission/seal02/SEAL02E_COMMIT_LIST.md`
- `docs/harvest/collect_v3_admission/seal02/SEAL02E_COMMIT_LIST.json`

From repository root, run this read-only guard before staging the explicit list:

```bash
python3 -B - <<'PY_GUARD'
from pathlib import Path
import hashlib, json
b = Path('docs/harvest/collect_v3_admission/seal02')
m = json.loads((b / 'SEAL02E_COMMIT_LIST.json').read_text())
assert set(m['paths']) == {str(b / p) for p in [
    'SEAL02.md', 'SEAL02E_RECEIPT.json',
    'SEAL02E_COMMIT_LIST.md', 'SEAL02E_COMMIT_LIST.json']}
assert set(m['sha256']) == {'SEAL02.md', 'SEAL02E_RECEIPT.json', 'SEAL02E_COMMIT_LIST.md'}
for name, digest in m['sha256'].items():
    assert hashlib.sha256((b / name).read_bytes()).hexdigest() == digest, name
print('SEAL02E_GUARDED_COMMIT_LIST_OK 4 paths; no git writes')
PY_GUARD
```

The JSON list excludes its own hash to avoid self-reference; the report, receipt,
and this rendered list are hash guarded. Review the JSON allowlist as well.
