"""Shared SF2/L1E policy: observation, agreement, K1, and bounded edits.

PRESENCE compares mark families; FULL compares exact mark sets. Neither is
independent print truth. Missing observation always abstains. Punctuation uses
detector opening quotes (canonical “) and word-final elisions (canonical ’).
Other punctuation and spaces must match, allowing explicit codepoint aliases.
Base letters and unsupported printed marks remain guarded.
ENSEMBLE_AB/AE compare A with B/E exactly and do not veto on detector names.
"""
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, fields, replace
import hashlib
import json
import unicodedata as ud
from . import reading as R
from .text import clusters, nfd, nfc, GREEK_LETTERS, ELISION, is_letter, word_final_elision

POLICY = 'sf4-release-v1'
MODES = ('PRESENCE', 'FULL', 'ENSEMBLE_AB', 'ENSEMBLE_AE')
ENSEMBLE_CAVEAT = "A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label experiment."
R1_LETTERS = frozenset('αεηιουωρΑΕΗΙΟΥΩΡ')
LEADING_QUOTES = '“”«»„"'


def policy_binding():
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    paths = [Path(__file__), Path(R.__file__),Path(__file__).with_name('text.py'),
             Path(__file__).with_name('segmentation.py'),
             root/'scripts/labelfix/clariden/l1_common.py',root/'scripts/labelfix/clariden/l1r_recompose.py',
             root/'scripts/labelfix/owner_reading.py',root/'scripts/labelfix/owner_pages_build_combined.py']
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
    if rd.evidence_sha256:record['evidence_sha256']=rd.evidence_sha256
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


_word_final_elision = word_final_elision


def _render_reading(text, slots):
    """Release composer: reader marks, detector final elisions, other quotes kept."""
    by={s['start']:s for s in slots};out=[];cs=clusters(nfd(text))
    for i,c in enumerate(cs):
        if _word_final_elision(cs,i):continue
        s=by.get(c.start)
        if s is None:out.append(c.base)
        else:
            out.append(c.base+''.join(R.MARKS[p] for p in s.get('parts',()) if p in R.MARKS))
            if s.get('apostrophe'):out.append('’')
    return nfc(''.join(out))


def _punctuation(text):
    """Remove only leading quote aliases and elisions after Greek word ends."""
    cs=clusters(nfd(text).lstrip(LEADING_QUOTES+' '))
    out=[]
    for i,c in enumerate(cs):
        if _word_final_elision(cs,i):continue
        if not c.base.isalpha() or c.base in ELISION:
            # Representation only: never drop a quote, space or attached mark.
            base = ('"' if c.base in LEADING_QUOTES else "'" if c.base in ELISION+'‘'
                    else ' ' if c.base in '\u00a0\u202f' else c.base)
            out.append(base+c.marks)
    return ''.join(out)


def edit_guard(original, proposal):
    """Return rejection reasons; unchanged unsupported characters are preserved.

    Greek bases and legal mark multiplicities are the only editable letters.
    Non-Greek clusters and unsupported Greek clusters must remain identical.
    Canonical equivalence alone is never a reason to rewrite source bytes.
    """
    a=[c for c in clusters(nfd(original)) if (c.base.isalpha() and c.base not in ELISION) or ud.combining(c.base)]
    b=[c for c in clusters(nfd(proposal)) if (c.base.isalpha() and c.base not in ELISION) or ud.combining(c.base)]
    reasons=[]
    # Preserve the raw spelling of out-of-domain clusters, including decomposed
    # Latin accents. NFC equivalence does not authorize rewriting those bytes.
    raw_a=[c for c in clusters(original) if c.base.isalpha() and c.base not in ELISION]
    raw_b=[c for c in clusters(proposal) if c.base.isalpha() and c.base not in ELISION]
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


