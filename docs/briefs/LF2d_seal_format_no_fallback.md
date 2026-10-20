# LF2d: revised replacement ruling (no source fallback) + seal02 FINAL_LIST format (gpt-6.1-sol, medium; network OFF; no .git writes; no reading)

Continues LF2c (`docs/labelfix/spellcheck/LF2C_REPORT.md`). Add no rule, guard, threshold or heuristic of your own.

1. **Revised ruling (coordinator, 20 Oct ~06:05, supersedes the fallback line in LF2b/LF2c):** a flagged in-quota line is replaced ONLY by
   the next unused reserve line by `overdraw_order` with the same `quota_scope` AND the same source. When that reserve is exhausted the
   line is `UNFILLED` (reported, never promoted from another source). Remove `FALLBACK_SOURCE` from `prod_finalize.py` and its tests;
   a non-OK reserve line is still marked used and never promoted.
2. **Seal format:** read `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seal02/FINAL_LIST.schema.json`
   (sha256 `ec430f1460fa9d35ccc581ee9408efdf6be03a69e73d14765563520d7ebf972f`, sourcing commit e6365239b; also `SEAL02.md`,
   `build_suite02.py`, `test_seal02.py` there, read-only) and emit exactly that format. Expected (coordinator's summary; the schema wins
   on any difference, say where):
   - final list row `{parent_id, row_id, split, quota_scope, lf1_verdict: "OK", replaces: null | {parent_id, row_id},
     lf1_receipt_ref: {verdicts_sha256, line_id}, mock: false}`;
   - receipt `{status: "FINALIZED", mock: false, final_list_sha256, verdicts_sha256, candidates_sha256:
     "0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2", counts: {flagged, REPLACED, UNFILLED}}` with
     flagged = REPLACED + UNFILLED;
   - three files for the seal bind: the final list, its receipt, the merged verdicts, each with its sha256.
   Keep the LF1 per-replacement record (flag reason) in a side receipt if the schema has no field for it.
3. Validate a synthetic end-to-end output against the schema, and run sourcing's seal-side checks on it if they can run locally
   read-only (e.g. the schema/foreign-source checks in `build_suite02.py`/`test_seal02.py`); say which ran. Do not finalize real data
   (batch 2 is not read yet). Update `artifacts/lf1/prod/PROD_PLAN.md`.

Report `docs/labelfix/spellcheck/LF2D_REPORT.md` with LEAD_COMMIT_PATHS. Final line:
`LF2d READY: tests N passed; fallback removed; seal schema valid on fixture (seal checks ran: …)` or `LF2d STOPPED: <reason>`.
