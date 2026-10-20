# T17 — Round-1 page reads, decades 1860–1880 (owner-approved pages): Document AI + Vision on each accepted page, page-mode harvest (lines + labels), owner review (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Google Vision + Document AI; ADC). No `.git` writes. Cost cap USD 2.00.
Scope: ONLY the accepted round-1 pages (docs/records/harvest/round1/manifest.json, harvest_accepted=true) of books with decade 1860, 1870 or 1880 (selection.json) — the owner
looked at these three decades in Finder and approved them (14 Oct). Decades 1890–1930 are NOT read in this task.
Method (established by T15, docs/records/harvest/PAGE_READS_v1.md, and the owner's verdict that DocAI's page line boxes are "clearly better"):
1. Read every in-scope page whole with both readers, one call per page per reader, T14/T15 cache + budget discipline (reservations, raw responses under
   docs/records/harvest/harvest_big/round1/google/, at-most-once, no retries of ambiguous failures). Same reader bindings as T15.
2. Line set = Document AI's line layouts on the native rendered page (the manifest's 200 dpi grayscale PNG; map through any DocAI image transform as T15 did).
   Vision lines (symbol-break unions) are attached to DocAI lines by box overlap (T15 rule) with a text-alignment fallback when boxes are ambiguous; record which.
3. Labels per DocAI line, the pilot rule: tier 1 = exact NFD agreement; tier 2 = letters+marks agree after the T14b unification → label = DocAI's reading
   ("letters agree → DocAI's marks"); tier 3 = disagree (kept, unlabelled); list-return/side-by-side handling per the pilot rule. Also keep DocAI symbol confidence
   per line. Drop lines shorter than 3 letters from the harvest counts but keep them in the records.
4. Output docs/records/harvest/round1/reads_d1/: records.jsonl (one row per DocAI line: page, book, decade, bbox on the native page, DocAI text, Vision text, tier, label,
   confidence, flags), per-page assignment files, summary.json (per decade and per book: pages, lines, tier1/2/3 counts, label yield, mean confidence), receipt.json.
   Line crops are NOT cut in this task (the page PNGs + bboxes are enough; cutting is a later, reviewed step).
5. Owner review, two forms: (a) docs/records/harvest/round1/reads_d1/review_<decade>.html — for EACH book one page (the median-yield page) shown exactly like the
   approved T15 side-by-side view: page image with numbered green DocAI boxes on the left, the numbered lines on the right with tier colour (green tier 1, amber
   tier 2 with the Vision reading folded, red tier 3 with both readings); self-contained, downscaled images; (b) a Finder folder
   docs/records/harvest/harvest_big/round1/reads_d1_look/<decade>/<year>_<title>_<id>/pNNNN.png with the numbered DocAI boxes drawn on every page and a pNNNN.txt next to
   it with the numbered lines and tiers.
6. Report docs/records/harvest/round1/READS_D1.md: counts, yield table, cost receipt, failure examples (lost pages, empty reads, transform cases). Tests (no network) for
   the tiering, Vision attachment and the review builders. INVENTORY.
Last line exactly: `T17: done | pages: <n> | lines: <n> | tier1: <n> | tier2: <n> | tier3: <n> | label_yield: <pct> | calls: <n> | usd: <x.xx> | tests: <n> passed`.
