# Census_05 follow-up — C readout fix and new deployment

The C deployment and local readouts have occurred; see the C section in HANDOFF_CENSUS05.md and c_evidence/. No Slurm submission has occurred. The earlier B recipe below is historical; do not execute its input-copy steps for C. The lead commits the exact pathspec first. The commands below use Bash. `CODE_SHA` binds the source origin; `PROJECTS_SHA256` is the file-level re-pointing contract.

## Deploy and input readback (CENSUS05-B)

Run locally, after the lead commit, with the existing Clariden connection. Refuse a non-empty code destination; no overwrite of an existing payload is authorized by this recipe. The copy preserves repository-relative paths, exactly as the unchanged verifier requires.

```bash
set -euo pipefail
REPO=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
REL=docs/harvest/census05
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
PID=17b0eb1ca7fe81a7
REMOTE="$W/census_05_20261020/code/$PID"
BUNDLE="$REMOTE/$REL"
COMMIT=$(git -C "$REPO" rev-parse HEAD)
python3 -B "$REPO/$REL/verify_projects.py" --revision 3b4090bf9b15d2d2cac53ee55161e936157ec0e5
ssh clariden "mkdir -p '$REMOTE'; test -z \"\$(find '$REMOTE' -mindepth 1 -print -quit)\""
rsync -a --files-from="$REPO/$REL/DEPLOY_PATHS.txt" "$REPO/" "clariden:$REMOTE/"
ssh clariden "cd '$REMOTE' && sha256sum --check --quiet -" < "$REPO/$REL/DEPLOY_SHA256SUMS"

# Restore ignored full-size ledger files if checking out this package elsewhere.
python3 -B "$REPO/$REL/restore_inputs.py"
ssh clariden "mkdir -p '$W/census_05_20261020/inputs'"
# Each entry is a new numerics ledger or the finalized compressed split.
python3 - "$REPO/$REL/INPUTS.json" <<'INPUTS'
import hashlib,json,pathlib,subprocess,sys
for item in json.loads(pathlib.Path(sys.argv[1]).read_text()):
    path=pathlib.Path(item['local_path'])
    with path.open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256']
    remote=item['remote_path']
    # Refuse overwriting an existing input, even one with the same name.
    subprocess.run(['ssh','clariden',"test ! -e '"+remote+"'"],check=True)
    subprocess.run(['rsync','-a',str(path),'clariden:'+remote],check=True)
    subprocess.run(['ssh','clariden','sha256sum --check --quiet -'],input=(item['sha256']+'  '+remote+'\n').encode(),check=True)
INPUTS
```

The split is **not in the code package**: local sourcing `../greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/split2/row_split.jsonl.gz` → `$W/census_05_20261020/inputs/row_split.jsonl.gz`, compressed SHA256 `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82`. `INPUTS.json` names all five new ledger paths, byte sizes and hashes. Standing cyrillic, parents, metadata and held-out/frozen inputs remain at census_03 paths. Compressed correction chunks are gitignored; durable copy at the data root, receipt `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archive_receipt.json`, checksums `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/ARCHIVES_SHA256SUMS`, archives `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archives/`, outside DEPLOY_PATHS; `restore_inputs.py` restores their exact bytes locally.

## Unchanged verifier

Require a real VERIFY_OK for every named batch kind; no ignored deploy payload or verifier exemption exists. The request says “all five”, but names four `.sbatch` kinds plus `common.sh`; `common.sh` is sourced, not a fifth job. These four checks cover all named jobs and the shared file through the same SHA manifest. Do not invent a fifth batch job.

```bash
for kind in regression parity census readout; do
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python -B \
    "$REPO/../greek-page-ocr-wave2/scripts/ops/verify_deploy.py" \
    --repo "$REPO" --commit "$COMMIT" \
    --sha-file "$REL/DEPLOY_SHA256SUMS" --remote-root "$REMOTE" \
    --sbatch "$REL/jobs/$kind.sbatch" \
    --sbatch-args="--export=ALL,W=$W,CENSUS05_BUNDLE=$BUNDLE,E4_SMOKE=1,CENSUS05_ATTEMPT=verify-smoke,CENSUS05_EXPECT_ROWS=200" \
    --out "$REPO/$REL/verify-$kind.json"
done
```

