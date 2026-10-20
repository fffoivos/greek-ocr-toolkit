# S8a6 — print-adjudicated training-wave DEV

**978 data cards read: parliament 578, round1/round2/mixed/vouli 100 each; 976 resolved, two UNKNOWN.** The cut contains 1,063 items with 85 controls. The other 671 data cards and 59 controls remain unadjudicated. This is training-wave DEV, not a held-out test.

Analysis HEAD `bd59f370f7db4a373e393103f5fbbb7c970caf8b`. Network OFF; saved evidence only; zero inference; no detector, reader, gate, deck or key edits. [Machine-readable evidence](S8_DEV/evidence/dev_truth.jsonl.gz), SHA256 `bbfba1509215d60517ab651324a44323f6a5cedd8378c97fdcadab48bc78a3ec`. The gzip contains metadata, all 1,793 item states and one summary record, with ID joins, votes, weights, letter-slot outcomes, input hashes and both cluster intervals.

## Readers and adjudication

**R1 82/84, R2 82/84 (97.62% each); zero shared control misses.** The 85th control, `item_fa47d3102d8d11bd`, is a control-construction defect: the print is **ἔχη**, without iota subscript; both options/key contain a subscript. Both readers correctly rejected both options. Exclusion follows the track lead’s image verification; the frozen key is preserved.

| Reader | Correct / valid controls | Missed control IDs |
|---|---|---|
| r1 | 82/84 | `item_8145fa65feecf1d0`, `item_9eaa0b2a891b0fdc` |
| r2 | 82/84 | `item_982b027efc109f25`, `item_ce182ecedbeb88d4` |


| Wave | R1/R2 data-form agreement | Adjudicated | Resolved truth | UNKNOWN | Unread data cards |
|---|---|---|---|---|---|
| parliament | 561/578 (97.06%) | 578 | 576 | 2 | 0 |
| round1 | 95/100 (95.00%) | 100 | 100 | 0 | 107 |
| round2 | 94/100 (94.00%) | 100 | 100 | 0 | 138 |
| mixed | 92/100 (92.00%) | 100 | 100 | 0 | 157 |
| vouli | 94/100 (94.00%) | 100 | 100 | 0 | 269 |

Tiebreak: **42/42 resolved; 16 support R1 and 26 support R2; zero third-distinct or unresolved outcomes.** Agreement above includes the two shared-unreadable parliament cards. Third-reader A/B letters are decoded against the tiebreak deck, never the original options. Forms, including none-of-these transcriptions, vote by canonical text. Majority unreadable or no majority becomes UNKNOWN and is excluded, counted and never scored as absence.

UNKNOWN IDs: `item_8fc8c43f607cb4e4`, `item_cc364be89d651c15`.

The `r?_000…270` files are checked against full-deck slices 0–359; `r?_cut_*` against the 703-item remaining-cut deck. Reader output ordering differs, so all joins use IDs. Exactly 1,063 unique IDs per reader cover the cut; there are no duplicate votes.

## Population, weights and uncertainty

The target population is the **4,942 connected word groups** in the 600-line DEV census, not only disagreements or mark-positive words. Data-card inclusion is 1 for disagreements and the stored exact ceil(5%)/population fraction for all-agree words. The second-stage wave fraction is 578/578 for parliament and 100/N for each other wave’s data deck. Use **w = 1/(card inclusion × wave cut fraction)** for every card and all its slots. The shuffled first 360 plus seeded remainder are treated as the coordinator’s marginal wave cut; no additional conditional cut probabilities were supplied. Ratios use weighted sums (Hájek); unread cards supply no truth. UNKNOWN weights are excluded without redistributing them.

**Intervals are 95% document-cluster percentile bootstrap (B), 4,000 replicates, seed 20261017 plus wave index; line-cluster bootstrap is also retained in the evidence.** Fixed inclusion weights are carried through cluster resampling; no finite-population correction is applied. Replicates with zero relevant denominator are omitted; valid replicate counts are retained. For a degenerate bootstrap only, W denotes a Wilson interval using Kish effective event n. W ignores clustering and is a boundary-data diagnostic; neither method includes reader error or proves performance outside these DEV lines. Undefined P/R denominators remain undefined.

