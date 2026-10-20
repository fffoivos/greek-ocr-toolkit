# L1R — SF4 Clariden recomposition readiness

17 October 2026. **Prepared, mocked, deployed and scheduler-tested; not submitted.** All 124,669 input lines / 974 shards passed the receipt/hash audit, all 256 mode/line and 7,620 slot/mode mock decisions match SF4, all 635 labelfix tests pass, and all 317 deployed files match locally and remotely. The coordinator submits only after the ongoing verification pass permits it.

Work used only `greek-ocr-toolkit-spellcheck-l1r`, branch `opus/spellcheck-l1r`. Actual HEAD is `137320ebb970fd0fcc8ccfc589bf0658f5016f66`; its sole addition over the brief's `47f7b6b0` is `docs/records/briefs/L1R_recompose_job.md`. No Git metadata writes were made: all seven metadata files retain their recorded hashes ([check](L1R_evidence/git_unchanged.json)). The separate `greek-ocr-toolkit-spellcheck` verification worktree was not written. No certificate refresh, model execution, detector execution, training or job submission occurred.

## Inputs verified in place

Base: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/`.

- L1-v0: `output_3679313/`; complete historical run, detector shards, stored windows/samples/timings, A predictions and coverage, input/exclusion receipt and binding.
- L1E: `l1e_20261017/output_3679545/inference/`; complete B/E inference receipt and every inference shard. **974/974 shards, 124,669 lines, 2,901,998 samples** match the historical shard counts and bindings. L1E also has a completed downstream run, but L1R neither depends on nor consumes its recomposed releases.
- Selection: `artifacts/labelfix_l1/binding/selection.jsonl`; 124,669 unique IDs, bound to the detector and B/E receipts.
- Original labels: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2/import_real_v2_train.jsonl`, checked against the original input receipt and binding.
- A/B/E checkpoint files and the SciPy manifest were checked against pinned SHA-256 values.

The final deployed entry point checked **8,784/8,784 input hashes**, including every historical step receipt, detector payload, A combined shard and B/E combined shard. It checks completion, checkpoint identities, population counts, selection identity and every B/E shard's binding to the corresponding A/window receipts. Missing/incomplete B/E inference fails closed. The job repeats this verification before release construction and rechecks the inputs before its final completion seal. Workers also compare actual line IDs, detector/A evidence, B/E prediction slots and peer coverage before composing each shard.

Final audit: **14.000 seconds**, four hashing threads, no composer/inference execution. See [full input receipt](L1R_evidence/input_verification.json) and [entry-point output](L1R_evidence/input_verification.log). Only small manifests/logs were returned from Clariden; no training-population evidence, arrays, crops or prediction shards were transferred to the Mac.

| Input | SHA-256 |
|---|---|
| L1-v0 run receipt | `2042fd48b6250636e7847d3b6a1cd6f8a3111dd31575af30c198e63e4d6062bc` |
| L1E inference receipt | `f9af3fb24cecf1e5559b202d014c1dd697411656764840a5ee001c101bad8ee6` |
| Selection | `ee6c51bdeb9131fd65361d060fd34b77823c1321d3a77849581cfaa577bd3eec` |
| Original label source | `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3` |
| A checkpoint | `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636` |
| B checkpoint | `f25f16e633966ec16037099e27ee75624b9a3600d96682dca654aeded9396d69` |
| E checkpoint | `330b43a04dc47425d3da977f06f28aaa54bee681700d81feef0bcb8ea1ed42c5` |
| SciPy manifest | `843ad752f7115545e2b5b0f0308b8a4b21829a7a67ecc1e2da43b97a21ac2596` |
| Final input-verification receipt | `5883758738b7df50ad70e2d5b10f4d3f965ecb3619a230f06a6d18c7f99425b0` |

Runtime is `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python`. All **2,398 entries** of `runtime/L1_scipy_SHA256.txt` passed; SciPy is **1.17.1**, imported from that venv. The sbatch prologue repeats the manifest and import-path assertions ([readback](L1R_evidence/remote_readback/runtime_verify.log)).

## Implementation and output contract

