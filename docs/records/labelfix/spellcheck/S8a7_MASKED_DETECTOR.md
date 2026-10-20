# S8a7 — masked detector against frozen DEV truth

**441/450 non-parliament lines have matched masks; nine retain their originals (six unmatched, three ambiguous). Parliament remains unmasked.** The frozen S6 detector and SF4 gate use the saved recogniser alignment and R1 A/B/E predictions. No reader inference, network access, source changes or new adjudication.

**On the paired eligible adjudicated words, physical presence recall is exactly unchanged in every wave.** Precision changes are small: round1 +0.27 pp, vouli −0.20 pp, other waves unchanged. Across the full DEV, clipping flags fall sharply (top 3,307→1,383; bottom 3,124→1,764) and AB kept rises 56→114, while loc_unknown barely moves (876→875) and seg_uncertain increases (1,389→1,394). Clipping diagnostics and gate releases improve, without demonstrated recall recovery on the eligible cut. There are 44 delta candidate words: 35 in the frozen data deck, including ten resolved words excluded from paired scoring, plus nine outside that deck.

Analysis HEAD `a639110499d24471bf61026e7475494ff87f144d`. [Receipt](S8_DEV/masked/receipt.json), [summary](S8_DEV/masked/summary.json), [per-line original→masked comparison](S8_DEV/masked/baseline_per_line.jsonl), [per-word scores](S8_DEV/masked/scores_per_word.jsonl.gz), [delta candidates](S8_DEV/masked/delta_cards.jsonl).

## Inputs and preservation

Saved runtime SHA256 `fae3140ea1e789ca817d3eec3ec71ae5d47774cf43503b9fa0b25aa54d64e4a2`; frozen truth SHA256 `bbfba1509215d60517ab651324a44323f6a5cedd8378c97fdcadab48bc78a3ec`. The runtime matches the S8a3/S8a4 request-bound receipt, with 600 complete runtimes and alignments and zero inference. Mask receipt and lines hashes, all 450 original/masked crop hashes, all ownership-map hashes, dimensions, 0–5 class values and changed-pixel counts are verified. The handoff guard records 0/450 over 30% wrong-line-risk threshold (maximum 26.58%); it was evaluated after the sourcing run and would change no line. Ownership maps are detector attribution, not semantic truth. Masking changed pixels on 374 lines; 67 matched masks were pixel-identical.

All 67 pixel-identical matched masks reproduce the original detector, metrics, composed modes and gate decisions exactly. The saved original baseline binding and all bound sources are checked against frozen commit `c6064650fa5451cbc3bd13197d7a31c0d3bbf33d`. A Python audit hook prohibits writes outside `S8_DEV/masked/` and this report, and prohibits sockets. Every pre-existing DEV artifact, including all three protected card directories, truth, and the S8a6 report, is hashed before/after. No `.git` writes.

The workspace advanced externally from task-start HEAD `78883b629fe1c48e5fe48b5be55f3a815a6f53dc` to the analysis HEAD; the only intervening change adds `docs/records/briefs/S8b_detector_iteration.md`. All S8a7 input and runtime content is unchanged.

## Baseline on the complete line population

These are unweighted recogniser-indexed letter counts across all 600 lines. Effective masked means the 441 matched-mask outputs plus the nine unchanged fallbacks and 150 unchanged parliament originals. Loc/seg/clip flags are detector diagnostics; truth presence below is a separate measurement.

| Wave | Lines / matched / changed | Letters | loc_unknown original→masked | seg_uncertain original→masked |
|---|---|---|---|---|
| parliament | 150 / 0 / 0 | 6497 | 600/6497 → 600/6497 (9.24→9.24%) | 843/6497 → 843/6497 (12.98→12.98%) |
| round1 | 100 / 100 / 81 | 4233 | 66/4233 → 65/4233 (1.56→1.54%) | 110/4233 → 109/4233 (2.60→2.58%) |
| round2 | 100 / 98 / 78 | 4210 | 58/4210 → 57/4210 (1.38→1.35%) | 118/4210 → 119/4210 (2.80→2.83%) |
| mixed | 100 / 97 / 74 | 4161 | 64/4161 → 67/4161 (1.54→1.61%) | 128/4161 → 133/4161 (3.08→3.20%) |
| vouli | 150 / 146 / 141 | 6493 | 88/6493 → 86/6493 (1.36→1.32%) | 190/6493 → 190/6493 (2.93→2.93%) |


