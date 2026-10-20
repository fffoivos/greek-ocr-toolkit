# T21 — Wave 1 of the collection plan: Vouli parliament volumes (1850s) → Document AI page reads → admitted lines + crops (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for Google Document AI only (ADC; same processor/bindings as T19). No Vision. No `.git` writes.
Cost cap USD 2.50 (budget ledger as T19: docs/records/harvest/harvest_big/vouli/google/budget.jsonl, at-most-once per page image sha).
Read docs/records/harvest/COLLECTION_PLAN_v1.md §1, §4 and docs/records/briefs/T20_line_admission_crops.md (its module greekocr/harvest/admission.py is the admission step —
reuse it unchanged; if it is missing or its tests fail, stop and report).
Input: 107 PDFs in docs/records/harvest/harvest_big/vouli/pdf/<sha256>.pdf with metadata docs/records/harvest/harvest_big/vouli/sources.json (licence CC-BY-4.0, source_url,
attribution per book). Hellenic Parliament proceedings 1850s, polytonic, one printer.
Required:
1. Render EVERY page of every PDF at 200 dpi grey PNG (pypdfium2, same renderer as round 1) to docs/records/harvest/harvest_big/vouli/images/<sha12>-<page6>.png.
   Expected ≈ 1,126 pages. Record page count per book.
2. Page gate: the frozen round-1 page gate + photometric guards (greekocr/harvest/round1.py / scripts/harvest/round1.py; same limits as
   docs/records/harvest/round1/SELECTION.md) → accepted / rejected per page with flags. No owner look in this run (owner, 15 Oct): all gate-accepted pages are read.
   Two-page spreads are accepted (DocAI reads both halves).
3. Read every accepted page with Document AI exactly as T19 (line layouts, native bboxes, inverse transforms, per-line mean/min confidence, flags short_line /
   tall_box / low_confidence). Raw responses under docs/records/harvest/harvest_big/vouli/google/docai/. Records docs/records/harvest/vouli/records.jsonl with the round-1
   schema plus source "vouli_parliament_1850s", licence "CC-BY-4.0", source_url, attribution, read_batch "vouli".
4. Admission with greekocr.harvest.admission (all rules incl. bad_page), script classes, labels. Hold-out: 15 % of the books (seed 20261015; 16 of 107) →
   split test (12) / dev (4), rest train; label_in_holdout rule against the round-1 hold-out labels AND this wave's. Crops as T20 (trim rule, padding) to
   docs/records/harvest/harvest_big/vouli/crops/<sha12>/p<page6>-l<line4>.png. Outputs docs/records/harvest/vouli/{admitted.jsonl, rejected.jsonl, admission_summary.json,
   holdout_books.json, READS.md}.
5. Compiled page images in the owner-approved format (scripts/harvest/compile_page_reads.py) for every read page →
   docs/records/harvest/harvest_big/vouli/compiled/<year>_<session-title40>_<sha6>/pNNNN.jpg; contact sheets per class (60 random admitted crops + labels) →
   docs/records/harvest/harvest_big/vouli/admission_sheet/<class>.jpg.
6. READS.md: pages rendered / gated / read, lines, admitted per class × split, reasons table, cost, per-source cap check (Vouli must stay ≤ 40 % of the
   polytonic train pool when combined with round 1 — report the share), failures. Tests (no network) for the gate wiring, scope (no page read twice), hold-out.
   INVENTORY. Append `## Wave 1` to docs/records/harvest/collection/EXECUTION_STATE.md with the counts.
Last line exactly: `T21: done | pages: <rendered>/<accepted>/<read> | lines: <n> | admitted: <n> | poly: <n> | train: <n> | dev: <n> | test: <n> | usd: <x.xx> | tests: <n> passed`.
