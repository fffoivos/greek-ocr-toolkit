# Segmenter generations — dated identification record

Documentation for `docs/A_ocr_development/MODEL_GENERATIONS.md`. Adapted from `docs/records/research/round8/MODEL_GENERATIONS.md` (12 October 2026), updated by source/history inspection on 19 October at `cleanup/20261019`, `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33`. The original dated research record is preserved. No model, pipeline, test suite or private evaluation was run for this update.

## Owner terminology and cleanup mapping

The 12 October source records the owner's distinction: first our own model alone; second the small neural detector plus heuristics; third the present revision. These are **project generations**, not package versions, Paddle model versions or filter versions.

The 19 October owner brief names (i) the slow segmenter, (ii) the next generation, (iii) the one on top of the small detector. `docs/cleanup_20261019/PLAN.md` proposes this mapping:

| Chronological generation | Owner cleanup label | Implementation | Role at the inspected integration |
| --- | --- | --- | --- |
| **1 — explicit pixel-first model** | **A.i / (i), slow** | `greekocr/pages`: `process_page`, `process_book`, `pages.lines.segment_page`; crop primitives in `greekocr/glyphs` | Executable slow physical reference with known errors; source of reusable calculations. |
| **2 — small detector plus heuristics** | **A.iii / (iii)** | PaddleOCR PP-OCRv6 small maps/localisations plus `prototypes/fast_lines/stack` and shared correction providers at R7 | Historical fast baseline, preserved inside the R8 lineage. |
| **3 — R8 revision** | **A.ii / (ii), next generation** | The same fast-stack paths, consolidating geometry/ink/type/recovery and qualifying numerical work | Current integrated prototype; narrow gains, accepted audit, broad goals partial. |

This is the plan's proposed taxonomy mapping, not a newly obtained owner ruling. A.ii and A.iii are two generations of the **same** fast stack. Generation 3 still uses Paddle and inherited generation-2 mechanisms. Optional Docling table layout in generation 1 is separate from the small-Paddle line detector. Four main font guides plus accent refinements do not make the pixel detector generation 2.

## Dated implementation record

| Date (2026; Git author dates where listed) | Source / commit | Event and evidentiary limit |
| --- | --- | --- |
| 8 October | `docs/A_ocr_development/reference/PAGE_LINES_ALGORITHM.md`, historical `a5750e2` status | Box-guided `recut.fix_page` algorithm: row identity/neighbours, shared skew/curve, font guides, midpoint boundaries and generous extension. Later owner direction switches discovery to pixels; old boxes become optional diagnostics. This is an ancestor specification, not today's pixel input contract. |
| 9 October | `f405fe38bc19febc7600c61a49cca05740fde73d` | Pixel-first detector introduced as `glyphs/page_text_lines.py` and `pixel_segments.py`. Generation 1 predates the fast small-Paddle project. |
| 10 October | Q3 `bb06ee4ecd72d22a7bb53c0a082e396a6588c96e` | Moves maintained page modules into `pages/{lines,pixels,font}.py`, adds shared API/CLI. Old module names alias current implementations; crop APIs remain. Q3 report retains a failed strict frozen-output gate. |
| 10 October | Q4 `76ad6fb4f513fb3eb99531cc553899976b4c8801` | Optimizes page analysis. Current core `pages/{lines,pixels,font}.py` still equal this snapshot. |
| 10 October | `3f75344e63c80bcdaecda11a1029079c1cd702b4` | Adds opt-in torch array experiments and GPU-pipeline design; `pages/torch_prototypes.py` is not imported by the production page API. This is the latest path change under `greekocr/pages`, not a new default detector. |
| 10 October | `4e2199ddf5141760255e469fac00d88ed759c749` | Source history of the current small-detector adapter: round-one prototypes, ONNX CPU session and DB postprocessing. Q7 study graph and later conditional Q8 paths precede R7 Stack. |
| 11 October | R7 work `932027e210debf0e63b152894d2bdd727770579b`; review/merge `52cee3bcc882e7426bdc1018d892cd9b1bf9feac` | Partial R7 benchmark and review baseline. R8 audit compares final masks against `52cee3b`. These commits survive as ancestors of `astra/ff-merged`; current paths are subsequently revised R8 code. |
| 12 October | `docs/records/research/round8/MODEL_GENERATIONS.md` | Identifies the three generations and saved 23-page slow comparison. Its source-equality statement was true of the dated comparison, not a perpetual assertion about later integration. |
| 15 October | Runtime `046bd52dddeea7ada7727971f1038d34328ba5b7`; audit delivery `2f1c91a09b844c87696b95b6c89cd5c3ff7beede` | R8 audit accounts for narrow retained output and remaining architectural/physical/speed limits. Addendum records ACCEPT WITH NOTES and supersedes original pending/no-worker-commit wording. No audit runtime change. |
| 15 October | `astra/ff-merged` tip `cae93fb49ac1e2e9332fdd57a60f920e266ba1ba` | Latest merged planner direction: nominated-edge curvature work is proposed, not allocated or implemented by the closing note. |
| 19 October | Shared crop change `582cacb7fc77da695e738de65fef02317535b840` | Adds `Band.curve_is_straight` construction provenance. The crop fitter is no longer byte-identical to Q4; a degree-1 tracked polyline may still bend. This shared primitive is consumed by B's curve measurement, not a fourth segmenter. |
| 19 October | Integration `cleanup/20261019`, `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33` | The documentation snapshot integrates the branch work. Integration alone does not requalify historical outputs, tests or timings. |

