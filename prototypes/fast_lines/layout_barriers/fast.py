"""Conditional A02: run witnesses, original-pixel rules, polygon-preserving cuts.

The algorithm receives pixels and Paddle items only, never names or cohort labels.
All geometric lengths use the shared provisional body-height estimate. It neither
certifies a page clean nor attempts missing-text or foreground ownership.
"""
from time import perf_counter
import cv2
import numpy as np
from ..shared.geometry import height_proxy, quantize, roi, robust_fit
from ..shared.image_evidence import runs, components
from ..shared.contracts import bbox


def scout(gray, items):
    start=perf_counter()
    H,W=gray.shape
    height=height_proxy(items,(W,H))
    scale=min(1.,12/height,1200/max(H,W))
    w,h=quantize(W*scale),quantize(H*scale)
    sx,sy=w/W,h/H
    # Integer area kernels are substantially cheaper than a large arbitrary ratio.
    step=max(1,2**int(np.floor(np.log2(1/scale))))
    ch,cw=(H//step)*step,(W//step)*step
    reduced=cv2.resize(gray[:ch,:cw],(cw//step,ch//step),interpolation=cv2.INTER_AREA)
    small=cv2.resize(reduced,(w,h),interpolation=cv2.INTER_AREA)
    sx,sy=w/cw,h/ch
    body=height*sy
    # Local mean, not a page darkness reference; no foreground classification.
    paper=cv2.boxFilter(small,cv2.CV_32F,(quantize(3*body)|1,quantize(3*body)|1))
    ink=(paper-small>255*.06).astype(np.uint8)
    ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((quantize(.5*body),1),np.uint8))
    tolerance=quantize(.6*body)
    widened=cv2.dilate(ink,np.ones((1,tolerance),np.uint8))
    vertical=runs(widened,12*body,True)
    _,stats,_=components(vertical)
    bounds=np.asarray([bbox(q) for q in items],float).reshape(-1,4)
    candidates=[]
    for x,y,rw,rh,area in stats:
        if rh<12*body or rw>2*body:
            continue
        cx=(x+rw/2)/sx
        crossed=np.flatnonzero((bounds[:,0]+6*height<cx)&(cx<bounds[:,2]-6*height)&
                              (bounds[:,1]>=y/sy)&(bounds[:,3]<=(y+rh)/sy))
        if len(crossed)>=3:
            candidates.append(dict(bbox=[x/sx,y/sy,(x+rw)/sx,(y+rh)/sy],lines=crossed.tolist()))
    return dict(candidates=candidates,height=height,shape=[h,w],seconds=perf_counter()-start,
                vertical_components=stats.tolist(),
                status='empty detector unresolved' if not items else 'rule crossings only'), (ink,sx,sy)


def clip_polygon(polygon, slope, intercept, side):
    """Sutherland-Hodgman clipping against a slanted half-plane."""
    points=np.asarray(polygon,float)
    result=[]
    for a,b in zip(points,np.roll(points,-1,axis=0)):
        da=side*(a[0]-slope*a[1]-intercept)
        db=side*(b[0]-slope*b[1]-intercept)
        if da<=0:
            result.append(a.tolist())
        if (da<0<db) or (db<0<da):
            result.append((a+(b-a)*da/(da-db)).tolist())
    return result


def verify_rule(gray, candidate, height):
    x0,y0,x1,y1=roi(candidate['bbox'],gray.shape)
    x0=max(0,int(x0-height)); x1=min(gray.shape[1],int(x1+height))
    crop=gray[y0:y1,x0:x1]
    # The slow explicit reference used Hough on independent paper-normalised ink.
    # This bounded verifier follows the darkest stroke in the nominated corridor.
    cx=(candidate['bbox'][0]+candidate['bbox'][2])/2
    a=max(0,int(cx-x0-.65*height)); b=min(crop.shape[1],int(cx-x0+.65*height)+1)
    if b<=a or not crop.size:
        return None, 'empty support'
    local=crop[:,a:b].astype(np.float32)
    paper=np.percentile(crop,85,axis=1)
    strength=(paper[:,None]-local)/np.maximum(paper[:,None],1)
    sustained=cv2.boxFilter(strength,cv2.CV_32F,(1,quantize(2*height)))
    ids=np.argmax(sustained,axis=1)
    contrast=(paper-local[np.arange(len(ids)),ids])/np.maximum(paper,1)
    good=contrast>.12
    ys=np.arange(y0,y1,dtype=float)
    xs=ids+a+x0
    if good.mean()<.85:
        return None, 'broken or faint long-run support'
    coef=robust_fit(ys[good],xs[good])
    intercept,slope=map(float,coef)
    residual=np.abs(xs-(intercept+slope*ys))
    support=good&(residual<.12*height)
    if support.mean()<.85:
        return None, 'not one continuous straight stroke'
    return dict(slope=slope,intercept=intercept,y0=y0,y1=y1,
                support=float(support.mean()),path=[[intercept+slope*y0,y0],[intercept+slope*y1,y1]]),None


def corridor_clear(gray, item, rule, height):
    b=bbox(item)
    ys=np.arange(max(0,int(b[1])),min(gray.shape[0],int(np.ceil(b[3]))),dtype=np.float32)
    offsets=np.linspace(-.65*height,.65*height,quantize(1.3*height))
    xs=rule['intercept']+rule['slope']*ys
    patch=cv2.remap(gray,(xs[:,None]+offsets[None]).astype(np.float32),
                    np.broadcast_to(ys[:,None],(len(ys),len(offsets))),cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REPLICATE)
    if not patch.size:
        return False,1.
    cx=float(np.median(xs))
    px0,py0,px1,py1=roi([cx-2*height,b[1]-height,cx+2*height,b[3]+height],gray.shape)
    paper=float(np.percentile(gray[py0:py1,px0:px1],90))
    dark=(paper-patch)/max(paper,1)>.12
    # A printed separator must have clear paper on each side. This also protects
    # headings and text intersecting a vertical stroke; no global grid assumption.
    flank=(abs(offsets)>.22*height)&(abs(offsets)<.55*height)
    density=float(dark[:,flank].mean()) if flank.any() else 1.
    return density<.08,density


def correct(gray, items, witness, primitive):
    ink,sx,sy=primitive
    height=witness['height']
    decisions=[]; rules=[]; proposals={}
    for j,candidate in enumerate(witness['candidates']):
        rule,reason=verify_rule(gray,candidate,height)
        if rule is None:
            decisions.append(dict(candidate=j,decision='abstain',reason=reason,lines=candidate['lines']))
            continue
        rule['candidate']=j
        rules.append(rule)
    # Count actual long horizontal runs meeting each rule at distinct heights.
    # A local grid is protected; a newspaper's single header does not qualify.
    horizontal=runs(ink,12*height*sy) if rules else None
    protected=[]
    for j,rule in enumerate(rules):
        yy=np.arange(ink.shape[0]); xx=np.rint((rule['intercept']+rule['slope']*yy/sy)*sx).astype(int)
        near=np.zeros(len(yy),bool)
        for dx in range(-quantize(height*sx),quantize(height*sx)+1):
            near |= horizontal[yy,np.clip(xx+dx,0,ink.shape[1]-1)]>0
        near &= (yy>=rule['y0']*sy)&(yy<=rule['y1']*sy)
        changes=np.diff(np.r_[False,near,False].astype(int))
        starts=np.flatnonzero(changes==1); ends=np.flatnonzero(changes==-1)
        rows=(starts+ends)/2
        distinct=[]
        for y in rows:
            if not distinct or y-distinct[-1]>height*sy:
                distinct.append(float(y/(sy)))
        if len(distinct)>=3:
            protected.append(j)
        rule['horizontal_intersections']=distinct
    for j,rule in enumerate(rules):
        for i in witness['candidates'][rule['candidate']]['lines']:
            if j in protected:
                decisions.append(dict(line=i,rule=j,decision='preserve',reason='ruled grid'))
                continue
            ok,density=corridor_clear(gray,items[i],rule,height)
            decisions.append(dict(line=i,rule=j,decision='split' if ok else 'abstain',
                                  reason='continuous rule with clear sides' if ok else 'ink beside rule',density=density))
            if ok:
                proposals.setdefault(i,[]).append(rule)
    output=[]; changes=[]
    for i,item in enumerate(items):
        if i not in proposals:
            output.append(item)
            continue
        polys=[item['polygon']]
        for rule in proposals[i]:
            split=[]
            for p in polys:
                left=clip_polygon(p,rule['slope'],rule['intercept']-.12*height,1)
                right=clip_polygon(p,rule['slope'],rule['intercept']+.12*height,-1)
                if len(left)>=3 and len(right)>=3:
                    split.extend([left,right])
                else:
                    split.append(p)
            polys=split
        if len(polys)==1:
            output.append(item)
            continue
        pieces=[dict(item,polygon=p,source_ids=[i],provenance='verified separator clip') for p in polys]
        output.extend(pieces)
        changes.append(dict(line=i,old=item['polygon'],new=polys))
    return dict(items=output,changes=changes,rules=rules,decisions=decisions,protected_rules=protected)


def run(gray,items):
    start=perf_counter()
    witness,primitive=scout(gray,items)
    t=perf_counter()
    if witness['candidates']:
        product=correct(gray,items,witness,primitive)
        correction=perf_counter()-t
    else:
        product=dict(items=items,changes=[],rules=[],decisions=[],protected_rules=[])
        correction=0.
    product.update(witness=witness,correction_s=correction,added_s=perf_counter()-start)
    return product
