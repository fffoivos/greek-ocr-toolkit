# O6-prep — Docling image layout + current line segmentation

Original preparation completed 2026-10-07 on CPU, offline, without OCR, installs, training edits or sub-agents. The original review personally inspected **all 40 page overlays** on ten contact sheets. O6-fix regenerated GT, metrics, tables, overlays and sheets from source PDFs after CP-O6prep H1; all overlay hashes remain identical, preserving those visual observations. This is the early F05 geometry diagnostic, not O6 recognizer, compact-variant or Core ML qualification.

## Result

On the 20 digital pages, **3,497 / 28,635 visible GT glyphs (12.21%) have zero line-box coverage**. **3,920 (13.69%) have less than 95% union-area coverage**, including those entirely missed. **7 glyphs (0.0244%) are split across line boxes**. There are **12 / 558 detected digital line boxes with no GT glyph intersection (2.15%)**, all on CSP_291 p20: visual inspection shows raster text in chart legends/captions/notes, so these are not proven false positives. The 20 true scans have **462 line boxes**, but no GT-based omission score.

The largest digital omissions are CGK_278 p141 (table, 99.28%), HTH_449 p163 (form/questionnaire, 95.73%) and AWU_928 p193 (tables, 85.86%). These reflect the text-block-only path; a recognizer cannot recover regions never offered as line crops. VJC_464 p52 also loses most footnotes (12.70% page omission). Good prose/column coverage on other pages cannot establish page completeness.

## Reproduction and provenance

```sh
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  ~/Projects/glossapi-development/.venv-docling/bin/python \
  -m bench.page_slice --out bench/runs/O6_prep_20261007

HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  ~/Projects/glossapi-development/.venv-docling/bin/python -m pytest bench/tests -q
```

Tool: [bench/page_slice.py](../../bench/page_slice.py). Tests: [test_page_slice.py](../../bench/tests/test_page_slice.py). Run artifacts: [manifest](../../bench/runs/O6_prep_20261007/manifest.json), [results](../../bench/runs/O6_prep_20261007/results.jsonl), [CSV](../../bench/runs/O6_prep_20261007/table.csv), [receipt](../../bench/runs/O6_prep_20261007/receipt.json), [inspection](../../bench/runs/O6_prep_20261007/inspection.json). Individual page images, overlays and GT/geometry JSON are under `bench/runs/O6_prep_20261007/pages/`.

PDFium renders at **200 dpi**. All boxes use rendered-page pixels, top-left origin. GT now decodes adjacent UTF-16 surrogate units into one Unicode code point before geometry filtering, unions their PDF boxes, and retains both `source_indices` and `source_codepoints`. Other coincident glyphs remain distinct; unpaired surrogates retain U+FFFD. GT is recomputed with `bench.extract_lines.char_records`, `valid_box`, `pixel_box` and `group_chars`, without admission filtering. Every source PDF hash matches its O1d receipt. The receipt binds source/segmentation code, model/config hashes, package versions and output hash. External inputs are the repaired PDFs in `~/Projects/glossapi-ocr-local/experiments/compute_reduction_20261006/e1_final/repaired` and the three specified scan PDFs; they are read only.

Docling **2.81.0**, docling-ibm-models **3.15.0**, default **Heron / RTDetrV2**, cached revision `8f39ad3c0b4c58e9c2d2c84a38465abf757272d8`, threshold 0.3, CPU with four threads, 640×640 internal layout input. Its standard `LayoutPostprocessor` confidence filtering/remapping/overlap handling is applied with **skip_cell_assignment=True**, **keep_empty_clusters=True**, **create_orphan_clusters=False**. No PDF GT cells, OCR or text content enter detection. Raw proposals are retained separately in every receipt; they are not counted as final blocks. Initial raw-only inspection exposed duplicate proposals, particularly on rotated captions; final numbers and sheets use Docling's standard postprocessing.

