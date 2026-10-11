import copy, json, math, importlib.util, sys
from pathlib import Path
import pytest
import numpy as np
from PIL import Image
from greekocr.harvest.core import *
from greekocr.harvest.readers import Budget, BudgetExceeded, montage, split_montage, response_pieces
from greekocr.harvest.pipeline import balanced_sample, match_layer


def rect(x,y,w,h): return [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]
def body():
    a=np.full((900,600),255,np.uint8); items=[]
    for y in range(100,800,40):
        for x in range(80,510,12): a[y:y+12,x:x+6]=30
        items.append({'polygon':rect(75,y-2,440,18)})
    return a,items

def piece(t,b): return dict(text=t,bbox=b,confidence=.9)

@pytest.mark.parametrize('a,b', [('καὶ ἐγώ','και\u0300 ἐγώ'),(' α  β\n','α β'),('','')])
def test_normalisation(a,b): assert normalise(a)==normalise(b)

@pytest.mark.parametrize('a,b,layer,expected',[
 ('λόγος','λόγος',None,'tier1'),('καὶ ἐγώ','κὶ ἐγώ',None,'tier1'),
 ('καὶ','κὰ',None,'tier1'),('καὶ','κὴ',None,'tier1'),('χείρισον','χείριςον',None,'tier1'),
 ('λόγος','λόχος',None,'tier2'),('πολύ διαφορετικό','ἀλλο',None,'tier3'),
 ('πολύ διαφορετικό','ἀλλο','ἀλλο','tier2'),('','κείμενο',None,'rejected'),('','',None,'rejected'),
 ('στρατός','σρατός',None,'tier2'),('διαφορετικό καὶ','ἄλλο κὶ',None,'tier3')])
def test_tiering(a,b,layer,expected):
    r=tier(a,b,layer); assert r['tier']==expected
    assert (r['label'] is not None)==(expected in ('tier1','tier2'))
    if 'κὶ' in b and expected=='tier1': assert 'rare_glyph_substitution' in r['tags']

@pytest.mark.parametrize('a,b,d',[('','abc',3),('abc','abc',0),('αβ','αγ',1),('abc','ac',1),('ab','ba',2)])
def test_edit_distance(a,b,d): assert edits(a,b)==d

def test_list_horizontal():
    r=list_return([piece('δεύτερο',[90,3,160,20]),piece('πρώτο',[0,0,80,18])]); assert not r['rejected'];assert r['text']=='πρώτο δεύτερο'

def test_list_stacked(): assert list_return([piece('αβ',[0,0,40,18]),piece('γδ',[0,25,40,43])])['rejected']
def test_list_internal_foreign_obstruction():
    r=list_return([piece('καὶ',[0,0,20,20]),piece('λόγος',[70,0,110,20]),piece('ЯЖ',[35,0,50,20])]);assert 'obstructed' in r['flags']
def test_list_exterior_garbage_dropped():
    r=list_return([piece('καὶ λόγος',[0,30,100,50]),piece('ЯЖ',[0,0,20,15])]); assert r['text']=='καὶ λόγος';assert not r['rejected']
def test_list_empty(): assert list_return([])['rejected']
def test_list_punctuation_only(): assert list_return([piece(',,,',[0,0,10,10])])['rejected']
def test_list_latin_allowed(): assert not list_return([piece('Greek',[0,0,80,20])])['rejected']

def test_body_page():
    a,i=body(); r=page_gate(a,i);assert r['accepted'];assert r['body_pitch']==40;assert len(r['column_bands'])==1

def test_table_rules():
    a,i=body()
    for y in (200,400,600):a[y:y+2,50:550]=0
    for x in (100,300,500):a[150:750,x:x+2]=0
    assert 'table' in page_gate(a,i)['flags']

@pytest.mark.parametrize('angle',[8,15,90])
def test_rotation(angle):
    a,i=body(); theta=math.radians(angle);rot=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
    for q in i:q['polygon']=(np.asarray(q['polygon'])@rot.T).tolist()
    assert 'rotated' in page_gate(a,i)['flags']

def test_bend_page():
    a,i=body();assert 'bend_scout' in page_gate(a,i,bend_fired=True)['flags']

def test_two_columns():
    a=np.full((900,600),255,np.uint8);i=[dict(polygon=rect(x,y,200,18)) for x in (30,350) for y in range(100,800,40)]
    r=page_gate(a,i);assert len(r['column_bands'])==2;assert r['accepted']

