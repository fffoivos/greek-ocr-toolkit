# Page lines round 4, part 3: orientation — 9 October 2026

## Case 35: the real sideways table

**Partial result.** The new path finds the dominant clockwise 270° writing, normalizes local views, and maps ordered word corners and guide samples back to the source page. The full Docling conversion succeeds and the adapted table is 8×15 with `Table.orientation=rot_90` (CCW). This is not a claim that its real grid or text is correct. The title and perpendicular headers remain incompletely segmented; the folio is absent in blind output.

| Part of page | Measured result | Status |
|---|---|---|
| Title | The standalone crop has the correct vertical axis but abstains between 90/270. The full-page words inherit 270° from the block; most title letters are still missed or fragmented. | Not fixed |
| «Καπνοῦ» | Oracle crop selects 180°; recognition is `Καπνο͂`, not an exact transcription. Blind discovery finds a 180° region, but its word crops are incomplete. | Orientation improved; word recovery not fixed |
| Folio | Oracle crop abstains with alternatives 0/180; blind output misses the folio. | Not fixed |
| Number rows | Most emitted numeric pieces inherit 270°; they are recognized in horizontal local views. Some digits remain split or omitted; no numeric transcription accuracy is claimed. | Improved axis handling; incomplete |
| Table | Actual Heron → oriented OCR → adapted Accurate V1 → reading order: SUCCESS, 8×15, `rot_90`. Image and tokens rotate together. | Adapter works; real structure not certified |

[Current case image](../../.astra/out/cases/r3-case-35-orientation.jpg) · [actual pipeline receipt](../../.astra/out/orientation-acceptance/s2-6419488b7f8e69fd20da-p00001.pipeline.json) · [document](../../.astra/out/orientation-acceptance/s2-6419488b7f8e69fd20da-p00001.document.json)

## Research acceptance gate

The specification was read in full from `.astra/orientation_research/REPORT.md`; the requested `docs/research/ORIENTATION_20261009.md` was not present. Fixtures were SHA-256 verified against the supplied manifest. No fixture was regenerated or altered. `evaluate_orientation_round4.py --require-gate` enforces the gate independently of unit-test success.

| Gate | This implementation | Result |
|---|---|---|
| offline/frame metadata | passed: 8; total: 8 | PASS |
| whole-page direction | axis_correct: 40; total: 40; accepted: 20; polarity_errors: 0 | PASS |
| skew controls | correct: 6; axis_correct: 12; total: 12 | **FAIL / incomplete** |
| word orientation | correct: 20; accepted: 20; total: 48; errors: 0; pasted_correct: 2; pasted_abstain: 2 | **FAIL / incomplete** |
| blind mixed discovery | passed: 2; total: 12; outside_vertical_proposals: 10; manual_word_annotations: False | **FAIL / incomplete** |
| real mixed page | crops_passed: 2; crops_total: 3; blind_full_page_coverage_certified: False | **FAIL / incomplete** |
| existing line fitter | passed: 40; total: 40; fresh_fits: 10; scope: truth-normalized fitter and inverse geometry; not polarity accuracy | PASS |
| table grid | passed: 4; total: 4; logical_labels: 48 | PASS |
| pipeline stage ordering | Both conversions SUCCESS; normalize → layout → OCR → table verified. Uniform-page normalization incorrectly vetoed as mixed. | **FAIL / incomplete** |

Whole-page accepted-polarity coverage is reported separately from axis accuracy. Unknown is never counted as a correct polarity. Skew is recorded separately; these tests do not certify deskew-angle accuracy. The 40 fitter comparisons use the labelled upright normalization to isolate the fitter, with only byte-identical normalized rasters sharing a fit (10 fresh fits). They do not certify the automatic direction decision.

