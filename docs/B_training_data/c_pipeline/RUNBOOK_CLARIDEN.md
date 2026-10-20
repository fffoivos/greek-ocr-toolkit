# B.c — Clariden verification, smoke and full census

Documentation synchronized 20 October 2026; original CLEAN5B run statements below are historical. Commands below are operational references, **not executed in CLEAN5B**. No deployment, scheduler check, job, reader, training, pipeline or Git mutation is authorized or performed by this documentation-only task. Use [README.md](README.md) for stage rules, input identities and known integration differences.

## Choose an exact build before using a runbook

There are two materially different implementations on this branch:

| Build | Entrypoint and status | Operational consequence |
|---|---|---|
| Current top-level integrated source | `python -B -m greekocr.harvest.line_pipeline_census`; pipeline 0.3.2, segmentation **0.13 (label 0.9-s5)**, gate/final **0.3**, numerics 0.3, composer 0.3, census 0.7 | Needs its own exact package/config/runtime/parity qualification. Historical census03/04 receipts do not establish this build's deployment or full result. |
| Archived census04 package | `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py`; segmentation **0.8**, gate/final **0.2** | Recorded package `bb1ea164338b3068`, 338 deploy entries. Final b2 receipt: deployed, three VERIFY_OK, dry scheduler checks only, **no submission**, no final split file. |

The package's `line_pipeline_census04.py` exists **inside the archive**, not at the top-level import path. Its `jobs/*.sbatch` set `PYTHONPATH` to that archived deployed package. Exporting a current working-directory path does not upgrade the package to S4. The original README's segmentation 0.5 and the policy JS's historical 0.8 comment also do not identify a deployed current build; inspect the exact tool manifest and component hashes.

**Historical integration limitation (before SEG10):** top-level code lacked numeric-adjacency negatives and the configured held-out crop hash union. Both are present in current `automatic_result()`/`Ledger.deduplicate()`. PIPE032 adds explicit correction release scope; empty scope retains the existing decisions. Verify the actual package/config/runtime rather than treating an archived receipt as a current-build check.

## Job kinds, resources and paths

Recorded census04 job kinds, from `docs/records/harvest/seg_census/JOB_KINDS.md` and the batch directives:

| Kind | Partition | Nodes/tasks/CPUs per task | Requested time | Measured census03 step |
|---|---|---|---|---|
| `jobs/regression.sbatch` | normal | 1 / 1 / 256 | **00:05:00** | 00:00:13 |
| `jobs/parity.sbatch` | normal | 1 / 1 / 256 | **00:05:00** | 00:00:01 |
| `jobs/census.sbatch` | normal | 1 / 1 / 256 | **04:00:00** | 01:49:19 |

Whole census03 job: 01:49:40. These measurements support inherited budgets with margin for the recorded build; they are not a forecast for S4. Slurm accounting can show 288 allocated CPUs for a node although the task requests 256. Native workers are in-process children (historically 64 workers/factor64), **not** Slurm shards. Correction results are imported ledgers; filter, import, composition, admission, dedup and export remain one census job. There are no independently measured correction-reader/merge-shard budgets.

The earlier `scripts/harvest/clariden/filter_worker.sbatch` has different defaults: account `a0140`, **debug**, 1 node/task, **16 CPUs/task**, **00:45:00**. It accepts bundle, workspace, mode, output and manifest SHA; modes are inventory, prepare, qualify, census and census-preflight. It verifies bundle hashes, builds the frozen Rust predictor offline, runs regressions/parity, then calls `scripts/harvest/clariden/worker.py`. Full census02 used explicit **normal/256 CPU/six-hour overrides**. Do not submit its debug defaults assuming they are the four-hour census04 allocation.

Recorded workspace:

```text
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
$W/filter_pipeline_20261018/
  code/bb1ea164338b3068/                  archived census04 deploy
  prepared/87407ec7430a375f/             repaired census03 inputs/build
  attempts/census_02/census/             immutable historical ledger/export
  attempts/census_03/                    historical repaired census
  census_04_seg08/<attempt>/             census04 new outputs/tmp/cache
  census_04_seg08/logs/                  regression/parity/census Slurm logs
  runtime/                              predictor, Node, PNG codec manifests
```

