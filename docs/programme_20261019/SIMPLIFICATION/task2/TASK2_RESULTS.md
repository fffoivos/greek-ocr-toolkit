# Task 2 v2 — initial recipe, admission policy, and label corrections

Report revision for [Astra review 1](ASTRA_TASK2_review_1.md). Training and scoring allocations are complete; this revision uses saved predictions only. **TASK2 v2 READY** for review. All comparisons remain diagnostic_only.

These results do not demonstrate that filtering and correcting the initial recipe improves the model. On cleaned v2_test, ctrl is effectively tied with as-is and ctrl_corr has slightly higher CER. The seal04 differences among these three arms remain within seed variation, including on the new ADMIT-only corrected test. Adding release data has a much larger seal04 benefit, with a v2 cost. These are descriptive three-seed comparisons; no new significance or H7 claim is made.

Arm names describe the actual populations:

- **as-is (wave-1c):** 211,451 old-admitted collection-v2 training rows, raw labels, as last run; not the earlier 212,925-row recovered pool. No release rows.
- **filtered / admission policy (ctrl):** census_06 generation-2 admission applied to the initial collection population: **195,346 retained + 881 reinstated = 196,227** raw-label rows. Relative to wave-1c, 16,105 rows were removed and 881 reinstated (874 previously rejected as `lookalike_only_word`, seven as `unexpected_script`). This is replacement of the admission policy, including reinstatements; the reinstatements are 0.45% of ctrl. It is not a removal-only subset of the 211,451 rows.
- **filtered + corrected (ctrl_corr):** the same 196,227 rows and indexed draws as ctrl, with **167 RU1 label corrections**, **166 inside the exact initial recipe** and one on reinstated row `0b4bf868-p000657-l0027`. SF7 and N1 change no ctrl labels. No release rows.
- **data-quantity extras add / add_corr:** 364,173 rows including 167,946 release rows; add uses raw labels, add_corr the same 167 RU1 changes plus 904 SF7 changes exclusively on release rows.

The coordinator accepted the population difference and requested this report repair with **no retraining**. It limits causal attribution as described below.

Raw v2_test has 42,038 rows / 221 E3 numerics; cleaned v2 has 39,434 ADMIT rows, 426 changed references (305 polytonic, 121 Cyrillic), and 175 numerics. ADMIT-raw scores below distinguish selection from label correction. Seal04 now has three explicitly separate reference variants: **raw** and **overlay-only** keep all 2,253 test / 437 dev rows, with 6 / 1 diagnostic label changes; **ADMIT-only corrected** keeps **2,232 test / 437 dev** rows, excludes 21 test HOLD rows, and applies the same overlay. All six test and one dev changed references are ADMIT. The sealed files remain unchanged.

Arithmetic mean of the three per-seed corpus NFD CERs, in percent; literal hypotheses and the seal04 scorer's per-codepoint decomposition are unchanged. The last column is new; the earlier two are preserved and checked against the saved hypotheses. For v2, the existing cleaned column already uses ADMIT-only corrected references.

