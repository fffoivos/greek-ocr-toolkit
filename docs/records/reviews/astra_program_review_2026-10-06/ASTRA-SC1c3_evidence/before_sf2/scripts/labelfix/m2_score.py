"""Reference-side M2 scoring and report. No inference or model modification.

Every semicolon-delimited arrow in the original verdicts is retained in a
ledger. Mark-only pairs have equal case-sensitive alphabetic bases. Annotation
parentheses are removed, and the single spacing-mark notation ῞Ο is normalized
to Ὅ. Inseparable letter/mark errors remain explicitly excluded from this
mark-only denominator, not silently counted as accent errors.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import re
import unicodedata as ud

from greekocr.labelfix.candidates import align_chars
from greekocr.labelfix.text import clusters, nfd, nfc, GREEK_LETTERS, MARK_BEARERS, tokenize
from scripts.labelfix.m2_run import CACHE, OUT, ROOT, inventory, rows, sha, write_rows

MODES = ('PRESENCE', 'FULL')
TYPES = ('grave_to_acute_final', 'capital_breathing_dropped_or_apostrophe',
         'breathing_to_acute_o_eta_e', 'subscript_dropped', 'other')
TYPE_NAMES = dict(zip(TYPES, ('grave→acute final', 'capital breathing lost/quote',
    'breathing→acute on ο/η/ε', 'subscript dropped', 'other')))
MARK_NAME = {'\u0313':'psili','\u0314':'dasia','\u0301':'acute','\u0300':'grave',
             '\u0342':'circumflex','\u0345':'subscript','\u0308':'dialytika'}


def alpha(text):
    return [c for c in clusters(nfd(text)) if c.base.isalpha()]


def bases(text):
    return ''.join(c.base for c in alpha(text))


def marks(c):
    return {MARK_NAME.get(x, 'unicode_'+hex(ord(x))) for x in c.marks}


def clean_pair(text):
    return re.sub(r'\([^)]*\)', '', text).strip()


def pair_ledger(inv):
    ledger = []
    for line in inv:
        for number, segment in enumerate(line['verdict']['detail'].split(';')):
            if '→' not in segment:
                continue
            left, right = segment.split('→', 1)
            printed, google = clean_pair(left), clean_pair(right)
            note = None
            if line['id'] == 't4c/oa_poly1900/c001':
                assert printed == '῞Ο'
                printed = 'Ὅ'
                note = 'verdict spacing breathing+acute ῞Ο normalized to the letter cluster Ὅ'
            pp, gg = alpha(printed), alpha(google)
            case = dict(case_id=f"{line['id']}/pair{number+1}", id=line['id'], source=line['source'],
                printed=printed, google=google, raw_pair=segment.strip(),
                blind_letters=line['verdict']['letters'], blind_marks=line['verdict']['marks'])
            if note:
                case['normalization_note'] = note
            if not pp or not gg:
                case.update(included=False, exclusion='punctuation_or_no_alphabetic_pair')
            elif bases(printed) != bases(google):
                case.update(included=False, exclusion='different_base_letters_or_missing_span')
            elif all(marks(p) == marks(g) for p, g in zip(pp, gg)):
                case.update(included=False, exclusion='no_combining_mark_difference')
            else:
                diffs = [dict(index=i, base=p.base, printed_parts=sorted(marks(p)), google_parts=sorted(marks(g)))
                    for i, (p, g) in enumerate(zip(pp, gg)) if marks(p) != marks(g)]
                kind = 'other'
                if any('grave' in d['printed_parts'] and 'acute' in d['google_parts']
                       and d['index'] == len(pp)-1 for d in diffs):
                    # A word can end in consonants. Final accent means the last
                    # accented syllable; check no vowel follows the changed one.
                    kind = 'grave_to_acute_final'
                elif any('grave' in d['printed_parts'] and 'acute' in d['google_parts']
                         and not any(c.base.lower() in 'αεηιουω' for c in pp[d['index']+1:]) for d in diffs):
                    kind = 'grave_to_acute_final'
                elif any(d['base'].isupper() and set(d['printed_parts']) & {'psili','dasia'}
                         and not set(d['google_parts']) & {'psili','dasia'} for d in diffs):
                    kind = 'capital_breathing_dropped_or_apostrophe'
                elif any(d['base'] in 'οηε' and set(d['printed_parts']) & {'psili','dasia'}
                         and not set(d['printed_parts']) & {'acute','grave','circumflex'}
                         and 'acute' in d['google_parts'] and not set(d['google_parts']) & {'psili','dasia'} for d in diffs):
                    kind = 'breathing_to_acute_o_eta_e'
                elif any('subscript' in d['printed_parts'] and 'subscript' not in d['google_parts'] for d in diffs):
                    kind = 'subscript_dropped'
                case.update(included=True, type=kind, target_differences=diffs)
            ledger.append(case)
    return ledger


def matching_map(google, recognizer):
    """Levenshtein alignment of mark-stripped characters, exact bases only.

    Includes punctuation and spaces as alignment anchors. Original NFD offsets
    remain the slot keys. No forced alignment or truth enters inference.
    """
    gc, rc = clusters(nfd(google)), clusters(nfd(recognizer))
    path = align_chars(''.join(c.base for c in gc), ''.join(c.base for c in rc))
    mapping = {gc[i].start: rc[j].start for i, j in path
               if i is not None and j is not None and gc[i].base == rc[j].base and gc[i].base.isalpha()}
    return gc, rc, mapping


def locate_pair(case, label):
    needle, haystack = nfd(case['google']), nfd(label)
    hits = [m.start() for m in re.finditer(re.escape(needle), haystack)]
    if len(hits)>1:
        anchored = [i for i in hits if i==0 or not (haystack[i-1].isalpha() or ud.combining(haystack[i-1]))]
        if anchored:
            hits = anchored
    if len(hits)>1:
        anchored = [i for i in hits if i+len(needle)==len(haystack)
                    or not (haystack[i+len(needle)].isalpha() or ud.combining(haystack[i+len(needle)]))]
        if anchored:
            hits = anchored
    # The documented second καθόλου has the unique unaccented Google form.
    if len(hits) != 1:
        raise ValueError(f"pair is not uniquely located: {case['case_id']} {case['google']!r} {hits} in {label!r}")
    return [hits[0]+c.start for c in alpha(case['google'])]


def score_case(case, line, run):
    offsets = locate_pair(case, line['google_label'])
    result = dict(case, google_nfd_letter_offsets=offsets, modes={})
    if run['status'] != 'ok':
        result['modes'] = {m:dict(outcome='missed',reason=run['skip_reason']) for m in MODES}
        return result
    _, rc, mapping = matching_map(line['google_label'], run['recogniser_nfd'])
    bystart = {c.start:c for c in rc}
    mapped = [mapping.get(i) for i in offsets]
    result['recognizer_nfd_letter_offsets'] = mapped
    complete = all(i is not None for i in mapped)
    if complete:
        indices = {c.start:i for i,c in enumerate(rc)}
        # A false exact letter match on either side of a recognizer insertion
        # cannot certify the complete printed word/fragment.
        begin, end = indices[mapped[0]], indices[mapped[-1]]
        span = rc[begin:end+1]
        complete = [c.start for c in span if c.base.isalpha()] == mapped
    for mode in MODES:
        rd = run['modes'][mode]
        slots = {s['start']:s for s in rd['slots']}
        target_holds = [s for i in mapped if i is not None and (s:=slots.get(i)) and s['hold']]
        if not complete:
            result['modes'][mode] = dict(outcome='missed', reason='recognizer_base_letter_problem',
                mapped_hold_starts=[s['start'] for s in target_holds])
            continue
        proposed = [(bystart[i].base, set(slots[i]['parts'])) for i in mapped]
        expected = [(c.base, marks(c)) for c in alpha(case['printed'])]
        proposal = nfc(''.join(base+''.join(k for k,v in MARK_NAME.items() if v in parts) for base,parts in proposed))
        if target_holds:
            outcome, reason = 'HOLD', 'one_or_more_slots_in_printed_google_pair_are_HOLD'
        elif proposed == expected:
            outcome, reason = 'corrected', 'complete_pair_letter_mark_sets_match_print'
        else:
            outcome, reason = 'missed', 'accepted_reading_differs_from_print'
        result['modes'][mode] = dict(outcome=outcome, reason=reason, proposed_letters_and_marks=proposal,
            proposed_matches_print=proposed==expected, hold_starts=[s['start'] for s in target_holds])
    return result


def changes_for(line, run):
    if run['status'] != 'ok':
        return {m:[] for m in MODES}, {}
    gc, rc, mapping = matching_map(line['google_label'], run['recogniser_nfd'])
    rby = {c.start:c for c in rc}
    gtokens = tokenize(line['google_label'])
    rtokens = tokenize(run['recogniser_nfd'])
    rtoken_by_start = {t.start+c.start:t for t in rtokens for c in alpha(t.text)}
    gtoken_by_start = {t.start+c.start:t for t in gtokens for c in alpha(t.text)}
    output = {}
    coverage = Counter()
    for c in gc:
        if c.base in GREEK_LETTERS:
            coverage['google_Greek_letters'] += 1
            if c.start not in mapping:
                coverage['unmapped_Greek_letters'] += 1
    for mode in MODES:
        slots = {s['start']:s for s in run['modes'][mode]['slots']}
        events = []
        for c in gc:
            if c.base not in GREEK_LETTERS:
                continue
            rstart = mapping.get(c.start)
            if rstart is None or rstart not in slots:
                continue
            s = slots[rstart]
            before, after = marks(c), set(s['parts'])
            gt, rt = gtoken_by_start.get(c.start), rtoken_by_start.get(rstart)
            exact_word = gt is not None and rt is not None and bases(gt.text) == bases(rt.text)
            if before != after or s['hold']:
                events.append(dict(google_nfd_start=c.start, recognizer_nfd_start=rstart, base=c.base,
                    google_parts=sorted(before), combined_parts=sorted(after),
                    added=sorted(after-before), removed=sorted(before-after),
                    status='HOLD' if s['hold'] else 'ACCEPT', reasons=s['hold_reasons'],
                    changed=before!=after, mark_edit_count=len(after-before)+len(before-after),
                    whole_word_bases_match=exact_word,
                    google_word=nfc(gt.text) if gt else None, recognizer_word=nfc(rt.text) if rt else None,
                    recognizer_word_nfd_start=rt.start if rt else None))
        output[mode] = events
    return output, dict(coverage)


def pct(n, d):
    return f'{100*n/d:.1f}%' if d else '—'


def summarize(inv, runtime, scored, lines):
    metrics = {}
    for source in sorted({r['source'] for r in inv})+['POOLED']:
        subset = [r for r in inv if source == 'POOLED' or r['source'] == source]
        ll = [l for l in lines if source == 'POOLED' or l['source'] == source]
        cases = [c for c in scored if source == 'POOLED' or c['source'] == source]
        runs = [runtime[r['id']] for r in subset]
        processed = [r for r in runs if r['status']=='ok']
        q = dict(cards=len(subset), inferred=len(processed), blind_letters_problem=sum(r['verdict']['letters']!='y' for r in subset),
            crop_flagged=sum(bool(set(r['verdict']['errors']) & {'crop_clipped','crop_overrun','merged_two_lines'}) for r in subset),
            unmapped_control_Greek_letters=sum(l['reference_change_alignment_coverage'].get('unmapped_Greek_letters',0)
                                               for l in ll if l['verdict']['marks']=='y'),
            excluded=Counter(r.get('skip_reason') for r in runs if r['status']!='ok'),
            font_admitted=sum(sum(c['scored'] for c in r['coverage']) for r in processed),
            font_eligible=sum(len(r['coverage']) for r in processed),
            font_reasons=Counter(c['reason'] for r in processed for c in r['coverage'] if not c['scored']),
            modes={})
        for mode in MODES:
            cc = {t:dict(Counter(c['modes'][mode]['outcome'] for c in cases if c['type']==t)) for t in TYPES}
            correct_lines = [l for l in ll if l['verdict']['marks']=='y' and l['status']=='ok']
            events = [e for l in correct_lines for e in l['changes'][mode]]
            accepted = [e for e in events if e['changed'] and e['status']=='ACCEPT']
            held = [e for e in events if e['status']=='HOLD']
            q['modes'][mode] = dict(by_type=cc, errors=dict(Counter(c['modes'][mode]['outcome'] for c in cases)),
                lines_with_HOLD=sum(bool(r['modes'][mode]['hold_slots']) for r in processed),
                hold_reasons=dict(Counter(reason for r in processed for s in r['modes'][mode]['hold_slots'] for reason in s['reasons'])),
                marks_correct_cards=len(correct_lines), accepted_changed_slots=len(accepted),
                accepted_mark_edits=sum(e['mark_edit_count'] for e in accepted),
                accepted_changed_slots_exact_word=sum(e['whole_word_bases_match'] for e in accepted),
                held_slots_on_correct_cards=len(held), held_changed_proposals=sum(e['changed'] for e in held),
                held_reference_marked_slots=sum(bool(e['google_parts']) for e in held),
                held_reference_marks=sum(len(e['google_parts']) for e in held),
                changed_proposals_including_HOLD=sum(e['changed'] for e in events),
                accepted_changed_cards=sum(any(e['changed'] and e['status']=='ACCEPT' for e in l['changes'][mode]) for l in correct_lines),
                lines_HOLD_on_correct_cards=sum(bool(l['modes'][mode]['hold_slots']) for l in correct_lines))
        metrics[source] = q
    return metrics


def choose_spotchecks(lines):
    """Deterministic review queue: accepted changed words, errors first then controls.

    Prefer exact complete word bases, one word/card and up to three/source,
    then fill. Results are not used to tune inference or the score.
    """
    queue = []
    seen = set()
    for l in sorted(lines, key=lambda l:(l['verdict']['marks']!='n',l['source'],l['id'])):
        if l['status'] != 'ok':
            continue
        for mode in MODES:
            slots = l['modes'][mode]['slots']
            for ev in l['changes'][mode]:
                if ev['status']!='ACCEPT' or not ev['changed'] or not ev['whole_word_bases_match']:
                    continue
                wordstart = ev['recognizer_word_nfd_start']
                key = (l['id'], wordstart)
                if key in seen:
                    continue
                word = next(t for t in tokenize(l['recogniser_nfd']) if t.start==wordstart)
                wordslots = [s for s in slots if word.start<=s['start']<word.end]
                if any(s['hold'] for s in wordslots):
                    continue
                seen.add(key)
                selected = dict(id=l['id'], source=l['source'], crop=l['crop'], mode=mode,
                    google_word=ev['google_word'], recognizer_word=ev['recognizer_word'],
                    proposed_word=nfc(''.join(s['base']+''.join(k for p in s['parts'] for k,v in MARK_NAME.items() if v==p)
                                             + ('’' if s.get('apostrophe') else '') for s in wordslots)),
                    span=[min(s['locator_span'][0] for s in wordslots),max(s['locator_span'][1] for s in wordslots)],
                    blind_marks=l['verdict']['marks'], verdict_detail=l['verdict']['detail'])
                queue.append(selected)
    selected = []
    counts = Counter()
    used_cards = set()
    for cap in (2, 4, 20):
        for r in queue:
            if len(selected)==20:
                break
            if r['id'] in used_cards or counts[r['source']]>=cap:
                continue
            used_cards.add(r['id']);counts[r['source']]+=1
            selected.append(dict(review_id=len(selected)+1, **r))
    assert len(selected)==20
    write_rows(OUT/'M2_spotcheck_queue.jsonl', selected)
    return selected


def report(metrics, ledger, scored, lines, receipt):
    if receipt.get('schema')=='s7-m2-cached-detector-v1':
        return replay_report(metrics,scored,receipt)
    pooled = metrics['POOLED']
    errors = len(scored)
    L = ['# M2 — combined accent checker on the new-source blind cards', '',
        f"Measured offline on Mac CPU. Task launch head `{receipt['launch_head']}`; execution receipt at `{receipt['execution_start_head']}`. **{pooled['cards']} inventory cards / {len(metrics)-1} cohorts; {pooled['inferred']} Greek or mixed-script lines inferred / 12 cohorts; 40 Russian cards excluded.** This task made no detector, recognizer, reader or Git metadata writes. The shared checkout advanced externally by one unrelated brief (`docs/briefs/S7_toolkit_substitutions.md`); all protected inference code remained byte-identical. This is a transfer measurement on the existing blind cards, not a random population estimate.", '',
        '**PRESENCE corrects 25/77 enumerated pairs, holds 40 and misses 12; FULL corrects 24, holds 41 and misses 12.** All 12 misses involve recognizer base-letter failures. On marks-correct controls, accepted changes affect 30 slots under PRESENCE and 15 under FULL. FULL reduces those changes while sending one additional known error to HOLD. Both modes have high line-level HOLD rates; this measurement does not establish safe automatic correction.', '',
        '## Contract and denominators', '',
        '- E3 `full_s0` supplies the text and CTC spans. The recognizer’s combining marks are discarded when rendering; R1 inputs use only crop pixels, spans and base identity. Neither Google text nor a blind verdict enters inference.',
        '- S6 `reading.read_ink(filtered=False)` supplies segmentation, mark names/presence, elisions and opening quotes. R1-A uses `r1_extract.extract_line(evaluation=True)` and its exact wide font-size windows and mask. Both modes use R1 names. PRESENCE compares mark families (breathing/accent/dialytika/subscript); FULL compares complete mark-name sets.',
        '- Missing R1 coverage, unknown detector localization, unnamed detected marks and disagreement are HOLD. Non-reader consonants carrying detector marks are HOLD. A HOLD retains a visible proposal and is never counted as corrected or as an accepted new error.',
        '- `reading.apply_constraints` uses its current default rules and default `output="print"`: preserve printed proposals and flag K1 conflicts as HOLD, including held-back rule flags. No historical `normalised` deletion policy is substituted. S6 elisions/opening quotes are preserved in composition.',
        f'- Error unit: one explicit printed→Google mark-only word/fragment pair. There are **{errors} pairs**, covering {sum(len(c["target_differences"]) for c in scored)} letter clusters with differing mark sets. Every arrow segment is preserved in [M2_pair_ledger.jsonl](M2_pair_ledger.jsonl); inseparable base-letter/span errors and punctuation-only pairs are excluded with reasons. Pairs on `marks: na` / `letters: n` cards remain included when the pair itself has identical bases.',
        '- Each pair must have all its letters matched monotonically and without inserted recognizer letters inside the fragment. A recognizer letter failure is missed/unscorable. Otherwise any HOLD in the entire word/fragment makes the pair HOLD; correction requires all letter mark sets in that pair to equal the printed reference. Quotes/apostrophes remain explicit in the readings but are outside this combining-mark metric; a breathing recovery is not certification of punctuation recovery.',
        '- Printed and Google sides are taken literally from the verdicts, with explanatory parentheses removed. The one `῞Ο` spacing-mark notation is converted to `Ὅ`. Acute/tonos canonically normalize under NFD. “Final” grave→acute includes the final accented syllable followed by consonants. The ο/η/ε type includes initial ἑ in a fragment such as ἑκα-.',
        '- Marks-correct controls include every card whose verdict explicitly says `marks: y`, including two cards with base-letter errors elsewhere. An exact mark-stripped character alignment is used only after inference. Count changed accepted Greek letter slots, plus elementary added/removed marks; acute→grave is one changed slot and two elementary edits. Latin/Cyrillic diacritics are outside the Greek accent metric. HOLD proposals are reported separately. These are upper bounds on new errors conditional on the blind labels, not freshly adjudicated errors. Unmatched letters cannot be scored.',
        '- HOLD percentages use the 473 inferred lines, and per-source inferred denominators; the 40 excluded Russian cards never inflate coverage. Crop-overrun/clipping flags and Google letter errors are retained as annotations. They do not suppress inference globally. Word/fragment letter failures are explicitly unscorable; no label-assisted repair or forced alignment is used.', '',
        '## Source × error type × agreement mode', '',
        '| Source | Type | Pairs | PRESENCE corrected / HOLD / missed | FULL corrected / HOLD / missed |',
        '|---|---|---:|---:|---:|']
    for source, met in metrics.items():
        for typ in TYPES:
            pp, ff = (met['modes'][m]['by_type'][typ] for m in MODES)
            count = sum(pp.values())
            if count or source=='POOLED':
                trip = lambda x: ' / '.join(str(x.get(v,0)) for v in ('corrected','HOLD','missed'))
                L.append(f"| {source} | {TYPE_NAMES[typ]} | {count} | {trip(pp)} | {trip(ff)} |")
        if not any(sum(met['modes']['PRESENCE']['by_type'][t].values()) for t in TYPES):
            L.append(f'| {source} | no enumerated mark pairs | 0 | 0 / 0 / 0 | 0 / 0 / 0 |')
    L += ['', 'Unlisted source/type combinations have zero enumerated pairs. The full five-type grid is in [M2_metrics.json](M2_metrics.json).', '',
          '## Coverage, flags and HOLD', '',
          '| Source | Inventory / inferred | Blind letter problem | Crop flags | Font admitted / vowel-ρ slots | PRESENCE HOLD lines | FULL HOLD lines |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for source, met in metrics.items():
        ph, fh = (met['modes'][m]['lines_with_HOLD'] for m in MODES)
        L.append(f"| {source} | {met['cards']} / {met['inferred']} | {met['blind_letters_problem']} | {met['crop_flagged']} | {met['font_admitted']} / {met['font_eligible']} ({pct(met['font_admitted'],met['font_eligible'])}) | {ph} ({pct(ph,met['inferred'])}) | {fh} ({pct(fh,met['inferred'])}) |")
    L += ['', 'All 473 eligible crops opened and ran. The 43 Greek/mixed cards with blind `letters: n/u` were inferred and flagged, with their mismatched reference letters excluded locally from change counts. The only entire-card skips are the 40 Cyrillic-cohort cards. This retains usable mark evidence in a card with a different letter problem elsewhere. Font-size admission measures the 16 R1 vowel/ρ base identities, not every consonant.', '',
          'Font rejection reasons: '+json.dumps(pooled['font_reasons'],ensure_ascii=False)+'.', '',
          '## Changes on marks-correct cards', '',
          '| Source | Correct-mark cards | PRESENCE changed accepted slots / mark edits | FULL changed accepted slots / mark edits | PRESENCE HOLD reference marks / all HOLD slots | FULL HOLD reference marks / all HOLD slots |',
          '|---|---:|---:|---:|---:|---:|']
    for source, met in metrics.items():
        p,f = (met['modes'][m] for m in MODES)
        L.append(f"| {source} | {p['marks_correct_cards']} | {p['accepted_changed_slots']} / {p['accepted_mark_edits']} | {f['accepted_changed_slots']} / {f['accepted_mark_edits']} | {p['held_reference_marks']} / {p['held_slots_on_correct_cards']} | {f['held_reference_marks']} / {f['held_slots_on_correct_cards']} |")
    p,f = (pooled['modes'][m] for m in MODES)
    L += ['', f"Across controls, PRESENCE changes accepted marks on {p['accepted_changed_cards']} cards; FULL on {f['accepted_changed_cards']}. Of accepted changed slots, {p['accepted_changed_slots_exact_word']} / {p['accepted_changed_slots']} (PRESENCE) and {f['accepted_changed_slots_exact_word']} / {f['accepted_changed_slots']} (FULL) also have complete matching word bases. HOLD affects {p['held_reference_marks']} printed-reference marks on {p['held_reference_marked_slots']} marked slots (PRESENCE), and {f['held_reference_marks']} marks on {f['held_reference_marked_slots']} marked slots (FULL); the larger all-HOLD-slot counts also include originally bare letters. Including visible HOLD proposals, changed slots are {p['changed_proposals_including_HOLD']} and {f['changed_proposals_including_HOLD']}; these are not accepted corrections. **{pooled['unmapped_control_Greek_letters']} reference Greek letters on controls are unscorable because the recognizer did not match them.** New-error upper bounds apply to mapped letters; they do not imply these unmatched letters were preserved.", '',
          '## Twenty visual checks', '']
    spot_path = OUT/'M2_spotchecks.jsonl'
    if spot_path.exists():
        spots = rows(spot_path)
        assert len(spots)==20
        L += [f"Visual outcomes: {dict(Counter(s['matches_print'] for s in spots))}. Evidence: [panels 1](M2_visual/review_1.png), [2](M2_visual/review_2.png), [3](M2_visual/review_3.png), [4](M2_visual/review_4.png).", '']
        L += ['Twenty accepted changed words were selected deterministically, prioritizing blind mark-error cards and limiting repeated cards/sources. Crops were viewed directly; the review does not tune either model or any acceptance rule. This targeted check is not a precision estimate.', '',
              '| # | Card | Mode | Google → proposal | Matches print? | Pixel observation |',
              '|---:|---|---|---|---|---|']
        for s in spots:
            L.append(f"| {s['review_id']} | {s['id']} | {s['mode']} | {s['google_word']} → {s['proposed_word']} | {s['matches_print']} | {s['observation']} |")
    else:
        L.append('Visual review pending; do not treat this intermediate report as complete.')
    pair_failures = Counter(c['modes']['PRESENCE']['reason'] for c in scored if c['modes']['PRESENCE']['outcome']=='missed')
    L += ['', '## Limits and reproducibility', '',
        'The recognizer itself is out of domain on several crops. HOLD protects many disagreements but does not establish correctness when detector and reader agree incorrectly. New changes on blind marks-correct lines remain a direct limitation. Explicit printed→Google pairs are a lower bound: unenumerated Google errors are not included. Multiple pairs on one card and repeated books are dependent; no binomial confidence interval is claimed.', '',
        'PRESENCE missed reasons: '+json.dumps(pair_failures,ensure_ascii=False)+'.', '',
        f"Runtime receipt: [M2_runtime_receipt.json](M2_runtime_receipt.json). Models, input manifests, crops, protected sources and alignments are SHA-256 bound; the run checked those inputs and protected code unchanged. E3 checkpoint `{receipt['model_bindings'][str(ROOT.parent/'greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt')]}`; R1-A epoch {receipt['r1_epoch']}, `{receipt['model_bindings'][str(ROOT/'artifacts/labelfix_r1/output_3678928/A/best.pt')]}`. The initial run newly aligned all 473 crops and completed recognition plus composition in 54.0 s; [its receipt](M2_initial_runtime_receipt.json) notes the original head-field timing issue. A bound-cache replay verifies the finalized wrapper and completed in {receipt['elapsed_seconds']:.1f} s, {receipt['threads']} Torch threads. No training or threshold fitting.", '',
        '```sh',
        'PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \\',
        '  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/m2_run.py --launch-head e702e666efe23371af9b2dd81392e856509dee9f',
        'PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 \\',
        '  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/m2_score.py',
        'PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 \\',
        '  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/m2_verify.py',
        '```', '',
        'Validation: [M2_validation.json](M2_validation.json), PASS. It verifies model/input/crop/source hashes; exact launch-commit inference sources; 513/473/40 cardinalities; all sample admission and reading-letter identities; FULL acceptance contained in PRESENCE; pair/control aggregation; unchanged native review pixels; and byte-identical initial/replay runtime outputs.', '',
        'Artifacts: [M2_lines.jsonl.gz](M2_lines.jsonl.gz) (all 513 cards, including skips, runtime evidence, Google references, per-mode text/HOLD/change lists); [M2_pairs_scored.jsonl](M2_pairs_scored.jsonl); [M2_pair_ledger.jsonl](M2_pair_ledger.jsonl); [M2_metrics.json](M2_metrics.json); [M2_spotchecks.jsonl](M2_spotchecks.jsonl). Scripts: `scripts/labelfix/m2_run.py`, `scripts/labelfix/m2_score.py`, `scripts/labelfix/m2_review.py`, `scripts/labelfix/m2_verify.py`. Alignment cache: `.cache/labelfix/m2/align_s0.jsonl`.', '']
    summary = (f"M2 RESULT: {pooled['inferred']} lines/12 sources; Google mark errors {errors}: "
        f"PRESENCE corrected {p['errors'].get('corrected',0)} HOLD {p['errors'].get('HOLD',0)} missed {p['errors'].get('missed',0)}; "
        f"FULL corrected {f['errors'].get('corrected',0)} HOLD {f['errors'].get('HOLD',0)} missed {f['errors'].get('missed',0)}; "
        f"new changes on marks-correct cards PRESENCE {p['accepted_changed_slots']} FULL {f['accepted_changed_slots']}; "
        f"lines with HOLD PRESENCE {pct(p['lines_with_HOLD'],pooled['inferred'])} FULL {pct(f['lines_with_HOLD'],pooled['inferred'])}")
    L.append(summary)
    (OUT/'M2_REPORT.md').write_text('\n'.join(L)+'\n')
    return summary


def replay_report(metrics,scored,receipt):
    """Candidate reports must never repeat the historical M2 fixed numbers."""
    q=metrics['POOLED'];active=sum(v['inferred']>0 for k,v in metrics.items() if k!='POOLED')
    p=q['modes']['PRESENCE'];f=q['modes']['FULL'];excluded=receipt['scope_excluded_lines']
    L=['# M2 — S7 cached detector replay','',
       f"{q['cards']} inventory cards; 473 original Greek/mixed eligible cards; {excluded} monotonic lines excluded; {q['inferred']} checked lines / {active} active source cohorts. The original 40 Cyrillic cards remain excluded. CTC and R1 forward passes: 0. Substitutions: {receipt['substitutions']}.",'',
       'Scope comes only from independent pixel-review script classes. Unknown/mixed classes remain eligible. Inference receives pixels, cached recognizer letters/spans and cached R1 outputs; reference texts and blind verdicts enter scoring only. Print proposals are preserved; disagreement, unresolved localization and UNSEEN coverage remain HOLD.','',
       f"All {len(scored)} original mark-only error pairs remain scored. Changed accepted slots on marks-correct cards are conditional upper bounds, not new visual adjudications.",'',
       '| mode | corrected / HOLD / missed | new accepted changed slots | HOLD / checked | HOLD / original 473 |',
       '|---|---|---|---|---|']
    for mode in MODES:
        v=q['modes'][mode];e=v['errors'];n=v['lines_with_HOLD']
        L.append(f"| {mode} | {e.get('corrected',0)} / {e.get('HOLD',0)} / {e.get('missed',0)} | {v['accepted_changed_slots']} | {n}/{q['inferred']} ({pct(n,q['inferred'])}) | {n}/473 ({pct(n,473)}) |")
    L+=['','| source | checked | PRESENCE corrected / HOLD / missed | capital-breathing corrected | new accepted changed slots |',
        '|---|---|---|---|---|']
    for source,v in metrics.items():
        w=v['modes']['PRESENCE'];e=w['errors'];c=w['by_type']['capital_breathing_dropped_or_apostrophe']
        L.append(f"| {source} | {v['inferred']} | {e.get('corrected',0)} / {e.get('HOLD',0)} / {e.get('missed',0)} | {c.get('corrected',0)} | {w['accepted_changed_slots']} |")
    summary=(f"M2 RESULT: {q['inferred']} lines/{active} active sources; monotonic excluded {excluded}; Google mark errors {len(scored)}: "
        f"PRESENCE corrected {p['errors'].get('corrected',0)} HOLD {p['errors'].get('HOLD',0)} missed {p['errors'].get('missed',0)}; "
        f"FULL corrected {f['errors'].get('corrected',0)} HOLD {f['errors'].get('HOLD',0)} missed {f['errors'].get('missed',0)}; "
        f"new changes PRESENCE {p['accepted_changed_slots']} FULL {f['accepted_changed_slots']}; "
        f"HOLD lines PRESENCE {pct(p['lines_with_HOLD'],q['inferred'])} checked / {pct(p['lines_with_HOLD'],473)} original")
    L+=['','Complete source/type/mode metrics: [M2_metrics.json](M2_metrics.json). Native runtime evidence and per-slot holds: [M2_lines.jsonl.gz](M2_lines.jsonl.gz). Exact error-pair ledger: [M2_pairs_scored.jsonl](M2_pairs_scored.jsonl). Hash bindings: [M2_runtime_receipt.json](M2_runtime_receipt.json).','',summary]
    (OUT/'M2_REPORT.md').write_text('\n'.join(L)+'\n')
    return summary


def main():
    import argparse
    global OUT, CACHE
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',type=Path)
    ap.add_argument('--no-spotcheck-queue',action='store_true',help='score only; useful for candidates with fewer than 20 accepted changes')
    a=ap.parse_args()
    if a.output_dir is not None:OUT=CACHE=a.output_dir
    inv = inventory()
    receipt = json.loads((OUT/'M2_runtime_receipt.json').read_text())
    assert receipt['runtime_sha256']==sha(CACHE/'runtime.jsonl')
    assert receipt['alignment_sha256']==sha(Path(receipt.get('alignment_path',CACHE/'align_s0.jsonl')))
    runtime = {r['id']:r for r in rows(CACHE/'runtime.jsonl')}
    assert set(runtime)=={r['id'] for r in inv}
    ledger = pair_ledger(inv)
    byid = {r['id']:r for r in inv}
    scored = [score_case(c,byid[c['id']],runtime[c['id']]) for c in ledger if c['included']]
    write_rows(OUT/'M2_pair_ledger.jsonl', ledger)
    write_rows(OUT/'M2_pairs_scored.jsonl', scored)
    cases_by_line = defaultdict(list)
    for c in scored:
        cases_by_line[c['id']].append(c)
    lines = []
    for r in inv:
        run = runtime[r['id']]
        changes, change_coverage = changes_for(r,run)
        lines.append(dict(**r, line_id=r['key']['line_id'], **{k:v for k,v in run.items() if k!='id'},
            changes=changes, reference_change_alignment_coverage=change_coverage,
            error_pairs=cases_by_line[r['id']],
            blind_flags=dict(letter_problem=r['verdict']['letters']!='y',
                crop_problems=sorted(set(r['verdict']['errors']) & {'crop_clipped','crop_overrun','merged_two_lines'}))))
    write_rows(OUT/'M2_lines.jsonl.gz', lines)
    metrics = summarize(inv,runtime,scored,lines)
    (OUT/'M2_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
    queue = [] if a.no_spotcheck_queue else choose_spotchecks(lines)
    print(report(metrics,ledger,scored,lines,receipt))
    score_binding=dict(schema='m2-score-v1',scorer_sha256=sha(Path(__file__)),
        runtime_sha256=receipt['runtime_sha256'],outputs={n:sha(OUT/n) for n in
        ('M2_metrics.json','M2_REPORT.md','M2_pair_ledger.jsonl','M2_pairs_scored.jsonl')})
    (OUT/'M2_score_receipt.json').write_text(json.dumps(score_binding,indent=2)+'\n')
    print('SPOTCHECK QUEUE',json.dumps(queue,ensure_ascii=False))


if __name__=='__main__':
    main()
