"""Capture all deployed/policy/labelfix pins without importing model code."""
import hashlib
import json
from pathlib import Path
import re
import sys
from greekocr.labelfix.release_gate import policy_binding
ROOT = Path(__file__).resolve().parents[2]

def capture(label):
    paths = set(json.loads((ROOT/'artifacts/cleanup_step3/cu3b/pinned_before.json').read_text()))
    policy = policy_binding()
    paths.update(policy['sources'])
    paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'greekocr/labelfix').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for manifest in ROOT.rglob('*DEPLOY_SHA256.txt'):
        paths.add(str(manifest.relative_to(ROOT)))
        for line in manifest.read_text().splitlines():
            match = re.match(r'^[0-9a-f]{64}\s+\*?(.+)$', line)
            if match:
                path = Path(match[1])
                if not path.is_absolute(): paths.add(str(path))
    table = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() if (ROOT/p).is_file() else None for p in sorted(paths)}
    out = ROOT/'artifacts/cleanup_step4'
    (out/f'pinned_{label}.json').write_text(json.dumps(table, indent=2)+'\n')
    (out/f'pinned_{label}.sha256').write_text(''.join(f'{sha or "MISSING"}  {p}\n' for p, sha in table.items()))
    (out/f'policy_{label}.json').write_text(json.dumps(policy, indent=2)+'\n')
    print(label, len(table), sum(v is not None for v in table.values()), policy['sha256'])

if __name__ == '__main__': capture(sys.argv[1])