| Wave | Word population | Deck D / agree | Cut D / agree | Weight D / agree | Resolved Σw | UNKNOWN Σw |
|---|---|---|---|---|---|---|
| parliament | 1224 | 544 / 34 | 544 / 34 | 1.0000 / 20.0000 | 1222.00 | 2.00 |
| round1 | 835 | 173 / 34 | 85 / 15 | 2.0700 / 40.3041 | 780.51 | 0.00 |
| round2 | 853 | 205 / 33 | 89 / 11 | 2.3800 / 46.7345 | 725.90 | 0.00 |
| mixed | 804 | 228 / 29 | 86 / 14 | 2.5700 / 51.0455 | 935.66 | 0.00 |
| vouli | 1226 | 323 / 46 | 84 / 16 | 3.6900 / 72.4363 | 1468.94 | 0.00 |

Σw need not equal the census total after random cut sampling and UNKNOWN exclusion; it is not a count of distinct adjudicated words.

## Source word accuracy

Each cell is **weighted % [95% interval]; unweighted correct/resolved cards**. All resolved data cards, including the tagged elision subset, are included here. Equality preserves ink and misprints, case, punctuation, boundaries and missing elision; NFC/NFD equivalents and word-final codec v2.1 elision aliases count as one atom. U+1FBF before a capital attaches as smooth breathing. Printed keraia identities remain significant. **Frozen AB is the saved ENSEMBLE_AB proposal**, including HOLD lines, not an assertion that it was released.

| Wave | google | r1_A | detector_original | frozen_AB |
|---|---|---|---|---|
| parliament | 96.07 [94.52, 97.29]B; 528/576 | 97.05 [95.70, 98.07]B; 540/576 | 57.20 [42.64, 68.95]B; 53/576 | 96.56 [94.98, 97.78]B; 534/576 |
| round1 | 96.02 [92.18, 98.29]B; 85/100 | 95.76 [91.88, 98.18]B; 84/100 | 80.11 [67.90, 87.29]B; 25/100 | 93.90 [89.44, 96.85]B; 77/100 |
| round2 | 95.08 [90.63, 97.50]B; 85/100 | 95.74 [91.97, 98.11]B; 87/100 | 74.75 [58.11, 83.77]B; 23/100 | 96.07 [92.58, 98.48]B; 88/100 |
| mixed | 90.15 [75.39, 97.34]B; 83/100 | 92.07 [77.45, 98.98]B; 90/100 | 73.39 [57.40, 84.36]B; 22/100 | 91.52 [76.66, 98.50]B; 88/100 |
| vouli | 96.23 [93.50, 98.11]B; 85/100 | 96.23 [93.50, 98.06]B; 85/100 | 81.16 [69.70, 88.33]B; 25/100 | 95.48 [92.22, 97.57]B; 82/100 |

All-agree adjudication is not assumed error-free: parliament 0/34 shared-error cards, round1 0/15 shared-error cards, round2 0/11 shared-error cards, mixed 1/14 shared-error cards, vouli 0/16 shared-error cards. Shared-error IDs: `item_eb92e68ee47af29f`. The small, highly weighted mixed all-agree sample is responsible for much of that wave’s word-accuracy uncertainty.

## Presence precision / recall

**Primary detector `any` uses saved physical above-or-below ink evidence, including unnamed detections.** R1-A `any` uses its saved emitted marks. Breathing, accent, subscript and diaeresis use emitted family presence for both sources; family identity therefore depends on naming. An acute/grave/circumflex swap remains accent-present; smooth/rough remains breathing-present. Detector `emitted_any` and physical above/below zone results are given separately below. This prevents a naming error being misreported as a physical detection loss.

Scores use the union of letter slots under a mark-blind base alignment with punctuation anchors and deterministic diagonal/delete/insert ties. Paired letter substitutions are location pairs for presence; base correctness is evaluated by word accuracy. Deleted positive truth slots count FN and inserted positive predictions count FP. Case does not alter presence alignment. Localisation-unknown, fused, uncertain and clipped slots stay in the scored cohort when the word truth is known; absent detector evidence is an emission miss, not proof of blank print. Elision is excluded from combining-mark presence and evaluated separately. These per-slot any-mark results are not the older S6 three-zone event denominator.

