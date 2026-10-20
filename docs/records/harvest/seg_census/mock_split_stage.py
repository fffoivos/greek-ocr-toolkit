"""Fresh native split-bound replay; compare verdict/reason with gate2 byte-exact."""
import gzip
import json
from pathlib import Path
import sys

D = Path(__file__).resolve().parent
REPO = D.parents[2]
sys.path.insert(0, str(D/'package/projects/greek-ocr-toolkit-sol-recut'))
from greekocr.harvest.line_pipeline_native import NativeSegmenter
from greekocr.harvest.line_pipeline_census04 import load_split
from greekocr.harvest.line_pipeline_census import file_sha


def main():
    inputs = [json.loads(s) for s in gzip.open(D/'mock_stage_inputs.jsonl.gz', 'rt')]
    expected = {}
    for cohort in ('segeval1', 'calibration'):
        path = REPO/f'docs/harvest/collect_v3_admission/segeval1/gate2/replay_{cohort}.jsonl'
        expected[cohort] = {r['line_id']: r['after'] for r in map(json.loads, path.read_text().splitlines())}
    split = D/'mock_stage/split-input.jsonl'
    assignments = [dict(parent_id=r['row']['parent_id'], row_id=r['row']['id'], edition_id='mock:'+r['row']['parent_id']+':'+r['row']['id'],
                        split=('train','dev','test')[i%3]) for i,r in enumerate(inputs)]
    split.write_text(''.join(json.dumps(r)+'\n' for r in assignments))
    allocation = load_split(dict(path=str(split), sha256=file_sha(split)))
    worker = NativeSegmenter({'segmentation': {'version': '0.8'}}, REPO/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
    # Context was optional in mode-i; use the same saved contexts for calibration.
    site = REPO.parent/'ocr-review-sites-20261018'
    contexts = {r['id']: r for r in json.loads((site/'qa/word-tolerance/context-evidence.json').read_text())['rows']}
    original_context = worker.context
    counts = dict(segeval1=0, calibration=0)
    try:
        for r in inputs:
            row = r['row']
            new = dict(row, **allocation[(row['parent_id'], row['id'])])
            worker.context = (lambda row,*args: contexts.get(row['id'],dict(status='unavailable',reason='no saved calibration source context'))) if r['cohort']=='calibration' else original_context
            answer = worker(new)
            want = expected[r['cohort']][row['id']]
            for key in ('verdict','reason'):
                assert answer[key].encode() == want[key].encode(), (row['id'],key)
            assert answer['binding']['split'] == new['split']
            counts[r['cohort']] += 1
    finally:
        worker.close()
    assert counts == dict(segeval1=150, calibration=888)
    result = dict(mode='split-bound-stage', counts=counts, verdict_and_reason_byte_exact=True,
                  split_input_sha256=file_sha(split), native_images_replayed=1038)
    (D/'mock_split_stage_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
