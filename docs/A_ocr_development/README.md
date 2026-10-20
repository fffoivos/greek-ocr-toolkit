# A — OCR and segmenter development

## Reference guides

- Page API and records: [guide](reference/PAGES_GUIDE.md), [pipeline](reference/PAGES_PIPELINE.md), [output format](reference/PAGES_OUTPUT_FORMAT.md), [owner algorithm](reference/PAGE_LINES_ALGORITHM.md), [line segments](reference/PAGE_LINE_SEGMENTS.md).
- Segmenter lineage and qualification: [implementations](reference/LINE_SEGMENTATION.md), [method](reference/LINE_SEGMENTATION_METHOD.md), [tests](reference/LINE_SEGMENTATION_TESTS.md).
- Crop geometry and annotation: [O4D geometry](reference/O4D_GEOMETRY.md), [line metadata](reference/LINE_METADATA.md).

Documentation for `docs/A_ocr_development/README.md`, inspected 19 October 2026 on `cleanup/20261019` at `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33`. Paths below are repository-root paths unless identified as local evidence or another repository. This documentation run performed source/history inspection only; commands are usage examples, not new execution receipts.

## Scope and the boundary with B

Aspect A develops the mechanisms: finding printed lines, following page geometry, preparing recognition strips, recognizing text, converting donor weights, generating synthetic lines, importing experimental real-line data, and scoring predictions. Aspect B creates OCR training data: source acquisition and Google page reads, correction/filtering tools, their organizing line pipeline, and human revision/publication. This follows `docs/cleanup_20261019/OWNER_BRIEF.md` and the proposed mapping in `docs/cleanup_20261019/PLAN.md`.

The shared primitives do not collapse these scopes. `greekocr/glyphs/components.py` is crop geometry used by A and B; the B segmentation **filter** is not one of A's three page segmenter generations. The authoritative B manifest, `docs/harvest/line_pipeline/tool_versions.json`, names segmentation `0.13` (label `0.9-s5`), content gate `0.3`, polytonic `0.7`, Cyrillic `0.3`, numerics `0.3`, and dashes `0.1`. These are named tool generations, not R7/R8 or neural-model versions. B's owner-accepted segmentation state is `accepted_as_is`; this A documentation grants no tuning or pipeline work.

`greekocr/real` belongs to A's experimental extraction/import/geometry surface in the plan; the current harvest and correction orchestration belongs to B. `greekocr/deploy` is shared deployment infrastructure, covered here only where it serves the recogniser and page APIs. No code/import paths are moved by these documents.

## The three segmenters

Read [model generations](MODEL_GENERATIONS.md), [A.i — slow pixel segmenter](segmenters/SLOW_PIXEL.md), [A.ii — R8](segmenters/NEXT_GEN_R8.md) and [A.iii — R7 small detector](segmenters/SMALL_DETECTOR_R7.md). The other A surfaces are in [recogniser and training](RECOGNISER_AND_TRAINING.md); the [B process](../B_training_data/README.md) and [shared infrastructure](../shared/README.md) have separate homes.

Owner labels are taxonomy slots, **not chronological generation numbers**: (i) = generation 1; (iii) = generation 2; (ii) = generation 3. R8 revises the R7 stack and still uses its small Paddle detector; there are not three independently installed detector models.

