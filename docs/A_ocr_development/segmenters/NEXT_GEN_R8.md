# A.ii — next-generation R8 fast stack

Documentation for `docs/A_ocr_development/segmenters/NEXT_GEN_R8.md`, inspected 19 October 2026 at integration head `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33` on `cleanup/20261019`. This is owner generation 3: a revision of the R7 small-detector stack, not a new independent neural detector.

`astra/ff-merged` currently resolves to `cae93fb49ac1e2e9332fdd57a60f920e266ba1ba` (15 October). The final audit binds runtime `046bd52dddeea7ada7727971f1038d34328ba5b7`; audit documents were delivered at `2f1c91a09b844c87696b95b6c89cd5c3ff7beede`. The dated correction `docs/records/research/round8/AUDIT_CHECK_ADDENDUM.md` records independent **ACCEPT WITH NOTES**, overriding the older audit/iteration handoff's pending-delivery wording. Audit completion does not complete the physical, architectural or speed goals.

Read-only `git diff 046bd52 HEAD -- prototypes/fast_lines` is empty in this integration: the checked prototype tree has not gained later runtime edits here. This verifies source continuity, not a new execution of the old audit.

## Inputs, detector base and public prototype interface

```python
from prototypes.fast_lines.stack import Stack
stack = Stack(image_threads=2, bend=False, final_export=False)
result = stack('page.png')
lines = result['items']
```

`Stack` in `prototypes/fast_lines/stack/pipeline.py` decodes an image file through OpenCV as grayscale and refuses undecodable files. It owns a warm reusable `shared.detector.Detector` session. It does not call `greekocr.pages.process_page`, train a model, read PDF text, or take recognized strings as a geometry reference. An explicit `parked=True` call returns original detections without corrections; cohort selection supplies that flag outside the algorithms.

`prototypes/fast_lines/shared/manifest.py` pins the local model path `.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx`. `shared/detector.py` uses ONNX Runtime `CPUExecutionProvider`, sequential execution, one intra-op and one inter-op thread. Grayscale is converted to RGB; `DetResizeForTest` limits the long side to 960 by default, then `NormalizeImage` and NCHW float32 feed inference. `infer` returns the text probability map plus preprocessing/inference, tensor/map-shape and scale metadata.

DB postprocessing from `shared/paddle_db.py` is invoked through `postprocess` with current defaults:

| Parameter | Default |
| --- | --- |
| `thresh` | `0.2` |
| `box_thresh` | `0.45` |
| `unclip_ratio` | `1.4` |
| `box_type` | `quad` |
| `max_candidates` | `3000` |

Map thresholding, contour scoring and polygon expansion yield source-pixel polygons, score and `baseline=None`. Poly/threshold variants exist for studies; they are not the `Stack()` baseline. The detector is the PP-OCRv6 **small detector**, distinct from PP-OCRv6 small **recogniser** donor R02. The package version `0.1.0` and B filter version `0.13` (label `0.9-s5`) do not version this model.

## Composition architecture and order

The operative chain is `stack/pipeline.py:compose`; `stack/geometry.py` composes shared geometry providers. A page-local geometry decorator memoizes identical polygon calculations within one call. Cached observations are reusable only when pixel region, scale, threshold and label provenance match. Geometry edits require fresh row/source/exclusion decisions.

