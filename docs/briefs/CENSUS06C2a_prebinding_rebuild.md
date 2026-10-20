# CENSUS06-C2a: rebuild the pre-binding package with C1 + kept_unverified reason split (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` only; no deploy, no jobs)

Base: CENSUS06-A/B (cf1db4dd4, 57ba1416b; deployed pre-binding `de597753a70a5d6d`) and C1 (672e981f2; local package 5de4fcd496663eae, not deployed). All in `docs/harvest/census06/`.

**Why now:** the coordinator's sf7 bind job (`bind_sf7.sbatch`) rebuilds the bound package **from the bundle it runs in**. So C1 and the change below must be in the deployed pre-binding bundle before the coordinator submits the bind job. This run builds it. A later C2a-deploy run deploys and verifies it after the lead commits.

## Coordinator ruling (20 Oct, ~13:50), binding on this run
- sf7 emits `kept_unverified` for two causes, which differ only in `evidence.reason`:
  - `"sf7 hold"` (expected ≈45–80% of routed rows);
  - `"sf7 out_of_scope"` (≈5–27%; the coordinator ruled it maps to kept_unverified, not HOLD).
- Other statuses expected: `applied` ≈1–2%, `verified_no_change` 8–35%, `failed` (no crop) 0–10%.
  - `failed` is already a valid wire status (`line_pipeline.py:288`).
  - It produces `correction_unresolved` (line 473).
  - Do not change that.
- Pipeline 0.3.3 already accepts any non-empty reason. **Do not change the pipeline or any digest.**

## Do
1. **Readout** (`readout/census_readout.py`, and any packaged copy that `jobs/readout.sbatch` runs):
   - Add a count of polytonic `kept_unverified` route results by `evidence.reason` × parent × split × disposition (class).
   - Use the exact reason string. Any other reason string is counted under its own key and listed. It does not fail.
   - Also report the totals per reason, and polytonic route status counts per parent.
   - Keep every existing invariant and output; this is additive.
2. **Flip report** (`flip_report.py`):
   - The `reason` attribution currently is `polytonic hold | polytonic edit | other`.
   - Split it so that a flip whose polytonic result is `kept_unverified` is attributed to `kept_unverified: sf7 hold` or `kept_unverified: sf7 out_of_scope` (the exact evidence reason).
   - `failed` and other unresolved statuses stay `polytonic hold`; edits stay `polytonic edit`.
   - Per parent and class (ADMIT-vs-not, admitted_train membership), both directions, as now.
3. **Binder** (`bind_sf7.py`):
   - Per-parent `status_counts` additionally gets `kept_unverified_reason_counts`.
   - No validation change, and coverage stays as is: the expected set is the census_05 `not_applied_out_of_scope` rows, and the 122,320 `not_run_due_to_prior_exclusion` rows are omitted.
4. **Carry C1 unchanged:**
   - the full-only `SBATCH_TIMELIMIT` / `--full-time` override;
   - the refusal when the projection exceeds 04:00:00 without a limit;
   - the smoke `CENSUS TIMING:` line.
5. **Tests:**
   - mock rows with both reasons, plus an unknown reason, through the readout and the flip report;
   - the binder reason counts;
   - the mock batch (smoke i / smoke ii / full ii invariants) with both reasons present;
   - all existing census06 + C1 + packaged regression suites green.
   - Delete your own pytest basetemp after a passing run; keep tests.log/tests.xml only.
6. **Package:**
   - Rebuild the pre-binding package locally: new id, DEPLOY_PATHS/DEPLOY_SHA256SUMS, package_id.json, payload_diff vs `de597753a70a5d6d`.
   - SF7 stays PENDING; `binding_state.py` and `submit_chain.sh` still refuse.
   - Update CENSUS06.md with a C2a section: what changed, the new id, and the coordinator block. The block is unchanged in procedure except for `CENSUS06_BUNDLE` = the new code dir, which C2a-deploy fills.
   - Write `C2A_COMMIT_PATHS.txt` (+ SHA256SUMS) of every file to commit.
   - Do not `git add` or `git commit`.

Touch nothing outside `docs/harvest/census06/` and this brief. Leave the unrelated dirty files (geometry_observations.py, row_inclusion.py, pyproject.toml, limit_probe.log) alone. Delete nothing else.

The last line must be exactly:
`CENSUS06-C2a: built | pre-binding package <id16> (C1 + kept_unverified reason split; not deployed) | readout + flip + binder reason counts | changed files <n> | tests <n> passed | basetemp deleted | no jobs submitted`
