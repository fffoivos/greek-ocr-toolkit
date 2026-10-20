"""Reused observations retain current pixels, coordinates and ownership."""
import cv2
import numpy as np
from .ink_photometry import sample_boxes
from .type_lattice import inspect_slot
from .type_context import recover
from .contracts import rect


def test_tones_change_with_pixels_or_sampling_rectangle_and_own_values():
    gray=np.full((100,180),240,np.uint8);gray[20:55,20:80]=80
    boxes=[[10,10,90,65],[100,10,170,65]]
    prepared=sample_boxes(gray,boxes)
    fresh=sample_boxes(gray,list(reversed(boxes)))
    reused=sample_boxes(gray,list(reversed(boxes)),prepared)
    assert np.array_equal(fresh[2],reused[2])
    reused[2][:]=0
    assert prepared[2][0,0]>0
    shifted=[[110,20,170,60]]
    assert np.array_equal(sample_boxes(gray,shifted,prepared)[2],sample_boxes(gray,shifted)[2])
    changed=gray.copy();changed[:]=240
    assert np.array_equal(sample_boxes(changed,boxes,prepared)[2],np.zeros((2,2)))


def slot_page():
    gray=np.full((100,180),255,np.uint8)
    for x in range(15,145,12):cv2.rectangle(gray,(x,36),(x+6,45),0,-1)
    slot=dict(height=10.,y=40.,x0=10.,x1=150.,xref=80.,slope=0.,pitch=25.,neighbours=[])
    return gray,slot


class NoInference:
    def infer(self,*args,**kwargs):raise AssertionError('no supported unowned witness')


def test_dense_negative_reused_but_geometry_and_image_changes_remeasure():
    gray,slot=slot_page();blank=np.full_like(gray,255)
    measured=inspect_slot(blank,slot,[],dense=True,version=3)
    assert not measured['supported']
    coarse=dict(measured,supported=True,owned_fraction=0.)
    result=recover(blank,[],NoInference(),lattice_evidence=dict(slots=[coarse]),dense_slots=(blank,{0:measured}))
    assert result['dense_checks'][0]['reused']
    positive=inspect_slot(gray,slot,[],dense=True,version=3);assert positive['supported']
    moved=dict(positive,y=80.)
    for image,current in [(blank,positive),(gray,moved)]:
        result=recover(image,[],NoInference(),lattice_evidence=dict(slots=[current]),dense_slots=(gray,{0:positive}))
        assert not result['dense_checks'][0]['reused']
        assert not result['dense_checks'][0]['evidence']['supported']


def test_dense_measurement_does_not_reuse_old_polygon_ownership():
    gray,slot=slot_page();dense=inspect_slot(gray,slot,[],dense=True,version=3)
    assert dense['supported'] and dense['owned_fraction']==0
    items=[dict(polygon=rect([0,25,170,55]))]
    result=recover(gray,items,NoInference(),lattice_evidence=dict(slots=[dense]),dense_slots=(gray,{0:dense}))
    assert result['dense_checks'][0]['evidence']['owned_fraction']==1
    assert dense['owned_fraction']==0
    assert not result['added']
