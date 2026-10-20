"""Slow offline referees. Only this module imports the existing page model."""
from pathlib import Path
import json
from time import perf_counter
import cv2
import numpy as np
from PIL import Image,ImageDraw
from ..shared.contracts import bbox
from ..shared.geometry import height_proxy,roi
from ..shared.ink_strokes import measure
from ..shared.ink_photometry import tones
from ..shared.ink_ownership import analyze
from ..shared.timing import dump
from ..round2 import ROOT, get_baseline


def page_image(gray,title,width=1300):
    im=Image.fromarray(gray).convert('RGB');s=min(1.,width/im.width)
    im=im.resize((round(im.width*s),round(im.height*s)))
    out=Image.new('RGB',(im.width,im.height+48),'white');out.paste(im,(0,48))
    ImageDraw.Draw(out).text((8,8),title,fill='black')
    return out,s


def boxes_image(gray,rows,title,key,colors,path):
    im,s=page_image(gray,title);d=ImageDraw.Draw(im)
    for r in rows:
        if r.get('discounted'):continue
        b=r.get('bbox',r.get('box'));v=r.get(key)
        if b is None or v not in colors:continue
        d.rectangle([b[0]*s,b[1]*s+48,b[2]*s,b[3]*s+48],outline=colors[v],width=1)
    im.save(path,quality=90)


def model_reference(row,dest):
    p=row['page'];dest.mkdir(parents=True,exist_ok=True)
    if (dest/(p+'.json')).exists():return
    from greekocr.pages import process_page,PageOptions
    gray=cv2.imread(str(ROOT/row['path']),0);t=perf_counter()
    result=process_page(gray,page_key=p,options=PageOptions(statistics=True))
    rows=result.glyphs
    dump(dest/(p+'.json'),dict(page=p,seconds=perf_counter()-t,glyphs=rows,stats=result.statistics['stats']))
    boxes_image(gray,rows,p+' | existing model: faint cyan; strong green; ownership is a hypothesis',
                'faint',{True:'deepskyblue',False:'green'},dest/(p+'.faintness.jpg'))
    boxes_image(gray,rows,p+' | existing model: orange under / red over / green intact (faint conflated)',
                'coverage_state',{'under_inked':'orange','over_inked':'red','intact':'green'},dest/(p+'.inkiness.jpg'))


def reference(row,dest,version=1):
    """All small-detector lines receive independent full-resolution measurements."""
    dest.mkdir(parents=True,exist_ok=True);p=row['page']
    gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
    height=height_proxy(items,row['image_size']);records=[];t=perf_counter()
    for i,item in enumerate(items):
        rec=measure(gray,bbox(item),height,maps=False);rec['line']=i;records.append(rec)
    own=analyze(gray,items,detail=True)
    dump(dest/(p+'.json'),dict(page=p,version=version,height=height,lines=records,ownership=own,seconds=perf_counter()-t))
    # Separate physical axes in the page view; no claim dark=front or thick=damaged.
    for feature in ('faintness','inkiness'):
        im,s=page_image(gray,p+' | contrast: blue low / red high' if feature=='faintness' else p+' | width: blue thin / orange thick; unknown cause')
        d=ImageDraw.Draw(im)
        for r in records:
            b=r['box'];v=r['contrast'] if feature=='faintness' else r['thresholds'][1]['width_h']
            c=(int(255*min(1,v)),100,int(255*(1-min(1,v)))) if feature=='faintness' else (int(255*min(1,v*4)),100,int(255*(1-min(1,v*4))))
            d.rectangle([b[0]*s,b[1]*s+48,b[2]*s,b[3]*s+48],outline=c,width=2)
            d.text((b[0]*s,b[1]*s+48),f"{r['line']} {v:.2f}",fill=c)
        im.save(dest/(p+'.'+feature+'.jpg'),quality=91)
    boxes_image(gray,own['regions'],p+' | spatial handedness: cyan reflected / green ordinary / amber unknown',
                'ownership',{'front':'green','back':'deepskyblue','unknown':'orange'},dest/(p+'.ownership.jpg'))
    # Original-resolution strips and actual threshold/width/counter support.
    sheets=[]
    for offset in range(0,len(items),12):
        tiles=[]
        for i in range(offset,min(offset+12,len(items))):
            r=measure(gray,bbox(items[i]),height,maps=True)
            raw=r['raw'];w=min(1300,raw.shape[1]);scale=min(1,w/raw.shape[1]);hh=max(1,round(raw.shape[0]*scale))
            tile=Image.new('RGB',(1300,4*hh+38),'white');d=ImageDraw.Draw(tile)
            d.text((5,2),f"line {i}: raw, relative .35/.50/.70; color=distance width; contrast={r['contrast']:.3f}",fill='black')
            tile.paste(Image.fromarray(raw).convert('RGB').resize((w,hh)),(0,30))
            for j,m in enumerate(r['maps']):
                col=cv2.applyColorMap(np.uint8(np.minimum(1,m['distance']*8/height)*255),cv2.COLORMAP_TURBO)[:,:,::-1]
                col[m['binary']==0]=255
                tile.paste(Image.fromarray(col).resize((w,hh)),(0,30+(j+1)*hh))
            tiles.append(tile)
        sheet=Image.new('RGB',(1300,sum(x.height for x in tiles)),'white');y=0
        for im in tiles:sheet.paste(im,(0,y));y+=im.height
        name=f'{p}.strokes-{offset//12:02d}.jpg';sheet.save(dest/name,quality=92);sheets.append(name)
    # Dense local texture map, not an image classifier: orthogonal variation + row-band occupancy.
    image_reference(gray,height,dest,p,version)
    mirror_pairs(gray,own,dest,p)
    return records


