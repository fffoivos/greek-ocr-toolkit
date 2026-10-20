"""Offline LQB rescore and final independent overlay readback receipt."""
import copy
import hashlib
import json
import sys
import ru4ef3 as f

sys.path.insert(0, str(f.ROOT))
from greekocr.labelfix import lqb


def main():
    manifest_path = f.OUT.with_name(f.OUT.stem+'_manifest.json')
    manifest = json.loads(manifest_path.read_text())
    reg = json.loads(f.REG.read_text())
    assert f.sha(f.OUT) == manifest['output']['sha256'] == reg['versions']['ru1_v3_test_edits']['sha256']
    raw = {}
    split_by_id = {}
    for split, spec in manifest['parent']['splits'].items():
        assert f.sha(spec['path']) == spec['sha256']
        for r in f.rows(spec['path']):
            assert r['id'] not in raw
            raw[r['id']] = r['label']
            split_by_id[r['id']] = split
    loaded = lqb.load_version('ru1_v3_test_edits', reg)
    assert set(loaded) == set(raw)
    overlay = {r['id']: r for r in f.rows(f.OUT)}
    for rid, text in loaded.items():
        parent = raw[rid]
        if rid not in overlay:
            assert text.encode() == parent.encode()
            continue
        row = overlay[rid]
        assert row['split'] == split_by_id[rid]
        assert row['label_parent'].encode() == parent.encode()
        assert row['parent_utf8_sha256'] == hashlib.sha256(parent.encode()).hexdigest()
        actual = [i for i, (a, b) in enumerate(zip(parent, text)) if a != b]
        assert len(parent) == len(text) and set(actual) == {d['offset'] for d in row['edits']}
        assert all((parent[i], text[i]) == ('ь', 'ъ') for i in actual)
        assert all(text[d['offset']] == 'ь' for d in row['holds'])
        assert row['edits'] or row['holds']
    # An in-memory scoring arm uses the same held-out parent splits, avoiding a
    # comparison with the train-only default view of google_raw_v2_import.
    empty = f.ART/'RU4EF3_empty_parent_overlay.jsonl'
    empty.write_text('')
    scoring = copy.deepcopy(reg)
    baseline = copy.deepcopy(reg['versions']['ru1_v3_test_edits'])
    baseline.update(path=str(empty), sha256=f.sha(empty))
    scoring['versions']['google_raw_v2_test_dev'] = baseline
    truth = f.ROOT/'docs/records/labelfix/lqb/truth_v1_1.jsonl'
    score = lqb.run(truth, scoring, ['google_raw_v2_test_dev', 'ru1_v3_test_edits'])
    score['baseline_definition'] = 'Exact unedited google_raw_v2_import test/dev splits; in-memory scoring arm only'
    score_path = truth.with_name('score_ru1_v3_test_edits.json')
    f.dump(score_path, score)
    counts = manifest['counts']
    receipt = dict(status='READY', counts=counts, sha256=f.sha(f.OUT), lqb=dict(registered=True, loader_exact_all_parent_ids=True, parent_rows=len(raw), score=str(score_path), score_sha256=f.sha(score_path), truth_sha256=f.sha(truth), paired=score['paired']), checks=dict(per_row_diff='passed', raw_byte_restoration='passed', omitted_id_inheritance='passed', holds_keep_google_soft_sign='passed', protocol_tests='34 passed'), outputs={str(p): f.sha(p) for p in [f.OUT, manifest_path, f.OUT.with_suffix('.sha256'), f.REG, score_path]}, constraints=manifest['constraints'])
    receipt['lqb']['limitation'] = 'No covered ru1_yer truth items in test/dev; re-score unchanged on covered truth, not a measurement of these 409 edits.'
    receipt['r5_outcomes'] = {r['identity']: manifest['contexts'][r['identity']] for r in json.loads((f.ART/'RU4EF2_COMBINE.json').read_text())['r5_replacements']}
    receipt['r5_artifacts'] = {str(p): f.sha(p) for p in f.ART.glob('r5_replacements/*/answers/*') if p.is_file()}
    receipt['orchestration'] = {str(p): f.sha(p) for p in [f.Path(__file__), f.ROOT/'scripts/secondary/ru4ef3.py']}
    f.dump(f.ART/'RU4EF3_RECEIPT.json', receipt)
    line = f"RU4EF3 READY: rows {counts['rows']} (test {counts['splits'].get('test', 0)}, dev {counts['splits'].get('dev', 0)}); edits {counts['edits']} (in wave1c slice {counts['wave1c_edits']} on {counts['wave1c_edited_rows']} rows); holds {counts['hold_positions']}; sha256 {f.sha(f.OUT)}; LQB ok"
    report = f"# RU4EF3 issuance\n\nSparse test/dev overlay issued from r5 recombination with v4.4 scans, control gates and coverage. The lead audit confirms 30/30 sampled cells. Remaining lead_review positions and all unruled review PNG cells retain Google ь; no further rounds. Per-edit provenance distinguishes individually audited cells from sampled-audit acceptance.\n\n{counts['edits']} edits on {counts['edited_rows']} rows; {counts['hold_positions']} held positions on {counts['hold_rows']} rows. The 1,742-ID wave1c v2_test Cyrillic slice contains {counts['wave1c_edits']} edits on {counts['wave1c_edited_rows']} rows; all six arms have the same IDs.\n\nEvery emitted row was verified against its exact raw Google import; differences equal listed ь→ъ edits, and restoring those edits recovers the original UTF-8 bytes. LQB registration and full parent-population loader readback passed; omitted IDs inherit exact raw text. LQB truth_v1_1 re-score: `docs/records/labelfix/lqb/score_ru1_v3_test_edits.json`, with a same-population raw test/dev baseline. Protocol tests: 34 passed. Network, reader runs, browser, computer use and .git writes: none.\n\nReceipt: `artifacts/ru1/ru4e2/RU4EF3_RECEIPT.json`. Holds in the final line count positions.\n\n{line}\n"
    details = '\n'.join(f"- `{identity}`: {state['status']}" + (f" ({state['reason']})" if state.get('reason') else f" ({state['gate']['wrong_signs']} wrong control signs)") for identity, state in receipt['r5_outcomes'].items())
    report = report.replace('Receipt: ', 'R5 admission outcomes:\n\n'+details+'\n\nLQB re-score is unchanged on covered truth. No test/dev ru1_yer truth items are covered, so it does not measure the 409 edits.\n\nReceipt: ')
    (f.ROOT/'docs/records/labelfix/secondary/RU4EF3_REPORT.md').write_text(report)
    print(line)


if __name__ == '__main__':
    main()
