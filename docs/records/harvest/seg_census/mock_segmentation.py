"""Authorized offline native 150+888 stage replay against the census03+0.8 package.
This is a stage check; it does not stand in for the exact batch-script mock.
"""
from pathlib import Path
import json
import sys

OUT = Path(__file__).resolve().parent
WORKTREE = OUT.parents[2]
PACKAGE = OUT/'package/projects/greek-ocr-toolkit-sol-recut'
DRAW = WORKTREE/'docs/harvest/collect_v3_admission/segeval1'
PREDICTOR = WORKTREE/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'
source = DRAW/'gate2/replay.py'
code = source.read_text().replace('ROOT = D.parents[4]', 'ROOT = Path('+repr(str(PACKAGE))+')')
code = code.replace("predictor = ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'", 'predictor = Path('+repr(str(PREDICTOR))+')')
code = code.replace("site = ROOT.parent/'ocr-review-sites-20261018'", 'site = Path('+repr(str(WORKTREE.parent/'ocr-review-sites-20261018'))+')')
namespace = {'__file__': str(source), '__name__': 'segcensus_stage_replay'}
exec(compile(code, str(source), 'exec'), namespace)
replay_out = OUT/'mock_stage'; replay_out.mkdir(exist_ok=True)
namespace.update(D=replay_out, DRAW=DRAW)
code = code.replace('failures=[]; records=[]; started=time.monotonic()', "globals()['captured_inputs']=inputs; failures=[]; records=[]; started=time.monotonic()")
namespace = {'__file__': str(source), '__name__': 'segcensus_stage_replay'}
exec(compile(code, str(source), 'exec'), namespace)
namespace.update(D=replay_out, DRAW=DRAW)
results={}
slice_rows=[]
all_stage_inputs=[]
for cohort, count in [('segeval1', 150), ('calibration', 888)]:
    namespace['run'](cohort)
    expected = namespace['load'](DRAW/f'gate2/replay_{cohort}.jsonl','line_id')
    actual = namespace['load'](replay_out/f'replay_{cohort}.jsonl','line_id')
    assert len(actual)==count and actual.keys()==expected.keys()
    for rid, value in actual.items():
        for field in ['verdict','reason']:
            assert value['after'][field].encode()==expected[rid]['after'][field].encode(),(rid,field)
    results[cohort]={'rows':count,'verdict_and_reason_exact':count}
    all_stage_inputs.extend(dict(cohort=cohort,row=row) for _,row,_ in namespace['captured_inputs'])
    history = namespace['load'](DRAW/f'deskew/replay_{cohort}.jsonl','line_id')
    for rid,row,_ in namespace['captured_inputs'][:150 if cohort=='segeval1' else 50]:
        slice_rows.append(dict(cohort=cohort,row=row,segmentation=actual[rid]['after'],frozen_05=dict(actual[rid]['after'],tool_version='0.5',verdict=history[rid]['verdict_before'],reason=history[rid]['reason_before'])))
(OUT/'mock_stage_results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))

import gzip
with gzip.open(OUT/'mock_slice_inputs.jsonl.gz','wt') as stream:
    for record in slice_rows: stream.write(json.dumps(record,ensure_ascii=False)+'\n')
assert len(slice_rows)==200

with gzip.open(OUT/'mock_stage_inputs.jsonl.gz','wt') as stream:
    for record in all_stage_inputs: stream.write(json.dumps(record,ensure_ascii=False)+'\n')
assert len(all_stage_inputs)==1038
