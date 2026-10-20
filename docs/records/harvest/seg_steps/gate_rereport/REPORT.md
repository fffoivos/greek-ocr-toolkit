# SEG re-report after content gate 0.3 exclusions

**Headline:** 150 → 137; 888 → 819; 250 cells → 213; 417 typology → 284; band population 500 → 420. The primary numeric best 2×2 cell changes to **s4/text-font**; the all-ink box still helps both numeric and non-numeric rows. The selected equal-cost band moves to **0.30–1.95 overall**, **0.35–1.70 numeric**. These are re-report results and flags, with no policy or expectation changes.

Only saved verdicts, measurements, reader answers and owner marks from steps 1–5 were used. No reader, segmentation/native service, detector, predictor or `Pipeline.evaluate` ran. The original finite-set scores, fits, 2×2 and entire step-5 grid reproduce exactly before filtering. The only executed gate is the shared `line_pipeline.py` metadata/text helper; step-5 uses the unchanged pure functions in `band_sweep.py`. All writes are confined to this directory.

## Authority, expectations and denominators

The gate calls `inventory(raw_text, codec)`, `expectations(row, metadata)` and `content_gate_exclusion(...)` with this checkout’s gate 0.3 code and codec. Page override > book declaration > `adm.expected_policy` is preserved. The saved step-1 input objects carry no books/pages metadata declarations, so the supplied metadata mapping is empty and all finite rows resolve through the pipeline’s source policy. Original source/class/wave fields are retained. Cells source/wave are restored from `cells/samples.jsonl`, joined on ID and exact raw text/crop hash; typology source/wave come from its manifest, supplemental numeric source/wave from cells_opus samples. Missing book/page keys use the existing stable ID components as in gate03 part2_analysis.py. No language or expected script is inferred from OCR text. See [row decisions](row_decisions.jsonl) for each resolved expectation, provenance and reason.

Every evaluation set resolves through source policy for all its entries (resolution counts in [summary.json](summary.json)); unresolved expectations: **0**. Such rows would be retained and listed in [unresolved_expectations.json](unresolved_expectations.json). Crop dimensions use original crop_bbox where present, otherwise the SHA-verified bound PNG header; 1744 distinct header-backed paths were hash checked. No ink/detector bbox or rotation is used for the content gate.

`mixed` means mixed-script-word DROP; `foreign` means unexpected-script HOLD with no mixed-word priority. The four part-2 reasons run after these. **Mixed/foreign only** removes part 1 alone. **Part 2 only** independently applies `short_line_exclusion` to every row, including overlaps with part 1; it is not the residual part-2 count. **All** removes the union with actual pipeline precedence. Part-2 counts after precedence make the headline sum additive. Final-eligibility diagnostics such as nonletter_fraction or ≥4-digit numeric rules are not added to this early gate.

| Set | Before → all after | Mixed/foreign only after (m+f) | Part 2 only after | Part 2 only reasons | Part 2 after part-1 precedence |
| --- | --- | --- | --- | --- | --- |
| segeval1 | 150 → 137 | 150 → 147 (1+2) | 150 → 140 | {'short_line': 3, 'single_character_cell': 7} | {'short_line': 3, 'single_character_cell': 7} |
| calibration | 888 → 819 | 888 → 868 (10+10) | 888 → 837 | {'short_line': 44, 'single_character_cell': 6, 'numeric_shape': 1} | {'short_line': 42, 'single_character_cell': 6, 'numeric_shape': 1} |
| cells | 250 → 213 | 250 → 249 (0+1) | 250 → 214 | {'single_character_cell': 36} | {'single_character_cell': 36} |
| typology | 417 → 284 | 417 → 391 (3+23) | 417 → 301 | {'short_line': 54, 'single_character_cell': 62} | {'short_line': 50, 'single_character_cell': 57} |
| owner_marks | 235 → 191 | 235 → 232 (1+2) | 235 → 193 | {'single_character_cell': 38, 'short_line': 3, 'numeric_shape': 1} | {'single_character_cell': 38, 'short_line': 2, 'numeric_shape': 1} |
| rated_888 | 135 → 91 | 135 → 128 (2+5) | 135 → 96 | {'short_line': 37, 'single_character_cell': 1, 'numeric_shape': 1} | {'short_line': 35, 'single_character_cell': 1, 'numeric_shape': 1} |
| typology_marked | 185 → 176 | 185 → 181 (1+3) | 185 → 179 | {'short_line': 6} | {'short_line': 5} |
| small | 642 → 508 | 642 → 619 (1+22) | 642 → 526 | {'single_character_cell': 116} | {'single_character_cell': 111} |
| band_population | 500 → 420 | 500 → 488 (4+8) | 500 → 429 | {'short_line': 31, 'single_character_cell': 39, 'numeric_shape': 1} | {'short_line': 28, 'single_character_cell': 39, 'numeric_shape': 1} |
| changed_lines | 59 → 38 | 59 → 57 (2+0) | 59 → 39 | {'short_line': 6, 'single_character_cell': 13, 'numeric_shape': 1} | {'short_line': 5, 'single_character_cell': 13, 'numeric_shape': 1} |
| sheet | 279 → 199 | 279 → 267 (2+10) | 279 → 205 | {'single_character_cell': 62, 'short_line': 11, 'numeric_shape': 1} | {'single_character_cell': 57, 'short_line': 10, 'numeric_shape': 1} |
| numeric_fit | 383 → 319 | 383 → 383 (0+0) | 383 → 319 | {'single_character_cell': 64} | {'single_character_cell': 64} |
| two_by_two | 304 → 263 | 304 → 302 (0+2) | 304 → 265 | {'single_character_cell': 39} | {'single_character_cell': 39} |

`cell_status_unresolved` = 0 in every set. The small table counts saved cohort entries (including overlaps); other tables identify unique-ID pools explicitly. Full excluded IDs, outcome, words/scripts and untruncated raw text, **per set**, are in [GATE_EXCLUSIONS.md](GATE_EXCLUSIONS.md) and [gate_failed.jsonl](gate_failed.jsonl).

## Step scores — every value before → after

150 uses the saved gate2 owner state: DROP/fine=FP, KEEP/faulty=FN, all UNCERTAIN counted. The 888 agreement uses only explicit ratings. Owner marks retain the latest timestamp, then file order, once per distinct ID (240 historical entries, 235 unique marks). Cells have no inferred labels and are reported by saved verdict counts. Typology excludes all 20 controls and scores explicit owner marks only; intermediate s1/s2 typology verdicts were never saved.

### Mixed/foreign only

| Metric | 0.8 | 0.9-s1 | 0.9-s2 | 0.9-s3 | 0.9-s4 |
| --- | --- | --- | --- | --- | --- |
| 150 FP/FN/UNC; new denominator 147 | 18/14/11 → 17/14/11 | 17/14/11 → 16/14/11 | 17/14/5 → 16/14/5 | 17/15/5 → 16/15/5 | 16/15/0 → 15/15/0 |
| 888 rated agreement / rated n | 94/135 → 89/128 | 95/135 → 90/128 | 105/135 → 100/128 | 105/135 → 100/128 | 109/135 → 104/128 |
| Owner marks agreement / distinct marked n | 155/235 → 153/232 | 156/235 → 154/232 | 169/235 → 167/232 | 170/235 → 168/232 | 189/235 → 187/232 |
| 250 cells KEEP/DROP/UNC; new denominator 249 | 184/6/60 → 183/6/60 | 184/6/60 → 183/6/60 | 212/8/30 → 211/8/30 | 212/8/30 → 211/8/30 | 230/15/5 → 229/15/5 |
| Typology owner agreement / marked n | 131/185 → 128/181 | not saved | not saved | 147/185 → 143/181 | 160/185 → 156/181 |

| Typology final_type | Bed n before → after | Owner n before → after | 0.8 agreement | s3 agreement | s4 agreement |
| --- | --- | --- | --- | --- | --- |
| abbrev_label | 46 → 45 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| caps_display | 77 → 72 | 66 → 63 | 36 → 33 | 43 → 40 | 51 → 48 |
| cut_fragment | 18 → 15 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| digits_letters | 5 → 5 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| figure_ornament | 12 → 12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| foreign_script | 5 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| handwriting | 18 → 15 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| marker | 10 → 9 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| multi_line | 31 → 31 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| noise | 7 → 5 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| number | 5 → 4 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| part_of_line | 5 → 5 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| punctuation | 53 → 50 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| roman_lower | 2 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| show_through | 2 → 1 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| watermark | 2 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| word | 119 → 118 | 119 → 118 | 95 → 95 | 104 → 103 | 109 → 108 |

### Part 2 only (independent length ablation)

| Metric | 0.8 | 0.9-s1 | 0.9-s2 | 0.9-s3 | 0.9-s4 |
| --- | --- | --- | --- | --- | --- |
| 150 FP/FN/UNC; new denominator 140 | 18/14/11 → 17/14/6 | 17/14/11 → 16/14/6 | 17/14/5 → 16/14/0 | 17/15/5 → 16/15/0 | 16/15/0 → 12/15/0 |
| 888 rated agreement / rated n | 94/135 → 66/96 | 95/135 → 67/96 | 105/135 → 77/96 | 105/135 → 77/96 | 109/135 → 81/96 |
| Owner marks agreement / distinct marked n | 155/235 → 133/193 | 156/235 → 134/193 | 169/235 → 145/193 | 170/235 → 146/193 | 189/235 → 159/193 |
| 250 cells KEEP/DROP/UNC; new denominator 214 | 184/6/60 → 165/2/47 | 184/6/60 → 165/2/47 | 212/8/30 → 190/4/20 | 212/8/30 → 190/4/20 | 230/15/5 → 206/3/5 |
| Typology owner agreement / marked n | 131/185 → 127/179 | not saved | not saved | 147/185 → 143/179 | 160/185 → 156/179 |

