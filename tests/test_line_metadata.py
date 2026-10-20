"""Real strips, controlled measurements and end-to-end offline metadata contracts."""
from dataclasses import FrozenInstanceError, fields
import ast
import hashlib
import json
from pathlib import Path
from scripts.layout_paths import relocated
import subprocess
import sys
import unicodedata as ud

import numpy as np
from PIL import Image, ImageFilter
import pytest

from greekocr.annotate import (LineFeatures, annotate_records, distribution_report, font_estimate,
                              font_style, line_features, load_lexicon, sampling_weights,
                              script_class, source_metadata, stratum_counts, stratum_key,
                              train_font_classifier)
from greekocr.annotate.pipeline import NUMERIC, CATEGORICAL
from greekocr.cli import main

ROOT = Path(__file__).resolve().parents[1]
O4D = ROOT / 'tests/fixtures/o4d_lines'
REAL_LINES = json.loads((O4D / 'index.json').read_text())['lines']
SYNTH = ROOT / 'tests/data/t5_font'
MODEL = ROOT / 'greekocr/annotate/fixtures/font_fixture.json'


def blocks():
    raster = np.full((32, 80), 204, dtype=np.uint8)
    for x in range(8, 68, 10):
        raster[10:22, x:x+4] = 51
    return raster


@pytest.mark.parametrize('row', REAL_LINES, ids=lambda r: r['file'])
def test_all_44_real_lines_finite_deterministic_and_nonblank(row):
    with Image.open(O4D / row['file']) as image:
        feature = line_features(image, row['layer'])
        assert (feature.width_px, feature.height_px) == image.size
        assert feature == line_features(image, row['layer'])
    assert len(REAL_LINES) == 44
    assert .01 < feature.ink_coverage < .55
    assert 0 <= feature.background_level <= 1
    assert 0 < feature.contrast <= 1
    assert 0 <= feature.local_contrast_p10 <= feature.local_contrast_p90 <= 1
    assert 1 <= feature.stroke_width_px <= feature.height_px
    assert 1 <= feature.xheight_px <= feature.height_px
    assert 1 <= feature.capheight_ratio <= feature.height_px
    assert feature.blur >= 0 and feature.noise >= 0
    assert feature.n_chars == len(ud.normalize('NFC', row['layer']))
    assert feature.n_words > 0 and feature.script_class == script_class(row['layer'])
    assert feature.lexicon_validity is None and feature.curl_px is None
    assert feature.font is None and feature.severity is None and feature.applied_ops is None
    json.dumps(feature.to_dict(), allow_nan=False)
    with pytest.raises(FrozenInstanceError):
        feature.noise = 1


def test_known_pixel_units_and_inversion():
    array = blocks()
    f = line_features(array)
    inverse = line_features(255 - array)
    assert f.ink_coverage == pytest.approx(6 * 12 * 4 / array.size)
    assert f.background_level == pytest.approx(.8)
    assert f.contrast == pytest.approx(.6)
    assert f.local_contrast_p10 == pytest.approx(.6)
    assert f.local_contrast_p90 == pytest.approx(.6)
    assert f.xheight_px == 12 and f.capheight_ratio == 1
    assert f.stroke_width_px == 4 and f.noise == 0
    assert f.polarity == 'dark_on_light' and inverse.polarity == 'light_on_dark'
    assert inverse.ink_coverage == f.ink_coverage
    assert inverse.contrast == pytest.approx(f.contrast)
    assert inverse.stroke_width_px == f.stroke_width_px


@pytest.mark.parametrize('level', [0, 127, 255])
def test_blank_missing_measurements_and_absent_text(level):
    f = line_features(Image.new('L', (40, 20), level))
    assert f.ink_coverage == f.blur == f.noise == 0
    for name in ('contrast', 'local_contrast_p10', 'stroke_width_px', 'xheight_px', 'capheight_ratio', 'n_chars', 'n_words', 'language_guess'):
        assert getattr(f, name) is None
    assert f.background_level == pytest.approx(level / 255)
    empty = line_features(Image.new('L', (40, 20), level), '')
    assert empty.n_chars == empty.n_words == empty.polytonic_mark_density == 0
    assert empty.language_guess == 'other'


