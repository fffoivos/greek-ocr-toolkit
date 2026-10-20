"""Independent field, edge, ownership and permanent-exclusion contracts."""
import cv2,numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from ..shared.geometry_edge_map import scout
from ..shared.geometry_field_detector import displacement
from ..shared.geometry_page_field import invert_points,render,certify
from ..shared.geometry_field_selection import apply
from ..shared.stack_ownership import reconcile
from ..shared.geometry_rows import scout as row_scout
from ..shared.geometry_contacts import prepare,trace


def item(a,b,c,d,source=0,**kw):
    return dict(polygon=[[a,b],[c,b],[c,d],[a,d]],baseline=None,score=.9,source_ids=[source],**kw)


def map_page(slope=0.,bend=0.):
    H,W=540,880;yy,xx=np.mgrid[:H,:W];pm=np.zeros((H,W),np.float32);items=[]
    delta=bend*np.maximum(0,(xx-570)/210)**2
    for n,y in enumerate(range(65,450,45)):
        pm=np.maximum(pm,np.exp(-((yy-y-slope*(xx-100)-delta)/4)**2).astype(np.float32)*((xx>100)&(xx<820)))
        q=item(100,y-13,780,y+13,n);p=np.array(q['polygon'],float);p[:,1]+=slope*(p[:,0]-100);q['polygon']=p.tolist();items.append(q)
    return pm,items,(W,H)


def test_outer_end_map_scout_rejects_affine_skew():
    for slope in [-.07,0,.07]:
        pm,qs,size=map_page(slope=slope)
        assert not scout(pm,qs,size)['trigger']


def test_outer_end_map_scout_observes_neighboring_bend():
    pm,qs,size=map_page(bend=18)
    r=scout(pm,qs,size)
    assert r['trigger'] and len(r['nominated'])>=3
    assert any(q['coherent'] and q['side']=='right' for q in r['records'])


def test_one_curved_row_does_not_certify_shared_bend():
    pm,qs,size=map_page(bend=18)
    assert not scout(pm,qs[:1],size)['trigger']


def test_empty_map_and_rows_are_quiet():
    assert not scout(np.zeros((64,64),np.float32),[],(640,640))['trigger']


def test_shared_field_inverse_round_trip():
    f=dict(xs=[0,100,200],knots=[0,150,300],mesh=[[0,10,20],[0,15,30],[0,20,40]])
    points=np.array([[10,60],[70,110],[140,250],[195,280]],float)
    bent=points.copy();bent[:,1]+=displacement(f,points[:,0],points[:,1])
    assert np.max(abs(invert_points(np.array(f['xs']),np.array(f['knots']),np.array(f['mesh']),bent)-points[:,1]))<1e-10


def text_page():
    g=np.full((200,650),245,np.uint8)
    cv2.putText(g,'ordinary printed words',(25,73),0,.8,20,2,cv2.LINE_AA)
    cv2.putText(g,'another printed row',(25,125),0,.8,20,2,cv2.LINE_AA)
    return g


def proposal(qs,h=20):return dict(items=[dict(q,page_field=True,field_ready=True) for q in qs],evidence=dict(height=h))


def test_permanent_footprint_vetoes_even_whole_field():
    g=text_page();old=[item(20,48,340,80)];new=item(18,45,345,82)
    r=apply(g,old,proposal([new]),forbidden_regions=[item(335,55,350,75)])
    assert r['items']==old and not r['replacements']


def test_foreign_row_witness_cannot_be_promoted():
    g=text_page();old=[item(20,48,340,80)];p=proposal(old);p['items'][0]['field_ready']=False
    assert apply(g,old,p)['items']==old


def test_unknown_lost_letters_keep_the_original():
    g=text_page();old=[item(20,45,400,82)];new=item(20,45,200,82)
    r=apply(g,old,proposal([new]))
    assert r['items']==old and any(d['lost_components'] for d in r['decisions'])


def test_separate_horizontal_sources_cannot_be_joined():
    g=np.full((150,650),245,np.uint8);cv2.putText(g,'first column',(20,80),0,.7,20,2);cv2.putText(g,'next column',(370,80),0,.7,20,2)
    old=[item(15,55,180,88,0),item(365,55,530,88,1)];r=apply(g,old,proposal([item(15,55,530,88)]),forbidden_regions=[])
    assert r['items']==old


def test_duplicate_child_is_merged_without_losing_any_polygon():
    g=text_page();owner=item(15,45,380,85,1);child=item(20,58,350,85,2,row_partition=True)
    r=reconcile(g,[owner,child]);assert len(r['items'])==1
    before=unary_union([Polygon(q['polygon']) for q in [owner,child]])
    assert Polygon(r['items'][0]['polygon']).symmetric_difference(before).area<1e-8


