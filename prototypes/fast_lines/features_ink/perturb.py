"""Known interventions: validate physical axes, never label untouched real print."""
import cv2
import numpy as np
from PIL import Image,ImageDraw
from ..round2 import manifest,get_baseline,ROOT
from ..shared.contracts import bbox
from ..shared.geometry import roi,height_proxy
from ..shared.ink_strokes import measure,heuristic
from ..shared.timing import dump
from .study import DEST


def run():
    cv2.setNumThreads(1)
    page='s2-77d1bd63d5babbe0df73-p00001'
    row=next(r for r in manifest()['pages'] if r['page']==page)
    gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size'])
    b=max((bbox(q) for q in items),key=lambda b:b[2]-b[0]);x0,y0,x1,y1=roi(b,gray.shape)
    source=gray[y0:y1,x0:x1];source=source[:,:min(source.shape[1],round(18*h))]
    source=np.pad(source,((round(h),round(h)),(round(h),round(h))),constant_values=250)
    kernel=np.ones((max(1,round(.07*h))|1,)*2,np.uint8)
    faded=np.uint8(250-(250-source.astype(float))*.35)
    thin=cv2.dilate(source,kernel);thick=cv2.erode(source,kernel)
    broken=source.copy();yy=round(broken.shape[0]*.5);broken[yy:yy+max(1,round(.10*h))]=250
    variants=dict(original=source,attenuated=faded,thin=thin,thick=thick,broken=broken,
                  blurred=cv2.GaussianBlur(source,(0,0),.06*h))
    records=[];tiles=[]
    for name,a in variants.items():
        box=[0,0,a.shape[1],a.shape[0]];dense=measure(a,box,h);r1=measure(a,box,h,samples=32);r2=heuristic(a,box,h)
        records.append(dict(name=name,slow=dense,route1=r1,route2=r2))
        im=Image.fromarray(a).convert('RGB');im=im.resize((1300,round(im.height*1300/im.width)))
        tile=Image.new('RGB',(1300,im.height+40),'white');tile.paste(im,(0,40))
        q=dense['thresholds'][1];ImageDraw.Draw(tile).text((6,5),f"{name}: contrast={dense['contrast']:.3f} width/h={q['width_h']:.3f} holes={q['holes']} components={q['components']}",fill='black');tiles.append(tile)
    out=Image.new('RGB',(1300,sum(t.height for t in tiles)),'white');y=0
    for tile in tiles:out.paste(tile,(0,y));y+=tile.height
    dest=DEST/'perturbations';dest.mkdir(parents=True,exist_ok=True);out.save(dest/'axes.jpg',quality=95)
    dump(dest/'axes.json',dict(page=page,source_box=b,height=h,variants=records,
         note='Known transformations of one real crop; not evidence of damage or unreadability on any untouched page'))
    return records


if __name__=='__main__':run()
