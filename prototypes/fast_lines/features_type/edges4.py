"""Explicit original-ink extension of the type grid on all41ours_more pages."""
import argparse,json
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..layout_barriers.fast import run as separators
from ..shared.manifest import ROOT,digest
from ..shared.type_grid_edges import analyze
from ..shared.timing import dump
from ..shared.review import save_image
from ..shared.geometry import roi
from .reference import DEST,label


def draw(g,data):
    im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
    for b in data['blocks']:
        for y in b['centres']:cv2.line(im,(round(b['x0']),round(y+b['slope']*(b['x0']-b['xref']))),(round(b['x1']),round(y+b['slope']*(b['x1']-b['xref']))),(170,170,170),1)
    for i,s in enumerate(data['slots']):
        color=(20,150,20) if s['supported'] and s['owned_fraction']<.25 else (20,140,220)
        cv2.line(im,(round(s['x0']),round(s['y'])),(round(s['x1']),round(s['y'])),color,2)
        for a,t,b,d in s['components']:cv2.rectangle(im,(round(a),round(t)),(round(b),round(d)),color,1)
        cv2.putText(im,str(i),(round(s['x0']),round(s['y'])),cv2.FONT_HERSHEY_SIMPLEX,.5,color,1)
    return im


def run(action,version,controls,all_pages=False):
    dest=DEST/(f'round4-edges-v{version}-{digest(ROOT/"prototypes/fast_lines/shared/type_grid_edges.py")[:12]}'+('-all' if all_pages else ''));dest.mkdir(exist_ok=True)
    tiles=[];ledger=[]
    for row in manifest()['pages']:
        if not all_pages and row['direction']!='ours_more' and not(controls and row['group']=='agreement'):continue
        p=row['page'];g=cv2.imread(str(ROOT/row['path']),0);it=separators(g,get_baseline(row))['items'];f=dest/(p+'.json')
        data=dict(page=p,input_sha256=row['sha256'],slow=analyze(g,it,route='slow',version=version)) if action=='slow' else json.loads(f.read_text())
        if action=='fast':
            for route in ['explicit','heuristic']:data[route]=analyze(g,it,route=route,version=version)
        dump(f,data);routes=['slow'] if action=='slow' else ['slow','explicit','heuristic']
        imgs={r:draw(g,data[r]) for r in routes}
        for r in routes:save_image(dest/(p+'.'+r+'.jpg'),label(imgs[r],p+' '+r+' | grid axes grey; edge ink green; uncertain amber'))
        for i,s in enumerate(data['slow']['slots']):
            h=s['height'];a,t,b,d=roi([s['x0'],s['y']-2*h,s['x1'],s['y']+2*h],g.shape)
            crop=np.vstack([cv2.cvtColor(g[t:d,a:b],cv2.COLOR_GRAY2BGR)]+[imgs[r][t:d,a:b] for r in routes]);sc=min(1,1050/crop.shape[1]);crop=cv2.resize(crop,None,fx=sc,fy=sc)
            tiles.append(label(crop,p+f' edge{i} raw/'+ '/'.join(routes)));ledger.append(dict(page=p,slot=i,board=(len(tiles)-1)//4))
        print(p,len(data['slow']['slots']),sum(s['supported'] and s['owned_fraction']<.25 for s in data['slow']['slots']),flush=True)
    for i in range(0,len(tiles),4):save_image(dest/(action+f'-edges-{i//4:02d}.jpg'),np.vstack(tiles[i:i+4]))
    dump(dest/(action+'-review.json'),ledger);dump(DEST/'active-edges4.json',dict(directory=str(dest.relative_to(ROOT)),version=version))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['slow','fast']);p.add_argument('--version',type=int,default=1);p.add_argument('--controls',action='store_true');p.add_argument('--all',action='store_true');a=p.parse_args();cv2.setNumThreads(1);run(a.action,a.version,a.controls,a.all)