Inside each text-family block (including captions, headers, footers, footnotes and formulas), reuse the **unchanged** `bench.source_wikisource.segment_lines`: O1 horizontal projection plus 8-connected component cleanup, quantized Otsu adaptation, tight component unions and three-pixel line padding. Crops round outward to integral pixels and offsets map results back onto the page. Tables, forms, key_value_region blocks, indexes, pictures and containers stay visible/recorded but have no text-line segmentation. No new detector, column repair, block expansion, deskew, orientation correction or custom deduplication was added. Rules tuned for full scan pages now act within sometimes very tight blocks; this can remove legitimate components or cut glyphs.

Selection: two pages each from ten repaired PDFs, mixing the known O1 column/table/formula failure cases with fixed p20/p50 pages from other types. It is a diagnostic slice, not a random corpus quality estimate. Digital fonts include **Times New Roman, Palatino Linotype, Calibri, Cambria Math and Arial**, with bold/italic variants; exact per-page font counts are in JSON. Source document-type labels below come from O1 metadata and are not validated genre claims (e.g. CSP_291 is tagged νοταριακό but the selected content is educational policy). The scans use seven spread-out pages each from VJM_898/VZE_306 and six from XEK_118; two blank VJM leaves are retained as noise controls. All three scan PDFs have zero text-layer characters on the sampled pages.

## CP-O6prep correction and remaining review note

H1 is corrected at the shared extractor, covering both page GT and native-line candidates. AWU_928 p100 contains 174 pairs and changes from GT/missed/clip/split **890/45/79/12** to **716/34/57/7**. No other page's coverage metrics change. Native-line labels now contain decoded non-BMP mathematical letters, and source adjacency checks use the last index in each pair. Historical O1d candidate artifacts were not regenerated by this O6 fix.

Reproduce the GT-only refresh with the requested extractor environment (the original inference command above still requires the Docling environment):

```sh
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  ~/Projects/glossapi-development/.venv-exp/bin/python \
  -m bench.refresh_page_slice_gt --out bench/runs/O6_prep_20261007
```

The receipt records the preceding results/code hashes and totals, the refresh script hash, and explicit reuse of historical detection and timing. Original visual review remains applicable because all 40 regenerated overlay hashes match its inspection record; the sheets were rebuilt with corrected shares.

M1 remains a logged coordinate limitation: this task retains nominal 200 dpi mapping. The review measured up to 0.566 pixel difference from PDFium's rounded render-size affine, affecting three missed and one clipping classification. With surrogate coalescing plus that affine, candidate totals would be 3,500 missed and 3,921 clipped, with 7 split. A future mapping change must regenerate geometry and scores; the current numbers isolate the surrogate correction. L1 wording now names excluded `key_value_region` blocks accurately; L2 hardware identity is supplied above from the review evidence.

## Metric definitions

- Denominator: one glyph per Unicode code point (not per UTF-16 code unit), for every non-whitespace, non-separator GT glyph with finite positive-area char geometry, including table/form text, digits and punctuation. No native-line admission gate filters GT. Whitespace and invalid/degenerate boxes are excluded and counted in page JSON.
- **Missed**: GT character box has **zero positive-area intersection** with every detected line box. Boundary contact alone gives no coverage.
- **Clip**: exact union of intersections covers **less than 95%** of the GT character box. This includes missed characters; a one-pixel sliver cannot hide a clipping failure. Red overlays mark this broader uncovered set.
- **Split**: at least two line boxes intersect the glyph, no single box covers 95%, and at least two boxes contribute unique covered area. It can overlap Clip. Identical/contained duplicate line boxes are not counted as splits; multiply intersected chars are recorded separately.
- **Empty**: detected line box intersects no eligible GT glyph. This is an empty-GT proxy, not a guaranteed figure/noise classification: digital pages can embed raster text. Scan metrics are deliberately null, never zero.

