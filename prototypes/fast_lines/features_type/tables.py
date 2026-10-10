"""Table feature rendering and two-route comparison on the supplied table pages."""
import json,argparse
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.type_tables import analyze
from ..shared.timing import dump
from ..shared.review import save_image
from .reference import DEST,label

def names():
    s=json.loads((ROOT/'.astra/fast_lines/discrepancy/selection.json').read_text())
    return [r['page'] for r in s['discrepancy'] if r['category']=='tables']+['s2-831443dc5e6f1ccfbaf5-p00020','an-7a2b17a3fb0f-p000200','an-a73d22211479-p000301','an-1f8e7d022643-p000003']

def draw(g,data,items,docling=()):
    im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
    for b in docling:
        a,t,c,d=map(int,b);cv2.rectangle(im,(a,t),(c,d),(190,70,190),3)
    for r in data['regions']:
        a,t,b,d=map(int,r['bbox']);cv2.rectangle(im,(a,t),(b,d),(30,160,30) if r['status']=='protect' else (0,160,230),3)
        for i in r['cells']:cv2.polylines(im,[np.rint(items[i]['polygon']).astype(np.int32)],True,(190,120,0),1)
    for r in data.get('leaders',[]):
        for x,y in r['points']:cv2.circle(im,(round(x),round(y)),max(1,round(data['height']*.12)),(170,40,170),1)
    for r in data['rules']:cv2.polylines(im,[np.rint(r['path']).astype(np.int32)],False,(0,110,230),2)
    return im


def run(action,version):
    dest=DEST/f'tables-v{version}-{digest(ROOT/"prototypes/fast_lines/shared/type_tables.py")[:12]}'
    dest.mkdir(parents=True,exist_ok=True)
    for row in manifest()['pages']:
        if row['page'] not in names():continue
        p=row['page'];record=dest/(p+'.json');g=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
        if action=='slow':
            if record.exists():continue
            data=dict(page=p,input_sha256=row['sha256'],slow=analyze(g,items,route='slow',version=version))
            lp=ROOT/'.astra/layout'/(p+'.json');data['docling']=[]
            if lp.exists():
                from greekocr.pages.layout import read_layout
                data['docling']=[list(box) for _,box in read_layout(lp,(g.shape[1],g.shape[0]))]
            data['docling_note']='cached boxes' if data['docling'] else 'selection gives count only; proposal coordinates unavailable here'
            dump(record,data);save_image(dest/(p+'.slow.jpg'),label(draw(g,data['slow'],items,data['docling']),p+' | LSD rule graph + aligned cells; purple Docling proposals'))
            print(p,'slow',len(data['slow']['regions']),round(data['slow']['seconds'],3),flush=True)
        else:
            data=json.loads(record.read_text())
            if 'explicit' in data:continue
            for route in ['explicit','heuristic']:
                data[route]=analyze(g,items,route=route,version=version)
                save_image(dest/(p+'.'+route+'.jpg'),label(draw(g,data[route],items),p+' | '+route+' table evidence'))
            data['per_line']=[dict(line=i,slow=i in data['slow']['protected_indices'],route1=i in data['explicit']['protected_indices'],route2=i in data['heuristic']['protected_indices']) for i in range(len(items))]
            dump(record,data);print(p,[(r,len(data[r]['regions'])) for r in ['slow','explicit','heuristic']],flush=True)
    dump(DEST/'active-tables.json',dict(directory=str(dest.relative_to(ROOT)),version=version))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['slow','fast']);p.add_argument('--version',type=int,default=1);a=p.parse_args();cv2.setNumThreads(1);run(a.action,a.version)
