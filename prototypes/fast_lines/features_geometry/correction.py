"""Saved correction products and readable per-source before/after crops."""
import argparse,json
from pathlib import Path
import cv2
import numpy as np
from ..round2 import manifest,get_baseline,contacts
from ..shared.manifest import ROOT,digest
from ..shared.geometry import roi,height_proxy,quantize,mask
from ..shared.geometry_feature_correct import run
from ..shared.contracts import bbox
from ..shared.timing import dump
from ..shared.review import detector_record,save_image
from .reference import DEST,save,line
from .study import probability


def changes(before,after):
    unchanged={tuple(np.asarray(q['polygon']).ravel()):i for i,q in enumerate(before)}
    matched={i:[] for i in range(len(before))}
    for q in after:
        ids=q.get('source_ids')
        if ids is None:ids=[unchanged[tuple(np.asarray(q['polygon']).ravel())]]
        for i in ids:matched[i].append(q['polygon'])
    return [dict(line=i,old=q['polygon'],new=matched[i]) for i,q in enumerate(before)
            if matched[i]!=[q['polygon']]]


def overlay(gray,before,after,delta):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR);H,W=gray.shape
    h=height_proxy(before,(W,H));paper=cv2.boxFilter(gray,cv2.CV_32F,(quantize(3*h)|1,quantize(3*h)|1));ink=paper-gray>255*.06
    old=mask(before,gray.shape,(W,H));new=mask(after,gray.shape,(W,H))
    im[ink&(old>0)&(new==0)]=(20,20,220);im[ink&(new>0)&(old==0)]=(30,180,20)
    changed={d['line'] for d in delta}
    for i,q in enumerate(before):
        if q.get('discounted'):continue
        line(im,q['polygon']+[q['polygon'][0]],(150,150,150) if i in changed else (180,160,150))
    for d in delta:
        for p in d['new']:line(im,p+[p[0]],(30,150,20),2)
    return im


def crops(gray,before,after,delta,out,page):
    if not delta:return []
    im=overlay(gray,before,after,delta);tiles=[];h=height_proxy(before,(gray.shape[1],gray.shape[0]));metadata=[]
    for d in delta:
        b=bbox(before[d['line']]);x0,y0,x1,y1=roi(np.asarray(b)+[-h,-h,h,h],gray.shape)
        raw=cv2.cvtColor(gray[y0:y1,x0:x1],cv2.COLOR_GRAY2BGR);draw=im[y0:y1,x0:x1]
        pair=np.vstack([raw,draw]);scale=min(1,1350/pair.shape[1]);pair=cv2.resize(pair,None,fx=scale,fy=scale)
        tile=np.full((pair.shape[0]+28,1400,3),255,np.uint8);tile[28:,:pair.shape[1]]=pair
        cv2.putText(tile,f"source {d['line']}: raw above; old grey / new green / lost ink red below",(5,19),cv2.FONT_HERSHEY_SIMPLEX,.46,(0,0,0),1)
        tiles.append(tile);metadata.append(dict(line=d['line'],bbox=[x0,y0,x1,y1],sheet=len(tiles[:-1])//8))
    names=[]
    for k in range(0,len(tiles),8):
        name=f'{page}.detail-{k//8:02d}.jpg';save_image(out/name,np.vstack(tiles[k:k+8]));names.append(name)
    dump(out/(page+'.crops.json'),dict(lines=metadata,sheets=names));return names


def study(rows,version):
    out=DEST/f'corrections-v{version}';out.mkdir(parents=True,exist_ok=True)
    summary=[]
    for j,r in enumerate(rows):
        p=r['page'];fp=out/(p+'.evidence.json')
        if fp.exists():summary.append(json.loads(fp.read_text())['summary']);continue
        gray=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r)
        a=run(gray,probability(r),items,version) if not r['parked'] else dict(items=items,added_s=0.,geometry_changes=[],separator_changes=[],geometry_decisions=[],parked=True)
        delta=changes(items,a['items']);stat=dict(page=p,group=r['group'],changed=len(delta),geometry=len(a['geometry_changes']),
            total_items=len(a['items']),added_s=a['added_s'],parked=r['parked'])
        dump(out/(p+'.json'),detector_record(r,a['items'],a['added_s']))
        save(out/(p+'.jpg'),overlay(gray,items,a['items'],delta),p+' | conditional geometry + Q8 separators')
        names=crops(gray,items,a['items'],delta,out,p)
        dump(fp,dict({k:v for k,v in a.items() if k!='items'},changes=delta,summary=stat,crops=names))
        summary.append(stat)
        if (j+1)%20==0:print('corrections',version,j+1,len(rows),flush=True)
    dump(out/'summary.json',summary)
    print('corrections',version,'changed',sum(x['changed']>0 for x in summary),'geometry',sum(x['geometry'] for x in summary),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',type=int,default=1);p.add_argument('--pages',nargs='*');args=p.parse_args();cv2.setNumThreads(1)
    rows=manifest()['pages']
    if args.pages:rows=[r for r in rows if r['page'] in args.pages]
    study(rows,args.version)
