"""Exact lead pathspec, final artifact hashes and candid final-state scope guard."""
import hashlib,json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];PREFIX=str(D.relative_to(R))+'/'
def git(*a):return subprocess.check_output(['git','-C',str(R),*a]).decode()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def changed():
 return sorted(set(git('diff','--name-only','--',str(D)).splitlines()+git('ls-files','--others','--exclude-standard','--',str(D)).splitlines()))
def main():
 pkg=json.loads((D/'package_id.json').read_text());mocks=json.loads((D/'mock_batch_results.json').read_text());checks=json.loads((D/'final_checks.json').read_text());assert checks['deploy_files']==pkg['deploy_files']
 (D/'COMMIT_LIST.md').write_text('''# CENSUS05-A exact lead commit list

Package `'''+pkg['package_id']+'''` is locally READY, not deployed or remotely verified. Use the exact pathspec, which includes new files, changed files and removed unused partial-capture files. Every final changed path is inside docs/harvest/census05/. No .git write occurred here.

```bash
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
git add --pathspec-from-file=docs/harvest/census05/commit_paths.txt
git diff --cached --stat
git commit -m "CENSUS05-A: package PIPE032 census with regenerated N1 and version-bound readout"
```

The code payload manifest has '''+str(pkg['deploy_files'])+''' files ('''+str(pkg['code_sha_identical'])+''' CODE_SHA-identical; 13 additive). Already tracked identical source blobs need no new diff. No ignored payload or verifier allow-list is needed. Full numerics inputs, SQLite validation databases, native target symlink and mock runtime are excluded. The 35 committed correction gzip chunks, their receipt and restore_inputs.py reproduce the five ignored full-size inputs exactly. The finalized sourcing split stays external.

readout_version.patch targets the canonical relocated CODE_SHA docs/records/harvest/census05/readout paths for the coordinator's separate docs-only merge. The local package mirror edits three files under docs/harvest/census05/readout/. Do not change production code or the frozen tool manifest.

FOLLOW_UP.md contains the unexecuted deployment/readback/verifier/smoke/full and main hash-comparison commands. Require actual VERIFY_OK and coordinator smoke approval before full submission. Four batch kinds are named in the brief; its “all five” wording remains a documented ambiguity.
''')
 for name in ['scope_guard.json','commit_paths.txt']:
  if not (D/name).exists():(D/name).write_text('')
 paths=sorted(set(changed()+[PREFIX+'scope_guard.json',PREFIX+'receipt.json',PREFIX+'commit_paths.txt']))
 assert all(p.startswith(PREFIX) for p in paths)
 outside=[p for p in git('diff','--name-only').splitlines() if not p.startswith(PREFIX)];assert not outside,outside
 assert not git('diff','--cached','--name-only').strip(),'unexpected index changes'
 readout=[p for p in paths if p.startswith(PREFIX+'readout/')]
 assert readout==[PREFIX+'readout/'+n for n in ['census_readout.py','readout.sbatch','test_census_readout.py']],readout
 (D/'commit_paths.txt').write_text(''.join(p+'\n' for p in paths))
 excludes={PREFIX+n for n in ['receipt.json','scope_guard.json']}
 artifacts={}
 allfiles=sorted(set(git('ls-files','--cached','--others','--exclude-standard','--',str(D)).splitlines()))
 for rel in allfiles:
  path=R/rel
  if path.is_file() and rel not in excludes:artifacts[rel]=dict(bytes=path.stat().st_size,sha256=sha(path))
 receipt=dict(task='CENSUS05-A',status='READY_LOCAL_NOT_DEPLOYED',code_sha='3b4090bf9b15d2d2cac53ee55161e936157ec0e5',package=pkg,
  component_checks=35,component_mismatches=0,pipeline_version='0.3.2',segmentation_version='0.13',segmentation_label='0.9-s5',
  project_prefix_map={'greek-ocr-toolkit-pipe032':'CODE_SHA tree / installed package root','greek-ocr-toolkit-main-next':'legacy CODE_SHA alias'},
  attempt3_reuse=json.loads((D/'attempt3_reuse.json').read_text()),corrections=dict(bound=10,regenerated=5,standing=5,unbound_polytonic=4,ArtifactCorrector_load='PASS every bound record',changes_beyond_tool_identity=0,status_moves=0,superseded_source=0),
  split=dict(rows=320479,sha256='7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82',validated_by_packaged_loader=True),expectation_resolution=dict(page_override=592466,book_declaration=0,source_policy=0,unresolved=0),
  tests=dict(packaged_regression_passed=360,readout_passed=20,passed=380,failed=0,skipped=9),mocks=mocks,runtime_estimate=json.loads((D/'runtime_estimate.json').read_text()),final_checks=checks,
  remote=dict(deployed=False,verified=False,VERIFY_OK=False,slurm=False,network=False,readers=0),
  limitations=['Committed S4/SEG10 per-row timers absent: forecast uses separately measured same-row 0.8/SEG10 local timing supplement.','Brief names four batch kinds but asks for five VERIFY_OK results; four named kinds supplied.','Final-line template 0.3.1 corrected to actual 0.3.2.','Later explicit sibling readout rule supersedes inside-attempt wording.','Initial temporary regression log/test directory escaped scope by one parent, then were moved back; no outside final change remains.'],
  artifacts=artifacts,artifact_hash_exclusions=sorted(excludes),lead_commits=True)
 (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 scope=dict(status='FINAL_CHANGED_PATHS_PASS_WITH_RECORDED_TRANSIENT_EXCEPTION',permitted_root=PREFIX.rstrip('/'),changed_files=paths,
  file_states=[dict(path=p,state='modified_or_added' if (R/p).exists() else 'removed_unused_partial_capture') for p in paths],final_changes_outside_scope=[],readout_changed=readout,
  transient_scope_exception=dict(paths=['docs/harvest/regression_tests.log','docs/harvest/regression-tmp/'],cause='initial regression output paths had one extra parent traversal',resolution='moved under docs/harvest/census05/; no outside final artifact remains'),
  preserved_outside_untracked='docs/harvest/seg09/',no_git_writes=True,index_diff_empty=True,no_network=True,no_reader_runs=True,no_deploy=True,no_slurm=True,
  ignored_payload_in_deploy_manifest=[],local_only_ignored=['corrections/work/','corrections/numerics_*.jsonl','mock_batch/','*-tmp/','readout-patch-check/','production-config-probe/','package/**/target/'])
 (D/'scope_guard.json').write_text(json.dumps(scope,indent=2)+'\n')
 assert paths==changed(),set(changed())^set(paths)
 for rel,x in artifacts.items():assert sha(R/rel)==x['sha256'],rel
 too_large=[p for p in paths if (R/p).is_file() and (R/p).stat().st_size>5_000_000];assert not too_large,too_large
 print(json.dumps(dict(status=receipt['status'],package=pkg['package_id'],changed_paths=len(paths),artifact_hashes=len(artifacts),all_final_paths_in_scope=True)))
if __name__=='__main__':main()
