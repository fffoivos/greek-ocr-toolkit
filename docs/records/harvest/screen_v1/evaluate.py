"""Reporting and held-out evaluation for the offline T4b screen."""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random
import re
import unicodedata as ud
import numpy as np
from screen import OUT, ROOT, TRACKS, SEED, rows, write_rows, write_json, sha, reject, positive, confusion
from conventions import apply_conventions, ROMAN_TABLE

# Twenty actual interleave witnesses. The requested 7/4/3/3/3 distribution
# cannot be reproduced: ELSTAT has two duplicate verdicts, plus two other n's.
CORE = {
    'openarchives': ['c014', 'c015', 'c025', 'c026', 'c028', 'c036', 'c040'],
    'elstat': ['c026', 'c030'],
    'government-gazette': ['c014', 'c026', 'c030', 'c035'],
    'pleias': ['c014', 'c019', 'c040'],
    'anemi': ['c005', 'c025', 'c032', 'c033'],
}


def wilson(y, n):
    if not n:
        return dict(y=y, n=n, rate=None, low=None, high=None)
    z = 1.959963984540054
    p = y/n
    d = 1+z*z/n
    center = (p+z*z/(2*n))/d
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return dict(y=y, n=n, rate=p, low=center-half, high=center+half)


def accuracy(cards, field='letters_fixed'):
    vals = [c[field] for c in cards]
    out = wilson(vals.count('y'), len(vals))
    out['unknown'] = vals.count('u')
    return out


def marks(cards):
    vals = [c['marks'] for c in cards]
    out = wilson(vals.count('y'), vals.count('y')+vals.count('n'))
    out['na'] = vals.count('na')
    return out


def fmt(a):
    if a['rate'] is None:
        return 'unmeasured (0)'
    return f"{100*a['rate']:.1f}% ({a['y']}/{a['n']}; {100*a['low']:.1f}–{100*a['high']:.1f})"


def bootstrap(values, name):
    values = np.asarray(values, float)
    if not len(values):
        return dict(pages=0, rows=0, mean=None, low=None, high=None)
    rng = np.random.default_rng(int.from_bytes(__import__('hashlib').sha256((str(SEED)+name).encode()).digest()[:8], 'big'))
    boot = values[rng.integers(0, len(values), size=(5000, len(values)))].mean(axis=1)
    return dict(pages=len(values), rows=int(values.sum()), mean=float(values.mean()),
                low=float(np.quantile(boot, .025)), high=float(np.quantile(boot, .975)))


def f_rate(r):
    return 'unmeasured' if r['mean'] is None else f"{r['mean']:.2f} [{r['low']:.2f}, {r['high']:.2f}]"


