# Line metadata

`greekocr.annotate.line_features(image, text=None, *, geometry=None, lexicon=None)`
returns a frozen `LineFeatures` dataclass. `features.to_dict()` is JSON serializable,
including with `json.dumps(..., allow_nan=False)`. Images may be local paths, Pillow
images, uint8 arrays, or finite float arrays normalized to [0, 1]. Grayscale, RGB
and RGBA are supported; alpha is composited on white. Empty/invalid arrays are
rejected. No OCR, network, GPU, torch, or training is involved in measurement.

Measurements describe the supplied line crop at its native resolution. The line
band is the whole supplied strip, including its margins; compare crops with the
same padding and scale. Values are diagnostics, never admission decisions. Source
text, licence declarations, label tiers and existing admission decisions survive
annotation unchanged. No annotation turns a provisional label into gold.

The shared vocabulary comes from
[`shard.rs`](../greekocr/_vendor/factory/src/shard.rs),
[`recipe.rs`](../greekocr/_vendor/factory/src/recipe.rs), and the frozen
[`line_categories`](../greekocr/_vendor/bench/line_categories.py) rules. Fonts keep
exact factory ids. `bg_type` uses `flat`, `gradient`, `textured`; `polarity` uses
`dark_on_light`, `light_on_dark`; severity is 0–3. `script_class` calls the same
vendored `o4b_common.tag` used by line categories, including its real-import
Cyrillic mapping. Nonletter text has no script tag (`null`), rather than an
invented script classification. Synthetic row fields remain in the input record
for provenance, even where those rules yield a different diagnostic tag.

## Pixel derivation

RGB luminance is 0.299R + 0.587G + 0.114B, in [0, 1]. Otsu thresholding and the
perimeter median choose polarity; light ink is inverted internally. A 31×31
grayscale closing, bounded by raster dimensions, estimates local paper. Ink is
below the oriented Otsu threshold and at least 2/255 below that local paper.
Uniform strips have no ink. Strips at least 3 pixels in each dimension whose
maximum second finite difference is <=1/255 also have no ink: this suppresses
closing-boundary artifacts on unprinted affine/quantized-affine gradients. The
same mask supports every pixel statistic.

This deterministic heuristic handles the 44 O4D scan strips and inverted text.
Paper patterns, broad filled regions, touching lines and extremely faint ink can
confuse it. It is not glyph segmentation: ink includes decorations/marks, and
small-component counts can include accents. Component heights approximate type
size and do not establish linguistic x-height or capital height without glyph
alignment. There is no estimated letter count from pixels.

## LineFeatures fields

All missing values are `null`. Present empty lists mean a known empty list, not
missing evidence. An absent text label leaves all text fields missing; an explicit
empty label gives zero counts/ratios and `language_guess="other"`.

