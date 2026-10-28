# Launch fix — focused Astra review handoff

**LAUNCH FIX READY**, pending focused Astra PASS. Payload `0446ee734d2c867cda056973ce5052f917865f1f53ecc6c2b8301c99d437280f` (ID `0446ee734d2c867c`). No remote action was taken by Sol.

Coordinator-reported failure:3749193 FAILED123:0 before training startup, inherited `SLURM_TIME_FORMAT=relative`, deadline string `Tomorr 10:05`; successors3749195/3749197 cancelled while pending. Original prelaunch [Astra PASS](ASTRA_PRELAUNCH_REVIEW.md) and all005 receipts remain unchanged.

Exact source comparison: [LAUNCH_FIX_SOURCE.diff](evidence/LAUNCH_FIX_SOURCE.diff). It includes every change to an existing payload file, normalized back to SHA-verified parent bytes. Added files are the immutable50-file parent seal `launch_parent_payload.json` and13 regression cases in `tests/test_launch_fix.py`. New payload seals52 files;45 original files remain byte-identical.

| Existing file | Exact change and purpose |
|---|---|
| job.sbatch | One expression: `$(squeue ...` becomes `$(SLURM_TIME_FORMAT=standard squeue ...`; same `%e`, same GNU date conversion, same numeric deadline validation. Override is scoped to the one command. |
| chain.py | Import compatibility predicate inside production branch; use it for smoke package binding. Review must still name the current payload, exact runtime and actual BIT_IDENTICAL smoke; owner-go and intent protection remain. |
| run.py | Import compatibility predicate alongside verifier; use it for prepared-runtime package binding. No training options/math changes. |
| verify.py | Add exact parent-hash/change-set/reversible-source proof and predicate; original payload/upstream checks unchanged. Only the one historical parent is accepted. |
| reuse_audit.py | Four lines compose the operational proof before its existing preparation-fix ancestry proof. No new audit is claimed. This keeps its original offline regression tests valid; relaunch does not invoke audit reuse. |

The proof permits exactly these five file changes and exactly two additions. For job/chain/run/reuse it reverses only the declared literal edits and checks the original source SHA. For verify it removes the delimited compatibility helper and checks the original source SHA. It refuses changed recipe/numerical/data/scorer/runtime-environment files, missing files, unrecognized parent and added code. The new helper itself is sealed for review by the new payload.

Scheduler scan of the entire payload: job.sbatch:21 is the **only formatted time parser**. job.sbatch:37 invokes `scontrol requeue` without reading time. chain.py requests `sacct --format=JobIDRaw,State,ExitCode,ElapsedRaw`; `ElapsedRaw` is validated as decimal, independent of display formatting. segment.py, readout.py, audit.sbatch/audit_job.py and prepare.sbatch/prepare_job.py parse no Slurm times. Runtime environment, durations, partition/resources, preemption, dependency policy and checkpoint/eval cadence are unchanged.

**runtime.json, all prepared pools, audit and real smoke identity remain valid without rewriting any bytes.** The proof explicitly inherits parent package294c3458c0d1fbbb. Runtime SHA `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`; smoke SHA `19db742de50994112da04a893b6fb331f2f2daf09a8a120c21ad10b084243175`. The scientific model/optimizer/sampler/evaluation/runtime-library implementation is unchanged. New training provenance records the current run.py source hash (binding check only changed); no training state was created by the failed pre-srun attempt. The relaunch commands refuse unexpected segment.pt/RUN_BINDING/COMPLETE evidence before treating it as an unstarted run.

**81 tests PASS**,0 failures/errors/skips; [XML](evidence/TESTS_LAUNCH_FIX_ALL.xml). Real Bash job wrapper executed offline with mocked scheduler and GNU-date commands under inherited relative formatting for same-day, `Tomorr 10:05`, and2032 date responses. Each asserts the numeric deadline and that only squeue receives standard formatting. This is an offline boundary test, not a fresh Clariden/GNU-date execution. Seven existing-source/parent/extra-file mutation probes plus the reuse-audit probe reject even locally resealed changes. Old runtime/smoke bytes bind; stale Astra review refuses; fresh mocked review permits dry-check/submit and prevents duplicate submission. Original real-S1 CPU resume identity and mocked complete release→prepare→train→evaluate rehearsal pass again. Local CPU dependency versions are not qualification of the pinned Clariden numerical environment.

[COMMANDS.md](../../../out/TRAIN_FULL_v1/COMMANDS.md) supplies exact redeploy/readback → compatibility and original runtime/smoke readback → focused Astra PASS → three-segment relaunch. It uses fresh `controls/train-launchfix-001`, retains the old chain directory and copies its claims/logs into failed-chain-evidence, with scoped sacct proof. Failed/cancelled parents are never dependencies. It keeps the original train output location, with an unstarted-state check. No rebind, re-audit, factory preparation or replacement smoke receipt is required. The new review must explicitly approve inherited smoke compatibility and name the new payload; the original review is preserved.

Current Gennadius population and recipe:793,227 real train /16,350 dev /52,846 test;198,312 updates; four archived evaluations50k/100k/150k/198,312 on all four instruments. Approximately25.02974 useful GPU-h including two historical restart allowances, before production iterator/preemption/queue tails; three12h reservations request36GPU-h. Refresh live budget. Original [PLAN](PLAN.md) now leads with current state and labels previous pending preparation narrative historical.

LAUNCH FIX READY
