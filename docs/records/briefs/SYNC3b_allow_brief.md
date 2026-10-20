# SYNC3b: one path missing from the cleanup-1 post-merge allowlist (gpt-6.1-sol, medium, network OFF; no git writes)

The SYNC3 dry-run failed on opus/cleanup-1 with "unapproved committed path". My SYNC3 brief left out the lead's brief file
`docs/records/briefs/SYNC2_policy_test.md`, which edf9c8786 committed after b4234ee0e.
- Add it to the cleanup-1 allowlist (exactly 3 paths: that brief, `docs/records/reviews/harness/SYNC2_NOTES.md`,
  `tests/labelfix/test_policy_frozen_after_merge.py`).
- Add `docs/records/briefs/SYNC3b_allow_brief.md` to the opus/spellcheck allowed-descendant paths.
- Update the test.
- Run `--dry-run`.

Last line: `SYNC3b READY: tests <n> passed; dry-run <ok|fail list>`.
