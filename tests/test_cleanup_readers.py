"""Relocation regressions: external bytes, local metadata, explicit siblings."""
import gzip
import hashlib
import json
from pathlib import Path

import pytest

from greekocr.ops import data_root


@pytest.fixture
def relocated_roots(tmp_path, monkeypatch):
    repo, external = tmp_path / 'repo', tmp_path / 'data'
    repo.mkdir(); external.mkdir()
    monkeypatch.setattr(data_root, 'REPO_ROOT', repo)
    monkeypatch.setenv('GREEK_OCR_DATA_ROOT', str(external))
    monkeypatch.chdir(repo)
    return repo, external


def put(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))
    return path


def test_sf7_audit_reads_and_hashes_external_inputs(relocated_roots, monkeypatch):
    from scripts.labelfix import sf7_measure as sf7
    repo, external = relocated_roots
    old = external / 'docs/labelfix/spellcheck/S8_DEV'
    ids = [str(i) for i in range(100)]
    inventory = put(old / 'private/audit100/line_inventory.json',
                    [dict(line_id=i, original_label='α', wave='tiny') for i in ids])
    overlays = old / 'private/audit100/selected_overlays.json.gz'
    with gzip.open(overlays, 'wt') as stream:
        json.dump(dict(records=[dict(line_id=i, status='unchanged', label='α') for i in ids]), stream)
    truth = put(old / 'audit100_private/audit100_final.json', {i: dict(ok=True) for i in ids})
    monkeypatch.setattr(sf7, 'runtime_from_overlay', lambda o: {})
    monkeypatch.setattr(sf7, 'sf6_overlay', lambda *a: dict(status='unchanged', label='α'))
    rows, hashes = sf7.audit_inputs()
    assert len(rows) == 100
    for path in (inventory, overlays, truth):
        logical = 'docs/records/labelfix/spellcheck/S8_DEV/' + path.relative_to(old).as_posix()
        assert hashes[logical] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert not (repo / logical).exists()


@pytest.mark.parametrize('wave', ['round1', 'round2'])
def test_collection_wave_resolves_each_external_file(relocated_roots, wave):
    from greekocr.harvest.collection import read_wave
    repo, external = relocated_roots
    # The directory/summary remain local while admitted and other inputs moved.
    local = repo / 'docs/records/harvest' / wave
    put(local / 'admission_summary.json', dict(admitted=1, rejected=0, per_reason={}))
    old = external / 'docs/harvest' / wave
    put(old / 'admitted.jsonl', dict(id='tiny'))
    (old / 'rejected.jsonl').write_text('')
    put(old / 'holdout_books.json', ['heldout'])
    (old / 'READS.md').write_text('external report')
    result = read_wave(repo, wave)
    assert result['status'] == 'delivered'
    assert result['rows'] == [dict(id='tiny')]
    assert result['holdouts'] == ['heldout']
    assert result['reports']['READS.md'] == 'external report'


@pytest.mark.parametrize('wave,records_name', [('round1', 'records_all.jsonl'), ('round2', 'records.jsonl')])
def test_r2_v2_metadata_keeps_explicit_sibling_checkout(relocated_roots, monkeypatch, wave, records_name):
    from scripts.labelfix import r2_cards_prepare as prep
    repo, external = relocated_roots
    sibling = repo.parent / 'sibling'
    monkeypatch.setattr(prep, 'HARVEST', sibling)
    old = sibling / 'docs/harvest' / wave
    put(old / 'admitted.jsonl', dict(id='tiny', source='admission'))
    put(old / records_name, dict(id='tiny', source='record'))
    admits, records = prep.v2_metadata([dict(id='tiny', wave=wave, pool='v2')])
    assert admits['tiny']['source'] == 'admission'
    assert records['tiny']['source'] == 'record'


def test_r2_bound_rows_read_the_same_external_bytes_they_hash(relocated_roots):
    from scripts.labelfix import r2_cards_prepare as prep
    repo, external = relocated_roots
    source = put(external / 'docs/labelfix/tiny.jsonl', dict(id='tiny'))
    logical = repo / 'docs/records/labelfix/tiny.jsonl'
    assert prep.rows(logical) == [dict(id='tiny')]
    assert prep.INPUTS[str(logical)] == hashlib.sha256(source.read_bytes()).hexdigest()


def test_c1_and_n1_hash_and_rows_use_external_inputs(relocated_roots, monkeypatch):
    from tests._paths import ROOT
    monkeypatch.syspath_prepend(str(ROOT / 'scripts/numerics'))
    from scripts.labelfix.clariden.c1_common import sha256
    from scripts.numerics.n1t_packs import rows, sha
    repo, external = relocated_roots
    source = put(external / 'docs/labelfix/tiny.jsonl', dict(id='tiny'))
    logical = repo / 'docs/records/labelfix/tiny.jsonl'
    assert rows(logical) == [dict(id='tiny')]
    assert sha(logical) == sha256(logical) == hashlib.sha256(source.read_bytes()).hexdigest()


def test_frozen_document_reader_resolves_input_without_rewriting_output(relocated_roots, tmp_path):
    import importlib.machinery
    from tests._paths import ROOT
    repo, external = relocated_roots
    source = put(external / 'docs/labelfix/tiny.json', dict(id='tiny'))
    output = tmp_path / 'output.txt'
    fixture_path = str(ROOT / 'docs/records/_synthetic_reader.py')
    loader = importlib.machinery.SourceFileLoader('synthetic_reader', fixture_path)
    code = loader.source_to_code(
        f"from pathlib import Path\np = Path('docs/labelfix/tiny.json')\n"
        f"value = p.read_text()\nPath({str(output)!r}).write_text(value)\n".encode(), fixture_path)
    namespace = {}
    exec(code, namespace)
    assert namespace['value'] == source.read_text() == output.read_text()
    assert not (repo / 'docs/records/labelfix/tiny.json').exists()


def test_frozen_document_adapter_preserves_sibling_layout(tmp_path):
    import importlib.machinery
    from tests._paths import ROOT
    sibling = tmp_path / 'sibling'
    source = put(sibling / 'docs/labelfix/tiny.json', dict(id='sibling'))
    fixture_path = str(ROOT / 'docs/records/_synthetic_sibling.py')
    loader = importlib.machinery.SourceFileLoader('synthetic_sibling', fixture_path)
    code = loader.source_to_code(
        (f"from pathlib import Path\nCOLLECTOR = Path({str(sibling)!r})\n"
         "p = COLLECTOR / 'docs/labelfix/tiny.json'\nvalue = p.read_bytes()\n").encode(), fixture_path)
    namespace = {}
    exec(code, namespace)
    assert namespace['p'] == source
    assert namespace['value'] == source.read_bytes()
