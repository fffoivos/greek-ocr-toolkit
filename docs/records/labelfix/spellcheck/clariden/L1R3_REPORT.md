# L1R3b — SF6c recomposition, evidence inventory, HOLD and deletion census

17 October 2026. **READY for coordinator submission. Deployed and SHA-verified on Clariden; both `sbatch --test-only` checks passed. No job was submitted.** Full-population evidence coverage will be measured inside job 2 and is **expected to be ~0% from the first saved records**, as directed in the [L1R3b brief](../../../briefs/L1R3b_finish.md). This expectation is not a measured production percentage.

## Frozen scope and policy

This worktree is `greek-ocr-toolkit-spellcheck-l1r3`, branch `opus/spellcheck-l1r3`, HEAD **`351e2d70a0fd7990089be462101a5697b2198863`**. All **30 tracked files under `greekocr/labelfix/` remain byte-identical to `d893a04d`**. The supplied merged `l1_common.py` is unchanged. All eight worktree Git metadata files match the start of this session; no Git writes or other-worktree writes were made. [Session starting hashes](L1R3_evidence/l1r3b_protected_before.json), [final verification](L1R3_evidence/protected_unchanged.json).

| Binding | SHA-256 |
|---|---|
| Frozen SF6c `release_gate.py` | `9ef1d6467229e86c9464f428716c792f2a6fc4ffa1e709b798df82c504120408` |
| Original SF6c source-bound policy | `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406` |
| Supplied merged `l1_common.py`, unchanged | `53385120c265c31f1a512c19bc9c2ab2cd12f0e4f2eef07275ce94003adfdaed` |
| L1R3 packaging-bound policy | `82f8d5423f88fdc05546ea834a878ce07c51399f60b7cb1150597db70be59363` |

The policy is `sf6-release-v1`. Its digest binds the merged consumer and recomposition packaging; the gate bytes remain SF6c. The source maps and file hashes bind this exact deployment. The inherited recomposition `code_commit` label is descriptive historical metadata, not a replacement for those bindings. Existing SF4/SF5 census pins remain; SF6 accepts only SF6c's exact gate hash, and the deletion census requires SF6.

The prior L1R3 preparation repaired stale SF5 policy/fixture dependencies without weakening gate assertions; its baseline was 173 failed / 1,318 passed. [Prior baseline](L1R3_evidence/tests_baseline.log), [restored fixture hashes](L1R3_evidence/restored_sf5_fixture.json). The current suite is **1,524 passed**.

The [CSCS skill](/Users/foivoskarounos-zamparloukos/.codex/skills/optimize-apertus-cscs/SKILL.md) was read for Clariden checks. This is experiment-owned packaging and analysis. Network access was limited to Clariden SSH, including its configured gateway. No credential refresh, inference, detector run, allocation or submission occurred. The certificate was inspected locally and remains valid until 17 October 2026, **19:18:52 Europe/Athens**. Deployment, preflight and readback each succeeded on the first attempt; no retries were needed. The coordinator helper allows at most three transient retries per step with 2/4/8-second backoff and stops immediately on authentication/certificate failures.

## Evidence availability — measured first in job 2

**The full-population inventory was removed from the login-node preflight.** [`l1r2_census.py`](../../../../../scripts/labelfix/clariden/l1r2_census.py) now runs [`l1r3_evidence.py`](../../../../../scripts/labelfix/clariden/l1r3_evidence.py) as its first stage, inside job 2's `srun`. The combined receipt seals `evidence_availability.json` alongside both census receipts and binds the inventory code and configuration. Production inventory requires a Slurm allocation; the CLI allows an outside-allocation mock only for the complete 64-line verification population.

The inventory streams **both complete saved populations**, L1-v0 and L1E, using at most two worker processes. It joins each runtime ID to the hash-bound selection for its wave, rejects duplicate/unselected/missing IDs or missing/extra shards, hashes compressed input bytes during reading, and compares every shard digest with job 1's verified input map. Each source has overall and **per-wave** results containing:

- Lines and detector slots; **omitted (`missing_key`), null, invalid and explicit** confidence counts for both units. Explicit means a finite numeric value in `[0,1]`, excluding booleans. Separate above-floor counts require `0.5 < confidence <= 1`.
- The same line/slot presence-state counts for `recognition_evidence` and `image_width`; a valid explicit width is finite and positive. Regional availability includes nonempty-region line counts, region counts and slots with a matching saved region start. Availability alone does not establish certification.
- Lines with at least one certified slot, certified slot counts and line/slot percentages, obtained by calling **SF6c's frozen `_recogniser_scored(runtime, slot, saved_window)` for every slot**. Malformed structures that make the predicate raise are counted separately as predicate errors and never counted as certified.

