# Pixel-first page line segments

`greekocr.glyphs.page_text_lines.page_line_segments(page, hints=None)` starts
with the page pixels. `segment_page` retains both active and explicitly discounted candidates together with their
rough pixel boxes, intermediate masks and measured diagnostics. This is an
experimental page pipeline; the reviewed crop tools and their defaults are
unchanged. See the measured development report in
`docs/reviews/PAGE_LINES_ROUND3_20261009.md` before using its output for OCR.

## Method

First, the pixel segmenter removes connected frames, large graphics and scan
borders, finds near-vertical rules at several slants, and looks for gutters
persisting through several printed lines. It estimates the letter size from
components. Horizontal zones allow the column layout and type size to change
down the page. Row-ink valleys give rough regions; when lines curve through
those valleys, a region can contain several lines.

Within each region, the existing `components.line_glyphs` fitter and
`baseline.text_lines` guide estimator discover the main band, remove its
explained ink from the working copy, and repeat. The working copy preserves
local paper tone and freezes its contrast reference before peeling. This
prevents grey paper and remaining bleed-through from being promoted to strong
text. All original pixels remain available for final extraction.

Duplicate seeds and aligned pieces join across word spaces. They stop at
rules, persistent gutters, or a gap over ten x-heights. A three-x-height gap
alone is not a stop. Weak residual bands beside well-supported lines are
rejected; isolated short cells retain their own vertical position.

The crop fits establish provisional identities and shared column geometry.
`page_font` then classifies bodies, tall letters, descenders, upper/lower marks,
punctuation and non-text. Detached marks follow nearby physical bodies. A fused
upper mark can be split at a narrow neck above the mean line. Each class supplies
its own contacts to a robust fit of one shape with six vertical offsets. Missing
classes borrow median ratios from comparable type sizes, with defaults only
when the page has no such evidence. Borrowing is explicit in every record.
All-capital bands measure their capital guide and borrow a mean line.

Faint ink is measured against both local paper and the page's stronger text.
Discounted candidates remain in `segment_page().lines` and the saved review,
but `page_line_segments()` excludes them from OCR. They do not enter the
neighbour graph or the active overlap/cutoff counts. A uniformly faded page
remains detectable. This is photometric evidence, not a semantic stamp or
mirrored-letter recognizer.

After fitting, seed rectangles are provenance. Final extents follow owned
components and stop at graphical rules and persistent gutters. Broken and
tilted rule pieces establish continued page-coordinate paths. Stable neighbour
seams extend through short line ends using the longer neighbour's shape;
local ink constraints route seams around marks. Incompatible ownership still
produces measured cutoff errors rather than a claim of perfect tessellation.
Regions without nearby text neighbours retain an ordinary font margin.

The normalised image has x-height 32 by default, meanline row 48, baseline row
80, and height 128. Slowly varying measured x-height is normalized per column.
Pixels are resampled from the original grayscale image; no recognised text is
used to repair or erase them. Faint stamps can remain visible in those pixels.

## API and coordinates

```python
from greekocr.glyphs.page_text_lines import segment_page
result = segment_page(page_image, hints=None)
line = result.lines[0]
image = line.unroll(page_image, xheight=32)
record = line.to_record()
```

`x0` is inclusive, `x1` exclusive. The arrays `baseline`, `font_top`,
`meanline`, `font_bottom`, `accent_bottom`, `accent_top`, `top`, and `bottom` have one value for every source
pixel column. Image y increases downwards. A `column` is a spatial lane ID,
not a recovered table cell or semantic reading-order label. Layout changes
and spanning headings can still make these lane IDs approximate.

`borrowed` lists guides without trustworthy measurements; `ink_classes` counts
classified pieces (a fused mark may add a second piece). `contrast` is relative
to the page's stronger text; `discounted` is null or an explicit reason.
`guide_residuals` reports count, median, p90 and maximum normalized distance
for each observed class, with null distances for absent classes. These are
self-consistency measurements, not independently labelled font truth.