| Field | Units / values | Derivation and missing-value rule |
| --- | --- | --- |
| `height_px` | px, integer | Raster height, positive. |
| `width_px` | px, integer | Raster width, positive. |
| `aspect` | ratio | Width / height. |
| `ink_coverage` | fraction [0, 1] | Foreground pixels / pixels in the supplied line band; light foreground is counted on inverted strips. This includes margins and all ink, not just letters. |
| `background_level` | luminance [0, 1] | Median original-polarity luminance outside ink; whole-image median if no paper is available. |
| `background_rgb` | RGB triple, each [0, 1] | Per-channel median outside ink; null for grayscale or no paper pixels. |
| `background_cast` | RGB triple, signed normalized levels | Each background RGB channel minus their mean; sums to zero. Retains off-white hue without inventing a colour name. Null without RGB. |
| `contrast` | luminance difference [0, 1] | Absolute difference of ink median and paper median in original luminance. Null without both populations. |
| `local_contrast_p10` | luminance difference [0, 1] | 10th percentile of oriented local paper minus ink, over foreground pixels. Null without ink. |
| `local_contrast_p90` | luminance difference [0, 1] | 90th percentile of the same local contrast. Null without ink. |
| `stroke_width_px` | px | Twice the median Euclidean distance-transform value on 3×3 local distance maxima inside ink; an outside zero border bounds distances. Null without ink. Ridge sampling avoids the boundary-heavy all-ink median. |
| `xheight_px` | px | Median body-component height. Bodies have area >=4 px and width/height <8; retain heights >=0.4×their p90. Null without bodies. Approximation including connected accents/capitals. |
| `capheight_ratio` | ratio, >=1 | p90 of those body heights / their median height; a capital-height proxy, not a glyph-level measurement. Null without bodies. |
| `polarity` | shared category | `dark_on_light` or `light_on_dark`, from perimeter median versus Otsu threshold. Blank polarity is only the algorithm's background convention. |
| `blur` | normalized luminance squared | Variance of scipy's discrete Laplacian, reflected boundaries. Larger usually means sharper/more textured; not a calibrated blur amount. |
| `noise` | component count | Number of 8-connected foreground components of area <=3 px. Small marks/accents can count; not a physical noise estimate. |
| `curl_px` | px | Supplied geometry `curl_px` or T2 `curl_amplitude_px`; no fresh geometry fit. Null if unavailable. |
| `skew_deg` | degrees | Supplied diagnostic, otherwise atan(c1/x_scale) in degrees from a supplied T2 baseline curve at its x_origin. Null if unavailable. |
| `clipped_edges` | list of edge names | Sorted unique supplied `clipped_edges` or T2 `source_boundary_ink`. Ink at a source boundary is a clipping diagnostic, not confirmed missing glyphs. Null without evidence; [] means supplied evidence has no flagged edges. |
| `n_chars` | Unicode code-point count | Length of NFC text, including spaces/punctuation. Not NFD atom count or grapheme count. Null without text. |
| `n_words` | token count | Maximal runs of Unicode letters in NFC; digits excluded, punctuation/apostrophes/hyphens split words. Null without text. |
| `n_letters` | letter count | Unicode alphabetic NFC code points; excludes digits, punctuation, spaces and detached combining marks. Complements n_chars for the owner's letter-count axis. Null without text. |
| `script_class` | shared category or null | Exact vendored tag over text: `greek_mono`, `greek_poly`, `greek_latin_cs`, `latin`, `cyrillic`, or null for no tagged script. Not inferred from the raster. |
| `polytonic_mark_density` | marks / Greek base letter | NFD marks U+0313, 0314, 0342, 0345, 0300, 0304, 0306 attached to Greek base letters, divided by Greek base-letter count. Multiple marks per letter can exceed 1. Zero without Greek letters; null without text. Acute/diaeresis alone do not make a polytonic tag. |
| `digit_ratio` | fraction [0, 1] | Unicode digits / nonspace NFC characters excluding combining marks. Zero if denominator empty; null without text. |
| `punct_ratio` | fraction [0, 1] | Unicode P-category characters / same visible-character denominator. Zero if empty; null without text. |
| `upper_ratio` | fraction [0, 1] | Uppercase NFC letters / all NFC letters. Zero without letters; null without text. |
| `language_guess` | `el`, `grc`, `en`, `fr`, `other` | Greek-majority letters → el, or grc if polytonic marks are present. Latin-majority letters use small French/English function-word sets, with French accents as a fallback. Other/ambiguous Latin words → other. Null without text. Historical modern Greek can be polytonic: this is a weak rule guess, not language identification. |
| `lexicon_validity` | fraction [0, 1] | Greek-only letter tokens found in supplied lexicon / Greek-only tokens, counting occurrences. Compare casefolded NFD words with marks removed and final sigma folded. Null without lexicon or without Greek tokens; an explicitly empty lexicon gives zero for Greek words. |
| `bg_type` | shared category | Fit a plane to <=approximately 4096 sampled paper pixels. Residual std >0.025 → textured; else summed absolute normalized x/y slopes >0.04 → gradient; else flat. Synthetic records retain their declared recipe category. Real-import placeholder flat is remeasured. |
| `font` | exact font family id or null | Standalone measurements leave it unset. Annotation preserves an explicit known record font or an opt-in model prediction. `real`/`unknown` are not font identities. |
| `font_style` | shared style or null | Known font mapping or model style: `didot_greek_19c`, `modern_serif`, `sans`, `mono`, `script/other`. Style does not date a document. |
| `severity` | shared ordinal 0–3 or null | Declared synthetic recipe severity only; never fitted from image appearance. A real-import `font="real"` severity=0 placeholder remains null in features. |
| `applied_ops` | list of operation names or null | Supplied operation history, preserving exact names/order. [] is known no operations; null is unknown. No operation history is inferred from real scans. |

`load_lexicon(path)` reads UTF-8 (BOM accepted), one word per line, ignoring blank
lines and `#` comments. It also accepts an iterable of words. Supply a local,
versioned Greek lexicon; no dictionary is downloaded or bundled. Annotation loads
it once and reuses the normalized entries.

Geometry accepts `GeometryDiagnostics`, `LineCrop`, a `LineCrop.receipt()` mapping,
or a flat diagnostic mapping. It measures the supplied image, not the original
page; curl/skew/boundary evidence describes the supplied receipt's coordinate frame.

## Font classifier

