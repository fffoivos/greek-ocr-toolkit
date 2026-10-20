"""Narrow edits of existing crops along one column bend; no page re-ownership.

Core operations take arrays, polygons and the typed ink reference. The final
run() is the legacy item/evidence adapter. A column transaction preserves all
previously held dark pixels or returns every input polygon unchanged.
"""
from time import perf_counter
import cv2
import numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import split,unary_union
from .geometry_bend import bodies,place,phase,offset
from .geometry_bend_gap import smooth_corridor
from .geometry_bend_rules import finite_rules
from .ink_normal import calibrate,follow_letters
from .ink_faintness import components
from .contracts import bbox
from .type_tables import box_grid


def mask(polygons,shape,origin=(0,0)):
    out=np.zeros(shape,np.uint8)
    for p in polygons:cv2.fillPoly(out,[np.rint(np.asarray(p)-origin).astype(np.int32)],1)
    return out


def loss_pixels(gray,before,after,excluded=()):
    """Exact native <200 found-ink invariant; no new exclusion excuses loss."""
    if not before:return 0
    bb=np.concatenate(before);a,b=np.maximum(0,np.floor(bb.min(0))).astype(int);c,d=np.minimum(gray.shape[::-1],np.ceil(bb.max(0))+1).astype(int)
    shape=(d-b,c-a);old=mask(before,shape,(a,b));new=mask(after,shape,(a,b));ex=mask(excluded,shape,(a,b))
    return int(np.count_nonzero((gray[b:d,a:c]<200)&(old>0)&(new==0)&(ex==0)))


def white_cut(gray,field,y0,y1,left,right):
    """Read only the inter-row corridor; project a smooth shared white cut."""
    h=field.height;xs=np.arange(max(0,int(left)-1),min(gray.shape[1]-1,int(right)+2));ym=(y0+y1)/2
    nominal=ym+offset(field,xs,np.full(len(xs),ym));off=np.arange(-max(1,round(h/2)),max(1,round(h/2))+1)
    raw=cv2.remap(gray,np.broadcast_to(xs,(len(off),len(xs))).astype(np.float32),(nominal[None,:]+off[:,None]).astype(np.float32),cv2.INTER_NEAREST,borderValue=255)
    white=(raw>=200);centre=len(off)//2;lo=np.zeros(len(xs));hi=np.zeros(len(xs))
    for j in range(len(xs)):
        candidates=np.flatnonzero(white[:,j])
        if not len(candidates):return None
        k=candidates[np.argmin(abs(candidates-centre))];l=k;r=k
        while l and white[l-1,j]:l-=1
        while r+1<len(off) and white[r+1,j]:r+=1
        lo[j]=nominal[j]+off[l];hi[j]=nominal[j]+off[r]
    gap,bad=smooth_corridor(nominal,lo,hi,h)
    if bad.any():return None
    return np.c_[xs,gap]


def _parts(poly):
    if poly.is_empty:return []
    # The detector format cannot express holes. Do not fill a protected hole
    # or manufacture triangular OCR fragments to encode it. Retention checks
    # reject a replacement whose representable parts cannot hold its parent.
    if poly.geom_type=='Polygon':return [] if poly.interiors else [np.asarray(poly.exterior.coords)[:-1]]
    return [p for g in poly.geoms for p in _parts(g)]


def band(field,y,left,right,half):
    xs=np.linspace(left,right,max(3,int((right-left)/max(1,field.height/3))+1));yy=y+offset(field,xs,np.full(len(xs),y))
    return np.r_[np.c_[xs,yy-half],np.c_[xs[::-1],yy[::-1]+half]]


def endpoint(gray,field,y,polygons,reference,side,gap_limit,excluded=()):
    """Native terminal window, including two retained bodies and candidate ink.

    Every admitted new body passes its own tone test. Existing polygons are
    unioned unchanged; punctuation in them never depends on the body test.
    """
    h=field.height;bb=max(polygons,key=lambda p:np.ptp(p[:,0]));left=bb[:,0].min();right=bb[:,0].max()
    end=left if side<0 else right
    l=max(field.bounds[0],end-4*h);r=min(field.bounds[2],end+4*h)
    if r-l<h:return polygons,0
    window=band(field,y,l,r,.8*h);gs=components(gray,dict(polygon=window.tolist()),h,route='localized')
    gs=[g for g in gs if g['body'] and g['bbox'][3]-g['bbox'][1]>=2*h/3 and not g['clipped']]
    if not gs:return polygons,0
    bounds=np.array([g['bbox'] for g in gs]);cc=(bounds[:,:2]+bounds[:,2:])/2;mat=phase(field,cc[:,0],cc[:,1]);old=unary_union([Polygon(p) for p in polygons])
    found=np.array([any(cv2.pointPolygonTest(np.asarray(p,np.float32),tuple(c),False)>=0 for p in polygons) for c in cc]);normal=np.array([max(g['core'],g['peak'])+g['noise']>=reference.boundary for g in gs])&(reference.support>=12)&(reference.boundary>0)
    grown=follow_letters(bounds,mat,normal,found,h,y,gap_limit=gap_limit)
    valid=[]
    for run in np.unique(grown.runs[grown.runs>=0]):
        ids=np.flatnonzero(grown.runs==run)
        if not found[ids].any():continue
        ids=ids[(~found[ids])&(bounds[ids,0]<end if side<0 else bounds[ids,2]>end)]
        valid.extend(ids.tolist())
    if not valid:return polygons,0
    ids=np.array(valid);extent=bounds[ids,0].min()-h/8 if side<0 else bounds[ids,2].max()+h/8
    # Only curl-side growth; all kept polygons are a strict geometric floor.
    l,r=(max(field.bounds[0],extent),end+h/4) if side<0 else (end-h/4,min(field.bounds[2],extent))
    new=Polygon(band(field,y,l,r,.7*h))
    if excluded:new=new.difference(unary_union([Polygon(p) for p in excluded]))
    return _parts(old.union(new)),len(ids)


