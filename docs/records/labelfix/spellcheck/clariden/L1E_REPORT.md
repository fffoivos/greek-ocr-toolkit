# L1E — ENSEMBLE_AB gate and prepared Clariden job

**READY for coordinator submission, 17 October 2026, 02:10 Athens. No job submitted.** The deployed job requests `a0140`, `debug`, one exclusive node, one task and `01:00:00`. All 380 labelfix tests pass, the exact sbatch CPU mock passes on 64 lines with 64/64 decision parity, deployed files verify 325/325, external bindings verify 4/4, and `sbatch --test-only` succeeds.

Workspace: `greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`, HEAD `45ebb4d7097b8d7c51dd51ca13b62c2b20896449`. The two commits following SF2 `0472a908` contain the L1E brief and restart ruling. No Git write commands were run; no other worktree was modified. The first attempt's 01:51 transport stop is preserved in [attempt1_report.md](L1E_evidence/attempt1_report.md). Access succeeded after the restart ruling; no certificate refresh was attempted. Interrupted deployment contents were replaced and rehashed before use.

## Shared gate and validation

`greekocr/labelfix/release_gate.py` provides PRESENCE, FULL, ENSEMBLE_AB and diagnostic ENSEMBLE_AE. A supplies mark names. The ensemble peer must predict an identical mark set. A/B or A/E disagreement causes HOLD. Reader UNKNOWN/uncertainty, missing or malformed predictions/coverage, unresolved detector localisation/segmentation, unnamed marks, relevant clipping/UNSEEN zones, K1 flags and the SF2 edit guard remain HOLD conditions. Detector mark-kind disagreement alone does not veto ensemble acceptance. Apostrophes and opening quotes come from detector evidence.

Release, measurement and page adapters use the same composer. New tests cover clean agreement, disagreement, every requested uncertainty class for both readers, detector-kind disagreement, punctuation, edit guards, checkpoint identity failures, missing/corrupted/unaccounted windows, historical-output protection and actual release/control payloads, including two-worker release execution. **380 passed in 5.19 seconds**; `git diff --check` also passed. See [tests.log](L1E_evidence/tests.log).

Final policy: `l1e-release-v1`, digest `965f3c5575ae8d385b2128919ba4e181b9992a3f5edaacbb6982f1789851a6b7`.

## Held-out print-truth table

The final **666-line** measurement ran on Clariden using the saved R1 A/B/E predictions, S6 detector evidence and the **frozen S4 ownership/truth instrument used by R1 RESULT**. There were no detector or model runs for this measurement. Each arm's prediction, extraction/index and checkpoint bindings were checked. The frozen ownership instrument reproduces **80 Google mark errors**, with 10,046 known and 300 unknown-truth mapped/scored slots. Unknown truth is excluded from outcome counts and retained in decisions.

| Shared mode | Corrected / 80 | Wrong | Missed | HOLD errors | New errors | Lines held / 666 |
|---|---:|---:|---:|---:|---:|---:|
| PRESENCE | 42 | 1 | 2 | 35 | 5 | 345 |
| FULL | 37 | 0 | 0 | 43 | 3 | 362 |
| ENSEMBLE_AB | 46 | 2 | 6 | 26 | 6 | 268 |
| ENSEMBLE_AE, diagnostic | 46 | 2 | 6 | 26 | 9 | 253 |

The first four outcome columns partition the 80 known Google errors. “New” counts accepted mark errors where Google was correct. Outcomes are **slot acceptance**, not counts of whole lines admitted to a training release; “lines held” counts lines containing any shared-composer HOLD, including holds outside the known-error slots. Punctuation is excluded from this mark-error instrument, but participates in composition and release.

The brief's historical PRESENCE reference is **48 corrected / 2 wrong / 5 new / 50 lines held**. It predates this complete SF2 observation/edit-guard gate and must not be substituted for the current PRESENCE row. The preserved historical component-proxy instrument explicitly lacks R1 coverage and detector segmentation/observability. Current rows use the same frozen truth/error population with the complete shared gate.

