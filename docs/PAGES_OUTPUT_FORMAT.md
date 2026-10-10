# Page output formats

A page result contains geometry, recognition pieces and optional measurements.
Use `result.to_records()` for JSON-ready geometry payloads and `result.files` for
paths written by an `OutputOptions` selection. Ordinary geometry uses source
pixels; physical/page units occur only in explicitly named fields. JSON numbers
retain the existing Q1/Q2 values. Curve serialization retains Q1's three-decimal
rounding; no additional rounding is applied by the new API.

This document describes public API files and the additional fields in historical
review artifacts. Historical run receipts are not manufactured by a new API call.
The strict comparison of those artifacts is in the [Q3 report](reviews/PAGE_LINES_Q3_CLEANUP_API.md).

## File selection

`KEY` is the page key, and `BOOK` is the caller's book ID.

| Output switch | Filename | Payload |
| --- | --- | --- |
| `lines` | `KEY.lines.json` | Array of fitted line records, including discounted candidates when kept. |
| `segments` | `KEY.segments.json` | Rough seed boxes with stable local segment IDs. |
| `structure` | `KEY.structure.json` | Physical leaves, boundaries, columns, blocks, rows and links. |
| `cells` | `KEY.cells.json` | Recognition-piece boxes and addresses. |
| `delivery` | `KEY.delivery.json` | The selected active line/row/piece view. |
| `rows` | `KEY.rows.json` | Existing Q1 joined-row envelope; requires joining at `rows` granularity. |
| `checks` | `KEY.checks.json` | Detector diagnostics, key, dimensions and x-height. |
| `statistics` | `KEY.stats.json` | Page statistics, aggregate groups and the glyph-table filename. |
| `statistics` | `KEY.glyphs.parquet` | Typed Q2 glyph table; with no Arrow installation, `KEY.glyphs.jsonl`. |
| `lines_image` | `KEY.lines.jpg` | Original image with active line bounds and six guides. |
| `unrolled_image` | `KEY.unrolled.jpg` | Active strips on a labeled contact sheet at a common x-height. |
| `structure_image` | `KEY.structure.jpg` | Active geometry, addresses and validated boundaries. |
| `glyphs_image` | `KEY.glyphs.jpg` | Glyph/ink classifications on the original image. |
| `orientation` | `KEY.orientation.json` | Dominant decision, proposals, groups and local-frame word records. |
| `statistics` on a book | `books/BOOK.stats.json` | Q2 book statistics. |
| `statistics` on a book | `corpus.stats.json` | Corpus statistics for the pages passed to this book call. |
| `statistics` on a book | `corpus.summary.csv` | One row per page, matching the corpus JSON's `table`. |
| `book_image` | `books/BOOK.summary.jpg` | Plot of book page summaries. |

The legacy review renderer also writes a combined `checks.json` array. Historical
orientation review runs write `KEY.words.json` and receipts, and may add links
from `cells.json`; the API's orientation envelope is deliberately named separately.
The archive's `artifact_audit.json`, round reports and timing receipts are evaluation
artifacts, not page API outputs. Their generators and paths remain in the archive.

## Shared conventions and addresses

Boxes are `[left, top, right, bottom]`, origin `TOPLEFT`, right/bottom exclusive.
A path is an array of `[x,y]` pairs. Polygon corners follow their recorded order.
Array indices are zero-based. Absent measurements and neighbours use JSON `null`;
vertical neighbour arrays use `-1` for no neighbour. IDs are local to a source
image unless prefixed with its page key. Neither an index nor an ID is recognized
text. Discounting never means silently removing the input's pixels.

Every addressed line/cell has these fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `page_side` | string | `single`, `left` or `right` physical leaf. |
| `column_id` | string | Boundary-bounded column in that leaf. |
| `block_id` | string | Text, table or diagnostic block within a column. |
| `row_id` | string | Printed row inside that block; not a semantic table grid row. |
| `piece_index` | integer | Horizontal ordinal inside the addressed row. |
| `reading_order` | integer | Order assigned by Q1; not a semantic reading model. |

## Segments, lines and delivery

