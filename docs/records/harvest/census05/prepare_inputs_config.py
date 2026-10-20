"""Bind regenerated inputs and document every config field change."""
from copy import deepcopy
import difflib,gzip,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 report=json.loads((D/'corrections/report.json').read_text());old=json.loads((D.parent/'seg_census/census04_config.json').read_text());new=deepcopy(old)
 for k,suffix in [('codec','greekocr/_vendor/codec/v2.json'),('versions','docs/harvest/line_pipeline/tool_versions.json')]:new[k]='@CENSUS05_PROJECTS@/greek-ocr-toolkit-pipe032/'+suffix
 new['component_roots']={p.name:'@CENSUS05_PROJECTS@/'+p.name for p in (D/'package/projects').iterdir() if p.is_dir()}
 new['routes_out_of_scope']=['polytonic'];new['corrections']=[];inputs=[]
 for release in report['releases']:
  out={k:v for k,v in release.items() if k!='local_path'}
  if release['tool']=='numerics':
   path=Path(release['local_path']);out['path']=W+'/inputs/'+path.name
   inputs.append(dict(local_path=str(path),remote_path=out['path'],sha256=sha(path),bytes=path.stat().st_size,kind='regenerated_numerics'))
  new['corrections'].append(out)
 assert new['frozen_05']==old['frozen_05'];assert new['parents']==old['parents'];assert new['metadata']==old['metadata'];assert new['final_policy']==old['final_policy']
 dump(D/'census05_config.json',new)
 fields=[]
 for key in sorted(set(old)|set(new)):
  if old.get(key)!=new.get(key):fields.append(dict(field=key,before=old.get(key),after=new.get(key)))
 dump(D/'config_diff.json',fields)
 (D/'config_diff.patch').write_text(''.join(difflib.unified_diff((json.dumps(old,indent=2)+'\n').splitlines(True),(json.dumps(new,indent=2)+'\n').splitlines(True),fromfile='census04_config.json',tofile='census05_config.json')))
 split=json.loads((D/'input_audit.json').read_text())['split'];inputs.append(dict(local_path=split['path'],remote_path=W+'/inputs/row_split.jsonl.gz',sha256=split['sha256'],bytes=split['bytes'],kind='finalized_split_not_packaged'))
 archive=D/'corrections/archives';archive.mkdir(exist_ok=True);archives=[]
 for inp in inputs:
  if inp['kind']!='regenerated_numerics':continue
  chunks=[];buf=bytearray();n=0
  def flush():
   nonlocal buf,n
   if not buf:return
   n+=1;p=archive/(Path(inp['local_path']).stem+'.part%02d.jsonl.gz'%n)
   with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(buf)
   assert p.stat().st_size<5_000_000
   chunks.append(dict(path=str(p.relative_to(D)),sha256=sha(p),bytes=p.stat().st_size,uncompressed_bytes=len(buf)));buf=bytearray()
  with Path(inp['local_path']).open('rb') as f:
   for line in f:
    if len(buf)+len(line)>15_000_000:flush()
    buf.extend(line)
  flush();h=hashlib.sha256()
  for c in chunks:h.update(gzip.decompress((D/c['path']).read_bytes()))
  assert h.hexdigest()==inp['sha256'];archives.append(dict(**inp,chunks=chunks))
 dump(D/'corrections/archive_receipt.json',archives);dump(D/'INPUTS.json',inputs)
 (D/'INPUTS_SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['remote_path'].split('/inputs/')[1]+'\n' for x in inputs))
 print('config fields changed:',[f['field'] for f in fields],'; input archives:',sum(len(x['chunks']) for x in archives))
if __name__=='__main__':main()
