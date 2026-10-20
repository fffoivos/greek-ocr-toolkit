"""Readback checks for every stored measurement, policy result and protected file."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
D=Path(__file__).resolve().parent;ROOT=D.parents[4];sys.path.insert(0,str(ROOT))
from replay_segeval1 import offline
sys.addaudithook(offline)
from greekocr.harvest.line_pipeline import canonical,digest
from greekocr.harvest.line_pipeline_native import ASSETS
initial=json.loads((D/'initial_state.json').read_text())
versions=json.loads((ROOT/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
records=[]
for name in ('replay_segeval1.jsonl','replay_calibration.jsonl'):
 values=[json.loads(s) for s in (D/name).read_text().splitlines()]
 assert len(values)==(150 if 'segeval1' in name else 888)
 assert len({r['line_id'] for r in values})==len(values)
 records.extend(values)
policy_sha=hashlib.sha256((ASSETS/'segmentation-policy.js').read_bytes()).hexdigest()
assert policy_sha=='8334dd4028822edbd740a1a96a0ead6367c7af953e545bad8bd60a911c65a819'
requests=[];pred_requests=[];expected=[]
for r in records:
 after=r['after'];e=after['evidence'];rf=e['box_evidence']['row_frame'];p=e['padding_evidence'];bbox=e['box_evidence']['bbox']
 assert after['tool_version']=='0.6' and after['policy_sha256']==policy_sha
 assert p['upright_box_height']==bbox[3]-bbox[1] and p['row_frame_height']==rf['height']
 assert p['total_padding_line_heights']==(after['frame']['height']-(bbox[3]-bbox[1]))/rf['height']
 assert rf['length']>0 and rf['height']>0 and len(rf['corners'])==4
 if rf['angle_deg']==0:
  assert rf['length']==bbox[2]-bbox[0] and rf['height']==bbox[3]-bbox[1]
 requests.append(dict(operation='decide',policy_sha256=policy_sha,evidence=e))
 before=r['before'];script=before.get('script')
 if script is None:
  script=None  # Bound below from the sealed selected metadata, never guessed.
 pred_requests.append(dict(long_side=max(rf['length'],rf['height']),short_side=min(rf['length'],rf['height']),script=script))
 expected.append(e['box_evidence']['predictions'][2])
features={r['row_id']:r for r in map(json.loads,(D.parent/'keys/selected_features.jsonl').read_text().splitlines())}
for r,request in zip(records,pred_requests):
 if request['script'] is None:request['script']=features[r['line_id']].get('script_class','pooled')
run=subprocess.run(['node',str(ASSETS/'service.mjs')],input=''.join(json.dumps(x)+'\n' for x in requests),text=True,capture_output=True,check=True)
outputs=[json.loads(s) for s in run.stdout.splitlines()]
assert len(outputs)==len(records) and all(r['ok'] for r in outputs)
assert all(o['result']=={k:r['after'][k] for k in ('verdict','reason')} for o,r in zip(outputs,records))
run=subprocess.run([str(ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'),str(ASSETS/'font-models.json')],input=''.join(json.dumps(x)+'\n' for x in pred_requests),text=True,capture_output=True,check=True)
outputs=[json.loads(s) for s in run.stdout.splitlines()]
assert len(outputs)==len(expected) and all(r['ok'] for r in outputs)
assert all(o['result']['expected']==v for o,v in zip(outputs,expected))
protected={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha for name,sha in initial['protected_sha256'].items()}
assert all(protected.values())
spec=importlib.util.spec_from_file_location('validate_version_build',ROOT/'scripts/harvest/build_filter_versions.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.build()['tools']==versions
# Compare complete top-level definitions, allowing only the requested methods.
pre=D/initial['portable_preimage_dir'];scope={}
for name,allowed in [('greekocr/harvest/filtering_assets/crop-tools.py',{'tight_box','features_from_observation'}),('greekocr/harvest/line_pipeline_native.py',{'NativeSegmenter'})]:
 a=ast.parse((pre/name).read_text());b=ast.parse((ROOT/name).read_text());assert len(a.body)==len(b.body)
 changed=[]
 for x,y in zip(a.body,b.body):
  if ast.dump(x)!=ast.dump(y):
   key=getattr(x,'name',None);assert key in allowed
   if key=='NativeSegmenter':
    assert len(x.body)==len(y.body)
    for u,v in zip(x.body,y.body):
     if ast.dump(u)!=ast.dump(v):assert getattr(u,'name',None)=='__call__'
   changed.append(key)
 scope[name]=changed
receipt=dict(status='PASS',rows=len(records),exact_policy_result_readback=len(records),exact_frozen_predictor_readback=len(records),
 padding_formula_verified=len(records),protected_files_unchanged=protected,source_definition_scope=scope,
 versions_rebuild_identical=True,policy_sha256=policy_sha,segmentation_digest=versions['segmentation']['digest'],
 toolchain_digest=digest(canonical(versions)))
(D/'replay_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
