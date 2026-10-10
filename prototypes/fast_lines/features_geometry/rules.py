"""Inspect a dense curved-stroke rendering before invoking its splitter."""
import argparse,json
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..layout_barriers.fast import scout,verify_rule
from ..shared.geometry_feature_rules import curved_rule
from ..shared.timing import dump
from ..shared.manifest import ROOT
from .reference import DEST,line,save


def run(rows):
    out=DEST/'explicit-curved-rules';out.mkdir(parents=True,exist_ok=True)
    for r in rows:
        p=r['page'];fp=out/(p+'.json')
        if fp.exists():continue
        gray=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r)
        w,_=scout(gray,items);record=[];im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
        for j,c in enumerate(w['candidates']):
            a,why=verify_rule(gray,c,w['height']);b,reason=curved_rule(gray,c,w['height'])
            record.append(dict(candidate=j,corridor=c,straight=a,straight_reason=why,curve=b,curve_reason=reason))
            if a:line(im,a['path'],(220,90,20),3)
            if b:line(im,b['path'],(30,180,30),2)
            if not b:
                x0,y0,x1,y1=np.rint(c['bbox']).astype(int);cv2.rectangle(im,(x0,y0),(x1,y1),(0,160,220),1)
        dump(fp,dict(page=p,records=record,height=w['height']))
        save(out/(p+'.jpg'),im,p+' | dense curved stroke green; straight blue; unsupported amber')
    print('rules',len(rows),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pages',nargs='*');args=p.parse_args();cv2.setNumThreads(1)
    rows=manifest()['pages']
    if args.pages:rows=[r for r in rows if r['page'] in args.pages]
    run(rows)
