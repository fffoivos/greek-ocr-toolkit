"""Whole proposed-rule crossing rendering, before enabling the new veto."""
import json
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT
from ..shared.timing import dump
from ..shared.geometry_feature_rules import boundary_ownership
from .reference import DEST,save,line


def run():
    cv2.setNumThreads(1);out=DEST/'rule-ownership-v2';out.mkdir(parents=True,exist_ok=True)
    for r in manifest()['pages']:
        p=r['page'];e=json.loads((DEST/'corrections-v4'/(p+'.evidence.json')).read_text());rules=(e.get('curved') or {}).get('rules',[])
        if not rules:continue
        gray=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r);h=e['witness']['height'];im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR);records=[]
        for rule in rules:
            a=boundary_ownership(gray,items,rule,h);records.append(dict(rule=rule,ownership=a))
            line(im,rule['path'],(30,170,30) if a['accepted'] else (20,30,200),3)
            for q in a['crossings']:
                x0,y0,x1,y1=np.rint(q['bbox']).astype(int);c=(20,30,220) if q['junction'] else (210,130,30)
                cv2.rectangle(im,(x0,y0),(x1,y1),c,1)
                cv2.putText(im,f"{q['line']} w={q.get('width_h',0):.2f}h",(x0,y0),cv2.FONT_HERSHEY_SIMPLEX,.5,c,1)
        dump(out/(p+'.json'),records);save(out/(p+'.jpg'),im,p+' | red glyph junction / blue checked row / green usable rule')
        print(p,[(a['ownership']['accepted'],sum(q['junction'] for q in a['ownership']['crossings'])) for a in records],flush=True)


if __name__=='__main__':run()
