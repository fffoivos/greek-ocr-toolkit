# S3 — recall candidate; precision goal not met

CPU only, network off, zero CTC forward passes. 598 DEV lines fit/calibrate; 666 lines from 14 frozen held-out books evaluate only. HEAD observed `cc57dc26` (two brief-only commits beyond requested 4a3ace67). No git writes; all changes remain in this worktree.

Print truth is unchanged: `print_truth_s0.json` plus three-way agreement words. The recogniser locates base letters only. Whole visible lines are scored; unknown words and competing character owners stay unknown. S2 outputs/model/artifacts are preserved. The first candidate failed DEV precision (83.98%); DEV-only inspection rejected right-hand eta descenders and whole unmarked bodies. Final classifier and geometric rules were frozen before reading final held-out results. No held-out thresholds or samples were fitted.

Changes: vowel-relative subscripts use 0.25–0.9 x-height, ink-band darkness, under-body position with 0.3 x-height slack; touching wedges must leave the left half. Thin punctuation runs, neighbouring descenders, specks and border ink are rejected. Bottom-edge ink is UNKNOWN for subscript presence, not an absent subscript. Joined vowel top lobes do not need a consonant-style neck; complete short bodies cannot supply a lobe. A short-body height mode repairs overestimated bands. Non-vowel ink remains diagnostic (rho may carry breathing). A CTC span crossing two components of at most 1.6 x-height uses their union; whole-line scoring refuses a union with another known character owner. Twelve compound classes remain explicit; no samples were invented.

## Whole-line metrics

Headline recall retains ALL known printed positives, including abstained cut-off subscripts. An UNKNOWN prediction is not an assertion of absence, but cannot earn a recall hit. Conditional recall on fully observable slots is shown separately; it must not replace the 94-positive subscript denominator. Mark identities are exact; nonempty unclassified blobs count as errors. Classifier argmax is diagnostic; engine decisions retain calibrated tau.

| population | detector | known / unknown slots | TP / FP / FN | P | R | F1 |
|---|---|---:|---:|---:|---:|---:|
| held-out (original scope) | S2 frozen | 18229 / 2647 | 3375 / 294 / 678 | 92.0% | 83.3% | 87.4% |
| held-out (all known print) | S2 | 18229 / 2647 | 3375 / 294 / 678 | 92.0% | 83.3% | 87.4% |
| held-out (all known print) | S3 | 18229 / 2647 | 3497 / 328 / 556 | 91.4% | 86.3% | 88.8% |
| owner 33 | S2 | 720 / 117 | 122 / 17 / 56 | 87.8% | 68.5% | 77.0% |
| owner 33 | S3 | 720 / 117 | 141 / 21 / 37 | 87.0% | 79.2% | 82.9% |

Bottom-clipped subscript slots: 443 held-out, counted separately from unknown word/slot ownership. Fully observable subscript recall (47 known positives): 78.7% → 89.4%. This conditional result excludes 47 of 94 printed positives; headline recall does not.

| kind | S2 P | S3 P | S2 R | S3 R | S2 F1 | S3 F1 |
|---|---:|---:|---:|---:|---:|---:|
| accent | 93.5% | 91.8% | 90.6% | 95.2% | 92.0% | 93.5% |
| breathing | 94.0% | 95.6% | 82.0% | 84.6% | 87.6% | 89.8% |
| compound | 75.8% | 76.6% | 66.2% | 62.4% | 70.7% | 68.8% |
| subscript | 100.0% | 97.7% | 41.5% | 44.7% | 58.6% | 61.3% |
| dialytika | — | — | 0.0% | 0.0% | 0.0% | 0.0% |
| apostrophe | 99.2% | 99.2% | 60.7% | 60.7% | 75.3% | 75.3% |

## Subscripts and specks side by side

| population | S2 subscript recall | S3 subscript recall | S2 speck rejection | S3 speck rejection |
|---|---:|---:|---:|---:|
| held-out | 41.5% | 44.7% | 94/94 = 100.0% | 93/94 = 98.9% |

Speck exposure is the S2 operational stratum: known non-subscript slots with an S1 below blob, excluding cut-off evidence. It includes descenders/noise; it is not a newly adjudicated pure-speck population.

