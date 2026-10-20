# REL3 package handoff

Package target: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v3/pkg/59d2de21`. Package identity `59d2de211ef8864df7517f9cba1d986a773bccb07ba3017561047700222ed148` is the SHA256 of the ordered seven-file core manifest (code, verifier, wrappers, inputs binding and tests); DEPLOY_SHA256SUMS separately binds every deployed payload file. No production export has run. The coordinator alone submits.

See INVENTORY.md for label formation, raw import semantics, existing named versions and provenance. Six versions are registered: cyrillic_0.3, numerics_0.3, content_repair_0.2, composer_0.3, ru1_v3_edits, n1_v1_w1. External overlays are registered, not applied. SF7 remains unregistered pending audit.

## Exclusions and receipts

Stream admitted_train, select the two exact W1/W2 parents, verify ADMIT/train and decision identity, join book to SPLIT2 edition and check census edition_id. Count dev/test-edition and benchmark-key exclusions, then require both counts zero; any nonzero count fails the attempt. Exact benchmark pixel duplicates are dropped and counted. Missing manifest matches, missing images, wrong sizes or nonmatching crop bytes are dropped and counted. Successful release requires at least one fully backed row. All counts include explicit zeros and source/edition release totals.

Only changed admitted labels enter release_v3_edits.jsonl. Recorded merged edits, full routes, toolchain and separate normalization are retained. Unknown edit provenance or a failure to reconstruct the label aborts. The batch job streams admission_records to reconcile every release decision by hash and key. A success receipt is written last; failed attempts retain FAILED.json and must never be consumed. Existing attempt paths are refused.

Job input hashes cover both multi-GB files before and after streaming, small input files, census CURRENT/summary/readout chain and both completed CROPS4 receipt chains. Original census files are referenced by path and SHA, never copied. The output receipt hashes the three payloads; its own hash can be recorded by the consumer after completion.

## Resource arithmetic

Measured synthetic run: 1505 rows, 62,201,734 input bytes, 0.234700 seconds = 265.03 MB/s, process peak 213.0 MiB including synthetic fixture construction. This is a throughput model, not a Clariden production timing measurement. Production census inputs total 7,870,677,512 + 10,412,166,460 = 18,282,843,972 bytes. Baseline 18,282,843,972 / 265026561.40 = 68.98 s; 20× allowance + 300 s for crop metadata/reads = 1,679.70 s (28.0 min), rounded to 30 min on normal, one node, one CPU, 8 GiB. The measured run includes both input hash passes, parse/reconcile, image reads and output writes.

Memory stores compact crop identities/paths and selected key/decision hashes, no corpus payloads. Conservative planning: 320,479 crop keys × 2 KiB + 168,637 selected keys × 1 KiB + 223 MB measured baseline, with 4× headroom, is below 8 GiB. Actual release count and time remain unknown until the coordinator runs it. No OCR, image regeneration, GPU stage or training occurs in this package.

## Coordinator commands

Run on Clariden after the full CROPS4 receipts finish:

```bash
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v3/pkg/59d2de21
bash "$ROOT/VERIFY.sh" package
bash "$ROOT/VERIFY.sh" inputs
bash "$ROOT/submit_release_v3.sh" rel3_c05_full_01
```

The final command submits exactly one normal-partition batch job and refuses failed/pending input verification or an existing output attempt. Absolute Slurm log: `$W/release_v3/rel3-rel3_c05_full_01-%j.log`. Absolute builder output: `$W/release_v3/rel3_c05_full_01/`. This command block is a handoff, not an execution record.

## Verification and pending work

Local: 12 synthetic tests passed; all shell scripts parsed. Production verification uses the pinned venv_l1 Python. Package mode checks every listed payload SHA and parses Python/shell source. Inputs mode hashes only files under 64 MiB, checks big-file existence/size, and inspects full CROPS4 receipt status without parsing or hashing big census files. Exit 2 means pending crops; other failures are hard errors.

Expected light-input denominator: 28; currently 26 pinned files/paths plus two pending CROPS4 receipts. The final deployment readback and actual verification results are reported in the response and local DEPLOY_READBACK.json (kept outside the immutable deployed manifest).

Pending: W1_CROPS4_receipt, W2_CROPS4_receipt; SF7 audit/registration for a future package revision; coordinator submission and production counts/output SHAs. No output population or admission count is claimed from synthetic tests. No jobs were submitted, no spend, no git add/commit. Existing dirty worktree files and seal02/bench02 were not modified.

Guarded commit list: COMMIT_LIST.json and guard_commit.py. Run `python3 -B guard_commit.py` in this package to validate and print its exact allowlist. No Git action is performed by that guard.
