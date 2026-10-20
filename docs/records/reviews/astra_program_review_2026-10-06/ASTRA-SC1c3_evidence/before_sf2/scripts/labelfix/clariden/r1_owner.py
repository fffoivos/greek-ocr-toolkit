"""Explicit owner-note checks over frozen slot identities; no new print labels."""
from copy import deepcopy
from collections import Counter
from scripts.labelfix.clariden.r1_common import rows, clusters, nfd
from greekocr.labelfix.owner_slots import overlap_slots

# Added/updated clauses in the complete 56-note file, relative to S4's 33-note snapshot.
EXTRA={
'02a3a2a6-p000041-l0005':[('ambiguous',None,'unified lambda-omicron: no slot range given'),('mark',24,1),('subscript',28,None)],
'02a3a2a6-p000046-l0014':[('apostrophe',8,None)],
'02a3a2a6-p000307-l0003':[('apostrophe',2,None),('apostrophe',15,None)],
'02a3a2a6-p000318-l0017':[('mark',2,1)],
'177b717d-p000017-l0012':[('mark',11,1),('mark',12,1)],
'177b717d-p000097-l0010':[('mark',2,1),('mark',5,1)],
'2793d64c-p000033-l0022':[('mark',1,1),('apostrophe',11,None)],
'384c3f89-p000050-l0016':[('mark',5,2),('mark',19,1)],
'384c3f89-p000068-l0036':[('apostrophe',6,None),('mark',7,2),('mark',30,1)],
'384c3f89-p000091-l0027':[('mark',1,2),('union_base',[1,2],'η')],
'384c3f89-p000142-l0010':[('subscript',14,None)],
'384c3f89-p000170-l0024':[('subscript',12,None)],
'384c3f89-p000182-l0023':[('apostrophe',3,None)],
'384c3f89-p000183-l0009':[('mark',9,2)],
'384c3f89-p000183-l0022':[('apostrophe',20,None)],
'51fe7386-p000024-l0015':[('quote',1,None),('mark',2,1),('mark',29,1)],
'602cc72e-p000113-l0009':[('mark',s,1) for s in [1,9,10,12]],
'602cc72e-p000167-l0027':[('mark',s,1) for s in [6,10,14]],
'8b6b0de9-p000007-l0011':[('mark',s,1) for s in [1,2,4]],
'8b6b0de9-p000007-l0021':[('mark',4,1),('mark',18,1)],
'8b6b0de9-p000008-l0001':[('mark',7,1),('mark',12,1)],
'8b6b0de9-p000016-l0013':[('mark',3,1),('mark',5,1)],
'9c1dca9b-p000005-l0017':[('mark',s,1) for s in [9,14,23,27]],
'9c1dca9b-p000015-l0065':[('mark',8,1)],
}


def units(ms):return sum(2 if k in ('compound','dialytika') else 1 for k,v in ms)
def as_set(ms):return set(map(tuple,ms))


