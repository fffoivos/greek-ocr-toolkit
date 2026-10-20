# S5 — case-aware detector candidate

CPU only, offline, cached alignments, zero CTC forward passes. Changes remain in the worktree; no git writes or owner-page builds. Start HEAD `28aac666bf8e5c0e0e4cafdfd549712af2a7ed6a`. Baseline first: `S5_baseline_owner_checks.json` was written before detector changes: S4 27/56 examples, 22/33 review notes, 46/59 earlier expectations. Baseline comes from the frozen S4 line predictions and S4 model; aggregate TP/FP/FN equality is asserted. Every S4 line, component slot, unknown truth, and held-out book is retained in order.

Runtime reads recogniser letters and pixel marks only. The C1 pixel classifier uses baseline-relative height, width, descender depth, stroke thickness, occupancy, holes and an 8×8 shape grid. Agreement labels include case. The recogniser contributes a bounded case prior; raw pixel class, probability, recogniser case and disagreement remain visible. Reading preserves the recogniser base characters even when case disagrees. Every letter/large component receives a case class; ambiguous character ownership remains flagged.

Word bands use complete lowercase-body components, excluding classified capitals, ascenders and descenders. A word with fewer than two reliable bodies borrows the line body band; a line without four reliable bodies keeps the frozen band and records the fallback. Runs with at least 80% classified capitals receive their own height band. Capitals use their own top for the mark zone and left-gap search; recognised vowels retain attached-mark extraction even when their body shape is descender-like (notably eta). This avoids confusing a descender body with absence of a top mark.

The first DEV audit showed over-vetoing of joined marks on eta and accented vowels classified as ascenders. That veto was narrowed to non-vowel bodies. No model or thresholds were fitted to held-out marks. The result remains a candidate; the requested no-regression and naming goals are assessed below.

## Frozen held-out table: 666 lines, 14 books

| kind | S4 P | S5 P | S4 R | S5 R | S4 F1 | S5 F1 |
|---|---:|---:|---:|---:|---:|---:|
| total | 93.5% | 93.7% | 91.9% | 91.6% | 92.7% | 92.7% |
| accent | 95.8% | 95.7% | 94.8% | 94.6% | 95.3% | 95.2% |
| breathing | 94.4% | 94.2% | 93.5% | 93.1% | 93.9% | 93.7% |
| compound | 80.5% | 80.9% | 89.1% | 88.2% | 84.6% | 84.4% |
| subscript | 97.7% | 97.7% | 44.7% | 44.7% | 61.3% | 61.3% |
| dialytika | 0.0% | — | 0.0% | 0.0% | 0.0% | 0.0% |
| apostrophe | 99.4% | 99.4% | 81.1% | 81.1% | 89.3% | 89.3% |
| capital detection P | 36.6% | 95.6% | — | — | — | — |
| capital detection R | — | — | 100.0% | 98.7% | — | — |
| marks-at-capitals naming accuracy | 86.0% | 87.1% | — | — | — | — |

Capital truth: 18960 held-out slots where Google and recogniser base letters agree exactly, including case, ignoring marks; 1189 capitals. This is the requested agreement stratum, not recogniser uppercase used as truth by itself. Raw pixel-only P/R 83.2%/45.3%; pixel/recogniser disagreements 753/18952. Slot receipt: `S5_capital_truth.jsonl`. Capital marked-slot support 93; mark P/R 92.0%/86.0% → 94.2%/87.1%. Naming accuracy requires the entire mark set, counting missed sets wrong.

## Class balance and S4 regressions

Hypothesis tested before detector edits and rejected: C1 has more dialytika and compounds proportionally than DEV. No rebalance on that unsupported premise. Counts are all available samples before bounding; S4 also uses square-root inverse-frequency weighting. Existing S4 mark weights are retained, so the old naming regressions are not claimed recovered by retraining. Dialytika predictions now require the physical two-dot shape.

