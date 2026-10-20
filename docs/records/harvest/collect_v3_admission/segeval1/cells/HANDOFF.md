# SEG-CELLS-1 — descriptive classification, census and crop samples

**Status: classification, complete census and tests finished; numeric crop samples blocked under the SCP-only constraint. Only 50/250 crops fetched.** No `done` claim is made. The pending fallback below requires an explicit owner scope change.

No segmentation verdict, policy, detector, version file, reader output or pipeline disposition was changed. The new pure function has no consumer in the pipeline. No Slurm, OCR reader or image regeneration ran. Clariden operations were read-only Python/stdout metadata reduction and path checks, plus SCP reads of existing crops. Nothing was pushed.

## Frozen population and receipts

The pinned generation is `g1-1c775230225d4bbea5871d4fae2475da`: **592,466 rows**, **8,168,706,501 bytes**, SHA256 `568d4759257787086ee8c0780cd0d4cf633c5ebf7b355d519d6053ff8c42764a`. The full export stayed on Clariden. Before/after size+mtime and CURRENT equality, resolved path, summary hash and exact export hash/count all passed. Every raw-text hash was rebound to verified frozen parent metadata; W1/W2 crop hashes also match their parent metadata. The original-v2 parent metadata is the earlier frozen read-only export, with its parent receipts checked against the census configuration. See [export_receipt.json](export_receipt.json), [export_remote.py](export_remote.py), [reduce_population.py](reduce_population.py).

The reduced [population_cells.jsonl.gz](population_cells.jsonl.gz) has exactly one record per population row: row and parent IDs; source, primary and script classes, wave; literal raw Google text; original crop width/height from the 0.5 segmentation frame; saved character count; raw trimmed codepoint count; x-height and method; unchanged 0.5 verdict/reason and pipeline disposition/reasons; crop path/hash binding; and the four descriptive classifier fields. There are no missing dimensions, saved character counts or curve-derived x-heights in this export.

## Exact classifier grammar and chosen limits

```text
Classify a crop descriptively, with no I/O or policy/verdict changes.

Exact numeric-output grammar, after Python ``str.strip()``:

1. One or more Unicode decimal digits (``str.isdecimal``), interspersed
   with any Unicode whitespace or these literal separators/signs only:
   ``. , : / - – — % ( ) + ' ′ § №``. A digit is required; separator
   balance/order is not checked (so ``29)`` and ``463.503.-`` qualify).
2. One canonical Roman numeral, case-insensitive, matching
   ``M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})``,
   nonempty, optionally wrapped by the above separators and ASCII
   whitespace. Only Latin IVXLCDM/ivxlcdm, Unicode Roman U+2160..217F
   (NFKC-expanded), and Greek capital iota Ι (mapped to I) are permitted
   inside the numeral. Internal whitespace is forbidden. Other Greek
   lookalikes are not mapped. Canonical numeral spellings that are also
   words, e.g. ``mix``, necessarily qualify by this lexical grammar.
3. One whitespace-free token with strictly more than half its codepoints
   decimal digits; every remaining codepoint must be Unicode punctuation
   or a symbol (general-category P* or S*). This admits e.g. ``12€``.
   Letters are forbidden in both digit branches, even with many digits;
   a digit/Roman-letter mixture such as ``123IV`` does not qualify.

``is_small_image`` requires finite positive numeric pixel dimensions,
width <= 200 px, height <= 40 px, and <= 10 visible characters. Visible
characters are NFC codepoints excluding whitespace, marks (M*) and
controls/format characters (C*), matching the saved segmentation count.
Empty text can be a small image but cannot be numeric. Both dimensions
are the original crop dimensions, never rotated or normalised.

The optional xheight_px is intentionally unused: corpus curve-derived
x-heights are reported, but tiny numeric crops have unstable font-height
estimates. It cannot affect classification. ``is_cell`` is exactly the
conjunction of the two booleans; reasons explain those two tests only.
These limits describe a proposed population for review, not correctness.
```

The named constants are `MAX_CELL_WIDTH_PX=200`, `MAX_CELL_HEIGHT_PX=40`, `MAX_CELL_CHARACTERS=10`. The width proposal rounds numeric P95=169 up to the next 50 px; height rounds numeric P75=35 up to the next 10 px; the character limit is numeric P90=10 without rounding. This selects the compact numeric population for review. It is a descriptive choice, not an inferred ground-truth boundary or an optimum. All distributions and the grid were computed before the crop sample was drawn.

