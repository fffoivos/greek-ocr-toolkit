# SF6 — Release gate: deleting any Google character needs two positive absence signals (gpt-6.1-sol, xhigh, network OFF)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head = this brief's commit on 05f2dafb = SF5 + its CLOSED
verification). No `.git` writes; do not touch other worktrees (`…-l1r2` is packaging the SF5 recompose — leave it alone; `…-s8` is being read
by print readers — read-only). Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.
Mac CPU; no detector/R1/CTC inference — saved evidence only. All labelfix tests green, none weakened; the rule gets witness tests that fail on
05f2dafb and pass after. **Change exactly one rule** (coordinator: reopens review; same reviewer thread verifies SF6 only). Policy id
`sf6-release-v1`. A partial `docs/records/labelfix/spellcheck/SF6_evidence/` from an aborted first run (old rule reading) exists: move it to
`SF6_evidence_aborted_run1/` and do not reuse anything from it.

## Why
SF5 fixed consensus elisions, but a deletion of a Google character on the strength of ONE absent source is still the unobserved-as-absent
pattern (C2-B01): the residual `Ι'.` → `Ι.` (numeral keraia, `a300f5e1c3f6a38d97201791-p000442-l0085`, recogniser lacks the sign), and the
leading opening quote removed when the detector sees none (ASTRA-SC1c3v2 out-of-scope note; probe cases in
`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v2_evidence/out_of_scope_quote_probe.json`). The coordinator's binding rule: any
keraia deletion triggers SF6.

## The rule (coordinator, exact)
A release may delete a character present in Google's label (combining mark, elision/other apostrophe, quote, numeral keraia, any other
character) only with **two positive signals that it is absent**: (reader AND detector) or (reader AND recogniser text). A single absent source
is **HOLD** for that line (not "keep and release" — HOLD, like the other uncertainty states).
- "Reader" = R1 (arms A and B together count as ONE signal: they share training data; the ensemble caveat). "Positive absence" means an
  observed, scored, in-window state that the character is absent — never a missing, unscored, clipped or uncertain state.
- **Apostrophes, quotes and numeral keraia** (coordinator ruling, 17 Oct — R1 has no head for them): the two positive signals are
  **detector absent AND recogniser text absent**, both observed, scored and in-window; anything less is HOLD. **Marks**: reader (A∧B as one)
  AND detector, or reader AND recogniser text, as above. Report the held-line count for punctuation deletions under this reading
  (held-out, M2 dev, witnesses), by class.
- Replacements count as deletions of the replaced character (e.g. acute → grave deletes the acute) unless the replacement is a pure elision
  alias (SF5's alias atom). Insertions are unchanged by SF6.

## Witnesses (repository tests)
1. The keraia line above → HOLD (not `Ι.`).
2. The leading-opening-quote class → HOLD where only the detector is absent (use the reviewer's probe cases + any saved lines you find).
3. A seeded 30 from the L1R2 deletion census when it lands (`~/Projects/greek-ocr-toolkit-spellcheck-l1r2/…/L1R2_REPORT.md` and its pulled
   census): make that a one-command addition (`--add-census <file>`); if it is absent at the end of your run, say "census witnesses pending".
4. Regression: every SF5 witness (56 lines) and the L1A audit lines keep their SF5 outcome unless SF6 turns a release into HOLD — list each.

## Report
Held-out tables before (SF5) / after (SF6) for all modes with the mark rows, the elision row, and a new **deletion row** (Google characters
deleted by class: mark / apostrophe / quote / keraia / other; and lines turned HOLD by SF6, by class). Same for the M2 dev pool. Any change in
the mark rows explained per slot. `docs/records/labelfix/spellcheck/SF6_REPORT.md`, last line:
`SF6 RESULT: policy sf6-release-v1; keraia witness HOLD <yes|no>; quote witnesses HOLD <k>/<n>; held-out AB corrected <..>, wrong <..>, new <..>, lines held <..>; single-source deletions released <a>→0; punctuation-deletion HOLDs <p> (apostrophe/quote/keraia …); tests <n> passed`.
