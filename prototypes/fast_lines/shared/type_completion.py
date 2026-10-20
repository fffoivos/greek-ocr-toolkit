"""Original-pixel completion reused from stopped 0b052af missed_crop.

Only component ownership and envelope completion; no old recovery decisions.
"""
import cv2
import numpy as np
from .geometry import roi,mask,line_axis

def snap_components(gray, q, height, items=()):
    """Complete intersected strokes without manufacturing baseline semantics."""
    p=np.asarray(q['polygon'],float); lo=p.min(0); hi=p.max(0)
    a,b,c,d=roi([lo[0]-3*height,lo[1]-2*height,hi[0]+height,hi[1]+height],gray.shape)
    g=gray[b:d,a:c]; k=max(1,round(3*height))|1
    paper=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
    ink=((paper.astype(float)-g)>.18*np.maximum(paper,1)).astype(np.uint8)
    n,labels,st,centres=cv2.connectedComponentsWithStats(ink,8)
    covered=np.zeros_like(ink); cv2.fillPoly(covered,[np.rint(p-[a,b]).astype(np.int32)],1)
    overlap=np.bincount(labels.ravel(),weights=covered.ravel(),minlength=n)
    left_columns=covered[:,max(0,int(lo[0]-a)):min(covered.shape[1],int(lo[0]-a+height))]
    local_bottom=float(np.flatnonzero(left_columns.any(1)).max()+b) if left_columns.any() else hi[1]
    shifted=[dict(q,polygon=(np.asarray(q['polygon'])-[a,b]).tolist()) for q in items]
    original=mask(shifted,g.shape,(c-a,d-b)) if items else np.zeros_like(ink)
    old_owned=np.bincount(labels.ravel(),weights=original.ravel(),minlength=n)
    expanded=covered.copy()
    axes=[]
    for item in items:
        op=np.asarray(item['polygon']);low=op.min(0);high=op.max(0)
        if low[0]<c and high[0]>a and low[1]<d and high[1]>b:
            axes.append((low[0],high[0],line_axis(item)))
    for i in range(1,n):
        x,y,w,h,area=st[i]
        # A body must principally belong to this polygon. Small detached marks
        # may intersect its edge, but touching a neighbour's descender is not
        # ownership of that neighbour's whole body.
        intersects=(.1 if h<.45*height else .5)<overlap[i]/area<1 and old_owned[i]/area<.5
        # An underboxed neighbour may expose most of a character. Ink overlap
        # alone must not reassign that whole character to the recovered row.
        cx,cy=centres[i]+[a,b];col=min(covered.shape[1]-1,max(0,round(cx-a)))
        yy=np.flatnonzero(covered[:,col])
        if len(yy):
            distance=abs(cy-(yy[0]+yy[-1])/2-b)
            if any(l<=cx<=r and abs(cy-cf[0]-cf[1]*cx)<distance for l,r,cf in axes):
                intersects=False
        # A detached large initial may belong to the preceding row. Geometry
        # alone cannot assign it; complete only intersected components.
        if intersects and .15*height<h<3.5*height and w<3*height:
            expanded[y:y+h,x:x+w][labels[y:y+h,x:x+w]==i]=1
    if np.any(expanded!=covered):
        # Dense raster envelope keeps every original polygon pixel. Sampling every
        # column prevents the sparse-vertex shrinkage observed in M3.
        xs=np.flatnonzero(expanded.any(0)); ys=np.arange(expanded.shape[0])[:,None]
        top=np.where(expanded[:,xs],ys,expanded.shape[0]).min(0)
        bottom=np.where(expanded[:,xs],ys,-1).max(0)
        p=np.vstack((np.c_[xs+a,top+b],np.c_[xs[::-1]+a,bottom[::-1]+b]))
        p=cv2.approxPolyDP(p.astype(np.float32),.02*height,True).reshape(-1,2).astype(float)
    return dict(q,polygon=p.tolist())


