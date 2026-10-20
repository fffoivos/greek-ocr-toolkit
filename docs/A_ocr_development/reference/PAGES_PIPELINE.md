# Page processing pipeline

This is the original explicit pixel-model pipeline (generation 1). The [line-segmentation map](LINE_SEGMENTATION.md) identifies the separate Paddle-based fast route and the current revision.

The pipeline turns image pixels into fitted text bands, safe recognition pieces
and optional descriptive measurements. Crop fitting remains the established
`greekocr.glyphs` implementation. Q3 reorganises its page-level callers; it does
not change the meaning of x-height, fit a new model or tune a page-specific rule.

## Order and boundaries

| Stage | Input | Work | Output / owner |
| --- | --- | --- | --- |
| Input | Pillow image, NumPy array or image path | Validate image values, key and page extent | Original raster; `pages.api` |
| Layout, when tables are enabled | Raster or supplied Docling regions | Find image-layout table/document-index proposals | `(id, pixel box)` regions; `pages.layout` |
| Pixel preparation | Original grayscale pixels | Local threshold, component evidence, graphical stops, persistent gutters, rough row seeds | `PixelPage`; `pages.pixels` |
| Crop fitting | Seed pixels and scale estimates | Discover body bands, recover supported rows, pool nearby geometry, assign ink, refine contacts | Fitted models; `pages.lines` calling `glyphs.components` and `glyphs.baseline` |
| Font guides and bounds | Fitted models and assigned ink | Fit six class-conditioned guides, discount nontext, bound neighbours and order lines | `LineSegment` curves and diagnostics; `pages.font`, `pages.lines` |
| Table delivery | Normal segmentation, original image and layout regions | Remove table strokes before labeling, recover pieces, refit bounded prose between tables | Addressed segmentation and `TextPiece` list; `pages.tables` |
| Structure | Lines, pieces and original pixels | Validate rule/gutter evidence; assign physical leaves, columns, blocks, rows, piece order and neighbours | Structure dictionary; `pages.boundaries`, `pages.structure` |
| Data selection | Addressed candidates | Keep diagnostic lines or remove them and remap indices | Selected data view; `pages.api` |
| Orientation, opt-in | Original image, table bounds and existing segmentation | Run the parked directional hypotheses and local upright fits | Words, transforms, corners, evidence; `glyphs.oriented_page` |
| Joining, opt-in | Addressed records and validated boundaries | Copy samples and interpolate only safe gaps inside a row | Safe delivery records, explicit refusals and row joinability; `pages.structure` |
| Statistics, opt-in | Original image and selected, unjoined Q1 records | Measure bodies, marks, residual ink, coverage and candidate provenance | Glyph rows and page summaries; `pages.statistics` |
| Book aggregation | Ordered page measurements from one book | Group font sizes; build independent references excluding each target page | Enriched pages, book summary and corpus summary; `pages.statistics` |
| Serialization, opt-in | Typed result and source image | Write selected data files and review images | Paths in `result.files`; `pages.outputs`, `pages.render` |

Structure is attached when ordinary segmentation is built and attached again
after table delivery, because table recovery changes the piece inventory.
Statistics never edits the fitted curves. Joining does not change the glyph
measurement denominator. Discounted lines never enter rendered review layers.

## How Docling fits

The detector path uses this order:

1. Docling renders the page and supplies image-layout regions **before OCR**.
2. Our detector and page API prepare geometry and table-aware recognition pieces.
3. Our recognizer reads each piece separately. Recognized strings are never split
   in proportion to box width.
4. The plugin installs OCR text cells in actual page units and clears stale native
   words and characters that would otherwise take precedence over the new cells.
5. Docling's table step consumes the layout regions and OCR cells to form a grid.
6. Docling assembles the document's text, tables and other layout items.

The plugin itself is an OCR model; it consumes existing page predictions and does
not schedule Docling's other stages. The enclosing Docling pipeline must make its
layout predictions available before invoking the detector path. Python callers
can supply a layout provider or use the local-model adapter. Text-layer mode is a
separate compatibility mode, not a source of reference truth for the detector.

A detector piece-group ID is not a TableFormer grid-cell ID. The table recognizer
and document assembler own semantic table structure. The standalone page API
returns geometry and measurement data; it does not assemble a Docling document.

## Coordinate systems

All ordinary curves have one source-pixel Y sample for every integer X from
`x0` through `x1 - 1`. The origin is top-left, X points right, Y points down, and
box right/bottom edges are exclusive. Segment provenance and neighbour arrays
retain their original index spaces.

X-height is the local fitted small-letter height. Geometric thresholds use
multiples of x-height or fractions of image width/height. Integer pixel floors
exist where a raster operation cannot use a subpixel kernel; these are sampling
constraints, not an assumed scan DPI. Photometric ratios, confidence gates,
counts and slope limits have their own units. Q2's measurement thresholds are
also serialized with each statistics table.

The page-unit box conversion is `x * page_width / image_width` and
`y * page_height / image_height`. Review PNGs historically use three pixels per
research page unit; that convention is confined to the layout reader and legacy
review wrapper. The public API defaults to image-pixel units.

An oriented word stores a local coordinate frame, its inverse transform, the
four corners and parametric guides. Its local line index belongs to the local
orientation segmentation; it is not an index into the result's original-frame
horizontal line list. Unknown orientation is not silently promoted to a decision.

## Compatibility and reproducibility

`greekocr.glyphs.page_text_lines`, `pixel_segments`, `page_font`, `table_lines`,
`line_structure`, `boundary_evidence` and `statistics` resolve to their new page
modules. Crop modules, including `components.py`, retain their public imports.
The legacy review renderer now uses `process_page` and the shared renderer.
`build_statistics.py` remains useful for measuring frozen geometry without
rerunning detection. Historical round/audit generators are in
`scripts/glyphs/archive/`; committed reports point to their new locations.

The Q2 committed implementation and its frozen review artifacts are different
reference surfaces: audit scripts added fields and reprocessed boundary
proposals. The Q3 report records exact comparisons against both, including
failures. A new run's timing and implementation hash are not historical receipts.