The width distribution is strongly separated: numeric median/P95 are 59/169 px, versus 765/2040 px for other outputs. Height alone is weaker: numeric median/P75/P90 are 22/35/81 px, versus 44/67/93 px for other outputs. The height cut deliberately leaves the tall numeric tail for boundary review. Saved visible-character median/P90 are 6/10 for numeric outputs, versus 44/57 for other outputs. The joint cut retains 39,014/54,440 numeric outputs (71.66%) and also describes 21,027 small non-numeric rows. No cell accuracy is asserted.

X-height is recovered only from saved evidence: median positive `base(x)-mean(x)` on the unique main detected row, at shared saved x coordinates (all 592,466 rows). These are the detector’s saved, rounded curve estimates, not independently measured font truth. Tiny numeric curves have substantial tails (numeric height P95=8.0 x-heights; all rows P95=4.57), supporting the decision to keep x-height out of this proposed pixel cut. No image was opened to derive thresholds.

### Sensitivity of the proposed joint cut

| Width ≤ px | Height ≤ px | Visible chars ≤ | Numeric rows included |
| --- | --- | --- | --- |
| 100 | 40 | 10 | 35529 |
| 150 | 40 | 10 | 38758 |
| 200 | 30 | 10 | 35103 |
| 200 | 40 | 8 | 32067 |
| 200 | 40 | 9 | 36052 |
| 200 | 40 | 10 | 39014 |
| 200 | 40 | 12 | 40246 |
| 200 | 40 | 16 | 40802 |
| 200 | 50 | 10 | 40997 |
| 200 | 60 | 10 | 42341 |
| 200 | 80 | 10 | 44829 |
| 200 | 100 | 10 | 47058 |
| 250 | 40 | 10 | 39062 |
| 300 | 40 | 10 | 39064 |


## Census totals and composition

| Population | Rows |
| --- | --- |
| all | 592466 |
| numeric | 54440 |
| cells | 39014 |
| small_not_numeric | 21027 |
| numeric_not_small | 15426 |


### By source

| source | All | Numeric output | Cells |
| --- | --- | --- | --- |
| anemi_mixed | 17260 | 0 | 0 |
| anemi_round1 | 58213 | 0 | 0 |
| anemi_round2 | 23128 | 0 | 0 |
| archive_AA9613308335D0B014B | 1712 | 0 | 0 |
| archive_b24878935 | 1193 | 0 | 0 |
| archive_b28038630 | 9665 | 0 | 0 |
| archive_b29337124 | 219 | 0 | 0 |
| archive_bub_gb_Cmg6AQAAIAAJ | 1531 | 0 | 0 |
| archive_bub_gb_mG0mAQAAIAAJ | 1558 | 0 | 0 |
| archive_izvestiianabul25192530bul | 1438 | 0 | 0 |
| archive_izvestiianabulga610193138bulg | 1225 | 0 | 0 |
| archive_izvestiianatsars1112193839tsar | 209 | 0 | 0 |
| archive_izvestiianatsars12192829tsar | 783 | 0 | 0 |
| archive_izvestiianatsars1516194243tsar | 1008 | 0 | 0 |
| archive_izvestiianatsars910193637tsar | 449 | 0 | 0 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 1575 | 0 | 0 |
| bsb_poly1850 | 33090 | 1719 | 1548 |
| elstat | 19879 | 13875 | 12626 |
| gazette_modern | 148547 | 33122 | 21489 |
| ia_greek_latin | 11755 | 664 | 376 |
| ia_poly1850 | 64476 | 3312 | 1522 |
| ia_russian | 2963 | 216 | 141 |
| kosmopolis | 5356 | 138 | 138 |
| lekythos | 13407 | 167 | 139 |
| nlg | 12109 | 604 | 517 |
| openarchives_Dione | 2828 | 0 | 0 |
| openarchives_IKEE_AUT | 260 | 0 | 0 |
| openarchives_KEIED | 2257 | 0 | 0 |
| openarchives_Pandemos | 2766 | 0 | 0 |
| openarchives_anaktisis | 2729 | 0 | 0 |
| openarchives_apothesis | 2207 | 0 | 0 |
| openarchives_hellanicus | 2861 | 0 | 0 |
| openarchives_kallipos | 2936 | 0 | 0 |
| openarchives_ktisis | 2620 | 0 | 0 |
| openarchives_mixed_Dione | 672 | 0 | 0 |
| openarchives_mixed_KEIED | 578 | 0 | 0 |
| openarchives_mixed_Pandemos | 60 | 0 | 0 |
| openarchives_mixed_anaktisis | 488 | 0 | 0 |
| openarchives_mixed_apothesis | 678 | 0 | 0 |
| openarchives_mixed_hellanicus | 335 | 0 | 0 |
| openarchives_mixed_kallipos | 219 | 0 | 0 |
| openarchives_mixed_ktisis | 663 | 0 | 0 |
| openarchives_mixed_nemertes | 124 | 0 | 0 |
| openarchives_mixed_ntua | 97 | 0 | 0 |
| openarchives_nemertes | 2156 | 0 | 0 |
| openarchives_ntua | 1752 | 0 | 0 |
| parliament_proceedings_1975_2000 | 81181 | 0 | 0 |
| serbia | 8897 | 623 | 518 |
| vouli_parliament_1850s | 28259 | 0 | 0 |
| wikisource_el | 8975 | 0 | 0 |
| wikisource_ru | 3120 | 0 | 0 |


