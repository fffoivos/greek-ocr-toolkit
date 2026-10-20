# SS2 — Where small segments come from: source, wave, class, book, page (read-only analysis)

You are Sol, executing for the small-segment analysis lead. Read-only, descriptive analysis: a script, tests, tables and a receipt.
No judgement or recommendation.

Worktree: `~/Projects/greek-ocr-toolkit-sol-recut` (branch `sol/recut-v1`). `B = docs/records/harvest/collect_v3_admission/segeval1`.
Python: `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Network off.

## Hard constraints
- Write ONLY under `B/small_segments/q2/`, `B/small_segments/tools/` (new file `ss2_q2.py`; do NOT edit `ss1_q1.py` or any other
  existing file) and `B/small_segments/tests/` (new file `test_ss2_q2.py`). Change nothing else; no git add/commit.
- Input: `B/cells/population_cells.jsonl.gz` (592,466 rows; stop if the count differs). Reuse — by import — the SS1 functions in
  `B/small_segments/tools/` for rotation (`L`, `S`, `A`), output type (numeric / mixed / nonnumeric) and `chars`, so both briefs
  share one definition. Read `B/small_segments/q1/SS1_RECEIPT.json` and record the SS1 script sha256 you imported.

## Definitions of "small" (evaluate every table for EACH of these; names are fixed)
- `D_rec` (the lead's recommendation): `chars ≤ 8 and A ≤ 6`.
- `D_alt5`: `chars ≤ 5 and A ≤ 4`.
- `D_cells`: `S ≤ 40 and L ≤ 200 and chars ≤ 10` (SS1 candidate C5).

Also, **T4 extension** (one extra table `G0`, same columns as SS1's T4, computed by importing SS1's T4 function rather than
re-implementing it): candidates `chars ≤ 10 and A ≤ 6`, `chars ≤ 10 and A ≤ 8`, `chars ≤ 12 and A ≤ 8`, `chars ≤ 8 and A ≤ 5`,
`chars ≤ 8 and A ≤ 8`, `chars ≤ 6 and A ≤ 5`, using the same owner inputs as SS1 (list them with sha256). If SS1's T4 code is not
importable as a function, copy it into `ss2_q2.py` verbatim, say so, and show on the existing SS1 candidate `C7_chars_le_8_A_le_6`
that your copy reproduces SS1's numbers exactly.

## Book and page ids
- Book = `row_id` prefix before `--s` (e.g. `gazette_modern--aeb6eb76fc7057f0`); page = book + the `sNNN` part. For row ids without
  `--s` (collection-v2 style, e.g. `129cff40-p000009-l0107`), book = prefix before `-p<digits>-l<digits>`, page = through
  `p<digits>`. Any other shape: book = whole id minus a trailing `-l<digits>` / `--l<digits>` if present, and count those rows.
  Report how many rows each rule covered, with 3 examples per rule.

## Tables (`q2/Q2_TABLES.md` + `q2/q2.json`), per definition
- **G1** by `source`, by `wave`, by `primary_class`, by `script_class`: rows in group, small rows, % of all small, density
  (small / rows in group), split numeric / mixed / nonnumeric. Sorted by small rows desc; all groups printed.
- **G2** concentration: number of books with ≥1 small row; how many books (sorted by small count desc) hold 50%, 80%, 95% of the
  small rows; the same three numbers for ALL rows (baseline, books sorted by row count) and for nonnumeric-small rows alone.
  Also the share of small rows held by the top 1, 5, 10, 20, 50, 100 books.
- **G3** top 40 books by small count: book, source, wave, primary_class, rows, small rows, density, numeric/mixed/nonnumeric
  small, pages, pages with ≥1 small row. Top 40 by density among books with ≥50 rows (same columns). Density histogram over books
  with ≥50 rows (buckets 0, (0–1%], 1–5, 5–10, 10–25, 25–50, 50–75, 75–100%).
- **G4** the same top-40-by-count and concentration numbers for nonnumeric-small (incl. mixed) rows only.
- **G5** pages: for each page, rows, small rows, numeric rows. Distribution of small rows by the page's small share (buckets 0–10,
  10–25, 25–50, 50–75, 75–90, 90–100%) and by the page's numeric share (same buckets); the share of small rows on "table-like"
  pages, with two proxies reported separately: (a) numeric rows ≥ 50% of the page, (b) small rows ≥ 50% of the page. Split by
  output type of the small row. Also: pages with exactly 1 small row (isolated small rows) — count and output-type split.
- **G6** cross-tab source × output type of small rows (counts), and source × wave.

## Tests (`tests/test_ss2_q2.py`, pytest with the venv python)
Synthetic rows covering: the three book-id rules (+ one odd id), page grouping, the 50/80/95% concentration count on a tiny
hand-computable case (with ties), density with a book of < 50 rows excluded from the density ranking, the two table-page proxies.

## Receipt and report
- `q2/SS2_RECEIPT.json`: input sha256 + row count, owner input sha256s (G0), imported SS1 script sha256, outputs with sha256, script sha256, test result,
  versions.
- Final message: per definition, small rows total, top 3 sources with their share, the 50/80/95% book counts vs the all-rows
  baseline, the % on table-like pages (both proxies), and any anomaly.
- Last line exactly: `SS2 READY: q2/Q2_TABLES.md, q2/q2.json, receipt q2/SS2_RECEIPT.json` (or `SS2 FAILED: <reason>`).
