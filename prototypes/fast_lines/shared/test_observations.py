"""Numerical observations preserve pixels and explicit physical distinctions."""
import cv2
import numpy as np
from . import observations as obs
from .local_scale import component_extent


def test_identity_resize_returns_owned_pixels():
    source=np.arange(120,dtype=np.uint8).reshape(10,12)
    result=obs.resize(source,source.shape[::-1]);result[0,0]=255
    assert source[0,0]==0
    assert np.array_equal(result[1:],source[1:])


def test_relative_contrast_at_every_uint8_paper_ink_pair():
    # Closing produces uint8 paper. Exhaust the physical domain, including all
    # exact and nearest representable contacts at the inherited .18 threshold.
    paper,gray=np.meshgrid(np.arange(256,dtype=np.uint8),np.arange(256,dtype=np.uint8))
    delta=paper.astype(np.float32)-gray
    divided=delta/np.maximum(paper,1)>.18
    multiplied=delta>.18*np.maximum(paper,1)
    assert np.array_equal(divided,multiplied)
    # A dark stroke on a fixed paper level reaches the same strict boundary.
    for p in (50,100,150,200,250):
        g=np.full((7,7),p,np.uint8);g[3,3]=p-round(.18*p)
        assert obs.ink(g,7,method='closing',threshold=.18,arithmetic='relative')[3,3]==0
        g[3,3]-=1
        assert obs.ink(g,7,method='closing',threshold=.18,arithmetic='relative')[3,3]==1


def test_absolute_texture_and_relative_contrast_are_distinct():
    g=np.full((19,25),200,np.uint8);g[6:13,10:15]=170
    k=15;p=cv2.boxFilter(g,cv2.CV_32F,(k,k))
    assert np.array_equal(obs.ink(g,k,method='mean',threshold=255*.08,arithmetic='dn'),(p-g>255*.08).astype('uint8'))
    a=obs.paper(g,k,method='closing');a[:]=0
    assert obs.paper(g,k,method='closing').max()==200


def test_local_scale_does_not_invent_body_classes_or_force_large_initials():
    body=component_extent([[0,0,10,20],[14,0,24,22]],compatibility='lower-contact chain')
    initial=component_extent([[0,0,40,95]],compatibility='isolated glyph')
    empty=component_extent([],compatibility='unknown')
    assert body['value_px']==21 and initial['value_px']==95
    assert body['body_height_px'] is None and initial['body_height_px'] is None
    assert body['uncertain'] and initial['uncertain'] and empty['value_px'] is None
