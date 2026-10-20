# BENCH02H: diagnostic sweep — benchmark 0.2 feasibility by edition cap and pool (gpt-6.1-sol, medium, network OFF, no spend)

**Why:** the census_03 dry draw (BENCH02G, `bench02/census03/DRYRUN_CENSUS03.md`) shows that benchmark 0.2 is structurally infeasible as specified:
- SPLIT2's test side is **49 non-forced editions (7,602 rows) + 99 forced editions (52,468 rows)**. The forced ones are 53 `lqb_truth_v1` editions (43,290 rows) and 46 `n1_locked_eval` editions (9,178 rows). §3.3 excludes them.
- The dev side is 52 editions (7,007 rows).
- With a **4-lines-per-edition** global cap, test can never exceed 49 × 4 = 196 lines (quota 2,460), and dev 208 (quota 615).

The coordinator and owner need numbers to choose a fix. This is a **diagnostic**: the production defaults (cap 4, forced editions excluded) must stay unchanged.

## Do
1. Add two diagnostic-only CLI options to `bench02_draw.py draw`:
   - `--edition-cap N` (default 4) and the matching series cap scaling (default 12 = 3 × edition cap; keep 12 unless the option is given);
   - `--pool-include-forced {none,n1,lqb,both}` (default none). When on, the named forced-test editions join the TEST pool, **excluding their exact locked rows**: the row ids in the registered locked/eval files (lqb_truth_v1 rows, n1_locked_eval rows) are never drawable. Only the other rows of those editions become eligible. Report how many rows each pool adds.
2. The sweep: for each combination, run on the census_03 tags under **two pool rules**:
   - **(i) dry** = the sole split-reason pool, as in BENCH02G;
   - **(ii) upper bound** = all W1/W2 rows in the split regardless of census verdict, labelled UPPER BOUND (not admitted). This approximates what census_05 can at most supply.
   The combinations are edition cap ∈ {4, 12, 25, 50, 100, unlimited} × pool ∈ {none, n1, lqb, both}.
3. For each combination report:
   - test/dev candidates credited vs 2,460/615;
   - classes filled (test/dev, out of 16);
   - total and per-class deficits;
   - distinct editions and sources drawn per class (the ≥10 books / ≥3 sources diagnostic);
   - the max lines from one edition;
   - the share of test lines from the top 5 editions.
4. Write `bench02/sweep/SWEEP.md` (tables + a short "smallest change that fills ≥ 14/16 classes in the upper bound" line) and `sweep.json`. Do not recommend beyond the numbers; the lead does.
5. Tests:
   - defaults unchanged (BENCH02G candidates reproduce byte-identically with no new flags);
   - locked rows are never drawable under any `--pool-include-forced`;
   - caps respected at every N.

Write a guarded commit list (bench02 code + tests + sweep/ + this brief). The last line must be exactly:
`BENCH02H: done | upper bound cap4/none test <a> dev <b> | best <cap>/<pool> test <c>/2460 dev <d>/615 classes <k>/16 | defaults unchanged | tests: <n> passed`
