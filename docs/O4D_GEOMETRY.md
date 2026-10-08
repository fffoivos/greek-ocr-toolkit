# O4d G1: ink-refined line geometry

`greekocr.real.geometry` adds an opt-in CPU geometry path for OCR text layers
on bound scans. This changes the behavior of the **new scan profile only**.
`extract_lines`, the vendored extractor, its label policy and its admission
implementation retain their bytes and behavior. Nothing is acquired, recognized,
trained or imported into factory shards by this module.

## Inputs and coordinates

Pass a locally rendered Pillow page image and `(left, top, right, bottom)` boxes
in **top-origin, half-open page pixels**, at the same resolution as the image.
PDF points require caller conversion before use. Floating boxes round outward
and clip to the image; empty, nonfinite and outside boxes fail. Component boxes
and baseline coefficients remain in page space; the output strip has its own
rectified pixel space. `LineCrop.image` is grayscale, with white background.

`TextLayerBox` optionally carries raw `text` and the complete original candidate
row as `legacy`. The page driver also accepts bare boxes or dictionaries with
`bbox_pixel`, optional `text` and optional `legacy`. A dictionary containing
original admission evidence such as `ink_bbox_error` is accepted as a legacy
candidate row. Never substitute the new crop's box for the recorded legacy
box when comparing admission profiles.

## Method

1. Expand the box by `pad` in all four directions, bounded by the image.
   Estimate local paper intensity using a Pillow box blur of radius 15 pixels.
   Significant ink is intensity `<80`, or intensity `<220` with at least 12
   grayscale levels of contrast below that local estimate. This avoids treating
   grey paper and gutter shadows as glyphs. SciPy measures 8-connected components;
   components smaller than three pixels are noise.
2. Estimate x-height using the area-weighted 60th percentile of component body
   heights, with weights capped at 500 pixels. This is a **body-height proxy**,
   including some marks/descenders, rather than a font metric. It avoids letting
   faded fragments and detached accents dominate the scale estimate.
3. Cluster component vertical centres around quadratic tracks using a local
   seeded RANSAC search (160 trials per cluster, at most four clusters) and Huber
   reweighting. Body support requires height at least 0.45 x-height, sufficient
   area, at least three components and 8% of the body's component count. Inlier
   tolerance is 0.55 x-height. Tracks need separation of 0.90 x-height on at least
   90% of their supporting centres. Limit quadratic bending to prevent a curve
   connecting outliers from two lines. Long rules and tall gutter strokes do not
   provide baseline support. Assign accents and other small components to the
   nearest track within 0.90 x-height.
4. For `refine_line`, select the track with the most component ink whose centres
   fall inside the original box. Ties prefer proximity to its vertical centre.
   Keep its components and return other significant components as dropped.
   Fit the **bottoms** of body components using a quadratic and 12 Huber IRLS
   iterations (delta 1.345, robust MAD scale). Descender outliers therefore have
   reduced influence. Sparse fits reduce to linear or constant fits.
5. Extend the horizontal extent to all kept ink plus a two-pixel margin, while
   retaining the original width. Estimate ascent/descent from every selected ink
   pixel's offset from the rounded fitted baseline, also with two-pixel margins.
   For each page column `x`, sample rows
   `round(baseline(x))-ascent .. round(baseline(x))+descent`, inclusively. Sampling
   uses integer translations without interpolation; selected grayscale pixels
   retain their original intensity, and dropped components become white.
6. Return the curve, source/search/refined boxes, kept/dropped components, ink
   coverage, retained-pixel fraction, curl amplitude and baseline counts.
   `n_baselines` describes the **selected output strip** (zero for no supported
   track); `source_n_baselines` records how many tracks were detected before
   neighbour removal. The input and caller's NumPy RNG state are unchanged.

`split_multiline` uses the same clustering and emits ink-extents boxes for each
supported track whose centre is inside the original box. Padding-only neighbours
are excluded from splitting. Curled tracks' axis-aligned bounds can overlap even
when their ink is separate. No split returns the original box.

`refine_page_lines` processes input boxes in their given order and split tracks
from top to bottom. It refines each resulting box and records `input_index`,
`split_index` and `parent_box`. A split keeps the original raw string as
`source_text`, sets output `text=None` and `text_assignment_required=True`, and
leaves hyphen-label diagnostics unset. The caller must assign per-line text;
labels are never divided uniformly or inferred from component counts.

## Admission thresholds

The named gate constants live in `greekocr/real/geometry.py`. Every `Admission`
receipt records the numeric thresholds, profile, decision, rejection reasons and
all diagnostics. They are heuristics for the supplied scan scale, not universal
font/DPI settings.

| Constant | Value | Justification |
| --- | ---: | --- |
| `SCAN_MAX_CURL_PX` | 48 px | Allow local curl below a typical line height; larger deformation requires review/G3. |
| `SCAN_MIN_INK_COVERAGE` | 0.015 | Permit faded print while rejecting nearly empty strips. |
| `SCAN_MAX_INK_COVERAGE` | 0.55 | Reject filled/inverted strips and dense rule-like regions. |
| Required `n_baselines` | 1 | A crop is a single supported output track. |
| `DEFAULT_PAD` | 16 px | Bound the search for omitted terminal ink and accents. |
| `MIN_COMPONENT_AREA` | 3 px | Match the legacy character-ink noise floor. |
| `STRIP_MARGIN_PX` | 2 px | Room for rounding, accents and descenders. |

