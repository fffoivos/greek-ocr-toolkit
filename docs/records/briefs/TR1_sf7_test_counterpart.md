# TR1: a test/dev counterpart of the sf7-rc1 variant-A release (gpt-6.1-sol, medium; network ON for Clariden only; no .git writes; NEVER submit)

**Coordinator (18 Oct):** wave 1c's marks arm needs corrected v2_test AND dev labels for the polytonic classes. Without them its verdict
is uninterpretable. Use the same variant A policy (sf7, digest f41e0563…, package opus/spellcheck 69a00ca13) as the train release
`artifacts/sf7_rc1/release_edits_only_A.jsonl` (RELEASE_RECEIPT.json). Nothing binds before the audit.

**MAC DISK IS CRITICAL (about 7 GB free; the watchdog trips at 10 GB).**
- Keep all large data on Clariden. Pull back ONLY the final edits-only files, receipts and logs (MB-scale).
- Never pull tarballs or full overlays.
- Delete your own temporary local copies once their sha is recorded.

## 1. Find out (read-only) whether L1-era saved outputs exist for v2_test and dev

The outputs needed are the reader A/B, S6 detector and recogniser alignments/scores for the polytonic test/dev lines. Check the L1/L1R3
roots on Clariden (`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/...`, `labelfix_r1_20261016/...`) and the selection
binding.
- Report which test/dev lines are polytonic-eligible.
- Identify the v2_test and dev raw Google import files (the train parent is
  `greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`; find the test/dev siblings and name their paths and shas).

## 2a. If the outputs exist

Build a recompose package (the GC1 pattern; the same sf7 code with variant A) over the test/dev selection. That means:
- the mock;
- a real-input login-node dry run;
- deploy to a new root `…/labelfix_sf7_test_20261018` with remote sha checks;
- `sbatch --test-only`;
- `LEAD_COMMIT_PATHS.txt` and `VERIFY_CMD.sh`.

The edits-only conversion (the RB7 converter, with parent = the matching raw import, release id `sf7_rc1_test_edits_A`, separate files for
test and dev) is written now, and runs after the job.

## 2b. If they do not exist

Do NOT run anything. Estimate the inference needed (recogniser + detector + reader A/B on the test/dev polytonic lines):
- line counts;
- the GPU/CPU-hours from L1-era receipts;
- the job wall time and partition;
- the Codex cost of building it.

Write the plan as a package outline, so the coordinator can decide.

## Report

`docs/records/labelfix/spellcheck/SF7_TEST_COUNTERPART.md`.

Last line: `TR1 READY: saved outputs <exist|missing>; test lines <n> dev lines <n>; <package deployed root … test-only ok | estimate: … GPU-h, … min wall, Codex ~… pts>`.
