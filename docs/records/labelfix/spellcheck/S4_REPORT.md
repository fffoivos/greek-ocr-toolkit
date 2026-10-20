# S4 — independent detector/reader candidate

Network off; CPU only; zero recogniser/CTC forward passes. Cached alignments only. No git writes by this run and no owner sheet build or publication. Worktree started clean at `426b9be3`. HEAD and the owner-notes input changed externally during execution (HEAD later observed `ed946b42`; notes grew from 33 to 56). `S4_owner_notes_snapshot.jsonl` preserves the original 33 records used for the requested accounting. `S4_live_notes_changes.json` records 23 added notes and one updated note, outside that frozen scope and unscored here. No concurrent input changes were overwritten.

Detector output depends only on crop pixels, recogniser letters and cached character locations. `reading.read_line` returns NFC text; `read_line_details` provides unnamed-blob and localisation flags separately. Recogniser combining marks are discarded. Disconnected strokes covered by a single unopposed recogniser character form one body; a physical blob is credited once. Capitals use a compact upper-left mark group bounded by the previous letter; distant leading quote ink is separate. Upper neighbour components require an accepted lower mark anchor and cannot touch the crop edge. Low-confidence compound sets fall back to per-blob naming, with conflicting names left unresolved.

Evaluation retains the frozen S2/S3 component-slot truth and unknown words. Predictions from independent recogniser slots are projected by exact primary component identity; split-body secondary components do not receive duplicate marks. All known printed positives remain in recall denominators; bottom-clipped subscript predictions abstain exactly as in the S3 report. No adjudication was changed. S3 before totals must equal the frozen S3 report. A preliminary projection bug (overlapping letter boxes) was corrected to exact component identity before final measurement. Exploratory held-out results were seen; no thresholds or class weights were fitted against held-out results.

## Whole-line mark metrics

| kind | S3 P | S4 P | S3 R | S4 R | S3 F1 | S4 F1 |
|---|---:|---:|---:|---:|---:|---:|
| total | 91.4% | 93.5% | 86.3% | 91.9% | 88.8% | 92.7% |
| accent | 91.8% | 95.8% | 95.2% | 94.8% | 93.5% | 95.3% |
| breathing | 95.6% | 94.4% | 84.6% | 93.5% | 89.8% | 93.9% |
| compound | 76.6% | 80.5% | 62.4% | 89.1% | 68.8% | 84.6% |
| subscript | 97.7% | 97.7% | 44.7% | 44.7% | 61.3% | 61.3% |
| dialytika | — | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| apostrophe | 99.2% | 99.4% | 60.7% | 81.1% | 75.3% | 89.3% |

Held-out: 666 lines; 18229 known and 2647 unknown component slots. S3 TP/FP/FN 3497/328/556; S4 3726/261/327. Fourteen books remain evaluation only.

Capitals with printed vowel/rho marks: 93 slots; recall 0.0% → 86.0%. Capital punctuation-only slots are excluded. Compound recall includes all breathing+accent sets, including stacked components. `ᾗσι` is a native stacked witness, not an independent large stacked-truth stratum.

## Training and per-class held-out results

Decoded 4112 distinct C1 training crops (cap 10,000), selected rare compounds first with seed 20261016, plus the existing S3 DEV samples. Exact NFD Google=recogniser word agreement supplies training labels only. All C1 IDs are train split, disjoint from test IDs and all non-DEV Wikisource books. Rare compound samples are retained; ordinary classes are bounded at 1,600 C1 samples plus DEV. MLP: 96 hidden units, 100 epochs, CPU NumPy. DEV calibration uses the original S3 held-aside line IDs. Training receipt and decoded crop inventory: `S4_training.json`; fitting targets/features: `S4_training_samples.jsonl.gz`. Model SHA-256: `9de4b47010ed1a0cbe8d495d919ae35808a0cbac5846fa1bf9bf3261ab857295`.

Counts below 200 are explicit when agreement/localisation yields fewer usable samples; no held-out or synthetic samples were added to fit. Zero-support classes stay explicit. Class metrics require the entire set to match, including subscript and apostrophe; they differ from the per-kind metrics above.

