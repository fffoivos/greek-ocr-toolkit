## L1M2 — Border ownership and padding decision input (17 October 2026)

**Attribution is now measured against the supplied ownership maps.** All **2,699 original (line, edge, native-label) border blobs** and all **2,947 original slot-edge flags** are joined to aligned native ownership pixels. **100/260 lines** have retained class-1 pixels at an SF4-relevant crop edge; **27/260** have no other remaining ENSEMBLE_AB hold. These are the requested **map-based candidate counts**, not demonstrated successful recuts or a semantic certification that every retained class-1 speck is part of a letter. There are **zero class-5 pixels or flags** in these 260 maps.

The two `identity_ambiguous` maps label all foreground as class 1 (`keep_basis=identity_unmasked`), so they cannot certify own-row identity. Excluding them gives **98/260 attributed candidate lines** and still **27/260 sole-hold candidates**. The failed identities are `b963a5d59be557e9eef8498b-p000042-l0020` (round1, 12 relevant class-1 flags) and `17cbdf94881f-p000002-l0015` (vouli, 2 flags). Neither is a sole-hold candidate. The mandatory RESULT line below uses the literal supplied-class definition (100), with this qualification.

### Alignment, custody and frozen semantics

All 200 r4 and 60 vouli-r2 ownership PNGs are 8-bit `L`, have exactly the original/masked crop dimensions, and match their exported ownership hashes and class histograms. The original PNG hashes match the L1M source records. Each r4/vouli-r2 masked PNG is byte-identical to its r3/vouli predecessor, the matching `comparison.json` entry and the saved L1M masked hash (**260/260**); comparison `lines.jsonl` hashes match the original L1M run receipts. The class-2/3/4 union reproduces every applied mask hash, and no grayscale pixel changes outside that union. [Per-line alignment receipt](L1M_evidence/ownership/alignment.csv), [all input hashes](L1M_evidence/ownership/input_hashes.json).

No reader, `read_ink`, gate recomposition, detector-code edit or network access ran. Native ink/labels and crop-wide clipping x-height were reconstructed with the recorded `ink.analyse` + S5 `case.estimate_font` code/model on the 520 already-saved crop variants; both ink masks and component-label arrays are bit-identical to L1M. Every original clipping window reproduces exactly. SF4 relevance and all AB reasons/line guards come directly from the saved `sf4-release-v1` modes and overlays. The neighbouring checkout now differs in `release_gate.py`, `text.py` and `l1_common.py`; none of that current changed code was executed. The S5 model loader indirectly imports text constants, so the historical committed `text.py` was loaded in memory and verified against its L1M hash. [Analysis script](L1M_evidence/ownership/analyse.py), [run log](L1M_evidence/ownership/run.log).

### Exhaustive blob attribution

Each blob is classified over **all of its saved native pixels**, including class-0 pixels in the denominator. A class wins at **≥80%**; otherwise the blob is mixed. Class-0 majority also stays mixed/unattributed, because class 0 is background in the sourcing map rather than an own/foreign ink assertion. The complete six-way pixel counts/fractions and a separate edge-only split are saved for every blob. If a flag joins several blobs, it receives their class only when all blob classes agree; otherwise it is mixed. Flags are counted once. [All blob pixels and splits](L1M_evidence/ownership/border_blobs.jsonl.gz), [all original flags and joins](L1M_evidence/ownership/border_flags.jsonl.gz).

| Wave | Blobs | Above | Below | Unowned | Own | Ring | Mixed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | 1045 | 159 | 66 | 102 | 311 | 0 | 407 |
| round2 | 617 | 71 | 43 | 86 | 131 | 0 | 286 |
| mixed | 451 | 64 | 30 | 75 | 71 | 0 | 211 |
| vouli | 586 | 64 | 46 | 131 | 118 | 0 | 227 |
| ALL | 2699 | 358 | 185 | 394 | 631 | 0 | 1131 |

Across 2,699 blobs: **543 neighbour (20.12%)**, **394 unowned (14.60%)**, **631 own (23.38%)**, **0 ring-abstained (0.00%)**, **1,131 mixed (41.90%)**. The denominator counts an original native component once per touched edge, exactly as L1M did; it is neither a flag count nor a character count. Class 0 accounts for 5,362/108,483 blob-pixel incidences (4.94%); those pixels are not silently reassigned to ink ownership.

### Before → after masking by original flag attribution

Each arrow tracks the **same original (line, slot start, edge) predicate**. A surviving predicate can be triggered by a different blob after masking. The `New` column adds newly flagged slots; therefore the six after columns plus `New` equal the actual masked total. Ring is 0→0 for every row. Full counts, including SF4 relevance, are in [flag transitions](L1M_evidence/ownership/flag_transitions.csv).

