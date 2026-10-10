"""Physical and invariance checks for the conditional Q8 separator path."""
import copy
import cv2
import numpy as np
import pytest
from prototypes.fast_lines.layout_barriers.fast import run, clip_polygon
from prototypes.fast_lines.shared.contracts import rect
from prototypes.fast_lines.shared.review import change_overlay


def specimen(rule=True, slant=0., cells=False):
    im=np.full((600,600),245,np.uint8)
    items=[]
    if rule:
        cv2.line(im,(int(300-270*slant),30),(int(300+270*slant),570),20,2)
    for y in range(70,550,35):
        for x in list(range(50,270,14))+list(range(330,555,14)):
            cv2.rectangle(im,(x,y),(x+7,y+14),30,-1)
        b=[45,y-3,565,y+20] if not cells else [265,y-3,335,y+20]
        items.append(dict(polygon=rect(b),baseline=None,score=.8))
    return im,items


@pytest.mark.parametrize('slant',[0.,.02,-.02])
def test_rule_splits_without_expanding_or_retilting(slant):
    im,items=specimen(slant=slant)
    original=copy.deepcopy(items)
    product=run(im,items)
    assert len(product['changes'])>=10
    assert items==original
    for q in product['changes']:
        old=np.asarray(q['old'],np.float32)
        for p in q['new']:
            assert all(cv2.pointPolygonTest(old,tuple(map(float,xy)),False)>=0 for xy in p)


def test_no_rule_means_no_correction():
    im,items=specimen(rule=False)
    product=run(im,items)
    assert product['items'] is items and product['correction_s']==0.
    assert not product['witness']['candidates']


def test_currency_width_is_outside_prose_scope():
    im,items=specimen(cells=True)
    product=run(im,items)
    assert not product['witness']['candidates']
    assert product['items']==items


def test_spanning_text_vetoes_cut():
    im,items=specimen()
    # Continuous title-like ink through the rule: it must not be clipped.
    cv2.rectangle(im,(280,68),(320,85),25,-1)
    product=run(im,items)
    assert 0 not in {q['line'] for q in product['changes']}


def test_empty_detector_not_declared_clean():
    im,_=specimen()
    product=run(im,[])
    assert product['witness']['status']=='empty detector unresolved'


def test_slanted_halfplane_preserves_existing_edges():
    p=[[0.,0.],[100.,10.],[100.,30.],[0.,20.]]
    q=clip_polygon(p,.1,50,1)
    assert q[0]==p[0] and q[-1]==p[-1]
    assert all(x<=.1*y+50+1e-8 for x,y in q)
    assert any(abs(x-.1*y-50)<1e-8 for x,y in q)


def test_odd_image_dimensions_have_bounded_geometry():
    im,items=specimen()
    im=np.pad(im,((0,3),(0,1)),constant_values=245)
    p=run(im,items)
    assert p['changes']
    for q in p['items']:
        a=np.asarray(q['polygon']); assert (a>=0).all() and (a<=[601,603]).all()


def test_discounted_geometry_never_drawn_in_delta():
    im=np.full((100,100),255,np.uint8)
    item=dict(polygon=rect([10,10,90,90]),discounted=True)
    delta=dict(line=0,old=item['polygon'],new=[rect([10,10,30,90])])
    image=change_overlay(im,[item],[],[delta],width=100)
    assert (image==255).all()
