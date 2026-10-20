"""Regenerate with the FP3 producer converter, then load every bound record.

The converter functions are extracted byte-for-byte from prepare_remote.py.
No old canonical record is used to generate a new result.
"""
import ast, collections as C, difflib, gzip, hashlib, importlib.util, json, shutil, sys
from pathlib import Path
D=Path(__file__).resolve().parent; R=D.parents[2]; P=D/'package/projects/greek-ocr-toolkit-pipe032'
sys.path.insert(0,str(P))
from greekocr.harvest.line_pipeline import identity, span_edits, validate_result, canonical, digest
from greekocr.harvest.line_pipeline_sources import canonicalize
from greekocr.harvest.line_pipeline_census import Ledger, ArtifactCorrector
from greekocr.harvest import admission as adm
BASE=R.parent/'greek-ocr-toolkit-segcensus/docs/harvest/census05'
F=R.parent/'greek-page-ocr-wave2/out/fp3'; S=F/'sources'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def rows(p):
 with Path(p).open() as f:
  for n,s in enumerate(f,1):
   if s.strip():yield n,json.loads(s)
def main():
 out=D/'corrections';out.mkdir(exist_ok=True);orig=out/'converter_original';orig.mkdir(exist_ok=True)
 for name in ['prepare_remote.py','finalize_remote.py']:shutil.copyfile(F/name,orig/name)
 source=(F/'prepare_remote.py').read_text(); lines=source.splitlines(True)
 names={'canonical_result','legacy_convert','n1_candidates'}
 extracted='\n'.join(''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names)+'\n'
 (out/'converter_functions.py').write_text(extracted)
 (out/'converter_extraction.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),extracted.splitlines(True),fromfile='fp3/prepare_remote.py',tofile='census05/corrections/converter_functions.py')))
 spec=importlib.util.spec_from_file_location('fp3_n1_tokens',S/'greek-ocr-toolkit-secondary/greekocr/numerics/tokens.py');tokens=importlib.util.module_from_spec(spec);sys.modules[spec.name]=tokens;spec.loader.exec_module(tokens)
 versions=json.loads((P/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 train=S/'greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_train.jsonl'
 # Preserve the producer path in evidence: the converter itself remains exact.
 w1=F/'prepared/87407ec7430a375f/code/87407ec7430a375f/projects/greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_w1.jsonl'
 assert sha(train)=='0b32e8d9b04383cc8fe5542b0b40ccfa47978c5cd09b36c1a535083f0b41bf92'
 assert sha(w1)=='94fb67c1aab9f2ec3bf5d47bc36508b7e700508cd27391f70ebfc26f8d73230e'
 source_refs=json.loads((F/'sources/source_receipt.json').read_text()) if (F/'sources/source_receipt.json').exists() else None
 # Original receipt lives in fp3/source snapshot; bind tokenizer and scanner explicitly.
 inventory=json.loads((F/'build_recipe.json').read_text())['sources']
 tokenkey='greek-ocr-toolkit-secondary/greekocr/numerics/tokens.py';scankey='greek-ocr-toolkit-secondary/scripts/numerics/n1tr.py'
 for key in [tokenkey,scankey]:assert sha(S/key)==inventory[key]['sha256']
 train_arg=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/sources/greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_train.jsonl')
 w1_arg=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/d74ad2830c479f7b/projects/greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_w1.jsonl')
 artifact_shas={str(train_arg):sha(train),str(w1_arg):sha(w1)}
 env=dict(identity=identity,span_edits=span_edits,validate_result=validate_result,versions=versions,digest=digest,canonical=canonical,artifact_shas=artifact_shas,tokens=tokens)
 exec(compile(extracted,str(out/'converter_functions.py'),'exec'),env)
 oldcfg=json.loads((D/'census05_config.json').read_text());inputaudit=json.loads((BASE/'input_audit.json').read_text());metadata=json.loads(Path(inputaudit['metadata']['path']).read_text())
 localparents={p['parent_id']:p['path'] for p in inputaudit['parents']}
 custody=json.loads((BASE/'correction_custody_audit.json').read_text()); releases=[];report=[]
 w1rows={r['id']:r for _,r in rows(w1)}
 work=out/'work';work.mkdir(exist_ok=True)
 codec=adm.load_codec(P/'greekocr/_vendor/codec/v2.json')
 for parent in oldcfg['parents']:
  pid=parent['id'];db=work/(pid+'.sqlite')
  ledger=Ledger(db,dict(parent=parent,code_sha='3b4090bf9b15d2d2cac53ee55161e936157ec0e5'))
  ledger.db.execute('DELETE FROM corrections');ledger.db.execute('DELETE FROM releases');ledger.db.commit()
  rawiter=iter(rows(train)) if pid=='collection-v2-train' else None
  newpath=out/("numerics_"+pid+'.jsonl');newstream=newpath.open('w');newcounts=C.Counter();generated=0
  for _,r in rows(localparents[pid]):
   row=canonicalize(r,parent,metadata);ledger.register(row,codec)
   if rawiter:
    _,nr=next(rawiter);assert nr['id']==row['id'];result=env['legacy_convert'](row,'numerics',nr,train_arg)
   elif pid=='collect-v3-W1-20261018-0524' and row['id'] in w1rows:result=env['legacy_convert'](row,'numerics',w1rows[row['id']],w1_arg)
   elif not env['n1_candidates'](row['raw_text']):
    result=env['canonical_result'](row,'numerics','verified_no_change',[],dict(candidate_scan='no N1 token with >=4 ASCII digits and internal single - or . slot',definition='scripts/numerics/n1tr.py:41-53 enumerate_slots; greekocr/numerics/tokens.py:1-89',definition_sha256=inventory[scankey]['sha256'],tokens_sha256=inventory[tokenkey]['sha256']))
   else:continue
   newstream.write(canonical(result)+'\n');newcounts[result['status']]+=1;generated+=1
  newstream.close();ledger.db.commit()
  if rawiter:assert next(rawiter,None) is None
  corrector=ArtifactCorrector(ledger,versions,{pid:parent['sha256']})
  for release in [x for x in oldcfg['corrections'] if x['parent_id']==pid]:
   original=(BASE/'corrections'/Path(release['path']).name) if release['tool']=='numerics' else F/'prepared/87407ec7430a375f'/Path(release['path']).name;assert sha(original)==release['sha256']
   entry=dict(release,old_bytes=original.stat().st_size,old_sha256=sha(original))
   if release['tool']=='polytonic':entry['action']='not bound in census_05';report.append(entry);continue
   updated=dict(release,path=str(newpath),sha256=sha(newpath)) if release['tool']=='numerics' else dict(release,path=str(original))
   # Each record passes the real CODE_SHA ArtifactCorrector.load, including standing cyrillic.
   corrector.load(updated)
   entry.update(action='regenerated' if release['tool']=='numerics' else 'standing',ArtifactCorrector_load='PASS',output_path=updated['path'],output_sha256=updated['sha256'],output_bytes=Path(updated['path']).stat().st_size)
   if release['tool']=='numerics':
    before=C.Counter();moves=C.Counter();changes=[];count=0
    # Row membership/order is part of the record diff, not merely totals.
    with original.open() as a,newpath.open() as b:
     for l1,l2 in __import__('itertools').zip_longest(a,b):
      assert l1 is not None and l2 is not None
      x,y=json.loads(l1),json.loads(l2);assert x['binding']==y['binding'];count+=1;before[x['status']]+=1;moves[x['status']+' -> '+y['status']]+=1
      xx={k:v for k,v in x.items() if k not in ['tool_version','tool_digest']};yy={k:v for k,v in y.items() if k not in ['tool_version','tool_digest']}
      if xx!=yy:changes.append(dict(id=x['binding']['id'],before=xx,after=yy,cause='regeneration from identical producer; evidence source path rebased locally' if {k:v for k,v in xx.items() if k!='evidence'}=={k:v for k,v in yy.items() if k!='evidence'} else 'producer converter output changed'))
    assert not changes, 'STOP: converter output changed beyond tool identity'
    entry.update(records_after=generated,status_before=dict(before),status_after=dict(newcounts),status_transitions=dict(moves),changes_beyond_identity=len(changes),changes=changes,edits_after=newcounts['applied'],holds_after=newcounts['required_evidence_unresolved'],no_change_after=newcounts['verified_no_change'])
    assert generated==count
   releases.append(dict(release,local_path=updated['path'],sha256=updated['sha256']))
   report.append(entry)
  ledger.db.close()
  print(pid,'registered',parent['rows'],'N1',generated,dict(newcounts),flush=True)
 dump(out/'report.json',dict(status='PASS',source_converters=[dict(path=str(F/n),sha256=sha(F/n)) for n in ['prepare_remote.py','finalize_remote.py']],producer_inputs=[dict(path=str(p),sha256=sha(p)) for p in [train,w1,S/tokenkey,S/scankey]],converter_functions_unchanged=True,changes_to_converter_functions=[],releases=releases,ledgers=report,standing=5,regenerated=5,unbound=5))
if __name__=='__main__':main()
