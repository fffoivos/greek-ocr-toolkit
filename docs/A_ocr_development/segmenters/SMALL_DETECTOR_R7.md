# A.iii — the earlier small-detector stack (R7)

Documentation for `docs/A_ocr_development/segmenters/SMALL_DETECTOR_R7.md`, inspected 19 October 2026 at `cleanup/20261019` integration head `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33`. This is owner generation 2, before the R8 revision (A.ii / generation 3). The plan maps owner label **(iii)** to this historical lineage even though it chronologically precedes (ii).

## Historical identity

`docs/records/research/round8/MODEL_GENERATIONS.md` identifies generation 2 as PaddleOCR PP-OCRv6 **small** probability maps/localisations plus the `prototypes/fast_lines/stack` corrections. It is not `greekocr/pages`, and not the failed from-scratch round-8 physical model. R7 implementation commit `932027e210debf0e63b152894d2bdd727770579b` (11 October 2026) published the partial benchmark. The R8 audit compares against R7 review/merge baseline `52cee3bcc882e7426bdc1018d892cd9b1bf9feac` (11 October). These are ancestors of `astra/ff-merged`; there is no separate R7 runtime copy in the current tree.

The stack README is headed “round 7” but includes an R8 consolidation section. Its R6 figures are explicitly historical R6, and its R7 behaviour must be read with the snapshot and task-4 report. Current code under the same paths is R8. Read-only historical inspection can use `git show 52cee3b:prototypes/fast_lines/stack/pipeline.py`; checking out or executing it is not part of this document.

## Small detector and conditional corrections

The base `prototypes/fast_lines/shared/detector.py:Detector` uses the pinned local `.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx`, CPU ONNX Runtime, sequential execution and one intra/inter-op thread. Preprocessing converts grayscale to RGB, resizes with max long side 960, normalizes and creates NCHW float32. Its output is a text probability map; DB postprocessing supplies polygon candidates and scores, not a glyph census or measured font lines.

The adapter still has defaults `thresh=.2`, `box_thresh=.45`, `unclip_ratio=1.4`, `box_type='quad'`, `max_candidates=3000`. Source log places this adapter at `4e2199ddf5141760255e469fac00d88ed759c749` (10 October); R8 retained the model/map/postprocess contract. Poly/threshold expansion variants are experiments, not the default quad route.

`layout_barriers.fast.scout` is the materialized Q8 printed-rule path: it builds a reduced-resolution local-mean ink witness scaled by the provisional body height, identifies long narrow vertical runs crossed by multiple candidate rows, then nominates native corridors. `verify_rule` checks sustained native stroke support; `corridor_clear` checks paper flanks. `correct` clips accepted polygons against verified slanted rules, preserving shape instead of replacing them with arbitrary axis-aligned boxes. It does not certify missing-text recall, foreground ownership or a clean page. Its current header explicitly receives pixels and Paddle items only, not page names or cohort labels.

By R7, `Stack` was one file-to-lines entry point with a warm detector. The documented order was Paddle → Q8 scout/correction → ink removals → edge scout → conditional early curved-rule/column cuts and shared field → remaining geometry/fragment joins → type/grid/native recovery and initial completion → envelopes → faintness → conditional second field selection → row splitting/duplicate audit → changed-footprint faintness. It retained original Paddle `source_ids`; new type rows carried slot provenance. Polygons were the output authority and baselines stayed null. Original/removed/added items, decisions and per-stage timings supplied review evidence (`prototypes/fast_lines/stack/README.md`).

The row model/residual-parent route and switches failed and were removed in R7 task 4. `Stack(bend=True)` remained an isolated opt-in experiment; the accepted default retained the R6 field and task-3 whole-nontext removals. The near-affine column-skip speed experiment was rejected after a clipped rho descender. This lineage already had splitting, columns, skew and bend mechanisms; R8 did not introduce all these concerns for the first time.

## The earlier Q7 graph is a different execution surface

The Q7 research runner is `python -m prototypes.fast_lines.run`, dispatched by `run.py` into `workflow.py`. Its source-defined study order is:

`native_contours → layout_barriers → font_guides → local_ribbons → sheet_lattice → foreground_profiles → image_motifs → ink_condition → residual_ledger → map_graph → classical_residual → selective_rerun`.

These are twelve experiments with shared context/primitives and saved dependencies. Standalone studies start from the same detector baseline; their topological evidence is not twelve successive edits to the same final line list. `workflow.compose` actually runs a fresh detector and shared scout, then `layout_barriers` and `local_ribbons`; it selects supported layout changes, otherwise local ribbons, while leaving unresolved scout evidence explicit. It does not apply all twelve competing repairs in succession. Parked orientation remains unchanged.

