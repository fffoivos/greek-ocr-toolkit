# MS3: merge script, accept the merge-brief commits in the handoff (gpt-6.1-sol, medium, network OFF; no git writes)

Your MS2 work (uncommitted script/test/NOTES edits) is in place; keep it.

The live history after the handoff base contains the lead's brief commit `6966d77a9` (`docs/records/briefs/MS2_merge_script_fix.md`). This file
(`docs/records/briefs/MS3_handoff_paths.md`) will be committed together with your edits. Change the script so that:
1. The handoff's allowed paths = the 6 harness files + `docs/records/briefs/MS2_merge_script_fix.md` + `docs/records/briefs/MS3_handoff_paths.md`.
   - Every commit since base 16307355d may only Add/Modify paths in that set.
   - The net delta must be exactly those paths, as additions.
   - Harness files are byte-checked against the working tree, as now.
2. The post-merge tree allowlist vs reference a241ed75e includes the same 8 paths. The 6 harness files may already be in it; check.
3. Tests are updated, including one where a non-allowed path in a later commit is still rejected.

Run `--dry-run`. With your edits still uncommitted, the remaining failures should only be "uncommitted edits", "aborted scratch merge"
(fixed by `--reset-scratch`, which the lead runs) and the Codex guard (your own process). Say exactly which.

Last line: `MS3 READY: handoff paths 8; tests <n> passed; dry-run remaining failures <list>`.
