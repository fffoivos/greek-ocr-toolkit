"""Physical perturbations and correction invariants; no page-name fixtures."""
import copy
import unittest
from unittest.mock import patch
import cv2
import numpy as np
from ..shared.contracts import rect
from ..shared.type_lattice import analyze,point_ownership
from ..shared.type_profiles import measure_line
from ..shared.type_tables import box_grid,analyze as table_analyze
from ..shared.type_completion import snap_components
from ..shared.type_recovery import run,ink_ownership
from ..shared.review import detector_record


def page(missing=3,ink=True,scale=1):
    g=np.full((300,500),255,np.uint8);items=[]
    for j in range(7):
        y=50+32*j
        if j!=missing or ink:
            for x in range(45,450,18):cv2.rectangle(g,(x,y-7),(x+8,y+7),0,-1)
        if j!=missing:items.append(dict(polygon=rect([35,y-15,465,y+15]),baseline=None,score=.9))
    if scale!=1:
        g=cv2.resize(g,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
        items=[dict(q,polygon=(np.asarray(q['polygon'])*scale).tolist()) for q in items]
    return g,items


class TypeFeatureTests(unittest.TestCase):
    def test_blank_slot_is_not_text(self):
        g,it=page(ink=False);r=analyze(g,it,version=3)
        self.assertEqual(len(r['slots']),1);self.assertFalse(r['slots'][0]['supported'])
    def test_body_ink_supports_bracketed_gap(self):
        g,it=page();r=analyze(g,it,version=3);self.assertTrue(r['slots'][0]['supported']);self.assertEqual(r['slots'][0]['owned_fraction'],0)
    def test_scale_equivariance_of_grid(self):
        records=[analyze(*page(scale=s),version=3) for s in [1,2]]
        self.assertEqual(len(records[0]['slots']),len(records[1]['slots']))
        self.assertAlmostEqual(records[0]['blocks'][0]['pitch']*2,records[1]['blocks'][0]['pitch'])
    def test_short_heading_owns_slot(self):
        g,it=page();it.append(dict(polygon=rect([180,137,270,155])))
        self.assertEqual(analyze(g,it,version=3)['slots'],[])
    def test_polygon_not_bbox_owns_points(self):
        it=[dict(polygon=[[0,0],[20,0],[0,20]])]
        self.assertEqual(point_ownership([[3,3],[18,18]],it),[True,False])
    def test_empty_detector_is_unknown(self):
        self.assertEqual(analyze(np.full((100,100),255,np.uint8),[],version=3)['slots'],[])
    def test_body_size_resists_detached_accents(self):
        g,it=page(missing=-1);a=measure_line(g,it[0],samples=None,version=3)
        for x in range(50,450,36):cv2.rectangle(g,(x,36),(x+3,39),0,-1)
        b=measure_line(g,it[0],samples=None,version=3)
        self.assertAlmostEqual(a['xheight'],b['xheight'],delta=2);self.assertIsNone(b['baseline']);self.assertGreater(b['mark_count'],2)
    def test_contact_height_scales(self):
        out=[]
        for s in [1,2]:
            g,it=page(missing=-1,scale=s);out.append(measure_line(g,it[0],samples=None,version=3)['xheight']/s)
        self.assertAlmostEqual(*out,delta=1)
    def test_table_grid_preserves_input(self):
        g=np.full((300,500),255,np.uint8);it=[dict(polygon=rect([x,y,x+20,y+16])) for x in [60,100,140] for y in [40,80,120,160]];before=copy.deepcopy(it)
        r=table_analyze(g,it,route='heuristic',version=5)
        self.assertTrue(r['regions']);self.assertEqual(it,before)
    def test_distant_leaves_do_not_form_table(self):
        it=[dict(polygon=rect([x,y,x+20,y+16])) for x in [60,350] for y in [40,80,120,160]]
        regions,_=box_grid(it,10,5);self.assertEqual(regions,[])
    def test_prose_not_short_cell_grid(self):
        g,it=page(missing=-1);self.assertEqual(box_grid(it,15,5)[0],[])
    def test_existing_ink_not_new_ink(self):
        g,it=page(missing=-1);self.assertEqual(ink_ownership(g,it[0]['polygon'],it,15),1)
    def test_no_detached_initial_growth(self):
        g=np.full((120,240),255,np.uint8);cv2.rectangle(g,(10,25),(25,65),0,-1);cv2.rectangle(g,(45,52),(200,65),0,-1)
        q=dict(polygon=rect([40,48,210,70]),baseline=None);r=snap_components(g,q,15)
        self.assertGreaterEqual(np.asarray(r['polygon'])[:,0].min(),40)
    def test_clean_page_does_not_infer(self):
        g,it=page(missing=-1)
        class NoDetector:
            def infer(self,*a,**kw):raise AssertionError('clean page inferred')
        out=run(g,it,NoDetector(),version=3);self.assertEqual(out['items'],it);self.assertEqual(out['calls'],[])
    def test_book_reference_excludes_current_page(self):
        from ..shared.type_book import summarize
        pages=[dict(page=str(i),width=1000,lines=[dict(xheight=h,uncertain=False)]) for i,h in enumerate([10,20,30])]
        r=summarize(pages)['pages'];self.assertAlmostEqual(r[0]['other_page_body'],.025);self.assertEqual(r[0]['reference_pages'],['1','2'])
    def test_book_does_not_borrow_uncertain_size(self):
        from ..shared.type_book import summarize
        r=summarize([dict(page='a',width=100,lines=[dict(xheight=20,uncertain=True)])])['pages'][0]
        self.assertEqual(r['support'],0);self.assertIsNone(r['relative_to_other_pages'])
    def test_stack_skips_both_separators(self):
        from ..shared.type_context import recover
        g,it=page(missing=-1)
        with patch('prototypes.fast_lines.shared.type_recovery.separators',side_effect=AssertionError('duplicate separator')):
            r=recover(g,it,None)
        self.assertEqual(r['items'],it);self.assertIsNone(r['separator'])
    def test_rejected_ink_never_recovered(self):
        from ..shared.type_context import recover
        g,it=page()
        class NoDetector:
            def infer(self,*a,**kw):raise AssertionError('rejected region inferred')
        r=recover(g,it,NoDetector(),excluded_regions=[[30,130,470,160]])
        self.assertEqual(r['added'],[]);self.assertIn('previously rejected',r['decisions'][0]['reason'])
    def test_ribbon_grid_view_preserves_actual_polygons(self):
        from ..shared.type_context import grid_view
        q=dict(polygon=[[0,20],[20,18],[40,20],[40,30],[20,28],[0,30]])
        before=copy.deepcopy(q);view=grid_view([q])
        self.assertEqual(q,before);self.assertEqual(len(view[0]['polygon']),4)
    def test_exclusion_uses_concave_polygon(self):
        from ..shared.type_context import overlaps_exclusion
        region=dict(polygon=[[0,0],[20,0],[20,5],[5,5],[5,20],[0,20]])
        self.assertFalse(overlaps_exclusion(rect([10,10,18,18]),[region]))
        self.assertTrue(overlaps_exclusion(rect([2,10,4,18]),[region]))
    def test_rows_do_not_average_adjacent_bodies(self):
        from ..shared.type_rows import render
        g,it=page(missing=-1)
        q=dict(polygon=rect([35,65,465,120]))
        r=render(g,q,version=3)
        self.assertTrue(r['ambiguous'] or r['body_height']<25)
        self.assertIsNone(r['baseline'])
    def test_native_shape_locations_are_deduplicated(self):
        from ..shared.type_identity import extract
        g,it=page(missing=-1);one,_=extract(g,it[:1],version=2);two,_=extract(g,it[:1]*2,version=2)
        self.assertEqual(len(one),len(two));self.assertTrue(all(z['owners']==[0,1] for z in two))
    def test_grid_edges_do_not_reinterpret_regular_interior(self):
        from ..shared.type_grid_edges import candidates
        from ..shared.type_lattice import blocks
        g,it=page();r=candidates(blocks(it,(500,300)),it,(500,300),version=2)
        self.assertFalse(any(s['edge']==0 for s in r))
    def test_ornament_negative_does_not_certify_recovery(self):
        from ..shared.type_extended import recover
        g,it=page(ink=False)
        class NoDetector:
            def infer(self,*a,**kw):raise AssertionError('blank slot inferred')
        r=recover(g,it,NoDetector());self.assertEqual(r['added'],[])
    def test_terminal_dots_protect_but_accents_do_not(self):
        from ..shared.type_table_extent import analyze
        g=np.full((280,500),255,np.uint8);it=[]
        for y in [50,90,130,170]:
            for x in range(40,210,18):cv2.rectangle(g,(x,y-10),(x+8,y+8),0,-1)
            for x in range(270,420,30):cv2.circle(g,(x,y+5),3,0,-1)
            it.append(dict(polygon=rect([30,y-18,440,y+18])))
        self.assertTrue(analyze(g,it,version=6)['regions'])
        g2=np.full_like(g,255)
        for y in [50,90,130,170]:
            for x in range(40,430,18):
                cv2.rectangle(g2,(x,y-10),(x+8,y+8),0,-1);cv2.circle(g2,(x+3,y-14),2,0,-1)
        self.assertEqual(analyze(g2,it,version=6)['regions'],[])
    def test_export_omits_discounted_and_keeps_null_baseline(self):
        r=detector_record(dict(page='fixture',image_size=[20,20]),[dict(polygon=rect([0,0,10,10]),baseline=None,score=.9),dict(polygon=rect([1,1,3,3]),discounted=True)],.1)
        self.assertEqual(len(r['items']),1);self.assertIsNone(r['items'][0]['baseline']);self.assertEqual(r['unit'],'line')

if __name__=='__main__':cv2.setNumThreads(1);unittest.main()
