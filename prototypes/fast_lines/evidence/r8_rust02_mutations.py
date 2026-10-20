# Sequential native mutations, scheduled only after corpus comparison finishes.
from pathlib import Path
import shutil,subprocess,os,json,sys
ROOT=Path.cwd();O=ROOT/'.astra/fast_lines/out/round8/R8-RUST-02-i1';src=ROOT/'prototypes/fast_lines/rust_field';text=(src/'src/lib.rs').read_text()
mutations={
'endpoint':('if x==xp[xp.len()-1] {return fp[fp.len()-1];}','if x==xp[xp.len()-1] {return 0.;}'),
'last_tie':('if s[j]>s[best]','if s[j]>=s[best]'),
'no_valid_mask':('let length=lengths[ki] as usize;','let length=w;')}
results=[]
for name,(old,new) in mutations.items():
 assert text.count(old)==1
 p=O/'mutations'/name;p.mkdir(parents=True,exist_ok=True);(p/'src').mkdir(exist_ok=True)
 for f in ['Cargo.toml','Cargo.lock']:shutil.copyfile(src/f,p/f)
 (p/'src/lib.rs').write_text(text.replace(old,new))
 r=subprocess.run(['cargo','build','--manifest-path',str(p/'Cargo.toml'),'--release','--locked','--offline','-j','1'],capture_output=True,text=True);(p/'BUILD.log').write_text(r.stdout+r.stderr);assert r.returncode==0
 env=dict(os.environ,FAST_LINES_FIELD_BACKEND='rust',FAST_LINES_FIELD_TEST_NATIVE='1',FAST_LINES_FIELD_LIBRARY=str(p/'target/release/libfast_lines_field.dylib'))
 r=subprocess.run([sys.executable,'-m','pytest','-q','prototypes/fast_lines/rust_field/test_field.py','-k','not missing_native and not mutations'],env=env,capture_output=True,text=True)
 (p/'TEST.log').write_text(r.stdout+r.stderr);results.append(dict(mutation=name,killed=r.returncode==1,exit_code=r.returncode,summary=r.stdout.splitlines()[-1]));print(results[-1],flush=True)
(O/'MUTATIONS.json').write_text(json.dumps(results,indent=1)+'\n');assert all(r['killed'] for r in results)