| Wave | Resolved word cards | Print letter slots | Weighted print letter slots | Union slots detector / R1-A | Documents / lines |
|---|---|---|---|---|---|
| parliament | 576 | 3309 | 6501.00 | 3311 / 3311 | 27 / 135 |
| round1 | 100 | 524 | 4143.41 | 525 / 525 | 51 / 68 |
| round2 | 100 | 522 | 3859.28 | 523 / 523 | 27 / 60 |
| mixed | 100 | 500 | 3660.30 | 501 / 501 | 25 / 59 |
| vouli | 100 | 618 | 7780.12 | 619 / 619 | 41 / 72 |


| Wave | Detector any P / R | R1-A any P / R | Baseline loc_unknown | Baseline seg_uncertain |
|---|---|---|---|---|
| parliament | 82.62 [74.00, 89.30]B / 68.23 [56.85, 77.26]B | 99.39 [98.86, 99.78]B / 99.77 [99.49, 100.00]B | 600/6497 (9.24%) | 843/6497 (12.98%) |
| round1 | 98.10 [95.46, 99.68]B / 92.11 [86.60, 95.36]B | 99.24 [98.11, 100.00]B / 99.24 [98.07, 100.00]B | 66/4233 (1.56%) | 110/4233 (2.60%) |
| round2 | 97.53 [92.65, 99.68]B / 91.59 [82.09, 96.61]B | 100.00 [86.59, 100.00]W / 99.42 [97.72, 100.00]B | 58/4210 (1.38%) | 118/4210 (2.80%) |
| mixed | 97.32 [93.10, 99.71]B / 89.08 [81.91, 94.19]B | 99.19 [97.67, 100.00]B / 99.73 [98.96, 100.00]B | 64/4161 (1.54%) | 128/4161 (3.08%) |
| vouli | 86.96 [77.00, 93.47]B / 95.24 [91.09, 97.70]B | 98.82 [97.45, 99.74]B / 99.76 [99.12, 100.00]B | 88/6493 (1.36%) | 190/6493 (2.93%) |

Baseline rates above cover all 600 original lines and use recogniser-indexed letters; they are not cut-weighted adjudication rates.

Raw TP/FP/FN beside family results are unweighted letter-slot counts. Weighted TP/FP/FN/TN, effective n and every denominator are in the gzip.

### detector_original

| Wave | Family | Weighted precision % [95%] | Weighted recall % [95%] | Raw TP / FP / FN |
|---|---|---|---|---|
| parliament | any | 82.62 [74.00, 89.30]B | 68.23 [56.85, 77.26]B | 262 / 187 / 414 |
| parliament | breathing | 58.17 [38.55, 74.44]B | 51.86 [35.49, 64.75]B | 58 / 110 / 142 |
| parliament | accent | 82.76 [73.88, 89.07]B | 67.29 [54.44, 77.26]B | 169 / 150 / 350 |
| parliament | subscript | 11.11 [0.00, 50.00]B | 33.33 [0.00, 100.00]B | 1 / 8 / 2 |
| parliament | diaeresis | — (0 denominator) | 0.00 [0.00, 79.35]W | 0 / 0 / 1 |
| round1 | any | 98.10 [95.46, 99.68]B | 92.11 [86.60, 95.36]B | 85 / 7 / 31 |
| round1 | breathing | 71.58 [40.00, 86.37]B | 74.34 [44.44, 86.35]B | 21 / 23 / 20 |
| round1 | accent | 95.93 [91.53, 98.49]B | 88.71 [80.51, 93.25]B | 48 / 13 / 39 |
| round1 | subscript | 0.00 [0.00, 56.15]W | 0.00 [0.00, 79.35]W | 0 / 3 / 1 |
| round1 | diaeresis | — (0 denominator) | — (0 denominator) | 0 / 0 / 0 |
| round2 | any | 97.53 [92.65, 99.68]B | 91.59 [82.09, 96.61]B | 92 / 8 / 29 |
| round2 | breathing | 81.23 [46.94, 92.32]B | 77.21 [44.19, 88.99]B | 22 / 18 / 23 |
| round2 | accent | 91.77 [81.82, 96.61]B | 84.45 [70.53, 91.78]B | 44 / 19 / 39 |
| round2 | subscript | 50.00 [0.00, 100.00]B | 25.00 [0.00, 100.00]B | 1 / 1 / 3 |
| round2 | diaeresis | — (0 denominator) | — (0 denominator) | 0 / 0 / 0 |
| mixed | any | 97.32 [93.10, 99.71]B | 89.08 [81.91, 94.19]B | 81 / 9 / 40 |
| mixed | breathing | 80.73 [47.90, 93.30]B | 77.58 [42.85, 89.11]B | 23 / 19 / 23 |
| mixed | accent | 93.64 [86.58, 97.44]B | 80.28 [63.11, 91.19]B | 47 / 16 / 39 |
| mixed | subscript | 0.00 [0.00, 65.76]W | 0.00 [0.00, 43.45]W | 0 / 2 / 5 |
| mixed | diaeresis | 0.00 [0.00, 79.35]W | — (0 denominator) | 0 / 1 / 0 |
| vouli | any | 86.96 [77.00, 93.47]B | 95.24 [91.09, 97.70]B | 102 / 60 / 20 |
| vouli | breathing | 77.09 [53.82, 89.56]B | 88.33 [71.52, 95.21]B | 28 / 36 / 16 |
| vouli | accent | 85.82 [75.63, 92.30]B | 94.17 [88.55, 97.35]B | 67 / 48 / 18 |
| vouli | subscript | 0.00 [0.00, 56.15]W | 0.00 [0.00, 79.35]W | 0 / 3 / 1 |
| vouli | diaeresis | — (0 denominator) | — (0 denominator) | 0 / 0 / 0 |


