# Wave 2 v4 — canonical results ready for CP4

Aggregate retry05 **3716860 COMPLETED 0:0** in **233 seconds**. All **9 runs / 90 result files / 18 seal04 test/dev scores** are complete. Canonical metrics match all 90 completed arm-report results and the local aggregation repair check exactly; all 18 complete-view numerics slices contain **221 rows / 9,103 reference atoms**. There are no pending verdicts.

Primary **v2_test_full_coverage**: **H7_ADD_REFUTED; H7_ADD_CORR_CONFIRMED**. Common-intersection **v2_test**: **both REFUTED**. Overall H7 is **refuted** on the primary view because both contrasts must confirm. These are the frozen preregistered rules, computed with exact rational edit/reference counts before rounding.

[Canonical report](aggregate/retry05/terminal_readback/outputs/report.json), [completion receipt](aggregate/retry05/terminal_readback/outputs/E4_AGGREGATE_COMPLETE.json), [full log](aggregate/retry05/terminal_readback/slurm_3716860.log), [final audit and exact contrasts](aggregate/retry05/FINAL_AUDIT.json), [submission receipt](aggregate/retry05/terminal_readback/SUBMISSION_RECEIPT.json), [real sbatch stdout](aggregate/retry05/terminal_readback/dispatch/SBATCH.stdout).

## Identity and completeness

Production commit `e0735c125c4d344fd46caf3045a7567e8c140ef5`; production package `9c20f520fb4462c657a4f23bb7b0452ded9ddcd2a8c5a130965b40bffabd150b`. Aggregation uses the same prep03 deployed root with only the eight committed `d9047e8bc9b5f955733ca84d923d82093770064f` files applied by SHA-verified copy: [old/new hashes](aggregate/retry05/OVERLAY_APPLIED.json). All 573 baseline source files were checked against the deployment manifest with only the authorized hashes substituted; other source bytes and the existing factory were verified unchanged before dispatch. [One-result scoring check](aggregate/retry05/ONE_RESULT_CHECK.json) resolved the factory and matched the original metric path exactly.

Bound inputs `3af51068d7f80aa1fc4b0460fd7a1b87b00ed2c2ad5ae37d3a224375660dbb61`; v4 release receipt `dbc99bdc7fd9c770e25880139ef3bd3184392bfe65e1eb2baf89544c8e390f32`. Census_06 generation 2 `31316332c860d411`; released rows 167,946. Prepared ctrl/add/add_corr counts **196,227 / 364,173 / 364,173**, corrected **1,071**, exposure recount **0**. Each production allocation's exposure receipt agrees. Inputs, recipe, labels, crops, predictions and production completion receipts were preserved.

Production ctrl **3714399**, add **3714400**, add_corr **3714401** all COMPLETED 0:0, each seeds 0/1/2. [Exact launch options](production/PRODUCTION_PLAN.json): normal 12:00:00, three GPUs each; wave-1c venv environment, no LD_LIBRARY_PATH/LD_PRELOAD. Nine runs completed the fixed eight-epoch budget. Per-run CTC infeasibility: 27/3,430,976 ctrl samples, 12,023/3,430,976 add/add_corr samples; no NaN batches.

Retry05 staged 90 predictions node-local, verified their bytes and the bound-input manifest once, and inherited completed prep/training/evaluation custody for crop and checkpoint bytes. No crop/checkpoint rehash was performed. It recomputed the same metrics and validated population equality using recorded crop hashes. The full terminal log contains 90 sequential RESULT_DONE records, CANONICAL_VALIDATED, STAGE_CLEANED and AGGREGATE_RETRY05_SUCCESS. [Staging manifest](aggregate/retry05/terminal_readback/STAGED_PREDICTIONS.json).

## Preregistered contrasts

Strict literal NFD codepoint CER, original references. CER and differences below are arithmetic means across seeds 0/1/2, shown as percentages and percentage points (pp). The add gate requires ctrl minus add to exceed ctrl's full three-seed range on overall **and every weak slice**. Correction requires add_corr to improve strictly on add in every corrected source class with support; it has no added seed-range threshold. Exact fractions and denominators are in FINAL_AUDIT.json.

### v2_test

| Slice | Lines | ctrl CER % | add CER % | add_corr CER % | ctrl − add, pp | ctrl range, pp | Add gate |
|---|---:|---:|---:|---:|---:|---:|---|
| overall | 42,038 | 1.235864 | 1.273781 | 1.268680 | -0.037917 | 0.017874 | FAIL |
| all_caps | 559 | 3.066050 | 2.561241 | 2.617036 | +0.504809 | 0.063765 | PASS |
| numerics | 221 | 2.405800 | 2.127504 | 2.171445 | +0.278297 | 0.472372 | FAIL |
| punctuation_heavy | 126 | 3.116721 | 3.319308 | 3.381643 | -0.202587 | 0.374007 | FAIL |
| mixed_script | 1,133 | 1.747881 | 1.825128 | 1.776275 | -0.077247 | 0.018790 | FAIL |
| cyrillic | 1,742 | 1.845712 | 1.819091 | 1.827561 | +0.026621 | 0.070182 | FAIL |

