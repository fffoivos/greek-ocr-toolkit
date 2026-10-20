"""Create sol/seg-gate2 from exact 67e670ba in the authorised bundle fallback."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

D=Path(__file__).resolve().parent
ROOT=D.parents[4]


def run(args,**kwargs):return subprocess.check_output(args,cwd=ROOT,text=True,**kwargs).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    initial=json.loads((D/'initial_state.json').read_text());parent=initial['base']
    assert parent=='67e670bac293b55afed32c1da823173344e33a38'
    assert run(['git','rev-parse','sol/seg-gate^'])==parent
    for group in ('protected','predictor','immutable_sources'):
        for name,expected in initial[group].items():assert sha(ROOT/name)==expected,name
    assert run(['git','rev-parse','HEAD'])==initial['head']
    assert subprocess.check_output(['git','diff','--stat'],cwd=ROOT,text=True)==initial['initial_diff_stat']
    shared_refs=run(['git','for-each-ref','--format=%(refname) %(objectname)'])
    shared_index=Path(run(['git','rev-parse','--path-format=absolute','--git-path','index']));index_sha=sha(shared_index)
    common=Path(run(['git','rev-parse','--path-format=absolute','--git-common-dir']))
    gitdir=Path(tempfile.mkdtemp(prefix='seg-gate2-commit-',dir='/private/tmp'))/'repo.git'
    subprocess.run(['git','init','--bare','--quiet',str(gitdir)],cwd=ROOT,check=True)
    (gitdir/'objects/info/alternates').write_text(str(common/'objects')+'\n')
    author=run(['git','var','GIT_AUTHOR_IDENT']);m=re.fullmatch(r'(.*) <([^>]+)> (\d+) ([+-]\d+)',author);assert m
    for key,value in [('user.name',m[1]),('user.email',m[2])]:run(['git','--git-dir='+str(gitdir),'config',key,value])
    git=['git','--git-dir='+str(gitdir),'--work-tree='+str(ROOT)]
    run(git+['read-tree',parent])
    production=['greekocr/harvest/filtering_assets/segmentation-policy.js','greekocr/harvest/filtering_assets/crop-tools.py','scripts/harvest/build_filter_versions.py','docs/harvest/line_pipeline/tool_versions.json']
    code=production+['tests/test_seg_gate.py']
    run(git+['add','-f','--',*code])
    patch=subprocess.check_output(git+['diff','--cached',parent,'--',*code],cwd=ROOT)
    (D/'code_git_diff.patch').write_bytes(patch)
    spec=importlib.util.spec_from_file_location('gate2_handoff',D/'write_handoff.py');report=importlib.util.module_from_spec(spec);spec.loader.exec_module(report)
    for cohort in ('segeval1','calibration'):report.flip_table(cohort)
    excluded={'HANDOFF.md','SEGGATE2.bundle','bundle_receipt.json'}
    artifacts=[str(p.relative_to(ROOT)) for p in sorted(D.rglob('*')) if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts]
    owned=code+artifacts
    assert not set(owned)&set(initial['protected'])
    run(git+['add','-f','--',*artifacts])
    changed=run(git+['diff','--cached','--name-only',parent]).splitlines()
    assert set(changed)==set(owned),(set(changed)-set(owned),set(owned)-set(changed))
    tree=run(git+['write-tree'])
    implementation=run(git+['commit-tree',tree,'-p',parent],input="Restore segmentation to exactly the owner's three rules (0.8)\n\nSEG-GATE-2: remove target-line-cut veto and taller-than-upright guard; retain skew diagnostics and crop-only inventory. Freeze predictor and length/padding functions. Include 157 passing tests, offline 150/888 native replays, four-version owner-standard/rating comparisons, exhaustive flips and independent readback/scope guards.\n")
    subprocess.run([str(ROOT/'.venv/bin/python'),str(D/'write_handoff.py'),implementation],cwd=ROOT,check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    handoff=str((D/'HANDOFF.md').relative_to(ROOT))
    run(git+['add','-f','--',handoff])
    doc_tree=run(git+['write-tree'])
    head=run(git+['commit-tree',doc_tree,'-p',implementation],input='Record SEG-GATE-2 hand-off and implementation commit\n')
    run(git+['update-ref','refs/heads/sol/seg-gate2',head])
    run(git+['symbolic-ref','HEAD','refs/heads/sol/seg-gate2'])
    bundle=D/'SEGGATE2.bundle'
    run(git+['bundle','create',str(bundle),'sol/seg-gate2','^'+parent])
    verification=subprocess.run(git+['bundle','verify',str(bundle)],cwd=ROOT,text=True,capture_output=True,check=True)
    # Independent local-only import; no network and no shared Git mutation.
    verifydir=Path(tempfile.mkdtemp(prefix='seg-gate2-verify-',dir='/private/tmp'))/'repo.git'
    subprocess.run(['git','init','--bare','--quiet',str(verifydir)],cwd=ROOT,check=True)
    (verifydir/'objects/info/alternates').write_text(str(common/'objects')+'\n')
    verifygit=['git','--git-dir='+str(verifydir)]
    run(verifygit+['fetch','--quiet',str(bundle),'refs/heads/sol/seg-gate2:refs/heads/sol/seg-gate2'])
    assert run(verifygit+['rev-parse','sol/seg-gate2'])==head
    assert run(verifygit+['rev-parse',implementation+'^'])==parent
    assert run(verifygit+['rev-parse',head+'^'])==implementation
    assert run(verifygit+['rev-list','--count',parent+'..'+head])=='2'
    final_paths=run(verifygit+['diff-tree','--no-commit-id','--name-only','-r',parent,head]).splitlines()
    assert set(final_paths)==set(owned)|{handoff}
    assert run(verifygit+['diff-tree','--no-commit-id','--name-only','-r',implementation,head])==handoff
    for name in final_paths:assert subprocess.check_output(verifygit+['show',head+':'+name],cwd=ROOT)==(ROOT/name).read_bytes(),name
    for name,expected in initial['protected'].items():
        assert sha(ROOT/name)==expected
        assert run(verifygit+['rev-parse',head+':'+name])==run(['git','rev-parse',parent+':'+name])
    assert run(['git','for-each-ref','--format=%(refname) %(objectname)'])==shared_refs
    assert sha(shared_index)==index_sha
    assert run(['git','rev-parse','HEAD'])==initial['head']
    assert subprocess.check_output(['git','diff','--stat'],cwd=ROOT,text=True)==initial['initial_diff_stat']
    receipt=dict(status='PASS_PORTABLE_BUNDLE_SHARED_GIT_OUTSIDE_WRITABLE_ROOTS',branch_in_bundle='sol/seg-gate2',requested_code_base=parent,parent_commit=parent,implementation_commit=implementation,handoff_commit=head,isolated_git_dir=str(gitdir),independent_import_git_dir=str(verifydir),shared_common_git_dir=str(common),bundle=str(bundle.relative_to(ROOT)),bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,committed_paths=final_paths,production_paths_changed=production,test_paths_changed=['tests/test_seg_gate.py'],committed_file_bytes_verified=len(final_paths),bundle_verify_stdout=verification.stdout,bundle_verify_stderr=verification.stderr,shared_worktree_branch=run(['git','branch','--show-current']),shared_refs_unchanged=True,shared_index_sha256=index_sha,shared_index_unchanged=True,protected_files_not_staged=True,protected_blobs_unchanged_in_commit=True,never_pushed=True)
    (D/'bundle_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('committed_paths','bundle_verify_stdout','bundle_verify_stderr')},indent=2))


if __name__=='__main__':main()
