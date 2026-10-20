# S8b — one bounded detector iteration

**Candidate does not qualify for adoption.** JUDGE parliament physical presence improves to **99.07/84.35 P/R** (paired baseline 83.96/73.09), but recall remains below 90%. JUDGE vouli precision improves sharply while recall falls. Held-out recall and owner-approved-state regressions remain. **Plan B is needed.**

Network OFF; Mac CPU; saved crops, CTC alignments and A/B/E predictions only. No CTC or R1 inference, training, new model, reader/gate/composer edit, `.git` write, other-worktree write, page publication or new adjudication. The checked-in runtime policy is **`sf4-release-v1`**; the coordinator’s SF6 motivation is not treated as permission to alter it. Results describe this single candidate, not a release.

Starting HEAD `4b69a87ac4225fda11f30ad7e0dc39a258422be4`. [Candidate lock](S8_DEV/s8b/candidate_lock.json), [DEV receipt](S8_DEV/s8b/dev_receipt.json), [regression receipt](S8_DEV/s8b/regression_receipt.json), [validation](S8_DEV/s8b/validation.json).

## Split, baseline and estimand

The split was frozen before pixel review: sorted unique document IDs within each wave, `random.Random("S8b-split-20261017:" + wave).shuffle`, first floor(n/2) documents TUNE, remainder JUDGE. No document crosses halves or waves. This balances documents rather than card counts; parliament is 13/14 documents and 232/346 read cards. Both UNKNOWN cards happen to be TUNE and are excluded without replacing their weights. No outcome-based rebalancing was performed.
Split SHA256 `f4e78bd3c9bc38b7f2ead76f44235776e81464f6de295c6edc9b662a09461760`. Frozen truth SHA256 `bbfba1509215d60517ab651324a44323f6a5cedd8378c97fdcadab48bc78a3ec`. All 976 resolved words are scored, including gaps/substitutions, clipped, unlocated and uncertain slots. Controls, UNKNOWN and unread words supply no truth.

| Wave | TUNE docs / resolved / read | JUDGE docs / resolved / read | Σw TUNE / JUDGE |
|---|---|---|---|
| parliament | 13 / 230 / 232 | 14 / 346 / 346 | 420.00 / 802.00 |
| round1 | 25 / 54 / 54 | 26 / 46 / 46 | 379.42 / 401.09 |
| round2 | 13 / 44 / 44 | 14 / 56 / 56 | 370.85 / 355.05 |
| mixed | 12 / 56 / 56 | 13 / 44 / 44 | 580.20 / 355.46 |
| vouli | 20 / 50 / 50 | 21 / 50 / 50 | 871.96 / 596.98 |

Before means saved S6 on **441 matched masked crops**, nine unchanged original fallbacks, and 150 unmasked parliament crops. After uses exactly the same crop for every line. This is a full resolved-truth comparison, whereas S8a7 excluded ten resolved new-candidate words from its paired cohort. No S8b prediction-dependent exclusions are made: the adjudicated printed transcription remains fixed even when the new emitted form was absent from the original options. Hence non-parliament before values need not equal S8a7’s restricted paired table. Parliament ALL before exactly reproduces S8a6 82.62/68.23.

Weights are the unchanged S8a6 inverse card-inclusion × wave-cut probabilities within each half. Ratios use weighted TP/(TP+FP) and TP/(TP+FN). `any` is physical above OR below, including unnamed ink; `above`/`below` are physical zones. Breathing, accent, subscript, diaeresis and `emitted_any` use emitted names. Apostrophes are outside this combining-mark denominator. Mark-blind base alignment, punctuation anchors and insertion/deletion accounting are unchanged.

Cells show weighted percent [95% interval]. B = document-cluster percentile bootstrap, 4,000 replicates, seed 20261017 + wave index; W = Wilson–Kish fallback only for a degenerate bootstrap. Undefined denominators remain undefined. Line-cluster intervals, valid replicate counts and weighted/raw TP/FP/FN/TN are retained in [the summary](S8_DEV/s8b/dev_summary.json); [per-word/slot evidence](S8_DEV/s8b/dev_scores.jsonl.gz) retains every input to the score. These intervals exclude reader error and do not establish generalization beyond DEV.

## JUDGE: detector presence and families


| Wave | Measure | Before P / R [95%] | After P / R [95%] | Raw TP/FP/FN before → after |
|---|---|---|---|---|
| parliament | any | 83.96 [73.20, 91.11]B / 73.09 [59.91, 82.22]B | 99.07 [98.43, 99.64]B / 84.35 [76.30, 90.17]B | 174/124/239 → 312/7/101 |
| parliament | breathing | 56.63 [28.79, 77.04]B / 51.37 [28.47, 65.13]B | 86.36 [77.78, 91.53]B / 72.68 [57.45, 82.21]B | 37/72/89 → 76/21/50 |
| parliament | accent | 83.18 [71.43, 90.62]B / 73.35 [58.37, 83.29]B | 97.77 [96.36, 98.80]B / 84.48 [75.68, 91.02]B | 116/108/194 → 235/14/75 |
| parliament | subscript | 14.29 [0.00, 80.00]B / 50.00 [0.00, 100.00]B | 40.00 [0.00, 100.00]B / 100.00 [34.24, 100.00]W | 1/6/1 → 2/3/0 |
| parliament | diaeresis | — (0 denominator) / 0.00 [0.00, 79.35]W | — (0 denominator) / 0.00 [0.00, 79.35]W | 0/0/1 → 0/0/1 |
| parliament | emitted_any | 85.01 [74.75, 91.70]B / 71.51 [58.10, 80.89]B | 99.07 [98.42, 99.64]B / 83.90 [76.00, 89.68]B | 160/112/253 → 308/7/105 |
| parliament | above | 84.11 [73.45, 91.16]B / 72.91 [59.53, 82.11]B | 99.34 [98.62, 99.87]B / 84.31 [76.28, 90.13]B | 171/122/240 → 310/5/101 |
| parliament | below | 14.29 [0.00, 80.00]B / 50.00 [0.00, 100.00]B | 40.00 [0.00, 100.00]B / 100.00 [34.24, 100.00]W | 1/6/1 → 2/3/0 |
| round1 | any | 97.92 [94.22, 100.00]B / 92.64 [85.59, 96.59]B | 97.39 [92.33, 100.00]B / 91.66 [83.70, 96.04]B | 41/4/15 → 39/5/17 |
| round1 | breathing | 77.76 [41.67, 92.85]B / 81.80 [44.99, 94.48]B | 75.29 [36.84, 92.44]B / 79.20 [40.89, 93.10]B | 13/9/7 → 12/10/8 |
| round1 | accent | 96.06 [91.22, 98.77]B / 90.46 [80.49, 95.63]B | 97.16 [93.70, 99.21]B / 90.46 [80.49, 95.63]B | 23/7/18 → 23/5/18 |
| round1 | subscript | 0.00 [0.00, 56.15]W / — (0 denominator) | 0.00 [0.00, 56.15]W / — (0 denominator) | 0/3/0 → 0/3/0 |
| round1 | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| round1 | emitted_any | 97.92 [94.22, 100.00]B / 92.64 [85.59, 96.59]B | 97.39 [92.33, 100.00]B / 91.66 [83.70, 96.04]B | 41/4/15 → 39/5/17 |
| round1 | above | 98.44 [95.01, 100.00]B / 92.64 [85.59, 96.59]B | 97.90 [93.04, 100.00]B / 91.66 [83.70, 96.04]B | 41/3/15 → 39/4/17 |
| round1 | below | 0.00 [0.00, 56.15]W / — (0 denominator) | 0.00 [0.00, 56.15]W / — (0 denominator) | 0/3/0 → 0/3/0 |
| round2 | any | 98.47 [94.34, 100.00]B / 90.82 [75.57, 98.53]B | 99.23 [96.65, 100.00]B / 90.82 [75.91, 97.98]B | 54/2/13 → 54/1/13 |
| round2 | breathing | 78.38 [46.43, 94.67]B / 68.51 [35.71, 86.73]B | 83.58 [56.25, 96.25]B / 74.81 [44.00, 91.97]B | 14/9/15 → 17/7/12 |
| round2 | accent | 89.88 [70.60, 97.56]B / 81.62 [56.82, 94.04]B | 95.29 [84.37, 99.13]B / 82.64 [59.30, 93.24]B | 24/9/18 → 25/4/17 |
| round2 | subscript | 0.00 [0.00, 79.35]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 79.35]W / 0.00 [0.00, 79.35]W | 0/1/1 → 0/1/1 |
| round2 | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| round2 | emitted_any | 98.38 [94.00, 100.00]B / 85.87 [68.05, 94.70]B | 99.18 [96.32, 100.00]B / 85.87 [66.84, 95.03]B | 47/2/20 → 47/1/20 |
| round2 | above | 98.47 [94.34, 100.00]B / 90.82 [75.57, 98.53]B | 99.23 [96.65, 100.00]B / 90.82 [75.91, 97.98]B | 54/2/13 → 54/1/13 |
| round2 | below | 0.00 [0.00, 79.35]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 79.35]W / 0.00 [0.00, 79.35]W | 0/1/1 → 0/1/1 |
| mixed | any | 98.09 [93.19, 100.00]B / 91.68 [79.37, 97.23]B | 99.36 [97.40, 100.00]B / 92.27 [81.35, 97.24]B | 41/3/14 → 42/1/13 |
| mixed | breathing | 87.87 [38.89, 98.30]B / 87.87 [41.18, 96.95]B | 92.69 [53.85, 98.64]B / 87.87 [43.46, 97.21]B | 13/7/7 → 13/4/7 |
| mixed | accent | 94.52 [85.67, 98.43]B / 77.02 [46.07, 95.53]B | 96.24 [89.95, 99.12]B / 76.28 [45.14, 95.04]B | 28/6/12 → 27/4/13 |
| mixed | subscript | 0.00 [0.00, 79.35]W / 0.00 [0.00, 56.15]W | 0.00 [0.00, 79.35]W / 0.00 [0.00, 56.15]W | 0/1/3 → 0/1/3 |
| mixed | diaeresis | 0.00 [0.00, 79.35]W / — (0 denominator) | 0.00 [0.00, 79.35]W / — (0 denominator) | 0/1/0 → 0/1/0 |
| mixed | emitted_any | 98.07 [93.04, 100.00]B / 90.49 [77.59, 96.59]B | 99.35 [97.24, 100.00]B / 90.49 [78.13, 96.42]B | 39/3/16 → 39/1/16 |
| mixed | above | 98.72 [94.35, 100.00]B / 93.34 [81.49, 98.39]B | 100.00 [72.29, 100.00]W / 93.95 [83.51, 98.39]B | 41/2/11 → 42/0/10 |
| mixed | below | 0.00 [0.00, 79.35]W / 0.00 [0.00, 56.15]W | 0.00 [0.00, 79.35]W / 0.00 [0.00, 56.15]W | 0/1/3 → 0/1/3 |
| vouli | any | 85.54 [68.28, 94.03]B / 93.66 [85.21, 97.12]B | 97.75 [92.49, 100.00]B / 91.55 [80.65, 96.26]B | 47/30/12 → 43/4/16 |
| vouli | breathing | 86.21 [60.41, 95.43]B / 89.75 [67.13, 96.53]B | 97.71 [88.10, 100.00]B / 87.70 [61.17, 95.44]B | 13/14/10 → 11/2/12 |
| vouli | accent | 81.18 [60.71, 91.54]B / 90.39 [77.28, 95.61]B | 97.21 [90.84, 100.00]B / 91.27 [78.43, 96.70]B | 29/24/11 → 30/3/10 |
| vouli | subscript | 0.00 [0.00, 65.76]W / 0.00 [0.00, 79.35]W | — (0 denominator) / 0.00 [0.00, 79.35]W | 0/2/1 → 0/0/1 |
| vouli | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| vouli | emitted_any | 86.53 [70.60, 94.21]B / 91.55 [80.24, 95.89]B | 98.85 [95.62, 100.00]B / 90.50 [78.15, 95.55]B | 43/27/16 → 41/2/18 |
| vouli | above | 85.47 [68.20, 94.03]B / 93.63 [85.12, 97.11]B | 97.75 [92.49, 100.00]B / 92.04 [81.43, 96.62]B | 46/30/12 → 43/4/15 |
| vouli | below | 0.00 [0.00, 65.76]W / 0.00 [0.00, 79.35]W | — (0 denominator) / 0.00 [0.00, 79.35]W | 0/2/1 → 0/0/1 |


