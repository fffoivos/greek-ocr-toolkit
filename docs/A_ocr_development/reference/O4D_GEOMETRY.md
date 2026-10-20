# O4d G1 v3: reference-free crop evaluation

Default policy: `o4d-local-line-geometry-v3`. Use `refine_line(..., policy='v3')`
or `greekocr geometry refine --policy v3`. V1 and v2 remain selectable for
comparison; added diagnostic fields have defaults.

The owner's 8 October 14:05 visual review of `O4D_G1_measure_v1.json` and
`O4D_G1_measure_v2.json` found that “attempt 1 is consistently better than the
original line”. The earlier exact-match adoption gate was invalid: the PDF text
layer is another OCR output, **never a reference**. Matching its mistakes cannot
establish crop or recognition quality. Historical CER/exact numbers measure
agreement with that OCR only; they support no accuracy ranking or rejection of
G1. They remain unchanged for audit. The four `_old`/`_new` pairs are also
unchanged; `_new` denotes historical v1 output, not a page raster or human gold.

V3 combines assigned-neighbour masking with v2's component-overlap band and
detached-mark protection, nearest-cluster target and integer row shifts. The
explicit keep rule takes precedence when a neighbour assignment conflicts with
the band: every overlapping component is kept, and small marks over kept body
ink are always kept. Unconditional cluster masking erased real ink in
`line33_small` and `line42_large` during development. The supplied v2 already
implemented this protected-neighbour combination, so **v2 and v3 produce the
same rasters on the 48 supplied originals**. The policy bump does not establish
an additional visual or reader accuracy improvement. V1 reproduces its original
0.55-height clustering, support-based target and component-only stencil; an
independent pre-edit replay receipt binds all 48 v1/v2 crop hashes and component
assignments in `tests/data/geometry_policy_replay.json`.

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
   tolerance is **0.35 body height** in v2/v3 (0.55 in selectable v1). Tracks need separation of 0.90 x-height on at least
   90% of their supporting centres. Limit quadratic bending to prevent a curve
   connecting outliers from two lines. Long rules and tall gutter strokes do not
   provide baseline support. Assign accents and other small components to the
   nearest track within 0.90 x-height.
4. Fit the **bottoms** of each cluster's body components using a quadratic and
   12 Huber IRLS iterations (delta 1.345, robust MAD scale). Descender outliers have
   reduced influence; sparse fits reduce to linear or constant fits. Select the
   fitted baseline whose **mean y across the original box's integer columns is
   nearest its vertical centre**, regardless of ink support. Deterministic ties
   use the original top-to-bottom cluster index. `selected_cluster_index` and
   `baseline_clusters` disclose every fitted curve, mean y, distance, component
   IDs, support ink and selected status.
5. Protect the page-space band `[baseline(x) − 1.9 × body_height,
   baseline(x) + 0.6 × body_height]`. Keep every component whose half-open bbox
   overlaps that band at any column, including components from other clusters.
   A detached small mark above the body zone, horizontally overlapping a kept
   body component, is also protected even outside the band: height < 0.60 body
   height, width ≤ 1.25 body height, area < 0.60 body height squared, and bbox
   bottom ≤ baseline at its centre − body height + two pixels. Protected mark
   IDs are recorded. **Mask only components fully outside the band and assigned
   to another baseline cluster**; unassigned ink is kept. This conservative rule
   can retain some overlapping neighbour ink and rules.
6. Extend the horizontal extent to all kept ink plus a two-pixel margin, while
   retaining the original width. Cover the entire protected band and all kept
   ink offsets from the rounded fitted baseline, with two-pixel margins.
   For each page column `x`, sample rows
   `round(baseline(x))-ascent .. round(baseline(x))+descent`, inclusively. Sampling
   uses **integer per-column row shifts / nearest-neighbour**, with no
   interpolation. Copy source grayscale values including paper, light stroke
   edges, noise below the component-size cutoff and detached accents. Only the
   explicitly dropped neighbour-component pixels become white; unavailable
   rows are white. The code supplied for v1 already used rounded row sampling,
   but its component-only stencil whitened all other source pixels. V2 removes
   that stencil and records the resampling policy.
7. Return the curve, source/search/refined boxes, kept/dropped components, ink
   coverage, retained-pixel fraction, curl amplitude and baseline counts.
   `n_baselines` describes the **selected output strip** (zero for no supported
   track); `source_n_baselines` records how many tracks were detected before
   neighbour removal. A chosen output baseline does not guarantee that all
   overlapping neighbour ink has been removed. A crop without a supported track
   retains its original raster and still fails the scan gate. The input and
   caller's NumPy RNG state are unchanged.

