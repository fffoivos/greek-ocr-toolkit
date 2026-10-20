# SYNC3: make sync_20261017.sh resumable after its first execute (gpt-6.1-sol, medium, network OFF; no git writes)

The first `--execute` of the untracked `docs/records/reviews/harness/sync_20261017.sh` stopped as follows:
- **opus/cleanup-1:** the merge committed (b4234ee0e). The suite then had one new failure, the over-broad frozen-greekocr test. SYNC2
  fixed it with a new commit on cleanup-1, which is now its tip (read it).
- **opus/r2-prep:** not reached (still d78b472b7).

The log is the latest `sync_20261017_*.log` in the scratchpad, and stdout is in `scratchpad/sync_execute_stdout.txt`.

Change the script (and its test/NOTES) so that:
1. **Per target, an "already synced" state is accepted.** If SOURCE_TIP is an ancestor of the target tip, skip the merge and run the
   post-checks only.
   - The target tip constant for cleanup-1 becomes its current tip.
   - Assert that the commits since b4234ee0e touch only `tests/labelfix/test_policy_frozen_after_merge.py` and
     `docs/records/reviews/harness/SYNC2_NOTES.md`.
2. **SOURCE_TIP is unchanged** (ac35c174b). The opus/spellcheck tip may be a descendant whose extra commits touch only
   `docs/records/briefs/SYNC3_resume.md`. The lead will NOT commit anything else to opus/spellcheck before executing.
3. **The suite parser accepts the known pre-existing set only, as before.** Sandbox socket errors are a sandbox artefact; the lead runs
   the script outside the sandbox, so do not add them to the known set.
4. **Tests:** a synthetic case for "already synced → post-checks only". Then `--dry-run` (expected: both targets PASS preconditions,
   with cleanup-1 as "already synced").

Last line: `SYNC3 READY: resumable yes; tests <n> passed; dry-run <ok|fail list>`.
