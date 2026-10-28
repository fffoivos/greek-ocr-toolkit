"""Publication assembly must use commit bytes, isolate outputs and retain evidence."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

import pytest
from scripts.release_v0_publish import build_public_tree as module


def fixture_archive(monkeypatch, source):
    def archive(repo, commit, destination):
        assert commit == 'reviewed-commit'
        shutil.copytree(source, destination, dirs_exist_ok=True, symlinks=True)
        return 'a'*40, [p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()]
    monkeypatch.setattr(module, 'archive_commit', archive)


def put(root, path, data):
    target = root/path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)


def test_commit_snapshot_filters_then_validates_actual_tree(tmp_path, monkeypatch):
    source = tmp_path/'commit'; source.mkdir()
    put(source, 'greekocr/parser.py', b'field = "fullTextAnnotation"\n')
    put(source, 'audit/deck/private/key.jsonl', b'answer')
    put(source, 'out/run/pytest_01/data.json', b'fixture')
    put(source, 'out/run/CLAIM.json', b'bound evidence')
    put(source, 'scripts/release_v0_publish/EVIDENCE_PATHS.txt', b'out/run/CLAIM.json\n')
    fixture_archive(monkeypatch, source)
    monkeypatch.setattr(module, 'check_evidence', lambda tree: [])
    calls = []
    def validate(tree, basetemp, logs):
        calls.append(tree)
        assert (tree/'greekocr/parser.py').read_bytes() == b'field = "fullTextAnnotation"\n'
        assert not (tree/'audit/deck/private/key.jsonl').exists()
        assert not (tree/'out/run/pytest_01/data.json').exists()
        assert (tree/'out/run/CLAIM.json').read_bytes() == b'bound evidence'
        return [dict(check='imports', exit_code=0), dict(check='pytest', exit_code=0)]
    monkeypatch.setattr(module, 'validate_tree', validate)
    out = tmp_path/'public'
    receipt = module.build(tmp_path, 'reviewed-commit', out)
    assert receipt['passed'] and calls == [out]
    assert receipt['commit'] == 'a'*40
    rows = list(csv.DictReader((out/'PUBLIC_TREE_MANIFEST.tsv').open(), delimiter='\t'))
    for row in rows:
        data = (out/row['path']).read_bytes()
        assert len(data) == int(row['bytes'])
        assert hashlib.sha256(data).hexdigest() == row['sha256']
    private = list(csv.DictReader((out/'PUBLIC_TREE_VALIDATION/PRIVATE_REVIEW.tsv').open(), delimiter='\t'))
    assert [r['path'] for r in private] == ['audit/deck/private/key.jsonl']
    with pytest.raises(ValueError, match='must not exist'):
        module.build(tmp_path, 'reviewed-commit', out)


def test_validation_mutation_fails_and_original_commit_bytes_survive(tmp_path, monkeypatch):
    source = tmp_path/'commit'; source.mkdir()
    put(source, 'historical.receipt.json', b'original')
    fixture_archive(monkeypatch, source)
    monkeypatch.setattr(module, 'check_evidence', lambda tree: [])
    def validate(tree, basetemp, logs):
        (tree/'historical.receipt.json').write_bytes(b'rebuilt')
        return [dict(check='pytest', exit_code=0)]
    monkeypatch.setattr(module, 'validate_tree', validate)
    out = tmp_path/'public'
    receipt = module.build(tmp_path, 'reviewed-commit', out)
    assert not receipt['passed']
    assert receipt['validation_modified_payload_paths'] == ['historical.receipt.json']
    assert (out/'historical.receipt.json').read_bytes() == b'original'


def test_archive_uses_resolved_commit_and_never_worktree(monkeypatch, tmp_path):
    import io, tarfile
    calls = []
    monkeypatch.setattr(module.subprocess, 'check_output', lambda args, **kwargs: 'b'*40+'\n')
    def run(args, **kwargs):
        calls.append(args)
        with tarfile.open(fileobj=kwargs['stdout'], mode='w') as tar:
            member = tarfile.TarInfo('source.py'); member.size = 6; member.mode = 0o755
            tar.addfile(member, io.BytesIO(b'commit'))
    monkeypatch.setattr(module.subprocess, 'run', run)
    put(tmp_path, 'source.py', b'working tree')
    destination = tmp_path/'snapshot'; destination.mkdir()
    resolved, paths = module.archive_commit(tmp_path, 'HEAD', destination)
    assert calls == [['git', 'archive', '--format=tar', 'b'*40]]
    assert resolved == 'b'*40 and paths == ['source.py']
    assert (destination/'source.py').read_bytes() == b'commit'
    assert (destination/'source.py').stat().st_mode & 0o777 == 0o755
