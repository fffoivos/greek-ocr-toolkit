"""Frozen owner-note checks, including all 56 examples and 33 review notes.

Review prefills are never read. Component slots resolve against both S2/S3.
"""
import json
from collections import defaultdict
from pathlib import Path
from scripts.labelfix.s4_report import read, units, same, SPECS
from scripts.labelfix.s3_report import passes
from greekocr.labelfix.owner_slots import overlap_slots
O=Path('docs/records/labelfix/spellcheck')

def specs():
    old=read(O/'S4_owner_notes_snapshot.jsonl')
    out={n['line_id']:s for n,s in zip(old,SPECS)}
    def put(lid,*ss):out[lid]=list(ss)
    def marks(lid,*ns):put(lid,*[('mark',n,1) for n in ns])
    put('02a3a2a6-p000041-l0005',('word_slots',None,'λο'),('mark',24,1),('subscript',28,None))
    put('02a3a2a6-p000046-l0014',('apostrophe',8,None))
    put('02a3a2a6-p000307-l0003',('apostrophe',2,None),('apostrophe',15,None))
    marks('02a3a2a6-p000318-l0017',2);marks('177b717d-p000017-l0012',11,12);marks('177b717d-p000097-l0010',2,5)
    put('2793d64c-p000033-l0022',('mark',1,1),('apostrophe',11,None))
    put('384c3f89-p000050-l0016',('mark',5,2),('mark',19,1))
    put('384c3f89-p000068-l0036',('apostrophe',6,None),('mark',7,2),('mark',30,1))
    put('384c3f89-p000091-l0027',('mark',1,2),('union_base',[1,2],'η'))
    for lid,n in [('384c3f89-p000142-l0010',14),('384c3f89-p000170-l0024',12)]:put(lid,('subscript',n,None))
    for lid,n in [('384c3f89-p000182-l0023',3),('384c3f89-p000183-l0022',20)]:put(lid,('apostrophe',n,None))
    put('384c3f89-p000183-l0009',('mark',9,2))
    put('51fe7386-p000024-l0015',('quote',1,None),('mark',2,1),('mark',29,1))
    for lid,ns in [('602cc72e-p000113-l0009',[1,9,10,12]),('602cc72e-p000167-l0027',[6,10,14]),('8b6b0de9-p000007-l0011',[1,2,4]),('8b6b0de9-p000007-l0021',[4,18]),('8b6b0de9-p000008-l0001',[7,12]),('8b6b0de9-p000016-l0013',[3,5]),('9c1dca9b-p000005-l0017',[9,14,23,27]),('9c1dca9b-p000015-l0065',[8])]:marks(lid,*ns)
    return out

