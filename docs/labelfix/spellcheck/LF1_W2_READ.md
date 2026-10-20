# LF1 production read, batch W2 (20 Oct 2026, 06:07–06:16 Athens)

Coordinator GO. 25 contexts (`artifacts/lf1/candidate_contexts_w2.json`), 1,242 bed + 150 frozen controls; `RUN_ALL.sh --jobs 24`;
scanner v4.5.5. 1,242/1,242 W2 crops fetched, sha256 = readout `crop_sha256`.

- Contexts: 23 VALID, 2 terminal VOID (w2_00004, w2_00013: attempt 1 "unsupported view loop", the fresh re-read "forbidden literal
  path/name"); per the fleet rule the second VOID is recorded and left, so their 100 bed lines have no verdict (VOID-twice).
  4 more contexts were VOID on attempt 1 and VALID on the re-read (00012, 00017, 00021, 00023).
- Controls: 137/138 correct in the 23 VALID contexts (one multiline control in w2_00023 got CROP_VIOLATES without the expected reason set).
- Bed read 1,142: 919 OK, 122 CROP_VIOLATES, 101 TEXT_DIFFERS: 223 flagged (19.5%). In-quota 178/952, reserve 45/190.
  Reasons: turned_or_clipped 101, text_ne_visible_line 59, one_central_line 15, other_complete_line 12, gt2_whole_neighbour_words 2.
- Flags by class: caps_headings 0/49, curved_skewed 2/44, degraded 13/48, font_extremes 4/42, greek_latin 15/56, latin 4/71,
  leaders_dashes 4/47, long 16/60, modern_cyrillic 5/46, monotonic 12/112, numeric_cells 12/117, poly_dictionary_journal 19/104,
  polytonic 32/151, short 10/103, **vertical_turned 75/92** (the owner rule "turned or clipped fails" applies to that class by design).
- Tokens: 13,797,533 over 31 attempts (88% cached), 0.99M per 100 cards. Codex weekly 42% → 42%.

Summary script `artifacts/lf1/prod/lf1_batch_summary.py <prefix>`; output `artifacts/lf1/prod/w2_read_summary.txt`.