| Arm | Panel | Raw CER %, mean (s0 / s1 / s2) | ADMIT-corrected v2 / overlay-only seal04 CER %, mean (s0 / s1 / s2) | ADMIT-only corrected seal04 CER %, mean (s0 / s1 / s2) |
|---|---|---:|---:|---:|
| as-is (wave-1c) | v2_test | 1.218873 (1.209621 / 1.212714 / 1.234284) | 1.275119 (1.266322 / 1.270129 / 1.288905) | — (already ADMIT-corrected in previous column) |
| as-is (wave-1c) | benchmark_v02_test | 3.740876 (3.775213 / 3.759901 / 3.687515) | 3.735720 (3.770985 / 3.755672 / 3.680503) | 3.664098 (3.696672 / 3.684108 / 3.611514) |
| as-is (wave-1c) | benchmark_v02_dev | 5.081572 (4.950495 / 5.245418 / 5.048803) | 5.079231 (4.943473 / 5.238396 / 5.055825) | 5.079231 (4.943473 / 5.238396 / 5.055825) |
| filtered / admission policy (ctrl) | v2_test | 1.235864 (1.231512 / 1.229102 / 1.246976) | 1.276102 (1.270215 / 1.272909 / 1.285184) | — (already ADMIT-corrected in previous column) |
| filtered / admission policy (ctrl) | benchmark_v02_test | 3.743660 (3.701435 / 3.872656 / 3.656890) | 3.738504 (3.702776 / 3.865642 / 3.647095) | 3.663167 (3.625475 / 3.791602 / 3.572426) |
| filtered / admission policy (ctrl) | benchmark_v02_dev | 4.997308 (4.992627 / 4.971561 / 5.027737) | 4.994968 (4.985605 / 4.978583 / 5.020715) | 4.994968 (4.985605 / 4.978583 / 5.020715) |
| filtered + corrected (ctrl_corr) | v2_test | 1.249668 (1.263927 / 1.234926 / 1.250150) | 1.286952 (1.295278 / 1.276416 / 1.289161) | — (already ADMIT-corrected in previous column) |
| filtered + corrected (ctrl_corr) | benchmark_v02_test | 3.738092 (3.808622 / 3.734844 / 3.670810) | 3.732008 (3.804393 / 3.730616 / 3.661015) | 3.658049 (3.728780 / 3.658979 / 3.586386) |
| filtered + corrected (ctrl_corr) | benchmark_v02_dev | 5.023055 (5.020715 / 5.027737 / 5.020715) | 5.016034 (5.013693 / 5.020715 / 5.013693) | 5.016034 (5.013693 / 5.020715 / 5.013693) |
| extra: add | v2_test | 1.273781 (1.272442 / 1.267622 / 1.281279) | 1.290858 (1.290915 / 1.285825 / 1.295834) | — (already ADMIT-corrected in previous column) |
| extra: add | benchmark_v02_test | 2.160447 (2.160447 / 2.195248 / 2.125646) | 2.156240 (2.156240 / 2.191041 / 2.121440) | 2.081937 (2.080076 / 2.119165 / 2.046571) |
| extra: add | benchmark_v02_dev | 3.616319 (3.756759 / 3.532055 / 3.560143) | 3.618660 (3.763781 / 3.539077 / 3.553121) | 3.618660 (3.763781 / 3.539077 / 3.553121) |
| extra: add_corr | v2_test | 1.268680 (1.266859 / 1.263324 / 1.275856) | 1.284770 (1.282318 / 1.281335 / 1.290658) | — (already ADMIT-corrected in previous column) |
| extra: add_corr | benchmark_v02_test | 2.129358 (2.153486 / 2.138174 / 2.096413) | 2.125152 (2.149280 / 2.133968 / 2.092207) | 2.050294 (2.073096 / 2.059136 / 2.018651) |
| extra: add_corr | benchmark_v02_dev | 3.667814 (3.763781 / 3.595253 / 3.644407) | 3.665473 (3.770803 / 3.588231 / 3.637385) | 3.665473 (3.770803 / 3.588231 / 3.637385) |

