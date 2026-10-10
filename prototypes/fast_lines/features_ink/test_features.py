"""Mechanism invariants, not seen-page label fitting."""
import copy
import cv2
import numpy as np
import pytest
from ..shared.ink_photometry import percentiles8,glyphs,match_glyphs
from ..shared.ink_ownership import analyze
from ..shared.ink_strokes import measure,heuristic
from ..shared.ink_images import render
from ..shared.ink_motif_gate import inspect
from ..shared.ink_edges import profiles
from .pipeline import ink_run
from ..shared.ink_recurrence import render as recurrent


def strokes():
    a=np.full((100,420),240,np.uint8)
    for x in range(20,390,55):
        cv2.rectangle(a,(x,25),(x+8,70),20,-1)
        cv2.rectangle(a,(x,25),(x+30,32),20,-1)
        cv2.rectangle(a,(x,46),(x+22,52),20,-1)
    return a


def item(b):
    x,y,z,t=b
    return dict(polygon=[[x,y],[z,y],[z,t],[x,t]],baseline=None,score=.8)


@pytest.mark.parametrize('seed',[0,1,2])
def test_integer_quantiles_match_numpy(seed):
    a=np.random.default_rng(seed).integers(0,256,(17,31),dtype=np.uint8)
    assert np.allclose(percentiles8(a,[0,2,10,90,100]),np.percentile(a,[0,2,10,90,100]))


def test_attenuation_changes_contrast_not_shape():
    a=strokes();f=np.uint8(240-(240-a.astype(float))*.3);b=[0,0,a.shape[1],a.shape[0]]
    x,y=measure(a,b,45),measure(f,b,45)
    assert y['contrast']<.4*x['contrast']
    for p,q in zip(x['thresholds'],y['thresholds']):
        assert p['width_h']==q['width_h']
        assert p['components']==q['components']
        assert p['readability']=='unknown'


def test_thickening_changes_shape_even_when_darkness_does_not():
    a=strokes();fat=cv2.erode(a,np.ones((5,5),np.uint8));b=[0,0,420,100]
    x,y=measure(a,b,45),measure(fat,b,45)
    assert x['contrast']==y['contrast']
    assert y['thresholds'][1]['width_h']>x['thresholds'][1]['width_h']


def test_breaks_are_separate_from_attenuation():
    a=strokes();broken=a.copy();broken[42:47]=240;b=[0,0,420,100]
    x,y=measure(a,b,45),measure(broken,b,45)
    assert y['thresholds'][1]['components']>x['thresholds'][1]['components']


def test_mirror_template_has_spatial_handedness():
    a=strokes();atlas=glyphs(a,[0,0,420,100],45)
    query=glyphs(a[:,::-1].copy(),[0,0,420,100],45)
    matches=match_glyphs(query,atlas)
    assert len(matches)>=4
    assert all(m['reflected']>m['direct']+.1 for m in matches)


def test_symmetry_does_not_supply_mirror_vote():
    a=np.full((100,420),240,np.uint8)
    for x in range(30,380,55):cv2.circle(a,(x,50),18,20,5)
    atlas=glyphs(a,[0,0,420,100],45);matches=match_glyphs(atlas,atlas)
    assert matches and all(m['margin']<=.01 for m in matches)


def test_no_dark_anchor_means_unknown_not_clean():
    a=np.full((100,200),240,np.uint8);items=[item([10,20,190,70])]
    r=analyze(a,items)
    assert not r['suppress_indices'] and r['regions'][0]['ownership']=='unknown'


def test_repeated_letters_are_not_continuous_ornament():
    a=strokes();r,_=inspect(a,item([5,15,410,80]),45)
    assert not r['drop']


def test_blank_paper_is_not_area_ink():
    r=render(np.full((180,220),220,np.uint8),15)
    assert not r['regions'] and not r['mask'].any()


def test_runtime_preserves_input_and_unknowns():
    a=strokes();items=[item([5,15,410,80])];saved=copy.deepcopy(items);raw=a.copy()
    r=ink_run(a,items)
    assert r['items']==items and items==saved and np.array_equal(a,raw)


def test_invalid_route_is_rejected():
    with pytest.raises(ValueError):analyze(strokes(),[],route='unregistered')


def test_heuristic_fading_invariance():
    a=strokes();f=np.uint8(240-(240-a.astype(float))*.3);b=[0,0,420,100]
    assert heuristic(a,b,45)['width_h']==heuristic(f,b,45)['width_h']


def test_profile_spread_is_separate_from_attenuation():
    a=strokes();f=np.uint8(240-(240-a.astype(float))*.3);b=[0,0,420,100]
    x,y=profiles(a,b,45),profiles(f,b,45)
    assert x['accepted']>20 and y['accepted']>20
    assert abs(x['edge_width_h']-y['edge_width_h'])<.002


def test_profile_spread_increases_on_known_blur():
    a=strokes();blur=cv2.GaussianBlur(a,(0,0),2);b=[0,0,420,100]
    x,y=profiles(a,b,45),profiles(blur,b,45)
    assert y['edge_width_h']>2*x['edge_width_h']


def test_shared_height_and_evidence_preserve_default_decisions():
    a=strokes();items=[item([5,15,410,80])];default=ink_run(a,items)
    supplied=ink_run(a,items,height=default['ownership']['height'])
    reused=ink_run(a,items,ownership_evidence=default['ownership'])
    assert default['items']==supplied['items']==reused['items']
    assert reused['ownership_reused'] and not supplied['ownership_reused']
    assert len(reused['motif_costs'])==len(items)


def test_shared_evidence_rejects_changed_regions():
    a=strokes();items=[item([5,15,410,80])];e=analyze(a,items)
    with pytest.raises(ValueError):ink_run(a,[item([5,15,409,80])],ownership_evidence=e)
    with pytest.raises(ValueError):ink_run(a,items,height=e['height']*2,ownership_evidence=e)
    with pytest.raises(ValueError):ink_run(a[:-1],items,ownership_evidence=e)


@pytest.mark.parametrize('height',[0,-1,float('nan')])
def test_shared_height_rejects_invalid_scale(height):
    with pytest.raises(ValueError):analyze(strokes(),[],height=height)


def test_recurrence_uses_shape_not_darkness_and_never_erases():
    a=strokes();q=item([0,0,420,100]);f=np.uint8(240-(240-a.astype(float))*.3)
    x=recurrent(a,q,45,route='explicit');y=recurrent(f,q,45,route='explicit')
    assert x['nominate'] and y['nominate']
    assert abs(x['best']['coverage']-y['best']['coverage'])<.01
    assert 'drop' not in x


def test_blank_and_nonperiodic_shapes_do_not_supply_recurrence():
    a=np.full((100,420),240,np.uint8)
    assert not recurrent(a,item([0,0,420,100]),45,route='heuristic')['nominate']
    cv2.rectangle(a,(30,20),(55,75),20,-1)
    cv2.circle(a,(100,55),15,20,2)
    cv2.line(a,(190,20),(230,75),20,5)
    assert not recurrent(a,item([0,0,420,100]),45,route='heuristic')['nominate']
