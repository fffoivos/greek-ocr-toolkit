"""R7 ink contracts and physical counterexamples; no production page model."""
import cv2
import numpy as np
import pytest
from ..shared.contracts import rect
from ..shared.ink_solid import render as solid,candidates
from ..shared.ink_normal import calibrate,NormalInk
from ..shared.ink_faintness import analyze,classify
from ..shared.ink_photometry import percentiles8
from .test_round6 import page,item


def test_exact_histogram_order_statistics():
    rng=np.random.default_rng(31)
    for shape in [(1,1),(17,22),(800,150)]:
        a=rng.integers(0,256,shape,dtype=np.uint8)
        np.testing.assert_array_equal(percentiles8(a,[50,90]),np.percentile(a,[50,90]))


@pytest.mark.parametrize('kind,drop',[('mass',True),('counter',False),('thin',False),('blank',False)])
def test_solid_interior_is_not_stroke_or_counter(kind,drop):
    gray=np.full((160,160),245,np.uint8);p=rect([40,40,90,90])
    if kind=='mass':cv2.circle(gray,(65,65),18,10,-1)
    elif kind=='counter':cv2.circle(gray,(65,65),18,10,3)
    elif kind=='thin':cv2.line(gray,(65,45),(65,85),10,3)
    assert bool(len(solid(gray,[p],32).indices))==drop


def test_solid_near_text_is_unknown():
    gray=np.full((160,160),245,np.uint8);cv2.circle(gray,(65,65),18,10,-1)
    p=[rect([40,40,90,90]),rect([95,50,130,80])]
    assert not len(candidates(p,32)[1])
    assert not len(solid(gray,p,32).indices)


def test_black_roi_has_finite_disk_and_empty_is_safe():
    gray=np.zeros((80,80),np.uint8)
    r=solid(gray,[rect([20,20,50,50])],24)
    assert len(r.indices)==1 and 0<r.disks[0,2]<=16
    assert not len(solid(gray,[],24).indices)
    with pytest.raises(ValueError):solid(gray,[],0)


def test_normal_reference_calibration():
    gray,items=page('faint');context,evidence=calibrate(gray,items,height=30)
    assert isinstance(context.normal,NormalInk)
    assert evidence['suppress_indices']==[7] and context.normal.support>=12


def test_clipped_neighbour_cannot_supply_normal_area():
    from ..stack.test_r6 import glyph
    gs=[glyph(x,30,.2) for x in range(0,150,10)];g=glyph(155,20,.9,800);g['clipped']=True;gs.append(g)
    ref=dict(core=.9,stroke=2,boundary=.6,body_height=10,support=30)
    r=classify([dict(components=gs)],ref)[0]
    assert not r['normal_run'] and r['drop']


def test_real_front_controls():
    import json
    from pathlib import Path
    from .round6_faintness import ROOT
    controls=json.loads(Path(__file__).with_name('round7_controls.json').read_text())
    for r in controls:
        gray=cv2.imread(str(ROOT/r['path']),0)
        if gray is None:pytest.skip('local development images unavailable')
        # Recompute the existing page reference on this real page. The stored
        # reference is a receipt, not an input to this test.
        a=analyze(gray,r['items'],height=r['height'],require_reference=True)
        from ..shared.ink_faintness import components
        for q in r['controls']:
            c=classify([dict(components=components(gray,q,r['height'],route='localized'))],a['reference'])[0]
            assert not c['drop'],(r['page'],q['owner_number'])


def test_footprint_generation_tracks_siblings_sources_and_copies():
    from ..shared.ink_footprints import Footprints
    import copy
    a=dict(item(0,0,100,20),source_ids=[4]);ledger=Footprints();judged=ledger.stamp_all([a])
    same=copy.deepcopy(a);assert not ledger.changed_indices([same],judged)
    left=dict(a,polygon=rect([0,0,50,20]));right=dict(a,polygon=rect([50,0,100,20]))
    assert ledger.changed_indices([left,right],judged)=={0,1}
    assert left['ink_token']!=right['ink_token'] and left['ink_token'][0]==right['ink_token'][0]
    ownership=dict(a,source_ids=[5]);assert ledger.changed_indices([ownership],judged)=={0}
    assert a['polygon']==rect([0,0,100,20])
