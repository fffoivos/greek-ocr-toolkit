# Q7 — Fast line finding: round-1 results

Status: **PARTIAL**. All twelve approaches have runnable prototypes and 174 output/status records, but several planned substeps and exhaustive visual validation remain unfinished. No production API integration or held-out evaluation.

The strongest concrete follow-up is an explicit separator model. The current local ribbon path damages a clean control; ownership and missing-text decisions remain unresolved. Fast timing does not rescue those failures.

The complete [owner charter](../../.astra/fast_lines/CHARTER.md), including the owner's own words, remains authoritative. In particular:

> a good result we could see is something like: for pages where small detector has no errors we add negligable overhead, and for pages where it needs fixes we have sub 1 second corrections.

## Scope and receipts

54 development pages + 80 selected disagreement pages (25 geometry, 25 missed lines, 20 false-positive candidates, 10 tables) + 40 supplied agreement controls = **174**. The sideways development page is unchanged and excluded from all upright aggregates: **173 upright**. The 220 agreement-pool figure describes the source population; it is not the number of supplied controls. Agreement between detectors is not verified absence of errors. All 174 supplied PNGs are grayscale. The 44 held-out pages were never opened or enumerated.

Outputs: [all galleries](../../.astra/fast_lines/out/shared/index.html), [manifest](../../.astra/fast_lines/out/shared/manifest.json), [registry](../../.astra/fast_lines/out/shared/registry/experiments.jsonl), [visual verdicts](../../.astra/fast_lines/out/shared/adjudication.jsonl), [all failures and unknowns](../../.astra/fast_lines/out/shared/failures_and_unknowns.json), [artifact validation](../../.astra/fast_lines/out/shared/validation.json). Code and exact commands: [prototype index](../../prototypes/fast_lines/README.md). Outputs remain outside git.

