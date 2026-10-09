# Q2 — descriptive glyph statistics

## Definitions and decisions fixed before measurement

This specification was written before running Q2 on either page collection.
No reader, PDF text, fitted classifier or page-name rule is used. A glyph row is
an observed letter body plus its detached marks, using `line_glyphs`,
`letter_boxes` and `ink_profile`. An unresolved merged blob remains one row with
its estimated multiplicity and `resolved=false`; it is not asserted to be one
Unicode character. Punctuation, unattached marks and residual ink are separate
rows (`entity_kind`); they do not inflate the letter denominator. Missing ink
which leaves no pixels is unobservable. Boxes are exclusive source-pixel boxes.

Q1 line records, their curves and `page_side`, `column_id`, `row_id` are read-only.
Only active lines provide addresses and front-text references. Residual ink has
null line/row/column addresses, a spatial page side when Q1 supplies it, and an
explicit nearest-line evidence field. Column spatial membership uses the Q1 left/right boundary paths at the ink-box centre, only when exactly one column contains it. Line/row/column aggregates expose this ink separately as `nearby_unassigned_ink`, never as additional addressed letters. Discounted lines are never drawn. Glyph
boxes are an added layer, not edits to line, cell or structure outputs.

### Size and ink class

`xheight_px` is the supplied Q1 line x-height; outside lines use the median active
line x-height and declare that source. If no active line exists, the residual detector uses 1% of the shorter page dimension as an explicit page-unit fallback, never a measured font size. Height, width and stroke width are divided
by this x-height. Stroke width is twice the median positive distance-transform
ridge radius. Body height excludes attached marks; full height includes them.
Ink classes follow the six-guide design: rise above baseline >1.24 xh is tall;
depth below baseline >0.22 xh is descender; otherwise body. Both rise and depth
remain recorded. Small detached ink with a body within 0.45 xh horizontally and
0.8 xh vertically is attached as mark above (bottom < baseline−0.8 xh) or below
(top >= baseline−0.1 xh). These are existing guide-design tolerances, allowing
breathings beside capitals and subscripts. Other small ink is punctuation;
large/rule/residual ink is not text unless the evidence supports a candidate.

Font groups are deterministic ascending complete-span clusters of line
xheight/page width: largest/smallest <=1.25 in each cluster. A quarter-size change
is the declared separation between type sizes; this avoids chaining a continuum
into one group. The group containing most letter rows is `body`; others are
`smaller` or `larger`, not claims of semantic footnotes/headings. Book groups use
the same normalized scale, not raw pixels, and IDs are book-local. Scan crop
changes can therefore still affect the comparison.

### Photometry

All grayscale values use [0,255], white=255. For each observed mask:

- Ink level I = median gray on its ink pixels; darkness D = 1−I/255.
- Local paper P = 90th percentile of the surrounding box padded by 0.5 xh,
  excluding the ink's bounding rectangle; if empty use page p90. This is a
  local-paper estimate, not a calibrated reflectance measurement.
- Absolute contrast C = max(0,P−I)/255; local-paper contrast = max(0,P−I)/max(P,1).
- Normalized edge sharpness E = xh × median boundary Sobel magnitude/8 /
  max(P−I,1). Scaling the edge gradient by xh expresses transition width in
  typographic units. Borders without an exterior sample do not vote.
- Color evidence = median pixel (max(R,G,B)−min(R,G,B))/255. Grayscale inputs
  declare color unavailable; zero is not evidence of absence of a colored stamp.
- Page front reference: median C, E and stroke/xh among geometrically aligned
  letter bodies in the upper half of their local-paper contrasts. Alignment
  means minimum top/body-guide or bottom/baseline-guide residual <=0.22 xh.
  If none exist the reference is unavailable, not an invented unit contrast.
- Page-relative contrast and sharpness = C/C_ref and E/E_ref. Book references
  are medians of other pages' front references (leave-one-page-out), equally
  weighting pages. One-page books have no independent book reference. The
  included page medians and their support counts are stored.

### Coverage and provenance thresholds

Coverage starts with the crop tool: broken/faint -> under-inked; merged ->
over-inked; intact -> intact. In addition, an otherwise intact letter with
stroke/xh >=1.75 times its line median AND fill >=0.65 is over-inked. A 75% stroke
increase with at least 65% box fill signals thickening, while protecting naturally
wide letters with open counters. Broken takes precedence over merged. Store
pieces, multiplicity, legacy state/score, line-relative contrast, stroke ratio,
fill, hole count and hole-area/box-area as evidence. Closed counters cannot be
proved without an intact template; zero holes alone never triggers over-inking.
The 0.5 contrast cutoff is inherited from `ink_profile`, not tuned here. Fading
is an intensity proxy, not a measured fraction of missing expected strokes.

