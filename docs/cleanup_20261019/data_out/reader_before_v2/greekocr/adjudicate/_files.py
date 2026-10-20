"""Private local-file helpers; never acquire data or follow custody symlinks."""
from __future__ import annotations
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator


def sha(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def dump(path: str | Path, value: Any) -> None:
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def rows(path: str | Path) -> Iterator[dict]:
    path = Path(path)
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def contained(root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('unsafe relative path')
    path = root / relative
    if any(p.is_symlink() for p in [root, path, *path.parents]):
        raise ValueError('symlink is not a custody input')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('path escapes root')
    return path


def hashes(root: Path) -> dict[str, str]:
    if root.is_symlink() or any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('symlink in file tree')
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}