def run():
    features = rows(OUT/'receipts/base_features.jsonl')
    byid = {r['id']: r for r in features}
    cards = rows(OUT/'receipts/split.jsonl')
    reviews = {(r['track'], r['source'], r['card_id']): r for r in rows(OUT/'receipts/assembly_review.jsonl')}
    model_path = OUT/'receipts/model.json'
    model = json.loads(model_path.read_text())
    model_hash = sha(model_path)
    for r in features:
        # Do not promote previously rejected F2 rows. Apply a deletion-induced
        # short/symbol-heavy check while retaining all original F2 gate flags.
        base = ''.join(c for c in ud.normalize('NFD', r['fixed_label']) if not ud.category(c).startswith('M'))
        letters = sum(c.isalpha() for c in base)
        nonspace = sum(not c.isspace() for c in base)
        exempt = bool(set(r['tags']) & {'caps', 'numeric', 'leaders'})
        fixed_pass = not r['assembly_changed'] or (bool(r['fixed_label']) and (exempt or (letters >= 10 and 3*(nonspace-letters) <= nonspace)))
        r['fixed_text_gate_pass'] = fixed_pass
        r['fixed_usable'] = r['original_usable'] and fixed_pass
        r['screen_reject'] = reject(r, model)
        r['screen_decision'] = 'reject_crop' if r['screen_reject'] else 'keep_crop'
        r['screen_reasons'] = [b for b in model['branches'] if all(r[k] > v for k, v in b.items())]
        r['usable_after_screen'] = r['fixed_usable'] and not r['screen_reject']
        if r['source'] == 'wikisource_ru':
            r['tags'].append('reference_only_no_training_supply')
    for c in cards:
        r = byid[c['id']]
        review = reviews.get((c['track'], c['source'], c['card_id']))
        c.update(old_label=r['old_label'], fixed_label=r['fixed_label'], page_id=r['page_id'],
                 primary_class=r['primary_class'], year=r['year'],
                 original_usable=r['original_usable'], fixed_usable=r['fixed_usable'],
                 assembly_changed=r['assembly_changed'], letters_fixed=c['letters'],
                 screen_reject=r['screen_reject'], usable_after_screen=r['usable_after_screen'],
                 positive_specified=positive(c), model_sha256=model_hash,
                 adjudication='unchanged blind verdict')
        if review:
            c['letters_fixed'] = review['letters_fixed']
            c['adjudication'] = review['reason']
            c['matches_printed_base'] = review.get('matches_printed_base')
            c['matches_printed_literal'] = review.get('matches_printed_literal')
        elif r['assembly_changed']:
            # Conservative: unreviewed changes to a previously correct card
            # cannot silently retain a correctness claim.
            c['letters_fixed'] = 'u' if c['letters'] == 'y' else c['letters']
            c['adjudication'] = 'changed; not manually adjudicated; conservative unknown'
        c['positive_residual'] = c['positive_specified'] and c['letters_fixed'] != 'y'
    stats = []
    groups = sorted({(r['track'], r['source']) for r in features})
    for track, source in groups:
        rr = [r for r in features if (r['track'], r['source']) == (track, source)]
        cc = [c for c in cards if (c['track'], c['source']) == (track, source)]
        test = [c for c in cc if c['split'] == 'test']
        usable_test = [c for c in test if c['original_usable']]
        surviving_test = [c for c in test if c['usable_after_screen']]
        surviving_all = [c for c in cc if c['usable_after_screen']]
        markstats = marks(surviving_all)
        fullmarkstats = marks(cc)
        ispoly = track == 'gr' or (track == 'ia' and source in {'poly1850', 'poly1900', 'greek_latin'}) or (track == 'intl' and source == 'bsb')
        # Retain the source-level weak-marks evidence from all 40 cards. A tiny
        # selected denominator (e.g. 1/1) does not withdraw that known defect.
        marktag = ispoly and any(m['rate'] is not None and m['rate'] < .90 for m in [markstats, fullmarkstats])
        for r in rr:
            if marktag:
                r['tags'].append('marks_correction_required')
            if ispoly and markstats['rate'] is None:
                r['tags'].append('marks_unmeasured')
        original = sum(r['original_usable'] for r in rr)
        after = sum(r['usable_after_screen'] for r in rr)
        stats.append(dict(track=track, source=source, cards=len(cc), original_usable=original,
                          after_screen=after, removed_fix_gate=sum(r['original_usable'] and not r['fixed_usable'] for r in rr),
                          removed_screen=sum(r['fixed_usable'] and r['screen_reject'] for r in rr),
                          removed_share=(original-after)/original if original else None,
                          letters_before_test=accuracy(usable_test, 'letters'),
                          letters_before_all=accuracy([c for c in cc if c['original_usable']], 'letters'),
                          letters_fixed_all=accuracy([c for c in cc if c['fixed_usable']]),
                          letters_fixed_test=accuracy([c for c in test if c['fixed_usable']]),
                          letters_after_test=accuracy(surviving_test),
                          letters_after_all=accuracy(surviving_all),
                          marks_after_all=markstats, marks_after_test=marks(surviving_test),
                          marks_blind_all_40=fullmarkstats,
                          marks_before_all=marks([c for c in cc if c['original_usable']]),
                          marks_correction_required=marktag, polytonic=ispoly,
                          test=confusion([c['positive_specified'] for c in test], [c['screen_reject'] for c in test]),
                          residual_test=confusion([c['positive_residual'] for c in test], [c['screen_reject'] for c in test]),
                          residual_errors=Counter(e for c in surviving_all if c['letters_fixed'] != 'y' for e in c['errors'])))
    apply_conventions(features)
    conventions = []
    for s in stats:
        rr = [r for r in features if (r['track'], r['source']) == (s['track'], s['source'])]
        cc = [c for c in cards if (c['track'], c['source']) == (s['track'], s['source'])]
        surviving = [r for r in rr if r['usable_after_screen']]
        orig = [r for r in rr if r['original_usable']]
        for r in rr:
            r['usable_final'] = r['usable_after_screen'] and not r['text_exclusions']
            r['training_usable_final'] = r['usable_final'] and r['source'] != 'wikisource_ru'
            r['tags'].extend(r['text_exclusions'])
            if r['roman_fixes']:
                r['tags'].append('roman_lookalike_normalized')
            if r['long_s_label_count']:
                r['tags'].append('long_s_glyph_variant_accepted')
            r['tags'] = sorted(set(r['tags']))
        s['after_conventions'] = sum(r['usable_final'] for r in rr)
        s['final_removed_share'] = (s['original_usable']-s['after_conventions'])/s['original_usable'] if s['original_usable'] else None
        # Known substitutions are evidence in the blind detail, never guessed
        # from ordinary hyphens in unreviewed labels.
        dash = [c for c in cc if re.search(r'—[^;]*→[^;]*-', c['detail'])]
        long_s = [c for c in cc if 'ſ' in c['detail']]
        conventions.append(dict(track=s['track'], source=s['source'], usable_scanned=len(surviving),
            original_usable_scanned=len(orig),
            roman_fixed_lines=sum(bool(r['roman_fixes']) and not r['roman_ambiguous'] for r in surviving),
            roman_fixed_tokens=sum(len(r['roman_fixes']) for r in surviving if not r['roman_ambiguous']),
            roman_fix_and_exclusion_overlap_lines=sum(bool(r['roman_fixes']) and bool(r['roman_ambiguous']) for r in surviving),
            roman_excluded_lines=sum(bool(r['roman_ambiguous']) for r in surviving),
            dropped_hyphen_excluded_lines=sum('dropped_line_end_hyphen' in r['text_exclusions'] for r in surviving),
            lowercase_fragment_unknown=sum(r['hyphen_test'] == 'lowercase_continuation_fragment_unknown' for r in surviving),
            long_s_label_lines=sum(bool(r['long_s_label_count']) for r in surviving),
            long_s_blind_witnesses=[c['card_id'] for c in long_s],
            long_s_visual_witnesses=['c008'] if s['track'] == 'intl' and s['source'] == 'bsb' else [],
            long_s_visual_surviving=[c['card_id'] for c in cc if c['card_id']=='c008' and s['track']=='intl' and s['source']=='bsb' and c['usable_after_screen']],
            printed_long_s_all_lines='not determinable from normalized labels; incomplete visual witnesses only',
            emdash_to_hyphen_blind_all=len(dash),
            emdash_to_hyphen_blind_surviving=sum(c['usable_after_screen'] for c in dash),
            emdash_to_hyphen_card_ids=[c['card_id'] for c in dash],
            label_has_hyphen_lines=sum('-' in r['fixed_label'] for r in surviving),
            original_roman_fixed_lines=sum(bool(r['roman_fixes']) and not r['roman_ambiguous'] for r in orig),
            original_roman_excluded_lines=sum(bool(r['roman_ambiguous']) for r in orig),
            original_dropped_hyphen_excluded_lines=sum('dropped_line_end_hyphen' in r['text_exclusions'] for r in orig)))
    for c in cards:
        r = byid[c['id']]
        c.update(usable_final=r['usable_final'], label_after_conventions=r['label_after_conventions'], tags=r['tags'])
    for s in stats:
        cc = [c for c in cards if c['track']==s['track'] and c['source']==s['source'] and c['usable_final']]
        s['letters_final_all'] = accuracy(cc)
        s['letters_final_test'] = accuracy([c for c in cc if c['split']=='test'])
        s['residual_errors_final'] = Counter(e for c in cc if c['letters_fixed']!='y' for e in c['errors'])
    rates = []
    for track, base in TRACKS.items():
        pages = rows(base/'pages.jsonl')
        successful = []
        for page in pages:
            p = base/'google/parsed/docai'/f"{page['image_sha256']}.json"
            if p.exists() and json.loads(p.read_text()).get('status') == 'ok':
                successful.append(page)
        for source in sorted({p['source'] for p in pages}):
            pp = [p for p in successful if p['source'] == source]
            rr = [r for r in features if r['track'] == track and r['source'] == source]
            classes = sorted({r['primary_class'] for r in rr})
            for period in [None]+sorted({p.get('period') for p in pp if p.get('period')}):
                pids = [p['id'] for p in pp if period is None or p.get('period') == period]
                for target in ['ALL']+classes:
                    counts = Counter(r['page_id'] for r in rr if r['usable_after_screen'] and (target == 'ALL' or r['primary_class'] == target))
                    finalcounts = Counter(r['page_id'] for r in rr if r['usable_final'] and (target == 'ALL' or r['primary_class'] == target))
                    rates.append(dict(track=track, source=source, period=period, primary_class=target,
                        after_screen=bootstrap([counts[p] for p in pids], f'{track}/{source}/{period}/{target}:screen'),
                        final=bootstrap([finalcounts[p] for p in pids], f'{track}/{source}/{period}/{target}:final')))
    test = [c for c in cards if c['split'] == 'test']
    primary = confusion([c['positive_specified'] for c in test], [c['screen_reject'] for c in test])
    residual = confusion([c['positive_residual'] for c in test], [c['screen_reject'] for c in test])
    physical = confusion([bool(set(c['errors']) & {'merged_two_lines', 'crop_overrun'}) for c in test], [c['screen_reject'] for c in test])
    primary['precision_wilson'] = wilson(primary['tp'], primary['tp']+primary['fp'])
    primary['recall_wilson'] = wilson(primary['tp'], primary['tp']+primary['fn'])
    totals = dict(lines=len(features), original_usable=sum(r['original_usable'] for r in features),
                  after_screen=sum(r['usable_after_screen'] for r in features),
                  after_conventions=sum(r['usable_final'] for r in features),
                  training_after_conventions=sum(r['training_usable_final'] for r in features),
                  changed_lines=sum(r['assembly_changed'] for r in features),
                  changed_pages=len({(r['track'], r['page_id']) for r in features if r['assembly_changed']}))
    write_rows(OUT/'features.jsonl', features)
    write_rows(OUT/'card_eval.jsonl', cards)
    write_json(OUT/'receipts/statistics.json', dict(sources=stats, test_primary=primary, test_residual=residual,
               test_physical_diagnostic=physical, totals=totals, model_sha256=model_hash))
    write_rows(OUT/'receipts/page_rates.jsonl', rates)
    write_rows(OUT/'receipts/convention_counts.jsonl', conventions)
    lek = {c['card_id']: c for c in cards if c['track']=='gr' and c['source']=='lekythos'}
    mark_cases = [
        ('grave_to_acute', 'c012', 'καθηγητὴς', 'καθηγητής'),
        ('grave_to_acute', 'c027', 'Τιμποὺκ', 'Τιμπούκ'),
        ('grave_to_acute', 'c034', 'μερικὰ', 'μερικά'),
        ('circumflex_to_acute', 'c012', 'διοριστεῖ', 'διοριστεί'),
        ('circumflex_to_acute', 'c022', 'γνῶστες', 'γνώστες'),
        ('breathing_dropped', 'c017', 'Ὡστόσο', 'Ωστόσο'),
        ('breathing_dropped', 'c033', '῎Αν', '"Αν'),
        ('accent_dropped', 'c009', 'τὶς', 'τις'),
        ('accent_dropped', 'c036', 'στὴ', 'στη'),
        ('mark_with_base_letter_error', 'c004', 'κριτικὸς', 'κριτικές'),
    ]
    mark_evidence = []
    for kind, ident, printed, google in mark_cases:
        c = lek[ident]
        assert printed in c['detail'] and google in c['detail']
        mark_evidence.append(dict(type=kind, card_id=ident, printed=printed, google=google,
             original_usable=c['original_usable'], usable_after_screen=c['usable_after_screen'],
             blind_marks=c['marks'], split=c['split']))
    mark_counts = {}
    for kind in sorted({r['type'] for r in mark_evidence}):
        ev = [r for r in mark_evidence if r['type']==kind]
        mark_counts[kind] = dict(all_40_cards=len({r['card_id'] for r in ev}),
             original_usable_cards=len({r['card_id'] for r in ev if r['original_usable']}),
             surviving_usable_cards=len({r['card_id'] for r in ev if r['usable_after_screen']}))
    write_json(OUT/'receipts/lekythos_marks.json', dict(counts=mark_counts, evidence=mark_evidence,
             qualification='Explicit printed-to-Google pairs only; cards can occur in several types. marks=na remains excluded from marks accuracy even when a detail names a mark error.'))
    changed = rows(OUT/'receipts/assembly_changes.jsonl')
    cardids = {c['id'] for c in cards}
    random_changed = random.Random(SEED).sample(sorted([r for r in changed if r['id'] not in cardids], key=lambda r:r['id']), 10)
    write_rows(OUT/'receipts/random_changed_non_cards.jsonl', random_changed)
    make_report(features, cards, stats, rates, conventions, model, primary, residual, physical, totals, random_changed)
    print(json.dumps(dict(totals=totals, test=primary), indent=2))


