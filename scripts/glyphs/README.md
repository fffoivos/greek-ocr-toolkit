# Glyph and page tools

For new page work use `greekocr pages` or `greekocr.pages.process_page`.
The crop library remains `greekocr.glyphs`. This directory retains reproducible
reviews and evaluation tools; it is not a second implementation of the pipeline.

- `render_page_line_segments.py`: legacy development review wrapper around the page API.
- `build_statistics.py`: measure frozen line/structure files without detecting again.
- `audit_page_line_outputs.py`, `audit_page_line_curl.py`: current offline artifact checks.
- `eval/book_pages.py`: main's development-book page selector, unchanged.
- `archive/`: historical rounds and box-based experiments, preserved for reports.
- `../pages/check_q3_equality.py`: exact Q2/current runtime and frozen-file comparison.
- `../pages/check_q3_books.py`: exact book/corpus aggregation and frozen statistics comparison.
- `../pages/check_stage_equivalence.py`: literal-expanded AST check of stage moves.

All image/PDF acquisition utilities retain their existing explicit input and
node-side requirements. An inventory entry does not authorize their execution.

| Script or template | Role | Purpose |
| --- | --- | --- |
| [annotate_tables_round4.py](archive/annotate_tables_round4.py) | Historical reproduction | Provisional pixel annotations for the round-4 development set. |
| [audit_orientation_guides.py](archive/audit_orientation_guides.py) | Historical reproduction | Audit actual oriented delivery against part-2 lines and part-1 table ink. |
| [audit_orientation_round4.py](archive/audit_orientation_round4.py) | Historical reproduction | Validate saved orientation units, corners, guides and per-image evidence. |
| [audit_tables_round4.py](archive/audit_tables_round4.py) | Historical reproduction | Compare every round-3 check and validate all 54 delivered artifact sets. |
| [check_tables_part2.py](archive/check_tables_part2.py) | Historical reproduction | Compare part-two delivery with the frozen part-one table acceptance figures. |
| [evaluate_orientation_guides.py](archive/evaluate_orientation_guides.py) | Historical reproduction | Frozen, development-only orientation evaluation; never fits decision margins. |
| [evaluate_orientation_round4.py](archive/evaluate_orientation_round4.py) | Historical reproduction | Fixed research fixtures: measured gates, with failures and abstentions retained. |
| [evaluate_tables_round4.py](archive/evaluate_tables_round4.py) | Historical reproduction | Offline A/B acceptance measurements using the owner's installed-stage probes. |
| [generate_orientation_guides.py](archive/generate_orientation_guides.py) | Historical reproduction | Generate development-only quarter turns and labelled two-orientation pastes. |
| [integrate_docling_tables_round4.py](archive/integrate_docling_tables_round4.py) | Historical reproduction | Actual offline DocumentConverter pipeline, detector plugin with injected labels. |
| [integrate_orientation_round4.py](archive/integrate_orientation_round4.py) | Historical reproduction | Run the actual offline oriented Docling pipeline and record its stage frames. |
| [page_before_after.py](archive/page_before_after.py) | Historical reproduction | One page, before and after: the text-layer boxes, then every line's outermost boundary (greekocr.glyphs.page_lines). |
| [page_segments_report.py](archive/page_segments_report.py) | Historical reproduction | Per text-layer box of one page: (1) the curves detected on the box's crop (four guide lines of every line found |
| [render_orientation_guides.py](archive/render_orientation_guides.py) | Historical reproduction | Draw the two newly fitted guide hypotheses, with measured/borrowed labels. |
| [render_orientation_round4.py](archive/render_orientation_round4.py) | Historical reproduction | Render orientation outputs, preserving the part-two horizontal audit schema. |
| [report_orientation_guides.py](archive/report_orientation_guides.py) | Historical reproduction | Write the part-3c measured report without changing its preregistered rules. |
| [report_orientation_round4.py](archive/report_orientation_round4.py) | Historical reproduction | Bounded regression/report audit for round four's opt-in orientation path. |
| [report_tables_round4.py](archive/report_tables_round4.py) | Historical reproduction | Build the round-4 tables report from the completed, bound measurements. |
| [review_line_boundaries.py](archive/review_line_boundaries.py) | Historical reproduction | Rebuild Q1 structure from frozen records and audit every boundary/crossing. |
| [review_line_structure.py](archive/review_line_structure.py) | Historical reproduction | Address and audit frozen delivery records; never rerun the line detector. |
| [review_page_lines_round3.py](archive/review_page_lines_round3.py) | Historical reproduction | Build the 25 numbered owner-case views and a reproducible round-3 report. |
| [review_page_lines_round4_nontable.py](archive/review_page_lines_round4_nontable.py) | Historical reproduction | Recheck all owner cases and compare the 54 outputs to round-four part one. |
| [review_statistics.py](archive/review_statistics.py) | Historical reproduction | Reproduce the descriptive Q2 audit from measured tables and preselected original-image regions. |
| [score_tables_round4.py](archive/score_tables_round4.py) | Historical reproduction | Score saved full-pipeline label destinations against provisional pixel cells. |
| [summarize_page_line_review.py](archive/summarize_page_line_review.py) | Historical reproduction | Build the committed round-2 development report from completed local audits. |
| [tessellate_three_lines.py](archive/tessellate_three_lines.py) | Historical reproduction | Tessellation experiment: the first 3 body lines of each column of one page (owner 8 Oct 19:40). |
| [time_orientation_guides.py](archive/time_orientation_guides.py) | Historical reproduction | Time production orientation, including table confirmation, on upright sources. |
| [audit_page_line_curl.py](audit_page_line_curl.py) | Current crop / page tooling | Check page curves against the owner's frozen curl contact points. |
| [audit_page_line_outputs.py](audit_page_line_outputs.py) | Current crop / page tooling | Independently audit serialized page-line geometry and delivered image files. |
| [build_column_geometry_page.py](build_column_geometry_page.py) | Current crop / page tooling | build column geometry page |
| [build_final_page_data.py](build_final_page_data.py) | Current crop / page tooling | Final review page data (owner 8 Oct 16:40: ≥ 200 lines): the owner's cases, then a stratified sample of the 444 real |
| [build_page_review_data.py](build_page_review_data.py) | Current crop / page tooling | Review data for every text-layer segment of one page, with the crop-level tools, as on the first review batches |
| [build_recut_page.py](build_recut_page.py) | Current crop / page tooling | Static review page for a recut_real.py run: per line, the page context (text-layer box in red, the fixed boundary of |
| [build_review_data.py](build_review_data.py) | Current crop / page tooling | Build review-page data. Usage: build_review_data.py MODE OUT.json [PREVIOUS.json ...] |
| [build_review_page.py](build_review_page.py) | Current crop / page tooling | Inline review data into a page template. Usage: build_review_page.py DATA.json OUT.html [--template NAME.html] |
| [build_statistics.py](build_statistics.py) | Current crop / page tooling | Build Q2 statistics from frozen Q1 outputs, with resumable per-page measurement. |
| [calib_analyse.py](calib/calib_analyse.py) | Calibration | Readability thresholds from the calibration strips: reader CER per strip vs (a) the injected degradation and (b) the |
| [calib_measure.py](calib/calib_measure.py) | Calibration | Measure the glyph tools' readability quantities on every calibration strip → measurements.jsonl. |
| [calib_strips.py](calib/calib_strips.py) | Calibration | Readability calibration strips (owner 8 Oct 16:40): synthetic lines with ONE controlled degradation each, at known |
| [column_line_geometry.py](column_line_geometry.py) | Current crop / page tooling | Per column of one page: every line's own baseline (fitted alone, on its letters), then compare across lines: |
| [compare_segments_page.py](compare_segments_page.py) | Current crop / page tooling | Per input segment of a page, as two images of the same crop: before = the crop tools' main line and every neighbour |
| [detector_review_data.py](detector_review_data.py) | Current crop / page tooling | Review data for a page detector's lines, in the format of build_page_review_data.py, so that pages_review.html |
| [draw_page_lines.py](draw_page_lines.py) | Current crop / page tooling | Draw, on a page image, every text-layer box's main line per column segment as found by the crop-level tools |
| [book_pages.py](eval/book_pages.py) | Evaluation / acquisition | Several pages from the same book/PDF, for book-level statistics (fonts, ink, show-through) — the counterpart of |
| [broken_eval.py](eval/broken_eval.py) | Evaluation / acquisition | Letter ink states vs renderer-only truth (CP-G1c2 F1), with injected defects; per-defect breakdown uses only each |
| [capitals_eval.py](eval/capitals_eval.py) | Evaluation / acquisition | Capitals (owner 8 Oct: be careful with them; speaker names in capitals open many lines in the minutes). |
| [common.py](eval/common.py) | Evaluation / acquisition | Shared setup for the glyph evaluation scripts: fonts, text, and renders whose characters the font covers. |
| [diverse_pages.py](eval/diverse_pages.py) | Evaluation / acquisition | A diverse page set for the page-line work: one page per Anemi book and one per Vouli PDF (different printers, type, |
| [double_eval.py](eval/double_eval.py) | Evaluation / acquisition | Double-line flag on rendered crops: half with a full second line, half single with neighbour tips. Seed 61. |
| [eval_glyphs.py](eval/eval_glyphs.py) | Evaluation / acquisition | Letters / marks / neighbours / letter states vs renderer-only truth. Usage: eval_glyphs.py DIR N SEED P_NEIGHBOURS |
| [extract_poly_lines.sh](eval/extract_poly_lines.sh) | Evaluation / acquisition | extract poly lines |
| [fixture_double.py](eval/fixture_double.py) | Evaluation / acquisition | Double-line flag on the 44 real fixtures vs docs/records/glyphs/glyphs_fixture_labels.json (provisional, in-sample threshold). |
| [mark_stats.py](eval/mark_stats.py) | Evaluation / acquisition | Uncensored calibration evidence for NEIGHBOUR_GAP_ABOVE / _BELOW (CP-G1 F7): every small component outside the |
| [neighbour_eval.py](eval/neighbour_eval.py) | Evaluation / acquisition | Neighbour-line placement (four-line model) vs the renderer's true neighbour baselines. Seed 71. |
| [recut_summary.py](eval/recut_summary.py) | Evaluation / acquisition | recut summary |
| [recut_synth_pages.py](eval/recut_synth_pages.py) | Evaluation / acquisition | Synthetic two-column pages with per-line ink truth; a tight, truncated 'text-layer' box per target line; measure |
| [skew_eval.py](eval/skew_eval.py) | Evaluation / acquisition | Skew angle and per-column baseline error vs render truth: straight lines and bent lines. Usage: skew_eval.py DIR [N] |
| [final_page.html](final_page.html) | Current crop / page tooling | Review template |
| [pages_review.html](pages_review.html) | Current crop / page tooling | Review template |
| [recut_real.py](recut_real.py) | Current crop / page tooling | Recut real parliament lines from their rendered pages (owner 8 Oct 18:05–18:25). Runs on the worker that holds the |
| [render_page_line_segments.py](render_page_line_segments.py) | Current crop / page tooling | Reproduce the pixel-only development review and its machine-readable checks. |
| [review_page.html](review_page.html) | Current crop / page tooling | Review template |
| [run_review.sh](run_review.sh) | Current crop / page tooling | run review |
| [segment_lines_review_data.py](segment_lines_review_data.py) | Current crop / page tooling | Review data for a page segmenter + line detector, one card per segment, for pages_review.html (plain cards): the |
| [segment_page_lines.py](segment_page_lines.py) | Current crop / page tooling | Pixel rough segments (columns, rules, then row valleys), without text-layer boxes. |