The exact rectangle-union metric never double-counts overlapping padding. Glyph-area coverage is geometry, not recognition accuracy, baseline purity, reading order or CER. In particular, raster lettering inside otherwise digital PDFs is invisible to this GT: CSP_291 p20 has just 58 eligible glyphs despite a visibly text-rich chart page. Figure captions/labels inside raster images need human review or future labels.

## Per-page measurements

`B` = text blocks / all postprocessed blocks; `L` = line boxes. Missed, Clip and Split are count / GT share. Timing columns show **wall / process CPU seconds** separately for layout (inference plus standard postprocessing) and current segmentation. CPU sums work across threads. Dash means no scan GT.

| Page | Source type | B | L | GT | Missed | Clip | Split | Empty | Layout wall/CPU s | Segment wall/CPU s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [COO_642-p0143](../../bench/runs/O6_prep_20261007/pages/COO_642-p0143-overlay.png) | thesis | 7/8 | 28 | 791 | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | 0 | 0.213/0.420 | 0.054/0.054 |
| [COO_642-p0153](../../bench/runs/O6_prep_20261007/pages/COO_642-p0153-overlay.png) | thesis | 5/5 | 79 | 2380 | 0 / 0.00% | 13 / 0.55% | 0 / 0.00% | 0 | 0.213/0.421 | 0.132/0.132 |
| [AWU_928-p0100](../../bench/runs/O6_prep_20261007/pages/AWU_928-p0100-overlay.png) | thesis | 18/18 | 42 | 716 | 34 / 4.75% | 57 / 7.96% | 7 / 0.98% | 0 | 0.215/0.425 | 0.147/0.147 |
| [AWU_928-p0193](../../bench/runs/O6_prep_20261007/pages/AWU_928-p0193-overlay.png) | thesis | 4/10 | 6 | 969 | 832 / 85.86% | 832 / 85.86% | 0 / 0.00% | 0 | 0.206/0.411 | 0.014/0.014 |
| [CGK_278-p0060](../../bench/runs/O6_prep_20261007/pages/CGK_278-p0060-overlay.png) | text | 1/1 | 7 | 396 | 2 / 0.51% | 10 / 2.53% | 0 / 0.00% | 0 | 0.206/0.408 | 0.030/0.030 |
| [CGK_278-p0141](../../bench/runs/O6_prep_20261007/pages/CGK_278-p0141-overlay.png) | text | 1/2 | 1 | 416 | 413 / 99.28% | 413 / 99.28% | 0 / 0.00% | 0 | 0.206/0.410 | 0.002/0.002 |
| [HTH_449-p0080](../../bench/runs/O6_prep_20261007/pages/HTH_449-p0080-overlay.png) | article | 7/8 | 61 | 2177 | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | 0 | 0.208/0.411 | 0.132/0.132 |
| [HTH_449-p0163](../../bench/runs/O6_prep_20261007/pages/HTH_449-p0163-overlay.png) | article | 4/6 | 5 | 1733 | 1659 / 95.73% | 1659 / 95.73% | 0 / 0.00% | 0 | 0.215/0.418 | 0.008/0.008 |
| [VJC_464-p0020](../../bench/runs/O6_prep_20261007/pages/VJC_464-p0020-overlay.png) | άρθρο | 7/8 | 28 | 1525 | 10 / 0.66% | 11 / 0.72% | 0 / 0.00% | 0 | 0.208/0.411 | 0.085/0.085 |
| [VJC_464-p0052](../../bench/runs/O6_prep_20261007/pages/VJC_464-p0052-overlay.png) | άρθρο | 5/5 | 37 | 2338 | 297 / 12.70% | 315 / 13.47% | 0 / 0.00% | 0 | 0.208/0.412 | 0.121/0.120 |
| [GMA_704-p0020](../../bench/runs/O6_prep_20261007/pages/GMA_704-p0020-overlay.png) | διάλεξη | 9/9 | 38 | 2623 | 45 / 1.72% | 158 / 6.02% | 0 / 0.00% | 0 | 0.215/0.421 | 0.121/0.121 |
| [GMA_704-p0050](../../bench/runs/O6_prep_20261007/pages/GMA_704-p0050-overlay.png) | διάλεξη | 12/13 | 31 | 2238 | 187 / 8.36% | 188 / 8.40% | 0 / 0.00% | 0 | 0.216/0.427 | 0.098/0.098 |
| [BIK_230-p0020](../../bench/runs/O6_prep_20261007/pages/BIK_230-p0020-overlay.png) | journal | 5/6 | 22 | 1429 | 2 / 0.14% | 53 / 3.71% | 0 / 0.00% | 0 | 0.212/0.422 | 0.070/0.070 |
| [BIK_230-p0050](../../bench/runs/O6_prep_20261007/pages/BIK_230-p0050-overlay.png) | journal | 4/5 | 23 | 1562 | 1 / 0.06% | 38 / 2.43% | 0 / 0.00% | 0 | 0.212/0.422 | 0.071/0.071 |
| [ESD_511-p0020](../../bench/runs/O6_prep_20261007/pages/ESD_511-p0020-overlay.png) | βιβλίο | 7/7 | 34 | 2013 | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | 0 | 0.199/0.426 | 0.130/0.130 |
| [ESD_511-p0050](../../bench/runs/O6_prep_20261007/pages/ESD_511-p0050-overlay.png) | βιβλίο | 8/8 | 32 | 1917 | 5 / 0.26% | 25 / 1.30% | 0 / 0.00% | 0 | 0.213/0.425 | 0.123/0.123 |
| [FUT_255-p0020](../../bench/runs/O6_prep_20261007/pages/FUT_255-p0020-overlay.png) | παρουσίαση | 5/8 | 10 | 567 | 4 / 0.71% | 4 / 0.71% | 0 / 0.00% | 0 | 0.210/0.415 | 0.035/0.035 |
| [FUT_255-p0050](../../bench/runs/O6_prep_20261007/pages/FUT_255-p0050-overlay.png) | παρουσίαση | 3/3 | 19 | 590 | 0 / 0.00% | 15 / 2.54% | 0 / 0.00% | 0 | 0.210/0.417 | 0.036/0.036 |
| [CSP_291-p0020](../../bench/runs/O6_prep_20261007/pages/CSP_291-p0020-overlay.png) | νοταριακό | 11/17 | 14 | 58 | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | 12 | 0.225/0.433 | 0.027/0.027 |
| [CSP_291-p0050](../../bench/runs/O6_prep_20261007/pages/CSP_291-p0050-overlay.png) | νοταριακό | 10/10 | 41 | 2197 | 6 / 0.27% | 129 / 5.87% | 0 / 0.00% | 0 | 0.215/0.417 | 0.111/0.110 |
| [VJM_898-p0008](../../bench/runs/O6_prep_20261007/pages/VJM_898-p0008-overlay.png) | unknown | 13/13 | 52 | — | — | — | — | — | 0.210/0.415 | 0.160/0.160 |
| [VJM_898-p0020](../../bench/runs/O6_prep_20261007/pages/VJM_898-p0020-overlay.png) | unknown | 4/6 | 17 | — | — | — | — | — | 0.212/0.418 | 0.044/0.044 |
| [VJM_898-p0032](../../bench/runs/O6_prep_20261007/pages/VJM_898-p0032-overlay.png) | unknown | 0/1 | 0 | — | — | — | — | — | 0.210/0.414 | 0.000/0.000 |
| [VJM_898-p0044](../../bench/runs/O6_prep_20261007/pages/VJM_898-p0044-overlay.png) | unknown | 2/3 | 67 | — | — | — | — | — | 0.212/0.420 | 0.015/0.014 |
| [VJM_898-p0056](../../bench/runs/O6_prep_20261007/pages/VJM_898-p0056-overlay.png) | unknown | 3/4 | 5 | — | — | — | — | — | 0.216/0.424 | 0.012/0.012 |
| [VJM_898-p0068](../../bench/runs/O6_prep_20261007/pages/VJM_898-p0068-overlay.png) | unknown | 3/4 | 83 | — | — | — | — | — | 0.217/0.423 | 0.020/0.020 |
| [VJM_898-p0080](../../bench/runs/O6_prep_20261007/pages/VJM_898-p0080-overlay.png) | unknown | 0/1 | 0 | — | — | — | — | — | 0.221/0.431 | 0.000/0.000 |
| [VZE_306-p0008](../../bench/runs/O6_prep_20261007/pages/VZE_306-p0008-overlay.png) | unknown | 18/22 | 43 | — | — | — | — | — | 0.215/0.419 | 0.074/0.074 |
| [VZE_306-p0021](../../bench/runs/O6_prep_20261007/pages/VZE_306-p0021-overlay.png) | unknown | 5/7 | 6 | — | — | — | — | — | 0.213/0.417 | 0.015/0.015 |
| [VZE_306-p0034](../../bench/runs/O6_prep_20261007/pages/VZE_306-p0034-overlay.png) | unknown | 13/16 | 13 | — | — | — | — | — | 0.215/0.419 | 0.024/0.024 |
| [VZE_306-p0047](../../bench/runs/O6_prep_20261007/pages/VZE_306-p0047-overlay.png) | unknown | 5/8 | 6 | — | — | — | — | — | 0.209/0.414 | 0.012/0.012 |
| [VZE_306-p0060](../../bench/runs/O6_prep_20261007/pages/VZE_306-p0060-overlay.png) | unknown | 16/19 | 19 | — | — | — | — | — | 0.212/0.417 | 0.042/0.042 |
| [VZE_306-p0073](../../bench/runs/O6_prep_20261007/pages/VZE_306-p0073-overlay.png) | unknown | 3/5 | 3 | — | — | — | — | — | 0.212/0.418 | 0.004/0.004 |
| [VZE_306-p0086](../../bench/runs/O6_prep_20261007/pages/VZE_306-p0086-overlay.png) | unknown | 16/18 | 29 | — | — | — | — | — | 0.214/0.418 | 0.042/0.042 |
| [XEK_118-p0008](../../bench/runs/O6_prep_20261007/pages/XEK_118-p0008-overlay.png) | unknown | 19/22 | 48 | — | — | — | — | — | 0.221/0.430 | 0.081/0.081 |
| [XEK_118-p0025](../../bench/runs/O6_prep_20261007/pages/XEK_118-p0025-overlay.png) | unknown | 6/7 | 6 | — | — | — | — | — | 0.211/0.423 | 0.012/0.012 |
| [XEK_118-p0042](../../bench/runs/O6_prep_20261007/pages/XEK_118-p0042-overlay.png) | unknown | 9/11 | 17 | — | — | — | — | — | 0.211/0.418 | 0.030/0.030 |
| [XEK_118-p0059](../../bench/runs/O6_prep_20261007/pages/XEK_118-p0059-overlay.png) | unknown | 5/6 | 6 | — | — | — | — | — | 0.209/0.413 | 0.014/0.014 |
| [XEK_118-p0076](../../bench/runs/O6_prep_20261007/pages/XEK_118-p0076-overlay.png) | unknown | 7/9 | 7 | — | — | — | — | — | 0.211/0.417 | 0.017/0.017 |
| [XEK_118-p0093](../../bench/runs/O6_prep_20261007/pages/XEK_118-p0093-overlay.png) | unknown | 23/24 | 35 | — | — | — | — | — | 0.219/0.426 | 0.062/0.062 |

