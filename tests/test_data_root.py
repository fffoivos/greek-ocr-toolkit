"""CLEAN3B resolver tests; the only test file added by this run."""
from pathlib import Path

import pytest

from greekocr.ops import data_root
from scripts.layout_paths import EXTRA_MOVES


@pytest.fixture
def roots(tmp_path, monkeypatch):
    repo = tmp_path / 'repo'
    external = tmp_path / 'data'
    repo.mkdir()
    external.mkdir()
    monkeypatch.setattr(data_root, 'REPO_ROOT', repo)
    monkeypatch.setenv('GREEK_OCR_DATA_ROOT', str(external))
    receipts = repo / data_root.RECEIPTS
    receipts.mkdir(parents=True)
    (receipts / 'receipt_01.tsv').write_text(
        'path\tbytes\tsha256\tproducing_commit\tkind\n'
        'docs/sample.bin\t3\tabc\t123\tother\n'
    )
    data_root._receipt_paths.cache_clear()
    return repo, external


def put(root, text='abc'):
    path = root / 'docs/sample.bin'
    path.parent.mkdir(exist_ok=True)
    path.write_text(text)
    return path


def test_repository_precedes_external(roots):
    repo, external = roots
    local = put(repo)
    put(external, 'external')
    assert data_root.resolve('docs/sample.bin') == local


def test_external_mirror_when_repo_file_absent(roots):
    repo, external = roots
    mirror = put(external)
    assert data_root.resolve(Path('docs/sample.bin')) == mirror
    assert data_root.input_path(repo / 'docs/sample.bin') == mirror


def test_missing_names_exact_receipt(roots):
    with pytest.raises(FileNotFoundError, match=r'receipt_01.tsv') as error:
        data_root.resolve('docs/sample.bin')
    assert 'GREEK_OCR_DATA_ROOT' in str(error.value)
    assert 'docs/sample.bin' in str(error.value)


def test_unset_root_and_unknown_path_name_index(roots, monkeypatch):
    monkeypatch.delenv('GREEK_OCR_DATA_ROOT')
    with pytest.raises(FileNotFoundError, match=r'RECEIPTS/INDEX.md') as error:
        data_root.resolve('docs/unknown.bin')
    assert 'unset' in str(error.value)


@pytest.mark.parametrize('path', ['../escape', '/absolute', 'docs/../../escape', ''])
def test_rejects_non_relative_paths(roots, path):
    with pytest.raises(ValueError, match='repo-relative'):
        data_root.resolve(path)


def test_input_adapter_preserves_explicit_other_inputs(roots, tmp_path, monkeypatch):
    repo, external = roots
    outside = tmp_path / 'outside.bin'
    outside.write_text('fixture')
    assert data_root.input_path(outside) == outside
    absent = tmp_path / 'another_checkout/missing.bin'
    assert data_root.input_path(absent) == absent
    monkeypatch.chdir(repo)
    put(repo)
    assert data_root.input_path('docs/sample.bin') == Path('docs/sample.bin')
    (repo / 'docs/sample.bin').unlink()
    mirror = put(external)
    assert data_root.input_path('docs/sample.bin') == mirror


def test_symlink_targets_are_not_mistaken_for_available_data(roots):
    repo, external = roots
    (repo / 'docs').mkdir(exist_ok=True)
    (repo / 'docs/sample.bin').symlink_to('absent.bin')
    with pytest.raises(FileNotFoundError, match='receipt_01.tsv'):
        data_root.resolve('docs/sample.bin')
    mirror = put(external)
    assert data_root.resolve('docs/sample.bin') == mirror


def test_resolver_import_is_standard_library_only_and_avoids_vendor_cycle():
    import os
    import subprocess
    import sys
    root = Path(__file__).resolve().parents[1]
    code = (
        'import sys; from greekocr.ops.data_root import resolve; '
        'assert not ({"torch", "PIL", "numpy", "scipy"} & sys.modules.keys()); '
        'import greekocr._vendor.train.mix; '
        'from greekocr.ops import file_sha256, watch; '
        'assert callable(file_sha256) and callable(watch)'
    )
    subprocess.run([sys.executable, '-c', code], cwd=root, check=True,
                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))


def test_layout_aliases_find_relocated_local_and_historical_mirror(roots):
    repo, external = roots
    old = 'docs/labelfix/spellcheck/witness.bin'
    new = 'docs/records/labelfix/spellcheck/witness.bin'
    mirror = external / old
    mirror.parent.mkdir(parents=True)
    mirror.write_bytes(b'historical data')
    assert data_root.resolve(new) == mirror
    local = repo / new
    local.parent.mkdir(parents=True)
    local.write_bytes(b'local data')
    assert data_root.resolve(old) == local
    assert data_root.resolve(new) == local
    assert data_root.input_path(repo / old) == local


def test_layout_missing_input_keeps_historical_custody_receipt(roots):
    repo, _ = roots
    shard = repo / data_root.RECEIPTS / 'receipt_02.tsv'
    shard.write_text('path\tbytes\tsha256\tproducing_commit\tkind\n'
                     'docs/labelfix/missing.bin\t3\tabc\t123\tother\n')
    data_root._receipt_paths.cache_clear()
    with pytest.raises(FileNotFoundError, match='receipt_02.tsv') as error:
        data_root.resolve('docs/records/labelfix/missing.bin')
    assert 'docs/records/labelfix/missing.bin' in str(error.value)


@pytest.mark.parametrize('old,new', EXTRA_MOVES, ids=[old for old, _ in EXTRA_MOVES])
def test_second_layout_local_mirror_and_custody(roots, old, new):
    repo, external = roots
    if not Path(old).suffix:
        old += '/witness.bin'
        new += '/witness.bin'
    mirror = external / old
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_bytes(b'historical mirror')
    local = repo / new
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_bytes(b'relocated local')
    assert data_root.resolve(old) == local
    assert data_root.input_path(repo / old) == local
    local.unlink()
    assert data_root.resolve(new) == mirror
    mirror.unlink()
    (repo / data_root.RECEIPTS / 'receipt_02.tsv').write_text(
        'path\tbytes\tsha256\tproducing_commit\tkind\n'
        f'{old}\t17\tabc\t123\tother\n')
    data_root._receipt_paths.cache_clear()
    with pytest.raises(FileNotFoundError, match='receipt_02.tsv'):
        data_root.resolve(new)