def test_rgb_cast_alpha_and_normalized_arrays():
    mask = blocks() < 100
    rgb = np.full((32, 80, 3), [240, 225, 210], dtype=np.uint8)
    rgb[mask] = [40, 30, 20]
    f = line_features(rgb)
    assert f.background_rgb == pytest.approx(np.array([240, 225, 210]) / 255)
    assert f.background_cast == pytest.approx(np.array([15, 0, -15]) / 255)
    assert f == line_features(rgb.astype(float) / 255)
    rgba = np.concatenate((rgb, np.full((32, 80, 1), 255, dtype=np.uint8)), axis=2)
    assert f == line_features(rgba)
    rgba[:, :, 3] = 0
    assert line_features(rgba).background_rgb == (1, 1, 1)
    assert line_features(Image.fromarray(rgba)).ink_coverage == 0


def test_blur_noise_and_unprinted_gradient():
    image = Image.fromarray(blocks())
    assert line_features(image).blur > line_features(image.filter(ImageFilter.GaussianBlur(1))).blur
    speckles = blocks()
    speckles[4, 4] = speckles[27, 73] = 51
    assert line_features(speckles).noise == 2
    gradient = np.tile(np.linspace(.65, 1, 80), (32, 1))
    f = line_features(gradient)
    assert f.ink_coverage == 0 and f.bg_type == 'gradient'


@pytest.mark.parametrize('image', [np.empty((0, 3)), np.zeros((2, 2, 2)), np.array([[np.nan]]), np.array([[2.0]])])
def test_invalid_rasters_refused(image):
    with pytest.raises(ValueError):
        line_features(image)


def test_unicode_denominators_lexicon_and_canonical_equivalence(tmp_path):
    text = 'Ἅλφα α 12, β.'
    lexicon = tmp_path / 'greek.txt'
    lexicon.write_text('# words\nαλφα\nΒ\n', encoding='utf-8')
    f = line_features(blocks(), text, lexicon=lexicon)
    assert f == line_features(blocks(), ud.normalize('NFD', text), lexicon=load_lexicon(lexicon))
    assert f.polytonic_mark_density == pytest.approx(1 / 6)
    assert f.digit_ratio == pytest.approx(2 / 10)
    assert f.punct_ratio == pytest.approx(2 / 10)
    assert f.upper_ratio == pytest.approx(1 / 6)
    assert f.n_words == 3 and f.lexicon_validity == pytest.approx(2 / 3)
    assert f.n_letters == 6
    assert line_features(blocks(), 'a\u0313').polytonic_mark_density == 0
    assert line_features(blocks(), '123').lexicon_validity is None
    assert line_features(blocks(), 'άλφα', lexicon=[]).lexicon_validity == 0
    assert line_features(blocks(), 'τελικός', lexicon=['ΤΕΛΙΚΟΣ']).lexicon_validity == 1


@pytest.mark.parametrize('text,language', [('ἅλφα', 'grc'), ('άλφα', 'el'), ('the book and the page', 'en'),
                                         ('le livre et la page', 'fr'), ('école', 'fr'), ('Русский', 'other'), ('xyz', 'other')])
def test_language_rules(text, language):
    assert line_features(blocks(), text).language_guess == language


def test_geometry_dataclass_receipt_and_no_guessed_clipping():
    from greekocr.real.geometry import GeometryDiagnostics, refine_line
    diagnostics = GeometryDiagnostics(1, 1, 2., 12., .1, False, 288, 1., (0, 0), ('top', 'left'))
    f = line_features(blocks(), geometry=diagnostics)
    assert f.curl_px == 2 and f.clipped_edges == ('left', 'top') and f.skew_deg is None
    crop = refine_line(Image.fromarray(blocks()), (0, 0, 80, 32), pad=0)
    assert line_features(crop.image, geometry=crop) == line_features(crop.image, geometry=crop.receipt())
    if hasattr(crop.diagnostics, 'baseline_curve'):
        assert line_features(crop.image, geometry=crop.diagnostics).skew_deg is not None
    receipt = dict(diagnostics=dict(curl_amplitude_px=3, source_boundary_ink=[]),
                   curve=dict(c1=10, c2=0, c0=0, x_origin=0, x_scale=100))
    assert line_features(blocks(), geometry=receipt).skew_deg == pytest.approx(np.degrees(np.arctan(.1)))
    assert line_features(blocks(), geometry=receipt).clipped_edges == ()
    with pytest.raises(ValueError):
        line_features(blocks(), geometry={'curl_px': float('nan')})


