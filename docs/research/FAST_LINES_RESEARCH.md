# Q6 — Fast line finding: research map

Research date: 2026-10-10. Branch: `astra/page-lines-4`. Research and small evidence scripts only; the page API and its tests are outside scope. The charter, including the owner's complete words, remains authoritative: [CHARTER.md](../../.astra/fast_lines/CHARTER.md). Its words are not replaced by this report's organisation.

## 1. What I saw

### Evidence and sequence

I read the entire charter first, then looked before reading theory. I viewed all 54 original pages in nine labelled contact sheets, all 378 supplied stage images in 54 seven-stage sheets, and ten-way overlays (nine cached detectors plus ours) on nine diagnostic pages: `an-1be6`, `an-1f8e`, `an-a73d`, `an-d600`, `an-ffcc`, `s2-09f5`, `s2-200e`, `s2-3229`, `s2-8686`. Prefixes in prose resolve to the full names in the ledger below. I inspected the raw JSON schemas and audited all 486 detector records. This is visual research, not exhaustive manual labelling of every box from every detector. Fine glyph legibility and ambiguous ownership remain unadjudicated.

Only `.astra/pages/*.png` supplied image pixels. The sideways `s2-6419488b7f8e69fd20da-p00001` was viewed descriptively and excluded from upright conclusions; orientation remains parked. The 44 held-out pages were neither opened nor used. I read `prototype/build_stages.py` and `prototype/common.py` as text; I did not run their default dataset enumeration. PDF text was not used. Ours is a source of visible guide hypotheses and counterexamples, never a reference answer.

The independent dreams in section 3 were saved before opening Fable or searching the web. Receipt: `2026-10-10T12:18:31.929181+00:00`, SHA-256 of the exact text between its markers: `5642ed9fee5b76ea39e04c8ed6a24f31fd79b860a69288d077bb97ef5d4bdfa9`. The receipt and frozen copy are in `.astra/fast_lines/out/q6_review/`. Only `dreams_fable.md` existed when phase 3 began. `dreams_coordinator.md` arrived during final validation (file timestamp 15:32:02 local); I then read it completely and extended the comparison, survey and map without changing section 3.

### What stands out physically

- **Curvature is not simply skew.** `s2-3229` has correlated left-end bending and boxes cutting across successive rows. `s2-8686` bends at the right, but its fragmented/short boxes produce **zero** curvature flags. `s2-4959` has uneven first-word geometry and weak map patches. A test restricted to a returned box cannot see a missing end beyond that box. Conversely, seven flags on the mixed-scale apparatus in `an-d83e7` do not establish seven physically curled lines.
- **Geometry can be wrong with no residual ink.** `an-a73d` has two columns separated by a fine rule. Small's 47 bands merge many opposing lines; ours has 90 stage-visible lines. There are zero weak-map and zero uncovered-ink flags. `an-c8b9` contains two leaves, each with columns; a single page-wide split or curvature model is inappropriate.
- **The small detector often already rejects ghost print correctly.** On `s2-09f5`, the right foreground is found while the left ghost column is largely ignored, yet the ink scout raises 271 regions. On `s2-0ce9`, the lower ghost area itself receives many Paddle boxes: 101 versus 35 stage-visible ours, with 63 Paddle-only disagreements. Those are not 63 independently established false positives. `an-1be6` has pale real text which any ghost suppression must preserve.
- **Rules, repeated ornament and pictures are not interchangeable.** `an-1f8e` has a repeated ornamental frame boxed as text; `an-d600` has an engraving, a vignette containing lettering, and nearby real text. Erasing the picture's entire rectangle would erase some lettering. Tables `an-7a2b`, `s2-200e`, and `s2-8314` need cell-aware grouping, not generic whole-row filling. Dashes in `an-a3c2` and leaders in `s2-dee99` have structural meaning.
- **Scale and type explain many count disagreements.** In `an-d83e7`, large verse and tiny apparatus occupy the same spread. `an-ffcc` mixes Greek and Arabic script geometry. `an-e745` changes type within dictionary entries; `an-1f8e` has widely spaced display lettering. `s2-8051` has separated names and small voting marks: ours' fragmentation is not evidence that 256 lines should replace 77 Paddle bands.
- **Ink condition is distinct from contrast.** Broken/dense strokes in `s2-8686`, mottled paper in `an-3352` and `an-ef48`, and pale foreground in `an-1be6` call for different explanations. At review-sheet resolution I can identify candidates for broken/filled-letter inspection, not declare exact unreadable letters. Existing `ink_classes`, `contrast`, and guide provenance must be inspected on original-size crops before trusting them.
- **Clean controls exist.** `s2-77d1` has 39 versus 39 lines and no weak/ink/curvature flags; `s2-f9ec` has 38 versus 38 and one ink flag. `s2-23a7` is a useful dense two-column control. Their job is to expose unnecessary work and correction damage, not merely to inflate success counts.

### Where the nine detectors fail in the observed comparisons

The first three caches are **word** detectors; their item counts must not be interpreted as line recall. All nine lack our complete font-guide, ink-condition and foreground-ownership rendering. Their confidence scores do not certify readability. A baseline from a line detector is also an estimate.

| Cached detector | Observed problems, with page names | Relevant limit |
|---|---|---|
| docTR DB ResNet50 | On `an-d600`, engraving details receive boxes. On `s2-3229`, local word boxes do not directly give a continuous bent line. On `an-1f8e`, spaced title fragments require grouping. | Word granularity; no evidence that grouping would preserve all accents or distinguish weak front from ghosts. |
| docTR FAST base | On `s2-09f5`, many left ghost fragments enter its 421 words; on `an-d600`, engraving detail is included. Curved words on `s2-3229` still need line reconstruction. | Fast word detection can create expensive, wrong line candidates. |
| EasyOCR CRAFT | Some left ghost material enters `s2-09f5`; curved local boxes on `s2-3229` follow local tilt better in places, but 182 word items are not 38–43 usable line paths. | Local word geometry does not solve line endpoints, guides or ownership. |
| Kraken | `an-d600` yields 16 lines including picture structure; `s2-3229`/`s2-8686` have locally useful curved paths but extra/jagged tracks. `s2-200e` connects through leaders/rules. | Useful independent geometry, not a truth oracle or cheap default. |
| PP-OCRv5 mobile | Only 13 items on `s2-3229` and 33 on `s2-8686`; broad missed/merged curved text. `an-1f8e` still attracts ornament boxes. | Detecting the main straight body well does not protect severe bend. |
| PP-OCRv5 server | 22 items on `s2-3229`, 33 on `s2-8686`; substantial curved text loss. Some vignette lettering in `an-d600` is detected, requiring ownership review rather than automatic rejection. | Larger runtime/model is not a monotonic geometric improvement. |
| PP-OCRv6 medium | Zero items in cached `an-a73d`, despite obvious print; 68 fragmented items on `s2-3229`, 42 on `s2-8686`. | Cache observation, not a diagnosed network cause; empty output must wake an independent scout. |
| **PP-OCRv6 small** | Cross-gutter merges `an-a73d`; crossing curved lines `s2-3229`; shortened/fragmented ends `s2-8686`; ornaments `an-1f8e`; ghosts `s2-0ce9`; tiny-cell/footnote ambiguities `an-7a2b`/`an-d83e7`. | Map, contour, acceptance and expansion can fail separately. The small detector remains the intended starting point. |
| Surya | `s2-09f5` includes a broad left ghost region and bottom watermark; `an-1f8e` merges a middle stanza; `an-ffcc` merges some Arabic rows; rectangles on `s2-3229`/`s2-8686` clip or cross bent ends. | A plausible rectangular envelope is not script-appropriate line geometry. |

These examples cover all nine, but do not establish their comparative accuracy over all 54 pages. Missing fine-print or accent claims not resolvable in the sheets require enlarged crops in round 1. Ours also overfragments tables (`an-d3237`, `s2-200e`) and isolated marks (`s2-8051`); adopting its counts would reproduce an error.

### Raw audit, and what the numbers actually mean

These are newly recomputed sums of **cached** evidence, not new inference measurements. Source: `prototype/stages_summary.json`, SHA-256 `04cc67cbad853678de7c36e97cff4fe77672711861f3d055eb48e0c23aaa5b9c`. Reproducer: `scripts/fast_lines/audit_evidence.py`.

| Quantity | All 54 | Upright 53 |
|---|---:|---:|
| Paddle boxes | 5,051 | 4,796 |
| Ours shown by stage builder | 7,079 | 5,797 |
| Ours-only / Paddle-only disagreements | 196 / 218 | 102 / 200 |
| Weak-map regions | 232 | 217 |
| Uncovered-ink regions | 2,913 | 2,828 |
| Ink: edge / dark / faint | 458 / 628 / 1,827 | 442 / 612 / 1,774 |
| Bent flags: total / left / right | 34 / 25 / 9 | 29 / 21 / 8 |
| Ours-only overlapped by weak / ink / either | 50 / 107 / 107 | 40 / 84 / 84 |
| Sum historical Paddle seconds | 3.061 | 2.996 |
| Sum historical extra seconds | 26.456 | 25.524 |
| Median historical Paddle / extra seconds | 0.056 / 0.3045 | 0.056 / 0.300 |

For 53 upright pages the historical means are 0.056528 s Paddle and 0.481585 s extra. Ink flags average **53.35849**, median **26**, per page. The charter's roughly 17 flags/page is **not reproduced by this supplied summary**; I do not reconcile that by inventing a filtering rule. The 84/102 overlap count and 40 weak-covered disagreements do reproduce. Any-region overlap is a nomination statistic, not recovered-line recall; an oversized ghost region can overlap a real missing line.

`build_stages.py` uses a weak-map threshold of 0.08; its ink path uses half-resolution adaptive thresholding and morphology. Its “letter height” for several checks is a proxy, 0.45 times the median box short side. Curvature uses a map-weighted y centroid inside each box, a central fit, and edge residuals; two ridges can average together and missing endpoints lie outside its search. The disagreement checks compare masks/overlaps, not transcription or human labels. Several fixed pixel floors are implementation artefacts, not approved round-1 constants.

The stage builder excludes discounted ours lines **and** drops some narrow tall slivers; stage counts therefore differ from raw nondiscounted counts. The new comparison renderer excludes discounted lines but does not silently apply the extra sliver filter. Historical `extra_s` excludes review-image writing and the final ours-comparison work; neither timer proves end-to-end wall time. Do not reuse those timings as an ONNX benchmark of another runner.