## Generation 1: connected physical construction

The actual reference chain is `prepare_pixels → _discover / _recover_bodies / _merge → _lanes / _pool_geometry → _assign / contact refinement → _make_lines → fit_guides → _boundaries`, with contrast/discount/order and structure stages in their source positions (`greekocr/pages/lines.py`). Rough pixel regions supply compatible discovery inputs. Font evidence measures body/tall/descender/mark classes; shared geometry and owned components support complete row extents and facing-guide boundaries.

The crop-level `glyphs/components.py`, `baseline.py`, `columns.py` and earlier `recut.py`/`page_lines.py` belong to this explicit lineage. They are not the small-detector generation. The low-level pixel `segment_page(gray)` does not require any Docling layout or recogniser boxes; higher page API tables are optional.

The recorded original run already covers all 23 R8 pilot pages in local worktree:

`greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/slow/`

The dated generation record points to `source.json`, guides, rows, native crops and a coordinator-local `R8-01_check.md`. It reports preservation of many 8686/3229/4959 curled endings, 77d1's 39 lines, “Γ. Μαυρομιχάλης”, table number “32”, weak “τῆς” and e259 leaves. It also records slivers, a misregistered 4959 row, a dropped Ψ, small end clips and a disputed apostrophe misassignment. These are attributed historical observations, not new image verification or universal correctness.

The rejected R8 slow adapter put tight Paddle polygons into `PixelPage.boxes`, where discovery expected rough pixel regions. Its lost/mixed rows do not show that the original pixel construction failed on the same page. Compare native coordinates, actual ink, row identities, guides and final crops; slow/fast row IDs are not interchangeable. Generation 1 remains a reference with errors, not gold truth or a requirement to install its full cost on every fast page.

## Generation 2 to generation 3: revisions, not reinvention

Generation 2 already supplied native rule/column corrections, skew/bend paths, ink/source suppression, fragment joining, type/residual recovery, envelopes, faintness and duplicate reconciliation. Q7's isolated graph and `run compose` are earlier diagnostic execution surfaces; the later `Stack` is the image-to-final entry point. See `segmenters/SMALL_DETECTOR_R7.md` for both histories.

