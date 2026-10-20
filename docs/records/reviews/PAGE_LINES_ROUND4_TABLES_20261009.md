# Page lines, round 4 part 1: tables — 9 October 2026

**Result: PARTIAL.** The detector and plugin changes are implemented and tested. Cases 28 and 33 recover substantial previously missing text; case 34’s upper-prose boundary defect is fixed on both named pages. The complete table acceptance gate is **not passed on any of the eight pages**. Remaining pixel omissions/crossings, missing image-layout wrappers, and incorrect TableFormer structures are measured below.

## Method and scope

Inside an image-layout table proposal, remove the observed rule strokes before rejecting connected components. This retains letters touching a table frame. Group nearby baselines, attach small marks, and split at rules, locally repeated whitespace lanes, and conservative word gaps. A divider is used only over its observed vertical extent. Refit the prose prefix independently so a lower table cannot divide the paragraph above it. A conservative fallback handles repeated ruled blocks missed by Heron.

The ordinary round-3 page fitter is unchanged. All thresholds in the production table module use x-heights or page-relative dimensions; there are no page-name branches. Page-specific coordinates occur only in annotation/review code. No PDF text or `.boxes.json` supplied the annotations. Part 2 and writing-orientation correction remain outside this change.

The plugin selector is now `recognition_mode="detector"`; inherited `OcrOptions.mode` retains Docling’s enum. Every delivered piece is unrolled and recognized separately by the existing recognizer. Narrow glyph strips receive white tensor padding without enlarging their output boxes. TextCells use explicit TOPLEFT page coordinates from the actual independent image/page x/y ratios. Replacement clears native and prior-OCR words, characters and old lines in both parsed-page and backend cached objects. V1 matching stays enabled, with Accurate as default.

The standalone review uses a declared logical page size of PNG/3. The actual DocumentConverter run uses native PNG resolution (`crop_scale=1`, because these PNGs have no DPI metadata). Different raster preprocessing can change the image model’s prediction; invariance is tested at fixed pixels within each controlled layout run, not between these two render configurations.

All 54 pages have `.segments.json`, `.lines.json`, `.checks.json`, `.cells.json`, `.lines.jpg`, and `.unrolled.jpg` in `.astra/out/`. Discounted candidates remain in JSON with reasons and are absent from both images. A table piece’s `cell_id` is explicitly a **provisional detector geometry-group ID**, not a recovered semantic grid ID.

## Owner cases

| Case | New output and measured figure | Verdict |
|---|---|---|
| 28 — V20, first two columns | 0 → 94 active pieces start left of x=637; leftmost start 637 → 55 px. Row numbers and municipality names are visibly recovered. Text completeness and currency boundaries still fail the gate below. [New image](../../../.astra/out/cases/case-28.jpg). | Improved, not fixed |
| 33 — navigation spread | Active pieces wholly left of the page midpoint: 14 → 607. Both table leaves now have substantial text; whole-page delivery grows 414 → 1,262 pieces. Remaining clipped characters, rule fragments and cross-entry pieces are enumerated. [New image](../../../.astra/out/cases/case-33.jpg). | Improved, not fixed |
| 34 — grammar **and** votes | Grammar’s opening paragraph: 6 halves → 3 full-width lines, x≈92–1143; the sentence between its two blocks is also restored from 2 pieces to 1. Votes’ first five prose rows: 10 halves → 5 full-width lines, x≈325–1778. Lower blocks remain divided. Grammar still has no Heron table wrapper; table completeness is not certified. [New image, both pages](../../../.astra/out/cases/case-34.jpg). | Fixed for the reported upper-boundary defect; tables remain incomplete |

## Annotations and measurement limits

The eight [annotation JSONs](../tables/annotations/) record extents, cell rows/columns/spans, headers, empty cells and pixel text envelopes, with source hashes. Grids and row sequences were set from page images; connected-ink envelopes were proposed independently inside them and reviewed as overlays. They are **provisional**, not exhaustive character transcriptions. Faint punctuation, touching rules, close currency subcolumns and independent panel row phases need owner adjudication. Sideways annotations were inspected in a rotated view and mapped back; detector inputs were never rotated.

“Covered” below means at least 98% of contrast pixels in an annotated text-element envelope fall inside emitted piece boxes; it is **not** OCR accuracy or proof of a correct unrolled crop. Every failed envelope is listed by cell/element ID in `acceptance/summary.json`. Crossing counts are pieces overlapping more than 20% of text envelopes in multiple annotated entries. They are provisional geometric flags; zero noise is not established.

Frozen tests inject one unique label per annotated envelope into fixed regions and run installed TableFormer V1, matching, postprocessing, and final TableItem construction. Exact row/column/span comparison is made for single-grid pages; independent panels additionally detect mixed-owner cells, but are not claimed fully grid-qualified. Their wrong-owner numbers are lower bounds. All labels surviving is explicitly insufficient.

## Each of the eight pages

