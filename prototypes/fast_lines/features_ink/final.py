"""Frozen study, review export and fresh timings. Input pages are Q8's allowlist."""
import argparse,json,random,platform,hashlib
from pathlib import Path
from time import perf_counter
import cv2
import numpy as np
from PIL import Image,ImageDraw
from ..round2 import manifest,get_baseline,ROOT
from ..shared.contracts import bbox
from ..shared.geometry import mask,height_proxy,roi
from ..shared.detector import Detector,postprocess
from ..shared.timing import dump
from .pipeline import run
from .study import DEST,source_key
from .reference import boxes_image


def directional(gray,old,new,title,changes=()):
    s=min(1.,1300/max(gray.shape));raw=cv2.resize(gray,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    h=height_proxy(old,(gray.shape[1],gray.shape[0]))*s;k=max(1,round(2*h))|1
    paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8)).astype(float)
    ink=(paper-raw)>max(3,.06*np.percentile(paper,90))
    a=mask(old,raw.shape,(gray.shape[1],gray.shape[0]))>0;b=mask(new,raw.shape,(gray.shape[1],gray.shape[0]))>0
    rgb=np.repeat(raw[:,:,None],3,axis=2);rgb[ink&a&~b]=(225,35,35);rgb[ink&b&~a]=(0,180,50)
    im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
    # Removed lines have no outline. Old/new separator geometry uses grey/green.
    for change in changes:
        pts=[tuple(v*s for v in p) for p in change['old']]
        d.line(pts+[pts[0]],fill=(135,135,135),width=2)
    for q in new:
        if q.get('discounted'):continue
        pts=[tuple(v*s for v in p) for p in q['polygon']]
        color=(0,165,45) if q.get('provenance')=='verified separator clip' else (100,125,145)
        d.line(pts+[pts[0]],fill=color,width=1)
    out=Image.new('RGB',(im.width,im.height+44),'white');out.paste(im,(0,44));ImageDraw.Draw(out).text((5,5),title,fill='black')
    return out


def removal_crops(gray,data,p,dest):
    panels=[];items=data['r2']['items']
    for i in data['removed']:
        b=np.array(bbox(items[i]));h=height_proxy(items,(gray.shape[1],gray.shape[0]));b+=np.array([-.2*h,-.3*h,.2*h,.3*h]);x0,y0,x1,y1=roi(b,gray.shape)
        raw=gray[y0:y1,x0:x1];w=min(1400,raw.shape[1]);hh=max(1,round(raw.shape[0]*w/raw.shape[1]));a=Image.fromarray(raw).convert('RGB').resize((w,hh))
        lo,hi=np.percentile(raw,[2,95]);enh=np.uint8(np.clip((raw.astype(float)-lo)*255/max(hi-lo,1),0,255))
        en=Image.fromarray(enh).convert('RGB').resize((w,hh))
        tile=Image.new('RGB',(1400,2*hh+32),'white');tile.paste(a,(0,32));tile.paste(en,(0,32+hh))
        reason=data['ownership']['regions'][i]['reason'] if data['ownership']['regions'][i]['ownership']=='back' else 'repeated motif'
        ImageDraw.Draw(tile).text((5,5),f'{p} R2 line {i}: {reason}; raw / display stretch',fill='black');panels.append(tile)
    names=[]
    for off in range(0,len(panels),6):
        group=panels[off:off+6];out=Image.new('RGB',(1400,sum(q.height for q in group)),'white');y=0
        for im in group:out.paste(im,(0,y));y+=im.height
        name=f'{p}.removed-{off//6:02d}.jpg';out.save(dest/name,quality=94);names.append(name)
    return names


def study(rows,version):
    dest=DEST/version;dest.mkdir(parents=True,exist_ok=True)
    for row in rows:
        p=row['page'];gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
        if row['parked']:
            data=dict(items=items,removed=[],r2=dict(items=items,changes=[]),ownership=dict(regions=[]),motifs=[],added_s=0.,ink_s=0.)
        else:data=run(gray,items,detail=True)
        data.update(page=p,image_sha256=row['sha256'],source_key=source_key(),group=row['group'])
        data['review_crops']=removal_crops(gray,data,p,dest)
        dump(dest/(p+'.evidence.json'),data)
        dump(dest/(p+'.json'),dict(page=p,image_size=row['image_size'],seconds=0.,unit='line',items=[{k:q.get(k) for k in ('polygon','baseline','score')} for q in data['items']],timing_status='diagnostic; final benchmark supplies seconds'))
        directional(gray,items,data['items'],p+' | green added ink / red removed ink / grey old geometry',data['r2']['changes']).save(dest/(p+'.jpg'),quality=91)
        boxes_image(gray,data['ownership']['regions'],p+' | ordinary / reflected / unknown evidence',
                    'ownership',{'front':'green','back':'deepskyblue','unknown':'orange'},dest/(p+'.faintness.jpg'))
        if data['removed']:print(p,'removed',data['removed'],'extra_ms',round(data['added_s']*1000,2),flush=True)
    gallery(version)


