"""Commit only reviewed T7 text artifacts; --check is read-only. No force-add."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PREFIX='docs/harvest/wikisource_r0/'

def git(*args,check=True):
    return subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True,check=check)

def main():
    manifest=json.loads((OUT/'COMMIT_MANIFEST.json').read_text())
    assert git('branch','--show-current').stdout.strip()=='sol/wikisource-r0'
    assert git('rev-parse','HEAD').stdout.strip()==manifest['parent_head'],'HEAD changed; regenerate only after review'
    assert not git('diff','--cached','--name-only').stdout.strip(),'index has existing staged work'
    paths=sorted(manifest['files'])
    assert paths
    for p,digest in manifest['files'].items():
        assert p.startswith(PREFIX) and '..' not in Path(p).parts
        assert git('check-ignore','--no-index','--',p,check=False).returncode==1, 'ignored path: '+p
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest, 'changed file: '+p
    discovered=set(git('ls-files','--others','--exclude-standard','--',PREFIX).stdout.splitlines())
    discovered.update(git('ls-files','--modified','--',PREFIX).stdout.splitlines())
    assert discovered==set(paths)|{PREFIX+'COMMIT_MANIFEST.json'},'unreviewed new/modified paths'
    print(f'Guard passed: {len(paths)+1} non-ignored files, parent {manifest["parent_head"]}')
    if '--check' in sys.argv:return
    if sys.argv[1:]!=['--commit']:raise SystemExit('use --check or --commit')
    # A protected index.lock is terminal. Never use alternate indices or retry.
    result=git('add','--',*paths,PREFIX+'COMMIT_MANIFEST.json',check=False)
    if result.returncode:
        print(result.stderr.strip(),file=sys.stderr);raise SystemExit(result.returncode)
    staged=set(git('diff','--cached','--name-only').stdout.splitlines())
    assert staged==set(paths)|{PREFIX+'COMMIT_MANIFEST.json'}
    git('diff','--cached','--check')
    result=git('commit','-m',manifest['message'],check=False)
    print(result.stdout);print(result.stderr,file=sys.stderr)
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