| Page | New output; covered elements round 3 → round 4 | Crossing pieces round 3 → round 4 | Verdict |
|---|---|---:|---|
| **Nav** — `an-7a2b17a3fb0f-p000200` | Both leaves recovered; frame-attached digits retained, finer independent pieces. **90 → 430 / 801** | 93 → 114 | Improved, not fixed |
| **V35** — `s2-200e977f2dab5291c42c-p00035` | Ruled table resegmented; currency subcolumns and small marks remain unreliable. **116 → 124 / 267** | 29 → 20 | Not fixed |
| **V20** — `s2-831443dc5e6f1ccfbaf5-p00020` | Previously absent numbers and municipality names recovered. **258 → 308 / 621** | 181 → 180 | Improved, not fixed |
| **Side** — `s2-6419488b7f8e69fd20da-p00001` | Completes without a crash; horizontal slices remain inappropriate for vertical writing. **135 → 56 / 306** | 43 → 47 | Not fixed; orientation deferred |
| **Dense** — `an-d3237d690aa0-p000138` | Four term/locator panels receive finer pieces; fragments and row ownership remain. **336 → 359 / 455** | 130 → 68 | Improved, not fixed |
| **Grammar** — `an-a3c2bdf81256-p000112` | Upper prose restored; two local ruled blocks split; Heron still misses both tables. **88 → 40 / 88** | 36 → 0 | Prose improved; table recall worse, not fixed |
| **Votes** — `s2-80513ae109b4f749ca58-p00003` | Upper prose restored; lower list split into small pieces; incomplete names/marks remain. **63 → 47 / 66** | 16 → 1 | Prose improved; table recall worse, not fixed |
| **Budget** — `s2-dee99fdf5214acdc6f25-p00005` | Original lines retained; leader/amount crossings remain and Heron finds no table. **23 → 23 / 24** | 6 → 6 | Not fixed |

## Acceptance gate (research A and B)

PASS requires the research’s strict result, not a page-average score. Extent coverage is intersection / annotated extent area; a value below 100% does not meet full-extent coverage. All eight controlled layout runs are invariant under lines, pieces, word approximations, omitted columns, and no cells. Annotation admission is distinct from detector recall.

| Research test | Nav | V35 | V20 | Side | Dense | Grammar | Votes | Budget |
|---|---|---|---|---|---|---|---|---|
| A: discovery / OCR invariance | 2 regions; extent 98.46%/98.67%; invariant PASS; discovery FAIL | 1 regions; extent 98.65%; invariant PASS; discovery FAIL | 1 regions; extent 99.60%; invariant PASS; discovery FAIL | 1 regions; extent 99.97%; invariant PASS; discovery FAIL | 2 regions; extent 98.60%/98.14%; invariant PASS; discovery FAIL | 0 regions; extent 0.00%/0.00%; invariant PASS; discovery FAIL | 1 regions; extent 99.30%; invariant PASS; discovery FAIL | 0 regions; extent 0.00%; invariant PASS; discovery FAIL |
| A: annotation admission exactly once | 801/801 PASS | 267/267 PASS | 621/621 PASS | 306/306 PASS | 455/455 PASS | 0/88 FAIL | 66/66 PASS | 0/24 FAIL |
| A: detector-piece admission exactly once | 1259/1259 | 383/383 | 581/582 | 1365/1365 | 1086/1086 | 0/311 | 358/358 | 0/0 (no proposed pieces) |
| Pixel-to-TextCell geometry | TOPLEFT/finite/IDs PASS; 114 crossing flags; crop fit unqualified | TOPLEFT/finite/IDs PASS; 20 crossing flags; crop fit unqualified | TOPLEFT/finite/IDs PASS; 180 crossing flags; crop fit unqualified | TOPLEFT/finite/IDs PASS; 47 crossing flags; crop fit unqualified | TOPLEFT/finite/IDs PASS; 68 crossing flags; crop fit unqualified | TOPLEFT/finite/IDs PASS; 0 crossing flags; crop fit unqualified | TOPLEFT/finite/IDs PASS; 1 crossing flags; crop fit unqualified | TOPLEFT/finite/IDs PASS; 6 crossing flags; crop fit unqualified |
| Detector recall | 430/801; FAIL | 124/267; FAIL | 308/621; FAIL | 56/306; FAIL | 359/455; FAIL | 40/88; FAIL | 47/66; FAIL | 23/24; FAIL |
| Matcher isolation: Accurate / Fast | 0 lost, 0 dup, 712 wrong / 0 lost, 0 dup, 755 wrong; FAIL | 0 lost, 0 dup, 115 wrong / 0 lost, 0 dup, 203 wrong; FAIL | 0 lost, 0 dup, 621 wrong / 1 lost, 0 dup, 620 wrong; FAIL | 0 lost, 0 dup, 306 wrong / 1 lost, 0 dup, 305 wrong; FAIL | 0 lost, 0 dup, 268 wrong / 0 lost, 0 dup, 220 wrong; FAIL | 0 lost, 0 dup, 74 wrong / 0 lost, 0 dup, 82 wrong; FAIL | 0 lost, 0 dup, 39 wrong / 0 lost, 0 dup, 45 wrong; FAIL | 0 lost, 0 dup, 24 wrong / 0 lost, 0 dup, 24 wrong; FAIL |
| Source ownership | 0 stale sentinels; PASS | 0 stale sentinels; PASS | 0 stale sentinels; PASS | 0 stale sentinels; PASS | 0 stale sentinels; PASS | 0 stale sentinels; PASS | 0 stale sentinels; PASS | 0 stale sentinels; PASS |
| Full integration | 2 tables; 1 missing, 942 wrong; FAIL | 1 tables; 74 missing, 246 wrong; FAIL | 1 tables; 0 missing, 302 wrong; FAIL | 1 tables; 6 missing, 968 wrong; FAIL | 2 tables; 0 missing, 1240 wrong; FAIL | 0 tables; 310 missing, 0 wrong; FAIL | 1 tables; 0 missing, 827 wrong; FAIL | 0 tables; 24 missing, 0 wrong; FAIL |
| Real recognition (optional) | Not run | Not run | Not run | Not run | Not run | Not run | Not run | Not run |

