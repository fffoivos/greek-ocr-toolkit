"""Run over SSH stdin on Clariden; hashes files and checks receipt bindings, read-only."""
import json,hashlib,pathlib,collections
ROOT=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019')
RUN=ROOT/'output_3702849'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
files={str(p.relative_to(RUN)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(RUN.rglob('*')) if p.is_file()}
checks=[]
def check(p,h,src):
 p=pathlib.Path(p)
 if not p.is_absolute():p=ROOT/p
 assert p.is_file(),(str(p),src)
 rel=str(p.relative_to(RUN)) if str(p).startswith(str(RUN)+'/') else None
 actual=files[rel]['sha256'] if rel else sha(p)
 assert actual==h,(str(p),h,actual,src)
 checks.append({'path':str(p),'sha256':h,'receipt':src})
def resolve(n,base):
 p=pathlib.Path(n)
 if p.is_absolute():return p
 for parent in (base,ROOT,RUN):
  if (parent/p).is_file():return parent/p
 raise ValueError((n,str(base)))
def maps(v,base,src):
 if isinstance(v,dict):
  for k,x in v.items():
   if isinstance(x,str) and len(x)==64 and (('/' in k or '.' in k) and not k.endswith('_sha256')):
    check(resolve(k,base),x,src)
   else:maps(x,base,src)
 elif isinstance(v,list):
  for x in v:maps(x,base,src)
for name in files:
 p=RUN/name
 if p.suffix=='.json' and ('receipt' in p.name.lower() or 'summary' in p.name or p.name.startswith('release_')):
  r=load(p);maps(r,p.parent,name)
  if 'output_sha256' in r:check(resolve(r['output'],p.parent),r['output_sha256'],name)
  if 'input_sha256' in r:check(resolve(r['input'],p.parent),r['input_sha256'],name)
  if p.name.startswith('worker_'):
   check(p.with_name(p.name.replace('.summary.json','.jsonl.gz')),r['alignment_sha256'],name)
cfg=load(ROOT/'config/tr2_job.json');r=load(RUN/'receipt.json')
assert r['complete'] and r['inference_executed'] and not r['dry_run']
assert r['status']=='candidate_pre_audit' and r['bound'] is False and r['release_id']=='sf7_rc1_test_edits_A'
POL='f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047';PRE='64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d'
assert r['intake']['policy_digest']==POL and r['intake']['preregistration_sha256']==PRE
for s,c in cfg['splits'].items():
 b=RUN/s;rr=load(b/f'RELEASE_RECEIPT_{s}.json');assert rr==r['releases'][s]
 assert rr['status']=='candidate_pre_audit' and rr['bound'] is False
 assert rr['policy_digest']==POL and rr['preregistration_sha256']==PRE and rr['source_job']=='3702849'
 check(c['source'],c['sha256'],s+' package parent');check(resolve(c['ids'],ROOT),c['ids_sha256'],s+' package ids')
 assert rr['parent_sha256']==c['sha256']
 for p,h in [(b/'selection.jsonl',rr['selection_sha256']),(b/'crop_inventory.jsonl',r['intake']['splits'][s]['inventory_sha256']),(b/'sf7/release/overlay_A.jsonl.gz',rr['overlay_sha256']),(pathlib.Path(rr['path']),rr['sha256']),(b/'binding/binding.json',load(b/'l1/run_receipt.json')['binding_sha256']),(b/'recogniser_scores.jsonl.gz',load(b/'scores_receipt.json')['sha256'])]:check(p,h,s+' receipt')
 for fn in ('release_A.json','release_ctrl_subset_A.json'):
  m=load(b/'sf7/release'/fn);assert m['policy_sha']==POL and m['preregistration_sha256']==PRE
  check(b/'sf7/release'/m['overlay'],m['overlay_sha256'],fn)
  check(b/'sf7/release'/m['kept_line_ids'],m['kept_line_ids_sha256'],fn)
  if 'labels_file' in m:check(b/'sf7/release'/m['labels_file'],m['labels_sha256'],fn)
  for path,h in m['policy_binding']['sources'].items():check(ROOT/path,h,fn+' policy')
covered={str(pathlib.Path(x['path']).relative_to(RUN)) for x in checks if x['path'].startswith(str(RUN)+'/')}
result={'all_ok':True,'root':str(ROOT),'run':str(RUN),'receipt_sha256':files['receipt.json']['sha256'],'files':files,'checks':checks,'receipt_bound_files':len(covered),'not_referenced_by_receipt':sorted(set(files)-covered),'config_sha256':sha(ROOT/'config/tr2_job.json'),'log_sha256':sha(ROOT/'logs/TR2_3702849.log')}
print(json.dumps(result,ensure_ascii=False,indent=2))
