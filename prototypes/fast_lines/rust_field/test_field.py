"""Committed numerical and true render/certify consumer qualification.

Native comparisons are opt-in; explicit native qualification never skips a build.
"""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
from . import Batch, shifts_python
from . import fixture_data
from ..shared import geometry_page_field as gf

HERE=Path(__file__).parent
NATIVE=os.environ.get('FAST_LINES_FIELD_TEST_NATIVE')=='1' or os.environ.get('FAST_LINES_FIELD_BACKEND')=='rust'
backends=pytest.mark.parametrize('backend',['python','rust'] if NATIVE else ['python'])


def equal(actual,expected):
    for name,a,b in zip(['delta','weight','scores'],actual,expected):
        if not np.array_equal(a.view(np.uint64),b.view(np.uint64)):
            i=tuple(np.argwhere(a.view(np.uint64)!=b.view(np.uint64))[0]);pytest.fail(f'first differing {name}{i}: {a[i].hex()} != {b[i].hex()}')


def args(d):
    return [d[k] for k in ['before','moved','columns']]


@backends
@pytest.mark.parametrize('fixture',json.loads((HERE/'fixtures/manifest.json').read_text())['batches'],ids=lambda q:q['file'])
def test_committed_actual_batches(backend,fixture):
    d=fixture_data.batch(fixture)
    a=Batch(*(d[k] for k in ['profiles','ys','lag','lengths']),backend=backend)
    result=a.shifts_many(*args(d),energy=d.get('energy'),diagnostic=True)
    expected=shifts_python(*args(d),*(d[k] for k in ['profiles','ys','lag','lengths']),d.get('energy'),diagnostic=True)
    equal(result,expected)


def case(w=41,constant=False,shift=0.):
    ys=np.arange(101,dtype=float)
    base=np.ones(len(ys)) if constant else np.exp(-((ys-35)/4)**2)+.6*np.exp(-((ys-67)/6)**2)
    profiles=np.stack([base,np.interp(ys-shift,ys,base,left=0,right=0)],axis=1).astype(np.float32)
    lag=np.linspace(-3,3,25);lengths=np.array([w,max(0,w-7),min(w,3)])
    window=np.stack([np.linspace(20,80,w)]*3);valid=np.arange(w)[None,:]<lengths[:,None]
    before=np.interp(window,ys,profiles[:,0]);before=np.where(valid,before-(before*valid).sum(-1,keepdims=True)/np.maximum(lengths,1)[:,None],0)
    return profiles,ys,lag,lengths,before[None],window[None]


@backends
@pytest.mark.parametrize('w,constant,shift',[(1,False,0),(4,False,0),(8,False,1),(41,False,-1.25),(140,False,2),(280,False,-2),(41,True,0)])
def test_short_constant_straight_and_known_shifts(backend,w,constant,shift):
    p,y,l,n,b,m=case(w,constant,shift)
    a=Batch(p,y,l,n,backend=backend).shifts_many(b,m,[1],diagnostic=True)
    expected=shifts_python(b,m,[1],p,y,l,n,diagnostic=True);equal(a,expected)
    assert np.all(a[0][:,n<5]==0) and np.all(a[1][:,n<5]==0)
    if constant and w>=5:assert a[0][0,0]==l[0] and a[1][0,0]==0 # first-maximum tie
    if not constant and w>=41:assert abs(a[0][0,0]-shift)<.03


@backends
def test_endpoints_and_border_and_near_tie(backend):
    # Integer endpoints and adjacent floats cannot be silently zeroed or clamped.
    y=np.arange(10,dtype=float);p=np.array([[1,0,3,2,5,4,7,6,9,8],[0,2,1,4,3,6,5,8,7,10]],float).T
    l=np.array([-np.finfo(float).eps,0.,np.finfo(float).eps]);n=np.array([6]);m=np.array([[[-1.,0.,np.nextafter(0.,1.),9.,np.nextafter(9.,10.),10.]]]);b=np.array([[[1.,-2.,3.,-4.,5.,-3.]]])
    result=Batch(p,y,l,n,backend=backend).shifts_many(b,m,[1],diagnostic=True)
    equal(result,shifts_python(b,m,[1],p,y,l,n,diagnostic=True))