@pytest.mark.parametrize('box,reason', [([75,100,515,170],'height_over_body_pitch'),([1,100,515,118],'page_edge_touch'),([75,100,82,118],'ornament_or_short_fragment'),([0,100,590,118],'outside_column_band')])
def test_crop_gates(box,reason):
    a,i=body(); pg=page_gate(a,i); r=crop_gate(box,[bbox(q['polygon']) for q in i],pg,(600,900));assert reason in r['flags']

def sample_record():
    return dict(schema=SCHEMA,id='r1',source='Vouli',book='b',decade=1850,page=1,page_id='p1',provenance={'pdf_sha256':'a'*64},stack_commit=STACK_COMMIT,
                polygon=rect(0,0,100,20),bbox=[0,0,100,20],gates={'accepted':True},features={},readers={},tier='unread',label=None,raw_crop='r.png',straight_crop='s.png')
def test_record_schema(): assert validate_record(sample_record())
@pytest.mark.parametrize('field',['source','book','provenance','polygon','gates','readers','stack_commit'])
def test_missing_schema(field):
    r=sample_record();r.pop(field)
    with pytest.raises(ValueError):validate_record(r)
def test_rejected_record_no_label():
    r=sample_record();r.update(tier='rejected',label='foo')
    with pytest.raises(ValueError):validate_record(r)
def test_gated_record_no_label():
    r=sample_record();r.update(tier='tier1',label='foo');r['gates']['accepted']=False
    with pytest.raises(ValueError):validate_record(r)

def test_montage_separator_and_map(tmp_path):
    rs=[]
    for i,h in enumerate([15,30]):
        p=tmp_path/f'{i}.png';Image.new('L',(100,h),0).save(p);rs.append(dict(id=str(i),straight_crop=str(p)))
    path=tmp_path/'montage.png'; mapping=montage(rs,path)
    with Image.open(path) as im:
        a=np.asarray(im); assert np.all(a[mapping[0]['bbox'][3]:mapping[1]['bbox'][1]]==255);assert mapping[1]['bbox'][1]-mapping[0]['bbox'][3]==24
    assert json.loads(path.with_suffix('.map.json').read_text())==mapping

def test_cross_crop_montage_box():
    mapping=[dict(id='a',bbox=[0,0,100,20]),dict(id='b',bbox=[0,44,100,64])]
    r=split_montage([piece('ἀβ',[0,0,100,64])],mapping)
    assert all('montage_cross_crop_box' in v['flags'] for v in r.values())

def test_docai_geometry():
    raw={'document':{'text':'λόγος','pages':[{'lines':[{'layout':{'textAnchor':{'textSegments':[{'endIndex':'5'}]},'confidence':.8,'boundingPoly':{'normalizedVertices':[{'x':.1,'y':.2},{'x':.9,'y':.8}]}}}]}]}}
    p=response_pieces('docai',raw,(100,50)); assert p[0]['bbox']==[10,10,90,40];assert p[0]['text']=='λόγος'

def test_budget_survives_restart_and_caps(tmp_path):
    b=Budget(tmp_path/'budget.jsonl',.003); b.reserve('vision','a'); Budget(b.path,.003).reserve('docai','b')
    with pytest.raises(BudgetExceeded):b.reserve('vision','c')
    assert b.receipt()['cost_usd']==.003

def test_stratified_sample():
    rows=[]
    for s in ('Anemi','Vouli'):
        for j in range(30):rows.append(dict(id=f'{s}{j}',source=s,decade=1900,features={'length_stratum':'full_width','readability_stratum':'normal'}))
    chosen=balanced_sample(rows,10);assert sum(r['source']=='Vouli' for r in chosen)==5;assert len({r['id'] for r in chosen})==10
    assert chosen[0]['sampling']['inclusion_probability']==5/30

def test_weak_layer_sixty_percent():
    rows=[{'bbox':[0,0,100,12],'text':'ok'}]
    assert match_layer([0,0,100,20],rows)['text']=='ok';assert match_layer([0,0,100,21],rows) is None