def zone_relevance(slot, signal_parts=()):
    """Conservative saved-evidence contract; no capital side-zone exception.

    Scalar meanline/xh do not certify the whole overhead AND preposed zone.
    Saved SF3 records lack that certificate, so top cuts remain decisive for
    mark bearers. Either recogniser case or physical capital case/band vetoes
    both clipping relaxations, including on otherwise unsupported capitals.
    """
    base=slot['base'].lower()
    ev=slot.get('evidence',{})
    ev=ev.to_record() if hasattr(ev,'to_record') else ev
    capital=(slot['base'].isupper() or slot.get('case_class')=='capital'
             or ev.get('case_class')=='capital'
             or any(record.get(key)=='capital' for record in (slot,ev)
                    for key in ('pixel_class','raw_pixel_class','frozen_pixel_class'))
             or slot.get('geometry_capital') is True or slot.get('all_caps') is True
             or str(ev.get('band_source','')).startswith('capital')
             or str(slot.get('height_band',{}).get('source','')).startswith('capital'))
    bearing=base in 'αεηιουωρ'
    return dict(above=bearing or capital,top_cut=bearing or capital,upper_zone_top=None,
        below=capital or not slot['base'].islower() or base in 'αηω'
              or bool(slot.get('iota_adscript')) or 'subscript' in signal_parts,
        left=bearing and capital,right=slot.get('word_final',False) or slot.get('apostrophe',False))


def _flag_relevant(flag, relevance):
    """Only known observation predicates can lose a veto; unknown flags hold."""
    if flag.get('rule','observation')!='observation':return True
    reason=flag.get('reason','')
    key={'clipped_top':'top_cut','detector_clipped_top':'top_cut',
         'clipped_bottom':'below','detector_clipped_bottom':'below',
         'unseen_above':'above','crop_UNSEEN:above':'above',
         'unseen_below':'below','crop_UNSEEN:below':'below'}.get(reason)
    return relevance[key] if key else True


def _flag_targets(flag, start):
    return (flag.get('start')==start or any(a.get('start')==start for a in flag.get('alternatives',()))
            or ('start' not in flag and not flag.get('alternatives')))


def decide(slot, prediction, coverage, mode, *, flagged=False, peer_prediction=None, peer_coverage=None, signal_parts=()):
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
    peer_parts=[] if peer_prediction is None else peer_prediction.get('parts',peer_prediction.get('cls','none').split('+'))
    relevant=zone_relevance(slot,[*det,*(rp or []),*peer_parts,*signal_parts])
    reasons.extend('crop_UNSEEN:'+z for z in slot.get('unseen_zones',()) if relevant.get(z,True))
    for zone,direction in [('above','top'),('below','bottom'),('left','left'),('right','right')]:
        if relevant['top_cut' if direction=='top' else zone] and ev.get('clipped_'+direction):reasons.append('detector_clipped_'+direction)
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
    active_flags=[f for f in slot.get('constraint_flags',()) if _flag_relevant(f,relevant)]
    if flagged or active_flags:reasons.append('K1:flag')
    if slot.get('hold'):
        old=slot.get('hold_reasons')
        # A saved K1-only HOLD must not resurrect a now-irrelevant flag.
        if old:
            for reason in old:
                predicate=reason.removeprefix('K1:observation:')
                if reason.startswith(('detector_clipped_','crop_UNSEEN:','K1:observation:')):
                    if not _flag_relevant(dict(reason=predicate),relevant):continue
                if (reason=='K1:flag' and slot.get('constraint_flags') and not active_flags and not flagged):continue
                reasons.append(reason)
        elif not slot.get('constraint_flags') or active_flags:reasons.append('detector_hold')
    reasons=list(dict.fromkeys(reasons))
    return dict(action='HOLD' if reasons else 'ACCEPT' if slot['base'] in R1_LETTERS else 'KEEP',
                reasons=reasons,detector_parts=det,r1_parts=rp)


