# S2 — mark detector and PRINT truth

Iteration `fb87c8f4dirty`. CPU; network off; **0 CTC forward passes**. 1,264 seed-0 lines, frozen 666 held-out lines from 14 non-DEV books. Classifier choices and second-pass detector adjustments used DEV only. Old model, input labels, truth, alignment caches and S1 artifacts preserved.

The recogniser only locates input characters. Google = human = recogniser cores establish agreement truth; the 189 adjudications override those words; null/other disagreements are UNKNOWN. No owner `printed_field` is used. Unmatched/competing letter-component ownership is UNKNOWN. The two seeds reuse the same images; pooled engine confidence bounds describe observations, not independent images. S1 baseline classifier originally used these held-out books for calibration, so before/after is a frozen-book comparison, not a newly untouched baseline.

## Whole-line metrics

Each letter component sorted by x is a slot. Exact accent/breathing identities are compared; fused breathing+accent is one compound kind, subscript separate, apostrophe separate. A physical blob classified none is retained as an unclassified false mark. The class prediction is diagnostic argmax (no confidence filtering); engine decisions use tau. UNKNOWN slots are counted and excluded.

| set | iteration | known slots | unknown slots | TP | FP | FN | precision | recall | F1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| held-out | before | 18229 | 2647 | 3406 | 2899 | 647 | 54.0% | 84.0% | 65.8% |
| held-out | after | 18229 | 2647 | 3375 | 294 | 678 | 92.0% | 83.3% | 87.4% |
| owner 33 | before | 720 | 117 | 141 | 149 | 37 | 48.6% | 79.2% | 60.3% |
| owner 33 | after | 720 | 117 | 122 | 17 | 56 | 87.8% | 68.5% | 77.0% |

| mark kind | before P | after P | before R | after R |
|---|---:|---:|---:|---:|
| accent | 48.6% | 93.5% | 93.0% | 90.6% |
| breathing | 74.2% | 94.0% | 86.4% | 82.0% |
| compound | 69.6% | 75.8% | 69.6% | 66.2% |
| subscript | 42.2% | 100.0% | 89.4% | 41.5% |
| dialytika | — | — | 0.0% | 0.0% |
| apostrophe | — | 99.2% | 0.0% | 60.7% |

## Failure-class strata

Operational, overlapping strata below describe observable exposure, not a claim that every error has a proven physical cause. Full per-slot evidence and per-line P/R/F1: `S2_lines.jsonl.gz`.

| failure class / slot exposure | slots | before P/R | after P/R |
|---|---:|---|---|
| (a) ascender/capital | 4736 | 0.6%/5.2% | 50.0%/39.0% |
| (b) old below blob, no printed subscript | 184 | 3.9%/40.0% | 31.2%/33.3% |
| (c) printed apostrophe | 206 | 3.2%/1.9% | 100.0%/61.4% |
| (c2) descender with old below blob | 81 | 0.0%/— | 0.0%/— |
| (d) faint candidate | 219 | 9.4%/51.5% | 22.4%/51.5% |
| (e) printed compound | 450 | 71.1%/69.8% | 74.3%/66.1% |

## Agreement-set false marks by unmarked letter

Rate = slots with any above blob / agreement slots with no printed marks. This table includes all books for reporting; held-out did not set thresholds.

| letter | slots | before | after | before rate | after rate |
|---|---:|---:|---:|---:|---:|
| a | 1 | 0 | 0 | 0.0% | 0.0% |
| capitals | 1119 | 215 | 29 | 19.2% | 2.6% |
| d | 1 | 1 | 0 | 100.0% | 0.0% |
| e | 4 | 2 | 1 | 50.0% | 25.0% |
| g | 1 | 0 | 0 | 0.0% | 0.0% |
| i | 4 | 4 | 0 | 100.0% | 0.0% |
| l | 3 | 3 | 0 | 100.0% | 0.0% |
| n | 2 | 0 | 0 | 0.0% | 0.0% |
| o | 2 | 0 | 0 | 0.0% | 0.0% |
| p | 1 | 0 | 0 | 0.0% | 0.0% |
| r | 1 | 0 | 0 | 0.0% | 0.0% |
| s | 1 | 0 | 0 | 0.0% | 0.0% |
| t | 2 | 2 | 0 | 100.0% | 0.0% |
| u | 1 | 0 | 0 | 0.0% | 0.0% |
| v | 1 | 0 | 0 | 0.0% | 0.0% |
| α | 1673 | 243 | 17 | 14.5% | 1.0% |
| β | 179 | 178 | 9 | 99.4% | 5.0% |
| γ | 355 | 45 | 3 | 12.7% | 0.8% |
| δ | 498 | 483 | 32 | 97.0% | 6.4% |
| ε | 1455 | 179 | 14 | 12.3% | 1.0% |
| ζ | 89 | 88 | 11 | 98.9% | 12.4% |
| η | 459 | 63 | 8 | 13.7% | 1.7% |
| θ | 405 | 404 | 3 | 99.8% | 0.7% |
| ι | 1299 | 102 | 1 | 7.9% | 0.1% |
| κ | 859 | 47 | 6 | 5.5% | 0.7% |
| λ | 792 | 782 | 36 | 98.7% | 4.5% |
| μ | 809 | 41 | 5 | 5.1% | 0.6% |
| ν | 2300 | 143 | 16 | 6.2% | 0.7% |
| ξ | 107 | 96 | 2 | 89.7% | 1.9% |
| ο | 1731 | 218 | 10 | 12.6% | 0.6% |
| π | 850 | 64 | 5 | 7.5% | 0.6% |
| ρ | 1086 | 107 | 11 | 9.9% | 1.0% |
| ς | 996 | 79 | 9 | 7.9% | 0.9% |
| σ | 863 | 54 | 9 | 6.3% | 1.0% |
| τ | 1621 | 116 | 13 | 7.2% | 0.8% |
| υ | 532 | 68 | 2 | 12.8% | 0.4% |
| φ | 272 | 172 | 0 | 63.2% | 0.0% |
| χ | 262 | 26 | 2 | 9.9% | 0.8% |
| ψ | 48 | 48 | 2 | 100.0% | 4.2% |
| ω | 305 | 44 | 3 | 14.4% | 1.0% |

## Classifier

DEV books only; fixed MLP 140 epochs; 20% DEV lines calibrate tau; held-out never selects model/threshold. tau=0.997. 13327 new agreement samples; old file 13312; matched 13312, changed feature vectors 2096, changed blob composition 1990 on the new sample population, labels changed 0. Sample IDs include word index and cluster for future exact matching; old samples lack these IDs so old/new matching uses occurrence order within (line, word, base, class).

Training collection inspected: 0 DEV-book lines, 0 cached. No extra training samples admitted: no eligible cached training alignments/recorded recogniser agreement. Single-vowel Google-only labels would not meet the agreement requirement. Twelve compound classes are represented in the model schema, but several have **zero independent fitting examples**. This requirement remains incomplete; absent classes cannot be claimed learned.

| class | fit | DEV calibration | held-out | held-out recall | precision at tau | prediction coverage |
|---|---:|---:|---:|---:|---:|---:|
| acute | 462 | 128 | 1277 | 90.4% | 99.9% | 11.9% |
| circumflex | 213 | 44 | 279 | 90.0% | 91.7% | 2.2% |
| circumflex+subscript | 17 | 5 | 36 | 22.2% | — | 0.0% |
| dasia | 109 | 13 | 194 | 74.7% | 100.0% | 0.9% |
| dasia+acute | 32 | 2 | 93 | 88.2% | 100.0% | 0.3% |
| dasia+acute+subscript | 0 | 0 | 0 | — | — | 0.0% |
| dasia+circumflex | 0 | 0 | 5 | 0.0% | — | 0.0% |
| dasia+circumflex+subscript | 0 | 0 | 1 | 0.0% | — | 0.0% |
| dasia+grave | 0 | 0 | 5 | 0.0% | — | 0.0% |
| dasia+grave+subscript | 0 | 0 | 0 | — | — | 0.0% |
| dialytika | 1 | 1 | 1 | 0.0% | — | 0.0% |
| grave | 311 | 103 | 587 | 86.0% | 99.8% | 4.9% |
| none | 2089 | 534 | 5396 | 99.7% | — | 0.0% |
| psili | 251 | 65 | 633 | 83.6% | 99.6% | 5.3% |
| psili+acute | 55 | 10 | 259 | 70.3% | 100.0% | 1.4% |
| psili+acute+subscript | 0 | 0 | 0 | — | — | 0.0% |
| psili+circumflex | 8 | 3 | 26 | 50.0% | — | 0.0% |
| psili+circumflex+subscript | 0 | 0 | 0 | — | — | 0.0% |
| psili+grave | 9 | 1 | 10 | 50.0% | — | 0.0% |
| psili+grave+subscript | 0 | 0 | 0 | — | — | 0.0% |
| subscript | 16 | 1 | 41 | 58.5% | — | 0.0% |

## Owner expectations

Literal notes are retained below and in `owner_slot_expectations.jsonl`. `missed` counts are minimum missing units; compounds carry two units. Fixed also requires all known printed marks at that slot. Qualitative blurry notes stay unresolved. The three marks across slots 1/2 are checked as a group. No-note card has no invented expectation. A note/truth conflict is reported without adjudicating it; alignment/slot mismatch is also a possible cause.

