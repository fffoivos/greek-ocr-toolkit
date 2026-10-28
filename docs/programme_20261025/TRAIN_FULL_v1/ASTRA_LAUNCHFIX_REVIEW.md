# ASTRA — TRAIN_FULL_v1 focused launch-fix review, 25 October 2026

**PASS. No BLOCKER or HIGH finding in the four requested checks.** This certifies the exact operational change and inheritance below for an unstarted production run. It does not certify a completed redeployment or relaunch.

## Scope and identities

Reviewed the comparison with the payload certified by [ASTRA_PRELAUNCH_REVIEW.md](ASTRA_PRELAUNCH_REVIEW.md), [LAUNCH_FIX.md](LAUNCH_FIX.md), the complete current package, retained local runtime/smoke receipts, test evidence and [relaunch commands](../../../out/TRAIN_FULL_v1/COMMANDS.md). All work was local and read-only except this report. No network, SSH, scheduler command, training, background job or remote write was performed. No machine-readable remote approval was created.

| Object | Independently verified SHA256 |
|---|---|
| Certified parent / `package/launch_parent_payload.json` | `294c3458c0d1fbbb45c61dcac2e11e8fab92f1ce10558cf9576ecccaabd30aac` |
| Current `package/PAYLOAD.json` | `0446ee734d2c867cda056973ce5052f917865f1f53ecc6c2b8301c99d437280f` |
| Local retained `receipts_005/data_prepared_runtime.json` | `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4` |
| Original `receipts_005/SMOKE_IDENTITY.json` | `19db742de50994112da04a893b6fb331f2f2daf09a8a120c21ad10b084243175` |
| Reviewed `out/TRAIN_FULL_v1/COMMANDS.md` | `b7c10a756737f278bb2c26d6f9dca851e3028180a352fb93ec82002593975cb4` |

## 1. Exact operational diff — PASS

Verified all **52 sealed files** against their byte counts and SHA256 values; there are no additional unsealed files in the package. Of the parent's 50 files, **45 are byte-identical**, five changed, none disappeared. The only additions are `launch_parent_payload.json` and `tests/test_launch_fix.py`.

Independently reversed [LAUNCH_FIX_SOURCE.diff](evidence/LAUNCH_FIX_SOURCE.diff) in memory against the actual current files, checking every hunk against current bytes, then reproduced each changed file's parent SHA256 and byte count. This check did not rely on the compatibility helper's own reversal logic.

| Changed file | Reviewed effect |
|---|---|
| `job.sbatch` | Adds the command-scoped `SLURM_TIME_FORMAT=standard` assignment to the existing `squeue` deadline query. |
| `run.py` | Accepts the exact historical runtime package binding through the compatibility proof. |
| `chain.py` | Accepts the exact historical smoke package binding through that proof; the review must still name the current payload and exact runtime. |
| `verify.py` | Adds the pinned-parent compatibility proof and predicate; original verification remains intact. |
| `reuse_audit.py` | Composes launch compatibility with the existing preparation-only audit ancestry proof. |

Recipe, data preparation, runtime environment and library checks, model, optimizer, sampler, schedule, evaluation, seeds and continuation implementation are unchanged. Runtime remains **793,227 real training rows, 198,312 updates, seed 20261015**. The claim/control changes are in the commands: they preserve the failed attempt and select a fresh submission namespace.

## 2. Deadline and package-wide time handling — PASS

`job.sbatch:21` now evaluates:

```bash
S1_DEADLINE_EPOCH=$(SLURM_TIME_FORMAT=standard squeue -h -j "$SLURM_JOB_ID" -o %e | xargs -I{} date -d '{}' +%s)
```

The explicit command environment overrides inherited `relative`, `standard`, `iso`, custom formats, or an unset variable. Standard Slurm output supplies the full calendar timestamp to the existing GNU-date conversion. Only `squeue` receives the override; the surrounding job environment is preserved. Thus `Tomorr 10:05` is no longer selected by inherited relative formatting. The shared local timezone interpretation of `squeue` and `date`, numeric validation, `set -euo pipefail`, and the trainer's existing **deadline minus 300 seconds** stop rule remain unchanged.

Fresh foreground shell probes exercised the extracted assignment/pipeline with real Bash and `xargs`, a function standing in for `squeue`, and a Python ISO-date converter substituted for GNU `date`. **15 cases passed**: five inherited-format states crossed with same-day, tomorrow and 2032 timestamps. They checked numeric epochs and preservation of the outer environment. **Four additional cases** refused unknown, relative, empty and multiple timestamp outputs. These establish shell scoping and pipeline behavior; they are explicitly not a fresh Clariden or GNU-date execution.

