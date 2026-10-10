"""Public option combinations, serialization and shared Docling contracts."""
from dataclasses import replace
from pathlib import Path
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytest

from greekocr.pages import PageOptions, OutputOptions, process_page, process_book
from greekocr.pages.lines import segment_page
from greekocr.pages.tables import prepare_delivery
from greekocr.pages.statistics import page_statistics, book_statistics
from greekocr.pages.structure import delivery_records

FONT = Path(__file__).parents[1] / 'fixtures/fonts/GFSDidot-Regular.ttf'


@pytest.fixture(scope='module')
def page():
    image = Image.new('RGB', (450, 170), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(FONT), 24)
    for y in (20, 65, 110):
        draw.text((20, y), 'λόγος καὶ γραφή', fill='black', font=font)
    return image


@pytest.mark.parametrize('tables', [False, True])
@pytest.mark.parametrize('statistics', [False, True])
@pytest.mark.parametrize('granularity', [None, 'default', 'rows', 'pieces'])
def test_options_compose_exact_existing_stages(page, tables, statistics, granularity):
    options = PageOptions(tables=tables, statistics=statistics, join_lines=granularity is not None,
                          granularity=granularity or 'default')
    regions = [('table', (0, 10, 440, 160))] if tables else None
    actual = process_page(page, options=options, page_key='sample', table_regions=regions)
    expected, pieces, _ = prepare_delivery(page, segment_page(page), regions or [], supplement=tables)
    lines = [line.to_record() for line in expected.lines]
    assert actual.lines == lines
    assert actual.structure == expected.structure
    assert actual.to_records()['cells']['cells'] == [p.to_record(i, page.size, page.size) for i,p in enumerate(pieces)]
    delivered = delivery_records(lines, structure=expected.structure, granularity=granularity) if granularity else [l for l in lines if l['discounted'] is None]
    assert actual.delivery == delivered
    assert actual.statistics == (page_statistics(page, lines, page_key='sample', structure=expected.structure) if statistics else None)


def test_drop_remaps_addresses_and_neighbours(page):
    regions = [('table', (0, 10, 440, 160))]
    kept = process_page(page, options=PageOptions(tables=True), table_regions=regions)
    assert any(line['discounted'] is not None for line in kept.lines)
    result = process_page(page, options=PageOptions(tables=True, discounted='drop', statistics=True), table_regions=regions)
    assert all(line['discounted'] is None for line in result.lines)
    assert [l['row_id'] for l in result.lines] == [l['row_id'] for l in kept.lines if l['discounted'] is None]
    for piece in result.pieces:
        assert result.lines[piece.line_index]['row_id'] == piece.address['row_id']
    for group in result.columns + result.blocks + result.rows:
        assert all(0 <= i < len(result.lines) for i in group['line_indices'])
    for glyph in result.glyphs:
        assert glyph['line_index'] is None or 0 <= glyph['line_index'] < len(result.lines)


def test_book_statistics_match_q2_without_mutating_pages(page):
    options = PageOptions(statistics=True)
    pages = [process_page(page, page_key=f'p{i}', book_id='book', options=options) for i in range(2)]
    expected = book_statistics([p.statistics for p in pages], book_id='book')
    book = process_book(pages, book_id='book', options=options)
    assert book.statistics == expected['stats']
    assert [p.statistics for p in book.pages] == expected['pages']
    assert 'book_reference' not in pages[0].statistics['stats']
    with pytest.raises(ValueError, match='Duplicate'):
        process_book([pages[0], pages[0]], book_id='book', options=options)


@pytest.mark.parametrize('discounted', [None, 'diagnostic'])
def test_invalid_ribbons_are_retained_unless_strict_active_geometry(page, monkeypatch, discounted):
    from copy import deepcopy
    from greekocr.pages import api
    segmentation = segment_page(page)
    line = next(line for line in segmentation.lines if line.discounted is None)
    line.bottom[0] = line.top[0]
    line.discounted = discounted
    monkeypatch.setattr(api.detector, 'segment_page', lambda image: deepcopy(segmentation))
    result = process_page(page)
    assert any(np.any(line.bottom <= line.top) for line in result.segmentation.lines)
    if discounted is None:
        with pytest.raises(ValueError, match='invalid_line_geometry'):
            process_page(page, options=PageOptions(strict_geometry=True))
    else:
        process_page(page, options=PageOptions(strict_geometry=True))


