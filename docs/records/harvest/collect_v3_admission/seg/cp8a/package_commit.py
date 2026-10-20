"""Create additive CP8a commit atop the prior additive ADMW2 bundle, in /tmp."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1];ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    prior=json.loads((BASE/'ADMW2_COMMIT_LIST.json').read_text())
    parent=prior['commit'];base=prior['base_HEAD']
    paths=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.bundle','.patch')]
    paths += [ROOT/'greekocr/harvest'/p for p in ('qualified_admission.py','application_identity.py')]
    paths += [ROOT/'tests/test_seg_cp8a.py',BASE/'build_release_admission.py',BASE/'stage_crops.py',BASE/'admw2/test_builder.py',HERE.parent/'CP8a_RECEIPT.md']
    cp7=HERE.parent/'cp7'
    paths += [p for p in (cp7/'r2/answers/segcp7r2_b').rglob('*') if p.is_file()]
    paths += [cp7/'r2/scan/segcp7r2_b/r1.scan.json',cp7/'r2/LEAD_ADJUDICATION_r2.json',cp7/'run_r2.log',cp7/'r2/launchers/limit_probe.log']
    for prefix in ('w1_originals_v3_screened','w2_originals_v3','gazette_w2_originals_v3'):
        receipt=json.loads((BASE/(prefix+'_receipt.json')).read_text())
        paths += [BASE/f['path'] for f in receipt['files']]
        paths += [BASE/(prefix+'_receipt.json'),BASE/(prefix+'_receipt.json.application.json')]
    closure=json.loads((HERE/'application_manifest.json').read_text())
    paths.extend(ROOT/name for name in closure['files'])
    paths=sorted(set(paths))
    env=dict(os.environ)
    for key in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'):env.pop(key,None)
    def original(*a):return subprocess.check_output(['git',*a],cwd=ROOT,env=env,text=True).strip()
    assert original('rev-parse','HEAD')==base,'source HEAD changed'
    common=Path(original('rev-parse','--git-common-dir')).resolve()
    for role in ('AUTHOR','COMMITTER'):
        env['GIT_'+role+'_NAME']=original('config','user.name');env['GIT_'+role+'_EMAIL']=original('config','user.email')
    with tempfile.TemporaryDirectory(prefix='segcp8a-git-') as temp:
        directory=Path(temp)/'repo.git'
        subprocess.run(['git','init','--bare','-q',str(directory)],check=True,env=env)
        (directory/'objects/info/alternates').write_text(str(common/'objects')+'\n')
        prefix=['git','-c','core.fsmonitor=false','-c','core.hooksPath=/dev/null','-c','pack.threads=1','-c','pack.window=0','--git-dir='+str(directory),'--work-tree='+str(ROOT)]
        def isolated(*a,input=None):return subprocess.check_output(prefix+list(a),cwd=ROOT,env=env,text=True,input=input).strip()
        isolated('fetch','-q',str(BASE/'ADMW2.bundle'),'refs/heads/admw2')
        isolated('read-tree',parent)
        files=[]
        for p in paths:
            assert p.is_file() and not p.is_symlink(),p
            name=str(p.relative_to(ROOT));oid=isolated('hash-object','-w','--no-filters','--',name)
            isolated('update-index','--add','--cacheinfo',('100755' if p.stat().st_mode & 0o111 else '100644')+','+oid+','+name)
            files.append(dict(path=name,sha256=sha(p)))
        tree=isolated('write-tree')
        commit=isolated('-c','commit.gpgsign=false','commit-tree',tree,'-p',parent,input='SEG-CP8a: close custody, qualify composed evaluator and retain crop withdrawals\n')
        isolated('update-ref','refs/heads/seg-cp8a',commit)
        bundle=HERE/'SEG_CP8a.bundle';isolated('bundle','create',str(bundle),'refs/heads/seg-cp8a','^'+base)
        check=subprocess.run(['git','bundle','verify',str(bundle)],cwd=ROOT,env=env,text=True,capture_output=True,check=True)
        assert isolated('rev-parse',commit+'^')==parent
        assert isolated('rev-parse',parent+'^')==base
        changed=isolated('diff-tree','--no-commit-id','--name-only','-r',commit).splitlines()
        assert set(changed)<={r['path'] for r in files}
    result=dict(schema='SEG-CP8a-commits-1',status='additive_commits_bundled_branch_update_sandbox_blocked',
        source_HEAD=base,commits=[dict(commit=parent,task='prior ADMW2'),dict(commit=commit,task='SEG-CP8a',parent=parent)],
        bundle=str(bundle.relative_to(ROOT)),bundle_sha256=sha(bundle),files=files,changed_paths=changed,
        verification=check.stdout+check.stderr,source_branch_updated=False,source_index_updated=False)
    (HERE.parent/'CP8a_COMMIT_LIST.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','commits','bundle','bundle_sha256')},indent=2))
if __name__=='__main__':main()