@pytest.mark.parametrize('entry,year,basis,kind', [
    ({'source': 'parliament', 'year': 1899}, 1899, 'catalogue.year', 'proceedings'),
    ({'source': 'parliament', 'metadata': {'dc.date.issued': [{'value': '1882-02-01'}]}}, 1882, 'catalogue.metadata.dc.date.issued', 'proceedings'),
    ({'source': 'anemi', 'publication_date_displayed': ['1864']}, 1864, 'catalogue.publication_date_displayed', 'book'),
    ({'source': 'archive', 'metadata': {'date': ['1902-05-01']}}, 1902, 'catalogue.metadata.date', 'book'),
    ({'source': 'web', 'fetched_at': '2026-10-08T12:00:00Z'}, 2026, 'fetched_at', 'web'),
    ({'source': 'gazette', 'year': '1900-1901'}, None, None, 'gazette'),
    ({'source': 'news-kathimerini'}, None, None, 'newspaper'),
])
def test_catalogue_year_sources(entry, year, basis, kind):
    row = {'source_doc_id': 'doc', 'source_dataset': entry['source']}
    result = source_metadata(row, {'doc': entry})
    assert (result['year'], result['year_basis'], result['doc_type']) == (year, basis, kind)
    assert result['licence'] is None and result['tier'] is None


@pytest.mark.parametrize('bbox,column,expected', [([0, 0, 80, 30], None, 'header'),
    ([0, 940, 80, 990], None, 'footer'), ([0, 400, 80, 430], None, 'body'), ([0, 400, 80, 430], 2, 'column_2')])
def test_page_position_uses_page_pixels(bbox, column, expected):
    row = dict(bbox_pixel=bbox, page_size_px=[800, 1000], column_index=column)
    assert source_metadata(row)['page_position'] == expected
    row.pop('page_size_px')
    assert source_metadata(row)['page_position'] is None


def test_source_join_ambiguity_rights_and_born_digital():
    row = dict(source_doc_id='same', source_dataset='web', label_tier='silver', licence='unknown', born_digital=True)
    entries = [{'document_id': 'same', 'source': 'archive', 'year': 1800},
               {'document_id': 'same', 'source': 'web', 'fetched_at': '2026-10-08', 'licence': 'CC0'}]
    result = source_metadata(row, entries)
    assert result['year'] == 2026 and result['doc_type'] == 'born_digital_article'
    assert result['licence'] == 'unknown' and result['tier'] == 'silver'
    with pytest.raises(ValueError, match='ambiguous'):
        source_metadata(row, entries + [entries[-1]])
    assert source_metadata(row, {'documents': {'web:same': {'year': 2020}}})['year'] == 2020
    assert source_metadata({'source_doc_id': 'no-match'}, entries)['year'] is None
    assert source_metadata({'source_doc_id': 'same'}, [entries[0]])['year'] == 1800
    assert source_metadata(row, {'same': entries[0]})['year'] is None


@pytest.mark.parametrize('index,family,style', [(0, 'Times-Roman', 'modern_serif'), (1, 'Arial', 'sans')])
def test_fixture_font_prediction(index, family, style):
    prediction = font_estimate(SYNTH / f'line{index}.png', model=MODEL)
    assert prediction.font == family and prediction.font_style == style
    assert prediction.distance == 0 and prediction.margin > 0
    assert prediction.fixture_only and prediction.model_id == 't5-two-raster-fixture'
    assert font_estimate(SYNTH / f'line{index}.png').font is None
    json.dumps(prediction.to_dict(), allow_nan=False)


def test_font_abstention_mapping_and_bad_model():
    assert font_estimate(Image.new('L', (100, 32), 255), model=MODEL).font is None
    assert font_estimate(blocks(), model=MODEL).font is None
    assert font_style('GFSDidot_Classic') == font_style('OldStandard-Regular') == 'didot_greek_19c'
    assert font_style('Courier') == 'mono' and font_style('real') is None
    assert font_style('Custom', {'Custom': 'sans'}) == 'sans'
    data = json.loads(MODEL.read_text())
    data['centroids'][0][0] = float('nan')
    with pytest.raises(ValueError, match='centroids'):
        font_estimate(blocks(), model=data)


def test_numpy_font_fitting_tiny_synthetic_shard_only(tmp_path):
    out = tmp_path / 'fixture-fit.json'
    model = train_font_classifier(SYNTH / 'records.jsonl', out)
    assert model['counts'] == {'Arial': 1, 'Times-Roman': 1}
    assert font_estimate(SYNTH / 'line0.png', model=out).font == 'Times-Roman'
    with pytest.raises(FileExistsError):
        train_font_classifier(SYNTH / 'records.jsonl', out)
    data = tmp_path / 'real.jsonl'
    data.write_text(json.dumps(dict(crop_path=str(SYNTH / 'line0.png'), font='real')) + '\n')
    with pytest.raises(ValueError, match='known synthetic'):
        train_font_classifier(data, tmp_path / 'bad.json')
    assert not (tmp_path / 'bad.json').exists()


