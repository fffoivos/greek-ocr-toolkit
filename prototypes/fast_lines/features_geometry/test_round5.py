"""R5 regression tests for native witnesses, column boundaries and source identity."""
import cv2
import numpy as np
import pytest
from prototypes.fast_lines.shared import geometry_columns as columns
from prototypes.fast_lines.shared import geometry_envelopes as shapes
from prototypes.fast_lines.shared.geometry_contacts import prepare


def box(a,b,c,d,**kw):
    return dict(polygon=[[a,b],[c,b],[c,d],[a,d]],baseline=None,score=.9,**kw)


def certificate(x=150,y0=40,y1=200):
    return dict(height=10,rules=[dict(accepted=True,rule=dict(path=[[x,y0],[x,y1]],y0=y0,y1=y1))])


def test_column_cut_keeps_source_metadata_and_all_original_pixels():
    q=box(5,60,295,85,source_ids=[7],initial_completed=True)
    r=columns.apply([q],certificate())
    assert len(r['items'])==2
    assert all(z['source_ids']==[7] and z['initial_completed'] for z in r['items'])
    old=np.zeros((250,300),np.uint8);new=old.copy()
    cv2.fillPoly(old,[np.array(q['polygon'])],1)
    for z in r['items']:cv2.fillPoly(new,[np.rint(z['polygon']).astype(np.int32)],1)
    assert np.array_equal(old,new)


@pytest.mark.parametrize('ys',[(5,35),(205,230)])
def test_rule_end_does_not_cut_running_title_or_following_prose(ys):
    q=box(5,*ys[:1],295,ys[1])
    assert columns.apply([q],certificate())['items']==[q]


def test_coincident_rule_nominees_do_not_create_slivers():
    e=certificate();e['rules']+=certificate(152)['rules']
    r=columns.apply([box(5,60,295,85)],e)
    assert len(r['items'])==2
    assert all(cv2.contourArea(np.array(q['polygon'],np.float32))>1000 for q in r['items'])


def test_wider_drift_nomination_still_requires_crossing_row():
    q=box(5,60,295,85);w=dict(height=10,vertical_components=[[138,20,23,220,300]])
    assert columns.nominate([q],w,(np.zeros((250,300)),1,1))
    assert not columns.nominate([box(5,60,100,85)],w,(np.zeros((250,300)),1,1))


def test_native_rule_crossing_fast_is_exact():
    g=np.full((240,300),255,np.uint8);g[40:200,149:152]=0
    rule=certificate()['rules'][0]['rule']
    assert columns.native_crossings(g,rule,10,'slow')==columns.native_crossings(g,rule,10,'explicit')
    assert columns.native_crossings(g,rule,10,'slow')['clear']
    g[80:83,140:160]=0
    a=columns.native_crossings(g,rule,10,'slow');b=columns.native_crossings(g,rule,10,'explicit')
    assert a==b and not a['clear'] and a['through'][0]['y0']==80


def test_no_through_stroke_without_bilateral_print_does_not_certify_rule(monkeypatch):
    e=certificate();rule=e['rules'][0]['rule']
    monkeypatch.setattr(columns,'nominate',lambda *a:[dict(bbox=[145,40,155,200])])
    monkeypatch.setattr(columns,'verify_rule',lambda *a:(rule,None))
    monkeypatch.setattr(columns,'grid_intersections',lambda *a:[])
    g=np.full((240,300),255,np.uint8);g[40:200,149:152]=0
    original=[box(5,80,295,95),box(5,110,145,125),box(155,110,295,125)]
    w=dict(height=10)
    assert columns.analyze(g,original,w,None)['rules'][0]['accepted']
    assert not columns.analyze(g,original,w,None,retained_source_indices={0,1})['rules'][0]['accepted']
    r=columns.analyze(g,original,w,None,retained_source_indices={1,2})
    assert r['rules'][0]['endpoints']['left'][0]['line']==1
    assert r['rules'][0]['endpoints']['right'][0]['line']==2


def test_component_labels_do_not_change_contact_field():
    g=np.full((80,160),255,np.uint8)
    for x in range(15,140,20):g[35:46,x:x+8]=0
    a=prepare(g,12,fast_filter=True);b=prepare(g,12,fast_filter=True,with_labels=True)
    assert a['components']==b['components'] and np.array_equal(a['density'],b['density'])
    assert 'labels' not in a and b['labels'].shape==g.shape


