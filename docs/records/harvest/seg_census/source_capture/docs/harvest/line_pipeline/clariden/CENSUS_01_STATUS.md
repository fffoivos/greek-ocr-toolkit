# Full filtering census — job 3693052

Owner-authorized on 2026-10-19 Europe/Athens. Slurm accepted the prepared command at 2026-10-18T21:09:29Z (2026-10-19 00:09:29 Athens).

- Scope: diagnostic filtering of all 592,466 bound input records; no model training.
- Runtime: census 0.4, scientific pipeline 0.3, accepted segmentation 0.5 unchanged.
- Source: `6261c3f58cc80e1bbfe70e35120aa9d9e8c388fa0dbc0a8f62f17a8d1045bf35`.
- Configuration: `9d7e6c0607e96628aac40415d11201fbd97f4ade9157c4043fcd2990c0131600`.
- Resources: one normal-partition node, account a0140, 256 task CPUs, 64 native workers, factor 64, six-hour allocation ceiling.
- Forecast: 2–3 processing hours after startup, plus queue time; not a measured full-population duration.
- Native log: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/logs/census_3693052.log`.
- Output root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_01`.
- Terminal state: FAILED after 62 seconds. Started 2026-10-19 00:11:35 Athens; ended 00:12:37. Startup tests/policy parity passed; original dev registration encountered legacy split `val`. All 214,436 train rows were registered, zero image-filter decisions produced.
- Recovery: explicit parent-confirmed `val` → `dev`, `reserved` → `test` adapter repair; frozen evaluation cohorts remain evaluation-only. New source and fresh output root required; failed ledger retained. Full input preflight is job 3693098.

[Submission receipt](census_01-submission.json) · [Scheduler observation](census_01-status.json) · [Bound plan](full-run-plan.json)

The launch script is the exact historical command used, not a resumable controller. Do not rerun it blindly: reconcile job 3693052 and its ledger first. Automatic training admission remains evidence-gated as described in the readiness report.
