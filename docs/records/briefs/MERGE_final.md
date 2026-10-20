# MERGE: owner-approved real merge into opus/spellcheck (gpt-6.1-sol, medium, network OFF; git writes ALLOWED for this brief)

**Owner decision (via coordinator, 17 Oct):** the merge is APPROVED. Perform it into `opus/spellcheck` exactly per the decision sheet
(`docs/records/cleanup_20261017/CLEANUP_MERGE_REHEARSAL.md`, the top block: Option C, Option A dropped), after a fresh rehearsal, because branches have moved.
**NO push**, ever.

**Workspaces:**
- `~/Projects/greek-ocr-toolkit-spellcheck` (THIS, branch `opus/spellcheck`);
- the scratch worktree `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal`
  (branch `rehearsal/merge-20261017` at a241ed75e, which holds the reference result).

Git writes are allowed **only** for:
- branches `rehearsal/merge-final` (new) and `opus/spellcheck`;
- the scratch worktree.

**Never touch** any other branch, never use `git stash`, and never touch other worktrees. Sol runs are active in `-cleanup`, `-r2prep`
and `-r2cards`.

Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.

## 1. Fresh rehearsal: `rehearsal/merge-final` from the CURRENT `opus/spellcheck` tip (in the scratch worktree)

Sequence (decision sheet):
1. **merge `opus/spellcheck-r0`.**
2. **merge `opus/spellcheck-s8`:**
   - keep opus/spellcheck's `greekocr/labelfix/case.py` and `ink.py`;
   - S8b stays as `S8_DEV/s8b/detector.patch`;
   - add `docs/records/archive/s8_l1r3_hashed_paths_20261017.patch`, taken from the reference branch.
3. **merge `opus/spellcheck-l1f`:**
   - all policy-hashed paths resolve to opus/spellcheck's SF6c versions;
   - add `docs/records/archive/l1f_hashed_paths_20261017.patch` from the reference.
4. **merge `opus/spellcheck-l1` DOCS ONLY:**
   - its old package goes to `docs/records/archive/l1_20261017/` exactly as on the reference (the 6 scripts, sbatch, `test_l1.py`, the 3 root
     `L1_*.txt` receipts, its copies of the 3 hashed files, README);
   - the hashed files keep the SF6c versions.
5. **Fixtures commit:** `artifacts/labelfix_sf6/frozen_sf5_05f2dafb` and `artifacts/labelfix_l1e/fixture_v4`, byte-identical to the
   reference.
6. **Option C (WITHOUT Option A):**
   - `scripts/labelfix/clariden/l1r_recompose_ext.py`;
   - the L1R drivers/configs/tests pointing at it;
   - `tests/labelfix/test_policy_frozen_after_merge.py`;
   - all as in reference commit a241ed75e. Because Option A (698cdfa7) is NOT applied, nothing needs restoring from
     `docs/records/archive/l1r_line_20261017/`. That archive directory must not exist on the final branch.

## 2. Verify (all must hold, reported with evidence)

1. **Tree vs the reference branch.** `git diff a241ed75e rehearsal/merge-final --stat` may show ONLY:
   - (a) the docs commits made on opus/spellcheck after 291f581a: CLEANUP_MERGE_REHEARSAL*.md, SOL_ROUTING*, R2_evidence additions,
     print_truth README, briefs;
   - (b) the absence of `docs/records/archive/l1r_line_20261017/`.

   List every path and explain any other difference, or STOP.
2. **`git diff opus/spellcheck rehearsal/merge-final -- <all policy_binding sources>`** is empty, and `greekocr/` is byte-identical
   (sha list).
3. **`release_gate.policy_binding()`** = `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`.
4. **Full suite (`tests/`):** failures ONLY in the pre-existing environmental set (test_collection_outputs 3, test_provenance_cli_api 2,
   test_apply_clean 5 errors; the flaky test_deadline_terminates_inflight_pool may be re-run once); L1R tests pass;
   test_policy_frozen_after_merge passes.

## 3. Real merge

Fast-forward `opus/spellcheck` to `rehearsal/merge-final` in THIS worktree: `git merge --ff-only rehearsal/merge-final`.

**Untracked-file collision handling.** This worktree holds untracked copies of the fixture dirs and other artifacts. If the fast-forward
refuses because an untracked file would be overwritten:
- compare the bytes with the incoming tracked file;
- if identical, move the untracked copy to
  `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_untracked_backup/`
  (keep it; do not delete), and retry;
- if not identical, STOP and report.

After the fast-forward, re-run checks 2–4 in THIS worktree. Keep the reference and rehearsal branches.

## Report

`docs/records/cleanup_20261017/MERGE_REPORT_20261017.md`, committed on `opus/spellcheck`:
- sequence, conflicts and resolutions;
- the tree-vs-reference diff list;
- digest, greekocr identity, suite counts;
- the final `opus/spellcheck` sha;
- the untracked files moved, if any.

Last line:
`MERGE DONE: opus/spellcheck <sha>; digest 6f62925a yes; greekocr identical yes; suite <passed>/<pre-existing failures only>; l1r_line archive absent yes; no push`.
