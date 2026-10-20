# T24c — Wave 4 (third attempt: select directly from the pipeline metadata; no join) of the collection plan: Open Archives scanned documents (modern Greek) via the glossAPI link tables → Document AI page reads → admitted lines + crops (gpt-6.1-sol, xhigh)
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
COORDINATOR DECISION (15 Oct 08:25) replacing steps 1–2 of the earlier attempts: NO JOIN to external_pdfs is required. The pipeline metadata itself proves
the link worked: `pipeline_metadata.download_success == true` and `ocr_success == true`, and `source_metadata.pdf_links_json` IS the direct PDF URL. Verified count
with exactly these filters: 6,141 documents over 21 repositories (IKEE_AUT 1,950, ntua 1,133, Dione 954, hellanicus 455, Pandemos 411, elocus 265, estia 169,
edulll 116, helios 116, nemertes 107, dias 105, elstat 94, kallipos 78, KEIED 39, apothesis 38, anaktisis 37, ktisis 34, ekke 24, ariadne 13 …).
Required:
1. Pool = doc_metadata rows with download_success == true, ocr_success == true, filter == "ok", is_empty == false, percentage_greek ≥ 80, page_count 20–600,
   a pdf_links_json URL starting with http; mojibake/greek-badness nulls pass; measured greek_badness_score ≤ its measured median. Repository = source_metadata
   .collection_slug. external_pdfs.parquet is used ONLY to record the earlier status_code when the URL matches (informational). Keep the 7,341 wave-5 candidates file as is.
2. Selection: 130 documents (seed 20264) with a per-repository cap of 10; if the cap cannot fill 130, raise it to 20, then 30, and report the cap used; stratify by type
   and by decade where known; over-draw by one third (173) and take the first 130 that download. Dead links are replaced from the over-draw, never retried more than twice.
   Table docs/records/harvest/openarchives/SELECTION.md (overwrite the blocked versions; keep their preflight folders).
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
Last line exactly: `T24c: done | docs: <downloaded>/<tried> | pages: <rendered>/<accepted>/<read> | lines: <n> | admitted: <n> | mono: <n> | cs: <n> | train: <n> | dev: <n> | test: <n> | usd: <x.xx> | tests: <n> passed`.