def test_selected_files_and_parquet_readback(page, tmp_path):
    files = frozenset({'lines', 'cells', 'structure', 'statistics', 'structure_image'})
    result = process_page(page, page_key='sample', options=PageOptions(statistics=True, outputs=OutputOptions(tmp_path, files)))
    assert {p.name for p in tmp_path.iterdir()} == {'sample.lines.json', 'sample.cells.json', 'sample.structure.json', 'sample.stats.json', 'sample.glyphs.parquet', 'sample.structure.jpg'}
    assert json.loads((tmp_path/'sample.lines.json').read_text()) == result.lines
    import pyarrow.parquet as pq
    assert pq.read_table(tmp_path/'sample.glyphs.parquet').num_rows == len(result.glyphs)
    with Image.open(tmp_path/'sample.structure.jpg') as image:
        assert image.size == page.size


def test_layout_provider_called_only_when_enabled(page):
    calls = []
    def provider(image):
        calls.append(image.size)
        return []
    process_page(page, options=PageOptions(tables=True), layout_provider=provider)
    assert calls == [page.size]
    with pytest.raises(ValueError, match='Layout input'):
        process_page(page, layout_provider=provider)


def test_cli_directory_and_plugin_mapping(page, tmp_path, capsys):
    from greekocr.cli import main
    inputs = tmp_path/'inputs';inputs.mkdir();page.save(inputs/'sample.png')
    out = tmp_path/'out'
    assert main(['pages',str(inputs),'--out',str(out),'--statistics','--book-id','book','--outputs','lines','statistics']) == 0
    assert json.loads(capsys.readouterr().out)['pages'] == 1
    assert (out/'books/book.stats.json').exists()
    from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
    options = GlossapiOcrOptions(checkpoint=Path('model.pt'),codec=Path('codec.json'),replace_policy='all',
                                recognition_mode='oriented',tables=False,statistics=True,join_lines=True,granularity='pieces')
    assert options.page_options() == PageOptions(orientation=True,statistics=True,join_lines=True,granularity='pieces')
    assert options.model_copy(update={'recognition_mode': 'detector'}).page_options().strict_geometry


def test_parked_orientation_is_opt_in_and_does_not_replace_original_geometry(page):
    normal = process_page(page)
    oriented = process_page(page, options=PageOptions(orientation=True))
    assert normal.orientation is None
    assert oriented.orientation is not None
    assert normal.lines == oriented.lines
    assert oriented.orientation.words


@pytest.mark.parametrize('kwargs', [dict(granularity='rows'),dict(discounted='hide'),dict(granularity='unknown',join_lines=True)])
def test_invalid_options_rejected(kwargs):
    with pytest.raises(ValueError):PageOptions(**kwargs)


def test_empty_page_and_normalized_numpy_image():
    result = process_page(np.ones((60, 80)), options=PageOptions(statistics=True))
    assert not result.lines and not result.pieces and not result.glyphs
    assert result.image_size == (80, 60)
    assert result.statistics['stats']['summary']['letter_bodies'] == 0


def test_review_image_preserves_normalized_numpy_color(tmp_path):
    image = np.zeros((60, 80, 3), dtype=float)
    image[:] = (1., .25, .25)
    result = process_page(image, options=PageOptions(outputs=OutputOptions(tmp_path, {'lines_image'})))
    with Image.open(result.files['lines_image']) as rendered:
        red, green, blue = np.asarray(rendered)[30, 40].astype(int)
    assert red - green > 100 and red - blue > 100


def test_book_does_not_write_null_rows_for_preexisting_unjoined_results(page, tmp_path):
    original = process_page(page, page_key='p0', book_id='book')
    options = PageOptions(join_lines=True, granularity='rows', outputs=OutputOptions(tmp_path, {'rows'}))
    with pytest.raises(ValueError, match='existing result joined at rows'):
        process_book([original], book_id='book', options=options)
    assert not (tmp_path/'p0.rows.json').exists()
