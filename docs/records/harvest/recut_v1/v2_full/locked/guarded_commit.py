"""Hash-bound T6i2 handoff; read-only by default, --commit stages exact paths once."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def git(*args, check=True, stdin=None):
    return subprocess.run(['git', *args], cwd=ROOT, input=stdin,
                          capture_output=True, check=check)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    manifest = json.loads((HERE / 'commit-inputs.json').read_text())
    assert git('rev-parse', 'HEAD').stdout.decode().strip() == manifest['base_HEAD'], 'HEAD changed'
    assert git('branch', '--show-current').stdout.decode().strip() == manifest['branch'] == 'sol/recut-v1'
    assert not git('diff', '--cached', '--name-only').stdout.strip(), 'index not empty'
    for entry in manifest['files'] + manifest['dependencies']:
        path = ROOT / entry['path']
        assert not path.is_symlink() and path.resolve().is_relative_to(ROOT)
        assert sha(path) == entry['sha256'], str(path)
        assert path.stat().st_mode & 0o777 == entry['mode'], str(path)
    paths = [e['path'] for e in manifest['files']] + [str((HERE / 'commit-inputs.json').relative_to(ROOT))]
    for name in paths:
        p = Path(name)
        assert p.is_relative_to(HERE.relative_to(ROOT))
        assert not {'work', 'mock-5', 'crops', 'code', 'logs', 'tmp'} & set(p.parts)
        assert p.suffix != '.png'
    assert len(paths) == len(set(paths))
    ignored = git('check-ignore', '--no-index', '-z', '--stdin', check=False,
                  stdin=b''.join(p.encode() + b'\0' for p in paths))
    assert ignored.returncode in (0, 1) and not ignored.stdout, 'commit path ignored'
    for stratum in ('ii', 'i-b'):
        assert git('check-ignore', '--no-index', str(HERE / 'crops' / stratum / 'probe.png'),
                   check=False).returncode == 0, 'PNGs not ignored'
    summary = json.loads((HERE / 'summary.json').read_text())
    mock = json.loads((HERE / 'mock-comparison.json').read_text())
    assert summary['state'] == 'completed' and summary['records_sha256'] == sha(HERE / 'records.jsonl')
    assert summary['mock_5_identical'] and mock['ok'] and mock['identical'] == 5
    assert summary['min_nice'] == 5 and summary['workers'] == 2 and min(summary['nice']) >= 5
    assert summary['originals_rehashed'] == 600 and summary['outputs_rehashed'] == 600
    records = [json.loads(v) for v in (HERE / 'records.jsonl').read_text().splitlines()]
    assert len(records) == len({r['id'] for r in records}) == 600
    for s, n in [('ii', 200), ('i-b', 400)]:
        assert sum(r['stratum'] == s for r in records) == summary['per_stratum'][s]['total'] == n
    assert all(not r['training_release_allowed'] and not r['train_pool_eligible'] for r in records)
    print(f'CHECK PASS: {len(paths)} hash-bound files; 600 records, summary, mock, HEAD, branch, index, dependencies, modes, PNG ignores')
    return manifest, paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', action='store_true')
    args = parser.parse_args()
    manifest, paths = validate()
    if args.commit:
        try:
            git('add', '--', *paths)
            staged = set(git('diff', '--cached', '--name-only').stdout.decode().splitlines())
            assert staged == set(paths), 'unexpected staged paths'
            git('diff', '--cached', '--check')
            print(git('commit', '-m', manifest['message']).stdout.decode())
        except subprocess.CalledProcessError as error:
            print(error.stderr.decode(), end='')
            raise SystemExit(error.returncode)
