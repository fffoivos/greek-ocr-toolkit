"""Pure classifier grammar and frozen owner-evaluation witnesses."""
import json
from pathlib import Path
from tests._paths import ADMISSION

import pytest

from greekocr.harvest.numeric_cells import _numeric_reason, classify_cell

D = ADMISSION / 'segeval1/cells'


@pytest.mark.parametrize('text', [
    '29)', '3.237.787', '270', 'ΙΙ', 'II', 'Ⅻ', 'iv', '(XIV)',
    '  -12,30 % ', '§ 42', '№ 2', '1 / 2', '1:02', "12'34′",
    '１２３', '١٢٣', '12€', '−12', '6 10 6', '+1–2—3',
])
def test_numeric_grammar(text):
    assert _numeric_reason(text) is not None


@pytest.mark.parametrize('text', [
    '', ' ', '---', '%', '§', '№', '123abc', '123ΙΙ', '2kg', '12a',
    '*Vid. Luc.', 'ἐᾶν, 95', 'ΑΘΗΝΑ', 'ΠΑΓΙΟ', 'προηγουμ. χρήσης',
    'Скрирания', 'I am', 'IIII', 'IC', 'ΙΧ', '12 €', '1€', '12²',
])
def test_non_numeric_grammar(text):
    assert _numeric_reason(text) is None


FIXTURES = json.loads((D / 'evaluation_fixtures.json').read_text())
FALSE_REJECT_CELL_IDS = {
    'gazette_modern--d4e7c0bb57264e92--s000-l0030',
    'gazette_modern--f4a16fe9302ade1e--s000-l0180',
    'elstat--24e6586813212fd1--s001-l0357',
    'elstat--d8fe6ab28d6113ba--s000-l0097',
    'gazette_modern--c4919950cda5532e--s000-l0030',
}


@pytest.mark.parametrize('row', FIXTURES['false_rejects'], ids=lambda r: r['row_id'])
def test_all_18_actual_false_rejects(row):
    result = classify_cell(row['text'], row['width_px'], row['height_px'])
    assert result['is_cell'] == (row['row_id'] in FALSE_REJECT_CELL_IDS)


@pytest.mark.parametrize('row', FIXTURES['ordinary'], ids=lambda r: r['row_id'])
def test_20_ordinary_evaluation_lines_are_not_cells(row):
    result = classify_cell(row['text'], row['width_px'], row['height_px'])
    assert not result['is_cell'] and not result['is_numeric_output']


@pytest.mark.parametrize('row', FIXTURES['numeric_evaluation'], ids=lambda r: r['row_id'])
def test_all_17_numeric_evaluation_outputs(row):
    result = classify_cell(row['text'], row['width_px'], row['height_px'])
    assert result['is_numeric_output']
    # Saved "330" is 46 px high; "6 10 6" is 60 px high. Both exceed 40.
    assert result['is_cell'] == (row['row_id'] not in {
        'gazette_modern--db904b88276128c8--s000-l0044',
        'ia_poly1850--8b16b26eee5a53a8--s021-l0001',
    })


@pytest.mark.parametrize('text,w,h,expected', [
    ('1234567890', 200, 40, True),
    ('1234567890', 201, 40, False),
    ('1234567890', 200, 41, False),
    ('12345678901', 200, 40, False),
    ('12345 67890', 200, 40, True),
    ('ΙΙ', 30, 20, True),
    ('12abc', 30, 20, False),
    ('', 30, 20, False),
])
def test_conjunction_and_inclusive_boundaries(text, w, h, expected):
    result = classify_cell(text, w, h)
    assert set(result) == {'is_numeric_output', 'is_small_image', 'is_cell', 'reasons'}
    assert result['is_cell'] == expected
    assert result['is_cell'] == (result['is_numeric_output'] and result['is_small_image'])


@pytest.mark.parametrize('w,h', [(None, 20), (20, None), (0, 20), (20, -1),
                                 (float('nan'), 20), (20, float('inf')), ('20', 20), (True, 20)])
def test_missing_or_invalid_dimensions(w, h):
    result = classify_cell('123', w, h)
    assert result['is_numeric_output'] and not result['is_small_image'] and not result['is_cell']
    assert 'image_dimensions:missing_or_invalid' in result['reasons']


@pytest.mark.parametrize('xh', [None, 1, 20, 1000, 0, -1, float('nan')])
def test_xheight_does_not_change_classification(xh):
    assert classify_cell('3.237.787', 190, 20, xh) == classify_cell('3.237.787', 190, 20)
