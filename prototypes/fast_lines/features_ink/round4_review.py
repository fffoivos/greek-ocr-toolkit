"""Inspect per-component fast-route disagreements; repeat full diagnostic costs."""
import cv2,json
import numpy as np
from PIL import Image,ImageDraw
from time import perf_counter
from ..round2 import manifest,ROOT,get_baseline
from ..shared.ink_type_identity import extract,sample
from ..shared.ink_observability import measure
from ..shared.timing import dump
from .study import DEST


def run():
    cv2.setNumThreads(1);src=DEST/'round4/observability-v4';dest=DEST/'round4/observability-review';dest.mkdir(exist_ok=True);summary=[];timings=[]
    for row in manifest()['pages']:
        p=row['page'];f=src/(p+'.json')
        if not f.exists():continue
        d=json.loads(f.read_text());gray=cv2.imread(str(ROOT/row['path']),0);records=d['records'];routes=('slow','explicit','heuristic')
        def error(r):
            a=r['slow'];b=r['heuristic'];c=r['explicit']
            return 3*(a['topology_stable']!=c['topology_stable'])+2*(a['topology_stable']!=b['topology_stable'])+abs(a['thresholds'][1]['width_h']-b['thresholds'][0]['width_h'])
        chosen=sorted(records,key=error,reverse=True)[:8];panels=[]
        for r in chosen:
            tile=Image.new('RGB',(1400,200),'white');dr=ImageDraw.Draw(tile);dr.text((5,5),p+f' component{r["glyph"]} owners{r["owners"]}',fill='black')
            for j,route in enumerate(routes):
                v=measure(gray,r['bbox'],r['bbox'][3]-r['bbox'][1],route=route,detail=True);x=j*460
                dr.text((x+5,25),f'{route} noise-topology stable{v["topology_stable"]} SNR{v["core_snr"]:.1f}',fill='black')
                imgs=[v['raw']]+[255-b*255 for b in v['masks']]
                for k,a in enumerate(imgs):
                    im=Image.fromarray(a).convert('RGB');s=min(3,95/im.width,140/im.height);im=im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))));tile.paste(im,(x+5+k*110,55))
            panels.append(tile)
        out=Image.new('RGB',(1400,200*len(panels)),'white')
        for j,im in enumerate(panels):out.paste(im,(0,200*j))
        out.save(dest/(p+'.jpg'),quality=94)
        entry=dict(page=p,components=len(records),selected=[r['glyph'] for r in chosen],differences={})
        for route in routes[1:]:
            entry['differences'][route]=dict(topology=[r['glyph'] for r in records if r['slow']['topology_stable']!=r[route]['topology_stable']],faintness=[r['glyph'] for r in records if r['slow']['faintness']!=r[route]['faintness']])
        summary.append(entry)
        for repeat in (1,2):
            # Each route pays extraction and sampling afresh, not just the
            # conveniently pre-localized measurements shown in comparison JSON.
            for route in routes:
                t=perf_counter();atlas,_=extract(gray,get_baseline(row),version=2);glyphs=sample(atlas,per_line=4)
                values=[measure(gray,g['bbox'],g['height'],route=route) for g in glyphs]
                timings.append(dict(page=p,repeat=repeat,route=route,seconds=perf_counter()-t,components=len(values)))
        print(p,'rendered metric disagreements; diagnostic repeats done',flush=True)
    dump(dest/'differences.json',summary);dump(dest/'timings.json',timings)


if __name__=='__main__':run()
