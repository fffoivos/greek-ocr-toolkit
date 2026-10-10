"""Render and compare local recurrence with the reviewed spatial templates."""
import argparse,json,cv2
import numpy as np
from PIL import Image,ImageDraw
from time import perf_counter
from ..round2 import manifest,ROOT
from ..shared.ink_recurrence import render
from ..shared.timing import dump
from .study import DEST


def run(version,dense=False,route='explicit',focus=False):
    cv2.setNumThreads(1);dest=DEST/'round4'/version;dest.mkdir(parents=True,exist_ok=True);records=[];panels=[];by_page={}
    old=json.loads((DEST/'motif-gate-v3/records.json').read_text());by={r['page']:r for r in manifest()['pages']}
    current=None
    for m in old:
        p=m['page'];i=m['line']
        if focus and not (m['accepted'] or p=='an-778126cc8c2b-p000011'):continue
        if current!=p:
            row=by[p];gray=cv2.imread(str(ROOT/row['path']),0);d=json.loads((DEST/'study-v2'/(p+'.evidence.json')).read_text());current=p
        h=d['ownership']['height'];item=d['r2']['items'][i]
        t=perf_counter();v=render(gray,item,h,samples=h if dense else 8,detail=True,route=route);seconds=perf_counter()-t
        rec=dict(page=p,line=i,old_accepted=m['accepted'],old_reduced=m['reduced']['coverage'],best=v['best'],nominate=v['nominate'],seconds=seconds,records=v['records']);records.append(rec)
        rgb=np.repeat(v['raw'][:,:,None],3,2);rgb[v['support']>0]=(np.float32(rgb[v['support']>0])*.5+[0,100,40]).clip(0,255).astype('uint8')
        raw=Image.fromarray(v['raw']).convert('RGB');im=Image.fromarray(rgb);w=min(1400,raw.width*3);hh=round(raw.height*w/raw.width)
        tile=Image.new('RGB',(1400,2*hh+40),'white');tile.paste(raw.resize((w,hh)),(0,40));tile.paste(im.resize((w,hh)),(0,hh+40))
        ImageDraw.Draw(tile).text((5,5),f'{p} L{i} old {m["accepted"]} gate {v["nominate"]} cover{v["best"]["coverage"]:.3f} span{v["best"]["span"]:.3f} {seconds*1000:.2f}ms',fill='black');panels.append(tile);by_page.setdefault(p,[]).append(tile)
        print(p,i,m['accepted'],v['nominate'],round(v['best']['coverage'],3),round(seconds*1000,2),flush=True)
    for off in range(0,len(panels),4):
        group=panels[off:off+4];out=Image.new('RGB',(1400,sum(x.height for x in group)),'white');y=0
        for im in group:out.paste(im,(0,y));y+=im.height
        out.save(dest/f'{off//4:02d}.jpg',quality=94)
    dump(dest/'records.json',records)
    for page,group in by_page.items():
        out=Image.new('RGB',(1400,sum(x.height for x in group)),'white');y=0
        for im in group:out.paste(im,(0,y));y+=im.height
        out.save(dest/(page+'.jpg'),quality=94)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',required=True);ap.add_argument('--dense',action='store_true');ap.add_argument('--focus',action='store_true');ap.add_argument('--route',default='explicit');a=ap.parse_args();run(a.version,a.dense,a.route,a.focus)
