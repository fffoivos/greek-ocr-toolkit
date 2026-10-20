"""Fixed development-only R8 regression and source-bound timing receipt."""
import argparse,json,platform,subprocess
from pathlib import Path
from time import perf_counter
import cv2,numpy as np
from ..stack import Stack
from ..shared.review import detector_record
from ..shared.timing import dump
from .r8_measurements import digest,sig


def make_inputs(old_root,fl,out):
    old_root=Path(old_root);fl=Path(fl)
    source=old_root/'.astra/fast_lines/out/round2/shared/manifest.json'
    x=json.loads(source.read_text());rows=x['pages']
    assert len(rows)==195
    for r in rows:r['path']=str(old_root/r['path'])
    for p in sorted((fl/'review_r4/pages').glob('*.png')):
        g=cv2.imread(str(p),0);rows.append(dict(page=p.stem,path=str(p),sha256=digest(p),image_size=list(g.shape[::-1]),group='new_supplied',direction='new',parked=False))
    assert len(rows)==208 and len({r['page'] for r in rows})==208
    for r in rows:
        r['previous']=str(old_root/'.astra/fast_lines/out/stack/r7'/f"{r['page']}.json")
        r['previous_sha256']=digest(r['previous'])
        assert digest(r['path'])==r['sha256']
    dump(out,dict(pages=rows,manifest_sha256=digest(source),scope='fixed 208 development: 195 plus 13 owner-supplied; no held-out'))


def run(inputs,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=json.loads(Path(inputs).read_text())['pages'];assert len(rows)==208
    sources=sig();dump(out/'source.json',sources);stack=Stack();records=[]
    for i,row in enumerate(rows):
        assert digest(row['path'])==row['sha256'];result=stack(row['path'],parked=row.get('parked',False))
        previous=json.loads(Path(row['previous']).read_text())['items']
        exported=detector_record(row,result['items'],result['timing']['total_s'])
        equal=exported['items']==previous
        page=row['page'];dump(out/f'{page}.json',exported)
        dump(out/f'{page}.evidence.json',{k:v for k,v in result.items() if k!='items'})
        receipt=dict(page=page,input_sha256=row['sha256'],previous_sha256=row['previous_sha256'],equal_items=equal,group=row['group'],counts=result['counts'],observations=result.get('observations',{}),stages=result['stages'],**result['timing'])
        dump(out/f'{page}.timing.json',receipt);records.append(receipt)
        print(i+1,page,'equal' if equal else 'CHANGED',round(result['timing']['correction_s']*1000,2),flush=True)
    assert sig()==sources,'sources changed during pass'
    summary={}
    for name,subset in [('all',records),('agreement',[r for r in records if r['group']=='agreement']),('discrepancy',[r for r in records if r['group'].startswith('discrepancy')])]:
        summary[name]={}
        for k in ('correction_s','detector_s','total_s'):
            v=np.array([r[k] for r in subset])*1000
            summary[name][k]=dict(n=len(v),median_ms=float(np.median(v)),p95_ms=float(np.percentile(v,95)),max_ms=float(v.max()))
    dump(out/'receipt.json',dict(inputs_sha256=digest(inputs),source_sha256=digest(out/'source.json'),python=platform.python_version(),platform=platform.platform(),opencv=cv2.__version__,opencv_threads=cv2.getNumThreads(),onnx='CPUExecutionProvider; sequential; intra/inter=1',timing_boundary='decode + first Paddle + all corrections; serialization outside',changed=[r['page'] for r in records if not r['equal_items']],over_1s=[dict(page=r['page'],seconds=r['correction_s']) for r in records if r['correction_s']>1],summary=summary))

if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True);a=s.add_parser('inputs');a.add_argument('old_root');a.add_argument('fl');a.add_argument('out');a=s.add_parser('run');a.add_argument('inputs');a.add_argument('out');a=p.parse_args()
    if a.cmd=='inputs':make_inputs(a.old_root,a.fl,a.out)
    else:run(a.inputs,a.out)