def mirror_pairs(gray,own,dest,p):
    tiles=[]
    for i,r in enumerate(own['regions']):
        ws=r.get('witnesses',[])
        if not ws:continue
        tile=Image.new('RGB',(1200,135),'white');d=ImageDraw.Draw(tile)
        d.text((5,3),f"line {i}: {r['ownership']}; query / reflected query / same-page exemplar",fill='black')
        for j,m in enumerate(sorted(ws,key=lambda q:-abs(q['margin']))[:5]):
            x0,y0,x1,y1=roi(m['bbox'],gray.shape);raw=Image.fromarray(gray[y0:y1,x0:x1])
            a,b,c,e=roi(m['exemplar'],gray.shape);ex=Image.fromarray(gray[b:e,a:c])
            for k,im in enumerate((raw,raw.transpose(Image.Transpose.FLIP_LEFT_RIGHT),ex)):
                # Display enlargement only: raw levels above, contrast-stretched
                # below. Faint query strokes otherwise vanish at review scale.
                a=np.asarray(im);lo,hi=np.percentile(a,[2,95])
                norm=Image.fromarray(np.uint8(np.clip((a-lo)*255/max(hi-lo,1),0,255)))
                size=(max(1,round(im.width*min(65/im.width,38/im.height))),max(1,round(im.height*min(65/im.width,38/im.height))))
                tile.paste(im.resize(size),(j*240+k*74,24))
                tile.paste(norm.resize(size),(j*240+k*74,65))
            d.text((j*240,110),f"D={m['direct']:.2f} R={m['reflected']:.2f}",fill='black')
        tiles.append(tile)
    for off in range(0,len(tiles),14):
        group=tiles[off:off+14];out=Image.new('RGB',(1200,sum(x.height for x in group)),'white');y=0
        for tile in group:out.paste(tile,(0,y));y+=tile.height
        out.save(dest/f'{p}.mirrors-{off//14:02d}.jpg',quality=93)


def image_reference(gray,height,dest,p,version):
    s=min(1,1600/max(gray.shape));raw=cv2.resize(gray,None,fx=s,fy=s,interpolation=cv2.INTER_AREA);h=height*s
    im=Image.fromarray(raw).convert('RGB');d=ImageDraw.Draw(im);rows=[]
    step=max(1,round(3*h))
    for y in range(0,raw.shape[0],step):
        for x in range(0,raw.shape[1],step):
            patch=raw[y:y+step,x:x+step].astype(np.float32)
            if min(patch.shape)<2:continue
            ink=(patch<np.percentile(patch,90)-.25*(np.percentile(patch,90)-np.percentile(patch,2)))
            gy,gx=np.gradient(patch);energy=gx*gx+gy*gy
            if energy.mean()<1:continue
            coherence=float(np.hypot((gx*gx-gy*gy).sum(),(2*gx*gy).sum())/max(energy.sum(),1))
            row_occupancy=float(np.mean(ink.any(1)));col_occupancy=float(np.mean(ink.any(0)))
            texture=coherence<.5 and row_occupancy>.95 and col_occupancy>.95
            if texture:d.rectangle((x,y,x+step,y+step),outline='magenta',width=2)
            rows.append(dict(box=[x/s,y/s,min(x+step,raw.shape[1])/s,min(y+step,raw.shape[0])/s],coherence=coherence,row_occupancy=row_occupancy,col_occupancy=col_occupancy,texture=texture))
    out=Image.new('RGB',(im.width,im.height+45),'white');out.paste(im,(0,45))
    ImageDraw.Draw(out).text((5,5),p+' | magenta: dense area texture; NOT an image exclusion mask',fill='black')
    out.save(dest/(p+'.images.jpg'),quality=91);dump(dest/(p+'.images.json'),dict(tiles=rows,version=version))