The allocation-stage inventory has a **900-second budget**; timeout or input mismatch prevents a new complete combined receipt. It performs no composition, inference or detector work. Missing values are not filled in. The subsequent HOLD and deletion censuses retain their output-DAG verification, original-label checks, durable partials, and consensus-elision zero requirement.

The earlier saved-record observations were:

| Source | Shards | Compressed bytes | First record |
|---|---:|---:|---|
| L1-v0 `output_3679313/combined/` | 974 | 1,851,684,318 | All three certification keys omitted; 56 slots |
| L1E `l1e_20261017/output_3679545/inference/` | 974 | 838,524,512 | All three certification keys omitted; 56 slots |

The omitted keys were `recognition_confidence`, `recognition_evidence`, `image_width`, rather than numeric zero or JSON null. These records, together with the supplied history that SF6c added the fields tonight, support the **~0% expectation**; they do not establish a population fraction. [Earlier probe receipt](L1R3_evidence/remote_evidence_probe.json). The current remote preflight verified the input receipt DAG for **124,669 lines / 974 shards / 8,784 input hashes**, without running the evidence census.

The current job-2 mock measures **0/64 explicitly scored lines, 0/1,905 explicitly scored slots and 0/1,905 certified slots in each saved source**, all in `heldout-verification`. Both sources omit all three fields on all 64 lines. These are fixture-only percentages. [Full two-source inventory](L1R3_evidence/mock_runtime_evidence.json).

SF6c's exact threshold is **strictly greater than 0.5**, at line and regional level. Certification also needs scored saved-alignment provenance, matching text/alignment identity, native image bounds, whole-window coverage and contained source spans. Missing certification supplies **no recogniser absence signal**. Recomposition preserves the original optional-field presence and values, including omission versus null.

**Expected effect:** punctuation deletion requiring recogniser absence will HOLD without certification. Combining-mark deletion can still pass with the required reader plus detector evidence when the saved observation/span contracts qualify. A valid same-kind capital-breathing MOVE remains an exception. This package neither recovers confidence nor runs recognition; production release yield remains unmeasured.

## Jobs and outputs

