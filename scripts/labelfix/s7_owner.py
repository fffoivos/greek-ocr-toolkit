"""S7 replay of CN1's unchanged strict predicates and complete-note HOLD gate.

The evaluation body is retained from cn1_measure; physical lines may change.
"""
from copy import deepcopy
from collections import Counter
from scripts.labelfix.cn1_measure import (S6, R1, O, example_specs, read, relevant_holds,
    clause_status, facets, predicate, rollup, CATEGORIES)


def evaluate(systems, frozen):
    parsed=R1.evaluate(systems['S6'],frozen['S4'],O)
    groups={}
    lookup=example_specs();lookup['8b6b0de9-p000021-l0012']=[('no_top',1,None)]
    for label,file,sp in [('review_v16','owner_notes_review_v16_20261016.jsonl',S6.current_review_specs()),('examples_v10','owner_notes_examples_v10_20261016.jsonl',lookup)]:
        groups[label]=[]
        for n in read(O/file):
            specs=sp.get(n['line_id']) if n['note'] else [('no_regression',None,None)]
            groups[label].append(dict(n,note_set=file,historical=False,specs=[dict(kind=k,slots=s if isinstance(s,list) else [s] if s is not None else [],value=v) for k,s,v in specs or [('uncertain',None,None)]]))
    for label,key in [('old33','review_notes_33'),('old56','example_notes_56')]:
        groups[label]=[dict(n,historical=True,specs=n['expectations']) for n in parsed[key]]
    groups['old59']=[dict(n,historical=True,specs=[]) for n in parsed['slot_expectations_59']]
    records=[]
    for group,notes in groups.items():
        for idx,n in enumerate(notes,1):
            lid=n['line_id'];base=frozen['S4'][lid]
            row=dict(type='note',note_set=group,source=n['note_set'],note_index=idx,line_id=lid,note=n['note'],systems={})
            for name,by in systems.items():
                line=by[lid]; cs=[]
                if group=='old59':
                    # Same exact count and Counter equality as r1_owner.evaluate,
                    # with S6 punctuation routed to the detector it actually has.
                    s=next((s for s in line['slots'] if s['slot']==n['mapped_slot']),None)
                    ex=n['expected'];ns=[n['mapped_slot']] if n['mapped_slot'] else []
                    kind='mark';value=ex.get('missed');ok=False;why=None
                    if ex.get('apostrophe'):kind='apostrophe';value=None
                    elif ex.get('false')=='punctuation_dot':kind='punctuation_dot';value=None
                    elif ex.get('false'):kind='no_subscript' if 'subscript' in ex['false'] else 'no_top';value=None
                    elif n.get('mark_kind')=='subscript':kind='subscript';value=None
                    if n.get('ambiguous') or s is None:why='ambiguous owner wording or unmapped v8 slot'
                    elif kind=='apostrophe':ok,why=S6.clause(line,base,kind,ns,None)
                    elif kind=='punctuation_dot':ok=not s['evidence'].get('below')
                    elif ex.get('false'):
                        ok=not any(k=='subscript' for k,v in s['detected']) if 'subscript' in ex['false'] else not any(k in ('accent','breathing','compound') for k,v in s['detected'])
                    elif kind=='subscript':ok=any(k=='subscript' for k,v in s['detected'])
                    else:
                        ok=R1.units(s['detected'])==ex.get('missed',0) and (s['truth'] is None or Counter(map(tuple,s['truth']))==Counter(map(tuple,s['detected'])))
                        if n.get('group_missed_total'):
                            ok=ok and sum(R1.units(q['detected']) for q in line['slots'] if q['slot'] in n['mapped_group_slots'])==n['group_missed_total']
                    spec=dict(kind=kind,slots=ns,value=value)
                    hs=relevant_holds(line,kind,ns)
                    if n.get('group_missed_total'):
                        hs=sorted(set(hs+relevant_holds(line,kind,n['mapped_group_slots'])))
                    state,unheld=clause_status(line,base,spec,True,ok,hs)
                    physical_line=systems['S6' if name=='S6' else 'SF1_detector_control'][lid]
                    cs.append(dict(spec,raw_fixed=bool(ok),status=state,hold_starts=hs,unheld_check=unheld,evidence=dict(detail=why,detected=s['detected'] if s else None,truth=s['truth'] if s else None,prior=n),facets=facets(line,base,spec,True,ok,hs,state,physical_line)))
                else:
                    for spec in n['specs']:
                        spec={k:v for k,v in spec.items() if k in ('kind','slots','value','ambiguous')}
                        ok,ev=predicate(line,base,spec,n['historical'])
                        hs=relevant_holds(line,spec['kind'],spec['slots'])
                        state,unheld=clause_status(line,base,spec,n['historical'],ok,hs)
                        physical_line=systems['S6' if name=='S6' else 'SF1_detector_control'][lid]
                        cs.append(dict(spec,raw_fixed=bool(ok),status=state,hold_starts=hs,unheld_check=unheld,evidence=ev,facets=facets(line,base,spec,n['historical'],ok,hs,state,physical_line)))
                state='fail' if any(c['status']=='fail' for c in cs) else 'HOLD' if any(c['status']=='HOLD' for c in cs) else 'fixed'
                row['systems'][name]=dict(reading=line['reading'],raw_fixed=all(c['raw_fixed'] for c in cs),status=state,clauses=cs)
            records.append(row)
    summaries={}
    for label in groups:
        rs=[r for r in records if r['note_set']==label];summaries[label]={}
        for name in systems:
            cc=[c for r in rs for c in r['systems'][name]['clauses']]
            summaries[label][name]=dict(**rollup(r['systems'][name]['status'] for r in rs),raw_strict_fixed=sum(r['systems'][name]['raw_fixed'] for r in rs),clauses=rollup(c['status'] for c in cc),facets={cat:rollup(c['facets'][cat]['status'] for c in cc if cat in c['facets']) for cat in CATEGORIES})
    assert summaries['review_v16']['S6']['fixed']==35
    assert summaries['examples_v10']['S6']['fixed']==33
    return records, summaries
