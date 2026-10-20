"""RU1-S gate regression and line-card semantics, with no inference or run writes."""
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary/reading'))
from ru1_map_answers import score_controls, map_records, DISPUTED_CONTROL
from ru1_decide import combine
from ru1_owner_sheet import proposed, select_lines, group_for


def control(call='ъ', truth='ъ', **fields):
    return dict(dict(control=True,control_truth=truth,source_id='row',row_id='row',slot=1,item_id='k1',call=call),**fields)


@pytest.mark.parametrize('calls,status,wrong,abstain',[
    (['u','u'],'VALID',0,2),(['ь','u'],'VALID',1,1),(['ь','ь'],'VOID',2,0),
    (['other','ъ'],'VALID',1,0),(['other','ь'],'VOID',2,0),(['ъ','ъ'],'VALID',0,0)])
def test_wrong_sign_gate(calls,status,wrong,abstain):
    s=score_controls([control(c) for c in calls])
    assert (s['status'],s['wrong_signs'],s['abstentions'])==(status,wrong,abstain)
    assert s['correct']+s['wrong_signs']+s['abstentions']==s['control_slots']


@pytest.mark.parametrize('call',['ъ','ь','u','other'])
def test_disputed_slot_excluded_only(call):
    source,slot=DISPUTED_CONTROL
    records=[control(call,truth='ь',source_id=source,slot=slot),control('ь')]
    s=score_controls(records)
    assert s['status']=='VALID' and s['wrong_signs']==1 and s['excluded']==1 and s['abstentions']==0
    assert s['control_slots']==1 and s['controls'][0]['outcome']=='excluded'
    records[0]['slot']=1
    assert score_controls(records)['excluded']==0


def test_mapper_abstention_and_disputed_control_both_readers():
    for reader in ['r1','r2']:
        ids=['k1','k2','k3']; items=[dict(item_id=i,slots=n) for i,n in zip(ids,[2,1,1])]
        meta={}
        for i,calls in zip(ids,[['ъ','ъ'],['u'],['ъ']]):
            meta[i]=dict(control=i!='k3',source_id=DISPUTED_CONTROL[0] if i=='k1' else i,row_id=DISPUTED_CONTROL[0] if i=='k1' else i,
                slots=[dict(offset=n,google='ь',kind='final',prior='unknown',control_truth='ь' if i=='k1' else 'ъ' if i=='k2' else None) for n in range(len(calls))])
        answers=[dict(item_id=i,slots={str(n+1):c for n,c in enumerate(calls)},confidence={str(n+1):'high' for n in range(len(calls))},unmarked_final_hard_signs=[],pre1918='yes',note='') for i,calls in zip(ids,[['ъ','ъ'],['u'],['ъ']])]
        m,s=map_records(answers,dict(context='ctx01',readers={reader:ids},items=meta),items,reader)
        assert (s['wrong_signs'],s['abstentions'],s['excluded'],s['status'])==(1,1,1,'VALID')
        assert m[-1]['edit_proposal'] is not None


def test_combiner_rejects_stale_gate(tmp_path):
    a=tmp_path/'answers';a.mkdir()
    (a/'ctx01.mapped.jsonl').write_text(json.dumps(control('u'))+'\n')
    (a/'ctx01.controls.json').write_text(json.dumps(dict(status='VOID')))
    (a/'ctx01.scan.json').write_text(json.dumps(dict(ok=True)))
    with pytest.raises(ValueError,match='stale control gate'):combine(tmp_path)


def decision(off=1,kind='edit_hard'):
    return dict(offset=off,google='ь',kind='final',decision=kind)


def test_proposed_edits_only_selected_soft_offsets():
    ds=[decision(),decision(4,'lead_review'),decision(7,'keep_soft')]
    assert proposed('аь бь вь ъ',ds)=='аъ бь вь ъ'


@pytest.mark.parametrize('ds',[ [decision(),decision()], [decision(2)], [dict(decision(),kind='pre_hyphen')] ])
def test_bad_proposal_offsets_fail(ds):
    with pytest.raises(ValueError):proposed('аь ъ',ds)


def test_line_severity_and_seeded_keep_sample():
    by={f'line{i:03}':[decision(kind='keep_soft')] for i in range(100)}
    by['edit']=[decision(),decision(4,'keep_soft')]
    by['review']=[decision(),decision(4,'lead_review')]
    full,shown=select_lines(by)
    assert len(full['keep_soft'])==100 and len(shown['keep_soft'])==40
    assert shown==select_lines(dict(reversed(list(by.items()))))[1]
    assert shown['edit_hard']==['edit'] and shown['lead_review']==['review']
    assert group_for(by['review'])=='lead_review'
