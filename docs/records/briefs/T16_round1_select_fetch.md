# T16 — Harvest round 1: pick books and pages (≈2,000 Anemi pages), fetch them, gate out bad scans and strange type, build the owner's look page. NO Google calls. (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON for Anemi only (ANEMI_USER/ANEMI_PASS in env; never write them to files, argv or logs). No `.git` writes.
No Vision/DocAI/Transkribus calls in this task: the owner looks at the picked pages first.
Owner (14 Oct): "ok, we just need to avoid very strange characters or bad scans". Page-level Document AI reads are now the harvest route (docs/records/harvest/PAGE_READS_v1.md):
one call per page gives the line set and the text, so the budget is pages, not lines. Round 1 = about 2,000 pages, ~13 per book, from the 150 wave-3 books.
Inputs: ~/Projects/greek-page-ocr/docs/evidence/o4c/anemi_wave3_proposal.json (150 books: document_id, year, pages, title); the pilot's per-book evidence
(docs/records/harvest/pilot_v1/*, page_reads_v1/comparisons.jsonl + assignments: both readers on 2 middle pages per book; pilot_t13c records with page_gate, features,
text_layer); fetcher ~/Projects/greek-page-ocr/scripts/fetch/o4b_anemi_pages.py (--records/--page-range as used by T13c; polite rate state; resumable receipts);
the 57 early-print books of waves 1–2 (docs/evidence/o4c/anemi.jsonl rows already fetched) are OUT of scope.
Required:
1. Book selection, written up in docs/records/harvest/round1/SELECTION.md with a per-book table (decade, title, pages, pilot signals, decision, reason):
   a. Strange type → OUT: books whose pilot pages show it. Signals, each computed from the pilot reads of that book's lines/pages: DocAI mean symbol confidence;
      letters-agree rate between the two readers; share of lines with Google's substitution fingerprints (Vision "καὶ" where DocAI has "κ"+mark or a lone "κ",
      "ου"/"8"/"ȣ" disagreements, final-sigma-in-mid-word, stigma/koppa-like confusions, Latin letters inside Greek words); a non-Greek or mixed-language text
      block share. Set the cut at the bottom quintile on confidence OR agreement, or any substitution fingerprint above 5% of lines; print the thresholds and
      the books they remove so the owner can see the borderline ones. Titles that are plainly liturgical/ecclesiastical/older-style editions get a flag column.
   b. Bad scans → OUT or REDUCED: from the pilot pages' features and page gate (darkest-percentile contrast, faintness proxy, ink fraction, skew/bend, show-through,
      gate flags). A book with both pilot pages failing → OUT; one failing → half allocation.
   c. Allocation: equal page budget per decade across the surviving books; ≈13 pages per book, up to 16 for books in thin decades, never more; total ≤ 2,000.
2. Page positions: spread evenly through each book between 8% and 95% of its page count, each nudged by a random offset of 0–2 pages (seeded), excluding the
   pilot's pages. For every fetched page run the EXISTING page gate (same code/revision as the pilot, record the sha); a page that fails (non-body, plate, table,
   title page, bad contrast/faint/skewed/show-through per the pilot's feature thresholds) is replaced by its next neighbour, at most two tries; record every
   replacement and failure reason.
3. Fetch with the existing fetcher: polite (its rate state), resumable, receipts with sha256, pages as single-page PDFs under
   docs/records/harvest/harvest_big/round1/records/<book>/<volume>/page-NNNNNN.pdf (ignored dir), rendered PNG at the pilot's 200 dpi grayscale for gating only.
   Report fetch throughput and total time; if the server throttles, slow down, never hammer.
4. Owner's look page docs/records/harvest/round1/look.html (self-contained, inlined downscaled images, ≤ 25 MB total; split into look_1.html… if larger): one row per
   book — title, decade, allocation, then thumbnails of all its accepted pages in book order (click = full-size page inline via <details>), with a red mark on
   any page that was a replacement; a final section "removed books" with one pilot page each and the reason. Order rows by decade then title.
5. Manifest docs/records/harvest/round1/manifest.json (every page: book, page number, pdf sha, gate result, replacement chain) and summary.json (pages per decade/book,
   failures by reason, fetch time). Tests (no network) for the allocation, position spreading, the strange-type signals and the replacement rule. INVENTORY.
Last line exactly: `T16: done | books_in: <n> | books_out_type: <n> | books_out_scan: <n> | pages_fetched: <n> | pages_accepted: <n> | replacements: <n> | fetch_minutes: <n> | tests: <n> passed`.