The exact entry point is [`l1r_recompose.py`](../../../../../scripts/labelfix/clariden/l1r_recompose.py), using the unchanged SF4 `release_gate.py`, policy `sf4-release-v1`. The gate's SHA-256 remains `fc3dc4b3370e8b1a205fe1a2acf55634b189c1cb49f57536a61f44f31a52598a`; reading/text/segmentation bytes also match the saved SF4 full-composer check.

The orchestration changes the source-binding digest to `88f3280a1cc7de3ec5d6b6dd08d9899f96af0baebfb26c8643b3e70788c3125f`: this binds the revised composer consumer and orchestration, while the scientific gate bytes remain unchanged. The [remote policy readback](L1R_evidence/remote_readback/deployed_policy.json) equals the policy used by the final mock. Current recomposition code hashes and historical inference code hashes are recorded separately; the old L1E code map never replaces the SF4 code map.

The job writes beside L1E's output:

```text
.../labelfix_l1_20261017/l1e_20261017/l1r_sf4_<jobid>/
  input_verification.json
  shards/shard-00000/{selection.jsonl,release/*,receipt.json}
  ...
  release/{overlay_*.jsonl.gz,kept_*_line_ids.txt,ctrl_subset_*.jsonl.gz,release_*.json}
  receipt.json
```

Three corrected releases are named `v2-corrected-presence-sf4`, `v2-corrected-full-sf4`, and `v2-corrected-ensemble-ab-sf4`; their paired controls are `v2-ctrl-subset-presence-sf4`, `v2-ctrl-subset-full-sf4`, and `v2-ctrl-subset-ensemble-ab-sf4`.

Each manifest includes per-wave/per-source status coverage, the unchanged L1 exclusion and R0 receipts, original-source and selection hashes, checkpoint hashes, current and historical code provenance, policy binding, and a resolvable hash-bound input-verification receipt. Every overlay line has its original-label SHA. HOLD/out-of-scope rows have no released label and enter neither kept lists nor original-label controls. Validation reads the actual overlays, controls and ID files to establish equality of the accepted line sets and preservation of original control labels.

The same release consumer composes each shard, with selection records matched by **line ID** rather than assumed alignment order. Thirty-two worker processes operate on separate shards. Full-source hashing occurs before/after the run, avoiding a repeated full-manifest scan per shard. Completed shard directories are atomically renamed with hash-bound receipts; exact-input restart can reuse them after a timeout. Final gzip JSONL files concatenate verified shard members and are decoded/validated again before the complete run receipt. A timeout leaves durable completed shards, without advertising an incomplete aggregate release. L1-v0 and L1E are never modified.

Every corrected/control manifest contains this exact string:

> A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label experiment.

## Exact-entry-point 64-line mock and tests