### r1_A

| Wave | Family | Weighted precision % [95%] | Weighted recall % [95%] | Raw TP / FP / FN |
|---|---|---|---|---|
| parliament | any | 99.39 [98.86, 99.78]B | 99.77 [99.49, 100.00]B | 673 / 8 / 3 |
| parliament | breathing | 98.65 [97.23, 99.69]B | 99.32 [97.51, 100.00]B | 198 / 4 / 2 |
| parliament | accent | 99.26 [98.61, 99.73]B | 99.91 [99.66, 100.00]B | 518 / 8 / 1 |
| parliament | subscript | 66.67 [0.00, 100.00]B | 66.67 [0.00, 100.00]B | 2 / 1 / 1 |
| parliament | diaeresis | 100.00 [20.65, 100.00]W | 100.00 [20.65, 100.00]W | 1 / 0 / 0 |
| round1 | any | 99.24 [98.11, 100.00]B | 99.24 [98.07, 100.00]B | 113 / 3 / 3 |
| round1 | breathing | 100.00 [65.93, 100.00]W | 98.72 [93.89, 100.00]B | 40 / 0 / 1 |
| round1 | accent | 100.00 [84.96, 100.00]W | 98.84 [97.18, 99.77]B | 83 / 0 / 4 |
| round1 | subscript | 14.29 [0.00, 50.00]B | 100.00 [20.65, 100.00]W | 1 / 6 / 0 |
| round1 | diaeresis | — (0 denominator) | — (0 denominator) | 0 / 0 / 0 |
| round2 | any | 100.00 [86.59, 100.00]W | 99.42 [97.72, 100.00]B | 119 / 0 / 2 |
| round2 | breathing | 98.02 [94.67, 100.00]B | 98.02 [94.88, 100.00]B | 43 / 2 / 2 |
| round2 | accent | 98.81 [97.54, 100.00]B | 99.20 [97.49, 100.00]B | 81 / 3 / 2 |
| round2 | subscript | 100.00 [51.01, 100.00]W | 100.00 [51.01, 100.00]W | 4 / 0 / 0 |
| round2 | diaeresis | — (0 denominator) | — (0 denominator) | 0 / 0 / 0 |
| mixed | any | 99.19 [97.67, 100.00]B | 99.73 [98.96, 100.00]B | 120 / 3 / 1 |
| mixed | breathing | 100.00 [69.08, 100.00]W | 100.00 [69.08, 100.00]W | 46 / 0 / 0 |
| mixed | accent | 99.63 [98.53, 100.00]B | 92.21 [76.03, 99.69]B | 82 / 1 / 4 |
| mixed | subscript | 71.43 [20.00, 100.00]B | 100.00 [56.55, 100.00]W | 5 / 2 / 0 |
| mixed | diaeresis | — (0 denominator) | — (0 denominator) | 0 / 0 / 0 |
| vouli | any | 98.82 [97.45, 99.74]B | 99.76 [99.12, 100.00]B | 121 / 5 / 1 |
| vouli | breathing | 97.15 [92.15, 99.48]B | 99.27 [97.00, 100.00]B | 43 / 4 / 1 |
| vouli | accent | 98.71 [96.83, 99.75]B | 99.35 [98.04, 100.00]B | 83 / 4 / 2 |
| vouli | subscript | 50.00 [0.00, 100.00]B | 100.00 [20.65, 100.00]W | 1 / 1 / 0 |
| vouli | diaeresis | — (0 denominator) | — (0 denominator) | 0 / 0 / 0 |

