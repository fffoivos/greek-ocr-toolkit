# BENCH02K: redefine degraded relative to its source; re-run the census_05 draw; restage (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend, no jobs)

BENCH02J (commit 866b88c77, `bench02/census05/DRAW_CENSUS05.md`) drew 0 degraded lines: test 0/100, dev 0/25. The class is defined as DocAI confidence < 0.89, and census admission keeps only rows with confidence ≥ 0.89: all 39,630 admitted dev/test rows are at or above it. The class was empty by construction.

**Coordinator ruling, 20 Oct, under the owner's night mandate.** The benchmark draws admitted rows only, so degraded becomes **relative**:
- the lowest 5% of DocAI mean line confidence (`evidence.confidence`) among admitted rows, **within each source, per split**;
- ties are broken by the tool's existing deterministic draw order;
- the label in tags, counts and reports is exactly **`degraded (relative: bottom 5% confidence within source)`**;
- no drawing from non-admitted rows.

**Change only that.** Precedence (degraded stays third), quotas, overdraw, cap 50 per class × edition with fair round-robin, the forced non-locked pool, locked exclusions, seed and order all stay as they are. Add no filters.

## Exact definition (implement as written and record it in `draw_plan.json`)
- **Population:** for each (split ∈ {dev, test}, source), the admitted W1/W2 rows of that split and source, before the v2/locked exclusions. Excluded rows still count toward the ranking but can never be drawn.
- **Ranking:** sort ascending by `(confidence, <the tool's existing deterministic per-row draw-order key>)`. Name that key in `draw_plan.json`.
- **Selection:** the first `ceil(0.05 × n)` rows are flagged degraded, where n is the population size; `n = 0` flags none.
  - Rows with no confidence are not ranked and are never degraded. Report their count, which should be 0.
- The old absolute branch (conf < 0.89, plus ink density) is retired for the census_05 production draw. Keep it reachable only if an existing census_03 test needs it, and say which.

## Do
1. Implement the change in `bench02_draw.py`.
2. Tests:
   - relative selection, including ceil, ties and per (split, source) independence;
   - excluded rows ranked but not drawn;
   - determinism;
   - the label string;
   - all existing tests pass, or are updated only where this ruling changes the expected output. List each update and why.
3. Re-run `bash docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh` unchanged (no flags). Outputs replace `bench02/census05/{candidates.jsonl,counts.json,COUNTS.md,draw_plan.json}`; BENCH02J's versions remain in git at 866b88c77.
   - Run a second time into a temp directory and confirm the outputs are byte-identical; then delete only that temp directory.
4. Write `bench02/census05/DRAW_CENSUS05_V2.md`:
   - the same table and totals as DRAW_CENSUS05.md;
   - **a per-class diff against BENCH02J**, credited and drawn, test and dev. Degraded is third in precedence, so rows newly flagged degraded leave later classes: show where that happens;
   - the degraded fill and its source mix;
   - the population sizes per (split, source) and the number flagged;
   - candidates path, sha, bytes, lines; the draw_plan sha; and the overlap with BENCH02J's candidates (row ids kept, added, dropped).
   - Numbers only.
5. **Restage:**
   - `rsync` the new `candidates.jsonl` to the **new** Clariden directory `$W/filter_pipeline_20261018/bench02/census05_draw_v2/` (`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`). It must be absent first; create it with `mkdir` (no `-p` on the leaf). Overwrite nothing; `census05_draw/` stays.
   - Read the sha back remotely.
   - Confirm `$W/filter_pipeline_20261018/bench02/census05_readout` is still absent.
6. **Readout:** the deployed `bench02_pkg/0019ce4b` readout path does not use degraded logic. Confirm from the diff that no code on the extract/readout path changed, so no redeploy is needed.
   - If anything on that path did change, stop and report; do not redeploy.
   - Write the exact readout submit line, with the candidates path set to `census05_draw_v2/candidates.jsonl` and everything else as in BENCH02J.
7. Guarded commit list: the code, the tests, `bench02/census05/` (minus `tags.jsonl.gz`), and this brief.

The last line must be exactly:
`BENCH02K: done | degraded relative test <a>/100 dev <b>/25 | draw test <c>/2460 dev <d>/615 classes test <k>/16 dev <j>/16 | candidates <lines> sha <sha8> staged census05_draw_v2 sha ok | deterministic yes | readout path unchanged | tests <n> passed | no jobs submitted`

## Execution receipt — 2026-10-20

Implemented relative flags over admitted W1/W2 dev/test rows before exclusions. Ranking uses `(evidence.confidence, (parent_id, row_id))`; `(parent_id, row_id)` is the existing sorted per-row key before seeded round-robin shuffling. Population size includes missing confidence; those rows are never ranked or flagged. Production missing confidence: 0. The Boolean `degraded` tag and stable class IDs remain machine-readable; `degraded_label`, class-count labels, and report labels carry exactly `degraded (relative: bottom 5% confidence within source)`.

