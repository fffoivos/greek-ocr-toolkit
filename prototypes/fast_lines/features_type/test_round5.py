"""Physical ownership and composition regressions, without page-name gates."""
import copy
import cv2
import numpy as np
from ..shared.contracts import rect
from ..shared.type_residual import render, ink_scout
from ..shared.type_residual_recovery import piece_support, recover
from ..shared.type_initials import complete


def item(box):return dict(polygon=rect(box),baseline=None,score=.9)


def test_separator_cannot_borrow_other_column_witness():
    points=[[x,25] for x in range(10,91,15)]
    assert piece_support(item([0,15,100,35]),points,[],10)
    assert not piece_support(item([110,15,210,35]),points,[],10)


def test_separator_cannot_reuse_recovered_witness():
    points=[[x,25] for x in range(10,91,15)];q=item([0,15,100,35])
    assert not piece_support(q,points,[q],10)
    assert not piece_support(q,points[:4],[],10)


def test_touching_box_edge_does_not_own_glyph_interior():
    g=np.full((100,200),255,np.uint8)
    for x in range(20,180,25):cv2.rectangle(g,(x,40),(x+10,59),0,-1)
    shallow=render(g,[item([0,20,200,41])],height=20,version=4)
    deep=render(g,[item([0,20,200,48])],height=20,version=4)
    assert all(z['touched'] and not z['interior_owned'] for z in shallow['bodies'])
    assert all(z['interior_owned'] for z in deep['bodies'])
    assert all(not z['owned'] for z in deep['bodies'])  # centre alone is insufficient


def test_native_depth_and_stroke_scale_together():
    records=[]
    for scale in (1,2):
        g=np.full((100*scale,160*scale),255,np.uint8)
        cv2.rectangle(g,(30*scale,40*scale),(40*scale,60*scale),0,-1)
        r=render(g,[item([0,0,160*scale,42*scale])],height=20*scale,version=4)
        records.append(r['bodies'][0])
    assert not any(z['interior_owned'] for z in records)
    assert abs(records[1]['stroke_radius']-2*records[0]['stroke_radius'])<=1


def initial_fixture():
    g=np.full((180,360),255,np.uint8)
    cv2.rectangle(g,(25,42),(34,105),0,-1)
    for y in (42,68,98):cv2.rectangle(g,(25,y),(61,y+7),0,-1)
    for x in range(80,330,25):cv2.rectangle(g,(x,84),(x+11,105),0,-1)
    return g,item([66,80,342,111])


def test_large_initial_attaches_to_first_adjacent_row():
    g,q=initial_fixture();before=copy.deepcopy(q)
    after,ev=complete(g,q,[q],22)
    assert ev['changed'] and after['initial_completed']
    assert np.asarray(after['polygon'])[:,1].min()<45
    assert q==before
    masks=[]
    for z in (q,after):
        m=np.zeros(g.shape,np.uint8);cv2.fillPoly(m,[np.rint(z['polygon']).astype(np.int32)],1);masks.append(m)
    assert not np.any(masks[0]&~masks[1])


def test_large_initial_not_stolen_from_earlier_row():
    g,q=initial_fixture();prior=item([66,43,342,69])
    after,ev=complete(g,q,[prior,q],22)
    assert not ev['changed'] and after==q


def test_large_initial_never_crosses_removal_footprint():
    g,q=initial_fixture()
    after,ev=complete(g,q,[q],22,excluded_regions=[item([20,38,65,110])])
    assert not ev['changed'] and after==q


def test_blank_clean_page_never_calls_regional_detector():
    g=np.full((180,360),255,np.uint8);items=[item([20,40,340,65])]
    class NoDetector:
        def infer(self,*a,**kw):raise AssertionError('unnecessary regional inference')
    result=recover(g,items,NoDetector())
    assert result['items']==items and not result['added'] and not result['calls']


def test_rejected_row_ink_cannot_wake_residual_scout():
    g=np.full((180,360),255,np.uint8)
    for x in range(20,330,22):cv2.rectangle(g,(x,80),(x+9,99),0,-1)
    rows=[item([10,75,345,105])]
    assert not ink_scout(g,rows,version=5)['regions']
    assert not ink_scout(g,[],excluded_regions=rows,version=5)['regions']


def test_recurrence_negative_skips_full_verifier_without_certifying_text(monkeypatch):
    from ..shared import type_residual_recovery as module
    monkeypatch.setattr(module,'recurrence',lambda *a,**k:dict(nominate=False))
    def forbidden(*a,**k):raise AssertionError('unnecessary full spatial verifier')
    monkeypatch.setattr(module,'motif',forbidden)
    r=module.candidate_motif(np.full((20,30),255,np.uint8),item([1,1,20,10]),5)
    assert not r['drop'] and 'unknown' in r['reason']


def test_recurrence_nomination_still_needs_full_ornament_witness(monkeypatch):
    from ..shared import type_residual_recovery as module
    monkeypatch.setattr(module,'recurrence',lambda *a,**k:dict(nominate=True))
    seen=[]
    def full(gray,q,h,diagnostic):
        seen.append((h,diagnostic));return dict(drop=False,remaining_glyphs=8),None
    monkeypatch.setattr(module,'motif',full)
    r=module.candidate_motif(np.full((20,30),255,np.uint8),item([1,1,20,10]),5)
    assert not r['drop'] and seen==[(5,True)]
