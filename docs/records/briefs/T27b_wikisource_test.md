# T27b — Wave 7 (resume after the T27 scan block) of the collection plan: Wikisource proofread pages (Greek polytonic + Russian) as TEST-ONLY lines with a human transcription beside the Google reading (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for el.wikisource.org, ru.wikisource.org, commons.wikimedia.org / upload.wikimedia.org (MediaWiki API; honour
robots.txt; descriptive User-Agent "GreekOCRToolkit-T27/1.0 (noncommercial OCR research)"; ≥ 1 s between requests) and Google Document AI (ADC). No Vision.
No `.git` writes. Google cost cap USD 0.80 (ledger docs/records/harvest/harvest_big/wikisource/google/budget.jsonl).
Read docs/records/harvest/COLLECTION_PLAN_v1.md (wave 7), T20 (admission module), T21 (read pattern), and docs/records/harvest/wikisource/READS.md (the T27 attempt: selection of
20 Greek + 10 Russian works and all 400 proofread transcriptions are SAVED under docs/records/harvest/wikisource/ — reuse them; do not re-select or re-fetch text).
COORDINATOR DECISIONS (15 Oct 08:15): (1) `thumb.wikimedia.org` AND `upload.wikimedia.org` are both allowed for page images; (2) honour HTTP 429 with the
Retry-After header (sleep max(Retry-After, 10 s)), keep ≥ 3 s between image requests, exponential backoff up to 5 minutes, at most 6 attempts per page; (3) request
ONE thumbnail size per page (width 2,500 px; 1,600 px fallback on repeated 429) through the API's imageinfo `iiurlwidth`/`iiurlparam` for the DjVu/PDF page, not
by probing several sizes; (4) if after the whole backoff schedule fewer than 50 % of pages are obtained, finish with what was obtained and report the shortfall.
These lines are TEST/DEV only — never train. Disk: strip `document.pages[*].image.content` from raw responses before saving; keep page PNGs ≤ 3,500 px long side.
Required:
1. Discover via the API (`list=allpages` in the Page: namespace with `prop=proofread`/`pageprops`, or `list=categorymembers` of the proofread-level categories):
   Greek Wikisource: 20 works whose index points to a scan on Commons (DjVu/PDF) printed 1850–1935, with ≥ 15 pages at proofread level ≥ 3 ("proofread" or
   "validated"); Russian Wikisource: 10 works 1850–1935, ≥ 10 validated pages each. If the API is blocked by robots for a listing, fall back to the index pages'
   HTML already allowed, and say so in the report. Table docs/records/harvest/wikisource/SELECTION.md (work, index page, scan file, licence/PD statement, pages used).
2. For each chosen page: fetch the scan page image at the largest width Commons serves (≥ 2,000 px; `page<N>-<width>px-<file>.jpg` thumbnail endpoint for DjVu/PDF),
   convert to 200-dpi-equivalent grey PNG; fetch the proofread wikitext (`action=parse` / `prop=revisions`), strip templates/markup to plain lines (keep the
   line breaks of the transcription; record where hyphenation markers were joined). Frozen page gate as elsewhere (pages failing are still read but flagged).
   Target ≈ 300 Greek + 100 Russian pages.
3. Document AI page reads as T21 → docs/records/harvest/wikisource/records.jsonl (source "wikisource_el" | "wikisource_ru", licence = the work's PD/CC statement,
   source_url, read_batch "wikisource"). Align each Google line to the transcription lines (sequence alignment on NFC text, character-level similarity; one
   Google line ↔ one transcription line, else `unaligned`); record `human_label`, `docai_label`, `cer_docai_vs_human` per aligned line.
4. Admission (standard rules on the Google reading), classes, labels; split: all `test` except 3 Greek works + 1 Russian → `dev`; label_in_holdout check of
   ALL existing train pools against these labels (report, and list any collisions for removal from train); crops
   docs/records/harvest/harvest_big/wikisource/crops/<work8>/p<page6>-l<line4>.png; outputs docs/records/harvest/wikisource/{admitted.jsonl (with both labels), rejected.jsonl,
   admission_summary.json, holdout_books.json, READS.md}; compiled page images docs/records/harvest/harvest_big/wikisource/compiled/<lang>/<year>_<title40>/pNNNN.jpg.
5. READS.md: works/pages/lines, aligned share, Google-vs-human CER per language and per polytonic mark class (breathings, iota subscript, perispomeni, grave,
   dialytika) — this is the first independent measure of Google's label quality on our kind of print; reasons; cost. Tests (no network; wikitext stripping,
   alignment on fixtures). INVENTORY. `## Wave 7` in docs/records/harvest/collection/EXECUTION_STATE.md.
Last line exactly: `T27b: done | works: <el>/<ru> | pages: <el>/<ru> | lines: <n> | aligned: <n> | admitted: <n> | cer_el: <x.xx>% | cer_ru: <x.xx>% | usd: <x.xx> | tests: <n> passed`.