| Wave | Edge | Above | Below | Unowned | Own | Mixed | New | Raw total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | top | 133→7 | 0→0 | 43→0 | 61→61 | 306→25 | 1 | 543→94 |
| round1 | bottom | 0→0 | 67→3 | 43→0 | 233→233 | 178→26 | 0 | 521→262 |
| round2 | top | 65→2 | 0→0 | 44→0 | 67→67 | 213→9 | 2 | 389→80 |
| round2 | bottom | 0→0 | 55→0 | 44→0 | 76→76 | 128→8 | 2 | 303→86 |
| mixed | top | 60→4 | 0→0 | 43→5 | 9→9 | 163→21 | 1 | 275→40 |
| mixed | bottom | 0→0 | 32→1 | 34→5 | 66→66 | 106→16 | 0 | 238→88 |
| vouli | top | 72→5 | 0→0 | 67→3 | 55→55 | 154→36 | 5 | 348→104 |
| vouli | bottom | 0→0 | 52→2 | 75→4 | 64→64 | 139→35 | 3 | 330→108 |
| ALL | top | 330→18 | 0→0 | 197→8 | 192→192 | 836→91 | 9 | 1555→318 |
| ALL | bottom | 0→0 | 206→6 | 196→9 | 439→439 | 551→85 | 5 | 1392→544 |

Original own-class flags persist **631/631**; original neighbour flags persist **24/536** and unowned flags **17/393**. Mixed flags persist **176/1,387**. In all, **2,099 original flags clear**, **848 survive** and **14 new flags** yield 862 masked flags. Reclassifying each masked flag’s own native blobs separately gives **637 own, 225 mixed, 0 neighbour/unowned/ring**; this second accounting is in [independent before/after counts](L1M_evidence/ownership/flag_counts_independent.csv) and [every masked flag](L1M_evidence/ownership/masked_border_flags.jsonl.gz). Raw 2,947→862 and SF4-relevant 1,383→378 exactly reproduce the 260-line L1M results.

### Expectation test and exceptions with identities

The proposed expectation is **not universally true**. All 631 original own-class flags persist, and no own-class flag clears. However, **1,211 cleared flags are mixed**, often a neighbour/unowned split rather than a single ≥80% class. **217 surviving flags** have an original class outside own/ring: **18 above, 6 below, 17 unowned, 176 mixed**. Mixed is an attribution result, not a failure to join the blob. Every exception retains its full line ID, slot start, edge, blob keys, original and masked window and surviving original edge split in [the exception ledger](L1M_evidence/ownership/exceptions.jsonl.gz); [readable identity index](L1M_evidence/ownership/exceptions.md).

The 41 above/below/unowned exceptions occur on **22 lines**. Their masked windows contain class-0 detector ink in all 41 cases: **40 background-only, one background+class-1**. In 15 cases an original border pixel survives, always label 0; in 26 cases none of the originally flagging edge pixels remains, but other pixels now satisfy the predicate (two have a shifted window, 24 have the same window). This distinguishes persistence of a Boolean flag from persistence of the original foreign blob. It is directly verified against saved native masks and maps; identifying the cause of each threshold change would require a separate detector analysis. Example IDs: `8b231047fdbd96ec30e1eded-p000033-l0013:16:top`, `290a133b0e55593eb4ecdcfd-p000027-l0053:13:top`, `2495f1aad484-p000001-l0111:14:top`; all 41 identities are enumerated in the linked index.

### Padding number and extent estimate

A padding candidate requires an actual **masked detector-ink pixel with ownership label 1 at y=0 or y=H−1**, inside that masked slot’s exact narrow clipping window, with a saved **SF4-relevant clipping hold**. This is a direct pixel query, not a whole-blob majority test: a mixed blob can contain the touching own pixels. All remaining AB slot reasons and original-label line guards participate in the sole-hold test. Clearing only these own-contact clipping predicates must leave an empty overlay hold list. This is an accounting counterfactual; the gate was not modified.

| Wave | N | Own-contact holds | Class-1 lines | Nonambiguous lines | Sole AB hold | Pure-own sole hold | Component median xh | Component median px | Line-max median xh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| round1 | 80 | 121 | 34 | 33 | 8 | 8 | 0.350 | 3.40 | 0.578 |
| round2 | 60 | 78 | 28 | 28 | 8 | 8 | 0.408 | 5.00 | 0.570 |
| mixed | 60 | 34 | 17 | 17 | 8 | 7 | 0.461 | 6.45 | 0.550 |
| vouli | 60 | 57 | 21 | 20 | 3 | 2 | 0.592 | 16.00 | 0.748 |
| 200 | 200 | 233 | 79 | 78 | 24 | 23 | 0.385 | 4.70 | 0.564 |
| ALL | 260 | 290 | 100 | 98 | 27 | 25 | 0.408 | 6.40 | 0.598 |

