# L1C census (job 3679781) — ENSEMBLE_AB under sf4-release-v1, per wave (lines)

Source: `CENSUS.json` (sha in `receipt.json`), L1R 3679725 outputs. "Clipping-only" = lines whose exact reason set ⊆ {clipped_top, clipped_bottom},
summed over the top-10 exact sets (a lower bound). "With X" = lines carrying reason X at any slot (not exclusive).

| Wave | Lines | Held | Clipping-only (≥) | with clipped_top | with localisation_unknown | with segmentation_uncertain | A/B disagreement | Sole reason, top 3 |
|---|---|---|---|---|---|---|---|---|
| parliament | 27,224 | 26,927 (98.9%) | 1,385 (5.1%) | 20,688 | 22,524 | 24,024 | 1,653 | clipped_top 547, clipped_bottom 183, seg_unc 84 |
| vouli | 23,088 | 22,389 (97.0%) | 6,338 (27.5%) | 19,927 | 6,681 | 9,943 | 1,575 | clipped_top 1,880, clipped_bottom 551, unnamed 148 |
| round1 | 43,869 | 37,901 (86.4%) | 12,883 (29.4%) | 29,544 | 10,779 | 16,074 | 4,277 | clipped_top 4,475, clipped_bottom 1,209, seg_unc 862 |
| round2 | 17,026 | 13,913 (81.7%) | 5,297 (31.1%) | 10,763 | 2,914 | 5,153 | 1,426 | clipped_top 1,916, clipped_bottom 511, seg_unc 381 |
| mixed | 13,227 | 11,465 (86.7%) | 4,081 (30.9%) | 8,844 | 3,355 | 5,101 | 1,252 | clipped_top 1,454, clipped_bottom 342, seg_unc 297 |
| openarchives | 235 | 194 | 113 | 120 | 0 | 38 | 16 | clipped_bottom 27, clipped_top 25, A/B 12 |
| ALL | 124,669 | 112,789 (90.5%) | 30,280 (24.3%) | 89,886 | 46,253 | 60,333 | — | — |

Top exact sets overall: {clipped_bottom, clipped_top} 17,160; {clipped_bottom, clipped_top, localisation_unknown, segmentation_uncertain} 10,379;
{clipped_top} 10,297; {clipped_top, localisation_unknown, segmentation_uncertain} 6,692; {clipped_bottom, clipped_top, unnamed} 4,760.

Reading: under sf4 the line-level driver is CLIPPING (72% of lines carry clipped_top), with localisation/segmentation second and dominant only
on parliament. This corrects the L1H pilot reading ("localisation_unknown dominates"), which counted slot entries on 1,024 rows under the
pre-SF4 gate. Clipping is exactly what neighbour-line ink at the crop border would produce, so the masking test measures the main driver.
