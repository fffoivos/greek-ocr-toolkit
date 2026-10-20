# SEG re-report without gate-failed rows (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no segmentation runs)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. HEAD contains content gate 0.3
(`docs/harvest/line_pipeline/gate03/REPORT.md`) and steps 1–5 (`docs/records/harvest/seg_steps/s1..s5/`).
- Output: `docs/records/harvest/seg_steps/gate_rereport/`.
- Edit nothing else: no step outputs, sheet files or source.
- Same untouchables as before: `seg_census/package/`, `seg09/` and the census02 evidence (read only).

**Read first:**
- `docs/harvest/line_pipeline/gate03/REPORT.md`;
- `s4/REPORT.md` (scores, the typology replay, the 2×2 and the numeric refits);
- `s5/BAND_PROPOSAL.md` with its `build_population.py` and `band_sweep.py`;
- `sheet/README.md` and `sheet/cards.jsonl`.

## Why

The owner's gate:
- a row with a word mixing scripts is dropped;
- a row with letters of a script outside the document's expected scripts is held.

Both happen before segmentation, so neither row is a segmentation case. The step scores so far included such rows. Remove them
from every evaluation set and report again.

**Also removed: the part-2 length exclusions.** Content gate 0.3 part 2 (`gate03/REPORT_part2.md`) also excludes these, before
segmentation:
- `short_line`: an ordinary (non-cell, non-numeric) line under the letter minimum;
- `single_character_cell`: a cell (A ≤ 6) with at most one letter-or-digit;
- `numeric_shape`: a numeric non-cell line with at most one letter-or-digit;
- `cell_status_unresolved`: a row with no crop dimensions, which is HELD.

Remove those rows too. Report every count three ways:
- mixed/foreign only;
- part-2 only, by reason;
- all gate exclusions together, which is the headline.

**Both halves of the step-4 2×2 stay decision inputs.** Under the owner's amendment, text cells with more than one letter-or-digit
are admitted. Report the numeric and the non-numeric halves alike. Give how many small rows per output type survive the gate.

## Which rows fail

**The authority is the pipeline's own gate.** Use content gate 0.3's shared exclusion helper from `line_pipeline.py`, run on
each row's raw Google text with the pipeline's `inventory`, `expectations` and codec. Resolve the expectations exactly as the
pipeline does: page override > book declaration > source policy (`adm.expected_policy`), from whatever local metadata the
step-1 inputs carry.
- Report, per set:
  - how the expectations were resolved;
  - any row whose expectations do not resolve (keep it, and list it);
  - the excluded rows by kind (mixed-script DROP / foreign-script HOLD), with their text.
- **Cross-check.** The coordinator's quick list, made with a plain Unicode-script rule, is at
  `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/db202b49-34e2-49d2-9fbd-271fe776b56d/scratchpad/foreign_mixed_ids.json`
  (keys `foreign`, `mixed`; read only). Its estimates:
  - 150 → 1 + 1; 888 → 3 + 10; 250 cells → 0; 417 typology → 18 + 3; s4 `small.jsonl` → 18 + 1;
  - band_population: 2 foreign + 4 mixed of 495; changed_lines 1 + 2.

  List every id where the two lists disagree, with the reason. The pipeline gate decides. The coordinator's list does not cover
  short lines.

## Re-report

Use only the saved verdicts and evidence from steps 1–5. No segmentation run. Score exactly as in each step's `validate_report.py`
and `s5/band_sweep.py`, with the gate-failed rows removed. For every number give **before → after** and the new denominator.

1. **Step scores**, columns 0.8 | 0.9-s1 | 0.9-s2 | 0.9-s3 | 0.9-s4:
   - the 150 FP/FN/UNC;
   - the 888 rated agreement /135;
   - owner marks /235, latest mark wins;
   - the 250 cells as reported before;
   - the 417 typology owner agreement /185 (0.8, s3, s4), with the per-`final_type` table.
