# What our OCR must deliver to Docling for tables

Research date: 9 October 2026. Installed versions: **Docling 2.135.0, docling-ibm-models 4.0.3, docling-core 2.101.0**. Findings concern the actual installed source, pinned in [manifest.json](experiments/manifest.json) and [layout-manifest.json](experiments/layout-manifest.json).

> Research by Sol (gpt-6.1-sol, xhigh, model asserted from the rollout), 9 Oct 2026, in two passes: the brief and the owner's follow-up (layout vs table structure) are in `docling_tables_20261009/`, with the scripts and the summary JSON/CSV. Per-case experiment files and overlays (70 MB) stayed in the session scratchpad; links to `experiments/` below point there.

## 1. Answer for the owner

**A (finding the table): Heron decides “Table” from the page image alone; our OCR cells do not change the retained table regions, but their geometry can prevent text from entering those regions during layout postprocessing.**

**B (building the table): Deliver separate, accurately positioned text pieces belonging to one logical table cell each, because default TableFormer V1 assigns a fused string whole to one cell and does not separate its contents.**

There is no conflicting granularity requirement: A does not need long or fused OCR lines to recognise a table. Deliver tight within-cell line pieces or valid words for tables, with complete recall, and normal lines confined to their text columns elsewhere. Never fuse table content with adjacent prose. The measured tradeoff is in ordinary text grouping after detection: word inputs can create more text clusters, while the table regions stay identical. A correct table region with missing text still fails B.

A line or several words **inside one table cell** are acceptable. Word boxes are a useful, safer target when table boundaries are uncertain, but Docling does not require one OCR box per word. Nor must our detector reconstruct the complete table grid: TableFormer predicts that grid from the pixels. Our responsibility is to detect all the text, keep each emitted piece within its own row/column entry, and attach the right recognised string to its box.

With the default TableFormer V1 matching path, an OCR box is indivisible. A box crossing two predicted cells is normally assigned **whole to one** of them. Its words are not separated. On the real Vouli page 35, fusing two labels originally in columns 2 and 3 put the entire fused label into column 2 and reduced the output from 226 to 225 table cells. Both constituent locations were not recovered. The tiny controlled-grid experiment independently showed both halves of a crossing string assigned together to the right-hand cell, and both halves of a row-crossing string assigned together to the lower cell.

Therefore: split at table column boundaries, row boundaries, and separating rules **before emitting `TextCell`s**. A genuine merged header cell may contain multiple words or lines across its valid span. The restriction concerns boundaries between distinct logical entries, including unruled boundaries; it does not mean every printed line or every decorative rule defines a new table cell.

**Two important corrections to the supplied 2.81 analysis:** in this installation, image-based layout prediction runs **before OCR**, then layout cell assignment runs **after OCR**. Also, the table stage can prefer backend word cells over our OCR lines. Disabling cell matching is not a remedy for fused OCR: it asks the backend for text and can give empty tables on image-only input.

## Source-reference roots

All references are local installed files, not documentation claims. Expand these prefixes against:

```text
SP = /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/lib/python3.11/site-packages
D  = SP/docling
C  = SP/docling_core
T  = SP/docling_ibm_models/tableformer
P  = /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/deploy/docling_plugin
```

## A. Layout: what makes the region a table

### Image classification and OCR-dependent postprocessing are separate

**The Heron neural prediction is image-only.** The default options select `layout_heron_default` (`D/datamodel/pipeline_options.py:1691–1720`). The stage calls `page.get_image(scale=1.0)` and constructs an input containing the image and page-number metadata, with no OCR boxes, strings or scores (`D/models/stages/layout/layout_object_detection_model.py:95–115`; input fields: `D/models/inference_engines/object_detection/base.py:128–137`). The Transformers engine converts those images to RGB, runs the processor and neural model, then thresholds detections (`D/models/inference_engines/object_detection/transformers_engine.py:220–238`). Raw clusters have the model's label, box and confidence and an empty cell list (layout stage :144–186). In this installed standard pipeline, this occurs **before OCR**, which precedes layout postprocessing (`D/pipeline/standard_pdf_pipeline.py:787–794`).

**OCR influences the regular text clusters and the table's text membership, not the table classification or retained box in this default path.** The actual postprocessor has these mechanisms:

| Mechanism | Effect and installed-source evidence |
|---|---|
| Detection confidence thresholds | The engine initially keeps scores above its default 0.3 (`D/models/inference_engines/object_detection/base.py:56–59`). Postprocessing requires TABLE confidence ≥0.5 and DOCUMENT_INDEX ≥0.45 (`D/utils/layout_postprocessor.py:129–147,278–283`). These are image-model confidences, not OCR confidence. A weak raw table can disappear here independently of OCR. |
| Whole-cell assignment to regular clusters | Assign each nonblank positive-area OCR box to its best **regular** cluster if intersection / OCR-box area >0.2 (:220–236,648–689). This is not direct assignment to the table wrapper. No text splitting occurs. |
| Empty clusters and orphans | With defaults, empty **regular** clusters disappear except FORMULA; unassigned OCR cells become TEXT clusters with their own boxes and confidence (:238–265). Empty TABLE wrappers are retained. Orphan confidence is not subjected to a second ≥0.5 filter here. |
| Text geometry and merging | Regular clusters are resized to their cells' envelope and overlap groups choose a surviving cluster/label while merging whole cell lists (:267–275,482–606,700–724). OCR can shrink, enlarge or merge ordinary TEXT/LIST/etc. clusters and create new orphan TEXT clusters. There is no operation that divides an OCR string. |
| Table deduplication and cross-type conflicts | TABLE/DOCUMENT_INDEX wrappers are deduplicated using raw boxes and model confidences (:306–318,551–606). Coincident TABLE/DOCUMENT_INDEX favors DOCUMENT_INDEX; coincident PICTURE/TABLE generally favors TABLE within the specified confidence tolerance (:420–480). Both TABLE and DOCUMENT_INDEX enter the table stage. OCR does not change these comparisons. There is no TABLE→TEXT/LIST/PICTURE remapping. |
| Text membership of a table | A regular child joins the wrapper only when intersection / **child-cluster** area >0.8 (:333–340). The table then takes the union of its children's whole OCR-cell lists, deduplicated by ID (:398–418). A fused child crossing the outer table border can fail this test, excluding its text while leaving the TABLE box intact. |
| Retained table geometry | `_set_cluster_children` resizes FORM/KEY_VALUE_REGION containers, **not TABLE** (:404–410). A TABLE branch in `_adjust_cluster_bboxes` (:713–720) might suggest otherwise, but this helper is called on regular clusters only (:154–172,267–275); tables take the separate special-cluster path. Empty or partly populated tables therefore retain their image-predicted extent. |

