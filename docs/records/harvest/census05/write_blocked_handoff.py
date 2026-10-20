"""Finalize reviewable blocker evidence without certifying/deploying a package."""
import hashlib,json,os,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];S='3b4090bf9b15d2d2cac53ee55161e936157ec0e5'
os.environ.update(GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
def read(n):return json.loads((D/n).read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n')
def main():
 old=read('receipt.json')
 # Preserve only old readout custody fields; other attempt-2 evidence stays in Git 0387e9177.
 readout_hashes=old['readout_files_observed_sha256']
 for rel,h in readout_hashes.items():assert sha(R/rel)==h,rel
 audit=read('code_sha_audit.json');source=read('package_provenance.json');witness=read('readout_contract_audit.json');inputs=read('input_audit.json');parity=read('native_parity_audit.json');custody=read('correction_custody_audit.json')
 for x in source['files']:
  assert sha(R/x['package_path'])==x['sha256']
  assert hashlib.sha256(subprocess.check_output(['git','cat-file','blob',x['git_blob']])).hexdigest()==x['sha256']
 n=len(source['files']);table='\n'.join('| '+r['tool']+' | '+r['version']+' | `'+r['actual_digest']+'` | yes |' for r in audit['stages'])
 ledger='\n'.join('| '+ ' | '.join(str(x[k]) for k in ('tool','parent_id','records','edits','holds','no_change'))+' | '+x['planned_disposition']+' |' for x in custody['ledgers'])
 last=f'CENSUS05-A BLOCKED: CODE_SHA {S[:8]}; unchanged CENSUS05-R expects pipeline 0.3, CODE_SHA emits 0.3.2; readout 13/14 invariants PASS (version mismatch); partial source capture {n} CODE_SHA-identical files; parity 150/150 888/888 = SEG10 yes; split validated 320479 rows; focused tests 305 passed 0 failed 1 skipped; correction regeneration/jobs/200-row mocks/deploy manifest not completed'
 handoff=f'''# CENSUS05-A hand-off — BLOCKED by unchanged CENSUS05-R version contract

CODE_SHA passes the required source/version gates and native parity, but the required unchanged readout rejects its pipeline version. **No deployable census_05 package is certified.** The native verdicts, reasons, dispositions, tool manifest and readout remain unchanged. This is a readout compatibility blocker, not a segmentation finding.

## Source capture and provenance

CODE_SHA is `{S}`. `audit_code_sha.py` was re-pointed first, mapping `greek-ocr-toolkit-pipe032/` to the CODE_SHA repository tree exactly like the legacy `greek-ocr-toolkit-main-next/` prefix. [First output](first_step_code_sha_audit.json) passes 35/35 component checks. [Expanded audit](code_sha_audit.json) additionally asserts the SEG10 and PIPE032 last-line gates, the expected tool versions, the segmentation label and pipeline 0.3.2.

The paths actually used at CODE_SHA are `docs/records/harvest/seg_steps/s5_adopt/REPORT.md`, `docs/records/harvest/pipe032/REPORT.md`, `docs/harvest/line_pipeline/README.md`, `docs/harvest/line_pipeline/tool_versions.json`, unchanged `greekocr/` and `scripts/` paths, and the retained `docs/harvest/seg_census/package/`. Both reports end READY. The read-only P3 plan was read at `../greek-ocr-toolkit-main-next/docs/programme_20261019/NIGHT_PLAN.md`; the present brief's 0.3.2 supersedes that plan's 0.3.1. The requested READY-line template also says 0.3.1; actual code is 0.3.2. No false READY line is emitted.

`package/projects/greek-ocr-toolkit-pipe032/` is a **partial source capture**, with secondary/spellcheck components in sibling project directories. There are **{n} CODE_SHA-identical files, zero additive files inside the source capture**. Every file has its repository source path, size, SHA256 and `git ls-tree`/`git cat-file` blob proof in [package_provenance.json](package_provenance.json). [PROJECTS_SHA256](PROJECTS_SHA256) binds repository paths by file bytes, not branch history. All captured files were rehashed after the runs. No manifest was regenerated or edited.

[build_package.py](build_package.py) derives imports transitively from the census entry point, component manifest and requested regression files, adding data-driven test dependencies as discovered. [Census_04 comparison](census04_file_comparison.json) accounts for all 338 old deploy entries. Inert pytest caches and files outside the runtime/test/component closure are dropped. This list has not yet passed the four segmentation test modules and is **not a complete final deployment inventory**.

The census_04 split/diagnostics adapter is already a committed CODE_SHA blob at `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py`. It is copied unchanged into the captured package's `greekocr/harvest/` and used by the split audit. Native `line_pipeline_census.py` still has no `load_split` capability or census_04 diagnostic join. No verdict-reading or verdict-changing adapter was added. Audit/build helpers are new local preparation artifacts, not certified runtime additions.

## Blocking readout finding

The immutable `readout/census_readout.py:19` sets `PIPELINE_VERSION = '0.3'`. At lines 205–207, it records a `pipeline_version_mismatch` for every decision whose version is different. CODE_SHA's `greekocr/harvest/line_pipeline.py` emits `PIPELINE_VERSION = "0.3.2"`. The CLI exits 1 if any invariant fails.

[Reproducer](audit_readout_contract.py) executed the captured, byte-identical census code and active tool manifest, with only native I/O replaced by CODE_SHA's existing test fixture. The actual output is a completed, one-row ADMIT export with pipeline 0.3.2. The untouched readout CLI exits **1**. Its only failed invariant is **pipeline_version_mismatch: 1**; all 13 other invariants pass. [Audit](readout_contract_audit.json), [console](readout_contract_audit.log), [readout](readout_contract_witness/reports/READOUT.md), [machine report](readout_contract_witness/reports/readout.json).

Verbatim readout last line:

> {witness['last_line']}

This is a one-row contract witness, **not** the requested 200-real-row batch mock. All 16 pre-existing readout files, including caches and prior receipts, retain their attempt-2 SHA256. No constant was overridden in memory, no exported decision was relabelled and no check was suppressed. [proposed_readout_version.patch](proposed_readout_version.patch) is an **unapplied proposal outside readout/** for the readout owner/coordinator; changing it here would violate the explicit no-edit instruction.

The readout separately refuses `--out <attempt>/readout` because output must be outside its read-only run directory. That refusal was reproduced as well. An eventual job wrapper can stage reports in a sibling directory and then move them into `<attempt>/readout`, keeping the reader unchanged. No such job is certified in this attempt.

## Stage composition

| Stage | Version | Recomputed SHA256 tool digest | Match |
|---|---|---|---|
{table}

Pipeline is **0.3.2**; segmentation is **0.13**, label **0.9-s5**. Segmentation policy SHA256 is `5888fe704e6170b51081d6fa4200a725d2b29f0c70301f238faf7b32088b5b99`. Every manifest component and digest recomputes from the captured bytes without edits.

## Native runtime

All four tracked runtime entries equal lineage `3679c8412`. The three build inputs `Cargo.lock`, `Cargo.toml`, `src/main.rs` also hash-equal the retained census_03 prepared source tree; [runtime_source_audit.json](runtime_source_audit.json) lists both hashes and paths. Census_03 binds remote predictor `2cc882d68be85cbef8ac43bf27a963bd6b249ff89ece80a23ff4821a1d3feacf` and runtime manifest `84ed3add6190afe57198a9654bd16a0fc9464126d6c09a14cc5cd3e5f0ca68a4`. Network is OFF, so no fresh remote binary/manifest readback is claimed.

The local native replay used the read-only main-next debug predictor, SHA256 `d2fe37a51f92f0b2d3416d4ca4917214ee0a354ab21e9ee80e664304ddce9adb`, matching SEG10. The segcensus symlink currently targets another debug build, so it was not used. No binary was built or copied.

## Parity

**Route: found existing replay, hash-checked; no expectation rebuild.** The file is `../greek-ocr-data/docs/records/harvest/seg_steps/s5_adopt/replay.jsonl`: 42,991,967 bytes, SHA256 `6e9ab21d28340ec7acf9d2b1b39bc7cf899a6bfc87b754e59d986265da417f32`, exactly SEG10's committed `receipt.json` artifact entry. The committed `replay_receipt.json` records 1,705 rows and 111 flips but has no replay-file hash; the artifact entry supplies that hash.

The complete expectation is retained losslessly in ordered `parity/replay-01.jsonl.gz` + `parity/replay-02.jsonl.gz`. Concatenating their decompressed bytes reproduces the original SHA256. Each compressed file is below 5,000,000 bytes. [Custody receipt](parity/source_receipt.json).

Fresh native execution under captured code reproduces **150/150 segeval1 + 888/888 calibration verdict AND reason**, in input order, byte-exact against SEG10. Saved calibration contexts and the inherited 120-second per-row bound are retained. [Harness](audit_native_parity.py), [audit](native_parity_audit.json), [log](native_parity_audit.log), [results](parity/native_results.jsonl.gz). Elapsed: {parity['elapsed_seconds']:.3f} seconds; readers 0, network OFF. No census parity batch script was run.

## Corrections

[Fresh custody audit](correction_custody_audit.json) rehashes all **14** census_03 canonical files. All match `census04_config.json`. Counts transfer from the attempt-2 complete scan only after that exact hash equality. [Producer source inventory](label_source_inventory.json) reads/hashes the requested registry, handoff, producer ledgers and their manifests/checksums.

The four named N1 ledgers require regeneration. **W1 numerics also has an incompatible active identity**, so five N1 ledgers require regeneration under section 2. Cyrilic method identities match. Full `ArtifactCorrector.load` validation, regeneration with the copied census_03 converter, producer validation and record-diffs are **not completed** after the readout blocker. No ledger is restamped, rewritten or certified.

The four polytonic ledgers are listed below as **not bound in census_05 (planned)**. No config has been emitted, so no binding change is claimed as executed. SF7 remains candidate_pre_audit; nothing is prepared to apply tonight.

| Tool | Parent | Census_03 records | Edited rows | Holds | No-change | Census_05 planned action |
|---|---|---:|---:|---:|---:|---|
{ledger}

Census_05 correction counts/bytes/SHA256 and census_03→05 record-diffs do not yet exist. Superseded-source references: zero in the freshly hash-verified inventory; no new ledgers generated.

## Config and split

No final census05 config was emitted. Production must preserve the five parents (592,466 rows), metadata, 9,119 held-out crops, 61 held-out editions and frozen_05 join, set `routes_out_of_scope: ["polytonic"]`, map `greek-ocr-toolkit-pipe032` to the actual package root, and bind the five regenerated N1 inputs. The field-by-field config diff and full-without-split refusal remain pending.

The finalized P1 split **is validated**. Its compressed bytes hash `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82` and equal `git show aa860af55:docs/harvest/collect_v3_admission/split2/row_split.jsonl.gz` in the sourcing checkout. All 320,479 records satisfy the census_04 JSON schema and the **captured package's** unchanged loader. Unique parent+row and one split per edition pass; W1/W2 joins have zero unmatched rows in either direction; 1,359 editions and all 99 forced-test editions pass. Totals: train 253,402; dev 7,007; test 60,070. Per-parent counts, neighboring file custody and parent hashes are in [input_audit.json](input_audit.json). The 436 later BSB pages remain outside these frozen parents.

All five local parent files match their frozen hashes/counts. The metadata hash matches census_03. Calling CODE_SHA expectations on every row resolves **592,466 by page override, 0 by book declaration, 0 by source policy, 0 unresolved**. [Harness](audit_inputs.py), [log](input_audit.log). No labels or split assignments were changed.

## Jobs, mocks and tests

No job scripts, deploy manifest or package ID are issued. Regression/parity/census/readout production settings are not altered. No Slurm, deployment, remote verifier, reader run or 200-real-row spooled mock ran. The readout witness is deliberately labelled separately from those required mocks.

Focused tests of captured `test_content_gate.py`, `test_line_pipeline.py`, `test_integration_fixes.py` and `test_numeric_cells.py`: **305 passed, 0 failed, 1 skipped**. The unchanged fixture helper skips numeric four-set parity because the captured `cells/samples.jsonl` input is absent. [Full output](focused_tests.log). Initial incomplete-closure checks exposed missing data dependencies; the final output above supersedes them. The four segmentation test modules and the complete batch regression remain pending, so this is not the coordinator's 7,305-test suite or final package qualification.

No census runtime forecast is certified. Historical elapsed time remains 01:49:19 for census_03 and the requested budget remains 04:00:00. S4/SEG10 replay records inspected here contain no per-row seconds/timing fields; only aggregate replay elapsed times are recorded. No unsupported 0.8-normalized estimate is supplied.

## Attempt 1

Evidence commit `5ca995d34`: stopped correctly for a stale census digest. The current 35/35 audit passes; this stop is resolved.

## Attempt 2

Evidence commit `0387e9177`: stopped correctly for segmentation version/history mismatch and four standing N1 ledgers at numerics 0.2. PIPE032 resolves the segmentation validator mismatch. The revised brief authorizes N1 regeneration, including W1 if needed; it has not yet been executed in this attempt. Old `audit_runtime_contracts.py`/`runtime_contract_audit.*` remain historical attempt-2 evidence against their recorded old SHA and are not current certification.

## Commit and follow-up

The lead commits only [commit_paths.txt](commit_paths.txt); [COMMIT_LIST.md](COMMIT_LIST.md) labels this as blocker evidence plus an uncertified source capture. [FOLLOW_UP.md](FOLLOW_UP.md) records the precise readout-owner resolution, the deferred SF7/TR2 note and remaining package gates. No fake deploy/submission commands containing an uncertified package ID are provided.

All writes remain inside `docs/harvest/census05/`; readout is hash-unchanged. No other worktree, Git metadata, network, reader, deployment or Slurm action was written/executed. `docs/harvest/seg09/` remains the pre-existing unrelated untracked tree.

{last}
'''
 (D/'HANDOFF_CENSUS05.md').write_text(handoff)
 follow='''# CENSUS05 follow-up — BLOCKED; no deployable package ID

## Required readout-owner resolution

The unchanged CENSUS05-R script expects pipeline `0.3` and rejects actual `0.3.2` output. The exact one-row witness and failed invariant are in HANDOFF_CENSUS05.md and readout_contract_audit.json. Its only failed invariant is pipeline_version_mismatch. `proposed_readout_version.patch` shows the one-line version update for the readout owner/coordinator; it is not applied. Do not suppress the invariant or relabel pipeline exports.

Readout output must be outside its input directory. A later jobs/readout.sbatch wrapper can call the unchanged readout with a unique sibling staging directory, then move the reports into `<attempt>/readout/`. This preserves all readout validation and satisfies the requested final layout. No wrapper is issued/certified here.

After the readout owner resolves the version contract, rerun the compatibility witness with a fresh directory inside census05. The harness currently asserts the known failure; revise its assertion to require all PASS only after the authorized readout update. Do not overwrite the retained failure evidence.

## Remaining package work

1. Regenerate all five N1 ledgers (including W1) with copied, diff-reviewed census_03 converters and the same hash-checked producers; record all non-identity record diffs. Validate every retained cyrillic ledger through actual ArtifactCorrector.load. Unbind the four polytonic ledgers; emit the exact config diff with routes_out_of_scope and frozen_05 unchanged.
2. Finish the import/test-data closure and all four segmentation regression files. Reuse the retained hash-checked SEG10 parity expectation and fresh 150/888 native results.
3. Emit CENSUS05 jobs with the requested production resources; enforce the submit-time CENSUS05_SPLIT_FILE + CENSUS05_SPLIT_SHA256 pair in full mode. Exercise smoke/full, fake split/absent split and readout through the real spooled scripts; full without a split must refuse.
4. Establish the requested runtime estimate from available comparable timing evidence; do not invent per-row timers absent from the replay. Retain 04:00:00.
5. Only after every gate passes, emit DEPLOY_PATHS.txt, DEPLOY_SHA256SUMS, package_id.json and exact local/remote per-file readback commands. Recreate the literal deploy/verify/smoke/full chains from the brief against that real package ID. All remain unexecuted in CENSUS05-A.

The finalized split's future remote input path is:
`$W/census_05_20261020/inputs/row_split.jsonl.gz`
with compressed SHA256 `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82`.
New correction ledgers will also belong under `$W/census_05_20261020/inputs/`; their names/hashes cannot be pinned before regeneration.

CENSUS05-B must read `scontrol show partition debug` and supply `<DEBUG_TIME_WITHIN_PARTITION_LIMIT>` in smoke submission commands. No Slurm command runs here. The source brief says “all five” verifier checks but names four executable job kinds (regression, parity, census, readout) plus common.sh; common.sh is not a Slurm job. Clarify the fifth intended kind in the coordinator handoff rather than inventing a job.

## SF7/TR2 note

When SF7's audit passes, a later census puts polytonic back in scope and rebinds its ledgers at the then-current status. Nothing is prepared to apply tonight.

## Re-pointing at main (literal commands, not executed)

File hashes, rather than later documentation commits, bind the captured source. Run after the local merge and after completing the source capture:

```bash
REPO=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
D="$REPO/docs/harvest/census05"
CODE_SHA=3b4090bf9b15d2d2cac53ee55161e936157ec0e5
paths=()
while read -r hash path; do paths+=("$path"); done < "$D/PROJECTS_SHA256"
git -C "$REPO" diff --quiet "$CODE_SHA" main -- "${paths[@]}"
python3 -B - "$REPO" "$D/PROJECTS_SHA256" <<'CHECK'
import hashlib, pathlib, subprocess, sys
repo, manifest = sys.argv[1:]
for line in pathlib.Path(manifest).read_text().splitlines():
    expected, path = line.split('  ', 1)
    data = subprocess.check_output(['git', '-C', repo, 'show', 'main:' + path])
    assert hashlib.sha256(data).hexdigest() == expected, path
print('PROJECTS_SHA256 main PASS')
CHECK
```

Any difference means rebuild. The current PROJECTS_SHA256 describes the partial source capture; it is not a deploy certificate.

## P4 outputs and readout contract

A future successful attempt must publish CURRENT.json with status completed and a hash-bound generation; decisions.jsonl with all 592,466 parent rows and exact reasons; admitted_train.jsonl with only qualified train rows; admission_records.jsonl; pending_* queues; summary.json with complete true and reconciled counts; readout/READOUT.md and readout.json with all invariants PASS.

The unchanged report's sections cover run/baseline provenance, versions, invariant status, dispositions/strata, input splits, gate deciding/overlapping reasons, segmentation reasons, correction statuses/edits, pending queues, deduplication, protected identities, diagnostics and file provenance. P4 must consume those exact tables and the verbatim final `CENSUS READOUT:` line, with every invariant PASS. The retained 13/14 compatibility witness is not P4 acceptance.

No deployment, remote VERIFY_OK, sbatch --test-only, smoke or full submission is claimed.
'''
 (D/'FOLLOW_UP.md').write_text(follow)
 receipt=dict(task='CENSUS05-A',status='BLOCKED_UNCHANGED_READOUT_CONTRACT',code_sha=S,
  component_audit=dict(status=audit['status'],checks=audit['component_checks'],mismatches=0),
  project_prefix_map=audit['project_prefix_map'],required_report_gates=dict(SEG10=True,PIPE032=True),
  pipeline_version='0.3.2',segmentation_version='0.13',segmentation_label='0.9-s5',
  source_capture=dict(files=n,code_sha_identical=n,additive=0,final_package=False,manifest='PROJECTS_SHA256'),
  blockers=[dict(kind='immutable_readout_version_contract',expected_by_readout='0.3',actual_pipeline='0.3.2',failed_invariant='pipeline_version_mismatch',witness_rows=1,exit_code=1)],
  package_id=None,package_built=False,deployable=False,parity=parity,split_validation=inputs,
  focused_tests=dict(passed=305,failed=0,skipped=1,complete_regression=False,log='focused_tests.log'),
  correction_custody=dict(ledgers=14,all_sha256_match=True,regeneration_required=5,new_ledgers=0,full_load_validation=False),
  correction_regeneration=None,whole_pipeline_200_mock=None,runtime_estimate=None,
  attempt_1=dict(evidence_commit='5ca995d34',finding='stale census digest',resolved=True),
  attempt_2=dict(evidence_commit='0387e9177',findings=['segmentation version/history','four N1 identities'],segmentation_resolved=True,regeneration_pending=True),
  readout_modified=False,readout_files_observed_sha256=readout_hashes,network_used=False,git_mutations=False,reader_runs=False,
  native_image_runs=1038,slurm_used=False,deployed=False,last_line=last)
 dump('receipt.json',receipt)
 print(last)
if __name__=='__main__':main()