| Wave | Any ΔP pp [95%] | Any ΔR pp [95%] | Breathing ΔP / ΔR pp [95%] |
|---|---|---|---|
| parliament | +15.12 [+7.96, +25.79] | +11.26 [-2.39, +24.65] | +29.74 [+13.35, +50.08] / +21.31 [+12.91, +32.94] |
| round1 | -0.53 [-2.09, +0.00] | -0.98 [-2.97, +0.00] | -2.47 [-11.44, +0.00] / -2.60 [-13.04, +0.00] |
| round2 | +0.76 [+0.00, +3.40] | +0.00 [-2.61, +2.29] | +5.20 [+0.21, +16.00] / +6.30 [+0.00, +15.00] |
| mixed | +1.27 [+0.00, +5.46] | +0.59 [+0.00, +2.41] | +4.82 [-8.08, +28.28] / +0.00 [-8.14, +8.61] |
| vouli | +12.21 [+5.02, +24.78] | -2.11 [-7.69, +0.77] | +11.51 [+2.63, +32.90] / -2.05 [-7.78, +0.00] |


## TUNE: detector presence and families


| Wave | Measure | Before P / R [95%] | After P / R [95%] | Raw TP/FP/FN before → after |
|---|---|---|---|---|
| parliament | any | 79.21 [60.73, 90.91]B / 57.83 [38.93, 75.48]B | 95.04 [92.33, 97.15]B / 83.13 [78.37, 88.92]B | 88/63/175 → 193/18/70 |
| parliament | breathing | 60.82 [27.87, 80.95]B / 52.68 [22.78, 74.07]B | 82.98 [63.93, 93.88]B / 69.64 [50.62, 82.90]B | 21/38/53 → 40/16/34 |
| parliament | accent | 81.58 [65.62, 90.48]B / 54.39 [35.27, 71.92]B | 94.48 [91.78, 96.85]B / 80.12 [75.21, 86.27]B | 53/42/156 → 141/16/68 |
| parliament | subscript | 0.00 [0.00, 65.76]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 29.91]W / 0.00 [0.00, 79.35]W | 0/2/1 → 0/9/1 |
| parliament | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| parliament | emitted_any | 81.47 [64.50, 91.44]B / 56.14 [36.59, 73.98]B | 94.97 [92.18, 97.11]B / 81.93 [77.15, 87.50]B | 81/53/182 → 188/18/75 |
| parliament | above | 79.73 [61.24, 91.45]B / 57.83 [38.93, 75.48]B | 96.90 [93.98, 98.84]B / 82.89 [78.09, 88.65]B | 88/61/175 → 192/11/71 |
| parliament | below | 0.00 [0.00, 65.76]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 29.91]W / 0.00 [0.00, 79.35]W | 0/2/1 → 0/9/1 |
| round1 | any | 99.43 [97.26, 100.00]B / 92.08 [81.60, 96.51]B | 100.00 [75.02, 100.00]W / 93.13 [84.13, 97.03]B | 45/1/15 → 47/0/13 |
| round1 | breathing | 70.64 [23.80, 88.67]B / 67.06 [21.43, 84.19]B | 75.98 [38.46, 89.82]B / 72.13 [29.41, 87.08]B | 8/11/13 → 10/9/11 |
| round1 | accent | 97.16 [90.58, 99.49]B / 87.25 [68.68, 94.04]B | 97.87 [92.77, 100.00]B / 87.88 [71.59, 94.28]B | 26/4/20 → 27/3/19 |
| round1 | subscript | — (0 denominator) / 0.00 [0.00, 79.35]W | — (0 denominator) / 0.00 [0.00, 79.35]W | 0/0/1 → 0/0/1 |
| round1 | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| round1 | emitted_any | 99.42 [97.22, 100.00]B / 91.02 [80.23, 95.79]B | 100.00 [74.81, 100.00]W / 92.60 [83.47, 96.73]B | 43/1/17 → 46/0/14 |
| round1 | above | 99.43 [97.26, 100.00]B / 92.56 [82.21, 97.01]B | 100.00 [75.02, 100.00]W / 93.63 [84.43, 97.51]B | 45/1/14 → 47/0/12 |
| round1 | below | — (0 denominator) / 0.00 [0.00, 79.35]W | — (0 denominator) / 0.00 [0.00, 79.35]W | 0/0/1 → 0/0/1 |
| round2 | any | 96.89 [86.71, 100.00]B / 92.12 [76.01, 97.43]B | 98.96 [94.89, 100.00]B / 94.09 [85.05, 97.43]B | 38/6/16 → 42/2/12 |
| round2 | breathing | 84.98 [23.08, 97.36]B / 84.98 [23.80, 96.43]B | 87.56 [47.06, 96.38]B / 92.49 [64.70, 98.01]B | 8/8/8 → 12/7/4 |
| round2 | accent | 93.00 [78.38, 98.20]B / 86.91 [67.84, 94.47]B | 96.45 [88.76, 99.37]B / 88.88 [75.09, 94.51]B | 21/10/20 → 24/5/17 |
| round2 | subscript | 100.00 [20.65, 100.00]W / 33.33 [0.00, 100.00]B | 100.00 [20.65, 100.00]W / 33.33 [0.00, 100.00]B | 1/0/2 → 1/0/2 |
| round2 | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| round2 | emitted_any | 97.37 [88.93, 100.00]B / 91.14 [74.75, 96.94]B | 99.48 [97.38, 100.00]B / 94.09 [85.05, 97.43]B | 36/5/18 → 42/1/12 |
| round2 | above | 96.88 [86.59, 100.00]B / 92.08 [76.12, 97.85]B | 98.96 [94.82, 100.00]B / 94.06 [84.57, 97.85]B | 37/6/16 → 41/2/12 |
| round2 | below | 100.00 [20.65, 100.00]W / 33.33 [0.00, 100.00]B | 100.00 [20.65, 100.00]W / 33.33 [0.00, 100.00]B | 1/0/2 → 1/0/2 |
| mixed | any | 96.63 [87.64, 100.00]B / 86.87 [74.58, 93.59]B | 99.44 [98.65, 100.00]B / 89.40 [76.58, 94.57]B | 40/6/26 → 45/1/21 |
| mixed | breathing | 74.27 [22.71, 93.91]B / 64.34 [20.00, 79.71]B | 86.06 [50.00, 96.13]B / 68.79 [23.08, 83.60]B | 10/10/16 → 12/5/14 |
| mixed | accent | 93.02 [78.49, 98.83]B / 83.67 [64.73, 92.19]B | 97.17 [91.38, 100.00]B / 86.18 [67.75, 93.14]B | 20/10/26 → 24/4/22 |
| mixed | subscript | 0.00 [0.00, 79.35]W / 0.00 [0.00, 65.76]W | 0.00 [0.00, 79.35]W / 0.00 [0.00, 65.76]W | 0/1/2 → 0/1/2 |
| mixed | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| mixed | emitted_any | 96.61 [87.64, 100.00]B / 86.37 [74.34, 93.02]B | 99.43 [98.64, 100.00]B / 88.39 [75.66, 93.54]B | 39/6/27 → 43/1/23 |
| mixed | above | 97.18 [88.04, 100.00]B / 87.31 [75.51, 94.09]B | 100.00 [74.45, 100.00]W / 89.85 [77.54, 94.97]B | 40/5/25 → 45/0/20 |
| mixed | below | 0.00 [0.00, 79.35]W / 0.00 [0.00, 65.76]W | 0.00 [0.00, 79.35]W / 0.00 [0.00, 65.76]W | 0/1/2 → 0/1/2 |
| vouli | any | 88.79 [75.43, 97.35]B / 96.10 [89.25, 99.15]B | 96.55 [90.84, 99.35]B / 96.97 [92.52, 99.13]B | 54/28/9 → 56/8/7 |
| vouli | breathing | 71.51 [30.76, 96.45]B / 82.34 [47.06, 96.17]B | 86.71 [50.00, 100.00]B / 82.34 [47.62, 94.94]B | 14/13/7 → 14/5/7 |
| vouli | accent | 89.37 [76.17, 96.17]B / 95.36 [86.46, 98.93]B | 95.41 [88.02, 98.77]B / 96.39 [90.10, 99.21]B | 36/22/9 → 38/9/7 |
| vouli | subscript | 0.00 [0.00, 79.35]W / — (0 denominator) | 0.00 [0.00, 79.35]W / — (0 denominator) | 0/1/0 → 0/1/0 |
| vouli | diaeresis | 0.00 [0.00, 79.35]W / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/1/0 → 0/0/0 |
| vouli | emitted_any | 89.37 [76.98, 97.34]B / 94.80 [86.63, 98.57]B | 96.52 [90.79, 99.34]B / 96.10 [90.52, 98.90]B | 51/26/12 → 54/8/9 |
| vouli | above | 89.14 [75.78, 97.77]B / 96.10 [89.25, 99.15]B | 96.97 [91.67, 99.60]B / 96.97 [92.52, 99.13]B | 54/27/9 → 56/7/7 |
| vouli | below | 0.00 [0.00, 79.35]W / — (0 denominator) | 0.00 [0.00, 79.35]W / — (0 denominator) | 0/1/0 → 0/1/0 |


