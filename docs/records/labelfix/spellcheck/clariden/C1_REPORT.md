C1 job 3678590; state: COMPLETED; exit code: 0:0

Selection: 91,469 lines = all 61,469 compound-bearing Greek-poly training lines + 30,000 of the 63,200 other Greek-poly lines (seed 20261016). Test IDs/crops and all non-dev Wikisource books are excluded; no eligible training rows overlap.

Mock: 192 crops (32 existing test-cache records for parity only, 160 selected training crops). Mock outputs are separate from the training alignment artifact.

Clariden: E3 scratch `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`; existing venv `torch 2.11.0+cu128`. Live debug limit 01:30:00, MaxNodes=4, debug-qos MaxJobsPU=1. C1 request: debug, a0140, one node, 01:00:00. No environment installation or credential refresh.

Text-only helper check: extracted unchanged pair_tokens/align_chars and mark_class agree with direct imports on 24 token-pair cases and all 12 compound classes. This avoids importing the optional SciPy image stack on Clariden.

Mock completed: 192/192 aligned, zero failures, 37.827 seconds on CPU. All 32 overlapping cache records match exactly, including confidence and spans. The initial worktree-root attempt aligned the same 32 parity crops but reported 160 missing paths; the final script uses an explicit read-only canonical crop root. Only 192 distinct crops were decoded across both attempts.

Deployment gate passed: 18 files matched SHA-256, as did both checkpoint artifacts and the reused E3 runtime. See `C1_DEPLOY_SHA256.txt`, `C1_CHECKPOINT_SHA256.txt`, and `C1_remote_sha256_and_limits.txt`. The remote E3 train JSONL also matches the local input SHA-256.

Scheduler test 2026-10-16T20:58:46.409560+03:00: `sbatch --test-only --parsable scripts/labelfix/clariden/c1_job.sbatch` rejected with `QOSMaxSubmitJobPerUserLimit`. No C1 allocation was submitted or consumed. Live debug-qos: MaxJobsPU=1, MaxSubmitPU=2; existing debug jobs 3678511 and 3678584 occupy both submission slots and wait on E4 dependencies. They are outside C1 and were left untouched. See `C1_sbatch_test_only.txt`.

Submitted 2026-10-16T21:00:43.964504+03:00: job **3678590**. The final scheduler test passed after an E4 slot was released externally. Crop inventory: 91,469/91,469 present, zero missing, 3,293,623,314 bytes; every reused crop SHA-256 is in `C1_inventory/C1_crop_inventory.jsonl.gz`. No crops or checkpoint bytes were transferred.

Initial audit: RUNNING, node nid006588, partition debug, account a0140, NumNodes=1, AllocTRES includes 4 GPUs, TimeLimit=01:00:00. The log did not yet exist during the 3-second prologue audit; this was a readback race, not a job failure.

## Final outcome

`sacct` confirms **COMPLETED**, exit **0:0**, **00:01:43** (103 seconds, 1.72 minutes), 2026-10-16 **20:00:44–20:02:27 Europe/Zurich**. The Python step took 94 seconds; the runner measured 93.241 seconds. Exactly **one debug job** was submitted; no resubmission was needed. One node (`nid006588`), four GH200 GPUs, account `a0140`, requested wall time 01:00:00. No other jobs were changed.

**91,469 selected / 91,469 aligned / 0 failures**. The full 202-line job log was read: all 180 worker progress records report zero failures, and it ends with `C1_ALIGNMENT_DONE`. The terminal accounting and post-run code/checkpoint hash checks are in [C1_terminal_sacct_and_sha256.txt](C1_terminal_sacct_and_sha256.txt); the full log is [C1_3678590.log](C1_3678590.log).

## Agreement counts

The unchanged `candidates.pair_tokens` function pairs Google and recogniser words. A word contributes only when its nonempty NFD core matches exactly, with case and marks preserved; edge punctuation is excluded by the existing tokenizer. Count breathing+accent clusters on Greek vowels, with optional subscript, using the unchanged `markshape.mark_class` function. **729,125 agreeing word occurrences contain 82,946 compound-cluster occurrences.** These are available label occurrences before ink localisation/filtering, not fitted classifier samples. No model was trained or evaluated.

| Compound class | In selected Google labels | Among agreeing words |
|---|---:|---:|
| psili+acute | 36,868 | 34,343 |
| psili+acute+subscript | 33 | 8 |
| psili+grave | 5,534 | 5,085 |
| psili+grave+subscript | 0 | 0 |
| psili+circumflex | 14,664 | 13,537 |
| psili+circumflex+subscript | 15 | 5 |
| dasia+acute | 28,104 | 26,360 |
| dasia+acute+subscript | 12 | 7 |
| dasia+grave | 1,364 | 1,098 |
| dasia+grave+subscript | 0 | 0 |
| dasia+circumflex | 2,838 | 2,285 |
| dasia+circumflex+subscript | 291 | 218 |