| class | DEV | C1 | total |
|---|---:|---:|---:|
| acute | 640 | 8785 | 9425 |
| acute+subscript | 0 | 40 | 40 |
| circumflex | 272 | 4112 | 4384 |
| circumflex+subscript | 21 | 681 | 702 |
| dasia | 125 | 2727 | 2852 |
| dasia+acute | 34 | 1130 | 1164 |
| dasia+acute+subscript | 0 | 7 | 7 |
| dasia+circumflex | 1 | 940 | 941 |
| dasia+circumflex+subscript | 0 | 213 | 213 |
| dasia+grave | 0 | 814 | 814 |
| dialytika | 3 | 448 | 451 |
| dialytika+acute | 0 | 177 | 177 |
| grave | 449 | 6552 | 7001 |
| none | 2618 | 45472 | 48090 |
| psili | 339 | 5733 | 6072 |
| psili+acute | 68 | 1232 | 1300 |
| psili+acute+subscript | 0 | 8 | 8 |
| psili+circumflex | 17 | 718 | 735 |
| psili+circumflex+subscript | 0 | 5 | 5 |
| psili+grave | 10 | 740 | 750 |
| psili+subscript | 0 | 18 | 18 |
| subscript | 17 | 600 | 617 |

DEV dialytika support is 3 slots; held-out is 4. Supplementary C1 agreement naming diagnostic: 625 slots, 362 exact classifications. These samples were used to train S4; this is explicitly an in-sample shape diagnostic, not independent accuracy. No new crops or held-out books were fitted.

| regression check | S3 | S4 | S5 |
|---|---:|---:|---:|
| DEV compound P | 93.0% | 87.1% | 81.0% |
| psili+circumflex P | 76.9% | 71.4% | 78.3% |
| circumflex R | 96.7% | 89.1% | 88.4% |
| DEV dialytika P | 100.0% | 11.1% | — |

These are classifier/feature-context failures, not rare-class scarcity: S4 retained 730 psili+circumflex, 1,729 circumflex, 450 dialytika fit examples. Feature normalisation and whole-set/per-blob composition can change a label despite identical physical evidence. Per-class exact-set results and the complete before/after evidence are retained in `S5_metrics.json` and `S5_lines.jsonl.gz`.

One-line causes of the named S4 losses (unchanged frozen truth):

- `602cc72e-p000155-l0009:11`: the attached tall oblique at bbox [478,8,489,30] is named psili rather than printed grave; localisation recovered the blob, but naming lost the expectation.
- `8b6b0de9-p000008-l0001:12`: the fused attached blob [417,4,442,26] is named dasia+circumflex rather than dasia+acute; the subscript is retained, so this is accent identity, not missing mark detection.
- `384c3f89-p000182-l0031:8`: S4 names the two blobs dasia+grave where frozen truth says psili+circumflex; S3 was already wrong, but S4 introduced a different false identity, violating the S3 empty-note preservation gate. The S5 baseline preservation gate separately compares against S4.

## Per-class held-out exact sets

| class | support | S4 P/R | S5 P/R |
|---|---:|---|---|
| acute | 1418 | 99.2%/95.6% | 99.0%/95.4% |
| acute+subscript | 2 | 100.0%/50.0% | 100.0%/50.0% |
| circumflex | 303 | 87.1%/89.1% | 86.2%/88.4% |
| circumflex+subscript | 39 | 100.0%/41.0% | 100.0%/41.0% |
| dasia | 223 | 88.3%/91.0% | 87.8%/90.1% |
| dasia+acute | 102 | 87.0%/98.0% | 87.0%/98.0% |
| dasia+acute+subscript | 0 | —/— | —/— |
| dasia+circumflex | 18 | 55.6%/55.6% | 52.6%/55.6% |
| dasia+circumflex+subscript | 3 | 50.0%/33.3% | 50.0%/33.3% |
| dasia+grave | 7 | 11.6%/71.4% | 10.9%/71.4% |
| dasia+grave+subscript | 0 | —/— | —/— |
| dialytika | 1 | 0.0%/0.0% | —/0.0% |
| dialytika+acute | 3 | 0.0%/0.0% | —/0.0% |
| grave | 661 | 98.4%/95.5% | 98.4%/95.2% |
| none | 14228 | 99.2%/99.6% | 99.1%/99.6% |
| psili | 646 | 97.1%/94.0% | 96.8%/93.8% |
| psili+acute | 268 | 94.5%/95.9% | 95.9%/95.1% |
| psili+acute+subscript | 1 | —/0.0% | —/0.0% |
| psili+circumflex | 40 | 71.4%/50.0% | 78.3%/45.0% |
| psili+circumflex+subscript | 0 | —/— | —/— |
| psili+grave | 11 | 36.8%/63.6% | 36.8%/63.6% |
| psili+grave+subscript | 0 | —/— | —/— |
| psili+subscript | 0 | —/— | —/— |
| subscript | 49 | 100.0%/49.0% | 100.0%/49.0% |