Provenance flags are nonexclusive descriptive candidates, with every predicate
stored. Show-through: contrast/reference <0.5, letter-like extent (height
0.3–2.8 xh and width <=3 xh), plus either edge/reference <0.65 or line residual
>0.35 xh or no assigned line. These require at least half the front contrast lost,
and a one-third blur loss or substantial misalignment. Stamp/watermark:
line-inconsistent ink with color spread >0.10; OR a non-rule residual blob
spanning >=3 xh wide and >=2.8 xh high with contrast/reference <0.85.
The size condition exceeds a single character; the contrast condition requires
a 15% separation from front ink. A rule is aspect ratio >=10. A grayscale stamp
made of disconnected ordinary dark letters can be missed. Front-text candidate:
addressed body/mark/punctuation, contrast/reference >=0.5, and neither candidate
flag. Non-text: residual ink without either candidate, or geometric not-text.
Mirroring is **unmeasured**: no recognition/template or reverse-page registration
is available. No flag asserts a known physical ink origin.

Residual mask: original grayscale below local paper minus max(10 gray levels,
4 times estimated bright-paper noise, 0.15 times page front contrast in gray
levels). Local paper is a coarse 90th-percentile grid at 4 xh spacing, interpolated
to source pixels. This detects faint residual ink separately from line binarization.
Noise is 1.4826 times MAD of pixels above page p75, sampled on a regular grid.
Residual components smaller than 0.02 xh² are excluded and their pixel count is
reported. Already assigned pixels and a 0.08 xh halo are excluded to avoid counting
antialiasing as a second letter. All pixel rounding has a one-pixel lower bound.

### Aggregates, stability and readability

Every line (piece index), printed row, column, page side, page and book reports
count, size/font distributions, darkness/contrast/sharpness median, p10, p90,
mean and standard deviation; coverage shares divide by letter-body count.
Candidate amount is both row count and observed ink-pixel area/share, **not**
estimated physical stamp area. Empty denominators are null. Per-book stability
is population SD/mean (CV) and (p90−p10)/median of per-page measurements; fewer
than two pages gives null stability. Font stability additionally reports the
per-page body size/page width and book font-group shares.

A descriptive `readability_proxy` is 100 times the mean, over addressed letter
bodies, of intact_indicator × local_paper_contrast × min(1,E/E_ref). It ranges
from 0 to 100, is not calibrated to human or OCR accuracy, and penalizes all
observed defects equally. Also publish the three factors separately, coverage
support, unresolved-merge count, and candidate ink share. Corpus score is the
unweighted mean of nonempty page scores; glyph-weighted score is reported
separately. Book score uses the same page weighting. Zero letters -> null score.

### Validation plan

Freeze SHA-256 of every pre-existing `.astra/out/` file, then verify byte identity.
Use frozen Q1 development records (already delivered with `.astra/layout`); run
the unchanged Q1 pipeline on the 41 new book pages. Compare old/new coverage
labels on identical letter boxes, with a confusion table (reuse is not independent
accuracy). Review owner-case regions on original images before computing their
numeric summaries; report those regions and text controls side by side, including
misses. Compare page vs independent book contrast separation only where both
references exist; do not infer accuracy from self-selected candidate groups.
Run the entire offline test suite and report skips separately.

## Results

The implementation adds `greekocr.glyphs.statistics`; existing geometry and crop-tool source files were not edited. The CLI consumes the existing Q1 records and stores a typed Parquet table, JSON aggregates and a glyph overlay for each image. Attached-mark evidence is a JSON string column in Parquet (a list in JSONL). Empty pages have the same Arrow schema as populated pages. `body_box=null` distinguishes non-body ink. The table has one observed body per row, with unresolved merged bodies explicitly marked.

| Cohort | Pages | Observed letter bodies | Page-weighted readability proxy |
|---|---:|---:|---:|
| Development | 54 | 130,272 | 56.32 |
| Six-book validation cohort | 41 | 118,708 | 53.11 |
| Combined corpus | 95 | 248,980 | 54.93 |

Combined glyph-weighted readability proxy: **57.51**. These are uncalibrated descriptive scores, not percentages correctly read. No OCR text layer was read.

### Stability across the requested 41 book pages

This table uses only `.astra/book_pages/selection.json`, without development-page additions. CV is population SD/mean; n=1 cannot establish stability. Size is the dominant page group’s median xheight/page width. The number of groups is the book-wide deterministic size clustering, not the number of font families.

