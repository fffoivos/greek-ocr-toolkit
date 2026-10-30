"""Front-column terminations along an independently verified printed rule.

A vertical stroke alone can be verso. Here both sides must independently have
several already separated long rows ending/starting at that stroke. The explicit
witness records each endpoint and its native rule. Clipping shares the centre
edge: it does not erase letters touching a narrow column rule.
"""
from time import perf_counter
import numpy as np
from .contracts import bbox
from .geometry import robust_fit
from .geometry_feature_rules import curved_rule,grid_intersections
from ..layout_barriers.fast import verify_rule,clip_polygon


def nominate(items,witness,primitive):
    if not witness.get('vertical_components'):return []
    ink,sx,sy=primitive;h=witness['height'];bb=np.asarray([bbox(q) for q in items]).reshape(-1,4);out=[]
    for x,y,w,hh,area in witness['vertical_components']:
        if hh/sy<12*h or w/sx>4*h:continue
        cx=(x+w/2)/sx;y0=y/sy;y1=(y+hh)/sy
        cross=np.flatnonzero((bb[:,0]+6*h<cx)&(cx<bb[:,2]-6*h)&(bb[:,1]>y0-2*h)&(bb[:,3]<y1+2*h))
        if len(cross):out.append(dict(bbox=[x/sx,y0,(x+w)/sx,y1],lines=cross.tolist()))
    return out


def termination_witness(items,rule,h):
    path=np.asarray(rule['path']);groups=[[],[]]
    for i,q in enumerate(items):
        b=bbox(q);cy=(b[1]+b[3])/2
        if b[2]-b[0]<8*h or not rule['y0']-h<cy<rule['y1']+h:continue
        cx=float(np.interp(cy,path[:,1],path[:,0]))
        for side,end in enumerate([b[2],b[0]]):
            if abs(end-cx)<1.5*h and (b[0]<cx-8*h if side==0 else b[2]>cx+8*h):
                groups[side].append(dict(line=i,point=[end,cy],distance_h=(end-cx)/h))
    distinct=[]
    for group in groups:
        ys=[]
        for rec in sorted(group,key=lambda r:r['point'][1]):
            y=rec['point'][1]
            if not ys or y-ys[-1]>2*h:ys.append(y)
        distinct.append(ys)
    spans=[max(y)-min(y) if y else 0 for y in distinct]
    # A run of terminations on BOTH sides is distinct from one pale stroke
    # crossing words. This uses measured geometric distances, no majority vote.
    accepted=all(len(y)>=3 and span>=12*h for y,span in zip(distinct,spans))
    return dict(left=groups[0],right=groups[1],span_h=[s/h for s in spans],accepted=accepted)


def analyze(gray,original,witness,primitive,route='explicit',version=4,retained_source_indices=None):
    start=perf_counter();h=witness['height'];records=[]
    for c in nominate(original,witness,primitive):
        rule,reason=verify_rule(gray,c,h)
        if rule is None:rule,reason=curved_rule(gray,c,h)
        if rule is None:
            records.append(dict(candidate=c,accepted=False,reason=reason));continue
        intersections=grid_intersections(rule,primitive,h)
        positive_ids=list(range(len(original))) if retained_source_indices is None else [i for i in range(len(original)) if i in retained_source_indices]
        positive=[original[i] for i in positive_ids]
        ends=termination_witness(positive,rule,h)
        for side in ('left','right'):
            for point in ends[side]:point['line']=positive_ids[point['line']]
        native=native_crossings(gray,rule,h,'slow' if route=='slow' else 'explicit') if version>=2 else None
        paired=any(abs(a['point'][1]-b['point'][1])<h for a in ends['left'] for b in ends['right'])
        accepted=(ends['accepted'] or (native and native['clear'] and (paired if version>=3 else True))) and len(intersections)<3
        records.append(dict(candidate=c,rule=rule,endpoints=ends,native=native,intersections=intersections,accepted=bool(accepted),
            reason='independent bilateral row terminations' if accepted else 'grid or no bilateral terminations'))
    return dict(rules=records,height=h,route=route,seconds=perf_counter()-start)


def apply(items,evidence):
    h=evidence['height'];out=[];changes=[];rules=[]
    for rec in sorted(evidence['rules'],key=lambda r:-(r.get('rule',{}).get('y1',0)-r.get('rule',{}).get('y0',0))):
        if not rec['accepted']:continue
        p=np.asarray(rec['rule']['path']);duplicate=False
        for old in rules:
            q=np.asarray(old['rule']['path']);lo=max(p[0,1],q[0,1]);hi=min(p[-1,1],q[-1,1])
            if hi>lo and abs(np.interp((lo+hi)/2,p[:,1],p[:,0])-np.interp((lo+hi)/2,q[:,1],q[:,0]))<.5*h:duplicate=True;break
        if not duplicate:rules.append(rec)
    for i,q in enumerate(items):
        pieces=[q['polygon']];b=bbox(q)
        for rec in rules:
            rule=rec['rule'];p=np.asarray(rule['path']);cy=(b[1]+b[3])/2;cx=np.interp(cy,p[:,1],p[:,0])
            if not (b[0]+6*h<cx<b[2]-6*h and rule['y0']<=cy<=rule['y1']):continue
            yy=np.linspace(b[1],b[3],9);xx=np.interp(yy,p[:,1],p[:,0]);a,s=robust_fit(yy,xx)
            new=[]
            for poly in pieces:
                left=clip_polygon(poly,s,a,1);right=clip_polygon(poly,s,a,-1)
                new.extend([left,right] if len(left)>=3 and len(right)>=3 else [poly])
            pieces=new
        if len(pieces)==1:out.append(q)
        else:
            out.extend(dict(q,polygon=p,baseline=None,provenance='bilateral column terminations') for p in pieces)
            changes.append(dict(line=i,old=q['polygon'],new=pieces))
    return dict(items=out,changes=changes)


def native_crossings(gray,rule,h,route='slow'):
    """Explicit horizontal glyph strokes crossing the verified rule.

    Close typesetting may touch ONE side. A connected ink run from the left
    flank through the stroke to the right flank is a different observation.
    No darkness rank or fraction of friendly rows determines this witness.
    """
    import cv2
    from .geometry import quantize
    path=np.asarray(rule['path']);ys=np.arange(rule['y0'],rule['y1'],dtype=float)
    off=np.arange(-quantize(1.5*h),quantize(1.5*h)+1,dtype=float)
    xx=np.interp(ys,path[:,1],path[:,0]);raw=cv2.remap(gray,(xx[:,None]+off).astype(np.float32),np.broadcast_to(ys[:,None],(len(ys),len(off))).astype(np.float32),cv2.INTER_LINEAR)
    paper=np.percentile(raw,90,axis=1);ink=(paper[:,None]-raw)/np.maximum(paper[:,None],1)>.12
    centre=len(off)//2;radius=quantize(.3*h)
    # Exact native connected runs through the stroke. The loop is deliberately
    # slow reference; route1's vectorized conjunction gives identical witnesses.
    if route=='slow':
        crossing=np.array([all(row[centre-radius:centre+radius+1]) for row in ink])
    else:crossing=ink[:,centre-radius:centre+radius+1].all(axis=1)
    runs=[];edge=np.diff(np.r_[False,crossing,False].astype(int))
    for a,b in zip(np.flatnonzero(edge==1),np.flatnonzero(edge==-1)):
        runs.append(dict(y0=float(ys[a]),y1=float(ys[b-1]+1),path=[[float(xx[a]-radius),float(ys[a])],[float(xx[a]+radius),float(ys[a])]]))
    return dict(through=runs,clear=not bool(runs))