| line | slot | expectation | before → after | truth conflict | owner note |
|---|---:|---|---|---|---|
| 02a3a2a6-p000046-l0014 | 8 | {"missed": 1} | fixed → not fixed | True | accent of 8 missed |
| 02a3a2a6-p000046-l0025 | 18 | {"false": "punctuation_dot"} | not fixed → fixed | None | dot of exclamation mark is detected |
| 177b717d-p000013-l0009 | 1 | {"missed": 2} | fixed → not fixed | False | missed 2 at 1, one at 13 |
| 177b717d-p000013-l0009 | 13 | {"missed": 1} | fixed → not fixed | True | missed 2 at 1, one at 13 |
| 177b717d-p000097-l0007 | 19 | {"false": "subscript_speck"} | not fixed → fixed | False | random mark under 19 |
| 177b717d-p000097-l0010 | 2 | {"missed": 2} | not fixed → not fixed | False | missed two at 2, one at 5 |
| 177b717d-p000097-l0010 | 5 | {"missed": 1} | fixed → not fixed | False | missed two at 2, one at 5 |
| 2793d64c-p000048-l0004 | 19 | {"missed": 1} | not fixed → not fixed | False | iota is missed |
| 2793d64c-p000048-l0010 | 6 | {"false": "subscript_speck"} | not fixed → fixed | False | random dot under 6 |
| 2793d64c-p000070-l0010 | 22 | {"false": "ascender_delta"} | not fixed → not fixed | False | 22 delta is detected |
| 2793d64c-p000070-l0014 | 10 | {"false": "subscript_speck"} | fixed → fixed | False | random marks under 10 and 13, and over 12 |
| 2793d64c-p000070-l0014 | 13 | {"false": "subscript_speck"} | not fixed → fixed | False | random marks under 10 and 13, and over 12 |
| 2793d64c-p000070-l0014 | 12 | {"false": "above_speck"} | not fixed → not fixed | False | random marks under 10 and 13, and over 12 |
| 2793d64c-p000072-l0007 | 3 | {"apostrophe": true} | not fixed → fixed | False | careful on the ellipsis at 3 |
| 384c3f89-p000030-l0021 | 22 | {"apostrophe": true} | not fixed → fixed | False | ellipsis at 22 missed |
| 384c3f89-p000030-l0029 | 1 | {"missed": 1} | fixed → not fixed | None | missed 1's accent |
| 384c3f89-p000053-l0021 | 10 | {"missed": 2} | fixed → fixed | False | 2 accents missed at 10, and 1 at 32, also ellipsis of 22 |
| 384c3f89-p000053-l0021 | 32 | {"missed": 1} | fixed → fixed | False | 2 accents missed at 10, and 1 at 32, also ellipsis of 22 |
| 384c3f89-p000053-l0021 | 22 | {"apostrophe": true} | not fixed → fixed | False | 2 accents missed at 10, and 1 at 32, also ellipsis of 22 |
| 384c3f89-p000053-l0028 | 25 | {"missed": 1} | fixed → fixed | False | accents of 25 missed |
| 384c3f89-p000068-l0036 | 6 | {"apostrophe": true} | not fixed → not fixed | False | ellispis after 6 missed, 2 accents of 7 missed |
| 384c3f89-p000068-l0036 | 7 | {"missed": 2} | not fixed → not fixed | False | ellispis after 6 missed, 2 accents of 7 missed |
| 384c3f89-p000091-l0039 | — | no expectation | — | — |  |
| 384c3f89-p000121-l0024 | 18 | {"apostrophe": true} | not fixed → fixed | False | ellipsis missed at 18 |
| 384c3f89-p000205-l0005 | 1 | {"missed": 2} | not fixed → not fixed | False | 2 accent of 1 missed, 1 ellipsis at 2 and 7 respectively |
| 384c3f89-p000205-l0005 | 2 | {"apostrophe": true} | not fixed → not fixed | False | 2 accent of 1 missed, 1 ellipsis at 2 and 7 respectively |
| 384c3f89-p000205-l0005 | 7 | {"apostrophe": true} | not fixed → fixed | False | 2 accent of 1 missed, 1 ellipsis at 2 and 7 respectively |
| 51fe7386-p000024-l0015 | 1 | {"missed": 1} | not fixed → not fixed | False | 3 accents of 1 and 2 missed, 2 of 29 missed |
| 51fe7386-p000024-l0015 | 2 | {"missed": 1} | not fixed → not fixed | False | 3 accents of 1 and 2 missed, 2 of 29 missed |
| 51fe7386-p000024-l0015 | 29 | {"missed": 2} | not fixed → not fixed | False | 3 accents of 1 and 2 missed, 2 of 29 missed |
| 51fe7386-p000024-l0020 | 6 | {"missed": 1} | fixed → not fixed | False | missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript |
| 51fe7386-p000024-l0020 | 8 | {"missed": 1} | fixed → not fixed | False | missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript |
| 51fe7386-p000024-l0020 | 11 | {"missed": 1} | fixed → not fixed | False | missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript |
| 51fe7386-p000024-l0020 | 20 | {"missed": 1} | fixed → not fixed | False | missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript |
| 51fe7386-p000024-l0020 | 37 | {"missed": 1} | fixed → not fixed | False | missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript |
| 51fe7386-p000024-l0020 | 39 | {"missed": 1} | not fixed → not fixed | False | missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript |
| 51fe7386-p000024-l0020 | 23 | {"false": "letter_part_subscript"} | not fixed → fixed | False | missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript |
| 602cc72e-p000155-l0009 | 2 | {"missed": 2} | not fixed → not fixed | False | missed two at 2, and one at 11, 12, and 16 |
| 602cc72e-p000155-l0009 | 11 | {"missed": 1} | not fixed → not fixed | False | missed two at 2, and one at 11, 12, and 16 |
| 602cc72e-p000155-l0009 | 12 | {"missed": 1} | not fixed → not fixed | False | missed two at 2, and one at 11, 12, and 16 |
| 602cc72e-p000155-l0009 | 16 | {"missed": 1} | not fixed → not fixed | False | missed two at 2, and one at 11, 12, and 16 |
| 602cc72e-p000167-l0027 | 1 | {"missed": 1} | not fixed → not fixed | False | missed 1 at 1, 6, 10, and 14 |
| 602cc72e-p000167-l0027 | 6 | {"missed": 1} | not fixed → not fixed | False | missed 1 at 1, 6, 10, and 14 |
| 602cc72e-p000167-l0027 | 10 | {"missed": 1} | not fixed → not fixed | False | missed 1 at 1, 6, 10, and 14 |
| 602cc72e-p000167-l0027 | 14 | {"missed": 1} | not fixed → not fixed | False | missed 1 at 1, 6, 10, and 14 |
| 8b6b0de9-p000004-l0028 | 2 | {"missed": 1} | fixed → not fixed | False | missed accent at 2 ,and 2 at 7 |
| 8b6b0de9-p000004-l0028 | 7 | {"missed": 2} | fixed → not fixed | False | missed accent at 2 ,and 2 at 7 |
| 8b6b0de9-p000007-l0030 | 13 | {"false": "subscript_speck"} | not fixed → fixed | False | random mark under lambda |
| 8b6b0de9-p000008-l0001 | 12 | {"missed": 2} | fixed → not fixed | False | 2 accents over 12 missed, delta 13 detected |
| 8b6b0de9-p000008-l0001 | 13 | {"false": "ascender_delta"} | not fixed → not fixed | False | 2 accents over 12 missed, delta 13 detected |
| 8b6b0de9-p000008-l0002 | 13 | {"false": "punctuation_dot"} | not fixed → fixed | None | dot of exclamation mark is detected |
| 8b6b0de9-p000008-l0019 | 17 | {"missed": 1} | fixed → not fixed | False | missed accent at 17 |
| 8b6b0de9-p000008-l0024 | 4 | {"missed": 1} | fixed → not fixed | False | missed at 4 and 18 |
| 8b6b0de9-p000008-l0024 | 18 | {"missed": 1} | fixed → not fixed | False | missed at 4 and 18 |
| 8b6b0de9-p000011-l0007 | 9 | {"false": "subscript_speck"} | not fixed → fixed | False | random dot under 9 |
| 8b6b0de9-p000011-l0014 | 13 | {"missed": 1} | not fixed → not fixed | False | missed 13 |
| 8b6b0de9-p000021-l0007 | 18 | {"false": "faint_letter"} | not fixed → fixed | False | faint eta at 18 is detected as accent |
| 9c1dca9b-p000005-l0017 | 23 | {"missed": 1} | not fixed → not fixed | False | very blurry and merged accents at 23 and 27 |
| 9c1dca9b-p000005-l0017 | 27 | {"missed": 1} | not fixed → not fixed | False | very blurry and merged accents at 23 and 27 |
| 9c1dca9b-p000015-l0065 | 8 | {"missed": 1} | fixed → not fixed | False | missed 8 |

Owner per-line exact metrics (including all visible slots):

| line | before P/R/F1 | after P/R/F1 | known/unknown slots |
|---|---|---|---|
| 02a3a2a6-p000046-l0014 | 71.4%/100.0%/83.3% | 100.0%/100.0%/100.0% | 16/3 |
| 02a3a2a6-p000046-l0025 | 75.0%/100.0%/85.7% | 100.0%/100.0%/100.0% | 7/13 |
| 177b717d-p000013-l0009 | 66.7%/80.0%/72.7% | 75.0%/60.0%/66.7% | 21/3 |
| 177b717d-p000097-l0007 | 60.0%/100.0%/75.0% | 100.0%/100.0%/100.0% | 16/6 |
| 177b717d-p000097-l0010 | 60.0%/75.0%/66.7% | 100.0%/50.0%/66.7% | 14/12 |
| 2793d64c-p000048-l0004 | 66.7%/85.7%/75.0% | 100.0%/71.4%/83.3% | 18/1 |
| 2793d64c-p000048-l0010 | 63.6%/100.0%/77.8% | 100.0%/85.7%/92.3% | 24/0 |
| 2793d64c-p000070-l0010 | 60.0%/100.0%/75.0% | 66.7%/66.7%/66.7% | 23/2 |
| 2793d64c-p000070-l0014 | 41.7%/100.0%/58.8% | 83.3%/100.0%/90.9% | 20/0 |
| 2793d64c-p000072-l0007 | 37.5%/75.0%/50.0% | 66.7%/100.0%/80.0% | 17/7 |
| 384c3f89-p000030-l0021 | 46.7%/77.8%/58.3% | 88.9%/88.9%/88.9% | 38/6 |
| 384c3f89-p000030-l0029 | 45.5%/83.3%/58.8% | 100.0%/100.0%/100.0% | 31/3 |
| 384c3f89-p000053-l0021 | 50.0%/77.8%/60.9% | 88.9%/88.9%/88.9% | 38/0 |
| 384c3f89-p000053-l0028 | 50.0%/75.0%/60.0% | 87.5%/87.5%/87.5% | 31/4 |
| 384c3f89-p000068-l0036 | 50.0%/66.7%/57.1% | 100.0%/66.7%/80.0% | 29/2 |
| 384c3f89-p000091-l0039 | 50.0%/85.7%/63.2% | 85.7%/85.7%/85.7% | 31/1 |
| 384c3f89-p000121-l0024 | 72.7%/88.9%/80.0% | 100.0%/100.0%/100.0% | 35/2 |
| 384c3f89-p000205-l0005 | 58.3%/63.6%/60.9% | 100.0%/63.6%/77.8% | 34/2 |
| 51fe7386-p000024-l0015 | 23.1%/42.9%/30.0% | 40.0%/28.6%/33.3% | 24/8 |
| 51fe7386-p000024-l0020 | 36.8%/87.5%/51.9% | 50.0%/12.5%/20.0% | 37/5 |
| 602cc72e-p000155-l0009 | 0.0%/0.0%/0.0% | —/0.0%/0.0% | 17/0 |
| 602cc72e-p000167-l0027 | 0.0%/0.0%/0.0% | —/0.0%/0.0% | 17/0 |
| 8b6b0de9-p000004-l0028 | 50.0%/100.0%/66.7% | 100.0%/33.3%/50.0% | 15/2 |
| 8b6b0de9-p000007-l0030 | 33.3%/100.0%/50.0% | 100.0%/100.0%/100.0% | 20/2 |
| 8b6b0de9-p000008-l0001 | 75.0%/100.0%/85.7% | 80.0%/66.7%/72.7% | 17/5 |
| 8b6b0de9-p000008-l0002 | 100.0%/100.0%/100.0% | 66.7%/66.7%/66.7% | 4/9 |
| 8b6b0de9-p000008-l0019 | 20.0%/50.0%/28.6% | 0.0%/0.0%/0.0% | 16/1 |
| 8b6b0de9-p000008-l0024 | 33.3%/100.0%/50.0% | 100.0%/33.3%/50.0% | 16/2 |
| 8b6b0de9-p000011-l0007 | 85.7%/100.0%/92.3% | 100.0%/66.7%/80.0% | 17/2 |
| 8b6b0de9-p000011-l0014 | 25.0%/50.0%/33.3% | 100.0%/50.0%/66.7% | 14/2 |
| 8b6b0de9-p000021-l0007 | 50.0%/100.0%/66.7% | 100.0%/100.0%/100.0% | 19/0 |
| 9c1dca9b-p000005-l0017 | 9.1%/25.0%/13.3% | —/0.0%/0.0% | 26/10 |
| 9c1dca9b-p000015-l0065 | 60.0%/100.0%/75.0% | 100.0%/66.7%/80.0% | 18/2 |

## S1 engine rescoring

S1 policy/proposal code is retained except the compound-compatible count check, new extractor and new classifier. ACCEPT and HOLD remain separate. Both seeds re-run by `spellcheck_validate`; raw rows and receipt in `S2_engine/`. Original S1 rows are scored both ways without rewriting them. Unknown print words remain excluded. HOLD contradicts print whenever its proposal differs from known print; this includes Google-right and both-wrong.

