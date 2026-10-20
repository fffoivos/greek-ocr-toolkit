# SYNC1: bring opus/cleanup-1 and opus/r2-prep up to the merged opus/spellcheck (gpt-6.1-sol, medium, network OFF; Sol writes the script, the lead executes it)

**Context:** opus/spellcheck was merged at 960a70163 (docs/records/cleanup_20261017/MERGE_REPORT_20261017.md) and has docs commits after it.

**Lead ruling: MERGE, not rebase.** Commit shas on these branches are cited in reports and briefs (e.g. R2P f1610f2a2, R2CU d78b472b7,
CU3 7bc40ddc2, CU4 888c0d512), and a rebase would orphan them. opus/r2-cards is NOT included: Sol runs are active there. It gets a later
run with the same script.

Write `docs/records/reviews/harness/sync_20261017.sh`, in the same style as `merge_20261017.sh`:
- `set -euo pipefail`, error trap, timestamped log in the scratchpad, `--dry-run` (default) / `--execute`;
- no push, with a test asserting it; the git wrapper with hooks off.

**Per target** (`opus/cleanup-1` in `~/Projects/greek-ocr-toolkit-cleanup`; `opus/r2-prep` in `~/Projects/greek-ocr-toolkit-spellcheck-r2prep`):

1. **Preconditions:**
   - the tip equals a constant you read now;
   - the target worktree's tracked files are clean (untracked files are allowed and listed);
   - no Codex process with that cwd;
   - the opus/spellcheck tip equals a constant you read now.
2. **Merge:** `git -C <worktree> merge --no-ff --no-edit opus/spellcheck`.
   - First, predict conflicts read-only (`git merge-tree --write-tree`) and print them.
   - Any conflict ABORTS (`merge --abort`) unless it is on a path listed with an explicit per-path resolution in the script, with a
     reason. For each predicted conflict you resolve, state why.
3. **Untracked collisions:** if an untracked file would be overwritten, a byte-identical one is moved to
   `scratchpad/sync_untracked_backup/<branch>/`; a non-identical one aborts.
4. **Post-checks (abort on mismatch):**
   - the policy digest via `release_gate.policy_binding()` is 6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406;
   - the hashed-set diff vs opus/spellcheck is empty;
   - every commit of the old tip is an ancestor of the new tip;
   - the branch's own test dirs pass (cleanup-1: `tests/adjudicate tests/recogniser` plus whatever CU3/CU4 added; r2-prep:
     `tests/labelfix -k r2`). Then the full suite, with pre-existing failures only (the same known set as the merge script).
5. Print the new tip.

**Tests:** a synthetic temp-repo case for "conflict on an unlisted path aborts and leaves the worktree as before", `bash -n`, the
no-push assertion. Run `--dry-run` and put its output in `docs/records/reviews/harness/SYNC_NOTES.md`.

Last line: `SYNC1 READY: sync_20261017.sh <lines>; predicted conflicts cleanup-1 <n> r2-prep <n> (resolved by rule <n>); tests <n> passed; dry-run preconditions <ok|fail list>`.
