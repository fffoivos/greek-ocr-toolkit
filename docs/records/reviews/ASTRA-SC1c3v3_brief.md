# ASTRA-SC1 cycle 3 — verification pass 3 (same reviewer session): SF6 only

After your SF5 pass (CLOSED), the coordinator ruled that any deletion of a Google character on ONE absent source is the unobserved-as-absent
pattern (your out-of-scope notes: keraia `Ι'.` → `Ι.`, leading opening quote). SF6 is committed on `opus/spellcheck` (see `git log -1`;
`docs/records/labelfix/spellcheck/SF6_REPORT.md`, policy `sf6-release-v1`). The rule, exactly as ruled: a release may delete a character present in
Google's label only with two positive absence signals — marks: reader (A∧B as one) AND detector, or reader AND recogniser text;
apostrophes/quotes/keraia: detector absent AND recogniser text absent; all observed, scored, in-window; replacements count as deletions of the
replaced character, elision aliases excepted; anything less is HOLD.

## Verify SF6 only
1. Is the rule implemented exactly, and only it? Diff 05f2dafb..8c5ad361 (`release_gate.py`, `l1_common.py`). Probe: can any Google character
   still be deleted on one signal (missing/unscored/clipped states, replacement paths, multi-character edits, alias paths, PRESENCE/FULL/AE)?
   Is "positive absence" for the recogniser text sound (the report uses a saved `recognition_confidence` and a located span)?
2. SF5 regression: SF6 edited `tests/labelfix/test_sf5.py` — confirm each edit only replaces a release expectation by an exact HOLD check
   under sf6 and keeps the composer/slot assertions (no weakening).
3. The cost and its cause: held-out AB corrected 45 → 11 (lines 35 → 6), wrong 2 → 0. The report says the local 666 artifact lacks full
   extraction coverage, so reader absence is often unavailable locally. Is that held-out number a property of the rule or of the local
   evidence? State what a full-runtime recomposition would need to answer it.
4. **Coordinator ruling, implemented as SF6b (8c5ad361) — verify it, do not re-rule it:** `-᾿Αλλά` → `-Ἀλλά` is a MOVE, not a deletion,
   when the combining breathing written is the same kind (psili/dasia) as the spacing sign consumed AND the reader (A∧B as one) names that
   breathing on that capital (observed, scored, in-window). It needs no absence signal. This is the ONLY exception to SF6. Check it cannot
   release a mismatched kind, an unnamed breathing, a non-capital, or anything other than that one spacing sign; witnesses in
   `tests/labelfix/test_sf6.py` and the SF6b section of `SF6_REPORT.md`.
(An earlier start of this pass was stopped before SF6b so that one pass covers both; ignore any partial log.)

Last line: `ASTRA-SC1c3v3 VERDICT: <CLOSED|NOT CLOSED>; SF6 rule exact <yes|no>; SF5 tests not weakened <yes|no>; recompose under sf6-release-v1 allowed: <yes|no>`.
