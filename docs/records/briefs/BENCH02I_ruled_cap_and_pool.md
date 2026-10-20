# BENCH02I: apply the coordinator's cap and pool ruling; re-run the census_03 dry draw (gpt-6.1-sol, medium, network OFF, no spend)

The base is the BENCH02H commit (bench02 with the `--edition-cap` / `--pool-include-forced` diagnostic options and `bench02/sweep/`).
- **Ruling (coordinator, 20 Oct, under the owner's night mandate): option (c), both, sized as below.**
- These become the **production defaults**: the census_05 run must be a path switch, with no flags.
- Change nothing else: precedence, thresholds, quotas and exclusion witnesses stay as they are. Add no filters.

## Rules
1. **The pool:** the non-locked rows of the 99 forced-test editions are drawable (`--pool-include-forced both` becomes the default).
   - The exact `lqb_truth_v1` and `n1_locked_eval` rows stay undrawable: the row ids from the registered locked files, hash-checked.
   - The other v2/locked exclusions stay as they were.
2. **The cap, per class × edition, with a fair allocation:**
   - The cap applies per (class, edition), no longer globally across classes.
   - Allocation inside an edition: round-robin over classes in precedence order, one line per class per pass. An early class can therefore never exhaust an edition.
   - The source → edition round-robin within a class is kept. Make the combined order deterministic and document it exactly in `draw_plan.json`.
   - The series cap scales as 3 × the edition cap per class (it stays unverifiable without series identity; report that).
3. **Choosing the cap:** the smallest value in **{12, 25, 50}** at which **every class with supply** reaches **≥ 90% of its quota** (test and dev separately) on the **all-rows upper bound** (BENCH02H's pool rule ii), with rules 1–2 applied.
   - "With supply" = upper-bound eligible supply > 0. Classes with no supply are deficits and do not block the choice.
   - If no value in the set meets it, choose 50 and list the classes below 90%.
   - Record the evaluation table in `bench02/sweep/CAP_CHOICE.md`. Set the chosen value as the default.
4. **Reporting** (counts.json + COUNTS.md, every run), per class and split:
   - credited vs quota;
   - the number of editions and sources used;
   - the **top-edition share** (largest single-edition count / class total);
   - the ≥10 books / ≥3 sources diagnostic.
5. **Deficits stay deficits, reported as before:** polytonic on census_03 (sf7 pending), bg/uk, historical Russian on test where no supply exists.
   - Label modern Cyrillic **"Serbian-only"** in the reports when only `sr` has supply.
   - Labels/notes only; no quota transfer.
6. **The extract receipt carries the tags sha:** `extract` writes the sha256 and bytes of `tags.jsonl.gz` into `tags.jsonl.receipt.json`.
   - `draw` verifies that sha when the receipt has one, and fails on a mismatch.
   - For census_03 (an old receipt without the sha), accept a `--tags-sha256` argument. Use `9f8f0c721766a95a10cece695726f8e9581214169f0fcde3abe46d3add46d26b` and check it.
   - Make `run_census05_draw.sh` require a receipt sha.
7. **Re-run the census_03 dry draw** with the new defaults into `bench02/census03/dryrun_v2/` (keep the BENCH02G `dryrun/` as it is). Report the same table as DRYRUN_CENSUS03.md, plus rule 4's columns, in `bench02/census03/DRYRUN_V2.md`.

## Tests
- Fair allocation: an edition with supply in 3 classes gives each its share before any class takes a second line, up to the cap.
- The per-class × edition cap is respected.
- Locked rows are never drawn.
- Determinism.
- The sha check in the receipt (match, mismatch, absent + argument).
- The existing tests keep passing, or are updated only where the ruled defaults change their expected outputs. List each one updated and why.

Write a guarded commit list. The last line must be exactly:
`BENCH02I: done | cap <N> per class×edition (fair) | pool +forced non-locked <rows> rows | census_03 dry v2 test <a>/2460 dev <b>/615 classes test <k>/16 dev <j>/16 | upper bound test <c> dev <d> | receipt sha check | tests: <n> passed`