| Raw cache (54 pages each) | Items | Unit | Median cached seconds/page |
|---|---:|---|---:|
| docTR DB ResNet50 MPS | 23,865 | word | 0.1477 |
| docTR FAST base MPS | 25,142 | word | 0.08725 |
| EasyOCR CRAFT MPS | 13,690 | word | 2.5039 |
| Kraken CPU | 4,242 | line | 4.8612 |
| Paddle v5 mobile CPU | 4,840 | line | 0.2224 |
| Paddle v5 server CPU | 4,899 | line | 2.093 |
| Paddle v6 medium CPU | 4,841 | line | 1.1343 |
| Paddle v6 small CPU | 5,051 | line | 0.2845 |
| Surya MPS | 4,604 | line | 0.64905 |

These use different models, devices and runners. In particular 0.2845 s in the small detector cache and 0.056 s in the ONNX stage experiment are not interchangeable baselines.

A separate exact image probe found **54/54 mode `L` images**, maximum RGB-channel difference after conversion **0** for every image. A saturation-based stamp separator cannot operate on this development evidence. This is a measured negative result, not a claim about the original books or future colour scans.

The coordinator's later mirror-histogram idea was probed on **422 unlabelled, nondiscounted line crops** across the 53 upright pages: up to eight evenly sampled sufficiently wide ours-line envelopes per page, with width at least five stored x-heights. Those heights select exploratory crops; they are not trusted font labels. Each crop was compared to its exact horizontal reflection and to other sampled lines on the same page using normalised magnitude-weighted 16-bin gradient histograms. No detector or foreground classifier was run.

| Histogram | Median original–reflection L1 distance | Median within-page other-line L1 distance | Crops whose reflection distance was no greater than their median other-line distance |
|---|---:|---:|---:|
| Unsigned directions | 0.2008981375 | 0.1249209765 | 132 / 422 |
| Signed directions | 0.1975144367 | 0.1116592448 | 103 / 422 |

These distances suggest some reflection signal, but also substantial confounding by text composition, font, blur and mixed content. This is **not** a mirror detector's accuracy: there are no verified foreground/ghost labels, the crops may contain either, and no decision boundary was fitted. A spatial glyph/edge rendering and compatibility controls would be required before accepting C05. Raw rows, crop coordinates and ours indices are in `mirror_histograms.json` under the Q6 output directory.

### All-page visual ledger

`P/O` = Paddle boxes / stage-visible ours lines; `W/I/B` = weak-map / uncovered-ink / bent flags. Counts describe the supplied diagnostics. Notes are visual observations, not ground truth. Full page names deliberately remain visible for reproducibility.

| Page | P/O | W/I/B | Visual note |
|---|---:|---:|---|
| `an-1436ae03653f-p000163` | 35/34 | 0/12/0 | Ornamental frame and lower decoration; main prose stable. |
| `an-1be60011c435-p000215` | 56/55 | 2/6/0 | Pale patchy fronts, changing column layout; stamp slivers. |
| `an-1c6e1c0e929e-p000167` | 30/29 | 1/5/0 | Mixed display/italic/body; rule and stamp confuse residual ink. |
| `an-1f8e7d022643-p000003` | 22/17 | 2/19/0 | Repeated frame boxed; widely spaced title; stanza grouping differs. |
| `an-2cfe28da5103-p000135` | 89/90 | 2/8/1 | Ruled two-column index; one bend flag without clear shared curl. |
| `an-3352d912f2e9-p000104` | 29/26 | 1/76/0 | Mottled paper, headings/drop caps; many residual false alarms. |
| `an-466cffad2cba-p000323` | 27/25 | 0/4/0 | Large older type, mild slope and stamp; body mostly stable. |
| `an-5c093c79d6bb-p000199` | 62/65 | 0/43/0 | Spread with edge shadow; running-head/margin disagreements. |
| `an-778126cc8c2b-p000010` | 49/37 | 0/23/0 | Verse and marginal quotation marks; stamp overlaps real text. |
| `an-7a2b17a3fb0f-p000200` | 658/879 | 46/148/0 | Dense numeric ruled spread; tiny cells and rules dominate residuals. |
| `an-9ea1564fcf4f-p000013` | 81/80 | 1/63/1 | Skewed spread and small footnotes; scan borders fire. |
| `an-a3c2bdf81256-p000112` | 118/237 | 7/26/0 | Grammar dashes and isolated numbers; ours fragments heavily. |
| `an-a73d22211479-p000301` | 47/90 | 0/0/0 | Two columns and central fine rule; small merges across gutter. |
| `an-b1a643813945-p000054` | 31/29 | 1/6/0 | Indented dialogue and footnotes; short rule is residual ink. |
| `an-c153f2c605b3-p000040` | 34/30 | 0/42/0 | Framed conjugation text and show-through; residual noise. |
| `an-c2c2053cfc10-p000056` | 74/74 | 2/8/0 | Spread with pale front print; small marginal/page-number disagreement. |
| `an-c8b96a901917-p000068` | 125/130 | 2/44/0 | Two leaves with two columns each; some narrow-gutter crossings. |
| `an-d3237d690aa0-p000138` | 297/673 | 0/4/0 | Four-column index with numbers; incompatible grouping counts. |
| `an-d6002cf45e4d-p000058` | 8/6 | 0/119/0 | Engraving and vignette lettering; ink scout floods picture. |
| `an-d6fd2cf2f618-p000047` | 37/34 | 3/6/0 | Pale foreground remains structured; stamp/blot at lower right. |
| `an-d83e7a198ade-p000099` | 120/82 | 4/31/7 | Large verse plus tiny apparatus; scale mixing and bend flags. |
| `an-e46611ae2fcc-p000041` | 64/61 | 2/37/0 | Spread with dark binding; many edge residuals, body mostly stable. |
| `an-e74539ae215c-p000338` | 97/93 | 2/9/0 | Dictionary type-family changes; stamp slivers and tiny marks. |
| `an-ef481610a820-p000181` | 36/34 | 3/56/0 | Mottled dialogue/ghosts; plausible missing continuations amid noise. |
| `an-fabf591ca801-p000067` | 75/67 | 0/46/0 | Spread with marginal chronology; missing marks/debris ambiguous. |
| `an-fd4fa0018ae1-p000037` | 31/32 | 2/9/0 | Short lower catchword/continuation near stamp needs inspection. |
| `an-ffccc97c07de-p000152` | 34/36 | 2/78/0 | Greek and Arabic; different guides and some merged script rows. |
| `s2-0683f98f964a6d41cb72-p00003` | 39/39 | 0/26/0 | Clean body; margin bleed/shadow drives residual flags. |
| `s2-09f5dfca4af4d74173c6-p00005` | 59/60 | 0/271/0 | Left ghost column/right foreground; small already rejects much ghost ink. |
| `s2-0ce9d1025b3f23c7119e-p00001` | 101/35 | 38/196/4 | Strong lower mirrored ghost print; many Paddle-only regions. |
| `s2-200e977f2dab5291c42c-p00035` | 195/318 | 3/119/0 | Ruled table and dot leaders; tiny row numbers and rule slivers. |
| `s2-23a70964fda83cb7aeb1-p00003` | 124/125 | 0/12/0 | Straight dense two-column control; main bands agree. |
| `s2-3229200bf47ca465a42d-p00004` | 43/38 | 3/11/11 | Correlated left curl; boxes cross rows and lose ends. |
| `s2-49598b2e848ab1f0ee1e-p00001` | 105/117 | 21/58/3 | Uneven/curved first words; weak map and missed-line candidates. |
| `s2-5ca02b142a2a3eaf078a-p00002` | 41/41 | 0/68/0 | Straight dark body; residuals mostly margins/borders. |
| `s2-60f24a3d8a2d714767f2-p00003` | 123/128 | 0/11/0 | Dense narrow columns; foot/page-number ambiguities. |
| `s2-63f072d79585d71224b6-p00002` | 40/39 | 0/14/0 | Clean body and centred heading; sparse edge residuals. |
| `s2-6419488b7f8e69fd20da-p00001` | 255/1282 | 15/85/5 | SIDEWAYS TABLE: orientation parked; no upright correction inference. |
| `s2-658e6dcb48b540357a9d-p00001` | 35/32 | 2/106/0 | Shaded display title, size changes and ghost/ornamental residuals. |
| `s2-661ddf05c8865e7b2c45-p00009` | 100/126 | 1/13/0 | Dense columns; count mismatch needs grouping/guide review. |
| `s2-6f552c96213b4c24a071-p00003` | 38/38 | 0/18/0 | Clean paragraphs/headings; edge ghost flags. |
| `s2-7247ee9b1bc2374b3980-p00001` | 111/111 | 0/153/0 | Greek/French columns; lower ghost text produces many ink flags. |
| `s2-74cdb23a34ca4a6cd01e-p00002` | 127/130 | 0/150/0 | Pale two-column print; many margin ghosts, mostly straight lines. |
| `s2-77d1bd63d5babbe0df73-p00001` | 39/39 | 0/0/0 | Clean control, including intentionally spaced signatures; zero flags. |
| `s2-80513ae109b4f749ca58-p00003` | 77/256 | 0/19/0 | Names and isolated voting marks; ours greatly overfragments. |
| `s2-831443dc5e6f1ccfbaf5-p00020` | 371/453 | 9/65/0 | Numeric table and leaders; tiny-cell ambiguities. |
| `s2-86865c33eef5932c013b-p00005` | 63/40 | 17/23/0 | Right curl with dense/broken strokes; truncated/fragmented boxes hide bend. |
| `s2-93f8070059f938bda524-p00001` | 128/116 | 24/160/0 | Ghost table/signatures; short headings and ownership ambiguous. |
| `s2-9de6cda8f03f0fc60a58-p00005` | 120/122 | 0/5/1 | Dense columns with heavy speaker/type changes; single bend flag. |
| `s2-be269b8c315b16befc35-p00002` | 41/42 | 0/55/0 | Clean narrow body; edge ink and isolated corner disagreement. |
| `s2-d1ed1c2db37f431f4acb-p00001` | 114/115 | 5/163/1 | Ghosts around blocks; bottom disagreement and one bend flag. |
| `s2-dee99fdf5214acdc6f25-p00005` | 43/41 | 2/10/0 | Budget leaders/rules; tiny continuation candidate. |
| `s2-dfcc21869afc140111ce-p00001` | 115/113 | 7/173/0 | Heavy ghosts in gaps; high residual count. |
| `s2-f9ec82212abc808325d7-p00010` | 38/38 | 0/1/0 | Clean control; single residual ink region. |