## Latency and the Live Text standard

Across 40 warm pages: layout median **0.212 s wall / 0.418 s CPU**, segmentation median **0.039 s wall / 0.039 s CPU**. Mean combined layout + segmentation is **0.268 s wall/page**; total **8.497 s wall / 16.767 s CPU** layout plus **2.225 s wall / 2.224 s CPU** segmentation. Model construction takes 0.168 s and the first-page warmup takes 0.571 s, reported separately. Package imports, PDF render/GT extraction, hashing, output writing and overlay drawing are outside these stage timings. Individual page times above are one observation each; this is not a repeated latency qualification. Blank or table-dominated pages are fast partly because almost no text is segmented.

These are the original CPU measurements on macOS 26.5.1 arm64; the independent review identifies an Apple M5 MacBook Air (Mac17,4), 10 cores (4 performance + 6 efficiency), 32 GB RAM. O6-fix reused recorded layout/segmentation boxes and timings; it did not rerun inference or measure new latency. **No same-page Live Text timing was measured**, and no latency parity is claimed. O1d's public Apple Vision timings are line-crop measurements and its receipt does not certify UI Live Text equivalence; they are not a page baseline. Owner-standard qualification still needs identical rendered pages, inclusion of recognition and end-to-end timing against Live Text. This slice reports the preparation overhead and coverage needed for that comparison.

