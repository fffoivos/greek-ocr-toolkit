"""CN1 offline measurement of the unchanged SF1 combined-page artifacts.

This is a scoring adapter, not a reader change. Run the two hash-bound page
builds first (commands are retained in CN1_REPORT.md), then run this module.
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from scripts.labelfix.s5_validate import read, write
from scripts.labelfix import s6_notes as S6
from scripts.labelfix.s5_notes import specs as example_specs
from scripts.labelfix.clariden import r1_owner as R1
from scripts.labelfix.owner_reading import digest, load_configuration
from scripts.labelfix.s6_validate import detected
from greekocr.labelfix.owner_slots import overlap_slots

O = Path('docs/records/labelfix/spellcheck')
E = O / 'CN1_evidence'
CATEGORIES = ('physical_presence', 'naming', 'segmentation', 'punctuation', 'letter_identity', 'complete_note_guard', 'uncertainty')


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def system_coverage(line):
    """Full systems have S6 output outside R1's four heads; don't erase it.

    reader_scored here means a system output is present, not R1 inference or
    confidence. This adapter is applied symmetrically to S6 and combined.
    """
    line = deepcopy(line)
    line['prediction_line_present'] = True
    for s in line['slots']:
        s['reader_scored'] = True
    for s in line['recogniser_slots']:
        s['system_output_present'] = True
        if 'r1_coverage' in s:
            s['r1_scored'] = bool(s['r1_coverage'] and s['r1_coverage'].get('scored'))
            s['acceptance_eligible'] = s.get('label_status') in ('ACCEPT','KEEP')
            # Historical clause adapter needs system coverage; acceptance uses HOLD.
        s['reader_scored'] = True
    return line


def adapt_page(side, frozen):
    line = deepcopy(frozen)
    record = side['line_reading']
    old = {r['start']:r for r in frozen['recogniser_slots']}
    serial = deepcopy(record['slots'])
    for r in serial:
        b = old[r['start']]
        for field in ('base', 'component_ids', 'bbox'):
            assert r[field] == b[field], (frozen['line_id'], r['start'], field)
        r['component_slots'] = b['component_slots']
        r['component_slot'] = b['component_slot']
    for s in line['slots']:
        children = [r for r in serial if r.get('component_slot') == s['slot']]
        s['detected'] = sorted({tuple(m) for r in children for m in detected(r)})
        ev = deepcopy(s['evidence'])
        for field in ('above', 'below', 'diagnostics', 'apostrophes'):
            ev[field] = list({tuple(b['bbox']):b for r in children for b in r['evidence'].get(field, [])}.values())
        if children:
            ev.update({k:v for k,v in children[0]['evidence'].items() if k not in ('above','below','diagnostics','apostrophes')})
        s.update(evidence=ev, hold=any(r.get('hold') for r in children),
                 unnamed=[v for r in children for v in r.get('unnamed',[])])
    line.update(reading=record['text'], recogniser_slots=serial,
                opening_quotes=record['opening_quotes'], constraint_flags=record['constraint_flags'])
    return system_coverage(line)


def page_from_saved(line):
    boxes=[]
    for r in line['recogniser_slots']:
        for field, kind in [('above','above'),('below','below'),('apostrophes','above')]:
            for b in r['evidence'].get(field,[]):
                boxes.append(dict(kind=kind,bbox=b['bbox'],start=r['start']))
    for b in line.get('opening_quotes',[]):
        boxes.append(dict(kind='quote',bbox=b['bbox']))
    return dict(reading=line['reading'],boxes=boxes,letters=[s['bbox'] for s in line['slots']])


def status(fixed, holds=()):
    return 'HOLD' if holds else 'fixed' if fixed else 'fail'


def rollup(values):
    c=Counter(values)
    return dict(n=sum(c.values()),fixed=c['fixed'],hold=c['HOLD'],fail=c['fail'])


def clause_category(kind, historical=False):
    if kind in ('apostrophe','quote','leading_sign','punctuation_dot'): return 'punctuation'
    if kind in ('fusion','split_union','union_base','word_slots'): return 'segmentation'
    if kind in ('base','letter_mark'): return 'letter_identity'
    if kind=='no_regression': return 'complete_note_guard'
    if kind in ('ambiguous','uncertain'): return 'uncertainty'
    if kind=='named' or historical and kind in ('mark','whole_marks'): return 'naming'
    return 'physical_presence'


def relevant_holds(line, kind, ns):
    # Letter layout, punctuation and raw pixel-zone audits do not consume R1
    # names. Mark assertions and line-wide name preservation must abstain when
    # their addressed output is held. Unrelated holds never change a note.
    if kind in ('apostrophe','quote','leading_sign','punctuation_dot','fusion','split_union','union_base','base','word_slots','safe_zone','printed_top_presence','uncertain','ambiguous'):
        return []
    rs = S6.targets(line, ns) if ns else line['recogniser_slots']
    return [r['start'] for r in rs if r.get('hold')]


def predicate(line, baseline, spec, historical):
    kind=spec['kind']; ns=spec['slots']; value=spec.get('value')
    if not historical or kind in ('apostrophe','quote','leading_sign'):
        return S6.clause(line,baseline,kind,ns or None,value)
    out=R1.clause(spec,line,baseline)
    return out['fixed'],out


def clause_status(line, baseline, spec, historical, fixed, holds):
    if not holds:
        return status(fixed), None
    if spec['kind'] not in ('no_regression','whole_marks'):
        return 'HOLD', None
    # A held character must not conceal a definite failure at another character.
    a=deepcopy(line); b=deepcopy(baseline); hs=set(holds)
    held_slots={n for r in line['recogniser_slots'] if r['start'] in hs for n in (r.get('component_slots') or [r.get('component_slot')])}
    for obj in (a,b):
        obj['recogniser_slots']=[r for r in obj['recogniser_slots'] if r['start'] not in hs]
        obj['slots']=[r for r in obj['slots'] if r['slot'] not in held_slots]
    ok, ev=predicate(a,b,spec,historical)
    return ('HOLD' if ok else 'fail'), dict(unheld_predicate_fixed=bool(ok),evidence=ev,excluded_frozen_slots=sorted(n for n in held_slots if n is not None))


def facets(line, baseline, spec, historical, raw_fixed, holds, state, physical_line):
    kind=spec['kind'];ns=spec['slots'];value=spec.get('value');out={}
    cat=clause_category(kind,historical)
    out[cat]=dict(raw_fixed=bool(raw_fixed),status=state)
    # Additional facets use existing S6 physical/segmentation predicates. They
    # explain exact-name clauses without replacing their stricter decision.
    if kind in ('mark','subscript','no_top','no_subscript','whole_marks','safe_zone','printed_top_presence','no_subscripts','word_accent'):
        ok, ev=S6.clause(physical_line,baseline,kind,ns or None,value)
        out['physical_presence']=dict(raw_fixed=bool(ok),status=status(ok),evidence=ev)
    if kind in ('split_union','union_base','base','letter_mark'):
        rs=S6.targets(line,ns)
        ok=any(r['base'].lower()==value for r in rs)
        out['letter_identity']=dict(raw_fixed=ok,status=status(ok))
        if kind=='letter_mark':
            ok, ev=S6.clause(line,baseline,'mark',ns,1)
            out['physical_presence']=dict(raw_fixed=ok,status=status(ok),evidence=ev)
    if kind=='no_regression':
        # Explicit naming and physical facets of the mixed empty-note guard.
        named=R1.clause(dict(kind='no_regression',slots=[]),line,baseline)['fixed']
        named_status,named_ev=clause_status(line,baseline,dict(kind='no_regression',slots=[]),True,named,holds)
        out['naming']=dict(raw_fixed=bool(named),status=named_status,evidence=named_ev)
        a=deepcopy(physical_line);b=deepcopy(baseline)
        for obj in (a,b):
            for r in obj['recogniser_slots']:r['parts']=[]
            for r in obj['slots']:r['detected']=[]
        ok,ev=S6.clause(a,b,'no_regression',None,None)
        out['physical_presence']=dict(raw_fixed=bool(ok),status=status(ok),evidence=ev)
    return out


def main():
    import argparse
    global E
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence-dir',type=Path)
    a=ap.parse_args()
    if a.evidence_dir is not None:E=a.evidence_dir
    started=time.monotonic()
    cfg=load_configuration(E/'combined_config.json')
    combined_page=json.loads((_data_input(E/'combined_boxes.json')).read_text())
    control_page=json.loads((_data_input(E/'s6_control_boxes.json')).read_text())
    for page, html in [(combined_page,'combined.html'),(control_page,'s6_control.html')]:
        assert page['page_sha256']==digest(E/html)
    assert combined_page['reading_configuration']==cfg
    frozen={k:{l['line_id']:l for l in read(O/f'{k}_lines.jsonl.gz')} for k in ('S4','S6')}
    ids=list(combined_page['lines'])
    assert set(ids)==set(control_page['lines'])
    systems={'S6':{lid:system_coverage(frozen['S6'][lid]) for lid in ids},
             'combined':{lid:adapt_page(combined_page['lines'][lid],frozen['S6'][lid]) for lid in ids},
             'SF1_detector_control':{lid:adapt_page(control_page['lines'][lid],frozen['S6'][lid]) for lid in ids}}
    dump(E/'saved_s6_boxes.json',dict(lines={lid:page_from_saved(frozen['S6'][lid]) for lid in ids}))
    for name,by in systems.items():
        write(E/f'{name}_scoring_lines.jsonl',list(by.values()))
    # Use the SF1 R1 strict parser for the old instruments; its saved 33-note
    # review transcription is distinct from the subsequently expanded examples.
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
    holds=[];pred={}
    for p in cfg['r1_predictions']:
        receipt=json.loads(Path(p).with_suffix('.receipt.json').read_text())
        assert receipt['prediction_sha256']==digest(p)
        for r in read(Path(p)):
            key=(r['line_id'],r['start']);assert key not in pred;pred[key]=r
    for lid, side in combined_page['lines'].items():
        for r in side['line_reading']['slots']:
            if not r.get('hold'):continue
            p=pred.get((lid,r['start']));rp=[x for x in p['cls'].split('+') if x!='none'] if p else None
            from scripts.labelfix.owner_pages_build_combined import _kinds
            holds.append(dict(type='hold_slot',line_id=lid,start=r['start'],display_slot=r['display_slot'],frozen_slots=next(s['component_slots'] for s in systems['combined'][lid]['recogniser_slots'] if s['start']==r['start']),base=r['base'],detector_parts=r['raw_parts'],combined_parts=r['parts'],kind_disagreement=p is not None and _kinds(rp)!=_kinds(r['raw_parts']),constraint_flagged=bool(r.get('constraint_flags')),constraint_flags=r.get('constraint_flags',[])))
    hold_counts=dict(unique_slots=len(holds),unique_lines=len({r['line_id'] for r in holds}),kind_disagreement=sum(r['kind_disagreement'] for r in holds),constraint_flagged=sum(r['constraint_flagged'] for r in holds),both=sum(r['kind_disagreement'] and r['constraint_flagged'] for r in holds))
    for label in groups:
        subset={r['line_id'] for r in records if r['note_set']==label}
        hold_counts[label]=dict(unique_slots=sum(r['line_id'] in subset for r in holds),targeted_unique_slots=len({(r['line_id'],start) for r in records if r['note_set']==label for c in r['systems']['combined']['clauses'] for start in c['hold_starts']}))
    differences=[]
    for r in records:
        a=r['systems']['S6'];b=r['systems']['combined']
        raw_direction='combined_worse' if a['raw_fixed'] and not b['raw_fixed'] else 'combined_better' if b['raw_fixed'] and not a['raw_fixed'] else None
        direction='combined_worse' if a['status']=='fixed' and b['status']=='fail' else 'combined_better' if b['status']=='fixed' and a['status']=='fail' else 'S6_fixed_combined_HOLD' if a['status']=='fixed' and b['status']=='HOLD' else 'combined_fixed_S6_HOLD' if b['status']=='fixed' and a['status']=='HOLD' else None
        if direction or raw_direction:
            changed=[dict(kind=x['kind'],slots=x['slots'],value=x.get('value'),S6=x['status'],combined=y['status'],S6_raw=x['raw_fixed'],combined_raw=y['raw_fixed'],combined_evidence=y['evidence'],hold_starts=y['hold_starts']) for x,y in zip(a['clauses'],b['clauses']) if x['status']!=y['status'] or x['raw_fixed']!=y['raw_fixed']]
            differences.append(dict(type='note_difference',note_set=r['note_set'],note_index=r['note_index'],line_id=r['line_id'],note=r['note'],direction=direction,raw_direction=raw_direction,clauses=changed,S6_reading=a['reading'],combined_reading=b['reading']))
    dump(E/'summary.json',dict(summary=summaries,holds=hold_counts,difference_counts=dict(Counter(d['direction'] for d in differences)),raw_difference_counts=dict(Counter(d['raw_direction'] for d in differences))))
    write(E/'differences.jsonl',differences)
    write(E/'CN1_checks.jsonl',records+holds+differences)
    sources=[Path(__file__),Path('scripts/labelfix/cn1_offline.py'),Path('scripts/labelfix/s6_notes.py'),Path('scripts/labelfix/s5_notes.py'),Path('scripts/labelfix/clariden/r1_owner.py'),O/'S4_lines.jsonl.gz',O/'S6_lines.jsonl.gz',Path('.cache/labelfix/align_s0.jsonl')]
    sources += [O/n for n in ['owner_notes_review_v16_20261016.jsonl','owner_notes_examples_v10_20261016.jsonl','owner_slot_expectations.jsonl','S5_review_expectations.jsonl','owner_notes_examples_20261016.jsonl','owner_examples_expectations.jsonl','S4_owner_notes_snapshot.jsonl']]
    sources += [Path('scripts/labelfix/cn1_report.py')]
    sources += [Path(m.__file__) for m in list(sys.modules.values()) if getattr(m,'__file__',None) and ('greekocr.labelfix' in getattr(m,'__name__','') or 'scripts.labelfix' in getattr(m,'__name__','')) and str(m.__file__).endswith('.py')]
    sources += [Path(frozen['S6'][lid]['crop']) for lid in ids]
    from greekocr.labelfix.validate import PRED_DIR, TEST_JSONL
    sources += [TEST_JSONL, PRED_DIR/'full_s0_v2_test.jsonl', PRED_DIR/'full_s0_wikisource_human.jsonl', O/'print_truth_s0.json']
    sources += [Path(p) for p in cfg['r1_predictions']]+[Path(p).with_suffix('.receipt.json') for p in cfg['r1_predictions']]+[Path(cfg['r1_checkpoint']['path'])]
    dump(E/'measurement_receipt.json',dict(schema='cn1-measurement-v1',head=cfg['detector_commit'],network=False,ctc_forward_passes=0,r1_inference=0,training=False,owner_lines=len(ids),sources={str(p):digest(p) for p in sources},page_sha256={name:digest(E/name) for name in ['combined.html','s6_control.html','combined_boxes.json','s6_control_boxes.json']},scoring_seconds=time.monotonic()-started))
    print(json.dumps(dict(summary={g:{k:{q:v[q] for q in ['fixed','hold','fail','raw_strict_fixed']} for k,v in ss.items()} for g,ss in summaries.items()},holds=hold_counts),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