## Ascender false marks

| split | slots | S4 | S5 |
|---|---:|---:|---:|
| all | 3558 | 12 (0.3%) | 14 (0.4%) |
| held-out | 2488 | 10 (0.4%) | 10 (0.4%) |

## All owner checks

All 56 current example records and all 33 review notes are checked; review `printed` prefills are never read. The original 59 preserve their v8 overlap resolution. Examples resolve letter-component slots against both S2 and S3; differing resolutions and qualitative ambiguous notes fail certification rather than invent truth. Empty notes require no lost true mark or new false identity against S4.

| set | S4 | S5 |
|---|---:|---:|
| earlier | 46/59 | 45/59 |
| examples | 27/56 | 26/56 |
| review | 22/33 | 21/33 |

### examples: every note

| line | note | S4 → S5 |
|---|---|---|
| 02a3a2a6-p000041-l0005 | unified λο  missed at 24, subscirpt at 28 | False → False |
| 02a3a2a6-p000046-l0014 | missed ellipsis at 8 | False → False |
| 02a3a2a6-p000307-l0003 | missed ellispis at 2, 15 | False → False |
| 02a3a2a6-p000318-l0014 | missed at 1, 17 | False → False |
| 02a3a2a6-p000318-l0017 | missed at 2 (confusion due to capital theta at 1) | True → True |
| 177b717d-p000017-l0012 | missed at 11, 12 | True → False |
| 177b717d-p000097-l0010 | missed at 2, 5 | True → True |
| 2793d64c-p000033-l0022 | missed at 1, ellispis at 11 | False → False |
| 2793d64c-p000070-l0010 | missed at 17 | True → True |
| 384c3f89-p000030-l0010 | missed quote and 2 accents at 1 | True → True |
| 384c3f89-p000030-l0029 | missed ellipsis or quote at 1  why the questionamrk at 23? | True → True |
| 384c3f89-p000050-l0016 | classified 2 accents as 1 at 5, missed at 19 | False → False |
| 384c3f89-p000050-l0027 | missed accent at 16, missed elipsis at 29 | False → False |
| 384c3f89-p000053-l0023 |  | True → True |
| 384c3f89-p000068-l0028 | missed ellipsis at 27, | True → True |
| 384c3f89-p000068-l0036 | missed ellipsis at 6, and 2 accens at 7 missed 1 at 30 | False → False |
| 384c3f89-p000091-l0014 | missed all accents except 1 | False → False |
| 384c3f89-p000091-l0027 | missed 2 accents at 1, and classified eta as 1-2 | False → False |
| 384c3f89-p000091-l0029 | missed ellipsis at 14 | True → True |
| 384c3f89-p000096-l0004 | missed second aaccent at 15 | True → True |
| 384c3f89-p000096-l0010 |  | True → True |
| 384c3f89-p000096-l0031 | missed elipsis at 4 | False → False |
| 384c3f89-p000121-l0023 | missed ellipsis at 34 and 2 accents at 35 | True → True |
| 384c3f89-p000142-l0010 | missed subscript at 14 | False → False |
| 384c3f89-p000142-l0014 | missed at 9 | True → True |
| 384c3f89-p000170-l0024 | missed subscript at 12 | False → False |
| 384c3f89-p000182-l0023 | missed ellipsis at 3 | True → True |
| 384c3f89-p000182-l0031 |  | True → True |
| 384c3f89-p000183-l0009 | missed second accent at 9 | False → False |
| 384c3f89-p000183-l0020 | missed sub at 21 | False → False |
| 384c3f89-p000183-l0022 | missed ellipsis at 20 | True → True |
| 51fe7386-p000024-l0015 | missed quote at 1,  missed at 2, 29 | False → False |
| 51fe7386-p000024-l0016 | missed 2 at 6, 1 at 11, 1 at 36 | False → False |
| 51fe7386-p000026-l0016 | missed at 1, 25, 12 | True → True |
| 602cc72e-p000113-l0009 | missed at 1, 9, 10, 12 | True → True |
| 602cc72e-p000167-l0027 | missed at 6, 10 , 14 | True → True |
| 602cc72e-p000353-l0006 | missed at 6, 10, 14 | False → False |
| 8b6b0de9-p000004-l0011 | missed at 2 at 6 | False → False |
| 8b6b0de9-p000004-l0029 | missed at 1, 4, 18 | False → False |
| 8b6b0de9-p000007-l0011 | missed at 1 and 2, 4 | False → False |
| 8b6b0de9-p000007-l0021 | missed at 4, 18 | False → False |
| 8b6b0de9-p000007-l0030 | missed letter classification for στω, and accent at omega | False → False |
| 8b6b0de9-p000008-l0001 | missed at 7, 12 | False → False |
| 8b6b0de9-p000008-l0002 | missed 9  misread εις as one 1 letter | False → False |
| 8b6b0de9-p000008-l0019 | missed at 17 | True → True |
| 8b6b0de9-p000009-l0024 | missed at 9, 11 | True → True |
| 8b6b0de9-p000011-l0014 | missed accent at 13 | False → False |
| 8b6b0de9-p000012-l0006 | missed at 17 | True → True |
| 8b6b0de9-p000016-l0013 | missed at 3, 5 | False → False |
| 8b6b0de9-p000016-l0029 | misread rho at 7 and 21 | True → True |
| 8b6b0de9-p000018-l0023 | missed accent at 2, missatributed lamba at 6-7 | True → True |
| 8b6b0de9-p000018-l0026 | missed at 2 | False → False |
| 8b6b0de9-p000021-l0028 | missed at 10 | True → True |
| 9c1dca9b-p000005-l0017 | missed at 9, 14, 23, 27 | False → False |
| 9c1dca9b-p000015-l0062 | missed at 9 | True → True |
| 9c1dca9b-p000015-l0065 | missed at 8 | True → True |

