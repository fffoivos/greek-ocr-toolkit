"""Freeze all Greek-poly metadata, new C1 selection and the bounded 192-line mock."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import subprocess

from scripts.labelfix.clariden.l1_common import WAVES, canonical, label_sha, rows, sha256, write_json, write_rows
from scripts.labelfix.clariden.r1_common import check_disjointness, crop_key, transfer_record


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--train', type=Path, required=True)
    ap.add_argument('--c1-selection', type=Path, required=True)
    ap.add_argument('--instrument-alignments', type=Path, required=True)
    ap.add_argument('--r1', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    assert not list(a.out.iterdir()), 'prepare output must be empty'
    before = sha256(a.train)
    all_rows = list(rows(a.train))
    selected = [dict(r, crop=crop_key(r['crop'])) for r in all_rows if r['script_class'] == 'greek_poly']
    excluded_scope = Counter(r['script_class'] for r in all_rows if r['script_class'] != 'greek_poly')
    waves = Counter(r['wave'] for r in selected)
    assert len(selected) == 124669 and all(waves[w] == n for w, n in WAVES.items())
    assert waves == Counter(dict(WAVES, openarchives=235)), waves
    assert all(r['split'] == 'train' for r in selected)
    assert len({r['id'] for r in selected}) == len({r['crop'] for r in selected}) == len(selected)
    c1 = list(rows(a.c1_selection))
    bycrop = {r['crop']: r for r in selected}
    assert len(c1) == 91469
    for r in c1:
        assert r['id'] == bycrop[r['crop']]['id'] and r['label'] == bycrop[r['crop']]['label']
    c1_crops = {r['crop'] for r in c1}
    remaining = [r for r in selected if r['crop'] not in c1_crops]
    assert len(remaining) == 33200
    exclusions = json.loads(Path('artifacts/labelfix_r1/binding/exclusions.json').read_text())
    assert len(exclusions['sets']['heldout_14']['line_ids']) == 666
    assert len(exclusions['sets']['DEV_3']['documents']) == 3
    assert len(exclusions['sets']['summary_heldout_27']['documents']) == 27
    disjoint = check_disjointness(selected, exclusions)
    frozen = [r for r in rows('docs/labelfix/spellcheck/S4_lines.jsonl.gz') if not r['dev']]
    assert len(frozen) == 666
    assert not {r['id'] for r in selected} & {r['line_id'] for r in frozen}
    write_json(a.out / 'exclusions.json', exclusions)
    for name, values in [('selection.jsonl', selected), ('remaining_selection.jsonl', remaining)]:
        write_rows(a.out / name, values)
    documents = sorted({r['doc'] for r in selected})
    (a.out / 'L1_input_documents.txt').write_text(''.join(d + '\n' for d in documents))
    rng = random.Random(20261017)
    mock = []
    # All actual waves, split evenly between old C1 and the new C1 path.
    for old in (True, False):
        arm = []
        for wave in waves:
            candidates = [r for r in selected if r['wave'] == wave and (r['crop'] in c1_crops) == old]
            arm += rng.sample(candidates, min(13, len(candidates)))
        used_ids = {r['id'] for r in arm}
        candidates = [r for r in selected if (r['crop'] in c1_crops) == old and r['id'] not in used_ids]
        mock += arm + rng.sample(candidates, 80-len(arm))
    write_rows(a.out / 'mock_selection.jsonl', mock)
    write_rows(a.out / 'mock_remaining_selection.jsonl', [r for r in mock if r['crop'] not in c1_crops])
    cached = {crop_key(r['crop']): r['alignment'] for r in rows(a.instrument_alignments)}
    instruments = []
    for doc in sorted({r['doc'] for r in frozen}):
        instruments += rng.sample([r for r in frozen if r['doc'] == doc], 2)
    used = {r['line_id'] for r in instruments}
    instruments += rng.sample([r for r in frozen if r['line_id'] not in used], 32-len(instruments))
    parity = []
    for r in instruments:
        key = crop_key(r['crop'])
        alignment, _ = transfer_record(r['recogniser_text'], cached[key])
        parity.append(dict(id=r['line_id'], doc=r['doc'], crop=key, alignment=alignment,
                           mode='heldout_verification_only_NOT_L1_input'))
    write_rows(a.out / 'parity_selection.jsonl', parity)
    assert not {r['id'] for r in parity} & {r['id'] for r in selected}
    assert len(mock) + len(parity) == 192
    protected = (sorted(Path('greekocr').rglob('*.py')) +
        sorted(Path('scripts/labelfix/clariden').glob('*.py')) +
        [Path('scripts/labelfix/m2_run.py'), Path('scripts/labelfix/owner_reading.py')])
    diff = subprocess.check_output(['git', 'diff', 'efdf5756', '--', 'greekocr',
        'scripts/labelfix/m2_run.py', 'scripts/labelfix/agreement_mode.py'], text=True)
    assert not diff, 'S6 differs from efdf5756'
    checkpoint_sha = sha256(a.r1)
    assert checkpoint_sha.startswith('719a06')
    policy = dict(schema='l1-policy-v1', detector='s6', detector_commit='efdf5756',
        agreement='M2 combine: PRESENCE kinds; FULL sets; print-preserving K1; any HOLD drops line',
        label_policy='recogniser/original base letters and non-mark punctuation must match; detector apostrophe/quotes allowed',
        golden_reference='unchanged scripts/labelfix/m2_run.py infer_line',
        source_sha256={str(p): sha256(p) for p in protected},
        assets={p: sha256(p) for p in ['docs/labelfix/markshape_model_S4.json', 'docs/labelfix/case_model_S5.json']})
    write_json(a.out / 'policy.json', policy)
    binding = dict(schema='l1-binding-v1', detector='s6', detector_commit='efdf5756',
        code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        r1_sha256=checkpoint_sha, policy_sha256=sha256(a.out / 'policy.json'),
        c1_selection_sha256=sha256(a.c1_selection), source_sha256=before,
        c1_alignment_sha256='951122655bd25af553f48951af986bcd2be4f3a57f184beaf2a5923de08bb398',
        ctc_sha256='5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663',
        ctc_safetensors_sha256='e468155d6130be4b7359d94ec197a357ad55b0dc7947104afc1336c352a6c6df')
    write_json(a.out / 'binding.json', binding)
    receipt = dict(schema='l1-input-v1', source=str(a.train), source_sha256=before,
        train_rows=len(all_rows), greek_poly=len(selected), by_wave=dict(waves),
        coordinator_wave_count_note='The five listed waves total 124434; the input also has 235 greek_poly openarchives rows. All 124669 are included.',
        by_source=dict(Counter(r['source'] for r in selected)),
        out_of_scope=dict(statement='Only greek_poly train rows enter L1. greek_mono and all other script classes are out of scope.',
                          count=sum(excluded_scope.values()), counts_by_script_class=dict(excluded_scope)),
        exclusions=disjoint, exclusions_binding_sha256=sha256(a.out / 'exclusions.json'),
        c1_existing=len(c1), c1_remaining=len(remaining), input_documents=len(documents),
        input_documents_sha256=sha256(a.out / 'L1_input_documents.txt'),
        r0_policy='Locked R0 fresh-book set not drawn. R0 must draw only from documents outside L1_input_documents.txt and publish a zero-intersection receipt.',
        mock=dict(training=160, verification_only=32, total_distinct=192, c1_existing=80, c1_new=80),
        original_labels_unchanged=before == sha256(a.train))
    write_json(a.out / 'input_receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