The package-wide scheduler/parser scan found **no other formatted Slurm time parser**. `chain.py` reads `ElapsedRaw` and validates decimal accounting seconds, independently of display formatting. `s1_segment.py` consumes the already numeric epoch; other timing fields use Python clocks. `scontrol requeue` reads no timestamp.

## 3. Runtime, prepared data and original smoke inheritance — PASS

Both retained runtime and smoke name the exact certified parent; their bytes reproduce the hashes in the prior review. The smoke still records **BIT_IDENTICAL**, `mock=false`, the same runtime hash and actual restart allocations **3748976/0 and 3748976/1**. The comparator and all 14 scientific comparison fields are unchanged. This is inheritance of the original CUDA smoke, not a claim that it ran under the new payload.

`launch_compatibility()` pins the parent seal, permits exactly the five reviewed changes and two additions, and reverses the declared edits to the parent hashes. The newly added helper is itself covered by the current reviewed seal. The earlier audit ancestry proof also passes. Fresh in-memory probes rejected eight resealed mutations: recipe, wrapper, run, chain, verifier, audit-reuse helper, parent seal and an extra source file. No mutated files were written.

The runtime's existing prepared-pool identities remain authoritative, and unchanged `load_pools()` still verifies each referenced parquet hash before loading. No pool regeneration, runtime rebinding or replacement smoke receipt is justified by this fix. Remote prepared bytes and remote smoke checkpoints were not reread here; their present custody remains subject to the supplied deployment/readback commands and existing runtime checks.

**Resume boundary:** changing `run.py` changes its source hash in training provenance. This is not permission to migrate a production checkpoint made by the parent package. The reported failure occurred before `srun`, and the commands explicitly refuse existing `segment.pt`, `RUN_BINDING.json` or `COMPLETE.json` before treating production as unstarted. A fresh run records the new source identity; subsequent segments use that same package and unchanged resume machinery. If unexpected prior state is found, the reviewed unstarted-run premise does not apply.

## 4. Failed-claim preservation and relaunch controls — PASS

The commands copy the old `controls/train` tree, including its failed segment-1 claim and logs, into `controls/train-launchfix-001/failed-chain-evidence`, retaining the originals. They require a fresh controls path and obtain scoped accounting for **3749193 / 3749195 / 3749197**. Segment 1 has no `--prior`; segments 2 and 3 receive only the newly returned predecessor IDs. These are reviewed instructions, not evidence that archival or cancellation has already been performed. Failure/cancellation status is owner/coordinator-reported in this offline review.

The unchanged wrapper retains **preemptable**, **--requeue**, and **12:00:00**; the production driver also explicitly requests **12:00:00**. Every submission performs the same-options `sbatch --test-only`, and existing intent/claim files prevent blind duplicate submissions. The fresh review must name the new payload, unchanged runtime and hash-bound original BIT_IDENTICAL receipt; the old review cannot authorize the new payload.

Fresh dependency probes confirmed active predecessors receive `afterok`, while **COMPLETED/0:0** yields no dependency and the driver verifies the predecessor's durable yield/checkpoint. Failed, cancelled, unsuccessful-completed, missing/purged accounting and malformed elapsed evidence refuse submission. A controller-purged completed ID with retained successful accounting is therefore never passed to `afterok`; completely unavailable accounting fails closed.

## Validation and evidence limits

Fresh checks: full payload/upstream verification; independent five-file diff reversal; launch/audit compatibility; runtime/smoke hashes; eight in-memory mutation refusals; 19 shell time probes; nine dependency probes; AST parsing of **39 Python files**; syntax checks for four shell files and all three command blocks.

Inspected retained [TESTS_LAUNCH_FIX_ALL.xml](evidence/TESTS_LAUNCH_FIX_ALL.xml): **81 tests, zero failures/errors/skips, 17.149 seconds**. The earlier `TESTS_LAUNCH_FIX.xml` preserves three failures caused by the test `srun` stub consuming the Python executable and attempting `exec -B`; the current stub correctly shifts the three `srun` options. The later passing suite includes the wrapper cases and existing resume/rehearsal tests. I did not rerun their file-writing/background-wrapper harness under this assignment's restrictions.

This focused PASS supersedes the parent-package approval only for the exact launch fix and inherited evidence identified above. Existing scientific limitations in the original review remain unchanged. Deployment, remote accounting, unstarted-output readback and actual trainer startup remain coordinator execution steps; none is represented as completed here.

VERDICT: PASS | BLOCKERS: 0 | HIGH: 0
