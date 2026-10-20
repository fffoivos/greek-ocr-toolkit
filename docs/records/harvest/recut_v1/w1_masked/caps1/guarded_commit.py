"""Prepare/check a CAPS1 text-only commit list. Never stages or commits."""
import argparse
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from build import HERE, REPO, dump, sha

MANIFEST = HERE / 'commit-inputs.json'
LIST = HERE / 'COMMIT_FILES.txt'
EXCLUDED = ('cache/', 'test_tmp/', '__pycache__/', 'launchers/logs/', 'launchers/probe.',
            'launchers/prompts_rendered/', 'scan/replay_tmp/', 'answers/')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO).decode().strip()


def files():
    result = []
    for p in sorted(HERE.rglob('*')):
        rel = str(p.relative_to(HERE))
        if p.is_file() and p not in (MANIFEST, LIST) and not rel.startswith(EXCLUDED):
            if p.is_symlink() or p.suffix.lower() == '.png':
                raise RuntimeError('symlink or PNG in commit scope: ' + rel)
            result.append(p)
    return result


def expected():
    return dict(schema='caps1-text-only-commit-1', base_HEAD=git('rev-parse', 'HEAD'),
                branch=git('branch', '--show-current'), message='CAPS1: prepare uniform headings/caps Sol packs',
                files=[dict(path=str(p.relative_to(REPO)), sha256=sha(p), bytes=p.stat().st_size) for p in files()],
                pngs_in_commit=0, staging_performed=False, readers_started=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if git('diff', '--cached', '--name-only'):
        raise RuntimeError('index must be empty')
    subprocess.run(['git', 'diff', '--check'], cwd=REPO, check=True)
    current = expected()
    paths = [x['path'] for x in current['files']] + [str(MANIFEST.relative_to(REPO)), str(LIST.relative_to(REPO))]
    if args.prepare:
        dump(MANIFEST, current)
        LIST.write_text('\n'.join(paths) + '\n')
        print('Prepared guarded list:', len(paths), 'text files; no staging, no PNGs')
        return
    if json.loads(MANIFEST.read_text()) != current or LIST.read_text().splitlines() != paths:
        raise RuntimeError('guarded list, source HEAD/branch, or file hashes changed')
    tests = ET.parse(HERE / 'tests.xml').getroot().attrib
    if int(tests['tests']) < 14 or any(int(tests[k]) for k in ('errors', 'failures', 'skipped')):
        raise RuntimeError('all 14 tests must pass')
    closure = json.loads((HERE / 'scan/closure.json').read_text())
    if len(closure) != 2 or any(not x['ok'] for x in closure):
        raise RuntimeError('both compatible closure scans must be clean')
    from reference_adapter import require_approval, load_reference, private_contract, CLOSURE_SUBSTITUTIONS
    from build import BED
    require_approval()
    scanner = load_reference('scan_packs', CLOSURE_SUBSTITUTIONS)
    for context in ('c1', 'c2'):
        result = scanner.scan(BED / context, 'caps1', write_manifest=False)
        if not result['ok'] or private_contract(BED / context):
            raise RuntimeError('live pack closure failed: ' + context)
    bindings = json.loads((HERE / 'build_receipt.json').read_text())['inputs']
    bindings.update(json.loads((HERE / 'runtime_bindings.json').read_text())['reference_sources'])
    if any(sha(path) != digest for path, digest in bindings.items()):
        raise RuntimeError('read-only input/source binding changed')
    print('Guarded list verified:', len(paths), 'files; 14 tests; both contexts clean; PNGs excluded')


if __name__ == '__main__':
    main()
