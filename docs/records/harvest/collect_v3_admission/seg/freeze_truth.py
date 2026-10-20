"""Freeze CP1 truth from existing local records; no detector, reader or publication."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'docs/harvest/collect_v3_admission'
SEG = BASE / 'seg'
COLLECT = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect'
RUN = Path.home() / 'Projects/collect-v3-data/run'

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def dump(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

C068 = 'gazette_modern--2e613d9290dd13d4--s000-l0209'
C068_RULING = "The card's verdict is a label error (label appends 'μένης αργίλλου' from the next line, which is only partly inside the crop). The neighbour word is clipped (token box 216–257×1233–1254 vs crop 217–715×1211–1249); under the owner's whole-word standard a clipped neighbour word is not a drop reason. Coordinator ruling 18 Oct."


def main():
    SEG.mkdir(exist_ok=True)
    sources = {}
    def bind(p):
        p = Path(p)
        key = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
        sources[key] = sha(p)
        return key
    brief = ROOT / 'docs/briefs/NW1b_neighbour_words_recalibrated.md'
    bind(brief)
    bind(ROOT / 'docs/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md')
    text = brief.read_text()
    keeps = re.findall(r'^- ([\w]+--[\w]+--s\d+-l\d+)$', text.split('**KEEP')[1].split('**BORDERLINE')[0], re.M)
    gallery_path = 'docs/harvest/collect_v3/segmentation_gallery/examples.jsonl'
    raw = subprocess.check_output(['git', 'show', '83aaab5d:' + gallery_path], cwd=COLLECT)
    gallery = [json.loads(l) for l in raw.splitlines()]
    merged = {r['line_id'] for r in gallery if r['type'] == 'merged_multi_line'}
    explicit = {'gazette_modern--0020420cfe156a73--s000-l' + n for n in ('0039','0138','0141','0162','0228')}
    explicit |= {'gazette_modern--1f7db88d63c02afa--s000-l0287', 'nlg--6146c0455e0103d2--s001-l0006'}
    drops = merged | explicit
    key_path = RUN / 'W1/c1/gazette_modern__modern_scanned__probe_1982_1985_key.json'
    key = json.loads(key_path.read_text()); bind(key_path)
    c1 = []
    for suffix in ('a', 'b'):
        vp = COLLECT / ('docs/harvest/collect_v3/c1/verdicts/gazette_modern__modern_scanned__probe_1982_1985__' + suffix + '.jsonl')
        bind(vp)
        for lineno, line in enumerate(vp.read_text().splitlines(), 1):
            v = json.loads(line)
            if 'merged_two_lines' in v['errors']:
                c1.append(dict(row_id=key[v['card_id']]['line_id'], card_id=v['card_id'], provenance=str(vp), line=lineno, detail=v['detail']))
    assert len(c1) == 7
    non_gating = [dict(c, classification='label-error witness, non-gating',
                       gating=False, reason=C068_RULING) for c in c1 if c['row_id'] == C068]
    assert len(non_gating) == 1 and non_gating[0]['card_id'] == 'c068'
    c1 = [c for c in c1 if c['row_id'] != C068]
    bind(ROOT / 'docs/briefs/SEG_CP4c_rulings.md')
    bind(Path(__file__))
    overrun = 'kosmopolis--62ca52b56ebe780a--s005-l0051'
    borderline = 'ia_poly1850--36dcee7ce4c29f8b--s004-l0032'
    ids = set(keeps) | drops | {r['row_id'] for r in c1} | {overrun, borderline, C068}
    mp = BASE / 'nw1b/measurements.jsonl'; bind(mp)
    measurements = {r['row_id']: r for r in map(json.loads, mp.read_text().splitlines())}
    builder_path = COLLECT / 'docs/harvest/collect_v3/release_admissions/build_w1_originals_v3.py'
    bind(builder_path)
    spec = importlib.util.spec_from_file_location('cp1_collector_builder', builder_path)
    builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
    rp = COLLECT / 'docs/harvest/collect_v3/release_exclusions/release_exclusions.json'
    bind(rp); registry = json.loads(rp.read_text())['classes']
    rotated_path = rp.parent / registry['rotated_crop']['file']; bind(rotated_path)
    rotated = set(rotated_path.read_text().split())
    fp = RUN / 'W1/features.jsonl'; bind(fp)
    features = {}; total = eligible = 0; pool_hash = hashlib.sha256()
    with fp.open() as f:
        for line in f:
            r = json.loads(line); total += 1
            included = builder.included(r)
            if included:
                eligible += 1
                pool_hash.update((r['id'] + '\n').encode())
            if r['id'] in ids:
                assert r['id'] not in features
                features[r['id']] = (r, included)
    assert set(features) == ids
    assert sha(fp) == sources[str(fp)], 'live source drifted; no lock taken'
    cases = []
    for rid in sorted(ids):
        r, included = features[rid]
        truth = 'keep' if rid in keeps else 'drop' if rid in drops else 'borderline' if rid == borderline else 'challenge' if rid in {c['row_id'] for c in c1} else 'diagnostic'
        if rid == C068: truth = 'label-error witness, non-gating'
        provenance = []
        if rid == C068: provenance.append(C068_RULING)
        if rid in keeps: provenance.append('NW1b brief section 2: explicit owner KEEP')
        if rid in explicit: provenance.append('NW1b brief section 2: named owner true issue')
        for g in gallery:
            if g['line_id'] == rid and rid in merged: provenance.append('83aaab5d gallery ' + g['id'] + ': ' + g['card_verdict_detail'])
        if truth == 'challenge': provenance.append('C1 verdict/key join; not the unidentified eighth owner issue')
        if truth == 'borderline': provenance.append('NW1b brief section 2: owner right-column borderline, nongating')
        if rid == overrun: provenance.append('CP1 owner-rule adjudication from pinned sg1-07: half-line-only evidence is not a required semantic DROP; no new owner KEEP verdict asserted')
        cases.append(dict(row_id=rid, truth=truth, provenance=provenance,
            pre_screen_eligible=included, crop_sha256=r.get('crop_sha256'),
            screen_merged=r.get('screen_merged'), rotated_crop=rid in rotated,
            measurement=measurements.get(rid, {}).get('measurement'),
            saved_measurement_status='available' if rid in measurements else 'unavailable; no CP1 detection',
            gallery=[g['id'] for g in gallery if g['line_id'] == rid]))
    g7 = next(g for g in gallery if g['line_id'] == overrun)
    ledger = dict(schema='SEG-CP1-truth-v1', sources=sources,
        owner_standard=['the important thing is that really there are no full words showing from the top or bottom line, and that we use the tools we have already built for it, and that we also avoid badly segmented horizontal ones as well',
                        'In general there has been at least a whole word from one of the other lines to show for it to be even worth considering for filtration'],
        gallery_binding=dict(repository=str(COLLECT), commit=subprocess.check_output(['git','rev-parse','83aaab5d'],cwd=COLLECT,text=True).strip(), path=gallery_path, sha256=hashlib.sha256(raw).hexdigest()),
        counts=dict(keep=22, required_drop=len(drops), named_owner_issues=7, borderline=1, c1=len(c1), gallery_merges=6),
        eighth_owner_issue=dict(status='unidentified', row_id=None, note='No uniquely identified eighth verdict in pinned manifest; c068 is a label-error witness, non-gating under the CP4c ruling.'),
        drop_adjudication=dict(prior_brief_directed_count=10, required_drop_count=9, removed_id=overrun, status='not_required_half_fragments',
            evidence=dict(gallery_id=g7['id'], type=g7['type'], detail=g7['card_verdict_detail']),
            reason='The saved semantic description says lower/upper halves only. Under the owner rule this does not establish a complete neighbour word or multiple complete rows. Historical screen_merged=true cannot validate itself. No new reading, owner verdict or KEEP label is invented.'),
        pre_screen_population=dict(builder=str(builder_path), predicate='included(r), before screen_merged, rotated_crop and class exclusions', feature_rows=total, eligible_rows=eligible, ordered_eligible_ids_sha256=pool_hash.hexdigest(), id_order='feature-file order', feature_source=str(fp)),
        c1_witnesses=sorted(c1,key=lambda r:r['card_id']),
        non_gating_witnesses=non_gating,
        gallery_witnesses=[dict(row_id=g['line_id'], gallery_id=g['id'], type=g['type'], detail=g['card_verdict_detail'], historical_screen_merged=g['screen_merged']) for g in gallery],
        cases=cases)
    assert len(keeps) == len(set(keeps)) == 22 and not set(keeps) & drops
    target = SEG / 'calibration_ledger.json'
    # Explicit coordinator-authorized re-freeze through the original builder.
    with target.open('w') as stream:
        stream.write(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(ledger['counts'])); print(json.dumps(ledger['pre_screen_population']))

if __name__ == '__main__': main()
