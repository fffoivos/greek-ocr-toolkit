"""SF7-rc1, additive to frozen SF6. Saved evidence only; no inference.

A/B are addition rules, independent of the reader mode (production ENSEMBLE_AB).
Mark replacements use the preregistered reader-alone rule.
"""
from collections import Counter
from copy import deepcopy
from difflib import SequenceMatcher
import hashlib
import json
import unicodedata as ud
from pathlib import Path

from greekocr.labelfix import release_gate as S6
from greekocr.labelfix.text import clusters, nfd, nfc, is_letter

POLICY = 'sf7-release-v1'
PREREGISTRATION = 'docs/labelfix/spellcheck/SF7_PREREGISTRATION.md'
PREREGISTRATION_SHA256 = '64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d'
SF6_SHA256 = '6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406'
ALIASES = S6.LEADING_QUOTES + "'’´ʼ῾᾿᾽"


def policy_binding():
    root = Path(__file__).resolve().parents[2]
    sources = dict(S6.policy_binding()['sources'])
    for path in ('scripts/labelfix/release_gate_sf7.py', PREREGISTRATION,
                 'scripts/labelfix/clariden/sf7_recompose.py',
                 'scripts/labelfix/clariden/l1r_recompose_ext.py',
                 'scripts/labelfix/clariden/sf7_job.sbatch'):
        sources[path] = hashlib.sha256((root/path).read_bytes()).hexdigest()
    if sources[PREREGISTRATION] != PREREGISTRATION_SHA256:
        raise ValueError('preregistration changed')
    return dict(schema=POLICY, sources=sources,
                preregistration_sha256=PREREGISTRATION_SHA256,
                sha256=hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest())


def _parts(c):
    return {p for p, m in S6.R.MARKS.items() if m in c.marks}


def _clean(slot, zone):
    ev = slot.get('evidence', {})
    edge = 'bottom' if zone == 'below' else 'top'
    return bool(slot and not any(slot.get(k) for k in
        ('localisation_unknown', 'segmentation_uncertain', 'unnamed', 'ambiguity', 'unseen_zones'))
        and slot.get('physical_resolved') is not False
        and ev.get('clipped_'+edge) is False
        and not ev.get('clipped_left') and not ev.get('clipped_right')
        and not ev.get('uncertainty') and ev.get('evidence_state') != 'UNKNOWN'
        and ev.get('observation', {}).get(zone) not in ('UNSEEN', 'UNKNOWN'))


def owned_ink(raw, slot, zone):
    """Positive native ink, uniquely assigned by the saved detector to this slot.

    Preposed capital ink can lie left of the locator window. Ownership comes
    from saved source IDs, not from horizontal overlap with a padded crop.
    """
    if not _clean(slot, zone):
        return []
    result = []
    for blob in slot.get('evidence', {}).get(zone, ()):
        ids = set(blob.get('source_ids', ()))
        box = blob.get('bbox', ())
        if not (ids and len(box) == 4 and box[0] < box[2] and box[1] < box[3]
                and blob.get('area', 0) > 0 and not blob.get('touches_border')):
            continue
        others = [b for s in raw.get('slots', ()) if s['start'] != slot['start']
                  for z in ('above', 'below', 'apostrophes')
                  for b in s.get('evidence', {}).get(z, ())]
        if any(ids & set(b.get('source_ids', ())) for b in others):
            continue
        result.append(blob)
    return result


def _compound(raw, slot, wanted):
    """Certify one named mark compound, not a count of connected components.

    A compound may have a breathing curl and an adjacent accent stroke. More
    blobs than named marks, separated blobs, or shared IDs are unresolved.
    """
    blobs = owned_ink(raw, slot, 'above')
    parts = set(slot.get('parts', ())) & {'psili', 'dasia', 'acute', 'grave', 'circumflex'}
    if not blobs or not wanted <= parts or len(blobs) > len(parts):
        return []
    ordered = sorted(blobs, key=lambda b: b['bbox'][0])
    for a, b in zip(ordered, ordered[1:]):
        x, y = a['bbox'], b['bbox']
        if b.get('source') != a.get('source') or y[0]-x[2] > .35*min(x[3]-x[1], y[3]-y[1]):
            return []
        if min(x[3], y[3]) <= max(x[1], y[1]):
            return []
    return ordered


