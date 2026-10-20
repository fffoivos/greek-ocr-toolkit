"""A12: stable intensity components + bounded neighbour graph, independent of map."""
from time import perf_counter
import cv2,numpy as np
from ..shared.geometry import roi,quantize
from ..shared.image_evidence import components,stroke_features
from ..shared.contracts import rect,result,deduplicate

def group(ctx,b,with_width=True):
    e=ctx.ev; x0,y0,x1,y1=roi(np.asarray(b)*[e.sx,e.sy,e.sx,e.sy],e.shape)
    persistence=e.persistence[y0:y1,x0:x1]; binary=(persistence>=2).astype(np.uint8); h=e.body
    labels,stats,centres=components(binary); st=stroke_features(binary) if with_width else None
    selected=[]
    for i,(x,y,w,rh,a) in enumerate(stats):
        if not .25*h<=rh<=2.5*h or w>4*h or a<.04*h*h: continue
        active=labels[y:y+rh,x:x+w]==i+1; stable=float(persistence[y:y+rh,x:x+w][active].mean()/3)
        width=float(np.median(2*st['distance'][y:y+rh,x:x+w][active])/max(h,1e-6)) if with_width else None
        if stable<.65 or (with_width and not .06<width<.85): continue
        selected.append(dict(bbox=[x,y,x+w,y+rh],centre=centres[i],width_h=width,stable=stable,component=i))
    selected.sort(key=lambda q:q['bbox'][0]); parents=list(range(len(selected))); edges=[]
    def root(i):
        while parents[i]!=i: parents[i]=parents[parents[i]]; i=parents[i]
        return i
    barriers=ctx.get('layout_barriers').get('barriers',[])
    for i,a in enumerate(selected):
        for j in range(i+1,len(selected)):
            c=selected[j]; gap=c['bbox'][0]-a['bbox'][2]
            if gap>2*h: break
            if abs(a['centre'][1]-c['centre'][1])>.6*h: continue
            ax=(a['centre'][0]+x0)/e.sx; cx=(c['centre'][0]+x0)/e.sx; cy=(c['centre'][1]+y0)/e.sy
            if any(ax<(q['bbox'][0]+q['bbox'][2])/2<cx and q['bbox'][1]<cy<q['bbox'][3] for q in barriers): continue
            parents[root(j)]=root(i); edges.append([i,j])
    groups={}
    for i,q in enumerate(selected): groups.setdefault(root(i),[]).append(q)
    out=[]
    for qs in groups.values():
        if len(qs)<3: continue
        a=np.asarray([q['bbox'] for q in qs]); box=[(a[:,0].min()+x0)/e.sx,(a[:,1].min()+y0)/e.sy,(a[:,2].max()+x0)/e.sx,(a[:,3].max()+y0)/e.sy]
        if box[2]-box[0]<2*ctx.height: continue
        out.append(dict(polygon=rect(box),baseline=None,score=None,provenance='stable component graph; foreground unknown'))
    return out,dict(components=len(stats),stable_components=len(selected),edges=edges,groups=len(out),bbox=b)

def run(ctx,phase=3):
    req=ctx.get('residual_ledger').get('requests',[]); variants={}; graphs={}; times={}
    for with_width,name in ((False,'persistence'),(True,'persistence_width')):
        t=perf_counter(); candidates=[]; graph=[]
        for r in req:
            lines,record=group(ctx,r['bbox'],with_width); candidates+=lines; graph.append(dict(record,request=r['id']))
        variants[name]=candidates; graphs[name]=graph; times[name]=perf_counter()-t
    t=perf_counter(); full,fullgraph=group(ctx,[0,0,*ctx.size],True); full_s=perf_counter()-t
    retained,conflicts=deduplicate(ctx.items,variants['persistence_width'])
    return result(retained,variants=variants,graphs=graphs,variant_seconds=times,full_page_diagnostic=full,
        full_page_graph=fullgraph,full_page_seconds=full_s,conflicts=conflicts,new_candidates=len(retained)-len(ctx.items),
        regions=[dict(bbox=r['bbox']) for r in req],status='map-independent candidates; ghosts remain unknown')
