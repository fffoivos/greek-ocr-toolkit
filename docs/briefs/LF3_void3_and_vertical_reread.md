# LF3: third read for two VOID contexts + vertical_turned re-read tooling (gpt-6.1-sol, medium; network OFF; no .git writes; BUILD ONLY, the lead runs readers)

Continues LF2d / the W2 read (`docs/labelfix/spellcheck/LF1_W2_READ.md`). Coordinator rulings of 20 Oct ~06:20 (binding tonight; the
owner may override). Add no rule, guard, threshold or heuristic beyond them.

## A. One authorised extra fresh read (attempt 3) for `candidate_w2_00004` and `candidate_w2_00013` only

- `run.py`/`RUN_ALL.sh`: plumbing for an explicitly authorised extra attempt (e.g. `--extra-attempt <context>...`, recorded with
  `authorised_by: "coordinator 20 Oct (VOID is a reader-process failure)"`), a fresh context like attempt 2. Default behaviour unchanged
  (two attempts max). Ledger history of attempts 1–2 stays.
- If attempt 3 is VOID, the context is terminal: in mapping/finalize its bed lines are not OK (replace from the same quota_scope + source
  reserve, else UNFILLED) and the receipt states `no verdict (reader VOID x3)`, kept distinct from a flag (and VOID-twice elsewhere stays
  `no verdict (reader VOID x2)`).

## B. vertical_turned re-read (all batches)

Ruling: that class IS rotated text by design, so orientation alone is never a violation there. "Turned" in the owner's rule means a
horizontal line cut askew, not a vertically printed line.

1. Prompt `artifacts/lf1/prompts/lf1_vertical.md` = `lf1.md` unchanged plus ONE added block, verbatim:
   "This class is printed vertically. Judge after mentally reading along the text direction. Flag only clipping, more than one line,
   more than 2 whole neighbour words, or text that differs from the ink." Keep every pack rule (no `-rotate`, no zoom overwrite,
   literal relative paths only, only `answers.jsonl` + `zoom/**`). List the added lines in the report.
2. Pack builder for the re-read: every bed card with `draw_class == vertical_turned` from given rosters (W1a, W2 now; W1b later),
   same crop bytes and labels as the first read, new opaque ids, seeded, ≤50 bed per context. Controls: the frozen pool minus
   `lf1-control-turned` (its expectation, a turned horizontal line, is undefined under the vertical statement; record the omission),
   so 5 controls per context, same scoring. Roster `artifacts/lf1/candidate_contexts_vert_<batch>.json`, prefix `candidate_vert_<batch>_`.
   The runner must use `lf1_vertical.md` for these contexts (a per-roster prompt field; default prompt unchanged).
3. Verdicts: the re-read writes a SEPARATE file (`artifacts/lf1/prod/vertical_reread_verdicts.jsonl`, line_id → first verdict and
   re-read verdict, both kept). Mapping/finalize: for `vertical_turned` lines the re-read verdict decides; the first verdict stays in the
   record. A vertical line with no re-read verdict (VOID) follows A's terminal rule.
4. Expected now: count the vertical_turned bed cards in W1a + W2 (including the two VOID contexts once read) and the contexts that gives.

Tests on synthetic fixtures (extra attempt only when named; VOID x3 receipt text; vertical builder selects only that class, drops only
the turned control; per-roster prompt; override in finalize, both verdicts kept). All existing tests pass. Update
`artifacts/lf1/prod/PROD_PLAN.md` with the lead's exact commands: (1) the attempt-3 run, (2) the vertical build + run for W1a+W2,
(3) the same for W1b after its read, (4) finalize + the three seal files.

Report `docs/labelfix/spellcheck/LF3_REPORT.md` with LEAD_COMMIT_PATHS. Final line:
`LF3 READY: tests N passed; extra-attempt plumbing; vertical prompt +1 block; vertical cards now v (contexts c)` or `LF3 STOPPED: <reason>`.