| Population | Lines / letters | loc_unknown | seg_uncertain | Clipped top / bottom |
|---|---|---|---|---|
| all DEV | 600 / 25594 | 876/25594 → 875/25594 (3.42→3.42%) | 1389/25594 → 1394/25594 (5.43→5.45%) | 3307→1383 / 3124→1764 |
| non-parliament | 450 / 19097 | 276/19097 → 275/19097 (1.45→1.44%) | 546/19097 → 551/19097 (2.86→2.89%) | 2434→510 / 2173→813 |
| matched masks only | 441 / 18628 | 240/18628 → 239/18628 (1.29→1.28%) | 498/18628 → 503/18628 (2.67→2.70%) | 2384→460 / 2135→775 |


| Wave | Clipped top | Clipped bottom | Unnamed letters | Unnamed blobs | Components/letter |
|---|---|---|---|---|---|
| parliament | 873/6497 → 873/6497 (13.44→13.44%) | 951/6497 → 951/6497 (14.64→14.64%) | 65/6497 → 65/6497 (1.00→1.00%) | 78→78 | 0.9527→0.9527 |
| round1 | 533/4233 → 79/4233 (12.59→1.87%) | 428/4233 → 144/4233 (10.11→3.40%) | 19/4233 → 18/4233 (0.45→0.43%) | 26→25 | 1.0482→1.0484 |
| round2 | 514/4210 → 78/4210 (12.21→1.85%) | 402/4210 → 108/4210 (9.55→2.57%) | 26/4210 → 26/4210 (0.62→0.62%) | 31→30 | 1.0226→1.0230 |
| mixed | 497/4161 → 91/4161 (11.94→2.19%) | 435/4161 → 193/4161 (10.45→4.64%) | 16/4161 → 15/4161 (0.38→0.36%) | 20→17 | 1.0363→1.0358 |
| vouli | 890/6493 → 262/6493 (13.71→4.04%) | 908/6493 → 368/6493 (13.98→5.67%) | 89/6493 → 88/6493 (1.37→1.36%) | 132→123 | 1.0334→1.0340 |


| Wave | ENSEMBLE_AB original→masked | PRESENCE original→masked |
|---|---|---|
| parliament | 1 kept (1 corrected / 0 unchanged), 149 hold → 1 kept (1 corrected / 0 unchanged), 149 hold | 1 kept (1 corrected / 0 unchanged), 149 hold → 1 kept (1 corrected / 0 unchanged), 149 hold |
| round1 | 15 kept (4 corrected / 11 unchanged), 85 hold → 32 kept (8 corrected / 24 unchanged), 68 hold | 7 kept (1 corrected / 6 unchanged), 93 hold → 17 kept (3 corrected / 14 unchanged), 83 hold |
| round2 | 21 kept (2 corrected / 19 unchanged), 79 hold → 35 kept (6 corrected / 29 unchanged), 65 hold | 11 kept (1 corrected / 10 unchanged), 89 hold → 19 kept (3 corrected / 16 unchanged), 81 hold |
| mixed | 15 kept (4 corrected / 11 unchanged), 85 hold → 24 kept (5 corrected / 19 unchanged), 76 hold | 5 kept (1 corrected / 4 unchanged), 95 hold → 9 kept (1 corrected / 8 unchanged), 91 hold |
| vouli | 4 kept (0 corrected / 4 unchanged), 146 hold → 22 kept (3 corrected / 19 unchanged), 128 hold | 2 kept (0 corrected / 2 unchanged), 148 hold → 12 kept (1 corrected / 11 unchanged), 138 hold |

Full status transition matrices, per-line proposals/holds/labels, component histograms and affected-line counts are in the machine-readable outputs.

## Frozen truth, eligibility and delta candidates

S8a6 read 978 data cards; 976 resolved and two parliament UNKNOWN. Other deck words remain unread. Weights are copied exactly: `1/(saved card inclusion probability × wave cut probability)`, including the exact all-agree sampling fraction. No UNKNOWN or unread word is scored. Masked forms are compared with the original per-word deck options after S8a6 canonicalization (including elision aliases, preposed breathing and keraia). **Every new masked candidate is excluded from both sides of the paired score.** Original full-cut scores are shown separately so exclusions cannot masquerade as improvement. For unselected all-agree census words, the saved consensus is the sole implicit candidate. `delta_cards.jsonl` lists all new candidate word groups, with separate counts for existing deck, resolved cut, unread deck and words absent from the original deck; no cards are rendered.

