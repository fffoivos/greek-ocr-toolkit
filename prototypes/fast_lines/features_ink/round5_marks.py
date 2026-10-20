"""Owner-marked stains/blobs and nearby physical glyph controls, three routes.

Page names select offline evidence only. This module is never imported by Stack.
"""
import argparse,cv2,numpy as np
from PIL import Image,ImageDraw
from ..round2 import ROOT,manifest,get_baseline
from ..shared.contracts import bbox
from ..shared.geometry import height_proxy
from ..shared.ink_photometry import glyphs
from ..shared.ink_observability import measure
from ..shared.timing import dump
from .round5_study import DEST

SELECT={'s2-922e617957fca8dfafd0-p00001':(14,13),
        'an-ffccc97c07de-p000152':(0,1),
        'an-1be60011c435-p000215':(8,10),
        'an-ef481610a820-p000150':(30,31)}


def run(version):
    out=DEST/version;out.mkdir(exist_ok=True);cv2.setNumThreads(1)
    for row in manifest()['pages']:
        p=row['page']
        if p not in SELECT:continue
        target=out/(p+'.json')
        if target.exists():raise RuntimeError('Existing experiment '+p)
        g=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size']);mark,control=SELECT[p]
        samples=[dict(bbox=bbox(items[mark]),label='owner region (not a character)',height=h)]
        samples += [dict(bbox=q['bbox'],label='nearby physical component',height=q['height']) for q in glyphs(g,bbox(items[control]),h,limit=8)]
        records=[];panels=[]
        for i,q in enumerate(samples):
            values={r:measure(g,q['bbox'],q['height'],route=r,detail=True) for r in ('slow','explicit','heuristic')}
            panel=Image.new('RGB',(1500,260),'white');dr=ImageDraw.Draw(panel);dr.text((5,5),f'{p} | {i} {q["label"]} | semantic readability / cause: UNKNOWN',fill='black')
            for j,(route,v) in enumerate(values.items()):
                x=j*500;dr.text((x+5,25),f'{route} contrast {v["contrast"]:.3f} SNR {v["core_snr"]:.1f} noise {v["noise_dn"]:.2f}',fill='black')
                ims=[v['raw']]+[255-m*255 for m in v['masks']]
                for k,a in enumerate(ims):
                    im=Image.fromarray(a).convert('RGB');im.thumbnail((115,170));fac=min(4,115/im.width,170/im.height);im=im.resize((max(1,round(im.width*fac)),max(1,round(im.height*fac))))
                    panel.paste(im,(x+5+120*k,55))
                dr.text((x+5,230),' '.join(f'w={z["width_h"]:.2f} holes={z["holes"]}' for z in v['thresholds']),fill='black')
                values[route]={k:v for k,v in v.items() if k not in ('raw','masks','certain','possible')}
            records.append(dict(sample=q,routes=values));panels.append(panel)
        for off in range(0,len(panels),3):
            im=Image.new('RGB',(1500,260*len(panels[off:off+3])),'white')
            for j,panel in enumerate(panels[off:off+3]):im.paste(panel,(0,j*260))
            im.save(out/f'{p}.marks-{off//3:02d}.jpg')
        dump(target,dict(page=p,height=h,records=records));print(p,len(records),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('version');run(ap.parse_args().version)