### review: every note

| line | note | S4 → S5 |
|---|---|---|
| 02a3a2a6-p000046-l0014 | accent of 8 missed | False → False |
| 02a3a2a6-p000046-l0025 | dot of exclamation mark is detected | True → True |
| 177b717d-p000013-l0009 | missed 2 at 1, one at 13 | False → False |
| 177b717d-p000097-l0007 | random mark under 19 | True → True |
| 177b717d-p000097-l0010 | missed two at 2, one at 5 | True → True |
| 2793d64c-p000048-l0004 | iota is missed | False → False |
| 2793d64c-p000048-l0010 | random dot under 6 | True → True |
| 2793d64c-p000070-l0010 | 22 delta is detected | True → True |
| 2793d64c-p000070-l0014 | random marks under 10 and 13, and over 12 | False → False |
| 2793d64c-p000072-l0007 | careful on the ellipsis at 3 | True → True |
| 384c3f89-p000030-l0021 | ellipsis at 22 missed | True → True |
| 384c3f89-p000030-l0029 | missed 1's accent | False → False |
| 384c3f89-p000053-l0021 | 2 accents missed at 10, and 1 at 32, also ellipsis of 22 | True → True |
| 384c3f89-p000053-l0028 | accents of 25 missed | True → True |
| 384c3f89-p000068-l0036 | ellispis after 6 missed, 2 accents of 7 missed | True → True |
| 384c3f89-p000091-l0039 |  | True → True |
| 384c3f89-p000121-l0024 | ellipsis missed at 18 | True → True |
| 384c3f89-p000205-l0005 | 2 accent of 1 missed, 1 ellipsis at 2 and 7 respectively | False → False |
| 51fe7386-p000024-l0015 | 3 accents of 1 and 2 missed, 2 of 29 missed | True → True |
| 51fe7386-p000024-l0020 | missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript | True → False |
| 602cc72e-p000155-l0009 | missed two at 2, and one at 11, 12, and 16 | False → False |
| 602cc72e-p000167-l0027 | missed 1 at 1, 6, 10, and 14 | False → False |
| 8b6b0de9-p000004-l0028 | missed accent at 2 ,and 2 at 7 | True → True |
| 8b6b0de9-p000007-l0030 | random mark under lambda | True → True |
| 8b6b0de9-p000008-l0001 | 2 accents over 12 missed, delta 13 detected | False → False |
| 8b6b0de9-p000008-l0002 | dot of exclamation mark is detected | True → True |
| 8b6b0de9-p000008-l0019 | missed accent at 17 | True → True |
| 8b6b0de9-p000008-l0024 | missed at 4 and 18 | True → True |
| 8b6b0de9-p000011-l0007 | random dot under 9 | True → True |
| 8b6b0de9-p000011-l0014 | missed 13 | False → False |
| 8b6b0de9-p000021-l0007 | faint eta at 18 is detected as accent | True → True |
| 9c1dca9b-p000005-l0017 | very blurry and merged accents at 23 and 27 | False → False |
| 9c1dca9b-p000015-l0065 | missed 8 | True → True |

