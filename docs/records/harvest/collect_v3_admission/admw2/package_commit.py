"""Package one additive commit without writing the shared worktree Git metadata.

The companion commit list is external to the commit, avoiding a self-reference.
No branch, index, configuration or object in the source repository is modified.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
    return h.hexdigest()


def package():
    manifest=BASE/'ADMW2_COMMIT_LIST.json'
    spec=json.loads(manifest.read_text())
    for item in spec['files']:
        assert digest(ROOT/item['path'])==item['sha256'],item['path']
    env=dict(os.environ)
    for key in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        env.pop(key,None)
    def original(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,env=env,text=True).strip()
    common=Path(original('rev-parse','--git-common-dir'))
    if not common.is_absolute():common=(ROOT/common).resolve()
    for role in ('AUTHOR','COMMITTER'):
        env['GIT_'+role+'_NAME']=original('config','user.name')
        env['GIT_'+role+'_EMAIL']=original('config','user.email')
    bundle=BASE/'ADMW2.bundle'
    with tempfile.TemporaryDirectory(prefix='admw2-git-') as temporary:
        directory=Path(temporary)/'repo.git'
        subprocess.run(['git','init','--bare','--quiet',str(directory)],check=True,env=env)
        (directory/'objects/info/alternates').write_text(str(common/'objects')+'\n')
        prefix=['git','-c','core.fsmonitor=false','-c','core.hooksPath=/dev/null',
                '-c','pack.threads=1','-c','pack.window=0',
                '--git-dir='+str(directory),'--work-tree='+str(ROOT)]
        def isolated(*args,input=None):
            return subprocess.check_output(prefix+list(args),cwd=ROOT,env=env,text=True,input=input).strip()
        isolated('read-tree',spec['base_HEAD'])
        # Exact bytes, no global Git/LFS clean filters or external helpers.
        for item in spec['files']:
            path=ROOT/item['path']
            assert path.is_file() and not path.is_symlink()
            oid=isolated('hash-object','-w','--no-filters','--',item['path'])
            mode='100755' if path.stat().st_mode & 0o111 else '100644'
            isolated('update-index','--add','--cacheinfo',mode+','+oid+','+item['path'])
        tree=isolated('write-tree')
        commit=isolated('-c','commit.gpgsign=false','commit-tree',tree,'-p',spec['base_HEAD'],input=spec['message']+'\n')
        isolated('update-ref','refs/heads/admw2',commit)
        temporary_bundle=BASE/'ADMW2.bundle.tmp'
        isolated('bundle','create',str(temporary_bundle),'refs/heads/admw2','^'+spec['base_HEAD'])
        temporary_bundle.replace(bundle)
        # Check against the actual read-only repository's prerequisite history.
        verification=subprocess.run(['git','bundle','verify',str(bundle)],cwd=ROOT,env=env,text=True,capture_output=True,check=True)
        changes=isolated('diff-tree','--no-commit-id','--name-only','-r',commit).splitlines()
        assert set(changes)<=set(item['path'] for item in spec['files'])
        assert isolated('rev-parse',commit+'^')==spec['base_HEAD']
    spec.update(status='packaged_additive_commit_branch_update_blocked',commit=commit,
                commit_parent=spec['base_HEAD'],bundle=bundle.name,bundle_sha256=digest(bundle),
                bundle_verification=(verification.stdout+verification.stderr).strip(),
                changed_paths=changes,source_branch_updated=False,source_index_updated=False)
    manifest.write_text(json.dumps(spec,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:spec[k] for k in ('status','commit','commit_parent','bundle','bundle_sha256','source_branch_updated')},indent=2))

if __name__=='__main__':package()
