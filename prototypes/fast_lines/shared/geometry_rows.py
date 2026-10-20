"""Rows actually inside one OCR segment. Experimental native rendering first.

No page identifiers, model line list, owner labels or external text are inputs.
Coordinates of the strip are page x and y minus the segment's straight slope.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from shapely.geometry import Polygon,LineString,box
from shapely.ops import split as split_shape
from .geometry import height_proxy, line_axis
from .contracts import bbox
from .geometry_filter import gaussian_columns
from ..layout_barriers.fast import verify_rule


def valley_grid(shape,h):
    """The existing gap solver's sampled coordinates in its unchanged ROI."""
    dx=max(1,round(.25*h));dy=max(1,round(.08*h))
    xs=np.unique(np.r_[np.arange(0,shape[1],dx),shape[1]-1])
    return np.arange(0,shape[0],dy),xs,shape[1]


def valley_path(cost,h,*,grid=None,max_step=None):
    """Minimum-cost continuous gap, with letter-scale displacement steps."""
    dx=max(1,round(.25*h));dy=max(1,round(.08*h))
    if grid is None:
        ys,xs,width=valley_grid(cost.shape,h);a=cost[np.ix_(ys,xs)]
    else:
        # Caller evaluated the same cost only at coordinates the solver reads.
        # This is not a resized image or a different gap search lattice.
        ys,xs,width=grid;a=cost
    n,w=a.shape;v=a[:,0].copy();back=np.zeros((n,w),np.int16)
    jumps=max(1,round(dx/dy)) if max_step is None else max_step;offsets=np.arange(-jumps,jumps+1)
    previous=np.arange(n)[None,:]-offsets[:,None]
    valid=(previous>=0)&(previous<n);previous=np.clip(previous,0,n-1)
    penalty=.005*abs(offsets[:,None]);rows=np.arange(n)
    for x in range(1,w):
        options=np.where(valid,v[previous]+penalty,1e6)
        best=options.argmin(0);v=options[best,rows]+a[:,x]
        back[:,x]=previous[best,rows]
    path=np.empty(w,int);path[-1]=v.argmin()
    for x in range(w-1,0,-1):path[x-1]=back[path[x],x]
    return np.interp(np.arange(width),xs,ys[path])