def test_offrow_exemption_uses_exact_pixels_not_component_bounding_box():
    g=np.full((80,160),255,np.uint8);g[20:25,20:30]=0;g[20:25,40:50]=0
    old=box(10,10,140,65);p=box(10,40,140,65)['polygon']
    labels=np.zeros_like(g,np.int32);labels[20:25,20:30]=4
    off=[dict(id=4,bbox=[15,15,60,30])]
    audit=shapes.owned_retention(g,[old],0,p,12,off,labels=labels)
    assert audit['offrow_ink']==50 and audit['lost_ink']==50
    with pytest.raises(ValueError):shapes.owned_retention(g,[old],0,p,12,off)


def test_shared_negative_scout_does_not_prepare_native_field(monkeypatch):
    def forbidden(*a,**k):raise AssertionError('unneeded native field')
    monkeypatch.setattr(shapes,'guided',forbidden)
    q=box(5,20,150,40)
    r=shapes.correct(np.zeros((100,200),np.uint8),np.zeros((10,20)),[q],[q],scout=dict(trigger=False))
    assert r['items']==[q] and not r['trigger']


@pytest.mark.parametrize('metadata,reason',[(dict(initial_completed=True),'completed initial shoulder retained'),(dict(source_ids=[3]),'separated source bounds retained')])
def test_protected_initial_and_split_ancestry_are_not_reshaped(monkeypatch,metadata,reason):
    q=box(5,20,150,40,**metadata);items=[q]
    if 'source_ids' in metadata:items.append(box(160,20,190,40,source_ids=[3]))
    path=[[5,35],[50,45],[100,45],[150,35]]
    evidence=dict(height=10,lines=[dict(line=0,polygon=box(5,25,150,50)['polygon'],path=path,ambiguous=False,extension_h=[0,0])],_labels=np.zeros((100,200),np.int32))
    monkeypatch.setattr(shapes,'guided',lambda *a,**k:evidence)
    r=shapes.correct(np.full((100,200),255,np.uint8),np.zeros((10,20)),items,[q],scout=dict(trigger=True))
    assert not r['changes'] and r['items']==items


def test_component_only_render_keeps_native_labels_and_statistics():
    g=np.full((80,160),255,np.uint8);g[35:46,20:28]=0
    a=prepare(g,12,with_labels=True);b=prepare(g,12,with_labels=True,with_density=False)
    assert a['components']==b['components'] and np.array_equal(a['labels'],b['labels'])
    assert b['density'] is None


def test_fast_tangent_preserves_paths_and_word_gap_uncertainty():
    from prototypes.fast_lines.shared.geometry_contacts import follow_contacts
    xs=np.linspace(0,300,101);ys=50+.03*xs;off=np.linspace(-20,20,81)
    sample=np.exp(-((off[:,None]-6*np.sin(xs[None,:]/140))/2)**2)
    sample[:,40:45]=0
    a=follow_contacts(sample,xs,ys,off,50,40,15)
    b=follow_contacts(sample,xs,ys,off,50,40,15,fast_fit=True)
    assert all(np.array_equal(x,y) for x,y in zip(a,b))


def test_later_band_cannot_borrow_an_earlier_replaced_polygon(monkeypatch):
    from prototypes.fast_lines.shared import geometry_joinbarriers
    items=[box(5,20,195,40,type_slot=True),box(5,40,195,60,type_slot=True)]
    proposed=[box(5,23,195,38)['polygon'],box(5,43,195,58)['polygon']]
    evidence=dict(height=10,components=[],_labels=np.zeros((100,210),np.int32),lines=[
        dict(line=i,polygon=proposed[i],path=[[5,30+20*i],[195,30+20*i]],
             bbox=[5,20+20*i,195,40+20*i],ambiguous=False,contacts=[],extension_h=[0,0]) for i in range(2)])
    monkeypatch.setattr(shapes,'guided',lambda *a,**k:evidence)
    monkeypatch.setattr(geometry_joinbarriers,'inspect',lambda *a:[])
    seen=[]
    def audit(gray,current,index,*a,**k):
        if index==1:assert current[0]['polygon']==proposed[0]
        seen.append(index)
        return dict(lost_ink=0,unique_ink=0,offrow_ink=0)
    monkeypatch.setattr(shapes,'owned_retention',audit)
    result=shapes.correct(np.full((100,210),255,np.uint8),np.zeros((10,21)),items,items,scout=dict(trigger=True))
    assert seen==[0,1] and len(result['changes'])==2


def test_display_order_uses_verified_column_before_row_sort():
    from prototypes.fast_lines.features_geometry.round5_benchmark import reading_order
    # Deliberately touching/overlapping raster envelopes defeat a global gap.
    items=[box(0,0,300,20),box(0,60,151,80),box(149,60,300,80),
           box(0,90,152,110),box(148,90,300,110),box(0,220,300,240)]
    assert reading_order(items,certificate())==[0,1,3,2,4,5]
