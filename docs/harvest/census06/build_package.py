"""Hash the explicit payload; never stage Git, deploy, or submit."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent

def build(bundle=D,repo=None):
 bundle=Path(bundle).resolve();repo=Path(repo).resolve() if repo else bundle.parents[2]
 rels=(bundle/'PAYLOAD_PATHS.txt').read_text().splitlines()
 if (bundle/'sf7_binding_report.json').exists():rels.append('sf7_binding_report.json')
 rels=sorted(set(rels));paths=[];lines=[]
 for rel in rels:
  p=bundle/rel
  if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(bundle):raise ValueError('unsafe/missing payload: '+rel)
  path=str(p.relative_to(repo));paths.append(path)
  lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+path+'\n')
 manifest=''.join(lines).encode();ident=hashlib.sha256(manifest).hexdigest()
 (bundle/'DEPLOY_PATHS.txt').write_text('\n'.join(paths)+'\n');(bundle/'DEPLOY_SHA256SUMS').write_bytes(manifest)
 package=dict(package_id=ident[:16],manifest_sha256=ident,files=len(paths),root='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/'+ident[:16],sf7_binding='PENDING' if any(x.get('kind')=='pending_sf7' for x in json.loads((bundle/'INPUTS.json').read_text())) else 'OK')
 (bundle/'package_id.json').write_text(json.dumps(package,indent=2)+'\n');return package
if __name__=='__main__':print(json.dumps(build()))
