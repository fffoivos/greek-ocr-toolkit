"""Source-bound final R6 A file-to-segments replay and numbered review exports."""
import argparse,json,platform
import cv2
from .round6_faintness import DEST,ROOT,cohort,inputs
from ..stack import Stack
from ..evidence.__main__ import signature
from ..shared.review import detector_record
from ..shared.timing import dump
from ..features_geometry.round5_benchmark import render


def run(version,repeat):
    out=DEST/version;out.mkdir(parents=True,exist_ok=True);key,files=signature()
    dump(out/f'source-r{repeat}.json',dict(key=key,files=files,platform=platform.platform()))
    rows=cohort();rows=rows if repeat%2 else rows[::-1]
    stack=Stack();stack.detector.infer(cv2.imread(str(ROOT/rows[0]['path']),0))
    for row in rows:
        p=row['page'];receipt=out/f'{p}.r{repeat}.json'
        if receipt.exists():raise RuntimeError('Existing experiment receipt '+p)
        r=stack(ROOT/row['path'],parked=row['parked']);gray,old=inputs(row)
        # Task A removes final polygons only. All survivors are byte-identical
        # to R5; no downstream geometry reruns can create hidden changes.
        kept={json.dumps(q['polygon']) for q in r['items']}
        assert kept.issubset({json.dumps(q['polygon']) for q in old}),p
        record=detector_record(row,r['items'],r['timing']['total_s']);target=out/(p+'.json')
        if target.exists():assert json.load(open(target))['items']==record['items'],p
        else:
            dump(target,record);dump(out/(p+'.evidence.json'),{k:v for k,v in r.items() if k!='items'})
            dump(out/(p+'.order.json'),render(gray,r,out/(p+'.jpg')))
            drop=[dict(q,index=i) for i,q in enumerate(old) if json.dumps(q['polygon']) not in kept]
            dump(out/(p+'.delta.json'),dict(page=p,removed=drop,old_count=len(old),new_count=len(r['items'])))
        dump(receipt,dict(page=p,group=row['group'],direction=row['direction'],image_sha256=row['sha256'],source=key,counts=r['counts'],stages=r['stages'],**r['timing']))
        print(p,r['counts'].get('faint',0),round(r['stages'].get('faint_s',0)*1000,2),round(r['timing']['correction_s']*1000,2),flush=True)
    assert signature()[0]==key,'Sources changed during the run'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('version');p.add_argument('--repeat',type=int,default=1);a=p.parse_args();run(a.version,a.repeat)
