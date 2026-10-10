"""Round4 component rendering; run slow then inspect before fast."""
import argparse,json
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.type_rows import render
from ..shared.review import save_image
from ..shared.geometry import roi
from ..shared.contracts import bbox
from ..shared.timing import dump
from .reference import DEST,label

NAMES=['an-d3237d690aa0-p000138','an-d83e7a198ade-p000099','an-ffccc97c07de-p000152','s2-3229200bf47ca465a42d-p00004','s2-77d1bd63d5babbe0df73-p00001']

def draw(g,r):
    im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
    for k,b in enumerate(r['bands']):
        col=(40,160,40) if b['supported'] else (0,160,220)
        for c in b['components']:
            a,t,d,e=map(round,c['bbox']);cv2.rectangle(im,(a,t),(d,e),col,1)
        for m in b['marks']:
            a,t,d,e=map(round,m['bbox']);cv2.rectangle(im,(a,t),(d,e),(0,130,240),1)
        for key,c in [('mass_top',(190,100,20)),('mass_bottom',(190,50,180))]:
            p=np.rint(b['paths'][key]).astype(np.int32)
            if len(p)>1:cv2.polylines(im,[p],False,c,1)
    return im


def run(action,version):
    dest=DEST/f'round4-rows-v{version}-{digest(ROOT/"prototypes/fast_lines/shared/type_rows.py")[:12]}';dest.mkdir(exist_ok=True)
    for row in manifest()['pages']:
        if row['page'] not in NAMES:continue
        p=row['page'];g=cv2.imread(str(ROOT/row['path']),0);it=get_baseline(row);f=dest/(p+'.json')
        if action=='slow':
            data=dict(page=p,sha256=row['sha256'],slow=[render(g,q,route='slow',version=version) for q in it]);dump(f,data)
        else:
            data=json.loads(f.read_text())
            for route in ['explicit','heuristic']:data[route]=[render(g,q,route=route,version=version) for q in it]
            dump(f,data)
        routes=['slow'] if action=='slow' else ['slow','explicit','heuristic']
        full={r:cv2.cvtColor(g,cv2.COLOR_GRAY2BGR) for r in routes}
        tiles=[]
        for i,q in enumerate(it):
            b=bbox(q);pad=(b[3]-b[1])*.65;a,t,c,d=roi([b[0],b[1]-pad,b[2],b[3]+pad],g.shape)
            crops=[cv2.cvtColor(g[t:d,a:c],cv2.COLOR_GRAY2BGR)]
            for r in routes:
                im=draw(g,data[r][i]);crops.append(im[t:d,a:c])
                full[r][t:d,a:c]=im[t:d,a:c]
            crop=np.vstack(crops);sc=min(1,1050/crop.shape[1]);crop=cv2.resize(crop,None,fx=sc,fy=sc)
            text=' / '.join(f"{r}:{sum(z['supported'] and z['within_box'] for z in data[r][i]['bands'])}" for r in routes)
            tiles.append(label(crop,f'{p} line{i} raw / {text}'))
        for i in range(0,len(tiles),5):save_image(dest/(p+f'.{action}.detail-{i//5:02d}.jpg'),np.vstack(tiles[i:i+5]))
        for r,im in full.items():save_image(dest/(p+'.'+r+'.jpg'),label(im,p+' '+r+' body rows / joined mass envelopes'))
        print(p,len(it),sum(r['ambiguous'] for r in data['slow']),flush=True)
    dump(DEST/'active-rows4.json',dict(directory=str(dest.relative_to(ROOT)),version=version))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['slow','fast']);p.add_argument('--version',type=int,default=1);a=p.parse_args();cv2.setNumThreads(1);run(a.action,a.version)
