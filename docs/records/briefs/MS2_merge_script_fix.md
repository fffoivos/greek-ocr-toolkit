# MS2: fix merge_20261017.sh after its first --execute aborted (gpt-6.1-sol, medium, network OFF; no git writes by Sol)

**First execute:** log `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_20261017_20261017T093753Z_78890.log`,
stdout `…/scratchpad/merge_execute_stdout.txt`.

**What happened:** all preconditions passed, then the run aborted in the l1 docs-only step:
`git rm -- L1_DEPLOY_FILES.txt` failed with "the following file has changes staged in the index (use --cached … or -f)". The merge staged
these files as additions; the script must use `git rm -f --` (or `--cached` plus a filesystem delete) for paths staged by the in-progress
merge.

**State now:**
- opus/spellcheck is UNTOUCHED: tip 776b0a83d = the handoff commit.
- The scratch worktree `…/scratchpad/merge_rehearsal` is on a NEW branch `rehearsal/merge-final`, with an in-progress merge (index has
  many `A` entries).

Do (edit only `docs/records/reviews/harness/merge_20261017.sh`, its test and NOTES):
1. **Fix the l1 step**, and audit EVERY other `git rm` / `git checkout` in the script for the same staged-state problem; fix them all.
2. **Add a guarded `--reset-scratch` mode.** It aborts an in-progress merge in the SCRATCH worktree only, checks the scratch worktree
   out back to `rehearsal/merge-20261017` (a241ed75e), and deletes branch `rehearsal/merge-final` ONLY if it is not checked out anywhere
   and is not an ancestor of `opus/spellcheck`. It must refuse to touch the main worktree or any other branch. It logs like the main
   modes, and supports dry-run.
3. **Handoff check.** After the lead commits your fix, opus/spellcheck's tip will be a child of 776b0a83d. Make the check accept a tip
   whose commits since 16307355d touch ONLY the harness handoff files, verified byte-by-byte against the working tree, rather than one
   exact sha.
4. **Tests:** a synthetic temp repo that reproduces "staged addition then rm" and the reset mode; the no-push assertion; `bash -n`.
   Then run `--dry-run` (read-only) and include its output in NOTES.

Last line: `MS2 READY: rm fixes <n>; reset-scratch added; handoff check accepts harness-only children; tests <n> passed; dry-run preconditions <...>`.