The default flags are `keep_empty_clusters=False`, `skip_cell_assignment=False`, `create_orphan_clusters=True`, `run_postprocessor=True`; the pipeline copies the first three from its layout options (`D/datamodel/pipeline_options.py:1750–1795`; `D/pipeline/standard_pdf_pipeline.py:630–638`). `keep_empty_clusters`' broad field description should not be read as deleting empty tables: its active deletion is in the regular-cluster path. `create_orphan_clusters=False` can lose unassigned table text; `skip_cell_assignment=True` leaves wrappers without assigned OCR text. Neither supplies text repair or improves image classification. Backend-word precedence in B can bypass wrapper text membership, so source ownership remains essential.

For the owner's cases: **missing columns, crossed borders, fused table/prose boxes, and omitted discounted detections did not lose, shrink, split or relabel the retained tables in these tests.** They can remove text children or leave a separate TEXT cluster beside the surviving table. Faint *pixels* can affect Heron's image inference; discounting an OCR detection or lowering its OCR confidence alone cannot change the neural classification. We changed cells while holding pixels fixed, not the scan's ink intensity.

### Measured layout clusters on all three full pages

[research_layout.py](research_layout.py) ran the actual `LayoutObjectDetectionModel.predict_layout` and complete `LayoutPostprocessingModel.postprocess_layout` with default flags, CPU/four threads, and cached Heron snapshot `8f39ad3c0b4c58e9c2d2c84a38465abf757272d8`. **All 27 cases executed fresh neural forwards**; none reused neural results. Input was the full PNG rendered at page scale 1.0 with logical page dimensions PNG/3, consistent with the B tests. Inference took **0.320–0.780 seconds per case**; no crop fallback was needed. No PDF text or `boxes.json` was read.

Here are **all raw TABLE clusters**, with TOPLEFT boxes `(l,t,r,b)` in logical page units. Coordinates below are rounded to six decimals; JSON retains full precision. Every variant produced these exact same unrounded boxes/confidences. The “retained” column applies to every variant, including no cells.

| Page | Cluster | Raw box | Model confidence | Retained after postprocessing |
|---|---:|---|---:|---|
| Navigation | 1, right | `(696.994080,52.794832,1063.394409,698.221913)` | 0.817123652 | Yes |
| Navigation | 2, left | `(238.079651,52.703883,604.192322,702.780580)` | 0.771641433 | Yes |
| Vouli 35 | 0 | `(189.381643,249.142017,962.618930,1264.875651)` | 0.982347369 | Yes |
| Vouli 20 | 0, main table | `(18.628137,311.871562,1098.540823,1260.638135)` | 0.984227359 | Yes |
| Vouli 20 | 40, small upper region | `(244.806396,146.836269,886.077987,228.171837)` | 0.320873976 | No: below TABLE 0.5 threshold |

The following table links each setting to that box/confidence inventory. “Table OCR” counts text cells attached to retained table wrappers, summed across tables. “Outside tables” includes real prose and noise as well as border failures; it is **not** an annotated table-text loss rate.

| Page | OCR setting | Page OCR cells | Raw→retained tables | Boxes/confidences vs (a) | Table OCR | Outside tables |
|---|---|---:|---:|---|---:|---:|
| Navigation | (a) current lines | 429 | 2→2 | Identical | 425 | 4 |
| Navigation | (b) wide-gap pieces | 429 | 2→2 | Identical | 425 | 4 |
| Navigation | (c) word approximation | 958 | 2→2 | Identical | 954 | 4 |
| Navigation | missing left part | 269 | 2→2 | Identical | 265 | 4 |
| Vouli 35 | (a) current lines | 317 | 1→1 | Identical | 248 | 69 |
| Vouli 35 | (b) wide-gap pieces | 325 | 1→1 | Identical | 248 | 77 |
| Vouli 35 | (c) word approximation | 426 | 1→1 | Identical | 314 | 112 |
| Vouli 35 | missing left part | 243 | 1→1 | Identical | 177 | 66 |
| Vouli 20 | (a) current lines | 388 | 2→1 | Identical | 330 | 58 |
| Vouli 20 | (b) wide-gap pieces | 390 | 2→1 | Identical | 330 | 60 |
| Vouli 20 | (c) word approximation | 460 | 2→1 | Identical | 364 | 96 |
| Vouli 20 | missing left part | 338 | 2→1 | Identical | 280 | 58 |

