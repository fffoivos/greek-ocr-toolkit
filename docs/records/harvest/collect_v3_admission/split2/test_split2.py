"""Offline SPLIT2 contract and actual census load-through tests."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_split2 as b
import jsonschema
import pytest


@pytest.fixture(scope='module')
def data():
    return b.read_lines(b.HERE / 'row_split.jsonl.gz')


@pytest.fixture(scope='module')
def prepared():
    return b.prepare_data()


def test_schema_every_line(data):
    schema = json.loads((b.CENSUS / 'split_input.schema.json').read_text())
    validator = jsonschema.Draft202012Validator(schema)
    for row in data:
        validator.validate(row)
        assert set(row) == {'parent_id', 'row_id', 'edition_id', 'split', 'forced'}


def test_unique_and_sorted(data):
    keys = [(r['parent_id'], r['row_id']) for r in data]
    assert len(set(keys)) == len(keys)
    assert keys == sorted(keys)


def test_one_split_per_edition(data):
    editions = {}
    for r in data:
        assert editions.setdefault(r['edition_id'], r['split']) == r['split']
    assert len(editions) == 1359


def test_forced_test_and_edition_evidence(data, prepared):
    maps = b.read_lines(b.HERE / 'edition_map.jsonl')
    assert maps == prepared[1]
    forced = {e['edition_id'] for e in maps if e['forced']}
    assert len(forced) == 99
    forced_rows = [r for r in data if r['forced']]
    assert len(forced_rows) == 52468
    assert {r['edition_id'] for r in forced_rows} == forced
    assert all(r['split'] == 'test' for r in forced_rows)


def test_exact_split1_adoption_and_counts(data, prepared):
    expected_rows, maps, counts, inputs = prepared
    assert data == expected_rows
    for key, expected in b.EXPECTED.items():
        assert counts[key] == expected
    receipt = json.loads((b.HERE / 'receipt.json').read_text())
    assert receipt['counts'] == counts
    assert receipt['input_shas'] == inputs
    assert receipt['build_script_sha256'] == b.sha(b.HERE / 'build_split2.py')


def test_rebuild_byte_identical(tmp_path, prepared):
    rows, maps, _, _ = prepared
    hashes = b.write_data(tmp_path, rows, maps)
    for name in ('row_split.jsonl.gz', 'edition_map.jsonl'):
        assert (tmp_path / name).read_bytes() == (b.HERE / name).read_bytes()
    assert hashes == json.loads((b.HERE / 'receipt.json').read_text())['output']
    blob = (tmp_path / 'row_split.jsonl.gz').read_bytes()
    assert blob[3] == 0  # no optional fields, including filename
    assert blob[4:8] == bytes(4)  # mtime=0
    plain = gzip.decompress(blob)
    assert hashlib.sha256(plain).hexdigest() == hashes['uncompressed_sha256']
    assert plain == b''.join(b.encode(r) for r in rows)


def test_census_own_loader_every_row(data):
    result = b.consumer_check(b.HERE / 'row_split.jsonl.gz', data)
    assert result['unmapped_rows'] == [], result['unmapped_rows']
    assert result['resolved'] == result['allocation_rows'] == result['rows'] == 320479
    assert result == json.loads((b.HERE / 'receipt.json').read_text())['loader_check']


def test_census_missing_rows_remain_unassigned(data):
    # consumer_check imports exclusively from the read-only retained package.
    sys.path.insert(0, str(b.PACKAGE))
    from greekocr.harvest import line_pipeline_census04 as c4
    from greekocr.harvest.line_pipeline import canonical
    from greekocr.harvest import line_pipeline_sources as sources
    path = b.HERE / 'row_split.jsonl.gz'
    allocation = c4.load_split(dict(path=str(path), sha256=b.sha(path)))
    metadata = dict(row_splits={canonical(list(k)): v['split'] for k, v in allocation.items()})
    record = dict(id='split2-absent-row', page_id='bsb--later--s436', label='')
    parent = dict(id=data[0]['parent_id'], format='collect-v3-features')
    assert (parent['id'], record['id']) not in allocation
    assert sources.canonicalize(record, parent, metadata)['split'] == 'unassigned'


def test_census_rejects_wrong_compressed_hash():
    sys.path.insert(0, str(b.PACKAGE))
    from greekocr.harvest.line_pipeline_census04 import load_split
    with pytest.raises(ValueError, match='pinned input SHA mismatch'):
        load_split(dict(path=str(b.HERE / 'row_split.jsonl.gz'), sha256='0'*64))