### Earlier 59 expectations

| line:slot | S4 → S5 |
|---|---|
| 02a3a2a6-p000046-l0014:8 | False → False |
| 02a3a2a6-p000046-l0025:18 | True → True |
| 177b717d-p000013-l0009:1 | True → True |
| 177b717d-p000013-l0009:13 | False → False |
| 177b717d-p000097-l0007:19 | True → True |
| 177b717d-p000097-l0010:2 | True → True |
| 177b717d-p000097-l0010:5 | True → True |
| 2793d64c-p000048-l0004:19 | False → False |
| 2793d64c-p000048-l0010:6 | True → True |
| 2793d64c-p000070-l0010:22 | True → True |
| 2793d64c-p000070-l0014:10 | True → True |
| 2793d64c-p000070-l0014:13 | True → True |
| 2793d64c-p000070-l0014:12 | False → False |
| 2793d64c-p000072-l0007:3 | True → True |
| 384c3f89-p000030-l0021:22 | True → True |
| 384c3f89-p000030-l0029:1 | False → False |
| 384c3f89-p000053-l0021:10 | True → True |
| 384c3f89-p000053-l0021:32 | True → True |
| 384c3f89-p000053-l0021:22 | True → True |
| 384c3f89-p000053-l0028:25 | True → True |
| 384c3f89-p000068-l0036:6 | True → True |
| 384c3f89-p000068-l0036:7 | True → True |
| 384c3f89-p000121-l0024:18 | True → True |
| 384c3f89-p000205-l0005:1 | False → False |
| 384c3f89-p000205-l0005:2 | True → True |
| 384c3f89-p000205-l0005:7 | True → True |
| 51fe7386-p000024-l0015:1 | True → True |
| 51fe7386-p000024-l0015:2 | True → True |
| 51fe7386-p000024-l0015:29 | True → True |
| 51fe7386-p000024-l0020:6 | True → True |
| 51fe7386-p000024-l0020:8 | True → True |
| 51fe7386-p000024-l0020:11 | True → True |
| 51fe7386-p000024-l0020:20 | True → True |
| 51fe7386-p000024-l0020:37 | True → False |
| 51fe7386-p000024-l0020:39 | True → True |
| 51fe7386-p000024-l0020:23 | True → True |
| 602cc72e-p000155-l0009:2 | True → True |
| 602cc72e-p000155-l0009:11 | False → False |
| 602cc72e-p000155-l0009:12 | False → False |
| 602cc72e-p000155-l0009:16 | True → True |
| 602cc72e-p000167-l0027:1 | False → False |
| 602cc72e-p000167-l0027:6 | True → True |
| 602cc72e-p000167-l0027:10 | True → True |
| 602cc72e-p000167-l0027:14 | True → True |
| 8b6b0de9-p000004-l0028:2 | True → True |
| 8b6b0de9-p000004-l0028:7 | True → True |
| 8b6b0de9-p000007-l0030:13 | True → True |
| 8b6b0de9-p000008-l0001:12 | False → False |
| 8b6b0de9-p000008-l0001:13 | True → True |
| 8b6b0de9-p000008-l0002:13 | True → True |
| 8b6b0de9-p000008-l0019:17 | True → True |
| 8b6b0de9-p000008-l0024:4 | True → True |
| 8b6b0de9-p000008-l0024:18 | True → True |
| 8b6b0de9-p000011-l0007:9 | True → True |
| 8b6b0de9-p000011-l0014:13 | False → False |
| 8b6b0de9-p000021-l0007:18 | True → True |
| 9c1dca9b-p000005-l0017:23 | False → False |
| 9c1dca9b-p000005-l0017:27 | False → False |
| 9c1dca9b-p000015-l0065:8 | True → True |