Archived jobs require an **absolute** `CENSUS04_BUNDLE=$W/filter_pipeline_20261018/code/bb1ea164338b3068/docs/harvest/seg_census`; Slurm executes a spooled script, so the submit-directory layout is not a package locator. `jobs/common.sh` sets Python to `$W/venv_l1/bin/python` unless overridden, package `PYTHONPATH`, single-thread BLAS/OpenMP settings, and per-attempt `TMPDIR`/cache. New attempts and changed input bindings must never overwrite census02/03 or another attempt.

## 1. Verify deployment and inputs

1. Identify the exact source/build, tool map, codec and config. Check frozen parent hashes/counts, metadata/edition/orthography declarations, correction release statuses and source raster/crop identities. SPLIT1 is still a proposal; mode i keeps W1/W2 unassigned. A later mode ii needs a finalized approved file with `parent_id,row_id,edition_id,split` and its compressed-file SHA for gzip. No proposal-only `proposed_split` is an allocation.
2. Bind the actual runtime, selected Python/Node/predictor paths, source/assets and loaded native libraries. Keep the same runtime/crop bytes during comparisons. The original collector's PNG bytes require private **zlib-ng 2.3.3 compatibility mode**; system zlib gave different hashes. The thin worker verifies the library SHA from `runtime/png-codec.json` before `LD_PRELOAD`. The archived common script conditionally preloads the recorded file if present, so that shell conditional alone is not proof of a valid codec: actual runtime validation and strict crop witnesses must pass.
3. Verify a committed immutable deploy inventory and remote per-file SHA readback with the existing `../greek-page-ocr-wave2/scripts/ops/verify_deploy.py`. Use the exact historical verifier arguments in `docs/records/harvest/seg_census/FOLLOW_UP.md`: `--repo`, `--commit`, `--sha-file`, `--remote-root`, `--sbatch`, `--sbatch-args`, exact listed `--allow-untracked` payload exemptions and a receipt `--out`. Do not replace a failed readback with expected local hashes or weaken the verifier. Credential/certificate readiness must be observed by the actual check, not inferred from the old b2 certificate timestamp.
4. Each kind must return **VERIFY_OK** and a real `sbatch --test-only` result for the intended smoke binding. Scheduler dry-check job numbers are **not submissions**. Inspect all three receipts and independent readback before smoke. New source/config/split binding requires fresh applicable verification.

For the **historical archive only**, the final receipt already records 338/338 exact remote matches, all three VERIFY_OK and six smoke/full mode-i test-only successes. Evidence: `docs/records/harvest/seg_census/b2_evidence/{verify-regression.json,verify-parity.json,verify-census.json,remote_readback.tsv,test_only.json}`, `receipt_b2.json` and the final `b2` section in `receipt.json`. The earlier stopped SSH-banner attempt and the “not deployed” paragraph in FOLLOW_UP are preserved historical states, superseded by the final b2 receipt. There is no live re-verification in this documentation run.

The saved verifier invocation below is for that **historical source checkout and package**. Its commit is resolved from the source checkout at verification time; the verifier checks the declared manifest against committed bytes and rejects drift. Replacing its source directory with this integration checkout does not establish that the old deployed package matches new code.

```bash
REPO=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
COMMIT=$(git -C "$REPO" rev-parse HEAD)
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
REMOTE="$W/filter_pipeline_20261018/code/bb1ea164338b3068"
BUNDLE_REL=docs/records/harvest/seg_census
BUNDLE="$REMOTE/$BUNDLE_REL"
allow=()
while IFS= read -r path; do allow+=(--allow-untracked "$path"); done < "$REPO/$BUNDLE_REL/verifier_allow_untracked.txt"
for kind in regression parity census; do
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python -B \
    "$REPO/../greek-page-ocr-wave2/scripts/ops/verify_deploy.py" \
    --repo "$REPO" --commit "$COMMIT" \
    --sha-file "$BUNDLE_REL/DEPLOY_SHA256SUMS" --remote-root "$REMOTE" \
    --sbatch "$BUNDLE_REL/jobs/$kind.sbatch" \
    --sbatch-args="--export=ALL,W=$W,CENSUS04_BUNDLE=$BUNDLE,E4_SMOKE=1,CENSUS04_ATTEMPT=verify-mode-i" \
    "${allow[@]}" --out "/private/tmp/segcensus04-verify-$kind.json"
done
```

