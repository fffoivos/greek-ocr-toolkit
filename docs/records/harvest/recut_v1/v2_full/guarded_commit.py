"""Read-only check by default. --commit is a coordinator action, without retries."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MANIFEST = HERE / 'commit-inputs.json'


def git(*args, check=True, stdin=None):
    return subprocess.run(['git', *args], cwd=ROOT, input=stdin, capture_output=True, check=check)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    manifest = json.loads(MANIFEST.read_text())
    assert git('rev-parse', 'HEAD').stdout.decode().strip() == manifest['base_HEAD'], 'HEAD changed'
    assert git('branch', '--show-current').stdout.decode().strip() == manifest['branch'] == 'sol/recut-v1'
    assert not git('diff', '--cached', '--name-only').stdout.strip(), 'index must start empty'
    paths = []
    for entry in manifest['files']:
        path = ROOT / entry['path']
        assert path.resolve().is_relative_to(HERE) and not path.is_symlink(), str(path)
        assert not {'out', 'mock-out'} & set(path.relative_to(HERE).parts)
        assert sha(path) == entry['sha256'], str(path)
        assert path.stat().st_mode & 0o777 == entry['mode'], str(path)
        paths.append(entry['path'])
    for entry in manifest['dependencies']:
        assert sha(ROOT / entry['path']) == entry['sha256'], 'dependency changed: ' + entry['path']
    paths.append(str(MANIFEST.relative_to(ROOT)))
    assert len(paths) == len(set(paths))
    ignored = git('check-ignore', '--no-index', '-z', '--stdin', check=False,
                  stdin=b''.join(p.encode() + b'\0' for p in paths))
    assert ignored.returncode in (0, 1) and not ignored.stdout, 'ignored path in commit list'
    return manifest, paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', action='store_true')
    args = parser.parse_args()
    manifest, paths = validate()
    if not args.commit:
        print(f'CHECK PASS: {len(paths)} hash-bound files; HEAD, branch, empty index, dependencies, modes, ignore rules')
    else:
        git('add', '--', *paths)
        staged = set(git('diff', '--cached', '--name-only').stdout.decode().splitlines())
        assert staged == set(paths), 'unexpected staged set'
        git('diff', '--cached', '--check')
        print(git('commit', '-m', manifest['message']).stdout.decode())
