# Census_04 job kinds

Census_03 is one monolithic pipeline job, **3695426**. The actual measured steps are regression, frozen-policy parity, and the census. Native filter workers are in-process workers (64, prefetch 64), not independent Slurm shards. Corrections are imported canonical ledgers; no correction reader shard is launched. Composition, merge, admission, deduplication and export execute in the census job. There is no measured independent correction/merge shard runtime to cite or invent.

| Batch script / kind | Partition | Nodes | Tasks | CPUs/task | Census_03 elapsed | New time limit | Margin over measured step |
|---|---|---:|---:|---:|---|---|---|
| jobs/regression.sbatch | normal | 1 | 1 | 256 | 00:00:13 | 00:05:00 | 00:04:47 |
| jobs/parity.sbatch | normal | 1 | 1 | 256 | 00:00:01 | 00:05:00 | 00:04:59 |
| jobs/census.sbatch (filter + correction import + merge/admission/export) | normal | 1 | 1 | 256 | 01:49:19 | 04:00:00 | 02:10:41 |

Evidence: [Slurm accounting](remote_evidence/accounting_and_config.txt) lines 1–8; [original batch script](remote_evidence/census03.sbatch); [runtime.json](remote_evidence/runtime.json). Whole job elapsed was 01:49:40; the retained four-hour census budget also exceeds that by 02:10:20. These are inherited budgets with margin, not a new 0.8 runtime forecast. The census_03 native worker-seconds sum was 110636.3227; filtering/export wall time was 6198.5689 seconds. No standalone shard measurements exist.

The three scripts use the same environment/srun shape as census_03 and execute independently. The coordinator chains regression → parity → census with `afterok`. The new parity job replays 0.8 saved 150+888 evidence; census_03's 0.5 parity script is kept byte-identical in the baseline package but cannot check the changed policy.

`E4_SMOKE=1` derives up to 40 rows per parent (up to 200 for the five production parents), retaining literal row records, subsetting the original correction ledgers and recording source hashes. `E4_SMOKE=0` retains all input paths, hashes, counts, metadata, policy and correction releases exactly. Regression/parity cover their complete bounded fixtures in either setting. Both use the listed resource limits.

All outputs, caches and temporary directories live under `$W/filter_pipeline_20261018/census_04_seg08/<attempt>/`. `CENSUS04_BUNDLE` is an absolute deployed bundle path, required in the coordinator's commands because Slurm executes a spooled copy of each script. Local tests copy the real scripts to a mock Slurm spool, start in `/private/tmp`, execute the real config/CLI entry points, and assert every `srun` working directory and output root. Only `srun` and native image/reader I/O are doubled; no `sbatch` executable is invoked. [Batch results](mock_batch_results.json).

No Slurm job was submitted, no `--test-only` check was run, and no deploy occurred in SEGCENSUS-1c.