Each segment record has `line_id` (`KEY-sNNNNN`) and `box` (integer source pixels).
These are detection seeds; a seed may contain more than one eventual text line.

Each line record has the address above and:

| Fields | Meaning |
| --- | --- |
| `x0`, `x1` | Integer horizontal extent; every curve has `x1-x0` samples. |
| `baseline`, `meanline` | Bottom and top of small-letter bodies, Y in source pixels. |
| `font_top`, `font_bottom` | Ascender/capital and descender guides. |
| `accent_top`, `accent_bottom` | Detached upper-mark guides. |
| `top`, `bottom` | Mutually bounded extraction ribbon, distinct from font guides. |
| `xheight` | Float fitted letter-height reference in source pixels. |
| `column` | Legacy integer detector lane; use `column_id` for Q1 structure. |
| `segment_indices` | Integer indices of source seed segments. |
| `hint_indices` | Optional provenance-only hint indices; hints never affect fitting. |
| `segment_positions` | `[segment_index, position, last_position]` placement provenance. |
| `support` | Number of body/support observations. |
| `geometry_source` | Fit origin, e.g. `joint-classes`, `borrowed`, `table-pixel-piece`. |
| `borrowed` | Guide names whose offsets lacked local evidence. |
| `ink_classes` | Counts keyed by `body_on_baseline`, `body_with_descender`, `tall_body`, `mark_above`, `mark_below`, `punctuation`, `not_text`. |
| `contrast` | Relative line contrast, retained at Q2 precision. |
| `discounted` | Rejection/supersession reason string, or null for an active line. |
| `guide_residuals` | Per guide: `count`, `median`, `p90`, `maximum`, measured in x-heights; unavailable values are null. |
| `neighbours` | `above` and `below` arrays of line indices at each X; scalar `left`/`right` line indices or null. |
| `row_source` | Optional component-row proposal provenance for a table piece. |
| `pieces` | Only on joined records: copied original addressed records. |

`delivery.json` is an array using the same line schema. It never contains
discounted candidates. In `rows.json`, `schema_version=1`, `rows` contains joined
records, `blocked_rows` lists rejected rows, `complete` says whether any were
blocked, and `geometry_policy` describes sample-preserving interpolation. The
API raises on unsafe joining before writing this file; successful API row files
have `blocked_rows=[]`. Archived Q1 audits instead saved partial rows with blocked
entries containing `row_id`, `line_indices`, `table_id`, `reason` and `crossings`.

## Cells

The envelope has `image_size=[width,height]`, `page_size=[width,height]`,
`page_units` (description), and `cells` (array). The API defaults `page_size` to
image pixels. Historical research output uses PNG pixels divided by three.
Historical optional `orientation_mode` and `orientation_output` describe and
link an independently generated orientation review.

Each cell has the shared address and:

- `index`: index in this file's `cells` array.
- `box_pixels`: tight integer source-image envelope.
- `box_page`: float box transformed using the actual independent X/Y ratios.
- `coord_origin`: `TOPLEFT`.
- `line_index`: index in `lines.json` whose curves define this crop.
- `table_id`: layout/pixel table region ID, or null.
- `cell_id`: detector piece-group ID, or null.
- `cell_id_kind`: `detector_piece_group` when an ID is present, otherwise null.
- `neighbours`: `left` and `right` **cell-array** indices, or null.

## Structure

The envelope fields are:

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer 1. |
| `image_size`, `units`, `coord_origin` | Dimensions, `source pixels`, `TOPLEFT`. |
| `id_scope` | `one source image`. |
| `neighbour_indices` | Maps `lines` and `cells` to their index-space filenames. |
| `fold` | Fold boundary object (kind/path/provenance) or null. |
| `pages` | Physical-leaf objects: `id`, `page_side`, `boundary_ids`, `polygon`. |
| `columns` | `id`, `page_side`, `boundary_ids`, `left_boundary`, `right_boundary`, `line_indices`, `reading_order`. |
| `blocks` | `id`, `column_id`, `page_side`, `table_id`, `kind` (`text`, `table`, `diagnostic`), `line_indices`. |
| `rows` | `id`, shared side/column/block addresses, `table_id`, `row_source`, `row_sources`, `discounted`, `line_indices`, `piece_indices`, `reading_order`, `box_pixels`. |
| `boundaries` | Accepted stopping paths; schema below. |
| `rejected_boundaries` | Rejected proposals with reasons and measured evidence. |
| `boundary_tracks` | `id` and constituent `boundary_ids` for one separator track. |
| `boundary_validation` | `pixel-validated` or `caller-supplied-unverified`. |
| `violations` | Line/boundary crossing inventory: `line_index`, `discounted`, `boundary_ids`. |
| `crossing_evidence` | Original-ink examination of crossings, described below. |
| `provenance` | Historical audit-only source/baseline file hashes. |

