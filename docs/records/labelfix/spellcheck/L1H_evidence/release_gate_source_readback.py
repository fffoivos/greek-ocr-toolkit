"""Shared SF2/L1E policy: observation, agreement, K1, and bounded edits.

PRESENCE compares mark families; FULL compares exact mark sets. Neither is
independent print truth. Missing observation always abstains. Punctuation uses
detector opening quotes (canonical “) and word-final elisions (canonical ’).
All other punctuation, spaces and base letters must match for label release.
ENSEMBLE_AB/AE compare A with B/E exactly and do not veto on detector names.
"""
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, fields, replace
import hashlib
import json
import unicodedata as ud
from . import reading as R
from .text import clusters, nfd, GREEK_LETTERS

POLICY = 'l1e-release-v1'
MODES = ('PRESENCE', 'FULL', 'ENSEMBLE_AB', 'ENSEMBLE_AE')
ENSEMBLE_CAVEAT = "A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label experiment."
R1_LETTERS = frozenset('αεηιουωρΑΕΗΙΟΥΩΡ')
LEADING_QUOTES = '“”«»„"'


def policy_binding():
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    paths = [Path(__file__), Path(R.__file__),Path(__file__).with_name('text.py'),
             root/'scripts/labelfix/clariden/l1_common.py',root/'scripts/labelfix/clariden/l1r_recompose.py']
    sources = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return dict(schema=POLICY, sources=sources,
                sha256=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest())


def serialize(rd):
    """Lossless decision/evidence serializer shared by pages and releases."""
    slots=[]
    for i,s in enumerate(rd.slots,1):
        c=s.get('component')
        d={k:v for k,v in s.items() if k not in ('component','evidence','naming')}
        d.update(display_slot=i,parts=list(s.get('parts',())),
                 bbox=[c.x0,c.y0,c.x1,c.y1] if c is not None else s.get('bbox'),
                 component_ids=list(s.get('component_ids',())))
        ev=s.get('evidence',{})
        d['evidence']=ev.to_record() if hasattr(ev,'to_record') else deepcopy(ev)
        nm=s.get('naming',{})
        d['naming']=asdict(nm) if hasattr(nm,'__dataclass_fields__') else deepcopy(nm)
        slots.append(d)
    record=dict(schema='line-reading-sf1-v1',text=rd.text,slots=slots,unnamed=rd.unnamed,
                opening_quotes=rd.opening_quotes,removed_by_constraint=rd.removed_by_constraint,
                constraint_flags=rd.constraint_flags)
    if rd.geometry:record['geometry']=deepcopy(rd.geometry)
    return record


def deserialize(record):
    return R.LineReading(**deepcopy({f.name:record[f.name] for f in fields(R.LineReading) if f.name in record}))


def kinds(parts):
    return {'breathing' if p in ('psili','dasia') else 'accent' if p in ('acute','grave','circumflex') else p for p in parts}


def prediction_index(records):
    result={}
    for p in records:
        if p['start'] in result:raise ValueError('duplicate R1 prediction start')
        result[p['start']]=p
    return result


def _supported(c):
    if c.base not in GREEK_LETTERS:return not c.marks
    if any(m not in R.MARKS.values() for m in c.marks):return False
    counts=Counter(kinds([p]).pop() for m in c.marks for p,v in R.MARKS.items() if v==m)
    if any(n>1 for n in counts.values()):return False
    if counts['breathing'] and counts['dialytika']:return False
    if c.marks and c.base not in R1_LETTERS:return False
    if counts['dialytika'] and c.base.lower() not in 'ιυ':return False
    if counts['subscript'] and c.base.lower() not in 'αηω':return False
    if c.base.lower()=='ρ' and any(k!='breathing' for k in counts):return False
    return True


def _punctuation(text):
    """Remove only leading quote aliases and elisions after Greek word ends."""
    cs=clusters(nfd(text).lstrip(LEADING_QUOTES+' '))
    out=[]
    for i,c in enumerate(cs):
        if c.base in R.ELISION and i and cs[i-1].base in GREEK_LETTERS:
            if i+1==len(cs) or not cs[i+1].base.isalpha():continue
        if not c.base.isalpha():out.append(c.base+c.marks)
    return ''.join(out)


def edit_guard(original, proposal):
    """Return rejection reasons; unchanged unsupported characters are preserved.

    Greek bases and legal mark multiplicities are the only editable letters.
    Non-Greek clusters and unsupported Greek clusters must remain identical.
    Canonical equivalence alone is never a reason to rewrite source bytes.
    """
    a=[c for c in clusters(nfd(original)) if c.base.isalpha() or ud.combining(c.base)]
    b=[c for c in clusters(nfd(proposal)) if c.base.isalpha() or ud.combining(c.base)]
    reasons=[]
    # Preserve the raw spelling of out-of-domain clusters, including decomposed
    # Latin accents. NFC equivalence does not authorize rewriting those bytes.
    raw_a=[c for c in clusters(original) if c.base.isalpha()]
    raw_b=[c for c in clusters(proposal) if c.base.isalpha()]
    if len(raw_a)==len(raw_b):
        for i,(x,y) in enumerate(zip(raw_a,raw_b)):
            decoded=clusters(nfd(x.base+x.marks))[0]
            if (decoded.base not in GREEK_LETTERS or not _supported(decoded)) and x.base+x.marks!=y.base+y.marks:
                reasons.append(f'edit_guard:unsupported_raw_character:{i}')
    if len(a)!=len(b) or [c.base for c in a]!=[c.base for c in b]:
        reasons.append('edit_guard:base_or_character_mismatch')
    else:
        for i,(x,y) in enumerate(zip(a,b)):
            if (not _supported(x) or not _supported(y) or x.base not in GREEK_LETTERS) and (x.base+x.marks!=y.base+y.marks):
                reasons.append(f'edit_guard:unsupported_character:{i}')
    if _punctuation(original)!=_punctuation(proposal):reasons.append('edit_guard:punctuation_mismatch')
    return reasons


