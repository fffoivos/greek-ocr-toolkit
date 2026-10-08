# Readability calibration

Raster checks and Greek reading checks are independent. The PDF text layer is another OCR and is never a reference or calibration target.

Unique rasters: 444. Available VLM labels: 0. Unlabelled: 444.
Source-separated training / held-out counts: 0 / 0.

VLM labels are provisional observations. Precision/recall below describe agreement with that judge, not verified accuracy against human gold.

## Default threshold confusion tables

| Defect | Metric / threshold | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| skew | skew_abs ge 1.000 | 0 | 0 | 0 | 0 | — | — | — |
| trails_up | trail_up ge 2.000 | 0 | 0 | 0 | 0 | — | — | — |
| trails_down | trail_down ge 2.000 | 0 | 0 | 0 | 0 | — | — | — |
| touches_top | top_fraction gt 0.000 | 0 | 0 | 0 | 0 | — | — | — |
| touches_bottom | bottom_fraction gt 0.000 | 0 | 0 | 0 | 0 | — | — | — |
| cut_left | left_fraction gt 0.000 | 0 | 0 | 0 | 0 | — | — | — |
| cut_right | right_fraction gt 0.000 | 0 | 0 | 0 | 0 | — | — | — |
| blurred | blur_mean ge 0.600 | 0 | 0 | 0 | 0 | — | — | — |
| low_contrast | local_contrast le 0.150 | 0 | 0 | 0 | 0 | — | — | — |
| obstructed | obstruction ge 0.020 | 0 | 0 | 0 | 0 | — | — | — |
| neighbour_intrusion | crowding ge 0.050 | 0 | 0 | 0 | 0 | — | — | — |
| two_lines | baseline_count ge 2.000 | 0 | 0 | 0 | 0 | — | — | — |
| empty | ink_coverage le 0.003 | 0 | 0 | 0 | 0 | — | — | — |

## Suggested thresholds and held-out agreement

| Defect | Suggested threshold | Fitted | Held-out TP / FP / FN / TN | Precision | Recall |
|---|---:|---|---|---:|---:|
| skew | 1.000 | False | 0 / 0 / 0 / 0 | — | — |
| trails_up | 2.000 | False | 0 / 0 / 0 / 0 | — | — |
| trails_down | 2.000 | False | 0 / 0 / 0 / 0 | — | — |
| touches_top | 0.000 | False | 0 / 0 / 0 / 0 | — | — |
| touches_bottom | 0.000 | False | 0 / 0 / 0 / 0 | — | — |
| cut_left | 0.000 | False | 0 / 0 / 0 / 0 | — | — |
| cut_right | 0.000 | False | 0 / 0 / 0 / 0 | — | — |
| blurred | 0.600 | False | 0 / 0 / 0 / 0 | — | — |
| low_contrast | 0.150 | False | 0 / 0 / 0 / 0 | — | — |
| obstructed | 0.020 | False | 0 / 0 / 0 / 0 | — | — |
| neighbour_intrusion | 0.050 | False | 0 / 0 / 0 / 0 | — | — |
| two_lines | 2.000 | False | 0 / 0 / 0 / 0 | — | — |
| empty | 0.003 | False | 0 / 0 / 0 / 0 | — | — |

**No empirical calibration is available:** the judge returned no labels. All displayed thresholds remain provisional; N=0 tables contain no observations, and undefined precision/recall are shown as dashes. These are not evidence of zero defects or high accuracy.

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

Unsupported named VLM categories: none observed (no labels).

Cheap features cannot establish semantic legibility, font familiarity, merged character identities, missing complete words, or whether faint mirrored ink truly came from the page reverse. Edge ink alone does not prove terminal clipping; the two-line row-profile proxy needs empirical validation.

## Method

Defaults are fixed before judging. Fit thresholds maximize training F1 among at most 65 quantiles; metrics on held-out source documents use the fitted value. A defect lacking both training classes is left at its default. Source split: SHA256(document id) modulo 5 equals 0 for held-out. Duplicate raster SHA256s are excluded. Readings, layer OCR and tier/CER fields never enter fitting.
