"""Offline complete-support probe of the actual M54/M55 implementation.

Capture arrays at existing function return, without altering its observation
operator, native ROI, recurrence rule or current polygon census.
"""
import sys,json,hashlib,os
from pathlib import Path
import cv2,numpy as np
from ..shared import ink_frame_field as frame,ink_faintness as faint
from ..shared.geometry import height_proxy
from ..shared.contracts import bbox
from ..shared.timing import dump
BASE=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack/.astra/fast_lines/out/round8/R8-01b-i4')
OUT=Path(os.environ.get('INK_EVIDENCE_OUT','.astra/fast_lines/out/round8/R8-02-i1'))

def capture(fn,*args,**kwargs):
    found=[]
    def profile(f,event,arg):
        if event=='return' and f.f_code is fn.__code__:found.append(dict(f.f_locals))
    old=sys.getprofile();sys.setprofile(profile)
    try:result=fn(*args,**kwargs)
    finally:sys.setprofile(old)
    return result,found[-1]

def frame_support(gray,polygons,h):
    records=[];original=frame.chain
    def traced(*a,**kw):
        units,loc=capture(original,*a,**kw)
        if len(units):
            records.append(dict(bounds=[loc['a'],loc['y'],loc['c'],loc['d']],labels=loc['lab'],stats=loc['st'],units=units,threshold=float((loc['paper']+loc['ink'])/2)))
        return units
    frame.chain=traced
    try:field=frame.render(gray,polygons,h)
    finally:frame.chain=original
    owned=np.zeros(gray.shape,bool);observed=np.zeros(gray.shape,bool);sampled=np.zeros(gray.shape,bool)
    accepted={tuple(x) for x in field.units.tolist()}
    for rec in records:
        a,b,c,d=rec['bounds'];ids=[]
        for j,(x,y,w,t,area) in enumerate(rec['stats'][1:],1):
            if (a+x,b+y,a+x+w,b+y+t) in accepted:ids.append(j)
        if not ids:continue
        owned[b:d,a:c]|=np.isin(rec['labels'],ids);observed[b:d,a:c]|=rec['labels']>0;sampled[b:d,a:c]=True
    return field,owned,observed,sampled,records

def support(gray,q,h):
    comps,l=capture(faint.components,gray,q,h,route='localized')
    return comps,l

def export_native(inputs,pages):
    """Expose all chain-label support, including rejected marks and edge contact.

    Bands here localize a finite corridor; they grant no pixel ownership. The
    rasterized band boundary is a display/overlap observation, not vector truth.
    """
    out=OUT/'frame-native';out.mkdir(parents=True,exist_ok=False);summary=[]
    for row in json.loads(Path(inputs).read_text())['pages']:
        p=row['page']
        if p not in pages:continue
        g=cv2.imread(row['path'],0);e=json.loads((BASE/'runtime'/f'{p}.evidence.json').read_text())
        h=e.get('ink',{}).get('ownership',{}).get('height',height_proxy(e['original'],g.shape[::-1]))
        f,owned,observed,sampled,records=frame_support(g,[q['polygon'] for q in e['original']],h)
        band=np.zeros(g.shape,np.uint8)
        for poly in f.bands:cv2.fillPoly(band,[np.rint(poly).astype(np.int32)],1)
        entries=[];arrays={}
        for j,r in enumerate(records):
            a,b,c,d=r['bounds'];lab=r['labels'];labels=[];bm=band[b:d,a:c]>0
            for k,(x,y,w,t,area) in enumerate(r['stats'][1:],1):
                m=lab[y:y+t,x:x+w]==k;inside=int((m&bm[y:y+t,x:x+w]).sum())
                labels.append(dict(id=k,bbox=[int(a+x),int(b+y),int(a+x+w),int(b+y+t)],pixels=int(area),corridor_pixels=inside,crosses_corridor=bool(0<inside<area),touches_roi=bool(x==0 or y==0 or x+w==lab.shape[1] or y+t==lab.shape[0]),selected_unit=bool(np.all(owned[b+y:b+y+t,a+x:a+x+w][m])),disposition='demonstrated recurrent unit' if np.all(owned[b+y:b+y+t,a+x:a+x+w][m]) else 'unresolved source; raw support retained'))
            entries.append(dict(bounds=r['bounds'],threshold_DN=r['threshold'],labels=labels));arrays[f'labels_{j}']=lab
            raw=cv2.cvtColor(g[b:d,a:c],cv2.COLOR_GRAY2BGR);v=raw.copy();v[(lab>0)&owned[b:d,a:c]]=(255,140,0);v[(lab>0)&~owned[b:d,a:c]]=(0,0,255)
            for poly in f.bands:cv2.polylines(v,[np.rint(poly-[a,b]).astype(np.int32)],True,(0,180,180),1)
            cv2.imwrite(str(out/f'{p}.chain-{j}.jpg'),np.hstack([raw,v]))
        np.savez_compressed(out/f'{p}.npz',**arrays,owned=owned,observed=observed,sampled=sampled,band=band)
        rec=dict(page=p,input=row,height=h,scale=1,units=f.units.tolist(),bands=[v.tolist() for v in f.bands],chains=entries,semantics='Native chain threshold CC8 before unit filtering; conditional support, not complete physical glyph census. All unselected labels and ROI-edge contacts remain unresolved; corridors do not establish source.')
        dump(out/f'{p}.json',rec);summary.append(dict(page=p,chains=len(entries),crossing=sum(z['crosses_corridor'] for x in entries for z in x['labels']),roi_edge=sum(z['touches_roi'] for x in entries for z in x['labels'])))
    dump(out/'summary.json',summary)

