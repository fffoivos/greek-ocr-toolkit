#!/usr/bin/env python3
"""CLEAN3B custody mover. --dry-run is read-only; execution is coordinator-only.

The plan hashes file contents, or raw link text for rule d symlinks. Every
source and existing destination is checked before execution. Existing identical
destinations are skipped with their repository sources left in place. No VCS
commands are used. Transfers copy exclusively, verify and fsync, then unlink the
source: this works across filesystems and never follows moved symlink targets.
"""
from __future__ import annotations
import argparse
import collections
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import stat
import sys

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parents[2]
FIELDS = ['path', 'bytes', 'sha256', 'moved_at']


def exists(path):
    return os.path.lexists(path)


def safe_path(root, relative):
    """Refuse escaping paths and symlink ancestors; terminal links are payload."""
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts or rel.as_posix() != relative:
        raise ValueError(f'Unsafe relative path: {relative!r}')
    parent = root
    for part in rel.parts[:-1]:
        parent = parent / part
        if parent.is_symlink():
            raise ValueError(f'Symlink ancestor is not a custody directory: {parent}')
        if exists(parent) and not parent.is_dir():
            raise ValueError(f'Non-directory ancestor: {parent}')
    return root / rel


def signature(path):
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode):
        raw = os.fsencode(os.readlink(path))
        return len(raw), hashlib.sha256(raw).hexdigest(), 'symlink'
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f'Not a regular file or symlink: {path}')
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return info.st_size, digest, 'file'


def verify(path, row):
    size, digest, kind = signature(path)
    if (size, digest) != (int(row['bytes']), row['sha256']):
        raise ValueError(f'Custody mismatch: {path}: {size} bytes sha256={digest}; '
                         f'expected {row["bytes"]} sha256={row["sha256"]}')
    if 'rule' in row and ((row['rule'] == 'd') != (kind == 'symlink')):
        raise ValueError(f'Unexpected file/link type: {path}')
    return kind


def read_plan(path):
    csv.field_size_limit(100_000_000)
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        required = {'path', 'bytes', 'sha256', 'decision', 'rule'}
        if not required <= set(reader.fieldnames or []):
            raise ValueError('Plan is missing required v2 columns')
        rows = list(reader)
    seen = set()
    for row in rows:
        if row['path'] in seen:
            raise ValueError('Duplicate plan path: ' + row['path'])
        seen.add(row['path'])
        if row['decision'] not in {'MOVE', 'KEEP'} or int(row['bytes']) < 0:
            raise ValueError('Invalid decision/size: ' + row['path'])
        if not re.fullmatch('[0-9a-f]{64}', row['sha256']):
            raise ValueError('Invalid sha256: ' + row['path'])
        if row['decision'] == 'MOVE' and row['rule'] not in {'a', 'b', 'c', 'd'}:
            raise ValueError('Invalid MOVE rule: ' + row['path'])
    return rows


def preflight(rows, repo, dest=None, *, dry_run=False):
    actions = []
    for row in rows:
        if row['decision'] != 'MOVE':
            continue
        source = safe_path(repo, row['path'])
        target = safe_path(dest, row['path']) if dest is not None else None
        source_present = exists(source)
        if source_present:
            source_kind = verify(source, row)
        elif dry_run or target is None or not exists(target):
            raise FileNotFoundError(f'MOVE source missing: {source}; receipt: {HERE / "RECEIPTS/INDEX.md"}')
        else:
            source_kind = None
        if target is not None and exists(target):
            target_kind = verify(target, row)
            if source_kind is not None and source_kind != target_kind:
                raise ValueError(f'Destination file/link type conflict: {target}')
            action = 'skip-identical'
        else:
            action = 'move'
        actions.append((row, source, target, action))
    return actions


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def transfer(source, target, row, before_unlink):
    """Exclusive copy + verified unlink. Journal intent before any source loss."""
    verify(source, row)
    before = source.lstat()
    target.parent.mkdir(parents=True, exist_ok=True)
    # Recheck ancestors after mkdir, including any destination race.
    # A terminal path is created exclusively: no replace/rename overwrites.
    if source.is_symlink():
        os.symlink(os.readlink(source), target)
    else:
        with source.open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
            dst.flush()
            os.fsync(dst.fileno())
        shutil.copystat(source, target, follow_symlinks=False)
    verify(target, row)
    fsync_dir(target.parent)
    after = source.lstat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
    ):
        raise ValueError(f'Source changed during transfer; preserved both paths: {source}')
    before_unlink()
    source.unlink()
    fsync_dir(source.parent)


def read_manifest(path):
    if not path.exists():
        return []
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        if reader.fieldnames != FIELDS:
            raise ValueError(f'Invalid manifest header: {path}')
        rows = list(reader)
    if len({r['path'] for r in rows}) != len(rows):
        raise ValueError(f'Duplicate entries in {path}')
    return rows


def rollback(repo, dest, manifest):
    rows = read_manifest(manifest)
    if not rows:
        raise ValueError('No journal entries to roll back')
    actions = []
    # Validate every entry first; an unrelated collision stops the entire run.
    for row in reversed(rows):
        source = safe_path(dest, row['path'])
        target = safe_path(repo, row['path'])
        if exists(target):
            verify(target, row)
            if exists(source):
                if verify(source, row) != verify(target, row):
                    raise ValueError(f'Rollback file/link type conflict: {target}')
            continue  # already restored, or journaled before interrupted unlink
        verify(source, row)
        actions.append((row, source, target))
    for row, source, target in actions:
        transfer(source, target, row, lambda: None)
    print(f'ROLLBACK: restored={len(actions)} already-present={len(rows)-len(actions)}; manifest retained')