2. **Step 4:**
   - the 2×2 per output type (numeric / mixed / non-numeric) with n and owner agreement per cell, plus the "<30 numeric crops →
     indicative only" flags;
   - the numeric refits per box: a, b, SD, MAD and n, both for all crops and for crops without an owner judgement.
3. **Step 5:**
   - re-run the band sweep on `band_population` without the gate-failed rows;
   - give the counts for the current 0.5–1.5, the proposed 0.30–2.00 overall, the numeric 0.35–2.00 and the class-weighted
     0.55–1.30;
   - say whether the best band in each sweep moves, and by how much;
   - list `changed_lines` with and without the gate-failed rows;
   - re-check the owner cases (ΠΟΛΕΩΣ, l0005, gazette l0120).
4. **The seg09 sheet** (read only):
   - which `cards.jsonl` cards are gate-failed, by group and section;
   - whether any remaining card would change group or section;
   - which intro numbers change, before → after.
5. **One line per set:** `<set>: <before> → <after> (removed <n mixed> + <n foreign> + <n part-2>); conclusion changes: <no | what>`. A
   conclusion is any statement in `s4/REPORT.md` or `s5/BAND_PROPOSAL.md` about direction, the best cell or band, or the 2×2
   answer.

6. **"Unexpected scripts by book" (owner's flagging request).** Run on the census_02 raw rows at `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells/population_cells.jsonl.gz`
   (all 592,466 census_02 rows: row_id, source, raw_text, width_px, height_px, primary_class, …; book = the second segment of row_id;
   page = sNNN; read only, do not regenerate), with the gate 0.3 inventory and expectations. These are the authority. The coordinator's Unicode-name
   estimate is in `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/script_inventory_20261019.md`
   and is for comparison only.
   - Give one table per source × book × unexpected script, with rows, gate outcome (HOLD foreign / DROP mixed) and 2–3 example
     texts.
   - Split the books into three classes:
     - **(a) Real other-language content.** The HOLD is correct, and the book expectation may deserve an extra script. The
       coordinator's candidates:
       - ia_poly1850 26e14cb9c90b750f, Chinese, 232;
       - 174d84a441d69a70, Syriac 22 + Arabic 15;
       - 61d0e23d1e93ae02, Arabic 82;
       - c39403323b6d5d89, Arabic 24;
       - 5aa15e93b2f445b8, Hebrew 28;
       - ebcfd6056abfa776, Hebrew 11;
       - ia_greek_latin, Hebrew, 3 books, 13 rows.
     - **(b) Letter-level confusion** handled by the mixed-word rule: Cyrillic in gazette_modern (~447 rows over 285 books); Greek
       in the Cyrillic archives.
     - **(c) Noise scripts on damaged glyphs, spread thin:** gazette Arabic (~145 rows/108 books), kana (~110), Hangul (29),
       Thai/Indic/Lao in single digits, and ia_russian/serbia Arabic/CJK single rows.
   - Classify by the evidence you can see: the row count per book, whether the rows are whole words in that script or single
     letters inside other-script words, and the example texts. Say which books are borderline.
   - **Codec questions, listed separately and not as scripts:** the ordinal indicators º ª (in Latin books, legitimate) and the
     MICRO SIGN µ where μ is printed. Give the rows and books.
   - This table is flagging only: no expectation is changed.

Write `REPORT.md`, `gate_failed.jsonl` (set, id, kind, words/scripts, text), `summary.json` and a receipt.

**Last line:** `SEG GATE REREPORT READY: removed 150 <m+f+s> / 888 <m+f+s> / 250 <m+f+s> / 417 <m+f+s> / band <m+f+s>; small rows surviving numeric <n> mixed <n> non-numeric <n>; 150 FP/FN/UNC s4 <before> → <after>; 888 <b> → <a>; marks <b>/<N> → <a>/<N>; typology <b> → <a>; 2x2 answer changes <no|yes>; best band moves <no|yes>; sheet cards removed <n>; coordinator list disagreements <n>; conclusions changed <none|list>`
