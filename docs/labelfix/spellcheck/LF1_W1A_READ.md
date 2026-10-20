# LF1 production read, batch W1a (20 Oct 2026, 05:54–06:00 Athens)

Coordinator GO. 12 contexts (`artifacts/lf1/candidate_contexts_w1a.json`), 576 bed + 72 frozen controls; `RUN_ALL.sh --jobs 12`; scanner v4.5.5.

- Contexts: 12/12 VALID. 2 first attempts VOID (w1a_00003, w1a_00005: scanner "unsupported view loop", i.e. the reader opened images in a
  JS `for…of` loop the scanner cannot replay); both VALID on their one fresh re-read.
- Controls: 72/72 correct (verdict match and expected reasons contained).
- Bed: 544 OK, 13 CROP_VIOLATES (text_ne_visible_line 13, turned_or_clipped 8), 19 TEXT_DIFFERS: 32/576 flagged (5.6%).
  In-quota 25/478, reserve 7/98.
- Flags by class (test+dev): caps_headings 0/80, curved_skewed 1/5, degraded 3/17, font_extremes 2/19, greek_latin 1/5,
  leaders_dashes 1/32, long 5/46, modern_cyrillic 1/8, monotonic 4/107, numeric_cells 1/7, poly_dictionary_journal 6/68,
  polytonic 5/170, short 2/12.
- Tokens: 5,969,369 over 14 attempts (88% cached), 0.92M per 100 cards. Codex weekly 41% → 42% (host probes).

Verdicts: `artifacts/lf1/verdicts.jsonl` (W1a rows), ledger `artifacts/lf1/ledger.json`. Finalize waits for batch 2 (PROD_PLAN: merge,
map, finalize once against candidates_v3).