def evaluate(lines, baseline):
    by={l['line_id']:l for l in lines};bb={l['line_id']:l for l in baseline}
    s2={l['line_id']:l for l in read(O/'S2_lines.jsonl.gz')};s3={l['line_id']:l for l in read(O/'S3_lines.jsonl.gz')}
    earlier=[];groups=defaultdict(list)
    for prior in read(O/'S4_owner_expectations.jsonl'):
        e=dict(prior);l=by[e['line_id']];slot,hits=overlap_slots(e['v8_x0'],e['v8_x1'],l['slots'])
        s=next((s for s in l['slots'] if s['slot']==slot),None)
        e.update(mapped_slot=slot,fixed=passes(e,s,l['slots'],False),s4_fixed=prior['fixed'])
        earlier.append(e);groups[e['line_id']].append(e)
    examples=[]
    for note in read(O/'owner_notes_examples_20261016.jsonl'):
        lid=note['line_id'];l=by[lid];b=bb[lid];checks=[]
        for kind,target,value in specs()[lid]:
            targets=target if isinstance(target,list) else [target] if target is not None else []
            resolution={v:[dict(slot=k,bbox=src[lid]['slots'][k-1]['bbox'],base=src[lid]['slots'][k-1]['base']) for k in targets if k<=len(src[lid]['slots'])] for v,src in [('S2',s2),('S3',s3)]}
            ambiguous=kind=='ambiguous' or resolution['S2']!=resolution['S3']
            def good(line):
                ss=[s for s in line['slots'] if s['slot'] in targets]
                if ambiguous:return False
                if kind in ('mark','subscript','apostrophe'):
                    if len(ss)!=1:return False
                    s=ss[0];ms=s['detected'];truth=s['truth']
                    if kind!='mark':return any(k==kind for k,v in ms)
                    return units(ms)>=value and (truth is None or set(map(tuple,truth))<=set(map(tuple,ms)))
                if kind in ('quote','leading_sign'):return bool(line.get('opening_quotes'))
                if kind=='named':return bool(ss) and not ss[0].get('unnamed')
                if kind=='whole_marks':return all(same(s['truth'],s['detected']) for s in line['slots'] if s['truth'] is not None)
                if kind=='no_regression':
                    return all(not ((set(map(tuple,s['truth'])) & set(map(tuple,old['detected'])))-set(map(tuple,s['detected']))) and not ((set(map(tuple,s['detected']))-set(map(tuple,s['truth'])))-(set(map(tuple,old['detected']))-set(map(tuple,s['truth'])))) for s,old in zip(line['slots'],b['slots']) if s['truth'] is not None)
                rs=[r for r in line['recogniser_slots'] if r.get('component_slot') in targets]
                if kind in ('base','union_base'):
                    return bool(rs) and all(r['base'].lower()==value and not r['localisation_unknown'] for r in rs) and (kind!='union_base' or len(rs)==1 and len(rs[0].get('component_ids',[]))==len(targets))
                from greekocr.labelfix.text import tokenize,nfd,clusters
                ts=[t for t in tokenize(nfd(line['recogniser_text'])) if value in ''.join(c.base for c in clusters(t.core))]
                rs=[r for t in ts for r in line['recogniser_slots'] if t.core_start<=r['start']<t.core_end]
                return bool(rs) and all(not r['localisation_unknown'] for r in rs) and (kind!='word_accent' or any(r['base']==value and set(r.get('parts',[]))&{'acute','grave','circumflex'} for r in rs))
            checks.append(dict(kind=kind,slots=targets,value=value,slot_lists=resolution,ambiguous=ambiguous,before_fixed=good(b),fixed=good(l)))
        examples.append(dict(line_id=lid,note=note['note'],expectations=checks,before_fixed=all(c['before_fixed'] for c in checks),fixed=all(c['fixed'] for c in checks)))
    review=[]
    for n in read(O/'owner_notes_db_20261016.jsonl'):
        lid=n['line_id'];es=groups[lid]
        if not n['note']:
            errors=[]
            for s,b in zip(by[lid]['slots'],bb[lid]['slots']):
                if s['truth'] is None:continue
                t,a,old=[set(map(tuple,x)) for x in (s['truth'],s['detected'],b['detected'])]
                if (t&old)-(t&a) or (a-t)-(old-t):errors.append(s['slot'])
            review.append(dict(line_id=lid,note=n['note'],before_fixed=True,fixed=not errors,new_errors=errors))
        else:review.append(dict(line_id=lid,note=n['note'],before_fixed=all(e['s4_fixed'] for e in es) if es else False,fixed=bool(es) and all(e['fixed'] for e in es),checks=[dict(slot=e['v8_slot'],expected=e['expected'],before_fixed=e['s4_fixed'],fixed=e['fixed'],ambiguous=e.get('ambiguous',False)) for e in es]))
    return dict(earlier=earlier,examples=examples,review=review)

if __name__=='__main__':
    baseline=read(O/'S4_lines.jsonl.gz');result=evaluate(baseline,baseline)
    (O/'S5_baseline_owner_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print({k:(sum(r['fixed'] for r in v),len(v)) for k,v in result.items()})