The production config uses `@CENSUS05_PROJECTS@` as a relocation marker. `prepare_config.py` resolves it to this deployed package's absolute `package/projects/` directory. No tool manifest byte changes. Gitignored native `target/` is not deploy payload: the regression wrapper makes only a runtime symlink to the existing census_03-bound predictor. Native binaries, Node and codec remain remote inputs.

## Coordinator smoke and full chains

On Clariden, after deploy readback and verifier success. CENSUS05-B must read `scontrol show partition debug`; replace `DEBUG_TIME_FROM_CENSUS05_B` with an actual duration within that limit before executing smoke. In-script production settings stay `normal`, 1 node/task, 256 CPUs and 5/5/240 minutes; readout uses 16 CPUs and 30 minutes.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export CENSUS05_BUNDLE="$W/census_05_20261020/code/17b0eb1ca7fe81a7/docs/harvest/census05"
RUN_ROOT="$W/census_05_20261020"
mkdir -p "$RUN_ROOT/logs"
submit_census05() {
  local regression parity census readout
  regression=$(sbatch --parsable "$@" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/regression-%j.log" "$CENSUS05_BUNDLE/jobs/regression.sbatch")
  parity=$(sbatch --parsable "$@" --dependency="afterok:$regression" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/parity-%j.log" "$CENSUS05_BUNDLE/jobs/parity.sbatch")
  census=$(sbatch --parsable "$@" --dependency="afterok:$parity" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/census-%j.log" "$CENSUS05_BUNDLE/jobs/census.sbatch")
  readout=$(sbatch --parsable "$@" --dependency="afterok:$census" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/readout-%j.log" "$CENSUS05_BUNDLE/jobs/readout.sbatch")
  printf 'regression=%s parity=%s census=%s readout=%s\n' "$regression" "$parity" "$census" "$readout"
}
unset CENSUS05_RUN CENSUS05_READOUT_OUT CENSUS05_CONFIG CENSUS05_BASELINE
export CENSUS05_SPLIT_FILE="$W/census_05_20261020/inputs/row_split.jsonl.gz"
export CENSUS05_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS05_ATTEMPT=smoke-split-001 CENSUS05_EXPECT_ROWS=200
submit_census05 --partition=debug --time=DEBUG_TIME_FROM_CENSUS05_B

# Separate coordinator action, only after smoke review and P3's gates pass.
# This uses the normal partition and each script's original production time.
export E4_SMOKE=0 CENSUS05_ATTEMPT=full-split-001 CENSUS05_EXPECT_ROWS=592466
# Optional real census_03 summary supplies the readout's baseline delta table.
export CENSUS05_BASELINE="$W/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json"
submit_census05
```

Smoke without split is also supported: use a fresh attempt, unset both split variables, and E4_SMOKE=1. **Full without either split variable refuses before pipeline execution.** No silent mode-i full fallback. Fake split data exists only in the local mock fixture.

## Expected publication and P4 report

Per attempt: `$W/census_05_20261020/attempts/$CENSUS05_ATTEMPT/` contains `CURRENT.json` with status `completed`, a matching generation/run binding and summary hash, then the published generation's `decisions.jsonl`, `admitted_train.jsonl`, `admission_records.jsonl`, `evaluation_diagnostics.jsonl`, `pending_{polytonic,cyrillic,numerics,content_repair}.jsonl`, and `summary.json`. Compatibility links expose the published files at the attempt root. `complete: true`, reconciled input/decision counts (200 smoke, 592466 full), correct pinned versions, zero held-out leaks and no INFRA_ERROR are required. Admissions and per-reason numbers are actual run outputs, never inferred from the mock.

The readout writes **outside** the run, to the sibling `$W/census_05_20261020/attempts/$CENSUS05_ATTEMPT.readout/{READOUT.md,readout.json}`. It must be complete with all invariants PASS and pipeline version 0.3.2. No output is moved into the run directory. This later explicit sibling rule supersedes section 4's older inside-attempt wording.

P4 consumes READOUT.md sections: disposition/reason counts, content-gate reasons and exclusions, overlapping pipeline reasons, route status and toolchain versions, segmentation availability, pending work, input/output strata, split/source/role/script partitions, held-out/leakage checks, optional baseline deltas, timing, diagnostics and file provenance. Exact table titles are enumerated in HANDOFF_CENSUS05.md. Report the full last line verbatim:

```text
CENSUS READOUT: rows <n> (complete yes); ADMIT <a> HOLD <h> DROP <d>; admitted_train <t>; gate DROP <gd> HOLD <gh> (mixed <m> foreign <f> short <s> cell1 <c> num1 <u> unresolved <r>); pending content_repair <n>, cyrillic <n>, numerics <n>, polytonic <n>; heldout leaks 0; invariants 14/14 PASS
```

Reason counts overlap: include both deciding-stage rows and overlapping-reason tables; do not sum overlapping reasons as disjoint dispositions. Corrections_not_applied for polytonic is separate from pending work. Record every invariant and raw source hash from readout.json.

## Re-point after local merge to main

Run read-only, after main carries the proposed source tree. A differing source byte means **rebuild**, even if only one tool component changes. Later docs/state commits outside packaged source paths do not break the contract.

```bash
CODE_SHA=3b4090bf9b15d2d2cac53ee55161e936157ec0e5
paths=()
while IFS= read -r line; do paths+=("${line#*  }"); done < "$REPO/$REL/PROJECTS_SHA256"
git -C "$REPO" diff --quiet "$CODE_SHA" main -- "${paths[@]}"
python3 -B "$REPO/$REL/verify_projects.py" --revision main
```

The helper recomputes SHA256 from `git show main:<repository-path>` for every PROJECTS_SHA256 entry; it also repeats the exact scoped git diff. The thirteen additive payload files have separate hashes in additive_files.json and DEPLOY_SHA256SUMS. The authorized readout patch targets the relocated CODE_SHA paths under `docs/records/harvest/census05/readout/`; the package mirror lives under `docs/harvest/census05/readout/`. Apply readout_fix.patch (superseding readout_version.patch) as the coordinator's separate docs-only merge; no production module changes.

## SF7/TR2

Polytonic is out of scope tonight. Its four ledgers are not bound. When SF7's audit passes, a later census restores the polytonic route and rebinds its ledgers at the then-current status. Nothing is prepared to apply tonight. No superseded producer release is referenced by the ten bound ledgers.


## C: readout fix + redeploy


New package **997b7d2ab5a8775b**, 167 files; bundle `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/997b7d2ab5a8775b/docs/harvest/census05`. No submission and no .git writes. Old B evidence and command block above remain historical. C smoke uses **--partition=debug --time=00:30:00** for all four kinds; full retains the packaged limits.

Changes since the Astra review:

- H1: `readout/census_readout.py` mirrors packaged `line_pipeline_census.py:167–171`; configured crops union observed dev/test crops, plus existing protected editions. `test_astra_config_only_crop` reproduces the one-row witness: leaks 1, exit 1; without configuration: leaks 0, exit 0.
- L1: `admitted_train_equals_eligible` mirrors packaged `line_pipeline_census.py:204–214`, using inventory train split and ADMIT decisions, exact row content hashes and unique identities. The subset invariant stays. `test_astra_missing_export` (three eligible decisions, empty export) fails with exit 1. `test_export_equality` also covers duplicates and changed row contents.
- M2: `readout/test_census_readout.py` finds its own repository root, skips absent historical fixtures with their paths in the reason, and writes all outputs and receipts to `tmp_path`. Synthetic successful exports now contain every eligible row. Tests: **28 passed in 31.23s** (0 failed, 0 skipped); packaged regression: **360 passed, 9 skipped in 3.11s** (0 failed). Logs in `c_evidence/`.
- M3: `INPUTS.json`, this handoff and `REVIEW_INPUTS.md` record durable archive custody; `c_evidence/archives.json` verifies **35/35** hashes against the original receipt and data-root checksum list.

`readout_fix.patch` targets `docs/records/harvest/census05/readout/` and supersedes `readout_version.patch`: it includes both the prior pipeline-version fix and these changes (including the prior wrapper change). No pipeline source changes. The 154 CODE_SHA-identical files and PROJECTS_SHA256 are byte-identical; DEPLOY_PATHS.txt was regenerated with identical bytes. The deployed payload changes only `readout/census_readout.py`; tests change locally but were never part of the deploy manifest. Updated manifests are DEPLOY_SHA256SUMS, additive_files.json and package_id.json.

Deployment completed into the new empty destination only. `c_evidence/readback.json`: **178/178** hashes match (167 payload, six unchanged inputs rehashed in place, five standing Cyrillic ledgers). No input copies or writes to the old package. Four unchanged verifier invocations and eight scheduler dry checks have receipts in `c_evidence/`; verifier status must be read there, not inferred from readback. The verifier requires a lead commit: it rejects tracked dirty files and payload bytes differing from HEAD. C must not be marked READY until all four are VERIFY_OK after the lead commits.

Mock readout last lines (synthetic generations, not production):

```text
CENSUS READOUT: rows 200 (complete yes); ADMIT 43 HOLD 128 DROP 29; admitted_train 43; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 15/15 PASS
CENSUS READOUT: rows 200 (complete yes); ADMIT 119 HOLD 39 DROP 42; admitted_train 103; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 15/15 PASS
CENSUS READOUT: rows 200 (complete yes); ADMIT 119 HOLD 39 DROP 42; admitted_train 103; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 15/15 PASS
```

Coordinator commands prepared only; require a successful unchanged verifier and owner review before actual submission:

```bash
# C COORDINATOR COMMANDS — NOT EXECUTED; REQUIRE VERIFY_OK AND REVIEW
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export CENSUS05_BUNDLE="$W/census_05_20261020/code/997b7d2ab5a8775b/docs/harvest/census05"
RUN_ROOT="$W/census_05_20261020"
mkdir -p "$RUN_ROOT/attempts" "$RUN_ROOT/logs"
submit_census05() {
  local regression parity census readout
  regression=$(sbatch --parsable "$@" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/regression-%j.log" "$CENSUS05_BUNDLE/jobs/regression.sbatch")
  parity=$(sbatch --parsable "$@" --dependency="afterok:$regression" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/parity-%j.log" "$CENSUS05_BUNDLE/jobs/parity.sbatch")
  census=$(sbatch --parsable "$@" --dependency="afterok:$parity" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/census-%j.log" "$CENSUS05_BUNDLE/jobs/census.sbatch")
  readout=$(sbatch --parsable "$@" --dependency="afterok:$census" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/readout-%j.log" "$CENSUS05_BUNDLE/jobs/readout.sbatch")
  printf 'regression=%s parity=%s census=%s readout=%s\n' "$regression" "$parity" "$census" "$readout"
}
unset CENSUS05_RUN CENSUS05_READOUT_OUT CENSUS05_CONFIG CENSUS05_BASELINE
export CENSUS05_SPLIT_FILE="$W/census_05_20261020/inputs/row_split.jsonl.gz"
export CENSUS05_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS05_ATTEMPT=smoke-split-001 CENSUS05_EXPECT_ROWS=200
submit_census05 --partition=debug --time=00:30:00

# Separate coordinator action, only after smoke review and P3's gates pass.
# This uses the normal partition and each script's original production time.
export E4_SMOKE=0 CENSUS05_ATTEMPT=full-split-001 CENSUS05_EXPECT_ROWS=592466
# Optional real census_03 summary supplies the readout's baseline delta table.
export CENSUS05_BASELINE="$W/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json"
submit_census05
```

C verifier result: **0/4 VERIFY_OK**, all four **VERIFY_FAIL** solely for tracked uncommitted changes and the new readout differing from HEAD. No bypass was used. Lead commit required; then rerun `python3 -B docs/harvest/census05/c_evidence/verify.py`. Scheduler test-only results: smoke **4/4**, full **4/4**, smoke debug **00:30:00**. `c_evidence/protection_recount.json` independently confirms 9,119 configured hashes, 2,215 observed overlap, and **6,904 config-only hashes**.
