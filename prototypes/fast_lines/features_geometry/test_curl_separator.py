"""Local unknowns exercise the unchanged recovery body-chain contract."""
import cv2
import numpy as np
import pytest
from ..shared import type_barriers as barriers
from ..shared.contracts import rect, bbox
from ..shared.type_residual_recovery import piece_support
from ..shared.geometry_bands import crop_mask


def nomination(monkeypatch, bounds):
    stats=np.asarray([[x,y,z-x,w-y,(z-x)*(w-y)] for x,y,z,w in bounds],np.int32)
    monkeypatch.setattr(barriers,'components',lambda mask:(None,stats,None))


def sample(points):
    gray=np.full((240,600),255,np.uint8)
    for x,y in points:cv2.rectangle(gray,(round(x)-3,round(y)-8),(round(x)+3,round(y)+8),30,-1)
    q=dict(polygon=rect([20,65,580,105]),type_witness_points=points)
    return gray,q


@pytest.mark.parametrize('points',[[],[[x,85] for x in range(40,261,40)]+[[x,85] for x in range(340,561,40)]])
def test_unknown_without_unique_supported_side_abstains(monkeypatch,points):
    gray,q=sample(points);nomination(monkeypatch,[[298,0,302,230]])
    pieces,decisions=barriers.protect(gray,q,20)
    assert not pieces and decisions[0]['decision']=='abstain'


def test_supported_chain_beats_an_unsupported_majority(monkeypatch):
    left=[[x,85] for x in range(40,261,40)];cluster=[[350+i,85] for i in range(20)]
    gray,q=sample(left+cluster);nomination(monkeypatch,[[298,0,302,230]])
    pieces,decisions=barriers.protect(gray,q,20)
    assert len(pieces)==1 and decisions[0]['retained_sides']==['left']
    assert piece_support(pieces[0],left,[],20)
    mask=crop_mask(gray.shape,pieces[0])>0
    assert all(mask[y,x] for x,y in left)
    assert not any(mask[y,x] for x,y in cluster)


def test_successive_unknowns_use_only_surviving_domain(monkeypatch):
    cluster=[[50+i,85] for i in range(20)];chain=[[x,85] for x in range(220,521,40)]
    gray,q=sample(cluster+chain);nomination(monkeypatch,[[178,0,182,230],[88,0,92,230]])
    pieces,decisions=barriers.protect(gray,q,20)
    assert len(pieces)==1 and bbox(pieces[0])[0]>182
    assert all(d['retained_sides']==['right'] for d in decisions)
    assert piece_support(pieces[0],chain,[],20)


@pytest.mark.parametrize('mode',['rule','beside','short'])
def test_verified_separator_controls_unchanged(monkeypatch,mode):
    gray=np.full((240,600),255,np.uint8);cv2.line(gray,(300,0),(300,239),25,2)
    q=dict(polygon=rect([280 if mode=='short' else 20,65,580,105]),type_witness_points=[])
    if mode=='beside':cv2.rectangle(gray,(289,65),(311,105),25,-1)
    nomination(monkeypatch,[[38,0,42,240] if mode=='short' else [298,0,302,240]])
    pieces,decisions=barriers.protect(gray,q,20)
    if mode=='rule':
        assert len(pieces)==2 and decisions[0]['decision']=='split'
        assert not (crop_mask(gray.shape,pieces[0])[:,300]>0).any()
        assert not (crop_mask(gray.shape,pieces[1])[:,300]>0).any()
    else:
        assert not pieces
        assert decisions[-1]['reason']==('ink beside rule' if mode=='beside' else 'short text crosses rule')