| Typology final_type | Bed n before → after | Owner n before → after | 0.8 agreement | s3 agreement | s4 agreement |
| --- | --- | --- | --- | --- | --- |
| abbrev_label | 46 → 45 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| caps_display | 77 → 66 | 66 → 60 | 36 → 32 | 43 → 39 | 51 → 47 |
| cut_fragment | 18 → 15 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| digits_letters | 5 → 5 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| figure_ornament | 12 → 9 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| foreign_script | 5 → 3 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| handwriting | 18 → 17 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| marker | 10 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| multi_line | 31 → 8 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| noise | 7 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| number | 5 → 5 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| part_of_line | 5 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| punctuation | 53 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| roman_lower | 2 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| show_through | 2 → 1 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| watermark | 2 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| word | 119 → 119 | 119 → 119 | 95 → 95 | 104 → 104 | 109 → 109 |

### All exclusions — headline

| Metric | 0.8 | 0.9-s1 | 0.9-s2 | 0.9-s3 | 0.9-s4 |
| --- | --- | --- | --- | --- | --- |
| 150 FP/FN/UNC; new denominator 137 | 18/14/11 → 16/14/6 | 17/14/11 → 15/14/6 | 17/14/5 → 15/14/0 | 17/15/5 → 15/15/0 | 16/15/0 → 11/15/0 |
| 888 rated agreement / rated n | 94/135 → 62/91 | 95/135 → 63/91 | 105/135 → 73/91 | 105/135 → 73/91 | 109/135 → 77/91 |
| Owner marks agreement / distinct marked n | 155/235 → 131/191 | 156/235 → 132/191 | 169/235 → 143/191 | 170/235 → 144/191 | 189/235 → 157/191 |
| 250 cells KEEP/DROP/UNC; new denominator 213 | 184/6/60 → 164/2/47 | 184/6/60 → 164/2/47 | 212/8/30 → 189/4/20 | 212/8/30 → 189/4/20 | 230/15/5 → 205/3/5 |
| Typology owner agreement / marked n | 131/185 → 125/176 | not saved | not saved | 147/185 → 140/176 | 160/185 → 153/176 |

| Typology final_type | Bed n before → after | Owner n before → after | 0.8 agreement | s3 agreement | s4 agreement |
| --- | --- | --- | --- | --- | --- |
| abbrev_label | 46 → 44 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| caps_display | 77 → 64 | 66 → 58 | 36 → 30 | 43 → 37 | 51 → 45 |
| cut_fragment | 18 → 13 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| digits_letters | 5 → 5 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| figure_ornament | 12 → 9 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| foreign_script | 5 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| handwriting | 18 → 14 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| marker | 10 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| multi_line | 31 → 8 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| noise | 7 → 1 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| number | 5 → 4 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| part_of_line | 5 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| punctuation | 53 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| roman_lower | 2 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| show_through | 2 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| watermark | 2 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| word | 119 → 118 | 119 → 118 | 95 → 95 | 104 → 103 | 109 → 108 |

## Step 4: both halves of the 2×2 and numeric refits

Output type is exactly common.py, distinct from script failure: its `mixed` output type means a small number of letters with digits, not a mixed-script word. The primary table filters the **saved 2×2 verdicts**, without changing their fitted expectations. The secondary refit table uses newly fitted numeric coefficients on the saved gate/box/padding only. Its pure decision arithmetic reproduces every original numeric counterfactual before filtering. Neither table reruns segmentation.

### Mixed/foreign only: saved 2×2

Fit: **without_owner**. Numeric n<30 flag applies to numeric evaluation cells; mixed is separately indicative with only three rows. Non-numeric is an equal decision input.

| Type | Box / expectation | n before → after | Agreement before → after | Flag |
| --- | --- | --- | --- | --- |
| numeric | s3/text-font | 144 → 144 | 111/144 → 111/144 | none |
| numeric | s4/text-font | 144 → 144 | 127/144 → 127/144 | none |
| numeric | s3/short-numeric | 144 → 144 | 111/144 → 111/144 | none |
| numeric | s4/short-numeric | 144 → 144 | 132/144 → 132/144 | none |
| mixed | s3/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s3/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| non-numeric | s3/text-font | 157 → 155 | 120/157 → 118/155 | none |
| non-numeric | s4/text-font | 157 → 155 | 137/157 → 135/155 | none |
| non-numeric | s3/short-numeric | 157 → 155 | 124/157 → 122/155 | none |
| non-numeric | s4/short-numeric | 157 → 155 | 137/157 → 135/155 | none |

Fit: **all**. Numeric n<30 flag applies to numeric evaluation cells; mixed is separately indicative with only three rows. Non-numeric is an equal decision input.

| Type | Box / expectation | n before → after | Agreement before → after | Flag |
| --- | --- | --- | --- | --- |
| numeric | s3/text-font | 144 → 144 | 111/144 → 111/144 | none |
| numeric | s4/text-font | 144 → 144 | 127/144 → 127/144 | none |
| numeric | s3/short-numeric | 144 → 144 | 109/144 → 109/144 | none |
| numeric | s4/short-numeric | 144 → 144 | 131/144 → 131/144 | none |
| mixed | s3/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s3/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| non-numeric | s3/text-font | 157 → 155 | 120/157 → 118/155 | none |
| non-numeric | s4/text-font | 157 → 155 | 137/157 → 135/155 | none |
| non-numeric | s3/short-numeric | 157 → 155 | 123/157 → 121/155 | none |
| non-numeric | s4/short-numeric | 157 → 155 | 138/157 → 136/155 | none |

### Mixed/foreign only: numeric refits

| Box | Fit | n before → after | a | b | Residual SD (ddof=2) | MAD |
| --- | --- | --- | --- | --- | --- | --- |
| s3 | all | 383 → 383 | 0.5231866 → 0.5231866 | 0.4765284 → 0.4765284 | 0.64484054 → 0.64484054 | 0.35075421 → 0.35075421 |
| s3 | without_owner | 239 → 239 | 0.56415509 → 0.56415509 | 0.30110696 → 0.30110696 | 0.62606848 → 0.62606848 | 0.30834527 → 0.30834527 |
| s4 | all | 383 → 383 | 0.58726792 → 0.58726792 | 0.18882083 → 0.18882083 | 0.59531236 → 0.59531236 | 0.21657823 → 0.21657823 |
| s4 | without_owner | 239 → 239 | 0.60753943 → 0.60753943 | 0.12114942 → 0.12114942 | 0.60906342 → 0.60906342 | 0.20535386 → 0.20535386 |

OLS fits ratio = a·saved_chars+b. S3 ratio=max(frame length,height)/min; S4 ratio=all-component width/height. Unscaled MAD is about the residual median. All local small numeric IDs, including saved supplemental crops and typology controls if eligible, are fitted once; without_owner excludes every owner mark/rating ID. [summary.json](summary.json) retains all fit IDs.

| Refitted 2×2 type | Fit | Cell | n before → after | Agreement before → after |
| --- | --- | --- | --- | --- |
| numeric | without_owner | s3/text-font | 144 → 144 | 111/144 → 111/144 |
| numeric | without_owner | s4/text-font | 144 → 144 | 127/144 → 127/144 |
| numeric | without_owner | s3/short-numeric | 144 → 144 | 111/144 → 111/144 |
| numeric | without_owner | s4/short-numeric | 144 → 144 | 132/144 → 132/144 |
| mixed | without_owner | s3/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s4/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s3/short-numeric | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s4/short-numeric | 3 → 3 | 3/3 → 3/3 |
| non-numeric | without_owner | s3/text-font | 157 → 155 | 120/157 → 118/155 |
| non-numeric | without_owner | s4/text-font | 157 → 155 | 137/157 → 135/155 |
| non-numeric | without_owner | s3/short-numeric | 157 → 155 | 124/157 → 122/155 |
| non-numeric | without_owner | s4/short-numeric | 157 → 155 | 137/157 → 135/155 |
| numeric | all | s3/text-font | 144 → 144 | 111/144 → 111/144 |
| numeric | all | s4/text-font | 144 → 144 | 127/144 → 127/144 |
| numeric | all | s3/short-numeric | 144 → 144 | 109/144 → 109/144 |
| numeric | all | s4/short-numeric | 144 → 144 | 131/144 → 131/144 |
| mixed | all | s3/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s4/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s3/short-numeric | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s4/short-numeric | 3 → 3 | 3/3 → 3/3 |
| non-numeric | all | s3/text-font | 157 → 155 | 120/157 → 118/155 |
| non-numeric | all | s4/text-font | 157 → 155 | 137/157 → 135/155 |
| non-numeric | all | s3/short-numeric | 157 → 155 | 123/157 → 121/155 |
| non-numeric | all | s4/short-numeric | 157 → 155 | 138/157 → 136/155 |

### Part 2 only (independent length ablation): saved 2×2

Fit: **without_owner**. Numeric n<30 flag applies to numeric evaluation cells; mixed is separately indicative with only three rows. Non-numeric is an equal decision input.

| Type | Box / expectation | n before → after | Agreement before → after | Flag |
| --- | --- | --- | --- | --- |
| numeric | s3/text-font | 144 → 110 | 111/144 → 91/110 | none |
| numeric | s4/text-font | 144 → 110 | 127/144 → 103/110 | none |
| numeric | s3/short-numeric | 144 → 110 | 111/144 → 91/110 | none |
| numeric | s4/short-numeric | 144 → 110 | 132/144 → 102/110 | none |
| mixed | s3/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s3/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| non-numeric | s3/text-font | 157 → 152 | 120/157 → 118/152 | none |
| non-numeric | s4/text-font | 157 → 152 | 137/157 → 133/152 | none |
| non-numeric | s3/short-numeric | 157 → 152 | 124/157 → 123/152 | none |
| non-numeric | s4/short-numeric | 157 → 152 | 137/157 → 133/152 | none |