| Wave | Any ΔP pp [95%] | Any ΔR pp [95%] | Breathing ΔP / ΔR pp [95%] |
|---|---|---|---|
| parliament | +15.83 [+5.15, +33.22] | +25.30 [+11.18, +41.20] | +22.15 [+9.56, +44.37] / +16.96 [+7.02, +31.04] |
| round1 | +0.57 [+0.00, +2.74] | +1.06 [+0.00, +3.66] | +5.34 [-3.16, +22.13] / +5.07 [+0.00, +23.53] |
| round2 | +2.07 [+0.00, +8.11] | +1.97 [+0.00, +9.27] | +2.58 [-3.12, +32.73] / +7.51 [+0.00, +45.00] |
| mixed | +2.81 [+0.00, +11.94] | +2.52 [+0.00, +5.98] | +11.79 [+0.00, +32.90] / +4.46 [+0.00, +13.09] |
| vouli | +7.76 [+1.56, +15.89] | +0.87 [-1.99, +6.02] | +15.20 [-1.99, +32.11] / +0.00 [-11.11, +10.00] |


## ALL: detector presence and families


| Wave | Measure | Before P / R [95%] | After P / R [95%] | Raw TP/FP/FN before → after |
|---|---|---|---|---|
| parliament | any | 82.62 [74.00, 89.30]B / 68.23 [56.85, 77.26]B | 97.77 [96.43, 98.72]B / 83.96 [78.47, 88.45]B | 262/187/414 → 505/25/171 |
| parliament | breathing | 58.17 [38.55, 74.44]B / 51.86 [35.49, 64.75]B | 85.08 [76.67, 90.65]B / 71.53 [60.70, 80.00]B | 58/110/142 → 116/37/84 |
| parliament | accent | 82.76 [73.88, 89.07]B / 67.29 [54.44, 77.26]B | 96.74 [95.24, 97.92]B / 83.08 [77.02, 88.21]B | 169/150/350 → 376/30/143 |
| parliament | subscript | 11.11 [0.00, 50.00]B / 33.33 [0.00, 100.00]B | 14.29 [0.00, 36.36]B / 66.67 [0.00, 100.00]B | 1/8/2 → 2/12/1 |
| parliament | diaeresis | — (0 denominator) / 0.00 [0.00, 79.35]W | — (0 denominator) / 0.00 [0.00, 79.35]W | 0/0/1 → 0/0/1 |
| parliament | emitted_any | 84.03 [75.98, 90.09]B / 66.62 [55.03, 75.88]B | 97.75 [96.39, 98.71]B / 83.27 [77.86, 87.72]B | 241/165/435 → 496/25/180 |
| parliament | above | 82.88 [74.34, 89.50]B / 68.10 [56.70, 77.20]B | 98.55 [97.33, 99.35]B / 83.86 [78.43, 88.35]B | 259/183/415 → 502/16/172 |
| parliament | below | 11.11 [0.00, 50.00]B / 33.33 [0.00, 100.00]B | 14.29 [0.00, 36.36]B / 66.67 [0.00, 100.00]B | 1/8/2 → 2/12/1 |
| round1 | any | 98.64 [96.55, 99.77]B / 92.37 [87.19, 95.48]B | 98.64 [96.07, 100.00]B / 92.37 [86.96, 95.53]B | 86/5/30 → 86/5/30 |
| round1 | breathing | 74.34 [42.86, 87.57]B / 74.34 [44.19, 86.73]B | 75.62 [46.66, 87.99]B / 75.62 [46.87, 87.70]B | 21/20/20 → 22/19/19 |
| round1 | accent | 96.55 [93.22, 98.58]B / 89.00 [81.11, 93.50]B | 97.47 [94.90, 99.00]B / 89.29 [81.68, 93.55]B | 49/11/38 → 50/8/37 |
| round1 | subscript | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0/3/1 → 0/3/1 |
| round1 | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| round1 | emitted_any | 98.63 [96.54, 99.76]B / 91.86 [86.52, 95.12]B | 98.64 [96.06, 100.00]B / 92.11 [86.70, 95.29]B | 84/5/32 → 85/5/31 |
| round1 | above | 98.91 [97.03, 100.00]B / 92.60 [87.39, 95.79]B | 98.91 [96.50, 100.00]B / 92.60 [87.29, 95.81]B | 86/4/29 → 86/4/29 |
| round1 | below | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0/3/1 → 0/3/1 |
| round2 | any | 97.53 [92.65, 99.68]B / 91.59 [82.09, 96.61]B | 99.07 [96.91, 100.00]B / 92.75 [85.36, 96.57]B | 92/8/29 → 96/3/25 |
| round2 | breathing | 82.09 [48.78, 93.11]B / 77.21 [44.19, 88.99]B | 85.85 [63.04, 93.74]B / 84.14 [59.52, 93.43]B | 22/17/23 → 29/14/16 |
| round2 | accent | 91.80 [81.96, 96.61]B / 84.84 [71.35, 92.12]B | 96.01 [90.98, 98.52]B / 86.44 [75.37, 92.31]B | 45/19/38 → 49/9/34 |
| round2 | subscript | 50.00 [0.00, 100.00]B / 25.00 [0.00, 100.00]B | 50.00 [0.00, 100.00]B / 25.00 [0.00, 100.00]B | 1/1/3 → 1/1/3 |
| round2 | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| round2 | emitted_any | 97.77 [93.54, 99.67]B / 88.97 [78.20, 94.55]B | 99.36 [97.91, 100.00]B / 90.71 [81.75, 95.35]B | 83/7/38 → 89/2/32 |
| round2 | above | 97.52 [92.62, 99.68]B / 91.56 [81.86, 96.72]B | 99.07 [96.90, 100.00]B / 92.72 [85.23, 96.68]B | 91/8/29 → 95/3/25 |
| round2 | below | 50.00 [0.00, 100.00]B / 25.00 [0.00, 100.00]B | 50.00 [0.00, 100.00]B / 25.00 [0.00, 100.00]B | 1/1/3 → 1/1/3 |
| mixed | any | 97.32 [93.10, 99.71]B / 89.08 [81.91, 94.19]B | 99.40 [98.51, 100.00]B / 90.72 [83.57, 94.78]B | 81/9/40 → 87/2/34 |
| mixed | breathing | 82.40 [48.00, 94.81]B / 77.58 [42.85, 89.11]B | 90.06 [65.38, 96.21]B / 79.53 [45.83, 90.13]B | 23/17/23 → 25/9/21 |
| mixed | accent | 93.67 [86.63, 97.44]B / 80.63 [63.23, 91.30]B | 96.77 [93.13, 98.75]B / 81.65 [63.97, 91.96]B | 48/16/38 → 51/8/35 |
| mixed | subscript | 0.00 [0.00, 65.76]W / 0.00 [0.00, 43.45]W | 0.00 [0.00, 65.76]W / 0.00 [0.00, 43.45]W | 0/2/5 → 0/2/5 |
| mixed | diaeresis | 0.00 [0.00, 79.35]W / — (0 denominator) | 0.00 [0.00, 79.35]W / — (0 denominator) | 0/1/0 → 0/1/0 |
| mixed | emitted_any | 97.29 [93.00, 99.70]B / 88.26 [81.06, 93.46]B | 99.39 [98.47, 100.00]B / 89.35 [82.05, 93.78]B | 78/9/43 → 82/2/39 |
| mixed | above | 97.90 [93.66, 100.00]B / 90.06 [83.03, 95.14]B | 100.00 [84.67, 100.00]W / 91.72 [84.78, 95.75]B | 81/7/36 → 87/0/30 |
| mixed | below | 0.00 [0.00, 65.76]W / 0.00 [0.00, 43.45]W | 0.00 [0.00, 65.76]W / 0.00 [0.00, 43.45]W | 0/2/5 → 0/2/5 |
| vouli | any | 87.31 [77.45, 93.80]B / 95.00 [90.78, 97.54]B | 97.07 [93.52, 99.08]B / 94.52 [90.25, 97.17]B | 101/58/21 → 99/12/23 |
| vouli | breathing | 81.65 [59.48, 92.63]B / 87.61 [69.98, 94.75]B | 94.41 [82.14, 99.34]B / 86.15 [66.49, 93.80]B | 27/27/17 → 25/7/19 |
| vouli | accent | 86.25 [75.94, 92.62]B / 93.52 [87.47, 96.94]B | 96.05 [91.84, 98.62]B / 94.49 [88.96, 97.45]B | 65/46/20 → 68/12/17 |
| vouli | subscript | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 79.35]W / 0.00 [0.00, 79.35]W | 0/3/1 → 0/1/1 |
| vouli | diaeresis | 0.00 [0.00, 79.35]W / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/1/0 → 0/0/0 |
| vouli | emitted_any | 88.09 [79.05, 94.07]B / 93.33 [88.16, 96.50]B | 97.52 [94.25, 99.35]B / 93.57 [88.75, 96.54]B | 94/53/28 → 95/10/27 |
| vouli | above | 87.47 [77.72, 94.00]B / 94.99 [90.77, 97.54]B | 97.30 [93.92, 99.27]B / 94.75 [90.60, 97.33]B | 100/57/21 → 99/11/22 |
| vouli | below | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 79.35]W / 0.00 [0.00, 79.35]W | 0/3/1 → 0/1/1 |


