"""Explicit terminal dot row witnesses and regional table boundaries."""
import argparse,json
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.type_table_extent import analyze
from ..shared.timing import dump
from ..shared.review import save_image
from .reference import DEST,label
from .tables import names


def run(action,version,triggered=False):
    selected=names()
    if triggered:
        from .audit4 import pointer
        selected={f.name.removesuffix('.evidence.json') for f in pointer('active-final4.json').glob('*.evidence.json')
                  if json.loads(f.read_text()).get('table_extents') is not None}
    dest=DEST/(f'round4-tables-v{version}-{digest(ROOT/"prototypes/fast_lines/shared/type_table_extent.py")[:12]}'+('-triggered' if triggered else ''));dest.mkdir(exist_ok=True)
    for row in manifest()['pages']:
        if row['page'] not in selected:continue
        p=row['page'];g=cv2.imread(str(ROOT/row['path']),0);it=get_baseline(row);f=dest/(p+'.json')
        if triggered:
            from ..layout_barriers.fast import run as separators
            it=separators(g,it)['items']
        data=dict(page=p,input_sha256=row['sha256'],slow=analyze(g,it,version=version)) if action=='slow' else json.loads(f.read_text())
        if action=='fast':
            for r in ['explicit','heuristic']:data[r]=analyze(g,it,route=r,version=version)
        dump(f,data)
        for route in ['slow'] if action=='slow' else ['explicit','heuristic']:
            r=data[route];im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
            for reg in r['regions']:
                a,t,b,d=map(round,reg['bbox']);cv2.rectangle(im,(a,t),(b,d),(20,145,30),3)
            for z in r['rows']:
                a,t,b,d=z['bbox'];cv2.rectangle(im,(a,t),(b,d),(180,80,20),1)
                for x,y in z['points']:cv2.circle(im,(round(x),round(y)),max(2,round(z['height']*.13)),(170,20,170),1)
            save_image(dest/(p+'.'+route+'.jpg'),label(im,p+' '+route+' | individual dots purple; witnessed rows blue; extent green'))
        print(p,[(r,len(data[r]['rows']),len(data[r]['regions'])) for r in data if r in ['slow','explicit','heuristic']],flush=True)
    dump(DEST/('active-extents4-triggered.json' if triggered else 'active-extents4.json'),dict(directory=str(dest.relative_to(ROOT)),version=version))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['slow','fast']);p.add_argument('--version',type=int,default=1);p.add_argument('--triggered',action='store_true');a=p.parse_args();cv2.setNumThreads(1);run(a.action,a.version,a.triggered)
