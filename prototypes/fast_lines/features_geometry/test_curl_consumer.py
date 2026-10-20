"""Native consumer witnesses; i1 replay is withdrawn, i2 separator uses local frames."""
import json
from pathlib import Path
import cv2
import numpy as np
import pytest
from ..shared.geometry_envelopes import correct
from ..shared.geometry_bands import crop_mask
from ..shared.type_barriers import protect
from ..shared.type_residual_recovery import field

HERE=Path(__file__).parent


def fixture(name):
    return np.load(HERE/(name+'.npz'))['gray'],json.loads((HERE/(name+'.json')).read_text())


def test_seedless_native_residual_field_reports_the_missing_row():
    gray,d=fixture('curl_missing_row_native')
    h,w=gray.shape
    result=field(gray,[],dict(bbox=[0,0,w,h]),d['height'],[],version=4)
    # τρου ... belongs to saved slow row 5, witnessed independently in the
    # photograph at native y=621..674. Empty seeds do not mean blank paper.
    a,b=d['native_origin'];matches=[r for r in result['rows'] if
        abs((r['bbox'][1]+r['bbox'][3])/2+b-647.5)<15 and
        r['bbox'][0]+a<650 and r['bbox'][2]+a>1350]
    assert matches and len(matches[0]['free'])>=20


def missing_row_v2():
    gray,old=fixture('curl_missing_row_native')
    d=json.loads((HERE/'curl_missing_row_native_v2.json').read_text())
    origin=np.asarray(d['native_origin'])
    for key in ('polygon','type_witness_points'):
        assert np.allclose(np.asarray(d['item'][key])+origin,d['absolute_item'][key])
    assert np.allclose(np.asarray(d['item']['type_support_bounds'])+origin[0],
                       d['absolute_item']['type_support_bounds'])
    assert d['item']['type_support_bounds']==[21.25,1442.75]
    return gray,d


def test_missing_row_proposal_survives_its_actual_separator():
    from ..shared.type_residual_recovery import supported_extent,piece_support
    gray,d=missing_row_v2();q=supported_extent(d['item'])
    pieces,decisions=protect(gray,q,d['height'])
    assert len(pieces)==1 and piece_support(pieces[0],q['type_witness_points'],[],d['height'])
    assert decisions[0]['decision']=='local unknown' and decisions[0]['retained_sides']==['left']
    # The native body is retained; the unverified corridor and risen νων remain unknown.
    mask=crop_mask(gray.shape,pieces[0])>0
    for x,y in np.rint(q['type_witness_points']).astype(int):
        assert mask[y,x]
    assert not mask[:,1390:1403].any()
    assert mask[207,60] and mask[211,857], 'returned body raster lost its own ink'


def native_compose(monkeypatch):
    from ..shared import type_residual_recovery as residual
    from ..stack.pipeline import compose
    gray,d=missing_row_v2();height,width=gray.shape
    class Detector:
        def infer(self,crop,side=960):
            return None,dict(tensor=[1,3,*crop.shape])
    # Only the model/request boundary is replayed. Native field, source,
    # protect, piece_support, completion and all final compose stages execute.
    monkeypatch.setattr(residual,'requests',lambda *args:[dict(
        bbox=[0,0,width,height],id='native fixture',derivation=[],dependencies=[])])
    monkeypatch.setattr(residual,'postprocess',lambda *args,**kw:[d['item']])
    result=compose(gray,np.zeros((64,256),np.float32),d['compose_initial'],Detector())
    final=[q for q in result['items'] if q.get('type_residual') is not None]
    mask=crop_mask(gray.shape,final[0])>0 if final else np.zeros(gray.shape,bool)
    assert not mask[:,1396:1403].any(),'unverified corridor acquired'
    # Actual upper/lower row strips survive the new discovery unchanged.
    for before in d['compose_initial']:
        assert any(q['polygon']==before['polygon'] for q in result['items'])
    return gray,d,mask


def test_native_missing_body_reaches_real_recovery_and_final_compose(monkeypatch):
    gray,d,mask=native_compose(monkeypatch)
    own=np.load(HERE/'curl_missing_row_witness_mask_v2.npz')['mask']
    assert own.sum()==d['witness_mask_contract']['pixels']
    assert np.array_equal(np.where(mask,gray,255)[own],gray[own]),'witnessed whole native body component cut'