| class | fit | held truth | predicted | exact TP | S3 P/R | S4 P/R |
|---|---:|---:|---:|---:|---|---|
| acute | 2008 | 1418 | 1366 | 1355 | 93.5%/94.4% | 99.2%/95.6% |
| acute+subscript | 40 | 2 | 1 | 1 | —/0.0% | 100.0%/50.0% |
| circumflex | 1729 | 303 | 310 | 270 | 87.7%/96.7% | 87.1%/89.1% |
| circumflex+subscript | 698 | 39 | 16 | 16 | 88.9%/41.0% | 100.0%/41.0% |
| dasia | 1656 | 223 | 230 | 203 | 89.2%/78.0% | 88.3%/91.0% |
| dasia+acute | 1162 | 102 | 115 | 100 | 67.0%/59.8% | 87.0%/98.0% |
| dasia+acute+subscript | 7 | 0 | 0 | 0 | —/— | —/— |
| dasia+circumflex | 941 | 18 | 18 | 10 | —/0.0% | 55.6%/55.6% |
| dasia+circumflex+subscript | 213 | 3 | 2 | 1 | —/0.0% | 50.0%/33.3% |
| dasia+grave | 814 | 7 | 43 | 5 | —/0.0% | 11.6%/71.4% |
| dasia+grave+subscript | 0 | 0 | 0 | 0 | —/— | —/— |
| dialytika | 450 | 1 | 4 | 0 | —/0.0% | 0.0%/0.0% |
| dialytika+acute | 177 | 3 | 6 | 0 | —/0.0% | 0.0%/0.0% |
| grave | 1870 | 661 | 641 | 631 | 98.1%/96.2% | 98.4%/95.5% |
| none | 3615 | 14228 | 14288 | 14173 | 98.2%/99.6% | 99.2%/99.6% |
| psili | 1806 | 646 | 625 | 607 | 97.4%/86.7% | 97.1%/94.0% |
| psili+acute | 1290 | 268 | 272 | 257 | 83.5%/71.6% | 94.5%/95.9% |
| psili+acute+subscript | 8 | 1 | 0 | 0 | —/0.0% | —/0.0% |
| psili+circumflex | 730 | 40 | 28 | 20 | 76.9%/50.0% | 71.4%/50.0% |
| psili+circumflex+subscript | 5 | 0 | 0 | 0 | —/— | —/— |
| psili+grave | 749 | 11 | 19 | 7 | 35.0%/63.6% | 36.8%/63.6% |
| psili+grave+subscript | 0 | 0 | 0 | 0 | —/— | —/— |
| psili+subscript | 18 | 0 | 0 | 0 | —/— | —/— |
| subscript | 616 | 49 | 24 | 24 | 100.0%/49.0% | 100.0%/49.0% |

Atomic marks (compounds expanded into their accent and breathing; supplementary to the frozen headline metric):

| kind | S3 P/R/F1 | S4 P/R/F1 |
|---|---|---|
| accent | 93.9%/94.1%/94.0% | 93.8%/94.6%/94.2% |
| breathing | 91.5%/78.8%/84.7% | 91.3%/93.9%/92.6% |
| compound | —/—/— | —/—/— |
| subscript | 97.7%/44.7%/61.3% | 97.7%/44.7%/61.3% |
| dialytika | —/0.0%/0.0% | 0.0%/0.0%/0.0% |
| apostrophe | 99.2%/60.7%/75.3% | 99.4%/81.1%/89.3% |

## Per-book subscripts

| book | printed positives | S3 P/R | S4 P/R |
|---|---:|---|---|
| wikisource:0b7bf21d | 0 | —/— | —/— |
| wikisource:177b717d | 3 | 0.0%/0.0% | 0.0%/0.0% |
| wikisource:22fda82b | 2 | 100.0%/50.0% | 100.0%/50.0% |
| wikisource:263438a3 | 0 | —/— | —/— |
| wikisource:384c3f89 | 80 | 100.0%/45.0% | 100.0%/45.0% |
| wikisource:4ad622a4 | 0 | —/— | —/— |
| wikisource:4f60b077 | 2 | 100.0%/100.0% | 100.0%/100.0% |
| wikisource:51fe7386 | 3 | 100.0%/33.3% | 100.0%/33.3% |
| wikisource:602cc72e | 1 | —/0.0% | —/0.0% |
| wikisource:69e993c1 | 0 | —/— | —/— |
| wikisource:6b47791c | 0 | —/— | —/— |
| wikisource:8fb8cb49 | 0 | —/— | —/— |
| wikisource:9c1dca9b | 2 | 100.0%/100.0% | 100.0%/100.0% |
| wikisource:c3e12e31 | 1 | —/0.0% | —/0.0% |

