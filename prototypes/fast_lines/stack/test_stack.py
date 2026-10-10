"""Integration invariants: one scout, stable ancestry, removal-before-recovery."""
import numpy as np
import cv2
from . import pipeline, geometry
from ..shared import type_recovery as recovery, type_context, geometry_context
from ..shared.contracts import rect


def item(x=0,y=0,w=80,h=10):
    return dict(polygon=rect([x,y,x+w,y+h]),baseline=None,score=.9)


def test_rejected_concave_footprint_is_not_convex_hull():
    shape=dict(polygon=[[0,0],[30,0],[30,5],[5,5],[5,30],[0,30]])
    assert not type_context.overlaps_exclusion(rect([10,10,20,20]),[shape])
    assert type_context.overlaps_exclusion(rect([1,10,10,20]),[shape])


def test_grid_view_preserves_real_polygons_and_order():
    q=item();r=dict(polygon=[[0,20],[20,18],[80,20],[80,30],[20,28],[0,30]])
    view=type_context.grid_view([q,r])
    assert view[0] is q and len(view[1]['polygon'])==4
    assert len(r['polygon'])==6
    assert type_context.grid_view([q])[0]==q


def test_type_adapter_never_calls_full_page_separator(monkeypatch):
    def forbidden(*a,**k):raise AssertionError('duplicate Q8')
    monkeypatch.setattr(recovery,'separators',forbidden)
    g=np.full((80,100),255,np.uint8)
    result=type_context.recover(g,[item()],object())
    assert result['items']==[item()] and not result['calls']
    extended=pipeline.recover(g,[item()],object())
    assert extended['items']==[item()] and not extended['calls']


def test_removed_seed_veto_precedes_detector(monkeypatch):
    slot=dict(supported=True,owned_fraction=0.,body_centres=[[10,10],[12,10]],height=5)
    r=type_context.recover(np.full((50,100),255,np.uint8),[],object(),
                          excluded_regions=[item(5,5,15,15)],lattice_evidence=dict(slots=[slot]))
    assert not r['added'] and not r['calls']
    assert r['decisions'][0]['reason']=='previously rejected region owns candidate ink'


def test_removed_neighbor_cannot_certify_geometry_retention(monkeypatch):
    g=np.full((80,100),255,np.uint8);g[15:25,15:75]=0
    original=[item(10,10,70,20),item(10,20,70,10)]
    kept=[dict(original[0],source_ids=[0])]
    monkeypatch.setattr(geometry,'sparse',lambda *a:dict(trigger=True,height=4,nominated=[0]))
    monkeypatch.setattr(geometry_context,'bands',lambda *a:dict(lines=[dict(line=0,bend_h=.8,polygon=rect([10,10,80,17]),source_boxes=1,multi_run_fraction=0,path=[[x,14] for x in range(10,81,10)],angle_deg=0)]))
    r=geometry.run(g,np.zeros((20,25),np.float32),original,kept,dict(candidates=[],height=4),None)
    assert r['items']==kept and not r['changes']
    assert r['decisions'][0]['reason']=='loss is not nearby envelope ink'


def test_compose_single_rule_scout_and_stable_sources(monkeypatch):
    original=[item(1,1),item(1,30)];calls=[]
    witness=dict(candidates=[],height=5)
    monkeypatch.setattr(pipeline,'scout',lambda *a:(calls.append('scout') or witness,None))
    def ink(g,current,**kwargs):
        assert current[1]['source_ids']==[1]
        calls.append('ink')
        return dict(items=[current[1]],removed=[0],ownership=dict(suppress_indices=[0]),scout_s=0,refinement_s=0)
    def geo(g,pm,orig,current,w,p,**kwargs):
        assert orig is original and len(current)==1 and current[0]['source_ids']==[1]
        assert kwargs['forbidden_regions'][0]['source_ids']==[0]
        calls.append('geometry')
        return dict(items=current,changes=[],curved=None,fragments=dict(joins=[]),joined_reduction=0,scout_s=0,geometry_s=0,curved_s=0,fragment_s=0)
    def typ(g,current,d,excluded_regions):
        assert excluded_regions[0]['source_ids']==[0] and current[0]['source_ids']==[1]
        calls.append('type')
        return dict(items=current,added=[],scout_s=0,correction_s=0)
    monkeypatch.setattr(pipeline,'ink_run',ink);monkeypatch.setattr(pipeline,'geometry_run',geo);monkeypatch.setattr(pipeline,'recover',typ)
    r=pipeline.compose(np.ones((100,100),np.uint8),np.zeros((10,10)),original,object())
    assert calls==['scout','ink','geometry','type']
    assert r['counts']['back']==1 and r['items'][0]['source_ids']==[1]


def test_public_entry_and_shared_height_preserve_ink_decisions():
    from . import Stack
    from ..features_ink.pipeline import ink_run
    from ..shared.geometry import height_proxy
    assert Stack is pipeline.Stack
    g=np.full((100,420),240,np.uint8)
    for x in range(20,390,35):
        cv2.line(g,(x,25),(x+7,70),25,3)
        cv2.circle(g,(x+15,53),9,25,2)
    current=[item(5,15,405,65)]
    default=ink_run(g,current)
    supplied=ink_run(g,current,height=height_proxy(current,(420,100)))
    reused=ink_run(g,current,ownership_evidence=default['ownership'])
    assert default['items']==supplied['items']==reused['items']==current
    assert default['removed']==supplied['removed']==reused['removed']==[]
    assert reused['ownership_reused'] and not supplied['ownership_reused']


def test_stack_uses_merged_track_functions():
    from ..features_ink.pipeline import ink_run
    from ..shared.type_extended import recover
    from ..shared.geometry_fragment_correct import run as joins
    from ..shared.geometry_context import correct_geometry
    assert pipeline.ink_run is ink_run and pipeline.recover is recover
    assert geometry.join_fragments is joins and geometry.correct_geometry is correct_geometry


def test_join_audit_counts_only_real_image_pixels():
    from .validate import retained_pixel_loss
    old=rect([2,2,10,8])
    assert retained_pixel_loss([old],rect([2,2,9,8]),(10,10))==0
    assert retained_pixel_loss([old],rect([2,2,8,8]),(10,10))==7
