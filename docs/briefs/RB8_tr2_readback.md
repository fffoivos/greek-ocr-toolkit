# RB8: readback of TR2 job 3702849 (sf7-A test/dev counterpart) (gpt-6.1-sol, medium; network ON for Clariden only; no .git writes; no submission)

Package: `docs/labelfix/spellcheck/SF7_TEST_PACKAGE.md`. Root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019`,
outputs `output_3702849/`. Train-side pattern to copy: RB7 (`artifacts/sf7_rc1/build_rb7.py`, `validate_rb7.py`,
`output_3687228/READBACK_RECEIPT.json`) and the TR2 verifier `docs/labelfix/spellcheck/TR2_evidence/readback_dryrun.py`.

1. Cert check (`ssh clariden true`); on any auth error STOP. Never refresh the cert.
2. Job state and log: `sacct -j 3702849` and `logs/TR2_3702849.log`. If the state is not COMPLETED/0:0, read the log, report the failing
   stage and STOP (no resubmit, no fix).
3. Remote: verify every output against the job's own receipts (sha256), and the remote receipt's selection/parent/policy shas against
   the package (`f41e0563…` digest, prereg `64a84ed0…`, test parent `e7a4f402…`, dev parent `d462edac…`).
4. Pull ONLY the release files, receipts, job log and small summaries to `artifacts/sf7_rc1_test/output_3702849/` (Mac disk is tight;
   nothing over 200 MB in total; list what stays remote with its sha).
5. Independent local readback (the readback_dryrun.py method, at full scale): every edit's byte patch reconstructs forward and backward
   against the raw parent rows (read remotely or via a streamed extract, not a full download), coverage = selected ids, no unselected or
   duplicate ids, release id `sf7_rc1_test_edits_A`, parent `google_raw_v2_import`, status `candidate_pre_audit`, `bound: false`.
6. Write `artifacts/sf7_rc1_test/output_3702849/READBACK_RECEIPT.json` (rb7 schema) and
   `docs/labelfix/spellcheck/SF7_TEST_READBACK.md`: per split rows, edits, edits by kind (insert/delete/substitute per head), HOLD
   counts, comparison of edit rate per line with the train release (605 rows / 665 edits over its selection), runtime and GPU-h vs the
   40 min forecast, and the commit list for the lead.

No status change: sf7 stays candidate_pre_audit (the audit decides). Final line:
`RB8 DONE: job 3702849 COMPLETED; test rows a edits b; dev rows c edits d; readback ok` or `RB8 STOPPED: <reason>`.
