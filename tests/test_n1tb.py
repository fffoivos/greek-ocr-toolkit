"""N1-Tb pruning custody, scoring and complete-line integration regressions."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
from greekocr.numerics.prune import prune,has_gap_component
from greekocr.numerics.combine_v2 import decide,DASHES,decode_and_gate,MEANINGS
from n1_calibration import score
from n1_map_answers import map_answers
from n1t_packs import rows,sha,typed_controls
from test_n1t import key_fixture,owner_fixture,owner_build
BASE=ROOT/'artifacts/n1'


def slot(sid='s',glyph='',components=(),status='ok',gap=(10,20)):
    return dict(slot_id=sid,line_id='l',glyph=glyph,geometry=dict(geom_status=status,gap=gap),
                measurements=dict(components=[dict(bbox=b) for b in components]))


def test_prune_space_mark_crossing_components_zero_gap_and_failure():
    inputs=[slot('empty'),slot('space',' '),slot('dot','.'),slot('ink',components=[[12,0,14,2]]),
            slot('overhang',components=[[8,0,12,5]]),slot('digit',components=[[0,0,10,10]]),
            slot('touch',components=[[8,0,22,10]],gap=(12,12)),slot('fail',status='misaligned')]
    result=prune(inputs,0)
    assert [s['read_reason'] for s in result]==['geometry-only','google-mark','google-mark','ink-only','ink-only','geometry-only','geometry-only','geom-fail']
    assert all('read_reason' not in s for s in inputs)
    assert decide(result[0],[])['reason']=='nothing (geometry)'
    with pytest.raises(ValueError):decide(dict(result[3],read_reason='geometry-only'),[])
    assert decide(result[-1],[])['status']=='lead_review'


def test_audit_seed_is_stable_order_independent_and_requires_reads():
    inputs=[slot(f's{i}') for i in range(100)]
    a=prune(inputs);b=prune(list(reversed(inputs)))
    aa={s['slot_id'] for s in a if s['read_reason']=='audit'}
    assert len(aa)==30 and aa=={s['slot_id'] for s in b if s['read_reason']=='audit'}
    assert all(decide(s,[])['truth_candidate'] is None for s in a if s['read_reason']=='audit')


@pytest.mark.parametrize('meaning',MEANINGS)
def test_unsure_controls_gate_mapper_and_calibration_accept_exactly_dashes(meaning):
    key,answers=key_fixture(['hyphen'])
    item=next(iter(key['items'].values()));item.update(control_truth='any dash',geometry={},google_glyph='-')
    answers[0]['answer']=next(k for k,v in item['option_map'].items() if v==meaning)
    gate,_=decode_and_gate(key,answers)
    assert gate['wrong']==int(meaning not in DASHES) and gate['abstentions']==0
    mapped=map_answers(key,answers)
    assert mapped['control_errors']==int(meaning not in DASHES)
    key['calibration']=True
    result=score(key,mapped,[dict(slot_id=item['slot_id'],truth='any dash')])
    assert result['correct']==int(meaning in DASHES)


def test_owner_keeps_geometry_nothing_rows_and_all_gap_boxes_and_ours_complete(tmp_path):
    line,slots,ds=owner_fixture(tmp_path)
    empty=next(s for s in slots if s['glyph']=='')
    empty['read_reason']='geometry-only';empty['measurements']={'components':[]}
    ds[[s['slot_id'] for s in slots].index(empty['slot_id'])]=decide(empty,[])
    c=owner_build([line],slots,ds)[0][0]
    assert c['printed']=='1·234 5·678'
    assert len(c['rows'][2]['text'].splitlines())==len(slots)
    assert 'nothing (geometry)' in c['rows'][2]['text']
    assert empty['slot_id'] not in {s['slot_id'] for s in c['slots']}
    assert len(c['slots'])==len(slots)-1
    assert sum(bool(s['evidence']) for s in c['slots'])==len(slots)-1


def test_real_pruning_partition_seal_and_superseded_custody():
    require_file('artifacts/n1/n1t/slots.jsonl')
    source=rows(BASE/'n1t/slots.jsonl');current=rows(BASE/'n1t2/slots.jsonl')
    expected=prune(source)
    assert [(s['slot_id'],s['read_reason']) for s in current]==[(s['slot_id'],s['read_reason']) for s in expected]
    assert Counter(s['read_reason'] for s in current)=={'google-mark':637,'ink-only':391,'geom-fail':1,'audit':30,'geometry-only':1070}
    automatic=rows(BASE/'n1t2/geometry_decisions.jsonl')
    assert automatic==[decide(s,[]) for s in current if s['read_reason']=='geometry-only']
    assert len(current)==2129 and len({s['line_id'] for s in current})==207
    preserved=json.loads((_data_input(BASE/'n1t2/superseded.json')).read_text())['files']
    # Owner outputs are authorized replacements in N1-TS2, not superseded packs.
    # Receipt paths belong to the producing checkout; the owner-sheet exception
    # is relative to the N1 artifact tree in every checkout.
    assert preserved and all(sha(p)==h for p,h in preserved.items()
                             if Path(p).parts[-4:-1] != ('artifacts', 'n1', 'owner_sheet'))
    assignments=rows(BASE/'controls/dash_types.jsonl')
    assert Counter(s['truth'] for s in assignments)=={'hyphen':14,'en dash':6,'em dash':5,'any dash':2}
    assert {s['cell_number'] for s in assignments if s['truth']=='any dash'}=={61,64}
    assert (_data_input(BASE/'controls/dash_types.jsonl.sha256')).read_text().split()[0]==sha(BASE/'controls/dash_types.jsonl')
    assert typed_controls(rows(BASE/'controls/approved.jsonl'),assignments)==rows(BASE/'n1cal2/controls/approved.jsonl')


def test_real_pruned_pack_coverage_controls_failure_and_independence():
    from n1_render import SCRATCH
    for items_path in sorted((SCRATCH / 'sol_packs/n1t2').glob('ctx*/r*/items.jsonl')):
        for item in rows(items_path):
            for name in ('line', 'zoom'):
                required = items_path.parent / item[name]
                if not required.is_file():
                    pytest.skip(f'missing input: {required}')
    from n1_render import SCRATCH
    current={s['slot_id']:s for s in rows(BASE/'n1t2/slots.jsonl')}
    expected={sid for sid,s in current.items() if s['read_reason']!='geometry-only'}
    seen={r:Counter() for r in ('r1','r2')};ids=set()
    contexts=sorted((SCRATCH/'sol_packs/n1t2').glob('ctx*'))
    assert len(contexts)==14
    for ctx in contexts:
        keys=[]
        for reader,suffix in [('r1',''),('r2','.r2')]:
            key=json.loads((_data_input(BASE/'n1t2/keys'/(ctx.name+suffix+'.json'))).read_text());keys.append(key)
            assert len(key['items'])<=100 and not ids.intersection(key['items']);ids.update(key['items'])
            controls=[i for i in key['items'].values() if i['control_truth'] is not None]
            truths=Counter(i['control_truth'] for i in controls)
            assert len(controls)==len({i['slot_id'] for i in controls})==9
            assert all(truths[t]>=1 for t in ('raised dot',*DASHES))
            for p in rows(ctx/reader/'items.jsonl'):
                i=key['items'][p['item_id']]
                if i['control_truth'] is None:
                    seen[reader][i['slot_id']]+=1
                    for name in ('line','zoom'):assert sha(ctx/reader/p[name])==current[i['slot_id']][name+'_sha256']
            assert (_data_input(ctx/reader/'answers.jsonl')).read_bytes()==(_data_input(BASE/'answers/n1t2'/f'{ctx.name}.{reader}.jsonl')).read_bytes()
        a=[keys[0]['items'][i] for i in keys[0]['readers']['r1']]
        b=[keys[1]['items'][i] for i in reversed(keys[1]['readers']['r2'])]
        assert [i['slot_id'] for i in a]==[i['slot_id'] for i in b]
        assert all(all(x['option_map'][k]!=y['option_map'][k] for k in x['option_map']) for x,y in zip(a,b))
    assert all(c==Counter({sid:1 for sid in expected}) for c in seen.values())
    failed=next(s for s in current.values() if s['read_reason']=='geom-fail')
    assert failed['geometry']=={'geom_status':'misaligned','reason':'reversed digit boxes'}
    assert failed['render_scope']=='whole_line_unlocalized'


def test_combiner_requires_each_selected_slot_both_readers_and_no_omitted_slot_reads():
    from n1t_combine import require_complete
    ss=prune([slot('empty'),slot('mark','-'),slot('fail',status='misaligned')],0)
    rr={sid:[dict(reader=r) for r in ('r1','r2')] for sid in ('mark','fail')}
    require_complete(ss,rr)
    for bad in [{}, {'mark':rr['mark']},dict(rr,empty=rr['mark']),dict(rr,fail=[dict(reader='r1')]*2)]:
        with pytest.raises(ValueError,match='both complete'):require_complete(ss,bad)
