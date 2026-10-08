"""Scoring replay and real file/CLI contracts with an explicit offline reader."""
import json
from pathlib import Path
import sys
import types

from PIL import Image, ImageDraw
import pytest

from greekocr.cli import main
from greekocr.real.geometry import GEOMETRY_POLICY, refine_line
from greekocr.real.geometry_measure import comparison_scores, measure_geometry, summarize_measurements

ROOT = Path(__file__).resolve().parents[1]


def test_coordinator_scores_replayed_for_all_400_saved_readings():
    recorded = json.loads((ROOT/'docs/O4D_G1_measure_v1.json').read_text())
    rows = []
    for row in recorded['rows']:
        scores = comparison_scores(row['layer'], row['old'], row['new'])
        for key in ('cer_old', 'cer_new', 'exact_old', 'exact_new'):
            assert scores[key] == row[key], (row['line_id'], key)
        rows.append(row | scores)
    summary = summarize_measurements(rows)
    for key, value in recorded['summary'].items():
        if key == 'by_tier':
            for tier, metrics in value.items():
                for metric, expected in metrics.items():
                    assert summary[key][tier][metric] == pytest.approx(expected)
        else:
            assert summary[key] == pytest.approx(value)
    assert summary['scored'] == 400
    assert summary['levenshtein_cer_old_mean'] < summary['cer_old_mean']


def test_normalization_exact_and_whitespace_conventions_are_explicit():
    scores = comparison_scores('ἅ', 'α\u0314\u0301 ', 'α\u0301\u0314')
    assert scores['exact_old'] and not scores['exact_new']
    assert scores['cer_old'] == scores['levenshtein_cer_old'] == 1/3
    assert scores['levenshtein_cer_new'] == 2/3
    assert comparison_scores('', '', '')['cer_new'] == 0
    assert comparison_scores('', '', 'abc')['cer_new'] == 3
    empty = summarize_measurements([])
    assert empty['n'] == empty['errors'] == empty['scored'] == 0
    assert empty['cer_old_mean'] is None


def manifest(tmp_path):
    image = Image.new('L', (300, 110), 250)
    draw = ImageDraw.Draw(image)
    for x in range(20, 280, 25):
        draw.rectangle((x, 35, x+10, 54), fill=35)
        draw.rectangle((x+2, 22, x+5, 25), fill=20)
    image.save(tmp_path/'page.png')
    box = [0, 15, 300, 70]
    image.crop(box).save(tmp_path/'original.png')
    rows = [dict(line_id='one', crop_path='original.png', bbox_pixel=box,
                 page_image_path='page.png', text='ἅ β', tier='silver_agreed'),
            dict(line_id='two', crop_path='original.png', bbox_pixel=box,
                 page_image_path='page.png', text='ἅ β', tier='flagged')]
    lines = tmp_path/'lines.jsonl'
    lines.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows)+'\n')
    return lines, image, box


def test_measure_callable_reads_original_and_exact_refined_png_and_retains_receipt(tmp_path):
    lines, image, box = manifest(tmp_path)
    expected = refine_line(image, box)
    calls = []
    def reader(path):
        calls.append(path)
        assert isinstance(path, Path) and path.is_file()
        if path.name == 'original.png':
            return 'α β'
        with Image.open(path) as saved:
            assert saved.tobytes() == expected.image.tobytes()
        return 'α\u0314\u0301 β'
    out = tmp_path/'measure'
    result = measure_geometry(lines, reader, out=out)
    assert json.loads((out/'receipt.json').read_text()) == json.loads(json.dumps(result))
    assert len(calls) == 4
    assert result['geometry_policy'] == GEOMETRY_POLICY
    assert result['summary']['n'] == result['summary']['scored'] == 2
    assert result['summary']['exact_old'] == 0 and result['summary']['exact_new'] == 2
    assert result['summary']['improved'] == result['summary']['admitted'] == 2
    assert len(result['summary']['by_tier']) == 2
    for row in result['rows']:
        assert row['text'] == row['layer'] == 'ἅ β'
        assert row['geometry']['text'] == row['geometry']['source_text'] == 'ἅ β'
        assert row['crop_sha256'] and row['page_sha256'] and row['refined_crop_sha256']
        assert (out/row['refined_crop_path']).exists()
    with pytest.raises(FileExistsError):
        measure_geometry(lines, reader, out=out)
    assert len(calls) == 4  # Refusal happens before reading any crop again.


