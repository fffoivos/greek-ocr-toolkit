"""A08: area texture and motif correspondences, preserving existing text."""
import cv2,numpy as np
from ..shared.geometry import mask,quantize
from ..shared.image_evidence import components
from ..shared.contracts import result

def run(ctx,phase=3):
    e=ctx.ev; h=e.body; cover=mask(ctx.items,e.shape,ctx.size); residual=e.ink*(1-cover)
    closed=cv2.morphologyEx(residual,cv2.MORPH_CLOSE,np.ones((quantize(2*h),quantize(2*h)),np.uint8))
    labels,stats,_=components(closed); gx,gy=e.gradients; regions=[]; pairs=[]
    for x,y,w,rh,area in stats:
        if w<4*h or rh<4*h: continue
        patch=residual[y:y+rh,x:x+w]; density=float(patch.mean()); dx=gx[y:y+rh,x:x+w]; dy=gy[y:y+rh,x:x+w]
        xx=float(np.sum(dx*dx)); yy=float(np.sum(dy*dy)); xy=float(np.sum(dx*dy)); coherence=float(np.sqrt((xx-yy)**2+4*xy**2)/max(xx+yy,1e-6))
        text_overlap=float(cover[y:y+rh,x:x+w].mean()); texture=density>.1 and coherence<.65 and text_overlap<.15
        # Regional repetition witness displays corresponding windows, never calls repeated glyphs nontext.
        shift=quantize(2*h); repeat=0.
        if w>2*shift:
            a=e.contrast[y:y+rh,x:x+w-shift].ravel(); b=e.contrast[y:y+rh,x+shift:x+w].ravel()
            if a.std()>1e-6 and b.std()>1e-6: repeat=float(np.corrcoef(a,b)[0,1])
        box=[x/e.sx,y/e.sy,(x+w)/e.sx,(y+rh)/e.sy]
        regions.append(dict(bbox=box,density=density,direction_coherence=coherence,text_overlap=text_overlap,repeat=repeat,
                            suppress_new=bool(texture),ownership='possible image texture' if texture else 'unknown',existing_text='preserved'))
        if repeat>.4: pairs.append(dict(bbox=box,shift_page=shift/e.sx,meaning='repeated structure; glyph/ornament unresolved'))
    return result(ctx.items,regions=regions,motif_pairs=pairs,status='new-proposal texture veto only; embedded Paddle text preserved')