### By primary_class

| primary_class | All | Numeric output | Cells |
| --- | --- | --- | --- |
| cyrillic | 25905 | 0 | 0 |
| dialogue_fiction | 10979 | 0 | 0 |
| greek_latin_cs | 7621 | 0 | 0 |
| greek_mono | 76430 | 1 | 1 |
| greek_poly | 163853 | 0 | 0 |
| headings_caps | 24144 | 1 | 1 |
| latin | 71782 | 949 | 817 |
| leaders_indices | 45 | 0 | 0 |
| mixed_greek_latin | 16181 | 0 | 0 |
| modern_scanned | 76797 | 3 | 3 |
| nonletter | 5149 | 1141 | 886 |
| numerics_tables | 56470 | 52345 | 37306 |
| poly1850 | 36354 | 0 | 0 |
| poly1900 | 20756 | 0 | 0 |


### By script_class

| script_class | All | Numeric output | Cells |
| --- | --- | --- | --- |
| cyrillic | 26078 | 0 | 0 |
| greek_latin_cs | 15905 | 0 | 0 |
| greek_mono | 186317 | 5 | 5 |
| greek_poly | 225057 | 0 | 0 |
| latin | 81322 | 949 | 817 |
| nonletter | 57787 | 53486 | 38192 |


### By wave

| wave | All | Numeric output | Cells |
| --- | --- | --- | --- |
| W1 | 101098 | 13146 | 9884 |
| W2 | 219381 | 41294 | 29130 |
| cyrillic | 12900 | 0 | 0 |
| mixed | 30839 | 0 | 0 |
| openarchives | 25372 | 0 | 0 |
| parliament | 81181 | 0 | 0 |
| round1 | 58213 | 0 | 0 |
| round2 | 23128 | 0 | 0 |
| vouli | 28259 | 0 | 0 |
| wikisource | 12095 | 0 | 0 |


### By parent_id

| parent_id | All | Numeric output | Cells |
| --- | --- | --- | --- |
| collect-v3-W1-20261018-0524 | 101098 | 13146 | 9884 |
| collect-v3-W2-20261018-0524 | 219381 | 41294 | 29130 |
| collection-v2-dev | 13522 | 0 | 0 |
| collection-v2-test | 44029 | 0 | 0 |
| collection-v2-train | 214436 | 0 | 0 |


## What the unchanged 0.5 filter and pipeline did

**Receipt discrepancy in the brief:** the exact requested hash contains **17,036 segmentation DROP / 151,931 UNCERTAIN / 423,499 KEEP**, rather than 16,736 / 151,645. The previous SEGEVAL draw receipt independently records these same actual totals. Pipeline disposition is a different field: **17,036 DROP / 575,430 HOLD**, with zero ADMIT/KEEP dispositions. Split/edition holds include segmentation KEEP rows. Counts below use the sealed export, without altering a verdict to match the brief.

| 0.5 segmentation verdict | All | Numeric output | Cells |
| --- | --- | --- | --- |
| DROP | 17036 | 3230 | 2419 |
| UNCERTAIN | 151931 | 14266 | 5068 |
| KEEP | 423499 | 36944 | 31527 |


| Pipeline disposition | All | Numeric output | Cells |
| --- | --- | --- | --- |
| DROP | 17036 | 3230 | 2419 |
| HOLD | 575430 | 51210 | 36595 |
| ADMIT | 0 | 0 | 0 |


The cells among pipeline HOLD are 36,595 = 31,527 segmentation KEEP + 5,068 segmentation UNCERTAIN. Every one of the 2,419 pipeline-DROP cells has segmentation DROP. The required status line uses **HOLD as an alias for 0.5 segmentation UNCERTAIN (5,068)**; it does not substitute the larger pipeline-HOLD count. The table stores the literal verdict `UNCERTAIN`.