| Wave | Any ΔP pp [95%] | Any ΔR pp [95%] | Breathing ΔP / ΔR pp [95%] |
|---|---|---|---|
| parliament | +15.15 [+8.68, +23.37] | +15.73 [+5.11, +26.52] | +26.91 [+14.89, +40.64] / +19.66 [+12.68, +27.87] |
| round1 | +0.00 [-0.81, +0.80] | +0.00 [-1.15, +1.06] | +1.28 [-3.98, +7.96] / +1.28 [-3.34, +7.88] |
| round2 | +1.54 [+0.00, +4.40] | +1.16 [-0.63, +4.62] | +3.76 [-0.59, +14.34] / +6.94 [+2.36, +17.65] |
| mixed | +2.09 [+0.00, +6.31] | +1.64 [+0.00, +4.13] | +7.67 [-1.47, +23.26] / +1.95 [-2.32, +7.00] |
| vouli | +9.76 [+4.83, +16.40] | -0.48 [-3.27, +2.38] | +12.76 [+4.32, +26.62] / -1.46 [-5.74, +1.27] |


## Geometry diagnostics

Diagnostic denominators are recognizer-indexed letter slots, unweighted. The first table covers all 600 lines. Below it, half/ALL diagnostics cover the union of complete lines containing resolved adjudicated words in that cohort; they include other letters on those lines and are not the weighted presence denominator. Clipping remains a border-ink flag, not proof of actual clipping or mark absence.

| Cohort / wave | Lines | loc_unknown | seg_uncertain | Clipped top | Clipped bottom |
|---|---|---|---|---|---|
| parliament | 150 | 600/6497 → 744/6497 (9.24→11.45%) | 843/6497 → 1169/6497 (12.98→17.99%) | 873/6497 → 933/6497 (13.44→14.36%) | 951/6497 → 993/6497 (14.64→15.28%) |
| round1 | 100 | 65/4233 → 65/4233 (1.54→1.54%) | 109/4233 → 117/4233 (2.58→2.76%) | 79/4233 → 79/4233 (1.87→1.87%) | 144/4233 → 144/4233 (3.40→3.40%) |
| round2 | 100 | 57/4210 → 57/4210 (1.35→1.35%) | 119/4210 → 129/4210 (2.83→3.06%) | 78/4210 → 79/4210 (1.85→1.88%) | 108/4210 → 109/4210 (2.57→2.59%) |
| mixed | 100 | 67/4161 → 67/4161 (1.61→1.61%) | 133/4161 → 139/4161 (3.20→3.34%) | 91/4161 → 92/4161 (2.19→2.21%) | 193/4161 → 196/4161 (4.64→4.71%) |
| vouli | 150 | 86/6493 → 77/6493 (1.32→1.19%) | 190/6493 → 191/6493 (2.93→2.94%) | 262/6493 → 262/6493 (4.04→4.04%) | 368/6493 → 370/6493 (5.67→5.70%) |


