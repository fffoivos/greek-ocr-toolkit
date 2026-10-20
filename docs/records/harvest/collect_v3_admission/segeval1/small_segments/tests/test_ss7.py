"""SS7 boundary, published-artifact and fail-closed refresh checks; no crop access."""
from pathlib import Path
from collections import Counter
import gzip
import io
import json
import os
import subprocess
import sys
import tempfile

import pytest

sys.dont_write_bytecode = True
SS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SS / 'tools'))
import ss7_key as key
import ss7_owner_marks as marks

DUMP = SS / 'sheet/marks_dump/20261019T1827'


@pytest.fixture(scope='module')
def population():
    with gzip.open(SS / 'small_population_key.jsonl.gz', 'rt', encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]


@pytest.fixture
def scratch():
    with tempfile.TemporaryDirectory(prefix='.ss7_test_', dir=SS / 'tools') as directory:
        yield Path(directory)


def sample(**overrides):
    row = dict(row_id='example--0123456789abcdef--s000-l0001', characters=8,
               text_characters=99, width_px=60, height_px=10,
               raw_text='123', is_numeric_output=True, source='example',
               primary_class='numerics_tables', script_class='nonletter',
               wave='W1', verdict_05='KEEP', reason_05='', crop_sha256='a' * 64)
    row.update(overrides)
    return row


@pytest.mark.parametrize('chars,width,height,inside', [
    (8, 60, 10, True), (9, 60, 10, False),
    (8, 60.001, 10, False), (8, 10, 60, True),
    (8, 10, 60.001, False), (9, 10, 60, False),
])
def test_definition_boundary(chars, width, height, inside):
    result = key.key_row(sample(characters=chars, width_px=width, height_px=height))
    assert (result is not None) == inside
    if inside:
        assert result['A'] == 6.0
        assert result['L'] == 60 and result['S'] == 10
        assert result['rotated'] == (height > width)
        assert result['chars'] == 8 and result['text_characters'] == 99


def test_ss1_helper_reuse():
    import ss1_q1
    for name in ('output_type', 'rotation', 'wave_group', 'reason_category'):
        assert getattr(key, name) is getattr(ss1_q1, name)


def test_counts_reconcile_ss1(population):
    assert len(population) == 59002
    assert Counter(r['output_type'] for r in population) == key.EXPECTED
    assert key.reconcile(population, 592466)['ss1_reconciled']


def test_reconciliation_refuses_mismatch(population):
    with pytest.raises(ValueError, match='reconciliation mismatch'):
        key.reconcile(population[:-1], 592466)


def test_sorted_unique_book_and_geometry(population):
    ids = [r['row_id'] for r in population]
    assert ids == sorted(set(ids))
    for row in population:
        assert row['book'] == '--'.join(row['row_id'].split('--')[:2])
        assert row['book'].split('--')[0] == row['source']
        assert len(row['book'].split('--')[1]) == 16
        assert row['chars'] <= 8
        assert row['L'] / row['S'] <= 6
        assert row['L'] == max(row['width_px'], row['height_px'])
        assert row['S'] == min(row['width_px'], row['height_px'])
        assert row['A'] == round(row['L'] / row['S'], 4)
        assert row['rotated'] == (row['height_px'] > row['width_px'])


def test_exact_census_membership_and_carried_fields(population):
    actual = {r['row_id']: r for r in population}
    matched, total = 0, 0
    with gzip.open(key.CENSUS, 'rt', encoding='utf-8') as stream:
        for line in stream:
            total += 1
            row = json.loads(line)
            inside = row['characters'] <= 8 and max(row['width_px'], row['height_px']) / min(row['width_px'], row['height_px']) <= 6
            assert (row['row_id'] in actual) == inside
            if inside:
                result = actual[row['row_id']]
                for field in ('row_id', 'text_characters', 'width_px', 'height_px', 'source',
                              'primary_class', 'script_class', 'wave', 'verdict_05', 'crop_sha256'):
                    assert result[field] == row[field]
                assert result['chars'] == row['characters']
                assert result['output_type'] == key.output_type(row['raw_text'], row['is_numeric_output'])
                assert result['reason_category'] == key.reason_category(row['verdict_05'], row['reason_05'])
                matched += 1
    assert total == 592466 and matched == len(population)


