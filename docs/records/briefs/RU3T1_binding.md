# RU3T-1: bound-input change, then resume readiness (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

The RU3T driver (`scripts/secondary/reading/run_ru3t_all.sh`) stopped, correctly failing closed. The log is
`artifacts/ru1/ru3t/driver_resume1.log`: "bound input changed: scripts/secondary/ru2t_coverage.py". The first driver run completed
ctx01–ctx14 r1 and then exited, most likely on the same check.

**Do.**
1. Find what changed in `ru2t_coverage.py` and when: `git diff` against the committed version, plus the N1-TR receipt/brief, which
   may have edited it.
2. **If** the change is behaviour-preserving for RU2T/RU3T: prove it by re-running the RU2T and RU3T coverage tests and recomputing
   the coverage of the finished RU3T contexts, identical before and after. Then re-bind the new sha in the RU3T binding (`ru3t.py`
   inputs) and record the old/new sha and the proof in the receipt.
   **Otherwise:** restore the RU3T copy to the bound version, under a separate path if N1-TR needs the new one, so that each pipeline
   binds its own file.
3. Make the driver resumable: it skips finished contexts and runs a dry-run listing the remaining contexts.
4. Write the receipt `artifacts/ru1/ru3t/RU3T1_RECEIPT.json`. Do NOT run readings.

**Last line:** `RU3T1 READY: change <behaviour-preserving|restored>; contexts done <n>/38, remaining <n>; dry-run <ok>`
