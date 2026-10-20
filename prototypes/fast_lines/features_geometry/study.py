"""Feature routes against independent explicit renderings, page and line ledgers."""
import argparse
import json
from pathlib import Path
from time import perf_counter
import cv2
import numpy as np
from ..round2 import manifest,get_baseline,COMMON,OLD,contacts
from ..shared.manifest import ROOT,digest
from ..shared.timing import dump
from ..shared.geometry_feature_paths import bands,sparse
from ..shared.geometry_feature_separation import route1,route2
from .reference import DEST,FEATURES,line,save


def probability(row):
    p=OLD/(row['page']+'.npy')
    if not p.exists():p=COMMON/'baseline'/(row['page']+'.npy')
    return np.load(p)


def comparisons(items,ref,r1,r2):
    out=[];d1={q['line']:q for q in r1['lines']};d2={q['line']:q for q in r2['lines']}
    def against_model(a):
        targets=[]
        if a.get('path'):
            x,y=np.asarray(a['path']).T
            for old in ref['lines']:
                ox,oy=np.asarray(old['centre']).T
                good=(x>=ox[0])&(x<=ox[-1])
                if good.sum()<3:continue
                delta=y[good]-np.interp(x[good],ox,oy);offset=float(np.median(delta))
                if abs(offset)>2*old['height']:continue
                targets.append(dict(model_line=old['id'],overlap_h=float(np.ptp(x[good])/old['height']),
                    median_offset_h=offset/old['height'],shape_p90_h=float(np.quantile(abs(delta-offset),.9)/old['height']),
                    angle_delta_deg=a['angle_deg']-old['angle_deg']))
        return targets
    for i,q in enumerate(items):
        a=d1.get(i,{});b=d2.get(i,{})
        out.append(dict(line=i,route1_status=a.get('status','absent'),route1_band=a.get('band'),
            route1_bend_h=a.get('bend_h'),route2_bend_h=b.get('bend_h'),
            route2_skew_error_h=b.get('skew_error_h'),model_candidates=against_model(a),
            route2_model_candidates=against_model(b),
            verdict='unadjudicated; overlapping model lines are hypotheses, not labels'))
    return out


def draw(gray,ref,geom,separation,feature,color):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    if feature=='separation':
        for c in ref['corridors']:
            a,b,z,d=np.rint(c['bbox']).astype(int);cv2.rectangle(im,(a,b),(z,d),(130,170,130),1)
        for c in separation['corridors']:
            a,b,z,d=np.rint(c['bbox']).astype(int);cv2.rectangle(im,(a,b),(z,d),color,2)
        return im
    for q in ref['lines']:line(im,q['centre' if feature=='curvature' else 'affine'],(100,170,100))
    for q in geom['lines']:
        if 'path' not in q:continue
        path=q['path' if feature=='curvature' else 'affine'];line(im,path,color,2)
    return im


def run(rows,version):
    dest=DEST/f'routes-v{version}';dest.mkdir(parents=True,exist_ok=True)
    for j,r in enumerate(rows):
        p=r['page'];fp=dest/(p+'.json')
        expected=[dest/(p+'.'+f+'.'+v+'.jpg') for f in FEATURES for v in ('r1','r2')]
        if fp.exists() and all(q.exists() for q in expected):continue
        gray=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r);pm=probability(r)
        refpath=DEST/'explicit-v2'/(p+'.json')
        if not refpath.exists():refpath=DEST/'explicit-v1'/(p+'.json')
        ref=json.loads(refpath.read_text())
        if r['parked']:a=b=dict(lines=[],height=ref['height'],seconds=0.);c=d=dict(corridors=[],seconds=0.)
        else:a=bands(pm,items,r['image_size'],version);b=sparse(pm,items,r['image_size'],version);c=route1(gray,items);d=route2(items,r['image_size'])
        comp=comparisons(items,ref,a,b)
        dump(fp,dict(page=p,reference=str(refpath.relative_to(ROOT)),reference_sha256=digest(refpath),
            route1=a,route2=b,separation1=c,separation2=d,lines=comp))
        for feature in FEATURES:
            save(dest/(p+'.'+feature+'.r1.jpg'),draw(gray,ref,a,c,feature,(220,100,0)),p+' | '+feature+' R1 blue vs model green')
            save(dest/(p+'.'+feature+'.r2.jpg'),draw(gray,ref,b,d,feature,(180,30,180)),p+' | '+feature+' R2 purple vs model green')
        if (j+1)%20==0:print('routes',version,j+1,len(rows),flush=True)
    print('complete routes',dest,len(rows),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',type=int,default=1);p.add_argument('--pages',nargs='*');args=p.parse_args()
    cv2.setNumThreads(1);rows=manifest()['pages']
    if args.pages:rows=[r for r in rows if r['page'] in args.pages]
    run(rows,args.version)
