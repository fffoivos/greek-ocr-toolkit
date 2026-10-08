# Page lines: the main algorithm

Owner direction, 8 October 2026 (19:10). This is the algorithm `greekocr.glyphs.recut.fix_page` follows. When a
detail of the code and this document disagree, this document wins and the code is changed.

Input: a page image and every text-layer box on it (the recogniser's segments). Output: every text line on the page,
each with its own region that overlaps no other line's region, and an image of it for OCR.

## The seven steps

1. **A coordinate system for every line.** Every line has an address: the segment (text-layer box) it belongs to and,
   when a segment holds more than one line, its position inside the segment: up / down (lines stacked in the box),
   left / right (columns in the box, split at a rule or a wide unaligned gap). Every line knows its neighbours: the
   line above, below, to the left and to the right, whether they live in the same segment or in another one.
2. **Neighbours are looked up, not searched for.** If a line's top is cropped, the missing part lies towards its top
   neighbour, and the coordinate system says which segment that neighbour lives in.
3. **Follow the curve.** Every line's baseline is followed letter by letter. It may be straight, skewed or curved.
4. **The four font lines.** We know where the short letters (α, σ, ι) sit, where tall letters (δ, β) and accents
   reach up to, and where hanging letters (ρ, φ) reach down to; capitals are measured too. Within a page set in one
   font these heights are consistent, so the four font lines (top, mean line, baseline, bottom) are a property of the
   page's font, measured across all its lines and applied to each line.
5. **The four font lines follow the line's curve.** Each is the baseline curve offset by the font's height for that
   line.
6. **Boundaries without overlap.** At every column k, the boundary between a line and a neighbour is the middle of
   the distance between this line's facing font line and the neighbour's facing font line: between this line's bottom
   and the lower neighbour's top, and between this line's top and the upper neighbour's bottom. Neighbours come from
   step 1, so two lines share one boundary and their regions never overlap.
7. **Extend generously and stop only for real reasons.** We detect reliably when a line's curve or skew runs outside
   its segment's boundary. It is better to overdo it and follow the line's continuation as far as it goes than to lose
   text. Stop at the page boundary. Cut back only at a graphical boundary (a column rule, page-edge shading, a frame)
   or a very large gap.

## The procedure (owner, 8 October 19:40)

1. Get the line segments (the recogniser's boxes) as an input.
2. Draw the curves / skew lines and the four font lines for each line in the segment; give each line its coordinates
   (its segment and its position in it), which separate the lines' identities.
3. Once there are curves and the four font lines for each text line, **forget the initial line segments completely**.
4. Draw a new segment simply by finding the middle between the bottom and top font lines of neighbouring lines, and by
   extending left and right along the curve until a boundary is found.

**Use of shared geometry.** Lines on a page generally share the same skew or curve (the page's geometry: its tilt and
its warp). Neighbouring lines' curves are therefore one shared curve shifted vertically per line, and their letters
are fitted together.

**Acceptance (owner, 8 October 19:40), first on three consecutive lines of each column of one page:**
- the line segments tessellate their space: no overlap and no gap between neighbouring segments;
- each line's characters are centred between its segment's top and bottom boundary in their true alignment (along the
  curve or skew).

Iterate on the mathematics on those six lines until both hold; then widen to the page.

**Owner direction (9 October, 00:15): start from pixels.** From now on the starting segments should come from our own
pixel segmentation, not the PDF's text-layer boxes: one path for every page (Anemi and other scans have no text layer),
and the line set our recogniser reads comes from our geometry rather than from InVision's segmentation errors. The
text-layer boxes remain optional hints and a diagnostic (their text). To confirm before switching: run the page
detector on the Vouli pages from pixels alone and with the boxes, and compare.

## Where the code stands (commit `a5750e2`)

| Step | Code | Status |
|---|---|---|
| 1 coordinates | `PageLine.box_index`, `.segment` (column in the box), `.kind` (`main` or `split`) | **Partial.** Lines know their box and column, but there is no explicit neighbour graph (up / down / left / right links); the up / down position of a split line inside its box is implicit. |
| 2 neighbour lookup | `_neighbour()` | **Searched, not looked up.** It scans every fitted line for the nearest one overlapping in x. Equivalent result; it should read the step-1 links. |
| 3 follow the curve | `components._track`, `_smooth_curve` (inside the box); `recut._walk` (beyond it) | Done. |
| 4 font lines per page | `text_lines()` per line; page medians for x-height and line pitch only | **Partial.** The top / mean / bottom offsets come from each line's own crop; the page-level font model (one set of heights for the page) is not used yet. |
| 5 font lines follow the curve | `LineFit.base`, `.rise`, `.up`, `.down` | Done: constant offsets from the baseline curve. |
| 6 boundaries | `_voronoi_keep()`: midline between the two lines' letter-body centre curves; ink kept per component by centroid | **Different rule.** It uses the centres, not the facing font lines. The two coincide when top height = bottom height + body height (about true for this print); otherwise the step-6 rule is the stated one. The per-component rule (an accent crossing the boundary stays with its line) is an addition. |
| 7 extension | `_walk()`: page edge; rule; shading or anything filling the walking window; blank gap > 3 x-heights | Done, except that a "very large gap" is set at 3 x-heights (word spaces reach 1.9 at the 99th percentile). That may cut back earlier than step 7 intends where columns are separated only by a gap. |

## Measured so far

- Synthetic two-column pages: original boxes keep 80 % of each line's ink; `fix_page` keeps ≥ 99.7 % (normal
  spacing, 72 lines) and ≥ 98.2 % (tight spacing, ±3° skew, 96 lines), other lines' ink ≤ 2 %.
- Real pages (443 lines, 321 pages, run `out_444w`): text-layer boxes overlap their neighbours in 79 % of 20,496
  adjacent pairs (median overlap 13 % of box height). Lines are 2.54 letter heights apart (median; 10th–90th
  percentile 2.31–2.77). The top is cut on 424 of 483 lines, the bottom on 38, line ends on 152; 40 boxes span two
  columns; 37 hold a second line.

## Next changes to make the code follow this document

1. Build the neighbour graph once per page (step 1) and use it for the boundaries (steps 2, 6).
2. Fit the page font model: median top / mean / bottom offsets over the page's lines (step 4), with per-line values
   kept only as a diagnostic.
3. Boundary = midpoint of the facing font lines at every column (step 6); compare with the centre rule on the
   synthetic pages and the owner's cases, and keep the per-component exception only if it is needed.
4. Revisit the gap stop (step 7): stop at a gap only when it is much wider than the page's word spaces and nothing on
   the far side lines up with this line's curve.
