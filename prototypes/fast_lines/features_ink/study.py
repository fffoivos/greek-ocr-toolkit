"""Reproducible feature studies and bounded warm-session benchmarks."""
import argparse, json, hashlib, html, random, shutil
from pathlib import Path
from time import perf_counter
import cv2
import numpy as np
from PIL import Image, ImageDraw
from ..round2 import manifest,get_baseline,ROOT
from ..shared.contracts import bbox
from ..shared.geometry import height_proxy,roi,mask
from ..shared.ink_ownership import analyze
from ..shared.ink_strokes import measure,heuristic as stroke_heuristic
from ..shared.ink_images import render as image_render,heuristic as image_heuristic
from ..shared.ink_motif_gate import inspect as motif_inspect
from ..shared.ink_stamps import analyze as stamp_analyze
from ..shared.timing import dump
from .reference import page_image,boxes_image,mirror_pairs

DEST=ROOT/'.astra/fast_lines/out/features_ink'
ANCHORS=['s2-0ce9d1025b3f23c7119e-p00001','s2-09f5dfca4af4d74173c6-p00005',
         'an-1be60011c435-p000215','an-1f8e7d022643-p000003','an-1436ae03653f-p000163',
         'an-d6002cf45e4d-p000058','s2-86865c33eef5932c013b-p00005','an-778126cc8c2b-p000010']


def source_key():
    files=sorted(list((ROOT/'prototypes/fast_lines/features_ink').glob('*.py'))+
                 list((ROOT/'prototypes/fast_lines/shared').glob('ink_*.py')))
    h=hashlib.sha256()
    for p in files:h.update(p.name.encode());h.update(p.read_bytes())
    return h.hexdigest()


def colored_support(product,title):
    a=np.repeat(product['raw'][:,:,None],3,axis=2)
    a[product['mask']>0]=(210,20,200)
    im=Image.fromarray(a);im=im.resize((700,round(im.height*700/im.width)));out=Image.new('RGB',(700,im.height+40),'white');out.paste(im,(0,40))
    ImageDraw.Draw(out).text((5,5),title,fill='black');return out


def triptych(ims,path):
    out=Image.new('RGB',(sum(im.width for im in ims),max(im.height for im in ims)),'white');x=0
    for im in ims:out.paste(im,(x,0));x+=im.width
    out.save(path,quality=92)