def request_neighbours(data, column_evidence=None):
    """Finite same-line fragments on an already witnessed column side.

    The common vertical interior of every body in a fragment is a contact
    band, not an x-height estimate. Compatible bands may name one neighbour;
    gaps between their observed x intervals remain unsupported.
    """
    from .geometry import robust_fit
    rules=[(i,r['rule']) for i,r in enumerate((column_evidence or {}).get('rules',[])) if r['accepted']]
    rules=[(i,dict(r,path=np.asarray(r['path']))) for i,r in rules]
    bodies=data['bodies'];fragments=[];unknown=[]
    for rid,row in enumerate(data['rows']):
        parts={}
        for cid in row['components']:
            x0,y0,x1,y1=bodies[cid]['bbox'];side=[];cross=False
            for index,rule in rules:
                if y1<rule['y0'] or y0>rule['y1']:side.append((index,0));continue
                if y0<rule['y0'] or y1>rule['y1']:cross=True;break
                p=rule['path'];ys=np.r_[y0,p[(p[:,1]>y0)&(p[:,1]<y1),1],y1]
                xs=np.interp(ys,p[:,1],p[:,0])
                if x1<xs.min():side.append((index,-1))
                elif x0>xs.max():side.append((index,1))
                else:cross=True;break
            if cross:unknown.append(dict(chain=rid,component=cid,reason='whole body crosses finite rule or endpoint'));continue
            parts.setdefault(tuple(side),[]).append(cid)
        for side,ids in parts.items():
            if len(ids)<2:unknown.extend(dict(chain=rid,component=i,reason='single contact has no row axis') for i in ids);continue
            bb=np.asarray([bodies[i]['bbox'] for i in ids]);xx=(bb[:,0]+bb[:,2])/2;cf=robust_fit(xx,bb[:,3])
            interior=[float(np.max(bb[:,1]-cf[0]-cf[1]*xx)),float(np.min(bb[:,3]-cf[0]-cf[1]*xx))]
            fragments.append(dict(chain=rid,components=ids,side=side,contact_axis=cf.tolist(),interior=interior,span=[float(bb[:,0].min()),float(bb[:,2].max())]))
    parent=list(range(len(fragments)));links=[]
    def root(i):
        while parent[i]!=i:i=parent[i]
        return i
    if fragments:
        spans=np.array([r['span'] for r in fragments]);coeff=np.array([r['contact_axis'] for r in fragments]);bands=np.array([r['interior'] for r in fragments])
        for i,a in enumerate(fragments):
            if a['interior'][0]>=a['interior'][1]:continue
            js=np.array([j for j,b in enumerate(fragments[:i]) if a['side']==b['side'] and b['interior'][0]<b['interior'][1]],int)
            if not len(js):continue
            xs=np.sort(np.c_[np.maximum(spans[i,0],spans[js,0]),np.minimum(spans[i,1],spans[js,1])],axis=1)
            ac=coeff[i,0]+coeff[i,1]*xs;bc=coeff[js,0,None]+coeff[js,1,None]*xs
            overlap=np.minimum(bands[i,1]+ac,bands[js,1,None]+bc)-np.maximum(bands[i,0]+ac,bands[js,0,None]+bc)
            for k in np.flatnonzero(np.all(overlap>0,axis=1)):
                j=int(js[k]);parent[root(i)]=root(j);links.append(dict(fragments=[j,i],x=xs[k].tolist(),body_band_overlap=overlap[k].tolist()))
    groups={}
    for i in range(len(fragments)):groups.setdefault(root(i),[]).append(i)
    return list(groups.values()),fragments,dict(links=links,unknown=unknown)


