# Working with page images

Use `greekocr.pages.process_page` for one image and `process_book` for an ordered
collection from one book. They find text geometry and prepare recognition pieces.
They do not read a PDF text layer or treat another OCR system as a reference.
The Docling plugin adds recognition and installs the resulting text cells.

From the checkout, install with `python -m pip install -e .` in your environment.
Install `pyarrow` for Parquet output; without it, statistics use JSONL. Computed
layout and the plugin require the `docling` extra (`pip install -e '.[docling]'`)
and locally available model weights. Supplied layout boxes need neither a
Docling model download nor a layout prediction. From the checkout,
`python -m greekocr pages` is also available in place of `greekocr pages`.

```python
from PIL import Image
from greekocr.pages import PageOptions, OutputOptions, process_page, process_book

image = Image.open("page.png")
result = process_page(image, page_key="page-1")
print(len(result.lines), len(result.pieces))
```

An image can be a Pillow image, a grayscale/RGB NumPy array, or a filename.
Arrays may use either 0–255 or 0–1 values. A filename supplies the default page
key; an in-memory image defaults to `page`. Use unique page keys when writing.
No output directory means no persistent artifact writes.

## Choose the work

`PageOptions` is immutable. Each call starts with these settings:

| Option | Default | Meaning |
| --- | --- | --- |
| `tables` | `False` | Recover boundary-safe pieces inside layout table proposals. |
| `orientation` | `False` | Run the parked experimental local orientation path. |
| `join_lines` | `False` | Use Q1's guarded joining for the `delivery` records. |
| `granularity` | `"default"` | With joining: ordinary rows and separate table pieces. |
| `statistics` | `False` | Measure Q2 glyphs and descriptive page statistics. |
| `discounted` | `"keep"` | Retain diagnostic lines in data; they are never drawn or delivered. |
| `strict_geometry` | `False` | Reject an invalid active line ribbon instead of retaining Q2 diagnostic geometry. |
| `outputs` | `OutputOptions()` | Select an output directory and files; default is in-memory only. |

### Tables: supplied or computed layout

Supply `(id, [left, top, right, bottom])` proposals in the **input image's pixels**:

```python
options = PageOptions(tables=True)
result = process_page(image, options=options,
                      table_regions=[("table-0", (20, 100, 780, 950))])
```

An explicit empty list means layout found no tables; the existing conservative
pixel fallback may still propose repeated ruled blocks. With `tables=False`,
that fallback is disabled. Supplying layout while tables are disabled is an error.

To read the development layout format:

```python
from greekocr.pages.layout import read_layout
regions = read_layout("layout/page-1.json", image.size)
result = process_page(image, options=PageOptions(tables=True), table_regions=regions)
```

The old `retained` layout format stores page-unit boxes. `read_layout` uses its
`page_size`, or the research convention of three PNG pixels per page unit when
that size is absent. A list of `id`/`box_pixels` objects needs no conversion.

When neither proposals nor a provider are supplied, the API runs Docling's
image-only layout model. Install the `docling` extra and stage its Heron model
in the local Hugging Face cache first. This adapter requires an existing local
snapshot and does not download weights. You can supply your own callable instead:

```python
def layout(image):
    return [("table-0", (20, 100, 780, 950))]
result = process_page(image, options=PageOptions(tables=True), layout_provider=layout)
```

Layout supplies regions, not semantic cell identities. The detector's `cell_id`
is a provisional piece-group identifier; Docling's later table stage assigns
its own grid rows and columns. Recognition operates on each piece independently.

### Orientation

```python
result = process_page(image, options=PageOptions(orientation=True))
words = result.orientation.words
```

Orientation is parked and opt-in. Unknown polarity remains unknown. The result
keeps the original horizontal geometry and adds local-frame word hypotheses;
use each word's transforms and corners, not a page-wide `y(x)` approximation for
vertical text. The optional `recognizer=` argument supplies the existing polarity
check. It does not turn ordinary page analysis into a full transcription call.
For transcription use the Docling plugin with its checkpoint and codec.

### Joining and delivery granularity

```python
result = process_page(image, options=PageOptions(join_lines=True))
rows = process_page(image, options=PageOptions(join_lines=True, granularity="rows"))
pieces = process_page(image, options=PageOptions(join_lines=True, granularity="pieces"))
```

`result.lines` always contains the fitted records. `result.pieces` contains the
recognition pieces. `result.delivery` is the requested view:

- Joining off: active fitted line records in detector order.
- `default`: whole ordinary rows; separate table pieces, in Q1 reading order.
- `rows`: join pieces sharing a page side, column, block and row.
- `pieces`: retain every piece separately, in Q1 reading order.

Joined records preserve every original sample and interpolate only gaps. Their
`pieces` field keeps the source records. A boundary crossing or incompatible
address raises `ValueError`, as the original Q1 joining function does. Request
`pieces` to inspect a page whose whole-row delivery is rejected. Joining changes
delivery; it does not refit geometry or change the statistics input.

### Statistics

```python
result = process_page(image, page_key="page-1", book_id="book-1",
                      options=PageOptions(statistics=True))
glyph_rows = result.glyphs
summary = result.statistics["stats"]["summary"]
```