| Order / concern | Actual producer and consumer | Output and constraint |
| --- | --- | --- |
| 1. Printed barriers | `layout_barriers.fast.scout`; conditional `correct` | Cheap witnesses nominate rules; native verification permits polygon-preserving cuts. `source_ids` retain original Paddle indices. |
| 2. Ink/source removal | `features_ink.pipeline.ink_run`, shared ink ownership/motif/seal/solid/discrete providers | Removes supported back-print/nontext and records each removal reason. Tone and glyph observations may be shared; classification/ownership policy is not made common merely by sharing samples. |
| 3. Shared field nomination | `shared.geometry_edge_map.scout` on the detector map/original items | If triggered, cheap `stack.geometry.cuts` establishes curved-rule/column boundaries first. With default bend off, `geometry_field_detector.run` proposes field rows and `geometry_field_selection.apply` claims supported rows early. |
| 4. Remaining geometry | `stack.geometry.run` → `geometry_scout`, `geometry_context`, `geometry_feature_rules`, `geometry_columns`, `geometry_fragment_correct` | Handles native geometry, finite columns/rules and fragment joining for remaining sources. Only intact originals substitute for original detector contours; cut fragments cannot inherit all their lost ink. |
| 5. Type and recovery | `shared.type_extended.recover` → inherited type context/recovery plus `type_residual_recovery` | Grid/native/residual candidates and bounded initial completion; exclusions/column evidence constrain recovery. It is geometry recovery, not character recognition. |
| 6. Envelopes and faintness | `shared.geometry_envelopes.correct`, `ink_footprints.Footprints`, `ink_faintness.analyze` | Fits final shapes, binds judged footprints, removes relative-faintness candidates on actual current polygons. |
| 7. Changed field selection | Conditional second `geometry_field_selection.apply` | Reuses the earlier proposal/native preparation if later polygons differ; does not silently rerun the detector or mesh. |
| 8. Row partition and extent | `shared.geometry_rows.analyze`, `confirmed_partition`, `whole_children`; `refresh_children` callback in compose | Accepted partitions may use certified whole-component native children; unsupported cases retain atomic vector fallback. Changed extents refresh source/motif/rule decisions. |
| 9. Final reconciliation | `shared.stack_ownership.reconcile`, followed by changed-footprint faintness and `ink_frame_field` | Audits duplicate/unique ink across the final row pool, rechecks changed polygons and applies final recurrent-frame exclusion. A constructor success may still fail at reconciliation. |
| 10. Optional export bands | `shared.geometry_bands.tessellate`, only with `final_export=True` | Explicit experiment; refreshes source/faintness and novel-content motif/rule/frame dependencies. Disabled in the default runtime. |

The field is shared geometry, but the audit still found multiple competing row/path, ink, size and ownership authorities. R8 is not yet one connected physical model with a single row/component definition. The desired construction is row assignment → class-conditioned font contacts/guides → shared page-edge geometry → facing-guide seam → complete native crop. The current native partition/whitespace repair does not fit the four font guides (`docs/A_ocr_development/reference/LINE_SEGMENTATION_METHOD.md`).

`bend=True` selects an alternative `geometry_bend`/`geometry_bend_edits` experiment. Default `bend=False` does **not** mean all field or curved-row work is disabled: the edge-triggered default field path above still runs. Python is the default numerical backend. Current Rust field arithmetic is explicitly selected and separately qualified; the old M17 Rust pilot is parked on another branch.

## Outputs, timing and CLI

The returned dictionary includes final `items`, `original`, `image_size`, `removed`, `added`, stage-specific geometry/ink/type/row/ownership evidence, correction `counts`, nested `stages`, and `timing`. Original `source_ids` are a lineage ledger, not current positional indices; newly recovered rows also retain type-slot provenance. Consumers use polygons; baselines remain null rather than fabricated measured font baselines.

`timing` separates decode, detector (inference plus DB work), corrections, Paddle file time, full file-to-final time, session startup and observed OpenCV threads. Startup is outside warm per-page time. The request `image_threads=2` does not guarantee two workers on macOS GCD; use observed receipts. ONNX settings are separate. Regional detector work inside recovery/field proposals is correction cost.

