"""Unroll observed stamp-ring hypotheses; intersections remain explicitly unknown."""
import cv2,numpy as np
from scipy.signal import find_peaks


def render(gray,ring,height,*,route='slow',version=4):
    a,b=np.asarray(ring['diameters'])/2;angle=np.deg2rad(ring['angle']);cx,cy=ring['center']
    scale=1. if route=='slow' else min(1.,16/height) if route=='explicit' else min(1.,8/height)
    theta=np.linspace(0,2*np.pi,max(48,round(2*np.pi*max(a,b)*scale)),endpoint=False)
    radii=np.linspace(.5,1.25,max(12,round(.75*max(a,b)*scale)))
    u=radii[:,None]*a*np.cos(theta);v=radii[:,None]*b*np.sin(theta)
    x=cx+u*np.cos(angle)-v*np.sin(angle);y=cy+u*np.sin(angle)+v*np.cos(angle)
    valid=(x>=0)&(y>=0)&(x<gray.shape[1]-1)&(y<gray.shape[0]-1)
    raw=cv2.remap(gray,x.astype('float32'),y.astype('float32'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
    # Column-local illumination prevents a page shadow being a circular band.
    paper=np.percentile(raw,90,axis=0,keepdims=True);depth=np.maximum(0,paper-raw.astype(float))
    if version>=4:
        # A circular STROKE must be darker than BOTH radial flanks. Darkness
        # relative to a column maximum also selected an annulus of paper grain.
        step=max(1,round(.15*height*scale));f=raw.astype(float)
        diff=np.diff(f,axis=1);noise=max(1/np.sqrt(12),float(1.4826*np.median(abs(diff-np.median(diff)))/np.sqrt(2)))
        bump=np.zeros_like(f);ok=np.zeros_like(valid)
        if 2*step<len(raw):
            bump[step:-step]=np.minimum(f[:-2*step],f[2*step:])-f[step:-step]
            ok[step:-step]=valid[:-2*step]&valid[step:-step]&valid[2*step:]
        if route=='heuristic':
            # Sparse spokes stand in for the angular persistence census.
            ids=np.unique(np.linspace(0,len(theta)-1,24).astype(int));bump=bump[:,ids];ok=ok[:,ids]
        profile=np.sum((bump>max(2,2*noise))&ok,axis=1)/np.maximum(ok.sum(1),1)
    elif version>=2:
        # Ring evidence is angular persistence, not mean depth. One intersecting
        # black word otherwise dominates a faint but continuous circular stroke.
        local=np.percentile(depth,90,axis=0,keepdims=True)
        ink=depth>np.maximum(3,.35*local)
        profile=np.sum(ink&valid,axis=1)/np.maximum(valid.sum(1),1)
    else:profile=np.sum(depth*valid,axis=1)/np.maximum(valid.sum(1),1)
    peaks,_=find_peaks(profile,prominence=.08 if version>=2 else 3,distance=max(1,round(.12*height*scale)))
    return dict(raw=raw,valid=valid,depth=depth,radii=radii,profile=profile,
                rings=[dict(radius_factor=float(radii[i]),support=float(profile[i])) for i in peaks],
                source=ring,scale=scale,route=route,ownership='unknown at every stamp/text intersection',safe_exclusions=[])