| Wave | Resolved | Delta all census / existing deck / resolved excluded / unread deck / no deck | Paired scored / matched-mask scored / fallback scored | Retained Σw / resolved Σw |
|---|---|---|---|---|
| parliament | 576 | 0 / 0 / 0 / 0 / 0 | 576 / 0 / 0 | 1222.00 / 1222.00 |
| round1 | 100 | 6 / 5 / 3 / 2 / 1 | 97 / 97 / 0 | 774.30 / 780.51 |
| round2 | 100 | 5 / 2 / 0 / 2 / 3 | 100 / 96 / 4 | 725.90 / 725.90 |
| mixed | 100 | 7 / 5 / 1 / 4 / 2 | 99 / 89 / 10 | 933.09 / 935.66 |
| vouli | 100 | 26 / 23 / 6 / 17 / 3 | 94 / 89 / 5 | 1446.80 / 1468.94 |

Delta exclusion makes the paired result conditional on existing-candidate coverage. It does not estimate performance on all masked words. Weights are retained without redistribution. Physical evidence can change even when the named word form remains an existing candidate.

## Presence precision and recall

Primary **any** is physical saved detector `above OR below`, including unnamed ink. Breathing/accent/subscript/diaeresis are emitted family presence, so family results include naming behavior. `emitted_any` and physical `above`/`below` are also retained. S8a6 mark-blind casefolded base alignment, punctuation anchors, deterministic ties, union slots and gap FP/FN rules are reused unchanged. All loc/seg/clip cases remain eligible when truth is resolved and the form is not a delta.

Cells are weighted % [95% interval], B = document-cluster percentile bootstrap (4,000 replicates, seed 20261017 + wave index); W = Wilson–Kish fallback for degenerate bootstrap, as in S8a6. Line-cluster intervals and valid-replicate counts are retained. Paired changes use the same resampled documents on both variants; intervals condition on the fixed eligible cohort and exclude reader uncertainty.

| Wave | Original full-cut any P / R | Paired original any P / R | Paired masked any P / R | Paired ΔP / ΔR pp [95%] |
|---|---|---|---|---|
| parliament | 82.62 [74.00, 89.30]B / 68.23 [56.85, 77.26]B | 82.62 [74.00, 89.30]B / 68.23 [56.85, 77.26]B | 82.62 [74.00, 89.30]B / 68.23 [56.85, 77.26]B | +0.00 [+0.00, +0.00] / +0.00 [+0.00, +0.00] |
| round1 | 98.10 [95.46, 99.68]B / 92.11 [86.60, 95.36]B | 98.63 [96.85, 99.72]B / 92.29 [86.92, 95.45]B | 98.90 [97.31, 99.77]B / 92.29 [86.92, 95.45]B | +0.27 [+0.00, +1.02] / +0.00 [+0.00, +0.00] |
| round2 | 97.53 [92.65, 99.68]B / 91.59 [82.09, 96.61]B | 97.53 [92.65, 99.68]B / 91.59 [82.09, 96.61]B | 97.53 [92.65, 99.68]B / 91.59 [82.09, 96.61]B | +0.00 [+0.00, +0.00] / +0.00 [+0.00, +0.00] |
| mixed | 97.32 [93.10, 99.71]B / 89.08 [81.91, 94.19]B | 97.31 [93.07, 99.71]B / 89.29 [82.13, 94.46]B | 97.31 [93.07, 99.71]B / 89.29 [82.13, 94.46]B | +0.00 [+0.00, +0.00] / +0.00 [+0.00, +0.00] |
| vouli | 86.96 [77.00, 93.47]B / 95.24 [91.09, 97.70]B | 88.89 [79.41, 94.90]B / 95.15 [90.86, 97.66]B | 88.69 [78.91, 94.85]B / 95.15 [90.86, 97.66]B | -0.20 [-0.67, +0.00] / +0.00 [+0.00, +0.00] |


