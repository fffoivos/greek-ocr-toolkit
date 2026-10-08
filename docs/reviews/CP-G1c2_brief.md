# CP-G1c2 — re-certify the glyph package after the CP-G1 HOLD fixes and the owner-requested changes

ROLE: independent fresh-eyes CERTIFIER. The implementer (a Claude Opus session) is not the certifier. Be adversarial,
verify FIRSTHAND, recompute claimed numbers (smaller N is fine where a full re-run is slow), report failing numbers RAW,
never trust the implementer's summary. Do NOT start background jobs; run everything in the foreground.

READ FIRST (repo root /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit):
- docs/GLYPHS_PLAN.md (owner requirements: hard constraints vs open; plan; measured numbers; known open problems)
- docs/GLYPHS_STATE.json, docs/STANDARD.md (repo standard), scripts/glyphs/eval/README.md

SCOPE (all new, uncommitted files; other working-tree changes belong to other jobs and are OUT of scope):
- greekocr/glyphs/{__init__,components,letters,baseline,ink,synthetic,evaluate,report}.py
- tests/glyphs/test_glyphs.py, tests/fixtures/fonts/ (two OFL fonts + PROVENANCE.json)
- scripts/glyphs/{build_review_data.py,build_review_page.py,review_page.html,run_review.sh}, scripts/glyphs/eval/*
- Evidence (outside the repo, read-only for you): ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/
  review_scratch/CP-G1c2-evidence/{review_data_v2.json, line-skew-ink.html (published v2), poly_lines.jsonl, evals_v4.txt, skew_eval_conf.txt, mark_stats.txt}
- Eval scripts take DIR = that evidence directory (it holds poly_lines.jsonl); fonts are read from
  ~/Projects/greek-page-ocr/assets/fonts. Run Python as `.venv/bin/python` from the repo root with
  PYTHONDONTWRITEBYTECODE=1; pytest with `-p no:cacheprovider`.

ACCEPTANCE CRITERIA
1. Correctness: binarisation, the band fit (RANSAC + growth, both-edge evidence, x-height estimators incl. the
   'substantial_letters' switch and the document prior), roles (letter / mark / punct / fragment / neighbour / rule /
   large), letter splitting, skew angle sign and trail convention, crossings, cut spans, cut letters, ink features and
   score, report fields. Find real bugs with concrete failing inputs.
2. Validation hygiene: thresholds/weights are set on one seed and measured on another (NEIGHBOUR_GAP_* from mark_stats
   seed 5; ink WEIGHTS from ink_eval seed 1, tested seed 2); check for leakage or circularity (e.g. the evaluator
   sharing logic with the thing it scores; truth that can be wrong, such as rotated glyph boxes or anti-aliasing
   in the mark truth).
3. Numbers: recompute the numbers quoted in docs/GLYPHS_PLAN.md and on the page ("State 14:45" paragraph) — at least
   eval_glyphs (any N ≥ 100, seed 11, neighbours 1), skew_eval, and ink_eval — and say whether each claim holds.
4. Owner hard constraints: the PDF text layer is never used as reference or gate anywhere in scope (grep the code and
   the page data); fonts are coverage-checked before use; outputs are localised along x.
5. The artifact data (review_data.json) matches what the code produces for those crops, and the page states its
   limits honestly (owner example limitation, straight-only validation).
6. Tests: run `tests/glyphs`; judge whether they would catch regressions in the claims above.
OUT OF SCOPE: greekocr/verify, greekocr/real, cli.py, pyproject.toml and other jobs' files; design preferences.

DISPOSITION: BLOCKER/HIGH are fixed before this package is committed and before the next iteration (P2) builds on it;
MEDIUM/LOW are fixed or explicitly deferred in a reply document.

DELIVERABLE (markdown only): header (scope, what you ran) → one-line verdict → findings F1… most severe first, each
[BLOCKER]/[HIGH]/[MEDIUM]/[LOW] with path:line or the number, a failure scenario and a fix → claims re-derived (table:
claim, your number, holds?) → cleared items. Last line exactly:
VERDICT: <PASS|HOLD> <one line> | BLOCKERS: <n> | HIGH: <n>

CYCLE 2 ADDITIONS
- Read your cycle-1 review docs/reviews/CP-G1_review_1.md and the implementer's reply docs/reviews/CP-G1_reply_1.md.
  For EACH finding F1–F8 verify the fix firsthand (re-run your cycle-1 probes where possible) and say fixed / not fixed.
- New since cycle 1 (owner-requested, in scope): bend tracking (components._track/_smooth_curve + model selection),
  letters.py rewritten (pieces grouping, rule 1 column share + rule 2 width, merged split with bridge test), ink.py
  rewritten (broken / faint / merged states), faint channel in binarise, baseline.second_line + DOUBLE_RATIO,
  evaluate.py rewritten (truth-enumerated), synthetic.py rewritten (real graphemes only, IGNORE, coverage gate,
  defect maps, bend, second_line), eval scripts rewritten (scripts/glyphs/eval/*: eval_glyphs, broken_eval,
  double_eval, skew_eval, mark_stats, common).
- Recompute the "State 15:15" numbers in docs/GLYPHS_PLAN.md (reduced N acceptable) and the facts box of the page.
- Judge whether the measured test floors (letter one-box ≥ 0.75 on Didot lines; double-line rendered FP ≤ 2/4;
  thick→merged factor 1.3) are honest regression guards or hide defects.
- The old evidence dir CP-G1-evidence is superseded.
