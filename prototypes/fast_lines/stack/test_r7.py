"""R7 speed/cleanup invariants, independent of page names and owner marks."""
import numpy as np
import cv2
import pytest
from ..shared.geometry_memo import page_geometry
from ..shared.geometry import line_axis,height_proxy
from ..shared.contracts import bbox,rect
from ..shared.type_dot_runs import chains
from ..shared.geometry_filter import gaussian_columns


def test_memo_geometry_replacement_and_scope():
    a=dict(polygon=rect([0,0,40,10]));b=dict(polygon=rect([0,0,80,20]))
    expected=(bbox(a),line_axis(a),height_proxy([a],(100,100)))
    @page_geometry
    def inside():
        box=bbox(a);box[0]=999
        axis=line_axis(a);axis[0]=999
        assert bbox(a)==expected[0]
        np.testing.assert_array_equal(line_axis(a),expected[1])
        assert height_proxy([a],(100,100))==expected[2]
        assert bbox(b)==[0,0,80,20] and height_proxy([b],(100,100))==10
    inside();a['polygon'][0][0]=-3
    assert bbox(a)[0]==-3  # no cache survives a call


def test_memo_exception_releases_context():
    a=dict(polygon=rect([0,0,40,10]))
    @page_geometry
    def fail():
        bbox(a);raise RuntimeError('test')
    with pytest.raises(RuntimeError):fail()
    a['polygon'][0][0]=-5
    assert bbox(a)[0]==-5


def test_dot_chains_keep_missing_dot_policy_and_distinct_rail():
    p=np.array([[x,0.] for x in [0,10,20,40,50,60]]+[[30,8.]],float)
    p=p[np.argsort(p[:,0])]
    one=list(chains(p,0,10,pitch_max=3,vertical=.22,horizontal=.25,lookahead=4,min_remaining=3,missing=False))
    two=list(chains(p,0,10,pitch_max=3,vertical=.22,horizontal=.25,lookahead=4,min_remaining=3,missing=True))
    assert next(r[2] for r in one if r[:2]==(0,1))==[0,1,2]
    assert next(r[2] for r in two if r[:2]==(0,1))==[0,1,2,4,5,6]


@pytest.mark.parametrize('shape,h', [((97,631),12.),((201,1371),49.5),((39,17),20.)])
def test_requested_gaussian_columns_preserve_native_density(shape,h):
    rng=np.random.default_rng(11);ink=(rng.random(shape)>.7).astype(np.float32)
    xs=np.arange(0,shape[1],max(1,round(.5*h)))
    explicit=cv2.GaussianBlur(ink,(0,0),.65*h,sigmaY=.12*h)[:,xs]
    sampled=gaussian_columns(ink,.65*h,.12*h,xs)
    # Native support/border unchanged. Different float accumulation is bounded
    # by float32 epsilon times the finite convolution support (unit-valued ink).
    bound=np.finfo(np.float32).eps*(round(8*.65*h+1)+round(8*.12*h+1))
    assert abs(sampled-explicit).max()<bound


def test_runtime_has_no_study_or_retired_route_imports():
    import ast
    from pathlib import Path
    from .pipeline import Stack,compose
    import inspect
    assert 'row_model' not in inspect.signature(Stack).parameters
    assert 'field_free' not in inspect.signature(compose).parameters
    tree=ast.parse(Path(inspect.getfile(inspect.unwrap(compose))).read_text())
    assert not any(isinstance(n,ast.ImportFrom) and n.module and any(z in n.module for z in ('evidence','round7','geometry_row_model')) for n in ast.walk(tree))
