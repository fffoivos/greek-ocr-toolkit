"""Read-only mover checks on synthetic files; never calls execute/transfer."""
import hashlib
import importlib.util
import os
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('clean3b_mover', Path(__file__).with_name('move_data.py'))
mover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mover)


def row(path='docs/input.bin', data=b'custody', rule='b'):
    return dict(path=path, bytes=str(len(data)), sha256=hashlib.sha256(data).hexdigest(), decision='MOVE', rule=rule)


def put(root, data=b'custody'):
    p = root / 'docs/input.bin'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


def test_dry_run_preflight_hashes_without_writes(tmp_path):
    repo = tmp_path / 'repo'
    p = put(repo)
    before = p.lstat()
    actions = mover.preflight([row()], repo, dry_run=True)
    after = p.lstat()
    assert actions[0][3] == 'move'
    assert (before.st_size, before.st_mtime_ns, before.st_ino) == (after.st_size, after.st_mtime_ns, after.st_ino)
    assert sorted(x.relative_to(repo).as_posix() for x in repo.rglob('*')) == ['docs', 'docs/input.bin']


def test_source_mismatch_stops(tmp_path):
    repo = tmp_path / 'repo'
    put(repo, b'changed')
    with pytest.raises(ValueError, match='Custody mismatch'):
        mover.preflight([row()], repo, dry_run=True)


def test_destination_conflict_stops_before_any_transfer(tmp_path):
    repo, dest = tmp_path / 'repo', tmp_path / 'dest'
    put(repo)
    p = put(dest, b'other')
    with pytest.raises(ValueError, match='Custody mismatch'):
        mover.preflight([row()], repo, dest)
    assert p.read_bytes() == b'other'
    assert (repo / row()['path']).read_bytes() == b'custody'


def test_identical_destination_skips_and_preserves_source(tmp_path):
    repo, dest = tmp_path / 'repo', tmp_path / 'dest'
    source, target = put(repo), put(dest)
    assert mover.preflight([row()], repo, dest)[0][3] == 'skip-identical'
    assert source.exists() and target.exists()


def test_execute_preflight_can_resume_but_dry_run_requires_source(tmp_path):
    repo, dest = tmp_path / 'repo', tmp_path / 'dest'
    repo.mkdir()
    put(dest)
    assert mover.preflight([row()], repo, dest)[0][3] == 'skip-identical'
    with pytest.raises(FileNotFoundError, match='MOVE source missing'):
        mover.preflight([row()], repo, dest, dry_run=True)


def test_dangling_link_uses_link_text_not_target_bytes(tmp_path):
    repo = tmp_path / 'repo'
    p = repo / 'docs/input.bin'
    p.parent.mkdir(parents=True)
    p.symlink_to('../missing-target')
    payload = os.fsencode(os.readlink(p))
    entry = row(data=payload, rule='d')
    assert mover.verify(p, entry) == 'symlink'
    assert len(mover.preflight([entry], repo, dry_run=True)) == 1


def test_same_hash_regular_file_cannot_replace_planned_link(tmp_path):
    repo, dest = tmp_path / 'repo', tmp_path / 'dest'
    p = repo / 'docs/input.bin'
    p.parent.mkdir(parents=True)
    p.symlink_to('target')
    put(dest, b'target')
    with pytest.raises(ValueError, match='Unexpected file/link type'):
        mover.preflight([row(data=b'target', rule='d')], repo, dest)


@pytest.mark.parametrize('path', ['../escape', '/absolute', 'docs/../escape', 'docs//input', ''])
def test_safe_paths_reject_escaping_and_noncanonical_paths(tmp_path, path):
    with pytest.raises(ValueError, match='Unsafe relative path'):
        mover.safe_path(tmp_path, path)


def test_symlink_ancestor_is_not_traversed(tmp_path):
    repo, outside = tmp_path / 'repo', tmp_path / 'outside'
    repo.mkdir(); outside.mkdir()
    (repo / 'docs').symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='Symlink ancestor'):
        mover.safe_path(repo, 'docs/input.bin')
