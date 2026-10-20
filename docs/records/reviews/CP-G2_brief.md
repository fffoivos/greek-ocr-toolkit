# CP-G2 — certify the four-guide-line model for every text line (main + neighbour lines) and the batch 3/4 pages

ROLE: independent fresh-eyes CERTIFIER (implementer: a Claude Opus session). Adversarial, firsthand, recompute
numbers, report failures raw. Do NOT start background jobs.

SCOPE (repo /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit, read-only):
- `git diff 7f61e32 e9f9a17 -- greekocr/glyphs tests/glyphs scripts/glyphs` — mainly baseline.text_lines / GuideLines,
  synthetic.other_base_truth, evaluate vanished/missed fix, report 'lines', scripts/glyphs/eval/neighbour_eval.py,
  build_review_data.py (modes fixes/new), review_page.html (guide-line drawing, facts box).
- Read: docs/records/glyphs/GLYPHS_PLAN.md ("State 16:20"), docs/records/reviews/CP-G1c3_review_1.md + CP-G1c3_reply_1.md.
- Evidence: ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/CP-G1c3-evidence/
  (neighbour_eval.txt, evals_v7.txt; poly_lines.jsonl = DIR). Published pages: batch 3
  https://claude.ai/artifact/FrYMi9ra4boVf6auGm3arm, batch 4 https://claude.ai/artifact/9KLGRzRd7VuEBCqC7mxrUC
  (rebuild their data with scripts/glyphs/build_review_data.py into scratch to compare; previous-batch JSONs are not
  in the repo — use mode `new` for a full comparison).

ACCEPTANCE CRITERIA
1. Correctness of text_lines: vote hypotheses (mean line / tall-letter top / baseline / hanging bottom / accent), the
   histogram/peak logic, the 1.8 x-height separation, the ±6 x-height range, side assignment, guide-line geometry
   (ascender < mean < base < descender), visible fraction. Construct failing inputs.
2. Truth: other_base_truth follows the same rotation / bend / crop as the image (verify independently).
3. neighbour_eval: the 'present' definition, matching of predicted to true lines, and whether the quoted numbers
   (96 % found, median 0.056, 74 % ≤ 0.25, 87 % ≤ 0.5 x-heights) hold; false lines are counted honestly?
4. The page facts box: every number traceable to evals_v7 / neighbour_eval / fixture_double; known limits disclosed.
5. Regression check: CP-G1 behaviours unchanged (tests/glyphs; skew/line04/owner example spot checks).
OUT OF SCOPE: verify/, readers/, other jobs' files; design preferences.
DISPOSITION: BLOCKER/HIGH fixed before the next feature step; MEDIUM/LOW fixed or explicitly deferred.
DELIVERABLE (markdown): header → verdict → findings most severe first with path:line/number, failure scenario, fix →
claims re-derived → cleared. Last line exactly: VERDICT: <PASS|HOLD> <one line> | BLOCKERS: <n> | HIGH: <n>
