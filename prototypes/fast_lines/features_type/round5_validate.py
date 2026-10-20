"""Fresh public Stack exports and read-only artifact validation for round 5.

No detector/recovery implementation lives here. Each experiment has its own
directory; replay checks deterministic outputs in reverse cohort order.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import cv2
import numpy as np
from .round5 import cohort, DEST, ROOT, PRIOR
from ..stack import Stack
from ..evidence.__main__ import signature
from ..shared.contracts import bbox
from ..shared.review import detector_record, save_image
from ..shared.timing import dump
from ..shared.type_context import overlaps_exclusion


def reading_order(items):
    """Recursive whitespace ordering: columns before rows within each block."""
    if len(items)<2:return list(items)
    bb=np.asarray([bbox(q) for q in items]);h=max(1.,float(np.median(bb[:,3]-bb[:,1])))
    for axis,minimum in [(0,h),(1,.4*h)]:
        ix=np.argsort(bb[:,axis],kind='stable');end=np.maximum.accumulate(bb[ix,axis+2])
        gaps=bb[ix[1:],axis]-end[:-1]
        if len(gaps) and gaps.max()>minimum:
            cut=int(gaps.argmax())+1
            return reading_order([items[i] for i in ix[:cut]])+reading_order([items[i] for i in ix[cut:]])
    return sorted(items,key=lambda q:((bbox(q)[1]+bbox(q)[3])/2,bbox(q)[0]))


def draw(gray,result,path):
    scale=min(1.,1900/gray.shape[1]);g=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR);base=im.copy()
    def poly(canvas,q,color,width=1):
        if q.get('discounted'):return
        cv2.polylines(canvas,[np.rint(np.asarray(q['polygon'])*scale).astype(np.int32)],True,color,width,cv2.LINE_AA)
    old={str(q['polygon']) for q in result['original']}
    final={str(q['polygon']) for q in result['items']}
    for q in result['original']:
        poly(base,q,(210,95,25))
        if str(q['polygon']) not in final:poly(im,q,(155,155,155))
    for q in result.get('removed',[]):poly(im,q,(20,20,225),2)
    for i,q in enumerate(reading_order(result['items']),1):
        if q.get('discounted'):continue
        new=q.get('type_slot') is not None or q.get('type_residual') is not None
        color=(30,155,25) if new else ((210,95,25) if str(q['polygon']) in old else (185,35,155))
        poly(im,q,color,2 if new else 1)
        a,t,_,_=bbox(q);pos=(max(0,round(a*scale)),max(12,round(t*scale)))
        cv2.putText(im,str(i),pos,cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),3,cv2.LINE_AA)
        cv2.putText(im,str(i),pos,cv2.FONT_HERSHEY_SIMPLEX,.35,color,1,cv2.LINE_AA)
    save_image(path,im);save_image(path.with_name(path.stem+'.paddle.jpg'),base)


def crops(gray,result,path):
    """Only R5 additions and completed initials; old R4 additions remain listed."""
    selected=[q for q in result.get('added',[]) if q.get('type_residual') is not None or q.get('initial_completed')]
    tiles=[]
    for i,q in enumerate(selected):
        a,t,b,d=bbox(q);h=(d-t)*.6;a=max(0,int(a-h));t=max(0,int(t-h));b=min(gray.shape[1],int(b+h));d=min(gray.shape[0],int(d+h))
        raw=cv2.cvtColor(gray[t:d,a:b],cv2.COLOR_GRAY2BGR);im=raw.copy()
        for z in result['original']:
            cv2.polylines(im,[np.rint(np.asarray(z['polygon'])-[a,t]).astype(np.int32)],True,(185,185,185),1)
        cv2.polylines(im,[np.rint(np.asarray(q['polygon'])-[a,t]).astype(np.int32)],True,(30,170,30),2)
        tile=np.vstack([raw,im]);scale=min(1.,1100/tile.shape[1]);tile=cv2.resize(tile,None,fx=scale,fy=scale)
        canvas=np.full((tile.shape[0]+28,1100,3),255,np.uint8);canvas[28:,:tile.shape[1]]=tile
        cv2.putText(canvas,f'{path.stem} R5 {i}',(5,19),cv2.FONT_HERSHEY_SIMPLEX,.44,(0,0,0),1);tiles.append(canvas)
    for i in range(0,len(tiles),4):save_image(path.with_name(path.stem+f'.new-{i//4:02d}.jpg'),np.vstack(tiles[i:i+4]))


def run(directory,replay=False):
    directory.mkdir(parents=True,exist_ok=True);key,files=signature();pass_id=2 if replay else 1
    source=directory/f'source-{pass_id}.json'
    if source.exists():raise RuntimeError('Refusing an identical experiment')
    dump(source,dict(key=key,files=files))
    stack=Stack();rows=cohort();rows=list(reversed(rows)) if replay else rows
    warm=cv2.imread(str(ROOT/rows[0]['path']),0);stack.detector.infer(warm)
    for row in rows:
        p=row['page'];result=stack(ROOT/row['path'],parked=row.get('parked',False))
        row=dict(row,image_size=result['image_size']);record=detector_record(row,result['items'],result['timing']['total_s'])
        if replay:assert record['items']==json.loads((directory/(p+'.json')).read_text())['items'],p
        else:
            dump(directory/(p+'.json'),record);dump(directory/(p+'.evidence.json'),{k:v for k,v in result.items() if k!='items'})
            g=cv2.imread(str(ROOT/row['path']),0);draw(g,result,directory/(p+'.jpg'));crops(g,result,directory/(p+'.jpg'))
        typ=result.get('type',{})
        dump(directory/(p+f'.r{pass_id}.json'),dict(page=p,group=row['group'],counts=result['counts'],source=key,
             stages=result['stages'],round5_added_s=typ.get('round5_added_s',0.),**result['timing']))
        print(p,result['counts'].get('added',0),round(typ.get('round5_added_s',0)*1000,3),flush=True)
    assert signature()[0]==key,'Source changed during run'


def validate(directory):
    rows=cohort();checks=0;totals={};links=[];summary={};observations=[]
    for row in rows:
        p=row['page'];r=json.loads((directory/(p+'.json')).read_text());e=json.loads((directory/(p+'.evidence.json')).read_text());w,h=r['image_size']
        assert r['page']==p and r['unit']=='line' and r['seconds']==e['timing']['total_s'];checks+=1
        for q in r['items']:
            a=np.asarray(q['polygon']);assert a.shape[1]==2 and len(a)>=3 and np.isfinite(a).all() and (a>=0).all() and (a<=[w,h]).all();checks+=1
            assert not q.get('discounted') and q.get('baseline') is None;checks+=1
        for q in e.get('added',[]):assert not overlaps_exclusion(q['polygon'],e['removed']);checks+=1
        if row.get('parked'):assert r['items']==e['original'];checks+=1
        for k,v in e['counts'].items():totals[k]=totals.get(k,0)+v
        for ext in ('.jpg','.paddle.jpg'):assert (directory/(p+ext)).stat().st_size>0;checks+=1
        prior=PRIOR/(p+'.json')
        if prior.exists():
            old=json.loads(prior.read_text())['items']
            retained=sum(any(q['polygon']==z['polygon'] for z in r['items']) for q in old)
            observations.append(dict(page=p,old_items=len(old),exactly_retained=retained,
                residual_added=len(e.get('type',{}).get('residual',{}).get('added',[])),
                initials=sum(z['changed'] for z in e.get('type',{}).get('initials',[]))))
        links.append(f'<p><a href="{p}.jpg">{p}</a> · <a href="{p}.paddle.jpg">Paddle</a> · <a href="{p}.json">JSON</a></p>')
    for repeat in (1,2):
        data=[json.loads(f.read_text()) for f in directory.glob(f'*.r{repeat}.json')]
        if not data:continue
        assert len(data)==200;checks+=1
        for group,pred in [('agreement',lambda r:r['group']=='agreement'),('discrepancy',lambda r:r['group'].startswith('discrepancy')),('new_curved',lambda r:r['group']=='new_curved'),('all',lambda r:True)]:
            selected=[r for r in data if pred(r)];fields={}
            for key in ('correction_s','total_s','round5_added_s','type_s'):
                val=np.array([r['stages'].get(key,0.) if key=='type_s' else r[key] for r in selected])*1000
                fields[key]=dict(median=float(np.median(val)),max=float(val.max()),max_page=selected[int(val.argmax())]['page'])
            summary[f'{group}_r{repeat}']=dict(n=len(selected),milliseconds=fields)
    dump(directory/'validation.json',dict(pages=200,checks=checks,totals=totals,observations=observations))
    dump(directory/'summary.json',summary)
    (directory/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Round5 type</title><h1>Round5 type: 200 public Stack exports</h1><p>Blue unchanged; green additions; purple changed over grey original; red removed. Numbers follow recursive whitespace reading order. No discounted items rendered.</p><p><a href="../COMMENTS.md">Owner comments</a> · <a href="summary.json">Measured timing</a> · <a href="validation.json">Validation</a></p>'+''.join(links))
    print(json.dumps(dict(checks=checks,totals=totals,summary=summary),indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['run','replay','validate']);ap.add_argument('--experiment',required=True);args=ap.parse_args();cv2.setNumThreads(1)
    directory=DEST/args.experiment
    validate(directory) if args.action=='validate' else run(directory,replay=args.action=='replay')
