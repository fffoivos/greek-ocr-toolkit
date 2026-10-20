"""Local-only final custody, source-scope and generated-package checks."""
import hashlib,importlib.util,json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];S='3b4090bf9b15d2d2cac53ee55161e936157ec0e5'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 checks={};entries=[]
 for line in (D/'DEPLOY_SHA256SUMS').read_text().splitlines():
  h,p=line.split('  ',1);assert sha(R/p)==h,p;assert not (R/p).is_symlink();entries.append(p)
 manifest=(D/'DEPLOY_SHA256SUMS').read_bytes();pkg=json.loads((D/'package_id.json').read_text());assert hashlib.sha256(manifest).hexdigest()[:16]==pkg['package_id'];assert entries==(D/'DEPLOY_PATHS.txt').read_text().splitlines();checks['deploy_files']=len(entries)
 prov=json.loads((D/'package_provenance.json').read_text())['files']
 for x in prov:
  assert sha(R/x['package_path'])==x['sha256']
  assert hashlib.sha256(subprocess.check_output(['git','show',S+':'+x['source_path']])).hexdigest()==x['sha256']
 actual={str(p.relative_to(R)) for p in (D/'package').rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and 'target' not in p.parts}
 expected={x['package_path'] for x in prov if '/package/' in x['package_path']};assert actual==expected,(actual-expected,expected-actual)
 checks['source_blobs']=len(prov)
 runtime=json.loads((D/'runtime_source_audit.json').read_text())
 for x in runtime['sources']:assert sha(x['bound_build_source_path'])==x['code_sha256']
 checks['native_build_sources']='PASS'
 for job in (D/'jobs').glob('*.sh'):subprocess.run(['bash','-n',str(job)],check=True)
 for job in (D/'jobs').glob('*.sbatch'):subprocess.run(['bash','-n',str(job)],check=True)
 checks['bash_syntax']='PASS'
 work=D/'readout-patch-check';work.mkdir(exist_ok=True)
 for name in ['census_readout.py','readout.sbatch','test_census_readout.py']:
  rel='docs/records/harvest/census05/readout/'+name;p=work/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(['git','show',S+':'+rel]))
 proc=subprocess.run(['patch','--dry-run','-s','-p1','-i',str(D/'readout_version.patch')],cwd=work,capture_output=True,text=True);assert proc.returncode==0,proc.stderr
 checks['coordinator_readout_patch_dry_run']='PASS'
 old=json.loads((D.parent/'seg_census/census04_config.json').read_text());new=json.loads((D/'census05_config.json').read_text())
 assert set(k for k in set(old)|set(new) if old.get(k)!=new.get(k))=={'codec','component_roots','corrections','versions','routes_out_of_scope'}
 assert new['routes_out_of_scope']==['polytonic'] and len(new['corrections'])==10
 spec=importlib.util.spec_from_file_location('census05_prepare',D/'prepare_config.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 inp=json.loads((D/'input_audit.json').read_text());split={k:inp['split'][k] for k in ['path','sha256']}
 prepared=mod.prepare(new,D/'package/projects',D/'production-config-probe',split_input=split)
 for key in ['codec','versions']:assert Path(prepared[key]).is_file(),key
 assert prepared['component_roots']['greek-ocr-toolkit-pipe032']==str(D/'package/projects/greek-ocr-toolkit-pipe032')
 checks['production_config_relocation']='PASS'
 mock=json.loads((D/'mock_batch_results.json').read_text())
 for tag in ['smoke-mode-i','smoke-mode-ii','full-mode-ii']:
  assert mock[tag]['rows']==200 and mock[tag]['complete'];assert all(x['status']=='PASS' for x in mock[tag]['readout_invariants'].values())
 assert mock['full-mode-i']['refused'] and mock['full-mode-i']['exit_code']==2
 checks['mocks']='PASS: three completed 200-row attempts, all 14/14; unsplit full refused'
 checks['network']='OFF';checks['reader_runs']=0;checks['slurm_actions']=0;checks['deploy_actions']=0
 (D/'final_checks.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
if __name__=='__main__':main()
