"""Independent line reading: recogniser letters, detector marks, cached locations.

No Google/human text, lexicon, truth labels or recogniser forward pass enters here.
Use read_line_details for parallel unnamed/localisation flags, constraint
constraint flags and held-back/tied proposals. Print output preserves detected
marks. Only output="normalised" may remove marks; filtered=False is raw replay.
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image
from . import ink as I
from .ctc_align import Alignment
from .markshape import name_marks
from .text import clusters, nfd, nfc, tokenize
from .segmentation import recogniser_slots

MARKS = dict(psili='\u0313', dasia='\u0314', acute='\u0301', grave='\u0300',
             circumflex='\u0342', subscript='\u0345', dialytika='\u0308')
ELISION = "'’ʼ᾽"


@dataclass
class LineReading:
    """Independent text with slot evidence and parallel unresolved-mark flags."""
    text: str
    slots: list
    unnamed: list
    opening_quotes: list = field(default_factory=list)
    removed_by_constraint: list = field(default_factory=list)
    constraint_flags: list = field(default_factory=list)


def render_reading(text, slots):
    """Replace every combining mark, preserving base characters and punctuation."""
    by={s['start']:s for s in slots}
    out=[]
    for cl in clusters(nfd(text)):
        if cl.base in ELISION:
            continue
        s=by.get(cl.start)
        if s is None:
            out.append(cl.base)
        else:
            out.append(cl.base+''.join(MARKS[p] for p in s.get('parts',()) if p in MARKS))
            if s.get('apostrophe'):
                out.append('’')
    return nfc(''.join(out))


# Qualified against S6 PRINT truth by scripts/labelfix/k1_validate.py.
# The audit may request every rule with enabled_rules=None; runtime uses this
# explicit allowlist. A printed-mark conflict holds back the entire subrule.
CONSTRAINT_RULES = frozenset({
    'C2:mark_on_consonant', 'C5:dialytika_not_on_iota_upsilon',
    'C6:subscript_not_under_alpha_eta_omega', 'C2:two_breathings',
    'C2:two_accents_one_letter', 'C2:breathing_with_dialytika',
    'C1:breathing_not_initial', 'C1:breathing_after_consonant_start',
    'C1:smooth_breathing_on_rho', 'C3:two_accents',
    'C4:grave_not_final', 'C4:circumflex_on_short_vowel',
    'C4:circumflex_before_penult',
})
APPLIED_CONSTRAINT_RULES = CONSTRAINT_RULES - {
    # A single DEV printed breathing conflicts with C1; 16 held-out printed
    # accents conflict with C3. See K1_REPORT.md and K1_printed_conflicts.jsonl.
    'C1:breathing_after_consonant_start', 'C3:two_accents',
}
_ACCENT_PARTS = frozenset(('acute', 'grave', 'circumflex'))
_BREATH_PARTS = frozenset(('psili', 'dasia'))


def _record(value):
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return value.to_record() if hasattr(value, 'to_record') else vars(value)


def _mark_support(slot, part):
    """Actual detector support, with shared whole-set evidence explicit.

    Rank: classifier probability, area / x-height squared, then negative
    horizontal distance / x-height. Whole-set names share support; no invented
    per-mark probabilities or blob assignments break ties.
    """
    reader_support=slot.get('mark_support_source')=='reader'
    ev = _record(slot.get('reader_evidence') if reader_support else slot.get('evidence'))
    naming = {} if reader_support else _record(slot.get('naming'))
    blobs = ev.get('below' if part == 'subscript' else 'above', [])
    records = [r for r in naming.get('per_blob', ()) if part in r['parts']]
    probability = naming.get('probability') if part != 'subscript' else None
    source = 'whole_set_shared'
    if records and part != 'subscript':
        blobs = [blobs[r['blob']] for r in records if r['blob'] < len(blobs)]
        probability = min(r['probability'] for r in records) if all(r.get('probability') is not None for r in records) else None
        source = 'per_blob'
    if 'mark_probabilities' in slot:
        probability = slot['mark_probabilities'].get(part)
        source = 'reader_head'
    bs = [_record(b) for b in blobs]
    xh = max(float(ev.get('xh', 1)), 1.)
    body = ev.get('body') or slot.get('region_bounds')
    center = sum(body) / 2 if body else None
    area = sum(float(b.get('area', 0)) for b in bs)
    distance = (sum(abs((b['bbox'][0] + b['bbox'][2]) / 2 - center)
                    * float(b.get('area', 0)) for b in bs) / area
                if center is not None and area else None)
    return dict(probability=probability, blob_area=area if bs else None,
                distance_to_letter=distance, xh=xh, source=source,
                blobs=[b['bbox'] for b in bs],
                rank=[float(probability) if probability is not None else 0.,
                      area / (xh*xh), -distance / xh if distance is not None else 0.])


def _normalise_constraints(reading: LineReading, *, enabled_rules=APPLIED_CONSTRAINT_RULES):
    """Return a copy with qualified impossible marks removed, plus a receipt.

    None enables all rules for offline qualification. Held-back proposals and
    tied conflicts are parallel flags, never deletions. Missing marks are never
    supplied. Base letters, punctuation, physical evidence and input are intact.
    """
    from . import constraints as C
    enabled = CONSTRAINT_RULES if enabled_rules is None else frozenset(enabled_rules)
    slots = [dict(s, parts=list(s.get('parts', ()))) for s in reading.slots]
    removed, flags = [], list(reading.constraint_flags)
    # Output NFD offsets differ from the recogniser offsets as marks change.
    # Join by letter order, retaining each original slot/start in all receipts.
    text_cls = clusters(nfd(reading.text))
    letters = [c for c in text_cls if c.base.isalpha()]
    if len(letters) != len(slots) or any(c.base != s['base'] for c,s in zip(letters, slots)):
        raise ValueError('reading letters and evidence slots differ')
    at = {c.start: i for i,c in enumerate(letters)}
    groups = []
    for token in tokenize(reading.text):
        group = []
        for c in clusters(token.core):
            if c.base.isalpha():
                group.append(at[token.core_start+c.start])
            elif group:
                groups.append((group, True)); group = []
        if group:
            groups.append((group, False))

    def describe(ref):
        i, k = ref; s = slots[i]; p = s['parts'][k]
        return dict(letter=s['base'], slot=s.get('component_slot', i),
                    start=s['start'], part=p, occurrence=k, evidence=_mark_support(s,p))

    def drop(rule, refs, conflict=False):
        refs = [(i,k) for i,k in refs if k < len(slots[i]['parts'])]
        if not refs:
            return
        choices = [describe(r) for r in refs]
        if conflict and len(refs) > 1:
            ranks = [tuple(x['evidence']['rank']) for x in choices]
            weakest = min(ranks)
            if ranks.count(weakest) > 1:
                flags.append(dict(rule=rule, reason='evidence_tie', alternatives=choices))
                return
            chosen = ranks.index(weakest)
            refs, choices = [refs[chosen]], [dict(choices[chosen], alternatives=choices)]
        for (i,k), receipt in sorted(zip(refs,choices), reverse=True):
            receipt = dict(receipt, rule=rule)
            if rule.startswith('C4:'):
                receipt['alternative'] = dict(action='keep_mark', part=receipt['part'],
                                               evidence=receipt['evidence'])
            if rule in enabled:
                slots[i]['parts'].pop(k)
                removed.append(receipt)
            else:
                flags.append(dict(receipt, reason='rule_held_back'))

    for gi, (ids, hyphen_part) in enumerate(groups):
        if all(slots[i]['base'].isupper() for i in ids):
            continue
        for i in ids:
            s = slots[i]; base = s['base'].lower()
            for part in list(s['parts']):
                if part not in s['parts']:
                    continue
                rule = None
                if part == 'dialytika' and base not in 'ιυ':
                    rule = 'C5:dialytika_not_on_iota_upsilon'
                elif part == 'subscript' and base not in 'αηω':
                    rule = 'C6:subscript_not_under_alpha_eta_omega'
                elif not C.is_vowel(base) and (part in _ACCENT_PARTS or part in _BREATH_PARTS and base != 'ρ'):
                    rule = 'C2:mark_on_consonant'
                if rule:
                    drop(rule, [(i,s['parts'].index(part))])
            for family, rule in [(_BREATH_PARTS,'C2:two_breathings'), (_ACCENT_PARTS,'C2:two_accents_one_letter')]:
                refs = [(i,k) for k,p in enumerate(s['parts']) if p in family]
                while len(refs) > 1:
                    before = len(s['parts']); drop(rule,refs,True)
                    if len(s['parts']) == before: break
                    refs = [(i,k) for k,p in enumerate(s['parts']) if p in family]
            refs = [(i,k) for k,p in enumerate(s['parts']) if p in _BREATH_PARTS or p == 'dialytika']
            if any(p in _BREATH_PARTS for p in s['parts']) and 'dialytika' in s['parts']:
                drop('C2:breathing_with_dialytika',refs,True)
        def current():
            return clusters(''.join(slots[i]['base']+''.join(MARKS[p] for p in slots[i]['parts'] if p in MARKS) for i in ids))
        cls = current(); syl = C.syllables(cls)
        rho_pair = set()
        for j in range(1, len(ids)-1):
            if cls[j].base.lower() == cls[j+1].base.lower() == 'ρ':
                rho_pair.update((j,j+1))
        first = cls[0].base.lower()
        allowed = {0}
        if C.is_vowel(first) and syl and len(syl[0]) == 2:
            allowed = {syl[0][1]}
        coronis = [j for j in (syl[0] if syl else []) if 'psili' in slots[ids[j]]['parts']]
        coronis = set(coronis) if first in C.CRASIS_CONSONANTS and len(coronis) == 1 else set()
        for j,i in enumerate(ids):
            for k in reversed(range(len(slots[i]['parts']))):
                part = slots[i]['parts'][k]
                if part not in _BREATH_PARTS or j in rho_pair or j in coronis and part == 'psili':
                    continue
                if C.is_vowel(first):
                    rule = 'C1:breathing_not_initial' if j not in allowed else None
                elif first == 'ρ':
                    rule = ('C1:smooth_breathing_on_rho' if j == 0 and part == 'psili'
                            else 'C1:breathing_not_initial' if j != 0 else None)
                else:
                    rule = 'C1:breathing_after_consonant_start'
                if rule: drop(rule,[(i,k)])
        # Recompute syllables after removals; never refit geometry.
        cls = current(); syl = C.syllables(cls)
        syl_of = {j:k for k,ss in enumerate(syl) for j in ss}
        next_ids = None
        if not hyphen_part and gi+1 < len(groups): next_ids = groups[gi+1][0]
        next_core = ''.join(slots[i]['base'] for i in next_ids) if next_ids else None
        refs = [(i,k) for i in ids for k,p in enumerate(slots[i]['parts']) if p in _ACCENT_PARTS]
        final_accent = any(syl_of.get(ids.index(i)) == len(syl)-1 for i,k in refs)
        enclitic = next_core is None or C.lexicon_key(next_core) in C.ENCLITICS
        if len(refs) > 1 and not (len(refs) == 2 and final_accent and enclitic):
            while len(refs) > 1:
                before = sum(len(slots[i]['parts']) for i in ids)
                drop('C3:two_accents',refs,True)
                if sum(len(slots[i]['parts']) for i in ids) == before: break
                refs = [(i,k) for i in ids for k,p in enumerate(slots[i]['parts']) if p in _ACCENT_PARTS]
        for j,i in enumerate(ids):
            for k in reversed(range(len(slots[i]['parts']))):
                part = slots[i]['parts'][k]; sy = syl_of.get(j)
                if sy is None: continue
                from_end = len(syl)-1-sy
                rule = None
                if part == 'grave' and from_end != 0: rule = 'C4:grave_not_final'
                elif part == 'circumflex':
                    if from_end > 1: rule = 'C4:circumflex_before_penult'
                    elif len(syl[sy]) != 2 and cls[j].base.lower() not in C.LONG_CAPABLE and 'subscript' not in slots[i]['parts']:
                        rule = 'C4:circumflex_on_short_vowel'
                if rule: drop(rule,[(i,k)])
    for original, slot in zip(reading.slots, slots):
        if isinstance(original.get('parts'), tuple):
            slot['parts'] = tuple(slot['parts'])
    by = {c.start:s for c,s in zip(letters,slots)}
    text = nfc(''.join(c.base+(''.join(MARKS[p] for p in by[c.start]['parts'] if p in MARKS)
                             if c.start in by else c.marks) for c in text_cls))
    return replace(reading, text=text, slots=slots,
                   removed_by_constraint=list(reading.removed_by_constraint)+removed,
                   constraint_flags=flags), removed


def apply_constraints(reading: LineReading, *, enabled_rules=APPLIED_CONSTRAINT_RULES,
                      output='print'):
    """Flag orthographic conflicts and HOLD labels, preserving the printed reading.

    Explicit normalised output reproduces the historical deletion policy. The
    policy is advisory: even a supported impossible mark remains in print output.
    """
    if output not in ('print', 'normalised'):
        raise ValueError('output must be print or normalised')
    candidate, removed = _normalise_constraints(reading, enabled_rules=enabled_rules)
    if output == 'normalised':
        return candidate, removed
    flags = list(candidate.constraint_flags)
    flags.extend(dict(r, reason='impossible_by_rule', action='flag') for r in removed)
    slots = [dict(s, parts=s.get('parts', ())) for s in reading.slots]
    affected = set()
    for flag in flags:
        if 'start' in flag: affected.add(flag['start'])
        affected.update(a['start'] for a in flag.get('alternatives', ()) if 'start' in a)
    for s in slots:
        if s['start'] in affected:
            s.update(hold=True, label_status='HOLD')
            s['constraint_flags'] = [f for f in flags if f.get('start') == s['start'] or
                any(a.get('start') == s['start'] for a in f.get('alternatives', ()))]
    # Reapplying the advisory policy must not multiply receipts.
    unique = {}
    for f in flags:
        import json
        unique[json.dumps(f, sort_keys=True)] = f
    return replace(reading, slots=slots, constraint_flags=list(unique.values())), []


def read_ink(ink, recogniser_text, alignment, model, *, filtered=True, output="print"):
    from .case import prepare, estimate_font
    estimate_font(ink)
    slots=recogniser_slots(ink,recogniser_text,alignment)
    prepare(ink,slots)
    located=[s for s in slots if s['component'] is not None]
    apost=I.apostrophe_candidates(ink,[(s['component'],s['base'],s['word_final']) for s in located])
    apost_boxes={(b.x0,b.y0,b.x1,b.y1) for bs in apost.values() for b in bs}
    for i,s in enumerate(located):
        c=s['component']
        # The union is already certified against all character owners. Pass it
        # directly so snap_body cannot include another overlapping character.
        ev=I.mark_evidence(ink,c.x0,c.x1,base_letter=s['base'],certified_body=(c.x0,c.x1), letter_region=s)
        ev.above=[b for b in ev.above if (b.x0,b.y0,b.x1,b.y1) not in apost_boxes]
        s.update(evidence=ev,apostrophe=i in apost)
    # Overhanging ink may enter two windows. Sloping meanlines can clip the
    # same native lobe by one different row, so exact-box equality is too weak.
    proposals=[]
    for s in located:
        for field in ('above','below'):
            for b in getattr(s['evidence'],field):
                proposals.append(dict(slot=s,field=field,blob=b,pixels=b.pixel_keys()))
    roots=list(range(len(proposals)))
    def root(i):
        while roots[i]!=i:
            roots[i]=roots[roots[i]];i=roots[i]
        return i
    for i,p in enumerate(proposals):
        a=p['blob']
        for j,q in enumerate(proposals[:i]):
            b=q['blob']
            if p['field']!=q['field']:continue
            if p['pixels'] & q['pixels']:roots[root(i)]=root(j)
    winners={}
    for i,p in enumerate(proposals):
        key=root(i);b=p['blob'];s=p['slot']
        rank=(abs(b.cx-s['component'].cx),-b.area,s['start'])
        if key not in winners or rank<winners[key][0]:winners[key]=(rank,i)
    accepted={i for rank,i in winners.values()}
    for key, (_, winner) in winners.items():
        group=[p for i,p in enumerate(proposals) if root(i)==key]
        pixels=set().union(*(p['pixels'] for p in group))
        b=proposals[winner]['blob']
        proposals[winner]['blob']=I.blob_from_pixels(ink,pixels,b.source)
        assert proposals[winner]['blob'].pixel_keys()==pixels
    for s in located:
        for field in ('above','below'):
            setattr(s['evidence'],field,[p['blob'] for i,p in enumerate(proposals) if i in accepted and p['slot'] is s and p['field']==field])
    flags=[]
    for s in slots:
        if s.get('localisation_unknown'):
            flags.append(dict(start=s['start'],reason='localisation_unknown'))
        if s['component'] is None:
            s['parts']=();s['unnamed']=()
            continue
        ev=s['evidence']
        names=name_marks(ev,model)
        s.update(parts=names.parts,unnamed=names.unnamed,naming=names)
        flags.extend(dict(start=s['start'],blob=i,reason='unnamed') for i in names.unnamed)
    reserved = [b for s in located for b in s['evidence'].above if b.source == 'preposed']
    quotes = I.opening_quote_candidates(ink,located[0]['component'],reserved) if located else []
    text = render_reading(recogniser_text,slots)
    # Quote glyphs in recogniser text are not evidence of printed punctuation.
    text = text.lstrip('“”«»„\" ')
    if quotes:
        text = '“'+text
    reading = LineReading(text,slots,flags,[b.to_record() for b in quotes])
    return apply_constraints(reading, output=output)[0] if filtered else reading


def read_line_details(crop: str | Path | Image.Image | I.CropInk, recogniser_text: str,
                      alignment: Alignment, model: Any, *, filtered=True, output="print") -> LineReading:
    """Read a crop; retain evidence and constraint receipts (raw: filtered=False)."""
    if isinstance(crop,I.CropInk):
        return read_ink(crop,recogniser_text,alignment,model,filtered=filtered,output=output)
    if isinstance(crop,Image.Image):
        return read_ink(I.analyse(crop),recogniser_text,alignment,model,filtered=filtered,output=output)
    with Image.open(crop) as image:
        return read_ink(I.analyse(image),recogniser_text,alignment,model,filtered=filtered,output=output)


def read_line(crop: str | Path | Image.Image | I.CropInk, recogniser_text: str,
              alignment: Alignment, model: Any, *, filtered=True, output="print") -> str:
    """Transcribe printed marks; output="normalised" explicitly selects deletion."""
    return read_line_details(crop,recogniser_text,alignment,model,filtered=filtered,output=output).text
