# SEG step 1 — 0.9-s1

Completed local native replay of 150 segeval1, 888 calibration and 250 frozen cell sample crops, for both 0.8 and 0.9-s1. No network, reader run, Git write, commit or deployed-package modification. The lead commits.

The single behavioral change replaces the old ≥2 detected bodies plus no horizontal-edge contact test with **every detected letter body ≥95% visible**. A group with no detected body remains cut-off; one detected body can now form a whole group. The 0.35-x-height groups and existing body predicate (role, width and ≥0.6-x-height band overlap) remain byte-for-byte in effect. Body visibility uses the existing text_lines mean/base geometric frame at the same component centre as body membership: `clip(min(base[x], crop_height) - max(mean[x], 0), 0, xheight) / xheight`. No rounding or epsilon enters the ≥0.95 comparison. Horizontal-edge contact remains diagnostic only.

Complete-row detection, >2-word allowance, second-complete-line veto, orientation/main-row handling, row-frame measurement, predictor, length 0.5–1.5 and padding 1.5 are unchanged. The JS policy is byte-identical to 0.8; native inventory supplies its changed word counts. Only segmentation version/fingerprint metadata changes.

## Native replay and scoring

The 150/888 inputs, contexts and owner scoring follow gate2/replay.py. Full stored reader answers are scored without a reader run; fine/faulty/unresolved labels are identical to gate2. Positive segmentation faults take precedence over unknown flags. `crop_overrun` alone is fine. FP = DROP/fine, FN = KEEP/faulty, UNC = every UNCERTAIN among all 150. The 888 uses only `owner_rating.decision` on 135 rated lines. Cells have no inherited owner-standard labels; only explicit marks are scored.

| 150 decision | 0.8 fine | 0.8 faulty | 0.8 unresolved | 0.9-s1 fine | 0.9-s1 faulty | 0.9-s1 unresolved |
| --- | --- | --- | --- | --- | --- | --- |
| DROP | 18 | 10 | 0 | 17 | 10 | 0 |
| KEEP | 97 | 14 | 0 | 98 | 14 | 0 |
| UNCERTAIN | 3 | 6 | 2 | 3 | 6 | 2 |

| Version | FP | FN | UNC |
| --- | --- | --- | --- |
| 0.8 | 18 | 14 | 11 |
| 0.9-s1 | 17 | 14 | 11 |

The saved 0.8 baseline is **18/14/11**, as the gate2 evidence and handoff show; the context pack’s FN=11 statement is not substituted for the saved full-population FN=14.

| 888 rated decision | 0.8 owner KEEP | 0.8 owner DROP | 0.9-s1 owner KEEP | 0.9-s1 owner DROP |
| --- | --- | --- | --- | --- |
| DROP | 22 | 44 | 21 | 44 |
| KEEP | 50 | 4 | 51 | 4 |
| UNCERTAIN | 6 | 9 | 6 | 9 |

888 rated agreement: **94 → 95/135**. The other 753 are unrated.

| Cohort | Rows | 0.8 → 0.9-s1 transitions |
| --- | --- | --- |
| segeval1 | 150 | {'KEEP->KEEP': 111, 'DROP->DROP': 27, 'DROP->KEEP': 1, 'UNCERTAIN->UNCERTAIN': 11} |
| calibration | 888 | {'KEEP->KEEP': 754, 'UNCERTAIN->UNCERTAIN': 41, 'DROP->KEEP': 7, 'DROP->DROP': 86} |
| cells | 250 | {'KEEP->KEEP': 184, 'UNCERTAIN->UNCERTAIN': 60, 'DROP->DROP': 6} |

## All explicit owner marks

The supplied local file contains **240 entries, 235 distinct IDs**: gate 62, cells 152 and deskew 26 entries. Five deskew IDs also occur in gate, leaving **21 additional deskew IDs**, matching the requested 62+152+21=235 distinct marks. All 235 IDs occur in the replay sets. Latest `updated` timestamp wins; file order breaks an exact timestamp tie. Agreement is counted once per distinct marked line, including UNCERTAIN as non-agreement. Two duplicate crop IDs across cohorts have identical verdicts and are counted once.

| Marked decision | 0.8 owner KEEP | 0.8 owner DROP | 0.9-s1 owner KEEP | 0.9-s1 owner DROP |
| --- | --- | --- | --- | --- |
| DROP | 26 | 14 | 25 | 14 |
| KEEP | 141 | 7 | 142 | 7 |
| UNCERTAIN | 34 | 13 | 34 | 13 |

Agreement: **155 → 156/235**. [Mark snapshot](owner_marks_snapshot.jsonl), [conflicts](mark_conflicts.json). There are no conflicting KEEP/DROP marks in the supplied file. Explicit marks are scored separately from historical owner-standard states and 888 ratings; they do not overwrite those reference labels.