The older R1 extraction predates explicit `evidence_state`/`uncertainty` fields. The measurement adapter recovers the **unchanged L1 extraction predicates** from saved `pixel_measurements`, spans and hash-bound PNG header dimensions; it does not decode or re-extract pixels. Missing font measurements fail instead of defaulting to clean. Details: [observation recovery](L1E_evidence/heldout_final/observation_recovery.json).

The final deployed-source rerun took **27.869 seconds**, reproduced all table counts and all 666 earlier decisions, and has SHA-256 `d50f638647ddea75f830a953e79e0172d9cd6ab1e9190485838a2cec23883d79`. See [measurement receipt](L1E_evidence/heldout_final/measurement_receipt.json), [events](L1E_evidence/heldout_final/events.jsonl), [decisions](L1E_evidence/heldout_final/decisions.jsonl.gz), and [remote readback](L1E_evidence/remote_readback/final_evidence_receipt.json).

## Stored windows and job behavior

The completed read-only audit verified **all 124,669 lines, 2,901,998 wide windows and 974 shards**, with **zero missing or repaired shards**, in **295.889 seconds**. Detector/run receipts, every stored array/sample/detector hash, array shapes, line identities and every scored extraction start verified. The audit receipt was rehashed after the interrupted connection: `bd11cd7527ee58315878338475a265332b33bf21d2d42726f4e8a60c894290df`. See [windows receipt](L1E_evidence/windows_receipt.json).

`l1e_job.sbatch` runs `l1e_run.py` through these steps:

1. Recheck deployed/external hashes and audit the historical detector shards. If a wide array is missing, `l1e_windows.py` uses unchanged L1 extraction and original crops/cached spans, writing into a new output directory. Historical samples, coverage and the original array hash must reproduce. L1-v0 is never written.
2. Verify historical A predictions against every audited stored sample and detector record. Load B/E using SHA-256, arm identity and strict model compatibility; B has no letter embedding, E has its original embedding. Run the unchanged L1 `predictions()` function on stored wide windows, on GPU in fp32 with TF32 disabled and no autocast. A's historical checkpoint identity is also checked.
3. Call the SF2 shared `l1r_recompose.py`, producing PRESENCE, FULL and ENSEMBLE_AB overlays, kept-ID lists, paired original-label controls and manifests named `v2-corrected-presence-r`, `v2-corrected-full-r` and `v2-corrected-ensemble-ab-r`. Each includes wave/source coverage, exclusions, original source hashes, checkpoint/code/policy hashes and the caveat below. Diagnostic E predictions remain in the inference shards.

The job writes a window-audit receipt, a durable inference receipt for every shard, an inference-step receipt, release/control manifests, a recomposition receipt and the final run receipt. A timeout preserves completed shard files and receipts. Reusing an inference shard requires identical inputs and output hashes. Incomplete releases are not advertised by a completed recomposition/run receipt.

All steps use `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python`; this is the existing L1 runtime, **torch 2.11.0+cu128 / CUDA build 12.8**. The detector-free path does not switch to the E3 venv. The original L1 sbatch uses this same venv directly. All three checkpoint identities and their fp32 floating tensors were read back without inference.

| Binding | SHA-256 |
|---|---|
| Historical run receipt | `2042fd48b6250636e7847d3b6a1cd6f8a3111dd31575af30c198e63e4d6062bc` |
| A checkpoint | `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636` |
| B checkpoint | `f25f16e633966ec16037099e27ee75624b9a3600d96682dca654aeded9396d69` |
| E checkpoint | `330b43a04dc47425d3da977f06f28aaa54bee681700d81feef0bcb8ea1ed42c5` |
| Unchanged L1 inference | `0710ca4c41c13b6804dcd8beacf16d0b7732cc76403c02a93abf1e40de2875ba` |
| Unchanged L1 extraction | `e16f0b69a853c9172bf40329af473480ddb7852bfef5930903f8e9f5314986ca` |
| Unchanged pixel helpers | `ee516375fb7447720d8efbb67a1cabf05e0861f48ee1b20a192000445137d3d6` |

Required release-manifest text, included verbatim in every corrected/control manifest:

> A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label experiment.

## Exact-entry-point Mac mock

The mock used **64 verification-only held-out lines / 1,051 stored windows**, with the real B/E checkpoints, CPU fp32 inference and the exact job entry points. No full 666-line or training-wave processing ran on the Mac.