### Detector physical zones and emitted marks


| Wave | Measure | Weighted precision % [95%] | Weighted recall % [95%] | Raw TP / FP / FN |
|---|---|---|---|---|
| parliament | emitted_any | 84.03 [75.98, 90.09]B | 66.62 [55.03, 75.88]B | 241 / 165 / 435 |
| parliament | above | 82.88 [74.34, 89.50]B | 68.10 [56.70, 77.20]B | 259 / 183 / 415 |
| parliament | below | 11.11 [0.00, 50.00]B | 33.33 [0.00, 100.00]B | 1 / 8 / 2 |
| round1 | emitted_any | 98.09 [95.43, 99.68]B | 91.60 [85.87, 94.97]B | 83 / 7 / 33 |
| round1 | above | 98.37 [95.90, 99.78]B | 92.35 [86.78, 95.66]B | 85 / 6 / 30 |
| round1 | below | 0.00 [0.00, 56.15]W | 0.00 [0.00, 79.35]W | 0 / 3 / 1 |
| round2 | emitted_any | 97.77 [93.54, 99.67]B | 88.97 [78.20, 94.55]B | 83 / 7 / 38 |
| round2 | above | 97.52 [92.62, 99.68]B | 91.56 [81.86, 96.72]B | 91 / 8 / 29 |
| round2 | below | 50.00 [0.00, 100.00]B | 25.00 [0.00, 100.00]B | 1 / 1 / 3 |
| mixed | emitted_any | 97.29 [93.00, 99.70]B | 88.26 [81.06, 93.46]B | 78 / 9 / 43 |
| mixed | above | 97.90 [93.66, 100.00]B | 90.06 [83.03, 95.14]B | 81 / 7 / 36 |
| mixed | below | 0.00 [0.00, 65.76]W | 0.00 [0.00, 43.45]W | 0 / 2 / 5 |
| vouli | emitted_any | 87.56 [78.17, 93.66]B | 93.81 [88.85, 96.77]B | 96 / 56 / 26 |
| vouli | above | 87.12 [77.27, 93.69]B | 95.23 [91.09, 97.70]B | 101 / 59 / 20 |
| vouli | below | 0.00 [0.00, 56.15]W | 0.00 [0.00, 79.35]W | 0 / 3 / 1 |

### Exact-letter sensitivity

This sensitivity retains only cards whose complete detector and R1-A letter sequences match the print (casefolded). Main scores above retain gaps/substitutions.

| Wave | Cards retained | Detector any P / R | R1-A any P / R |
|---|---|---|---|
| parliament | 568 | 82.66 [74.00, 89.45]B / 68.21 [56.83, 77.23]B | 99.46 [99.05, 99.79]B / 99.85 [99.63, 100.00]B |
| round1 | 94 | 98.07 [95.35, 99.65]B / 92.95 [87.89, 96.02]B | 99.22 [97.97, 100.00]B / 100.00 [86.86, 100.00]W |
| round2 | 97 | 97.51 [92.57, 99.68]B / 92.07 [82.83, 96.79]B | 100.00 [86.46, 100.00]W / 100.00 [86.46, 100.00]W |
| mixed | 97 | 97.31 [93.07, 99.70]B / 89.54 [82.59, 94.60]B | 99.45 [98.14, 100.00]B / 100.00 [86.78, 100.00]W |
| vouli | 98 | 87.28 [77.35, 93.77]B / 95.22 [91.06, 97.70]B | 98.82 [97.44, 99.74]B / 99.76 [99.11, 100.00]B |