def make_report(features, cards, stats, rates, conventions, model, primary, residual, physical, totals, random_changed):
    byid = {r['id']: r for r in features}
    bycard = {(c['track'], c['source'], c['card_id']): c for c in cards}
    traces = {r['id']: r for r in rows(OUT/'receipts/card_traces.jsonl')}
    witnesses = []
    for source, ids in CORE.items():
        for ident in ids:
            c = bycard[('gr', source, ident)]
            witnesses.append(dict(traces[c['id']], letters_fixed=c['letters_fixed'],
                                  matches_printed_base=c.get('matches_printed_base'),
                                  matches_printed_literal=c.get('matches_printed_literal'),
                                  blind_detail=c['detail'], original_letters=c['letters'], core_twenty=True))
    # Include every additional changed card, plus the two ELSTAT non-interleave controls.
    coreids = {r['id'] for r in witnesses}
    for c in cards:
        if c['id'] in coreids:
            continue
        if c['assembly_changed'] or (c['track']=='gr' and c['source']=='elstat' and c['card_id'] in {'c001','c009'}):
            witnesses.append(dict(traces[c['id']], letters_fixed=c['letters_fixed'],
                matches_printed_base=c.get('matches_printed_base'), matches_printed_literal=c.get('matches_printed_literal'),
                blind_detail=c['detail'], original_letters=c['letters'], core_twenty=False))
    write_rows(OUT/'receipts/interleave_witnesses.jsonl', witnesses)
    esc = lambda s: str(s).replace('|', '\\|').replace('\n', ' ')
    corefixed = sum(w['letters_fixed']=='y' for w in witnesses if w['core_twenty'])
    changedpct = totals['changed_lines']/totals['lines']*100
    report = ['# T4b — assembly repair and admission-only merged-crop screen', '',
      '## 1. Duplicate-interleave repair', '',
      f"Reassembled **all {totals['lines']:,} lines** from the saved Google responses. **{totals['changed_lines']:,} labels changed ({changedpct:.3f}%) on {totals['changed_pages']} pages**. No provider calls, network access, or spend. The shipped code and all input tracks remain unchanged. The new opt-in function is [assembly_fix.py](assembly_fix.py); the offline pipeline is [screen.py](screen.py).", '',
      'The root-cause trace corrects the working hypothesis: P1 does not interleave two separately returned lines itself. `montage.response_lines()` slices each Google line text anchor, and P1 `process_reads.one()` passes it through normalization. The **saved Google line anchor already contains the overlapping alternative readings**. The missing assembly safeguard is box suppression. On OpenArchives c014, Google line index 211, anchor [8189,8250), already reads the entire bad label. The page record confirms `text_object_count=0` and `scanned_image_no_text_operators`; hidden PDF text is not the source.', '',
      '**Final rule:** native token AABB IoU > **0.10**, vertical intersection ≥80% of the shorter token height, vertical-center separation ≤45% of that height, and horizontal intersection ≥60% of the shorter width. A geometric overlap component must contain a base-text substring pair or SequenceMatcher ratio ≥0.40. Within that component, choose the nonconflicting token set maximizing Σ(base letters/digits × saved token confidence). This allows two genuine short words to defeat one combined hallucination. Punctuation competes only with identical punctuation and ties prefer the earliest anchor. No word is removed merely because its spelling repeats.', '',
      'The low IoU is needed for a one-character suffix inside a much longer full token; 0.20 misses ELSTAT `σεις` and short OA tails. The vertical and text-compatibility guards protect stacked marginal notes and ordinary punctuation. The horizontal guard preserves adjacent numeric date fields: an earlier prototype changed `1/1-30/6` to `/1-30/6`; the final function leaves it intact. Actual negative witnesses include IA poly1850 c032 (two stacked marginal readings) and BSB c020 / Pleias c021 (two printed rows). They remain intact. Prototype rules that removed punctuation or stacked-row words were rejected.', '',
      f"**Twenty actual interleave witnesses: {corefixed}/20 now have correct base letters relative to the supplied printed readings.** The duplicate defect and whole-card correctness are separate: ELSTAT retains its Y/Υ and digit errors; Pleias retains Κα!/Καὶ and Latin O/Greek Ὁ errors. The requested source count 7+4+3+3+3 is not supported by the files: only ELSTAT c026/c030 show duplicate interleave; c001/c009 are other OCR errors. Therefore the core twenty are OA 7, ELSTAT 2, Gazette 4, Pleias 3, Anemi 4. Both ELSTAT controls and every additional changed card are also traced below and in the receipt.", '',
      'The table reports **base-letter agreement**, not a fresh blind verdict. Literal agreement is shown separately; `unverified` means the old `marks=na` or partial detail cannot certify every mark. Blind `letters`, `marks`, errors and detail remain unchanged in [card_eval.jsonl](card_eval.jsonl); `letters_fixed` is the explicitly documented analyst comparison. [Full token IDs, native boxes, anchors, confidence, retained/dropped IDs and raw-response hashes for every witness](receipts/interleave_witnesses.jsonl).', '',
      '| Source/card | Old label → fixed label | Base letters now match? | Literal/marks | Dropped token IDs → retained IDs |',
      '|---|---|---|---|---|']
    for w in witnesses:
        if not w['core_twenty']:
            continue
        d = '; '.join(f"{d['dropped_token_id']}→{','.join(map(str,d.get('competing_kept_ids',[d['kept_token_id']])))} (IoU {d['iou']:.3f})" for d in w['drops'])
        report.append(f"| {w['source']}/{w['card_id']} | {esc(w['old_label'])} → **{esc(w['fixed_label'])}** | {'yes' if w['letters_fixed']=='y' else 'no'} | {w.get('matches_printed_literal','unverified')} | {d} |")
    report += ['', 'All additional changed cards and non-interleave controls:', '',
      '| Source/card | Old → fixed | Base letters now | Reason from original blind detail |', '|---|---|---|---|']
    for w in witnesses:
        if not w['core_twenty']:
            report.append(f"| {w['track']}/{w['source']}/{w['card_id']} | {esc(w['old_label'])} → {esc(w['fixed_label'])} | {w['letters_fixed']} | {esc(w['blind_detail'])} |")
    report += ['', 'Changes across every input line (denominator includes originally unusable lines):', '',
      '| Track/source | Changed / all lines | Changed % |', '|---|---:|---:|']
    for group in sorted({(r['track'], r['source']) for r in features}):
        rr = [r for r in features if (r['track'],r['source'])==group]
        n = sum(r['assembly_changed'] for r in rr)
        report.append(f"| {'/'.join(group)} | {n}/{len(rr)} | {100*n/len(rr):.3f}% |")
    for track in TRACKS:
        rr = [r for r in features if r['track']==track]
        n = sum(r['assembly_changed'] for r in rr)
        report.append(f"| **{track} total** | **{n}/{len(rr)}** | **{100*n/len(rr):.3f}%** |")
    report += ['', 'Ten seeded random changed lines outside all 640 cards (seed 20261016; see [receipt](receipts/random_changed_non_cards.jsonl)):', '',
      '| Line | Old → fixed |', '|---|---|']
    for r in random_changed:
        report.append(f"| {r['track']}/{r['id']} | {esc(r['old_label'])} → **{esc(r['fixed_label'])}** |")
    report += ['', '## 2. Per-source held-out accuracy, marks, removal, and yield', '',
      'Letters columns use the **held-out 20 cards per source** and only the F2-usable subset at each stage. They show original → assembly-fixed → screen-surviving. Each value is y/n with a Wilson 95% interval; any `u` remains in the denominator and does not count as success. Marks use **all up-to-40 cards**, restricted to surviving usable cards with marks y/n; `na` is excluded and counted in the receipts. The separate test-only marks estimates are in [statistics.json](receipts/statistics.json). No marks verdict is promoted after a letter repair.', '',
      'Full-line removal is measured over **all original `usable_candidate` rows**, not the card sample. Original P1 admission, codec, G1b and dedup eligibility are frozen: no rejected row is promoted. A fixed label that becomes empty/short/symbol-heavy is withheld as well. The removal column includes that conservative fix gate plus the merged-crop screen. The screen rejects a crop; it never recuts or repairs one.', '',
      'Yield cells show rows per **successful saved read page** and page-bootstrap 95% intervals (5,000 resamples). Primary classes are disjoint. All successful final-cohort pages, including zero-yield pages, enter the denominator. These intervals describe the F2 page mix; they are not a population-coverage or 40k-supply guarantee. Wikisource RU is an unreviewed alignment reference and contributes **zero training supply**, regardless of its diagnostic pipeline-usable counts.', '',
      '| Track/source | Letters original → fixed → after screen (test; Wilson 95%) | Marks after screen (all cards; Wilson 95%) | Full usable removed | Rows/read page by primary class after fix + screen [page-bootstrap 95%] |',
      '|---|---|---|---|---|']
    for s in stats:
        rr = [r for r in rates if r['track']==s['track'] and r['source']==s['source'] and r['period'] is None]
        ratestr = '; '.join(f"{r['primary_class']}: {f_rate(r['after_screen'])}" for r in rr)
        letters = 'unreviewed' if not s['cards'] else ' → '.join(fmt(s[k]) for k in ['letters_before_test','letters_fixed_test','letters_after_test'])
        markstr = fmt(s['marks_after_all'])+f"; na={s['marks_after_all']['na']}; full-40: {fmt(s['marks_blind_all_40'])}"
        if s['marks_correction_required']:
            markstr += '; **marks_correction_required**'
        remove = f"{s['original_usable']-s['after_screen']}/{s['original_usable']} ({100*s['removed_share']:.2f}%)" if s['original_usable'] else '0/0'
        report.append(f"| {s['track']}/{s['source']} | {letters} | {markstr} | {remove} | {ratestr} |")
    gaz = next(s for s in stats if s['source']=='government-gazette')
    gm = next(r for r in rates if r['source']=='government-gazette' and r['period']=='modern' and r['primary_class']=='modern_scanned')
    gp = next(r for r in rates if r['source']=='government-gazette' and r['period']=='poly1900' and r['primary_class']=='poly1900')
    gazcards = [c for c in cards if c['source']=='government-gazette' and c['usable_after_screen']]
    gaztest = [c for c in gazcards if c['split']=='test']
    gazmodern = [c for c in gaztest if c['primary_class']=='modern_scanned']
    gazpoly = [c for c in gaztest if c['primary_class']=='poly1900']
    mix = ', '.join(f'{k}={v}' for k,v in sorted(Counter(c['primary_class'] for c in gaztest).items())) or 'none'
    report += ['', f"**Government Gazette — priority modern-scanned route.** {gaz['after_screen']:,}/{gaz['original_usable']:,} original usable rows survive the fix gate and screen ({100*(1-gaz['removed_share']):.1f}%). Held-out surviving usable accuracy is **{fmt(gaz['letters_after_test'])}**, compared with {fmt(gaz['letters_before_test'])} originally; the all-40 diagnostic is **{fmt(gaz['letters_after_all'])}**. The surviving test mix is **{mix}**. Modern-scanned target test accuracy is **{fmt(accuracy(gazmodern))}** and poly1900 target test accuracy is **{fmt(accuracy(gazpoly))}**; numeric and Latin by-products do not establish Greek target accuracy. Conditional yield on the **{gm['after_screen']['pages']} modern read pages** is **{f_rate(gm['after_screen'])} modern-scanned rows/page**; on the **{gp['after_screen']['pages']} poly1900 read pages**, **{f_rate(gp['after_screen'])} poly1900 rows/page**. These conditional period rates use their own read-page denominators; the main table uses all Gazette read pages. **The 40k modern-scanned route remains unqualified:** the class-specific card evidence is limited, its Wilson interval cannot establish ≥90% target accuracy, and marks remain a separate requirement ({fmt(gaz['marks_after_all'])}).", '',
      '| Gazette primary class | Surviving usable letters, all 40 | Surviving usable letters, test only |', '|---|---|---|']
    for target in dict.fromkeys(['modern_scanned','poly1900','greek_mono','latin','numerics_tables']+sorted({c['primary_class'] for c in gazcards})):
        gc=[c for c in gazcards if c['primary_class']==target]
        report.append(f"| {target} | {fmt(accuracy(gc))} | {fmt(accuracy([c for c in gc if c['split']=='test']))} |")
    report += ['',
      '## 3. Calibration and held-out screen performance', '',
      'Seed **20261016**, exactly 20 calibration / 20 test cards for each of 16 sources; source-stratified only, not outcome-stratified. The split was written before feature extraction. The global threshold family contains height ratio, token vertical spread, internal x-gap, label/ink density ratio, paragraph count, and projection-peak/height conjunctions. At most three OR branches are allowed. The objective was calibration F1, with fixed tie breaks (precision, fewer calibration rejections, fewer branches); no per-source tuning or test threshold selection.', '',
      'Frozen selected screen: `'+json.dumps(model['branches'],ensure_ascii=False)+'`. Every inequality is strict `>`. [Model, full candidate grid and calibration-card identities](receipts/model.json); [seeded split](receipts/split.jsonl). The screen never consumes a card ID, source identity, or G1b measurement. The assembly guard was settled before this final fit. An earlier discarded prototype used G1b scales and its held-out outcomes were already read; the final features were replaced solely to enforce the requested input contract, and final thresholds were fitted using calibration outcomes only. This is **not a pristine new blind validation** of the final full pipeline. [Protocol and discarded-prototype disclosure](receipts/screen_protocol.json).', '',
      f"Calibration: TP={model['calibration']['tp']}, FP={model['calibration']['fp']}, FN={model['calibration']['fn']}, TN={model['calibration']['tn']}; P={100*(model['calibration']['precision'] or 0):.1f}%, R={100*(model['calibration']['recall'] or 0):.1f}%. Held-out specified endpoint: **TP={primary['tp']}, FP={primary['fp']}, FN={primary['fn']}, TN={primary['tn']}; precision {fmt(primary['precision_wilson'])}, recall {fmt(primary['recall_wilson'])}.**", '',
      '**Screen verdict: experimental, not qualified for automatic admission.** The requested-endpoint performance is reported above; the limited class-specific sample and prior discarded-prototype test exposure prevent a fresh blind production-validation claim. The stored decisions make the observed tradeoff inspectable.', '',
      'The primary positive is exactly the requested **original blind letters=n AND errors includes merged_two_lines, extra_text, or crop_overrun**. It deliberately retains duplicate-only cards even when assembly has repaired them. A secondary residual endpoint removes only cards whose base letters were repaired: '+f"P={100*(residual['precision'] or 0):.1f}%, R={100*(residual['recall'] or 0):.1f}% (TP/FP/FN/TN {residual['tp']}/{residual['fp']}/{residual['fn']}/{residual['tn']}). "+'These are different endpoints, not interchangeable scores. Some specified-endpoint false positives have blind letters=y despite `merged_two_lines` or `crop_overrun`; the physical diagnostic is reported separately in the receipt, without changing the requested positive definition.', '',
      '| Source | Held-out screen TP / FP / FN / TN | Precision / recall |', '|---|---|---|']
    for s in stats:
        if s['cards']:
            a=s['test']; p='n/a' if a['precision'] is None else f"{100*a['precision']:.1f}%"; r='n/a' if a['recall'] is None else f"{100*a['recall']:.1f}%"
            report.append(f"| {s['track']}/{s['source']} | {a['tp']} / {a['fp']} / {a['fn']} / {a['tn']} | {p} / {r} |")
    report += ['', 'Pixel features use the exact existing F2 crop rectangle on its stored page raster: fixed dark-ink threshold `(p05+p90)/2`, capped at 200. The x-height scale is a **crop-component median body-height proxy**, not a typographic measurement: connected components with height ≥max(3 px, 12% crop height) and ≤90% crop height, width/height 0.12–3, and width ≤max(6 px, 25% crop width). At least three eligible components are needed; otherwise use half the median saved Google token height. No detector or G1b measurement supplies this scale. The page row height is the median saved Google line-box height on alphabetic lines. Horizontal ink projection is smoothed at 0.12 of the body-height proxy; peaks at ≥20% of maximum with ≥18% prominence and 0.7 proxy-height separation. An internal low-ink x-gap requires ≥10% of ink mass on each side. Density is visible fixed-label characters per crop ink width in proxy x-heights divided by that page’s median. Token centers and paragraph membership come from saved Google geometry. Every F2 row has one Google line anchor, so the Google-line contributor count is one and offers no discrimination; token vertical spread still detects multi-row anchors. G1b flags enter only the frozen original-usability denominator, never the screen decision.', '',
      '## 4. Marks remain a separate requirement', '',
      'The marks column above is taken verbatim from the blind marks field on surviving usable cards, with Wilson 95% intervals. Every row from a measured polytonic source below 90% carries `marks_correction_required` in [features.jsonl](features.jsonl), including its Latin/numeric by-products. Conservatively, the source tag is retained if **either** the full blind-40 marks estimate **or** the surviving-usable estimate is below 90%. In particular, ELSTAT 19/29 (65.5%) and Pergamos 11/17 (64.7%) retain their known weak-source evidence even if a tiny selected subset is perfect. This source tag is not a mark repair. A zero measurable surviving denominator is also tagged `marks_unmeasured`, not passed.', '',
      'Lekythos mark-error types (card counts, not token counts) are derived only from explicit printed → Google pairs in the blind detail. Grave→acute, circumflex→acute and breathing dropped are tabulated in [lekythos_marks.json](receipts/lekythos_marks.json); these include all 40, the usable subset, and the post-screen usable subset. No error type is inferred from `marks=na`. Its large supply therefore remains conditional on mark correction whenever the measured surviving marks point estimate is below 90%.', '',
      '| Lekythos mark error | All 40 cards | Originally usable | Surviving usable |', '|---|---:|---:|---:|']
    lekcounts = json.loads((OUT/'receipts/lekythos_marks.json').read_text())['counts']
    for kind, label in [('grave_to_acute','grave→acute'),('circumflex_to_acute','circumflex→acute'),('breathing_dropped','breathing dropped'),('accent_dropped','accent dropped'),('mark_with_base_letter_error','mark plus wrong base letter')]:
        a=lekcounts[kind]
        report.append(f"| {label} | {a['all_40_cards']} | {a['original_usable_cards']} | {a['surviving_usable_cards']} |")
    report += ['', '## 5. Text-side conventions and counts', '',
      'Checks ran over every line; the table counts every usable row **after steps 1–2**, before text exclusions. Original-usable branch counts are also retained in [convention_counts.jsonl](receipts/convention_counts.jsonl). Text-side exclusions are applied in `usable_final`; `fixed_label` remains the assembly output and `label_after_conventions` is the convention-normalized label.', '',
      '**ſ→s:** accepted as a glyph variant. Count literal ſ in labels and exact blind-detail witnesses. BSB c008 is an additional visually inspected Fraktur witness. The total number of printed long-s lines is **not determinable** from labels already normalized to s; a zero Unicode count is not proof of zero printed ſ.', '',
      '**Roman look-alikes:** deterministic table `'+json.dumps(ROMAN_TABLE,ensure_ascii=False)+'`, with Latin I,V,X,L,C,M,D unchanged. Convert only a whole letter token whose complete mapped value matches `^[IVXLCMD]+$`. No Δ→D or Λ→L guess is allowed. A single Greek/Cyrillic letter followed by a period (e.g. Χ. as a person’s initial) has ambiguous numeral intent and excludes the line instead of changing its script. Ambiguous Roman-shaped tokens containing Λ,Δ,Д,Л,П,Ӏ, or mixed Latin-Roman / Greek-Cyrillic tokens that fail the complete map, also exclude the line. The table’s fixed and excluded Roman line branches are disjoint: a line containing both types is counted in exclusion, with overlap recorded separately in the receipt. This candidate grammar is explicit; general all-script capital words cannot reliably be identified as intended Roman numerals from text alone.', '',
      '**Dropped line-end hyphen:** bind the nearest lower Google row in the same column (≥50% shorter-width overlap, left edges within 1.5 page-median Google row heights, gap ≤2 crop heights). Exclude a no-hyphen final word fragment followed by lowercase only when tail+head is attested on at least two other pages and the tail never appears as a nonfinal corpus word. This is a conservative text-only fragment test; remaining lowercase continuations are explicitly `fragment_unknown`, not silently asserted to be complete words. No pixel-derived feature or ink work is used for this check.', '',
      '**Em dash→hyphen:** accepted. Exact printed em-dash substitutions are counted only where blind detail establishes them; ordinary hyphens elsewhere cannot distinguish a changed em dash from a true hyphen. Therefore whole-corpus physical substitution counts are **not determinable**. The table also gives label-hyphen candidate lines without asserting their printed glyph.', '',
      '| Track/source | Usable lines checked | ſ label lines / blind witnesses / visual witnesses | Roman fixed lines (tokens) / excluded lines | Dropped-hyphen exclusions / lowercase-fragment unknown | Em-dash→hyphen blind witnesses, all→surviving / label-hyphen lines |',
      '|---|---:|---|---|---|---|']
    for c in conventions:
        report.append(f"| {c['track']}/{c['source']} | {c['usable_scanned']} | {c['long_s_label_lines']} / {len(c['long_s_blind_witnesses'])} / {len(c['long_s_visual_witnesses'])}→{len(c['long_s_visual_surviving'])} | {c['roman_fixed_lines']} ({c['roman_fixed_tokens']}) / {c['roman_excluded_lines']} | {c['dropped_hyphen_excluded_lines']} / {c['lowercase_fragment_unknown']} | {c['emdash_to_hyphen_blind_all']}→{c['emdash_to_hyphen_blind_surviving']} / {c['label_has_hyphen_lines']} |")
    report += ['', 'After text exclusions (pipeline counts; RU reference remains excluded from training supply):', '',
      '| Source | After screen → after text checks | Additional text exclusions | Total original usable removed |', '|---|---:|---:|---:|']
    for s in stats:
        report.append(f"| {s['track']}/{s['source']} | {s['after_screen']}→{s['after_conventions']} | {s['after_screen']-s['after_conventions']} | {100*(s['final_removed_share'] or 0):.2f}% |")
    report += ['', '## 6. Verdict and limits', '']
    yes_test = [s['source'] for s in stats if s['cards'] and s['letters_after_test']['rate'] is not None and s['letters_after_test']['rate'] >= .90]
    yes = [s['source'] for s in stats if s['cards'] and s['letters_final_all']['rate'] is not None and s['letters_final_all']['rate'] >= .90]
    no = [s for s in stats if s['cards'] and (s['letters_final_all']['rate'] is None or s['letters_final_all']['rate'] < .90)]
    weak = [s['source'] for s in stats if s['marks_correction_required']]
    report.append('The requested source verdict, limited to the **descriptive final surviving usable subset of all 40 supplied cards per source**, reaches a ≥90% letters-y point estimate for **'+(', '.join(yes) or 'none')+'**. The separate held-out after-screen ≥90% list is **'+(', '.join(yes_test) or 'none')+'**. The denominators and class mix matter; neither list establishes whole-source accuracy. No source has a held-out Wilson lower bound ≥90%. Repaired labels were compared with the existing printed readings, not sent for a new blind check.')
    report += ['', 'All-40 letter counts (descriptive, includes the calibration cards):', '', '| Source | Original → fixed → screen → final usable letters, all 40 (Wilson 95%) |', '|---|---|']
    for s in stats:
        if s['cards']:
            report.append(f"| {s['track']}/{s['source']} | {fmt(s['letters_before_all'])} → {fmt(s['letters_fixed_all'])} → {fmt(s['letters_after_all'])} → {fmt(s['letters_final_all'])} |")
    report += ['', '| Source below 90%, or unmeasured (all 40) | Surviving usable letters | Residual errors on all surviving usable cards |', '|---|---|---|']
    for s in no:
        errs = ', '.join(f'{k}={v}' for k,v in s['residual_errors_final'].most_common(5)) or 'no determinable surviving sample'
        report.append(f"| {s['track']}/{s['source']} | {fmt(s['letters_final_all'])} | {errs} |")
    report += ['', 'Measured polytonic sources below 90% in the full blind sample or surviving usable marks-y: **'+', '.join(weak)+'**. All carry the requested source tag; no marks were corrected by this task.', '',
      f"Overall: {totals['original_usable']:,} original pipeline-usable rows → {totals['after_screen']:,} after fix+screen → {totals['after_conventions']:,} after text exclusions. {totals['training_after_conventions']:,} are candidate rows after removing reference-only RU. These remain silver candidates, not released or independently revalidated training labels. The final footer removal percentage includes text exclusions; the per-source main table isolates fix+screen removal.", '',
      'Reproduce offline with the worktree’s existing Python environment (Pillow, NumPy, SciPy):', '',
      '```sh',
      'PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/harvest/screen_v1/screen.py extract',
      'PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/harvest/screen_v1/screen.py calibrate',
      'PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/harvest/screen_v1/evaluate.py',
      'PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/harvest/screen_v1/validate.py',
      '```', '',
      'The manual assembly comparisons are frozen in [assembly_review.jsonl](receipts/assembly_review.jsonl). Native review panels are in [changed-card panel 1](receipts/changed_cards_01.png), [random non-cards 1](receipts/random_changed_01.png), [random non-cards 2](receipts/random_changed_02.png), and [stacked-row/date controls](receipts/negative_controls.png). The random rows expose residual provider errors and crop defects as well as resolved duplicates; they are not ten newly certified labels ([review notes](receipts/random_collateral_review.jsonl)). Source and output hashes, crop-pixel checks, outcome counts, statistical denominators, and commit status are in [receipts/](receipts/). The source-bound [guarded commit helper](commit_helper.py) is left for a writable Git index; it validates input and artifact hashes and stages only the enumerated output files.', '',
      'For exact calibration replay, `screen.py calibrate` uses the archived final crop/Google feature snapshot and split when those receipts exist. The discarded G1b-scaled prototype is isolated under [prototype_g1b_scaled/](receipts/prototype_g1b_scaled/); none of its metrics or features is the final screen result.', '',
      'Footer conventions: screen P/R uses the held-out half; source letters and Gazette accuracy use the descriptive all-40 final surviving subset; marks lists sources below 90% in either their full blind marks sample or surviving usable marks subset; Gazette modern rows/page uses the modern-period denominator after fix+screen; total removal includes the text-side exclusions.', '']
    footer = f"T4b: done | interleave fix: {corefixed} cards fixed of 20, lines changed {changedpct:.3f}% | screen P/R test: {100*(primary['precision'] or 0):.1f}%/{100*(primary['recall'] or 0):.1f}% | letters ≥90% after: {','.join(yes) or 'none'} | marks <90%: {','.join(weak) or 'none'} | gazette letters after: {100*(gaz['letters_final_all']['rate'] or 0):.1f}% rows/page modern {gm['after_screen']['mean']:.2f} | usable rows removed: {100*(totals['original_usable']-totals['after_conventions'])/totals['original_usable']:.2f}%"
    report.append(footer)
    (OUT/'REPORT.md').write_text('\n'.join(report)+'\n')
    (OUT/'receipts/final_line.txt').write_text(footer+'\n')


if __name__ == '__main__':
    run()