Fit: **all**. Numeric n<30 flag applies to numeric evaluation cells; mixed is separately indicative with only three rows. Non-numeric is an equal decision input.

| Type | Box / expectation | n before → after | Agreement before → after | Flag |
| --- | --- | --- | --- | --- |
| numeric | s3/text-font | 144 → 110 | 111/144 → 91/110 | none |
| numeric | s4/text-font | 144 → 110 | 127/144 → 103/110 | none |
| numeric | s3/short-numeric | 144 → 110 | 109/144 → 89/110 | none |
| numeric | s4/short-numeric | 144 → 110 | 131/144 → 103/110 | none |
| mixed | s3/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s3/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| non-numeric | s3/text-font | 157 → 152 | 120/157 → 118/152 | none |
| non-numeric | s4/text-font | 157 → 152 | 137/157 → 133/152 | none |
| non-numeric | s3/short-numeric | 157 → 152 | 123/157 → 122/152 | none |
| non-numeric | s4/short-numeric | 157 → 152 | 138/157 → 134/152 | none |

### Part 2 only (independent length ablation): numeric refits

| Box | Fit | n before → after | a | b | Residual SD (ddof=2) | MAD |
| --- | --- | --- | --- | --- | --- | --- |
| s3 | all | 383 → 319 | 0.5231866 → 0.59313588 | 0.4765284 → 0.11458814 | 0.64484054 → 0.61546613 | 0.35075421 → 0.26274179 |
| s3 | without_owner | 239 → 209 | 0.56415509 → 0.60509549 | 0.30110696 → 0.09618915 | 0.62606848 → 0.61093425 | 0.30834527 → 0.2405864 |
| s4 | all | 383 → 319 | 0.58726792 → 0.59563386 | 0.18882083 → 0.15739207 | 0.59531236 → 0.60304741 | 0.21657823 → 0.21714699 |
| s4 | without_owner | 239 → 209 | 0.60753943 → 0.6086058 | 0.12114942 → 0.130589 | 0.60906342 → 0.62255107 | 0.20535386 → 0.19706221 |

OLS fits ratio = a·saved_chars+b. S3 ratio=max(frame length,height)/min; S4 ratio=all-component width/height. Unscaled MAD is about the residual median. All local small numeric IDs, including saved supplemental crops and typology controls if eligible, are fitted once; without_owner excludes every owner mark/rating ID. [summary.json](summary.json) retains all fit IDs.

| Refitted 2×2 type | Fit | Cell | n before → after | Agreement before → after |
| --- | --- | --- | --- | --- |
| numeric | without_owner | s3/text-font | 144 → 110 | 111/144 → 91/110 |
| numeric | without_owner | s4/text-font | 144 → 110 | 127/144 → 103/110 |
| numeric | without_owner | s3/short-numeric | 144 → 110 | 111/144 → 92/110 |
| numeric | without_owner | s4/short-numeric | 144 → 110 | 132/144 → 102/110 |
| mixed | without_owner | s3/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s4/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s3/short-numeric | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s4/short-numeric | 3 → 3 | 3/3 → 3/3 |
| non-numeric | without_owner | s3/text-font | 157 → 152 | 120/157 → 118/152 |
| non-numeric | without_owner | s4/text-font | 157 → 152 | 137/157 → 133/152 |
| non-numeric | without_owner | s3/short-numeric | 157 → 152 | 124/157 → 123/152 |
| non-numeric | without_owner | s4/short-numeric | 157 → 152 | 137/157 → 133/152 |
| numeric | all | s3/text-font | 144 → 110 | 111/144 → 91/110 |
| numeric | all | s4/text-font | 144 → 110 | 127/144 → 103/110 |
| numeric | all | s3/short-numeric | 144 → 110 | 109/144 → 92/110 |
| numeric | all | s4/short-numeric | 144 → 110 | 131/144 → 103/110 |
| mixed | all | s3/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s4/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s3/short-numeric | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s4/short-numeric | 3 → 3 | 3/3 → 3/3 |
| non-numeric | all | s3/text-font | 157 → 152 | 120/157 → 118/152 |
| non-numeric | all | s4/text-font | 157 → 152 | 137/157 → 133/152 |
| non-numeric | all | s3/short-numeric | 157 → 152 | 123/157 → 123/152 |
| non-numeric | all | s4/short-numeric | 157 → 152 | 138/157 → 134/152 |

### All exclusions — headline: saved 2×2

Fit: **without_owner**. Numeric n<30 flag applies to numeric evaluation cells; mixed is separately indicative with only three rows. Non-numeric is an equal decision input.

| Type | Box / expectation | n before → after | Agreement before → after | Flag |
| --- | --- | --- | --- | --- |
| numeric | s3/text-font | 144 → 110 | 111/144 → 91/110 | none |
| numeric | s4/text-font | 144 → 110 | 127/144 → 103/110 | none |
| numeric | s3/short-numeric | 144 → 110 | 111/144 → 91/110 | none |
| numeric | s4/short-numeric | 144 → 110 | 132/144 → 102/110 | none |
| mixed | s3/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s3/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| non-numeric | s3/text-font | 157 → 150 | 120/157 → 116/150 | none |
| non-numeric | s4/text-font | 157 → 150 | 137/157 → 131/150 | none |
| non-numeric | s3/short-numeric | 157 → 150 | 124/157 → 121/150 | none |
| non-numeric | s4/short-numeric | 157 → 150 | 137/157 → 131/150 | none |

Fit: **all**. Numeric n<30 flag applies to numeric evaluation cells; mixed is separately indicative with only three rows. Non-numeric is an equal decision input.

| Type | Box / expectation | n before → after | Agreement before → after | Flag |
| --- | --- | --- | --- | --- |
| numeric | s3/text-font | 144 → 110 | 111/144 → 91/110 | none |
| numeric | s4/text-font | 144 → 110 | 127/144 → 103/110 | none |
| numeric | s3/short-numeric | 144 → 110 | 109/144 → 89/110 | none |
| numeric | s4/short-numeric | 144 → 110 | 131/144 → 103/110 | none |
| mixed | s3/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/text-font | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s3/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| mixed | s4/short-numeric | 3 → 3 | 3/3 → 3/3 | 3 mixed crops → indicative only |
| non-numeric | s3/text-font | 157 → 150 | 120/157 → 116/150 | none |
| non-numeric | s4/text-font | 157 → 150 | 137/157 → 131/150 | none |
| non-numeric | s3/short-numeric | 157 → 150 | 123/157 → 120/150 | none |
| non-numeric | s4/short-numeric | 157 → 150 | 138/157 → 132/150 | none |

### All exclusions — headline: numeric refits

| Box | Fit | n before → after | a | b | Residual SD (ddof=2) | MAD |
| --- | --- | --- | --- | --- | --- | --- |
| s3 | all | 383 → 319 | 0.5231866 → 0.59313588 | 0.4765284 → 0.11458814 | 0.64484054 → 0.61546613 | 0.35075421 → 0.26274179 |
| s3 | without_owner | 239 → 209 | 0.56415509 → 0.60509549 | 0.30110696 → 0.09618915 | 0.62606848 → 0.61093425 | 0.30834527 → 0.2405864 |
| s4 | all | 383 → 319 | 0.58726792 → 0.59563386 | 0.18882083 → 0.15739207 | 0.59531236 → 0.60304741 | 0.21657823 → 0.21714699 |
| s4 | without_owner | 239 → 209 | 0.60753943 → 0.6086058 | 0.12114942 → 0.130589 | 0.60906342 → 0.62255107 | 0.20535386 → 0.19706221 |

OLS fits ratio = a·saved_chars+b. S3 ratio=max(frame length,height)/min; S4 ratio=all-component width/height. Unscaled MAD is about the residual median. All local small numeric IDs, including saved supplemental crops and typology controls if eligible, are fitted once; without_owner excludes every owner mark/rating ID. [summary.json](summary.json) retains all fit IDs.

| Refitted 2×2 type | Fit | Cell | n before → after | Agreement before → after |
| --- | --- | --- | --- | --- |
| numeric | without_owner | s3/text-font | 144 → 110 | 111/144 → 91/110 |
| numeric | without_owner | s4/text-font | 144 → 110 | 127/144 → 103/110 |
| numeric | without_owner | s3/short-numeric | 144 → 110 | 111/144 → 92/110 |
| numeric | without_owner | s4/short-numeric | 144 → 110 | 132/144 → 102/110 |
| mixed | without_owner | s3/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s4/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s3/short-numeric | 3 → 3 | 3/3 → 3/3 |
| mixed | without_owner | s4/short-numeric | 3 → 3 | 3/3 → 3/3 |
| non-numeric | without_owner | s3/text-font | 157 → 150 | 120/157 → 116/150 |
| non-numeric | without_owner | s4/text-font | 157 → 150 | 137/157 → 131/150 |
| non-numeric | without_owner | s3/short-numeric | 157 → 150 | 124/157 → 121/150 |
| non-numeric | without_owner | s4/short-numeric | 157 → 150 | 137/157 → 131/150 |
| numeric | all | s3/text-font | 144 → 110 | 111/144 → 91/110 |
| numeric | all | s4/text-font | 144 → 110 | 127/144 → 103/110 |
| numeric | all | s3/short-numeric | 144 → 110 | 109/144 → 92/110 |
| numeric | all | s4/short-numeric | 144 → 110 | 131/144 → 103/110 |
| mixed | all | s3/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s4/text-font | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s3/short-numeric | 3 → 3 | 3/3 → 3/3 |
| mixed | all | s4/short-numeric | 3 → 3 | 3/3 → 3/3 |
| non-numeric | all | s3/text-font | 157 → 150 | 120/157 → 116/150 |
| non-numeric | all | s4/text-font | 157 → 150 | 137/157 → 131/150 |
| non-numeric | all | s3/short-numeric | 157 → 150 | 123/157 → 121/150 |
| non-numeric | all | s4/short-numeric | 157 → 150 | 138/157 → 132/150 |