## Elision / alias-only cards

**33 tagged data cards in the frozen deck; only 13 were read in this cut.** The rest remain unadjudicated. Alias normalization does not forgive an omitted elision or a different printed raised dot. These are small selected subsets; do not read the wide intervals as an independent elision benchmark.

Deck tags are 32 elision-presence-only and one alias-only. Alias-only coverage: 0/1 read. R1-A elision comes from saved recogniser punctuation; its mark head does not predict elision.

| Wave | Tagged deck / cut / resolved | google | r1_A | detector_original | frozen_AB |
|---|---|---|---|---|---|
| parliament | 2 / 2 / 2 | 100.00 [34.24, 100.00]W; 2/2 | 100.00 [34.24, 100.00]W; 2/2 | 0.00 [0.00, 65.76]W; 0/2 | 0.00 [0.00, 65.76]W; 0/2 |
| round1 | 8 / 5 / 5 | 100.00 [56.55, 100.00]W; 5/5 | 100.00 [56.55, 100.00]W; 5/5 | 0.00 [0.00, 43.45]W; 0/5 | 0.00 [0.00, 43.45]W; 0/5 |
| round2 | 10 / 2 / 2 | 0.00 [0.00, 65.76]W; 0/2 | 0.00 [0.00, 65.76]W; 0/2 | 50.00 [0.00, 100.00]B; 1/2 | 50.00 [0.00, 100.00]B; 1/2 |
| mixed | 5 / 2 / 2 | 100.00 [34.24, 100.00]W; 2/2 | 100.00 [34.24, 100.00]W; 2/2 | 0.00 [0.00, 65.76]W; 0/2 | 0.00 [0.00, 65.76]W; 0/2 |
| vouli | 8 / 2 / 2 | 100.00 [34.24, 100.00]W; 2/2 | 100.00 [34.24, 100.00]W; 2/2 | 0.00 [0.00, 65.76]W; 0/2 | 0.00 [0.00, 65.76]W; 0/2 |

Ordinary-only word accuracy, with all tagged cards removed (same weights):

| Wave | google | r1_A | detector_original | frozen_AB |
|---|---|---|---|---|
| parliament | 96.07 [94.52, 97.28]B; 526/574 | 97.05 [95.69, 98.07]B; 538/574 | 57.30 [42.64, 69.12]B; 53/574 | 96.72 [95.10, 97.93]B; 534/574 |
| round1 | 95.97 [91.70, 98.22]B; 80/95 | 95.70 [91.63, 98.10]B; 79/95 | 81.19 [69.33, 87.98]B; 25/95 | 95.16 [90.90, 97.69]B; 77/95 |
| round2 | 95.71 [91.78, 97.85]B; 85/98 | 96.37 [93.06, 98.70]B; 87/98 | 74.92 [58.07, 83.90]B; 22/98 | 96.37 [93.06, 98.70]B; 87/98 |
| mixed | 90.10 [76.71, 97.28]B; 81/98 | 92.03 [78.56, 98.96]B; 88/98 | 73.80 [57.40, 85.32]B; 22/98 | 92.03 [78.56, 98.96]B; 88/98 |
| vouli | 96.21 [93.44, 98.10]B; 83/98 | 96.21 [93.47, 98.05]B; 83/98 | 81.57 [70.26, 88.60]B; 25/98 | 95.96 [93.03, 97.92]B; 82/98 |

## S8b targets from detector errors

Rank by inverse-probability weighted **letter-slot failure events** in each wave. Counts estimate wave word-population events, not distinct cards. Physical above/below errors and naming errors have separate classes; classes can overlap on a slot. These are observed failure types, not proven geometric causes: localisation, clipping, ownership and font mechanisms still require pixel review. Example links point to the frozen word crops; per-slot flags, boxes and source baseline hashes remain in the gzip.

