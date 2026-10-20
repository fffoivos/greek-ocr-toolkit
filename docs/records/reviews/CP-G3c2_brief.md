# CP-G3c2 — verify the CP-G3 fixes (second Sol cycle, scoped)

ROLE: independent CERTIFIER of FIXES (implementer: Claude Opus). Adversarial and firsthand: re-run your CP-G3 probes
(review_scratch/CP-G3/: probes.py, extra_probes.py, geometry_contract_probes.py, test_independent.py) against the
current code and report raw results. Do NOT start background jobs.

SCOPE (repo /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit, read-only):
- `git diff 1dc5570 b5a639d -- greekocr/glyphs tests/glyphs scripts/glyphs`
- docs/records/reviews/CP-G3_review_1.md (your findings; full report in review_scratch/CP-G3/CP-G3_review_1.md) and
  docs/records/reviews/CP-G3_reply_1.md (claimed fixes).
- DIR for eval scripts: ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/CP-G1c3-evidence
- Python: `.venv/bin/python` from the repo root, PYTHONDONTWRITEBYTECODE=1; pytest -p no:cacheprovider.

ACCEPTANCE CRITERIA
1. F1–F9: fixed / not fixed, each verified by re-running the original failure.
2. The new binarise patch rule (short side ≥ 30 % of crop height AND thickness ≥ 40 % of short side): does it still
   delete legitimate faint letters (large faint capitals in short crops, faint bold type)? Does it still remove the
   owner's page-edge shadow (tests/fixtures/o4d_sample400/crops/s2-3229200bf47ca465a42d-p00004-l00018.png)?
3. Removing PATCH_THICKNESS from letters: does any stain/shadow now become a letter box spanning outside its line?
4. Report / builder / page: run `scripts/glyphs/build_review_data.py new OUT.json` end to end; flattened coordinates.
5. No regressions in the 51 tests or in neighbour_eval (seed 71, N 150).
OUT OF SCOPE: anything outside the diff; design preferences.
DISPOSITION: BLOCKER/HIGH fixed before the readability calibration (S3) relies on this code; MEDIUM/LOW fixed or deferred.
DELIVERABLE (markdown): header → verdict → per-finding table → new findings (path:line, failure, fix) → cleared.
Last line exactly: VERDICT: <PASS|HOLD> <one line> | BLOCKERS: <n> | HIGH: <n>
