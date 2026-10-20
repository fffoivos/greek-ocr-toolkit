"""Physical rectangle contracts; no provider/model dependencies."""
from dataclasses import replace
import numpy as np
from PIL import Image, ImageDraw
import pytest
from greekocr.glyphs.vertical_recut import (
    FontBand, TightenParams, band_from_record, fit_font_band, tighten_box, tighten_page,
)


def band():
    return FontBand(10,110,10.,np.full(100,30.),np.full(100,55.),
                    np.full(100,50.),np.full(100,40.))


def test_tightening_never_expands_and_horizontal_extent_is_literal():
    rng=np.random.default_rng(42)
    for _ in range(200):
        y0=int(rng.integers(0,40));y1=int(rng.integers(51,100))
        old=(7,y0,115,y1)
        r=tighten_box(old,band(),[],params=TightenParams(.2,.3))
        assert r.new_box[0]==old[0] and r.new_box[2]==old[2]
        assert y0<=r.new_box[1]<r.new_box[3]<=y1


def test_neighbour_token_edges_round_inward_and_ignore_other_columns():
    r=tighten_box((10,10,110,80),band(),[(20,10,40,35.2),(20,53.8,40,75), (111,40,140,70)])
    assert r.new_box==(10,36,110,53)
    assert r.neighbour_top==35.2 and r.neighbour_bottom==53.8


def test_neighbour_conflict_abstains():
    r=tighten_box((10,10,110,80),band(),[(20,5,40,50),(20,42,40,80)])
    assert r.status=='conflicting_neighbour_or_band'
    assert r.new_box==r.old_box


def test_idempotence_with_stable_own_guides_and_token_boxes():
    first=tighten_box((10,10,110,80),band(),[(15,5,45,33)])
    again=tighten_box(first.new_box,band(),[(15,5,45,33)])
    assert again.new_box==first.new_box


def test_owned_accent_or_descender_pixel_refuses_trim():
    yy=np.array([27,42,57]);xx=np.array([50,51,52])
    r=tighten_box((10,10,110,80),band(),[],own_pixels=(yy,xx))
    assert r.status=='own_ink_guard' and not r.changed
    assert r.proposed_own_pixels_lost==2 and r.own_pixels==3


def test_guides_round_outward_and_native_pixels_are_unchanged():
    b=replace(band(),top=np.full(100,30.4),bottom=np.full(100,55.2))
    r=tighten_box((10,10,110,80),b,[],params=TightenParams(0,0))
    assert r.new_box==(10,30,110,56)
    a=np.random.default_rng(5).integers(0,256,(100,150,3),dtype=np.uint8)
    image=Image.fromarray(a).crop(r.new_box)
    assert np.array_equal(np.asarray(image),a[30:56,10:110])


def test_page_callable_uses_existing_fitter_without_saved_detector_cache():
    # Native Google geometry + simple repeated body pixels, no F2 path or source ID.
    image=Image.new('L',(250,100),255);draw=ImageDraw.Draw(image)
    for x in range(15,225,15):draw.rectangle((x,35,x+7,48),fill=0)
    fitted=fit_font_band(image,(10,20,235,70))
    assert fitted is not None
    lines=[dict(guide_box=(10,20,235,70),crop_bbox=(10,20,235,70),tokens=[(15,35,225,49)])]
    result=tighten_page(image,lines)
    assert len(result)==1 and result[0].new_box[0::2]==(10,235)
    assert 20<=result[0].new_box[1]<result[0].new_box[3]<=70


def test_cached_six_guides_include_accent_top():
    row=dict(x0=10,x1=110,xheight=10.,font_top=np.full(100,32),accent_top=np.full(100,28),
             font_bottom=np.full(100,55),baseline=np.full(100,50),meanline=np.full(100,40))
    r=tighten_box((10,10,110,80),band_from_record(row),[],params=TightenParams(0,0))
    assert r.new_box[1]==28


def test_missing_or_invalid_guides_abstain():
    assert not tighten_box((10,10,110,80),None,[]).changed
    assert not tighten_box((10,10,110,80),replace(band(),xheight=float('nan')),[]).changed


def test_parameter_hash_is_canonical_and_rejects_expansion_margins():
    p=TightenParams(.2,.3)
    assert p.sha256==TightenParams(**__import__('json').loads(p.canonical())).sha256
    assert p.sha256!=TightenParams(.3,.2).sha256
    with pytest.raises(ValueError):TightenParams(-.1,.2)
    with pytest.raises(ValueError):TightenParams(.1,float('nan'))