The source-ownership controls install conflicting backend words, characters and old line labels before replacement. None survives in any frozen final table. Separate unit tests cover distinct backend/parsed caches and both native and prior-OCR words. Border-fused controls preserve retained table identity while excluding the fused label. **22/22 fused controls** retain both constituent labels exactly once in the same output cell despite their different annotated owners. This is explicitly rejected as wrong ownership: [fused-control audit](../../../.astra/out/acceptance/fused-controls-audit.json).

### Frozen structure details

| Page / table | Mode | Input labels | Grid rows × cols | Lost / duplicated / wrong-owner | Exact grid comparable? |
|---|---|---:|---|---|---|
| Nav / left | accurate | 383 | 52 × 8 | 0 / 0 / 328 | False |
| Nav / right | accurate | 418 | 31 × 9 | 0 / 0 / 384 | False |
| Nav / left | fast | 383 | 18 × 5 | 0 / 0 / 365 | False |
| Nav / right | fast | 418 | 31 × 5 | 0 / 0 / 390 | False |
| V35 / main | accurate | 267 | 42 × 8 | 0 / 0 / 115 | True |
| V35 / main | fast | 267 | 41 × 6 | 0 / 0 / 203 | True |
| V20 / main | accurate | 621 | 3 × 8 | 0 / 0 / 621 | True |
| V20 / main | fast | 621 | 38 × 9 | 1 / 0 / 620 | True |
| Side / sideways | accurate | 306 | 14 × 6 | 0 / 0 / 306 | True |
| Side / sideways | fast | 306 | 5 × 5 | 1 / 0 / 305 | True |
| Dense / left | accurate | 207 | 36 × 4 | 0 / 0 / 126 | False |
| Dense / right | accurate | 248 | 36 × 4 | 0 / 0 / 142 | False |
| Dense / left | fast | 207 | 37 × 4 | 0 / 0 / 93 | False |
| Dense / right | fast | 248 | 37 × 4 | 0 / 0 / 127 | False |
| Grammar / adjectives | accurate | 43 | 11 × 2 | 0 / 0 / 36 | False |
| Grammar / participles | accurate | 45 | 6 × 3 | 0 / 0 / 38 | False |
| Grammar / adjectives | fast | 43 | 8 × 2 | 0 / 0 / 40 | False |
| Grammar / participles | fast | 45 | 8 × 2 | 0 / 0 / 42 | False |
| Votes / votes | accurate | 66 | 15 × 3 | 0 / 0 / 39 | False |
| Votes / votes | fast | 66 | 19 × 2 | 0 / 0 / 45 | False |
| Budget / budget | accurate | 24 | 7 × 2 | 0 / 0 / 24 | True |
| Budget / budget | fast | 24 | 11 × 2 | 0 / 0 / 24 | True |

### Actual standard pipeline

Ran `DocumentConverter` on all eight full PNGs: image layout → detector plugin → layout postprocessing → Accurate V1 table stage → assembly and reading order. Only recognition was replaced by unique labels. All eight conversions complete with SUCCESS and no conversion errors; this does not mean the resulting tables are correct. The serialized documents and OCR call records are preserved. Ownership scoring uses each run’s actual TextCell rectangles and page size. Ambiguous input pieces and unmatched ink are excluded from positive ownership claims and listed separately.

| Page | Final grids | OCR pieces inside annotated extents | Ambiguous / unmatched inputs | Missing / duplicated / wrong final labels |
|---|---|---:|---|---|
| Nav | 32×8, 27×8 | 1312 | 153 / 117 | 1 / 0 / 942 |
| V35 | 3×7 | 381 | 32 / 49 | 74 / 0 / 246 |
| V20 | 3×8 | 558 | 204 / 52 | 0 / 0 / 302 |
| Side | 14×6 | 1315 | 223 / 124 | 6 / 0 / 968 |
| Dense | 2×3, 39×5 | 1779 | 390 / 34 | 0 / 0 / 1240 |
| Grammar | none | 310 | 15 / 11 | 310 / 0 / 0 |
| Votes | 15×3 | 1110 | 38 / 11 | 0 / 0 / 827 |
| Budget | none | 24 | 7 / 0 | 24 / 0 / 0 |

