# ASTRA-TASK2 — independent results certification

**REQUEST CHANGES: the scores reproduce, but two scope errors prevent certification as the requested strict filtering-and-correction experiment.**

Reviewed [TASK2_RESULTS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/TASK2_RESULTS.md) at `66ea22d`. The current checkout, `804c8d2`, adds only the review brief. I independently recomputed CER from all 45 saved prediction files on Clariden, checked report hashes and training identities, and made no writes or submissions.

**Findings, most severe first**

1. **HIGH — “filtered” is not filtering only of the exact initial training population.**  
   Comparing the seven SHA-bound wave-1c training sidecars against the ctrl inventory gives:

   | Membership | Rows |
   |---|---:|
   | Initial wave-1c population | 211,451 |
   | Retained in ctrl | 195,346 |
   | Removed from wave-1c | 16,105 |
   | Added back by the newer admission | **881** |
   | Actual ctrl population | 196,227 |

   All 881 added-back rows failed the old admission: 874 on `lookalike_only_word`, seven on `unexpected_script`. Thus the contrast measures **replacement of the admission policy**, including reinstatements, rather than removal-only filtering of the initial recipe.

   This also refines the correction-placement claim: **166**, not 167, corrected rows belonged to the exact initial recipe. The remaining corrected row, `0b4bf868-p000657-l0027`, is among the 881 reinstatements. The report’s “strict arms” interpretation at [line 7](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/TASK2_RESULTS.md:7) needs correction. The existing numerical results remain valid for their actual populations.

2. **HIGH — the “cleaned” seal04 test is corrected but not admission-filtered.**  
   It retains **21 HOLD rows**: 2,232 ADMIT + 21 HOLD = 2,253. Dev contains 437 ADMIT rows.

   The written plan explicitly specifies an overlay-only seal04 variant; the implementation follows that wording. However, it does **not** satisfy this review mandate’s explicit admitted-only benchmark requirement. The missing variant can be obtained from existing predictions without training.

   My independent admitted-only, corrected seal04-test recount gives:

   | Arm | Reported overlay-only CER % | ADMIT-only corrected CER % |
   |---|---:|---:|
   | as-is | 3.735720 | **3.664098** |
   | ctrl | 3.738504 | **3.663167** |
   | ctrl_corr | 3.732008 | **3.658049** |
   | add | 2.156240 | **2.081937** |
   | add_corr | 2.125152 | **2.050294** |

   This does not reveal a convincing strict-arm improvement, but the requested benchmark variant must be distinguished from the reported one.

3. **MEDIUM — the filtering contrast also changes the model’s output vocabulary.**  
   Wave-1c uses **254 codec atoms**; ctrl/ctrl_corr use **265**, appending 11 Cyrillic atoms. Prefix compatibility preserves existing IDs but does not make the output heads identical. This disclosed caveat prevents attribution of the small as-is/ctrl differences solely to filtering. Ctrl versus ctrl_corr does share the codec, parameters, population and indexed draws.

4. **MEDIUM — the strict correction result has very limited coverage of the tools.**  
   Ctrl_corr changes **167/196,227 labels = 0.0851%**, all RU1; SF7 and N1 change zero. Add_corr contains the **same 167 RU1 corrections**, plus **904 SF7 corrections exclusively on release rows**. Consequently, the strict comparison cannot establish the value—or lack of value—of SF7 or N1.

**Recomputed scores and seed uncertainty**

Every reported overall score matched my independent edit-distance recount. These are arithmetic means of the three per-seed corpus CERs, in **NFD percent**:

| Panel | References | as-is | ctrl | ctrl_corr |
|---|---|---:|---:|---:|
| v2_test | Raw | 1.218873 | 1.235864 | 1.249668 |
| v2_test | Cleaned | 1.275119 | 1.276102 | 1.286952 |
| seal04 test | Raw | 3.740876 | 3.743660 | 3.738092 |
| seal04 test | Overlay-only | 3.735720 | 3.738504 | 3.732008 |
| seal04 dev | Raw | 5.081572 | 4.997308 | 5.023055 |
| seal04 dev | Overlay-only | 5.079231 | 4.994968 | 5.016034 |

The apparent discrepancy with earlier seal04 results is **NFC versus NFD**, not a changed score. For ctrl, the earlier NFC values are **3.981593 / 4.167492 / 3.938928**; their NFD counterparts are **3.701435 / 3.872656 / 3.656890**, exactly those used here. No DI CER is substituted.

Below, positive differences mean worse CER; all values are percentage points. “Filtering” refers to the actual admission-policy contrast identified above.

| Panel / references | Filtering: ctrl − as-is | Correction: ctrl_corr − ctrl | Both: ctrl_corr − as-is | Seed ranges: as-is / ctrl / ctrl_corr |
|---|---:|---:|---:|---|
| v2 raw | +0.016991 | +0.013804 | +0.030795 | 0.024662 / 0.017874 / 0.029000 |
| v2 cleaned | +0.000984 | +0.010849 | +0.011833 | 0.022582 / 0.014969 / 0.018861 |
| Seal test raw | +0.002784 | −0.005568 | −0.002784 | 0.087699 / 0.215766 / 0.137812 |
| Seal test overlay | +0.002784 | −0.006496 | −0.003712 | 0.090481 / 0.218547 / 0.143378 |
| Seal dev raw | −0.084264 | +0.025747 | −0.058516 | 0.294923 / 0.056176 / 0.007022 |
| Seal dev overlay | −0.084264 | +0.021066 | −0.063198 | 0.294923 / 0.042132 / 0.007022 |