| iteration | seed | policy | split | stage | column | reference | decided | correct | wrong | unknown | precision | LB95 |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| S1 | 0 | strict | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | dev | D1 | HOLD | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 0 | strict | dev | D1 | HOLD | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 0 | strict | dev | D2 | ACCEPT | human | 24 | 23 | 1 | 0 | 95.8% | 81.7% |
| S1 | 0 | strict | dev | D2 | ACCEPT | print | 24 | 24 | 0 | 0 | 100.0% | 88.3% |
| S1 | 0 | strict | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | dev | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | strict | dev | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | strict | dev | L1 | HOLD | human | 13 | 7 | 4 | 2 | 63.6% | 35.0% |
| S1 | 0 | strict | dev | L1 | HOLD | print | 13 | 7 | 3 | 3 | 70.0% | 39.3% |
| S1 | 0 | strict | dev | L2 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 0 | strict | dev | L2 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 0 | strict | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | dev | all | ACCEPT | human | 27 | 26 | 1 | 0 | 96.3% | 83.6% |
| S1 | 0 | strict | dev | all | ACCEPT | print | 27 | 27 | 0 | 0 | 100.0% | 89.5% |
| S1 | 0 | strict | dev | all | HOLD | human | 14 | 8 | 4 | 2 | 66.7% | 39.1% |
| S1 | 0 | strict | dev | all | HOLD | print | 14 | 8 | 3 | 3 | 72.7% | 43.6% |
| S1 | 0 | strict | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | held-out | D1 | HOLD | human | 8 | 5 | 2 | 1 | 71.4% | 34.1% |
| S1 | 0 | strict | held-out | D1 | HOLD | print | 8 | 5 | 2 | 1 | 71.4% | 34.1% |
| S1 | 0 | strict | held-out | D2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | strict | held-out | D2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | strict | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | held-out | L1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | held-out | L1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | held-out | L1 | HOLD | human | 24 | 20 | 4 | 0 | 83.3% | 65.8% |
| S1 | 0 | strict | held-out | L1 | HOLD | print | 24 | 17 | 5 | 2 | 77.3% | 58.0% |
| S1 | 0 | strict | held-out | L2 | ACCEPT | human | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 0 | strict | held-out | L2 | ACCEPT | print | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 0 | strict | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | held-out | all | ACCEPT | human | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S1 | 0 | strict | held-out | all | ACCEPT | print | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S1 | 0 | strict | held-out | all | HOLD | human | 32 | 25 | 6 | 1 | 80.6% | 65.3% |
| S1 | 0 | strict | held-out | all | HOLD | print | 32 | 22 | 7 | 3 | 75.9% | 59.4% |
| S1 | 0 | strict | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | all | D1 | HOLD | human | 9 | 6 | 2 | 1 | 75.0% | 40.0% |
| S1 | 0 | strict | all | D1 | HOLD | print | 9 | 6 | 2 | 1 | 75.0% | 40.0% |
| S1 | 0 | strict | all | D2 | ACCEPT | human | 26 | 25 | 1 | 0 | 96.2% | 83.0% |
| S1 | 0 | strict | all | D2 | ACCEPT | print | 26 | 26 | 0 | 0 | 100.0% | 89.1% |
| S1 | 0 | strict | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | all | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | strict | all | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | strict | all | L1 | HOLD | human | 37 | 27 | 8 | 2 | 77.1% | 62.5% |
| S1 | 0 | strict | all | L1 | HOLD | print | 37 | 24 | 8 | 5 | 75.0% | 59.4% |
| S1 | 0 | strict | all | L2 | ACCEPT | human | 2 | 1 | 1 | 0 | 50.0% | 2.5% |
| S1 | 0 | strict | all | L2 | ACCEPT | print | 2 | 1 | 1 | 0 | 50.0% | 2.5% |
| S1 | 0 | strict | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | strict | all | all | ACCEPT | human | 30 | 28 | 2 | 0 | 93.3% | 80.5% |
| S1 | 0 | strict | all | all | ACCEPT | print | 30 | 29 | 1 | 0 | 96.7% | 85.1% |
| S1 | 0 | strict | all | all | HOLD | human | 46 | 33 | 10 | 3 | 76.7% | 63.8% |
| S1 | 0 | strict | all | all | HOLD | print | 46 | 30 | 10 | 6 | 75.0% | 61.3% |
| S1 | 0 | ratio | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | dev | D1 | HOLD | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 0 | ratio | dev | D1 | HOLD | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 0 | ratio | dev | D2 | ACCEPT | human | 24 | 23 | 1 | 0 | 95.8% | 81.7% |
| S1 | 0 | ratio | dev | D2 | ACCEPT | print | 24 | 24 | 0 | 0 | 100.0% | 88.3% |
| S1 | 0 | ratio | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | dev | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | ratio | dev | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | ratio | dev | L1 | HOLD | human | 20 | 7 | 11 | 2 | 38.9% | 19.9% |
| S1 | 0 | ratio | dev | L1 | HOLD | print | 20 | 7 | 9 | 4 | 43.8% | 22.7% |
| S1 | 0 | ratio | dev | L2 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | dev | L2 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | dev | all | ACCEPT | human | 26 | 25 | 1 | 0 | 96.2% | 83.0% |
| S1 | 0 | ratio | dev | all | ACCEPT | print | 26 | 26 | 0 | 0 | 100.0% | 89.1% |
| S1 | 0 | ratio | dev | all | HOLD | human | 21 | 8 | 11 | 2 | 42.1% | 23.0% |
| S1 | 0 | ratio | dev | all | HOLD | print | 21 | 8 | 9 | 4 | 47.1% | 26.0% |
| S1 | 0 | ratio | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | held-out | D1 | HOLD | human | 8 | 5 | 2 | 1 | 71.4% | 34.1% |
| S1 | 0 | ratio | held-out | D1 | HOLD | print | 8 | 5 | 2 | 1 | 71.4% | 34.1% |
| S1 | 0 | ratio | held-out | D2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | ratio | held-out | D2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | ratio | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | held-out | L1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | held-out | L1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | held-out | L1 | HOLD | human | 32 | 21 | 11 | 0 | 65.6% | 49.6% |
| S1 | 0 | ratio | held-out | L1 | HOLD | print | 32 | 18 | 12 | 2 | 60.0% | 43.4% |
| S1 | 0 | ratio | held-out | L2 | ACCEPT | human | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 0 | ratio | held-out | L2 | ACCEPT | print | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 0 | ratio | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | held-out | all | ACCEPT | human | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S1 | 0 | ratio | held-out | all | ACCEPT | print | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S1 | 0 | ratio | held-out | all | HOLD | human | 40 | 26 | 13 | 1 | 66.7% | 52.3% |
| S1 | 0 | ratio | held-out | all | HOLD | print | 40 | 23 | 14 | 3 | 62.2% | 47.3% |
| S1 | 0 | ratio | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | all | D1 | HOLD | human | 9 | 6 | 2 | 1 | 75.0% | 40.0% |
| S1 | 0 | ratio | all | D1 | HOLD | print | 9 | 6 | 2 | 1 | 75.0% | 40.0% |
| S1 | 0 | ratio | all | D2 | ACCEPT | human | 26 | 25 | 1 | 0 | 96.2% | 83.0% |
| S1 | 0 | ratio | all | D2 | ACCEPT | print | 26 | 26 | 0 | 0 | 100.0% | 89.1% |
| S1 | 0 | ratio | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | all | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | ratio | all | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 0 | ratio | all | L1 | HOLD | human | 52 | 28 | 22 | 2 | 56.0% | 43.4% |
| S1 | 0 | ratio | all | L1 | HOLD | print | 52 | 25 | 21 | 6 | 54.3% | 41.3% |
| S1 | 0 | ratio | all | L2 | ACCEPT | human | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 0 | ratio | all | L2 | ACCEPT | print | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 0 | ratio | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 0 | ratio | all | all | ACCEPT | human | 29 | 27 | 2 | 0 | 93.1% | 79.8% |
| S1 | 0 | ratio | all | all | ACCEPT | print | 29 | 28 | 1 | 0 | 96.6% | 84.7% |
| S1 | 0 | ratio | all | all | HOLD | human | 61 | 34 | 24 | 3 | 58.6% | 47.0% |
| S1 | 0 | ratio | all | all | HOLD | print | 61 | 31 | 23 | 7 | 57.4% | 45.3% |
| S1 | 1 | strict | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | dev | D1 | HOLD | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 1 | strict | dev | D1 | HOLD | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 1 | strict | dev | D2 | ACCEPT | human | 25 | 23 | 2 | 0 | 92.0% | 76.9% |
| S1 | 1 | strict | dev | D2 | ACCEPT | print | 25 | 24 | 1 | 0 | 96.0% | 82.4% |
| S1 | 1 | strict | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | dev | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | strict | dev | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | strict | dev | L1 | HOLD | human | 10 | 7 | 2 | 1 | 77.8% | 45.0% |
| S1 | 1 | strict | dev | L1 | HOLD | print | 10 | 7 | 1 | 2 | 87.5% | 52.9% |
| S1 | 1 | strict | dev | L2 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 1 | strict | dev | L2 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 1 | strict | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | dev | all | ACCEPT | human | 28 | 26 | 2 | 0 | 92.9% | 79.2% |
| S1 | 1 | strict | dev | all | ACCEPT | print | 28 | 27 | 1 | 0 | 96.4% | 84.1% |
| S1 | 1 | strict | dev | all | HOLD | human | 11 | 8 | 2 | 1 | 80.0% | 49.3% |
| S1 | 1 | strict | dev | all | HOLD | print | 11 | 8 | 1 | 2 | 88.9% | 57.1% |
| S1 | 1 | strict | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | held-out | D1 | HOLD | human | 7 | 5 | 1 | 1 | 83.3% | 41.8% |
| S1 | 1 | strict | held-out | D1 | HOLD | print | 7 | 5 | 1 | 1 | 83.3% | 41.8% |
| S1 | 1 | strict | held-out | D2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | strict | held-out | D2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | strict | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | held-out | L1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | held-out | L1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | held-out | L1 | HOLD | human | 23 | 19 | 4 | 0 | 82.6% | 64.5% |
| S1 | 1 | strict | held-out | L1 | HOLD | print | 23 | 16 | 5 | 2 | 76.2% | 56.3% |
| S1 | 1 | strict | held-out | L2 | ACCEPT | human | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 1 | strict | held-out | L2 | ACCEPT | print | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 1 | strict | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | held-out | all | ACCEPT | human | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S1 | 1 | strict | held-out | all | ACCEPT | print | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S1 | 1 | strict | held-out | all | HOLD | human | 30 | 24 | 5 | 1 | 82.8% | 67.1% |
| S1 | 1 | strict | held-out | all | HOLD | print | 30 | 21 | 6 | 3 | 77.8% | 60.8% |
| S1 | 1 | strict | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | all | D1 | HOLD | human | 8 | 6 | 1 | 1 | 85.7% | 47.9% |
| S1 | 1 | strict | all | D1 | HOLD | print | 8 | 6 | 1 | 1 | 85.7% | 47.9% |
| S1 | 1 | strict | all | D2 | ACCEPT | human | 27 | 25 | 2 | 0 | 92.6% | 78.5% |
| S1 | 1 | strict | all | D2 | ACCEPT | print | 27 | 26 | 1 | 0 | 96.3% | 83.6% |
| S1 | 1 | strict | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | all | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | strict | all | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | strict | all | L1 | HOLD | human | 33 | 26 | 6 | 1 | 81.2% | 66.3% |
| S1 | 1 | strict | all | L1 | HOLD | print | 33 | 23 | 6 | 4 | 79.3% | 63.2% |
| S1 | 1 | strict | all | L2 | ACCEPT | human | 2 | 1 | 1 | 0 | 50.0% | 2.5% |
| S1 | 1 | strict | all | L2 | ACCEPT | print | 2 | 1 | 1 | 0 | 50.0% | 2.5% |
| S1 | 1 | strict | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | strict | all | all | ACCEPT | human | 31 | 28 | 3 | 0 | 90.3% | 76.8% |
| S1 | 1 | strict | all | all | ACCEPT | print | 31 | 29 | 2 | 0 | 93.5% | 81.1% |
| S1 | 1 | strict | all | all | HOLD | human | 41 | 32 | 7 | 2 | 82.1% | 68.9% |
| S1 | 1 | strict | all | all | HOLD | print | 41 | 29 | 7 | 5 | 80.6% | 66.6% |
| S1 | 1 | ratio | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | dev | D1 | HOLD | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 1 | ratio | dev | D1 | HOLD | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S1 | 1 | ratio | dev | D2 | ACCEPT | human | 25 | 23 | 2 | 0 | 92.0% | 76.9% |
| S1 | 1 | ratio | dev | D2 | ACCEPT | print | 25 | 24 | 1 | 0 | 96.0% | 82.4% |
| S1 | 1 | ratio | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | dev | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | ratio | dev | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | ratio | dev | L1 | HOLD | human | 16 | 7 | 8 | 1 | 46.7% | 24.4% |
| S1 | 1 | ratio | dev | L1 | HOLD | print | 16 | 7 | 5 | 4 | 58.3% | 31.5% |
| S1 | 1 | ratio | dev | L2 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | dev | L2 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | dev | all | ACCEPT | human | 27 | 25 | 2 | 0 | 92.6% | 78.5% |
| S1 | 1 | ratio | dev | all | ACCEPT | print | 27 | 26 | 1 | 0 | 96.3% | 83.6% |
| S1 | 1 | ratio | dev | all | HOLD | human | 17 | 8 | 8 | 1 | 50.0% | 27.9% |
| S1 | 1 | ratio | dev | all | HOLD | print | 17 | 8 | 5 | 4 | 61.5% | 35.5% |
| S1 | 1 | ratio | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | held-out | D1 | HOLD | human | 7 | 5 | 1 | 1 | 83.3% | 41.8% |
| S1 | 1 | ratio | held-out | D1 | HOLD | print | 7 | 5 | 1 | 1 | 83.3% | 41.8% |
| S1 | 1 | ratio | held-out | D2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | ratio | held-out | D2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | ratio | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | held-out | L1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | held-out | L1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | held-out | L1 | HOLD | human | 31 | 20 | 11 | 0 | 64.5% | 48.2% |
| S1 | 1 | ratio | held-out | L1 | HOLD | print | 31 | 17 | 12 | 2 | 58.6% | 41.7% |
| S1 | 1 | ratio | held-out | L2 | ACCEPT | human | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 1 | ratio | held-out | L2 | ACCEPT | print | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 1 | ratio | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | held-out | all | ACCEPT | human | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S1 | 1 | ratio | held-out | all | ACCEPT | print | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S1 | 1 | ratio | held-out | all | HOLD | human | 38 | 25 | 12 | 1 | 67.6% | 52.8% |
| S1 | 1 | ratio | held-out | all | HOLD | print | 38 | 22 | 13 | 3 | 62.9% | 47.6% |
| S1 | 1 | ratio | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | all | D1 | HOLD | human | 8 | 6 | 1 | 1 | 85.7% | 47.9% |
| S1 | 1 | ratio | all | D1 | HOLD | print | 8 | 6 | 1 | 1 | 85.7% | 47.9% |
| S1 | 1 | ratio | all | D2 | ACCEPT | human | 27 | 25 | 2 | 0 | 92.6% | 78.5% |
| S1 | 1 | ratio | all | D2 | ACCEPT | print | 27 | 26 | 1 | 0 | 96.3% | 83.6% |
| S1 | 1 | ratio | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | all | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | ratio | all | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | 1 | ratio | all | L1 | HOLD | human | 47 | 27 | 19 | 1 | 58.7% | 45.5% |
| S1 | 1 | ratio | all | L1 | HOLD | print | 47 | 24 | 17 | 6 | 58.5% | 44.5% |
| S1 | 1 | ratio | all | L2 | ACCEPT | human | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 1 | ratio | all | L2 | ACCEPT | print | 1 | 0 | 1 | 0 | 0.0% | 0.0% |
| S1 | 1 | ratio | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | 1 | ratio | all | all | ACCEPT | human | 30 | 27 | 3 | 0 | 90.0% | 76.1% |
| S1 | 1 | ratio | all | all | ACCEPT | print | 30 | 28 | 2 | 0 | 93.3% | 80.5% |
| S1 | 1 | ratio | all | all | HOLD | human | 55 | 33 | 20 | 2 | 62.3% | 50.1% |
| S1 | 1 | ratio | all | all | HOLD | print | 55 | 30 | 18 | 7 | 62.5% | 49.6% |
| S1 | both | strict | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | dev | D1 | HOLD | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | both | strict | dev | D1 | HOLD | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | both | strict | dev | D2 | ACCEPT | human | 49 | 46 | 3 | 0 | 93.9% | 84.9% |
| S1 | both | strict | dev | D2 | ACCEPT | print | 49 | 48 | 1 | 0 | 98.0% | 90.7% |
| S1 | both | strict | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | dev | L1 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | strict | dev | L1 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | strict | dev | L1 | HOLD | human | 23 | 14 | 6 | 3 | 70.0% | 49.2% |
| S1 | both | strict | dev | L1 | HOLD | print | 23 | 14 | 4 | 5 | 77.8% | 56.1% |
| S1 | both | strict | dev | L2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | both | strict | dev | L2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | both | strict | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | dev | all | ACCEPT | human | 55 | 52 | 3 | 0 | 94.5% | 86.5% |
| S1 | both | strict | dev | all | ACCEPT | print | 55 | 54 | 1 | 0 | 98.2% | 91.7% |
| S1 | both | strict | dev | all | HOLD | human | 25 | 16 | 6 | 3 | 72.7% | 53.2% |
| S1 | both | strict | dev | all | HOLD | print | 25 | 16 | 4 | 5 | 80.0% | 59.9% |
| S1 | both | strict | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | held-out | D1 | HOLD | human | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S1 | both | strict | held-out | D1 | HOLD | print | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S1 | both | strict | held-out | D2 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | strict | held-out | D2 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | strict | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | held-out | L1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | held-out | L1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | held-out | L1 | HOLD | human | 47 | 39 | 8 | 0 | 83.0% | 71.4% |
| S1 | both | strict | held-out | L1 | HOLD | print | 47 | 33 | 10 | 4 | 76.7% | 63.8% |
| S1 | both | strict | held-out | L2 | ACCEPT | human | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 | both | strict | held-out | L2 | ACCEPT | print | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 | both | strict | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | held-out | all | ACCEPT | human | 6 | 4 | 2 | 0 | 66.7% | 27.1% |
| S1 | both | strict | held-out | all | ACCEPT | print | 6 | 4 | 2 | 0 | 66.7% | 27.1% |
| S1 | both | strict | held-out | all | HOLD | human | 62 | 49 | 11 | 2 | 81.7% | 71.5% |
| S1 | both | strict | held-out | all | HOLD | print | 62 | 43 | 13 | 6 | 76.8% | 65.6% |
| S1 | both | strict | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | all | D1 | HOLD | human | 17 | 12 | 3 | 2 | 80.0% | 56.0% |
| S1 | both | strict | all | D1 | HOLD | print | 17 | 12 | 3 | 2 | 80.0% | 56.0% |
| S1 | both | strict | all | D2 | ACCEPT | human | 53 | 50 | 3 | 0 | 94.3% | 86.0% |
| S1 | both | strict | all | D2 | ACCEPT | print | 53 | 52 | 1 | 0 | 98.1% | 91.4% |
| S1 | both | strict | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | all | L1 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | strict | all | L1 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | strict | all | L1 | HOLD | human | 70 | 53 | 14 | 3 | 79.1% | 69.3% |
| S1 | both | strict | all | L1 | HOLD | print | 70 | 47 | 14 | 9 | 77.0% | 66.5% |
| S1 | both | strict | all | L2 | ACCEPT | human | 4 | 2 | 2 | 0 | 50.0% | 9.8% |
| S1 | both | strict | all | L2 | ACCEPT | print | 4 | 2 | 2 | 0 | 50.0% | 9.8% |
| S1 | both | strict | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | strict | all | all | ACCEPT | human | 61 | 56 | 5 | 0 | 91.8% | 83.5% |
| S1 | both | strict | all | all | ACCEPT | print | 61 | 58 | 3 | 0 | 95.1% | 87.8% |
| S1 | both | strict | all | all | HOLD | human | 87 | 65 | 17 | 5 | 79.3% | 70.5% |
| S1 | both | strict | all | all | HOLD | print | 87 | 59 | 17 | 11 | 77.6% | 68.4% |
| S1 | both | ratio | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | dev | D1 | HOLD | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | both | ratio | dev | D1 | HOLD | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 | both | ratio | dev | D2 | ACCEPT | human | 49 | 46 | 3 | 0 | 93.9% | 84.9% |
| S1 | both | ratio | dev | D2 | ACCEPT | print | 49 | 48 | 1 | 0 | 98.0% | 90.7% |
| S1 | both | ratio | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | dev | L1 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | ratio | dev | L1 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | ratio | dev | L1 | HOLD | human | 36 | 14 | 19 | 3 | 42.4% | 27.8% |
| S1 | both | ratio | dev | L1 | HOLD | print | 36 | 14 | 14 | 8 | 50.0% | 33.3% |
| S1 | both | ratio | dev | L2 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | dev | L2 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | dev | all | ACCEPT | human | 53 | 50 | 3 | 0 | 94.3% | 86.0% |
| S1 | both | ratio | dev | all | ACCEPT | print | 53 | 52 | 1 | 0 | 98.1% | 91.4% |
| S1 | both | ratio | dev | all | HOLD | human | 38 | 16 | 19 | 3 | 45.7% | 31.2% |
| S1 | both | ratio | dev | all | HOLD | print | 38 | 16 | 14 | 8 | 53.3% | 37.0% |
| S1 | both | ratio | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | held-out | D1 | HOLD | human | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S1 | both | ratio | held-out | D1 | HOLD | print | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S1 | both | ratio | held-out | D2 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | ratio | held-out | D2 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | ratio | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | held-out | L1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | held-out | L1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | held-out | L1 | HOLD | human | 63 | 41 | 22 | 0 | 65.1% | 54.0% |
| S1 | both | ratio | held-out | L1 | HOLD | print | 63 | 35 | 24 | 4 | 59.3% | 47.8% |
| S1 | both | ratio | held-out | L2 | ACCEPT | human | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 | both | ratio | held-out | L2 | ACCEPT | print | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 | both | ratio | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | held-out | all | ACCEPT | human | 6 | 4 | 2 | 0 | 66.7% | 27.1% |
| S1 | both | ratio | held-out | all | ACCEPT | print | 6 | 4 | 2 | 0 | 66.7% | 27.1% |
| S1 | both | ratio | held-out | all | HOLD | human | 78 | 51 | 25 | 2 | 67.1% | 57.2% |
| S1 | both | ratio | held-out | all | HOLD | print | 78 | 45 | 27 | 6 | 62.5% | 52.2% |
| S1 | both | ratio | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | all | D1 | HOLD | human | 17 | 12 | 3 | 2 | 80.0% | 56.0% |
| S1 | both | ratio | all | D1 | HOLD | print | 17 | 12 | 3 | 2 | 80.0% | 56.0% |
| S1 | both | ratio | all | D2 | ACCEPT | human | 53 | 50 | 3 | 0 | 94.3% | 86.0% |
| S1 | both | ratio | all | D2 | ACCEPT | print | 53 | 52 | 1 | 0 | 98.1% | 91.4% |
| S1 | both | ratio | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | all | L1 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | ratio | all | L1 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S1 | both | ratio | all | L1 | HOLD | human | 99 | 55 | 41 | 3 | 57.3% | 48.4% |
| S1 | both | ratio | all | L1 | HOLD | print | 99 | 49 | 38 | 12 | 56.3% | 46.9% |
| S1 | both | ratio | all | L2 | ACCEPT | human | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 | both | ratio | all | L2 | ACCEPT | print | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 | both | ratio | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 | both | ratio | all | all | ACCEPT | human | 59 | 54 | 5 | 0 | 91.5% | 83.0% |
| S1 | both | ratio | all | all | ACCEPT | print | 59 | 56 | 3 | 0 | 94.9% | 87.4% |
| S1 | both | ratio | all | all | HOLD | human | 116 | 67 | 44 | 5 | 60.4% | 52.1% |
| S1 | both | ratio | all | all | HOLD | print | 116 | 61 | 41 | 14 | 59.8% | 51.2% |
| S2 | 0 | strict | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | dev | D1 | HOLD | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | strict | dev | D1 | HOLD | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | strict | dev | D2 | ACCEPT | human | 21 | 20 | 1 | 0 | 95.2% | 79.3% |
| S2 | 0 | strict | dev | D2 | ACCEPT | print | 21 | 21 | 0 | 0 | 100.0% | 86.7% |
| S2 | 0 | strict | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | dev | L1 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | strict | dev | L1 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | strict | dev | L1 | HOLD | human | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S2 | 0 | strict | dev | L1 | HOLD | print | 15 | 9 | 2 | 4 | 81.8% | 53.0% |
| S2 | 0 | strict | dev | L2 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | strict | dev | L2 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | strict | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | dev | all | ACCEPT | human | 23 | 22 | 1 | 0 | 95.7% | 81.0% |
| S2 | 0 | strict | dev | all | ACCEPT | print | 23 | 23 | 0 | 0 | 100.0% | 87.8% |
| S2 | 0 | strict | dev | all | HOLD | human | 16 | 11 | 3 | 2 | 78.6% | 53.4% |
| S2 | 0 | strict | dev | all | HOLD | print | 16 | 10 | 2 | 4 | 83.3% | 56.2% |
| S2 | 0 | strict | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | held-out | D1 | HOLD | human | 8 | 5 | 2 | 1 | 71.4% | 34.1% |
| S2 | 0 | strict | held-out | D1 | HOLD | print | 8 | 5 | 2 | 1 | 71.4% | 34.1% |
| S2 | 0 | strict | held-out | D2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 0 | strict | held-out | D2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 0 | strict | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | held-out | L1 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | strict | held-out | L1 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | strict | held-out | L1 | HOLD | human | 23 | 19 | 4 | 0 | 82.6% | 64.5% |
| S2 | 0 | strict | held-out | L1 | HOLD | print | 23 | 16 | 5 | 2 | 76.2% | 56.3% |
| S2 | 0 | strict | held-out | L2 | ACCEPT | human | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S2 | 0 | strict | held-out | L2 | ACCEPT | print | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S2 | 0 | strict | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | held-out | all | ACCEPT | human | 6 | 5 | 1 | 0 | 83.3% | 41.8% |
| S2 | 0 | strict | held-out | all | ACCEPT | print | 6 | 5 | 1 | 0 | 83.3% | 41.8% |
| S2 | 0 | strict | held-out | all | HOLD | human | 31 | 24 | 6 | 1 | 80.0% | 64.3% |
| S2 | 0 | strict | held-out | all | HOLD | print | 31 | 21 | 7 | 3 | 75.0% | 58.1% |
| S2 | 0 | strict | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | all | D1 | HOLD | human | 9 | 6 | 2 | 1 | 75.0% | 40.0% |
| S2 | 0 | strict | all | D1 | HOLD | print | 9 | 6 | 2 | 1 | 75.0% | 40.0% |
| S2 | 0 | strict | all | D2 | ACCEPT | human | 23 | 22 | 1 | 0 | 95.7% | 81.0% |
| S2 | 0 | strict | all | D2 | ACCEPT | print | 23 | 23 | 0 | 0 | 100.0% | 87.8% |
| S2 | 0 | strict | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | all | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 0 | strict | all | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 0 | strict | all | L1 | HOLD | human | 38 | 29 | 7 | 2 | 80.6% | 66.6% |
| S2 | 0 | strict | all | L1 | HOLD | print | 38 | 25 | 7 | 6 | 78.1% | 62.8% |
| S2 | 0 | strict | all | L2 | ACCEPT | human | 4 | 3 | 1 | 0 | 75.0% | 24.9% |
| S2 | 0 | strict | all | L2 | ACCEPT | print | 4 | 3 | 1 | 0 | 75.0% | 24.9% |
| S2 | 0 | strict | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | strict | all | all | ACCEPT | human | 29 | 27 | 2 | 0 | 93.1% | 79.8% |
| S2 | 0 | strict | all | all | ACCEPT | print | 29 | 28 | 1 | 0 | 96.6% | 84.7% |
| S2 | 0 | strict | all | all | HOLD | human | 47 | 35 | 9 | 3 | 79.5% | 67.0% |
| S2 | 0 | strict | all | all | HOLD | print | 47 | 31 | 9 | 7 | 77.5% | 64.0% |
| S2 | 0 | ratio | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | dev | D1 | HOLD | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | ratio | dev | D1 | HOLD | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | ratio | dev | D2 | ACCEPT | human | 21 | 20 | 1 | 0 | 95.2% | 79.3% |
| S2 | 0 | ratio | dev | D2 | ACCEPT | print | 21 | 21 | 0 | 0 | 100.0% | 86.7% |
| S2 | 0 | ratio | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | dev | L1 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | ratio | dev | L1 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | ratio | dev | L1 | HOLD | human | 22 | 10 | 10 | 2 | 50.0% | 30.2% |
| S2 | 0 | ratio | dev | L1 | HOLD | print | 22 | 9 | 8 | 5 | 52.9% | 31.1% |
| S2 | 0 | ratio | dev | L2 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | dev | L2 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | dev | all | ACCEPT | human | 22 | 21 | 1 | 0 | 95.5% | 80.2% |
| S2 | 0 | ratio | dev | all | ACCEPT | print | 22 | 22 | 0 | 0 | 100.0% | 87.3% |
| S2 | 0 | ratio | dev | all | HOLD | human | 23 | 11 | 10 | 2 | 52.4% | 32.8% |
| S2 | 0 | ratio | dev | all | HOLD | print | 23 | 10 | 8 | 5 | 55.6% | 34.1% |
| S2 | 0 | ratio | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | held-out | D1 | HOLD | human | 8 | 5 | 2 | 1 | 71.4% | 34.1% |
| S2 | 0 | ratio | held-out | D1 | HOLD | print | 8 | 5 | 2 | 1 | 71.4% | 34.1% |
| S2 | 0 | ratio | held-out | D2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 0 | ratio | held-out | D2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 0 | ratio | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | held-out | L1 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | ratio | held-out | L1 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 0 | ratio | held-out | L1 | HOLD | human | 31 | 20 | 11 | 0 | 64.5% | 48.2% |
| S2 | 0 | ratio | held-out | L1 | HOLD | print | 31 | 17 | 12 | 2 | 58.6% | 41.7% |
| S2 | 0 | ratio | held-out | L2 | ACCEPT | human | 2 | 1 | 1 | 0 | 50.0% | 2.5% |
| S2 | 0 | ratio | held-out | L2 | ACCEPT | print | 2 | 1 | 1 | 0 | 50.0% | 2.5% |
| S2 | 0 | ratio | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | held-out | all | ACCEPT | human | 5 | 4 | 1 | 0 | 80.0% | 34.3% |
| S2 | 0 | ratio | held-out | all | ACCEPT | print | 5 | 4 | 1 | 0 | 80.0% | 34.3% |
| S2 | 0 | ratio | held-out | all | HOLD | human | 39 | 25 | 13 | 1 | 65.8% | 51.2% |
| S2 | 0 | ratio | held-out | all | HOLD | print | 39 | 22 | 14 | 3 | 61.1% | 46.0% |
| S2 | 0 | ratio | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | all | D1 | HOLD | human | 9 | 6 | 2 | 1 | 75.0% | 40.0% |
| S2 | 0 | ratio | all | D1 | HOLD | print | 9 | 6 | 2 | 1 | 75.0% | 40.0% |
| S2 | 0 | ratio | all | D2 | ACCEPT | human | 23 | 22 | 1 | 0 | 95.7% | 81.0% |
| S2 | 0 | ratio | all | D2 | ACCEPT | print | 23 | 23 | 0 | 0 | 100.0% | 87.8% |
| S2 | 0 | ratio | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | all | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 0 | ratio | all | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 0 | ratio | all | L1 | HOLD | human | 53 | 30 | 21 | 2 | 58.8% | 46.3% |
| S2 | 0 | ratio | all | L1 | HOLD | print | 53 | 26 | 20 | 7 | 56.5% | 43.4% |
| S2 | 0 | ratio | all | L2 | ACCEPT | human | 2 | 1 | 1 | 0 | 50.0% | 2.5% |
| S2 | 0 | ratio | all | L2 | ACCEPT | print | 2 | 1 | 1 | 0 | 50.0% | 2.5% |
| S2 | 0 | ratio | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 0 | ratio | all | all | ACCEPT | human | 27 | 25 | 2 | 0 | 92.6% | 78.5% |
| S2 | 0 | ratio | all | all | ACCEPT | print | 27 | 26 | 1 | 0 | 96.3% | 83.6% |
| S2 | 0 | ratio | all | all | HOLD | human | 62 | 36 | 23 | 3 | 61.0% | 49.5% |
| S2 | 0 | ratio | all | all | HOLD | print | 62 | 32 | 22 | 8 | 59.3% | 47.2% |
| S2 | 1 | strict | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | dev | D1 | HOLD | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | strict | dev | D1 | HOLD | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | strict | dev | D2 | ACCEPT | human | 22 | 20 | 2 | 0 | 90.9% | 74.1% |
| S2 | 1 | strict | dev | D2 | ACCEPT | print | 22 | 21 | 1 | 0 | 95.5% | 80.2% |
| S2 | 1 | strict | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | dev | L1 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | strict | dev | L1 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | strict | dev | L1 | HOLD | human | 13 | 10 | 2 | 1 | 83.3% | 56.2% |
| S2 | 1 | strict | dev | L1 | HOLD | print | 13 | 9 | 1 | 3 | 90.0% | 60.6% |
| S2 | 1 | strict | dev | L2 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | strict | dev | L2 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | strict | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | dev | all | ACCEPT | human | 24 | 22 | 2 | 0 | 91.7% | 76.0% |
| S2 | 1 | strict | dev | all | ACCEPT | print | 24 | 23 | 1 | 0 | 95.8% | 81.7% |
| S2 | 1 | strict | dev | all | HOLD | human | 14 | 11 | 2 | 1 | 84.6% | 59.0% |
| S2 | 1 | strict | dev | all | HOLD | print | 14 | 10 | 1 | 3 | 90.9% | 63.6% |
| S2 | 1 | strict | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | held-out | D1 | HOLD | human | 7 | 5 | 1 | 1 | 83.3% | 41.8% |
| S2 | 1 | strict | held-out | D1 | HOLD | print | 7 | 5 | 1 | 1 | 83.3% | 41.8% |
| S2 | 1 | strict | held-out | D2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | strict | held-out | D2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | strict | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | held-out | L1 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | strict | held-out | L1 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | strict | held-out | L1 | HOLD | human | 22 | 18 | 4 | 0 | 81.8% | 63.1% |
| S2 | 1 | strict | held-out | L1 | HOLD | print | 22 | 15 | 5 | 2 | 75.0% | 54.4% |
| S2 | 1 | strict | held-out | L2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | strict | held-out | L2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | strict | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | held-out | all | ACCEPT | human | 5 | 5 | 0 | 0 | 100.0% | 54.9% |
| S2 | 1 | strict | held-out | all | ACCEPT | print | 5 | 5 | 0 | 0 | 100.0% | 54.9% |
| S2 | 1 | strict | held-out | all | HOLD | human | 29 | 23 | 5 | 1 | 82.1% | 66.1% |
| S2 | 1 | strict | held-out | all | HOLD | print | 29 | 20 | 6 | 3 | 76.9% | 59.5% |
| S2 | 1 | strict | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | all | D1 | HOLD | human | 8 | 6 | 1 | 1 | 85.7% | 47.9% |
| S2 | 1 | strict | all | D1 | HOLD | print | 8 | 6 | 1 | 1 | 85.7% | 47.9% |
| S2 | 1 | strict | all | D2 | ACCEPT | human | 24 | 22 | 2 | 0 | 91.7% | 76.0% |
| S2 | 1 | strict | all | D2 | ACCEPT | print | 24 | 23 | 1 | 0 | 95.8% | 81.7% |
| S2 | 1 | strict | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | all | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | strict | all | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | strict | all | L1 | HOLD | human | 35 | 28 | 6 | 1 | 82.4% | 68.1% |
| S2 | 1 | strict | all | L1 | HOLD | print | 35 | 24 | 6 | 5 | 80.0% | 64.3% |
| S2 | 1 | strict | all | L2 | ACCEPT | human | 3 | 3 | 0 | 0 | 100.0% | 36.8% |
| S2 | 1 | strict | all | L2 | ACCEPT | print | 3 | 3 | 0 | 0 | 100.0% | 36.8% |
| S2 | 1 | strict | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | strict | all | all | ACCEPT | human | 29 | 27 | 2 | 0 | 93.1% | 79.8% |
| S2 | 1 | strict | all | all | ACCEPT | print | 29 | 28 | 1 | 0 | 96.6% | 84.7% |
| S2 | 1 | strict | all | all | HOLD | human | 43 | 34 | 7 | 2 | 82.9% | 70.3% |
| S2 | 1 | strict | all | all | HOLD | print | 43 | 30 | 7 | 6 | 81.1% | 67.4% |
| S2 | 1 | ratio | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | dev | D1 | HOLD | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | dev | D1 | HOLD | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | dev | D2 | ACCEPT | human | 22 | 20 | 2 | 0 | 90.9% | 74.1% |
| S2 | 1 | ratio | dev | D2 | ACCEPT | print | 22 | 21 | 1 | 0 | 95.5% | 80.2% |
| S2 | 1 | ratio | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | dev | L1 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | dev | L1 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | dev | L1 | HOLD | human | 19 | 10 | 8 | 1 | 55.6% | 34.1% |
| S2 | 1 | ratio | dev | L1 | HOLD | print | 19 | 9 | 5 | 5 | 64.3% | 39.0% |
| S2 | 1 | ratio | dev | L2 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | dev | L2 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | dev | all | ACCEPT | human | 23 | 21 | 2 | 0 | 91.3% | 75.1% |
| S2 | 1 | ratio | dev | all | ACCEPT | print | 23 | 22 | 1 | 0 | 95.7% | 81.0% |
| S2 | 1 | ratio | dev | all | HOLD | human | 20 | 11 | 8 | 1 | 57.9% | 36.8% |
| S2 | 1 | ratio | dev | all | HOLD | print | 20 | 10 | 5 | 5 | 66.7% | 42.3% |
| S2 | 1 | ratio | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | held-out | D1 | HOLD | human | 7 | 5 | 1 | 1 | 83.3% | 41.8% |
| S2 | 1 | ratio | held-out | D1 | HOLD | print | 7 | 5 | 1 | 1 | 83.3% | 41.8% |
| S2 | 1 | ratio | held-out | D2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | ratio | held-out | D2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | ratio | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | held-out | L1 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | held-out | L1 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | held-out | L1 | HOLD | human | 30 | 19 | 11 | 0 | 63.3% | 46.7% |
| S2 | 1 | ratio | held-out | L1 | HOLD | print | 30 | 16 | 12 | 2 | 57.1% | 40.0% |
| S2 | 1 | ratio | held-out | L2 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | held-out | L2 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | held-out | all | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | 1 | ratio | held-out | all | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | 1 | ratio | held-out | all | HOLD | human | 37 | 24 | 12 | 1 | 66.7% | 51.7% |
| S2 | 1 | ratio | held-out | all | HOLD | print | 37 | 21 | 13 | 3 | 61.8% | 46.2% |
| S2 | 1 | ratio | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | all | D1 | HOLD | human | 8 | 6 | 1 | 1 | 85.7% | 47.9% |
| S2 | 1 | ratio | all | D1 | HOLD | print | 8 | 6 | 1 | 1 | 85.7% | 47.9% |
| S2 | 1 | ratio | all | D2 | ACCEPT | human | 24 | 22 | 2 | 0 | 91.7% | 76.0% |
| S2 | 1 | ratio | all | D2 | ACCEPT | print | 24 | 23 | 1 | 0 | 95.8% | 81.7% |
| S2 | 1 | ratio | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | all | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | ratio | all | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | 1 | ratio | all | L1 | HOLD | human | 49 | 29 | 19 | 1 | 60.4% | 47.5% |
| S2 | 1 | ratio | all | L1 | HOLD | print | 49 | 25 | 17 | 7 | 59.5% | 45.7% |
| S2 | 1 | ratio | all | L2 | ACCEPT | human | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | all | L2 | ACCEPT | print | 1 | 1 | 0 | 0 | 100.0% | 5.0% |
| S2 | 1 | ratio | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | 1 | ratio | all | all | ACCEPT | human | 27 | 25 | 2 | 0 | 92.6% | 78.5% |
| S2 | 1 | ratio | all | all | ACCEPT | print | 27 | 26 | 1 | 0 | 96.3% | 83.6% |
| S2 | 1 | ratio | all | all | HOLD | human | 57 | 35 | 20 | 2 | 63.6% | 51.7% |
| S2 | 1 | ratio | all | all | HOLD | print | 57 | 31 | 18 | 8 | 63.3% | 50.5% |
| S2 | both | strict | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | dev | D1 | HOLD | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | strict | dev | D1 | HOLD | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | strict | dev | D2 | ACCEPT | human | 43 | 40 | 3 | 0 | 93.0% | 82.9% |
| S2 | both | strict | dev | D2 | ACCEPT | print | 43 | 42 | 1 | 0 | 97.7% | 89.4% |
| S2 | both | strict | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | dev | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | strict | dev | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | strict | dev | L1 | HOLD | human | 28 | 20 | 5 | 3 | 80.0% | 62.5% |
| S2 | both | strict | dev | L1 | HOLD | print | 28 | 18 | 3 | 7 | 85.7% | 67.1% |
| S2 | both | strict | dev | L2 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | strict | dev | L2 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | strict | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | dev | all | ACCEPT | human | 47 | 44 | 3 | 0 | 93.6% | 84.3% |
| S2 | both | strict | dev | all | ACCEPT | print | 47 | 46 | 1 | 0 | 97.9% | 90.3% |
| S2 | both | strict | dev | all | HOLD | human | 30 | 22 | 5 | 3 | 81.5% | 64.9% |
| S2 | both | strict | dev | all | HOLD | print | 30 | 20 | 3 | 7 | 87.0% | 69.6% |
| S2 | both | strict | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | held-out | D1 | HOLD | human | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S2 | both | strict | held-out | D1 | HOLD | print | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S2 | both | strict | held-out | D2 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | both | strict | held-out | D2 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | both | strict | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | held-out | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | strict | held-out | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | strict | held-out | L1 | HOLD | human | 45 | 37 | 8 | 0 | 82.2% | 70.2% |
| S2 | both | strict | held-out | L1 | HOLD | print | 45 | 31 | 10 | 4 | 75.6% | 62.1% |
| S2 | both | strict | held-out | L2 | ACCEPT | human | 5 | 4 | 1 | 0 | 80.0% | 34.3% |
| S2 | both | strict | held-out | L2 | ACCEPT | print | 5 | 4 | 1 | 0 | 80.0% | 34.3% |
| S2 | both | strict | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | held-out | all | ACCEPT | human | 11 | 10 | 1 | 0 | 90.9% | 63.6% |
| S2 | both | strict | held-out | all | ACCEPT | print | 11 | 10 | 1 | 0 | 90.9% | 63.6% |
| S2 | both | strict | held-out | all | HOLD | human | 60 | 47 | 11 | 2 | 81.0% | 70.6% |
| S2 | both | strict | held-out | all | HOLD | print | 60 | 41 | 13 | 6 | 75.9% | 64.5% |
| S2 | both | strict | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | all | D1 | HOLD | human | 17 | 12 | 3 | 2 | 80.0% | 56.0% |
| S2 | both | strict | all | D1 | HOLD | print | 17 | 12 | 3 | 2 | 80.0% | 56.0% |
| S2 | both | strict | all | D2 | ACCEPT | human | 47 | 44 | 3 | 0 | 93.6% | 84.3% |
| S2 | both | strict | all | D2 | ACCEPT | print | 47 | 46 | 1 | 0 | 97.9% | 90.3% |
| S2 | both | strict | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | all | L1 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | both | strict | all | L1 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | both | strict | all | L1 | HOLD | human | 73 | 57 | 13 | 3 | 81.4% | 72.1% |
| S2 | both | strict | all | L1 | HOLD | print | 73 | 49 | 13 | 11 | 79.0% | 68.7% |
| S2 | both | strict | all | L2 | ACCEPT | human | 7 | 6 | 1 | 0 | 85.7% | 47.9% |
| S2 | both | strict | all | L2 | ACCEPT | print | 7 | 6 | 1 | 0 | 85.7% | 47.9% |
| S2 | both | strict | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | strict | all | all | ACCEPT | human | 58 | 54 | 4 | 0 | 93.1% | 84.9% |
| S2 | both | strict | all | all | ACCEPT | print | 58 | 56 | 2 | 0 | 96.6% | 89.5% |
| S2 | both | strict | all | all | HOLD | human | 90 | 69 | 16 | 5 | 81.2% | 72.8% |
| S2 | both | strict | all | all | HOLD | print | 90 | 61 | 16 | 13 | 79.2% | 70.2% |
| S2 | both | ratio | dev | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | dev | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | dev | D1 | HOLD | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | ratio | dev | D1 | HOLD | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | ratio | dev | D2 | ACCEPT | human | 43 | 40 | 3 | 0 | 93.0% | 82.9% |
| S2 | both | ratio | dev | D2 | ACCEPT | print | 43 | 42 | 1 | 0 | 97.7% | 89.4% |
| S2 | both | ratio | dev | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | dev | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | dev | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | ratio | dev | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | ratio | dev | L1 | HOLD | human | 41 | 20 | 18 | 3 | 52.6% | 38.2% |
| S2 | both | ratio | dev | L1 | HOLD | print | 41 | 18 | 13 | 10 | 58.1% | 41.8% |
| S2 | both | ratio | dev | L2 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | dev | L2 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | dev | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | dev | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | dev | all | ACCEPT | human | 45 | 42 | 3 | 0 | 93.3% | 83.7% |
| S2 | both | ratio | dev | all | ACCEPT | print | 45 | 44 | 1 | 0 | 97.8% | 89.9% |
| S2 | both | ratio | dev | all | HOLD | human | 43 | 22 | 18 | 3 | 55.0% | 40.9% |
| S2 | both | ratio | dev | all | HOLD | print | 43 | 20 | 13 | 10 | 60.6% | 44.8% |
| S2 | both | ratio | held-out | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | held-out | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | held-out | D1 | HOLD | human | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S2 | both | ratio | held-out | D1 | HOLD | print | 15 | 10 | 3 | 2 | 76.9% | 50.5% |
| S2 | both | ratio | held-out | D2 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | both | ratio | held-out | D2 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | both | ratio | held-out | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | held-out | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | held-out | L1 | ACCEPT | human | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | ratio | held-out | L1 | ACCEPT | print | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | both | ratio | held-out | L1 | HOLD | human | 61 | 39 | 22 | 0 | 63.9% | 52.6% |
| S2 | both | ratio | held-out | L1 | HOLD | print | 61 | 33 | 24 | 4 | 57.9% | 46.1% |
| S2 | both | ratio | held-out | L2 | ACCEPT | human | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S2 | both | ratio | held-out | L2 | ACCEPT | print | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S2 | both | ratio | held-out | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | held-out | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | held-out | all | ACCEPT | human | 9 | 8 | 1 | 0 | 88.9% | 57.1% |
| S2 | both | ratio | held-out | all | ACCEPT | print | 9 | 8 | 1 | 0 | 88.9% | 57.1% |
| S2 | both | ratio | held-out | all | HOLD | human | 76 | 49 | 25 | 2 | 66.2% | 56.1% |
| S2 | both | ratio | held-out | all | HOLD | print | 76 | 43 | 27 | 6 | 61.4% | 50.9% |
| S2 | both | ratio | all | D1 | ACCEPT | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | all | D1 | ACCEPT | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | all | D1 | HOLD | human | 17 | 12 | 3 | 2 | 80.0% | 56.0% |
| S2 | both | ratio | all | D1 | HOLD | print | 17 | 12 | 3 | 2 | 80.0% | 56.0% |
| S2 | both | ratio | all | D2 | ACCEPT | human | 47 | 44 | 3 | 0 | 93.6% | 84.3% |
| S2 | both | ratio | all | D2 | ACCEPT | print | 47 | 46 | 1 | 0 | 97.9% | 90.3% |
| S2 | both | ratio | all | D2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | all | D2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | all | L1 | ACCEPT | human | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | both | ratio | all | L1 | ACCEPT | print | 4 | 4 | 0 | 0 | 100.0% | 47.3% |
| S2 | both | ratio | all | L1 | HOLD | human | 102 | 59 | 40 | 3 | 59.6% | 50.8% |
| S2 | both | ratio | all | L1 | HOLD | print | 102 | 51 | 37 | 14 | 58.0% | 48.6% |
| S2 | both | ratio | all | L2 | ACCEPT | human | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S2 | both | ratio | all | L2 | ACCEPT | print | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S2 | both | ratio | all | L2 | HOLD | human | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | all | L2 | HOLD | print | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | both | ratio | all | all | ACCEPT | human | 54 | 50 | 4 | 0 | 92.6% | 83.8% |
| S2 | both | ratio | all | all | ACCEPT | print | 54 | 52 | 2 | 0 | 96.3% | 88.8% |
| S2 | both | ratio | all | all | HOLD | human | 119 | 71 | 43 | 5 | 62.3% | 54.2% |
| S2 | both | ratio | all | all | HOLD | print | 119 | 63 | 40 | 16 | 61.2% | 52.6% |