The (a)/(b)/(c) cell-generation method is exactly the B method below. “Missing left part” removes **every line intersecting the left 35% of B's manually fixed table rectangle**, including any long line crossing that strip; the removed counts are **160 / 74 / 50**. This guarantees an empty strip without treating detector text as truth. It stresses missing coverage beyond the omissions already present in the supplied detector; the strip is not a manual annotation of exactly two columns. The navigation strip is on its right-hand table. Its left-hand table already has only **17** line tokens versus **408** on the right, yet both tables are found at unchanged extents. On Vouli 20, missing columns likewise do not prevent a full-width table region.

Additional controls, each run on all three full pages, retained exactly the same table identities:

| Setting | Navigation: input / table OCR | Vouli 35: input / table OCR | Vouli 20: input / table OCR | Observed effect |
|---|---:|---:|---:|---|
| No OCR cells anywhere | 0 / 0 | 0 / 0 | 0 / 0 | Tables retained, including their empty text lists. |
| Every line's OCR confidence = 0 | 429 / 425 | 317 / 248 | 388 / 330 | Same table membership and table confidence. |
| Omit all `discounted != null` entries | 414 / 411 | 268 / 238 | 356 / 323 | Removed 15 / 49 / 32 detections; table boxes unchanged. |
| One synthetic border-crossing box only | 1 / 0 | 1 / 0 | 1 / 0 | Whole token survives as separate TEXT, outside table children. |
| One synthetic table-plus-outside fused box only | 1 / 0 | 1 / 0 | 1 / 0 | Same exclusion; no split or substring salvage. |

The synthetic border box is 50% inside the chosen table and 50% above its top border; the fused box combines a larger upper-table piece with an outside extension (2/3 inside). Both stay within page bounds and fail the >0.8 child-containment gate. They replace other cells for a clear controlled test and are not assertions about a particular recognised string. For the navigation spread, these controls use the larger left-hand table; the missing-strip control uses the right-hand table as stated above.

The **page-level mean `layout_score` is OCR-dependent**, although the table score is not: line→zero-confidence controls changed it from **0.8535→0.4035, 0.8935→0.0964, 0.8245→0.2331**. The stage averages all retained cluster confidences, including orphan TEXT scores (`D/models/stages/layout/layout_postprocessing_model.py:86–94`). Do not confuse this diagnostic with a Table confidence threshold. Line→word inputs also changed total retained clusters from **6→6, 35→61, 35→61**, without changing any table box or label.

The real full layout path admitted **248 / 330** line labels on the Vouli pages, compared with **258 / 341** under B's broader fixed-region assignment. Those are **10 / 11 additional exclusions before TableFormer**, not TableFormer dropping text. They combine image-box differences and full wrapper containment; no manual adjudication establishes that every excluded label was valid table content. This is why table discovery, layout text admission, and table ownership need separate tests.

Exact raw predictions, retained clusters/children, token lists, boxes, confidences and equality assertions: [layout-summary.json](experiments/layout-summary.json), [layout-summary.csv](experiments/layout-summary.csv), [layout-experiments.log](layout-experiments.log), and per-case `experiments/*.layout.<variant>.json`. Full-page box overlays: [Navigation](experiments/an-7a2b17a3fb0f-p000200.layout.tables.jpg), [Vouli 35](experiments/s2-200e977f2dab5291c42c-p00035.layout.tables.jpg), [Vouli 20](experiments/s2-831443dc5e6f1ccfbaf5-p00020.layout.tables.jpg). Equality was checked on the **entire raw prediction**, and separately on retained table IDs, labels, unrounded boxes and confidences, not just counts.

To reproduce A (foreground execution, with outputs in this directory):

```sh
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 "$PY" research_layout.py
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 "$PY" summarize_layout.py
```

## B. Table structure: what TableFormer needs from our cells

### The actual path from OCR to `TableItem`

