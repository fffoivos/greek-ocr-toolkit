# A.i — slow pixel-first page segmenter

Documentation for `docs/A_ocr_development/segmenters/SLOW_PIXEL.md`. Source snapshot: `cleanup/20261019`, `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33`, inspected 19 October 2026. Generation 1 is an explicit pixel construction, not the small Paddle detector. The public page API prepares geometry and recognition pieces; recognition is a later consumer.

## Entry points and contracts

`greekocr.pages.process_page(image, *, options=PageOptions(), page_key=None, book_id=None, table_regions=None, layout_provider=None, page_size=None, recognizer=None)` accepts a Pillow image, grayscale/RGB NumPy array, or image filename. Arrays accept 0–255 or 0–1 values. The default key is a filename stem or `page`; physical/page-unit extent defaults to raster `(width, height)`. Source geometry remains in pixels regardless of page units.

`greekocr.pages.lines.segment_page(page, hints=None)` is the lower-level pixel-only line builder. It returns `PageSegmentation`: candidate `LineSegment` objects, rough pixel segments, x-height, diagnostics, pixel evidence and attached structure. `page_line_segments` filters out discounted candidates for OCR. Optional hints must be finite positive-area N×4 rectangles; they annotate provenance, not discovery, splits, fits or final geometry. Hint text is not an input.

`process_page` returns `PageResult` with fitted line records, `TextPiece` recognition pieces, delivery records, table regions, structure through the segmentation, optional orientation/statistics, and written-file paths. It does not transcribe an ordinary page. `recognizer=` supports the optional orientation polarity check. `process_book` preserves the caller's order for images or compatible precomputed `PageResult` objects from one book; it aggregates statistics and outputs. Precomputed results must already have statistics and matching book identity. Book references exclude the target page; a one-page book has no independent book reference (`greekocr/pages/api.py`, `docs/A_ocr_development/reference/PAGES_GUIDE.md`).

## Actual stage order

1. **Validate and obtain layout if requested.** `pages.api` loads the image, validates grayscale conversion and positive finite page size. With tables enabled, it accepts supplied pixel boxes or a callable layout provider, otherwise calls the local Docling layout adapter. Supplying layout when tables are disabled, or supplying both regions and provider, fails. Layout proposes table/document-index regions; it does not provide line truth.
2. **Prepare pixel evidence.** `pages.pixels.prepare_pixels` locally binarizes grayscale, labels eight-connected ink and estimates x-height from substantial components. It separates strong/faint support before relabeling, protecting plausible letter stems from rule masking. Graphical masses, scan borders/frames, slanted near-vertical rules, continued rule paths and persistent gutters constrain clean text. Horizontal zones and row-ink valleys form rough regions. Original grayscale/ink remain available; an empty or flat image produces empty evidence.
3. **Discover and recover rows.** In `pages.lines.segment_page`, `_discover` uses the existing crop fitter inside rough pixel regions, repeatedly peeling explained ink while preserving paper tone and a stable contrast reference. `_recover_bodies` recovers supported bodies; `_merge` joins compatible seeds, then `_reject_residual_bands` rejects weak residuals near established rows. Faintness is measured against page support, not promoted by repeatedly whitening a working crop.
4. **Share geometry before assigning ink.** `_lanes` supplies provisional lanes; `_pool_geometry` pools supported neighbouring skew/curvature. A second `_merge` joins pieces aligned by pooling. `_assign` associates native components with row models independently of original seed rectangles; `_refine_bottom_contacts` refines support, then assignment runs again. Short rows can borrow geometry without losing their distinct positions.
5. **Build complete extents and font evidence.** `_make_lines` follows owned components to actual barriers; `_coalesce_lines` joins compatible fragments. `_split_contrast_runs` and `_line_contrast` handle photometric differences. `pages.font.fit_guides` classifies body, tall-letter, descender, detached/fused marks and punctuation contacts, then fits one shape with six guide offsets: font top, meanline, baseline, font bottom and accent top/bottom. Missing classes borrow measured ratios from comparable sizes, otherwise defaults; records disclose borrowing. All-caps lines measure capital support and borrow an unsupported meanline.
6. **Discount, order and bound rows.** `_discount_nontext`, `_final_columns`, `_reading_order`, `_boundaries`, and `_addresses` run in that order. Shared neighbour seams start from facing guides and are constrained by native ink and finite graphical boundaries. Longer neighbours can carry a seam past a short line end. Rough seed boxes become provenance. Diagnostics count failures rather than certify perfect tessellation. `_attach_structure` attaches physical leaf, column, block, row, piece order and neighbour relationships.
7. **Prepare table delivery.** `pages.tables.prepare_delivery` consumes the original raster, segmentation and layout regions, removes table strokes before labeling, recovers bounded pieces and refits prose between tables. It updates structure after changing the inventory. No proposed table means the original ordinary segmentation is retained; the conservative repeated-ruled-block fallback is enabled only with tables. A provisional `cell_id` is not a Docling grid-cell identity.
8. **Select data, then optional consumers.** `discounted='drop'` compacts/remaps candidate, piece, structure and neighbour indices. Orientation runs next if enabled. Joining then selects safe delivery rows/pieces; statistics measure the selected **unjoined** fitted records and original image. Serialization is last, and only occurs with an output directory. Book aggregation operates on ordered measurements.