The plain interpretation is:

- **Cleaned v2:** none of the three contrasts establishes an effect beyond seed uncertainty. Filtering is essentially tied; correction worsens all three matched seeds, but its magnitude is uncertain.
- **Raw v2:** there is a consistent deterioration signal. Filtering worsens all three matched seeds; an exploratory paired 95% t interval is **+0.005492 to +0.028489 pp**. Both changes together also worsen every seed, and their observed arm ranges do not overlap. Nevertheless, the paired interval for “both” includes zero, and the population/codec changes prevent a filtering-only causal claim. Correction alone is not resolved beyond seed uncertainty.
- **Seal04 test and dev, under either reference variant:** none of the three strict-arm contrasts is distinguishable from seed noise in these results.

The intervals are descriptive, assumption-dependent checks with **three seeds**, not new preregistered significance or H7 verdicts.

**The release-data extras**

| Panel | ctrl → add, raw / cleaned change | add → add_corr, raw / cleaned change |
|---|---:|---:|
| v2_test | +0.037917 / +0.014756 | −0.005101 / −0.006088 |
| Seal04 test | −1.583214 / −1.582264 | −0.031089 / −0.031088 |
| Seal04 dev | −1.380989 / −1.376308 | +0.051495 / +0.046813 |

Adding the release population produces a **large seal04 improvement, clearly exceeding seed variation**, while worsening v2. That is a useful data-expansion result, not a universal improvement.

Corrections in the expanded population produce a **small, consistent v2 improvement in all three matched seeds**. Exploratory paired intervals exclude zero for raw and cleaned v2, supporting a small signal within this experiment. Seal04 test also improves in all three pairs, but its **−0.0311 pp** mean effect remains uncertain; dev worsens in all three pairs. The corrections therefore show some value, but not a consistent benchmark-wide gain.

**Cleared items**

- **Reference consistency:** all five arms use identical reference identities and labels for each reported variant. Cleaned v2 contains **39,434 ADMIT rows**, excluding 1,634 DROP and 970 HOLD rows; its **426 label changes comprise 305 polytonic and 121 Cyrillic corrections**. Replaying their recorded edits produced zero mismatches. Numerics support is **175** in every cleaned arm, versus 221 raw.
- **Benchmark overlays:** the same six test and one dev label changes are applied to every arm. They replay the selected correctors’ recorded edits; they are not an independent human adjudication of those tools.
- **Arm and checkpoint identity:** all 15 run receipts show from-scratch training, seeds 0/1/2, eight epochs, **53,616 updates**, and `val_cer` selection. Baseline scoring uses the existing wave-1c checkpoints. Ctrl and ctrl_corr parameters agree apart from the training-mix path; their indexed-draw hash and all eight underlying ctrl draw hashes agree.
- **Exposure checks:** independent recounts found zero benchmark row-ID, recorded edition-ID and recorded crop-hash overlaps for the wave-2 inventories. Wave-1c likewise has zero row-ID and recorded original-crop overlaps; its book-ID mapping agrees with the shared inventory rows and shows zero benchmark overlap. Ctrl_corr inherits ctrl’s unchanged identities. These checks do **not** resolve canonical-work or historical checkpoint exposure: seal04 correctly remains `diagnostic_only`.
- **Accounting:** the 25 recorded allocation rows sum to **44.441389 requested / 81.453333 allocated GPU-hours**; requested reservations total **222.75 GPU-hours**, below 350. Historical wave-1c training and S1 remain excluded.

**For the owner**

The current results **do not demonstrate that filtering and correcting the initial recipe improves the model**. On the cleaned internal test, filtering is effectively tied and adding corrections is slightly worse; the tiny benchmark differences are within seed uncertainty. The correction tools are not shown to be useless: this strict arm exercises only 167 RU1 changes, while the expanded-data experiment shows a small, consistent internal-test benefit from its combined correction overlay. The substantial benchmark gain comes from adding release data. Before treating Task 2 as settled, the report must acknowledge the 881 reinstated training rows and supply the admitted-only benchmark scores.

**One next experiment:** run one controlled three-arm ablation using the exact **211,451-row initial population**, its **195,346-row census-admitted intersection**, and that identical intersection with its **166 reachable corrections**. Hold the original model/codec, validation, training budget and sampling procedure fixed; use enough matched seeds for a prespecified useful effect size. Score every arm on raw and admitted-only corrected references, including the **2,232-row** benchmark test. This would isolate the initial-recipe question; SF7 remains outside that population’s correction coverage.

VERDICT: REQUEST CHANGES — numerical scores verified; strict training-population and cleaned-benchmark scope not satisfied | BLOCKERS: 0 | HIGH: 2