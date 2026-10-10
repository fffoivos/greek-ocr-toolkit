"""A07: adaptive local profile families; only evidence-supported guide modes."""
import numpy as np
from scipy.signal import find_peaks
from ..shared.geometry import sample_strip
from ..shared.contracts import bbox,result

def run(ctx,phase=3):
    lines=[]; families=[]; paths=[]; refs={q['id']:q for q in ctx.reference.get('lines',[])}
    for i,item in enumerate(ctx.items):
        b=bbox(item); h=max(ctx.height*.5,min((b[3]-b[1])*.5,ctx.height*2))
        strip,x,y,o=sample_strip(ctx.ev.contrast,item,ctx.size,h,nx=25,ny=61,extend=0)
        p=strip.mean(1); p/=max(float(p.max()),1e-6)
        active=np.flatnonzero(p>.3); measured=float(o[active[-1]]-o[active[0]]) if len(active)>1 else h
        # Families stay in a local block and must agree in scale AND profile.
        block=int((b[0]+b[2])/2/ctx.size[0]*4)
        compatible=[f for f in families if f['block']==block and abs(np.log(max(measured,1e-6)/max(f['height'],1e-6)))<.25 and np.mean(abs(p-np.asarray(f['profile'])))<.14]
        if compatible:
            f=min(compatible,key=lambda f:np.mean(abs(p-np.asarray(f['profile'])))); provenance='borrowed with profile residual check'
            f['members'].append(i)
        else:
            peaks,_=find_peaks(p,prominence=.12,distance=5)
            f=dict(id=len(families),block=block,members=[i],height=measured,profile=p.tolist(),guide_modes=[dict(offset_h=float(o[k]/h),support=float(p[k]),meaning='unidentified density mode') for k in peaks])
            families.append(f); provenance='measured exemplar'
        guides=[]
        if len(active)>1:
            for k in (active[0],active[-1]):
                path=np.c_[x,y+o[k]].tolist(); paths.append(path); guides.append(path)
        ref=refs.get(i); err=float(np.mean(abs(p-np.interp(np.linspace(0,1,61),np.linspace(0,1,81),ref['profile'])))) if ref else None
        lines.append(dict(line=i,bbox=b,family=f['id'],height_interval=[measured*.8,measured*1.2],provenance=provenance,
                          guide_modes=f['guide_modes'],extent_guides=guides,baseline=None,dense_profile_mae=err))
    return result(ctx.items,families=families,lines=lines,paths=paths,regions=[],status='adaptive density guides; baseline/accents not identified semantically')
