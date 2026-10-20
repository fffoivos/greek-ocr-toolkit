"""T15 offline polygon mapping, harvest denominators and blinded artifact tests."""
import base64
import io
import json
import re

import numpy as np
from PIL import Image
import pytest

from greekocr.harvest.page_reads import (polygon_overlap, assign_page_lines,
    assign_page_symbols, page_summary, build_blind_review)
from greekocr.harvest.page_reads import _response_geometry


def target(ident='a', box=(0, 0, 100, 40)):
    x0, y0, x1, y1 = box
    return dict(id=ident, polygon=[[x0, y0], [x1, y0], [x1, y1], [x0, y1]])


def piece(text='άλφα', box=(0, 1, 90, 35)):
    return dict(text=text, bbox=list(box), confidence=.9)


@pytest.mark.parametrize('bottom,assigned', [(7, True), (6.999, False)])
def test_exact_seventy_percent_height(bottom, assigned):
    row = assign_page_lines([piece(box=(0, bottom - 10, 90, bottom))], [target()])['targets']['a']
    assert (not row['lost']) == assigned


@pytest.mark.parametrize('left,assigned', [(50, True), (50.001, False)])
def test_fifty_percent_shorter_width(left, assigned):
    row = assign_page_lines([piece(box=(left, 0, left + 100, 35))], [target()])['targets']['a']
    assert (not row['lost']) == assigned


def test_vertical_height_is_not_returned_area_fraction():
    # Width outside the target doesn't dilute height; shorter-width overlap=1.
    value = polygon_overlap([0, -3, 1000, 7], target()['polygon'])
    assert value['height_fraction'] == pytest.approx(.7)
    assert value['horizontal_fraction'] == 1
    assert not assign_page_lines([piece(box=(0, -3, 1000, 7))], [target()])['targets']['a']['lost']


def test_sloped_polygon_is_not_bounding_rectangle():
    poly = [[0, 0], [100, 100], [100, 120], [0, 20]]
    assert polygon_overlap([0, 95, 10, 110], poly)['height_fraction'] == 0
    value = polygon_overlap([80, 90, 100, 110], poly)
    assert value['height_fraction'] == pytest.approx(.75)
    assert not assign_page_lines([piece(box=(80, 90, 100, 110))], [dict(id='a', polygon=poly)])['targets']['a']['lost']


def test_sloped_band_uses_mean_height_not_midpoint_guess():
    poly = [[0, 0], [100, 100], [100, 120], [0, 20]]
    assert polygon_overlap([0, 50, 100, 70], poly)['height_fraction'] == pytest.approx(.2)


def test_edge_contact_not_merge():
    targets = [target(), target('b', (0, 40, 100, 80))]
    mapped = assign_page_lines([piece(box=(0, 0, 90, 40))], targets)
    assert not mapped['targets']['a']['merged']
    assert mapped['targets']['b']['lost']


def test_merge_even_if_one_target_meets_seventy_percent():
    mapped = assign_page_lines([piece(box=(0, 0, 90, 41))], [target(), target('b', (0, 40, 100, 80))])
    assert mapped['merged_box_count'] == 1
    assert all(t['merged'] and t['lost'] and t['rejected'] and not t['text'] for t in mapped['targets'].values())


def test_merge_with_horizontal_sliver_never_guessed():
    mapped = assign_page_lines([piece(box=(0, 0, 101, 35))], [target(), target('b', (100, 0, 200, 40))])
    assert mapped['merged_box_count'] == 1


def test_distinct_columns_at_same_height():
    mapped = assign_page_lines([piece(box=(110, 0, 190, 35))], [target(), target('b', (100, 0, 200, 40))])
    assert mapped['targets']['a']['lost']
    assert mapped['targets']['b']['text'] == 'άλφα'


def test_split_side_by_side_x_order():
    mapped = assign_page_lines([piece('βήτα', (50, 0, 90, 35)), piece('άλφα', (0, 1, 40, 36))], [target()])
    row = mapped['targets']['a']
    assert row['text'] == 'άλφα βήτα' and row['split'] and not row['rejected']
    assert 'horizontal_pieces_joined' in row['flags']


def test_stacked_split_rejected_and_lf_preserved():
    row = assign_page_lines([piece('βήτα', (0, 25, 90, 38)), piece('άλφα', (0, 0, 90, 15))], [target()])['targets']['a']
    assert row['split'] and row['rejected'] and row['text'] == 'άλφα\nβήτα'


def test_merged_split_flags_independent():
    targets = [target(), target('b', (0, 40, 100, 80))]
    pieces = [piece('άλφα', (0, 0, 40, 35)), piece('βήτα', (50, 0, 90, 35)), piece('γ', (0, 0, 90, 41))]
    row = assign_page_lines(pieces, targets)['targets']['a']
    assert row['merged'] and row['split'] and not row['lost'] and row['rejected']
    assert row['text'] == 'άλφα βήτα'


