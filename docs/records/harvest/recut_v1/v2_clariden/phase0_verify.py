"""Read-only custody verification for the completed, rejected Phase 0 mock."""
import argparse
import hashlib
import json
from pathlib import Path
import socket

p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()


ids=set();bad=[]
for path in sorted((a.out/'page-lines').glob('*.guarded.jsonl')):
    for line in path.read_text().splitlines():
        r=json.loads(line)
        assert r['id'] not in ids
        ids.add(r['id'])
        for role,path,expected in [('original',Path(r['original_path']),r['original_sha256']),
                                   ('output',a.out/r['masked_path'],r['output_sha256'])]:
            actual=sha(path)
            if actual!=expected:bad.append(dict(id=r['id'],role=role,actual=actual,expected=expected))
assert len(ids)==50
result=dict(host=socket.gethostname(),code_tree_sha='63c640a3aa4abe08d200258cf24d235dfa4a1625',
            records=50,originals_rehashed=50,outputs_rehashed=50,mismatches=bad,ok=not bad)
a.receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
assert not bad