## Owner height-band changes

Every owner slot, class, old/new meanline, word x-height, and fallback reason is recorded in `S5_owner_bands.jsonl`. Per-line ranges below exclude unavailable ownership.

| line | S4 xh | S5 word xh range | capital bands |
|---|---:|---|---:|
| 02a3a2a6-p000041-l0005 | 29.00 | 28.00–29.00 | 2 |
| 02a3a2a6-p000046-l0014 | 29.00 | 29.00–29.00 | 1 |
| 02a3a2a6-p000046-l0025 | 28.00 | 27.00–28.00 | 1 |
| 02a3a2a6-p000307-l0003 | 29.00 | 28.00–29.00 | 0 |
| 02a3a2a6-p000318-l0014 | 27.00 | 27.00–30.00 | 2 |
| 02a3a2a6-p000318-l0017 | 29.00 | 29.00–30.00 | 1 |
| 177b717d-p000013-l0009 | 33.50 | 32.00–34.00 | 1 |
| 177b717d-p000017-l0012 | 33.00 | 33.00–35.00 | 3 |
| 177b717d-p000097-l0007 | 33.50 | 33.00–33.00 | 1 |
| 177b717d-p000097-l0010 | 32.00 | 33.50–34.00 | 2 |
| 2793d64c-p000033-l0022 | 35.50 | 35.00–36.50 | 1 |
| 2793d64c-p000048-l0004 | 36.00 | 35.50–37.00 | 0 |
| 2793d64c-p000048-l0010 | 36.00 | 36.00–38.00 | 0 |
| 2793d64c-p000070-l0010 | 36.00 | 36.00–38.00 | 0 |
| 2793d64c-p000070-l0014 | 37.00 | 37.00–37.00 | 0 |
| 2793d64c-p000072-l0007 | 61.00 | 61.00–61.00 | 0 |
| 384c3f89-p000030-l0010 | 30.00 | 30.00–30.50 | 1 |
| 384c3f89-p000030-l0021 | 30.50 | 30.00–31.00 | 0 |
| 384c3f89-p000030-l0029 | 30.00 | 30.00–31.00 | 0 |
| 384c3f89-p000050-l0016 | 31.00 | 31.00–32.00 | 2 |
| 384c3f89-p000050-l0027 | 31.00 | 31.00–32.50 | 0 |
| 384c3f89-p000053-l0021 | 31.50 | 31.00–32.00 | 0 |
| 384c3f89-p000053-l0023 | 30.00 | 30.00–32.00 | 1 |
| 384c3f89-p000053-l0028 | 32.00 | 31.00–32.00 | 0 |
| 384c3f89-p000068-l0028 | 30.00 | 30.00–31.00 | 0 |
| 384c3f89-p000068-l0036 | 30.00 | 29.00–30.50 | 2 |
| 384c3f89-p000091-l0014 | 19.00 | 19.00–19.00 | 3 |
| 384c3f89-p000091-l0027 | 31.00 | 29.00–31.00 | 0 |
| 384c3f89-p000091-l0029 | 30.00 | 29.00–30.50 | 0 |
| 384c3f89-p000091-l0039 | 31.00 | 30.50–31.00 | 0 |
| 384c3f89-p000096-l0004 | 30.00 | 30.00–31.00 | 0 |
| 384c3f89-p000096-l0010 | 30.00 | 29.00–31.00 | 3 |
| 384c3f89-p000096-l0031 | 30.50 | 29.00–31.00 | 0 |
| 384c3f89-p000121-l0023 | 31.00 | 30.00–32.00 | 3 |
| 384c3f89-p000121-l0024 | 31.00 | 30.00–31.50 | 0 |
| 384c3f89-p000142-l0010 | 30.00 | 30.00–31.00 | 1 |
| 384c3f89-p000142-l0014 | 30.00 | 30.00–31.00 | 1 |
| 384c3f89-p000170-l0024 | 30.00 | 30.00–30.50 | 0 |
| 384c3f89-p000182-l0023 | 31.00 | 30.50–31.00 | 0 |
| 384c3f89-p000182-l0031 | 30.50 | 30.00–31.00 | 0 |
| 384c3f89-p000183-l0009 | 31.00 | 30.00–31.00 | 0 |
| 384c3f89-p000183-l0020 | 31.00 | 30.50–31.50 | 0 |
| 384c3f89-p000183-l0022 | 30.50 | 30.00–31.00 | 2 |
| 384c3f89-p000205-l0005 | 31.00 | 30.00–32.00 | 1 |
| 51fe7386-p000024-l0015 | 35.00 | 33.00–35.00 | 3 |
| 51fe7386-p000024-l0016 | 34.00 | 34.00–36.00 | 1 |
| 51fe7386-p000024-l0020 | 35.00 | 34.00–54.00 | 2 |
| 51fe7386-p000026-l0016 | 35.00 | 34.00–35.50 | 1 |
| 602cc72e-p000113-l0009 | 33.30 | 33.00–34.00 | 1 |
| 602cc72e-p000155-l0009 | 31.00 | 30.50–31.00 | 2 |
| 602cc72e-p000167-l0027 | 32.00 | 31.50–32.00 | 2 |
| 602cc72e-p000353-l0006 | 31.00 | 31.50–33.00 | 1 |
| 8b6b0de9-p000004-l0011 | 36.00 | 34.00–36.00 | 0 |
| 8b6b0de9-p000004-l0028 | 35.50 | 35.00–36.00 | 0 |
| 8b6b0de9-p000004-l0029 | 55.00 | 55.00–55.00 | 0 |
| 8b6b0de9-p000007-l0011 | 37.00 | 36.00–37.00 | 0 |
| 8b6b0de9-p000007-l0021 | 35.00 | 33.50–35.00 | 1 |
| 8b6b0de9-p000007-l0030 | 36.00 | 36.00–37.00 | 0 |
| 8b6b0de9-p000008-l0001 | 35.00 | 34.00–37.00 | 1 |
| 8b6b0de9-p000008-l0002 | 37.00 | 34.00–34.50 | 0 |
| 8b6b0de9-p000008-l0019 | 36.00 | 35.00–37.00 | 0 |
| 8b6b0de9-p000008-l0024 | 35.00 | 35.00–35.50 | 0 |
| 8b6b0de9-p000009-l0024 | 35.00 | 35.00–37.00 | 0 |
| 8b6b0de9-p000011-l0007 | 35.50 | 35.00–36.50 | 0 |
| 8b6b0de9-p000011-l0014 | 36.50 | 35.00–37.00 | 0 |
| 8b6b0de9-p000012-l0006 | 37.00 | 36.00–37.00 | 0 |
| 8b6b0de9-p000016-l0013 | 33.00 | 33.00–34.00 | 1 |
| 8b6b0de9-p000016-l0029 | 33.00 | 33.00–34.00 | 0 |
| 8b6b0de9-p000018-l0023 | 33.00 | 32.50–33.00 | 1 |
| 8b6b0de9-p000018-l0026 | 34.00 | 32.00–35.00 | 1 |
| 8b6b0de9-p000021-l0007 | 34.00 | 33.50–34.00 | 1 |
| 8b6b0de9-p000021-l0028 | 34.00 | 34.00–34.50 | 1 |
| 9c1dca9b-p000005-l0017 | 19.00 | 17.00–19.50 | 6 |
| 9c1dca9b-p000015-l0062 | 21.00 | 20.00–21.00 | 1 |
| 9c1dca9b-p000015-l0065 | 21.00 | 21.00–22.00 | 0 |