@backends
@pytest.mark.parametrize('path',sorted((HERE/'fixtures').glob('*-render.json')),ids=lambda p:p.stem)
def test_real_render_through_certify(monkeypatch,backend,path):
    d,data=fixture_data.render(path)
    source=dict(d['source'],density=np.zeros((1,1)));gray=np.zeros(d['gray_shape'],np.uint8)
    profiles=iter([data[f'profiles{i}'] for i in range(len(data))])
    monkeypatch.setattr(gf.cv2,'remap',lambda *a,**kw:next(profiles).copy())
    # Prepared photometry from this exact call; body/seed/scale/certify run normally.
    monkeypatch.setattr(gf,'prepare',lambda *a,**kw:source)
    from .. import rust_field
    monkeypatch.setattr(rust_field,'BACKEND',backend)
    previous=dict(rust_field.COUNTERS)
    result=gf.render(gray,d['items'],route='slow')
    delta={key:rust_field.COUNTERS[key]-previous[key] for key in ('python','rust','fallback')}
    assert delta[backend]>0, f'{backend} backend was bypassed: {delta}'
    assert delta['rust' if backend=='python' else 'python']==0, delta
    assert delta['fallback']==0, delta
    result.pop('seconds')
    assert result==d['expected']
    assert any('mesh' in f for f in result['fields'])
    assert all('certificate' in f for f in result['fields'] if f.get('rows'))


def test_missing_native_fails_at_explicit_import(tmp_path):
    env=dict(os.environ,FAST_LINES_FIELD_BACKEND='rust',FAST_LINES_FIELD_LIBRARY=str(tmp_path/'missing.so'))
    r=subprocess.run([sys.executable,'-c','from prototypes.fast_lines import rust_field'],env=env,capture_output=True,text=True)
    assert r.returncode!=0 and 'Explicit M15 Rust backend needs a usable build' in r.stderr



def test_valid_mask_mutation_at_real_render_consumer(monkeypatch):
    path=next((HERE/'fixtures').glob('*86865*-render.json'));d,data=fixture_data.render(path)
    source=dict(d['source'],density=np.zeros((1,1)));gray=np.zeros(d['gray_shape'],np.uint8)
    profiles=iter([data[f'profiles{i}'] for i in range(len(data))])
    monkeypatch.setattr(gf.cv2,'remap',lambda *a,**kw:next(profiles).copy())
    monkeypatch.setattr(gf,'prepare',lambda *a,**kw:source)
    original=Batch.shifts_many
    def changed(self,before,moved,columns,energy=None,**kw):
        old=self.lengths;old_native=getattr(self,'native_lengths',None)
        try:
            self.lengths=np.full_like(old,moved.shape[-1]);self.valid=(np.ones((len(old),moved.shape[-1]),bool),self.lengths)
            if old_native is not None:self.native_lengths=self.array(self.lengths,np.int64)
            return original(self,before,moved,columns,energy,**kw)
        finally:
            if old_native is not None:self.native_lengths=old_native
            self.lengths=old;self.valid=(np.arange(moved.shape[-1])[None,:]<old[:,None],np.maximum(old,1))
    monkeypatch.setattr(Batch,'shifts_many',changed)
    result=gf.render(gray,d['items']);result.pop('seconds')
    assert result!=d['expected']


@backends
def test_empty_render_has_no_numeric_entries(monkeypatch,backend):
    from .. import rust_field
    monkeypatch.setattr(rust_field,'BACKEND',backend)
    monkeypatch.setattr(gf,'prepare',lambda *a,**kw:dict(density=np.zeros((32,32)),scale=[1,1],components=[]))
    previous=dict(rust_field.COUNTERS)
    r=gf.render(np.full((32,32),255,np.uint8),[])
    assert r['fields']==[] and rust_field.COUNTERS==previous


@backends
def test_selector_bypass_fails_real_consumer_entry_assertion(monkeypatch,backend):
    # In Python-only qualification a dropped call is caught without a library.
    # Native qualification forces the numerically identical Python path: output
    # parity still holds, but the real render's native-entry assertion must fail.
    from .. import rust_field
    path=next((HERE/'fixtures').glob('*86865*-render.json'))
    original=rust_field.Batch.shifts_many
    def bypass(self,*a,**kw):
        if backend=='rust':
            self.backend='python'
            return original(self,*a,**kw)
        before=dict(rust_field.COUNTERS)
        result=original(self,*a,**kw)
        rust_field.COUNTERS.update(before)
        return result
    monkeypatch.setattr(rust_field.Batch,'shifts_many',bypass)
    with pytest.raises(AssertionError,match=backend+' backend was bypassed'):
        test_real_render_through_certify(monkeypatch,backend,path)