## Failure modes from personal review

- **Multi-column merges:** no visible cross-column line merge on COO_642 p143/p153 or bilingual VZE_306 p8 / XEK_118 p8; blocks keep the columns separate. Table rows are excluded, so this is not evidence of table-cell purity. Dense scan footnotes can have overlapping padded bands (VZE_306 p86, XEK_118 p42/p93).
- **Headers/footers dropped:** CGK_278 p60's folio is missed. FUT_255 p20 has no footer box; its last caption reference is missed. Most other headers/folios survive, but some are clipped (e.g. VJC_464 p52, FUT_255 p50). A surviving folio does not imply the body was covered.
- **Tables and forms:** AWU_928 p193 and CGK_278 p141 have boxed tables but no line crops within them; HTH_449 p163's questionnaire is a form region. This is the largest measured omission mechanism. Most nonblank scan pages are table-heavy and likewise have virtually no body lines. XEK_118 p76 also has major table areas with no layout box, distinct from intentionally unsegmented detected tables.
- **Footnotes:** VJC_464 p20 retains footnote bodies but misses some superscript markers; p52 drops most footnotes. GMA_704 p20 loses a final footnote line. Scan footnotes are often detected, but tight/overlapping bands need close review.
- **Formulas, diacritics and glyph-edge clipping:** AWU_928 p100 splits fraction structures into horizontal bands, clips numerator/denominator pieces, and entirely loses equation (5.2.62). Its 7 split glyphs are the only measured splits. Other pages show partial glyph coverage at block bottoms, paragraph endings and accents; zero complete omissions can coexist with clipping (COO_642 p153, FUT_255 p50).
- **Drop caps:** no typographic drop cap is present in the selected pages; this failure mode is untested. Ordinary enlarged section initials/headings are not substitutes.
- **Marginalia:** no handwritten marginalia is present. Printed vertical caption material on VJM_898 p44/p68 is fragmented; page-edge dirt and watermarks are mostly excluded. General marginalia coverage is untested.
- **Rotated text:** VJM_898 p44/p68 are sideways tables with vertical caption/heading strips. Projection yields 67/83 horizontal boxes, mostly character-like fragments, not usable text lines. Rotated column labels inside XEK_118 p25/p59 tables are excluded with the tables. The PDFs themselves are rendered in their stored orientation; there is no deskew or automatic rotation repair.
- **Figures/noise and GT limits:** chart and chemical-diagram regions remain excluded. CSP_291 p20's 12 empty-GT boxes are visibly raster text; none is established as pure noise. The two blank VJM pages have only watermark picture blocks and no lines, which is appropriate. Raster figure lettering can be missed while the native GT metric reads zero omissions.

