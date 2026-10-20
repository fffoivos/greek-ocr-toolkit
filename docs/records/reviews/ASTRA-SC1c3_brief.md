# ASTRA-SC1 cycle 3 — NARROWED re-review of the release gate (gpt-6-astra, xhigh, read-only)

Repository: this worktree, branch `opus/spellcheck` at the harness head. Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`,
`PYTHONPATH=<repo root>`. No network, no GPU/CTC/R1 inference, ≤ 30 crops for spot checks.

Cycle 2 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c2_review_1.md`) found C2-B01 (blocker: corrections accepted despite recorded
uncertainty), C2-M01 (edit guard deleted unsupported marks), C2-M02 (page builder not at parity), C2-M03 (S7 adapters), C2-N01/N02. Fix
rounds since: SF2 (`docs/records/labelfix/spellcheck/SF2_REPORT.md`, shared gate `greekocr/labelfix/release_gate.py`), L1E (ENSEMBLE_AB mode +
Clariden job, `docs/records/labelfix/spellcheck/clariden/L1E_REPORT.md`), SF3 (gate relevance, `SF3_REPORT.md`). The coordinator narrowed this cycle;
the owner was told why a third cycle runs.

## Scope (only these)
1. **The shared composer and gate semantics** (`release_gate.py` and every caller: L1r/`l1r_recompose.py`, `l1_common.py`, L1E scripts,
   M2/`m2_run.py`, `agreement_mode.py`, owner-page builders): do C2-B01/C2-M01/C2-M02/C2-N01/C2-N02 now hold? Re-run your cycle-2 probes
   (`ASTRA-SC1c2_evidence/`) against the current code. Is ENSEMBLE_AB implemented as ruled (names from A; accept only on identical A/B mark
   sets; HOLD on K1 flags and every uncertainty state; detector contributes only localisation_unknown, segmentation_uncertain, apostrophes /
   quotes; its kind veto dropped)? Are SF3's relevance rules (clipped_bottom only on α η ω / predicted below-mark; clipped_top only where the
   cut meets the mark zone; edit-guard character classes) safe — can any of them now let an unobserved or unsupported mark through?
2. **The edit-guard domain:** is it explicit, complete for polytonic Greek, and does it preserve every unsupported printed mark?
3. **L1r / L1E receipts:** release manifests (overlays, kept/control releases, per-wave coverage, exclusions, the verbatim ensemble caveat,
   code/policy/checkpoint hashes); would a wave-1c consumer be able to verify original-label hashes, pairing, and that no HOLD falls back?
4. **Your probes as tests:** are the witness probes now repository tests that fail on the old code and pass on the new?

## Explicitly out of scope (deferred by the coordinator, with owners)
M01 correlated supervision + truth provenance → R0 (now partly delivered: `R0_REPORT.md`, locked strata); M02 character-indexed fused/unmapped
evaluation → R0; M10 straightened R1 view → R2; N02 arm ablation → R2; C2-M03 S7 adapter contracts → a future S-iteration after the
training-wave DEV exists (adapters stay off). Context: `docs/records/labelfix/DIRECTION_DECISION_20261017.md`.

## Output
`ASTRA-SC1c3_review_1.md`: per-finding verdicts for C2-B01, C2-M01, C2-M02, C2-N01, C2-N02 (FIXED / PARTLY / NOT FIXED) with file:line
evidence; new findings in scope ranked BLOCKER / MAJOR / MINOR; an explicit answer whether L1r releases recomposed under this gate may be
bound by wave 1c as a pseudo-label experiment. Last line:
`ASTRA-SC1c3 VERDICT: <PASS|PASS WITH FIXES|FAIL>; C2 fixed <n>/5; new blockers <n>; new majors <n>; L1r releases usable for wave 1c: <yes|no|with conditions>`.