| held-out book | true subscripts | S2 P / R | S3 P / R |
|---|---:|---|---|
| wikisource:0b7bf21d | 0 | — / — | — / — |
| wikisource:177b717d | 3 | — / 0.0% | 0.0% / 0.0% |
| wikisource:22fda82b | 2 | 100.0% / 50.0% | 100.0% / 50.0% |
| wikisource:263438a3 | 0 | — / — | — / — |
| wikisource:384c3f89 | 80 | 100.0% / 42.5% | 100.0% / 45.0% |
| wikisource:4ad622a4 | 0 | — / — | — / — |
| wikisource:4f60b077 | 2 | — / 0.0% | 100.0% / 100.0% |
| wikisource:51fe7386 | 3 | 100.0% / 66.7% | 100.0% / 33.3% |
| wikisource:602cc72e | 1 | — / 0.0% | — / 0.0% |
| wikisource:69e993c1 | 0 | — / — | — / — |
| wikisource:6b47791c | 0 | — / — | — / — |
| wikisource:8fb8cb49 | 0 | — / — | — / — |
| wikisource:9c1dca9b | 2 | 100.0% / 100.0% | 100.0% / 100.0% |
| wikisource:c3e12e31 | 1 | — / 0.0% | — / 0.0% |

## Ascender false marks

| population | eligible unmarked slots | S2 false | S3 false |
|---|---:|---:|---:|
| all | 3461 | 122 (3.5%) | 6 (0.2%) |
| held-out | 2440 | 78 (3.2%) | 5 (0.2%) |

## Owner slots and missed-mark causes

Both old modules were recovered with `git show 153ff82e:...` and imported from a temporary `owner_v8` package outside greekocr. `owner_v8_slots.json` stores every old letter box; `owner_slot_expectations.jsonl` pins v8_x0/v8_x1 and maps by unique maximum overlap (ties/unavailable ranges abstain). The modules yield identical letter-component boxes to S2 on all 33 supplied crops: **zero actual renumberings**. The requested example cannot honestly be relabelled 8→9: old slot 8 is x=362–403, mapped to current slot 8, whose input base is β. The crop has a leading elision sign before β; that is an unresolved punctuation/expectation mismatch, not a fabricated vowel accent. A fixture with an inserted slot verifies renumbering by overlap.

S2 corrected accounting: 18/59; S3: 35/59. Qualitative blurry notes remain unresolved. Every expectation is shown below, and every owner card has the fixed count and both slot identities. No-note card remains 0/0.

