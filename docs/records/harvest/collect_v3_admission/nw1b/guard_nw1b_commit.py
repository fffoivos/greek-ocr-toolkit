"""Read-only guard: reviewed exact hashes, owner gate, HEAD/branch, empty index."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def main():
    manifest=json.loads((BASE/'NW1b_COMMIT_LIST.json').read_text())
    assert git('rev-parse','HEAD')==manifest['base_HEAD'], 'HEAD changed'
    assert git('branch','--show-current')==manifest['branch'], 'branch changed'
    assert not git('diff','--cached','--name-only'), 'preserve unrelated staged work'
    paths=[]
    for r in manifest['files']:
        p=ROOT/r['path']
        assert not p.is_symlink() and p.resolve().is_relative_to(ROOT), 'unsafe path'
        assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'], 'file changed: '+r['path']
        paths.append(r['path'])
    paths.append(str((BASE/'NW1b_COMMIT_LIST.json').relative_to(ROOT)))
    subprocess.run(['git','diff','--check','--',*paths],cwd=ROOT,check=True)
    ignored=subprocess.run(['git','check-ignore','--no-index','--',*paths],cwd=ROOT,capture_output=True)
    assert ignored.returncode==1, 'ignored reviewed path or check-ignore error'
    pngs=sorted(str(p.relative_to(ROOT)) for p in (BASE.parent/'crops').rglob('*.png'))
    result=subprocess.run(['git','check-ignore','--no-index','--stdin'],cwd=ROOT,
                          input='\n'.join(pngs)+'\n',text=True,capture_output=True)
    assert result.returncode==0 and result.stdout.splitlines()==pngs, 'PNGs not all ignored'
    gate=json.loads((BASE/'calibration.json').read_text())
    assert gate['gate'] and gate['selected']['standalone']['gate']
    verified=json.loads((BASE/'verification.json').read_text())
    assert verified['deleted_pngs']==0 and verified['all_pngs_match_original_crop_hash']
    print(f'NW1b guard passed: {len(paths)} exact paths; HEAD/branch bound; empty index; {len(pngs)} PNGs ignored; no staging or commit')
    print('\n'.join(paths))


if __name__=='__main__':main()
