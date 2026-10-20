"""Physical faintness controls: page calibration, mixed ink and real stroke runs."""
import cv2
import numpy as np
import pytest
from ..shared.contracts import rect
from ..shared.ink_faintness import render,analyze
from ..shared.ink_faint_scout import render as scout


def item(x,y,z,w):return dict(polygon=rect([x,y,z,w]),baseline=None,score=.9)


def page(mode):
    g=np.full((480,720),245,np.uint8);items=[]
    for k in range(7):
        y=38+k*52;cv2.putText(g,'NATIVE NORMAL PRINT',(18,y),0,.85,25,2,cv2.LINE_AA)
        items.append(item(12,y-28,360,y+5))
    y=430
    if mode in ('faint','speck'):cv2.putText(g,'PALE WHOLE LINE',(18,y),0,.85,205,2,cv2.LINE_AA)
    elif mode=='mixed':
        cv2.putText(g,'PALE WORD',(18,y),0,.85,205,2,cv2.LINE_AA)
        cv2.putText(g,'REAL',(230,y),0,.85,25,2,cv2.LINE_AA)
    elif mode=='thin':cv2.putText(g,'THIN REAL LINE',(18,y),0,.85,25,1,cv2.LINE_AA)
    elif mode=='grey':cv2.putText(g,'REAL GREY LINE',(18,y),0,.85,60,2,cv2.LINE_AA)
    if mode=='speck':g[y-15:y-13,45:47]=25
    items.append(item(12,y-28,360,y+5))
    return g,items


@pytest.mark.parametrize('mode,removed',[('faint',[7]),('speck',[7]),('mixed',[]),('thin',[]),('grey',[])])
def test_faint_whole_segment_and_normal_run(mode,removed):
    g,items=page(mode)
    assert render(g,items,height=30)['suppress_indices']==removed
    assert analyze(g,items,height=30)['suppress_indices']==removed


def test_uniformly_pale_page_is_its_own_reference():
    g,items=page('grey');g=np.rint(245-(245-g.astype(float))*.2).astype(np.uint8)
    assert not render(g,items,height=30)['suppress_indices']
    assert not analyze(g,items,height=30)['suppress_indices']


def test_thinness_is_not_a_faintness_label():
    g,items=page('thin');e=render(g,items,height=30)
    bodies=[a for a in e['regions'][-1]['components'] if a['body']]
    assert np.median([a['relative_stroke'] for a in bodies])<1
    assert not e['regions'][-1]['drop']


def test_blank_and_empty_input_never_deleted():
    g=np.full((100,200),240,np.uint8)
    assert not analyze(g,[],height=20)['suppress_indices']
    assert not analyze(g,[item(0,0,180,60)],height=20)['suppress_indices']


def test_existing_page_census_is_bound_to_image_size():
    g,items=page('faint')
    with pytest.raises(ValueError):analyze(g,items,height=30,ownership_evidence=dict(image_size=[1,1],regions=[]))


def test_colour_scale_tracks_common_illumination():
    g,items=page('faint');darker=np.rint(g.astype(float)*.8).astype(np.uint8)
    assert analyze(darker,items,height=30)['suppress_indices']==[7]


def test_tilted_polygon_does_not_sample_rectangular_neighbours():
    g=np.full((200,500),245,np.uint8)
    cv2.putText(g,'NORMAL',(40,70),0,1,25,2,cv2.LINE_AA)
    q=dict(polygon=[[20,85],[400,100],[400,130],[20,115]],baseline=None,score=.9)
    from ..shared.ink_faintness import components
    assert not any(a['core']>.8 for a in components(g,q,30))