```bash
L1E_MOCK=1 \
L1E_PYTHON=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
L1E_CONFIG=artifacts/labelfix_l1e/config/l1e_mock.json \
L1E_OUT=artifacts/labelfix_l1e/mock_run_v4 \
bash scripts/labelfix/clariden/l1e_job.sbatch
```

The completed run took **5.112 seconds**; inference/shard serialization took **3.836 seconds**. The full decision record—text, parts, status, HOLD starts/reasons and apostrophes—matched **64/64 lines across all four modes**. Final remote readback confirms the expected-decision fixture is identical to the final 666-line measurement. Both extraction accounting and the actual release/control payloads passed. Mock whole-line corrected/unchanged/HOLD counts were PRESENCE **14/1/49**, FULL **11/0/53**, and ENSEMBLE_AB **20/3/41**. These verification labels are never training inputs.

Evidence: [mock log](L1E_evidence/mock.log), [run receipt](L1E_evidence/mock_run_receipt.json), [parity receipt](L1E_evidence/mock_parity_receipt.json), [inference receipt](L1E_evidence/mock_inference_receipt.json), [recomposition receipt](L1E_evidence/mock_recomposition_receipt.json).

## Deployment, scheduler check and estimate

Deployment root:

```text
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/
```

The exact 3,758,080-byte deployment archive was SHA-checked before extraction. Every **325/325** listed file passed remote `sha256sum --check`, and was compared locally to the deployed source/configuration. The **4/4** external bindings passed separately. Full lists and readback logs are retained:

- [L1E_DEPLOY_SHA256.txt](L1E_evidence/L1E_DEPLOY_SHA256.txt), SHA-256 `9addae32df7cd337462e4c459dbe6dda8d556055840de032e21f9604921a7e7e`.
- [L1E_EXTERNAL_SHA256.txt](L1E_evidence/L1E_EXTERNAL_SHA256.txt), SHA-256 `0e63e2285d1a76905e861f938f400db17253505d1e2136220f915e4e34fb5e1a`.
- [Remote deployed-file checks](L1E_evidence/remote_readback/deployment_sha_check.log) and [external checks](L1E_evidence/remote_readback/external_sha_check.log).
- Executable configuration `config/l1e_job.json`, SHA-256 `a0f7a5b0a43db5fafb43ea507c437f5a70c1a265757f69a2d91a9ee9f6c6be64`.

Live `debug` was UP, with `debug-qos` and a 01:30:00 partition maximum. The exact job requests 01:00:00. `sbatch --test-only scripts/labelfix/clariden/l1e_job.sbatch` returned exit 0:

```text
sbatch: Job 3679519 to start at 01:05:27 a using 288 processors on nodes nid007645 in partition debug
```

This is scheduler validation output, not a submitted job or reserved node. Deployment/external manifests, executable configuration and sbatch script were rehashed after the test and were unchanged. See [test-only output](L1E_evidence/remote_readback/test_only.log) and [partition/runtime/binding readback](L1E_evidence/test_only_and_runtime.log).

**Planning estimate: 45 minutes, with a 35–55 minute range.** The observed window audit costs 4.93 minutes. Historical L1 on this exact population spent 58.438 seconds on A GPU inference and 1,314.995 seconds on inference/composition together; its total was 1,785.544 seconds. Two reader passes suggest roughly two minutes of GPU arithmetic, while shard decoding, serialization, integrity checks and recomposition dominate. The new three-mode recomposition uses 16 workers with bounded batches. The estimate allows for the extra reader outputs and a separate recomposition pass; it is a forecast, not measured L1E GPU throughput or a guarantee against filesystem stalls. Per-step/per-shard receipts retain completed work if the one-hour limit is reached.

Exact **coordinator-only** submit command, prepared but not executed:

```bash
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017
sbatch scripts/labelfix/clariden/l1e_job.sbatch
```

L1E READY: gate ENSEMBLE_AB tests ok; held-out AB corrected 46/80 wrong 2 new 6 lines held 268 (PRESENCE 48/2/5/50); mock ok (64, parity 64/64); windows stored all; deploy sha256 325/325; test-only sbatch: Job 3679519 to start at 01:05:27 a using 288 processors on nodes nid007645 in partition debug; est 45 min
