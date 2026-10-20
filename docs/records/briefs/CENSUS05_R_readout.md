# CENSUS05-R: the census readout script for checkpoint P4 (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no census; no Slurm)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead commits.
- Output: `docs/records/harvest/census05/readout/`.
- Edit nothing outside it. Read only: `docs/harvest/seg_census/` (including the untracked `mock_batch/`), `docs/harvest/seg09/`,
  `greekocr/`, `tests/`.

## Why

Census_05 (night plan step P3) reruns the whole filter pipeline on the five census_03 parents (592,466 rows). Checkpoint P4 is an
Astra review of its numbers. Astra needs one script that turns a finished census run into a complete, checkable count report.
The script must run on Clariden, inside a Slurm job, on the full output (census_03's `decisions.jsonl` was 8.9 GB), so it must
stream: never load a whole file into memory.

**Read first:**
- the census output layout, from the mock runs: `docs/harvest/seg_census/mock_batch/mode-i-removed/` (`CURRENT.json`,
  `current/`, `generations/`, `decisions.jsonl`, `summary.json`, `admission_records.jsonl`, `admitted_train.jsonl`,
  `pending_*.jsonl`, `evaluation_diagnostics.jsonl`, `runtime.json`, `progress.json`) and
  `mock_batch/W/filter_pipeline_20261018/census_04_seg08/{mode-i,mode-ii,smoke-mode-i,smoke-mode-ii}/`;
- the writer of those files: `greekocr/harvest/line_pipeline_census.py` (`Ledger`, the export and summary code), and
  `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py`;
- the decision record and reasons: `greekocr/harvest/line_pipeline.py` (`finish()`, `content_gate_exclusion`,
  `short_line_exclusion`, `final_eligibility`, `automatic_result`), and `docs/harvest/line_pipeline/README.md`;
- `docs/harvest/seg_census/HANDOFF_SEGCENSUS1.md` and `remote_evidence/validation.json` (census_03 inputs: 592,466 rows, five
  parents).

## The script

Write `docs/records/harvest/census05/readout/census_readout.py`: stdlib only, Python 3.6-compatible syntax (the Clariden login Python is
3.6; inside the job the uenv Python is newer, but the script must run under both). Its usage:

```
python3 census_readout.py --run <attempt dir> --out <dir> [--baseline <census_03 summary.json>] [--expect-rows <n>]
```

- It resolves the published generation through `CURRENT.json`, the same way the census does. It reads only that generation's
  files, and it records each file's path, bytes and sha256.
- It writes `readout.json` (every number, machine-readable) and `READOUT.md` (the same numbers as tables), and nothing else.
- It is read only on the run directory.
- It counts **only what the pipeline wrote**. Disposition and reasons come from the decision records. It recomputes no verdict
  and applies no rule of its own.

## What it reports

Every count is broken down by disposition (ADMIT / HOLD / DROP), and by `parent` and `split` unless stated otherwise.

1. **Completeness.**
   - Input rows per parent, from the run binding. Decisions per parent. Exactly one decision per (parent_id, row id).
   - Duplicates, missing rows, and rows with no reason on a non-ADMIT disposition, each listed (first 20) and counted.
   - With `--expect-rows`, a PASS/FAIL line against it.
2. **Gate counts.** The content gate's exclusions, before segmentation, by reason:
   - `mixed_script_word` (DROP), the foreign-script reason (HOLD), `short_line`, `single_character_cell`, `numeric_shape`,
     `cell_status_unresolved` (HOLD), and any other reason the gate stage carries;
   - per parent, per source, and per class;
   - and the check that every gate-excluded row has every route `not_run_due_to_prior_exclusion` (count the violations).
   Take the reason names from the code, not from this list. If a name differs, use the code's name and say so.
3. **Per reason, all stages.**
   - The first (deciding) reason of every non-ADMIT row: one table, reason × disposition, with the stage that produced it.
   - All reasons: one table, counting a row once per distinct reason it carries.
   - Segmentation reasons broken out, including the length band reasons.
4. **Per source and class.** ADMIT / HOLD / DROP per source × class (primary class / content role, exactly the fields the
   summary's `by_stratum` uses) × split. Also per source alone and per class alone, with admit rates.
5. **Pending queues.** Per correction tool: rows in `pending_<tool>.jsonl`, per source and per class, plus the HOLD reasons that
   send a row there.
6. **Admission and export.**
   - `admitted_train.jsonl` row count.
   - The V3 split counts (train / dev / test / unassigned).
   - Rows whose `pre_dedup_disposition` differs from `disposition` (deduplication effects), by reason.
   - Held-out protection: admitted rows whose crop is in the held-out crop list or whose edition is held out. This must be 0;
     count and list them.
   - Rows carrying a correction edit, per tool and per status.
7. **Versions.** The `pipeline_version` values seen, and the tool versions from the run binding. Any row with a different
   pipeline version is flagged.
8. **Against census_03** (only with `--baseline`): per parent and per disposition, census_03 → this run, with the delta. Search
   the repository read-only for a census_03 `summary.json` or equivalent counts (`docs/harvest/line_pipeline/clariden/`,
   `docs/harvest/seg_census/remote_evidence/`, the sol-recut and main-next trees, read only). Report what you found and use it in
   the tests. If none exists locally, say so: census_03's 65,900 admissions is the one figure on record, from
   `HANDOFF_SEGCENSUS1.md`.
9. **Invariants**, each with PASS/FAIL and a count:
   - the dispositions sum to the decisions;
   - `admitted_train` ⊆ ADMIT ∩ split train;
   - zero held-out leaks;
   - every gate-excluded row has no segmentation verdict;
   - the summary's `by_stratum` totals equal the counts recomputed from `decisions.jsonl`.

`READOUT.md` opens with a one-paragraph headline: rows, ADMIT / HOLD / DROP, admitted_train, the gate total, and the invariants
PASS/FAIL. Every table names the file it was counted from.

**Last line of `READOUT.md`:** `CENSUS READOUT: rows <n> (complete <yes|no>); ADMIT <n> HOLD <n> DROP <n>; admitted_train <n>; gate DROP <n> HOLD <n> (mixed <n> foreign <n> short <n> cell1 <n> num1 <n> unresolved <n>); pending <tool n, …>; heldout leaks <n>; invariants <k>/<k> PASS`

## Tests

`docs/records/harvest/census05/readout/test_census_readout.py`, run with
`~/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python -m pytest -q -p no:cacheprovider` and `PYTHONPATH=.`:
- on the real mock outputs, `mock_batch/mode-i-removed/` and the four `census_04_seg08/*` attempts: the script's totals equal
  each run's `summary.json` exactly;
- on a small synthetic run with every gate reason, a held-out leak, a duplicate, a missing row and a dedup change: each is
  counted and each invariant fails where it should;
- streaming: on a synthetic 600,000-row `decisions.jsonl`, peak memory (`resource.getrusage`) stays under 1 GB. Report the time
  and peak memory.
- Also run the script under the Mac's `/usr/bin/python3`, to check the stdlib-only, old-syntax requirement. If it is not 3.6,
  say which version it is and check the syntax with `ast` against `feature_version=(3, 6)`.

## Job

Write `docs/records/harvest/census05/readout/readout.sbatch`: normal partition, 1 node, 1 task, 16 CPUs, `00:30:00`. It takes the run
directory from `CENSUS05_RUN`, the output from `CENSUS05_READOUT_OUT`, and the bundle from `CENSUS05_BUNDLE` (an absolute path,
because Slurm runs a spooled copy). It uses the same uenv/srun shape as `docs/harvest/seg_census/jobs/common.sh`.
- Test it with the mock spool approach of `docs/harvest/seg_census/mock_batch.py`: copy the script to a spool, run it from an
  unrelated cwd, and double `srun` only.
- No `sbatch` is invoked.

## Report

Write `docs/records/harvest/census05/readout/REPORT.md`:
- the files written, the test counts verbatim, the timings;
- the readout of `mock_batch/mode-i-removed/` as an example;
- whether census_03 counts exist locally;
- a scope guard: the changed files with sha256, all inside `docs/records/harvest/census05/readout/`;
- a receipt.

**Last line:** `CENSUS05-R READY: script <sha8>; sbatch <sha8>; mock totals = summary <k>/<k>; synthetic invariants <ok>; 600k rows <s> s peak <MB> MB; census_03 baseline <found at X|absent>; tests <n> passed <n> failed`
