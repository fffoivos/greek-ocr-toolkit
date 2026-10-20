"""Native corridor regressions; request-only trial and unchanged default route.

The tiny ink fixture is a crop of the pinned M17 mask, not a synthetic Greek
font. Its provenance is beside the array. Default defects remain strict xfail
when the request-only implementation is not installed.
"""
import inspect
from pathlib import Path
import cv2
import numpy as np
import pytest
from ..shared import geometry_field_detector as field
from ..shared.contracts import rect

REQUEST_MODE = 'request_mode' in inspect.signature(field.separate_bands).parameters


def mask(shape, row):
    out = np.zeros(shape, np.uint8)
    cv2.fillPoly(out, [np.rint(row['polygon']).astype(np.int32)], 1)
    return out


@pytest.mark.parametrize('phase', [0, 1])
@pytest.mark.xfail(not REQUEST_MODE, strict=True,
                   reason='Default coarse/dilated separator fails the same native phi/beta ink across lattice origins')
def test_native_phi_beta_corridor_reaches_final_clipping(phase):
    # Cover every x phase of the actual 13px coarse lattice; two lucky crop
    # origins do not establish native-resolution separation.
    for origin_shift in range(13):
        check_native_phi_beta(phase,origin_shift)


def check_native_phi_beta(phase, origin_shift):
    z = np.load(Path(__file__).with_name('native_corridor.npz'))
    ink = z[f'ink{phase}'][:,origin_shift:]; axes = z[f'axes{phase}'].copy(); h = float(z['height'])
    axes[:,0] += axes[:,1]*origin_shift
    n, labels, stats, _ = cv2.connectedComponentsWithStats(ink, 8)
    rows = [dict(polygon=p.tolist()) for p in z[f'rows{phase}']]
    for q in rows:
        for point in q['polygon']:
            point[0] = max(0,point[0]-origin_shift)
    kw = dict(request_mode=True, axes=axes,
              supports=[[[0, ink.shape[1]-1]]]*2) if REQUEST_MODE else {}
    output, audit = field.separate_bands(255-ink*255, rows, h, ink,
                                         stats, labels, {}, **kw)
    assert len(audit) == 1 and audit[0]['path'], 'actual separator not reached'
    assert audit[0]['accepted'], audit[0]['crossing']
    upper, lower = [mask(ink.shape, q) for q in output]
    phi = z[f'phi{phase}'][:,origin_shift:].astype(bool); beta = z[f'beta{phase}'][:,origin_shift:].astype(bool)
    assert phi.any() and beta.any()
    assert upper[phi].all() and not upper[beta].any(), 'phi clipped or beta absorbed'
    assert lower[beta].all() and not lower[phi].any(), 'beta clipped or phi duplicated into lower row'
    # Pixel contact, even without a sign-changing crossing, is not accepted.
    path = np.asarray(audit[0]['path'])
    for component in (phi, beta):
        yy, xx = np.nonzero(component)
        delta = yy-np.interp(xx, path[:,0], path[:,1])
        assert np.all(delta < 0) or np.all(delta > 0)


@pytest.mark.skipif(not REQUEST_MODE, reason='Archived request-only candidate contract, not installed runtime')
def test_default_keyword_is_byte_equal():
    from .test_residual_completion import ambiguous_corridor_fixture
    gray, rows = ambiguous_corridor_fixture()
    plain = field.native_bands(gray, rows, 40)
    explicit = field.native_bands(gray, rows, 40, request_mode=False)
    assert plain == explicit


@pytest.mark.skipif(not REQUEST_MODE, reason='Archived request-only candidate contract, not installed runtime')
def test_rule_edge_and_body_endpoint_are_real_preparation():
    gray = np.zeros((80, 120), np.uint8)
    gray[5:76, 48:54] = 1
    _, labels, stats, _ = cv2.connectedComponentsWithStats(gray, 8)
    rule = dict(rule_id=0, path=[[50,5],[50,75]], y0=5, y1=75, side=1)
    domains = field.rule_edges([[rule]], gray, labels)
    assert np.asarray(domains[0][0]['path'])[:,0].min() == 54
    # An observed span alone omits an owned body in its gap.
    stats = np.array([[0,0,0,0,0], [73,25,6,12,72]])
    support = field.body_supports([[[50,70],[90,110]]], [[1]], stats, domains)[0]
    assert min(p[0] for p in support) >= 54
    assert any(lo <= 73 and hi >= 78 for lo, hi in support)


@pytest.mark.skipif(not REQUEST_MODE, reason='Archived request completion consumer, not installed runtime')
def test_complete_request_keeps_unassigned_mark_rule_side_and_order():
    from ..shared.type_completion import complete_request
    from .test_residual_completion import ambiguous_corridor_fixture, item
    gray, old = ambiguous_corridor_fixture()
    # This synthetic rule is observed over the whole fixture, with actual ink
    # on both sides of its fitted centre. It is not a discovered new gutter.
    cv2.line(gray, (320,0), (320,249), 20, 2)
    evidence=dict(rules=[dict(accepted=True,rule=dict(
        path=[[320,0],[320,249]],y0=0,y1=249))])
    # Lower-contact observations refer to this native component census. Marks
    # are intentionally absent from the body list and must enter by corridor.
    _,labels,stats,centres=cv2.connectedComponentsWithStats((gray<100).astype(np.uint8),8)
    bodies=[];chains=[[] for _ in range(6)]
    for k,(x,y,w,h,n) in enumerate(stats[1:],1):
        if w>20 or h<15:continue
        side=0 if x<320 else 3
        row=int(np.argmin(abs(np.array([50,115,180])-y)))
        i=len(bodies);bodies.append(dict(bbox=[int(x),int(y),int(x+w),int(y+h)],centre=centres[k].tolist()))
        chains[side+row].append(i)
    data=dict(bodies=bodies,rows=[dict(components=ids) for ids in chains])
    pieces=[]
    for side in [0,3]:
        ids=chains[side+1];q=item([20+(320 if side else 0),112,309+(320 if side else 0),135])
        q['type_support_chains']=[dict(row=side+1,components=ids,observed=ids)]
        pieces.append(q)
    request=dict(bbox=[0,0,640,250])
    out,audit=complete_request(gray,pieces,40,data,request,column_evidence=evidence)
    assert audit['band_calls']==1 and audit['targets']==2
    for k,q in enumerate(out):
        rec=next(r for r in audit['records'] if r['piece']==k)
        assert rec['status']=='completed between native separators', rec['status']
        m=mask(gray.shape,q);x=108+320*k
        assert m[101:105,x:x+5].all(), 'nearer upper descender must not steal detached target mark'
        assert not m[50:94,x-8:x-3].any()
        assert not np.any(m[:,319:322] & (gray[:,319:322]<100))
        assert not np.any(m[180:198] & (gray[180:198]<100))
    reverse,other=complete_request(gray,pieces[::-1],40,dict(data,rows=data['rows'][::-1]),request,column_evidence=evidence)
    assert [q['polygon'] for q in out]==[q['polygon'] for q in reverse[::-1]]
