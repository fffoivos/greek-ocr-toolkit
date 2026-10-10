"""R5 native row contacts and smooth envelopes. Diagnostic until validated.

Component contact is geometric evidence only, never front/back ownership.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d, minimum_filter1d, maximum_filter1d
from .geometry import height_proxy,quantize
from .contracts import bbox
from .geometry_contacts import prepare,trace


def analyze(gray,items,route='slow',version=1):
    start=perf_counter();h=height_proxy(items,(gray.shape[1],gray.shape[0]))
    field=prepare(gray,h,fast_filter=route!='slow')
    records=[]
    for i,q in enumerate(items):
        b=bbox(q)
        if b[2]-b[0]<8*h:continue
        r=trace(field,q,version=7)
        p=np.asarray(r['path']);seen=np.asarray(r['observed']);x,y=p.T
        keep=(x>=b[0])&(x<=b[2]);usable=seen&keep
        if not usable.any():continue
        contacts=r['contacts']
        # Native component extrema are rendered against a body-support path.
        # A support centre is not a semantic baseline or a foreground label.
        top=y-.6*h;bottom=y+.6*h
        for c in contacts:
            a,bb,z,w=c['bbox'];cx,cy=c['centre']
            ix=(x>=a-.2*h)&(x<=z+.2*h)&seen
            top[ix]=np.minimum(top[ix],bb-.1*h);bottom[ix]=np.maximum(bottom[ix],w+.1*h)
        sigma=max(1,1.5*h/(x[1]-x[0]));top=minimum_filter1d(top,quantize(sigma)|1);bottom=maximum_filter1d(bottom,quantize(sigma)|1)
        top=gaussian_filter1d(top,sigma);bottom=gaussian_filter1d(bottom,sigma)
        ids=np.flatnonzero(keep);poly=np.vstack([np.c_[x[ids],top[ids]],np.c_[x[ids[::-1]],bottom[ids[::-1]]]])
        records.append(dict(r,line=i,polygon=poly.tolist(),top=np.c_[x,top].tolist(),bottom=np.c_[x,bottom].tolist()))
    return dict(height=h,lines=records,components=field['components'],seconds=perf_counter()-start,route=route,version=version)


def guided(gray,pm,items,original,route='slow',version=2,selected=None,*,with_labels=False,map_bands=None,envelope_indices=None):
    """Native contacts constrained by map ancestry, with competitors exposed.

    The map supplies identity inside its observed extent, not a glyph envelope.
    Outside it, a tangent is a hypothesis checked against actual components.
    """
    from .geometry_feature_paths import bands
    from .geometry import line_axis
    start=perf_counter();h=height_proxy(original,(gray.shape[1],gray.shape[0]))
    field=prepare(gray,h,12 if route=='heuristic' else None,fast_filter=route!='slow',with_labels=with_labels,with_density=route=='slow')
    bb=bands(pm,original,(gray.shape[1],gray.shape[0]),4) if map_bands is None else map_bands
    lookup={q['line']:q for q in bb['lines'] if q.get('path') and q.get('source_boxes')==1}
    records=[]
    centres=np.array([c['centre'] for c in field['components']]).reshape(-1,2)
    for i,q in enumerate(items):
        if selected is not None and i not in selected:continue
        box=bbox(q)
        if box[2]-box[0]<8*h:continue
        sources=q.get('source_ids',[i] if items is original else []);chunks=[np.array(lookup[k]['path']) for k in sources if k in lookup]
        if not chunks:
            if q.get('centreline') is not None:chunks=[np.array(q['centreline'])]
            elif version>=4:
                from .geometry import roi
                x0,y0,x1,y1=roi(box,gray.shape);mask=np.zeros((y1-y0,x1-x0),np.uint8)
                cv2.fillPoly(mask,[np.rint(np.array(q['polygon'])-[x0,y0]).astype(np.int32)],1)
                count=mask.sum(0);use=count>0;cx=np.arange(x0,x1)[use]
                cy=(mask*np.arange(y0,y1)[:,None]).sum(0)[use]/count[use];chunks=[np.c_[cx,cy]]
            else:continue
        anchor=np.concatenate(chunks);anchor=anchor[np.argsort(anchor[:,0])]
        anchor=anchor[(anchor[:,0]>=box[0])&(anchor[:,0]<=box[2])]
        if len(anchor)<5:continue
        x=np.arange(max(0,box[0]-6*h),min(gray.shape[1],box[2]+6*h),max(1,.25*h));ay=np.interp(x,*anchor.T)
        for right in (False,True):
            xx=anchor[:,0];idx=xx>xx[-1]-6*h if right else xx<xx[0]+6*h
            if idx.sum()<3:continue
            slope=np.clip(np.polyfit(xx[idx]-xx[idx].mean(),anchor[idx,1],1)[0],-.65,.65)
            ex,ey=anchor[-1 if right else 0];ix=x>ex if right else x<ex;ay[ix]=ey+slope*(x[ix]-ex)
        if route=='slow':
            r=trace(field,q,version=7);rx,ry=np.asarray(r['path']).T
            raw=np.interp(x,rx,ry);seen=np.interp(x,rx,np.asarray(r['observed'],float))>.99
        else:
            raw=ay.copy();seen=np.ones(len(x),bool)
        inside=(x>=anchor[0,0])&(x<=anchor[-1,0])
        # A row switch inside the observed map extent is not an endpoint curve.
        compatible=abs(raw-ay)<.65*h
        y=np.where(compatible&seen,raw,ay)
        y=gaussian_filter1d(y,max(1,1.5*h/(x[1]-x[0])))
        if version>=3:
            # All routes keep the independently observed map identity. Native
            # contacts provide extent; an uncorroborated tangent never does.
            y=gaussian_filter1d(ay,max(1,.75*h/(x[1]-x[0])))
        eligible=(centres[:,0]>=x[0])&(centres[:,0]<=x[-1])&(abs(centres[:,1]-np.interp(centres[:,0],x,y))<.65*h)
        contacts=[field['components'][k] for k in np.flatnonzero(eligible)]
        records.append(dict(line=i,path=np.c_[x,y].tolist(),reference=np.c_[x,ay].tolist(),observed=seen.tolist(),contacts=contacts,bbox=box,
            disagreement_h=float(np.max(abs(raw[inside]-ay[inside]))/h) if inside.any() else 0))
    # The same physical glyph cannot independently belong to two row bands.
    owners={};ambiguous=set()
    for r in records:
        x,y=np.array(r['path']).T
        for c in r['contacts']:
            cx,cy=c['centre'];d=abs(cy-np.interp(cx,x,y));owners.setdefault(c['id'],[]).append((d,r['line']))
    assigned={}
    for cid,choices in owners.items():
        choices.sort()
        if len(choices)>1 and choices[1][0]-choices[0][0]<.25*h:
            ambiguous.update(i for _,i in choices)
        assigned[cid]=choices[0][1]
    for r in records:
        x,y=np.array(r['path']).T;box=r['bbox'];r['contacts']=[c for c in r['contacts'] if assigned[c['id']]==r['line']]
        r['ambiguous']=r['line'] in ambiguous
        contacts=r['contacts']
        if version>=3:
            # A separated mark six heights away is not an endpoint continuation.
            connected=[c for c in contacts if c['bbox'][2]>=box[0] and c['bbox'][0]<=box[2]]
            for right_side in (False,True):
                edge=box[2] if right_side else box[0]
                tail=[c for c in contacts if (c['bbox'][0]>box[2] if right_side else c['bbox'][2]<box[0])]
                tail.sort(key=lambda c:c['bbox'][0] if right_side else -c['bbox'][2])
                for c in tail:
                    gap=c['bbox'][0]-edge if right_side else edge-c['bbox'][2]
                    if gap>1.5*h:break
                    connected.append(c);edge=c['bbox'][2] if right_side else c['bbox'][0]
            contacts=connected;r['contacts']=contacts
        inside=[c for c in contacts if box[0]<c['centre'][0]<box[2]]
        r['polygon']=None
        if envelope_indices is not None and r['line'] not in envelope_indices:continue
        if len(inside)<4:continue
        # Only contact-backed ends grow; no padding out to an unobserved tangent.
        left=min(box[0],min(c['bbox'][0] for c in contacts)-.15*h);right=max(box[2],max(c['bbox'][2] for c in contacts)+.15*h)
        ix=(x>=left)&(x<=right)
        if version>=5:
            xx=np.unique(np.r_[left,x[ix],right]);y=np.interp(xx,x,y);x=xx
        else:x=x[ix];y=y[ix]
        top=y-.65*h;bot=y+.65*h
        for c in contacts:
            a,b,z,w=c['bbox'];idx=(x>=a-.2*h)&(x<=z+.2*h)
            top[idx]=np.minimum(top[idx],b-.18*h);bot[idx]=np.maximum(bot[idx],w+.18*h)
        sig=max(1,2*h/(x[1]-x[0]));lo=gaussian_filter1d(top,sig);hi=gaussian_filter1d(bot,sig)
        # Smooth extrema, then apply a constant margin for the worst owned mark.
        # This keeps native contact extents without saw-toothed per-letter sides.
        if version<3:
            lo-=max(0,float(np.max(lo-top)));hi+=max(0,float(np.max(bot-hi)))
        else:
            # Local extremal envelopes: a remote accent must not widen an
            # entire line. The quadratic shoulder has a physical two-height
            # radius, independent of image resolution.
            lo=y-.7*h;hi=y+.7*h
            for c in contacts:
                a,b,z,w=c['bbox'];distance=np.maximum(0,np.maximum(a-x,x-z))
                lo=np.minimum(lo,b-.22*h+distance**2/((32 if version>=4 else 8)*h))
                hi=np.maximum(hi,w+.22*h-distance**2/((32 if version>=4 else 8)*h))
            lo=gaussian_filter1d(lo,1)-.05*h;hi=gaussian_filter1d(hi,1)+.05*h
        r['polygon']=np.vstack([np.c_[x,lo],np.c_[x[::-1],hi[::-1]]]).tolist()
        r['owned']=len(contacts);r['extension_h']=[(box[0]-left)/h,(right-box[2])/h]
    return dict(height=h,lines=records,components=field['components'],seconds=perf_counter()-start,route=route,version=version,
                **({'_labels':field['labels']} if with_labels else {}))


def correct(gray,pm,items,original,*,scout=None,forbidden_regions=(),detail=False,map_bands=None,column_evidence=None):
    """Smooth contact-backed bands, conditional on the shared geometry scout.

    This never treats a deleted line as an ink owner. Initial-letter completions
    retain their explicit shoulder. Missing ancestry is not a positional index.
    """
    from collections import Counter
    from .geometry_scout import sparse_fast
    from .geometry_feature_correct import retention
    from .geometry import line_axis
    t=perf_counter();size=(gray.shape[1],gray.shape[0]);s=scout or sparse_fast(pm,original,size,3)
    new_rows=any(q.get('type_slot') is not None for q in items)
    if not s['trigger'] and not new_rows:return dict(items=items,changes=[],decisions=[],seconds=perf_counter()-t,trigger=False)
    counts=Counter(k for q in items for k in q.get('source_ids',[]))
    eligible=set();h=height_proxy(original,size)
    rules=[r['rule'] for r in (column_evidence or {}).get('rules',[]) if r['accepted']]
    for i,q in enumerate(items):
        b=bbox(q);cy=(b[1]+b[3])/2
        if b[2]-b[0]<8*h or q.get('initial_completed') or any(counts[k]>1 for k in q.get('source_ids',[])):continue
        blocked=False
        for r in rules:
            path=np.asarray(r['path']);cx=np.interp(cy,path[:,1],path[:,0])
            if r['y0']<=cy<=r['y1'] and b[0]-h<cx<b[2]+h:blocked=True;break
        if not blocked:eligible.add(i)
    if not eligible:return dict(items=items,changes=[],decisions=[],seconds=perf_counter()-t,trigger=True,eligible=[])
    evidence=guided(gray,pm,items,original,route='explicit',version=5,with_labels=True,map_bands=map_bands,envelope_indices=eligible);labels=evidence.pop('_labels');h=evidence['height'];out=list(items);changes=[];decisions=[]
    for r in evidence['lines']:
        i=r['line'];q=items[i];p=r.get('polygon');reason=None
        if not p or i not in eligible:continue
        x,y=np.array(r['path']).T;b=bbox(q);inbox=(x>=b[0])&(x<=b[2]);a,sl=line_axis(q)
        deviation=float(np.max(abs(y[inbox]-(a+sl*x[inbox])))/h) if inbox.any() else 0
        if deviation<.3 and max(r.get('extension_h',[0]))<.5 and q.get('type_slot') is None:continue
        if q.get('initial_completed'):reason='completed initial shoulder retained'
        elif r['ambiguous']:reason='competing row contacts'
        elif any(counts[k]>1 for k in q.get('source_ids',[])):reason='separated source bounds retained'
        # A smooth band cannot silently remove unique native ink (including
        # small accents excluded from the body-component field).
        audit=None
        if reason is None:
            offrow=offrow_components(r,evidence['components'],h)
            audit=owned_retention(gray,out,i,p,h,offrow,labels=labels)
            if audit['lost_ink']:
                # A small uniform margin preserves shape smoothness. Wider
                # unexplained losses are identity uncertainty, not padding.
                poly=np.array(p);n=len(poly)//2;poly[:n,1]-=.2*h;poly[n:,1]+=.2*h
                widened=owned_retention(gray,out,i,poly.tolist(),h,offrow,labels=labels)
                if widened['lost_ink']:
                    padded=pad_unique(gray,out,i,p,h,offrow,labels=labels)
                    if padded is None:reason='unassigned original ink outside smooth band'
                    else:p=padded;audit=owned_retention(gray,out,i,p,h,offrow,labels=labels)
                else:p=poly.tolist();audit=widened
        if reason is None:
            pb=np.asarray(p);pb=np.clip(pb,[0,0],[gray.shape[1]-1,gray.shape[0]-1]);p=pb.tolist()
            for f in forbidden_regions:
                fb=bbox(f)
                if min(pb[:,0].max(),fb[2])>max(pb[:,0].min(),fb[0]) and min(pb[:,1].max(),fb[3])>max(pb[:,1].min(),fb[1]):
                    reason='removed region footprint';break
        if reason is None:
            # Never reclaim ink assigned to a neighboring current polygon.
            # Check ONLY newly covered region, so pre-existing overlap is not
            # mistaken for a regression introduced by this operation.
            from .geometry import roi
            xx0,yy0,xx1,yy1=roi([min(b[0],pb[:,0].min()),min(b[1],pb[:,1].min()),max(b[2],pb[:,0].max()),max(b[3],pb[:,1].max())],gray.shape)
            shape=(yy1-yy0,xx1-xx0);old=np.zeros(shape,np.uint8);new=old.copy();other=old.copy();origin=[xx0,yy0]
            cv2.fillPoly(old,[np.rint(np.array(q['polygon'])-origin).astype(np.int32)],1);cv2.fillPoly(new,[np.rint(pb-origin).astype(np.int32)],1)
            for j,z in enumerate(out):
                zb=bbox(z)
                if j!=i and min(zb[2],xx1)>max(zb[0],xx0) and min(zb[3],yy1)>max(zb[1],yy0):cv2.fillPoly(other,[np.rint(np.array(z['polygon'])-origin).astype(np.int32)],1)
            raw=gray[yy0:yy1,xx0:xx1];paper=cv2.boxFilter(raw,cv2.CV_32F,(quantize(3*h)|1,quantize(3*h)|1));ink=paper-raw>255*.06
            mine=np.zeros(shape,np.uint8)
            for c in r['contacts']:
                a,bb,z,w=c['bbox'];a=max(0,int(a-xx0-.2*h));bb=max(0,int(bb-yy0-.35*h));z=min(shape[1],int(np.ceil(z-xx0+.2*h)));w=min(shape[0],int(np.ceil(w-yy0+.2*h)))
                mine[bb:w,a:z]=1
            if np.any((new>0)&(old==0)&(other>0)&(mine==0)&ink):reason='new overlap with retained neighbor ink'
        if reason is None:
            from .geometry_joinbarriers import inspect as rule_barriers
            if rule_barriers(gray,p,h):reason='regional boundary remains unresolved'
        decision=dict(line=i,accepted=reason is None,reason=reason or 'smooth native contacts with unique ink retained',retention=audit,deviation_h=deviation)
        decisions.append(decision)
        if reason is None:
            out[i]=dict(q,polygon=p,baseline=None,provenance='smooth native contact envelope')
            changes.append(dict(line=i,old=q['polygon'],new=[p]))
    return dict(items=out,changes=changes,decisions=decisions,seconds=perf_counter()-t,trigger=True,
                **({'rendering':evidence} if detail else {}))


def pad_unique(gray,items,index,polygon,h,offrow=(),*,labels=None):
    """Smooth local padding for unexplained marks within half a body height."""
    from .geometry_feature_correct import retention
    audit,unique,new,origin=owned_retention(gray,items,index,polygon,h,offrow,True,labels=labels);lost=unique&(new==0)
    if not lost.any():return polygon
    dist=cv2.distanceTransform(1-new,cv2.DIST_L2,5)
    if float(dist[lost].max())>.5*h:return None
    n,lab,stats,_=cv2.connectedComponentsWithStats(lost.astype(np.uint8),8)
    poly=np.array(polygon);half=len(poly)//2;xx=poly[:half,0];lo=poly[:half,1];hi=poly[half:,1][::-1]
    a=min(xx[0],min(stats[1:,0])+origin[0]-.1*h);b=max(xx[-1],max(stats[1:,0]+stats[1:,2])+origin[0]+.1*h)
    x=np.unique(np.r_[a,xx,b]);low=np.interp(x,xx,lo);high=np.interp(x,xx,hi)
    for cx,cy,w,hh,area in stats[1:]:
        left=cx+origin[0];right=left+w;top=cy+origin[1];bottom=top+hh;dx=np.maximum(0,np.maximum(left-x,x-right))
        low=np.minimum(low,top-.12*h+dx*dx/(32*h));high=np.maximum(high,bottom+.12*h-dx*dx/(32*h))
    result=np.vstack([np.c_[x,low],np.c_[x[::-1],high[::-1]]]).tolist()
    return result if owned_retention(gray,items,index,result,h,offrow,labels=labels)['lost_ink']==0 else None


def offrow_components(record,components,h):
    """A rectangle's sliver of another whole glyph is not row ownership.

    Require a body-sized connected component whose centre is outside this row's
    body strip. Small marks/diacritics remain unexplained and are preserved.
    """
    x,y=np.asarray(record['path']).T;b=record['bbox'];out=[]
    for c in components:
        a,top,z,bot=c['bbox'];cx,cy=c['centre']
        if z<b[0] or a>b[2] or bot<b[1] or top>b[3]:continue
        if bot-top>.55*h and abs(cy-np.interp(cx,x,y))>h:out.append(c)
    return out


def owned_retention(gray,items,index,polygon,h,offrow=(),detail=False,*,labels=None):
    from .geometry_feature_correct import retention
    audit,unique,new,origin=retention(gray,items,index,polygon,h,True)
    before=unique.copy();H,W=unique.shape
    if offrow:
        if labels is None:raise ValueError('Native component labels required to exempt off-row ink')
        x0,y0=origin
        local=labels[y0:y0+H,x0:x0+W]
        unique[np.isin(local,[c['id'] for c in offrow])]=False
    lost=unique&(new==0);audit=dict(unique_ink=int(unique.sum()),lost_ink=int(lost.sum()),offrow_ink=int((before&~unique).sum()),offrow_components=[c['id'] for c in offrow])
    return (audit,unique,new,origin) if detail else audit


def endpoint_pairs(items,evidence):
    """Diagnostic: small fragments sharing the same physical contact ownership."""
    from collections import Counter
    h=evidence['height'];count=Counter(k for q in items for k in q.get('source_ids',[]));pairs=[]
    allcomps=evidence['components']
    for r in evidence['lines']:
        i=r['line'];b=bbox(items[i]);owned={c['id'] for c in r['contacts']}
        if r.get('ambiguous') or b[2]-b[0]<16*h:continue
        x,y=np.array(r['path']).T
        for j,q in enumerate(items):
            sources=q.get('source_ids',[])
            if i==j or len(sources)!=1 or count[sources[0]]!=1:continue
            f=bbox(q);width=f[2]-f[0];gap=max(f[0]-b[2],b[0]-f[2]);cx=(f[0]+f[2])/2;cy=(f[1]+f[3])/2
            if not (.5*h<width<8*h and -.5*h<gap<2*h and x[0]<=cx<=x[-1] and abs(cy-np.interp(cx,x,y))<h):continue
            cs=[c for c in allcomps if f[0]<=c['centre'][0]<=f[2] and f[1]<=c['centre'][1]<=f[3]]
            if len(cs)<2 or any(c['id'] not in owned for c in cs):continue
            pairs.append(dict(line=i,fragment=j,components=[c['id'] for c in cs],gap_h=gap/h))
    counts=Counter(q['fragment'] for q in pairs)
    return [q for q in pairs if counts[q['fragment']]==1]