def second_reference(row,version):
    dest=DEST/version;dest.mkdir(parents=True,exist_ok=True);p=row['page']
    gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size'])
    slow_path=DEST/'reference-v1'/(p+'.json')
    if not slow_path.exists():
        from .reference import reference
        reference(row,DEST/'reference-v1')
    slow=json.loads(slow_path.read_text())
    data=dict(page=p,source_key=source_key(),image_sha256=row['sha256'],lines=[])
    own={route:analyze(gray,items,detail=True,route=route) for route in ('dense','explicit','sampled')}
    data['ownership']=own
    ims=[]
    for route,title in [('dense','dense glyph reference'),('explicit','route 1 explicit glyphs'),('sampled','route 2 sampled glyphs')]:
        q=dest/(p+'.'+route+'.jpg')
        boxes_image(gray,own[route]['regions'],p+' | '+title,'ownership',{'front':'green','back':'deepskyblue','unknown':'orange'},q)
        im=Image.open(q);im.thumbnail((650,1200));ims.append(im.copy())
    triptych(ims,dest/(p+'.faintness.jpg'));mirror_pairs(gray,own['dense'],dest,p)
    for i,item in enumerate(items):
        r=measure(gray,bbox(item),h,samples=32)
        q=stroke_heuristic(gray,bbox(item),h)
        s=slow['lines'][i]
        data['lines'].append(dict(line=i,bbox=bbox(item),slow=s,route1=r,route2=q,
            ownership={k:v['regions'][i]['ownership'] for k,v in own.items()}))
    ims=[]
    for key,title in [('slow','dense original-pixel width'),('route1','route 1 reduced distance width'),('route2','route 2 area/perimeter width')]:
        im,scale=page_image(gray,p+' | '+title,width=650);d=ImageDraw.Draw(im)
        for r in data['lines']:
            v=r[key]['thresholds'][1]['width_h'] if key!='route2' else r[key]['width_h'];b=r['bbox']
            color=(int(255*min(1,v*4)),90,int(255*(1-min(1,v*4))))
            d.rectangle([b[0]*scale,b[1]*scale+48,b[2]*scale,b[3]*scale+48],outline=color,width=1)
            d.text((b[0]*scale,b[1]*scale+48),f"{r['line']} {v:.2f}",fill=color)
        ims.append(im)
    triptych(ims,dest/(p+'.inkiness.jpg'))
    products=[image_render(gray,h,samples=24),image_render(gray,h,samples=8),image_heuristic(gray,h)]
    triptych([colored_support(q,t) for q,t in zip(products,['slow connected area ink','route 1 sampled area ink','route 2 dense tile heuristic'])],dest/(p+'.images.jpg'))
    data['images']=[{k:v for k,v in q.items() if k not in ('raw','mask')} for q in products]
    # Store actual support masks to compare, not bounding-box IoU.
    for q,name in zip(products,('dense','route1','route2')):cv2.imwrite(str(dest/(p+'.images-'+name+'.png')),q['mask']*255)
    data['motifs']=[];panels=[]
    for i,item in enumerate(items):
        # Dense reference is independent of the runtime nomination scout.
        m,raw=motif_inspect(gray,item,h,diagnostic=True)
        fast,_=motif_inspect(gray,item,h)
        data['motifs'].append(dict(line=i,reference=m,route1=fast))
        if m.get('coverage',0)<.35 or raw is None:continue
        a=Image.fromarray(raw).convert('RGB');a=a.resize((min(1500,a.width*2),max(1,round(a.height*min(1500/a.width,2)))))
        tile=Image.new('RGB',(1500,a.height+35),'white');tile.paste(a,(0,35));d=ImageDraw.Draw(tile)
        d.text((5,5),f"line {i}: explicit repeated ink coverage {m['coverage']:.3f}; runtime {fast['reason']}",fill='black')
        ss=a.width/raw.shape[1]
        for support in m.get('supports',[]):
            _,_,tw,th=support['template']
            for x,y,c in support['matches']:d.rectangle((x*ss,y*ss+35,(x+tw)*ss,(y+th)*ss+35),outline='magenta')
        panels.append(tile)
    if panels:
        out=Image.new('RGB',(1500,sum(q.height for q in panels)),'white');y=0
        for q in panels:out.paste(q,(0,y));y+=q.height
        out.save(dest/(p+'.motifs.jpg'),quality=93)
    stamp=stamp_analyze(gray,items);data['stamps']=stamp
    im,ss=page_image(gray,p+' | fitted ring paths; text overlap unresolved');d=ImageDraw.Draw(im)
    for ring in stamp['rings']:
        th=np.linspace(0,2*np.pi,181);angle=np.deg2rad(ring['angle']);a,b=np.array(ring['diameters'])/2
        x=ring['center'][0]+a*np.cos(th)*np.cos(angle)-b*np.sin(th)*np.sin(angle)
        y=ring['center'][1]+a*np.cos(th)*np.sin(angle)+b*np.sin(th)*np.cos(angle)
        d.line([(float(xx*ss),float(yy*ss+48)) for xx,yy in zip(x,y)],fill='magenta',width=2)
    im.save(dest/(p+'.stamps.jpg'),quality=91)
    dump(dest/(p+'.json'),data)
    print('features',version,p,flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['reference']);ap.add_argument('--version',default='reference-v2');ap.add_argument('--pages',nargs='*')
    args=ap.parse_args();cv2.setNumThreads(1)
    wanted=args.pages or ANCHORS
    for row in manifest()['pages']:
        if row['page'] in wanted:second_reference(row,args.version)


if __name__=='__main__':main()