| Panel / slice | Reference | as-is | filtered ctrl | corrected ctrl | extra add | extra add_corr |
|---|---|---:|---:|---:|---:|---:|
| v2_test / overall | raw | 1.218873 | 1.235864 | 1.249668 | 1.273781 | 1.268680 |
| v2_test / all_caps | raw | 2.842872 | 3.066050 | 3.145757 | 2.561241 | 2.617036 |
| v2_test / numerics | raw | 2.043282 | 2.405800 | 2.281299 | 2.127504 | 2.171445 |
| v2_test / punctuation_heavy | raw | 2.968677 | 3.116721 | 3.233598 | 3.319308 | 3.381643 |
| v2_test / mixed_script | raw | 1.412168 | 1.747881 | 1.766671 | 1.825128 | 1.776275 |
| v2_test / cyrillic | raw | 1.489961 | 1.845712 | 1.904601 | 1.819091 | 1.827561 |
| v2_test / class:greek_latin_cs | raw | 1.295394 | 1.320058 | 1.314160 | 1.310943 | 1.273947 |
| v2_test / class:greek_poly | raw | 1.414865 | 1.413963 | 1.426376 | 1.467479 | 1.461949 |
| v2_test / overall | cleaned | 1.275119 | 1.276102 | 1.286952 | 1.290858 | 1.284770 |
| v2_test / all_caps | cleaned | 2.951361 | 3.129903 | 3.186712 | 2.583455 | 2.640264 |
| v2_test / numerics | cleaned | 2.112124 | 2.229736 | 2.239537 | 2.219935 | 2.234637 |
| v2_test / punctuation_heavy | cleaned | 2.894013 | 2.950944 | 3.064807 | 3.017364 | 3.074295 |
| v2_test / mixed_script | cleaned | 1.423633 | 1.453795 | 1.440802 | 1.428273 | 1.391151 |
| v2_test / cyrillic | cleaned | 1.543876 | 1.632406 | 1.566909 | 1.482697 | 1.458225 |
| v2_test / class:greek_latin_cs | cleaned | 1.344148 | 1.367586 | 1.357229 | 1.348508 | 1.311988 |
| v2_test / class:greek_poly | cleaned | 1.519841 | 1.515294 | 1.527288 | 1.541014 | 1.534860 |
| benchmark_v02_test / overall | raw | 3.740876 | 3.743660 | 3.738092 | 2.160447 | 2.129358 |
| benchmark_v02_test / all_caps | raw | 8.410256 | 8.747253 | 8.263736 | 6.227106 | 6.073260 |
| benchmark_v02_test / numerics | raw | 10.334412 | 10.140237 | 10.377562 | 5.663430 | 5.415318 |
| benchmark_v02_test / punctuation_heavy | raw | 7.880387 | 8.021108 | 8.232190 | 4.028144 | 4.098505 |
| benchmark_v02_test / mixed_script | raw | 4.129082 | 4.199007 | 4.261940 | 1.398504 | 1.356548 |
| benchmark_v02_test / cyrillic | raw | 3.867978 | 3.934178 | 3.940483 | 3.867978 | 3.833302 |
| benchmark_v02_test / class:greek_latin_cs | raw | 4.139067 | 4.209161 | 4.272246 | 1.401886 | 1.356324 |
| benchmark_v02_test / class:greek_poly | raw | 1.904029 | 1.860915 | 1.832949 | 1.291104 | 1.279452 |
| benchmark_v02_test / overall | overlay-only | 3.735720 | 3.738504 | 3.732008 | 2.156240 | 2.125152 |
| benchmark_v02_test / all_caps | overlay-only | 8.410256 | 8.747253 | 8.263736 | 6.227106 | 6.073260 |
| benchmark_v02_test / numerics | overlay-only | 10.334412 | 10.140237 | 10.377562 | 5.663430 | 5.415318 |
| benchmark_v02_test / punctuation_heavy | overlay-only | 7.880387 | 8.021108 | 8.232190 | 4.028144 | 4.098505 |
| benchmark_v02_test / mixed_script | overlay-only | 4.129082 | 4.199007 | 4.261940 | 1.398504 | 1.356548 |
| benchmark_v02_test / cyrillic | overlay-only | 3.867978 | 3.934178 | 3.940483 | 3.867978 | 3.833302 |
| benchmark_v02_test / class:greek_latin_cs | overlay-only | 4.139067 | 4.209161 | 4.272246 | 1.401886 | 1.356324 |
| benchmark_v02_test / class:greek_poly | overlay-only | 1.891146 | 1.848033 | 1.817737 | 1.280572 | 1.268920 |
| benchmark_v02_dev / overall | raw | 5.081572 | 4.997308 | 5.023055 | 3.616319 | 3.667814 |
| benchmark_v02_dev / all_caps | raw | 16.101056 | 16.402715 | 15.912519 | 9.577677 | 8.974359 |
| benchmark_v02_dev / numerics | raw | 11.666667 | 11.161616 | 11.919192 | 6.666667 | 6.313131 |
| benchmark_v02_dev / punctuation_heavy | raw | 8.955224 | 7.628524 | 7.628524 | 4.477612 | 4.809287 |
| benchmark_v02_dev / mixed_script | raw | 5.479930 | 5.375218 | 5.200698 | 2.338569 | 2.652705 |
| benchmark_v02_dev / cyrillic | raw | 2.917076 | 2.818748 | 2.917076 | 1.901016 | 1.868240 |
| benchmark_v02_dev / class:greek_latin_cs | raw | 5.479930 | 5.375218 | 5.200698 | 2.338569 | 2.652705 |
| benchmark_v02_dev / class:greek_poly | raw | 1.161034 | 1.130821 | 1.135137 | 0.789849 | 0.837326 |
| benchmark_v02_dev / overall | overlay-only | 5.079231 | 4.994968 | 5.016034 | 3.618660 | 3.665473 |
| benchmark_v02_dev / all_caps | overlay-only | 16.101056 | 16.402715 | 15.912519 | 9.577677 | 8.974359 |
| benchmark_v02_dev / numerics | overlay-only | 11.666667 | 11.161616 | 11.919192 | 6.666667 | 6.313131 |
| benchmark_v02_dev / punctuation_heavy | overlay-only | 8.955224 | 7.628524 | 7.628524 | 4.477612 | 4.809287 |
| benchmark_v02_dev / mixed_script | overlay-only | 5.479930 | 5.375218 | 5.200698 | 2.338569 | 2.652705 |
| benchmark_v02_dev / cyrillic | overlay-only | 2.917076 | 2.818748 | 2.917076 | 1.901016 | 1.868240 |
| benchmark_v02_dev / class:greek_latin_cs | overlay-only | 5.479930 | 5.375218 | 5.200698 | 2.338569 | 2.652705 |
| benchmark_v02_dev / class:greek_poly | overlay-only | 1.156718 | 1.126505 | 1.122189 | 0.794165 | 0.833010 |

