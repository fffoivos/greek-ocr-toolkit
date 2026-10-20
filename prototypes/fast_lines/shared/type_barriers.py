# Reused unchanged from stopped 0b052af; candidate-only R2 verification.
"""Apply existing R2 rule verification to newly recovered regions only."""
import cv2
import numpy as np
from .geometry import roi,quantize
from .image_evidence import runs,components
from ..layout_barriers.fast import verify_rule,corridor_clear,clip_polygon

def protect(gray,item,height):
    p=np.asarray(item['polygon']);lo=p.min(0);hi=p.max(0)
    a,b,c,d=roi([lo[0]-height,lo[1]-5*height,hi[0]+height,hi[1]+5*height],gray.shape)
    g=gray[b:d,a:c]; k=quantize(3*height)|1
    paper=cv2.boxFilter(g,cv2.CV_32F,(k,k))
    ink=(paper-g>255*.06).astype(np.uint8)
    ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((quantize(.4*height),1),np.uint8))
    widened=cv2.dilate(ink,np.ones((1,quantize(.2*height)),np.uint8))
    vertical=runs(widened,6*height,True)
    _,stats,_=components(vertical);polys=[item['polygon']];decisions=[]
    for x,y,w,h,area in stats:
        cx=x+w/2+a
        if w>height or not lo[0]+.5*height<cx<hi[0]-.5*height: continue
        if y+b>lo[1] or y+h+b<hi[1]: continue
        candidate=dict(bbox=[x+a,y+b,x+w+a,y+h+b])
        rule,reason=verify_rule(gray,candidate,height)
        if rule is None:
            decisions.append(dict(bbox=candidate['bbox'],decision='abstain',reason=reason))
            return [],decisions
        ok,density=corridor_clear(gray,item,rule,height)
        if not ok:
            decisions.append(dict(bbox=candidate['bbox'],decision='abstain',reason='ink beside rule',density=density))
            return [],decisions
        # Do not split an existing cell or assume that a short rule denotes prose.
        if min(cx-lo[0],hi[0]-cx)<2*height:
            return [],decisions+[dict(decision='abstain',reason='short text crosses rule')]
        pieces=[]
        for poly in polys:
            l=clip_polygon(poly,rule['slope'],rule['intercept']-.12*height,1)
            r=clip_polygon(poly,rule['slope'],rule['intercept']+.12*height,-1)
            if len(l)>=3 and len(r)>=3: pieces.extend((l,r))
            else: pieces.append(poly)
        polys=pieces;decisions.append(dict(decision='split',rule=rule))
    return [dict(item,polygon=p) for p in polys],decisions