Rows in historical audits additionally contain `joinable`; the live low-level
structure builder does not add that audit outcome. `piece_indices` indexes the
cells file, while `line_indices` indexes the lines file. With `discounted="drop"`
these indices are compacted; address IDs are retained.

A boundary has `kind`, `path`, and, where applicable, `id`, `track_id`, `source`,
`table_id`, `radius` or `width` in pixels, `extent`, `proposal_id`, `proposal_path`,
`supporting_windows`, `evidence`, and `rejection_reasons`. `image_edge` boundaries
need only kind/path. `extent` retains the proposing pixel rectangle; a separator
is never assumed to continue through unrelated text. `proposal_path` preserves
the pre-validation path. `supporting_windows` are source-pixel gutter windows.

Boundary `evidence` has `method`, `accepted`, and a `checks` map. Spacing checks
are `spacing_observed`, `wide_at_local_scale`, `separate_blocks`, `persistent`,
`bilateral_support`, `original_whitespace`. Rule checks are `long_enough`,
`sustained_straight_thin_ink`, `isolated_thin_support`, `no_long_unprinted_gap`.
All are booleans. Depending on method it includes:

- Spacing: `width_px`, `width_xh`, `local_xheight_max_px`, `required_width_px`,
  `spacing_sides` (`samples`, `letter_q25_xh`, `median_xh`, `word_q75_xh`, `q90_xh`),
  `side_row_counts`, `side_span_xh`, `shared_span_xh`, `occupied_rows`,
  `bilateral_rows`, `participants` (`line_index`, `xheight`),
  `observed_gap_widths_px`, `white_rows`, `baseline_matching_reach_px`, and
  `interpiece_spacing_samples`. These quantify actual local text and whitespace.
- Rule support: `xheight_px`, `extent_xh`, `support_fraction`, `supported_rows`,
  `thin_support_fraction`, `original_ink_rows`, `sampled_rows`,
  `thickness_q90_xh`, `residual_q90_xh`, `dash_lengths_xh`, `gap_lengths_xh`,
  `style`, `validated_path`. These distinguish sustained thin strokes from
  aligned glyph stems, shadows and long unprinted gaps.
- Structural provenance: `source` identifies the original proposal supplier.

A crossing evidence object has `line_index`, `boundary_id`, `boundary_kind`,
`boundary_path`, `line_extent`, `xheight_px`, `classification`, `discounted`,
`own_ink_pixels_sides`, `common_ink_rows`, `foreground_contrast`,
`excluded_rule_components`, `rule_exclusion_margin_px`, `required_common_rows`,
`required_ink_pixels_per_side`. Historical review enrichment adds `piece_indices`,
`row_id`, and `proposal_id`. Threshold and count fields explain whether ink on
both sides establishes a real crossing; a geometric overlap alone is insufficient.

Historical structure provenance records `source_sha256`, `baseline_lines_sha256`,
`baseline_cells_sha256`, and `baseline_structure_sha256`. These identify the
particular earlier files replayed by that audit, not the current implementation.

## Detector checks