NFD CER is percent. Same readout/benchmark_readout functions, literal hypotheses, and exact reference IDs for all arms. All per-seed sufficient statistics and slices are in the respective report.json files. RESULTS.md and its two preregistered H7 verdicts remain the original quantity ablation; this task-2 table does not replace them.

## Task 2 admission-policy and correction contrasts

Changes below are candidate minus parent in percentage points of mean NFD CER; negative means lower error. Means use all three seeds. These are descriptive contrasts, with no new H7 or significance claim.

| Panel | References | Admission-policy ctrl minus as-is, pp | Corrected ctrl minus filtered ctrl, pp |
|---|---|---:|---:|
| v2_test | raw | +0.016991 | +0.013804 |
| v2_test | cleaned | +0.000984 | +0.010849 |
| benchmark_v02_test | raw | +0.002784 | -0.005568 |
| benchmark_v02_test | overlay-only | +0.002784 | -0.006496 |
| benchmark_v02_dev | raw | -0.084264 | +0.025747 |
| benchmark_v02_dev | overlay-only | -0.084264 | +0.021066 |
| benchmark_v02_test | ADMIT-only corrected | -0.000931 | -0.005119 |
| benchmark_v02_dev | ADMIT-only corrected | -0.084264 | +0.021066 |

## Caveats retained from Astra review 1

**MEDIUM 3 — output vocabulary changes with admission policy.** Wave-1c uses codec v2 with 254 atoms; ctrl/ctrl_corr use append-compatible v2.1 with 265 atoms, adding 11 Cyrillic atoms. Prefix compatibility preserves old IDs but does not hold the output head fixed. As-is versus ctrl therefore combines the population/admission-policy change with an output-vocabulary change. Ctrl versus ctrl_corr shares codec, model parameters, population, draws, validation, training budget and recipe.

**MEDIUM 4 — limited correction coverage.** Ctrl_corr changes 167/196,227 labels (0.0851%), all RU1; only 166 belong to the exact initial recipe. SF7/N1 change zero ctrl labels. The 904 SF7 corrections are on release rows and appear only in add_corr. The ctrl correction contrast cannot establish SF7 or N1's value or lack of value. The expanded-data correction contrast shows a small, consistent v2 improvement across matched seeds, but no consistent benchmark-wide improvement.

