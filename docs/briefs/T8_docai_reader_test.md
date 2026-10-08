# T8 — Google Document AI reader adapter + the 444-line commercial-OCR test driver (gpt-6.1-sol, xhigh). Workspace = this repo.
No `.git` writes (T8_HANDOFF.json). No network: build everything against a recorded fixture response and mocks; the coordinator runs the
live calls afterwards (`greekocr readers docai run ...`). Do not touch greekocr/glyphs, tests/glyphs, scripts/glyphs, docs/GLYPHS_*, docs/reviews.
Context: docs/research/COMMERCIAL_OCR_20261008.md (R3) recommended Google Document AI Enterprise Document OCR. Live facts (coordinator smoke
test, 8 Oct 15:55): project `ocr-ground-truth-20261008`, location `eu`, processor id `9a98b7aca3c19561` (type OCR_PROCESSOR, display name
ocr-ground-truth), default version `pretrained-ocr-v2.1-2024-08-07` (also v2.0/v1.2/v1.1/v1.0 deployed); endpoint
https://eu-documentai.googleapis.com/v1/projects/{P}/locations/eu/processors/{ID}:process with `rawDocument{content(base64),mimeType}` and
`processOptions.ocrConfig{enableSymbol:true, hints.languageHints:["el"]}`; response `document.text` plus `pages[0].tokens/symbols` with
`layout.confidence` and `layout.textAnchor.textSegments`; 2.1 s per call; auth = Application Default Credentials (google-auth) with header
`x-goog-user-project`. One line crop = one page of billing (~USD 1.50 / 1,000). On a strip that contained a neighbour line the engine
returned two lines separated by "\n" (keep ALL returned text; record line count).
Build:
1. `greekocr.readers.services.google_docai`: `DocAIReader(project, location, processor_id, version=None, language_hints=('el',),
   enable_symbol=True, user_project=None)` with `read(path) -> Reading(text, lines, token_confidences, symbol_confidences, mean_symbol_conf,
   min_symbol_conf, raw_json_path, request_id, latency_s)`; `read_batch(paths, concurrency=4)`; every call writes the raw JSON response
   to a receipts dir keyed by crop sha256 + version, and appends a ledger row (crop sha256, version, pages billed = 1, latency, timestamp,
   mean/min confidence); a cache so a repeated run re-uses receipts unless `--fresh`; a `binding()` dict (project, location, processor,
   version, options) for provenance. Pure-Python requests + google-auth; no Google client library.
2. Test driver `greekocr readers docai run --manifest M.jsonl --out DIR [--fresh] [--repeat N]` where each manifest row has
   {crop_path, line_id, cohort, gold_text (may be null), diagnostics: {layer_text, cllg_text, ours_text}} → writes predictions.jsonl and
   `REPORT.md`: per cohort strict NFD CER vs gold where gold exists (Polyton-DB 300 = true gold), mark precision/recall/F1 per diacritic,
   Greek→Latin homoglyph counts, line-count anomalies, determinism (repeat calls: fraction identical, mean CER between repeats), latency and
   cost ledger; for cohorts without gold (owner 44, sample 400) report agreement with CLLG and with the layer as DIAGNOSTICS only, never as
   accuracy. Reuse greekocr.score for the scorer.
3. Manifest builders for our fixtures: tests/fixtures/polytondb_gold300 (gold.jsonl + imported_gold/crops), tests/fixtures/o4d_lines,
   tests/fixtures/o4d_sample400, and tests/fixtures/borndigital100 (if present; the coordinator is staging it).
4. Tests: recorded fixture response (synthesise from the shape above; 2 tokens/5 symbols), mocked transport, ledger/cache behaviour,
   report arithmetic on a tiny manifest, binding determinism. Docs: docs/READERS_DOCAI.md (setup, cost, data-use note: Document AI does not
   train on customer data by default per the R3 report — cite it). Last line exactly: `T8: done | tests: <n> passed`.
