#!/usr/bin/env python3
"""Coordinator-only sparse update drill on private staging's drill branch."""
import argparse
import json
from pathlib import Path
import shutil
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .common import atomic_json, canonical, records, sha, safe_path
from .layered import config_rows
from . import promote_candidate
from .promote_candidate import add_operations, client, verify_tree, xet_commit
from .seal_candidate import verify
from .update_labels import update, allowed
from .upload_staging import STAGING


def immutable_oids(api, repo, revision):
    result = {}
    for file in api.list_repo_tree(repo_id=repo, repo_type='dataset', revision=revision, recursive=True):
        if hasattr(file, 'size') and file.path.startswith(('data/', 'images/')):
            lfs = file.lfs
            result[file.path] = {'oid': (lfs.get('sha256') or lfs.get('oid')) if isinstance(lfs, dict) else getattr(lfs, 'sha256', None),
                                 'blob_id': file.blob_id, 'bytes': file.size}
    return result


def drill(candidate, corrections, scratch, expected_head, generation, repo=STAGING):
    candidate, scratch = Path(candidate).resolve(), Path(scratch).resolve()
    verify(candidate)
    if repo != STAGING or scratch.exists() or candidate == scratch or candidate in scratch.parents:
        raise ValueError('drill requires designated staging and fresh disjoint scratch directory')
    edits = list(records(corrections))
    if len(edits) != 10 or len({r['row_key'] for r in edits}) != 10:
        raise ValueError('drill requires exactly ten distinct real row corrections')
    scratch.mkdir(parents=True)
    base = scratch / 'C-copy'
    shutil.copytree(candidate, base)
    # The original seal applies to this independent byte copy before editing.
    verify(base)
    overlay = scratch / 'overlay'
    paths = update(base, corrections, overlay, generation)
    if paths != update(base, corrections, overlay, generation):
        raise ValueError('idempotent drill rerun changed commit operations')
    current = {r['row_key']: r for r in config_rows(base, 'labels_current')}
    from .layered import unpack
    import pyarrow.parquet as pq
    receipt = json.loads((overlay / 'manifests/UPDATE_RECEIPT.json').read_text())
    configs = json.loads((overlay / 'manifests/CONFIGS.json').read_text())
    labels, features = {}, {}
    for name, target in (('labels_current', labels), ('current_features', features)):
        for parts in configs[name].values():
            for path in parts:
                selected = overlay / path if (overlay / path).exists() else base / path
                for batch in pq.ParquetFile(selected).iter_batches(batch_size=256):
                    for output in batch.to_pylist():
                        row = unpack(output); target[row['row_key']] = row
    if set(labels) != set(current):
        raise ValueError('drill current cardinality changed')
    for edit in edits:
        label, feature = labels[edit['row_key']], features[edit['row_key']]
        if label['text'] == current[edit['row_key']]['text'] or label['text'] != edit['text']:
            raise ValueError('drill requires real sparse text edits')
        if label['label_version_id'] != feature['label_version_id'] or label['text_sha256'] != feature['label_sha256']:
            raise ValueError('drill current feature join differs')
    promote_candidate.require_xet()  # no silent HTTP fallback; transport is measured from hf_xet
    api, token = client()
    detail = api.repo_info(repo_id=repo, repo_type='dataset', revision='main')
    if not detail.private or detail.sha != expected_head:
        raise ValueError('private staging main differs from recorded head')
    expected = {e['path']: e for e in verify(base)['files']}
    manifest = json.loads((base / 'manifests/MANIFEST.json').read_text())
    expected.update({e['path']: e for e in manifest.get('frozen_trained', {}).get('files', [])})
    expected.update({e['path']: e for e in manifest.get('retained_public', [])})
    verify_tree(api, repo, expected_head, expected, token)
    api.create_branch(repo_id=repo, repo_type='dataset', branch='drill', revision=expected_head, exist_ok=False)
    before = immutable_oids(api, repo, expected_head)
    from huggingface_hub import CommitOperationAdd, CommitOperationDelete
    operations = [CommitOperationDelete(path_in_repo=p) if p in receipt['delete_paths'] else
                  add_operations(CommitOperationAdd, [(p, safe_path(overlay, p))])[0] for p in allowed(paths)]
    result, measured = xet_commit(api, repo_id=repo, repo_type='dataset', revision='drill', parent_commit=expected_head,
                                  operations=operations, commit_message='Ten-row sparse correction drill')
    for path in receipt['delete_paths']: expected.pop(path)
    expected.update({e['path']: e for e in receipt['files']})
    verify_tree(api, repo, result.oid, expected, token)
    if immutable_oids(api, repo, result.oid) != before:
        raise ValueError('drill changed immutable image/data oids')
    # Rewriting identical table bytes isolates CDC transport behaviour without another generation.
    rewrite_paths = [p for p in paths if p.startswith('tables/current_features')]
    second, rewrite = xet_commit(api, repo_id=repo, repo_type='dataset', revision='drill', parent_commit=result.oid,
        operations=add_operations(CommitOperationAdd, [(p, overlay / p) for p in rewrite_paths]),
        commit_message='CDC identical feature-table rewrite measurement')
    verify_tree(api, repo, second.oid, expected, token)
    verify(candidate)
    report = {'branch': 'drill', 'commit': result.oid, 'rewrite_commit': second.oid, 'rows': 10,
              'commit_paths': paths, 'immutable_oids_unchanged': True, 'current_joins_verified': True,
              'idempotent_rerun': True, 'local_operation_bytes': sum(e['bytes'] for e in receipt['files']),
              # Filled from hf_xet's own counters during the coordinator's run against HF;
              # null (with a reason) when the client did not report them.
              'transmitted_bytes': measured['transmitted_bytes'], 'rewrite_transmitted_bytes': rewrite['transmitted_bytes'],
              'transport': measured, 'rewrite_transport': rewrite,
              'transport_measurement': 'hf_xet total_transfer_bytes_completed plus inline regular files; local file sizes are not transport evidence.'}
    atomic_json(scratch / 'DRILL_REPORT.json', report)
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('candidate', type=Path); p.add_argument('corrections', type=Path)
    p.add_argument('--scratch', type=Path, required=True); p.add_argument('--parent-commit', required=True)
    p.add_argument('--generation', required=True)
    args = p.parse_args(argv)
    print(canonical(drill(args.candidate, args.corrections, args.scratch, args.parent_commit, args.generation)))


if __name__ == '__main__':
    main()
