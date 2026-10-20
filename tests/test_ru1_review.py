"""Synthetic pixels and retained-geometry fixtures only; no real review positions."""
import json
import sys
from pathlib import Path
import pytest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
from ru1_review import render_sheets, symbol_crops, reviews


def cell():
    return dict(line=Image.new('RGB',(500,30),'white'),word=Image.new('RGB',(60,25),'gray'),final=Image.new('RGB',(15,25),'black'),title='FIXTURE',source_id='synthetic',annotation='r1: ъ   r2: ь   prior: unknown')


def test_pagination_and_index(tmp_path):
    ix=render_sheets([cell() for _ in range(25)],tmp_path)
    assert len(ix)==25
    assert [sum(i['sheet']==s for i in ix) for s in sorted({i['sheet'] for i in ix})]==[12,12,1]
    assert json.loads((tmp_path/'sheets_index.json').read_text())['sheets']==3
    for path in tmp_path.glob('*.png'):
        with Image.open(path) as im:im.verify()
    with pytest.raises(ValueError):render_sheets([],tmp_path,max_cells=13)


def test_empty_sheet_index(tmp_path):
    assert render_sheets([],tmp_path)==[]
    assert json.loads((tmp_path/'sheets_index.json').read_text())['cells']==0


def test_exact_offset_and_geometry():
    def layout(a,b,x):return dict(textAnchor=dict(textSegments=[dict(startIndex=str(a),endIndex=str(b))]),boundingPoly=dict(vertices=[dict(x=x,y=3),dict(x=x+8,y=13)]))
    line=dict(layout=layout(0,4,0));doc=dict(text='абь\n',pages=[dict(dimension=dict(width=100,height=20),symbols=[dict(layout=layout(i,i+1,i*10)) for i in range(3)])])
    word,final,g=symbol_crops(Image.new('RGB',(100,20)),'абь',2,doc,line,[0,0])
    assert g['final_box']==[18,1,30,15] and final.size==(12,14) and word.size==(30,14)
    with pytest.raises(ValueError,match='differs'):symbol_crops(Image.new('RGB',(100,20)),'абъ',2,doc,line,[0,0])


def test_review_cells_with_calls_and_prior(monkeypatch,tmp_path):
    import ru1_review
    class FixtureResolver:
        def resolve(self,*args):return cell()
    monkeypatch.setattr(ru1_review,'Resolver',FixtureResolver)
    d=dict(row_id='synthetic',offset=2,decision='lead_review',prior='ь_only',reads={r:dict(pack_context='ctx01',item_id='fixture',call=c,gate_status='VALID') for r,c in [('r1','ъ'),('r2','ь')]})
    ix=reviews([d],tmp_path);assert ix[0]['prior']=='ь_only' and 'r2: ь' in ix[0]['annotation']
    d['reads']['r2']=None
    with pytest.raises(ValueError,match='r2 missing'):reviews([d],tmp_path)
