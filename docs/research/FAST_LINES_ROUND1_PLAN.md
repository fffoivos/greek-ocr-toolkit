# Fast lines — round-1 build plan

This is the build specification for one Astra run, following [Q6 research](FAST_LINES_RESEARCH.md) and the complete [owner's charter](../../.astra/fast_lines/CHARTER.md). Build **12 small prototypes, A01–A12**, once, using the shared components below. Build the shared evidence scheduler X01 and perturbation referee X02 once. A13–A19 remain mapped alternatives; do not build the seven deferred algorithms. The coordinator's orientation proposal P01 remains parked. No API integration, training, push, background jobs, or held-out access is part of this plan.

The research includes Astra's frozen independent dreams, Fable's, and the coordinator's later-arriving file. Coordinator contributions reuse the same prototypes: affine skew and competing grids in A04/A05, ring/initial cues in A08, and a joint page record in S4/S8. Mirror-signature A19 is rank 13 and deferred after a small Q6 ambiguity probe; do not repeat that probe in round 1.

The aim is viewable evidence about what works and why, including negative results. It is not to match our model's counts or reach a preselected latency claim. The old model is a skeleton for what can be rendered. Its lines, the other detectors and PDF text are not reference truth. The owner's descriptions remain authoritative and are not replaced by the terminology used to organise this plan.

## 1. Scope, receipts and completion

Use the worktree root and:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python <script>
```

Read only the 54 development PNGs enumerated from `.astra/pages/`; make an explicit content-hashed manifest and pass it to every command. Never import a helper that silently adds another dataset. `prototype/common.py` was read during Q6 but must not supply round-1 enumeration. Do not inspect or access the 44 held-out pages. Keep `s2-6419488b7f8e69fd20da-p00001` as an orientation-parked record: emit an unchanged result and status, exclude it from upright corrections and aggregates. All 54 still get an output/status row.

All image-dependent lengths are expressed in estimated letter/body heights or normalised page coordinates. A bootstrap box-height interval is allowed, explicitly labelled a proxy; `0.45 × box height` is not measured x-height. Uncertain height uses a small global multiscale range derived from page units, then updates from ink support. Network sampling controls (the supplied long-side 960 and stride 32), scalar probabilities, sample counts and machine tolerances are not page-specific geometric tuning. Record every conversion and quantisation. No page-name branches, crop coordinates encoded from a page, or per-page threshold constants.

Q6 checked: ONNX Runtime 1.31.0 exists in the repo venv; PaddleOCR/PaddleX packages do not. The supplied ONNXs are available. Build a minimal isolated, source-checked pre/postprocessing adapter; do not assume the old prototype can execute unmodified. Do not change the environment to mask a preprocessing mismatch. If a truly necessary optional dependency is unavailable, record it and use the native/reference fallback described below.

A prototype is complete when it has its README, a runnable command, a fixed globally specified configuration, 54 output/status records, viewable stages for its decisions, raw timing rows, and a short result stating observed improvements, regressions and unresolved cases. A negative experiment counts as completed if its evidence is inspectable. A missing implementation or an unrun experiment does not.

## 2. Tidy repository and output layout

```text
prototypes/fast_lines/
  README.md                     # exact commands, dependency DAG and results index
  run.py                        # manifest-driven experiment registry/orchestration
  experiments.json             # unique IDs, global configurations and ownership
  shared/
    README.md
    manifest.py                 # S0
    detector.py                 # S1
    image_evidence.py           # S2
    geometry.py                 # S3
    contracts.py                # S4
    references.py               # S5
    review.py                   # S6
    timing.py                   # S7
    scheduler.py                # S8
    perturbations.py            # S9
  native_contours/               # A01
  layout_barriers/               # A02
  local_ribbons/                 # A03
  sheet_lattice/                 # A04
  foreground_profiles/          # A05
  residual_ledger/               # A06
  font_guides/                   # A07
  image_motifs/                  # A08
  selective_rerun/               # A09
  ink_condition/                 # A10
  map_graph/                     # A11
  classical_residual/            # A12
    README.md                   # EACH approach folder has this and run.py
    run.py                      # algorithm only, imports shared components

.astra/fast_lines/out/           # ignored, outside tracked output
  shared/
    manifest.json
    cache/                      # content/config-addressed maps and primitives
    references/                 # one set of dense visual references
    adjudication.jsonl
    timings.jsonl
    experiments.jsonl
    perturbations/
    index.html                  # local static review index, no web service
  <approach>/
    README-results.md           # measured vs expected, command and receipt links
    <page>.json                 # detector-format view where meaningful
    <page>.evidence.json        # decisions, paths, support, status, provenance
    <page>_<n>_<stage>.jpg
    timing.jsonl               # references shared event IDs, does not rerun them
    index.html
```

Output directories use the folder names above. Do not create one-off copied helpers inside prototypes. The shared core should remain small; use arrays and native library operators rather than a framework or per-pixel Python. Add no production API dependency. Q6 scripts under `scripts/fast_lines/` are evidence utilities; do not repeat their contact sheets, cache audit, grayscale probe or 422-crop mirror-histogram study unless their inputs change.

## 3. Shared modules — each built once

Inputs and outputs below are explicit contracts, not permission to make all stages eager. Cache keys include image/model/source/config hashes, coordinate frame, dtype and scale. Changes invalidate the relevant product only. Read-only cached products can be shared across comparisons; latency accounting must distinguish reuse from a hypothetical fresh-page computation.

| ID / module and purpose | Inputs → outputs | Consumers | Explicit visual verification |
|---|---|---|---|
| **S0 manifest**: scope, identity, provenance | 54 PNGs, supplied cached records/model files/configs → exact allowlist, hashes, dimensions, source metadata, parked status, run environment | All | R01 raw page identity; a manifest gallery confirms each full name. Unknown book/pair IDs stay unknown. |
| **S1 detector**: one small-detector inference and replayable postprocess | Image/crop, ONNX hash, declared preprocessing and postprocess config → float map, tensor shape, all coordinate transforms, raw/accepted contours, boxes, scores and rejection genealogy | All; A01 owns control studies, A09 owns new inference shapes | R01 map/contours on original pixels; compare supplied default boxes without treating them as truth. |
| **S2 image_evidence**: lazy pyramid and physical primitives | Raw page, requested scale/ROI, height interval → paper estimate, normalised contrast, gradients, edge profiles, threshold masks, run lengths, components and optional distance/skeleton arrays | A02/03/05/06/07/08/10/12; A04 anchors; A09 triggers | R05 photometry and R10 stroke tiles; raw pixels remain alongside every transformed view. |
| **S3 geometry**: coordinates and reusable mathematical operations | Maps/strips, sparse anchors, height intervals, candidate paths → reversible mappings, profiles, correlation/pitch measurements, robust fit operators, contour-to-ribbon and support sampling | A01–A04, A06/07/09/11/12 | R03 dense anchors/path support, R04 mesh residuals, R09 remap receipt. No baseline inferred merely from a density centre. |
| **S4 contracts**: shared data types and evidence ownership | Product records → `RegionRequest`, `LineEvidence`, `LayoutEvidence`, `FamilyProfile`, `Decision`, dependency IDs; merge/dedup request operations; a joint per-page record linking leaf/skew/curl/grid/table/type evidence | All | R02/R06 ownership layers and provenance labels; inspect overlaps rather than silently raster-erasing them. |
| **S5 references**: slow explicit renderers and existing guide imports | Raw pages, union of diagnostic ROIs, nondiscounted ours, cached Kraken/other detectors, independent dense measurements → R01–R13 products described below | All, once per unique request/config | The owner or Astra checks the original pixels and visible supports. Renderer disagreement creates an unknown label, never automatic truth. |
| **S6 review**: one writer, gallery and adjudication format | Non-discounted results, evidence, reference/timing IDs → stage images, detector JSON, HTML links, evidence records | All | Inspect clean, curved, faint, image and table examples at full resolution; assert no discounted IDs reach drawing functions. |
| **S7 timing**: one measurement/receipt harness | Registered operation calls and cache context → raw event times, tensor/ROI sizes, touched pixels, warm/cold metadata, per-page totals and summaries | All | R12 timeline labels and checks that displayed work matches charged operations. |
| **S8 scheduler**: X01's lazy dependency/trigger ledger | Cheap witnesses plus unresolved requests → deterministic work queue, dedup requests, no-change/abstain/correction status | Composition of A01–A12 | R12 trigger maps against dense offline references; empty-output and whole-block blindness probes. |
| **S9 perturbations**: X02's one offline falsification set | Selected dev exemplar crops, globally defined changes/seeds → altered pixels, exact displacement/damage masks, unchanged controls | Witness checks for A01–A12 | R13 original/changed pairs and known mapping; report synthetic findings separately. |

**Algorithm ownership matters.** S2 supplies operators, not a second foreground classifier. A05 owns the ownership decision; A08 owns image/motif decisions; A10 owns ink-condition inference. S3 supplies sampling/fitting operators, not three line detectors: A03 owns local paths, A04 owns the shared-sheet fit, A11 owns regional map topology. A02 owns the barrier graph. A07 owns family/guide estimation. Their immutable results flow through S4. The slow references use dense independent support and raw pixels, not merely the same estimator with prettier colours.

**Important contracts:** a `LineEvidence` contains page-coordinate polygon, optional supported baseline, optional centreline kept under its own name, height estimate/interval, guide arrays, source IDs, measured/borrowed/unknown provenance and evidence diagnostics. A `RegionRequest` contains purpose, geometry, derivation, uncertainty and dependency IDs. Do not ask another prototype to crop by a page name. A discarded result may remain in a machine ledger but is never drawn.

## 4. Explicit references and the eye-check protocol

Build these as views from five shared cores: detector genealogy; geometry/profile rendering; ink/ownership rendering; original-guide/cached-detector import; and work/perturbation receipts. They are not thirteen new detection systems.

| Reference | Explicit product | What the observer checks / who uses it |
|---|---|---|
| **R01 detector genealogy** | Raw page, float map, initial/accepted contours, unclip and final representation | Does shape follow real ink; at which step is an end/line lost? A01 and all comparisons. |
| **R02 layout** | Coarse/full corridor masks, rules/intersections, leaf/block and provisional cell boundaries | Genuine sustained gutters, spanning headings, broken rules, captions. A02/06/08; future A17. |
| **R03 line strips** | Enlarged raw strips; slow dense ridge/edge support; independently fitted paths; old guides/cached baselines separately | Does a path follow the same row all the way out, and do accents/descenders belong to it? A03/04/07/11/12. |
| **R04 sheet** | Independent dense line anchors, displacement mesh, residual arrows, two-leaf distinction | Shared physical bend versus a bad regularity assumption. A04/09; future A15. |
| **R05 photometry** | Paper, contrast, edge spread, threshold persistence, foreground/ghost/unknown exemplars | Preserve faint front, avoid sharp-ghost certainty, expose paper-estimate errors. A05/06/12; future A14/16. |
| **R06 residual ledger** | Actual supported ink versus envelope, rules/images separately, unowned ink and nominations | Does subtraction hide misses; do new tracks correspond to visible text; what remains unexplained? A06/11/12. |
| **R07 typography** | Aligned family exemplars, candidate guide modes, components supporting each guide, provenance | Font/size mixing, scripts, detached marks, unidentified guides. A07/03/10; future A13/18. |
| **R08 images/motifs** | Directions, region ownership, corresponding repeated crops, embedded lettering | Does a veto erase caption/prose; is repetition typographic or decorative? A08. |
| **R09 crop/remap** | Input crop, optional unbend grid, tensor size/map, inverse coordinates and overlap ownership | Distortion/interpolation, seam duplication, more ghost detection. A09. |
| **R10 ink grammar** | Original-size patches with width/distance/skeleton/counter/fragment overlays at multiple thresholds | Broken versus disconnected accents, filled versus native bold, damage versus blur; readability may remain unknown. A10/12. |
| **R11 duplex** | Future paired-side registration and source reconstruction | **Interface only in round 1:** no verified pairs, no registration experiment. A14 deferred. |
| **R12 work ledger** | Trigger coverage, unresolved reasons and operation timeline | A clean page actually skipped detail; false-negative triggers did not disappear from the report. X01/all. |
| **R13 perturbations** | Changed pixels and exact synthetic geometry/damage masks | The alteration is physically plausible and the witness reacts for the expected reason. X02/all. |
| **R14 mirror evidence** | Future original/reflected glyph and spatial edge views | **Deferred interface only:** Q6 histogram distances are not labels; a spatial referee is required if A19 is later built. |

Start visual verification on the named challenge pages below **and the clean controls**; then review every changed region, every rejected candidate via an unannotated source crop, and the page-wide contact sheet on all 53 upright pages. Review remaining unexplained areas, not just successful corrections. Never draw a discounted line, even red or dashed. An uncertain, still-retained proposal may be labelled as such; once discounted its geometry disappears from all review overlays.

For each inspected event, record page, raw crop coordinates, source product IDs, feature, G/M/F, previous/proposed state, observer (`Astra` or owner), and verdict (`supported`, `regression`, `ambiguous`, `not checked`). Support is a visual judgement, not an official ground-truth annotation. Report raw event counts and all regressions; do not present partial inspection as page-wide precision/recall. Do not infer owner approval from Astra's review.

Use existing `ours_lines` fields (guides, `xheight`, `column`, `support`, `geometry_source`, `borrowed`, `contrast`, `ink_classes`, residuals) to display the old model's hypothesis and provenance. Never copy its decision as the label. Import cached nine-detector records once; remember docTR/CRAFT units are words. No new baseline network is required for round 1.

## 5. Experimental order and the clean-page budget

Build in this order; promise ranking is not dependency order:

1. **Freeze scope and baseline.** S0/S1/S6/S7, then the common evidence contracts. Confirm preprocessing/coordinate parity, save one float map per page, and expose both contours and boxes. Do not continue comparisons on a misnormalised map. Render the baseline including clean controls.
2. **Build reference views from requested evidence.** Implement S2/S3/S5 incrementally, reusing the same arrays. Inspect original-sized samples before trusting a fast witness. Start with A01/A02/A03/A04; these expose geometry and layout assumptions.
3. **Build physical/typographic evidence.** A05/A07/A08/A10, using one shared primitive cache. They do not need a finished missing-line detector to render useful evidence.
4. **Build the common residual request set.** A06 produces it from the frozen baseline and those evidence products, including one coarse independent raw-image coverage pass. Save it. A11/A12 and A09 consume the same requests where their question applies.
5. **Build all remaining algorithms and compare alone.** Each A01–A12 gets one registered fixed-input diagnostic run on the manifest. No-change pages receive a status and common-stage links, not needless repeated expensive renderings.
6. **Test lazy composition and falsify the shortcuts.** S8 plus S9, using already-produced products for diagnostic comparisons. Run one fresh-path composed timing pass to measure actual paid work. Inspect interactions, especially A05→A06 and A02→A03/A11, and any regressions on clean pages.

Always-on work is a hypothesis to minimise: metadata/box checks, very coarse map projections/barrier cues, sparse raw-image support across the page and a few endpoint/profile checks. Full-resolution binarisation, full-page connected components, glyph skeletons, dense paths and review rendering must be lazy. Sparse coverage can miss small text; test this explicitly and report the accuracy/cost tradeoff. Empty detector output asks for a broader independent image check. It is not a cheap-page certificate.

The aspirational 2–10 ms shared overhead is **not an acceptance claim**. Measure current base inference anew. Print the clean-control ratio `(base + mandatory scout) / base`, absolute extra milliseconds and any false-negative triggers. A near-base time obtained by overlooking errors fails the intended design. Expensive pages may honestly cost much more.

## 6. Plan per prototype

Each folder README must contain the hypothesis, commands, dependencies, global configuration, expected failure, evidence links, actual findings and next decision. The steps below are deliberately small and informative. Page prefixes resolve to full names in the research ledger; they are review selections, never runtime conditionals. Every algorithm still receives the same 54-page manifest.

### A01 — `native_contours` (rank 1)

**Show:** whether existing map geometry and documented controls already correct bands. **Prediction:** polygons improve some left bend on `s2-3229`; reducing expansion can reduce overlap, but neither restores missing right-end response on `s2-8686` nor necessarily splits `an-a73d`. Lower thresholds risk ghosts on `s2-0ce9` and ornament on `an-1f8e`.

1. Record the source-pinned DB defaults/config and replay baseline quad/poly on one saved float map per page. This identifies representation losses without a second network pass.
2. Run one global compact study: baseline quad, baseline poly, and lower/higher map threshold, box-score threshold and expansion around the recorded baseline poly (eight configurations total). Values are fixed globally before results; constrain probabilities to valid ranges. Inspect dilation and score-mode support; add at most one justified paired ablation, recorded in the registry, if rejection genealogy implicates it. No Cartesian sweep.
3. Inspect end/accent/merge and rejection changes; freeze a documented candidate config or conclude native controls are insufficient. Emit variant results and genealogy, preserving regression cases.

**Shared:** S0/S1/S3–S7; **reference/output:** R01 plus original-size crops, quad/poly detector JSON and stage images. **Owns:** E01, all fixed-map DB control sweeps. Input-size experiments belong solely to A09.

### A02 — `layout_barriers` (rank 2)

**Show:** a fast explicit representation of leaves, columns, rules and cell constraints. **Prediction:** `an-a73d` cross-gutter boxes split despite zero residual-ink flags. `an-c8b9` needs four text columns on two leaves; `s2-200e` and `an-7a2b` expose rule/cell grouping, while `an-a3c2` and centred headings resist blind splitting.

1. Render coarse whitespace persistence, long runs and candidate separators once. This separates an actual gutter from a single word gap or a dash.
2. Build block-local barrier/cell graphs and mark crossed Paddle bands; nominate full-resolution checks only there. This tests whether the cheap graph can stand in for explicit ink/rule inspection.
3. Split only supported crossings, keep spanning text and uncertain cells, and publish assignments and failures. Inside a supported table region preserve small-detector cell boxes by default: no prose-slot filling, cross-cell merging or shared curl fit. A real cell-text error needs its own explicit evidence. This establishes barriers reusable by all later line graphs; it does not require a Docling call.

**Shared:** S0–S7; **reference/output:** R02 mask/graph stages, split-line JSON, uncertainty ledger. **Owns:** E02 barrier/rule experiments; no duplicate table detector in another folder.

### A03 — `local_ribbons` (rank 3)

**Show:** local curved paths, multi-ridge checks and endpoint completion beyond accepted boxes. **Prediction:** `s2-3229` and `s2-8686` need endpoint/path changes; `an-ffcc` exposes script/diacritic attachment; `s2-77d1` should remain unchanged and avoid dense tracing.

1. Sample sparse normal profiles inside and beyond ends in body-height units. This tests whether the current in-box curve test's blind spot is visible cheaply.
2. Trace only nominated strips using multiple ridge hypotheses and continuity, respecting A02 barriers. Compare against dense R03 measurements. This tests real geometry rather than mean-density movement.
3. Fit a small ribbon and attach supported guides/accents through A07's outputs. Publish measured versus uncertain endpoints and record any neighbour jumps.

**Shared:** S0–S7, A02 barriers, optional A07 profiles; **reference/output:** R03 support tiles and polylines; baseline stays null if only a centreline is identified. **Owns:** E03 local path variants. No full-region graph or independent guide estimator here.

### A04 — `sheet_lattice` (rank 4)

**Show:** shared per-leaf displacement, local pitch/phase and cheap box audits. **Prediction:** coherent left bend on `s2-3229` reduces repeated per-line fitting; `s2-8686` tests whether fragments suffice for a shared field; `an-d83e7` defeats a single pitch across sizes; `an-c8b9` defeats a single sheet across the spread.

1. Compute robust box-tilt initialisers, strip correlations, anchor supports and multiple pitch candidates using S3. Render phase ambiguity and alternative grid membership for A05, retaining different physical leaves/blocks. This tests F01/F02 directly without assuming a regular page.
2. Fit separate affine-plus-smooth leaf fields; compare sparse fit against the independently dense R04 support. This tests whether sheet physics predicts held-back anchors **within dev pages**, not held-out pages.
3. Transport paths, report residuals and dispatch local failures to A03. Compare one shared field to A03 on the same geometry requests, reusing its results. This measures marginal cost and structural failure, not two duplicated benchmarks.

**Shared:** S0–S7, A02 leaf blocks; **reference/output:** R04 mesh/residual stages, transformed JSON and pitch/phase strips. **Owns:** E04 field/lattice fit. Full external dewarper adapters remain deferred A15.

### A05 — `foreground_profiles` (rank 5)

**Show:** foreground/ghost/unknown evidence separate from darkness. **Prediction:** `s2-09f5` should lose many scout nominations without deleting the right body; `s2-0ce9` challenges sharp ghost rejection; `an-1be6` must retain weak front print; `an-ef48` exposes a poor paper estimate.

1. Render contrast, edge spread and threshold-persistence profiles from shared S2 on nominated regions and matched credible front samples. This makes the physical hypothesis inspectable.
2. Compare contrast-only, normalised edge and combined witnesses using the same samples. Reuse A04's competing pitch/phase/skew grids as coordinator C04's additional explicit witness; display memberships on `s2-0ce9` and `s2-93f807`. This tests whether sharpness or a second grid adds separation. A dominant grid is not automatically front, and in-register verso defeats the cue.
3. Assign cautious ownership/unknown outputs and test sparse versus dense agreement. Retain overlap ambiguity; report preserved/lost pale fronts explicitly.

**Shared:** S0–S7, A07 compatibility when available; **reference/output:** R05 tiles, ownership masks and decision records, optional retained-line JSON. **Owns:** E05 foreground witness study. No source-layer restoration or separate threshold sweep elsewhere.

### A06 — `residual_ledger` (rank 6)

**Show:** useful missing-text nominations without flooding the page with ghost/picture candidates. **Prediction:** `an-fd4fa` lower continuation, `s2-4959` first-word areas and `an-5c09` marginal/running-head cases nominate plausible misses; `s2-09f5` and `an-d600` must shrink the flood. `an-a73d` must still be handled by A02, not claimed as a residual success.

1. Render actual unexplained support separately from envelope subtraction using the shared baseline and physical/layout evidence. This reveals whether oversized boxes conceal omissions.
2. Add a page-wide coarse image scout and both rhythm-gap and off-rhythm requests. This tests whole-block and margin blindness. No rhythm slot becomes a line without ink.
3. Save one frozen `RegionRequest` set with nomination reasons; ask A03/A11/A12/A09 for geometry where relevant. Compare raw candidate counts, visually supported cases, false alarms and unexplained remainder to the supplied stage scout, without treating its 102 disagreements as labels.

**Shared:** S0–S8, A02/A05/A07/A08 products; **reference/output:** R06 ownership/residual stages and request JSON, retained recovered lines after review. **Owns:** E06 request nomination and fixed request corpus used by the other fallbacks.

### A07 — `font_guides` (rank 7)

**Show:** compatible local type families, letter-height intervals, supported guides and honest borrowing. **Prediction:** `an-ffcc` needs separate script/profile treatment; `an-d83e7` separates large verse and tiny apparatus; `an-e745` needs local family changes; `an-1f8e` display spacing must not dictate body spacing.

1. Build exemplar groups using body profiles, scale and spacing from a few credible lines; show the grouped crops. This tests compatibility without font recognition.
2. Stack aligned profiles and estimate only supported body/baseline/extent/accent modes, comparing to R07 and ours' displayed hypotheses. This tests an adaptive guide count against a fixed six-guide assumption.
3. Borrow within a compatible block, recording residual checks, reset and unknown cases. This measures whether sharing saves work without propagating a wrong font/guide estimate.

**Shared:** S0–S7; **reference/output:** R07 exemplar atlas, guide overlay stages and evidence JSON; line JSON only for supported geometry. **Owns:** E07 all body/guide/spacing estimation. No independent x-height algorithm in other prototypes; book identity work is deferred A13.

### A08 — `image_motifs` (rank 8)

**Show:** image/frame/motif ownership that protects text. **Prediction:** `an-d600` engraving stops driving speculative line recovery while vignette lettering stays inspectable; `an-1f8e` repeated border separates from display title; stamp overlaps in `an-7781` resist rectangular suppression; leaders in `s2-200e` remain structural evidence.

1. Render coarse directional support and candidate repeated crops in residual-rich regions. This tests text-band versus area texture without a deep image model.
2. Compute regional motif similarity/autocorrelation, boundary and optional ring/tall-initial evidence only when triggered. This tests F11's addition against repeated characters/digits and semantic marks.
3. Publish region ownership and suppress unsupported new proposals; separately adjudicate any existing line rejection. This measures false-positive reduction and protected embedded text.

**Shared:** S0–S7, A02/A05/A07; **reference/output:** R08 repeated crop pairs, ownership stages, retained-line JSON. **Owns:** E08 picture/motif study. No colour experiment: Q6 measured 54/54 grayscale pages.

### A09 — `selective_rerun` (rank 9)

**Show:** whether the cost of another inference restores genuinely missing information. **Prediction:** tiny cells/apparatus on `an-7a2b`/`an-d83e7` may improve with sampling; `s2-8686` may benefit from scale/unbend; `s2-0ce9` may gain undesirable ghosts. Clean controls should issue zero crop requests.

1. Use shared height/map-resolution uncertainty to merge crop requests. Run **one full-page larger-input comparator** per upright page at a single globally chosen scale factor, cached here alone. This distinguishes resolution limitations from crop-context effects; it is offline diagnostic cost, not the clean runtime path.
2. On frozen relevant requests compare scale-only, unbend-only and combined reruns with identical remap code. This separates information gain from coordinate flattening; charge actual tensor sizes and every call.
3. Deduplicate at seams with S4 and expose conflicting ownership. Compare benefits, crop area, number of calls and latency against the same baseline; publish cases where doing nothing wins.

**Shared:** S0–S8, A02/A04/A06/A07; **reference/output:** R09, map-before/after stages and remapped detector JSON. **Owns:** E09 every input-size/crop/unbend neural experiment. Do not add local threshold tuning; use A01's recorded configurations.

### A10 — `ink_condition` (rank 10)

**Show:** ink-condition evidence distinct from faintness and font weight. **Prediction:** `s2-8686` yields useful damaged/dense stroke examples; `an-3352`/`an-ef48` expose noise and fragmentation; bold/display material in `an-1f8e` is a counterexample to declaring all thick strokes over-inked. Actual unreadability is unresolved until original-size review.

1. Select representative suspect component groups using existing evidence, then render width, skeleton endpoints, counters and threshold variants from S2. This tests whether the proposed grammar is visible at all.
2. Compare local family-conditioned samples to dense R10 patches and a smooth condition field with explicit local exceptions. This tests F08 without assuming page-wide uniform damage.
3. Emit independent contrast/width/fragmentation axes and broken/filled/unknown hypotheses; obtain visual verdicts. Do not synthesise repaired glyphs or turn a heuristic into a definitive readability label.

**Shared:** S0–S7, A05/A07; **reference/output:** R10 original-size patch sheets and condition overlays on retained lines. **Owns:** E10 stroke/condition study. A12 imports the same width/persistence products.

### A11 — `map_graph` (rank 11)

**Show:** a regional map-only topology fallback, distinct from local ribbon correction. **Prediction:** map-present fragments on `s2-3229`/`s2-4959` may join without raw-ink noise; absent tiny-map response on `an-d83e7` cannot be restored; `an-a73d` requires imported barriers to prevent the same crossing.

1. Reuse A06's region requests, map ridges and barriers; build a minimal noncrossing seam/line graph. This tests regional grouping without reimplementing our full model.
2. Compare to A03 on exactly the same relevant regions and R03/R06 references. This identifies complementary wins versus redundancy.
3. Publish only supported paths plus unresolved map-blind requests routed to A12/A09. Negative or redundant results are retained in the final comparison.

**Shared:** S0–S7, A02/A06/A07; **reference/output:** R03/R06 graph/path stages and line JSON. **Owns:** E11 regional map topology. No new map run, threshold sweep or independent benchmark set.

### A12 — `classical_residual` (rank 12)

**Show:** a bounded map-independent fallback from stable intensity regions and stroke-supported grouping. **Prediction:** some faint/map-weak fronts in `an-1be6`/`s2-4959` may be nominated independently; `s2-09f5`/`s2-0ce9` will demonstrate that stable, coherent strokes also describe ghosts; `an-ffcc` challenges component-to-glyph assumptions.

1. In the same frozen A06 regions, construct intensity-stable components and reuse stroke-width features; show them without premature acceptance. This tests whether independent evidence exists where the map is weak.
2. Add a simple normalised neighbour graph constrained by A02/A07 and compare persistence-only versus persistence-plus-width. This tests the classical literature addition with one shared implementation of each primitive.
3. Run one coarse full-page diagnostic with that same algorithm on each upright page to expose completely absent blocks. Compare the triggered version against this offline view and cost it separately. Keep wrong ghost nominations and unresolved ownership visible.

**Shared:** S0–S7, A02/A05/A06/A07/A10; **reference/output:** R05/R06/R10 component/stroke/graph stages and reviewed line JSON. **Owns:** E12 classical grouping. This is the bounded twelfth experiment, not permission for a new global production detector.

## 7. Duplicate-experiment check and unique ownership

The registry must refuse a second execution of the same input/config/source tuple unless the first failed or a deliberate timing repeat is requested. Record cache hits separately. Execution reuse does not imply runtime is free on a fresh page.

| Experiment/product that could be duplicated | Sole owner | Other consumers / rule |
|---|---|---|
| Baseline inference, RGB/normalisation/resize parity, float map and transforms | **E00 S1**, once per image/model/input configuration | Every prototype imports. Do not recover numeric maps from JPEG stage images. |
| Quad/poly, thresholds, unclip, optional dilation/score ablation | **E01 A01** | A03/A04/A06/A09/A11 reuse; no local “better threshold” sweeps. |
| Gutters, leaves, runs, rules and cells | **E02 A02**, S2 primitives | All grouping and exclusion methods share one barrier graph. |
| Local strip/ribbon/end walk | **E03 A03**, S3 operators | A04 compares to saved A03 paths; A06 consumes them. |
| Shared field/pitch/phase and sparse-versus-dense comparison | **E04 A04** | A09 imports the field, never fits a second dewarp. |
| Background/contrast/edge/persistence primitive images | **S2 cache**, requests owned by E05 | A05/A08/A10/A12 share masks/arrays; globally specified variants only. |
| Front/ghost witness comparisons | **E05 A05** | A06/A08/A10/A12 consume labels/evidence; do not independently relabel ghosts. |
| Residual candidates and fallback request corpus | **E06 A06** | A03/A09/A11/A12 compare on the same requests. Log any algorithm-specific eligibility filter. |
| Letter height, guides, family compatibility, spacing | **E07 A07** | Everyone imports profile evidence; bootstrap proxy remains explicitly provisional. |
| Picture/stamp/repetition experiments | **E08 A08** | A06 imports ownership; A02 still owns rules. No saturation experiment on grayscale. |
| Full-page larger-input comparison, crop selection, scale/unbend reruns and neural timing | **E09 A09 through S1** | Everyone reuses results; neither A01 nor A04 runs a second resolution study. |
| Skeleton, width, counters and ink-condition sampling | **E10 A10 through S2** | A12 reuses primitives; photometric contrast stays E05. |
| Regional learned-map graph | **E11 A11** | A06 nominates, A11 groups; no second implementation in A06. |
| Stable-region/neighbour graph and full-page classical diagnostic | **E12 A12** | A06 uses requests/results; no parallel generic binarisation detector. |
| Dense reference paths, sheets, profiles and glyph patches; cached ours/Kraken/nine-detector views | **ER S5**, union of requested ROIs | One renderer/cache; all claims reference its IDs. No new Kraken inference. |
| Mirror-direction histogram ambiguity probe | **Q6 `probe_mirror_histograms.py`**, already run | A19 is deferred; reuse its 422-crop receipt, do not repeat a mirror study inside A05. |
| Physical perturbations and unchanged controls | **EP S9**, one seeded set | All witnesses evaluated once per unique variant; synthetic and real counts separate. |
| Output writing/discount filtering, adjudication and gallery | **S6** | No custom overlay writers hiding different subsets. |
| Timing repeats, control pages, triggered-versus-dense composition | **ET S7/S8** | One orchestrated benchmark; prototypes cite event IDs, not repeated inference for reporting. |

Start with standalone diagnostic outputs on the common baseline. For composition, run one explicit topological chain: A01 → A02 → A07/A05/A08 evidence → A03/A04 conditional geometry → A06 requests → eligible A09/A10/A11/A12 branches. A10's cheap features may already exist; request expensive glyph detail only where needed. Avoid running competing A03/A04/A11 repairs sequentially and reporting the last one as a combined gain: preserve variant IDs, compare them, then choose a deterministic evidence-based dispatch. Re-adjudicate any region changed by composition.

## 8. Timing, presentation and the round-2 handoff

Time model startup separately; warm the model once with a dev input and label that call. For **E00 and the final composed path**, collect three timed warm repetitions per upright page in a fixed seeded order, with fixed thread settings and no competing background job. These are intentional harness repeats, not independently repeated experiments. Save all raw values, not just a best time. For exploratory variants, a single diagnostic timing suffices until a new uncertainty justifies repetitions. Include tensor dimensions, map size, ROI area, component/line counts and cache status.

Separate decode, preprocessing, inference, detector postprocessing, mandatory scout, each activated correction, and review/JSON/image writing. Report both compute-from-decoded-page and end-to-end wall time; avoid hiding cache materialisation or repeated map resizing. Give per-page raw rows, p50/p95, cold/warm and clean/challenging groups, and explain observed outliers. Do not add medians of separate stages and call that median total latency. The historical stage numbers in Q6 are context only.

Each prototype's visual sequence should reuse the supplied stage style: (1) original; (2) relevant explicit evidence; (3) baseline result; (4) trigger/request/uncertainty; (5) reference/support detail; (6) proposed retained result; (7) side-by-side result plus provenance/cost. Shared stages are linked, not regenerated. Provide original-resolution crop links for decisions that a thumbnail cannot resolve.

Detector-format JSON uses `items` with `polygon`, `baseline`, `score`, page identity and dimensions. Keep page-coordinate transforms explicit. Carry an inherited detector score with its source; it is not a newly calibrated correction confidence. A new candidate with no comparable score uses null plus an evidence record; verify local viewer compatibility once. If it cannot display null, use the image gallery for that candidate rather than inventing a numeric probability. Similarly, do not label a centreline as a baseline merely to satisfy the viewer. No changes to the comparison app or page API are required by this plan.

Round-1's handoff should link all 12 results, the shared gallery, raw timing/decision records and the exact manifest/config/source hashes. For each charter feature and each error type, say what improved, what regressed, what remains ambiguous, and which explicit rendering supports that statement. Show cheap-page overhead and false-negative triggers together. Recommend a small surviving combination for round 2, explaining why discarded approaches failed or duplicated another's contribution. Record deferred A13–A19 and their missing evidence rather than silently forgetting them. Do not access held-out pages or claim readiness for production from the 54 development pages.
