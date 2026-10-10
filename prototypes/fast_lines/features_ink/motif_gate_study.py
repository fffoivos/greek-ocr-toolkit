"""Render rejected whole-lag and reduced spatial witnesses before using a gate."""
import cv2
import json
from PIL import Image,ImageDraw
from ..round2 import manifest,ROOT
from ..shared.ink_motifs import inspect as lag_inspect
from ..shared.ink_motif_gate import inspect
from ..shared.timing import dump
from .study import DEST


def run():
    cv2.setNumThreads(1);dest=DEST/'motif-gate-v3';dest.mkdir(exist_ok=True)
    records=[];panels=[]
    for row in manifest()['pages']:
        p=row['page'];d=json.loads((DEST/'study-v1'/(p+'.evidence.json')).read_text())
        selected=[m for m in d['motifs'] if 'remaining_glyphs' in m]
        if not selected:continue
        gray=cv2.imread(str(ROOT/row['path']),0)
        for m in selected:
            i=m['line'];item=d['r2']['items'][i];h=d['ownership']['height']
            lag,_=lag_inspect(gray,item,h)
            r,raw=inspect(gray,item,h,diagnostic=True,samples=8)
            records.append(dict(page=p,line=i,accepted=m['drop'],lag=lag,reduced=r,full=m))
            im=Image.fromarray(raw).convert('RGB');scale=min(3,1350/im.width)
            im=im.resize((round(im.width*scale),max(1,round(im.height*scale))))
            tile=Image.new('RGB',(1400,im.height+45),'white');tile.paste(im,(0,45));dr=ImageDraw.Draw(tile)
            dr.text((5,5),f'{p} line{i} full accepted={m["drop"]}  lag={lag["repeat"]:.3f} reduced coverage={r["coverage"]:.3f} span={r["span"]:.2f}',fill='black')
            ss=im.width/raw.shape[1]
            for support in r.get('supports',[]):
                _,_,tw,th=support['template']
                for x,y,c in support['matches']:dr.rectangle((x*ss,y*ss+45,(x+tw)*ss,(y+th)*ss+45),outline='magenta')
            panels.append(tile)
    for off in range(0,len(panels),6):
        group=panels[off:off+6];out=Image.new('RGB',(1400,sum(x.height for x in group)),'white');y=0
        for im in group:out.paste(im,(0,y));y+=im.height
        out.save(dest/f'{off//6:02d}.jpg',quality=94)
    dump(dest/'records.json',records)
    for r in records:print(r['page'],r['line'],r['accepted'],round(r['reduced']['coverage'],3),round(r['reduced']['span'],3),flush=True)


if __name__=='__main__':run()