Repeated marks (including every KEEP/DROP conflict):

| Line ID | Chronological marks | Winning mark | Conflict |
| --- | --- | --- | --- |
| 66112e132fd96ac8e30e5328-p000159-l0079 | 2026-10-19 11:15 DROP (deskew flips (27 lines)); 2026-10-19 13:50 DROP (gate (150 lines, 0.8)) | DROP | False |
| 847e1ec1-p000015-l0035 | 2026-10-19 11:15 DROP (deskew flips (27 lines)); 2026-10-19 13:50 DROP (gate (150 lines, 0.8)) | DROP | False |
| b8b6779da9a68fbed0ccdb5b-p000011-l0018 | 2026-10-19 11:16 KEEP (deskew flips (27 lines)); 2026-10-19 13:50 KEEP (gate (150 lines, 0.8)) | KEEP | False |
| gazette_modern--9701a3a500ecbd85--s000-l0139 | 2026-10-19 11:15 KEEP (deskew flips (27 lines)); 2026-10-19 14:49 KEEP (gate (150 lines, 0.8)) | KEEP | False |
| gazette_modern--e85649b67a7af9ab--s000-l0078 | 2026-10-19 11:15 DROP (deskew flips (27 lines)); 2026-10-19 13:49 DROP (gate (150 lines, 0.8)) | DROP | False |

## Gazette l0120 witness

Owner: “should have been dropped, more than 2 full words showing, the output length is correct”. Measured: **whole 0 → 0; DROP → DROP**, both on `length: Too much OCR output for the text box after height normalisation.`. The unchanged inventory detects **zero bodies in the above row** (votes 23.8, visible 0.236, coverage 0.958159); therefore no group can satisfy the new all-body test. This does **not** reproduce the owner’s whole-word assessment, and no detector or length repair is introduced in S1.

![Gazette native overlay](overlays/gazette_modern--80e8a42cbf8e629f--s000-l0120.png)

| Group | BBox | Component IDs | 0.8 body IDs | Per-body visible | 0.8 → 0.9-s1 |
| --- | --- | --- | --- | --- | --- |
| 0 | [6, 0, 62, 18] | [1, 2, 4, 5, 6] | [] | none: no detected body | cut-off → cut-off |
| 1 | [116, 1, 126, 13] | [38] | [] | none: no detected body | cut-off → cut-off |
| 2 | [183, 1, 193, 8] | [41, 48] | [] | none: no detected body | cut-off → cut-off |
| 3 | [255, 0, 269, 20] | [9] | [] | none: no detected body | cut-off → cut-off |
| 4 | [301, 0, 352, 20] | [10, 11, 12, 51, 13] | [] | none: no detected body | cut-off → cut-off |
| 5 | [370, 0, 471, 19] | [14, 15, 16, 17, 18, 19] | [] | none: no detected body | cut-off → cut-off |
| 6 | [492, 0, 521, 18] | [20, 21] | [] | none: no detected body | cut-off → cut-off |
| 7 | [551, 0, 636, 10] | [23, 24, 49, 26, 27, 28, 29, 30] | [] | none: no detected body | cut-off → cut-off |
| 8 | [648, 0, 704, 10] | [32, 33, 34, 35] | [] | none: no detected body | cut-off → cut-off |

Counts: 0.8 0 whole / 9 cut-off; 0.9-s1 0 whole / 9 cut-off. No complete neighbour row. Gate PASS in both versions. Length ratio `(characters+1)/(predicted+1)` = 1.64127101847905; box and padding evidence are exact to 0.8. This is the tool’s measured output, not an endorsement of that diagnosis.

For completeness, per-component body-frame visibility is recorded below as a diagnostic even where the unchanged body predicate rejects the component. These fractions do not create additional bodies or votes. Full per-body/per-component data and both versions are in [witnesses.json](witnesses.json).

### `gazette_modern--80e8a42cbf8e629f--s000-l0120` row inventory

Native crop 717×53; x-height 21.0; de-skew angle 0.11331880433656424°.

| Row | Side | Votes | Bodies | Visibility | Coverage | Complete | Component IDs | Body IDs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | main | 67.0 | 38 | 1.0 | 0.9735006973500697 | True | [54, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111] | [56, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96] |
| 1 | above | 23.8 | 0 | 0.236 | 0.9581589958158996 | False | [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 52, 53, 55] | [] |

Row 0 (main), assigned components and body-frame visibility:

