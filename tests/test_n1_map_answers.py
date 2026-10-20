import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('mapper',Path(__file__).resolve().parents[1]/'scripts/numerics/n1_map_answers.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def key():
    return dict(readers={'r1':['k1','k2','k3','k4']},items={f'k{i}':dict(slot_id=f's{i}',option_map={'A':'comma','B':'unreadable'},control_truth='comma' if i<3 else None,geometry={'geom_status':'ok'},geometry_record_ref='g',google_glyph='.') for i in range(1,5)})


def test_void_unreadable_invalid_missing():
    result=m.map_answers(key(),[dict(item_id='k1',answer='B'),dict(item_id='k2',answer='Z'),dict(item_id='k3',answer='B')])
    assert result['context_status']=='VOID';assert result['control_errors']==2
    assert [s['status'] for s in result['slots']]==['unreadable','invalid_letter','unreadable','missing']
    assert all(s['google_glyph']=='.' and s['geometry']['geom_status']=='ok' for s in result['slots'])


def test_one_error_valid():
    result=m.map_answers(key(),[dict(item_id=f'k{i}',answer='A' if i!=1 else 'B') for i in range(1,5)])
    assert result['context_status']=='VALID';assert result['control_errors']==1


def test_duplicate_unexpected():
    result=m.map_answers(key(),[dict(item_id='k1',answer='A')]*2+[dict(item_id='extra',answer='A')])
    assert result['slots'][0]['status']=='duplicate';assert result['unexpected_ids']==['extra']
