"""CP-H1 pixel regressions; all inputs are inside the repository."""
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np
from PIL import Image
import pytest

from greekocr.harvest.core import bbox, column_bands, crop_gate, list_return, page_gate, split_columns
from greekocr.harvest.pipeline import inspect_straight_crop, neighbour_ink, polygon_crop, straighten_candidate
from greekocr.harvest.readers import Readers, split_montage

ROOT=Path(__file__).parent/'fixtures/harvest_fix1'
MANIFEST=json.loads((ROOT/'manifest.json').read_text())
CROSS=[c for c in MANIFEST['cases'] if c['kind']=='cross_column']


def test_harvest_fixture_custody():
    for name,digest in MANIFEST['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest


@pytest.mark.parametrize('case',CROSS,ids=[c['id'] for c in CROSS])
def test_harvest_reviewer_columns_split_before_gating(case):
    with Image.open(ROOT/case['page']) as im:
        pg=page_gate(np.asarray(im),case['items'])
        assert pg['accepted'] and np.allclose(pg['column_bands'],case['expected_column_bands'],atol=.1)
        original=crop_gate(bbox(case['target_polygon']),[bbox(q['polygon']) for q in case['items']],pg,im.size,long_complete=True)
        assert not original['accepted'] and 'crosses_column' in original['flags']
        pieces=split_columns([dict(polygon=case['target_polygon'])],pg['column_bands'],np.asarray(im))
        assert len(pieces)==2
        for piece,expected in zip(pieces,case['expected_split_polygons']):
            assert np.allclose(piece['polygon'],expected)
            assert piece['harvest_parent_polygon']==case['target_polygon']
            gate=crop_gate(bbox(piece['polygon']),[bbox(q['polygon']) for q in pieces],pg,im.size,piece,long_complete=True)
            assert gate['accepted']
            assert 'crosses_column' not in gate['flags']
        original_ink=(np.asarray(polygon_crop(im,case['target_polygon']))<200).sum()
        split_ink=sum((np.asarray(polygon_crop(im,q['polygon'],parent_polygon=q['harvest_parent_polygon']))<200).sum() for q in pieces)
        assert split_ink==original_ink
        for reader_pieces in case['reader_pieces'].values():
            result=list_return(reader_pieces,column_bands=pg['column_bands'],x_offset=bbox(case['target_polygon'])[0])
            assert result['rejected'] and 'crosses_column' in result['flags']
            assert not result['text']


@pytest.mark.parametrize('fraction,expected',[(.15,False),(.15001,True)])
def test_harvest_cross_column_strict_threshold(fraction,expected):
    pg=dict(accepted=True,flags=[],body_pitch=40,column_bands=[[10,110],[150,250]])
    box=[10,100,150+100*fraction,120]
    gate=crop_gate(box,[box],pg,(300,500))
    assert ('crosses_column' in gate['flags'])==expected


def test_harvest_join_never_bridges_even_small_column_pieces():
    pieces=[dict(text='καὶ',bbox=[0,0,10,20]),dict(text='und',bbox=[150,0,160,20])]
    bands=[[0,100],[150,250]]
    assert list_return(pieces,column_bands=bands)['rejected']
    mapping=[dict(id='a',bbox=[0,0,200,20])]
    result=split_montage(pieces,mapping,column_context={'a':dict(column_bands=bands)})
    assert result['a']['flags']==['crosses_column']


def test_harvest_tiny_second_band_is_split_and_gated():
    pg=dict(accepted=True,flags=[],body_pitch=30,column_bands=[[10,110],[150,250]])
    item=dict(polygon=[[10,100],[155,100],[155,120],[10,120]])
    pieces=split_columns([item],pg['column_bands'])
    assert len(pieces)==2
    sliver=crop_gate(bbox(pieces[1]['polygon']),[bbox(q['polygon']) for q in pieces],pg,(300,500),long_complete=True)
    assert not sliver['accepted']


def test_harvest_box_clusters_ignore_minority_fused_rows():
    boxes=[[x,y,x+200,y+18] for x in (30,350) for y in range(100,800,40)]
    boxes.extend([[30,y,550,y+18] for y in (200,400,600)])
    assert column_bands(boxes,600)==[[30,230],[350,550]]


def test_harvest_duplicate_row_cannot_invent_page_gutter():
    gray=np.full((900,600),255,np.uint8)
    gray[100:112,30:230]=0;gray[100:112,350:550]=0
    boxes=[[30,98,550,118]]*10
    assert len(column_bands(boxes,600,gray))==1


def test_harvest_column_split_does_not_accept_a_cut_letter():
    gray=np.full((300,300),255,np.uint8);gray[100:120,10:250]=0
    pg=dict(accepted=True,flags=[],body_pitch=30,column_bands=[[10,110],[150,250]])
    item=dict(polygon=[[10,100],[250,100],[250,120],[10,120]])
    pieces=split_columns([item],pg['column_bands'],gray)
    assert len(pieces)==2 and all(q['harvest_split_cuts_ink'] for q in pieces)
    assert all('column_split_cuts_ink' in crop_gate(bbox(q['polygon']),[],pg,(300,300),q)['flags'] for q in pieces)


def test_harvest_legacy_gate_cache_cannot_reach_readers(tmp_path,monkeypatch):
    from greekocr.harvest import pipeline
    row=dict(id='legacy',source='Anemi',sampled=True,gates={'accepted':True,'flags':[]})
    monkeypatch.setattr(pipeline,'collect',lambda out:([],[row]))
    (tmp_path/'sampling.json').write_text(json.dumps({'ids':['legacy']}))
    def forbidden(*args,**kwargs): raise AssertionError('legacy gates constructed a reader')
    monkeypatch.setattr(Readers,'__init__',forbidden)
    with pytest.raises(ValueError,match='predates H1-fix1'):
        pipeline.label(tmp_path)


def test_harvest_reviewer_neighbour_sliver_pre_reader(tmp_path,monkeypatch):
    case=next(c for c in MANIFEST['cases'] if c['kind']=='neighbour_sliver')
    def forbidden(*args,**kwargs): raise AssertionError('reader called during geometry gate')
    monkeypatch.setattr(Readers,'pair',forbidden)
    r=dict(id=case['id'],page_id='fixture',polygon=case['target_polygon'],bbox=bbox(case['target_polygon']),
           provenance={'page_image':str(ROOT/case['page'])},gates={'flags':[],'accepted':True},features={},tier='unread',label=None)
    assert not straighten_candidate(r,tmp_path)
    assert 'neighbour_sliver' in r['gates']['flags']
    measured=r['gates']['neighbour_sliver']['above']
    assert measured['height_fraction']==pytest.approx(5/32)
    assert measured['x_span_fraction']==pytest.approx(572/796)
    assert measured['ink_pixels']==158
    assert r['tier']=='rejected' and r['label'] is None


def test_harvest_clean_polytonic_keeps_own_marks():
    with Image.open(ROOT/'clean_polytonic.raw.png') as raw:
        result=inspect_straight_crop(raw)
    assert not result['flags']
    assert not result['neighbour_sliver']['rejected']


@pytest.mark.parametrize('side', ['above','below'])
@pytest.mark.parametrize('height,span,rejected',[(12,30,False),(13,10,True),(1,31,True)])
def test_harvest_neighbour_pixel_fraction_thresholds(monkeypatch,side,height,span,rejected):
    from greekocr.glyphs import components
    labels=np.zeros((100,100),np.int32)
    start=0 if side=='above' else 100-height
    # Count ink rows rather than the component's larger bounding rectangle.
    labels[start:start+height,:span]=1
    g=SimpleNamespace(labels=labels,ink=labels>0,width=100,height=100,
        components=[SimpleNamespace(index=1,role='neighbour',rel_cy=-2 if side=='above' else 2)],
        band=SimpleNamespace(top=np.full(100,40),bottom=np.full(100,60)))
    monkeypatch.setattr(components,'line_glyphs',lambda *args,**kwargs:g)
    result=neighbour_ink(SimpleNamespace(image=None,xh=20,baseline_row=60))
    assert result[side]['height_fraction']==height/100
    assert result[side]['x_span_fraction']==span/100
    assert result['rejected']==rejected


def test_harvest_reviewer_border_is_prose():
    case=next(c for c in MANIFEST['cases'] if c['kind']=='page_border')
    with Image.open(ROOT/case['page']) as im:
        pg=page_gate(np.asarray(im),case['items'])
        assert pg['rule_counts']['horizontal']>=3 and pg['rule_counts']['vertical']>=2
        assert not pg['box_lattice'] and 'table' not in pg['flags']
        gate=crop_gate(bbox(case['target_polygon']),[bbox(q['polygon']) for q in case['items']],pg,im.size,long_complete=True)
        assert pg['accepted'] and gate['accepted']


def test_harvest_offline_replay_preserves_sources_and_sample_labels(tmp_path,monkeypatch):
    from greekocr.harvest.regate import run
    from greekocr.harvest.pipeline import FrozenStack
    case=CROSS[0];bulk=tmp_path/'bulk';(bulk/'pages').mkdir(parents=True)
    shutil.copyfile(ROOT/case['page'],bulk/'pages'/case['page'])
    rows=[dict(id=str(i),page_id='p',polygon=q['polygon'],bbox=bbox(q['polygon']),
        provenance={'page_image':'docs/harvest/pages/'+case['page']},gates={'accepted':True,'flags':[]},
        features={},tier='tier1',label='unchanged',sampled=q['polygon']==case['target_polygon'])
        for i,q in enumerate(case['items'])]
    records=bulk/'records.jsonl';records.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    receipts=bulk/'page_gates.json';receipts.write_text(json.dumps([dict(id='p',bend_scout=[],page_gate={})]))
    hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (records,receipts,bulk/'pages'/case['page'])]
    def forbidden(*args,**kwargs): raise AssertionError('offline replay ran stack or readers')
    monkeypatch.setattr(Readers,'__init__',forbidden);monkeypatch.setattr(FrozenStack,'run',forbidden)
    summary=run(records,receipts,bulk,tmp_path/'out',progress=None)
    assert summary['records']==len(rows) and summary['sampled_now_rejected']==1
    assert summary['google_calls']==0 and summary['no_detector_run']
    assert hashes==[hashlib.sha256(p.read_bytes()).hexdigest() for p in (records,receipts,bulk/'pages'/case['page'])]
    sidecar=json.loads((tmp_path/'out/sampled_post_fix1_gate.json').read_text())[0]
    assert 'crosses_column' in sidecar['post_fix1_gate']['flags']
    assert len(sidecar['split_candidates'])==2
    assert all(p['label'] is None for p in sidecar['split_candidates'])
    assert all(r['tier']=='tier1' and r['label']=='unchanged' for r in [json.loads(s) for s in records.read_text().splitlines()])
    with pytest.raises(ValueError,match='protected'):
        run(records,receipts,bulk,bulk/'new',progress=None)


