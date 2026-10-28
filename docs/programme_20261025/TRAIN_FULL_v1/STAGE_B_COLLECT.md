# Stage B collection reconciliation — 26 October 2026

**STAGE B COLLECT READY.** Offline accounting reconciliation passes; remote
collection and B2 submission remain coordinator-run. The sealed scientific
package is unchanged: `3c9e5d5f4fb8702e` (full SHA in the receipt).

The copied evidence contains **151 allocations**, including **26 killed-lane
intents** with recovery witnesses. All 26 uniquely match a parent job's exact
job ID, restart number and physical host, and a numeric single-GPU/24-CPU Slurm
step containing that lane's recorded start. Its step start must lie within
that parent allocation. Step IDs alone are not unique across requeues. No
nearest-timestamp or inferred duration is used. The observed allocation start
offset from the accounting step start is 0.63–1.70 seconds (Python startup).

| Isolation measurement | Original recovery upper bounds | Measured step ends |
|---|---:|---:|
| Global GPU UUID conflicting pairs | 18 | 0 |
| Same-host CPU affinity conflicting pairs | 18 | 0 |
| Distinct conflicting allocation pairs | 18 | 0 |

For each recovered interval, use exactly
`min(original ended_upper_bound_unix, uniquely matched step End)`.
All 26 measured ends are tighter here. No measured-complete lane is changed.
Original allocation and recovery files retain their bytes and SHA; no model,
loss, CER, trial setting, prepared data or checkpoint is modified.
The accounting capture SHA256 is
`8ae7b9c82a00f0b510ab881c75317e5be85f4423fd5a8567723da639fcfa56a2`.
Its 438 records use the explicit field order in the reconciliation artifact,
with epoch-second Start/End and `sacct -D` requeue duplicates retained.

[Offline artifact](evidence/STAGE_B_COLLECT_ISOLATION/RECONCILIATION_OFFLINE.json)
binds every allocation/recovery, copied PLAN, tool and accounting capture,
retains every before-conflict pair, and records the complete matched parent
and step rows plus capture line numbers. Accounting is second-resolution;
the original floating-point lane starts/known ends remain unchanged. The
capture is coordinator-supplied evidence, authenticated here by its SHA; this
does not independently query Slurm or validate remote checkpoint bytes.

## External adapter and unchanged result logic

[collection/reconcile.py](collection/reconcile.py) verifies the exact payload
and its sealed files, then authenticates the PLAN and all bound inputs using
the sealed `checked_plan`. Its live isolation callback rehashes original
receipts, matches accounting and checks every GPU/CPU pair. It supplies only
the reconciled recovery bound through an in-memory read overlay to the
**original sealed `stage_b.isolation()`**. The sealed checker independently
passes. Nonunique matches, mismatched SHA/host/restart, missing receipts,
invalid intervals, or remaining overlaps fail. A real overlap report names
both allocation paths/hashes, hosts, GPU UUIDs, shared CPUs and overlap times.

It then calls **`stage_b.collect()` with its real default `fixture=False`**.
All COMPLETE, checkpoint, loss-journal, evaluation and pooled-objective checks
and `results.jsonl` generation remain the original sealed logic. No model
checkpoint is loaded locally. Offline copied-evidence mode is restricted to
`audit`, and labels remote runtime/checkpoint/result validation as unperformed.

`reconcile.py seeds` calls the original **`stage_b.seeds()`**, including its
internal `collect()`, under the same authenticated callback. Calling the raw
CLI without this adapter would repeat the upper-bound isolation rejection.
B2 uses fresh model seeds 0/1/2 for each width's best final dev point, with the
same scientific payload and data. Parent best-point selection remains based
on final micro-pooled NFD-atom dev CER: sum edits / sum reference units across
seal04 dev and harvest dev. Test instruments are excluded. Study analysis uses
`--objective val_error` and omits `--scientific`; its generic best-checkpoint
diagnostic is unavailable because this study measured final CER only.

## B2 8-hour operational override

The sealed `submit()` has no time parameter. `reconcile.py submit-b2` calls it
with a scheduler-command adapter that adds **`--time=08:00:00`** to both its
dry checks and actual submissions, preserving its Astra/smoke gates, locks,
intent-before-submit protocol and idempotency. Exact effective commands and
returned job IDs are retained under `b2/submit-controls/time-override/`, linked
to the original sealed submission commands/receipts. An incomplete intent or
inconsistent effective receipt requires scheduler reconciliation, not a
second blind submission. No external action is run by Sol.

The warning moves from 1h50 to **7h50**, beyond the measured B2 trial durations
(smoke projection about **9.99 GPU-h for nine runs**). No other batch/training
change is needed for this workaround. It does not repair the launcher path:
preemption, unusually long stalls or reaching 7h50 can still require recovery.
Refresh accounting: nine requested GPUs ×8h = **72 requested GPU-h**, and
three exclusive 4-GPU nodes ×8h = **96 GPU-h** conservatively; retries/requeues
are extra. These reservations are much larger than expected elapsed cost and
must be reconciled against the owner's wave cap. No new budget is assumed.

[Exact deploy/collect/analyze/B2 commands](../../../out/TRAIN_FULL_v1/COMMANDS.md).
[Stage C deadline repair design](STAGE_C_DEADLINE_DESIGN.md) is documentation
only; no sealed Stage B code changes. The existing CUDA smoke and scientific
review bindings remain valid, because no training/allocation-recording code
changed. No new CUDA smoke is needed for this evidence adapter. Focus review
on the accounting join, original-checker overlay and effective scheduler
receipts; B2 still needs its exact PLAN-bound focused Astra PASS.

## Verification and custody

[Final suite](evidence/STAGE_B_COLLECT_ISOLATION/TESTS_COLLECT_FINAL.xml):
**162 passed**, no failures/errors/skips, 59.74 seconds: the original 140
package tests plus 22 reconciliation/adapter tests. This includes the actual
copied evidence, unique restart/host/step matching, ambiguity and byte-tamper
refusal, real-overlap pair reporting, endpoint and distinct-host handling,
the production collector and successful original B2 seed construction, and
the unchanged submission gates with exact 8-hour command receipts/idempotency.
The tests use small synthetic completion records for adapter integration;
they do not represent remote scientific results or CUDA measurements.

The original sealed payload verifies before/after, with no package diff.
[Implementation receipt](evidence/STAGE_B_COLLECT_ISOLATION/IMPLEMENTATION_RECEIPT.json)
binds the source revision observed during preparation, uncommitted external
tool/tests, original accounting/PLAN/payload, final tests, commands, readout
and design. No remote action, data copy, cache, git mutation or scientific
payload change was performed. Both passing basetemps were removed, with
logical bytes and verified absence retained in the
[cleanup receipt](evidence/STAGE_B_COLLECT_ISOLATION/TEST_SCRATCH_CLEANUP.json).