| Name / owner label | Code entry point | Generation | State at inspected source | Latest relevant branch / commit | Documentation |
| --- | --- | --- | --- | --- | --- |
| Slow pixel-first page detector, A.i | `greekocr.pages.process_page`, `process_book`; `greekocr.pages.lines.segment_page` | 1 | Executable explicit physical construction and slow reference; known crop, ownership, table and equality limitations | Integrated in `cleanup/20261019`; core page modules match Q4 `76ad6fb4f513fb3eb99531cc553899976b4c8801`; latest `greekocr/pages` change `3f75344e63c80bcdaecda11a1029079c1cd702b4` adds opt-in torch experiments; shared crop provenance updated at `582cacb7fc77da695e738de65fef02317535b840` | This set: `segmenters/SLOW_PIXEL.md`; existing `docs/A_ocr_development/reference/PAGES_GUIDE.md`, `docs/A_ocr_development/reference/PAGES_PIPELINE.md`, `docs/A_ocr_development/reference/PAGE_LINE_SEGMENTS.md` |
| Next-generation fast stack, A.ii | `prototypes.fast_lines.stack.Stack`; `stack/pipeline.py:compose` | 3 / R8 | Current integrated prototype; accepted audit, broader architecture/physical/speed goals partial; Python, bend off, final export off | `astra/ff-merged` tip `cae93fb49ac1e2e9332fdd57a60f920e266ba1ba` (15 October); audited runtime `046bd52dddeea7ada7727971f1038d34328ba5b7`, audit delivery `2f1c91a09b844c87696b95b6c89cd5c3ff7beede`; integrated here | This set: `segmenters/NEXT_GEN_R8.md`; `docs/A_ocr_development/reference/LINE_SEGMENTATION{,_METHOD,_TESTS}.md`, `docs/records/research/round8/` |
| Small-detector plus heuristics stack, A.iii | Same `Stack` paths **at the R7 history snapshot**; `shared.detector.Detector`, `layout_barriers.fast` | 2 / R7 | Historical predecessor preserved inside the R8 lineage; not a second current copy | R7 implementation `932027e210debf0e63b152894d2bdd727770579b`; R7 review/merge baseline `52cee3bcc882e7426bdc1018d892cd9b1bf9feac` (11 October), ancestors of `astra/ff-merged` | This set: `segmenters/SMALL_DETECTOR_R7.md`, `MODEL_GENERATIONS.md`; existing stack README and round-7 reports |

The table distinguishes branch tips, runtime snapshots, and latest path changes. The root integration head is not a new detector release. `docs/records/research/round8/AUDIT_CHECK_ADDENDUM.md` supersedes older audit “pending” wording; physical completion remains partial.

## Recogniser, synthetic, real-data and scoring surfaces

| Code | Inputs → work → outputs | Limits / provenance |
| --- | --- | --- |
| `greekocr/recogniser` | Checkpoint + codec + ordered crops → named `labelfix`, `eval`, or `serve` backend → `Reading` objects, optional alignment/confidence; `align`, `transfer`, `AlignmentCache`, `run_shard`, `forbid_forward` | Phase-1 wrapper over frozen implementations; profiles preserve different preprocessing/decoding. Alignment windows are not physical glyph ownership. |
| `greekocr/warmstart` | Family R01/R02/R03 + local donor weights/config/revision + codec → exact mapping, classifier swap, provenance and independent endpoint parity APIs | Conversion is separate from native parity and training qualification; no fuzzy key matching. |
| `greekocr/synth` | Captured recipe v5/v7/v8 + existing `linefactory` binary + text pool → factory shards and verified `build_info.json`; manifest mix construction/validation | All synthetic training/evaluation data must come from linefactory sources. Registered recipe hashes come from `greekocr/_vendor/origins.json`; exact shard membership and role matter. |
| `greekocr/real` | Reviewed canonical-work partition + native sources/crops + optional independent readers → extraction/import records, adjudication, factory real shards; geometry measurements/evaluation | `extract_lines` is the older text-layer extraction API, not Google's page-reading pipeline. `import_real_shards` invokes `linefactory import-real` and verifies partition, shards and word-tag sidecar. |
| `greekocr/score` | Literal references/predictions or bake-off readings → edit distance/CER, marks/script diagnostics, summaries and readouts | `strict_cer` does not normalize inputs; `score_readings` canonically decomposes both sides to NFD. Instrument boundaries must remain explicit. |
| `scripts/train_line_font.py` → `greekocr.annotate.font.train_font_classifier` | Existing synthetic shards with known factory font IDs → NumPy CPU descriptors/centroids/radii → new JSON font-classifier model | Not the neural OCR trainer. Requires a fresh model path; distance/support is not calibrated real-scan accuracy. |
| `greekocr/_vendor/train/{train,model,data,mix,eval_cer}.py` | Bound mix, codec and run configuration → neural training/checkpoints and evaluation | Vendored implementation surface; E1–E4 experiment drivers/results belong to greek-page-ocr. |
| `greekocr/deploy/docling_plugin` | Docling rendered page/layout + local recogniser checkpoint/codec → OCR text cells through registered `glossapi` engine | Detector mode uses the slow page API; it does not select `Stack`. The plugin still calls its existing recognizer implementation directly. |