def _compose_reading(text, raw, predictions, coverage, mode, k1_flags=(), *, peer_predictions=None, peer_coverage=None, signal_parts=None):
    """Compose from detector punctuation and R1 names, retaining all HOLD evidence."""
    if isinstance(raw,dict):raw=deserialize(raw)
    # Old saved U+02BC slots are punctuation, not evidence for another letter.
    # Preserve their complete records and carry unresolved evidence as a veto.
    aliases=[s for s in raw.slots if s['base'] in ELISION]
    if aliases:
        flags=list(raw.constraint_flags)
        if any(any(s.get(key) for key in ('parts','unnamed','hold','constraint_flags','localisation_unknown',
                    'segmentation_uncertain','ambiguity','unseen_zones')) or s.get('physical_resolved') is False
               for s in aliases):
            flags.append(dict(rule='observation',reason='legacy_elision_slot_unresolved'))
        raw=replace(raw,slots=[s for s in raw.slots if s['base'] not in ELISION],
                    constraint_flags=flags,geometry=dict(raw.geometry,elision_alias_slots=[s for s in serialize(raw)['slots'] if s['base'] in ELISION]))
    cov={c['start']:c for c in coverage}
    if len(cov)!=len(coverage):raise ValueError('duplicate R1 coverage start')
    pcov={c['start']:c for c in (peer_coverage or [])}
    if len(pcov)!=len(peer_coverage or []):raise ValueError('duplicate peer coverage start')
    slots=[]
    cs=clusters(nfd(text))
    source_parts={c.start:[p for p,v in R.MARKS.items() if v in c.marks] for c in cs}
    # A written iota immediately after Α/Η/Ω can be an adscript. Without a
    # separate adscript adjudication, keep the below zone conservative there.
    adscript={c.start for i,c in enumerate(cs) if i and c.base in 'ιΙ' and cs[i-1].base in 'ΑΗΩ'}
    relevance={}
    for s in raw.slots:
        parts=list(s.get('parts',()))+source_parts.get(s['start'],[])+list((signal_parts or {}).get(s['start'],()))
        for p in (predictions.get(s['start']), (peer_predictions or {}).get(s['start'])):
            if p:parts.extend(p.get('parts',p.get('cls','none').split('+')))
        relevance[s['start']]=zone_relevance(dict(s,iota_adscript=True) if s['start'] in adscript else s,parts)
    flags=[]
    for f in [*raw.constraint_flags,*k1_flags]:
        targets=[s for s in raw.slots if _flag_targets(f,s['start'])]
        active=[s for s in targets if _flag_relevant(f,relevance[s['start']])]
        if len(active)==len(targets):flags.append(f)
        else:flags.extend(dict(f,start=s['start'],alternatives=[]) for s in active)
    raw=replace(raw,constraint_flags=flags)
    for original in raw.slots:
        s=deepcopy({k:v for k,v in original.items() if k not in ('component','evidence','naming')})
        s.update(component=original.get('component'),evidence=original.get('evidence',{}),naming=original.get('naming',{}))
        start=s['start'];p=predictions.get(start)
        if start in adscript:s['iota_adscript']=True
        if p is not None:
            if 'parts' not in p and 'cls' not in p:
                p=dict(p,evidence_state='UNKNOWN',uncertainty=['invalid_prediction'])
            p=dict(p,parts=p.get('parts',[x for x in p.get('cls','none').split('+') if x!='none']))
        flagged=any(_flag_targets(f,start) for f in flags)
        peer=(peer_predictions or {}).get(start)
        signals=[*source_parts.get(start,()),*(signal_parts or {}).get(start,())]
        d=decide(s,p,cov.get(start),mode,flagged=flagged,peer_prediction=peer,peer_coverage=pcov.get(start),signal_parts=signals)
        s['constraint_flags']=[f for f in s.get('constraint_flags',()) if _flag_relevant(f,relevance[start])]
        mapping=raw.geometry.get('physical_mapping',{})
        if mapping.get('ambiguous'):
            d['reasons'].append('detector_physical_mapping_ambiguous')
        for variant in raw.geometry.get('substitutions',()):
            if variant not in R.QUALIFIED_GEOMETRY:
                d['reasons'].append('detector_geometry_unqualified:'+variant)
        if d['reasons']:d['action']='HOLD'
        s.update(detector_parts=d['detector_parts'],r1_parts=d['r1_parts'],
                 r1_coverage=deepcopy(cov.get(start)),hold_reasons=d['reasons'],hold=bool(d['reasons']),label_status=d['action'])
        s['zone_relevance']=relevance[start]
        if mode.upper().startswith('ENSEMBLE_'):
            s.update(peer_arm=mode[-1].upper(),peer_prediction=deepcopy(peer),peer_coverage=deepcopy(pcov.get(start)))
        if p is not None and s['base'] in R1_LETTERS:
            s.update(parts=p['parts'],naming={},mark_support_source='reader',reader_evidence={},mark_probabilities=p.get('mark_probabilities',{}))
        slots.append(s)
    rendered=_render_reading(text,slots).lstrip(LEADING_QUOTES+' ')
    if raw.opening_quotes:rendered='“'+rendered
    rd,removed=R.apply_constraints(replace(raw,text=rendered,slots=slots))
    assert not removed
    guard=edit_guard(text,rendered)
    for s in rd.slots:
        rr=list(s['hold_reasons'])+guard
        rr.extend('K1:'+f.get('rule','observation')+':'+f.get('reason','unknown') for f in s.get('constraint_flags',()))
        s.update(hold=bool(rr),hold_reasons=list(dict.fromkeys(rr)),label_status='HOLD' if rr else s['label_status'])
    return rd


