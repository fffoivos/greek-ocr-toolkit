"""Read-only CROPS1 commit-list guard; never stages or commits."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
LIST = BASE / 'CROPS1_COMMIT_LIST.json'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode().strip()


def main():
    manifest = json.loads(LIST.read_text())
    if git('branch', '--show-current') != manifest['branch']:
        raise SystemExit('wrong branch')
    if git('rev-parse', 'HEAD') != manifest['base_HEAD']:
        raise SystemExit('HEAD changed; review and regenerate list')
    if git('diff', '--cached', '--name-only'):
        raise SystemExit('index is not empty; preserve unrelated staged work')
    paths = []
    for row in manifest['files']:
        path = ROOT / row['path']
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise SystemExit('path escapes scope')
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise SystemExit('changed file: ' + row['path'])
        paths.append(row['path'])
    paths.append(str(LIST.relative_to(ROOT)))
    result = subprocess.run(['git', 'check-ignore', '--no-index', '--', *paths], cwd=ROOT, capture_output=True)
    if result.returncode != 1:
        raise SystemExit('commit paths ignored or check-ignore failed')
    crops = [str((BASE / json.loads(line)['path']).relative_to(ROOT))
             for line in (BASE / 'crops_manifest.jsonl').read_text().splitlines()]
    result = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin'],
                            input='\n'.join(crops) + '\n', text=True, capture_output=True, cwd=ROOT)
    if result.returncode != 0 or result.stdout.splitlines() != crops:
        raise SystemExit('crop PNGs are not all ignored')
    subprocess.run(['git', 'diff', '--check', '--', *paths], cwd=ROOT, check=True)
    print(f'CROPS1 guard passed: {len(paths)} exact paths; {len(crops)} ignored PNGs; empty index')
    print('\n'.join(paths))


if __name__ == '__main__':
    main()
