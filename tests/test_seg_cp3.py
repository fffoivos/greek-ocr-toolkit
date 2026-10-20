"""CP3 physical-row mechanics, not synthetic lexical truth or native recall."""
import json
from pathlib import Path
from tests._paths import run_record

import numpy as np
import pytest
from greekocr.harvest import geometry_observations as g
from greekocr.harvest.row_inclusion import supported_rows, screen_merged
from test_seg_cp2 import cached, load


def planted(specs, shape=(150, 160)):
    ink = np.zeros(shape, bool)
    labels = np.zeros(shape, np.int32)
    ownership = g.vendor_ownership()
    rows = []; structure = {}; cid = 0
    for spec in specs:
        rid, column, a, b, y, slope = spec
        x = np.arange(a,b); top = y+slope*(x-a); bottom = top+10
        ids = []
        for start in range(a,b,12):
            cid += 1; ids.append(cid)
            for xx in range(start,min(start+6,b)):
                t = int(np.ceil(top[xx-a])); bot = int(np.floor(bottom[xx-a]))
                ink[t:bot,xx] = True; labels[t:bot,xx] = cid
        r = dict(row_id=rid,column_id=column,block_id='block',x0=a,x1=b,xheight=10.,
                 component_ids=ids,owned_box=[a,int(np.floor(top.min()))-5,b,int(np.ceil(bottom.max()))+5])
        for key in ownership.CURVES:
            r[key] = top if key in ('meanline','font_top','accent_top','top') else bottom
        rows.append(r); structure[rid]=dict(id=rid,column_id=column,block_id='block')
    rows = [ownership.prepare_row(r,ink,labels) for r in rows]
    return dict(rows=rows,structure=structure,ink=ink,labels=labels,ownership=ownership)


@pytest.mark.parametrize('n',[1,2,3])
def test_rows_count_before_owner_fraction(n):
    p=planted([(f'r{i}','c',10,100,15+i*35,0) for i in range(n)])
    m=supported_rows(p,[0,0,160,150])
    assert m['supported_row_count']==n and m['merged']==(n>=2)
    if n==3:
        old=p['ownership'].ownership([0,0,160,150],p['rows'])
        assert all(r['fraction']<.5 for r in old['row_overlaps'])


def test_skew_local_not_whole_envelope():
    p=planted([('a','c',10,145,15,.5),('b','c',10,145,45,.5)])
    m=supported_rows(p,[10,10,45,80])
    assert m['merged'] and m['supported_row_count']==2
    assert max(p['rows'][1]['baseline'])>80


def test_split_delivery_pieces_one_physical_row():
    p=planted([('same','c',5,50,25,0),('same','c',80,140,25,0)])
    m=supported_rows(p,[0,0,160,150])
    assert m['supported_row_ids']==['same'] and not m['merged']


def test_short_heading():
    p=planted([('heading','c',10,16,20,0)])
    m=supported_rows(p,[0,0,160,150])
    assert m['supported_row_count']==1 and not m['merged']


@pytest.mark.parametrize('box',[[0,25,160,55],[0,26,160,54],[0,24,160,56]])
def test_top_bottom_half_or_sixty_percent_only(box):
    p=planted([('above','c',10,100,20,0),('below','c',10,100,50,0)])
    m=supported_rows(p,box)
    assert not m['merged'] and m['supported_row_count']==0


def test_full_row_plus_edge_halves():
    p=planted([('above','c',10,100,20,0),('own','c',10,100,50,0),('below','c',10,100,80,0)])
    m=supported_rows(p,[0,25,160,85])
    assert m['supported_row_ids']==['own'] and not m['merged']


def test_adjacent_columns_do_not_make_multiline():
    p=planted([('left','c0',5,60,20,0),('right','c1',90,145,45,0)])
    m=supported_rows(p,[0,0,160,150])
    assert m['supported_row_count']==2 and not m['merged']


@pytest.mark.parametrize('vertical',[False,True])
def test_native_rule_cannot_support_row(vertical):
    p=planted([('own','c',10,70,20,0),('rule','c',80,145,60,0)])
    r=p['rows'][1]; p['labels'][p['labels']>=6]=0
    p['ink'][:]=p['labels']>0
    if vertical: p['labels'][35:110,85:87]=99
    else: p['labels'][62:64,80:145]=99
    p['ink'][:]=p['labels']>0
    raw={k:v for k,v in r.items() if not k.startswith('_')}
    raw.update(component_ids=[99],owned_box=[80,30,145,115])
    p['rows'][1]=p['ownership'].prepare_row(raw,p['ink'],p['labels'])
    m=supported_rows(p,[0,0,160,150])
    assert m['supported_row_ids']==['own'] and not m['merged']
    assert m['rows'][1]['excluded_component_ids']==[99]


def test_envelope_without_assigned_body_not_positive():
    p=planted([('one','c',10,100,20,0),('two','c',10,100,60,0)])
    p['rows'][1]['meanline'][:]=100; p['rows'][1]['baseline'][:]=110
    m=supported_rows(p,[0,0,160,150])
    assert m['supported_row_ids']==['one']