### Exploratory scripts and unverified matters

- `review_atlas.py`: assembled the 54-page and seven-stage contact sheets; showed the cross-feature failure patterns above without running a detector.
- `audit_evidence.py`: audited all nine caches and stage totals; exposed the flag-count discrepancy, word/line granularity, and sliver-count differences; rendered nine selected comparison sheets.
- `probe_colour.py`: found all 54 source pages grayscale, ruling out a colour-only stamp experiment on these pages.
- `probe_mirror_histograms.py`: measured reflected-versus-other-line histogram distances on 422 unlabelled dev crops; found a possible signal with substantial ambiguity, not classification accuracy.

Outputs live outside git at `.astra/fast_lines/out/q6_review/`. No detector was rerun and no correction prototype was built in Q6. The repo venv has ONNX Runtime **1.31.0**, but does **not** have `paddleocr` or `paddlex` installed (package-metadata check). Round 1 must provide a minimal, source-checked adapter instead of assuming the old stage script imports work. Exact current ONNX latency, per-feature accuracy, pixel-level guides, readable/unreadable labels, paired recto/verso identity, book identity, and owner agreement on ambiguous cases remain unverified.


## 2. The physics and typography of each feature

The charter's own descriptions remain the specification. This table explains mechanisms that could produce the observed page features; the physical causes are hypotheses unless the image itself establishes them. One raster rarely distinguishes light inking from fading, paper transmission from a later watermark, or true deformation from a printing defect.

| Feature in the charter | Physical/typographic account and observed pages | Route 1: explicit rendering to try | Route 2: cheap stand-in, with its counterexample |
|---|---|---|---|
| Curl / skew | A bound leaf bends several printed rows together; in-plane skew is approximately affine, binding curl varies with x and possibly y. `s2-3229`, `s2-8686`, spread `an-9ea1`. | Per-leaf displacement mesh plus independent line paths and residual anchors (A03/A04). | Sparse edge-slope agreement, strip correlation; a crease or mixed leaves defeats one field. |
| Faintness; show-through, bleed-through, watermarks | Light front ink, faded pigment, transmission from the reverse, and later overlays can all reduce local contrast. Diffusion often broadens ghost strokes, but sharp ghosts and blurred fronts exist. `an-1be6`, `s2-09f5`, `s2-0ce9`, `s2-dfcc`. | Separate paper, normalised darkness, edge spread and ownership-unknown maps (A05); optional source separation (A14/A16). | Normalised sparse edge profiles and threshold persistence; never a darkness-only deletion. |
| Inkiness; unreadable broken/filled letters | Incomplete transfer/wear can break strokes; excess ink/spread can fill counters. Scan blur, compression and native bold weight mimic both. `s2-8686`, `an-3352`, `an-ef48`. | Stroke widths, skeleton ends, counters and local original-size exemplars (A10). | Fragment/width/counter statistics within a compatible family; connected components are not glyphs. Readability can remain unknown. |
| Tables | Rules and aligned cells reflect layout, while numerical/dotted content resembles line fragments. `an-7a2b`, `s2-200e`, `s2-8314`, `s2-dee99`. | Rule graph/cells and separately retained Paddle cell text (A02); learned structure comparator A17. | Long runs plus aligned endpoints nominate a region. Borderless tables and semantic dashes prevent a universal rule veto. |
| Ignore images | Engraving hatching is ink with repeated strokes but different spatial support. Stamps contain real curved letters, and initials can be both art and type. `an-d600`, `an-1f8e`, `an-7781`. | Picture boundaries, direction/motif maps and overlapping text ownership (A08). | Residual density without coherent line flow nominates review; does not prove “picture”. Colour is unavailable in all 54. |
| Separate columns / leaves | A gutter is persistent whitespace or a separator within a layout band; two facing leaves may have unrelated skew/curl. `an-a73d`, `an-c8b9`, `an-d3237`. | Corridor/rule graph with page and block boundaries, crossed-box splits (A02). | Persistent endpoint trough/crossing witness. Centred headings, poetry and sparse lists must be allowed across a corridor. |
| Font properties | Manufactured type repeats body height, slant, weight and spacing. Different sizes/families coexist; print wear is not a new font. `an-e745`, `an-1f8e`, `an-d83e7`, `s2-8051`. | Local exemplar atlas of body profiles, stroke and spacing distributions (A07/A10). | Borrow compatible block estimates with residual checks. Font name classification is unnecessary; book priors require verified identity (A13). |
| Font guide geometry, scripts and accents | Baselines are alignment conventions, not density centroids. Greek accents detach, descenders vary, and mixed-script rows need different guides. `an-ffcc`, `an-466c`, `an-d83e7`. | Aligned strip profiles, component-to-guide support and optional multiple guide sets (A07). | Sparse support validates a borrowed profile. Short capitals/digits can make baseline/descender estimates unidentified; Latin can also have accents. |

Geometry, missing lines and false positives are **error types**, not mutually exclusive page classes. A curved ghost line can satisfy a rhythm test, a column merge can retain every ink pixel, and raising resolution can simultaneously recover footnotes and detect more verso text. Every proposed correction must therefore retain its evidence and interactions.


## 3. My dreams, written before reading the other dreamers

<!-- BEGIN INDEPENDENT DREAMS -->
These are Astra's independent hypotheses, written after looking at the 54 development pages, their seven-stage renderings, nine selected pages across all nine cached detectors and our output, and the stage-building code. No `dreams_*.md`, external literature, or project theory notes have yet been read. They are predictions, not results. Lengths below mean local letter heights or normalised page coordinates, not page-specific pixel constants.

**D01 — Give the detector's shape back to it.** On s2-3229 the likelihood bands visibly bend while the returned quadrilaterals cross neighbouring lines. First ask whether the contour has already solved the problem and a rectangle discarded the answer. Route 1: trace and expand that contour into a ribbon, preserving its bend; take normal cross-sections to display the body and its margin. Route 2: compare a cheap central/edge likelihood track with the quadrilateral, and invoke contour tracing only where the shape departs. Vary the map threshold and expansion independently: a missed contour, a rejected contour, and an overgrown accepted contour are three different events. No second neural pass should be necessary to test this. Accents outside the learned band and two joined lines remain dangers.

**D02 — A line is a path through ink, not its centre of mass.** Type gives a repeated body zone interrupted by spaces, ascenders, descenders and accents. A mean drifts with the words and can run through white space between two lines. Route 1: in a Paddle-localised strip, follow a dominant ink/likelihood ridge with an explicit continuity constraint; fit a small set of upper/lower body rails, then attach accent islands. Let paths split when two ridges persist; never average them into an invented line. Route 2: sample a few normal cross-sections, including outside both box ends; a two-peak profile or endpoint departure asks for the full strip. Verify against enlarged ink, current guides, and a slow dense ridge fit. Clean straight boxes need only sparse samples. This directly joins skew, curvature, letter height and clipped first letters.

**D03 — The book bends many lines together.** Binding acts on a sheet, not independently on every sentence. On s2-3229 many left ends share a bend; on s2-8686 the right ends rise. Route 1: fit a low-dimensional displacement field per physical leaf, with a separate affine component for skew. Draw the field as a mesh and every predicted line, with residual arrows to measured ink anchors. Work in coordinates; do not resample the whole image just to deliver lines. Route 2: agreement of a few edge slopes across nearby lines is a witness for a shared curl; apply the fit only on that leaf and only if local residuals permit. A crease or local disturbance gets a local path instead. A shared bad detector bias must not masquerade as paper physics; two leaves must not share one bend merely because they appear in one PNG.

**D04 — Account for the spaces between lines as well as the lines.** Looking only inside accepted boxes cannot discover a lost paragraph. Route 1: an explicit residual-ink ledger: subtract accepted text support, rules and images, then group the remaining foreground-like strokes along nearby text flow. Display the residual itself before adding any line. Route 2: a sparse page-wide scan for unexplained coherent ink and gaps in the local line rhythm nominates strips for this ledger. A weak-map island is supporting evidence, not a prerequisite. Check beyond paragraph boundaries and in margins too. Short catchwords, missing initials and isolated page numbers need distinct handling from a whole missing line. Cost follows the unexplained area; most pages should not pay for full-resolution connected components everywhere. Never manufacture a line to fill an expected rhythm slot.

**D05 — Faintness has depth; inkiness has shape.** A front-page stroke can be weak but sharply drawn; a back-page stroke can be pale and diffused through paper. A watermark may instead be a sharp added layer. Route 1: show local paper-normalised darkness, edge spread and the topology of individual stroke fragments as separate renderings; put ambiguous overlapping ink in an explicit unknown layer. Route 2: a few cross-stroke profiles per suspect line, relative to adjacent credible foreground print, can stand in for the expensive rendering. Sweep intensity levels and watch which ridges remain in the same place rather than choosing one binarisation. Sharp weak fronts should persist geometrically; diffuse ghosts may spread or disappear. This is not an assumption that dark means front. On s2-09f5 the left ghost column and the right foreground are a useful visual contrast; an-1be6 is the counterexample that must preserve pale real text. Only doubtful regions pay for profiles.

**D06 — Diagnose ink by how a letter can break or fill.** Too little ink loses bridges; too much ink fills counters and fuses strokes. Neither is equivalent to low darkness. Route 1: skeleton, distance-to-boundary, counter and endpoint renderings on representative character-like components, with original pixels alongside; compare width and holes within a locally consistent font. Route 2: component fragmentation, stroke-width distribution and counter survival sampled per line. Never call every detached accent a fracture or every naturally bold letter over-inked. Broken bodies may be linked for line geometry without inventing the missing glyph. Use this only for disputed textness/readability or damaged-line repair; a full glyph census is unnecessary on clean pages. A black-and-white scan cannot recover missing tonal evidence.

**D07 — Respect the printer's furniture.** Rules, cell edges and aligned number columns describe a table more directly than a huge line count does. Route 1: render long thin strokes, intersections and a cell/column lattice, retaining gaps where a rule is broken. Hand the cell's text localisation to Paddle. Route 2: a few long connected runs plus repeated box-edge alignments nominate a table region for explicit verification. Borderless lists also have alignment, but should not automatically be forced into a ruled grid. The lower apparatus on an-d83e7 and the dense table on an-7a2b are scale traps. A Greek dash, repeated ditto marks, or a decorative frame is not by itself a table. Rules are barriers or furniture, never new text proposals. The expensive work is regional.