Thus the literal class-1 padding input is **100/260 lines and 27/260 sole remaining AB holds** (base 200: **79 and 24**; vouli: **21 and 3**). Of 378 masked SF4 clipping holds, 290 contain class-1 border ink and 88 do not. The remaining 73 of those 100 lines have at least one other hold. Twenty-five sole-hold lines have exclusively class-1 edge pixels in every held clipping window. The other two are `b4266bf58120943ab8864b23-p001333-l0060` (mixed wave) and `838d5080b03f-p000007-l0015` (vouli), which also contain class-0 edge ink. Padding alone is therefore not established to remove every residual on these two lines. The complete [line census](L1M_evidence/ownership/lines.csv) preserves all hold reasons and both sole-hold definitions.

**Padding proxy, not recoverable missing height:** for each touching component, restrict its pixels to retained class 1, then measure `max(0, meanline−min_y)` at the top or `max(0, max_y+1−baseline)` at the bottom. Divide by the saved slot evidence `xh`; coordinates use half-open pixel boxes. Deduplicate by `(line, edge, masked native label)` and take the maximum across qualifying slot bands sharing that component. This yields **321 component-edge observations**, median **0.408 x-height / 6.40 px**, IQR **0.138–0.611 x-height**, P90 **0.942 x-height**. Fifty-one observations have zero extent because the saved band already reaches/passes the cropped component edge; zero does not prove no padding is needed. [All component bounds and slot-specific measurements](L1M_evidence/ownership/padding_components.jsonl.gz).

Taking the largest proxy per candidate line (so many touching letters do not overweight a line) gives median **0.598 x-height / 8.25 px**, IQR **0.470–0.786 x-height**, P90 **1.162 x-height** over 100 lines. Excluding the two ambiguous identities leaves 304 component observations with median **0.400 x-height / 6.20 px**. The RESULT line uses the requested touching-component median, **0.408**, not the line-max median. These measure visible extent outside the fitted body band; the original crop does not contain the missing continuation, so neither value is a measured sufficient recut padding. No recut, re-read or actual release is claimed.

**Letter/mark qualification:** the supplied map’s class 1 means ink kept by the row policy, not independently adjudicated print truth. Inspection confirms the old panels 8/10/12 body-cut pattern (new panels 5/6/7) and an own accent at the top (new panel 8), but also finds retained isolated specks and ornamental/background strokes in class 1. In particular, `2f9e996ffbdaaa3b4a9dfdcf-p000049-l0019` (new panel 9) is not a clean letter-only witness. The 100/98 counts are therefore exact under the supplied ownership-label contract; they must not be presented as 100/98 semantically verified letter-body/mark cuts, nor 27 verified padding rescues. Establishing that stricter physical count would require adjudicating those ambiguous components, rather than silently changing their exported ownership labels. The twelve requested panels plus all 100 candidate-line thumbnails were inspected; [visual observations and limits](L1M_evidence/ownership/visual_review.md).

### Ring abstention and inspected panels

**Ring abstention: 0 original blobs, 0 original flags, 0 masked flags, 0 SF4-relevant flags**, both overall and in each wave/edge stratum. The label-5 pixel count is also zero across all 260 full maps. The last four requested panels therefore show **mixed** witnesses; there are no ring examples to fabricate. Ring-abstained border ink would be a masking-policy input, but it contributes none of this sample’s measured holds. Class-0 residuals are a separate category.

The **12 distinct lines** comprise four neighbour-cleared (one per wave), four own-persistent (including old panels 8/10/12) and four mixed (two persistent, two cleared). Each panel shows original grayscale, original tinted ownership and masked surviving ownership, using nearest-neighbour native-pixel zooms. [Panels 1–3](L1M_evidence/ownership/panels/sheet_1.png), [4–6](L1M_evidence/ownership/panels/sheet_2.png), [7–9](L1M_evidence/ownership/panels/sheet_3.png), [10–12](L1M_evidence/ownership/panels/sheet_4.png); [selection and native bounds](L1M_evidence/ownership/visual_selection.json).

### Reproduction and validation

From this workspace, use the specified local Python with `PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1` to run `L1M_evidence/ownership/analyse.py`, then `panels.py`, `write_section.py` and `validate.py` (paths relative to this report’s directory). The first three write only ownership evidence; `write_section.py` produces `appendix.md` and never regenerates this report. The section was appended once, preserving the original byte prefix. [Validation receipt](L1M_evidence/ownership/validation.json), [validation script](L1M_evidence/ownership/validate.py), [output hashes](L1M_evidence/ownership/SHA256SUMS.txt). The sample remains 200 + 60, with vouli separate; no population extrapolation or downstream rerun follows from this analysis.

L1M2 RESULT: border blobs 2699: neighbour 20.12% / unowned 14.60% / own 23.38% / ring-abstained 0.00% / mixed 41.90%; own-ink clipping lines 100/260, sole remaining AB hold 27/260 (per wave round1 34/80, sole 8/80; round2 28/60, sole 8/60; mixed 17/60, sole 8/60; vouli 21/60, sole 3/60); padding estimate median 0.408 x-height
