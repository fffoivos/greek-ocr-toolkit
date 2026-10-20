"""Immutable task B experiments on the explicitly authorized 208-page cohort."""
import argparse,json
from pathlib import Path
import cv2,numpy as np
from ..features_ink.round6_faintness import cohort,ROOT
from ..shared.geometry_rows import render,analyze,scout
from ..shared.geometry import roi
from ..shared.contracts import bbox
from ..shared.timing import dump

DEST=ROOT/'.astra/fast_lines/out/round6/B_rows'
BASE=ROOT.parent/'greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round6/A_faintness/final'


def inputs(row):
    return cv2.imread(str(ROOT/row['path']),0),json.load(open(BASE/(row['page']+'.json')))['items']


def draw(gray,items,evidence,path,*,crop=None,title=''):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    if crop is None:crop=[0,0,gray.shape[1],gray.shape[0]]
    for r in evidence['records']:
        p=np.rint(items[r['line']]['polygon']).astype(int);cv2.polylines(im,[p],True,(160,160,160),2)
        for b in r.get('bodies',[]):
            cv2.polylines(im,[np.rint(b['polygon']).astype(int)],True,(0,130,0) if b['complete'] else (150,150,150),1)
        for k,t in enumerate(r['tracks']):
            color=(230,40,0) if t['word'] else (0,150,210)
            cv2.polylines(im,[np.rint(t['path']).astype(int)],False,color,2)
        for bridge in r.get('bridges',[]):cv2.polylines(im,[np.rint(bridge['path']).astype(int)],False,(0,150,0),1)
        for v in r.get('valleys',[]):
            if v['path']:cv2.polylines(im,[np.rint(v['path']).astype(int)],False,(200,0,200) if v['accepted'] else (0,90,230),2)
        x,y=p.min(0);cv2.putText(im,str(r['line']),(x,max(12,y)),0,.5,(0,0,240),1)
    a,b,c,d=crop;im=im[b:d,a:c];s=min(1.,1600/im.shape[1]);im=cv2.resize(im,None,fx=s,fy=s)
    if title:
        bar=np.full((30,im.shape[1],3),255,np.uint8);cv2.putText(bar,title,(5,20),0,.45,(0,0,0),1);im=np.vstack([bar,im])
    cv2.imwrite(str(path),im)


def study(version,pages,marked=False):
    cv2.setNumThreads(2)
    out=DEST/version;out.mkdir(parents=True,exist_ok=False)
    marks=json.load(open(BASE/'owner-marks.json'))
    for row in cohort():
        p=row['page']
        if pages and not any(k in p for k in pages):continue
        gray,items=inputs(row);lookup={json.dumps(q['polygon']):i for i,q in enumerate(items)}
        mm=[dict(m,item_index=lookup[json.dumps(m['polygon'])]) for m in marks if m['page']==p and json.dumps(m['polygon']) in lookup]
        selected={m['item_index'] for m in mm} if marked else None
        for route in ('slow','explicit'):
            e=render(gray,items,route=route,selected=selected);dump(out/(p+'.'+route+'.json'),e)
            draw(gray,items,e,out/(p+'.'+route+'.jpg'))
            for m in mm:
                i=m['item_index'];q=items[i];a,b,c,d=bbox(q);h=e['height'];crop=roi([a-h,b-h,c+h,d+h],gray.shape)
                sub=dict(records=[r for r in e['records'] if r['line']==i]);draw(gray,items,sub,out/f'{p}.{i}.{route}.jpg',crop=crop,title=f'{p} {i} owner={m["mark"]} {route}')
            print(p,route,len(e['records']),sum(sum(t['word'] for t in r['tracks'])>=2 for r in e['records']),round(e['seconds'],2),flush=True)


def pilot(version,pages):
    cv2.setNumThreads(2)
    out=DEST/version;out.mkdir(parents=True,exist_ok=False)
    for row in cohort():
        p=row['page']
        if pages and not any(k in p for k in pages):continue
        gray,items=inputs(row)
        # Offline diagnostic has no runtime source refresh. Use legacy extent;
        # this is not the default-stack qualification oracle.
        e=analyze(gray,items,complete_children=False) if not row['parked'] else dict(items=items,changes=[],records=[],scout={},seconds=0)
        dump(out/(p+'.json'),e);draw(gray,items,e,out/(p+'.jpg'))
        for c in e['changes']:
            i=c['line'];a,b,cc,d=bbox(items[i]);h=e['scout']['height'];crop=roi([a-h,b-h,cc+h,d+h],gray.shape)
            rec=next(r for r in e['records'] if r['line']==i)
            draw(gray,items,dict(records=[rec]),out/f'{p}.{i}.jpg',crop=crop,title=f'{p} {i} proposed split')
        print(p,len(e['scout'].get('candidates',[])),len(e['changes']),round(e['seconds']*1000,2),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('version');ap.add_argument('--pages',nargs='*');ap.add_argument('--marked',action='store_true');ap.add_argument('--pilot',action='store_true');a=ap.parse_args()
    (pilot(a.version,a.pages) if a.pilot else study(a.version,a.pages,a.marked))
