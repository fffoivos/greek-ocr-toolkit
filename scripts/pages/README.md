# Page verification

The supported processing entry points are `greekocr.pages.process_page`,
`process_book`, and `greekocr pages`. These scripts compare implementations;
they are not alternate page detectors.

- `check_stage_equivalence.py` compares the relocated stages to Q2 commit
  `10eda96`, expanding named constants. It returns a nonzero status on a mismatch.
- `check_q3_equality.py` runs Q2 and the new API independently on the 54 page and
  41 book fixtures. It checks both default and table modes, exact JSON values,
  glyph Parquet rows, delivered crop pixels, and Q1 join outcomes. `--resume`
  reuses completed per-page receipts; use a fresh `--out` after algorithm changes.
- `check_q3_books.py` finishes book/corpus checks using the paired measurements
  from that run, including the separate 41-page book cohort.

- `write_q3_receipt.py` bundles the completed page/book comparisons, final test
  receipt, source identities and every observed difference into the Q3 review.

Run with the Python environment and offline flags in `.astra/QUEUE_COMMON.md`.
The page and book runners write detailed JSON receipts under `.astra/q3-equality`.
Both equality runners return nonzero if either comparison fails. Inspect
`runtime_equal` and `frozen_equal`, and retain every difference file. Historical artifact fields
count as differences; these scripts do not filter them out.
