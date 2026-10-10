import argparse
import cv2,numpy as np
from .round5_data import rows,load,DEST
from ..layout_barriers.fast import scout
from ..shared.geometry_columns import analyze,apply
from ..shared.timing import dump

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='1');ap.add_argument('--pages',nargs='+');a=ap.parse_args();out=DEST/('columns-v'+a.version);out.mkdir(parents=True,exist_ok=True)
    for row in rows():
        if a.pages and not any(k in row['page'] for k in a.pages):continue
        dst=out/(row['page']+'.json')
        if dst.exists():raise RuntimeError('Already recorded '+str(dst))
        g,obj,pm=load(row);w,p=scout(g,obj['original']);e=analyze(g,obj['original'],w,p,route='slow',version=int(a.version));r=apply(obj['items'],e);dump(dst,dict(e,changes=r['changes']))
        im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
        for q in obj['items']:cv2.polylines(im,[np.rint(q['polygon']).astype(np.int32)],True,(170,170,170),1)
        for rec in e['rules']:
            if 'rule' not in rec:continue
            color=(0,150,0) if rec['accepted'] else (0,0,220);cv2.polylines(im,[np.rint(rec['rule']['path']).astype(np.int32)],False,color,3)
            for cross in (rec.get('native') or {}).get('through',[]):cv2.polylines(im,[np.rint(cross['path']).astype(np.int32)],False,(0,0,240),3)
            for side in ('left','right'):
                for pt in rec['endpoints'][side]:cv2.circle(im,tuple(np.rint(pt['point']).astype(int)),max(2,round(.18*w['height'])),color,2)
        for c in r['changes']:
            for q in c['new']:cv2.polylines(im,[np.rint(q).astype(np.int32)],True,(180,0,180),2)
        s=min(1,1600/im.shape[1]);cv2.imwrite(str(dst.with_suffix('.jpg')),cv2.resize(im,None,fx=s,fy=s))
        print(row['page'],len(e['rules']),sum(q['accepted'] for q in e['rules']),len(r['changes']),flush=True)
if __name__=='__main__':main()
