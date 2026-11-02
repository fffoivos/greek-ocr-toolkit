#!/usr/bin/env python3
"""Coordinator-only foreground promotion: one CAS commit, then whole-tree SHA readback."""
import argparse
from contextlib import contextmanager
import json
import os
import re
from pathlib import Path
import sys
import tempfile

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .common import canonical, info, safe_path, sha, verify_file
from .seal_candidate import verify


QUALIFIED_HUB = '2.2.0'


def require_xet():
    """The archive uploader's guard (P1g): fail before any HTTP/LFS fallback.

    The private Xet dispatch was qualified on huggingface_hub 2.2.0; Xet must be
    available and enabled, and the native module importable.
    """
    import huggingface_hub
    from huggingface_hub._commit_api import is_xet_available
    if huggingface_hub.__version__ != QUALIFIED_HUB:
        raise RuntimeError('Xet upload requires qualified huggingface_hub ' + QUALIFIED_HUB)
    if not is_xet_available():
        raise RuntimeError('Xet unavailable or disabled; HTTP/LFS fallback forbidden')
    import hf_xet  # noqa: F401


def add_operations(factory, items):
    """CommitOperationAdd from filesystem str paths only: a file object or buffer
    makes huggingface_hub fall back to HTTP, which is forbidden."""
    operations = []
    for path_in_repo, local in items:
        if not isinstance(local, (str, os.PathLike)):
            raise RuntimeError('Xet requires filesystem str paths; HTTP fallback forbidden')
        operation = factory(path_in_repo=path_in_repo, path_or_fileobj=str(local))
        if not isinstance(operation.path_or_fileobj, str):
            raise RuntimeError('Xet requires filesystem str paths; HTTP fallback forbidden')
        operations.append(operation)
    return operations


@contextmanager
def transfer_meter():
    """Record hf_xet's own upload counters for commits made inside the block.

    huggingface_hub 2.2.0 passes XetUploadProgressReporter.update_progress to
    hf_xet only when progress bars are enabled; total_transfer_bytes_completed is
    the network transfer after chunk deduplication. Local file sizes are not
    transport evidence, so a missing reporter leaves the measurement null.
    """
    meter = {'xet_transfer_bytes': 0, 'xet_file_bytes': 0, 'reports': 0, 'reason': None}
    try:
        from importlib import import_module
        utils = import_module('huggingface_hub.utils')
        reporting = import_module('huggingface_hub.utils._xet_progress_reporting')
        reporter = reporting.XetUploadProgressReporter
        original, disabled = reporter.update_progress, utils.are_progress_bars_disabled
    except (ImportError, AttributeError) as exc:
        meter['reason'] = 'Xet progress reporter unavailable: ' + type(exc).__name__
        yield meter
        return
    def update_progress(self, group_report, *args, **kwargs):
        meter['reports'] += 1
        meter['xet_transfer_bytes'] = max(meter['xet_transfer_bytes'], int(group_report.total_transfer_bytes_completed))
        meter['xet_file_bytes'] = max(meter['xet_file_bytes'], int(group_report.total_bytes_completed))
        return original(self, group_report, *args, **kwargs)
    update_progress.__name__ = 'update_progress'
    reporter.update_progress = update_progress
    utils.are_progress_bars_disabled = lambda *args, **kwargs: False
    try:
        yield meter
    finally:
        reporter.update_progress = original
        utils.are_progress_bars_disabled = disabled


def transport(meter, operations):
    """Transmitted bytes for one commit: Xet transfer plus inline regular files."""
    modes = [getattr(op, '_upload_mode', None) for op in operations if hasattr(op, 'path_or_fileobj')]
    sizes = [Path(op.path_or_fileobj).stat().st_size for op in operations if hasattr(op, 'path_or_fileobj')]
    regular = sum(n for n, mode in zip(sizes, modes) if mode == 'regular')
    unknown = any(mode not in ('regular', 'lfs') for mode in modes)
    lfs = any(mode == 'lfs' and n for n, mode in zip(sizes, modes))
    result = dict(meter, regular_upload_bytes=None if unknown else regular, local_operation_bytes=sum(sizes))
    if meter['reason'] or unknown or (lfs and not meter['reports']):
        result.update(transmitted_bytes=None, reason=meter['reason'] or (
            'upload mode not recorded by the client' if unknown else 'no Xet progress report for LFS-mode files'))
    else:
        result.update(transmitted_bytes=meter['xet_transfer_bytes'] + regular,
                      basis='hf_xet total_transfer_bytes_completed + raw bytes of regular (inline) files')
    return result


def xet_commit(api, **kwargs):
    """One guarded create_commit; returns the commit and its measured transport."""
    require_xet()
    with transfer_meter() as meter:
        result = api.create_commit(**kwargs)
    return result, transport(meter, kwargs['operations'])


