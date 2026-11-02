#!/usr/bin/env python3
"""Coordinator-only recovery: restore public main's tree to a recorded parent commit after a failed promotion readback.

One CAS commit on top of the failed head. LFS files are restored server-side with CommitOperationCopy from the
parent revision, so no LFS bytes are uploaded; only small non-LFS files are re-sent. The result is then read back:
the new tree must equal the parent tree path-for-path (git blob oid, and lfs sha256 where present).
Token from HF_TOKEN only. --dry-run lists the operations and makes no commit.
"""
import argparse
import json
import os
import sys
import tempfile


def tree(api, repo, revision):
    out = {}
    for e in api.list_repo_tree(repo, repo_type='dataset', revision=revision, recursive=True, expand=False):
        if getattr(e, 'blob_id', None) is None:
            continue  # folder
        lfs = getattr(e, 'lfs', None)
        out[e.path] = {'oid': e.blob_id, 'lfs': lfs.sha256 if lfs else None, 'size': e.size}
    return out


def plan(parent, head):
    deletes = sorted(p for p in head if p not in parent)
    restores = sorted(p for p in parent if head.get(p) != parent[p])
    return deletes, restores


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--repo', default='fffoivos/greek-ocr-lines')
    p.add_argument('--parent', required=True, help='full SHA of the commit whose tree is restored')
    p.add_argument('--expected-head', required=True, help='full SHA of the failed promotion commit (CAS)')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args(argv)
    if len(a.parent) != 40 or len(a.expected_head) != 40:
        raise SystemExit('full 40-character SHAs required')
    from huggingface_hub import HfApi, CommitOperationAdd, CommitOperationCopy, CommitOperationDelete
    api = HfApi(token=None if a.dry_run else os.environ['HF_TOKEN'])
    head_now = api.repo_info(a.repo, repo_type='dataset').sha
    if head_now != a.expected_head:
        raise SystemExit(f'main is at {head_now}, not the expected failed head {a.expected_head}; refusing')
    parent, head = tree(api, a.repo, a.parent), tree(api, a.repo, a.expected_head)
    deletes, restores = plan(parent, head)
    lfs_restores = [r for r in restores if parent[r]['lfs']]
    small_restores = [r for r in restores if not parent[r]['lfs']]
    summary = {'deletes': len(deletes), 'lfs_copies': len(lfs_restores), 'small_reuploads': len(small_restores),
               'small_bytes': sum(parent[r]['size'] for r in small_restores)}
    print(json.dumps(summary), flush=True)
    if a.dry_run:
        print(json.dumps({'deletes': deletes[:20], 'restores': restores[:20]}))
        return
    if not deletes and not restores:
        print('NOTHING TO REVERT')
        return
    with tempfile.TemporaryDirectory() as tmp:
        from huggingface_hub import hf_hub_download
        ops = [CommitOperationDelete(path_in_repo=d) for d in deletes]
        ops += [CommitOperationCopy(src_path_in_repo=r, path_in_repo=r, src_revision=a.parent) for r in lfs_restores]
        for r in small_restores:
            local = hf_hub_download(a.repo, r, repo_type='dataset', revision=a.parent, local_dir=tmp)
            ops.append(CommitOperationAdd(path_in_repo=r, path_or_fileobj=str(local)))
        info = api.create_commit(a.repo, repo_type='dataset', operations=ops, parent_commit=a.expected_head,
                                 commit_message=f'Revert failed promotion {a.expected_head[:12]}: restore tree of {a.parent[:12]}')
    after = tree(api, a.repo, info.oid)
    if after != parent:
        diff = sorted(p for p in set(after) | set(parent) if after.get(p) != parent.get(p))[:10]
        raise SystemExit(f'REVERT READBACK FAILED at {info.oid}: differing paths {diff}')
    print(json.dumps({'revert_commit': info.oid, 'tree_equals_parent': True, **summary}))


if __name__ == '__main__':
    sys.exit(main())
