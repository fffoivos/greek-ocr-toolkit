"""Native-support reuse must preserve changing ownership and valid geometry."""
import cv2
import numpy as np
import pytest
from shapely.errors import GEOSException
from shapely.geometry import Polygon
from .contracts import rect
from .geometry_feature_correct import retention, retention_ink
from . import ink_faintness, ink_faint_scout


def test_source_ink_reuses_pixels_but_not_candidate_or_neighbor_ownership():
    gray=np.full((80,160),240,np.uint8)
    gray[25:40,25:130]=20
    old=dict(polygon=rect([10,10,145,55]))
    smaller=rect([10,10,60,55])
    source=retention_ink(gray,old,12)
    assert not source[3].flags.writeable
    before=retention(gray,[old],0,smaller,12,prepared=source)
    assert before['lost_ink']>0
    neighbor=dict(polygon=rect([59,10,145,55]))
    assert retention(gray,[old,neighbor],0,smaller,12,prepared=source)['lost_ink']==0
    assert retention(gray,[old],0,old['polygon'],12,prepared=source)['lost_ink']==0
    assert retention(gray,[old],0,smaller,12,prepared=source)==before
    for changed, item, height in [(np.full_like(gray,240),old,12),
                                 (gray,dict(polygon=rect([15,10,140,54])),12),
                                 (gray,old,18)]:
        assert retention(changed,[item],0,smaller,height,prepared=source)==retention(changed,[item],0,smaller,height)


def test_full_strip_intersection_valid_empty_and_invalid(monkeypatch):
    gray=np.full((50,80),240,np.uint8)
    monkeypatch.setattr(ink_faint_scout,'render',lambda g,qs,h:dict(
        candidate_indices=list(range(len(qs))),regions=[dict(core=.5) for q in qs],seconds=0))
    component=dict(bbox=[15,15,20,25],body=True,core=.5,peak=.5,noise=0,
                   stroke=1.,area=40.,clipped=False)
    monkeypatch.setattr(ink_faintness,'components',lambda g,q,*a,**k:[dict(component,bbox=list(component['bbox']),input_valid=Polygon(q['polygon']).is_valid)])
    q=dict(polygon=rect([10,10,30,30]))
    r=ink_faintness.analyze(gray,[q],height=10,detail=True)
    assert len(r['calibration'])==1
    candidate=r['regions'][0]['components'][0]
    calibration=r['calibration'][0]['components'][0]
    assert candidate is not calibration and candidate['bbox'] is not calibration['bbox']
    candidate['bbox'][0]=-1
    assert calibration['bbox'][0]==15
    degenerate=dict(polygon=[[10,10],[20,20],[30,30]])
    assert not ink_faintness.analyze(gray,[degenerate],height=10,detail=True)['calibration']
    crossing=dict(polygon=[[10,10],[30,30],[30,10],[10,30]])
    with pytest.raises(GEOSException):
        ink_faintness.analyze(gray,[crossing],height=10,detail=True)

    spike=dict(polygon=[[10,10],[30,10],[30,30],[20,30],[20,20],[20,30],[10,30]])
    normalized=ink_faintness.analyze(gray,[spike],height=10,detail=True)
    assert not normalized['regions'][0]['components'][0]['input_valid']
    assert normalized['calibration'][0]['components'][0]['input_valid']
