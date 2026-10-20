"""Check only this package's explicit candidate paths. Never stages or commits."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]
# Resolve by the explicit docs prefix rather than any neighboring checkout.
while not (REPO/'.git').exists() and REPO.parent!=REPO:REPO=REPO.parent
prefix=str(ROOT.relative_to(REPO))+'/'
entries=json.loads((ROOT/'COMMIT_LIST.json').read_text())
for name,h in entries.items():
    assert name.startswith(prefix) or name=='docs/briefs/P1POOL_unlabelled_pool.md','outside allowed scope'
    f=REPO/name;assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==h,'changed candidate: '+name
print('guarded commit list ok:',len(entries),'pinned paths; no git mutation')