## Round-3 checks on all 54 pages

**46/46 non-table pages preserve the complete line-record JSON exactly, with no worsening of the measured checks.** Case 27 (`s2-93f8070059f938bda524-p00001`) retains 117 active / 12 discounted lines, 47 cut flags, 39 foreign-ink flags, and zero rule crossings, overlaps or broken pairs. Existing errors are preserved, not claimed solved. The extra part-2 page is included unchanged.

The following table includes every page. Each vector is **round 3 → round 4**. `1` = median guide p90 / borrowed lines; `2` = no-body / close pairs; `3` = cut lines; `4` = discounts; `5` = maximum boundary step (x-heights); `6` = detected / review-reference crossings; `7` = unassigned text-size components / pixels; `8` = graphic line / segment flags; `9` = broken pairs; `10` = foreign / overlap / seam-gap flags. Counts on recovered table pixels have a different denominator; increases are still explicitly flagged. Complete check-path differences, source-boundary/strip-edge counts, retained-ink fractions and source hashes are in [regression.json](../../../.astra/out/regression.json).

| Page | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Any worse? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `an-1436ae03653f-p000163` | 0.1025/8→0.1025/8 | 0/0→0/0 | 5→5 | 0→0 | 0.0586→0.0586 | 0/0→0/0 | 103/28061→103/28061 | 0/0→0/0 | 0→0 | 2/0/0→2/0/0 | No |
| `an-1be60011c435-p000215` | 0.1407/30→0.1407/30 | 0/2→0/2 | 35→35 | 1→1 | 0.0942→0.0942 | 0/0→0/0 | 159/15324→159/15324 | 0/0→0/0 | 0→0 | 30/0/1→30/0/1 | No |
| `an-1c6e1c0e929e-p000167` | 0.1476/4→0.1476/4 | 0/0→0/0 | 14→14 | 0→0 | 0.0517→0.0517 | 0/0→0/0 | 100/5599→100/5599 | 0/0→0/0 | 0→0 | 14/0/0→14/0/0 | No |
| `an-1f8e7d022643-p000003` | 0.0893/6→0.0893/6 | 0/0→0/0 | 9→9 | 3→3 | 0.0495→0.0495 | 0/0→0/0 | 44/7334→44/7334 | 0/1→0/1 | 0→0 | 8/0/0→8/0/0 | No |
| `an-2cfe28da5103-p000135` | 0.0998/14→0.0998/14 | 0/0→0/0 | 40→40 | 1→1 | 0.0972→0.0972 | 0/0→0/0 | 162/9569→162/9569 | 0/0→0/0 | 0→0 | 35/0/2→35/0/2 | No |
| `an-3352d912f2e9-p000104` | 0.1086/11→0.1086/11 | 0/0→0/0 | 16→16 | 9→9 | 0.0516→0.0516 | 0/0→0/0 | 241/35916→241/35916 | 0/1→0/1 | 0→0 | 15/0/1→15/0/1 | No |
| `an-466cffad2cba-p000323` | 0.1116/2→0.1116/2 | 0/0→0/0 | 4→4 | 0→0 | 0.0414→0.0414 | 0/0→0/0 | 7/567→7/567 | 0/0→0/0 | 0→0 | 2/0/0→2/0/0 | No |
| `an-5c093c79d6bb-p000199` | 0.1104/21→0.1104/21 | 0/1→0/1 | 13→13 | 4→4 | 0.0366→0.0366 | 0/0→0/0 | 174/13182→174/13182 | 0/0→0/0 | 0→0 | 9/0/0→9/0/0 | No |
| `an-778126cc8c2b-p000010` | 0.1105/3→0.1105/3 | 0/0→0/0 | 32→32 | 4→4 | 0.0745→0.0745 | 0/0→0/0 | 210/24676→210/24676 | 0/2→0/2 | 0→0 | 31/0/4→31/0/4 | No |
| `an-7a2b17a3fb0f-p000200` | 0.0440/405→0.0435/1256 | 0/0→123/6 | 53→39 | 15→429 | 0.0781→0.0010 | 0/0→307/0 | 335/34798→2/108 | 0/5→0/0 | 2→404 | 34/0/79→218/293/0 | **YES** |
| `an-9ea1564fcf4f-p000013` | 0.1713/14→0.1713/14 | 0/2→0/2 | 51→51 | 4→4 | 0.0821→0.0821 | 0/0→0/0 | 406/22280→406/22280 | 0/0→0/0 | 0→0 | 49/0/6→49/0/6 | No |
| `an-a3c2bdf81256-p000112` | 0.0624/44→0.0167/309 | 0/0→42/1 | 22→6 | 0→71 | 0.0439→0.0138 | 0/0→48/0 | 23/2696→3/234 | 0/0→0/0 | 0→132 | 22/0/9→60/92/0 | **YES** |
| `an-a73d22211479-p000301` | 0.0923/6→0.0923/6 | 0/1→0/1 | 71→71 | 0→0 | 0.0687→0.0687 | 0/0→0/0 | 346/25665→346/25665 | 0/0→0/0 | 0→0 | 68/0/5→68/0/5 | No |
| `an-b1a643813945-p000054` | 0.0813/11→0.0813/11 | 0/0→0/0 | 20→20 | 1→1 | 0.0509→0.0509 | 0/0→0/0 | 129/10695→129/10695 | 0/0→0/0 | 0→0 | 17/0/0→17/0/0 | No |
| `an-c153f2c605b3-p000040` | 0.0972/8→0.0972/8 | 0/1→0/1 | 12→12 | 3→3 | 0.1034→0.1034 | 0/0→0/0 | 87/18818→87/18818 | 0/0→0/0 | 0→0 | 5/0/3→5/0/3 | No |
| `an-c2c2053cfc10-p000056` | 0.1537/16→0.1537/16 | 0/0→0/0 | 32→32 | 0→0 | 0.0885→0.0885 | 0/0→0/0 | 121/8607→121/8607 | 0/0→0/0 | 0→0 | 30/0/3→30/0/3 | No |
| `an-c8b96a901917-p000068` | 0.0877/32→0.0877/32 | 0/3→0/3 | 27→27 | 12→12 | 0.0477→0.0477 | 0/0→0/0 | 154/26539→154/26539 | 0/0→0/0 | 0→0 | 20/0/2→20/0/2 | No |
| `an-d3237d690aa0-p000138` | 0.0500/279→0.0000/1081 | 0/19→158/7 | 102→46 | 2→316 | 0.0496→0.0000 | 0/0→185/0 | 313/74225→28/4878 | 0/0→0/0 | 0→721 | 71/0/107→369/469/0 | **YES** |
| `an-d6002cf45e4d-p000058` | 0.0531/5→0.0531/5 | 0/0→0/0 | 0→0 | 5→5 | 0.0077→0.0077 | 0/0→0/0 | 26/7928→26/7928 | 0/2→0/2 | 0→0 | 0/0/2→0/0/2 | No |
| `an-d6fd2cf2f618-p000047` | 0.1186/4→0.1186/4 | 0/0→0/0 | 21→21 | 2→2 | 0.0654→0.0654 | 0/0→0/0 | 173/21389→173/21389 | 2/1→2/1 | 0→0 | 25/0/1→25/0/1 | No |
| `an-d83e7a198ade-p000099` | 0.1143/8→0.1143/8 | 0/4→0/4 | 40→40 | 1→1 | 0.0853→0.0853 | 0/0→0/0 | 266/23085→266/23085 | 0/1→0/1 | 0→0 | 35/0/21→35/0/21 | No |
| `an-e46611ae2fcc-p000041` | 0.1178/11→0.1178/11 | 0/0→0/0 | 21→21 | 3→3 | 0.0655→0.0655 | 0/0→0/0 | 240/16225→240/16225 | 0/0→0/0 | 0→0 | 17/0/2→17/0/2 | No |
| `an-e74539ae215c-p000338` | 0.1032/18→0.1032/18 | 0/0→0/0 | 49→49 | 1→1 | 0.0849→0.0849 | 0/0→0/0 | 66/4721→66/4721 | 0/0→0/0 | 0→0 | 43/0/6→43/0/6 | No |
| `an-ef481610a820-p000181` | 0.1559/9→0.1559/9 | 0/1→0/1 | 28→28 | 7→7 | 0.0701→0.0701 | 0/0→0/0 | 471/69846→471/69846 | 0/0→0/0 | 0→0 | 27/0/9→27/0/9 | No |
| `an-fabf591ca801-p000067` | 0.1258/19→0.1258/19 | 0/4→0/4 | 22→22 | 2→2 | 0.0676→0.0676 | 0/0→0/0 | 62/6670→62/6670 | 0/0→0/0 | 0→0 | 17/0/1→17/0/1 | No |
| `an-fd4fa0018ae1-p000037` | 0.1189/9→0.1189/9 | 0/1→0/1 | 20→20 | 0→0 | 0.0709→0.0709 | 0/0→0/0 | 207/13782→207/13782 | 0/0→0/0 | 0→0 | 16/0/1→16/0/1 | No |
| `an-ffccc97c07de-p000152` | 0.1493/23→0.1493/23 | 0/5→0/5 | 25→25 | 9→9 | 0.0699→0.0699 | 0/0→0/0 | 224/48936→224/48936 | 0/0→0/0 | 0→0 | 16/0/15→16/0/15 | No |
| `s2-0683f98f964a6d41cb72-p00003` | 0.1420/7→0.1420/7 | 0/0→0/0 | 18→18 | 19→19 | 0.0649→0.0649 | 0/0→0/0 | 87/8807→87/8807 | 0/0→0/0 | 0→0 | 16/0/0→16/0/0 | No |
| `s2-09f5dfca4af4d74173c6-p00005` | 0.0914/16→0.0914/16 | 0/1→0/1 | 25→25 | 9→9 | 0.0586→0.0586 | 0/0→0/0 | 182/15636→182/15636 | 0/0→0/0 | 0→0 | 18/0/5→18/0/5 | No |
| `s2-0ce9d1025b3f23c7119e-p00001` | 0.2296/4→0.2296/4 | 0/2→0/2 | 29→29 | 34→34 | 0.0643→0.0643 | 0/0→0/0 | 532/64653→532/64653 | 0/0→0/0 | 0→0 | 25/0/5→25/0/5 | No |
| `s2-200e977f2dab5291c42c-p00035` | 0.0218/266→0.0153/395 | 0/34→83/5 | 41→20 | 49→317 | 0.0766→0.0231 | 0/0→119/0 | 262/88204→45/15222 | 0/0→0/0 | 1→25 | 38/0/60→104/129/0 | **YES** |
| `s2-23a70964fda83cb7aeb1-p00003` | 0.1097/12→0.1097/12 | 0/0→0/0 | 72→72 | 9→9 | 0.0476→0.0476 | 0/0→0/0 | 601/66492→601/66492 | 0/0→0/0 | 0→0 | 74/0/0→74/0/0 | No |
| `s2-3229200bf47ca465a42d-p00004` | 0.1519/9→0.1519/9 | 0/2→0/2 | 21→21 | 6→6 | 0.0762→0.0762 | 0/0→0/0 | 212/22107→212/22107 | 0/0→0/0 | 0→0 | 19/0/1→19/0/1 | No |
| `s2-49598b2e848ab1f0ee1e-p00001` | 0.1713/16→0.1713/16 | 0/4→0/4 | 35→35 | 14→14 | 0.1011→0.1011 | 0/0→0/0 | 273/34432→273/34432 | 0/0→0/0 | 0→0 | 27/0/6→27/0/6 | No |
| `s2-5ca02b142a2a3eaf078a-p00002` | 0.1054/2→0.1054/2 | 0/0→0/0 | 22→22 | 4→4 | 0.0273→0.0273 | 0/0→0/0 | 133/22415→133/22415 | 0/0→0/0 | 0→0 | 23/0/0→23/0/0 | No |
| `s2-60f24a3d8a2d714767f2-p00003` | 0.1440/17→0.1440/17 | 0/4→0/4 | 66→66 | 0→0 | 0.0983→0.0983 | 0/0→0/0 | 137/13136→137/13136 | 0/1→0/1 | 0→0 | 60/0/5→60/0/5 | No |
| `s2-63f072d79585d71224b6-p00002` | 0.1243/5→0.1243/5 | 0/0→0/0 | 15→15 | 2→2 | 0.0464→0.0464 | 0/0→0/0 | 43/5599→43/5599 | 0/0→0/0 | 0→0 | 16/0/0→16/0/0 | No |
| `s2-6419488b7f8e69fd20da-p00001` | 0.0000/324→0.0000/1459 | 0/71→195/26 | 73→73 | 41→368 | 0.0974→0.2694 | 0/0→305/0 | 396/109676→19/6460 | 0/0→0/0 | 0→489 | 54/0/67→398/568/0 | **YES** |
| `s2-658e6dcb48b540357a9d-p00001` | 0.0969/12→0.0969/12 | 0/1→0/1 | 18→18 | 48→48 | 0.0420→0.0420 | 0/0→0/0 | 184/34690→184/34690 | 0/0→0/0 | 0→0 | 14/0/1→14/0/1 | No |
| `s2-661ddf05c8865e7b2c45-p00009` | 0.1761/8→0.1761/8 | 0/0→0/0 | 47→47 | 37→37 | 0.0543→0.0543 | 0/0→0/0 | 267/32108→267/32108 | 0/0→0/0 | 0→0 | 45/0/0→45/0/0 | No |
| `s2-6f552c96213b4c24a071-p00003` | 0.1247/8→0.1247/8 | 0/0→0/0 | 17→17 | 10→10 | 0.0546→0.0546 | 0/0→0/0 | 100/9444→100/9444 | 0/0→0/0 | 0→0 | 17/0/0→17/0/0 | No |
| `s2-7247ee9b1bc2374b3980-p00001` | 0.0928/23→0.0928/23 | 0/2→0/2 | 53→53 | 19→19 | 0.0658→0.0658 | 0/14→0/14 | 406/64989→406/64989 | 0/0→0/0 | 0→0 | 52/0/25→52/0/25 | No |
| `s2-74cdb23a34ca4a6cd01e-p00002` | 0.1236/14→0.1236/14 | 0/3→0/3 | 98→98 | 59→59 | 0.0638→0.0638 | 0/0→0/0 | 1292/194100→1292/194100 | 0/0→0/0 | 0→0 | 93/0/7→93/0/7 | No |
| `s2-77d1bd63d5babbe0df73-p00001` | 0.1815/13→0.1815/13 | 0/0→0/0 | 17→17 | 0→0 | 0.1025→0.1025 | 0/0→0/0 | 76/5129→76/5129 | 0/0→0/0 | 0→0 | 12/0/1→12/0/1 | No |
| `s2-80513ae109b4f749ca58-p00003` | 0.1147/20→0.0167/352 | 0/0→57/9 | 23→24 | 5→89 | 0.0487→0.0384 | 0/0→51/0 | 88/13066→5/769 | 0/0→0/0 | 0→374 | 19/0/3→165/159/0 | **YES** |
| `s2-831443dc5e6f1ccfbaf5-p00020` | 0.0222/356→0.0176/590 | 0/61→110/6 | 47→23 | 32→388 | 0.0264→0.0450 | 0/0→157/0 | 455/161793→6/1520 | 0/0→0/0 | 0→62 | 36/0/84→127/146/0 | **YES** |
| `s2-86865c33eef5932c013b-p00005` | 0.2039/2→0.2039/2 | 0/0→0/0 | 37→37 | 2→2 | 0.0621→0.0621 | 0/0→0/0 | 100/12955→100/12955 | 0/0→0/0 | 0→0 | 36/0/0→36/0/0 | No |
| `s2-93f8070059f938bda524-p00001` | 0.1583/18→0.1583/18 | 0/2→0/2 | 47→47 | 12→12 | 0.0713→0.0713 | 0/0→0/0 | 833/82936→833/82936 | 0/0→0/0 | 0→0 | 39/0/3→39/0/3 | No |
| `s2-9de6cda8f03f0fc60a58-p00005` | 0.1302/12→0.1302/12 | 0/3→0/3 | 68→68 | 1→1 | 0.0715→0.0715 | 0/37→0/37 | 213/26976→213/26976 | 0/0→0/0 | 2→2 | 64/0/40→64/0/40 | No |
| `s2-be269b8c315b16befc35-p00002` | 0.1439/7→0.1439/7 | 0/0→0/0 | 25→25 | 1→1 | 0.0237→0.0237 | 0/0→0/0 | 108/17589→108/17589 | 0/0→0/0 | 0→0 | 23/0/0→23/0/0 | No |
| `s2-d1ed1c2db37f431f4acb-p00001` | 0.1702/18→0.1702/18 | 0/5→0/5 | 67→67 | 7→7 | 0.0685→0.0685 | 0/43→0/43 | 1483/197275→1483/197275 | 0/0→0/0 | 2→2 | 62/1/28→62/1/28 | No |
| `s2-dee99fdf5214acdc6f25-p00005` | 0.1153/5→0.1153/5 | 0/0→0/0 | 21→21 | 0→0 | 0.0458→0.0458 | 0/0→0/0 | 33/3622→33/3622 | 0/0→0/0 | 0→0 | 20/0/3→20/0/3 | No |
| `s2-dfcc21869afc140111ce-p00001` | 0.1143/23→0.1143/23 | 0/1→0/1 | 41→41 | 5→5 | 0.0454→0.0454 | 0/0→0/0 | 1163/128874→1163/128874 | 0/0→0/0 | 0→0 | 36/0/2→36/0/2 | No |
| `s2-f9ec82212abc808325d7-p00010` | 0.1847/6→0.1847/6 | 0/0→0/0 | 19→19 | 18→18 | 0.0595→0.0595 | 0/0→0/0 | 102/9290→102/9290 | 0/0→0/0 | 0→0 | 18/0/0→18/0/0 | No |