### Small row survival by output type

The ready line uses **unique evaluated small IDs in s4/small.jsonl**, with overlapping cohorts deduplicated. The local numeric fit adds supplemental crops and therefore has a larger numeric n. The owner-judged 2×2 subset is shown separately.

| Population | Output type | Before | Mixed/foreign only after | Part-2 only after | All after |
| --- | --- | --- | --- | --- | --- |
| cohort_entries | numeric | 251 | 251 | 210 | 210 |
| cohort_entries | mixed | 38 | 35 | 38 | 35 |
| cohort_entries | non-numeric | 353 | 333 | 278 | 263 |
| unique_evaluation_small | numeric | 249 | 249 | 208 | 208 |
| unique_evaluation_small | mixed | 37 | 34 | 37 | 34 |
| unique_evaluation_small | non-numeric | 327 | 308 | 257 | 243 |
| All local small crop pool (incl supplemental) | numeric | 383 | 383 | 319 | 319 |
| All local small crop pool (incl supplemental) | mixed | 37 | 34 | 37 | 34 |
| All local small crop pool (incl supplemental) | non-numeric | 327 | 308 | 257 | 243 |
| Owner-judged 2×2 | numeric | 144 | 144 | 110 | 110 |
| Owner-judged 2×2 | mixed | 3 | 3 | 3 | 3 |
| Owner-judged 2×2 | non-numeric | 157 | 155 | 152 | 150 |

Saved no-main/box abstentions moved by S4, after the content gate: segeval1 5 → 0, calibration 7 → 5, cells 25 → 15, typology 51 → 20. Main replay total 37 → 20. Surviving moved rows retain their saved counterfactual UNCERTAIN without the S4 ruling.

## Step 5: sweep and fixed candidate bands

The supplied quick estimate says 495 band rows; the actual immutable band_population.jsonl contains **500** and the saved build receipt/report also says 500. Likewise, script-only removals are 4 mixed + 8 foreign, not the estimate 4+2. The gate removes 80 total rows. All counts below retain the same objective and tie rule: false drops + false keeps, excluding only owner-DROP notes that length cannot assess; then nearest 0.50–1.50, lower L, lower U. The entire original grid matches sweep.json before filtering.

### Mixed/foreign only

| Group | Fixed band | fd/fk before → after; new denominator |
| --- | --- | --- |
| overall | 0.50-1.50 | 59/16 (total 75; objective n=490; population n=500; blind kept 8/10) → 57/16 (total 73; objective n=479; population n=488; blind kept 7/9) |
| overall | 0.30-2.00 | 10/24 (total 34; objective n=490; population n=500; blind kept 10/10) → 9/23 (total 32; objective n=479; population n=488; blind kept 9/9) |
| overall | 0.35-2.00 | 12/23 (total 35; objective n=490; population n=500; blind kept 10/10) → 11/22 (total 33; objective n=479; population n=488; blind kept 9/9) |
| overall | 0.55-1.30 | 84/11 (total 95; objective n=490; population n=500; blind kept 8/10) → 82/11 (total 93; objective n=479; population n=488; blind kept 7/9) |
| numeric | 0.50-1.50 | 15/3 (total 18; objective n=168; population n=171; blind kept 2/3) → 15/3 (total 18; objective n=168; population n=171; blind kept 2/3) |
| numeric | 0.30-2.00 | 2/3 (total 5; objective n=168; population n=171; blind kept 3/3) → 2/3 (total 5; objective n=168; population n=171; blind kept 3/3) |
| numeric | 0.35-2.00 | 2/3 (total 5; objective n=168; population n=171; blind kept 3/3) → 2/3 (total 5; objective n=168; population n=171; blind kept 3/3) |
| numeric | 0.55-1.30 | 22/3 (total 25; objective n=168; population n=171; blind kept 2/3) → 22/3 (total 25; objective n=168; population n=171; blind kept 2/3) |

| Sweep group | Mode | Best band before → after | ΔL / ΔU | Minimum errors / objective n before → after |
| --- | --- | --- | --- | --- |
| overall | length_alone | 0.30–2.00 → 0.30–2.00 | +0.00 / +0.00 | 36/490 → 33/479 |
| overall | end_to_end | 0.30–2.00 → 0.30–2.00 | +0.00 / +0.00 | 34/490 → 32/479 |
| numeric | length_alone | 0.35–2.00 → 0.35–2.00 | +0.00 / +0.00 | 6/168 → 6/168 |
| numeric | end_to_end | 0.35–2.00 → 0.35–2.00 | +0.00 / +0.00 | 5/168 → 5/168 |
| non-numeric | length_alone | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 30/318 → 27/307 |
| non-numeric | end_to_end | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 29/318 → 27/307 |
| mixed | length_alone | 0.50–1.50 → 0.50–1.50 | +0.00 / +0.00 | 0/4 → 0/4 |
| mixed | end_to_end | 0.50–1.50 → 0.50–1.50 | +0.00 / +0.00 | 0/4 → 0/4 |
| small | length_alone | 0.40–2.00 → 0.40–2.00 | +0.00 / +0.00 | 14/295 → 14/293 |
| small | end_to_end | 0.35–2.00 → 0.35–2.00 | +0.00 / +0.00 | 13/295 → 13/293 |
| non-small | length_alone | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 22/195 → 19/186 |
| non-small | end_to_end | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 21/195 → 19/186 |

| Unequal-cost group | w before → after | Best band before → after | ΔL / ΔU | fd/fk before → after |
| --- | --- | --- | --- | --- |
| overall | 1 → 1 | 0.30–2.00 → 0.30–2.00 | +0.00 / +0.00 | 10/24 → 9/23 |
| overall | 2 → 2 | 0.35–2.00 → 0.35–2.00 | +0.00 / +0.00 | 12/23 → 11/22 |
| overall | 3 → 3 | 0.35–1.85 → 0.35–1.85 | +0.00 / +0.00 | 15/22 → 14/21 |
| overall | 7.75 → 8.04 | 0.55–1.30 → 0.55–1.25 | +0.00 / -0.05 | 84/11 → 90/10 |
| numeric | 1 → 1 | 0.35–2.00 → 0.35–2.00 | +0.00 / +0.00 | 2/3 → 2/3 |
| numeric | 2 → 2 | 0.35–2.00 → 0.35–2.00 | +0.00 / +0.00 | 2/3 → 2/3 |
| numeric | 3 → 3 | 0.35–2.00 → 0.35–2.00 | +0.00 / +0.00 | 2/3 → 2/3 |
| numeric | 32.6 → 32.6 | 0.35–1.25 → 0.35–1.25 | +0.00 / +0.00 | 21/2 → 21/2 |

| Class-balanced fit group | Weight before → after | Best band before → after | fd/fk before → after |
| --- | --- | --- | --- |
| overall | 7.75 → 8.04 | 0.55–1.30 → 0.55–1.25 | 84/11 → 90/10 |
| numeric | 32.6 → 32.6 | 0.35–1.25 → 0.35–1.25 | 21/2 → 21/2 |

### Part 2 only (independent length ablation)

| Group | Fixed band | fd/fk before → after; new denominator |
| --- | --- | --- |
| overall | 0.50-1.50 | 59/16 (total 75; objective n=490; population n=500; blind kept 8/10) → 39/16 (total 55; objective n=421; population n=429; blind kept 7/8) |
| overall | 0.30-2.00 | 10/24 (total 34; objective n=490; population n=500; blind kept 10/10) → 6/21 (total 27; objective n=421; population n=429; blind kept 8/8) |
| overall | 0.35-2.00 | 12/23 (total 35; objective n=490; population n=500; blind kept 10/10) → 7/21 (total 28; objective n=421; population n=429; blind kept 8/8) |
| overall | 0.55-1.30 | 84/11 (total 95; objective n=490; population n=500; blind kept 8/10) → 57/11 (total 68; objective n=421; population n=429; blind kept 7/8) |
| numeric | 0.50-1.50 | 15/3 (total 18; objective n=168; population n=171; blind kept 2/3) → 5/3 (total 8; objective n=134; population n=136; blind kept 2/2) |
| numeric | 0.30-2.00 | 2/3 (total 5; objective n=168; population n=171; blind kept 3/3) → 2/3 (total 5; objective n=134; population n=136; blind kept 2/2) |
| numeric | 0.35-2.00 | 2/3 (total 5; objective n=168; population n=171; blind kept 3/3) → 2/3 (total 5; objective n=134; population n=136; blind kept 2/2) |
| numeric | 0.55-1.30 | 22/3 (total 25; objective n=168; population n=171; blind kept 2/3) → 7/3 (total 10; objective n=134; population n=136; blind kept 2/2) |

| Sweep group | Mode | Best band before → after | ΔL / ΔU | Minimum errors / objective n before → after |
| --- | --- | --- | --- | --- |
| overall | length_alone | 0.30–2.00 → 0.30–1.95 | +0.00 / -0.05 | 36/490 → 28/421 |
| overall | end_to_end | 0.30–2.00 → 0.30–1.95 | +0.00 / -0.05 | 34/490 → 27/421 |
| numeric | length_alone | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 6/168 → 5/134 |
| numeric | end_to_end | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 5/168 → 5/134 |
| non-numeric | length_alone | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 30/318 → 23/283 |
| non-numeric | end_to_end | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 29/318 → 22/283 |
| mixed | length_alone | 0.50–1.50 → 0.50–1.50 | +0.00 / +0.00 | 0/4 → 0/4 |
| mixed | end_to_end | 0.50–1.50 → 0.50–1.50 | +0.00 / +0.00 | 0/4 → 0/4 |
| small | length_alone | 0.40–2.00 → 0.40–1.85 | +0.00 / -0.15 | 14/295 → 11/256 |
| small | end_to_end | 0.35–2.00 → 0.40–1.85 | +0.05 / -0.15 | 13/295 → 11/256 |
| non-small | length_alone | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 22/195 → 17/165 |
| non-small | end_to_end | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 21/195 → 16/165 |

