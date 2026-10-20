"""Offline approved raster layout, font fitting and rerunnable builder tests."""
import hashlib
import io
import json

import pytest
from PIL import Image, ImageDraw

from scripts.harvest.compile_page_reads import (render_page, relative_path, fit, font,
                                               compile_records, GREEN, RED, PAD, GAP)


def row(number=1, **changes):
    return dict(dict(id=f'page-l{number}', page_id='page', docai_index=number-1, line_number=number,
                     bbox=[60, 20*number, 260, 20*number+20], docai_text='λόγος',
                     counted=True, confidence=.95), **changes)


def test_native_canvas_margins_gap_and_rule():
    canvas, layout = render_page(Image.new('L', (300, 200), 220), [row()])
    assert canvas.size == (720, 280)
    assert layout['native_size'] == [300, 200]
    assert canvas.getpixel((0, 0)) == (255, 255, 255)
    assert canvas.getpixel((PAD, PAD)) == (220, 220, 220)
    assert canvas.getpixel((PAD+300+GAP//2, PAD+100)) == (200, 200, 200)
    assert canvas.getpixel((PAD+300+GAP, PAD)) == (255, 255, 255)


def test_green_box_and_red_tall_box_with_distinct_placement():
    rows = [row(i) for i in (1, 2, 3)] + [row(4, bbox=[60, 100, 260, 150])]
    canvas, layout = render_page(Image.new('L', (300, 200), 255), rows)
    assert canvas.getpixel((PAD+60, PAD+20)) == GREEN
    assert canvas.getpixel((PAD+60, PAD+100)) == RED
    assert layout['positions'][-1]['panel_xy'] == [60, 102]
    assert layout['positions'][-1]['tall']
    assert layout['positions'][0]['panel_xy'][1] == pytest.approx(17.65)


@pytest.mark.parametrize('confidence,low', [(.89, False), (.889, True), (0, True), (None, False)])
def test_low_confidence_uses_mean_and_handles_zero(confidence, low):
    _, layout = render_page(Image.new('L', (300, 200), 255), [row(confidence=confidence)])
    assert layout['positions'][0]['low_confidence'] is low


def test_page_type_is_discrete_quartile_and_overflow_shrinks_individually():
    rows = [row(i, bbox=[60, i*40, w, i*40+30], docai_text='λόγος λόγος λόγος λόγος')
            for i, w in enumerate((90, 180, 240, 290, 290, 290, 290, 290), 1)]
    _, layout = render_page(Image.new('L', (320, 400), 255), rows)
    positions = layout['positions']
    fits = sorted(p['fitted_size'] for p in positions)
    assert layout['page_font_size'] == fits[len(fits)//4]
    assert all(p['font_size'] == min(layout['page_font_size'], p['fitted_size']) for p in positions)
    assert positions[0]['font_size'] < layout['page_font_size']
    assert layout['page_font_size'] <= 30*.95


def test_font_floor_and_long_text_preserve_approved_overflow_limit():
    draw = ImageDraw.Draw(Image.new('RGB', (200, 100)))
    assert fit(draw, 'λόγος'*100, 10, 20) == 9
    _, layout = render_page(Image.new('L', (300, 200), 255), [row(bbox=[60,20,70,40], docai_text='λόγος'*100)])
    assert layout['positions'][0]['overflow_at_minimum']


def test_multiline_text_is_normalized_only_for_visual_panel():
    rows = [row(docai_text='  λόγος\n  δεύτερος  ')]
    _, layout = render_page(Image.new('L', (300, 200), 255), rows)
    assert layout['positions'][0]['text'] == 'λόγος δεύτερος'
    assert rows[0]['docai_text'] == '  λόγος\n  δεύτερος  '


def test_empty_page_still_compiles_to_native_canvas():
    canvas, layout = render_page(Image.new('L', (300, 200), 220), [])
    assert canvas.size == (720, 280)
    assert layout['positions'] == []


def test_rescue_naming_title40_and_page_number():
    page = dict(origin='rescue', decade=1870, year=1873, title='Λόγος / περί: "γλώσσης" '*5,
                key='abcdef123456', page=7)
    path = relative_path(page)
    assert path.parts[0] == '1870s'
    assert path.parts[1].startswith('RESCUED_1873_')
    assert path.name == 'p0007.jpg'
    assert len(path.parts[1]) <= len('RESCUED_1873_')+40+len('_abcdef')


def test_rerun_is_byte_identical_and_provider_order_is_preserved(tmp_path):
    image = tmp_path / 'page.png'
    Image.new('L', (300, 200), 220).save(image)
    page = dict(id='page', image=str(image), image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                origin='rescue', decade=1900, year=1901, title='Λόγος', key='abcdef', page=1)
    rows = [dict(row(2), image_sha256=page['image_sha256']), dict(row(1), image_sha256=page['image_sha256'])]
    records = tmp_path / 'records.jsonl'
    records.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
    first = compile_records(records, tmp_path / 'out', pages=[page])
    second = compile_records(records, tmp_path / 'out', pages=[page])
    assert first == second
    assert [r['line_number'] for r in first['pages'][0]['positions']] == [1, 2]
    jpeg = tmp_path / 'out' / relative_path(page)
    with Image.open(image) as im:
        canvas, _ = render_page(im, sorted(rows, key=lambda r: r['docai_index']))
    expected = io.BytesIO()
    canvas.save(expected, 'JPEG', quality=85)
    assert jpeg.read_bytes() == expected.getvalue()
