# BIND1: sf7 release-binding script, executed only after the audit verdict (gpt-6.1-sol, medium, network OFF; no .git writes). WRITE + TEST ONLY.

Write `docs/records/reviews/harness/sf7_bind.sh` in the merge-script style: `set -euo pipefail`, `--dry-run` (default) / `--execute`, a log, no
push. Its input is the final audit verdict file written by `artifacts/sf7_rc1/audit/FINAL_SCORE.sh` (OC2); it reads the verdict and
branches.

**PASS** (line precision ≥ 83/100 with no PENDING lines, per SF7_PREREGISTRATION.md):
1. Set `status: bound` in `artifacts/sf7_rc1/RELEASE_RECEIPT.json` (train edits-only A, sha 1e3ac334…). Record the audit verdict sha
   and the time from `date` in Athens time.
2. If the test/dev counterpart exists (TR2 job output, release id `sf7_rc1_test_edits_A`, its RELEASE_RECEIPT), bind it the same way.
   If it is absent, train is bound alone and the test counterpart is recorded as pending.
3. Register both in the label-version registry, following the **edits-only registry pattern of `ru1_v3_edits`** (train and test
   counterparts). Find that registry in the wave-1c / greek-page-ocr worktrees, read-only, and name its path. Write the new entries as
   a PATCH FILE for the coordinator (`docs/records/labelfix/spellcheck/sf7_registry_entries.json`); never edit another worktree.
4. Write an LQB registration patch the same way, for the secondary lead.
5. Update `docs/records/labelfix/spellcheck/CORRECTION_STATUS_MARKS.md` with the sf7 row, the audit result and the release ids.
6. Write `docs/records/labelfix/spellcheck/SF7_BINDING.md`: the ids, shas, counts and the experiment-A switch-on handoff (version id + sha).

**FAIL:** set `status: rejected` with the reasons from the verdict. Nothing else changes. Write the SF7_BINDING.md stating so.

**PENDING:** refuse.

**Tests:** synthetic verdicts for PASS (with and without the test counterpart), FAIL and PENDING; a check that no file outside this
worktree is written; the no-push assertion.

Last line: `BIND1 READY: script <path>; tests <n> passed; registry pattern source <path>`.
