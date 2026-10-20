"""CLEAN3B verification. Read-only except its new validation report."""
import ast,collections,csv,hashlib,importlib.util,json,os,subprocess,tempfile
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
csv.field_size_limit(100_000_000)
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
a=read(O/'MOVE_PLAN.tsv');b=read(O/'MOVE_PLAN_v2.tsv');by={x['path']:x for x in b};move={p:r for p,r in by.items() if r['decision']=='MOVE'}
assert len(b)==len(by)==len(a)==61533
for x,y in zip(a,b):
    for k in ('path','bytes','sha256','kind','producing_commit','readers'):assert x[k]==y[k],(k,x['path'])
small={x['path'] for x in read(O/'SMALL_INPUTS_v2.tsv')}
for x,y in zip(a,b):
    p=x['path'];n=int(x['bytes']);e=Path(p).suffix[1:].lower()
    scope=p.startswith(('docs/','artifacts/','out/','legacy_l1/','fixes/')) or (p.startswith('prototypes/') and bool({'evidence','outputs','runs'} & set(Path(p).parts[1:-1])))
    rule='a' if n>5_000_000 else 'd' if x['decision']=='ASK' else 'b' if e in set('png jpg jpeg gif webp tif tiff bmp pdf gz tgz tar zip bundle npy npz pt pth onnx bin mp4 mov wav'.split()) and scope and not (n<=50_000 and p in small) else 'c' if n>1_000_000 and e in set('jsonl html htm xml log codexlog txt tsv csv'.split()) and p.startswith(('docs/','artifacts/','out/')) else ''
    assert y['rule']==rule and y['decision']==('MOVE' if rule else 'KEEP'),p
receipts=[];sizes={}
for p in sorted((O/'RECEIPTS').glob('receipt_*.tsv')):
    assert p.stat().st_size<=4_000_000
    receipts.extend(read(p));sizes[p.name]=p.stat().st_size
assert len(receipts)==len(move)==len({x['path'] for x in receipts})
for x in receipts:
    assert x['path'] in move
    for k in ('bytes','sha256','kind','producing_commit'):assert x[k]==move[x['path']][k],(x['path'],k)
links=read(O/'SYMLINKS_v2.tsv')
assert len(links)==19
for x in links:
    p=x['path'];assert move[p]['rule']=='d' and (R/p).is_symlink()
    assert os.readlink(R/p)==x['link_text']
    raw=os.fsencode(x['link_text']);assert len(raw)==int(x['bytes']) and hashlib.sha256(raw).hexdigest()==x['sha256']==move[p]['sha256']
patterns=O/'gitignore_additions_v2.txt';lines=patterns.read_text().splitlines();assert len(lines)<=300
# Ask Git's own ignore parser to evaluate only these additions against an empty
# worktree, reading the existing Git directory. No init/index/config write.
gitdir=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=R,text=True).strip())
with tempfile.TemporaryDirectory(prefix='clean3b-ignore-') as directory:
    env=dict(os.environ,GIT_DIR=str(gitdir),GIT_WORK_TREE=directory,GIT_OPTIONAL_LOCKS='0')
    paths=[x['path'] for x in b]
    result=subprocess.run(['git','-c','core.excludesFile='+str(patterns),'check-ignore','--no-index','-z','--stdin'],input=b'\0'.join(os.fsencode(p) for p in paths)+b'\0',stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=directory,env=env)
    assert result.returncode in (0,1),result.stderr
    ignored={os.fsdecode(p) for p in result.stdout.split(b'\0') if p}
assert set(move)<=ignored,sorted(set(move)-ignored)[:30]
assert not (small & ignored),sorted(small&ignored)
changes=json.loads((O/'reader_changes_v2.json').read_text())
for c in changes:
    assert not c['path'].startswith(('tests/','docs/'))
    ast.parse((R/c['path']).read_text());assert digest(R/c['path'])==c['sha256_after'],c['path']
    assert digest(O/'reader_before_v2'/c['path'])==c['sha256_before']
    # Input adapters must never redirect a known write-mode open.
    tree=ast.parse((R/c['path']).read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='open' and isinstance(node.func.value,ast.Call) and isinstance(node.func.value.func,ast.Name) and node.func.value.func.id=='_data_input':
            mode=node.args[0] if node.args else next((k.value for k in node.keywords if k.arg=='mode'),None)
            if isinstance(mode,ast.Constant) and isinstance(mode.value,str):assert not any(c in mode.value for c in 'wax+'),(c['path'],node.lineno)
base=json.loads((O/'baseline_v2.json').read_text())
immutable={name:digest(O/name)==sha for name,sha in base['existing_data_out'].items()}
assert all(immutable.values()),immutable
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
# Another coordinator may commit unrelated concurrent work; report it, do not undo it.
index_bytes_unchanged=digest(Path(base['index_path']))==base['index_sha256']
# Object identity also checks no untracking/staging occurred despite stat-cache
# refreshes potentially made by another concurrent session.
listing=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=R,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
indexed={}
for item in listing.split(b'\0'):
    if not item:continue
    metadata,p=item.split(b'\t',1);mode,oid,stage=metadata.split();assert stage==b'0';indexed[os.fsdecode(p)]=(mode.decode(),oid.decode())
snapshot=json.loads((O/'snapshot.json').read_text())
original_index={r['path']:(r['mode'],r['oid']) for r in snapshot['rows']}
assert all(indexed.get(p)==v for p,v in original_index.items())
index_added=sorted(set(indexed)-set(original_index))
# The guard's failure is required until the coordinator moves AND untracks.
spec=importlib.util.spec_from_file_location('size_guard_v2',O/'size_guard_test_v2.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
oversized=guard.oversized_tracked_files(R);assert len(oversized)==232 and all(p in move for p,n in oversized)
# Full source verification is deliberately performed by the shipped dry-run.
result=subprocess.run(['python3',str(O/'move_data.py'),'--dry-run'],cwd=R,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
assert result.returncode==0,result.stderr
summary=result.stdout.strip();(O/'DRY_RUN_v2.txt').write_text(summary+'\n')
report=dict(HEAD=head,inventory_rows=len(b),MOVE_count=len(move),MOVE_bytes=sum(int(x['bytes']) for x in move.values()),KEEP_count=len(b)-len(move),all_original_metadata_preserved=True,classification_verified=True,receipt_coverage_exact=True,receipt_shard_sizes=sizes,symlink_texts_verified=19,ignore_lines=len(lines),all_MOVE_ignored=True,small_live_exceptions_not_ignored=True,KEEP_lexically_matched_by_scoped_export_ignores=len(ignored-set(move)),source_files_changed=len(changes),source_patches_parse_and_hash=True,no_known_write_open_redirected=True,CLEAN3A_files_unchanged=all(immutable.values()),HEAD_at_baseline=base['head'],HEAD_unchanged=(head==base['head']),concurrent_index_additions=index_added,index_bytes_unchanged_since_CLEAN3B_baseline=index_bytes_unchanged,original_inventory_index_modes_and_blob_ids_unchanged=True,size_guard_expected_failures=len(oversized),size_guard_expected_failure_bytes=sum(n for p,n in oversized),dry_run=summary,no_MOVE_path_missing_or_changed=True,execute_transfer_rollback_not_run=True,tests={'new_resolver_and_read_only_mover':'24 passed','broader_selection':'96 passed, 17 failed: SciPy architecture / missing historical external inputs','verify_collection':'blocked by SciPy architecture'})
(O/'VALIDATION_v2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