def run(gray,items,fields,*,excluded=(),witness=None,primitive=None,columns=None,target=12):
    start=perf_counter();records=[];out=list(items)
    if not any(f.side for f in fields):return dict(items=out,columns=[],fallbacks=0,seconds=perf_counter()-start)
    proxy=witness['height'];bb,cc=bodies(gray,proxy,target);grid,_=box_grid(items,proxy,3)
    rules=finite_rules(gray,proxy,witness,primitive,columns);tables=[r['bbox'] for r in grid]
    for i,r in enumerate(rules):
        for s in rules[:i]:
            lo=max(r['y0'],s['y0']);hi=min(r['y1'],s['y1'])
            x=float(np.median(np.asarray(r['path'])[:,0]));z=float(np.median(np.asarray(s['path'])[:,0]))
            if hi-lo>3*proxy and abs(x-z)>proxy:tables.append([min(x,z)-proxy,lo,max(x,z)+proxy,hi])
    # Scout nominates before paying a single early calibration. This reference
    # is used ONLY here for growth; the deletion path never receives it.
    page_ink,_=calibrate(gray,items,height=proxy)
    for col,f in enumerate(fields):
        if not f.side:continue
        f,bs,ids=place(f,bb,cc);h=f.height
        if not len(f.phases):continue
        centres=(bs[:,:2]+bs[:,2:])/2;bounds=np.array([bbox(q) for q in out]);membership=[];protected=[]
        for i,q in enumerate(out):
            a,b,c,d=bounds[i]
            if not f.bounds[0]<=(a+c)/2<f.bounds[2]:continue
            near=np.flatnonzero((centres[:,0]>=a)&(centres[:,0]<=c)&(centres[:,1]>=b)&(centres[:,1]<=d)&(ids>=0))
            near=np.array([j for j in near if cv2.pointPolygonTest(np.asarray(q['polygon'],np.float32),tuple(centres[j]),False)>=0],int)
            rows,counts=np.unique(ids[near],return_counts=True);rows=rows[counts>=3]
            table=any(a<z and c>x and b<w and d>y for x,y,z,w in tables)
            large=q.get('initial_completed',False) or min(cv2.minAreaRect(np.asarray(q['polygon'],np.float32))[1])>1.6*f.pitch
            if table or large:protected.append(i);continue
            membership.append((i,rows))
        # Measured body-block start protects isolated running heads/page numbers.
        phases=f.phases;delta=np.diff(phases);body_start=0
        for j in range(min(5,len(delta))):
            if delta[j]>1.5*f.pitch:body_start=phases[j+1]
        candidates={};replaced=set();events=[];gap_samples=[]
        for row,y in enumerate(phases):
            rowbb=bs[ids==row]
            if len(rowbb)<3:continue
            ordered=rowbb[np.argsort(rowbb[:,0])];gaps=ordered[1:,0]-ordered[:-1,2];gap_samples.extend((gaps[(gaps>0)&(gaps<2*h)]/h).tolist())
        # Use observed word gaps where possible, bounded by the brief's 2h.
        # The run itself remains letter-by-letter; a 1h floor avoids treating
        # ordinary spaces as a break when the sample has only letter gaps.
        gap_limit=h*min(2.,max(1.,float(np.quantile(gap_samples,.95))*1.5 if gap_samples else 1.))
        for i,rows in membership:
            if not len(rows) or phases[rows[0]]<body_start:continue
            q=out[i];p=np.asarray(q['polygon']);pieces=[(p,None)]
            if len(rows)==2:
                cut=white_cut(gray,f,*phases[rows],p[:,0].min(),p[:,0].max())
                if cut is not None:
                    parts=_parts(split(Polygon(p),LineString(cut)))
                    if len(parts)==2:
                        pieces=[(v,int(rows[np.argmin(abs(phases[rows]-phase(f,np.mean(v[:,0]),np.mean(v[:,1]))))])) for v in parts]
                        events.append(dict(kind='split',parent=i,rows=rows.tolist()))
            elif len(rows)==1:pieces=[(p,int(rows[0]))]
            for v,row in pieces:
                if row is not None:candidates.setdefault(row,[]).append((i,v))
        edits=[];transfer_loss=0
        for row,parts in candidates.items():
            parents=sorted(set(i for i,p in parts));polys=[p for i,p in parts];y=phases[row]
            new,grown=endpoint(gray,f,y,polys,page_ink.normal,f.side,gap_limit,[q['polygon'] for q in excluded])
            # Absorb tilted pieces only if connected by the admitted terminal
            # continuation; never bridge an unobserved blank between crops.
            joined=_parts(unary_union([Polygon(p) for p in new]));changed=grown or len(joined)<len(polys) or any(len(r)==2 for i,r in membership if i in parents)
            if not changed:continue
            transfer_loss+=loss_pixels(gray,polys,joined,[q['polygon'] for q in excluded])
            source=sorted({k for i in parents for k in out[i].get('source_ids',[])})
            for p in joined:edits.append(dict(out[parents[0]],polygon=p.tolist(),source_ids=source,baseline=None,page_field=True,bend_2c=True))
            replaced.update(parents);events.append(dict(kind='row edit',row=row,parents=parents,grown_bodies=grown,pieces=len(joined)))
        # A missing row starts with observed body ink, never an empty pitch slot.
        # Every emitted run has three native normal bodies on this material row.
        for row,y in enumerate(phases):
            if y<body_start or row in candidates:continue
            bsrow=bs[ids==row]
            if len(bsrow)<3:continue
            left=float(bsrow[:,0].min());right=float(bsrow[:,2].max())
            cy=y+float(offset(f,(left+right)/2,y))
            if any(left<z and right>x and cy+h>w0 and cy-h<w1 for x,w0,z,w1 in tables):continue
            window=band(f,y,left-h/4,right+h/4,.8*h)
            if any(Polygon(window).intersects(Polygon(out[i]['polygon'])) for i in protected):continue
            gs=[g for g in components(gray,dict(polygon=window.tolist()),h,route='localized') if g['body'] and not g['clipped'] and g['bbox'][3]-g['bbox'][1]>=2*h/3]
            if len(gs)<3:continue
            bb0=np.array([g['bbox'] for g in gs]);cc0=(bb0[:,:2]+bb0[:,2:])/2;mat=phase(f,cc0[:,0],cc0[:,1])
            found=np.array([any(cv2.pointPolygonTest(np.asarray(q['polygon'],np.float32),tuple(c),False)>=0 for q in out) for c in cc0])
            if found.any():continue
            ref=page_ink.normal;normal=np.array([max(g['core'],g['peak'])+g['noise']>=ref.boundary for g in gs])&(ref.support>=12)&(ref.boundary>0)
            grown=follow_letters(bb0,mat,normal,found,h,y,gap_limit=gap_limit)
            for runid in np.unique(grown.runs[grown.runs>=0]):
                chosen=bb0[grown.runs==runid];l=max(f.bounds[0],chosen[:,0].min()-h/8);r=min(f.bounds[2],chosen[:,2].max()+h/8)
                poly=Polygon(band(f,y,l,r,.7*h))
                if excluded:poly=poly.difference(unary_union([Polygon(np.asarray(q['polygon'],float)) for q in excluded]))
                nearest=min(range(len(out)),key=lambda k:abs((bounds[k,1]+bounds[k,3])/2-cy)) if out else None
                if nearest is None:continue
                for p in _parts(poly):edits.append(dict(out[nearest],polygon=p.tolist(),baseline=None,page_field=True,bend_2c=True,provenance='native normal run on unoccupied bend path'))
                events.append(dict(kind='missed row',row=row,bodies=len(chosen)))
        before=[q for i,q in enumerate(out) if i in replaced];candidate=[q for i,q in enumerate(out) if i not in replaced]+edits
        loss=max(transfer_loss,loss_pixels(gray,[np.asarray(q['polygon']) for q in before],[np.asarray(q['polygon']) for q in candidate],[q['polygon'] for q in excluded]))
        if loss:events.append(dict(kind='column fallback',lost_pixels=loss))
        else:out=candidate
        records.append(dict(column=col,bounds=f.bounds.tolist(),height=h,pitch=f.pitch,side=f.side,phases=f.phases.tolist(),coefficients=f.coefficients.tolist(),protected=protected,gap_limit_h=gap_limit/h,word_gaps_h=gap_samples,events=events,fallback=bool(loss)))
    return dict(items=out,columns=records,fallbacks=sum(r['fallback'] for r in records),seconds=perf_counter()-start)