| 0.5 verdict and literal reason | All | Numeric output | Cells |
| --- | --- | --- | --- |
| DROP \| A second complete printed line is visible. | 95 | 13 | 13 |
| DROP \| More than 2 complete neighbouring words are visible. | 60 | 0 | 0 |
| DROP \| Too little OCR output for the text box after height normalisation. | 7999 | 2105 | 1797 |
| DROP \| Too much OCR output for the text box after height normalisation. | 7069 | 944 | 500 |
| DROP \| Top and bottom padding together exceed 1.5 target-line heights. | 1813 | 168 | 109 |
| KEEP \| OCR length matches; neighbouring words and vertical padding are within the selected allowances, with no second complete line. | 423499 | 36944 | 31527 |
| UNCERTAIN \| No usable text box was measured. | 77 | 52 | 41 |
| UNCERTAIN \| The complete neighbouring-word count or line extent is unresolved. | 125635 | 169 | 127 |
| UNCERTAIN \| The detector returned no row with observed support. | 6400 | 4081 | 3781 |
| UNCERTAIN \| The reading direction remains unresolved. | 19819 | 9964 | 1119 |


## Dimension distributions

Nearest-rank empirical quantiles, using all rows in each cohort. Width and height refer to original source pixels. Character counts use saved segmentation evidence (NFC visible characters); the additional raw-length distribution is available in [distributions.json](distributions.json). No missing measurements were imputed.

### width_px: quantiles

| Cohort | N | Min | P10 | P25 | P50 | P75 | P90 | P95 | P99 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numeric | 54440 | 8 | 19 | 27 | 59 | 84 | 114 | 169 | 368 | 1673 |
| rest | 538026 | 6 | 213 | 531 | 765 | 1305 | 1926 | 2040 | 2107 | 4119 |
| all | 592466 | 6 | 79 | 379 | 724 | 1216 | 1804 | 2036 | 2104 | 4119 |


### height_px: quantiles

| Cohort | N | Min | P10 | P25 | P50 | P75 | P90 | P95 | P99 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numeric | 54440 | 9 | 16 | 18 | 22 | 35 | 81 | 103 | 164 | 1362 |
| rest | 538026 | 5 | 29 | 36 | 44 | 67 | 93 | 102 | 206 | 2297 |
| all | 592466 | 5 | 25 | 34 | 43 | 65 | 93 | 102 | 199 | 2297 |


### characters: quantiles

| Cohort | N | Min | P10 | P25 | P50 | P75 | P90 | P95 | P99 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numeric | 54440 | 1 | 2 | 3 | 6 | 9 | 10 | 13 | 25 | 167 |
| rest | 538026 | 1 | 15 | 30 | 44 | 50 | 57 | 63 | 76 | 399 |
| all | 592466 | 1 | 8 | 22 | 42 | 49 | 56 | 62 | 76 | 399 |


### width_xh: quantiles

| Cohort | N | Min | P10 | P25 | P50 | P75 | P90 | P95 | P99 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numeric | 54440 | 0.116 | 1.373 | 1.855 | 3.649 | 6.091 | 8.5 | 11.895 | 22.5 | 198.143 |
| rest | 538026 | 0.035 | 13.071 | 31.429 | 49.111 | 56.346 | 64.8 | 72.696 | 119.111 | 285 |
| all | 592466 | 0.035 | 5.396 | 21.929 | 46.571 | 55.769 | 64.083 | 71.929 | 117.059 | 285 |


### height_xh: quantiles

| Cohort | N | Min | P10 | P25 | P50 | P75 | P90 | P95 | P99 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numeric | 54440 | 0.084 | 1.107 | 1.319 | 1.515 | 2.111 | 6.125 | 8 | 12.909 | 136.2 |
| rest | 538026 | 0.018 | 1.722 | 2.179 | 2.579 | 2.923 | 3.385 | 4 | 17.385 | 255.222 |
| all | 592466 | 0.018 | 1.542 | 2.067 | 2.538 | 2.92 | 3.4 | 4.571 | 16.75 | 255.222 |


### width_px: histogram

| Non-overlapping interval | Numeric output | Rest | All |
| --- | --- | --- | --- |
| <= 25 | 12552 | 9389 | 21941 |
| > 25, <= 50 | 10824 | 6410 | 17234 |
| > 50, <= 75 | 13171 | 4664 | 17835 |
| > 75, <= 100 | 10110 | 4983 | 15093 |
| > 100, <= 150 | 4587 | 11673 | 16260 |
| > 150, <= 200 | 1397 | 13125 | 14522 |
| > 200, <= 250 | 773 | 13686 | 14459 |
| > 250, <= 300 | 289 | 11986 | 12275 |
| > 300, <= 400 | 248 | 22985 | 23233 |
| > 400, <= 600 | 274 | 55922 | 56196 |
| > 600, <= 800 | 146 | 140832 | 140978 |
| > 800, <= 1200 | 42 | 92786 | 92828 |
| > 1200, <= 2000 | 27 | 104389 | 104416 |
| > 2000 | 0 | 45196 | 45196 |


