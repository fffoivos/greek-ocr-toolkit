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

def native_bands(crop,rows,h,*,request_mode=False,axes=None,supports=None,domains=None,target_rows=None,retain_support=False):
    """Whole connected ink belongs to the closest rectified row, once only.

    This is an envelope observation, not a foreground classifier. The final
    caller must enforce existing exclusions and reject ambiguous ownership.
    """
    if not request_mode and any(v is not None for v in (axes,supports,domains,target_rows)):
        raise ValueError("Explicit row support belongs to request completion")
    from scipy.ndimage import gaussian_filter1d
    from .geometry import line_axis
    from .contracts import bbox
    paper=cv2.boxFilter(crop,cv2.CV_32F,(max(3,round(4*h)|1),)*2)
    # Same inherited 8-bit texture floor as geometry_contacts.prepare;
    # component ownership below does not classify front/back or faintness.
    ink=(paper-crop>255*.08).astype(np.uint8)
    n,labels,stats,centres=cv2.connectedComponentsWithStats(ink,8)
    if request_mode:
        domains=rule_edges(domains or [[] for _ in rows], ink, labels, stats=stats)
        # Hoist corridor_hulls' existing domain-unknown rejection. If every
        # target already lacks a finite observed rule edge, no envelope or
        # separator can authorize a completion. Keep the fixed census/rows.
        if target_rows and all(any(r.get('unknown') for r in domains[j]) for j in target_rows):
            return list(rows),[dict(row=j,status='unknown finite rule ink edge',
                domain_unknown=any(r.get('unknown') for r in domains[j]),
                gaps=[],corridor_complete=False,
                support_accounting=dict(census='request-local M17 mean-paper CC8 labels',
                    population=n-1,present=[],complete_support=None,
                    semantics='Not measured: existing finite-rule rejection already prevents completion.'))
                for j in range(len(rows))]
    boxes=np.array([bbox(q) for q in rows]);axes=np.array([line_axis(q) for q in rows]) if axes is None else np.asarray(axes,float)
    heights=np.array([max(h,.65*min(cv2.minAreaRect(np.asarray(q['polygon'],np.float32))[1])) for q in rows])
    if not len(rows):return [],[]
    xx=centres[:,0];yy=centres[:,1];target=axes[:,0,None]+axes[:,1,None]*xx
    dist=abs(yy-target);inside=(xx>boxes[:,0,None]-.5*h)&(xx<boxes[:,2,None]+.5*h)
    if domains is not None:
        for j,rules in enumerate(domains):
            for rule in rules:
                path=np.asarray(rule['path']);x0=stats[:,0];x1=x0+stats[:,2];y0=stats[:,1];y1=y0+stats[:,3]
                lo=np.interp(y0,path[:,1],path[:,0]);hi=np.interp(y1,path[:,1],path[:,0])
                same=(x0>np.maximum(lo,hi)) if rule['side']>0 else (x1<np.minimum(lo,hi))
                inside[j]&=same&(y0>=rule['y0'])&(y1<=rule['y1'])
    dist=np.where(inside,dist,np.inf)
    choice=np.argmin(dist,axis=0);near=dist[choice,np.arange(n)]
    margin=np.full(n,np.inf)
    if len(rows)>1:
        # Only the nearest two distances enter the ownership margin.
        order=np.partition(dist,1,axis=0)[:2]
        valid_distance=np.isfinite(order[0]);margin[valid_distance]=order[1,valid_distance]-order[0,valid_distance]
    localh=heights[choice]
    valid=(stats[:,3]>.3*localh)&(stats[:,3]<2*localh)&(stats[:,2]<5*localh)&(stats[:,4]>.025*localh*localh)&(near<.75*localh)&(margin>.15*localh);valid[0]=False
    ids=np.flatnonzero(valid)
    # Reject multi-row connected objects rather than assigning a capital,
    # touching adjacent rows or a rule to one row merely by its centre.
    hit=inside[:,ids]&(target[:,ids]>stats[ids,1]+.15*h)&(target[:,ids]<stats[ids,1]+stats[ids,3]-.15*h)
    multiple=hit.sum(axis=0)>1;ambiguous=ids[multiple].tolist();ids=ids[~multiple]
    owner={int(i):int(choice[i]) for i in ids}
    bb=stats[ids,:4].astype(float) if len(ids) else np.empty((0,4));bb[:,2:]+=bb[:,:2]
    from scipy.spatial import cKDTree
    tree=cKDTree((bb[:,:2]+bb[:,2:])/2) if len(bb) else None
    possible=(stats[:,3]<.5*localh)&(stats[:,2]<localh)&(stats[:,4]>=np.maximum(2,.003*localh*localh));possible[0]=False
    if request_mode and tree is not None:
        # Exact same body-neighbour queries and distances, once in a batch.
        # The body census is fixed before mark attachment; later marks never
        # enter this tree. Min/max over tied body owners replaces the set test.
        marks=np.array([i for i in np.flatnonzero(possible) if i not in owner],int)
        neighbours=tree.query_ball_point(centres[marks],3*h)
        lengths=np.array([len(v) for v in neighbours],int)
        mi=np.repeat(marks,lengths);bi=np.array([k for v in neighbours for k in v],int)
        if len(mi):
            rect=bb[bi];cx,cy=centres[mi].T
            dx=np.maximum(0,np.maximum(rect[:,0]-cx,cx-rect[:,2]))
            dy=np.maximum(0,np.maximum(rect[:,1]-cy,cy-rect[:,3]))
            ds=np.hypot(dx,dy);best=np.full(n,np.inf);np.minimum.at(best,mi,ds)
            close=(best[mi]<=.45*h)&(ds<best[mi]+.08*h)
            low=np.full(n,len(rows),int);high=np.full(n,-1,int)
            np.minimum.at(low,mi[close],choice[ids[bi[close]]])
            np.maximum.at(high,mi[close],choice[ids[bi[close]]])
            for i in marks[low[marks]==high[marks]]:owner[int(i)]=int(low[i])
    else:
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
    grouped=[[] for _ in rows];uncertain=[[] for _ in rows]
    for i,j in owner.items():grouped[j].append(i)
    for i in ambiguous:uncertain[choice[i]].append(i)
    if request_mode:
        supports=body_supports(supports,grouped,stats,domains)
    mapped=[];audit=[]
    for j,q in enumerate(rows):
        use=grouped[j]
        bodies=[i for i in use if stats[i,3]>.3*h]
        if not bodies:mapped.append(q);audit.append(dict(row=j,status='no native bodies'));continue
        b=stats[use,:4].astype(float);b[:,2:]+=b[:,:2]
        a=max(0,min(boxes[j,0],b[:,0].min()-.1*h));c=min(crop.shape[1]-1,max(boxes[j,2],b[:,2].max()+.1*h))
        xs=np.linspace(a,c,max(3,round((c-a)/(.2*h))+1));centre=axes[j,0]+axes[j,1]*xs
        hh=heights[j]
        # One smooth row envelope in rectified coordinates, not individual
        # letter shoulders. Native extrema include accents and descenders.
        slopes=axes[j,1];tops=b[:,1]-axes[j,0]-slopes*np.where(slopes>0,b[:,2],b[:,0])
        bottoms=b[:,3]-axes[j,0]-slopes*np.where(slopes>0,b[:,0],b[:,2])
        top=centre+tops.min()-.12*hh;bottom=centre+bottoms.max()+.12*hh
        poly=np.vstack([np.c_[xs,top],np.c_[xs[::-1],bottom[::-1]]]).tolist()
        mapped.append(dict(q,polygon=poly));audit.append(dict(row=j,status='native component envelope',components=use,ambiguous=uncertain[j]))
    if domains is not None:
        from shapely.geometry import Polygon
        for j,rules in enumerate(domains):
            shape=Polygon(mapped[j]['polygon'])
            for rule in rules:
                path=np.asarray(rule['path']);y0,y1=shape.bounds[1],shape.bounds[3]
                if y0<rule['y0'] or y1>rule['y1']:
                    audit[j]['domain_unknown']=True;continue
                yy=np.r_[y0,path[(path[:,1]>y0)&(path[:,1]<y1),1],y1];xx=np.interp(yy,path[:,1],path[:,0])
                edge=crop.shape[1] if rule['side']>0 else 0
                half=Polygon(np.vstack([np.c_[xx,yy],[edge,y1],[edge,y0]]))
                shape=shape.intersection(half)
            if shape.geom_type=='Polygon' and not shape.is_empty:mapped[j]=dict(mapped[j],polygon=list(shape.exterior.coords)[:-1])
            else:audit[j]['domain_unknown']=True
    mapped,gaps=separate_bands(crop,mapped,h,ink,stats,labels,owner,request_mode=request_mode,axes=axes if request_mode else None,supports=supports,target_rows=target_rows)
    coverage=[];containers={}
    for r in audit:
        r['gaps']=[q for q in gaps if r['row'] in q['rows']]
        if request_mode:
            r['supports']=supports[r['row']]
            r['domain_unknown']=r.get('domain_unknown',False) or any(q.get('unknown') for q in domains[r['row']])
        q=mapped[r['row']];a,b,c,d=roi(bbox(q),crop.shape);m=np.zeros((d-b,c-a),np.uint8);cv2.fillPoly(m,[np.rint(np.asarray(q['polygon'])-[a,b]).astype(int)],1)
        counts=np.bincount(labels[b:d,a:c][m>0],minlength=n);ls=np.flatnonzero(counts)
        r['foreign_components']=[int(k) for k in ls if k in owner and owner[k]!=r['row'] and stats[k,3]>.3*h and counts[k]>max(2,.02*h*h)]
        # Reuse the coverage already measured for the inherited foreign-body
        # decision. Unassigned ink is not background, and that decision does
        # not certify the completeness or unique ownership of this envelope.
        present={int(k):int(counts[k]) for k in ls if k}
        coverage.append(present)
        for k in present:containers.setdefault(k,[]).append(r['row'])
    for r,present in zip(audit,coverage):
        j=r['row'];records=[]
        for k,count in present.items():
            others=[i for i in containers[k] if i!=j]
            assignment=owner.get(k)
            state=('shared' if others else 'partial' if count!=int(stats[k,4]) else
                   'contained_unassigned' if assignment is None else
                   'contained_assigned' if assignment==j else 'assignment_conflict')
            records.append(dict(component=k,pixels=count,total_pixels=int(stats[k,4]),
                                assigned_row=assignment,other_rows=others,state=state))
        r['support_accounting']=dict(
            census='request-local M17 mean-paper CC8 labels',population=len(stats)-1,
            present=records,outside_polygon=len(stats)-1-len(present),
            assigned_but_absent=[k for k in r.get('components',[]) if k not in present],
            semantics='Threshold-mask containment only; neither semantic attachment nor print source. Outside the mask is unobserved, not blank.',
            complete_support=None)
    if request_mode:
        from .type_completion import corridor_hulls
        mapped= corridor_hulls(mapped,audit,ink,labels,stats,h,target_rows if target_rows is not None else set(range(len(rows))),axes=axes,retain_support=retain_support)
    return mapped,audit


