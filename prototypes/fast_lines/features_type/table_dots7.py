"""Diagnostic cycle7: make a purported dot's filled interior explicit.

The prior compactness test admits small letter bodies when localization straddles
rows. A dot should have an ink-filled interior, not a character counter. This
wrapper is deliberately outside runtime; source and rejected witnesses remain.
"""
import argparse, json
from time import perf_counter
import cv2
import numpy as np
from ..round2 import manifest, get_baseline
from ..layout_barriers.fast import run as separators
from ..shared.type_table_extent import analyze as previous
from ..shared.geometry import roi
from ..shared.contracts import bbox
from ..shared.manifest import ROOT
from ..shared.review import save_image
from ..shared.timing import dump
from .reference import DEST, label
from .tables import names
from .audit4 import pointer


def interior(gray, point, height, route):
    x, y = point
    a, t, b, d = roi([x-height*.6,y-height*.6,x+height*.6,y+height*.6], gray.shape)
    g = gray[t:d,a:b]
    factor = 1 if route == 'slow' else max(1,height/(20 if route == 'explicit' else 8))
    if factor > 1:
        g = cv2.resize(g,None,fx=1/factor,fy=1/factor,interpolation=cv2.INTER_AREA)
    paper = float(np.percentile(g,90)); depth = paper-g.astype(float)
    ink = (depth > max(.18*paper,.5*np.percentile(depth,95))).astype(np.uint8)
    _, lab, s, c = cv2.connectedComponentsWithStats(ink,8)
    if len(s)<2:return dict(filled=False,reason='no component')
    centre = np.array([(x-a)*g.shape[1]/(b-a),(y-t)*g.shape[0]/(d-t)])
    idx = int(np.argmin(np.linalg.norm(c[1:]-centre,axis=1)))+1
    sx,sy,w,h,area = s[idx]
    z = (lab[sy:sy+h,sx:sx+w]==idx).astype(np.uint8)
    _,hierarchy = cv2.findContours(z,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    counters = 0 if hierarchy is None else sum(int(v[3]>=0) for v in hierarchy[0])
    fill = float(area/(w*h))
    clipped = sx==0 or sy==0 or sx+w==g.shape[1] or sy+h==g.shape[0]
    return dict(filled=bool(fill>=.55 and counters==0 and not clipped),fill=fill,
                counters=counters,clipped=bool(clipped))


def analyze(gray,items,route='slow'):
    start=perf_counter();data=previous(gray,items,route=route,version=6);retained=[];rejected=[]
    for r in data['rows']:
        witnesses=[dict(point=p,**interior(gray,p,r['height'],route)) for p in r['points']]
        points=[z['point'] for z in witnesses if z['filled']]
        q=dict(r,points=points,interiors=witnesses)
        # Preserve three separate witnessed marks and original leader span.
        if len(points)>=3 and np.ptp(np.array(points)[:,0])>=2*r['height']:retained.append(q)
        else:rejected.append(q)
    accepted={r['item']:r for r in retained};regions=[]
    bounds=np.asarray([bbox(q) for q in items]).reshape(-1,4);yc=bounds[:,1::2].mean(1)
    for reg in data['regions']:
        rr=[accepted[r['item']] for r in reg['rows'] if r['item'] in accepted]
        if len(rr)<3:continue
        boxes=np.array([r['bbox'] for r in rr]);box=[float(boxes[:,0].min()),float(boxes[:,1].min()),float(boxes[:,2].max()),float(boxes[:,3].max())]
        ids=np.flatnonzero((yc>=box[1])&(yc<=box[3])&(bounds[:,0]>=box[0]-data['height'])&(bounds[:,2]<=box[2]+data['height'])).tolist()
        regions.append(dict(reg,bbox=box,cells=ids,rows=rr,source='v6 grouping with filled-interior witnesses'))
    return dict(data,rows=retained,rejected=rejected,regions=regions,
                protected_indices=sorted({i for r in regions for i in r['cells']}),seconds=perf_counter()-start)


def run(action):
    dest=DEST/'round4-table-dots-v7';dest.mkdir(exist_ok=True)
    triggered={f.name.removesuffix('.evidence.json') for f in pointer('active-final4.json').glob('*.evidence.json') if json.loads(f.read_text()).get('table_extents') is not None}
    selected=set(names())|triggered
    for row in manifest()['pages']:
        p=row['page']
        if p not in selected:continue
        g=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
        if p in triggered:items=separators(g,items)['items']
        f=dest/(p+'.json');data=dict(page=p,slow=analyze(g,items)) if action=='slow' else json.loads(f.read_text())
        routes=['slow'] if action=='slow' else ['explicit','heuristic']
        for route in routes:
            if action=='fast':data[route]=analyze(g,items,route)
            im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR);r=data[route]
            for z in r['regions']:
                a,t,b,d=map(round,z['bbox']);cv2.rectangle(im,(a,t),(b,d),(20,145,30),3)
            for z in r['rows']+r['rejected']:
                for w in z['interiors']:
                    x,y=map(round,w['point']);cv2.circle(im,(x,y),max(2,round(z['height']*.15)),(170,20,170) if w['filled'] else (20,20,240),1)
            save_image(dest/(p+'.'+route+'.jpg'),label(im,p+' '+route+' | filled dot purple; rejected interior red; extent green'))
        dump(f,data);print(p,[(r,len(data[r]['rows']),len(data[r]['regions'])) for r in routes],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['slow','fast']);a=p.parse_args();cv2.setNumThreads(1);run(a.action)
