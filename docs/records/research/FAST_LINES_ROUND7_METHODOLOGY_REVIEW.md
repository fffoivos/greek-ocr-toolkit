# Round 7 task 5 — methodology review

**The default stack contains substantial explicit feature work, but its physical page model is incomplete.** Of 44 mechanism groups, 3 receive A, 26 B, 5 C and 10 D under the owner’s methodology definition. The A grades are bounded rule/contact measurements. They do not establish complete physical rows, front-ink ownership or reliable generalisation of the composed stack. D includes necessary input/detector/bookkeeping machinery; it is not a software-quality verdict or a deletion recommendation.

Reviewed commit **932027e210debf0e63b152894d2bdd727770579b** on `astra/ff-review`, default `Stack()("page.png")` (`bend=False`, `parked=False`). The current signature no longer exposes `row_model=True`; T2/T2b were historical candidates. This is a methodology review, not another assignment or follow-up plan. Code was read only, no inference/benchmark was launched, and the 44 held-out pages remain unseen.

## Standard and evidence boundaries

The criteria come from [charter §§2, 3, 5, 8](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/.astra/fast_lines/CHARTER.md) and [research §§2, 6, 7](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_RESEARCH.md). The earlier explicit detector is a conceptual skeleton: cached guides, heights, darkness and gutters can be shown on the image. Its own 54-page tuning and visibly wrong extrapolations make it neither ground truth nor a design to copy. A rendered fast output is not automatically an independent slow model. A slow implementation of the same wrong assignment rule can validate arithmetic while failing the printed page.

- **A:** real feature; slow rendering checked visually; fast route measured against it in the stated scope.
- **B:** real feature and explicit reference, but correspondence is partial, absent or demonstrably inadequate. A failed physical model can be B.
- **C:** physical intention, without an independently verified slow target; decisions built through cases.
- **D:** detector/algorithm properties, bookkeeping or case rules without a page-feature model.

Historical reports supply their own visual-review claims, named below. They are distinguished from the 12 images reopened in this task and from independently recomputed saved-data counts. No claim that I re-viewed every glyph on 208 pages is made. The source receipt matches all 225 current source files; 208 run 1 receipts carry that source key. All 208 saved T4 outputs and 15,093 items exactly match T3 final-v1. This is preservation evidence, not correctness or physical-model agreement.

Constants are treated separately from units. A measured stroke/height/pitch/noise is a page observation; choosing 0.3 of it is still a modeling choice. Gaussian MAD factors and optical-density midpoint algebra have stated derivations; their distribution/optical assumptions remain hypotheses. I do not infer deliberate page fitting merely from the existence of a number. Named regression-driven changes have evidence; other tuning provenance is unknown. No page-keyed runtime rule was found. The companion JSON gives every numeric occurrence in the indexed current function families, its source expression, classification and branch context. Historical/diagnostic branches inside those functions are explicitly included for auditability, not presented as active thresholds.

## Execution order and scope

The 44 groups preserve IDs M00–M40 and add M53–M55; retired M41–M52 are discussed only as geometry attempts. This is first-use order rather than a claim that every conditional branch runs on every page. Decode/Paddle/Q8 → ink/mirror/seal/motif/solid/discrete → edge scout → conditional printed boundaries and shared-field unbend/replacement → local geometry and joins → type/grid/residual recovery and initials → envelopes → faintness → conditional field replacement again → parent-row splitting → duplicate reconciliation → changed-footprint faintness → frame rendering/deletion → result.

M12/M13 run before the field when M11 wakes it, otherwise after local M19/M20. M14 is prepared when a native consumer needs it. M06/M08/M09/M26/M28 can recur inside recovery. M18 may run early and again after faintness. M39 stamps before M35 and checks again after M38. M40 is the cross-cutting orchestration, listed last. Library kernels (CC, interpolation, polygon Boolean operations, robust fit, filtering) are covered in their first consuming mechanism and numeric catalog rather than assigned artificial separate feature grades. Offline `round7_*` studies are evidence tools, not default-path mechanisms.

## 01. M00 — File decode, warm session and explicit parked-page input

Source: [pipeline.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/stack/pipeline.py:24).

**1. Feature.** Infrastructure: file/session state and a caller-supplied orientation exception, not a printed-page feature. Charter: none.

**2. Slow model and visual check.** None. Decoding a grayscale raster is input handling, not the charter’s explicit feature model. Historical visual evidence: Source and image hashes; no visual model is implied.

**3. Fast against slow.** 208 source-bound outputs are reproducible; this is not a fast-versus-slow feature comparison. Comparison unit: input pages.

**4. Constants and regression guards.** image_threads=2 is a compute setting (actual GCD count 10); ONNX intra/inter-op=1 is scheduling. Pixel encoding, dimensions and bounds are representation choices. No page-derived parameter. parked=True bypasses correction only when the caller supplies it. The benchmark’s named sideways page is cohort scope, not a feature detector inside Stack. Numeric source catalogue: `M00.constants.numeric_occurrences` in the companion JSON (5 occurrences).

**5. Generalisation risk.** No feature generalisation claim. Upright assumptions remain; grayscale decoding loses any colour evidence that might separate rubrication or stains. Research §7: P01, G4.

**6. Grade D.** It prepares inputs and execution state, without measuring a page feature.

