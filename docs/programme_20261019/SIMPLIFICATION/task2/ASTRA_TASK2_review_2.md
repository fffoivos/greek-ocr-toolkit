# ASTRA-TASK2 review 2 — scoped certification

**PASS — the corrected report satisfies the scoped report-only repair; no blocking findings remain.**

Reviewed [TASK2_RESULTS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/TASK2_RESULTS.md) at `831b708`. Current HEAD `7b7400e` adds only the review-2 brief. This review made no writes, submissions, or background jobs.

**Findings**

1. **HIGH 2 resolved — ADMIT-only corrected seal04 scores reproduce.** My independent recount gives these arithmetic means of three per-seed corpus NFD CERs, in percent:

   | Arm | Test: 2,232 ADMIT rows | Dev: 437 ADMIT rows |
   |---|---:|---:|
   | as-is | 3.664098 | 5.079231 |
   | ctrl | 3.663167 | 4.994968 |
   | ctrl_corr | 3.658049 | 5.016034 |
   | add | 2.081937 | 3.618660 |
   | add_corr | 2.050294 | 3.665473 |

   The 21 test HOLD rows are excluded. All six corrected test references and the one corrected dev reference are ADMIT. Dev’s overlay-only and ADMIT-only sufficient statistics are identical for every seed. Raw and overlay-only columns remain present.

2. **HIGH 1 resolved — population and correction placement are stated correctly.** As-is contains **211,451** old-admitted rows. Ctrl contains **195,346 retained + 881 reinstated = 196,227**, after removing 16,105 original rows. The reinstatements comprise 874 `lookalike_only_word` and seven `unexpected_script` cases. Ctrl_corr applies **167 RU1 corrections**, with **166** inside the exact initial population and one on reinstated row `0b4bf868-p000657-l0027`. The “strict arms” claim is gone. Vocabulary and correction-coverage limitations remain explicit.

3. **The owner-facing conclusion matches the numbers.** These results do not demonstrate improvement from filtering and correcting the initial recipe. The ADMIT-only test contrasts are **−0.000931 pp** for ctrl versus as-is and **−0.005119 pp** for ctrl_corr versus ctrl, unresolved against seed variation. Adding release data yields the much larger seal04 benefit, with a v2 cost. The controlled three-arm follow-up is clearly optional and unrun; its cost is identified as a planning estimate.

4. **No unrelated changes found.** All **120 original overall CER values**, **240 slice values**, the v2 selection/correction table, terminal accounting, and completed-evidence entries are unchanged. Existing training/scoring code and `RESULTS.md` H7 results are unchanged. Supporting additions are confined to the report repair, coordinator instruction, recount helper, fixture, and regression tests.

Verification included **38 source hashes checked live on Clariden**, exact fixture-content agreement with all **30 saved prediction files**, and an independent recount matching **90 per-seed statistic sets and all 120 printed seal04 values**. The seven new regression tests passed. Previously cleared items were not reopened.

VERDICT: PASS — scoped report-only repair certified | BLOCKERS: 0 | HIGH: 0