1. **Preprocessing and raw layout prediction.** Preprocessing assigns the backend's segmented page to `page.parsed_page` (`D/models/stages/page_preprocessing/page_preprocessing_model.py:100–105`). `Page.cells` is a read-only view of `parsed_page.textline_cells` (`D/datamodel/base_models.py:528–533`). The standard pipeline wiring is preprocessing → layout prediction → OCR → layout postprocessing → table → assembly (`D/pipeline/standard_pdf_pipeline.py:787–794`). The default object-detection layout model consumes a page image and emits raw clusters with empty cell lists (`D/models/stages/layout/layout_object_detection_model.py:95–109,124–140,173–186`). It does not split our text.
2. **OCR installs cells and yields pages.** Bundled engines call `BaseOcrModel.post_process_cells`; it merges/replaces cells, reindexes them, and writes `parsed_page.textline_cells` (`D/models/base_ocr_model.py:411–476`). The callable yields updated `Page`s; it does not return a standalone cell list. OCR regions now come from raw layout detections, optionally filtered against native content, or the full page (`D/models/base_ocr_model.py:214–259,261–348`). The old bitmap-area thresholds and pipeline order in the 2.81 note do not describe this code.
3. **Layout postprocessing associates whole cells with clusters.** It runs after OCR (`D/models/stages/layout/layout_postprocessing_model.py:57–67`). The basic assignment chooses the best cluster with intersection / OCR-cell area **strictly greater than 0.2**, ignores blank/zero-area cells, and deduplicates by `index` (`D/utils/layout_postprocessor.py:648–689`). Table wrappers collect the cells of contained regular children, with child containment >0.8 (`D/utils/layout_postprocessor.py:333–340,398–418`). This association does not divide OCR strings. Actual layout detection and wrapper formation are a separate potential source of exclusion.
4. **Table stage chooses its text source.** For each TABLE or DOCUMENT_INDEX cluster, V1 first calls `page._backend.get_segmented_page().get_cells_in_bbox(WORD, table_bbox)`. If **any** words are returned, those are the tokens; only an empty word result falls back to `table_cluster.cells` (`D/models/stages/table_structure/table_structure_model.py:206–247`). Word selection requires intersection / word area >0.8 and converts word origins to the table's origin (`C/types/doc/page.py:771–796`). A single retained backend word can therefore displace all our table OCR lines; this is not a per-cell fallback.
5. **Tokens and image enter TableFormer.** The wrapper filters whitespace-only strings and passes only `{id: index, text, bbox}` for each token, scaling boxes and image by 2 (`D/models/stages/table_structure/table_structure_model.py:224–267`). The predictor first resizes the page image to height 1024, then crops the table (`T/data_management/tf_predictor.py:524–558`). The neural model receives the image tensor and predicts structure tags, classes and boxes; OCR strings are not neural inputs (`T/data_management/tf_predictor.py:747–792`).
6. **This is where OCR boxes are matched to predicted table cells.** `CellMatcher.match_cells` builds structural cells and computes geometric intersections (`T/data_management/tf_cell_matcher.py:129–173,465–527`). Despite a misleading docstring saying “only 1,” initial matches include **every positive intersection**, scored as intersection / OCR-box area. The configured `pdf_cell_iou_thres=0.05` is not used by this active intersection routine. Postprocessing adjusts boxes/columns, rematches, then retains the highest-scoring match per OCR token (`T/data_management/matching_post_processor.py:678–713,1375–1464`). `enable_post_process` is True in the predictor (`T/data_management/tf_predictor.py:112,825–850`).
7. **Whole text is assembled into table cells.** Responses are sorted by input cell ID; entries at the same row/column start are merged, carrying the entire token strings (`T/data_management/tf_predictor.py:836–850,379–435`). `TableCell` joins these strings with spaces (`C/types/doc/items/table/table_data.py:36–57`). The wrapper creates an intermediate `Table`, records rows/columns/spans and rescales boxes to page units (`D/models/stages/table_structure/table_structure_model.py:278–305`). Assembly takes that `Table` (`D/models/stages/page_assemble/page_assemble_model.py:221–239`). Reading order transfers its cells into `TableData` and calls `out_doc.add_table`, producing the final `TableItem` (`D/models/stages/reading_order/readingorder_model.py:134–154,257–273`). Reading order does not repair a fused cell's text ownership.

### Granularity and boundaries

| Delivery requirement | Why / evidence |
|---|---|
| Prefer tight word boxes or tight line pieces confined to one logical table cell. | V1 explicitly prefers available word cells, but supports line/phrase fallback: table wrapper :236–247. The controlled grid produced identical `WORD_ONE WORD_TWO` text from one within-cell line and two within-cell word boxes. |
| Do not cross distinct columns, rows, separating rules, or two separate tables. | V1 final assignment is one token → one table cell. Real fusion control and synthetic crossing probes below. There is no substring-to-position alignment. |
| Multiple OCR pieces may belong to one table cell. | Final merging joins multiple tokens at one row/column slot. Within-cell multiline text is supported as ordered pieces; an enormous whole-cell box is less precise than tight text boxes. |
| Detect missing columns and every text element from pixels. | No later V1 step recognises missing glyphs from the image. Placeholder survival measures only supplied detections, not omitted text. The supplied line overlays visibly omit much of the navigation spread's left table and page 20's municipality-name column. |
| Do not emit duplicated detections or rules/leader dots as content. | Layout deduplication uses cell `index`, not recognised-string identity (`D/utils/layout_postprocessor.py:638–646`). Different IDs with repeated content are not a dependable deduplication mechanism. |

Docling's bundled OCR is not uniformly word-level. **EasyOCR:** one `TextCell` per `reader.readtext` result, with no further word splitting in the wrapper (`D/models/stages/ocr/easyocr_model.py:339–365`); its result granularity depends on EasyOCR detection/grouping. **Tesseract Python/tesserocr:** uses `RIL.TEXTLINE`, then recognises each rectangle (`D/models/stages/ocr/tesseract_ocr_model.py:246–287`). **Tesseract CLI:** reads TSV, retains nonempty text entries, then creates one cell per retained row—normally TSV word entries (`D/models/stages/ocr/tesseract_ocr_cli_model.py:227–258,394–424`). These implementations demonstrate that lines are permitted, not that cross-cell lines are repaired.

### Coordinates and fields

Return coordinates in the **page's logical coordinate system**, normally PDF points (72 units/inch), with **TOPLEFT** origin, x increasing rightward, y downward, and positive boxes `l < r`, `t < b`. Do not submit coordinates in the recogniser's resized/straightened-strip frame.

For an OCR region rendered at scale `s`, convert pixel coordinates by `x_page = region.l + x_pixel/s`, `y_page = region.t + y_pixel/s`. If there was extra resizing, rotation or dewarping, undo that transform too. For arbitrary raster input, obtain the actual image/page-size ratio; do not assume our experiment's scale of 3. EasyOCR's installed conversion demonstrates division by render scale plus crop offset with explicit TOPLEFT (`D/models/stages/ocr/easyocr_model.py:351–360`). OCR's default scale is 3 = 216 dpi (`D/datamodel/pipeline_options.py:246–258`); V1 table scale is independently 2 = 144 dpi (table wrapper :96).

