from greekocr.numerics.slots_geom import locate_slot
from greekocr.numerics.locks import load_locks
from pathlib import Path
import pytest


def fixture(text='12.34'):
    def anchored(a,b,box=None):
        x={'layout':{'textAnchor':{'textSegments':[{'startIndex':str(a),'endIndex':str(b)}]}}}
        if box:x['layout']['boundingPoly']={'vertices':[{'x':box[0],'y':box[1]},{'x':box[2],'y':box[3]}]}
        return x
    row=dict(text=text,label=text,docai_line_index=0,crop_bbox=[100,200,200,250])
    doc=dict(text=text+'\n',pages=[dict(lines=[anchored(0,len(text)+1)],symbols=[anchored(i,i+1,[100+10*i,210,108+10*i,230]) for i,c in enumerate(text) if not c.isspace()])])
    return row,doc


def test_exact_transform():
    r,d=fixture();g=locate_slot(r,dict(start=2,end=3,glyph='.',boundary=None),d)
    assert g['geom_status']=='ok';assert g['left_digit']==[10,10,18,30];assert g['gap']==[18,30]
    assert g['zoom_bbox']==[4,4,44,36]


@pytest.mark.parametrize('side,start,end', [('left',0,0),('right',5,5)])
def test_boundary(side,start,end):
    r,d=fixture();g=locate_slot(r,dict(start=start,end=end,glyph='',boundary=side),d)
    assert g['geom_status']=='ok';assert g['gap_width']>=0


def test_no_symbols():
    r,d=fixture();d['pages'][0]['symbols']=[]
    assert locate_slot(r,dict(start=2,end=3,glyph='.'),d)['geom_status']=='no_symbols'


def test_misaligned():
    r,d=fixture();r['label']='12,34'
    assert locate_slot(r,dict(start=2,end=3,glyph=','),d)['geom_status']=='misaligned'


def test_wrong_slot():
    r,d=fixture()
    assert locate_slot(r,dict(start=2,end=3,glyph=','),d)['geom_status']=='misaligned'


def test_reserved_refused():
    locks=load_locks(Path(__file__).resolve().parents[1]/'artifacts/n1')
    with pytest.raises(ValueError):locks.assert_fit_rows([next(iter(locks.reserved_line_ids))])
