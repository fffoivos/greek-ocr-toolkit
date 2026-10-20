"""Offline build verification; does not invoke RUN_ALL, probes or model services."""
import hashlib,io,json,unittest
from pathlib import Path
from build import OUT,ROOT,SCANNER_SHA,PREREG_SHA,load,dump

def main():
 suite=unittest.defaultTestLoader.discover(str(OUT/'tools'),pattern='test_*.py')
 with (OUT/'tests.log').open('w') as log:
  result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 frozen=load(OUT/'build_hashes.json');mismatches=[]
 for rel,value in frozen.items():
  if hashlib.sha256((OUT/rel).read_bytes()).hexdigest()!=value:mismatches.append(rel)
 receipt=load(OUT/'build_receipt.json')
 validation=dict(ok=result.wasSuccessful() and not mismatches,tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),frozen_files_verified=len(frozen),frozen_mismatches=mismatches,scanner_sha256=SCANNER_SHA,preregistration_sha256=PREREG_SHA,contexts=receipt['contexts'],controls_pool=40,lead_control_review=load(OUT/'control_review/lead_review.json')['status'],reader_runs=sum(sum('run' in r for r in load(p)) for p in (OUT/'initial_ledger.json',OUT/'reread_ledger.json') if p.exists()),context_attempts=sum(len(load(p)) for p in (OUT/'initial_ledger.json',OUT/'reread_ledger.json') if p.exists()),network='offline validation',git_writes=False,layout_qa='8 word/native-line pairs viewed; control sheet layout viewed; no truth grading')
 dump(OUT/'validation.json',validation)
 print(json.dumps(validation,indent=2))
 if not validation['ok']:raise SystemExit(1)
if __name__=='__main__':main()
