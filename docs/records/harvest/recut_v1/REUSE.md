# T6a reuse inventory — written before new implementation

Scope: F2 development and paired harm testing only. No W1 access or qualification (T6b). Network off. Existing defaults remain unchanged. Recorded before adding code, 2026-10-16 UTC.

## Existing functions and interfaces

| File:function | Existing job | T6a use and reason |
|---|---|---|
| `greekocr/glyphs/recut.py:fix_page` | Whole-page fit, optional splitting and outward repair | Inspected only; do not invoke because splitting and expansion violate T6a. Reuse its lower-level fit instead. |
| `greekocr/glyphs/recut.py:fit_box` | Fits the original box's own baseline and guide offsets | Direct reuse with `splits=False`; no new line is emitted. |
| `greekocr/glyphs/recut.py:_guide_offsets` | Reduces four fitted guide curves to rise/up/down offsets | Transitive reuse through `fit_box`, keeping the existing font-band definition. |
| `greekocr/glyphs/recut.py:LineFit.base_at` | Samples/continues the fitted baseline in page coordinates | Direct reuse for own-line curves and native component attribution. |
| `greekocr/glyphs/recut.py:_voronoi_keep` | Neighbour-bounded component-centroid ownership; only splits components touching two bodies | Reuse for ink-loss measurement, not to erase pixels in output. Retains detached marks whole where owned. |
| `greekocr/glyphs/baseline.py:text_lines` | Four guides: ascender, mean, baseline, descender | Transitive reuse through the existing fit; request no emitted split lines. |
| `greekocr/glyphs/columns.py:column_segments` | Existing font-band fitting per horizontal segment | Transitive reuse through `fit_box`; segments contribute one enclosing vertical envelope, never new crops. |
| `greekocr/glyphs/components.py:to_gray` | Native raster to grayscale array | Direct reuse for fitting and pixel measurements. |
| `greekocr/glyphs/components.py:binarise` | Existing foreground threshold | Direct reuse for component-pixel loss measurements. |
| `greekocr/glyphs/lines_api.py:straighten`, `separate_lines` | Baseline resampling / separating and normalising lines | Inspected, not called: output remains a literal native rectangular subarray with unchanged X. |
| `greekocr/glyphs/line_structure.py` → `greekocr/pages/structure.py:_copy_line`, `_combine` | Compatibility alias; preserves frozen source guide curves when copying/joining addressed records | Inspected only. The four traditional guides are baseline/meanline/font_top/font_bottom; current records also carry accent_top/accent_bottom and top/bottom envelopes. No joining/resegmentation in T6a. |
| `greekocr/glyphs/page_font.py` → `greekocr/pages/font.py:evidence`, `fit_guides` | Compatibility alias; component-class contacts and shared six-guide fitting | Inspected as page-runtime alternative. Not rerunning page segmentation or borrowing a neighbouring font as the own band. Existing F2 cache guides may be used only if uniquely matched. |
| `greekocr/pages:process_page` and page-lines runtime at `046bd52`, merged by `89c2817e` | Page detector, ownership, guide curves and ribbons; shared ink atlas | Source inspected. Reuse saved F2 G1b audit decisions for the clean subset, not a fresh detector run. Runtime equality is not physical ink truth. |
| F2 GR `sample_v1/gr/process.py:analyse_one` → `reference/p1/process_reads.py:one`; IA `sample_v1/ia/process_reads.py:one` | P1 cutter: native mapped Google line rectangle, pad 2 px (headings max(4, ceil(.12*height))), PIL crop | Reuse saved `crop_bbox` and native page rasters literally. GR rebinds the exact P1 roots; IA encodes the identical PNG in memory. Never reconstruct boxes from text. |
| `greekocr/harvest/montage.py:response_lines` (via `page_reads._response_geometry`) | Slices each Google line anchor and maps native geometry | Inspected to establish P1 custody; it does not interleave independently returned lines. |
| F2 `screen_v1/assembly_fix.py:page_tokens`, `spans`, `box`, `inverse_frame` | Saved Google token anchors and inverse provider transforms | Reuse the existing offline adapter to obtain native token boxes and line membership. Never import the provider/request runners. |
| `greek-page-ocr/bench/o4b_models.py:resize` (actual exported name checked in implementation) | Existing raw-crop real-data 48-pixel resize/letterbox | Reuse its existing crop preprocessing for both paired arms. |
| `greek-page-ocr/train/eval_cer.py:load_checkpoint`, `evaluate`; `train/data.py:collate_strips`; `train/cer.py:load_codec` | Safe model loading, strict NFD CER, width/halo padding and codec | Reuse the unchanged E3/E4 evaluation core on CPU. The full `evaluate_run` wrapper requires training-runtime equality and therefore cannot certify a CPU readout of CUDA training. Record this adapter boundary explicitly. |