### height_px: histogram

| Non-overlapping interval | Numeric output | Rest | All |
| --- | --- | --- | --- |
| <= 15 | 4329 | 3749 | 8078 |
| > 15, <= 20 | 16853 | 10743 | 27596 |
| > 20, <= 25 | 12625 | 16495 | 29120 |
| > 25, <= 30 | 4595 | 31843 | 36438 |
| > 30, <= 40 | 4234 | 162126 | 166360 |
| > 40, <= 50 | 2135 | 103592 | 105727 |
| > 50, <= 60 | 1495 | 52747 | 54242 |
| > 60, <= 80 | 2609 | 72345 | 74954 |
| > 80, <= 100 | 2601 | 54365 | 56966 |
| > 100, <= 150 | 2222 | 22143 | 24365 |
| > 150, <= 200 | 454 | 2292 | 2746 |
| > 200 | 288 | 5586 | 5874 |


### characters: histogram

| Non-overlapping interval | Numeric output | Rest | All |
| --- | --- | --- | --- |
| <= 1 | 4531 | 3445 | 7976 |
| > 1, <= 2 | 5955 | 1778 | 7733 |
| > 2, <= 3 | 7671 | 1396 | 9067 |
| > 3, <= 4 | 3834 | 1986 | 5820 |
| > 4, <= 5 | 4506 | 2611 | 7117 |
| > 5, <= 6 | 4555 | 3308 | 7863 |
| > 6, <= 8 | 7409 | 7620 | 15029 |
| > 8, <= 9 | 6096 | 4551 | 10647 |
| > 9, <= 10 | 4561 | 4571 | 9132 |
| > 10, <= 12 | 2168 | 10495 | 12663 |
| > 12, <= 16 | 1321 | 22593 | 23914 |
| > 16, <= 20 | 910 | 21028 | 21938 |
| > 20, <= 40 | 772 | 133792 | 134564 |
| > 40, <= 80 | 126 | 315435 | 315561 |
| > 80, <= 120 | 18 | 3030 | 3048 |
| > 120 | 7 | 387 | 394 |


## Seeded samples and observed segment types

The draw uses **seed 20261019**, equal probability per row over the full pool across sources (no source quotas), separately for 150 cells, 50 numeric outputs above at least one size limit and 50 small non-numeric rows. Each pool is sorted by `(parent_id,row_id)` before a full `random.Random(seed).sample` permutation, in that category order. The first fetchable rows in each fixed permutation are retained. [sample_order.jsonl.gz](sample_order.jsonl.gz) seals the complete replacement order. [samples.jsonl](samples.jsonl) is the coordinator input, with all requested fields plus group, parent/wave, script class and pipeline disposition.

**50/250** crops fetched with read-only SCP; every crop’s SHA256 matches the census binding, every PNG decodes, and its physical dimensions match the saved source frame. There were **57,985** unavailable/failed candidate paths before replacements. See [sample_failures.jsonl](sample_failures.jsonl) and [sample_receipt.json](sample_receipt.json). No missing crop was reconstructed, and no new source page was fetched.

**Exhausted numeric pools:** all **39,014 cell paths** and **15,426 numeric-not-small paths** are unavailable. Every numeric row is W1/W2, and both recorded W1/W2 crop directories are absent. The source-page hashes and crop boxes are present in the frozen metadata. [crop_availability_probe.txt](crop_availability_probe.txt) verifies the missing directories and the actual exported crop/source binding. Replacement cannot supply even one numeric crop under the literal SCP-only instruction.

**Prepared, not executed:** [pending_reconstruction.jsonl](pending_reconstruction.jsonl) binds the first 150 cell and 50 numeric-boundary rows from the original seeded orders to **156** existing source-page identities and frozen boxes. [pending_reconstruction_receipt.json](pending_reconstruction_receipt.json) records the proposed exact action; [stream_missing_crops_remote.py](stream_missing_crops_remote.py) implements the existing L-mode crop / PNG compress_level=3 contract in memory, with source and output SHA256 checks. It has not been run. Proceeding requires owner authorization to change SCP-only fetching to in-memory reconstruction over read-only SSH. No remote file, reader, detector, policy or Slurm action is proposed. The already fetched 50 controls remain available.

