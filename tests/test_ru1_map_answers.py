import copy
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary/reading'))
from ru1_map_answers import map_records

def fixture(calls=('ъ','ъ','ъ','ь')):
    items=[];answers=[];key=dict(context='ctx01',readers={'r1':[]},items={})
    for i,call in enumerate(calls):
        iid=f'k{i:010x}';items.append(dict(item_id=iid,slots=1));key['readers']['r1'].append(iid)
        key['items'][iid]=dict(control=i<2,row_id=f'row{i}',source_id=f'row{i}',slots=[dict(offset=3,google='ъ' if i==3 else 'ь',kind='final',prior='unknown',control_truth='ъ' if i<2 else None)])
        answers.append(dict(item_id=iid,slots={'1':call},confidence={'1':'high'},unmarked_final_hard_signs=[],pre1918='yes',note=''))
    return answers,key,items

def test_void_context_removes_every_edit():
    a,k,i=fixture(('ь','ь','ъ','ь'));mapped,score=map_records(a,k,i)
    assert score['status']=='VOID' and score['control_errors']==2
    assert all(r['edit_proposal'] is None for r in mapped)

def test_u_hold():
    a,k,i=fixture(('ъ','ъ','u','ь'));m,s=map_records(a,k,i)
    assert m[2]['needs_review'] and m[2]['edit_proposal'] is None

def test_other_hold():
    a,k,i=fixture(('ъ','ъ','other','ь'));m,s=map_records(a,k,i)
    assert m[2]['needs_review'] and m[2]['edit_proposal'] is None

def test_missing_item_fail_closed():
    a,k,i=fixture()
    with pytest.raises(ValueError,match='missing item'):map_records(a[:-1],k,i)

def test_google_hard_read_soft_never_edits():
    a,k,i=fixture();m,s=map_records(a,k,i)
    assert s['google_hard_read_soft']==1 and m[3]['edit_proposal'] is None
    assert m[2]['edit_proposal']==dict(offset=3,old='ь',new='ъ')

def test_pre_hyphen_never_edits():
    a,k,i=fixture();k['items'][i[2]['item_id']]['slots'][0]['kind']='pre_hyphen'
    m,s=map_records(a,k,i);assert m[2]['edit_proposal'] is None

def test_single_control_error_allowed():
    a,k,i=fixture(('u','ъ','ъ','ь'));m,s=map_records(a,k,i)
    assert s['control_errors']==1 and s['status']=='VALID' and m[2]['edit_proposal'] is not None

def test_answer_order_fail_closed():
    a,k,i=fixture()
    with pytest.raises(ValueError,match='order'):map_records(list(reversed(a)),k,i)
