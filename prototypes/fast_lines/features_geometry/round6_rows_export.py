"""Fresh public Stack replay; exact parent/exclusion ledger and OCR crops."""
import argparse,json,platform
import cv2,numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from .round6_rows import DEST,BASE,ROOT,cohort,inputs
from .round5_benchmark import render
from ..stack import Stack
from ..evidence.__main__ import signature
from ..shared.timing import dump
from ..shared.review import detector_record
from ..shared.geometry import roi
from ..shared.geometry_bands import crop_mask


def conservation(old,new,changes):
    changed={c['line']:c for c in changes};position=0;checks=0;area=0.
    for i,q in enumerate(old):
        if i not in changed:
            assert q==new[position],('unchanged',i);position+=1;checks+=1;continue
        c=changed[i];children=new[position:position+len(c['new'])];position+=len(children)
        shape=Polygon(q['polygon']);joined=unary_union([Polygon(v['polygon']) for v in children])
        delta=shape.symmetric_difference(joined).area;area=max(area,delta)
        assert delta<1e-6,(i,delta)
        assert sum(Polygon(v['polygon']).area for v in children)-joined.area<1e-6
        for child in children:
            assert child.get('source_ids')==q.get('source_ids') and child['score']==q['score']
            assert child['row_parent_polygon']==q['polygon']
            assert child['baseline'] is None and 'centreline' not in child
            checks+=4
    assert position==len(new)
    return dict(checks=checks,max_vector_difference=area)


def ocr_crop(gray,old,children,path,title):
    p=np.asarray(old['polygon']);pad=4
    a,b,c,d=roi([*list(p.min(0)-pad),*list(p.max(0)+pad)],gray.shape)
    panels=[]
    for k,q in enumerate([old]+children):
        g=gray[b:d,a:c].copy();mask=np.zeros(g.shape,np.uint8)
        poly=np.rint(np.asarray(q['polygon'])-[a,b]).astype(int);mask=crop_mask(g.shape,q,[a,b]);g[mask==0]=255
        im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR);cv2.polylines(im,[poly],True,(160,160,160) if k==0 else (180,0,180),1)
        scale=min(1.,1300/im.shape[1]);im=cv2.resize(im,None,fx=scale,fy=scale)
        bar=np.full((25,max(900,im.shape[1]),3),255,np.uint8);cv2.putText(bar,title+(' BEFORE' if k==0 else f' child {k}'),(4,17),0,.4,(0,0,0),1)
        canvas=np.full((im.shape[0],bar.shape[1],3),255,np.uint8);canvas[:,:im.shape[1]]=im;panels.extend([bar,canvas])
    cv2.imwrite(str(path),np.vstack(panels))


def run(version,repeat):
    out=DEST/version;out.mkdir(parents=True,exist_ok=True);key,files=signature()
    dump(out/f'source-r{repeat}.json',dict(key=key,files=files,platform=platform.platform()))
    rows=cohort();rows=rows if repeat%2 else rows[::-1];stack=Stack()
    stack.detector.infer(cv2.imread(str(ROOT/rows[0]['path']),0))
    for row in rows:
        p=row['page'];receipt=out/f'{p}.r{repeat}.json'
        if receipt.exists():raise RuntimeError('Existing receipt '+p)
        r=stack(ROOT/row['path'],parked=row['parked']);gray,old=inputs(row)
        old_e=json.load(open(BASE/(p+'.evidence.json')))
        assert r.get('removed',[])==old_e.get('removed',[]),(p,'A exclusions')
        assert r['original']==old_e['original'],(p,'Paddle')
        assert all(r['counts'][k]==v for k,v in old_e['counts'].items()),(p,'retained operators')
        check=conservation(old,r['items'],r.get('rows',{}).get('changes',[]))
        record=detector_record(row,r['items'],r['timing']['total_s']);target=out/(p+'.json')
        if target.exists():assert json.load(open(target))['items']==record['items'],(p,'fresh identity')
        else:
            dump(target,record);dump(out/(p+'.evidence.json'),{k:v for k,v in r.items() if k!='items'})
            dump(out/(p+'.order.json'),render(gray,r,out/(p+'.jpg')))
            for change in r.get('rows',{}).get('changes',[]):
                i=change['line'];children=[q for q in r['items'] if q.get('row_parent_index')==i and q.get('row_partition')]
                ocr_crop(gray,old[i],children,out/f'{p}.split-{i}.jpg',f'{p} A item {i}')
        dump(receipt,dict(page=p,group=row['group'],direction=row['direction'],image_sha256=row['sha256'],source=key,
                         counts=r['counts'],stages=r['stages'],validation=check,**r['timing']))
        print(p,r['counts'].get('rows',0),round(r['stages'].get('rows_s',0)*1000,3),round(r['timing']['correction_s']*1000,3),flush=True)
    assert signature()[0]==key,'Sources changed during run'


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('version');p.add_argument('--repeat',type=int,default=1);a=p.parse_args();run(a.version,a.repeat)