This order is the source order in `greekocr/pages/lines.py:segment_page` and `greekocr/pages/api.py:process_page`; `docs/A_ocr_development/reference/PAGES_PIPELINE.md` supplies the wider contracts. The crop primitives remain `greekocr/glyphs/components.py` (`binarise`, `line_glyphs`, body tracking/curves and component evidence) and `greekocr/glyphs/baseline.py` (`text_lines`, guide/skew/cut observations). `glyphs.letters`, `columns`, `lines_api`, `ink`, `readability` and `recut` are related crop tools, not extra page-detector generations.

## Parameters, coordinates and outputs

| Setting | Default / meaning |
| --- | --- |
| `tables`, `orientation`, `join_lines`, `statistics` | All `False` in `PageOptions`. Each selects a separate optional stage. |
| `granularity` | `default`; `rows`/`pieces` require `join_lines=True`. Default joining delivers whole ordinary rows and separate table pieces. |
| `discounted` | `keep`: retain rejected candidates and reasons in data. Both keep/drop exclude them from recognition and rendered review layers. |
| `strict_geometry` | `False`: diagnostic invalid ribbons may remain. `True` rejects nonfinite or nonpositive active top/bottom samples with `invalid_line_geometry` before table delivery. |
| `OutputOptions.directory` | `None`: no persistent artifacts. With a directory, default files are lines, segments, structure, cells and checks. Unknown switches fail. |
| `extract_line_image(..., xheight=32)` / `LineSegment.unroll` | Normalizes varying x-height using original grayscale pixels. Default output height 128, meanline row 48, baseline row 80. |
| Scale and stops | Geometric thresholds use x-height or page fractions, with raster floors. Compatible fragments can span word spaces; a gap over ten x-heights stops joining, not an ordinary three-x-height word gap. |

Curves store one sample per integer X in `[x0, x1)`; Y increases downward, right/bottom box edges are exclusive. `baseline`, `font_top`, `meanline`, `font_bottom`, `accent_top`, `accent_bottom`, `top`, `bottom` are source-pixel curves. `borrowed`, `ink_classes`, `guide_residuals`, `contrast`, `discounted`, `segment_indices`, `segment_positions` and `hint_indices` retain evidence/provenance. Above/below neighbour arrays use final line indices and `-1` for none; scalar horizontal neighbours and piece/cell index spaces must not be interchanged (`docs/A_ocr_development/reference/PAGE_LINE_SEGMENTS.md`).

Page-unit conversion independently uses `page_width/image_width` and `page_height/image_height`. The old research frame of PNG pixels/3 must be requested explicitly; requested PDF render scale is not a substitute for measured dimensions.