Read `RECOGNISER_AND_TRAINING.md` for API contracts, tests and the E1–E4 map. Synthetic page/glyph fixtures are controlled tests, not an alternative source of production synthetic training shards.

## Reading and evidence rules

Start with `MODEL_GENERATIONS.md`, then the segmenter document matching the intended entry point. For pixel APIs use `docs/A_ocr_development/reference/PAGES_GUIDE.md`; for fast runtime use `docs/A_ocr_development/reference/LINE_SEGMENTATION.md` and the R8 audit addendum, not the Q7 experiment runner. `python -m pytest` defaults to `tests/`; the 41 prototype pytest files need an explicit `prototypes/fast_lines` path.

Code and `docs/harvest/line_pipeline/tool_versions.json` take precedence over old descriptions. In particular, `docs/A_ocr_development/reference/PAGE_LINES_ALGORITHM.md` describes historical box-guided `recut.fix_page` and says the document overrides code; that historical sentence is not the precedence rule for this snapshot. Current `pages.lines.segment_page` starts from pixels. The 12 October generation record's equality statement for `glyphs/components.py` also predates the 19 October `curve_is_straight` addition. See the detailed documents for both discrepancies.

Historical evidence under `.astra/fast_lines/out/` is generally local to its named worktree. Counts and timings quoted here are attributed records, not fresh pipeline, inference or test runs. The 208-page development cohort, 23-page reference subset and coordinator-only private 44 are separate populations.

## Sources read

- `docs/cleanup_20261019/OWNER_BRIEF.md`, `docs/cleanup_20261019/PLAN.md`, `AGENTS.md`.
- `docs/harvest/line_pipeline/tool_versions.json`, `pyproject.toml`.
- `docs/A_ocr_development/reference/LINE_SEGMENTATION.md`, `docs/A_ocr_development/reference/LINE_SEGMENTATION_TESTS.md`, `docs/records/research/round8/MODEL_GENERATIONS.md`, `docs/records/research/round8/AUDIT_CHECK_ADDENDUM.md`.
- `docs/A_ocr_development/reference/PAGES_GUIDE.md`, `docs/A_ocr_development/reference/PAGES_PIPELINE.md`, `docs/A_ocr_development/reference/PAGE_LINES_ALGORITHM.md`, `docs/records/reviews/PAGE_LINES_Q3_CLEANUP_API.md`.
- `greekocr/pages/{api,options,lines,pixels,font,torch_prototypes}.py`, `greekocr/glyphs/{components,baseline}.py`.
- `prototypes/fast_lines/stack/{__init__,pipeline,__main__}.py`, `prototypes/fast_lines/stack/README.md`, `prototypes/fast_lines/shared/detector.py`.
- `greekocr/recogniser/{README.md,__init__.py,api.py}`, `greekocr/{synth,warmstart,score}/__init__.py`, `greekocr/real/{__init__,extract,importers,partition,adjudicate}.py`.
- `scripts/train_line_font.py`, `greekocr/annotate/font.py`, `greekocr/deploy/docling_plugin/{docling_plugin,options,model}.py`.
- Read-only Git log/show/diff for integration HEAD, `astra/ff-merged`, R7 `932027e21`/`52cee3b`, Q4 `76ad6fb`, page experiment `3f75344e6`, and crop provenance `582cacb7f`; filesystem enumeration of prototype test files.
