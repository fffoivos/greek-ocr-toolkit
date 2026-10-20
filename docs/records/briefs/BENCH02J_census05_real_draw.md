# BENCH02J: the census_05 real draw for benchmark 0.2, and staging candidates for the P6 readout (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend, no jobs)

census_05 is complete. The coordinator ran the bench02 extract on it (job 3704816, package `bench02_pkg/0019ce4b`) and copied the outputs to `docs/harvest/collect_v3_admission/bench02/census05/`:
- `tags.jsonl.gz`: 27,990,456 bytes, sha `8b5fc9d3acccd12572d744e35984b0e89c50df1901ac066ed0bc8c2d5840f553`;
- `tags.jsonl.receipt.json`: decisions 320,479, diagnostics 67,077, joined 67,077, diagnostic join 1.0.

This is the **real draw** under the ruled production defaults (BENCH02I):
- admitted rows only;
- 50 per class × edition, fair round-robin;
- the forced editions' non-locked rows are drawable, and the locked lqb_truth_v1/n1_locked_eval rows are never drawn;
- 20% overdraw.

**Change no code and pass no flags.** If the run fails, stop and report; do not fix it. A separate CROPS4B Sol run is working in `crops4/` at the same time: do not touch `crops4/` or `docs/briefs/CROPS4B*`.

## Do
1. **Check the receipt:**
   - `shasum -a 256` of tags.jsonl.gz equals the receipt's `tags_sha256`;
   - its bytes equal `tags_bytes`;
   - the decision count is 320,479, matching SPLIT2;
   - diagnostics equal joined, which equals dev 7,007 + test 60,070 = 67,077. Report any difference.
2. Run `bash docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh` exactly. Its output goes to `bench02/census05/` (candidates.jsonl, counts.json, COUNTS.md, draw_plan.json). Run it a second time into a temp directory and confirm `candidates.jsonl` is byte-identical (determinism). Then delete only that temp directory.
3. Write `bench02/census05/DRAW_CENSUS05.md`, using the same table as `census03/DRYRUN_V2.md`, per split × class:
   - pre-filter and eligible supply, quota, target, drawn, credited, deficit;
   - editions, sources, top-edition share, and the ≥10 books / ≥3 sources diagnostic.

   Also give:
   - **totals:** test credited /2,460, drawn /target; dev credited /615; classes filled test k/16 and dev j/16;
   - **deficits by class**, with the reason in the tool's own words: no supply, Serbian-only, and so on. Where a deficit class had supply on the census_03 upper bound, say so in one column;
   - **the pool:** admitted rows by split, rows added by the forced non-locked pool, and locked rows excluded (count);
   - **candidates.jsonl:** path, sha256, bytes, line count; the draw_plan.json sha; the series-cap note (unverifiable without series identity).
   - Report numbers only, without recommendations.
4. **Stage the candidates for the P6 readout.**
   - `rsync` `candidates.jsonl` to the new Clariden directory `$W/filter_pipeline_20261018/bench02/census05_draw/` (`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`). The directory must not already exist; create it. Overwrite nothing.
   - Read the sha back remotely; it must equal the local one.
   - Confirm read-only that `$W/filter_pipeline_20261018/bench02/census05_readout` does **not** exist.
5. In DRAW_CENSUS05.md, give **the exact readout submit line**, for the coordinator to run. Do not run it.
   ```
   export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
   cd $W/filter_pipeline_20261018/bench02_pkg/0019ce4b && bash docs/harvest/collect_v3_admission/bench02/submit_job.sh readout "$W/census_05_20261020/attempts/full-split-001" "$W/filter_pipeline_20261018/bench02/census05_readout" "$W/filter_pipeline_20261018/bench02/census05_draw/candidates.jsonl"
   ```
   Check it against `submit_job.sh`, `readout.sbatch` and `bench02_draw.py readout` in the deployed package:
   - the argument order;
   - the census directory form: the extract used the attempt directory, so check the readout resolves the same `decisions.jsonl`/`evaluation_diagnostics.jsonl` symlinks;
   - the time limit, 01:00:00;
   - the expected outputs, `candidates_readout.jsonl` + log.

   Correct the line if anything differs, and say what changed.
6. Guarded commit list:
   - `bench02/census05/`: everything except `tags.jsonl.gz`, which stays out of git with its sha recorded. Keep candidates.jsonl in git only if ≤ 5 MB;
   - this brief.

The last line must be exactly:
`BENCH02J: done | census_05 draw test <a>/2460 dev <b>/615 classes test <k>/16 dev <j>/16 | deficits <class:n,...> | candidates <lines> sha <sha8> staged <remote path> sha ok | deterministic yes | no jobs submitted`
