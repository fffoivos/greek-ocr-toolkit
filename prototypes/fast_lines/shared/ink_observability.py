"""Local pixel observability, separate from stroke shape and semantic readability.

No image-only score can identify a lost letter without a shape/context hypothesis.
These products expose noise-relative faintness and threshold topology, never
turning a thick or pale component into an automatic unreadability label.
"""
import cv2,numpy as np
from .geometry import roi


def measure(gray,box,height,*,route='slow',detail=False,version=4):
    if route not in ('slow','explicit','heuristic'):raise ValueError(route)
    x0,y0,x1,y1=roi(box,gray.shape);pad=max(1,round(.4*height))
    xa,ya=max(0,x0-pad),max(0,y0-pad);xb,yb=min(gray.shape[1],x1+pad),min(gray.shape[0],y1+pad)
    native=gray[ya:yb,xa:xb];scale=min(1.,32/height) if route=='explicit' else min(1.,12/height) if route=='heuristic' else 1.
    raw=cv2.resize(native,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA) if scale<1 else native.copy()
    h=height*scale;paper=float(np.percentile(raw,90));f=raw.astype(np.float32)
    # Selecting bright RAW pixels truncates the very noise distribution being
    # measured. V3 selects on a smoothed image, then measures ORIGINAL residuals.
    selection=cv2.GaussianBlur(f,(0,0),max(.5,.1*h)) if version>=3 else f
    bright=selection>=np.percentile(selection,65)
    differences=(f[:,1:]-f[:,:-1])[bright[:,1:]&bright[:,:-1]]
    noise=max(1/np.sqrt(12),float(1.4826*np.median(abs(differences-np.median(differences)))/np.sqrt(2))) if differences.size else 1.
    xx,yy=round((x0-xa)*scale),round((y0-ya)*scale);ww,hh=max(1,round((x1-x0)*scale)),max(1,round((y1-y0)*scale))
    patch=f[yy:yy+hh,xx:xx+ww];depth=np.maximum(0,paper-patch)
    if version>=2:
        # Fit smooth illumination to observed bright pixels. No histogram
        # normalization may turn a shadow slope into a letter's local contrast.
        ys,xs=np.indices(f.shape,dtype=np.float32);xs/=max(f.shape[1]-1,1);ys/=max(f.shape[0]-1,1)
        design=np.stack([np.ones_like(f),xs,ys],-1)
        coef=np.linalg.lstsq(design[bright],f[bright],rcond=None)[0]
        surface=design@coef;localpaper=surface[yy:yy+hh,xx:xx+ww];depth=np.maximum(0,localpaper-patch);paper=float(np.median(localpaper))
    amplitude=float(np.percentile(depth,90)) if depth.size else 0.
    levels=(.25,.5,.75) if route!='heuristic' else (.5,)
    rows=[];masks=[]
    for threshold in levels:
        mask=(depth>max(threshold*amplitude,2*noise)).astype(np.uint8)
        n,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
        significant=sum(s[4]>.003*h*h for s in stats[1:])
        contours,hierarchy=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        holes=sum(v[3]>=0 for v in hierarchy[0]) if hierarchy is not None else 0
        dist=cv2.distanceTransform(mask,cv2.DIST_L2,5);ridge=(dist>0)&(dist>=cv2.dilate(dist,np.ones((3,3),np.uint8)))
        width=float(np.median(2*dist[ridge])/h) if ridge.any() else 0.
        rows.append(dict(level=threshold,components=int(significant),holes=int(holes),width_h=width,fill=float(mask.mean())))
        masks.append(mask)
    certain=depth>4*noise;possible=depth>2*noise
    # Near-threshold topology under the actually observed noise scale, separate
    # from the wider relative-threshold stroke sweep above.
    topology=[]
    for delta in (-2,0,2):
        b=(depth>max(2*noise,.5*amplitude+delta*noise)).astype(np.uint8)
        _,_,stats,_=cv2.connectedComponentsWithStats(b,8)
        cs,hi=cv2.findContours(b,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        topology.append(dict(noise_delta=delta,components=int(sum(s[4]>.003*h*h for s in stats[1:])),holes=int(sum(v[3]>=0 for v in hi[0])) if hi is not None else 0))
    out=dict(bbox=[x0,y0,x1,y1],route=route,scale=scale,noise_dn=noise,depth_dn=amplitude,
             contrast=amplitude/max(paper,1),core_snr=amplitude/noise,
             weak_fraction=float((possible&~certain).sum()/max(possible.sum(),1)),
             thresholds=rows,noise_topology=topology,
             topology_stable=all(r['components']>0 for r in topology) and len({(r['components'],r['holes']) for r in topology})==1,
             readability='unknown',faintness='noise-limited candidate' if amplitude<4*noise else 'core resolved above noise',
             cause='unknown: typography, ink loss, blur and overlap need independent evidence')
    if detail:out.update(raw=patch.astype(np.uint8),masks=masks,certain=certain,possible=possible)
    return out
