"""Submission guard: pending per-parent SF7 bindings never enter an attempt."""
import argparse,json
from pathlib import Path
D=Path(__file__).resolve().parent
def pending(config):
 entries=[r for r in config.get('corrections',[]) if r.get('tool')=='polytonic']
 parents={p['id'] for p in config.get('parents',[])} or {r['parent_id'] for r in entries}
 missing=[]
 for parent in sorted(parents):
  rs=[r for r in entries if r['parent_id']==parent]
  if len(rs)!=1 or any(r.get('binding_status')=='PENDING' or not r.get('sha256') or str(r.get('path','')).startswith('PENDING') for r in rs):missing.append(parent)
 if any(r['parent_id'] not in parents for r in entries):missing.append('unexpected parent')
 return missing
def require_bound(config):
 missing=pending(config)
 if missing: raise ValueError('sf7-binding PENDING: '+', '.join(missing))
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=D/'census06_config.json');p.add_argument('--submit',action='store_true');a=p.parse_args()
 c=json.loads(a.config.read_text());m=pending(c)
 print('sf7-binding '+('PENDING: '+', '.join(m) if m else 'OK'))
 if a.submit:require_bound(c)
if __name__=='__main__':main()