| Unequal-cost group | w before → after | Best band before → after | ΔL / ΔU | fd/fk before → after |
| --- | --- | --- | --- | --- |
| overall | 1 → 1 | 0.30–2.00 → 0.30–1.95 | +0.00 / -0.05 | 10/24 → 6/21 |
| overall | 2 → 2 | 0.35–2.00 → 0.30–1.85 | -0.05 / -0.15 | 12/23 → 8/20 |
| overall | 3 → 3 | 0.35–1.85 → 0.30–1.85 | -0.05 / +0.00 | 15/22 → 8/20 |
| overall | 7.75 → 11.38 | 0.55–1.30 → 0.55–1.25 | +0.00 / -0.05 | 84/11 → 62/10 |
| numeric | 1 → 1 | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 2/3 → 2/3 |
| numeric | 2 → 2 | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 2/3 → 2/3 |
| numeric | 3 → 3 | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 2/3 → 2/3 |
| numeric | 32.6 → 32.5 | 0.35–1.25 → 0.35–1.25 | +0.00 / +0.00 | 21/2 → 7/2 |

| Class-balanced fit group | Weight before → after | Best band before → after | fd/fk before → after |
| --- | --- | --- | --- |
| overall | 7.75 → 11.38 | 0.55–1.30 → 0.55–1.25 | 84/11 → 62/10 |
| numeric | 32.6 → 32.5 | 0.35–1.25 → 0.35–1.25 | 21/2 → 7/2 |

### All exclusions — headline

| Group | Fixed band | fd/fk before → after; new denominator |
| --- | --- | --- |
| overall | 0.50-1.50 | 59/16 (total 75; objective n=490; population n=500; blind kept 8/10) → 38/16 (total 54; objective n=412; population n=420; blind kept 7/8) |
| overall | 0.30-2.00 | 10/24 (total 34; objective n=490; population n=500; blind kept 10/10) → 5/20 (total 25; objective n=412; population n=420; blind kept 8/8) |
| overall | 0.35-2.00 | 12/23 (total 35; objective n=490; population n=500; blind kept 10/10) → 6/20 (total 26; objective n=412; population n=420; blind kept 8/8) |
| overall | 0.55-1.30 | 84/11 (total 95; objective n=490; population n=500; blind kept 8/10) → 56/11 (total 67; objective n=412; population n=420; blind kept 7/8) |
| numeric | 0.50-1.50 | 15/3 (total 18; objective n=168; population n=171; blind kept 2/3) → 5/3 (total 8; objective n=134; population n=136; blind kept 2/2) |
| numeric | 0.30-2.00 | 2/3 (total 5; objective n=168; population n=171; blind kept 3/3) → 2/3 (total 5; objective n=134; population n=136; blind kept 2/2) |
| numeric | 0.35-2.00 | 2/3 (total 5; objective n=168; population n=171; blind kept 3/3) → 2/3 (total 5; objective n=134; population n=136; blind kept 2/2) |
| numeric | 0.55-1.30 | 22/3 (total 25; objective n=168; population n=171; blind kept 2/3) → 7/3 (total 10; objective n=134; population n=136; blind kept 2/2) |

| Sweep group | Mode | Best band before → after | ΔL / ΔU | Minimum errors / objective n before → after |
| --- | --- | --- | --- | --- |
| overall | length_alone | 0.30–2.00 → 0.30–1.95 | +0.00 / -0.05 | 36/490 → 25/412 |
| overall | end_to_end | 0.30–2.00 → 0.30–1.95 | +0.00 / -0.05 | 34/490 → 25/412 |
| numeric | length_alone | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 6/168 → 5/134 |
| numeric | end_to_end | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 5/168 → 5/134 |
| non-numeric | length_alone | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 30/318 → 20/274 |
| non-numeric | end_to_end | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 29/318 → 20/274 |
| mixed | length_alone | 0.50–1.50 → 0.50–1.50 | +0.00 / +0.00 | 0/4 → 0/4 |
| mixed | end_to_end | 0.50–1.50 → 0.50–1.50 | +0.00 / +0.00 | 0/4 → 0/4 |
| small | length_alone | 0.40–2.00 → 0.40–1.85 | +0.00 / -0.15 | 14/295 → 11/254 |
| small | end_to_end | 0.35–2.00 → 0.40–1.85 | +0.05 / -0.15 | 13/295 → 11/254 |
| non-small | length_alone | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 22/195 → 14/158 |
| non-small | end_to_end | 0.30–1.95 → 0.30–1.95 | +0.00 / +0.00 | 21/195 → 14/158 |

| Unequal-cost group | w before → after | Best band before → after | ΔL / ΔU | fd/fk before → after |
| --- | --- | --- | --- | --- |
| overall | 1 → 1 | 0.30–2.00 → 0.30–1.95 | +0.00 / -0.05 | 10/24 → 5/20 |
| overall | 2 → 2 | 0.35–2.00 → 0.30–1.85 | -0.05 / -0.15 | 12/23 → 7/19 |
| overall | 3 → 3 | 0.35–1.85 → 0.30–1.85 | -0.05 / +0.00 | 15/22 → 7/19 |
| overall | 7.75 → 12.29 | 0.55–1.30 → 0.60–1.25 | +0.05 / -0.05 | 84/11 → 73/9 |
| numeric | 1 → 1 | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 2/3 → 2/3 |
| numeric | 2 → 2 | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 2/3 → 2/3 |
| numeric | 3 → 3 | 0.35–2.00 → 0.35–1.70 | +0.00 / -0.30 | 2/3 → 2/3 |
| numeric | 32.6 → 32.5 | 0.35–1.25 → 0.35–1.25 | +0.00 / +0.00 | 21/2 → 7/2 |

| Class-balanced fit group | Weight before → after | Best band before → after | fd/fk before → after |
| --- | --- | --- | --- |
| overall | 7.75 → 12.29 | 0.55–1.30 → 0.60–1.25 | 84/11 → 73/9 |
| numeric | 32.6 → 32.5 | 0.35–1.25 → 0.35–1.25 | 21/2 → 7/2 |

The headline upper-bound moves are selections among tied optima: the old overall and numeric proposals still attain the new minimum. The substantive equal-cost widening direction survives, while the chosen points and support for numeric generalization change.

### Bound support and short owner-KEEP rows

| Group | Owner KEEP/DROP before → after | Original neighbour support → new selected-point neighbour support |
| --- | --- | --- |
| overall | {'KEEP': 434, 'DROP': 66} → {'KEEP': 381, 'DROP': 39} | [(0.35, 2.0, 3), (0.3, 1.95, 1), (0.3, 2.05, 1)] → [(0.35, 1.95, 1), (0.3, 1.9, 3), (0.3, 2.0, 0)] |
| numeric | {'KEEP': 163, 'DROP': 8} → {'KEEP': 130, 'DROP': 6} | [(0.3, 2.0, 0), (0.4, 2.0, 2), (0.35, 1.95, 1), (0.35, 2.05, 1)] → [(0.3, 1.7, 0), (0.4, 1.7, 1), (0.35, 1.65, 1), (0.35, 1.75, 0)] |

Short owner-KEEP non-small rows outside the current length band: 15 → 8; kept by original overall proposal: 10 → 7. Full IDs in summary.json. The original overall U neighbour 1.95 vs 2.00 loses its sole supporting one-character numeric row; the old and newly selected upper bounds now give identical eligible verdicts.

### Stability after all exclusions

| Group | Check | Before gains → after gains |
| --- | --- | --- |
| overall | split_half | [20, 18] → [14, 13] |
| overall | loso_source_set | [9, 8, 2, 8, 12] → [6, 0, 2, 8, 11] |
| overall | loso_cohort | [13, 8, 10, 8] → [9, 0, 10, 8] |
| numeric | split_half | [3, 6] → [0, 1] |
| numeric | loso_source_set | [1, 6, 0, 0] → [0, 0, 0, 0] |
| numeric | loso_cohort | [1, 6, 0] → [0, 0, 0] |

| Group | Objective n | Bootstrap U 2.5–97.5% | Saved≤0 /1000 | Current tied optimum /1000 | Proposal tied optimum /1000 |
| --- | --- | --- | --- | --- | --- |
| overall | 490 → 412 | 1.75–2.45 → 1.7–2.45 | 0 → 0 | 0 → 0 | 585 → 782 |
| numeric | 168 → 134 | 1.7–2.45 → 1.5–2.45 | 0 → 48 | 0 → 30 | 673 → 657 |

All bootstrap settings remain the saved 1000 resamples, seed 20261019. Full frequencies, ties, per-fold denominators and all grids are in summary.json. Numeric held-out gains shrink to 0–1 and its bootstrap has 48/1000 nonpositive gains; this replaces the previous 0/1000 claim for numerics. Overall still has 0/1000 nonpositive bootstrap gains, but some held-out folds now tie.

### Changed lines: with and without gate-failed rows

Unique original changed lines **59 → 38**, and newly selected best-band changes **38**. The new selected bands produce the same remaining changed-ID union; all group/section memberships stay the same. Full lists: [original](changed_lines_before.jsonl), [filtered at original proposal](changed_lines_filtered_original_band.jsonl), [new best bands](changed_lines.jsonl). Tables below list every original changed line, including excluded lines, so the before/after membership is reviewable.

