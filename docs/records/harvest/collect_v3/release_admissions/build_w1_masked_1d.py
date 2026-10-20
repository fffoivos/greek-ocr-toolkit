"""Build docs/harvest/collect_v3/release_admissions/w1_masked_1d.jsonl (prep only; wave 1d is the owner's decision)."""
import collections, hashlib, json, os, subprocess
from pathlib import Path

HOME = Path.home()
RUN = HOME / 'Projects/collect-v3-data/run'
RECUT = HOME / 'Projects/greek-ocr-toolkit-sol-recut'
W = RECUT / 'docs/harvest/recut_v1/w1_masked'
REPO = HOME / 'Projects/greek-ocr-toolkit-sol-collect'
OUT = REPO / 'docs/harvest/collect_v3/release_admissions'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

ADMIT = {('gazette_modern', 'modern_scanned', 'measured_1986_1990'), ('kosmopolis', 'poly1900', None), ('lekythos', 'poly1900', None)}
rot_ids = set((REPO / 'docs/harvest/collect_v3/release_exclusions/w1_rotated_crop_ids.txt').read_text().split())
excl = json.loads((REPO / 'docs/harvest/collect_v3/release_exclusions/release_exclusions.json').read_text())
line_excluded = set()
for cls, v in excl['classes'].items():
    f = REPO / 'docs/harvest/collect_v3/release_exclusions' / v['file']
    if f.exists(): line_excluded |= set(f.read_text().split())

rows = {}
for l in open(RUN / 'W1/crop_tight_page.jsonl'):
    r = json.loads(l)
    if r['source'] in ('gazette_modern', 'kosmopolis', 'lekythos'): rows[r['id']] = r
recs = {}
for s in ('gazette_modern', 'kosmopolis', 'lekythos'):
    for l in open(W / s / 'records.jsonl'):
        x = json.loads(l); recs[x['id']] = x

counts = collections.Counter(); out = []
for rid, r in sorted(rows.items()):
    s = r['source']; st = r.get('gazette_stratum') if s == 'gazette_modern' else None
    def drop(reason): counts[(s, reason)] += 1
    if r.get('screen_merged'): drop('screen_merged'); continue
    if rid in rot_ids: drop('rotated_crop'); continue
    if rid in line_excluded: drop('release_exclusions_line_class'); continue
    x = recs.get(rid)
    if x is None: drop('not_in_t6b_eligible (caps/heading or earlier exclusion)'); continue
    if (s, r['primary_class'], st) not in ADMIT:
        drop('unchecked_class_or_failed_stratum:' + r['primary_class'] + (':' + st if st else '')); continue
    kind = x.get('output_kind')
    if kind not in ('masked', 'guarded_original'): drop('output_kind:' + str(kind)); continue
    crop = W / x['masked_crop']  # guarded rows: T6b stores a byte-exact copy of the original here
    if not crop.exists(): drop('crop_file_missing'); continue
    csha = sha(crop)
    want = x['masked_crop_sha256'] if kind == 'masked' else x['original_crop_sha256']
    assert csha == want, (rid, kind)
    assert x['original_crop_sha256'] == r['crop_sha256'], ('collector crop hash mismatch', rid)
    out.append(dict(row_id=rid, source=s, primary_class=r['primary_class'], gazette_stratum=st, page_id=r['page_id'],
        line_index=int(rid.rsplit('-l', 1)[1]), tranche='W1', label=r['label'],
        crop=str(crop), crop_sha256=csha, original_crop_sha256=x['original_crop_sha256'],
        guard_status='masked' if kind == 'masked' else 'guarded_original', wrong_line_risk=bool(x.get('wrong_line_risk')),
        crop_masked_tag='crop_masked' if kind == 'masked' else None, arm='wave-1d only',
        provenance=dict(t6b_commit='sol/recut-v1 63c640a3', t6b_checks_commit='sol/recut-v1 7f70de90',
                        params_sha256=x.get('params_sha256', '801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8'))))
    counts[(s, 'admitted:' + r['primary_class'])] += 1

OUT.mkdir(parents=True, exist_ok=True)
p = OUT / 'w1_masked_1d.jsonl'
p.write_text(''.join(json.dumps(o, ensure_ascii=False) + '\n' for o in out))
checks = W / 'checks/t6b_results.json'
summary = dict(file=p.name, rows=len(out), sha256=sha(p), status='prep only; wave 1d admission is the owner decision',
    w1_features_sha256=sha(RUN / 'W1/features.jsonl'), crop_tight_page_sha256=sha(RUN / 'W1/crop_tight_page.jsonl'),
    t6b_check_results_sha256=sha(checks), release_exclusions_sha256=sha(REPO / 'docs/harvest/collect_v3/release_exclusions/release_exclusions.json'),
    admitted_strata=sorted(['/'.join(x for x in k if x) for k in ADMIT]),
    validation=['every admitted row exists in W1 crop_tight_page.jsonl (candidate_usable) under its collector row id',
                'original_crop_sha256 equals the collector crop_sha256 for that row',
                'crop file on disk hashes to the T6b masked (or original, for guarded) sha256'],
    counts={f'{s}|{k}': v for (s, k), v in sorted(counts.items())},
    label_rule_gaps=['dropped line-end hyphen not caught by dropped_line_end_hyphen (3/30 probe-supplement cards)',
                     'skewed multi-line crops missed by screen_merged (3/30 probe-supplement cards)'])
(OUT / 'w1_masked_1d_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1) + '\n')
print(json.dumps(summary['counts'], indent=0)); print(len(out))
