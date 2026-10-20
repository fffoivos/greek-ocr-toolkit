"""Read-only full cache envelope census; output only to this isolated SEG directory.

Live cache is concurrently collected: this is an enumerated snapshot, not a
claim about discarded historical pages. No preparation or detector call.
"""
import gzip,json,hashlib
from pathlib import Path
import numpy as np
S=Path('docs/harvest/collect_v3_admission/seg'); R=Path.home()/'Projects/collect-v3-data/run'
out={'roots':[str(R/'cache/g1b'),str(S/'CP3_geometry')],'pages':[],'invalid_rows':[]}
for root in map(Path,out['roots']):
 for p in sorted(root.rglob('detector.json.gz')):
  try:raw=p.read_bytes();d=json.loads(gzip.decompress(raw))
  except FileNotFoundError:continue
  invalid=[]
  for r in d['rows']:
   delta=np.array(r['bottom'])-r['top']; body=np.array(r['baseline'])-r['meanline']
   if np.any(delta<=0) or np.any(body<=0) or r['x1']<=r['x0']:
    q=dict(path=str(p),row_id=r['row_id'],minimum_envelope=float(delta.min()),minimum_body=float(body.min()),inverted_columns=int((delta<0).sum()),degenerate_columns=int((delta==0).sum()))
    invalid.append(q);out['invalid_rows'].append(q)
  out['pages'].append(dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),rows=len(d['rows']),invalid_rows=len(invalid)))
p=S/'CP3_geometry/gazette_modern--0020420cfe156a73--s000';d=json.loads(gzip.decompress((p/'detector.json.gz').read_bytes()));r=next(r for r in d['rows'] if r['row_id']=='row-00077')

curves={k:dict(min=min(r[k]),max=max(r[k]),first=r[k][0],last=r[k][-1]) for k in ('baseline','meanline','top','bottom','font_top','font_bottom','accent_top','accent_bottom')}
labels=np.load(p/'labels.npz')['labels']; yy,xx=np.nonzero(np.isin(labels,r['component_ids']))
out['diagnosis']={'row':r,'curve_summary':curves,'component_pixels':len(xx),'component_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'structure':[s for s in d['structure_rows'] if s['id']==r['row_id']]}
out['inverted_rows']=sum(q['inverted_columns']>0 for q in out['invalid_rows']);out['degenerate_rows']=sum(q['degenerate_columns']>0 for q in out['invalid_rows']);out['cache_records']=len(out['pages']);out['row_records']=sum(q['rows'] for q in out['pages'])
# Bind recorded tranche metadata and neighbour addresses without list-index guesses.
line_rows={i:z['id'] for z in d['structure_rows'] for i in z.get('line_indices',[])}
out['diagnosis']['neighbour_row_ids']={k:[line_rows.get(i) for i in sorted(set(v)) if i>=0]
    for k,v in r['neighbours'].items() if isinstance(v,list)}
out['diagnosis']['overlapping_feature_labels']=[]
for raw in (R/'W1/features.jsonl').open():
 f=json.loads(raw)
 if f['page_id']=='gazette_modern--0020420cfe156a73--s000':
  a,b,c,e=f['crop_bbox'];hits=int(((xx>=a)&(xx<c)&(yy>=b)&(yy<e)).sum())
  if hits:out['diagnosis']['overlapping_feature_labels'].append(dict(id=f['id'],crop_bbox=f['crop_bbox'],label=f['label'],assigned_pixels_in_crop=hits))
for page in out['pages']:
 pid=Path(page['path']).parent.name
 page['recorded_tranches']=[t for t in ('W1','W2') if (R/t/'pages'/f'{pid}.json').is_file()]
from datetime import datetime,timezone
out['completed_utc']=datetime.now(timezone.utc).isoformat()
out['snapshot_scope']='All detector.json.gz files enumerated under the two roots; live cache is concurrent, not historical. Duplicate page copies, if any, are separate records.'
(S/'CP3b_geometry_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('inverted_rows','degenerate_rows','cache_records','row_records')}))