`font_estimate(image, model=local_model)` uses a numpy nearest-centroid classifier.
It crops the ink bounding box, pools its mask to 32×8, and appends ink density,
median component width/height, and component width/height coefficients of variation
(260 dimensions). It returns a frozen `FontEstimate`:

| Field | Meaning |
| --- | --- |
| `font`, `font_style` | Predicted factory id and shared style; null when no model, blank image, or beyond that family's support radius. |
| `distance` | RMS descriptor distance to the nearest centroid, nonnegative, or null without an eligible raster/model. |
| `margin` | Second-nearest minus nearest distance, or null with fewer than two families/no prediction input. Not a calibrated confidence. |
| `model_id` | Caller model's identifier; `record.font` for a known source font; null without a model. |
| `fixture_only` | Whether the explicitly loaded model is marked as a test fixture. |

Font mapping recognizes Didot/OldStandard, mono/Courier, sans/Arial/Helvetica,
and common serif names; other known names use script/other. A caller's JSON style
mapping overrides these name rules during fitting. Production models store the
chosen mapping. Annotation also respects a known record's supported font_style,
then a supplied model's style mapping, then the name rules. The test model is
[`font_fixture.json`](../greekocr/annotate/fixtures/font_fixture.json): two direct
descriptors of generated Times/Arial strips, explicitly `fixture_only=true`. It
is shipped for contract tests and is **never loaded by default**. Its two exact
fixture predictions do not qualify a classifier for real scans.

Training is streaming CPU numpy: per-font descriptor means and second moments.
Support radius is max(0.05, 3×within-family RMS deviation). No torch is required or
imported. Parquet I/O lazily uses the repository's optional `pyarrow`; JSONL needs
only numpy/scipy/Pillow and Python's standard library. No actual dataset/model
training was performed for T5; tests fit only the two generated fixture rasters.

Documented worker-side fitting command, **not executed on real supply here**:

```sh
python scripts/train_line_font.py --shards /staged/synthetic/train --out /new/font_model.json --styles /staged/font_styles.json
```

Input can be an existing factory directory (`shard-*.parquet`, recursively), one
Parquet shard, one JSONL manifest, or a directory of JSONL manifests. Every training
row must have a known `font`. PNG bytes come from `image_png` or local crop paths.
Use balanced fonts, varied texts and severities; qualify on held-out document/text
groups and real scans before relying on predictions. The descriptor can learn text,
scale, degradation and crop confounds. No accuracy claim accompanies this baseline.

## Source metadata

`source_metadata(record, catalogue)` joins by `source_doc_id`, `document_id`,
`identifier` or `id`. Catalogue inputs can be a mapping keyed by document identity,
source-qualified `source:identity` keys, a list of identified rows, or a
`{"documents": ...}` / `{"records": ...}` wrapper. Lists filter by source and reject
duplicate matching identities. Annotation also accepts a JSON/JSONL catalogue path.
Absent matches produce unknown values, never a title-based fuzzy join.

| Output field | Derivation / units |
| --- | --- |
| `year` | One unambiguous four-digit year in explicit catalogue year/date fields, including parliament DSpace dcterms.created.from / dc.date.issued, Anemi displayed publication date, and IA metadata date. Catalogue precedes record fallback. Date ranges/conflicts within a field remain unresolved. Web/born-digital fetched_at supplies a fallback capture year only. |
| `year_basis` | Exact origin field (`catalogue.year`, `catalogue.metadata.date`, etc.), or `fetched_at`; null without year. A fetch year is not a writing/publication year. |
| `collection` | Explicit record/catalogue collection; null if missing. No collection inferred from an image. |
| `doc_type` | Explicit allowed type, otherwise source rule: parliament/vouli→proceedings; gazette/FEK→gazette; Anemi/IA/archive/Gutenberg→book; news source→newspaper; recognized web source→web. Explicit born_digital flag converts web/unknown to born_digital_article. Allowed vocabulary: proceedings, gazette, book, newspaper, web, born_digital_article. Unknown sources stay null. |
| `licence` | Preserve explicit licence/license or raw IA metadata licenseurl. Unknown declarations stay unknown; rights are not inferred from dates. |
| `licence_tier` | Explicit rights/access tier, e.g. Anemi's research-only tier; null if absent. |
| `tier` | Record label_tier/tier then catalogue fallback; no upgrade or reinterpretation. |
| `page_position` | Requires a valid top-origin bbox_pixel/source_box and explicit page_height_px or page_size_px=[width,height]. Box centre in top/bottom 10%→header/footer; elsewhere an explicit zero-based column_index→column_k, else body. No page dimensions or invalid box→null. Strip coordinates alone cannot establish page position. |