`segment_indices` refer to `result.segments`, the pixel-only boxes.
`segment_positions` contain `(segment, row, horizontal_position)` addresses.
`neighbours['above']` and `['below']` are per-pixel arrays of final line indices;
`-1` means no neighbour. Left/right addresses are scalars or `None`.
`hint_indices` refer only to optional rectangles. Hints never create, split,
fit or move a line, and their `text` is never consumed. The renderer reruns
Vouli pages with hints and compares extents, column, provenance, four font
curves and both region edges exactly.

The restored opt-in Docling `mode='detector'` uses this API and these unrolled
strips before layout. Docling receives rectangular envelopes; its call log
keeps pixel-segment indices and separate hint indices. Invalid geometry
preserves native cells. The default native-line mode keeps its existing
behaviour. Tests mock the recognizer; no recognition-quality claim is made.

## Reproduction

Run these commands from the worktree root with the Python specified in the
implementer brief (set `PYTHONDONTWRITEBYTECODE=1` for each invocation):

```sh
python scripts/generate_api_docs.py
python -m pytest -q -p no:cacheprovider tests/glyphs tests/test_provenance_cli_api.py tests/test_docling_contract.py > .astra/tests-round3.log 2>&1
python scripts/glyphs/render_page_line_segments.py --compare-hints
python scripts/glyphs/review_page_lines_round3.py
python scripts/glyphs/audit_page_line_outputs.py
python scripts/glyphs/audit_page_line_curl.py
python scripts/glyphs/review_page_lines_round3.py
```

The first report pass supplements check 8 with rough-box/graphic intersections.
The audit then binds those saved files, and the last report pass includes the
completed audit and test receipts. It does not change detector geometry.

The renderer writes `.astra/out/<key>.segments.json`, `.lines.json`,
`.checks.json`, `.lines.jpg`, and `.unrolled.jpg`. Strips retain their fixed
scale; sheets exceeding 300 lines wrap into consecutive stacks, read down
then right. Indices link the sheet to `.lines.json`. `checks.json` aggregates
all pages and binds source-image and implementation hashes. The independent
artifact audit validates the saved arrays, all overlapping pairs, provenance,
and image files. The curl audit first verifies exact pixel registration with
the frozen crop fixtures, then measures the manually selected contacts.

## Meaning and limits of the measurements

* **Segments / lines / multi** are counts of rough boxes, final strips, and
  rough boxes referenced by more than one strip. A wide rough box can cover
  several horizontal pieces as well as several stacked lines.
* **Cut** counts a strip if assigned source ink lies beyond its curved boundary
  or normalisation window, or if dark ink touches the delivered top/bottom
  raster edge. Counting source pixels before clipping prevents white padding
  from hiding a cut. The actual raster-edge count is also recorded separately.
* **Foreign** counts regions containing a component assigned to another line.
  This is an ownership-based diagnostic, not manually labelled ground truth.
  Stamps rejected during discovery, missed lines and unassigned ink are not
  magically recognised by this measurement. Unassigned body-component counts
  and retained assigned-ink fractions are included separately.
* **Cross** counts crossing a detected rule/gutter, including continued rule paths and full-height folds. It still cannot count an undetected boundary.
* **Overlap** tests actual positive intersection of all pairs of regions. The
  independent saved-output audit repeats this on the rounded JSON curves.
* **Broken** counts aligned disjoint pieces separated by at most ten x-heights
  without a detected stop. Different type sizes and missed table separators
  can make this diagnostic ambiguous; it is not a hand-labelled error count.

There is no independent full-page text-line ground truth for the 48 scans.
The synthetic tests have independent per-pixel line ownership and known
baselines. The real-page contacts are independent geometry references, not
text or detection-recall references. High assigned-ink retention does not
measure text recall and does not imply that each strip is suitable for OCR.