`profile='scan'` requires one baseline, finite nonnegative curl at most 48 pixels,
ink coverage in the inclusive range `[0.015, 0.55]`, and a nonblank strip. Explicit
cross-column evidence, including recorded candidate gutters without a spanning
exemption, still rejects. `unexplained_ink`, `missing_ink`, `ink_bbox_error` and
source multiline evidence remain in diagnostics; glyph-box spatial membership
is not a scan rejection. This is a **geometry gate**, not label correctness,
rights review or training admission. Original label controls and all other
candidate evidence remain available in the legacy row.

`profile='born_digital'` calls the unmodified vendored `admit` on a copy of the
original row, preserving its label, geometry, column and fragment rules and the
0.25 ink-bbox-error limit. Input text/box evidence is required. Caller-owned
cross-row duplicate and lexicon state are outside this geometry API. Where no
original character geometry is supplied, default diagnostics explicitly set
`invalid_char_geometry=True` and measure character-ink containment against an
empty expected union; they do not manufacture glyph boxes.

## Missing end hyphens

`hyphen_at_line_end` inspects a rectified `LineCrop` or a Pillow strip. It finds
the rightmost body glyph and asks whether a separate later component has dash
geometry: aspect at least 2, width 0.15–1.25 x-height, height at most 0.45 x-height,
centre within 0.35 x-height of the final glyph's ink centre, and gap at most 1.50
x-height. The height/width allowance includes scan bleed. Dots and long rules
fail. Labels already ending in `-`, soft hyphen, U+2010 or U+2011 (ignoring trailing
space) return false. The page driver records `hyphen_missing_in_label` when
unsplit raw text is available. It never appends a character or normalizes a label.
The flag requests review: ink morphology alone does not certify glyph identity.

## Offline CLI

Create `boxes.json` as a list of boxes, a list of candidate rows, or
`{"boxes": [...]}`. For example, one row may be
`{"bbox_pixel": [10, 20, 800, 70], "text": "ἀλήθεια λέξεις"}`.

```sh
.venv/bin/greekocr geometry refine --image page.png --boxes boxes.json --out refined --pad 16 --profile scan
```

The output directory must be new. The command validates/refines inputs before
creating it, saves every output crop including rejects, and writes/prints
`receipt.json` containing input SHA-256s, crop/raster SHA-256s, raw label custody,
geometry metadata and admission receipts. Crop paths are relative to that
directory. Split labels remain unassigned; all labels remain provisional
`silver_ocr_layer` / `unadjudicated`. The CLI has no PDF acquisition, OCR reader,
network, GPU or factory-import side effects.

## Recorded fixture validation and evidence limits

The delivered `tests/fixtures/o4d_lines/index.json` contains 44 strips but
`owner_notes={}`. It contains no page, pixel-box or character coordinates beyond
the already-extracted rasters. The following test selections are based on visible
ink and are **not attributed to owner notes**:

| Fixture | Verified contract |
| --- | --- |
| `line01_large.png` | Two visible tracks split into two boxes; no label assignment. Its upper line curls downward at the right end. |
| `line06_large.png` | Selected line curls upward at the right end; remove neighbouring ink. |
| `line24_small.png` | Final ς of γυρίζεις is available at x=1451..1462. Deliberately narrow the test box to x1=1457; padding recovers it and extends the crop by 8 pixels. This is a controlled box-clipping test on recorded ink. |
| `line02_small.png` | Visible πρόσω- has no trailing hyphen in the raw label; flag its missing hyphen without modifying the text. |
| `line07_medium.png` | The source raster itself ends through Θεσσαλίας. Report right-boundary ink; do not claim recovery of unavailable pixels. |

For the two curled fixtures, compare the selected ink-row profiles in the left
and right 15% before/after. Both retain **100%** of the selected endpoint ink with
white top/bottom margins. Left/right profile-centre separation changes from
30.83 to 1.75 pixels (line01) and 21.87 to 7.41 pixels (line06). This proves local
containment/flattening of **selected** ink, not perfect glyph classification.

On all 44 full strips, single-track refinement admits **44/44 (100%)** under the
scan geometry gate; the born-digital comparison admits **0/44**. The independent
pre-change replay in `tests/data/o4d_legacy_admission.json` binds fixture hashes
and the vendor SHA-256. Because character coordinates are absent, its expected
character union is explicitly empty. This is not a reproduction of the unavailable
vouli_v6 cohort or its reported 5,003 source receipts. The supplied fixture HEAD
bytes are additively inventoried in `docs/INVENTORY.md` and the origins manifest;
no upstream page-acquisition provenance is inferred.

Offline tests also cover known quadratic synthetic ink with descender outliers,
blank strips, gate boundary/negative cases, terminal-dot/rule negatives, preserved
legacy decisions, input/RNG immutability, repeated raster/receipt determinism,
CLI readback, retained rejects and refusal to overwrite prior output.

## What G1 does not solve

- **G3 page-level dewarp** is a separate arm. This method translates columns of
  individual strips; it does not repair a page surface, perspective, character
  width distortion or deformation too large for the local quadratic model.
- **G2 Kraken segmentation** is a separate arm. G1 requires existing text-layer
  boxes; it does not discover complete page reading order or assign columns.
- Pixels absent from the page image cannot be recovered. `source_boundary_ink`
  discloses selected ink touching page edges; `search_boundary_ink` also exposes
  a possibly insufficient pad. Both are diagnostics under the requested scan
  gate. Supply the full page and sufficient padding for actual recovery.
- Connected glyphs spanning neighbouring lines, unusual layouts, sparse text,
  faded components near the clustering boundary and gutter rules touching glyphs
  can still require review. Pixel-retention checks concern selected components;
  no human gold geometry or OCR accuracy is claimed.
- No automatic label correction, cross-line substring assignment, adjudication,
  training import, production extraction or replacement of the existing gate is
  performed. Rejected and dropped evidence remains in the returned receipts.