def separate_bands(crop,rows,h,ink,stats,labels,owner,*,request_mode=False,axes=None,supports=None,target_rows=None):
    """One whitespace corridor between neighboring rectified row bands.

    Native connected components are barriers, including dots and accents. A
    corridor that cuts any component is rejected and its bands remain unready.
    This separates row envelopes; the page displacement remains shared.
    """
    from .geometry_rows import valley_path,valley_grid
    from .geometry import line_axis
    from .contracts import bbox
    from shapely.geometry import Polygon,LineString
    from shapely.ops import split
    shapes=[Polygon(np.asarray(q['polygon'],float)) for q in rows];boxes=np.array([bbox(q) for q in rows]);axes=np.array([line_axis(q) for q in rows]) if axes is None else np.asarray(axes,float);audit=[]
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
            if request_mode and target_rows is not None and i not in target_rows and j not in target_rows:continue
            m=mid[j];ys=axes[:,0]+axes[:,1]*m
            between=(boxes[:,0]<m)&(m<boxes[:,2])&(np.minimum(yi[j],yj[j])<ys)&(ys<np.maximum(yi[j],yj[j]))
            between[[i,j]]=False
            if not between.any():pairs.append((i,int(j),l[j],r[j],yi[j]<yj[j]))
    if request_mode:
        finite=[]
        for i,j,l,r,above in pairs:
            for a,b in supports[i]:
                for c,d in supports[j]:
                    left=max(l,a,c);right=min(r,b,d)
                    if right>left:finite.append((i,j,left,right,above))
        pairs=finite
    for i,j,l,r,i_above in pairs:
            up,down=(i,j) if i_above else (j,i)
            # There is no row-ownership conflict when these envelopes do not
            # overlap and neither holds another row's assigned native ink.
            if supports is None and shapes[i].distance(shapes[j])>.15*h:continue
            a=max(0,int(l));c=min(crop.shape[1],int(r)+1);xx=np.arange(a,c)
            y1=axes[up,0]+axes[up,1]*xx;y2=axes[down,0]+axes[down,1]*xx
            b=max(0,int(y1.min()));d=min(crop.shape[0],int(y2.max())+1)
            if d-b<3 or c-a<3:continue
            grid=valley_grid((d-b,c-a),h);gy,gx,_=grid
            yy=(gy+b)[:,None];midline=(y1[gx]+y2[gx])/2
            solid=cv2.dilate(ink[b:d,a:c],np.ones((max(1,round(.1*h)),max(1,round(.1*h))),np.uint8))
            # Native dilation and border context stay intact. Cost outside the
            # solver's fixed sample coordinates was allocated but never read.
            permitted=(yy>y1[gx]+.2*h)&(yy<y2[gx]-.2*h)
            cost=np.where(permitted,solid[np.ix_(gy,gx)].astype(float)*1e3+.005*((yy-midline)/h)**2,1e6)
            path=valley_path(cost,h,grid=grid)+b
            # Exact native crossing check, not just a low sampled path cost.
            crossing=[]
            ids=np.flatnonzero((stats[:,0]<c)&(stats[:,0]+stats[:,2]>a)&(stats[:,1]<d)&(stats[:,1]+stats[:,3]>b))
            for k in ids:
                if k==0:continue
                x,y,w,z,_=stats[k];lo=max(a,x);hi=min(c,x+w)
                cut=path[lo-a:hi-a]
                if y>cut.max() or y+z<cut.min():continue
                iy,ix=np.nonzero(labels[y:y+z,lo:hi]==k);delta=iy+y-path[ix+lo-a]
                if len(delta) and ((delta.min()<.5 and delta.max()>-.5) if request_mode else (delta.min()<-.04*h and delta.max()>.04*h)):crossing.append(int(k))
            if request_mode and crossing:
                path=refine_corridor(ink,a,c,y1,y2,path,stats[crossing],h)
                crossing=[]
                for k in ids:
                    if k==0:continue
                    x,y,w,z,_=stats[k];lo=max(a,x);hi=min(c,x+w)
                    iy,ix=np.nonzero(labels[y:y+z,lo:hi]==k);delta=iy+y-path[ix+lo-a]
                    if len(delta) and delta.min()<.5 and delta.max()>-.5:crossing.append(int(k))
            accepted=not crossing
            audit.append(dict(rows=[up,down],accepted=accepted,crossing=crossing,path=np.c_[xx,path].tolist()))
            if not accepted:continue
            if request_mode:
                # The clipping geometry consumes every native path point. Restrict
                # it to the witnessed common span; no flat end-axis extrapolation.
                pts=np.vstack([[xx[0]-.5,path[0]],np.c_[xx,path],[xx[-1]+.5,path[-1]]])
                for k,above in [(up,True),(down,False)]:
                    outer=crop.shape[0]+1 if above else -1
                    forbidden=Polygon(np.vstack([pts,[xx[-1]+.5,outer],[xx[0]-.5,outer]]))
                    clipped=shapes[k].difference(forbidden)
                    if clipped.geom_type=='Polygon' and not clipped.is_empty:
                        shapes[k]=clipped
            else:
                sample=np.unique(np.r_[np.arange(0,len(xx),max(1,round(.25*h))),len(xx)-1])
                pts=np.c_[xx[sample],path[sample]];pts=np.vstack([[min(boxes[i,0],boxes[j,0])-h,path[0]],pts,[max(boxes[i,2],boxes[j,2])+h,path[-1]]]);cut=LineString(pts)
                for k,above in [(up,True),(down,False)]:
                    pieces=list(split(shapes[k],cut).geoms)
                    if len(pieces)>1:
                        keep=[q for q in pieces if (q.representative_point().y<np.interp(q.representative_point().x,xx,path))==above]
                        if len(keep)==1:shapes[k]=keep[0]
    return [dict(q,polygon=list((shapes[i].simplify(0,preserve_topology=True) if request_mode else shapes[i]).exterior.coords)[:-1]) for i,q in enumerate(rows)],audit


