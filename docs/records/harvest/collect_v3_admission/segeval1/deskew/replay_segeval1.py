"""Offline, byte-bound native SEG-DESKEW-1 replay; writes only under deskew/."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
D = Path(__file__).resolve().parent
DRAW = D.parent
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', PYTHONDONTWRITEBYTECODE='1')
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[name] = '1'


def offline(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo'):
        raise RuntimeError('network disabled for SEG-DESKEW-1')


sys.addaudithook(offline)
from greekocr.harvest.line_pipeline import canonical, digest
from greekocr.harvest.line_pipeline_native import NativeSegmenter


def load(path, key):
    values = [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
    result = {r[key]: r for r in values}
    assert len(result) == len(values)
    return result


def ratio(evidence):
    b = evidence['box_evidence']
    return (evidence['characters']+1)/(b['prediction']['expected']+1) if b.get('available') else None


def fail_timeout(signum, frame):
    raise TimeoutError('native row exceeded 120 seconds')


def main():
    before = load(DRAW/'keys/census02_segmentation_evidence.jsonl', 'row_id')
    features = load(DRAW/'keys/selected_features.jsonl', 'row_id')
    sealed = load(DRAW/'keys/sealed_decisions.jsonl', 'row_id')
    owner = load(DRAW/'scored/owner_rows.jsonl', 'line_id')
    assert len(before) == 150 and before.keys() == features.keys() == sealed.keys() == owner.keys()
    versions = json.loads((ROOT/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
    predictor = ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'
    worker = NativeSegmenter(versions, predictor)
    parity = []; flips = []; nonmeasurement_drift = []; failures = []
    allrows = []; started = time.monotonic()
    signal.signal(signal.SIGALRM, fail_timeout)
    try:
        with (D/'replay_segeval1.jsonl').open('w') as output:
            for index, (line_id, old) in enumerate(before.items(), 1):
                seal = sealed[line_id]
                assert old['verdict'] == seal['segmentation']['verdict']
                assert old['reason'] == seal['segmentation']['reason']
                row = dict(features[line_id], **seal['segmentation']['binding'],
                    raw_text=seal['google_text'], crop_path=str(DRAW/'crops'/f'{line_id}.png'))
                try:
                    signal.alarm(120)
                    after = worker(row)
                except Exception as exc:
                    failures.append(dict(line_id=line_id,type=type(exc).__name__,error=str(exc)))
                    print(json.dumps(failures[-1]), flush=True)
                    continue
                finally:
                    signal.alarm(0)
                assert after['policy_sha256'] == seal['segmentation']['policy_sha256']
                assert after['raw_text_sha256'] == seal['segmentation']['raw_text_sha256']
                a, b = after['evidence'], old['evidence']
                rf = a['box_evidence'].get('row_frame')
                comparisons = dict(bbox=a['box_evidence'].get('bbox') == b['box_evidence'].get('bbox'),
                    expected=a['box_evidence'].get('prediction',{}).get('expected') == b['box_evidence'].get('prediction',{}).get('expected'),
                    total_padding_line_heights=a['padding_evidence'].get('total_padding_line_heights') == b['padding_evidence'].get('total_padding_line_heights'))
                if rf and rf['angle_deg'] == 0:
                    parity.append(dict(line_id=line_id, **comparisons))
                # Every nonmeasurement evidence field must remain unchanged.
                other = deepcopy(a); original = deepcopy(b)
                for evidence in (other, original):
                    evidence['box_evidence'].pop('row_frame',None)
                    evidence['box_evidence'].pop('predictions',None)
                    if 'prediction' in evidence['box_evidence']:
                        evidence['box_evidence']['prediction'].pop('expected',None)
                    for key in ('total_padding_line_heights','upright_box_height','row_frame_height'):
                        evidence['padding_evidence'].pop(key,None)
                changed = [key for key in set(other)|set(original) if other.get(key) != original.get(key)]
                if after['frame'] != old['frame']:
                    changed.append('frame')
                if changed:
                    nonmeasurement_drift.append(dict(line_id=line_id,fields=changed))
                record = dict(line_id=line_id, before=old, after=after,
                    verdict_before=old['verdict'],verdict_after=after['verdict'],
                    reason_before=old['reason'],reason_after=after['reason'],
                    reader_state=owner[line_id]['reader_state'],theta_deg=rf['angle_deg'] if rf else None,
                    ratio_before=ratio(b),ratio_after=ratio(a),parity=comparisons,
                    nonmeasurement_drift=changed)
                output.write(json.dumps(record,ensure_ascii=False,allow_nan=False,sort_keys=True)+'\n');output.flush()
                allrows.append(record)
                if after['verdict'] != old['verdict']:
                    flips.append({k:record[k] for k in ('line_id','theta_deg','verdict_before','verdict_after','reason_before','reason_after','reader_state','ratio_before','ratio_after')} | dict(
                        upright_height=b['box_evidence']['bbox'][3]-b['box_evidence']['bbox'][1],row_frame_height=rf['height']))
                print(f"{index}/150 {line_id} theta={record['theta_deg']} {old['verdict']}->{after['verdict']}",flush=True)
    finally:
        worker.close()
    counters = Counter()
    for flip in flips:
        if flip['verdict_before'] == 'DROP' and flip['verdict_after'] == 'KEEP':
            counters['FP->KEEP' if flip['reader_state'] == 'fine' else 'flagged->KEEP'] += 1
        else:
            counters['other'] += 1
    summary = dict(rows=len(allrows),elapsed_seconds=time.monotonic()-started,
        theta0_rows=len(parity),theta0_exact=sum(all(r[k] for k in ('bbox','expected','total_padding_line_heights')) for r in parity),
        theta0_comparisons=parity,theta0_mismatches=[r for r in parity if not all(r[k] for k in ('bbox','expected','total_padding_line_heights'))],
        flips=flips,flip_counts={key:counters[key] for key in ('FP->KEEP','flagged->KEEP','other')},
        before_verdicts=dict(Counter(r['verdict_before'] for r in allrows)),
        after_verdicts=dict(Counter(r['verdict_after'] for r in allrows)),
        reader_states=dict(Counter(r['reader_state'] for r in allrows)),
        nonmeasurement_drift=nonmeasurement_drift,failures=failures,
        toolchain_digest=digest(canonical(versions)),segmentation_digest=versions['segmentation']['digest'],
        policy_sha256=worker.policy_sha,
        source_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [
            DRAW/'keys/census02_segmentation_evidence.jsonl',DRAW/'keys/selected_features.jsonl',DRAW/'keys/sealed_decisions.jsonl',
            DRAW/'scored/owner_rows.jsonl',ROOT/'docs/harvest/line_pipeline/tool_versions.json',predictor]})
    (D/'cp2_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    assert not failures and len(allrows) == 150
    assert not summary['theta0_mismatches']
    # Census-to-local runtime drift is reported verbatim; compare the untouched
    # adapter with check_baseline_drift.py rather than hiding or tuning it away.


if __name__ == '__main__':
    main()