The ink-preservation census counts grayscale values **<220** independently of
component labels. Compare the original crop's pixels in the continuous baseline
band to exactly the same source positions in the strip, using the inverse
integer-column shift. The diacritic zone is the part of that band above
`baseline − body_height`. V3 requires ≥0.97 retention separately in the diacritic
zone and the body zone (the rest of the band). Diagnostics record original/refined counts and both
fractions (1.0 when a zone has no original ink), along with numeric band limits.
Tests additionally require every in-band source intensity to be bit-identical
after rectification, including pixels too small/light to count as components.

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
| `BASELINE_CLUSTER_TOLERANCE` | 0.35 × body height | Keep close visible tracks separate. |
| `BAND_ASCENT_RATIO` | 1.9 | Protect capitals and stacked breathing/accent ink. |
| `BAND_DESCENT_RATIO` | 0.6 | Protect descenders and overlapping component bboxes. |
| `INK_MASS_MAX_GRAY` | 220 | Count dark source pixels independently of clustering. |

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

## Historical text-layer agreement replay (diagnostic only)

Prefer `geometry evaluate` below. The older `geometry measure` API remains for
reproducing historical records; its receipts now explicitly carry
`diagnostic_only=true` and state that the text layer is another OCR, never a
reference or adoption gate. Its CER/exact fields must not be interpreted as
recognition accuracy.

`greekocr.real.geometry_measure.measure_geometry(lines, reader, *, out=None,
pad=16)` accepts a JSONL path or a sequence of rows and a callable
`reader(Path) -> str`. For an existing toolkit reader, pass `cllg.read`.
Required fields are `line_id`, `crop_path` (the original crop), `bbox_pixel`,
`page_image_path` and `text`. Optional `tier` enables tier summaries. Relative
paths resolve against the JSONL's parent; sequence paths resolve against cwd.
The page raster and box must use the same pixel resolution.

```json
{"line_id":"s2-example-l00001","crop_path":"crops/original.png","bbox_pixel":[10,20,800,70],"page_image_path":"pages/page.png","text":"ἀλήθεια λέξεις","tier":"silver_agreed"}
```

For CLI use, expose the initialized reader through an importable callable,
for example `staged_reader.read_crop(path)` which invokes `cllg.read(path)`:

```sh
.venv/bin/greekocr geometry measure --lines lines.jsonl --reader staged_reader:read_crop --out measured-v2 --pad 16
```

Only the named reader is imported/called. The caller supplies its staged model,
runtime and any external-action authorization. Each original crop is read once,
then its new PNG is read once. `out` must be a new directory; it retains the
refined PNGs and `receipt.json`. Python calls without `out` use temporary PNGs
that are deleted after the readings. No reader or checkpoint is loaded by default.

Receipts bind the input JSONL, original crops, page images and refined PNGs by
SHA-256 and retain raw source text, readings, geometry and per-row decisions.
Per-line image/reader errors are retained and excluded from successful score
means/counts. Summary fields include old/new mean/median CER, exact counts,
improved/worsened/unchanged counts, admission and hyphen counts, and optional
tiers. `multi_baseline` counts boxes with multiple supported tracks inside the
original box; `source_multi_baseline` also includes padding-only neighbours.
`split_boxes` disclose detections. Scoring reads the selected track against the
original unsplit label; it does not infer or concatenate split-line text.

For exact reproduction of the saved coordinator scores, `cer_old` / `cer_new`
use NFD codepoints with `difflib.SequenceMatcher(autojunk=False)`, summing the
maximum replaced/inserted/deleted lengths per unequal opcode and dividing by
reference length (at least one). Whitespace is preserved. Exact matches compare
NFD strings after stripping only leading/trailing whitespace. This opcode cost
is not minimum Levenshtein distance; `levenshtein_cer_old` / `_new` and their
means report that separate metric on the NFD strings. The toolkit's existing
strict atom scorer remains unchanged. A test reproduces **all 800 saved CER
values and 800 exact flags**, and the saved aggregate/tier statistics.

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

For the two curled fixtures, compare the chosen cluster's ink-row profiles in the
left and right 15% before/after. Both retain **100%** of the selected endpoint ink
with margins, and the endpoint profile separation falls below 40% of its original
value. Other pixels protected by the wider band remain in the raster and are not
excluded merely to flatten the measured profile.

V2 passes both preservation invariants on **48/48 originals**: all 44 fixtures
and the four regression `_old` rasters. Both minimum retained fractions are
**1.0**. `O4D_G1_validation_v2.json` records the input hashes, counts, selected
clusters and alternatives. Synthetic tests cover a stronger intrusive neighbour,
kept components assigned to other clusters whose boxes overlap the band,
stacked marks including outside-band marks assigned to another track, paper
intensity preservation and close two-track separation. `line01_large` splits
deterministically into two boxes; split labels remain unassigned.

