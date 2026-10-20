# L1 — S6 corrected-label overlays: scripts, mock and deployment

17 October 2026. **No job submitted.** The coordinator retains submission authority. All requested pre-submit gates passed; the node parity gate will run inside the coordinator-submitted job.

## Identity and scope

This worktree is `greek-ocr-toolkit-spellcheck-l1`, branch `opus/spellcheck-l1`, HEAD `748c182839200d8db236b382272f08fd07b78f24`. A read-only diff against `efdf5756` is empty for `greekocr/`, `m2_run.py` and `agreement_mode.py`. **S6/SF1 at efdf5756 is frozen and hash-bound.** No `.git` writes or other-worktree edits were performed. The existing `.cache/labelfix` symlink was used only to read frozen C1/instrument artifacts; all new caches and outputs are under this worktree's `artifacts/labelfix_l1/`.

Input is every `greek_poly` row of `docs/records/harvest/collection/v2/import_real_v2_train.jsonl`: **124,669 lines / 318 documents**, from 214,436 total train rows. Original source SHA-256: `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`. Original labels and frozen source files remain unchanged after the mock. See [L1_input_receipt.json](L1_input_receipt.json), [L1_binding.json](L1_binding.json) and [L1_local_revalidation.json](L1_local_revalidation.json).

| Actual wave | Polytonic lines |
|---|---:|
| round1 | 43,869 |
| parliament | 27,224 |
| vouli | 23,088 |
| round2 | 17,026 |
| mixed | 13,227 |
| openarchives | 235 |

The coordinator's five listed waves sum to 124,434. The source also has 235 `openarchives` rows; all are retained under the all-polytonic scope. Release coverage uses these **six actual waves** and all **12 source values**.

**89,767 rows are out of scope:** `greek_mono` 58,749; `latin` 13,107; `cyrillic` 11,531; `greek_latin_cs` 6,380. They do not enter L1 processing or corrected/control subsets. Each manifest records these counts and the explicit scope statement. Production overlays contain the 124,669 polytonic rows; mixed-selection out-of-scope status handling is tested.

## Exclusions and R0

The full selection was checked using R1's frozen exclusion sets and canonical document/line identities, normalizing human suffixes. Every current required intersection is zero:

| Exclusion | Excluded docs | Excluded lines | Input doc intersection | Input line intersection |
|---|---:|---:|---:|---:|
| heldout_14 | 14 | 666 | 0 | 0 |
| DEV_3 | 3 | 598 | 0 | 0 |
| summary_heldout_27 | 27 | 666 | 0 | 0 |
| import_real_v2_test | 92 | 44,029 | 0 | 0 |
| v2_test | 92 | 42,038 | 0 | 0 |
| wikisource_human | 25 | 1,392 | 0 | 0 |
| e1_real_test | 36 | 3,600 | 0 | 0 |

A planted document or line overlap fails closed. [L1_input_documents.txt](L1_input_documents.txt) lists all 318 input documents, SHA-256 `5386fb3dfcd5846edf87a16a4fa305814ae89f69c61f358966a382614e98b061`. **The locked R0 fresh-book set has not been drawn. R0 must draw only outside this inventory and publish its own zero-intersection receipt.** No current R0 result is claimed.

## Entry points and output policy

`l1_job.sbatch` calls `l1_run.py` for both mock and node execution. `--detector s6` is explicit; a detector/binding mismatch fails closed. A future S7/L1b run needs a separately prepared/qualified bundle; release naming supports `v2-corrected-presence-s7` and `v2-corrected-full-s7`.

Before any training-crop processing, `l1_verify.py` runs the 32 held-out instruments with the deployed detector, R1 and full M2 composition. It compares canonical UTF-8 detector readings/parts/localisation and both combined readings with every HOLD decision/reason against the shipped local M2 expected output. A difference writes `verification/parity_receipt.json` and stops before training-crop alignment/detection and before any L1 overlays/releases. Success copies `parity_receipt.json` to the run root. Instruments are never L1 input.

After the gate, the job runs:

