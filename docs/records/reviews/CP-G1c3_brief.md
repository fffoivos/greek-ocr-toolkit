# CP-G1c3 — scoped verification of the CP-G1c2 fixes (final check after two Sol HOLDs)

ROLE: independent CERTIFIER of FIXES (the implementer is a Claude Opus session). Adversarial, firsthand: re-run the
cycle-2 reviewer's probes and your own; report failing numbers raw. Do NOT start background jobs.

SCOPE (repo /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit, read-only):
- `git diff 6df1fca 7f61e32 -- greekocr/glyphs tests/glyphs scripts/glyphs docs/records/glyphs/glyphs_fixture_labels.json`
- Read: docs/records/reviews/CP-G1c2_review_1.md (the findings), docs/records/reviews/CP-G1c2_reply_1.md (the claimed fixes),
  docs/records/glyphs/GLYPHS_PLAN.md ("State 16:05").
- Evidence: ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/CP-G1c3-evidence/
  (evals_v5.txt, evals_v6.txt, fixture_double.txt, review_data_v3.json, poly_lines.jsonl = DIR for eval scripts).
- Run Python as `.venv/bin/python` from the repo root with PYTHONDONTWRITEBYTECODE=1; pytest with -p no:cacheprovider.

ACCEPTANCE CRITERIA
1. For each CP-G1c2 finding F1–F7: fixed / not fixed, verified by re-running the original failure or an equivalent.
2. Truth independence: letter-state truth (print and visible) and neighbour recall must not depend on the detector's
   band, ink mask or components. Probe it.
3. The two truths are defined before measurement and not tuned to the detector; the plan reports both honestly,
   including the weak numbers (print-truth merged precision, broken recall, vanished letters).
4. No regression in the cleared parts (skew, band, marks, document prior, strict JSON) — spot-check line04 and the
   owner example.
5. Re-derive at least: eval_glyphs (N ≥ 100, seed 11, neighbours 1) and broken_eval (N ≥ 80) headline numbers.
OUT OF SCOPE: new features not in the diff; design preferences; verify/, readers/, other jobs' files.

DISPOSITION: BLOCKER/HIGH are fixed before the next feature step (multi-line tracking) builds on this package;
MEDIUM/LOW fixed or explicitly deferred.

DELIVERABLE (markdown): header → one-line verdict → findings most severe first ([BLOCKER]/[HIGH]/[MEDIUM]/[LOW], path:line
or number, failure scenario, fix) → per-finding fix table → claims re-derived → cleared. Last line exactly:
VERDICT: <PASS|HOLD> <one line> | BLOCKERS: <n> | HIGH: <n>
