"""Regional printed-rule ownership veto for fragment joins.

Reuses the pixel method in C type_barriers.protect (stopped 0b052af): local ink,
long runs, then Q8 native stroke verification. Joining has a stricter contract:
a rule bordering the row is also an unresolved cell boundary. No rule removal.
"""
import cv2
import numpy as np
from .geometry import roi,quantize
from .image_evidence import runs,components
from ..layout_barriers.fast import verify_rule


def inspect(gray,polygon,height):
    p=np.asarray(polygon);lo=p.min(0);hi=p.max(0)
    a,b,c,d=roi([lo[0]-height,lo[1]-5*height,hi[0]+height,hi[1]+5*height],gray.shape)
    g=gray[b:d,a:c];paper=cv2.boxFilter(g,cv2.CV_32F,(quantize(3*height)|1,quantize(3*height)|1))
    ink=(paper-g>255*.06).astype(np.uint8)
    ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((quantize(.4*height),1),np.uint8))
    widened=cv2.dilate(ink,np.ones((1,quantize(.2*height)),np.uint8))
    _,stats,_=components(runs(widened,6*height,True));records=[]
    for x,y,w,h,area in stats:
        if w>height or y+b>hi[1] or y+h+b<lo[1]:continue
        candidate=dict(bbox=[x+a,y+b,x+w+a,y+h+b]);rule,reason=verify_rule(gray,candidate,height)
        records.append(dict(candidate=candidate,rule=rule,reason=reason or 'printed rule makes row/cell ownership uncertain'))
    return records
