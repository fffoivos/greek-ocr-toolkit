"""Lead launcher custody and budget checks; never launches a model itself."""
import json,re,sys
from pathlib import Path
from common import sha,rows
D=Path(__file__).resolve().parents[1]
SC='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
def load(p):return json.loads(p.read_text())
def verify():
 r=load(D/'draw_receipt.json');assert sha(D/'keys/sealed_decisions.jsonl')==r['seal_sha256']
 assert sha(D/'tools/scan_rollout.py')==SC
 c=load(D/'pack_closure.json');root=Path(c['pack_root'])
 assert {p.name for p in root.iterdir()}=={'segeval1_a','segeval1_b'}
 for bed,m in c['manifests'].items():
  rd=root/bed/'r1';assert load(rd.parent/'MANIFEST.r1.json')==m
  expected=m['files'];actual={str(p.relative_to(rd)) for p in rd.rglob('*') if p.is_file()}
  assert actual==set(expected),'Pre-read pack closure changed'
  for p,h in expected.items():
   f=rd/p;assert sha(f)==h and not f.is_symlink() and f.stat().st_nlink==1
  assert len(rows(rd/'cards.jsonl'))==80
 print('verified two isolated contexts, 150 study + 10 controls')
def limit(line):
 assert 'limit_id=codex ' in line,'No Codex limit snapshot'
 f=re.findall(r'(?:primary|secondary)=([0-9.]+)%/10080m',line)
 assert len(f)==1 and 0<=float(f[0])<78,'STOP: weekly used >=78% or missing bucket'
 print(f[0])
if __name__=='__main__':
 action,*args=sys.argv[1:]
 if action=='verify':verify()
 elif action=='limit':limit(args[0])
 else:raise ValueError(action)