### Every page with a worsened measurement

- `an-7a2b17a3fb0f-p000200`: foreign_ink_lines 34→218, rule_gutter_crossings 0→307, boundary_overlaps 0→293, broken_line_pairs 2→404, strip_edge_touch_lines 14→30, borrowed_lines 405→1256, no_body_lines 0→123, close_pairs 0→6, lost_assigned_ink_fraction 0.0021→0.0035.
- `an-a3c2bdf81256-p000112`: foreign_ink_lines 22→60, rule_gutter_crossings 0→48, boundary_overlaps 0→92, broken_line_pairs 0→132, borrowed_lines 44→309, no_body_lines 0→42, close_pairs 0→1, lost_assigned_ink_fraction 0.0005→0.0017.
- `an-d3237d690aa0-p000138`: foreign_ink_lines 71→369, rule_gutter_crossings 0→185, boundary_overlaps 0→469, broken_line_pairs 0→721, strip_edge_touch_lines 7→37, borrowed_lines 279→1081, no_body_lines 0→158.
- `s2-200e977f2dab5291c42c-p00035`: foreign_ink_lines 38→104, rule_gutter_crossings 0→119, boundary_overlaps 0→129, broken_line_pairs 1→25, strip_edge_touch_lines 4→6, borrowed_lines 266→395, no_body_lines 0→83.
- `s2-6419488b7f8e69fd20da-p00001`: foreign_ink_lines 54→398, rule_gutter_crossings 0→305, boundary_overlaps 0→568, broken_line_pairs 0→489, strip_edge_touch_lines 13→24, source_boundary_cut_lines 63→68, borrowed_lines 324→1459, no_body_lines 0→195, maximum_jump 0.0974→0.2694.
- `s2-80513ae109b4f749ca58-p00003`: cut_ink_lines 23→24, foreign_ink_lines 19→165, rule_gutter_crossings 0→51, boundary_overlaps 0→159, broken_line_pairs 0→374, strip_edge_touch_lines 1→4, source_boundary_cut_lines 23→24, borrowed_lines 20→352, no_body_lines 0→57, close_pairs 0→9, lost_assigned_ink_fraction 0.0006→0.0023.
- `s2-831443dc5e6f1ccfbaf5-p00020`: foreign_ink_lines 36→127, rule_gutter_crossings 0→157, boundary_overlaps 0→146, broken_line_pairs 0→62, strip_edge_touch_lines 4→7, borrowed_lines 356→590, no_body_lines 0→110, maximum_jump 0.0264→0.0450, lost_assigned_ink_fraction 0.0042→0.0083.