| Cohort / wave | Lines | loc_unknown | seg_uncertain | Clipped top | Clipped bottom |
|---|---|---|---|---|---|
| JUDGE / parliament | 78 | 358/3367 → 405/3367 (10.63→12.03%) | 493/3367 → 648/3367 (14.64→19.25%) | 429/3367 → 457/3367 (12.74→13.57%) | 539/3367 → 561/3367 (16.01→16.66%) |
| JUDGE / round1 | 33 | 28/1379 → 28/1379 (2.03→2.03%) | 42/1379 → 46/1379 (3.05→3.34%) | 27/1379 → 27/1379 (1.96→1.96%) | 61/1379 → 61/1379 (4.42→4.42%) |
| JUDGE / round2 | 33 | 12/1468 → 12/1468 (0.82→0.82%) | 40/1468 → 42/1468 (2.72→2.86%) | 36/1468 → 36/1468 (2.45→2.45%) | 65/1468 → 66/1468 (4.43→4.50%) |
| JUDGE / mixed | 28 | 16/1156 → 16/1156 (1.38→1.38%) | 26/1156 → 26/1156 (2.25→2.25%) | 32/1156 → 33/1156 (2.77→2.85%) | 56/1156 → 58/1156 (4.84→5.02%) |
| JUDGE / vouli | 35 | 17/1557 → 17/1557 (1.09→1.09%) | 39/1557 → 39/1557 (2.50→2.50%) | 83/1557 → 83/1557 (5.33→5.33%) | 122/1557 → 123/1557 (7.84→7.90%) |
| TUNE / parliament | 57 | 217/2500 → 314/2500 (8.68→12.56%) | 301/2500 → 470/2500 (12.04→18.80%) | 377/2500 → 408/2500 (15.08→16.32%) | 338/2500 → 358/2500 (13.52→14.32%) |
| TUNE / round1 | 35 | 34/1462 → 34/1462 (2.33→2.33%) | 52/1462 → 56/1462 (3.56→3.83%) | 38/1462 → 38/1462 (2.60→2.60%) | 54/1462 → 54/1462 (3.69→3.69%) |
| TUNE / round2 | 27 | 36/1170 → 36/1170 (3.08→3.08%) | 56/1170 → 64/1170 (4.79→5.47%) | 30/1170 → 30/1170 (2.56→2.56%) | 20/1170 → 20/1170 (1.71→1.71%) |
| TUNE / mixed | 31 | 46/1391 → 46/1391 (3.31→3.31%) | 80/1391 → 84/1391 (5.75→6.04%) | 33/1391 → 33/1391 (2.37→2.37%) | 70/1391 → 70/1391 (5.03→5.03%) |
| TUNE / vouli | 37 | 39/1660 → 30/1660 (2.35→1.81%) | 59/1660 → 56/1660 (3.55→3.37%) | 71/1660 → 71/1660 (4.28→4.28%) | 99/1660 → 99/1660 (5.96→5.96%) |
| ALL / parliament | 135 | 575/5867 → 719/5867 (9.80→12.25%) | 794/5867 → 1118/5867 (13.53→19.06%) | 806/5867 → 865/5867 (13.74→14.74%) | 877/5867 → 919/5867 (14.95→15.66%) |
| ALL / round1 | 68 | 62/2841 → 62/2841 (2.18→2.18%) | 94/2841 → 102/2841 (3.31→3.59%) | 65/2841 → 65/2841 (2.29→2.29%) | 115/2841 → 115/2841 (4.05→4.05%) |
| ALL / round2 | 60 | 48/2638 → 48/2638 (1.82→1.82%) | 96/2638 → 106/2638 (3.64→4.02%) | 66/2638 → 66/2638 (2.50→2.50%) | 85/2638 → 86/2638 (3.22→3.26%) |
| ALL / mixed | 59 | 62/2547 → 62/2547 (2.43→2.43%) | 106/2547 → 110/2547 (4.16→4.32%) | 65/2547 → 66/2547 (2.55→2.59%) | 126/2547 → 128/2547 (4.95→5.03%) |
| ALL / vouli | 72 | 56/3217 → 47/3217 (1.74→1.46%) | 98/3217 → 95/3217 (3.05→2.95%) | 154/3217 → 154/3217 (4.79→4.79%) | 221/3217 → 222/3217 (6.87→6.90%) |

Parliament’s full-line loc_unknown rises 600→744 and seg_uncertain 843→1,169 despite better scored presence. The font repair changes component roles/ownership and exposes more ambiguous regions. This is an unresolved segmentation cost, not a successful localization claim.

## What changed and why

- **`ink.analyse`: repair the scale before fitting roles.** TUNE parliament examples contained ~36-pixel bodies but a ~10-pixel component-count mode. The existing toolkit `_xheight` estimator is reused on dark, non-border, substantial components: area ≥ half the 90th-percentile component area, width 0.25–2 heights, height ≥0.6 initial x-height, at least eight supports. Only a >1.5× scale discrepancy triggers `line_glyphs(..., xh_prior=height)`. This reruns existing band/role geometry on unchanged native pixels; it does not invent letters or marks.
- **`case.estimate_font`: qualify smaller bodies and preserve curvature.** The unconditional preliminary lower-quantile shrink in `analyse` is removed. The existing lowercase-body fit can still correct joined-accent inflation, using heights 0.6–1.15 x-height and area ≥0.20 x-height². That support floor excludes small broken strokes that previously drove the meanline into letter ink. Body contacts adjust the toolkit baseline by a robust vertical offset; the toolkit per-column curvature is retained instead of replaced by a new straight line.
- **Detached above ink:** require existing blob photometry `not faint`, and area ≥max(3, 0.008 x-height²). TUNE vouli false marks included pale specks (gray ~198–200 against much darker letters), which the old `faint_letter` check admitted because they were short. This correction also loses some genuine faint marks; the held-out/DEV recall costs are retained below.
- **Capital side marks:** allow short detached components tagged `letter` into the existing bounded upper-left search; only preceding components reaching the capital body establish its left bound. TUNE initial breathings such as `item_61eea590def01747` were tagged `letter`, so the old role check and left bound suppressed them. Existing font-scaled dimensions, photometry and compact-group rules remain; no new gap heuristic is introduced.
- The fixed S4 mark-shape and S5 case-model assets, `markshape.py`, segmentation code, CTC locations, reader and release-gate/composer semantics are unchanged. Breathing improvements are downstream of geometry/input cleanup; there is no new breathing model or naming-threshold search. All generated blobs retain source labels and exact native pixel membership.

TUNE review used only the split-filtered examples in [tune_examples.json](S8_DEV/s8b/tune_examples.json) and [native contact sheet](S8_DEV/s8b/tune_contact.png). Causes were checked against full lines and component/band records. Parliament `item_be16dd5438fa2895` / `item_df34b7a696a366c9` illustrate scale collapse; `item_957b79be3005ef26` / `item_ca3a664735c24149` illustrate letter tops sliced as marks. Other wave witnesses include round1 `item_f06e0245fdad9554`, round2 `item_a4a0aae73b2e227e`, mixed `item_00a27339e0bd0540`, vouli `item_694f8ba4a992e0e8`. Residual examples were retained rather than iteratively fitted. The final [native before/after comparison](S8_DEV/s8b/tune_before_after.png) shows recovered parliament bands/marks and removed pale vouli specks, alongside still-missed round1/round2 circumflexes. Blue is the selected meanline, green above evidence, red below evidence. [Exact detector patch](S8_DEV/s8b/detector.patch).

One native detector candidate was frozen and measured. Native S6 tests first exposed the need to retain a substantial-body downward correction; it was fixed before the measurement. After measurement, a synthetic test component lacking `area` exposed a compatibility error. A missing-attribute fallback to the existing `component_mask` area was added before JUDGE scores were inspected. Native toolkit `Component` always has `area`, so the measured branch and all thresholds are unchanged; [the exact one-expression amendment](S8_DEV/s8b/fixture_compatibility.json) binds both source hashes and [measured source](S8_DEV/s8b/measured_case.py). Completed detector records were not rerun. Evaluation-adapter errors were corrected using hash-bound caches, never by tuning detector outputs.

