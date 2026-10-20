# CENSUS06-C1: set the full census time limit from the smoke measurement (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` only; no deploy, no spend, no jobs)

The base is CENSUS06-A/B (commits cf1db4dd4 and 57ba1416b; `docs/harvest/census06/`; deployed pre-binding `de597753a70a5d6d`). The coordinator merged the pre-binding package into `cleanup` (bed6eb4db).

**Why:** the census runtime budget (`runtime_sizing.json`: 03:31:24 of 04:00:00) rests on an **assumed** sf7 rate of 250 records/s. The coordinator sets the full job's limit from the **smoke measurement**: full limit = projection × 1.5, capped at the partition maximum.

When the sf7 shas arrive, a later CENSUS06-C2 binds sf7, rebuilds and redeploys a new code id, and re-verifies. **This run only prepares the source changes that C2's rebuild will carry. Do not deploy anything.**

## Do
1. **An override for the full time limit, through the environment or an argument.**
   - `submit_chain.sh` (and any wrapper it calls) must honour `SBATCH_TIMELIMIT` and/or an explicit `--full-time HH:MM:SS` for the **full census job only**.
   - Check how REL3 did it: its block used `SBATCH_TIMELIMIT=01:30:00`. Slurm's `SBATCH_TIMELIMIT` overrides `#SBATCH --time`.
   - Default behaviour, with nothing set, is unchanged.
   - Smoke keeps its debug/00:30:00. Regression, parity, readout, bind and flip keep their packaged limits unless they are explicitly overridden.
   - **Refuse** a full submit without an explicit full limit **when the smoke readout's projection exceeds the packaged 04:00:00**, so that the job cannot be silently killed at the packaged limit.
   - Print the effective `--time` of every job that is submitted.
2. **Measure in smoke; project in the readout.**
   - The census job must record:
     - the wall time of the sf7 (polytonic) per-row file load: bytes, records, seconds;
     - the per-row decision throughput (rows/s, after the load).
     Record these in its timing/summary output. Use the census's existing timing hooks if they exist; otherwise add the minimum.
   - The smoke readout (and full readout) prints one line:
     `CENSUS TIMING: sf7 load <records> rec in <s> s (<rec/s> rec/s); decisions <rows> in <s> s (<rows/s> rows/s); projected full <HH:MM:SS> (load + 592466 rows / measured rate, + census_05 fixed overhead <s>); suggested limit ×1.5 = <HH:MM:SS> (partition max <HH:MM:SS>)`
   - **Derive the projection honestly.**
     - Smoke caps rows at 40 per parent; check whether it loads the **full** sf7 files (it should, because the binding is whole-file) and say so.
     - If the smoke per-row rate is not representative (native segmentation work differs, or the row mix differs), say so in the line and use the census_05 full measured time (job 3703989: 9,112 s for 592,466 rows) for the non-sf7 part, plus the **measured** sf7 load and the per-row sf7 lookup cost.
     - State the formula in CENSUS06.md.
   - Read the partition maximum for `normal` from `scontrol show partition normal` (read-only) and record it.
3. **Tests:**
   - the env/arg override reaches only the full census sbatch;
   - the refusal when the projection exceeds 04:00:00 and no limit was given;
   - the timing line parses from a mock smoke summary;
   - the regression and readout suites stay green.
   - Delete your own pytest basetemp after a passing run, keeping only tests.log/tests.xml. Delete nothing else.
4. **Package:** rebuild the package manifest locally so C2 can see the delta, but **do not deploy**. List the changed files and their patch (`timing_c1.patch`). Update CENSUS06.md and the coordinator block: smoke → read the TIMING line → set `SBATCH_TIMELIMIT` (or `--full-time`) = projection × 1.5, capped at the partition max → full.

Write a guarded commit list. Do not run `git add` or `git commit`. Touch nothing outside `docs/harvest/census06/` and this brief.

The last line must be exactly:
`CENSUS06-C1: done | full limit override (<mechanism>) full-only, refuses when projection > 04:00:00 without limit | smoke TIMING line (sf7 load + rows/s + projection) | partition max <HH:MM:SS> | changed files <n> (not deployed) | tests <n> passed | basetemp deleted | no jobs submitted`
