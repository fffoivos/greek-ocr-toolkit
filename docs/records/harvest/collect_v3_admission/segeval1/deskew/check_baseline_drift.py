"""Attribute witnessed census-to-Mac drift using the untouched 0.5 preimage."""
import importlib.util
import json
from pathlib import Path
import sys

D=Path(__file__).resolve().parent
ROOT=D.parents[4]
sys.path.insert(0,str(ROOT))
from replay_segeval1 import load, offline
sys.addaudithook(offline)
from greekocr.harvest.line_pipeline_native import ASSETS
initial=json.loads((D/'initial_state.json').read_text())
pre=D/initial['portable_preimage_dir']
spec=importlib.util.spec_from_file_location('greekocr.harvest._segdeskew_baseline',pre/'greekocr/harvest/line_pipeline_native.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.ASSETS=ASSETS
worker=module.NativeSegmenter({'segmentation':{'version':'0.5'}},ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
spec=importlib.util.spec_from_file_location('crop_tools_before',pre/'greekocr/harvest/filtering_assets/crop-tools.py')
crop=importlib.util.module_from_spec(spec);spec.loader.exec_module(crop);worker.crop_tools=crop


def strip_measurements(e):
    e=json.loads(json.dumps(e))
    b=e['box_evidence'];b.pop('row_frame',None);b.pop('predictions',None)
    if 'prediction' in b:b['prediction'].pop('expected',None)
    for k in ('total_padding_line_heights','upright_box_height','row_frame_height'):e['padding_evidence'].pop(k,None)
    return e


def strip_seconds(o):
    if isinstance(o,dict):return {k:strip_seconds(v) for k,v in o.items() if k!='seconds'}
    if isinstance(o,list):return [strip_seconds(v) for v in o]
    return o


features=load(D.parent/'keys/selected_features.jsonl','row_id')
sealed=load(D.parent/'keys/sealed_decisions.jsonl','row_id')
checks=[]
try:
    with (D/'baseline_drift_rows.jsonl').open('w') as out:
        for record in map(json.loads,(D/'replay_segeval1.jsonl').read_text().splitlines()):
            if not record['nonmeasurement_drift']:continue
            rid=record['line_id'];seal=sealed[rid]
            row=dict(features[rid],**seal['segmentation']['binding'],raw_text=seal['google_text'],crop_path=str(D.parent/'crops'/f'{rid}.png'))
            baseline=worker(row)
            same_evidence=strip_measurements(baseline['evidence'])==strip_measurements(record['after']['evidence'])
            same_frame=strip_seconds(baseline['frame'])==strip_seconds(record['after']['frame'])
            check=dict(line_id=rid,fields=record['nonmeasurement_drift'],
                untouched_adapter_matches_after_nonmeasurement_evidence=same_evidence,
                untouched_adapter_matches_after_frame_except_seconds=same_frame,
                untouched_adapter_matches_saved_verdict=baseline['verdict']==record['verdict_before'],
                untouched_adapter_matches_saved_bbox=baseline['evidence']['box_evidence'].get('bbox')==record['before']['evidence']['box_evidence'].get('bbox'))
            checks.append(check)
            out.write(json.dumps(dict(check=check,untouched_adapter_result=baseline),ensure_ascii=False,allow_nan=False)+'\n')
            print(json.dumps(check),flush=True)
finally:worker.close()
summary=dict(rows=len(checks),checks=checks,
    all_nonmeasurement_evidence_reproduced=all(r['untouched_adapter_matches_after_nonmeasurement_evidence'] for r in checks),
    all_frames_except_seconds_reproduced=all(r['untouched_adapter_matches_after_frame_except_seconds'] for r in checks),
    all_saved_verdicts_reproduced=all(r['untouched_adapter_matches_saved_verdict'] for r in checks))
(D/'baseline_drift_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
assert summary['all_nonmeasurement_evidence_reproduced'] and summary['all_frames_except_seconds_reproduced'] and summary['all_saved_verdicts_reproduced']
