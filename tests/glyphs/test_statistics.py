"""Q2: immutable geometry, independent photometry, grouping and book isolation."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw
import pytest

from greekocr.glyphs.statistics import (
    page_statistics, book_statistics, corpus_statistics, write_statistics,
    render_glyph_statistics, render_book_statistics, _measure, _provenance,
)


def fixture(scale=1, ink=20, color=False):
    im = Image.new('RGB' if color else 'L', (360, 150), 'white' if color else 245)
    d = ImageDraw.Draw(im)
    for i in range(10):
        x = 25+i*28
        d.rectangle((x, 55, x+13, 74), fill=(ink,)*3 if color else ink)
        d.rectangle((x+4, 59, x+9, 70), fill=(245,)*3 if color else 245)
    d.rectangle((29, 48, 33, 50), fill=(ink,)*3 if color else ink)
    line = dict(x0=15, x1=320, xheight=20., page_side='single', column_id='single:column-0000',
                row_id='row-00000', block_id='block', piece_index=0, discounted=None, support=10)
    for name, y in dict(baseline=75, meanline=55, font_top=45, font_bottom=85, top=40, bottom=90).items():
        line[name] = [float(y)]*305
    if scale != 1:
        im = im.resize((im.width*scale, im.height*scale), Image.Resampling.NEAREST)
        line = dict(line, x0=line['x0']*scale, x1=line['x1']*scale, xheight=20.*scale)
        for name in ('baseline', 'meanline', 'font_top', 'font_bottom', 'top', 'bottom'):
            line[name] = [line[name][0]*scale]*(305*scale)
    return im, [line]


def measured(key='test-p1', book='test', **kwargs):
    im, lines = fixture(**kwargs)
    return im, page_statistics(im, lines, page_key=key, book_id=book)


def test_q1_geometry_and_addresses_are_immutable_and_marks_attach_once():
    im, lines = fixture()
    before = deepcopy(lines)
    result = page_statistics(im, lines, page_key='a')
    assert lines == before
    bodies = [r for r in result['glyphs'] if r['entity_kind'] == 'letter_body']
    assert len(bodies) == 10
    assert sum(len(r['attached_marks']) for r in bodies) == 1
    assert bodies[0]['attached_marks'][0]['ink_class'] == 'mark_above'
    assert bodies[0]['height_xh'] > bodies[0]['body_height_xh']
    assert all((r['page_side'], r['column_id'], r['row_id'], r['line_index']) ==
               ('single', 'single:column-0000', 'row-00000', 0) for r in bodies)
    assert len({r['glyph_id'] for r in result['glyphs']}) == len(result['glyphs'])
    assert result['stats']['summary']['legacy_agreement']['fraction'] == 1
    assert result['stats']['summary']['coverage_shares']['intact'] == 1


def test_absolute_photometry_and_stroke_are_measured_not_labels():
    gray = np.full((100, 100), 240., float)
    gray[30:50, 30:50] = 60
    mask = np.ones((20, 20), bool)
    m = _measure(gray, None, [30, 30, 50, 50], mask, 20., 240.)
    assert m['ink_gray'] == 60
    assert m['darkness'] == pytest.approx(1-60/255)
    assert m['contrast_local'] == .75
    assert m['contrast_absolute'] == pytest.approx(180/255)
    assert m['edge_sharpness'] > 0
    assert m['color_spread'] is None
    assert m['hole_fraction'] == 0


def test_font_sizes_are_scale_normalized_and_unresolved_is_explicit():
    _, first = measured()
    _, large = measured(scale=2)
    a = first['stats']['font_groups'][0]['size_page_width']['median']
    b = large['stats']['font_groups'][0]['size_page_width']['median']
    assert a == b
    assert first['stats']['summary']['letter_bodies'] == large['stats']['summary']['letter_bodies']
    assert all('resolved' in r and 'merged' in r for r in first['glyphs'])


def test_residual_ink_is_not_assigned_a_q1_line_and_discounted_lines_never_drive_reference():
    im, lines = fixture()
    d = ImageDraw.Draw(im)
    d.rectangle((40, 113, 51, 131), fill=185)
    other = deepcopy(lines[0])
    for name in ('baseline', 'meanline', 'font_top', 'font_bottom', 'top', 'bottom'):
        other[name] = [y+58 for y in other[name]]
    other['discounted'] = 'faint'
    other['row_id'] = 'row-00001'
    result = page_statistics(im, lines+[other], page_key='residual')
    residual = [r for r in result['glyphs'] if r['box'][1] >= 100]
    assert residual
    assert all(r['row_id'] is None and r['line_index'] is None for r in residual)
    assert any(r['show_through_candidate'] for r in residual)
    assert result['stats']['discounted_lines'] == 1
    assert len(result['stats']['lines']) == 1
    assert len(result['stats']['rows']) == 1


def test_parquet_roundtrip_with_null_body_boxes(tmp_path):
    import pyarrow.parquet as pq
    im, lines = fixture()
    ImageDraw.Draw(im).rectangle((40, 113, 51, 131), fill=185)
    result = page_statistics(im, lines, page_key='nullboxes')
    paths = write_statistics(result, tmp_path)
    records = pq.read_table(paths['glyphs']).to_pylist()
    assert any(r['body_box'] is None for r in records)
    assert len(records) == len(result['glyphs'])


def test_color_stamp_and_blurred_showthrough_predicates_are_evidenced():
    _, result = measured()
    row = dict(result['glyphs'][0], line_index=None, entity_kind='residual_ink', height_xh=1., width_xh=.8,
               contrast_absolute=.1, edge_sharpness=.1, color_spread=.2)
    p = _provenance(row, dict(contrast_absolute=.8, edge_sharpness=2.))
    assert p['show_through_candidate'] and p['stamp_watermark_candidate']
    assert p['faint'] and p['blurred'] and p['colored'] and p['line_inconsistent']
    assert p['mirrored'] is None


def test_book_reference_excludes_self_and_does_not_mutate_pages():
    _, p1 = measured(key='a', ink=20)
    _, p2 = measured(key='b', ink=110)
    before = deepcopy(p1)
    book = book_statistics([p1, p2], book_id='test')
    assert p1 == before
    assert book['pages'][0]['stats']['book_reference']['pages'] == ['b']
    assert book['pages'][0]['stats']['book_reference']['contrast_absolute'] == p2['stats']['reference']['contrast_absolute']
    assert book['stats']['stability']['body_size_page_width']['cv'] == 0
    assert book['stats']['stability']['contrast']['cv'] > 0
    assert render_book_statistics(book['stats']).size == (1200, 980)
    single = book_statistics([p1], book_id='test')
    assert single['pages'][0]['stats']['book_reference']['support_pages'] == 0
    assert all(r['book_contrast_ratio'] is None for r in single['pages'][0]['glyphs'])
    assert single['stats']['stability']['contrast']['cv'] is None
    with pytest.raises(ValueError, match='Duplicate'):
        book_statistics([p1, p1], book_id='test')
    with pytest.raises(ValueError, match='identity'):
        book_statistics([p1], book_id='another')


def test_empty_page_has_null_statistics_and_no_divisions_by_zero(tmp_path):
    im = Image.new('L', (80, 90), 255)
    result = page_statistics(im, [], page_key='blank', book_id='b')
    assert result['glyphs'] == []
    assert result['stats']['summary']['readability_proxy'] is None
    assert result['stats']['summary']['coverage_shares']['intact'] is None
    assert result['stats']['reference']['support'] == 0
    paths = write_statistics(result, tmp_path)
    assert Path(paths['glyphs']).exists()
    json.dumps(result, allow_nan=False)
    book = book_statistics([result], book_id='b')
    assert book['stats']['summary']['readability_proxy'] is None


def test_parquet_and_jsonl_preserve_nested_evidence(tmp_path, monkeypatch):
    import pyarrow.parquet as pq
    im, result = measured()
    paths = write_statistics(result, tmp_path)
    records = pq.read_table(paths['glyphs']).to_pylist()
    assert len(records) == len(result['glyphs'])
    assert json.loads(records[0]['attached_marks']) == result['glyphs'][0]['attached_marks']
    assert records[0]['box'] == result['glyphs'][0]['box']
    assert render_glyph_statistics(im, result).height == im.height+38
    monkeypatch.setitem(sys.modules, 'pyarrow', None)
    paths = write_statistics(result, tmp_path/'fallback')
    assert paths['glyphs'].endswith('.jsonl')
    assert json.loads(Path(paths['glyphs']).read_text().splitlines()[0]) == result['glyphs'][0]


def test_corpus_readability_uses_declared_page_weighting():
    _, p1 = measured(key='a', ink=20)
    _, p2 = measured(key='b', ink=110)
    c = corpus_statistics([p1, p2])
    expected = np.mean([p['stats']['summary']['readability_proxy'] for p in (p1, p2)])
    assert c['readability_proxy'] == expected
    assert c['letter_bodies'] == 20
    assert 0 <= c['readability_proxy'] <= 100
    with pytest.raises(ValueError, match='Duplicate'):
        corpus_statistics([p1, p1])


def test_missing_q1_address_is_rejected():
    im, lines = fixture()
    del lines[0]['row_id']
    with pytest.raises(ValueError, match='row_id'):
        page_statistics(im, lines, page_key='missing')


def test_broken_merged_and_faint_letters_keep_crop_tool_evidence():
    im, lines = fixture()
    d = ImageDraw.Draw(im)
    d.rectangle((25, 63, 38, 65), fill=245)  # Break both sides of the first counter.
    d.rectangle((66, 64, 81, 66), fill=20)   # Join the second and third letters.
    d.rectangle((109, 55, 122, 74), fill=195)
    d.rectangle((113, 59, 118, 70), fill=245)
    result = page_statistics(im, lines, page_key='defects')
    bodies = [r for r in result['glyphs'] if r['entity_kind'] == 'letter_body']
    assert any(r['legacy_state'] == 'broken' and r['coverage_state'] == 'under_inked' and r['pieces'] > 1 for r in bodies)
    assert any(r['legacy_state'] == 'faint' and r['coverage_state'] == 'under_inked' and r['legacy_contrast_ratio'] < .5 for r in bodies)
    assert any(r['legacy_state'] == 'merged' and r['coverage_state'] == 'over_inked' and r['merged'] > 1 for r in bodies)


def test_empty_and_populated_parquet_have_identical_schema(tmp_path):
    import pyarrow.parquet as pq
    _, result = measured()
    full = write_statistics(result, tmp_path)
    blank = page_statistics(Image.new('L', (80, 90), 255), [], page_key='empty')
    empty = write_statistics(blank, tmp_path)
    assert pq.read_schema(full['glyphs']) == pq.read_schema(empty['glyphs'])


def test_adjacent_line_ownership_does_not_double_count_ink():
    im, lines = fixture()
    duplicate = deepcopy(lines[0])
    duplicate['row_id'] = 'row-duplicate'
    result = page_statistics(im, lines+[duplicate], page_key='overlap')
    assert result['stats']['summary']['letter_bodies'] == 10
    assert len(result['stats']['lines']) == 2
    assert result['stats']['lines'][1]['letter_bodies'] == 0


def test_column_residual_totals_are_spatial_evidence_not_addresses():
    im, lines = fixture()
    ImageDraw.Draw(im).rectangle((40, 113, 51, 131), fill=185)
    structure = dict(pages=[dict(page_side='single', polygon=[[0, 0], [360, 0], [360, 150], [0, 150]])],
                     columns=[dict(id='single:column-0000', page_side='single',
                                   left_boundary={'path': [[0, 0], [0, 150]]},
                                   right_boundary={'path': [[360, 0], [360, 150]]})])
    result = page_statistics(im, lines, page_key='spatial', structure=structure)
    residual = [r for r in result['glyphs'] if r['entity_kind'] == 'residual_ink']
    assert residual and all(r['column_id'] is None for r in residual)
    assert all(r['spatial_column_id'] == 'single:column-0000' for r in residual)
    column = result['stats']['columns'][0]
    assert column['nearby_unassigned_ink']['ink_pixels'] == sum(r['ink_pixels'] for r in residual)
    assert column['nearby_unassigned_ink']['candidates']['show_through_candidate']['rows'] > 0


def test_long_rules_inside_a_band_are_not_promoted_to_merged_letters():
    im, lines = fixture()
    draw = ImageDraw.Draw(im)
    draw.rectangle((160, 40, 330, 90), fill=245)
    draw.rectangle((170, 62, 315, 67), fill=20)
    result = page_statistics(im, lines, page_key='rule')
    assert not any(r['entity_kind'] == 'letter_body' and r['box'][0] >= 160 for r in result['glyphs'])
    rules = [r for r in result['glyphs'] if r['box'][0] >= 160]
    assert rules and any(r['rule_like'] and r['non_text'] for r in rules)