## Ascender exposure

Same frozen known unmarked bases δβλθφξζ and uppercase letters; rate counts physical above blobs, including unresolved blobs. This is a geometric false-mark diagnostic, independent of classifier correctness.

| split | slots | S3 false | S4 false |
|---|---:|---:|---:|
| all | 3558 | 6 (0.2%) | 12 (0.3%) |
| held-out | 2488 | 5 (0.2%) | 10 (0.4%) |

## Original 59 owner expectations

S3 35/59 → S4 46/59. Each v8 range uses unique maximum x-overlap, with ties/unavailable ranges unresolved. Machine receipt: `S4_owner_expectations.jsonl`; the original expectations file is unchanged.

| line | v8 → current | expectation | S3 → S4 |
|---|---|---|---|
| 02a3a2a6-p000046-l0014 | 8 → 8 | {"missed": 1} | False → False |
| 02a3a2a6-p000046-l0025 | 18 → 18 | {"false": "punctuation_dot"} | True → True |
| 177b717d-p000013-l0009 | 1 → 1 | {"missed": 2} | False → True |
| 177b717d-p000013-l0009 | 13 → 13 | {"missed": 1} | False → False |
| 177b717d-p000097-l0007 | 19 → 19 | {"false": "subscript_speck"} | True → True |
| 177b717d-p000097-l0010 | 2 → 2 | {"missed": 2} | False → True |
| 177b717d-p000097-l0010 | 5 → 5 | {"missed": 1} | True → True |
| 2793d64c-p000048-l0004 | 19 → 19 | {"missed": 1} | False → False |
| 2793d64c-p000048-l0010 | 6 → 6 | {"false": "subscript_speck"} | True → True |
| 2793d64c-p000070-l0010 | 22 → 22 | {"false": "ascender_delta"} | True → True |
| 2793d64c-p000070-l0014 | 10 → 10 | {"false": "subscript_speck"} | True → True |
| 2793d64c-p000070-l0014 | 13 → 13 | {"false": "subscript_speck"} | True → True |
| 2793d64c-p000070-l0014 | 12 → 12 | {"false": "above_speck"} | False → False |
| 2793d64c-p000072-l0007 | 3 → 3 | {"apostrophe": true} | True → True |
| 384c3f89-p000030-l0021 | 22 → 22 | {"apostrophe": true} | True → True |
| 384c3f89-p000030-l0029 | 1 → 1 | {"missed": 1} | False → False |
| 384c3f89-p000053-l0021 | 10 → 10 | {"missed": 2} | True → True |
| 384c3f89-p000053-l0021 | 32 → 32 | {"missed": 1} | True → True |
| 384c3f89-p000053-l0021 | 22 → 22 | {"apostrophe": true} | True → True |
| 384c3f89-p000053-l0028 | 25 → 25 | {"missed": 1} | True → True |
| 384c3f89-p000068-l0036 | 6 → 6 | {"apostrophe": true} | False → True |
| 384c3f89-p000068-l0036 | 7 → 7 | {"missed": 2} | False → True |
| 384c3f89-p000121-l0024 | 18 → 18 | {"apostrophe": true} | True → True |
| 384c3f89-p000205-l0005 | 1 → 1 | {"missed": 2} | False → False |
| 384c3f89-p000205-l0005 | 2 → 2 | {"apostrophe": true} | False → True |
| 384c3f89-p000205-l0005 | 7 → 7 | {"apostrophe": true} | True → True |
| 51fe7386-p000024-l0015 | 1 → 1 | {"missed": 1} | False → True |
| 51fe7386-p000024-l0015 | 2 → 2 | {"missed": 1} | False → True |
| 51fe7386-p000024-l0015 | 29 → 29 | {"missed": 2} | False → True |
| 51fe7386-p000024-l0020 | 6 → 6 | {"missed": 1} | True → True |
| 51fe7386-p000024-l0020 | 8 → 8 | {"missed": 1} | True → True |
| 51fe7386-p000024-l0020 | 11 → 11 | {"missed": 1} | False → True |
| 51fe7386-p000024-l0020 | 20 → 20 | {"missed": 1} | True → True |
| 51fe7386-p000024-l0020 | 37 → 37 | {"missed": 1} | False → True |
| 51fe7386-p000024-l0020 | 39 → 39 | {"missed": 1} | False → True |
| 51fe7386-p000024-l0020 | 23 → 23 | {"false": "letter_part_subscript"} | True → True |
| 602cc72e-p000155-l0009 | 2 → 2 | {"missed": 2} | True → True |
| 602cc72e-p000155-l0009 | 11 → 11 | {"missed": 1} | True → False |
| 602cc72e-p000155-l0009 | 12 → 12 | {"missed": 1} | False → False |
| 602cc72e-p000155-l0009 | 16 → 16 | {"missed": 1} | False → True |
| 602cc72e-p000167-l0027 | 1 → 1 | {"missed": 1} | False → False |
| 602cc72e-p000167-l0027 | 6 → 6 | {"missed": 1} | True → True |
| 602cc72e-p000167-l0027 | 10 → 10 | {"missed": 1} | True → True |
| 602cc72e-p000167-l0027 | 14 → 14 | {"missed": 1} | True → True |
| 8b6b0de9-p000004-l0028 | 2 → 2 | {"missed": 1} | True → True |
| 8b6b0de9-p000004-l0028 | 7 → 7 | {"missed": 2} | True → True |
| 8b6b0de9-p000007-l0030 | 13 → 13 | {"false": "subscript_speck"} | True → True |
| 8b6b0de9-p000008-l0001 | 12 → 12 | {"missed": 2} | True → False |
| 8b6b0de9-p000008-l0001 | 13 → 13 | {"false": "ascender_delta"} | True → True |
| 8b6b0de9-p000008-l0002 | 13 → 13 | {"false": "punctuation_dot"} | True → True |
| 8b6b0de9-p000008-l0019 | 17 → 17 | {"missed": 1} | True → True |
| 8b6b0de9-p000008-l0024 | 4 → 4 | {"missed": 1} | True → True |
| 8b6b0de9-p000008-l0024 | 18 → 18 | {"missed": 1} | True → True |
| 8b6b0de9-p000011-l0007 | 9 → 9 | {"false": "subscript_speck"} | True → True |
| 8b6b0de9-p000011-l0014 | 13 → 13 | {"missed": 1} | False → False |
| 8b6b0de9-p000021-l0007 | 18 → 18 | {"false": "faint_letter"} | True → True |
| 9c1dca9b-p000005-l0017 | 23 → 23 | {"missed": 1} | False → False |
| 9c1dca9b-p000005-l0017 | 27 → 27 | {"missed": 1} | False → False |
| 9c1dca9b-p000015-l0065 | 8 → 8 | {"missed": 1} | False → True |