Selected outputs include lines/segments/structure/cells/checks, delivery/rows, statistics/glyph tables, orientation, and independent line/unrolled/structure/glyph/book images. `rows` output requires rows granularity; statistics/orientation outputs require those computations. Parquet requires `pyarrow`, otherwise glyph tables use JSONL. Filenames use page keys and overwrite the selected destination on rerun (`pages/options.py`, `docs/A_ocr_development/reference/PAGES_GUIDE.md`). The legacy renderer records `.astra/out/<key>.{segments,lines,checks}.json`, `.lines.jpg`, `.unrolled.jpg`, structure/cell files and aggregate checks with image/implementation hashes. These are historical artifact paths, not files generated by this document.

Safe joining copies original samples and interpolates only gaps. It refuses incompatible addresses, crossing geometry and detected boundaries. The public API records `blocked_rows` and `complete=False`, allowing other safe rows to remain; direct low-level unsafe joins raise. Statistics never alter fitted curves, and joining never changes their measurement denominator.

## Known failures and limits

`docs/records/research/round8/MODEL_GENERATIONS.md` records saved 23-page slow runs in local worktree `greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/slow/` and a coordinator G1 check. Reported successes include several curled ends, 77d1's 39 rows and e259 leaf separation; reported failures include slivers, a misregistered 4959 row, a dropped Ψ initial, small end clips and a disputed apostrophe assignment. This document reads the repository record, not those native images, and treats none of these assignments as ground truth.

`docs/A_ocr_development/reference/PAGE_LINE_SEGMENTS.md` discloses no independent full-page line truth for its 48 scans. Owned-ink retention is not text recall. Cut diagnostics test assigned source ink and actual delivered raster edges; foreign-ink counts use the implementation's ownership; undetected barriers cannot enter crossing counts. A high retention/equality score can preserve missing rows, wrong ownership, stamps or wrong marks. Table recovery and lane/fold heuristics retain omissions, crossings and model-structure failures.

`docs/records/glyphs/GLYPHS_CALIBRATION.md` is an 8 October crop/readability study, not page-segmentation qualification or the current B filter policy. Its CP-G4 corrections retract E1 cut/skew limits, qualify in-sample straightening, and identify a mismatch between support-averaged calibration and production per-X cut policy. Crop-only blank accent gaps and neighbour fragments can defeat cut detection. CLLG thresholds describe those synthetic Didot-like texts/readers; they are not universal OCR limits. `GLYPHS_PLAN.md` and `GLYPHS_STATE.json` retain earlier plans/counts, not current release state.

The Q3 report `docs/records/reviews/PAGE_LINES_Q3_CLEANUP_API.md` says its strict frozen-output gate was NOT DONE with recorded differences. API/equality unit tests are not evidence that this historical acceptance gate later passed.

## Parked and experimental paths

- Orientation is opt-in and parked: `PageOptions(orientation=True)` calls `glyphs.oriented_page`, retains horizontal geometry, and adds local frames/transforms/corners. Unknown polarity stays unknown; local line indices do not index the original horizontal list.
- `greekocr/pages/torch_prototypes.py` explicitly is never imported by the production page API. `TorchArrays(device='cpu'|'mps'|'cuda', batch_size=16)` contains bounded morphology/fit/resampling experiments, imports torch only on construction, and refuses silent device fallback. Float32 fitting/resampling is not an exact default replacement. `scripts/pages/benchmark_q5.py` is the referenced experiment harness.
- Optional Docling table layout is separate from pixel-only `segment_page`; no Paddle detector is introduced into generation 1 by enabling it.

## Source drift and lineage

Introduced as `glyphs/page_text_lines.py`/`pixel_segments.py` at `f405fe38bc19febc7600c61a49cca05740fde73d` (9 October), moved to `pages` at `bb06ee4ecd72d22a7bb53c0a082e396a6588c96e` (10 October), optimized at Q4 `76ad6fb4f513fb3eb99531cc553899976b4c8801`. Old imports alias the maintained page modules; box-guided ancestors remain compatibility code.

`docs/A_ocr_development/reference/PAGE_LINES_ALGORITHM.md` preserves the 8 October box-guided algorithm and status at `a5750e2`, followed by the owner's pixel-first direction. Its document-over-code sentence and old box-input contract are historical. **Current code wins here**: the public detector does not require recogniser/text-layer boxes.