The fetchable sample is conditional on archived crop availability. W1/W2 runtime crops can be reconstructed in memory by the existing pipeline without being saved at their declared crop paths; this task deliberately does not run that reconstruction. Missing-source coverage must therefore not be read as absence of those segment types. The source counts below expose this limitation.

| Sample group | Pool size | Fetched | Fetched by source |
| --- | --- | --- | --- |
| cells | 39014 | 0 | {} |
| numeric_not_small | 15426 | 0 | {} |
| small_not_numeric | 21027 | 50 | {"anemi_mixed": 4, "anemi_round1": 11, "anemi_round2": 5, "archive_b24878935": 1, "archive_izvestiianatsars1516194243tsar": 1, "openarchives_Dione": 5, "openarchives_IKEE_AUT": 1, "openarchives_KEIED": 1, "openarchives_Pandemos": 5, "openarchives_anaktisis": 2, "openarchives_apothesis": 1, "openarchives_kallipos": 1, "openarchives_mixed_Dione": 3, "openarchives_mixed_Pandemos": 1, "openarchives_mixed_anaktisis": 2, "openarchives_mixed_apothesis": 1, "openarchives_mixed_ktisis": 2, "openarchives_nemertes": 1, "openarchives_ntua": 2} |


[sample_observations.md](sample_observations.md) records visual observations from six identified fetched control crops: short Greek/Latin words, capital headers and fragments. These are review material, not accuracy labels. There are no fetched numeric crops and no observed numeric segment-type claim. The classifier does not assign semantic classes such as page number, amount or date.

## Exact membership on the 150 evaluation lines

**15/150 cells**, **17/150 numeric outputs**. The two numeric non-cells are `330` (103×46 px) and `6 10 6` (63×60 px), both above the 40 px height cut. All 150 rows and their unchanged 0.5/0.8 verdicts are in [evaluation_150_cells.jsonl](evaluation_150_cells.jsonl).

**Brief discrepancy:** the base-commit replay and scored Google-text file contain **five numeric cells among the 18 false rejects**, not thirteen. `ΙΙ` is not present in these 150 texts. The 18 false rejects include eleven outputs with 1–9 saved visible characters, of which only five meet the requested numeric grammar; the others contain words or punctuation alone. Both source files were read back equal to commit `410f4566`. No extra numeric class or altered label was introduced to force thirteen witnesses. The synthetic `ΙΙ` grammar case is tested separately.

