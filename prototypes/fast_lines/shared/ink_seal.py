"""Geometric seal evidence: locally traced concentric strokes, not a logo template.

Proposals are not exclusions. Native/reduced paths expose unsupported arcs;
ordinary rows crossing a seal are retained. No page or book identifiers enter.
"""
import cv2
import numpy as np
from time import perf_counter
from .contracts import bbox
from .geometry import roi


def scout(items,height):
    ids=[]
    for i,q in enumerate(items):
        p=np.asarray(q['polygon'],np.float32)
        (_, _),(a,b),angle=cv2.minAreaRect(p)
        if a<b:a,b=b,a;angle+=90
        drift=abs(np.sin(np.deg2rad(angle)))*a
        if height<a<10*height and b<3*height and drift>.5*height:ids.append(i)
    return ids


def trace(gray,center,radius,height,*,route='slow',max_radius=None,early=False):
    """Follow an observed dark radial ridge, with both flanks as local paper."""
    s=1. if route=='slow' else min(1.,12/height) if route=='explicit' else min(1.,6/height)
    n=max(48,round(2*np.pi*radius*s));radial_scale=1. if route in ('slow','explicit') else s
    nr=max(7,round(3*height*radial_scale))
    n=48 if route=='heuristic' else n
    theta=np.linspace(0,2*np.pi,n,endpoint=False);rr=radius+np.linspace(-1.5*height,1.5*height,nr)
    x=center[0]+rr[:,None]*np.cos(theta);y=center[1]+rr[:,None]*np.sin(theta)
    raw=cv2.remap(gray,x.astype('float32'),y.astype('float32'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255).astype('float32')
    valid=(x>=0)&(y>=0)&(x<gray.shape[1]-1)&(y<gray.shape[0]-1)
    k=max(1,round(.18*height*radial_scale));bump=np.zeros_like(raw)
    bump[k:-k]=np.minimum(raw[:-2*k],raw[2*k:])-raw[k:-k]
    # Native gray differences, including paper and ring: a conservative noise floor.
    noise=max(1.,float(np.median(abs(np.diff(raw,axis=1)))/.954))
    reward=np.clip(bump/max(noise,1),-4,12);reward[~valid]=-4
    if max_radius is not None:reward[rr>max_radius]=-1e6
    # An upper bound: even an unconstrained radial path cannot observe these
    # angular columns. Skipping DP here cannot change an accepted ring.
    possible=(valid&(bump>3*noise)).any(0)
    gap=largest=0
    for v in np.r_[possible,possible]:
        gap=0 if v else gap+1;largest=max(largest,gap)
    bound=min(n,largest)*2*np.pi*radius/n/height
    if early and bound>=2:
        return dict(max_gap_h=float(bound),smooth=False,early_negative=True)
    # Two turns avoid privileging one angular starting point. A radial step costs
    # its displacement in sampling units; this keeps letters from pulling a path.
    score=reward[:,0].copy();parents=np.zeros((2*n,nr),np.int16)
    for t in range(1,2*n):
        choices=np.stack([np.r_[-1e6,score[:-1]]-1,score,np.r_[score[1:],-1e6]-1])
        choice=choices.argmax(0);parents[t]=np.arange(nr)+choice-1
        score=choices.max(0)+reward[:,t%n]
    path=np.zeros(2*n,np.int16);path[-1]=score.argmax()
    for t in range(2*n-1,0,-1):path[t-1]=parents[t,path[t]]
    ids=path[n//2:n//2+n];tt=np.arange(n//2,n//2+n)%n
    if route=='heuristic':ids=reward.argmax(0);tt=np.arange(n)
    r=rr[ids];xx=center[0]+r*np.cos(theta[tt]);yy=center[1]+r*np.sin(theta[tt])
    strength=bump[ids,tt];observed=valid[ids,tt]&(strength>3*noise)
    gap=0;largest=0
    for v in np.r_[observed,observed]:
        gap=0 if v else gap+1;largest=max(largest,gap)
    missing_h=min(n,largest)*2*np.pi*radius/n/height
    xy=np.c_[xx,yy].astype('float32')
    ellipse=cv2.fitEllipse(xy);(ex,ey),(ea,eb),angle=ellipse
    uv=xy-[ex,ey];ca=np.cos(np.deg2rad(angle));sa=np.sin(np.deg2rad(angle))
    er=np.hypot((uv[:,0]*ca+uv[:,1]*sa)/(ea/2),(-uv[:,0]*sa+uv[:,1]*ca)/(eb/2))
    residual=float(np.sqrt(np.mean(((er-1)*min(ea,eb)/2)**2)))
    widths=[]
    for j,k0 in enumerate(ids):
        if not observed[j]:continue
        col=tt[j];cut=bump[k0,col]/2;lo=hi=int(k0)
        while lo>0 and bump[lo-1,col]>cut:lo-=1
        while hi+1<nr and bump[hi+1,col]>cut:hi+=1
        widths.append((hi-lo+1)*(rr[1]-rr[0]))
    width=float(np.median(widths)) if widths else 0.
    return dict(ellipse=[list(ellipse[0]),list(ellipse[1]),angle],fit_rms=residual,stroke_width=width,
                smooth=residual<=width,path=xy.tolist(),strength=strength.tolist(),observed=observed.tolist(),
                max_gap_h=float(missing_h),noise_dn=noise,radius=float(np.median(r)),raw=raw.astype('uint8'),
                radial_path=ids.tolist(),angle_order=tt.tolist(),scale=s)


def render(gray,items,height,*,route='slow',detail=False,candidate_indices=None):
    t=perf_counter();ids=scout(items,height)
    if candidate_indices is not None:ids=[i for i in ids if i in candidate_indices]
    ts=perf_counter()-t;rings=[];proposals=[]
    scale=min(1.,8/height)
    for i in ids:
        b=bbox(items[i]);cx,cy=(b[0]+b[2])/2,(b[1]+b[3])/2
        region=roi([cx-14*height,cy-14*height,cx+14*height,cy+14*height],gray.shape)
        if any(np.linalg.norm(np.array([cx,cy])-q['center'])<q['outer']['radius']+2*height for q in rings):continue
        if any(np.linalg.norm(np.array([cx,cy])-q['candidate_center'])<4*height for q in proposals):continue
        x0,y0,x1,y1=region;raw=cv2.resize(gray[y0:y1,x0:x1],None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
        # Proposal settings in the 8-pixel/body image, inherited from R5.
        # param1=40 is the high Sobel/Canny gradient threshold (low=20);
        # param2=28 is the centre-accumulator vote threshold. Neither is
        # a physical ownership criterion or a calibrated probability. Their
        # original numerical selection was not documented: recall sensitivity
        # remains open. Only the subsequent noise-relative native radial path,
        # stroke-width fit and polygon-contained rim ink authorize removal.
        circles=cv2.HoughCircles(raw,cv2.HOUGH_GRADIENT,1,4*height*scale,param1=40,param2=28,minRadius=round(3*height*scale),maxRadius=round(12*height*scale))
        cand=[]
        for x,y,r in ([] if circles is None else circles[0]):
            center=[float(x/scale+x0),float(y/scale+y0)];radius=float(r/scale)
            # Candidate lettering must be near the proposed circumference.
            distance=np.linalg.norm(np.array([cx,cy])-center)
            if abs(distance-radius)>2*height:continue
            if any(np.linalg.norm(np.array(center)-z['center'])<height for z in rings):continue
            a=trace(gray,center,radius,height,route=route,early=not detail)
            # Only observed closed strokes nominate a second independent ring.
            if a['max_gap_h']<2 and a['smooth']:
                d=trace(gray,center,a['radius']-height,height,route=route,max_radius=a['radius']-.4*height) if detail else None
                cand.append(dict(center=center,initial_radius=radius,outer=a,inner=d,line=i))
                rings.append(cand[-1])
            if cand:break
        proposals.append(dict(line=i,candidate_center=[cx,cy],roi=region,rings=len(cand),hough_candidates=0 if circles is None else len(circles[0])))
    decisions=classify(gray,items,height,rings,candidate_indices if candidate_indices is not None else ids)
    out=dict(candidates=ids,proposals=proposals,rings=rings,decisions=decisions,suppress_indices=[d['line'] for d in decisions],scout_s=ts,seconds=perf_counter()-t)
    if not detail:
        for r in rings:
            for k in ('outer','inner'):
                if r[k] is not None:r[k].pop('raw',None)
    return out


def classify(gray,items,height,rings,candidate_indices):
    decisions=[]
    # Only the independently nominated weak-ink boxes can be assigned to the rim.
    # Ring interior and all ordinary long rows remain unknown and retained.
    for i in candidate_indices:
        q=items[i];p=np.asarray(q['polygon'],np.float32);(cx,cy),(a,b),angle=cv2.minAreaRect(p)
        if a<b:a,b=b,a;angle+=90
        if not (height<a<10*height and b<3*height):continue
        for j,r in enumerate(rings):
            (ex,ey),(ea,eb),ang=r['outer']['ellipse'];ca=np.cos(np.deg2rad(ang));sa=np.sin(np.deg2rad(ang))
            bx0,by0,bx1,by1=roi(bbox(q),gray.shape);crop=gray[by0:by1,bx0:bx1]
            paper,core=np.percentile(crop,[90,10]);mask=(crop<paper-.5*(paper-core)).astype('uint8')
            inside=np.zeros(crop.shape,np.uint8);cv2.fillPoly(inside,[np.rint(p-[bx0,by0]).astype('int32')],1)
            n,lab,stats,_=cv2.connectedComponentsWithStats(mask&inside,8)
            accepted=[z for z in range(1,n) if stats[z,4]>.025*height*height]
            ys,xs=np.nonzero(np.isin(lab,accepted))
            if not len(xs):continue
            uv=np.c_[xs+bx0,ys+by0]-[ex,ey];rho=np.hypot((uv[:,0]*ca+uv[:,1]*sa)/(ea/2),(-uv[:,0]*sa+uv[:,1]*ca)/(eb/2))
            distance=(rho-1)*min(ea,eb)/2
            center=np.array([cx-ex,cy-ey]);axis=np.array([np.cos(np.deg2rad(angle)),np.sin(np.deg2rad(angle))])
            radial_drift=abs(float(center@axis))/max(np.linalg.norm(center),1)*a
            if distance.min()>-2.5*height and distance.max()<.5*height and radial_drift<height:
                decisions.append(dict(line=i,ring=j,reason='weak compact lettering tangent to an observed smooth seal rim',radial_range_h=(distance/height).tolist(),radial_drift_h=radial_drift/height))
                break
    return decisions