CLI entry `stack/__main__.py` delegates to offline `evidence/__main__.py`; importing `Stack` alone does not import the evidence tools. Example only, not run here:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m prototypes.fast_lines.stack page.png --output result.json
```

The CLI writes the established detector record (`unit: line`, size, polygons, null baselines, scores/provenance) plus timings/correction counts, or prints it. JSON serialization/review rendering are outside file-to-final timing. CLI image mode calls `Stack()` and does not expose bend/final-export switches.

The same CLI offers `benchmark`, `summary` and `review`. **Version prefixes affect cohort selection** in `evidence/__main__.py`: r6/r7 use the 208-page round-6 cohort, r5 uses round-5, other prefixes use the earlier round-2 manifest. Do not invent an `r8-*` benchmark label and assume it selects the audited full208 population. Exact R8 reproduction follows the source-bound audit/task runner and allowlist. The old `python -m prototypes.fast_lines.run compose` executes the historical Q7 graph, not this `Stack`.

## What round 8 retained, and what remains partial

The 15 October audit and its accepted addendum distinguish output, architecture, physical validity and cost:

- **Output:** relative to R7 `52cee3b`, 15,093 → 15,094 items; 205/208 development pages have identical final crop masks. Four R rows on 4959 p5, one lower B row on 3229 p2 and one recovered body row on 8686 p5 improved. Exclusion polygons/masks are identical on all 208. Export metadata additionally differs on 33 items/10 pages (`type_support_chains`); mask equality does not mean whole-export equality.
- **Remaining crop defects:** the six improved lines are not six clean final crops. An old 4959 neighbour still duplicates ink; 3229's lower outline is tight and its neighbour duplicates ink; 8686's recovered body still loses its raised curled end. The 4959 #107/#105 shared seam is a narrow success, not full-page tessellation. No complete curved ending was gained.
- **Architecture:** six copied `type_ink_*` modules (485 lines), unused observation-cache machinery, repeated kernels, M06 neighbour propagation and a second glyph-atlas input authority were removed. M06's own reflected-glyph votes remain. Competing physical definitions and seven row/path authorities remain; the addendum cautions that the inherited 6/9/9/7 count is not a fresh exhaustive census. Runtime grew net 920 lines versus R7.
- **Font and curl:** the FONT live guide adapter and mark refinement were withdrawn after native class/raster/reconcile failures. A73d147 is the lower track3/body77 grave, contradicting the earlier own-mark premise. Offline evidence/tests remain; FONT is parked. The from-scratch R8 model failed G1; the tight-Paddle-box slow adapter was an invalid input adaptation, not generation 1's actual pipeline.
- **Ink:** worker review covered 153 M35 removals on 34 pages, an independent sample 38/13, and auditor openings six removals/four pages. No confirmed current-leaf loss within those scopes is not proof of zero faint-text loss throughout 208. Strict faint-front failures and known retained ghosts remain.
- **Speed:** two final-source descriptive runs measured correction median/p95/max 264.4/1766.8/2735.1 ms and 264.6/1992.8/3311.6 ms; 29/32 pages crossed one second. Detector drift +5.674% exceeded the 5% comparison control, with substantial within-run load swings. These clocks establish no round-wide causal speed change. Agreement40 is not a verified-clean cohort. The exact Rust field batch was 9.3% slower; parity is not a speed gain.

`docs/records/research/round8/AUDIT_CHECK_ADDENDUM.md` closes the allocation at 22 used + 3 retired + 1 parked FONT, zero launchable slots. Shared-field crop bands, flat/no-curl and binding-side handling, and field resolution/pass experiments remain unallocated. The later nominated-edge direction in `OWNER_CLOSING_SUMMARY.md` is a proposed next step, not implemented completion. The detector contract checklist's narrow pass does not include a delivered detector Rust binding.

## Tests: 41 files outside default discovery

At this checkout, filesystem enumeration finds:

| Directory under `prototypes/fast_lines/` | `test_*.py` files | Typical scope |
| --- | ---: | --- |
| `features_geometry` | 17 | Rows, fields, finite domains, seams, whole children, curl, bend, smooth/final bands, font-class counterexamples |
| `features_ink` | 5 | Feature and R4–R7 ink cases |
| `features_type` | 4 | Recovery/completion and request separators |
| `shared` | 7 | Observations, provenance/atlas contracts, R8 ink and reuse |
| `stack` | 4 | Caller orchestration and R5/R6/R7 integration |
| `rust_field` | 1 | Numerical batches and actual render-through-certify consumer |
| `tests` | 3 | Earlier Q7/shared/round-2 controls |
| **Total** | **41** | Explicitly include this path; `pyproject.toml` has `testpaths = ["tests"]`. |

Documented invocation, **not executed for this document**:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider prototypes/fast_lines
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/glyphs
```