def complete_request(gray,pieces,height,data,request,items=(),column_evidence=None,retain_support=False):
    """Complete one fixed request census, retaining finite contact provenance."""
    from .contracts import bbox,rect
    from .geometry import robust_fit
    from .type_lattice import point_ownership
    from .geometry_field_detector import native_bands
    bounds=np.asarray(request['bbox'],float)+[-2*height,-2*height,2*height,2*height]
    a,b,c,d=roi(bounds,gray.shape);origin=np.array([a,b]);crop=gray[b:d,a:c]
    centres=np.array([z['centre'] for z in data['bodies']]).reshape(-1,2)
    groups,fragments,grouping=request_neighbours(data,column_evidence)
    group_ids=[set(i for f in group for i in fragments[f]['components']) for group in groups]
    rows=[];axes=[];supports=[];sides=[];records=[];used=set()
    def append(q,ids,spans):
        cf=robust_fit(centres[ids,0],centres[ids,1])
        rows.append(dict(q,polygon=(np.asarray(q['polygon'])-origin).tolist()))
        axes.append([cf[0]+cf[1]*a-b,cf[1]])
        # Merge only overlapping observations. Empty x gaps are not certified.
        merged=[]
        for lo,hi in sorted(spans):
            if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
            else:merged.append([lo,hi])
        supports.append([[lo-a,hi-a] for lo,hi in merged])
    order=sorted(range(len(pieces)),key=lambda i:tuple(bbox(pieces[i])))
    for i in order:
        p=pieces[i];candidates=sorted({cid for r in p.get('type_support_chains',[]) for cid in r['components']})
        here=point_ownership(centres[candidates],[p])
        observed={cid for cid,owned in zip(candidates,here) if owned}
        match=[j for j,ids in enumerate(group_ids) if ids&observed]
        ids=sorted(set().union(*(group_ids[j] for j in match))) if match else []
        rec=dict(piece=i,groups=match,filtered_body_indices=ids);records.append(rec)
        if len(ids)<2:rec['status']='unknown: no finite native axis';continue
        # A group is a neighbour only once. It cannot certify two candidates.
        if any(j in used for j in match):rec['status']='unknown: competing candidates share chain';continue
        rec['row']=len(rows);used.update(match)
        sides.append(fragments[groups[match[0]][0]]['side'])
        append(p,ids,[[min(bbox(p)[0],min(data['bodies'][cid]['bbox'][0] for cid in ids)),max(bbox(p)[2],max(data['bodies'][cid]['bbox'][2] for cid in ids))]])
    targets=len(rows)
    neighbours=[]
    for j,ids in enumerate(group_ids):
        if j in used:continue
        ids=sorted(ids);bb=np.asarray([data['bodies'][i]['bbox'] for i in ids])
        q=dict(polygon=rect([bb[:,0].min(),bb[:,1].min(),bb[:,2].max(),bb[:,3].max()]))
        neighbours.append(dict(row=len(rows),group=j,fragments=groups[j],components=ids))
        sides.append(fragments[groups[j][0]]['side'])
        append(q,ids,[fragments[f]['span'] for f in groups[j]])
    if not targets:return list(pieces),dict(status='unknown',records=records,band_calls=0)
    domains=[]
    for side in sides:
        bounds=[]
        for index,sign in side:
            if not sign:continue
            rule=column_evidence['rules'][index]['rule']
            bounds.append(dict(rule_id=index,path=(np.asarray(rule['path'])-origin).tolist(),y0=rule['y0']-b,y1=rule['y1']-b,side=sign))
        domains.append(bounds)
    mapped,audit=native_bands(crop,rows,height,request_mode=True,axes=axes,supports=supports,domains=domains,target_rows=set(range(targets)),retain_support=retain_support)
    out=list(pieces)
    for rec in records:
        if 'row' not in rec:continue
        j=rec['row'];ev=audit[j];gaps=ev.get('gaps',[])
        candidate=dict(pieces[rec['piece']],polygon=(np.asarray(mapped[j]['polygon'])+origin).tolist())
        if mapped[j].get('raster_edges'):
            candidate['raster_edges']=mapped[j]['raster_edges']
            candidate['shared_separators']=[dict(g,path=(np.asarray(g['path'])+origin).tolist(),
                domain_x=(np.asarray(g['domain_x'])+a).tolist(),
                request_origin=origin.tolist()) for g in mapped[j]['shared_separators']]
        if mapped[j].get('_selected_pixel_support'):
            receipt=mapped[j]['_selected_pixel_support']
            candidate['_selected_pixel_support']=dict(receipt,points=receipt['points']+origin,path=np.asarray(receipt.get('path',[]))+origin if len(receipt.get('path',[])) else [],
                image=gray,shape=gray.shape,origin=origin.tolist())
        rec.update(native=ev,candidate_polygon=candidate['polygon'])
        if not ev.get('corridor_complete'):
            rec['status']='unknown: incomplete separator or competing component support'
        else:
            out[rec['piece']]=candidate;rec['status']='completed between native separators'
    return out,dict(origin=origin.tolist(),bounds=[a,b,c,d],height=height,operator='M17 mean 4h, 20.4 DN',band_calls=1,rows=len(rows),targets=targets,pixels=int(crop.size),records=records,fragments=fragments,groups=groups,neighbours=neighbours,grouping=grouping,supports=supports)


