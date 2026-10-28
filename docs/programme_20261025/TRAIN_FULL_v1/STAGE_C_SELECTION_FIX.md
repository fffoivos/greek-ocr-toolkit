# Stage C selection correction — prepare only

Payload **7e8a497f21527b90**; full SHA256
`7e8a497f21527b90bfd758fa8afceeabcc4b329aa31dc08535a2ce0472dde1e6`.
Parent: `c826ff52b1764246f125fdb8f738f26ade08d5f324081e8cacc0127cd951521b`.
[Astra's complete review](ASTRA_STAGE_C_REVIEW.md) remains HOLD pending new-seal
CUDA qualification and focused review. Owner authority **“82 GPU-h, all three”
stands**. Sol performed no network/SSH/Slurm/HF action, commit or push.
All old attempts, including full-v1-012, are untouched.

## H1 — actual best.pt loader and provenance

`stage_c.execute()` calls `run.install(..., selection_pool='seal04_dev')`, with
`study=False`. The explicit selection option changes only the in-memory
validation view: exactly the Stage B rows/labels/order, with `split='val'` as the
frozen trainer requires. Selection provenance is the identical SHA-bound
`runtime['pools']['seal04_dev']` spec used by Stage B. Study mode still excludes
tests and skips full-pass provenance; **Stage C does neither**. All full-pass and
parliament/half-synthetic checks remain active.

The selection loader feeds the frozen trainer's epoch CER → `best['metric']`,
`best.pt`, `bad_epochs` path. Eight epoch diagnostics use **437 seal04-dev rows**.
No test metric feeds selection/stopping or tuning. `PATIENCE=epochs+1=9` still
cannot stop eight epochs; last/final and all archives remain unconditional.
All four reporting panels remain present: seal04 dev **437**, seal04 test
**2,253**, harvest dev **16,350**, harvest test **52,847** = **71,887 rows**.
The harvest test crop-unique count 52,846 is not the evaluation denominator.
254 full-coverage loss/model points and four full-coverage CER checkpoints retain
the owner's cadence. HPs, widths/batches, seeds, draw horizon and OneCycle are
unchanged: 49,584 / 49,584 / 198,312 updates; 12,691,632 draws/run.

`SELECTION_POOL.json` binds pool files/count and ordered line-id/label identity.
A diagnostic wrapper observes the **actual loader passed to the frozen epoch
evaluator**, verifies the identity, measures duration and records its unchanged
result in `SELECTION_EVAL_*.json`. It changes no metric, RNG or model mode.
RUN_BINDING includes that selection attestation. New smoke readout checks the
actual final state's validation provenance, selection identity/count, all six
loader attestations, and epoch timings. Console now prints `[selection]
seal04_dev rows=437 identity=...`; generic setup must also show `val=437 rows`.

Regression: deliberately distinct legacy validation (8 IDs) and seal04 dev
(3 different IDs); the real trainer/CTC/optimizer runs eight worsening selection
epochs, the loader observer sees only the three seal04 rows, best epoch remains
1, bad_epochs reaches 7, and the full horizon and all reporting/CER archives
survive. A separate test proves equality with Stage B's view/provenance and that
full-pass provenance still refuses duplicated real draws. These are CPU toy-model
tests, not a CUDA qualification. Earlier STAGE_C and memory-fix selection claims
are corrected explicitly; the older seals actually used legacy 13,088-row val.

## M1 — memory diagnostics only

`memory_diagnostics.py` resolves Linux cgroup mount roots/memberships and records
the lane, job and ancestor cgroups. Each segment captures raw `memory.peak`,
`memory.max`, `memory.current`, `memory.events` (including oom/oom_kill). cgroup-v1
uses explicitly named max-usage/limit/usage/failcnt/oom_control equivalents, never
mislabels them as v2 counters. Job scope is identified by the Slurm job ID.

The lane samples summed `/proc/<pid>/smaps_rollup` **Pss**, in bytes, across its
live descendant process tree: at start, every 30 seconds, at graceful yield, and
in the segment's finalizer. A receipt is flushed on every sample; killed segments
retain their last sample. PID races/inaccessible counters are recorded. The
final allocation receipt SHA-binds `MEMORY_*.json`. Completed/yielded segments
have end samples; SIGKILL cannot manufacture one. Readout reports job peak,
limit/headroom, OOM counters and aggregate PSS peak, sample counts, raw receipt
SHAs and any missing measurements. A legitimate `memory.max=max` is reported as
unlimited; headroom remains unknown. Diagnostics do not alter/stop training or
select models. Inspect PARTIAL capture status or OOM events with Astra.

**Keep --mem=110G.** No new memory measurement is claimed locally. The new real
smoke must supply it. Sampled summed RSS is still a separate accounting diagnostic
and cannot establish unique/cgroup-charged RAM. Short-horizon full-pool smoke does
not qualify full-size epoch arrays, long-lived workers or 23h memory headroom;
readout deliberately sets capacity_qualified=false.

## M2 / M3 — forecast, renewals and retained storage

Fresh `smoke-readout` measures the corrected epoch-validation loader separately.
`forecast.py` includes **8 × measured selection_seconds_mean**, 254 loss/model
points, four full CER passes, durable saves, all measured startup costs, the
observed Stage B interruption hazard and explicit 23h segment renewals. Usable
segment time is 23h minus the 600s warning window. It conservatively counts
`ceil(scenario elapsed / usable)-1` renewals and re-solves restart/startup cost;
actual preemptions reset the limit, so this can overcount deterministic renewals.
At ×2 at least one renewal occurs. High doubles the observed hazard; it is not a
bound. Full-size startup and late-resume archive verification remain unmeasured.

The [interim forecast](evidence/STAGE_C_SEL_INTERIM_FORECAST.json) is **old c826
measured four-panel timings + an unmeasured row-ratio proxy for corrected epoch
selection**, not new-smoke or launch evidence. Its proxy input and raw old source
are SHA-bound in [STAGE_C_SEL_COST_PROXY.json](evidence/STAGE_C_SEL_COST_PROXY.json).
New CUDA measurements must replace these costs before focused Astra/launch.

| Width | Low / expected / high GPU-h | Renewals low / expected / high | Output GB low / expected / high |
|---|---|---|---|
| ×1 | 19.117 / 19.968 / 23.178 | 0 / 0 / 1 | 5.263 / 6.250 / 7.585 |
| ×1.5 | 20.572 / 21.569 / 25.381 | 0 / 0 / 1 | 10.343 / 12.499 / 15.336 |
| ×2 | 38.595 / 40.358 / 46.938 | 1 / 1 / 2 | 17.612 / 24.081 / 32.832 |
| Total | **78.284 / 81.895 / 95.497** | | **33.218 / 42.829 / 55.753** |

The 82-GPU-h authority is an approved forecast/scope, not a runtime guarantee;
expected margin is only ~0.105 GPU-h before new measurements. Compare the new
forecast and actual ledger with that authority; no automatic extension is implied.
Keep the owner cadence when eval/training exceeds 25%. Options remain an
owner-authorized coarser cadence in a new plan, or a separately qualified identical
full-coverage evaluator optimization; never silently subsample.

Storage counts 254 model archives plus four CER full states, best/last/rolling,
1GB log/prediction allowance/run, and one retained full-state inode for **every
forecast interruption plus deterministic renewal**. Abrupt preemption may not
create a yield; counting all is conservative. Hardlinks are cheap only until the
rolling inode is atomically replaced; thereafter every yield consumes space.
Full-state size is measured from smoke; long-run state/log growth is unqualified,
and arbitrary requeues can exceed scenarios. The prior 52GB allowance is
superseded by scenario estimates plus operational headroom. The commands capture
filesystem bytes/inodes **and actual user/project quota immediately before full
submit**, preserve raw output and SHA, and require reading available capacity
against the high forecast plus existing occupancy/margin. No pruning is added.

## Seal, data reuse, tests and handoff

The exact payload delta is [STAGE_C_SEL.diff](evidence/STAGE_C_SEL.diff):
changed existing files **run.py, stage_c.py, forecast.py**; new files
**selection_diagnostics.py, memory_diagnostics.py**, and three focused test files.
Every vendor, data-producing, runtime, resource/signal shell and adopted input
byte remains unchanged. Audit/prepared005 data is reusable by the same exact
compatibility proof. Old smoke/training state is not reusable across this change.

Fresh attempt: **full-v1-013-stage-c-sel**. Offline expected full/smoke PLAN/config
bytes and hashes are in [STAGE_C_SEL_BINDINGS/EXPECTED.json](evidence/STAGE_C_SEL_BINDINGS/EXPECTED.json).
They are generated without remote writes; commands compare the actual remote
PLANs against these predictions. Runtime SHA remains `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`.

**CUDA smoke MUST rerun**: the actual selection/evaluation population changed.
Use three width-specific control/requeue pairs, six workers, full four panels,
48 updates and tiny loss/model cadence; actual `scancel --batch --signal=TERM`
triggers checkpoint → 75 → Slurm requeue. Require BIT_IDENTICAL scientific state,
per-point models/loss/CER, actual selection identity, real memory receipts,
measured costs and unchanged GPU-global/same-host CPU isolation. Preserve the
old full-v1-012 attempt as evidence; never rebind or overwrite its claims.

The stable-seal full release tests, cleanup, data proof and artifact SHAs are
recorded in [STAGE_C_SEL_RECEIPT.json](evidence/STAGE_C_SEL_RECEIPT.json).
[Exact commands](../../../out/TRAIN_FULL_v1/COMMANDS.md): immutable deploy → fresh
plans/data proof → new CUDA smoke → accounting/readout/forecast → focused Astra
→ prelaunch capacity/authority readback → full submit. No remote action by Sol.
