# Stage B H1 closure — prepare only

**STAGE B FIX READY.** Local qualification is complete. The coordinator must run
the new-binding CUDA smoke, obtain focused Astra PASS, and then submit the study.
Sol performed no network, SSH, Slurm, HF, commit or push action.

Payload: `3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8`
(ID `3c9e5d5f4fb8702e`). Parent: `f3944e2a242e83de`.
[Exact source diff](evidence/STAGE_B_H1.diff),
[SHA/byte inventory](evidence/STAGE_B_H1_DIFF_INVENTORY.json),
[execution commands](../../../out/TRAIN_FULL_v1/COMMANDS.md).

## H1 changes and review scope

| File | Exact scope |
|---|---|
| `package/stage_b_trial.py` | Add `physical_host()` using `os.uname().nodename`, independent of inherited `HOSTNAME`/Slurm values. Record host and its source in the initial allocation intent, before training, and retain it in the final receipt. Recovery requires the original host, retains the original file bytes and SHA, and records `prior_physical_host` and `next_physical_host` separately. |
| `package/stage_b.py` | Replace the single-node Stage A isolation call with Stage B's host-aware checker. Keep all original and recovered allocation intervals. Verify recovery's prior-file SHA and prior-host match. Require host/GPU/CPU attestation and finite ordered timestamps. On overlapping intervals, reject equal GPU UUIDs globally; reject intersecting CPU sets only when physical hosts match. Equal interval endpoints remain nonoverlap. Return the host inventory and allocation count. |
| `package/tests/test_stage_b.py` | Existing killed-allocation test now supplies and verifies original/next physical hosts. |
| `package/tests/test_stage_b_isolation.py` | Add 20 cases covering distinct-host CPU/index reuse, same-host CPU collision across jobs, global GPU collision, disjoint hardware, sequential intervals, missing attestation, invalid intervals, kernel identity, recovered allocations and host/SHA tampering, missing prior-host refusal, and the actual production collector. |

All **71 other parent files** are byte-identical. Stage A's checker and report
remain unchanged. Training, optimizer implementation/defaults, fixed and searched
HPs, trial horizons, data, furniture fallback, codec, preprocessing, scoring,
loss cadence/journal, exact continuation and Slurm time handling are unchanged.
No isolation bypass was added. The production collector test calls actual
`checked_plan → isolation → collect` with `fixture=False`, without mocks; it
accepts distinct hosts and rejects the same-host CPU collision on that path.

The diff's three parent source files were reconstructed from retained earlier
test copies and verified against their exact deployed parent SHA256 values
before comparison. The inventory binds both payloads and the resulting diff.

## Local verification and storage

[Full package suite](evidence/TESTS_STAGE_B_H1_RESUME.xml): **140 passed**, zero
failures/errors/skips, 51.18 seconds. This includes the existing four-subprocess
mock rehearsal, forced yield/restart identity, hard-kill resume at all three
widths, poisoned test-pool paths, sampler/cadence tests and new H1 tests.
[Retained rehearsal](evidence/REHEARSAL_STAGE_B_H1.json) uses real S1 updates/CTC
with the existing toy model; it does not certify CUDA arithmetic.

Command used (local existing Python environment; no installation/cache):

```bash
env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  -m pytest -q -p no:cacheprovider \
  docs/programme_20261025/TRAIN_FULL_v1/package/tests \
  --basetemp=out/TRAIN_FULL_v1/pytest_stage_b_h1_resume \
  --junitxml=docs/programme_20261025/TRAIN_FULL_v1/evidence/TESTS_STAGE_B_H1_RESUME.xml
```

The passing basetemp's **27,958,427 logical bytes** were removed after retaining
the XML and rehearsal, as explicitly requested. Its absence is verified in the
[cleanup receipt](evidence/STAGE_B_H1_TEST_CLEANUP.json). Earlier failed/crashed
basetemps and remote claims are preserved. No data, model or cache was copied.

## Binding reuse and regenerated plans

**Audit/prepared005 runtime/pools and measured Stage A remain valid.**
`verify.data_compatibility()` passes; every data-producing input/module and
trainer restoration proof remain unchanged. Only the exact inherited runtime
SHA `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`
is accepted. No audit, rebind, import or relocation is required.

**CUDA smoke rerun: YES.** Previous job **3749768** completed BIT_IDENTICAL with
no tests opened, but its allocations do not attest physical host. The repaired
recording/recovery code must be exercised and all smoke/trial/PLAN bindings must
name the new payload. Preserve `full-v1-008-stage-b` intact. Fresh work:
`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-009-stage-b-h1`.

[Regenerated binding manifest](evidence/STAGE_B_H1_BINDINGS/BINDINGS.json):

| Plan | Trials / groups | Expected remote SHA256 |
|---|---:|---|
| [Smoke](evidence/STAGE_B_H1_BINDINGS/smoke/PLAN.json) |4 /1|`9f60dc76d8767f40a6a4c71e6cb73e7d9f5fb5fc9e35cb0ccd6be05f17d4ae09`|
| [Study](evidence/STAGE_B_H1_BINDINGS/study/PLAN.json) |51 /13|`01cc2ae0bb09d2b61d3b6a7fc15627366d3a131e385efe30028e82cb81903f38`|

All 55 configs are supplied alongside those plans with remote paths. The
[offline generator](evidence/generate_stage_b_h1_bindings.py) reproduced **every
original trial config SHA** from the retained old plans before changing only
the payload SHA and destination paths. Runtime, Stage A, selections, points and
space retain their original identities. These are expected remote artifacts,
not remote execution evidence. Commands run the unchanged production planner on
Clariden, rehash its dependencies, and assert these exact plan hashes before
submission. Changed destinations require regeneration rather than editing a plan.

## Coordinator sequence and remaining evidence

1. Deploy to the new payload directory; compare full local/remote SHA256.
2. Generate smoke/study plans in fresh `009` controls and verify expected hashes.
3. Rerun four-lane CUDA smoke: control and forced-requeue twin at ×1/b256,
   ×1.5/b256 and ×2/b64; loss steps 8/16/24/32/40; forced yield at 12. Require
   BIT_IDENTICAL, actual restart, host-aware isolation PASS and no tests opened.
4. Supply the exact diff, 140-test XML, fresh smoke/allocation/recovery evidence,
   new study plan and accounting to focused Astra H1 re-review. Record the actual
   verdict with current package, study-plan and smoke hashes. Previous HOLD is
   retained; no PASS is fabricated here.
5. After that PASS, launch the 51 unchanged trials; collect/analyze per width;
   prepare B2 seeds 0/1/2 and obtain its plan-bound review. Stage C remains deferred.

The retained previous smoke projects **B17 56.6571 GPU-h / B2 9.9983 GPU-h**,
with dev-eval overhead 15.34% /14.19% /12.91% for ×1 /×1.5 /×2. These are prior
measurements used for forecasts, not measurements of this repair or study costs.
The fresh smoke refreshes them. No coverage or cadence is reduced.

Coordinator ledger at the 01:27 brief: **184.41 used /165.59 remaining of350**.
Smoke maximum reservation is5.33 GPU-h; conservatively B/B2 reserve104+24,
leaving32.26 before intervening work, retries/requeues and any later C reservation.
Refresh scoped accounting before each launch. No new recipe condition is imposed.

STAGE B FIX READY
