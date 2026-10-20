"""Final, all-segment native-ink duplicate audit and conservative clipping.

A high shared-ink fraction nominates a duplicate; it is not permission to erase
unshared ink. Subtract only the already-owned polygon. Keep every remaining
connected polygon with observed ink, including uncertain fragments. This makes
source-pixel conservation explicit and does not invent a row count.
"""
from time import perf_counter
import cv2
import numpy as np
from shapely.geometry import Polygon
from .geometry import height_proxy,roi
from .contracts import bbox
from .geometry_bands import crop_mask


def spatial(items):
    shapes=[Polygon(np.asarray(q['polygon'],float)) for q in items]
    # Only spatial neighbours pay native photometry. No whole-page filtering.
    boxes=np.array([p.bounds for p in shapes]).reshape(-1,4)
    pairs=[]
    for i,b in enumerate(boxes):
        for j in np.flatnonzero((boxes[:i,0]<b[2])&(boxes[:i,2]>b[0])&(boxes[:i,1]<b[3])&(boxes[:i,3]>b[1])):
            if shapes[i].intersection(shapes[j]).area>0:pairs.append((int(j),i))
    return shapes,boxes,pairs


def _pass(gray,items,ink,strong,spatial_context=None):
    start=perf_counter();h=height_proxy(items,gray.shape[::-1]);changes=[]
    shapes,boxes,pairs=spatial(items) if spatial_context is None else spatial_context
    masks={};strong_masks={};ink_masks={};offsets={};counts={};strong_counts={}
    for i in sorted({i for p in pairs for i in p}):
        a,b,c,d=roi(boxes[i],gray.shape)
        local_ink=ink[b:d,a:c]
        m=crop_mask((d-b,c-a),items[i],[a,b])
        ink_masks[i]=local_ink;masks[i]=(m>0)&local_ink;strong_masks[i]=(m>0)&strong[b:d,a:c];strong_counts[i]=int(strong_masks[i].sum());offsets[i]=(a,b,c,d);counts[i]=int(masks[i].sum())
    def share(i,j,layer):
        a,b,c,d=offsets[i];x,y,z,w=offsets[j];l=max(a,x);t=max(b,y);r=min(c,z);v=min(d,w)
        if l>=r or t>=v:return 0
        return int((layer[i][t-b:v-b,l-a:r-a]&layer[j][t-y:v-y,l-x:r-x]).sum())
    records=[]
    for i,j in pairs:
        n=share(i,j,masks);s=share(i,j,strong_masks)
        if n:records.append(dict(indices=[i,j],shared_ink=n,shares=[n/max(1,counts[i]),n/max(1,counts[j])],strong_shares=[s/max(1,strong_counts[i]),s/max(1,strong_counts[j])]))
    # Review's 80% criterion is a nomination, never a pixel deletion rule.
    nominated=[r for r in records if max(r['shares']+r['strong_shares'])>=.8]
    out=list(items);gone=set();extras=[]
    for r in sorted(nominated,key=lambda r:-max(r['shares']+r['strong_shares'])):
        i,j=r['indices']
        if i in gone or j in gone:continue
        child,owner=sorted((i,j),key=lambda k:(bool(out[k].get('page_field')),counts[k],shapes[k].area,-k))
        if out[child].get('initial_completed') and not out[owner].get('initial_completed'):child,owner=owner,child
        old=shapes[child];remaining=old.difference(shapes[owner])
        parts=list(remaining.geoms) if remaining.geom_type=='MultiPolygon' else ([remaining] if remaining.geom_type=='Polygon' and not remaining.is_empty else [])
        kept=[];a,b,c,d=offsets[child]
        for p in parts:
            m=crop_mask((d-b,c-a),dict(out[child],polygon=list(p.exterior.coords)[:-1]),[a,b])
            # Pixels on the common integer boundary are already owned. If a
            # fragment has only these, it is an empty OCR crop and is retired.
            x,y,z,w=offsets[owner];l=max(a,x);t=max(b,y);r0=min(c,z);v=min(d,w)
            unique=(m>0)&ink_masks[child]
            if l<r0 and t<v:unique[t-b:v-b,l-a:r0-a]&=~masks[owner][t-y:v-y,l-x:r0-x]
            if unique.any():kept.append(p)
        gone.add(child)
        new=[dict(out[child],polygon=list(p.exterior.coords)[:-1],duplicate_clipped=True,duplicate_parent_index=child) for p in kept]
        for q in new:
            q.pop('shared_separators',None)
            # A fragment is not the original whole-member receipt. Existing
            # ownership already transferred that complete support elsewhere.
            q.pop('_selected_pixel_support',None)
        extras.extend(new)
        out[owner]=dict(out[owner],source_ids=sorted(set(out[owner].get('source_ids',[]))|set(out[child].get('source_ids',[]))))
        changes.append(dict(child=child,owner=owner,owner_polygon=list(shapes[owner].exterior.coords)[:-1],old=items[child]['polygon'],new=[q['polygon'] for q in new],retired=not new,
                            reason='subtract only ink polygon already owned by neighbour',shared_ink=r['shared_ink'],shares=r['shares']))
    return dict(items=[q for i,q in enumerate(out) if i not in gone]+extras,changes=changes,decisions=records,
                duplicate_pairs_before=len(nominated),seconds=perf_counter()-start)