The word fallback uses the plugin’s supported **compact** recognizer, `t1_compact_nfd_s0/best.safetensors`, bound to the packaged v1 codec. The newer local A32 checkpoint is not supported by this plugin’s frozen architecture registry and was not substituted. Crop preparation removes uniform external canvas before estimating grey paper/ink, normalizes contrast, then pads by 0.1 body heights, matching the recognizer’s documented ink-height policy. Both axis-consistent readings and scores are preserved. Thresholds are conservative evidence margins, **not calibrated probabilities**; production calibration remains undone.

Blind discovery uses component neighbours and rule exclusion before any horizontal fit. Its union IoU and threshold-ink coverage are scored only afterward using the fixed ROI. These are not manually annotated word precision/recall. Remaining proposals outside inserted regions and missed faint units are retained in `blind.json`.

## Code and invocation

- `greekocr/glyphs/orientation.py`: quarter-turn frames, axis/skew evidence, block polarity, optional Tesseract OSD, recognizer two-reading fallback, consistent word crops, and blind chains in both axes.
- `greekocr/glyphs/oriented_page.py`: horizontal fitting in local views, within-piece word splitting, separately addressable word IDs, and inverse-mapped corners and parametric guides.
- `greekocr/deploy/docling_plugin/orientation.py`: coherent backend adapter before layout; table-stage wrapper rotates page image/table bounds/tokens together and maps cells back while retaining logical rows/columns.
- `GlossapiOcrOptions(recognition_mode="oriented")` selects the experimental word output. Use `ImageFormatOption(pipeline_cls=OrientationPdfPipeline, pipeline_options=options)` (or the corresponding PDF format option). An OCR entry point alone cannot normalize before layout.
- Every emitted Greek TextCell has `from_ocr=True`, ordered BL/BR/TR/TL corners, and `TextDirection.LEFT_TO_RIGHT`. OCR confidence is independent of orientation confidence. Unknown cells retain alternatives and an explicitly labelled geometry hypothesis. Unknown words do not vote for table rotation. Native cached words/chars are cleared.
- `textlayer` and `detector` compatibility modes are unchanged. Because the acceptance gate fails, **oriented mode is opt-in and is not promoted as a replacement for part 2**.

## All 54 pages against part 2

**The compatibility detector’s 54 line/check records and all delivered cell records are unchanged.** Existing outputs were preserved before work in `.astra/previous_round4_part2`. New recognized orientation output is in `<key>.words.json` and `<key>.orientation.jpg`; local main-frame lines/checks are in `<key>.oriented.lines.json` and `<key>.oriented.checks.json`. `cells.json` links to the opt-in word output. Thus the following compatibility preservation is not evidence that the new word path has no regressions. Local replacement groups are not counted by the old horizontal diagnostics.

C/F/X/O/B = cuts / foreign ink / rule crossings / overlaps / broken pairs. Each old→new pair compares the part-2 compatibility output. Every changed main-frame metric in the opt-in path is listed afterward. Each page links to its new-output case image: green 0°, blue 90°, purple 180°, orange 270°, grey unknown. Arrows mark the proposed reading direction.

