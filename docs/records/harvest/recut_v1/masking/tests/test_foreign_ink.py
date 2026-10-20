import sys
from pathlib import Path
import numpy as np
from PIL import Image
import pytest
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from greekocr.glyphs.foreign_ink import mask_foreign_ink,mask_detected_line,prepare_mask_page,_centre_fit,_foreign_mask
from greekocr.glyphs.components import EIGHT
from greekocr.pages.lines import LineSegment


def line(centre,width=240):
    base=np.full(width,centre+10.)
    return LineSegment(0,width,base,base-30,base-20,base+12,base-45,base+25,20.)


def fixture():
    bg=np.broadcast_to((225+np.arange(240)%9)[None,:],(260,240)).astype(np.uint8).copy()
    upper,own,lower=line(80),line(140),line(200)
    bg[70:90,20:35]=25;bg[90:119,28:33]=25 # upper body's descender
    bg[130:150,55:75]=25;bg[150:167,68:73]=25 # own body + descender
    bg[111:115,58:63]=25 # own detached accent / breathing
    bg[116:121,208:212]=25 # own apostrophe / coronis near right end
    bg[155:160,85:89]=25 # own iota subscript
    bg[143:149,225:230]=25 # own punctuation near right end
    bg[174:178,105:110]=25 # lower line's high accent
    bg[190:210,105:125]=25
    return Image.fromarray(bg),own,[upper,own,lower]


def test_own_accents_breathings_descenders_apostrophe_coronis_iota_end_punctuation():
    page,own,neighbours=fixture()
    result=mask_foreign_ink(page,own,neighbours,(0,100,240,181))
    original=np.asarray(page)[100:181]
    for sy,sx in [(slice(11,15),slice(58,63)),(slice(16,21),slice(208,212)),
                  (slice(30,67),slice(55,75)),(slice(55,60),slice(85,89)),
                  (slice(43,49),slice(225,230))]:
        assert not result.mask[sy,sx].any()
        assert np.array_equal(np.asarray(result.image)[sy,sx],original[sy,sx])
    assert result.mask[0:19,28:33].all()
    assert result.mask[74:78,105:110].all()


def test_touching_two_bodies_uses_existing_midline():
    page,own,neighbours=fixture();arr=np.array(page);arr[80:145,145:149]=25
    result=mask_foreign_ink(Image.fromarray(arr),own,neighbours,(0,80,240,170))
    assert result.mask[:31,145:149].all() # rows <= (80+140)/2
    assert not result.mask[31:65,145:149].any()


def test_native_pixels_ring_statistic_and_no_mutation():
    page,own,neighbours=fixture();before=np.array(page);prepared=prepare_mask_page(page)
    result=mask_foreign_ink(prepared,own,neighbours,(0,100,240,181))
    assert result.image.size==(240,81) and result.image.mode==page.mode
    assert np.array_equal(np.asarray(page),before)
    assert np.array_equal(np.asarray(result.image)[~result.mask],before[100:181][~result.mask])
    assert result.record['masked_pixel_count']==int(result.mask.sum())
    for r in result.record['fills']:
        component=prepared.labels==r['component_id']
        ring=ndi.binary_dilation(component,structure=EIGHT,iterations=3)&~ndi.binary_dilation(component,structure=EIGHT,iterations=1)&~prepared.ink
        assert r['ring_median']==np.median(before[ring]).tolist()
        assert r['ring_spread']==(np.percentile(before[ring],90)-np.percentile(before[ring],10)).tolist()
        assert r['fill']<255


def test_exact_training_runtime_adapter_equivalence_and_prepared_raw_identity():
    page,own,neighbours=fixture();box=(0,100,240,181)
    a=mask_foreign_ink(page,own,neighbours,box)
    b=mask_detected_line(prepare_mask_page(page),own,neighbours,box)
    assert np.array_equal(a.mask,b.mask) and a.record==b.record
    assert np.array_equal(np.asarray(a.image),np.asarray(b.image))
    assert mask_detected_line(page,own,neighbours).record['crop_box']==[0,105,240,175]


def test_curved_integer_translation_is_exact_for_equivalent_curves():
    page,own,neighbours=fixture()
    for n in neighbours:
        bend=np.round(2*np.sin(np.arange(240)/35))
        for key in ('baseline','meanline','font_top','font_bottom','top','bottom'):
            setattr(n,key,getattr(n,key)+bend)
    records=[dict(x0=n.x0,x1=n.x1,xheight=n.xheight,baseline=n.baseline.tolist(),meanline=n.meanline.tolist()) for n in neighbours]
    a=mask_foreign_ink(page,own,neighbours,(0,100,240,181))
    b=mask_foreign_ink(page,records[1],records,(0,100,240,181))
    assert np.array_equal(a.mask,b.mask)


def test_no_neighbours_is_identity_and_colour_channels_preserved():
    page,own,_=fixture();arr=np.array(page);rgb=np.stack([arr,arr-2,arr-4],axis=2)
    result=mask_foreign_ink(Image.fromarray(rgb),own,[],(0,100,240,181))
    assert not result.mask.any()
    assert np.array_equal(np.asarray(result.image),rgb[100:181])


def test_detached_mark_nearest_wrong_line_is_a_safety_counterexample():
    # The fixed existing rule has no semantic attachment tolerance. A high own
    # accent at y=106 is closer to centre 80 than 140 and WILL be erased. This
    # characterization deliberately prevents claiming a universal safety proof.
    page,own,neighbours=fixture();arr=np.array(page);arr[105:108,165:170]=25
    result=mask_foreign_ink(Image.fromarray(arr),own,neighbours,(0,100,240,181))
    assert result.mask[5:8,165:170].all()


@pytest.mark.parametrize('box',[(0,-1,240,180),(0,100,241,180),(0.,100,240,180),(0,100,0,180)])
def test_invalid_rectangles_rejected(box):
    page,own,neighbours=fixture()
    with pytest.raises(ValueError):mask_foreign_ink(page,own,neighbours,box)