def test_deterministic_gzip_bytes(population):
    first, second = io.BytesIO(), io.BytesIO()
    key.write_gzip(population, first)
    key.write_gzip(population, second)
    expected = (SS / 'small_population_key.jsonl.gz').read_bytes()
    assert first.getvalue() == second.getvalue() == expected
    assert expected[4:8] == b'\x00' * 4
    assert expected[3] & 8 == 0  # no destination filename in the header


def test_real_dump_and_reference_key_order():
    reference = [json.loads(line) for line in (SS.parent / 'owner_marks_20261019.jsonl').read_text().splitlines()]
    rows = marks.collect_marks(DUMP)
    assert len(json.loads(marks.MANIFEST.read_text())) == 417
    assert len(list((DUMP / 'notes').glob('*.json'))) == len(rows) == 185
    assert Counter(r['owner_mark'] for r in rows) == {'KEEP': 177, 'DROP': 8}
    assert all(list(row) == list(reference[0]) for row in reference + rows)
    assert [r['line_id'] for r in rows] == sorted({r['line_id'] for r in rows})
    for row in rows:
        original = json.loads((DUMP / 'notes' / ('smallseg:' + row['line_id'] + '.json')).read_text())
        assert row['sheet'] == marks.SHEET
        assert row['owner_mark'] == original['verdict']
        assert row['note'] == original['note'] and row['updated'] == original['updated']
    assert (SS / 'owner_marks_smallseg.jsonl').read_text(encoding='utf-8') == ''.join(
        json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    assert marks.collect_marks(DUMP / 'notes') == rows


@pytest.mark.parametrize('case,message', [
    ('filename', 'filename doc_id mismatch'), ('unknown', 'not a manifest card'),
    ('verdict', 'invalid verdict'), ('duplicate', 'duplicate line_id'),
])
@pytest.mark.parametrize('existing', [False, True])
def test_refusals_no_output_written(scratch, case, message, existing):
    notes = scratch / 'notes'
    notes.mkdir()
    line_id = sorted(r['line_id'] for r in json.loads(marks.MANIFEST.read_text()))[0]
    mark = dict(line_id=line_id, verdict='KEEP', note='δοκιμή', updated='2026-10-19 18:21')
    filename = 'smallseg:' + line_id + '.json'
    if case == 'filename':
        filename = 'wrong.json'
    elif case == 'unknown':
        mark['line_id'] = 'unknown'
        filename = 'smallseg:unknown.json'
    elif case == 'verdict':
        mark['verdict'] = 'UNCERTAIN'
    (notes / filename).write_text(json.dumps(mark), encoding='utf-8')
    if case == 'duplicate':
        (notes / 'zz_duplicate.json').write_text(json.dumps(mark), encoding='utf-8')
    out = scratch / 'out.jsonl'
    if existing:
        out.write_bytes(b'existing output\n')
    result = subprocess.run([sys.executable, '-B', str(SS / 'tools/ss7_owner_marks.py'),
                             str(scratch), str(out)], capture_output=True, text=True,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    assert result.returncode != 0
    assert message in result.stderr
    assert out.read_bytes() == b'existing output\n' if existing else not out.exists()


def test_marks_cli_sort_utf8_and_repeat(scratch):
    notes = scratch / 'notes'
    notes.mkdir()
    ids = sorted(r['line_id'] for r in json.loads(marks.MANIFEST.read_text()))[:2]
    for line_id in reversed(ids):
        mark = dict(line_id=line_id, verdict='KEEP', note='ελληνική σημείωση', updated='unchanged')
        (notes / ('smallseg:' + line_id + '.json')).write_text(json.dumps(mark), encoding='utf-8')
    out = scratch / 'out.jsonl'
    command = [sys.executable, '-B', str(SS / 'tools/ss7_owner_marks.py'), str(scratch), str(out)]
    first = subprocess.run(command, capture_output=True, text=True)
    assert first.returncode == 0 and 'KEEP 2 / DROP 0' in first.stdout
    payload = out.read_bytes()
    assert 'ελληνική σημείωση'.encode('utf-8') in payload
    assert [r['line_id'] for r in map(json.loads, payload.decode().splitlines())] == ids
    assert subprocess.run(command, capture_output=True).returncode == 0
    assert out.read_bytes() == payload