| Book | Pages | Letters | Book size groups | Body size CV | Front contrast CV | Edge sharpness CV | Intact share mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0ce9d1025b3f23c7119e | 1 | 3,897 | 8 | unavailable | unavailable | unavailable | 66.59% |
| 1be60011c435 | 8 | 14,359 | 5 | 2.46% | 0.00% | 2.89% | 79.80% |
| 49598b2e848ab1f0ee1e | 8 | 42,094 | 5 | 3.16% | 2.85% | 2.13% | 87.63% |
| 9de6cda8f03f0fc60a58 | 8 | 42,960 | 7 | 2.90% | 3.76% | 0.50% | 85.99% |
| d6fd2cf2f618 | 8 | 8,318 | 3 | 1.80% | 3.98% | 2.91% | 71.49% |
| ef481610a820 | 8 | 7,080 | 4 | 1.72% | 5.77% | 3.55% | 59.49% |

| Book | Book groups present per page | Dominant book-group share range |
|---|---:|---:|
| 0ce9d1025b3f23c7119e | 8–8 | 42.19%–42.19% |
| 1be60011c435 | 3–5 | 53.62%–95.31% |
| 49598b2e848ab1f0ee1e | 3–4 | 61.76%–98.65% |
| 9de6cda8f03f0fc60a58 | 2–7 | 95.14%–99.25% |
| d6fd2cf2f618 | 1–3 | 91.81%–100.00% |
| ef481610a820 | 1–4 | 82.22%–100.00% |

Across the five multi-page books, dominant size CV is **1.72–3.16%** and front-contrast CV is **0–5.77%**. This supports consistency of the dominant size and sampled ink profile, but **not uniform font-group membership**: the dominant book group ranges from 53.62% to 95.31% of bodies in `1be60011c435`, and from 61.76% to 98.65% in `49598b2e848ab1f0ee1e`. Size variation, page content, inherited guide errors and fixed cluster boundaries can all contribute; no labelled font inventory identifies their separate effects.

Full distributions, font shares on each page, coverage-state stability, candidate amounts and page-by-page values are in each `book_pages/books/<book>.stats.json`, with the adjacent summary figure. The combined `books/` directory uses all staged pages of that book; per-page book-relative columns explicitly list the other pages used.

### Owner cases: regions selected on original images

The region coordinates and selection notes are in `PAGE_LINES_Q2_OWNER_REGIONS.json`. Magenta rectangles in `<key>.stats-regions.jpg` show the ink regions; green rectangles show front-text controls. Region ink includes all detected row centres in that rectangle; text controls include observed letter bodies. Thus the stamp samples can contain overlapping front print, and faint regions can contain noise. These are descriptive region comparisons, not labelled character accuracy. Medians are row-weighted. D=darkness, C=local-paper contrast, Cp=page-relative contrast, E=edge sharpness in typographic units.

| Page / sample | Rows | D | C | Cp | E |
|---|---:|---:|---:|---:|---:|
| s2-d1ed1c2db37f431f4acb-p00001 / show-through region | 43 | 0.220 | 0.104 | 0.187 | 6.395 |
| s2-d1ed1c2db37f431f4acb-p00001 / text control | 1,176 | 0.631 | 0.567 | 1.000 | 11.112 |
| s2-0ce9d1025b3f23c7119e-p00001 / show-through region | 3,273 | 0.235 | 0.109 | 0.190 | 6.118 |
| s2-0ce9d1025b3f23c7119e-p00001 / text control | 466 | 0.633 | 0.570 | 0.972 | 10.096 |
| s2-5ca02b142a2a3eaf078a-p00002 / show-through region | 15 | 0.212 | 0.140 | 0.162 | 7.997 |
| s2-5ca02b142a2a3eaf078a-p00002 / text control | 1,172 | 0.769 | 0.762 | 0.962 | 10.380 |
| s2-09f5dfca4af4d74173c6-p00005 / show-through region | 5,470 | 0.278 | 0.120 | 0.194 | 7.468 |
| s2-09f5dfca4af4d74173c6-p00005 / text control | 1,406 | 0.655 | 0.585 | 0.961 | 10.458 |
| an-d6fd2cf2f618-p000047 / stamp region | 117 | 0.263 | 0.183 | 0.350 | 6.856 |
| an-d6fd2cf2f618-p000047 / text control | 535 | 0.525 | 0.487 | 0.939 | 8.974 |
| an-3352d912f2e9-p000104 / stamp region | 133 | 0.267 | 0.162 | 0.263 | 6.642 |
| an-3352d912f2e9-p000104 / text control | 301 | 0.624 | 0.578 | 0.935 | 8.218 |