def test_symbol_assignment_uses_same_rule():
    symbols = [piece('α', (0, -3, 20, 7)), piece('β', (0, 0, 20, 41)), dict(text='γ', bbox=None, confidence=.8)]
    mapped = assign_page_symbols(symbols, [target(), target('b', (0, 40, 100, 80))])
    assert len(mapped['targets']['a']) == 1 and len(mapped['unassigned']) == 2
    assert mapped['symbols'][0]['target_id'] == 'a'


@pytest.mark.parametrize('box', [[0, 0, 0, 1], [0, 0, 1, 0], [200, 0, 300, 40]])
def test_zero_invalid_or_external_extent_is_lost(box):
    assert assign_page_lines([piece(box=box)], [target()])['targets']['a']['lost']


def test_invalid_geometry_and_duplicate_ids():
    with pytest.raises(ValueError):
        polygon_overlap([0, 0, float('nan'), 2], target()['polygon'])
    with pytest.raises(ValueError):
        polygon_overlap([0, 0, 2, 2], [[0, 0], [1, 1]])
    with pytest.raises(ValueError):
        assign_page_lines([], [target(), target()])


def metric_row(ident, engine, crop, page, rejected=False):
    return dict(id=ident, engine=engine, crop_text=crop, page_text=page, crop_status='ok', page_status='ok',
        crop_rejected=rejected, page_rejected=rejected, merged=False, lost=not page, split=False, rejected=rejected,
        identical=crop == page, letters_marks_identical=crop == page, nfd_edits=0 if crop == page else 1,
        crop_symbols=[dict(confidence=.8)], page_symbols=[dict(confidence=.9), dict(confidence=.7)])


def test_harvest_empty_and_rejected_pairs_do_not_agree():
    rows = [metric_row(ident, engine, text, text, rejected) for ident, text, rejected in
            [('valid', 'άλφα', False), ('empty', '', False), ('reject', 'βήτα', True)] for engine in ('vision', 'docai')]
    summary = page_summary(rows)
    assert summary['harvest']['page']['tier1_exact'] == 1
    assert summary['harvest']['page']['tier1_exact_pct'] == pytest.approx(100 / 3)
    assert summary['readers']['vision']['exact_pct'] == 100
    assert summary['readers']['vision']['page_mean_symbol_confidence'] == pytest.approx(.8)


def test_pilot_substitutions_reported_separately():
    rows = [metric_row('a', 'vision', 'καὶ', 'καὶ'), metric_row('a', 'docai', 'κὶ', 'κὶ')]
    h = page_summary(rows)['harvest']['page']
    assert h['tier1_exact'] == 0 and h['letters_agree'] == 0 and h['pilot_tier1'] == 1


def test_incomplete_or_duplicate_metric_pair_refused():
    r = metric_row('a', 'vision', 'a', 'a')
    with pytest.raises(ValueError):
        page_summary([r])
    with pytest.raises(ValueError):
        page_summary([r, r, metric_row('a', 'docai', 'a', 'a')])


def blind_fixture(tmp_path):
    path = tmp_path / 'crop.png'
    Image.new('L', (100, 20), 240).save(path)
    page = tmp_path / 'page.png'
    Image.new('L', (100, 1400), 220).save(page)
    rows, records = [], []
    for i in range(36):
        ident = f'line{i:02d}'
        records.append(dict(id=ident, page_id='p', straight_crop=str(path), bbox=[0, i * 30, 100, i * 30 + 20], gates=dict(column=0)))
        for engine in ('vision', 'docai'):
            changed = i < 12 and engine == 'vision' or 12 <= i < 24 and engine == 'docai' or i >= 24
            rows.append(metric_row(ident, engine, '<script>alert(1)</script>άλφα', 'βήτα' if changed else '<script>alert(1)</script>άλφα'))
    return rows, records, [dict(id='p', image=str(page))]


def test_blind_stratification_inlined_images_escaping_and_key_absence(tmp_path):
    rows, records, manifest = blind_fixture(tmp_path)
    page, key = build_blind_review(rows, records, manifest)
    assert len(key['cards']) == 30 and len({c['id'] for c in key['cards']}) == 30
    assert {s: sum(c['stratum'] == s for c in key['cards']) for s in key['candidates']} == dict(vision_only=10, docai_only=10, both=10)
    assert len(key['most_changed']) == 10
    assert len(re.findall('<article id=', page)) == 40
    assert page.count('data:image/png;base64,') == 50
    assert '<script>alert' not in page and '&lt;script&gt;' in page
    assert all(s not in page for s in ('blind_key', 'vision_only', 'docai_only', 'crop_text', 'page_text', 'line00'))
    for encoded in re.findall('data:image/png;base64,([A-Za-z0-9+/=]+)', page):
        with Image.open(io.BytesIO(base64.b64decode(encoded))) as image:
            assert image.format == 'PNG'


