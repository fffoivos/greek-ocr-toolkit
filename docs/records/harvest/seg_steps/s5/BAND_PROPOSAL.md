# SEG step 5 — length-band proposal from the owner marks (0.9-s4 measurement)

**Proposal only. Not an adoption.** No tool, rule, test or existing file changed. The only free parameters are the lower bound L and the upper bound U of rule 2, fitted separately for all lines ("overall") and for numeric lines. Non-numeric, small, non-small and mixed are diagnostics.

Rule 2 as in `segmentation-policy.js::boxLengthJudgement`: r = (Google chars + 1) / (predicted chars + 1); KEEP iff L ≤ r ≤ U. "End to end" adds rule 3 (padding ≤ 1.5, unchanged); every population line already passed rule 1. **fd** = false drops (owner KEEP, tool does not keep). **fk** = false keeps (owner DROP, tool keeps). The objective is fd + fk, equally weighted. Owner KEEP outnumbers owner DROP 434 : 66 in the population, so an equal-weight total favours keeping; every table shows fd and fk separately so another weighting can be read off.

## Summary

| Item | Value |
| --- | --- |
| Population (excluded) | 500 (33: gate DROP 28, gate UNCERTAIN 5, no box 0) |
| Owner DROPs length cannot see (outside the objective) | 10 |
| Overall, current 0.50–1.50, end to end fd/fk | 59/16 |
| Overall, proposed 0.30–2.00, end to end fd/fk | 10/24 |
| Numeric, current, end to end fd/fk | 15/3 |
| Numeric, proposed 0.35–2.00, end to end fd/fk | 2/3 (the overall proposal gives the same verdicts on all numeric lines) |
| Held-out errors saved, split half (both ways) | [20, 18] |
| Held-out errors saved, leave-one-set-out (source sets, then cohorts) | [9, 8, 2, 8, 12, 13, 8, 10, 8] |
| Bootstrap optimal L, 2.5–97.5 % (0.30 is the grid floor) | 0.30–0.35 |
| Bootstrap optimal U, 2.5–97.5 % | 1.75–2.45 |
| Bootstrap resamples where proposed saves ≤ 0 errors vs current | 0/1000 (numeric 0/1000) |
| Lines separating the proposal from its grid neighbours | L 0.30 vs 0.35: 3; U 2.00 vs 1.95: 1; U 2.00 vs 2.05: 1 |
| Changed lines (overall scheme; numeric-scheme changes are a subset) | 59 |
| Class-balanced cost (diagnostic, not proposed) | optimum 0.55–1.30 fd/fk 84/11 |

Reading of the table: moving both bounds outward reduces owner-KEEP false drops by 49 and adds 8 owner-DROP false keeps on these judged lines; the overall gain holds on every held-out split (numeric held-out gains are 0–6 lines). The exact point is not pinned down: 0.30 vs 0.35 and 2.00 vs its neighbours each rest on 1–3 lines, and the bootstrap U spans 1.75–2.45. With equal costs the optimum widens the band; with class-balanced costs it narrows it (section 3).

## 1. Population and exclusions

Owner judgements: (a) owner_marks_20261019 (240 entries / 235 IDs), (b) the 135 explicit 888 ratings, (c) 185 typology marks. Joined exactly as `s4/validate_report.py`: explicit marks beat ratings; among explicit marks the latest `updated` wins (Athens-local strings → UTC, `Z` strings as UTC), then list order. Result: **533 judged IDs**. Row data come from `s4/replay.jsonl` (1,288 rows), then `s4/typology_replay.jsonl` for IDs not in the main replay; typology controls carry no marks.

| Set | n |
| --- | --- |
| Judged IDs | 533 |
| Excluded: gate DROP | 28 |
| Excluded: gate UNCERTAIN | 5 |
| Excluded: gate PASS but no usable box/prediction | 0 |
| **Band population** | 500 |
| … of which owner DROPs that length cannot see (not in the objective) | 10 |
| Objective population | 490 |

Readback: on every population line, the current 0.5–1.5 band plus padding 1.5 reproduces the saved 0.9-s4 verdict.

| Population breakdown | Counts |
| --- | --- |
| Owner mark | {'DROP': 66, 'KEEP': 434} |
| Judgement source (source set) | {'888 ratings': 96, 'cells (census samples, 0.5)': 152, 'deskew flips (27 lines)': 16, 'gate (150 lines, 0.8)': 55, 'typology marks': 181} |
| Line cohort | {'calibration': 118, 'cells': 152, 'segeval1': 65, 'typology': 165} |
| Output type | {'mixed': 4, 'non-numeric': 325, 'numeric': 171} |
| Small (chars ≤ 8 and A ≤ 6) | {'false': 201, 'true': 299} |
| Padding (rule 3) state | {'KEEP': 493, 'DROP': 7} |

### Excluded owner-judged lines (not the band's job)

| ID | Cohort | Exclusion | Owner | Owner note | S4 reason |
| --- | --- | --- | --- | --- | --- |
| bsb_poly1850--2032df1e3e983f1d--s005-l0009 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| bsb_poly1850--3496ab66cde251ee--s005-l0112 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| elstat--0a2c92120843658d--s001-l0147 | segeval1 | gate DROP | DROP |  | gate: too many whole neighbour words |
| elstat--d3b9d73bb0fbd59e--s000-l0162 | calibration | gate DROP | DROP |  | gate: second complete line |
| gazette_modern--37ed2e85ffdd5592--s000-l0067 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| gazette_modern--5158b7bf9def2bab--s000-l0068 | calibration | gate DROP | DROP |  | gate: second complete line |
| gazette_modern--57e4032e7fd9fa48--s000-l0039 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| gazette_modern--5d57a0a85aede133--s000-l0015 | calibration | gate DROP | DROP |  | gate: second complete line |
| gazette_modern--67dfc161a690ff25--s000-l0038 | calibration | gate DROP | DROP |  | gate: second complete line |
| gazette_modern--91dc31daecf45e05--s000-l0090 | calibration | gate DROP | DROP |  | gate: second complete line |
| gazette_modern--9a06f5aaa5be314f--s000-l0379 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| gazette_modern--a895f3d785bb13b6--s000-l0150 | calibration | gate DROP | DROP |  | gate: second complete line |
| gazette_modern--ad190c653ed8f486--s000-l0079 | calibration | gate DROP | DROP |  | gate: second complete line |
| gazette_modern--dc95e9d95cc9cb8e--s000-l0107 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| gazette_modern--e1ffcad236d8706c--s000-l0266 | segeval1 | gate DROP | DROP |  | gate: too many whole neighbour words |
| gazette_modern--f0442a79e7e8d415--s000-l0096 | calibration | gate DROP | DROP |  | gate: second complete line |
| ia_poly1850--3cbcc415675468a9--s034-l0001 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| ia_poly1850--df8f2267db2b7275--s039-l0034 | segeval1 | gate DROP | DROP |  | gate: second complete line |
| ia_poly1850--df8f2267db2b7275--s039-l0041 | calibration | gate DROP | DROP |  | gate: second complete line |
| kosmopolis--9a17c86798d2c74a--s007-l0035 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| lekythos--36e76126a4edbc72--s001-l0006 | calibration | gate DROP | DROP |  | gate: second complete line |
| lekythos--3bfc4a385d61b883--s002-l0012 | calibration | gate DROP | DROP |  | gate: second complete line |
| lekythos--49c082ba27aa27da--s000-l0241 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| lekythos--7f67b784930deef5--s004-l0003 | calibration | gate DROP | DROP |  | gate: second complete line |
| lekythos--7f67b784930deef5--s004-l0020 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| lekythos--dcfa99599048d352--s000-l0070 | calibration | gate DROP | DROP |  | gate: too many whole neighbour words |
| 129cff40-p000009-l0107 | segeval1 | gate DROP | KEEP | accents of ἔχει are detected as second line; complete error | gate: second complete line |
| ia_russian--61f76a57b26f9b13--s001-l0001 | calibration | gate DROP | KEEP |  | gate: second complete line |
| ia_greek_latin--f40a7578d8cd5825--s002-l0112 | calibration | gate UNCERTAIN | DROP |  | gate: no main row found |
| bsb_poly1850--2032df1e3e983f1d--s005-l0217 | calibration | gate UNCERTAIN | KEEP |  | gate: no main row found |
| gazette_modern--104e152774c2805f--s000-l0002 | typology | gate UNCERTAIN | KEEP |  | gate: no main row found |
| gazette_modern--bf43bbfea6d6754d--s000-l0194 | typology | gate UNCERTAIN | KEEP |  | gate: no main row found |
| gazette_modern--ce928a6f37dc6b04--s000-l0065 | typology | gate UNCERTAIN | KEEP |  | gate: no main row found |