On all 44 full strips, single-track refinement admits **43/44** under the
scan geometry gate; the born-digital comparison admits **0/44**. The independent
pre-change replay in `tests/data/o4d_legacy_admission.json` binds fixture hashes
and the vendor SHA-256. Because character coordinates are absent, its expected
character union is explicitly empty. This is not a reproduction of the unavailable
vouli_v6 cohort or its reported 5,003 source receipts. The supplied fixture HEAD
bytes are additively inventoried in `docs/INVENTORY.md` and the origins manifest;
no upstream page-acquisition provenance is inferred.

These raster tests do **not** constitute a new 400-line CLLG measurement: the
supplied evidence contains old/new readings and four crop pairs, but no original
page images, boxes or staged reader runtime for that cohort. The helper supports
that worker-side replay when those inputs are available. No v2 OCR accuracy
gain is claimed here.

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
  can still require review. Pixel-retention checks concern all original pixels
  in the protected band and diacritic zone, independently of selected components;
  no human gold geometry or OCR accuracy is claimed.
- No automatic label correction, cross-line substring assignment, adjudication,
  training import, production extraction or replacement of the existing gate is
  performed. Rejected and dropped evidence remains in the returned receipts.

## Historical real-page agreement (8 Oct 2026, 400 lines; text layer is another OCR)

| version | OCR-layer matches (400) | OCR-layer matches on 100 silver | median OCR-layer CER | mean OCR-layer CER | lower / higher OCR-layer CER |
| --- | --- | --- | --- | --- | --- |
| text-layer crops (baseline) | 100 | 100 | 0.042 | 0.106 | |
| G1 v1 | 27 | 20 | 0.082 | 0.136 | 67 / 272 |
| G1 v2 | 98 | 76 | 0.039 | 0.129 | 129 / 115 |

The former gate (exact ≥100 and lower-CER count > higher-CER count) is withdrawn.
Its conclusion that G1 should be rejected does not follow from OCR-to-OCR
agreement. G2 segmentation and G3 page dewarp remain separate arms; these
historical agreement numbers do not decide between them.

## Reference-free pixel signals

`crop_quality(original_crop, refined_crop, diagnostics)` accepts Pillow rasters
and `line.diagnostics`, its serialized dictionary or `line.receipt()`. Source
box, baseline curve, strip horizontal origin, strip baseline row and rectification
status bind corresponding pixels. Both crops must use the same pixel resolution.
Only their shared page-space x-range contributes to retention/removal; recovered
pixels outside that range cannot conceal losses. Cached ink counts and text are
not used. The evaluator uses the v3 target band for **all** policies while mapping
pixels through each policy's own row shifts. Changing the selected line cannot
change the retention measurement zone.

| Signal | Definition and direction |
| --- | --- |
| `diacritic_ink_retained` | Refined/original count of pixels <220 in `[baseline − 1.9 body, baseline − body)`. Higher is better; no original ink gives 1.0, with counts retained. This is an accent-zone proxy, not mark recognition. |
| `body_ink_retained` | Same count ratio in `[baseline − body, baseline + 0.6 body]`. Higher is better. |
| `neighbour_ink_removed` | Fraction of original dark pixels outside the line band that are no longer dark at corresponding source positions. No outside-band ink gives null. Outside-band ink can also be noise or a rule; this is a removal proxy. |
| `clipped_left`, `clipped_right` | Any dark pixel touching the actual output strip's first/last column. This flags possible clipping, not proof of a missing glyph. |
| `curl_residual_px` | Peak-to-peak variation of a fresh robust body-bottom baseline fit to output pixels over the shared width, selecting the track nearest the expected mapped target baseline. Lower is better; unsupported fits give null. This measures output ink, not a fabricated zero from the applied transform. |
| `contrast_delta` | Refined minus original ink/paper contrast: `(95th-percentile gray − mean dark gray)/255`, floored at zero, over the shared columns. Higher generally indicates more contrast. |
| `blur_delta` | Refined minus original Laplacian variance on grayscale pixels over shared columns. Higher means sharper. Ink density, padding and neighbour removal affect this proxy, so it does not independently prove preserved sharpness. |
| `reader_confidence` | Optional caller hook: mean per-character natural log probability. Larger (closer to zero) is more confident. Missing confidence gives null. |
| `inter_reader_agreement` | Optional caller hook: CER between independent reader outputs on the same crop. The evaluator uses symmetric NFD codepoint edit distance / max(lengths, 1); **zero means agreement**, lower is better. Whitespace is preserved. Neither reader is a reference. |

Supply reader hooks in a diagnostics mapping. Pixel-only calls leave both hooks
null. Counts, threshold, original/refined appearance values and the shared x-range
are included. Confidence and agreement are evidence for comparison, not human
correctness: independent readers can share errors and differently calibrated
readers' confidence scales are not interchangeable.