def _reader_reasons(slot, prediction, coverage, prefix):
    reasons=[]
    if prediction is None:reasons.append(prefix+'_missing')
    elif not ('parts' in prediction or 'cls' in prediction):reasons.append(prefix+'_prediction_invalid')
    if prediction and prediction.get('base',slot['base'])!=slot['base']:reasons.append(prefix+'_base_mismatch')
    if coverage is None:reasons.append(prefix+'_missing_coverage')
    else:
        if coverage.get('base',slot['base'])!=slot['base']:reasons.append(prefix+'_coverage_base_mismatch')
        if coverage.get('scored') is not True:reasons.append(prefix+'_unscored:'+str(coverage.get('reason')))
        if coverage.get('evidence_state') in (None,'UNKNOWN'):reasons.append(prefix+'_evidence_UNKNOWN')
        if not isinstance(coverage.get('uncertainty'),(list,tuple)):
            reasons.append(prefix+'_uncertainty_not_recorded')
        else:reasons.extend(prefix+'_uncertainty:'+str(z) for z in coverage['uncertainty'])
    if prediction is not None:
        if prediction.get('evidence_state')=='UNKNOWN':reasons.append(prefix+'_evidence_UNKNOWN')
        reasons.extend(prefix+'_uncertainty:'+str(z) for z in (prediction.get('uncertainty') or ()))
        parts=prediction.get('parts',prediction.get('cls','none').split('+'))
        if any(p not in R.MARKS and p!='none' for p in parts):reasons.append(prefix+'_unsupported_mark')
    return reasons


def decide(slot, prediction, coverage, mode, *, flagged=False, peer_prediction=None, peer_coverage=None):
    mode=mode.upper()
    if mode not in MODES:raise ValueError('unknown release mode: '+mode)
    ev=slot.get('evidence',{})
    ev=ev.to_record() if hasattr(ev,'to_record') else ev
    det=list(slot.get('parts',()))
    rp=None if prediction is None else list(prediction.get('parts',prediction.get('cls','none').split('+')))
    if rp==['none']:rp=[]
    reasons=[]
    for key in ('localisation_unknown','segmentation_uncertain'):
        if slot.get(key):reasons.append('detector_'+key)
    if slot.get('physical_resolved') is False or slot.get('ambiguity'):
        reasons.append('detector_physical_unresolved')
    if slot.get('unnamed'):reasons.append('detector_unnamed_mark')
    reasons.extend('crop_UNSEEN:'+z for z in slot.get('unseen_zones',()))
    base=slot['base'].lower()
    relevant={'above':base in 'αεηιουωρ' or bool(det) or bool(rp) or slot.get('apostrophe',False),
              'below':base in 'αηω' or 'subscript' in det or 'subscript' in (rp or []),
              'left':base in 'αεηιουωρ' and slot['base'].isupper(),
              'right':slot.get('word_final',False) or slot.get('apostrophe',False)}
    for zone,direction in [('above','top'),('below','bottom'),('left','left'),('right','right')]:
        if relevant[zone] and ev.get('clipped_'+direction):reasons.append('detector_clipped_'+direction)
        if relevant[zone] and ev.get('observation',{}).get(zone) in ('UNSEEN','UNKNOWN'):
            reasons.append('crop_UNSEEN:'+zone)
    if slot['base'] in R1_LETTERS:
        reasons.extend(_reader_reasons(slot,prediction,coverage,'r1'))
        if mode.startswith('ENSEMBLE_'):
            peer='r1_'+mode[-1]
            reasons.extend(_reader_reasons(slot,peer_prediction,peer_coverage,peer))
            pp=None if peer_prediction is None else peer_prediction.get('parts',peer_prediction.get('cls','none').split('+'))
            if pp==['none']:pp=[]
            if prediction is not None and peer_prediction is not None and set(rp)!=set(pp):
                reasons.append(mode.lower()+'_mark_set_disagreement')
        if prediction is not None:
            if mode in ('PRESENCE','FULL') and (kinds(det)!=kinds(rp) if mode=='PRESENCE' else set(det)!=set(rp)):
                reasons.append('mark_kind_disagreement' if mode=='PRESENCE' else 'mark_set_disagreement')
    elif (det and not mode.startswith('ENSEMBLE_')) or slot.get('unnamed'):reasons.append('r1_unsupported_letter')
    if flagged or slot.get('constraint_flags'):reasons.append('K1:flag')
    if slot.get('hold'):reasons.extend(slot.get('hold_reasons') or ['detector_hold'])
    reasons=list(dict.fromkeys(reasons))
    return dict(action='HOLD' if reasons else 'ACCEPT' if slot['base'] in R1_LETTERS else 'KEEP',
                reasons=reasons,detector_parts=det,r1_parts=rp)


