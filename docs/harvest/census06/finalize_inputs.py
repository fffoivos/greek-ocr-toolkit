"""Bind regenerated numerics, keep all other census05 input fields unchanged."""
from pathlib import Path
import gzip,hashlib,json
D=Path(__file__).resolve().parent;BASE=D.parents[2].parent/'greek-ocr-toolkit-segcensus/docs/harvest/census05'
W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 base=json.loads((D/'census05_config.json').read_text());config=json.loads(json.dumps(base));report=json.loads((D/'corrections/report.json').read_text());assert report['status']=='PASS'
 inputs=[]
 versions=json.loads((D/'package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 for r in config['corrections']:
  if r['tool']=='numerics':
   path=D/'corrections'/Path(r['path']).name
   e=next(x for x in report['ledgers'] if x['parent_id']==r['parent_id'] and x['tool']=='numerics')
   assert e['changes_beyond_identity']==0 and sha(path)==e['output_sha256']
   r.update(path=W+'/census_06_20261020/inputs/'+path.name,sha256=sha(path))
   archive=D/'corrections/archives'/(path.name+'.gz');archive.parent.mkdir(exist_ok=True)
   with path.open('rb') as src,archive.open('wb') as dst:
    with gzip.GzipFile(filename='',mode='wb',fileobj=dst,mtime=0) as gz:
     __import__('shutil').copyfileobj(src,gz)
   inputs.append(dict(local_path=str(path),remote_path=r['path'],sha256=r['sha256'],bytes=path.stat().st_size,kind='regenerated_numerics',archive_path=str(archive),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size))
 config['routes_out_of_scope']=[]
 for key in ('codec','versions'):
  config[key]=config[key].replace('@CENSUS05_PROJECTS@','@CENSUS06_PROJECTS@')
 for parent in config['parents']:
  config['corrections'].append(dict(tool='polytonic',parent_id=parent['id'],parent_manifest_sha256=parent['sha256'],format='line-tool-result-v1',status='released',path='PENDING:sf7:'+parent['id'],sha256=None,tool_version=versions['polytonic']['version'],tool_digest=versions['polytonic']['digest'],binding_status='PENDING'))
  inputs.append(dict(kind='pending_sf7',parent_id=parent['id'],path=None,sha256=None,status='PENDING',tool_version=versions['polytonic']['version'],tool_digest=versions['polytonic']['digest']))
 # Same split bytes at new census06 input location; c05 remains untouched.
 split=next(x for x in json.loads((BASE/'INPUTS.json').read_text()) if x['kind']=='finalized_split_not_packaged');split['remote_path']=W+'/census_06_20261020/inputs/row_split.jsonl.gz';inputs.append(split)
 dump(D/'census06_config.json',config);dump(D/'INPUTS.json',inputs)
 changes={k:dict(reason={'codec':'relocation marker only','versions':'relocation marker and amended manifest','corrections':'five converter-regenerated numerics shas and five pending released SF7 full-row files','routes_out_of_scope':'polytonic in scope'}[k]) for k in set(base)|set(config) if base.get(k)!=config.get(k)}
 assert set(changes)=={'codec','versions','corrections','routes_out_of_scope'}
 assert [r for r in base['corrections'] if r['tool']=='cyrillic']==[r for r in config['corrections'] if r['tool']=='cyrillic']
 dump(D/'config_diff.json',dict(status='PASS',changed_keys=changes,unchanged_keys=sorted(k for k in base if base[k]==config.get(k)),cyrillic_bindings_identical=True,all_other_inputs_native_settings_policy_identical=True,authorized_amendment='pipeline 0.3.3 and readout/test additions; eight regenerated fingerprints and five regenerated numerics ledgers per final lead ruling'))
if __name__=='__main__':main()
