# BIND1 offline handoff

Prepared and tested only. The live receipts, correction status, registry entries and binding report have not been changed. No network or Git commands are used.

Run from any directory:

```bash
bash docs/records/reviews/harness/sf7_bind.sh /absolute/path/to/final_score.json
bash docs/records/reviews/harness/sf7_bind.sh --execute /absolute/path/to/final_score.json artifacts/sf7_rc1_test/output_JOB
python3 -B docs/records/reviews/harness/test_sf7_bind.py
```

The first command defaults to dry-run. The optional second positional argument is the locally read-back TR2 production output directory, containing `receipt.json`, `test/RELEASE_RECEIPT_test.json`, `dev/RELEASE_RECEIPT_dev.json` and their edits-only payloads. Default: `artifacts/sf7_rc1_test`. An absent directory means pending; a present but incomplete directory refuses the entire PASS operation. Remote receipt payload paths are deliberately replaced by verified local readback paths.

Input is the actual `final_score.json` schema written by `artifacts/sf7_rc1/audit/FINAL_SCORE.sh`: `summary`, 100 unique `lines`, and optional `heads`. Counts must agree with statuses. PASS requires at least 83 correct lines, zero pending lines or heads, passed reader controls and precision gate, a reported bootstrap interval, and `summary.full_preregistration_pass: true`. That last field must be resolved by the final audit owner after the separate sf6 line-class comparison. The current scorer leaves it null; the binder cannot infer that comparison from 83/100. Optional top-level `verdict` and `reasons` are checked for contradictions and preserved on rejection. A complete FAIL records the verdict reasons and gate failures in the train receipt and rejection report. PENDING or malformed input refuses before writes.

PASS writes coordinator patch `docs/records/labelfix/spellcheck/sf7_registry_entries.json` and secondary patch `docs/records/labelfix/spellcheck/sf7_lqb_registration.json`. Each is an envelope with `target`, `base_sha256`, `versions`, and `pending`; the lead checks the target SHA and merges only the `versions` map. These are reviewable registration proposals, not claims of applied registration. Registry entries preserve the sparse edits-only pattern and explicitly use the SF7 payload's actual `line_id`/`text` fields. The LQB entries declare exact raw-parent inheritance. Test/dev is a combined local reference file with its own SHA, both original split hashes, raw-parent sources, counts and receipts; it is never a training version.

Read-only pattern sources:

- `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1c/labels/VERSIONS.json`, entries `ru1_v3_edits` and `ru1_v3_test_edits`.
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/versions.json`, matching sparse overlay entries.

Successful plans and executions append `docs/records/reviews/harness/sf7_bind.log`; dry-run changes only this log. Refusals print `ABORT` to stderr before changing any file. Every planned destination is checked before the first write; symlinks, hardlinks, `.git` paths and paths outside the script's worktree are refused. Individual replacements are atomic, but a multi-file binding is not a filesystem transaction; review the log and rerun after an interrupted execution. No external registry is edited. No push or compute launch occurs.

Validation: 16 synthetic tests, including both PASS branches, FAIL scope, PENDING refusal, both dry-run branches, unresolved/failed line-class gate, contradictory PASS, duplicate audit IDs, tampered payload, incomplete/mock TR2, external destination/log symlinks, and forbidden command traps. A Python audit hook rejects every attempted filesystem write outside each rehearsal worktree; external registry hashes are checked after every test. `bash -n` passes. The tests rehearse on local copies and do not invoke the live binder.
