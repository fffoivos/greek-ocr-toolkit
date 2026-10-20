"""Prepare/check ADM2's exact commit list. Never stage or commit anything."""
import argparse
import json
import subprocess

import append_adm2_poly1850 as adm

MANIFEST = adm.HERE / 'adm2_commit_inputs.json'
FILES = ('w1_masked_1d.jsonl', 'w1_masked_1d_summary.json', 'append_adm2_poly1850.py',
         'test_adm2_poly1850.py', 'guard_adm2_commit.py', 'adm2_tests.log', 'ADM2_HANDOFF.md')


def git(*args):
    return subprocess.run(['git', *args], cwd=adm.ROOT, check=True, capture_output=True).stdout


def manifest():
    adm.require(git('rev-parse', 'HEAD').decode().strip() == adm.BASE_HEAD, 'source HEAD changed')
    adm.require(git('branch', '--show-current').decode().strip() == 'sol/collect-v3', 'branch changed')
    adm.require(not git('diff', '--cached', '--name-only').strip(), 'index must be empty')
    paths = [str((adm.HERE / name).relative_to(adm.ROOT)) for name in FILES]
    git('diff', '--check', '--', *paths)
    ignored = subprocess.run(['git', 'check-ignore', '--no-index', '--',
                              *paths, str(MANIFEST.relative_to(adm.ROOT))],
                             cwd=adm.ROOT, capture_output=True)
    adm.require(ignored.returncode in (0, 1) and not ignored.stdout.strip(),
                'ignored file in commit list or check-ignore failure')
    for name in FILES:
        adm.require(not (adm.HERE / name).is_symlink(), 'symlink in guarded files: ' + name)
    tests = (adm.HERE / 'adm2_tests.log').read_text()
    adm.require('\nRan 10 tests in ' in tests and tests.rstrip().endswith('OK'), 'clean 10-test receipt required')
    result = adm.verify()
    return dict(schema='adm2-guarded-commit-1', base_HEAD=adm.BASE_HEAD, branch='sol/collect-v3',
                message='ADM2: append kosmopolis poly1850 release-v3 candidate pool',
                files=[dict(path=str((adm.HERE / name).relative_to(adm.ROOT)),
                            sha256=adm.sha(adm.HERE / name)) for name in sorted(FILES)],
                manifest_path=str(MANIFEST.relative_to(adm.ROOT)),
                manifest_note='Include this manifest itself; its own hash is omitted to avoid recursion.',
                bound_inputs=adm.bindings(), tests_passed=10, validation=result,
                arm_contract_note='Existing literal wave-1d only preserved; exact wave-1d filter returns 0.',
                staging_performed=False, commit_performed=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    expected = manifest()
    if args.prepare:
        MANIFEST.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n')
    else:
        adm.require(json.loads(MANIFEST.read_text()) == expected, 'guarded file/input hashes changed')
    print('ADM2 guarded list:', len(FILES) + 1, 'files; tests: 10 passed; no staging or commit')