@pytest.mark.xfail(strict=True,reason='CURL i2: regional proposal already clips tall/touching observed components beyond the 24 witnessed body chain; no whole-line extent certificate')
def test_missing_body_all_initial_polygon_observations_are_whole(monkeypatch):
    gray,d,mask=native_compose(monkeypatch)
    observed=np.load(HERE/'curl_missing_row_body_mask_v2.npz')['mask']
    assert np.array_equal(np.where(mask,gray,255)[observed],gray[observed])


@pytest.mark.xfail(strict=True,raises=AssertionError,reason='CURL closed PARTIAL3/3: source37 end not retained through default consumer; no complete-end claim')
def test_shared_curved_end_is_whole_in_its_actual_native_crop():
    gray,d=fixture('curl_m33_native');witness=np.load(HERE/'curl_end_witness_v3.npz')
    r=correct(gray,None,d['items'],d['original'],scout={'trigger':True},
              map_bands=d['map_bands'],field_cache={'evidence':d['field']})
    mask=crop_mask(gray.shape,r['items'][d['target']])>0
    assert mask[witness['own']].all(),'source37 end remains incomplete'
    assert not mask[witness['neighbor']].any(),'continued crop takes next-row print'


# 2026-10-14 correction: the archived replay leaked the last row's `shared`
# state and replaced in-anchor support. It is historical evidence, not a test
# of shared continuation quality. The desired physical end assertion stays open at CURL closure; it is not
# replaced by a passing assertion that the native end is still refused.


def overhang_v3():
    data=np.load(HERE/'curl_overhang_native_v3.npz')
    d=json.loads((HERE/'curl_overhang_native_v3.json').read_text())
    return data['gray'],data['own'],d


def test_unknown_side_bounds_agree_in_native_and_local_frames():
    gray,own,d=overhang_v3();origin=np.asarray(d['native_origin'])
    # Exact observation ROI stays inside the captured native context in both
    # frames. White outside this context is never read by either protect call.
    native=np.full((d['native_bounds'][3],d['native_bounds'][2]),255,np.uint8)
    native[origin[1]:,origin[0]:]=gray
    local,ld=protect(gray,d['item'],d['height'])
    absolute,ad=protect(native,d['absolute_item'],d['height'])
    assert len(local)==len(absolute)==1
    assert np.allclose(np.asarray(local[0]['polygon'])+origin,absolute[0]['polygon'])
    mask=crop_mask(gray.shape,local[0])>0
    assert mask[own].all(),'native body cut by admission hardening'
    left=d['item']['type_support_bounds'][0]
    assert not mask[:,:int(np.floor(left))].any(),'unsafe local overhang still claimed'


def test_unclipped_overhang_reaches_real_recovery_admission(monkeypatch):
    from ..shared import type_residual_recovery as residual
    gray,own,d=overhang_v3();height,width=gray.shape
    class Detector:
        def infer(self,crop,side=960):return None,dict(tensor=[1,3,*crop.shape])
    monkeypatch.setattr(residual,'requests',lambda *args:[dict(
        bbox=[0,0,width,height],id='unclipped native proposal',derivation=[],dependencies=[])])
    monkeypatch.setattr(residual,'postprocess',lambda *args,**kw:[d['item']])
    original_protect=residual.protect;received=[]
    def observed(g,q,h):
        received.append(q)
        return original_protect(g,q,h)
    monkeypatch.setattr(residual,'protect',observed)
    result=residual.recover(gray,d['initial'],Detector(),version=11,
        scout_evidence=dict(height=d['field_height'],regions=[dict(bbox=[0,0,width,height])]))
    assert received and min(p[0] for p in received[0]['polygon'])<received[0]['type_support_bounds'][0], 'setup pre-clipped the proposal and hid the bypass'
    mask=np.zeros(gray.shape,bool)
    for q in result['added']:mask|=crop_mask(gray.shape,q)>0
    assert np.array_equal(np.where(mask,gray,255)[own],gray[own]),'returned raster clips the witnessed body'
    left=received[0]['type_support_bounds'][0]
    # supported_extent retains the inherited integer polygon raster convention.
    unsafe=np.indices(gray.shape)[1]<np.floor(left)
    assert not mask[unsafe].any(),'returned raster still includes unsupported overhang'


@pytest.mark.parametrize('bounds',[None,[],[float('nan'),100],[100,20],['0','100']])
def test_invalid_unknown_side_bounds_do_not_invent_admission_limits(bounds):
    gray,own,d=overhang_v3();q=dict(d['item'],type_support_bounds=bounds)
    pieces,_=protect(gray,q,d['height'])
    assert len(pieces)==1 and min(p[0] for p in pieces[0]['polygon'])==min(p[0] for p in q['polygon'])