| Scheme | ID | Raw text | Current | Original proposal | Gate / after membership |
| --- | --- | --- | --- | --- | --- |
| overall | bsb_poly1850--2032df1e3e983f1d--s005-l0029 | PAEONIA | DROP (too little) | KEEP | short_line |
| overall | elstat--0877c813a8512b56--s000-l0114 | Slightly | DROP (too much) | KEEP | survives |
| overall | elstat--0a2c92120843658d--s001-l0216 | 1 | DROP (too much) | KEEP | single_character_cell |
| overall | elstat--2b5780c7c9896a54--s000-l0051 | Sommaire | DROP (too little) | KEEP | short_line |
| overall | elstat--c4d30f00b317e558--s001-l0501 | 1 | DROP (too much) | KEEP | single_character_cell |
| overall | gazette_modern--00a5942b52d08f1e--s000-l0115 | 1 | DROP (too little) | KEEP | single_character_cell |
| overall | gazette_modern--1456dcb167f23bfe--s000-l0027 | 1 | DROP (too little) | KEEP | single_character_cell |
| overall | gazette_modern--232906bf221ad08d--s000-l0144 | & ΣΙΑ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--2e613d9290dd13d4--s000-l0017 | 1 | DROP (too much) | KEEP | single_character_cell |
| overall | gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | 1. | DROP (too much) | KEEP | single_character_cell |
| overall | gazette_modern--3ff46b4e721f2046--s000-l0375 | 254/6 | DROP (too much) | KEEP | survives |
| overall | gazette_modern--5158b7bf9def2bab--s000-l0012 | - | DROP (too little) | KEEP | single_character_cell |
| overall | gazette_modern--52ee6226bb7d4834--s000-l0122 | ΠΟΛΕΩΣ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--59bea69d71112ea7--s000-l0064 | ΖΗΜΙΑΙ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--62822e3af8f17cf4--s000-l0074 | ανέρ- | DROP (too much) | KEEP | survives |
| overall | gazette_modern--6bc7acccf0163698--s000-l0268 | 1 | DROP (too much) | KEEP | single_character_cell |
| overall | gazette_modern--6d58ca2e2dc41e69--s000-l0140 | του | DROP (too little) | KEEP | survives |
| overall | gazette_modern--6efb0af18300ce89--s000-l0085 | Γραμματέα, Δ/ντές και Τμηματάρχες της Κεντρικής Υπηρεσίας του | DROP (too much) | KEEP | survives |
| overall | gazette_modern--7e81c2a51da91d05--s000-l0065 | Βασίλης Τσιουρίκης | DROP (too much) | KEEP | survives |
| overall | gazette_modern--7f20c8792129c8f6--s000-l0062 | που | DROP (too little) | KEEP | survives |
| overall | gazette_modern--80e8a42cbf8e629f--s000-l0120 | 13.3.1986 (ΦΕΚ 93/Γ΄/11.4.86) και μόνο κατά το μέρος | DROP (too much) | KEEP | survives |
| overall | gazette_modern--819a6ad32e0c7ab2--s000-l0004 | ΝΤΙΛΕΣΙΠ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--82115ca04c55f5b7--s000-l0005 | ΥΠΟΜΝΗΜΑ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--8757f64ef1908c90--s000-l0009 | 1. Τις διατάξεις του από 24.4.85 Π.Δ/τος (ΦΕΚ 181Δ΄/3.5.85) | DROP (too much) | KEEP | survives |
| overall | gazette_modern--96035db0434dc980--s000-l0074 | 1 | DROP (too little) | KEEP | single_character_cell |
| overall | gazette_modern--9aa01acfc4b8b0a7--s000-l0100 | κτηριστικών (απόφαση ΣΤ-20270/73-Φ.Ε.Κ. 884/73, όπως | DROP (too much) | KEEP | survives |
| overall | gazette_modern--a895f3d785bb13b6--s000-l0138 | θε όσουε τη συμφωνία του περιεχομένου της Εκθέσεως διαχειρίσεως του Διοικητικού Συμβουλίου προς την τακτική Γενική Συνέλευση των μετόχων, με τις σχετικές Οικονομικές Καταστάσεις. Το Προσάρτημα περιλαμβάνει | DROP (too much) | KEEP | survives |
| overall | gazette_modern--a8e70ef11baca460--s000-l0001 | 1 | DROP (too little) | KEEP | single_character_cell |
| overall | gazette_modern--aeb6eb76fc7057f0--s000-l0050 | " | DROP (too little) | KEEP | single_character_cell |
| overall | gazette_modern--af3c2f9a667e8669--s000-l0004 | ΑΘΗΝΑ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--b05f7f66a8e2e416--s000-l0067 | ΔΗΜ. ΓΕΩΡΓΑΚΟΠΟΥΛΟΣ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--bd7c91e6a214949b--s000-l0125 | ハンハンΟΜΙΑΣ. | DROP (too little) | KEEP | mixed |
| overall | gazette_modern--c1b2194696b35bb5--s000-l0004 | ΑΘΗΝΑ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--c36d4711ccb77454--s000-l0227 | του αρθ. 42ε παράγρ. 14 του Ν.2190/1920, δεν σχημάτισε πρόβλεψη για την πιθανή υποχρέωσή της για αποζημίωση του συνόλου του προσωπικού της λόγω εξόδου του από την υπηρεσία για συνταξιοδότηση, η οποία κατά την 31.12.1997 12.199 | DROP (too much) | KEEP | survives |
| overall | gazette_modern--c4919950cda5532e--s000-l0008 | ΠΑΓΙΟ | DROP (too little) | KEEP | survives |
| overall | gazette_modern--d4e7c0bb57264e92--s000-l0030 | 3.237.787 | DROP (too little) | KEEP | survives |
| overall | gazette_modern--d6092126b747cac8--s000-l0014 | 1 | DROP (too much) | KEEP | single_character_cell |
| overall | gazette_modern--e4940977902166f0--s000-l0109 | γούρια) | DROP (too much) | KEEP | survives |
| overall | gazette_modern--f4a16fe9302ade1e--s000-l0180 | 29) | DROP (too much) | KEEP | survives |
| overall | ia_greek_latin--2b4cfc7c6d70fd98--s000-l0053 | ἀνάμνησις, 36 | DROP (too much) | KEEP | survives |
| overall | ia_greek_latin--5f5319037ff4b70f--s000-l0028 | LIBRARY | DROP (too much) | KEEP | survives |
| overall | ia_greek_latin--5f5319037ff4b70f--s001-l0039 | II. INDEX LOCORUM | DROP (too little) | KEEP | survives |
| overall | ia_greek_latin--8af66d4d113847ee--s003-l0022 | ...................... | DROP (too little) | KEEP | short_line |
| overall | ia_greek_latin--8af66d4d113847ee--s003-l0107 | ......................... | DROP (too little) | KEEP | short_line |
| overall | ia_greek_latin--e02bf39b0ef9974e--s007-l0001 | THE ODYSSEY BOOK XIV. | DROP (too little) | KEEP | survives |
| overall | ia_greek_latin--f40a7578d8cd5825--s005-l0001 | NEW SERIES OF LATIN SCHOOL BOOKS. | DROP (too little) | KEEP | survives |
| overall | ia_poly1850--36dcee7ce4c29f8b--s005-l0065 | *Vid. Luc. | DROP (too much) | KEEP | survives |
| overall | ia_poly1850--61d0e23d1e93ae02--s031-l0002 | ΠΕΡΙΕΧΟΜΕΝΑ. | DROP (too little) | KEEP | survives |
| overall | ia_russian--06528548147a3a3d--s002-l0005 | ли | DROP (too little) | KEEP | survives |
| overall | lekythos--456def1ccfc2283e--s001-l0177 | -'-'-'-'-'-'-'0 | DROP (too little) | KEEP | numeric_shape |
| overall | lekythos--49c082ba27aa27da--s000-l0046 | Η του | DROP (too little) | KEEP | short_line |
| overall | lekythos--7f67b784930deef5--s004-l0004 | HUMILLY (HAUTE SAVOIE) | DROP (too much) | KEEP | survives |
| overall | lekythos--a0c4e6327052acfc--s002-l0089 | / | DROP (too little) | KEEP | single_character_cell |
| overall | nlg--1144074169f43992--s003-l0001 | ΜΕΡΟΣ ΠΡΩΤΟΝ | DROP (too little) | KEEP | survives |
| overall | nlg--6ae0ac01064a587e--s002-l0004 | ΤΑ ΨΗΛΑ ΒΟΥΝΑ | DROP (too little) | KEEP | survives |
| overall | nlg--f4b52df5f8130047--s034-l0008 | Ο ΠΥΡΓΟΣ | DROP (too little) | KEEP | survives |
| overall | serbia--9caa9fc02f50cad6--s000-l0010 | САВЕ ДЕЧАНЦА | DROP (too little) | KEEP | survives |
| overall | serbia--9caa9fc02f50cad6--s003-l0009 | САВЕ ДЕЧАНЦА | DROP (too little) | KEEP | survives |
| overall | serbia--b6450341d87fb144--s007-l0002 | ВИЉЕМ БУE | DROP (too little) | KEEP | mixed |
| numeric | elstat--0a2c92120843658d--s001-l0216 | 1 | DROP (too much) | KEEP | single_character_cell |
| numeric | elstat--c4d30f00b317e558--s001-l0501 | 1 | DROP (too much) | KEEP | single_character_cell |
| numeric | gazette_modern--00a5942b52d08f1e--s000-l0115 | 1 | DROP (too little) | KEEP | single_character_cell |
| numeric | gazette_modern--1456dcb167f23bfe--s000-l0027 | 1 | DROP (too little) | KEEP | single_character_cell |
| numeric | gazette_modern--2e613d9290dd13d4--s000-l0017 | 1 | DROP (too much) | KEEP | single_character_cell |
| numeric | gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | 1. | DROP (too much) | KEEP | single_character_cell |
| numeric | gazette_modern--3ff46b4e721f2046--s000-l0375 | 254/6 | DROP (too much) | KEEP | survives |
| numeric | gazette_modern--6bc7acccf0163698--s000-l0268 | 1 | DROP (too much) | KEEP | single_character_cell |
| numeric | gazette_modern--96035db0434dc980--s000-l0074 | 1 | DROP (too little) | KEEP | single_character_cell |
| numeric | gazette_modern--a8e70ef11baca460--s000-l0001 | 1 | DROP (too little) | KEEP | single_character_cell |
| numeric | gazette_modern--d4e7c0bb57264e92--s000-l0030 | 3.237.787 | DROP (too little) | KEEP | survives |
| numeric | gazette_modern--d6092126b747cac8--s000-l0014 | 1 | DROP (too much) | KEEP | single_character_cell |
| numeric | gazette_modern--f4a16fe9302ade1e--s000-l0180 | 29) | DROP (too much) | KEEP | survives |
| numeric | lekythos--456def1ccfc2283e--s001-l0177 | -'-'-'-'-'-'-'0 | DROP (too little) | KEEP | numeric_shape |

