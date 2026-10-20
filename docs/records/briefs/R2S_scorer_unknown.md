# R2S: four-head scorer, inserted prediction slots are UNKNOWN, not "unmarked" (gpt-6.1-sol, medium, network OFF; no .git writes)

Workspace: THIS worktree (`opus/r2-prep`, tip d891bcaa3). Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.
Never touch `greekocr/labelfix` or the 16 policy paths; digest 6f62925a stays.

**Defect** (lead diagnosis, recorded in `docs/records/labelfix/spellcheck/R2/R2_JOB1_DIGEST.md`):
- `scripts/labelfix/r2_score.py` `union_records` gives "inserted prediction" slots truth none ([0]*4) by default. These are recogniser
  letters with no frozen physical truth slot: 1,334 slots in job 1.
- So every mark predicted on them counts as a false positive: 406 of A16's 452 four-head FPs.
- The design review requires uncovered regions to be UNKNOWN (ASTRA-R2design §5).
- The continuity scorer (`r1_score.map_lines`) already leaves them unscored.

Do:
1. **Fix:** inserted slots get truth UNKNOWN, excluded from numerator and denominator on every head, like the existing 924 print-truth
   None slots.
   - Report them separately per arm as a diagnostic: `inserted_slots`, `inserted_slots_marked` (by head and letter).
   - Do NOT count them as errors anywhere.
   - Deletion-side cases are unaffected: a truth slot with no prediction still scores as now. Confirm this with a test.
2. **Tests:**
   - a synthetic line with an inserted marked slot gives no FP, appears in the diagnostic, and leaves P/R unchanged;
   - the existing r2_score tests still pass, or each changed expectation is listed with its reason.
3. **Rescore job 1** from the saved scorer inputs (`artifacts/labelfix_r2/scorer_inputs/`, readback 3681404) for A16, s17 and s18,
   with overlay v1.1 as before.
   - Write the new table to `docs/records/labelfix/spellcheck/R2/evidence/job1/scores_r2s.json`, keeping `scores.json` unchanged.
   - Add a short "R2S rescore" section to `R2_JOB1_DIGEST.md`: old vs new four-head P/R/F1 per arm, and matched-slot FP (expected
     about 46/44/49).
   - The seed comparison (BASE vs A) must not change sign. If it does, say so first.
4. **Make the deploy manifest carry the new `r2_score.py` hash.** List the manifest files you changed; the R2a + DEV package redeploys
   them, and nothing is deployed now.

Last line: `R2S READY: inserted slots UNKNOWN; four-head P A16 <old>→<new>, s17 <..>, s18 <..>; matched FP <a>/<b>/<c>; tests <n> passed`.
