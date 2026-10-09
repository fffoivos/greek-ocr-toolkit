"""Build REPORT.md from source evidence and the experiment result files."""
from summarize import rows,group_label
from research_orientation import *
def table(headers,data):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in data])
def detector_table():
    summary=load('results_summary.json')['rows'];groups={}
    for r in summary:
        if r['detector']=='geometry projection':continue
        groups.setdefault((r['detector'],r['unit']),[]).append(r)
    data=[]
    for (det,unit),rr in groups.items():
        rr=sorted(rr,key=lambda r:r['rotation_cw']);n=sum(r['n'] for r in rr);right=sum(r['correct'] for r in rr);ab=sum(r['abstain'] for r in rr)
        data.append([det,unit,'; '.join(f"{r['rotation_cw']}°: {r['correct']}/{r['n']}" for r in rr),f'{right}/{n} ({100*right/n:.1f}%)',ab,f"{sum(r['mean_seconds']*r['n'] for r in rr)/n:.4f}"])
    return table(['Detector','Unit / test category','Correct / total by observed CW rotation','Overall','Abstentions','Mean seconds per input'],data)
def main():
    line_summary=load('lines_summary.json');layout=load('layout_summary.json')['cases'];lt={r['id']:r for r in layout};tc=load('table_results.json')['cases'];backend=load('backend_results.json');local=load('local_results.json')['cases'];real=load('real_local_results.json')['cases'];manifest=load('run_manifest.json')
    line_table=table(['Observed CW rotation','Pages','Mean kept lines','Median of page median length (px)','Median of page median x-height (px)','Mean page fraction length <3×own x-height','Mean s/page'],[[r['rotation_cw'],r['n'],f"{r['mean_kept']:.1f}",f"{r['median_page_median_length']:.1f}",f"{r['median_page_median_xheight']:.1f}",f"{100*r['mean_page_fraction_short']:.1f}%",f"{r['mean_seconds']:.2f}"] for r in line_summary['rows']])
    layout_table=table(['Source page','Applied CW0°: raw clusters / retained tables','90°','180°','270°'],[[name]+[f"{lt[name+f'__r{a}']['raw_clusters']} / {len(lt[name+f'__r{a}']['retained_tables'])}" for a in (0,90,180,270)] for name in sorted({r['id'].split('__')[0] for r in layout if r['kind']=='whole'})])
    table_table=table(['Table input','Mode','Predicted rows×cols','Orientation emitted','Input→assigned labels','Known logical cell ownership','Seconds'],[[r['id'],r['mode'],f"{r['num_rows']}×{r['num_cols']}",r['orientation'],f"{r['input_tokens']}→{r['assigned_tokens']}",f"{r['logical_grid_correct']}/12" if r['logical_grid_total'] else 'unannotated',f"{r['seconds']:.3f}"] for r in tc])
    local_table=table(['Composite insertion','Blind proposals','Best IoU with inserted ROI','Detected at IoU≥0.3','Inserted threshold-ink coverage','Proposals outside inserted ROI','Seconds'],[[r['id'],len(r['proposals']),f"{r['best_iou']:.3f}",r['detected'],f"{100*r['inserted_threshold_ink_covered']:.1f}%",r['outside_roi'],f"{r['seconds']:.4f}"] for r in local])
    real_table=table(['Real image crop','Manual CW angle','Ink asymmetry','OSD','4-way Greek OCR vote','Axis + RapidOCR'],[[r['annotation']['id'],r['annotation']['truth_cw']]+[str(r[d]['pred_cw']) for d in ['geometry','osd','ocr_vote','rapid']] for r in real])
    line_details=table(['Source','Observed CW0° kept / short%','90°','180°','270°'],[[name]+[next(f"{r['kept']} / {100*r['shorter_than_3xh']:.1f}%" for r in line_summary['cases'] if r['id'].startswith(name+'__') and r['truth_cw']==a) for a in (0,90,180,270)] for name in sorted({r['id'].split('__')[0] for r in line_summary['cases']})])
    pdf_table=table(['Backend','/Rotate','Page dimensions','Bitmap dimensions','MAE vs rotated /Rotate=0 bitmap','Native text lines'],[[r['backend'],r['pdf_rotate'],f"{r['page_size']['width']}×{r['page_size']['height']}",str(r['render_size']),f"{r['mae_to_rotate0']:.6f}" if r['mae_to_rotate0'] is not None else 'size mismatch',r['native_text_cells']] for r in backend['pdf_tests']])
    layout_times=[r['seconds'] for r in layout]
    real_original=next(r for r in line_summary['cases'] if r['id']==REAL+'__r0');real_normal=next(r for r in line_summary['cases'] if r['id']==REAL+'__r90')
    report=f'''# Writing orientation: installed Docling and offline rotation experiments

Research date: 9 October 2026. Primary evidence is installed source and fresh experiments in this directory. No PDF OCR text layer was used as reference. Versions and source/model hashes are in [run_manifest.json](run_manifest.json), [source_evidence.json](source_evidence.json), and [model_files.json](model_files.json).

## 1. Answer for the owner

**We must detect the orientation of local writing ourselves, before fitting horizontal lines. A page-wide rotation decision cannot solve this.** The real page demonstrates three directions on one image: the main title and numeric rows are sideways at clockwise 270°, the header word “Καπνοῦ” is upside down at 180°, and the folio is upright at 0°. [Image-labelled examples](real_local_labels.png).

Docling honours PDF `/Rotate` and image EXIF orientation. Its Tesseract engines also run OSD on OCR rectangles and map recognised boxes back. But the standard image-layout stage runs **before** that OCR correction, and default TableFormer does not use the text rectangle's angle to rotate its table image. Docling can find some sideways tables, including this one, but it misses others. A surviving “Table” label does not establish a correct logical grid.

**Use component-neighbour geometry to find the horizontal/vertical text axis locally. Decide upright versus upside down with line or block evidence when available, and attach that decision to each word.** Ink alone got the axis right on 40/40 whole-page rotations and 12/12 skew controls here. Greek letter asymmetry was useful on blocks but insufficient on short words. Tesseract OSD is an optional page/block check, not a word detector. The cached RapidOCR binary classifier was poor on these Greek line and word crops.

For an isolated word, the best measured fallback was **ink axis + Greek OCR scoring of the two possible upright directions**: 48/48 padded word rotations, versus 44/48 with unconstrained four-way OCR. However, both scored 0/4 on the smaller-margin pasted-word ROI crops. This padding sensitivity, and the blind proposal results below, prevent a production reliability claim. Use this as the implementation starting point with explicit abstention, context aggregation and consistent crop preparation; validate the same two-hypothesis approach with our own recognizer. Do not force a confident orientation for a single digit or a word with inadequate evidence.

For a uniformly rotated page, normalize the whole page **before layout**, keeping backend size, pixels and coordinates in the same frame. An OCR plugin invoked after layout cannot do that retroactively. On a mixed page, rotate each local OCR crop for fitting/recognition, then inverse-map its four corners to the **current Docling page frame**. Keep Greek `text_direction=left_to_right`; the rectangle carries geometric rotation. For sideways **table structure**, add a table-stage adapter that rotates the table crop and tokens together and maps the predicted grid back. Returning rotated OCR cells alone does not supply that adapter.

## 2. Docling source trace and coordinate contract

Source prefixes:

```text
SP = /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/lib/python3.11/site-packages
D  = SP/docling
C  = SP/docling_core
P  = SP/docling_parse
L  = /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4
```

The following references name the installed files, not web documentation or recollection. Exact excerpts and SHA-256 hashes are archived in `source_evidence.json`.

| Finding | Installed file:line evidence |
| --- | --- |
| Default PDF backend is the threaded parser | `D/document_converter.py:271–277` |
| Default OCR options select an availability-dependent OCR engine, not necessarily Tesseract | `D/datamodel/pipeline_options.py:2153–2161` uses `OcrAutoOptions`; `D/models/stages/ocr/auto_ocr_model.py:65–80,121–139,152–165,175–189` tries macOS OCR, RapidOCR ONNX, EasyOCR and RapidOCR Torch as available. Tesseract OSD behaviour applies when a Tesseract engine is explicitly selected. Our plugin replaces that engine. |
| PDF content coordinates are relative to page boundary and transformed by `/Rotate` | `P/pdf_parser.py:1264–1279`; default backend uses parser rendering and page dimensions at `D/backend/docling_parse_backend.py:246–261,291–301` |
| Alternative PDFium backend also reconciles object coordinates with the rotated display frame | `D/backend/pypdfium2_backend.py:164–204`; rendering uses `rotation=0` meaning **no additional** rotation at `:655–665` |
| Image metadata orientation is applied | `D/backend/image_backend.py:56–69`, `ImageOps.exif_transpose`; this reads metadata, not letter orientation |
| Order is preprocess → layout → OCR → layout postprocess → table → assemble | `D/pipeline/standard_pdf_pipeline.py:787–794`; do not infer execution order from the differently ordered `stages` list at `:796` |
| Heron input is pixels and page-number metadata only | `D/models/stages/layout/layout_object_detection_model.py:95–115`; scaled, axis-aligned output boxes at `:149–185`; Transformers inference at `D/models/inference_engines/object_detection/transformers_engine.py:220–244` |
| No general pre-layout writing-orientation classifier/option was found in this standard pipeline | Searched installed `D` Python source for `orientation`, `rotation`, `rotate`, `text_direction`; options select Heron at `D/datamodel/pipeline_options.py:1691–1720`. PDF/EXIF handling and OCR-specific paths exist; this is not a claim that every optional OCR engine is orientation blind. |
| Both Tesseract engines perform OSD for each selected OCR rectangle, even with explicit languages | CLI `_perform_osd` at `D/models/stages/ocr/tesseract_ocr_cli_model.py:262–284`, called unconditionally at `:351–374`; bindings call `DetectOrientationScript` at `D/models/stages/ocr/tesseract_ocr_model.py:193–220` |
| `lang=[]` additionally enables automatic script reader selection | `D/datamodel/pipeline_options.py:614–665`; CLI `_auto_script` at `D/models/stages/ocr/tesseract_ocr_cli_model.py:74–76`. If OSD fails, auto mode skips that rectangle; explicit language mode continues with unrotated OCR at `:356–369`. `psm`, `lang`, `scale`, `path` and command selection are OCR options, not page/layout rotation controls. |
| OSD angle is converted CW→CCW, corrected pixels are read, cells are mapped back | `D/models/stages/ocr/tesseract_utils.py:119–163`; CLI correction at `:370–374` and cells at `:409–423`; corner geometry in `D/utils/orientation.py:12–70` |
| `TextCell.rect` is an oriented four-corner rectangle | `C/types/doc/page.py:109–161,281–309`; width is corner 0→1, height is 0→3, and `angle_360` is CCW degrees computed from ordered corners |
| `text_direction` is LTR / RTL / unspecified, not 0° / 90° / 180° / 270° | `C/types/doc/page.py:273–309`; parser maps its boolean LTR property at `P/pdf_parser.py:398–428`. There is no separate angle/orientation field on `TextCell` or `PdfTextCell`; angle is derived from `rect`. |
| Later layout assignment uses the axis-aligned envelope | `D/utils/layout_postprocessor.py:660–688`; `rect.to_bounding_box()` takes coordinate minima/maxima at `C/types/doc/page.py:169–196`, discarding oriented edges |
| Default TableFormer V1 discards oriented token geometry and uses the uncorrected page image | `D/models/stages/table_structure/table_structure_model.py:213–273`; it calls `page.get_image(scale=2)`, converts each rect to an AABB and then reconstructs an axis-aligned rect, sending tokens with only ID/text/bbox |
| TableFormer V1 has matching and fast/accurate options, no orientation correction option | `D/datamodel/pipeline_options.py:151–174`; table construction omits orientation at `D/models/stages/table_structure/table_structure_model.py:294–322` |
| Table orientation is representable but not inferred by this stage | `D/datamodel/base_models.py:436–441` defaults to `ROT_0`; reading order copies it at `D/models/stages/reading_order/readingorder_model.py:256–273`. `C/types/doc/items/table/table_data.py:90–111` defines CCW table orientation; row/column bbox helpers use it at `:295–315,388–407`. It does not rotate tokens or rerun a neural model. |
| A later visualization actually uses rect angle | `C/types/doc/page.py:1254–1278` rotates drawn text according to `rect.angle_360`; standard reading-order child text/provenance uses cluster AABBs at `D/models/stages/reading_order/readingorder_model.py:97–112`. Search found no rect-angle or `TextCell.text_direction` consumer that corrects default layout/table inference. HTML direction helpers infer bidi direction from text instead. |
| RapidOCR has local text direction classification, not a general page normalizer | `D/datamodel/pipeline_options.py:425–449` exposes `use_cls`; OCR call at `D/models/stages/ocr/rapid_ocr_model.py:764–798`. Cached classifier labels are only `0,180` at `SP/rapidocr/config.yaml:161–168`; it flips crops at `SP/rapidocr/ch_ppocr_cls/main.py:77–110`. |

### PDF metadata experiment

`research_docling.py backend` writes an image-only PDF derived from the upright book page, applies `/Rotate=0,90,180,270`, and runs both installed backends. Bitmap comparisons use each backend's own zero-rotation render. No PDF text exists in this fixture.

{pdf_table}

The same probe exercised Docling's installed Tesseract corner mapper for all four angles, with scale 2 and crop offset `(11,13)`. Detailed corners and AABBs are in [backend_results.json](backend_results.json). **Our emitted cells belong in the rendered/display page frame already used by Docling**, after metadata rotation, with crop offsets and rendering scale removed. They do not belong in raw, pre-`/Rotate` PDF coordinates. If we introduce additional global normalization, all page consumers must share that new frame, and the transform back to the source must remain explicit.

## 3. Reproducible test set

Generation: [research_orientation.py](research_orientation.py), stage `generate`. The complete inventory, source boxes, dimensions, labels, applied transforms and PNG hashes are in [testset/manifest.json](testset/manifest.json). [contact.png](contact.png) shows all originals, and [templates.png](templates.png) shows selected crops.

| Category | Contents |
| --- | --- |
| Whole images | All 10 supplied PNGs × applied CW `0,90,180,270` = **40**. The nine dominant-upright pages have label 0 before transformation; the real sideways page starts at 270. One supplied page mixes Greek and Arabic. |
| Skew controls | Two prose pages × CW `−5,−3,−1,+1,+3,+5` = **12**, expanded canvas, bicubic interpolation, white fill; quarter-turn label stays 0. These test orientation classification under skew, not deskew angle accuracy. |
| Local crops | Three blocks, three line crops and twelve visually checked whole-word crops × four angles = **72**. Line proposals come from the supplied **pixel** detector's curves, not PDF boxes or text. Word spans use ink gaps; the third source's spans were manually corrected before the final benchmark. Bounding line crops can include small neighbouring fragments on skewed originals. |
| Mixed composites | Two prose bases × block/line/word insertion × CW `90,270` = **12**. A left strip is cleared and a rotated source crop pasted there, with an explicit inserted ROI. The rest of the page stays upright. This is a clean mixed-direction test, not a realistic estimate of tiny-header recall in crowded tables. |
| Extra real local probes | `research_real_local.py` generates 3 image-labelled crops: main title 270°, “Καπνοῦ” 180°, folio 0°. The folio is deliberately orientation ambiguous at glyph level. |
| Extra TableFormer control | `research_docling.py tables` generates a known 4×3 ruled grid from the source word pixels, at CW0 and CW90. Its token row/column identities are known by construction. |

Primary total: **136 images, 64 of them pages**. Each orientation candidate runs on all 136 and additionally on the 12 composite ROIs: **148 unit evaluations per candidate**. Heron runs 64 fresh page forwards. The current line detector runs all 40 whole-page cases at original resolution. TableFormer runs 6 image/table cases × 2 modes = 12 fresh forwards. Extra real crops are reported separately.

Angles in the manifest and detector tables are **observed clockwise angles from upright**. Correction is Pillow `rotate(+observed_cw, expand=True)`. Docling rectangle/table angles instead use CCW, so observed CW90 is rect/table CCW270. Positive synthetic skew is CW. Quarter turns use exact pixel transpositions; skews interpolate.

Reproduce sequentially, in the foreground, from this directory:

```bash
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
"$PY" research_orientation.py generate
"$PY" research_orientation.py geometry
"$PY" research_orientation.py osd
"$PY" research_orientation.py ocr_vote
"$PY" derive_candidates.py
"$PY" research_rapid.py
"$PY" research_orientation.py layout
"$PY" research_orientation.py lines
"$PY" research_docling.py backend
"$PY" research_docling.py tables
"$PY" research_local.py
"$PY" research_real_local.py
"$PY" summarize.py
"$PY" write_report.py
"$PY" verify_artifacts.py
```

Scripts enforce offline mode and place subprocess temporary files under `./tmp`. Cached model files are read by explicit local path; all created files are here. No background jobs or repository edits were made. Heron/TableFormer use CPU and four PyTorch threads. Tesseract is 5.5.3 with one OpenMP thread; RapidOCR's cached ONNX classifier runs through **OpenCV DNN CPU**, since `onnxruntime` is absent in the supplied Python. This tests the available model's predictions with its installed preprocessing, not a full RapidOCR pipeline.

## 4. Orientation candidate results

**Accuracy includes abstentions as failures.** `None` means no decision. Axis-only accuracy identifies `0/180` versus `90/270` and must not be compared as though it were four-way accuracy. Times include per-call image work and subprocess startup except where noted; crop times are per crop, page times per page. They exclude script imports/model loading. This is a small, correlated fixture set, not a held-out corpus: rotations of one source are not independent samples.

{detector_table()}

Complete rotation-specific rows and actual runtimes are in [results_summary.csv](results_summary.csv). Raw decisions, confidences and reasons are in `geometry.jsonl`, `osd.jsonl`, `ocr_vote.jsonl`, `constrained_vote.jsonl`, and `rapid.jsonl`.

### What each method establishes

**Ink axis / Greek asymmetry:** adaptive local thresholding, long-rule removal, connected-component neighbour spacing and projection concentration. Dominant nearest neighbours distinguish text running across versus down the image. Global normalized projection alone got only 28/40 whole-page axes and 7/12 skew axes, because margins, columns and sparse content compete with row bands; component geometry reached 40/40 and 12/12. After axis alignment, the prototype scores detached marks above/below letter bodies plus relative top/bottom contact alignment. This correctly polarizes all 12 block rotations, but only 6/12 line rotations and 20/48 word rotations (12 word abstentions). Greek accents, ascenders and descenders are useful **statistical evidence**, not a guaranteed word-level feature: attached marks, punctuation, capitals, few components, faded ink and neighbouring fragments confound it. A three-letter word can establish an elongated axis without establishing polarity. The thresholds were developed on this same set; they need held-out validation.

**OSD:** measured 38/40 whole-page decisions, with the two navigation-spread errors at CW90 and CW270 selecting the opposite polarity (confidence 3.90 and 3.16). On skew controls it abstained on four low-contrast scans. It abstained on all 48 isolated word cases with insufficient characters; lines/blocks also sometimes fail or flip. It reports one dominant direction per supplied rectangle, so a correct composite full-page answer still says nothing about the inserted sideways words. Smallest useful unit here is a text-rich block, not a word. Its confidence is not a calibrated probability.

**Four-way Greek OCR vote:** Tesseract `grc+ell`, no OSD, tests four corrected views. PSM11 for pages, 6 blocks, 7 lines and 8 words. Score is the sum of nonnegative OCR confidence × Greek character count; the OCR strings are observations, not ground truth. Numeric tables and Arabic are outside that scoring objective. It scored all four navigation rotations along the wrong axis, and the real mostly numeric table along another wrong axis. Restricting the choices to the independently measured ink axis improves 32/40 pages to 36/40 and 44/48 words to 48/48. It still abstains on poor skew/page inputs and flips the two pasted short words at both rotations. The verifier confirms that the four pasted-word ROI interiors have exactly the same rotated word pixels as their standalone crops; only the white margins differ (8 versus 20 pixels). Different surrounding white margins change short-word Tesseract results. Production should use a consistent crop/unroll policy and calibrate the actual Greek engine's two scores, including blank/garbage rejection.

The four-way experiment caches **only identical resized RGB pixels, dimensions and PSM**, checked by SHA-256, across rotated equivalents. There were {manifest['ocr_vote_cache']['actual_tesseract_forwards']} actual Tesseract recognition forwards for {manifest['ocr_vote_cache']['logical_hypothesis_evaluations']} logical hypotheses. Table times above use the sum of measured uncached inference costs plus each call's preprocessing; raw JSON also preserves actual cached elapsed time. `constrained_vote` is a derived two-hypothesis evaluation using those actual outputs and ink-axis decisions; its cost is the two measured subprocess costs plus geometry, excluding PNG preprocessing. It is not an independently timed optimized recognizer.

**RapidOCR binary classifier:** the available Chinese PP-OCR mobile 0/180 model is fast, but axis+classifier got only 28/48 word crops and 2/12 line crops. It is unsuitable as the sole Greek polarity decision on these scans. Feeding a whole page to its 48×192 text-strip input is outside its intended unit; those page results are diagnostic only. `use_cls=True` does not create a four-way page/word detector by itself.

### Blind local proposal experiment

The earlier crop tests know where the rotated text is. To avoid confusing that with detection, [research_local.py](research_local.py) independently proposes vertical component chains across the entire composite **without reading its ROI**. It uses local nearest-neighbour votes, chains of at least three bodies, and elongation. Only the evaluator reads the insertion box. It detects an inserted unit when a proposal's IoU with that box is ≥0.3; this is a lenient region diagnostic, not word annotation recall. Blue/red overlays are in `testset/*_local.jpg`.

{local_table}

These results measure discovery separately from polarity. Multiple short chains inside a large block can be useful text proposals while failing block-envelope IoU, so the table also reports the fraction of the inserted ROI's thresholded foreground covered by the **union** of proposal boxes. That is an ink-coverage diagnostic, not manually annotated word recall; it can include paper texture/noise. Proposals outside the inserted ROI are false-positive **candidates** on these otherwise horizontal prose bases; stamps and segmentation noise were not independently annotated. A production implementation must group consistent chains and reject nontext; oracle ROI accuracy cannot be used as its end-to-end accuracy.

### Local directions on the actual page

{real_table}

The image inspection, not an OCR transcription, supplies these labels. The title crop is only a fragment of its printed line, and the numeric folio is not proof of word-polarity reliability. Full details and timing are in [real_local_results.json](real_local_results.json).

## 4a. Docling layout, separately

Every case ran the installed `LayoutObjectDetectionModel.predict_layout` and its default postprocessor with **no OCR cells**. Heron used PNG/3 logical dimensions and the image at scale 1.0, following Docling's layout image path. This isolates image classification from OCR-driven text-cluster resizing. Empty text clusters can disappear in postprocessing; table wrappers are retained if their image confidence clears the default 0.5 threshold.

Mean Heron forward time: **{np.mean(layout_times):.3f} s/page**, range {min(layout_times):.3f}–{max(layout_times):.3f}; model load {load('layout_config.json')['load_seconds']:.3f} s. Counts are behaviour diagnostics, **not layout accuracy**, because a complete manually annotated layout corpus was not created.

{layout_table}

The real sideways table remains a table at confidence **0.980** in its original sideways view, **0.972** after CW90 correction, **0.970** after CW180 and **0.977** after CW270. Page 35 retains its table at **0.982 / 0.716 / 0.986 / 0.778** for applied `0/90/180/270`. The navigation spread has two retained tables at 0° and 180°, and **none** at 90° or 270°. Its CW270 view produces 39 raw clusters instead of 5 upright. Rotation robustness is content dependent; there is no universal “sideways table becomes text” rule or a guarantee it remains a table.

Skew/composite cases, every raw box/label/confidence, and retained tables are preserved in [layout.jsonl](layout.jsonl) and [layout_summary.json](layout_summary.json). Overlays for the two parliamentary tables are in `testset/*_layout.jpg`.

## 4b. TableFormer, separately

[research_docling.py](research_docling.py) runs the actual default V1 `predict_tables` in **accurate and fast** modes, using fixed image-selected table rectangles to isolate structure from layout recall. It supplies identical source-associated placeholder labels with transformed four-corner geometry, not recognised Greek truth. Table 35 and the real page are tested at applied CW0 and CW90; for the real page, CW90 is normalization. The original detector's bad cells are deliberately not treated as word annotations. The controlled grid's labels have known logical row/column ownership. Every table image runs a fresh neural forward.

{table_table}

All emitted table orientation values remain `rot_0`, even on rotated inputs. **Accurate recovered the upright known grid as 4×3 with 12/12 correct logical label locations; at CW90 it returned 3×4 with 0/12 correct locations, while retaining all 12 strings.** Fast already under-segmented the upright grid (4×2, 8/12 correct), and its CW90 grid gave only 1/12 correct locations. Rotation correction therefore cannot be assumed to repair all intrinsic table-model errors. The real-data grid dimensions and token survival are **not structure accuracy**; the input segmentation can be wrong and no complete real cell grid was hand-labelled. Inspect `assignments` in [table_results.json](table_results.json). These measurements directly test why sending rotated rectangles is not equivalent to correcting TableFormer's table view.

## 4c. Our current line detector, separately

`segment_page` was imported read-only from the specified worktree and run with **no hints**, at original PNG resolution. All 40 whole-page cases were recomputed. Kept means `discounted is None`; “short” compares each line's x span with **its own** x-height. Times include pixel preparation, segmentation and guide fitting, but exclude output serialization/overlay drawing.

{line_table}

Detailed per-source counts:

{line_details}

On the real original sideways page the fresh run kept **{real_original['kept']}** lines, median x span **{real_original['median_length']:.1f} px**, median x-height **{real_original['median_xheight']:.1f} px**, **{100*real_original['shorter_than_3xh']:.1f}%** shorter than three own x-heights. After clockwise90 normalization it kept **{real_normal['kept']}**, with median span **{real_normal['median_length']:.1f} px** and short fraction **{100*real_normal['shorter_than_3xh']:.1f}%**. Remaining perpendicular headers still need local handling.

The failure mechanism is explicit in code: `L/greekocr/glyphs/page_text_lines.py:27–42` stores every guide as y(x), `_discover` searches row-profile peaks and fits assumed-upright bodies at `:143–172`, and `segment_page` invokes that directly at `:927–966`. `pixel_segments.py:1–5` describes gutters then row valleys. At 90/270°, it cuts across vertical letter streams and constructs horizontal pseudo-lines: many short slices on some pages, long cross-stream bands on others. For example the prose book page `an-d6...` goes from 35 kept lines to 96 at CW90 while retaining a 432px median x span; a short-line heuristic alone misses that failure. At 180°, long x spans can survive, so short-span diagnostics alone cannot establish success: baseline/meanline/accents and reading direction are reversed relative to its upright assumptions. We did not measure final recognition or manually annotate every fitted guide, so do not call the 180° output correct merely because its line count resembles upright output. See `testset/*_lines.jpg` and [lines.jsonl](lines.jsonl).

## 5. Specification for implementation part 3

This is an OCR geometry feature plus an explicit integration requirement. It should not depend on a PDF OCR text layer.

1. **Input/frame setup.** Consume the pixels in the backend's rendered frame after PDF/EXIF metadata rotation. Record image-to-page scale, crop offset and source-to-current-page transform. Optionally obtain a dominant page prior from OSD/ink votes. A confident global correction must be applied before Heron through a coherent page/backend adapter; do not mutate only an OCR crop or only the cached page bitmap. Keep mixed regions eligible for different directions even after that correction.
2. **Local discovery before horizontal fitting.** Extend pixel segmentation with orientation-neutral component extraction, rule exclusion and neighbourhood direction evidence. Detect separate horizontal and vertical text chains; group chains by direction/scale without joining across table rules, columns or words with different directions. Do not let today's horizontal `segment_page` determine where all rotated words must be. Use layout/table regions as hints, while retaining candidates missed by layout.
3. **Separate axis, polarity and skew.** Axis is `horizontal/vertical/unknown`; quarter-turn orientation is `0/90/180/270/unknown`; skew is a small signed residual angle. Aggregate evidence from coherent line/block neighbours to establish polarity. Greek accent and baseline statistics are a cheap prior. OSD can check text-rich groups. Isolated-word fallback evaluates the two axis-consistent rotations with the recognizer; require meaningful text evidence and a calibrated score margin, otherwise keep both hypotheses or mark unknown. Reject interpreting ±1–5° as a quarter turn. Numerals/capitals and sparse marks must not force a false polarity.
4. **Normalize locally, then detect/recognize.** Resample/rotate each coherent local region into an upright horizontal view. Use a stable padding, paper/contrast and scale policy, since the pasted-word tests exposed sensitivity. Run existing horizontal line fitting in that view, split words without crossing logical table cell boundaries, recognize, and inverse-map word corners **and line-guide geometry**. For a vertical source line, store curves parametrically or in its local frame plus affine transform; y(x) alone cannot represent it.
5. **Output per word.** Return unique IDs, recognised text, `from_ocr=True`, recognition confidence, ordered oriented rectangle in the current page frame, and `TextDirection.LEFT_TO_RIGHT` for Greek. Preserve separately `orientation_cw`, axis/polarity confidence, residual skew, evidence source, `unknown`/alternative hypotheses, group ID, local-to-page transform and source provenance. Do not overload OCR recognition confidence with orientation confidence. Use corner order from the canonical upright word `(bottom-left,bottom-right,top-right,top-left)` mapped through the inverse transform; merely enumerating AABB corners loses rotation. Keep words individually addressable even when they inherit a line/block decision.
6. **Table integration.** In a separately adapted table stage, normalize a rotated table image, its crop boundary and all candidate tokens together before TableFormer. Inverse-map output cell boxes and preserve canonical logical row/column indices. Set `Table.orientation` to the corresponding **CCW** orientation so `TableData` consumers see the correct direction. The current default V1 stage must be bypassed/wrapped for this; an OCR-only change cannot make it consume rect angles. Keep the existing native-word precedence/ownership issue explicit: cached backend words must not silently supersede our pixel OCR cells.

Proposed acceptance tests, with this set as deterministic regression fixtures (these are requirements for part 3, not claims that the exploratory prototypes already pass):

| Test | Acceptance requirement |
| --- | --- |
| Offline/frame metadata | Both PDF backends honour all four `/Rotate` values; no native text required. Round-trip corner geometry, offsets and scale error ≤1 source pixel; no double application of metadata rotation. |
| Whole-page direction | Correct axis on all 40; accepted polarity decisions contain no known opposite-polarity error, with abstentions logged. Low-confidence OSD navigation failures must be flagged or resolved by other evidence. |
| Skew controls | All 12 stay at quarter-turn orientation 0; residual skew handled separately. A later deskew implementation must be independently checked against labelled residual angles, allowing pre-existing scan skew. |
| Word orientation | At least 46/48 correct on the padded word rotations; all four pasted-word ROIs must also be correct **after the same production crop policy**, or explicitly abstain with preserved alternatives. Report decision coverage and error rate separately. A good score on padded oracle crops alone is insufficient. |
| Blind mixed discovery | Each of the 12 inserted units must be discovered without manifest ROI hints; ≥0.5 coverage IoU of its region union, with words' true ink covered. No uncontrolled population of vertical false-positive text chains. Annotate word boxes for stricter recall/precision before release. |
| Real mixed page | Distinguish title 270° and “Καπνοῦ” 180° in the source frame; allow `unknown` for the ambiguous numeric folio. Inspect all other perpendicular headers before claiming full-page word coverage. |
| Existing line fitter | On normalized versions of each whole-page fixture, inverse-mapped output should agree with the same upright-view baseline within measured numerical tolerance. Preserve each word's corner order and guide-frame transform. Reject the known 327-slice behaviour as successful text lines. |
| Table grid | Controlled 4×3 grid remains the same logical grid and token ownership under quarter turns through the adapter. Add 180/270 controlled-grid cases for implementation testing. Real table text/structure recall needs manual cell annotations; token survival alone is not acceptance. |
| Pipeline stage ordering | Global correction precedes layout. Local OCR correction returns cells in the current page frame. Table adaptation receives matching normalized pixels and token geometry, then returns the mapped grid with orientation set. |

Use source-disjoint real held-out scans before setting production confidence thresholds. Keep the current scripts/manifest as regression evidence; do not tune solely until these repeated rotations pass.

## 6. What could not be verified

- A universally reliable, blind word-orientation detector is **not established**. Crop-level decisions and discovering those crops are separate problems; pasted-word and blind-proposal tests expose remaining failures.
- Our recognizer was not loaded for polarity scoring or OCR accuracy testing. Tesseract scores test a possible fallback, not the quality/calibration of our recognizer. No Greek text transcription accuracy is reported.
- No complete ground-truth word, line or table-cell annotation was made for the 10 real pages. Layout counts, real-table dimensions, label survival, and short-line rates are diagnostics, not full precision/recall or table accuracy. Only the constructed grid has known logical cell identities.
- No production plugin, pre-layout normalizer or rotated-table adapter was implemented or run end to end. These experiments isolate actual installed stages with stub page wrappers and no native text. Other Docling table backends (V2/Granite/VLM) were not benchmarked.
- The native PDF parser's compiled implementation was not traced in C++ source. Its Python frame contract and observed image-only PDF renders were checked; crop-box offsets, nonzero PDF origins, malformed `/Rotate`, EXIF integration and rotated native-text rectangles were not exhaustively exercised.
- The cached RapidOCR classifier ran through OpenCV because its usual ONNX runtime is absent. Its results do not benchmark RapidOCR detection/recognition, all model variants or another OCR orientation network. No downloads were attempted.
- Skew tests establish quarter-turn classification behaviour only. They do not measure deskew estimator error, arbitrary-angle words, mirrored pages, handwriting or true top-to-bottom character stacking. Vertical **rotated Greek words** are not the same writing system as stacked vertical glyphs.
- Timing is single-machine CPU latency on a small fixture set, without repetitions or confidence intervals. OCR caching and derived two-hypothesis timing are disclosed above. Letter-asymmetry/local-proposal parameters and crop preparation were explored on this set; it is not an unbiased generalization benchmark.

RESULT: ANSWERED Installed rotation handling, local-direction limits, offline experiments and an implementation contract are documented; production word detection remains to be validated.
'''
    (ROOT/'REPORT.md').write_text(report)
    print('Wrote REPORT.md',len(report.split()),'words',flush=True)
if __name__=='__main__':main()
