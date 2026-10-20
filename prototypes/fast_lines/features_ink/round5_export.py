"""Immutable, source-bound 200-page combined-stack experiment and owner colours."""
import argparse,hashlib,html,json,platform
from pathlib import Path
import cv2,numpy as np
from ..round2 import ROOT,manifest,get_baseline
from ..stack import Stack
from ..evidence.__main__ import signature
from ..shared.contracts import bbox
from ..shared.geometry import roi
from ..shared.timing import dump
from ..shared.review import detector_record
from .round5_study import DEST,REVIEW

PREVIOUS=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r4b')


def cohort():
    rows=list(manifest()['pages'])
    for p in sorted((REVIEW/'pages').glob('*.png')):
        g=cv2.imread(str(p),0)
        rows.append(dict(page=p.stem,path=str(p),image_size=[g.shape[1],g.shape[0]],group='new_curved',direction=None,parked=False,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    assert len(rows)==200 and len({r['page'] for r in rows})==200
    return rows


def numbered(gray,result,path):
    scale=min(1.,1800/gray.shape[1]);im=cv2.cvtColor(cv2.resize(gray,None,fx=scale,fy=scale),cv2.COLOR_GRAY2BGR)
    def poly(q,color,width=1):
        if q.get('discounted'):return
        cv2.polylines(im,[np.rint(np.asarray(q['polygon'])*scale).astype(np.int32)],True,color,width,cv2.LINE_AA)
    old={json.dumps(q['polygon']) for q in result['original']}
    for q in result['original']:poly(q,(155,155,155))
    for q in result.get('removed',[]):poly(q,(0,0,220),2)
    ordered=sorted((q for q in result['items'] if not q.get('discounted')),key=lambda q:(round(bbox(q)[1]/5)*5,bbox(q)[0]))
    for i,q in enumerate(ordered,1):
        color=(210,75,0) if json.dumps(q['polygon']) in old else (170,0,170) if q.get('source_ids') else (0,150,0)
        poly(q,color,1 if json.dumps(q['polygon']) in old else 2)
        x,y,_,_=bbox(q);pos=(max(1,round(x*scale)),max(13,round(y*scale)))
        cv2.putText(im,str(i),pos,cv2.FONT_HERSHEY_SIMPLEX,.43,(255,255,255),3,cv2.LINE_AA);cv2.putText(im,str(i),pos,cv2.FONT_HERSHEY_SIMPLEX,.43,color,1,cv2.LINE_AA)
    cv2.imwrite(str(path),im,[cv2.IMWRITE_JPEG_QUALITY,92])
    return [q.get('source_ids',[]) for q in ordered]


def changes(gray,row,result,directory):
    p=row['page'];prior=PREVIOUS/(p+'.json')
    if not prior.exists():return dict(page=p,new_page=True,crops=[])
    old=json.loads(prior.read_text())['items'];new=result['items'];key=lambda q:json.dumps(q['polygon'])
    aa={key(q) for q in old};bb={key(q) for q in new};before=[q for q in old if key(q) not in bb];after=[q for q in new if key(q) not in aa]
    rec=dict(page=p,before=before,after=after,crops=[])
    for i,q in enumerate(before+after):
        b=bbox(q);pad=max(16,(b[3]-b[1])/2);x,y,z,w=roi([b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad],gray.shape)
        raw=cv2.cvtColor(gray[y:w,x:z],cv2.COLOR_GRAY2BGR);panels=[raw]
        for items,color in ((old,(210,75,0)),(new,(0,150,0))):
            im=raw.copy()
            for item in items:
                a=bbox(item)
                if not item.get('discounted') and a[0]<z and a[2]>x and a[1]<w and a[3]>y:
                    cv2.polylines(im,[np.rint(np.asarray(item['polygon'])-[x,y]).astype(np.int32)],True,color,1)
            panels.append(im)
        im=np.vstack(panels);s=min(1.,1500/im.shape[1]);im=cv2.resize(im,None,fx=s,fy=s)
        name=f'{p}.change-{i:02d}.jpg';cv2.imwrite(str(directory/name),im);rec['crops'].append(name)
    return rec


def run(version,repeat,offset,limit):
    out=DEST/version;out.mkdir(parents=True,exist_ok=True);rows=cohort()[offset:offset+limit]
    if repeat%2==0:rows=rows[::-1]
    key,hashes=signature();source=out/f'source-r{repeat}.json'
    if not source.exists():dump(source,dict(key=key,files=hashes,platform=platform.platform()))
    else:assert json.loads(source.read_text())['key']==key
    stack=Stack();stack.detector.infer(cv2.imread(str(ROOT/rows[0]['path']),0))
    for row in rows:
        p=row['page'];receipt=out/f'{p}.r{repeat}.json'
        if receipt.exists():raise RuntimeError('Existing experiment receipt '+p)
        r=stack(ROOT/row['path'],parked=row['parked']);gray=cv2.imread(str(ROOT/row['path']),0)
        if row['group']!='new_curved':assert r['original']==get_baseline(row)
        record=detector_record(row,r['items'],r['timing']['total_s']);target=out/(p+'.json')
        if target.exists():assert json.loads(target.read_text())['items']==record['items'],p
        else:
            dump(target,record);order=numbered(gray,r,out/(p+'.jpg'))
            dump(out/(p+'.evidence.json'),dict(r,items=None,reading_order_sources=order));dump(out/(p+'.changes.json'),changes(gray,row,r,out))
        dump(receipt,dict(page=p,group=row['group'],image_sha256=row['sha256'],source=key,counts=r['counts'],stages=r['stages'],**r['timing']))
        print(p,r['counts'],round(r['timing']['correction_s']*1000,2),flush=True)
    assert signature()[0]==key,'Source changed during run'


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('version');ap.add_argument('--repeat',type=int,default=1);ap.add_argument('--offset',type=int,default=0);ap.add_argument('--limit',type=int,default=200);a=ap.parse_args();run(a.version,a.repeat,a.offset,a.limit)
