# Line segmentation: implementations and responsibilities

[Documentation index](../../shared/DOCUMENTATION_INDEX.md) · [Current handoff](../../records/research/round8/LOOP_HANDOFF.md) · [Worker roster](../../records/research/round8/ROSTER.json)

Read the [method](LINE_SEGMENTATION_METHOD.md) for the charter and physical construction, and [test guide](LINE_SEGMENTATION_TESTS.md) for the evidence required to claim it works. The [completion plan](../../records/research/round8/GEOMETRY_COMPLETION_PLAN.md) assigns the missing font-guide and edge-curl consumers explicitly.

## The three generations

These are the owner's development generations. They do not correspond to three independent installed models.

| Generation | Source and entry point | What it represents |
|---|---|---|
| **1 — our explicit pixel model** | [greekocr/pages](../../../greekocr/pages/): `process_page` for the page API; `pages.lines.segment_page` for pixel-based line construction. Crop primitives remain in [greekocr/glyphs](../../../greekocr/glyphs/). | Connected row discovery, component ownership, font guides, skew/curvature and boundaries. The slow physical reference, with known errors. |
| **2 — small neural detector plus heuristics** | [prototypes/fast_lines/stack](../../../prototypes/fast_lines/stack/): `Stack`; orchestration in [pipeline.py](../../../prototypes/fast_lines/stack/pipeline.py), providers mainly in [shared](../../../prototypes/fast_lines/shared/). | PaddleOCR PP-OCRv6 small localisations/maps followed by conditional corrections, recovery and reconciliation. |
| **3 — the current revision** | The same fast-stack source paths, developed in the checked worker branches named by the roster. | Consolidating generation 2, correcting its physical assumptions and qualifying Rust work. This is work in progress, not a separate completed implementation. |

Generation 1 originally lived in `glyphs/page_text_lines.py`, `pixel_segments.py` and `page_font.py`. Those names now alias the maintained `pages` modules; they are not additional independent implementations. The [dated lineage record](../../records/research/round8/MODEL_GENERATIONS.md) gives the introduction, relocation and reference commits, source checks and saved evidence.

Optional Docling table layout in the page API is separate from the original pixel-only line construction. It does not turn generation 1 into the small-Paddle pipeline.

## Follow a line through each implementation

**Original pixel construction:** `pages.pixels.prepare_pixels` supplies rough regions and components. In `pages.lines`, discovery and recovery form row models; `_pool_geometry` shares supported geometry; `_assign` assigns components independently of the original seeds; `_make_lines` follows their extent to barriers. `pages.font.fit_guides` fits the font/accent curves and `_boundaries` constructs neighbouring bands. See the [page pipeline](PAGES_PIPELINE.md) for the complete API stages and [owner algorithm](PAGE_LINES_ALGORITHM.md) for the original intended construction.

**Fast route:** `Stack` drives Paddle and the existing correction stages in `stack/pipeline.py`. Native row splitting, column handling, field geometry, envelopes and residual recovery remain separate providers. Trace the actual caller before changing a provider: different paths can use different row identities or component masks. A shared filename or a matching final polygon does not prove shared physical ownership.

## The four geometry concerns

The following is a map to existing code, not a claim that the current providers have one agreed authority or that all cases pass.

| Concern | Generation-1 construction | Fast-route code to trace |
|---|---|---|
| **One printed line per segment** | [lines.py](../../../greekocr/pages/lines.py): `_discover`, `_assign`, `_make_lines`, `_boundaries`; [font.py](../../../greekocr/pages/font.py): `fit_guides`. | [pipeline.py](../../../prototypes/fast_lines/stack/pipeline.py): row splitting/reconciliation; [geometry_rows.py](../../../prototypes/fast_lines/shared/geometry_rows.py): `analyze`, `confirmed_partition`, `whole_children`; [geometry_field_detector.py](../../../prototypes/fast_lines/shared/geometry_field_detector.py): `native_bands`, `separate_bands`; [type_residual_recovery.py](../../../prototypes/fast_lines/shared/type_residual_recovery.py): `recover`. |
| **Columns and finite boundaries** | [pixels.py](../../../greekocr/pages/pixels.py), [boundaries.py](../../../greekocr/pages/boundaries.py), [structure.py](../../../greekocr/pages/structure.py); lane assignment and barrier stops in `lines.py`. | [geometry_columns.py](../../../prototypes/fast_lines/shared/geometry_columns.py): `analyze`/`apply`; [geometry_page_field.py](../../../prototypes/fast_lines/shared/geometry_page_field.py): `blocks`; callers in [stack/geometry.py](../../../prototypes/fast_lines/stack/geometry.py). |
| **Skew** | Crop [baseline.py](../../../greekocr/glyphs/baseline.py), observed contacts and pooled geometry in `pages.lines`; guides follow the fitted path. | Existing row axes, native contacts and [geometry_envelopes.py](../../../prototypes/fast_lines/shared/geometry_envelopes.py), plus page-field/native-band consumers. Check their coordinate and support contracts. |
| **Curvature and complete endings** | `_pool_geometry` → `_assign` → `_make_lines` → font guides/boundaries, continuing beyond initial seed regions. | [geometry_page_field.py](../../../prototypes/fast_lines/shared/geometry_page_field.py), [geometry_field_detector.py](../../../prototypes/fast_lines/shared/geometry_field_detector.py), [geometry_envelopes.py](../../../prototypes/fast_lines/shared/geometry_envelopes.py): `guided`/`correct`. Their consolidation and outstanding cases are tracked in the current plan. |

Font guides connect the four concerns: row identities determine neighbours, shared geometry follows skew/curvature, and facing guides plus component support define boundaries. A local separator fix does not establish that the complete construction has been reconciled.