## Every human → print decision verdict flip

| iteration | policy | seed | line / word | column | Google → proposal | human → print verdict | printed |
|---|---|---:|---|---|---|---|---|
| S1 | ratio | 0 | 8b6b0de9-p000004-l0017 / 3 | HOLD | εἷς, → εἰς | google_right → unknown | UNKNOWN |
| S1 | strict | 0 | 2793d64c-p000048-l0004 / 3 | HOLD | ἡσυχάση, → ἡσυχάσῃ | both_wrong → correct | ἡσυχάσῃ |
| S1 | ratio | 0 | 2793d64c-p000048-l0004 / 3 | HOLD | ἡσυχάση, → ἡσυχάσῃ | both_wrong → correct | ἡσυχάσῃ |
| S1 | strict | 0 | 9c1dca9b-p000015-l0064 / 1 | HOLD | ἐξῆντα → ἑξῆντα | correct → unknown | UNKNOWN |
| S1 | ratio | 0 | 9c1dca9b-p000015-l0064 / 1 | HOLD | ἐξῆντα → ἑξῆντα | correct → unknown | UNKNOWN |
| S1 | strict | 0 | 8b6b0de9-p000016-l0013 / 4 | ACCEPT | φωλεά → φωλεὰ | both_wrong → correct | φωλεὰ |
| S1 | ratio | 0 | 8b6b0de9-p000016-l0013 / 4 | ACCEPT | φωλεά → φωλεὰ | both_wrong → correct | φωλεὰ |
| S1 | strict | 0 | 22fda82b-p000063-l0018 / 2 | HOLD | ἑσιώπα. → ἐσιώπα | correct → google_right | ἑσιώπα |
| S1 | ratio | 0 | 22fda82b-p000063-l0018 / 2 | HOLD | ἑσιώπα. → ἐσιώπα | correct → google_right | ἑσιώπα |
| S1 | strict | 0 | 2793d64c-p000072-l0007 / 3 | HOLD | ἐκβάλη. → ἐκβάλῃ | correct → unknown | UNKNOWN |
| S1 | ratio | 0 | 2793d64c-p000072-l0007 / 3 | HOLD | ἐκβάλη. → ἐκβάλῃ | correct → unknown | UNKNOWN |
| S1 | strict | 0 | 602cc72e-p000113-l0009 / 2 | HOLD | ἁλώπηξ. → ἀλώπηξ | correct → google_right | ἁλώπηξ |
| S1 | ratio | 0 | 602cc72e-p000113-l0009 / 2 | HOLD | ἁλώπηξ. → ἀλώπηξ | correct → google_right | ἁλώπηξ |
| S1 | strict | 0 | 384c3f89-p000179-l0027 / 5 | HOLD | δίω → δίῳ | both_wrong → unknown | UNKNOWN |
| S1 | ratio | 0 | 384c3f89-p000179-l0027 / 5 | HOLD | δίω → δίῳ | both_wrong → unknown | UNKNOWN |
| S1 | ratio | 1 | 8b6b0de9-p000004-l0017 / 3 | HOLD | εἷς, → εἰς | google_right → unknown | UNKNOWN |
| S1 | strict | 1 | 2793d64c-p000048-l0004 / 3 | HOLD | ἡσυχάση, → ἡσυχάσῃ | both_wrong → correct | ἡσυχάσῃ |
| S1 | ratio | 1 | 2793d64c-p000048-l0004 / 3 | HOLD | ἡσυχάση, → ἡσυχάσῃ | both_wrong → correct | ἡσυχάσῃ |
| S1 | ratio | 1 | 8b6b0de9-p000011-l0017 / 1 | HOLD | εἷς → εἰς | google_right → unknown | UNKNOWN |
| S1 | strict | 1 | 9c1dca9b-p000015-l0064 / 1 | HOLD | ἐξῆντα → ἑξῆντα | correct → unknown | UNKNOWN |
| S1 | ratio | 1 | 9c1dca9b-p000015-l0064 / 1 | HOLD | ἐξῆντα → ἑξῆντα | correct → unknown | UNKNOWN |
| S1 | strict | 1 | 8b6b0de9-p000016-l0013 / 4 | ACCEPT | φωλεά → φωλεὰ | both_wrong → correct | φωλεὰ |
| S1 | ratio | 1 | 8b6b0de9-p000016-l0013 / 4 | ACCEPT | φωλεά → φωλεὰ | both_wrong → correct | φωλεὰ |
| S1 | strict | 1 | 22fda82b-p000063-l0018 / 2 | HOLD | ἑσιώπα. → ἐσιώπα | correct → google_right | ἑσιώπα |
| S1 | ratio | 1 | 22fda82b-p000063-l0018 / 2 | HOLD | ἑσιώπα. → ἐσιώπα | correct → google_right | ἑσιώπα |
| S1 | strict | 1 | 2793d64c-p000072-l0007 / 3 | HOLD | ἐκβάλη. → ἐκβάλῃ | correct → unknown | UNKNOWN |
| S1 | ratio | 1 | 2793d64c-p000072-l0007 / 3 | HOLD | ἐκβάλη. → ἐκβάλῃ | correct → unknown | UNKNOWN |
| S1 | strict | 1 | 602cc72e-p000113-l0009 / 2 | HOLD | ἁλώπηξ. → ἀλώπηξ | correct → google_right | ἁλώπηξ |
| S1 | ratio | 1 | 602cc72e-p000113-l0009 / 2 | HOLD | ἁλώπηξ. → ἀλώπηξ | correct → google_right | ἁλώπηξ |
| S1 | strict | 1 | 384c3f89-p000179-l0027 / 5 | HOLD | δίω → δίῳ | both_wrong → unknown | UNKNOWN |
| S1 | ratio | 1 | 384c3f89-p000179-l0027 / 5 | HOLD | δίω → δίῳ | both_wrong → unknown | UNKNOWN |
| S2 | ratio | 0 | 8b6b0de9-p000004-l0017 / 3 | HOLD | εἷς, → εἰς | google_right → unknown | UNKNOWN |
| S2 | strict | 0 | 2793d64c-p000048-l0004 / 3 | HOLD | ἡσυχάση, → ἡσυχάσῃ | both_wrong → correct | ἡσυχάσῃ |
| S2 | ratio | 0 | 2793d64c-p000048-l0004 / 3 | HOLD | ἡσυχάση, → ἡσυχάσῃ | both_wrong → correct | ἡσυχάσῃ |
| S2 | strict | 0 | 9c1dca9b-p000015-l0064 / 1 | HOLD | ἐξῆντα → ἑξῆντα | correct → unknown | UNKNOWN |
| S2 | ratio | 0 | 9c1dca9b-p000015-l0064 / 1 | HOLD | ἐξῆντα → ἑξῆντα | correct → unknown | UNKNOWN |
| S2 | strict | 0 | 8b6b0de9-p000011-l0030 / 2 | HOLD | ἔκαστος → ἕκαστος | correct → unknown | UNKNOWN |
| S2 | ratio | 0 | 8b6b0de9-p000011-l0030 / 2 | HOLD | ἔκαστος → ἕκαστος | correct → unknown | UNKNOWN |
| S2 | strict | 0 | 8b6b0de9-p000016-l0013 / 4 | ACCEPT | φωλεά → φωλεὰ | both_wrong → correct | φωλεὰ |
| S2 | ratio | 0 | 8b6b0de9-p000016-l0013 / 4 | ACCEPT | φωλεά → φωλεὰ | both_wrong → correct | φωλεὰ |
| S2 | strict | 0 | 22fda82b-p000063-l0018 / 2 | HOLD | ἑσιώπα. → ἐσιώπα | correct → google_right | ἑσιώπα |
| S2 | ratio | 0 | 22fda82b-p000063-l0018 / 2 | HOLD | ἑσιώπα. → ἐσιώπα | correct → google_right | ἑσιώπα |
| S2 | strict | 0 | 2793d64c-p000072-l0007 / 3 | HOLD | ἐκβάλη. → ἐκβάλῃ | correct → unknown | UNKNOWN |
| S2 | ratio | 0 | 2793d64c-p000072-l0007 / 3 | HOLD | ἐκβάλη. → ἐκβάλῃ | correct → unknown | UNKNOWN |
| S2 | strict | 0 | 602cc72e-p000113-l0009 / 2 | HOLD | ἁλώπηξ. → ἀλώπηξ | correct → google_right | ἁλώπηξ |
| S2 | ratio | 0 | 602cc72e-p000113-l0009 / 2 | HOLD | ἁλώπηξ. → ἀλώπηξ | correct → google_right | ἁλώπηξ |
| S2 | strict | 0 | 384c3f89-p000179-l0027 / 5 | HOLD | δίω → δίῳ | both_wrong → unknown | UNKNOWN |
| S2 | ratio | 0 | 384c3f89-p000179-l0027 / 5 | HOLD | δίω → δίῳ | both_wrong → unknown | UNKNOWN |
| S2 | ratio | 1 | 8b6b0de9-p000004-l0017 / 3 | HOLD | εἷς, → εἰς | google_right → unknown | UNKNOWN |
| S2 | strict | 1 | 2793d64c-p000048-l0004 / 3 | HOLD | ἡσυχάση, → ἡσυχάσῃ | both_wrong → correct | ἡσυχάσῃ |
| S2 | ratio | 1 | 2793d64c-p000048-l0004 / 3 | HOLD | ἡσυχάση, → ἡσυχάσῃ | both_wrong → correct | ἡσυχάσῃ |
| S2 | ratio | 1 | 8b6b0de9-p000011-l0017 / 1 | HOLD | εἷς → εἰς | google_right → unknown | UNKNOWN |
| S2 | strict | 1 | 9c1dca9b-p000015-l0064 / 1 | HOLD | ἐξῆντα → ἑξῆντα | correct → unknown | UNKNOWN |
| S2 | ratio | 1 | 9c1dca9b-p000015-l0064 / 1 | HOLD | ἐξῆντα → ἑξῆντα | correct → unknown | UNKNOWN |
| S2 | strict | 1 | 8b6b0de9-p000011-l0030 / 2 | HOLD | ἔκαστος → ἕκαστος | correct → unknown | UNKNOWN |
| S2 | ratio | 1 | 8b6b0de9-p000011-l0030 / 2 | HOLD | ἔκαστος → ἕκαστος | correct → unknown | UNKNOWN |
| S2 | strict | 1 | 8b6b0de9-p000016-l0013 / 4 | ACCEPT | φωλεά → φωλεὰ | both_wrong → correct | φωλεὰ |
| S2 | ratio | 1 | 8b6b0de9-p000016-l0013 / 4 | ACCEPT | φωλεά → φωλεὰ | both_wrong → correct | φωλεὰ |
| S2 | strict | 1 | 22fda82b-p000063-l0018 / 2 | HOLD | ἑσιώπα. → ἐσιώπα | correct → google_right | ἑσιώπα |
| S2 | ratio | 1 | 22fda82b-p000063-l0018 / 2 | HOLD | ἑσιώπα. → ἐσιώπα | correct → google_right | ἑσιώπα |
| S2 | strict | 1 | 2793d64c-p000072-l0007 / 3 | HOLD | ἐκβάλη. → ἐκβάλῃ | correct → unknown | UNKNOWN |
| S2 | ratio | 1 | 2793d64c-p000072-l0007 / 3 | HOLD | ἐκβάλη. → ἐκβάλῃ | correct → unknown | UNKNOWN |
| S2 | strict | 1 | 602cc72e-p000113-l0009 / 2 | HOLD | ἁλώπηξ. → ἀλώπηξ | correct → google_right | ἁλώπηξ |
| S2 | ratio | 1 | 602cc72e-p000113-l0009 / 2 | HOLD | ἁλώπηξ. → ἀλώπηξ | correct → google_right | ἁλώπηξ |
| S2 | strict | 1 | 384c3f89-p000179-l0027 / 5 | HOLD | δίω → δίῳ | both_wrong → unknown | UNKNOWN |
| S2 | ratio | 1 | 384c3f89-p000179-l0027 / 5 | HOLD | δίω → δίῳ | both_wrong → unknown | UNKNOWN |