| Corrected class | Lines | add − add_corr, pp | Correction improves |
|---|---:|---:|---|
| cyrillic | 1,742 | -0.008470 | no |
| greek_latin_cs | 849 | +0.036996 | yes |
| greek_poly | 28,549 | +0.005530 | yes |

Verdicts: **H7_ADD_REFUTED / H7_ADD_CORR_REFUTED**.

### v2_test_full_coverage

| Slice | Lines | ctrl CER % | add CER % | add_corr CER % | ctrl − add, pp | ctrl range, pp | Add gate |
|---|---:|---:|---:|---:|---:|---:|---|
| overall | 43,883 | 1.241751 | 1.279684 | 1.272995 | -0.037933 | 0.016008 | FAIL |
| all_caps | 559 | 3.068707 | 2.558584 | 2.617036 | +0.510123 | 0.055795 | PASS |
| numerics | 221 | 2.405800 | 2.120180 | 2.171445 | +0.285620 | 0.472372 | FAIL |
| punctuation_heavy | 129 | 3.059216 | 3.271240 | 3.316674 | -0.212025 | 0.363471 | FAIL |
| mixed_script | 1,225 | 1.941154 | 2.071854 | 1.983690 | -0.130699 | 0.009280 | FAIL |
| cyrillic | 3,510 | 1.586993 | 1.590047 | 1.570766 | -0.003054 | 0.050399 | FAIL |

| Corrected class | Lines | add − add_corr, pp | Correction improves |
|---|---:|---:|---|
| cyrillic | 3,510 | +0.019281 | yes |
| greek_latin_cs | 854 | +0.037326 | yes |
| greek_poly | 28,587 | +0.005170 | yes |

Verdicts: **H7_ADD_REFUTED / H7_ADD_CORR_CONFIRMED**.

On the primary view, add worsens overall CER by 0.037933 pp versus ctrl. add_corr improves versus add by 0.006690 pp but remains 0.031244 pp worse than ctrl. Correction confirmation is the preregistered classwise contrast against add. In the common-intersection view, Cyrillic fails that correction contrast. The census primary-class `numerics_tables` remains a separately reported zero-support diagnostic; it does not replace the preregistered 221-row `numerics` slice.

## Seal04 test/dev — per arm and seed

**diagnostic_only**, pending checkpoint-exposure/work-identity review. These scores do not replace the original-reference v2 H7 instruments. All runs cover 2,253 test rows and 437 dev rows, with zero missing/failed predictions. Percentages use each metric's own denominator: NFC characters, NFD atoms, diacritic-insensitive characters, and words. [Exact edits and denominators](aggregate/retry05/SEAL04_SEED_METRICS_FINAL.json).

| Arm | Seed | Panel | NFC CER % | NFD CER % | DI CER % | WER % | Exact lines |
|---|---:|---|---:|---:|---:|---:|---:|
| ctrl | 0 | test | 3.981593 | 3.701435 | 3.620461 | 13.666916 | 1452/2253 |
| ctrl | 0 | dev | 5.369021 | 4.992627 | 5.020589 | 12.897016 | 284/437 |
| ctrl | 1 | test | 4.167492 | 3.872656 | 3.762171 | 14.180358 | 1469/2253 |
| ctrl | 1 | dev | 5.392778 | 4.971561 | 5.044346 | 13.811357 | 271/437 |
| ctrl | 2 | test | 3.938928 | 3.656890 | 3.525988 | 13.489544 | 1481/2253 |
| ctrl | 2 | dev | 5.440291 | 5.027737 | 5.036427 | 13.907603 | 270/437 |
| add | 0 | test | 2.316120 | 2.160447 | 2.050985 | 8.429798 | 1682/2253 |
| add | 0 | dev | 4.038644 | 3.756759 | 3.745645 | 9.913378 | 295/437 |
| add | 1 | test | 2.357261 | 2.195248 | 2.093650 | 8.588499 | 1668/2253 |
| add | 1 | dev | 3.777320 | 3.532055 | 3.500158 | 8.806545 | 314/437 |
| add | 2 | test | 2.281073 | 2.125646 | 2.015939 | 8.345780 | 1687/2253 |
| add | 2 | dev | 3.864428 | 3.560143 | 3.595185 | 8.854668 | 313/437 |
| add_corr | 0 | test | 2.303930 | 2.153486 | 2.047938 | 8.485810 | 1667/2253 |
| add_corr | 0 | dev | 4.046563 | 3.763781 | 3.769401 | 9.961501 | 300/437 |
| add_corr | 1 | test | 2.285645 | 2.138174 | 2.034224 | 8.383122 | 1681/2253 |
| add_corr | 1 | dev | 3.864428 | 3.595253 | 3.579347 | 9.480269 | 307/437 |
| add_corr | 2 | test | 2.249074 | 2.096413 | 2.002225 | 8.075056 | 1700/2253 |
| add_corr | 2 | dev | 3.919861 | 3.644407 | 3.650618 | 9.287777 | 312/437 |