The mock consumes the complete saved L1E verification runtime whose two input hashes are pinned by [SF4's original parity receipt](../SF4_evidence/runtime64_parity.json). It uses saved A/B/E predictions; it runs no inference or detector and processes no training-wave population on the Mac.

```bash
PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  scripts/labelfix/clariden/l1r_mock_check.py \
  --config artifacts/labelfix_l1r/mock.json \
  --out artifacts/labelfix_l1r/mock_verified \
  --evidence docs/records/labelfix/spellcheck/clariden/L1R_evidence
```

The checker invokes the exact job entry point with two shard workers. **64/64 lines, 256/256 mode/line decisions and 7,620/7,620 slot/mode decisions** match the local full composer across PRESENCE, FULL, ENSEMBLE_AB and diagnostic ENSEMBLE_AE. The actual three-mode release overlays additionally match **192/192 mode/line and 5,715/5,715 slot decisions**. SF4's saved numbers of lines held are reproduced: **48 / 52 / 42 / 37**. Release-level original-label edit guards add one held line in each emitted variant, giving **49 / 53 / 43** held release rows; those guards also remain active.

The exact entry point completed in **2.133 seconds**, including a **1.828-second** shard with the optional four-mode diagnostic audit. [Parity receipt](L1R_evidence/mock_parity.json), [mock log](L1R_evidence/mock_verified.log), [complete mock output/receipts](L1R_evidence/mock/receipt.json), and [mock manifests/payloads](L1R_evidence/mock/release/release_ensemble_ab.json) are retained.

**635 passed in 5.95 seconds**, with no skips/errors/deselections ([all labelfix results](L1R_evidence/tests_labelfix.log)):

```bash
PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  -m pytest -q tests/labelfix -p no:cacheprovider
```

Seven new integration cases cover reversed selection/shard order, two-process execution, timeout/restart reuse, aggregation recovery, incomplete/missing/corrupt B/E inputs, changed checkpoint identity, missing peer fields, and refusal to write within/around historical input paths. The sbatch script also passes `bash -n`.

## Deployment, scheduler check and estimate

Deployment: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf4/`.

**317/317 files** passed remote `sha256sum --check`; the remote SHA list is byte-identical to the local list, and the local source tree matches every deployed source. Full [deploy SHA list](L1R_evidence/L1R_DEPLOY_SHA256.txt), [external SHA list](L1R_evidence/L1R_EXTERNAL_SHA256.txt), [remote check output](L1R_evidence/remote_readback/deploy_verify.log), and [readback verification](L1R_evidence/deploy_verification.json) are retained. The deployment-manifest SHA-256 is `b896e1bbed4d2513c24d84a50e136f016e190c7268811965a30ed983b1c81df6`.

| Deployed entry | SHA-256 |
|---|---|
| `l1r_recompose.py` | `a440c34bd8129c01972ba2992b905bd1e89fbbf5e166288b32bf53dcf0806239` |
| `l1_common.py` | `63290471995a03b7c3cc8d0148c72a968559ee9cfb29a4e10aca923e6514ca02` |
| `l1r_job.sbatch` | `20ef6bf2f9099b42a85cbc39e4f9568fa679d76e16aa052879ba4885a1a2f2fb` |

[`l1r_job.sbatch`](../../../../../scripts/labelfix/clariden/l1r_job.sbatch) requests account `a0140`, partition `debug`, one exclusive node, one task, 64 CPUs, a **01:00:00** limit, and 32 CPU workers. It requests no GPU execution. Live `debug` is UP, with a **01:30:00** partition cap, `debug-qos`, maximum four nodes per QoS job and one job per user ([partition](L1R_evidence/remote_readback/partition_debug.txt), [QoS](L1R_evidence/remote_readback/qos_debug.txt)).

The exact `sbatch --test-only scripts/labelfix/clariden/l1r_job.sbatch` returned exit **0**:

```text
sbatch: Job 3679708 to start at 02:13:05 a using 288 processors on nodes nid005421 in partition debug
```

This is the scheduler's test-only prediction, not a submitted job or allocation. The node is exclusive, hence the reported 288 processors. Deployment manifest, config, sbatch script and input-verification receipt hashes stayed unchanged across the test ([before hashes](L1R_evidence/remote_readback/test_only_before.sha256), [after check](L1R_evidence/remote_readback/test_only_unchanged.log)). The final audit began at cluster timestamp `2026-10-17T02:12:41+02:00`.

Planning estimate: **15 minutes**, aiming for ≤20 minutes within the one-hour limit. The completed input audit takes 14 seconds; the 64-line Mac shard takes 1.828 seconds including diagnostic work. Ideal 32-worker scaling would put that shard work near two minutes, before platform differences, decoding, filesystem contention and serial aggregate validation. The 15-minute forecast allows substantial margin for those costs. It is not measured Clariden SF4 throughput; no compute job was launched to benchmark it. Durable shard receipts preserve completed work if the limit is reached.

Exact **coordinator-only** submit command, prepared but **not executed**:

```bash
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf4
sbatch scripts/labelfix/clariden/l1r_job.sbatch
```

L1R READY: policy sf4-release-v1; inputs verified ok (8784/8784 files, 974/974 shards); mock parity 256/256; deploy sha256 317/317; test-only sbatch: Job 3679708 to start at 02:13:05 a using 288 processors on nodes nid005421 in partition debug; est 15 min
