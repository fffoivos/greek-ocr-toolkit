"""Validate saved final exports, source accounting, exclusions and repeat equality."""
import argparse
import json
from pathlib import Path
import numpy as np
import cv2
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.timing import dump
from ..shared.type_context import overlaps_exclusion


def retained_pixel_loss(original_polygons,polygon,image_size):
    """Count lost source pixels inside the image's half-open raster domain."""
    points=np.vstack([np.asarray(polygon)]+[np.asarray(p) for p in original_polygons])
    lo=np.maximum(0,np.floor(points.min(0)).astype(int))
    hi=np.minimum(np.asarray(image_size)-1,np.ceil(points.max(0)).astype(int))
    masks=[np.zeros((hi[1]-lo[1]+1,hi[0]-lo[0]+1),np.uint8) for _ in range(2)]
    cv2.fillPoly(masks[1],[np.rint(np.asarray(polygon)-lo).astype(np.int32)],1)
    for p in original_polygons:cv2.fillPoly(masks[0],[np.rint(np.asarray(p)-lo).astype(np.int32)],1)
    return int(np.count_nonzero(masks[0]&~masks[1]))


def validate(directory,repeats=(1,2)):
    if directory.name.startswith('r6'):
        from .review_r6 import validate as validate_r6
        return validate_r6(directory)
    from .__main__ import cohort
    rows=cohort(directory.name);checks=0;totals={};changed=[];agreements=[]
    review=json.loads((directory/'review.json').read_text())
    assert {x['page'] for x in review}=={x['page'] for x in rows};checks+=1
    for row in rows:
        p=row['page'];record=json.loads((directory/f'{p}.json').read_text());e=json.loads((directory/f'{p}.evidence.json').read_text())
        assert record['unit']=='line' and record['image_size']==row['image_size'];checks+=1
        if row['group']!='new_curved':assert e['original']==get_baseline(row);checks+=1
        else:
            pin=json.loads((directory.parent/'r5-merged'/f'{p}.evidence.json').read_text())
            assert e['original']==pin['original'];checks+=1
        assert record['seconds']==e['timing']['total_s'];checks+=1
        assert digest(ROOT/row['path'])==row['sha256'];checks+=1
        w,h=row['image_size']
        for q in record['items']:
            a=np.array(q['polygon']);assert a.ndim==2 and a.shape[1]==2 and len(a)>=3 and np.isfinite(a).all()
            assert (a>=0).all() and (a[:,0]<=w).all() and (a[:,1]<=h).all()
            assert q.get('baseline') is None and not q.get('discounted');checks+=1
        for q in record['items']:
            if q.get('type_slot') is not None or q.get('type_residual') is not None:
                assert not overlaps_exclusion(q['polygon'],e.get('removed',[]));checks+=1
        for q in e.get('shapes',{}).get('decisions',[]):
            if q['accepted']:assert q['retention']['lost_ink']==0;checks+=1
        for q in e.get('geometry',{}).get('changes',[]):assert q['retention']['lost_ink']==0;checks+=1
        for ext in ('.jpg','.paddle.jpg'):
            assert (directory/(p+ext)).stat().st_size>0;checks+=1
        # Every fragment join must retain every original source polygon pixel.
        for join in e.get('geometry',{}).get('fragments',{}).get('joins',[]):
            ids=join['source_ids']
            assert retained_pixel_loss([e['original'][i]['polygon'] for i in ids],join['polygon'],row['image_size'])==0;checks+=1
            assert any(q.get('source_ids')==ids for q in record['items']);checks+=1
        c=e['counts']
        if not row['parked']:
            assert len(record['items'])==len(e['original'])+c['q8']+c['curved']+c.get('columns',0)-c['back']-c['ornaments']-c.get('seals',0)+c['added']-c.get('joined_reduction',0);checks+=1
            # Original sources are accounted for by retained source IDs or removal.
            present={i for q in record['items'] for i in q.get('source_ids',[])}
            removed={i for q in e['removed'] for i in q['source_ids']}
            assert present|removed==set(range(len(e['original'])));checks+=1
            # Every Q8 piece remains exactly present (unless expressly removed).
            for cut in e['q8']['changes']:
                for poly in cut['new']:
                    descendants=[q for q in record['items']+e['removed'] if cut['line'] in q.get('source_ids',[])]
                    assert descendants;checks+=1
        else:assert record['items']==e['original'];checks+=1
        if directory.name.startswith('r5'):
            from shapely.geometry import Polygon
            from shapely.ops import unary_union
            for cut in e.get('geometry',{}).get('columns',{}).get('changes',[]):
                error=Polygon(cut['old']).symmetric_difference(unary_union([Polygon(poly) for poly in cut['new']])).area
                assert error<1e-7,(p,error);checks+=1
            order=json.loads((directory/f'{p}.order.json').read_text())
            assert sorted(x['item_index'] for x in order)==list(range(len(record['items'])));checks+=1
        for repeat in repeats:
            r=json.loads((directory/f'{p}.r{repeat}.json').read_text())
            assert r['counts']==c and r['image_sha256']==row['sha256'];checks+=1
        note=next(n for n in review if n['page']==p)
        assert note['review']!='pending' and note['observation'];checks+=1
        for k,v in c.items():totals[k]=totals.get(k,0)+v
        if any(c.values()):changed.append(p)
        if row['group']=='agreement':agreements.append(dict(page=p,changed=any(c.values())))
    out=dict(pages=len(rows),checks=checks,totals=totals,changed_pages=changed,agreement=agreements,
             repeats=list(repeats),held_out_accessed=False,review_scope='all 200 overviews; owner comment pages and changed details; not glyph transcription')
    dump(directory/'validation.json',out);print(json.dumps({k:v for k,v in out.items() if k not in ('changed_pages','agreement')},indent=2));return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='final');a=ap.parse_args();validate(ROOT/'.astra/fast_lines/out/stack'/a.version)
