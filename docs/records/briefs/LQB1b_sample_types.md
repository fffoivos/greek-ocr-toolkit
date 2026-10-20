# LQB1b: sample-type honesty + letters truth check (gpt-6.1-sol, medium, network OFF; no .git writes; no reading)

Continue LQB1 (`docs/records/labelfix/lqb/SCORE_v1.md`). Same worktree and constraints. Keep every temporary write inside this worktree
(pytest `--basetemp` in-worktree, no `/private/tmp`).

**Lead review findings.**
1. **Rates from selected samples.** The headline rates mix in samples that were not drawn at random:
   - N1 truth is the approved controls plus lead-ruled raised cells: enriched;
   - the RU1 audit was drawn FROM ru1_v1's own decisions (30 edits + 10 keeps). It measures the precision of those decisions, not a
     population error rate;
   - the yer adjudication cards are a C1 uniform draw: population-like within its stratum.

   **Do:** add a `sample_type` to every truth set: `uniform` (a seeded uniform draw from a stated population), `enriched`
   (selected for suspected faults or for controls), `decision_audit` (sampled from a version's own decisions), or `locked_stratum`.
   - The scorer reports `sample_type` per row.
   - Errors per 100 are printed as a POPULATION rate only for `uniform` and `locked_stratum`.
   - For the others, print "x / n on this sample" and call it "on the sample", never "per 100 lines".
   - A `decision_audit` row reads "decision precision: k/n correct (95% CI …)".
2. **Scoreboard intro, in plain words.** For each class that has a measurement, give one sentence of the form "Google vs ours on
   <sample described in words>: <a> errors → <b> errors (95% interval)". Then add the "not measured" list, and a line "sf6 release
   (accents): not scored yet; its labels on the truth lines are being fetched". Rebuild `scoreboard.html` at the same path.
3. **Letters.** The locked Wikisource classes (ia 133, ib 1,246) carry aligned human transcriptions. Check, in their source docs and
   the spell-check R0 files, whether any part of them is pixel-adjudicated (and so tier A or B) for letters.
   - If it is, add it as a letters truth set, with `sample_type` `locked_stratum` and the edition-normalisation caveat stated.
   - If it is not, list it as "reference transcription, not pixel truth", and keep it out of truth.
   - Report which, with citations.
4. Update `SCORE_v1.md` (it becomes v1.1), the manifest, the receipt section and the tests.

**Last line:** `LQB1b READY: sample types assigned <n> sets (uniform <n>, enriched <n>, decision_audit <n>, locked <n>); letters truth <added n | not pixel truth>; scoreboard <MB> MB; tests <n> passed`