| False reject row ID | Google text | Width | Height | Chars | Numeric | Cell | 0.8 reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gazette_modern--d4e7c0bb57264e92--s000-l0030 | 3.237.787 | 190 | 20 | 9 | True | True | length: Too little OCR output for the text box after height normalisation. |
| gazette_modern--f4a16fe9302ade1e--s000-l0180 | 29) | 33 | 22 | 3 | True | True | length: Too much OCR output for the text box after height normalisation. |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0065 | *Vid. Luc. | 225 | 79 | 9 | False | False | length: Too much OCR output for the text box after height normalisation. |
| lekythos--49c082ba27aa27da--s001-l0228 | κλυσμό. Μέσα στὸ πλαίσιο τῆς σοβαρῆς προσπά- | 530 | 39 | 38 | False | False | gate: too many whole neighbour words |
| elstat--24e6586813212fd1--s001-l0357 | 37 | 36 | 18 | 2 | True | True | length: Top and bottom padding together exceed 1.5 target-line heights. |
| elstat--d8fe6ab28d6113ba--s000-l0097 | 270 | 50 | 19 | 3 | True | True | length: Too much OCR output for the text box after height normalisation. |
| gazette_modern--5d57e9c685c50ca6--s000-l0073 | Скрирания | 160 | 61 | 9 | False | False | length: Top and bottom padding together exceed 1.5 target-line heights. |
| gazette_modern--6efb0af18300ce89--s000-l0085 | Γραμματέα, Δ/ντές και Τμηματάρχες της Κεντρικής Υπηρεσίας του | 709 | 45 | 54 | False | False | length: Too much OCR output for the text box after height normalisation. |
| gazette_modern--7ea39dff64198917--s000-l0093 | προηγουμ. χρήσης | 117 | 20 | 15 | False | False | length: Too much OCR output for the text box after height normalisation. |
| gazette_modern--80e8a42cbf8e629f--s000-l0120 | 13.3.1986 (ΦΕΚ 93/Γ΄/11.4.86) και μόνο κατά το μέρος | 717 | 53 | 45 | False | False | length: Too much OCR output for the text box after height normalisation. |
| gazette_modern--9aa01acfc4b8b0a7--s000-l0100 | κτηριστικών (απόφαση ΣΤ-20270/73-Φ.Ε.Κ. 884/73, όπως | 716 | 46 | 48 | False | False | length: Too much OCR output for the text box after height normalisation. |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | " | 14 | 10 | 1 | False | False | length: Too little OCR output for the text box after height normalisation. |
| gazette_modern--af3c2f9a667e8669--s000-l0004 | ΑΘΗΝΑ | 131 | 23 | 5 | False | False | length: Too little OCR output for the text box after height normalisation. |
| gazette_modern--b05f7f66a8e2e416--s000-l0067 | ΔΗΜ. ΓΕΩΡΓΑΚΟΠΟΥΛΟΣ | 306 | 22 | 18 | False | False | length: Too little OCR output for the text box after height normalisation. |
| gazette_modern--c4919950cda5532e--s000-l0008 | ΠΑΓΙΟ | 110 | 19 | 5 | False | False | length: Too little OCR output for the text box after height normalisation. |
| gazette_modern--c4919950cda5532e--s000-l0030 | 54.296 | 82 | 24 | 6 | True | True | length: Too much OCR output for the text box after height normalisation. |
| ia_poly1850--4ab77886725d9e1e--s035-l0035 | ἐᾶν, 95 | 117 | 39 | 6 | False | False | length: Too much OCR output for the text box after height normalisation. |
| 129cff40-p000009-l0107 | τικὸς ἔχει τὸν λόγον. | 723 | 88 | 18 | False | False | gate: second complete line |


### All cell members among the 150

| Row ID | Google text | Width | Height | Chars | 0.8 verdict | Owner state |
| --- | --- | --- | --- | --- | --- | --- |
| elstat--07520765bc203a33--s000-l0134 | 5,914 | 73 | 22 | 5 | KEEP | fine |
| gazette_modern--158b2e0a2843dd81--s000-l0030 | 463.503.- | 101 | 22 | 9 | KEEP | fine |
| gazette_modern--d4e7c0bb57264e92--s000-l0030 | 3.237.787 | 190 | 20 | 9 | DROP | fine |
| gazette_modern--f4a16fe9302ade1e--s000-l0180 | 29) | 33 | 22 | 3 | DROP | fine |
| elstat--24e6586813212fd1--s001-l0357 | 37 | 36 | 18 | 2 | DROP | fine |
| elstat--3b2d88122b3f037c--s001-l0043 | 141,48 | 81 | 24 | 6 | KEEP | fine |
| elstat--d8fe6ab28d6113ba--s000-l0097 | 270 | 50 | 19 | 3 | DROP | fine |
| gazette_modern--02e723ce58227531--s000-l0126 | 321.295 | 67 | 17 | 7 | KEEP | fine |
| gazette_modern--1349d550e27fdac0--s000-l0088 | 100.000 | 78 | 17 | 7 | KEEP | fine |
| gazette_modern--13a9303cfc83a9d4--s000-l0045 | 3 | 17 | 16 | 1 | UNCERTAIN | unresolved |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | 1 | 22 | 24 | 1 | UNCERTAIN | fine |
| gazette_modern--59ebc3dbeb1516d3--s000-l0066 | 25,50 | 59 | 27 | 5 | KEEP | fine |
| gazette_modern--65492f4d3675f146--s000-l0001 | 670 | 54 | 24 | 3 | KEEP | fine |
| gazette_modern--6d58ca2e2dc41e69--s000-l0067 | 4. | 21 | 18 | 2 | KEEP | fine |
| gazette_modern--c4919950cda5532e--s000-l0030 | 54.296 | 82 | 24 | 6 | DROP | fine |


## Tests, scope and delivery

