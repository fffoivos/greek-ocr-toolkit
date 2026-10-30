"""Localize rows on the unbent leaf; map their bands through the shared field."""
from time import perf_counter
import cv2,numpy as np
from .geometry import roi
from .geometry_page_field import render
from .detector import postprocess


def displacement(f,x,t):
    xs=np.asarray(f['xs']);knots=np.asarray(f['knots']);mesh=np.asarray(f['mesh'])
    x,t=np.broadcast_arrays(x,t);flat=x.ravel();phase=t.ravel()
    columns=np.array([np.interp(flat,xs,row) for row in mesh])
    k=np.clip(np.searchsorted(knots,phase)-1,0,len(knots)-2)
    w=np.clip((phase-knots[k])/(knots[k+1]-knots[k]),0,1);n=np.arange(len(flat))
    return ((1-w)*columns[k,n]+w*columns[k+1,n]).reshape(x.shape)


def unbend(gray,f):
    a,b,c,d=roi(f['region'],gray.shape);x=np.arange(a,c);t=np.arange(b,d)
    # Column interpolation first, then vectorized vertical knot interpolation.
    mesh=np.array([np.interp(x,f['xs'],row) for row in f['mesh']]);knots=np.asarray(f['knots'])
    k=np.clip(np.searchsorted(knots,t)-1,0,len(knots)-2);w=np.clip((t-knots[k])/(knots[k+1]-knots[k]),0,1)
    yy=t[:,None]+(1-w[:,None])*mesh[k]+w[:,None]*mesh[k+1]
    xx=np.broadcast_to(x[None,:],yy.shape).astype(np.float32)
    crop=cv2.remap(gray,xx,yy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
    return crop,[a,b]


def run(gray,original,detector,*,column_evidence=None,evidence=None,excluded_regions=(),field_cache=None):
    start=perf_counter();e=render(gray,original,column_evidence=column_evidence,route='slow',excluded_regions=excluded_regions,with_source=field_cache is not None) if evidence is None else evidence
    source=e.pop('_source',None)
    if source is not None and not excluded_regions:
        field_cache.update(height=e['height'],shape=gray.shape,prepared=source,native_full=True)
    out=[];regions=[]
    for fid,f in enumerate(e['fields']):
        if not f.get('curved'):continue
        crop,offset=unbend(gray,f);pm,meta=detector.infer(crop);rows=postprocess(pm,(crop.shape[1],crop.shape[0]));rows,native=native_bands(crop,rows,e['height']);mapped=[]
        for i,q in enumerate(rows):
            from shapely.geometry import Polygon
            vertices=np.asarray(Polygon(np.asarray(q['polygon'],float)).simplify(1e-5,preserve_topology=True).exterior.coords)[:-1]+offset;sample=[]
            for p,z in zip(vertices,np.roll(vertices,-1,axis=0)):
                n=max(1,int(np.linalg.norm(z-p)/(.4*e['height'])))
                sample.extend(p[None,:]+np.arange(n)[:,None]/n*(z-p)[None,:])
            points=np.asarray(sample);points[:,1]+=displacement(f,points[:,0],points[:,1])
            from shapely.geometry import Polygon
            from shapely.geometry import box
            shape=Polygon(points).buffer(.06*e['height']).intersection(box(0,0,gray.shape[1]-1,gray.shape[0]-1))
            if shape.geom_type!='Polygon':continue
            points=np.array(shape.exterior.coords)[:-1]
            mapped.append(dict(q,polygon=points.tolist(),baseline=None,page_field=True,field=fid,field_ready=not native[i].get('foreign_components',[]),rectified_polygon=vertices.tolist(),provenance='Paddle on shared unbent region'))
        out.extend(mapped);regions.append(dict(field=fid,items=mapped,offset=offset,shape=list(crop.shape),meta=meta,native=native))
    return dict(items=out,evidence=e,regions=regions,seconds=perf_counter()-start)

def native_bands(crop,rows,h):
    """Whole connected ink belongs to the closest rectified row, once only.

    This is an envelope observation, not a foreground classifier. The final
    caller must enforce existing exclusions and reject ambiguous ownership.
    """
    from scipy.ndimage import gaussian_filter1d
    from .geometry import line_axis
    from .contracts import bbox
    paper=cv2.boxFilter(crop,cv2.CV_32F,(max(3,round(4*h)|1),)*2)
    # Same inherited 8-bit texture floor as geometry_contacts.prepare;
    # component ownership below does not classify front/back or faintness.
    ink=(paper-crop>255*.08).astype(np.uint8)
    n,labels,stats,centres=cv2.connectedComponentsWithStats(ink,8)
    boxes=np.array([bbox(q) for q in rows]);axes=np.array([line_axis(q) for q in rows])
    heights=np.array([max(h,.65*min(cv2.minAreaRect(np.asarray(q['polygon'],np.float32))[1])) for q in rows])
    if not len(rows):return [],[]
    xx=centres[:,0];yy=centres[:,1];target=axes[:,0,None]+axes[:,1,None]*xx
    dist=abs(yy-target);inside=(xx>boxes[:,0,None]-.5*h)&(xx<boxes[:,2,None]+.5*h)
    dist=np.where(inside,dist,np.inf)
    choice=np.argmin(dist,axis=0);near=dist[choice,np.arange(n)]
    order=np.sort(dist,axis=0);margin=np.full(n,np.inf)
    if len(rows)>1:
        valid_distance=np.isfinite(order[0]);margin[valid_distance]=order[1,valid_distance]-order[0,valid_distance]
    localh=heights[choice]
    valid=(stats[:,3]>.3*localh)&(stats[:,3]<2*localh)&(stats[:,2]<5*localh)&(stats[:,4]>.025*localh*localh)&(near<.75*localh)&(margin>.15*localh);valid[0]=False
    ids=np.flatnonzero(valid);owner={int(i):int(choice[i]) for i in ids};ambiguous=[]
    # Reject multi-row connected objects rather than assigning a capital,
    # touching adjacent rows or a rule to one row merely by its centre.
    for i in list(owner):
        x,y,w,z,area=stats[i];hit=(inside[:,i])&(target[:,i]>y+.15*h)&(target[:,i]<y+z-.15*h)
        if hit.sum()>1:ambiguous.append(int(i));del owner[i]
    ids=np.array(list(owner),int)
    bb=stats[ids,:4].astype(float) if len(ids) else np.empty((0,4));bb[:,2:]+=bb[:,:2]
    from scipy.spatial import cKDTree
    tree=cKDTree((bb[:,:2]+bb[:,2:])/2) if len(bb) else None
    possible=(stats[:,3]<.5*localh)&(stats[:,2]<localh)&(stats[:,4]>=np.maximum(2,.003*localh*localh));possible[0]=False
    for i in np.flatnonzero(possible):
        if i in owner:continue
        x,y,w,z,area=stats[i];hh=localh[i]
        if z>=.5*hh or w>=hh or area<max(2,.003*hh*hh) or not len(bb):continue
        cx,cy=centres[i];local=np.array(tree.query_ball_point([cx,cy],3*h),int)
        if not len(local):continue
        rect=bb[local];dx=np.maximum(0,np.maximum(rect[:,0]-cx,cx-rect[:,2]));dy=np.maximum(0,np.maximum(rect[:,1]-cy,cy-rect[:,3]));ds=np.hypot(dx,dy);best=ds.min()
        if best>.45*h:continue
        owners={owner[int(ids[local[k]])] for k in np.flatnonzero(ds<best+.08*h)}
        if len(owners)==1:owner[i]=owners.pop()
    mapped=[];audit=[]
    for j,q in enumerate(rows):
        use=[i for i,k in owner.items() if k==j]
        bodies=[i for i in use if stats[i,3]>.3*h]
        if not bodies:mapped.append(q);audit.append(dict(row=j,status='no native bodies'));continue
        b=stats[use,:4].astype(float);b[:,2:]+=b[:,:2]
        a=max(0,min(boxes[j,0],b[:,0].min()-.1*h));c=min(crop.shape[1]-1,max(boxes[j,2],b[:,2].max()+.1*h))
        xs=np.linspace(a,c,max(3,round((c-a)/(.2*h))+1));centre=axes[j,0]+axes[j,1]*xs
        bh=np.median(stats[bodies,3]);hh=heights[j]
        # One smooth row envelope in rectified coordinates, not individual
        # letter shoulders. Native extrema include accents and descenders.
        slopes=axes[j,1];tops=b[:,1]-axes[j,0]-slopes*np.where(slopes>0,b[:,2],b[:,0])
        bottoms=b[:,3]-axes[j,0]-slopes*np.where(slopes>0,b[:,0],b[:,2])
        top=centre+tops.min()-.12*hh;bottom=centre+bottoms.max()+.12*hh
        poly=np.vstack([np.c_[xs,top],np.c_[xs[::-1],bottom[::-1]]]).tolist()
        mapped.append(dict(q,polygon=poly));audit.append(dict(row=j,status='whole native components',components=use,ambiguous=[i for i in ambiguous if choice[i]==j]))
    mapped,gaps=separate_bands(crop,mapped,h,ink,stats,labels,owner)
    for r in audit:
        r['gaps']=[q for q in gaps if r['row'] in q['rows']]
        q=mapped[r['row']];a,b,c,d=roi(bbox(q),crop.shape);m=np.zeros((d-b,c-a),np.uint8);cv2.fillPoly(m,[np.rint(np.asarray(q['polygon'])-[a,b]).astype(int)],1)
        counts=np.bincount(labels[b:d,a:c][m>0],minlength=n);ls=np.flatnonzero(counts)
        r['foreign_components']=[int(k) for k in ls if k in owner and owner[k]!=r['row'] and stats[k,3]>.3*h and counts[k]>max(2,.02*h*h)]
    return mapped,audit


def separate_bands(crop,rows,h,ink,stats,labels,owner):
    """One whitespace corridor between neighboring rectified row bands.

    Native connected components are barriers, including dots and accents. A
    corridor that cuts any component is rejected and its bands remain unready.
    This separates row envelopes; the page displacement remains shared.
    """
    from .geometry_rows import valley_path
    from .geometry import line_axis
    from .contracts import bbox
    from shapely.geometry import Polygon,LineString
    from shapely.ops import split
    shapes=[Polygon(np.asarray(q['polygon'],float)) for q in rows];boxes=np.array([bbox(q) for q in rows]);axes=np.array([line_axis(q) for q in rows]);audit=[]
    # All negative pair tests depend on the original axes, not on the shapes
    # subsequently clipped below. Batch those tests, preserving i/j order and
    # keeping the mutable shape-distance test at its original decision point.
    pairs=[]
    for i in range(len(rows)):
        js=np.arange(i)
        l=np.maximum(boxes[i,0],boxes[:i,0]);r=np.minimum(boxes[i,2],boxes[:i,2]);mid=(l+r)/2
        yi=axes[i,0]+axes[i,1]*mid;yj=axes[:i,0]+axes[:i,1]*mid
        eligible=(r-l>=2*h)&(abs(yi-yj)>.7*h)&(abs(yi-yj)<4*h)
        for j in js[eligible]:
            m=mid[j];ys=axes[:,0]+axes[:,1]*m
            between=(boxes[:,0]<m)&(m<boxes[:,2])&(np.minimum(yi[j],yj[j])<ys)&(ys<np.maximum(yi[j],yj[j]))
            between[[i,j]]=False
            if not between.any():pairs.append((i,int(j)))
    for i,j in pairs:
            l=max(boxes[i,0],boxes[j,0]);r=min(boxes[i,2],boxes[j,2]);mid=(l+r)/2
            if r-l<2*h:continue
            yi=axes[i,0]+axes[i,1]*mid;yj=axes[j,0]+axes[j,1]*mid
            if not .7*h<abs(yi-yj)<4*h:continue
            up,down=(i,j) if yi<yj else (j,i)
            # There is no row-ownership conflict when these envelopes do not
            # overlap and neither holds another row's assigned native ink.
            if shapes[i].distance(shapes[j])>.15*h:continue
            a=max(0,int(l));c=min(crop.shape[1],int(r)+1);xx=np.arange(a,c)
            y1=axes[up,0]+axes[up,1]*xx;y2=axes[down,0]+axes[down,1]*xx
            b=max(0,int(y1.min()));d=min(crop.shape[0],int(y2.max())+1)
            if d-b<3 or c-a<3:continue
            yy=np.arange(b,d)[:,None];midline=(y1+y2)/2
            solid=cv2.dilate(ink[b:d,a:c],np.ones((max(1,round(.1*h)),max(1,round(.1*h))),np.uint8))
            permitted=(yy>y1+.2*h)&(yy<y2-.2*h)
            cost=np.where(permitted,solid.astype(float)*1e3+.005*((yy-midline)/h)**2,1e6)
            path=valley_path(cost,h)+b
            # Exact native crossing check, not just a low sampled path cost.
            crossing=[]
            ids=np.flatnonzero((stats[:,0]<c)&(stats[:,0]+stats[:,2]>a)&(stats[:,1]<d)&(stats[:,1]+stats[:,3]>b))
            for k in ids:
                if k==0:continue
                x,y,w,z,_=stats[k];lo=max(a,x);hi=min(c,x+w)
                cut=path[lo-a:hi-a]
                if y>cut.max() or y+z<cut.min():continue
                iy,ix=np.nonzero(labels[y:y+z,lo:hi]==k);delta=iy+y-path[ix+lo-a]
                if len(delta) and delta.min()<-.04*h and delta.max()>.04*h:crossing.append(int(k))
            accepted=not crossing
            audit.append(dict(rows=[up,down],accepted=accepted,crossing=crossing,path=np.c_[xx,path].tolist()))
            if not accepted:continue
            sample=np.unique(np.r_[np.arange(0,len(xx),max(1,round(.25*h))),len(xx)-1])
            pts=np.c_[xx[sample],path[sample]];pts=np.vstack([[min(boxes[i,0],boxes[j,0])-h,path[0]],pts,[max(boxes[i,2],boxes[j,2])+h,path[-1]]]);cut=LineString(pts)
            for k,above in [(up,True),(down,False)]:
                pieces=list(split(shapes[k],cut).geoms)
                if len(pieces)>1:
                    keep=[q for q in pieces if (q.representative_point().y<np.interp(q.representative_point().x,xx,path))==above]
                    if len(keep)==1:shapes[k]=keep[0]
    return [dict(q,polygon=list(shapes[i].exterior.coords)[:-1]) for i,q in enumerate(rows)],audit
