"""Prepare/check an exact T6g commit list; commits only with explicit --commit.

No staging retries or alternate index. PNGs and existing unrelated files excluded.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
MANIFEST = HERE / 'commit-inputs.json'
HEAD = '1a85772173ccae3853a7568319e31729fdfe6127'
BRANCH = 'sol/recut-v1'
SPEC = importlib.util.spec_from_file_location('t6g_guard_pack', HERE / 'pack.py')
pack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pack)
SOURCES = ('pack.py', 'test_pack.py', 'guarded_commit.py', 'receipt.json', 'tests.log', 'tests.xml', 'HANDOFF.md')


def git(*args, check=True, stdin=None):
    return subprocess.run(['git', *args], cwd=ROOT, input=stdin, capture_output=True, check=check)


def ignored(paths):
    result = git('check-ignore', '--no-index', '-z', '--stdin', check=False,
                 stdin=b''.join(p.encode() + b'\0' for p in paths))
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.decode())
    return {p.decode() for p in result.stdout.split(b'\0') if p}


def paths():
    return sorted(str(p.relative_to(ROOT)) for p in (
        *[HERE / name for name in SOURCES], pack.KEY,
        pack.READER / 'cards.jsonl', pack.READER / 'PROTOCOL.md'))


def guards():
    if git('branch', '--show-current').stdout.decode().strip() != BRANCH:
        raise RuntimeError('wrong branch')
    if git('rev-parse', 'HEAD').stdout.decode().strip() != HEAD:
        raise RuntimeError('source HEAD changed')
    if git('diff', '--cached', '--name-only').stdout.strip():
        raise RuntimeError('index must be empty')
    git('diff', '--check')
    result = pack.verify()
    suites = list(ET.parse(HERE / 'tests.xml').getroot().iter('testsuite'))
    if not suites or any(int(s.get(k, '0')) for s in suites for k in ('failures', 'errors', 'skipped')):
        raise RuntimeError('clean test evidence required')
    tests = sum(int(s.get('tests', '0')) for s in suites)
    if tests < 4:
        raise RuntimeError('requested tests missing')
    candidates = paths()
    if ignored(candidates):
        raise RuntimeError('commit list contains ignored files')
    if any((ROOT / p).is_symlink() for p in candidates):
        raise RuntimeError('commit list contains symlink')
    pngs = [str(p.relative_to(ROOT)) for p in (pack.READER / 'crops').iterdir()]
    if ignored(pngs) != set(pngs) or len(pngs) != result['cards']:
        raise RuntimeError('all crop PNGs must remain git-ignored')
    return result, tests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--check-only', action='store_true')
    mode.add_argument('--commit', action='store_true')
    args = parser.parse_args()
    result, tests = guards()
    expected = dict(schema='t6g-guarded-commit-1', base_HEAD=HEAD, branch=BRANCH,
                    message='T6g: pack 100 masked kosmopolis poly1850 qualification cards',
                    files=[dict(path=p, sha256=pack.sha(ROOT / p)) for p in paths()],
                    ignored_pngs=result['cards'], png_hashes_in=str(pack.KEY.relative_to(ROOT)),
                    tests_passed=tests, admitted=False)
    if args.prepare:
        pack.write_json(MANIFEST, expected)
        print('Prepared guarded list:', len(expected['files']) + 1, 'files; PNGs excluded:', result['cards'])
        return
    if json.loads(MANIFEST.read_text()) != expected:
        raise RuntimeError('guarded list/hash/evidence mismatch')
    commit_paths = paths() + [str(MANIFEST.relative_to(ROOT))]
    if ignored(commit_paths):
        raise RuntimeError('ignored path in commit scope')
    if args.check_only:
        print('Validated guarded list:', len(commit_paths), 'files;', tests, 'tests passed; isolation ok')
        return
    # A failed git operation is terminal; never use an alternate index.
    git('add', '--', *commit_paths)
    if set(git('diff', '--cached', '--name-only').stdout.decode().splitlines()) != set(commit_paths):
        raise RuntimeError('staged set differs from guarded list')
    git('diff', '--cached', '--check')
    print(git('commit', '-m', expected['message']).stdout.decode())


if __name__ == '__main__':
    main()