## All 33 added notes

Complete notes satisfied/certified: 11/33 → 19/33. Individual clauses: 23/51 → 34/51. `owner_examples_expectations.jsonl` records every clause, both S2/S3 slot resolutions, conflicts, ambiguity and before/after checks. Empty notes require no new known-slot error; their owner judgment is not silently converted into new print truth. Ambiguous count syntax stays unresolved. Letter segmentation uses recogniser characters, not mark predictions. S3 has no independent letter-reading certificate, so letter-only baseline clauses remain uncertified rather than borrowing its evaluation base labels.

| line | owner note | S3 → S4 | clauses / unresolved |
|---|---|---|---|
| 02a3a2a6-p000318-l0014 | missed at 1, 17 | False → False | mark [1]: False→False; mark [17]: True→True |
| 2793d64c-p000070-l0010 | missed at 17 | True → True | mark [17]: True→True |
| 384c3f89-p000030-l0010 | missed quote and 2 accents at 1 | False → True | quote [1]: False→True; mark [1]: False→True |
| 384c3f89-p000030-l0029 | missed ellipsis or quote at 1  why the questionamrk at 23? | False → True | leading_sign [1]: False→True; named [23]: True→True |
| 384c3f89-p000050-l0027 | missed accent at 16, missed elipsis at 29 | False → False | mark [16]: False→False; apostrophe [29]: True→True |
| 384c3f89-p000053-l0023 | (empty: preserve correctness) | True → True | no_regression []: True→True |
| 384c3f89-p000068-l0028 | missed ellipsis at 27, | False → True | apostrophe [27]: False→True |
| 384c3f89-p000091-l0014 | missed all accents except 1 | False → False | whole_marks []: False→False |
| 384c3f89-p000091-l0027 | (empty: preserve correctness) | True → True | no_regression []: True→True |
| 384c3f89-p000091-l0029 | missed ellipsis at 14 | False → True | apostrophe [14]: False→True |
| 384c3f89-p000096-l0004 | missed second aaccent at 15 | False → True | mark [15]: False→True |
| 384c3f89-p000096-l0010 | (empty: preserve correctness) | True → True | no_regression []: True→True |
| 384c3f89-p000096-l0031 | missed elipsis at 4 | False → False | apostrophe [4]: False→False |
| 384c3f89-p000121-l0023 | missed ellipsis at 34 and 2 accents at 35 | False → True | apostrophe [34]: True→True; mark [35]: False→True |
| 384c3f89-p000142-l0014 | missed at 9 | True → True | mark [9]: True→True |
| 384c3f89-p000182-l0031 | (empty: preserve correctness) | True → False | no_regression []: True→False |
| 384c3f89-p000183-l0020 | missed sub at 21 | False → False | subscript [21]: False→False |
| 51fe7386-p000024-l0016 | missed 2 at 6, 1 at 11, 1 at 36 | False → False | mark [6]: False→False; mark [11]: True→True; mark [36]: True→True |
| 51fe7386-p000026-l0016 | missed at 1, 25, 12 | False → True | mark [1]: False→True; mark [25]: True→True; mark [12]: True→True |
| 602cc72e-p000353-l0006 | missed at 6, 10, 14 | False → False | mark [6]: False→True; mark [10]: True→True; mark [14]: False→False |
| 8b6b0de9-p000004-l0011 | missed at 2 at 6 | False → False | ambiguous []: False→False [ambiguous] |
| 8b6b0de9-p000004-l0029 | missed at 1, 4, 18 | False → False | mark [1]: False→False; mark [4]: False→False; mark [18]: False→False |
| 8b6b0de9-p000007-l0030 | missed letter classification for στω, and accent at omega | False → False | word_slots []: False→False; word_accent []: False→False |
| 8b6b0de9-p000008-l0002 | missed 9  misread εις as one 1 letter | False → False | mark [9]: True→True; word_slots []: False→False |
| 8b6b0de9-p000008-l0019 | missed at 17 | True → True | mark [17]: True→True |
| 8b6b0de9-p000009-l0024 | missed at 9, 11 | True → True | mark [9]: True→True; mark [11]: True→True |
| 8b6b0de9-p000011-l0014 | missed accent at 13 | False → False | mark [13]: False→False |
| 8b6b0de9-p000012-l0006 | missed at 17 | True → True | mark [17]: True→True |
| 8b6b0de9-p000016-l0029 | misread rho at 7 and 21 | False → True | base [7]: False→True; base [21]: False→True |
| 8b6b0de9-p000018-l0023 | missed accent at 2, missatributed lamba at 6-7 | False → True | mark [2]: True→True; union_base [6, 7]: False→True |
| 8b6b0de9-p000018-l0026 | missed at 2 | False → False | mark [2]: False→False |
| 8b6b0de9-p000021-l0028 | missed at 10 | True → True | mark [10]: True→True |
| 9c1dca9b-p000015-l0062 | missed at 9 | True → True | mark [9]: True→True |

