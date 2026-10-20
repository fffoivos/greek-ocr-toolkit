"""Validate saved orientation units, corners, guides and per-image evidence.

The one-time --upgrade-units option migrates this run's preliminary pixel-named
guide fields to explicit pixels/page-units fields. It never changes pixel boxes,
corners, recognition, decisions, or images. Final artifacts use the same schema
as OrientedWord.to_record; the receipt preserves pre/post hashes of migrations.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[3]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def words(records,image_size,page_size,upgrade=False):
    scale=np.array(page_size)/np.array(image_size);changed=False
    for r in records:
        if 'local_to_pixels' not in r:
            if not upgrade:raise AssertionError('preliminary ambiguous guide units; explicit migration required')
            r['local_to_pixels']=r['local_to_page']
            r['local_to_page']=(np.diag([*scale,1.])@np.array(r['local_to_pixels'])).tolist()
            r['guides_pixels']=r['guides_page']
            r['guides_page']={k:(np.array(v)*scale).tolist() for k,v in r['guides_pixels'].items()}
            r['geometry_units']=dict(local='crop pixels',pixels='current input raster pixels',page='current page units')
            changed=True
        corners=np.array(r['corners_pixels']);assert np.isfinite(corners).all()
        assert np.all(corners.min(0)>=-1e-6) and np.all(corners.max(0)<=np.array(image_size)+1e-6),r['word_id']
        assert np.allclose(corners*scale,r['corners_page'])
        l,t,b,bot=r['local_box'];p=np.array([[l,bot,1],[b,bot,1],[b,t,1],[l,t,1]])
        assert np.allclose((p@np.array(r['local_to_pixels']).T)[:,:2],corners)
        assert np.allclose((p@np.array(r['local_to_page']).T)[:,:2],r['corners_page'])
        for k,v in r['guides_local'].items():
            p=np.c_[v,np.ones(len(v))]
            assert np.allclose((p@np.array(r['local_to_page']).T)[:,:2],r['guides_page'][k])
            assert np.allclose(np.array(r['guides_pixels'][k])*scale,r['guides_page'][k])
        assert r['geometry_is_hypothesis']==(r['orientation_cw'] is None)
        assert r['recognition_confidence'] is not None and 0<=r['recognition_confidence']<=1
        assert r['text_direction']=='left_to_right' and r['from_ocr']
    return changed


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=ROOT/'.astra/out')
    ap.add_argument('--upgrade-units',action='store_true');args=ap.parse_args();receipts=[];count=0
    for path in sorted(args.out.glob('*.words.json'))+sorted((args.out/'rotated').glob('*.words.json')):
        before=sha(path);r=json.loads(path.read_text());changed=words(r['words'],r['image_size'],r['page_size'],args.upgrade_units)
        count+=1
        if changed:path.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        # The rotated part-two-schema cells mirror the new word records.
        if path.parent.name=='rotated':
            cells=path.with_name(path.name.replace('.words.json','.cells.json'))
            c=json.loads(cells.read_text());c['cells']=r['words'];cells.write_text(json.dumps(c,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
            assert (r['dominant']['orientation_cw'],r['dominant']['polarity_confidence'],r['dominant']['axis_confidence']) == (r['groups'][0]['orientation_cw'],r['groups'][0]['polarity_confidence'],r['groups'][0]['axis_confidence']),f'cached prior mismatch: {path.name}'
        receipts.append(dict(path=str(path.relative_to(ROOT)),before=before,after=sha(path),units_upgraded=changed,words=len(r['words'])))
    for path in (args.out/'orientation-acceptance').rglob('*.pipeline.json'):
        before=sha(path);r=json.loads(path.read_text());changed=False
        for record in r.get('ocr',[]):
            if 'words' in record:
                changed |= words(record['words'],record['frame']['image_size'],record['frame']['page_size'],args.upgrade_units)
        if changed:path.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        receipts.append(dict(path=str(path.relative_to(ROOT)),before=before,after=sha(path),units_upgraded=changed))
    assert count==94,f'expected 54+40 outputs, got {count}'
    (args.out/'orientation-artifact-audit.json').write_text(json.dumps(dict(pages=count,passed=True,receipts=receipts),indent=2)+'\n')
    print(json.dumps(dict(pages=count,passed=True,unit_migrations=sum(r['units_upgraded'] for r in receipts))))


if __name__=='__main__':main()
