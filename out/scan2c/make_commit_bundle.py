"""Build the requested commit without writing the sandbox's read-only .git.
The bundle branch is opus/sol-reading; the actual checkout branch is unchanged.
"""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'out/scan2c'
def run(*args,env=None):
    return subprocess.check_output(['git',*args],cwd=ROOT,env=env,text=True).strip()
def main():
    result=json.loads((ROOT/'out/scan2/rescan_v452.json').read_text())
    digest=hashlib.sha256((ROOT/'docs/harvest/sol_reading/tools/scan_rollout.py').read_bytes()).hexdigest()
    assert result['scanner_sha256']==digest
    assert len(result['contexts'])==15 and result['original_receipts_unchanged']
    log=(OUT/'tests_final.log').read_text()
    assert 'Ran 98 tests' in log and log.rstrip().endswith('OK')
    parent=run('rev-parse','HEAD')
    common=Path(run('rev-parse','--git-common-dir')).resolve()
    name=run('config','user.name');email=run('config','user.email')
    paths=['docs/harvest/sol_reading/tools/scan_rollout.py',
        'docs/harvest/sol_reading/tools/test_scan_rollout_canonical.py',
        'docs/harvest/sol_reading/HANDOVER.md','tests/test_scan_rollout.py',
        'out/scan2/rescan_v452.json','out/scan2c/tests_final.log',
        'out/scan2c/rescan_final.log','out/scan2c/rescan.py',
        'out/scan2c/make_commit_bundle.py',
        'out/scan2c/probe_baseline.py','out/scan2c/probes_v451_baseline.log','out/scan2c/probes_final.log',
        'tests/fixtures/v45/helper_overwrites.json']
    paths+=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'out/scan2').glob('*.v452.scan.json'))
    assert len(paths)==28
    with tempfile.TemporaryDirectory(prefix='scan2c-git-') as temp:
        gitdir=Path(temp)/'repo.git'
        run('init','--bare',str(gitdir))
        (gitdir/'objects/info/alternates').write_text(str(common/'objects')+'\n')
        env=dict(os.environ,GIT_DIR=str(gitdir),GIT_WORK_TREE=str(ROOT),GIT_INDEX_FILE=str(Path(temp)/'index'))
        run('read-tree',parent,env=env)
        run('add','--',*paths,env=env)
        tree=run('write-tree',env=env)
        commit=run('-c','user.name='+name,'-c','user.email='+email,'commit-tree',tree,'-p',parent,
            '-m','Fix SCAN2R2 helper replay invalidation in scanner v4.5.2; 98 tests and 15 rescans',env=env)
        run('update-ref','refs/heads/opus/sol-reading',commit,env=env)
        bundle=OUT/'scan2c-v452.bundle'
        run('bundle','create',str(bundle),'opus/sol-reading','^'+parent,env=env)
        verification=run('bundle','verify',str(bundle),env=env)
        changed=run('diff-tree','--no-commit-id','--name-only','-r',commit,env=env).splitlines()
        assert set(changed)==set(paths),(changed,paths)
        (OUT/'COMMIT.json').write_text(json.dumps(dict(commit=commit,parent=parent,
            branch='opus/sol-reading',checkout_branch_updated=False,
            reason='Sandbox denied creation of worktree index.lock; .git is read-only',
            bundle=str(bundle.relative_to(ROOT)),paths=paths,bundle_verification=verification),indent=2)+'\n')
        print(commit)
if __name__=='__main__':main()