def rule_edges(domains,ink,labels,*,stats=None):
    """Observe the ink touched by each already accepted finite rule path.

    This does not discover rules. Missing path samples leave the domain
    unknown; no centreline is substituted for an unobserved ink edge.
    """
    prepared={};edges={};out=[]
    for rules in domains:
        sides=[]
        for rule in rules:
            key=rule['rule_id']
            if key not in prepared:
                p=np.asarray(rule['path']);ys=np.arange(max(0,int(np.ceil(rule['y0']))),min(ink.shape[0],int(np.floor(rule['y1']))+1))
                xs=np.rint(np.interp(ys,p[:,1],p[:,0])).astype(int)
                valid=(xs>=0)&(xs<ink.shape[1]);ls=np.zeros(len(ys),int);ls[valid]=labels[ys[valid],xs[valid]]
                ids=np.unique(ls[ls>0])
                # CC boxes bound every pixel of the nominated labels exactly;
                # unrelated page columns cannot enter this min/max observation.
                leftmost=int(stats[ids,0].min()) if stats is not None and len(ids) else 0
                rightmost=int((stats[ids,0]+stats[ids,2]).max()) if stats is not None and len(ids) else ink.shape[1]
                bar=np.isin(labels[ys,leftmost:rightmost],ids) if len(ids) else np.zeros((len(ys),rightmost-leftmost),bool)
                xx=np.arange(leftmost,rightmost);seen=bar.any(1)
                left=np.where(seen,np.where(bar,xx,ink.shape[1]).min(1)-1,np.nan)
                right=np.where(seen,np.where(bar,xx,-1).max(1)+1,np.nan)
                prepared[key]=(ys,np.asarray(left),np.asarray(right))
            side_key=(key,rule['side'])
            if side_key not in edges:
                ys,left,right=prepared[key];edge=right if rule['side']>0 else left
                good=np.isfinite(edge)
                edges[side_key]=dict(path=np.c_[edge[good],ys[good]].tolist() if good.any() else rule['path'],
                    unknown=not bool(good.all()),observed_rows=ys[good].tolist())
            sides.append(dict(rule,**edges[side_key]))
        out.append(sides)
    return out


