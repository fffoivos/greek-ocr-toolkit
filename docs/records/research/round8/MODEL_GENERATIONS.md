# Which older model the owner means

[Repository implementation map](../../../A_ocr_development/reference/LINE_SEGMENTATION.md) · [Documentation index](../../../shared/DOCUMENTATION_INDEX.md). This file is the dated identification/evidence record; the implementation map is the durable starting point.

12 October 2026. The owner distinguishes:

> 1st gen that our model alone
> 2nd gen which was "small detector" neural model + heuristics on top
> and now we are doing 3rd gen

These are the owner's project generations, not package or neural-model version numbers. The code/history support the following mapping.

| Generation | Actual implementation and lineage | Role now |
|---|---|---|
| 1: our own explicit detector | Pixel-first page detector introduced as `greekocr/glyphs/page_text_lines.py` and `pixel_segments.py` in `f405fe38bc19febc7600c61a49cca05740fde73d` (9 October). Later page/font refinements; Q3 moved it to `greekocr/pages/lines.py`, `pixels.py`, `font.py` in `bb06ee4ecd72d22a7bb53c0a082e396a6588c96e`. Q4 snapshot `76ad6fb4f513fb3eb99531cc553899976b4c8801` contains the maintained slow construction. | Existing physical construction to run/read as a whole reference, with its errors recorded; source of specific reusable calculations. |
| 2: small neural detector plus corrections | PaddleOCR PP-OCRv6 **small**, probability maps and localisations, followed by `prototypes/fast_lines/stack` and its `shared` heuristics. Fast-lines rounds before the present consolidation produced the R7 stack. | Useful existing fast behaviour to preserve and simplify. It already includes splitting, column, skew and bend mechanisms, but their row/ownership representations compete. |
| 3: current revision | Round-8 consolidation, geometry/ink repairs and Rust work on that fast stack. It still uses Paddle and inherited generation-2 mechanisms; it is not an already completed third independent detector. | Reconcile useful existing mechanisms with explicit page features; replace failed/duplicate decisions only after verifying their replacement. |

## Why this is the first-generation model

The original [page-detector brief](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/chats/rollout-2026-10-09T_greek-ocr-toolkit-astra-lines_1a11d5b-a0e4-.md) explicitly asks for one pixel-first path, four font curves, shared skew/curvature, rows discovered without input boxes and non-overlapping neighbouring boundaries. Its final report describes that construction. It predates the small-Paddle fast-lines project.

The [Q3 module map](../../reviews/PAGE_LINES_Q3_CLEANUP_API.md) documents the move from `glyphs/page_text_lines.py` to `pages/lines.py`, and `page_font.py` to `pages/font.py`. Those old import names still alias the maintained modules. The crop-level ancestors `glyphs/components.py`, `baseline.py`, `columns.py`, and earlier `recut.py`/`page_lines.py` belong to the same explicit-model lineage. They are not the small-detector generation; the complete pixel-first page detector is the principal reference.

The [archived charter](../FAST_LINES_CHARTER_2026-10-10.md) explicitly contrasts “Our detector (`greekocr/pages`, ~5 s/page)” with the small Paddle detector. Optional Docling table layout in the broader page API is separate from the pixel-only `segment_page(gray)` line construction. Four principal font guides were extended with accent guides; that is a refinement of generation 1, not evidence that it is generation 2.

Verified by read-only source comparison on this date: current `pages/lines.py`, `font.py`, `pixels.py`, and crop `glyphs/components.py`/`baseline.py` equal their `76ad6fb` contents. The three page modules also match the SHA-256 manifest attached to the saved R8-01 unmodified slow runs. No detector was run for this identification.

## Use the connected construction, not only its name

`prepare_pixels` → `_discover`/recovery → `_pool_geometry` → `_assign`/contact refinement → `_make_lines` → `fit_guides` → `_boundaries` is the reference chain. Read the actual calls in [segment_page](../../../../greekocr/pages/lines.py); the [page pipeline](../../../A_ocr_development/reference/PAGES_PIPELINE.md) describes their contracts.

| Owner aspect | Generation-1 construction to inspect and compare |
|---|---|
| One printed line per segment | Distinct discovered row identities, component assignment to final curves, fitted font/accent guides and shared boundaries. Compare whole components and row count/identity, not just polygon overlap. |
| Columns | Native graphical barriers/gutters, lane assignment, stopping of the whole text band, and the later boundary/structure evidence. Inspect actual finite endpoints and multi-leaf layouts. |
| Skew | Observed line contacts and pooled neighbouring geometry, with geometry borrowed for short rows. Separate measured support from extrapolation. |
| Curvature | Shared curved paths, ink assignment beyond initial seeds, fitted guides and lateral continuation to actual boundaries. Compare whole line ends and neighbour separation together. |

This construction already connects the four aspects. Recent fast-route separator work is not the first attempt at (a). It repairs one inconsistent fast-route representation; it does not replace the broader first-generation reference obligation.

## Existing evidence to use before repeating work

The absolute chat, image and check paths in this dated record are local coordinator evidence locations, not GitHub links. The source/API links and archived charter are repository navigation.

The unmodified reference already ran on all 23 R8 pilot pages:

`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/slow/`

Use its `source.json`, per-page guides, row records and native crops with the [independent G1 check](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-01_check.md). That check finds the old detector already preserves many curl endings on 8686/3229/4959, separates 77d1's 39 lines, keeps “Γ. Μαυρομιχάλης”, table number “32” and weak “τῆς”, and separates the e259 leaves. It also records slivers, a misregistered 4959 row, a dropped Ψ initial and small end clips. Those successes and errors are evidence, not universal correctness claims.

For the current 4959 p5 case, match the same native coordinates and ink in generation 1, the accepted fast stack and the new trial. Do not equate slow row IDs with fast #109. Prior checks also found that the slow reference can misassign the disputed apostrophe: do not use its assignment as truth. Inspect original pixels, row identities, all guides, neighbours, owned components and final crops together. Reuse saved evidence where it answers the question; any missing rendering is a scoped development-only worker action under the established runner, not a new planner run or a full-corpus rediscovery.

## Consequence for subsequent planning

The next result/check must explicitly say what the first-generation construction does on the same failure and identify the earliest divergence in the fast route: region input, row identity, component ownership, guide fit or final boundary. If the old construction succeeds, reuse/adapt that identified calculation with compatible inputs and delete the competing decision in its verified scope. If the old construction fails too, preserve the exact common counterexample; another citation to the old code is not a solved model.

Keep the generation-1 pixel seed contract intact. The rejected R8 reference adapter fed tight Paddle polygons into `_discover` through `PixelPage.boxes`; those were not its expected rough pixel regions and that attempt lost/mixed rows. That failed adapter is not generation 1 and does not establish that the original model failed. Generation 2 localisations may inform a compatible fast adapter; they must not silently redefine the old detector's inputs.

Generation 1 is an executable reference and a source of reusable mechanisms. This does not install its full slow pipeline on every fast page, declare it perfect, or require copying all its thresholds. Use native evidence to decide which construction works and profile the actual computation before choosing its fast or Rust implementation. A faithful port does not resolve an existing physical error.

This identification does not silently rewrite or relaunch the already issued geometry-i5 prompt, change task caps, or create another worker iteration. Attach this evidence to the next coordinator/planner result review and use it in the next prompt where geometry semantics are chosen or ported. No code changes, launches or held-out access were made here.
