"""Arithmetic equivalence and strict-dispatch invariants for batched scouting."""
import numpy as np
import pytest
from prototypes.fast_lines.shared.geometry import robust_fit
from prototypes.fast_lines.shared.geometry_feature_paths import sparse
from prototypes.fast_lines.shared.geometry_scout import affine_batch,sparse_fast
from prototypes.fast_lines.shared.detector import postprocess


def test_batched_robust_fit_keeps_outlier_resistance():
    x=np.broadcast_to(np.linspace(1500,2800,19),(3,19)).copy()
    y=np.array([20+.03*x[0],100-.02*x[1],500+.005*x[2]])
    y[0,8]+=20;y[1,10]-=15
    mask=np.ones_like(x,bool);mask[2,:3]=False;mask[2,-2:]=False
    a,b=affine_batch(x,y,mask)
    for j in range(3):
        expected=robust_fit(x[j,mask[j]],y[j,mask[j]])
        assert np.allclose([a[j],b[j]],expected,atol=1e-7,rtol=0)


@pytest.mark.parametrize('curve', [False,True])
def test_synthetic_scout_dispatch_equivalence(curve):
    pm=np.zeros((200,400),np.float32)
    for y in (30,70,110,150):
        for x in range(30,370):
            bend=int(10*np.exp(-(x-30)/25)) if curve else 0
            pm[y-bend:y-bend+11,x]=.9
    items=postprocess(pm,(400,200))
    slow=sparse(pm,items,(400,200),3);fast=sparse_fast(pm,items,(400,200))
    assert slow['trigger']==fast['trigger'] and slow['nominated']==fast['nominated']
    assert slow['fragments']==fast['fragments']
    for a,b in zip(slow['lines'],fast['lines']):
        assert a['path']==b['path'] and a['support']==b['support']
        assert abs(a['bend_h']-b['bend_h'])<1e-7


def test_empty_scout_is_not_a_clean_page_certificate():
    out=sparse_fast(np.zeros((100,100),np.float32),[],(100,100))
    assert not out['trigger'] and not out['lines']