### Owner cases

| ID / case | Gate | r | Current | Original 0.30–2.00 | New overall 0.30–1.95 |
| --- | --- | --- | --- | --- | --- |
| gazette_modern--52ee6226bb7d4834--s000-l0122 | ADMIT | 0.35136416 | DROP (too little) | KEEP | KEEP |
| gazette_modern--82115ca04c55f5b7--s000-l0005 | ADMIT | 0.36929613 | DROP (too little) | KEEP | KEEP |
| gazette_modern--80e8a42cbf8e629f--s000-l0120 | ADMIT | 1.641271 | DROP (too much) | KEEP | KEEP |
| elstat--0877c813a8512b56--s000-l0037 | ADMIT | 0.81251075 | DROP (padding) | DROP (padding) | DROP (padding) |
| gazette_modern--6d6a6fe53e769b59--s000-l0009 | ADMIT | 0.74999135 | DROP (padding) | DROP (padding) | DROP (padding) |
| ia_poly1850--df8f2267db2b7275--s025-l0037 | ADMIT | 1.3391192 | KEEP | KEEP | KEEP |
| 129cff40-p000009-l0107 | ADMIT | n/a | None | None | not in band population |

ΠΟΛΕΩΣ and l0005 survive despite having fewer than ten letters because their source primary class is headings_caps (minimum four). They remain KEEP under both wider proposals. Gazette l0120 remains KEEP against owner DROP under either wider band, and stays length-blind; the owner’s neighbour-word objection is not fixed by filtering or changing bounds. Both padding witnesses remain DROP. The 129cff40 witness remains outside the band because its saved segmentation gate drops it; it is not a content-gate exclusion.

## Read-only sheet audit

The existing sheet, its HTML and cards.jsonl were not edited. Gate-failed cards by group and section are listed in full in [SHEET_AUDIT.md](SHEET_AUDIT.md) and [sheet_failed_cards.jsonl](sheet_failed_cards.jsonl). Remaining cards keep their historical group because marks and verdicts do not change. Recomputing proposal membership with the new tie-rule bands produces no remaining group/section move.

| Section / group | Before → mixed/foreign after | Before → part-2 after | Before → all after |
| --- | --- | --- | --- |
| changed/disagree | 12 → 12 | 12 → 12 | 12 → 12 |
| changed/newly_agree | 75 → 74 | 75 → 67 | 75 → 66 |
| changed/unjudged | 133 → 124 | 133 → 87 | 133 → 83 |
| proposal/disagree | 49 → 48 | 49 → 33 | 49 → 33 |
| proposal/newly_agree | 10 → 9 | 10 → 6 | 10 → 5 |

### Intro numbers that would change

| Intro item | Before → after |
| --- | --- |
| Cards | 279 → 199 |
| 235 marks, baseline → new tool | 155/235 → 189/235 → 131/191 → 157/191 |
| 135 ratings, baseline → new tool | 94/135 → 109/135 → 62/91 → 77/91 |
| 185 typology marks, baseline → new tool | 131/185 → 160/185 → 125/176 → 153/176 |
| 150 FP/FN/UNC baseline → new tool | 18/14/11 → 16/15/0 → 16/14/6 → 11/15/0; n=137 |
| Numeric box gain | 111 → 127 /144 → 91 → 103 /110 |
| Numeric expectation extra agreements | +5 (132/144) → −1 (102/110), same after refit |
| Non-numeric box gain | 120 → 137 /157 → 116 → 131 /150 |
| Mixed | 3/3 in every cell → unchanged 3/3, indicative |
| Selected overall proposal | 0.30–2.00 → 0.30–1.95 (old band still tied) |
| Original proposed-band cards | 59 → 38 |

The counts describing five historical implementation steps and fixed rule thresholds (≤8, aspect≤6, visibility95%, padding1.5, etc.) are historical/method descriptions and do not change. The input-set sizes in the intro would need eligible counts 137/819/213/284 alongside their historical 150/888/250/417 identities.

## Coordinator list cross-check

Finite saved crop pool: **13 unique disagreeing IDs**. This compares only mixed/foreign categories, not part 2. Every ID, raw text and per-row expected scripts is in [COORDINATOR_CROSSCHECK.md](COORDINATOR_CROSSCHECK.md) / [coordinator_disagreements.jsonl](coordinator_disagreements.jsonl). The coordinator list covers the census as well; the exhaustive census comparison finds **1452 disagreements**, and the union with finite-only IDs is **1452**. The ready line explicitly uses the finite-set count. [Census differences](coordinator_census_disagreements.jsonl) lists all census IDs and reasons. The pipeline gate decides; an item in the coordinator list outside an evaluation set is not counted as an evaluation disagreement.

## Unexpected scripts by book — flagging only

Scanned all **592,466** raw census_02 rows from the supplied read-only gzip. All expectations resolve ({'source policy adm.expected_policy': 592466}); unresolved list is [census_unresolved_expectations.json](census_unresolved_expectations.json), empty. The exact supplied source/wave/script_class fields, inventory, codec and gate helper decide HOLD/DROP. Book is the second `--` segment; rows without it have an explicit null book, never a made-up book per row. Page identity is the saved sNNN-containing ID prefix where present. No metadata expectation is changed.

2712 rows have at least one pipeline-unexpected script, including codec questions; the script table (excluding ordinal/micro characters as requested) has 833 source×book×script entries. A row can occur in multiple script entries. Gate mixed-word DROP precedes foreign HOLD even when the script is real content. This is distinct from all mixed-word rows, including mixtures of two otherwise expected scripts.

**Complete per-book tables and 2–3 available raw examples:** [UNEXPECTED_SCRIPTS_BY_BOOK.md](UNEXPECTED_SCRIPTS_BY_BOOK.md). Each combination has its own table, outcome counts, whole-token and mixed-word evidence, classification and borderline flag. All witness IDs/texts are saved in [unexpected_scripts_rows.jsonl](unexpected_scripts_rows.jsonl). Single-row books have one available example. Named script labels refine the gate’s `other` category only for presentation; they never decide eligibility.

Classification is a raw-text assessment, not physical glyph validation: (a) plausible real other-language content/scholarly sigla; (b) letter-level confusion supported by mixed words; (c) noise candidates. “Borderline” explicitly marks ambiguous short fragments, contradictory patterns and weak source context. No raw OCR text alone proves what was printed.

Chinese 26e14cb9c90b750f has long CJK sequences on 232 rows: strong real-content evidence. Syriac 174d84a441d69a70 has 22 rows with Biblical/grammar context; its 15 Arabic-letter rows include whole phrases/glosses and are borderline in script identity. Hebrew 5aa15e93b2f445b8 is predominantly the legitimate Aleph manuscript siglum (`א = Sinaiticus`), not 28 rows of Hebrew prose; context supports class (a), while 8 mixed-token rows still DROP. Hebrew ebcfd6056abfa776 (11) and the three ia_greek_latin books (13 rows total) have quotation/apparatus evidence. Two further ia_poly1850 Hebrew books (09f9190274fc82bd, 41e90f3ba967f920; 8 each) also have explicit scholarly language examples.

**Coordinator candidate reassessment:** Arabic 61d0e23d1e93ae02 has 82 rows consisting of only six short forms (68 `دو`, six `اد`, four `وو`, two `د`, one `ام`, one `و`). c39403323b6d5d89 has 24 rows (20 `دو`, four `وو`). These support repeated ditto/rule/glyph-noise candidates, not a confident real-Arabic-content classification; both remain borderline (c). An extra expected script is not recommended from this OCR evidence alone. The same caution applies to repeated `دو` in several other books and to Arabic/Hebrew-looking forms in Greek Gazette tables. Their current foreign HOLD remains the actual pipeline outcome.

The Gazette Cyrillic and Cyrillic-archive Greek flags are not assumed to be all mixed. Per-book counts distinguish whole words from single letters inside mixed words; some rows correctly HOLD rather than DROP. Raw-presence versus pipeline-unexpected source totals, and the coordinator’s rough counts, are compared below.

| Source | Script | Coordinator raw estimate rows/books | Pipeline raw presence rows/books | Unexpected rows/books | Actual outcomes |
| --- | --- | --- | --- | --- | --- |
| gazette_modern | cyrillic | 447 rows /285 books | 447 /285 | 447 /285 | {'DROP mixed_script_word': 168, 'HOLD unexpected_script': 279} |
| gazette_modern | ARABIC | 145 /108 | 145 /108 | 145 /108 | {'HOLD unexpected_script': 134, 'DROP mixed_script_word': 11} |
| gazette_modern | HIRAGANA | 61 /49 | 61 /49 | 61 /49 | {'HOLD unexpected_script': 53, 'DROP mixed_script_word': 8} |
| gazette_modern | KATAKANA | 43 /37 | 43 /37 | 43 /37 | {'HOLD unexpected_script': 34, 'DROP mixed_script_word': 9} |
| gazette_modern | KATAKANA-HIRAGANA | 9 /8 | 9 /8 | 9 /8 | {'HOLD unexpected_script': 5, 'DROP mixed_script_word': 4} |
| gazette_modern | HANGUL | 29 /25 | 29 /25 | 29 /25 | {'HOLD unexpected_script': 25, 'DROP mixed_script_word': 4} |
| ia_russian | ARABIC | 6 /3 | 6 /3 | 6 /3 | {'HOLD unexpected_script': 6} |
| serbia | ARABIC | 5 /2 | 5 /2 | 5 /2 | {'HOLD unexpected_script': 5} |
| serbia | CJK | 4 /3 | 4 /3 | 4 /3 | {'HOLD unexpected_script': 4} |

