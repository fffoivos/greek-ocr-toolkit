"""Two independent gate-passing votes produce proposals; labels are never mutated."""
MEANINGS = ('raised dot','baseline dot','comma','hyphen','en dash','em dash','space','nothing','other','unreadable')
DASHES = ('hyphen','en dash','em dash')
GLYPHS = dict(zip(MEANINGS[:8], ('·','.',',','-','–','—',' ','')))


def control_matches(truth, meaning):
    return meaning in DASHES if truth == 'any dash' else meaning == truth


def decide(slot, reads):
    if slot.get('read_reason')=='geometry-only':
        from .prune import has_gap_component
        if reads or slot.get('glyph') or slot['geometry']['geom_status']!='ok' or has_gap_component(slot):
            raise ValueError('invalid geometry-only decision')
        return dict(slot_id=slot['slot_id'],line_id=slot['line_id'],truth_candidate='nothing',
            status='truth_candidate',reason='nothing (geometry)',reads=[],agreement=True,
            confidence='geometry',tags=[],edit_candidate=None,edit=None,apply_edit=False,void_votes=[])
    if len({r['reader'] for r in reads}) != len(reads):
        raise ValueError('duplicate reader vote')
    usable = [r for r in reads if r.get('context_status')=='VALID' and r.get('read_status')=='ok'
              and r.get('confidence')=='high' and r.get('meaning') in GLYPHS]
    candidate = None
    reason = 'two_valid_high_confidence_votes_required'
    from collections import Counter
    counts = Counter(r['meaning'] for r in usable)
    winners = [meaning for meaning, count in counts.items() if count >= 2]
    if len(winners)==1:
        candidate = winners[0]; reason = 'two_agreeing_valid_reads'
    elif len(usable)>=2: reason = 'reader_disagreement'
    elif any(r.get('context_status')=='INVALID' for r in reads): reason = 'invalid_context_provenance'
    elif any(r.get('context_status')=='VOID' for r in reads): reason = 'void_context'
    elif any(r.get('meaning') in ('other','unreadable') for r in reads): reason = 'unreadable_or_other'
    elif any(r.get('confidence')!='high' for r in reads): reason = 'low_confidence'
    dash = slot.get('dash', {})
    if candidate in DASHES and candidate != dash.get('geometric_type'):
        candidate = None; reason = 'dash_geometry_disagreement_or_unavailable'
    if slot.get('geometry',{}).get('geom_status') != 'ok':
        candidate = None; reason = 'geometry_unavailable'
    glyph = slot.get('glyph', slot.get('google_glyph'))
    edit = None
    if candidate=='raised dot' and glyph in ('-', '.') and 'thousands' in slot['grammar_candidates']:
        edit = dict(start=slot['start'],end=slot['end'],original=glyph,replacement='·')
    return dict(slot_id=slot['slot_id'],line_id=slot['line_id'],truth_candidate=candidate,
        status='truth_candidate' if candidate is not None else 'lead_review',reason=reason,
        reads=reads,agreement=bool(candidate),confidence='high' if candidate else 'unresolved',
        tags=[candidate] if candidate in DASHES else [],edit_candidate=edit,edit=None,apply_edit=False,
        void_votes=[dict(r,vote_role='second_only') for r in reads if r.get('context_status')=='VOID'])


def decode_and_gate(key, answers):
    if len(key['readers']) != 1: raise ValueError('one reader required')
    ids = next(iter(key['readers'].values()))
    if len(ids)!=len(set(ids)) or set(ids)!=set(key['items']): raise ValueError('inconsistent key')
    if len(answers)!=len(ids) or [a.get('item_id') for a in answers]!=ids:
        raise ValueError('missing, duplicate, unexpected or out-of-order answers')
    decoded=[]; wrong=0; abstain=0
    for a in answers:
        item=key['items'][a['item_id']]
        meaning=item['option_map'].get(a.get('answer'))
        if meaning not in MEANINGS or a.get('confidence') not in ('high','low'):
            raise ValueError('invalid answer')
        truth=item['control_truth']
        if truth is not None:
            if truth not in (*MEANINGS, 'any dash'): raise ValueError('unsealed control truth')
            if meaning=='unreadable' and truth!='any dash': abstain+=1
            elif not control_matches(truth, meaning): wrong+=1
        decoded.append(dict(a,meaning=meaning,slot_id=item['slot_id'],control=truth is not None))
    return dict(status='VOID' if wrong>1 else 'VALID',wrong=wrong,abstentions=abstain),decoded
