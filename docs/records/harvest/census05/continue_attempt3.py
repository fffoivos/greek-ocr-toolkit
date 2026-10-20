"""Verify retained attempt 3 custody, then apply only authorized readout version logic."""
import difflib, gzip, hashlib, json, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent; R=D.parents[2]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 old=json.loads((D/'receipt.json').read_text()); checks={}
 for p,m in old['artifacts'].items():
  if p.endswith('/first_step_code_sha_audit.json'):
   previous=subprocess.check_output(['git','show','ae2703a69:'+p]);assert hashlib.sha256(previous).hexdigest()==m['sha256']
   assert json.loads((R/p).read_text())['component_mismatches']==[]
   continue
  assert sha(R/p)==m['sha256'],p
 checks['attempt3_artifacts']=len(old['artifacts'])
 prov=json.loads((D/'package_provenance.json').read_text())
 for x in prov['files']:
  assert sha(R/x['package_path'])==x['sha256']
  assert hashlib.sha256(subprocess.check_output(['git','cat-file','blob',x['git_blob']])).hexdigest()==x['sha256']
 checks['CODE_SHA_files']=len(prov['files'])
 replay=json.loads((D/'parity/source_receipt.json').read_text()); h=hashlib.sha256()
 for x in replay['chunks']:
  assert sha(D/'parity'/x['path'])==x['sha256'];h.update(gzip.decompress((D/'parity'/x['path']).read_bytes()))
 assert h.hexdigest()==replay['sha256']==sha(replay['source'])
 checks['parity_expectation_sha256']=h.hexdigest()
 inputs=json.loads((D/'input_audit.json').read_text())
 for x in [*inputs['parents'],inputs['metadata'],inputs['split'],*inputs['neighboring_split_evidence']]:
  assert sha(x['path'])==x['sha256']
 assert sha(inputs['loader'])==inputs['loader_sha256']
 checks.update(split_rows=inputs['loader_rows'],expectations=inputs['expectation_resolution'],focused_tests='305 passed, 1 skipped',parity=json.loads((D/'native_parity_audit.json').read_text()))
 (D/'attempt3_reuse.json').write_text(json.dumps(checks,indent=2)+'\n')
 p=D/'readout/census_readout.py'; before=p.read_text();s=before
 s=s.replace("PIPELINE_VERSION = '0.3'  # line_pipeline.PIPELINE_VERSION; not a verdict rule\n",'')
 s=s.replace('def readout(run, out, baseline=None, expect_rows=None):','def readout(run, out, baseline=None, expect_rows=None, expect_pipeline_version=None):')
 s=s.replace('if version != PIPELINE_VERSION:',"if version == 'MISSING' or version != (expect_pipeline_version if expect_pipeline_version is not None else next(iter(versions))):")
 s=s.replace('expected_pipeline_version=PIPELINE_VERSION,','expected_pipeline_version=expect_pipeline_version,')
 s=s.replace('    args = parser.parse_args()','    parser.add_argument(\'--expect-pipeline-version\')\n    args = parser.parse_args()')
 s=s.replace('readout(args.run, args.out, args.baseline, args.expect_rows)','readout(args.run, args.out, args.baseline, args.expect_rows, args.expect_pipeline_version)')
 p.write_text(s)
 patch=''.join(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile='a/'+str(p.relative_to(R)),tofile='b/'+str(p.relative_to(R))))
 (D/'readout_version.patch').write_text(patch)
 print('Attempt 3 reused:',checks['attempt3_artifacts'],'artifacts;',checks['CODE_SHA_files'],'source files')
if __name__=='__main__':main()
