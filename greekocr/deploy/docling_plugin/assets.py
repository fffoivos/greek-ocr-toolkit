"""Explicit variant-only recognition downloads; verify before release loading."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
from tempfile import TemporaryDirectory

from greekocr.segmenters.assets import cache_root, sha256, verify_file


def _verify(directory, manifest_sha256):
    manifest_path = directory / 'MANIFEST.json'
    if manifest_sha256 is not None and sha256(manifest_path) != manifest_sha256:
        raise ValueError('OCR manifest SHA256 mismatch; file retained')
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('schema') != 'greekocr-release-v1':
        raise ValueError('unsupported release manifest')
    files = manifest['files']
    if not {'config.json', 'codec.json', 'model.safetensors'} <= files.keys():
        raise ValueError('incomplete release manifest')
    for name in files:
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or name == 'MANIFEST.json':
            raise ValueError(f'unsafe release manifest path: {name}')
    missing = [str(directory / name) for name in files if not (directory / name).is_file()]
    if missing:
        raise FileNotFoundError('Missing release files: ' + ', '.join(missing))
    for name, identity in files.items():
        verify_file(directory / name, identity)
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    if actual != set(files) | {'MANIFEST.json'}:
        raise ValueError('release contains files absent from MANIFEST.json')
    return manifest


def fetch_model(*, repo_id, variant, revision, manifest_sha256=None):
    """Return a regular-file release and resolved commit; cached revisions work offline.

    Tags resolve once through HF's cached ref. A receipt binds the requested ref to
    the immutable snapshot commit. No conversion or unverified loader call occurs.
    """
    from huggingface_hub import snapshot_download
    from huggingface_hub import constants
    from huggingface_hub.utils import LocalEntryNotFoundError
    if variant not in ('x1', 'x1.5', 'x2') or not revision:
        raise ValueError('explicit model variant and revision required')
    kwargs = dict(repo_id=repo_id, revision=revision, allow_patterns=[f'{variant}/*'],
                  cache_dir=str(cache_root() / 'models' / 'hub'))
    try:
        snapshot = Path(snapshot_download(**kwargs, local_files_only=True))
    except LocalEntryNotFoundError:
        snapshot = Path(snapshot_download(**kwargs))
    commit = snapshot.name
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError(f'cannot record resolved model commit from snapshot: {snapshot}')
    source = snapshot / variant
    try:
        _verify(source, manifest_sha256)
    except FileNotFoundError as error:
        if os.environ.get('HF_HUB_OFFLINE', str(constants.HF_HUB_OFFLINE)).upper() in ('1', 'ON', 'YES', 'TRUE'):
            raise FileNotFoundError(f'Offline OCR cache is incomplete: {error}') from error
        # A commit directory can exist for another variant or an interrupted fetch.
        # Resolve no mutable ref again: finish only this variant at the cached pin.
        snapshot = Path(snapshot_download(**dict(kwargs, revision=commit)))
        if snapshot.name != commit:
            raise ValueError(f'model snapshot commit changed: expected {commit}, got {snapshot.name}')
        source = snapshot / variant
        _verify(source, manifest_sha256)
    # HF blobs are symlinks; load_release intentionally accepts regular files only.
    destination = cache_root() / 'models' / ('repo-' + hashlib.sha256(repo_id.encode()).hexdigest()[:16]) / commit
    destination.mkdir(parents=True, exist_ok=True)
    release = destination / variant
    if not release.exists():
        with TemporaryDirectory(prefix='.verify-', dir=destination) as scratch:
            copied = Path(scratch) / variant
            shutil.copytree(source, copied, symlinks=False)
            _verify(copied, manifest_sha256)
            try:
                copied.rename(release)
            except OSError:
                if not release.is_dir():
                    raise
    _verify(release, manifest_sha256)
    receipt = dict(repo_id=repo_id, requested_revision=revision, resolved_commit=commit,
                   variant=variant, manifest_sha256=sha256(release / 'MANIFEST.json'))
    # Stable per-request receipt; separate from the sealed variant directory.
    key = hashlib.sha256((revision + ':' + variant).encode()).hexdigest()[:16]
    with TemporaryDirectory(prefix='.receipt-', dir=destination) as scratch:
        temporary = Path(scratch) / 'receipt.json'
        temporary.write_text(json.dumps(receipt, indent=2) + '\n')
        temporary.replace(destination / f'acquisition-{key}.json')
    return release, receipt
