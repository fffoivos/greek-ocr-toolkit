"""Copy explicitly selected local artifacts into a new tree and verify SHA-256 custody."""
from __future__ import annotations
import os
from pathlib import Path
import shutil
import tempfile
from ._files import contained, dump, hashes, sha

__all__ = ['copy_artifacts', 'verify']


def verify(destination: str | Path, manifest: dict) -> dict:
    """Verify the exact file set and bytes against a relative-path SHA manifest."""
    root = Path(destination)
    expected = manifest['files']
    for name in expected:
        contained(root, name)
    actual = hashes(root)
    actual.pop('custody_manifest.json', None)
    mismatches = sorted(k for k in set(actual) | set(expected) if actual.get(k) != expected.get(k))
    return dict(passed=not mismatches, files=len(expected), mismatches=mismatches)


def copy_artifacts(source: str | Path, destination: str | Path, paths: list[str]) -> dict:
    """Copy selected relative files, without symlinks/overwrites, then atomically publish.

    Source hashes are checked again after copying. The manifest contains no private
    absolute source paths. No deletions, remote transfers or git operations occur.
    """
    source, destination = Path(source).absolute(), Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    if not paths or len(paths) != len(set(paths)) or 'custody_manifest.json' in paths:
        raise ValueError('nonempty unique file selection required; manifest name reserved')
    inputs = {name: contained(source, name) for name in paths}
    before = {name: sha(p) for name, p in inputs.items()}
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.custody-', dir=destination.parent))
    try:
        for name, src in inputs.items():
            target = contained(stage, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
        manifest = dict(version=1, files=before)
        if not verify(stage, manifest)['passed'] or any(sha(p) != before[n] for n, p in inputs.items()):
            raise ValueError('custody hash mismatch or source changed during copy')
        dump(stage/'custody_manifest.json', manifest)
        if destination.exists():
            raise FileExistsError(destination)
        os.rename(stage, destination)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return dict(manifest=manifest, verification=verify(destination, manifest))