### parliament

| Failure class | Weighted events | Raw events / cards | Example IDs |
|---|---|---|---|
| missing_above_presence | 415.00 | 415 / 362 | [item_0218a58b4757fe4b](S8_DEV/cards/img/item_0218a58b4757fe4b.png), [item_02aa8c1d9495023b](S8_DEV/cards/img/item_02aa8c1d9495023b.png), [item_0522356c3e72153a](S8_DEV/cards/img/item_0522356c3e72153a.png) |
| false_above_presence | 183.00 | 183 / 136 | [item_007b3c471388122a](S8_DEV/cards/img/item_007b3c471388122a.png), [item_02b1b85365c1e380](S8_DEV/cards/img/item_02b1b85365c1e380.png), [item_0522356c3e72153a](S8_DEV/cards/img/item_0522356c3e72153a.png) |
| extra_breathing_name_with_ink | 48.00 | 48 / 48 | [item_01bceee64bc0a06d](S8_DEV/cards/img/item_01bceee64bc0a06d.png), [item_07bde6859efb853a](S8_DEV/cards/img/item_07bde6859efb853a.png), [item_0bbb35e4de0dbd93](S8_DEV/cards/img/item_0bbb35e4de0dbd93.png) |


### round1

| Failure class | Weighted events | Raw events / cards | Example IDs |
|---|---|---|---|
| missing_above_presence | 62.10 | 30 / 30 | [item_029ab8654a3db431](S8_DEV/cards/img/item_029ab8654a3db431.png), [item_032f75f3c5f409f6](S8_DEV/cards/img/item_032f75f3c5f409f6.png), [item_0cf572d4b186957f](S8_DEV/cards/img/item_0cf572d4b186957f.png) |
| extra_breathing_name_with_ink | 37.26 | 18 / 18 | [item_0bce2838af287f3c](S8_DEV/cards/img/item_0bce2838af287f3c.png), [item_0d7db4797f4bde9d](S8_DEV/cards/img/item_0d7db4797f4bde9d.png), [item_1769d4c707e97752](S8_DEV/cards/img/item_1769d4c707e97752.png) |
| missing_accent_name_with_ink | 31.05 | 15 / 15 | [item_0bce2838af287f3c](S8_DEV/cards/img/item_0bce2838af287f3c.png), [item_0d7db4797f4bde9d](S8_DEV/cards/img/item_0d7db4797f4bde9d.png), [item_21263364fbaf53d9](S8_DEV/cards/img/item_21263364fbaf53d9.png) |


### round2

| Failure class | Weighted events | Raw events / cards | Example IDs |
|---|---|---|---|
| missing_above_presence | 69.02 | 29 / 27 | [item_0815d59d5686736c](S8_DEV/cards/img/item_0815d59d5686736c.png), [item_1066622eea430d52](S8_DEV/cards/img/item_1066622eea430d52.png), [item_2a3ed6b0fdce3d77](S8_DEV/cards/img/item_2a3ed6b0fdce3d77.png) |
| missing_breathing_name_with_ink | 38.08 | 16 / 16 | [item_030366e13c1bf568](S8_DEV/cards/img/item_030366e13c1bf568.png), [item_04991bc1f5430968](S8_DEV/cards/img/item_04991bc1f5430968.png), [item_069af98248640317](S8_DEV/cards/img/item_069af98248640317.png) |
| extra_breathing_name_with_ink | 35.70 | 15 / 15 | [item_0274bdb2e851cbcf](S8_DEV/cards/img/item_0274bdb2e851cbcf.png), [item_18e0d91549a05885](S8_DEV/cards/img/item_18e0d91549a05885.png), [item_1a8478d344ee4dc1](S8_DEV/cards/img/item_1a8478d344ee4dc1.png) |


### mixed