def prepare(gray,items):
    """One ephemeral observation under the reconciler's unchanged contract."""
    h=height_proxy(items,gray.shape[::-1])
    paper=cv2.boxFilter(gray,cv2.CV_32F,(max(3,round(4*h)|1),)*2)
    contrast=np.maximum(0,paper-gray)/np.maximum(paper,1)
    quantized=np.rint(255*contrast).astype(np.uint8)
    threshold=cv2.threshold(quantized,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[0]
    return dict(ink=contrast>.08,strong=quantized>threshold,height=h,
                image=gray,shape=gray.shape,scale=1.,threshold=.08,
                paper_kernel=max(3,round(4*h)|1),builds=1)


def reconcile(gray,items,*,prepared_output=None):
    start=perf_counter();out=items;all_changes=[];before=None;receipts=[]
    context=spatial(items)
    if not context[2]:return dict(items=items,changes=[],decisions=[],duplicate_pairs_before=0,duplicate_pairs_after=0,seconds=perf_counter()-start)
    # Inclusive contrast > .08 requires grey < .92 * paper <= .92 * 255.
    # An entirely brighter shared bounding rectangle cannot hold duplicate ink.
    # Bounds include the raster edge; no resized or estimated ink is consulted.
    boxes=context[1];possible=False
    for i,j in context[2]:
        a=boxes[i];b=boxes[j]
        l,t,r,v=roi([max(a[0],b[0])-1,max(a[1],b[1])-1,min(a[2],b[2])+1,min(a[3],b[3])+1],gray.shape)
        if np.any(gray[t:v,l:r]<255*(1-.08)):possible=True;break
    if not possible:return dict(items=items,changes=[],decisions=[],duplicate_pairs_before=0,duplicate_pairs_after=0,seconds=perf_counter()-start)
    prepared=prepare(gray,items)
    if prepared_output is not None:prepared_output.update(prepared)
    ink,strong=prepared['ink'],prepared['strong']
    for iteration in range(len(items)+1):
        r=_pass(gray,out,ink,strong,context if iteration==0 else None)
        if before is None:before=r['duplicate_pairs_before']
        receipts.append(dict(iteration=iteration,pairs=r['duplicate_pairs_before'],decisions=r['decisions']))
        if not r['changes']:break
        all_changes.extend(dict(c,iteration=iteration) for c in r['changes'])
        if [q['polygon'] for q in r['items']]==[q['polygon'] for q in out]:break
        out=r['items']
    return dict(items=out,changes=all_changes,decisions=receipts,duplicate_pairs_before=before,
                duplicate_pairs_after=r['duplicate_pairs_before'],seconds=perf_counter()-start)