@pytest.fixture
def fetcher():
    root=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/scripts/fetch');sys.path.insert(0,str(root))
    spec=importlib.util.spec_from_file_location('t13_anemi_fetch',Path('docs/harvest/pilot/_fetch/o4b_anemi_pages.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

@pytest.mark.parametrize('sizes,n,expected', [([100],15,[list(range(42,57))]),([10,20],15,[list(range(7,10)),list(range(12))]),([5],15,[list(range(5))])])
def test_fetch_middle_pages(fetcher,sizes,n,expected):
    r={'volumes':[{'volume_id':str(i),'pages':s} for i,s in enumerate(sizes)]};assert list(fetcher.selected_indices(r,f'middle:{n}').values())==expected
@pytest.mark.parametrize('value',['middle:0','middle:-1','end:15','middle:x'])
def test_fetch_bad_range(fetcher,value):
    with pytest.raises(ValueError):fetcher.selected_indices({'volumes':[{'volume_id':'v','pages':30}]},value)
def test_fetch_selection_order(fetcher,tmp_path):
    p=tmp_path/'records.json';p.write_text(json.dumps([{'document_id':'b'},'a']))
    r=fetcher.select_records([{'record_id':'a'},{'record_id':'b'}],p);assert [x['record_id'] for x in r]==['b','a']
def test_fetch_duplicate_selection(fetcher,tmp_path):
    p=tmp_path/'records.json';p.write_text('["a","a"]')
    with pytest.raises(ValueError):fetcher.select_records([{'record_id':'a'}],p)

def test_budget_parallel_reservations(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    b=Budget(tmp_path/'budget.jsonl',.015)
    def attempt(i):
        try:b.reserve('vision',str(i));return True
        except BudgetExceeded:return False
    with ThreadPoolExecutor(max_workers=8) as pool:r=list(pool.map(attempt,range(20)))
    assert sum(r)==10;assert b.receipt()['cost_usd']==.015

def test_no_general_sigma_or_accent_folding():
    r=tier('διαφορετικὸς λόγος','διαφορετικός λογος')
    assert 'rare_glyph_substitution' not in r['tags']

def test_qualification_fails_on_one_reader_crop(tmp_path):
    from greekocr.harvest.readers import Readers
    reader=object.__new__(Readers);reader.root=tmp_path
    records=[dict(id=str(i)) for i in range(50)]
    def single(r):return {e:{'text':'αβ','rejected':False,'status':'ok','flags':[]} for e in ('vision','docai')}
    def batch(rows):
        result={r['id']:single(r) for r in rows}
        if '3' in result:result['3']['docai']['text']='αγ'
        return result
    reader.single=single;reader.batch=batch
    q,s=reader.qualify(records);assert not q['qualified'];assert q['matched']==99;assert len(s)==50


def test_qualification_requires_fifty(tmp_path):
    from greekocr.harvest.readers import Readers
    reader=object.__new__(Readers);reader.root=tmp_path
    with pytest.raises(ValueError):reader.qualify([])

def test_more_than_two_columns_rejected():
    a=np.full((900,900),255,np.uint8);items=[dict(polygon=rect(x,y,200,18)) for x in (30,330,630) for y in range(100,800,40)]
    assert 'more_than_two_columns' in page_gate(a,items)['flags']

@pytest.mark.parametrize('width,accepted',[(351,False),(352,True),(440,True)])
def test_long_complete_width_gate(width,accepted):
    a,i=body(); pg=page_gate(a,i)
    box=[75,300,75+width,318]
    gate=crop_gate(box,[bbox(q['polygon']) for q in i],pg,(600,900),long_complete=True)
    assert gate['accepted']==accepted
    assert gate['width_band_ratio']==pytest.approx(width/440)

def test_short_paragraph_last_is_excluded():
    a,i=body();pg=page_gate(a,i)
    b=[75,780,300,798]
    assert 'short_paragraph_boundary' in crop_gate(b,[bbox(q['polygon']) for q in i],pg,(600,900),long_complete=True)['flags']

def test_column_gutter_touch_excluded():
    pg=dict(accepted=True,flags=[],body_pitch=30,column_bands=[[30,270],[330,570]])
    b=[30,100,300,118]
    gate=crop_gate(b,[b],pg,(600,900),long_complete=True)
    assert not gate['accepted']

def test_budget_one_thousand_call_ceiling(tmp_path):
    b=Budget(tmp_path/'budget.jsonl',3)
    b.state.write_text('{"calls":1000}')
    with pytest.raises(BudgetExceeded): b.reserve('vision','next')

def test_budget_rejects_oversized_task_cap(tmp_path):
    with pytest.raises(ValueError): Budget(tmp_path/'budget.jsonl',3.01)

def test_sample_schema_rejects_vouli():
    r=sample_record();r['sampled']=True
    with pytest.raises(ValueError):validate_record(r)

def test_rare_substitution_accented_observed_pair():
    assert tier('χείρισὸν','χείριςον')['tags']==['rare_glyph_substitution']

def test_substitution_does_not_match_embedded_word():
    assert 'rare_glyph_substitution' not in tier('ἀκαὶ β','ἀκὶ β')['tags']

def test_sampling_interleaves_pages_without_api_calls():
    from greekocr.harvest.pipeline import sample_order
    rs=[]
    for p in ('a','b'):
        for i in range(4):rs.append(dict(id=p+str(i),page_id=p,gates={'paragraph_position':'interior'},features={'width_band_ratio':.9+i*.01}))
    chosen=sample_order(rs)
    assert [r['page_id'] for r in chosen[:4]]==['a','b','a','b']

@pytest.mark.parametrize('sizes,expected',[([100],[[49,50]]),([1,3],[[],[0,1]]),([2,2],[[1],[0]])])
def test_fetch_exact_two_middle_pages(fetcher,sizes,expected):
    r={'volumes':[{'volume_id':str(i),'pages':n} for i,n in enumerate(sizes)]}
    assert list(fetcher.selected_indices(r,'middle:2').values())==expected

def test_frozen_sample_represents_all_eligible_books_and_caps_four(tmp_path,monkeypatch):
    from greekocr.harvest import pipeline
    pages=[];records=[]
    for b in range(150):
        for page in range(2):
            pid=f'b{b}-p{page}'
            pages.append(dict(id=pid,book=str(b),decade=1860+b%8*10,timing={'straighten_s':0.,'total_cpu_s':0.}))
            for j in range(10):
                r=sample_record();r.update(id=pid+f'-l{j}',page_id=pid,source='Anemi',book=str(b),decade=1860+b%8*10,text_layer=None,sampled=False)
                r['gates'].update(width_band_ratio=.95,paragraph_position='interior',flags=[])
                r['features'].update(width_band_ratio=.95)
                records.append(r)
    monkeypatch.setattr(pipeline,'collect',lambda out:(pages,records))
    monkeypatch.setattr(pipeline,'persist',lambda *args:None)
    monkeypatch.setattr(pipeline,'straighten_candidate',lambda r,big:r.update(straighten={}) or True)
    chosen=pipeline.sample(tmp_path,tmp_path,500)
    counts=Counter(r['book'] for r in chosen)
    assert len(chosen)==500 and len(counts)==150
    assert set(counts.values())=={3,4}
    assert len({r['decade'] for r in chosen})==8
    assert all(r['source']=='Anemi' for r in chosen)
    assert json.loads((tmp_path/'sampling.json').read_text())['selection_frozen_before_calls']
    assert [r['id'] for r in pipeline.sample(tmp_path,tmp_path,500)]==[r['id'] for r in records if r['sampled']]

def test_no_recall_for_interrupted_reserved_attempt(tmp_path):
    from greekocr.harvest.readers import Readers
    reader=Readers.__new__(Readers);reader.root=tmp_path;reader.budget=Budget(tmp_path/'budget.jsonl',3)
    image=tmp_path/'crop.png';Image.new('L',(100,20),255).save(image)
    import hashlib
    key=hashlib.sha256(image.read_bytes()).hexdigest();reader.budget.reserve('docai',key)
    result=reader.call('docai',image)
    assert result['error_class']=='InterruptedReservedAttempt'
    assert reader.budget.receipt()['calls_reserved']==1

def test_body_font_excludes_small_furniture():
    records=[]
    for xh in (10,20,20,20):
        records.append(dict(gates={'accepted':True,'column':0,'flags':[]},features={'x_height_estimate':xh},tier='unread',label=None))
    pg={'column_bands':[[0,100]]};body_font_gate(records,pg)
    assert records[0]['gates']['flags']==['small_type_furniture']
    assert all(r['gates']['accepted'] for r in records[1:])

def test_short_indented_first_line_excluded_even_at_eighty_percent():
    a,i=body();pg=page_gate(a,i)
    b=[125,300,500,318]
    assert 'short_paragraph_boundary' in crop_gate(b,[bbox(q['polygon']) for q in i],pg,(600,900),long_complete=True)['flags']

@pytest.mark.parametrize('field,value',[('bbox',[1,1,1,2]),('polygon',[[0,0],[1,1]]),('bbox',[0,0,float('nan'),1]),('readers',[]),('provenance',{'pdf_sha256':'x'})])
def test_schema_rejects_malformed_geometry_and_hash(field,value):
    r=sample_record();r[field]=value
    with pytest.raises(ValueError):validate_record(r)

def test_table_lattice_without_rules():
    a=np.full((900,600),255,np.uint8)
    items=[dict(polygon=rect(x,y,55,15)) for y in range(100,700,40) for x in (50,170,300,430)]
    assert 'table' in page_gate(a,items)['flags']

def test_neighbour_height_gate():
    a,i=body();pg=page_gate(a,i)
    b=[75,300,515,342];near=[[75,260,515,278],[75,345,515,363]]
    assert 'taller_than_neighbours' in crop_gate(b,near,pg,(600,900))['flags']
