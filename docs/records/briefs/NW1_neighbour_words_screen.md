# NW1: third admission screen `neighbour_words`, from the existing foreign-ink measure (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Owner rule tonight (verbatim):** "the important thing is that really there are no full words showing from the top or bottom line, and that we use the tools we have already built for it, and that we also avoid badly segmented horizontal ones as well".

The coordinator's ruling is a third admission screen built from the **existing** foreign-ink ownership measure:
- `greekocr/glyphs/foreign_ink.py` + `greekocr/glyphs/recut.py`, Voronoi ownership;
- frozen params **801d517e**, as used by `docs/records/harvest/recut_v1/v2_full/run.py`;
- **measure only, NO masking.** Admission stays on the original crops.

Reuse those functions. Do not write a new ink model. The run root `~/Projects/collect-v3-data/run` is live (a materialize and the BSB reads): read only, no locks. Crop regeneration uses only `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` (byte-exact).

## 1. Definition: rule `neighbour_words`
Drop a row when the foreign ink inside its original crop (ink owned by a neighbouring line) forms a readable word. In the tool's own quantities:
- a connected horizontal run of foreign-ink components **≥ 3 components wide**;
- spanning **≥ 2 x-heights of width**;
- with component height **≥ 0.5 × the line's x-height**.

Half-letters at the edge (lower or upper halves only) **stay**. Expose the three thresholds as parameters, with the frozen defaults above.

## 2. Calibrate on the C1 card verdicts
- **Data:** `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/` (+ `c1_results.json`, and the keys there or in its README, to map cards to row_ids).
- **Truth labels:**
  - crop_overrun where the detail contains "readable" / "word" / "text" → **should drop**;
  - "lower halves" / "upper halves" only → **should keep**;
  - crop_ok cards → keep.
- **Report:**
  - precision and recall of the screen at the default thresholds, the confusion matrix, and a small grid around the defaults (±1 component, ±0.5 x-height, height 0.4/0.5/0.6);
  - pick the setting with the best recall at precision ≥ 0.8, else state the trade-off;
  - list every disagreement card (row_id, verdict detail, the measured run).
- **Also count, for information only:** C1 crop verdicts that describe a horizontally mis-segmented line (words cut off left or right, a line split in two, or two lines side by side) and that neither rotated_crop nor screen_merged catch. `rotated_crop` stays the screen for horizontal/vertical mis-segmentation; no new rule here.

## 3. Apply
- Add `neighbour_words` to `greekocr.harvest.admission`: bump `tool_version`, keep the schema, record the params sha in the receipt.
- **Re-issue** the W1 admission: `docs/records/harvest/collect_v3_admission/w1_originals_v3_admission.jsonl`, `_admitted.jsonl` and receipt, from the same input. Give drop counts per source × class.
- Then **stage_crops** for the re-issued W1 set into the same crops tree. Mark rows no longer admitted as `admitted: false` in `crops_manifest.jsonl`, adding a column; **do not delete PNGs**. The coordinator's W1 upload is already running, so give them the list of withdrawn row_ids as `w1_neighbour_words_withdrawn.txt`.
- Make the W2, Gazette, BSB and final admissions pick the rule up automatically (the same CLI).

## Tests
- Planted cases: a crop with a full neighbour word (drop), a crop with only lower-half descenders (keep), a clean crop (keep).
- The calibration numbers are reproducible.
- The params sha is recorded.
- The existing admission tests still pass.

Leave a guarded commit list. The last line must be exactly:
`NW1: done | calibration: P <p> R <r> on <n> cards (thresholds <...>) | W1: 28798 -> <pass> (neighbour_words drops <n>; top <source|class n>) | withdrawn list: <n> | horizontal-missegmentation uncaught (info): <n> | tests: <n> passed`