| Component | Role | BBox | Area | Touches | Body | Frame visibility |
| --- | --- | --- | --- | --- | --- | --- |
| 54 | mark | [78, 10, 83, 20] | 25 | [] | False | 100.000000% |
| 56 | letter | [665, 17, 676, 39] | 107 | [] | True | 100.000000% |
| 57 | mark | [586, 18, 591, 27] | 24 | [] | False | 100.000000% |
| 58 | letter | [485, 20, 496, 41] | 92 | [] | True | 100.000000% |
| 59 | letter | [6, 21, 17, 42] | 85 | [] | True | 100.000000% |
| 60 | letter | [21, 21, 33, 42] | 94 | [] | True | 100.000000% |
| 61 | letter | [240, 21, 253, 43] | 102 | [] | True | 100.000000% |
| 62 | letter | [291, 21, 300, 50] | 66 | [] | True | 100.000000% |
| 63 | letter | [316, 21, 326, 42] | 87 | [] | True | 100.000000% |
| 64 | letter | [360, 21, 373, 42] | 127 | [] | True | 100.000000% |
| 65 | letter | [375, 21, 388, 42] | 127 | [] | True | 100.000000% |
| 66 | letter | [393, 21, 399, 47] | 73 | [] | True | 100.000000% |
| 67 | letter | [43, 22, 55, 43] | 99 | [] | True | 100.000000% |
| 68 | letter | [65, 22, 76, 43] | 76 | [] | True | 100.000000% |
| 69 | letter | [79, 22, 93, 44] | 111 | [] | True | 100.000000% |
| 70 | letter | [94, 22, 107, 43] | 114 | [] | True | 100.000000% |
| 71 | letter | [108, 22, 122, 44] | 125 | [] | True | 100.000000% |
| 72 | letter | [171, 22, 187, 43] | 135 | [] | True | 100.000000% |
| 73 | letter | [190, 22, 211, 44] | 172 | [] | True | 100.000000% |
| 74 | letter | [225, 22, 239, 44] | 125 | [] | True | 100.000000% |
| 75 | letter | [254, 22, 262, 50] | 54 | [] | True | 100.000000% |
| 76 | letter | [265, 22, 282, 43] | 110 | [] | True | 100.000000% |
| 77 | fragment | [284, 22, 289, 30] | 23 | [] | False | 100.000000% |
| 78 | letter | [302, 22, 313, 43] | 91 | [] | True | 100.000000% |
| 79 | letter | [337, 22, 351, 42] | 106 | [] | True | 100.000000% |
| 80 | letter | [149, 23, 169, 44] | 176 | [] | True | 100.000000% |
| 81 | letter | [140, 24, 147, 50] | 66 | [] | True | 100.000000% |
| 82 | letter | [608, 26, 621, 40] | 75 | [] | True | 100.000000% |
| 83 | letter | [622, 26, 633, 40] | 76 | [] | True | 100.000000% |
| 84 | letter | [650, 26, 664, 45] | 103 | [] | True | 100.000000% |
| 85 | letter | [677, 26, 688, 38] | 75 | [] | False | 100.000000% |
| 86 | letter | [690, 26, 702, 40] | 83 | [] | True | 100.000000% |
| 87 | letter | [703, 26, 714, 43] | 72 | [] | True | 100.000000% |
| 88 | letter | [537, 27, 549, 40] | 58 | [] | True | 100.000000% |
| 89 | letter | [552, 27, 565, 40] | 97 | [] | True | 100.000000% |
| 90 | letter | [566, 27, 579, 40] | 61 | [] | True | 100.000000% |
| 91 | letter | [580, 27, 593, 40] | 98 | [] | True | 100.000000% |
| 92 | letter | [431, 28, 445, 41] | 97 | [] | True | 100.000000% |
| 93 | letter | [447, 28, 453, 41] | 43 | [] | True | 100.000000% |
| 94 | letter | [469, 28, 484, 47] | 101 | [] | True | 100.000000% |
| 95 | letter | [498, 28, 521, 41] | 136 | [] | True | 100.000000% |
| 96 | letter | [416, 29, 429, 42] | 64 | [] | True | 100.000000% |
| 97 | fragment | [544, 35, 549, 40] | 16 | [] | False | 100.000000% |
| 98 | punct | [179, 36, 188, 43] | 26 | [] | False | 100.000000% |
| 99 | punct | [36, 38, 40, 42] | 14 | [] | False | 100.000000% |
| 100 | punct | [59, 38, 63, 43] | 14 | [] | False | 100.000000% |
| 101 | punct | [331, 38, 335, 42] | 14 | [] | False | 100.000000% |
| 102 | punct | [354, 38, 358, 42] | 14 | [] | False | 100.000000% |
| 103 | punct | [424, 38, 430, 42] | 18 | [] | False | 100.000000% |
| 104 | fragment | [677, 38, 681, 45] | 15 | [] | False | 100.000000% |
| 105 | punct | [640, 47, 658, 53] | 54 | ['bottom'] | False | 100.000000% |
| 106 | punct | [552, 48, 565, 53] | 41 | ['bottom'] | False | 100.000000% |
| 107 | mark | [591, 48, 596, 53] | 16 | ['bottom'] | False | 100.000000% |
| 108 | punct | [479, 49, 496, 53] | 42 | ['bottom'] | False | 100.000000% |
| 109 | neighbour | [407, 50, 411, 53] | 11 | ['bottom'] | False | 100.000000% |
| 110 | neighbour | [317, 51, 324, 53] | 11 | ['bottom'] | False | 100.000000% |
| 111 | neighbour | [106, 52, 109, 53] | 3 | ['bottom'] | False | 100.000000% |