def test_blind_order_reproducible_and_independent(tmp_path):
    args = blind_fixture(tmp_path)
    first = build_blind_review(*args)
    assert first == build_blind_review(*args)
    orders = first[1]['cards']
    assert any(c['order']['vision'] != c['order']['docai'] for c in orders)
    assert {c['order']['vision']['A'] for c in orders} == {'crop', 'page'}
    assert first != build_blind_review(*args, seed=16)


def test_context_ranking_and_plus_minus_two_bounds(tmp_path):
    rows, records, manifest = blind_fixture(tmp_path)
    for row in rows:
        if row['id'] == 'line30':
            row['nfd_edits'] = 100
    _, key = build_blind_review(rows, records, manifest)
    top = key['most_changed'][0]
    assert top['id'] == 'line30' and top['nfd_edits'] == 200
    assert top['neighbor_ids'] == [f'line{i:02d}' for i in range(28, 33)]
    assert top['context_box'] == [0, 832, 100, 988]


def test_blind_insufficient_stratum_refused(tmp_path):
    rows, records, manifest = blind_fixture(tmp_path)
    rows = [r for r in rows if not r['id'].startswith('line0')]
    with pytest.raises(ValueError, match='fewer than 10'):
        build_blind_review(rows, records, manifest)


@pytest.mark.parametrize('matrix_type', [5, 6])
@pytest.mark.parametrize('normalized', [False, True])
def test_docai_recorded_transforms_inverse_actual_vertices(matrix_type, normalized):
    native = np.asarray([[10, 20, 1], [70, 25, 1], [70, 40, 1], [10, 35, 1]])
    first = np.asarray([[1., 0, 12], [0, 1, 18], [0, 0, 1]])
    second = np.asarray([[0., -1, 100], [1, 0, 0], [0, 0, 1]])
    points = (second @ first @ native.T).T
    poly = dict(normalizedVertices=[dict(x=v[0]/200, y=v[1]/150) for v in points]) if normalized else dict(vertices=[dict(x=v[0],y=v[1]) for v in points])
    dtype = '<f4' if matrix_type == 5 else '<f8'
    transforms = [dict(rows=2, cols=3, type=matrix_type, data=base64.b64encode(m[:2].astype(dtype).tobytes()).decode()) for m in (first, second)]
    layout = dict(boundingPoly=poly, textAnchor=dict(textSegments=[dict(endIndex=1)]), confidence=.9)
    raw = dict(document=dict(text='Α', pages=[dict(dimension=dict(width=200,height=150,unit='pixels'),
        transforms=transforms, lines=[dict(layout=layout)], symbols=[dict(layout=layout)])]))
    frozen = json.dumps(raw)
    geometry = _response_geometry('docai', raw, (100, 100))
    assert geometry['lines'][0]['bbox'] == pytest.approx([10, 20, 70, 40])
    assert geometry['symbols'][0]['bbox'] == pytest.approx([10, 20, 70, 40])
    assert geometry['coordinate_frame']['converted']
    assert geometry['lines'][0]['reported_bbox'] != geometry['lines'][0]['bbox']
    assert json.dumps(raw) == frozen


def test_docai_dimension_change_without_transform_fails_closed():
    raw = dict(document=dict(pages=[dict(dimension=dict(width=110,height=100))]))
    with pytest.raises(ValueError, match='without a recorded transform'):
        _response_geometry('docai', raw, (100,100))


@pytest.mark.parametrize('matrix', [[[0.,0,0],[0,0,0]], [[float('nan'),0,0],[0,1,0]]])
def test_docai_invalid_transform_refused(matrix):
    transform = dict(rows=2,cols=3,type=6,data=base64.b64encode(np.asarray(matrix,dtype='<f8').tobytes()).decode())
    raw = dict(document=dict(pages=[dict(dimension=dict(width=100,height=100),transforms=[transform])]))
    with pytest.raises(ValueError):
        _response_geometry('docai', raw, (100,100))


def test_docai_identity_frame_retains_normalized_only_geometry():
    raw = dict(document=dict(text='Α',pages=[dict(dimension=dict(width=100,height=100),lines=[dict(layout=dict(
        boundingPoly=dict(normalizedVertices=[dict(x=.1,y=.2),dict(x=.7,y=.2),dict(x=.7,y=.4),dict(x=.1,y=.4)]),
        textAnchor=dict(textSegments=[dict(endIndex=1)])))])]))
    geometry = _response_geometry('docai',raw,(100,100))
    assert geometry['lines'][0]['bbox'] == pytest.approx([10,20,70,40])
    assert not geometry['coordinate_frame']['converted']
