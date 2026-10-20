# SEG-CP7c: refreeze, a NEW fresh uniform 100, gate geometry and packs (gpt-6.1-sol, medium, network OFF, no reading)

**Authority:** ASTRA-SEG1 plan item 7: a failure goes back to the relevant checkpoint, then a refreeze and a **new** fresh 100.

**Coordinator rulings since the first fresh 100** (7b16c5cf):
- `geometry_unavailable` drops count as **policy, not error**, in the gate;
- end-clips: **option C** (33a177e1). They are admitted as a known class. `edge_clip_candidate` is a non-gating diagnostic and a lower bound; it is counted, not dropped.
- **The gate standard stays: 0 FP + 0 FN on the screens** (merged, neighbour_words, orientation).

Every CP7a/CP7a3 constraint applies (snapshots only, never the live root; byte-exact crops; HANDOVER packs; canonical scanner by hash; the 10 lead-approved controls; sealed decisions; launcher not run).

## Do
1. **Refreeze:** `seg/CP7_FREEZE_r2.json`, covering every current SEG/admission module (incl. the CP5′b diagnostic), params, the ledger 76ea2d35…, and the codec/lookalikes/Serbian shas. Re-verify the frozen gate: KEEP 22/22, D 9/9 composed, C1 6/6, gallery 6/6, rotated 4/4. **Every freeze-bound file must be present** (note: `CP5_verification.json` was restored from its .gz). List the bound paths so the lead never deletes one.
2. **New draw:** seed `seg-cp7:fresh100-r2`; the same pre-screen population as CP7a2 (W1 + W2 snapshots `*_20261018_0524`, verify their shas).
   - Exclude the first fresh 100, all calibration witnesses, and the 22 KEEP.
   - Report the overlap check (0).
3. **Gate geometry:** prepare the ≤ 100 pages of the new draw exactly as CP7a3 (the CP2 fallback, separate cache outside the run root, counted; reuse already-prepared pages when hash-valid).
   - Disk: Mac free space is about 12 GB; stop if < 10 GB.
   - Then compute the **sealed** decisions (composed union, each screen, geometry_unavailable, orientation_unknown, edge_clip_candidate).
4. **Packs:** beds `segcp7r2_a` and `segcp7r2_b`, 2 × (50 + 5 controls), fresh opaque ids, `prompts/bsb.md` verbatim plus a rubric revised as `prompts/segcp7_crop_rubric_r2.md`:
   - the same fields as before, but **split end-clipping out**: `end_clip: yes/no` (the left or right boundary cuts letters or punctuation of the target line) is a **separate** field;
   - `horizontally_missegmented` now means only "the target line is split, or the crop crosses a column, or two horizontally adjacent text blocks are joined";
   - each field with a one-line reason, and the owner's sentences verbatim;
   - no screen outputs leaked;
   - include W2C1c's reader-behaviour addendum, `prompts/` in `docs/records/harvest/recut_v1/w1_masked/w2c1/`, which prevents path-construction VOIDs.
5. **Launcher:** `seg/cp7/launch_cp7_r2.sh`, sequential, with the limit probe, logging to `cp7/run_r2.log`, and run_bed's refuse-rerun guard. **Do not run it.**
6. **Scoring tool, for after the read:** `seg/cp7/score_r2.py`.
   - DROP-truth = neighbour_whole_word ∨ multi_line ∨ rotated ∨ horizontally_missegmented. **end_clip is not part of the truth**; it is reported separately as the known-class rate, alongside edge_clip_candidate agreement.
   - Report the confusion matrix per screen and composed, with geometry_unavailable reported as policy.
   - **Gate pass** = screen FP 0 and FN 0, controls 10/10, mapped 100/100, scans ok.
   - Also produce an adjudication sheet with a contact sheet, as CP7b did.

Tests: freeze binding list, deterministic and disjoint draw, crop shas, pack closure and opacity, scanner hash, rubric with no leaks, score_r2 on fixtures.

Write `seg/CP7c_RECEIPT.md` and the commit list. The last line must be exactly:
`SEG-CP7c: done | freeze r2: <sha> | frozen gate ok | draw r2 disjoint (overlap 0) | gate pages prepared <n> (unavailable <u>/100) | sealed drops <k> (<by rule>) | packs 2x55 | launch_cp7_r2.sh ready | score_r2 ready | tests: <n> passed`
