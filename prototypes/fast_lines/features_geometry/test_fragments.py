"""Conservation, separation and ancestry contracts for native fragment joins."""
import cv2
import numpy as np
import pytest
from prototypes.fast_lines.shared import geometry_fragment_correct as correct
from prototypes.fast_lines.shared.geometry_contacts import prepare,follow_contacts
from prototypes.fast_lines.shared.geometry_joinbarriers import inspect


def box(x0,y0,x1,y1):return dict(polygon=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],baseline=None,score=.9)


def fixture():
    gray=np.full((120,240),255,np.uint8)
    items=[box(10,40,160,60),box(171,34,205,54)]
    path=[[x,50-(x-160)*.1 if x>160 else 50] for x in range(10,206)]
    witness=dict(height=10,pairs=[dict(line=0,fragment=1,owners=1)],trigger=True)
    rendering=dict(lines=[dict(line=0,path=path,alternatives=[dict(fragment=1,path=path,observed=[True]*len(path),agrees=True,overlap_h=12,error_p90_h=0)])])
    return gray,items,witness,rendering


def test_envelope_preserves_rotated_polygons():
    qs=[box(5,30,100,55),dict(polygon=[[114,25],[145,15],[150,40],[120,50]])]
    p,old,new,_=correct.envelope(qs,(90,170),[[x,42-.2*max(x-100,0)] for x in range(5,151)],10)
    assert len(p)>4
    assert not np.any((old>0)&(new==0))


def test_join_conserves_ancestry_without_mutating_originals():
    g,items,w,r=fixture();a=correct.run(g,items,witness=w,rendering=r)
    assert len(a['joins'])==1 and len(a['items'])==1
    assert a['items'][0]['source_ids']==[0,1]
    assert 'source_ids' not in items[0]
    assert a['items'][0]['baseline'] is None


def test_disagreeing_native_path_abstains():
    g,items,w,r=fixture();r['lines'][0]['alternatives'][0]['agrees']=False
    assert not correct.run(g,items,witness=w,rendering=r)['joins']


def test_new_neighbor_ink_vetoes_join():
    g,items,w,r=fixture();g[45:49,162:167]=0;items.append(box(162,42,167,52))
    a=correct.run(g,items,witness=w,rendering=r)
    assert not a['joins']
    assert any('neighboring' in q['reason'] for q in a['decisions'])


def test_rejected_region_cannot_be_recaptured():
    g,items,w,r=fixture()
    a=correct.run(g,items,witness=w,rendering=r,forbidden_regions=[dict(bbox=[162,42,167,52])])
    assert not a['joins']


def test_removed_or_split_fragment_cannot_be_joined():
    g,items,w,r=fixture()
    for current in [[dict(items[0],source_ids=[0])],[dict(items[0],source_ids=[0]),dict(items[1],source_ids=[1]),dict(items[1],source_ids=[1])]]:
        assert not correct.run(g,items,current,witness=w,rendering=r)['joins']


def test_untraced_original_competing_owner_abstains():
    g,items,w,r=fixture();items.append(box(10,65,160,85))
    w['pairs'].append(dict(line=2,fragment=1,owners=2))
    a=correct.run(g,items,[dict(items[0],source_ids=[0]),dict(items[1],source_ids=[1])],witness=w,rendering=r)
    assert not a['joins']


def test_regional_rule_preserves_separate_cells():
    g,items,w,r=fixture();cv2.line(g,(165,0),(165,119),0,2)
    assert any(x['rule'] for x in inspect(g,box(10,34,205,60)['polygon'],10))
    assert not correct.run(g,items,witness=w,rendering=r)['joins']


def test_native_filter_keeps_original_component_inventory():
    g=np.full((100,250),255,np.uint8)
    for x in range(15,230,14):g[40:52,x:x+6]=0
    a=prepare(g,12);b=prepare(g,12,fast_filter=True)
    assert a['components']==b['components']
    assert np.max(abs(a['density']-b['density']))<1e-6


def test_long_empty_gap_stops_contacts_instead_of_changing_rows():
    xs=np.arange(80,dtype=float);ys=np.zeros(80);offsets=np.arange(-20,21,dtype=float)
    sample=np.zeros((41,80));sample[20,:20]=1;sample[30,40:]=1
    indices,observed=follow_contacts(sample,xs,ys,offsets,10,20,4)
    assert observed[:20].all() and not observed[20:].any()


def test_missing_ancestry_is_explicit_error():
    g,items,w,r=fixture()
    with pytest.raises(ValueError):correct.run(g,items,items,witness=w,rendering=r)
