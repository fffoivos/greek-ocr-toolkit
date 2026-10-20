# SG1: gallery pack of Google line-segmentation failures (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Owner request via the coordinator, for an owner artifact.** Write only under `docs/records/harvest/collect_v3/segmentation_gallery/`. A live W2 run imports `collect_v3/` from this checkout: never touch it. All inputs are read-only.

## 1. Example crops: 24–30 PNGs, chosen by type from existing card failures
- **Sources of failures:**
  - C1 verdicts `docs/records/harvest/collect_v3/c1/verdicts/*.jsonl`, with card → line ids through `~/Projects/collect-v3-data/run/W1/c1/<set>_key.json` (read only to map ids);
  - T6b masked-card verdicts `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/*.jsonl` with their keys;
  - the CAPS1/SRK results where they exist.
- **Types,** taking each example's type from the verdict error tags and detail:
  1. merged two/three lines in one crop, where the label covers one (merged_two_lines; multi-line crops);
  2. overrun with readable half-lines (crop_overrun);
  3. box fragment: the crop is shorter than the printed line (crop_clipped, or a label/line length mismatch);
  4. rotated vertical line (rotated_crop rows: Gazette digit cells, vertical headings);
  5. clipped edge (crop_clipped at the left or right);
  6. **printed rows with NO Google box**, 3–4 examples. Look in the label-repair / O4d evidence, read-only: `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/` and the toolkit's labelfix and geometry-audit dirs. Use a page if one is at hand; otherwise state "none available" with the paths searched.
- **Per example:**
  - the original crop exactly as Google cut it;
  - where the page raster is at hand (`~/Projects/collect-v3-data/run/cache/pages/`, or harvest_big for v2), also a **page strip** of the same region with Google's box drawn, so the neighbouring lines are visible;
  - a record in `examples.jsonl`: id, source, class, type, crop height, label text, card verdict detail, image paths.
- **Total PNG bytes under 6 MB.** Downscale to about 2× line height and state the scale.

## 2. `counts.json`
- **Per source** (gazette, kosmopolis, lekythos, ia_greek_latin and the C1-checked sources):
  - candidate rows;
  - screen_merged;
  - rotated_crop;
  - overrun cards per 100, before masking (C1) and after masking (T6b);
  - clipped per 100.
  - Inputs: W1 features, T6b population.json, `release_exclusions` (rotated_crop), `c1/c1_results.json`, T6b `checks/t6b_results.json`.
- **v2-wide figures**, each with its provenance path (find the source documents read-only; if a figure cannot be traced, write "not found" instead of guessing):
  - 2.8% of test lines with a ≥3-atom length mismatch carry 44% of edits (E3 analysis, greek-page-ocr);
  - 19% of printed rows without a Google box (label-repair state, 16 Oct).

## 3. `NOTE.md`, one paragraph
What fraction of each failure type masking fixes (T6b vs C1 crop_ok), screening removes (screen_merged / rotated_crop counts) and what remains open: merged multi-line crops that screen_merged misses, box fragments, and missing rows. Quote only numbers from counts.json.

## Hand-off
Leave a guarded commit list (the PNGs are committed this time; the total stays under 6 MB). The last line must be exactly:
`SG1: done | examples: <n> (<per type>) | png bytes: <n> | page strips: <n> | no-box examples: <n or none> | counts.json ok`
