"""Offline accounting only. Reads receipts; never opens images or writes run roots."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import math
import subprocess

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'weak_ledger'
RUN = Path.home() / 'Projects/collect-v3-data/run'
PLAN = Path.home() / 'Projects/greek-page-ocr/docs/ocr_program_2026-10-06'
RECUT = Path.home() / 'Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked'
RU = Path.home() / 'Projects/greek-ocr-toolkit-secondary/artifacts/ru1'
inputs = {}

def path(p):
    p = Path(p)
    try:
        return str(p.relative_to(BASE.parents[2]))
    except ValueError:
        return str(p).replace(str(Path.home()), '~')

def read(p):
    p = Path(p)
    b = p.read_bytes()
    inputs[path(p)] = hashlib.sha256(b).hexdigest()
    return b.decode()

def obj(p):
    return json.loads(read(p))

def lines(p):
    return [json.loads(s) for s in read(p).splitlines() if s.strip()]

def fact(value, source, method=None):
    d = {'value': value, 'source': source if isinstance(source, list) else [path(source)]}
    if method:
        d['method'] = method
    return d

def missing(label, searched):
    return {'value': None, 'status': 'not found', 'field': label, 'paths_searched': [path(p) for p in searched]}

dp = PLAN / 'DATA_PLAN_v2_20261016.md'
sp = PLAN / 'SOURCING_T5_COLLECTION_PLAN_20261016.md'
e3 = PLAN / 'E3_RESULTS.md'
for p in [dp, sp, e3]:
    read(p)
fs = RUN / 'W1/features.jsonl'
gatep = BASE / 'release_exclusions/unchecked_strata.json'
gates = obj(gatep)['strata']
exp = BASE / 'release_exclusions/release_exclusions.json'
exclusions = obj(exp)
excluded_ids = set()
expaths = [path(exp)]
for entry in exclusions['classes'].values():
    p = exp.parent / entry['file']
    excluded_ids.update(s.strip() for s in read(p).splitlines() if s.strip())
    expaths.append(path(p))
features = lines(fs)
usable = [d for d in features if d.get('candidate_usable')]
gate = {(d['source'], d['primary_class'], d.get('gazette_stratum')): d['status'] for d in gates}
statusmap = {'c1_pass': 'passed', 'c1_pending': 'pending check', 'c1_fail': 'failed', 'unchecked': 'unchecked'}
admp = BASE / 'release_admissions/w1_masked_1d.jsonl'
admissions = lines(admp)
summary = obj(BASE / 'release_admissions/w1_masked_1d_summary.json')
c1p = BASE / 'c1/c1_results.json'
c1 = obj(c1p)
read(BASE / 'c1/C1_REPORT.md')
caps = obj(RECUT / 'caps3/results.json')
krp = RECUT / 'checks/kosmo_poly1850_sol/results.json'
kr = obj(krp)
rucp = RECUT / 'ruc1/results.json'
ruc = obj(rucp)
ruc_cards_p = RECUT / 'ruc1/scored_cards.jsonl'
ruc_cards = lines(ruc_cards_p)
ruc_errors = Counter(tag for card in ruc_cards if not card.get('control') for tag in card.get('errors', []))
rup = RU / 'decisions.summary.json'
ru = obj(rup)
w2p = RUN / 'W2/receipt.json'
w2 = obj(w2p)
assert not (RUN / 'W2/features.jsonl').exists(), 'W2 features appeared: update accounting before replacing fallback'
w1statep = RUN / 'W1/state.json'
w2statep = RUN / 'W2/state.json'
w1state, w2state = obj(w1statep), obj(w2statep)
manifestp = RUN / 'W2_manifest.jsonl'
manifest = lines(manifestp)
w1manifestp = RUN / 'W1_manifest.jsonl'
w1manifest = lines(w1manifestp)
gazette_pages = {d['id'] for d in w1manifest if d['source'] == 'gazette_modern' and d.get('gazette_stratum') == 'measured_1986_1990' and w1state['pages'].get(d['id']) == 'completed'}
read(RUN / 'W2_owner_go.json')
read(BASE / 'w2_gate/LAUNCH_RECEIPT_GAZETTE_20261017.md')
# Exact successful-page denominator, including pages with no surviving feature rows.
w1pages = Counter(k.split('--')[0] for k, v in w1state['pages'].items() if v == 'completed')
planned = Counter(d['source'] for d in manifest)
completed = Counter(d['source'] for d in manifest if w2state['pages'].get(d['id']) == 'completed')
terminal = Counter(d['source'] for d in manifest if w2state['pages'].get(d['id']) in ('completed', 'excluded'))
specs = [
 ('all-caps / headings', ['headings_caps'], 6000, 4.12,
  'Book front band 0–8% and newspaper mastheads (DATA_PLAN §3); T5 uses Gazette and Lekythos by-products. Dedicated front-band reads were never ordered in the supplied brief; no band-order receipt found.',
  'gazette_modern'),
 ('punctuation-heavy / dialogue', ['dialogue_fiction'], 12000, 3.25,
  'DATA_PLAN: novels/periodicals, Anemi, IA, Kosmopolis. T5: NLG, Kosmopolis, Lekythos, Gazette; Anemi excluded by T5. Dialogue is a collector proxy for punctuation-heavy, not identical.', 'gazette_modern'),
 ('dotted leaders', ['leaders_indices'], 4000, 2.97,
  'DATA_PLAN: contents/index bands 0–8% and 95–100%, new reads, plus R14-pattern reject candidates. T5 supersedes acquisition with factory synthetic only. Dedicated band reads never ordered per brief; no order receipt found.', None),
 ('numerics in lines', ['numerics_tables'], 10000, 2.71,
  'DATA_PLAN: historic Gazette, ELSTAT yearbooks, parliament budgets, NBS bank reports. T5: ELSTAT plus IA/Gazette by-products.', 'elstat'),
 ('Cyrillic', ['cyrillic'], 12000, 1.87,
  'DATA_PLAN: IA Russian/Bulgarian/Serbian, national libraries, NBS archive. T5: IA Russian and Serbia; IA Russian failed, RUC recheck also failed.', 'serbia'),
 ('mixed Greek+Latin', ['mixed_greek_latin'], 20000, 1.54,
  'DATA_PLAN: Persée BCH, e-rara, E-Periodica/Museum Helveticum, commentaries, LSJ, scientific journals. T5: IA Greek+Latin on crop hold; IA poly1850 mixed pending fresh rule/check.', 'ia_greek_latin'),
 ('polytonic 1850–1890', ['poly1850'], 40000, None,
  'DATA_PLAN: IA, BSB/MDZ, NLG newspapers, Kosmopolis/Pleias, Gennadius. T5: BSB, IA, NLG, Kosmopolis; no special page band. Collector poly1850 includes later dates; proxy gap is not an exact date-scoped gap.', 'bsb_poly1850'),
 ('polytonic 1900–1982', ['poly1900'], 50000, None,
  'DATA_PLAN: IA university scans, Pergamos, HathiTrust, BSB. T5: NLG, Kosmopolis, Lekythos; Gazette poly1900 dropped. No special page band.', 'lekythos'),
 ('monotonic / born-digital', ['greek_mono', 'modern_scanned'], 40000, 0.72,
  'Quota is DATA_PLAN modern scanned non-parliament, not a born-digital quota. DATA_PLAN: OA, Pergamos, Psifiothiki, Lekythos, ELSTAT/Bank of Greece, theses. T5: measured Gazette monotonic only; born-digital is a separate on-disk replay pool.', 'gazette_modern'),
]
t5pages = {'bsb_poly1850': 1000, 'ia_poly1850': 1600, 'ia_greek_latin': 1000,
           'ia_russian': 400, 'serbia': 300, 'nlg': 400, 'elstat': 60,
           'kosmopolis': 600, 'lekythos': 290, 'gazette_modern': 1200}
t5sources = [['gazette_modern','lekythos'], ['nlg','kosmopolis','lekythos','gazette_modern'], [],
             ['elstat','ia_poly1850','gazette_modern'], ['ia_russian','serbia'], ['ia_greek_latin'],
             ['bsb_poly1850','ia_poly1850','nlg','kosmopolis'], ['nlg','kosmopolis','lekythos'], ['gazette_modern']]
rows = []
byid = {d['id']: d for d in features}
for name, classes, quota, cer, sourcing, costsource in specs:
    pool = [d for d in usable if d['primary_class'] in classes]
    counts = defaultdict(Counter)
    for d in pool:
        counts[d['source']][statusmap[gate.get((d['source'], d['primary_class'], d.get('gazette_stratum')), 'unchecked')]] += 1
    collected = []
    for source, cnt in sorted(counts.items()):
        collected.append({'tranche': 'W1 original', 'source_name': source,
                          'counts': {s: fact(cnt[s], [path(fs), path(gatep)], 'candidate_usable, original stratum status; not release-certified') for s in statusmap.values()}})
    w2count = sum(w2['classes'].get(c, 0) for c in classes)
    # Receipt does not include rejected/by-product populations or source counts.
    w2entry = {'tranche': 'W2 main receipt', 'source_name': 'receipt aggregate; source split not found',
               'counts': {'passed': fact(w2count, w2p, 'usable_rows by listed class; inherited exploratory gate only'),
                          **{s: missing('W2 '+s+' population', [RUN/'W2/features.jsonl', w2p]) for s in ['pending check', 'failed', 'unchecked']}}}
    collected.append(w2entry)
    arms = defaultdict(Counter)
    for a in admissions:
        if a['primary_class'] in classes:
            arms[a['arm']][a['source']] += 1
    masked = [{'arm': arm, 'source_name': source, 'rows': fact(n, admp, 'group by exact arm/source/primary_class; overlaps W1, never add to original population')}
              for arm, cnt in sorted(arms.items()) for source, n in sorted(cnt.items())]
    qualified = {d['id'] for d in pool if gate.get((d['source'], d['primary_class'], d.get('gazette_stratum'))) == 'c1_pass'}
    qualified.update(a['row_id'] for a in admissions if a['primary_class'] in classes)
    excluded_qualified = len(qualified & excluded_ids)
    qualified -= excluded_ids
    gap = max(0, quota-len(qualified)-w2count)
    row = {'category': name, 'primary_classes': classes,
           'e3_cer_percent': fact(cer, e3, 'full seed-zero v2_test slice') if cer is not None else missing('exact period E3 CER', [e3, dp]),
           'plan_quota_rows': fact(quota, dp, '§3 disjoint usable train primary target'),
           'collected_by_source_status': collected, 'masked_by_arm_source': masked,
           'qualified_w1_union_rows': fact(len(qualified), [path(fs), path(gatep), path(admp)] + expaths, 'distinct original row IDs passing C1 or named masked arm minus all current line-level exclusion classes; arms combined for planning only'),
           'excluded_from_qualified_w1_rows': fact(excluded_qualified, [path(fs), path(gatep), path(admp)] + expaths, 'distinct qualified original IDs also listed in current line-level exclusions'),
           'gap_to_quota_proxy_rows': fact(gap, [path(dp), path(fs), path(gatep), path(admp), path(w2p)] + expaths, 'max(quota - qualified W1 ID union after current exclusions - W2 listed-class usable, 0); final dedupe/codec/spread/C2 and W2 exclusion audit pending; arms not a frozen release'),
           'source_and_page_band_reads': {'text': sourcing, 'source': [path(dp), path(sp)]},
           'pending_rows': [], 'correction': "see the spell-check lead's answer (pending)"}
    row['source_and_page_band_reads']['t5_planned_source_reads'] = [
        {'source_name': s, 'pages': fact(t5pages[s], sp, '§3 revised source allocation; shared across categories, never sum across ledger rows')}
        for s in t5sources[len(rows)]]
    if name == 'dotted leaders':
        row['e3_cer_percent']['method'] += '; ellipsis-triggered tag; DATA_PLAN says no true-leader test stratum'
    if name == 'monotonic / born-digital':
        row['born_digital_e3_instrument_cer_percent'] = fact(1.063, e3, 'e1_real_test full mean of two seeds, separate instrument, not category CER')
        row['born_digital_collected_rows'] = missing('born-digital release-v3 manifest count', [fs, admp, dp])
    if name.startswith('polytonic'):
        lo, hi = (1850, 1890) if '1850' in name else (1900, 1982)
        strict = sum(isinstance(d.get('year'), int) and lo <= d['year'] <= hi for d in pool)
        row['w1_exact_period_candidate_rows'] = fact(strict, fs, 'primary class plus inclusive category year bounds; all statuses')
        row['exact_period_gap_rows'] = missing('exact-period qualified gap: W2 dates absent', [RUN/'W2/features.jsonl', w2p])
        row['e3_context_only'] = {'text': 'E3 polytonic overall is not date-scoped; Vouli is a source slice, not the period category.',
                                 'overall_polytonic_cer_percent': fact(1.58, e3)}
    for source, label in [('bsb_poly1850', 'BSB'), ('gazette_modern', 'Gazette')]:
        n = sum(d['source'] == source and (label != 'Gazette' or d.get('gazette_stratum') == 'measured_1986_1990') for d in pool)
        denom = len(gazette_pages) if label == 'Gazette' else w1pages[source]
        remaining = planned[source] - terminal[source]
        row['pending_rows'].append({'source_name': label, 'status': 'pending',
            'activity': 'deferred; resumes 18 Oct per coordinator brief; state confirms MDZ cap defer' if label == 'BSB' else 'reading now; pending masked qualification/admission',
            'planned_w2_pages': fact(planned[source], manifestp, 'count source manifest records'),
            'unclosed_w2_pages': fact(remaining, [path(manifestp), path(w2statep)], 'planned less completed/excluded at snapshot'),
            'w1_candidate_rows': fact(n, fs, 'candidate_usable in mapped primary classes; Gazette restricted to measured stratum matching W2'),
            'w1_completed_pages': fact(denom, [path(w1statep), path(w1manifestp)], 'all successful source pages, including zero-row pages; Gazette measured stratum only'),
            'w1_yield_rows_per_page': fact(n/denom, [path(fs), path(w1statep), path(w1manifestp)], 'source/category candidates divided by completed matching-stratum pages'),
            'projected_pending_rows': fact(round(remaining*n/denom, 2), [path(fs), path(w1statep), path(w1manifestp), path(manifestp), path(w2statep)], 'unclosed pages × matching W1 candidate yield; forecast only, not admitted or subtracted from gap')})
    if costsource is not None:
        n = sum(d['source'] == costsource for d in pool)
        denom = w1pages[costsource]
        pages = math.ceil(gap*denom/n) if n else None
        row['cost_to_fill_proxy_gap'] = {'yield_source_name': costsource,
            'yield_rows_per_page': fact(n/denom, [path(fs), path(w1statep)], 'W1 mapped-category candidate yield; source hold/failure may prevent all admission'),
            'pages': fact(pages, [path(dp), path(fs), path(w1statep), path(gatep), path(admp), path(w2p)] + expaths, 'ceil(proxy gap / W1 source candidate yield)'),
            'usd': fact(round(pages*0.0015, 4), [path(dp), path(fs), path(w1statep), path(gatep), path(admp), path(w2p)] + expaths, 'pages × plan rate; read-cost arithmetic, not an order or qualified yield'),
            'rate_usd_per_page': fact(0.0015, dp, '§3 USD 1.50 per 1,000 pages'),
            'dedicated_band_yield': missing('dedicated page-band yield', [dp, sp, fs]) if name.startswith('all-caps') else 'not applicable'}
    else:
        row['cost_to_fill_proxy_gap'] = {'pages': missing('true-leader page-band yield/cost', [dp, sp, fs]), 'usd': missing('true-leader page-band yield/cost', [dp, sp, fs]), 'text': 'T5 factory synthetic only; no defensible read-page cost from ellipsis/proxy rows.'}
    faults = []
    for key, result in c1.items():
        if key.split('__')[1] not in classes:
            continue
        for tag in ['superscript', 'dash', 'separator', 'lunate_sigma', 'mark_errors']:
            events = result.get(tag, [])
            if events:
                faults.append({'stratum': key, 'tag': tag, 'cards': fact(len(events), c1p, 'number of recorded events/cards in tag list, not a population fault rate'), 'examples': events[:2]})
    if name == 'polytonic 1850–1890':
        faults.append({'tag': 'marks_bias:breathing_dropped', 'text': 'NLG poly1850; class-level evidence, not exact period adjudication.', 'source': [path(BASE/'c1/C1_REPORT.md')]})
        faults.append({'tag': 'KR/SRK2', 'error_types': {k: fact(v, krp, 'sample card error labels; overlapping, marks pending_opus') for k,v in kr['error_types'].items()}})
    if name == 'polytonic 1900–1982':
        faults.append({'tag': 'marks_bias:grave_to_acute', 'text': 'NLG poly1900 and Lekythos', 'source': [path(BASE/'c1/C1_REPORT.md')]})
    if name.startswith('all-caps'):
        faults.append({'tag': 'CAPS', 'text': 'Masked CAPS4: extra_mark, missing_mark, hyphen and punctuation; marks pending_opus. Original CAPS2 failed crop gate; masked CAPS4 passed. No new reading here.', 'source': [path(RECUT/'caps3/RESULTS.md'), path(RECUT/'caps1/RESULTS.md')]})
        read(RECUT/'caps3/RESULTS.md'); read(RECUT/'caps1/RESULTS.md')
    if name == 'Cyrillic':
        faults.extend([{'tag': 'RUC', 'text': 'Residual letter and crop failures after RU1; recheck gate fail, marks pending_opus.', 'source': [path(rucp)]},
          {'tag': 'RUC residual error classes', 'counts': {k: fact(v, ruc_cards_p, 'non-control sample cards carrying tag; overlapping labels, marks pending_opus') for k,v in sorted(ruc_errors.items())}},
          {'tag': 'RU1 residual decision classes', 'counts': {k: fact(v, rup, 'position decisions, NOT collected-row additions') for k,v in ru['counts'].items()},
           'text': 'Google final soft sign for printed hard sign; uncertain and yat positions remain held. Existing soft signs retained. Other residual letter/geometry errors stay under RUC failure.'}])
    row['google_label_faults'] = faults or [missing('category-specific Google fault check', [c1p, RECUT/'caps3/results.json', krp, rucp])]
    rows.append(row)

ledger = {'title': 'Weak-category ledger; owner steering page replacing RELEASE_V3_INPUTS.md',
          'scope': 'Offline receipt accounting; no OCR, visual reading, network, spend, locks, collector writes, staging or commit.',
          'mapping_policy': 'Map only primary classes as listed in each row; no secondary flags added. greek_poly is undated/unallocated; latin/nonletter are outside requested categories. poly1850 proxy includes dates outside owner period; strict period rows reported separately. Dialogue is not identical to punctuation-heavy. modern_scanned + greek_mono is a monotonic proxy, not born-digital acquisition.',
          'status_policy': 'W1 original passed/pending check/failed/unchecked from unchecked_strata. Masked arms are separate overlays and can rescue original failed/unchecked IDs; do not add populations. W2 receipt usable = inherited exploratory pass, final release checks pending. Null means not found, never zero. No pipeline or admission state changed.',
          'unallocated_w2_greek_poly_rows': fact(w2['classes']['greek_poly'], w2p, 'no dates; not assigned to either period'),
          'unallocated_w1_greek_poly_rows': fact(sum(d['primary_class'] == 'greek_poly' for d in usable), fs, 'generic primary class held outside the named period proxies; dates require separate qualification'),
          'w2_main_usable_rows': fact(w2['usable_rows'], w2p),
          'masked_arm_totals': {k: fact(v, admp, 'count exact arm across file') for k,v in Counter(a['arm'] for a in admissions).items()},
          'w2_by_source_missing': missing('main receipt source/class breakdown', [RUN/'W2/features.jsonl', w2p]),
          'bsb_resume_file_receipt': missing('18 Oct resume timestamp in a file; date supplied by coordinator brief', [w2statep, RUN/'W2_owner_go.json', sp]),
          'rows': rows, 'input_sha256': inputs}

def count_fields(d):
    numbers = absent = 0
    if isinstance(d, dict):
        if d.get('status') == 'not found':
            return 0, 1
        if isinstance(d.get('value'), (int, float)):
            assert d.get('source'), d
            return 1, 0
        for v in d.values():
            n,a = count_fields(v); numbers += n; absent += a
    elif isinstance(d, list):
        for v in d:
            n,a = count_fields(v); numbers += n; absent += a
    return numbers, absent

n, a = count_fields(ledger)
ledger['accounting'] = {'numbers_sourced': n, 'not_found': a, 'counting_rule': 'Numeric fact objects, including derived arithmetic, count once per field; not-found objects count once per field. Metadata, dates in labels, examples and hashes excluded.'}
(OUT/'ledger.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2)+'\n')

def render(v):
    if isinstance(v, dict):
        if v.get('status') == 'not found':
            return 'not found ('+v['field']+')<br><small>Searched: '+ '; '.join('`'+s+'`' for s in v['paths_searched'])+'</small>'
        if 'value' in v:
            val = f"{v['value']:,}" if isinstance(v['value'], int) else str(round(v['value'], 4))
            return val+'<br><small>'+ '; '.join('`'+s+'`' for s in v['source'])+ ('; '+v['method'] if v.get('method') else '')+'</small>'
        return '<br>'.join(k.replace('_',' ')+': '+render(x) for k,x in v.items())
    if isinstance(v, list):
        return '<br><br>'.join(render(x) for x in v)
    return str(v).replace('|', '&#124;').replace('\n', ' ')

md = ['# Weak-category ledger', '', ledger['scope'], '', ledger['mapping_policy'], '', ledger['status_policy'], '',
      'The gaps below are **planning proxies**, not certified release deficits. They exclude pending BSB/Gazette forecasts, combine the named masked arms by original row ID, subtract current W1 line-level exclusions, and precede final deduplication, codec, spread, W2 exclusion audit and release assurance. Exact period gaps cannot be certified from the W2 aggregate receipt. Page costs extrapolate candidate yields, not admission yields; failed or held sources need qualification before those estimates can become orders.', '',
      'The E3 leaders figure measures an ellipsis-triggered tag, not true leaders. The monotonic quota belongs to scanned non-parliament material; born-digital has no separate quota in the targeted table. Dedicated caps/leader bands originate in DATA_PLAN, while the later T5 plan uses by-products and synthetic leaders. No dedicated band-order evidence was found in the inspected manifests.', '',
      '| Weak category / mapping | E3 CER (%) | Plan quota (rows) | Collected by source: passed / pending check / failed / unchecked | Masked overlays by exact arm | Pending BSB / Gazette | Gap to quota | Named sources / bands; pages and USD to fill | Google label faults / tags | Correction |',
      '|---|---|---|---|---|---|---|---|---|---|']
for r in rows:
    gapcell = render(r['gap_to_quota_proxy_rows'])+'<br>Qualified W1 ID union after exclusions: '+render(r['qualified_w1_union_rows'])+'<br>Current excluded IDs removed: '+render(r['excluded_from_qualified_w1_rows'])
    if 'exact_period_gap_rows' in r:
        gapcell += '<br>'+render(r['exact_period_gap_rows'])+'<br>W1 exact-period candidates: '+render(r['w1_exact_period_candidate_rows'])
    cercell = render(r['e3_cer_percent'])
    if 'e3_context_only' in r: cercell += '<br>'+render(r['e3_context_only'])
    if 'born_digital_e3_instrument_cer_percent' in r: cercell += '<br>Born-digital instrument: '+render(r['born_digital_e3_instrument_cer_percent'])+'<br>Born-digital collected: '+render(r['born_digital_collected_rows'])
    cells = [r['category']+'<br>'+', '.join('`'+c+'`' for c in r['primary_classes']), cercell, render(r['plan_quota_rows']), render(r['collected_by_source_status']), render(r['masked_by_arm_source']) or 'No mapped rows in admission file (see source file).', render(r['pending_rows']), gapcell, render(r['source_and_page_band_reads'])+'<br>'+render(r['cost_to_fill_proxy_gap']), render(r['google_label_faults']), r['correction']]
    md.append('| '+' | '.join(cells)+' |')
md += ['', 'Receipt qualifications and unallocated counts:', '',
       render({k:ledger[k] for k in ['w2_main_usable_rows','unallocated_w1_greek_poly_rows','unallocated_w2_greek_poly_rows','masked_arm_totals','w2_by_source_missing','bsb_resume_file_receipt']}), '',
       'All source files are hash-bound in `weak_ledger/ledger.json`. This is a non-locking snapshot: the live Gazette state can advance immediately. The W2 receipt fallback is the completed main-run receipt and does not credit the live Gazette rows. Original W1 failures remain visible even where a separate masked arm qualifies. Check-based fault counts are overlapping sample tags, never estimates of faulty collected rows. RU1 position decisions are not additional rows. Marks from CAPS/KR/RUC remain pending Opus.', '',
       'How to update: see [weak_ledger/UPDATE.md](weak_ledger/UPDATE.md). Guarded commit paths: [weak_ledger/WCL1_COMMIT_FILES.txt](weak_ledger/WCL1_COMMIT_FILES.txt); bindings and staging conditions: [weak_ledger/WCL1_COMMIT_GUARD.json](weak_ledger/WCL1_COMMIT_GUARD.json).', '',
       f'Accounting: {n} numeric fact fields sourced; {a} explicit not-found fields. Repeated display occurrences are not counted again. Derived figures retain their input paths and formulas in JSON.', '',
       f'WCL1: done | categories: 9 | numbers sourced: {n} | not found: {a} | pending rows marked: BSB, Gazette']
(BASE/'WEAK_CATEGORY_LEDGER.md').write_text('\n'.join(md)+'\n')

files = ['docs/harvest/collect_v3/WEAK_CATEGORY_LEDGER.md'] + ['docs/harvest/collect_v3/weak_ledger/'+f for f in ['build_ledger.py','ledger.json','UPDATE.md','WCL1_COMMIT_FILES.txt','WCL1_COMMIT_GUARD.json']]
(OUT/'WCL1_COMMIT_FILES.txt').write_text('\n'.join(files)+'\n')
guard = {'head': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
         'branch': subprocess.check_output(['git','branch','--show-current'], text=True).strip(),
         'conditions': ['No staging or commit performed.', 'Require unchanged HEAD and branch and empty index.', 'Verify all output and input hashes; stop on drift. Live run inputs may advance: review or regenerate instead of bypassing guard.', 'Stage only exact list; verify staged path set equals list. Never git add -A; preserve unrelated changes. Guard/list excluded from their own hash set.'],
         'input_sha256': inputs,
         'output_sha256': {f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files if not f.endswith(('WCL1_COMMIT_FILES.txt','WCL1_COMMIT_GUARD.json'))}}
(OUT/'WCL1_COMMIT_GUARD.json').write_text(json.dumps(guard, indent=2)+'\n')
print(md[-1])