## Changed independent owner readings

- `8b6b0de9-p000016-l0013`: και εἰς πᾶν δένδρον φωλεὰ → και εις πᾶν δένδρον φωλεὰ
- `602cc72e-p000155-l0009`: Εὔνουχος καἰ ἶερεύς. → Εὔνουχος καἰ ιερεύς.
- `602cc72e-p000113-l0009`: *Ἄρκτος καὶ ἁλώπῆξ. → *Αρκτος καὶ ἁλώπῆξ.
- `02a3a2a6-p000046-l0014`: Ὠς νὰ τὸν βγάλω πεταχτός, → Ως νὰ τὸν βγάλω πεταχτός,
- `384c3f89-p000183-l0022`: Ἄργῴη περὶ νηί, Θέτις δ’ ἴθυνε κέλευθον. → Ἀργῴη περὶ νηί, Θέτις δ’ ἴθυνε κέλευθον.
- `384c3f89-p000053-l0028`: ἣ θέμις, α̈́μ πεδίον λειμώνιον, ἔνθ’ ἔτι νυν περ → ἣ θέμις, άμ πεδίον λειμώνιον, ἔνθ’ ἔτι νυν περ
- `51fe7386-p000024-l0020`: Και δὲν ἐπέρασε καιρὸς, χρὁνοι πολλοὶ καὶ μῆνες → Και δὲν ἐπέρασε καιρὸς, χρὁνοι πολλοὶ και μῆνες
- `177b717d-p000017-l0012`: Ταράζει καὶ ἡ ἀνάσα σου τὰ μαῦρα τῆς Στυγὸς → Ταράζει καὶ ἡ ανάσα σου τὰ μαῦρα τῆς Στυγὸς