def raster_envelope(support, origin, epsilon=0.):
    """Column extrema of assigned native support, with canonical vertex order."""
    a,b=origin;xs=np.flatnonzero(support.any(0))
    if not len(xs):return None
    ys=np.arange(support.shape[0])[:,None]
    top=np.where(support[:,xs],ys,support.shape[0]).min(0)
    bottom=np.where(support[:,xs],ys,-1).max(0)
    p=np.vstack((np.c_[xs+a,top+b],np.c_[xs[::-1]+a,bottom[::-1]+b]))
    return cv2.approxPolyDP(p.astype(np.float32),epsilon,True).reshape(-1,2).astype(float)



def corridor_hulls(rows,audit,ink,labels,stats,h,target_rows,*,smooth_exports=True,axes=None,retain_support=False):
    """A tight envelope of whole components admitted by both finite seams.

    Containment may supersede nearest-body attachment for an unowned mark;
    it does not provide a semantic attachment or a print-source classification.
    """
    out=list(rows);qualified={}
    for j,r in enumerate(audit):
        r['corridor_complete']=False
        if j not in target_rows:continue
        present=r['support_accounting']['present']
        if r.get('domain_unknown') or not present or any(q['pixels']!=q['total_pixels'] for q in present):continue
        gaps=r['gaps'];upper=[g for g in gaps if g['rows'][1]==j and g['accepted']];lower=[g for g in gaps if g['rows'][0]==j and g['accepted']]
        def covers(gs,x0,x1):
            intervals=sorted((g['path'][0][0],g['path'][-1][0]) for g in gs)
            at=x0
            for lo,hi in intervals:
                if hi<at:continue
                if lo>at:return False
                at=max(at,hi+1)
                if at>x1:return True
            return False
        ids=[q['component'] for q in present]
        missing=[k for k in ids if any(not covers(gs,stats[k,0],stats[k,0]+stats[k,2]-1) for gs in (upper,lower))]
        r['components_without_opposed_x_support']=missing
        # All witnessed neighbouring intervals must pass; accepting one of
        # several intervals cannot certify the rest. Components in a gap in
        # the opposite row have no opposing axis there. Keep their unresolved
        # attachment explicit, and require unique whole containment below.
        if not upper or not lower or any(not g['accepted'] for g in gaps):continue
        if any(q['other_rows'] for q in present):continue
        if r.get('foreign_components') or r.get('ambiguous'):continue
        x0=int(stats[ids,0].min());y0=int(stats[ids,1].min());x1=int((stats[ids,0]+stats[ids,2]).max());y1=int((stats[ids,1]+stats[ids,3]).max())
        if smooth_exports:
            qualified[j]=ids
            continue
        # The inherited hull uses a small raster halo for antialiased edges.
        pad=max(1,round(.06*h));a=max(0,x0-pad);b=max(0,y0-pad);c=min(ink.shape[1],x1+pad);d=min(ink.shape[0],y1+pad)
        keep=np.zeros(len(stats),np.uint8);keep[ids]=1;support=keep[labels[b:d,a:c]]
        support=cv2.dilate(support,np.ones((2*pad+1,2*pad+1),np.uint8))
        corridor=np.zeros((d-b,c-a),np.uint8);cv2.fillPoly(corridor,[np.rint(np.asarray(rows[j]['polygon'])-[a,b]).astype(np.int32)],1)
        support&=corridor
        polygon=raster_envelope(support,[a,b])
        final=np.zeros_like(support);cv2.fillPoly(final,[np.rint(polygon-[a,b]).astype(np.int32)],1)
        counts=np.bincount(labels[b:d,a:c][final>0],minlength=len(stats));actual=set(np.flatnonzero(counts))- {0}
        if actual!=set(ids) or any(counts[k]!=stats[k,4] for k in ids) or np.any(final&~corridor):
            r['hull_unknown']='exported hull changes the verified partition';continue
        r['hull_polygon']=polygon.tolist();r['admitted_components']=ids
        r['corridor_complete']=True
        r['unsupported_axis_intervals']='No axis or semantic attachment is inferred across gaps in finite neighbour support.'
        r['membership']='whole component containment between verified native separators; semantic attachment/source unknown'
        out[j]=dict(rows[j],polygon=polygon.tolist())
    if smooth_exports and qualified:
        _smooth_corridors(rows,out,audit,ink,labels,stats,h,qualified,axes)
    # Only the final Stack requests this ephemeral transport. Other native
    # callers retain their serializable export and pay no packet construction.
    if retain_support:
        for j in target_rows:
            if not audit[j].get('corridor_complete'):continue
            ids=audit[j]['admitted_components'];ss=stats[ids]
            a=int(ss[:,0].min());b=int(ss[:,1].min());c=int((ss[:,0]+ss[:,2]).max());d=int((ss[:,1]+ss[:,3]).max())
            keep=np.zeros(len(stats),bool);keep[ids]=True;yy,xx=np.nonzero(keep[labels[b:d,a:c]]);xx+=a;yy+=b
            packet=dict(points=np.c_[xx,yy],namespace='M17 native mean4h absolute20.4DN',height=h)
            if axes is not None:
                xs=np.array([xx.min(),xx.max()]);packet['path']=np.c_[xs,np.asarray(axes[j])[0]+np.asarray(axes[j])[1]*xs]
            out[j]=dict(out[j],_selected_pixel_support=packet)
    return out


