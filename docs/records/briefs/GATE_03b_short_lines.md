# Content gate 0.3, part 2: short non-numeric lines are excluded before segmentation (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no census)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. HEAD contains the first part of content gate 0.3
(the mixed-script and foreign-script exclusions): see `docs/harvest/line_pipeline/gate03/REPORT.md` and
`docs/records/briefs/GATE_03_content_gate.md`. Add to the same `gate03/` folder with `REPORT_part2.md`. The untouchables are the same.

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md`. A tool is EXACTLY the owner's
  rules; never add a guard, threshold or heuristic.
- `greekocr/harvest/line_pipeline.py`: `final_eligibility` (~275–300), `Pipeline.evaluate`, and the gate helper from part 1.
- `greekocr/harvest/line_pipeline_census.py`: `prepare()`.
- The numeric grammar: `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/scripts/common.py`,
  `output_type(text)`, read only. A line is numeric if it is decimal digits plus that exact separator list, or canonical uppercase
  Latin Roman numerals.

## The change (owner, 19 Oct)

The owner said: "we should probably have a <10 chars exclusion criterion as well; although numerical cells should be admitted
even if they are short." The rule already exists in `final_eligibility`, as `short_line`:
- prose: fewer than `prose_min_letters` (10) letters;
- `headings_caps`: fewer than `heading_min_letters` (4) letters.

It counts letters, as the owner decided on 14 Oct: `inv["letter_count"]`. But it runs last, so short lines reach segmentation,
every tool and every sheet.

**Owner amendment, same evening:** "let's say we allow text cells [and] numericals that contain >1 chars." The coordinator's
reading, which is binding here:

1. **Letter-or-digit count** (`alnum`) = the number of characters in the raw output that are Unicode letters (category L*) or
   decimal digits (Nd). Punctuation, marks and spaces do not count.
2. **Cell** = a crop whose long side is at most 6× its short side, on the crop's pixel dimensions (A ≤ 6, rotation-free, exactly
   the A of step 4). The chars ≤ 8 half of the small definition is not needed here: the length rule implies it.
   - Take the dimensions from the row record the way the census already carries them (`crop_bbox` or the bound crop's size). Say
     which field you used.
   - If a row has no crop dimensions, the gate cannot decide whether it is a cell. HOLD it with
     `reason="cell_status_unresolved"`, and report the count on each set.
3. **The gate test**, run right after the part-1 exclusions and before the crop-identity check and segmentation, in this order:
   - **Cell:** exempt from the letter minimum, whether its content is text or numeric, provided alnum > 1. Otherwise DROP with
     `dict(reason="single_character_cell", alnum=..., A=...)`.
   - **Numeric, not a cell** (role `numerics_tables` OR the raw text matches the numeric grammar): exempt from the letter minimum,
     provided alnum > 1. Otherwise DROP with `dict(reason="numeric_shape", alnum=..., detail="<=1 letter-or-digit")`.
   - **Ordinary line, otherwise:** prose under `prose_min_letters` (10) letters, or `headings_caps` under `heading_min_letters`
     (4) letters, gives DROP with `dict(reason="short_line", role=..., letters=..., minimum=...)`. Use the same letter count on
     the raw text (`inv["letter_count"]`) and the same role resolution as `final_eligibility`
     (`expected.content_role` > `row.content_role` > `row.primary_class` > `"prose"`).

   Every exclusion goes through `finish()`, so every route is `not_run_due_to_prior_exclusion`. `prepare()` makes no native call
   for these rows, through the same shared helper as part 1.
4. **The numeric grammar.** Put it into `line_pipeline.py` as one function that reproduces `output_type(text) == "numeric"`
   exactly. Do not import it from sol-recut. Add a parity test against `common.py`'s `output_type` on every text in the 150, 888,
   250 and 417 sets, reading them only.
5. **Final eligibility keeps its checks, and stays idempotent.** Its `short_line` test calls the same shared function, with the
   same exemptions, so an admitted cell or a grammar-numeric line is not dropped as short at the end either.
   - Leave `nonletter_fraction` and `numeric_shape` (≥4 digits and 60% shape, `numerics_tables` role only) UNCHANGED.
   - **Diagnostic only:** count, on the 150, 888, 250 and 417 sets, the gate-admitted cells and numeric lines that
     `final_eligibility` would still exclude, split by `nonletter_fraction` and by `numeric_shape` (≥4 digits), with examples.
     This is for an owner decision; it changes no code.
6. **Versions and docs:**
   - The content gate stays 0.3. Add the iteration "short ordinary lines excluded before segmentation (letters); cells and numeric lines
     exempt with more than one letter-or-digit" and regenerate `tool_versions.json`.
   - `pipeline.mmd`: C gets `"Short ordinary line, single-character cell or numeric line" --> D`.
   - `README.md`: executed-sequence steps 2 and 7.

## Do

1. **Tests** in `tests/test_content_gate.py`. In every exclusion case the segmenter is never called, using a segmenter that raises.
   "Wide" means A > 6 (not a cell); "cell" means A ≤ 6.
   - A wide 9-letter prose line → DROP `short_line`; a wide 10-letter one passes.
   - A wide 3-letter `headings_caps` line → DROP `short_line`; a wide 4-letter one passes.
   - A cell "ΑΒ" (text, 2 letters) passes; a cell "Α." → DROP `single_character_cell`; a cell "7" → DROP `single_character_cell`.
   - A wide "1.234" on a prose page passes the gate and is not `short_line` at final eligibility.
   - A wide "XIV" passes; a wide "12" passes; a wide "1" → DROP `numeric_shape`.
   - A wide "12" with the `numerics_tables` role passes the gate.
   - A row with no crop dimensions → HOLD `cell_status_unresolved`.
   - A part-1 exclusion still takes precedence: a mixed-script word in a short line gives DROP `mixed_script_word`.
   - `prepare()` skips all three new exclusion kinds.
   - The grammar parity test.
2. **Run** `tests/test_content_gate.py`, `tests/test_line_pipeline.py` and the four `tests/test_seg_*.py`. Report the counts. If an
   existing assertion encodes the old order (short lines reaching segmentation), update only that assertion and show the diff.
3. **Counts, read only, no tool run:** on the 150, 888, 250 and 417 sets, how many rows each new reason excludes
   (`short_line`, `single_character_cell`, `numeric_shape`, `cell_status_unresolved`), and the field the crop dimensions came from.
4. **Scope guard** and `REPORT_part2.md` with the diagnostic from step 5 of the change and the counts, plus a receipt.

**Last line:** `GATE 0.3 PART 2 READY: short_line <ok>; cell exempt <ok>; single_character_cell <ok>; numeric_shape <ok>; numeric exempt role <ok> grammar <ok>; counts 150/888/250/417 short <n> cell1 <n> num1 <n> unresolved <n>; grammar parity <n>/<n>; final idempotent <ok>; still-excluded diag nonletter <n> numeric_shape <n>; tests <n> passed <n> failed`
