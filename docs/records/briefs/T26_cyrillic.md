# T26 — Wave 6 of the collection plan: Cyrillic scans from the Internet Archive → Document AI page reads → admitted lines + crops (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for archive.org and Google Document AI (ADC). No Vision. No `.git` writes.
Google cost cap USD 1.20 (ledger docs/records/harvest/harvest_big/cyrillic/google/budget.jsonl, at-most-once per page sha).
Read docs/records/harvest/COLLECTION_PLAN_v1.md (wave 6), T20 (admission module — reuse unchanged; class `cyrillic` = Cyrillic-majority line; a word mixing Cyrillic with
Latin/Greek letters drops the line), T21 (read + outputs pattern).
Owner cannot read Cyrillic (15 Oct): quality rests on automatic checks — add a page rule: a read page whose letters are < 70 % Cyrillic is dropped (`not_cyrillic_page`).
Inputs: ~/Projects/greek-page-ocr/docs/evidence/o4c/candidates.jsonl rows with source "archive" and estimated_cyrillic_lines > 0 (13 items: Russian, Bulgarian,
Serbian; public-domain or CC-BY; print_review verified-target-sample; media_probes.jsonl has the resolved PDF/DjVu URLs). Scanned books only — the Tolstoy CC0
uploads are digital editions and are already excluded.
Required:
1. For each of the 13 items: download the PDF (archive.org/download/<identifier>/<file>; if only DjVu exists, use the IA single-page JP2/JPEG endpoints) — skip
   > 300 MB items (download the "_text.pdf" or page images instead); pick 45 pages spread 8–95 % (seeded 0–2 offsets; seed 20266); render 200 dpi grey; frozen page
   gate + photometric guards (dictionary two-column pages expected; reject more_than_two_columns); failed → neighbour ≤ 2 tries. Target ≈ 550 accepted pages.
2. Document AI page reads as T21 (language hints: none — DocAI auto-detects; record the detected language per page) → docs/records/harvest/cyrillic/records.jsonl
   (source "archive_<identifier>", licence from the candidate row, source_url, read_batch "cyrillic").
3. Admission + the not_cyrillic_page rule; classes; labels; hold-out 2 of the 13 items (seed 20261015; test) + 1 (dev); crops
   docs/records/harvest/harvest_big/cyrillic/crops/<id8>/p<page6>-l<line4>.png; outputs docs/records/harvest/cyrillic/{admitted.jsonl, rejected.jsonl, admission_summary.json,
   holdout_books.json, READS.md}; compiled page images docs/records/harvest/harvest_big/cyrillic/compiled/<year>_<title40>_<id6>/pNNNN.jpg; contact sheet
   docs/records/harvest/harvest_big/cyrillic/admission_sheet/cyrillic.jpg (60 random crops + labels).
4. READS.md: items/pages/lines, admitted per class × split × item, detected languages, Cyrillic-share distribution per page, reasons, cost. Tests (no network).
   INVENTORY. `## Wave 6` in docs/records/harvest/collection/EXECUTION_STATE.md.
Last line exactly: `T26: done | items: <n> | pages: <rendered>/<accepted>/<read> | lines: <n> | admitted: <n> | cyr: <n> | latin: <n> | train: <n> | dev: <n> | test: <n> | usd: <x.xx> | tests: <n> passed`.
