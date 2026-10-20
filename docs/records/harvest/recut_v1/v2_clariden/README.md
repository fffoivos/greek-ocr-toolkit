**T6f2 stopped: the numpy 2.4.6 retry failed the byte gate, 19/50.** The 31 differing output SHA256 values are the only differences among the compared fields; guard, match, wrong-line-risk, masked-pixel and component decisions agree for all 50. Phase 1 was not entered. No production pages, rate run, Slurm package, test-only command or real submission followed.

The retry used the identical seed `20261017`, selection, 50 existing pages (69,376,265 bytes), frozen `phase0_mask.py` and two-worker `phase0_launch.py`. All 50 page hashes and all deployed frozen source hashes were checked before execution. Every aggregate retry record binds the actual worker host, frozen tree, numpy pin, venv path, lockfile path and lockfile SHA256. All workers ran on `clariden-ln001`. The mock took 244.633 seconds; this is not the requested 1,000-crop rate.

| T6f2 check | Result | Evidence |
|---|---|---|
| Verified private venv copy | PASS: 27,376 entries / 6,758,923,289 file bytes checked; zero non-numpy changes; shared venv unchanged | [Verification](receipts/t6f2/venv_verification.json) |
| numpy-only package difference | PASS: `numpy==2.5.4` → `numpy==2.4.6`; every other freeze entry unchanged | [Shared before](receipts/t6f2/venv_l1.before.lock), [shared after](receipts/t6f2/venv_l1.after.lock), [pinned lock](receipts/t6f2/venv_np246.lock) |
| Original inputs and frozen code | PASS: exact original selection and Mac baseline; all 50 rasters rehashed; frozen code unchanged | [Input verification](receipts/t6f2/input_verification.json) |
| Output byte gate | **FAIL: 19/50 identical; 31/50 different** | [Comparison](receipts/t6f2/mock_comparison.json), [records](receipts/t6f2/mock_records.jsonl), [execution](receipts/t6f2/mock_execution.json) |
| Original/output custody | PASS: 50 originals and 50 outputs independently rehashed, zero custody mismatches | [Verification](receipts/t6f2/mock_verify.json) |
| Phase 1 stop boundary | No production transfer, rate, time limit, package, test-only or submission | [Status](receipts/t6f2/status.json), [remote path absence](receipts/t6f2/stop_boundary.json) |

`W/venv_np246/` is a filesystem copy, with no links back into `venv_l1`; its Python executable uses the same external base interpreter as the original. Only numpy-owned files and its two console scripts differ. No masking, matching, guard or PNG encoder code was changed. Pillow still reports zlib `1.2.13` in the pinned environment. The original shared environment fingerprint was reproduced before and after the final verification: `90a24609621ef12c07fd89b137d0fdd7681d6faa7a01534aee0aad8246c76862`.

The wheel is `numpy-2.4.6-cp312-cp312-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl`. Its SHA256 is `5f9fb9157b4ce2971008323afe46053787b526ef624fea915b261468a8421a0f` ([wheel receipt](receipts/t6f2/numpy_np246_wheel.sha256)); `W/venv_np246.lock` SHA256 is `69cbde45d47e05c4ced4a4011681303c13011db871b21421f8e07ebca81c6fa6`. The wheel was downloaded on Clariden into `W/t6f2/wheels/` with caching disabled and installed offline with `--no-deps`. The Mac connected only through Clariden SSH/rsync. The first setup check stopped because pip freeze recorded a direct wheel-file reference; reinstalling the same wheel by version through `--find-links` normalized the lock entry. [Setup correction](receipts/t6f2/setup_correction.json) preserves that first attempt and the completed verification. This did not change the frozen masking code.

Only Step A was executed. `W/pages/`, `W/out/`, `W/run_v2_mask.py`, `W/verify.py`, `W/mask_v2.sbatch`, `W/DEPLOY_SHA256.txt` and `W/test_only.txt` are absent. Parliament was never uploaded. No production time-limit arithmetic or coordinator sbatch command exists for this rejected retry. The terminal page count means **new production uploads in T6f2**: 0 pages / 0 GB; the original 50 mock pages were reused. The Mac fallback remains the separate T6h task.

The local handoff is hash-bound to HEAD `1a85772173ccae3853a7568319e31729fdfe6127` on `sol/recut-v1`. Git metadata is read-only in this sandbox, so no worker commit or Git write was attempted. [commit-inputs.json](commit-inputs.json) contains the exact local list. Check it with `python3 -B docs/records/harvest/recut_v1/v2_clariden/guarded_commit.py`; the coordinator can use the same command with `--commit` in a writable context. The helper checks HEAD, branch, an empty index, every file hash and the exact staged set, with no alternate index or retry. Validate the evidence with `python3 -B docs/records/harvest/recut_v1/v2_clariden/validate_receipts.py`.

