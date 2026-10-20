#!/usr/bin/env python3
"""Read-only checks for the exact commit list; never writes the Git index."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]
PREFIX=str(ROOT.relative_to(REPO))+'/'


def git(*args):
    return subprocess.check_output(['git',*args],cwd=REPO)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(staged=False):
    paths=(ROOT/'COMMIT_FILES.txt').read_text().splitlines()
    assert len(paths)==len(set(paths)) and paths
    for p in paths:
        assert p.startswith(PREFIX) and '..' not in Path(p).parts and not p.endswith('.png')
        assert (REPO/p).is_file() and not (REPO/p).is_symlink()
    receipt=json.loads((ROOT/'COMMIT_SHA256.json').read_text())
    frozen=set(receipt['sha256'])|{PREFIX+'COMMIT_SHA256.json'}
    assert set(paths)<=frozen
    for p,h in receipt['sha256'].items():
        assert digest((REPO/p).read_bytes())==h, f'Candidate changed: {p}'
    actual={str(p.relative_to(REPO)) for p in ROOT.rglob('*') if p.is_file() and p.suffix!='.png' and '__pycache__' not in p.parts and '.work' not in p.parts and '.pytest_cache' not in p.parts}
    assert actual==frozen,f'Candidate tree changed: {actual.symmetric_difference(frozen)}'
    # E-build2 extends an existing commit: unchanged tracked artifacts cannot
    # appear in git diff --cached. Bind the full tree, but stage only its delta.
    if receipt.get('commit_list_kind')=='changed_or_untracked_relative_to_HEAD':
        changed=set(git('diff','HEAD','--name-only','-z','--',PREFIX).decode().rstrip('\0').split('\0'))-{''}
        untracked=set(git('ls-files','--others','--exclude-standard','-z','--',PREFIX).decode().rstrip('\0').split('\0'))-{''}
        expected_delta={p for p in changed|untracked if not p.endswith('.png')}
        assert set(paths)==expected_delta, f'Commit delta changed: {set(paths).symmetric_difference(expected_delta)}'
    else:
        assert set(paths)==frozen
    snapshot=ROOT/'keys/build2_prebuild_state.json'
    state=json.loads((snapshot if snapshot.exists() else ROOT/'keys/prebuild_state.json').read_text())
    assert git('branch','--show-current').decode().strip()==state['branch']=='sol/collect-v3'
    if 'head' in receipt:
        assert git('rev-parse','HEAD').decode().strip()==receipt['head'], 'HEAD changed after commit-list preparation'
    diff=git('diff','--binary','--','.',':(exclude)'+PREFIX.rstrip('/'))
    assert digest(diff)==state['outside_diff_sha256'],'Outside-scope tracked changes differ from prebuild state'
    for rel,r in state['collect_v3'].items():
        p=REPO/rel
        assert digest(p.read_bytes())==r['sha256'] and p.stat().st_mtime_ns==r['mtime_ns'], f'Live source changed: {rel}'
    for rel,h in state.get('frozen_beds',{}).items():
        assert digest((REPO/rel).read_bytes())==h, f'Existing bed changed: {rel}'
    source_hashes=ROOT/'keys/owner39/source_hashes.json'
    if source_hashes.exists():
        for path,h in json.loads(source_hashes.read_text()).items():
            assert digest(Path(path).read_bytes())==h, f'Owner39 source changed: {path}'
    current_staged=set(git('diff','--cached','--name-only','-z').decode().rstrip('\0').split('\0'))-{''}
    if staged:
        assert current_staged==set(paths),'Staged paths must exactly match COMMIT_FILES.txt'
        for p in paths:
            assert digest(git('show',':'+p))==digest((REPO/p).read_bytes()), f'Staged blob differs: {p}'
    else:
        assert not current_staged,'Index already has staged changes; inspect it before staging this build'
    spec=importlib.util.spec_from_file_location('efficiency_validate',ROOT/'validate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    validation=module.validate()
    return {'guard':'ok','mode':'staged' if staged else 'prestage','files':len(paths),'git_writes':False,'pack_validation':validation}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--staged',action='store_true');args=parser.parse_args()
    try:
        print(json.dumps(check(args.staged),indent=2))
    except (AssertionError,KeyError,ValueError) as exc:
        print(f'Commit guard rejected: {exc}',file=sys.stderr);raise SystemExit(2)
