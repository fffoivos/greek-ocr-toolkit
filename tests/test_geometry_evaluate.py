"""Pixel-only invariants and offline evaluation with independent mock readers."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import random
import sys
import types

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pytest

from greekocr.cli import main
from greekocr.real.geometry import GEOMETRY_POLICY, crop_quality, refine_line
from greekocr.real.geometry_evaluate import evaluate_geometry, inter_reader_cer

ROOT = Path(__file__).resolve().parents[1]
REPLAY = json.loads((ROOT/'tests/data/geometry_policy_replay.json').read_text())['rows']


@pytest.mark.parametrize('row', REPLAY, ids=lambda r: Path(r['path']).name)
def test_v3_retains_diacritic_and_body_ink_and_is_deterministic(row):
    path = ROOT/row['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['source_sha256']
    with Image.open(path) as source:
        original = source.convert('L')
    before = original.tobytes()
    line = refine_line(original, (0, 0, *original.size), policy='v3')
    quality = crop_quality(original, line.image, line.diagnostics)
    # Independent coordinate census, never using cached retained counts.
    curve = np.array([line.curve.evaluate(x) for x in range(original.width)])[None, :]
    y = np.arange(original.height)[:, None]
    height = line.diagnostics.x_height_px
    band = (y >= curve-1.9*height) & (y <= curve+.6*height)
    output_y = y-np.rint(curve).astype(int)+line.ascent
    output_x = np.arange(original.width)[None, :]-line.refined_box[0]
    after = np.asarray(line.image)[np.clip(output_y, 0, line.image.height-1), output_x] < 220
    after &= (output_y >= 0) & (output_y < line.image.height)
    dark = np.asarray(original) < 220
    for name, zone in [('diacritic', band & (y < curve-height)), ('body', band & (y >= curve-height))]:
        old, new = int((dark & zone).sum()), int((after & zone).sum())
        assert new >= .97*old
        assert quality[f'{name}_ink_retained'] == (new/old if old else 1)
    assert quality['diacritic_ink_retained'] >= .97
    assert quality['body_ink_retained'] >= .97
    assert quality['reader_confidence'] is quality['inter_reader_agreement'] is None
    repeated = refine_line(original, (0, 0, *original.size))
    assert repeated.receipt() == line.receipt()
    assert repeated.image.tobytes() == line.image.tobytes()
    assert original.tobytes() == before
    assert line.diagnostics.policy == GEOMETRY_POLICY
    assert crop_quality(original, line.image, line.receipt()) == quality
    if path.name.endswith('_old.png'):
        # Both supplied rasters are preserved evidence; the v1 output is not a page.
        assert path.with_name(path.name.replace('_old.png', '_new.png')).is_file()


@pytest.mark.parametrize('row', REPLAY, ids=lambda r: Path(r['path']).name)
@pytest.mark.parametrize('policy', ['v1', 'v2'])
def test_historical_policies_replay_independently_captured_raster_contracts(row, policy):
    with Image.open(ROOT/row['path']) as source:
        image = source.convert('L')
    line = refine_line(image, (0, 0, *image.size), policy=policy)
    expected = row[policy]
    assert list(line.image.size) == expected['size']
    assert hashlib.sha256(line.image.tobytes()).hexdigest() == expected['raster_sha256']
    assert [c.id for c in line.kept_components] == expected['kept_ids']
    assert [c.id for c in line.dropped_components] == expected['dropped_ids']


@pytest.mark.parametrize('name', ['line01_large.png', 'line06_large.png'])
def test_v3_removes_neighbour_intrusions_and_rectifies_measured_baseline(name):
    with Image.open(ROOT/'tests/fixtures/o4d_lines'/name) as source:
        original = source.convert('L')
    line = refine_line(original, (0, 0, *original.size))
    quality = crop_quality(original, line.image, line.diagnostics)
    assert quality['ink_counts']['neighbour']['original'] > 0
    assert quality['neighbour_ink_removed'] > 0
    assert line.dropped_components
    assert quality['curl_residual_px'] < 2  # A fresh robust pixel fit, not a claimed exact zero.
    assert quality['curl_residual_px'] < .1*line.diagnostics.curl_amplitude_px


def staged_manifest(tmp_path, *, layer='another OCR is not truth'):
    pages = tmp_path/'pages'
    pages.mkdir()
    image = Image.new('L', (310, 125), 250)
    draw = ImageDraw.Draw(image)
    for x in range(15, 295, 25):
        draw.rectangle((x, 40, x+10, 59), fill=30)
        draw.rectangle((x+2, 27, x+5, 30), fill=10)
        draw.rectangle((x, 100, x+10, 119), fill=45)
    image.save(pages/'page.png')
    box = [0, 15, 310, 122]
    image.crop(box).save(tmp_path/'original.png')
    rows = [dict(line_id=f'line-{i}', page_id='page', bbox_pixel=box,
                 crop_path='original.png', text=layer) for i in range(2)]
    records = tmp_path/'lines.jsonl'
    records.write_text('\n'.join(json.dumps(row) for row in rows)+'\n')
    return records, pages, image, box


def test_crop_quality_detects_erased_marks_clipping_blur_and_supports_reader_hooks(tmp_path):
    _, _, page, box = staged_manifest(tmp_path)
    original = page.crop(box)
    line = refine_line(page, box)
    pixels = np.asarray(line.image).copy()
    pixels[:line.ascent-int(line.diagnostics.x_height_px)] = 255
    pixels[:, 0] = 0
    pixels[:, -1] = 0
    quality = crop_quality(original, Image.fromarray(pixels), asdict(line.diagnostics) | {
        'reader_confidence': -.25, 'inter_reader_agreement': .1})
    assert quality['diacritic_ink_retained'] < .97
    assert quality['body_ink_retained'] >= .97
    assert quality['clipped_left'] and quality['clipped_right']
    assert quality['reader_confidence'] == -.25 and quality['inter_reader_agreement'] == .1
    blurred = crop_quality(original, line.image.filter(ImageFilter.GaussianBlur(2)), line.diagnostics)
    good = crop_quality(original, line.image, line.diagnostics)
    assert blurred['blur_refined'] < good['blur_refined']
    assert blurred['contrast_refined'] < good['contrast_refined']
    with pytest.raises(ValueError, match='reader_confidence'):
        crop_quality(original, line.image, asdict(line.diagnostics) | {'reader_confidence': float('nan')})
    with pytest.raises(ValueError, match='source_box'):
        crop_quality(original, line.image, {})
    with pytest.raises(ValueError, match='size'):
        crop_quality(page, line.image, line.diagnostics)
    with pytest.raises(ValueError, match='policy'):
        refine_line(page, box, policy='v4')


def test_blank_signals_never_invent_confidence_or_neighbour_removal():
    image = Image.new('L', (200, 80), 255)
    line = refine_line(image, (0, 0, *image.size))
    quality = crop_quality(image, line.image, line.diagnostics)
    assert quality['diacritic_ink_retained'] == quality['body_ink_retained'] == 1
    assert quality['neighbour_ink_removed'] is quality['curl_residual_px'] is None
    assert quality['contrast_delta'] == quality['blur_delta'] == 0
    assert not quality['clipped_left'] and not quality['clipped_right']
    assert json.loads(json.dumps(quality, allow_nan=False)) == quality


def test_evaluate_cli_mocked_readers_reference_free_summary_and_blind_mapping(tmp_path, monkeypatch, capsys):
    records, pages, _, _ = staged_manifest(tmp_path)
    module = types.ModuleType('t6_mock_reader')
    calls = []
    def cllg(path):
        calls.append(path)
        with Image.open(path) as crop:
            assert crop.width == 310
        return dict(text='ἅβ', character_confidences=[.9, .8])
    module.cllg, module.ours = cllg, lambda path: 'αβ'
    monkeypatch.setitem(sys.modules, module.__name__, module)
    out = tmp_path/'evaluation'
    argv = ['geometry', 'evaluate', '--records', str(records), '--page-images', str(pages),
            '--policies', 'original,v1,v2,v3', '--readers', 'cllg,ours',
            '--reader', 'cllg=t6_mock_reader:cllg', '--reader', 'ours=t6_mock_reader:ours', '--out', str(out)]
    random.seed(19)
    before = random.getstate()
    assert main(argv) == 0
    assert random.getstate() == before
    receipt = json.loads(capsys.readouterr().out)
    assert receipt == json.loads((out/'receipt.json').read_text())
    assert len(calls) == 8
    for summary in receipt['summary'].values():
        assert summary['evaluated'] == summary['confidence_samples'] == summary['agreement_samples'] == 2
        assert summary['mean_reader_confidence'] == pytest.approx((np.log(.9)+np.log(.8))/2)
        assert summary['mean_inter_reader_agreement'] == .5
        assert summary['by_reader']['ours']['mean_reader_confidence'] is None
    for row in receipt['rows']:
        assert row['text_layer_diagnostic']['status'] == 'another OCR; never a reference'
        for crop in row['policies'].values():
            assert (out/crop['crop_path']).is_file()
            assert crop['readers']['cllg']['mean_confidence'] == pytest.approx(.85)
            assert crop['readers']['cllg']['min_confidence'] == .8
            assert crop['pixels']['inter_reader_agreement'] == .5
            assert crop['readers']['ours']['mean_log_probability'] is None
    for file in ('summary.csv', 'summary.md'):
        table = (out/file).read_text()
        assert 'layer' not in table and 'exact' not in table
    pairs = json.loads((out/'ab_pairs.json').read_text())
    mapping = json.loads((out/'ab_mapping.json').read_text())
    assert (out/'ab.html').is_file()
    assert 'v3' not in (out/'ab.html').read_text()
    assert 'policy' not in json.dumps(pairs)
    for line, key, row in zip(pairs['lines'], mapping['lines'], receipt['rows']):
        assert len(line['choices']) == 4
        for choice in line['choices']:
            policy = key['policy_by_choice'][choice['choice']]
            assert (out/choice['crop_path']).read_bytes() == (out/row['policies'][policy]['crop_path']).read_bytes()
    assert main(argv) == 3
    assert 'File exists' in capsys.readouterr().err and len(calls) == 8
    other = tmp_path/'repeated'
    assert main(argv[:-1]+[str(other)]) == 0
    assert json.loads(capsys.readouterr().out) == receipt
    assert (out/'ab_pairs.json').read_bytes() == (other/'ab_pairs.json').read_bytes()


def test_text_layer_cannot_change_scores_and_errors_are_not_agreement(tmp_path):
    records, pages, _, _ = staged_manifest(tmp_path)
    def failed(path):
        raise RuntimeError('reader unavailable')
    readers = {'first': lambda path: 'ἅ', 'failed': failed}
    first = evaluate_geometry(records, page_images=pages, readers=readers, out=tmp_path/'first')
    rows = [json.loads(s) for s in records.read_text().splitlines()]
    for row in rows:
        row['text'] = 'changed arbitrary OCR output'
    records.write_text('\n'.join(json.dumps(r) for r in rows))
    second = evaluate_geometry(records, page_images=pages, readers=readers, out=tmp_path/'second')
    assert first['summary'] == second['summary']
    for summary in first['summary'].values():
        assert summary['reader_errors'] == 2
        assert summary['agreement_samples'] == summary['confidence_samples'] == 0
        assert summary['mean_inter_reader_agreement'] is summary['mean_reader_confidence'] is None
    for row in rows:
        row['crop_path'] = str(tmp_path/row['crop_path'])  # Sequence paths resolve against cwd.
    rows[0]['crop_path'] = 'missing.png'
    partial = evaluate_geometry(rows, page_images=pages, readers=readers, out=tmp_path/'partial')
    assert 'error' in partial['rows'][0] and 'error' not in partial['rows'][1]
    assert 'name="line1"' in (tmp_path/'partial/ab.html').read_text()
    assert 'name="line0"' not in (tmp_path/'partial/ab.html').read_text()
    rows[1]['crop_path'] = 'missing-too.png'
    result = evaluate_geometry(rows, page_images=pages, readers=readers, out=tmp_path/'missing')
    assert all('error' in r for r in result['rows'])
    assert all(s['evaluated'] == 0 and s['clipping_rate'] is None for s in result['summary'].values())


def test_evaluate_cli_builtin_cllg_requests_confidence_and_closes(tmp_path, monkeypatch, capsys):
    records, pages, _, _ = staged_manifest(tmp_path)
    config = tmp_path/'readers.json'
    config.write_text(json.dumps({'cllg': {'checkpoint': 'local.safetensors', 'python': 'venv/bin/python'}}))
    calls = []
    class MockCLLG:
        binding = {'checkpoint_sha256': 'mock'}
        def read(self, path):
            return {'text': 'ἅ', 'mean_confidence': .8, 'min_confidence': .7, 'mean_log_probability': -.3}
        def close(self):
            calls.append('closed')
    def load(checkpoint, contract, **kwargs):
        assert checkpoint == tmp_path/'local.safetensors'
        assert kwargs['confidence'] is True
        assert kwargs['python'] == tmp_path/'venv/bin/python'
        calls.append('loaded')
        return MockCLLG()
    monkeypatch.setattr('greekocr.readers.cllg.load_cllg_worker', load)
    assert main(['geometry', 'evaluate', '--records', str(records), '--page-images', str(pages),
                 '--readers', 'cllg', '--reader-config', str(config), '--out', str(tmp_path/'native')]) == 0
    receipt = json.loads(capsys.readouterr().out)
    assert calls == ['loaded', 'closed']
    assert receipt['reader_bindings'] == {'cllg': {'checkpoint_sha256': 'mock'}}


def test_page_mapping_validation_and_missing_confidence(tmp_path):
    records, pages, _, _ = staged_manifest(tmp_path)
    mapping = tmp_path/'page_images.json'
    mapping.write_text(json.dumps({'page': 'pages/page.png'}))
    result = evaluate_geometry(records, page_images=mapping, policies=['original', 'v3'],
                               readers={'one': lambda path: ''}, out=tmp_path/'mapped')
    assert result['page_images_sha256']
    assert all(s['mean_reader_confidence'] is None for s in result['summary'].values())
    rows = [json.loads(s) for s in records.read_text().splitlines()]
    rows[1]['line_id'] = rows[0]['line_id']
    with pytest.raises(ValueError, match='unique'):
        evaluate_geometry(rows, page_images=pages, readers={'one': lambda path: ''}, out=tmp_path/'bad')
    assert not (tmp_path/'bad').exists()
    for policies in ([], ['v3', 'v3'], ['unknown']):
        with pytest.raises(ValueError, match='policies'):
            evaluate_geometry([], policies=policies, readers={'one': lambda p: ''}, out=tmp_path/'bad')


@pytest.mark.parametrize('a,b,expected', [('ἅ', 'α\u0314\u0301', 0), ('', '', 0), ('', 'abc', 1),
                                       ('ab', 'abc', 1/3), ('a b', 'ab', 1/3)])
def test_inter_reader_cer_is_symmetric_normalized_and_preserves_whitespace(a, b, expected):
    assert inter_reader_cer(a, b) == inter_reader_cer(b, a) == expected
