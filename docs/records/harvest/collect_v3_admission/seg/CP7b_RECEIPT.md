# SEG-CP7b receipt

Freeze verified before scoring and again after output: `9212fe491a37e3992d245aec0d8a47a7e9437e8e6ef3a7aa6a1025ac825fa22e`. Current CP7a3 seal: `87014014a5098e67b033b9ac49003f2e793ad4701349be68171f5c3a39c16119`. Network OFF; no reader launched, OCR, new crop reading, threshold changes, geometry preparation, or staged replay.

Both original pack manifests and CP7a3 pack-preservation hashes match. Raw answers remap exactly to the 100 mapped rows and 10 controls; each original pack crop and repository copy matches the sealed crop SHA. Scan reports are ok with zero violations; their rollout hashes, usage and receipts match the logged runs.

Context A provenance: its lead-written receipt exactly matches the successful run JSON, 50/5 mapping and before/after limit snapshots in `cp7/run.log`. The log subsequently records a preflight FileNotFoundError for CP5_verification.json before B starts. That file now matches the freeze byte-for-byte. The receipt is consistent with the logged run, but the run log itself does not record the restoration action or receipt creation. No claim of contemporaneous automated A-receipt creation is made.

The pre-reader CP7a3 verifier was attempted and stops at pack-directory closure because reader answers and zoom files now exist; its later pre-reader no-answers assertion is also obsolete. CP7b directly verifies the original manifest entries and preservation hashes without removing reader products. No frozen verifier was edited.

Controls: **10/10 passed**, including letters, marks and crop_ok against lead-approved caps1 control_truth.json reference values; no context voided. The key's explicit required fields letters/crop_ok also all pass. Reasons/error wording is descriptive, not an additional control target.

| Context | Control | Expected letters/marks/crop | Reader letters/marks/crop | Pass |
|---|---|---|---|---|
| segcp7_a | c046 | y/y/y | y/y/y | True |
| segcp7_a | c009 | y/y/y | y/y/y | True |
| segcp7_a | c057 | y/y/n | y/y/n | True |
| segcp7_a | c013 | y/y/y | y/y/y | True |
| segcp7_a | c026 | y/y/y | y/y/y | True |
| segcp7_b | c035 | y/y/y | y/y/y | True |
| segcp7_b | c041 | n/y/n | n/y/n | True |
| segcp7_b | c029 | y/y/y | y/y/y | True |
| segcp7_b | c072 | y/y/n | y/y/n | True |
| segcp7_b | c066 | y/y/y | y/y/y | True |

Truth is DROP iff any of neighbour_whole_word, multi_line, rotated, horizontally_missegmented is yes; otherwise KEEP. All 100 are scored; 8 reader DROP, 92 reader KEEP. Flags do not silently change this truth.

A positive prediction means the screen drops. FP = screen DROP / reader KEEP; FN = screen KEEP / reader DROP. Standalone null merged/neighbour/orientation values do not trigger that screen and are counted as non-drops; geometry-unavailable is scored separately as the fail-closed policy. Orientation uses the final sealed decision, including regional inheritance; unknown admits for orientation only. Union is screen_drop/composed.drop, excluding the separate text admission rules. Crossing is included as an additional composed constituent.

| Screen | TP | FP | FN | TN | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|
| union | 4 | 2 | 4 | 90 | 0.6667 | 0.5000 |
| merged | 4 | 0 | 4 | 92 | 1.0000 | 0.5000 |
| neighbour_words | 4 | 0 | 4 | 92 | 1.0000 | 0.5000 |
| orientation | 4 | 0 | 4 | 92 | 1.0000 | 0.5000 |
| geometry_unavailable | 0 | 2 | 8 | 90 | 0.0000 | 0.0000 |
| crossing | 0 | 0 | 8 | 92 | undefined | 0.0000 |

Rotated-miss rate: **0/4 (0.0000)**, denominator = reader rotated=yes, numerator = composed screen admits. This is segmentation admission; admission_drop also includes independent text rules and is not this metric.