`key`, `image_size`, and `xheight` identify the image and fitted scale. Diagnostic
counts are `pixel_segments`, `final_lines`, `active_lines`, `discounted_lines`,
`multi_line_segments`, `boundary_overlaps`,
`cut_ink_lines`, `foreign_ink_lines`, `rule_gutter_crossings`, `broken_line_pairs`,
`strip_edge_touch_lines`, `source_boundary_cut_lines`, `unassigned_body_components`,
`assigned_ink_pixels`, `cut_assigned_ink_pixels`, `assigned_ink_retained_fraction`.
The last field is a ratio; pixel fields count ink pixels; other fields count
segments, lines or pairs as named.

The matching details are `overlap_pairs`, `cut_line_indices`, `foreign_line_indices`,
`crossing_line_indices`, `broken_pairs`, `strip_edge_indices`, `invalid_boundary_lines`. `checks` contains these ten diagnostic groups (not boolean verdicts):

| Group | Fields |
| --- | --- |
| `1_font_and_accent_lines` | `per_line` (`line`, `borrowed`, `distances` per guide), `borrowed_lines`. |
| `2_extra_lines` | `no_body_lines`, `close_pairs`. |
| `3_cutoffs` | `lines`, `source_boundary_lines`, `strip_edge_lines`. |
| `4_faint_detections` | `discounted` count; `per_line` (`line`, `contrast`, `discounted` reason). |
| `5_smoothness` | `per_line` (`line`, `top`, `bottom` maximum step in x-heights), `maximum`. |
| `6_column_crossings` | `lines`, `full_height_boundaries`, `all_boundaries`, `continued_rules` (`kind`, `centre`, `slope`, `radius`, `top`, `bottom`, `support_rows`). |
| `7_missed_text` | `unassigned_text_size_components`, `unassigned_text_size_ink`, `rule_mask_fraction`. |
| `8_nontext_ink` | `candidate_lines_on_detected_graphics`, `detected_graphics`, `stamp_truncation` caveat. |
| `9_headings` | `possible_broken_pairs`. |
| `10_existing_checks` | `foreign_lines`, `overlap_pairs`, `broken_pairs`, `seam_gaps` (`above`, `below`, `maximum_xh`). |

`measurement` describes the diagnostic policy. Optional
`table_delivery` contains `regions` (`id`, `box_pixels`), `pieces`, `table_pieces`,
`prefix_refitted`.

Some early frozen reviews use `candidate_segments_on_detected_graphics` for
the nontext count; current code uses `candidate_lines_on_detected_graphics`.
Legacy review checks add `source_sha256`, `implementation_sha256`, `seconds`,
`hint_comparison` (`hint_boxes`, `identical_pixel_geometry`, `source_sha256`),
and optional `nontable_review_sha256`. A new API call does not pretend to have
an earlier run's duration, implementation hash or review receipt.

## Glyph table: one row per observed entity

Parquet has a fixed nullable Arrow schema, including empty tables. Arrays `box`
and `body_box` are lists of 64-bit integers. `attached_marks` is stored as a JSON
string in Parquet and as an array in JSONL/in-memory data. Its entries have
`ink_class`, `box`, `component_id`, and `ink_pixels`. `read_statistics` restores
those strings to arrays. Missing book enrichment is null in Parquet and can be
absent in the in-memory page-only dictionary.

