"""Replay 0.8 saved evidence through the packaged policy, with no detector/reader."""
import argparse
import gzip
import json
from pathlib import Path
from greekocr.harvest.line_pipeline_native import ASSETS, JsonService, file_sha


def check(records):
    service = JsonService(['node', str(ASSETS/'service.mjs')])
    counts = {}
    try:
        with gzip.open(records, 'rt') as stream:
            for line in stream:
                r = json.loads(line)
                result = service.call(dict(operation='decide', policy_sha256=file_sha(ASSETS/'segmentation-policy.js'),
                                           evidence=r['after']['evidence']))
                assert result == {k: r['after'][k] for k in ('verdict', 'reason')}, r['line_id']
                counts[r['cohort']] = counts.get(r['cohort'], 0) + 1
    finally:
        service.close()
    assert counts == dict(segeval1=150, calibration=888)
    return dict(status='PASS', counts=counts, policy_sha256=file_sha(ASSETS/'segmentation-policy.js'), native_images_processed=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', type=Path, default=Path(__file__).with_name('parity_inputs.jsonl.gz'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = check(args.records)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