def clause(e,line,baseline):
    e=deepcopy(e);kind=e['kind'];slots=e.get('slots',[]);value=e.get('value')
    chosen=[s for s in line['slots'] if s['slot'] in slots]
    fixed=False;unresolved=None
    if slots and (not chosen or {s['slot'] for s in chosen}!=set(slots)):
        unresolved='missing target slot'
    elif e.get('ambiguous') or kind=='ambiguous':unresolved='ambiguous owner wording or slot identity'
    elif kind in ('apostrophe','quote','leading_sign'):
        unresolved='punctuation is outside the four reader heads; retained for detector follow-up'
    elif kind in ('mark','subscript') and len(chosen)==1:
        s=chosen[0];truth=s['truth'];ms=s['detected']
        conflict=(truth is not None and (not any(k=='subscript' for k,v in truth) if kind=='subscript' else units(truth)<value))
        e['truth_conflict']=conflict
        fixed=not conflict and s.get('reader_scored',False) and (any(k=='subscript' for k,v in ms) if kind=='subscript' else units(ms)==value and (truth is None or Counter(map(tuple,truth))==Counter(map(tuple,ms))))
        if not s.get('reader_scored'):unresolved='slot unscored or not a reader target'
    elif kind in ('no_top','no_subscript') and chosen:
        rs=[r for r in line['recogniser_slots'] if r.get('component_slot') in slots]
        fixed=bool(rs) and all(r.get('reader_scored',False) for r in rs) and not any(p=='subscript' if kind=='no_subscript' else p!='subscript' for r in rs for p in r.get('parts',[]))
    elif kind=='named' and len(chosen)==1:fixed=chosen[0].get('reader_scored',False)
    elif kind in ('no_regression','whole_marks'):
        known=[s for s in line['slots'] if s['truth'] is not None]
        if kind=='whole_marks':fixed=all(as_set(s['truth'])==as_set(s['detected']) for s in known)
        else:
            old={s['slot']:s for s in baseline['slots']}
            fixed=all(not ((as_set(s['truth'])&as_set(old[s['slot']]['detected']))-(as_set(s['truth'])&as_set(s['detected']))) and not ((as_set(s['detected'])-as_set(s['truth']))-(as_set(old[s['slot']]['detected'])-as_set(s['truth']))) for s in known)
            current={s['slot']:s for s in line['slots']}
            fixed=fixed and all(slot in current and Counter(map(tuple,s['detected']))==Counter(map(tuple,current[slot]['detected'])) for slot,s in old.items() if s['truth'] is None)
            oldnames={r['start']:Counter(r.get('parts',[])) for r in baseline['recogniser_slots']}
            newnames={r['start']:Counter(r.get('parts',[])) for r in line['recogniser_slots']}
            fixed=fixed and oldnames==newnames
    elif kind in ('base','union_base'):
        boxes=[s['bbox'] for s in chosen]
        rs=[r for r in line['recogniser_slots'] if any(min(r['locator_span'][1],b[2])>max(r['locator_span'][0],b[0]) for b in boxes)]
        if kind=='base':fixed=bool(rs) and all(r['base'].lower()==value for r in rs)
        else:fixed=len(rs)==1 and rs[0]['base'].lower()==value and len(boxes)==len(slots)
        e['source']='recogniser letters and cached spans; independent of mark heads'
    elif kind in ('word_slots','word_accent'):
        from greekocr.labelfix.text import tokenize
        wanted=value
        ts=[t for t in tokenize(nfd(line['recogniser_text'])) if wanted in ''.join(c.base for c in clusters(t.core))]
        rs=[r for t in ts for r in line['recogniser_slots'] if t.core_start<=r['start']<t.core_end]
        fixed=bool(rs)
        if kind=='word_accent':fixed=fixed and any(r['base']==wanted and any(p in r.get('parts',[]) for p in ('acute','grave','circumflex')) and r.get('reader_scored') for r in rs)
        e['source']='recogniser character segmentation; marks require a scored reader slot'
    else:unresolved='unmapped clause or slot'
    if not fixed and unresolved is None:unresolved='clause not satisfied'
    e.update(fixed=bool(fixed and unresolved is None and line.get('prediction_line_present',False)),unresolved=unresolved)
    return e


def category(kind):
    if kind in ('fusion','base','union_base','split_union','word_slots'):return 'segmentation'
    if kind in ('safe_zone','printed_top_presence','mark','subscript','no_top','no_subscript'):return 'physical'
    if kind=='no_regression':return 'complete_note'
    return 'naming'