## 666-line held-out instrument

The exact Wikisource line set is fixed: **19,249 known and 1,176 UNKNOWN character truths**. Presence below is the historical S6 three-zone event instrument (above, below, apostrophe), distinct from DEV per-letter `any`. Atomic name scoring separates compound accents/breathings; punctuation is separate. Known/UNKNOWN membership never changes.

| Measure | Before TP/FP/FN | After TP/FP/FN | Before P/R % | After P/R % | ΔP pp [95%] | ΔR pp [95%] |
|---|---|---|---|---|---|---|
| presence | 4174/56/199 | 4146/29/227 | 98.68/95.45 | 99.31/94.81 | +0.63 [-0.29, +6.04] | -0.64 [-7.93, +0.99] |
| above | 3961/53/108 | 3933/26/136 | 98.68/97.35 | 99.34/96.66 | +0.66 [-0.30, +6.22] | -0.69 [-8.21, +1.02] |
| below | 46/1/50 | 46/1/50 | 97.87/47.92 | 97.87/47.92 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| apostrophe | 167/2/41 | 167/2/41 | 98.82/80.29 | 98.82/80.29 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| marks | 4264/280/382 | 4245/243/401 | 93.84/91.78 | 94.59/91.37 | +0.75 [-1.45, +7.72] | -0.41 [-8.33, +3.53] |
| accent | 2913/141/227 | 2898/118/242 | 95.38/92.77 | 96.09/92.29 | +0.70 [-1.52, +8.16] | -0.48 [-8.41, +3.11] |
| breathing | 1303/138/102 | 1299/124/106 | 90.42/92.74 | 91.29/92.46 | +0.86 [-2.36, +8.07] | -0.28 [-9.13, +5.52] |
| subscript | 46/1/50 | 46/1/50 | 97.87/47.92 | 97.87/47.92 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| dialytika | 2/0/3 | 2/0/3 | 100.00/40.00 | 100.00/40.00 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |

**Observed held-out recall regression:** three-zone TP falls by 28, FP falls by 27, and recall falls 0.64 pp; above-only recall falls 0.69 pp. Document-cluster intervals include zero and are wide, so the supplied “beyond noise” condition is not established either way. Absence of statistical significance is not proof of non-regression. Exact changed known slots are in [heldout_detector_changes.jsonl](S8_DEV/s8b/heldout_detector_changes.jsonl). No second iteration was made.

### Frozen gate tables

Full runtime recomposition uses the unchanged gate, exact saved A/B/E predictions and exact saved extraction coverage, read-only from the R1 worktree. The SF3 hash-bound observation recovery supplies missing state fields from saved measurements and PNG bounds; no missing evidence is assumed clean. **Every baseline SF4 table cell is reproduced exactly.** The instrument remains 80 Google error slots, 10,046 known and 300 UNKNOWN scored slots. These are slot outcomes, not whole-line labels.

| Mode / variant | Corrected | Wrong | Missed | HOLD errors | New errors | Kept controls | HOLD controls | Lines with holds |
|---|---|---|---|---|---|---|---|---|
| PRESENCE / before | 42 | 1 | 2 | 35 | 5 | 9332 | 629 | 348 |
| PRESENCE / after | 43 | 1 | 3 | 33 | 5 | 9332 | 629 | 342 |
| FULL / before | 37 | 0 | 0 | 43 | 3 | 9317 | 646 | 365 |
| FULL / after | 38 | 0 | 1 | 41 | 3 | 9321 | 642 | 359 |
| ENSEMBLE_AB / before | 45 | 2 | 6 | 27 | 6 | 9479 | 481 | 274 |
| ENSEMBLE_AB / after | 45 | 2 | 6 | 27 | 6 | 9488 | 472 | 268 |
| ENSEMBLE_AE / before | 46 | 2 | 6 | 26 | 9 | 9476 | 481 | 261 |
| ENSEMBLE_AE / after | 46 | 2 | 6 | 26 | 9 | 9485 | 472 | 256 |

AB/AE corrected, wrong, missed and new-error counts are unchanged; their control holds fall by nine. PRESENCE and FULL each release one additional correction and one additional missed error. New-error counts do not increase. This narrower gate result does not cancel the physical recall or owner-state regressions. [Gate evidence](S8_DEV/s8b/heldout_gate_summary.json), [error events](S8_DEV/s8b/heldout_gate_events.jsonl).

## Owner pages: boxes and implicit approval

**92/92 owner lines compared; zero missing lines.** The unchanged `scripts/labelfix/box_regression.py` CLI and its maximum-cardinality IoU matcher give **23 removed, 28 added, 5 moved boxes across 39 changed lines**. Baseline coordinates match the saved S6 owner sidecar on all 92 lines. Full count-by-line, including zero-change lines, is in [owner_box_regression.json](S8_DEV/s8b/owner_box_regression.json); [CLI receipt](S8_DEV/s8b/owner_box_cli.json). Matching threshold 0.3, moved threshold 0.6 are unchanged.

Legacy S6 blobs lack source-pixel runs: 554 matched pairs have unknown pixel-change status, so box overlap is not a claim of pixel identity. Owners/notes refer to the frozen S4 slot namespace, carried by saved recognizer starts, rather than new display-slot numbers or nearest-neighbor widening. The original reviewed HTML is unavailable here; no artificial page hash or new approval binding is invented. Approval statements below mean the exact frozen S4 machine snapshot plus the explicit v16/v10 note sets, with named slots excluded. This is a saved-state regression, not a new visual owner certification.

| Note set | Clauses fixed before → after | Implicit slots | Missed approved presence before → after | False vs approved presence before → after |
|---|---|---|---|---|
| owner_notes_review_v16_20261016.jsonl | 58→56 / 74 | 1169 | 6→7 | 0→1 |
| owner_notes_examples_v10_20261016.jsonl | 76→74 / 100 | 1350 | 3→10 | 4→1 |

The note sets overlap and are reported separately. **16 distinct removed boxes touch at least one implicitly approved slot** under these note sets. Every removal is listed below, including named and unresolved slots; complete before/after clauses and per-slot missed/false states are in [owner_note_checks.jsonl](S8_DEV/s8b/owner_note_checks.jsonl), [owner_implicit_checks.jsonl](S8_DEV/s8b/owner_implicit_checks.jsonl), and [owner_box_removals.jsonl](S8_DEV/s8b/owner_box_removals.jsonl).

| Line | Removed kind / bbox | Old S4 slot | Scope by note set |
|---|---|---|---|
| 02a3a2a6-p000041-l0005 | above / [59, 14, 74, 32] | 2 | examples: implicitly approved |
| 02a3a2a6-p000041-l0005 | above / [329, 15, 349, 29] | 8 | examples: implicitly approved |
| 02a3a2a6-p000041-l0005 | above / [529, 9, 551, 29] | 12 | examples: implicitly approved |
| 02a3a2a6-p000041-l0005 | above / [810, 7, 824, 25] | 19 | examples: implicitly approved |
| 02a3a2a6-p000041-l0005 | above / [1157, 4, 1178, 18] | 28 | examples: named |
| 02a3a2a6-p000046-l0014 | above / [164, 8, 178, 25] | 4 | review: implicitly approved; examples: implicitly approved |
| 02a3a2a6-p000318-l0014 | above / [154, 5, 168, 25] | None | examples: unresolved |
| 02a3a2a6-p000318-l0014 | above / [413, 4, 425, 22] | 8 | examples: implicitly approved |
| 2793d64c-p000070-l0014 | above / [484, 19, 488, 21] | 12 | review: implicitly approved |
| 51fe7386-p000024-l0015 | above / [551, 16, 565, 35] | 11 | review: implicitly approved; examples: implicitly approved |
| 51fe7386-p000024-l0015 | above / [957, 20, 971, 35] | 20 | review: implicitly approved; examples: implicitly approved |
| 51fe7386-p000026-l0016 | above / [174, 31, 195, 38] | 4 | examples: implicitly approved |
| 51fe7386-p000026-l0016 | above / [337, 31, 350, 36] | 8 | examples: implicitly approved |
| 51fe7386-p000026-l0016 | above / [375, 26, 381, 36] | 9 | examples: implicitly approved |
| 51fe7386-p000026-l0016 | above / [1187, 19, 1193, 25] | None | examples: unresolved |
| 8b6b0de9-p000004-l0028 | above / [50, 19, 74, 28] | 2 | review: implicitly approved |
| 8b6b0de9-p000004-l0028 | above / [222, 11, 232, 27] | None | review: unresolved |
| 8b6b0de9-p000004-l0029 | above / [19, 16, 33, 31] | 1 | examples: named |
| 8b6b0de9-p000004-l0029 | above / [115, 10, 129, 30] | 4 | examples: named |
| 8b6b0de9-p000007-l0021 | above / [207, 14, 219, 30] | 7 | examples: implicitly approved |
| 8b6b0de9-p000007-l0021 | above / [472, 8, 484, 25] | 14 | examples: implicitly approved |
| 8b6b0de9-p000007-l0021 | above / [821, 8, 832, 21] | None | examples: unresolved |
| 8b6b0de9-p000018-l0026 | above / [355, 26, 357, 28] | 9 | examples: implicitly approved |


