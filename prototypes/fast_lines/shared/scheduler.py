"""S8/X01: cheap, independent coverage scout and explicit dispatch requests."""
import cv2,numpy as np
from .geometry import mask,height_proxy,quantize

def scout(gray,pm,items):
    h,w=gray.shape; mh,mw=pm.shape
    raw=cv2.resize(gray,(mw,mh),interpolation=cv2.INTER_AREA)
    proxy=height_proxy(items,(w,h)); bh=proxy*mh/h
    kernel=quantize(3*bh)|1
    paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((kernel,kernel),np.uint8))
    ink=((paper.astype(float)-raw)/np.maximum(paper,1)>.12).astype(np.uint8)
    cover=mask(items,pm.shape,(w,h)); residual=ink*(1-cover)
    grouped=cv2.morphologyEx(residual,cv2.MORPH_CLOSE,np.ones((1,quantize(2*bh)),np.uint8))
    n,lab,stats,_=cv2.connectedComponentsWithStats(grouped,8)
    regions=[]
    for x,y,rw,rh,area in stats[1:]:
        if rw>=2*bh and .25*bh<=rh<=4*bh and area>=.3*bh*bh:
            regions.append(dict(bbox=[x*w/mw,y*h/mh,(x+rw)*w/mw,(y+rh)*h/mh],reason='independent unexplained image support'))
    reason=['empty detector'] if not items else []
    if regions: reason.append('unexplained ink')
    return dict(regions=regions,reasons=reason,trigger=bool(reason),residual_pixels=int(residual.sum()),sampled_pixels=int(raw.size),height_proxy=proxy)

def dispatch(witnesses):
    """Uncertainty remains a request; no aggregate score certifies a clean page."""
    return ['layout_barriers','font_guides','foreground_profiles','image_motifs','local_ribbons','sheet_lattice','residual_ledger'] if witnesses['trigger'] else ['layout_barriers','local_ribbons']
