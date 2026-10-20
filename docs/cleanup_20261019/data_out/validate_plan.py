"""Validate coverage and proposals without changing source, artifacts or git state."""
import csv,hashlib,json,os,pathlib,re,subprocess
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];os.chdir(R)
S=json.loads((O/'snapshot.json').read_text());orig={x['path']:x for x in S['rows']};A=json.loads((O/'AUDIT.json').read_text())
csv.field_size_limit(100_000_000)
seen=set();move=set();large=0;total=0;movetotal=0;special={}
with (O/'MOVE_PLAN.tsv').open(newline='') as f:
 for x in csv.DictReader(f,delimiter='\t'):
  p=x['path'];assert p not in seen;seen.add(p);o=orig[p]
  assert int(x['bytes'])==o['bytes'] and x['sha256']==o['sha256']
  assert re.fullmatch('[0-9a-f]{64}',x['sha256'])
  assert x['producing_commit']==o['producing_commit'] and x['readers']
  if int(x['bytes'])>5_000_000:large+=1;assert x['decision']=='MOVE'
  if x['decision']=='MOVE':move.add(p);movetotal+=int(x['bytes'])
  total+=int(x['bytes'])
  if p.endswith(('n1_v1_train.sha256','truth_v1_1.sha256','census02_segmentation_evidence.jsonl')):special[p]=x['decision'];assert x['decision'].startswith('KEEP')
assert seen==set(orig) and len(move)==A['move_count'] and movetotal==A['move_bytes']
assert large==232 and total==A['tracked_bytes']
index={x.split(b'\t',1)[1].decode():x.split(b'\t',1)[0].decode().split()[1] for x in subprocess.check_output(['git','ls-files','-s','-z']).split(b'\0') if x}
assert set(index)==seen and all(index[p]==orig[p]['oid'] for p in seen)
assert subprocess.check_output(['git','show','-s','--format=%H %D','HEAD'],text=True).strip()==S['head']
for p,expected in S['stats'].items():
 st=(R/p).lstat();assert [st.st_size,st.st_mtime_ns,st.st_mode]==expected,('source metadata changed',p)
patterns=[re.sub(r'\\(.)',r'\1',x[1:]) for x in (O/'.gitignore.proposed').read_text().splitlines() if x.startswith('/')]
exact={x for x in patterns if not x.endswith('/')};dirs={x for x in patterns if x.endswith('/')}
for p in seen:
 ignored=p in exact or any(str(d)+'/' in dirs for d in pathlib.PurePosixPath(p).parents)
 assert ignored==(p in move),('ignore coverage',p,ignored)
refs=json.loads((O/'readers.json').read_text());sample=[]
for name in ['SEGEVAL1.bundle','candidate_order_KEEP.jsonl','population_cells.jsonl.gz','truth_v1_1.jsonl','n1_v1_train.jsonl','receipt.json','initial_hashes.json']:
 q=subprocess.run(['rg','--files-with-matches','--null','--no-ignore','--hidden','--fixed-strings','--glob','!.git/**','--glob','!docs/cleanup_20261019/data_out/**','--',name,'.'],capture_output=True)
 assert q.returncode in (0,1)
 got={x.decode().removeprefix('./') for x in q.stdout.split(b'\0') if x}
 assert got==set(refs.get(name,[])),('reader scan mismatch',name,len(got),len(refs.get(name,[])))
 sample.append(dict(basename=name,reference_files=len(got),independent_grep_equal=True))
validation=dict(HEAD=S['head'],TSV_rows=len(seen),MOVE_count=len(move),MOVE_bytes=movetotal,oversized_count=large,all_HEAD_paths_covered=True,all_TSV_hashes_and_sizes_match_verified_snapshot=True,all_producing_commits_exact_path_log_results=True,index_object_ids_unchanged=True,HEAD_unchanged=True,all_tracked_lstat_metadata_unchanged=True,ignore_rules_cover_all_MOVE_and_no_KEEP_or_ASK_paths=True,retained_segmentation_receipt_exceptions=special,reader_grep_spotchecks=sample,proposed_guard_expected_failure_count=232,no_moves_performed=True,no_git_writing_commands_used=True)
(O/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps(validation,indent=2))