## What still does not work

- Complete table text recall and suppression of rule/noise fragments are not achieved. Per-element omission lists and cross-entry piece IDs are saved, not averaged away. The 98% coverage test also does not certify dewarped crop completeness.
- Heron misses the grammar and budget tables. The grammar pixel fallback does not inject a TABLE wrapper into Docling, so its recovered pieces remain ordinary text. Its header above the first rule is still fused across the two paradigm panels. Budget leader/amount splitting is not implemented outside a table proposal and remains unchanged.
- TableFormer produces incorrect grids even with fixed regions and independently annotated labels. Fast is not an automatic remedy. Single-grid span errors and mixed-owner cells fail acceptance; multi-panel exact grid qualification is still incomplete.
- Annotations are provisional pixel-reviewed cell grids with automatic envelope proposals, not certified exhaustive ground truth. Currency splits, empty-cell decisions, punctuation and nested-panel spans need owner review. Semantic cell IDs are not reconstructed by the detector.
- Sideways text is still processed horizontally. This run proves it does not crash; orientation belongs to part 3.
- Real character recognition, per-cell CER and monetary transcription accuracy were not tested. No production-readiness claim is made. The 44 held-out pages were not accessed.

## Validation and reproduction

**2,022 passed, 16 skipped, 0 failed** in the full pytest suite (2,038 collected), including `tests/glyphs`, Docling contracts, provenance/API, and 12 new table tests. All 16 skips are browser-render tests because Chromium is unavailable in this sandbox. [Full test log](../../../.astra/out/tests-all-final.log). API regenerated: 211 public callable entries. All 54 artifact sets pass the saved-output audit.

