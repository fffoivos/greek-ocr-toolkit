"""Inspect large line-level disagreements in the measured physical width."""
import json,cv2,numpy as np
from PIL import Image,ImageDraw
from ..round2 import manifest,ROOT
from ..shared.ink_strokes import measure,heuristic
from .study import DEST


def run():
    cv2.setNumThreads(1);dest=DEST/'stroke-comparisons';dest.mkdir(exist_ok=True)
    rows={r['page']:r for r in manifest()['pages']};records=json.loads((DEST/'route-comparisons.json').read_text())
    for r in records:
        if r['version']=='reference-v2':continue
        p=r['page'];gray=cv2.imread(str(ROOT/rows[p]['path']),0)
        data=json.loads((DEST/r['version']/(p+'.json')).read_text());h=data['ownership']['dense']['height']
        chosen=sorted({max(r['lines'],key=lambda q:abs(q[k+'_error_h']))['line'] for k in ('route1','route2')})
        panels=[]
        for i in chosen:
            line=r['lines'][i];a=measure(gray,line['bbox'],h,maps=True);b=measure(gray,line['bbox'],h,samples=32,maps=True);c=heuristic(gray,line['bbox'],h,maps=True)
            for title,raw in [('raw',a['raw']),('slow .50 support',255-a['maps'][1]['binary']*255),('R1 .50 support',255-b['maps'][1]['binary']*255),('R2 support',255-c['binary']*255)]:
                im=Image.fromarray(raw).convert('RGB');s=min(2,1400/im.width);im=im.resize((round(im.width*s),max(1,round(im.height*s))))
                tile=Image.new('RGB',(1400,im.height+32),'white');tile.paste(im,(0,32));ImageDraw.Draw(tile).text((5,5),f'{p} line{i} {title}; width/body {line["slow_width_h"]:.4f} / {line["route1_width_h"]:.4f} / {line["route2_width_h"]:.4f}',fill='black');panels.append(tile)
        out=Image.new('RGB',(1400,sum(q.height for q in panels)),'white');y=0
        for im in panels:out.paste(im,(0,y));y+=im.height
        out.save(dest/(p+'.jpg'),quality=94)


if __name__=='__main__':run()
