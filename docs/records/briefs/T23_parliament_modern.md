# T23 — Wave 3 of the collection plan: Hellenic Parliament proceedings 1975–2000 (scanned modern Greek) → Document AI page reads → admitted lines + crops (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for digitallibrary.parliament.gr (DSpace 7 REST API, public, polite: ≥2 s between requests) and Google
Document AI (ADC). No Vision. No `.git` writes. Google cost cap USD 2.50 (ledger docs/records/harvest/harvest_big/parliament/google/budget.jsonl, at-most-once per page sha).
Read docs/records/harvest/COLLECTION_PLAN_v1.md (wave 3), T20 (admission module — reuse unchanged), T21 (read + outputs pattern).
Inputs: docs/records/harvest/harvest_big/parliament/parliament_catalogue.jsonl (76,246 catalogue rows: document_id = DSpace item UUID, title, year, collection, rights raw,
metadata_url); docs/records/harvest/harvest_big/parliament/o4c_discover_parliament.py + o4c_common.py show how the earlier crawl resolved item → bundles → bitstreams
(`/core/items/<uuid>/bundles`, `/core/bundles/<uuid>/bitstreams`, ORIGINAL bundle PDF). Reuse that resolution logic (copy what you need into greekocr/harvest/).
Required:
1. Selection: collection "ΠΡΑΚΤΙΚΑ ΒΟΥΛΗΣ", year 1975–2000, rights raw containing "CC BY 4.0" only (NC-ND rows are OUT), 4 volumes per year (seed 20263; 104
   volumes), spreading sessions across the year. Table docs/records/harvest/parliament/SELECTION.md (year, title, uuid, rights, bitstream size).
2. For each volume: resolve the ORIGINAL PDF bitstream; skip volumes whose PDF is > 250 MB (pick the next candidate of that year); stream-download to
   docs/records/harvest/harvest_big/parliament/pdf/<uuid>.pdf; pick 12 pages spread 8–95 % with seeded 0–2 offsets; render those pages at 200 dpi grey PNG; run the frozen
   page gate + photometric guards; failed page → next neighbour, ≤ 2 tries; THEN delete the PDF (keep sha256, size, page count in the receipt) to bound disk.
   Target ≈ 1,200 accepted pages. These are typewriter/phototypeset proceedings, often two columns: the gate's two-column handling applies; more_than_two_columns pages are rejected.
3. Document AI page reads as T21 → docs/records/harvest/parliament/records.jsonl (source "parliament_proceedings_1975_2000", licence "CC-BY-4.0", source_url =
   https://hdl.handle.net/… from the catalogue record_url, attribution "Hellenic Parliament Library; <title>", read_batch "parliament_modern").
   Tag each page's era: 1975–1981 lines may be polytonic (script class decides), 1982+ monotonic.
4. Admission (greekocr.harvest.admission), classes, labels; hold-out 16 of the 104 volumes (seed 20261015; 12 test / 4 dev) stratified by year; label_in_holdout
   against all existing hold-outs (round 1, Vouli, round 2 if present); crops docs/records/harvest/harvest_big/parliament/crops/<uuid8>/p<page6>-l<line4>.png;
   outputs docs/records/harvest/parliament/{admitted.jsonl, rejected.jsonl, admission_summary.json, holdout_books.json, READS.md}; compiled page images
   docs/records/harvest/harvest_big/parliament/compiled/<year>/<year>_<title40>_<uuid6>/pNNNN.jpg; contact sheets docs/records/harvest/harvest_big/parliament/admission_sheet/<class>.jpg.
5. READS.md: volumes selected/resolved/downloaded/skipped(size)/failed, pages rendered/accepted/read, lines, admitted per class × split × era, reasons, cost,
   API politeness receipt (request count, min gap). Tests (no network) for selection filters, bitstream resolution parsing (fixtures), page spread, hold-out.
   INVENTORY. `## Wave 3` in docs/records/harvest/collection/EXECUTION_STATE.md.
Last line exactly: `T23: done | volumes: <n> | pages: <rendered>/<accepted>/<read> | lines: <n> | admitted: <n> | mono: <n> | poly: <n> | train: <n> | dev: <n> | test: <n> | usd: <x.xx> | tests: <n> passed`.