The ONNX adapter reuses content-pinned installed [PaddleX DB source](https://github.com/PaddlePaddle/PaddleX/blob/develop/paddlex/inference/models/text_detection/processors.py) and the model configuration: map threshold 0.2, score threshold 0.45, expansion 1.4, max 3000 contours; long side 960 and stride 32. [Source/config receipt](../../prototypes/fast_lines/shared/detector_source.json). CPUExecutionProvider, one ONNX/OpenCV thread. No environment installation. Against the older native-Paddle cache, line counts match 51/54 development records; three have one additional ONNX item. This is not bit-for-bit native-Paddle parity. The ordered-vertex comparison is also not an accuracy metric.

## Explicit evidence before fast checks

The first dense raw-ink referee used independent column maxima and visibly jumped rows even on `s2-77d1bd63d5babbe0df73-p00001`. Its 174-page artifacts are preserved in `shared/references-v1`. Before heuristic execution, v2 adds a letter-height search window, weak centre prior and continuity on raw contrast; it was visually checked on the clean control and curled `s2-3229200bf47ca465a42d-p00004`. Both are hypotheses, never labels. V2 still leaves difficult endpoints unresolved.

Every baseline line has an original-pixel crop beside its dense support, plus page photometry and original-size stroke panels. Each approach has per-page evidence and a `per_line_comparison.json` containing independent raw-support containment for every baseline line. Low containment is a review flag, **not** a false-negative label. All discounted old lines are excluded. New, still-retained unknown candidates may be drawn; no centre path is renamed a baseline.

## Measured timing and the owner target

The following are **marginal algorithm/study seconds** after saved shared dependencies and S2 primitives, one diagnostic timing per page. A01 shows the poly replay (including genealogy); A09/A12 exclude their separately logged full-page comparator. They are **diagnostic costs, not fresh-page added latency**: dependencies are reused, while some studies include competing variants or genealogy that a runtime would not all execute. They cannot establish the negligible-overhead target. Raw page timings include decode, primitive build cost/cache state, study, offline comparator and review I/O. No medians were added to form a total.

| Prototype | Agreement p50 / p95 / max (s) | Discrepancy p50 / p95 / max (s) | Discrepancy pages ≥1 s |
|---|---:|---:|---:|
| native_contours | 0.003890 / 0.013349 / 0.015081 | 0.006486 / 0.021563 / 0.027141 | 0/80 |
| layout_barriers | 0.229653 / 0.868470 / 0.962457 | 0.184013 / 0.588554 / 0.830997 | 0/80 |
| local_ribbons | 0.032092 / 0.083930 / 0.095363 | 0.051827 / 0.200070 / 0.253840 | 0/80 |
| sheet_lattice | 0.013574 / 0.021371 / 0.030504 | 0.012967 / 0.038223 / 0.062131 | 0/80 |
| foreground_profiles | 0.002062 / 0.002568 / 0.002936 | 0.002404 / 0.005356 / 0.007336 | 0/80 |
| residual_ledger | 0.006172 / 0.015787 / 0.025460 | 0.007229 / 0.014553 / 0.039338 | 0/80 |
| font_guides | 0.010427 / 0.017569 / 0.019885 | 0.014458 / 0.051126 / 0.082132 | 0/80 |
| image_motifs | 0.008364 / 0.012279 / 0.012412 | 0.010082 / 0.012936 / 0.015395 | 0/80 |
| selective_rerun | 0.355358 / 0.633570 / 0.892914 | 0.443669 / 0.852119 / 1.159944 | 1/80 |
| ink_condition | 0.016896 / 0.027530 / 0.033225 | 0.019070 / 0.038675 / 0.052845 | 0/80 |
| map_graph | 0.220056 / 0.418752 / 0.452729 | 0.243136 / 0.770984 / 0.956105 | 0/80 |
| classical_residual | 0.087980 / 0.292525 / 0.314857 | 0.085361 / 0.654180 / 1.052466 | 2/80 |



The fresh composition uses no diagnostic primitive/reference cache and takes three warm repetitions per upright page in seeded order. Startup/warm-up and review writing are excluded from compute, decode is included in wall time. Only A02 and A03 are dispatched; residual requests stay unresolved. Baseline-only E00 also has three raw repeats, but its final few diagnostic pages overlapped the start of reference materialisation; prefer the isolated baseline intervals inside ET for the final runtime comparison.

| Cohort (warm page repetitions) | Baseline p50 / p95 (s) | Mandatory scout p50 / p95 (s) | Actual added p50 / p95 / max (s) | Compute p50 / p95 (s) | Wall including decode p50 / p95 (s) |
|---|---:|---:|---:|---:|---:|
| development (159) | 0.130084 / 0.157007 | 0.034433 / 0.080208 | 0.417848 / 1.024858 / 1.875607 | 0.542357 / 1.169421 | 0.571188 / 1.253588 |
| agreement (120) | 0.122774 / 0.154584 | 0.034037 / 0.044499 | 0.360538 / 1.077296 / 1.130328 | 0.477483 / 1.195910 | 0.503254 / 1.226388 |
| discrepancy (240) | 0.129894 / 0.158968 | 0.033216 / 0.075391 | 0.403123 / 0.780480 / 1.104570 | 0.539058 / 0.914888 | 0.551540 / 0.962126 |

Agreement `(base + scout)/base`: p50 **1.2734**, p95 **1.3228**. The full correction layer costs more than the mandatory scout; its raw rows are in [composition/timing.jsonl](../../.astra/fast_lines/out/composition/timing.jsonl). Below-one-second compute is not a passed correction target when geometry or ownership fails. This run does **not** establish the owner's intended result.

The fresh correction layer adds **360.5 ms median** on agreement pages, with a **1077.3 ms p95**. That is not negligible. Discrepancy added cost is **403.1 ms median**, but its maximum is **1.105 s**, and visual correction quality is unresolved or regressive on the cases below.

## Per-prototype result and next step

### A01 — native_contours

Replays one float map through quad/poly and six one-factor control changes.

**Prediction → result.** Polygons preserve local contour shape but do not repair topology. `s2-3229200bf47ca465a42d-p00004` retains bent contours and lower-left fragments; `an-a73d22211479-p000301` still crosses the rule. Lower-threshold outputs are diagnostic variants, not a selected accuracy winner.

**Evidence:** [running log](../../prototypes/fast_lines/native_contours/README.md), [174-page gallery](../../.astra/fast_lines/out/native_contours/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/native_contours/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/native_contours/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Keep contour genealogy and compare polygon versus local geometry only on adjudicated ends. No global control setting is accepted as superior.

### A02 — layout_barriers

Finds long rules and persistent whitespace, checks crossed bands, preserves detected table text.

**Prediction → result.** V1 failed both `an-a73d22211479-p000301` and `an-a73d22211479-p000141`, and falsely protected newspaper `s2-661ddf05c8865e7b2c45-p00005` as a table. This prompted a globally applied, explicitly supported sloped-rule revision and distinct grid intersections. Its final named-page findings are recorded below. `an-7a2b17a3fb0f-p000200` is a table-preservation check, not an accuracy label.

**Evidence:** [running log](../../prototypes/fast_lines/layout_barriers/README.md), [174-page gallery](../../.astra/fast_lines/out/layout_barriers/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/layout_barriers/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/layout_barriers/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Prioritise explicit separators, then validate spanning headings, local cell/leaf identity and every new split. Do not call the provisional block list a physical leaf model.

The supported sloped-rule follow-up separates the visible columns on the three inspected prose examples. These counts describe split operations, not line accuracy:

| Page | Split operations | Table protected | Marginal seconds |
|---|---:|---|---:|
| `an-a73d22211479-p000301` | 40 | False | 0.168855 |
| `an-a73d22211479-p000141` | 36 | False | 0.169576 |
| `s2-661ddf05c8865e7b2c45-p00005` | 52 | False | 0.144347 |
| `an-7a2b17a3fb0f-p000200` | 0 | True | 1.259699 |

V1 outputs and its exact recovered, hash-matching source are retained at `layout_barriers-v1/` and `shared/source/A02-v1-run.py`. Dense Hough voting is now the cost failure: this is a useful explicit model, not a negligible always-on check.

### A03 — local_ribbons

Sparse map cross-sections nominate local dynamic-programming paths and endpoint proposals.

**Prediction → result.** The clean-control prediction failed: `s2-77d1bd63d5babbe0df73-p00001` has unnecessary retracing, a signature pulled toward its neighbour, and clipped ends. `s2-3229200bf47ca465a42d-p00004` largely remains unresolved after multi-ridge abstention. Preserving item count is not preserving geometry.

**Evidence:** [running log](../../prototypes/fast_lines/local_ribbons/README.md), [174-page gallery](../../.astra/fast_lines/out/local_ribbons/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/local_ribbons/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/local_ribbons/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Do not promote this repair. Replace the endpoint acceptance check, preserve supported extents, and enforce neighbour ownership/noncrossing before another runtime claim.

### A04 — sheet_lattice

Fits median quadratic displacement per provisional block, with affine initialisers and pitch/phase alternatives.

**Prediction → result.** It makes shared geometry and residuals inspectable, but blocks are not verified physical leaves. Sparse fragments and mixed sizes remain underconstrained. `s2-3229200bf47ca465a42d-p00004`, `s2-86865c33eef5932c013b-p00005`, and `an-d83e7a198ade-p000099` are the key unresolved cases; no independent curl-accuracy success is established.

**Evidence:** [running log](../../prototypes/fast_lines/sheet_lattice/README.md), [174-page gallery](../../.astra/fast_lines/out/sheet_lattice/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/sheet_lattice/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/sheet_lattice/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Use explicit leaf/column assignment, fit/train anchor separation and residual coverage. Keep local alternatives instead of imposing one sheet on a spread.

### A05 — foreground_profiles

Measures sparse contrast, normalised gradient and threshold persistence against dense profiles; attaches competing-grid evidence.

**Prediction → result.** All ownership remains unknown and existing pale fronts are retained. On `s2-09f5dfca4af4d74173c6-p00005` and `an-1be60011c435-p000215`, contrast-only flags are zero and edge-only flags are three each: this does not separate ghosts from pale fronts. `s2-0ce9d1025b3f23c7119e-p00001` remains a sharp-ghost counterexample. No verified false-positive removal.

**Evidence:** [running log](../../prototypes/fast_lines/foreground_profiles/README.md), [174-page gallery](../../.astra/fast_lines/out/foreground_profiles/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/foreground_profiles/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/foreground_profiles/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Materialise actual cross-stroke edge-spread measurements and matched front/ghost exemplars. Do not turn relative darkness or the dominant grid into ownership.

### A06 — residual_ledger

Separates support subtraction from envelope subtraction, removes explicit rules, applies the motif veto, and freezes common region requests.

**Prediction → result.** `s2-77d1bd63d5babbe0df73-p00001` produces 70 raw nominations merged to 11 requests despite being a clean control. `s2-09f5dfca4af4d74173c6-p00005` produces zero accepted-size regions while 263116 support-residual pixels remain: the component size filter hides a large region; this is not successful ghost classification. `an-d6002cf45e4d-p000058` has 21 nominations, 10 texture vetoes and seven merged requests.

**Evidence:** [running log](../../prototypes/fast_lines/residual_ledger/README.md), [174-page gallery](../../.astra/fast_lines/out/residual_ledger/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/residual_ledger/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/residual_ledger/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Tile and inspect the rejected large residuals; compare actual support ownership before suppression. Reduce clean-page false alarms without losing whole blocks. Preserve the frozen request corpus for fair fallbacks.

### A07 — font_guides

Groups local scale/profile-compatible lines, measures density extents/modes and labels measured versus borrowed profiles.

**Prediction → result.** Adaptive mode counts are available, but baseline/accent semantics remain unknown. `an-ffccc97c07de-p000152` has 25 families for 34 bands and visually mixed Arabic-row extents; `an-d83e7a198ade-p000099` has 65 families for 120 bands. This is overfragmented for a useful shared type prior.

**Evidence:** [running log](../../prototypes/fast_lines/font_guides/README.md), [174-page gallery](../../.astra/fast_lines/out/font_guides/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/font_guides/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/font_guides/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Build compatible block exemplar stacks and attach components to guide modes. Test actual amortisation and reject borrowing across mixed scripts/scales.

### A08 — image_motifs

Uses residual area texture, directional coherence and a fixed height-relative repetition witness to veto new speculative proposals.

**Prediction → result.** On `an-d6002cf45e4d-p000058`, the engraving and decorative initial become texture regions while all existing lettering remains. The region extends beyond the picture and is not an exact boundary. On `an-1f8e7d022643-p000003`, ornament boxes remain; repeated glyph versus ornament ownership is unresolved. `an-778126cc8c2b-p000010` remains an overlap challenge.

**Evidence:** [running log](../../prototypes/fast_lines/image_motifs/README.md), [174-page gallery](../../.astra/fast_lines/out/image_motifs/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/image_motifs/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/image_motifs/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Keep the new-proposal-only veto as a candidate, refine support boundaries and review every suppressed crop. Existing line rejection needs separate evidence.

### A09 — selective_rerun

Runs a 1440 full-page comparator, then scale-only, unbend-only and combined crops from at most three frozen requests; remaps and deduplicates.

**Prediction → result.** Actual tensor dimensions and all crop calls are saved. The three-request budget explicitly leaves requests unresolved. Increased item count cannot establish missing-line recovery; inspect `an-d83e7a198ade-p000099`, `an-7a2b17a3fb0f-p000200`, `s2-86865c33eef5932c013b-p00007`, and ghost-rich `s2-0ce9d1025b3f23c7119e-p00001`. Where no shared field is supported, unbend is the identity and is labelled by its zero shift. On clean development control `s2-77d1bd63d5babbe0df73-p00001`, nine calls add no candidates and leave eight requests unscheduled. On `s2-86865c33eef5932c013b-p00007`, ten extra candidates include isolated ditto/letter marks, while broad bands still straddle at the curved right edge. On `s2-d12a9a4feb23254f4080-p00009`, nine calls add no candidates and leave 23 requests unscheduled.

**Evidence:** [running log](../../prototypes/fast_lines/selective_rerun/README.md), [174-page gallery](../../.astra/fast_lines/out/selective_rerun/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/selective_rerun/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/selective_rerun/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** First fix request quality, then adjudicate actual tiny-front gains and new ghost detections. Do not infer cost from crop area; use the recorded tensor/call cost.

The clean-control prediction failed: `s2-77d1bd63d5babbe0df73-p00001` makes nine crop calls, adds zero retained lines and leaves eight requests unscheduled. On discrepancy `s2-86865c33eef5932c013b-p00007`, ten additions include visible isolated marks, but the overview still shows broad curved bands with unresolved right ends. No complete recovery count is claimed.

### A10 — ink_condition

Renders/compares component width, skeleton ends, counters, contrast and local family-conditioned width axes.

**Prediction → result.** Condition and faintness are separate numbers. `s2-86865c33eef5932c013b-p00005` has 63 measured samples but no automatic damage attribution; readability is unknown. `an-1f8e7d022643-p000003` bold/display text and `an-3352d912f2e9-p000104` noise remain counterexamples. No verified unreadability classification.

**Evidence:** [running log](../../prototypes/fast_lines/ink_condition/README.md), [174-page gallery](../../.astra/fast_lines/out/ink_condition/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/ink_condition/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/ink_condition/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Review original-size glyph groups against the dense threshold panels; improve family matching before interpreting width or fragmentation as damage.

### A11 — map_graph

Builds regional learned-map ridge paths on the common requests, splits at imported barriers and records seam conflicts.

**Prediction → result.** Its map-only candidates cannot restore absent evidence. It does not solve ownership or validate topology merely by having strong map support. `s2-49598b2e848ab1f0ee1e-p00001` and `s2-86865c33eef5932c013b-p00007` provide review candidates; tiny apparatus on `an-d83e7a198ade-p000099` and ghosts remain unresolved. The inspected `s2-86865c33eef5932c013b-p00007` result is a regression: twelve additional candidates include thin overlapping bands over already boxed text, and the severe right-end curl remains. Its 68 paths are not 68 useful lines. The clean development control adds zero candidates from 37 paths.

**Evidence:** [running log](../../prototypes/fast_lines/map_graph/README.md), [174-page gallery](../../.astra/fast_lines/out/map_graph/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/map_graph/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/map_graph/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Compare request by request with A03 using the saved line evidence and original pixels; keep only complementary, adjudicated geometry. No second network or independent request set.

Visual failure on discrepancy `s2-86865c33eef5932c013b-p00007`: thin overlapping paths are added over already boxed body text while the right curl remains. Twelve new candidates are not twelve recovered lines. This prototype needs an acceptance/ownership stage before use.

### A12 — classical_residual

Groups intensity-persistent components with a height-relative neighbour graph; compares persistence alone with width support and one full-page offline pass.

**Prediction → result.** It provides map-independent candidates, not foreground decisions. Stable coherent ghost print on `s2-09f5dfca4af4d74173c6-p00005` and `s2-0ce9d1025b3f23c7119e-p00001` defeats the premise that stability alone means front. Pale `an-1be60011c435-p000215` and mixed-script `an-ffccc97c07de-p000152` require component-level review. On `s2-86865c33eef5932c013b-p00007`, fourteen extra candidates include narrow fragments and isolated marks; the main curl remains. The clean development control `s2-77d1bd63d5babbe0df73-p00001` gains one unvalidated candidate. Neither is demonstrated missing-line recovery.

**Evidence:** [running log](../../prototypes/fast_lines/classical_residual/README.md), [174-page gallery](../../.astra/fast_lines/out/classical_residual/index.html), [page-by-page failures/unknowns](../../.astra/fast_lines/out/classical_residual/page_failures.json), [line-by-line comparison](../../.astra/fast_lines/out/classical_residual/per_line_comparison.json). Counts are not accuracy. The timing table above and raw per-page files distinguish agreement and discrepancy.

**Next:** Reuse stroke primitives and common requests; do not turn the coarse full-page diagnostic into an always-on detector. Review accents, touching components and every accepted new candidate.

## Shared modules and consumers

| Module | Consumers / ownership |
|---|---|
| S0 manifest | All: exact allowlist, image/model/old-output hashes and parked record. |
| S1 detector / extracted DB | All share E00; A01 owns controls, A09 owns additional inference. |
| S2 image evidence | A02–A08/A10/A12: one lazy paper/contrast/gradient/persistence/stroke implementation and diagnostic primitive cache. |
| S3 geometry | Sampling, coordinate conversion, robust fit, continuity and pitch operators; algorithm ownership remains A03/A04/A11. |
| S4 contracts / context | All: one page record, typed evidence, request union and seam deduplication. |
| S5 references | All share original-pixel crops, dense raw supports, photometry, old-model hypotheses and stroke panels. |
| S6 review | All: detector JSON, discount filtering, stage style, contacts and HTML. |
| S7 timing/registry | All: source/config/input/dependency keyed receipts, cache hits and raw timing. |
| S8 scheduler | One independent raw-image scout and fresh A02/A03 composition, with unresolved ledger. |
| S9 perturbations | One seven-variant physical set on eight manifest-selected line crops; photometric responses only. |

The frozen standalone request corpus and fallbacks use A02 **v1**. The later sloped-rule follow-up is preserved separately as A02 **v2** and used by fresh composition. Its evidence is not silently substituted into earlier A03–A12 runs. Their dependency hashes bind the original inputs; propagating v2 through the entire fallback DAG remains unfinished. No duplicate higher-resolution or crop inference was run to dress up the report.

## Every unfinished item

- Exhaustive visual adjudication of every changed region and every line on all 174 pages is **not complete**. All baseline-line raw crops and page/line diagnostics are generated; inspected events are in the adjudication ledger. Uninspected cases remain `not checked`. There are no precision/recall claims.
- The fine-grained prediction/result process is incomplete for several approaches: READMEs record the common reference phase, compact batch study and follow-ups, rather than a separately reviewed iteration for every numbered substep. Some supplementary genealogy/variant overlays are materialised after the diagnostic runs from saved products; no claim is made that every heuristic completed the requested visual-first acceptance process.
- A02 has rules, barriers, provisional blocks and preservation decisions, but no completed cell-assignment graph or verified physical-leaf graph. Spanning-heading validation remains incomplete.
- A03 has no accepted guide/diacritic attachment or reliable endpoint/noncrossing acceptance; the current endpoint check can shrink support. A04 lacks explicit independent anchor train/test splits and cross-strip correlation fitting; its pitch autocorrelation is not that experiment.
- A05 uses normalised gradients, not a complete cross-stroke edge-spread model; competing grids are shown but not used to assign ownership. A06 does not solve the giant-component/whole-block blind spot. No accepted missing-line recovery is established by nomination counts.
- A07 does not identify semantic baseline/accent systems or demonstrate reliable stack-based borrowing. A08 lacks precise overlapping image/text ownership and an adjudicated existing-line rejection study. Optional ring/initial refinements are unimplemented.
- A09 runs the requested comparator and three crop variants within a declared budget; requests beyond that budget remain unresolved. No exhaustive visual verdict proves which added bands are useful. Inference maps for the larger/crop runs are not preserved, only results/tensor/remap receipts.
- A10 provides physical axes and sampled original-size referees, not an adjudicated broken/filled/readability classifier. A11/A12 candidates are unreviewed unless explicitly named in the ledger; the A12 prototype is a simple threshold-persistence/distance-width graph, not a full MSER/SWT implementation.
- The fresh composition measures **scout + A02 + A03**, with unresolved residual requests; the full proposed A01–A12 dispatch DAG is **unfinished**. It is timed as an unsuccessful candidate, not presented as the finished hybrid.
- The shared perturbation set covers seven changes on eight manifest-selected line crops and photometric responses. Every prototype's witness has **not** been tested against every perturbation. Cached Kraken/nine-detector reference import is not added beyond Q6's existing evidence.
- Viewer JSON/null-score shape is checked and existing Kraken cache uses null scores, but a live comparison-app import was not performed. Use the provided static galleries; no GUI validation is claimed.


## What round 2 should materialise

1. Finish the explicit separator/cell/leaf model and adjudicate its splits on both cohorts. It attacks the visible zero-residual column failure and constrains every later path. Include the newspaper false-table counterexample and spanning headings.

2. Rebuild geometry acceptance around independent support, preserved endpoints and noncrossing ownership. Compare the small detector's native polygon with one local correction; retire the present A03 clean-path dispatch until its regression is fixed. Test a shared leaf field only where support and held-back anchors justify it.

3. Make foreground/unknown ownership and residual coverage explicit before accepting new lines. Fix giant rejected components, inspect off-rhythm and whole-block cases, and distinguish verified suppression from silence caused by a size filter. Keep image-text overlap local.

4. Reuse one frozen request corpus to adjudicate map graph, classical graph and crop inference. Materialise only branches with a complementary visible success, then measure a complete fresh path and its missed triggers. Cheap-page overhead must include every dependency.

A13 book priors and A14 duplex remain blocked by identity/pairing evidence; A15/A16/A17 external dewarp/source/layout references remain deferred; A18 uses existing evidence only; A19 mirror signatures need spatial, labelled compatibility tests. Orientation remains parked. No held-out evaluation or API integration follows from this partial round.

## Validation and commit scope

Prototype/shared tests: **33 passed / 33**. Artifact validation checks all 174 records per prototype, full-page finite polygon coordinates, required JSON keys/null scores, no discounted results, unchanged parked page and protected-table identity. Local-link validation covers 190 HTML documents and 31381 local links, with zero missing targets. The API and its tests are unchanged. No push or background worker was started. All foreground experiment runs completed. Full live-app rendering and exhaustive visual adjudication are not claimed.

The optional comparator audit checked 2595 exports and found three A12 records extending beyond the page by 2.2737367544323206e-13 pixels (floating-point rounding). They now use the same shared coordinate clipping as the main results. Original JSONs are preserved in `shared/original-variant-exports`, and the correction receipt is `shared/variant-validation.json`. No candidate-generation or inference experiment was rerun. Publishing-only fixes and the S9 change below postdate the measured runtime source, archived in `shared/source/Q7-measured-source`; A02 v1 has its separate exact source archive.

An S9 artifact correction replaced empty blur/thickening change arrays with exact changed-pixel magnitudes. The eight exemplars retain identical rendered images and photometric measurements; both generations and the pre-correction source snapshot are saved. The stored break mask marks the intervention strip; curl and shift arrays describe displacement. Only this corrected EP materialisation was rerun. Publishing and report generation perform no inference.

Git staging was blocked by the sandbox when creating the worktree `index.lock`; no commit was created. The requested fallback is `.astra/Q7.patch`, validated by applying it to a clean copy of the research plan and comparing every resulting file byte-for-byte, plus `.astra/commit-Q7.sh`. The script checks the branch, research HEAD, clean index and reviewed file hashes before staging only the reviewed paths and committing with both required trailers. It does not push.
