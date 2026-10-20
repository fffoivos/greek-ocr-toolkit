"""Sequential clean-source/build and consumer/mutation qualification for i2."""
import os
os.environ.update({k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
import argparse, io, json, platform, shutil, subprocess, sys, tarfile, time
from pathlib import Path
from .r8_curl_trace import ROOT, FL, dump, sha
O=ROOT/'.astra/fast_lines/out/round8/R8-RUST-02-i2'
CRATE=ROOT/'prototypes/fast_lines/rust_field'

def run(label,command,cwd,env,expected=0):
    assert not (FL.parent/'METER_STOP').exists()
    start=time.perf_counter();r=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True)
    (O/(label+'.log')).write_text(r.stdout+r.stderr)
    record=dict(label=label,command=command,exit_code=r.returncode,expected=expected,seconds=time.perf_counter()-start,tail=(r.stdout+r.stderr).splitlines()[-3:])
    assert r.returncode==expected,record
    return record

def clean():
    target=O/'clean-checkout';assert not target.exists()
    target.mkdir();data=subprocess.check_output(['git','archive','HEAD','prototypes','greekocr','pyproject.toml'],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:archive.extractall(target)
    dest=target/'prototypes/fast_lines/rust_field'
    shutil.rmtree(dest/'fixtures');shutil.copytree(CRATE/'fixtures',dest/'fixtures')
    for name in ['test_field.py','fixture_data.py','README.md']:shutil.copyfile(CRATE/name,dest/name)
    assert not (target/'.astra').exists() and not (dest/'target').exists()
    env=dict(os.environ,FAST_LINES_FIELD_BACKEND='python');env.pop('FAST_LINES_FIELD_TEST_NATIVE',None);env.pop('FAST_LINES_FIELD_LIBRARY',None)
    records=[run('CLEAN_PYTHON',[sys.executable,'-m','pytest','-q','prototypes/fast_lines'],target,env)]
    missing=dict(env,FAST_LINES_FIELD_BACKEND='rust')
    records.append(run('CLEAN_NATIVE_MISSING',[sys.executable,'-c','from prototypes.fast_lines import rust_field'],target,missing,1))
    assert 'Explicit M15 Rust backend needs a usable build' in (O/'CLEAN_NATIVE_MISSING.log').read_text()
    home=O/'empty-cargo-home';home.mkdir();buildenv=dict(env,CARGO_HOME=str(home),RUSTFLAGS='')
    buildenv.pop('CARGO_TARGET_DIR',None)
    records.append(run('CLEAN_BUILD',['sh','prototypes/fast_lines/rust_field/build.sh'],target,buildenv))
    lib=dest/'target/release/libfast_lines_field.dylib'
    native=dict(env,FAST_LINES_FIELD_BACKEND='rust',FAST_LINES_FIELD_TEST_NATIVE='1',FAST_LINES_FIELD_LIBRARY=str(lib))
    records.append(run('CLEAN_NATIVE_TESTS',[sys.executable,'-m','pytest','-q','prototypes/fast_lines/rust_field'],target,native))
    dump(O/'CLEAN_CHECKOUT.json',dict(records=records,binary_sha256=sha(lib),rustc=subprocess.check_output(['rustc','-Vv'],text=True),cargo=subprocess.check_output(['cargo','-V'],text=True),platform=platform.platform(),dependencies=[],flags='release O3 thinLTO one codegen-unit; RUSTFLAGS empty; offline locked; empty CARGO_HOME',files={str(p.relative_to(CRATE)):sha(p) for p in [CRATE/'Cargo.lock',CRATE/'Cargo.toml',CRATE/'src/lib.rs',CRATE/'__init__.py']},bare_has_no_astra=True))

def mutations():
    text=(CRATE/'src/lib.rs').read_text();sumtext=text[text.index('fn sum('):text.index('fn interp(')]
    changes={'endpoint':('if x==xp[xp.len()-1] {return fp[fp.len()-1];}','if x==xp[xp.len()-1] {return 0.;}'),
        'last_tie':('if s[j]>s[best]','if s[j]>=s[best]'),
        'no_valid_mask':('let length=lengths[ki] as usize;','let length=w;'),
        'no_fma':('slope.mul_add(x-xp[j],fp[j])','slope*(x-xp[j])+fp[j]'),
        'sequential_sum':(sumtext,'fn sum(a: &[f64]) -> f64 {let mut s=-0.0; for &x in a {s+=x;} s}\n')}
    results=[]
    for name,(old,new) in changes.items():
        assert text.count(old)==1
        p=O/'mutations'/name;assert not p.exists();(p/'src').mkdir(parents=True)
        for file in ['Cargo.toml','Cargo.lock']:shutil.copyfile(CRATE/file,p/file)
        (p/'src/lib.rs').write_text(text.replace(old,new));env=dict(os.environ)
        record=run('MUTATION_'+name+'_BUILD',['cargo','build','--manifest-path',str(p/'Cargo.toml'),'--release','--locked','--offline','-j','1'],ROOT,env)
        env.update(FAST_LINES_FIELD_BACKEND='rust',FAST_LINES_FIELD_TEST_NATIVE='1',FAST_LINES_FIELD_LIBRARY=str(p/'target/release/libfast_lines_field.dylib'))
        test=run('MUTATION_'+name+'_TEST',[sys.executable,'-m','pytest','-q','prototypes/fast_lines/rust_field/test_field.py','-k','not missing_native and not selector_bypass'],ROOT,env,1)
        log=(O/('MUTATION_'+name+'_TEST.log')).read_text()
        results.append(dict(mutation=name,target_count=1,source_sha256=sha(p/'src/lib.rs'),binary_sha256=sha(p/'target/release/libfast_lines_field.dylib'),build=record,test=test,real_consumer_failed=any(line.startswith('FAILED ') and '::test_real_render_through_certify[' in line and '-rust]' in line for line in log.splitlines())))
        dump(O/'MUTATIONS.json',results)
    assert all(x['real_consumer_failed'] for x in results if x['mutation']!='last_tie')
    assert 'test_committed_actual_batches' in (O/'MUTATION_last_tie_TEST.log').read_text()

def entries():
    import pytest
    from .. import rust_field
    from ..rust_field.test_field import test_real_render_through_certify
    rows=[]
    for backend in ['python','rust']:
        for path in sorted((CRATE/'fixtures').glob('*-render.json')):
            before=dict(rust_field.COUNTERS)
            with pytest.MonkeyPatch.context() as monkeypatch:test_real_render_through_certify(monkeypatch,backend,path)
            delta={k:rust_field.COUNTERS[k]-before[k] for k in before}
            rows.append(dict(backend=backend,fixture=path.name,entries=delta,consumer_exact=True))
    dump(O/'CONSUMER_BACKENDS.json',rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['clean','mutations','entries']);a=p.parse_args();globals()[a.action]()