| line | v8 slot [x0,x1) → current | expectation | S2 → S3 | physical cause / remaining limitation |
|---|---|---|---|---|
| 02a3a2a6-p000046-l0014 | 8 [362,403) → 8 | {"missed": 1} | not fixed → not fixed | non-vowel range; leading elision is not a vowel accent |
| 02a3a2a6-p000046-l0025 | 18 [753,768) → 18 | {"false": "punctuation_dot"} | fixed → fixed | false punctuation_dot rejected |
| 177b717d-p000013-l0009 | 1 [30,84) → 1 | {"missed": 2} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 177b717d-p000013-l0009 | 13 [461,511) → 13 | {"missed": 1} | not fixed → not fixed | non-vowel range; leading elision is not a vowel accent |
| 177b717d-p000097-l0007 | 19 [715,739) → 19 | {"false": "subscript_speck"} | fixed → fixed | false subscript_speck rejected |
| 177b717d-p000097-l0010 | 2 [68,111) → 2 | {"missed": 2} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 177b717d-p000097-l0010 | 5 [198,213) → 5 | {"missed": 1} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 2793d64c-p000048-l0004 | 19 [743,782) → 19 | {"missed": 1} | not fixed → not fixed | below-baseline size/position or connected wedge |
| 2793d64c-p000048-l0010 | 6 [183,211) → 6 | {"false": "subscript_speck"} | fixed → fixed | false subscript_speck rejected |
| 2793d64c-p000070-l0010 | 22 [809,838) → 22 | {"false": "ascender_delta"} | not fixed → fixed | false ascender_delta rejected |
| 2793d64c-p000070-l0014 | 10 [393,428) → 10 | {"false": "subscript_speck"} | fixed → fixed | false subscript_speck rejected |
| 2793d64c-p000070-l0014 | 13 [541,572) → 13 | {"false": "subscript_speck"} | fixed → fixed | false subscript_speck rejected |
| 2793d64c-p000070-l0014 | 12 [471,510) → 12 | {"false": "above_speck"} | not fixed → not fixed | false above_speck remains |
| 2793d64c-p000072-l0007 | 3 [98,131) → 3 | {"apostrophe": true} | fixed → fixed | elision window/word-final eligibility |
| 384c3f89-p000030-l0021 | 22 [715,742) → 22 | {"apostrophe": true} | fixed → fixed | elision window/word-final eligibility |
| 384c3f89-p000030-l0029 | 1 [39,81) → 1 | {"missed": 1} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 384c3f89-p000053-l0021 | 10 [335,369) → 10 | {"missed": 2} | fixed → fixed | classifier identity/compound support |
| 384c3f89-p000053-l0021 | 32 [1257,1275) → 32 | {"missed": 1} | fixed → fixed | classifier identity/compound support |
| 384c3f89-p000053-l0021 | 22 [844,872) → 22 | {"apostrophe": true} | fixed → fixed | elision window/word-final eligibility |
| 384c3f89-p000053-l0028 | 25 [907,935) → 25 | {"missed": 1} | fixed → fixed | classifier identity/compound support |
| 384c3f89-p000068-l0036 | 6 [201,228) → 6 | {"apostrophe": true} | not fixed → not fixed | elision window/word-final eligibility |
| 384c3f89-p000068-l0036 | 7 [293,338) → 7 | {"missed": 2} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 384c3f89-p000121-l0024 | 18 [639,669) → 18 | {"apostrophe": true} | fixed → fixed | elision window/word-final eligibility |
| 384c3f89-p000205-l0005 | 1 [33,86) → 1 | {"missed": 2} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 384c3f89-p000205-l0005 | 2 [115,146) → 2 | {"apostrophe": true} | not fixed → not fixed | elision window/word-final eligibility |
| 384c3f89-p000205-l0005 | 7 [360,387) → 7 | {"apostrophe": true} | fixed → fixed | elision window/word-final eligibility |
| 51fe7386-p000024-l0015 | 1 [33,79) → 1 | {"missed": 1} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0015 | 2 [157,201) → 2 | {"missed": 1} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0015 | 29 [1400,1442) → 29 | {"missed": 2} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0020 | 6 [192,216) → 6 | {"missed": 1} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0020 | 8 [288,311) → 8 | {"missed": 1} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0020 | 11 [363,386) → 11 | {"missed": 1} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0020 | 20 [718,747) → 20 | {"missed": 1} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0020 | 37 [1434,1455) → 37 | {"missed": 1} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0020 | 39 [1542,1573) → 39 | {"missed": 1} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 51fe7386-p000024-l0020 | 23 [847,883) → 23 | {"false": "letter_part_subscript"} | fixed → fixed | false letter_part_subscript rejected |
| 602cc72e-p000155-l0009 | 2 [66,99) → 2 | {"missed": 2} | not fixed → fixed | mean-line/x-height included joined mark; body band corrected |
| 602cc72e-p000155-l0009 | 11 [478,498) → 11 | {"missed": 1} | not fixed → fixed | mean-line/x-height included joined mark; body band corrected |
| 602cc72e-p000155-l0009 | 12 [532,556) → 12 | {"missed": 1} | not fixed → not fixed | mean-line/x-height included joined mark; body band corrected |
| 602cc72e-p000155-l0009 | 16 [681,711) → 16 | {"missed": 1} | not fixed → not fixed | mean-line/x-height included joined mark; body band corrected |
| 602cc72e-p000167-l0027 | 1 [21,69) → 1 | {"missed": 1} | not fixed → not fixed | mean-line/x-height included joined mark; body band corrected |
| 602cc72e-p000167-l0027 | 6 [252,285) → 6 | {"missed": 1} | not fixed → fixed | mean-line/x-height included joined mark; body band corrected |
| 602cc72e-p000167-l0027 | 10 [459,479) → 10 | {"missed": 1} | not fixed → fixed | mean-line/x-height included joined mark; body band corrected |
| 602cc72e-p000167-l0027 | 14 [662,692) → 14 | {"missed": 1} | not fixed → fixed | mean-line/x-height included joined mark; body band corrected |
| 8b6b0de9-p000004-l0028 | 2 [46,76) → 2 | {"missed": 1} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 8b6b0de9-p000004-l0028 | 7 [304,329) → 7 | {"missed": 2} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 8b6b0de9-p000007-l0030 | 13 [447,485) → 13 | {"false": "subscript_speck"} | fixed → fixed | false subscript_speck rejected |
| 8b6b0de9-p000008-l0001 | 12 [410,443) → 12 | {"missed": 2} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 8b6b0de9-p000008-l0001 | 13 [447,473) → 13 | {"false": "ascender_delta"} | not fixed → fixed | false ascender_delta rejected |
| 8b6b0de9-p000008-l0002 | 13 [561,576) → 13 | {"false": "punctuation_dot"} | fixed → fixed | false punctuation_dot rejected |
| 8b6b0de9-p000008-l0019 | 17 [583,616) → 17 | {"missed": 1} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 8b6b0de9-p000008-l0024 | 4 [114,137) → 4 | {"missed": 1} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 8b6b0de9-p000008-l0024 | 18 [627,654) → 18 | {"missed": 1} | not fixed → fixed | joined vowel mark rejected by S2 ascender neck rule |
| 8b6b0de9-p000011-l0007 | 9 [326,359) → 9 | {"false": "subscript_speck"} | fixed → fixed | false subscript_speck rejected |
| 8b6b0de9-p000011-l0014 | 13 [528,549) → 13 | {"missed": 1} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |
| 8b6b0de9-p000021-l0007 | 18 [699,722) → 18 | {"false": "faint_letter"} | fixed → fixed | false faint_letter rejected |
| 9c1dca9b-p000005-l0017 | 23 [549,571) → 23 | {"missed": 1} | not fixed → not fixed | qualitative blurry/merged note; no invented count |
| 9c1dca9b-p000005-l0017 | 27 [690,712) → 27 | {"missed": 1} | not fixed → not fixed | qualitative blurry/merged note; no invented count |
| 9c1dca9b-p000015-l0065 | 8 [189,204) → 8 | {"missed": 1} | not fixed → not fixed | joined vowel mark rejected by S2 ascender neck rule |