Publication fields describe catalogue evidence, not necessarily the year a text
was composed. Header/footer/column assignment is a positional heuristic; no page
layout inference is run. Original records retain complete geometry and rights
evidence alongside this summary.

## Annotation and reports

```sh
greekocr annotate lines records.jsonl annotated.jsonl --catalogue catalogue.json --lexicon greek_words.txt
greekocr annotate lines records.jsonl --out annotated.jsonl --font-model qualified_font_model.json
greekocr annotate report annotated.jsonl --out real-distribution.md
greekocr annotate report /staged/synthetic/train --out synthetic-distribution.md
```

Legacy `greekocr annotate 'ἅλφα Latin'` still tags text; `annotate text '...'` is an
explicit equivalent. `annotate_records` also accepts the shard inputs above.
Relative crop references resolve against their input JSONL location and export as
absolute `crop_path` values. Annotation emits a new sidecar with
`annotation_schema="greekocr-line-metadata-v1"`, `line_features`, `source_metadata`,
`font_estimate`, and `line_categories`. Known fonts are metadata, not classifier
predictions. Synthetic severity/background/operations use shared fields unchanged;
real-import unmeasured font/severity/background placeholders are not promoted.
Factory operations supplied on a real import remain recorded operations.

The input cannot equal the output; a directory's output must be outside its input
tree. Existing outputs are refused. A temporary JSONL is removed on any failure;
after a complete write/fsync, an atomic no-replacement hard link publishes it.
Records stream one at a time. Parquet raster bytes are omitted from the metadata
sidecar and replaced with `image_png_sha256`; original shards remain the image
source. A sidecar is not a standalone image dataset. Base64 image_png is accepted
in JSONL for fixture/interchange inputs.

`distribution_report(path)` returns Markdown. Annotated JSONL is reported without
reopening images; raw manifests/shards are measured with the same pipeline in
memory. Every scalar numeric field, each RGB/cast channel, year and classifier
distance/margin gets present/missing counts, p0/p10/p25/p50/p75/p90/p100, and ten
equal-width histogram bins. The last bin includes its right edge; constants get
one bin. Every categorical field gets counts, including source/licence/tier/model
provenance and category/operation/edge lists. Lists count each member once per
line, with `<empty>` distinguished from `<unknown>`. Groups are source_dataset,
then source, then unknown. Empty reports are valid. Exact quantiles currently
retain numeric values in memory; report memory grows with supply size.

## Strata and future weighted mixes

`stratum_key(record)` accepts an annotated row (or a flat feature/source mapping):

`(script_class, polytonic, doc_type, year_bucket, contrast_bucket, ink_bucket, font_style)`

| Axis | Rule |
| --- | --- |
| polytonic | density >0; unknown without density, except exact greek_poly/greek_mono tags imply true/false. |
| year_bucket | pre1800, 1800_1899, 1900_1949, 1950_1999, 2000_plus; unknown when absent. |
| contrast_bucket | low <0.2; medium [0.2,0.5); high >=0.5; unknown when absent. |
| ink_bucket | sparse <0.05; medium [0.05,0.2); dense >=0.2; unknown when absent. |

`stratum_counts(rows)` returns tuple-keyed counts. `sampling_weights(rows, floor=0,
floors=None, targets=None)` returns probabilities in original row order, summing
to one. Default mass is uniform across existing strata, then uniform across lines
inside each stratum. Targets are arbitrary nonnegative relative stratum masses.
The global floor and optional per-key floors are **minimum stratum probability
masses**, not per-line probabilities. Water filling fixes under-target strata at
their floors and renormalizes the rest while retaining their target ratios.
Absent strata requested with positive floors/targets, negative/nonfinite inputs,
and floors totalling >1 are rejected. No helper samples, writes a mix, changes a
partition, or starts training. Unknown axes stay explicit strata.

## Validation

`tests/test_line_metadata.py` measures all 44 original O4D strips twice and checks
finite ranges/serialization, frozen values, exact controlled raster units and
inversion, colour/alpha, blank/gradient strips, blur/speckle response, Unicode and
lexicon denominators, T2 receipt compatibility, catalogue sources, page position,
font fixture prediction/abstention, tiny fixture-only fitting, CLI/atomic failure,
real/synthetic report parity, Parquet adapter, no eager optional ML imports, and
floor guarantees. All execution is offline and CPU-only.

The final scoped run passed 93 metadata tests and 31 existing annotation/CLI/package
compatibility tests (124 total). The full shared-workspace suite was not green:
concurrent geometry-policy, vendor-provenance and new global API-inventory changes
are recorded separately in `T5_HANDOFF.json`. They were not changed to satisfy T5.

T5: done | tests: 124 passed
