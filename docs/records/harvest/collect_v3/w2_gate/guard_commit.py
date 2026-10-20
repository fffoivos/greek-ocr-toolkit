"""Verify the exact GATE2b commit list; stage only with explicit --stage."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--stage', action='store_true')
args = parser.parse_args()
here = Path(__file__).resolve().parent
root = here.parents[3]
manifest = json.loads((here / 'commit-list.json').read_text())
expected = {str(p.relative_to(root)) for p in here.iterdir() if p.is_file()}
assert expected == set(manifest['commit_paths']), 'Unexpected or missing handoff files'
assert len(manifest['files']) == len(expected) - 1
assert {item['path'] for item in manifest['files']} == expected - {str((here / 'commit-list.json').relative_to(root))}
for item in manifest['files']:
    path = root / item['path']
    assert path.parent == here and not path.is_symlink(), path
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], path

def staged():
    raw = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=root)
    return set(filter(None, raw.decode().split('\0')))

assert staged() <= expected, 'Unrelated staged paths; refusing staging'
print(f'Verified {len(expected)} exact commit paths and all payload hashes')
if args.stage:
    subprocess.run(['git', 'add', '--', *sorted(expected)], cwd=root, check=True)
    assert staged() == expected, 'Staged set differs from exact GATE2b commit list'
    for item in manifest['files']:
        blob = subprocess.check_output(['git', 'show', ':' + item['path']], cwd=root)
        assert hashlib.sha256(blob).hexdigest() == item['sha256'], item['path']
    blob = subprocess.check_output(['git', 'show', ':' + str((here / 'commit-list.json').relative_to(root))], cwd=root)
    assert blob == (here / 'commit-list.json').read_bytes(), 'Staged manifest drift'
    print('Staged exact GATE2b list; no commit performed')
