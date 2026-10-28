"""Local file custody helpers. No network or scheduler calls."""
import gzip
import hashlib
import json
import os
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def bound(spec):
    path = Path(spec['path'])
    if sha(path) != spec['sha256']:
        raise ValueError('SHA mismatch: ' + str(path))
    return path


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('w') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def write_rows(path, records):
    path = Path(path)
    with path.open('x') as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')


def spec(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)


def cadence(step, total, every):
    return step > 0 and (step % every == 0 or step == total)


def schedule(total=53616, every=50000):
    if total < 1 or every < 1:
        raise ValueError('positive horizon/cadence required')
    return sorted(set(range(every, total + 1, every)) | {total})