| Page | Part-2 C/F/X/O/B → current | Exact lines/checks/cells | New words / accepted orientation | Compatibility worse? |
|---|---|---|---:|---|
| [an-1436ae03653f-p000163](../../.astra/out/cases/orientation-an-1436ae03653f-p000163.jpg) | 4/2/0/0/0 → 4/2/0/0/0 | yes/yes/yes | 389 / 387 | No |
| [an-1be60011c435-p000215](../../.astra/out/cases/orientation-an-1be60011c435-p000215.jpg) | 27/26/0/0/1 → 27/26/0/0/1 | yes/yes/yes | 640 / 17 | No |
| [an-1c6e1c0e929e-p000167](../../.astra/out/cases/orientation-an-1c6e1c0e929e-p000167.jpg) | 14/14/0/0/0 → 14/14/0/0/0 | yes/yes/yes | 254 / 30 | No |
| [an-1f8e7d022643-p000003](../../.astra/out/cases/orientation-an-1f8e7d022643-p000003.jpg) | 9/8/0/0/0 → 9/8/0/0/0 | yes/yes/yes | 115 / 115 | No |
| [an-2cfe28da5103-p000135](../../.astra/out/cases/orientation-an-2cfe28da5103-p000135.jpg) | 40/35/0/0/0 → 40/35/0/0/0 | yes/yes/yes | 600 / 110 | No |
| [an-3352d912f2e9-p000104](../../.astra/out/cases/orientation-an-3352d912f2e9-p000104.jpg) | 16/15/0/0/0 → 16/15/0/0/0 | yes/yes/yes | 198 / 1 | No |
| [an-466cffad2cba-p000323](../../.astra/out/cases/orientation-an-466cffad2cba-p000323.jpg) | 4/2/0/0/0 → 4/2/0/0/0 | yes/yes/yes | 199 / 199 | No |
| [an-5c093c79d6bb-p000199](../../.astra/out/cases/orientation-an-5c093c79d6bb-p000199.jpg) | 13/9/0/0/0 → 13/9/0/0/0 | yes/yes/yes | 698 / 495 | No |
| [an-778126cc8c2b-p000010](../../.astra/out/cases/orientation-an-778126cc8c2b-p000010.jpg) | 32/31/0/0/0 → 32/31/0/0/0 | yes/yes/yes | 295 / 21 | No |
| [an-7a2b17a3fb0f-p000200](../../.astra/out/cases/orientation-an-7a2b17a3fb0f-p000200.jpg) | 39/218/307/293/404 → 39/218/307/293/404 | yes/yes/yes | 1623 / 18 | No |
| [an-9ea1564fcf4f-p000013](../../.astra/out/cases/orientation-an-9ea1564fcf4f-p000013.jpg) | 51/47/0/0/0 → 51/47/0/0/0 | yes/yes/yes | 961 / 816 | No |
| [an-a3c2bdf81256-p000112](../../.astra/out/cases/orientation-an-a3c2bdf81256-p000112.jpg) | 6/60/48/92/132 → 6/60/48/92/132 | yes/yes/yes | 430 / 71 | No |
| [an-a73d22211479-p000301](../../.astra/out/cases/orientation-an-a73d22211479-p000301.jpg) | 71/67/0/0/0 → 71/67/0/0/0 | yes/yes/yes | 676 / 76 | No |
| [an-b1a643813945-p000054](../../.astra/out/cases/orientation-an-b1a643813945-p000054.jpg) | 20/17/0/0/0 → 20/17/0/0/0 | yes/yes/yes | 204 / 32 | No |
| [an-c153f2c605b3-p000040](../../.astra/out/cases/orientation-an-c153f2c605b3-p000040.jpg) | 12/5/0/0/0 → 12/5/0/0/0 | yes/yes/yes | 177 / 2 | No |
| [an-c2c2053cfc10-p000056](../../.astra/out/cases/orientation-an-c2c2053cfc10-p000056.jpg) | 32/30/0/0/0 → 32/30/0/0/0 | yes/yes/yes | 790 / 130 | No |
| [an-c8b96a901917-p000068](../../.astra/out/cases/orientation-an-c8b96a901917-p000068.jpg) | 19/17/0/0/0 → 19/17/0/0/0 | yes/yes/yes | 908 / 897 | No |
| [an-d3237d690aa0-p000138](../../.astra/out/cases/orientation-an-d3237d690aa0-p000138.jpg) | 46/369/185/469/721 → 46/369/185/469/721 | yes/yes/yes | 1153 / 72 | No |
| [an-d6002cf45e4d-p000058](../../.astra/out/cases/orientation-an-d6002cf45e4d-p000058.jpg) | 0/0/0/0/0 → 0/0/0/0/0 | yes/yes/yes | 74 / 3 | No |
| [an-d6fd2cf2f618-p000047](../../.astra/out/cases/orientation-an-d6fd2cf2f618-p000047.jpg) | 21/25/0/0/0 → 21/25/0/0/0 | yes/yes/yes | 311 / 55 | No |
| [an-d83e7a198ade-p000099](../../.astra/out/cases/orientation-an-d83e7a198ade-p000099.jpg) | 40/35/0/0/0 → 40/35/0/0/0 | yes/yes/yes | 1010 / 912 | No |
| [an-e46611ae2fcc-p000041](../../.astra/out/cases/orientation-an-e46611ae2fcc-p000041.jpg) | 18/16/0/0/0 → 18/16/0/0/0 | yes/yes/yes | 333 / 68 | No |
| [an-e74539ae215c-p000338](../../.astra/out/cases/orientation-an-e74539ae215c-p000338.jpg) | 49/43/0/0/0 → 49/43/0/0/0 | yes/yes/yes | 680 / 668 | No |
| [an-ef481610a820-p000181](../../.astra/out/cases/orientation-an-ef481610a820-p000181.jpg) | 28/27/0/0/0 → 28/27/0/0/0 | yes/yes/yes | 217 / 0 | No |
| [an-fabf591ca801-p000067](../../.astra/out/cases/orientation-an-fabf591ca801-p000067.jpg) | 22/18/0/0/0 → 22/18/0/0/0 | yes/yes/yes | 558 / 133 | No |
| [an-fd4fa0018ae1-p000037](../../.astra/out/cases/orientation-an-fd4fa0018ae1-p000037.jpg) | 20/16/0/0/0 → 20/16/0/0/0 | yes/yes/yes | 256 / 253 | No |
| [an-ffccc97c07de-p000152](../../.astra/out/cases/orientation-an-ffccc97c07de-p000152.jpg) | 23/17/0/0/0 → 23/17/0/0/0 | yes/yes/yes | 299 / 297 | No |
| [s2-0683f98f964a6d41cb72-p00003](../../.astra/out/cases/orientation-s2-0683f98f964a6d41cb72-p00003.jpg) | 18/16/0/0/0 → 18/16/0/0/0 | yes/yes/yes | 383 / 371 | No |
| [s2-09f5dfca4af4d74173c6-p00005](../../.astra/out/cases/orientation-s2-09f5dfca4af4d74173c6-p00005.jpg) | 25/18/0/0/0 → 25/18/0/0/0 | yes/yes/yes | 573 / 102 | No |
| [s2-0ce9d1025b3f23c7119e-p00001](../../.astra/out/cases/orientation-s2-0ce9d1025b3f23c7119e-p00001.jpg) | 29/26/0/0/0 → 29/26/0/0/0 | yes/yes/yes | 368 / 10 | No |
| [s2-200e977f2dab5291c42c-p00035](../../.astra/out/cases/orientation-s2-200e977f2dab5291c42c-p00035.jpg) | 20/104/119/129/26 → 20/104/119/129/26 | yes/yes/yes | 517 / 503 | No |
| [s2-23a70964fda83cb7aeb1-p00003](../../.astra/out/cases/orientation-s2-23a70964fda83cb7aeb1-p00003.jpg) | 72/74/0/0/0 → 72/74/0/0/0 | yes/yes/yes | 1139 / 1139 | No |
| [s2-3229200bf47ca465a42d-p00004](../../.astra/out/cases/orientation-s2-3229200bf47ca465a42d-p00004.jpg) | 16/17/0/0/0 → 16/17/0/0/0 | yes/yes/yes | 233 / 84 | No |
| [s2-49598b2e848ab1f0ee1e-p00001](../../.astra/out/cases/orientation-s2-49598b2e848ab1f0ee1e-p00001.jpg) | 35/27/0/0/0 → 35/27/0/0/0 | yes/yes/yes | 2750 / 2700 | No |
| [s2-5ca02b142a2a3eaf078a-p00002](../../.astra/out/cases/orientation-s2-5ca02b142a2a3eaf078a-p00002.jpg) | 22/23/0/0/0 → 22/23/0/0/0 | yes/yes/yes | 354 / 350 | No |
| [s2-60f24a3d8a2d714767f2-p00003](../../.astra/out/cases/orientation-s2-60f24a3d8a2d714767f2-p00003.jpg) | 66/60/0/0/0 → 66/60/0/0/0 | yes/yes/yes | 1459 / 1443 | No |
| [s2-63f072d79585d71224b6-p00002](../../.astra/out/cases/orientation-s2-63f072d79585d71224b6-p00002.jpg) | 15/16/0/0/0 → 15/16/0/0/0 | yes/yes/yes | 386 / 386 | No |
| [s2-6419488b7f8e69fd20da-p00001](../../.astra/out/cases/orientation-s2-6419488b7f8e69fd20da-p00001.jpg) | 72/397/305/568/489 → 72/397/305/568/489 | yes/yes/yes | 726 / 688 | No |
| [s2-658e6dcb48b540357a9d-p00001](../../.astra/out/cases/orientation-s2-658e6dcb48b540357a9d-p00001.jpg) | 18/14/0/0/0 → 18/14/0/0/0 | yes/yes/yes | 326 / 315 | No |
| [s2-661ddf05c8865e7b2c45-p00009](../../.astra/out/cases/orientation-s2-661ddf05c8865e7b2c45-p00009.jpg) | 46/45/0/0/0 → 46/45/0/0/0 | yes/yes/yes | 1364 / 1344 | No |
| [s2-6f552c96213b4c24a071-p00003](../../.astra/out/cases/orientation-s2-6f552c96213b4c24a071-p00003.jpg) | 17/17/0/0/0 → 17/17/0/0/0 | yes/yes/yes | 343 / 335 | No |
| [s2-7247ee9b1bc2374b3980-p00001](../../.astra/out/cases/orientation-s2-7247ee9b1bc2374b3980-p00001.jpg) | 57/54/0/0/0 → 57/54/0/0/0 | yes/yes/yes | 855 / 852 | No |
| [s2-74cdb23a34ca4a6cd01e-p00002](../../.astra/out/cases/orientation-s2-74cdb23a34ca4a6cd01e-p00002.jpg) | 95/92/0/0/0 → 95/92/0/0/0 | yes/yes/yes | 1276 / 1269 | No |
| [s2-77d1bd63d5babbe0df73-p00001](../../.astra/out/cases/orientation-s2-77d1bd63d5babbe0df73-p00001.jpg) | 17/12/0/0/0 → 17/12/0/0/0 | yes/yes/yes | 423 / 22 | No |
| [s2-80513ae109b4f749ca58-p00003](../../.astra/out/cases/orientation-s2-80513ae109b4f749ca58-p00003.jpg) | 24/165/51/159/374 → 24/165/51/159/374 | yes/yes/yes | 509 / 500 | No |
| [s2-831443dc5e6f1ccfbaf5-p00020](../../.astra/out/cases/orientation-s2-831443dc5e6f1ccfbaf5-p00020.jpg) | 23/127/157/146/62 → 23/127/157/146/62 | yes/yes/yes | 761 / 52 | No |
| [s2-86865c33eef5932c013b-p00005](../../.astra/out/cases/orientation-s2-86865c33eef5932c013b-p00005.jpg) | 37/36/0/0/0 → 37/36/0/0/0 | yes/yes/yes | 287 / 124 | No |
| [s2-93f8070059f938bda524-p00001](../../.astra/out/cases/orientation-s2-93f8070059f938bda524-p00001.jpg) | 47/39/0/0/0 → 47/39/0/0/0 | yes/yes/yes | 1230 / 151 | No |
| [s2-9de6cda8f03f0fc60a58-p00005](../../.astra/out/cases/orientation-s2-9de6cda8f03f0fc60a58-p00005.jpg) | 65/60/0/0/0 → 65/60/0/0/0 | yes/yes/yes | 1030 / 1026 | No |
| [s2-be269b8c315b16befc35-p00002](../../.astra/out/cases/orientation-s2-be269b8c315b16befc35-p00002.jpg) | 25/23/0/0/0 → 25/23/0/0/0 | yes/yes/yes | 360 / 355 | No |
| [s2-d1ed1c2db37f431f4acb-p00001](../../.astra/out/cases/orientation-s2-d1ed1c2db37f431f4acb-p00001.jpg) | 77/77/0/0/0 → 77/77/0/0/0 | yes/yes/yes | 1129 / 398 | No |
| [s2-dee99fdf5214acdc6f25-p00005](../../.astra/out/cases/orientation-s2-dee99fdf5214acdc6f25-p00005.jpg) | 21/20/0/0/0 → 21/20/0/0/0 | yes/yes/yes | 327 / 321 | No |
| [s2-dfcc21869afc140111ce-p00001](../../.astra/out/cases/orientation-s2-dfcc21869afc140111ce-p00001.jpg) | 43/38/0/0/0 → 43/38/0/0/0 | yes/yes/yes | 1065 / 264 | No |
| [s2-f9ec82212abc808325d7-p00010](../../.astra/out/cases/orientation-s2-f9ec82212abc808325d7-p00010.jpg) | 19/18/0/0/0 → 19/18/0/0/0 | yes/yes/yes | 575 / 551 | No |