def quote_decisions(original, proposal, runtime):
    old, new, rec = map(S6._letters, (original, proposal, runtime['recogniser_text']))
    if not [c.base for c in old] == [c.base for c in new] == [c.base for c in rec]:
        return []
    raw = runtime['detector']; slots = {s['start']: s for s in raw['slots']}
    cs = clusters(nfd(original)); boundary = 0; result = []
    for i, c in enumerate(cs):
        if is_letter(c.base):
            boundary += 1
            continue
        if not (c.base in ALIASES and not c.marks and i+1 < len(cs)
                and cs[i+1].base.isupper() and boundary < len(new)):
            continue
        wanted = (_parts(new[boundary]) - _parts(old[boundary])) & {
            'psili', 'dasia', 'acute', 'grave', 'circumflex'}
        restoring = bool(wanted)
        if not wanted:
            wanted = _parts(new[boundary]) & {'psili', 'dasia', 'acute', 'grave', 'circumflex'}
            if not wanted:
                continue
        slot = slots.get(rec[boundary].start, {})
        blobs = _compound(raw, slot, wanted)
        mark_ids = {j for b in blobs for j in b['source_ids']}
        quotes = raw.get('opening_quotes', ()) if boundary == 0 else slot.get('evidence', {}).get('quotes', ())
        quote_ids = {j for b in quotes if isinstance(b, dict) for j in b.get('source_ids', ())}
        # A separate quote requires native IDs and disjoint physical groups.
        separate = bool(quote_ids and mark_ids and not quote_ids & mark_ids)
        if not restoring and not separate:
            continue
        operation = 'KEEP_BOTH' if separate else 'CONSUME_ALIAS' if blobs and not quotes else 'HOLD'
        result.append(dict(rule='SQ1', boundary=boundary, alias=c.base,
            original_start=c.start, recogniser_start=rec[boundary].start,
            operation=operation, mark_source_ids=sorted(mark_ids), quote_source_ids=sorted(quote_ids),
            component_count=len(blobs), semantic_mark_groups=1 if blobs else None))
    return result


def _quote_text(text, decisions):
    """Apply the SAME physical decision to every punctuation/edit surface."""
    by = {d['boundary']: d for d in decisions if d['operation'] != 'HOLD'}
    cs = clusters(nfd(text)); out = []; boundary = 0
    for i, c in enumerate(cs):
        d = by.get(boundary)
        if d and c.base in ALIASES and not c.marks and i+1 < len(cs) and cs[i+1].base.isupper():
            continue
        if is_letter(c.base):
            if d and d['operation'] == 'KEEP_BOTH':
                out.append(d['alias'])
            boundary += 1
        out.append(c.base+c.marks)
    return nfc(''.join(out))


def mark_operations(original, proposal):
    """Pair removed and added marks at the same slot, same family first.

    Remaining unmatched marks are pure additions/deletions. Retaining an
    existing accent while adding a subscript is therefore always an addition.
    """
    a, b = S6._letters(original), S6._letters(proposal)
    if [c.base for c in a] != [c.base for c in b]:
        return []
    events = []
    for i, (x, y) in enumerate(zip(a, b)):
        removed, added = _parts(x)-_parts(y), _parts(y)-_parts(x)
        rm, ad = set(removed), set(added); paired = set()
        for x in sorted(removed):
            choices = sorted(ad, key=lambda y: (S6.kinds([x]) != S6.kinds([y]), y))
            if choices:
                y = choices[0]; ad.remove(y); rm.remove(x); paired.update((x, y))
        for part in sorted(removed | added):
            substitute = part in paired
            events.append(dict(boundary=i, part=part, direction='remove' if part in removed else 'add',
                               operation='SUBSTITUTE' if substitute else 'DELETE' if part in removed else 'ADD'))
    return events


def compose(original, runtime, *, addition_rule='A', mode='ENSEMBLE_AB'):
    if addition_rule not in ('A', 'B'):
        raise ValueError('addition_rule must be A or B')
    decision = S6.compose_runtime(runtime, mode)
    quotes = quote_decisions(original, decision['text'], runtime)
    go = _quote_text(original, quotes)
    rec = _quote_text(runtime['recogniser_text'], quotes)
    rendered = _quote_text(decision['text'], quotes)
    proposal, census = S6.release_text(go, rec, rendered)
    # All composer punctuation vetoes are recomputed through that same map.
    holds = [dict(start=s['start'], letter=s['base'], reason=r)
             for s in decision['slots'] for r in s['hold_reasons'] if not r.startswith('edit_guard:')]
    holds += [dict(start=0, letter='', reason=r) for r in
              S6.edit_guard(go, rec)+S6.edit_guard(go, proposal)+S6.edit_guard(rec, rendered)]
    holds += [dict(start=d['original_start'], letter=d['alias'], reason='sf7:quote_group_unresolved')
              for d in quotes if d['operation'] == 'HOLD']
    operations = mark_operations(go, proposal)
    replacements = {(o['boundary'], S6.R.MARKS[o['part']]) for o in operations
                    if o['direction'] == 'remove' and o['operation'] == 'SUBSTITUTE'}
    deletions = S6.deletion_guard(go, proposal, runtime, decision)
    accepted = {s['start']: s for s in decision['slots']}
    rec_letters = S6._letters(runtime['recogniser_text'])
    raw = runtime['detector']; slots = {s['start']: s for s in raw['slots']}
    for event in deletions:
        if (event['letter'], event['character']) in replacements:
            s = accepted.get(event['recogniser_start'], {})
            event.update(allowed=bool(s.get('label_status') == 'ACCEPT' and not s.get('hold_reasons')),
                         operation='SUBSTITUTE', reason=None)
        if not event['allowed']:
            holds.append(dict(start=event['start'], letter=event['character'], reason=event['reason'] or 'sf7:reader_substitution_unresolved'))
    additions = []
    for op in operations:
        if op['direction'] != 'add':
            continue
        c = rec_letters[op['boundary']]; s = slots.get(c.start, {}); d = accepted.get(c.start, {})
        part = op['part']; zone = 'below' if part == 'subscript' else 'above'
        reader = d.get('label_status') == 'ACCEPT' and not d.get('hold_reasons') and part in d.get('r1_parts', ())
        ink = owned_ink(raw, s, zone)
        detector = bool(ink)  # Presence, never detector naming as a reader vote.
        recogniser = S6._recogniser_scored(runtime, s, s.get('evidence', {}).get('window')) and part in _parts(c)
        if op['operation'] == 'SUBSTITUTE':
            allowed = bool(reader)
        elif addition_rule == 'A':
            allowed = bool(reader and (part != 'subscript' or detector))
        else:
            allowed = bool(reader and (detector or recogniser))
        event = dict(op, recogniser_start=c.start, signals=dict(reader=bool(reader), detector=detector,
            recogniser=bool(recogniser)), source_ids=sorted({j for b in ink for j in b['source_ids']}), allowed=allowed)
        additions.append(event)
        if not allowed:
            holds.append(dict(start=c.start, letter=c.base, reason='sf7:insertion_needs_presence:'+part))
    return dict(policy=POLICY, variant=addition_rule, preregistration_sha256=PREREGISTRATION_SHA256,
        decision=decision, proposal=proposal, elision_census=census, hold_slots=holds,
        rule_traces=dict(quotes=quotes, marks=operations, deletions=deletions, additions=additions))