Use the supplied Python from this worktree root, with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`. All commands run in the foreground; no push or model download was performed.

```sh
python scripts/generate_api_docs.py
python -m pytest -p no:cacheprovider
python .astra/layout_inventory.py
python scripts/glyphs/render_page_line_segments.py --layout .astra/layout
python scripts/glyphs/archive/annotate_tables_round4.py
python scripts/glyphs/archive/evaluate_tables_round4.py
python scripts/glyphs/archive/integrate_docling_tables_round4.py
python scripts/glyphs/archive/score_tables_round4.py
python scripts/glyphs/archive/audit_tables_round4.py
python scripts/glyphs/archive/report_tables_round4.py
```

The acceptance harness reuses `.astra/docling_research/research_tables.py` and `research_layout.py`; matcher unit tests follow `probe_matching.py`, and frozen tests follow the real-stage method of `probe_actual_stage.py`. Accurate and Fast each execute 11 real table-image forwards, reusing tensors only for identical fused controls. The layout stage executes 54 fresh full-page forwards (six variants × eight pages plus six border controls).

Evidence: [acceptance summary](../../../.astra/out/acceptance/summary.json), [delivery audit](../../../.astra/out/acceptance/delivery-audit.json), [integration summary](../../../.astra/out/integration/summary.json), [artifact/regression audit](../../../.astra/out/regression.json), [durable compact receipt](../tables/round4-summary.json). Per-label destinations, omissions, final TableItems, per-mode forward hashes and annotation hashes remain under `.astra/out/acceptance/`.

## Commit handoff

The sandbox refused creation of the worktree `index.lock` during `git add` (`Operation not permitted`), so no commit was made. The requested fallback is [page-lines-round4-tables.patch](../../../.astra/page-lines-round4-tables.patch), with [commit-page-lines-round4-tables.sh](../../../.astra/commit-page-lines-round4-tables.sh). The script verifies branch `astra/page-lines-4`, base revision, an empty staging area, every file hash, and reverse patch applicability before staging the explicit file list and committing with the requested Co-Authored-By and Claude-Session footers. It does not push. The patch is checked and replayed against a temporary copy of its HEAD source files, with byte-for-byte equality verified.