def execute(rows, repo, dest, manifest):
    actions = preflight(rows, repo, dest)
    prior = read_manifest(manifest)
    planned = {r['path']: r for r in rows if r['decision'] == 'MOVE'}
    for row in prior:
        if row['path'] not in planned or any(row[k] != planned[row['path']][k] for k in ('bytes', 'sha256')):
            raise ValueError('Manifest conflicts with current plan: ' + row['path'])
    rollback_script = manifest.with_name('rollback.sh')
    command = [sys.executable, str(Path(__file__).resolve()), '--rollback', '--repo-root', str(repo),
               '--dest', str(dest), '--manifest', str(manifest)]
    script = '#!/bin/sh\nset -eu\nexec ' + shlex.join(command) + '\n'
    if rollback_script.is_symlink():
        raise ValueError('rollback.sh must not be a symlink')
    if rollback_script.exists():
        if rollback_script.read_text() != script:
            raise ValueError('Existing rollback.sh refers to a different execution; stop')
    else:
        with rollback_script.open('x') as stream:
            stream.write(script);stream.flush();os.fsync(stream.fileno())
        rollback_script.chmod(0o700)
    new = not manifest.exists()
    with manifest.open('a', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter='\t', lineterminator='\n')
        if new:
            writer.writeheader();stream.flush();os.fsync(stream.fileno())
        journaled = {r['path'] for r in prior}
        moved = skipped = 0
        for row, source, target, action in actions:
            if action == 'skip-identical':
                skipped += 1
                continue
            safe_path(repo, row['path']);safe_path(dest, row['path'])
            def journal(row=row):
                if row['path'] not in journaled:
                    writer.writerow(dict(path=row['path'], bytes=row['bytes'], sha256=row['sha256'],
                                         moved_at=datetime.now(timezone.utc).isoformat()))
                    stream.flush();os.fsync(stream.fileno());fsync_dir(manifest.parent)
                    journaled.add(row['path'])
            transfer(source, target, row, journal)
            moved += 1
    # Only remove parents actually emptied by MOVE; never recurse/delete content.
    parents = {p for _, source, _, action in actions if action == 'move' for p in source.parents if p != repo and repo in p.parents}
    emptied = 0
    for parent in sorted(parents, key=lambda p: len(p.parts), reverse=True):
        try:
            parent.rmdir();emptied += 1
        except OSError:
            pass
    print(f'EXECUTE: moved={moved} skipped-identical={skipped} empty-directories-removed={emptied}; '
          f'manifest={manifest}; rollback={rollback_script}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--execute', action='store_true')
    mode.add_argument('--rollback', action='store_true')
    parser.add_argument('--plan', type=Path, default=HERE / 'MOVE_PLAN_v2.tsv')
    parser.add_argument('--repo-root', type=Path, default=DEFAULT_REPO)
    parser.add_argument('--dest', type=Path)
    parser.add_argument('--manifest', type=Path, default=HERE / 'MOVE_MANIFEST.tsv')
    args = parser.parse_args(argv)
    repo = args.repo_root.resolve(strict=True)
    dest = args.dest.absolute() if args.dest else None
    manifest = args.manifest.absolute()
    if not args.dry_run and dest is None:
        parser.error('--execute/--rollback requires --dest (coordinator destination: /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data)')
    if dest is not None:
        # No mirror inside the checkout, nor a checkout inside the mirror.
        canonical = dest.resolve()
        if canonical == repo or canonical.is_relative_to(repo) or repo.is_relative_to(canonical):
            raise ValueError('Data destination and repository must be disjoint')
        for parent in [dest, *dest.parents]:
            if parent.is_symlink():
                raise ValueError(f'Symlink in destination root: {parent}')
    if args.dry_run:
        rows = read_plan(args.plan)
        actions = preflight(rows, repo, dest, dry_run=True)
        sums = collections.defaultdict(lambda: [0, 0])
        for row in rows:
            sums[row['decision']][0] += 1;sums[row['decision']][1] += int(row['bytes'])
        print(f'DRY-RUN: MOVE={sums["MOVE"][0]} bytes={sums["MOVE"][1]} '
              f'KEEP={sums["KEEP"][0]} bytes={sums["KEEP"][1]} '
              f'verified={len(actions)} symlinks={sum(r[0]["rule"] == "d" for r in actions)}; no files moved')
        return
    for output in (manifest, manifest.with_suffix('.lock')):
        if output.is_symlink():
            raise ValueError(f'Journal/lock must not be a symlink: {output}')
    # Only execution creates a lock or any other output. Dry-run never writes.
    if not manifest.parent.is_dir():
        raise ValueError('Manifest directory must already exist')
    with manifest.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.rollback:
            rollback(repo, dest, manifest)
        else:
            execute(read_plan(args.plan), repo, dest, manifest)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, csv.Error) as error:
        print(f'STOP: {error}', file=sys.stderr)
        sys.exit(1)
