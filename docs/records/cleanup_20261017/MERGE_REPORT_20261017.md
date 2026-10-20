# Merge report, 17 Oct 2026: spell-check branches into opus/spellcheck (owner-approved)

**Final `opus/spellcheck` = `960a701639e9f50c55df44a54e59fcbcfc381b73`. No push.**

**Method (owner choice + coordinator form (b)):**
- Sol wrote `docs/records/reviews/harness/merge_20261017.sh` (briefs MS, MS2, MS3, MS4).
- The lead executed it verbatim, with `--dry-run` before each `--execute` and `--reset-scratch` between attempts.
- No hand-typed git.

## Sequence (decision sheet, Option C, Option A dropped)

| Commit | Step |
|---|---|
| fbb2098ad | merge r0: adjudicated docs |
| 54315f561 | merge s8: case.py/ink.py kept SF6c-frozen; S8b candidate archived as a patch |
| 35d6c341a | merge l1f: policy-hashed paths kept SF6c; l1f hashed edits archived as a patch |
| 0fa4f415a | merge l1, docs only: the v0 package archived verbatim under docs/records/archive/l1_20261017/ |
| d5cfa8adb | fixtures: exact reference bytes |
| 960a70163 | Option C: the non-hashed `l1r_recompose_ext.py` and its consumers; no Option-A archive |

## Checks (abort-on-mismatch, run by the script)

| Check | Result |
|---|---|
| Handoff history | Only the harness and merge-brief paths; exact working-tree bytes |
| Branch tips | Equal to the constants |
| Worktrees | Clean |
| Codex writer guard | Passed |
| Delta vs reference a241ed75e | Equals the literal allowlist; the Option-A archive is absent from the git tree |
| Hashed-set diff vs opus/spellcheck | Empty |
| `policy_binding()` | 6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406 |
| `greekocr/` sha list | Identical |

**Full suite**, run twice: in the scratch worktree before the fast-forward, and in the main worktree after it.
- Result: **4,809 passed, 19 skipped, 5 failed, 5 errors**.
- The failures and errors are exactly the known pre-existing environmental set: test_collection_outputs 3, test_provenance_cli_api 2,
  test_apply_clean 5 errors.

**Fast-forward:** 54 untracked files in the main worktree were byte-IDENTICAL to incoming tracked files (the fixture copies). They
were moved to `scratchpad/merge_untracked_backup/` (kept) before `git merge --ff-only`.

## Attempts (receipts under docs/records/reviews/harness/merge_logs/)

1. **`execute1_abort_staged_rm.log`:** aborted in the l1 step because `git rm` hit staged additions. Fixed by MS2 (`git rm -f`),
   which also added `--reset-scratch`.
2. **`execute2_abort_fs_check.log`:** every merge step committed, then an abort because a filesystem existence check found EMPTY
   leftover directories. Fixed by MS4 (git-tree check; the reset removes empty dirs).
3. **`execute3_success.log`:** complete. The final SHA is above.

opus/spellcheck was never modified by the aborted attempts. They only touched the scratch worktree and branch `rehearsal/merge-final`,
which the guarded reset removed.

## Next (owner-approved, Sol-only)

- Rebase `opus/cleanup-1`, `opus/r2-prep` and `opus/r2-cards` onto 960a70163 when their Sol runs are idle.
- Stale worktree removals per the deletion sheet (git worktree remove after an untracked-file listing; r1 stays blocked by the
  m2_run.py path).