def study(inputs,pages):
    OUT.mkdir(parents=True,exist_ok=True);rows=json.loads(Path(inputs).read_text())['pages'];result=[]
    out=OUT/'support-v1';out.mkdir(exist_ok=False)
    for row in rows:
        if row['page'] not in pages:continue
        p=row['page'];g=cv2.imread(row['path'],0);e=json.loads((BASE/'runtime'/f'{p}.evidence.json').read_text());final=json.loads((BASE/'runtime'/f'{p}.json').read_text())['items']
        items=final+[dict(q) for q in e.get('removed',[]) if q['removal']=='recurrent frame'];h=e.get('ink',{}).get('ownership',{}).get('height',height_proxy(e['original'],g.shape[::-1]))
        f,owned,observed,sampled,recs=frame_support(g,[q['polygon'] for q in e['original']],h)
        old=frame.exclude_whole(g,items,f,h);oldset=set(old['removed']);entries=[]
        np.savez_compressed(out/f'{p}.support.npz',frame=owned,observed=observed,sampled=sampled,units=f.units)
        for i,q in enumerate(items):
            x,y,z,w=map(int,bbox(q));x=max(0,x);y=max(0,y);z=min(g.shape[1],z+1);w=min(g.shape[0],w+1)
            if not owned[y:w,x:z].any():continue
            cs,l=support(g,q,h);a,b,c,d=l['a'],l['b'],l['c'],l['d'];m=l['ink']>0;unknown=m&~owned[b:d,a:c]
            pm=l['mask']>0;extra=(observed[b:d,a:c]&pm)&~owned[b:d,a:c]
            n,lab,st,_=cv2.connectedComponentsWithStats(unknown.astype(np.uint8),8)
            rec=dict(line=i,old_drop=i in oldset,proposed_drop=bool(m.any() and not unknown.any() and not extra.any()),body_count=sum(v['body'] for v in cs),observed_pixels=int(m.sum()),unowned_pixels=int(unknown.sum()),unowned_frame_observation=int(extra.sum()),unobserved_domain=int((pm&~sampled[b:d,a:c]).sum()),unowned_components=[dict(bbox=[a+int(xx),b+int(yy),a+int(xx+ww),b+int(yy+hh)],pixels=int(ar)) for xx,yy,ww,hh,ar in st[1:]])
            entries.append(rec)
            if rec['old_drop'] or i<len(final):
                raw=cv2.cvtColor(g[b:d,a:c],cv2.COLOR_GRAY2BGR);over=raw.copy();over[m&owned[b:d,a:c]]=(255,140,0);over[unknown|extra]=(0,0,255)
                cv2.polylines(over,[np.rint(np.asarray(q['polygon'])-[a,b]).astype(np.int32)],True,(0,180,0),1)
                cv2.imwrite(str(out/f'{p}.{i}.jpg'),np.hstack([raw,over]))
        result.append(dict(page=p,height=h,unit_count=len(f.units),old=len(oldset),proposed=sum(v['proposed_drop'] for v in entries),items=entries));print(p,result[-1]['old'],result[-1]['proposed'],flush=True)
    dump(out/'results.json',result)
if __name__=='__main__':
    study(sys.argv[1],sys.argv[2:])
