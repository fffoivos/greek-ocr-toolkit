"""Contour-fitted concentric-ring evidence; S1 diagnostic, no blanket image eraser."""
import cv2,numpy as np
from .geometry import roi,quantize
from .contracts import bbox


def inspect(gray,box,height):
    b=np.array(box);center=(b[:2]+b[2:])/2
    x0,y0,x1,y1=roi([center[0]-9*height,center[1]-9*height,center[0]+9*height,center[1]+9*height],gray.shape)
    crop=gray[y0:y1,x0:x1];s=min(1.,16/height)
    raw=cv2.resize(crop,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    low,high=map(float,np.percentile(raw,[10,90]));contrast=max(8,high-low)
    edges=cv2.Canny(raw,contrast*.25,contrast*.75)
    contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    dist=cv2.distanceTransform(1-(edges>0).astype(np.uint8),cv2.DIST_L2,3)
    rings=[]
    for c in contours:
        if len(c)<4*height*s:continue
        (cx,cy),(a,d),angle=cv2.fitEllipse(c)
        if not (3*height*s<min(a,d)<max(a,d)<17*height*s and min(a,d)/max(a,d)>.55):continue
        theta=np.linspace(0,2*np.pi,180,endpoint=False);ang=np.deg2rad(angle)
        xx=cx+.5*a*np.cos(theta)*np.cos(ang)-.5*d*np.sin(theta)*np.sin(ang)
        yy=cy+.5*a*np.cos(theta)*np.sin(ang)+.5*d*np.sin(theta)*np.cos(ang)
        valid=(xx>=0)&(yy>=0)&(xx<raw.shape[1]-1)&(yy<raw.shape[0]-1)
        if valid.mean()<.6:continue
        # Verify actual edge support around the whole ellipse, not fit quality alone.
        ds=cv2.remap(dist,xx.astype(np.float32)[None],yy.astype(np.float32)[None],cv2.INTER_LINEAR)[0]
        support=float((ds[valid]<.10*height*s).mean())
        if support<.8:continue
        ring=dict(center=[cx/s+x0,cy/s+y0],diameters=[a/s,d/s],angle=angle,support=support)
        if any(np.linalg.norm(np.array(r['center'])-ring['center'])<.15*height and max(abs(np.array(r['diameters'])-[a/s,d/s]))<.15*height for r in rings):continue
        radial=[]
        for factor in np.linspace(.7,1.22,53):
            rx=cx+(xx-cx)*factor;ry=cy+(yy-cy)*factor
            valid=(rx>=0)&(ry>=0)&(rx<raw.shape[1]-1)&(ry<raw.shape[0]-1)
            if valid.mean()<.6:radial.append(0.);continue
            ds=cv2.remap(dist,rx.astype(np.float32)[None],ry.astype(np.float32)[None],cv2.INTER_LINEAR)[0]
            radial.append(float((ds[valid]<.08*height*s).mean()))
        from scipy.signal import find_peaks
        peaks,_=find_peaks(radial,height=.8,prominence=.08,distance=4)
        ring['radial_peaks']=[dict(factor=float(.7+k*.01),support=radial[k]) for k in peaks]
        rings.append(ring)
    pairs=[]
    for i,a in enumerate(rings):
        for j,d in enumerate(rings[:i]):
            same=np.linalg.norm(np.array(a['center'])-d['center'])<.35*height
            ratios=np.array(a['diameters'])/d['diameters']
            ratio=float(ratios.mean())
            if same and max(abs(ratios-ratio))<.08 and (.75<ratio<.97 or 1.03<ratio<1.33):pairs.append([i,j])
    return dict(bbox=list(box),rings=rings,pairs=pairs,roi=[x0,y0,x1,y1])


def radial_coordinates(xs,ys,ring):
    angle=np.deg2rad(ring['angle']);x=xs-ring['center'][0];y=ys-ring['center'][1]
    u=x*np.cos(angle)+y*np.sin(angle);v=-x*np.sin(angle)+y*np.cos(angle)
    return np.hypot(u/(ring['diameters'][0]/2),v/(ring['diameters'][1]/2))


def analyze(gray,items):
    from time import perf_counter
    from .geometry import height_proxy
    from .ink_photometry import tone
    t=perf_counter();h=height_proxy(items,(gray.shape[1],gray.shape[0]));boxes=[bbox(q) for q in items]
    tones=np.array([tone(gray,b) for b in boxes]);high=float(np.percentile(tones,80)) if len(tones) else 0.
    ids=[i for i,b in enumerate(boxes) if b[2]-b[0]<8*h and tones[i]<.8*high]
    ts=perf_counter()-t;rings=[];evidence=[]
    for i in ids:
        ev=inspect(gray,boxes[i],h);ev['line']=i;evidence.append(ev)
        for ring in ev['rings']:
            peaks=ring['radial_peaks']
            if len(peaks)>=2 and max(q['factor'] for q in peaks)-min(q['factor'] for q in peaks)>.15:
                rings.append(ring)
    decisions=[]
    for i in ids:
        b=boxes[i];x0,y0,x1,y1=roi(b,gray.shape);crop=gray[y0:y1,x0:x1]
        paper=float(np.percentile(crop,90));dark=(paper-crop.astype(float))/max(paper,1)
        ys,xs=np.nonzero(dark>.06)
        if not len(xs):continue
        for ring in rings:
            r=radial_coordinates(xs+x0,ys+y0,ring)
            annulus=float(((r>.65)&(r<1.12)).mean())
            if annulus<.9:continue
            # Strong dark foreground islands veto a pale seal-only decision.
            core=float(np.percentile(dark,98))
            if core>.7*high:continue
            decisions.append(dict(line=i,reason='faint compact ink in verified concentric outer stamp annulus',
                    annulus_fraction=annulus,ring=ring,core=core))
            break
    return dict(suppress_indices=[r['line'] for r in decisions],decisions=decisions,rings=rings,
                candidates=ids,evidence=evidence,scout_s=ts,seconds=perf_counter()-t)
