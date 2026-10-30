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
            # A nomination is not a separator certificate. Retain only the
            # independently witnessed side; the nominated corridor stays unknown.
            # Use the recovery caller's body-chain contract, not a majority vote.
            from .type_residual_recovery import piece_support,supported_extent
            from .type_lattice import point_ownership
            points=np.asarray(item.get('type_witness_points',[]),float).reshape(-1,2)
            surviving=[];sides=[]
            for poly in polys:
                current=dict(item,polygon=poly)
                here=points[np.asarray(point_ownership(points,[current]),bool)]
                if not len(here):continue
                left=clip_polygon(poly,0.,candidate['bbox'][0]-.12*height,1)
                right=clip_polygon(poly,0.,candidate['bbox'][2]+.12*height,-1)
                supported=[(side,p) for side,p in [('left',left),('right',right)]
                           if len(p)>=3 and piece_support(dict(item,polygon=p),here,[],height)]
                if len(supported)==1:
                    side,p=supported[0]
                    piece=dict(item,polygon=p)
                    try:bounds=np.asarray(item.get('type_support_bounds',[]))
                    except (TypeError,ValueError):bounds=np.array([])
                    if bounds.shape==(2,) and bounds.dtype.kind in 'iuf' and np.isfinite(bounds).all() and bounds[0]<bounds[1]:
                        piece=supported_extent(piece)
                        if piece is None or not piece_support(piece,here,[],height):continue
                    surviving.append(piece['polygon']);sides.append(side)
            decisions.append(dict(bbox=candidate['bbox'],decision='local unknown' if surviving else 'abstain',
                                  reason=reason,retained_sides=sides))
            polys=surviving
            if not polys:return [],decisions
            continue
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