Owner whole-line metrics (all visible slots):

| line | S2 P/R/F1 | S3 P/R/F1 |
|---|---|---|
| 02a3a2a6-p000046-l0014 | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| 02a3a2a6-p000046-l0025 | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| 177b717d-p000013-l0009 | 75.0%/60.0%/66.7% | 75.0%/60.0%/66.7% |
| 177b717d-p000097-l0007 | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| 177b717d-p000097-l0010 | 100.0%/50.0%/66.7% | 100.0%/75.0%/85.7% |
| 2793d64c-p000048-l0004 | 100.0%/71.4%/83.3% | 100.0%/85.7%/92.3% |
| 2793d64c-p000048-l0010 | 100.0%/85.7%/92.3% | 100.0%/85.7%/92.3% |
| 2793d64c-p000070-l0010 | 66.7%/66.7%/66.7% | 83.3%/83.3%/83.3% |
| 2793d64c-p000070-l0014 | 83.3%/100.0%/90.9% | 83.3%/100.0%/90.9% |
| 2793d64c-p000072-l0007 | 66.7%/100.0%/80.0% | 100.0%/75.0%/85.7% |
| 384c3f89-p000030-l0021 | 88.9%/88.9%/88.9% | 88.9%/88.9%/88.9% |
| 384c3f89-p000030-l0029 | 100.0%/100.0%/100.0% | 83.3%/83.3%/83.3% |
| 384c3f89-p000053-l0021 | 88.9%/88.9%/88.9% | 88.9%/88.9%/88.9% |
| 384c3f89-p000053-l0028 | 87.5%/87.5%/87.5% | 87.5%/87.5%/87.5% |
| 384c3f89-p000068-l0036 | 100.0%/66.7%/80.0% | 100.0%/66.7%/80.0% |
| 384c3f89-p000091-l0039 | 85.7%/85.7%/85.7% | 85.7%/85.7%/85.7% |
| 384c3f89-p000121-l0024 | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| 384c3f89-p000205-l0005 | 100.0%/63.6%/77.8% | 71.4%/45.5%/55.6% |
| 51fe7386-p000024-l0015 | 40.0%/28.6%/33.3% | 75.0%/42.9%/54.5% |
| 51fe7386-p000024-l0020 | 50.0%/12.5%/20.0% | 62.5%/62.5%/62.5% |
| 602cc72e-p000155-l0009 | —/0.0%/0.0% | 50.0%/50.0%/50.0% |
| 602cc72e-p000167-l0027 | —/0.0%/0.0% | 100.0%/75.0%/85.7% |
| 8b6b0de9-p000004-l0028 | 100.0%/33.3%/50.0% | 100.0%/100.0%/100.0% |
| 8b6b0de9-p000007-l0030 | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| 8b6b0de9-p000008-l0001 | 80.0%/66.7%/72.7% | 100.0%/83.3%/90.9% |
| 8b6b0de9-p000008-l0002 | 66.7%/66.7%/66.7% | 100.0%/100.0%/100.0% |
| 8b6b0de9-p000008-l0019 | 0.0%/0.0%/0.0% | 50.0%/50.0%/50.0% |
| 8b6b0de9-p000008-l0024 | 100.0%/33.3%/50.0% | 100.0%/100.0%/100.0% |
| 8b6b0de9-p000011-l0007 | 100.0%/66.7%/80.0% | 100.0%/100.0%/100.0% |
| 8b6b0de9-p000011-l0014 | 100.0%/50.0%/66.7% | 50.0%/50.0%/50.0% |
| 8b6b0de9-p000021-l0007 | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| 9c1dca9b-p000005-l0017 | —/0.0%/0.0% | 33.3%/25.0%/28.6% |
| 9c1dca9b-p000015-l0065 | 100.0%/66.7%/80.0% | 66.7%/66.7%/66.7% |