| Wave | Family/zone | Original P / R [95%] | Masked P / R [95%] | Raw TP/FP/FN original→masked |
|---|---|---|---|---|
| parliament | breathing | 58.17 [38.55, 74.44]B / 51.86 [35.49, 64.75]B | 58.17 [38.55, 74.44]B / 51.86 [35.49, 64.75]B | 58/110/142 → 58/110/142 |
| parliament | accent | 82.76 [73.88, 89.07]B / 67.29 [54.44, 77.26]B | 82.76 [73.88, 89.07]B / 67.29 [54.44, 77.26]B | 169/150/350 → 169/150/350 |
| parliament | subscript | 11.11 [0.00, 50.00]B / 33.33 [0.00, 100.00]B | 11.11 [0.00, 50.00]B / 33.33 [0.00, 100.00]B | 1/8/2 → 1/8/2 |
| parliament | diaeresis | — (0 denominator) / 0.00 [0.00, 79.35]W | — (0 denominator) / 0.00 [0.00, 79.35]W | 0/0/1 → 0/0/1 |
| parliament | emitted_any | 84.03 [75.98, 90.09]B / 66.62 [55.03, 75.88]B | 84.03 [75.98, 90.09]B / 66.62 [55.03, 75.88]B | 241/165/435 → 241/165/435 |
| parliament | above | 82.88 [74.34, 89.50]B / 68.10 [56.70, 77.20]B | 82.88 [74.34, 89.50]B / 68.10 [56.70, 77.20]B | 259/183/415 → 259/183/415 |
| parliament | below | 11.11 [0.00, 50.00]B / 33.33 [0.00, 100.00]B | 11.11 [0.00, 50.00]B / 33.33 [0.00, 100.00]B | 1/8/2 → 1/8/2 |
| round1 | breathing | 73.06 [40.90, 86.73]B / 74.98 [44.00, 86.90]B | 74.98 [42.86, 87.99]B / 74.98 [44.00, 86.90]B | 20/21/19 → 20/19/19 |
| round1 | accent | 96.82 [93.74, 98.64]B / 88.91 [80.96, 93.37]B | 97.14 [94.36, 98.87]B / 89.20 [81.45, 93.60]B | 46/10/38 → 47/9/37 |
| round1 | subscript | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0/3/1 → 0/3/1 |
| round1 | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| round1 | emitted_any | 98.62 [96.84, 99.71]B / 91.78 [86.21, 95.10]B | 98.89 [97.29, 99.77]B / 91.78 [86.21, 95.10]B | 80/5/32 → 80/4/32 |
| round1 | above | 98.90 [97.35, 99.78]B / 92.53 [87.08, 95.77]B | 99.17 [97.80, 100.00]B / 92.53 [87.08, 95.77]B | 82/4/29 → 82/3/29 |
| round1 | below | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0/3/1 → 0/3/1 |
| round2 | breathing | 81.23 [46.94, 92.32]B / 77.21 [44.19, 88.99]B | 82.09 [48.78, 93.11]B / 77.21 [44.19, 88.99]B | 22/18/23 → 22/17/23 |
| round2 | accent | 91.77 [81.82, 96.61]B / 84.45 [70.53, 91.78]B | 91.80 [81.96, 96.61]B / 84.84 [71.35, 92.12]B | 44/19/39 → 45/19/38 |
| round2 | subscript | 50.00 [0.00, 100.00]B / 25.00 [0.00, 100.00]B | 50.00 [0.00, 100.00]B / 25.00 [0.00, 100.00]B | 1/1/3 → 1/1/3 |
| round2 | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| round2 | emitted_any | 97.77 [93.54, 99.67]B / 88.97 [78.20, 94.55]B | 97.77 [93.54, 99.67]B / 88.97 [78.20, 94.55]B | 83/7/38 → 83/7/38 |
| round2 | above | 97.52 [92.62, 99.68]B / 91.56 [81.86, 96.72]B | 97.52 [92.62, 99.68]B / 91.56 [81.86, 96.72]B | 91/8/29 → 91/8/29 |
| round2 | below | 50.00 [0.00, 100.00]B / 25.00 [0.00, 100.00]B | 50.00 [0.00, 100.00]B / 25.00 [0.00, 100.00]B | 1/1/3 → 1/1/3 |
| mixed | breathing | 80.53 [45.47, 93.30]B / 77.36 [40.74, 89.03]B | 82.22 [45.82, 94.77]B / 77.36 [40.74, 89.03]B | 22/19/23 → 22/17/23 |
| mixed | accent | 93.64 [86.58, 97.44]B / 80.56 [63.23, 91.52]B | 93.67 [86.63, 97.44]B / 80.90 [63.50, 91.60]B | 47/16/38 → 48/16/37 |
| mixed | subscript | 0.00 [0.00, 65.76]W / 0.00 [0.00, 43.45]W | 0.00 [0.00, 65.76]W / 0.00 [0.00, 43.45]W | 0/2/5 → 0/2/5 |
| mixed | diaeresis | 0.00 [0.00, 79.35]W / — (0 denominator) | 0.00 [0.00, 79.35]W / — (0 denominator) | 0/1/0 → 0/1/0 |
| mixed | emitted_any | 97.28 [92.98, 99.70]B / 88.47 [81.21, 93.69]B | 97.28 [92.98, 99.70]B / 88.47 [81.21, 93.69]B | 77/9/42 → 77/9/42 |
| mixed | above | 97.89 [93.64, 100.00]B / 90.28 [83.21, 95.49]B | 97.89 [93.64, 100.00]B / 90.28 [83.21, 95.49]B | 80/7/35 → 80/7/35 |
| mixed | below | 0.00 [0.00, 65.76]W / 0.00 [0.00, 43.45]W | 0.00 [0.00, 65.76]W / 0.00 [0.00, 43.45]W | 0/2/5 → 0/2/5 |
| vouli | breathing | 81.27 [58.36, 92.30]B / 87.98 [69.97, 95.10]B | 82.41 [59.90, 93.32]B / 87.98 [69.97, 95.10]B | 24/27/16 → 24/25/16 |
| vouli | accent | 87.71 [77.90, 93.58]B / 94.07 [88.28, 97.31]B | 87.98 [78.21, 93.84]B / 94.07 [88.28, 97.31]B | 62/40/18 → 62/39/18 |
| vouli | subscript | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0/3/1 → 0/3/1 |
| vouli | diaeresis | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | 0/0/0 → 0/0/0 |
| vouli | emitted_any | 89.56 [80.78, 95.07]B / 93.69 [88.54, 96.73]B | 89.56 [80.78, 95.07]B / 93.69 [88.54, 96.73]B | 88/45/26 → 88/45/26 |
| vouli | above | 89.07 [79.67, 95.10]B / 95.13 [90.85, 97.66]B | 88.87 [79.24, 95.06]B / 95.13 [90.85, 97.66]B | 93/48/20 → 93/49/20 |
| vouli | below | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0.00 [0.00, 56.15]W / 0.00 [0.00, 79.35]W | 0/3/1 → 0/3/1 |