def test_narrow_gutter_and_overlapping_envelopes_preserve_independent_owners():
    g=np.full((150,650),245,np.uint8)
    cv2.putText(g,'first text',(20,80),0,.7,20,2)
    cv2.putText(g,'next text',(230,80),0,.7,20,2)
    for end,start in [(219,221),(230,215)]:
        old=[item(15,55,end,88,0),item(start,55,440,88,1)]
        r=apply(g,old,proposal([item(15,55,440,88)]))
        assert r['items']==old


def test_duplicate_resolution_keeps_unique_other_row():
    g=text_page();owner=item(15,45,380,85,1);child=item(20,48,350,130,2,row_partition=True)
    result=reconcile(g,[owner,child])['items']
    # The active all-segment reconciler may retire the upper duplicate. It
    # must preserve the lower row, rather than enforcing the retired policy's
    # unchanged segment count.
    assert any(q['polygon']==child['polygon'] for q in result)
    masks=[np.zeros(g.shape,np.uint8) for _ in range(2)]
    for q in [owner,child]:cv2.fillPoly(masks[0],[np.rint(q['polygon']).astype(int)],1)
    for q in result:cv2.fillPoly(masks[1],[np.rint(q['polygon']).astype(int)],1)
    assert not np.any((g<200)&(masks[0]>0)&(masks[1]==0))


def test_page_field_rows_do_not_reenter_B():
    g=text_page();q=item(15,45,380,135,page_field=True)
    assert not row_scout(g,[q],20)['candidates']


def test_cached_native_contacts_match_scalar_paths():
    g=text_page();qs=[item(20,47,400,80),item(20,99,400,132,1)];p=prepare(g,20,fast_filter=True)
    a=trace(p,qs[0],7,fast_fit=True);p.pop('_boxes');p.pop('_centres');b=trace(p,qs[0],7,fast_fit=True)
    assert a==b and a['contacts']


def test_native_field_does_not_call_flat_repeated_print_curved():
    g=np.full((650,1000),245,np.uint8);qs=[]
    for n,y in enumerate(range(70,600,45)):
        cv2.putText(g,'some ordinary printed words across this page',(35,y),0,.85,20,2,cv2.LINE_AA);qs.append(item(30,y-25,730,y+8,n))
    e=render(g,qs)
    assert not any(f.get('curved') for f in e['fields'])


def test_inverse_outside_mesh_is_unknown_not_endpoint_row_support():
    f=dict(xs=[0,100,200],knots=[0,150,300],mesh=[[0,10,20],[0,15,30],[0,20,40]])
    points=np.array([[-1,60],[201,60],[100,9],[100,321],[100,10],[100,320]],float)
    t=invert_points(np.array(f['xs']),np.array(f['knots']),np.array(f['mesh']),points)
    assert np.isnan(t[:4]).all()
    assert np.array_equal(t[4:],[0,300])


def test_inverse_fold_has_no_single_material_row_identity():
    xs=np.array([0,100,200]);knots=np.array([0,150,300]);mesh=np.array([[0,0,0],[0,-200,0],[0,0,0]])
    t=invert_points(xs,knots,mesh,np.array([[100,50],[0,50]],float))
    assert np.isnan(t[0]) and t[1]==50


def certificate_support():
    # The region includes both rows, but this translated mesh only represents
    # native y=100..300. All components pass the region and size filters.
    xs=np.linspace(0,600,31)
    field=dict(region=[0,0,600,400],xs=xs.tolist(),knots=[0,100,200],
               mesh=np.full((3,len(xs)),100.).tolist(),
               rows=[dict(seed=100.,path=np.c_[xs,np.full(len(xs),200.)].tolist())])
    def components(y):
        return [dict(centre=[float(x),y],bbox=[float(x-5),y-10,float(x+5),y+10])
                for x in np.linspace(20,580,31)]
    return dict(height=20.,fields=[field]),components(200.),components(50.)


def test_certificate_does_not_assign_unknown_inverse_support_to_first_row():
    evidence,valid,unknown=certificate_support()
    field=certify(evidence,valid+unknown)['fields'][0]
    assert {r['side'] for r in field['certificate']}=={'left','right'}
    expected=[[q['centre'][0],q['bbox'][3]] for q in valid]
    assert all(r['row']==0 and r['body_bottoms']==expected for r in field['certificate'])
    assert not field['curved']


def test_certificate_with_only_unknown_or_empty_support_has_no_witness():
    for empty in (False,True):
        evidence,_,unknown=certificate_support()
        field=certify(evidence,[] if empty else unknown)['fields'][0]
        assert field['certificate']==[] and not field['curved']
