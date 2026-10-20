"""Bend regression controls: retention, short tails, affine and white cuts."""
import cv2
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import split
from ..shared.ink_normal import NormalInk,follow_letters
from ..shared.geometry_bend import Bend,scout,phase,offset
from ..shared.geometry_bend_edits import loss_pixels,white_cut


def test_short_tail_counts_kept_letters_and_stops_at_faint():
    bb=np.array([[x,10,x+7,20] for x in [0,9,18,27,36,45,54]])
    r=follow_letters(bb,np.full(7,15),[1,1,1,0,1,1,1],[1,1,0,0,0,0,0],10,15,gap_limit=20)
    assert r.admitted.tolist()==[True,True,True,False,True,True,True]
    # The independent later run may become a separate crop; it cannot extend
    # the anchored run across the faint letter.
    assert r.runs[0]==r.runs[2] and r.runs[4]!=r.runs[0]


def test_faint_found_ink_is_not_a_deletion_permission():
    bb=np.array([[x,10,x+7,20] for x in [0,9,18]])
    r=follow_letters(bb,[15]*3,[0,0,0],[1,1,0],10,15,gap_limit=20)
    assert r.admitted.tolist()==[True,True,False]


def test_growth_uses_material_position_not_box_median():
    bb=np.array([[0,0,7,10],[9,7,16,17],[18,19,25,29]])
    r=follow_letters(bb,[5,5,5],[1,1,1],[1,1,0],10,5,gap_limit=20)
    assert r.admitted.all()


def test_wide_gap_cannot_join_a_single_last_letter():
    bb=np.array([[0,0,7,10],[9,0,16,10],[40,0,47,10]])
    r=follow_letters(bb,[5]*3,[1]*3,[1,1,0],10,5,gap_limit=20)
    assert r.admitted.tolist()==[True,True,False]


def test_affine_column_is_not_curvature():
    boxes=[];records=[]
    for i,y in enumerate(range(30,190,20)):
        xs=np.linspace(10,390,39);ys=y+.08*xs
        boxes.append([10,y,390,y+40]);records.append(dict(line=i,path=np.c_[xs,ys].tolist()))
    fields=scout(np.ones((250,400),np.float32),np.array(boxes),(400,250),dict(height=10,records=records))
    assert all(f.side==0 for f in fields)


def test_inverse_shared_bend():
    f=Bend(np.array([0,0,400,300]),np.array([2,0,0,12,1,0,-15,0,0.]),10,20,np.array([100,120]),1,np.array([100,120]))
    x=np.linspace(0,400,20);y=np.full(20,100.)
    assert np.max(abs(phase(f,x,y+offset(f,x,y))-y))<.01


def test_white_cut_preserves_dark_pixels():
    g=np.full((80,180),255,np.uint8);g[20:30,10:170]=0;g[43:54,10:170]=0
    f=Bend(np.array([0,0,180,80]),np.zeros(9),10,24,np.array([25,48]),1,np.array([25,48]))
    p=np.array([[5,15],[175,15],[175,59],[5,59]])
    cut=white_cut(g,f,25,48,4,176);assert cut is not None
    parts=[np.asarray(q.exterior.coords) for q in split(Polygon(p),LineString(cut)).geoms]
    assert len(parts)==2 and loss_pixels(g,[p],parts)==0


def test_pixel_invariant_counts_a_partial_letter():
    g=np.full((30,30),255,np.uint8);g[10:20,10:20]=0
    old=np.array([[5,5],[25,5],[25,25],[5,25]])
    new=np.array([[5,5],[15,5],[15,25],[5,25]])
    assert loss_pixels(g,[old],[new])==40


def test_normal_reference_has_no_row_model_dependency():
    assert NormalInk.__module__.endswith('ink_normal')


def test_hole_is_not_silently_filled_over_an_exclusion():
    from ..shared.geometry_bend_edits import _parts
    outer=Polygon([(0,0),(20,0),(20,20),(0,20)],holes=[[(5,5),(15,5),(15,15),(5,15)]])
    assert _parts(outer)==[]
