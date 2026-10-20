"""Bind published line crops by exact native pixels, then run read-only G1b."""
from __future__ import annotations
import cv2,json,sys,math
import numpy as np
from PIL import Image
from concurrent.futures import ProcessPoolExecutor,as_completed
from pilotlib import *
sys.path.insert(0,str(ROOT))
import greekocr
GEO=ROOT.parent/'greek-ocr-toolkit-sol-labelfix/greekocr';greekocr.__path__.append(str(GEO))
from greekocr.labelfix.geometry.io import cache_page
from greekocr.labelfix.geometry.ownership import prepare_row,ownership
from greekocr.labelfix.geometry.magnitude import measure,measured_owner,page_ratios,decision
from prepare_detector import detector_identity
from classify import inspect
ALGORITHM='exact-native-crop-v3-axis-scales'

def one(path):
    item=path.parents[1].name;page_name=path.stem;ident='ajax--'+page_name
    result_file=BASE/'receipts/ajax-geometry'/(ident+'.json');out=BASE/'bulk/ajax-geometry'/(ident+'.jsonl')
    if result_file.exists() and out.exists() and json.loads(result_file.read_text()).get('algorithm')==ALGORITHM:return ident,'cached'
    with Image.open(path) as image:
        original=np.asarray(image.convert('L'));native_size=list(image.size);image=image.convert('L');image.thumbnail((LONG_SIDE,LONG_SIDE),Image.Resampling.LANCZOS)
        scale=image.width/native_size[0];scale_y=image.height/native_size[1];page=BASE/'bulk/pages'/(ident+'.png');page.parent.mkdir(parents=True,exist_ok=True);image.save(page,compress_level=3)
    manifest=dict(id=ident,pilot='ajax',item=item,page=int(page_name.rsplit('_',1)[1]),image=str(page.relative_to(BASE)),image_sha256=sha(page),width=image.width,height=image.height,native_size=native_size,source_page_path=str(path.relative_to(BASE)),source_page_sha256=sha(path),long_side_cap=LONG_SIDE,google_read=False)
    write(BASE/'receipts/pages'/(ident+'.json'),manifest)
    data,ink,labels,receipt=cache_page(page,BASE/'cache/g1b'/ident,sha(page),detector_identity());det=[]
    for r in data['rows']:
        try:det.append(prepare_row(r,ink,labels))
        except ValueError:pass
    results=[]
    for gt in sorted((path.parents[1]/'GT-pairs').glob(page_name+'_*.gt.txt')):
        crop=gt.with_suffix('').with_suffix('.png');c=np.asarray(Image.open(crop).convert('L'));match=cv2.matchTemplate(original,c,cv2.TM_SQDIFF_NORMED);minimum,_,location,_=cv2.minMaxLoc(match)
        # Only an exact pixel match establishes original line coordinates.
        if minimum>1e-6:
            results.append(dict(id=gt.stem,page_id=ident,pilot='ajax',binding='unresolved_pixel_match',minimum_error=minimum,geometry_positive=None));continue
        yy,xx=np.where(match<=max(1e-6,minimum+1e-8));exact=[]
        if len(xx)<=20:
            for tx,ty in zip(xx,yy):
                if np.array_equal(original[ty:ty+c.shape[0],tx:tx+c.shape[1]],c):exact.append((int(tx),int(ty)))
        if len(exact)!=1:
            results.append(dict(id=gt.stem,page_id=ident,pilot='ajax',binding='unresolved_or_ambiguous_exact_pixels',minimum_error=minimum,geometry_positive=None));continue
        x,y=exact[0];native_bbox=[x,y,x+c.shape[1],y+c.shape[0]]
        bbox=[native_bbox[0]*scale,native_bbox[1]*scale_y,native_bbox[2]*scale,native_bbox[3]*scale_y];cb=[math.floor(bbox[0]),math.floor(bbox[1]),math.ceil(bbox[2]),math.ceil(bbox[3])]
        info=inspect(gt.read_text(),human_gt=True);old=dict(old_label=info['text'],bbox=bbox,crop_bbox=cb,**ownership(bbox,det))
        owner,failure=measured_owner(old,det);feat=dict(**measure(old,owner,det),measurement_failure=failure)
        results.append(dict(id=gt.stem.removesuffix('.gt'),page_id=ident,pilot='ajax',item=item,binding='exact_native_crop_pixels',minimum_error=minimum,native_bbox=native_bbox,bbox=bbox,crop_bbox=cb,scale=scale,scale_y=scale_y,source_gt_crop=str(crop.relative_to(BASE)),source_gt_crop_sha256=sha(crop),**info,**feat))
    page_ratios([r for r in results if r.get('binding')=='exact_native_crop_pixels']);thresholds=json.loads((GEO/'labelfix/geometry/thresholds.json').read_text())
    for r in results:
        if r.get('binding')=='exact_native_crop_pixels':r.update(decision(r,thresholds));r['usable_candidate']=r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in results))
    summary=dict(page_id=ident,pilot='ajax',algorithm=ALGORITHM,lines=len(results),bound=sum(r['binding']=='exact_native_crop_pixels' for r in results),unbound=sum(r['binding']!='exact_native_crop_pixels' for r in results),geometry_positive=sum(r['geometry_positive'] is True for r in results),geometry_negative=sum(r['geometry_positive'] is False for r in results),geometry_unresolved=sum(r['geometry_positive'] is None for r in results),usable_candidate=sum(r.get('usable_candidate',False) for r in results),lines_sha256=sha(out),detector_rows=len(det),google_reads=0)
    write(result_file,summary);return ident,len(results)

if __name__=='__main__':
    paths=sorted((BASE/'bulk/ajax/data').glob('*/imgs/*.png'))
    with ProcessPoolExecutor(max_workers=2) as pool:
        for f in as_completed([pool.submit(one,p) for p in paths]):print(*f.result(),flush=True)