| `TextCell` field | What V1 table matching actually uses |
|---|---|
| `index` | Token ID, must be unique on the page; determines token assembly order. Base OCR reindexes. The image-to-table helper explicitly rejects duplicates (table wrapper :338–351). Use stable top-to-bottom / left-to-right ordering within each logical cell. |
| `text` | Complete indivisible string; whitespace-only strings are omitted. |
| `rect` | `rect.to_bounding_box()`; only its axis-aligned envelope survives into matching. |
| `orig` | Required by `TextCell`; normally set to raw recogniser output. Not passed to TableFormer. |
| `confidence` | Not passed to V1 matching, so it cannot prevent a crossing assignment. Use a real 0–1 recogniser score for upstream filtering/reporting. Base OCR aggregates it into the page OCR score (:472–476). |
| `from_ocr` | Set True. Not passed to V1 matching; does matter to native-word/character cleanup and OCR confidence accounting (base OCR :461–476). |
| `text_direction` | Defaults to LEFT_TO_RIGHT, appropriate for Greek; not passed to V1 matching. It does not sort or split a table string. |

Field definitions: `C/types/doc/page.py:281–323`. Rectangles can have four oriented corners, but `to_bounding_box()` takes min/max coordinates (`C/types/doc/page.py:104–119,168–200`). **Skew is accepted as an envelope, not handled as an oriented intersection. Curved baseline/top/bottom arrays are not an input to the matcher.** Keep the curves for strip recognition, but emit tight page-space boxes per within-cell piece. A long curved line's envelope can overlap another row even if its actual ink does not. The V1 wrapper does not normalise origins for the cluster-cell fallback; explicitly convert those OCR cells to TOPLEFT yourself.

Measured control: changing every page-35 cell's confidence to 0, `from_ocr` to False, `orig` to a sentinel, direction to RIGHT_TO_LEFT, and rectangle to a skewed quadrilateral with the **same envelope** produced an exactly equal final `TableItem`. This establishes the table-stage effect, not upstream OCR/layout behavior. Evidence: [actual-probes-summary.json](experiments/actual-probes-summary.json), [probe_actual_stage.py](probe_actual_stage.py).

### Settings, pixel reading, and PDF text-layer paths

| Setting / path | Actual behavior |
|---|---|
| `do_table_structure=True` | Enables the table model in the standard pipeline (`D/pipeline/standard_pdf_pipeline.py:641–650`). Tables must also have layout TABLE / DOCUMENT_INDEX clusters. |
| `TableStructureOptions(do_cell_matching=True)` | Default V1 behavior: geometric matching and postprocessing of supplied tokens. No text re-OCR. |
| `do_cell_matching=False` | Predicts structure without matching, then calls `page._backend.get_text_in_rect(predicted_bbox)` for every output cell (table wrapper :265–278). Injected OCR tokens are not used by that path. |
| `TableFormerMode.ACCURATE` / `.FAST` | Select different `accurate` / `fast` checkpoint/config directories (table wrapper :72–95); they do not change the atomic OCR-token contract. Defaults are matching=True, mode=ACCURATE (`D/datamodel/pipeline_options.py:151–172`). “Accurate” is not a guarantee: page 20 was structurally much worse with that checkpoint here. |
| `OcrMode.FULL_PAGE` | Base OCR uses only OCR lines and removes non-OCR native word/character cells; default modes may merge native and OCR cells (base OCR :432–469). Deprecated `force_full_page_ocr=True` maps to FULL_PAGE (`D/datamodel/pipeline_options.py:282–309`). |

**V1 TableFormer reads pixels for structure, not for recognition.** In matching=True, table text comes exclusively from the selected tokens, but the token source is not necessarily our plugin: backend word-cell precedence can select another OCR's PDF text layer. In matching=False, backend text extraction is explicit:

- Docling-parse caches its segmented page; preprocessing normally aliases that object. Its `get_text_in_rect` scans that object's current line cells and includes a whole string when overlap / line area >0.5 (`D/backend/docling_parse_backend.py:142–171`). After a replacement on that shared object, it can read our OCR lines; otherwise it reads native lines. It still does not split a string. Overlapping predicted boxes can duplicate it: the direct backend probe returned `FUSED_BACKEND` for both overlapping rectangles.
- PDFium's `get_text_in_rect` calls the PDF text layer via `get_text_bounded` (`D/backend/pypdfium2_backend.py:585–605`), regardless of our injected page cells. A scanned PDF with an earlier OCR layer can therefore use that earlier OCR here.
- The image backend returns `""` for `get_text_in_rect` (`D/backend/image_backend.py:102–104`). A scan without any text layer cannot get recognition from disabling matching.

Guarantee the selected source by replacing/clearing stale backend words and characters on OCR-owned pages, keeping the appropriate backend/parsed-page alias consistent, and testing the resulting table tokens. Merely setting `from_ocr=True` on new lines is insufficient. If intentionally maintaining a word-cell cache, it must contain this pass's valid OCR words, not remnants of another engine. Base FULL_PAGE keeps existing `from_ocr` word/character cells; clear stale OCR caches too.

**Scope distinction in 2.135:** the default `TableStructureOptions` selects V1. Separately, `TableStructureV2Options` uses an independent >0.3 overlap test per predicted cell and can duplicate a fused string into two cells; its backend fallback also reads `get_text_in_rect` (`D/models/stages/table_structure/table_structure_model_v2.py:196–228,489–515`). Calling its installed matching helper with a 140-wide fused box returned `V2_FUSED` twice. No V2 checkpoint was run. The optional Granite Vision table model generates table output from images (`D/models/stages/table_structure/table_structure_model_granite_vision.py:167–217`); the V1 no-re-OCR conclusion should not be generalized to all alternative backends.

### Current plugin and old contract

The supplied plugin presently recognises **native text-layer line rectangles**, keeps their geometry, and installs replacement strings (`P/model.py:113–120,145–167,173–174`). `mode="detector"` explicitly reports `detector_out_of_scope` (:108–112), empty native lines report `no_textlayer_lines` (:114–117), and the raster-body guard can preserve native cells (:125–132,168–174). This research tests the desired future detector delivery through direct cell injection; it does not demonstrate detector integration in that plugin.