## Crops and review selection

Fixed seed-20261016 sample: `heldout_sample60.txt`; 60 cards plus changed held-out detection/decisions, total eligible 636, capped at 140. Remaining 496 IDs in `S2_sheet_overflow.txt`. Only HTML is built; no db collection/document was touched. Existing 33 notes are displayed. The save script now writes printed text only after a real input event (`printed_edited: true`) and merges note-only updates.

Before/after crop witnesses (same native pixels; old/new detector evidence and bounding boxes in `S2_lines.jsonl.gz`; embedded annotated images in the owner sheet for selected lines):

- `02a3a2a6-p000046-l0014`: [paired before/after crop](crops_S2/02a3a2a6-p000046-l0014.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/02a3a2a6/p000046-l0014.png`
- `02a3a2a6-p000046-l0025`: [paired before/after crop](crops_S2/02a3a2a6-p000046-l0025.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/02a3a2a6/p000046-l0025.png`
- `177b717d-p000013-l0009`: [paired before/after crop](crops_S2/177b717d-p000013-l0009.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/177b717d/p000013-l0009.png`
- `177b717d-p000097-l0007`: [paired before/after crop](crops_S2/177b717d-p000097-l0007.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/177b717d/p000097-l0007.png`
- `177b717d-p000097-l0010`: [paired before/after crop](crops_S2/177b717d-p000097-l0010.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/177b717d/p000097-l0010.png`
- `2793d64c-p000048-l0004`: [paired before/after crop](crops_S2/2793d64c-p000048-l0004.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/2793d64c/p000048-l0004.png`
- `2793d64c-p000048-l0010`: [paired before/after crop](crops_S2/2793d64c-p000048-l0010.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/2793d64c/p000048-l0010.png`
- `2793d64c-p000070-l0010`: [paired before/after crop](crops_S2/2793d64c-p000070-l0010.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/2793d64c/p000070-l0010.png`
- `2793d64c-p000070-l0014`: [paired before/after crop](crops_S2/2793d64c-p000070-l0014.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/2793d64c/p000070-l0014.png`
- `2793d64c-p000072-l0007`: [paired before/after crop](crops_S2/2793d64c-p000072-l0007.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/2793d64c/p000072-l0007.png`
- `384c3f89-p000030-l0021`: [paired before/after crop](crops_S2/384c3f89-p000030-l0021.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/384c3f89/p000030-l0021.png`
- `384c3f89-p000030-l0029`: [paired before/after crop](crops_S2/384c3f89-p000030-l0029.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/384c3f89/p000030-l0029.png`
- `384c3f89-p000053-l0021`: [paired before/after crop](crops_S2/384c3f89-p000053-l0021.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/384c3f89/p000053-l0021.png`
- `384c3f89-p000053-l0028`: [paired before/after crop](crops_S2/384c3f89-p000053-l0028.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/384c3f89/p000053-l0028.png`
- `384c3f89-p000068-l0036`: [paired before/after crop](crops_S2/384c3f89-p000068-l0036.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/384c3f89/p000068-l0036.png`
- `384c3f89-p000091-l0039`: [paired before/after crop](crops_S2/384c3f89-p000091-l0039.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/384c3f89/p000091-l0039.png`
- `384c3f89-p000121-l0024`: [paired before/after crop](crops_S2/384c3f89-p000121-l0024.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/384c3f89/p000121-l0024.png`
- `384c3f89-p000205-l0005`: [paired before/after crop](crops_S2/384c3f89-p000205-l0005.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/384c3f89/p000205-l0005.png`
- `51fe7386-p000024-l0015`: [paired before/after crop](crops_S2/51fe7386-p000024-l0015.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/51fe7386/p000024-l0015.png`
- `51fe7386-p000024-l0020`: [paired before/after crop](crops_S2/51fe7386-p000024-l0020.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/51fe7386/p000024-l0020.png`
- `602cc72e-p000155-l0009`: [paired before/after crop](crops_S2/602cc72e-p000155-l0009.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/602cc72e/p000155-l0009.png`
- `602cc72e-p000167-l0027`: [paired before/after crop](crops_S2/602cc72e-p000167-l0027.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/602cc72e/p000167-l0027.png`
- `8b6b0de9-p000004-l0028`: [paired before/after crop](crops_S2/8b6b0de9-p000004-l0028.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000004-l0028.png`
- `8b6b0de9-p000007-l0030`: [paired before/after crop](crops_S2/8b6b0de9-p000007-l0030.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000007-l0030.png`
- `8b6b0de9-p000008-l0001`: [paired before/after crop](crops_S2/8b6b0de9-p000008-l0001.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000008-l0001.png`
- `8b6b0de9-p000008-l0002`: [paired before/after crop](crops_S2/8b6b0de9-p000008-l0002.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000008-l0002.png`
- `8b6b0de9-p000008-l0019`: [paired before/after crop](crops_S2/8b6b0de9-p000008-l0019.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000008-l0019.png`
- `8b6b0de9-p000008-l0024`: [paired before/after crop](crops_S2/8b6b0de9-p000008-l0024.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000008-l0024.png`
- `8b6b0de9-p000011-l0007`: [paired before/after crop](crops_S2/8b6b0de9-p000011-l0007.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000011-l0007.png`
- `8b6b0de9-p000011-l0014`: [paired before/after crop](crops_S2/8b6b0de9-p000011-l0014.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000011-l0014.png`
- `8b6b0de9-p000021-l0007`: [paired before/after crop](crops_S2/8b6b0de9-p000021-l0007.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/8b6b0de9/p000021-l0007.png`
- `9c1dca9b-p000005-l0017`: [paired before/after crop](crops_S2/9c1dca9b-p000005-l0017.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/9c1dca9b/p000005-l0017.png`
- `9c1dca9b-p000015-l0065`: [paired before/after crop](crops_S2/9c1dca9b-p000015-l0065.png); native `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/harvest/harvest_big/wikisource/crops/9c1dca9b/p000015-l0065.png`

## Validation and open work

Synthetic detector/compound/two-line metric cases pass. Existing labelfix tests: all runnable tests pass; one localhost capture test cannot bind under the sandbox (PermissionError). Test evidence: `S2_verification.json`; 109 tests passed, the existing socket test was separately observed to fail at bind and then deselected. The actual notes JavaScript was exercised with an in-memory db stub: a note-only save omits printed/printed_edited, an edited printed field sets printed_edited=true, and updates merge without replacing existing fields. Rare compound sample support is insufficient; zero-sample classes are explicit. The owner case `384c3f89-p000096-l0004` (ᾗσι) remains unrecovered: its dasia+circumflex+subscript class has zero fitting examples. Two note/truth conflicts are retained (slot 8 on 02a3a2a6-p000046-l0014; slot 13 on 177b717d-p000013-l0009). Physical masks are unchanged; the stricter subscript rule can lose attached or borderline genuine subscripts by design. Owner slot-truth conflicts and unmapped slots remain open. This iteration is a measured candidate, not an accepted replacement.

S2 RESULT: held-out line mark P 54.0%→92.0% R 84.0%→83.3% (owner 33-line expectations fixed 18/59); ascender false-mark rate 69.9%→3.5%; compound recall 66.2%; S1 ACCEPT vs print p=96.6% (LB95 89.5%), HOLD vs print p=79.2%
