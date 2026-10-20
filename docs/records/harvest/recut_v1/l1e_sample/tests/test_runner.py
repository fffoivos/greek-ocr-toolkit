import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
import pytest

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('t6d_runner', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
audit = runner.load_module('t6d_audit_test', runner.AUDIT)


def line(doc='document', page=1, number=1, wave='round1', split='train', crop_doc=None):
    stem = f'p{page:06d}-l{number:04d}'
    return dict(id=f'{doc}-{stem}', wave=wave, doc=f'{wave}:{doc}', split=split, admitted=True,
                crop=f'docs/harvest/harvest_big/{wave}/crops/{crop_doc or doc}/{stem}.png')


def manifest(tmp_path, records):
    filename = tmp_path / 'manifest.jsonl'
    filename.write_text(''.join(json.dumps(r) + '\n' for r in records))
    return {'train': filename}


def test_validate_ids_preserves_requested_order(tmp_path):
    a, b = line(), line(number=2)
    result = runner.validate_ids([b['id'], a['id']], manifest(tmp_path, [a, b]))
    assert [r['id'] for r in result] == [b['id'], a['id']]


def test_round2_short_crop_directory_is_valid(tmp_path):
    row = line(doc='abcdef012345', wave='round2', crop_doc='abcdef')
    result = runner.validate_ids([row['id']], manifest(tmp_path, [row]))
    assert result[0]['doc_id'] == 'abcdef012345'


@pytest.mark.parametrize('wave', ['parliament', 'cyrillic', 'unknown'])  # vouli accepted since 17 Oct (coordinator)
def test_reject_other_wave(tmp_path, wave):
    row = line(wave=wave)
    with pytest.raises(ValueError, match='unsupported wave'):
        runner.validate_ids([row['id']], manifest(tmp_path, [row]))


def test_reject_non_v2_id(tmp_path):
    with pytest.raises(ValueError, match='not a v2 line'):
        runner.validate_ids(['missing'], manifest(tmp_path, [line()]))


def test_reject_duplicate_manifest_id(tmp_path):
    row = line()
    with pytest.raises(ValueError, match='duplicate v2 ID'):
        runner.validate_ids([row['id']], manifest(tmp_path, [row, row]))


@pytest.mark.parametrize('mutation', [dict(crop='../bad.png'), dict(admitted=False),
                                     dict(doc='round1:wrong'), dict(split='dev')])
def test_reject_malformed_v2_metadata(tmp_path, mutation):
    row = line()
    row.update(mutation)
    with pytest.raises(ValueError, match='not a valid v2 line'):
        runner.validate_ids([row['id']], manifest(tmp_path, [row]))


def test_id_list_rejects_duplicates(tmp_path):
    filename = tmp_path / 'ids.txt'
    filename.write_text('same\nsame\n')
    with pytest.raises(ValueError, match='duplicate'):
        runner.read_ids(filename)


def test_group_pages_separates_wave_doc_and_page(tmp_path):
    records = [line(), line(number=2), line(page=2), line(doc='another'), line(wave='mixed')]
    validated = runner.validate_ids([r['id'] for r in records[:4]], manifest(tmp_path, records[:4]))
    mixed = dict(records[-1], page=1, doc_id='document')
    groups = runner.group_pages(validated + [mixed])
    assert len(groups) == 4
    assert len(groups[('round1', 'document', 1)]) == 2
    assert len(groups[('mixed', 'document', 1)]) == 1


def test_default_output_is_outside_checkout():
    assert not runner.OUTPUT.resolve().is_relative_to(ROOT.resolve())
    assert runner.OUTPUT == Path.home() / 'Projects/collect-v3-data/v2_masked/l1e_sample'


def test_matching_failures_are_identity_crops():
    original = Image.fromarray(np.arange(100, dtype=np.uint8).reshape(10, 10))
    for index, candidates, expected in [(None, [], 'unmatched'), (0, [{}, {}], 'ambiguous')]:
        assert runner.match_failure(index, candidates) == expected
        image, record = runner.identity(original, [0, 0, 10, 10])
        assert np.array_equal(np.asarray(image), np.asarray(original))
        assert record['changed'] is False and record['masked_pixel_count'] == 0
    assert runner.match_failure(0, [{}]) is None


def test_matcher_is_original_and_has_no_extra_column_gate():
    runner.frozen()
    match, fit = runner.matcher()
    records = [dict(x0=0, x1=100, xheight=10., baseline=np.full(100, 55.), meanline=np.full(100, 45.))]
    fits = [fit(r) for r in records]
    assert match([0, 40, 100, 60], fits) == 0
    assert runner.candidate_diagnostics([0, 40, 100, 60], fits)[0]['index'] == 0
    assert match([0, 100, 100, 120], fits) is None


def box_hits(row, box):
    x0, y0, x1, y1 = box
    return (row['_x'] >= x0) & (row['_x'] < x1) & (row['_y'] >= y0) & (row['_y'] < y1)


def test_shared_audit_counts_components_and_actual_pixel_changes():
    labels = np.array([[1, 1, 0, 2], [1, 0, 0, 2]])
    prepared = {i: dict(row_id=i, _y=np.nonzero(labels == i)[0], _x=np.nonzero(labels == i)[1]) for i in (1, 2)}
    mask = np.array([[False, True, False, True], [False, False, False, True]])
    counts, lost_ids = audit.component_audit(prepared, labels, [0, 0, 4, 2], mask, 1, box_hits)
    assert counts['own_component_pixels_lost'] == 1
    assert counts['own_pixels'] == 3 and lost_ids == {1}
    assert counts['foreign_pixels_removed'] == 2
    assert counts['foreign_components_removed_from_crop'] == 1


def test_shared_audit_unknown_owner_stays_unknown():
    counts, lost = audit.component_audit({}, np.zeros((2, 2), int), [0, 0, 2, 2],
                                        np.zeros((2, 2), bool), None, box_hits)
    assert counts['own_component_pixels_lost'] is None
    assert counts['foreign_pixels_removed'] is None and not lost


def test_low_priority_fails_closed(monkeypatch):
    monkeypatch.setattr(runner.os, 'getpriority', lambda *unused: 0)
    with pytest.raises(RuntimeError, match='require at least 15'):
        runner.low_priority()


def test_output_rejects_read_only_input_root():
    with pytest.raises(ValueError, match='overlaps'):
        runner.prepare_output(runner.INPUT)


def test_watchdog_checks_output_and_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'OUTPUT', tmp_path)
    watchdog = runner.Watchdog()
    watchdog.deadline = 0
    assert watchdog.check() == '55_minute_run_budget'


def test_opencv_is_actually_single_threaded():
    assert runner.single_thread_opencv().getNumThreads() == 1


def test_nonempty_output_cannot_be_resumed(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'OUTPUT', runner.OUTPUT)
    output = tmp_path / 'output'
    output.mkdir()
    (output / 'receipt.json').write_text('{}')
    with pytest.raises(ValueError, match='no resume or overwrite'):
        runner.prepare_output(output)
