# LQB5: finish truth v1.1 + scoreboard v2 (gpt-6.1-sol, medium, network OFF; no .git writes; NO browser or computer-use tools)

Continue LQB4 (`docs/records/labelfix/lqb/LQB4_PREFLIGHT.md`). Same worktree and constraints.

**DEV ruling (lead, from the spell-check lead's answer).**
- **Tier A:** two blind Opus readers + a third-reader tiebreak; controls 82/84 each with zero shared misses; source opus/spellcheck-s8
  `docs/records/labelfix/spellcheck/S8a6_DEV_TRUTH.md`.
- **Sample type:** the new type `weighted_stratified`.
  - The 600 lines are stratified by wave (receipt `docs/records/labelfix/spellcheck/S8_DEV/S8_DEV_receipt.json`).
  - The cards are all disagreement word groups plus 5% of the all-agree words per wave (S8a_REPORT.md).
  - A population rate is allowed ONLY as a weighted estimate using the S8a6 inverse card-inclusion × wave weights (read them from
    that worktree; never re-derive them), over the stated population: v2 train greek_poly, training wave.
  - Unweighted counts are printed as "on the sample".
  - Only the 976 resolved cards count. The 671 unadjudicated cards and the 2 UNKNOWN are excluded, and that is stated.
- **in-sample:** DEV is in-sample for S8b, and out-of-sample for the frozen sf6.

**Do.**
1. **Build** truth v1.1 (DEV + substitution60, as specified in LQB4) and freeze it with a sha.
2. **Re-score** all versions.
   - **Headline:** google_raw → sf6_release on DEV (weighted estimate, with a bootstrap over documents within waves), then audit100
     and substitution60 (decision audits).
3. **Baseline table ordering**, for every class:
   - FIRST, the measured rows: C1 card-level rates per stratum for marks, letters and crop (marks_y/n, letters_y/n), the locked
     strata, and DEV weighted;
   - THEN one collapsed line per class listing what is not measured.

   The per-head-direction marks rows show only where head-resolved truth exists (DEV, audit100, substitution60). Otherwise they fold
   into the collapsed line.
4. **Rebuild** `scoreboard.html` at the same path, under 14 MB, with a ≤4-sentence plain bottom line at the top, naming the marks
   change first. Write SCORE_v2.md as v2.2, the receipt and the tests.

**Last line:** `LQB5 READY: truth v1.1 <n> sha <hex8>; headline <one line>; baseline measured rows <n>; scoreboard <MB> MB; tests <n> passed`