## Local reader confidence protocol

`r2_cllg_worker.py --confidence` returns one object per crop: `text`,
`character_confidences`, `mean_confidence`, `min_confidence` and
`mean_log_probability`. These come directly from `records[0].prediction` and
`records[0].confidences`; probabilities are not invented from text agreement.
Empty confidence sequences give null summaries. Mean log probability averages
the natural logs of individual probabilities, not the log of their arithmetic
mean; exact zeros are floored at 1e-300 for finite JSON. Unicode output is unchanged.
`--serve --confidence` uses the same newline protocol; `--describe` keeps the
model binding unchanged. Plain one-shot and serving modes retain the exact
string-list JSON bytes and do not access confidence records.

Use `load_cllg_worker(..., confidence=True)` for structured `read`/`read_batch`
results; the default remains string results. Close the reader after use. Toolkit
vendor changes and prior/current hashes are recorded in `T6_VENDOR_UPDATE.json`
and the origins inventory. Tests mock Kraken prediction records and the worker
protocol; no actual CLLG model/runtime is qualified here.

## Reference-free evaluator and blind comparison

```sh
.venv/bin/greekocr geometry evaluate --records lines.jsonl --page-images pages --policies original,v1,v2,v3 --readers cllg,ours --reader-config readers.json --out evaluated
```

Rows require unique `line_id` and `bbox_pixel`. Supply `page_image_path` (relative
to the records parent or `--page-images` directory), or `page_id` with a page
directory (`page_id.png`) or JSON mapping of IDs to locally staged raster paths.
An optional original `crop_path` resolves against the records parent and must
have the box's dimensions; otherwise the original crop comes from the page.
Paths in a page-images JSON map resolve against that map's parent. Original and
page rasters must share pixel coordinates and resolution; no resizing is hidden.
`text`, `layer` and `text_layer` are optional and retained only under the clearly
labelled `text_layer_diagnostic`. They cannot affect any pixel or reader score.

`readers.json` names staged local artifacts, with paths relative to that JSON:

```json
{"cllg":{"checkpoint":"ppocr_v6_tau090.safetensors","python":"venvs/cllg/bin/python","contract":"cllg_contract.json"},"ours":{"checkpoint":"ours.pt","codec":"codec/v1.json"}}
```

Alternatively use `CLLG_CHECKPOINT` / `CLLG_PYTHON` and
`GREEKOCR_OURS_CHECKPOINT` / `GREEKOCR_OURS_CODEC`, or an explicit callable
override `--reader cllg=staged_reader:read_crop`. A config entry can also specify
`{"callable":"staged_reader:read_crop"}`. Only selected readers load, using local
artifacts; built-in readers use CPU and a non-CPU `CLLG_ACCELERATOR` is rejected.
No downloads or service reader defaults are introduced. The ours reader currently
returns text only, so its confidence remains null. Callables may return text or
the confidence object described above. Python callers pass
`evaluate_geometry(..., readers={"cllg": cllg.read, "ours": ours.read}, out=...)`.

The new output directory contains:

- `crops/`: original and each requested policy raster for every successful line.
- `receipt.json`: source/page/crop hashes, geometry, measured pixel signals, each
  reader's raw text and confidence, pairwise CER, per-reader means and per-policy
  means/counts. Reader and crop failures remain visible and are excluded from
  corresponding means. Missing confidence/agreement is null, never zero.
- `summary.csv` / `summary.md`: mean reader log confidence, mean inter-reader CER,
  diacritic/body retention, neighbour removal and clipping rate per policy, with
  sample/error counts. There is **no text-layer column**. Single-reader evaluation
  leaves inter-reader agreement unavailable.
- `ab_pairs.json` / `ab.html` / `ab_crops/`: per-line shuffled choices with opaque
  A/B/C/D filenames and no policy or reader-result labels. The HTML lets a reviewer
  download selections locally. `ab_mapping.json` separately maps choices to
  policies. Do not disclose that mapping or the evaluation receipt to a blind
  reviewer. Local per-line seeded shuffling is reproducible (`--blind-seed`) and
  does not alter caller RNG state.

V3's independent pixel checks cover all 44 fixtures and all four regression
originals: body and diacritic retention are each at least 0.97 on every original
(measured minima 1.0), and outside-band ink is removed on `line01_large` and
`line06_large`. `O4D_G1_validation_v3.json` binds fixture hashes and these signals.
The companion historical v1 crops remain evidence; they are not treated as pages.
Determinism, historical raster replay, missing confidence, reader failures,
blind mapping and CLI readback are tested offline. No new 400-line OCR result or
automatic adoption claim is made; that requires locally staged pages/readers and
review of the resulting reference-free evidence.
