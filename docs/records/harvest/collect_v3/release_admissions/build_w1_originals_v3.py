"""ADM4 offline metadata admission. Never imports collector code or opens crop images."""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import hashlib
import json

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'release_admissions'
FEATURES = Path.home() / 'Projects/collect-v3-data/run/W1/features.jsonl'
EXCLUSIONS = BASE / 'release_exclusions/release_exclusions.json'
UNCHECKED = EXCLUSIONS.with_name('unchecked_strata.json')
MASKED = OUT / 'w1_masked_1d.jsonl'
OWNER_RULE = ('Owner decision, 17 Oct 2026 evening via coordinator: "forget the crop correction". '
              'On ORIGINAL collector crops, admission drops only crops containing two or more complete lines '
              '(screen_merged) and rotated crops (rotated_crop). Everything else is acceptable, overruns included. '
              'Apply no other crop screen; CAPS3 edge-clip screen is not applied. '
              'The specified stratum allowlist and every registered line-level exclusion class still apply; '
              'lqb_truth_v1_wave1d_in_sample_ids is not a class and is not removed.')
C1 = {('bsb_poly1850', 'poly1850'), ('ia_poly1850', 'poly1850'),
      ('nlg', 'poly1850'), ('nlg', 'poly1900'), ('nlg', 'greek_poly'),
      ('serbia', 'cyrillic'), ('elstat', 'numerics_tables')}
QUALIFIED = {('kosmopolis', 'poly1900'), ('lekythos', 'poly1900'), ('kosmopolis', 'poly1850')}
EXPECTED_MASKED_SHA = 'd9343b74c4eeb61b592257f25f63f9b624e7a83d3ddcb3971d8951998253d064'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def obj(p):
    return json.loads(Path(p).read_text())

def lines(p):
    return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]

def included(r):
    pair = (r['source'], r['primary_class'])
    return (r.get('candidate_usable') is True and
            (pair in C1 or pair in QUALIFIED or r['primary_class'] == 'headings_caps' or
             (pair == ('gazette_modern', 'modern_scanned') and
              r.get('gazette_stratum') == 'measured_1986_1990')))

def provenance(r):
    if r['primary_class'] == 'headings_caps':
        return {'evidence_commit': 'sol/recut-v1 abaa200c', 'evidence': 'CAPS4 letters; marks pending Opus',
                'crop_policy': 'ADM4 original; no CAPS3 edge screen'}
    if (r['source'], r['primary_class']) == ('kosmopolis', 'poly1850'):
        return {'evidence_commit': 'sol/recut-v1 87db4392', 'cards_commit': 'sol/recut-v1 72ae7114',
                'evidence': 'SRK/KR letters; marks pending Opus'}
    if (r['source'], r['primary_class']) in C1:
        return {'evidence_commit': 'sol/collect-v3 a62d089d1', 'evidence': 'C1 pass'}
    return {'evidence_commit': 'sol/recut-v1 7f70de90', 'build_commit': 'sol/recut-v1 63c640a3',
            'evidence': 'T6b masked qualification; ADM4 admits original crop'}