Its current `_install` removes non-OCR native word/character cells (:82–92), which is relevant to the V1 source preference. Retained OCR word caches still need an ownership test. The plugin's own `mode` names (`textlayer`, `detector`) also override the new inherited Docling OCR `mode`; rename that plugin-specific selector when adding detector support so `OcrMode` remains usable.

The existing [contract tests](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/tests/test_docling_contract.py) were run by absolute path, without editing them: **13 passed**, with deprecation warnings, in 1.78 s. Log: [contract-tests.log](contract-tests.log). Those tests verify routing/replacement and refusal boundaries with mocked recognition, not table ownership or the pixel detector. The old [DOCLING_PLUGIN_CONTRACT.md](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/DOCLING_PLUGIN_CONTRACT.md) remains useful for the yielded-page correction and crop-coordinate principle, but its stage order, OCR region-selection rules, and source paths must be updated for 2.135.

### B experiments and numbers

### Method and limits of the measurements

All execution was offline (`HF_HUB_OFFLINE=1`, additionally `TRANSFORMERS_OFFLINE=1`) with the supplied Python. No background job was launched. Models were loaded by explicit local path from cached snapshot `fc0f2d45e2218ea24bce5045f58a389aed16dc23`; nothing was downloaded. All created scripts/logs/results are in this directory. **No `pages/*.boxes.json` was read or used as truth.**

The three full PNGs were supplied to the actual V1 `TableStructureModel.predict_tables`, with one manually fixed table region per page. The navigation test covers the right-hand table and its lower continuation, not both spread halves. Original-pixel regions `(l,t,r,b)`:

| Short name | Page | Region |
|---|---|---|
| Navigation | `an-7a2b17a3fb0f-p000200` | `(2090,150,3190,2090)` |
| Vouli 35 | `s2-200e977f2dab5291c42c-p00035` | `(565,745,2900,3840)` |
| Vouli 20 | `s2-831443dc5e6f1ccfbaf5-p00020` | `(55,920,3290,3800)` |

The stub backend has no native text or words except in the explicit sentinel controls. The installed layout assignment helper selects cells for the fixed region; full layout inference/wrapper processing is bypassed to isolate table matching. Final serialization uses the installed reading-order `TableItem` construction helper.

- **(a) line:** every supplied `lines.json` entry becomes a cell using `x0,x1,min(top),max(bottom)`, clipped to page bounds. Discounted entries are retained and recorded. These are line cells, not the often much larger `segments.json` connected-component rectangles.
- **(b) wide:** same line curves split at blank runs ≥1.5×x-height, using pixel ink projection. Piece x bounds are trimmed to ink; y bounds remain the corresponding line-curve envelope.
- **(c) word approximation:** same operation with blank runs ≥max(4 pixels,0.3×x-height). Adaptive thresholding, long straight-rule removal, and font/diacritic curves determine gaps. This is an approximation, capable of splitting numeric strings; it is not a word annotation or recognised-text alignment.

Each cell contains only its unique label, e.g. `L0126P00`. The first neural pass for each page/mode is real; identical image-tensor hashes then reuse its exact output tensors. Every variant runs the installed matching, postprocessing and final `TableItem` construction afresh. This holds raw structure constant and isolates OCR geometry. Real forwards took Accurate **11.09 / 4.46 / 0.36 s**, Fast **1.08 / 1.10 / 1.30 s**, in page order above, CPU / four threads. No small-crop fallback was needed for runtime.

“Found” means materialized `TableItem.data.table_cells`, not all grid slots or an accuracy score. “Input” means labels admitted to the chosen table region. “Assigned” means the complete input label occurs in output; “split” means the matcher divided an input label; “duplicated” means one input label occurs more than once in materialized output cells; “lost” means absent there. Whitespace joining and normal merged-cell grid expansion are not duplication. The scripts check that output tokens are complete known labels and that assigned + lost = input. Labels excluded by the fixed layout-region selection are counted separately in JSON/CSV, not as table-stage loss.

### Main comparison: matching=True

| Mode | Page | OCR setting | Found | Rows×cols | Input | Assigned | Split | Duplicated | Lost |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Accurate | Navigation | (a) line | 115 | 25×8 | 408 | 408 | 0 | 0 | 0 |
| Accurate | Navigation | (b) wide | 115 | 25×8 | 408 | 408 | 0 | 0 | 0 |
| Accurate | Navigation | (c) word approximation | 119 | 27×8 | 833 | 833 | 0 | 0 | 0 |
| Accurate | Vouli 35 | (a) line | 226 | 40×9 | 258 | 258 | 0 | 0 | 0 |
| Accurate | Vouli 35 | (b) wide | 226 | 40×9 | 258 | 258 | 0 | 0 | 0 |
| Accurate | Vouli 35 | (c) word approximation | 240 | 41×9 | 328 | 328 | 0 | 0 | 0 |
| Accurate | Vouli 20 | (a) line | 16 | 3×7 | 341 | 341 | 0 | 0 | 0 |
| Accurate | Vouli 20 | (b) wide | 16 | 3×7 | 339 | 339 | 0 | 0 | 0 |
| Accurate | Vouli 20 | (c) word approximation | 16 | 3×7 | 366 | 366 | 0 | 0 | 0 |
| Fast | Navigation | (a) line | 107 | 25×7 | 408 | 408 | 0 | 0 | 0 |
| Fast | Navigation | (b) wide | 107 | 25×7 | 408 | 408 | 0 | 0 | 0 |
| Fast | Navigation | (c) word approximation | 115 | 26×7 | 833 | 833 | 0 | 0 | 0 |
| Fast | Vouli 35 | (a) line | 177 | 40×6 | 258 | 258 | 0 | 0 | 0 |
| Fast | Vouli 35 | (b) wide | 177 | 40×6 | 258 | 258 | 0 | 0 | 0 |
| Fast | Vouli 35 | (c) word approximation | 179 | 40×6 | 328 | 328 | 0 | 0 | 0 |
| Fast | Vouli 20 | (a) line | 131 | 34×7 | 341 | 341 | 0 | 0 | 0 |
| Fast | Vouli 20 | (b) wide | 131 | 34×7 | 339 | 339 | 0 | 0 | 0 |
| Fast | Vouli 20 | (c) word approximation | 133 | 34×7 | 366 | 366 | 0 | 0 | 0 |