The required owner-line recall target was not reached: S3 79.2% equals S1 79.2%, rather than exceeding it. Held-out precision also misses the S2 floor. This candidate is not qualified as an S2 replacement.

The actual 384c3f89-p000096-l0004 η window expands from [523,540) to [523,554), but its arch at [533,7,555,19) is already labelled `neighbour` by the unchanged glyph pass. The breathing blob is counted; the full compound is still not recovered, and its class has zero fitting samples. The synthetic union test proves the window contract only.

## Compound support

No recogniser passes or agreement harvesting were performed. Counts describe existing DEV fitting/calibration examples and known held-out component-slot truths, not independent newly labelled samples.

| compound class | fit | DEV calibration | held-out slots | exact recovered |
|---|---:|---:|---:|---:|
| dasia+acute | 32 | 2 | 102 | 61 |
| dasia+acute+subscript | 0 | 0 | 0 | 0 |
| dasia+circumflex | 1 | 0 | 18 | 0 |
| dasia+circumflex+subscript | 0 | 0 | 3 | 0 |
| dasia+grave | 0 | 0 | 7 | 0 |
| dasia+grave+subscript | 0 | 0 | 0 | 0 |
| psili+acute | 58 | 10 | 268 | 192 |
| psili+acute+subscript | 0 | 0 | 1 | 0 |
| psili+circumflex | 12 | 5 | 40 | 20 |
| psili+circumflex+subscript | 0 | 0 | 0 | 0 |
| psili+grave | 9 | 1 | 11 | 7 |
| psili+grave+subscript | 0 | 0 | 0 | 0 |

## S1 engine re-scored against print

The original S1 outputs are re-scored; the same S1 engine is also run with S2 and S3 extraction/classifiers. Both seeds reuse crops and are not independent image observations. Strict and ratio policies retain separate columns. Full rows/receipts are in S3_engine/.

