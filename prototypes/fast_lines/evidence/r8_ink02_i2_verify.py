"""Bare-checkout and surviving-mutant qualification; no ignored fixture inputs."""
import io,json,os,shutil,subprocess,tarfile,time
from pathlib import Path
from .r8_ink02_i2 import ROOT,O,dump,sha,sources
P=ROOT.parent/'greek-ocr-toolkit/.venv/bin/python';BASE=Path('/private/tmp/ink02-i2-bare');env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',NUMEXPR_NUM_THREADS='1',FAST_LINES_FIELD_BACKEND='python')
def run(label,root,args,extra=None):
 t=time.perf_counter();r=subprocess.run([str(P),'-m','pytest',*args,'-p','no:cacheprovider'],cwd=root,env=dict(env,**(extra or {})),capture_output=True,text=True);log=O/(label+'.log');log.write_text(r.stdout+r.stderr);return dict(label=label,exit_code=r.returncode,command=[str(P),'-m','pytest',*args,'-p','no:cacheprovider'],seconds=time.perf_counter()-t,log=str(log.relative_to(O)),log_sha256=sha(log),tail=(r.stdout+r.stderr).splitlines()[-4:])
def main():
 if BASE.exists():shutil.rmtree(BASE)
 data=subprocess.check_output(['git','archive','HEAD','prototypes'],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(data)) as tar:
  assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in tar.getmembers())
  tar.extractall(BASE)
 for relative in ['prototypes/fast_lines/shared/ink_photometry.py','prototypes/fast_lines/shared/test_ink_atlas_contract.py']:
  shutil.copy2(ROOT/relative,BASE/relative)
 records=[run('SUITE_PYTHON',ROOT,['-q','prototypes/fast_lines']),run('BARE_PYTHON',BASE,['-q','prototypes/fast_lines'])]
 lib=ROOT.parent/'greek-ocr-toolkit-ff-r8-stack/prototypes/fast_lines/rust_field/target/release/libfast_lines_field.dylib';assert sha(lib)=='3c20ffbf1342065976c8e11dd2c05518613adf45409a78bd94a2dab6946f6746'
 records.append(run('BARE_NATIVE',BASE,['-q','prototypes/fast_lines'],dict(FAST_LINES_FIELD_LIBRARY=str(lib),FAST_LINES_FIELD_TEST_NATIVE='1')))
 assert all(r['exit_code']==0 for r in records)
 photo=Path('prototypes/fast_lines/shared/ink_photometry.py');owner=Path('prototypes/fast_lines/shared/ink_ownership.py');original={photo:(BASE/photo).read_text(),owner:(BASE/owner).read_text()};targets='prototypes/fast_lines/shared/test_ink_atlas_contract.py'
 changes=[('exposed_owning_arrays',photo,lambda s:s.replace("'vectors',vectors.view()","'vectors',vectors").replace("'aspects',aspects.view()","'aspects',aspects")),('raw_empty_input_escape',photo,lambda s:s.replace("    if not isinstance(atlas,GlyphAtlas):raise TypeError('matcher requires glyph_atlas observation')\n",'')),('unsealed_independent_parts',photo,lambda s:s.replace("        raise TypeError('use glyph_atlas(selected_glyphs), not independent atlas parts')","        for name,value in zip(('vectors','aspects','exemplars'),args):object.__setattr__(self,name,value)\n        for name,value in kwargs.items():object.__setattr__(self,name,value)")),('removed_structure_validation',photo,lambda s:s[:s.index('        if vectors.shape!=')]+s[s.index('        # A read-only owned base'):]),('aspect_dtype_drift',photo,lambda s:s.replace("np.array([g['aspect'] for g in census],np.float64)","np.array([g['aspect'] for g in census])")),('old_arrays_current_metadata',owner,lambda s:s.replace("list(observation.exemplars[m['reflected_id'] if m['margin']>0 else m['direct_id']].bbox)","list(atlas[m['reflected_id'] if m['margin']>0 else m['direct_id']]['bbox'])")),('per_query_rebuild',owner,lambda s:s.replace('        if i in suspects and observation:\n','        if i in suspects and observation:\n            observation=glyph_atlas(atlas)\n'))]
 mutations=[]
 for name,path,change in changes:
  mutated=change(original[path]);assert mutated!=original[path];(BASE/path).write_text(mutated)
  receipt=run('MUTATION_'+name,BASE,['-q',targets]);receipt.update(name=name,mutated_file=str(path),mutated_sha256=sha(BASE/path));assert receipt['exit_code']==1,receipt
  receipt['failures']=[l for l in (O/receipt['log']).read_text().splitlines() if l.startswith('FAILED ')];mutations.append(receipt);(BASE/path).write_text(original[path]);print('mutant',name,len(receipt['failures']),'fails',flush=True)
 dump(O/'VERIFICATION.json',dict(source=sources(ROOT),records=records,mutations=mutations,bare_archive_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),ignored_captures_absent=not (BASE/'.astra').exists(),native_library=dict(path=str(lib),sha256=sha(lib),unchanged=True),fixture=dict(path='prototypes/fast_lines/shared/fixtures/ink_atlas_native.png',sha256=sha(ROOT/'prototypes/fast_lines/shared/fixtures/ink_atlas_native.png'),reused=True,new_fixture_bytes=0)))
if __name__=='__main__':main()
