# SEG final sheet: every changed line, 0.8 → 0.9-s4, with the owner's mark beside the tool's (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; NO publish)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. HEAD contains steps 1–4 (`docs/records/harvest/seg_steps/s1..s4/`)
and the step-5 proposal (`s5/`). Output: `docs/records/harvest/seg_steps/sheet/`. Never re-run the segmentation tool: build cards from the
saved evidence records only.

**Renderer (mandatory, owner decision).** Use the package renderer on branch `coord/review-sheets`, checked out read only at
`~/Projects/greek-ocr-toolkit-review` (HEAD 19347b5a8). Do not edit that worktree.
- Read its design `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md` and follow it exactly: card anatomy, frames, keys, persistence, the
  checklist in §7.
- Copy `greekocr/adjudicate/owner_sheet.py`, `owner_sheet.css` and `owner_sheet.js` byte for byte into `sheet/vendor/` (record the
  shas), and import from there.
- Follow `scripts/review/build_sheet1_demos.py` and `docs/records/review/reference_scratch/build_gate_sheet.py` for the overlay adapter.

## Sheet content

- **Sheet prefix `seg09`** (database ids `seg09:<line_id>`).
- **Last two versions only:** "0.8" and "0.9-s4 (latest)". Each shows the verdict, the reason and the numbers behind it: box long
  side / short side, ratio, padding, and the gate counts. Add one row, **"Changed by"**: which steps changed the verdict (s1 whole
  word, s2 turn, s3 curve, s4 small all-ink), from the per-step flips files.
- **Inner frame** = the 0.9-s4 verdict. **Outer border** = the owner's mark.
- **The owner's existing marks**, shown as a text row "Owner mark (sheet, time)" beside the tool's verdict. Sources:
  `owner_marks_20261019.jsonl`, the 888 rating and the typology marks.
  - **The page must NOT pre-fill the database from these.** It never writes on load.
  - The db mark starts empty unless the owner marks it on this sheet.
- **Overlays:** the 0.9-s4 saved evidence.
  - Main row: ascender and base. For s3 curved rows, the base curve polyline.
  - Other rows, whole and cut-off neighbour words.
  - The final text box: the de-skewed or unrolled box for normal rows; the all-ink box for small rows (label it "all-ink box").
  - For turned (s2) crops, draw in the processed frame mapped back to the crop. Overlays come from saved evidence only.
- **Cards:** every line in the 150 + 888 + 250 replay AND the 417 typology cards (no controls) whose 0.8 verdict ≠ the 0.9-s4
  verdict. De-duplicate by line_id, keeping one card and listing both cohorts in the tags.
- **Groups, in this order:**
  1. now disagrees with the owner (tool vs mark/rating) — most important;
  2. newly agrees with the owner;
  3. changed, no owner judgement.

  Within each group, order by step, then source.
- **Step-5 section** at the end, if `s5/changed_lines.jsonl` exists: "Proposed band (not adopted)". It holds every line whose
  verdict the proposed band would change, with the current and proposed verdict in a row. The inner frame stays the 0.9-s4
  verdict.
- **Intro:**
  - what the sheet shows;
  - the five steps in one line each;
  - the scores table 0.8 → s4 from `s4/REPORT.md` (150 FP/FN/UNC, 888 /135, marks /235, typology /185);
  - the 2×2 summary from s4;
  - the colour legend and the keys.

  Plain words.

## Do

1. Build `sheet/seg09_sheet.html` through `owner_sheet.render` with `spec.sheet_prefix='seg09'`. Write a manifest
   `sheet/cards.jsonl` (line_id, group, cohorts, steps, verdicts, owner mark source) and the builder `sheet/build.py`.
2. **Checks:**
   - every card's crop bytes sha256 = the record's crop sha;
   - the card count equals the computed changed set;
   - the page has no load-time db write (static check of the JS, same as the package runtime test, if runnable offline);
   - the HTML size is < 16 MB;
   - a headless screenshot of the first 3 cards, if a local headless browser is available; otherwise say so.
3. Receipt `sheet/receipt.json`. Do NOT publish: the lead publishes.

**Last line:** `SEG SHEET READY: cards <n> (disagree <n>, newly agree <n>, unjudged <n>; proposed-band <n>); html <MB>; crop sha <n>/<n>; no-load-write <ok>; screenshot <ok|unavailable>`