def client():
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
    os.environ['HF_TOKEN_PATH'] = '/dev/null'
    # A token is required even for reads of private staging. Never consult saved tokens.
    token = os.environ.get('HF_TOKEN')
    if not token:
        raise ValueError('HF_TOKEN must be injected into the foreground environment')
    from huggingface_hub import HfApi
    return HfApi(token=token), token


def verify_tree(api, repo, revision, expected, token, allow_replacements=()):
    from huggingface_hub import hf_hub_download
    remote = {p.path: p for p in api.list_repo_tree(repo_id=repo, repo_type='dataset', revision=revision, recursive=True) if hasattr(p, 'size')}
    if set(remote) - set(allow_replacements) != set(expected):
        raise ValueError('whole remote tree differs; unexpected/missing: ' + str(sorted(set(remote) ^ set(expected))))
    # Whole-tree object readback. Bulk LFS oids are the byte SHA256; the separate
    # full-download CPU acceptance proves their actual bytes before promotion.
    with tempfile.TemporaryDirectory(prefix='rel0-hf-readback-') as scratch:
        for path, entry in sorted(expected.items()):
            file = remote[path]
            if file.size != entry['bytes']:
                raise ValueError('remote file size differs: ' + path)
            lfs = getattr(file, 'lfs', None)
            oid = (lfs.get('sha256') or lfs.get('oid')) if isinstance(lfs, dict) else getattr(lfs, 'sha256', None)
            if oid:
                if oid != entry['sha256']:
                    raise ValueError('remote LFS byte SHA256 differs: ' + path)
            else:
                local = hf_hub_download(repo_id=repo, repo_type='dataset', revision=revision,
                                        filename=path, token=token, cache_dir=scratch)
                verify_file({**entry, 'path': local})


def promote(root, repo, expected_head, frozen, api=None, token=None):
    root = Path(root).resolve()
    sealed = verify(root)
    if api is None:
        api, token = client()
    if not expected_head or not re.fullmatch(r'[0-9a-f]{40}', expected_head):
        raise ValueError('full recorded public parent_commit required')
    expected = {e['path']: e for e in frozen['files']}
    if len(expected) != len(frozen['files']) or any(not (p.startswith('data/') or p == '.gitattributes') for p in expected):
        raise ValueError('frozen manifest permits only trained data/ and explicit .gitattributes')
    manifest = json.loads((root / 'manifests/MANIFEST.json').read_text())
    bound = manifest.get('frozen_trained', {}).get('files', [])
    identity = lambda entries: {e['path']: (e['bytes'], e['sha256']) for e in entries if e['path'].startswith('data/')}
    if identity(bound) != identity(frozen['files']):
        raise ValueError('promotion frozen inventory differs from sealed C')
    # .gitattributes belongs to C; an older caller may still list it as frozen.
    expected.pop('.gitattributes', None)
    expected.update({e['path']: e for e in manifest.get('retained_public', [])})
    additions = {e['path']: e for e in sealed['files']}
    if set(additions) & set(expected):
        raise ValueError('candidate overlaps immutable frozen paths')
    # A reviewed inventory is also the precise allowed starting public tree.
    remote = {p.path for p in api.list_repo_tree(repo_id=repo, repo_type='dataset', revision=expected_head, recursive=True) if hasattr(p, 'size')}
    if remote - (set(expected) | set(additions)) or set(expected) - remote:
        raise ValueError('unexpected public parent tree paths')
    verify_tree(api, repo, expected_head, expected, token, allow_replacements=set(additions))
    require_xet()
    from huggingface_hub import CommitOperationAdd
    operations = add_operations(CommitOperationAdd, [(p, safe_path(root, p)) for p in sorted(additions)])
    # Public promotion remains exactly one CAS commit.
    result, measured = xet_commit(api, repo_id=repo, repo_type='dataset', revision='main',
        parent_commit=expected_head, operations=operations, commit_message='Publish sealed dataset candidate C')
    expected.update(additions)
    verify_tree(api, repo, result.oid, expected, token)
    return {'commit': result.oid, 'parent_commit': expected_head,
            'whole_tree_files_verified': len(expected), 'candidate_manifest_sha256': sha(root / 'C_MANIFEST.json'),
            'transmitted_bytes': measured['transmitted_bytes'], 'transport': measured}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--repo', default='fffoivos/greek-ocr-lines')
    p.add_argument('--parent-commit', required=True)
    p.add_argument('--frozen-manifest', type=Path, required=True)
    args = p.parse_args(argv)
    print(canonical(promote(args.root, args.repo, args.parent_commit, json.loads(args.frozen_manifest.read_text()))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