Row 1 (above), assigned components and body-frame visibility:

| Component | Role | BBox | Area | Touches | Body | Frame visibility |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | neighbour | [6, 0, 19, 13] | 67 | ['top'] | False | 20.401884% |
| 2 | neighbour | [19, 0, 33, 13] | 88 | ['top'] | False | 20.533736% |
| 4 | neighbour | [34, 0, 46, 18] | 66 | ['top'] | False | 20.665589% |
| 5 | neighbour | [47, 0, 56, 13] | 58 | ['top'] | False | 20.769188% |
| 6 | neighbour | [59, 0, 62, 9] | 18 | ['top'] | False | 20.853950% |
| 7 | mark | [102, 0, 115, 14] | 85 | ['top'] | False | 21.306016% |
| 8 | mark | [171, 0, 182, 14] | 54 | ['top'] | False | 21.946443% |
| 9 | neighbour | [255, 0, 269, 20] | 93 | ['top'] | False | 22.756394% |
| 10 | neighbour | [301, 0, 315, 20] | 95 | ['top'] | False | 23.189624% |
| 11 | neighbour | [317, 0, 327, 12] | 60 | ['top'] | False | 23.321477% |
| 12 | neighbour | [330, 0, 334, 7] | 18 | ['top'] | False | 23.415657% |
| 13 | neighbour | [338, 0, 352, 13] | 97 | ['top'] | False | 23.538092% |
| 14 | neighbour | [370, 0, 383, 12] | 86 | ['top'] | False | 23.830051% |
| 15 | neighbour | [384, 0, 399, 12] | 88 | ['top'] | False | 23.971322% |
| 16 | neighbour | [400, 0, 411, 12] | 66 | ['top'] | False | 24.103174% |
| 17 | neighbour | [413, 0, 427, 19] | 110 | ['top'] | False | 24.244445% |
| 18 | neighbour | [429, 0, 443, 12] | 77 | ['top'] | False | 24.395134% |
| 19 | neighbour | [445, 0, 471, 18] | 164 | ['top'] | False | 24.602331% |
| 20 | neighbour | [492, 0, 506, 18] | 87 | ['top'] | False | 24.988470% |
| 21 | neighbour | [508, 0, 521, 11] | 81 | ['top'] | False | 25.129741% |
| 22 | punct | [522, 0, 532, 15] | 56 | ['top'] | False | 25.252176% |
| 23 | neighbour | [551, 0, 569, 10] | 81 | ['top'] | False | 25.562971% |
| 24 | neighbour | [560, 0, 564, 4] | 9 | ['top'] | False | 25.581807% |
| 26 | neighbour | [578, 0, 592, 10] | 51 | ['top'] | False | 25.798422% |
| 27 | neighbour | [594, 0, 602, 2] | 13 | ['top'] | False | 25.920856% |
| 28 | neighbour | [594, 0, 606, 10] | 40 | ['top'] | False | 25.939693% |
| 29 | neighbour | [607, 0, 621, 10] | 59 | ['top'] | False | 26.071545% |
| 30 | neighbour | [622, 0, 636, 10] | 67 | ['top'] | False | 26.212816% |
| 31 | punct | [636, 0, 641, 16] | 35 | ['top'] | False | 26.297578% |
| 32 | neighbour | [648, 0, 658, 10] | 51 | ['top'] | False | 26.438849% |
| 33 | neighbour | [661, 0, 674, 10] | 66 | ['top'] | False | 26.570701% |
| 34 | neighbour | [676, 0, 690, 9] | 66 | ['top'] | False | 26.721390% |
| 35 | neighbour | [692, 0, 704, 10] | 49 | ['top'] | False | 26.862661% |
| 36 | mark | [705, 0, 710, 16] | 37 | ['top'] | False | 26.947423% |
| 37 | mark | [66, 1, 76, 18] | 64 | [] | False | 20.957548% |
| 38 | neighbour | [116, 1, 126, 13] | 50 | [] | False | 21.428450% |
| 39 | punct | [127, 1, 141, 14] | 84 | [] | False | 21.550885% |
| 40 | mark | [156, 1, 169, 14] | 84 | [] | False | 21.814590% |
| 41 | neighbour | [183, 1, 193, 5] | 24 | [] | False | 22.059459% |
| 42 | mark | [203, 1, 215, 14] | 57 | [] | False | 22.257238% |
| 43 | mark | [216, 1, 229, 14] | 83 | [] | False | 22.379673% |
| 44 | mark | [232, 1, 237, 14] | 36 | [] | False | 22.492689% |
| 45 | mark | [288, 1, 299, 14] | 71 | [] | False | 23.048354% |
| 46 | mark | [141, 2, 153, 14] | 54 | [] | False | 21.673320% |
| 47 | mark | [195, 2, 201, 14] | 39 | [] | False | 22.153640% |
| 48 | neighbour | [186, 6, 190, 8] | 7 | [] | False | 22.059459% |
| 49 | neighbour | [572, 6, 576, 10] | 16 | [] | False | 25.694823% |
| 51 | neighbour | [330, 8, 336, 12] | 15 | [] | False | 23.425075% |
| 52 | punct | [59, 9, 64, 14] | 14 | [] | False | 20.863368% |
| 53 | mark | [183, 9, 193, 14] | 31 | [] | False | 22.059459% |
| 55 | mark | [150, 10, 155, 14] | 15 | [] | False | 21.720410% |