| Fields | Type and meaning |
| --- | --- |
| `page_key`, `book_id`, `glyph_id` | Strings: page/book identities and `KEY:glyph-NNNNNN`. Book ID can be null. |
| `line_id`, `line_index` | Nullable string/index into Q1 lines; null for residual ink. |
| `page_side`, `column_id`, `row_id`, `block_id`, `piece_index` | Nullable Q1 address. |
| `spatial_column_id` | Spatial membership without pretending residual ink is line-addressed. |
| `nearest_line_index` | Nearest line evidence; not a replacement for a null address. |
| `entity_kind` | `letter_body`, `punctuation`, `orphan_mark`, or `residual_ink`. |
| `ink_class` | `body`, `tall`, `descender`, `mark_above`, `mark_below`, `punctuation`, or `not_text`. |
| `box`, `body_box` | Whole-entity/body-only source boxes. Non-body rows have null `body_box`. |
| `attached_marks` | Detached mark evidence owned by this body. |
| `xheight_px`, `xheight_page_width`, `xheight_source` | Reference size in pixels, size/page width, and provenance of that estimate. |
| `height_xh`, `width_xh`, `body_height_xh`, `body_width_xh` | Full/body extents divided by x-height. Body-only values are nullable. |
| `rise_xh`, `depth_xh` | Body top above baseline and bottom below baseline. |
| `line_residual_xh` | Distance to closest legal body/font guide; nullable off-line. |
| `coverage_state` | `under_inked`, `over_inked`, `intact`, or null outside bodies. |
| `legacy_state`, `legacy_coverage_state` | Crop-tool verdict and its mapped coverage class. |
| `legacy_score`, `legacy_contrast_ratio` | Original crop evidence retained for audit. |
| `pieces`, `merged`, `resolved` | Crop fragment count, estimated blob multiplicity and resolution flag. |
| `thickened`, `stroke_ratio_line` | Thickening predicate and stroke width / line's median stroke width. |
| `ink_pixels`, `ink_gray`, `darkness`, `paper_gray` | Pixel count, median ink gray, `1-ink_gray/255`, local paper estimate. |
| `contrast_absolute`, `contrast_local` | `(paper-ink)/255` and `(paper-ink)/max(paper,1)`, clipped below at zero. |
| `edge_sharpness` | Median Sobel boundary magnitude × x-height / contrast (Sobel normalized by 8). |
| `color_spread`, `color_available` | Median RGB channel range / 255 and whether color was supplied. |
| `stroke_width_px`, `stroke_width_xh` | Twice median distance-transform ridge radius, in pixels/x-heights. |
| `fill`, `holes`, `hole_area`, `hole_fraction` | Ink share, hole count, hole pixels and hole share of entity box. |
| `font_group`, `font_role` | Page-local size group and `body`, `smaller`, or `larger` role. |
| `contrast_ratio`, `edge_ratio` | Ratios to the page's independently selected front-text reference. |
| `front_text`, `show_through_candidate`, `stamp_watermark_candidate`, `non_text` | Nonexclusive descriptive evidence flags. |
| `faint`, `blurred`, `line_inconsistent`, `letter_like`, `colored`, `large_blob`, `rule_like` | Individual predicates used in those flags. |
| `mirrored` | Always null: no reverse-page registration or template measurement exists. |
| `book_font_group`, `book_font_role` | Book-local font size grouping after aggregation. |
| `book_contrast_ratio`, `book_edge_ratio` | Ratios to other pages' reference, excluding this page. |
| `book_front_text`, `book_show_through_candidate`, `book_stamp_watermark_candidate`, `book_non_text` | The same candidate logic with that book reference. |
| `book_faint`, `book_blurred`, `book_line_inconsistent`, `book_letter_like`, `book_colored`, `book_large_blob`, `book_rule_like`, `book_mirrored` | Book-reference predicates. Null when independent reference is unavailable. |

Sizes use x-heights or page-width fractions. Photometric values use gray units
or explicitly defined ratios. Counts are integers. Flags are nullable booleans.
An unresolved merged blob remains one observed row; it is not silently counted
as known characters.

## Statistics JSON and aggregates

A page statistics object has `schema_version`, `page_key`, `book_id`, `image_size`,
`units`, `geometry_sha256` (canonical JSON of all input line records), `thresholds`,
`reference`, `font_groups`, `active_lines`, `discounted_lines`, `residual_detection`,
`summary`, and arrays `lines`, `rows`, `columns`, `page_sides`. The writer adds
`glyph_table`, the relative Parquet/JSONL filename. The frozen-geometry statistics
script also records `source_sha256`, `implementation_sha256`, `lines_file_sha256`,
`source_image`, and `seconds`; these are run-specific receipts.

Each aggregate contains `address` and the summary schema below. For lines/rows/
columns, `nearby_unassigned_ink` is a separate summary of spatially nearby residual
ink; it does not inflate the addressed letter denominator.

A distribution is `{n, median, p10, p90, mean, std}`. `std` is population standard
deviation. Empty distributions have `n=0` and null values. A stability distribution
also has `cv=std/mean` and `relative_p90_p10=(p90-p10)/median` where defined.

