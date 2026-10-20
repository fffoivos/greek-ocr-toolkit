# LQB4: SX1 v2 extract + truth v1.1 (DEV, substitution60), rebuild scoreboard v2 (gpt-6.1-sol, medium, network OFF; no .git writes)

Continue LQB3 (`docs/records/labelfix/lqb/SCORE_v2.md`). Same worktree and constraints. **Do NOT launch any browser or computer-use tool.**

1. **sf6_release** now reads `~/Projects/greek-ocr-toolkit-spellcheck/artifacts/sx1/sf6_release_extract_lqb_v2.jsonl` (the
   ENSEMBLE_AB mode, which is the audited release mode).
   - Verify it against `RECEIPT_v2.json`, and check that audit100 shows 99/99 released.
   - If the check fails, stop and report.
   - Keep the v1 extract registered as `sf6_presence_full` for the record.
2. **truth v1.1.** Add these sets from the spell-check lead's `LQB_MARKS_INPUTS.md` (opus/spellcheck 33cacf520 or later):
   - **S8 DEV** (600 lines): sample_type uniform within the training wave, if its draw is documented as uniform; otherwise enriched.
     Out-of-sample for sf6; in-sample for S8b.
   - **substitution60:** decision_audit for sf6.

   Same record schema, tiers and conflict rules as truth v1. Write `truth_v1_1.jsonl` plus a manifest and a new sha. v1 stays
   frozen.

   List the new ids that need training exclusion in `truth_v1_1_exclusion_ids_new.txt`, leaving out any id that is already in a
   registered class (DEV is the registered class `eval_only_dev`). The lead sends that file to the sourcing lead.
3. **Re-score** every version on truth v1.1 and rebuild `scoreboard.html` at the same path, layout as in LQB3.
   - **Headline:** the marks delta google_raw → sf6_release on the out-of-sample uniform sets first (DEV, if uniform), then the
     decision audits (audit100, substitution60), each labelled with its sample type.
   - Keep the page under 14 MB.
   - Write SCORE_v2.md as v2.1, the receipt and the tests.

**Last line:** `LQB4 READY: sx1 v2 verified <ok> (audit100 released 99/99); truth v1.1 <n> items sha <hex8> (+DEV <n>, +sub60 <n>; exclusion-new <n>); headline <one line>; scoreboard <MB> MB; tests <n> passed`
