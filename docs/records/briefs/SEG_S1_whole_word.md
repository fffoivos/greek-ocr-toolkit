# SEG step 1: whole word = every letter body ≥95% visible (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead commits. This supersedes
`docs/records/briefs/SEG09_CP1.md` (not acted on). Leave the stray `docs/records/harvest/seg09/cp1_initial_hashes.json` untouched, and use the new
output directory `docs/records/harvest/seg_steps/s1/`.

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md`. The owner's standing rules are
  binding: a tool is EXACTLY the owner's rules; never add a guard, test, threshold or heuristic; extras are diagnostics only.
- `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md`, `DESIGN.md`, and the 0.8
  policy (410f4566, on this branch). Also the SEG-CELLS hand-off `segeval1/cells/HANDOFF.md`, for the 250 cell sample crops.

**The single change (owner, 19 Oct).** This is version **0.9-s1**, built on the 0.8 owner-stage source files on this branch (NOT the
deployed census_04 package copy under `docs/harvest/seg_census/package/`, which stays untouched).
- In the other-lines rule, a word from another row is **WHOLE iff EVERY letter body of that word is ≥95% visible** in the crop. This
  replaces the "≥2 bodies ≥60% visible + no horizontal-edge contact" test. Keep the existing word grouping (the 0.35-x-height gap) and
  letter-body definition. The ">2 whole words → DROP" and "second complete line → DROP" rules, rule 2 (length 0.5–1.5) and rule 3
  (padding 1.5) are unchanged.
- Nothing else changes.

**Do.**
1. Implement the change, with tests: bodies at 94.9% vs 95.0%; a word with one cut body counts as cut-off; exactly 2 vs 3 whole
   words.
2. **Witness `gazette_modern--80e8a42cbf8e629f--s000-l0120`.** The owner says: "should have been dropped, more than 2 full words
   showing, the output length is correct". Report the 0.8 vs 0.9-s1 word groups (per body visibility, whole/cut-off), the counts and
   the verdicts, with an overlay PNG.
3. **Witness `129cff40-p000009-l0107`.** The owner says: "the accents of ἔχει were detected as a second line, complete error". REPORT
   ONLY what the inventory saw: rows, votes, bodies, visibility, coverage, and which components formed that row, with an overlay. Do
   not change anything for it.
4. **Replay** 0.9-s1 natively on the **150** (segeval1), the **888** (calibration) and the **250 cell sample crops** (cells), using
   the gate2 replay workflow and inputs. Then score against the owner standard exactly as gate2 did:
   - the 150: fine/faulty/unresolved, giving FP/FN/UNC;
   - the 888: agreement on the 135 owner-rated rows;
   - **additionally, all owner marks:** `segeval1/owner_marks_20261019.jsonl` (gate 62, cells 152, de-skew 21) for any marked line in
     these sets. Report KEEP/DROP agreement (latest mark wins; list conflicts).

   Give the 0.8 → 0.9-s1 confusion side by side, plus flip tables (every changed verdict, with the owner label or mark).
5. **Readback:** every unchanged verdict replays exactly, and the box/padding evidence equals 0.8 wherever the gate result is
   unchanged. Include a scope guard listing the changed source files.
6. **Report** in `docs/records/harvest/seg_steps/s1/REPORT.md`, plus `flips.jsonl`, a receipt and the overlay PNGs under `s1/overlays/`.

**Last line:** `SEG S1 READY: gazette l0120 whole 0.8 <n> → <n> (<verdict>); 129cff40 second row = <one line>; 150 FP/FN/UNC 0.8 <a/b/c> → <a/b/c>; 888 rated agree <n> → <n>/135; owner marks agree <n> → <n>/<N>; flips <n>; tests <n> passed`
