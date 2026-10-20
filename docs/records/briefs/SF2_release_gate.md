# SF2 — Fix round for ASTRA-SC1 cycle 2: one release gate (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head 2ac34b23). No `.git` writes. Network OFF. Python:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU; cached data only; no CTC/R1/GPU
runs; ≤ 40 min. Do not touch other worktrees (R0a runs in `…-spellcheck-r0`; L1 is in `…-spellcheck-l1`, read it, do not modify it).
Read `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c2_review_1.md` and its `ASTRA-SC1c2_evidence/` probes in full first. Every
probe becomes a repository test that fails before and passes after. No existing test weakened. No retraining, no detector-geometry change.

## Fixes
1. **C2-B01 (blocker) + C2-M02: ONE shared composer/serializer** (e.g. `greekocr/labelfix/release_gate.py`) used by the L1 release path
   (`l1_common`/`m2_run.combine` equivalents), the measurement paths (M2, CN1-style owner scoring) and the owner-page builders. It takes the
   detector reading, the R1 prediction + its coverage record, K1 flags, and decides per slot ACCEPT / KEEP / HOLD with a reason. HOLD when:
   R1 missing; R1 `evidence_state=UNKNOWN` or any R1 uncertainty (no pixel evidence, out-of-image span, …); detector `localisation_unknown`,
   `segmentation_uncertain`, unnamed marks; relevant directional clipping of the mark zone (until validated observability masks exist, a
   clipped relevant zone is HOLD, not "no mark"); K1 flag; mark-kind disagreement (PRESENCE) / mark-set disagreement (FULL). A prediction never
   turns absent or invalid observation into "no mark". Fused-but-resolved slots stay eligible. Opening quotes and elision apostrophes are
   composed from detector evidence identically on every path (fixes the page's lost opening quotes and the missing apostrophe boxes the
   track lead found: `scripts/labelfix/owner_reading.py` reads `evidence['apostrophes']`, which `read_ink` does not fill).
2. **C2-M01: edit guard.** Before any edit is released, compare original label and proposal per character against an explicit supported
   domain (Greek base letters; marks psili, dasia, acute, grave, circumflex, subscript, dialytika with legal multiplicity). Any original
   character/mark outside the domain (macron ᾱ, Latin diacritics é, double accents ά̀, …) is preserved unchanged or the line is HOLD —
   never deleted or normalised. Punctuation edits have their own explicit policy (state it).
3. **C2-N01:** `scripts/labelfix/agreement_mode.py` calls the shared gate (or is renamed as a historical counterfactual); flags are part of
   the decisive HOLD predicate.
4. **C2-N02:** `box_regression.py` also diffs matched owners (display slot), source-pixel membership and status at high IoU; the CLI requires
   an explicit notes-to-reviewed-page binding before it uses "approved" language.
5. **L1r recomposition:** a script `scripts/labelfix/clariden/l1r_recompose.py` that rebuilds both variants' overlays, kept/control
   releases and receipts from L1-v0's SAVED per-line evidence (detector reading, window coverage, R1 prediction) under the new bound
   policy, without rerunning detection or R1. Inspect what `l1_*.py` in the L1 worktree saves per line and state whether it is sufficient
   for every gate input (esp. R1 coverage/uncertainty, detector segmentation/clipping state). If not sufficient, say exactly what is missing
   and design the minimal re-run. L1-v0 outputs stay as historical; L1r gets new release names (`v2-corrected-presence-r`, `…-full-r`).
   Mock it on the L1 mock outputs (`~/Projects/greek-ocr-toolkit-spellcheck-l1/artifacts/labelfix_l1/`) and report how many mock decisions
   change and why.
6. Re-run M2 and the owner-page build through the shared gate (scratch outputs; report changes vs the previous numbers: corrected / HOLD /
   new, lines held; box regression S6 pages → combined pages with the fixed apostrophe/quote handling).

## Deliverables
Code + tests, `docs/records/labelfix/spellcheck/SF2_REPORT.md` (one section per finding; numbers before → after), last line:
`SF2 RESULT: shared gate on <paths>; C2-B01/M01/M02/N01/N02 fixed; L1r evidence sufficient <yes|no: …>; mock decisions changed <n>; M2 PRESENCE corrected … HOLD lines …; tests <n> passed`.