A page `reference` has `contrast_absolute`, `edge_sharpness`, `stroke_width_xh`,
`aligned_bodies`, `support`, `method`. It uses aligned bodies in the upper half
of local contrast. Each `font_groups` item has `id`, `size_page_width`
(distribution), `members`, `letter_bodies`, and `role`.

`residual_detection` has `noise_sigma_gray`, `minimum_contrast_gray`,
`reference_xheight_px`, `small_component_pixels_excluded`, `owned_ink_pixels`,
`detected_residual_pixels`, and `halo_xh`. These disclose the residual mask's
noise/contrast threshold, reference size and pixel accounting.

Each `summary` contains:

- Counts: `rows`, `letter_bodies`, `ink_pixels`, `entity_counts`, `ink_classes`,
  `font_groups`, `unresolved_merged`.
- `distributions`: distributions of `height_xh`, `body_height_xh`, `width_xh`,
  `stroke_width_xh`, `xheight_page_width`, `darkness`, `contrast_absolute`,
  `contrast_local`, `contrast_ratio`, `edge_sharpness`, `edge_ratio`, `fill`,
  `hole_fraction`, over observed bodies.
- `coverage_counts`, `coverage_shares`: maps keyed by `under_inked`, `over_inked`,
  `intact`. Shares divide by observed letter bodies, not all ink rows.
- `candidates`: `front_text`, `show_through_candidate`, `stamp_watermark_candidate`,
  `non_text`, each with `rows`, `ink_pixels`, `ink_share`.
- `legacy_agreement`: `compared`, `matched`, `fraction`, `confusion`. Confusion
  keys encode `legacy_coverage_state->coverage_state`.
- `readability_proxy`: mean of intact-indicator × local contrast × capped edge
  ratio, times 100; null without support. `readability_support` counts eligible
  bodies. `readability_factors` has `intact_share`, `mean_local_contrast`,
  `mean_edge_factor`. This is a descriptive proxy, not an accuracy estimate.

After book aggregation, page stats also have `book_reference` (`contrast_absolute`,
`edge_sharpness`, `stroke_width_xh`, `method`, `pages`, `support_pages`) and
`book_candidate_amounts`. The latter maps show-through and stamp candidates to
`rows` and `ink_pixels`, or null if no independent reference exists.

`thresholds` reproduces Q2's named values: `font_size_ratio`, `tall_rise_xh`,
`descender_depth_xh`, `mark_dx_xh`, `mark_dy_xh`, `aligned_residual_xh`,
`show_contrast_ratio`, `blurred_edge_ratio`, `off_line_residual_xh`,
`letter_min_height_xh`, `letter_max_height_xh`, `letter_max_width_xh`,
`stamp_min_width_xh`, `stamp_min_height_xh`, `stamp_contrast_ratio`, `color_spread`,
`rule_aspect`, `thick_stroke_ratio`, `thick_fill`, `paper_pad_xh`,
`residual_paper_grid_xh`, `residual_noise_sigma`, `residual_contrast_fraction`,
`residual_min_gray`, `residual_area_xh2`, `owned_halo_xh`. Their predicates and
pre-measurement reasons are specified in [Q2](reviews/PAGE_LINES_Q2_STATISTICS.md).

## Book and corpus files

A book JSON has `schema_version`, `book_id`, `pages` (count), ordered `page_keys`,
`thresholds`, `summary`, `font_groups`, `per_page`, `stability`,
`font_share_stability`. Book `summary` additionally has
`glyph_weighted_readability_proxy`; its main `readability_proxy` averages pages.
`font_share_stability` maps each book font ID to a stability distribution.

Each `per_page` record has `page_key`, `letter_bodies`, `body_size_page_width`,
`contrast`, `sharpness`, `darkness`, `readability_proxy`, `under_inked`,
`over_inked`, `intact`, `show_through_share`, `stamp_share`, `font_shares`.
The stability map covers those numeric measures except the ID/count/map fields.
`font_shares` maps book font IDs to observed-body fractions.

