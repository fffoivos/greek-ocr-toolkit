"""Reproduce every failed pipeline field, with no diagnostic truncation.
Run from the worktree root after benchmark_q5.py has completed. No timings here.
"""
import hashlib, inspect, json, sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'scripts/pages'))
import benchmark_q5 as bench
import benchmark_q4 as q4
import torch
from greekocr.pages.torch_prototypes import TorchArrays

torch.set_num_threads(1)
bench.cv2.setNumThreads(1)
backend=TorchArrays('cpu',16)
source=inspect.getsource(bench.differences)
needle='if sum(e["kind"] == kind for e in report["examples"]) < 20:'
assert source.count(needle)==1
uncapped=source.replace(needle,'if True:  # Preserve every diagnostic field.')
namespace=dict(bench.__dict__)
exec(compile(uncapped,'<uncapped-q5-comparator>','exec'),namespace)
compare=namespace['differences']
original=json.loads((ROOT/'.astra/q5-cpu/summary.json').read_text())
assert len(original['pages'])==54
assert all(bench.sha(ROOT/name)==value for name,value in original['source_manifest'].items())
output=dict(scope='Uncapped failure diagnostics, not timing',comparator_sha256=hashlib.sha256(uncapped.encode()).hexdigest(),pages=[])
for old in original['pages']:
 if not (old['pipeline_check']['discrete'] or old['pipeline_check']['numerical']):continue
 key=old['page_key']
 path=ROOT/'.astra/pages'/(key+'.png')
 with bench.Image.open(path) as opened:image=opened.copy()
 layout=ROOT/'.astra/layout'/(key+'.json')
 assert bench.sha(path)==old['source_sha256']
 assert (bench.sha(layout) if layout.exists() else None)==old['layout_sha256']
 regions=bench.read_layout(layout,image.size) if layout.exists() else []
 kwargs=dict(page_key=key,page_size=tuple(v/3 for v in image.size),table_regions=regions,options=bench.PageOptions(tables=True,statistics=True,join_lines=True))
 left=bench.snapshot(bench.process_page(image,**kwargs))
 with patch.object(bench.pixels,'_rect_morphology',lambda mask,shape,closing=False:backend.morphology_batch([(mask,shape,closing)])[0]), patch.object(bench.font,'_smooth_samples',lambda *c:backend.smooth_batch([c])[0]):
  right=bench.snapshot(bench.process_page(image,**kwargs))
 for value in (left,right):
  value['records']={k:q4.normalized(v,k,q4.allowlist()) for k,v in value['records'].items()}
  value['statistics']['stats']=q4.normalized(value['statistics']['stats'],'stats',q4.allowlist())
  value['statistics']['stats'].pop('geometry_sha256')
 result=compare(left,right)
 for name in ('discrete','numerical','maximum_float_error'):
  assert result[name]==old['pipeline_check'][name],(key,name,result[name],old['pipeline_check'][name])
 result['examples'].sort(key=lambda e:(e['kind'],e['path']))
 assert len(result['examples'])==result['discrete']+result['numerical']
 output['pages'].append(dict(page_key=key,**result))
 (ROOT/'.astra/q5-full-failures.json').write_text(json.dumps(output,indent=2))
 print(key,result['discrete'],result['numerical'],flush=True)
