"""Build page-detector caches, bound to the exact main harvest source tree."""
import argparse,hashlib,json,sys
from concurrent.futures import ProcessPoolExecutor,as_completed
from pilotlib import *
sys.path.insert(0,str(ROOT))
import greekocr
GEO=ROOT.parent/'greek-ocr-toolkit-sol-labelfix/greekocr'
greekocr.__path__.append(str(GEO))
from greekocr.labelfix.geometry.io import cache_page

def detector_identity():
    paths=sorted([*(ROOT/'greekocr/pages').glob('*.py'),*(ROOT/'greekocr/glyphs').glob('*.py')]);h=hashlib.sha256()
    for p in paths:h.update(str(p.relative_to(ROOT/'greekocr')).encode());h.update(p.read_bytes())
    return h.hexdigest()

def one(r):
    try:
        data,ink,labels,receipt=cache_page(BASE/r['image'],BASE/'cache/g1b'/r['id'],r['image_sha256'],detector_identity())
        write(BASE/'receipts/detector'/(r['id']+'.json'),dict(page_id=r['id'],pilot=r['pilot'],rows=len(data['rows']),blocked_rows=data['blocked_rows'],detector_sha256=detector_identity(),source_sha256=r['image_sha256'],detector_s=receipt['detector_s'],cache_hit=receipt['cache_hit'],status='ok'))
        return r['id'],len(data['rows'])
    except Exception as e:
        write(BASE/'receipts/detector'/(r['id']+'.json'),dict(page_id=r['id'],pilot=r['pilot'],status='error',error_class=type(e).__name__,error=str(e)[:500]));return r['id'],type(e).__name__

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pilots');parser.add_argument('--workers',type=int,default=3);args=parser.parse_args()
    selected=[json.loads(p.read_text()) for p in sorted((BASE/'receipts/pages').glob('*.json'))]
    selected=[r for r in selected if not r.get('excluded') and not (BASE/'receipts/detector'/(r['id']+'.json')).exists()]
    if args.pilots:selected=[r for r in selected if r['pilot'] in args.pilots.split(',')]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for f in as_completed([pool.submit(one,r) for r in selected]):print(*f.result(),flush=True)
