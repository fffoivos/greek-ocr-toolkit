import argparse
import cv2,numpy as np
from .round5_data import rows,load,DEST
from ..shared.geometry_envelopes import correct
from ..shared.timing import dump
from .round5_shapes import draw

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pages',nargs='+');ap.add_argument('--version',default='1');a=ap.parse_args();out=DEST/('shape-corrections-v'+a.version);out.mkdir(parents=True,exist_ok=True)
    for row in rows():
        if a.pages and not any(k in row['page'] for k in a.pages):continue
        dst=out/(row['page']+'.json')
        if dst.exists():raise RuntimeError('Already recorded '+str(dst))
        g,obj,pm=load(row);r=correct(g,pm,obj['items'],obj['original'],forbidden_regions=obj.get('removed',[]),detail=True) if not row['parked'] else dict(items=obj['items'],changes=[],decisions=[],seconds=0)
        dump(dst,r)
        im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
        for q in obj['items']:cv2.polylines(im,[np.rint(q['polygon']).astype(np.int32)],True,(170,170,170),1)
        for c in r['changes']:
            for p in c['new']:cv2.polylines(im,[np.rint(p).astype(np.int32)],True,(180,0,180),2)
        sc=min(1,1600/im.shape[1]);cv2.imwrite(str(dst.with_suffix('.jpg')),cv2.resize(im,None,fx=sc,fy=sc))
        print(row['page'],len(r['changes']),round(r['seconds']*1000,1),flush=True)
if __name__=='__main__':main()
