"""Per-page and per-line route comparisons against native component contacts."""
import json
import cv2
import numpy as np
from ..round2 import manifest
from ..shared.manifest import ROOT
from ..shared.timing import dump
from .reference import DEST,save,line


def run():
    out=DEST/'round4/contact-audit';out.mkdir(parents=True,exist_ok=True);records=[]
    for r in manifest()['pages']:
        p=r['page'];slow=json.loads((DEST/'round4/body-slow-v7'/(p+'.json')).read_text());fast=json.loads((DEST/'round4/body-explicit_fast-v7'/(p+'.json')).read_text())
        im=cv2.imread(str(ROOT/r['path']));rows=[];fm={q['line']:q for q in fast['lines']}
        for q in slow['lines']:
            f=fm[q['line']];a=np.asarray(q['path']);b=np.asarray(f['path']);seen=np.asarray(q['observed']);h=q['height']
            delta=abs(a[:,1]-b[:,1])/h
            for j in range(1,len(a)):
                if seen[j]&seen[j-1]:line(im,a[j-1:j+1],(40,180,20),3)
                if f['observed'][j]&f['observed'][j-1]:line(im,b[j-1:j+1],(180,30,180),1)
            alternatives=[dict(fragment=x['fragment'],agrees=x['agrees']) for x in q['alternatives']]
            other=[dict(fragment=x['fragment'],agrees=x['agrees']) for x in f['alternatives']]
            rows.append(dict(line=q['line'],r1_max_h=float(delta.max()),r1_p90_h=float(np.quantile(delta,.9)),
                             observed_equal=q['observed']==f['observed'],alternatives_equal=alternatives==other))
        r2=[]
        sm={q['line']:q for q in slow['lines']}
        for pair in slow.get('fragment_witness',{}).get('paths',[]):
            q=sm.get(pair['line'])
            if not q:continue
            a=np.asarray(q['path']);b=np.asarray(pair['path']);common=np.asarray(q['observed'])&(a[:,0]>=b[:,0].min())&(a[:,0]<=b[:,0].max());h=q['height']
            error=abs(a[common,1]-np.interp(a[common,0],b[:,0],b[:,1]))/h
            alt=next((x for x in q['alternatives'] if x['fragment']==pair['fragment']),{})
            r2.append(dict(line=pair['line'],fragment=pair['fragment'],p90_h=float(np.quantile(error,.9)) if len(error) else None,
                           native_agrees=alt.get('agrees',False)))
        record=dict(page=p,group=r['group'],lines=rows,route2=r2,components_equal=slow['components']==fast['components'])
        dump(out/(p+'.json'),record);save(out/(p+'.jpg'),im,p+' | slow native green / fast native purple')
        records.append(record)
    dump(out/'summary.json',dict(pages=len(records),lines=sum(len(r['lines']) for r in records),
        component_pages_equal=sum(r['components_equal'] for r in records),
        path_max_h=max(q['r1_max_h'] for r in records for q in r['lines']),
        differing=[dict(page=r['page'],**q) for r in records for q in r['lines'] if q['r1_max_h'] or not q['observed_equal'] or not q['alternatives_equal']],
        route2_pairs=sum(len(r['route2']) for r in records)))

if __name__=='__main__':
    cv2.setNumThreads(1);run()
