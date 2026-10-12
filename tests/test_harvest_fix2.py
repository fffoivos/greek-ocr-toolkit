"""Offline ownership, local-column and ruled-cell regressions from CP-H1."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image
import pytest

from greekocr.harvest.core import bbox, crop_gate, page_gate, split_columns
from greekocr.harvest.pipeline import inspect_straight_crop, neighbour_ink, polygon_crop

ROOT=Path(__file__).parent/'fixtures/harvest_fix2'
MANIFEST=json.loads((ROOT/'manifest.json').read_text())


def test_harvest_fix2_fixture_custody():
    for name,digest in MANIFEST['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest


@pytest.mark.parametrize('case',[c for c in MANIFEST['cases'] if 'crop' in c],ids=lambda c:c['id'])
def test_harvest_fix2_clean_own_marks_and_scan_grain_pass(case):
    with Image.open(ROOT/case['crop']) as raw: result=inspect_straight_crop(raw)
    assert not result['flags']
    assert not result['neighbour_sliver']['rejected']
    assert result['neighbour_sliver']['own_zone']['padding_xh']==.15


def test_harvest_fix2_upper_prose_intact_lower_glossary_split():
    case=next(c for c in MANIFEST['cases'] if c['kind']=='mixed_regions')
    with Image.open(ROOT/case['page']) as im:
        pg=page_gate(np.asarray(im),case['items'])
        assert pg['accepted']
        split=split_columns(case['items'],pg,np.asarray(im));boxes=[bbox(q['polygon']) for q in split]
        for number in range(30,38):
            target=next(q for q in case['items'] if q['id'].endswith(f'l{number:04d}'))
            pieces=[p for p in split if p['id']==target['id']]
            assert len(pieces)==1 and pieces[0]['polygon']==target['polygon']
            gate=crop_gate(bbox(target['polygon']),boxes,pg,im.size,long_complete=True)
            assert gate['accepted'], (number,gate)
            assert len(gate['column_bands'])==1
        for number in (5,8,14,16):
            target=next(q for q in case['items'] if q['id'].endswith(f'l{number:04d}'))
            pieces=[p for p in split if p['id']==target['id']]
            assert len(pieces)==2
            gate=crop_gate(bbox(target['polygon']),boxes,pg,im.size,long_complete=True)
            assert 'crosses_column' in gate['flags'] and len(gate['column_bands'])==2
            original=(np.asarray(polygon_crop(im,target['polygon']))<200).sum()
            recovered=sum((np.asarray(polygon_crop(im,p['polygon'],parent_polygon=p['harvest_parent_polygon']))<200).sum() for p in pieces)
            assert recovered==original
            assert not any(p['harvest_split_cuts_ink'] for p in pieces)
            for piece in pieces:
                g=crop_gate(bbox(piece['polygon']),boxes,pg,im.size,piece,long_complete=True)
                assert 'crosses_column' not in g['flags']
        # Centred prose immediately above the glossary is not a partial entry.
        for number in (18,19,20):
            target=next(q for q in case['items'] if q['id'].endswith(f'l{number:04d}'))
            assert len([p for p in split if p['id']==target['id']])==1


def test_harvest_fix2_catalogue_has_no_invented_columns():
    case=next(c for c in MANIFEST['cases'] if c['kind']=='catalogue')
    with Image.open(ROOT/case['page']) as im:
        pg=page_gate(np.asarray(im),case['items'])
        assert not any(len(r['column_bands'])>1 for r in pg['column_regions'])
        pieces=split_columns(case['items'],pg,np.asarray(im))
        assert len(pieces)==len(case['items'])
        for number in (26,27):
            target=next(q for q in case['items'] if q['id'].endswith(f'l{number:04d}'))
            gate=crop_gate(bbox(target['polygon']),[bbox(p['polygon']) for p in pieces],pg,im.size,long_complete=True)
            assert gate['accepted']


def test_harvest_fix2_facing_pages_keep_short_continuations_in_their_columns():
    case=next(c for c in MANIFEST['cases'] if c['kind']=='facing_pages_short_rows')
    with Image.open(ROOT/case['page']) as im:
        pg=page_gate(np.asarray(im),case['items'])
        pieces=split_columns(case['items'],pg,np.asarray(im));boxes=[bbox(q['polygon']) for q in pieces]
        for number in (4,6,19,21,25):
            target=next(q for q in case['items'] if q['id'].endswith(f'l{number:04d}'))
            gate=crop_gate(bbox(target['polygon']),boxes,pg,im.size,long_complete=True)
            assert gate['accepted'] and len(gate['column_bands'])==2


@pytest.mark.parametrize('kind,numbers',[('poem_blocks',(2,4)),('prose_and_illustration',(12,))])
def test_harvest_fix2_separate_blocks_and_non_row_shapes_do_not_widen_bands(kind,numbers):
    case=next(c for c in MANIFEST['cases'] if c['kind']==kind)
    with Image.open(ROOT/case['page']) as im:
        pg=page_gate(np.asarray(im),case['items'])
        pieces=split_columns(case['items'],pg,np.asarray(im));boxes=[bbox(q['polygon']) for q in pieces]
        for number in numbers:
            target=next(q for q in case['items'] if q['id'].endswith(f'l{number:04d}'))
            gate=crop_gate(bbox(target['polygon']),boxes,pg,im.size,long_complete=True)
            assert gate['accepted']
            assert len([p for p in pieces if p['id']==target['id']])==1


def test_harvest_fix2_reviewer_table_is_excluded():
    case=next(c for c in MANIFEST['cases'] if c['kind']=='ruled_table')
    with Image.open(ROOT/case['page']) as im: pg=page_gate(np.asarray(im),case['items'])
    assert not pg['accepted'] and 'table' in pg['flags']
    assert pg['ruled_cells']['closed_cells']>=2


@pytest.mark.parametrize('cells,table',[(1,False),(2,True),(3,True)])
def test_harvest_fix2_closed_cells_do_not_need_lattice(cells,table):
    gray=np.full((600,800),255,np.uint8)
    gray[180:183,100:601]=0;gray[330:333,100:601]=0
    for x in np.linspace(100,600,cells+1).astype(int): gray[180:333,x:x+3]=0
    items=[dict(polygon=[[50,y],[740,y],[740,y+20],[50,y+20]]) for y in range(30,170,20)]
    pg=page_gate(gray,items)
    assert not pg['box_lattice']
    assert ('table' in pg['flags'])==table


@pytest.mark.parametrize('centroid_outside,overlap,expected',[(True,.25,True),(True,.26,False),(False,.25,False),(True,0,False)])
def test_harvest_fix2_component_centroid_and_extent_ownership(monkeypatch,centroid_outside,overlap,expected):
    from greekocr.glyphs import components, page_font
    labels=np.zeros((100,100),np.int32)
    # Zone starts at y=37; a 20px component overlaps by 5px at the boundary.
    y1=37+20*overlap;y0=y1-20
    start=int(np.floor(y0));stop=int(np.ceil(y1))
    labels[start:stop,20:25]=1
    if not centroid_outside:
        labels[:]=0;labels[37:stop,20:25]=1
    c=SimpleNamespace(index=1,x0=20,x1=25,y0=start,y1=stop,h=stop-start,role='neighbour')
    g=SimpleNamespace(labels=labels,ink=labels>0,width=100,height=100,components=[c],
        band=SimpleNamespace(bottom=np.full(100,60.),n_support=20))
    monkeypatch.setattr(components,'line_glyphs',lambda *a,**k:g)
    def fit(p,lines):
        lines[0].accent_top=np.full(100,40.);lines[0].font_bottom=np.full(100,65.)
    monkeypatch.setattr(page_font,'fit_guides',fit)
    result=neighbour_ink(SimpleNamespace(image=None,xh=20.,baseline_row=60))
    assert result['rejected']==expected
    if expected: assert result['touches_zone'] and result['combined']['x_span_fraction']<.20


@pytest.mark.parametrize('axis',['horizontal','vertical'])
def test_harvest_fix2_large_closed_cells_are_tables(axis):
    gray=np.full((600,800),255,np.uint8)
    gray[50:53,50:750]=0;gray[547:550,50:750]=0
    gray[50:550,50:53]=0;gray[50:550,747:750]=0
    if axis=='horizontal': gray[298:301,50:750]=0
    else: gray[50:550,397:400]=0
    items=[dict(polygon=[[50,y],[740,y],[740,y+20],[50,y+20]]) for y in range(30,170,20)]
    pg=page_gate(gray,items)
    assert not pg['box_lattice']
    assert pg['ruled_cells']['closed_cells']>=2 and 'table' in pg['flags']


def test_harvest_fix2_counts_neighbour_union_on_both_sides(monkeypatch):
    from greekocr.glyphs import components, page_font
    labels=np.zeros((100,100),np.int32);labels[10:16,0:10]=1;labels[90:96,10:20]=2
    cs=[SimpleNamespace(index=i,x0=x,x1=x+10,y0=y,y1=y+6,h=6,role='neighbour') for i,x,y in [(1,0,10),(2,10,90)]]
    g=SimpleNamespace(labels=labels,ink=labels>0,width=100,height=100,components=cs,
        band=SimpleNamespace(bottom=np.full(100,60.),n_support=20))
    monkeypatch.setattr(components,'line_glyphs',lambda *a,**k:g)
    def fit(p,lines):
        lines[0].accent_top=np.full(100,40.);lines[0].font_bottom=np.full(100,65.)
    monkeypatch.setattr(page_font,'fit_guides',fit)
    result=neighbour_ink(SimpleNamespace(image=None,xh=20.,baseline_row=60))
    assert result['combined']['height_fraction']==.12
    assert result['combined']['x_span_fraction']==.20
    assert result['rejected'] and not result['touches_zone']


def test_harvest_fix2_empty_bbox_corner_does_not_touch_zone(monkeypatch):
    from greekocr.glyphs import components, page_font
    labels=np.zeros((100,100),np.int32);labels[10:12,20:25]=1
    c=SimpleNamespace(index=1,x0=20,x1=25,y0=10,y1=12,h=2,role='neighbour')
    g=SimpleNamespace(labels=labels,ink=labels>0,width=100,height=100,components=[c],
        band=SimpleNamespace(bottom=np.full(100,60.),n_support=20))
    monkeypatch.setattr(components,'line_glyphs',lambda *a,**k:g)
    def fit(p,lines):
        lines[0].accent_top=np.full(100,14.8);lines[0].font_bottom=np.full(100,65.)
    monkeypatch.setattr(page_font,'fit_guides',fit)
    result=neighbour_ink(SimpleNamespace(image=None,xh=20.,baseline_row=60))
    assert result['components'][0]['overlap_fraction']==pytest.approx(.1)
    assert not result['touches_zone'] and not result['rejected']


def test_harvest_fix2_offline_counts_tier1_and_reason_without_labels(tmp_path,monkeypatch):
    from greekocr.harvest.regate import run
    from greekocr.harvest.pipeline import FrozenStack
    from greekocr.harvest.readers import Readers
    import shutil
    case=next(c for c in MANIFEST['cases'] if c['kind']=='mixed_regions')
    bulk=tmp_path/'bulk';(bulk/'pages').mkdir(parents=True)
    shutil.copyfile(ROOT/case['page'],bulk/'pages'/case['page'])
    rows=[dict(id=q['id'],page_id='p',polygon=q['polygon'],bbox=bbox(q['polygon']),
        provenance={'page_image':'docs/harvest/pages/'+case['page']},gates={'accepted':True,'flags':[]},
        features={},tier='tier1',label='unchanged',sampled=q['id'].endswith(('l0014','l0037'))) for q in case['items']]
    records=bulk/'records.jsonl';records.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    receipts=bulk/'page_gates.json';receipts.write_text(json.dumps([dict(id='p',bend_scout=[],page_gate={})]))
    prior=tmp_path/'fix1.jsonl';prior.write_text(''.join(json.dumps(dict(id=r['id'],post_fix1_gate=dict(accepted=False,flags=['crosses_column'])))+'\n' for r in rows))
    hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (records,receipts,prior)]
    def forbidden(*a,**k): raise AssertionError('offline replay constructed readers or ran detector')
    monkeypatch.setattr(Readers,'__init__',forbidden);monkeypatch.setattr(FrozenStack,'run',forbidden)
    summary=run(records,receipts,bulk,tmp_path/'out',previous_gates=prior,progress=None)
    assert summary['sampled_now_rejected']==summary['tier1_rejected']==1
    assert summary['sampled_now_rejected_by_reason']['crosses_column']==1
    assert summary['fix1_comparison']['rejects_released']>0
    assert hashes==[hashlib.sha256(p.read_bytes()).hexdigest() for p in (records,receipts,prior)]
    sampled=json.loads((tmp_path/'out/sampled_post_fix2_gate.json').read_text())
    prose=next(r for r in sampled if r['id'].endswith('l0037'))
    assert prose['post_fix2_gate']['accepted'] and not prose['split_candidates']
    glossary=next(r for r in sampled if r['id'].endswith('l0014'))
    assert len(glossary['split_candidates'])==2 and all(p['label'] is None for p in glossary['split_candidates'])