def overlay(record, runtime, addition_rule, binding, mode='ENSEMBLE_AB'):
    from scripts.labelfix.clariden.l1_common import label_sha, hold_reason
    from greekocr.labelfix.text import elision_alias_key
    result = dict(line_id=record['id'], original_label_sha256=label_sha(record['label']),
        changes=[], hold_slots=[], detector_version=binding['detector'], r1_sha=binding['r1_sha256'],
        policy_sha=binding['policy_sha256'], release_policy=POLICY, policy=POLICY, variant=addition_rule,
        preregistration_sha256=PREREGISTRATION_SHA256, rule_traces={})
    if record['script_class'] != 'greek_poly':
        return dict(result, status='out_of_scope')
    composed = compose(record['label'], runtime, addition_rule=addition_rule, mode=mode)
    d = composed['decision']; proposal = composed['proposal']
    result.update(evidence_sha256=d['evidence_sha256'], opening_quotes=d['opening_quotes'],
        gate_decisions=d['slots'], composed_text=proposal,
        hold_slots=[dict(start=h['start'],letter=h['letter'],
            reason='deletion_uncertain' if str(h['reason']).startswith('sf6:deletion_') else
                   'edit_guard' if str(h['reason']).startswith('edit_guard:') else hold_reason(str(h['reason'])),
            detail=h['reason']) for h in composed['hold_slots']],
        rule_traces=composed['rule_traces'], deletion_checks=composed['rule_traces']['deletions'],
        elision_census=composed['elision_census'],
        alias_only=(nfd(record['label']) != nfd(d['text']) and
                    elision_alias_key(record['label']) == elision_alias_key(d['text'])))
    if result['hold_slots']:
        return dict(result, status='hold')
    if nfd(record['label']) == nfd(proposal):
        return dict(result, status='unchanged', label=record['label'])
    old, new = nfd(record['label']), nfd(proposal)
    for tag, i, j, lo, hi in SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag != 'equal':
            context=i
            if (lo<hi and ud.combining(new[lo])) or (i<j and ud.combining(old[i])):
                context-=1
            while 0<=context<len(old) and ud.combining(old[context]):context-=1
            letter=old[context] if 0<=context<len(old) and old[context].isalpha() else ''
            evidence=dict(recogniser_text=runtime['recogniser_text'],agreement=mode,
                slots=[dict(start=z['start'],letter=z['base'],r1_coverage=z.get('r1_coverage'),
                    segmentation_uncertain=z.get('segmentation_uncertain'),localisation_unknown=z.get('localisation_unknown'),
                    hold_reasons=z.get('hold_reasons'),detector_parts=z.get('detector_parts'),r1_parts=z.get('r1_parts'),
                    peer_arm=z.get('peer_arm'),peer_prediction=z.get('peer_prediction'),peer_coverage=z.get('peer_coverage'),
                    locator_span=z.get('locator_span'),mark_probabilities=z.get('mark_probabilities'),evidence=z.get('evidence'))
                    for z in d['slots']],opening_quotes=d['opening_quotes'],detector_text=runtime['detector']['text'])
            result['changes'].append(dict(start=i,letter=letter,**{'from':old[i:j],'to':new[lo:hi]},evidence=evidence))
    return dict(result, status='corrected', label=proposal)