A corpus JSON has `schema_version`, `pages`, `books`, `letter_bodies`,
`readability_proxy` (page average), `glyph_weighted_readability_proxy`, `table`.
The CSV contains the same `table` fields: `page_key`, `book_id`, `letters`,
`residual_rows`, `readability_proxy`, `readability_support`, `darkness`,
`under_inked`, `over_inked`, `intact`, `show_through_ink_share`, `stamp_ink_share`,
`legacy_compared`, `legacy_matched`. Nulls become empty CSV cells.

## Orientation records

The API orientation envelope has `dominant`, `proposals`, `groups`, and `words`.
A decision record has `axis`, `orientation_cw`, `axis_confidence`,
`polarity_confidence`, `residual_skew_cw`, `alternatives`, `evidence` (as emitted
by the existing orientation object). Angles are clockwise degrees; an unknown
angle is null, and `alternatives` retains the candidate quarter turns. The two
confidence fields are independent dimensionless evidence scores.

Each direction proposal contains `box` (source pixels), `axis`, `components`
(support count), `axis_confidence`, and `xheight` (source pixels). Each group has
`id`, `box`, the decision fields, and either `frame` (3×3 source-to-local matrix)
or `delivery` (`table-region-preserved` or `no-local-lines`).

The decision's optional `evidence` fields are:

| Fields | Meaning |
| --- | --- |
| `component_votes`, `body_count`, `xheight` | Horizontal/vertical vote totals, supporting bodies and source-pixel size. |
| `projection_concentration` | Horizontal/vertical normalized projection variance. |
| `source`, `axis_source`, `polarity_source` | Which observation or inheritance supplied each decision. |
| `content_kind` | Caller-known content kind; numeric rows cannot orient themselves. |
| `inherited_from` | Parent group ID supplying the decision. |
| `rejected_orientation_cw`, `unapplied_candidate` | An angle withheld by group/delivery constraints. |
| `seconds` | Measured orientation runtime, not a deterministic geometric value. |
| `osd` | Optional external hint: `available`, optional `reason`, `angle`, `confidence`, `returncode`. |
| `readings` | Recognizer alternatives: `orientation_cw`, `text`, `recognition_confidence`, `score`. |
| `crop_policy`, `recognition_confidence_gap` | Recognition crop convention and the gap between hypotheses. |
| `guide_test` | Both fitted guide readings, detailed below. |

`guide_test` has `method`, `readings`, `sampled_lines`, `sample_budget`,
`orientation_cw`, `close_candidate`, and `margin_marks`. Each guide reading has
`orientation_cw`, `lines`, `class_counts`, `contacts`, `residuals_xh`, `proportions`,
`accent_above`, `mark_below`, `net_marks`, `variable_bodies`, `strong`, `close`,
and `font_disagreements`. Counts describe observed classes/contacts, residuals
use x-heights, and `proportions` maps guides to `{median, spread, lines}` signed
baseline offsets in x-heights. A sampled `lines` item contains `box` in the
sampled local raster, `xheight`, `classes`, per-guide `contacts` using the normal
count/median/p90/maximum residual schema, `borrowed`, `measured_accents`, and
`ratios` (signed guide offsets divided by x-height).

Each word contains `index`, `word_id`, `group_id`, `line_index`, `text`, `from_ocr`,
`text_direction`, `recognition_confidence`, the decision fields, `box_pixels`,
`box_page`, `corners_pixels`, `corners_page`, `coord_origin`, `local_box`,
`local_to_pixels`, `local_to_page`, `geometry_orientation_cw`,
`geometry_is_hypothesis`, `guides_local`, `guides_pixels`, `guides_page`,
`geometry_units`, `table_id`, `cell_id`. Guide maps use the same eight curve names,
but contain parametric `[x,y]` points in the stated frame. The two transforms are
3×3 homogeneous matrices. Geometry units describe `local`, `pixels`, `page`.
Text can be empty when only geometry/polarity was requested; confidence for
recognition is separate from orientation confidence.

Historical word-review envelopes additionally record source/frame and recognizer
provenance. Refer to the preserved [orientation report](reviews/PAGE_LINES_ROUND4_ORIENTATION_20261009.md)
and its archived generator when replaying those exact receipts.