## Requested strings versus native print

The actual supplied crops were inspected at 2× nearest-neighbour scale. `384c3f89-p000096-l0004` now reads `ᾗσι` (dasia + perispomeni + subscript) once over components 24+29. The other three requested strings conflict with the native pixels: `177b717d-p000013-l0009` prints a smooth breathing and acute (`Ἤταν`, not `Ἦταν`); `51fe7386-p000024-l0015` prints `Ὁ Ὄλυμπος … Ὄσσα` (smooth breathing over the two names); `384c3f89-p000068-l0028` has a horizontal arch above the smooth breathing (`ἆσσον`, not `ἂσσον`). The frozen print instrument may disagree and is retained. Actual-crop tests assert the visible readings; a separate per-blob regression proves a low-probability psili+grave pair composes `ἂ`. The literal requested real-crop assertions for those three strings are therefore not claimed to pass. Source crops/alignments are copied into `tests/data/labelfix_s4/` for review.

## Owner readings changed

Before strings render frozen S3 component predictions over the same recogniser letters. They are not Google text and are not a claim that S3 had a standalone reader. Full strings are in `S4_changed_owner_lines.jsonl`.

- `8b6b0de9-p000004-l0011`: διότι έ̓σχιζεν εὐρὺ → διότι ἔσχιζεν εὐρὺ
- `8b6b0de9-p000008-l0002`: εις ᾴ̔δου ὰ̓ν ἡγῆσαι ! → “εις ᾷδου ἂν ἡγῆσαι !
- `8b6b0de9-p000008-l0019`: εις στεναγμὀν διακαῆ, → εις στεναγμὸν διακαῆ,
- `8b6b0de9-p000004-l0028`: βῆμα την έ̓κρουε βαρύ → βῆμα την ἔκρουε βαρύ
- `9c1dca9b-p000015-l0062`: Στοὺς πενῆντα για βουλὴ̓ → Στοὐς πενῆντα γιὰ βουλη
- `2793d64c-p000070-l0014`: ἠχὼ στενάξασα θρηνῳδός, → ηχὼ στενάξασᾶ θρηνῳδός,
- `8b6b0de9-p000018-l0023`: Πᾶσα πληγη αἱματηρἁ → Πᾶσα πληγἠ αἱματηρὰ
- `9c1dca9b-p000015-l0065`: καὶ μαγκού̔ρες περμαζώνει. → καὶ μαγκοῦρες περμαζώνει.
- `602cc72e-p000353-l0006`: Χελιδων καὶ κορώ̓νη → Χελιδὼν καὶ κορωνῆ
- `2793d64c-p000070-l0010`: τρανῶς ἀνῳμωξεν ἐκ καρδίας, → τρανῶς ἀνᾧμωξεν ἐκ καρδίας,
- `8b6b0de9-p000018-l0026`: Δεν ειναι ά̓νθρωποι, οὺρὰ → Δεν ειναι ἄνθρωποι, οὺρὰ
- `8b6b0de9-p000008-l0001`: « Καὶ εις τὸν ᾴ̔δην μετὰ σοῦ, → Καὶ εις τὸν ᾇδην μετὰ σοῦ,
- `602cc72e-p000155-l0009`: Εύ̓νουχος καὶ ί̓ερεὺ̓ς. → Εὔνουχος καἰ ἶερεύς.
- `02a3a2a6-p000046-l0025`: “ καὶ νὰ γενῇς Σπαλάγγι !” → “καὶ νὰ γενῇς Σπαλάγγι !”
- `177b717d-p000097-l0007`: ὀ Σηκουάνας πό̓χει πνίξει, → ὀ Σηκουάνας πὄχει πνίξει,
- `177b717d-p000013-l0009`: Ηταν εὐτυχισμενη τότε ἡ ώ̓ρα, → Ἤταν εὐτυχισμενη τότε ἡ ὥρα,
- `177b717d-p000097-l0010`: «Ω, τί ζέστη, Θεέ μου, βράζει !» → Ὤ, τί ζέστη, Θεέ μου, βράζει !»
- `384c3f89-p000096-l0004`: δωσέμεναι, ό̔ κεν ῇσι μετὰ φρεσὶν ἰθύσειεν. → δωσέμεναι, ὅ κεν ᾗσι μετὰ φρεσὶν ἰθύσειεν.
- `51fe7386-p000026-l0016`: Εμπρὸς τρισκότειδο καὶ πί̓σω ἐχθροι. → Ἐμπρὸς τρισκότειδο καἶ πἷσω ἐχθροι.
- `384c3f89-p000068-l0036`: αύ̓τως δ Αρητος μενεδήιον Εὐρύτου υια → αὔτως δ’ Ἄρητος μενεδήιον Εὐρύτου υια
- `384c3f89-p000096-l0010`: υῖ̓ες, Δηιλέων τε καὶ Αὐτόλυκος Φλογίος τε → υἷες, Δηιλέων τε καὶ Αὐτόλυκος Φλογίος τε
- `384c3f89-p000053-l0023`: Κύζικον ἐν κονίησι και αί̔ματι πεπτηῶτα. → Κύζικον ἐν κονίησι και αἵματι πεπτηῶτα.
- `51fe7386-p000024-l0015`: Ο Ολυμπος ὲκύτταξε τὴν ώμορφη τὴν Οσσα, → Ὁ Ὄλυμπος ὲκύτταξε τὴν ὤμορφη τἡν Ὄσσα,
- `384c3f89-p000030-l0029`:  Ει μὲν δή μοι κῦδος ἐπιτρωπἁτε μέλεσθαι, → “Ει μὲν δή μοι κὓδος ἐπιτρωπἁτε μέλεσθαι,
- `384c3f89-p000096-l0031`: τόσσ ἐπὶ γαιαν ίήσι παρὲξ έθεν ά̓νδιχα βαλλων. → τόσσ ἐπὶ γαιαν ἵησι παρὲξ ἕθεν ἄνδιχα βαλλων.
- `384c3f89-p000121-l0024`: οῖ̓ος, ἐπεὶ μεσσηγυς έ̓τ’ αὐτόθι νεῦσε λιπέσθαι → οιος, ἐπεὶ μεσσηγυς ἔτ’ αὐτόθι νεῦσε λιπέσθαι
- `384c3f89-p000053-l0028`: ή θέμις, ὰ̓μ πεδίον λειμώνιον, έ̓νθ’ έ̓τι νυν περ → ἣ θέμις, α̈́μ πεδίον λειμώνιον, ἔνθ’ ἔτι νυν περ
- `384c3f89-p000053-l0021`: ἀμπλακίην ά̓μφω· στυγερὸν δ’ ά̓χος εῖ̓λεν ἰδόντας → ἀμπλακίην ἄμφω· στυγερὸν δ’ ἄχος εἷλεν ἰδόντας
- `384c3f89-p000183-l0020`: άλλοτε παρβολάδην, ναυτησι δὲ χάρμα τέτυκται· → ἄλλοτε παρβολάδην, ναυτησι δὲ χάρμα τέτυκται·
- `384c3f89-p000030-l0010`: Αλλα μὲν όσσα τε νηὶ ἐφοπλίσσασθαι έ̓οικεν → “Ἄλλα μὲν ὅσσα τε νηὶ ἐφοπλίσσασθαι ἔοικεν
- `384c3f89-p000205-l0005`: Η ῥ, άμα δ’ εὐχωλῆσιν ἐς ύδατα λαιμοτομησας → Ἠ ῥ’, ἅμα δ’ εὐχωλῆσιν ἐς ὕδατα λαιμοτομήσας
- `384c3f89-p000068-l0028`: πλῆξε, καὶ ἐν κονίῃσι βάλεν· τοῦ δ ἀσσον ἰόντος → πλῆξε, καὶ ἐν κονίῃσι βάλεν· τοῦ δ’ ἆσσον ἰόντος
- `384c3f89-p000182-l0031`: σχέτλιος. ὴ̓ τέ οἱ αιψα καταυτόθι νόστον ἀπηύρων, → σχέτλιος. ἣ τέ οἱ αιψα καταυτόθι νόστον ἀπηύρων,
- `51fe7386-p000024-l0020`: Και δὲν ἐπέ̓ρασε καιρὸς, χρόνοι πολλοὶ καἱ μηνες → Και δὲν ἐπέρασε καιρὸς, χρὁνοι πολλοὶ καὶ μῆνες
- `384c3f89-p000142-l0014`: πάμπαν ἐύρρηνός τε καὶ εύ̓βοτος, ένθα Προμηθεὺς → πάμπαν ἐύρρηνός τε καὶ εὔβοτος, ἔνθα Προμηθεὺς
- `384c3f89-p000091-l0029`: δῶρα φέρειν· άμα δ υία δόμων έ̓κπεμπε νέεσθαι. → δῶρα φέρειν· ἅμα δ’ υἳα δόμων ἔκπεμπε νέεσθαι.
- `384c3f89-p000121-l0023`: Αὐγείης Τελαμών τε παρασχεδόν· εί̔πετο δ’ Αργος → Αὐγείης Τελαμών τε παρασχεδόν· εἵπετο δ’ Ἄργος
- `384c3f89-p000030-l0021`: σημαίνειν ἐπέτελλον· ὁ δ’ αὐτόθεν, έ̓νθα περ ηστο, → σημαίνειν ἐπέτελλον· ὁ δ’ αὐτόθεν, ἔνθα περ ἥστο,
- `9c1dca9b-p000005-l0017`: Συθιστορια Ιουλιου Κλαρετῆ. -Μεταφρασις Χ. Α. → Συθιστορἱα Ιουλἰου Κλαρετῆ. -Μετἁφρασις Χ. Α.
- `384c3f89-p000091-l0014`: αννδρασι, εὐτ αρξωσινν αρειονες αλλοι οελλειν. → αννδρασι, εὖτ αρξωσινν αρειονες αλλοι οελλειν.

