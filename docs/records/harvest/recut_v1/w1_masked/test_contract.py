"""Boundary checks for the audit and the qualification population contract."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import component_audit
spec = importlib.util.spec_from_file_location('t6b_contract_run', BASE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_audit_distinguishes_own_and_foreign_and_unknown():
    own = dict(row_id='own', _y=np.zeros(10, dtype=int), _x=np.arange(10))
    foreign = dict(row_id='foreign', _y=np.ones(10, dtype=int), _x=np.arange(10))
    prepared = dict(own=own, foreign=foreign)
    labels = np.vstack([np.ones(10, dtype=int), np.full(10, 2, dtype=int)])
    def hits(row, box):
        return np.ones(len(row['_y']), dtype=bool)
    changed = np.zeros((2, 10), dtype=bool); changed[0, :3] = True; changed[1, :] = True
    counts, ids = component_audit.component_audit(prepared, labels, (0, 0, 10, 2), changed, 'own', hits)
    assert counts['own_pixels'] == 10 and counts['own_component_pixels_lost'] == 3
    assert counts['foreign_pixels_removed'] == 10 and counts['foreign_components_removed_from_crop'] == 1
    assert ids == {1}
    assert not counts['own_component_pixels_lost']/counts['own_pixels'] > .30
    changed[0, 3] = True
    counts, _ = component_audit.component_audit(prepared, labels, (0, 0, 10, 2), changed, 'own', hits)
    assert counts['own_component_pixels_lost']/counts['own_pixels'] > .30
    counts, _ = component_audit.component_audit(prepared, labels, (0, 0, 10, 2), changed, None, hits)
    assert counts['own_pixels'] is None and counts['own_component_pixels_lost'] is None
    empty = dict(row_id='own', _y=np.array([], dtype=int), _x=np.array([], dtype=int))
    counts, _ = component_audit.component_audit(dict(own=empty, foreign=foreign), labels,
                                               (0, 0, 10, 2), changed, 'own', hits)
    assert counts['own_pixels'] == counts['own_component_pixels_lost'] == 0
    assert counts['foreign_pixels_removed'] == 10


def test_rotated_letter_boundary_and_caps_tag_union():
    row = dict(crop_bbox=[0, 0, 10, 11], label='αβγ 123')
    assert not runner.rotated(row)
    row['label'] = 'αβγδ 123'; assert runner.rotated(row)
    row['crop_bbox'] = [0, 0, 11, 11]; assert not runner.rotated(row)
    assert runner.caps_heading(dict(tags=[], line_tags=['heading']))
    assert runner.caps_heading(dict(tags=['caps'], line_tags=[]))
    assert not runner.caps_heading(dict(tags=['numeric'], line_tags=[]))


def test_guard_uses_original_dark_ink_and_strict_threshold():
    ink = np.ones((1, 10), dtype=bool)
    changed = np.zeros_like(ink); changed[:, :3] = True
    m = runner.guard_measure(ink, changed)
    assert m['own_ink_masked_fraction'] == .30 and not m['own_ink_masked_fraction'] > .30
    changed[:, 3] = True
    assert runner.guard_measure(ink, changed)['own_ink_masked_fraction'] > .30
    empty = runner.guard_measure(np.zeros_like(ink), changed)
    assert empty['original_dark_ink_empty'] and empty['own_ink_masked_fraction'] == 0.


def test_seeded_cards_keep_guarded_originals_and_public_key_separation(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'BASE', tmp_path)
    (tmp_path / 'cards').mkdir()
    records = []
    for i in range(100):
        crop = tmp_path / f'crop{i:03d}.png'; crop.write_bytes(f'original-{i}'.encode())
        digest = runner.sha(crop)
        records.append(dict(id=f'l{i:03d}', page_id='p1', masked_crop=crop.name, google_text='α'*(i+1),
            original_crop_sha256=digest, masked_crop_sha256=digest, wrong_line_risk=i == 0,
            own_ink_masked_fraction=.31 if i == 0 else 0., output_kind='guarded_original' if i == 0 else 'masked',
            mask_applied=i != 0, changed=False))
    receipt = runner.draw_cards('test', records)
    cards = runner.rows(tmp_path / receipt['cards'])
    key = __import__('json').loads((tmp_path / receipt['key']).read_text())
    assert receipt['count'] == 100 and receipt['guarded_cards'] == 1
    assert key['_pool'] == 100
    assert {key[c['card_id']]['line_id'] for c in cards} == {r['id'] for r in records}
    assert [len(c['google_text']) for c in cards] != sorted(len(c['google_text']) for c in cards)
    assert all(set(c) == {'card_id', 'crop', 'google_text', 'word_scripts'} for c in cards)
