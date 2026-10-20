"""Independent image/geometry contracts for vertical row partitioning."""
import cv2
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from ..shared.geometry_rows import native,partition,analyze,scout,valley_path


def item(a,b,c,d):
    return dict(polygon=[[a,b],[c,b],[c,d],[a,d]],baseline=None,score=.8,source_ids=[7])


def page(rows=(65,110)):
    g=np.full((180,460),245,np.uint8)
    for y in rows:cv2.putText(g,'some printed words',(20,y),cv2.FONT_HERSHEY_SIMPLEX,.85,20,2,cv2.LINE_AA)
    return g


def test_two_native_rows_have_a_clear_gap():
    g=page();q=item(15,40,400,117);r=native(g,q,24)
    pieces,_=partition(q,r)
    assert len(pieces)==2
    assert unary_union([Polygon(p) for p in pieces]).symmetric_difference(Polygon(q['polygon'])).area<1e-8
    assert Polygon(pieces[0]).intersection(Polygon(pieces[1])).area<1e-8


def test_actual_polygon_excludes_neighbouring_rows():
    g=page((35,75,115));q=item(15,51,400,81);r=native(g,q,24)
    assert not partition(q,r)[0]


def test_accents_and_separated_words_are_not_two_rows():
    g=page((90,));q=item(15,55,400,103)
    for x in range(50,330,35):cv2.line(g,(x,61),(x+3,57),20,2)
    assert not partition(q,native(g,q,24))[0]


def test_oversized_initial_cannot_be_cut():
    g=page();cv2.rectangle(g,(25,41),(43,110),20,-1);q=item(15,39,400,117)
    r=native(g,q,24)
    assert not partition(q,r)[0]
    assert any(v['crossing'] for v in r['valleys'])


def test_tall_word_does_not_become_rows_of_single_letters():
    g=np.full((260,140),245,np.uint8)
    for k,char in enumerate('TEXT'):cv2.putText(g,char,(40,50+45*k),0,1,20,2)
    q=item(33,23,73,204)
    assert not partition(q,native(g,q,24))[0]


def test_blanks_and_empty_input():
    g=np.full((100,200),255,np.uint8)
    assert not analyze(g,[])['changes']
    assert not analyze(g,[item(5,10,190,80)])['changes']


def test_scout_nominates_two_rows_but_cannot_change_items():
    g=page();q=item(15,40,400,117);before=dict(q)
    r=scout(g,[q],24)
    assert r['candidates']==[0] and q==before


def test_page_margin_and_nonrectangular_polygon_are_respected():
    g=page();q=item(0,0,420,125);q['polygon']=[[0,0],[420,0],[420,80],[220,80],[220,125],[0,125]]
    pieces,_=partition(q,native(g,q,24))
    if pieces:
        assert unary_union([Polygon(p) for p in pieces]).symmetric_difference(Polygon(q['polygon'])).area<1e-8
        assert all(Polygon(p).difference(Polygon(q['polygon'])).area<1e-8 for p in pieces)


def test_detached_mark_stays_with_its_body():
    g=page();cv2.circle(g,(68,86),2,20,-1);q=item(15,40,400,117)
    pieces,_=partition(q,native(g,q,24))
    assert len(pieces)==2
    # The added accent and the lower letter directly beneath it share a child.
    from shapely.geometry import Point
    owners=lambda x,y:{i for i,p in enumerate(pieces) if Polygon(p).covers(Point(x,y))}
    assert owners(68,86)==owners(68,101)


def test_minimum_gap_follows_bend_without_crossing_barriers():
    h=20;cost=np.full((75,160),1e6)
    mid=25+np.rint(10*np.sin(np.linspace(0,np.pi,160))).astype(int)
    for x,y in enumerate(mid):cost[y-4:y+5,x]=abs(np.arange(y-4,y+5)-y)*.01
    path=valley_path(cost,h)
    assert np.max(abs(path-mid))<4


def test_row_split_source_and_parent_are_stable():
    g=page();q=item(15,40,400,117)
    # Normal one-row peers establish the body scale independently of the bad
    # tall box. The shared parent, source and score survive each partition.
    r=analyze(g,[q,item(15,41,400,70),item(15,86,400,115)])
    changed=[v for v in r['items'] if v.get('row_parent_index')==0]
    assert len(changed)==2
    assert all(v['source_ids']==[7] and v['score']==.8 and v['row_parent_polygon']==q['polygon'] for v in changed)