## Final sacct accounting

Allocation-level `sacct -X`; elapsed seconds × GPU count from ReqTRES and AllocTRES are reported separately, with no duplicate step rows. CPU jobs requested zero GPUs but received four-GPU nodes. Includes failed preparation, smoke and aggregation attempts. Rejected submissions have no allocation or GPU-h cost. [All 17 rows](aggregate/retry05/FINAL_ACCOUNTING.json); [raw sacct](aggregate/retry05/terminal_readback/sacct.final).

| Stage | Job ID | State / exit | Seconds | Requested GPU-h | Allocated GPU-h |
|---|---|---|---:|---:|---:|
| e4_wave2_inventory | 3705102 | FAILED / 1:0 | 540 | 0.000000 | 0.600000 |
| e4_wave2_inventory | 3705163 | FAILED / 1:0 | 284 | 0.000000 | 0.315556 |
| e4_wave2_inventory | 3705261 | COMPLETED / 0:0 | 530 | 0.000000 | 0.588889 |
| smoke_e4_wave2 | 3705405 | FAILED / 1:0 | 795 | 0.220833 | 0.883333 |
| smoke_e4_wave2 | 3705669 | FAILED / 1:0 | 996 | 0.276667 | 1.106667 |
| e4_wave2_prepare | 3713398 | FAILED / 1:0 | 10 | 0.000000 | 0.011111 |
| e4_wave2_prepare | 3713491 | COMPLETED / 0:0 | 622 | 0.000000 | 0.691111 |
| smoke_e4_wave2_job01 | 3713629 | COMPLETED / 0:0 | 1235 | 0.343056 | 1.372222 |
| e4_wave2_prepare | 3714068 | COMPLETED / 0:0 | 620 | 0.000000 | 0.688889 |
| smoke_e4_wave2_job01 | 3714153 | COMPLETED / 0:0 | 1225 | 0.340278 | 1.361111 |
| e4_wave2_job01 | 3714399 | COMPLETED / 0:0 | 14697 | 12.247500 | 16.330000 |
| e4_wave2_job02 | 3714400 | COMPLETED / 0:0 | 13393 | 11.160833 | 14.881111 |
| e4_wave2_job03 | 3714401 | COMPLETED / 0:0 | 14500 | 12.083333 | 16.111111 |
| e4_wave2_aggregate | 3716069 | TIMEOUT / 0:0 | 1575 | 0.000000 | 1.750000 |
| e4_wave2_aggregate | 3716442 | CANCELLED by 1883 / 0:0 | 11035 | 0.000000 | 12.261111 |
| e4_wave2_aggregate | 3716824 | FAILED / 1:0 | 40 | 0.000000 | 0.044444 |
| e4_wave2_aggregate | 3716860 | COMPLETED / 0:0 | 233 | 0.000000 | 0.258889 |

All-attempt consumption: **36.672500 requested / 69.255556 allocated GPU-h**. Retry05 adds **0.000000 requested / 0.258889 allocated GPU-h**. Production alone: **35.491667 requested / 47.322222 allocated GPU-h**. The production reservation was 108 requested GPU-h; prior consumption plus that reservation was 109.180833.

Owner wave cap **350 requested GPU-h**; series caps remain **120**. This wave is below both numerical thresholds on the stated requested-GPU basis. Other RUNNER3/S1 series costs are excluded; combined-series compliance is not asserted. Full node allocation is reported separately above.

## CP4 notes

Retain the two MEDIUM v4 findings: sf7 duplicated breathing (`lekythos--3bfc4a385d61b883--s001-l0106`) and residual raw OCR Χρξώστες for Χρεώστες (`gazette_modern--dacf995fd419bebd--s000-l0113`). Neither was changed. Seal04 stays diagnostic_only; this is a completed result packet for Astra review, not CP4 acceptance or a data-floor/generalization claim.

Earlier aggregation attempts: retry02 3716069 TIMEOUT; retry03 3716442 coordinator-cancelled after repeated crop hashing; retry04 3716824 FAILED because the fresh aggregation tree omitted factory/src/codec.rs. Retry05 reused the built prep03 root and the committed aggregation delta. Their costs are included; canonical results come exclusively from completed retry05.

**READY FOR CP4**
