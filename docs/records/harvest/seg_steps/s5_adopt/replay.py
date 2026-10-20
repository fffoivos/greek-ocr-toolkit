"""Native S5 replay using S4 worker, S2 contexts and unchanged 120s row bound.

The only scientific change is the checked-in policy's default band. The
receipt-backed temporary view preserves historical script depth and paths.
"""
from greekocr.harvest.predictor_path import predictor_binary
from pathlib import Path
import importlib.util, json, signal, time
from collections import Counter

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
VIEW = Path(json.loads((OUT / 'view_receipt.json').read_text())['view'])
spec = importlib.util.spec_from_file_location('seg10_s4', VIEW / 'docs/harvest/seg_steps/s4/replay.py')
s4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s4)
read, dump, write, sha = s4.read, s4.dump, s4.write, s4.sha


def norm(z):
    if isinstance(z, dict):
        return {k: norm(v) for k, v in z.items() if k not in ('seconds', 'tool_version', 'policy_sha256')}
    if isinstance(z, list):
        return [norm(x) for x in z]
    return z


def run():
    main = read(s4.D / 'replay.jsonl')
    typology = [r for r in read(s4.D / 'typology_replay.jsonl') if not r['manifest']['control']]
    inputs = read(s4.D / 'inputs.jsonl')
    assert len(main) == len(inputs) == 1288 and len(typology) == 417
    assert [(r['cohort'], r['line_id'], r['row']) for r in main] == [(r['cohort'], r['line_id'], r['row']) for r in inputs]
    rows = [(r, r['after']) for r in main] + [(r, r['versions']['s4']) for r in typology]
    w = s4.worker()  # unchanged S4 factory; regenerated manifest labels it 0.9-s5
    assert w.policy_sha == sha(ROOT / 'greekocr/harvest/filtering_assets/segmentation-policy.js')
    signal.signal(signal.SIGALRM, s4.s1.timeout)
    start = time.monotonic(); counts = Counter(); drift = []; flips = []
    try:
        with (OUT / 'replay.jsonl').open('w') as output:
            for i, (r, old) in enumerate(rows, 1):
                assert sha(r['row']['crop_path']) == r['row']['crop_sha256']
                s4.s2.context(w, r)
                signal.alarm(120)
                new = w(r['row'])
                signal.alarm(0)
                assert new['tool_version'] == '0.9-s5'
                # Run old saved evidence through the newly loaded native service.
                # Full native evidence and decisions must equal this counterfactual.
                expected = w.service.call(dict(operation='decide', policy_sha256=w.policy_sha, evidence=old['evidence']))
                check = dict(old, verdict=expected['verdict'], reason=expected['reason'])
                box = old['evidence']['box_evidence']; pred = box.get('predictions', [None]*3)[2]
                ratio = (old['evidence']['characters']+1)/(pred+1) if pred is not None else None
                if norm(check) != norm(new):
                    drift.append(dict(line_id=r['line_id'], cohort=r['cohort'], saved_ratio=ratio,
                                      expected=norm(check), actual=norm(new)))
                counts['native_' + r['cohort']] += 1
                counts['native_matches_saved_measurement_and_new_band'] += norm(check) == norm(new)
                rec = dict(cohort=r['cohort'], line_id=r['line_id'], row=r['row'], before=old, after=new,
                           saved_ratio=ratio, small=r['small'], chars=r['chars'], A=r['A'])
                for key in ('owner_standard_state', 'owner_rating', 'manifest'):
                    if key in r: rec[key] = r[key]
                output.write(json.dumps(rec, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n'); output.flush()
                if old['verdict'] != new['verdict']:
                    flip = {k: rec[k] for k in ('cohort', 'line_id', 'saved_ratio', 'small', 'chars', 'A')}
                    flip.update(old_verdict=old['verdict'], new_verdict=new['verdict'], old_reason=old['reason'], new_reason=new['reason'])
                    flips.append(flip)
                    assert old['reason'].startswith('length:') and new['reason'].startswith('length:')
                if i % 100 == 0: print('S5 native replay', i, '/', len(rows), flush=True)
    finally:
        signal.alarm(0); w.close()
    write(OUT / 'flips.jsonl', flips)
    write(OUT / 'measurement_differences.jsonl', drift)
    dump(OUT / 'replay_receipt.json', dict(rows=len(rows), checks=counts, flips=len(flips), measurement_differences=len(drift),
        elapsed_seconds=time.monotonic()-start, network='OFF via unchanged S1 audit hook', readers=0, census=0,
        policy_sha256=sha(ROOT / 'greekocr/harvest/filtering_assets/segmentation-policy.js'),
        predictor_sha256=sha(predictor_binary()),
        workflow='unchanged S4 worker, S2 contexts, S1 timeout; only label/band change; original saved S4 comparison'))


if __name__ == '__main__': run()