The two-label real fusion control on Vouli 35 / Accurate produced **225 found, 257 input/assigned, 0 split/duplicated/lost**. This apparently perfect survival hid wrong ownership: `L0126P00` originally landed at (row 10,col 2), `L0164P00` at (10,3), while their fused token landed only at (10,2). Evidence: [actual-probes-summary.json](experiments/actual-probes-summary.json).

The wide-gap threshold produced **no multi-piece parents inside these table regions**. Its trimming altered admission of two edge labels on Vouli 20, explaining 341 → 339 input. It is not evidence that wide-gap splitting fixes table crossings. Word approximation split 199 / 51 / 22 admitted parent lines into multiple pieces; 44 / 23 / 0 parents then reached multiple output cells in Accurate, 40 / 6 / 3 in Fast. That redistribution was done because **our experiment split the inputs**, not because Docling split a fused string. Evidence: [combined-summary.json](experiments/combined-summary.json).

Initial geometric ambiguity was common: Accurate line inputs intersected multiple raw predicted cells for **286/408, 228/258, 24/341** labels. The corresponding initially unmatched counts were **26, 5, 8**. Final postprocessed matches had zero multi-target tokens and retained all labels. These are overlaps with predicted boxes, not manually adjudicated logical-boundary crossings.

**Retention is not table correctness.** The [Vouli-20 Accurate overlay](experiments/s2-831443dc5e6f1ccfbaf5-p00020.accurate.line.matching-1.jpg) shows columns covering many printed rows as huge cells. Finer OCR did not repair that structure. The [Vouli-35 overlay](experiments/s2-200e977f2dab5291c42c-p00035.accurate.line.matching-1.jpg) also shows row/column imperfections. Neither checkpoint/result is accepted as a correct table merely because every supplied label survived.

### Source-selection controls

| Accurate setting | Page | Found | Input OCR | Assigned | Split | Duplicated | Lost OCR |
|---|---|---:|---:|---:|---:|---:|---:|
| matching=False, image-style backend | Navigation | 895 | 408 | 0 | 0 | 0 | 408 |
| matching=False, image-style backend | Vouli 35 | 362 | 258 | 0 | 0 | 0 | 258 |
| matching=False, image-style backend | Vouli 20 | 18 | 341 | 0 | 0 | 0 | 341 |
| matching=True, one retained backend word | Navigation | 1 | 408 | 0 | 0 | 0 | 408 |
| matching=True, one retained backend word | Vouli 35 | 1 | 258 | 0 | 0 | 0 | 258 |
| matching=True, one retained backend word | Vouli 20 | 1 | 341 | 0 | 0 | 0 | 341 |

matching=False made **895 / 362 / 18 backend text queries**, yielding empty strings. The retained-word controls yielded one `BACKEND_WORD` table cell and never selected the injected OCR lines. This is a deliberate stale-source simulation, not a claim that current per-page `_install` leaves a non-OCR native word behind.

### Tiny deterministic crossing/outlier probes

The installed V1 matcher/postprocessor was given a known 2×2 grid with four anchor words. These probes isolate matching from model prediction; coordinates here are arbitrary common units. Evidence: [micro-probes.json](experiments/micro-probes.json), [probe_matching.py](probe_matching.py).

| Additional controlled input | Assigned | Split | Duplicated | Lost | Result |
|---|---:|---:|---:|---:|---|
| One line `WORD_ONE WORD_TWO` within one cell | 1 | 0 | 0 | 0 | Joined intact to that cell. |
| Two word boxes in that same cell | 2 | 0 | 0 | 0 | Same final phrase. |
| `LEFT_CONTENT RIGHT_CONTENT` across columns | 1 | 0 | 0 | 0 | Both strings in right cell (0,1). |
| `TOP_CONTENT BOTTOM_CONTENT` across rows | 1 | 0 | 0 | 0 | Both strings in lower cell (1,0). |
| Box partly outside predicted cells | 1 | 0 | 0 | 0 | Whole `PARTIAL` string retained in right cell. |
| No cell intersection, but row-band intersection | 1 | 0 | 0 | 0 | Recovered whole to nearest column. |
| No cell intersection, but column-band intersection | 1 | 0 | 0 | 0 | Recovered whole to nearest row. |
| Neither row- nor column-band intersection | 0 | 0 | 0 | 1 | Dropped, with a warning. |

The partial box had only 20% overlap with the initial right cell. Thus “not fully contained” is not automatic loss. Orphan recovery can reuse or create a structural cell and expand its box; it does not clip the text (`T/data_management/matching_post_processor.py:738–788,790–837,1137–1239`). It can preserve text in an incorrect location. A cell excluded earlier by layout/source selection never reaches this recovery path.

### Reproduce and inspect

```sh
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 "$PY" research_tables.py --controls
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 "$PY" research_tables.py --mode fast
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 "$PY" probe_matching.py
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 "$PY" probe_actual_stage.py
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 "$PY" summarize_experiments.py
```