| Line | Removed | Added | Moved |
|---|---|---|---|
| 02a3a2a6-p000041-l0005 | 5 | 1 | 0 |
| 02a3a2a6-p000046-l0014 | 1 | 0 | 0 |
| 02a3a2a6-p000046-l0025 | 0 | 0 | 0 |
| 02a3a2a6-p000307-l0003 | 0 | 1 | 0 |
| 02a3a2a6-p000318-l0014 | 2 | 0 | 0 |
| 02a3a2a6-p000318-l0017 | 0 | 0 | 0 |
| 177b717d-p000013-l0009 | 0 | 0 | 0 |
| 177b717d-p000017-l0012 | 0 | 0 | 0 |
| 177b717d-p000072-l0001 | 0 | 0 | 0 |
| 177b717d-p000097-l0007 | 0 | 0 | 0 |
| 177b717d-p000097-l0010 | 0 | 0 | 0 |
| 177b717d-p000104-l0007 | 0 | 0 | 0 |
| 2793d64c-p000033-l0022 | 0 | 1 | 0 |
| 2793d64c-p000048-l0004 | 0 | 0 | 0 |
| 2793d64c-p000048-l0010 | 0 | 0 | 0 |
| 2793d64c-p000070-l0010 | 0 | 0 | 0 |
| 2793d64c-p000070-l0014 | 1 | 0 | 0 |
| 2793d64c-p000072-l0007 | 0 | 1 | 0 |
| 384c3f89-p000030-l0010 | 0 | 0 | 0 |
| 384c3f89-p000030-l0021 | 0 | 1 | 0 |
| 384c3f89-p000030-l0029 | 0 | 0 | 0 |
| 384c3f89-p000050-l0016 | 0 | 0 | 0 |
| 384c3f89-p000050-l0027 | 0 | 1 | 0 |
| 384c3f89-p000053-l0010 | 0 | 0 | 0 |
| 384c3f89-p000053-l0021 | 0 | 1 | 0 |
| 384c3f89-p000053-l0023 | 0 | 0 | 0 |
| 384c3f89-p000053-l0028 | 0 | 1 | 0 |
| 384c3f89-p000059-l0027 | 0 | 2 | 0 |
| 384c3f89-p000068-l0028 | 0 | 1 | 0 |
| 384c3f89-p000068-l0036 | 0 | 1 | 0 |
| 384c3f89-p000091-l0011 | 0 | 0 | 0 |
| 384c3f89-p000091-l0014 | 0 | 0 | 0 |
| 384c3f89-p000091-l0027 | 0 | 0 | 0 |
| 384c3f89-p000091-l0029 | 0 | 1 | 0 |
| 384c3f89-p000091-l0039 | 0 | 0 | 0 |
| 384c3f89-p000096-l0004 | 0 | 0 | 0 |
| 384c3f89-p000096-l0010 | 0 | 0 | 0 |
| 384c3f89-p000096-l0031 | 0 | 0 | 0 |
| 384c3f89-p000121-l0023 | 0 | 1 | 0 |
| 384c3f89-p000121-l0024 | 0 | 1 | 0 |
| 384c3f89-p000142-l0002 | 0 | 1 | 0 |
| 384c3f89-p000142-l0010 | 0 | 0 | 0 |
| 384c3f89-p000142-l0014 | 0 | 0 | 0 |
| 384c3f89-p000170-l0024 | 0 | 0 | 0 |
| 384c3f89-p000170-l0031 | 0 | 1 | 0 |
| 384c3f89-p000179-l0022 | 0 | 0 | 0 |
| 384c3f89-p000182-l0006 | 0 | 1 | 0 |
| 384c3f89-p000182-l0023 | 0 | 1 | 0 |
| 384c3f89-p000182-l0031 | 0 | 0 | 0 |
| 384c3f89-p000183-l0005 | 0 | 0 | 0 |
| 384c3f89-p000183-l0009 | 0 | 0 | 0 |
| 384c3f89-p000183-l0020 | 0 | 0 | 0 |
| 384c3f89-p000183-l0022 | 0 | 1 | 0 |
| 384c3f89-p000205-l0005 | 0 | 2 | 0 |
| 51fe7386-p000024-l0015 | 2 | 0 | 0 |
| 51fe7386-p000024-l0016 | 0 | 0 | 0 |
| 51fe7386-p000024-l0020 | 0 | 1 | 0 |
| 51fe7386-p000026-l0016 | 4 | 0 | 0 |
| 602cc72e-p000113-l0009 | 0 | 1 | 0 |
| 602cc72e-p000113-l0016 | 0 | 2 | 2 |
| 602cc72e-p000113-l0030 | 0 | 0 | 0 |
| 602cc72e-p000155-l0009 | 0 | 0 | 1 |
| 602cc72e-p000167-l0027 | 0 | 0 | 0 |
| 602cc72e-p000353-l0006 | 0 | 1 | 1 |
| 8b6b0de9-p000004-l0011 | 0 | 0 | 0 |
| 8b6b0de9-p000004-l0028 | 2 | 0 | 1 |
| 8b6b0de9-p000004-l0029 | 2 | 0 | 0 |
| 8b6b0de9-p000007-l0011 | 0 | 0 | 0 |
| 8b6b0de9-p000007-l0021 | 3 | 0 | 0 |
| 8b6b0de9-p000007-l0030 | 0 | 0 | 0 |
| 8b6b0de9-p000008-l0001 | 0 | 0 | 0 |
| 8b6b0de9-p000008-l0002 | 0 | 0 | 0 |
| 8b6b0de9-p000008-l0019 | 0 | 0 | 0 |
| 8b6b0de9-p000008-l0024 | 0 | 0 | 0 |
| 8b6b0de9-p000009-l0024 | 0 | 0 | 0 |
| 8b6b0de9-p000011-l0007 | 0 | 0 | 0 |
| 8b6b0de9-p000011-l0014 | 0 | 0 | 0 |
| 8b6b0de9-p000012-l0006 | 0 | 0 | 0 |
| 8b6b0de9-p000016-l0013 | 0 | 0 | 0 |
| 8b6b0de9-p000016-l0029 | 0 | 0 | 0 |
| 8b6b0de9-p000018-l0023 | 0 | 0 | 0 |
| 8b6b0de9-p000018-l0026 | 1 | 0 | 0 |
| 8b6b0de9-p000021-l0007 | 0 | 0 | 0 |
| 8b6b0de9-p000021-l0012 | 0 | 0 | 0 |
| 8b6b0de9-p000021-l0028 | 0 | 0 | 0 |
| 9c1dca9b-p000005-l0017 | 0 | 0 | 0 |
| 9c1dca9b-p000015-l0051 | 0 | 0 | 0 |
| 9c1dca9b-p000015-l0057 | 0 | 0 | 0 |
| 9c1dca9b-p000015-l0060 | 0 | 1 | 0 |
| 9c1dca9b-p000015-l0062 | 0 | 0 | 0 |
| 9c1dca9b-p000015-l0065 | 0 | 0 | 0 |
| 9c1dca9b-p000015-l0067 | 0 | 0 | 0 |

One returned non-preposed upper box in the regression set crosses its receiving slot’s scalar meanline: `22fda82b-p000109-l0023`, start 2, box `[96,34,106,48]`, meanline 47.5. This survives existing whole-line proposal union; it is a half-pixel boundary exception, not proof that the letter is safely uncut. DEV has zero returned-box boundary exceptions. [Boundary ledger](S8_DEV/s8b/regression_detector_boundary_exceptions.json). Native ink/labels and blob-pixel membership checks pass, but the owner’s complete geometric/no-regression requirement is not closed.