def compose_reading(text, raw, predictions, coverage, mode, k1_flags=(), *, peer_predictions=None, peer_coverage=None):
    """Compose from detector punctuation and R1 names, retaining all HOLD evidence."""
    if isinstance(raw,dict):raw=deserialize(raw)
    cov={c['start']:c for c in coverage}
    if len(cov)!=len(coverage):raise ValueError('duplicate R1 coverage start')
    pcov={c['start']:c for c in (peer_coverage or [])}
    if len(pcov)!=len(peer_coverage or []):raise ValueError('duplicate peer coverage start')
    slots=[]
    flags=[*raw.constraint_flags,*k1_flags]
    for original in raw.slots:
        s=deepcopy({k:v for k,v in original.items() if k not in ('component','evidence','naming')})
        s.update(component=original.get('component'),evidence=original.get('evidence',{}),naming=original.get('naming',{}))
        start=s['start'];p=predictions.get(start)
        if p is not None:
            if 'parts' not in p and 'cls' not in p:
                p=dict(p,evidence_state='UNKNOWN',uncertainty=['invalid_prediction'])
            p=dict(p,parts=p.get('parts',[x for x in p.get('cls','none').split('+') if x!='none']))
        flagged=any(f.get('start')==start or any(a.get('start')==start for a in f.get('alternatives',())) or
                    ('start' not in f and not f.get('alternatives')) for f in flags)
        peer=(peer_predictions or {}).get(start)
        d=decide(s,p,cov.get(start),mode,flagged=flagged,peer_prediction=peer,peer_coverage=pcov.get(start))
        mapping=raw.geometry.get('physical_mapping',{})
        if mapping.get('ambiguous'):
            d['reasons'].append('detector_physical_mapping_ambiguous')
        for variant in raw.geometry.get('substitutions',()):
            if variant not in R.QUALIFIED_GEOMETRY:
                d['reasons'].append('detector_geometry_unqualified:'+variant)
        if d['reasons']:d['action']='HOLD'
        s.update(detector_parts=d['detector_parts'],r1_parts=d['r1_parts'],
                 r1_coverage=deepcopy(cov.get(start)),hold_reasons=d['reasons'],hold=bool(d['reasons']),label_status=d['action'])
        if mode.upper().startswith('ENSEMBLE_'):
            s.update(peer_arm=mode[-1].upper(),peer_prediction=deepcopy(peer),peer_coverage=deepcopy(pcov.get(start)))
        if p is not None and s['base'] in R1_LETTERS:
            s.update(parts=p['parts'],naming={},mark_support_source='reader',reader_evidence={},mark_probabilities=p.get('mark_probabilities',{}))
        slots.append(s)
    rendered=R.render_reading(text,slots).lstrip(LEADING_QUOTES+' ')
    if raw.opening_quotes:rendered='“'+rendered
    rd,removed=R.apply_constraints(replace(raw,text=rendered,slots=slots))
    assert not removed
    guard=edit_guard(text,rendered)
    for s in rd.slots:
        rr=list(s['hold_reasons'])+guard
        rr.extend('K1:'+f.get('rule','observation')+':'+f.get('reason','unknown') for f in s.get('constraint_flags',()))
        s.update(hold=bool(rr),hold_reasons=list(dict.fromkeys(rr)),label_status='HOLD' if rr else s['label_status'])
    return rd


def compose(text,raw,predictions,coverage,mode,k1_flags=(),**kwargs):
    serial=serialize(compose_reading(text,raw,predictions,coverage,mode,k1_flags,**kwargs))
    serial.update(mode=mode.upper(),release_policy=POLICY,
        hold_slots=[dict(start=s['start'],base=s['base'],reasons=s['hold_reasons'],parts=s['parts'],
                         detector_parts=s['detector_parts'],r1_parts=s['r1_parts'],locator_span=s.get('locator_span'))
                    for s in serial['slots'] if s['hold']])
    return serial


def compose_runtime(runtime, mode, k1_flags=()):
    """Saved evidence adapter. All readers use the same receipt-bound windows.

    A peer's coverage is explicit; callers must bind it to that extraction.
    Missing peer predictions/coverage always abstain.
    """
    peer=mode[-1].upper() if mode.upper().startswith('ENSEMBLE_') else None
    return compose(runtime.get('recogniser_nfd',runtime['recogniser_text']),runtime['detector'],
        prediction_index(runtime['r1_predictions']),runtime['coverage'],mode,k1_flags,
        peer_predictions=prediction_index(runtime.get('peer_predictions',{}).get(peer,[])),
        peer_coverage=runtime.get('peer_coverage',{}).get(peer))