Detector vote provenance (unchanged text_lines accumulator; a component can cast several alternative hypotheses; only accepted votes are listed):

| Side | Shift px | Accepted weighted votes: component / x / shift / weight |
| --- | --- | --- |
| above | -24.68686188033899 | 1 / 113.0 / -25.26103716655617 / 1.0; 1 / 113.0 / -24.128769010264826 / 0.6; 2 / 428.0 / -26.841277190428883 / 1.0; 2 / 428.0 / -25.709009034137537 / 0.6; 3 / 583.0 / -22.51885561487419 / 0.6; 3 / 583.0 / -25.486587458582846 / 0.6; 4 / 239.0 / -24.89313317610526 / 1.0; 4 / 239.0 / -25.760865019813913 / 0.6; 5 / 227.0 / -23.8329335561482 / 1.0; 5 / 227.0 / -24.8329335561482 / 1.0; 6 / 531.0 / -22.35799059506028 / 1.0 |
| below | 24.717830154387045 | 38 / 118.0 / 25.71387965846172 / 1.0; 39 / 73.5 / 23.039628233300682 / 0.6; 39 / 73.5 / 25.93962823330068 / 1.0; 40 / 583.0 / 24.381144385125808 / 1.0; 42 / 433.0 / 22.23363963458901 / 0.6; 42 / 433.0 / 24.13363963458901 / 1.0; 44 / 654.0 / 23.124963300379896 / 0.6; 44 / 654.0 / 24.024963300379895 / 1.0; 45 / 229.5 / 23.157033173858956 / 1.0; 45 / 229.5 / 24.157033173858956 / 1.0; 46 / 301.0 / 22.79583545411662 / 1.0; 46 / 301.0 / 23.79583545411662 / 1.0; 47 / 555.0 / 26.621610165025608 / 0.6; 47 / 555.0 / 24.521610165025606 / 1.0; 48 / 23.0 / 25.190459983121748 / 1.0; 48 / 23.0 / 26.190459983121748 / 1.0; 49 / 329.0 / 23.65536967421683 / 1.0; 49 / 329.0 / 24.65536967421683 / 1.0; 50 / 402.5 / 23.28915531947807 / 1.0; 50 / 402.5 / 26.28915531947807 / 1.0; 51 / 48.5 / 26.065044108211218 / 1.0; 52 / 93.0 / 26.83929553337226 / 1.0; 52 / 93.0 / 25.83929553337226 / 1.0; 53 / 152.0 / 26.5433140685834 / 1.0; 54 / 715.5 / 23.718948565598197 / 1.0; 54 / 715.5 / 23.718948565598197 / 1.0; 55 / 618.5 / 26.205562160251063 / 1.0 |

## 129cff40 l0107 — inventory report only

Owner: “the accents of ἔχει were detected as a second line, complete error”. No witness-specific repair was made. The unchanged inventory returns **three rows total**, including **two complete neighbour rows**, above and below; the first complete neighbour is the above row. Both versions DROP for `gate: second complete line`. These are detector observations, not a claim that either neighbour is a real printed text line.

![129cff40 native overlay](overlays/129cff40-p000009-l0107.png)

### `129cff40-p000009-l0107` row inventory

Native crop 723×88; x-height 10.0; de-skew angle 0.2874296014575906°.

| Row | Side | Votes | Bodies | Visibility | Coverage | Complete | Component IDs | Body IDs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | main | 17.0 | 19 | 1.0 | 0.8395573997233748 | True | [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 33, 35, 36, 37] | [7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 26, 27, 28, 30] |
| 1 | above | 9.0 | 6 | 1.0 | 0.6514522821576764 | True | [1, 2, 3, 4, 5, 6] | [1, 2, 3, 4, 5, 6] |
| 2 | below | 25.4 | 9 | 1.0 | 0.9585062240663901 | True | [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59] | [38, 39, 47, 48, 49, 50, 51, 52, 54] |