## Verification and limitations

Final full suite: 3,363 passed, 19 skipped, 5 failures and 6 setup errors. The five setup errors in apply_clean lack `docs/records/harvest/collection/v2/admitted_all_v2.jsonl`; the sixth is the sandbox-forbidden localhost capture bind. Three collection-output failures concern missing frozen harvest budget/index inputs; the other two concern an existing uninventoried `parliament_resolution.json` and an existing four-line API example where the API test requires two lines. Those files/tests are unchanged. All 124 runnable labelfix tests pass, including 11 S4 tests; one existing socket test is deselected in that focused run. Exact commands/logs, hashes and elapsed time are in `S4_verification.json`, `S4_pytest_full.txt` and `S4_inputs.json`. All-existing-tests-green is not achieved in this checkout. Unresolved connected-letter ownership remains flagged; it is not repaired by substituting Google letters. Overall held-out precision exceeds S3; smaller-stratum and owner regressions below remain open.

This candidate is not qualified under the no-empty-note-regression requirement: `384c3f89-p000182-l0031`, slot 8, changes one false compound identity to another. Empty-note checks reject any newly introduced false identity or lost true mark, even when the old slot was already wrong against the frozen print instrument. The native-string conflicts above also leave three literal requested real-crop assertions unmet.

Regressions: held-out accent recall 95.2%→94.8%; held-out breathing precision 95.6%→94.4%; DEV precision 95.6%→94.3%; DEV f1 92.8%→92.7%; DEV accent precision 95.3%→94.5%; DEV accent recall 96.9%→96.5%; DEV accent f1 96.1%→95.5%; DEV breathing precision 96.8%→96.3%; DEV compound precision 93.0%→87.1%; DEV compound f1 89.9%→87.8%; DEV dialytika precision 100.0%→11.1%; DEV dialytika f1 50.0%→16.7%; all ascender false 0.2%→0.3%; held-out ascender false 0.2%→0.4%; class circumflex precision 87.7%→87.1%; class circumflex recall 96.7%→89.1%; class dasia precision 89.2%→88.3%; class grave recall 96.2%→95.5%; class psili precision 97.4%→97.1%; class psili+circumflex precision 76.9%→71.4%; atomic accent precision 93.9%→93.8%; atomic breathing precision 91.5%→91.3%; old owner expectations lost 602cc72e-p000155-l0009:11,8b6b0de9-p000008-l0001:12; empty-note new errors 384c3f89-p000182-l0031:8.