## Separate matched masks and nine original fallbacks

This sensitivity removes all nine fallbacks from the masking estimate. Parliament has no matched-mask score.

| Wave | Matched-mask eligible cards | Original any P / R | Masked any P / R | Δ recall pp [95%] |
|---|---|---|---|---|
| parliament | 0 | — (0 denominator) / — (0 denominator) | — (0 denominator) / — (0 denominator) | — |
| round1 | 97 | 98.63 [96.85, 99.72]B / 92.29 [86.92, 95.45]B | 98.90 [97.31, 99.77]B / 92.29 [86.92, 95.45]B | +0.00 [+0.00, +0.00] |
| round2 | 96 | 97.53 [92.65, 99.68]B / 92.93 [85.42, 96.82]B | 97.53 [92.65, 99.68]B / 92.93 [85.42, 96.82]B | +0.00 [+0.00, +0.00] |
| mixed | 89 | 98.77 [96.77, 100.00]B / 91.20 [85.49, 95.29]B | 98.77 [96.77, 100.00]B / 91.20 [85.49, 95.29]B | +0.00 [+0.00, +0.00] |
| vouli | 89 | 87.81 [76.97, 94.35]B / 95.66 [91.89, 97.81]B | 87.59 [76.70, 94.30]B / 95.66 [91.89, 97.81]B | +0.00 [+0.00, +0.00] |


| Line ID | Wave | Reason | Resolved cards | loc / seg / clipped top / bottom | AB / PRESENCE status |
|---|---|---|---|---|---|
| 593b45a064a4-p000007-l0051 | vouli | unmatched | 0 | 2 / 6 / 11 / 16 | hold / hold |
| 91252504a906-p000009-l0093 | vouli | unmatched | 1 | 0 / 0 / 9 / 3 | hold / hold |
| 17cbdf94881f-p000002-l0027 | vouli | ambiguous | 3 | 15 / 17 / 0 / 0 | hold / hold |
| 593b45a064a4-p000003-l0034 | vouli | unmatched | 1 | 0 / 0 / 23 / 16 | hold / hold |
| 6d957fa757c72e1408f65dde-p000088-l0027 | round2 | ambiguous | 4 | 11 / 13 / 0 / 1 | hold / hold |
| 395473997d50a60416fa3684-p000022-l0004 | round2 | unmatched | 0 | 0 / 0 / 0 / 0 | unchanged / unchanged |
| a38045f531c81af524934fb8-p000034-l0010 | mixed | unmatched | 4 | 2 / 2 / 2 / 2 | hold / hold |
| c8654864d161aa7fc41f65cb-p000672-l0053 | mixed | unmatched | 0 | 0 / 0 / 4 / 0 | hold / hold |
| b8b6779da9a68fbed0ccdb5b-p000024-l0057 | mixed | ambiguous | 6 | 6 / 10 / 1 / 0 | hold / hold |


