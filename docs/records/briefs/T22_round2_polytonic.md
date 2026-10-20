# T22 — Wave 2 of the collection plan: polytonic round 2 — 50 NEW Anemi books, 650 pages, fetched, gated, read with Document AI, admitted, cropped (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for Anemi (ANEMI_USER/ANEMI_PASS in env only; never in files/argv/logs) and Google Document AI (ADC).
No Vision. No `.git` writes. Google cost cap USD 1.50 (ledger docs/records/harvest/harvest_big/round2/google/budget.jsonl, at-most-once per page sha).
Read docs/records/harvest/COLLECTION_PLAN_v1.md, docs/records/briefs/T16_round1_select_fetch.md (fetcher usage, page positions, gate), T20 (admission module, reuse unchanged), T21 (read + outputs pattern).
No owner look in this run (owner, 15 Oct): gate-accepted pages are read; bad pages are filtered after the read (bad_page rule) and shown in compiled images.
Inputs: Anemi catalogue ~/Projects/greek-page-ocr/docs/evidence/o4c/anemi.jsonl (7,841 records; 6,531 with download_url); EXCLUDE every book in
docs/records/harvest/round1/selection.json (the 150 round-1 books) and the 57 early-print books of waves 1–2 (anemi.jsonl rows already fetched, see T16); fetcher
~/Projects/greek-page-ocr/scripts/fetch/o4b_anemi_pages.py (polite rate state; resumable receipts).
Required:
1. Selection: 50 books, years 1860–1935, Greek (title/language fields; skip titles that are plainly French/German/Italian/English or dictionaries/grammars —
   those are wave 5), monographs with a listed PDF and pages ≥ 60; stratified: 6–7 books per decade 1860s–1930s (8 decades); seeded draw (seed 20262); prefer
   publishers/places not dominant in round 1 (count round-1 places from selection.json titles where present; report). Table in docs/records/harvest/round2/SELECTION.md.
2. Pages: 13 per book spread 8–95 % with seeded 0–2 offsets; fetch single pages with the existing fetcher to docs/records/harvest/harvest_big/round2/records/…, render
   200 dpi grey PNG; frozen page gate + photometric guards; failed page → next neighbour, ≤ 2 tries; record replacements. Target 650 accepted pages.
3. Document AI page reads as T21 → docs/records/harvest/round2/records.jsonl (source "anemi_round2", licence "anemi-research-internal", read_batch "round2").
4. Admission (greekocr.harvest.admission), classes, labels; hold-out 8 of the 50 books (seed 20261015; 6 test / 2 dev); label_in_holdout against ALL existing
   hold-outs (round 1 + Vouli); crops to docs/records/harvest/harvest_big/round2/crops/<id6>/p<page6>-l<line4>.png; outputs docs/records/harvest/round2/{admitted.jsonl,
   rejected.jsonl, admission_summary.json, holdout_books.json, READS.md}; compiled page images docs/records/harvest/harvest_big/round2/compiled/<decade>s/<year>_<title40>_<id6>/pNNNN.jpg;
   contact sheets docs/records/harvest/harvest_big/round2/admission_sheet/<class>.jpg.
5. READS.md tables (books, pages fetched/accepted/read, lines, admitted per class × split, reasons, cost, fetch failures), tests (selection exclusions,
   stratification, no re-reads), INVENTORY, `## Wave 2` in docs/records/harvest/collection/EXECUTION_STATE.md.
Last line exactly: `T22: done | books: <n> | pages: <fetched>/<accepted>/<read> | lines: <n> | admitted: <n> | poly: <n> | train: <n> | dev: <n> | test: <n> | usd: <x.xx> | tests: <n> passed`.