Top-level census CLI with no `--execute` only prints its declared inputs. Real `--validate-inputs-only` requires the execute path and records zero native decisions; it is an input-registration check, not smoke filtering. The historical all-parent preflight checked 592,466 rows; do not reduce that denominator to a small smoke and describe inputs as fully validated.

## 2. Run the bounded smoke, then inspect its publication

The recorded census04 smoke derives **up to 40 literal rows per parent**, up to 200 over the five production parents, and subsets correction ledgers while retaining source hashes. Regression and parity still run their full bounded fixtures. Mock plumbing tests used six fixture parents and 144-row smoke slices; 144 is not the production five-parent bound.

The following is the **recorded archived-build submission pattern**, from FOLLOW_UP. It is not a current-S4 deployment command and has not run here. The coordinator uses a new attempt suffix and performs the full stage later, after smoke review.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export CENSUS04_BUNDLE="$W/filter_pipeline_20261018/code/bb1ea164338b3068/docs/harvest/seg_census"
RUN_ROOT="$W/filter_pipeline_20261018/census_04_seg08"
mkdir -p "$RUN_ROOT/logs"
submit_census04() {
  local regression parity
  regression=$(sbatch --parsable --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/regression-%j.log" "$CENSUS04_BUNDLE/jobs/regression.sbatch")
  parity=$(sbatch --parsable --dependency="afterok:$regression" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/parity-%j.log" "$CENSUS04_BUNDLE/jobs/parity.sbatch")
  sbatch --dependency="afterok:$parity" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/census-%j.log" "$CENSUS04_BUNDLE/jobs/census.sbatch"
}
unset CENSUS04_SPLIT_FILE CENSUS04_SPLIT_SHA256 CENSUS04_CONFIG
export E4_SMOKE=1 CENSUS04_ATTEMPT=smoke-mode-i-001
submit_census04
```

Inspect regression/parity success and dependency accounting, exact version/config/runtime fingerprints, `job-policy-parity.json`, prepared `inputs/config.json`, and final `CURRENT.json`/summary/output hashes. Check expected parent coverage, explicit exclusion reasons, no UNPROCESSED/INFRA_ERROR rows, and no fictitious correction approvals. Mode i must not admit W1/W2 into train. Dev/test rows remain diagnostics. Match `current`/all aliases to the same immutable generation and reconcile output row counts. A Slurm COMPLETED state alone is insufficient.

The archived package's saved native parity was 150+888 exact verdict/reason matches against **0.8** references. Its 200-row mocked full-pipeline results used synthetic no-change reader outcomes and verified saved native measurements: they validate plumbing, not reader quality or production retention. For current segmentation 0.13 (label 0.9-s5), the older 0.5/0.8 parity launcher cannot certify changed geometry; use the exact current reference/test evidence and preserve any intended changes instead of claiming unchanged verdicts.

## 3. Full census is a separate stage

After successful smoke inspection for that same intended build and mode, the archived full invocation uses:

```bash
export E4_SMOKE=0 CENSUS04_ATTEMPT=full-mode-i-001
submit_census04
```

The function must already be defined in the verified archived-build environment above. Full preparation preserves all five parent paths/hashes/counts, metadata, policy and correction releases. When a final split is later available, pin `CENSUS04_SPLIT_FILE` and `CENSUS04_SPLIT_SHA256`, verify mode ii separately, and smoke it before a new mode-ii full attempt. The finalized join may change only the documented split/edition identities and derived evidence bindings; original correction status/edits/holds remain. Train assignment is not automatic admission.

Current top-level full runs need a separate verified package and config, with their own output root/version evidence; the archived function is not a shortcut for that work. The current docs-only scope leaves this operational preparation unperformed.

## Output acceptance and FAILED diagnosis

| Observation | Check and interpretation |
|---|---|
| Slurm FAILED, CANCELLED, TIMEOUT or dependency never satisfied | Read job and step accounting (`sacct`), exit codes, exact log, requested partition/time and upstream `afterok` results. Identify whether failure was registration, runtime startup, native filtering or export. Keep the failed attempt. |
| `unknown split` / legacy alias errors | Inspect frozen parent split versus literal row/book/row_splits declarations. The census01 failure was a registration defect with zero native decisions. Never default unknown cohorts to train. |
| Parent count/SHA or row identity mismatch | Compare exact input manifest, duplicate IDs, metadata/crop maps and registration receipt. Stop before substituting/rebuilding a parent; a new binding requires a new ledger. |
| Missing component/runtime/predictor or SHA mismatch | Compare deployed files against manifest, selected executable paths, loaded runtime and codec/preload hashes. Existing ledgers reject drift even on cached resume. Do not edit manifests to match an unexpected runtime. |
| Reconstructed crop SHA mismatch | Check source image SHA, box, grayscale/encoding contract and zlib-ng preload. No tolerance for “same pixels” when the encoded frozen SHA differs. |
| Crop unavailable / invalid geometry | Separate bound-byte absence from protocol/invalid evidence. Expected unavailable crop evidence yields segmentation UNCERTAIN/HOLD; infrastructure exceptions give `infrastructure_or_invalid_evidence` / INFRA_ERROR. Collector cache-plane/envelope issues are recorded in `collect_v3/KNOWN_ISSUES.md`. |
| Native timeout or protocol failure | Check row timeout, child cleanup/restart, hard request/response deadline, runtime counters and worker/prefetch bound. Do not promote a timed-out row as a measured scientific DROP. |
| Correction/proposal HOLD | Inspect parent/raw/crop/split/version/digest and producer holds, missing coverage, SF7 audit status and pending queue. Sparse omission never equals no change. Corrector queues are work remaining, not errors to suppress. |
| Split-only HOLD | Expected for unassigned W1/W2 in mode i. Supply only finalized sourced edition assignments in a new bound run; do not force train. |
| Slurm success but missing/mismatched `CURRENT.json` or `complete=false` | Inspect durable inventory/rows/dedup/export phases, generation and summary SHA. A partial export or stale root alias is not a completed publication. |

Read-only remote investigation should identify the exact attempt before any action; no live SSH or scheduler inspection was performed here. On a recoverable same-binding interruption, retain `ledger.sqlite` and verified native measurements. `--retry-errors` retries infrastructure rows; `--retry-holds` retries HOLD evidence under the unchanged binding. Changed metadata, corrections, splits, source or runtime require a new attempt/ledger, keeping earlier receipts and generations. Final summary must reconcile all 592,466 frozen input rows for these five parents, report ADMIT/DROP/HOLD/remaining work separately, and preserve evaluation membership. A complete diagnostic census is not a training launch or correction audit pass.

## Sources read

- `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`; `docs/harvest/line_pipeline/tool_versions.json`.
- `greekocr/harvest/{line_pipeline,line_pipeline_census,line_pipeline_native,line_pipeline_sources}.py`.
- `scripts/harvest/clariden/filter_worker.sbatch`.
- `docs/records/harvest/seg_census/{JOB_KINDS.md,FOLLOW_UP.md,HANDOFF_SEGCENSUS1.md,receipt.json}`.
- `docs/records/harvest/seg_census/jobs/{common.sh,regression.sbatch,parity.sbatch,census.sbatch}`.
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py`.
- `docs/records/harvest/seg_census/remote_evidence/{accounting_and_config.txt,census03_config.json,runtime.json,HANDOFF.md,integration_fixes.diff}`.
- `docs/harvest/line_pipeline/{README.md,pipeline.mmd}`; `docs/harvest/line_pipeline/clariden/{CENSUS_02_STATUS.md,census_02-status.json}`.
- `docs/records/harvest/collect_v3_admission/{split1/SPLIT_PROPOSAL.md,HANDOFF_20261018_sourcing.md}`; `docs/records/harvest/collect_v3/KNOWN_ISSUES.md`.
- `docs/records/harvest/seg_steps/s4/{receipt.json,summary.json}` (current version/replay evidence).
- `docs/records/harvest/seg_census/receipt_b2.json`; `docs/records/harvest/seg_census/b2_evidence/verify-census.json`.
- `greekocr/harvest/{line_pipeline_adapters,line_pipeline_parallel,line_pipeline_runtime}.py`.
