# LF4: finalize pairs flagged slots by scope_rank (gpt-6.1-sol, medium; network OFF; no .git writes; no reading)

The seal (SEAL02_FAIL "replacement must match split, class, scope, source and reserve rank") expects, within each quota_scope + source,
the flagged in-quota slot with the lowest `scope_rank` to receive the lowest-`overdraw_order` eligible reserve. `prod_finalize.py` walks
flagged slots in draw-file order instead; 13 of 73 groups (94 rows) cross. Coordinator GO (20 Oct ~07:00): pairing only.

1. `artifacts/lf1/tools/prod_finalize.py`: walk the flagged in-quota slots of each quota_scope + source in ascending `scope_rank`.
   Nothing else changes: the eligible reserve set, `overdraw_order`, same scope+source only, non-OK reserve never promoted, UNFILLED,
   vertical re-read override, VOID handling, schema and receipt format.
2. Tests: a fixture where draw-file order and scope_rank disagree, asserting the lowest-rank slot gets the lowest-order OK reserve; all
   existing tests pass.
3. Re-finalize with the exact PROD_PLAN §4 finalize command (inputs unchanged: candidates_v3 0432c56f…, `prod/line_verdicts_merged.jsonl`
   a203509c…, `prod/vertical_reread_verdicts.jsonl`), writing `prod/final_list.jsonl`, `finalize.receipt.json`, `finalize.details.json`,
   `finalize.bindings.json`. The previous outputs are copied in `artifacts/lf1/prod/v1/` (final list 75fe0dbc…).
4. Checks, written to `artifacts/lf1/prod/lf4_checks.json`: the (parent_id,row_id) row set equals v1's row set exactly; 2,691 rows;
   counts flagged 350, REPLACED 248, UNFILLED 102 identical to v1; only `replaces` (and the shas that depend on it) differ; number of
   rows whose `replaces` changed; the pairing rule holds in all groups; the seal-side check `build_suite02.final_checked` from
   `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seal02/` (read-only) accepts the new list if it can run
   locally on these files; say whether it ran. Any check failing: STOP and report; do not adjust.

Report `docs/labelfix/spellcheck/LF4_REPORT.md` with LEAD_COMMIT_PATHS and the three seal files' absolute paths + sha256. Final line:
`LF4 READY: tests N passed; rows 2691 set-equal v1; REPLACED 248 UNFILLED 102; replaces changed r; seal check ran yes|no ok` or
`LF4 STOPPED: <reason>`.
