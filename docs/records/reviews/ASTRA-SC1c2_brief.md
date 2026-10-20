# ASTRA-SC1 cycle 2 — re-review of the spell-check / accent-detection track (gpt-6-astra, xhigh, read-only)

Repository: this worktree, branch `opus/spellcheck` at the head given by the harness. Also read (read-only) the L1 worktree
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1` at commit 6b91ebaa (branch `opus/spellcheck-l1`), which is what
Clariden job 3679313 runs. Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=<repo root>`.
No network, no CTC/GPU runs, no bulk processing (≤ 30 crops for spot checks).

Your first review: `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1_review_1.md` (FAIL: B01, M01–M10, N01–N03, 4 toolkit substitutions),
with probes in `ASTRA-SC1_evidence/`. The owner asked for this re-review "after you are done".

## Check 1 — Did the fixes hold?
For EVERY finding of cycle 1, verdict FIXED / PARTLY / NOT FIXED / ACCEPTED-AS-DEFERRED with file:line evidence, re-running your own
probes (`ASTRA-SC1_evidence/review_probes.py`) against the current code. Fix round: `docs/records/labelfix/spellcheck/SF1_REPORT.md` (commit 50b825a9).
Deferred by plan: M01 (locked fresh-book test set + per-slot truth provenance → R0, not started), M02 (character-indexed evaluation of
fused/unmapped strata → R0), M10 (R1 window/admission robustness → R2 retrain), N02 (arm ablation). Judge whether the deferral is
honestly recorded and whether anything shipped since (L1) depends on a deferred defect.

## Check 2 — The toolkit substitutions (your Question 1)
S7 implemented your four recommended substitutions as opt-in adapters and rejected all of them on qualification
(`docs/records/labelfix/spellcheck/S7_REPORT.md`, `greekocr/labelfix/toolkit_geometry.py`, `scripts/labelfix/s7_*.py`). Did S7 implement them
faithfully (the toolkit APIs used as designed: `glyphs.letters` middle-region pieces with parent sets and unresolved state; one shared guide
object with per-x provenance; cut masks), or did adapter choices cause the rejections? Are the qualification rules and instruments sound
(e.g. the "80 kind-disagreements" target, the owner-note instruments, the box regression)? Is rejecting all four justified, and what would
you try next for the detector's presence evidence?

## Check 3 — New work since cycle 1
- K1 print-preserving flags (B01 fix) and the agreement modes (`scripts/labelfix/agreement_mode.py`: FULL, PRESENCE, ZONE) — is the
  PRESENCE rule a sound "two pixel signals agree" check, given that the detector's mark KINDS come from the frozen S4 shape classifier?
- CN1 (`docs/records/labelfix/spellcheck/CN1_REPORT.md`) and M2 (`M2_REPORT.md`): instruments, denominators, claims.
- L1 (worktree above, `docs/records/labelfix/spellcheck/clariden/L1_REPORT.md`, `scripts/labelfix/clariden/l1_*.py`, `l1_job.sbatch`): input and
  exclusions, venv_l1 (scipy 1.17.1, E3 venv untouched), the in-job parity gate, overlay/release format, the ctrl-subset release, anything
  that would make the overlays unsafe for wave 1c training.
- The hash-bound owner-page builders and the regression tools (`owner_pages_build*.py`, `box_regression.py`, `owner_implicit_changes.py`).

## Output
`ASTRA-SC1c2_review_1.md`: the per-finding table for cycle 1; findings ranked BLOCKER / MAJOR / MINOR with file:line evidence and concrete
fixes; an explicit statement whether L1's overlays may be used by wave 1c. Last line:
`ASTRA-SC1c2 VERDICT: <PASS|PASS WITH FIXES|FAIL>; cycle-1 fixed <n>/<m>; new blockers <n>; new majors <n>; L1 overlays usable: <yes|no|with conditions>`.
