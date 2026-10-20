"""Observed-ink boundaries and negative counterexamples for round5 corrections."""
import cv2,numpy as np
from ..shared.contracts import rect
from ..shared.ink_seal import trace,classify
from ..shared.ink_discrete_motifs import inspect,verify,layout_candidates
from ..shared.ink_ownership import analyze


def item(box):return dict(polygon=rect(box),baseline=None,score=.9)


def test_radial_upper_bound_preserves_closed_circle():
    g=np.full((280,280),235,np.uint8);cv2.circle(g,(140,140),90,90,3)
    a=trace(g,[140,140],90,20,route='explicit');b=trace(g,[140,140],90,20,route='explicit',early=True)
    assert a['smooth'] and a['max_gap_h']<2
    assert a['path']==b['path'] and a['observed']==b['observed']


def test_radial_shortcut_rejects_unobserved_circle():
    g=np.full((280,280),235,np.uint8)
    a=trace(g,[140,140],90,20,route='explicit');b=trace(g,[140,140],90,20,route='explicit',early=True)
    assert a['max_gap_h']>=2 and b['max_gap_h']>=2 and b['early_negative']


def test_observed_ring_does_not_own_interior_or_unnominated_text():
    g=np.full((300,300),235,np.uint8);cv2.circle(g,(150,150),100,150,3)
    g[136:166,239:245]=100;g[130:170,145:151]=30
    items=[item([232,130,252,170]),item([140,125,157,175])]
    ring=dict(outer=dict(ellipse=[[150,150],[200,200],0]))
    result=classify(g,items,20,[ring],[0,1])
    assert [r['line'] for r in result]==[0]
    assert classify(g,items,20,[ring],[])==[]


def test_vertical_repeated_quotes_never_promoted_by_component_gate():
    g=np.full((240,120),240,np.uint8)
    for y in range(30,220,45):cv2.putText(g,'"',(45,y),cv2.FONT_HERSHEY_SIMPLEX,.8,30,2)
    r=verify(g,item([35,5,75,225]),20,scouted=True)
    assert not r['drop'] and r['reason']=='vertical discrete ownership unresolved'


def test_fast_topology_matches_native_for_multi_lobed_repeated_ink():
    g=np.full((130,640),235,np.uint8)
    for x in range(40,620,55):
        for angle in np.linspace(0,2*np.pi,8,endpoint=False):
            cv2.line(g,(x,65),(round(x+20*np.cos(angle)),round(65+20*np.sin(angle))),25,3)
        cv2.circle(g,(x,65),3,25,-1)
    q=item([20,38,625,94]);slow=inspect(g,q,32);fast=inspect(g,q,32,fast=True)
    assert slow['groups']>0 and slow['matches']==fast['matches'] and slow['groups']==fast['groups']


def test_layout_nominates_outer_and_isolated_rows_without_certifying_ownership():
    items=[item([10,y,410,y+25]) for y in (10,40,70,170,280,310)]
    r=layout_candidates(items,20)
    assert [q['line'] for q in r]==[0,3,5]
    assert all('drop' not in q for q in r)


def test_short_weak_regions_are_exposed_but_remain_unknown():
    g=np.full((170,500),240,np.uint8);items=[]
    for y in (10,50,90):
        for x in range(10,480,12):g[y+6:y+26,x:x+6]=15
        items.append(item([5,y,490,y+32]))
    cv2.line(g,(12,145),(20,145),215,1);items.append(item([5,133,28,158]))
    r=analyze(g,items,height=20)
    assert 3 in r['weak_indices'] and 3 not in r['suspects']
    assert r['regions'][3]['ownership']=='unknown' and 3 not in r['suppress_indices']
