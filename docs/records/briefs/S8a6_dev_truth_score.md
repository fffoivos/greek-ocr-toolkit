# S8a6 — Score the print-adjudicated S8 DEV: truth per wave, source accuracy, presence P/R (gpt-6.1-sol, xhigh, network OFF)

Workspace/rules: as S8a/S8a2/S8a4 (read them). Head = this commit. Network OFF; no detector/reader/gate code changes; analysis only.
Do not modify `docs/records/labelfix/spellcheck/S8_DEV/cards/` or `private/cards/` (frozen deck + key).

## Inputs
- Deck/key: `S8_DEV/cards/items_blind.json`, `S8_DEV/private/cards/items_key.json` (1,793 items, per-item `wave`, `control`, `selection`
  (disagreement / all-agree 5% sample / control), source `forms`, `candidate_sources`, inclusion probabilities if present).
- Adjudication cut (coordinator): `S8_DEV/cards/cut_receipt.json` — 1,063 items adjudicated: parliament ALL 578 data cards; round1/round2/
  mixed/vouli 100 data cards each (seeded); 85 controls. Unread cards stay unadjudicated (state it).
- Readers: `S8_DEV/cards_private/readers/r{1,2}_*.jsonl` (files `r?_000…r?_270` index the FULL deck items 0–359; files `r?_cut_*` index
  `cards/items_blind_cut.json`; join by `id`, not by position). Tiebreak: `S8_DEV/cards_private/tiebreak/{items_tb.json,r3.jsonl}`
  (majority of three; unresolved → UNKNOWN, excluded, counted).
- Excluded control: `item_fa47d3102d8d11bd` — its key is wrong (the print has ἔχη, no iota subscript; both readers correctly rejected both
  options; verified by the track lead on the image). Report it as a control-construction defect.
- Truth conventions: the ink, misprints included; elision aliases one atom (codec v2.1); U+1FBF before a capital = breathing.

## Report
1. Reader quality: per reader controls (expect 82/84 each, 0 shared misses), inter-reader agreement per wave, tiebreak outcomes.
2. DEV truth per wave with sample sizes stated: for each source (Google label, R1 arm A, detector-composed original, frozen-gate AB outcome)
   the share of adjudicated word cards whose form equals the print — **weighted** to the wave's card population (disagreement cards by the cut
   sampling fraction; all-agree words by the 5% sample's inclusion probability), with Wilson / bootstrap 95% intervals; unweighted counts beside.
3. **Presence P/R per wave** (the S8 judging metric): per letter slot in adjudicated words, mark presence (any mark / per mark family:
   breathing, accent, subscript, diaeresis) for the detector (original crops) and R1-A against the print; weighted as in 2, with intervals.
   Also `localisation_unknown` and `segmentation_uncertain` rates from the S8a baseline beside them.
4. Elision/alias-only cards scored separately (33 tagged).
5. What S8b should target: the top failure classes for the detector per wave (by weighted count), with ≥ 3 example ids each.

`docs/records/labelfix/spellcheck/S8a6_DEV_TRUTH.md` + `S8_DEV/evidence/dev_truth.jsonl.gz`; last line:
`S8 DEV TRUTH: adjudicated <n> data cards (parliament <p>, others 4×100); controls r1 <a>/84 r2 <b>/84; detector presence P/R by wave …; R1-A …; Google word accuracy …; S8b targets …`.
