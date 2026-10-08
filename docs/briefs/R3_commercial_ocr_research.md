# R3 — research: which commercial / hosted OCR will help most as a reliable reader for Greek (gpt-6-astra, web-enabled, read-mostly)
Workspace = greek-ocr-toolkit. Write ONLY docs/research/COMMERCIAL_OCR_20261008.md (+ a JSON table beside it). No code changes. No `.git`.
Context: we build a lightweight Greek OCR (Docling plugin). We need a reliable, independent reader for VERIFICATION on small samples
(hundreds to a few thousand lines at a time): polytonic Greek print 1850–1950 (parliament proceedings, gazettes, books; curled scans),
modern Greek born-digital and scanned pages, mixed Greek/Latin, some Cyrillic. Current independent reader: CLLG (Inria Kraken PP-OCRv6):
1.3% CER on 300 real polytonic gold lines; Tesseract 4 grc: 33% (unusable). The bake-off harness already has candidate kinds for
Google Document AI, Azure Document Intelligence and Mistral OCR behind --service; new engines need an adapter (line-image in, text +
per-char/word confidence out).
Evaluate (with URLs and dates for every claim; mark unknowns): Google Document AI / Cloud Vision; Azure AI Document Intelligence (Read);
Mistral OCR; Amazon Textract; ABBYY (FineReader Engine / Cloud / Vantage — "Greek (ancient)"/polytonic support); Transkribus (public models
for printed polytonic Greek; API; pricing credits); vision LLMs as OCR (Gemini 2.5 Pro/Flash, GPT-5.x vision, Claude): determinism,
cost, polytonic evidence; eScriptorium/Kraken hosted; any Greek-specific services (e.g. from Greek academia/industry). For each:
polytonic/ancient Greek support (explicit?), modern Greek, mixed script, line-image vs page input, confidence outputs (char/word),
output format (text, boxes, reading order), price per 1,000 pages/lines, free tier, rate limits, latency, data-use/retention terms
(is our data used for training? opt-out?), EU data residency, any published Greek accuracy evidence or benchmarks (esp. historical print),
and integration effort for our harness. Then: a ranked shortlist with reasoning; a 1-day test plan on our 300 Polyton-DB gold lines +
the 44 owner-checked parliament lines + 100 modern born-digital lines (what to measure: strict NFD CER, mark F1, Greek→Latin
homoglyphs, determinism across two calls, cost); and ONE recommendation to enable first with the exact credential/setup steps.
Last line exactly: `R3: done | recommended: <engine>`.
