"""Shared page displacement from neighbouring native row profiles.

Diagnostic construction first. The mesh is ink geometry, not front-ink ownership
or a baseline model. No page identifiers or reference-detector lines are inputs.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from .geometry import height_proxy
from .contracts import bbox
from .geometry_contacts import prepare


def blocks(items, size, h, column_evidence=None):
    """Observed horizontal supports, split only at sustained empty channels."""
    W,H=size
    boxes=np.array([bbox(q) for q in items if bbox(q)[2]-bbox(q)[0]>8*h]).reshape(-1,4)
    if len(boxes)<4:return []
    a=max(0,float(boxes[:,0].min())-3*h);b=min(W,float(boxes[:,2].max())+5*h)
    x=np.arange(a,b,max(1,h));cover=((x[None,:]>boxes[:,0,None])&(x[None,:]<boxes[:,2,None])).sum(0)
    # No inferred gutter in the middle of a long crossing source.
    gaps=np.flatnonzero((cover==0)&(x>a+8*h)&(x<b-8*h));cuts=[]
    if len(gaps):
        for run in np.split(gaps,np.flatnonzero(np.diff(gaps)>1)+1):
            if len(run)*h>=2*h:cuts.append(float(np.mean(x[run])))
    for r in (column_evidence or {}).get('rules',[]):
        if r.get('accepted'):
            cuts.append(float(np.median(np.array(r['rule']['path'])[:,0])))
    edges=[a,*sorted(set(cuts)),b];result=[]
    for l,r in zip(edges,edges[1:]):
        use=boxes[(boxes[:,2]>l)&(boxes[:,0]<r)]
        # Cross-column originals may be the very boxes being repaired. The
        # independent printed boundary, not their current midpoint, splits us.
        if len(use)<4:use=boxes[(boxes[:,2]>l)&(boxes[:,0]<r)]
        if len(use)<4 or r-l<12*h:continue
        result.append([l,max(0,float(use[:,1].min())-h),r,min(H,float(use[:,3].max())+h)])
    return result


def render(gray,items,*,route='slow',regions=None,column_evidence=None,with_source=False,excluded_regions=()):
    start=perf_counter();h=height_proxy(items,gray.shape[::-1])
    working=gray
    if excluded_regions:
        from .geometry import roi
        working=gray.copy()
        for q in excluded_regions:
            a,b,c,d=roi(bbox(q),gray.shape);paper=float(np.quantile(gray[b:d,a:c],.9))
            cv2.fillPoly(working,[np.rint(q['polygon']).astype(int)],paper)
    source=prepare(working,h,12 if route=='explicit' else None,fast_filter=True,with_labels=with_source)
    density=source['density'];sx,sy=source['scale'];fields=[]
    for region in (blocks(items,gray.shape[::-1],h,column_evidence) if regions is None else regions):
        a,b,c,d=region
        local_bodies=[q for q in source['components'] if a<q['centre'][0]<c and b<q['centre'][1]<d]
        body_height=float(np.median([q['bbox'][3]-q['bbox'][1] for q in local_bodies])) if local_bodies else h
        xs=np.linspace(a,c,max(9,int((c-a)/h)+1));ys=np.arange(b,d,max(1,h/10))
        mx=np.broadcast_to((xs*sx)[None,:],(len(ys),len(xs))).astype(np.float32)
        my=np.broadcast_to((ys*sy)[:,None],mx.shape).astype(np.float32)
        # Density thresholds (.035/.05 etc.) are fractions of binary body
        # occupancy after letter-scaled smoothing, not raw grey-level cutoffs.
        profiles=cv2.remap(density,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        anchor=len(xs)//2
        ref=profiles[:,max(0,anchor-2):anchor+3].mean(1)
        peaks,_=find_peaks(ref,distance=max(1,int(.9*h/(ys[1]-ys[0]))),prominence=.035,height=.05)
        seeds=ys[peaks]
        if len(seeds)<4:
            fields.append(dict(region=region,status='insufficient rows',rows=[]));continue
        # Displacement knots are spaced over several rows, not one free curve
        # per detector item. All row predictions interpolate the same mesh.
        knots=np.linspace(b,d,max(3,int((d-b)/(8*h))+1))
        mesh=np.zeros((len(knots),len(xs)));support=np.zeros_like(mesh)
        lag_bound=min(h,.4*float(np.median(np.diff(seeds))))
        lag=np.linspace(-lag_bound,lag_bound,25)
        # All knot windows observe the same native profiles. Batch their
        # correlations; padding is masked, so it contributes to neither mean
        # nor energy. No sampling, lag, field smoothing or acceptance changes.
        local_windows=[ys[(ys>t-7*h)&(ys<t+7*h)] for t in knots]
        lengths=np.array([len(q) for q in local_windows]);width=int(lengths.max())
        window=np.stack([np.pad(q,(0,width-len(q)),mode='edge') for q in local_windows])
        valid=np.arange(width)[None,:]<lengths[:,None]
        valid_lengths=np.maximum(lengths,1)
        def demean(values):
            return np.where(valid,values-(values*valid).sum(-1,keepdims=True)/valid_lengths[:,None],0)
        def shifts_many(before,moved,columns):
            # Each column keeps the original np.interp and last-axis reduction
            # order. Only independent columns of one refinement iteration are
            # batched; outward propagation below remains strictly sequential.
            after=np.stack([np.interp(m+lag[None,:,None],ys,profiles[:,col],left=0,right=0)
                            for m,col in zip(moved[:, :, None, :],columns)])
            after=np.where(valid[None,:,None,:],after-(after*valid[None,:,None,:]).sum(-1,keepdims=True)/valid_lengths[None,:,None,None],0)
            scores=np.sum(after*before[:,:,None,:],axis=3)/(np.sqrt(np.sum(after**2,axis=3)*np.sum(before**2,axis=2)[:,:,None])+1e-9)
            js=np.argmax(scores,axis=2);cc,kk=np.indices(js.shape);delta=lag[js].copy();middle=(js>0)&(js<len(lag)-1);ci=cc[middle];ii=kk[middle];jj=js[middle]
            delta[middle]+=.5*(scores[ci,ii,jj-1]-scores[ci,ii,jj+1])/np.minimum(-1e-9,scores[ci,ii,jj-1]-2*scores[ci,ii,jj]+scores[ci,ii,jj+1])*(lag[1]-lag[0])
            weight=np.maximum(0,scores[cc,kk,js]);delta[:,lengths<5]=0;weight[:,lengths<5]=0
            return delta,weight
        def shifts(before,moved,col):
            delta,weight=shifts_many(before[None],moved[None],[col])
            return delta[0],weight[0]
        for direction in (-1,1):
            for col in range(anchor+direction,len(xs) if direction==1 else -1,direction):
                prev=col-direction;estimate=mesh[:,prev].copy()
                moved=window+np.interp(window,knots,estimate)
                before=demean(np.interp(moved,ys,profiles[:,prev],left=0,right=0))
                delta,weight=shifts(before,moved,col)
                smooth=gaussian_filter1d(delta*weight,1)/np.maximum(.05,gaussian_filter1d(weight,1))
                mesh[:,col]=estimate+smooth;support[:,col]=weight
        mesh=gaussian_filter1d(mesh,1,axis=1);rows=[]
        # Align against the same joint template for the same two iterations.
        for iteration in range(2):
            unbent=np.stack([np.interp(ys+np.interp(ys,knots,mesh[:,k]),ys,profiles[:,k],left=0,right=0) for k in range(len(xs))],axis=1)
            template=unbent.mean(1);adjust=np.zeros_like(mesh);weight=np.zeros_like(mesh)
            before=demean(np.interp(window,ys,template))
            usable=(before**2).sum(1)>=1e-5
            for first in range(0,len(xs),8):
                columns=np.arange(first,min(first+8,len(xs)))
                moved=np.stack([window+np.interp(window,knots,mesh[:,col]) for col in columns])
                delta,wgt=shifts_many(np.broadcast_to(before,(len(columns),*before.shape)),moved,columns)
                adjust[np.ix_(usable,columns)]=delta[:,usable].T;weight[np.ix_(usable,columns)]=wgt[:,usable].T
            adjust=gaussian_filter1d(adjust*weight,1,axis=0)/np.maximum(.1,gaussian_filter1d(weight,1,axis=0))
            mesh+=gaussian_filter1d(adjust,1,axis=1)
        # Once the field is observed, all strips vote for row positions. Short
        # rows missing at the anchor column can now appear without inventing a
        # periodic grid or treating the detector's line list as complete.
        # Ink profiles can have two lobes within one printed row. Row phase is
        # instead witnessed by centres of body-sized connected components,
        # transported through the same shared field. Detached accents cannot
        # create a second row merely because their ink forms another lobe.
        selected=[]
        for q in local_bodies:
            l,t,r,z=q['bbox'];cx,cy=q['centre']
            if not (.6*body_height<z-t<2*body_height and r-l>.08*body_height):continue
            selected.append([cx,cy])
        centres=invert_points(xs,knots,mesh,np.asarray(selected).reshape(-1,2))
        histogram=np.histogram(centres,bins=np.r_[ys,ys[-1]+ys[1]-ys[0]])[0].astype(float)
        ref=gaussian_filter1d(histogram,max(1,.2*body_height/(ys[1]-ys[0])))
        peaks,_=find_peaks(ref,distance=max(1,int(body_height/(ys[1]-ys[0]))),prominence=.12,height=.25)
        seeds=ys[peaks]
        for n,seed in enumerate(seeds):
            prediction=seed+np.array([np.interp(seed,knots,mesh[:,k]) for k in range(len(xs))])
            rows.append(dict(row=n,seed=float(seed),path=np.c_[xs,prediction].tolist()))
        edges=[]
        fields.append(dict(region=region,status='measured candidate',body_height=body_height,xs=xs.tolist(),knots=knots.tolist(),mesh=mesh.tolist(),support=support.tolist(),anchor=anchor,rows=rows,edges=edges,curved=any(r['coherent'] for r in edges)))
    e=certify(dict(height=h,route=route,fields=fields,excluded_footprints=len(excluded_regions)),source['components'])
    for f in e['fields']:
        if 'mesh' in f:
            f['minimum_vertical_jacobian']=float(np.min(np.diff(np.asarray(f['knots'])[:,None]+np.asarray(f['mesh']),axis=0)/np.diff(f['knots'])[:,None]))
            if f['minimum_vertical_jacobian']<=0:f.update(curved=False,status='non-monotone correspondence rejected')
    e['seconds']=perf_counter()-start
    if with_source:e['_source']=source
    return e


def certify(e,components):
    """Independent letter-bottom witnesses for the candidate field's bend.

    A smooth mesh is not itself evidence that a flat page curves. This compares
    measured component bottoms with a straight interior tangent, row by row.
    The mesh only establishes correspondence when the straight box crosses rows.
    """
    from .geometry import robust_fit
    h=e['height']
    for f in e['fields']:
        if not f.get('rows'):continue
        a,b,c,d=f['region'];xs=np.asarray(f['xs']);knots=np.asarray(f['knots']);mesh=np.asarray(f['mesh']);seeds=np.array([r['seed'] for r in f['rows']]);byrow={}
        phases=invert_points(xs,knots,mesh,np.asarray([q['centre'] for q in components]).reshape(-1,2))
        for q,phase in zip(components,phases):
            x,y=q['centre'];l,t,r,z=q['bbox']
            if not (a<x<c and b<y<d and .35*h<z-t<1.4*h and .08*h<r-l<2*h):continue
            i=int(np.argmin(abs(seeds-phase)))
            if abs(seeds[i]-phase)>.5*h:continue
            byrow.setdefault(i,[]).append([x,z])
        records=[]
        for i,points in byrow.items():
            p=np.asarray(points);x,y=p.T
            if len(p)<12 or np.ptp(x)<12*h:continue
            lo,hi=x.min(),x.max();width=hi-lo;mid=(lo+hi)/2;inside=(x>lo+width/3)&(x<hi-width/3)
            if inside.sum()<6:continue
            coef=robust_fit((x[inside]-mid)/h,y[inside]/h)
            residual=y/h-np.polynomial.polynomial.polyval((x-mid)/h,coef)
            noise=max(.05,float(1.4826*np.median(abs(residual[inside]-np.median(residual[inside])))))
            path=np.array(f['rows'][i]['path']);basefit=np.polyfit(path[(xs>lo+width/3)&(xs<hi-width/3),0],path[(xs>lo+width/3)&(xs<hi-width/3),1],1)
            for side,select in [('left',x<lo+width/3),('right',x>hi-width/3)]:
                ids=np.flatnonzero(select)
                if len(ids)<5:continue
                ids=ids[np.argsort(x[ids])];outer=ids[:max(4,len(ids)//2)] if side=='left' else ids[-max(4,len(ids)//2):]
                deviation=float(np.median(residual[outer]));ex=float(np.median(x[outer]));dy=(np.interp(ex,xs,path[:,1])-np.polyval(basefit,ex))/h
                edge_noise=max(.05,float(1.4826*np.median(abs(residual[outer]-deviation))));uncertainty=(noise**2/inside.sum()+edge_noise**2/len(outer))**.5
                good=abs(deviation)>.35 and abs(deviation)>3*uncertainty and abs(deviation-dy)<.3
                records.append(dict(row=i,side=side,edge=[ex,float(np.median(y[outer]))],deviation_h=deviation,field_deviation_h=float(dy),uncertainty_h=uncertainty,candidate=bool(good),body_bottoms=points))
        for r in records:
            near=[q for q in records if q['candidate'] and q['side']==r['side'] and q['deviation_h']*r['deviation_h']>0 and abs(q['edge'][1]-r['edge'][1])<8*h and abs(q['edge'][0]-r['edge'][0])<6*h]
            r['coherent']=r['candidate'] and len(near)>=3
        f['certificate']=records;f['curved']=any(r['coherent'] for r in records)
    return e


def invert_points(xs,knots,mesh,points):
    """Vectorized inverse of the monotone piecewise-linear vertical mesh."""
    if not len(points):return np.array([])
    delta=np.array([np.interp(points[:,0],xs,row) for row in mesh]);warped=knots[:,None]+delta
    idx=np.clip((warped<=points[:,1]).sum(0)-1,0,len(knots)-2);n=np.arange(len(points))
    fraction=np.clip((points[:,1]-warped[idx,n])/np.maximum(1e-9,warped[idx+1,n]-warped[idx,n]),0,1)
    return knots[idx]+fraction*(knots[idx+1]-knots[idx])