| Failure class | Weighted events | Raw events / cards | Example IDs |
|---|---|---|---|
| missing_above_presence | 92.52 | 36 / 32 | [item_00a27339e0bd0540](S8_DEV/cards/img/item_00a27339e0bd0540.png), [item_103ca4946de9fa2b](S8_DEV/cards/img/item_103ca4946de9fa2b.png), [item_116a20fb770bce4b](S8_DEV/cards/img/item_116a20fb770bce4b.png) |
| missing_accent_name_with_ink | 79.32 | 12 / 12 | [item_eb92e68ee47af29f](S8_DEV/cards/img/item_eb92e68ee47af29f.png), [item_237e2284d33fac68](S8_DEV/cards/img/item_237e2284d33fac68.png), [item_4115adc7becb55ba](S8_DEV/cards/img/item_4115adc7becb55ba.png) |
| extra_breathing_name_with_ink | 43.69 | 17 / 17 | [item_07366b46bfc4e0f9](S8_DEV/cards/img/item_07366b46bfc4e0f9.png), [item_237e2284d33fac68](S8_DEV/cards/img/item_237e2284d33fac68.png), [item_255b62b77313f6ee](S8_DEV/cards/img/item_255b62b77313f6ee.png) |


### vouli

| Failure class | Weighted events | Raw events / cards | Example IDs |
|---|---|---|---|
| false_above_presence | 217.71 | 59 / 30 | [item_026a1b8799e85fcd](S8_DEV/cards/img/item_026a1b8799e85fcd.png), [item_038416b0512bb291](S8_DEV/cards/img/item_038416b0512bb291.png), [item_15657af7c5a88032](S8_DEV/cards/img/item_15657af7c5a88032.png) |
| missing_above_presence | 73.80 | 20 / 18 | [item_08bc278864a9c9fb](S8_DEV/cards/img/item_08bc278864a9c9fb.png), [item_0ed144fbbecd64fd](S8_DEV/cards/img/item_0ed144fbbecd64fd.png), [item_121b24d719e27139](S8_DEV/cards/img/item_121b24d719e27139.png) |
| extra_breathing_name_with_ink | 44.28 | 12 / 12 | [item_01ba9e73c7bf77f9](S8_DEV/cards/img/item_01ba9e73c7bf77f9.png), [item_0a5d9cafb66b852e](S8_DEV/cards/img/item_0a5d9cafb66b852e.png), [item_4cea4e7ca1dc9529](S8_DEV/cards/img/item_4cea4e7ca1dc9529.png) |

The next bounded iteration should first test the ranked physical presence losses/additions on these examples, with naming held fixed; where naming classes rank highly, retain the physical/naming distinction in S8b qualification. No change is implemented or accepted by this analysis.

## Reproduction and limits

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/s8_score_truth.py`

Audit: replace the final script path with `scripts/labelfix/s8_validate_truth.py`. Independent reaggregation verifies all 80 source/family/wave presence cells and all 20 source/wave accuracy cells; hand-calculated witnesses cover weighted ratios, elision aliases, spacing breathing, keraia, shifted marks, insertion/deletion and unnamed physical ink.

The scorer checks full/cut file membership by ID, all 42 tiebreak identities, candidate decoding, control denominators, source-slot base identity, both frozen directories byte-for-byte before/after scoring and unchanged HEAD. All input file hashes are retained. No unadjudicated card is inferred correct from source agreement. UNKNOWN exclusions and cut sampling limit generalization; the existing masked DEV baseline remains pending.

S8 DEV TRUTH: adjudicated 978 data cards (parliament 578, others 4×100); controls r1 82/84 r2 82/84; detector presence P/R by wave parliament 82.62%/68.23%, round1 98.10%/92.11%, round2 97.53%/91.59%, mixed 97.32%/89.08%, vouli 86.96%/95.24%; R1-A parliament 99.39%/99.77%, round1 99.24%/99.24%, round2 100.00%/99.42%, mixed 99.19%/99.73%, vouli 98.82%/99.76%; Google word accuracy parliament 96.07%, round1 96.02%, round2 95.08%, mixed 90.15%, vouli 96.23%; S8b targets parliament: missing_above_presence, false_above_presence, extra_breathing_name_with_ink; round1: missing_above_presence, extra_breathing_name_with_ink, missing_accent_name_with_ink; round2: missing_above_presence, missing_breathing_name_with_ink, extra_breathing_name_with_ink; mixed: missing_above_presence, missing_accent_name_with_ink, extra_breathing_name_with_ink; vouli: false_above_presence, missing_above_presence, extra_breathing_name_with_ink.
