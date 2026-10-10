"""Bounded curved printed-rule verification, using round 2's existing witness.

No additional full-page scout. A curve is evidence only with sustained original
pixel support and clean flanks. Grid protection uses the complete nominated rule.
"""
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from .geometry import quantize, roi, robust_fit
from .image_evidence import runs
from .contracts import bbox
from ..layout_barriers.fast import verify_rule, corridor_clear, clip_polygon


def curved_rule(gray,candidate,height):
    x0,y0,x1,y1=roi(candidate['bbox'],gray.shape)
    x0=max(0,int(x0-height)); x1=min(gray.shape[1],int(x1+height))
    crop=gray[y0:y1,x0:x1]
    if not crop.size:return None,'empty corridor'
    paper=np.percentile(crop,85,axis=1)
    strength=np.maximum(0,(paper[:,None]-crop)/np.maximum(paper[:,None],1)).astype(np.float32)
    smooth=cv2.boxFilter(strength,cv2.CV_32F,(1,quantize(2*height)))
    a=max(0,int(candidate["bbox"][0]-x0)); b=min(crop.shape[1],int(candidate["bbox"][2]-x0)+1)
    ids=np.argmax(smooth[:,a:b],axis=1)+a
    xs=gaussian_filter1d(ids.astype(float),2*height)+x0
    ys=np.arange(y0,y1,dtype=float)
    # Actual stroke pixels near the fitted curve; no gap-filled image evidence.
    idx=np.rint(xs-x0).astype(int)
    support=np.zeros(len(ys),bool)
    for d in range(-quantize(.12*height),quantize(.12*height)+1):
        support |= strength[np.arange(len(ys)),np.clip(idx+d,0,crop.shape[1]-1)]>.12
    if support.mean()<.85:return None,'curve lacks sustained original-pixel support'
    block=min(len(support),quantize(8*height))
    sustained_support=np.convolve(support.astype(float),np.ones(block)/block,mode='valid')
    if sustained_support.min()<.70:return None,'long unsupported rule interval'
    if np.quantile(abs(np.gradient(xs)),.99)>.08:return None,'rule path changes too fast'
    step=quantize(height)
    take=np.unique(np.r_[np.arange(0,len(ys),step),len(ys)-1])
    return dict(path=np.c_[xs[take],ys[take]].tolist(),support=float(support.mean()),
                y0=y0,y1=y1,provenance='curved sustained printed stroke'),None


def grid_intersections(rule,primitive,height):
    ink,sx,sy=primitive; horizontal=runs(ink,12*height*sy)
    path=np.asarray(rule['path']); yy=np.arange(ink.shape[0]); xx=np.rint(np.interp(yy/sy,path[:,1],path[:,0])*sx).astype(int)
    near=np.zeros(len(yy),bool)
    for dx in range(-quantize(height*sx),quantize(height*sx)+1):
        near |= horizontal[yy,np.clip(xx+dx,0,ink.shape[1]-1)]>0
    near &= (yy>=rule['y0']*sy)&(yy<=rule['y1']*sy)
    changes=np.diff(np.r_[False,near,False].astype(int)); rows=(np.flatnonzero(changes==1)+np.flatnonzero(changes==-1))/2
    distinct=[]
    for y in rows:
        if not distinct or y/sy-distinct[-1]>height:distinct.append(float(y/sy))
    return distinct


def isolated_stroke(gray,item,rule,height,wide_paper=False):
    """Exact connected-stroke witness for tight typesetting, not lower density."""
    b=bbox(item); yy=np.arange(max(0,int(b[1])),min(gray.shape[0],int(np.ceil(b[3]))),dtype=float)
    offsets=np.arange(-quantize(.65*height),quantize(.65*height)+1,dtype=float)
    centre=rule['intercept']+rule['slope']*yy
    raw=cv2.remap(gray,(centre[:,None]+offsets[None]).astype(np.float32),
                 np.broadcast_to(yy[:,None],(len(yy),len(offsets))).astype(np.float32),cv2.INTER_LINEAR)
    if not raw.size:return False,{'reason':'empty stroke'}
    paper=np.percentile(raw,90,axis=1)
    if wide_paper:
        x0,y0,x1,y1=roi([centre.min()-2*height,b[1]-height,centre.max()+2*height,b[3]+height],gray.shape)
        paper=np.full(len(yy),np.percentile(gray[y0:y1,x0:x1],90))
    ink=((paper[:,None]-raw)/np.maximum(paper[:,None],1)>.12).astype(np.uint8)
    closed=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((quantize(.2*height),1),np.uint8))
    n,lab,stats,_=cv2.connectedComponentsWithStats(closed,8); middle=abs(offsets)<.12*height
    ids,counts=np.unique(lab[:,middle],return_counts=True); valid=ids>0
    if not valid.any():return False,{'reason':'no stroke component'}
    k=ids[valid][np.argmax(counts[valid])]; stroke=lab==k
    width=stats[k,2]
    centre_mass=float(np.mean(np.any(stroke[:,middle]& (ink[:,middle]>0),axis=1)))
    # Component cannot touch either distant flank; width is measured after
    # rectification to the locally curved rule, so thickness is not slant.
    ok=centre_mass>.85 and width<.3*height and not stroke[:,[0,-1]].any()
    return bool(ok),dict(centre_support=centre_mass,width_h=float(width/height),touches_edge=bool(stroke[:,[0,-1]].any()))


