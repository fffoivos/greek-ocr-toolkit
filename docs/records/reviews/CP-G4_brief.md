# CP-G4 — certify S2–S4: readability verdicts, tight straightening, calibration, final page (+ CP-G3c2 residual fix)

ROLE: independent CERTIFIER (implementer: Claude Opus). Adversarial and firsthand; recompute quoted numbers (reduced N
fine); report failures raw. Do NOT start background jobs.

SCOPE (repo /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit, read-only):
- `git diff b5a639d 31b7783 -- greekocr/glyphs tests/glyphs scripts/glyphs docs/records/glyphs/GLYPHS_CALIBRATION.md`
- Read: docs/records/glyphs/GLYPHS_CALIBRATION.md (the claims), docs/records/reviews/CP-G3c2_review_1.md (residual F1 — the shading rule is
  now edge-softness based), docs/records/glyphs/GLYPHS_PLAN.md (owner direction 16:40).
- Data (read-only): ~/Projects/glossapi-ocr-local/experiments/glyphs_calib/ — strips_v1, strips_v2,
  strips_v2_straight, strips_v2_straight_tight, strips_v2_tight_m02/m05/m03_level: manifest.jsonl,
  measurements.jsonl, predictions_cllg.jsonl, predictions_e1.jsonl (E1 = e2e_retrain_f50_s0; text NFD).
- Published final page: https://claude.ai/artifact/47PAcqCiBPw7eYa7f8Ecqi (built by scripts/glyphs/build_final_page_data.py
  + build_review_page.py --template final_page.html; rebuild locally to inspect).
- Python: `.venv/bin/python` from the repo root, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider.

ACCEPTANCE CRITERIA
1. CP-G3c2 residual F1: faint bold letters in tight crops keep their ink (re-run the CP-G3c2 probes); the owner's
   shadow (s2-3229200bf47ca465a42d-p00004-l00018) is still removed; _edge_sharpness is sound (border, letters inside).
2. Calibration claims: recompute the CLLG and E1 tables (NFD headline, NFC, mark F1) and the limits from the raw files;
   is the limit rule applied as stated? Is any limit derived circularly or from too few strips? Are the v2 conditions
   what the doc says (accent_cut / top_cut / tail_cut / bottom_cut geometry in calib_strips.py)?
3. readability.py: zone-cut profiles (gating on ink touching the edge), limits from READER_LIMITS, verdict thresholds,
   target clarity; construct failing inputs (e.g. a crop cut at the top where no ink touches the edge but letters are
   missing; neighbour ink touching the edge counted as the main line's).
4. lines_api tight / margin 0.2 / level_deg 0.3: geometry and the claimed level-line equivalence (paired bootstrap).
5. Final page: verdict counts (195 / 241 / 8 of 444), selection logic, data size, honesty of the facts box.
6. Tests (57) guard the claims?
OUT OF SCOPE: other jobs' files; design preferences.
DISPOSITION: BLOCKER/HIGH fixed before the readability API is handed on (coordinator / data-mix); MEDIUM/LOW fixed or deferred.
DELIVERABLE (markdown): header → verdict → findings most severe first (path:line/number, failure, fix) → claims
re-derived → cleared. Last line exactly: VERDICT: <PASS|HOLD> <one line> | BLOCKERS: <n> | HIGH: <n>
