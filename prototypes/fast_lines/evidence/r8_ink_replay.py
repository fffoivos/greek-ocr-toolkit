"""Foreground source-bound R8-02 replay; run as a script to choose source root."""
import sys,json,hashlib,platform
from pathlib import Path
source,out,mode=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
sys.path.insert(0,str(source))
from prototypes.fast_lines.shared import detector
from prototypes.fast_lines.stack import Stack
from prototypes.fast_lines.shared.review import detector_record
import cv2,numpy as np
P=Path('/Users/foivoskarounos-zamparloukos/Projects');BASE=Path(sys.argv[4]) if len(sys.argv)>4 else P/'greek-ocr-toolkit-ff-r8-stack/.astra/fast_lines/out/round8/R8-01b-i4';ROOT=Path(sys.argv[5]) if len(sys.argv)>5 else P/'greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round8/R8-02-i1'
manifest=P/'greek-ocr-toolkit-ff-r8-stack/.astra/fast_lines/out/round8/R8-01b/inputs-208.json';detector.MODEL=P/'greek-ocr-toolkit-astra-lines4/.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,default=lambda v:v.tolist() if hasattr(v,'tolist') else float(v))+'\n')
def sources():return {str(p.relative_to(source)):sha(p) for p in sorted((source/'prototypes/fast_lines').rglob('*.py')) if '/evidence/' not in str(p) and not p.name.startswith('test_')}
rows=json.loads(manifest.read_text())['pages'];assert len(rows)==208
if mode!='full':
 controls=set(json.loads((ROOT/'paired-controls.json').read_text()));rows=[r for r in rows if r['page'] in controls]
 if mode=='reverse':rows=rows[::-1]
out.mkdir(parents=True,exist_ok=False);identity=sources();dump(out/'source.json',identity);stack=Stack();records=[]
for i,row in enumerate(rows):
 assert sha(row['path'])==row['sha256'];p=row['page'];r=stack(row['path'],parked=row.get('parked',False));export=detector_record(row,r['items'],r['timing']['total_s']);old=json.loads((BASE/'runtime'/f'{p}.json').read_text());record=dict(page=p,group=row['group'],equal=export['items']==old['items'],items=len(r['items']),counts=r.get('counts'),stages=r['stages'],**r['timing'])
 if mode=='full':dump(out/f'{p}.json',export);dump(out/f'{p}.evidence.json',{k:v for k,v in r.items() if k!='items'})
 dump(out/f'{p}.timing.json',record);records.append(record);print(i+1,p,'equal' if record['equal'] else 'CHANGED',round(record['correction_s']*1000,3),flush=True)
assert sources()==identity
summary={}
for name,rr in [('all',records),('agreement',[r for r in records if r['group']=='agreement']),('discrepancy',[r for r in records if r['group'].startswith('discrepancy')])]:
 if rr:summary[name]={k:dict(n=len(rr),median_ms=float(np.median([r[k] for r in rr])*1000),p95_ms=float(np.percentile([r[k] for r in rr],95)*1000),max_ms=float(max(r[k] for r in rr)*1000)) for k in ('correction_s','detector_s','decode_s','total_s')}
dump(out/'receipt.json',dict(baseline=str(BASE.resolve()),baseline_source_sha256=sha(BASE/'runtime/source.json'),source_sha256=sha(out/'source.json'),input_sha256=sha(manifest),model_sha256=sha(detector.MODEL),mode=mode,python=platform.python_version(),platform=platform.platform(),opencv=cv2.__version__,opencv_threads=cv2.getNumThreads(),onnx='CPU sequential intra/inter1',timing='file decode + original Paddle + all correction dependencies; startup separate; export outside; no warmup, first-page effects retained in both sources',summary=summary,records=records,changed=[r['page'] for r in records if not r['equal']],over1s=[r['page'] for r in records if r['correction_s']>1]))
