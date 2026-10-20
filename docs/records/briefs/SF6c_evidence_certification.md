# SF6c — Fix SF6's evidence certification (ASTRA-SC1c3v3 B01, B02) (gpt-6.1-sol, xhigh, network OFF)

Workspace/rules: as `docs/records/briefs/SF6_two_signal_deletions.md` + `SF6b_breathing_move.md` (read both). Head = this commit (SF6b 8c5ad361 +
the NOT CLOSED review). No `.git` writes; other worktrees read-only; saved evidence only. All labelfix tests green, none weakened. **Fix only
the two findings; the SF6 rule, the SF6b MOVE exception and everything else stay as they are.** Policy id stays `sf6-release-v1`; bump the
policy binding/sha and state it.

## Findings (read `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_review_1.md` and its evidence)
- **B01:** `ctc_align.py:89` loads a missing `recognition_confidence` as `0.0`; `m2_run.py:127` (and any other runtime writer, incl. the
  Clariden L1 runtime builders) passes it into the runtime; `release_gate.py:394` accepts any finite value in [0,1]. A missing score becomes a
  positive absence. Fix: a missing score must stay missing end to end (None / explicit `scored: false` with provenance), and the gate's
  recogniser absence requires an explicitly scored confidence; decide and state whether a genuine score of 0.0 can ever be "positive" (the
  safe reading: no — require a score above a stated floor, justified from the saved evidence distribution, else HOLD).
- **B02:** ordinary reader (lines ~367–379) and recogniser (~395–397) absence checks only test `_finite_span`; they must also require the
  span inside the image and covering the saved target letter window (as the MOVE path does at ~339–341). Use one shared helper so the three
  paths cannot drift.

## Witnesses
The reviewer's executable tests `ASTRA-SC1c3v3_evidence/test_sf6_reviewer.py` (12 failed / 63 passed on 8c5ad361) become repository tests:
all must pass after SF6c; `unsafe_release_witnesses.json` cases must HOLD. Check every existing runtime source on disk (held-out, M2 dev,
witnesses, the L1 Clariden runtime format) for how missing confidences are represented, and state the effect (lines newly HOLD).

## Report
Append an "SF6c" section to `docs/records/labelfix/spellcheck/SF6_REPORT.md`: diffs, the confidence floor and its justification, held-out/M2/witness
tables before (SF6b) / after, reviewer tests 75/75. Last line:
`SF6c RESULT: B01 fixed <yes|no> (floor <x>); B02 fixed <yes|no>; reviewer tests <k>/75; held-out AB corrected <..>, wrong <..>; tests <n> passed; policy sha <..>`.
