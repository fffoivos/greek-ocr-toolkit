"""Native preparation contracts, not a new source-attribution test."""
import cv2
import numpy as np
import pytest
from . import ink_photometry as photo
from ..evidence.r8_frame_parts import correspond


def page():
    g=np.full((70,120),255,np.uint8)
    for x in (15,45,75):cv2.rectangle(g,(x,20),(x+14,45),0,-1)
    return g,[0,0,120,70]


def test_native_glyph_labels_reused_but_height_and_limit_are_fresh(monkeypatch):
    g,b=page();p=photo.glyph_pixels(g,b);old=photo.components;calls=[]
    def counted(mask):calls.append(mask.size);return old(mask)
    monkeypatch.setattr(photo,'components',counted)
    shared=photo.glyph_pixels(g,b,prepared=[p]);assert shared is p
    assert len(photo.glyphs(g,b,20,pixels=shared))==3
    assert len(photo.glyphs(g,b,20,limit=1,pixels=shared))==1
    assert photo.glyphs(g,b,90,pixels=shared)==[]
    assert calls==[]
    fresh=photo.glyphs(g,b,20);assert calls==[g.size]
    reused=photo.glyphs(g,b,20,pixels=shared)
    for a,z in zip(fresh,reused):
        assert a['bbox']==z['bbox']
        np.testing.assert_array_equal(a['vector'],z['vector'])


def test_native_observation_does_not_alias_mutable_glyph_records():
    g,b=page();p=photo.glyph_pixels(g,b)
    with pytest.raises(ValueError):p[3][0,0]=1
    with pytest.raises(ValueError):p[4][0,0]=1
    first=photo.glyphs(g,b,20,pixels=p);first[0]['line']=99;first[0]['bbox'][0]=-1;first[0]['vector'][:]=0
    second=photo.glyphs(g,b,20,pixels=p)
    assert 'line' not in second[0] and second[0]['bbox'][0]>=0
    assert np.linalg.norm(second[0]['vector'])>0


@pytest.mark.parametrize('change',['image','roi','threshold'])
def test_incompatible_native_observations_recompute_or_reject(change,monkeypatch):
    g,b=page();p=photo.glyph_pixels(g,b);old=photo.components;calls=[]
    def counted(mask):calls.append(mask.size);return old(mask)
    monkeypatch.setattr(photo,'components',counted)
    gg=g.copy() if change=='image' else g
    bb=[1,0,120,70] if change=='roi' else b
    threshold=.6 if change=='threshold' else .7
    new=photo.glyph_pixels(gg,bb,threshold,prepared=[p]);assert new is not p and calls
    with pytest.raises(ValueError):photo.glyphs(gg,bb,20,threshold,pixels=p)


def test_native_part_correspondence_never_inserts_ink_or_absorbs_remote_mark():
    exemplar=np.zeros((30,30),np.uint8);cv2.circle(exemplar,(15,15),7,1,-1)
    actual=exemplar.copy();actual[13:16,13:16]=0;actual[1,1]=1
    explained,_,_=correspond(actual,exemplar)
    assert not explained[1,1] and not explained[14,14]
    assert not (explained & ~actual.astype(bool)).any()
