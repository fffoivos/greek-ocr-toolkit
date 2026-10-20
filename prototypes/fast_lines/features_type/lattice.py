"""Lattice rendering before recovery: raw ridges, pitch, phase and empty slots."""
import argparse,json
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.type_lattice import analyze
from ..shared.review import save_image
from ..shared.timing import dump
from .reference import DEST,label

ANCHORS=['an-1ba3fdb1436b-p000009','s2-86865c33eef5932c013b-p00007','an-d83e7a198ade-p000099','s2-77d1bd63d5babbe0df73-p00001','an-c153f2c605b3-p000056','s2-09f5dfca4af4d74173c6-p00005']

def draw(gray,data):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    for b in data['blocks']:
        for y in np.arange(b['y0'],b['y1']+b['pitch']/2,b['pitch']):
            p=np.array([[x,y+b['slope']*(x-b['xref'])] for x in [b['x0'],b['x1']]],np.int32)
            cv2.polylines(im,[p],False,(180,130,80),1)
    for rr in data['raw_rows']:
        b=data['blocks'][rr['block']]
        for y in rr['peaks']:
            p=np.array([[x,y+b['slope']*(x-b['xref'])] for x in [b['x0'],b['x1']]],np.int32);cv2.polylines(im,[p],False,(190,70,170),1)
    for r in data['slots']:
        col=(40,175,40) if r['supported'] else (0,150,235)
        for k,(a,t,b,d) in enumerate(r['components']):
            cc=(150,150,150) if r.get('owned_centres',[]) and r['owned_centres'][k] else col
            cv2.rectangle(im,(round(a),round(t)),(round(b),round(d)),cc,1)
        for x in [r['x0'],r['x1']]:cv2.circle(im,(round(x),round(r['y']+r['slope']*(x-r['xref']))),max(2,round(.2*r['height'])),col,2)
    return im


def run(action,version,all_ours=False,all_pages=False):
    dest=DEST/f'lattice-v{version}-{digest(ROOT/"prototypes/fast_lines/shared/type_lattice.py")[:12]}';dest.mkdir(parents=True,exist_ok=True)
    for row in manifest()['pages']:
        if not (all_pages or row['page'] in ANCHORS or all_ours and row['direction']=='ours_more'):continue
        p=row['page'];record=dest/(p+'.json');g=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
        if action=='slow':
            if record.exists():continue
            data=dict(page=p,input_sha256=row['sha256'],slow=analyze(g,items,route='slow',version=version));dump(record,data)
            save_image(dest/(p+'.slow.jpg'),label(draw(g,data['slow']),p+' | blue pitch grid, magenta actual raw ridges, green/amber slots'))
            print(p,'slots',len(data['slow']['slots']),'ink',sum(q['supported'] for q in data['slow']['slots']),flush=True)
        else:
            data=json.loads(record.read_text())
            if 'explicit' in data:continue
            for route in ['explicit','heuristic']:
                data[route]=analyze(g,items,route=route,version=version);save_image(dest/(p+'.'+route+'.jpg'),label(draw(g,data[route]),p+' | '+route+' lattice'))
            data['per_slot']=[dict(slot=i,slow_bodies=q['bodies'],route1_bodies=data['explicit']['slots'][i]['bodies'],route2_bodies=data['heuristic']['slots'][i]['bodies']) for i,q in enumerate(data['slow']['slots'])]
            dump(record,data);print(p,'fast ink',sum(q['supported'] for q in data['heuristic']['slots']),flush=True)
    dump(DEST/'active-lattice.json',dict(directory=str(dest.relative_to(ROOT)),version=version))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['slow','fast']);p.add_argument('--version',type=int,default=1);p.add_argument('--all-ours',action='store_true');p.add_argument('--all-pages',action='store_true');a=p.parse_args();cv2.setNumThreads(1);run(a.action,a.version,a.all_ours,a.all_pages)