### Every main-frame increase in the opt-in orientation path

These main-frame counts exclude the additional locally replaced groups. A rotated frame changes the diagnostic denominator; increases are still disclosed.
- `s2-6419488b7f8e69fd20da-p00001`: strip_edge_touch_lines 24 → 25, guide_p90_median 0.0 → 0.013290434831564637, maximum_jump 0.2693766515475864 → 0.30843180685379445, graphic_lines 0 → 18.

## Eight table pages: new words versus part-2 acceptance geometry

The part-1/part-2 acceptance and pipeline receipts remain unchanged for compatibility mode. The new word path is measured separately below with the same provisional annotations and ≥98% contrast-ink coverage definition. **It does not meet the no-regression requirement.** Full new-path final-grid ownership has not been certified on all eight pages.

| Page | Complete elements: part 2 → oriented / total | Crossing pieces: part 2 → oriented | Elements with lower coverage | Geometry preserved? |
|---|---:|---:|---:|---|
| `an-7a2b17a3fb0f-p000200` | 430 → 403 / 801 | 114 → 109 | 241 | **NO** |
| `an-a3c2bdf81256-p000112` | 40 → 34 / 88 | 0 → 0 | 64 | **NO** |
| `an-d3237d690aa0-p000138` | 359 → 343 / 455 | 68 → 65 | 192 | **NO** |
| `s2-200e977f2dab5291c42c-p00035` | 124 → 115 / 267 | 20 → 17 | 108 | **NO** |
| `s2-6419488b7f8e69fd20da-p00001` | 56 → 126 / 306 | 47 → 96 | 60 | **NO** |
| `s2-80513ae109b4f749ca58-p00003` | 47 → 24 / 66 | 1 → 1 | 51 | **NO** |
| `s2-831443dc5e6f1ccfbaf5-p00020` | 308 → 279 / 621 | 180 → 175 | 226 | **NO** |
| `s2-dee99fdf5214acdc6f25-p00005` | 23 → 21 / 24 | 6 → 0 | 19 | **NO** |