A glyph is an observed body with its attached marks, not necessarily one Unicode
character. Punctuation, unattached marks and residual ink have separate rows.
Candidate show-through/stamp flags describe evidence, not known physical causes.
The readability proxy is not OCR accuracy. Keep color images when color evidence
matters: grayscale cannot establish that a stamp lacks color.

### Discounted lines

```python
kept = process_page(image, options=PageOptions(discounted="keep"))
active = process_page(image, options=PageOptions(discounted="drop"))
```

`keep` retains candidates and rejection reasons for audit. `drop` compacts the
line list and remaps piece, structure and neighbour indices; address IDs remain
stable. Statistics are measured against the selected list. In both modes,
discounted candidates are excluded from recognition and all review images.

Q2 can retain active ribbons with invalid top/bottom samples as diagnostic data.
The default preserves them. Use `PageOptions(strict_geometry=True)` or CLI
`--strict-geometry` to raise `ValueError("invalid_line_geometry")` before delivery
when an active ribbon is invalid. Discounted ribbons do not trigger this check.

### Files and images

```python
outputs = OutputOptions("out", frozenset({"lines", "segments", "structure", "cells",
    "checks", "statistics", "lines_image", "unrolled_image", "structure_image", "glyphs_image"}))
result = process_page("page.png", options=PageOptions(statistics=True, outputs=outputs))
print(result.files)
```

Every selected filename and field is described in [PAGES_OUTPUT_FORMAT.md](PAGES_OUTPUT_FORMAT.md).
Writing statistics produces both a statistics JSON and a glyph Parquet table
(JSONL if `pyarrow` is unavailable). Image switches are independent. Statistics
and orientation image/data switches require their corresponding computation.
Files at the selected destination use the page key and are overwritten on rerun.
Use a new output directory when retaining an earlier run.

`page_size=(width, height)` gives the physical/page-unit extent used in cell
serialization. Omit it to use source pixels. X and Y are converted separately;
never assume a requested PDF render scale equals the actual image dimensions.

## A book

```python
from pathlib import Path
book = process_book(sorted(Path("book-images").glob("*.png")), book_id="book-1",
    options=PageOptions(statistics=True,
        outputs=OutputOptions("book-output", frozenset({"statistics", "book_image"}))))
print(book.statistics["pages"], book.corpus["letter_bodies"])
```

Input order is preserved. For in-memory images, page keys are `page-00000`, etc.
For an exact replay, pass the original manifest's page order. Reordering the same
pages changes ordered output arrays and can change the last bits of floating-point
aggregates; the API does not sort or round those results to hide the difference.
A mapping `table_regions={page_key: proposals}` supplies per-page layout. Existing
`PageResult` objects can also be aggregated: their `book_id` must match, and
statistics must already have been measured. With existing results, geometry
switches have already been applied; the book call applies statistics and output
selection. Book enrichment copies measurement
tables; it does not overwrite the supplied page statistics. Original images are
required to write review images, so pass image inputs when requesting those.

Book statistics use other pages' references, excluding the page being scored.
Single-page books have no independent book reference. Results include a corpus
summary for this one book. To reproduce a multi-book corpus, call the existing
`greekocr.pages.statistics.corpus_statistics` on the ordered page summaries.
Do not combine different books under one invented book ID.

## Command line

```sh
greekocr pages scans/ --out out/
greekocr pages scans/ --out tables/ --tables --layout layout/
greekocr pages scans/ --out stats/ --statistics --book-id book-1
greekocr pages scans/ --out rows/ --join-lines --granularity rows
greekocr pages scans/ --out active/ --discounted drop --outputs lines cells structure
greekocr pages scans/ --out oriented/ --orientation --outputs orientation
greekocr pages scans/ --out review/ --statistics --outputs lines_image glyphs_image statistics
```

The command reads PNG, JPEG and TIFF files in lexical filename order, using one
raster per file (the first frame of a multi-frame TIFF). Duplicate
stems are rejected before writing. `--page-size WIDTH HEIGHT` applies to every
image in the directory; omit it for image-pixel units. An input directory can be
processed page by page or as one book using `--book-id`.

## Docling

`GlossapiOcrOptions.page_options()` maps `tables`, `join_lines`, `granularity`,
`statistics`, `discounted` and `outputs` to the same `PageOptions`. `recognition_mode="oriented"`
also enables orientation. Detector mode preserves the plugin's historical default
of tables enabled; Python/CLI callers opt into tables explicitly. Text-layer mode
keeps its existing path. Checkpoint, codec, routing and crop scale remain plugin
settings. The plugin uses layout already present on the Docling page and passes
actual page dimensions to the page API.
Detector mode also sets `strict_geometry=True`, preserving the plugin's existing
rule to leave native page cells intact when active line geometry is invalid.

For the stage order and coordinate boundaries, see [PAGES_PIPELINE.md](PAGES_PIPELINE.md).
For the strict Q3 equality gate and its unresolved differences, see
[the cleanup report](reviews/PAGE_LINES_Q3_CLEANUP_API.md).
