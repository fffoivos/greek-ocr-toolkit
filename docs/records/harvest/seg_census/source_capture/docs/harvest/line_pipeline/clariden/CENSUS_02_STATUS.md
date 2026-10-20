# Repaired full filtering census — job 3693110

Started **2026-10-19 00:24:17 Europe/Athens** (2026-10-18T21:24:17Z), normal partition, one node, 256 task CPUs, 64 native workers, factor64, six-hour limit. Diagnostic filtering only; no training launched.

Scope:592466 input records. Census0.5 repairs legacy evaluation split aliases; pipeline0.3 and segmentation0.5 unchanged. Before launch, all records passed actual registration/indexing in debug job3693098, and Astra approved the repaired source. The earlier job3693052 failed during registration and produced zero native decisions; it is preserved.

Expected completion: approximately **02:25–03:25 Athens**, conditional on the measured 2–3-hour processing forecast. This is not a full-population measured ETA. Consult the timestamped [scheduler/progress observation](census_02-status.json) for actual stage.

[Submission](census_02-submission.json) · [Bound plan](census_02-plan.json) · [All-parent preflight](split-repair-all-parent-preflight.json) · [Astra repair review](ASTRA_CSCS_SPLIT_REPAIR_REVIEW_20261019.md)

Remote log:`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/logs/census_3693110.log`

Remote output:`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_02`

Automatic training admission remains evidence-gated. Missing corrective coverage, metadata and candidate audit are explicit holds, never implicit approvals.