Row 0 (main), assigned components and body-frame visibility:

| Component | Role | BBox | Area | Touches | Body | Frame visibility |
| --- | --- | --- | --- | --- | --- | --- |
| 7 | large | [527, 29, 544, 66] | 222 | [] | True | 100.000000% |
| 8 | letter | [4, 31, 33, 43] | 217 | [] | False | 100.000000% |
| 9 | letter | [63, 31, 75, 41] | 94 | [] | True | 100.000000% |
| 10 | letter | [107, 31, 123, 39] | 82 | [] | True | 100.000000% |
| 11 | letter | [293, 31, 311, 39] | 105 | [] | True | 100.000000% |
| 12 | letter | [420, 31, 440, 47] | 145 | [] | True | 100.000000% |
| 13 | letter | [642, 31, 661, 54] | 170 | [] | True | 100.000000% |
| 14 | letter | [43, 32, 51, 48] | 97 | [] | True | 100.000000% |
| 15 | letter | [220, 32, 238, 42] | 108 | [] | True | 100.000000% |
| 16 | letter | [248, 32, 261, 42] | 90 | [] | True | 100.000000% |
| 17 | letter | [265, 32, 282, 58] | 169 | [] | True | 100.000000% |
| 18 | large | [459, 32, 474, 66] | 166 | [] | True | 100.000000% |
| 19 | letter | [569, 32, 589, 51] | 160 | [] | True | 100.000000% |
| 20 | punct | [692, 32, 694, 36] | 6 | [] | False | 100.000000% |
| 21 | letter | [79, 33, 92, 47] | 121 | [] | True | 100.000000% |
| 22 | letter | [322, 33, 332, 49] | 112 | [] | True | 100.000000% |
| 23 | letter | [668, 33, 682, 44] | 90 | [] | True | 100.000000% |
| 24 | letter | [139, 34, 167, 48] | 241 | [] | False | 100.000000% |
| 25 | letter | [388, 34, 413, 44] | 190 | [] | False | 100.000000% |
| 26 | letter | [598, 34, 613, 43] | 110 | [] | True | 100.000000% |
| 27 | letter | [627, 34, 633, 40] | 22 | [] | True | 100.000000% |
| 28 | letter | [450, 35, 457, 44] | 41 | [] | True | 100.000000% |
| 29 | punct | [103, 37, 110, 48] | 49 | [] | False | 100.000000% |
| 30 | large | [682, 37, 698, 66] | 185 | [] | True | 100.000000% |
| 33 | punct | [616, 41, 629, 53] | 66 | [] | False | 100.000000% |
| 35 | punct | [445, 44, 449, 46] | 7 | [] | False | 100.000000% |
| 36 | neighbour | [221, 45, 236, 52] | 80 | [] | False | 100.000000% |
| 37 | punct | [293, 45, 307, 50] | 48 | [] | False | 100.000000% |

Row 1 (above), assigned components and body-frame visibility:

| Component | Role | BBox | Area | Touches | Body | Frame visibility |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | neighbour | [107, 6, 119, 24] | 109 | [] | True | 100.000000% |
| 2 | neighbour | [422, 6, 434, 24] | 111 | [] | True | 100.000000% |
| 3 | neighbour | [576, 6, 590, 25] | 143 | [] | True | 100.000000% |
| 4 | neighbour | [234, 7, 244, 23] | 84 | [] | True | 100.000000% |
| 5 | neighbour | [222, 8, 232, 17] | 71 | [] | True | 100.000000% |
| 6 | neighbour | [522, 11, 540, 22] | 116 | [] | True | 100.000000% |

Row 2 (below), assigned components and body-frame visibility:

| Component | Role | BBox | Area | Touches | Body | Frame visibility |
| --- | --- | --- | --- | --- | --- | --- |
| 38 | neighbour | [108, 48, 128, 67] | 166 | [] | True | 100.000000% |
| 39 | neighbour | [67, 49, 80, 67] | 149 | [] | True | 100.000000% |
| 40 | neighbour | [572, 49, 594, 68] | 184 | [] | False | 100.000000% |
| 41 | neighbour | [218, 50, 220, 52] | 3 | [] | False | 100.000000% |
| 42 | neighbour | [422, 50, 444, 67] | 146 | [] | False | 100.000000% |
| 43 | neighbour | [17, 51, 19, 53] | 4 | [] | False | 100.000000% |
| 44 | neighbour | [643, 52, 665, 68] | 182 | [] | False | 100.000000% |
| 45 | neighbour | [218, 55, 241, 66] | 185 | [] | False | 100.000000% |
| 46 | neighbour | [290, 55, 312, 66] | 142 | [] | False | 100.000000% |
| 47 | neighbour | [549, 55, 561, 68] | 92 | [] | True | 100.000000% |
| 48 | neighbour | [16, 56, 30, 67] | 94 | [] | True | 100.000000% |
| 49 | neighbour | [324, 56, 334, 67] | 84 | [] | True | 100.000000% |
| 50 | neighbour | [396, 56, 409, 69] | 119 | [] | True | 100.000000% |
| 51 | neighbour | [44, 58, 53, 67] | 74 | [] | True | 100.000000% |
| 52 | neighbour | [88, 58, 98, 67] | 69 | [] | True | 100.000000% |
| 53 | neighbour | [139, 58, 165, 69] | 190 | [] | False | 100.000000% |
| 54 | neighbour | [710, 58, 721, 68] | 88 | [] | True | 100.000000% |
| 55 | neighbour | [617, 60, 620, 63] | 7 | [] | False | 100.000000% |
| 56 | neighbour | [250, 64, 266, 84] | 136 | [] | False | 100.000000% |
| 57 | neighbour | [613, 69, 623, 85] | 123 | [] | False | 100.000000% |
| 58 | neighbour | [147, 71, 166, 81] | 124 | [] | False | 100.000000% |
| 59 | neighbour | [271, 75, 283, 85] | 90 | [] | False | 100.000000% |

Detector vote provenance (unchanged text_lines accumulator; a component can cast several alternative hypotheses; only accepted votes are listed):

| Side | Shift px | Accepted weighted votes: component / x / shift / weight |
| --- | --- | --- |
| above | -24.68686188033899 | 1 / 113.0 / -25.26103716655617 / 1.0; 1 / 113.0 / -24.128769010264826 / 0.6; 2 / 428.0 / -26.841277190428883 / 1.0; 2 / 428.0 / -25.709009034137537 / 0.6; 3 / 583.0 / -22.51885561487419 / 0.6; 3 / 583.0 / -25.486587458582846 / 0.6; 4 / 239.0 / -24.89313317610526 / 1.0; 4 / 239.0 / -25.760865019813913 / 0.6; 5 / 227.0 / -23.8329335561482 / 1.0; 5 / 227.0 / -24.8329335561482 / 1.0; 6 / 531.0 / -22.35799059506028 / 1.0 |
| below | 24.717830154387045 | 38 / 118.0 / 25.71387965846172 / 1.0; 39 / 73.5 / 23.039628233300682 / 0.6; 39 / 73.5 / 25.93962823330068 / 1.0; 40 / 583.0 / 24.381144385125808 / 1.0; 42 / 433.0 / 22.23363963458901 / 0.6; 42 / 433.0 / 24.13363963458901 / 1.0; 44 / 654.0 / 23.124963300379896 / 0.6; 44 / 654.0 / 24.024963300379895 / 1.0; 45 / 229.5 / 23.157033173858956 / 1.0; 45 / 229.5 / 24.157033173858956 / 1.0; 46 / 301.0 / 22.79583545411662 / 1.0; 46 / 301.0 / 23.79583545411662 / 1.0; 47 / 555.0 / 26.621610165025608 / 0.6; 47 / 555.0 / 24.521610165025606 / 1.0; 48 / 23.0 / 25.190459983121748 / 1.0; 48 / 23.0 / 26.190459983121748 / 1.0; 49 / 329.0 / 23.65536967421683 / 1.0; 49 / 329.0 / 24.65536967421683 / 1.0; 50 / 402.5 / 23.28915531947807 / 1.0; 50 / 402.5 / 26.28915531947807 / 1.0; 51 / 48.5 / 26.065044108211218 / 1.0; 52 / 93.0 / 26.83929553337226 / 1.0; 52 / 93.0 / 25.83929553337226 / 1.0; 53 / 152.0 / 26.5433140685834 / 1.0; 54 / 715.5 / 23.718948565598197 / 1.0; 54 / 715.5 / 23.718948565598197 / 1.0; 55 / 618.5 / 26.205562160251063 / 1.0 |

## Exhaustive verdict flips

**8 cohort records / 8 unique lines.** All changes are listed here and in [flips.jsonl](flips.jsonl). Blank label fields mean no saved label, rating or explicit mark.

