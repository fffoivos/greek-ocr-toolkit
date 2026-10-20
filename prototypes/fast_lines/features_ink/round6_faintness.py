"""Immutable R6 faintness experiments and evidence exports; runtime has no cohort."""
import argparse,hashlib,json
from pathlib import Path
import cv2,numpy as np
from ..round2 import ROOT,manifest,get_baseline
from ..stack import Stack
from ..shared.detector import Detector,postprocess
from ..shared.ink_faintness import render
from ..shared.timing import dump
from ..features_geometry.round5_benchmark import render as numbered
from ..shared.review import detector_record
REVIEW=ROOT.parent/'greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r4'
DEST=ROOT/'.astra/fast_lines/out/round6/A_faintness'
PREVIOUS=ROOT.parent/'greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r5'


def cohort():
    rows=list(manifest()['pages'])
    for p in sorted((REVIEW/'pages').glob('*.png')):
        g=cv2.imread(str(p),0);rows.append(dict(page=p.stem,path=str(p),image_size=[g.shape[1],g.shape[0]],group='new_supplied',direction='new',parked=False,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    assert len(rows)==208 and len({r['page'] for r in rows})==208
    return rows


def inputs(row):
    gray=cv2.imread(str(ROOT/row['path']),0)
    p=PREVIOUS/(row['page']+'.json')
    if p.exists():items=json.loads(p.read_text())['items']
    else:
        p=DEST/'baseline'/(row['page']+'.json')
        if p.exists():items=json.loads(p.read_text())['items']
        else:
            r=Stack()(ROOT/row['path'],parked=row['parked']);items=r['items'];dump(p,dict(r))
    return gray,items


def picture(gray,items,evidence,path):
    s=min(1.,1800/gray.shape[1]);im=cv2.cvtColor(cv2.resize(gray,None,fx=s,fy=s),cv2.COLOR_GRAY2BGR)
    for r in evidence['regions']:
        for g in r['components']:
            if not g['body']:continue
            a,b,c,d=np.rint(np.array(g['bbox'])*s).astype(int)
            color=(30,50,230) if g['faint'] else (25,160,10)
            cv2.rectangle(im,(a,b),(c,d),color,1)
        a,b,c,d=np.rint(np.array(r['bbox'])*s).astype(int)
        cv2.rectangle(im,(a,b),(c,d),(0,0,255) if r['drop'] else (220,90,10),1)
        cv2.putText(im,f"{r['line']}: {r['normal']}/{r['bodies']}",(a,max(12,b)),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),3)
        cv2.putText(im,f"{r['line']}: {r['normal']}/{r['bodies']}",(a,max(12,b)),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,0,0),1)
    cv2.imwrite(str(path),im)
    strokes=cv2.cvtColor(cv2.resize(gray,None,fx=s,fy=s),cv2.COLOR_GRAY2BGR)
    for r in evidence['regions']:
        for g in r['components']:
            if not g['body']:continue
            a,b,c,d=np.rint(np.array(g['bbox'])*s).astype(int)
            ratio=g['relative_stroke'];color=(220,90,10) if ratio<1 else (160,0,160)
            cv2.rectangle(strokes,(a,b),(c,d),color,1)
    cv2.imwrite(str(path.with_name(path.stem+'.strokes.jpg')),strokes)


def study(version,pages):
    out=DEST/version;out.mkdir(parents=True,exist_ok=False)
    for row in cohort():
        if pages and not any(q in row['page'] for q in pages):continue
        gray,items=inputs(row)
        for route in ('slow','explicit'):
            e=render(gray,items,route=route);dump(out/(row['page']+'.'+route+'.json'),e)
            picture(gray,items,e,out/(row['page']+'.'+route+'.jpg'))
            print(row['page'],route,len(e['regions']),e['reference'],e['suppress_indices'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('version');ap.add_argument('--pages',nargs='*');a=ap.parse_args();study(a.version,a.pages)
