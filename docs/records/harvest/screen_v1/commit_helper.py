"""Guarded local commit of the exact reviewed T4b output tree.

Run with the existing worktree Python after making the Git index writable.
Refuses branch/HEAD drift, changed input/code/artifact hashes, missing files,
and staged paths outside this output directory. It never pushes.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import argparse

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PREFIX = 'docs/harvest/screen_v1/'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true',help='verify all guards without staging or committing')
    args=parser.parse_args()
    manifest = json.loads((OUT/'receipts/artifact_manifest.json').read_text())
    assert Path(git('rev-parse','--show-toplevel')).resolve()==ROOT
    assert git('rev-parse','HEAD')==manifest['expected_head'], 'HEAD changed; review again'
    assert git('branch','--show-current')==manifest['expected_branch'], 'branch changed'
    validation = json.loads((OUT/'receipts/validation.json').read_text())
    assert validation['status']=='pass', 'validation did not pass'
    inputs = json.loads((OUT/'receipts/inputs.json').read_text())['input_files']
    code = json.loads((OUT/'receipts/code_provenance.json').read_text())['shipped_files']
    for r in inputs+code:
        assert digest(Path(r['path']))==r['sha256'], 'input or shipped code changed: '+r['path']
    paths = []
    for r in manifest['files']:
        assert r['path'].startswith(PREFIX) and '..' not in Path(r['path']).parts
        assert digest(ROOT/r['path'])==r['sha256'], 'artifact changed: '+r['path']
        paths.append(r['path'])
    actual = {str(f.relative_to(ROOT)) for f in OUT.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    manifest_path = str((OUT/'receipts/artifact_manifest.json').relative_to(ROOT))
    assert actual==set(paths)|{manifest_path}, 'unbound output files appeared'
    staged = git('diff','--cached','--name-only').splitlines()
    assert all(p.startswith(PREFIX) for p in staged), 'unrelated paths already staged'
    if args.check:
        print('Guard checks passed:',len(paths),'bound artifact files; no Git mutation')
        return
    subprocess.run(['git','add','--',*paths,manifest_path],cwd=ROOT,check=True)
    staged = git('diff','--cached','--name-only').splitlines()
    assert staged and all(p.startswith(PREFIX) for p in staged)
    subprocess.run(['git','commit','-m','T4b: offline interleave assembly overlay and blind-card screen'],cwd=ROOT,check=True)
    print(git('rev-parse','HEAD'))


if __name__=='__main__':
    main()