The following T6f report is historical. Its unattempted actions, starting HEAD and deployment inventory describe the earlier phase 0 run; the T6f2 result above supersedes its handoff status.

**T6f stopped at Phase 0: the byte-identity gate failed.** The completed seeded mock has 19/50 byte-identical outputs and 31/50 SHA256 mismatches. No production masking, production page transfer, rate run, Slurm package, `sbatch --test-only`, or real submission followed the failure. The coordinator fallback is the Mac masking run under a separate brief.

The frozen source tree is `63c640a3aa4abe08d200258cf24d235dfa4a1625`; the worktree starts at `bb517940b1273439cf1b3e557e48769fc598b749` on `sol/recut-v1`. [Frozen source hashes](receipts/frozen_sources.json) verify the seven relevant source/config files byte-for-byte against that tree. Parameters remain `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`, and the masking library remains `f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5`.

| Phase 0 gate | Result | Evidence |
|---|---|---|
| Population and crop custody | PASS: 214,436 train / 44,029 test; full counts, full ID sets and manifest hashes match; 2,000/2,000 sampled original crop hashes match | [Local](receipts/local_population.json), [remote](receipts/remote_population.json), [sample](receipts/sample_2000.jsonl) |
| Page inventory and absence | PASS: 5,585 pages / 16,168,304,605 bytes; no original raster filename hits outside the new work directory in the inspected E3 tree | [Page list](receipts/pages.jsonl), [absence scope](receipts/raster_absence.json) |
| Transfer probe | PASS: 201,227,396 bytes / 427 pages in 31.384 s; probe directory deleted | [Timing](receipts/transfer_probe.json), [cleanup](receipts/probe_cleanup.log) |
| aarch64 detector imports and one page | PASS in shared `venv_l1`, no installs: 39 detector rows byte-equal to Mac | [Imports](receipts/venv_l1_imports.json), [comparison](receipts/detector_comparison.json) |
| Full 50-crop byte identity | **FAIL: 19/50 equal, 31/50 different**; discrete guard/match/pixel/component decisions agree for all 50 | [Comparison](receipts/mock_comparison.json), [Mac records](receipts/mock_mac_records.jsonl), [Clariden records](receipts/mock_remote_records.jsonl) |
| 1,000-crop rate and RSS | NOT RUN after failed byte gate; a 1,002-crop / 31-page selection was prepared locally but never transferred or executed | [Selection receipt](receipts/rate_selection_receipt.json) |

Only the v2 train and test import files are in scope. Dev was not included. Test is stored as `split=reserved` in its import; receipts call that population `test` and preserve `import_split=reserved`. Per-wave admitted split labels can differ from the v2 manifest assignments: the v2 imports define membership, while admitted files bind crop paths, rectangles and hashes. No codec-based exclusions were applied.

| Wave | Train | Test |
|---|---:|---:|
| cyrillic | 12,023 | 658 |
| mixed | 27,583 | 2,203 |
| openarchives | 19,625 | 4,680 |
| parliament | 64,521 | 11,942 |
| round1 | 46,964 | 8,115 |
| round2 | 18,782 | 3,689 |
| vouli | 24,938 | 1,742 |
| wikisource | 0 | 11,000 |
| Total | 214,436 | 44,029 |

Parliament accounts for 76,463 lines on 645 pages and remains unmasked with `skipped_wave=parliament`. It was excluded from the mock. The 4,940 non-parliament pages total 5,767,039,604 bytes (5.767 GB). The measured transfer rate was 6.412 MB/s including SSH/rsync startup: about 899.45 s (14.99 min) for those pages, or 2,521.68 s (42.03 min) for all 16.168 GB. These are transfer estimates, not a completed production transfer.

The default T6c2 detector is `greekocr.pages.process_page(native)` with `PageOptions()` (tables, orientation, joining and statistics disabled). It uses connected components and fitted curves, with no model weight files or model hashes. All 21 imported toolkit source files matched between hosts. Package versions and distribution `RECORD` hashes are retained in the [Mac stack receipt](receipts/detector_stack_mac.json) and the [Clariden import receipt](receipts/venv_l1_imports.json).

| Dependency | Mac | Clariden venv_l1 |
|---|---|---|
| numpy | 2.4.6 | 2.5.4 |
| Pillow | 12.3.0 | 12.3.0 |
| scipy | 1.17.1 | 1.17.1 |
| opencv-python-headless | 5.0.0.93 | 5.0.0.93 |