Machine-readable summaries: [summary.csv](experiments/summary.csv), [combined-summary.json](experiments/combined-summary.json). Each per-case JSON records source boxes, admitted IDs, exact label-to-table destinations, raw TableFormer details, and final `TableItem`. Matching counts use those final objects, not PDF text or a rendered Markdown table.

## Changes and acceptance test satisfying both A and B

1. **Implement the actual detector-backed path.** Recognise pixel-derived curves/segments without requiring native PDF lines. Keep the line recogniser and curve-following strips, but generate final boxes/text only after separating independent table entries. Rename the plugin's recogniser-mode selector to avoid its collision with Docling's new `OcrOptions.mode`.
2. **Add boundary-aware segmentation.** Use ruled separators and unruled gutters; split a detected line at distinct columns and rows. Wide whitespace alone is insufficient on these pages. Do not cut a word's text into guessed fractions after recognition: recognise separated pieces or use validated character/word alignment to attach correct substrings to their boxes. Keep accents, digits and punctuation; suppress rules and navigation noise. For tables, prefer valid word boxes when available, otherwise within-cell line pieces with tight envelopes.
3. **Make OCR-source ownership explicit.** Replace/clear stale native and prior-OCR word/character caches on OCR-owned pages. Use matching=True for the V1 plugin path. Verify which cells the backend word query returns. Default to Accurate initially, but qualify Fast too; do not select a mode from its name alone.
4. **Measure discovery, admission, placement, structure, and recognition separately.** Add pixel-reviewed annotations for every table on the three pages, including both navigation-spread halves, header spans, empty cells, municipality-name columns, and currency subcolumns. Track raw Heron TABLE detections, retained wrappers, admitted OCR pieces, and final row/column ownership separately. The PDF layer is another OCR's output and must not supply these annotations.

Proposed acceptance gate for this small development set:

| Test | Required result |
|---|---|
| A: table discovery and OCR invariance | Every pixel-annotated table has a retained TABLE/DOCUMENT_INDEX region covering its full extent, including empty/missed columns. Compare raw and final boxes/confidences under lines, pieces, words, omitted-column and no-cell controls: unchanged for fixed pixels in this default Heron path. Do not substitute page mean `layout_score` for table confidence. Investigate an image detection or threshold failure independently of OCR segmentation. |
| A: admission to table wrappers | With stale backend words cleared, every valid annotated table piece reaches its table wrapper exactly once. Border/fused-prose negative controls may preserve the TABLE region while excluding text; the detector must resolve these crossings before emission. Record exclusions separately from TableFormer loss. If correct table ink lies outside Heron's predicted box, fix/qualify the layout region rather than distort the OCR box. |
| Pixel-to-`TextCell` geometry | Positive finite TOPLEFT page-space boxes; unique IDs; crop/resize/dewarp round-trip overlay fits the intended ink, including diacritics. No emitted text piece crosses an annotated boundary between distinct entries. |
| Detector recall | Every manually annotated text element in each table has a corresponding correct piece; no missing column. No rule/noise emitted as text. For this fixed small set, enumerate and resolve each omission rather than hiding it in an average. |
| Matcher isolation | Inject unique labels into annotated words/within-cell lines with fixed table regions. Each label appears exactly once, in its annotated row/column/span; zero lost, duplicated or wrong-owner labels. Keep crossing-box negative controls to demonstrate that a fused output is rejected even if text survives. |
| Source ownership | Add conflicting backend-word and native-line sentinels. After page replacement, none appears in the final table. Tables use the new OCR labels, including scans with a preexisting hidden OCR layer. |
| Full integration | Run actual layout inference → detector-backed OCR → layout postprocessing → V1 table → reading order on all three full pages. Confirm every table region, exact annotated rows/columns/spans, and label ownership. Failure of the frozen-cell test identifies structure/matching; failure only here identifies layout/routing/integration. |
| Real recognition | Replace labels with recogniser output and compare each cell against manually transcribed pixels. Record per-cell character errors, especially monetary digits/decimal separators; agree the recognition threshold before declaring production readiness. |

The existing 13 plugin tests remain useful compatibility checks. They must be supplemented by these table and source-ownership tests; a page-level replacement assertion or “all tokens present” assertion is insufficient.

## What was not verified

- No character-recognition accuracy or human-adjudicated ownership score was computed. Labels isolate geometry, and gap-based words are only approximations. The tables have visible model and detector failures; more output cells are not proven improvements.
- Full Heron inference and complete layout wrapper postprocessing were run on all three full PNGs, including both navigation tables. B's TableFormer runs still used fixed regions to isolate matching, with only the right navigation table exercised there. We did not chain the measured layout outputs into TableFormer, run real OCR routing, run the full standard pipeline, or run the reading-order predictor; its final `TableItem` construction helper was exercised.
- No detector mode exists in the supplied plugin to exercise. The current contract tests use mocked recognition and native line geometry. No plugin or external project file was edited.
- EasyOCR/tesserocr/CLI return construction was verified from installed Docling wrapper code, not by running those engines on these pages. EasyOCR is not installed in this Python environment.
- No TableFormer V2 or Granite Vision neural checkpoint was run. V2's different matching behavior was verified by its actual helper and source only.
- No systematic sweep of scan resolution, skew/curvature, gap thresholds, or box tolerances was performed. The ignored-field/skew control applies to V1 with fixed envelopes and selected table tokens; upstream processing can use those fields.
- No image-fading or ink-intensity perturbation was run. Faintness can change the image-model output; omission of discounted OCR entries and zero OCR confidence were tested with unchanged pixels. Nondefault layout flags/alternative layout models were traced where discussed, not exhaustively run.

RESULT: ANSWERED A finds table regions from pixels but OCR geometry controls text admission; B needs complete within-cell pieces because V1 does not split fused text.
