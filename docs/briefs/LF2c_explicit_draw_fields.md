# LF2c: finalize from sourcing's explicit draw fields (gpt-6.1-sol, medium; network OFF; no .git writes; no reading)

Continues LF2b (`docs/labelfix/spellcheck/LF2B_REPORT.md`). Sourcing emitted the explicit fields, which supersede the coordinator's
rank-based rule in LF2b §A:
`~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl`, sha256
`0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2`: the same 3,341 rows in the same order as 70a29c20 (lead-checked),
with `quota_scope` (= split:class[:subgroup]), `scope_rank`, `in_quota`, `overdraw_order`. Expected: in-quota test 2,340 / dev 453;
reserve test 468 / dev 80.

1. `prod_finalize.py` and the adapter read in-quota membership and reserve order ONLY from these fields (no derivation from rank or
   quota). Rule (coordinator, binding): a line passes only with verdict `OK`; a flagged in-quota line is replaced by the next unused
   reserve line by `overdraw_order` within the same `quota_scope` and the same source; if that source is exhausted, the next within the
   same `quota_scope` (`FALLBACK_SOURCE` in the receipt); none left → `UNFILLED` (scopes with zero reserve report every flagged line as
   UNFILLED). A non-OK reserve line is marked used and never promoted. Record every replacement with its flag reason.
2. Keep the LF2b rank-based path only if tests depend on it; production uses v3. Point the adapter's draw input at v3 and record its sha
   in the receipts. Verify the in-quota/reserve counts above and that v3's rows and order equal 70a29c20.
3. The 576 W1 packs built in LF2b stay as they are if the bed rows and labels are unchanged by the switch (prove it: same line ids and
   label shas); otherwise report, do not rebuild.
4. Update tests (fixtures with explicit fields; zero-reserve scope → UNFILLED; fallback; non-OK reserve; test/dev isolation) and
   `artifacts/lf1/prod/PROD_PLAN.md`.

Report `docs/labelfix/spellcheck/LF2C_REPORT.md` with LEAD_COMMIT_PATHS. Final line:
`LF2c READY: tests N passed; v3 in-quota 2340/453 reserve 468/80; W1 packs unchanged yes|no` or `LF2c STOPPED: <reason>`.
