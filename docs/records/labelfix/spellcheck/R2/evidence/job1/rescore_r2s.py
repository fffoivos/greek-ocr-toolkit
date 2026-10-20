"""Offline R2S rescore: run from the worktree root; no inference or deployment."""
import json
from pathlib import Path
from scripts.labelfix import r2_score as scorer
from scripts.labelfix.clariden.r1_common import rows, sha256
from greekocr.labelfix.release_gate import policy_binding

EVID = Path('docs/labelfix/spellcheck/R2/evidence/job1')
FIX = Path('tests/labelfix/fixtures/r2')
ROOT = Path('artifacts/labelfix_r2/output_3681404')
TRUTH = Path('docs/labelfix/spellcheck/S4_lines.jsonl.gz')
OVERLAY = Path('docs/labelfix/spellcheck/R2/truth_overlay_v1_1.json')


def metrics(atomic):
    p, r = atomic['precision'], atomic['recall']
    return dict(precision=p, recall=r, f1=2*p*r/(p+r),
                tp=atomic['tp'], fp=atomic['fp'], fn=atomic['fn'])


def main():
    inputs = {}
    def bind(path, expected=None):
        actual = sha256(path)
        if expected is not None:
            assert actual == expected, str(path)
        inputs[str(path)] = actual
        return actual

    bind(EVID/'scores.json', 'f2eb0f090734338c2a127272153f132044a98670461575343a6560895ae235f2')
    historical = json.loads((EVID/'scores.json').read_text())['v1_1']
    bind(TRUTH)
    bind(OVERLAY, '34691279fb2634b103b42c779aacfec735480727259cfff643205b57deaa7f2a')
    bind(FIX/'binding.json')
    binding = json.loads((FIX/'binding.json').read_text())['sha256']
    for name in ('heldout_lines.jsonl.gz', 'A_predictions.jsonl.gz'):
        bind(FIX/name, binding[name])
    bind(ROOT/'READBACK_RECEIPT.json')
    readback = {f['path']: f['sha256'] for f in json.loads((ROOT/'READBACK_RECEIPT.json').read_text())['files']}
    md = list(rows(FIX/'heldout_lines.jsonl.gz'))
    meta = {l['id']: dict(l, coverage_by_start={c['start']: c for c in l['coverage']}) for l in md}
    extraction = Path('artifacts/labelfix_r1/heldout_font/extraction_receipt.json')
    ex_hash = bind(extraction)
    ex = json.loads(extraction.read_text())
    predictions = {'A16': list(rows(FIX/'A_predictions.jsonl.gz'))}
    for seed in (17, 18):
        folder = ROOT/'C'/str(20261000+seed)
        path = folder/'heldout_predictions.jsonl'
        receipt = folder/'heldout_predictions.receipt.json'
        bind(receipt, readback[str(receipt.relative_to(ROOT))])
        rr = json.loads(receipt.read_text())
        bind(path, readback[str(path.relative_to(ROOT))])
        assert sha256(path) == rr['prediction_sha256']
        bind(folder/'best.pt', rr['checkpoint_sha256'])
        assert rr['extraction_receipt_sha256'] == ex_hash
        assert rr['input_index_sha256'] == ex['sha256']['index.npy']
        pp = list(rows(path))
        assert len(pp) == rr['samples']
        predictions[f's{seed}'] = pp
    expected = {(lid, c['start']) for lid, l in meta.items() for c in l['coverage'] if c['scored']}
    for pp in predictions.values():
        assert len(pp) == len(expected) == 11329
        assert {(p['line_id'], p['start']) for p in pp} == expected
        for p in pp:
            coverage = meta[p['line_id']]['coverage_by_start'][p['start']]
            assert p['base'] == coverage['base']
            p['coverage'] = coverage
    lines = [l for l in scorer.truth_lines(TRUTH) if not l['dev']]
    assert len(lines) == 666
    lines, overlay = scorer.apply_overlay(lines, json.loads(OVERLAY.read_text()))
    result = dict(schema='R2S-UNKNOWN-insertions-v1', overlay=overlay, arms={}, comparison={})
    records = {}
    for model, pp in predictions.items():
        raw, records[model] = scorer.score(lines, pp)
        current = raw['micro']
        # Reproduce the historical defect on these exact inputs before comparing.
        legacy = [dict(r, truth=[0]*4, unknown=[]) if r['inserted_prediction'] else r for r in records[model]]
        assert scorer.summarize(legacy)['atomic'] == historical[model]['raw']['micro']['atomic']
        continuity = scorer.continuity(lines, meta, pp)
        assert continuity == historical[model]['continuity']
        old = metrics(historical[model]['raw']['micro']['atomic'])
        new = metrics(current['atomic'])
        assert old['tp'] == new['tp'] and old['fn'] == new['fn']
        marked = current['inserted_slots_marked']
        assert old['fp']-new['fp'] == sum(marked['by_head'].values())
        assert current['inserted_slots'] == 1334 and current['states']['UNKNOWN'] == 2258
        matched_fp = scorer.summarize([r for r in records[model] if not r['unmatched_print']])['atomic']['fp']
        assert matched_fp == new['fp']
        result['arms'][model] = dict(old=old, new=new, matched_slot_fp=matched_fp,
            inserted_slots=current['inserted_slots'], inserted_slots_marked=marked,
            raw=raw, continuity=continuity)
        print(model, 'old', old, 'new', new, 'matched FP', matched_fp, flush=True)
    sign = lambda x: int(x > 0)-int(x < 0)
    for model in ('s17', 's18'):
        a, b = result['arms']['A16'], result['arms'][model]
        comparison = {}
        for metric in ('precision', 'recall', 'f1'):
            old = b['old'][metric]-a['old'][metric]
            new = b['new'][metric]-a['new'][metric]
            comparison[metric] = dict(old_delta=old, new_delta=new, sign_changed=sign(old) != sign(new))
        pair = scorer.paired(records['A16'], records[model])
        old_delta = historical[model]['paired_union_vs_A']['weighted_accuracy_delta']
        comparison['paired_tuple_accuracy'] = dict(old_delta=old_delta,
            new_delta=pair['weighted_accuracy_delta'], sign_changed=sign(old_delta) != sign(pair['weighted_accuracy_delta']))
        result['arms'][model]['paired_union_vs_A'] = pair
        result['comparison'][model] = comparison
        print(model, 'BASE minus A:', comparison, flush=True)
    result['seed_pair'] = scorer.paired(records['s17'], records['s18'])
    assert policy_binding()['sha256'] == '6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406'
    result['receipt'] = dict(inputs=inputs, code_sha256=sha256('scripts/labelfix/r2_score.py'),
        rescore_script_sha256=sha256(__file__), policy=policy_binding(), inference_runs=0,
        network='OFF', deployed=False,
        input_note='scorer_inputs/ contains a one-line synthetic fixture; used saved job 3681404 exports and frozen truth/metadata, reproducing historical atomic counts exactly')
    (EVID/'scores_r2s.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