**121 tests passed** with `.venv/`: exact lexical grammar, all 17 actual numeric evaluation outputs, all 18 actual false rejects (five cells), 20 fixed ordinary evaluation lines (no cells), inclusive size/character boundaries, invalid dimensions and x-height independence. The requested thirteen numeric false-reject witnesses cannot be sourced from the exact supplied artifacts; the expanded real-witness coverage and discrepancy above are explicit. [tests.log](tests.log), [evaluation_fixtures.json](evaluation_fixtures.json).

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_numeric_cells.py -q
```

Implementation commit **`7350e39c0461bc89cce812186b2e3cdafe46bb2a`**, exact parent **`410f4566db26a9acefb541a5af12312c661fb918`**. The sandbox cannot write the shared Git directory. The authorised [SEGCELLS1.bundle](SEGCELLS1.bundle) contains branch **`sol/seg-cells`** in a separate writable Git directory, followed by a hand-off-only commit. [bundle_receipt.json](bundle_receipt.json) verifies ancestry, independent local import and committed-file bytes. The shared checkout stays on `sol/recut-v1`; shared refs/index and all five pre-existing edited files remain unchanged. No existing production file was staged or changed; production addition is only `numeric_cells.py`. Nothing was pushed.

SEGCELLS1: blocked | numeric-output rows 54440/592466 | cells 39014 (thresholds: width<=200px, height<=40px, chars<=10) | cells among 0.5 DROP 2419, HOLD 5068, KEEP 31527 | samples fetched 50/250 | tests 121 passed | commit 7350e39c0461bc89cce812186b2e3cdafe46bb2a


## 1b

**Complete: 250/250 samples are present and byte-exact to the frozen census.**
This section supersedes the historical sample-availability blocker above.
The saved seeded orders and descriptive classifier are unchanged: the first
150 cells and first 50 numeric-not-small rows were reconstructed, and the
original 50 small-non-numeric PNGs were retained byte-for-byte. No replacement
was needed.

### Local reconstruction and provenance

The 200 new crops use **156 unique cached pages**, all verified against their
recorded source SHA256. Both frozen W1/W2 feature snapshots were already local;
their full hashes and row counts were rechecked against `export_receipt.json`.
The W2 page JSON and resolved manifest were inspected first; the feature
snapshot supplies the per-row boxes. Every selected metadata crop hash, page
hash, bbox and colour mode was rebound to the prepared/census records.

The script imports `greekocr.harvest.line_pipeline_native.reconstructed_crop`
and `digest_bytes` directly. That production file is unchanged. It makes the
same page conversion, bbox crop and PNG encoding as the pipeline, and checks
`digest_bytes(encoded) == crop_sha256` before writing each PNG. **200 local
line crops** were made, within the authorised limit. No cache file was written.
There were **zero page fetches, zero SCP page reads, zero replacements and zero
Clariden commands** in 1b. The original 50 controls remain labelled as existing
SEG-CELLS-1 SCP crop reads; they are not counted as page-cache reconstructions.
The old pending receipt and crop-file failure log describe SEG-CELLS-1 history.

[samples.jsonl](samples.jsonl) now contains absolute local crop paths, crop
SHA256, width/height, character count, literal OCR text, source/classes, literal
0.5 verdict/reason and group for every sample. [sample_receipt.json](sample_receipt.json)
contains all 250 per-sample acquisition records, original seeded ranks,
page hashes/paths, zero fetch/replacement logs, and metadata verification.
[selected_metadata_1b.json](selected_metadata_1b.json) keeps the 200 compact
source/bbox bindings. Page counts in the final line mean **unique source-page
hashes**, not sample counts (200 samples use 156 pages).

### Visual review and validation

**40 of the 150 native cell PNGs were opened individually with the image tool**;
ten difficult cases were additionally viewed at 6× display scale. See
[sample_observations.md](sample_observations.md),
[visual_review_1b.json](visual_review_1b.json) and
[visual_zoom_1b.png](visual_zoom_1b.png). They show page-number-like crops,
amounts, a date, parenthesized markers of unresolved role, faint/broken or
heavy ink, sideways strips and clipped extra strokes. These are visual
observations, not new rules, corrected OCR, owner labels or independent gold.

[validation_1b.json](validation_1b.json) records **PASS**: all 250 physical PNG
hashes/dimensions and required fields match the census; both numeric seeded
prefixes and all original controls are preserved; 156 page hashes match;
the native function and all five pre-existing edited files are unchanged.
The shared HEAD, refs, index and existing diff are also unchanged.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B docs/records/harvest/collect_v3_admission/segeval1/cells/validate_1b.py
```

### Commit delivery

The shared Git write probe returned `Operation not permitted`. The authorised
[SEGCELLS1B.bundle](SEGCELLS1B.bundle) therefore extends imported branch
`sol/seg-cells` at `01111b82d5e2449a7b2a8dcd0106b3fe890c5bde` in an isolated writable Git directory.
Materialisation/observations/validation commit: **`84fe20998348ffc826d7cdc5c3b997c2a4f07384`**.
A following hand-off-only commit contains this section; its hash is recorded
in [bundle_receipt_1b.json](bundle_receipt_1b.json). The final line names the
materialisation commit to avoid a self-referential commit hash.
Independent bundle import verifies the branch tip, ancestry and every changed
file's committed bytes. No production path was changed; nothing was pushed.

SEGCELLS1B: done | samples 250/250 byte-exact | pages from cache 156, scp 0, replacements 0 | commit 84fe20998348ffc826d7cdc5c3b997c2a4f07384
