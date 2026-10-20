"""Offline W2 storage replay, two workers; no live-run writes or locks."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,os,concurrent.futures,time
HERE=Path(__file__).resolve().parent
PROJECTS=HERE.parents[5]; COLLECTOR=PROJECTS/'greek-ocr-toolkit-sol-collect'; LIVE=PROJECTS/'collect-v3-data/run'
sys.path.insert(0,str(COLLECTOR))
from collect_v3.common import sha,read_json,write_json,write_rows,rows
SOURCES={'bsb_poly1850','ia_poly1850','nlg','serbia','elstat'}
def guard():
 def audit(event,args):
  if event.startswith('socket.'):raise PermissionError('network OFF')
  if event=='open' and args[2]&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
   if not isinstance(args[0],int) and str(args[0])!=os.devnull:
    p=Path(args[0]).resolve()
    if HERE not in p.parents:raise PermissionError('read-only outside W2C1: '+str(p))
 sys.addaudithook(audit)
def one(entry):
 from collect_v3.storage import page_rows
 f,record,digest=entry;out=HERE/'rebuild';target=out/'rows'/(f.stem+'.json')
 if target.exists():
  saved=read_json(target);assert saved['page_sha256']==digest;return len(saved['rows'])
 rr=page_rows(record,out/'cache',out,CONTEXT,True)
 write_json(target,dict(page_sha256=digest,rows=rr));return len(rr)
if __name__=='__main__':
 assert Path(sys.prefix).resolve()==(COLLECTOR/'.venv').resolve()
 guard()
 from collect_v3.storage import verify_recipe
 verify_recipe(LIVE,'W2')
 CONTEXT=read_json(LIVE/'convention_context.json');entries=[]
 for f in sorted((LIVE/'W2/pages').glob('*.json')):
  b=f.read_bytes();r=json.loads(b)
  if r['source'] in SOURCES and r['status']=='completed':entries.append((f,r,hashlib.sha256(b).hexdigest()))
 write_json(HERE/'rebuild_inputs.json',dict(method='collect_v3.storage.page_rows offline; W2 target sources only; global rules and W1-first dedupe',pages=[dict(path=str(f),sha256=d,source=r['source']) for f,r,d in entries],bindings={str(p):sha(p) for p in [LIVE/'W1/features.jsonl',LIVE/'convention_context.json',LIVE/'c1_gate.json',COLLECTOR/'collect_v3/storage.py',COLLECTOR/'collect_v3/runner.py',COLLECTOR/'collect_v3/pipeline.py',COLLECTOR/'collect_v3/rules.py']}))
 print('pages',len(entries),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for i,n in enumerate(pool.map(one,entries),1):
   if i%20==0:print('rebuilt',i,'/',len(entries),flush=True)
 from collect_v3.rules import apply_rules,boundary_hyphens
 allrows=rows(LIVE/'W1/features.jsonl')
 for f,r,d in entries:allrows.extend(read_json(HERE/'rebuild/rows'/(f.stem+'.json'))['rows'])
 apply_rules(allrows,CONTEXT,serbian=True);boundary_hyphens(allrows,CONTEXT)
 gate=read_json(LIVE/'c1_gate.json')['sources'];seen=set();result=[]
 for r in allrows:
  r['tags']=sorted(set(r['tags']+r['text_exclusions']));key=r['crop_sha256'],r['label'];r['duplicate_exact']=key in seen;r['candidate_before_dedupe']=bool(r['candidate_usable'])
  if r['candidate_usable']:seen.add(key)
  r['candidate_usable']=bool(r['candidate_usable'] and not r['duplicate_exact'])
  if r['tranche']=='W2':
   r['candidate_usable']=r['candidate_usable'] and gate[r['source']]['classes'].get(r['primary_class']) is True
   r['usable_final']=bool(r['candidate_usable'] and not r['crop_tight_page']);result.append(r)
 write_rows(HERE/'rebuild/W2/features.jsonl',result);print('DONE',len(result),flush=True)
