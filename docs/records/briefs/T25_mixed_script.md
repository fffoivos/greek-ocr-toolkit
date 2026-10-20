# T25 — Wave 5 of the collection plan: Greek-with-Latin (code-switch) and Latin-only lines from dictionaries, grammars, journals, bibliographies → Document AI → admitted lines + crops (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for Anemi (ANEMI_USER/ANEMI_PASS in env only; never in files/argv/logs), Greek repository hosts (direct
links), archive.org, and Google Document AI (ADC). No Vision. No `.git` writes. Google cost cap USD 2.00 (ledger docs/records/harvest/harvest_big/mixed/google/budget.jsonl).
Read docs/records/harvest/COLLECTION_PLAN_v1.md (wave 5), T20 (admission module — reuse unchanged; majority-Latin lines are class `latin`, Greek-majority lines with a whole
Latin word are `greek_latin_cs`), T22 (Anemi fetch pattern), T24 (repository download pattern).
Sources, three parts (target ≈ 1,000 accepted pages):
 A. Anemi, 40 books 1860–1935 (seed 20265), excluding every book already used (docs/records/harvest/round1/selection.json, docs/records/harvest/round2/SELECTION.md): titles
    matching λεξικ|γραμματικ|περιοδικ|επετηρ|δελτίον|Γαλλ|Αγγλ|Γερμ|Ιταλ|Λατιν|διάλογ|μέθοδος (case/accent-insensitive) in
    ~/Projects/greek-page-ocr/docs/evidence/o4c/anemi.jsonl; 12 pages each spread 8–95 % → fetch single pages with the existing fetcher, 200 dpi grey.
 B. Open Archives: docs/records/harvest/openarchives/wave5_candidates.json (scanned documents with latin_percentage 20–50 from T24); 40 documents (≤ 5 per repository),
    10 pages each: 7 from the last 12 % of the document (bibliography/footnotes) + 3 from the middle; direct bitstream download, delete PDF after rendering.
 C. Internet Archive item b28038630 (A Greek-English lexicon, 1883, public domain, 1,806 pages; media URL via archive.org/download/<id>/): 100 pages spread 8–95 %.
Required:
1. Fetch + frozen page gate + photometric guards for all three parts (two-column dictionary pages are expected: the gate's two-column handling applies; reject
   more_than_two_columns). Record replacements and failures. Table docs/records/harvest/mixed/SELECTION.md.
2. Document AI page reads as T21 → docs/records/harvest/mixed/records.jsonl (source "anemi_mixed" | "openarchives_mixed_<slug>" | "archive_b28038630"; licences
   "anemi-research-internal" | "per-repository (recorded, unverified)" | "public-domain"; read_batch "mixed").
3. Admission, classes, labels; hold-out 15 % of sources per part (seed 20261015; test/dev 3:1); label_in_holdout against all existing hold-outs; crops
   docs/records/harvest/harvest_big/mixed/crops/<src8>/p<page6>-l<line4>.png; outputs docs/records/harvest/mixed/{admitted.jsonl, rejected.jsonl, admission_summary.json,
   holdout_books.json, READS.md}; compiled page images docs/records/harvest/harvest_big/mixed/compiled/<part>/<year>_<title40>_<id6>/pNNNN.jpg; contact sheets
   docs/records/harvest/harvest_big/mixed/admission_sheet/<class>.jpg.
4. READS.md: per part sources/pages/lines; admitted per class (the point of this wave: greek_latin_cs and latin counts) × split; mixed-line share per page
   distribution; reasons; cost. Tests (no network) for title filters, exclusions, page picks (last-12 % rule), hold-out. INVENTORY. `## Wave 5` in
   docs/records/harvest/collection/EXECUTION_STATE.md.
Last line exactly: `T25: done | sources: <A>/<B>/<C> | pages: <rendered>/<accepted>/<read> | lines: <n> | admitted: <n> | cs: <n> | latin: <n> | poly: <n> | mono: <n> | usd: <x.xx> | tests: <n> passed`.
