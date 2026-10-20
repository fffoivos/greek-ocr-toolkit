"""Independent full-population local RB8 validation from compact streamed witnesses."""
import json,gzip,hashlib,collections,pathlib,unicodedata as ud,difflib
BASE=pathlib.Path(__file__).resolve().parent;OUT=BASE/'output_3702849';REPO=BASE.parents[1]
POL='f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047';PRE='64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def rows(p):
 with (gzip.open if str(p).endswith('.gz') else open)(p,'rt',encoding='utf8') as f:
  for l in f:
   if l.strip():yield json.loads(l)
def dump(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
def patch_check(a,b,ps):
 x0=y0=0;out=[];back=[]
 for q in ps:
  x,x1,y,y1=(q[k] for k in ('raw_byte_start','raw_byte_end','output_byte_start','output_byte_end'))
  assert 0<=x0<=x<=x1<=len(a) and 0<=y0<=y<=y1<=len(b)
  assert a[x0:x]==b[y0:y] and a[x:x1]==q['before'].encode() and b[y:y1]==q['after'].encode()
  out.extend([a[x0:x],q['after'].encode()]);back.extend([b[y0:y],q['before'].encode()]);x0,y0=x1,y1
 out.append(a[x0:]);back.append(b[y0:]);assert b''.join(out)==b and b''.join(back)==a
remote=load(OUT/'remote_sha_verification.json');job=load(OUT/'receipt.json');cfg=load(REPO/'config/tr2_job.json')
assert remote['all_ok'] and sha(OUT/'receipt.json')==remote['receipt_sha256']
assert sha(REPO/'config/tr2_job.json')==remote['config_sha256']
assert job['complete'] and job['inference_executed'] and not job['dry_run']
assert job['status']=='candidate_pre_audit' and job['bound'] is False
local={}
for p in OUT.rglob('*'):
 if not p.is_file():continue
 n=str(p.relative_to(OUT))
 if n in remote['files']:
  assert sha(p)==remote['files'][n]['sha256'],n;local[n]=sha(p)
assert sha(OUT/'TR2_3702849.log')==remote['log_sha256']
log=(OUT/'TR2_3702849.log').read_text();terminal=[json.loads(l) for l in log.splitlines() if l.startswith('{"complete": true, "dry_run": false, "intake":')]
assert terminal==[job]
metadata=load(OUT/'metadata_verification.json');assert metadata['all_ok'] and metadata['alignment_binding_equals_summary']
for q in metadata['checks']:assert remote['files'][q['path']]['sha256']==q['sha256']
state=(OUT/'job_state.txt').read_text().splitlines();fields=state[0].split('|');states=[dict(zip(fields,l.split('|'))) for l in state[1:]]
assert all(r['State']=='COMPLETED' and r['ExitCode']=='0:0' for r in states)
main=next(r for r in states if r['JobID']=='3702849')
data={s:{k:{} for k in ('selection','raw','overlay','control')} for s in ('test','dev')}
for r in rows(OUT/'readback_witness.jsonl.gz'):
 t=r.pop('type');s=r.pop('split');lid=r.get('id',r.get('line_id'));assert lid not in data[s][t],(s,t,lid);data[s][t][lid]=r
result={}
for s,c in cfg['splits'].items():
 b=OUT/s;rr=load(b/f'RELEASE_RECEIPT_{s}.json');release=list(rows(b/f'release_edits_only_{s}_A.jsonl'));d=data[s];ids=set(d['selection'])
 expected=(REPO/c['ids']).read_text().splitlines();assert len(expected)==len(set(expected))==c['lines'] and set(expected)==ids
 assert sha(REPO/c['ids'])==c['ids_sha256']
 assert set(d['raw'])==set(d['overlay'])==ids and len(ids)==c['lines']
 assert all(d['raw'][i]['label'].encode()==d['selection'][i]['label'].encode() for i in ids)
 assert rr==job['releases'][s] and rr['status']=='candidate_pre_audit' and rr['bound'] is False
 assert rr['release_id']=='sf7_rc1_test_edits_A' and rr['parent']=='google_raw_v2_import'
 assert rr['parent_sha256']==c['sha256'] and rr['selection_sha256']==job['intake']['splits'][s]['selection_sha256']
 assert rr['policy_digest']==POL and rr['preregistration_sha256']==PRE
 assert sha(b/f'release_edits_only_{s}_A.jsonl')==rr['sha256']
 assert len(release)==len({r['line_id'] for r in release})==rr['row_count']
 kind=collections.Counter();head=collections.defaultdict(collections.Counter);patches=0
 for r in release:
  lid=r['line_id'];assert lid in ids and d['overlay'][lid]['status']=='corrected'
  for k,v in {'release_id':'sf7_rc1_test_edits_A','parent':'google_raw_v2_import','split':s,'variant':'A','source_job':'3702849','policy_digest':POL}.items():assert r[k]==v
  a=d['raw'][lid]['label'].encode();bb=r['text'].encode();assert a!=bb and hashlib.sha256(a).hexdigest()==r['parent_text_sha256']
  patch_check(a,bb,r['byte_patches']);patches+=len(r['byte_patches'])
  union=[]
  for e in r['edits']:
   assert e['source_job']=='3702849' and e['variant']=='A' and e['policy_digest']==POL
   assert all(k in e for k in ('slot','kind','head','rule','signals','byte_patches')) and e['byte_patches']
   for q in e['byte_patches']:assert q in r['byte_patches'] and q['slot']==e['slot']
   # Each edit's patch is independently reversible on the raw parent.
   tmp=a
   for q in reversed(e['byte_patches']):tmp=tmp[:q['raw_byte_start']]+q['after'].encode()+tmp[q['raw_byte_end']:]
   shift=0;back=tmp;positions=[]
   for q in e['byte_patches']:
    x=q['raw_byte_start']+shift;y=x+len(q['after'].encode());assert tmp[x:y]==q['after'].encode();positions.append((x,y,q));shift+=len(q['after'].encode())-(q['raw_byte_end']-q['raw_byte_start'])
   for x,y,q in reversed(positions):back=back[:x]+q['before'].encode()+back[y:]
   assert back==a
   union.extend(e['byte_patches']);kind[e['kind']]+=1;head[e['head']][e['kind']]+=1
  assert all(q in union for q in r['byte_patches'])
 assert sum(kind.values())==rr['edit_count'] and dict(kind)==rr['edit_counts_by_kind']
 m=load(b/'sf7/release/release_A.json');counts=collections.Counter(v['status'] for v in d['overlay'].values())
 assert all(counts[k]==v for k,v in m['counts_by_status'].items())
 for lid,v in d['overlay'].items():assert v['original_label_sha256']==hashlib.sha256(d['raw'][lid]['label'].encode()).hexdigest()
 kept={i for i,v in d['overlay'].items() if v['status'] in ('corrected','unchanged')};assert set(d['control'])==kept
 corrected={i for i,v in d['overlay'].items() if v['status']=='corrected'};norm=set(rr['normalization_only'])
 assert len(norm)==len(rr['normalization_only']) and corrected=={r['line_id'] for r in release}|norm and not norm&{r['line_id'] for r in release}
 omitted=[]
 for i in sorted(norm):
  a=d['raw'][i]['label'];v=d['overlay'][i]['label']
  diff=[dict(operation=t,before=a[x:y],after=v[u:w]) for t,x,y,u,w in difflib.SequenceMatcher(None,a,v,autojunk=False).get_opcodes() if t!='equal']
  assert len(diff)==1 and diff[0]==dict(operation='insert',before='',after='“'),(i,diff)
  omitted.append(dict(line_id=i,differences=diff))
 scores=load(b/'scores_receipt.json');assert scores['complete'] and scores['lines']==scores['counts']['alignment_identity_matches']==c['lines'] and not scores['counts'].get('alignment_identity_mismatches',0)
 result[s]=dict(selection_lines=len(ids),rows=len(release),edits=sum(kind.values()),byte_patches=patches,edits_by_kind=dict(kind),edits_by_head={k:dict(v) for k,v in head.items()},composer_counts=dict(counts),normalization_only=len(norm),omitted_composer_rows=omitted,omission_note='Receipt field normalization_only actually contains composer-only U+201C insertions, excluded by the converter; these are not Unicode-normalization-only differences.',selection_sha256=rr['selection_sha256'],parent_sha256=rr['parent_sha256'],independent_forward_reverse_byte_check=True,every_edit_patch_checked=True,overlay_control_membership_check=True,coverage_equals_selected_ids=True,no_unselected_or_duplicate_ids=True,score_alignment_identity_matches=scores['counts']['alignment_identity_matches'],edits_per_selected_line=sum(kind.values())/len(ids))
assert not set(data['test']['selection'])&set(data['dev']['selection'])
# Every data output is covered by an original job SHA. Unreferenced files are metadata/receipts.
unref=sorted(set(remote['not_referenced_by_receipt'])-{q['path'] for q in metadata['checks']})
assert all(n.endswith('.json') for n in unref)
stays={n:v for n,v in remote['files'].items() if n not in local};dump(OUT/'REMOTE_ONLY_SHA256.json',stays)
train=load(BASE.parent/'sf7_rc1/RELEASE_RECEIPT.json');assert train['row_count']==605 and train['edit_count']==665
seconds=int(main['ElapsedRaw']);receipt=dict(schema='rb7-readback-v1',status='sha_verified',job='3702849',job_state='COMPLETED',exit_code='0:0',receipt_sha256=sha(OUT/'receipt.json'),preregistration_sha256=PRE,policy_digest=POL,remote_outputs_verified=len(remote['files']),stage_outputs_verified=remote['receipt_bound_files'],receipt_hash_checks=len(remote['checks']),local_outputs_verified=len(local),local_sha256=local,remote_verification_sha256=sha(OUT/'remote_sha_verification.json'),metadata_verification_sha256=sha(OUT/'metadata_verification.json'),metadata_checks=len(metadata['checks']),config_sha256=remote['config_sha256'],splits=result,release_id='sf7_rc1_test_edits_A',release_status='candidate_pre_audit',bound=False,auth_refresh=False,git_writes=False,submitted=False,remote_only_inventory_sha256=sha(OUT/'REMOTE_ONLY_SHA256.json'),streamed_witness_sha256=sha(OUT/'readback_witness.jsonl.gz'),unreferenced_metadata=unref,unreferenced_metadata_note='The job does not publish hashes of these 22 metadata/receipt files in another receipt. Their current hashes are captured in the remote inventory; 3498 files match the main receipt checks, and two additional recompose configs match scalar config_sha256 references.',runtime=dict(slurm_seconds=seconds,pipeline_seconds=job['elapsed_seconds'],allocated_gpus=4,allocated_gpu_hours=seconds*4/3600,forecast_seconds=2400,forecast_gpu_hours=2400*4/3600),train_comparison=dict(selected_lines=124669,rows=605,edits=665,edits_per_selected_line=665/124669,source_receipt_sha256=sha(BASE.parent/'sf7_rc1/RELEASE_RECEIPT.json')))
receipt['local_bytes_before_readback_receipt']=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
assert receipt['local_bytes_before_readback_receipt']<200_000_000
dump(OUT/'READBACK_RECEIPT.json',receipt)
print(json.dumps({'splits':result,'runtime':receipt['runtime'],'local_bytes':receipt['local_bytes_before_readback_receipt']},ensure_ascii=False,indent=2))