Raw versus cleaned v2 changes the evaluation population as well as labels; use the ADMIT-raw column below to separate selection from correction. The diagnostic overlays replay the tools' recorded edits, not independent human adjudication. Row-ID, recorded edition and crop-hash exposure checks passed, but canonical-work and historical checkpoint exposure remain unresolved; seal04 remains diagnostic_only.

## Optional next experiment — not run

Astra's next experiment would compare the exact **211,451-row initial population**, its **195,346-row census-ADMIT intersection**, and that identical intersection with the **166 reachable corrections**. Hold the original model/codec, validation, sampling procedure and training budget fixed; use matched seeds, with seed count chosen for a prespecified useful effect size. Score raw and ADMIT-only corrected references, including the 2,232-row seal04 test. SF7 remains outside this population's correction coverage.

At the current 8-epoch / 53,616-update budget, a three-seed, three-arm rerun is nine runs: approximately **36 requested GPU-h actual-time planning estimate**, using the completed production ctrl allocation's 12.25 requested GPU-h as a rough per-arm anchor. This is not a runtime qualification for the changed codec/populations. Retaining the present 3-GPU × 12-hour allocation limits reserves **108 requested GPU-h** (36 per arm); 222.75 already reserved + 108 = **330.75/350**, before any new preparation, smoke or scoring. Each new three-seed arm would reserve 36/120 series GPU-h. More than three seeds would need a new budget assessment. This is a follow-up option only: no job, reservation, retraining or submission was made.


## v2 reference selection versus correction

All figures below are mean NFD CER percent across seeds 0/1/2. ADMIT raw and cleaned use the same 39,434 row identities; only cleaned applies the 426 corrected references. The first column instead uses all 42,038 raw-reference rows.

| Arm | Raw, all rows | ADMIT raw, same retained rows | ADMIT corrected |
|---|---:|---:|---:|
| asis | 1.218873 | 1.283181 | 1.275119 |
| ctrl | 1.235864 | 1.285505 | 1.276102 |
| ctrl_corr | 1.249668 | 1.298280 | 1.286952 |
| add | 1.273781 | 1.300518 | 1.290858 |
| add_corr | 1.268680 | 1.296041 | 1.284770 |

## Execution and verification

ctrl_corr04 **3719761 COMPLETED/0:0** in **7,807 s**, on nid006166, with nid006260 excluded. Seeds 0/1/2 each completed all 8 epochs / 53,616 updates from scratch; no partial checkpoint was resumed. Training logged 27 CTC-infeasible samples out of 3,430,976 per seed and zero NaN batches. Raw evaluation, reference-overlay scoring and the five-arm join completed in the same allocation.

Completion, report, copied preparation and node-binding hashes were checked. All 15 models have 42,038 raw / 39,434 cleaned v2 rows and 221 / 175 numerics rows. The three new models also have complete 2,253-row seal04 test and 437-row dev scores on both reference variants. The original raw/overlay-only main table matched the remote table exactly; revision 2 preserves those values and checks all 80 seal04 printed mean/seed numbers against the saved hypotheses. Full run/worker logs were read.

Startup evidence: sbatch stdout and srun were confirmed, and all three CUDA/model/optimizer setups were observed at 655 s. The unchanged trainer emits completed-update counts only per epoch; the first completed-update proof was read at 1,260 s, outside the requested 15-minute window. This is recorded rather than inferred from a RUNNING state.

Remote output root: `/capstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel4_e0735c1_20261021_prep03/code/out/e4/task2_ctrl_corr04/work`. Local evidence: [completion](../../../out/runner2/resume_20261022_ctrl_corr04/CTRL_CORR_COMPLETE.json), [ctrl_corr scores](../../../out/runner2/resume_20261022_ctrl_corr04/ctrl_corr_report.json), [baseline scores](../../../out/runner2/resume_20261022_ctrl_corr04/baseline_report.json), [prior wave-2 rescore](../../../out/runner2/resume_20261022_ctrl_corr04/wave2_rescore_report.json), [submission receipt](../../../out/runner2/resume_20261022_ctrl_corr04/dispatch/SUBMISSION_RECEIPT.json), [sacct](../../../out/runner2/resume_20261022_ctrl_corr04/FINAL_SACCT.psv).