Excluded by mark: {'gate DROP / owner DROP': 26, 'gate DROP / owner KEEP': 2, 'gate UNCERTAIN / owner DROP': 1, 'gate UNCERTAIN / owner KEEP': 4}.

### Owner DROPs that length cannot see

Selected on the literal owner note only: the note says the Google output is wrong ("wrong output", "actual output is …", "wrong reading", "bad output") or that the length is correct ("length is correct", "correct char count", "evenly matched per chars"). They are counted in a separate "length-blind kept" column and never enter the objective. Typology DROPs with Sol `final_text=wrong` but no owner note (HARIAZ, IIIXX, БАЦИМА) are **not** in this set; they stay in the objective.

| ID | Text | r | Category | Owner note | Current |
| --- | --- | --- | --- | --- | --- |
| bsb_poly1850--3496ab66cde251ee--s001-l0099 | NOTE. | 0.639 | label fault (owner note: output wrong) | wrong output | KEEP |
| bsb_poly1850--d7db5a3b1eb289a3--s006-l0029 | νὴ τοὺς δ. | 0.923 | label fault (owner note: output wrong) | actual output is "νὴ τοὺς s." | KEEP |
| bsb_poly1850--e2115ba0deaf6a07--s004-l0033 | διαλύεται τὸ πλεῖστον ταχέως καὶ κενοῦται μετὰ τῶν οὔρων.ύξό (and | 1.200 | owner note: length correct | 2 faint words are detect from the back ... but the length of output is correct ... shouldn't be training data though. | KEEP |
| gazette_modern--7c70c29daed80864--s000-l0006 | Η Άντρια | 0.826 | label fault (owner note: output wrong) | wrong output | KEEP |
| gazette_modern--80e8a42cbf8e629f--s000-l0120 | 13.3.1986 (ΦΕΚ 93/Γ΄/11.4.86) και μόνο κατά το μέρος | 1.641 | owner note: length correct | green box is a little high (seems to be dragged under the top line  should have been dropped because there are more than 2 or more full words showing. the output length is correct | DROP (too much) |
| gazette_modern--b00f99fd4af2363c--s000-l0008 | 7571 | 1.159 | label fault (owner note: output wrong) | wrong output correct char count | KEEP |
| gazette_modern--c6501fb163489dad--s000-l0028 | 4.267.49% | 1.013 | label fault (owner note: output wrong) | reasonable output, wrong reading | KEEP |
| ia_poly1850--26e14cb9c90b750f--s000-l0041 | ch'uh văn. | 0.726 | label fault (owner note: output wrong) | wrong output | KEEP |
| lekythos--456def1ccfc2283e--s001-l0177 | -'-'-'-'-'-'-'0 | 0.465 | label fault (owner note: output wrong) | bad output, although evenly matched per chars | DROP (too little) |
| serbia--3ab59a8d4ee49339--s005-l0014 | INCAII. | 0.552 | label fault (owner note: output wrong) | bad output, although evenly matched per chars | KEEP |

### Owner judgement conflicts

| ID | Chosen | All judgements |
| --- | --- | --- |
| bsb_poly1850--027215cc6d2a7e8a--s009-l0001 | KEEP (small_segments (417, Q3 typology), 2026-10-19 18:21) | DROP (888 rating, 2026-10-18T16:36:33.815Z); KEEP (small_segments (417, Q3 typology), 2026-10-19 18:21) |
| gazette_modern--279b47524ddd0a32--s000-l0069 | DROP (deskew flips (27 lines), 2026-10-19 11:17) | KEEP (888 rating, 2026-10-18T16:28:53.727Z); DROP (deskew flips (27 lines), 2026-10-19 11:17) |
| serbia--3ab59a8d4ee49339--s005-l0014 | DROP (deskew flips (27 lines), 2026-10-19 11:19) | KEEP (888 rating, 2026-10-18T16:35:27.816Z); DROP (deskew flips (27 lines), 2026-10-19 11:19) |
| serbia--90015698e9ce2250--s006-l0001 | DROP (small_segments (417, Q3 typology), 2026-10-19 18:22) | KEEP (888 rating, 2026-10-18T16:35:28.896Z); DROP (small_segments (417, Q3 typology), 2026-10-19 18:22) |

## 2. Sweep

Grid: L = 0.3…0.8 step 0.05; U = 1.2…2.5 step 0.05 (inclusive). Cells read fd/fk (total; length-blind kept). Full grids for every group and both modes are in [sweep.json](sweep.json).

### overall (n = 500, objective n = 490, owner {'KEEP': 434, 'DROP': 66})

| Band | Length alone fd/fk | End to end fd/fk |
| --- | --- | --- |
| current 0.50–1.50 | 57/18 (total 75; length-blind kept 8/10) | 59/16 (total 75; length-blind kept 8/10) |
| joint optimum (tie rule) 0.30–2.00 | 8/28 (total 36; length-blind kept 10/10) | 10/24 (total 34; length-blind kept 10/10) |

Joint minimum end-to-end total 34; every tie (L–U fd/fk): 0.30–2.00 10/24.

Length alone: joint minimum total 36; ties: 0.30–2.00 8/28.

Lower bound alone (U = 1.50):

| L | Length alone fd/fk (total) | End to end fd/fk (total) | Length-blind kept |
| --- | --- | --- | --- |
| 0.30 | 26/25 (51) | 28/21 (49) | 9 |
| 0.35 | 28/24 (52) | 30/20 (50) | 9 |
| 0.40 | 36/22 (58) | 38/19 (57) | 9 |
| 0.45 | 47/20 (67) | 49/17 (66) | 9 |
| 0.50 | 57/18 (75) | 59/16 (75) | 8 |
| 0.55 | 61/16 (77) | 63/15 (78) | 8 |
| 0.60 | 75/15 (90) | 77/14 (91) | 7 |
| 0.65 | 90/14 (104) | 92/13 (105) | 6 |
| 0.70 | 102/14 (116) | 104/13 (117) | 6 |
| 0.75 | 131/12 (143) | 132/11 (143) | 5 |
| 0.80 | 162/11 (173) | 163/10 (173) | 5 |

Upper bound alone (L = 0.50):

| U | Length alone fd/fk (total) | End to end fd/fk (total) | Length-blind kept |
| --- | --- | --- | --- |
| 1.20 | 97/13 (110) | 99/11 (110) | 7 |
| 1.25 | 86/13 (99) | 88/11 (99) | 8 |
| 1.30 | 78/14 (92) | 80/12 (92) | 8 |
| 1.35 | 71/15 (86) | 73/13 (86) | 8 |
| 1.40 | 68/16 (84) | 70/14 (84) | 8 |
| 1.45 | 63/17 (80) | 65/15 (80) | 8 |
| 1.50 | 57/18 (75) | 59/16 (75) | 8 |
| 1.55 | 51/20 (71) | 53/18 (71) | 8 |
| 1.60 | 51/20 (71) | 53/18 (71) | 8 |
| 1.65 | 49/20 (69) | 51/18 (69) | 9 |
| 1.70 | 47/20 (67) | 49/18 (67) | 9 |
| 1.75 | 44/20 (64) | 46/18 (64) | 9 |
| 1.80 | 43/20 (63) | 45/18 (63) | 9 |
| 1.85 | 42/20 (62) | 44/18 (62) | 9 |
| 1.90 | 42/20 (62) | 44/18 (62) | 9 |
| 1.95 | 40/21 (61) | 42/19 (61) | 9 |
| 2.00 | 39/21 (60) | 41/19 (60) | 9 |
| 2.05 | 39/22 (61) | 41/20 (61) | 9 |
| 2.10 | 39/22 (61) | 41/20 (61) | 9 |
| 2.15 | 39/23 (62) | 41/21 (62) | 9 |
| 2.20 | 38/23 (61) | 40/21 (61) | 9 |
| 2.25 | 38/23 (61) | 40/21 (61) | 9 |
| 2.30 | 38/24 (62) | 40/22 (62) | 9 |
| 2.35 | 38/24 (62) | 40/22 (62) | 9 |
| 2.40 | 38/25 (63) | 40/23 (63) | 9 |
| 2.45 | 37/25 (62) | 39/23 (62) | 9 |
| 2.50 | 37/26 (63) | 39/24 (63) | 9 |

### numeric (n = 171, objective n = 168, owner {'KEEP': 163, 'DROP': 8})

| Band | Length alone fd/fk | End to end fd/fk |
| --- | --- | --- |
| current 0.50–1.50 | 15/3 (total 18; length-blind kept 2/3) | 15/3 (total 18; length-blind kept 2/3) |
| joint optimum (tie rule) 0.35–2.00 | 2/4 (total 6; length-blind kept 3/3) | 2/3 (total 5; length-blind kept 3/3) |

Joint minimum end-to-end total 5; every tie (L–U fd/fk): 0.30–2.00 2/3, 0.30–2.45 1/4, 0.30–2.50 1/4, 0.35–2.00 2/3, 0.35–2.45 1/4, 0.35–2.50 1/4.

Length alone: joint minimum total 6; ties: 0.30–2.00 2/4, 0.30–2.45 1/5, 0.30–2.50 1/5, 0.35–2.00 2/4, 0.35–2.45 1/5, 0.35–2.50 1/5.

Lower bound alone (U = 1.50):

| L | Length alone fd/fk (total) | End to end fd/fk (total) | Length-blind kept |
| --- | --- | --- | --- |
| 0.30 | 10/4 (14) | 10/3 (13) | 3 |
| 0.35 | 10/4 (14) | 10/3 (13) | 3 |
| 0.40 | 12/3 (15) | 12/3 (15) | 3 |
| 0.45 | 14/3 (17) | 14/3 (17) | 3 |
| 0.50 | 15/3 (18) | 15/3 (18) | 2 |
| 0.55 | 15/3 (18) | 15/3 (18) | 2 |
| 0.60 | 17/3 (20) | 17/3 (20) | 2 |
| 0.65 | 20/3 (23) | 20/3 (23) | 2 |
| 0.70 | 23/3 (26) | 23/3 (26) | 2 |
| 0.75 | 29/3 (32) | 29/3 (32) | 2 |
| 0.80 | 47/3 (50) | 47/3 (50) | 2 |

Upper bound alone (L = 0.50):

| U | Length alone fd/fk (total) | End to end fd/fk (total) | Length-blind kept |
| --- | --- | --- | --- |
| 1.20 | 29/2 (31) | 29/2 (31) | 2 |
| 1.25 | 26/2 (28) | 26/2 (28) | 2 |
| 1.30 | 22/3 (25) | 22/3 (25) | 2 |
| 1.35 | 21/3 (24) | 21/3 (24) | 2 |
| 1.40 | 20/3 (23) | 20/3 (23) | 2 |
| 1.45 | 17/3 (20) | 17/3 (20) | 2 |
| 1.50 | 15/3 (18) | 15/3 (18) | 2 |
| 1.55 | 12/3 (15) | 12/3 (15) | 2 |
| 1.60 | 12/3 (15) | 12/3 (15) | 2 |
| 1.65 | 12/3 (15) | 12/3 (15) | 2 |
| 1.70 | 10/3 (13) | 10/3 (13) | 2 |
| 1.75 | 9/3 (12) | 9/3 (12) | 2 |
| 1.80 | 8/3 (11) | 8/3 (11) | 2 |
| 1.85 | 8/3 (11) | 8/3 (11) | 2 |
| 1.90 | 8/3 (11) | 8/3 (11) | 2 |
| 1.95 | 8/3 (11) | 8/3 (11) | 2 |
| 2.00 | 7/3 (10) | 7/3 (10) | 2 |
| 2.05 | 7/4 (11) | 7/4 (11) | 2 |
| 2.10 | 7/4 (11) | 7/4 (11) | 2 |
| 2.15 | 7/4 (11) | 7/4 (11) | 2 |
| 2.20 | 7/4 (11) | 7/4 (11) | 2 |
| 2.25 | 7/4 (11) | 7/4 (11) | 2 |
| 2.30 | 7/4 (11) | 7/4 (11) | 2 |
| 2.35 | 7/4 (11) | 7/4 (11) | 2 |
| 2.40 | 7/4 (11) | 7/4 (11) | 2 |
| 2.45 | 6/4 (10) | 6/4 (10) | 2 |
| 2.50 | 6/4 (10) | 6/4 (10) | 2 |

### non-numeric (n = 325, objective n = 318, owner {'KEEP': 267, 'DROP': 58}) — diagnostic

| Band | Length alone fd/fk | End to end fd/fk |
| --- | --- | --- |
| current 0.50–1.50 | 42/15 (total 57; length-blind kept 6/7) | 44/13 (total 57; length-blind kept 6/7) |
| joint optimum (tie rule) 0.30–1.95 | 6/24 (total 30; length-blind kept 7/7) | 8/21 (total 29; length-blind kept 7/7) |

Joint minimum end-to-end total 29; every tie (L–U fd/fk): 0.30–1.95 8/21, 0.30–2.00 8/21, 0.30–2.05 8/21, 0.30–2.10 8/21, 0.30–2.20 7/22, 0.30–2.25 7/22.

Length alone: joint minimum total 30; ties: 0.30–1.95 6/24, 0.30–2.00 6/24, 0.30–2.05 6/24, 0.30–2.10 6/24, 0.30–2.20 5/25, 0.30–2.25 5/25.

### small (n = 299, objective n = 295, owner {'KEEP': 279, 'DROP': 20}) — diagnostic

| Band | Length alone fd/fk | End to end fd/fk |
| --- | --- | --- |
| current 0.50–1.50 | 24/9 (total 33; length-blind kept 4/4) | 24/9 (total 33; length-blind kept 4/4) |
| joint optimum (tie rule) 0.35–2.00 | 1/13 (total 14; length-blind kept 4/4) | 1/12 (total 13; length-blind kept 4/4) |

Joint minimum end-to-end total 13; every tie (L–U fd/fk): 0.30–2.00 1/12, 0.30–2.45 0/13, 0.35–2.00 1/12, 0.35–2.45 0/13.

Length alone: joint minimum total 14; ties: 0.30–2.00 1/13, 0.30–2.45 0/14, 0.35–2.00 1/13, 0.35–2.45 0/14, 0.40–2.00 2/12, 0.40–2.45 1/13.

### non-small (n = 201, objective n = 195, owner {'KEEP': 155, 'DROP': 46}) — diagnostic

| Band | Length alone fd/fk | End to end fd/fk |
| --- | --- | --- |
| current 0.50–1.50 | 33/9 (total 42; length-blind kept 4/6) | 35/7 (total 42; length-blind kept 4/6) |
| joint optimum (tie rule) 0.30–1.95 | 7/15 (total 22; length-blind kept 6/6) | 9/12 (total 21; length-blind kept 6/6) |

Joint minimum end-to-end total 21; every tie (L–U fd/fk): 0.30–1.95 9/12, 0.30–2.00 9/12, 0.30–2.05 9/12, 0.30–2.10 9/12, 0.30–2.20 8/13, 0.30–2.25 8/13.

Length alone: joint minimum total 22; ties: 0.30–1.95 7/15, 0.30–2.00 7/15, 0.30–2.05 7/15, 0.30–2.10 7/15, 0.30–2.20 6/16, 0.30–2.25 6/16.

### mixed (n = 4, objective n = 4, owner {'KEEP': 4}) — **too few lines; indicative only**

| Band | Length alone fd/fk | End to end fd/fk |
| --- | --- | --- |
| current 0.50–1.50 | 0/0 (total 0; length-blind kept 0/0) | 0/0 (total 0; length-blind kept 0/0) |
| joint optimum (tie rule) 0.50–1.50 | 0/0 (total 0; length-blind kept 0/0) | 0/0 (total 0; length-blind kept 0/0) |

Joint minimum end-to-end total 0; every tie (L–U fd/fk): 0.30–1.50 0/0, 0.30–1.55 0/0, 0.30–1.60 0/0, 0.30–1.65 0/0, 0.30–1.70 0/0, 0.30–1.75 0/0, 0.30–1.80 0/0, 0.30–1.85 0/0, 0.30–1.90 0/0, 0.30–1.95 0/0, 0.30–2.00 0/0, 0.30–2.05 0/0, 0.30–2.10 0/0, 0.30–2.15 0/0, 0.30–2.20 0/0, 0.30–2.25 0/0, 0.30–2.30 0/0, 0.30–2.35 0/0, 0.30–2.40 0/0, 0.30–2.45 0/0, 0.30–2.50 0/0, 0.35–1.50 0/0, 0.35–1.55 0/0, 0.35–1.60 0/0, 0.35–1.65 0/0, 0.35–1.70 0/0, 0.35–1.75 0/0, 0.35–1.80 0/0, 0.35–1.85 0/0, 0.35–1.90 0/0, 0.35–1.95 0/0, 0.35–2.00 0/0, 0.35–2.05 0/0, 0.35–2.10 0/0, 0.35–2.15 0/0, 0.35–2.20 0/0, 0.35–2.25 0/0, 0.35–2.30 0/0, 0.35–2.35 0/0, 0.35–2.40 0/0, 0.35–2.45 0/0, 0.35–2.50 0/0, 0.40–1.50 0/0, 0.40–1.55 0/0, 0.40–1.60 0/0, 0.40–1.65 0/0, 0.40–1.70 0/0, 0.40–1.75 0/0, 0.40–1.80 0/0, 0.40–1.85 0/0, 0.40–1.90 0/0, 0.40–1.95 0/0, 0.40–2.00 0/0, 0.40–2.05 0/0, 0.40–2.10 0/0, 0.40–2.15 0/0, 0.40–2.20 0/0, 0.40–2.25 0/0, 0.40–2.30 0/0, 0.40–2.35 0/0, 0.40–2.40 0/0, 0.40–2.45 0/0, 0.40–2.50 0/0, 0.45–1.50 0/0, 0.45–1.55 0/0, 0.45–1.60 0/0, 0.45–1.65 0/0, 0.45–1.70 0/0, 0.45–1.75 0/0, 0.45–1.80 0/0, 0.45–1.85 0/0, 0.45–1.90 0/0, 0.45–1.95 0/0, 0.45–2.00 0/0, 0.45–2.05 0/0, 0.45–2.10 0/0, 0.45–2.15 0/0, 0.45–2.20 0/0, 0.45–2.25 0/0, 0.45–2.30 0/0, 0.45–2.35 0/0, 0.45–2.40 0/0, 0.45–2.45 0/0, 0.45–2.50 0/0, 0.50–1.50 0/0, 0.50–1.55 0/0, 0.50–1.60 0/0, 0.50–1.65 0/0, 0.50–1.70 0/0, 0.50–1.75 0/0, 0.50–1.80 0/0, 0.50–1.85 0/0, 0.50–1.90 0/0, 0.50–1.95 0/0, 0.50–2.00 0/0, 0.50–2.05 0/0, 0.50–2.10 0/0, 0.50–2.15 0/0, 0.50–2.20 0/0, 0.50–2.25 0/0, 0.50–2.30 0/0, 0.50–2.35 0/0, 0.50–2.40 0/0, 0.50–2.45 0/0, 0.50–2.50 0/0, 0.55–1.50 0/0, 0.55–1.55 0/0, 0.55–1.60 0/0, 0.55–1.65 0/0, 0.55–1.70 0/0, 0.55–1.75 0/0, 0.55–1.80 0/0, 0.55–1.85 0/0, 0.55–1.90 0/0, 0.55–1.95 0/0, 0.55–2.00 0/0, 0.55–2.05 0/0, 0.55–2.10 0/0, 0.55–2.15 0/0, 0.55–2.20 0/0, 0.55–2.25 0/0, 0.55–2.30 0/0, 0.55–2.35 0/0, 0.55–2.40 0/0, 0.55–2.45 0/0, 0.55–2.50 0/0, 0.60–1.50 0/0, 0.60–1.55 0/0, 0.60–1.60 0/0, 0.60–1.65 0/0, 0.60–1.70 0/0, 0.60–1.75 0/0, 0.60–1.80 0/0, 0.60–1.85 0/0, 0.60–1.90 0/0, 0.60–1.95 0/0, 0.60–2.00 0/0, 0.60–2.05 0/0, 0.60–2.10 0/0, 0.60–2.15 0/0, 0.60–2.20 0/0, 0.60–2.25 0/0, 0.60–2.30 0/0, 0.60–2.35 0/0, 0.60–2.40 0/0, 0.60–2.45 0/0, 0.60–2.50 0/0, 0.65–1.50 0/0, 0.65–1.55 0/0, 0.65–1.60 0/0, 0.65–1.65 0/0, 0.65–1.70 0/0, 0.65–1.75 0/0, 0.65–1.80 0/0, 0.65–1.85 0/0, 0.65–1.90 0/0, 0.65–1.95 0/0, 0.65–2.00 0/0, 0.65–2.05 0/0, 0.65–2.10 0/0, 0.65–2.15 0/0, 0.65–2.20 0/0, 0.65–2.25 0/0, 0.65–2.30 0/0, 0.65–2.35 0/0, 0.65–2.40 0/0, 0.65–2.45 0/0, 0.65–2.50 0/0, 0.70–1.50 0/0, 0.70–1.55 0/0, 0.70–1.60 0/0, 0.70–1.65 0/0, 0.70–1.70 0/0, 0.70–1.75 0/0, 0.70–1.80 0/0, 0.70–1.85 0/0, 0.70–1.90 0/0, 0.70–1.95 0/0, 0.70–2.00 0/0, 0.70–2.05 0/0, 0.70–2.10 0/0, 0.70–2.15 0/0, 0.70–2.20 0/0, 0.70–2.25 0/0, 0.70–2.30 0/0, 0.70–2.35 0/0, 0.70–2.40 0/0, 0.70–2.45 0/0, 0.70–2.50 0/0, 0.75–1.50 0/0, 0.75–1.55 0/0, 0.75–1.60 0/0, 0.75–1.65 0/0, 0.75–1.70 0/0, 0.75–1.75 0/0, 0.75–1.80 0/0, 0.75–1.85 0/0, 0.75–1.90 0/0, 0.75–1.95 0/0, 0.75–2.00 0/0, 0.75–2.05 0/0, 0.75–2.10 0/0, 0.75–2.15 0/0, 0.75–2.20 0/0, 0.75–2.25 0/0, 0.75–2.30 0/0, 0.75–2.35 0/0, 0.75–2.40 0/0, 0.75–2.45 0/0, 0.75–2.50 0/0, 0.80–1.50 0/0, 0.80–1.55 0/0, 0.80–1.60 0/0, 0.80–1.65 0/0, 0.80–1.70 0/0, 0.80–1.75 0/0, 0.80–1.80 0/0, 0.80–1.85 0/0, 0.80–1.90 0/0, 0.80–1.95 0/0, 0.80–2.00 0/0, 0.80–2.05 0/0, 0.80–2.10 0/0, 0.80–2.15 0/0, 0.80–2.20 0/0, 0.80–2.25 0/0, 0.80–2.30 0/0, 0.80–2.35 0/0, 0.80–2.40 0/0, 0.80–2.45 0/0, 0.80–2.50 0/0.

Length alone: joint minimum total 0; ties: 0.30–1.50 0/0, 0.30–1.55 0/0, 0.30–1.60 0/0, 0.30–1.65 0/0, 0.30–1.70 0/0, 0.30–1.75 0/0, 0.30–1.80 0/0, 0.30–1.85 0/0, 0.30–1.90 0/0, 0.30–1.95 0/0, 0.30–2.00 0/0, 0.30–2.05 0/0, 0.30–2.10 0/0, 0.30–2.15 0/0, 0.30–2.20 0/0, 0.30–2.25 0/0, 0.30–2.30 0/0, 0.30–2.35 0/0, 0.30–2.40 0/0, 0.30–2.45 0/0, 0.30–2.50 0/0, 0.35–1.50 0/0, 0.35–1.55 0/0, 0.35–1.60 0/0, 0.35–1.65 0/0, 0.35–1.70 0/0, 0.35–1.75 0/0, 0.35–1.80 0/0, 0.35–1.85 0/0, 0.35–1.90 0/0, 0.35–1.95 0/0, 0.35–2.00 0/0, 0.35–2.05 0/0, 0.35–2.10 0/0, 0.35–2.15 0/0, 0.35–2.20 0/0, 0.35–2.25 0/0, 0.35–2.30 0/0, 0.35–2.35 0/0, 0.35–2.40 0/0, 0.35–2.45 0/0, 0.35–2.50 0/0, 0.40–1.50 0/0, 0.40–1.55 0/0, 0.40–1.60 0/0, 0.40–1.65 0/0, 0.40–1.70 0/0, 0.40–1.75 0/0, 0.40–1.80 0/0, 0.40–1.85 0/0, 0.40–1.90 0/0, 0.40–1.95 0/0, 0.40–2.00 0/0, 0.40–2.05 0/0, 0.40–2.10 0/0, 0.40–2.15 0/0, 0.40–2.20 0/0, 0.40–2.25 0/0, 0.40–2.30 0/0, 0.40–2.35 0/0, 0.40–2.40 0/0, 0.40–2.45 0/0, 0.40–2.50 0/0, 0.45–1.50 0/0, 0.45–1.55 0/0, 0.45–1.60 0/0, 0.45–1.65 0/0, 0.45–1.70 0/0, 0.45–1.75 0/0, 0.45–1.80 0/0, 0.45–1.85 0/0, 0.45–1.90 0/0, 0.45–1.95 0/0, 0.45–2.00 0/0, 0.45–2.05 0/0, 0.45–2.10 0/0, 0.45–2.15 0/0, 0.45–2.20 0/0, 0.45–2.25 0/0, 0.45–2.30 0/0, 0.45–2.35 0/0, 0.45–2.40 0/0, 0.45–2.45 0/0, 0.45–2.50 0/0, 0.50–1.50 0/0, 0.50–1.55 0/0, 0.50–1.60 0/0, 0.50–1.65 0/0, 0.50–1.70 0/0, 0.50–1.75 0/0, 0.50–1.80 0/0, 0.50–1.85 0/0, 0.50–1.90 0/0, 0.50–1.95 0/0, 0.50–2.00 0/0, 0.50–2.05 0/0, 0.50–2.10 0/0, 0.50–2.15 0/0, 0.50–2.20 0/0, 0.50–2.25 0/0, 0.50–2.30 0/0, 0.50–2.35 0/0, 0.50–2.40 0/0, 0.50–2.45 0/0, 0.50–2.50 0/0, 0.55–1.50 0/0, 0.55–1.55 0/0, 0.55–1.60 0/0, 0.55–1.65 0/0, 0.55–1.70 0/0, 0.55–1.75 0/0, 0.55–1.80 0/0, 0.55–1.85 0/0, 0.55–1.90 0/0, 0.55–1.95 0/0, 0.55–2.00 0/0, 0.55–2.05 0/0, 0.55–2.10 0/0, 0.55–2.15 0/0, 0.55–2.20 0/0, 0.55–2.25 0/0, 0.55–2.30 0/0, 0.55–2.35 0/0, 0.55–2.40 0/0, 0.55–2.45 0/0, 0.55–2.50 0/0, 0.60–1.50 0/0, 0.60–1.55 0/0, 0.60–1.60 0/0, 0.60–1.65 0/0, 0.60–1.70 0/0, 0.60–1.75 0/0, 0.60–1.80 0/0, 0.60–1.85 0/0, 0.60–1.90 0/0, 0.60–1.95 0/0, 0.60–2.00 0/0, 0.60–2.05 0/0, 0.60–2.10 0/0, 0.60–2.15 0/0, 0.60–2.20 0/0, 0.60–2.25 0/0, 0.60–2.30 0/0, 0.60–2.35 0/0, 0.60–2.40 0/0, 0.60–2.45 0/0, 0.60–2.50 0/0, 0.65–1.50 0/0, 0.65–1.55 0/0, 0.65–1.60 0/0, 0.65–1.65 0/0, 0.65–1.70 0/0, 0.65–1.75 0/0, 0.65–1.80 0/0, 0.65–1.85 0/0, 0.65–1.90 0/0, 0.65–1.95 0/0, 0.65–2.00 0/0, 0.65–2.05 0/0, 0.65–2.10 0/0, 0.65–2.15 0/0, 0.65–2.20 0/0, 0.65–2.25 0/0, 0.65–2.30 0/0, 0.65–2.35 0/0, 0.65–2.40 0/0, 0.65–2.45 0/0, 0.65–2.50 0/0, 0.70–1.50 0/0, 0.70–1.55 0/0, 0.70–1.60 0/0, 0.70–1.65 0/0, 0.70–1.70 0/0, 0.70–1.75 0/0, 0.70–1.80 0/0, 0.70–1.85 0/0, 0.70–1.90 0/0, 0.70–1.95 0/0, 0.70–2.00 0/0, 0.70–2.05 0/0, 0.70–2.10 0/0, 0.70–2.15 0/0, 0.70–2.20 0/0, 0.70–2.25 0/0, 0.70–2.30 0/0, 0.70–2.35 0/0, 0.70–2.40 0/0, 0.70–2.45 0/0, 0.70–2.50 0/0, 0.75–1.50 0/0, 0.75–1.55 0/0, 0.75–1.60 0/0, 0.75–1.65 0/0, 0.75–1.70 0/0, 0.75–1.75 0/0, 0.75–1.80 0/0, 0.75–1.85 0/0, 0.75–1.90 0/0, 0.75–1.95 0/0, 0.75–2.00 0/0, 0.75–2.05 0/0, 0.75–2.10 0/0, 0.75–2.15 0/0, 0.75–2.20 0/0, 0.75–2.25 0/0, 0.75–2.30 0/0, 0.75–2.35 0/0, 0.75–2.40 0/0, 0.75–2.45 0/0, 0.75–2.50 0/0, 0.80–1.50 0/0, 0.80–1.55 0/0, 0.80–1.60 0/0, 0.80–1.65 0/0, 0.80–1.70 0/0, 0.80–1.75 0/0, 0.80–1.80 0/0, 0.80–1.85 0/0, 0.80–1.90 0/0, 0.80–1.95 0/0, 0.80–2.00 0/0, 0.80–2.05 0/0, 0.80–2.10 0/0, 0.80–2.15 0/0, 0.80–2.20 0/0, 0.80–2.25 0/0, 0.80–2.30 0/0, 0.80–2.35 0/0, 0.80–2.40 0/0, 0.80–2.45 0/0, 0.80–2.50 0/0.

### Owner marks by r interval (objective population, all types)

| r interval | owner KEEP | owner DROP |
| --- | --- | --- |
| [0, 0.2) | 1 | 15 |
| [0.2, 0.25) | 2 | 2 |
| [0.25, 0.3) | 1 | 2 |
| [0.3, 0.35) | 2 | 1 |
| [0.35, 0.4) | 8 | 2 |
| [0.4, 0.45) | 11 | 2 |
| [0.45, 0.5) | 10 | 2 |
| [0.5, 0.55) | 4 | 2 |
| [0.55, 0.6) | 14 | 1 |
| [0.6, 1.4) | 348 | 13 |
| [1.4, 1.5) | 11 | 2 |
| [1.5, 1.6) | 6 | 2 |
| [1.6, 1.8) | 8 | 0 |
| [1.8, 2.0) | 3 | 1 |
| [2.0, 2.25) | 2 | 2 |
| [2.25, 2.5) | 1 | 3 |
| [2.5, 99) | 2 | 4 |

L = 0.30 is the floor of the requested grid. Below it the objective population has 4 owner KEEP and 19 owner DROP lines, so extending the grid lower adds owner DROPs faster than owner KEEPs: [0.25, 0.30) holds 1 KEEP / 2 DROP.

## 3. Proposed bounds (from the end-to-end joint optimum and the tie rule)

Tie rule: fewest total errors, then nearest to the current band (|L − 0.5| + |U − 1.5|), then lower L, then lower U.

| Scheme | Band | Length alone fd/fk | End to end fd/fk (padding 1.5 unchanged) |
| --- | --- | --- | --- |
| overall, current | 0.50–1.50 | 57/18 (total 75; length-blind kept 8/10) | 59/16 (total 75; length-blind kept 8/10) |
| **overall, proposed** | **0.30–2.00** | 8/28 (total 36; length-blind kept 10/10) | 10/24 (total 34; length-blind kept 10/10) |
| numeric, current | 0.50–1.50 | 15/3 (total 18; length-blind kept 2/3) | 15/3 (total 18; length-blind kept 2/3) |
| **numeric, proposed** | **0.35–2.00** | 2/4 (total 6; length-blind kept 3/3) | 2/3 (total 5; length-blind kept 3/3) |
| numeric lines under the overall proposal | 0.30–2.00 | 2/4 (total 6; length-blind kept 3/3) | 2/3 (total 5; length-blind kept 3/3) |

Overall: fd 59 → 10 (-49), fk 16 → 24 (+8); length-blind kept 8 → 10 of 10.

Numeric: fd 15 → 2 (-13), fk 3 → 3 (+0); length-blind kept 2 → 3 of 3. A separate numeric band would be an output-type switch in the tool. On these 171 numeric lines the overall proposal 0.30–2.00 gives the same keep/drop as the numeric proposal 0.35–2.00 on 171 of 171 lines (row 'numeric lines under the overall proposal').

### How many lines each bound move rests on

From current to proposed (overall): the lower bound 0.50 → 0.30 changes 39 lines (owner KEEP 31, owner DROP 8); the upper bound 1.50 → 2.00 changes 22 lines (owner KEEP 18, owner DROP 4). Counts include length-blind and padding-dropped lines.

One grid step away from each proposed point (end to end):

| Scheme | Neighbour band | Lines whose keep/drop differs from the proposal | Their owner marks | Neighbour fd/fk (total) |
| --- | --- | --- | --- | --- |
| overall | 0.35–2.00 | 3 | {'KEEP': 2, 'DROP': 1} | 12/23 (35) |
| overall | 0.30–1.95 | 1 | {'KEEP': 1} | 11/24 (35) |
| overall | 0.30–2.05 | 1 | {'DROP': 1} | 10/25 (35) |
| numeric | 0.30–2.00 | 0 | {} | 2/3 (5) |
| numeric | 0.40–2.00 | 2 | {'KEEP': 2} | 4/3 (7) |
| numeric | 0.35–1.95 | 1 | {'KEEP': 1} | 3/3 (6) |
| numeric | 0.35–2.05 | 1 | {'DROP': 1} | 2/4 (6) |

### Diagnostic: unequal costs

Not part of the proposal. If a false keep is counted as w false drops, the end-to-end optimum (same tie rule) is:

| Scheme | w | Optimum | fd/fk | Current fd/fk |
| --- | --- | --- | --- | --- |
| overall | 1 | 0.30–2.00 | 10/24 | 59/16 |
| overall | 2 | 0.35–2.00 | 12/23 | 59/16 |
| overall | 3 | 0.35–1.85 | 15/22 | 59/16 |
| overall | 7.75 (class-balanced: KEEP n / DROP n) | 0.55–1.30 | 84/11 | 59/16 |
| numeric | 1 | 0.35–2.00 | 2/3 | 15/3 |
| numeric | 2 | 0.35–2.00 | 2/3 | 15/3 |
| numeric | 3 | 0.35–2.00 | 2/3 | 15/3 |
| numeric | 32.6 (class-balanced: KEEP n / DROP n) | 0.35–1.25 | 21/2 | 15/3 |

The judged sets are not a random sample of the census (the typology sheet holds small crops; the deskew sheet holds verdict flips; the cells sheet holds census samples), so all counts in this report are counts of owner-judged lines, not census error rates.

## 4. Stability

Every fit uses the same tie rule on the training part and counts end-to-end errors (fd/fk, length-blind excluded) on the held-out part, for the fitted band and for the current 0.50–1.50.

### overall (proposed 0.30–2.00)

| Check | Held out | n train | n held out | Fitted band | Held-out current fd/fk (total) | Held-out fitted fd/fk (total) | Errors saved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| split_half | hash half 1 (fit on half 0) | 268 | 232 | 0.35–2.00 | 29/7 (36) | 7/9 (16) | 20 |
| split_half | hash half 0 (fit on half 1) | 232 | 268 | 0.30–1.85 | 30/9 (39) | 8/13 (21) | 18 |
| loso_source_set | 888 ratings | 404 | 96 | 0.30–2.00 | 18/3 (21) | 5/7 (12) | 9 |
| loso_source_set | cells (census samples, 0.5) | 348 | 152 | 0.30–1.95 | 11/2 (13) | 3/2 (5) | 8 |
| loso_source_set | deskew flips (27 lines) | 484 | 16 | 0.30–2.00 | 3/2 (5) | 0/3 (3) | 2 |
| loso_source_set | gate (150 lines, 0.8) | 445 | 55 | 0.30–2.00 | 14/5 (19) | 3/8 (11) | 8 |
| loso_source_set | typology marks | 319 | 181 | 0.35–2.00 | 13/4 (17) | 1/4 (5) | 12 |
| loso_cohort | calibration | 382 | 118 | 0.30–2.00 | 23/6 (29) | 5/11 (16) | 13 |
| loso_cohort | cells | 348 | 152 | 0.30–1.95 | 11/2 (13) | 3/2 (5) | 8 |
| loso_cohort | segeval1 | 435 | 65 | 0.30–2.00 | 16/5 (21) | 3/8 (11) | 10 |
| loso_cohort | typology | 335 | 165 | 0.35–2.00 | 9/3 (12) | 1/3 (4) | 8 |

Bootstrap (1000 resamples of the 490 objective lines, seed 20261019): optimal L quantiles 2.5/25/50/75/97.5 % = 0.30, 0.30, 0.30, 0.35, 0.35; optimal U = 1.75, 1.95, 2.00, 2.00, 2.45.

L frequency: {0.3: 600, 0.35: 395, 0.4: 5}. U frequency: {1.7: 1, 1.75: 25, 1.8: 39, 1.85: 107, 1.95: 173, 2.0: 449, 2.2: 117, 2.45: 89}.

Current 0.50–1.50 is a tied optimum in 0/1000 resamples; the proposed band in 585/1000. Errors saved by the proposed band over current, per resample, quantiles 2.5/25/50/75/97.5 % = 27, 37, 41, 46, 58; ≤ 0 in 0/1000.

### numeric (proposed 0.35–2.00)

| Check | Held out | n train | n held out | Fitted band | Held-out current fd/fk (total) | Held-out fitted fd/fk (total) | Errors saved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| split_half | hash half 1 (fit on half 0) | 91 | 80 | 0.35–2.45 | 5/1 (6) | 1/2 (3) | 3 |
| split_half | hash half 0 (fit on half 1) | 80 | 91 | 0.40–1.80 | 10/2 (12) | 4/2 (6) | 6 |
| loso_source_set | 888 ratings | 162 | 9 | 0.35–2.00 | 1/0 (1) | 0/0 (0) | 1 |
| loso_source_set | cells (census samples, 0.5) | 21 | 150 | 0.35–1.70 | 11/1 (12) | 5/1 (6) | 6 |
| loso_source_set | deskew flips (27 lines) | 169 | 2 | 0.35–2.00 | 0/1 (1) | 0/1 (1) | 0 |
| loso_source_set | gate (150 lines, 0.8) | 161 | 10 | 0.40–2.45 | 3/1 (4) | 2/2 (4) | 0 |
| loso_cohort | calibration | 159 | 12 | 0.35–2.00 | 1/1 (2) | 0/1 (1) | 1 |
| loso_cohort | cells | 21 | 150 | 0.35–1.70 | 11/1 (12) | 5/1 (6) | 6 |
| loso_cohort | segeval1 | 162 | 9 | 0.40–2.45 | 3/1 (4) | 2/2 (4) | 0 |

Bootstrap (1000 resamples of the 168 objective lines, seed 20261019): optimal L quantiles 2.5/25/50/75/97.5 % = 0.35, 0.35, 0.35, 0.35, 0.40; optimal U = 1.70, 2.00, 2.00, 2.45, 2.45.

L frequency: {0.35: 891, 0.4: 97, 0.45: 7, 0.5: 5}. U frequency: {1.55: 1, 1.7: 29, 1.75: 61, 1.8: 151, 2.0: 431, 2.45: 327}.

Current 0.50–1.50 is a tied optimum in 0/1000 resamples; the proposed band in 673/1000. Errors saved by the proposed band over current, per resample, quantiles 2.5/25/50/75/97.5 % = 7, 10.75, 13, 15, 20; ≤ 0 in 0/1000.

## 5. Lines whose verdict changes (proposed vs current 0.50–1.50, end to end)

[changed_lines.jsonl](changed_lines.jsonl). Overall scheme: 59 lines ({'fixes': 49, 'breaks': 8, 'length cannot see this': 2}). Numeric scheme (numeric lines only): 14 lines ({'fixes': 13, 'length cannot see this': 1}). 'fixes' = new keep/drop agrees with the owner; 'breaks' = it now disagrees. Lines that stay DROP but change reason are not counted: overall: gazette_modern--13a9303cfc83a9d4--s000-l0045 (3, r 0.395, owner DROP) DROP (too little) → DROP (padding); overall: ia_greek_latin--d53eaf7b3036014c--s004-l0001 (hagrep, scorpione, r 0.475, owner DROP) DROP (too little) → DROP (padding); numeric: gazette_modern--13a9303cfc83a9d4--s000-l0045 (3, r 0.395, owner DROP) DROP (too little) → DROP (padding).

### overall scheme (0.30-2.00)

| ID | Text | r | Owner | Type | Small | Current | Proposed | Effect | Owner note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ia_greek_latin--8af66d4d113847ee--s003-l0107 | ......................... | 0.318 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--819a6ad32e0c7ab2--s000-l0004 | ΝΤΙΛΕΣΙΠ | 0.346 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| lekythos--49c082ba27aa27da--s000-l0046 | Η του | 0.350 | DROP | non-numeric | False | DROP (too little) | KEEP | breaks |  |
| nlg--1144074169f43992--s003-l0001 | ΜΕΡΟΣ ΠΡΩΤΟΝ | 0.350 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--52ee6226bb7d4834--s000-l0122 | ΠΟΛΕΩΣ | 0.351 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--d4e7c0bb57264e92--s000-l0030 | 3.237.787 | 0.358 | KEEP | numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--82115ca04c55f5b7--s000-l0005 | ΥΠΟΜΝΗΜΑ | 0.369 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | 1 | 0.381 | KEEP | numeric | True | DROP (too little) | KEEP | fixes |  |
| elstat--2b5780c7c9896a54--s000-l0051 | Sommaire | 0.389 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| serbia--9caa9fc02f50cad6--s000-l0010 | САВЕ ДЕЧАНЦА | 0.394 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--bd7c91e6a214949b--s000-l0125 | ハンハンΟΜΙΑΣ. | 0.395 | DROP | non-numeric | False | DROP (too little) | KEEP | breaks | why am I seeing lines with these chars ハンハン |
| nlg--6ae0ac01064a587e--s002-l0004 | ΤΑ ΨΗΛΑ ΒΟΥΝΑ | 0.400 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| nlg--f4b52df5f8130047--s034-l0008 | Ο ΠΥΡΓΟΣ | 0.401 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| ia_greek_latin--8af66d4d113847ee--s003-l0022 | ...................... | 0.402 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--96035db0434dc980--s000-l0074 | 1 | 0.409 | KEEP | numeric | True | DROP (too little) | KEEP | fixes |  |
| serbia--9caa9fc02f50cad6--s003-l0009 | САВЕ ДЕЧАНЦА | 0.410 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--59bea69d71112ea7--s000-l0064 | ΖΗΜΙΑΙ | 0.417 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| ia_greek_latin--e02bf39b0ef9974e--s007-l0001 | THE ODYSSEY BOOK XIV. | 0.429 | DROP | non-numeric | False | DROP (too little) | KEEP | breaks |  |
| gazette_modern--c4919950cda5532e--s000-l0008 | ΠΑΓΙΟ | 0.433 | KEEP | non-numeric | True | DROP (too little) | KEEP | fixes |  |
| serbia--b6450341d87fb144--s007-l0002 | ВИЉЕМ БУE | 0.435 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | PAEONIA | 0.438 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--af3c2f9a667e8669--s000-l0004 | ΑΘΗΝΑ | 0.440 | KEEP | non-numeric | True | DROP (too little) | KEEP | fixes |  |
| gazette_modern--c1b2194696b35bb5--s000-l0004 | ΑΘΗΝΑ | 0.440 | KEEP | non-numeric | True | DROP (too little) | KEEP | fixes |  |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | - | 0.441 | DROP | non-numeric | True | DROP (too little) | KEEP | breaks |  |
| gazette_modern--a8e70ef11baca460--s000-l0001 | 1 | 0.441 | KEEP | numeric | True | DROP (too little) | KEEP | fixes |  |
| lekythos--456def1ccfc2283e--s001-l0177 | -'-'-'-'-'-'-'0 | 0.465 | DROP | numeric | False | DROP (too little) | KEEP | length cannot see this | bad output, although evenly matched per chars |
| gazette_modern--232906bf221ad08d--s000-l0144 | & ΣΙΑ | 0.472 | KEEP | non-numeric | True | DROP (too little) | KEEP | fixes |  |
| ia_greek_latin--5f5319037ff4b70f--s001-l0039 | II. INDEX LOCORUM | 0.475 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--7f20c8792129c8f6--s000-l0062 | που | 0.478 | KEEP | non-numeric | True | DROP (too little) | KEEP | fixes |  |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | " | 0.478 | DROP | non-numeric | True | DROP (too little) | KEEP | breaks |  |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | 1 | 0.482 | KEEP | numeric | True | DROP (too little) | KEEP | fixes |  |
| ia_poly1850--61d0e23d1e93ae02--s031-l0002 | ΠΕΡΙΕΧΟΜΕΝΑ. | 0.488 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| ia_greek_latin--f40a7578d8cd5825--s005-l0001 | NEW SERIES OF LATIN SCHOOL BOOKS. | 0.490 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| lekythos--a0c4e6327052acfc--s002-l0089 | / | 0.492 | KEEP | non-numeric | True | DROP (too little) | KEEP | fixes |  |
| gazette_modern--b05f7f66a8e2e416--s000-l0067 | ΔΗΜ. ΓΕΩΡΓΑΚΟΠΟΥΛΟΣ | 0.494 | KEEP | non-numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--6d58ca2e2dc41e69--s000-l0140 | του | 0.496 | KEEP | non-numeric | True | DROP (too little) | KEEP | fixes |  |
| ia_russian--06528548147a3a3d--s002-l0005 | ли | 0.497 | KEEP | non-numeric | True | DROP (too little) | KEEP | fixes |  |
| ia_greek_latin--5f5319037ff4b70f--s000-l0028 | LIBRARY | 1.510 | DROP | non-numeric | True | DROP (too much) | KEEP | breaks |  |
| gazette_modern--8757f64ef1908c90--s000-l0009 | 1. Τις διατάξεις του από 24.4.85 Π.Δ/τος | 1.522 | KEEP | non-numeric | False | DROP (too much) | KEEP | fixes |  |
| lekythos--7f67b784930deef5--s004-l0004 | HUMILLY (HAUTE SAVOIE) | 1.524 | DROP | non-numeric | False | DROP (too much) | KEEP | breaks |  |
| elstat--0a2c92120843658d--s001-l0216 | 1 | 1.534 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--62822e3af8f17cf4--s000-l0074 | ανέρ- | 1.535 | KEEP | non-numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--f4a16fe9302ade1e--s000-l0180 | 29) | 1.538 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0065 | *Vid. Luc. | 1.542 | KEEP | non-numeric | False | DROP (too much) | KEEP | fixes |  |
| gazette_modern--d6092126b747cac8--s000-l0014 | 1 | 1.542 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--9aa01acfc4b8b0a7--s000-l0100 | κτηριστικών (απόφαση ΣΤ-20270/73-Φ.Ε.Κ.  | 1.613 | KEEP | non-numeric | False | DROP (too much) | KEEP | fixes | length is correct;  |
| ia_greek_latin--2b4cfc7c6d70fd98--s000-l0053 | ἀνάμνησις, 36 | 1.627 | KEEP | non-numeric | False | DROP (too much) | KEEP | fixes |  |
| gazette_modern--80e8a42cbf8e629f--s000-l0120 | 13.3.1986 (ΦΕΚ 93/Γ΄/11.4.86) και μόνο κ | 1.641 | DROP | non-numeric | False | DROP (too much) | KEEP | length cannot see this | green box is a little high (seems to be dragged under the top line  should have been dropped because there are more than 2 or more full words showing. the output length is correct |
| gazette_modern--3ff46b4e721f2046--s000-l0375 | 254/6 | 1.677 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--6bc7acccf0163698--s000-l0268 | 1 | 1.694 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--e4940977902166f0--s000-l0109 | γούρια) | 1.713 | KEEP | non-numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--6efb0af18300ce89--s000-l0085 | Γραμματέα, Δ/ντές και Τμηματάρχες της Κε | 1.721 | KEEP | non-numeric | False | DROP (too much) | KEEP | fixes |  |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | 1. | 1.737 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | 1 | 1.770 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| elstat--0877c813a8512b56--s000-l0114 | Slightly | 1.830 | KEEP | non-numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--c36d4711ccb77454--s000-l0227 | του αρθ. 42ε παράγρ. 14 του Ν.2190/1920, | 1.908 | DROP | non-numeric | False | DROP (too much) | KEEP | breaks |  |
| gazette_modern--a895f3d785bb13b6--s000-l0138 | θε όσουε τη συμφωνία του περιεχομένου τη | 1.912 | KEEP | non-numeric | False | DROP (too much) | KEEP | fixes |  |
| gazette_modern--7e81c2a51da91d05--s000-l0065 | Βασίλης Τσιουρίκης | 1.925 | KEEP | non-numeric | False | DROP (too much) | KEEP | fixes |  |
| elstat--c4d30f00b317e558--s001-l0501 | 1 | 2.000 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |

### numeric scheme (0.35-2.00)

| ID | Text | r | Owner | Type | Small | Current | Proposed | Effect | Owner note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gazette_modern--d4e7c0bb57264e92--s000-l0030 | 3.237.787 | 0.358 | KEEP | numeric | False | DROP (too little) | KEEP | fixes |  |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | 1 | 0.381 | KEEP | numeric | True | DROP (too little) | KEEP | fixes |  |
| gazette_modern--96035db0434dc980--s000-l0074 | 1 | 0.409 | KEEP | numeric | True | DROP (too little) | KEEP | fixes |  |
| gazette_modern--a8e70ef11baca460--s000-l0001 | 1 | 0.441 | KEEP | numeric | True | DROP (too little) | KEEP | fixes |  |
| lekythos--456def1ccfc2283e--s001-l0177 | -'-'-'-'-'-'-'0 | 0.465 | DROP | numeric | False | DROP (too little) | KEEP | length cannot see this | bad output, although evenly matched per chars |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | 1 | 0.482 | KEEP | numeric | True | DROP (too little) | KEEP | fixes |  |
| elstat--0a2c92120843658d--s001-l0216 | 1 | 1.534 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--f4a16fe9302ade1e--s000-l0180 | 29) | 1.538 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--d6092126b747cac8--s000-l0014 | 1 | 1.542 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--3ff46b4e721f2046--s000-l0375 | 254/6 | 1.677 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--6bc7acccf0163698--s000-l0268 | 1 | 1.694 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | 1. | 1.737 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | 1 | 1.770 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |
| elstat--c4d30f00b317e558--s001-l0501 | 1 | 2.000 | KEEP | numeric | True | DROP (too much) | KEEP | fixes |  |

## 6. Owner cases from steps 1–3

| ID | Case | In population | Owner | r | Padding | Current | Proposed overall 0.30–2.00 | Proposed numeric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gazette_modern--52ee6226bb7d4834--s000-l0122 | S2 vertical witness, letter-spaced caps "ΠΟΛΕΩΣ"; owner KEEP, drops on too-little (r≈0.35) | True | KEEP | 0.351 | 0.414 | DROP (too little) | KEEP | n/a (not numeric) |
| gazette_modern--82115ca04c55f5b7--s000-l0005 | S2 vertical witness; owner KEEP, drops on too-little | True | KEEP | 0.369 | 0.460 | DROP (too little) | KEEP | n/a (not numeric) |
| gazette_modern--80e8a42cbf8e629f--s000-l0120 | S1 witness; owner DROP: "should have been dropped ... more than 2 full words ... the output length is correct" | True | DROP | 1.641 | 0.000 | DROP (too much) | KEEP | n/a (not numeric) |
| elstat--0877c813a8512b56--s000-l0037 | S2 vertical witness; owner KEEP, drops on padding | True | KEEP | 0.813 | 2.390 | DROP (padding) | DROP (padding) | n/a (not numeric) |
| gazette_modern--6d6a6fe53e769b59--s000-l0009 | S2 vertical witness; owner KEEP, drops on padding | True | KEEP | 0.750 | 1.667 | DROP (padding) | DROP (padding) | n/a (not numeric) |
| ia_poly1850--df8f2267db2b7275--s025-l0037 | S3 curved-row witness; owner KEEP | True | KEEP | 1.339 | 0.048 | KEEP | KEEP | n/a (not numeric) |
| 129cff40-p000009-l0107 | S1 witness; owner KEEP: "accents of ἔχει are detected as second line" | False | KEEP |  |  | gate DROP | DROP: gate: second complete line |  |

ΠΟΛΕΩΣ (r 0.351) and l0005 (r 0.369): owner KEEP; current DROP (too little) / DROP (too little); under 0.30–2.00 they become KEEP / KEEP. Gazette l0120 (owner DROP, note: the output length is correct; the line should drop on >2 whole neighbour words): r 1.641; current DROP (too much), i.e. it drops on length today; under 0.30–2.00 length keeps it and the 0.9-s4 gate passes it, so end to end it becomes KEEP against the owner DROP. It is in the 'length cannot see this' column, not in the objective. The two padding witnesses (elstat l0037, gazette l0009) stay DROP (padding) under the proposal.

Short owner-KEEP lines outside small (chars ≤ 10, non-small, currently dropped by length; the step-5 note in NOTES_FOR_LATER_STEPS.md): 15 in this population; the overall proposal keeps 10 of them by length.

| ID | Text | Chars | r | Proposed 0.30–2.00 |
| --- | --- | --- | --- | --- |
| ia_poly1850--c3f3a531e277da9a--s036-l0026 | ..... | 5 | 0.172 | DROP (too little) |
| ia_poly1850--63f57af8d450f3e8--s009-l0033 | τους υπερ | 8 | 0.212 | DROP (too little) |
| ia_russian--6cfc00f06e0f7241--s004-l0043 | ...... | 6 | 0.240 | DROP (too little) |
| ia_poly1850--a89bd2c9bdb1ca6d--s034-l0035 | .......... | 10 | 0.250 | DROP (too little) |
| gazette_modern--819a6ad32e0c7ab2--s000-l0004 | ΝΤΙΛΕΣΙΠ | 8 | 0.346 | KEEP |
| gazette_modern--52ee6226bb7d4834--s000-l0122 | ΠΟΛΕΩΣ | 6 | 0.351 | KEEP |
| gazette_modern--d4e7c0bb57264e92--s000-l0030 | 3.237.787 | 9 | 0.358 | KEEP |
| gazette_modern--82115ca04c55f5b7--s000-l0005 | ΥΠΟΜΝΗΜΑ | 8 | 0.369 | KEEP |
| elstat--2b5780c7c9896a54--s000-l0051 | Sommaire | 8 | 0.389 | KEEP |
| nlg--f4b52df5f8130047--s034-l0008 | Ο ΠΥΡΓΟΣ | 7 | 0.401 | KEEP |
| gazette_modern--59bea69d71112ea7--s000-l0064 | ΖΗΜΙΑΙ | 6 | 0.417 | KEEP |
| serbia--b6450341d87fb144--s007-l0002 | ВИЉЕМ БУE | 8 | 0.435 | KEEP |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | PAEONIA | 7 | 0.438 | KEEP |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0065 | *Vid. Luc. | 9 | 1.542 | KEEP |
| gazette_modern--4c8de7adeabc34fe--s000-l0105 | 1,036,678 | 9 | 3.559 | DROP (too much) |

## Files and reproduction

- [band_population.jsonl](band_population.jsonl): one row per population line (id, source set, cohort, chars, output type, small, r, padding, owner mark/note/source, 0.9-s4 verdict and reason, length_blind).
- [excluded.jsonl](excluded.jsonl), [owner_conflicts.jsonl](owner_conflicts.jsonl), [population_receipt.json](population_receipt.json) (input SHA-256s).
- [sweep.json](sweep.json): full grids per group and mode, stability, bootstrap, owner cases. [changed_lines.jsonl](changed_lines.jsonl). [owner_cases.json](owner_cases.json).
- Reproduce: `python3 -B s5/build_population.py && python3 -B s5/band_sweep.py` (sol-recut .venv; numpy). Read-only over s4 and the owner files; no tool, OCR, reader, network or git write.

SEG S5 READY: population 500 (excluded 33); current 0.5–1.5 errors overall 59/16; proposed overall 0.30–2.00 errors 10/24; numeric current 15/3 → proposed 0.35–2.00 2/3; stability held-out gain on every overall split (numeric 0–6 lines), gain ≤ 0 in 0/1000 bootstraps, exact bounds rest on 1–3 lines (bootstrap U 1.75–2.45); changed lines 59
