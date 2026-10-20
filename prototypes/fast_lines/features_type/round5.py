"""Owner-review experiments. Unique output directories preserve every iteration."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from ..round2 import manifest
from ..shared.manifest import ROOT, OUT
from ..shared.type_residual import render, scout, ink_scout
from ..shared.review import save_image
from ..shared.timing import dump
from ..shared.detector import Detector
from ..shared.contracts import bbox

DEST = OUT/'round5/type'
PRIOR = ROOT.parent/'greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r4b'
REVIEW = ROOT.parent/'greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r4'
OWN = ['s2-032eaf8e6b3b83918feb-p00004','an-00f143ecce59-p000258',
       's2-c0b02fe229794d2fe76d-p00010','an-2cfe28da5103-p000084',
       'an-00f143ecce59-p000192','an-ef481610a820-p000181','an-1ba3fdb1436b-p000035',
       's2-3229200bf47ca465a42d-p00006','an-d83e7a198ade-p000099',
       's2-49598b2e848ab1f0ee1e-p00001','s2-49598b2e848ab1f0ee1e-p00004',
       's2-3229200bf47ca465a42d-p00004','an-466cffad2cba-p000277',
       's2-86865c33eef5932c013b-p00005','s2-49598b2e848ab1f0ee1e-p00005']


def cohort():
    rows = manifest()['pages']
    for p in sorted((REVIEW/'pages').glob('*.png')):
        rows.append(dict(page=p.stem,path=str(p),group='new_curved',parked=False))
    assert len(rows) == 200
    return rows


def draw(gray, data):
    im = cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    for b in data['bodies']:
        a,t,d,e = map(round,b['bbox'])
        color = (200,120,20) if b['owned'] else (20,130,230)
        if b['rejected']: color=(25,25,220)
        cv2.rectangle(im,(a,t),(d,e),color,1)
    for n,r in enumerate(data['rows']):
        p=np.rint(r['path']).astype(np.int32)
        cv2.polylines(im,[p],False,(180,40,170),2)
        if len(r['free'])>=5:
            a,t,d,e=map(round,r['bbox']);cv2.rectangle(im,(a,t),(d,e),(30,170,30),2)
            cv2.putText(im,str(n),(a,t),cv2.FONT_HERSHEY_SIMPLEX,.5,(30,170,30),1)
    return im


def study(args):
    dest=DEST/args.experiment;dest.mkdir(parents=True,exist_ok=True)
    for row in cohort():
        if row['page'] not in OWN:continue
        page=row['page'];target=dest/(page+'.'+args.route+'.json')
        if target.exists():raise RuntimeError('Experiment already recorded: '+str(target))
        gray=cv2.imread(str(ROOT/row['path']),0)
        items=json.loads((PRIOR/(page+'.json')).read_text())['items']
        ev=json.loads((PRIOR/(page+'.evidence.json')).read_text())
        if args.route=='heuristic':
            candidates=[OUT/'shared/cache'/(page+'.npy'),OUT/'round2/shared/baseline'/(page+'.npy')]
            pm=np.load(next(p for p in candidates if p.exists()))
            r=(scout(pm,items,(gray.shape[1],gray.shape[0]),excluded_regions=ev['removed'],version=args.version) if args.version<3 else
               ink_scout(gray,items,excluded_regions=ev['removed'],version=args.version))
            dump(target,r);im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
            for i,q in enumerate(r['regions']):
                a,t,b,d=map(round,q['bbox']);cv2.rectangle(im,(a,t),(b,d),(30,170,30),2)
                cv2.putText(im,str(i),(a,t),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,0),1)
            save_image(dest/(page+'.heuristic.jpg'),im)
            print(page,len(r['regions']),round(r['seconds']*1000,2),flush=True);continue
        r=render(gray,items,route=args.route,version=args.version,excluded_regions=ev['removed'])
        dump(target,r);im=draw(gray,r)
        save_image(dest/(page+'.'+args.route+'.jpg'),im)
        crops=[]
        for i,rr in enumerate(r['rows']):
            if len(rr['free'])<5:continue
            a,t,b,d=rr['bbox'];h=rr['height'];a=max(0,int(a-h));t=max(0,int(t-h));b=min(gray.shape[1],int(b+h));d=min(gray.shape[0],int(d+h))
            raw=cv2.cvtColor(gray[t:d,a:b],cv2.COLOR_GRAY2BGR);crop=np.vstack([raw,im[t:d,a:b]])
            scale=min(1,1100/crop.shape[1]);crop=cv2.resize(crop,None,fx=scale,fy=scale)
            bar=np.full((27,crop.shape[1],3),255,np.uint8)
            cv2.putText(bar,f'row {i}: {len(rr["free"])} free bodies; h={h:.1f}',(5,19),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
            canvas=np.full((crop.shape[0]+27,1100,3),255,np.uint8);canvas[:27,:bar.shape[1]]=bar;canvas[27:,:crop.shape[1]]=crop;crops.append(canvas)
        for i in range(0,len(crops),6):save_image(dest/(page+f'.{args.route}.free-{i//6:02d}.jpg'),np.vstack(crops[i:i+6]))
        print(page,len(r['rows']),sum(len(q['free'])>=5 for q in r['rows']),round(r['seconds']*1000),flush=True)


def correction(args):
    from ..shared.type_residual_recovery import recover
    dest=DEST/args.experiment;dest.mkdir(parents=True,exist_ok=True);detector=Detector()
    for row in cohort():
        page=row['page']
        if row.get('parked'):continue
        if not args.all and page not in OWN:continue
        if not (PRIOR/(page+'.json')).exists():continue
        target=dest/(page+'.json')
        if target.exists():raise RuntimeError('Experiment already recorded: '+str(target))
        gray=cv2.imread(str(ROOT/row['path']),0);items=json.loads((PRIOR/(page+'.json')).read_text())['items']
        ev=json.loads((PRIOR/(page+'.evidence.json')).read_text())
        r=recover(gray,items,detector,excluded_regions=ev.get('removed',[]),version=args.version)
        dump(target,r);im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
        for q in items:cv2.polylines(im,[np.rint(q['polygon']).astype(np.int32)],True,(180,180,180),1)
        for q in r['added']:cv2.polylines(im,[np.rint(q['polygon']).astype(np.int32)],True,(30,170,30),2)
        save_image(dest/(page+'.jpg'),im)
        tiles=[]
        for i,q in enumerate(r['added']):
            a,t,b,d=bbox(q);h=(d-t)*.6;a=max(0,int(a-h));t=max(0,int(t-h));b=min(gray.shape[1],int(b+h));d=min(gray.shape[0],int(d+h))
            tile=np.vstack([cv2.cvtColor(gray[t:d,a:b],cv2.COLOR_GRAY2BGR),im[t:d,a:b]])
            scale=min(1,1100/tile.shape[1]);tile=cv2.resize(tile,None,fx=scale,fy=scale)
            canvas=np.full((tile.shape[0]+26,1100,3),255,np.uint8);canvas[26:,:tile.shape[1]]=tile
            cv2.putText(canvas,f'{page} addition {i}',(5,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1);tiles.append(canvas)
        for i in range(0,len(tiles),4):save_image(dest/(page+f'.add-{i//4:02d}.jpg'),np.vstack(tiles[i:i+4]))
        print(page,'added',len(r['added']),'requests',len(r['requests']),'calls',len(r['calls']),'ms',round(r['seconds']*1000),flush=True)


def initials(args):
    from ..shared.type_initials import render as initial_render,complete
    from ..shared.geometry import height_proxy
    dest=DEST/args.experiment;dest.mkdir(parents=True,exist_ok=True)
    for row in cohort():
        page=row['page'];f=PRIOR/(page+'.evidence.json')
        if not f.exists():continue
        ev=json.loads(f.read_text());added=ev.get('added',[])
        extra=[]
        if args.recover_from:
            sf=DEST/args.recover_from/(page+'.json')
            if sf.exists():extra=json.loads(sf.read_text())['added'];added=added+extra
        if not added:continue
        if (dest/(page+'.json')).exists():raise RuntimeError('Already recorded')
        g=cv2.imread(str(ROOT/row['path']),0);items=json.loads((PRIOR/(page+'.json')).read_text())['items']+extra;h=height_proxy(items,(g.shape[1],g.shape[0]));records=[]
        for i,q in enumerate(added):
            record={route:initial_render(g,q,items,h,route=route,excluded_regions=ev.get('removed',[])) for route in ('slow','explicit','heuristic')}
            after,receipt=complete(g,q,items,h,excluded_regions=ev.get('removed',[]));record.update(after=after,receipt=receipt);records.append(record)
            if not any(r['candidates'] for r in [record['slow'],record['explicit'],record['heuristic']]):continue
            a,t,b,d=record['slow']['crop'];b=min(g.shape[1],b+round(6*h));tiles=[]
            for route in ['raw','slow','explicit','heuristic','after']:
                im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
                if route in ('slow','explicit','heuristic'):
                    for c in record[route]['candidates']:
                        x0,y0,x1,y1=map(round,c['bbox']);col=(30,170,30) if c['accepted'] else (0,110,240);cv2.rectangle(im,(x0,y0),(x1,y1),col,2)
                if route=='after':cv2.polylines(im,[np.rint(after['polygon']).astype(np.int32)],True,(30,170,30),2)
                tiles.append(im[t:d,a:b])
            save_image(dest/(page+f'.{i}.jpg'),np.vstack(tiles))
        dump(dest/(page+'.json'),records);print(page,[(i,r['receipt']['changed']) for i,r in enumerate(records)],flush=True)


if __name__=='__main__':
    from ..shared.contracts import bbox
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['study','correction','initials']);ap.add_argument('--experiment',required=True);ap.add_argument('--all',action='store_true')
    ap.add_argument('--recover-from')
    ap.add_argument('--route',default='slow');ap.add_argument('--version',type=int,default=1)
    args=ap.parse_args();cv2.setNumThreads(1);globals()[args.action](args)
