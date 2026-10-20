"""Local CENSUS06-A custody and scope checks, with no deploy or Git mutation."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;R=D.parents[2];BASE=R.parent/'greek-ocr-toolkit-segcensus/docs/harvest/census05';P=D/'package/projects/greek-ocr-toolkit-pipe032'
sys.path.insert(0,str(P));sys.path.insert(0,str(D))
from greekocr.harvest.line_pipeline_census import verify_versions
from build_package import build
from binding_state import pending

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 v=json.loads((P/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools'];verify_versions(v,{p.name:str(p) for p in P.parent.iterdir() if p.is_dir()})
 package=build();changed=[];unchanged=[]
 basefiles=json.loads((D/'source_custody.json').read_text())['files']
 for x in basefiles:
  rel=x['base_path'].removeprefix('docs/harvest/census05/');new=rel.replace('census05_config.json','census06_config.json');p=D/new
  if sha(p)==x['sha256']:unchanged.append(new)
  else:
   if new.startswith('package/'):
    assert new in ['package/projects/greek-ocr-toolkit-pipe032/'+p for p in ['greekocr/harvest/line_pipeline.py','tests/test_content_gate.py','docs/harvest/line_pipeline/tool_versions.json']]
   elif new not in ['census06_config.json','prepare_config.py','readout/census_readout.py','readout/readout.sbatch'] and not new.startswith('jobs/'):raise AssertionError('unexpected inherited payload change: '+new)
   changed.append(dict(path=new,before_sha256=x['sha256'],after_sha256=sha(p)))
 assert len(unchanged)+len(changed)==167
 patch=[]
 import difflib
 for name in ['census_readout.py','readout.sbatch','test_census_readout.py']:
  old=(BASE/'readout'/name).read_text();new=(D/'readout'/name).read_text();patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/docs/harvest/census05/readout/'+name,tofile='b/docs/harvest/census06/readout/'+name))
 (D/'readout_033.patch').write_text(''.join(patch))
 for p in list((D/'jobs').glob('*'))+[D/'flip_report.sbatch',D/'VERIFY.sh',D/'submit_chain.sh']:
  subprocess.run(['bash','-n',str(p)],check=True)
  if p.suffix=='.sbatch':
   text=p.read_text();assert '#SBATCH --account=a0140' in text and '#SBATCH --partition=normal' in text and '#SBATCH --time=' in text
 assert json.loads((D/'parity_result.json').read_text())['counts']==dict(segeval1=150,calibration=888)
 reg=json.loads((D/'regression_comparison.json').read_text());assert reg['existing_fixture_changes']==[]
 nums=json.loads((D/'corrections/report.json').read_text());assert nums['regenerated']==5
 for e in nums['ledgers']:
  assert e['ArtifactCorrector_load']=='PASS'
  if e['tool']=='numerics':assert e['changes_beyond_identity']==0 and all(k.split(' -> ')[0]==k.split(' -> ')[1] for k in e['status_transitions'])
 mocks=json.loads((D/'mock_batch_results.json').read_text());passed=0;total=0
 for name in ['smoke-mode-i','smoke-mode-ii','full-mode-ii']:
  inv=mocks[name]['readout_invariants'];passed+=sum(v['status']=='PASS' for v in inv.values());total+=len(inv)
 assert passed==total and total==48
 config=json.loads((D/'census06_config.json').read_text());assert len(pending(config))==5
 tests=list(ET.parse(D/'tests.xml').iter('testcase'));assert not any(c.find('failure') is not None or c.find('error') is not None for c in tests)
 count=sum(c.find('skipped') is None for c in tests)+reg['counts']['033']['passed']
 payload=set((D/'PAYLOAD_PATHS.txt').read_text().splitlines());original={x['base_path'].removeprefix('docs/harvest/census05/').replace('census05_config.json','census06_config.json') for x in basefiles}
 diff=dict(inherited_files=167,unchanged=len(unchanged),changed=changed,additive_paths=sorted(payload-original),dropped_paths=sorted(original-payload))
 assert not diff['dropped_paths'];(D/'payload_diff.json').write_text(json.dumps(diff,indent=2)+'\n')
 result=dict(status='READY',package=package,tests_passed=count,amendment_readout_binding_flip_tests_passed=count-360,tests_skipped=len(tests)-(count-360)+9,existing_fixture_changes=0,parity='150/150 888/888',mocks_passed=passed,mocks_invariants=total,sf7_binding='PENDING',fingerprints_changed=8,numerics_regenerated=5,numerics_status_moves=0,deployed=False,jobs_submitted=0,verifier_dirty_scope='whole tree; every tracked uncommitted path is rejected',verifier='DEFERRED TO B; no bypass')
 (D/'final_checks.json').write_text(json.dumps(result,indent=2)+'\n');(D/'status.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
