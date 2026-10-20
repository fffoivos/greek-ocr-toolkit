# CELLS-OPUS handoff: crop size vs Google output for short crops

Read-only analysis on the Mac. I changed no repository code, made no commits and made no network, ssh or reader calls. All outputs are in this folder.

## Data used

| population | rows | source |
|---|---:|---|
| census | 592,466 | `../cells/population_cells.jsonl.gz`. It was already present, so no polling was needed. Fields used: `row_id, wave, source, primary_class, raw_text, width_px, height_px, characters, verdict_05, reason_05, crop_sha256`. |
| W1 | 101,098 | Census rows with `wave == "W1"`, which the census reduced from `collect-v3-data/snapshots/W1_features_20261018_0524.jsonl`. The snapshot supplied `crop_bbox` and `crop_source_sha256` to rebuild the crops. |
| 888 | 888 | `../gate2/replay_calibration.jsonl`: `after.frame.source_width/source_height`, `verdict_05..08`, `owner_rating.decision` (135 rated: 78 KEEP, 57 DROP). Google text comes from the lookup in `../deskew/replay_calibration.py`, copied into `scripts/pass2_small.py`: `predicted-rows.json.gz`, falling back to `population-data/details`. That lookup asserts `character_count` equality on all 888 rows. |
| 150 | 150 | `../scored/owner_rows.jsonl` (google_text, crop, 0.5 reason) and `../gate2/replay_segeval1.jsonl` (dimensions, verdicts, `owner_standard_state`: fine 118, faulty 30, unresolved 2). |

Cross-checks: all 1,038 rows of the 888 and the 150 are census rows with identical text and dimensions. 41 of the 888 carry a `verdict_05` that differs from the census `verdict_05`; for those I used the 888 file's own value and left the 0.5 reason blank.

## Outputs

- `size_vs_output.md`: the summary, then per population A1 (ratio quantiles per chars, by numeric/mixed/non-numeric, plus the long reference), A1b (pixel sizes), A2 (fits), A3 (0.5 verdicts by reason; false rejects on the 150 and 888), A4 (counts by source and class), and A3b (percentile of each owner-judged short row within the census).
- `short_non_numeric_typology.md`: 120 uniform plus 59 owner-anchored crops, all looked at, in 14 types, with counts, verdicts and examples.
- `samples.jsonl`: 329 rows (120 typology_uniform, 59 typology_owner_supplement, 150 numeric_sample). Fields: `set, population, line_id, crop_path (absolute), text, width, height, chars, output_type, verdict_05, reason_05, verdict_08, owner, source, primary_class, type, note, crop_hash_verified, viewed`.
- `crops/`: 266 W1 crops rebuilt from the local page cache. All 266 are byte-identical to the census `crop_sha256`.
- `analysis.json` holds the machine-readable tables. `scripts/` holds the code: common.py, pass1_census.py, pass2_small.py, analyse.py, percentiles.py, draw_samples.py, sheets.py, typology.py, typology_md.py.

## What I could not do, or did differently

- W1 crop PNGs are not on this Mac, so I rebuilt them from local page JPEGs (hash-verified). I did not rebuild W2 crops; W2 is in the census tables but not in the samples.
- The typology is one viewer's labels, assigned by eye from aspect-preserving contact sheets. It is not blind and not double-read. Of the 150 numeric samples I looked at 20 (19 are clean cells; 1 is a 3-line text block whose Google text is only the line number "1050").
- I added an owner supplement of 59 crops (all short non-numeric rows of the 150, plus the owner-rated ones of the 888) beyond the ~120 asked for, to tie each type to owner verdicts. The uniform counts exclude it.
- Definitions: numeric requires at least one digit, or an upper-case Latin Roman numeral. Lower-case or Greek-iota Roman numerals fall in non-numeric. mixed = has a digit, not numeric, and ≤ 2 letters (this includes digits plus an unlisted symbol). `§ 5` is numeric by the separator list given.
- The vertical rule (height > width) also removes 1,566 short numeric 1–2-char crops that are only slightly taller than wide; only 108 of them have height > 2·width. I applied it as specified.
- I proposed no thresholds.

## Main findings

1. All 71,251 short crops (chars ≤ 9) come from W1 and W2. No collection-v2 wave has a row under 10 chars.
2. Short non-vertical crops in the census: numeric 36,307, mixed 1,312, non-numeric 21,490. Another 12,142 are vertical.
3. Short numeric: ratio = 0.460·chars + 0.787 (SD 0.63). Text lines: 0.385·chars + 1.995 (SD 3.11). The numeric slope is about 1.2× steeper, the intercept about 1.2 lower, and the scatter about 5× tighter. The hypothesis holds.
4. The text-line line predicts 0.43–1.18 more width/height than the numeric median at every chars value from 1 to 9.
5. Short non-numeric crops have no clean line (R² 0.20, long upper tail). Their median fit (0.406·chars + 0.932) is numeric-like.
6. Under 0.5, short numeric crops are DROP 5.2% and UNCERTAIN 10.9% ("no detected row" 10.4%). Short non-numeric are DROP 16.3%, mostly "too little OCR" (13.5%).
7. Of the 18 false rejects on the 150 under 0.8, 11 are short: 5 numeric and 6 non-numeric. On the 888, 9 of 22 are short non-numeric and none is short numeric.
8. Three of the six owner-fine short numeric drops sit in the central numeric band ("29)" at the 9th percentile, "54.296" at the 34th, "670" at the 63rd). Two are high ("270" 93rd, "37" 94th) and one is extreme ("3.237.787" 99.9th, letter-spaced digits).
9. Short non-numeric types in the uniform sample of 120: word_or_phrase 43, heading_caps_display 24, abbreviation_reference_label 14 and roman_numeral_lowercase 2, which are legitimate printed lines (83, 69%); punctuation_only 13; and 24 (20%) segmentation faults or non-text.
10. The owner-good short non-numeric drops are mostly letter-spaced or display headings in capitals (10 of 18). Full-line crops whose Google text is 1–2 words (text_covers_part_of_crop) are 25 of the 30 owner-bad rated rows, and 0.5 drops all of them.

CELLS-OPUS: done | populations: census n=592466, W1 n=101098, 888 n=888, 150 n=150 | short numeric n=36307 slope 0.460 vs text slope 0.385 | short non-numeric types: word_or_phrase:43, heading_caps_display:24, abbreviation_reference_label:14, punctuation_only:13, noise_non_text:8, cut_fragment:4, foreign_script_printed:3, handwriting:3, map_figure_ornament_logo:2, roman_numeral_lowercase:2, text_covers_part_of_crop:2, show_through_mirrored:1, multi_line_crop:1 | samples 329