def test_legacy_flag_is_diagnostic_only():
    p=planted([('one','c',10,100,20,0)])
    assert not screen_merged(p,[0,0,160,150],legacy_features={'screen_merged':True,'projection_peaks':99})['merged']


def test_shared_before_ambiguous_owner_and_no_mutation(cached):
    p=load(cached); ink=p['ink'].copy(); labels=p['labels'].copy()
    m=g.observe_crop(p,[0,0,100,90])
    assert m['reason']=='ambiguous_target'
    assert m['row_inclusion']['supported_row_count']==3
    assert m['row_inclusion']['merged']
    assert np.array_equal(ink,p['ink']) and np.array_equal(labels,p['labels'])


def test_exact_frozen_witness_sets():
    ledger=json.loads((Path(__file__).parents[1]/'docs/records/harvest/collect_v3_admission/seg/calibration_ledger.json').read_text())
    c1={w['row_id'] for w in ledger['c1_witnesses']}
    gallery={w['row_id'] for w in ledger['gallery_witnesses'] if w['type']=='merged_multi_line'}
    prefix='gazette_modern--0020420cfe156a73--s000-'
    assert {prefix+i for i in ('l0039','l0162','l0228')}<=c1
    assert len(c1)==6 and len(gallery)==6
    assert len(c1 & gallery)==5


@pytest.mark.parametrize('case',['head','scope'])
def test_commit_guard_rejects_changed_head_or_scope(case,monkeypatch):
    import runpy
    guard=run_record(str(Path(__file__).parents[1]/'docs/records/harvest/collect_v3_admission/seg/guard_cp3_commit.py'))
    monkeypatch.setattr(guard['subprocess'],'check_output',lambda *a,**kw:'current\n')
    manifest=dict(base_HEAD='old' if case=='head' else 'current',files=[],read_only_dependencies=[])
    with pytest.raises(ValueError,match='base HEAD moved' if case=='head' else 'exact review scope'):
        guard['verify'](manifest)


def invalidate_first_row(cached, change='inverted'):
    import gzip
    p=cached[1]/'detector.json.gz'
    d=json.loads(gzip.decompress(p.read_bytes()))
    d['structure_rows'][0]['line_indices']=[101]
    d['structure_rows'][1]['line_indices']=[102]
    d['structure_rows'][2]['line_indices']=[103]
    d['rows'][1]['neighbours']['above']=[101]*100
    d['rows'][0]['bottom']=[6 if change=='inverted' else 8]*100
    p.write_bytes(gzip.compress(json.dumps(d).encode()))
    rp=cached[1]/'receipt.json';receipt=json.loads(rp.read_text())
    receipt['geometry_sha256']=g.sha(p);rp.write_text(json.dumps(receipt))


@pytest.mark.parametrize('change',['inverted','degenerate'])
def test_invalid_envelope_is_explicit_and_valid_rows_load(cached,change):
    invalidate_first_row(cached,change)
    page=load(cached)
    assert page['invalid_geometry_count']==1
    assert page['invalid_rows'][0]['status']=='invalid_geometry'
    assert page['invalid_rows'][0]['component_ids']==[1]
    assert [r['row_id'] for r in page['rows']]==['row-00001','row-00002']
    clean=screen_merged(page,[0,60,100,85])
    assert clean['status']=='measured' and not clean['merged']
    assert clean['invalid_geometry_count']==1


@pytest.mark.parametrize('box,target', [([0,0,100,30],None),
    ([0,60,100,85],'row-00000'),([0,35,100,55],'row-00001')])
@pytest.mark.parametrize('side',['above','left'])
def test_invalid_crop_target_or_neighbour_cannot_be_keep_or_detected(cached,box,target,side):
    invalidate_first_row(cached)
    page=load(cached)
    if side=='left':
        page['rows'][0]['neighbours']={'above':None,'below':None,'left':101,'right':None}
    m=g.observe_crop(page,box,target_row_id=target)
    assert m['status']=='unavailable' and not m['matched']
    assert m['reason']=='invalid_geometry' and m['invalid_row_ids']==['row-00000']
    if target!='row-00000':
        candidate=screen_merged(page,box)
        assert candidate['status']=='unavailable' and candidate['merged'] is None


@pytest.mark.parametrize('key,value',[('font_top',[1]),('top',[float('nan')]*100),
    ('baseline',[0]*100),('component_ids',[999])])
def test_invalid_envelope_does_not_hide_other_contract_errors(cached,key,value):
    import gzip
    invalidate_first_row(cached)
    p=cached[1]/'detector.json.gz';d=json.loads(gzip.decompress(p.read_bytes()))
    d['rows'][0][key]=value;p.write_bytes(gzip.compress(json.dumps(d).encode()))
    rp=cached[1]/'receipt.json';r=json.loads(rp.read_text());r['geometry_sha256']=g.sha(p)
    rp.write_text(json.dumps(r))
    with pytest.raises(ValueError):load(cached)
