"""Machine clauses for every owner note; current numbering is frozen S4.

Older checks retain their original exact naming semantics. New checks score
physical evidence and segmentation, with uncertain owner wording explicit.
Empty notes preserve S4 known truth and all its detected physical evidence;
no-note lines are not certified as reviewed.
"""
import json
from collections import Counter
from pathlib import Path
from scripts.labelfix.s5_validate import read,write
from scripts.labelfix.s5_notes import evaluate as old_evaluate,specs
from scripts.labelfix.s6_validate import detected,physical,zones
O=Path('docs/records/labelfix/spellcheck')


def current_review_specs():
    d={}
    def put(lid,*clauses):d[lid]=list(clauses)
    def marks(lid,*ns):put(lid,*[('mark',n,1) for n in ns])
    marks('02a3a2a6-p000046-l0014',8);marks('177b717d-p000013-l0009',13)
    put('177b717d-p000072-l0001',('fusion',33,2),('mark',33,1))
    marks('177b717d-p000104-l0007',23)
    put('2793d64c-p000048-l0004',('subscript',19,None))
    put('2793d64c-p000048-l0010',('uncertain',24,'possible subscript'))
    put('2793d64c-p000070-l0010',('no_top',22,None))
    put('2793d64c-p000072-l0007',('mark',4,1),('uncertain',24,'possible mark'))
    for lid,n in [('384c3f89-p000030-l0021',22),('384c3f89-p000059-l0027',21)]:put(lid,('apostrophe',n,None))
    marks('384c3f89-p000053-l0010',18,24);marks('384c3f89-p000053-l0028',32)
    for lid,n in [('384c3f89-p000091-l0011',3),('384c3f89-p000121-l0024',15),('384c3f89-p000170-l0031',22),('384c3f89-p000183-l0005',26),('8b6b0de9-p000004-l0028',5)]:put(lid,('fusion',n,2),('mark',n,1))
    put('384c3f89-p000091-l0039',('fusion',20,2),('letter_mark',20,'υ'))
    put('384c3f89-p000142-l0002',('split_union',[1,2],'η'),('mark',1,2))
    marks('384c3f89-p000179-l0022',28);marks('384c3f89-p000182-l0006',26)
    put('384c3f89-p000205-l0005',('subscript',13,None),('mark',1,2))
    marks('51fe7386-p000024-l0020',4);marks('602cc72e-p000113-l0016',3)
    for lid in ('602cc72e-p000113-l0030','602cc72e-p000155-l0009'):put(lid,('safe_zone',None,None),('printed_top_presence',None,None))
    marks('602cc72e-p000167-l0027',1,6,10,14)
    put('8b6b0de9-p000007-l0030',('fusion',15,3),('letter_mark',15,'ω'))
    marks('8b6b0de9-p000008-l0001',7)
    # The frozen v8/S4 expectation identifies the exclamation stem as slot 13.
    # The alpha in ᾄδου has a legitimate subscript; it is not this false dot.
    put('8b6b0de9-p000008-l0002',('no_subscript',13,None))
    marks('8b6b0de9-p000008-l0019',2);marks('8b6b0de9-p000008-l0024',3)
    put('8b6b0de9-p000011-l0007',('no_subscript',9,None))
    put('8b6b0de9-p000011-l0014',('fusion',4,2),('mark',4,1),('fusion',6,2),('mark',6,1))
    marks('9c1dca9b-p000005-l0017',9)
    put('9c1dca9b-p000015-l0051',('fusion',3,2),('mark',3,1),('mark',26,1))
    put('9c1dca9b-p000015-l0057',('fusion',12,3),('mark',12,1))
    put('9c1dca9b-p000015-l0060',('fusion',7,3),('mark',7,1),('mark',15,1))
    marks('9c1dca9b-p000015-l0065',8);marks('9c1dca9b-p000015-l0067',2)
    return d


def targets(line,ns):
    # S4/S5 only carry the primary component number; a union owns the additional
    # original labels as well. S6 explicitly serializes all source slot numbers.
    out=[]
    for r in line['recogniser_slots']:
        ids=r.get('component_slots') or [r.get('component_slot')]
        if set(ids)&set(ns):out.append(r)
    return out