| Set | Line ID | 0.8 → 0.9-s1 | Whole 0.8 → 0.9-s1 | Owner state | 888 rating | Latest mark | 0.8 reason | 0.9-s1 reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| segeval1 | lekythos--49c082ba27aa27da--s001-l0228 | DROP → KEEP | 3 → 0 | fine |  | KEEP | gate: too many whole neighbour words | length: OCR length matches; vertical padding is within the selected allowance. |
| calibration | kosmopolis--62ca52b56ebe780a--s005-l0023 | DROP → KEEP | 3 → 0 |  |  |  | gate: too many whole neighbour words | length: OCR length matches; vertical padding is within the selected allowance. |
| calibration | kosmopolis--62ca52b56ebe780a--s005-l0012 | DROP → KEEP | 3 → 1 |  |  |  | gate: too many whole neighbour words | length: OCR length matches; vertical padding is within the selected allowance. |
| calibration | lekythos--e9f314aab488b65f--s003-l0248 | DROP → KEEP | 6 → 0 |  |  |  | gate: too many whole neighbour words | length: OCR length matches; vertical padding is within the selected allowance. |
| calibration | lekythos--e9f314aab488b65f--s003-l0286 | DROP → KEEP | 8 → 0 |  |  |  | gate: too many whole neighbour words | length: OCR length matches; vertical padding is within the selected allowance. |
| calibration | elstat--24e6586813212fd1--s001-l0029 | DROP → KEEP | 3 → 0 |  |  |  | gate: too many whole neighbour words | length: OCR length matches; vertical padding is within the selected allowance. |
| calibration | kosmopolis--109d033afd51aea6--s006-l0010 | DROP → KEEP | 3 → 0 |  |  |  | gate: too many whole neighbour words | length: OCR length matches; vertical padding is within the selected allowance. |
| calibration | kosmopolis--654bf46f6d37c4b4--s004-l0034 | DROP → KEEP | 4 → 0 |  | KEEP |  | gate: too many whole neighbour words | length: OCR length matches; vertical padding is within the selected allowance. |

## Readback and source scope

| Check | Passed |
| --- | --- |
| saved_08_exact_excluding_orientation_seconds | 1038 |
| unchanged_inventory_except_word_status_and_visibility | 1288 |
| same_gate_box_padding_exact | 1267 |
| exact_gate_and_final_decision_readbacks | 2576 |
| exact_predictor_readbacks | 2279 |
| Unchanged final verdicts replayed exactly | 1280 |
| Tests | 158 |

Every gate and final verdict was recomputed from stored evidence for both versions; predictor results were independently re-run. Every unchanged final verdict replays exactly. Box/padding evidence equals 0.8 wherever the gate verdict is unchanged. Fresh native 0.8 matches all 1038 saved gate2 results and evidence, excluding only orientation elapsed `seconds`. Every other inventory field, body membership, component assignment, row curve and cut diagnostic is equal across versions. No Stage B measurements are fabricated for blocked gates.

Changed existing source files (exhaustive scope guard):

- `docs/harvest/line_pipeline/tool_versions.json`
- `greekocr/harvest/filtering_assets/crop-tools.py`
- `scripts/harvest/build_filter_versions.py`
- `tests/test_seg_gate.py`

Only `line_inventory` changes in crop-tools.py. All JS decision functions, NativeSegmenter, geometry, grouping/body definitions and predictor files remain unchanged. 25966 other initial files match their hashes, including 328 package files and the stray cp1_initial_hashes.json. [Scope guard](scope_guard.json), [initial hashes](initial_hashes.json), [input hashes](input_hashes.json), [crop bindings](crop_bindings.jsonl), [native replay](replay.jsonl), [readback summary](summary.json), [receipt](receipt.json). Generated tool metadata updates segmentation only and preserves its canonical sol-recut component namespace. The isolated segmentation definition rebuilds exactly; the unrelated full versions builder cannot run in this checkout because pre-existing untracked Clariden deployment sources are absent.

Tests used the existing sibling `.venv` with this checkout first on PYTHONPATH. The historical `test_line_pipeline.py` is absent here, so its existing sibling copy was executed read-only against this checkout, alongside this checkout’s deskew and gate tests. Offline fixtures block network; bytecode and pytest cache writes were disabled. `tests.log`: **158 passed**. The native replay blocks socket access with a Python audit hook. No OCR reader or page fetch ran. A test-only exact-float assertion was corrected to `pytest.approx`; the production ≥0.95 predicate has no tolerance.

Reproduce from this worktree (using the existing sol-recut `.venv/bin/python`): `python -B docs/records/harvest/seg_steps/s1/replay.py`, then `python -B docs/records/harvest/seg_steps/s1/validate_report.py`. These write only S1 artifacts and rerun local native segmentation. Do not rerun prepare.py: initial hashes are the before-change receipt.

SEG S1 READY: gazette l0120 whole 0.8 0 → 0 (DROP); 129cff40 second row = above votes 9 bodies 6 visibility 1.0 coverage 0.651452 complete (below also complete); 150 FP/FN/UNC 0.8 18/14/11 → 17/14/11; 888 rated agree 94 → 95/135; owner marks agree 155 → 156/235; flips 8; tests 158 passed
