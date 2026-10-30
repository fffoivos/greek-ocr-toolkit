"""Render separated repeated lobed ornaments from physical ink components.

Unlike the connected-band gate, each component retains its own contour and
concavity witnesses. Repetition alone (digits, dots, letters) is not an ornament.
"""
import cv2,numpy as np
from time import perf_counter
from .contracts import bbox
from .geometry import roi
from .ink_photometry import percentiles8


def component_features(mask,height,*,fast=False):
    n,labels,stats,centers=cv2.connectedComponentsWithStats(mask,8);features=[]
    for k,(x,y,w,h,area) in enumerate(stats[1:],1):
        if not (.35*height<max(w,h)<3*height and min(w,h)>.18*height and area>.025*height*height):continue
        if x==0 or y==0 or x+w>=mask.shape[1] or y+h>=mask.shape[0]:continue
        b=(labels[y:y+h,x:x+w]==k).astype('uint8');cs,_=cv2.findContours(b,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        c=max(cs,key=cv2.contourArea)
        hull=cv2.convexHull(c,returnPoints=False)
        try:defects=cv2.convexityDefects(c,hull) if len(c)>3 and len(hull)>3 else None
        except cv2.error:defects=None  # Self-touching contour: topology unknown, never certify lobes.
        # Any nonempty native mask has distance-ridge diameter >=2 pixels.
        # Defects no deeper than2 cannot pass the measured-width condition.
        if fast and (defects is None or np.count_nonzero(defects.reshape(-1,4)[:,3]>512)<5):
            features.append(dict(id=k,bbox=[int(x),int(y),int(x+w),int(y+h)],center=centers[k].tolist(),lobes=0,defects=[],stroke=None,tile=None,mask=b,area=int(area)))
            continue
        dist=cv2.distanceTransform(b,cv2.DIST_L2,5);ridge=(dist>0)&(dist>=cv2.dilate(dist,np.ones((3,3),np.uint8)))
        stroke=float(np.median(2*dist[ridge])) if ridge.any() else 1.
        deep=[]
        if defects is not None:
            for a,z,d,depth in defects.reshape(-1,4):
                if depth/256>stroke:deep.append([int(c.reshape(-1,2)[d,0]+x),int(c.reshape(-1,2)[d,1]+y)])
        tile=np.zeros((40,40),np.float32);s=32/max(w,h);sw,sh=max(1,round(w*s)),max(1,round(h*s));tile[(40-sh)//2:(40-sh)//2+sh,(40-sw)//2:(40-sw)//2+sw]=cv2.resize(b.astype('float32'),(sw,sh),interpolation=cv2.INTER_AREA)
        features.append(dict(id=k,bbox=[int(x),int(y),int(x+w),int(y+h)],center=centers[k].tolist(),lobes=len(deep),defects=deep,stroke=stroke,tile=tile,mask=b,area=int(area)))
    if fast:
        seeds=[q for q in features if q['lobes']>=5]
        if not seeds:return [],labels
        # Only components whose dimensions can match a seed need width/tile work.
        features=[q for q in features if any(max(abs(np.array(q['mask'].shape)-z['mask'].shape))<=.3*height for z in seeds)]
        for q in features:
            if q['tile'] is not None:continue
            b=q['mask'];h,w=b.shape;dist=cv2.distanceTransform(b,cv2.DIST_L2,5);ridge=(dist>0)&(dist>=cv2.dilate(dist,np.ones((3,3),np.uint8)))
            q['stroke']=float(np.median(2*dist[ridge])) if ridge.any() else 1.
            tile=np.zeros((40,40),np.float32);s=32/max(w,h);sw,sh=max(1,round(w*s)),max(1,round(h*s));tile[(40-sh)//2:(40-sh)//2+sh,(40-sw)//2:(40-sw)//2+sw]=cv2.resize(b.astype('float32'),(sw,sh),interpolation=cv2.INTER_AREA);q['tile']=tile
    return features,labels


def inspect(gray,item,height,*,route='slow',detail=False,fast=False):
    t=perf_counter();b=bbox(item);p=np.asarray(item['polygon'],np.float32);(_, _),(a,d),angle=cv2.minAreaRect(p)
    vertical=bool((b[3]-b[1])>(b[2]-b[0]));padx=.4*height if vertical else 6*height;pady=6*height if vertical else .4*height
    x0,y0,x1,y1=roi([b[0]-padx,b[1]-pady,b[2]+padx,b[3]+pady],gray.shape)
    s=1. if route=='slow' else min(1.,16/height) if route=='explicit' else min(1.,8/height)
    raw=cv2.resize(gray[y0:y1,x0:x1],None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    paper,core=percentiles8(raw,[90,10]);mask=(raw<paper-.5*(paper-core)).astype('uint8');h=height*s
    fs,labels=component_features(mask,h,fast=fast)
    for q in fs:
        q['binary']=(q['tile']>.5).astype('uint8');q['distance']=cv2.distanceTransform(1-q['binary'],cv2.DIST_L2,3)
    lobed=[q for q in fs if q['lobes']>=5];groups=[]
    peers={}
    if fast and lobed:
        # Same bidirectional mean distance as the scalar renderer. Batched GEMM
        # avoids re-reading a 40-square tile for every Python pair.
        all_binary=np.array([q['binary'].ravel() for q in fs],np.float64)
        all_distance=np.array([q['distance'].ravel() for q in fs],np.float64)
        by_id={q['id']:i for i,q in enumerate(fs)};seeds=[by_id[q['id']] for q in lobed]
        da=cv2.gemm(all_distance[seeds],all_binary,1,None,0,flags=cv2.GEMM_2_T)/all_binary.sum(1)[None,:]
        db=cv2.gemm(all_binary[seeds],all_distance,1,None,0,flags=cv2.GEMM_2_T)/all_binary[seeds].sum(1)[:,None]
        dims=np.array([[q['bbox'][2]-q['bbox'][0],q['bbox'][3]-q['bbox'][1]] for q in fs])
        tolerance=np.array([q['stroke']*32/max(d) for q,d in zip(fs,dims)])
        eligible=(abs(dims[seeds,None,:]-dims[None,:,:]).max(2)<=.3*h)&(np.maximum(da,db)<=np.minimum(tolerance[seeds,None],tolerance[None,:])/2)
        peers={q['id']:[fs[j] for j in np.flatnonzero(eligible[k])] for k,q in enumerate(lobed)}
    for seed in lobed:
        group=list(peers.get(seed['id'],[]))
        for q in ([] if fast else fs):
            dims=np.diff(np.array(q['bbox']).reshape(2,2),axis=0)[0];ds=np.diff(np.array(seed['bbox']).reshape(2,2),axis=0)[0]
            # Shape disagreement in canonical pixels, tolerated only to measured
            # stroke width. Fine variations inside a printed flower stay visible.
            if max(abs(dims-ds))>.3*h:continue
            sa=seed['binary'];qa=q['binary'];da=seed['distance'];db=q['distance']
            shape_error=max(float(da[qa>0].mean()),float(db[sa>0].mean()))
            tolerance=min(seed['stroke']*32/max(ds),q['stroke']*32/max(dims))/2
            if shape_error<=tolerance:group.append(q)
        if len(group)>=4:
            minor=0 if vertical else 1;major=1-minor
            group=[q for q in group if abs(q['center'][minor]-seed['center'][minor])<h/2]
            group.sort(key=lambda q:q['center'][major]);gaps=np.diff([q['center'][major] for q in group])
            if len(group)>=4:
                period=float(np.median(gaps));chain=[group[0]]
                for q,gap in zip(group[1:],gaps):
                    if abs(gap-period)<h/2:chain.append(q)
                    else:
                        if len(chain)>=4:groups.append(chain)
                        chain=[q]
                if len(chain)>=4:groups.append(chain)
    selected=list({q['id']:q for g in groups for q in g}.values());ids={q['id'] for q in selected};poly=np.rint((p-[x0,y0])*s).astype('int32');target=np.zeros(mask.shape,np.uint8);cv2.fillPoly(target,[poly],1)
    remaining=(mask>0)&(target>0)&~np.isin(labels,list(ids))
    _,_,stats,_=cv2.connectedComponentsWithStats(remaining.astype('uint8'),8)
    unexplained=[q.tolist() for q in stats[1:] if q[4]>.025*h*h]
    touches=bool(np.any(np.isin(labels,list(ids))&(target>0)))
    drop=bool(touches and not unexplained and len(selected)>=4)
    record=dict(drop=drop,vertical=vertical,roi=[x0,y0,x1,y1],scale=s,route=route,groups=len(groups),
                matches=[q['bbox'] for q in selected],unexplained=unexplained,seconds=perf_counter()-t,
                components=[{k:v for k,v in q.items() if k not in ('tile','mask','binary','distance')} for q in fs])
    if detail:record.update(raw=raw,mask=mask,labels=labels)
    return record


def scout(gray,item,height):
    """Cheap equal-size/equal-spacing component chain; nomination only."""
    b=bbox(item);vertical=bool(b[3]-b[1]>b[2]-b[0]);px=.4*height if vertical else 6*height;py=6*height if vertical else .4*height
    x0,y0,x1,y1=roi([b[0]-px,b[1]-py,b[2]+px,b[3]+py],gray.shape);step=max(1,int(height/8))
    raw=gray[y0:y1:step,x0:x1:step]
    if not raw.size:return False
    paper,core=percentiles8(raw,[90,10]);mask=(raw<paper-.5*(paper-core)).astype('uint8');h=height/step
    _,_,stats,centers=cv2.connectedComponentsWithStats(mask,8);stats=stats[1:];centers=centers[1:]
    keep=(stats[:,2]>.18*h)&(stats[:,3]>.35*h)&(stats[:,2]<3*h)&(stats[:,3]<3*h)
    stats=stats[keep];centers=centers[keep]
    if len(stats)<4:return False
    axis=1 if vertical else 0;order=np.argsort(centers[:,axis]);stats=stats[order];centers=centers[order]
    q=np.lib.stride_tricks.sliding_window_view(stats[:,2:4],4,axis=0)
    c=np.lib.stride_tricks.sliding_window_view(centers,4,axis=0)
    regular=(np.ptp(q,axis=2)<=2).all(1)&(np.ptp(np.diff(c[:,axis,:],axis=1),axis=1)<=2)&(np.ptp(c[:,1-axis,:],axis=1)<=2)
    return bool(regular.any())


def verify(gray,item,height,*,scouted=None):
    """Native component topology nominates full R1 spatial support.

    Vertical repeated quotation marks falsified the standalone topology test.
    Its `drop` field is diagnostic only; this gate never promotes that decision.
    """
    from .ink_motif_gate import inspect as spatial
    b=bbox(item)
    if b[3]-b[1]>b[2]-b[0]:
        return dict(drop=False,reason='vertical discrete ownership unresolved')
    if not (scout(gray,item,height) if scouted is None else scouted):
        return dict(drop=False,reason='separated component chain absent')
    native=inspect(gray,item,height,route='slow',fast=True)
    if not native['groups']:
        return dict(drop=False,reason='native repeated lobed component absent',component=native)
    result,_=spatial(gray,item,height,diagnostic=True,samples=16)
    return dict(drop=bool(result['drop']),reason='native component chain plus spatial motif support' if result['drop'] else 'unexplained ink remains',component=native,spatial=result)


def adjacent(item,verified,height):
    """Parallel same-extent neighbour of a verified frieze; nomination only."""
    a=bbox(item)
    if a[2]-a[0]<5*height or a[3]-a[1]>3*height:return False
    for q in verified:
        b=bbox(q)
        gap=max(0,max(a[1],b[1])-min(a[3],b[3]))
        if gap<3*height and max(abs(a[0]-b[0]),abs(a[2]-b[2]))<height:return True
    return False


def layout_candidates(items,height):
    """Outer rows or one-body clearances on both sides nominate component work.

    This is only a cheap layout scout, never proof of a non-word. Thin page
    frames and separated flowers have explicit free support in the reviewed
    renderings. Inline ornament fragments can be missed by this scout.
    """
    if not items:return []
    b=np.array([bbox(q) for q in items]);centers=(b[:,1]+b[:,3])/2
    long=(b[:,2]-b[:,0]>8*height)&(b[:,2]-b[:,0]>b[:,3]-b[:,1]);records=[]
    for i,a in enumerate(b):
        if a[2]-a[0]<5*height or a[3]-a[1]>a[2]-a[0]:continue
        intersects=long&(np.minimum(a[2],b[:,2])>np.maximum(a[0],b[:,0]));intersects[i]=False
        above=intersects&(centers<centers[i]);below=intersects&~above
        up=max(0,float(np.min(a[1]-b[above,3]))) if above.any() else None
        down=max(0,float(np.min(b[below,1]-a[3]))) if below.any() else None
        if up is None or down is None or (up>height and down>height):
            records.append(dict(line=i,above_h=None if up is None else up/height,below_h=None if down is None else down/height))
    return records
