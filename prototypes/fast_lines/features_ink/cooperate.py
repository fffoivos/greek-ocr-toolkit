"""Offline consumption of track C's explicit type/pitch hypotheses.

No runtime dependency on another mutable worktree. Source snapshots accompany
the comparison. An uncertain body height is never substituted for our scale.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
import cv2,numpy as np
from PIL import ImageDraw
from ..round2 import manifest,get_baseline,ROOT
from ..shared.ink_ownership import analyze
from ..shared.ink_strokes import measure
from ..shared.contracts import bbox
from ..shared.geometry import height_proxy
from ..shared.timing import dump
from .reference import page_image
from .study import DEST,ANCHORS


def run(tree):
    import prototypes.fast_lines.shared as shared
    path=Path(tree)/'prototypes/fast_lines/shared'
    shared.__path__.append(str(path))
    from ..shared.type_profiles import measure_line
    from ..shared.type_lattice import blocks
    dest=DEST/'cooperation';dest.mkdir(parents=True,exist_ok=True);sources={}
    for name in ('type_profiles.py','type_lattice.py'):
        p=path/name;sources[name]=hashlib.sha256(p.read_bytes()).hexdigest();shutil.copy2(p,dest/name)
    cv2.setNumThreads(1)
    for row in manifest()['pages']:
        if row['page'] not in ANCHORS:continue
        p=row['page'];gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size'])
        records=[];im,s=page_image(gray,p+' | C body contacts: green measured / amber uncertain; numbers width/body')
        d=ImageDraw.Draw(im)
        for i,item in enumerate(items):
            c=measure_line(gray,item,samples=24,version=3)
            size=h if c['uncertain'] else c['xheight']
            m=measure(gray,bbox(item),size,samples=32,levels=(.5,))
            records.append(dict(line=i,type=c,body_source='proxy: C uncertain' if c['uncertain'] else 'C component contacts',ink=m))
            b=bbox(item);color='orange' if c['uncertain'] else 'green'
            d.rectangle([b[0]*s,b[1]*s+48,b[2]*s,b[3]*s+48],outline=color,width=1)
            d.text((b[0]*s,b[1]*s+48),f"{i} {m['thresholds'][0]['width_h']:.2f}",fill=color)
        im.save(dest/(p+'.body-width.jpg'),quality=91)
        own=analyze(gray,items);layers={}
        front=[items[i] for i in own['anchors']]
        back=[items[i] for i in own['suppress_indices']]
        im,s=page_image(gray,p+' | two grids: strong exemplar rows green / mirrored rows cyan; not ownership proof');d=ImageDraw.Draw(im)
        for name,selected,color in [('strong',front,'green'),('mirrored',back,'deepskyblue')]:
            bb=blocks(selected,row['image_size']);layers[name]=bb
            for b in bb:
                for y in b['centres']:
                    xs=np.array([b['x0'],b['x1']]);ys=y+b['slope']*(xs-b['xref'])
                    d.line([(float(x*s),float(v*s+48)) for x,v in zip(xs,ys)],fill=color,width=2)
                d.text((b['x0']*s,b['y0']*s+32),f"{name}: pitch/h {b['pitch']/b['height']:.2f}",fill=color)
        im.save(dest/(p+'.grids.jpg'),quality=91)
        dump(dest/(p+'.json'),dict(page=p,sources=sources,lines=records,layers=layers,
             caveat='Sparse strong anchors can misestimate pitch; a distinct grid does not identify front or back'))
        print('cooperation',p,flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('type_worktree');run(ap.parse_args().type_worktree)
