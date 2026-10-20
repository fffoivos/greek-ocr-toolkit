"""Cost sampling and fixed-census matching keep their observation contracts."""
import cv2
import numpy as np
import pytest
from .geometry_rows import valley_grid,valley_path
from .ink_photometry import glyph_atlas,match_glyphs,glyphs,glyph_pixels


@pytest.mark.parametrize('height',[7.,20.,37.])
def test_gap_cost_sampling_preserves_path_and_roi_border(height):
    shape=(97,413);yy,xx=np.indices(shape)
    ink=np.zeros(shape,np.uint8)
    ink[5:42,13:38]=1;ink[58:93,134:167]=1
    ink[:,0]=1;ink[-1,:]=1
    native=cv2.dilate(ink,np.ones((max(1,round(.1*height)),)*2,np.uint8))
    y1=8+.013*np.arange(shape[1]);y2=77-.025*np.arange(shape[1])
    full=np.where((yy>y1+.2*height)&(yy<y2-.2*height),
                  native.astype(float)*1e3+.005*((yy-(y1+y2)/2)/height)**2,1e6)
    grid=valley_grid(shape,height);gy,gx,_=grid
    sampled=np.where((gy[:,None]>y1[gx]+.2*height)&(gy[:,None]<y2[gx]-.2*height),
                     native[np.ix_(gy,gx)].astype(float)*1e3+.005*((gy[:,None]-(y1[gx]+y2[gx])/2)/height)**2,1e6)
    assert np.array_equal(sampled,full[np.ix_(gy,gx)])
    assert np.array_equal(valley_path(full,height),valley_path(sampled,height,grid=grid))


def test_atlas_snapshot_survives_changed_membership():
    gray=np.full((70,310),245,np.uint8)
    cv2.putText(gray,'Greek types',(7,45),0,1.,20,2)
    atlas=glyphs(gray,[4,20,190,51],25)
    assert len(atlas)>2
    query=list(reversed(atlas))
    prepared=glyph_atlas(atlas)
    scores=match_glyphs(query,prepared)
    assert not prepared.vectors.flags.writeable and not prepared.aspects.flags.writeable
    atlas[:]=atlas[::-1]
    assert match_glyphs(query,prepared)==scores
    assert glyph_atlas(atlas).exemplars==prepared.exemplars[::-1]
    original=prepared.vectors.copy();atlas[0]['vector'][:]=0
    assert np.array_equal(prepared.vectors,original)
    assert not np.array_equal(glyph_atlas(atlas).vectors,prepared.vectors)


def test_component_tiles_survive_height_selection_without_sharing_mutable_records():
    gray=np.full((70,310),245,np.uint8)
    cv2.putText(gray,'Greek types',(7,45),0,1.,20,2)
    box=[4,20,190,51];pixels=glyph_pixels(gray,box)
    first=glyphs(gray,box,25,pixels=pixels);assert first
    first[0]['vector'][:]=0;first[0]['tile'][:]=0;first[0]['line']=999
    for height,limit in [(20,3),(30,64),(25,64)]:
        fresh=glyphs(gray,box,height,limit=limit)
        shared=glyphs(gray,box,height,limit=limit,pixels=pixels)
        assert len(fresh)==len(shared)
        for a,b in zip(fresh,shared):
            assert a.keys()==b.keys() and a['bbox']==b['bbox']
            assert np.array_equal(a['vector'],b['vector']) and np.array_equal(a['tile'],b['tile'])
    changed=gray.copy();changed[:]=245
    assert not glyphs(changed,box,25)
    with pytest.raises(ValueError):glyphs(changed,box,25,pixels=pixels)