| Fallback wave | Lines / letters | loc / seg / top / bottom | Eligible cards | Unchanged any P / R [95%] |
|---|---|---|---|---|
| round1 | 0 / 0 | 0 / 0 / 0 / 0 | 0 | — (0 denominator) / — (0 denominator) |
| round2 | 2 / 59 | 11 / 13 / 0 / 1 | 4 | — (0 denominator) / 0.00 [0.00, 43.45]W |
| mixed | 3 / 133 | 8 / 12 / 7 / 2 | 10 | 44.44 [37.50, 100.00]B / 33.33 [20.00, 42.86]B |
| vouli | 4 / 277 | 17 / 23 / 43 / 35 | 5 | 100.00 [34.24, 100.00]W / 90.75 [0.00, 100.00]B |

All nine fallback crops are byte-identical to originals: baseline, detector, gate decisions and eligible presence counts are therefore unchanged. Fallback subgroup weights are inherited S8a6 weights; its small-sample intervals are descriptive.

## Per-wave verdict

- **parliament:** Unmasked reference only: no masking experiment or masking effect is established. loc_unknown 600→600; seg_uncertain 843→843; clipping top/bottom 873/951→873/951; AB kept 1→1; 0 resolved words excluded for new candidates (0 total delta words).
- **round1:** Eligible any recall 92.29%→92.29%, Δ +0.00 [+0.00, +0.00] pp: no physical recall gain on this cohort. loc_unknown 66→65; seg_uncertain 110→109; clipping top/bottom 533/428→79/144; AB kept 15→32; 3 resolved words excluded for new candidates (6 total delta words).
- **round2:** Eligible any recall 91.59%→91.59%, Δ +0.00 [+0.00, +0.00] pp: no physical recall gain on this cohort. loc_unknown 58→57; seg_uncertain 118→119; clipping top/bottom 514/402→78/108; AB kept 21→35; 0 resolved words excluded for new candidates (5 total delta words).
- **mixed:** Eligible any recall 89.29%→89.29%, Δ +0.00 [+0.00, +0.00] pp: no physical recall gain on this cohort. loc_unknown 64→67; seg_uncertain 128→133; clipping top/bottom 497/435→91/193; AB kept 15→24; 1 resolved words excluded for new candidates (7 total delta words).
- **vouli:** Eligible any recall 95.15%→95.15%, Δ +0.00 [+0.00, +0.00] pp: no physical recall gain on this cohort. loc_unknown 88→86; seg_uncertain 190→190; clipping top/bottom 890/908→262/368; AB kept 4→22; 6 resolved words excluded for new candidates (26 total delta words).

These DEV comparisons do not establish held-out generalization or causal geometric recovery. New masked candidates require a later, separately authorized adjudication.

## Reproduction and validation

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B docs/records/labelfix/spellcheck/S8_DEV/masked/run_s8a7.py`

The equivalent runner imports the frozen detector/gate and the original S8a6 scoring functions; it never invokes the card builders. Cached masked records are hash-bound. Original per-word physical scores are reproduced exactly for every resolved word; full-cut P/R and confidence outputs are checked against S8a6. Validation also independently reaggregates all score cells from per-slot boolean presence, checks denominator equality, delta exclusion, fallback identity and protected file hashes.

Validation command: replace `run_s8a7.py` above with `validate_s8a7.py`. The final [validation receipt](S8_DEV/masked/validation.json) records 240 source/family/cohort/wave cells and 23 independently rebuilt paired document intervals; the unchanged S8a6 validator also passes.

S8a7 RESULT: masked 441/450; detector presence P/R original→masked by wave parliament 82.62%/68.23%→82.62%/68.23%; round1 98.63%/92.29%→98.90%/92.29%; round2 97.53%/91.59%→97.53%/91.59%; mixed 97.31%/89.29%→97.31%/89.29%; vouli 88.89%/95.15%→88.69%/95.15%; loc_unknown 876/25594→875/25594; seg_uncertain 1389/25594→1394/25594; clipping top 3307→1383, bottom 3124→1764; AB kept 56→114; delta cards 44
