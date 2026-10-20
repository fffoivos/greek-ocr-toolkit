# CQ4e: diagnose the 15 VOID contexts of the CQ4 read (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs)

The lead ran `RUN_ALL.sh`, then BUILD_REREAD, the re-read and AGGREGATE (18 Oct 07:02–07:44).
- **Initial ledger** (`artifacts/cq4/initial_ledger.json`): 18 contexts, **15 VOID** ("reader/closure leak scan failed") and 3 VALID.
- **Aggregate:** W-CAP 0/300 resolved; top-up 211 resolved (84 marked / 127 bare); re-read agreement 79/83; lead queue 1,294.
- The earlier all-VOID CQ4d attempt (a nested reader without network) is archived in `artifacts/cq4/void_attempt_cq4d/`. Do not use it.

**Do, read-only:**
1. For every VOID context, re-run the canonical scanner v4.4 (copy sha dd2fc59d…) on its rollout (the path is in the ledger `run`), plus
   the closure/manifest check, exactly as `tools/workflow.py` does.
2. Tabulate the violations by class: absolute path, template, image provenance, manifest (extra or changed files), forbidden names,
   other. Give 3 literal examples per class with record numbers.
3. **Verdict per class:**
   - (a) **A genuine leak risk:** the reader read or wrote outside its folder, or touched a key or truth path.
   - (b) **A scanner/closure false positive:** list the pattern. If it is closure-side, e.g. the CQ4d control swap changed items but a
     manifest or frozen list wasn't updated, say exactly which.
   - (c) **A reader behaviour** that is harmless but rule-violating, e.g. writing outside `answers.jsonl` / `zoom/`.
4. **Recommendation:**
   - for (b) closure/manifest bugs: the fix to the build, with a test;
   - for scanner patterns: the minimal canonical-scanner change to propose to the coordinator (do NOT edit the canonical scanner);
   - for (a) or (c): a fresh re-read in new reader folders, with the prompt verbatim.

Write `docs/records/labelfix/spellcheck/R2/CQ4E_VOIDS.md` + `artifacts/cq4/void_diagnosis.json`.

Last line: `CQ4e READY: VOID 15 → classes {<class>: <n>}; genuine leaks <n>; closure bugs <n>; scanner false positives <n>; recommendation <...>`.
