# T24b — Wave 4 (rerun after the T24 block) of the collection plan: Open Archives scanned documents (modern Greek) via the glossAPI link tables → Document AI page reads → admitted lines + crops (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for the Greek repository hosts (direct bitstream links; polite ≥1 s between requests per host) and Google
Document AI (ADC). No Vision. No `.git` writes. Google cost cap USD 3.00 (ledger docs/records/harvest/harvest_big/openarchives/google/budget.jsonl, at-most-once per page sha).
Read docs/records/harvest/COLLECTION_PLAN_v1.md (wave 4), T20 (admission module — reuse unchanged), T21/T23 (read + outputs pattern), and docs/records/harvest/openarchives/READS.md
(the T24 attempt: it built the join + pool code in greekocr/harvest/openarchives.py and scripts/harvest/openarchives.py, saved 7,341 wave-5 candidates, and stopped
because ALL scanned documents carry a null mojibake score). REUSE that code; change only what this brief changes.
FILTER FIX (coordinator, 15 Oct): a null mojibake_badness_score PASSES (the score is computed on text layers only; scanned documents never have one); likewise a null
greek_badness_score passes; the greek_badness_score ≤ pool-median rule applies only to documents that have a value. Expected pool ≈ 6,000 documents.
DISK DISCIPLINE (the Mac has ~20 GB free): render sampled pages with the long side capped at 3,500 px (record the scale factor and the native page size; bboxes
stay in the rendered frame), PNG compress level 6; strip `document.pages[*].image.content` from every raw Document AI response before saving it (keep a
`content_stripped` note; the page PNG is the image of record); delete each PDF right after its pages are rendered; never keep more than one PDF on disk at a time;
abort gracefully with a report if free space drops below 4 GB (`shutil.disk_usage`).
Inputs (docs/records/harvest/harvest_big/openarchives/): external_pdfs.parquet (561,271 rows: collection_slug, edm_url, external_link, type, language_code, status_code,
pdf_links_json = direct PDF URLs), all_links.parquet, collections_links_summary.parquet, and doc_metadata.jsonl (one row per processed document:
pipeline_metadata {ocr_success, needs_ocr, filter, percentage_greek, greek_badness_score, mojibake_badness_score, latin_percentage, polytonic_ratio, page_count,
is_empty, char_count_no_comments …} and source_metadata {filename, collection_slug, type, pdf_links_json, metadata_json (title/creator/date), language_code}).
If doc_metadata.jsonl is still being written (a `.partial` file exists instead), wait for it (poll every 2 min) — do not start without it.
Required:
1. Join doc_metadata rows to external_pdfs by (collection_slug, pdf_links_json URL) or edm_url; report join coverage. Candidate pool = documents with
   pipeline_metadata.ocr_success == true (the pipeline had to OCR them → scanned), filter == "ok", is_empty == false, percentage_greek ≥ 80,
   mojibake_badness_score == 0, greek_badness_score ≤ the pool's median, page_count 20–600, and an external_pdfs row with status_code 200. Document year from
   metadata_json date fields (report the share with a year). Write docs/records/harvest/openarchives/wave5_candidates.json = scanned docs with latin_percentage 20–50 (for T25).
2. Selection: 130 documents (seed 20264) stratified by repository (≤ 10 per collection_slug), type (thesis / article / book / other) and decade where known
   (1980s … 2010s), over-drawn by one third (173) because links die; take the first 130 that download. Table docs/records/harvest/openarchives/SELECTION.md.
3. Per document: stream-download the PDF (skip > 200 MB → next candidate), pick 12 pages spread 8–95 % (seeded 0–2 offsets), render 200 dpi grey PNG, frozen
   page gate + photometric guards (failed page → neighbour, ≤ 2 tries), then delete the PDF (keep sha256/size/pages in the receipt). Target ≈ 1,500 accepted pages.
4. Document AI page reads as T21 → docs/records/harvest/openarchives/records.jsonl (source "openarchives_<collection_slug>", licence "per-repository (recorded, unverified)",
   source_url = external_link, read_batch "openarchives").
5. Admission (greekocr.harvest.admission), classes, labels; hold-out 20 of the 130 documents (seed 20261015; 15 test / 5 dev) stratified by repository;
   label_in_holdout against all existing hold-outs; crops docs/records/harvest/harvest_big/openarchives/crops/<doc8>/p<page6>-l<line4>.png; outputs
   docs/records/harvest/openarchives/{admitted.jsonl, rejected.jsonl, admission_summary.json, holdout_books.json, READS.md}; compiled page images
   docs/records/harvest/harvest_big/openarchives/compiled/<collection_slug>/<year>_<title40>_<doc6>/pNNNN.jpg; contact sheets docs/records/harvest/harvest_big/openarchives/admission_sheet/<class>.jpg.
6. READS.md: pool sizes at each filter, join coverage, documents tried/downloaded/dead-link/skipped-size, pages rendered/accepted/read, lines, admitted per
   class × split × repository, reasons, cost. Tests (no network; small parquet/jsonl fixtures) for the join, filters, stratified draw, hold-out. INVENTORY.
   `## Wave 4` in docs/records/harvest/collection/EXECUTION_STATE.md.
Last line exactly: `T24b: done | docs: <downloaded>/<tried> | pages: <rendered>/<accepted>/<read> | lines: <n> | admitted: <n> | mono: <n> | cs: <n> | train: <n> | dev: <n> | test: <n> | usd: <x.xx> | tests: <n> passed`.