def evaluate(by,baseline,root):
    old=[]
    for prior in rows(root/'owner_slot_expectations.jsonl'):
        e=deepcopy(prior);line=by.get(e['line_id'])
        if line is None:
            old.append(dict(e,fixed=False,unresolved='missing target line'));continue
        ss=line['slots'];slot,hits=overlap_slots(e['v8_x0'],e['v8_x1'],ss)
        s=next((s for s in ss if s['slot']==slot),None);ex=e['expected'];fixed=False;why=None
        if e.get('ambiguous'):why='ambiguous owner wording'
        elif s is None:why='unmapped v8 slot'
        elif ex.get('apostrophe') or ex.get('false')=='punctuation_dot':why='punctuation outside reader heads'
        elif not s.get('reader_scored'):why='slot unscored or outside vowel/rho targets'
        elif ex.get('false'):
            fixed=not any(k=='subscript' for k,v in s['detected']) if 'subscript' in ex['false'] else not any(k in ('accent','breathing','compound') for k,v in s['detected'])
        elif e.get('mark_kind')=='subscript':fixed=any(k=='subscript' for k,v in s['detected'])
        else:
            fixed=units(s['detected'])==ex.get('missed',0) and (s['truth'] is None or Counter(map(tuple,s['truth']))==Counter(map(tuple,s['detected'])))
            if e.get('group_missed_total'):fixed=fixed and sum(units(q['detected']) for q in ss if q['slot'] in e['mapped_group_slots'])==e['group_missed_total']
        e.update(note_set='owner_slot_expectations.jsonl',mapped_slot=slot,overlapping_slots=hits,fixed=bool(fixed),unresolved=why,
                 after=s['detected'] if s else None);old.append(e)
    frozen={n['line_id']:n for n in rows(root/'owner_examples_expectations.jsonl')}
    review=[]
    for prior in rows(root/'S5_review_expectations.jsonl'):
        specs=[]
        if not prior['note']:specs=[dict(kind='no_regression',slots=[])]
        for check in prior.get('checks',[]):
            ex=check['expected'];kind='mark';value=ex.get('missed',1)
            if ex.get('false'):kind='no_subscript' if 'subscript' in ex['false'] else 'no_top'
            elif ex.get('subscript'):kind='subscript';value=None
            elif ex.get('apostrophe'):kind='apostrophe';value=None
            specs.append(dict(kind=kind,slots=[check['slot']],value=value,ambiguous=check.get('ambiguous',False)))
        l=by.get(prior['line_id']);es=[clause(e,l,baseline[l['line_id']]) if l and l['line_id'] in baseline else dict(e,fixed=False,unresolved='missing target line') for e in specs]
        review.append(dict(prior,note_set='owner_notes_db_20261016.jsonl',expectations=es,fixed=bool(es) and all(e['fixed'] for e in es)))
    examples=[]
    for note in rows(root/'owner_notes_examples_20261016.jsonl'):
        lid=note['line_id'];prior=frozen.get(lid)
        if lid in EXTRA:
            specs=[dict(kind=k,slots=s if isinstance(s,list) else [s] if s is not None else [],value=v) for k,s,v in EXTRA[lid]]
        elif prior:specs=prior['expectations']
        else:raise ValueError('owner note has no explicit transcription '+lid)
        es=[clause(e,by[lid],baseline[lid]) if lid in by and lid in baseline else dict(e,fixed=False,unresolved='missing target line') for e in specs]
        examples.append(dict(note,note_set='owner_notes_examples_20261016.jsonl',expectations=es,fixed=all(e['fixed'] for e in es)))
    assert len(old)==59 and len(review)==33 and len(examples)==56
    from scripts.labelfix.s6_notes import current_review_specs
    from scripts.labelfix.s5_notes import specs as example_specs
    spec=example_specs();spec['8b6b0de9-p000021-l0012']=[('no_top',1,None)]
    current={}
    for label,file,lookup in [('review_v16_49','owner_notes_review_v16_20261016.jsonl',current_review_specs()),
                              ('examples_v10_57','owner_notes_examples_v10_20261016.jsonl',spec)]:
        checks=[]
        for note in rows(root/file):
            lid=note['line_id'];ls=by.get(lid);base=baseline.get(lid)
            parsed=lookup.get(lid) if note['note'] else [('no_regression',None,None)]
            es=[]
            for k,target,value in parsed or [('ambiguous',None,None)]:
                e=dict(kind=k,slots=target if isinstance(target,list) else [target] if target is not None else [],value=value)
                es.append(clause(e,ls,base) if ls and base else dict(e,fixed=False,unresolved='missing target line'))
            checks.append(dict(note,note_set=file,expectations=es,fixed=all(e['fixed'] for e in es)))
        current[label]=checks
    groups=dict(slot_expectations_59=old,review_notes_33=review,example_notes_56=examples,**current)
    labels=dict(old_59=old,review_33=review,examples_56=examples,**current)
    groups['counts']={name:dict(fixed=sum(r['fixed'] for r in rs),n=len(rs),
        missing_prediction_lines=sum(not by.get(r['line_id'],{}).get('prediction_line_present',False) for r in rs),
        note_set=(rs[0].get('note_set') if rs else 'owner_slot_expectations.jsonl'),
        dimensions={cat:dict(fixed=sum(e['fixed'] for r in rs for e in r.get('expectations',[dict(kind='mark',fixed=r['fixed'])]) if category(e['kind'])==cat),
            n=sum(category(e['kind'])==cat for r in rs for e in r.get('expectations',[dict(kind='mark',fixed=r['fixed'])]))) for cat in ('physical','naming','segmentation','complete_note')}) for name,rs in labels.items()}
    return groups
