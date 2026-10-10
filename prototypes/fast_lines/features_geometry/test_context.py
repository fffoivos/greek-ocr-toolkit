"""Ownership and identity invariants for the shared-stack geometry adapter."""
import numpy as np
import pytest
from prototypes.fast_lines.shared import geometry_context as context


def box(x0, y0, x1, y1):
    return dict(polygon=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]], baseline=None, score=.9)


def witnesses(trigger=False):
    return dict(candidates=[]), dict(trigger=trigger, nominated=[0], height=10)


def test_scout_reuse_and_original_source_identity(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Precomputed scout repeated')
    monkeypatch.setattr(context, 'scout', forbidden)
    monkeypatch.setattr(context, 'sparse', forbidden)
    rules, geometry = witnesses()
    items = [box(0,0,20,10), box(30,0,50,10), box(60,0,80,10)]
    out = context.correct_geometry(np.full((100,100),255,np.uint8), np.zeros((10,10)),
        items, retained_source_indices=[2,0], rule_witness=rules, geometry_scout=geometry)
    assert [q['source_ids'] for q in out['items']] == [[0], [2]]
    assert out['reused'] == dict(rule_scout=True, geometry_scout=True)
    assert items[0].get('source_ids') is None


def test_removed_neighbor_cannot_authorize_ink_loss(monkeypatch):
    gray = np.full((100,200),255,np.uint8)
    gray[30:35,20:180] = 0
    items = [box(10,20,190,75), box(10,20,190,75)]
    proposal = box(10,60,190,75)['polygon']
    def band_stub(pm, originals, size, version):
        assert originals is items  # ancestry always sees originals, including removed neighbors
        return dict(lines=[dict(line=0, polygon=proposal, source_boxes=1,
            multi_run_fraction=0, path=[[x,65] for x in range(10,191,20)], bend_h=.5,
            angle_deg=0)])
    monkeypatch.setattr(context, 'bands', band_stub)
    rules, geometry = witnesses(True)
    shared = dict(rule_witness=rules, geometry_scout=geometry)
    all_retained = context.correct_geometry(gray, np.zeros((10,10)), items, **shared)
    assert len(all_retained['geometry_changes']) == 1
    removed = context.correct_geometry(gray, np.zeros((10,10)), items,
        retained_source_indices=[0], **shared)
    assert not removed['geometry_changes']
    assert removed['items'][0]['polygon'] == items[0]['polygon']
    assert removed['geometry_decisions'][0]['retention']['lost_ink'] > 0


@pytest.mark.parametrize('indices', [[0,0],[-1],[2],[.5]])
def test_invalid_retained_sources_reject(indices):
    rules, geometry = witnesses()
    with pytest.raises(ValueError):
        context.correct_geometry(np.zeros((30,30),np.uint8), np.zeros((10,10)),
            [box(0,0,20,10)], retained_source_indices=indices,
            rule_witness=rules, geometry_scout=geometry)