The two grave-plus-subscript classes have zero occurrences in the selected Google labels as well as the agreeing words. Several other subscript classes remain small; C1 does not apply any ink-quality or fitting threshold.

## Output and verification

- [C1_alignments.jsonl.gz](C1_alignments.jsonl.gz): **69,015,388 bytes** (69.02 MB / 65.82 MiB), copied from Clariden with `rsync --checksum` and SHA-256 verified locally.
- Output SHA-256: `951122655bd25af553f48951af986bcd2be4f3a57f184beaf2a5923de08bb398`.
- [C1_manifest.json](C1_manifest.json) binds the job, selection, checkpoint, counts, output path/size/hash, mock result and structural validation. Per-worker and runner receipts are in [C1_job_metadata/summary.json](C1_job_metadata/summary.json).
- [C1_output_validation.json](C1_output_validation.json): all **91,469 unique crop keys**, exact selected-set coverage, no missing/extra/duplicate crops, **5,725,124 character spans**, prediction equals concatenated span atoms, valid frame bounds/schema/scales/confidences, and valid gzip CRC. This was a remote metadata-only pass, with no image or model processing; its exact source and enforced source hash are retained beside the receipt.
- Each output record is `{"crop": "docs/records/harvest/...", "alignment": <Alignment.to_record()>, "prediction": <same prediction>}`. Crop keys start at `docs/harvest/` for portability. All nested alignment fields follow the existing cache format. Output order is deterministic within four worker shards; consumers join by crop key, not row position.
- The successful CPU mock aligned **192/192**, with **32/32 cached alignment payloads exactly equal**, including confidence, frames and rounded coordinates. The comparison normalises only the absolute cache crop prefix to `docs/harvest/`; the new top-level prediction field duplicates `alignment.prediction`. See [C1_mock_mock_cache_diff.json](C1_mock_mock_cache_diff.json) and [C1_mock_summary.json](C1_mock_summary.json). Its 32 instrument crops were used only for parity and are absent from the training selection and final output.
- All local frozen code, original Google source JSONLs, and the original 1,264-record test alignment cache were re-hashed unchanged; see [C1_local_revalidation.json](C1_local_revalidation.json). No tracked source files or test instruments were changed. All C1 additions remain uncommitted in this worktree.

## Bound inputs

- Selection: [C1_selection.jsonl](C1_selection.jsonl), SHA-256 `bd0f740258bcf64688323d3a79eb8f1ee78518bc7a8c2a491adc7766dd8adbc3`. All 61,469 compound-bearing lines plus a seed-20261016 sample of 30,000/63,200 other Greek-poly lines. [C1_selection.summary.json](C1_selection.summary.json) records source hashes, exclusions, held-out book identities and wave counts. No train ID/crop intersects v2 test; no held-out Wikisource book is included.
- E3 `full_s0` `best.pt`: SHA-256 `5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663`.
- Actual safe-loader weights, existing `best.safetensors`: SHA-256 `e468155d6130be4b7359d94ec197a357ad55b0dc7947104afc1336c352a6c6df`.
- All **18 deployed source/selection files** matched local SHA-256 before submission, were checked again in the job prologue, and remained unchanged afterward. See [C1_DEPLOY_SHA256.txt](C1_DEPLOY_SHA256.txt), [C1_CHECKPOINT_SHA256.txt](C1_CHECKPOINT_SHA256.txt), [C1_remote_sha256_and_limits.txt](C1_remote_sha256_and_limits.txt), and [C1_sbatch_test_only_passed.txt](C1_sbatch_test_only_passed.txt). Deployed scripts were never edited.
- All **91,469 E3-staged crops** were present: **3,293,623,314 bytes**, zero missing. [C1_inventory/summary.json](C1_inventory/summary.json) and [C1_inventory/C1_crop_inventory.jsonl.gz](C1_inventory/C1_crop_inventory.jsonl.gz) bind every selected crop by path, size and SHA-256. No crops or checkpoint data were copied to Clariden.
- Environment reused unchanged: E3 `runtime.sh`, `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python`, torch `2.11.0+cu128`, aarch64. The text-only functions were loaded from the hashed unchanged source definitions to avoid importing the optional SciPy ink stack. No environment was created or packages installed; no certificate was refreshed.

C1 RESULT: job 3678590 COMPLETED, 91469 lines aligned in 1.72 min; agreeing compound clusters by class: psili+acute=34343, psili+acute+subscript=8, psili+grave=5085, psili+grave+subscript=0, psili+circumflex=13537, psili+circumflex+subscript=5, dasia+acute=26360, dasia+acute+subscript=7, dasia+grave=1098, dasia+grave+subscript=0, dasia+circumflex=2285, dasia+circumflex+subscript=218; output docs/records/labelfix/spellcheck/clariden/C1_alignments.jsonl.gz (69015388 bytes)