Deploy directory: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6/`.

Job 1 runs the unchanged recomposition entry point with original input/receipt verification, final input rehashing, 32 shard workers, durable exact-binding receipts, paired corrected/control releases, HOLD exclusion, original-label hashes, per-wave/source coverage, aliases, elision census and the ensemble caveat. Releases end in `-sf6`.

Job 2 runs the evidence inventory first, then the existing HOLD and SF6c deletion censuses. It imports the frozen gate only for the inventory's certification predicate and performs no recomposition. Per mode × wave, `CHANGES.json`/`.md` include:

- `sf6_deletion_held_lines` and `sf6_deletion_holds_by_class` for mark, apostrophe, quote, keraia and other; distinct line counts, blocked-atom counts and examples must agree with exact `sf6:deletion_needs_two_positive_absences:*` HOLD reasons. Class line counts overlap.
- Proposed MOVEs separately from `sf6_move_lines_applied` / `sf6_move_exceptions_applied` on actual corrected releases.
- Real mark-correction lines: corrected labels with NFD combining-mark edits, excluding alias-only and punctuation-only changes.

**`changes/real_mark_correction_lines.jsonl`** contains every real mark-correction `line_id`, `wave`, `mode`, without the example cap. Its shard and merged hashes, deduplication and per-wave totals are checked. **Draw the future 100-line audit from this production job-2 list**, with mode filtering or line-ID deduplication as required.

```text
.../labelfix_l1_20261017/l1e_20261017/l1r_sf6_<JOB1>/
  input_verification.json
  shards/shard-NNNNN/{selection.jsonl,release/*,receipt.json}
  release/{overlay_*.jsonl.gz,ctrl_subset_*.jsonl.gz,kept_*_line_ids.txt,release_*.json}
  receipt.json

.../labelfix_l1_20261017/l1r_sf6/census/output_<JOB1>_<JOB2>/
  evidence_availability.json
  hold/{CENSUS.json,CENSUS.md,binding.json,input_verification.json,partials/*,receipt.json}
  changes/{CHANGES.json,CHANGES.md,real_mark_correction_lines.jsonl,
           binding.json,input_verification.json,partials/*,receipt.json}
  receipt.json
```

Both scripts use account `a0140`, partition `debug`, one node/task. Job 1 requests 64 CPUs, 32 workers, exclusive, a one-hour limit; job 2 requests 16 CPUs/workers and a 30-minute limit, with at most two concurrent inventory streams. The scheduler dry runs predict 288 allocated processors for either job. The live debug limit was 1:30:00. Based on historical L1R2's 7 + 1 minutes and the earlier full-decoding estimates of about 289/146 seconds for the two inventory sources, allow **20 minutes after allocation starts**, excluding queue delay. This is an estimate, not a full-population SF6 timing result.

## Fresh mocks and validation

Both exact Python entry points ran on the complete 64-line verification runtime; no production data was transferred to the Mac.

```bash
PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  scripts/labelfix/clariden/l1r_mock_check.py \
  --config artifacts/labelfix_l1r3/mock.json \
  --out artifacts/labelfix_l1r3/mock_l1r3b \
  --evidence docs/records/labelfix/spellcheck/clariden/L1R3_evidence

PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  scripts/labelfix/clariden/l1r2_census.py \
  --config artifacts/labelfix_l1r3/mock.json \
  --input-dir artifacts/labelfix_l1r3/mock_l1r3b \
  --out artifacts/labelfix_l1r3/mock_l1r3b_census --workers 2
```

Job 1: **2.747 seconds**, exact SF6c parity **256/256 mode/line decisions and 7,620/7,620 slot/mode decisions**. The three releases also match all 192 mode/line decisions, 5,715 slot decisions and serialized deletion checks. Job 2, including both inventories: **0.606 seconds**, all three receipt outputs hash-verified. [Parity](L1R3_evidence/mock_parity.json), [job-1 log](L1R3_evidence/mock_l1r3b.log), [job-2 log](L1R3_evidence/mock_census_l1r3b.log), [combined receipt](L1R3_evidence/mock_census_receipt.json), [independent counts](L1R3_evidence/mock_independent_checks.json).

| Mode | Real mark-correction lines | Release HOLD lines | SF6 deletion HOLD lines | Mark / apostrophe / quote / keraia / other HOLD lines | Applied MOVEs |
|---|---:|---:|---:|---|---:|
| PRESENCE | 2 | 61 | 39 | 36 / 1 / 3 / 0 / 3 | 0 |
| FULL | 2 | 62 | 39 | 36 / 1 / 3 / 0 / 3 | 0 |
| ENSEMBLE_AB | 2 | 58 | 39 | 36 / 1 / 3 / 0 / 3 | 0 |

The fixture audit list has six mode/line rows and two unique IDs. These counts do not establish production yield or MOVE frequency. [Audit list](L1R3_evidence/mock_changes_real_mark_correction_lines.jsonl), [changes](L1R3_evidence/mock_changes_CHANGES.json), [HOLD census](L1R3_evidence/mock_hold_CENSUS.json).

**1,524 tests passed in 13.69 seconds**, with no skips or deselections. New coverage includes confidence omission/null/invalid/explicit states, booleans/NaN/out-of-range scores, exact floor boundaries, malformed and mismatched regional evidence, selected-wave completeness, changed input hashes, allocation guarding, inventory-before-census ordering and the combined receipt binding. Existing gate/parity, HOLD, MOVE, integrity, restart/corruption and consensus-elision assertions remain. [Suite log](L1R3_evidence/tests_l1r3b_labelfix.log).

```bash
PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  -m pytest -q tests/labelfix -p no:cacheprovider
```

Both sbatch scripts and the preflight pass `bash -n`; all packaged Python files parse, and `git diff --check` passes.

## Verified deployment and scheduler dry runs

The [archive](../../../../../artifacts/labelfix_l1r3/L1R3_deploy.tar) contains **335 payload files plus the manifest**, with no AppleDouble sidecars. The unchanged production config and six external pins remain bound. All local/archive members match; all **335/335 remote hashes pass both before and after preflight**. The returned `L1R3_DEPLOY_SHA256.txt` is byte-identical to the local manifest. All six external pins and the complete SciPy manifest check pass; the real input verifier completes. The returned 331-file source map equals the mock's source map and deployed manifest, and remote/local policy bindings match. [Local receipt](L1R3_evidence/deployment_local.json), [remote receipt](L1R3_evidence/deployment_remote.json).

`L1R3_DEPLOY_SHA256.txt` SHA-256: **`e9976587d148d506f03fbd654ffd75e4dc812bd7d6ea26d81a264b03de50c325`**.

These commands were executed successfully, from this worktree:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=20 clariden \
  'mkdir -p /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6/logs; tar -xf - -C /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6' \
  < artifacts/labelfix_l1r3/L1R3_deploy.tar
ssh -o BatchMode=yes -o ConnectTimeout=20 clariden \
  'bash /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6/scripts/labelfix/clariden/l1r3_preflight.sh'
```

The actual coordinator adds `ConnectionAttempts=1`, `ServerAliveInterval=15`, `ServerAliveCountMax=2` and the bounded retry policy above. [Deployment attempt](L1R3_evidence/remote_l1r3b/deploy.json), [preflight attempt](L1R3_evidence/remote_l1r3b/preflight.json), [readback attempt](L1R3_evidence/remote_l1r3b/readback.json).

The login preflight hashes inputs, records policy/source bindings and runs exactly these scheduler checks; **it does not run `l1r3_evidence.py`**:

```bash
sbatch --test-only scripts/labelfix/clariden/l1r_job.sbatch
sbatch --test-only scripts/labelfix/clariden/l1r2_census_job.sbatch 3680629
```

Job 1 dry-run identifier: **3680720**. Job 2 dry-run identifier: **3680721**. Both predicted a start on `nid005421`, partition `debug`. These are test-only results, not submitted job IDs. The numeric argument `3680629` is a historical job-1-shaped payload argument only; it does not request a stale dependency. A real `afterok` dependency requires the actual future job 1 ID. [Job-1 result](L1R3_evidence/remote_l1r3b/verified/preflight/job1_test_only.log), [job-2 result](L1R3_evidence/remote_l1r3b/verified/preflight/job2_test_only.log), [empty queue readback](L1R3_evidence/remote_l1r3b/verified/preflight/squeue_after.txt).

## Exact coordinator submit commands — prepared, NOT executed

Run **on Clariden only after separate submission authorization**:

```bash
set -euo pipefail
L1R3_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6
cd "$L1R3_ROOT"
sha256sum --check L1R3_DEPLOY_SHA256.txt
JOB1=$(sbatch --parsable scripts/labelfix/clariden/l1r_job.sbatch)
JOB1=${JOB1%%;*}
JOB2=$(sbatch --parsable --dependency=afterok:"$JOB1" \
  scripts/labelfix/clariden/l1r2_census_job.sbatch "$JOB1")
JOB2=${JOB2%%;*}
printf 'L1R3_JOB1=%s\nL1R3_JOB2=%s\n' "$JOB1" "$JOB2"
```

## Exact pull commands — after successful completion

Run on the Mac in this worktree, replacing both IDs with real submitted IDs. Pulls include the production inventory and complete audit population, alongside small manifests, receipts and census results.

```bash
set -euo pipefail
JOB1=REPLACE_WITH_REAL_JOB1
JOB2=REPLACE_WITH_REAL_JOB2
L1R3_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R3_RELEASE="$L1R3_BASE/l1e_20261017/l1r_sf6_$JOB1"
L1R3_CENSUS="$L1R3_BASE/l1r_sf6/census/output_${JOB1}_${JOB2}"
L1R3_LOCAL="docs/records/labelfix/spellcheck/clariden/L1R3_evidence/production_${JOB1}_${JOB2}"
mkdir -p "$L1R3_LOCAL/release" "$L1R3_LOCAL/census"
ssh -o BatchMode=yes -o ConnectTimeout=20 clariden \
  "cd '$L1R3_RELEASE' && tar -cf - receipt.json input_verification.json release/release_*.json" \
  | tar -xf - -C "$L1R3_LOCAL/release"
ssh -o BatchMode=yes -o ConnectTimeout=20 clariden \
  "cd '$L1R3_CENSUS' && tar -cf - receipt.json evidence_availability.json hold/CENSUS.json hold/CENSUS.md hold/receipt.json changes/CHANGES.json changes/CHANGES.md changes/real_mark_correction_lines.jsonl changes/receipt.json" \
  | tar -xf - -C "$L1R3_LOCAL/census"
```

L1R3 READY: policy sf6-release-v1; gate identical to d893a04d; scored-confidence coverage measured in job 2 (expected ~0% from first records); mock parity 256/256; deploy sha256 335/335; test-only 3680720/3680721; est 20 min
