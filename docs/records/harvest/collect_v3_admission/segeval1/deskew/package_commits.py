"""Package scoped commits without writing the sandbox's read-only shared Git dir."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

D=Path(__file__).resolve().parent;ROOT=D.parents[4]
base='602938bb54b728c3136c5e98493cac3fba651db7'

def run(args,**kwargs):
    return subprocess.check_output(args,cwd=ROOT,text=True,**kwargs).strip()

assert run(['git','rev-parse','HEAD'])==base
assert run(['git','branch','--show-current'])=='sol/recut-v1'
initial=json.loads((D/'initial_state.json').read_text())
assert run(['git','diff','--stat'])==initial['initial_diff_stat'].strip()
for name,sha in initial['protected_sha256'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha
common=Path(run(['git','rev-parse','--path-format=absolute','--git-common-dir']))
gitdir=Path(tempfile.mkdtemp(prefix='seg-deskew-commit-',dir='/private/tmp'))/'repo.git'
subprocess.run(['git','init','--bare','--quiet',str(gitdir)],cwd=ROOT,check=True)
(gitdir/'objects/info/alternates').write_text(str(common/'objects')+'\n')
author=run(['git','var','GIT_AUTHOR_IDENT'])
m=re.fullmatch(r'(.*) <([^>]+)> (\d+) ([+-]\d+)',author);assert m
for key,value in [('user.name',m[1]),('user.email',m[2])]:
    run(['git','--git-dir='+str(gitdir),'config',key,value])
git=['git','--git-dir='+str(gitdir),'--work-tree='+str(ROOT)]
run(git+['read-tree',base])
owned=[
 'greekocr/harvest/line_pipeline_native.py',
 'greekocr/harvest/filtering_assets/crop-tools.py',
 'scripts/harvest/build_filter_versions.py',
 'docs/harvest/line_pipeline/tool_versions.json',
 'tests/test_seg_deskew.py',
]
excluded={'HANDOFF.md','SEGDESKEW1.bundle','bundle_receipt.json'}
owned += [str(p.relative_to(ROOT)) for p in sorted(D.rglob('*')) if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts]
protected=set(initial['protected_sha256']);assert not (set(owned)&protected)
run(git+['add','-f','--',*owned])
changed=run(git+['diff','--cached','--name-only',base]).splitlines()
assert set(changed)==set(owned)
tree=run(git+['write-tree'])
implementation=run(git+['commit-tree',tree,'-p',base],input='Measure segmentation boxes in the detected row frame (0.6)\n\nSEG-DESKEW-1: preserve frozen policy/predictor, use text-component ink in the main baseline frame, and apply the owner padding input. Include 150/888 replay evidence and offline tests.\n')
subprocess.run([str(ROOT/'.venv/bin/python'),str(D/'write_handoff.py'),implementation],cwd=ROOT,check=True)
run(git+['add','-f','--',str((D/'HANDOFF.md').relative_to(ROOT))])
doc_tree=run(git+['write-tree'])
head=run(git+['commit-tree',doc_tree,'-p',implementation],input='Record SEG-DESKEW-1 hand-off and implementation commit\n')
run(git+['update-ref','refs/heads/sol/seg-deskew',head])
run(git+['symbolic-ref','HEAD','refs/heads/sol/seg-deskew'])
bundle=D/'SEGDESKEW1.bundle'
run(git+['bundle','create',str(bundle),'sol/seg-deskew','^'+base])
verification=subprocess.run(git+['bundle','verify',str(bundle)],cwd=ROOT,text=True,capture_output=True,check=True)
# Readback of the real commits and the complete hand-off bytes.
assert run(git+['rev-parse',implementation+'^'])==base
assert run(git+['rev-parse',head+'^'])==implementation
committed_handoff=subprocess.check_output(git+['show',head+':'+str((D/'HANDOFF.md').relative_to(ROOT))],cwd=ROOT)
assert committed_handoff==(D/'HANDOFF.md').read_bytes()
assert run(['git','branch','--show-current'])=='sol/recut-v1'
assert run(['git','diff','--stat'])==initial['initial_diff_stat'].strip()
receipt=dict(status='PORTABLE_COMMIT_BUNDLE_CREATED_SHARED_GIT_BLOCKED',
 branch_in_bundle='sol/seg-deskew',base=base,implementation_commit=implementation,handoff_commit=head,
 isolated_git_dir=str(gitdir),bundle=str(bundle.relative_to(ROOT)),bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),
 bundle_bytes=bundle.stat().st_size,implementation_paths=changed,
 handoff_paths=run(git+['diff-tree','--no-commit-id','--name-only','-r',head]).splitlines(),
 bundle_verify_stdout=verification.stdout,bundle_verify_stderr=verification.stderr,
 shared_worktree_branch='sol/recut-v1',shared_refs_and_index_untouched=True,
 protected_files_not_staged=True,never_pushed=True)
(D/'bundle_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('implementation_paths','handoff_paths','bundle_verify_stdout','bundle_verify_stderr')},indent=2))