R8 consolidated numerical observations, removed six ink copies and unused observation-cache infrastructure, removed M06 neighbour propagation, and sealed a single glyph-atlas construction route. It retained narrow certified native-child changes and one recovered body row. The accepted audit records 205/208 crop-mask-identical pages versus R7, six improved lines on three pages and identical exclusions, with remaining duplicate ink/tight boundaries/clipped curl. Metadata changes on 33 items/10 pages are separate from mask deltas.

A failed replacement physical model, a rejected tight-Paddle-box slow adapter, offline font tools, opt-in bend/final export and an old parked Rust pilot do not become accepted detector generations because of their directory names. Current Python / `bend=False` / `final_export=False` defaults stay distinct from experiments. FONT is parked; no complete curved ending or live font-guide gain was retained. Timing drift prevents a final round-wide speed claim. `docs/records/research/round8/AUDIT_CHECK_ADDENDUM.md` and `OWNER_CLOSING_SUMMARY.md` are later status records than the original audit's pending-review prose.

## Source precedence and current checks

Q4 comparison against current source (byte and executable-AST identities checked separately):

| File | Equals Q4 `76ad6fb` now? |
| --- | --- |
| `greekocr/pages/lines.py` | Yes |
| `greekocr/pages/pixels.py` | Yes |
| `greekocr/pages/font.py` | Yes |
| `greekocr/glyphs/baseline.py` | **No**: documentation/path edits; executable AST remains identical after removing the module docstring. This does not assert byte equality. |
| `greekocr/glyphs/components.py` | **No**: `curve_is_straight` field and construction provenance added at `582cacb7f`. |

Thus the 12 October source-equality sentence is updated, not copied as a current fact. The old algorithm document's document-over-code rule is also historical; current code and the authoritative B manifest win for this integration. B segmentation `0.13` (label `0.9-s5`) / gate `0.3` are crop-policy versions in `docs/harvest/line_pipeline/tool_versions.json`, not generation 3 or R8 detector releases.

No physical images or tests were needed to identify the lineage. Tests, independent native witnesses, final-output checks and speed qualification answer different questions; `docs/A_ocr_development/reference/LINE_SEGMENTATION_TESTS.md` separates them. The 41 prototype pytest files live outside default testpaths. Recorded 23/208/private44 populations retain their own roles and source identities.

## Sources read

- `docs/cleanup_20261019/OWNER_BRIEF.md`, `docs/cleanup_20261019/PLAN.md`, `docs/records/research/round8/MODEL_GENERATIONS.md`.
- `docs/A_ocr_development/reference/LINE_SEGMENTATION.md`, `docs/A_ocr_development/reference/LINE_SEGMENTATION_METHOD.md`, `docs/A_ocr_development/reference/LINE_SEGMENTATION_TESTS.md`.
- `docs/A_ocr_development/reference/PAGES_GUIDE.md`, `docs/A_ocr_development/reference/PAGES_PIPELINE.md`, `docs/A_ocr_development/reference/PAGE_LINES_ALGORITHM.md`, `docs/records/reviews/PAGE_LINES_Q3_CLEANUP_API.md`.
- `docs/records/research/round8/{AUDIT,AUDIT_COST,AUDIT_CHECK_ADDENDUM,OWNER_CLOSING_SUMMARY,ITERATION_HANDOFF}.md`; beginning of `ROSTER.json`.
- `docs/harvest/line_pipeline/tool_versions.json`, `greekocr/pages/{api,lines,pixels,font,torch_prototypes}.py`, `greekocr/glyphs/{components,baseline}.py`.
- `prototypes/fast_lines/stack/{README.md,pipeline.py}`, `prototypes/fast_lines/{README.md,run.py,workflow.py}`, `prototypes/fast_lines/shared/detector.py`.
- Read-only Git identity/history/ancestry commands for the commits above, R7 `stack/pipeline.py` at `52cee3b`, exact Q4/current byte comparisons, and the Q4-to-HEAD crop-fitter diff.
