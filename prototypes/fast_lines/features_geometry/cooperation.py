"""Offline reuse of track C's contact-height component, with an immutable snapshot.

No import or call from the runtime geometry stack. This compares physical scale
measurements; an uncertain body contact is never promoted to a font height.
"""
import importlib.util,json,shutil
from pathlib import Path
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.geometry import roi,height_proxy
from ..shared.contracts import bbox
from ..shared.review import save_image
from ..shared.timing import dump
from .reference import DEST


def run():
    cv2.setNumThreads(1);out=DEST/'cooperation';out.mkdir(parents=True,exist_ok=True)
    original=ROOT.parent/'greek-ocr-toolkit-ff-type/prototypes/fast_lines/shared/type_profiles.py'
    sha=digest(original);snapshot=out/('type_profiles-'+sha[:12]+'.py');shutil.copyfile(original,snapshot)
    spec=importlib.util.spec_from_file_location('prototypes.fast_lines.shared.geometry_type_snapshot',snapshot)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    results=[];tiles=[]
    for r in manifest()['pages']:
        p=r['page'];e=json.loads((DEST/'corrections-v6'/(p+'.evidence.json')).read_text())
        if not e.get('geometry_changes'):continue
        gray=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r);h=height_proxy(items,r['image_size'])
        routes=json.loads((DEST/'routes-v4'/(p+'.json')).read_text());bands={q['line']:q for q in routes['route1']['lines']}
        for c in e['geometry_changes']:
            i=c['line'];a=module.measure_line(gray,items[i],samples=24,version=3)
            results.append(dict(page=p,line=i,type=a,map_height=bands[i]['local_height'],box_proxy=h))
            b=np.asarray(bbox(items[i]));x0,y0,x1,y1=roi(b+[-h,-h,h,h],gray.shape)
            raw=cv2.cvtColor(gray[y0:y1,x0:x1],cv2.COLOR_GRAY2BGR);s=min(1,850/raw.shape[1],200/raw.shape[0]);raw=cv2.resize(raw,None,fx=s,fy=s)
            tile=np.full((250,1250,3),255,np.uint8);tile[35:35+raw.shape[0],:raw.shape[1]]=raw
            cv2.putText(tile,p+f' source {i}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
            labels=[f'box proxy {h:.1f}px',f'DB band {bands[i]["local_height"]:.1f}px',f'C contacts {a["xheight"]:.1f}px',f'C uncertain: {a["uncertain"]}']
            for j,label in enumerate(labels):cv2.putText(tile,label,(870,60+j*30),cv2.FONT_HERSHEY_SIMPLEX,.55,(40,60,60),1)
            tiles.append(tile)
    for k in range(0,len(tiles),8):save_image(out/f'body-scale-{k//8:02d}.jpg',np.vstack(tiles[k:k+8]))
    dump(out/'body-scale.json',dict(source=str(original),sha256=sha,snapshot=snapshot.name,rows=results,
        meaning='Offline component-contact comparison only; no runtime height borrowing or front ownership.'))
    print('C contact comparison',len(results),'uncertain',sum(q['type']['uncertain'] for q in results),flush=True)


if __name__=='__main__':run()