Gazette Cyrillic is 447 rows over 285 books, but only 168 DROP as mixed; 279 HOLD as foreign. Gazette Arabic is 145 rows/108 books: 11 mixed DROP and 134 foreign HOLD. Thus neither script inventory is uniformly handled by the mixed-word rule. Greek in the Cyrillic archive sources resolves from each supplied script_class; the six unexpected Greek rows are stand-alone Greek lookalikes in Roman month numerals and HOLD, rather than mixed-word DROP. This rejects the coordinator’s blanket mixed-rule interpretation. Raw Greek presence in archive_b24878935 and archive_izvestiianabulga610193138bulg is one row each, but those supplied rows have Greek expected by source/class policy and do not fail this script gate. The unexpected archive-Greek rows are:

| Source / book | Unexpected Greek rows | Mixed-word rows | Actual gate outcomes | Examples |
| --- | --- | --- | --- | --- |
| archive_izvestiianabul25192530bul/None | 5 | 0 | {'HOLD unexpected_script': 5} | ляръ е билъ уловенъ отъ Н. В. Царь Фердинандъ на 23. Χ. · (4. ΙΧ), Дивиташката пещера при с. Дивитаки, с. Зъл- · 13. 30. Χ. въ Търновско Преображ. манастиръ и |
| archive_izvestiianatsars1516194243tsar/None | 1 | 0 | {'HOLD unexpected_script': 1} | ΧΙΧ., 1934 № 4 р. 1), по екземпляри ловени отъ Н. Reisser и R. Züllich |

### Codec questions — separately, not scripts

Ordinals º/ª are legitimate in Latin bibliographic/paragraph contexts; the current codec can still count them as `other` and HOLD/DROP them. These are codec representation questions, not evidence of another language. MICRO SIGN µ needs a codec/label question where Greek μ is intended; no substitution was made and printed-glyph identity is not claimed from raw text alone.

| Character | Rows | Books |
| --- | --- | --- |
| º | 17 | 6 |
| ª | 16 | 3 |
| µ | 2 | 2 |

Every codec row ID, source/book, raw text, current codec script vote and gate outcome is in [CODEC_QUESTIONS.md](CODEC_QUESTIONS.md) and [codec_questions.jsonl](codec_questions.jsonl).

## Conclusion audit

| Original direction / best-cell / band statement | Changes? | Evidence / replacement |
| --- | --- | --- |
| S4 all-ink box helps both numeric and non-numeric small rows | no | Primary numeric text-font agreement 111/144 → 127/144 before; 91/110 → 103/110 after. Non-numeric 120/157 → 137/157 before; 116/150 → 131/150 after. |
| Separate numeric expectation is the numeric best cell | yes | s4/short-numeric 132/144 vs text-font 127/144 becomes 102/110 vs 103/110; best cell becomes s4/text-font. Refit numeric expectations give the same best cell. |
| All-crops fit 2×2 best cells | yes | Saved-fit filtering: numeric best moves from s4/short-numeric to s4/text-font; with newly refitted all-crops coefficients numeric becomes a tie of s4/text-font and s4/short-numeric. Non-numeric all-crops best remains s4/short-numeric. |
| Non-numeric primary best cell tie and mixed tie | no | Non-numeric s4/text-font and s4/short-numeric remain tied; all four mixed cells tied (3/3, indicative only). |
| S4 main and typology owner agreement improves over S3 | no | Marks 170/235 → 189/235 before, 144/191 → 157/191 after; typology 147/185 → 160/185 before, 140/176 → 153/176 after. |
| S2 reduces undecided cases on the 150; S4 resolves the remaining cases | yes | S2 still reduces UNC, 6 → 0 after filtering. S4 no longer resolves remaining 150 cases: there are already zero at S2/S3 (originally five at S3). |
| Overall best equal-cost band is 0.30–2.00 | yes | Tie-rule point becomes 0.30–1.95 (ΔL=0, ΔU=−0.05); 0.30–2.00 remains tied in total errors. |
| Numeric best equal-cost band is 0.35–2.00 | yes | Tie-rule point becomes 0.35–1.70 (ΔL=0, ΔU=−0.30); 0.35–2.00 remains tied in total errors. |
| Small diagnostic best end-to-end band is 0.35–2.00 | yes | Becomes 0.40–1.85 (ΔL=+0.05, ΔU=−0.15). Non-numeric and non-small end-to-end best 0.30–1.95 and mixed 0.50–1.50 do not move. |
| Other unequal-cost best points (w=2,3) | yes | Overall w=2: 0.35–2.00 → 0.30–1.85; w=3: 0.35–1.85 → 0.30–1.85. Numeric w=2 and w=3: 0.35–2.00 → 0.35–1.70. Full before/after tables include every ablation. |
| Class-balanced overall best band is 0.55–1.30 | yes | Becomes 0.60–1.25 (ΔL=+0.05, ΔU=−0.05), new weight 12.29 instead of 7.75. Numeric class-balanced 0.35–1.25 stays. |
| Equal costs widen the band; class-balanced costs narrow it | no | Direction remains true for overall. The new numeric equal-cost point also remains wider than 0.50–1.50. |
| Overall fitted band gains on every held-out split | yes | All gains are non-negative; the cells source-set and cells cohort now tie (gain 0), replacing strictly positive gains. Hash-half gains 20/18 → 14/13. |
| Numeric held-out gains are 0–6 lines | yes | Becomes 0–1; every leave-source-set/cohort-out gain is 0. |
| Bootstrap saves ≤0 errors in 0/1000 resamples | yes | Overall remains 0/1000; numeric becomes 48/1000 (and current is a tied optimum in 30/1000). |
| Exact bounds remain uncertain | no | Overall bootstrap U 2.5–97.5% range 1.75–2.45 → 1.70–2.45; numeric 1.70–2.45 → 1.50–2.45. |
| Owner cases ΠΟΛΕΩΣ/l0005 become KEEP, l0120 becomes wrong KEEP under proposal | no | All three survive the content gate; both the original and new overall band give the same verdicts. Gazette l0120 remains outside the length objective because the owner says its output length is correct. |

## One line per set

segeval1: 150 → 137 (removed 1 mixed + 2 foreign + 10 part-2); conclusion changes: S4 no longer resolves remaining UNC; S2 already reaches zero

calibration: 888 → 819 (removed 10 mixed + 10 foreign + 49 part-2); conclusion changes: no

cells: 250 → 213 (removed 0 mixed + 1 foreign + 36 part-2); conclusion changes: no (unlabelled verdict counts; contributes to changed numeric best cell)

typology: 417 → 284 (removed 3 mixed + 23 foreign + 107 part-2); conclusion changes: no

owner_marks: 235 → 191 (removed 1 mixed + 2 foreign + 41 part-2); conclusion changes: no

rated_888: 135 → 91 (removed 2 mixed + 5 foreign + 37 part-2); conclusion changes: no

typology_marked: 185 → 176 (removed 1 mixed + 3 foreign + 5 part-2); conclusion changes: no

small: 642 → 508 (removed 1 mixed + 22 foreign + 111 part-2); conclusion changes: numeric best cell changes; S4 abstention subset shrinks

band_population: 500 → 420 (removed 4 mixed + 8 foreign + 68 part-2); conclusion changes: overall/numeric/small best bands; class-balanced overall; held-out and numeric bootstrap claims

changed_lines: 59 → 38 (removed 2 mixed + 0 foreign + 19 part-2); conclusion changes: best-band selections move; remaining changed-ID set unchanged

sheet: 279 → 199 (removed 2 mixed + 10 foreign + 68 part-2); conclusion changes: numeric intro conclusion and selected proposal bounds

numeric_fit: 383 → 319 (removed 0 mixed + 0 foreign + 64 part-2); conclusion changes: no direction claim from fit coefficients alone

two_by_two: 304 → 263 (removed 0 mixed + 2 foreign + 39 part-2); conclusion changes: numeric best cell becomes s4/text-font

## Reproduction and receipt

Run with the existing sol-recut virtualenv and `PYTHONPATH=.` / `PYTHONDONTWRITEBYTECODE=1`: `python -B docs/records/harvest/seg_steps/gate_rereport/analyze.py`, then `augment.py`, `review.py`, then `report.py`. All scripts are confined to this output directory. The analysis has a write-path audit guard and network-denial audit hook. The receipt checks the pre-run versus post-run file stat inventory outside this directory, fingerprints inputs and lists output hashes. No old step validator main is executed because those routines would launch native segmentation readbacks.

[summary.json](summary.json) includes before, mixed/foreign-only, independent part-2-only and all-filtered results; [receipt.json](receipt.json) records checks, exact input hashes and artifact hashes.

SEG GATE REREPORT READY: removed 150 1+2+10=13 / 888 10+10+49=69 / 250 0+1+36=37 / 417 3+23+107=133 / band 4+8+68=80; small rows surviving numeric 208 mixed 34 non-numeric 243; 150 FP/FN/UNC s4 16/15/0 → 11/15/0; 888 109/135 → 77/91; marks 189/235 → 157/191; typology 160/185 → 153/176; 2x2 answer changes yes; best band moves yes; sheet cards removed 80; coordinator list disagreements 13; conclusions changed numeric best cell, 150 S4 UNC-resolution claim, overall/numeric/small bands, class-balanced overall band, strict held-out gain claim, numeric stability