S4 RESULT: held-out P 91.4%→93.5% R 86.3%→91.9%; capitals R 0.0%→86.0%; stacked/compound R 62.4%→89.1%; owner expectations fixed 46/59 (S3 35/59); regressions: held-out accent recall 95.2%→94.8%; held-out breathing precision 95.6%→94.4%; DEV precision 95.6%→94.3%; DEV f1 92.8%→92.7%; DEV accent precision 95.3%→94.5%; DEV accent recall 96.9%→96.5%; DEV accent f1 96.1%→95.5%; DEV breathing precision 96.8%→96.3%; DEV compound precision 93.0%→87.1%; DEV compound f1 89.9%→87.8%; DEV dialytika precision 100.0%→11.1%; DEV dialytika f1 50.0%→16.7%; all ascender false 0.2%→0.3%; held-out ascender false 0.2%→0.4%; class circumflex precision 87.7%→87.1%; class circumflex recall 96.7%→89.1%; class dasia precision 89.2%→88.3%; class grave recall 96.2%→95.5%; class psili precision 97.4%→97.1%; class psili+circumflex precision 76.9%→71.4%; atomic accent precision 93.9%→93.8%; atomic breathing precision 91.5%→91.3%; old owner expectations lost 602cc72e-p000155-l0009:11,8b6b0de9-p000008-l0001:12; empty-note new errors 384c3f89-p000182-l0031:8