The mock reused the unchanged T6c2 `worker`, its nearest-curve matcher and candidate diagnostics, and the unchanged foreign-ink masker. [phase0_mask.py](phase0_mask.py) adapts input paths and source bindings and calls the T6b `guard_measure` helper with **original crop grayscale pixels <128** and proposed changed pixels. A fraction strictly greater than 0.30 restores the exact original bytes. Frozen evaluation/codec pins unrelated to this masking population were replaced with explicit masking source bindings; no masking or matching formula was rewritten. All 50 selections matched uniquely and none tripped the guard, so this sample does not exercise a positive guard or unmatched branch.

Seed `20261017` selected 50 crops on 50 distinct non-parliament pages: 8 cyrillic and 7 each from mixed, openarchives, round1, round2, vouli and wikisource. All 31 changed crops have differing encoded output hashes; all 19 unchanged crops retain identical original bytes. Both hosts independently rehashed all 50 originals and 50 outputs after the run ([Mac verification](receipts/mock_verify_mac.json), [Clariden verification](receipts/mock_verify.json)). Every mock record includes its actual host and frozen code tree SHA. The mask workers ran on `clariden-ln001` at nice 19 (the launcher was nice 15); Mac workers reported nice 5 after the sandbox rejected the requested increase.

The preserved [counterexample](receipts/byte_mismatch_witness/comparison.json), `10349bf796b8cd19c7415595-p000512-l0006`, has identical L-mode 731 × 48 decoded pixels and identical decompressed PNG scanlines. Its Mac PNG is 5,333 bytes (`0251fa4639517f7f88f7d4ceea43892d2dd57427a90ec19c982e093ad085827f`); the Clariden PNG is 5,723 bytes (`af0281e9e28d0cea7d0be1fcc71fa649788dfc884f6a73a1243139345a0fbaa8`). Their IDAT data differ. Pillow reports zlib `1.3.1.zlib-ng` on Mac and `1.2.13` in the remote venv ([remote encoding receipt](receipts/png_encoding.json), captured on `clariden-ln002`). This identifies a compression-byte difference in this witness; pixel identity does not relax the owner’s byte gate. No encoder change, dependency installation, venv copy, port or masking rerun was attempted.

The rejected mock took 222.814 s with two Clariden workers and maximum per-worker RSS 1,235,812,352 bytes (1.151 GiB). Mac took 226.752 s and peaked at 1,875,476,480 bytes per worker. These timings cover one selected crop per page and do not qualify the requested 1,000-crop throughput. No Slurm time limit was computed. The intended arithmetic, once qualified, would be `seconds = 258465 / measured_crops_per_second * 1.5`; no node scaling or production ETA is asserted here.

All remote writes stayed below `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/recut_1d_20261017/`. Existing crops, imports and venvs were read-only. The local main checkout, admitted files, rasters and page scan were read-only. Network use was limited to SSH/rsync through `clariden`; detector/masking calls denied network access.

The Phase 0 deploy consists of `W/code/greekocr/{__init__.py,pages/,glyphs/}`, the frozen T6c2/T6b/pilot runners and matcher/params under `W/code/docs/harvest/recut_v1/`, their `W/phase0/code.tar`, the audit scripts and input manifests under `W/phase0/`, and only the 50 selected rasters under `W/mock_pages/harvest_big/<wave>/...`. Rejected mock outputs and receipts are under `W/phase0/mock_50/`. The 200 MB `W/pages_probe/` directory was deleted. The complete [Phase 0 deployment/output ledger](receipts/PHASE0_DEPLOY_SHA256.txt) covers 372 files and was rechecked remotely. It is not a production deployment manifest.

`W/PHASE0_DEPLOY_SHA256.txt` SHA256: `3075914ef77ae69a83b76e6f0f5f020529d3b43e607aab70447e9f67f9c2f052`. Production `W/DEPLOY_SHA256.txt`, `W/pages/`, `W/out/`, `W/run_v2_mask.py`, `W/verify.py` and `W/mask_v2.sbatch` were not created. There is **no coordinator sbatch command** for this rejected deployment, and no test-only receipt: Phase 1 was not entered.

The local handoff contains the Phase 0 scripts, receipts and counterexample. Git metadata is read-only in this sandbox, so no worker commit was made. The exact hash-bound file list is [commit-inputs.json](commit-inputs.json); run `python3 -B docs/records/harvest/recut_v1/v2_clariden/guarded_commit.py` to check it, then the same command with `--commit` in a writable coordinator context. The helper checks HEAD, branch, the empty index, paths and every file hash, and never uses an alternate index or retries a failed Git write.

T6f: stopped at phase 0: byte-identity gate failed (31/50 SHA256 mismatches) | population: 214436/44029 lines, 5585 pages, 16.168 GB | detector on aarch64: ok | rate: not run | time limit: not set | mock 50: failed (19/50 byte-identical) | test-only: not run

T6f2: gate failed 19/50 | numpy pin: 2.4.6 | mock 50: 19/50 | pages uploaded: 0/0 GB | rate: not run | time limit: not set | test-only: not run