def body_supports(supports,grouped,stats,domains):
    """Observed spans plus whole native bodies, in pixel-centre coordinates."""
    out=[]
    for j,spans in enumerate(supports):
        ranges=list(spans)+[[float(stats[k,0])-.5,float(stats[k,0]+stats[k,2])-.5] for k in grouped[j]]
        limits=[(rule['side'],float(np.max(np.asarray(rule['path'])[:,0])) if rule['side']>0 else float(np.min(np.asarray(rule['path'])[:,0]))) for rule in domains[j]]
        clipped=[]
        for lo,hi in ranges:
            for side,edge in limits:
                if side>0:lo=max(lo,edge)
                else:hi=min(hi,edge)
            if hi>lo:clipped.append([lo,hi])
        merged=[]
        for lo,hi in sorted(clipped):
            if merged and lo<=merged[-1][1]+1:merged[-1][1]=max(hi,merged[-1][1])
            else:merged.append([lo,hi])
        out.append(merged)
    return out


def refine_corridor(ink,a,c,upper,lower,proposal,crossing_stats,h):
    """Refine the crossed portions of a coarse proposal on native ink.

    The y search is bounded by the observed row axes, not by the possibly
    incorrect coarse path. Uncrossed neighbouring columns anchor each repair.
    Whole-component verification remains the caller's acceptance decision.
    """
    from .geometry_rows import valley_path
    spans=[]
    for x,y,w,z,area in sorted(crossing_stats.tolist()):
        lo=max(a,x-max(1,round(.25*h)));hi=min(c,x+w+max(1,round(.25*h)))
        if spans and lo<=spans[-1][1]:spans[-1][1]=max(hi,spans[-1][1])
        else:spans.append([lo,hi])
    path=proposal.copy()
    for lo,hi in spans:
        u=upper[lo-a:hi-a];v=lower[lo-a:hi-a]
        b=max(0,int(np.floor(u.min())));d=min(ink.shape[0],int(np.ceil(v.max()))+1)
        yy=np.arange(b,d)[:,None];mid=(u+v)/2
        allowed=(yy>u+.2*h)&(yy<v-.2*h)
        cost=np.where(allowed,(ink[b:d,lo:hi]>0)*1e3+.005*((yy-mid)/h)**2,1e6)
        grid=(np.arange(d-b),np.arange(hi-lo),hi-lo)
        path[lo-a:hi-a]=valley_path(cost,h,grid=grid,max_step=1)+b
    return path