The `sol/label-geometry` report was read using `git show`: owner inspection found 37/165 expanded crops worse (22%); `expand_vertical` failed acceptance. No expansion is reused.

## Exactly what is added

1. An opt-in `greekocr/glyphs/vertical_recut.py` callable accepting any native page raster, original crop boxes and native Google token geometry. It fits only existing boxes, never adds/splits/joins rows, and writes no input files.
2. A deterministic vertical rectangle: top is the minimum own fitted ascender/accent guide minus `top_margin_xh * xheight`; bottom is maximum own descender guide plus `bottom_margin_xh * xheight`. Initial dev grid is margins 0.10, 0.20, 0.30 xh (additional conservative margin only if documented before freeze).
3. Clip top to the bottom edge of the nearest overlapping-X Google neighbour tokens above, and bottom to the top edge of neighbour tokens below. Do not use another column's token boxes. Ambiguous/conflicting constraints abstain to the original.
4. Intersect the result with the original crop, rounding top down and bottom up to preserve native pixels; retain original left/right exactly. A failed/ambiguous fit returns the original. Parameter identity and source geometry remain fixed on a repeated application, making the operation idempotent.
5. Offline F2 binding, dev-grid component measurements and review witnesses, frozen canonical parameters/hash, paired CPU evaluator adapter with seeded paired bootstrap, per-source receipts, and cutter contract tests. Outputs stay under `docs/records/harvest/recut_v1/`, beside originals. No row is admitted here; all remain pending the owner's later blind gate.

Function counts in the final receipt distinguish direct/transitive computational reuse from inspected-only interfaces, and count named newly defined functions (including helpers/tests) separately.

### Pre-implementation clarification

The F2 caches already contain six fitted own-line guides and assigned-component labels. T6a will directly reuse these receipt-verified guides for each strictly unique recorded owner, rather than refit/segment those pages. The general API also supports `fit_box(splits=False)` when no prior guides exist. `strip` is the actual existing name in `bench/o4b_models.py`. A zero-own-component-loss guard will abstain to the original if the proposed rectangle loses supplied owned pixels; report proposed loss and guard refusals separately so a zero accepted loss is not portrayed as independent validation. Ambiguous ownership abstains. No mask is painted into the output.

Additional exact direct reuse for F2 measurement: frozen `reference/greekocr/labelfix/geometry/ownership.py:prepare_row` and `box_hits` (native assigned component coordinates), and `greekocr/ops/receipts.py:file_sha256`. Cache loading is read-only and verifies the existing receipt; `cache_page` is not called because a miss could write/rerun segmentation.

## Final execution accounting

The initially considered `_voronoi_keep`/binarisation route was not executed on F2: receipt-bound assigned-component coordinates (`prepare_row`, `box_hits`) give the existing ownership witness without resampling or introducing a second attribution. The fitted four-guide fallback is exercised by the arbitrary-page contract test; F2 itself uses saved six-guide font bands. This clarifies planned versus actual reuse above.

The 14 directly reused repository functions/methods are: `fit_box`, `LineFit.base_at`, `to_gray`, `file_sha256`, `prepare_row`, `box_hits`, `page_tokens`, `spans`, `strip`, `load_codec`, `load_checkpoint`, `load_safetensors`, `evaluate`, and `collate_strips`. Transitive functions and inspected-only alternatives are not added to this count. The new library has eight functions/methods (including dataclass validation, canonical serialization/hash and the changed property). The final line reports all 47 new named functions/methods across the cutter (8), F2 experiment driver (16), reporting (4), guarded commit helper (8), and tests/fixture (11); it does not hide harness functions in a library-only count.

## Reusing the frozen cutter on another native page

```python
from greekocr.glyphs.vertical_recut import TightenParams, tighten_page

# Load the exact params.json parameters; keep guide_box fixed across reapplications.
records = [dict(crop_bbox=original_box, guide_box=original_box,
                tokens=own_native_google_token_boxes)]
result = tighten_page(page_image, records, params=TightenParams(**frozen['params']))
# Each result is a proposal. Publish only to a distinct experimental output path.
recut_image = page_image.crop(result[0].new_box)
```

Pass all Google line records on the page to enable neighbour-token clipping. Optional `band=band_from_record(own_saved_row)` and `own_pixels=(native_y, native_x)` reuse a prior fit and enable the zero-loss guard, as in F2. Generic fitting without ownership is callable but does not inherit F2's component-preservation evidence or admit a row.