Q7's `shared.manifest.build` enumerated 174 pages: 54 development + 80 disagreement + 40 supplied agreement, with an orientation-parked page. Shared baseline/maps/registry/reference evidence lived under `.astra/fast_lines/out/shared/`; composition under `.astra/fast_lines/out/composition/`. Later Q8 rule-separator studies used 195 pages. R7 stack benchmarking used the later 208-page cohort (195 + 13 supplied). These populations must not be merged into one timing or quality claim.

The root prototype README's `run compose` and historical phase commands reproduce that experiment graph, **not** `Stack`. Its dense references-v1/reference outputs are comparisons with known failures, not physical truth. Historical experiment receipts include source/config identities and cache hits; changing a source/dependency creates a different experiment, not a silent replay of the frozen result.

## What remains live inside R8

| R7 lineage | Current R8 use | Revision / limit |
| --- | --- | --- |
| Small detector and DB adapter | `Stack` still invokes `Detector.infer` and `postprocess` | Model/map/postprocessing retained; numerical/physical consolidation is downstream. |
| Q8 barrier scout/correct | First correction stage in `stack/pipeline.py` | Native rule/column evidence still constrains later ownership; not a complete line detector alone. |
| Geometry context, feature rules, columns, fragment joining | Composed by `stack/geometry.py` | Shared observations and repeated work reduced; multiple row/path authorities remain. |
| Ink ownership, motifs, seals, solid/discrete removals | `features_ink.pipeline.ink_run` plus final faintness/frame checks | Six copied type-ink modules now use shared providers; M06 propagation removed, own reflected-glyph votes retained. |
| Type/context/residual recovery | `shared.type_extended.recover` | R8 gained one body row but not its full curled ending. |
| Field, envelopes and final duplicate reconciliation | Early field selection, remaining envelopes, later row/ownership passes | Narrow certified native-child changes; full font/curl/shared-band construction remains partial. |
| Call-local polygon memo and field dependencies | Retained in compose | Later removed observation-cache wrappers are a different cache; no cross-page policy reuse is implied. |

The accepted R8 audit's mask delta from R7 is narrow: 205/208 pages unchanged; six improved lines on three pages, one net new item; all exclusion masks unchanged. Remaining duplicates, tight contours and curled-end loss prevent describing the revision as a completed physical replacement. The R8 addendum also records metadata changes on 33 items/10 pages, so crop equality is not full-export equality.

## Outputs, tests and historical evidence

R7 evidence root is local `.astra/fast_lines/out/stack/r7/` in the historical owning worktree. The stack README names `TIMING.md`, `COMMENTS.md` (104 original comments), `ROWS.md` (256 marked segments), native context crops and retention/exclusion ledgers. These paths are evidence references; their local images were not opened by this documentation run. R6 `RECOVERY.md` and `DUPLICATES.md` describe earlier regressions and an audit losing 27 boundary ink pixels on three pages; they do not become R7 successes by being linked from the same README.

The stack benchmark separates startup, decode, primary detector and correction time; serialization/rendering are outside the timer. On the historical Mac, a positive OpenCV two-thread request yielded ten observed GCD workers; no two-worker guarantee follows. R7/R6 timing records are not R8 timings. R8 final-source cost is descriptive because detector/load drift invalidated causal comparison.

Tests include `prototypes/fast_lines/stack/test_r7.py`, earlier stack tests, `features_ink/test_round7.py`, and the shared/geometry/type suites. They live outside default pytest testpaths. Documented commands, not run here:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider prototypes/fast_lines
```

The current invocation tests the current integrated R8 source. Historical R7 testing requires the named historical source/environment and available evidence fixtures; a current pass cannot be assigned retroactively to R7. See `NEXT_GEN_R8.md` for the present 41-file inventory and audit receipts.

## Sources read

- `docs/cleanup_20261019/OWNER_BRIEF.md`, `docs/cleanup_20261019/PLAN.md`.
- `docs/records/research/round8/MODEL_GENERATIONS.md`, `docs/A_ocr_development/reference/LINE_SEGMENTATION.md`, `docs/A_ocr_development/reference/LINE_SEGMENTATION_TESTS.md`.
- `docs/records/research/round8/{AUDIT,AUDIT_COST,AUDIT_CHECK_ADDENDUM,OWNER_CLOSING_SUMMARY}.md`.
- `prototypes/fast_lines/README.md`, `prototypes/fast_lines/stack/README.md`, `prototypes/fast_lines/stack/{pipeline,geometry}.py`.
- `prototypes/fast_lines/shared/{detector,manifest}.py`, `prototypes/fast_lines/layout_barriers/fast.py`, `prototypes/fast_lines/features_ink/pipeline.py`, `prototypes/fast_lines/shared/type_extended.py`.
- `prototypes/fast_lines/{run,workflow}.py`, `prototypes/fast_lines/evidence/__main__.py`, `pyproject.toml`; prototype test-file inventory.
- Read-only Git log/show for `4e2199ddf`, `932027e21`, `52cee3b`, `astra/ff-merged`, and ancestry listing for the R7 implementation commit.
