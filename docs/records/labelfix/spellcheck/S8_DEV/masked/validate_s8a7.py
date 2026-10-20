"""Independent slot/count aggregation and output-boundary checks for S8a7."""
import run_s8a7 as r
import collections as C
import gzip
import json
import math
from pathlib import Path
import numpy as np


def equal(a, b):
    if a is None or b is None:
        assert a is b
    else:
        assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), (a, b)


def main():
    d, p, t = r.DEST, r.p, r.t
    receipt = p.load(d/'receipt.json')
    summary = p.load(d/'summary.json')
    assert receipt['status'] == 'PASS' and not receipt['network'] and receipt['reader_inference_runs'] == 0
    assert r.protected() == p.load(d/'protected_inputs.json')
    for name, digest in receipt['output_sha256'].items():
        assert p.sha(d/name) == digest, name
    assert p.sha(r.REPORT) == receipt['report_sha256']
    truth = {x['id']: x for x in p.rows(p.E/'dev_truth.jsonl.gz') if x.get('type') == 'item'}
    scores = p.rows(d/'scores_per_word.jsonl.gz')
    words, delta = p.rows(d/'word_comparison.jsonl'), p.rows(d/'delta_cards.jsonl')
    assert len({x['uid'] for x in words}) == len(words) == 4942
    assert {x['uid'] for x in delta} == {x['uid'] for x in words if x['new_candidate']}
    assert len(delta) == summary['delta_total'] == receipt['delta_words']
    assert {x['id'] for x in scores} == {k for k, v in truth.items() if v['status'] == 'resolved'}
    assert sum(x['scored'] for x in scores) == receipt['paired_scored']
    for x in words:
        new = t.canonical(x['forms']['detector_masked']) not in {t.canonical(y) for y in x['frozen_options'].values()}
        assert new == x['new_candidate']
        assert x['scored'] == (x['truth_status'] == 'resolved' and not new)
    counts = {}
    for x in scores:
        old = truth[x['id']]
        assert x['weight'] == old['weight'] and x['truth'] == old['truth']
        assert x['presence']['original'] == old['presence']['detector_original']
        assert ('masked' in x['presence']) == x['scored']
        if x['fallback_kind']:
            assert not x['mask_applied'] and x['presence']['original'] == x['presence']['masked']
        for variant, data in x['presence'].items():
            counts[x['id'], variant] = {}
            for f in t.KINDS:
                c = C.Counter(dict(TP=0, FP=0, FN=0, TN=0))
                for s in data['slots']:
                    a, b = s['truth_presence'][f], s['prediction_presence'][f]
                    c[('TP' if a else 'FP') if b else ('FN' if a else 'TN')] += 1
                    if variant == 'masked':
                        ds = s.get('detector_slot')
                        ev = ds.get('evidence', {}) if ds else {}
                        equal(int(s['prediction_presence']['any']), int(bool(ev.get('above') or ev.get('below'))))
                assert dict(c) == data['counts'][f]
                counts[x['id'], variant][f] = c
    checked_cells, paired_intervals = 0, 0
    for wi, w in enumerate(t.WAVES):
        ws = summary['waves'][w]
        resolved = [x for x in scores if x['wave'] == w]
        for name, cohort in (
            ('eligible_paired', [x for x in resolved if x['scored']]),
            ('masked_only', [x for x in resolved if x['scored'] and x['mask_applied']]),
            ('unmasked_fallback', [x for x in resolved if x['scored'] and x['fallback_kind']])):
            saved = ws['cohorts'][name]
            assert len(cohort) == saved['cards']
            equal(sum(x['weight'] for x in cohort), saved['sum_weights'])
            for f in t.KINDS:
                for v in ('original', 'masked'):
                    cell = saved['presence'][f][v]
                    totals = {k: sum(x['weight']*counts[x['id'], v][f][k] for x in cohort) for k in ('TP', 'FP', 'FN', 'TN')}
                    for k in totals:
                        equal(totals[k], cell['counts'][k]['weighted'])
                        assert cell['counts'][k]['raw'] == sum(counts[x['id'], v][f][k] for x in cohort)
                    for metric, error in (('precision', 'FP'), ('recall', 'FN')):
                        den = totals['TP']+totals[error]
                        equal(cell[metric]['weighted_den'], den)
                        equal(cell[metric]['value'], totals['TP']/den if den else None)
                        interval = cell[metric]['ci']
                        assert interval is None or 0 <= interval[0] <= interval[1] <= 1
                    checked_cells += 1
            # Independently rebuild the primary document paired bootstrap.
            groups = sorted({x['line_id'].split('-p')[0] for x in cohort})
            if groups:
                for metric, error in (('precision', 'FP'), ('recall', 'FN')):
                    matrices = []
                    for group in groups:
                        rr = [x for x in cohort if x['line_id'].split('-p')[0] == group]
                        matrices.append([sum(x['weight']*(counts[x['id'], v]['any']['TP']+(counts[x['id'], v]['any'][error] if den else 0)) for x in rr)
                                         for v in ('original', 'masked') for den in (False, True)])
                    rng = np.random.default_rng(t.SEED+wi)
                    totals = rng.multinomial(len(groups), [1/len(groups)]*len(groups), size=t.REPS) @ np.asarray(matrices)
                    good = (totals[:, 1] > 0) & (totals[:, 3] > 0)
                    if np.any(good):
                        diffs = totals[good, 2]/totals[good, 3]-totals[good, 0]/totals[good, 1]
                        ci = np.quantile(diffs, [.025, .975])
                        for a, b in zip(ci, saved['presence']['any']['paired_change'][metric]['document_bootstrap95']):
                            equal(a, b)
                        paired_intervals += 1
    ids = (p.OUT/'S8_DEV_ids.txt').read_text().split()
    originals, effective = {}, {}
    for k in ids:
        originals[k] = json.loads(gzip.decompress((p.E/'baseline/original'/(k+'.json.gz')).read_bytes()))
        masked = d/'baseline/masked'/(k+'.json.gz')
        effective[k] = json.loads(gzip.decompress(masked.read_bytes())) if masked.exists() else originals[k]
        for record in (originals[k], effective[k]):
            slots = record['detector']['slots']
            m = record['metrics']
            assert m['letters'] == len(slots)
            for key in p.METRICS:
                n = sum(bool(s.get('evidence', {}).get(key) if key.startswith('clipped_') else s.get(key)) for s in slots)
                assert m[key] == n
            assert m['component_assignments'] == sum(len(s.get('component_ids', [])) for s in slots)
            assert m['unnamed_blobs'] == sum(len(s.get('unnamed', [])) for s in slots)
    for w in (*t.WAVES, 'ALL'):
        ws = summary['ALL'] if w == 'ALL' else summary['waves'][w]
        kk = [k for k in ids if w == 'ALL' or originals[k]['wave'] == w]
        for variant, source in (('original', originals), ('effective', effective)):
            saved = ws['baseline'][variant]
            for key in ('letters', *p.METRICS, 'component_assignments', 'unnamed_blobs'):
                assert saved[key] == sum(source[k]['metrics'][key] for k in kk)
            for mode in p.MODES:
                assert saved['gate'][mode] == dict(C.Counter(source[k]['decisions'][mode]['status'] for k in kk))
    assert len(list((d/'baseline/masked').glob('*.json.gz'))) == 441
    assert len(summary['fallbacks']) == 9 and C.Counter(x['reason'] for x in summary['fallbacks']) == {'unmatched': 6, 'ambiguous': 3}
    assert r.protected() == p.load(d/'protected_inputs.json')
    result = dict(status='PASS', score_cells=checked_cells, independently_rebuilt_paired_intervals=paired_intervals,
                  baseline_lines=600, frozen_truth_preserved=True, protected_files=len(r.protected()),
                  delta_exclusion=True, matched_masks=441, fallbacks=9, report_sha256=p.sha(r.REPORT), receipt_sha256=p.sha(d/'receipt.json'))
    p.dump(d/'validation.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
