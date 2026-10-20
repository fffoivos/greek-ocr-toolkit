"""Prepare or verify the ADM4 exact commit list; never stage or commit."""
import argparse
import json
from pathlib import Path
import subprocess
from build_w1_originals_v3 import BASE, OUT, compute, obj, sha
ROOT = BASE.parents[2]
MANIFEST = OUT/'adm4_commit_inputs.json'
LIST = OUT/'ADM4_COMMIT_FILES.txt'
FILES = [OUT/name for name in ['w1_originals_v3.jsonl','w1_originals_v3_summary.json',
         'w1_masked_1d_summary.json','build_w1_originals_v3.py','update_adm4_ledger.py',
         'test_adm4_originals_v3.py','guard_adm4_commit.py','adm4_tests.log','ADM4_HANDOFF.md']]
FILES += [BASE/'WEAK_CATEGORY_LEDGER.md',BASE/'weak_ledger/ledger.json',LIST]

def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)

def expected():
    assert git('branch','--show-current').decode().strip()=='sol/collect-v3'
    assert not git('diff','--cached','--name-only').strip(), 'index must be empty'
    data, summary = compute()
    assert (OUT/summary['file']).read_bytes()==data
    assert obj(OUT/'w1_originals_v3_summary.json')==summary
    assert '\nRan 7 tests in ' in (OUT/'adm4_tests.log').read_text()
    assert (OUT/'adm4_tests.log').read_text().rstrip().endswith('OK')
    for p in FILES: assert p.is_file() and not p.is_symlink(), str(p)
    paths = [str(p.relative_to(ROOT)) for p in FILES]
    git('diff','--check','--',*paths)
    exact = sorted(paths+[str(MANIFEST.relative_to(ROOT))])
    assert LIST.read_text()==''.join(p+'\n' for p in exact)
    ignored=[]
    for p in paths:
        result=subprocess.run(['git','check-ignore','--no-index',p],cwd=ROOT,capture_output=True)
        assert result.returncode in (0,1)
        if result.returncode==0: ignored.append(p)
    return dict(schema='adm4-guarded-commit-1',head=git('rev-parse','HEAD').decode().strip(),
                branch='sol/collect-v3',files={p:sha(ROOT/p) for p in sorted(paths)},
                manifest_path=str(MANIFEST.relative_to(ROOT)),
                manifest_note='Include manifest itself; own hash omitted to avoid recursion.',
                exact_commit_list=exact,ignored_exact_paths_requiring_force_add=ignored,
                bound_inputs=summary['input_sha256'],tests_passed=7,rows=summary['rows'],
                removals=summary['removals'],staging_performed=False,commit_performed=False,
                conditions=['Require unchanged HEAD/branch, empty index and all bound hashes.',
                            'Stage only exact_commit_list, then verify staged set equals list.',
                            'Never stage masked JSONL, live collector, run roots or unrelated edits.'])

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare',action='store_true')
    mode.add_argument('--check-only',action='store_true')
    args=parser.parse_args()
    if args.prepare:
        paths=sorted(str(p.relative_to(ROOT)) for p in FILES+[MANIFEST])
        LIST.write_text(''.join(p+'\n' for p in paths))
        MANIFEST.write_text(json.dumps(expected(),indent=2)+'\n')
    else: assert obj(MANIFEST)==expected(), 'guarded file/input/HEAD drift'
    print('ADM4 guarded list verified; 13 files; 7 tests passed; no staging or commit')