def split_items(gray,items,rules,height):
    """Reuse verified curves on any proposed bands; returns items, changes, decisions.

    Rules must have path/y0/y1/support and horizontal_intersections (from refine).
    Coordinates are original-page pixels. No missing- or false-positive inference.
    """
    out=[]; changes=[]; decisions=[]
    for i,q in enumerate(items):
        b=bbox(q); polys=[q['polygon']]
        for j,rule in enumerate(rules):
            path=np.asarray(rule['path']); cx=float(np.interp((b[1]+b[3])/2,path[:,1],path[:,0]))
            if not (b[0]+6*height<cx<b[2]-6*height and b[1]>=rule['y0'] and b[3]<=rule['y1']):continue
            if len(rule.get('horizontal_intersections',[]))>=3:
                decisions.append(dict(line=i,rule=j,decision='preserve',reason='ruled grid')); continue
            yy=np.linspace(b[1],b[3],9); xx=np.interp(yy,path[:,1],path[:,0]); intercept,slope=robust_fit(yy,xx)
            local=dict(intercept=float(intercept),slope=float(slope))
            ok,density=corridor_clear(gray,q,local,height)
            isolated,detail=isolated_stroke(gray,q,local,height) if not ok else (False,{})
            ok=ok or isolated
            decisions.append(dict(line=i,rule=j,decision='split' if ok else 'abstain',density=density,isolation=detail,reason='isolated narrow stroke' if isolated else ('clear flanks' if ok else 'ink beside rule')))
            if not ok:continue
            pieces=[]
            for poly in polys:
                left=clip_polygon(poly,slope,intercept-.12*height,1); right=clip_polygon(poly,slope,intercept+.12*height,-1)
                pieces.extend([left,right] if len(left)>=3 and len(right)>=3 else [poly])
            polys=pieces
        if len(polys)==1:out.append(q)
        else:
            out.extend(dict(q,polygon=p,baseline=None,source_ids=q.get('source_ids',[i]),provenance='verified curved separator clip') for p in polys)
            changes.append(dict(line=i,old=q['polygon'],new=polys))
    return dict(items=out,changes=changes,decisions=decisions)


def boundary_ownership(gray,items,rule,height,wide_paper=True):
    """Render cross-row stroke/letter junctions; any junction leaves ownership unknown.

    A back-page rule can be perfectly continuous. An isolated word gap on that
    rule cannot establish a separator. Reuse the explicit connected-stroke width
    at EVERY crossing, not a vote or a darkness comparison against front ink.
    """
    records=[];path=np.asarray(rule['path'])
    for i,q in enumerate(items):
        b=bbox(q);cx=float(np.interp((b[1]+b[3])/2,path[:,1],path[:,0]))
        if not (b[0]+6*height<cx<b[2]-6*height and b[1]>=rule['y0'] and b[3]<=rule['y1']):continue
        yy=np.linspace(b[1],b[3],9);xx=np.interp(yy,path[:,1],path[:,0]);a,s=robust_fit(yy,xx)
        local=dict(intercept=a,slope=s);clear,density=corridor_clear(gray,q,local,height)
        ok,detail=isolated_stroke(gray,q,local,height,wide_paper=wide_paper)
        junction=not clear and (detail.get('width_h',0)>=.3 or detail.get('touches_edge',False))
        records.append(dict(line=i,bbox=b,clear=clear,isolated=ok,junction=bool(junction),density=density,**detail))
    return dict(crossings=records,accepted=bool(records) and not any(q['junction'] for q in records),
        semantics='No observed glyph junction; not a front-side ownership certificate')


def refine(gray,items,witness,primitive,apply=True,ownership=False,wide_paper=False):
    rules=[]; abstentions=[]
    for i,candidate in enumerate(witness['candidates']):
        straight,_=verify_rule(gray,candidate,witness['height'])
        if straight is not None:continue
        rule,reason=curved_rule(gray,candidate,witness['height'])
        if rule is None:abstentions.append(dict(candidate=i,reason=reason));continue
        rule['candidate']=i; rule['horizontal_intersections']=grid_intersections(rule,primitive,witness['height'])
        if ownership:
            rule['ownership']=boundary_ownership(gray,items,rule,witness['height'],wide_paper=wide_paper)
            if not rule['ownership']['accepted']:
                abstentions.append(dict(candidate=i,reason='whole-rule ownership uncertain at glyph junction',rule=rule));continue
        rules.append(rule)
    result=split_items(gray,items,rules,witness['height']) if rules and apply else dict(items=items,changes=[],decisions=[])
    return dict(result,rules=rules,abstentions=abstentions)