def test_measure_per_line_errors_and_temporary_cleanup(tmp_path):
    lines, _, _ = manifest(tmp_path)
    calls = []
    def reader(path):
        calls.append(path)
        if len(calls) == 1:
            raise RuntimeError('fixture reader failed')
        return 'ἅ β'
    result = measure_geometry(lines, reader)
    assert result['summary']['n'] == 2 and result['summary']['errors'] == 1
    assert result['summary']['scored'] == result['summary']['exact_new'] == 1
    assert result['summary']['improved'] == result['summary']['worsened'] == 0
    assert result['rows'][0]['error'] == dict(type='RuntimeError', message='fixture reader failed')
    assert result['rows'][1]['refined_crop_path'] is None
    assert calls[-1].name.startswith('line') and not calls[-1].exists()
    result = measure_geometry(lines, lambda path: None)
    assert result['summary']['errors'] == 2
    assert result['summary']['cer_new_mean'] is None


def test_measure_cli_imports_only_named_callable_and_refuses_overwrite(tmp_path, monkeypatch, capsys):
    lines, _, _ = manifest(tmp_path)
    module = types.ModuleType('fixture_geometry_reader')
    module.read = lambda path: 'ἅ β'
    monkeypatch.setitem(sys.modules, module.__name__, module)
    out = tmp_path/'cli'
    argv = ['geometry', 'measure', '--lines', str(lines), '--reader', 'fixture_geometry_reader:read',
            '--out', str(out)]
    assert main(argv) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed == json.loads((out/'receipt.json').read_text())
    assert printed['reader'] == 'fixture_geometry_reader:read'
    assert printed['summary']['exact_old'] == printed['summary']['exact_new'] == 2
    assert main(argv) == 3
    assert 'File exists' in capsys.readouterr().err
    assert main(argv[:-3]+['invalid', '--out', str(tmp_path/'invalid')]) == 3
    assert 'module:callable' in capsys.readouterr().err
    assert not (tmp_path/'invalid').exists()


def test_measure_validates_manifest_before_creating_output(tmp_path):
    lines, _, _ = manifest(tmp_path)
    rows = [json.loads(s) for s in lines.read_text().splitlines()]
    rows[1]['line_id'] = rows[0]['line_id']
    lines.write_text('\n'.join(json.dumps(r) for r in rows))
    out = tmp_path/'bad'
    with pytest.raises(ValueError, match='unique'):
        measure_geometry(lines, lambda path: 'text', out=out)
    assert not out.exists()
    with pytest.raises(TypeError, match='callable'):
        measure_geometry([], None)
    with pytest.raises(ValueError, match='requires'):
        measure_geometry([{'line_id': 'incomplete'}], lambda path: '')


def test_measure_reports_two_tracks_without_assigning_split_labels(tmp_path):
    original = ROOT/'tests/fixtures/o4d_lines/line01_large.png'
    with Image.open(original) as image:
        size = image.size
    row = dict(line_id='two_tracks', crop_path=str(original), page_image_path=str(original),
               bbox_pixel=[0, 0, *size], text='unassigned two-line text')
    result = measure_geometry([row], lambda path: 'unassigned two-line text')
    assert result['summary']['multi_baseline'] == result['summary']['source_multi_baseline'] == 1
    assert result['rows'][0]['split_count'] == 2
    assert result['rows'][0]['text'] == row['text']
    assert 'split text remains unassigned' in result['scoring']['split_labels']