## Artifacts, tests, and remaining work

All 54 development pages and 40 whole-page rotation fixtures have new recognized word JSON and review images. All 54 also have a case image under `.astra/out/cases/`; the combined case-35 image is linked above. Rotated outputs live in `.astra/out/rotated/`. Rotated inference reuses only SHA-256-identical normalized grayscale tensors, retains the measured automatic decision/abstention, and inverse-maps each fixture separately. It never uses fixture truth to decide output direction. The manifest labels are used only in acceptance scoring.

Full pytest: **2171 passed, 0 failed, 0 errors, 16 skipped** (2187 collected). The 16 browser skips are the pre-existing missing-Chromium skips. API regenerated. New tests cover ordered corner mapping with offsets/scales, grey-paper crop padding, numeric/garbage abstention, all 100 whole/skew/word axis fixtures, normalized fitter reversibility, actual backend metadata, the real four-turn TableFormer grid, stage wiring, and plugin confidence/LTR/source-ownership contracts. The acceptance gate remains failed despite passing unit tests.

- Short-word polarity is far below the required 46/48 decisions. The four pasted words are safe (correct or abstained), but that does not repair low standalone decision coverage.
- Blind regions miss faint inserted words/lines and parts of blocks. Local chains do not yet have source-disjoint precision/recall qualification or complete manual word annotations.
- The real title, headers and folio are not completely recovered. Numeric pieces can inherit a direction from a block, but isolated numerals cannot establish polarity.
- Full-page versus local grouping, tiny crop fitting, noise suppression, table-piece recall and integration with the horizontal diagnostics require more work. Residual skew is measured, not independently validated as deskew.
- A fresh uniform CW90 fixture (`s2-49598b2e848ab1f0ee1e-p00001__r90`) was falsely classified as mixed by the pre-layout guard. Its accepted 90-degree direction was not applied. The adapter is wired before layout and controlled tests verify its transformed backend, but automatic global normalization is not fully qualified.
- The adapter preserves controlled logical tables under rotation; it cannot correct TableFormer’s intrinsic real-grid errors. Real table token survival or SUCCESS status is not a grid acceptance result.
- No held-out pages were accessed, no model was downloaded, no push was made, and no detached/background job was started. All subprocesses were foreground tool sessions.

