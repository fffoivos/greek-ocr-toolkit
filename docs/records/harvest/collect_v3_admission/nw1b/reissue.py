"""Publish W1 only after the shared actual-union gate and complete measurements."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
import hashlib
import json
import os
from collections import Counter
from greekocr.harvest.admission import NEIGHBOUR_PARAMS, run_files
from calibrate import require_qualification
BASE=Path(__file__).resolve().parent
OUT=BASE.parent


def main():
    gate=require_qualification(BASE/'calibration.json')
    assert gate['selected']['params']==NEIGHBOUR_PARAMS
    before=json.loads((BASE/'w1_before.json').read_text())
    expected=json.loads((BASE/'published_before.json').read_text())
    for path,digest in expected.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest, 'published baseline changed: '+path
    destination=BASE/'reissued'
    result=run_files([before['receipt']['input_path']],output_dir=destination)
    assert result['input_sha256']==before['receipt']['input_sha256']
    decisions=[json.loads(l) for l in (destination/'w1_originals_v3_admission.jsonl').read_text().splitlines()]
    old=set(before['passed_ids']);new={r['row_id'] for r in decisions if r['pass']}
    assert len(old)==28798 and not new-old
    withdrawn=sorted(old-new)
    for r in decisions:
        if r['row_id'] in old-new:
            assert 'neighbour_words' in r['rules_failed']
    drops=Counter(r['source']+'|'+r['class'] for r in decisions if 'neighbour_words' in r['rules_failed'])
    withdrawals=Counter(r['source']+'|'+r['class'] for r in decisions if r['row_id'] in old-new)
    report=dict(before=len(old),after=len(new),withdrawn=len(withdrawn),params=NEIGHBOUR_PARAMS,
                all_neighbour_drops=sum(drops.values()),neighbour_drops_per_source_class=dict(sorted(drops.items())),
                withdrawals_per_source_class=dict(sorted(withdrawals.items())),unmatched=result['neighbour_words_unmatched'],
                input_sha256=result['input_sha256'])
    for suffix in ('_admission.jsonl','_admitted.jsonl','_admission_receipt.json'):
        os.replace(destination/('w1_originals_v3'+suffix),OUT/('w1_originals_v3'+suffix))
    destination.rmdir()
    (OUT/'w1_neighbour_words_withdrawn.txt').write_text(''.join(r+'\n' for r in withdrawn))
    (BASE/'w1_summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    from prepare_w1 import offline
    sys.addaudithook(offline)
    main()