def test_annotate_real_lines_deterministic_and_report_complete(tmp_path):
    inputs = tmp_path / 'lines.jsonl'
    rows = [dict(row, crop_path=str(O4D / row['file']), text=row['layer'], source_dataset='parliament', source_doc_id='doc',
                 admitted=False, label_tier='silver_ocr_layer') for row in REAL_LINES]
    inputs.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    digest = hashlib.sha256(inputs.read_bytes()).hexdigest()
    catalogue = {'doc': dict(year=1889, collection='proceedings', licence='unknown')}
    receipt = annotate_records(inputs, tmp_path / 'out.jsonl', catalogue=catalogue)
    assert receipt['records'] == 44
    annotate_records(inputs, tmp_path / 'second.jsonl', catalogue=catalogue)
    assert (tmp_path / 'out.jsonl').read_bytes() == (tmp_path / 'second.jsonl').read_bytes()
    assert hashlib.sha256(inputs.read_bytes()).hexdigest() == digest
    result = [json.loads(s) for s in (tmp_path / 'out.jsonl').read_text().splitlines()]
    assert all(r['text'] == original['text'] and r['admitted'] is False for r, original in zip(result, rows))
    assert all(r['source_metadata']['year'] == 1889 for r in result)
    report = distribution_report(tmp_path / 'out.jsonl')
    assert report == distribution_report(tmp_path / 'out.jsonl')
    assert 'Source: parliament (44 lines)' in report
    for field in NUMERIC + CATEGORICAL:
        assert f'| {field} |' in report
    assert '| background_rgb.r | 0 | 44 |' in report
    assert '| font | <unknown> | 44 |' in report


def test_pipeline_failure_atomic_no_overwrite_and_paths(tmp_path):
    inputs = tmp_path / 'records.jsonl'
    Image.fromarray(blocks()).save(tmp_path / 'line.png')
    good = dict(crop_path='line.png', text='ἅλφα', source_dataset='fixture')
    inputs.write_text(json.dumps(good) + '\n' + json.dumps(dict(crop_path='missing.png')) + '\n')
    target = tmp_path / 'other/out.jsonl'
    with pytest.raises(FileNotFoundError):
        annotate_records(inputs, target)
    assert not target.exists() and not list(target.parent.glob('*.tmp'))
    inputs.write_text(json.dumps(good) + '\n')
    annotate_records(inputs, target)
    assert json.loads(target.read_text())['crop_path'] == str(tmp_path / 'line.png')
    with pytest.raises(FileExistsError):
        annotate_records(inputs, target)
    with pytest.raises(ValueError):
        annotate_records(inputs, inputs)
    assert 'Source: fixture (1 lines)' in distribution_report(target)


def test_synthetic_report_recipe_parity_and_import_placeholders(tmp_path):
    out = tmp_path / 'synth.jsonl'
    annotate_records(SYNTH / 'records.jsonl', out)
    rows = [json.loads(s) for s in out.read_text().splitlines()]
    assert rows[0]['line_features']['font'] == 'Times-Roman'
    assert rows[0]['line_features']['font_style'] == 'modern_serif'
    assert rows[0]['line_features']['applied_ops'] == []
    assert rows[0]['line_features']['severity'] == 0
    assert distribution_report(out) == distribution_report(SYNTH / 'records.jsonl')
    real = dict(crop_path=str(SYNTH / 'line0.png'), text='άλφα', font='real', bg_type='flat', severity=0)
    inputs = tmp_path / 'real.jsonl'
    inputs.write_text(json.dumps(real) + '\n')
    annotate_records(inputs, tmp_path / 'real-out.jsonl')
    result = json.loads((tmp_path / 'real-out.jsonl').read_text())
    assert result['severity'] == 0 and result['line_features']['severity'] is None
    assert result['line_features']['font'] is None


def test_embedded_parquet_shard_report_and_annotation(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    raw = json.loads((SYNTH / 'records.jsonl').read_text().splitlines()[0])
    raw.pop('crop_path')
    raw['image_png'] = (SYNTH / 'line0.png').read_bytes()
    raw['gt_nfd'] = ud.normalize('NFD', raw.pop('text'))
    shards = tmp_path / 'shards/train'
    shards.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([raw]), shards / 'shard-00000.parquet')
    report = distribution_report(shards.parent)
    assert '| font | Times-Roman | 1 |' in report
    annotate_records(shards.parent, tmp_path / 'out.jsonl')
    result = json.loads((tmp_path / 'out.jsonl').read_text())
    assert result['image_png_sha256'] == hashlib.sha256(raw['image_png']).hexdigest()
    assert 'image_png' not in result
    model = train_font_classifier(shards.parent, tmp_path / 'fit.json')
    assert model['counts'] == {'Times-Roman': 1}


