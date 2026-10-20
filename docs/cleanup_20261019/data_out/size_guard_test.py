"""Proposed pytest only; not installed into tests/ by CLEAN3A.

After approval, install as tests/test_tracked_file_size.py. MB means 1,000,000
bytes. Symlinks are measured as their stored target text, never dereferenced.
"""
import os
from pathlib import Path
import stat
import subprocess

MAX_TRACKED_BYTES = 5_000_000


def test_no_tracked_file_exceeds_5_mb():
    root = next(p for p in Path(__file__).resolve().parents if (p / '.git').exists())
    result = subprocess.run(
        ['git', 'ls-files', '-z'], cwd=root, check=True, stdout=subprocess.PIPE
    )
    oversized = []
    unavailable = []
    for raw in result.stdout.split(b'\0'):
        if not raw:
            continue
        relative = os.fsdecode(raw)
        path = root / relative
        try:
            info = path.lstat()
        except FileNotFoundError:
            unavailable.append(relative)
            continue
        if stat.S_ISLNK(info.st_mode):
            size = len(os.fsencode(os.readlink(path)))
        elif stat.S_ISREG(info.st_mode):
            size = info.st_size
        else:
            unavailable.append(relative + ' (not a regular file or symlink)')
            continue
        if size > MAX_TRACKED_BYTES:
            oversized.append(f'{relative}\t{size}')
    assert not unavailable, 'Tracked paths unavailable for size check:\n' + '\n'.join(unavailable)
    assert not oversized, (
        'Tracked files exceed 5,000,000 bytes; move to GREEK_OCR_DATA_ROOT '
        'and retain a hash receipt:\n' + '\n'.join(oversized)
    )