def clause(line,baseline,kind,target,value):
    if line is None or baseline is None:return False,dict(unresolved='missing target line')
    ns=target if isinstance(target,list) else [target] if target is not None else []
    rs=targets(line,ns)
    ss=[s for s in line['slots'] if s['slot'] in ns]
    if ns and (not rs or any(not targets(line,[n]) for n in ns)):
        return False,dict(unresolved='missing target',targets=ns)
    if kind=='uncertain':return False,'owner uncertainty; no positive truth asserted'
    if kind=='no_regression':
        errors=[]
        newslots={s['slot']:s for s in line['slots']}
        for b in baseline['slots']:
            s=newslots.get(b['slot'])
            if s is None:
                errors.append(b['slot']);continue
            if s['truth'] is None:continue
            t,a,old=[set(map(tuple,x)) for x in (s['truth'],s['detected'],b['detected'])]
            if (t&old)-a or (a-t)-(old-t):errors.append(s['slot'])
        # Also preserve all physical marks on reviewed-empty lines; frozen print
        # unknowns cannot silently license dropping the owner's accepted marks.
        oldby={r['start']:r for r in baseline['recogniser_slots']}
        newby={r['start']:r for r in line['recogniser_slots']}
        name_changes=[start for start,r in oldby.items() if start not in newby or
                      Counter(r.get('parts',[]))!=Counter(newby[start].get('parts',[])) or
                      bool(r.get('apostrophe'))!=bool(newby[start].get('apostrophe'))]
        lost=[r['start'] for r in line['recogniser_slots'] if not set(physical(oldby.get(r['start'])))<=set(physical(r))]
        known={s['slot'] for s in line['slots'] if s['truth'] is not None}
        unknown_additions=[]
        for r in line['recogniser_slots']:
            sources=r.get('component_slots') or [r.get('component_slot')]
            if set(sources)&known:continue
            old=oldby.get(r['start'],{})
            if set(physical(r))-set(physical(old)) or set(r.get('parts',[]))-set(old.get('parts',[])):
                unknown_additions.append(r['start'])
        # Empty means the owner accepted S4. A new mark/name at an unknown
        # print slot cannot be certified correct merely because truth is absent.
        return not errors and not lost and not unknown_additions and not name_changes,dict(approved_name_changes=name_changes,new_naming_errors=errors,lost_presence=lost,uncertified_unknown_additions=unknown_additions)
    if kind=='safe_zone':
        bad=[r['start'] for r in line['recogniser_slots'] for b in r.get('evidence',{}).get('above',[]) if b['source']!='preposed' and b['bbox'][3]>r['evidence']['meanline']]
        return not bad,dict(below_own_meanline=bad)
    if kind=='printed_top_presence':
        missed=[s['slot'] for s in line['slots'] if s['truth'] is not None and 'above' in zones(s['truth']) and not s['evidence']['above']]
        return not missed,dict(missed=missed)
    if kind in ('mark','letter_mark','word_accent'):
        if kind=='letter_mark':rs=[r for r in rs if r['base'].lower()==value]
        if kind=='word_accent':rs=[r for r in line['recogniser_slots'] if r['base'].lower()==value]
        count=sum(len(r.get('evidence',{}).get('above',[])) for r in rs)
        return count>=(value if kind=='mark' else 1),dict(blobs=count,required=value if kind=='mark' else 1,starts=[r['start'] for r in rs])
    if kind in ('subscript','no_subscript','no_subscripts'):
        selected=line['recogniser_slots'] if kind=='no_subscripts' else rs
        count=sum(len(r.get('evidence',{}).get('below',[])) for r in selected)
        return (count>0 if kind=='subscript' else count==0),dict(blobs=count)
    if kind=='no_top':return not any(r.get('evidence',{}).get('above') for r in rs),dict(starts=[r['start'] for r in rs])
    if kind=='fusion':
        located=[r for r in rs if not r.get('localisation_unknown')]
        boxes=[r.get('bbox') for r in located]
        return len(located)>=value and all(b is not None for b in boxes) and all(a[2]<=b[0] for a,b in zip(boxes,boxes[1:])),dict(located=len(located),required=value,boxes=boxes)
    if kind in ('split_union','union_base','base'):
        good=[r for r in rs if r['base'].lower()==value and not r.get('localisation_unknown')]
        ok=len(good)==1 and (kind=='base' or len(good[0].get('component_ids',[]))>=len(ns))
        return ok,dict(starts=[r['start'] for r in good])
    if kind in ('quote','leading_sign'):return bool(line.get('opening_quotes')),dict(boxes=line.get('opening_quotes'))
    if kind=='apostrophe':return any(r.get('apostrophe') for r in rs),dict(starts=[r['start'] for r in rs])
    if kind=='named':return bool(rs) and all(not r.get('unnamed') for r in rs),dict(naming_check=True)
    if kind=='whole_marks':
        return all(s['truth'] is None or set(zones(s['truth']))==set(zones(s['detected'])) for s in line['slots']),dict(uses_frozen_presence=True)
    if kind=='word_slots':
        from greekocr.labelfix.text import tokenize,nfd,clusters
        ts=[t for t in tokenize(nfd(line['recogniser_text'])) if value in ''.join(c.base for c in clusters(t.core))]
        rr=[r for t in ts for r in line['recogniser_slots'] if t.core_start<=r['start']<t.core_end]
        return bool(rr) and all(not r.get('localisation_unknown') for r in rr),dict(starts=[r['start'] for r in rr])
    return False,dict(unresolved_kind=kind)