## Validation and reproduction

**409 detector/gate regression tests passed** (`tests_detector_gate.log`); the 12 targeted native S6/mark-shape tests also pass. Independent audit rebuilt **240 score cells and 480 intervals**, verified the disjoint split/weights, all 976 word truths, exact saved SF4 baseline tables, saved S6 owner-box parity and **3728 protected files unchanged**. Model assets, frozen cards/keys/truth, reader, composer and gate sources are byte-identical. The broad-suite attempt was interrupted after 124 passes/one socket-fixture error under the network-OFF audit hook; it is not reported as a full-suite pass. The subsequent selected suite excludes that server fixture and the unrelated CLI/thread path that blocked the broad run. [Tests](S8_DEV/s8b/tests_detector_gate.log), [audit](S8_DEV/s8b/validation.log).

Commands use `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD` and `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B`:

```sh
python -B scripts/labelfix/s8b_split.py
python -B scripts/labelfix/s8b_measure.py
python -B scripts/labelfix/s8b_regressions.py
python -B scripts/labelfix/box_regression.py docs/records/labelfix/spellcheck/S8_DEV/s8b/owner_before_boxes.json docs/records/labelfix/spellcheck/S8_DEV/s8b/owner_after_boxes.json --out docs/records/labelfix/spellcheck/S8_DEV/s8b/owner_box_cli.json
python -B scripts/labelfix/s8b_validate.py
python -B scripts/labelfix/s8b_report.py
```

The measurement scripts reject sockets and writes outside `S8_DEV/s8b`, bind every cache to candidate/crop hashes, and prohibit recognizer construction through the existing offline preparation guard. Reruns reuse completed detector caches for audit/reaggregation; they do not add a detector tuning round. The frozen text-only held-out instrument functions are extracted unchanged from `l1e_measure.py` to avoid importing its GPU CLI. No torch model is loaded.

## Plan B — independent pixel presence reader

**Needed: yes.** JUDGE parliament recall is 84.35%, with residual segmentation/clipping ambiguity, and this candidate fails owner/physical regression checks. The detector should pass its combining-mark presence role to a second, independently built pixel reader only after a separately reviewed experiment succeeds. The detector remains responsible for apostrophes, segmentation and clipping; that planned division is not implemented here.

**Architecture/input:** R1 is the existing four-stage residual patch CNN, grayscale plus recognizer-span mask, with letter embedding and four mark heads (`scripts/labelfix/clariden/r1_model.py`). A concrete independent candidate is a raw-grayscale line-strip patch transformer with a monotonic per-slot presence head and an explicit UNKNOWN output. It sees wider vertical/horizontal context, no R1 span-mask channel, no letter embedding, no R1 weights/features/logits or detector mark proposals. Its body/slot locator must be independently built and audited; if cached base-only CTC spans are retained as a temporary locator, that shared dependency is declared and tested as a correlated-failure stratum. Reinitializing R1 or changing its seed alone does not qualify.

**Data/labels:** prepare a new document-disjoint five-wave training pool, with parliament emphasized but every wave and font-size/quality stratum represented. A planning starting point is ~10,000 double-read word cards (~50,000 letter slots), retaining natural-frequency positive and blank controls plus separately tagged rare breathing/compound/subscript strata. Require full printed transcription, above/below presence, family/shape, clipping/foreign-ink flags and UNKNOWN, with independent tiebreaks. Add hard speck, pale mark, broken-body, capital-side and locator-failure negatives. Exclude all current DEV documents and every 666-instrument document from model fitting; do not use either reader’s predicted absence or the detector as blank truth. Labels and any oversampling probabilities need the same ID/hash/weight custody as S8a6.

**Budget (proposal, not a measured ETA or launch):** allow 40–100 reader-hours for the first double-read/adjudicated tranche, then reassess agreement and rare-class coverage. Reserve a 2 GPU-hour feasibility pilot and a provisional 24 GPU-hour single-accelerator cap for the new architecture’s training/calibration experiments; benchmark actual throughput and memory before scheduling. Stop at the pilot if crop/locator quality or label coverage cannot support independent absence evidence. No new compute or annotation job is authorized/launched by S8b.

**Show independence:** retain disjoint implementation/weight/checkpoint receipts, input ablations and shared-dependency inventory. Report R1-vs-reader-2 error contingency tables and the weighted joint false-absence rate on print-positive slots, stratified by wave/font, mask status, faintness, clipping and localization. Use document-cluster intervals for shared misses; compare observed joint error with marginal errors as a diagnostic, without assuming their product. Architectural difference is necessary evidence, not proof of statistical independence. Reader disagreement or either UNKNOWN must hold; absence needs two individually qualified reader negatives.

**Validate on this DEV:** preregister the architecture, thresholds, eligibility, two-reader decision table and no-regression criteria before scoring reader 2. Use the existing TUNE documents only for calibration, keep fixed S8a6 weights, then evaluate JUDGE once and publish TUNE/JUDGE/ALL marginal and joint-presence tables, family results, UNKNOWN/clipping coverage and error witnesses. Reader 2 may not train on any of these adjudicated DEV labels. JUDGE has now been consumed to assess S8b and motivate Plan B, so reuse is explicitly a retrospective comparison; final generalization needs a fresh document-held-out print-adjudicated confirmation set. Also replay the unchanged 666 frozen-gate tables and owner-box/implicit-approval instruments. Any future reader-vs-reader gate change requires its own implementation/review task; this report does not change release semantics.

S8b RESULT: JUDGE detector presence P/R parliament 99.07/84.35 (was 82.6/68.2), vouli 97.75/91.55, round1 97.39/91.66, round2 99.23/90.82, mixed 99.36/92.27; breathing P/R parliament 86.36/72.68; held-out regression physical recall -0.64 pp (28 TP lost), marks recall -0.41 pp; box regression 23 removed/28 added/5 moved (16 approved removals); Plan B needed yes

## Options for the owner (track lead, after coordinator review, 17 Oct) — options, not decisions

### Option (i): per-regime adoption of the S8b detector (cheap test)
- **Regime signal:** for label correction no pixel regime detector is needed: every training line carries its source/wave
  (`import_real_v2_train.jsonl`: `wave`, `source`), so the detector can be selected by wave — S8b for `parliament` and `vouli`, S6 elsewhere
  (round1/round2/mixed show no S8b gain on JUDGE; the Wikisource-like owner pages regress under S8b). A pixel regime detector is only needed
  for unlabeled inference outside the harvest, which this track does not do.
- **What it needs:** one bounded iteration that wires wave-selected detectors into the L1 runtime (code + receipts), the same JUDGE-style
  table per wave, and the owner-page/666 regression checks run under S6 (they must then be unchanged by construction). Parliament recall stays
  at S8b's 84.4% [76.3, 90.2] — still short of ~90%, so (i) raises coverage but does not by itself meet the Plan-B trigger.

### Option (ii): Plan B, independent second pixel presence reader (durable fix)
As above. Two entry variants:
- **(ii-a) Full:** ~10k double-read word cards, 40–100 reader-hours, 2 GPU-h pilot, 24 GPU-h cap (above).
- **(ii-b) Cheaper first step (coordinator's suggestion), with two constraints from standing rules:**
  1. *Independence.* The 2.06 M R1 agreement positions are R1's own training labels (C1 agreement). A reader trained on them inherits R1's
     label errors — the very shared-error mechanism the ensemble caveat names — so it would not be an independent second signal for the
     two-signal rule. Usable only if independence is then demonstrated empirically on print truth (joint false-absence on print-positive
     slots, stratified), and the report must state the shared-label dependency. A safer variant trains on positions where R1 agreement AND
     an independent source (Google label or the detector) concur, still declared as a shared dependency.
  2. *Locked strata.* (ii) and (i-b) are locked, never-tune comparison sets (release_exclusions); they cannot be used for calibration. Allowed
     for calibration/validation: S8 DEV TUNE (and its unread cards once adjudicated), the 666 continuity instrument (Wikisource, held-out from
     training), and the R0 new-source dev pool (273 cards). JUDGE is consumed; final confirmation needs a fresh document-held-out
     print-adjudicated set; (ii)/(i-b) stay as the final locked check.
  With those constraints the 10k double-read cards become a later refinement, as suggested; budget for (ii-b): the 2 GPU-h pilot, then reassess.