def test_cli_legacy_lines_report_lexicon_model_and_failures(tmp_path, capsys):
    assert main(['annotate', 'ἅλφα Latin']) == 0
    assert json.loads(capsys.readouterr().out)['script_class'] == 'greek_latin_cs'
    out = tmp_path / 'out.jsonl'
    assert main(['annotate', 'lines', str(SYNTH / 'records.jsonl'), '--out', str(out)]) == 0
    assert json.loads(capsys.readouterr().out)['records'] == 2
    report = tmp_path / 'report.md'
    assert main(['annotate', 'report', str(out), '--out', str(report)]) == 0
    assert report.read_text() == capsys.readouterr().out
    assert main(['annotate', 'lines', str(SYNTH / 'records.jsonl'), str(out)]) == 3
    assert capsys.readouterr().err
    assert main(['annotate', 'lines']) == 3
    assert 'INPUT OUTPUT' in capsys.readouterr().err


def test_stratum_buckets_counts_and_floor_guarantees():
    a = dict(script_class='greek_poly', polytonic_mark_density=.1, doc_type='book', year=1899,
             contrast=.19, ink_coverage=.049, font_style='didot_greek_19c')
    b = dict(a, script_class='greek_mono', polytonic_mark_density=0, year=2000, contrast=.5, ink_coverage=.2)
    assert stratum_key(a) == ('greek_poly', True, 'book', '1800_1899', 'low', 'sparse', 'didot_greek_19c')
    assert stratum_key(b)[3:6] == ('2000_plus', 'high', 'dense')
    assert stratum_key({}) == (None, None, None, 'unknown', 'unknown', 'unknown', None)
    assert stratum_key(dict(line_features=a, source_metadata=a)) == stratum_key(a)
    rows = [a] * 9 + [b]
    assert stratum_counts(rows) == {stratum_key(a): 9, stratum_key(b): 1}
    weights = sampling_weights(rows)
    assert sum(weights[:9]) == pytest.approx(.5) and weights[-1] == .5
    weights = sampling_weights(rows, targets={stratum_key(a): 99, stratum_key(b): 1}, floor=.2)
    assert sum(weights) == pytest.approx(1) and weights[-1] == pytest.approx(.2)
    assert sum(weights[:9]) == pytest.approx(.8)
    weights = sampling_weights(rows, floors={stratum_key(b): .7})
    assert weights[-1] == .7
    assert sampling_weights([]) == []
    assert sampling_weights(rows) == sampling_weights(rows)
    weights = sampling_weights(rows, targets={stratum_key(a): 1e308, stratum_key(b): 1e308})
    assert sum(weights) == pytest.approx(1) and weights[-1] == .5


@pytest.mark.parametrize('kwargs', [{'floor': .6}, {'floor': -1}, {'floor': float('nan')},
                                   {'floors': {('absent',): .1}}, {'targets': {('absent',): .1}}])
def test_infeasible_weights_refused(kwargs):
    with pytest.raises(ValueError):
        sampling_weights([dict(script_class='latin'), dict(script_class='greek_poly')], **kwargs)


def test_imports_without_torch_or_arrow():
    code = "import sys; from greekocr.annotate import line_features, font_estimate; assert 'torch' not in sys.modules; assert 'pyarrow' not in sys.modules"
    subprocess.run([sys.executable, '-c', code], cwd=ROOT, check=True, timeout=20)


def test_field_documentation_covers_dataclass():
    docs = (relocated(ROOT / 'docs/LINE_METADATA.md')).read_text()
    for field in fields(LineFeatures):
        assert f'`{field.name}`' in docs


def test_metadata_public_api_typed_and_documented():
    from scripts.generate_api_docs import api_entries
    docs = (ROOT / 'docs/API.md').read_text()
    for module, name, node, owner in api_entries():
        if not module.startswith('greekocr.annotate'):
            continue
        qualified = module + '.' + (owner + '.' if owner else '') + name
        assert f'### `{qualified}`' in docs
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None
            assert all(arg.annotation is not None for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                       if arg.arg not in ('self', 'cls'))
