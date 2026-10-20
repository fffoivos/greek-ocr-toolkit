"""Source authority and requested-region contracts, including the removed policy."""
import numpy as np
import pytest
from . import ink_ownership as own
from ..features_ink.pipeline import ink_run


def test_nearby_mirrored_rows_cannot_certify_an_unknown_region(monkeypatch):
    gray=np.full((100,200),240,np.uint8)
    items=[dict(polygon=[[0,y],[100,y],[100,y+8],[0,y+8]]) for y in (0,10,20,40,50,60)]
    # Strong rows supply a same-page atlas; three neighboring weak requested
    # rectangles have identical photometry. The middle one's shapes give no
    # handedness evidence. Old propagation assigned it back from its neighbors.
    def samples(g,boxes,previous=None):
        values=np.array([[.8,.8,240] if b[1]<30 else [.1,.1,240] for b in boxes])
        return g,boxes,values
    monkeypatch.setattr(own,'sample_boxes',samples)
    monkeypatch.setattr(own,'glyphs',lambda g,b,h,limit,**kw: [dict(bbox=b,tile=np.zeros((2,2)),vector=np.zeros(484),aspect=1.,y=b[1])])
    def matches(query,atlas):
        return [] if query[0]['y']==50 else [dict(direct=.1,reflected=.95,margin=.85) for _ in range(4)]
    monkeypatch.setattr(own,'match_glyphs',matches)
    r=own.analyze(gray,items,height=5)
    assert r['suppress_indices']==[3,5]
    assert r['regions'][4]['ownership']=='unknown'
    assert 'supporters' not in r['regions'][4]
    requested=[[0,60,100,68],[0,50,100,58],[0,40,100,48]]
    rr=own.analyze(gray,items,regions=requested,height=5)
    assert rr['suppress_indices']==[0,2]  # requested order, not item order
    assert rr['regions'][1]['ownership']=='unknown'


def test_old_propagated_source_record_cannot_reenter_ink_run():
    gray=np.full((50,100),240,np.uint8)
    q=dict(polygon=[[5,10],[95,10],[95,30],[5,30]])
    with pytest.raises(ValueError,match='source policy'):
        ink_run(gray,[q],ownership_evidence=dict(version='B4'))