def compute():
    assert sha(MASKED) == EXPECTED_MASKED_SHA, 'historical masked file changed'
    registry = obj(EXCLUSIONS)['classes']
    inputs = {str(p): sha(p) for p in [FEATURES, EXCLUSIONS, UNCHECKED, MASKED]}
    sets = {}
    for name, entry in registry.items():
        p = EXCLUSIONS.parent / entry['file']
        inputs[str(p)] = sha(p)
        sets[name] = set(p.read_text().split())
    rotated = sets.pop('rotated_crop')
    class_union = set().union(*sets.values())
    pool = sorted((r for r in lines(FEATURES) if included(r)), key=lambda r: r['id'])
    assert len({r['id'] for r in pool}) == len(pool), 'duplicate candidate IDs'
    counts = defaultdict(Counter)
    removed = defaultdict(list)
    hits = defaultdict(list)
    per_class = defaultdict(Counter)
    out = []
    for r in pool:
        rid = r['id']
        key = r['source'] + '|' + r['primary_class']
        counts[key]['pool'] += 1
        reasons = []
        if r.get('screen_merged') is True: reasons.append('screen_merged')
        if rid in rotated: reasons.append('rotated_crop')
        if rid in class_union: reasons.append('classes')
        for reason in reasons:
            hits[reason].append(rid)
            counts[key]['hit_' + reason] += 1
        for name, ids in sets.items():
            if rid in ids: per_class[name][key] += 1
        if reasons:
            reason = reasons[0]  # deterministic, disjoint accounting
            removed[reason].append(rid)
            counts[key]['removed_' + reason] += 1
            continue
        counts[key]['rows'] += 1
        out.append(dict(row_id=rid, source=r['source'], primary_class=r['primary_class'],
                        gazette_stratum=r.get('gazette_stratum'), page_id=r['page_id'],
                        line_index=int(rid.rsplit('-l', 1)[1]), label=r['label'],
                        crop_bbox=r['crop_bbox'], crop_sha256=r['crop_sha256'], arm='release-v3',
                        crop='original', marks_status='pending_opus' if r['primary_class'] == 'headings_caps'
                        or (r['source'], r['primary_class']) == ('kosmopolis', 'poly1850') else 'recorded',
                        provenance=provenance(r)))
    data = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in out).encode()
    summary = dict(file='w1_originals_v3.jsonl', rows=len(out), pool=len(pool),
                   sha256=hashlib.sha256(data).hexdigest(), owner_rule=OWNER_RULE,
                   input_sha256=inputs, masked_file_sha256=EXPECTED_MASKED_SHA,
                   counts_per_source_class={k:dict(v) for k,v in sorted(counts.items())},
                   counts_per_stratum=dict(sorted(Counter('|'.join([r['source'], r['primary_class'], r.get('gazette_stratum') or '-']) for r in out).items())),
                   removals={k:len(removed[k]) for k in ['screen_merged','rotated_crop','classes']},
                   removal_order=['screen_merged','rotated_crop','classes'],
                   removal_accounting='Disjoint first-hit removals reconcile pool minus removals = rows; screen_hits includes overlaps.',
                   removed_row_ids={k:removed[k] for k in ['screen_merged','rotated_crop','classes']},
                   screen_hits={k:len(hits[k]) for k in ['screen_merged','rotated_crop','classes']},
                   screen_hit_row_ids={k:hits[k] for k in ['screen_merged','rotated_crop','classes']},
                   registered_class_hits_per_source_class={k:dict(v) for k,v in sorted(per_class.items())},
                   registered_line_classes=sorted(registry),
                   no_other_crop_screens=True, label_rule='W1 post-convention label unchanged')
    assert len(pool) - sum(summary['removals'].values()) == len(out)
    # Detect input drift during this non-locking, read-only snapshot.
    assert all(sha(p) == digest for p,digest in inputs.items())
    return data, summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    data, summary = compute()
    p = OUT / summary['file']
    sp = OUT / 'w1_originals_v3_summary.json'
    if args.check_only:
        assert p.read_bytes() == data
        assert obj(sp) == summary
    else:
        p.write_bytes(data)
        sp.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
        legacy = OUT / 'w1_masked_1d_summary.json'
        old = obj(legacy)
        old['superseded_for_admission_by'] = p.name
        old['owner_rule'] = OWNER_RULE
        legacy.write_text(json.dumps(old, ensure_ascii=False, indent=1) + '\n')
    assert sha(MASKED) == EXPECTED_MASKED_SHA
    print(json.dumps({k:summary[k] for k in ['rows','pool','removals','counts_per_stratum','sha256']}, indent=2))

if __name__ == '__main__':
    main()
