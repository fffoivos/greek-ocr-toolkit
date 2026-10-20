"""Synthetic geometric and conservation invariants; no accuracy labels from ours."""
import cv2
import numpy as np
from prototypes.fast_lines.shared.detector import postprocess
from prototypes.fast_lines.shared.geometry_feature_paths import bands,sparse,contour_owners,describe
from prototypes.fast_lines.shared.geometry_feature_correct import retention,keep_nearby_ink,run
from prototypes.fast_lines.shared.geometry_feature_rules import split_items,curved_rule,boundary_ownership
from prototypes.fast_lines.shared.geometry_feature_separation import pixel_corridors,route2


def box(x0,y0,x1,y1):
    return dict(polygon=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],baseline=None,score=.9)


def test_affine_is_skew_not_curl():
    x=np.linspace(0,1000,101);d=describe(x,30+.03*x,20)
    assert d['bend_h']<1e-10
    assert abs(d['angle_deg']-np.degrees(np.arctan(.03)))<1e-10


def test_curl_is_not_absorbed_into_affine():
    x=np.linspace(0,1000,101);d=describe(x,30+.02*x-30*np.exp(-x/70),20)
    assert d['bend_h']>.3
    assert abs(d['angle_deg']-np.degrees(np.arctan(.02)))<.1


def test_exact_native_genealogy_and_no_baseline():
    pm=np.zeros((200,400),np.float32);pm[40:51,30:370]=.9;pm[110:121,20:350]=.9
    items=postprocess(pm,(800,400));owners=contour_owners(pm,(800,400))
    assert len(items)==2
    assert all(tuple(np.rint(q['polygon']).astype(int).ravel()) in owners for q in items)
    r=bands(pm,items,(800,400),3)
    assert len(r['lines'])==2
    assert all(q['source_boxes']==1 for q in r['lines'])
    assert all('baseline' not in q for q in r['lines'])


def test_straight_sparse_scout_does_not_dispatch():
    pm=np.zeros((200,400),np.float32)
    for y in (30,70,110,150):pm[y:y+11,30:370]=.9
    items=postprocess(pm,(400,200));s=sparse(pm,items,(400,200),3)
    assert not s['trigger']


def test_unique_ink_guard_rejects_whole_row_loss():
    gray=np.full((100,200),255,np.uint8);gray[30:35,20:180]=0;gray[60:65,20:180]=0
    q=box(10,20,190,75);p=box(10,55,190,75)['polygon']
    assert retention(gray,[q],0,p,12)['lost_ink']>0
    assert keep_nearby_ink(gray,[q],0,p,12)[0] is None


def test_guard_uses_current_neighbour_coverage():
    gray=np.full((80,160),255,np.uint8);gray[30:34,20:130]=0
    before=[box(10,20,140,50),box(10,20,140,50)];removed=box(10,40,140,50)['polygon']
    assert retention(gray,before,0,removed,10)['lost_ink']==0
    current=[dict(before[0],polygon=removed),before[1]]
    assert retention(gray,current,1,removed,10)['lost_ink']>0


def test_nearby_mark_retained_without_whole_row_padding():
    gray=np.full((100,200),255,np.uint8);gray[46:58,20:180]=0;gray[40:43,75:79]=0
    old=box(15,35,185,62);p=box(15,44,185,62)['polygon']
    repaired,audit=keep_nearby_ink(gray,[old],0,p,14)
    assert repaired is not None
    assert retention(gray,[old],0,repaired,14)['lost_ink']==0


def test_no_items_is_unresolved_no_invented_lines():
    gray=np.full((100,200),255,np.uint8);gray[30:40,20:180]=0
    d=run(gray,np.zeros((100,200),np.float32),[],3)
    assert d['items']==[] and d['geometry_changes']==[]
    assert d['rule_witness']['status']=='empty detector unresolved'


def test_white_page_is_not_gutter_evidence():
    assert pixel_corridors(np.full((200,300),255,np.uint8),10)==[]
    assert route2([], (300,200))['corridors']==[]


def test_repeated_endpoint_gaps_are_explicit():
    items=[q for y in (20,50,80,110) for q in (box(10,y,110,y+15),box(140,y,240,y+15))]
    assert route2(items,(250,150))['corridors']


def test_curved_rule_follows_original_ink():
    gray=np.full((300,200),255,np.uint8);y=np.arange(300);x=100+3*np.sin(y/100)
    for yy,xx in enumerate(x):gray[yy,int(xx):int(xx)+2]=0
    r,reason=curved_rule(gray,dict(bbox=[93,0,108,300]),10)
    assert r is not None,reason
    p=np.asarray(r['path']);assert np.max(abs(p[:,0]-np.interp(p[:,1],y,x)))<3


def test_split_preserves_original_source_ids():
    gray=np.full((200,300),255,np.uint8)
    q=box(0,50,290,70);q['source_ids']=[42]
    r=dict(path=[[150,0],[150,200]],y0=0,y1=200,horizontal_intersections=[])
    d=split_items(gray,[q],[r],10)
    assert len(d['items'])==2
    assert all(q['source_ids']==[42] for q in d['items'])


def test_word_gap_cannot_certify_rule_crossing_another_word():
    gray=np.full((140,300),255,np.uint8);gray[:,150:152]=0
    gray[30:35,135:170]=0
    items=[box(0,20,299,45),box(0,70,299,95)]
    rule=dict(path=[[151,0],[151,140]],y0=0,y1=140)
    a=boundary_ownership(gray,items,rule,10)
    assert not a['accepted'] and a['crossings'][0]['junction']
    assert not a['crossings'][1]['junction']


def test_isolated_separator_has_no_glyph_junction():
    gray=np.full((140,300),255,np.uint8);gray[:,150:152]=0
    items=[box(0,20,299,45),box(0,70,299,95)]
    rule=dict(path=[[151,0],[151,140]],y0=0,y1=140)
    a=boundary_ownership(gray,items,rule,10)
    assert a['accepted'] and len(a['crossings'])==2
