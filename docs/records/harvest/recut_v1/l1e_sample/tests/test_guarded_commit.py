import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('t6e_commit', HERE / 'guarded_commit.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


@pytest.fixture
def commit_scope(tmp_path, monkeypatch):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=tmp_path)
    git('init', '-q', '-b', 'sol/l1e-mask')
    git('config', 'user.name', 'Local Test')
    git('config', 'user.email', 'local-test@example.invalid')
    base = tmp_path / 'sample'
    base.mkdir()
    (base / '.gitignore').write_text('/test_out*/\n/COMMIT_STATUS.json\n/handoff.patch\n')
    source = base / 'run.py'
    source.write_text('before\n')
    git('add', 'sample')
    git('commit', '-qm', 'baseline')
    monkeypatch.setattr(helper, 'ROOT', tmp_path)
    monkeypatch.setattr(helper, 'BASE', base)
    monkeypatch.setattr(helper, 'MANIFEST', base / 'commit-inputs.json')
    monkeypatch.setattr(helper, 'STATUS', base / 'COMMIT_STATUS.json')
    monkeypatch.setattr(helper, 'EXPECTED_HEAD', git('rev-parse', 'HEAD').decode().strip())
    source.write_text('after\n')
    ignored = base / 'test_out_t6e'
    ignored.mkdir()
    (ignored / 'pixels.png').write_bytes(b'ignored-output')
    (base / 'new-test.py').write_text('test source\n')
    return git, base


def test_helper_commits_only_changed_sources_and_excludes_ignored_outputs(commit_scope, monkeypatch):
    git, base = commit_scope
    helper.prepare()
    manifest, paths = helper.validate()
    assert set(paths) == {'sample/run.py', 'sample/new-test.py', 'sample/commit-inputs.json'}
    assert manifest['ignored_paths_excluded'] == 1
    monkeypatch.setattr(sys, 'argv', ['guarded_commit.py'])
    helper.main()
    assert json.loads(helper.STATUS.read_text())['status'] == 'committed'
    committed = set(git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').decode().splitlines())
    assert committed == set(paths)
    assert (base / 'test_out_t6e/pixels.png').read_bytes() == b'ignored-output'


def test_helper_rejects_source_changes_after_manifest(commit_scope):
    _, base = commit_scope
    helper.prepare()
    (base / 'run.py').write_text('changed after binding\n')
    with pytest.raises(RuntimeError, match='scope/hash changed'):
        helper.validate()
