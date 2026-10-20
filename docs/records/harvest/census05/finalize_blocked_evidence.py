"""Write exact lead pathspec and scope/custody receipts; never write Git metadata."""
import hashlib,json,os,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];PREFIX=str(D.relative_to(R))+'/'
os.environ['GIT_OPTIONAL_LOCKS']='0'
def git(*args):return subprocess.check_output(['git','-C',str(R),*args]).decode()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def changed():
 return sorted(set(git('diff','--name-only','--',str(D)).splitlines()+git('ls-files','--others','--exclude-standard','--',str(D)).splitlines()))
def main():
 (D/'COMMIT_LIST.md').write_text('''# CENSUS05-A attempt 3 — exact lead commit paths

Status: **BLOCKED**, not a deployable package. This commit retains the readout compatibility witness, passing source/version/native-parity/split checks and an explicitly partial, uncertified source capture. Correction regeneration, jobs, complete regression, 200-row batch mocks and deploy manifests remain pending.

[commit_paths.txt](commit_paths.txt) is an exact pathspec file; all paths are inside docs/harvest/census05/. It excludes all readout files (unchanged), local test temporaries, the witness SQLite/input files and unrelated pre-existing docs/harvest/seg09/.

Lead commands, **not executed**:

```bash
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
git add --pathspec-from-file=docs/harvest/census05/commit_paths.txt
git diff --cached --stat
git commit -m "CENSUS05-A: record immutable readout version blocker and verified source inputs"
```

There is no package ID, deploy manifest or verifier allow-list. No ignored payload exists in the partial package. PROJECTS_SHA256 and package_provenance.json bind every captured source blob to CODE_SHA and preserve its repository path. The lead must not describe this evidence commit as CENSUS05-A READY.
''')
 for n in ('scope_guard.json','commit_paths.txt'):
  if not (D/n).exists():(D/n).write_text('')
 paths=sorted(set(changed()+[PREFIX+'scope_guard.json',PREFIX+'commit_paths.txt']));assert all(p.startswith(PREFIX) for p in paths)
 assert not any(p.startswith(PREFIX+'readout/') for p in paths)
 ignored=git('ls-files','--others','--ignored','--exclude-standard','--',str(D/'package')).splitlines();assert not ignored,ignored
 (D/'commit_paths.txt').write_text(''.join(p+'\n' for p in paths))
 receipt=json.loads((D/'receipt.json').read_text())
 exclusions={PREFIX+n for n in ('receipt.json','scope_guard.json','commit_paths.txt')}
 receipt['artifacts']={p:dict(bytes=(R/p).stat().st_size,sha256=sha(R/p)) for p in paths if p not in exclusions}
 receipt['artifact_hash_exclusions']=sorted(exclusions)
 (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 scope=dict(status='PASS',permitted_write_root=PREFIX.rstrip('/'),changed_files=paths,
  changed_files_outside_scope=[],readout_files_changed=[],readout_hashes_match_attempt_2=True,
  ignored_package_payload=[],local_only_ignored_paths=['focused-tests-tmp/','readout_contract_witness/attempt/','readout_contract_witness/input.jsonl','readout_contract_witness/metadata.json','readout_contract_witness/versions.json'],
  no_git_writes=True,no_network=True,no_reader_runs=True,no_slurm=True,no_deploy=True,
  preexisting_outside_scope_preserved='docs/harvest/seg09/',
  caveat='Exact changed-file scope from read-only Git queries; lead commits. This is not deploy qualification.')
 (D/'scope_guard.json').write_text(json.dumps(scope,indent=2)+'\n')
 assert paths==changed()
 for rel,h in receipt['readout_files_observed_sha256'].items():assert sha(R/rel)==h,rel
 source=json.loads((D/'package_provenance.json').read_text())
 for x in source['files']:assert sha(R/x['package_path'])==x['sha256']
 for p,meta in receipt['artifacts'].items():assert sha(R/p)==meta['sha256'],p
 large=[p for p in paths if (R/p).stat().st_size>5000000];assert not large,large
 print(json.dumps(dict(status='SCOPE_AND_CUSTODY_PASS',changed_paths=len(paths),source_files=len(source['files']),readout_unchanged=True,ignored_package_payload=0,package_certified=False)))
if __name__=='__main__':main()
