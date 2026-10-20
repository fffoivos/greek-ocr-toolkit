"""Offline RB7 readback verification and compact release extraction. Never writes peers."""
import json,gzip,hashlib,pathlib,collections,unicodedata as ud,sys
BASE=pathlib.Path(__file__).resolve().parent
OUT=BASE/'output_3687228'
BAS=BASE/'baseline/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729'
SEL=BASE/'baseline/labelfix_l1_20261017/artifacts/labelfix_l1/binding/selection.jsonl'
RAW=BASE.parents[2]/'greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'
# Resolve against sibling Projects directory, independent of invocation cwd.
RAW=BASE.parents[2]/'greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'
RAW=pathlib.Path.home()/'Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'
PREREG='64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d'
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(p,r):pathlib.Path(p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
def rows(p):
 with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:
  for l in f:
   if l.strip():yield json.loads(l)
def verify():
 remote=json.load(open(BASE/'remote_sha_verification.json'));r=json.load(open(OUT/'receipt.json'))
 assert remote['all_ok'] and sha(OUT/'receipt.json')==remote['receipt_sha256'] and r['complete']
 assert r['preregistration_sha256']==PREREG
 local={}
 for p in sorted(OUT.rglob('*')):
  if not p.is_file() or p.name.startswith(('READBACK','job_state')):continue
  name=str(p.relative_to(OUT))
  if name in r['outputs']:
   actual=sha(p);assert actual==r['outputs'][name],name;local[name]=actual
 assert len(local)==985,len(local)
 b=json.load(open(BAS/'receipt.json'));assert sha(BAS/'receipt.json')=='c7cfcc852281c9ba6ebbe4c6d121455e8b094f48da84472989b0ac795fd991a3'
 assert sha(BAS/'input_verification.json')==b['input_verification_sha256']
 for p in (BAS/'release').iterdir():assert sha(p)==b['outputs'][str(p.relative_to(BAS))]
 assert sha(RAW)=='5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3'
 assert sha(SEL)==r['inputs']['/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/artifacts/labelfix_l1/binding/selection.jsonl']
 cfg=BASE/'baseline/labelfix_sf7_20261017/config/sf7_job.json';assert sha(cfg)==r['config_sha256']
 assert json.load(open(OUT/'input_verification.json'))['inputs']==json.load(open(BAS/'input_verification.json'))['inputs']
 dump(OUT/'READBACK_RECEIPT.json',dict(schema='rb7-readback-v1',status='sha_verified',job='3687228',job_state='COMPLETED',exit_code='0:0',receipt_sha256=sha(OUT/'receipt.json'),preregistration_sha256=PREREG,remote_outputs_verified=len(remote['output_checks']),stage_outputs_verified=len(remote['stage_checks']),local_outputs_verified=len(local),local_sha256=local,remote_verification_sha256=sha(BASE/'remote_sha_verification.json'),baseline_receipt_sha256=sha(BAS/'receipt.json'),selection_sha256=sha(SEL),parent_path=str(RAW),parent_sha256=sha(RAW),config_sha256=sha(cfg),transfer_note='Initial archive exit 2: nonexistent config/sf7_production.json only; all requested outputs present and verified. Actual config/sf7_job.json retrieved and verified separately.',auth_refresh=False,git_writes=False,submitted=False))
 print('readback verified',flush=True)
def compact():
 sel={r['id']:r for r in rows(SEL)};assert len(sel)==124669
 for name,p in [('A',OUT/'release/overlay_A.jsonl.gz'),('B',OUT/'release/overlay_B.jsonl.gz'),('sf6',BAS/'release/overlay_ensemble_ab.jsonl.gz')]:
  target=BASE/f'compact_{name}.jsonl';count=collections.Counter();seen=set()
  with target.open('w') as f:
   for r in rows(p):
    lid=r['line_id'];assert lid in sel and lid not in seen;seen.add(lid);s=sel[lid]
    assert r['original_label_sha256']==hashlib.sha256(s['label'].encode()).hexdigest()
    count[r['status']]+=1
    out={k:r[k] for k in ('line_id','status','label','original_label_sha256','policy_sha','rule_traces','alias_only') if k in r}
    if r['status']=='corrected':
     out['changes']=[{k:v for k,v in c.items() if k!='evidence'} for c in r['changes']]
     if name=='sf6':
      out['deletion_checks']=r.get('deletion_checks',[])
    out['wave']=s['wave'];f.write(json.dumps(out,ensure_ascii=False)+'\n')
  assert seen==set(sel);print(name,dict(count),flush=True)
if __name__=='__main__':
 verify();compact()