Orientation provenance: {"measured": 79, "unknown": 21}.

## Unknown-axis rows

21 rows; reader DROP 1, KEEP 20.

| Row id | Reader truth | Reader rotated | Union | Sealed reason |
|---|---|---|---|---|
| elstat--0a2c92120843658d--s000-l0191 | KEEP | no | KEEP | line_block_disagreement |
| elstat--2983ce8660f4b1e0--s000-l0236 | KEEP | no | KEEP | line_block_disagreement |
| gazette_modern--b9f79d4b5629fc76--s000-l0008 | KEEP | no | KEEP | line_block_disagreement |
| gazette_modern--a93e57bdf58c5799--s000-l0104 | KEEP | no | KEEP | line_block_disagreement |
| lekythos--9447d290d59a2411--s001-l0432 | KEEP | no | DROP | line_block_disagreement |
| elstat--d8fe6ab28d6113ba--s000-l0127 | KEEP | no | KEEP | line_block_disagreement |
| elstat--ee37bc488988f1bd--s001-l0414 | KEEP | no | KEEP | line_block_disagreement |
| elstat--3b2d88122b3f037c--s000-l0159 | KEEP | no | KEEP | compact_ink |
| gazette_modern--da6dbe3e9a901b78--s000-l0090 | KEEP | no | KEEP | mixed_region_axes |
| elstat--68d11dcd7e01b0d8--s001-l0234 | KEEP | no | KEEP | line_block_disagreement |
| elstat--07520765bc203a33--s000-l0086 | KEEP | no | KEEP | line_block_disagreement |
| elstat--c5f7ea1f26d39839--s000-l0226 | KEEP | no | KEEP | line_block_disagreement |
| nlg--6ae0ac01064a587e--s007-l0013 | DROP | no | KEEP | mixed_region_axes |
| bsb_poly1850--9342f9a56a4065cd--s001-l0003 | KEEP | no | KEEP | line_block_disagreement |
| elstat--07520765bc203a33--s000-l0241 | KEEP | no | KEEP | line_block_disagreement |
| elstat--c5f7ea1f26d39839--s001-l0312 | KEEP | no | KEEP | compact_ink |
| nlg--3d71f4f87abea186--s027-l0004 | KEEP | no | DROP | line_block_disagreement |
| gazette_modern--4a698b178a4fb0b4--s000-l0107 | KEEP | no | KEEP | line_block_disagreement |
| elstat--0877c813a8512b56--s000-l0145 | KEEP | no | KEEP | line_block_disagreement |
| elstat--df38bce62200e7db--s001-l0160 | KEEP | no | KEEP | line_block_disagreement |
| gazette_modern--fe17dfd989dcb4dd--s000-l0010 | KEEP | no | KEEP | line_block_disagreement |

## Geometry unavailable: fail-closed cost

2 rows; reader DROP 0, KEEP 2.

| Row id | Reader truth | Reader rotated | Union | Sealed reason |
|---|---|---|---|---|
| lekythos--9447d290d59a2411--s001-l0432 | KEEP | no | DROP | invalid_source_frame_or_labels |
| nlg--3d71f4f87abea186--s027-l0004 | KEEP | no | DROP | invalid_source_frame_or_labels |

Adjudication: **28 unique fresh rows**; 23 flagged, 0 unreadable. Includes standalone disagreements as well as union disagreements. See `cp7/ADJUDICATION_SHEET.md` and contact sheets (at most 30 crops each). Labels remain reader truth pending the lead's pixel check.

Validation: 51 tests passed (see `cp7/pytest_cp7b.log`); input/output SHA manifest in `CP7b_COMMIT_LIST.json`. The full-population geometry and staged replay remain held for the owner.

SEG-CP7b: done | controls 10/10 | mapped 100/100 | union TP 4 FP 2 FN 4 TN 90 (P 0.6667 R 0.5000) | rotated-miss 0/4 | unknown-axis 21 (reader drop 1) | geometry_unavailable 2 (reader drop 0) | to adjudicate 28 | tests: 51 passed
