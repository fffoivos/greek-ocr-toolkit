"""Commit sol/seg-gate in a writable isolated Git dir, never shared refs or push."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

D=Path(__file__).resolve().parent
ROOT=D.parents[4]


def run(args,**kwargs):
    return subprocess.check_output(args,cwd=ROOT,text=True,**kwargs).strip()


def main():
    initial=json.loads((D/'initial_state.json').read_text())
    for name,expected in initial['protected'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
    assert run(['git','rev-parse','HEAD'])==initial['head']
    assert run(['git','diff','--stat'])==initial['initial_diff_stat'].strip()
    parent=run(['git','rev-parse','sol/seg-deskew'])
    assert parent=='cb042ae4ff74bb99c546e8af4de4b3e944aa2339'
    assert run(['git','rev-parse',parent+'^'])==initial['base']
    common=Path(run(['git','rev-parse','--path-format=absolute','--git-common-dir']))
    gitdir=Path(tempfile.mkdtemp(prefix='seg-gate-commit-',dir='/private/tmp'))/'repo.git'
    subprocess.run(['git','init','--bare','--quiet',str(gitdir)],cwd=ROOT,check=True)
    (gitdir/'objects/info/alternates').write_text(str(common/'objects')+'\n')
    author=run(['git','var','GIT_AUTHOR_IDENT']);m=re.fullmatch(r'(.*) <([^>]+)> (\d+) ([+-]\d+)',author);assert m
    for key,value in [('user.name',m[1]),('user.email',m[2])]:run(['git','--git-dir='+str(gitdir),'config',key,value])
    git=['git','--git-dir='+str(gitdir),'--work-tree='+str(ROOT)]
    run(git+['read-tree',parent])
    production=['greekocr/harvest/line_pipeline_native.py','greekocr/harvest/filtering_assets/crop-tools.py',
        'greekocr/harvest/filtering_assets/segmentation-policy.js','scripts/harvest/build_filter_versions.py',
        'docs/harvest/line_pipeline/tool_versions.json']
    owned=production+['tests/test_seg_gate.py','tests/test_seg_deskew.py']
    excluded={'HANDOFF.md','SEGGATE1.bundle','bundle_receipt.json'}
    owned += [str(p.relative_to(ROOT)) for p in sorted(D.rglob('*')) if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts]
    assert not set(owned)&set(initial['protected'])
    run(git+['add','-f','--',*owned])
    changed=run(git+['diff','--cached','--name-only',parent]).splitlines()
    assert set(changed)==set(owned)
    patch=subprocess.check_output(git+['diff','--cached',parent,'--',*production,'tests/test_seg_gate.py','tests/test_seg_deskew.py'],cwd=ROOT)
    (D/'code_git_diff.patch').write_bytes(patch)
    run(git+['add','-f','--',str((D/'code_git_diff.patch').relative_to(ROOT))])
    tree=run(git+['write-tree'])
    implementation=run(git+['commit-tree',tree,'-p',parent],input='Gate segmentation on crop line inventory and cut evidence before length (0.7)\n\nSEG-GATE-1: retain frozen predictor and length/padding arithmetic, add crop-only whole-word and complete-line inventory, record all cut evidence, and make context optional diagnostics. Include offline tests and complete 150/888 replays with owner-standard scores and regression evidence.\n')
    subprocess.run([str(ROOT/'.venv/bin/python'),str(D/'write_handoff.py'),implementation],cwd=ROOT,check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    run(git+['add','-f','--',str((D/'HANDOFF.md').relative_to(ROOT))])
    doc_tree=run(git+['write-tree'])
    head=run(git+['commit-tree',doc_tree,'-p',implementation],input='Record SEG-GATE-1 hand-off and implementation commit\n')
    run(git+['update-ref','refs/heads/sol/seg-gate',head])
    run(git+['symbolic-ref','HEAD','refs/heads/sol/seg-gate'])
    bundle=D/'SEGGATE1.bundle'
    run(git+['bundle','create',str(bundle),'sol/seg-gate','^'+parent])
    verification=subprocess.run(git+['bundle','verify',str(bundle)],cwd=ROOT,text=True,capture_output=True,check=True)
    # Independently import the portable branch into another isolated repo.
    verifydir=Path(tempfile.mkdtemp(prefix='seg-gate-verify-',dir='/private/tmp'))/'repo.git'
    subprocess.run(['git','init','--bare','--quiet',str(verifydir)],cwd=ROOT,check=True)
    (verifydir/'objects/info/alternates').write_text(str(common/'objects')+'\n')
    verifygit=['git','--git-dir='+str(verifydir)]
    run(verifygit+['fetch','--quiet',str(bundle),'refs/heads/sol/seg-gate:refs/heads/sol/seg-gate'])
    assert run(verifygit+['rev-parse','sol/seg-gate'])==head
    assert run(verifygit+['rev-parse',implementation+'^'])==parent
    assert run(verifygit+['rev-parse',head+'^'])==implementation
    final_paths=run(verifygit+['diff-tree','--no-commit-id','--name-only','-r',parent,head]).splitlines()
    expected=set(owned)|{str((D/'HANDOFF.md').relative_to(ROOT)),str((D/'code_git_diff.patch').relative_to(ROOT))}
    assert set(final_paths)==expected
    for name in final_paths:
        committed=subprocess.check_output(verifygit+['show',head+':'+name],cwd=ROOT)
        assert committed==(ROOT/name).read_bytes(),name
    for name,expected_sha in initial['protected'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected_sha
        assert run(verifygit+['rev-parse',head+':'+name])==run(['git','rev-parse',parent+':'+name])
    assert run(['git','rev-parse','HEAD'])==initial['head']
    assert run(['git','diff','--stat'])==initial['initial_diff_stat'].strip()
    receipt=dict(status='PASS_PORTABLE_BUNDLE_SHARED_GIT_BLOCKED',branch_in_bundle='sol/seg-gate',
        requested_code_base=initial['base'],parent_branch='sol/seg-deskew',parent_commit=parent,
        implementation_commit=implementation,handoff_commit=head,isolated_git_dir=str(gitdir),
        independent_import_git_dir=str(verifydir),bundle=str(bundle.relative_to(ROOT)),
        bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),bundle_bytes=bundle.stat().st_size,
        committed_paths=final_paths,committed_file_bytes_verified=len(final_paths),
        bundle_verify_stdout=verification.stdout,bundle_verify_stderr=verification.stderr,
        shared_worktree_branch=run(['git','branch','--show-current']),shared_refs_and_index_untouched=True,
        protected_files_not_staged=True,protected_blobs_unchanged_in_commit=True,never_pushed=True)
    (D/'bundle_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['committed_paths','bundle_verify_stdout','bundle_verify_stderr']},indent=2))


if __name__=='__main__':main()