def strip(gray, item, h, scale=1.):
    p=np.asarray(item['polygon'],float)
    a=line_axis(item);slope=float(np.clip(a[1],-.25,.25))
    if np.ptp(p[:,1])>np.ptp(p[:,0]):slope=0. # stacked numeric cells, not rotated text
    x0=max(0,int(np.floor(p[:,0].min()))-2)
    x1=min(gray.shape[1],int(np.ceil(p[:,0].max()))+3)
    pp=p.copy();pp[:,1]-=slope*(pp[:,0]-x0)
    y0=int(np.floor(pp[:,1].min()-h));y1=int(np.ceil(pp[:,1].max()+h))
    w=max(1,round((x1-x0)*scale));hh=max(1,round((y1-y0)*scale))
    xs=x0+np.arange(w)/scale;ys=y0+np.arange(hh)/scale
    mx=np.broadcast_to(xs[None,:],(hh,w)).astype(np.float32)
    my=(ys[:,None]+slope*(xs[None,:]-x0)).astype(np.float32)
    g=cv2.remap(gray,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
    mask=np.zeros(g.shape,np.uint8)
    cv2.fillPoly(mask,[np.rint((pp-[x0,y0])*scale).astype(np.int32)],1)
    return g,mask,dict(x0=x0,y0=y0,slope=slope,scale=scale)


def to_page(points, tr):
    q=np.array(points,dtype=float).reshape(-1,2)/tr['scale']
    q[:,1]+=tr['y0']+tr['slope']*q[:,0];q[:,0]+=tr['x0']
    return q.tolist()


def mark_bodies(cx,cy,boxes,h):
    """Native's existing finite detached-mark relation, without a second vote."""
    if not len(boxes):return []
    dx=np.maximum.reduce([boxes[:,0]-cx,cx-boxes[:,2],np.zeros(len(boxes))])
    dy=np.maximum.reduce([boxes[:,1]-cy,cy-boxes[:,3],np.zeros(len(boxes))])
    distance=np.hypot(dx,dy);best=distance.min()
    return np.flatnonzero(distance<=best+.08*h).tolist() if best<=.4*h else []


def native(gray,item,h,*,route='slow',measure_only=False,prepared=None):
    start=perf_counter();scale=1. if route=='slow' else min(1.,20/h)
    g,mask,tr=strip(gray,item,h,scale);hs=h*scale
    blur=cv2.GaussianBlur(g,(3,3),.6)
    threshold,_=cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    ink=(blur<threshold).astype(np.uint8)
    # Rendering candidates comes from local density, not a whole-box row count.
    step=max(1,round(.5*hs));paths=[];sample_x=np.arange(0,g.shape[1],step)
    density=gaussian_columns(ink.astype(np.float32),.65*hs,.12*hs,sample_x)
    for column,x in enumerate(sample_x):
        peaks,_=find_peaks(density[:,column],distance=max(1,int(.7*hs)),prominence=.06,height=.08)
        used=set()
        for y in peaks:
            near=[(abs(t[-1][1]-y),k) for k,t in enumerate(paths) if k not in used and x-t[-1][0]<=1.5*hs and abs(t[-1][1]-y)<=.45*hs]
            if near:
                _,k=min(near);paths[k].append([x,int(y)]);used.add(k)
            else:paths.append([[x,int(y)]]);used.add(len(paths)-1)
    n,labels,stats,centres=cv2.connectedComponentsWithStats(ink,8)
    bodies=[];body_labels=[]
    for i,(x,y,w,hh,area) in enumerate(stats[1:],1):
        if not (.45*hs<=hh<=1.8*hs and .08*hs<=w<=3*hs and area>=.018*hs*hs):continue
        yy,xx=np.nonzero(labels[y:y+hh,x:x+w]==i);inside=mask[y+yy,x+xx]>0
        # Full centre and central body must lie in the polygon. Edge grazes
        # remain in the explicit display but cannot witness a second word.
        cx,cy=centres[i];core=(abs(xx+x-cx)<.2*hs)&(abs(yy+y-cy)<.15*hs)
        complete=bool(core.any() and inside[core].all() and inside.all())
        extent=float(np.ptp(yy[inside])+1) if inside.any() else 0.
        body_labels.append(i)
        bodies.append(dict(bbox=[int(x),int(y),int(x+w),int(y+hh)],centre=[float(cx),float(cy)],complete=complete,inside_height_h=extent/hs,area=int(area)))
    body_centres=np.asarray([b['centre'] for b in bodies]).reshape(-1,2)
    tracks=[];body_tracks=[[] for _ in bodies];compact=g.shape[1]<4*hs
    pb=bbox(item);orientation_ambiguous=bool(pb[3]-pb[1]>pb[2]-pb[0])
    for path in paths:
        p=np.asarray(path);span=p[-1,0]-p[0,0]
        if span<(.4 if compact else 1)*hs:continue
        cx,cy=body_centres.T
        near=np.flatnonzero((cx>=p[0,0]-.5*hs)&(cx<=p[-1,0]+.5*hs)&(abs(cy-np.interp(cx,p[:,0],p[:,1]))<.35*hs)).tolist()
        for bi in near:body_tracks[bi].append(len(tracks))
        ids=[];run=[];runs=[]
        for i in sorted(near,key=lambda k:bodies[k]['bbox'][0]):
            if not bodies[i]['complete']:
                if run:runs.append(run);run=[]
                continue
            if run and bodies[i]['bbox'][0]-bodies[run[-1]]['bbox'][2]>hs:
                runs.append(run);run=[]
            run.append(i);ids.append(i)
        if run:runs.append(run)
        words=[r for r in runs if len(r)>=2 and max(bodies[i]['bbox'][2] for i in r)-min(bodies[i]['bbox'][0] for i in r)>=1.2*hs]
        tracks.append(dict(path=to_page(p,tr),body_ids=ids,word_runs=words,word=bool(words),span_h=float(span/hs),local_path=p))
    valleys=[];rules=[];bridges=[];attachments={}
    # A detached accent is still owned by its nearby body. Preserve that local
    # connection as well as each connected ink component. Ambiguous equally
    # near bodies are all protected, so uncertainty can only veto a cut.
    bs=np.asarray([b['bbox'] for b in bodies],float).reshape(-1,4)
    for k,(bx,by,bw,bh,area) in ([] if measure_only else enumerate(stats[1:],1)):
        if not len(bs) or not (bh<.45*hs and bw<.8*hs and area>=max(2,.004*hs*hs)):continue
        cx,cy=centres[k]
        if not mask[min(len(mask)-1,round(cy)),min(mask.shape[1]-1,round(cx))]:continue
        near=mark_bodies(cx,cy,bs,hs)
        if prepared is not None and near:attachments[k]=near
        for j in near:
            bridges.append(dict(component=k,body=int(j),local=[[float(cx),float(cy)],bodies[j]['centre']]))
    valley_cost=None;component_pixels=None
    for i,one in enumerate(tracks):
        if orientation_ambiguous:break # narrow vertical label or number stack: unresolved
        if not one['word']:continue
        for j,two in enumerate(tracks[i+1:],i+1):
            if not two['word']:continue
            p=one['local_path'];q=two['local_path'];lo=max(p[0,0],q[0,0]);hi=min(p[-1,0],q[-1,0])
            if hi-lo<(.4 if compact else 1.2)*hs:continue
            xs=np.arange(lo,hi+1);yp=np.interp(xs,p[:,0],p[:,1]);yq=np.interp(xs,q[:,0],q[:,1])
            if np.median(yp-yq)>0:p,q=q,p;yp,yq=yq,yp
            if np.min(yq-yp)<.7*hs:continue
            midpoint=(lo+hi)/2;u=np.interp(midpoint,p[:,0],p[:,1]);d=np.interp(midpoint,q[:,0],q[:,1])
            if any(t['word'] and k not in (i,j) and t['local_path'][0,0]<=midpoint<=t['local_path'][-1,0] and u+.35*hs<np.interp(midpoint,t['local_path'][:,0],t['local_path'][:,1])<d-.35*hs for k,t in enumerate(tracks)):continue
            # Both body runs must witness the same interval. This prevents a
            # distant word, or two successive pieces of one row, authorizing it.
            def support(t):
                return [k for k in t['body_ids'] if lo-.5*hs<=bodies[k]['centre'][0]<=hi+.5*hs]
            if min(len(support(one)),len(support(two)))<2:continue
            if measure_only:
                valleys.append(dict(tracks=[i,j],accepted=False,path=[]));continue
            if valley_cost is None:
                connected=ink.copy()
                for bridge in bridges:
                    a,b=np.rint(bridge['local']).astype(int);cv2.line(connected,tuple(a),tuple(b),1,max(1,round(.04*hs)))
                # A gap is empty space. Prefer a continuous empty corridor to
                # a lower *average* density path that crosses a short accent.
                guard=cv2.dilate(connected,np.ones((max(1,round(.08*hs)),max(1,round(.25*hs))),np.uint8))
                valley_cost=guard.astype(np.float32)*1e3+.05*cv2.GaussianBlur(connected.astype(np.float32),(0,0),.3*hs,sigmaY=.07*hs)
                component_pixels=[]
                for k,(bx,by,bw,bh,area) in enumerate(stats[1:],1):
                    if bw<.6*hs and bh>3*hs:
                        corners=np.asarray(to_page([[bx,by],[bx+bw,by+bh]],tr));lo=corners.min(0);hi=corners.max(0)
                        # Observe beyond this segment: an isolated capital I
                        # must not become a printed-rule certificate.
                        candidate=dict(bbox=[lo[0],lo[1]-3*h,hi[0],hi[1]+3*h])
                        rule,reason=verify_rule(gray,candidate,h)
                        if rule is not None:
                            rules.append(dict(component=k,rule=rule));continue
                    iy,ix=np.nonzero((labels[by:by+bh,bx:bx+bw]==k)&(mask[by:by+bh,bx:bx+bw]>0))
                    if len(ix):component_pixels.append((k,iy+by,ix+bx))
            xx=np.arange(g.shape[1]);up=np.interp(xx,p[:,0],p[:,1]);down=np.interp(xx,q[:,0],q[:,1]);mid=(up+down)/2
            yy=np.arange(g.shape[0])[:,None]
            # Ink valley, constrained between the actual row bodies. A mild
            # centre preference chooses stable positions in a wide white gap.
            permitted=(yy>up+.25*hs)&(yy<down-.25*hs)
            cost=np.where(permitted,valley_cost+.005*((yy-mid)/hs)**2,1e6)
            y=valley_path(cost,hs)
            y=gaussian_filter1d(y,max(1.,.15*hs))
            # Reject a valley that cuts a complete native body. Large initials
            # and joined-script ambiguities therefore remain explicit unknowns.
            stride=max(1,round(.15*hs));sample=np.unique(np.r_[np.arange(0,len(xx),stride),len(xx)-1])
            y=np.interp(xx,xx[sample],y[sample])
            outside_corridor=bool(np.any((y<=up+.25*hs)|(y>=down-.25*hs)))
            crossing=[]
            # All components participate, including oversized initials. Body
            # filters establish word evidence, never permission to cut ink.
            for k,iy,ix in component_pixels:
                delta=iy-y[ix]
                if delta.min()<-.08*hs and delta.max()>.08*hs:crossing.append(k)
            mark_crossing=[]
            for k,bridge in enumerate(bridges):
                points=np.asarray(bridge['local']);delta=points[:,1]-np.interp(points[:,0],xx,y)
                if delta.min()<0<delta.max():mark_crossing.append(k)
            row_crossing=[]
            for k,t in enumerate(tracks):
                if not t['word']:continue
                points=np.asarray([bodies[b]['centre'] for b in t['body_ids']])
                delta=points[:,1]-np.interp(points[:,0],xx,y)
                if delta.min()<-.1*hs and delta.max()>.1*hs:row_crossing.append(k)
            duplicate=any(np.median(abs(y-v['_y']))<.4*hs for v in valleys)
            if duplicate:continue
            valleys.append(dict(path=to_page(np.c_[xx[sample],y[sample]],tr),tracks=[i,j],crossing=crossing,mark_crossing=mark_crossing,row_crossing=row_crossing,outside_corridor=outside_corridor,accepted=not (crossing or mark_crossing or row_crossing or outside_corridor),_y=y))
    if prepared is not None and not measure_only:
        # Same-call observations; arrays live only until this parent's consumer
        # returns. Public diagnostics retain page coordinates and no arrays.
        prepared.update(gray=g,mask=mask,ink=ink,labels=labels,stats=stats,centres=centres,
                        transform=tr,height=hs,threshold=float(threshold),
                        tracks=[t['local_path'] for t in tracks],body_labels=body_labels,
                        body_tracks=body_tracks,body_boxes=bs,attachments=attachments)
    for t in tracks:del t['local_path']
    for v in valleys:v.pop('_y',None)
    for bridge in bridges:bridge['path']=to_page(bridge.pop('local'),tr)
    for b in bodies:
        x,y,xx,yy=b['bbox'];b['polygon']=to_page([[x,y],[xx,y],[xx,yy],[x,yy]],tr)
        b['centre']=to_page([b['centre']],tr)[0]
    return dict(tracks=tracks,bodies=bodies,valleys=valleys,bridges=bridges,rules=rules,orientation_ambiguous=orientation_ambiguous,height=h,route=route,seconds=perf_counter()-start)


def partition(item,record):
    """Exact vector partition; union is the original, with no recovered ink."""
    pieces=[Polygon(np.asarray(item['polygon'],float))]
    if not pieces[0].is_valid:return [],'invalid original polygon'
    for v in record['valleys']:
        if not v['accepted']:continue
        path=np.asarray(v['path']);direction=path[-1]-path[0]
        if direction[0]<=0:continue
        # Ensure the cutting curve exits both ends of the original polygon.
        path=np.vstack([path[0]-direction,path,path[-1]+direction])
        cut=LineString(path);new=[]
        for p in pieces:new.extend(split_shape(p,cut).geoms)
        pieces=new
    if len(pieces)<2:return [],'no certified internal valley'
    return [list(map(list,p.exterior.coords))[:-1] for p in sorted(pieces,key=lambda p:p.centroid.y)],'native word runs and ink valley'


def confirmed_partition(item,record,*,prepared=None):
    pieces,reason=partition(item,record);census=[]
    for p in pieces:
        contour=np.asarray(p,np.float32)
        owned={i for i,b in enumerate(record['bodies']) if b['complete'] and cv2.pointPolygonTest(contour,tuple(b['centre']),False)>=0}
        if prepared is None:
            if not any(set(run)<=owned for t in record['tracks'] for run in t['word_runs']):
                return [],'piece lacks a whole horizontal body run'
        else:
            found=[j for j,t in enumerate(record['tracks']) if any(set(run)<=owned for run in t['word_runs'])]
            if not found:return [],'piece lacks a whole horizontal body run'
            census.append(found)
    if prepared is not None:
        prepared['partition_tracks']=census
        prepared['partition_polygons']=pieces
    return pieces,reason


def from_page(points,tr):
    """Exact inverse of this native call's rectification, before rasterisation."""
    p=np.asarray(points,float).reshape(-1,2).copy();p[:,0]-=tr['x0']
    p[:,1]-=tr['y0']+tr['slope']*p[:,0]
    return p*tr['scale']


def _filled(shape,polygon):
    mask=np.zeros(shape,np.uint8)
    cv2.fillPoly(mask,[np.rint(polygon).astype(np.int32)],1)
    return mask


def whole_children(gray,item,record,pieces,prepared,*,forbidden_regions=(),smooth_exports=False):
    """Conditional extent replacement; unknown preserves the atomic old split.

    Discovery and child identity are already accepted. Component membership
    reuses native's finite body/track and detached-mark relations, not another
    nearest-row classifier. Prepared observations belong to that full call.
    """
    from .type_completion import raster_envelope
    from .geometry_field_detector import refine_corridor
    receipt=dict(accepted=False,first_failure=None)
    def unknown(why):
        receipt['first_failure']=why
        return [],receipt
    if not prepared:return unknown('full-parent prepared context unavailable')
    labels=prepared['labels'];stats=prepared['stats'];tr=prepared['transform']
    hs=prepared['height'];shape=labels.shape;tracks=prepared['tracks']
    same=('partition_tracks' in prepared and len(prepared['partition_polygons'])==len(pieces)
          and all(np.array_equal(a,b) for a,b in zip(prepared['partition_polygons'],pieces)))
    if same:targets=prepared['partition_tracks']
    else:
        # Diagnostic callers may use the legacy partition API. The real
        # analyze caller passes this exact unchanged-geometry census once.
        targets=[]
        for p in pieces:
            contour=np.asarray(p,np.float32)
            owned={i for i,b in enumerate(record['bodies']) if b['complete'] and cv2.pointPolygonTest(contour,tuple(b['centre']),False)>=0}
            found=[j for j,t in enumerate(record['tracks']) if any(set(run)<=owned for run in t['word_runs'])]
            targets.append(found)
    receipt['whole_word_tracks_per_child']=targets
    if any(len(t)!=1 for t in targets) or len({t[0] for t in targets})!=len(pieces):
        return unknown('child lacks a unique whole word track')
    targets=[t[0] for t in targets];owner={}
    for label,ts in zip(prepared['body_labels'],prepared['body_tracks']):
        if len(ts)==1:owner[label]=ts[0]
    # Native already observed whether each body intersects this same parent.
    # This exact necessary prerequisite needs no second mask-support scan.
    missing_bodies=sorted(label for bi,label in enumerate(prepared['body_labels'])
                          if record['bodies'][bi]['inside_height_h']>0 and label not in owner)
    if missing_bodies:
        receipt['unassigned_parent_components']=missing_bodies
        return unknown('parent component lacks unique native body/mark identity')
    parent_counts=np.bincount(labels[prepared['mask']>0],minlength=len(stats))
    present=set(np.flatnonzero(parent_counts))-{0}
    edge=(stats[:,0]==0)|(stats[:,1]==0)|(stats[:,0]+stats[:,2]>=shape[1])|(stats[:,1]+stats[:,3]>=shape[0])
    excluded=set(map(int,np.flatnonzero(edge & (parent_counts==0))))-{0}
    attachments=dict(prepared['attachments'])
    body_labels=set(prepared['body_labels'])
    for label,(x,y,w,h,area) in enumerate(stats[1:],1):
        if label in attachments or label in body_labels or label in excluded:continue
        if h<.45*hs and w<.8*hs and area>=max(2,.004*hs*hs):
            cx,cy=prepared['centres'][label]
            near=mark_bodies(cx,cy,prepared['body_boxes'],hs)
            if near:attachments[label]=near
    for label,bs in attachments.items():
        if label in body_labels:continue
        ts={owner.get(prepared['body_labels'][b],-1) for b in bs}
        if len(ts)==1 and -1 not in ts:owner[label]=ts.pop()
    unsupported=sorted(present-set(owner));receipt['unassigned_parent_components']=unsupported
    if unsupported:return unknown('parent component lacks unique native body/mark identity')
    groups=[sorted(k for k,t in owner.items() if t==target and k not in excluded) for target in targets]
    receipt.update(admitted_components=groups,outside_boundary_components=sorted(excluded))
    # Zero-parent boundary fragments stay unadmitted. A native body on a
    # selected track is nevertheless evidence of unsupported outer continuation.
    outer=[label for label,ts in zip(prepared['body_labels'],prepared['body_tracks'])
           if label in excluded and any(t in targets for t in ts)]
    receipt['outside_boundary_bodies_on_selected_tracks']=outer
    if outer:return unknown('selected native body track continues through a strip-cut outside body')
    cut=[k for group in groups for k in group if edge[k]];receipt['retained_boundary_components']=cut
    if cut:return unknown('admitted parent member truncated by strip boundary')
    if any(not g for g in groups):return unknown('empty whole-component child')
    # Certify the existing proposal on full members in its finite corridor.
    relevant=sorted(k for g in groups for k in g);certificates=[]
    for v in record['valleys']:
        if not v['accepted']:continue
        up,down=[tracks[t] for t in v['tracks']]
        if np.median(up[:,1])>np.median(down[:,1]):up,down=down,up
        a=max(0,int(np.ceil(max(up[0,0],down[0,0]))));c=min(shape[1],int(np.floor(min(up[-1,0],down[-1,0])))+1)
        if c<=a:return unknown('unsupported finite internal corridor')
        xs=np.arange(a,c);vp=from_page(v['path'],tr);path=np.interp(xs,vp[:,0],vp[:,1])
        def crossings(path):
            bad=[]
            for k in relevant:
                x,y,w,h,_=stats[k];yy,xx=np.nonzero(labels[y:y+h,x:x+w]==k);xx+=x;yy+=y
                at=(xx>=a)&(xx<c);delta=yy[at]-path[xx[at]-a]
                if len(delta) and delta.min()<.5 and delta.max()>-.5:bad.append(k)
            return bad
        bad=crossings(path);before=list(bad)
        if bad:path=refine_corridor(prepared['ink'],a,c,np.interp(xs,up[:,0],up[:,1]),np.interp(xs,down[:,0],down[:,1]),path,stats[bad],hs);bad=crossings(path)
        certificates.append(dict(tracks=v['tracks'],finite_x=[a,c],crossing_before=before,crossing_after=bad))
        if bad:return unknown('whole member crosses refined half-pixel corridor')
    receipt['certificates']=certificates;polygons=[]
    if not smooth_exports:
        for group in groups:
            keep=np.zeros(len(stats),np.uint8);keep[group]=1;support=keep[labels]
            p=raster_envelope(support,[0,0]);m=_filled(shape,p)
            counts=np.bincount(labels[m>0],minlength=len(stats));actual=set(np.flatnonzero(counts))-{0}
            if actual!=set(group) or any(counts[k]!=stats[k,4] for k in group):
                return unknown('rectified hull clips a member or contains foreign support')
            polygons.append(to_page(p,tr))
    # Actual original-page raster, with the same observed Gaussian threshold.
    # Source components are a local export audit, not a new row/mark estimator.
    # Inverse-mapped strip centres alone cannot certify interpolated source ink.
    corners=to_page([[0,0],[shape[1]-1,0],[shape[1]-1,shape[0]-1],[0,shape[0]-1]],tr)
    allp=np.asarray(corners);lo=np.maximum(0,np.floor(allp.min(0))-2).astype(int)
    hi=np.minimum(gray.shape[::-1],np.ceil(allp.max(0))+3).astype(int);a,b=lo;c,d=hi
    masks=[_filled((d-b,c-a),np.asarray(p)-lo) for p in polygons]
    for q in forbidden_regions:
        forbidden=_filled((d-b,c-a),np.asarray(q['polygon'])-lo)
        if any((m & forbidden).any() for m in masks):return unknown('export intersects forbidden footprint')
    source=cv2.GaussianBlur(gray[b:d,a:c],(3,3),.6)<prepared['threshold']
    n,source_labels,source_stats,_=cv2.connectedComponentsWithStats(source.astype(np.uint8),8)
    yy,xx=np.indices(source.shape);local=from_page(np.c_[xx.ravel()+a,yy.ravel()+b],tr)
    uv=np.rint(local).astype(int);inside=(uv[:,0]>=0)&(uv[:,0]<shape[1])&(uv[:,1]>=0)&(uv[:,1]<shape[0])
    mapped=np.zeros(source.size,np.int32);mapped[inside]=labels[uv[inside,1],uv[inside,0]];mapped=mapped.reshape(source.shape)
    # Export extent is tight in the final raster's own units. Include each
    # uniquely corresponding original component and every mapped native member
    # centre; padding of a rectified hull is not a page-space certificate.
    correspondence={};ambiguous=[]
    group_sets=list(map(set,groups))
    for k in range(1,n):
        x,y,w,h,count=source_stats[k];at=source_labels[y:y+h,x:x+w]==k
        ids=set(np.unique(mapped[y:y+h,x:x+w][at]))-{0}
        owners={j for j,g in enumerate(group_sets) if ids & g}
        if len(owners)==1:
            j=next(iter(owners))
            if ids-group_sets[j]:ambiguous.append(k)
            correspondence[k]=j
        elif owners:ambiguous.append(k)
    if ambiguous:return unknown('original component corresponds to competing native identities')
    page_polygons=[];page_supports=[]
    for j,group in enumerate(groups):
        support=np.isin(source_labels,[k for k,t in correspondence.items() if t==j]).astype(np.uint8)
        yy,xx=np.nonzero(np.isin(labels,group));points=np.rint(np.asarray(to_page(np.c_[xx,yy],tr))-lo).astype(int)
        support[points[:,1],points[:,0]]=1
        page_supports.append(support)
        if not smooth_exports:
            p=raster_envelope(support,lo);page_polygons.append(p.tolist())
    if smooth_exports:
        from .geometry_bands import smooth_band,shared_separator,band_polygon,polygon_mask,EDGE_CONVENTION
        bands=[]
        for j,support in enumerate(page_supports):
            band,why=smooth_band(support,lo,None,hs/tr['scale'],path=to_page(tracks[targets[j]],tr))
            if band is None:return unknown(why)
            bands.append(band)
        seams=[]
        for v in record['valleys']:
            if not v['accepted'] or not set(v['tracks'])<=set(targets):continue
            one,two=[targets.index(t) for t in v['tracks']]
            if np.median(bands[one]['top'])>np.median(bands[two]['top']):one,two=two,one
            vp=np.asarray(v['path']);left=int(np.ceil(max(vp[:,0].min(),bands[one]['x'][0],bands[two]['x'][0])))
            right=int(np.floor(min(vp[:,0].max(),bands[one]['x'][-1],bands[two]['x'][-1])))+1
            seam,why=shared_separator(bands[one],bands[two],page_supports[one],page_supports[two],lo,hs/tr['scale'],[left,right])
            if seam is None:return unknown(why)
            seams.append(dict(rows=[one,two],domain_x=[left,right],path=seam.tolist(),edge_convention=EDGE_CONVENTION))
        for band in bands:
            p,why=band_polygon(band)
            if p is None:return unknown(why)
            page_polygons.append(p.tolist())
        receipt.update(raster_edges=EDGE_CONVENTION,shared_separators=seams,smooth_export=True,
                       final_neighbour_qualification='Constructor siblings only; analyze requires explicit opt-in until both final compose neighbours qualify')
    polygons=page_polygons
    if smooth_exports:
        masks=[polygon_mask(source.shape,p,lo,half_open=True) for p in polygons]
    else:masks=[_filled(source.shape,np.asarray(p)-lo) for p in polygons]
    yy,xx=np.nonzero(labels);points=np.rint(np.asarray(to_page(np.c_[xx,yy],tr))-lo).astype(int)
    full_labels=labels[yy,xx]
    for j,group in enumerate(groups):
        included=masks[j][points[:,1],points[:,0]]>0
        counts=np.bincount(full_labels[included],minlength=len(stats))
        if set(np.flatnonzero(counts))-{0}!=set(group) or any(counts[k]!=stats[k,4] for k in group):
            receipt['native_page_delta']=dict(child=j,
                lost=[dict(component=k,lost=int(stats[k,4]-counts[k]),bbox=stats[k,:4].tolist()) for k in group if counts[k]!=stats[k,4]],
                added=[dict(component=int(k),pixels=int(counts[k]),total=int(stats[k,4]),bbox=stats[k,:4].tolist()) for k in np.flatnonzero(counts) if k and k not in group])
            return unknown('actual page raster changes rectified whole membership')
    for q in forbidden_regions:
        forbidden=_filled(source.shape,np.asarray(q['polygon'])-lo)
        if any((m & forbidden).any() for m in masks):return unknown('final export intersects forbidden footprint')
    losses=[];foreign=[];duplicates=[];members=[];foreign_details=[]
    for k in range(1,n):
        x,y,w,h,count=source_stats[k];at=source_labels[y:y+h,x:x+w]==k
        hits=[int(m[y:y+h,x:x+w][at].sum()) for m in masks]
        if k in correspondence:
            j=correspondence[k];members.append([k,j,int(count)])
            if hits[j]!=count:losses.append([k,j,int(count-hits[j])])
            if any(hits[t] for t in range(len(groups)) if t!=j):duplicates.append(k)
            if x==0 or y==0 or x+w==source.shape[1] or y+h==source.shape[0]:return unknown('original-page member touches audit boundary')
        elif any(hits):
            foreign.append(k);foreign_details.append(dict(component=k,bbox=[int(x+a),int(y+b),int(w),int(h)],hits=hits))
    receipt['page_membership']=dict(members=members,losses=losses,foreign=foreign,duplicates=duplicates,foreign_details=foreign_details)
    if losses or foreign or duplicates:return unknown('original-page export changes whole physical membership')
    if {j for _,j,_ in members}!=set(range(len(groups))):return unknown('no original-page members')
    if prepared.get('retain_support'):
        prepared['whole_page_supports']=[dict(points=np.c_[np.nonzero(m)[1]+a,np.nonzero(m)[0]+b],namespace='B native Gaussian/Otsu mapped original-page whole membership',path=np.asarray(to_page(tracks[targets[j]],tr)),image=gray,shape=gray.shape,height=prepared['height'] if 'height' in prepared else hs/tr['scale']) for j,m in enumerate(page_supports)]
    return polygons,receipt


def scout(gray,items,h=None,*,sampling='linear'):
    """Route 2: small local profiles request, but never authorize, a split."""
    start=perf_counter();h=h or height_proxy(items,gray.shape[::-1]);s=min(1.,8/h)
    if sampling not in ('area','linear'):raise ValueError(sampling)
    records=[];small=cv2.resize(gray,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if sampling=='area' else cv2.INTER_LINEAR)
    for i,q in enumerate(items):
        b=bbox(q)
        if q.get('page_field') or b[3]-b[1]>b[2]-b[0] or q.get('discounted'):
            records.append(dict(line=i,candidate=False,peaks=[],reason='shared page field already owns rows' if q.get('page_field') else ('tall polygon has unresolved orientation' if not q.get('discounted') else 'discounted')));continue
        p=np.asarray(q['polygon'])*s;lo=np.maximum(0,np.floor(p.min(0)).astype(int));hi=np.minimum(small.shape[::-1],np.ceil(p.max(0)).astype(int)+1)
        x0,y0=lo;x1,y1=hi;g=small[y0:y1,x0:x1];m=np.zeros(g.shape,np.uint8)
        if g.size==0:records.append(dict(line=i,candidate=False,peaks=[]));continue
        cv2.fillPoly(m,[np.rint(p-lo).astype(int)],1);tr=dict(x0=x0/s,y0=y0/s,slope=0,scale=s);hs=h*s
        threshold,_=cv2.threshold(g,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        ink=((g<threshold)&(m>0)).astype(np.float32)
        width=max(1,round(4*hs));nb=max(1,int(np.ceil(g.shape[1]/width)))
        padded=np.pad(ink,((0,0),(0,nb*width-g.shape[1])))
        p=padded.reshape(len(g),nb,width).mean(2)
        p=np.round(cv2.GaussianBlur(p,(1,0),0,sigmaY=.12*hs),6)
        samples=[]
        # Broad body bands, not an accent peak and the body of the same row.
        # Vectorized neighbour probes replace per-block scipy peak searches.
        gap=max(1,round(.23*hs));pad=np.pad(p,((gap,gap),(0,0)))
        peaks=(p>np.roll(p,1,0))&(p>=np.roll(p,-1,0))&(p>.06)&(pad[:-2*gap]>.06)&(pad[2*gap:]>.06)
        for k in np.flatnonzero(peaks.sum(0)>1):
            ys=np.flatnonzero(peaks[:,k])
            if ys[-1]-ys[0]<hs:continue
            if not any(ys[j]-ys[i]>=hs and p[ys[i]:ys[j]+1,k].min()<.06 for i in range(len(ys)) for j in range(i+1,len(ys))):continue
            samples.extend(to_page(np.c_[np.full(len(ys),min(g.shape[1]-1,(k+.5)*width)),ys],tr))
        records.append(dict(line=i,candidate=bool(samples),peaks=samples))
    return dict(height=h,records=records,candidates=[r['line'] for r in records if r['candidate']],sampling=sampling,seconds=perf_counter()-start)


def analyze(gray,items,*,detail=False,complete_children=True,forbidden_regions=(),refresh=None,smooth_children=False,retain_support=False):
    start=perf_counter();s=scout(gray,items);out=[];changes=[];records=[]
    wanted=set(s['candidates']);native_s=0.
    for i,q in enumerate(items):
        if i not in wanted:out.append(q);continue
        h=s['height'];witness=s['records'][i];windows=[]
        for x in sorted({p[0] for p in witness['peaks']}):
            if windows and x-3*h<=windows[-1][1]:windows[-1][1]=x+3*h
            else:windows.append([x-3*h,x+3*h])
        positive=False;checks=[];rec=None;context=dict(retain_support=retain_support) if complete_children else None
        a,b,c,d=bbox(q)
        for lo,hi in windows:
            if lo<=a and hi>=c:
                rec=native(gray,q,h,route='slow',prepared=context);native_s+=rec['seconds'];positive=True;break
            clipped=Polygon(np.asarray(q['polygon'],float)).intersection(box(lo,b-1,hi,d+1))
            if clipped.geom_type!='Polygon' or clipped.is_empty:continue
            query=dict(q,polygon=list(clipped.exterior.coords)[:-1])
            check=native(gray,query,h,measure_only=True);native_s+=check['seconds'];checks.append(dict(window=[lo,hi],pairs=len(check['valleys']),seconds=check['seconds']))
            if check['valleys']:positive=True;break
        if not positive:
            out.append(q);records.append(dict(line=i,reason='no two whole word runs in nominated windows',split=False,tracks=[],bodies=[],valleys=[],windows=checks));continue
        if rec is None:rec=native(gray,q,h,route='slow',prepared=context);native_s+=rec['seconds']
        rec['windows']=checks
        # Known unsupported bodies cannot become eligible through another
        # word-track census. Preserve the original acceptance/fallback, and
        # only request its full unchanged-piece census for possible completion.
        unsupported=(sorted(label for bi,label in enumerate(context['body_labels'])
                            if rec['bodies'][bi]['inside_height_h']>0 and len(context['body_tracks'][bi])!=1)
                     if context else [])
        pieces,reason=confirmed_partition(q,rec,prepared=context if not unsupported else None)
        if pieces and complete_children and unsupported:
            rec['completion']=dict(accepted=False,first_failure='parent component lacks unique native body/mark identity',
                                   unassigned_parent_components=unsupported,qualification_shortcircuit=True)
        if pieces and complete_children and not unsupported:
            completed,receipt=whole_children(gray,q,rec,pieces,context,forbidden_regions=forbidden_regions,smooth_exports=smooth_children)
            if completed and refresh is not None:
                decisions=refresh(i,q,completed,h,out+items[i:])
                receipt['refresh']=decisions
                if not decisions['accepted']:completed=[];receipt['first_failure']='changed footprint source/rule/motif decision unsupported'
            receipt['accepted']=bool(completed);rec['completion']=receipt
            if completed:pieces=completed;reason='certified whole native components after accepted partition'
        if pieces:
            added=[dict(q,polygon=p,baseline=None,row_partition=True,row_parent_index=i,row_parent_polygon=q['polygon'],row_piece=k,provenance='native inter-row valley') for k,p in enumerate(pieces)]
            completion=rec.get('completion',{})
            if completion.get('accepted') and context.get('whole_page_supports'):
                for child,support in zip(added,context['whole_page_supports']):child['_selected_pixel_support']=support
            if completion.get('accepted') and completion.get('smooth_export'):
                for k,child in enumerate(added):
                    child['raster_edges']=completion['raster_edges']
                    child['shared_separators']=[g for g in completion['shared_separators'] if k in g['rows']]
            # Prior centreline belongs to the unsplit source, not each child.
            for v in added:v.pop('centreline',None)
            out.extend(added);changes.append(dict(line=i,old=q['polygon'],new=pieces,reason=reason))
        else:out.append(q)
        records.append(dict(line=i,reason=reason,split=bool(pieces),**rec))
    return dict(items=out,changes=changes,records=records,scout=s,scout_s=s['seconds'],native_s=native_s,seconds=perf_counter()-start)


def render(gray,items,*,route='slow',selected=None):
    start=perf_counter();h=height_proxy(items,gray.shape[::-1]);records=[]
    for i,q in enumerate(items):
        if selected is not None and i not in selected:continue
        if q.get('discounted'):continue
        records.append(dict(line=i,**native(gray,q,h,route=route)))
    return dict(height=h,records=records,route=route,seconds=perf_counter()-start)
