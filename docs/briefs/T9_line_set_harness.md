# T9 — Line-set measurement harness: find EVERY printed line from pixels; score candidates against a gold line inventory (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit). Network ON only for `pip install kraken` into a NEW venv `.venv-kraken` (python 3.11, torch cpu) if
`.venv` cannot take it; no `.git` writes. The MacBook runs this: CPU only, ~10 pages, keep every step under a minute per page.

## Why (owner, 9 Oct 00:00)
The plugin's Mode A re-reads the PDF's InVision OCR 1.0.1 textline cells, and the detector mode is a stub (`greekocr/deploy/docling_plugin/model.py:115`).
Lines InVision never boxed, or merged across columns/rows, never reach the recogniser; scans with no text layer (Anemi) get no lines. Vouli p00001:
71 cells for ~120 printed lines. We need a LINE SET found from pixels. This task builds the MEASUREMENT HARNESS and runs three candidates; it
does not pick the recogniser and does not do OCR.

## Inputs (all local)
- Page renders + InVision boxes for the six Vouli review pages: `~/Projects/glossapi-ocr-local/node_backup_20261008/work/claude-glyphs/pages/`
  (`<page>.png` at DPI 200 via bench/extract_lines.py SCALE, `<page>.boxes.json`); PDFs in `~/Projects/greek-page-ocr/data/raw/pdf_cache/`;
  all Vouli rows (`page`, `bbox_pixel`, `bbox_pdf`) in `~/Projects/glossapi-ocr-local/node_backup_20261008/out/e2d/vouli_v6/vouli_v6_rows.jsonl`.
- Anemi pages (NO text layer): `~/Projects/glossapi-ocr-local/node_backup_20261008/e2-assets/anemi/records/<record>/` (page PDFs/images; read the
  ledger.jsonl there for paths). Pick 4 pages: two plain prose, one with a table/navigation page, one two-column. Internal-only data (CC BY-NC-ND).
- Docling is importable in `.venv` (`import docling` ok). For the "Docling native cells" candidate, run Docling's PDF pipeline with OCR OFF on the six
  Vouli PDF pages and dump the textline cells it produces (this is exactly what the plugin receives in Mode A); record the Docling version.
- Existing code to reuse, not rewrite: `scripts/glyphs/segment_page_lines.py` (owner's pixel procedure, first version), `scripts/glyphs/page_segments_report.py`,
  `greekocr/glyphs/page_lines.py`, `greekocr/glyphs/recut.py` (fix_page), `docs/PAGE_LINES_ALGORITHM.md` (the 7-step owner procedure — follow it literally
  for candidate A), `scripts/glyphs/build_page_review_data.py` + `pages_review.html` (the owner's review page generator — REUSE its format for the output page).
- DBNet detector (ours): `~/Projects/greek-page-ocr/out/detector/gpu_final/best.pt` (+ checkpoint_meta.json); loader lives in greek-page-ocr `train/detector_*.py` /
  `pipeline/page_ocr_detector.py` (read-only; vendor the minimal loader under `greekocr/_vendor/` as the repo standard does).

## Deliverables
1. `greekocr/lines/` package: `gold.py` (gold line inventory schema + loader/writer: per page, per column, list of printed lines as {baseline polyline,
   top, bottom, column_id}), `candidates.py` with FOUR candidates behind one interface `find_lines(page_image, *, seeds=None) -> list[LineCandidate]`:
   A `owner_procedure` (docs/PAGE_LINES_ALGORITHM.md, seeds = InVision boxes when present), B `kraken_blla` (kraken's default baseline segmenter,
   CPU, optional dependency, skip with a receipt if not installable), C `dbnet_ours` (box detector), D `docling_native` (the Docling cells; Vouli only;
   for Anemi it yields nothing and that is the measurement). `score.py`: per page and per candidate: missed (gold line with no candidate covering ≥50% of
   its height within its column), merged (candidate covering ≥2 gold lines), false (candidate covering no gold line), column_violations (candidate crossing
   a gold column boundary), plus counts; and a pooled table. `cli.py`: `greekocr lines gold-draft`, `greekocr lines run`, `greekocr lines score`,
   `greekocr lines review-page`.
2. Gold inventory: there is no human-counted gold yet. Produce a DRAFT gold per page by union-and-dedupe of A, B and D with per-line provenance, then
   render it on the page (one colour per provenance) in the review-page format so the owner can mark misses/extras; write
   `docs/lines/GOLD_DRAFT_v1/<page>.json`. Scores against the draft are explicitly "draft-gold" and labelled so.
3. Run all candidates on the 6 Vouli + 4 Anemi pages; write `docs/lines/LINE_SET_MEASUREMENT_v1.md` with the pooled table, per-page table, timings
   per page per candidate, and a before/after figure for Vouli p00001 (InVision cells vs candidate A vs candidate B). Include the raw counts: printed
   lines with no InVision cell, cells holding >1 line (from the draft gold).
4. Tests under `tests/lines/` with small synthetic pages (two columns, a rule, a merged box, a missing box) proving the scorer counts missed / merged /
   false / column_violations correctly; INVENTORY registration for any fixture; docs/API.md + docs/STANDARD.md entries.
Constraints: no OCR anywhere; no changes under greekocr/glyphs (another session owns it; import only); every output page must render at phone width.
Last line exactly: `T9: done | pages: <n> | candidates_run: <list> | tests: <n> passed`.
