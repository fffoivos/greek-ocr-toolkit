# MS4: merge script, make the Option-A check git-tree based; reset removes empty leftover dirs (gpt-6.1-sol, medium, network OFF; no git writes)

Second `--execute` log: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_20261017_20261017T094356Z_85494.log`.

- **Outcome:** all six merge steps committed on `rehearsal/merge-final` (68dff5d81 … 5454ed7a7). The reference-delta allowlist check
  (line 378) passed. Then line 379 aborted: "Option-A archive exists".
- **Cause:** `[[ -e $SCRATCH/docs/archive/l1r_line_20261017 ]]` tests the FILESYSTEM. The scratch worktree has only EMPTY leftover
  directories there (config/, tests/labelfix/, scripts/labelfix/clariden/), which git does not track. No commit on the branch contains the
  path: `git ls-tree` gives 0 entries for all six commits. opus/spellcheck is untouched (tip 77e4ab160).

Do (edit only the script, test and NOTES):
1. **Base the check on the git tree:** `git ls-tree -r --name-only $FINAL -- docs/records/archive/l1r_line_20261017` must be empty. Audit any other
   filesystem-based existence checks the same way.
2. **Extend `--reset-scratch`** to also remove EMPTY directories left under the scratch worktree after the checkout. Use `find … -type d
   -empty -delete`, scoped to the scratch worktree only, and never a non-empty directory. Log each one removed.
3. **Handoff paths** gain `docs/records/briefs/MS4_tree_check.md` (9 paths). The lead commits it with your edits.
4. **Tests:** an empty-leftover-dir case (passes); a tracked file under the archive (still aborts).

Run `--dry-run`. The expected remaining failures are "uncommitted edits", "final branch exists" (the lead runs `--reset-scratch` first)
and the Codex guard (your own process).

Last line: `MS4 READY: tree-based checks <n>; reset removes empty dirs; handoff paths 9; tests <n> passed; dry-run remaining failures <list>`.
