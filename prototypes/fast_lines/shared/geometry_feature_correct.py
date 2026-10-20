"""Conditional map-geometry proposals with local original-ink preservation.

Q8 separators are always enabled. Geometry uses exact contour lineage; empty,
shared, multirow or inadequately supported bands abstain. No new line search,
foreground rejection, semantic baseline or inferred orientation.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.ndimage import minimum_filter1d,maximum_filter1d
from .contracts import bbox
from .geometry import roi,quantize,line_axis
from .geometry_feature_paths import sparse,bands
from .geometry_feature_rules import refine,split_items
from ..layout_barriers.fast import scout,correct


def retention_ink(gray,item,height):
    """Owned source-ROI ink for one audit/repair sequence; image stays immutable.

    Polygons and neighbour ownership are deliberately absent from this value.
    Those are rasterized afresh for each candidate and current item census.
    """
    bounds=tuple(roi(bbox(item),gray.shape));x0,y0,x1,y1=bounds
    a,b,c,d=roi([x0-height,y0-height,x1+height,y1+height],gray.shape)
    raw=gray[b:d,a:c]
    paper=cv2.boxFilter(raw,cv2.CV_32F,(quantize(3*height)|1,)*2)
    ink=(paper-raw>255*.06)[y0-b:y1-b,x0-a:x1-a].copy()
    ink.flags.writeable=False
    return gray,bounds,height,ink


def retention(gray,items,index,polygon,height,detail=False,*,prepared=None):
    """Account for every thresholded pixel uniquely covered by the old box.

    Neighbour-owned ink may leave a straddling box; unique ink may not be silently
    lost. This is a preservation guard, not a proof that new geometry is correct.
    """
    b=bbox(items[index]);x0,y0,x1,y1=roi(b,gray.shape);shape=(y1-y0,x1-x0)
    old=np.zeros(shape,np.uint8);new=np.zeros(shape,np.uint8);others=np.zeros(shape,np.uint8)
    origin=np.array([x0,y0])
    cv2.fillPoly(old,[np.rint(np.asarray(items[index]['polygon'])-origin).astype(np.int32)],1)
    cv2.fillPoly(new,[np.rint(np.asarray(polygon)-origin).astype(np.int32)],1)
    for j,q in enumerate(items):
        if j==index:continue
        a=bbox(q)
        if min(a[2],x1)>max(a[0],x0) and min(a[3],y1)>max(a[1],y0):
            cv2.fillPoly(others,[np.rint(np.asarray(q['polygon'])-origin).astype(np.int32)],1)
    if (prepared is None or prepared[0] is not gray or prepared[1]!=(x0,y0,x1,y1)
            or prepared[2]!=height):
        prepared=retention_ink(gray,items[index],height)
    ink=prepared[3]
    unique=ink&(old>0)&(others==0);lost=unique&(new==0)
    audit=dict(unique_ink=int(unique.sum()),lost_ink=int(lost.sum()),
               lost_fraction=float(lost.sum()/max(1,unique.sum())))
    return (audit,unique,new,origin) if detail else audit


def keep_nearby_ink(gray,items,index,polygon,h,*,prepared=None):
    """Enlarge a contour only enough to retain nearby originally owned marks.

    Refuse whole-row losses: a missing region farther than half a body-height
    from the proposed ribbon is topology uncertainty, not envelope padding.
    """
    audit,unique,new,origin=retention(gray,items,index,polygon,h,True,prepared=prepared)
    lost=unique&(new==0)
    if not lost.any():return polygon,audit
    distance=cv2.distanceTransform(1-new,cv2.DIST_L2,5)
    if float(distance[lost].max())>.5*h:return None,audit
    # Include native polygon outside the old crop as well as lost pixels.
    points=np.asarray(polygon);ys,xs=np.where(lost);lost_points=np.c_[xs,ys]+origin
    x0=int(min(points[:,0].min(),lost_points[:,0].min()));x1=int(np.ceil(max(points[:,0].max(),lost_points[:,0].max())))+1
    y0=int(min(points[:,1].min(),lost_points[:,1].min()));y1=int(np.ceil(max(points[:,1].max(),lost_points[:,1].max())))+1
    support=np.zeros((y1-y0,x1-x0),np.uint8)
    cv2.fillPoly(support,[np.rint(points-[x0,y0]).astype(np.int32)],1)
    support[lost_points[:,1]-y0,lost_points[:,0]-x0]=1
    yy=np.arange(y0,y1)[:,None];xx=np.arange(x0,x1)
    top=np.min(np.where(support>0,yy,np.inf),axis=0);bot=np.max(np.where(support>0,yy,-np.inf),axis=0)
    valid=np.isfinite(top);top=np.interp(xx,xx[valid],top[valid]);bot=np.interp(xx,xx[valid],bot[valid])
    window=quantize(.5*h)|1;top=minimum_filter1d(top,window)-.05*h;bot=maximum_filter1d(bot,window)+.05*h
    ids=np.unique(np.r_[np.arange(0,len(xx),quantize(.15*h)),len(xx)-1])
    p=np.vstack([np.c_[xx[ids],top[ids]],np.c_[xx[ids[::-1]],bot[ids[::-1]]]])
    p=np.clip(p,[0,0],[gray.shape[1],gray.shape[0]]).tolist()
    second=retention(gray,items,index,p,h,prepared=prepared)
    return (p if second['lost_ink']==0 else None),dict(before=audit,after=second)


def run(gray,pm,items,version=6):
    t=perf_counter();H,W=gray.shape
    rule_witness,primitive=scout(gray,items)
    s=sparse(pm,items,(W,H),3)
    scout_s=perf_counter()-t;start=perf_counter()
    out=[dict(q,source_ids=q.get('source_ids',[i])) for i,q in enumerate(items)] if version>=4 else list(items)
    decisions=[];geometry=[];explicit=None
    rule_lines={i for c in rule_witness['candidates'] for i in c['lines']}
    if s['trigger']:
        explicit=bands(pm,items,(W,H),4 if version>=4 else 3);h=s['height'];sparse_rows={v['line']:v for v in s['lines']}
        for a in explicit['lines']:
            i=a['line'];reason=None;b=sparse_rows.get(i)
            if i not in s['nominated'] and a.get('bend_h',0)<.4:continue
            if i in rule_lines:reason='separator corridor takes priority'
            elif not a.get('polygon'):reason='no native polygon'
            elif a.get('source_boxes')!=1:reason='shared band topology'
            elif a.get('multi_run_fraction',1)>.08:reason='multiple map ridges'
            elif len(a['path'])<8:reason='short band'
            elif a['bend_h']<.25 and abs(np.tan(np.radians(a['angle_deg']))-line_axis(items[i])[1])*(bbox(items[i])[2]-bbox(items[i])[0])/h<.5:reason='dense geometry does not corroborate'
            if reason:
                decisions.append(dict(line=i,decision='preserve',reason=reason));continue
            p=a['polygon'];prepared=retention_ink(gray,out[i],h)
            audit=retention(gray,out,i,p,h,prepared=prepared)
            if version>=3 and audit['lost_ink']>0:
                repaired,repair_audit=keep_nearby_ink(gray,out,i,p,h,prepared=prepared)
                if repaired is not None:p=repaired;audit=retention(gray,out,i,p,h,prepared=prepared)
                else:
                    decisions.append(dict(line=i,decision='preserve',reason='loss is not nearby envelope ink',retention=audit,repair=repair_audit));continue
            # V1 is an intentionally unguarded proposal for visual falsification.
            if version>=2 and audit['lost_ink']>0:
                decisions.append(dict(line=i,decision='preserve',reason='unique original ink would be removed',retention=audit));continue
            out[i]=dict(items[i],polygon=p,baseline=None,centreline=a['path'],source_ids=[i],provenance='exact DB contour geometry')
            geometry.append(dict(line=i,old=items[i]['polygon'],new=[p],kind='geometry'))
            decisions.append(dict(line=i,decision='native geometry',retention=audit))
    geometry_s=perf_counter()-start
    t2=perf_counter()
    base=correct(gray,out,rule_witness,primitive) if rule_witness['candidates'] else dict(items=out,changes=[],rules=[],decisions=[],protected_rules=[])
    # The curved refinement is compared independently before being enabled in v3.
    extra=None
    if version>=3 and rule_witness['candidates']:
        extra=refine(gray,items,rule_witness,primitive,apply=version<4,ownership=version>=5,wide_paper=version>=6)
        if extra['rules']:
            split=split_items(gray,base['items'],extra['rules'],s['height']);base['items']=split['items']
            extra['applied']=split['changes'];extra['applied_decisions']=split['decisions']
    separator_s=perf_counter()-t2
    return dict(items=base['items'],geometry_changes=geometry,separator_changes=base['changes'],
                geometry_decisions=decisions,witness=s,rule_witness=rule_witness,rules=base['rules'],
                rule_decisions=base['decisions'],curved=extra,scout_s=scout_s,geometry_s=geometry_s,
                separator_s=separator_s,added_s=perf_counter()-t)