The retained `native_bands`/`separate_bands` request repair uses native components and whitespace corridors but does not fit the four font guides. Existing `pages.font.evidence/fit_guides` does that class-conditioned work; reuse requires correct row/component attribution and actual caller migration. Likewise, the page displacement mesh is a candidate representation, not proof of book-induced edge curl. Shared bend should be visible as virtual parallel lines and govern continuation beyond clipped boxes. FONT is parked and geometry/CURL closed partial; any separately authorized future work must verify its consumer and displaced decision.

## Runtime, reference tools and historical experiments

- **Executable package API:** use the [page guide](PAGES_GUIDE.md). Importing this API does not select the fast prototype.
- **Executable fast prototype:** use the [stack README](../../../prototypes/fast_lines/stack/README.md), with the actual source head and runner specified by the current task. Its R7/R6 measurements remain historical.
- **Feature/reference tools:** `prototypes/fast_lines/font_guides`, `features_geometry`, `features_ink` and other study directories contain useful renderers or providers. Some are imported by the stack; “prototype” does not mean unused.
- **Original Q7/Q8 experiment runner:** the [fast-lines root README](../../../prototypes/fast_lines/README.md) documents that earlier experiment graph. Its `run compose` command is not the current `Stack` entry point.
- **Rejected round-8 constructions:** the from-scratch physical model and Paddle-seeded slow adapter are experiments, not generation 1 or accepted replacement providers. Do not infer their status from their directory names.
- **Rust pilot:** location and acceptance are recorded in the [roster](../../records/research/round8/ROSTER.json) and [completion plan](../../records/research/round8/RUST_COMPLETION_PLAN.md). The parked pilot is not automatically present or active in every checkout. Qualify any adoption against the then-current Python contract.

No single directory name tells you whether an experiment is accepted. The worker report and independent review establish that; the roster/handoff identifies which head to use. The [15 October audit](../../records/research/round8/AUDIT.md) binds the checked runtime at `046bd52` and separates default, optional, offline and parked-branch code.

## Evidence and current work

The [final runtime audit](../../records/research/round8/REPORT_R8-AUDIT-02-i1.md) accounts for retained R/B/A output, actual deletions, all historical owner records, tests and two final-source timing passes. Audit completion does not complete the physical or speed goals. Python, `bend=False` and `final_export=False` remain default; broad tessellation and the current exact/slower native field batch remain explicit experiments. Both owner field questions are unallocated; planner closure follows independent review.

Read [LOOP_HANDOFF.md](../../records/research/round8/LOOP_HANDOFF.md) first for current work, then [ROSTER.json](../../records/research/round8/ROSTER.json) for the correct branch/worktree and [PLAN.md](../../records/research/round8/PLAN.md) for the full reasoning. Prompts are task inputs; reports record outcomes; independent checks can reject a worker's proposed outcome. Keep all three roles visible.

The [generation record](../../records/research/round8/MODEL_GENERATIONS.md) points to the saved 23-page first-generation comparison, its source hashes and known local errors. Native images and JSON usually reside under `.astra/fast_lines/out/` in the worker's worktree, rather than this checkout. Historical rows are matched by native page coordinates and ink, not by assuming row numbers agree between models.

For each physical repair, show the original construction and fast route on the same development case, find the earliest divergence, and reuse the working calculation with compatible inputs. `PixelPage.boxes` expects rough pixel regions; replacing them with tight Paddle polygons previously invalidated that comparison. The old model is evidence, not ground truth. Final crops and whole letters/marks determine correctness; output equality alone preserves existing defects.

Keep code and reproduction paths stable during active worker iterations. Place durable navigation in `docs/`, task status in the existing handoff/roster, dated reports in their research/review locations, and generated evidence in its source-bound output directory. A later physical module move must migrate imports, tests and reproduction paths in the owning worker task; it must not create a third live copy of the same algorithm.


R8-GEOM-03 closes PARTIAL at3/3. The accepted-partition consumer passes its same-call native context and exact old-piece census to a conditional whole-component extent builder; unsupported parents retain one atomic vector fallback. Changed extents refresh source/motif/rule and final ownership/footprint/faintness/frame decisions. See [final geometry report](../../records/research/round8/REPORT_R8-GEOM-03-i3.md) and the provenance-bound native/phase tests in `features_geometry/test_whole_children.py`. Four R rows and one additional-book lower B row are retained; row discovery, font guides and finite field/curl domains remain separate.

FONT-03 i1 retains stronger [returned-polygon tests](../../../prototypes/fast_lines/features_geometry/test_whole_children.py) in all13 phases, a strict real apostrophe-omission prerequisite and passing final-reconciler preservation check, plus [native accent-veto witnesses](../../../prototypes/fast_lines/features_geometry/test_accent_admission.py). Its bounded accent refinement passed native/constructor checks but was withdrawn after final reconciliation introduced partial upper-row ink and duplicate marks. Runtime R/B and membership/priority remain at aa6d3d4. See [iteration report](../../records/research/round8/REPORT_R8-FONT-03-i1.md).

FONT-03 i2 corrects i1's premise: a73d147 belongs to lower track3/body77; nearest-box singleton agreement was false ownership evidence. The [offline native input adapter](../../../prototypes/fast_lines/evidence/r8_font_guides.py) and [contract tests](../../../prototypes/fast_lines/features_geometry/test_native_font_contract.py) expose conditional guide fits and three letter-stroke/upper-mark class counterexamples. The attempted live guide consumer is withdrawn; R/B runtime remains56afb02/aa6d3d4. See the [i2 report](../../records/research/round8/REPORT_R8-FONT-03-i2.md) for all22 callers and independent later raster/reconcile failures.