def gallery(version):
    dest=DEST/version;rows=[];sheets=[]
    for row in manifest()['pages']:
        p=row['page'];path=dest/(p+'.evidence.json')
        if not path.exists():continue
        d=json.loads(path.read_text());rows.append((row,d));sheets.append((p,dest/(p+'.jpg')))
    contacts=dest/'sheets';contacts.mkdir(exist_ok=True)
    for off in range(0,len(sheets),6):
        out=Image.new('RGB',(1800,1800),'white')
        for j,(name,path) in enumerate(sheets[off:off+6]):
            im=Image.open(path);im.thumbnail((600,900));out.paste(im,((j%3)*600,(j//3)*900))
        out.save(contacts/f'{off//6:02d}.jpg',quality=91)
    links=[]
    for row,d in rows:
        p=row['page'];links.append(f'<tr><td>{p}</td><td>{row["direction"]}</td><td>{len(d["removed"])}</td><td><a href="{p}.jpg">correction</a> · <a href="{p}.faintness.jpg">ownership</a> · <a href="{p}.json">detector JSON</a> · <a href="{p}.evidence.json">evidence</a> '+''.join(f'<a href="{x}">crop {i}</a> ' for i,x in enumerate(d['review_crops']))+'</td></tr>')
    (dest/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Feature B</title><style>body{font:16px system-ui;max-width:1600px;margin:30px auto}td{padding:6px;border-bottom:1px solid #ddd}</style><h1>Faintness, inkiness, images</h1><p>Final stack versus original Paddle. Red: removed ink; green: newly covered ink. Separator clips: old boundary grey, new green. Removed boxes are not drawn. Direction means coverage, not correctness.</p><table>'+''.join(links)+'</table>')
    dump(dest/'summary.json',dict(source_key=source_key(),pages=len(rows),removed=sum(len(d['removed']) for _,d in rows),
        changed_pages=[r['page'] for r,d in rows if d['removed']],
        agreement_changes=[r['page'] for r,d in rows if r['group']=='agreement' and d['items']!=get_baseline(r)]))


def benchmark(rows,version,repeat):
    dest=DEST/version;f=dest/f'benchmark-{repeat}-{rows[0]["page"]}.json'
    if f.exists():raise RuntimeError('This declared benchmark batch already exists')
    model=Detector();warm=cv2.imread(str(ROOT/rows[0]['path']),0);model.infer(warm)
    order=list(rows);random.Random(3100+repeat).shuffle(order);records=[]
    for row in order:
        t=perf_counter();gray=cv2.imread(str(ROOT/row['path']),0);decode=perf_counter()-t
        t=perf_counter();pm,meta=model.infer(gray);items=postprocess(pm,row['image_size']);base=perf_counter()-t
        t=perf_counter()
        if row['parked']:data=dict(items=items,added_s=0.,ink_s=0.,scout_s=0.,refinement_s=0.,r2=dict(added_s=0.,correction_s=0.))
        else:data=run(gray,items)
        added=perf_counter()-t
        expected=json.loads((dest/(row['page']+'.evidence.json')).read_text())
        assert items==get_baseline(row),(row['page'],'baseline drift')
        assert data['items']==expected['items'],(row['page'],'output drift')
        records.append(dict(page=row['page'],group=row['group'],direction=row['direction'],repeat=repeat,
            decode_s=decode,baseline_s=base,added_s=added,ink_s=data['ink_s'],r2_s=data['r2']['added_s'],
            ink_scout_s=data['scout_s'],ink_refinement_s=data['refinement_s'],
            correction_s=data['refinement_s']+data['r2']['correction_s'],total_s=base+added,wall_s=decode+base+added,parked=row['parked']))
    dump(f,dict(source_key=source_key(),environment=platform.platform(),startup_s=model.startup_s,rows=records))
    print('benchmark',repeat,len(rows),'done',flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['study','benchmark','gallery']);ap.add_argument('--version',default='study-v1');ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=195);ap.add_argument('--repeat',type=int,default=0);ap.add_argument('--agreement',action='store_true')
    args=ap.parse_args();cv2.setNumThreads(1);rows=manifest()['pages']
    if args.agreement:rows=[r for r in rows if r['group']=='agreement']
    rows=rows[args.start:args.start+args.count]
    if args.command=='study':study(rows,args.version)
    elif args.command=='benchmark':benchmark(rows,args.version,args.repeat)
    else:gallery(args.version)


if __name__=='__main__':main()