| Region | Page show-through flags | Page stamp flags | Book show-through flags | Book stamp flags |
|---|---:|---:|---:|---:|
| s2-d1ed1c2db37f431f4acb-p00001 | 23/43 | 4/43 | unavailable | unavailable |
| s2-0ce9d1025b3f23c7119e-p00001 | 2110/3273 | 1/3273 | 2110/3273 | 1/3273 |
| s2-5ca02b142a2a3eaf078a-p00002 | 8/15 | 0/15 | unavailable | unavailable |
| s2-09f5dfca4af4d74173c6-p00005 | 2616/5470 | 0/5470 | unavailable | unavailable |
| an-d6fd2cf2f618-p000047 | 37/117 | 4/117 | 37/117 | 4/117 |
| an-3352d912f2e9-p000104 | 63/133 | 1/133 | unavailable | unavailable |

### Page-relative versus book-relative ink

For each independently selected ink region, faint-ranking AUC = P(region contrast < text-control contrast), with ties counted half. It describes contrast separation in those rectangles; it does not validate physical provenance. Threshold share is the fraction with relative contrast <0.5. Book references use all available companion pages and always exclude the evaluated page.

| Page | Other reference pages | Region Cp / Cbook | AUC page / book | Region below 0.5 page / book | Text below 0.5 page / book |
|---|---:|---:|---:|---:|---:|
| s2-d1ed1c2db37f431f4acb-p00001 | 0 | 0.187 / unavailable | 1.000 / unavailable | 100.00% / unavailable | 3.74% / unavailable |
| s2-0ce9d1025b3f23c7119e-p00001 | 1 | 0.190 / 0.207 | 0.998 / 0.998 | 100.00% / 100.00% | 6.22% / 5.58% |
| s2-5ca02b142a2a3eaf078a-p00002 | 0 | 0.162 / unavailable | 1.000 / unavailable | 100.00% / unavailable | 0.00% / unavailable |
| s2-09f5dfca4af4d74173c6-p00005 | 0 | 0.194 / unavailable | 1.000 / unavailable | 99.95% / unavailable | 0.14% / unavailable |
| an-d6fd2cf2f618-p000047 | 8 | 0.350 / 0.329 | 0.921 / 0.921 | 64.96% / 65.81% | 0.75% / 0.75% |
| an-3352d912f2e9-p000104 | 0 | 0.263 / unavailable | 0.939 / unavailable | 75.94% / unavailable | 1.99% / unavailable |

**Book normalization cannot improve within-page contrast ranking:** dividing both samples by the same positive reference preserves their ordering. It can change fixed-threshold decisions and comparability across pages. In the `0ce…` case, the text-control share below half contrast changes from 6.22% to 5.58% while the faint-region share remains 100%; in the `d6fd…` stamp case the region share changes from 64.96% to 65.81%, with the text-control share unchanged at 0.75%. These are small threshold movements, not evidence of generally better provenance classification. The 41-page cohort has no independently labelled front/show-through/stamp masks; accuracy improvement across that cohort is unmeasured.

### Agreement with the crop tools

**247,376/248,980 = 99.36% agreement** after mapping broken/faint to under-inked and merged to over-inked. There are 1,977 unresolved merged body rows among 550,174 total observed body/mark/punctuation/residual rows. This agreement is on the same boxes and the frozen Q1 band: it measures compatibility with reused crop-tool evidence, not an independent validation against human-labelled intact letters.

| Crop-tool mapped state → Q2 state | Bodies |
|---|---:|
| intact->intact | 203,254 |
| intact->over_inked | 1,604 |
| over_inked->over_inked | 12,289 |
| under_inked->under_inked | 31,833 |

### Mandatory gates and reproducibility

- Q1 preservation: **744/744 pre-existing output files byte-identical**; changed files: `[]`. This is stronger than comparing only line, piece and address fields.
- Book geometry preservation: **164/164 line/cell/structure/segment files byte-identical** after statistics. The unchanged Q1 renderer produced them; SHA-256 values are in the machine report.
- Artifact audit: **95 pages, 550,174 rows, zero failures**. Checked source/implementation hashes, exclusive boxes inside images, unique IDs, Q1 addresses, null residual addresses, consistent Arrow schemas, exact pixel accounting and valid overlay dimensions/JPEGs.
- Full offline tests: **2248 passed, 16 skipped, 0 failures, 0 errors** (2264 collected). Chromium is unavailable for the 16 existing browser-dependent skips. The existing Docling deprecation warning remains.
- Sixteen new tests cover immutable geometry, body/mark ownership, exact synthetic photometry, scale normalization, residual addresses, candidate evidence, broken/faint/merged compatibility, duplicate rejection, independent book references, empty denominators, stable Parquet schema, nullable-box roundtrip, JSONL fallback, spatial column totals and inherited rule exclusions.

