# SF3 — Release-gate relevance: clipping and edit-guard holds (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head fd967dc4 = L1E). No `.git` writes. Network ON only to
re-run the held-out measurement on Clariden the way L1E did (read-only use of the deployed copy; never modify
`labelfix_l1_20261017/l1e_20261017/`, which job 3679545 is running from). Transient SSH errors: retry ≤ 3 with backoff; auth/cert error → STOP;
never refresh the cert. No detector/R1/CTC inference: decisions come from saved evidence. Mac CPU otherwise. All labelfix tests green, none
weakened; every rule change gets a witness test.

## Why
The complete SF2 gate holds 268/666 held-out lines under ENSEMBLE_AB (345 PRESENCE). Drivers (slots; lines held for that reason alone):
K1 260; detector_clipped_top 183 (28); edit_guard punctuation_mismatch 166; detector_clipped_bottom 127 (58);
segmentation_uncertain 114 (15); edit_guard unsupported character 99+66; A/B disagreement 75 (40); unnamed 64; localisation_unknown 44.
(`docs/records/labelfix/spellcheck/clariden/L1E_evidence/heldout_final/decisions.jsonl.gz`.) The safety principle stays (C2-B01: an unobserved zone is
never "no mark"), but a hold must be RELEVANT to the slot.

## Changes (coordinator, 17 Oct)
1. **clipped_bottom** holds a slot only if the letter can carry a below-mark (α η ω and their capitals, iota adscript cases) or a
   below-mark (subscript) is predicted by any signal at that slot. Elsewhere it is recorded but not a HOLD.
2. **clipped_top** holds a slot only if the cut actually intersects that slot's mark zone (per-x, from the detector's saved geometry:
   meanline / capital side zone and the crop top) for a mark-bearing letter (vowel, ρ, capital vowel's side zone).
3. **Edit guard:** examine every `punctuation_mismatch` and `unsupported_character` hold on the 666 character by character (list the
   characters and counts). For each class decide: genuinely unsupported (keep the HOLD — e.g. macron, Latin diacritics, double accents),
   representation-only differences that the policy should accept (e.g. apostrophe codepoint variants ' ᾽ ᾿ ’ in elision, quote variants,
   spacing), or a composer bug. Change only with a witness; never delete an unsupported printed mark.
4. Re-check K1's observation-based flags (`K1:observation:*`) for the same relevance logic.

## Report
The held-out table BEFORE (L1E final) and AFTER SF3 for PRESENCE / FULL / ENSEMBLE_AB / ENSEMBLE_AE (corrected / wrong / missed / HOLD
errors / new / lines held), plus the reason table after; any change in wrong/new must be explained per slot. Re-run the M2 cards (dev pool
only — never the locked stratum (ii)) through the gate before/after as a second table. `SF3_REPORT.md`, last line:
`SF3 RESULT: AB held-out lines held 268→…, corrected 46→…, wrong 2→…, new 6→…; PRESENCE 345→…; clipping holds …→…; guard holds …→…; tests <n> passed`.
