# CP-G3 — certify step S1: CP-G2 fixes, letters bounded by their line, column split, per-column records, lines API, capitals measurement

ROLE: independent fresh-eyes CERTIFIER (implementer: a Claude Opus session). Adversarial, firsthand; reproduce probes,
recompute quoted numbers (reduced N fine); report failures raw. Do NOT start background jobs.

SCOPE (repo /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit, read-only):
- `git diff b11b2e8 1dc5570 -- greekocr/glyphs tests/glyphs scripts/glyphs docs/records/glyphs/GLYPHS_PLAN.md`
- Read first: docs/records/reviews/CP-G2_review_1.md + CP-G2_reply_1.md; docs/records/glyphs/GLYPHS_PLAN.md (owner direction 16:40, state,
  capitals section). Owner rules: a letter box never leaves its line; split columns at rules / unaligned wide gaps,
  never force alignment; be careful with capitals.
- Evidence dir (DIR for eval scripts): ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/CP-G1c3-evidence
- Run Python as `.venv/bin/python` from the repo root, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider.

ACCEPTANCE CRITERIA
1. CP-G2 F1–F6 fixed as claimed (re-run your cycle probes; scripts/glyphs/eval/neighbour_eval.py numbers).
2. letters.py: LINE_HEIGHT / PATCH_THICKNESS exclusion and line clipping — correct, and not excluding legitimate letters
   (over-inked, tall capitals with accents, ligatures); components.binarise stroke-like faint rule — does it drop real
   faint letters? Construct counterexamples.
3. columns.py: rule detection (RULE_HEIGHT, RULE_ASPECT, RULE_OVER_LETTERS), soft cuts (GAP_CUT, ALIGN_TOL, SOFT_MIN,
   trusted x-height), shared x-height refit — false splits of single lines? missed columns? Use the 444 crops
   (40 two-segment crops claimed; owner crops s2-49598b2e848ab1f0ee1e-p00001-l00043, s2-74cdb23a34ca4a6cd01e-p00002-l00048,
   s2-74cdb23a34ca4a6cd01e-p00010-l00018 must split; the owner example s2-60f24a3d8a2d714767f2-p00003-l00024 must not).
4. report.line_record per-column structure: fields, coordinates (x_offset), JSON strictness, top-level summary choice.
5. lines_api.separate_lines / straighten: geometry (straightened baseline flat; missing mask = rows outside the crop;
   top_cut/bottom_cut definitions), x ranges in crop coordinates, neighbour lines included only above min_visible.
6. Capitals: capitals_eval.py measurement and the plan's claims; the reverted capital rule is not in the code.
7. Tests: 43 pass; do the new tests guard the claims?
OUT OF SCOPE: verify/, readers/, web_render, other jobs' files; design preferences.
DISPOSITION: BLOCKER/HIGH fixed before the readability calibration (S3) builds on this; MEDIUM/LOW fixed or deferred.
DELIVERABLE (markdown): header → verdict → findings most severe first (path:line/number, failure scenario, fix) →
claims re-derived → cleared. Last line exactly: VERDICT: <PASS|HOLD> <one line> | BLOCKERS: <n> | HIGH: <n>