**D08 — An engraving is a different kind of repetition.** Text repeats strokes in narrow height bands along a flow; engraving hatching repeats over an area and many directions. Route 1: render local direction fields, stroke-scale distributions and connected picture boundaries, with captions and embedded lettering separately visible. Route 2: disagreement between lots of uncovered ink and little coherent line evidence is a request to inspect a possible image, not proof that it is an image. On an-d600 the detector correctly ignores most of the engraving while the ink scout would undo that success. Stamps have curved letter flow and circular borders; their overlap with real lines needs local ownership, not a rectangular eraser. Decorative initials are simultaneously typography and pictures. A cheap regional veto should suppress speculative recovery there, while keeping the detector's plausible text until the explicit rendering justifies a change.

**D09 — A gutter is persistent absence or a separator, not one large word space.** Route 1: render whitespace corridors and rule barriers across neighbouring lines, using box endpoints and the page's ink. Split a Paddle band only where the corridor persists through a block. Route 2: a long box crossing an established corridor is a cheap geometry-error witness. an-a73d has many apparently complete Paddle bands that are actually two columns merged; no missing-ink detector will catch that. On an-c8b9 there are two physical pages, each with its own columns. Paragraph indents, centred headings, verse and sparse tables invalidate a universal vertical split. The evidence must be local to the layout band, and the cost proportional to ambiguous crossings.

**D10 — Discover the number of guide lines from the script.** Greek polytonic marks occupy bands above a body; Arabic-like connected writing, capitals, and tiny footnotes produce other distributions. Route 1: align normal ink profiles from a few confident line strips and show the recurring vertical modes as candidate guides, with their supporting components. Keep different scripts/sizes separate without needing OCR labels. Route 2: reuse a block's measured height/guide signature on compatible lines, testing sparse residuals; borrow only with labelled provenance. A four-guide Latin assumption cannot be silently imposed on an-ffcc's mixed scripts. Baseline, body centre and bottom of a box are different objects. A short all-accent or all-capital sample may not identify a baseline; uncertainty is an output, not a missing value to fake.

**D11 — Treat type as repeated manufacture.** Repeated type brings recurring body height, stroke width, slant and spacing; letterpress wear varies their appearance. Route 1: build an explicit local family atlas of normalised ink profiles and spacing distributions, with exemplars displayed from the page. Route 2: a few measured lines initialise a block prior and, only with actual book identity, a reusable book prior. Detect font changes from incompatible body profiles rather than make every line repeat the same measurement. Wide-spaced titles on an-1f8e and dictionary columns on an-e745 are counterexamples to a single page-wide gap rule. Typeface identification by name is unnecessary: geometry and compatibility are enough. Book-level reuse must include a reset on new font, resolution, page scale or print condition; filenames alone are not proof of a shared book.

**D12 — Buy resolution only where information is missing.** Small print in an-7a2b or an-d83e7 may occupy too few network cells; changing thresholds cannot restore erased strokes. Route 1: rerun a small region at a sampling scale derived from its letter height, then explicitly map its contours back to page coordinates. Route 2: too few map samples per body height, fragmented contour topology, or persistent unexplained ink triggers that crop. Merge overlapping crop requests and keep a coordinate receipt to prevent duplicated text. A full-page higher-resolution pass is a comparator, not the default. More resolution may expose back-page print as readily as front-page print; photometric checks remain necessary. Keep total corrected area and real latency visible.

**D13 — Let every extra operation have a visible reason.** A page is cheap when its text is already explained. Route 1: an evidence ledger displaying supported text, uncertain residuals, geometry discrepancies, separators and image regions can itself be the fast explicit model. Route 2: sparse witnesses on map/box geometry, raw-image ink and local print compatibility wake only the relevant renderer. An empty detector output must trigger a page-level check, never qualify as a clean page. A high confidence score cannot certify a absence of missed text. The always-on part must be measured separately; lazy caches and reusing map/ink work matter more than a fancy global switch. For ambiguous pages, abstain or invoke an explicit local fallback; report the exceptional cost instead of claiming everything takes detector time.

**D14 — Use physical perturbations and a second side as questions, not truth.** A tiny threshold change, blur or scale change can reveal whether a candidate is a stable printed structure; synthetic fading/breaking/curving of existing strips can expose a proposed shortcut's assumptions. Route 1: explicitly render the changed pixels, displacement field and known synthetic correspondences. Route 2: use instability only as an uncertainty cue; a stable ornament is still not prose. If independently available recto/verso scans exist, mirrored registration and a transmission model could explicitly render show-through, with sparse correlation as its fast witness. We do not have verified paired sides here. Do not pull held-out pages into this experiment or claim synthetic damage establishes real-world success. Run this off the production path, once for all prototypes.

Across these dreams, a run-length/projection implementation is worth trying before per-pixel Python work: it can render ink bands, gaps, rule continuity and vertical profiles directly. It cannot decide foreground ownership on its own. The most radical simplification may be to keep a small, explicit model of the sheet, print families and line paths, and only resolve individual strokes where those models disagree with the page. None of this requires reproducing our old detector's output exactly.
<!-- END INDEPENDENT DREAMS -->

## 4. What the other dreamers added

I read **every** available `dreams_*.md` after freezing section 3: [Fable's dreams](../../.astra/fast_lines/dreams_fable.md), then the later-arriving [coordinator's dreams](../../.astra/fast_lines/dreams_coordinator.md). The latter appeared during final validation, after the initial survey; I extended the survey and map to include it. The owner's earlier charter ideas remain shared context. **F01–F18** mean Fable's numbered dreams; **C01–C18** mean the coordinator's, distinct from Astra's D01–D14.

| Fable dream | Agreement / addition after the freeze | Where it enters the single map |
|---|---|---|
| F01 type lattice | Adds explicit strip correlation, pitch/phase and shared displacement to D03's sheet model. Agreement is a reason to test, not proof. | A04, A06 |
| F02 box audit | Height/pitch and phase are useful cheap witnesses; a second lattice could be verso or another real block. | A02–A04, X01 |
| F03 curved geometry | Strong agreement with coordinate-only shared curl, avoiding full-image resampling. | A04 |
| F04 local unbend/rerun | Adds unbending before D12's selective scale pass. A small crop is not automatically a small neural input. | A09 |
| F05 stacked six guides | Strong agreement with aligned block profiles; replace fixed guide count with measured support. | A07 |
| F06 sharpness vs darkness | Strong agreement with D05; sharpness alone still cannot guarantee front ownership. | A05 |
| F07 mirrored verso | Strong agreement with conditional D14; explicit registration is useful, not exact truth. No verified paired sides here. | A14 |
| F08 smooth ink field | Adds spatial smoothness across letters to D06. Permit local damage and family changes instead of forcing a smooth cause. | A10 |
| F09 printer furniture | Strong agreement with rules/cells; also covers frames. | A02 |
| F10 images/stamps | Adds colour saturation. Exact probe shows all 54 images are grayscale; colour branch is inapplicable here. | A08 |
| F11 repeated motifs | Adds autocorrelation/template repetition for ornaments/leaders. Repeated glyphs, digits and ditto marks must survive. | A08 |
| F12 column troughs | Strong agreement with persistent, block-local gutters. | A02 |
| F13 book font prior | Strong agreement with D11; no verified book identity, and curl cannot be fixed once per volume. | A13 |
| F14 foreground outside boxes | Strong agreement with D04; retain an independent scout when the map misses an entire block. | A06, A12 |
| F15 endpoint walk | Strong agreement with D02; follow the path beyond the existing envelope. | A03 |
| F16 map-first fallback | Adds a clear experiment: line finding on the learned map before raw ink. Still blind to absent map signal. | A11 |
| F17 glyph ink grammar | Adds a slow explicit referee for damage. Components need not be glyphs; ambiguous readability remains unknown. | A10, shared R03 |
| F18 easy-page condition | Strong agreement with D13's lazy scheduling; “absence of evidence” requires coverage, not only good scores. | X01 |

Fable's millisecond estimates are hypotheses; none were measured here. The original dreams remain unchanged even where the survey or these checks weaken them. In particular: Latin does not imply no accents; digits do not universally identify a no-descender baseline; front/back separation is not certain from sharpness or registration; and a book does not have one immutable bend.


### The coordinator's additions and disagreements

| Coordinator dream | Agreement / addition | Single-map destination |
|---|---|---|
| C01 map ridge | Strong agreement with D01/D02/F15; map geometry can precede repair. A weighted centre can average two rows and is not a baseline. | A01/A03 |
| C02 shared curl | Strong convergence with D03/F03. Use one field per physical leaf with residual checks, not necessarily one curve per column or a pixel-valued flatness gate. | A04 |
| C03 skew plus residual | Makes the inexpensive affine box-tilt estimate explicit; useful as an initializer. Real blocks/leaves can have different slopes. | A04, X01 |
| C04 two grids | Adds a concrete front/verso pitch/phase/column/skew mixture to the ownership question. Dominant grid is not automatically front; both sides may be printed in register. | A04/A05 |
| C05 mirror signature | **New to Astra's and Fable's dreams:** contrast a line's edge-direction distribution with reflected compatible text. Requires its own falsification and glyph-level rendering. | A19 |
| C06 two ink numbers | Agreement on contrast versus stroke condition. Low model score alone misses high-scoring damaged/ghost text; use independent witnesses. | A05/A10 |
| C07 missing grid slots | Agreement with rhythm nominations. Entire missing blocks, indented short lines and verso ink require the independent scout too. | A06 |
| C08 selective higher sampling | Agreement with D12/F04. Actual network tensor shape, not source crop area alone, determines cost. | A09 |
| C09 orientation | A recognisable proposal, but conflicts with the explicit parked scope. It is mapped, not executed. | P01 parked |
| C10 table lattice/rules | Strong agreement: protect Paddle cell boxes, do not apply prose slots or cross-cell curls. Adds an optional Docling structural handoff. | A02; A17 optional |
| C11 outside-band/periodic/round | Adds ring-like stamp and tall-initial witnesses. Marginal text and repeated digits defeat simple vetoes; keep initials attached to real lines. | A08 |
| C12 box column bands | Agreement with D09/F12; cross-gutter merged boxes can contaminate the endpoint clustering itself. | A02 |
| C13 guides on demand | Strong agreement on conditional profiles/spacing. Four strongest profile steps need not be baseline/meanline/ascender/descender for every script. | A07 |
| C14 book prior | Agreement with D11/F13, but books may change type, paper, plate/layout and scan conditions. Identity and compatibility are required. | A13 |
| C15 four-number gate | Clear explicit witnesses, shared with D13/F18. They must retain spatial coverage and exceptions; good global medians can hide one missed region. | X01 |
| C16 outer-fifth witness | Explicit agreement with the owner's edge check. The `s2-8686` zero-flag counterexample requires looking beyond the old box. | A03 |
| C17 mirrored neighbour | Agreement with D14/F07. A neighbouring scan is not established to be the other side of this leaf; pairing and elastic alignment need proof. | A14 |
| C18 one page record | Adds a useful explicit joint review product: reusable leaf/block, skew/curl, table and type evidence instead of independent per-line recalculation. | S4 contracts / X01 |