Use the report's configured environment and local dependencies: the detector imports ONNX Runtime; the package test extra alone does not list it. Native images, model assets and fixture-dependent controls are separate requirements. Python field tests collect without a Rust build; `FAST_LINES_FIELD_TEST_NATIVE=1` or `FAST_LINES_FIELD_BACKEND=rust` explicitly enables native comparisons and missing native support fails clearly. Expected failures pin unresolved physical claims and must not be recast as passes.

The audit reuses a source-bound 430 passed/15 strict-xfail worker/checker receipt; bare checkout 429 passed/one older image skip/15 xfails. It independently ran six focused Python render-through-certify fixtures. These counts are historical, not results of the enumeration or of a new suite run here. Unit/mock/numerical parity checks do not replace complete native crops or held-out qualification.

## Evidence locations and populations

Durable records: `docs/records/research/round8/{AUDIT.md,AUDIT.json,AUDIT_COST.md,AUDIT_MECHANISMS.json,AUDIT_OWNER_CASES.json,AUDIT_EVIDENCE.json,AUDIT_CHECK_ADDENDUM.md,OWNER_CLOSING_SUMMARY.md}`. Mechanism JSON has mixed list/JSON-string fields; automated consumers need normalization rather than assuming a uniform schema.

Local evidence is under `.astra/fast_lines/out/` in the owning worktree named by each record, including `round8/R8-01/slow/` for the original 23-page reference and `stack/r7/` for R7. `AUDIT_EVIDENCE.json` is the recorded inventory; it is not a promise those images are present here. The R8 roster identifies worker branches/worktrees. The 208 development pages are 195 plus 13 supplied review pages; the 23 pilots are a development subset; private44 belongs to the coordinator. No private inputs were inspected or run for this document. Historical 104 comments/256 marks keep original text, coordinates and identities; inherited verdicts are not new visual certification.

## Sources read

- `docs/cleanup_20261019/OWNER_BRIEF.md`, `docs/cleanup_20261019/PLAN.md`, `pyproject.toml`, `docs/harvest/line_pipeline/tool_versions.json`.
- `docs/A_ocr_development/reference/LINE_SEGMENTATION.md`, `docs/A_ocr_development/reference/LINE_SEGMENTATION_METHOD.md`, `docs/A_ocr_development/reference/LINE_SEGMENTATION_TESTS.md`.
- `docs/records/research/round8/{MODEL_GENERATIONS,AUDIT,AUDIT_COST,AUDIT_CHECK_ADDENDUM,OWNER_CLOSING_SUMMARY,ITERATION_HANDOFF}.md`; beginning of `ROSTER.json`.
- `prototypes/fast_lines/stack/{__init__,__main__,pipeline,geometry}.py`, `prototypes/fast_lines/stack/README.md`.
- `prototypes/fast_lines/shared/{detector,manifest}.py`, `prototypes/fast_lines/layout_barriers/fast.py`, `prototypes/fast_lines/features_ink/pipeline.py`, `prototypes/fast_lines/shared/type_extended.py`.
- `prototypes/fast_lines/evidence/__main__.py`, `prototypes/fast_lines/README.md`, `prototypes/fast_lines/{run,workflow}.py`.
- `prototypes/fast_lines/rust_field/test_field.py`; strict-xfail declarations in `features_geometry/test_native_font_contract.py`; filesystem enumeration of all 41 prototype pytest files.
- Read-only Git identities for `astra/ff-merged`, `046bd52`, `52cee3b`, `932027e21`, and empty `046bd52`-to-HEAD prototype diff; no new runtime/evidence execution.