Evidence: [T4](#t4).

## 02. M01 — Paddle resize, normalization and learned localization map

Source: [detector.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/detector.py:14), [paddle_db.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/paddle_db.py:22).

**1. Feature.** Algorithm property: a learned text probability map, not measured ink, font height, row baseline or front-side ownership. Charter: none.

**2. Slow model and visual check.** No slow physical feature rendering is approximated by this pretrained network in this project. R01 map visualizations expose its representation; they are not a slow physical target. Historical visual evidence: Round-1 native-contour galleries and the repeated Paddle overlays were viewed; they show localization successes and misses, not feature calibration.

**3. Fast against slow.** All 208 base localizations are exported. No page/line correspondence establishes the map as a fast approximation to a visually certified physical text model; network repeatability is a different test. Comparison unit: no physical-reference agreement study.

**4. Constants and regression guards.** 960 maximum side and 32-pixel grid are detector/sampling settings; ImageNet means (.485,.456,.406) and standard deviations (.229,.224,.225), 1/255 normalization and CPU settings are inherited model conventions. Recovery side is capped at 960 after choosing 16 samples per local h; 16 is a chosen budget, not a typography law. Crop-specific side selection responds to small-text sampling failure. No page-keyed rule, but all learned-model training/generalisation is outside this review’s evidence. Numeric source catalogue: `M01.constants.numeric_occurrences` in the companion JSON (57 occurrences).

**5. Generalisation risk.** Unquantified transfer risk for small apparatus, unusual scripts, photographs and weak ink; reducing a whole region to 960 can erase the feature before a later native guard sees it. Research §7: G1, G3, G4, G5, G6, A01, A09.

**6. Grade D.** The charter permits Paddle as a locator, but this project has not derived it from a slow page-feature model.

Evidence: [Q8](#q8), [A34](#a34), [C6](#c6), [T4](#t4).

## 03. M02 — DB threshold, contour score, expansion and quad/polygon output

Source: [detector.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/detector.py:31), [paddle_db.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/paddle_db.py:212).

**1. Feature.** Algorithm property: connected sets and scores in Paddle’s output, including expansion-induced box shape. Charter: none.

**2. Slow model and visual check.** R01, prototypes/fast_lines/native_contours/run.py, renders raw map contours, expansion and genealogy; it explicitly measures an algorithm representation, not letter ownership. Historical visual evidence: Round-1 native contour comparisons and A34 ancestry crops were viewed; joined contours and clipped marks remain counterexamples.

**3. Fast against slow.** The R1 174-page gallery and later 195/208 exports expose variants. There is no certified page-feature target for the .2/.45/1.4 choices; variant output counts are not agreement with physical rows. Comparison unit: historical detector-variant pages; no physical agreement.

**4. Constants and regression guards.** Installed map threshold .2, box score .45, unclip 1.4, cap 3000 and polygon epsilon .002×perimeter are empirical detector settings. Minimum short side 3 map pixels (5 after expansion), 32 network grid and rounding are detector/discretization choices. Other VARIANTS and DB defaults are not the installed configuration. Exact contour ancestry replaced nearest/centre assignment after neighbor-row misassociation; that fixes representation identity, not the truth of a contour. Numeric source catalogue: `M02.constants.numeric_occurrences` in the companion JSON (126 occurrences).

**5. Generalisation risk.** Expansion can join rows, cross columns and swallow accents; score has no calibrated front/back or single-row meaning. High confidence does not remove these risks. Research §7: G1, G2, G3, G4, A01.

**6. Grade D.** It transforms the learned detector’s representation rather than measuring a charter feature.

Evidence: [A34](#a34), [C6](#c6), [T4](#t4).

## 04. M03 — Height proxy, straight axes, raster/ROI primitives and call-local geometry memo

Source: [contracts.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/contracts.py:48), [geometry.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry.py:9), [geometry_memo.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_memo.py:14), [image_evidence.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/image_evidence.py:35).

**1. Feature.** Mostly detector geometry: half a rectangle’s short side is called a provisional height; it is not an observed x-height. Polygon axes and masks represent algorithm output. Charter: font properties, font geometry.

**2. Slow model and visual check.** The earlier explicit detector and offline type_profiles/type_rows render real guide and height hypotheses, but height_proxy and line_axis are not fitted or calibrated to those renderings. Historical visual evidence: C34’s false-clear 3229 p4 height and T2b’s 3229 p6 proxy/body comparison are visual counterexamples. No comprehensive proxy-to-letter calibration exists.

**3. Fast against slow.** T2b reports 46.10 px proxy versus 23 px native body on 3229 p6: nominal 12 samples/proxy becomes about 6/body. T4 memo tests and 208 exact outputs establish arithmetic/cache parity, not physical scale accuracy. Comparison unit: no per-letter scale agreement census.

**4. Constants and regression guards.** h=max(min(page size)/1000,.5×median(minAreaRect short side)); empty fallback min(size)/100 before halving. .5,100, 1000 are empirical proxies. Four IRLS iterations and Huber-like 1.5 weight cutoff are estimator choices; 1.4826 is the normal-consistent MAD conversion, not proof of Gaussian print errors. Pixel floors and small epsilons are numerical settings; memo identity has no feature constant. The memo holds strong polygon references only within compose. It adds no physical evidence. Axis selection from the first/last two x-sorted vertices can misrepresent a many-vertex ribbon even when computed exactly. Numeric source catalogue: `M03.constants.numeric_occurrences` in the companion JSON (62 occurrences).

**5. Generalisation risk.** High scale-transfer risk on two-row boxes, mixed type, large initials and curl. Every downstream h-relative threshold inherits that bias; changing detector boxes can change the supposed physical unit. Research §7: G1, G3, G6, A03, A04, A07.

**6. Grade D.** Its principal measurements are properties of detector polygons, without validation as font geometry.

Evidence: [C34](#c34), [T2b](#t2b), [T4](#t4).

## 05. M04 — Reduced printed-rule nomination

Source: [fast.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/layout_barriers/fast.py:15).

**1. Feature.** Real feature: a sustained printed vertical stroke crossing long text localizations. Box crossing is an algorithm-assisted nomination, not a physical leaf boundary. Charter: separation, tables.

**2. Slow model and visual check.** Q8 references and layout_barriers/run.py provide native paper-normalized dense rule hypotheses (R02); fast.scout approximates long-stroke evidence at reduced scale. Historical visual evidence: Q8: all 195 explicit/final overviews and all 308 accepted seam crops viewed, with page/image-bound FAST_LINES_ROUND2_REVIEW.json.

**3. Fast against slow.** Recounted 195 comparison files, 13,639 source items: 3,207 crossed by a dense hypothesis, 590 nominated, 308 ultimately cut. These are page/line comparisons, not recall because the dense hypotheses include false rules. Current scout has inherited feature thresholds; no new post-T4 physical reference census. Comparison unit: source items (13,639).

**4. Constants and regression guards.** 12 samples/h and 1200-pixel cap are sampling choices; paper mean 3h, fixed .06×255 contrast, closing .5h, widening .6h, run 12h, width≤2h, crossings≥3 with 6h end margins are empirical feature settings. h supplies scale units, but is M03’s box proxy. Power-of-two area reduction is an implementation optimization. Bridge short breaks and increase sampling after missing thin rules; grid and clear-side regressions are resolved in M05. Requiring three crossing boxes misses isolated crossings by construction. Numeric source catalogue: `M04.constants.numeric_occurrences` in the companion JSON (29 occurrences).

**5. Generalisation risk.** Moderate risk for the narrow long-rule feature; high miss risk for solitary rows, broken/faint rules, headings, unruled columns and small tables. A page with no nomination is not certified clean. Research §7: G2, G3, G5, A02, X01.

**6. Grade B.** A physical native rule rendering and complete comparisons exist, but nomination agreement is partial and the reference itself overproposes.

Evidence: [Q8](#q8), [A5](#a5).

## 06. M05 — Native straight-rule/flank verification and Q8 cut

Source: [fast.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/layout_barriers/fast.py:52).

**1. Feature.** Real sustained stroke plus nearby clear paper; grid intersections indicate a table rather than prose-column separation. Charter: separation, tables.

**2. Slow model and visual check.** Native dense rule and clear-flank rendering in layout_barriers/run.py and Q8 references; verify_rule samples the same observed corridor and correct applies its boundary. Historical visual evidence: Q8’s 308 individual native cut seams were inspected; 8314 p20 and 200e p35 currency-cell regressions and spanning-heading controls were retained. The explicit model remains a rule-specific one.

**3. Fast against slow.** All 195 pages/13,639 sources have dense/fast/action records. 308 cuts were checked at native seams; no observed new glyph cut was reported there. No scalar dense-vs-fast equality is claimed, and this is not validation of all unseen separators. Comparison unit: 13,639 sources; 308 reviewed cuts.

**4. Constants and regression guards.** .65h search, 85th-percentile paper, 2h stroke smoothing, .12 contrast and .12h residual, .85 support, flanks .22–.55h, density<.08, three horizontal intersections and ±.12h cut offsets are chosen thresholds. Robust fit uses measured stroke positions; clipping/interpolation is mathematical, but the removed corridor width is empirical. Grid intersections replaced enclosing-grid logic after unwanted currency cuts on 200e p35/8314 p20; per-cut clear flanks protect headings. These guards encode actual intersections/paper, rather than page identity, but can overprotect or reject tight genuine columns. Numeric source catalogue: `M05.constants.numeric_occurrences` in the companion JSON (68 occurrences).

**5. Generalisation risk.** Better evidence for this narrow feature than for broad layout. Faint/back rules, broken strokes and text touching a rule remain risks; a verified rule does not establish its front-side ownership in all cases. Research §7: G2, G4, A02.

**6. Grade A.** The narrow stroke-and-clear-flank feature was rendered, visually falsified and checked per source/cut against the fast path.

Evidence: [Q8](#q8), [A34](#a34), [A5](#a5).

## 07. M06 — Weak-layer nomination and reflected-glyph ownership, including recovery callers

Source: [ink_ownership.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_ownership.py:15), [ink_photometry.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_photometry.py:10), [type_ink_ownership.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_ink_ownership.py:16), [type_ink_photometry.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_ink_photometry.py:11).

**1. Feature.** Real optical attenuation and handedness of recurring glyph shapes; box-tone ranking and atlas votes are proxies for those features. “Front” is only a direct-shape hypothesis. Charter: faintness, font properties.

**2. Slow model and visual check.** B34 reference-v1/v2/v3 and reference-v4-controls render native glyphs, direct/reflected exemplars and up to 256 components per ROI. ink_photometry/glyphs and ink_ownership dense are the explicit model; the type_ink_* snapshot uses its own input census. Historical visual evidence: Enlarged raw/contrast-stretched glyph witnesses, all 61 accepted back-print removals and pale-front controls were viewed. B5 back-witness-v1 adds eight ghost pages plus the pale-front control.

**3. Fast against slow.** Recounted latest records per page: 12 distinct pages, 793 ROIs, zero dense/explicit ownership differences. The JSON has 20 versioned page records/1,187 rows and must not be called 20 independent pages. Sparse variants differ. Recovery calls use later/current boxes and a separate snapshot; there is no exhaustive 208-page dense agreement for every recovery call. Comparison unit: 793 latest-version ROIs.

**4. Constants and regression guards.** Own-page 80th-percentile tone and median anchor core are measurements. .85 anchor tone, .72 weak tone, .5 weak core, .08 contrast floor, 8h/2h widths, ≥3 anchors, max 12 anchors, 64 components and .70 silhouette are empirical. 18→22 normalized glyph tiles, .80 match, .08 margin, four votes/two-to-one and propagation via two seeds within 8h/.12 core/.4 overlap are chosen spatial/vote rules, not calibrated probabilities. Nonrecursive two-seed propagation supplies evidence to short weak rows but is a regional consistency hypothesis; it cannot turn one reflected witness into a physical ink layer. Symmetric digits and short heads remain unknown. No threshold was lowered for R5 ghosts. Numeric source catalogue: `M06.constants.numeric_occurrences` in the companion JSON (243 occurrences).

**5. Generalisation risk.** Moderate evidence for visibly asymmetric mirror recurrence, high risk on short/symmetric or mixed/blurred text and pages without strong exemplars. Different fonts and front/back type differences break the atlas assumption. Research §7: G4, G5, G6, A05, A12, A19.

**6. Grade B.** A visually checked native mirror model has exact agreement on the studied ROIs, but not for every composed/recovery use or the tone nomination.

Evidence: [B34](#b34), [B5](#b5), [T3](#t3).

## 08. M07 — Native seal-rim trace and tangent-letter exclusion

Source: [ink_seal.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_seal.py:13).

**1. Feature.** Real curved rim stroke and tangential lettering, with weak-ink nomination. A rim is not ownership of a whole stamp interior. Charter: images, faintness.

**2. Slow model and visual check.** ink_seal slow unrolls angle-by-radius native strips and traces a supported stroke; explicit reduces angular samples but keeps native radial evidence. Historical visual evidence: B5 seal-v1…v6 records false letter-loop/rim fits, and seal-ownership-v5/review-00..02.jpg records all 20 baseline explicit removal crops; composed b9d6 p255’s additional rim crop was inspected.

**3. Fast against slow.** 195 pages have slow/explicit/sparse records: native proposes 21 removals, explicit 20; c153 p56 is native-only. Sparse 48-spoke route misses verified seals and is not an eraser/negative gate. Exact radial negative bound preserves all 195 explicit decisions. Comparison unit: rim candidates and proposed line removals.

**4. Constants and regression guards.** 8 samples/h Hough nomination, Hough 40/28 parameters, 12 angular samples/h and 48 diagnostic spokes are selected budgets/thresholds. Unsupported arc<2h and ellipse residual≤measured stroke have physical meaning but chosen tolerances; radius/tangent/compactness gates are empirical. Native stroke width is measured, not an imported probability. Native radial sampling restored after reduced routes lost 1f8e p3/466 p323 rims; actual-polygon ink replaced bbox-corner rejection on dbd 045 p249. These repair feature measurement, but weak-box nomination can still miss stamp lettering. Numeric source catalogue: `M07.constants.numeric_occurrences` in the companion JSON (151 occurrences).

**5. Generalisation risk.** Moderate-to-high risk for warped, interrupted, noncircular and text-overlapping seals. Ring-shaped letters and pale front text can resemble parts of the witness. Generic images/watermarks are outside this model. Research §7: G4, G5, G6, A05, A08.

**6. Grade B.** The physical rim is explicit and visually checked, but the installed angular approximation demonstrably misses one native proposal and does not model whole-stamp ownership.

Evidence: [B5](#b5), [T3](#t3).

## 09. M08 — Coarse connected-ornament and recurrence gate

Source: [ink_motif_gate.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_motif_gate.py:12), [type_ink_motif_gate.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_ink_motif_gate.py:13).

**1. Feature.** Real repeated ink texture in a strip; detector aspect, edge/layout and scalar occupancy are nominations only. Charter: images.

**2. Slow model and visual check.** B34 native spatial repeat-field/patch-chain renderings and final motif verifier supply the reference; the cheap coarse gate is not itself image semantics. Historical visual evidence: All 11 R3 accepted ornament types and seven costly negative p11 prose strips were inspected; recurrence-v4-* fixed an overstated union-of-periods drawing.

**3. Fast against slow.** Both fast recurrence routes cover 93 full-search nominations, including 11 reviewed ornaments. Native dense support was inspected on 18 strips, not all 93; both retain 11 positives, sparse rejects seven p11 negatives. No full-image/ornament recall study exists. Comparison unit: 93 strip nominees; native study of 18 strips.

**4. Constants and regression guards.** 8 samples/h, then 16/h refinement; aspect/connected-support limits, four-copy recurrence and support/span fractions are empirical. Their values are not derived from “decoration” as a physical class. Threshold provenance is feature experiments, not independent calibration. Continuity and four-copy spatial nomination were introduced after curved prose/stamp overlap caused expensive false wakes. Border-reflection matches were removed because the repeated patch must be observed, a physically meaningful guard. Numeric source catalogue: `M08.constants.numeric_occurrences` in the companion JSON (252 occurrences).

**5. Generalisation risk.** High miss risk for disconnected, irregular, vertical and deformed ornaments; repeated letters and leaders can still nominate. A negative scout does not certify text, as the missed 7792 ornament in C demonstrated. Research §7: G4, G5, A08, X01.

**6. Grade B.** Its intended recurrence feature has a checked slow witness, but dense nomination coverage is only partial and the gate does not represent image ownership.

Evidence: [B34](#b34), [B5](#b5), [C5](#c5).

## 10. M09 — Spatial repeated-ink support and residual-glyph veto

Source: [ink_motifs.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_motifs.py:8), [ink_recurrence.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_recurrence.py:12), [ink_repeat_field.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_repeat_field.py:13), [type_ink_motifs.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_ink_motifs.py:9), [type_ink_recurrence.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_ink_recurrence.py:13), [type_ink_repeat_field.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_ink_repeat_field.py:14).

**1. Feature.** Real two-dimensional recurrence of observed ink patches, with contextual extent and remaining body-like ink; recurrence is shared by text and decoration. Charter: images.

**2. Slow model and visual check.** ink_motifs.strip, ink_repeat_field and ink_recurrence dense fields; B34 reference and round 4 recurrence render matched support on actual pixels. The type-prefixed copies use the same style of model. Historical visual evidence: Raw/matched support masks, motif controls and all accepted strips viewed. Winning-period support replaced a misleading union of unrelated periods; that was a correction to the evidence rendering itself.

**3. Fast against slow.** Dense/R1/R2 strip records exist in B34; native recurrence covers 18 selected strips and 93 fast nominations. Final 195-page equality verifies optimization preservation, not a complete independent dense census of all potential ornaments. Comparison unit: 18 native strips; 93 nominations; 195 output parity pages.

**4. Constants and regression guards.** Template sizes/lags/context in h, correlation thresholds, occupancy/support fractions and four-copy chain are empirical modeling choices. FFT peaks are computational proposals; actual supported pixels are measured. Residual-glyph size/area cutoffs assume ordinary typography and are not a learned image class. Full spatial evidence replaced whole-strip autocorrelation; observed-patch bounds and winning-period accounting reject numerical artifacts. Residual-glyph protection handles text amid ornament but misses filled or touching letters. Numeric source catalogue: `M09.constants.numeric_occurrences` in the companion JSON (274 occurrences).

**5. Generalisation risk.** High transfer risk on engravings/hatching, distorted ivy, repeated letters and text inside frames. c99 p25 upper ivy fails the rigid-template model despite being visibly decorative. Research §7: G4, G6, A08, A12.

**6. Grade B.** The rendered spatial feature is real and falsifiable, but comparisons cover selected motifs and do not establish general non-text ownership.

Evidence: [B34](#b34), [B5](#b5), [T3](#t3).

## 11. M53 — Compact isolated solid-mass nomination and native disk/counter test

Source: [ink_solid.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_solid.py:18).

**1. Feature.** Real filled stroke mass, inscribed radius, counters and local isolation. The inference that the whole detector box is non-text remains a shape hypothesis. Charter: inkiness, images.

**2. Slow model and visual check.** ink_solid.render measures native Otsu silhouette, largest interior disk and enclosing extent; T3 solid-v1/v2 draws the disk and controls. T4 keeps this native route after deleting the failed reduced variant. Historical visual evidence: T3 solid-v2 blob crop was viewed again in this review (V3): an isolated dark filled mark with no visible counter. Reduced e259 p176 false positive was inspected in T3; the small counter vanished on reduction.

**3. Fast against slow.** Recounted T3 census: 208 pages, 15 geometry nominees, exactly one native positive (922e p1), two reduced positives (plus e259 p176). Current T4 uses native confirmation directly and preserves the T3 deletion exactly. This is one positive example, not broad inkiness validation. Comparison unit: 15 nominated segments; 1 native positive.

**4. Constants and regression guards.** Extent h/2–2h, isolation≥2h, disk radius≥h/4 and enclosing distance≤2r are empirically selected physical ratios. Otsu threshold and r are measured per crop; no-counter test is observed topology. Padding/connectivity/distance-transform masks are numerical choices. h is still a detector proxy, despite the docstring’s “measured” phrasing. Median ridge width failed on the ragged blob, prompting connected interior/enclosing disks. Native confirmation became mandatory after downsampling filled e259’s counter. These address real geometry, but the positive design is shaped on the one owner blob. Numeric source catalogue: `M53.constants.numeric_occurrences` in the companion JSON (50 occurrences).

**5. Generalisation risk.** High risk for filled bullets, heavily over-inked isolated numerals or symbols. It measures compactness, not unreadability or whether an observed mass originated as text. Research §7: G4, G6, A08, A10, A12.

**6. Grade B.** An explicit native mass rendering and reduced counterexample exist, but the class decision has only one native positive and no general text-versus-mass model.

Evidence: [T3](#t3), [T4](#t4).

## 12. M10 — Disconnected motifs with border/layout nomination

Source: [ink_discrete_motifs.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_discrete_motifs.py:13).

**1. Feature.** Real repeated connected-component topology and neighboring layout gaps; page-edge position alone is not non-text. Charter: images.

**2. Slow model and visual check.** ink_discrete_motifs native contour concavity, measured stroke width and symmetric shape-distance evidence, then M09 spatial verification for horizontal groups. Historical visual evidence: B5 discrete-v4…motifs-v8 visual sequence includes filled flowers and the four real quotation marks on 8686 p7; all 25 horizontal native groups were compared.

**3. Fast against slow.** 195-page census: 25 horizontal native groups, five positive borders and 20 negatives agree with explicit confirmation. Layout nomination shrank 1,187 candidates to 92 and retained the five positives; native-positive vertical groups were not admitted. Reduced component-only route misses flowers. Comparison unit: 25 horizontal groups; five positives.

**4. Constants and regression guards.** Native contour concavity relative to measured stroke, h-scaled area/extent/alignment and recurrence counts/fractions are selected model settings. One-h gaps/page-edge layout and four-copy checks are empirical; they do not derive a decorative class. Allow filled siblings when a lobed seed exists; reject standalone vertical deletion after true quotation-mark counterexample. Layout scout was added for cost after the ordinary-row census proved expensive, and excludes potential inline ornaments. Numeric source catalogue: `M10.constants.numeric_occurrences` in the companion JSON (218 occurrences).

**5. Generalisation risk.** High risk on new motifs, connected/damaged flowers, quotation marks, leaders and inline decoration. Matching a lobed shape is not a glyph/non-glyph distinction. Research §7: G4, G6, A08, X01.

**6. Grade B.** A checked physical component model exists with measured horizontal-group agreement, but layout recall and vertical ownership remain unresolved.

Evidence: [B5](#b5), [T3](#t3).

## 13. M11 — Outer-third map-ridge coherence scout for the shared page field

Source: [geometry_edge_map.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_edge_map.py:13).

**1. Feature.** Intended common binding bend, sampled from the outer thirds of detector-map ridges relative to an inner affine tangent. The actual ridge/threshold is an algorithm representation, not native letter geometry. Charter: binding curvature, skew.

**2. Slow model and visual check.** geometry_page_field.render/certify provides native profile registration, row paths and edge certificates (C6); geometry_edge_map.scout is its cheap detector-map nomination. Earlier cached model guides are rendered by features_geometry/reference.py, not assumed to be truth. Historical visual evidence: A34 bend galleries and pure-skew controls were inspected; native R6 field galleries expose two-leaf failures. This review re-viewed e259 p198 (V12).

**3. Fast against slow.** Recomputed C6 on 208 pages:71 native-field positive pages, 73 scout positive pages, 39 shared (34 scout-only, 32 native-only). These are model disagreements, not 32 proved missed real bends. The ledger has 20,509 edge comparisons; no independent all-endpoint ground truth exists. Comparison unit: page trigger decisions; native row matches in M15.

**4. Constants and regression guards.** Width≥12h; 65 offsets over±4h but peak choice restricted to±h; horizontal sampling about one/h across a box plus one-third each side; map support .3; ≥4 inner-third points; three-sample end average; deviation>.35h; ≥3 coherent neighbouring endpoints within 6h horizontally/8h vertically. All are empirical sampling/coherence choices. The affine least-squares formula is mathematical; its selected samples and DB support threshold are not physically derived. Three neighbouring endpoint departures of the same sign reject isolated local wiggles. A narrow peak cannot follow a departure beyond its allowed±h band. This is a feature-motivated but unvalidated nomination boundary, not a physical correction certificate. Numeric source catalogue: `M11.constants.numeric_occurrences` in the companion JSON (47 occurrences).

**5. Generalisation risk.** High false-negative risk for weak/short rows, sharp curl outside sampled columns, DB ridge hops and tiny type; headings or two leaves can create false shared-bend expectations. Research §7: G3, G5, A03, A04, X01.

**6. Grade B.** A physical bend reference exists, but the scout samples a detector representation and its physical-reference agreement is incomplete.

Evidence: [A34](#a34), [C6](#c6), [T4](#t4).

## 14. M12 — Native straight/curved rule verification and grid rejection

Source: [geometry_feature_rules.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_feature_rules.py:15).

**1. Feature.** Real elongated printed stroke, continuity, curvature and intersections; the semantic interpretation as a front column boundary is separate. Charter: tables, separation.

**2. Slow model and visual check.** layout_barriers.fast.verify_rule plus geometry_feature_rules.curved_rule/grid_intersections render native stroke paths and crossbars; R02 and A34/A5 rule panels are explicit witnesses. Historical visual evidence: A34/A5 native rule panels include 661d, a0e, 922e and verso/grid controls. V9 shows a true central divider with real text endings.

**3. Fast against slow.** Historical Q8 census and A5 column study cover the rule pipeline; 52 later column witnesses agree native/vectorized. This does not measure all possible curved rules or distinguish front from verso without M13. Comparison unit: 52 column certificates plus historical Q8 census.

**4. Constants and regression guards.** Lengths/widths/windows in h, selected sampling density, continuity/residual tolerances and ≥3 grid intersections are empirical shape definitions. Local grayscale contrast is measured; fixed thresholds and quantiles are not derivations from ink physics. See numeric catalogue for all sampled windows and stroke predicates. Grid veto followed 200e/8314 tables; curved tracing followed bent rules missed by straight Hough. Grid intersections encode a feature, but a blanket grid exclusion does not model table cells. Numeric source catalogue: `M12.constants.numeric_occurrences` in the companion JSON (114 occurrences).

**5. Generalisation risk.** Medium/high risk on faint broken rules, wide ornaments, dense crossbars and verso lines; a real stroke does not establish which text it separates. Research §7: G2, G4, A02, A17.

**6. Grade B.** A visible native rule model exists, but coverage and front-side semantic agreement are partial.

Evidence: [Q8](#q8), [A34](#a34), [A5](#a5).

## 15. M13 — Bilateral column termination certificate and shared-edge split

Source: [geometry_columns.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_columns.py:16).

**1. Feature.** Printed column boundaries inferred from repeated row endings on both sides of a real rule, plus absence of a native stroke crossing it. Detector endpoints supply some observations. Charter: separation.

**2. Slow model and visual check.** geometry_columns.termination_witness/native_crossings slow loops draw row endpoints and every crossing; vectorized route computes the same native conjunction. Applied splits share the rule centre edge. Historical visual evidence: A5 corrected column panels and owner close-column comments were checked. V9 rechecks 661d p5; c8 p36 rho and a0e p2 end strokes motivate shared rather than eroded boundaries.

**3. Fast against slow.** Recomputed A5 ledger: 52 certificates are exactly equal between slow and vectorized native routes. Reduced route disagrees on seven certificates in six pages. The 200-page census includes 11,011 line records, but there are only 52 certificate comparisons. Comparison unit: 52 certificates; reduced route has seven disagreements.

**4. Constants and regression guards.** Rule≥12h, width≤4h, cross extent 6h, row width>8h, endpoint distance<1.5h, ≥3 distinct endings spaced>2h spanning≥12h, paired rows within h, .12 local contrast and ±.3h connected crossing are empirical physical ratios. Nine samples fit the local split, .5h duplicate-rule tolerance is selected. No multiplier is derived just by naming h. Native crossing test followed a verso-rule false split; paired endings tightened it later. Positive endpoint evidence excludes already suppressed sources. Shared centre boundary followed loss of c8’s rho and related close-rule ink; these guards address observable stroke/contact features. Numeric source catalogue: `M13.constants.numeric_occurrences` in the companion JSON (98 occurrences).

**5. Generalisation risk.** Medium risk for broken rules, touching letters genuinely crossing a divider, missing endpoint localizations, tables and nonparallel columns. Exact witness parity is strong evidence for this restricted physical predicate, not all column structure. Research §7: G2, G4, A02, A17.

**6. Grade A.** Its bounded native crossing/termination rendering was visually checked and the fast native certificate was compared exactly across the recorded census.

Evidence: [A5](#a5), [T4](#t4).

## 16. M14 — Native paper/ink components and body-contact preparation

Source: [geometry_contacts.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_contacts.py:17).

**1. Feature.** Local contrast, connected ink and plausible body-sized components; thresholded components are observations, not identified letters. Charter: font geometry, inkiness.

**2. Slow model and visual check.** geometry_contacts.prepare/trace has dense native masks, labels, contacts and ambiguity strips in A34; supplies page-field and envelope paths too. Historical visual evidence: A34 contact strips and A5 dense envelopes were inspected, including accents, touching type and boundaries. These show component geometry, not ground-truth glyph identities.

**3. Fast against slow.** 195-page A34 comparison: connected-component renderings identical and 9,086 path comparisons; 13 differ by at most .0625h (p90 zero). This validates the implementation of the threshold model. It does not validate every body/noise decision against letters. Comparison unit: 9,086 path comparisons.

**4. Constants and regression guards.** Local paper windows (including 4h), absolute .08×255 darkness, h-scaled area/extent bands, row-search ranges and density smoothing are empirical. Labels/areas/contacts are directly measured after thresholding; they inherit the detector h. Native connectivity and pixel floors are representation choices. Ambiguous support is recorded rather than averaging through two rows. Filtering sustained components avoids rules determining row identity, but their ink may still participate in retention. Numeric source catalogue: `M14.constants.numeric_occurrences` in the companion JSON (45 occurrences).

**5. Generalisation risk.** Medium/high risk for faint fronts, dark paper, joined glyphs, accents and mixed heights. Absolute darkness differs materially from later relative faintness and Otsu models. Research §7: G4, G6, A03, A07, A10, A12.

**6. Grade B.** It renders real ink geometry with strong arithmetic agreement, but the physical interpretation of body components remains only partially checked.

Evidence: [A34](#a34), [A5](#a5), [C6](#c6).

## 17. M15 — Shared page-field mesh, row phases and native edge certificate

Source: [geometry_page_field.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_page_field.py:16).

**1. Feature.** Intended smooth deformation shared across rows, with phases and observed native body ridges; text-block domains still derive from detector boxes. Charter: binding curvature, skew, font geometry.

**2. Slow model and visual check.** geometry_page_field.render/certify and invert_points implement native profile registration, mesh/phase paths and edge certificates; C6 renders these and reduced routes. features_geometry/reference.py separately draws cached earlier-detector guides; no claim that the native mesh is that detector’s verified geometry. Historical visual evidence: C6 galleries checked; V12 rechecks e259 p198 where two leaf systems are crossed by mutually similar fitted paths. Similar rendered routes can share a physically wrong domain.

**3. Fast against slow.** Recomputed 208-page ledger: 14,949 predicted native rows, 13,712 matched, 1,237 unmatched; 20,509 edge records. Matches and native edge certificates are partly conditioned on the fitted field. No independent all-row, one-to-one baseline agreement; scout disagreement is in M11. Comparison unit: 14,949 predicted rows; 13,712 matches.

**4. Constants and regression guards.** Long-box width 8h, block support≥4 and width 12h, nominal empty channels 2h, mesh knot density/regularization, native sampling steps and ridge/phase tolerance are selected physical priors. They are not derived material properties. Robust fitting measures shifts but its smoothness and shared-field hypothesis are imposed. Separate supports/empty channels were added after spanning-gap failures; box envelopes can fill the very gutter used to separate domains. Native certificates protect local support but do not independently establish leaf segmentation. Numeric source catalogue: `M15.constants.numeric_occurrences` in the companion JSON (204 occurrences).

**5. Generalisation risk.** High risk for two leaves, mixed font phases, local folds, ghost lattices and unconstrained blank spans. Extrapolated paths can look smooth while representing no printed row. Research §7: G2, G4, G5, G6, A03, A04, A15.

**6. Grade B.** A substantial slow physical-field rendering exists with partial route comparisons, but its domains and row correspondence are not fully validated.

Evidence: [C6](#c6), [T2c](#t2c), [T4](#t4).

## 18. M16 — Field-based image unbending and regional Paddle rerun

Source: [geometry_field_detector.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_field_detector.py:9).

**1. Feature.** Real geometric remapping intended to straighten distorted print; the subsequent detector is still M01/M02. Charter: binding curvature, skew.

**2. Slow model and visual check.** geometry_field_detector.unbend remaps native pixels through the shared field; C6 rectified-region images and remapped polygons render the transformation. The older detector’s cached guides provide a separate geometric view, not proof of this rectification. Historical visual evidence: C6 rectified crops and owner curl cases were viewed. Unlike T2c, this route does actually make a rectified image; that alone does not validate its field.

**3. Fast against slow.** C6 supplies 208-page field ledgers and selected corrected rows. No complete R09 scale-only/unbend-only/combined factorial comparison or independent row-by-row OCR ownership agreement was found. T4 exact output equality confirms preservation only. Comparison unit: selected rectified regions; no isolated all-page R09 agreement.

**4. Constants and regression guards.** Mesh interpolation, .4h horizontal sampling, padding including .06h and raster rounding are selected representation settings. Crop sampling budget and 960 detector side are M01 choices. Interpolation is mathematically defined once the unverified field is chosen. Native ownership/band and retention checks are applied after rerun. No guard can reconstruct a native stroke already erased by low-resolution resampling. Numeric source catalogue: `M16.constants.numeric_occurrences` in the companion JSON (36 occurrences).

**5. Generalisation risk.** High risk where field domains merge leaves, local folds exceed smoothness, tiny type is resampled away or the rerun relocalizes the same errors. Two Paddle runs are not independent physical evidence. Research §7: G2, G3, G5, A04, A09, A15.

**6. Grade B.** It explicitly renders the intended physical transformation, but its fast localization benefit and one-row correspondence were not separately measured against a certified slow target.

Evidence: [C6](#c6), [T4](#t4).

## 19. M17 — Native components assigned to rectified row bands

Source: [geometry_field_detector.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_field_detector.py:54).

**1. Feature.** Real component-to-row proximity interpreted through a rectified detector axis; this is a proposed ownership model, not measured glyph identity. Charter: font geometry, separation.

**2. Slow model and visual check.** geometry_field_detector.native_bands/separate_bands/native-band records draw assigned components and resulting ribbons. No separately certified slow assignment of every glyph/mark to its true row was found. Historical visual evidence: C6 native band panels expose competing rows and missed end support; visual checks are selected corrected examples, not an exhaustive assignment atlas.

**3. Fast against slow.** Developed through C6 curl and retention failures. Output and component masks are exported, but no independent page/line assignment agreement denominator exists. Comparison unit: case-based band decisions.

**4. Constants and regression guards.** Nearest-axis tolerance .75h, winner margin .15h, local=max(h,.65×box short side), body height .3–2h, width 5h, area .025h², mark distance .45h and other extent limits are empirical. h-relative units make them portable in scale only. Another-row field_ready guard and uncertainty rejection protect against multirow proposals; they test this same assignment model, not an independent full-row rendering. Numeric source catalogue: `M17.constants.numeric_occurrences` in the companion JSON (181 occurrences).

**5. Generalisation risk.** High risk for diacritics, touching components, variable font sizes, curved tails and fragments nearer a wrong detector axis. Research §7: G1, G2, G6, A03, A07, A12.

**6. Grade C.** It proposes a real row-ownership feature, but its class and assignment thresholds were built through cases without independent slow assignment truth.

Evidence: [C6](#c6).

## 20. M18 — Old-to-new field ownership, horizontal-source veto and fixed-point retention

Source: [geometry_field_selection.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_field_selection.py:9).

**1. Feature.** Predominantly detector lineage/count/overlap and conservation of the previous output. Pixel retention is useful evidence preservation but is not a model of which printed row owns it. Charter: none.

**2. Slow model and visual check.** geometry_field_selection.apply renders masks, dominant label votes and lost pixels. This is an explicit algorithm audit, not a slow page-feature skeleton. Historical visual evidence: C6 and R6 loss crops, including 9ea p170 independent horizontal sources, were checked; T4 trial ledgers expose c8 p36 loss.

**3. Fast against slow.** Native lost-ink checks and 208-page output parity exist. Neither proves correct physical row reassignment. No page/line comparison to an independent ownership rendering exists. Comparison unit: output conservation tests.

**4. Constants and regression guards.** Votes≥.8 of maximum, old-source width>8h, 3×3 dilation, accepted rule mask .4h, component area≥max(2,.004h²), geometric 1e-6 tolerance are chosen safeguards. Fewer new than old owners plus disjoint source-centre intervals is a detector partition rule. Fixed-point retention followed mutually certifying losses; initial/already-field protections prevent reprocessing. Separate-horizontal-sources guard followed cross-column joins, but can also block two fragments of one bent row. These are operational case guards, not leaf/row features. Numeric source catalogue: `M18.constants.numeric_occurrences` in the companion JSON (33 occurrences).

**5. Generalisation risk.** High risk of locking in wrong Paddle partitions or protecting noise as text, while sub-threshold thin strokes can still escape the conservation mask. Research §7: G1, G2, G5, A03, A04.

**6. Grade D.** Its decisions are anchored to prior detector ownership and conservation rules, without a physical row-identity model.

Evidence: [C6](#c6), [R6](#r6), [T4](#t4).

## 21. M19 — Per-line sparse DB ridge scout and affine/residual measurement

Source: [geometry_scout.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_scout.py:15).

**1. Feature.** Physical baseline/body path approximated first by a detector probability ridge, then checked/refined through native ink contacts; the ridge is not a baseline. Charter: binding curvature, skew.

**2. Slow model and visual check.** geometry_feature_paths.sparse/describe and dense bands, plus independent geometry_contacts native strips; features_geometry/reference.py renders cached earlier-model baseline/meanline guides. The source calls its scale DB band. Native references can themselves be wrong. Historical visual evidence: A34 dense native/DB path figures include ridge hops and pure-skew controls. A5 owner envelopes highlight hilly fits when a local path follows glyph rather than line geometry.

**3. Fast against slow.** A34 supplies 195 pages and 13,639 source-item comparison records, including absent and ambiguous guide matches. Its batched sparse route matches prior arithmetic/dispatch, not certified physical row truth. Native contact route comparison has 9,086 paths (M14/M22). No independent full baseline agreement count exists. Comparison unit: rendered path census; physical truth partial.

**4. Constants and regression guards.** 19 columns ×31 offsets over±1.5h; width≥12h/height≤6h; peak penalty .15, continuity penalty .03 and jump≤4 bins; support>.3, band edge .2; ≥6 supported inner samples; central .25–.75 span and three-point same-sign endpoints; bend>.3 DB-band heights or skew>.6. Tilted fragments 2–12h, slope>.08, gap−.5–2h and ≥3 fragments also wake correction. These are empirical detector-map/model settings. Four-iteration robust affine fit is an estimator; 1.4826 is MAD normal-consistency. T4 1e-8 replay at fragile decisions preserves arithmetic, not a new physical feature. Same-sign endpoint and central fitting reduce glyph noise; pure-skew controls exposed width/bend confusion. Ambiguous/native unsupported paths may abstain rather than authorize trimming. Numeric source catalogue: `M19.constants.numeric_occurrences` in the companion JSON (155 occurrences).

**5. Generalisation risk.** Medium/high risk on bold caps, double ridges, accents, weak endpoints and mixed script; local path and shared page mesh can disagree even on one crop. Research §7: G1, G6, A03, A04, A07.

**6. Grade B.** Real path renderings and comparisons exist, but detector-ridge to physical-row agreement is incomplete.

Evidence: [A34](#a34), [A5](#a5).

## 22. M20 — Local geometry correction, component completion and original-ink retention

Source: [geometry_context.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_context.py:17), [geometry_feature_correct.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_feature_correct.py:18), [geometry_feature_paths.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_feature_paths.py:16).

**1. Feature.** Real row envelope and native covered ink, conditioned on one old localization; does not solve the whole-page row topology. Charter: binding curvature, font geometry.

**2. Slow model and visual check.** geometry_feature_correct helpers plus stack.geometry build native component envelopes and before/after loss masks from M14/M19; A34/A5 path galleries are the slow witness. Historical visual evidence: Owner curl/width/too-tall crops and native retention overlays were checked, including 3229 p6 and c0b02 p10; R6 integration still documents cropped ends.

**3. Fast against slow.** Component/path route comparisons are M14/M33. No separate all-page agreement for the combined correction/rollback decision against adjudicated final rows; it evolved from approved and regressed cases. Comparison unit: primitive parity plus selected corrections.

**4. Constants and regression guards.** Expansion, component membership, support width, lost-ink windows and padding are h-relative empirical settings; threshold masks and chosen contact percentiles determine which faint accents count. Integer dilation/floors encode tolerance, not a measured glyph margin. keep_nearby_ink and retention preserve established ink after aggressive fits; safe original outlines on ambiguity are a fallback to an algorithm box. These are conservation guards around a physical envelope model. Numeric source catalogue: `M20.constants.numeric_occurrences` in the companion JSON (159 occurrences).

**5. Generalisation risk.** High risk for faint marks below threshold, multirow parents, large initials and sharp terminal curls. Conserving old pixels can preserve an incorrect crop topology. Research §7: G1, G2, G4, A03, A07, A12.

**6. Grade B.** Its physical envelope primitives have explicit renderings, but the combined correction and rollback policy lacks complete independent row agreement.

Evidence: [A34](#a34), [A5](#a5), [R6](#r6).

## 23. M21 — Angled short-fragment and Hermite box-join nomination

Source: [geometry_fragments.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_fragments.py:8).

**1. Feature.** Detector box gaps, tangent angles and widths; these are not direct evidence that printed glyphs lie on one row. Charter: none.

**2. Slow model and visual check.** A34 overlays candidate box joins and hypothetical Hermite curves; that is an algorithm proposal drawing, not an independently observed row path. Historical visual evidence: Rejected join galleries show that attractive smooth curves can bridge separate rows; physical endpoint evidence is supplied only later by M22/M23.

**3. Fast against slow.** A34 candidate comparisons informed rejection of unsafe joins; no box-only fast-versus-physical-slow calibration proves same-row identity. Comparison unit: algorithm candidate studies.

**4. Constants and regression guards.** Short/long widths, angle, gap and vertical-overlap limits in h, three-fragment wake and Hermite interpolation are proposal heuristics. No physical law derives the cutoffs. Cheap box nomination survives only ahead of native contact verification; the gate can still miss the true partner before verification. Numeric source catalogue: `M21.constants.numeric_occurrences` in the companion JSON (77 occurrences).

**5. Generalisation risk.** High risk of joining headings/columns or failing unlocalized tails; geometrically compatible boxes can be unrelated printed rows. Research §7: G2, G5, A03, A04, X01.

**6. Grade D.** The nomination is based on detector shapes rather than an observed printed-page feature.

Evidence: [A34](#a34), [A5](#a5).

## 24. M22 — Native endpoint paths and tangent agreement

Source: [geometry_contacts.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_contacts.py:60).

**1. Feature.** Real ink-supported endpoint direction and continuity across a small gap, rather than box-edge direction. Charter: binding curvature, font geometry.

**2. Slow model and visual check.** geometry_contacts dense endpoint paths and geometry_contact_cache; A5 tangent contour/contact renderings compare scalar and vectorized implementations. Historical visual evidence: A34 join panels and A5 tangent strips show support/alternatives, including ambiguous nearby rows.

**3. Fast against slow.** Recounted A34:195 pages, 9,086 native/R1 paths; 13 differ by at most.0625h. The 69 R2 fragment-pair comparisons include 46 native_agrees=true and 23=false, not 69 agreements. Independently recounted A5:200 pages, 71 tangent-bearing lines, 12,386 samples and 77 alternatives exactly equal between explicit and fast native route. Grade A applies to the installed native/R1 measurement, not the rejected coarser R2 nomination. Comparison unit: 71 lines /12,386 samples /77 alternatives exact R1; 69 historical R2 pair comparisons (46 agree, 23 disagree).

**4. Constants and regression guards.** Strip span and offset windows, contact quantiles and tangent fit length in h are empirical measurement resolutions; exact fast route preserves them. Four robust-fit iterations/MAD choices are estimator constants, not row semantics. Independent end support replaced extrapolated box tangents. Ambiguity is retained as alternatives, so a plausible tangent alone cannot certify a join. Numeric source catalogue: `M22.constants.numeric_occurrences` in the companion JSON (150 occurrences).

**5. Generalisation risk.** Medium risk on touching glyphs, short/noisy endpoints and faint ink; a locally correct tangent does not prove long-range row identity. Research §7: G4, G6, A03, A07, A12.

**6. Grade A.** The restricted native endpoint measurement was rendered, visually checked and compared sample by sample to the fast route.

Evidence: [A34](#a34), [A5](#a5).

## 25. M23 — Fragment join authorization and column/rule protection

Source: [geometry_fragment_correct.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_fragment_correct.py:18), [geometry_joinbarriers.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_joinbarriers.py:14).

**1. Feature.** Intended continuous printed row constrained by physical rules, but authorization also uses parent detector relationships and case guards. Charter: separation, font geometry.

**2. Slow model and visual check.** M22 supplies explicit endpoint measurements and M12/M13 supplies rules; no independent slow model assigns every fragment to a complete physical row. Historical visual evidence: Owner join/curl and column cases were checked after each policy change; accepted geometry does not provide exhaustive one-row ground truth.

**3. Fast against slow.** The 69 historical R2 fragment-pair comparisons contain 46 native agreements and 23 disagreements. The installed native tangent measurement has the exact R1 comparison in M22. The full join policy was developed from failures and owner comments, not an all-row slow ownership rendering. Comparison unit: 69 primitive pair decisions; no full ownership agreement.

**4. Constants and regression guards.** Gap/support/width/tangent tolerances and directional exclusion margins are empirically selected h-relative guards. Their existence is physically motivated; their exact values are not derived. Rule barriers, independent endpoint supports and overlap/retention vetoes followed bad bridging or text loss. Preservation of old horizontal sources can encode a prior detector partition. Numeric source catalogue: `M23.constants.numeric_occurrences` in the companion JSON (100 occurrences).

**5. Generalisation risk.** High risk for broken lines across large gaps, spanning headings, facing leaves, rule-touching glyphs and multirow fragments. Research §7: G1, G2, A02, A03, A04.

**6. Grade C.** The measurements are feature-based, but the final same-row join policy has no independently verified slow ownership model.

Evidence: [A34](#a34), [A5](#a5), [C6](#c6).

## 26. M24 — Local type pitch, phase and missing-slot nomination

Source: [type_context.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_context.py:7), [type_grid_edges.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_grid_edges.py:12), [type_lattice.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_lattice.py:16), [type_profiles.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_profiles.py:29).

**1. Feature.** Real repeated row spacing and local size families, approximated from detector centres/short sides; not font identity or true baselines. Charter: font properties, font geometry.

**2. Slow model and visual check.** type_lattice.raw_rows draws dense whole-block ink ridges; C34 native/12-sample/heuristic slot studies compare this with detector-axis lattices. Historical visual evidence: C34 slot galleries show supported missing rows, false slots caused by headings and inconsistent family heights. Owner c0b02 p10 #118 recovery is a visible positive.

**3. Fast against slow.** C34 195-page census: 389 nominated slots, eight native versus nine in each sampled route, with three decision differences. This measures the candidate set, not recall of entirely absent blocks or irregular poetry. Comparison unit: 389 slots; 8 native and 9 sampled supports.

**4. Constants and regression guards.** Width 8h, box overlap>.65, centre distance<.3 width, height ratio .6–1.67, gap<8h, ≥4 members, .15/.85 extents, pitch in 1–5h, ≥2 mode supports, gaps 2–4 pitches with .4h residual, .65h owned-slot radius are empirical lattice priors. Pitch/phase are estimated; the fixed admissible range is not derived. All short headings can own a slot after false missing-long-box nominations. This corrects a detector completeness assumption, but still treats a box centre as row occupancy. Numeric source catalogue: `M24.constants.numeric_occurrences` in the companion JSON (117 occurrences).

**5. Generalisation risk.** High miss risk for wholly absent blocks, verse, mixed type, nonuniform leading, sharp curl and a coherent verso lattice. Research §7: G2, G5, G6, A04, A06, A07.

**6. Grade B.** A real spacing feature has a dense ink rendering and partial slot comparisons, but detector-conditioned nomination leaves substantial unmeasured scope.

Evidence: [C34](#c34), [C5](#c5).

## 27. M25 — Missing-slot body contacts and point ownership

Source: [type_lattice.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_lattice.py:89).

**1. Feature.** Native body-sized ink and repeated lower contacts at a proposed row; geometric point ownership is a proxy for complete glyph ownership. Charter: font geometry.

**2. Slow model and visual check.** type_lattice.inspect_slot dense route draws components, bottoms and support; fast route resamples at 12 samples per provisional h. Historical visual evidence: C34/C5 contact panels expose false-centre consensus and bodies already covered by short localizations.

**3. Fast against slow.** C34 slot comparison in M24 includes native/sampled decisions. C5 changes to measured contact mode and owned-centre veto were checked through owner cases; no new comprehensive independent glyph-to-row agreement is present. Comparison unit: 389 historical slots; later predicate agreement partial.

**4. Constants and regression guards.** ±.8h strip, paper 3h, relative darkness .18, body height .45–1.6h, width .1–3h, area .06h², ≥5 bodies spanning 5h, .25h bottom tolerance and ≥half contacts are empirically selected. Point-in-polygon tolerance is geometry, not letter evidence. Bottom-contact mode replaces centre agreement; measured_y replaces ideal grid position; point ownership blocks rediscovering parts of an existing row. The latter can also reject genuinely unowned parts in an oversized polygon. Numeric source catalogue: `M25.constants.numeric_occurrences` in the companion JSON (69 occurrences).

**5. Generalisation risk.** High risk for descenders, accents, mixed scripts, touching components and cropped neighbouring-row bodies; a mode of component bottoms need not be a baseline. Research §7: G1, G5, G6, A03, A07, A12.

**6. Grade B.** A native contact rendering exists and sampling was compared, but current ownership/confirmation changes are only partly checked against it.

Evidence: [C34](#c34), [C5](#c5).

## 28. M26 — Table, leader and repeated-dot structural exclusion

Source: [type_dot_runs.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_dot_runs.py:10), [type_table_extent.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_table_extent.py:13), [type_tables.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_tables.py:16).

**1. Feature.** Real aligned repeated ink, rules and crossing structure; currently used chiefly to protect recovery from table-like regions, not to segment a table into cells. Charter: tables, separation.

**2. Slow model and visual check.** type_tables and type_table_extent native rules, repeated cells, leaders and region drawings; type_dot_runs shares chain measurements with ink analysis. This exclusion is not a full R02 cell/row model. Historical visual evidence: C5 table/leader panels include 8314 p20 and prose-like false structures. V1 confirms that T2 row paths still cross right-hand table rules.

**3. Fast against slow.** C34 compares 14 table/control pages: on 63c4 p4 native protects 44/77 localizations, R1 22/77 and R2 13/77; R1 differs on 22 items, R2 on 43. R1 otherwise agrees on protected indices; R2 also differs on 200e p10 (five) and 8314 p39 (four). Seven actual post-Q8 runtime-guard pages were checked later:4959 p5 falsely protects prose and 0ce9 p1 admits ghost structures. C5 extends guards on two table pages; no complete cell-ownership comparison. Comparison unit: table/leader study pages; not a full cell census.

**4. Constants and regression guards.** Component size/area bands, dot counts, inter-dot gaps, axis agreement, rule lengths and region expansion are selected h-relative thresholds. Dot groups are measured; “table” from a group is an imposed structural interpretation. T4 chain caching does not change them. Grid and leader exclusions followed spurious residual additions and 8314 failures. Whole-region exclusion avoids a bad addition but does not render why each table cell owns each row. Numeric source catalogue: `M26.constants.numeric_occurrences` in the companion JSON (411 occurrences).

**5. Generalisation risk.** High risk on borderless/spanning cells, verse, leaders without rules, repeated letters and genuine prose with aligned punctuation. Research §7: G2, G5, A02, A17.

**6. Grade B.** It renders real table cues, but route comparisons are partial and its region veto is much weaker than an explicit cell/row model.

Evidence: [C5](#c5), [T2](#t2), [T4](#t4).

## 29. M27 — Lattice-slot regional Paddle confirmation

Source: [type_context.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_context.py:39), [type_recovery.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_recovery.py:21).

**1. Feature.** A second detector result and its overlap with proposed slots; it is not independent evidence of a physical row beyond M25’s contacts. Charter: none.

**2. Slow model and visual check.** type_recovery draws rerun localizations over nominated slots. No independent slow physical localization model certifies the second Paddle pass. Historical visual evidence: C34/C5 accepted recovery panels, including c0b02 p10 #118, checked by eye; agreement with comments is direct case evidence.

**3. Fast against slow.** Recovery records cover the development cohort, but no page/line fast-versus-independent-slow agreement for rerun localization exists. The same detector may repeat its initial bias. Comparison unit: selected nominated regional calls.

**4. Constants and regression guards.** Regional crop padding, minimum overlap/body coverage, 16 samples/h and maximum 960 detector side, ownership overlap tolerances and output score settings are empirical detector/selection settings. Existing-centre, exclusion and crop-edge checks followed duplicate/partial additions. They constrain detector boxes; they do not establish complete row ownership. Numeric source catalogue: `M27.constants.numeric_occurrences` in the companion JSON (52 occurrences).

**5. Generalisation risk.** High risk on tiny/faint type, engravings, missing whole blocks and repeated detector omissions. Research §7: G1, G3, G5, A06, A09, A18.

**6. Grade D.** The confirmation criterion is another detector localization, with no independent slow physical row target.

Evidence: [C34](#c34), [C5](#c5).

## 30. M28 — Recovered component completion and repeated ink-ownership filters

Source: [type_barriers.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_barriers.py:9), [type_completion.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_completion.py:9), [type_context.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_context.py:17).

**1. Feature.** Real connected ink extent around a candidate, then mirror/motif properties already reviewed in M06/M09; selection of which components complete the row remains a candidate-bound hypothesis. Charter: font geometry.

**2. Slow model and visual check.** type_completion.snap_components and type_ink_ownership render masks/shape witnesses. M06/M09 have slow models, but no independent complete-glyph assignment target for component snapping. Historical visual evidence: C34/C5 recovered-line panels show missing accents/end letters and ornament counterexamples. Type-prefixed ownership code is a second consumer/model parameterization, not new validation.

**3. Fast against slow.** Historical strip/motif agreement applies only to those witnesses. No complete per-line native/reference correspondence proves recovered component selection; final additions were developed through owner cases. Comparison unit: selected recovery candidates.

**4. Constants and regression guards.** Component extent/distance/padding h-multipliers and source overlap fractions are empirical; reflection/recurrence settings belong to M06/M09. Pixel inclusion and dilation are chosen tolerances, not observed glyph margins. Independent reflected evidence and full spatial motif confirmation were added after weak/ornament recovery; unknown ordinary shape cannot certify text. Completion is checked against permanent exclusions. Numeric source catalogue: `M28.constants.numeric_occurrences` in the companion JSON (106 occurrences).

**5. Generalisation risk.** High risk for accents, nearby-row ink, mixed scripts, touching characters and decorations shaped like glyphs. Research §7: G1, G4, G6, A07, A08, A12.

**6. Grade C.** Completion tracks real ink extent but lacks an independently validated slow ownership model; borrowing other measured filters does not supply one.

Evidence: [C34](#c34), [C5](#c5), [B5](#b5).

## 31. M29 — Unowned residual-ink scout

Source: [contracts.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/contracts.py:63), [type_residual.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_residual.py:127), [type_residual_recovery.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_residual_recovery.py:52).

**1. Feature.** Real ink outside current ownership with rough row-like organization; “unowned” itself is relative to detector polygons. Charter: font geometry, separation.

**2. Slow model and visual check.** type_residual.render and type_residual_recovery.field render native residual masks, local component heights and bottom-contact chains (R06-style views); type_residual.ink_scout supplies cheaper nominations. Historical visual evidence: C5 residual panels and approved d83 p99 #108/3229 p6 #26 recoveries inspected; unowned front letters and noise coexist in these views.

**3. Fast against slow.** C5 selected native/reduced contact studies and full-cohort scout exports exist; reported 22 versus 40 route candidates are not an accuracy denominator. No complete unboxed-glyph truth or all-negative native audit establishes recall. Comparison unit: selected native contact fields plus cohort scout census.

**4. Constants and regression guards.** Residual sampling scale, threshold masks, h-sized components, chain counts and gaps are empirical. Existing-polygon occupancy is an algorithm reference, and can conceal whole missed rows inside oversized boxes. Residual route was added after pitch-grid recovery missed irregular/end-of-block text. Independent native confirmation reduces false wakes, but no wake still leaves missing text unseen. Numeric source catalogue: `M29.constants.numeric_occurrences` in the companion JSON (70 occurrences).

**5. Generalisation risk.** High risk for absent blocks, engravings flooding the residual, coherent verso, oversized existing polygons and very faint bodies. Research §7: G4, G5, A06, X01.

**6. Grade B.** It has an explicit native residual witness, but scout recall and physical front-row agreement remain incompletely measured.

Evidence: [C5](#c5), [R6](#r6).

## 32. M30 — Native residual body height, lower-contact chains and ambiguity

Source: [type_residual.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_residual.py:15), [type_residual_recovery.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_residual_recovery.py:61).

**1. Feature.** Real local body dimensions and repeated lower contacts, estimated from components rather than only page box height; neither equals a certified x-height/baseline. Charter: font properties, font geometry.

**2. Slow model and visual check.** type_residual.render and type_residual_recovery.field render native component/contact graphs, measured support, chains and competing rows. Historical visual evidence: C5 native contact sheets show the approved d83 and 3229 rows and ambiguous component groups; annotations distinguish observations from borrowed assumptions.

**3. Fast against slow.** C5 native versus reduced studies expose differing component/contact support on selected pages. No exhaustive per-letter guide/row assignment measurement covers the full 208; current contextual predicates evolved afterwards. Comparison unit: selected native contact studies, not all physical rows.

**4. Constants and regression guards.** Mode binning, local component height/width bands, chain gaps, minimum support/span, bottom residual and ambiguity margins are selected physical ratios. Measured local mode improves the units, but does not derive the cutoffs. Local height and repeated contacts replaced page-proxy/centre-only assumptions; axis ambiguity and existing-body ownership were introduced after duplicate or multirow proposals. Numeric source catalogue: `M30.constants.numeric_occurrences` in the companion JSON (90 occurrences).

**5. Generalisation risk.** Medium/high risk on all-caps, accents/descenders, ligatures, touching glyphs and mixed-script apparatus; component bottoms can form multiple plausible lattices. Research §7: G2, G6, A03, A07, A12.

**6. Grade B.** It gives an explicit native rendering of useful typography features, with partial sampling comparisons and unresolved glyph/row interpretation.

Evidence: [C5](#c5), [T2b](#t2b).

## 33. M31 — Residual regional recovery, axis vetoes and separator-piece checks

Source: [type_residual_recovery.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_residual_recovery.py:27).

**1. Feature.** Intended missing physical rows supported by M30, with substantial detector-axis, source-centre and unresolved-rule vetoes. Charter: font geometry, separation.

**2. Slow model and visual check.** Native contact chains and Q8/column witnesses are explicit primitives; no independently rendered whole-page row ownership model defines the final allow/reject policy. Historical visual evidence: C5 owner crops include d83 p99 #108, 3229 p6 #26 and lost d559 words; repeated versions show policy adjustments after failures.

**3. Fast against slow.** Recovered rows and native witnesses are exported, but no independent all-row agreement tests the current version 11 decision cascade. T4 parity preserves the cascade, including known limitations. Comparison unit: case-based final recovery policy.

**4. Constants and regression guards.** Local box thickness 3.5h, shared-axis margin .5h, crop-edge .15h, body-chain support/span and separator interior .5h are empirical. Detector crop side and scaling are M01; native chain parameters M30. Versions add line-centre exclusion, competing-axis veto, weak-layer rejection, body support per separator piece and rejection when an interior sustained rule remains unresolved. These often encode physical concerns through algorithm proxies rather than resolving the page feature. Numeric source catalogue: `M31.constants.numeric_occurrences` in the companion JSON (93 occurrences).

**5. Generalisation risk.** High miss risk near existing wrong envelopes, narrow columns, table rules and ambiguous weak front rows. Abstention protects against bad additions but can systematically leave approved text unrecovered. Research §7: G2, G4, G5, A02, A06, A09, A17.

**6. Grade C.** It combines real witnesses with a case-developed acceptance cascade, without an independent slow model of final physical row ownership.

Evidence: [C5](#c5), [R6](#r6).

## 34. M32 — Large initial observation and first-row completion

Source: [type_initials.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_initials.py:15).

**1. Feature.** A physically large isolated glyph near a paragraph’s first row, with native components and enclosure; identity as an initial is a layout hypothesis. Charter: font properties, font geometry.

**2. Slow model and visual check.** type_initials native explicit component/contour renderings and reduced route comparisons in C5. Historical visual evidence: C5 initial panels compare a visible E, skewed/curled negatives and a reduced-edge miss; one clear positive dominates the accepted evidence.

**3. Fast against slow.** C5 compares native, 12-samples/body and 5-samples/body routes (12 and 5 are resolutions, not sample counts). After the nomination-margin fix all three agree on the clear E case. The 18 prior additions produce one completion in the standalone control. There is no reported all-initial semantic accuracy denominator; the initial exploratory full run was incomplete. Comparison unit: one clear E positive; 18 prior additions checked; 12/body and 5/body routes.

**4. Constants and regression guards.** Relative height/width, distance to first row, component enclosure and two-sample uncertainty margin are empirically selected physical/layout ratios. Reduced sample resolution is a budget choice. Extra reduced boundary allowance followed an approximately 1.8 px edge loss. Native observed extent is meaningful; attachment to the first nearby row is an unverified layout prior. Numeric source catalogue: `M32.constants.numeric_occurrences` in the companion JSON (77 occurrences).

**5. Generalisation risk.** High risk for decorated initials, equations, marginal signs, isolated capitals and multiple nearby rows; enlarging one crop need not assign the whole initial correctly. Research §7: G1, G6, A07, A08, A12.

**6. Grade B.** An explicit native initial rendering exists and selected routes were compared, but evidence is narrow and attachment semantics remain uncertain.

Evidence: [C5](#c5).

## 35. M33 — Smooth native contact envelope and component-preserving application

Source: [geometry_envelopes.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_envelopes.py:40).

**1. Feature.** Real upper/lower ink extent along a row, with smoothing to avoid tracing individual glyph hills; row membership remains inherited. Charter: binding curvature, font geometry.

**2. Slow model and visual check.** geometry_envelopes.guided dense native contact paths and R1 integral/vectorized implementation; A5 explicit/R1/R2 overlays. Historical visual evidence: A5 envelope galleries and owner row marks checked by eye, including box-height/curl examples. The full 11,011-line numerical census is not an 11,011-line independently adjudicated guide atlas.

**3. Fast against slow.** Recomputed 200-page ledger: 11,011 explicit/R1 polygon, contact and ambiguity results exactly equal. R2 distances exist for 10,951 lines (60 absent): max-distance median .158h, p95 .501h, max 1.370h. Applying an equal envelope still has additional retention/overlap guards. Comparison unit: 11,011 exact R1 envelopes; 10,951 R2 distance records.

**4. Constants and regression guards.** Contact quantiles, smoothing/knot scales, body envelopes, .h expansion and retention margins are empirically selected typography assumptions; native extrema are measured. R1 changes arithmetic only; R2 changes sampling and can move an edge by more than h. Smooth contact fitting replaced hilly local traces; native component preservation followed accent/end clipping. Ambiguity falls back to original geometry, which can retain a wrong parent row. Numeric source catalogue: `M33.constants.numeric_occurrences` in the companion JSON (256 occurrences).

**5. Generalisation risk.** Medium/high risk on mixed height, initials, faint accents, overlapping rows and sharp curl; a correct contact envelope is conditional on selecting the right row’s ink. Research §7: G1, G2, G6, A03, A07, A12.

**6. Grade B.** The envelope measurement has excellent explicit/fast agreement, but the full default application includes incompletely modeled row-membership and retention decisions.

Evidence: [A5](#a5), [R6](#r6), [T4](#t4).

## 36. M34 — Longitudinal faintness scout and sampled page calibration

Source: [ink_faint_scout.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_faint_scout.py:8).

**1. Feature.** Real within-page contrast distribution sampled along current row polygons; neither contrast rank nor weakness establishes front/back ownership. Charter: faintness.

**2. Slow model and visual check.** ink_faint_scout contrasted with ink_faintness.render full native component photometry; A6 native/reduced/localized/sparse panels. Historical visual evidence: A6 components and weak/normal controls were viewed; T3 revisits 16 target/control segments. V11 rechecks ef481 p151 local faint components.

**3. Fast against slow.** Recounted historical A6:15,271 segments,149 native drops,149 localized,136 reduced,297 heuristic; native/localized drop lists agree then. Current three-body/short-ambiguity predicate and T3 clipped-body change are later, so this is not proof of present 149-drop parity. No current full-native recalibration census was found. Comparison unit: 15,271 historical segments; 16 T3 target/control segments.

**4. Constants and regression guards.** Sparse sample counts/tiles, contrast summaries, eight calibration rows selected across rank, central ±8h strip, support≥12 bodies and scout cutoffs are empirical sampling choices. Ranking/statistics are measured, but eight rows do not derive a page-wide normal mode. Current polygons are scouted again after geometry changes; calibration intersects their actual shape. This fixes stale-box reference contamination but keeps a global page mode, which can combine unlike text families. Numeric source catalogue: `M34.constants.numeric_occurrences` in the companion JSON (48 occurrences).

**5. Generalisation risk.** High risk for multiple inks/fonts, few normal exemplars, small isolated words, pale front matter and scout-negative faint rows. Sampling can miss the precise dark witness protecting a real row. Research §7: G4, G5, G6, A05, A16, X01.

**6. Grade B.** A visually checked native photometry reference exists, but historical route agreement does not fully cover the current sampling and decision policy.

Evidence: [A6](#a6), [T3](#t3).

## 37. M35 — Relative component faintness and whole-segment suppression

Source: [ink_faintness.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_faintness.py:16).

**1. Feature.** Physical optical contrast, noise, core stroke thickness and repeated normal bodies. Suppression means predominantly faint observed ink, not demonstrated verso or unreadability. Charter: faintness, font geometry.

**2. Slow model and visual check.** ink_faintness.components/reference/classify and native render expose each component, page normal distribution, noise interval and retained normal run. Historical visual evidence: A6/T3 component sheets and original pale controls were reviewed. V6 shows a faint reflected heading with a dark dash; V11 shows why ordinary components and faint bodies are not text transcription.

**3. Fast against slow.** A6 historical route comparison is M34. T3 keeps pale-front controls through abstention but four of five synthetic all-front fixtures are removed (the pre-existing faint-front test is retained as an expected failure); 16 target/control cases do not establish general faint-front safety. T4 exact output parity is not new photometric truth. T3 reports native/reduced/localized agreement on all 16 numbered target/control regions, including wrong retentions on 93f8/ef481/0ce9; agreement does not validate their normal reference or ownership. Comparison unit: historical full census; current selected controls and synthetic counterexamples.

**4. Constants and regression guards.** h/40 blur (floor .25), paper 2h, area .006h², body .25–2h×.07–3h, core 90th percentile/half peak, 3-noise bound, upper-half reference, three-body adjacency, bh/2 alignment/height and gap≤bh are empirical physical assumptions. 1.4826 MAD and .954 neighbour-difference factors have Gaussian statistical meanings. Optical midpoint 1−sqrt(1−ref) derives from equal distance in optical density; min(ref−3MAD, midpoint), ≥12 reference supports and one median faint-body area contamination budget remain selected safety rules. Broad-normal spread causes abstention. Short ambiguous rows retain any normal owned body. Clipped small edge fragments cannot protect a faint row; T3 also removes all clipped components from dark_area. Three components are not necessarily three letters; a dark dash can still be a “body”. Morphological core paper prevents a large black interior from being called faint. Numeric source catalogue: `M35.constants.numeric_occurrences` in the companion JSON (143 occurrences).

**5. Generalisation risk.** High unresolved risk for genuinely pale front text, coherent verso, mixed inks/fonts and connected normal words. No visual contrast model alone establishes intent or legibility, and current front-only synthetic failures demonstrate the limit. Research §7: G4, G6, A05, A12, A16.

**6. Grade B.** It has a substantial explicit physical photometry model and partial route evidence, but current suppression semantics and pale-front generalisation remain unvalidated.

Evidence: [A6](#a6), [T3](#t3), [T4](#t4).

## 38. M36 — Two-band scout for merged detector rows

Source: [geometry_rows.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_rows.py:232).

**1. Feature.** Real two vertically separated ink bands inside a parent box, with a cheap vertical-profile nomination; parent shape is only the search window. Charter: font geometry, separation.

**2. Slow model and visual check.** geometry_rows native column-band/gap rendering with reduced/scout comparisons in B6. Historical visual evidence: B6 gap strips and split crops were checked. V10 rechecks 4959 p1: two bands are real, but one child is a clipped neighbouring strip rather than a full row.

**3. Fast against slow.** Recounted B6:15,131 segments; 76 native positives,875 scout nominations. All 75 upright native positives are scouted; the sole unscouted native positive is the explicitly parked sideways page. Five upright positives are missed by the later evaluation window, leaving 70 actual splits. This is strong historical nomination recall in the declared orientation scope, not full-row correctness. Comparison unit: 15,131 segments; 76 native positives /875 scout wakes.

**4. Constants and regression guards.** Profile sampling, peak separation/prominence, h-scaled thickness and support limits are empirical band priors. Projection sums observed ink; a second peak can be accents or a neighbouring row fragment. Scout separates cheap nomination from native action after false/expensive candidates. Its domain remains existing polygons; two physical rows not jointly localized are invisible to it. Numeric source catalogue: `M36.constants.numeric_occurrences` in the companion JSON (55 occurrences).

**5. Generalisation risk.** Medium/high risk for diacritics, bold caps, touching rows and partial parent coverage. Current post-field inputs differ from an isolated B6 census. Research §7: G1, G2, G5, A03, X01.

**6. Grade B.** The native band feature and strong historical scout comparison exist, but current input scope and complete-row interpretation are only partially verified.

Evidence: [B6](#b6), [T4](#t4).

## 39. M37 — Native curved gap path, retained-ink split and guard

Source: [geometry_filter.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_filter.py:12), [geometry_rows.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/geometry_rows.py:19).

**1. Feature.** A real low-ink corridor between two bands, used to partition a prior polygon; finding a gap is not finding each whole printed row. Charter: font geometry, separation.

**2. Slow model and visual check.** geometry_rows explicit native bands/gap trace; geometry_rows.confirmed_partition checks native retained ink. B6 route images draw the split path before/after. Historical visual evidence: B6 selected row marks/crops checked, with V10 showing the parent-completeness limitation. Owner marks remain physical corrections, not ground-truth paths for every cohort row.

**3. Fast against slow.** B6:76 native positives, 75 reduced; 35 route 1 decisions differ from native; 70 accepted splits, five missed by the limited window and one parked. T4 selected-column Gaussian optimization preserves saved final polygons on 208 pages but changes floating accumulation order slightly. Comparison unit: 15,131 historical parent segments; 70 splits.

**4. Constants and regression guards.** Otsu masks, Gaussian width/kernel truncation, band gap/width/support limits, path jump penalty, sample windows and lost-ink dilation/tolerance are selected physical/discretization assumptions. T4 exact finite-kernel subset computation is an acceleration, not a new page model. Window limits and retained-ink guards followed destructive splits; disallowing a proposed gap does not correct a pre-existing multirow box. A no-loss cut can still create a useless clipped strip. Numeric source catalogue: `M37.constants.numeric_occurrences` in the companion JSON (268 occurrences).

**5. Generalisation risk.** High risk for accents versus true rows, curved close lines, large parent omissions and mixed-script heights; per-parent topology cannot fix globally wrong ownership. Research §7: G1, G2, G6, A03, A07, A12.

**6. Grade B.** A visible native gap model and route comparisons exist, but incomplete agreement and parent-conditioned ownership prevent grade A for the full split policy.

Evidence: [B6](#b6), [R6](#r6), [T4](#t4).

## 40. M38 — Final duplicate/overlap reconciliation

Source: [stack_ownership.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/stack_ownership.py:16).

**1. Feature.** Algorithm output overlap, shared thresholded pixels and source preference; these do not identify true physical rows. Charter: none.

**2. Slow model and visual check.** stack_ownership overlap/mask diagnostics render invariants, not an independent page-feature model. Historical visual evidence: R6 duplicate crops and native-ink loss checks inspected; zero duplicate pairs did not prevent documented coverage loss.

**3. Fast against slow.** 208-page deterministic receipts and duplicate checks validate output invariants only. There is no independent physical row correspondence for which duplicate owner should survive. Comparison unit: output reconciliation, not feature agreement.

**4. Constants and regression guards.** Overlap/shared-ink ratios including .8, area/count/order preference, local darkness/Otsu thresholds and pixel tolerances are selected policy settings. T4 dark-bound skip is an exact negative test of the same policy. Unique-ink protection followed loss when a small overlapping source was deleted. Page-field/initial/source preference resolves algorithm conflicts, and can retain the wrong crop. Numeric source catalogue: `M38.constants.numeric_occurrences` in the companion JSON (61 occurrences).

**5. Generalisation risk.** High risk for close distinct rows, nested table cells, a full row overlapping a clipped row and faint unique letters below the shared ink threshold. Research §7: G1, G2, G4, A01, A12.

**6. Grade D.** It reconciles detector outputs using invariants and preferences rather than a slow physical row-identity model.

Evidence: [R6](#r6), [T4](#t4).

## 41. M39 — Changed-footprint faintness recheck and exclusion bookkeeping

Source: [ink_footprints.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_footprints.py:11), [pipeline.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/stack/pipeline.py).

**1. Feature.** Identity/version of polygon footprints and scheduling of M34/M35; no separate printed-page feature. Charter: none.

**2. Slow model and visual check.** ink_footprints tokens and pipeline source/exclusion diagnostics are algorithm bookkeeping. Physical photometry evidence belongs to M34/M35. Historical visual evidence: T3/T4 changed-footprint cases checked; unchanged-token equality is not a visual model.

**3. Fast against slow.** T4 saved 208-page output equality and token/cache checks demonstrate preserved scheduling, not new feature agreement. Comparison unit: scheduling/output parity.

**4. Constants and regression guards.** Token identity, cache scope and small numeric tolerances are implementation settings. Recalibration policy inherits all M34/M35 assumptions; no independent physical constants. Changed polygons must be re-observed after row/field/duplicate changes; reusing old evidence would certify the wrong footprint. This guards stale evidence but cannot validate the classifier itself. Numeric source catalogue: `M39.constants.numeric_occurrences` in the companion JSON (5 occurrences).

**5. Generalisation risk.** No separate feature generalisation claim; any changed shape can alter photometry/reference, and the final frame deletion is later than this recheck. Research §7: G1, G4, A05.

**6. Grade D.** It ensures observations belong to the current algorithm footprint, without adding a physical feature model.

Evidence: [T3](#t3), [T4](#t4).

## 42. M54 — Native recurrent frame units, connected sides and ragged corridor

Source: [ink_frame_field.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_frame_field.py:21).

**1. Feature.** Real repeated shapes in two parallel chains and an orthogonal linking chain, with native observed perimeter ink; more specific than page-edge location. Charter: images, separation.

**2. Slow model and visual check.** ink_frame_field.chain/render/trace explicitly draws native repeated units, side supports and a narrow corridor; T3 routes compare native, 16/h and 8/h. Historical visual evidence: T3 frame views checked; V4 rechecks 7792 p154 where reduced routes mistake last-row letters for a border. The native route draws the actual lower flower chain.

**3. Fast against slow.** Recounted 208-page census:15 nominated pages, five native positive pages, all from 7792; 136/122/135/114/115 units. Reduced wrong chains caused native-only T4 default. No evidence of general recall across unrelated frame families. Comparison unit: 15 frame nominees; five positive pages from one book.

**4. Constants and regression guards.** Nomination height>8h, thin<2h or aspect>8; compact<2h×3h, ≥4 aligned; native unit size .4–2.5h, area>.08h²; 24×24 shape normalization, correlation>.75 or symmetric distance≤half ridge width; alignment/dimension error<h/2; four repetitions, side≥8 units spanning 8h, inter-side 8h, doubled-period missing-unit allowance and h/20 corridor pad are empirically selected. Shape/ridge/period/edge extent are measured; constants are not all letter-height-derived. Orthogonal support prevents isolated real quotation marks becoming a frame; double-period allowance tolerates a missing unit. Native route retained after reduced text-chain false positives. Native corridor edges avoid smoothing through border ink. Numeric source catalogue: `M54.constants.numeric_occurrences` in the companion JSON (209 occurrences).

**5. Generalisation risk.** High uncertainty on new frames, irregular/broken motifs, text forming repeated border-like structures and curved perspective. All positive census pages share one decorative family. Research §7: G4, G6, A08, X01.

**6. Grade B.** A checked native physical frame rendering and failed reduced comparisons exist, but positive diversity and nomination recall are very limited.

Evidence: [T3](#t3), [T4](#t4).

## 43. M55 — Whole-segment frame ownership and deletion

Source: [ink_frame_field.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/ink_frame_field.py:118).

**1. Feature.** Intended assignment of all segment ink to a decorative perimeter; implemented as inclusion of body-component centres in M54’s corridor. Charter: images.

**2. Slow model and visual check.** exclude_whole uses localized M35 components and Shapely centre containment. No independent slow per-glyph/per-pixel ownership rendering proves that a mixed border/text crop contains only frame ink. Historical visual evidence: T3 removal/loss sheets were inspected and retained in T4. The source is narrower than “every observed body belongs to frame”: it tests each body centre, not the entire body or all non-body marks.

**3. Fast against slow.** T3→T4 retains all 59 deletions (57 frame segments, one blob, one faint heading) exactly. This does not independently certify every deleted glyph on future mixed crops. No whole-body native-versus-fast ownership comparison exists. Comparison unit: 57 reviewed frame deletions; 59 total T3 deletions preserved.

**4. Constants and regression guards.** No fraction threshold: all selected body centres must be covered and at least one body must exist. “All” is exact only for that selected set; body selection inherits .25–2h height/.07–3h width, area and clipping/contrast thresholds from M35. Whole-segment-only deletion avoids clipping mixed text/frame boxes when any selected body centre lies outside. A mark or a text stroke extending outside a centred component does not veto deletion. Numeric source catalogue: `M55.constants.numeric_occurrences` in the companion JSON (7 occurrences).

**5. Generalisation risk.** High unresolved risk for mixed frame/text boxes, small annotations, accents and touching ink. Centre containment is insufficient evidence of exclusive decorative ownership. Research §7: G1, G4, G6, A07, A08, A12.

**6. Grade C.** It targets a physical ownership question but uses a case-developed centre-containment surrogate without an independently checked slow ownership model.

Evidence: [T3](#t3), [T4](#t4).

## 44. M40 — Compose order, permanent exclusions, source ancestry and result contract

Source: [pipeline.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/features_ink/pipeline.py:17), [contracts.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/contracts.py), [type_extended.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/shared/type_extended.py:14), [geometry.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/stack/geometry.py:11), [pipeline.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/prototypes/fast_lines/stack/pipeline.py:47).

**1. Feature.** Algorithm composition, provenance and invariants, with no distinct page feature. Charter: none.

**2. Slow model and visual check.** stack/pipeline.py diagnostics and source IDs audit what ran; no physical slow model is claimed. Historical visual evidence: R6/T4 final overlays and receipts checked, but composition can change the inputs on which each historical primitive was evaluated.

**3. Fast against slow.** Independently compared T4 to T3: all 208 pages and 15,093 final items exactly equal. Verified 225 source hashes and 208 run 1 receipt keys. No fresh Stack inference, physical accuracy estimate or held-out test in this review. Comparison unit: 15,093 final items; source-bound saved output parity.

**4. Constants and regression guards.** Stage versions, thresholds delegated to modules, ordering and parked/bend options are execution policy. Default bend=False retains R6 field+local path; T2/T2b/T2c opt-ins/study scripts are not the default physical model. Permanent exclusions prevent rejected ink returning; source ancestry traces changes. Ordering protects prior decisions but is not a jointly fitted generative model of the page. Numeric source catalogue: `M40.constants.numeric_occurrences` in the companion JSON (47 occurrences).

**5. Generalisation risk.** No new physical generalisation claim. Correlated assumptions and downstream changed inputs limit transfer of isolated historical route agreement to the entire stack. Research §7: G1, G2, G4, G5, A18.

**6. Grade D.** Composition and provenance make evidence auditable, but do not supply a page-feature model.

Evidence: [R6](#r6), [T4](#t4).

## Summary table

“Measured” below means the bounded comparison described in the mechanism section. It does not turn the slow reference into ground truth.

| Mechanism | Feature | Slow model | Fast-versus-slow evidence | Grade |
|---|---|---|---|---|
| M00 File decode, warm session and explicit parked-page input | None | None | 208 input/output receipts only | **D** |
| M01 Paddle resize, normalization and learned localization map | None | None physical; learned map | No physical target agreement | **D** |
| M02 DB threshold, contour score, expansion and quad/polygon output | None | R01 contour genealogy (algorithm) | 174 historical variant pages; no physical target | **D** |
| M03 Height proxy, straight axes, raster/ROI primitives and call-local geometry memo | font properties, font geometry | Offline guides, not calibrated proxy | 46.10 px proxy vs 23 px body counterexample | **D** |
| M04 Reduced printed-rule nomination | separation, tables | Q8 native rule fields | 195 pages; 13,639 sources; 590 nominees | **B** |
| M05 Native straight-rule/flank verification and Q8 cut | separation, tables | Native rule/flank strips | 195 pages; 308 inspected cut seams | **A** |
| M06 Weak-layer nomination and reflected-glyph ownership, including recovery callers | faintness, font properties | Native direct/reflected glyph atlas | 12 pages/793 latest ROIs; 0 dense/explicit differences | **B** |
| M07 Native seal-rim trace and tangent-letter exclusion | images, faintness | Native angular/radial rim | 195 pages; 21 native vs 20 explicit removals | **B** |
| M08 Coarse connected-ornament and recurrence gate | images | Native repeat-patch support | 18 native strips/93 nominations | **B** |
| M09 Spatial repeated-ink support and residual-glyph veto | images | Dense spatial recurrence | 18 strips; selected motif agreement | **B** |
| M53 Compact isolated solid-mass nomination and native disk/counter test | inkiness, images | Native mass/disk/counter | 208 census; 15 nominees; 1 native vs 2 reduced positives | **B** |
| M10 Disconnected motifs with border/layout nomination | images | Native contour/motif groups | 195 pages; 25 horizontal groups/5 positives | **B** |
| M11 Outer-third map-ridge coherence scout for the shared page field | binding curvature, skew | C6 native shared field/edge | 208 pages; 71 native, 73 scout, 39 both | **B** |
| M12 Native straight/curved rule verification and grid rejection | tables, separation | Native stroke/grid rendering | Partial rule/column census | **B** |
| M13 Bilateral column termination certificate and shared-edge split | separation | Slow native crossings/endings | 52 certificates exact; 7 reduced disagreements | **A** |
| M14 Native paper/ink components and body-contact preparation | font geometry, inkiness | Dense native contacts/components | 195 pages/9,086 paths; 13 tiny differences | **B** |
| M15 Shared page-field mesh, row phases and native edge certificate | binding curvature, skew, font geometry | Native registered page mesh | 208 pages; 13,712/14,949 rows matched | **B** |
| M16 Field-based image unbending and regional Paddle rerun | binding curvature, skew | Native unbent image | No full isolated R09 comparison | **B** |
| M17 Native components assigned to rectified row bands | font geometry, separation | Band output; no independent ownership | Case-based assignment checks | **C** |
| M18 Old-to-new field ownership, horizontal-source veto and fixed-point retention | None | Conservation audit, not physical model | No physical-row agreement | **D** |
| M19 Per-line sparse DB ridge scout and affine/residual measurement | binding curvature, skew | Dense DB/native strips; cached guides | 195 pages/13,639 unadjudicated source records | **B** |
| M20 Local geometry correction, component completion and original-ink retention | binding curvature, font geometry | Native envelope/retention primitives | Primitive parity; combined policy case-tested | **B** |
| M21 Angled short-fragment and Hermite box-join nomination | None | Hypothetical join curve only | No physical nomination calibration | **D** |
| M22 Native endpoint paths and tangent agreement | binding curvature, font geometry | Dense native endpoint tangents | 71 lines/12,386 samples/77 alternatives exact R1; historical R2 has 23/69 disagreements | **A** |
| M23 Fragment join authorization and column/rule protection | separation, font geometry | Contact/rule primitives only | 69 contact pairs; no full join target | **C** |
| M24 Local type pitch, phase and missing-slot nomination | font properties, font geometry | Dense whole-block ink ridges | 195 pages/389 slots; 8 vs 9 supports; 3 differences | **B** |
| M25 Missing-slot body contacts and point ownership | font geometry | Dense component lower contacts | Historical slots; later predicates partial | **B** |
| M26 Table, leader and repeated-dot structural exclusion | tables, separation | Native rules/leaders/extents | 14 controls; native/R1/R2 differences | **B** |
| M27 Lattice-slot regional Paddle confirmation | None | Second detector, not slow feature | Selected recoveries only | **D** |
| M28 Recovered component completion and repeated ink-ownership filters | font geometry | Completion output; borrowed filters | No independent complete-glyph assignment | **C** |
| M29 Unowned residual-ink scout | font geometry, separation | Native residual contact fields | Selected native studies; no full recall | **B** |
| M30 Native residual body height, lower-contact chains and ambiguity | font properties, font geometry | Native local-height/contact graph | Partial selected-page comparison | **B** |
| M31 Residual regional recovery, axis vetoes and separator-piece checks | font geometry, separation | Contact/rule primitives; no policy target | Case-driven final decisions | **C** |
| M32 Large initial observation and first-row completion | font properties, font geometry | Native initial extent/ownership | One clear E; 12/body and 5/body routes | **B** |
| M33 Smooth native contact envelope and component-preserving application | binding curvature, font geometry | Dense native envelopes | 200 pages/11,011 exact R1; R2 partial | **B** |
| M34 Longitudinal faintness scout and sampled page calibration | faintness | Native full component census | 15,271 historical segments; current predicate changed | **B** |
| M35 Relative component faintness and whole-segment suppression | faintness, font geometry | Native contrast/noise/stroke/reference | Historical parity; current pale-front failures | **B** |
| M36 Two-band scout for merged detector rows | font geometry, separation | Native two-band rendering | 15,131 parents; 75 upright native positives all scouted; 1 parked | **B** |
| M37 Native curved gap path, retained-ink split and guard | font geometry, separation | Native curved white-gap path | 70 splits; 5 window misses; route differences | **B** |
| M38 Final duplicate/overlap reconciliation | None | Overlap/output invariant audit | No physical row correspondence | **D** |
| M39 Changed-footprint faintness recheck and exclusion bookkeeping | None | Token/scheduling audit | 208 output parity only | **D** |
| M54 Native recurrent frame units, connected sides and ragged corridor | images, separation | Native frame units/corridors | 208 census; 15 nominees; 5 positives in one book | **B** |
| M55 Whole-segment frame ownership and deletion | images | Body centres in frame corridor | 57 reviewed deletions; no full-body agreement | **C** |
| M40 Compose order, permanent exclusions, source ancestry and result contract | None | Composition/provenance only | 208 pages/15,093 items exact T3→T4 | **D** |

## Feature coverage and absent physical models

No whole charter category is honestly described as “only C/D”: each broad category has at least one physical B-level primitive, and separation has bounded A witnesses. That does **not** mean the intended feature is fully tracked. The missing subfeatures below matter more than counting category names. In particular, a stroke-width statistic is not an ink-condition referee; a box-derived h is not letter height; recurrent border units are not exclusive ownership of all ink in a crop.

| Charter feature | Default evidence | Missing or weakly grounded part |
|---|---|---|
| Faintness | M06, M34, M35 | B: explicit photometry and mirror-shape witnesses exist. Whole-line faintness, pale-front safety and watermark ownership are unresolved; no physical source-separation/transmission model or verified pairing. |
| Inkiness | M14, M35, M53 | B for measured stroke/components/solid mass only. General under-/over-inking relative to compatible glyphs, broken bridges/counters across thresholds and unreadability are not implemented as a verified runtime feature. R10 and earlier Q2 intensity proxy are not a demonstrated fast referee. |
| Tables | M04, M05, M12, M26 | B/A narrow rules, B leaders/region protection. General cells, spanning entries and borderless topology are absent. Returning a region to Paddle is present; recognizing all table extent accurately is not established. |
| Images | M07, M08, M09, M10, M53, M54, M55 | B specialized seals/motifs/frame/mass; C whole-frame ownership adapter. No general engraving/image/watermark-versus-embedded-caption model. This is not general image recognition. |
| Binding curvature | M11, M15, M16, M19, M20, M22, M33 | Mostly B; A bounded endpoint measurement. Shared field is real work, but physical leaf domains, sharp folds, independent row phases and end ownership remain unvalidated. M18 detector-partition guards are D substitutes where the field fails. |
| Skew | M11, M15, M19, M20 | B: affine slope is explicit and can be separated algebraically from bend; full native direction/guide validity is not measured across all typography. Rotation/orientation is parked, not solved. |
| Separation | M04, M05, M12, M13, M23, M26, M36, M37 | A bounded native rule/crossing certificate; B/C other separators. Distinct leaves, unruled columns, running heads and full physical row identity lack a verified common model. M18/M38 detector ownership is D, not that missing model. |
| Font properties | M03, M06, M24, M30, M32 | B local spacing/body/shape/initial cues, D shared box-height proxy. Typeface identity, compatible within-book reuse and measured letter/word spacing are not coherent default-path features. Offline feature-family studies are not runtime guide borrowing. |
| Font geometry | M03, M14, M17, M22, M24, M25, M28, M30, M32, M33, M35, M36, M37 | A/B narrow contacts; C ownership/completion and D box proxy. No adaptive script-specific number of guides, certified baseline/x-height/diacritic system. Output baseline remains null. Body centres and density bands must not be relabelled as semantic guides. |

The most consequential C/D substitutions are complete glyph-to-row ownership (M17/M23/M28/M31), old/new crop identity (M18/M38), and exclusive frame ownership (M55). The offline C typography studies render guide uncertainty, script differences and compatible exemplars, but the default does not consume a verified adaptive guide system. No runtime feature consistently models front-versus-back physical source identity, font-conditioned broken/filled strokes, complete image/caption ownership, or physical leaf domains. These are scope findings, not new tasks.

## Same feature, different models

**Faintness / page normal print (M06, M34, M35, M55).** M06/type_ink_ownership uses tone-ranked anchor glyphs and reflection matches; M35 uses ridge core/peak, noise, optical-density midpoint and sampled page reference. These can call the same component weak/normal differently. M55 borrows localized M35 segmentation without proving whole-body ownership. T2 initially added incompatible mean-ridge contrast; T2b/c share a typed reference but observation contexts still differ.

**Bend / row path (M11, M15, M19, M20, M22, M33, M37).** M11 outer-third DB scout and M19 per-line DB ridge have different offset windows, units and trigger predicates. M15 shared native mesh competes with per-line map/contact paths, tangent joins and smoothed envelopes. M37 traces a gap inside an old parent. No jointly certified physical row/leaf coordinate system reconciles them. T2c is a third off-default cubic field, not extra default evidence.

**Height / typography (M03, M17, M19, M24, M30, M35).** M03 half box short side; M19 DB-band thickness; M17 max(h,.65×box short side); M24 local detector-size family; M30 native component modes; M35 upper-normal-body median. They have different physical meanings. T2b’s46.10 px proxy vs 23 px body is a concrete factor-of-two discrepancy, not just duplicate software.

**Ink mask / paper (M04, M06, M14, M25, M30, M35, M37, M38, M54).** Absolute .06/.08×255 local darkness, relative .18 slot/residual contrast, glyph tone percentiles, component-ridge noise/Otsu, band Otsu, reconciliation inclusive ink and frame percentile-midpoint masks select different pixels. Gray<200 acceptance audits are yet another broad diagnostic, not text truth. Identical geometry can pass one retention mask and fail another.

**Row / component ownership (M17, M18, M25, M28, M30, M31, M37, M38, M55).** Nearest rectified axis, dominant label vote, body-centre inclusion, local contacts, existing-axis veto, per-parent gap, overlap preference and frame-centre containment are different models of ownership. Native-pixel union equality does not reconcile them or guarantee whole glyphs in readable rows.

**Separation / layout (M05, M12, M13, M15, M23, M26).** Clear rule flanks, grid veto, bilateral terminations, box-empty channels, fragment barriers and table-region guards have different domains. A table rule can veto a new row in one stage while not being a barrier to another field. Preserving an approved column split is narrower than a common physical layout model.

## Round 7 geometry attempts in methodological terms

These are historical candidates, not additional default-path mechanisms or promotions. Their explicit drawings are useful even where the models fail. The following judgments distinguish the reference construction, approximation and final crop policy.

### T2

Report: [T2 report](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_T2_ROWS.md); independent [check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T2_check.md).

**Feature and rendering first.** Layout domains, material row phase in a shared bend field, native obstacles, component ownership and endpoints. Yes: native v1–v10 renderings preceded/falsified successive changes. Bodies, marks, domains, mesh, phases and shared gaps were drawn. R6 field ideas were reused rather than declaring Paddle boxes to be true rows.

**What follows the methodology.** This is substantially closer to the charter methodology than a box-only patch. Pixel-obstacle rendering replaced an overbroad rectangle-overlap veto after visualization falsified it. It recorded uncertainty and did not promote a failed candidate.

**What fails the methodology.** The slow model was not reliable enough: rule endpoints manufactured horizontal region cuts (4959 p1), finite table rules did not constrain right-hand rows (8314 p20), a whole-region unresolved_columns guard substituted for layout, endpoint normal-run tests could shrink already found weak text (31f40), and _assign retired an entire parent when only some content transferred. Mean-ridge photometry was compared to A’s different reference statistic. Whole-component audits missed partial characters. Running all this after much of the legacy stack was not a cheap rendering of the same model.

**Fast against slow.** Independent recount:207 active pages, 11,447 native paths and 11,422 reduced; 75 pages differ in count,199 native paths unmatched. The deliberately slow obstacle loop and scatter reductions give identical emitted items on 207/207, but share region/phase/assignment logic. This validates the obstacle implementation, not the slow page model’s truth.

**Assessment of the independent check.** T2_check’s retirement, endpoint, unsafe region cut, unresolved-column and table-barrier findings agree with the report, source snapshot and V1. Their precise failure is incomplete ownership and incorrect physical domains. It is incorrect to explain all T2 failures as excessive zero-loss vetoing: the destructive retirement had no complete coverage check.

**Methodology grade.** B for shared physical-row construction; C/D for the unvalidated endpoint/retirement/region-veto policies. Obstacle scatter parity alone could merit A as a narrow primitive, never for the entire candidate.

### T2b

Report: [T2b report](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_T2B_ROWS.md); independent [check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T2b_check.md).

**Feature and rendering first.** Finite barriers, intersecting component ownership, shared material rows and explicit distinction between found ink and new normal growth. Yes: explicit-v1…v12 and reduced/native overlays drove changes; native uncovered-pixel sheets exposed losses hidden by centre-only component counting.

**What follows the methodology.** Typed NormalInk reused A’s reference; grouped median replaced mean-ridge contrast; physical rule paths/white gaps replaced rule-end slabs; finite table barriers and intersecting components improved the physical observation. The full found-ink raster was an honest falsification tool.

**What fails the methodology.** Parent leftovers were retained and subtracted from modeled bands, giving slivers, split words and coupled wrong ownership. This is a model failure even with zero union loss: d83 #108’s word and e745 Ψ can be divided among crops. Nominal 12 samples per proxy was not 12/body (46.10 px proxy vs 23 px native body on 3229 p6). Layout, reference context and component semantics still differed between native/reduced runs.

**Fast against slow.** Recounted 207 pages:16,991 line comparisons, 96 unmatched, 16,895 matched; path-error median 2.663 px, p9522.824 px, max 2460.586 px.12,730 matches have zero endpoint delta. In122 pages nearest correspondence reuses a reduced target within one native region, so these are not one-to-one line accuracy statistics. V5 rechecks native rendering; 208 repeat equality is separate from native/reduced agreement.

**Assessment of the independent check.** T2b_check’s fragmentation and regression findings are consistent with the report and saved rendering. It should not be collapsed into “no explicit model”: the explicit model and falsification evidence are extensive; they failed to establish reliable ownership. Zero union loss does not guarantee an intact glyph or one physical row per crop.

**Methodology grade.** B for observable field/barrier/row features; residual subtraction and detector-parent fallback are C/D closure policies, not a validated physical ownership model.

### T2c

Report: [T2c report](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_T2C_BEND.md); independent [check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T2c_check.md).

**Feature and rendering first.** Columnwise affine slope plus shared low-order bend, body-derived phase, native growth and gap checks around retained crops. Yes: explicit-v1 on 14 requested pages preceded crop mutations, and final native-handoff/reduced-handoff drawings remain. No rectified/unbent image or new detector rerun is produced on this route.

**What follows the methodology.** One affine component is removed before measuring coherent bend; nominations use observed departures rather than merely a fitted curve. Per-body normal decisions, measured word gaps and preserved found ink make the growth claim more explicit. Invalid inactive fields and missed triggers are reported as failures.

**What fails the methodology.** Shared scout misses are inherited by both native and reduced routes (3229 p6, 8686 p7); a quiet scout does not validate flat geometry. d83/9ea spread domains and table extrapolations remain physically wrong (V2, V7, V8). Keep/split/grow operations preserve much old crop partition, and transactional loss checks concern their input, not the final saved R6 output. h-scaled cubic hinges, three-body runs and the 1200 px thumbnail are chosen priors, not derived laws.

**Fast against slow.** Recounted 14 pages and 1,237 nearest-phase path comparisons:median per-path max distance .0817h, p952.073h, max 81.285h. The report’s nominated-column subset has 346 matches, p95 .154h, max 1.455h (reported, not rederived here). Subset agreement cannot remove the bad inactive renderings or common scout misses; phase mismatches contaminate a pure bend-error interpretation.

**Assessment of the independent check.** T2c_check correctly rejects promotion and identifies wrong/missing rows. Its statement that there is no rendering of corrected geometry is too broad: there is no unbent-image rendering, but explicit native fields and final crop comparisons exist. Its proposed diagnosis does not make default unbend+Paddle automatically grade A: field validity, R09 scale/unbend isolation and physical row correspondence are separate unresolved evidence. Retention itself need not preserve a wrong partition—ink can be reassigned losslessly. These implementations’ box floors/leftovers constrain reassignment; that is not an inherent conflict between no text loss and physical modeling.

**Methodology grade.** B for the bend-field hypothesis with partial/failed agreement; C/D for retained-box closure policies. Not an A physical geometry model.

## What task 4 changed about this evidence

Task 4 reduces repeated computation and drops failed reduced solid/frame routes. It adds no new physical model and does not upgrade a mechanism’s methodology grade simply because it is faster or easier to port. Its source-bound 208-page equality with T3 is strong preservation evidence. The rejected reduced-field scout (missed 14 accepted pages, including 8686 p7/p26/p29) and curved-column rerun trial (13 changed pages, including 207 dark rho pixels lost on c8 p36) are useful falsifications. They do not count as successful fast approximations. Keeping native solid/frame confirmation avoids the observed reduced counterexamples; its remaining class/ownership generalisation is still limited. See [T4](#t4).

## Evidence audit and limits

All risk judgments are qualitative. No unseen-page success probability can be estimated from repeated case-driven use of the 208 development pages. No page-keyed rule is necessary for overfitting: a succession of globally applied guards can still encode the examples that generated them. Conversely, a threshold with unknown provenance is not proof of deliberate page tuning.

The numerical checks in this review read saved JSON and source hashes. They verify denominators and correspondence definitions; they do not rerun OCR or re-adjudicate every historical visual claim. Corrections made during the audit include 12 distinct mirror-study pages (not 20 versioned records), 10,951 R2 envelope distances (not all 11,011), and distinguishing 12/body/5/body initial resolutions from counts of examples. T2b nearest matches reuse targets in 122 pages. These qualifications are material to the strength of “agreement.”

The companion [machine-readable review](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_METHODOLOGY.json) contains 44 mechanism records, the source-function/constant census, recomputed ledgers, feature gaps, overlapping models and these attempt assessments. Each numeric occurrence names a source line and expression. Values in unselected historical branches are evidence about implementation history, not default active thresholds. The Markdown gives installed values and the semantic assessment; the JSON prevents small guards and floors disappearing into “all in letter heights.”

### Images reopened in task 5

| ID | Image | Direct observation |
|---|---|---|
| V1 | [s2-831443dc5e6f1ccfbaf5-p00020.native.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2_rows/final/renderings/s2-831443dc5e6f1ccfbaf5-p00020.native.jpg) | Many left table cells have domains; the right numeric columns share a region and blue row paths cross vertical rules. |
| V2 | [an-d83e7a198ade-p000099.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2c_bend/native-handoff/an-d83e7a198ade-p000099.jpg) | Three inferred domains do not represent the two leaves; inactive field paths extrapolate across the gutter. |
| V3 | [s2-922e617957fca8dfafd0-p00001.0.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round7/T3_ink/solid-v2/s2-922e617957fca8dfafd0-p00001.0.jpg) | Isolated filled black mass and native inscribed disk; no visible counter. |
| V4 | [an-7792a3301892-p000154.comparison.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round7/T3_ink/routes/an-7792a3301892-p000154.comparison.jpg) | Native blue witness follows bottom flower chain; 16/h and 8/h witnesses select letters in the last real row. |
| V5 | [s2-3229200bf47ca465a42d-p00006.native.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2b_rows/renderings/s2-3229200bf47ca465a42d-p00006.native.jpg) | Shared body paths broadly follow left curl; gap boundaries are toothed around ink. This is not final OCR ownership truth. |
| V6 | [s2-0ce9d1025b3f23c7119e-p00001.16.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round7/T3_ink/supplement/s2-0ce9d1025b3f23c7119e-p00001.16.jpg) | Faint reflected heading with a dark dash; a dark component is not necessarily a normal-letter run. |
| V7 | [s2-3229200bf47ca465a42d-p00006.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2c_bend/native-handoff/s2-3229200bf47ca465a42d-p00006.jpg) | Visible left bend with some unsupported/poor endpoints; saved scout does not nominate it. |
| V8 | [s2-86865c33eef5932c013b-p00007.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2c_bend/native-handoff/s2-86865c33eef5932c013b-p00007.jpg) | Right bend appears in the field; terminal sharp upturn is underfit and some phases follow leaders. Saved scout is inactive. |
| V9 | [s2-661ddf05c8865e7b2c45-p00005.columns.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round5/geometry/routes-v5/s2-661ddf05c8865e7b2c45-p00005.columns.jpg) | A real central divider and text endings on both sides support the narrow column witness. |
| V10 | [s2-49598b2e848ab1f0ee1e-p00001.split-89.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round6/B_rows/final-v16/s2-49598b2e848ab1f0ee1e-p00001.split-89.jpg) | Gap split separates real bands, but one band is a clipped neighbour fragment, not a complete OCR row. |
| V11 | [an-ef481610a820-p000151.9.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round7/T3_ink/explicit-v1/an-ef481610a820-p000151.9.jpg) | Local faint margin components with an isolated normal component; component classification is not letter transcription. |
| V12 | [an-e259bbf5081c-p000198.jpg](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round6/C_curvature/routes-final/an-e259bbf5081c-p000198.jpg) | Native/reduced shared-field paths can agree while spanning the physical binding and incompatible leaf systems. |

### Primary report and artifact index

<a id="q8"></a>
**Q8** — [FAST_LINES_ROUND2_RESULTS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND2_RESULTS.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/round2/rule_separators).

<a id="a34"></a>
**A34** — [FAST_LINES_FEATURES_A.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_FEATURES_A.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/features_geometry).

<a id="b34"></a>
**B34** — [FAST_LINES_FEATURES_B.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_FEATURES_B.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/features_ink).

<a id="c34"></a>
**C34** — [FAST_LINES_FEATURES_C.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_FEATURES_C.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/features_type).

<a id="a5"></a>
**A5** — [FAST_LINES_ROUND5_GEOMETRY.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND5_GEOMETRY.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round5/geometry).

<a id="b5"></a>
**B5** — [FAST_LINES_ROUND5_INK.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND5_INK.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round5/ink).

<a id="c5"></a>
**C5** — [FAST_LINES_ROUND5_TYPE.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND5_TYPE.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-type/.astra/fast_lines/out/round5/type).

<a id="a6"></a>
**A6** — [FAST_LINES_ROUND6_A_FAINTNESS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND6_A_FAINTNESS.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round6/A_faintness).

<a id="b6"></a>
**B6** — [FAST_LINES_ROUND6_B_ROWS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND6_B_ROWS.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round6/B_rows).

<a id="c6"></a>
**C6** — [FAST_LINES_ROUND6_C_CURVATURE.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND6_C_CURVATURE.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round6/C_curvature).

<a id="r6"></a>
**R6** — [FAST_LINES_STACK.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_STACK.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r6).

<a id="t2"></a>
**T2** — [FAST_LINES_ROUND7_T2_ROWS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_T2_ROWS.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2_rows).

<a id="t2b"></a>
**T2b** — [FAST_LINES_ROUND7_T2B_ROWS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_T2B_ROWS.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2b_rows).

<a id="t2c"></a>
**T2c** — [FAST_LINES_ROUND7_T2C_BEND.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_T2C_BEND.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry/.astra/fast_lines/out/round7/T2c_bend).

<a id="t3"></a>
**T3** — [FAST_LINES_ROUND7_T3_INK.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_T3_INK.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink/.astra/fast_lines/out/round7/T3_ink).

<a id="t4"></a>
**T4** — [FAST_LINES_ROUND7_T4_SPEED.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review/docs/research/FAST_LINES_ROUND7_T4_SPEED.md); [artifact root](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7).

Owner evidence: [COMMENTS_CHECKED.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r6/COMMENTS_CHECKED.md), [owner_marks.json](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r5_rows/owner_marks.json), [review_r4](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r4), [review_r5_rows](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r5_rows). Independent round 7 checks: [T2_check.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T2_check.md), [T2b_check.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T2b_check.md), [T2c_check.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T2c_check.md), [T3_check.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T3_check.md), [T4_check.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r7/T4_check.md).

### Research §7 failure identifiers

G1–G6 are shorthand for the six numbered small-detector failure modes in the source document; A/P/X IDs retain its approach names.

| ID | Failure exposure |
|---|---|
| G1 | wrong representation: quad/unclip/accents |
| G2 | wrong topology: gutters or merged rows |
| G3 | insufficient sampling: tiny text/marks |
| G4 | front/back/image ownership confusion |
| G5 | clipped evidence and absent blocks |
| G6 | unmodeled typography |
| A01 | joined contours or clipped accents; ghost/faint threshold tradeoff |
| A02 | spanning heading, dash/rule confusion, borderless cells |
| A03 | ridge hops, two peaks, bold caps and accent islands |
| A04 | mixed leaves/fonts/folds, ghost lattice, blank underconstraint |
| A05 | sharp ghosts, blurred fronts/watermarks, bad paper estimate |
| A06 | oversized envelopes hide residual; missing whole blocks; engraving floods |
| A07 | absent accents/descenders, mixed script, wrong borrowed family |
| A08 | hatching/text, repeated letters/motifs, captions/stamps overlapping prose |
| A09 | resampling cost and weak-stroke loss, duplicate overlap, more ghosts |
| A10 | boldness vs damage, accents vs breakage, threshold-dependent holes |
| A11 | missing/ghost map ridge, seam crosses whitespace or columns |
| A12 | stable verso, detached Greek accents, touching ink |
| A13 | wrong book/font/scan prior |
| A14 | wrong paired-page registration deletes front |
| A15 | dewarp changes correct text, joins leaves or invents flattening |
| A16 | source model whitens pale front |
| A17 | historical leaders/spanning cells/verse defeat table prior |
| A18 | baseline model correlated bias and non-Latin/image failures |
| A19 | reflection confounded by font/italics/wear or artifacts |
| P01 | tall rule/character and 180-degree orientation ambiguity |
| X01 | cheap-trigger false negatives and hidden diagnostic cost |
| X02 | easy synthetic perturbations fail to model real degradation |
