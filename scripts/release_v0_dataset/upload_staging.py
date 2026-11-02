#!/usr/bin/env python3
"""Foreground coordinator uploader. Batching is permitted only on private staging.

Xet only: the P1g guard refuses an unqualified hub or unavailable Xet before any
work, and every operation is a filesystem str path (no silent HTTP fallback).
"""
import argparse
import json
from pathlib import Path
import sys
import tempfile

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .common import canonical, safe_path, verify_file
from .seal_candidate import verify
from . import promote_candidate
from .promote_candidate import add_operations, client, verify_tree, xet_commit
from .frozen_identity import public_file

STAGING = 'fffoivos/greek-ocr-lines-build'


def upload(root, repo=STAGING, batch_size=32, frozen_root=None):
    root = Path(root).resolve()
    sealed = verify(root)
    if repo != STAGING or batch_size < 1:
        raise ValueError('batch uploads restricted to designated private staging repository')
    build_manifest = json.loads((root / 'manifests/MANIFEST.json').read_text())
    frozen = build_manifest.get('frozen_trained', {}).get('files', [])
    if frozen and frozen_root is None:
        raise ValueError('A1 frozen trainer files require explicit --frozen-root')
    promote_candidate.require_xet()  # before any hashing, download or remote write; no silent HTTP fallback
    sources = {e['path']: safe_path(root, e['path']) for e in sealed['files']}
    for entry in frozen:
        path = public_file(frozen_root, entry['path'])
        verify_file({**entry, 'path': str(path)})
        sources[entry['path']] = path
    api, token = client()
    with tempfile.TemporaryDirectory(prefix='hfd-retained-public-') as cache:
        for entry in build_manifest.get('retained_public', []):
            # The A1 cache may contain only the 264 shards. Fetch these five
            # small retained files at the public revision, never at mutable main.
            from huggingface_hub import hf_hub_download
            path = hf_hub_download(repo_id=build_manifest['frozen_trained']['repo'],
                repo_type='dataset', revision=build_manifest['frozen_trained']['revision'],
                filename=entry['path'], token=token, cache_dir=cache)
            path = Path(path).resolve(strict=True)
            verify_file({**entry, 'path': str(path)})
            sources[entry['path']] = path
        return upload_verified(api, token, root, sealed, build_manifest, sources, repo, batch_size)


def upload_verified(api, token, root, sealed, manifest, sources, repo, batch_size):
    if '.gitattributes' not in sources:
        raise ValueError('.gitattributes must be emitted in C')
    api.create_repo(repo_id=repo, repo_type='dataset', private=True, exist_ok=True)
    detail = api.repo_info(repo_id=repo, repo_type='dataset')
    if not detail.private:
        raise ValueError('staging must be private')
    from huggingface_hub import CommitOperationAdd
    expected = {e['path']: e for e in sealed['files']}
    for entries in (manifest.get('frozen_trained', {}).get('files', []), manifest.get('retained_public', [])):
        if set(expected) & {e['path'] for e in entries}:
            raise ValueError('candidate overlaps retained public paths')
        expected.update({e['path']: e for e in entries})
    remote = {p.path for p in api.list_repo_tree(repo_id=repo, repo_type='dataset', revision='main', recursive=True) if hasattr(p, 'size')}
    if remote - set(expected):
        raise ValueError('unexpected staging paths: ' + str(sorted(remote - set(expected))))
    verify_tree(api, repo, detail.sha, {p: expected[p] for p in remote}, token)
    pending = sorted(set(expected) - remote)
    head = detail.sha
    for start in range(0, len(pending), batch_size):
        paths = pending[start:start + batch_size]
        operations = add_operations(CommitOperationAdd, [(p, sources[p]) for p in paths])
        result, measured = xet_commit(api, repo_id=repo, repo_type='dataset', revision='main', parent_commit=head,
                                      operations=operations, commit_message='Stage sealed C files and retained public tree')
        head = result.oid
        print(canonical({'commit': head, 'files_committed': len(paths),
                         'transmitted_bytes': measured['transmitted_bytes'], 'transport': measured}), flush=True)
    verify_tree(api, repo, head, expected, token)
    return head


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--repo', default=STAGING)
    p.add_argument('--batch-size', type=int, default=32)
    p.add_argument('--frozen-root', type=Path)
    args = p.parse_args(argv)
    print(canonical({'staging_commit': upload(args.root, args.repo, args.batch_size, args.frozen_root)}))


if __name__ == '__main__':
    sys.exit(main())