## Terminal Slurm accounting

| Job | Stage | State | Elapsed s | GPUs requested / allocated | Requested / allocated GPU-h, actual elapsed | Requested GPU-h reservation |
|---|---|---|---:|---:|---:|---:|
| 3705102 | e4_wave2_inventory | FAILED | 540 | 0 / 4 | 0.000000 / 0.600000 | 0.000000 |
| 3705163 | e4_wave2_inventory | FAILED | 284 | 0 / 4 | 0.000000 / 0.315556 | 0.000000 |
| 3705261 | e4_wave2_inventory | COMPLETED | 530 | 0 / 4 | 0.000000 / 0.588889 | 0.000000 |
| 3705405 | smoke_e4_wave2 | FAILED | 795 | 1 / 4 | 0.220833 / 0.883333 | 0.750000 |
| 3705669 | smoke_e4_wave2 | FAILED | 996 | 1 / 4 | 0.276667 / 1.106667 | 1.000000 |
| 3713398 | e4_wave2_prepare | FAILED | 10 | 0 / 4 | 0.000000 / 0.011111 | 0.000000 |
| 3713491 | e4_wave2_prepare | COMPLETED | 622 | 0 / 4 | 0.000000 / 0.691111 | 0.000000 |
| 3713629 | smoke_e4_wave2_job01 | COMPLETED | 1235 | 1 / 4 | 0.343056 / 1.372222 | 0.500000 |
| 3714068 | e4_wave2_prepare | COMPLETED | 620 | 0 / 4 | 0.000000 / 0.688889 | 0.000000 |
| 3714153 | smoke_e4_wave2_job01 | COMPLETED | 1225 | 1 / 4 | 0.340278 / 1.361111 | 0.500000 |
| 3714399 | e4_wave2_job01 | COMPLETED | 14697 | 3 / 4 | 12.247500 / 16.330000 | 36.000000 |
| 3714400 | e4_wave2_job02 | COMPLETED | 13393 | 3 / 4 | 11.160833 / 14.881111 | 36.000000 |
| 3714401 | e4_wave2_job03 | COMPLETED | 14500 | 3 / 4 | 12.083333 / 16.111111 | 36.000000 |
| 3716069 | e4_wave2_aggregate | TIMEOUT | 1575 | 0 / 4 | 0.000000 / 1.750000 | 0.000000 |
| 3716442 | e4_wave2_aggregate | CANCELLED by 1883 | 11035 | 0 / 4 | 0.000000 / 12.261111 | 0.000000 |
| 3716824 | e4_wave2_aggregate | FAILED | 40 | 0 / 4 | 0.000000 / 0.044444 | 0.000000 |
| 3716860 | e4_wave2_aggregate | COMPLETED | 233 | 0 / 4 | 0.000000 / 0.258889 | 0.000000 |
| 3717948 | e4_wave2_rescore | COMPLETED | 505 | 0 / 4 | 0.000000 / 0.561111 | 0.000000 |
| 3718079 | e4_task2_wave1c | FAILED | 31 | 1 / 4 | 0.008611 / 0.034444 | 2.000000 |
| 3718182 | e4_ctrl_corr_prepare | FAILED | 155 | 0 / 4 | 0.000000 / 0.172222 | 0.000000 |
| 3718218 | e4_task2_wave1c | COMPLETED | 217 | 1 / 4 | 0.060278 / 0.241111 | 2.000000 |
| 3718299 | e4_ctrl_corr_prepare | COMPLETED | 830 | 0 / 4 | 0.000000 / 0.922222 | 0.000000 |
| 3718482 | e4_ctrl_corr_runs | FAILED | 8 | 3 / 4 | 0.006667 / 0.008889 | 36.000000 |
| 3718666 | e4_ctrl_corr03 | NODE_FAIL | 1425 | 3 / 4 | 1.187500 / 1.583333 | 36.000000 |
| 3719761 | e4_ctrl_corr04 | COMPLETED | 7807 | 3 / 4 | 6.505833 / 8.674444 | 36.000000 |

