"""Bare-source tests and adversarial mutations of the real B5 consumer."""
import os
os.environ.update({k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
import io,json,shutil,subprocess,sys,tarfile,time
from pathlib import Path
from .r8_ink02 import ROOT,OUT,dump,sha

def run(label,args,cwd,env,expected=0):
    t=time.perf_counter();r=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True)
    (OUT/(label+'.log')).write_text(r.stdout+r.stderr)
    rec=dict(label=label,exit_code=r.returncode,expected=expected,seconds=time.perf_counter()-t,command=args,tail=(r.stdout+r.stderr).splitlines()[-3:])
    assert r.returncode==expected,rec
    return rec

def main():
    target=OUT/'bare-checkout';target.mkdir(exist_ok=False)
    data=subprocess.check_output(['git','archive','HEAD','prototypes','greekocr','pyproject.toml'],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:archive.extractall(target)
    names=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    for name in names:
        if not name.startswith('prototypes/'):continue
        p=ROOT/name;q=target/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    assert not (target/'.astra').exists()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',FAST_LINES_FIELD_BACKEND='python');env.pop('FAST_LINES_FIELD_TEST_NATIVE',None);env.pop('FAST_LINES_FIELD_LIBRARY',None)
    records=[run('BARE_PYTHON',[sys.executable,'-m','pytest','-q','prototypes/fast_lines','-p','no:cacheprovider'],target,env)]
    lib=ROOT.parent/'greek-ocr-toolkit-ff-r8-stack/prototypes/fast_lines/rust_field/target/release/libfast_lines_field.dylib'
    if lib.exists():
        native=dict(env,FAST_LINES_FIELD_BACKEND='rust',FAST_LINES_FIELD_TEST_NATIVE='1',FAST_LINES_FIELD_LIBRARY=str(lib))
        records.append(run('BARE_NATIVE',[sys.executable,'-m','pytest','-q','prototypes/fast_lines','-p','no:cacheprovider'],target,native))
        records.append(dict(existing_native_library=str(lib),sha256=sha(lib),kernels_unchanged=True))
    source=target/'prototypes/fast_lines/shared/ink_ownership.py';original=source.read_text();mutations=[]
    changes={
        'old_arrays_current_metadata':("exemplar=list(observation.exemplars[m['reflected_id'] if m['margin']>0 else m['direct_id']].bbox)","exemplar=atlas[m['reflected_id'] if m['margin']>0 else m['direct_id']]['bbox']"),
        'per_query_rebuild':("(256 if route=='dense' else 64)),observation)","(256 if route=='dense' else 64)),glyph_atlas(atlas))"),
        'raw_membership_gate':("if i in suspects and observation:","if i in suspects and atlas:"),
    }
    for name,(old,new) in changes.items():
        assert original.count(old)==1;source.write_text(original.replace(old,new))
        try:
            rec=run('MUTATION_'+name,[sys.executable,'-m','pytest','-q','prototypes/fast_lines/shared/test_ink_atlas_contract.py','-p','no:cacheprovider'],target,env,1)
            log=(OUT/('MUTATION_'+name+'.log')).read_text();failed=[line for line in log.splitlines() if line.startswith('FAILED ')]
            assert any('test_b5_native_witnesses_use_the_scored_snapshot' in line for line in failed)
            if name=='per_query_rebuild':assert any('test_b5_builds_once_for_multiple_requested_regions_and_refreshes' in line for line in failed)
            mutations.append(dict(name=name,target_matches=1,source_sha256=sha(source),failures=failed,record=rec))
        finally:source.write_text(original)
    dump(OUT/'VERIFICATION.json',dict(records=records,mutations=mutations,bare_no_astra=True,fixture_files={p.name:sha(p) for p in (target/'prototypes/fast_lines/shared/fixtures').glob('ink_atlas_native.*')}))
    print('verification complete',records,flush=True)
if __name__=='__main__':main()