The coordinator's observation that “real text never” repeats is too strong: repeated numbers, ditto marks, leaders and display lettering are counterexamples. Its 63 ghost-line description and roughly 17 flags/page are not adopted as ground-truth counts; section 1 states what the supplied summary actually measures. The timings and confidence levels in that dream file remain predictions. Triple independent convergence on map geometry, shared sheet shape, conditional profiles and sparse recovery increases their priority, but does not prove the proposed shortcut.

C05 prompted one small **post-dream** measurement, reported in section 1 and in A19. It does not amend the independent dreams or establish front/back classification.

## 5. The survey, with citations

Sources were checked on 2026-10-10. These are primary papers, author repositories, library source and official documentation. “Known” means the mechanism has a close published neighbour, not that its speed or suitability for these historical Greek pages has been established. No method here is claimed as a novel invention.

### Detector options before another model

**S01 — Paddle's supported controls.** The [official text-detection module documentation](https://www.paddleocr.ai/latest/en/version3.x/module_usage/text_detection.html) exposes `limit_side_len`, `limit_type`, `max_side_limit`, `thresh`, `box_thresh`, `unclip_ratio`, and input-shape controls. Model defaults must be resolved from the selected configuration: `None` in the API is not an experimental value. Threshold, accepted-box score, expansion and input sampling affect different failure points. These are A01/A09's first ablations; no retraining is needed.

**S02 — Polygon versus quadrilateral is real, but check the plumbing.** [PaddleX's DB postprocessor source](https://raw.githubusercontent.com/PaddlePaddle/PaddleX/develop/paddlex/inference/models/text_detection/processors.py) contains `box_type="poly"` and `"quad"`, contour approximation, polygon expansion, dilation and score-mode options. Quad reconstruction can discard curvature. Poly can retain it but still reject short contours or problematic expansion results. The public module signature does not document every postprocessor knob as a direct constructor argument; do not assume `TextDetection(box_type="poly")` works. Pin the source/config and route it through a research adapter. [PaddleOCR's corresponding DB source](https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/main/ppocr/postprocess/db_postprocess.py) independently exposes these paths. Source constructor defaults are not proof of the shipped v6-small configuration.

