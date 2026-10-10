"""S6: one discount-safe renderer, JSON writer and local static gallery."""
from pathlib import Path
import html,json
import cv2,numpy as np
from .timing import dump
from .geometry import roi

COLORS={'result':(35,145,20),'reference':(210,150,0),'request':(0,155,235),'guide':(200,40,170)}

def overlay(gray,items=(),paths=(),regions=(),title='',width=1100):
    scale=min(1.,width/gray.shape[1]); base=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    base=cv2.cvtColor(base,cv2.COLOR_GRAY2BGR) if base.ndim==2 else base
    base=cv2.addWeighted(base,.55,np.full_like(base,255),.45,0)
    for item in items:
        if item.get('discounted'): continue
        p=np.rint(np.asarray(item['polygon'])*scale).astype(np.int32)
        cv2.polylines(base,[p],True,COLORS['result'],1,cv2.LINE_AA)
    for path in paths:
        if isinstance(path,dict):
            if path.get('discounted'): continue
            path=path['points']
        if len(path)>1: cv2.polylines(base,[np.rint(np.asarray(path)*scale).astype(np.int32)],False,COLORS['reference'],1,cv2.LINE_AA)
    for region in regions:
        if region.get('discounted'): continue
        x0,y0,x1,y1=np.rint(np.asarray(region['bbox'])*scale).astype(int)
        cv2.rectangle(base,(x0,y0),(x1,y1),COLORS['request'],1)
    bar=np.full((38,base.shape[1],3),255,np.uint8)
    cv2.putText(bar,title[:145],(8,25),cv2.FONT_HERSHEY_SIMPLEX,.46,(30,30,30),1,cv2.LINE_AA)
    return np.vstack([bar,base])

def save_image(path,array):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if not cv2.imwrite(str(path),array,[cv2.IMWRITE_JPEG_QUALITY,85]): raise IOError(path)

def detector_record(row,items,seconds):
    """One export boundary for main, variant and offline comparator lines."""
    items=[q for q in items if not q.get('discounted')]
    w,h=row['image_size']
    clipped=[]
    for q in items:
        p=np.array(q['polygon'],dtype=float,copy=True); p[:,0]=np.clip(p[:,0],0,w); p[:,1]=np.clip(p[:,1],0,h)
        q=dict(q,polygon=p.tolist())
        clipped.append(q)
    return dict(page=row['page'],image_size=row['image_size'],seconds=seconds,unit='line',items=clipped)

def write_result(directory,row,gray,data,seconds,reference=None):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True); page=row['page']
    record=detector_record(row,data['items'],seconds); items=record['items']
    dump(directory/f'{page}.json',record)
    evidence={k:v for k,v in data.items() if k!='items'}
    evidence.update(page=page,group=row['group'],reference=reference,seconds=seconds)
    dump(directory/f'{page}.evidence.json',evidence)
    paths=[q['centreline'] for q in items if q.get('centreline')]
    save_image(directory/f'{page}_6_result.jpg',overlay(gray,items,paths,title=f'{page} | {directory.name} | retained result | {seconds*1000:.2f} ms'))
    save_image(directory/f'{page}_4_evidence.jpg',overlay(gray,paths=data.get('paths',[]),regions=data.get('regions',data.get('requests',[])),title=f'{page} | {directory.name} | cyan support, amber unknown requests'))

def atlas(cells,path,columns=4,cell_width=280):
    thumbs=[]
    for label,im in cells:
        if im is None: continue
        if im.ndim==2: im=cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
        target_h=390; scale=min(cell_width/im.shape[1],(target_h-40)/im.shape[0]); small=cv2.resize(im,None,fx=scale,fy=scale)
        tile=np.full((target_h,cell_width,3),255,np.uint8); tile[35:35+small.shape[0],:small.shape[1]]=small
        cv2.putText(tile,label[:40],(4,18),cv2.FONT_HERSHEY_SIMPLEX,.34,(0,0,0),1)
        thumbs.append(tile)
    while len(thumbs)%columns: thumbs.append(np.full_like(thumbs[0],255))
    if thumbs: save_image(path,np.vstack([np.hstack(thumbs[i:i+columns]) for i in range(0,len(thumbs),columns)]))

def gallery(directory,rows,title):
    directory=Path(directory); parts=['<!doctype html><meta charset="utf-8"><title>'+html.escape(title)+'</title>',
       '<style>body{font:16px system-ui;margin:24px;background:#faf8f4}article{display:inline-block;width:320px;vertical-align:top;margin:8px}img{width:100%}a{color:#154e75}</style>',f'<h1>{html.escape(title)}</h1>',
       '<p>Green retained results; cyan measured support; amber uncertain requests. Centre paths are not baselines. Old model is a hypothesis. Full-page JSON coordinates are pixels. Click images to enlarge.</p>']
    for r in rows:
        p=r['page']; image=f'{p}_6_result.jpg'
        parts.append(f'<article><b>{html.escape(p)}</b><p>{html.escape(r["group"])}</p><a href="{image}"><img loading="lazy" src="{image}"></a><a href="{p}_4_evidence.jpg">Evidence</a> · <a href="{p}.json">Lines</a> · <a href="{p}.evidence.json">Ledger</a> · <a href="../shared/references/{p}.html">Reference</a></article>')
    (directory/'index.html').write_text('\n'.join(parts))