1. Unchanged `c1_run.py` on the new 33,200-row selection, with four GPU workers and the E3 full_s0 checkpoint; reuse all 91,469 old C1 alignments.
2. S6 on CPU with 64 workers. Each worker also calls unchanged `r1_extract.extract_line(..., evaluation=True)` on the same decoded crop. This preserves R1 font-height windows and coverage rules without labels entering detector/window inference. Only A's wide windows are stored; the original extraction still computes its narrow view.
3. R1-A on GPU 0, fp32, TF32 disabled, no autocast. Both modes call unchanged `m2_run.combine`, including print-preserving K1 flags.
4. Both overlays and corrected/control-subset releases. Any HOLD drops the entire line. A recogniser/original base-letter or non-mark punctuation mismatch also holds the line; detector apostrophes/quotes can be composed. Original labels are never overwritten.

Alignment has a binding/summary; every detector/window and R1/composition shard saves an independent receipt and payload hashes. Timeout can leave those results without a final run receipt or complete release. All stages use `venv_l1`.

Per variant, `release/` contains `overlay_<variant>.jsonl.gz`, `release_<variant>.json`, `release_ctrl_subset_<variant>.json`, `ctrl_subset_<variant>.jsonl.gz`, and `kept_<variant>_line_ids.txt`. Overlays have the required status, changes/evidence and HOLD-reason schema. Edit starts are original-label NFD offsets; evidence slots keep recogniser NFD offsets. Manifests bind source/overlay SHA-256, code commit, detector/policy/model hashes, status counts, coverage per wave **and per source**, exclusions and R0 policy. Each control uses exactly the corrected arm's kept IDs and their ORIGINAL labels; the actual written control payload is checked against the kept set.

R1-A SHA-256: `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636`. The full binding, source/asset policy and expected parity payload are in deployed `artifacts/labelfix_l1/binding/`.

## Bounded mock, parity, timing and tests

Only **192 distinct crops** were processed: 160 training crops (80 old C1, 80 new C1, all six waves) plus 32 held-out instruments across all 14 instrument books in separate verification mode. Development reruns reused these same crops. Golden reference generation called unchanged `m2_run.infer_line`, without labels or truth. The first parity run caught NFC/NFD serialization in the wrapper and stopped before training processing; the wrapper was corrected without changing S6 or M2. A later overlay check repaired the evidence letter for an inserted final combining mark.

Final parity is **32/32 exact**, including whole canonical files byte-for-byte. Expected/actual SHA-256: `6587287bef8da8af5d323a76c2dbfd0096dc4148aebf238a2a923cba7f07d305`. Both mock variants contain 160 rows: **5 corrected, 29 unchanged, 126 HOLD**. The 34 kept IDs match each paired control. These are smoke-test counts, not production coverage or mark-quality claims. Mock output is separate from production. See [L1_mock.log](L1_mock.log), [L1_mock_receipt.json](L1_mock_receipt.json), [L1_parity_receipt.json](L1_parity_receipt.json) and `artifacts/labelfix_l1/mock_checked_192/release/`.

Per-line detector, window and R1 timings appear in the mock log. R1 timings are measured per line, not apportioned from a batch. The final timing summary is [L1_timing_summary.json](L1_timing_summary.json). The approved planning estimate remains **25–35 minutes (30 minutes central)** with a 60-minute limit, including alignment, CPU extraction/detection, GPU R1, composition, I/O and startup reserve. This is not measured node throughput. No allocation or GPU qualification job was launched.

Final mock wall time: **38.76 seconds**. The 80 new C1 CPU alignments took 17.18 seconds including startup. The 160 training lines produced 3,643 R1 windows.

| Measured CPU stage | Mean seconds/line | p95 seconds/line | Total seconds |
|---|---:|---:|---:|
| S6 detector | 0.02932 | 0.05346 | 4.691 |
| R1 window extraction | 0.00371 | 0.00603 | 0.594 |
| R1 inference | 0.04882 | 0.07451 | 7.811 |

**235 labelfix tests pass**, including 11 L1 cases covering statuses/evidence, all HOLD reason families, recogniser letter mismatch, punctuation, monotonic/other-script exclusion, planted document/line overlap, paired control sets and unchanged original source bytes. No tests were deselected or existing tests changed. See [L1_pytest_labelfix.log](L1_pytest_labelfix.log).

## Isolated SciPy runtime

