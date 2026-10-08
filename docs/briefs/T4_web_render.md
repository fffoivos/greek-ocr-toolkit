# T4 — greekocr.real.sources.web_render: rendered web pages as exact-label page data (gpt-6.1-sol, xhigh). Workspace = this repo.
No `.git` writes (T4_HANDOFF.json). Network allowed ONLY for `pip`/`playwright install chromium` and for the recorded fixture capture noted below.
Owner idea (8 Oct 2026, plan O4e): render HTML pages (Wikipedia/Wikisource, government, news, social timelines) and use them as exact-label
page images: the DOM text is ground truth, the geometry is exact, and the typography/layout diversity is real. Build:
1. `render_pages(urls | html_files, out_dir, *, viewport, scale, print_to_pdf=True, screenshot=True, block_media=True) -> [PageRecord]`:
   Playwright + Chromium; for each page save (a) print-to-PDF with embedded fonts (A4, no margins beyond CSS, background on) and (b) a
   full-page PNG at `scale`; plus (c) the per-text-node line geometry from the DOM: for every text node, Range.getClientRects() → line
   boxes in CSS px → scaled to the PNG, with the text per box (split by rects); (d) a receipt per page: url, fetched_at, final URL, status,
   title, lang, sha256 of HTML/PDF/PNG, fonts used (document.fonts), licence field (caller-supplied per source), user agent.
   Determinism: fixed viewport, animations disabled, fonts awaited (document.fonts.ready), lazy images blocked or forced.
2. `records_from_pdf(pdf_path)`: run the vendored born-digital text-layer extractor (greekocr/_vendor/bench/o4b_textlayer_lines.py path /
   its API) on the printed PDF to get line records with exact boxes; cross-check against the DOM line boxes (IoU) and report agreement;
   `records_from_dom(png, dom_lines)` as the direct path. Records carry tier "exact-rendered", provenance "web_render", source url, licence.
3. `degrade_twins(page_png, labels)` hook: call the vendored page degradation (pipeline/page_degrade.py origin) if available in the vendor
   tree, else a documented stub, so each rendered page can get a scan-like twin with labels intact.
4. Source lists (`greekocr/real/sources/web_sources.py`): seed URL generators for el.wikipedia random/featured articles, el.wikisource
   polytonic pages (by category), gov.gr pages, eur-lex el, 3 Greek news front pages + article links, Mastodon public timeline (JSON API →
   rendered post HTML), Gutenberg el; each with a licence tag and a polite rate (≥1 s, robots respected).
5. CLI `greekocr web render --sources ... --max-pages N --dest DIR` and `greekocr web records DIR`.
Tests: offline, using 3 local HTML fixtures rendered by the installed Chromium (skip gracefully if Chromium absent): DOM line boxes exist
for every text node, PDF path produces records that match DOM text (NFC) on ≥95% of lines, receipts complete, determinism of boxes across
two renders. Record one fixture capture of a Wikisource polytonic page if network is available (receipt + HTML saved), else skip.
Docs: docs/API.md + docs/WEB_RENDER.md (what is exact, what is not: rendering ≠ scanning; degraded twins; licence posture).
Last line exactly: `T4: done | tests: <n> passed`.
