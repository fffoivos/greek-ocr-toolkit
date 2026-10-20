"""Compare calibration flips/identity drift with the unchanged local 0.5 adapter."""
import gzip
import importlib.util
import json
from pathlib import Path
import sys
D=Path(__file__).resolve().parent;ROOT=D.parents[4];sys.path.insert(0,str(ROOT))
from replay_segeval1 import offline
sys.addaudithook(offline)
from greekocr.harvest.line_pipeline_native import ASSETS
initial=json.loads((D/'initial_state.json').read_text());pre=D/initial['portable_preimage_dir']
spec=importlib.util.spec_from_file_location('greekocr.harvest._segdeskew_calibration_baseline',pre/'greekocr/harvest/line_pipeline_native.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.ASSETS=ASSETS
worker=module.NativeSegmenter({'segmentation':{'version':'0.5'}},ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
spec=importlib.util.spec_from_file_location('calibration_crop_tools_before',pre/'greekocr/harvest/filtering_assets/crop-tools.py')
crop=importlib.util.module_from_spec(spec);spec.loader.exec_module(crop);worker.crop_tools=crop
site=ROOT.parent/'ocr-review-sites-20261018'
contexts={r['id']:r for r in json.loads((site/'qa/word-tolerance/context-evidence.json').read_text())['rows']}
worker.context=lambda row,*args:contexts.get(row['id'],dict(status='unavailable',reason='no saved calibration source context'))
meta={r['id']:r for r in json.loads(gzip.decompress((site/'review-data/font-normalized/predicted-rows.json.gz').read_bytes()))}
classes=json.loads((site/'review-data/population.json').read_text())['codebooks']['classes'];details={}
summary=json.loads((D/'cp3_calibration_summary.json').read_text())
selected={r['line_id'] for r in summary['flips']+summary['theta0_mismatches']+summary['bbox_drift']}
checks=[]
try:
 with (D/'calibration_drift_rows.jsonl').open('w') as output:
  for r in map(json.loads,(D/'replay_calibration.jsonl').read_text().splitlines()):
   if r['line_id'] not in selected:continue
   rid=r['line_id'];m=meta[rid]
   if m.get('google_text') is None or 'content_class' not in m:
    chunk=r['index']//1024
    if chunk not in details:details[chunk]=json.loads(gzip.decompress((site/f'population-data/details/{chunk:05d}.json.gz').read_bytes()))
    detail=details[chunk][r['index']%1024];assert detail[0]==rid
    m['google_text']=detail[2];m['content_class']=classes[int(dict(x.split(':') for x in detail[8].split('|'))['class'])]
   row=dict(r['after']['binding'],raw_text=m['google_text'],script_class=r['before']['script'],primary_class=m['content_class'],
    crop_path=str(site/'population-images'/(r['before']['image_sha256']+'.png')))
   baseline=worker(row);b=baseline['evidence']['box_evidence'];a=r['after']['evidence']['box_evidence']
   expected=b.get('predictions',[None]*3)[2];saved=r['before']['box_evidence']['predictions'][2]
   check=dict(line_id=rid,saved_verdict=r['verdict_before'],local05_verdict=baseline['verdict'],after_verdict=r['verdict_after'],
    local05_reason=baseline['reason'],saved_to_after_flip=r['verdict_before']!=r['verdict_after'],
    local05_to_after_flip=baseline['verdict']!=r['verdict_after'],
    local05_bbox_matches_after=b.get('bbox')==a.get('bbox'),
    local05_bbox_matches_saved=b.get('bbox')==r['before']['box_evidence'].get('bbox'),
    local05_expected=expected,saved_expected=saved,expected_delta=expected-saved if expected is not None else None,
    theta0=r['theta_deg']==0,
    local05_expected_matches_after=expected==a.get('predictions',[None]*3)[2],
    local05_padding_matches_after=baseline['evidence']['padding_evidence'].get('total_padding_line_heights')==r['after']['evidence']['padding_evidence'].get('total_padding_line_heights'))
   checks.append(check);output.write(json.dumps(dict(check=check,local05=baseline),ensure_ascii=False)+'\n')
   print(json.dumps(check),flush=True)
finally:worker.close()
receipt=dict(rows=len(checks),checks=checks,
 saved_to_after_flips=sum(r['saved_to_after_flip'] for r in checks),
 local05_to_after_flips_on_checked_rows=sum(r['local05_to_after_flip'] for r in checks),
 inherited_saved_to_local05_flips=[r for r in checks if r['saved_verdict']!=r['local05_verdict']],
 theta0_all_match_local05=all(r['local05_expected_matches_after'] and r['local05_padding_matches_after'] and r['local05_bbox_matches_after'] for r in checks if r['theta0']))
(D/'calibration_drift_summary.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='checks'},indent=2))
