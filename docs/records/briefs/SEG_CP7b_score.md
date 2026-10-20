# SEG-CP7b: score the fresh 100 against the sealed screen decisions (gpt-6.1-sol, medium, network OFF, no reading)

**Authority:** ASTRA-SEG1 plan item 7. The CP7a/a2/a3 receipts and freeze (`seg/CP7_FREEZE.json`, 9212fe49…) apply. Verify the freeze first.

**Inputs:**
- the reader answers: `seg/cp7/answers/segcp7_{a,b}/r1.mapped.jsonl` + `r1.controls.jsonl`;
- the receipts: `seg/cp7/receipts/`;
- the scans: `seg/cp7/scan/` (both ok, 0 violations);
- the sealed decisions (CP7a3).

**Note:** context A's receipt was written by the lead after a freeze-binding file was restored byte-identically (see `cp7/run.log`). Check that the receipt is consistent with the logged run.

## Do
1. **Controls:** 10/10 answered. Compare each with its known lead-approved values. Any control miss voids its context; say so.
2. **Truth per card,** from the reader's owner-standard rubric:
   - DROP-truth = `neighbour_whole_word` OR `multi_line` OR `rotated` OR `horizontally_missegmented`;
   - KEEP-truth otherwise;
   - flags and unreadables are listed for adjudication.
3. **Confusion matrices** for the sealed composed screen decision vs reader truth:
   - the composed union, and each screen standalone (merged, neighbour_words, orientation incl. regional and unknown, geometry_unavailable);
   - FP = the screen drops but the reader says KEEP; FN = the screen keeps but the reader says DROP;
   - precision and recall, stating "recall undefined" if there are no positives.
   - **Separately:**
     - the **rotated-miss rate** (reader rotated=yes and admitted);
     - `orientation_unknown` rows and their reader verdicts;
     - `geometry_unavailable` rows and their reader verdicts (the cost of fail-closed).
4. **Adjudication sheet** `seg/cp7/ADJUDICATION_SHEET.md`, for the lead's pixel check. For every FP, FN, flag or unreadable: row_id, crop path (byte-exact, from the CP7a packs' crops), the reader's rubric answers plus one-line reasons, and the screen decision with its measured evidence (neighbour run, rows, axis). Also a contact sheet `ADJUDICATION_SHEET.png`: the crops tiled with their ids, at most 30 per image.
5. **Do not** tune anything. The decisions are sealed: no threshold changes after the answers.

The staged replay (plan item 7, last part) needs the full-population geometry, which is held for the owner. Do not attempt it.

Write `seg/CP7b_RECEIPT.md` and the commit list. The last line must be exactly:
`SEG-CP7b: done | controls <c>/10 | mapped 100/100 | union TP <a> FP <b> FN <c> TN <d> (P <p> R <r>) | rotated-miss <m> | unknown-axis <u> (reader drop <x>) | geometry_unavailable <g> (reader drop <y>) | to adjudicate <n> | tests: <n> passed`
