# ASTRA — focused Stage B H1 re-review

26 October 2026, Europe/Athens. Independent CERTIFIER review of payload `3c9e5d5f4fb8702e` and the supplied `full-v1-009-stage-b-h1` receipt snapshot, recorded by the coordinator at 10:54 EET. **PASS: H1 is closed for this payload and study plan; zero BLOCKER and zero HIGH findings.** The repaired checker distinguishes physical hosts without dropping GPU or temporal isolation checks. Two nonblocking observations remain below.

Scope: the latest [owner brief and RESUMEs](../../ocr_program_2026-10-06/briefs/TRAIN_FULL_v1_brief.md), including the 26 October crash-resume; [H1 fix record](STAGE_B_H1_FIX.md); exact diff/inventory; sealed package; test XML; regenerated bindings; [commands](../../../out/TRAIN_FULL_v1/COMMANDS.md); [execution ledger](EXECUTION_STATE.md); and [fresh smoke receipts](../../../out/TRAIN_FULL_v1/receipts_stage_b_h1_remote_009/). The owner's autonomous A → B → C authorization is acknowledged. This certifier launched nothing and added no approval requirement. Inspection and Python checks were local, synchronous and read-only, with bytecode writes disabled. No network, SSH, scheduler, training, background job or full test-suite execution occurred. Only this report was written.

The [original HOLD](ASTRA_STAGE_B_REVIEW.md) remains historical evidence, unchanged: SHA256 `3ad8df86b1a662a0c35cd1b21914deddb7d042adbf268fb386b5e9ca7717f91b`. This report does not rewrite its conclusion for the old payload.

**Exact reviewed identities.** These hashes were recomputed firsthand from local bytes.

| Object | SHA256 |
|---|---|
| [Current PAYLOAD.json](package/PAYLOAD.json) | `3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8` |
| [Preserved parent payload](evidence/STAGE_B_H1_PARENT_PAYLOAD.json) | `f3944e2a242e83def0ff86a034c7f1e64bb30276a1c52ed5e291b441e162dd17` |
| [Actual copied study PLAN](../../../out/TRAIN_FULL_v1/receipts_stage_b_h1_remote_009/study_PLAN.json) | `01cc2ae0bb09d2b61d3b6a7fc15627366d3a131e385efe30028e82cb81903f38` |
| [Local smoke PLAN, matching remote attestation](evidence/STAGE_B_H1_BINDINGS/smoke/PLAN.json) | `9f60dc76d8767f40a6a4c71e6cb73e7d9f5fb5fc9e35cb0ccd6be05f17d4ae09` |
| [Fresh SMOKE_IDENTITY.json](../../../out/TRAIN_FULL_v1/receipts_stage_b_h1_remote_009/SMOKE_IDENTITY.json) | `842bb11af2f00c318f48716b523eb128dc41fde55508bc89154854a96ff4d37f` |
| [Remote PLAN_BINDINGS_VERIFIED.json](../../../out/TRAIN_FULL_v1/receipts_stage_b_h1_remote_009/PLAN_BINDINGS_VERIFIED.json) | `1f70708527000fc3c62bc78b3452c72454ab5f39f3d934b551aecb5901e4bc09` |
| [H1 source diff](evidence/STAGE_B_H1.diff) | `d12c148a4d45ef3781fee66ec185ad4e487e3797b432f8b7178b1e6a3bb70a26` |
| [Diff inventory](evidence/STAGE_B_H1_DIFF_INVENTORY.json) | `30ec9939556070f5f8d41f58e995e5ba82799d7d09271850d8b1a1e06f857da3` |
| [140-test XML](evidence/TESTS_STAGE_B_H1_RESUME.xml) | `bef4c25589628ce3be8dcaf25a3c4544562b49e300e7d7003c14f3061c6e53eb` |

**H1 closure — PASS.**