def test_harvest_bulk_root_mapping_and_escape(tmp_path):
    from greekocr.harvest.regate import resolve_artifact
    (tmp_path/'pages').mkdir();p=tmp_path/'pages/p.png';p.write_bytes(b'fixture')
    assert resolve_artifact('/old/repo/docs/harvest/pages/p.png',tmp_path)==p
    with pytest.raises(ValueError,match='escapes'):
        resolve_artifact('docs/harvest/../escape.png',tmp_path)
    with pytest.raises(FileNotFoundError):
        resolve_artifact('docs/harvest/pages/missing.png',tmp_path)


def test_harvest_extraction_gates_column_pieces_not_fused_parent(tmp_path,monkeypatch):
    from greekocr.harvest import pipeline
    case=CROSS[0]
    with Image.open(ROOT/case['page']) as source: image=source.copy()
    class Bitmap:
        def to_pil(self): return image
        def close(self): pass
    class Page:
        def render(self,**kwargs): return Bitmap()
        def close(self): pass
    class Document:
        def __init__(self,*args): pass
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def __getitem__(self,index): return Page()
    monkeypatch.setattr(pipeline.pdfium,'PdfDocument',Document)
    gated=[];actual_gate=pipeline.crop_gate
    def capture(box,*args,**kwargs):
        gated.append(box);return actual_gate(box,*args,**kwargs)
    monkeypatch.setattr(pipeline,'crop_gate',capture)
    pdf=tmp_path/'source.pdf';pdf.write_bytes(b'offline render stub')
    stack=SimpleNamespace(model_sha256='a'*64,source_sha256='b'*64,
        run=lambda *args:dict(items=case['items'],harvest_bend=[],stages={},timing={}))
    inp=dict(id='p',pdf=str(pdf),pdf_page_index=0,book='b',year=1887,decade=1880,page=23,
        source_url='fixture',catalogue={},rights='internal',fetch_receipt={})
    receipt,records=pipeline.extract_page(inp,stack,tmp_path/'artifacts',tmp_path)
    assert bbox(case['target_polygon']) not in gated
    target=[r for r in records if r.get('pre_split_polygon')==case['target_polygon']]
    assert len(target)==2 and {r['id'] for r in target}=={'p-l0038-c1','p-l0038-c2'}
    assert all(r['gates']['accepted'] and r['label'] is None and r['tier']=='unread' for r in target)
    assert all(r['gates']['column_bands']==receipt['page_gate']['column_bands'] for r in target)