Every saved word was checked for finite bounded corners, inverse-frame consistency, pixel/page-unit guide consistency, explicit hypothesis status, and separate recognition confidence. Preliminary guide-unit fields were migrated with before/after file hashes; directions, recognized text, pixel boxes and review images were unchanged by that migration. Rotated views with an incorrectly shared accepted/unknown prior were rerun using the corrected cache key. These checks validate serialization, not detection accuracy.

Evidence: [compact review JSON](PAGE_LINES_ROUND4_ORIENTATION_20261009.json), [94-page geometry audit](../../.astra/out/orientation-artifact-audit.json), [gate details](../../.astra/out/orientation-acceptance/gates.json), [blind discovery](../../.astra/out/orientation-acceptance/blind.json), [word decisions](../../.astra/out/orientation-acceptance/decisions.json), [test log](../../.astra/orientation-tests-final.log).

## Reproduce

Use the Python in `.astra/BRIEF.md` with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`. The recognizer checkpoint is an explicit argument; the codec hash is verified by its loader.

```sh
python scripts/glyphs/archive/evaluate_orientation_round4.py --checkpoint "$CKPT" --require-gate
python scripts/glyphs/archive/render_orientation_round4.py --checkpoint "$CKPT"
python scripts/glyphs/archive/render_orientation_round4.py --checkpoint "$CKPT" --rotated --out .astra/out/rotated
python scripts/glyphs/archive/integrate_orientation_round4.py --checkpoint "$CKPT"
python scripts/generate_api_docs.py
python -m pytest -p no:cacheprovider -q --junitxml=.astra/orientation-tests-final.xml
python scripts/glyphs/archive/audit_orientation_round4.py
python scripts/glyphs/archive/report_orientation_round4.py
```

## Commit handoff

**No commit was created.** The authorized commit script reached `git add`, which failed with exit 128: the sandbox could not create the worktree’s `index.lock` (`Operation not permitted`). HEAD remains `f611ee2` on `astra/page-lines-4`. The 18-file patch was replayed byte-for-byte against that base, then checked in reverse. [Commit script](../../.astra/commit-page-lines-round4-orientation.sh), [patch](../../.astra/page-lines-round4-orientation.patch), and [validation receipt](../../.astra/round4-orientation-patch-validation.json) provide the requested fallback. The script verifies the branch, base revision, empty index and file hashes before committing with both requested trailers. It does not push.
