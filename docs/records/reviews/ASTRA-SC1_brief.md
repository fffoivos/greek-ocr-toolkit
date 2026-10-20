# ASTRA-SC1 — Review of the polytonic spell-check / accent-detection track (gpt-6-astra, xhigh, read-only)

Repository: this worktree, branch `opus/spellcheck` (head at review start; the track lead keeps working in scratch only, so nothing
in the repo changes during the review). You may read anything, run python/pytest (Python:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=<repo root>`) and small scripts on
≤ 30 line crops; no network, no CTC/GPU runs, no bulk processing.

## What the track does (context)
Owner task: "an algorithm that fact-checks all accents; it works independently from Google, otherwise how can it correct Google".
Labels must transcribe what is PRINTED (misprints included); a correction is admitted only when the ink justifies it.
Pipeline under review:
- letters + positions: our CTC recogniser (cached alignments, `greekocr/labelfix/ctc_align.py`);
- mark detection / segmentation: `greekocr/labelfix/ink.py`, `segmentation.py` (S6: letters by font size, fused/split letters,
  accents separated above the meanline), `case.py` (S5: capitals), `reading.py` (independent line reading, `apply_constraints` = K1);
- mark naming: R1 purpose-built reader (`scripts/labelfix/clariden/r1_*.py`, result `docs/records/labelfix/spellcheck/clariden/R1_result_3678928/`);
- orthographic constraints: `greekocr/labelfix/constraints.py`;
- evaluation: held-out print truth (666 lines, 14 books; `scripts/labelfix/s*_validate.py`, `r1_score.py`), owner notes
  (`docs/records/labelfix/spellcheck/owner_notes_*`), regression tools `scripts/labelfix/owner_implicit_changes.py`, `box_regression.py`;
- reports: `docs/records/labelfix/spellcheck/S4_REPORT.md` … `S6_REPORT.md`, `K1_REPORT.md`, briefs in `docs/records/briefs/S4…S6, K1, R1, R0`.

## Question 1 — Did the track use the toolkit's own tools where they exist?
The owner asks whether we "used all tools properly from our ocr toolkit (eg font lines or other aspects) that are available".
Inventory the toolkit (`greekocr/glyphs/*`, `greekocr/pages/*` (font, structure), `greekocr/glyphs/lines_api.py` (four guide lines,
straightening), `glyphs/letters.py` (owner rule 8 Oct: letters = pieces in the middle region, merged blobs split), `glyphs/baseline.py`,
`glyphs/readability.py`, `glyphs/statistics.py`, `greekocr/readers`, `greekocr/score`, `greekocr/verify`, `greekocr/synth`, docs such as
`docs/records/glyphs/GLYPHS_CALIBRATION.md`) and, for every function the spell-check track needs (x-height / mean line / baseline / ascender and
descender lines per x, font size, letter segmentation and merged-letter splitting, capital vs ascender, line straightening, crop
cut-off masks, skew), answer: does `greekocr/labelfix` use the toolkit implementation, re-implement it, or ignore it? Where it
re-implements: is the toolkit version better (owner-validated, calibrated, tested), and what concretely would change if we switched?
Give file:line evidence on both sides. Rank the substitutions by expected effect on the owner's open complaints (fused letters,
capitals and side marks, accents merged with letters, letter height in a word).

## Question 2 — Issues in the current implementation
Look for correctness problems, measurement problems and process problems, e.g.:
- leakage: anything from Google, the human text or print truth reaching runtime decisions or R1 inputs; held-out/DEV/train overlap;
- evaluation: denominators, unscored/unknown handling, the "all slots" vs "scored" tables, S4-frozen instrument limits (truth known on
  only 16 fused slots), owner-note checks' interpretation, the implicit-approval and box-regression tools (matching, slot assignment);
- K1: rules that could delete printed marks on other books; the held-back C3/C1 rules;
- R1: label noise from Google = recogniser agreement (the recogniser was trained on Google labels), sampling arms, window geometry,
  the font-size admission rule, the 715 unmapped held-out samples, fused-letter windows;
- code: fragile heuristics, magic numbers without evidence, silent fallbacks, tests that assert little;
- the owner-page builder `scripts/labelfix/owner_pages_build.py` (independent "Ours" line; must show nothing from Google in Ours).

## Output
`ASTRA-SC1_review_1.md`: findings ranked by severity (BLOCKER / MAJOR / MINOR), each with file:line evidence and a concrete fix;
a table for Question 1 (need → toolkit implementation → labelfix status → recommendation). Last line:
`ASTRA-SC1 VERDICT: <PASS|PASS WITH FIXES|FAIL>; blockers <n>; majors <n>; toolkit substitutions recommended <n>`.