Cumulative wave-2/Task-2 actual-elapsed cost: **44.441389 requested / 81.453333 allocated GPU-h**. Sum of submitted requested-GPU limit reservations across these attempts: **222.750000 GPU-h**, below the owner's 350 cap. This reservation sum is conservative for completed and failed jobs; it is not additional consumption. The ctrl_corr02, ctrl_corr03 and ctrl_corr04 allocations each reserve 36 requested GPU-h (108 total, below the 120 series cap). CPU jobs request zero GPUs but can allocate four; the allocation column retains that charge. No job-step double counting.

Scope includes all recorded wave-2 preparation/smoke/production/aggregate attempts since 6 October, the cleaned-reference rescore, both baseline scoring attempts, and both ctrl_corr preparations, failed allocations 3718482 and 3718666, plus the successful ctrl_corr training/scoring allocation. Rejected submissions without a real job ID cost zero. Historical wave-1c training and RUNNER3/S1 are excluded; no combined-series cap assertion is made.

## Completed evidence

- Baseline scoring: 3718218; report SHA256 `bbe158ff5a48f49fdf3cdcf5db1d1a1c2300b18bed0248723cfbbe57cf994204`.
- Nine-wave-2 checkpoint rescore: 3717948; report SHA256 `294f482d8d22735ab1359405cf3c06874df5f52d27863ac0bc3f467037426144`.
- ctrl_corr prep: 3718299; training/scoring: 3719761; operator source commit `2fc2a24`, allocation dispatch `a3eb4d6`; report SHA256 `2b47b7206c7ca405ad8a22925e64dba9143f6ec7d0721070059b41fb26048a53`.
- ctrl_corr completion SHA256 `303d8c1940c64363c0df7304e79e4dbe02c003d7fd12717833fd624536dfcd07`; input binding `3af51068d7f80aa1fc4b0460fd7a1b87b00ed2c2ad5ae37d3a224375660dbb61`.
- Original RESULTS.md and its preregistered quantity-ablation H7 verdicts are retained unchanged. RUNNER2 did not submit, cancel or commit jobs.

## Revision 2 evidence

The report-only recount uses all 30 saved seal04 prediction files (five arms × three seeds × test/dev), with 38 checked source SHA256 bindings. It does not read crops, load checkpoints, retrain, infer, or modify sealed files. Reference/audit parent and row IDs and original/overlaid text hashes must agree before selecting ADMIT rows. The NFD CER uses the unchanged `bench.score.normalize` and `train.cer.levenshtein` numerator/denominator calculation.

The full-real-panel regression reproduces Astra's five ADMIT-only corrected test means to six decimals: **3.664098 / 3.663167 / 3.658049 / 2.081937 / 2.050294%** (as-is / ctrl / ctrl_corr / add / add_corr). All original/overlay-only test means also reproduce; dev's overlay-only and ADMIT-only sufficient statistics are identical for every seed. A direct comparison with `bench.score.aggregate` on all six changed test references checks metric parity. **29 tests passed**, including a comparison of all **120 printed seal04 mean/seed values** across the three reference variants.

Reproducible fixture: [full-panel witnesses](../../../tests/fixtures/e4_task2_seal04_all.README.md); [report-only scorer](../../../scripts/ops/e4_task2_admitted_seal.py); [regression test](../../../tests/test_e4_task2_admitted_seal.py). Per-seed sufficient statistics and all source hashes: [ADMITTED_SEAL04.json](../../../out/runner2/task2_v2/ADMITTED_SEAL04.json). Existing v2 and slice tables above are preserved; seal04 slice rows previously called cleaned are now explicitly overlay-only. No new allocation cost; terminal accounting above is unchanged.

**TASK2 v2 READY**
