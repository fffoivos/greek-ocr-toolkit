# Readability calibration

Raster checks and Greek reading checks are independent. The PDF text layer is another OCR and is never a reference or calibration target.

Unique rasters: 444. Available VLM labels: 444. Unlabelled: 0.
Source-separated training / held-out counts: 333 / 111.

VLM labels are provisional observations. Precision/recall below describe agreement with that judge, not verified accuracy against human gold.

## Default threshold confusion tables

| Defect | Metric / threshold | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| skew | skew_abs ge 1.000 | 0 | 29 | 0 | 415 | 0.000 | — | 0.000 |
| trails_up | trail_up ge 2.000 | 0 | 181 | 0 | 263 | 0.000 | — | 0.000 |
| trails_down | trail_down ge 2.000 | 0 | 131 | 0 | 313 | 0.000 | — | 0.000 |
| touches_top | top_fraction gt 0.000 | 232 | 212 | 0 | 0 | 0.523 | 1.000 | 0.686 |
| touches_bottom | bottom_fraction gt 0.000 | 288 | 139 | 4 | 13 | 0.674 | 0.986 | 0.801 |
| cut_left | left_fraction gt 0.000 | 38 | 118 | 25 | 263 | 0.244 | 0.603 | 0.347 |
| cut_right | right_fraction gt 0.000 | 91 | 80 | 82 | 191 | 0.532 | 0.526 | 0.529 |
| blurred | blur_mean ge 0.600 | 3 | 19 | 31 | 391 | 0.136 | 0.088 | 0.107 |
| low_contrast | local_contrast le 0.150 | 4 | 5 | 19 | 416 | 0.444 | 0.174 | 0.250 |
| obstructed | obstruction ge 0.020 | 3 | 40 | 20 | 381 | 0.070 | 0.130 | 0.091 |
| neighbour_intrusion | crowding ge 0.050 | 91 | 184 | 42 | 127 | 0.331 | 0.684 | 0.446 |
| two_lines | baseline_count ge 2.000 | 1 | 20 | 40 | 383 | 0.048 | 0.024 | 0.032 |
| empty | ink_coverage le 0.003 | 0 | 0 | 0 | 444 | — | — | — |

## Suggested thresholds and held-out agreement

| Defect | Suggested threshold | Fitted | Held-out TP / FP / FN / TN | Precision | Recall |
|---|---:|---|---|---:|---:|
| skew | 1.000 | False | 0 / 3 / 0 / 108 | 0.000 | — |
| trails_up | 2.000 | False | 0 / 44 / 0 / 67 | 0.000 | — |
| trails_down | 2.000 | False | 0 / 30 / 0 / 81 | 0.000 | — |
| touches_top | 0.006 | True | 53 / 58 / 0 / 0 | 0.477 | 1.000 |
| touches_bottom | 0.000 | True | 65 / 44 / 0 / 2 | 0.596 | 1.000 |
| cut_left | 0.073 | True | 8 / 17 / 1 / 85 | 0.320 | 0.889 |
| cut_right | 0.000 | True | 20 / 24 / 17 / 50 | 0.455 | 0.541 |
| blurred | 0.576 | True | 0 / 10 / 12 / 89 | 0.000 | 0.000 |
| low_contrast | 0.213 | True | 0 / 7 / 7 / 97 | 0.000 | 0.000 |
| obstructed | 0.003 | True | 12 / 65 / 0 / 34 | 0.156 | 1.000 |
| neighbour_intrusion | 0.036 | True | 25 / 62 / 3 / 21 | 0.287 | 0.893 |
| two_lines | 1.000 | True | 9 / 102 / 0 / 0 | 0.081 | 1.000 |
| empty | 0.003 | False | 0 / 0 / 0 / 111 | — | — |

## Owner notes

Available notes: 0; comparable explicit defect labels: 0. The task expected seven notes.
The supplied `tests/fixtures/o4d_lines/index.json` has `owner_notes: {}`. No human annotations were invented.

| Defect | TP | FP | FN | TN | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|
| skew | 0 | 0 | 0 | 0 | — | — |
| trails_up | 0 | 0 | 0 | 0 | — | — |
| trails_down | 0 | 0 | 0 | 0 | — | — |
| touches_top | 0 | 0 | 0 | 0 | — | — |
| touches_bottom | 0 | 0 | 0 | 0 | — | — |
| cut_left | 0 | 0 | 0 | 0 | — | — |
| cut_right | 0 | 0 | 0 | 0 | — | — |
| blurred | 0 | 0 | 0 | 0 | — | — |
| low_contrast | 0 | 0 | 0 | 0 | — | — |
| obstructed | 0 | 0 | 0 | 0 | — | — |
| neighbour_intrusion | 0 | 0 | 0 | 0 | — | — |
| two_lines | 0 | 0 | 0 | 0 | — | — |
| empty | 0 | 0 | 0 | 0 | — | — |

## Other features not yet detected

Unsupported named VLM categories: other.
- A dark vertical rule crosses the line near the left; neighbouring line ink is visible at the top and bottom edges.
- Ink from a neighbouring line intrudes along the lower edge, especially near the left and center.

Cheap features cannot establish semantic legibility, font familiarity, merged character identities, missing complete words, or whether faint mirrored ink truly came from the page reverse. Edge ink alone does not prove terminal clipping; the two-line row-profile proxy needs empirical validation.

## Method

Defaults are fixed before judging. Fit thresholds maximize training F1 among at most 65 quantiles; metrics on held-out source documents use the fitted value. A defect lacking both training classes is left at its default. Source split: SHA256(document id) modulo 5 equals 0 for held-out. Duplicate raster SHA256s are excluded. Readings, layer OCR and tier/CER fields never enter fitting.
