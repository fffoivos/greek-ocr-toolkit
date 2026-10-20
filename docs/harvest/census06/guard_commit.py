"""Exact allowlist for the lead. This script never invokes add or commit."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2]
EVIDENCE='''CENSUS06.md CHANGES.md COMMIT_LIST.md .gitignore commit_paths.txt commit_receipt.json guard_commit.py package_id.json DEPLOY_PATHS.txt DEPLOY_SHA256SUMS final_checks.py final_checks.json status.json payload_diff.json config_diff.json fingerprints.json source_custody.json input_custody.json audit_inputs.py continue_a.py finalize_inputs.py regenerate_n1.py regenerate_n1.log corrections/report.json corrections/converter_functions.py corrections/converter_extraction.patch corrections/converter_original/prepare_remote.py corrections/converter_original/finalize_remote.py restore_inputs.py regression_comparison.json run_regression_comparison.py baseline-regression.log baseline-regression.xml 033-regression.log 033-regression.xml regression_rerun.log parity_result.json parity.log local_runtime.json test_census06.py tests.log tests.xml readout/test_census_readout.py readout_033.patch mock_batch.py mock_batch_results.json mock_result_diff.json mock_batch.log mock_slice_inputs.jsonl.gz read_remote_basis.py remote_basis.json remote_basis.log runtime_remote.log runtime_sizing.json load_timing.json load_timing.log measure_load.py build_filter_versions_main.py verify_b.py census05_config.json'''.split()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--write-list',action='store_true');a=p.parse_args()
 paths=sorted(set((D/'DEPLOY_PATHS.txt').read_text().splitlines())|{str((D/x).relative_to(R)) for x in EVIDENCE})
 if a.write_list:
  for name in ('commit_paths.txt','commit_receipt.json'):
   if not (D/name).exists():(D/name).write_text('')
 for rel in paths:
  path=R/rel
  if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(D):raise ValueError('invalid commit path '+rel)
  if '/archives/' in rel or '/work/' in rel or '/target/' in rel:raise ValueError('archive/runtime data in commit list')
 if a.write_list:(D/'commit_paths.txt').write_text('\n'.join(paths)+'\n')
 else:assert (D/'commit_paths.txt').read_text().splitlines()==paths
 receipt={rel:sha(R/rel) for rel in paths if rel not in ('docs/harvest/census06/commit_receipt.json',)}
 if a.write_list:(D/'commit_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 else:assert json.loads((D/'commit_receipt.json').read_text())==receipt,'guarded bytes changed'
 outside=subprocess.check_output(['git','diff','HEAD','--no-ext-diff','--name-only','--'],cwd=R,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')).decode().splitlines()
 assert all(not p.startswith('docs/harvest/census06/') for p in outside),'unexpected tracked census06 path before lead commit'
 print(json.dumps(dict(paths=len(paths),root=str(D),git_mutations=0,unrelated_tracked_dirty_paths=outside,verifier_scope='whole tree')))
if __name__=='__main__':main()