1. **Physical host comes from the kernel.** [stage_b_trial.py:120](package/stage_b_trial.py#L120) reads `os.uname().nodename`, rejecting empty or whitespace-padded values. It does not derive identity from job ID, inherited `HOSTNAME` or `SLURMD_NODENAME`. Each training allocation records `physical_host` and `physical_host_source` together with job/restart, CPU affinity and GPU identity before `execute()` starts; the final receipt retains that same host ([lines 169–220](package/stage_b_trial.py#L169)). Finished lanes authenticate their completion and skip training on restart.

2. **Recovery retains the original host and bytes.** [recover_allocations():128](package/stage_b_trial.py#L128) refuses an unfinished same-allocation claim, a boundary preceding its start, and an original intent without a physical host. It writes a separate witness containing the original file's path/bytes/SHA256, `prior_physical_host`, and independently obtained `next_physical_host`; it does not rewrite the original intent or assign the next host to it. [isolation():268](package/stage_b.py#L268) checks the witness against the original file and requires its prior-host field to match. Recovery's end remains an explicitly conservative upper bound from the next controller boundary, not a measured death timestamp; ambiguous hardware reuse can therefore require reconciliation. This does not relax collision detection.

3. **CPU scope, GPU scope and time overlap are correct.** [stage_b.py:256–296](package/stage_b.py#L256) retains original and recovered intervals, requires host/GPU/CPU evidence and finite ordered times, then compares pairs only when `max(start) < min(end)`. Equal endpoints are nonoverlap. Equal GPU UUIDs are rejected globally during overlap, including across different hostnames. CPU-set intersections are rejected only when physical hosts are equal, regardless of job ID. Distinct nodes can legitimately reuse CPU numbers and visible-device indices. The historical Stage A checker is unchanged.

4. **Production collection uses the checker.** [collect():213–218](package/stage_b.py#L213) defaults to `fixture=False`, invokes actual `checked_plan()`, and evaluates `isolation(p)` before publishing any isolation/result output. CLI collection calls that default; `seeds()` and `adoption()` also use it. The new [production-collector regression](package/tests/test_stage_b_isolation.py#L140) uses synthetic failure receipts but actual verification/collection without algorithm mocks or `fixture=True`; it accepts distinct-host CPU reuse and rejects a same-host collision.

**Firsthand behavioral verification.** I invoked the sealed isolation, recovery and default collection functions through an in-memory storage adapter, retaining the real `checked_plan()`/payload verifier. The adapter prevented creation of fixture files; an audit hook also refused filesystem writes, process launches and network connections. All **20 independent checks passed**: distinct-host reuse; same-host cross-job CPU collision; global GPU collision; same-host disjoint resources; equal-endpoint/sequential reuse; four missing-attestation cases; reversed interval; kernel identity independent of inherited names; original-host preservation after recovery; recovered CPU/GPU collision detection; prior-host and original-byte tampering; missing original-host refusal; and production collection acceptance/refusal. No isolation or recovery decision function was mocked. These are in-memory behavior checks, not an unmocked filesystem integration run or a new CUDA run.

I also parsed the supplied XML: **140 test cases, zero failures/errors/skips, 51.183 seconds**, including **20 cases in `test_stage_b_isolation`**. Source inspection confirms NaN/infinite interval coverage in addition to the checks above. This is the recorded execution evidence from the fix run; I did not rerun pytest. The retained toy-model rehearsal reports four subprocesses, exact continuation and poisoned test-pool paths; it is explicitly `mock=true` and does not establish CUDA arithmetic.

**Fresh real smoke — PASS on the supplied execution evidence.** [SMOKE_IDENTITY.json](../../../out/TRAIN_FULL_v1/receipts_stage_b_h1_remote_009/SMOKE_IDENTITY.json) binds the current payload, smoke plan and exact prepared runtime. It reports `BIT_IDENTICAL`, `mock=false`, five loss steps **8/16/24/32/40**, isolation **PASS** over **five allocations on two physical hosts**, and **zero test instruments opened**.

| Requeue-twin allocation | Job ID | Restart | Physical host | Exit |
|---|---|---:|---|---:|
| Original, forced yield at step 12 | 3752522 | 0 | nid006755 | 75 |
| Resumed, completed | 3752522 | 1 | nid006079 | 0 |

Both embedded allocation records name `os.uname().nodename` as their host source. Their GPU UUIDs differ, their local CPU sets both contain 0–23, and their recorded intervals do not overlap. The forced-yield checkpoint is bound by SHA256 `a5f73e16959395cfeb2c40d6a39faf1bbb949837b47c9eda2a972353661eb470`. [SMOKE_SACCT.txt](../../../out/TRAIN_FULL_v1/receipts_stage_b_h1_remote_009/SMOKE_SACCT.txt) independently records job **3752522 COMPLETED, 0:0**, four requested/allocated GPUs and `ElapsedRaw=262`. The [batch log](../../../out/TRAIN_FULL_v1/receipts_stage_b_h1_remote_009/smoke-3752522.log) contains two payload-verification entries and the original node's exit-75 step. The unchanged [wrapper](package/stage_b.sbatch) waits for the lanes, calls actual `scontrol requeue` on status 75 and retains the job ID. These records consistently establish a real forced requeue.

The inspected [smoke readout](package/stage_b.py#L299) validates checkpoint digests, compares model/optimizer/scheduler/RNG/iterator/draw continuation fields, authenticates the step-12 yield, requires an increased restart count on the same job, and compares all five loss points and final dev metrics. `execute(study=True)` and [run.install()](package/run.py#L31) restrict pool loading/evaluation to training components and the two dev instruments. The zero-test field is a program attestation supported by that unchanged loading path and recorded poisoned-path tests, not an independent OS file-open trace.

Evidence limit: full checkpoint tensors, all five raw allocation files, lane logs and remote pool bytes were not supplied locally. I did not rerun the CUDA tensor comparison. The copied readout contains both raw requeue-twin allocation records and completion hashes, while its five-allocation isolation result remains a remote readout attestation checked against the sealed implementation. This graceful-yield smoke does not exercise a hard-killed allocation's recovery witness; that branch is covered by source, recorded tests and the independent in-memory checks. The CUDA requeue identity comparison is the ×1/b256 twin pair; ×1.5/b256 and ×2/b64 are additional completed smoke lanes.

**Scientific invariance — PASS against actual bytes.** `verify.verify()` authenticated all **75 sealed files**, original numerical-module identities and trainer restoration. `verify.data_compatibility()` passed its 33-file lineage check. The local prepared runtime hashes to `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`, with **793,227 train rows** and `mock=false`.

I compared both manifests and inverted every unified-diff hunk in memory. All three reconstructed pre-existing files exactly reproduce their parent SHA256/byte counts; the fourth is the added isolation-test file. Thus the inventory is complete: **71 parent files unchanged, three modified, one added**. The only production changes are host recording/recovery and host-aware isolation. Recipe, model/trainer, data production, sampling, scorer, cadence, horizons, batches and scheduler wrapper are byte-identical to the reviewed parent.

I independently read and hashed all **55 supplied trial configs**. Replacing only each config's payload reference with the parent reference reproduces its exact old plan-bound bytes/hash. Normalizing only declared package/output paths, payload and affected config hashes makes both new plans equal to their old plans. The actual copied study plan is byte-identical to the regenerated expected plan; both plan hashes match `PLAN_BINDINGS_VERIFIED.json`. This verifies unchanged 16 Halton points plus unscaled control per width, batches **256/256/64**, six workers, **1,269,164 draws** and **4,958/4,958/19,831 updates**, dev-only loss cadence and final pooled NFD-atom CER. No scientific change is hidden in the reseal.

**Cost — B/B2 fit the supplied reconciled ledger.** Recomputed fresh-smoke forecasts use measured Stage A throughput plus 26 times the maximum complete-dev loss time and one final dev CER pass per trial:

| Width | B17 projected GPU-h | B2 projected GPU-h | Evaluation / training |
|---|---:|---:|---:|
| ×1 | 16.2051 | 2.8597 | 15.12% |
| ×1.5 | 18.5960 | 3.2816 | 14.30% |
| ×2 | 21.8139 | 3.8495 | 12.76% |
| Total | **56.6150** | **9.9909** | All below 25% |

These useful-work projections exclude startup, checkpoint/storage overhead, the legacy epoch diagnostic, idle lanes and requeues. The log's repeated step-creation waits reinforce that distinction. They do not replace launch reservations: study **51 × 2 h = 102 requested GPU-h**, conservatively **13 × 4 × 2 = 104**; B2 **9 × 2 = 18**, conservatively **3 × 4 × 2 = 24**.

The supplied coordinator ledger is **184.41 used of 350 before this smoke**, leaving **165.59**. Reserving one complete 4-GPU/80-minute smoke allowance, then conservative B/B2, leaves **32.2567 GPU-h**. More conservatively, allowing a full 80 minutes for **each of the two evidenced smoke allocations** costs **10.6667 GPU-h** and leaves **26.9233 GPU-h after 104 + 24**. Thus B/B2 fit even under that broader smoke allowance. These are capacity envelopes, not claims about actual smoke expenditure. Additional jobs/retries/requeues must remain within the existing cap; Stage C has no reservation in this calculation and still needs its specified later accounting/package review.

**M1 — MEDIUM, nonblocking: accounting provenance remains partial.** The coordinator's reconciliation supersedes the old understated 119-plus-4–5 narrative. However, the supplied pre-smoke capture contains **63 rows since 25 October**, summing to **49.9481 requested-GPU elapsed hours** or **51.6756 allocated-GPU elapsed hours**; it is not the stated 69-job reconciliation from 22 October. The ledger describes its reconciliation using allocated GPUs, whereas the historical cap uses requested GPUs. I accept the explicitly supplied 184.41 as the conservative planning baseline, not as a firsthand reconstruction of every charged interval. The single fresh sacct row gives **0.2911 GPU-h for its reported elapsed field** and must not be presented as the complete two-allocation smoke cost. Preserve the commands' existing accounting refresh before submission and include requeues and intervening work. The conservative fit above keeps this nonblocking.

**L1 — LOW, nonblocking: narrative status is partly stale.** The 10:54 execution-log entry records the fresh smoke correctly, but its top status table, `STAGE_B.md`, `STAGE_B_H1_FIX.md` and the commands' closing status still describe that smoke as pending. The operational handoff should point to job 3752522 and this report outside the sealed payload. This review changes none of those files.

Disposition: **close H1 and PASS the exact Stage B study binding above**. The coordinator can record the actual plan/package/smoke-bound review and proceed within the existing owner authorization and budget process. This certifies neither completed study results nor B2 adoption or Stage C; their already specified later reviews remain applicable. The original HOLD stays intact.

VERDICT: PASS | BLOCKERS: 0 | HIGH: 0
