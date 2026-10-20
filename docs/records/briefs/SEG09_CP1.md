# SEG09 CP1: implement the owner's items 2–4, plus witness traces (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no replay of the full sets yet)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead commits.

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md`. The owner's standing rules are
  binding: a tool is EXACTLY the owner's rules; never add a guard, test, threshold or heuristic; extras are diagnostics only.
- The 0.8 hand-off `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md`,
  `DESIGN.md` and its policy code (410f4566).

**Version.** Segmentation **0.9-dev**, built on the 0.8 source files on this branch: the owner stage files, NOT the deployed
census_04 package copy under `docs/harvest/seg_census/package/`, which stays untouched. Owner rules 1 (other lines), 2 (length 0.5–1.5)
and 3 (padding 1.5) are unchanged EXCEPT for the following owner changes (19 Oct, verbatim intent):

- **Item 2, curved and nonlinear lines.** Long side = the arc length of the detected main-row base curve over its supported
  x-range. Short side = the perpendicular ascender–descender distance the detector already provides for that row. Rule 2 normalises
  the long side by that short side.
  - On straight lines this must reduce to the 0.8 de-skewed box. Test: every flat-angle row replays the 0.8 box/ratio to the digit
    (use the gate2 150+888 evidence).
  - Witness `ia_poly1850--df8f2267db2b7275--s025-l0037`: 0.8 shows a baseline sag of 41 px and a single-angle box 92 px tall vs a
    57 px line. Report the 0.8 vs 0.9-dev long side, short side and ratio, with a crop overlay PNG of both boxes / the curve.
- **Item 3, vertical crops.** If crop height > width, rotate it 90° RIGHT (clockwise) before ALL measurement and detection. Nothing
  else changes.
  - Witnesses: the vertical owner-KEEP crops on the 150 (69×252, 26×166, 32×265, 19×156; find their ids). Report 0.8 vs 0.9-dev
    verdicts and evidence.
- **Item 4, whole word.** In the other-lines rule, a word from another row is WHOLE iff EVERY letter body of that word is ≥95%
  visible in the crop. This replaces the "≥2 bodies ≥60% visible + no edge contact" proxy. Keep the existing word grouping (the
  0.35-x-height gap). The ">2 whole words → DROP" and "second complete line → DROP" rules are unchanged.
  - Witness `gazette_modern--80e8a42cbf8e629f--s000-l0120`. The owner says: "should have been dropped, more than 2 full words
    showing, the output length is correct". Report the 0.8 and 0.9-dev word groups (bodies, visibility per body, whole/cut-off) and
    the verdicts, with an overlay.
  - Witness `129cff40-p000009-l0107`. The owner says: "the accents of ἔχει were detected as a second line, complete error".
    REPORT ONLY what the inventory saw: rows, votes, bodies, visibility, coverage, and which components formed the "second line",
    with an overlay. Do not add a rule for it.
- **The owner's box notes, diagnostic only:** for the lines the owner noted "bad boxes" ("270", "37"), "wrong box" ("προηγουμ.
  χρήσης") and "length is correct" (`9aa01acfc…`, ratio 1.56), report the 0.8 and 0.9-dev measured boxes with crop overlays. Find
  the ids in `segeval1/owner_marks_20261019.jsonl` (sol-recut, read only).

**Deliver:**
- the code + tests: item 2 straight-line identity, item 3 rotation, item 4 boundaries (a body at 94.9% / 95.0%), and the witnesses;
- `docs/records/harvest/seg09/CP1_REPORT.md` with the witness tables and overlay PNG paths (under `docs/records/harvest/seg09/cp1_overlays/`);
- a scope guard: list every changed source file.

**Last line:** `SEG09 CP1 READY: item2 straight identity <n>/<n>, sag witness 0.8 <ratio> → 0.9 <ratio>; item3 vertical witnesses <verdicts>; item4 gazette l0120 whole words 0.8 <n> → 0.9 <n> (<verdict>); 129cff40 second-line cause <one line>; tests <n> passed`
