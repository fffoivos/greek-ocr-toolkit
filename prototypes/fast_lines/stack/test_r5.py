"""Contract tests for local filtering, shared fields and row-statistic reuse."""
import numpy as np
from ..shared.geometry_contacts import prepare
from ..shared.geometry_envelopes import guided


def test_local_gaussian_has_complete_halo_and_original_page_edges():
    rng=np.random.default_rng(31);g=np.full((220,350),240,np.uint8)
    for _ in range(200):
        x=int(rng.integers(0,345));y=int(rng.integers(0,213));g[y:y+7,x:x+5]=int(rng.integers(10,150))
    regions=[(0,0,80,40),(100,80,250,140),(300,180,350,220)]
    a=prepare(g,12,fast_filter=True,with_labels=True)
    b=prepare(g,12,fast_filter=True,with_labels=True,density_regions=regions)
    assert a['components']==b['components'] and np.array_equal(a['labels'],b['labels'])
    for x,y,z,w in regions:np.testing.assert_allclose(a['density'][y:w,x:z],b['density'][y:w,x:z],rtol=0,atol=2e-7)


def test_native_field_reuse_rejects_wrong_height():
    import pytest
    g=np.full((100,200),255,np.uint8)
    with pytest.raises(AssertionError):
        guided(g,np.zeros((10,20)),[],[],route='explicit',field_cache=dict(height=-1,shape=g.shape,prepared={}))


def test_batched_ownership_matches_native_predicate_at_concavities_and_edges():
    import cv2
    from ..shared.type_lattice import point_ownership
    polys=[dict(polygon=[[0,0],[12,0],[12,4],[4,4],[4,12],[0,12]]),
           dict(polygon=[[20,2],[24,10],[17,10]])]
    pts=[[x,y] for x in np.linspace(-1,25,53) for y in np.linspace(-1,13,29)]
    expected=[any(cv2.pointPolygonTest(np.array(q['polygon'],np.float32),tuple(map(float,p)),False)>=0 for q in polys) for p in pts]
    assert point_ownership(pts,polys)==expected
    assert point_ownership(pts[:3],polys)==expected[:3]
