import json
from common import ROOT,PACK_ROOT,sha
frozen=json.loads((ROOT/'build_hashes.json').read_text())
for rel,digest in frozen.items():
    assert sha(ROOT/rel)==digest, 'STOP: frozen build changed: '+rel
r=json.loads((ROOT/'control_review/lead_review.json').read_text());key=json.loads((ROOT/'keys/cap1.json').read_text())
ids={i for i,k in key['items'].items() if k['control']}
assert r.get('status')=='verified','STOP: lead control review still pending'
assert r['sheet_sha256']==sha(ROOT/'control_review/controls.png'),'STOP: reviewed sheet changed'
assert set(r.get('verified_items',[]))==ids,'STOP: all six controls must be pixel-verified'
assert not (PACK_ROOT/'cap1/r1b/answers.jsonl').exists(),'STOP: answers already exist'
print('Lead controls gate passed')
