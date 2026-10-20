# ASTRA-SC1 cycle 3 — verification pass 4 (same reviewer session): SF6c only — FINAL pass tonight

Your pass 3 (`ASTRA-SC1c3v3_review_1.md`) was NOT CLOSED with SF6-V3-B01 (missing recogniser confidence loaded as 0.0 counted as scored) and
SF6-V3-B02 (ordinary absence spans not checked against the image / target window). SF6c is committed on `opus/spellcheck` (`git log -1`;
SF6c section of `docs/records/labelfix/spellcheck/SF6_REPORT.md`, policy `sf6-release-v1`, sha 6f62925a…c406). The coordinator ruled this is the last
gate pass tonight: no further gate change follows, whatever you find.

## Verify SF6c only
1. B01: does a missing score now stay missing end to end (loader `ctc_align.py`, writers `m2_run.py`, `l1_infer.py`, `l1e_run.py`,
   `l1e_measure.py`, `r1_extract.py`, and `scripts/labelfix/clariden/l1_detect.py` — the historical L1 builder restored from the immutable
   snapshot with only confidence/regional-evidence/width added; check that claim)? Is the 0.5 floor justified by the saved evidence, and is
   a genuine 0.0 never positive?
2. B02: one shared containment helper for the reader, recogniser and MOVE paths; image bounds and target-window coverage required.
3. Your 75 reviewer tests are now `tests/labelfix/test_sf6_reviewer.py`: confirm the only harness adaptation (`0.0` → `None` for the loader
   default) is legitimate and that no release/HOLD assertion was weakened; confirm the fixture change in `test_sf6.py` (explicit width and
   synthetic regional scores) does not mask a production gap.
4. Did SF6c change anything beyond B01/B02 (rule, MOVE exception, slot decisions, held-out/M2/witness outcomes other than newly HOLD lines)?

Last line: `ASTRA-SC1c3v4 VERDICT: <CLOSED|NOT CLOSED>; B01 fixed <yes|no>; B02 fixed <yes|no>; reviewer tests not weakened <yes|no>; recompose under sf6-release-v1 allowed: <yes|no>`.