## Qualification and verification

Requested owner strings are not silently relabelled. The retained frozen print instrument, owner diagnosis and native-crop witnesses are reported separately; changing case geometry alone does not establish Ἦ/Ἤ or rough/smooth breathing correctness. Remaining literal naming failures are open. This is not a qualified replacement if any required regression or owner gate remains unmet. Test logs: `S5_pytest.txt`, `S5_pytest_runnable.txt`. The capture test requires a localhost bind forbidden by this sandbox and cannot pass here.

Regressions: held-out total recall 91.9%→91.6%; held-out total f1 92.7%→92.7%; held-out accent precision 95.8%→95.7%; held-out accent recall 94.8%→94.6%; held-out accent f1 95.3%→95.2%; held-out breathing precision 94.4%→94.2%; held-out breathing recall 93.5%→93.1%; held-out breathing f1 93.9%→93.7%; held-out compound recall 89.1%→88.2%; held-out compound f1 84.6%→84.4%; DEV total precision 94.3%→94.2%; DEV total recall 91.2%→89.2%; DEV total f1 92.7%→91.6%; DEV accent recall 96.5%→95.3%; DEV accent f1 95.5%→95.0%; DEV breathing precision 96.3%→95.7%; DEV breathing recall 90.8%→86.9%; DEV breathing f1 93.5%→91.1%; DEV compound precision 87.1%→81.0%; DEV compound recall 88.4%→83.3%; DEV compound f1 87.8%→82.1%; DEV subscript recall 67.3%→65.5%; DEV subscript f1 80.4%→79.1%; DEV dialytika recall 33.3%→0.0%; DEV dialytika f1 16.7%→0.0%; owner expectations lost 51fe7386-p000024-l0020:37.

S5 RESULT: capital detection P 95.6%/R 98.7%; marks at capitals R 86.0%→87.1% naming 86.0%→87.1%; held-out P 93.5%→93.7% R 91.9%→91.6%; ascender false 10/2488→10/2488; owner notes 26/56 + 45/59 (S4 27/56, 46/59); regressions: held-out total recall 91.9%→91.6%; held-out total f1 92.7%→92.7%; held-out accent precision 95.8%→95.7%; held-out accent recall 94.8%→94.6%; held-out accent f1 95.3%→95.2%; held-out breathing precision 94.4%→94.2%; held-out breathing recall 93.5%→93.1%; held-out breathing f1 93.9%→93.7%; held-out compound recall 89.1%→88.2%; held-out compound f1 84.6%→84.4%; DEV total precision 94.3%→94.2%; DEV total recall 91.2%→89.2%; DEV total f1 92.7%→91.6%; DEV accent recall 96.5%→95.3%; DEV accent f1 95.5%→95.0%; DEV breathing precision 96.3%→95.7%; DEV breathing recall 90.8%→86.9%; DEV breathing f1 93.5%→91.1%; DEV compound precision 87.1%→81.0%; DEV compound recall 88.4%→83.3%; DEV compound f1 87.8%→82.1%; DEV subscript recall 67.3%→65.5%; DEV subscript f1 80.4%→79.1%; DEV dialytika recall 33.3%→0.0%; DEV dialytika f1 16.7%→0.0%; owner expectations lost 51fe7386-p000024-l0020:37.