| detector | policy | split | stage | column | decided | correct | wrong | unknown | print P | LB95 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| S1 original | strict | all | all | ACCEPT | 61 | 58 | 3 | 0 | 95.1% | 87.8% |
| S1 original | strict | all | all | HOLD | 87 | 59 | 17 | 11 | 77.6% | 68.4% |
| S1 original | strict | all | L2 | ACCEPT | 4 | 2 | 2 | 0 | 50.0% | 9.8% |
| S1 original | strict | all | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 original | strict | held-out | all | ACCEPT | 6 | 4 | 2 | 0 | 66.7% | 27.1% |
| S1 original | strict | held-out | all | HOLD | 62 | 43 | 13 | 6 | 76.8% | 65.6% |
| S1 original | strict | held-out | L2 | ACCEPT | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 original | strict | held-out | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 original | strict | DEV | all | ACCEPT | 55 | 54 | 1 | 0 | 98.2% | 91.7% |
| S1 original | strict | DEV | all | HOLD | 25 | 16 | 4 | 5 | 80.0% | 59.9% |
| S1 original | strict | DEV | L2 | ACCEPT | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S1 original | strict | DEV | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 original | ratio | all | all | ACCEPT | 59 | 56 | 3 | 0 | 94.9% | 87.4% |
| S1 original | ratio | all | all | HOLD | 116 | 61 | 41 | 14 | 59.8% | 51.2% |
| S1 original | ratio | all | L2 | ACCEPT | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 original | ratio | all | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 original | ratio | held-out | all | ACCEPT | 6 | 4 | 2 | 0 | 66.7% | 27.1% |
| S1 original | ratio | held-out | all | HOLD | 78 | 45 | 27 | 6 | 62.5% | 52.2% |
| S1 original | ratio | held-out | L2 | ACCEPT | 2 | 0 | 2 | 0 | 0.0% | 0.0% |
| S1 original | ratio | held-out | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 original | ratio | DEV | all | ACCEPT | 53 | 52 | 1 | 0 | 98.1% | 91.4% |
| S1 original | ratio | DEV | all | HOLD | 38 | 16 | 14 | 8 | 53.3% | 37.0% |
| S1 original | ratio | DEV | L2 | ACCEPT | 0 | 0 | 0 | 0 | — | 0.0% |
| S1 original | ratio | DEV | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | strict | all | all | ACCEPT | 58 | 56 | 2 | 0 | 96.6% | 89.5% |
| S2 | strict | all | all | HOLD | 90 | 61 | 16 | 13 | 79.2% | 70.2% |
| S2 | strict | all | L2 | ACCEPT | 7 | 6 | 1 | 0 | 85.7% | 47.9% |
| S2 | strict | all | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | strict | held-out | all | ACCEPT | 11 | 10 | 1 | 0 | 90.9% | 63.6% |
| S2 | strict | held-out | all | HOLD | 60 | 41 | 13 | 6 | 75.9% | 64.5% |
| S2 | strict | held-out | L2 | ACCEPT | 5 | 4 | 1 | 0 | 80.0% | 34.3% |
| S2 | strict | held-out | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | strict | DEV | all | ACCEPT | 47 | 46 | 1 | 0 | 97.9% | 90.3% |
| S2 | strict | DEV | all | HOLD | 30 | 20 | 3 | 7 | 87.0% | 69.6% |
| S2 | strict | DEV | L2 | ACCEPT | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S2 | strict | DEV | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | ratio | all | all | ACCEPT | 54 | 52 | 2 | 0 | 96.3% | 88.8% |
| S2 | ratio | all | all | HOLD | 119 | 63 | 40 | 16 | 61.2% | 52.6% |
| S2 | ratio | all | L2 | ACCEPT | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S2 | ratio | all | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | ratio | held-out | all | ACCEPT | 9 | 8 | 1 | 0 | 88.9% | 57.1% |
| S2 | ratio | held-out | all | HOLD | 76 | 43 | 27 | 6 | 61.4% | 50.9% |
| S2 | ratio | held-out | L2 | ACCEPT | 3 | 2 | 1 | 0 | 66.7% | 13.5% |
| S2 | ratio | held-out | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | ratio | DEV | all | ACCEPT | 45 | 44 | 1 | 0 | 97.8% | 89.9% |
| S2 | ratio | DEV | all | HOLD | 43 | 20 | 13 | 10 | 60.6% | 44.8% |
| S2 | ratio | DEV | L2 | ACCEPT | 0 | 0 | 0 | 0 | — | 0.0% |
| S2 | ratio | DEV | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S3 | strict | all | all | ACCEPT | 76 | 73 | 3 | 0 | 96.1% | 90.1% |
| S3 | strict | all | all | HOLD | 83 | 56 | 16 | 11 | 77.8% | 68.2% |
| S3 | strict | all | L2 | ACCEPT | 6 | 5 | 1 | 0 | 83.3% | 41.8% |
| S3 | strict | all | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S3 | strict | held-out | all | ACCEPT | 12 | 11 | 1 | 0 | 91.7% | 66.1% |
| S3 | strict | held-out | all | HOLD | 61 | 42 | 13 | 6 | 76.4% | 65.1% |
| S3 | strict | held-out | L2 | ACCEPT | 4 | 3 | 1 | 0 | 75.0% | 24.9% |
| S3 | strict | held-out | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S3 | strict | DEV | all | ACCEPT | 64 | 62 | 2 | 0 | 96.9% | 90.5% |
| S3 | strict | DEV | all | HOLD | 22 | 14 | 3 | 5 | 82.4% | 60.4% |
| S3 | strict | DEV | L2 | ACCEPT | 2 | 2 | 0 | 0 | 100.0% | 22.4% |
| S3 | strict | DEV | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S3 | ratio | all | all | ACCEPT | 74 | 71 | 3 | 0 | 95.9% | 89.9% |
| S3 | ratio | all | all | HOLD | 112 | 58 | 40 | 14 | 59.2% | 50.4% |
| S3 | ratio | all | L2 | ACCEPT | 4 | 3 | 1 | 0 | 75.0% | 24.9% |
| S3 | ratio | all | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S3 | ratio | held-out | all | ACCEPT | 12 | 11 | 1 | 0 | 91.7% | 66.1% |
| S3 | ratio | held-out | all | HOLD | 77 | 44 | 27 | 6 | 62.0% | 51.5% |
| S3 | ratio | held-out | L2 | ACCEPT | 4 | 3 | 1 | 0 | 75.0% | 24.9% |
| S3 | ratio | held-out | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |
| S3 | ratio | DEV | all | ACCEPT | 62 | 60 | 2 | 0 | 96.8% | 90.2% |
| S3 | ratio | DEV | all | HOLD | 35 | 14 | 13 | 8 | 51.9% | 34.7% |
| S3 | ratio | DEV | L2 | ACCEPT | 0 | 0 | 0 | 0 | — | 0.0% |
| S3 | ratio | DEV | L2 | HOLD | 0 | 0 | 0 | 0 | — | 0.0% |