Commands (from the worktree root, with the queue’s Python interpreter):

```sh
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
python scripts/glyphs/render_page_line_segments.py --pages .astra/book_pages --out .astra/out/book_pages
python scripts/glyphs/build_statistics.py --collection .astra/pages .astra/out --collection .astra/book_pages .astra/out/book_pages --resume
python scripts/generate_api_docs.py
python -m pytest -q -p no:cacheprovider --junitxml=.astra/q2-tests.xml
python scripts/glyphs/review_statistics.py
```

The existing development Q1 records were consumed in place; they were already generated with `.astra/layout`. Re-running the statistics command verifies source-image, line-file and implementation hashes before reusing measurements. Parquet tables carry schema version and threshold metadata. The review script needs the frozen `.astra/q2-q1-before.json` and `.astra/q2-book-q1-before.json` receipts for its byte-identity gates. It inventories the 95 input PNG keys, excluding pre-existing optional orientation artifacts.

### Deliverables

- `greekocr/glyphs/statistics.py`: per-page, per-book and per-corpus functions; persistence and review renderers.
- `scripts/glyphs/build_statistics.py` and `scripts/glyphs/review_statistics.py`: reproduction and audit.
- `tests/glyphs/test_statistics.py` and regenerated `docs/API.md`.
- `.astra/out/<key>.glyphs.parquet`, `.stats.json`, `.glyphs.jpg` for 54 development pages; the same under `.astra/out/book_pages/` for 41 book pages.
- `.astra/out/books/<book>.stats.json` and `.summary.jpg`; a separate six-book/41-page cohort under `.astra/out/book_pages/books/`.
- `.astra/out/corpus.summary.csv` and `corpus.stats.json`; the 41-page cohort also has its own summary files.
- `docs/reviews/PAGE_LINES_Q2_STATISTICS.json`: machine-readable results, region comparisons, book stability, tests and preservation hashes.

### Limitations and observed failures

- Development checks exposed a nullable fixed-size Arrow-list readback error and a rule-as-punctuation regression. Both were corrected; the final full suite above passes. The failed regression log is retained in `.astra/q2-tests-before-rule-fix.log`. Sparse crop fits emit the existing `RankWarning`; these did not abort any page.
- These rows describe observed ink, not guaranteed character counts. Inherited split/merge errors and missed Q1 lines remain; unresolved merged blobs are not silently expanded into fictional letters. Entirely absent strokes or characters cannot be counted.
- Fused marks remain part of their connected body; detached marks have explicit ownership. Body class can therefore be affected by fused accents. No character identity or intact template exists to prove that a counter has filled in.
- The residual pass detects paper texture, specks and some edge halos. Show-through candidates are not confirmed back-page characters, and stamp fragments can also trigger show-through flags. Candidate flags are deliberately nonexclusive.
- The known show-through regions also receive **4 stamp flags in `d1ed…` and 1 in `0ce…`**. Conversely the two stamp regions receive **37 and 63 show-through flags**. This is observed confusion between the candidate mechanisms; the flags do not reliably separate physical ink origins.
- All **95** source pages are grayscale and provide no color evidence. Mirroring and registered reverse-page correspondence are unmeasured. Disconnected dark stamp lettering may be missed, and the conservative size rule does not label every part of a stamp.
- The subtle `s2-5ca02b142a2a3eaf078a-p00002` bottom-margin sample is not independently separable into faint letters versus paper texture; its statistics cannot certify successful show-through detection.
- A one-page validation book has no measurable across-page stability. Font grouping describes relative size, not font identity or semantic heading/footnote roles. Variable crops and inherited x-height errors can shift book-relative group assignments.
- Readability is an explicit uncalibrated proxy. No claim of improved OCR accuracy, human readability prediction, or provenance-classification accuracy is supported by these unlabelled pages.

### Commit handoff

Git staging was blocked by the sandbox: creating the worktree `index.lock` returned `Operation not permitted`. The queue-authorized fallback is `.astra/Q2-statistics.patch` plus `.astra/commit-Q2.sh`, with source hashes in `.astra/q2-commit-files.json`. The patch passed reverse application checking against this working tree and forward checking against a separate index populated from the committed Q1 HEAD. No push was attempted.