`docs/A_ocr_development/reference/PAGE_LINE_SEGMENTS.md` also says discounted candidates remain in the saved review. The later page guide/pipeline explicitly exclude them from rendered review layers while retaining diagnostic data. Use the current keep/drop and rendering contract described above, rather than treating that older review sentence as current behaviour.

Read-only comparison in this documentation run confirms `pages/{lines,pixels,font}.py` and `glyphs/baseline.py` equal Q4. Contrary to the 12 October generation record's broader equality statement, `glyphs/components.py` now differs: commit `582cacb7fc77da695e738de65fef02317535b840` (19 October) adds `Band.curve_is_straight` and records whether a tracked curve is actually straight; degree 1 alone may describe a bent polyline. It is construction provenance used by B's curve measurement. This is not a new segmenter generation.

## Tests and reproduction scope

Commands below are documented only; no tests, renderer or pipeline ran for CLEAN5A. Use a configured environment with the package's dependencies and test extra.

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/glyphs tests/test_docling_contract.py tests/test_docling_tables.py tests/test_docling_orientation.py
```

`tests/glyphs/test_page_line_segments.py`, `test_page_lines_round3.py`, `test_page_lines_round4_nontable.py` cover line and controlled page cases; `test_pages_api.py` covers API/options/selection; `test_pages_equality.py` tests comparator exemptions/refusal, not a full frozen corpus. Structure, boundary, statistics, curl, orientation and Q4/Q5 numerical tests have separate files in the same directory. `tests/test_geometry_measure.py` and `tests/test_geometry_evaluate.py` cover related crop-evaluation contracts. Some evidence-dependent paths require local fixtures; a skip is not full-page qualification.

Usage examples, for a separately authorized execution:

```python
from greekocr.pages import PageOptions, process_page, process_book
result = process_page('page.png', options=PageOptions())  # in memory
book = process_book(['p1.png', 'p2.png'], book_id='one-book')
```

`python -m greekocr pages scans/ --out output/` is the CLI (`greekocr/pages/cli.py`); `--tables`, `--statistics`, `--join-lines`, `--granularity`, `--discounted`, `--strict-geometry`, `--page-size` and `--outputs` expose the documented switches. It orders PNG/JPEG/TIFF filenames lexically, takes one raster per file, and rejects duplicate stems before writing. Historical render/audit scripts in `docs/A_ocr_development/reference/PAGE_LINE_SEGMENTS.md` write artifacts and are not a documentation-validation step.

## Sources read

- `docs/cleanup_20261019/OWNER_BRIEF.md`, `docs/cleanup_20261019/PLAN.md`.
- `docs/A_ocr_development/reference/PAGES_GUIDE.md`, `docs/A_ocr_development/reference/PAGES_PIPELINE.md`, `docs/A_ocr_development/reference/PAGE_LINES_ALGORITHM.md`, `docs/A_ocr_development/reference/PAGE_LINE_SEGMENTS.md`.
- `docs/records/glyphs/GLYPHS_PLAN.md`, `docs/records/glyphs/GLYPHS_CALIBRATION.md`, `docs/records/glyphs/GLYPHS_STATE.json`, `docs/records/reviews/PAGE_LINES_Q3_CLEANUP_API.md`.
- `docs/A_ocr_development/reference/LINE_SEGMENTATION.md`, `docs/records/research/round8/MODEL_GENERATIONS.md`, `docs/harvest/line_pipeline/tool_versions.json`.
- `greekocr/pages/{api,options,lines,pixels,font,torch_prototypes}.py`, discounted-render filtering in `greekocr/pages/render.py`, `greekocr/glyphs/{components,baseline}.py`.
- `tests/glyphs/test_pages_equality.py`; test-file inventory under `tests/glyphs`; `pyproject.toml`.
- Read-only Git show/log for `f405fe38`, `bb06ee4`, `76ad6fb`, `3f75344e6`, `582cacb7f`; exact Q4/current byte comparison and `git diff 76ad6fb HEAD -- greekocr/glyphs/components.py`.