def main():
    versions={k:{l['line_id']:l for l in read(O/f'{k}_lines.jsonl.gz')} for k in ('S4','S5','S6')}
    for k in ('S4','S5','S6'):
        old=old_evaluate(list(versions[k].values()),list(versions['S4'].values()))
        (O/f'S6_old_checks_{k}.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
    groups={};spec=specs()
    # The new example adds only the capital-T clause; older nonempty wording
    # keeps its parsed clauses but now resolves against the displayed S4 slots.
    spec['8b6b0de9-p000021-l0012']=[('no_top',1,None)]
    for name,path,lookup in [('review','owner_notes_review_v16_20261016.jsonl',current_review_specs()),('examples','owner_notes_examples_v10_20261016.jsonl',spec)]:
        checks=[]
        for note in read(O/path):
            lid=note['line_id'];clauses=lookup.get(lid) if note['note'] else [('no_regression',None,None)]
            assert clauses is not None,(lid,note)
            row=dict(line_id=lid,note=note['note'],note_set=path,reviewed_snapshot='S4_lines.jsonl.gz',checks=[])
            for kind,target,value in clauses:
                c=dict(kind=kind,target=target,value=value,versions={})
                for k,by in versions.items():
                    ok,ev=clause(by.get(lid),versions['S4'].get(lid),kind,target,value)
                    c['versions'][k]=dict(fixed=ok,evidence=ev)
                row['checks'].append(c)
            row['fixed']={k:all(c['versions'][k]['fixed'] for c in row['checks']) for k in versions}
            checks.append(row)
        groups[name]=checks;write(O/f'S6_current_{name}_checks.jsonl',checks)
    summary={name:{k:dict(fixed=sum(r['fixed'][k] for r in rs),n=len(rs),clauses_fixed=sum(c['versions'][k]['fixed'] for r in rs for c in r['checks']),clauses=sum(len(r['checks']) for r in rs)) for k in versions} for name,rs in groups.items()}
    (O/'S6_owner_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(summary)
    notes={n['line_id'] for f in ('owner_notes_review_v16_20261016.jsonl','owner_notes_examples_v10_20261016.jsonl','owner_notes_db_20261016.jsonl','owner_notes_examples_20261016.jsonl') for n in read(O/f)}
    changed=[]
    for lid in sorted(notes):
        l=versions['S6'][lid]
        if any(versions[k][lid]['reading']!=l['reading'] for k in ('S4','S5')):changed.append(dict(line_id=lid,S4=versions['S4'][lid]['reading'],S5=versions['S5'][lid]['reading'],S6=l['reading']))
    write(O/'S6_changed_owner_lines.jsonl',changed)

if __name__=='__main__':main()
