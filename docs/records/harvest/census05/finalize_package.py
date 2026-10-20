"""Certify source blobs, additive payload and deployment bytes; no version edits."""
import difflib,hashlib,json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];S='3b4090bf9b15d2d2cac53ee55161e936157ec0e5'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def blob(path):return subprocess.check_output(['git','show',S+':'+path])
def main():
 prov=json.loads((D/'package_provenance.json').read_text())
 # The unchanged schema is a CODE_SHA byte copy, outside package/projects.
 source='docs/records/harvest/seg_census/split_input.schema.json';target=D/'split_input.schema.json'
 assert target.read_bytes()==blob(source)
 tree=subprocess.check_output(['git','ls-tree',S,'--',source]).decode().strip();oid=tree.split()[2]
 if not any(x['package_path']==str(target.relative_to(R)) for x in prov['files']):prov['files'].append(dict(source_path=source,package_path=str(target.relative_to(R)),bytes=target.stat().st_size,sha256=sha(target),git_blob=oid,git_ls_tree=tree))
 prov['files']=sorted(prov['files'],key=lambda x:x['source_path']);dump(D/'package_provenance.json',prov)
 for x in prov['files']:
  assert sha(R/x['package_path'])==x['sha256']
  assert (R/x['package_path']).read_bytes()==subprocess.check_output(['git','cat-file','blob',x['git_blob']])
 (D/'PROJECTS_SHA256').write_text(''.join(x['sha256']+'  '+x['source_path']+'\n' for x in prov['files']))
 paths=[R/x['package_path'] for x in prov['files']]
 extra=[D/'census05_config.json',D/'prepare_config.py',D/'parity_check.py',D/'readout/census_readout.py',*sorted((D/'jobs').glob('*')),D/'parity/source_receipt.json',D/'readout/readout.sbatch']
 receipt=json.loads((D/'parity/source_receipt.json').read_text());extra += [D/'parity'/c['path'] for c in receipt['chunks']]
 paths=sorted(set(paths+extra));additive=[]
 origins={'prepare_config.py':'docs/harvest/seg_census/prepare_config.py','parity_check.py':'docs/harvest/seg_census/parity_check.py','census05_config.json':'docs/harvest/seg_census/census04_config.json'}
 for p in paths:
  if any(x['package_path']==str(p.relative_to(R)) for x in prov['files']):continue
  relative=str(p.relative_to(D));origin=origins.get(relative)
  if relative.startswith('jobs/') and p.name!='readout.sbatch':origin='docs/harvest/seg_census/jobs/'+p.name
  if relative in ['jobs/readout.sbatch','readout/readout.sbatch','readout/census_readout.py']:origin='CODE_SHA docs/records/harvest/census05/readout/'+('census_readout.py' if p.suffix=='.py' else 'readout.sbatch')
  if relative.startswith('parity/'):origin='SEG10 found-existing replay; exact lossless compression; attempt 3 custody'
  additive.append(dict(path=str(p.relative_to(R)),sha256=sha(p),bytes=p.stat().st_size,origin=origin))
 dump(D/'additive_files.json',additive)
 raw=''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in paths)
 (D/'DEPLOY_SHA256SUMS').write_text(raw);(D/'DEPLOY_PATHS.txt').write_text(''.join(str(p.relative_to(R))+'\n' for p in paths))
 digest=hashlib.sha256(raw.encode()).hexdigest();pid=digest[:16]
 dump(D/'package_id.json',dict(package_id=pid,package_hash=pid,deploy_manifest_sha256=digest,deploy_files=len(paths),code_sha_identical=len(prov['files']),additive=len(additive),code_sha=S))
 # Every derivative diff is reviewable, including the mock's test-I/O boundary.
 diffs=[]
 for new,old in [('prepare_config.py','prepare_config.py'),('parity_check.py','parity_check.py'),('mock_batch.py','mock_batch.py')]+[('jobs/'+n,'jobs/'+n) for n in ['common.sh','regression.sbatch','parity.sbatch','census.sbatch']]:
  before=(D.parent/'seg_census'/old).read_text();after=(D/new).read_text();diffs.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='census04/'+old,tofile='census05/'+new))
 (D/'additive_changes.patch').write_text(''.join(diffs))
 patches=[]
 for rel in ['readout/census_readout.py','readout/readout.sbatch','readout/test_census_readout.py']:
  source='docs/records/harvest/census05/'+rel;before=blob(source).decode();after=(D/rel).read_text()
  patches.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+source,tofile='b/'+source))
 (D/'readout_version.patch').write_text(''.join(patches))
 print(json.dumps(dict(package_id=pid,files=len(paths),CODE_SHA_identical=len(prov['files']),additive=len(additive))))
if __name__=='__main__':main()
