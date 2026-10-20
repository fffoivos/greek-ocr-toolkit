"""Replay G1b from already exact-bound GT boxes using actual X/Y raster scales."""
from ajax_geometry import *
from concurrent.futures import ProcessPoolExecutor,as_completed

def reframe(path):
    rs=rows(path);ident=path.stem;page=json.loads((BASE/'receipts/pages'/(ident+'.json')).read_text())
    sx=page['width']/page['native_size'][0];sy=page['height']/page['native_size'][1]
    data,ink,labels,_=cache_page(BASE/page['image'],BASE/'cache/g1b'/ident,page['image_sha256'],detector_identity());det=[]
    for r in data['rows']:
        try:det.append(prepare_row(r,ink,labels))
        except ValueError:pass
    for r in rs:
        if 'native_bbox' not in r:continue
        b=r['native_bbox'];bbox=[b[0]*sx,b[1]*sy,b[2]*sx,b[3]*sy];cb=[math.floor(bbox[0]),math.floor(bbox[1]),math.ceil(bbox[2]),math.ceil(bbox[3])]
        old=dict(old_label=r['text'],bbox=bbox,crop_bbox=cb,**ownership(bbox,det));owner,failure=measured_owner(old,det)
        r.update(bbox=bbox,crop_bbox=cb,scale=sx,scale_y=sy,**measure(old,owner,det),measurement_failure=failure)
    bound=[r for r in rs if 'native_bbox' in r];page_ratios(bound);thresholds=json.loads((GEO/'labelfix/geometry/thresholds.json').read_text())
    for r in bound:r.update(decision(r,thresholds));r['usable_candidate']=r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rs));sp=BASE/'receipts/ajax-geometry'/(ident+'.json');summary=json.loads(sp.read_text());summary.update(algorithm=ALGORITHM,geometry_positive=sum(r['geometry_positive'] is True for r in rs),geometry_negative=sum(r['geometry_positive'] is False for r in rs),geometry_unresolved=sum(r['geometry_positive'] is None for r in rs),usable_candidate=sum(r.get('usable_candidate',False) for r in rs),lines_sha256=sha(path));write(sp,summary)
    return ident,len(rs)

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=2) as pool:
        for f in as_completed([pool.submit(reframe,p) for p in sorted((BASE/'bulk/ajax-geometry').glob('*.jsonl'))]):print(*f.result(),flush=True)