## Sheet and validation

`sheets/owner_iter_S3.html` uses sheet_build.py; CSS and notes JavaScript are unchanged. Section 1: 33 owner lines. Section 2: fixed sample60 plus changed held-out lines, unique line IDs, capped at 140 non-owner cards. 336 held-out detections changed; 140 section-2 cards; 210 overflow IDs in S3_sheet_overflow.txt. Some fixed-sample lines may already appear in section 1, never twice.

New regression tests cover subscript stroke/speck/darkness/connected/cutoff, split-eta union and v8 overlap mapping. The existing capture test cannot bind a localhost socket in this sandbox, as in S2. Exact test results and artifact/notes-script checks are in S3_verification.json. Visual rendering is unverified: the default browser is absent and installed Chrome aborted in the sandbox. This environmental test remains unverified; no all-tests-green claim is made.

Regressions: held-out precision 92.0%→91.4%; accent precision 93.5%→91.8%; compound recall 66.2%→62.4%; compound f1 70.7%→68.8%; subscript precision 100.0%→97.7%; owner whole-line precision 87.8%→87.0%; wikisource:51fe7386 subscript recall 66.7%→33.3%; speck rejection 100.0%→98.9%; engine ACCEPT precision 96.6%→96.1%; engine HOLD precision 79.2%→77.8%.

S3 RESULT: held-out P 92.0%→91.4% R 83.3%→86.3%; subscript R 41.5%→44.7%; owner expectations fixed 35/59 (v8 mapping; S2 was 18/59); ascender false 3.5%→0.2%; S1 ACCEPT vs print p=96.1%; regressions: held-out precision 92.0%→91.4%; accent precision 93.5%→91.8%; compound recall 66.2%→62.4%; compound f1 70.7%→68.8%; subscript precision 100.0%→97.7%; owner whole-line precision 87.8%→87.0%; wikisource:51fe7386 subscript recall 66.7%→33.3%; speck rejection 100.0%→98.9%; engine ACCEPT precision 96.6%→96.1%; engine HOLD precision 79.2%→77.8%
