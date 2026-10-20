"""Bounded saved-metadata parity check. Never opens images or runs a detector."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'greekocr/harvest/filtering_assets'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--review-root',type=Path,default=ROOT.parent/'ocr-review-sites-20261018')
    p.add_argument('--predictor',type=Path,default=ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
    p.add_argument('--out',type=Path,default=ROOT/'docs/harvest/line_pipeline/policy-parity.json')
    args=p.parse_args();site=args.review_root
    report_path=site/'review-data/box-length-experiment.json';report=json.loads(report_path.read_text())
    assert (ASSETS/'segmentation-policy.js').read_bytes()==(site/'worker/box-length-policy.js').read_bytes()
    policy_sha=sha(ASSETS/'segmentation-policy.js')
    def service(requests):
        run=subprocess.run(['node',str(ASSETS/'service.mjs')],input=''.join(json.dumps(dict(r,policy_sha256=policy_sha))+'\n' for r in requests),text=True,capture_output=True,check=True)
        outputs=[json.loads(x) for x in run.stdout.splitlines()]
        assert len(outputs)==len(requests) and all(r['ok'] for r in outputs)
        return [r['result'] for r in outputs]
    outputs=service([dict(operation='decide',evidence=r) for r in report['rows']])
    assert all(a==r['judgements']['current'] for a,r in zip(outputs,report['rows']))
    valid=[r for r in report['rows'] if r['box_evidence']['available']]
    requests=[dict(script=r['script'],long_side=r['box_evidence']['long_side'],short_side=r['box_evidence']['short_side']) for r in valid]
    run=subprocess.run([str(args.predictor),str(ASSETS/'font-models.json')],input=''.join(json.dumps(r)+'\n' for r in requests),text=True,capture_output=True,check=True)
    predictions=[json.loads(x) for x in run.stdout.splitlines()]
    assert len(predictions)==len(valid) and all(r['ok'] for r in predictions)
    errors=[abs(a['result']['expected']-r['box_evidence']['predictions'][2]) for a,r in zip(predictions,valid)]
    assert max(errors)<1e-10
    raw_path=site/'qa/word-tolerance/context-evidence.json';raw=json.loads(raw_path.read_text())
    prior=json.loads((site/'qa/word-tolerance/reconciled-evidence.json').read_text())
    description=json.loads((site/'review-data/font-normalized-experiment.json').read_text())
    native_path=site/description['artifacts']['predicted-rows.json']['file']
    native={r['index']:r for r in json.loads(gzip.decompress(native_path.read_bytes()))}
    expected={r['index']:r for r in prior['rows']}
    reconciled=service([dict(operation='reconcile',context=r,crop=native[r['index']]) for r in raw['rows']])
    keys=('status','reason','whole_neighbour_words','partial_neighbour_words','unresolved_neighbour_words','whole_word_count_resolved','additional_full_line_count','split_neighbour_bands','physical_neighbour_band_count','group_bindings','raw_target_row_id')
    for original,answer in zip(raw['rows'],reconciled):
        assert {k:answer.get(k) for k in keys}=={k:expected[original['index']].get(k) for k in keys}
    receipt=dict(status='PASS',frozen_policy_byte_identical=True,decision_and_reason_parity=len(outputs),
        rust_prediction_rows=len(valid),max_absolute_prediction_error=max(errors),context_reconciliation_parity=len(reconciled),
        native_images_processed=0,refitted=False,source_files={str(p):sha(p) for p in [Path(__file__),report_path,raw_path,ASSETS/'service.mjs',ASSETS/'segmentation-policy.js',ASSETS/'font-models.json',args.predictor]})
    args.out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='source_files'}))


if __name__=='__main__':main()