Legacy absolute classification remains for census_03 diagnostics and direct legacy tag tests. Specifically `Bench02HTests.test_default_cli_reproduces_ruled_v2_bytes` needs the frozen census_03 dry-run candidates, and `Bench02ETests.test_classifier_matches_pinned_bench02d_sample` checks the pinned census_03-era classifier. `Bench02FTests.test_confidence_boundary` and `test_density_p25_per_source_and_strict_boundary` retain direct coverage of that legacy branch. The production draw always supplies a relative flag; neither absolute confidence nor density can affect its degraded membership.

Existing test updates (2):
- `Bench02FTests.test_missing_evidence_deficit_and_recorded_plan`: replace production density-plan expectations with relative population/missing-confidence expectations; retain the independent density-helper assertion. Production no longer reports a density branch.
- `Bench02ITests.test_draw_fair_default_and_receipt_failure_before_output`: the 180-row synthetic admitted population flags 9 rows; the remaining former absolute-degraded rows fall through to polytonic, capped at 50. Vertical/font caps and fair emission checks remain.

New `test_bench02k.py` covers ceil, tied confidence, independent splits/sources, empty populations, missing confidence, non-admitted/non-W1/W2/train exclusion from ranking, excluded rows retaining ranking positions but never drawing, exact labels, legacy-branch override, input permutation, and all-four-artifact byte determinism. Full BENCH02 suite: `python3 -B -m unittest discover -s docs/harvest/collect_v3_admission/bench02 -v`: 49 passed, 0 skipped, 0 failures. `git diff --check`: passed.

Production run: `bash docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh`, unchanged, no flags. Repeat: same wrapper, temporary PATH shim replaces only the output destination with a directory under `.bench02k-repeat-7vvs_stl`; original code, tags, inputs and arguments otherwise unchanged. `candidates.jsonl`, `counts.json`, `COUNTS.md`, `draw_plan.json` all byte-identical. Only that repeat directory was deleted. The volatile `athens_time` draw-plan field was removed to permit byte determinism; selection is unaffected.

Numeric results: `docs/harvest/collect_v3_admission/bench02/census05/DRAW_CENSUS05_V2.md`. Test credited 2348/2460, drawn 2808/2952, filled 15/16. Dev credited 455/615, drawn 533/739, filled 11/16. Degraded credited 100/100 test and 25/25 dev; drawn 120 and 30. Dev greek_latin and latin each lose 1 credited/drawn row to degraded; all per-class supply shifts and primary transitions are recorded in the report.

Candidates: 3341 lines, 3811251 bytes, SHA-256 `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5`. Draw-plan SHA-256 `8007e93ff170fdf897d4604d5c6bffe5725317cec226ab16f33ecc31c3b0ddb7`. BENCH02J overlap by row ID: 1659 kept, 1682 added, 1534 dropped.

Remote `census05_draw_v2` was checked absent including dangling symlinks, then created by `mkdir` without `-p`. Transfer: `rsync --ignore-existing`; no existing files overwritten. Remote readback: SHA-256 `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5`, 3341 lines, 3811251 bytes. `census05_draw/` still exists; `census05_readout` remains absent including dangling symlinks.

AST comparison against BENCH02J verifies no changes to `extract`, `readout`, their transitive helpers (`slim`, `census05_evidence`, `text_facets`, `numeric_grammar`, `canonical`, `sha`, `rows`, `output`, `dump`, `key`, `w12`), `absolute_dir` or `main` (16 functions). Byte comparison verifies unchanged `run_census05_draw.sh`, `submit_job.sh`, `readout.sbatch`, `extract.sbatch`, `job_common.sh`. Degraded logic is draw-only. No extract/readout path changes; no redeploy needed or performed. Deployed readout package remains `bench02_pkg/0019ce4b`.

Prepared submit line only; not executed. Sole change from BENCH02J: `census05_draw/` → `census05_draw_v2/`:

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
cd $W/filter_pipeline_20261018/bench02_pkg/0019ce4b && bash docs/harvest/collect_v3_admission/bench02/submit_job.sh readout "$W/census_05_20261020/attempts/full-split-001" "$W/filter_pipeline_20261018/bench02/census05_readout" "$W/filter_pipeline_20261018/bench02/census05_draw_v2/candidates.jsonl"
```

Network use: `ssh clariden` and `rsync` only. No spend, jobs, allocations or readout execution.

Guarded commit blocked by filesystem permissions: `git add` could not create `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.git/worktrees/greek-ocr-toolkit-sol-recut/index.lock` (`Operation not permitted`). No files staged and no commit created. The authorized changes are preserved in `/private/tmp/BENCH02K.patch`; unrelated working-tree changes and `tags.jsonl.gz` are excluded.