## Page-by-page inspection log

I viewed every final contact-sheet page, with additional individual-page checks where needed. These are geometric visual observations, not scan transcriptions or certified line labels. [Machine-readable review](../../bench/runs/O6_prep_20261007/inspection.json) binds every overlay hash.

| Page | Observation |
|---|---|
| COO_642-p0143 | Columns stay separate; prose, caption, bottom note and folio covered. Diagram lettering is raster and outside GT. |
| COO_642-p0153 | Columns stay separate; a few accents/glyph edges clipped. No visible cross-column line merge. |
| AWU_928-p0100 | Fractions become separate horizontal bands; numerator/denominator glyphs clipped or split. Formula (5.2.62) entirely absent from layout. |
| AWU_928-p0193 | Three tables excluded from text segmentation; headings and folio survive. Figure screenshots also contain text outside extractable GT. |
| CGK_278-p0060 | Folio dropped; final prose line has glyph-edge clipping from tight block/line bounds. |
| CGK_278-p0141 | Full-page table excluded; only footer folio segmented. |
| HTH_449-p0080 | Body, running header, author footer and folio covered; small header picture excluded. |
| HTH_449-p0163 | Questionnaire in a form region excluded; only header, introductory text and footer segmented. |
| VJC_464-p0020 | Body/caption/three footnotes detected; superscript footnote markers omitted or clipped. |
| VJC_464-p0052 | Footnote region mostly dropped; small footnote fragments fall inside a text block. Last body line clipped; folio partly clipped. |
| GMA_704-p0020 | Quote attribution and some end-of-block lines/heading glyphs clipped or missed. A small last footnote line omitted. |
| GMA_704-p0050 | Table excluded; body, quote attribution, caption and footnotes mostly segmented. |
| BIK_230-p0020 | Flowchart excluded; body/section title/caption/footer detected but several glyph edges clipped. |
| BIK_230-p0050 | Illustration excluded; body/caption/footer detected; paragraph endings clipped. |
| ESD_511-p0020 | Running headers, prose and folio covered; no visible omission. |
| ESD_511-p0050 | Headers/prose/folio detected; some paragraph-end glyphs clipped or omitted. |
| FUT_255-p0020 | Chemical diagrams excluded; captions/body detected; final caption reference [20] omitted. Page has no separate folio. |
| FUT_255-p0050 | Sparse body and bullet item detected; bottom of final item and folio clipped. |
| CSP_291-p0020 | Charts excluded; raster legends/captions/footnotes still produce lines without GT. 12 empty-GT lines are visible text, not established noise. |
| CSP_291-p0050 | Bullet paragraphs remain separate; several paragraph endings and glyph bottoms clipped. |
| VJM_898-p0008 | Historical prose, headings and top folio detected. Slight skew and dirty left edge; no visible column merge. |
| VJM_898-p0020 | Table body excluded; heading, prose and top folio detected; watermark picture excluded. |
| VJM_898-p0032 | Blank scan leaf with watermark; zero text blocks/lines is appropriate. |
| VJM_898-p0044 | Sideways table excluded; vertical caption sliced into 66 horizontal character-like fragments plus folio. No orientation correction. |
| VJM_898-p0056 | Table body excluded; caption, units and folio detected. |
| VJM_898-p0068 | Sideways table excluded; vertical caption/marginal heading sliced into 82 horizontal fragments plus folio. |
| VJM_898-p0080 | Blank scan leaf with watermark; zero text blocks/lines is appropriate. |
| VZE_306-p0008 | Greek/English prose columns remain separate; abbreviation/symbol lists inside key_value_region blocks excluded; isolated list numbers sometimes clipped. |
| VZE_306-p0021 | Two table bodies excluded; bilingual titles, heading and folio detected. |
| VZE_306-p0034 | Three table bodies excluded; titles/units/footnotes/folio detected. Dense small cells never become lines. |
| VZE_306-p0047 | Full-page table excluded; headings and bottom note/folio detected; base-period labels classified outside text. |
| VZE_306-p0060 | Three table bodies excluded; bilingual titles/footnotes detected; some multiline footnotes share tight bands. |
| VZE_306-p0073 | Full-page table excluded; headings and folio detected; base-period label outside text. |
| VZE_306-p0086 | Table body excluded; bilingual bottom footnote columns and titles detected; tiny footnote lines have overlapping padding. |
| XEK_118-p0008 | Greek/English prose columns stay separate; abbreviation lists excluded as tables; one symbol-definition line visibly missed. |
| XEK_118-p0025 | Tall table excluded, including rotated column labels; title/header/bottom notes/folio detected. |
| XEK_118-p0042 | Table body excluded; bilingual headings and footnotes detected; tight, crowded footnote bands. |
| XEK_118-p0059 | Table body with rotated column labels excluded; titles, bottom notes and folio detected. |
| XEK_118-p0076 | Only one of several large table sections receives a table box; remaining table areas have no layout box. Titles and folio detected. |
| XEK_118-p0093 | Tall table excluded; headings, bilingual footnotes and folio detected; dense bottom bands overlap. |

