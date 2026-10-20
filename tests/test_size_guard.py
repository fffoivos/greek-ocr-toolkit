"""Read-only post-cleanup guard. Run directly or with pytest after untracking.

Reads blob sizes from the index rather than the working tree: deleting a file
without untracking it cannot make this guard pass. Uses no Git writing command.
"""
import os
from pathlib import Path
import subprocess

LIMIT = 5_000_000


def oversized_tracked_files(root):
    listing = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=root)
    entries = []
    for item in listing.split(b'\0'):
        if not item:
            continue
        metadata, path = item.split(b'\t', 1)
        mode, oid, stage = metadata.split()
        if mode == b'160000':
            continue  # submodule commit, not a tracked file blob
        entries.append((oid, os.fsdecode(path), stage))
    unique = sorted({oid for oid, _, _ in entries})
    if not unique:
        return []
    process = subprocess.run(['git', 'cat-file', '--batch-check=%(objectname) %(objectsize)'],
                             input=b'\n'.join(unique) + b'\n', stdout=subprocess.PIPE,
                             cwd=root, check=True)
    sizes = {oid: int(size) for oid, size in (line.split() for line in process.stdout.splitlines())}
    return sorted((path, sizes[oid]) for oid, path, _ in entries if sizes[oid] > LIMIT)


def test_no_tracked_file_exceeds_5_mb():
    # Archive verification supplies the source metadata through read-only
    # GIT_DIR/GIT_WORK_TREE; the exported tree has no .git marker of its own.
    root = Path(__file__).resolve().parents[1]
    oversized = oversized_tracked_files(root)
    assert not oversized, ('Tracked blobs exceed 5,000,000 bytes; retain custody receipts and untrack after moving:\n'
                           + '\n'.join(f'{p}\t{n}' for p, n in oversized))


if __name__ == '__main__':
    test_no_tracked_file_exceeds_5_mb()