def _smooth_corridors(rows,out,audit,ink,labels,stats,h,qualified,axes):
    """Migrate same-request neighbours together; keep unknown external edges."""
    from .geometry_bands import smooth_band,shared_separator,band_polygon,extent,polygon_mask,EDGE_CONVENTION
    from .geometry import line_axis
    from .contracts import bbox
    axes=np.asarray([line_axis(q) for q in rows] if axes is None else axes)
    pairs={}
    for j in qualified:
        for g in audit[j]['gaps']:
            up,down=g['rows']
            if up in qualified and down in qualified and g['accepted']:
                pairs.setdefault((up,down),[]).append(g)
    # A component-backed adjacent chain is the transaction. Preserve unknown
    # outer edges rather than smooth one side of an unqualified external pair.
    unseen=set(qualified)
    while unseen:
        group={unseen.pop()}
        while True:
            nxt={k for pair in pairs if set(pair)&group for k in pair}
            if nxt<=group:break
            group|=nxt;unseen-=nxt
        if len(group)<2:
            for j in group:audit[j]['smooth_unknown']='no qualified same-call final adjacent pair'
            from copy import deepcopy
            fallback=deepcopy(audit)
            legacy=corridor_hulls(rows,fallback,ink,labels,stats,h,set(group),smooth_exports=False)
            for j in group:out[j]=legacy[j];audit[j].update(fallback[j])
            continue
        members={};bands={};failure=None
        all_ids=[k for j in group for k in qualified[j]];pad=int(np.ceil(.15*h))+1
        ga=max(0,int(stats[all_ids,0].min())-pad);gb=max(0,int(stats[all_ids,1].min())-pad)
        gc=min(ink.shape[1],int((stats[all_ids,0]+stats[all_ids,2]).max())+pad)
        gd=min(ink.shape[0],int((stats[all_ids,1]+stats[all_ids,3]).max())+pad)
        local_labels=labels[gb:gd,ga:gc];local_shape=local_labels.shape
        for j in sorted(group):
            keep=np.zeros(len(stats),np.uint8);keep[qualified[j]]=1;support=keep[local_labels];members[j]=support
            xs,_,_=extent(support)
            has_up=any(pair[1]==j for pair in pairs);has_down=any(pair[0]==j for pair in pairs)
            if not has_up or not has_down:
                pad=max(1,round(.06*h));halo=cv2.dilate(support,np.ones((2*pad+1,2*pad+1),np.uint8))
                corridor=polygon_mask(local_shape,rows[j]['polygon'],[ga,gb]);halo&=corridor
                hx,ht,hb=extent(halo)
            else:hx=ht=hb=None
            fixed_top=None if has_up else (hx,ht-.5)
            fixed_bottom=None if has_down else (hx,hb+.5)
            # Preserve the external pair's finite extent as well as its edge.
            path=np.c_[[0,ink.shape[1]-1],axes[j,0]+axes[j,1]*np.array([0,ink.shape[1]-1])]
            band,why=smooth_band(support,[ga,gb],rows[j]['polygon'],h,path=path,fixed_top=fixed_top,fixed_bottom=fixed_bottom)
            if band is None:failure=why;break
            if fixed_top is not None or fixed_bottom is not None:
                take=(band['x']>=hx[0]+ga)&(band['x']<=hx[-1]+ga)
                for k in ['x','top','bottom']:band[k]=band[k][take]
            bands[j]=band
        contracts=[]
        if failure is None:
            for (up,down),gs in sorted(pairs.items()):
                if up not in group:continue
                # Existing finite common corridor, intersected with both finite
                # selected extents. The domain is bound before candidate scoring.
                a=int(max(bands[up]['x'][0],bands[down]['x'][0],min(g['path'][0][0] for g in gs)))
                c=int(min(bands[up]['x'][-1]+1,bands[down]['x'][-1]+1,max(g['path'][-1][0]+1 for g in gs)))
                seam,why=shared_separator(bands[up],bands[down],members[up],members[down],[ga,gb],h,[a,c])
                if seam is None:failure=why;break
                contracts.append(dict(rows=[up,down],domain_x=[a,c],path=seam.tolist(),edge_convention=EDGE_CONVENTION))
        polygons={}
        if failure is None:
            for j in sorted(group):
                p,why=band_polygon(bands[j])
                if p is None:failure=why;break
                m=polygon_mask(local_shape,p,[ga,gb],half_open=True);counts=np.bincount(local_labels[m>0],minlength=len(stats))
                if set(np.flatnonzero(counts))-{0}!=set(qualified[j]) or any(counts[k]!=stats[k,4] for k in qualified[j]):
                    added=[dict(component=int(k),pixels=int(counts[k]),total=int(stats[k,4]),bbox=stats[k,:4].tolist()) for k in np.flatnonzero(counts) if k and k not in qualified[j]]
                    audit[j]['smooth_added_ink']=added
                    failure='smooth export changes whole native membership';break
                polygons[j]=p
        if failure is not None:
            # No partially installed seam: replay the legacy construction only
            # for this unresolved transaction. No detector or owner vote added.
            for j in group:audit[j]['smooth_unknown']=failure
            from copy import deepcopy
            fallback=deepcopy(audit)
            legacy=corridor_hulls(rows,fallback,ink,labels,stats,h,set(group),smooth_exports=False)
            for j in group:out[j]=legacy[j];audit[j].update(fallback[j])
            continue
        for j in group:
            r=audit[j];p=polygons[j]
            r.update(hull_polygon=p.tolist(),admitted_components=qualified[j],corridor_complete=True,
                     smooth_band=True,shared_separators=[g for g in contracts if j in g['rows']],
                     fixed_external_edges=[k for k in ['top','bottom'] if bands[j]['fixed_'+k]],
                     membership='unchanged whole native components; shared same-request separators')
            out[j]=dict(rows[j],polygon=p.tolist(),raster_edges=EDGE_CONVENTION,
                        shared_separators=r['shared_separators'])