def bind_runtime(runtime, k1_flags=()):
    """One content-bound envelope for every input used by the release policy.

    Keep all saved peers, including diagnostic E in AB. The binding covers
    detector geometry, recogniser context, coverage, predictions and K1 flags.
    It proves input identity; source-file/checkpoint custody remains the caller's.
    """
    evidence={k:deepcopy(runtime.get(k,default)) for k,default in (
        ('recogniser_text',''),('detector',{}),('r1_predictions',[]),('coverage',[]),
        ('peer_predictions',{}),('peer_coverage',{}),('k1_flags',[]))}
    if 'recogniser_nfd' in runtime:
        if nfd(runtime['recogniser_text'])!=nfd(runtime['recogniser_nfd']):raise ValueError('runtime recogniser text mismatch')
        evidence['recogniser_nfd']=runtime['recogniser_nfd']
    if not isinstance(evidence['detector'],dict):evidence['detector']=serialize(evidence['detector'])
    digest=hashlib.sha256(json.dumps(evidence,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    if runtime.get('evidence_sha256',digest)!=digest:raise ValueError('runtime evidence binding mismatch')
    if k1_flags:
        evidence['k1_flags'].extend(deepcopy(k1_flags))
        digest=hashlib.sha256(json.dumps(evidence,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return dict(evidence,evidence_sha256=digest)


def compose_runtime(runtime, mode, k1_flags=()):
    """Compose the complete saved evidence envelope, without selecting inputs."""
    runtime=bind_runtime(runtime,k1_flags)
    peer=mode[-1].upper() if mode.upper().startswith('ENSEMBLE_') else None
    signals={}
    for records in runtime['peer_predictions'].values():
        prediction_index(records)  # Diagnostic peers must not hide duplicate starts.
        for p in records:signals.setdefault(p['start'],[]).extend(p.get('parts',p.get('cls','none').split('+')))
    rd=_compose_reading(runtime.get('recogniser_nfd',runtime['recogniser_text']),runtime['detector'],
        prediction_index(runtime['r1_predictions']),runtime['coverage'],mode,runtime['k1_flags'],
        peer_predictions=prediction_index(runtime['peer_predictions'].get(peer,[])),
        peer_coverage=runtime['peer_coverage'].get(peer),signal_parts=signals)
    serial=serialize(rd)
    serial.update(mode=mode.upper(),release_policy=POLICY,evidence_sha256=runtime['evidence_sha256'],
        hold_slots=[dict(start=s['start'],base=s['base'],reasons=s['hold_reasons'],parts=s['parts'],
                         detector_parts=s['detector_parts'],r1_parts=s['r1_parts'],locator_span=s.get('locator_span'))
                    for s in serial['slots'] if s['hold']])
    return serial


def compose(text,raw,predictions,coverage,mode,k1_flags=(),*,peer_predictions=None,peer_coverage=None,signal_parts=None):
    """Legacy component adapter; bind all supplied evidence before composition.

    Runtime-aware callers must use compose_runtime to retain diagnostic peers.
    """
    peer=mode[-1].upper() if mode.upper().startswith('ENSEMBLE_') else None
    def records(index):return [dict(p,start=start) for start,p in (index or {}).items()]
    peers={peer:records(peer_predictions)} if peer else {}
    # Preserve explicit legacy relevance inputs as another diagnostic signal.
    if signal_parts:peers['diagnostic']=[dict(start=start,parts=list(parts)) for start,parts in signal_parts.items()]
    return compose_runtime(dict(recogniser_text=text,detector=raw,r1_predictions=records(predictions),coverage=coverage,
        peer_predictions=peers,peer_coverage={peer:peer_coverage or []} if peer else {}),mode,k1_flags)


def compose_reading(*args,**kwargs):
    return deserialize(compose(*args,**kwargs))
