# SF4 — Conservative fixes for ASTRA-SC1 cycle 3 (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head at launch). No `.git` writes. Network OFF (no Clariden
work in this task). Mac CPU, saved evidence only. All labelfix tests green, none weakened. Read
`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_review_1.md` and its `ASTRA-SC1c3_evidence/` (incl. `test_c3_scope.py`) first.

**Principle (track lead, after three review cycles):** prefer the simplest conservative rule over a clever relevance predicate. When in doubt,
HOLD. Do not add new relevance logic.

## Fixes
1. **C3-B01 (blocker):** for any slot whose base is uppercase OR whose saved physical case/band is capital (either signal), ANY recorded top
   clipping holds the slot (the L1E-baseline behaviour) — no capital side-zone relaxation. Keep SF3's clipped_bottom relevance only for
   lowercase letters that cannot carry a below-mark AND have no below-mark predicted by any signal; keep SF3's lowercase clipped_top rule only if
   the saved geometry establishes clearance of the WHOLE upper mark zone (overhead and preposed); otherwise HOLD. An empty A/B prediction never
   removes a zone from the observation requirement.
2. **C3-M01:** one bound runtime/evidence envelope (all saved peers A, B, E and every relevance input) passed through every adapter, including
   the owner-page builders; parity test with DIFFERING diagnostic-peer predictions (the review's ι/clipped_bottom/E=subscript witness).
3. **C3-N01:** consistent punctuation/letter classification across slotting, rendering and K1 for every declared elision alias (U+02BC
   included); exercise every alias through actual composition.
4. **C2-N02 residual:** `scripts/labelfix/owner_implicit_changes.py` requires and verifies a notes-to-reviewed-page binding (as
   `box_regression.py` does) before emitting approval language.
5. Every failing test in `ASTRA-SC1c3_evidence/test_c3_scope.py` becomes a repository test (fails on the SF3 head, passes now).

## Report
Held-out table (PRESENCE / FULL / ENSEMBLE_AB / ENSEMBLE_AE) SF3 → SF4 with per-slot proof that wrong/new did not increase, and the hold-reason
table. `SF4_REPORT.md`, last line:
`SF4 RESULT: C3-B01/M01/N01 + C2-N02 residual fixed; review witnesses as tests <n>/<n>; AB held-out lines held 256→…, corrected 49→…, wrong 2→…, new 6→…; tests <n> passed`.
