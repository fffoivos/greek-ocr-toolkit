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

Q3b's strict behaviour gate is `check_q3b_equality.py`, followed by
`check_q3b_books.py --out .astra/q3b-equality` and `write_q3b_receipt.py`.
The final receipt requires complete page/file coverage, source identity and the
full test receipt; it retains every non-allowlisted failure. The gate uses only the field-by-field
metadata allowlist documented in `docs/PAGES_OUTPUT_FORMAT.md`; every other
difference fails. The historical Q3 scripts above retain their original rules.

The Q3b runner calls the public API 16 times per page (table recovery on/off,
statistics on/off, joining off/default/rows/pieces). Within that page only,
deterministic detector/delivery/statistics stages cache their complete serialized
inputs and return independent copies. All cache misses execute the current code;
no frozen data or prior run supplies a stage output. Independent committed Q2
stages provide numeric/crop references, and an independent Q1b row audit provides
the partial delivery reference. Frozen Q1b envelopes are also compared directly.
`--workers N` runs a foreground process pool. `--resume` requires identical source
hashes and image hashes; choose a fresh directory after source changes.