**S03 — What the map means.** [DBNet, Liao et al.](https://arxiv.org/abs/1911.08947) learns differentiable binarisation for text detection; [DBNet++](https://arxiv.org/abs/2202.10304) adds adaptive scale fusion. This supports separating segmentation from geometric postprocessing. It does not make the output a calibrated foreground-ink, legibility or baseline probability. Starting from the supplied long-side-960, stride-32, BGR→RGB, ImageNet-normalised input is essential to avoid a preprocessing experiment masquerading as a geometry improvement.

### Geometry, baselines and page curl

**S04 — Explicit classical sheet models.** [Leptonica `dewarp2.c`](https://raw.githubusercontent.com/DanBloomberg/leptonica/master/src/dewarp2.c) fits line centres and smooths their displacement into a page field; its horizontal assumptions include approximately aligned long-line endpoints. It provides an unusually direct slow visual neighbour for A04, including failure when support is sparse. [Zucker's page-dewarping method](https://mzucker.github.io/2016/08/15/page-dewarping.html) and [author code](https://github.com/mzucker/page_dewarp) fit a compact page model from text-line evidence. We can compare meshes without committing to resampling pixels. Neither makes two leaves one surface.

**S05 — Learned dewarping alternatives.** [DewarpNet](https://openaccess.thecvf.com/content_ICCV_2019/html/Das_DewarpNet_Single-Image_Document_Unwarping_With_Stacked_3D_and_2D_Regression_ICCV_2019_paper.html), [author implementation](https://github.com/cvlab-stonybrook/DewarpNet), [DocTr](https://arxiv.org/abs/2110.12942), and [its implementation](https://github.com/fh2019ustc/DocTr) offer learned geometry/illumination representations. **DocTr dewarping is not docTR OCR**, which appears in our detector caches. These are A15's optional offline mesh comparators; photographed-document results do not establish reliable historical scan correction or local latency.

**S06 — Lines are paths, not boxes.** [ARU-Net/two-stage historical line detection](https://arxiv.org/abs/1802.03345) separates learned baseline evidence from subsequent grouping. [Kraken's segmentation documentation](https://kraken.re/6.0.0/advanced/segmentation.html) describes heatmap-derived baselines and boundary extraction. [READ-BAD](https://arxiv.org/abs/1705.03311) evaluates baselines as geometric objects, a useful warning against box-count scoring. Reuse our cached Kraken outputs as an independent view before considering another network (A18). They still require visual adjudication.

**S07 — Ribbons and seams.** [TextSnake](https://arxiv.org/abs/1807.01544) represents curved text with local centreline geometry rather than a rigid rectangle. [SeamFormer, author project](https://ihdia.iiit.ac.in/seamformer/) connects learned line evidence and seam-based extraction. These are representational neighbours of A03/A11; adopting a ribbon or a constrained path does not require training their networks. A baseline must subsequently be tied to type support, not renamed from a centreline.

### Foreground, ink and classical low-cost analysis

**S08 — Binarisation is evidence, not ownership.** [scikit-image's official Sauvola documentation](https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_sauvola) supplies a local-statistics reference; [Wolf et al.'s original contrast-adaptive work](https://chriswolfvision.github.io/www/papers/icpr2002v.pdf) supplies a nearby alternative. Their threshold masks are useful explicit views for A05/A12, but both sides of the sheet can satisfy them. [Water-Filling shadow removal](https://arxiv.org/abs/1904.09763) is a different illumination model, relevant to A16; shadow correction is not bleed-through separation.

**S09 — Actual bleed-through models.** The authors' [Blind Bleed-Through Removal with Conditional Random Fields abstract](https://pubmed.ncbi.nlm.nih.gov/28114067/) describes a single-image spatial model; [Gerace, Martinelli and Tonazzini's regularised recto-verso model](https://new.eurasip.org/Proceedings/Eusipco/Eusipco2012/Conference/papers/1569583261.pdf) uses both sides. These support A16 and A14 respectively. They add something beyond intensity cutoffs: explicit assumptions about latent sources and spatial consistency. The separate Savino/Tonazzini local-registration PDF found in the survey could not be fetched (403); no detailed claim relies on it. Paired-side methods are conditional on genuinely paired scans and adequate registration.

**S10 — Stroke geometry and region persistence.** [Epshtein, Ofek and Wexler's Stroke Width Transform](https://iacl.ece.jhu.edu/proceedings/cvpr2010/papers/1509.pdf) uses opposing edges to estimate stroke width and group text-like structure. [Matas et al.'s maximally stable extremal regions](https://cmp.felk.cvut.cz/ftp/articles/matas/matas-tr-2001-33.pdf) supplies an explicit threshold-stability mechanism. These are useful literature additions to the dreams: A12 can test a map-independent component graph with A10's stroke measurements. Neither constant stroke width nor stable components establish readability, and disconnected Greek marks need contextual attachment.

**S11 — Cheap shared operators.** [OpenCV's rule-extraction tutorial](https://docs.opencv.org/4.12.0/dd/dd7/tutorial_morph_lines_detection.html), [integral-image/distance-transform functions](https://docs.opencv.org/doc/doxygen/html/d7/d1b/group__imgproc__misc.html), and [phase correlation](https://docs.opencv.org/4.x/d7/df3/group__imgproc__motion.html) provide concrete operators for runs/rules, local statistics, stroke depth and strip displacement. Kernel sizes in an example are not portable page constants. [Tesseract's baseline source](https://raw.githubusercontent.com/tesseract-ocr/tesseract/main/src/textord/baselinedetect.cpp) includes robust line fitting and spacing-grid constraints: a close neighbour to Fable's lattice audit, including the need to retain independent estimates. Run-length projections and component-neighbour grouping are established classical strategies; the exact Docstrum original was located but its [publisher DOI](https://doi.org/10.1109/34.244677) was inaccessible, so it is a follow-up lead rather than a fully checked implementation source.

### Typography, ornaments and tables

**S12 — Script and font geometry.** [OpenType's BASE specification](https://learn.microsoft.com/en-us/typography/opentype/spec/base) explicitly distinguishes baseline systems and extents by script. It informs what we must display, not a way to retrieve metrics from an unknown scanned font. [Tesseract's own normalisation tutorial](https://tesseract-ocr.github.io/docs/das_tutorial2016/3CharacterClassifiers.pdf) distinguishes baseline/x-height normalisation from moment-based normalisation. This supports A07's separation of body, baseline and bounding envelope. [DeepFont](https://arxiv.org/abs/1507.03196) is a font-identification neighbour; identifying a named font is deferred because compatible local geometry is the immediate requirement (A13).

**S13 — Repetition can be pictured explicitly.** [Historical Printed Ornaments: Dataset and Tasks](https://arxiv.org/abs/2408.08633) and its [project](https://printed-ornaments.github.io/) make ornament identity/repetition an established research object. That supports F11's repeated-motif experiment in A08, without implying a generic ornament classifier transfers to stamps, initials or dot leaders. A view showing the actual repeated crops is more persuasive than a scalar autocorrelation score.

**S14 — Learned table structure is a distinct neighbour.** [Microsoft's Table Transformer/PubTables-1M repository](https://github.com/microsoft/table-transformer) provides table detection and structure models with row/column/cell output. A17 can use these as a slow optional comparator for borderless structure; their training domain and latency on our Mac remain untested. Reading extracted PDF text or dataset text annotations would not create a reference transcription for our pages.

**S15 — Mirror direction is a real neighbouring problem, not solved by one histogram.** [Lin et al., Visual Chirality](https://arxiv.org/abs/2006.09512) studies visual statistics changed by reflection, including low-level imaging cues. It is a conceptual neighbour to C05/A19, not validation of an edge histogram for historical Greek show-through. A marginal histogram discards spatial glyph arrangement; paired opposing stroke edges and axis-aligned type can make it nearly symmetric. The Q6 probe above checks that risk empirically. [Dubois and Pathak's recto-verso bleed-through paper](https://www.site.uottawa.ca/~edubois/documents/dubo01pics.pdf) is a directly relevant paired-image neighbour for C17/A14; it does not establish our scans' pairing.

**S16 — Coordinator-specific structural neighbours.** [Tesseract's orientation/script source](https://raw.githubusercontent.com/tesseract-ocr/tesseract/main/src/ccmain/osdetect.cpp) is an established neighbour to C09; a text baseline axis alone cannot distinguish 0° from 180°, and tall boxes may be isolated upright characters or rules. Orientation remains parked. For C10's optional table handoff, [TableFormer](https://arxiv.org/abs/2203.01017) and [Docling's official pipeline options](https://docling-project.github.io/docling/reference/pipeline_options/) provide explicit structure models and fast/accurate modes. These extend deferred A17; they do not justify another model on clean pages or override the small detector inside known table cells.

### What the survey changes

The strongest immediate opportunities need no new model: retain contour geometry, respect gutters/rules, measure local paths, and share a sheet/profile representation. The literature also supplies genuinely independent alternatives to our map: stable intensity regions, stroke edges, blind source separation, and learned layout. They belong in the map even when deferred. The precise proposed integration, witnesses and cost gates are our research design; this survey is not an exhaustive novelty search or evidence that any estimated millisecond budget is achieved.


## 6. One map

### Reading the map

**G / M / F** mean geometry / missed-line / false-positive correction. **R1** is a different fast explicit rendering; **R2** is a fast witness standing in for a slower explicit rendering. “Both” means test them side by side using the same evidence, not build two unrelated pipelines. Origins list independent contributions; C labels denote the later coordinator dream, while the charter remains shared starting context. The mechanisms are mostly known; the proposed conditional combination and its applicability here are untested.

All costs below are **Astra's rough engineering envelopes, not measurements or paper benchmark claims**. They are additional milliseconds per page with the base map already available, excluding review I/O and model startup. Ranges assume vectorised/native operators and limited nominated regions; Python per-component loops or large full-resolution pages may be much slower. Deep-tool ranges are deliberately broad. Costs are not additive because the inputs are shared. A zero means a branch is not called, not that its witness is free. The shared always-on work has an aspirational **2–10 ms** envelope to test; that is challenging given the historical 482 ms extra-work mean.

| Rank / ID | Approach and origin | Features; errors | Route / conditional cost | Nearest neighbours; round 1 |
|---|---|---|---|---|
| 1 A01 | Native contours and detector controls — Astra D01, charter, literature | Bend, extents, faint/tiny bands; G/M/F | Both; 1–15 ms postprocessing, zero new inference at fixed map | S01–S03; **yes** |
| 2 A02 | Gutters, leaves, rules and cell barriers — Astra D07/D09, F09/F12, coordinator C10/C12 | Columns, tables, frames; G/M/F | Both; 2–20 ms coarse; 10–80 ms regional refinement | S11/S14; **yes** |
| 3 A03 | Local line ribbons and endpoint walks — Astra D02, F15, coordinator C01/C16 | Curl/skew, clipping, merged rows; G/M | Both; 1–5 ms scout, 5–60 ms selected strips | S06/S07/S11; **yes** |
| 4 A04 | Shared leaf displacement and type lattice — Astra D03, F01–F03, coordinator C02–C04 | Curl/skew, line spacing; G/M/F witnesses | Both; 2–20 ms map fit; dense referee 100–1,000 ms offline | S04/S11; **yes** |
| 5 A05 | Foreground ownership from profiles / competing grids — Astra D05, F06, coordinator C04/C06 | Faint fronts, ghosts, watermarks; F/M | Both; 1–5 ms samples, 10–100 ms suspect areas | S08–S10; **yes** |
| 6 A06 | Residual-ink and missing-line ledger — Astra D04, F14/F01, coordinator C07 | Whole/partial missing text, margins; M/F | Both; 2–10 ms sparse scan, 10–100 ms nominated strips | S08/S11; **yes** |
| 7 A07 | Adaptive font-family and guide profiles — Astra D10/D11, F05, coordinator C13 | Height, spacing, scripts, accents; G/M/F witnesses | Both; 2–10 ms samples, 10–80 ms new families | S11/S12; **yes** |
| 8 A08 | Picture/stamp ownership and repeated motifs — Astra D08, F10/F11, coordinator C11 | Images, stamps, ornament, leaders; F/M protection | Both; 1–5 ms region cues, 10–100 ms doubtful regions | S10/S13; **yes**, grayscale only |
| 9 A09 | Selective scale or unbend-and-rerun — Astra D12, F04, coordinator C08 | Tiny print, severe curl; G/M | Both; 0 if not called; 20–200+ ms for crop batch, potentially base-pass cost per crop | S01/S04/S05; **yes** |
| 10 A10 | Ink-condition field and stroke grammar — Astra D06, F08/F17, coordinator C06 | Broken/filled letters, weight; G/M/F evidence | Both; 2–10 ms samples, 20–200 ms suspect patches | S08/S10/S12; **yes** |
| 11 A11 | Map-first seam/line-graph fallback — F16, Astra D02, literature | Difficult map-present lines; G/M | R1 plus R2 dispatch; 10–100 ms regional | S06/S07; **yes** |
| 12 A12 | Map-independent stable-region/stroke graph — literature, Astra D05/D14/classical note | Map-blind faint text, missing blocks; M/F | Both; 10–150 ms region; full-page 50–500+ ms | S08/S10/S11; **yes**, bounded diagnostic |
| 13 A19 | Mirrored-type signature — coordinator C05, literature | Show-through; F/M protection | Both; 1–10 ms sampled, 20–200 ms glyph referee | S15; deferred after Q6 ambiguity probe |
| 14 A13 | Verified book priors / font retrieval — Astra D11, F13, coordinator C14, literature | Repeated typography; G/M/F evidence | Both; 1–5 ms compatibility; 20–200 ms new atlas, learned retrieval unknown | S12; deferred, identity missing |
| 15 A14 | Registered recto/verso transmission — Astra D14, F07, coordinator C17 | Show-through; F/M protection | Both; 50–1,000+ ms registration/fit, cheaper reuse unmeasured | S09; deferred, paired inputs missing |
| 16 A15 | Physical or learned dewarp comparator — literature, Astra D03/F03 neighbour | Non-simple curl; G | R1 slow reference, possible distilled R2 later; 100–5,000+ ms | S04/S05; full adapters deferred |
| 17 A16 | Blind source/illumination separation — literature, Astra D05/F06 neighbour | Ghosts, shadows, faintness; F/M | R1 reference, possible sampled R2; 100–5,000+ ms | S08/S09; deferred |
| 18 A17 | Learned table/layout reference — literature, coordinator C10 (Docling) | Borderless structure and cells; G/M/F | R1 reference, R2 region trigger; 100–3,000+ ms | S14; deferred |
| 19 A18 | Independent learned baseline reference — literature, cached Kraken | Baselines and curved text; G/M | R1 reference, R2 fallback only if needed; cached read now, new run 500–5,000+ ms | S06; new inference deferred |
| parked P01 | Orientation from boxes / script evidence — coordinator C09, literature | Sideways pages; out of scope | R1 angle rendering / R2 histogram; hypothetically 1–5 ms scout plus rerun | S16; **parked, no correction experiment** |
| X01 | Lazy evidence scheduler / joint page record — Astra D13, F02/F18, coordinator C15/C18 | All three errors and cost | Both; shared 2–10 ms always-on target, plus activated work | Conditional composition of known operations; **shared round 1** |
| X02 | Physical perturbation referee — Astra D14 | Tests witnesses across all features | R1 synthetic rendering, R2 stability diagnostic; offline 50–500+ ms per page/variant | S08/S10 stability neighbours; **shared round 1** |

### One entry per approach

**A01 — Retain native geometry before repairing it.** Known DB controls, proposed application to these errors. Preserve the float map; compare raw contour, accepted contour, unclip result and final quad/poly at fixed input. An explicit contour ribbon is R1; shape/score disagreement is R2. Verify with **R01** (raw page, map, stage-by-stage contours) and original-size accent/end crops, with ours' nondiscounted guides only as a second view. Smallest sketch: replay one cached float map per page through a compact parameter ablation, emit before/after detector JSON and rejection-reason counts. If float maps are absent, infer once per page; JPEG heatmaps are unsuitable numerical substitutes. No extra network pass for a threshold/unclip experiment. Inputs missing from the map remain missing.

**A02 — Barriers before grouping.** Known morphology and whitespace layout; joint leaf/gutter/cell use proposed here. A rule graph plus persistent whitespace corridors explicitly shows what separates text. Endpoint/rule crossings nominate only ambiguous blocks. Verify **R02** corridor/cell masks over raw pixels, including spanning headings and broken rules. Smallest sketch: extract one shared run representation, split only clearly crossed corridors and assign existing Paddle lines to provisional cells. Render why each split is allowed; do not reconstruct a table's text from ours. Costs rise only for complex bands. The `an-a73d` case motivates this before residual recovery.

**A03 — Follow a local ribbon, then its ends.** Known path optimisation/local geometry, independently dreamed. R1 is a multi-ridge strip path with top/body/bottom support; R2 samples sparse cross-sections, endpoint support and ridge multiplicity. Verify **R03** dense independent strip fits plus actual ink, preserving disconnected accents. Smallest sketch: trace selected curved/clipped bands and walk beyond both old ends; compare with no-change controls and A01's contours. Output polylines, envelope polygons, sampled support and unresolved alternatives. Disagreement wakes work, not a mandatory full strip census. A line centre must not be emitted as a baseline without guide evidence.

**A04 — Fit the sheet and its local rhythm once.** Known dewarping/grid neighbours, strong independent convergence. R1 fits a robust field per physical leaf from several line anchors, allowing an affine skew term and x/y variation; R2 uses strip correlation and pitch/phase consistency to nominate the field and audit boxes. Verify **R04** dense anchors, field mesh and residual vectors against raw bent letters; compare independent A03 paths. Smallest sketch: fit a small displacement model on nominated leaves, then render all predicted paths and their failures. Cost scales with anchors, not a repeated dense fit for every line. A broad phase change can be a heading or a ghost lattice; it never authorises invented rows.

**A05 — Separate low contrast from uncertain foreground.** Known local photometry/edge analysis; the joint ownership witness is unvalidated. R1 displays paper estimate, contrast, edge spread and threshold persistence separately; add coordinator C04's competing grid memberships from A04 as another explicit layer. A grid becomes evidence only with ink and typography, not because it is dominant. R2 samples compatible front candidates and doubtful regions, abstaining where source layers overlap. Verify **R05** original-size front/ghost exemplars, profiles and an unknown mask; the observer checks that pale foreground stays visible. Smallest sketch: compare one contrast-only baseline to the shared edge/persistence features on nominated regions; propose suppression only with visible evidence and preserve all decisions in a non-rendered ledger. This spends nothing on detailed profiles where no photometric doubt arises, beyond the common scout.

**A06 — A missing-line ledger that can discover absent boxes.** Classical residual grouping plus the independently dreamed accounting model. R1 renders unexplained foreground-like support and candidate tracks; R2 scans independently of accepted boxes and samples local pitch gaps. Verify **R06** raw residual mosaics, unboxed ink crops and recovered-line overlays; inspect the unexplained remainder too. Smallest sketch: subtract supported text/rules/images with provenance, nominate both on-rhythm and off-rhythm components, then ask A03/A11/A12 to form geometry. A gap is a question, not a line. Only residual area is refined. This approach owns **candidate nomination**, not three duplicate line-finding implementations.

**A07 — Render the local type system.** Known typographic alignment, proposed adaptive guide count and borrowing policy. R1 stacks compatible normal profiles into a family atlas with explicit guide supports; R2 checks sparse residuals before reuse. Verify **R07** enlarged exemplars with guide labels, component supports and measured/borrowed/unknown provenance, next to ours' guides. Smallest sketch: separate body-size/profile families, estimate only identifiable guides, and attach accent components without assuming six lines everywhere. Shared estimates make subsequent work cheaper. Greek/Arabic mixtures, capitals and tiny apparatus are deliberate counterexamples to universal x-height rules.

**A08 — Explain non-text ink without erasing embedded text.** Known motif/texture analysis; joint exclusion ownership is proposed. R1 renders picture direction fields, repeated motif crops and overlapping line support; R2 flags residual-rich, line-poor regions or repetition outside a text band. Verify **R08** local masks over the engraving/stamp/frame and captions, with unresolved overlaps visible. Smallest sketch: use a few region statistics, motif correspondences and optional ring/tall-initial witnesses to suppress *new speculative proposals*, then separately review any existing detector-line rejection. Repeated letters/digits and dotted leaders are counterexamples. Colour is documented as unavailable, not implemented as a dead experiment. Detail is computed only in nominated regions.

**A09 — Spend another inference where it restores information.** Known crop/multiscale inference; joint local unbend is Fable's addition. R1 outputs explicit crop/remap coordinates and corrected shapes; R2 uses samples-per-body-height or unresolved curve/ink evidence as a trigger. Verify **R09** input crop, optional unbend mesh, network map, remapped result and seam overlaps. Smallest sketch: compare scale-only, unbend-only and combined crops using the same requests; include a full-page larger-input comparator owned here alone. Cache and merge overlapping requests. A tiny source crop resized to a 960-long-side network input may cost almost a base pass; report actual tensor shapes and latency, not source-area optimism.

**A10 — Ink condition with a glyph-level referee.** Known stroke topology and width analysis; spatial pooling is F08's addition. R1 renders skeletons, distances, broken bridges/counters and a cautious local ink field. R2 samples line fragments using A07 family compatibility. Verify **R10** original pixels, multiple threshold renderings and explicit uncertain component groups; let the observer distinguish native bold type, detached accents, blur and damage. Smallest sketch: expose independent contrast/width/fragmentation axes and tentative broken/filled/unknown labels. Do not “repair” glyph pixels or infer unreadability automatically. A slow patch renderer can cost more than the detector because it is an offline referee; only witnessed patches enter the runtime branch.

**A11 — Use the learned map as a fast explicit line surface.** F16 plus established seam/graph methods; differs from A03 by reconstructing line topology over a nominated **region**, rather than fixing accepted individual bands. R1 uses ridge seeds and noncrossing paths over the map; R2 dispatches on unresolved merging/fragmentation. Verify **R03/R06** original ink and independent dense paths, not the same graph's own output. Smallest sketch: an isolated regional seam/graph variant, compared against A03 with identical requests. It can cheaply avoid raw-ink ghosts, but cannot find print whose map response is absent. No imports or edits to `greekocr/pages/`.

**A12 — Ask classical image evidence when the network is blind.** MSER/SWT are known literature additions to the threshold-stability dream. R1 displays stable regions, stroke rays and a component-neighbour graph; R2 uses cheap persistence/width summaries before full grouping. Verify **R05/R06/R10** against original-size residual crops, including accents and ghosts. Smallest sketch: in the *same* A06 request regions, ablate persistence, width and simple neighbour grouping; emit candidates for review without forcing acceptance. One bounded page-wide coarse diagnostic tests whole-block blindness. Its cost makes this an exception, not the clean-page path; a second printed verso layer is also stable text.

**A13 — Reuse book typography only when identity and compatibility exist.** Known adaptive priors/font retrieval; D11/F13 agreement. R1 is a book atlas of displayed exemplars; R2 compares current profile residuals before borrowing. Verify **R07** cross-page exemplars with true book IDs and reset reasons. Deferred sketch: if provenance establishes repeated volumes, use their dev pages only to compare independent-page estimates with compatible reuse and forced font-change resets; otherwise produce an explicit “no verified group” receipt. Rough cost in the table excludes training. Do not infer book identity from a filename prefix or apply one bend to a volume.

**A14 — Paired sides as an explicit transmission model.** Known recto/verso restoration, dreamed by both. R1 registers a mirrored paired side, estimates transmission and renders residuals; R2 sparse correlation can nominate confident regions. Verify **R11** side-by-side scans, registration vectors, overlap error and front-stroke preservation. Deferred sketch: first prove pairing from source provenance; then compare registered and deliberately misregistered fits on those dev inputs. With current evidence the appropriate output is “paired sides unverified”, not synthetic pairing presented as real. Never delete front support merely because it coincides with verso print.

**A15 — A stronger dewarp referee when the simple field fails.** Known physical/learned models from S04/S05. R1 renders their meshes; R2 may eventually approximate a verified mesh with a low-order coordinate fit. Verify **R04** forward/inverse correspondences on actual letters, separate leaves, and residuals independent of the mesh estimator. Deferred sketch: one source-pinned external adapter, run on unresolved curl cases, output both deformation and original-page line coordinates. The cheap dense geometric referee in round 1 is already built in shared code; do not rebuild it here. No training or universal learned correction is currently justified.

**A16 — Blind source and illumination models.** Known CRF/source separation/shadow models from S08/S09. R1 renders estimated front/back/background and reconstruction error; R2 would use sampled fits only after visual validation. Verify **R05** faint fronts, ghost-only areas and overlaps, always beside raw pixels. Deferred sketch: one small blind-model adapter on nominated ghost/shadow patches, compared to A05's same requests and labels. If a model removes real faint strokes, it fails regardless of improved-looking whiteness. Colour-separation variants are inapplicable to these grayscale inputs.

**A17 — Learned layout as a slow structural referee.** Literature addition, joined by coordinator C10's Docling handoff. R1 displays table/cell predictions; R2 limits a possible call to unresolved table regions. Verify **R02** original rules, blank cells and borderless alignments; compare the predicted graph to ink, not PDF text. Deferred sketch: one pinned TATR **or Docling/TableFormer** adapter on A02's unresolved dev tables (choose one, not two duplicate studies), writing cells and existing Paddle text assignments separately. Its extra model/dependency cost and domain transfer uncertainty put it behind classical barriers. Table success is not line recall.

**A18 — Independent baseline networks as references.** Known historical line methods. R1 displays their baselines and line envelopes; R2 could dispatch only on unresolved geometry. Verify **R03/R07** path-to-ink and guide support. Smallest sketch is **already available evidence**: import cached Kraken comparisons once in shared reference code. New-network inference is deferred; if ever needed, nominate the model and failure it resolves before running it on the same 54-page manifest. It must not become a consensus truth label. The existing Kraken cached median, 4.8612 s, is evidence against making that runner an unconditional correction.

**A19 — The handedness of print.** Coordinator C05's distinct proposal; known reflection-statistics neighbour S15, unvalidated mechanism for these pages. R1 would render compatible glyph/edge patches in original and mirrored form with spatial directional supports; R2 is the cheap 16-bin edge-direction signature, used only on unresolved weak/grid-ambiguous regions. Verify with **R14**, original-size glyph exemplars and their reflected edge fields; never let a scalar histogram certify ownership. Smallest deferred sketch: reuse Q6's 422-crop probe, add visually adjudicated comparable front/ghost crops on `s2-0ce9`, `s2-93f807`, `s2-09f5`, preserve pale `an-1be6`, and compare a spatial signature against the already-measured marginal one. Emit crop pairs and uncertainty masks, then a per-page status on all 54. Rough cost: 1–10 ms sampled, 20–200 ms local referee; not measured. Rank 13 because it is cheap and physically interesting, but text composition/font variability already confounds the preliminary distance. No new standalone round-1 prototype; later A19 would import A05/A07's compatibility and uncertainty rather than repeat them.

**P01 — Orientation from boxes, explicitly parked.** Coordinator C09 and known orientation analysis S16. R1 would display box-axis/character-direction evidence; R2 would summarise angles/aspects before a possible rotated rerun. Raw source and axis overlays would verify it by eye, but angle conventions and 180° ambiguity prevent treating tall boxes as proof. Hypothetical 1–5 ms scout plus inference if rerun; no measurement or correction attempted. The only round-1 action is the existing parked status for `s2-6419488b7f8e69fd20da-p00001`. A future sketch would compare axes with script-direction evidence only after the owner reopens orientation. This records the dream without violating scope.

**X01 — Make cost follow witnessed need.** The integration is an experimental design, not a published speed result. R1 is a visible ownership/uncertainty/work ledger; R2 is the cheap subset of its witnesses. Verify **R12** per-page trigger tiles beside a timing timeline, and inspect false-negative triggers against the dense offline references. Smallest sketch: baseline-only, each correction alone, and one staged composition using cached products; log exactly which work ran. High scores and zero boxes cannot certify a clean page. Always-on independent raw-image sampling must be tested for blind spots. An unresolved page is allowed a documented expensive branch or abstention.

**X02 — Make assumptions break visibly.** Known perturbation/stability ideas, independently proposed by Astra. R1 renders known synthetic fading, blur, gaps, thickening, curl and layout displacement on dev crops; R2 measures witness stability. Verify **R13** original/changed pixels, masks and exact coordinate fields. Smallest sketch: one shared deterministic set derived from visual dev exemplars, recorded once. Report synthetic results separately from real pages. Perturbing a line does not prove the label of an untouched faint line, and synthetic known geometry does not make ours ground truth. This is offline shared work, never per-page production overhead.

The renderer IDs are implemented/specified once in the [round-1 plan](FAST_LINES_ROUND1_PLAN.md). They are shared evidence products, not separate full models for every map entry.


## 7. Failure cases to expect

### Small detector failure modes to anticipate

1. **Wrong representation:** a good bent likelihood band becomes a quad; unclip merges neighbouring rows or includes ghosts; an accent lies outside the learned core. A01 can change geometry but cannot recover zero signal.
2. **Wrong topology:** a contour crosses a narrow gutter or merges successive lines. Ink coverage and high score can both look good (`an-a73d`). Small-box count is not line count.
3. **Insufficient sampling:** tiny cells, footnotes, accents and broken first letters disappear at long-side 960. Lowering a threshold cannot recreate lost spatial information (`an-d83e7`, `an-7a2b`).
4. **Domain/ownership confusion:** ornaments, mirrored print, stamps and watermark-like additions may be high-scoring text; real pale fronts can be lower-scoring (`s2-0ce9`, `an-1f8e`, `an-1be6`).
5. **Clipped evidence:** testing only inside accepted boxes hides missing curved ends (`s2-8686`) and whole omitted blocks. Empty output must escalate independently.
6. **Unmodelled typography:** scripts, display spacing, initials, detached marks and tables break one-height/one-baseline assumptions. Map density is neither body height nor readability.

### Approach-specific ways to fail, decided before prototypes

| Approach | Expected failure / concrete counterexample | Required response |
|---|---|---|
| A01 | Poly follows a joined contour through two lines; reduced unclip clips accents; threshold sweep trades ghosts for faint fronts. | Preserve contour genealogy and show omissions as unboxed raw crops; do not select by agreement with ours. |
| A02 | A heading spans a gutter; a dash/ditto mark looks like a rule; borderless cells lack separators (`an-a3c2`, `s2-8051`). | Block-local barriers, labelled uncertainty and unchanged spanning text. |
| A03 | A ridge hops to a neighbouring line or averages two peaks; bold capitals pull the path; accent islands mistaken for extra lines (`an-ffcc`). | Multi-path evidence, noncrossing checks, independent guide support or abstention. |
| A04 | One field mixes leaves, font-size changes or local folds; ghost lines form a stronger lattice; blank areas underconstrain it. | Per-leaf fit, support coverage, residuals, local fallback; never impose regular pitch globally. |
| A05 | Sharp show-through survives; defocused front text looks like ghosts; a watermark is sharp; paper estimate eats broad strokes. | Unknown ownership, original-pixel checks, no darkness/sharpness-only deletion. |
| A06 | Subtraction hides a genuinely missed line under an oversized accepted polygon; a fully absent block falls between scan samples; engraving floods candidates. | Use support as well as envelopes, coarse area coverage, image/rule evidence, remaining-residual review. |
| A07 | Accents/descenders are absent from the sample; multiple scripts share a band; borrowed family is wrong. | Output only supported guides, provenance and intervals; no manufactured baseline. |
| A08 | Hatching resembles text; repeated letters resemble ornament; captions and stamps overlap prose (`an-d600`, `an-7781`). | Ownership by actual support, preserve embedded text, uncertain overlap; no rectangular eraser. |
| A09 | Resizing every crop to 960 costs many passes; unbend interpolation destroys weak strokes; overlaps duplicate lines; more resolution finds ghosts. | Actual tensor/timing ledger, remapping receipt and deduplication; compare scale-only and no-change. |
| A10 | Native boldness resembles over-inking; accents resemble broken pieces; skeleton/holes vary with threshold and blur. | Family-conditioned axes, threshold witnesses and unknown readability; no automatic glyph restoration. |
| A11 | The map omits text or has a ghost ridge; seam continuity joins across whitespace or columns. | Same barriers as A02, independent raw residual scout; request A12/A09 or abstain. |
| A12 | Verso print is also stable and has coherent strokes; Greek accents split; touching ink merges characters. | Apply A05/A07 evidence, show the component graph, keep ownership uncertainty. |
| A13 | Wrong book identity or new font/scan condition propagates a bad prior. | Verified provenance and reset; current round has no valid cross-book experiment. |
| A14 | Incorrect pairing or elastic mismatch subtracts real front strokes; both sides overlap. | Registration uncertainty, reconstruction check and explicit front preservation; do not run without pairs. |
| A15 | Learned dewarp changes correct straight text, joins leaves or hallucinates plausible flattening. | Inspect original-coordinate correspondences, foldovers and endpoint support; keep reference status. |
| A16 | Source model explains weak front as back/background and whitens it away. | Compare local raw strokes and keep ambiguous pixels; cosmetic cleanliness is not success. |
| A17 | Modern-table prior misses historical leaders, splits spanning cells, or treats verse as a table. | Validate cells/rules by eye and leave current text geometry intact unless supported. |
| A18 | Baseline network follows picture structures or misses non-Latin print; agreement is correlated bias. | Keep cached output as a view, not labels; no vote-as-ground-truth. |
| A19 | Reflected and ordinary type have similar marginal gradients; italics, script and print wear change the signature; scan artefacts supply spurious direction. | Spatial glyph referee and family controls; Q6 probe is not a classifier; retain unknown ownership. |
| P01 | Tall upright characters/rules or 180° ambiguity are mistaken for page rotation. | Parked status only; no inferred rotation is applied. |
| X01 | A cheap trigger misses the very page needing work, or diagnostics secretly dominate latency. | Report missed triggers on all 53 upright pages and the always-on time separately. |
| X02 | Synthetic distortions are unrealistically easy or preserve clues absent in real degradation. | Separate synthetic/real conclusions and keep unchanged real counterexamples. |

Discounted lines must **never** be drawn on review images, including “rejected-lines” overlays. The audit may retain non-rendered IDs/reasons and show unannotated source crops to make a rejection inspectable. Orientation stays parked even when an external tool supports it.


## 8. Ranking and round-1 selection

I choose **12 approaches for round 1: A01–A12**, plus the shared X01 scheduler and X02 referee. Twelve is a cap on small distinct algorithms, not twelve independent end-to-end systems. They cover every charter feature, both requested routes, a shared-sheet versus local-path comparison, and one map-independent literature alternative. A13–A19 require missing inputs, another heavyweight model, or a second-stage justification; implementing them now would consume the budget before the fast hypotheses are tested. Cached A18 evidence and simple dense A15-style geometry are reused as shared references, not rebuilt as extra prototypes.

The ordering is judgement, not a score formula:

1. **A01 native contours/controls:** the map visibly contains some of the bend discarded by boxes. A free-of-new-inference change must be checked before a repair layer.
2. **A02 barriers/layout:** the clear `an-a73d` failure is invisible to residual ink. It also protects tables, images and every later grouping algorithm from cross-column errors.
3. **A03 local ribbons/endpoints:** directly attacks the two observed curl failures without requiring all lines to share a physical model; its explicit evidence can also verify shortcuts.
4. **A04 shared sheet/lattice:** independently dreamed and strongly supported by page physics, with real classical neighbours. Potentially cheaper across many lines, but vulnerable to false global regularity.
5. **A05 foreground ownership:** the 2,828 ink flags and `s2-09f5` make this essential before recovery is trusted. Sharpness must be tested against pale fronts, not assumed sufficient.
6. **A06 missing-line ledger:** closes the whole-block/endpoint blind spot; it depends on the preceding ownership/layout evidence to avoid replacing a competent small detector with ghost detection.
7. **A07 font guides:** central to the charter, and useful shared scale/provenance for nearly every correction. Geometry is useful without font naming; this deserves a real prototype even if line counts barely change.
8. **A08 pictures/motifs:** protects `an-d600` and ornament pages from the scout; the literature and Fable add a cheap repetition experiment. Ambiguous embedded text limits automatic suppression.
9. **A09 selective scale/unbend:** valuable where information truly disappears, but a second pass is an appreciable cost. It follows evidence of insufficient sampling, not habitual high-resolution inference.
10. **A10 ink condition:** explicitly covers a charter requirement the detector does not render. It is harder to validate and must not confuse weight with damage or diagnostics with readability.
11. **A11 map-first graph:** a compact regional fallback worth comparing with A03; it may prove redundant, which is a useful negative result. It must not become a second implementation of the entire current model.
12. **A12 stable-region/stroke graph:** the most useful independent classical challenge to map dependence. Limit its scope because it is also the easiest way to rediscover ghost print expensively.

Immediately below the selected twelve, **A19 is rank 13**: the coordinator's mirror cue adds a distinct physical question, but the unlabelled crop probe has not established reliable ownership. A13–A18 retain their IDs at ranks 14–19. Orientation P01 remains unranked and parked.

A13's priors may later save substantial time but cannot be honestly tested without identity; A14 lacks paired scans. A15/A16/A17 provide credible explicit reference alternatives if simple renderings remain ambiguous. A18 already has cached evidence and a demonstrated expensive runner. Round 2 should choose surviving mechanisms from **visual corrections, documented regressions and actual marginal cost**, and may combine fewer algorithms than round 1 explored. No Q6 result authorises API integration or a held-out evaluation.

The next run's executable specification is [FAST_LINES_ROUND1_PLAN.md](FAST_LINES_ROUND1_PLAN.md). It assigns every shared product, parameter study, reference rendering and output writer one owner so the 12 prototypes do not repeat the work.
