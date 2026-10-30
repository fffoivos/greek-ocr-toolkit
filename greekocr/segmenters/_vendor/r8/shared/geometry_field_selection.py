from time import perf_counter
import cv2,numpy as np
from shapely.geometry import Polygon
from .geometry import roi
from .contracts import bbox
from .geometry_contacts import prepare


def apply(gray,items,proposal,*,forbidden_regions=(),column_evidence=None,prepared=None,label_cache=None):
    """Resolve dominant old-row ownership, then verify the complete final ink union.

    Edge grazes do not connect every row of a curled book into one giant group.
    Near-equal owners remain a many-to-many group. A fixed-point retention audit
    reinstates any group whose ink would otherwise disappear.
    """
    start=perf_counter();h=proposal['evidence']['height'];candidates=proposal['items']
    if not candidates:return dict(items=items,changed_indices=[],replacements=[],decisions=[],unowned_candidates=[],seconds=perf_counter()-start)
    cache={} if label_cache is None else label_cache
    if cache and (cache['_image'] is not gray or cache['_height']!=h):raise ValueError('field label cache belongs to another image/height')
    src=cache.get('_source',prepared)
    if src is None:src=prepare(gray,h,with_labels=True,with_density=False)
    lab=src['labels']
    if lab.shape!=gray.shape or src['height']!=h:raise ValueError('field selection native context mismatch')
    if not cache:
        area=np.bincount(lab.ravel());valid=np.zeros(len(area),bool)
        for b in src['components']:valid[b['id']]=True
        cache.update(_image=gray,_height=h,_source=src,_area=area,_valid=valid,_polygons={})
    area=cache['_area'];valid=cache['_valid'];n=len(area)
    # Sustained components cannot establish row identity: rules/scan edges can
    # touch dozens of rows. Their pixels still participate in final retention.
    # The caller owns this cache for one image/proposal only. Exclusion and
    # fixed-point retention decisions are always recomputed on current items.
    polygons=cache['_polygons']
    def labels(q):
        key=id(q['polygon'])
        if key in polygons:return polygons[key][1]
        a,b,c,d=roi(bbox(q),gray.shape);mask=np.zeros((d-b,c-a),np.uint8);cv2.fillPoly(mask,[np.rint(np.asarray(q['polygon'])-[a,b]).astype(int)],1)
        counts=np.bincount(lab[b:d,a:c][mask>0],minlength=n)
        ids=np.flatnonzero((counts>0)&valid)
        result={int(i):int(counts[i]) for i in ids};polygons[key]=(q['polygon'],result)
        return result
    new_labels=[labels(q) for q in candidates];old_labels=[labels(q) for q in items];owners={}
    for j,ls in enumerate(new_labels):
        for i,k in ls.items():
            if i not in owners or k>new_labels[owners[i]][i]:owners[i]=j
    links={};weights=[]
    for i,ls in enumerate(old_labels):
        scores={}
        for k,count in ls.items():
            if k not in owners:continue
            j=owners[k];scores[j]=scores.get(j,0)+min(count,new_labels[j][k])
        if scores:
            maximum=max(scores.values());links[i]={j for j,v in scores.items() if v>=.8*maximum};weights.append(dict(old=i,votes=scores))
    groups=[];seen=set()
    for i,js in links.items():
        if i in seen:continue
        old={i};new=set(js)
        while True:
            more={k for k,v in links.items() if v&new};ns=set().union(*(links[k] for k in more))
            if more==old and ns==new:break
            old,new=more,ns
        groups.append((sorted(old),sorted(new)));seen|=old
    # Native masks are prepared once. Retention is recomputed to a fixed point
    # after vetoes: one rejected proposal can never certify another's loss.
    def raster(qs):
        mask=np.zeros(gray.shape,np.uint8)
        for q in qs:cv2.fillPoly(mask,[np.rint(q['polygon']).astype(int)],1)
        return mask
    forbidden=[Polygon(np.asarray(q['polygon'],float)) for q in forbidden_regions];decisions=[]
    forbidden_bounds=[f.bounds for f in forbidden]
    candidate_shapes=[Polygon(np.asarray(q['polygon'],float)) for q in candidates]
    def touches_forbidden(j):
        p=candidate_shapes[j];a,b,c,d=p.bounds
        return any(a<z and c>x and b<w and d>y and p.intersection(f).area>1e-6 for f,(x,y,z,w) in zip(forbidden,forbidden_bounds))
    old_boxes=[bbox(q) for q in items]
    for oldids,newids in groups:
        oldqs=[items[i] for i in oldids];qs=[candidates[j] for j in newids];reason=None
        if all(q.get('page_field') for q in oldqs):reason='already owned by the page field'
        if any(q.get('initial_completed') for q in oldqs):reason='completed initial protected'
        if not any(old_boxes[i][2]-old_boxes[i][0]>8*h for i in oldids):reason='independent small cells retained'
        if any(not q.get('field_ready',True) for q in qs):reason='candidate contains another native row'
        intervals=[(old_boxes[i][0],old_boxes[i][2]) for i in oldids]
        # Curvature does not authorize joining horizontally independent old
        # owners. Narrow gutters and slightly overlapping detector envelopes
        # need the same protection as wide gutters. Their native labels have
        # already linked them to this candidate group; preserve their boundary.
        if len(newids)<len(oldids) and any(
            not a<=(c+d)/2<=b and not c<=(a+b)/2<=d
            for n,(a,b) in enumerate(intervals) for c,d in intervals[n+1:]
        ):reason='separate horizontal sources retained'
        if any(touches_forbidden(j) for j in newids):reason='permanent exclusion'
        decisions.append(dict(old_indices=oldids,new_indices=newids,accepted=reason is None,reason=reason or 'shared field and native retention',lost_pixels=0,lost_components=[]))
    rulemask=np.zeros(gray.shape,np.uint8)
    for rule in (column_evidence or {}).get('rules',[]):
        if rule.get('accepted'):cv2.polylines(rulemask,[np.rint(rule['rule']['path']).astype(int)],False,1,max(1,round(.4*h)))
    while True:
        removed={i for r in decisions if r['accepted'] for i in r['old_indices']};added={j for r in decisions if r['accepted'] for j in r['new_indices']}
        all_kept=[q for i,q in enumerate(items) if i not in removed]+[candidates[j] for j in sorted(added)]
        union=cv2.dilate(raster(all_kept),np.ones((3,3),np.uint8));new_rejections=0
        for r in decisions:
            if not r['accepted']:continue
            oldqs=[items[i] for i in r['old_indices']];points=np.concatenate([q['polygon'] for q in oldqs]);a,b,c,d=roi([*points.min(0),*points.max(0)],gray.shape)
            m=np.zeros((d-b,c-a),np.uint8)
            for q in oldqs:cv2.fillPoly(m,[np.rint(np.asarray(q['polygon'])-[a,b]).astype(int)],1)
            lost=(m>0)&(union[b:d,a:c]==0)&(lab[b:d,a:c]>0)&(rulemask[b:d,a:c]==0)
            ids,counts=np.unique(lab[b:d,a:c][lost],return_counts=True);substantial=[int(k) for k,v in zip(ids,counts) if area[k]>=max(2,.004*h*h)]
            if substantial:r.update(accepted=False,reason='native ink would be lost',lost_pixels=int(lost.sum()),lost_components=substantial);new_rejections+=1
        if not new_rejections:break
    replacements=[];removed=set()
    for r in decisions:
        if not r['accepted']:continue
        oldqs=[items[i] for i in r['old_indices']];sources=sorted({s for q in oldqs for s in q.get('source_ids',[])})
        parents=[]
        for q in oldqs:
            p=q.get('row_parent_polygon',q['polygon'])
            if p not in parents:parents.append(p)
        replacements.extend(dict(candidates[j],source_ids=sources,field_parent_indices=r['old_indices'],field_parent_polygons=parents) for j in r['new_indices']);removed.update(r['old_indices'])
    used=set().union(*links.values()) if links else set()
    return dict(items=[q for i,q in enumerate(items) if i not in removed]+replacements,changed_indices=sorted(removed),replacements=replacements,decisions=decisions,ownership=weights,unowned_candidates=[j for j in range(len(candidates)) if j not in used],seconds=perf_counter()-start)