Coordinator-authorized attempt-2 option A was used. `cp -a` copied E3 to the separate `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1`; configuration/activation/script paths were repaired only in that copy. The only installation was `pip install --no-deps scipy==1.17.1`. It succeeded on the login node without proxies or alternate indexes. **The E3 venv was not modified.**

Before/after E3 file lists bind sorted relative paths, modes, sizes, mtimes and symlink targets. Both SHA-256 values: `379466f022be1344d437e24d050ab54ea4ddad8009dc3d67aed2e84fb153af5b`. Post-deploy verification rechecked the digest successfully. Runtime: Python 3.12.15, torch 2.11.0+cu128, NumPy 2.5.4, Pillow 12.3.0, SciPy 1.17.1, OpenCV 5.0.0. Base interpreter: `/users/fffoivos/.local/share/uv/python/cpython-3.12-linux-aarch64-gnu/bin/python3.12`.

[L1_runtime_receipt.json](L1_runtime_receipt.json) records base/venv paths and full pip freeze. Before/after file lists, pip log/freeze and the per-file SciPy SHA manifest are retained in `L1_runtime/`. The SciPy package, bundled libraries and distribution metadata are bound; `l1_runtime.py --verify` asserts them again in the job prologue.

The requested certificate check reported validity 2026-10-16 19:17:52 through 2026-10-17 19:18:52. SSH succeeded. No certificate refresh was attempted.

## Deployment and coordinator handoff

Destination: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/`. Request: **debug, a0140, one exclusive node, 01:00:00**. Live debug limits: MaxTime 01:30:00, MaxNodes 4; debug-qos MaxJobsPU 1, MaxSubmitPU 2. The scheduler test uses the explicit `--partition=debug` form.

The full deploy list is [L1_DEPLOY_SHA256.txt](L1_DEPLOY_SHA256.txt); original source, checkpoints, C1 alignments and runtime bindings are in [L1_EXTERNAL_SHA256.txt](L1_EXTERNAL_SHA256.txt). Existing Clariden data/models are reused. No crops or checkpoints were transferred.

**Remote gates passed.** All **299/299 deployed files** and **11/11 external bindings** match; the remote deploy manifest was retrieved and is byte-equal to the local list. Deploy-list SHA-256: `76cb6c7403816fb9b8008690e88583d189fb97ff71dd0e484aaa5d2fc1963405`. See [L1_remote_sha256_final.txt](L1_remote_sha256_final.txt) and [L1_DEPLOY_REMOTE_SHA256.txt](L1_DEPLOY_REMOTE_SHA256.txt).

**124,669/124,669 crops present**, 91,469 C1 inventory hashes unchanged plus 33,200 newly inventoried; **32/32 parity crops present and hash-equal**. Zero missing or mismatched crops, 4,407,724,367 training-crop bytes. No image decoding occurred during this inventory; no crops were transferred. Inventory took 175.77 seconds. See [L1_inventory/inventory_receipt.json](L1_inventory/inventory_receipt.json) and [L1_inventory/L1_crop_inventory.jsonl.gz](L1_inventory/L1_crop_inventory.jsonl.gz).

The exact scheduler test was `sbatch --test-only --partition=debug --export=ALL,L1_DETECTOR=s6 scripts/labelfix/clariden/l1_job.sbatch` (exit 0). [L1_sbatch_test_only.txt](L1_sbatch_test_only.txt):

```text
sbatch: Job 3679303 to start at 23:46:22 a using 288 processors on nodes nid006105 in partition debug
```

This is scheduler validation output, not a submitted job. The test does not execute the 32-line node parity gate. The job must pass that gate before training-crop processing. The certificate evidence is [L1_certificate.txt](L1_certificate.txt).

Exact coordinator submit command (documented only; **not executed**):

```bash
ssh clariden 'cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017 && sbatch --partition=debug --export=ALL,L1_DETECTOR=s6 scripts/labelfix/clariden/l1_job.sbatch'
```

L1 READY: mock ok (192 lines, parity 32/32); input 124669 greek_poly (out of scope 89767); exclusions all 0; runtime venv_l1 (scipy 1.17.1, E3 venv unchanged); in-job parity gate 32 lines; deploy sha256 299/299; test-only sbatch: Job 3679303 to start at 23:46:22 a using 288 processors on nodes nid006105 in partition debug; est 30 min