Contact sheets: [sheet 01](../../bench/runs/O6_prep_20261007/contact-01.png), [sheet 02](../../bench/runs/O6_prep_20261007/contact-02.png), [sheet 03](../../bench/runs/O6_prep_20261007/contact-03.png), [sheet 04](../../bench/runs/O6_prep_20261007/contact-04.png), [sheet 05](../../bench/runs/O6_prep_20261007/contact-05.png), [sheet 06](../../bench/runs/O6_prep_20261007/contact-06.png), [sheet 07](../../bench/runs/O6_prep_20261007/contact-07.png), [sheet 08](../../bench/runs/O6_prep_20261007/contact-08.png), [sheet 09](../../bench/runs/O6_prep_20261007/contact-09.png), [sheet 10](../../bench/runs/O6_prep_20261007/contact-10.png).

## Validation and completion boundary

**237 benchmark tests passed, 1 skipped across two environment-specific commands**: `.venv-exp` ran 236 passed / 1 skipped / 1 deselected in 25.81 s, and `.venv-docling` ran the deselected Docling postprocessing test (1 passed in 2.89 s). The requested `.venv-exp` environment lacks Docling; the initial full run's sole failure was that missing optional dependency, retained in `tests-exp-initial.txt`. No installs were performed.

The nine new [UTF-16 regressions](../../bench/tests/test_utf16_glyphs.py) cover identical and distinct pair boxes, scalar GT/split counting, unpaired units, already-decoded non-BMP values, coincident unrelated glyphs, retained source indices and real-PDF native-label admission. Original O6 geometry/segmentation tests also pass. [Extractor test log](../../bench/runs/O6_prep_20261007/tests.txt), [Docling test log](../../bench/runs/O6_prep_20261007/tests-docling.txt). Commands:

```sh
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  ~/Projects/glossapi-development/.venv-exp/bin/python -m pytest bench/tests \
  -q -p no:cacheprovider -k 'not test_docling_postprocess_without_text_cells'
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  ~/Projects/glossapi-development/.venv-docling/bin/python -m pytest \
  bench/tests/test_page_slice.py::test_docling_postprocess_without_text_cells \
  -q -p no:cacheprovider
```

[Artifact validation](../../bench/runs/O6_prep_20261007/validation.txt) confirms 40 unique pages, 20/20 balance, ten sheets, independent recomputed metrics, source-PDF receipt matches, code/results/notes/inspection hashes, pair provenance and line-coordinate bounds.

O6-prep is complete. The full O6 recognition/latency comparison, compact variant qualification, Core ML pin and any detector/segmentation repair remain outside this task. The next page evaluation must keep the omission/clipping columns alongside recognition scores, and supply an explicit table/form/rotated-text path before claiming page completeness.
