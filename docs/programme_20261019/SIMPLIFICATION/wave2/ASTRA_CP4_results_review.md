# ASTRA-CP4 — wave-2 release-v4 results certification

**PASS: the retest is interpretable and the reported verdicts are correct—overall H7 is refuted; add_corr confirms only on the primary view.**

Reviewed firsthand on 22 October 2026, read-only. Scope: `95241cd`; current HEAD `4883f2e` adds only the review brief. No files changed or jobs submitted.

## Findings — most severe first

1. **MEDIUM — one identified erroneous sf7 correction remains.**  
   Row `lekythos--3bfc4a385d61b883--s001-l0106` changes `στὴν᾿ Αθήνα.` to `στὴν᾿ Ἀθήνα.`, retaining the detached mark while adding another breathing. I rechecked the hash-matching crop and released labels. This qualifies correction quality; its effect on the trained models is unmeasured. Repair belongs in a future versioned overlay. It does not invalidate the measured comparison of these exact released arms. [Original finding](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/SIMPLIFICATION/wave2/ASTRA_CP3B_review_1.md:25).

2. **MEDIUM — one identified raw OCR error remains.**  
   Row `gazette_modern--dacf995fd419bebd--s000-l0113` retains `Χρξώστες Διάφοροι`; the hash-matching crop reads `Χρεώστες Διάφοροι`. It affects the shared raw-label supply of add/add_corr and is consistent with the preregistered recipe. Neither this observation nor the sf7 example establishes a population error rate or explains the observed CER differences. [Original finding](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/SIMPLIFICATION/wave2/ASTRA_CP3B_review_1.md:29).

3. **LOW — retry03’s “20 equal results” evidence is overstated.**  
   Retry03 logged **20 completed result IDs**, but persisted no corresponding metric dictionaries. The validation checks those IDs occur among the 90 compared results; it does not compare separately saved retry03 numbers. Describe this as completion coverage. Metric integrity is independently cleared by **90/90 full-result dictionary equality against the original production reports**, the unchanged scoring code, and my raw recount. [Validation code](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/out/runner2/aggregate/retry04/validate_real.py:48).

4. **LOW — all 13 relative evidence links in `RESULTS.md` are broken.**  
   The artifacts exist under `out/runner2`, rather than beneath the document’s directory. Correct the links; the underlying evidence is available. Working locations: [canonical report](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/out/runner2/aggregate/retry05/terminal_readback/outputs/report.json) and [FINAL_AUDIT.json](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/out/runner2/aggregate/retry05/FINAL_AUDIT.json).

## Cleared items

**Identity, recipe and completion**

- **573/573** archived source files match `e0735c1`. Live deployment matches that baseline with exactly the **eight documented aggregation-overlay files** matching `d9047e8`; zero unexpected mismatches. The factory executable also matches its deployment hash.
- Package manifest: `9c20f520fb4462c657a4f23bb7b0452ded9ddcd2a8c5a130965b40bffabd150b`.
- Bound inputs: `3af51068d7f80aa1fc4b0460fd7a1b87b00ed2c2ad5ae37d3a224375660dbb61`.
- All **nine runs** completed **eight epochs, 3,430,976 draws and 53,616 updates**. Common parameters match the registered recipe: codec v2.1, compact ×2, batch 64, accumulation 1, AdamW `1e-4/.05`, and validation-CER selection.
- Add/add_corr’s nonlabel draw files are hash-identical across **all eight epochs and all three allocations**.

| Arm | Unique real rows | Verified composition |
|---|---:|---|
| ctrl | 196,227 | Admitted native control pool |
| add | 364,173 | ctrl + 167,946 raw release rows |
| add_corr | 364,173 | Same membership and draws; registered corrections |

The release adds **50,622 W1 + 117,324 W2 rows**, with **zero raw-text hash failures**. All **364,173** union rows match final ADMIT/train decisions and crop identities. The admitted ledger contains **364,180** unique rows; the extra **seven** are absent from the native control pool.

Correction membership reproduces **904 sf7 + 167 RU1 + 0 N1 = 1,071** changes, with zero codec rejections. Their classes are **897 Greek polytonic, seven Greek–Latin, and 167 Cyrillic**. N1 receives no training treatment in this retest.

**Exposure**

The recount covers **2,253 test + 437 dev rows**, **2,690 unique keys/hashes**, **199 seal04 editions**, and all **200 SPLIT2 held-out editions**, including **99 forced editions**.

Every arm has **zero inventoried row/key, crop-hash, seal04-edition, SPLIT2-edition or protected-crop overlaps**. All **3,430,976 paired draw records** also have zero seal04 row-ID/image-hash matches, including **1,715,488 synthetic draws covering all 190,486 synthetic pool entries**. These checks establish the recorded exposure boundaries; canonical-work and broader provenance qualifications still apply.

**Aggregation and H1**

I independently recomputed strict edit distances for **931,752 prediction rows across 90 files**, checked their hashes and populations, and reproduced overall, source-class and required weak-slice counts. Full result dictionaries match the original arm reports **90/90**; seal04 score dictionaries match **18/18**. The aggregation change alters verification/I/O, with no observed metric change.

H1 is cleared in production: all **18 v2 view/run combinations** retain **221 numeric rows / 9,103 reference atoms**. `numerics_tables` remains a separate zero-support diagnostic.

## Recomputed preregistered results

CER below is the arithmetic mean across seeds 0/1/2. Decisions use exact fractions before rounding.

| View | Rows | Reference atoms per seed | ctrl CER % | add CER % | add_corr CER % |
|---|---:|---:|---:|---:|---:|
| Common `v2_test` | 42,038 | 2,489,622 | 1.235864 | 1.273781 | 1.268680 |
| Primary full coverage | 43,883 | 2,586,133 | 1.241751 | 1.279684 | 1.272995 |

Raw overall edit counts, seeds **0 / 1 / 2**:

| View | ctrl | add | add_corr |
|---|---|---|---|
| Common | 30,660 / 30,600 / 31,045 | 31,679 / 31,559 / 31,899 | 31,540 / 31,452 / 31,764 |
| Primary | 32,026 / 31,950 / 32,364 | 33,045 / 32,939 / 33,299 | 32,865 / 32,758 / 33,141 |

For H7_ADD, **ctrl − add must strictly exceed the control’s full seed range in every row below**. Units are percentage points.

| Slice | Common improvement | Common range | Primary improvement | Primary range | Gate, both views |
|---|---:|---:|---:|---:|---|
| Overall | −0.037917 | 0.017874 | −0.037933 | 0.016008 | FAIL |
| All caps | +0.504809 | 0.063765 | +0.510123 | 0.055795 | PASS |
| Numerics | +0.278297 | 0.472372 | +0.285620 | 0.472372 | FAIL |
| Punctuation-heavy | −0.202587 | 0.374007 | −0.212025 | 0.363471 | FAIL |
| Mixed script | −0.077247 | 0.018790 | −0.130699 | 0.009280 | FAIL |
| Frozen-source Cyrillic | +0.026621 | 0.070182 | −0.003054 | 0.050399 | FAIL |

Thus **H7_ADD_REFUTED in both views**.

For H7_ADD_CORR, each corrected source class must have a strictly positive **add − add_corr** mean difference. There is no seed-range requirement.

| Corrected class | Common support | Common gain, pp | Primary support | Primary gain, pp |
|---|---:|---:|---:|---:|
| Greek polytonic | 28,549 | +0.005530 | 28,587 | +0.005170 |
| Greek–Latin | 849 | +0.036996 | 854 | +0.037326 |
| Cyrillic | 1,742 | **−0.008470** | 3,510 | **+0.019281** |

Therefore:

- **Common:** `H7_ADD_REFUTED / H7_ADD_CORR_REFUTED`.
- **Primary:** `H7_ADD_REFUTED / H7_ADD_CORR_CONFIRMED`.
- **Overall H7: refuted**, because both primary contrasts must confirm.

The common view preserves the original codec-compatible population and factory references. Full coverage adds **1,845 recovered held-out rows**, including **1,768 Cyrillic rows**; shared references and crop hashes are identical. This support difference materially changes the Cyrillic correction contrast. The primary-view correction confirmation follows the preregistration, but remains a small, view-dependent result.

These numbers and verdicts match [RESULTS.md](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/RESULTS.md:19).

## Seal04 — diagnostic_only retained

I independently reproduced all **18** NFC/NFD/diacritic-insensitive CER, WER and exact-line summaries. Every run covers all test/dev rows without missing predictions.

NFC denominators are **65,627 test characters** and **12,628 dev characters**.

| Arm | Seed | Test edits | Test CER % | Dev edits | Dev CER % |
|---|---:|---:|---:|---:|---:|
| ctrl | 0 | 2,613 | 3.981593 | 678 | 5.369021 |
| ctrl | 1 | 2,735 | 4.167492 | 681 | 5.392778 |
| ctrl | 2 | 2,585 | 3.938928 | 687 | 5.440291 |
| add | 0 | 1,520 | 2.316120 | 510 | 4.038644 |
| add | 1 | 1,547 | 2.357261 | 477 | 3.777320 |
| add | 2 | 1,497 | 2.281073 | 488 | 3.864428 |
| add_corr | 0 | 1,512 | 2.303930 | 511 | 4.046563 |
| add_corr | 1 | 1,500 | 2.285645 | 488 | 3.864428 |
| add_corr | 2 | 1,476 | 2.249074 | 495 | 3.919861 |

Test means are **4.029338 → 2.318152 → 2.279550%**: add gains **1.711186 pp** over ctrl. The gain also appears under NFD scoring: **3.743660 → 2.160447%**. Corrections further improve test by **0.038602 pp**, while worsening dev by **0.050153 pp**.

Seal04 measures a selected new-source panel with pipeline-corrected, LF1-filtered references. The v2 instruments measure their frozen legacy reference populations. Stronger new-panel performance alongside a small legacy loss is interpretable; it does not replace the registered H7 gates. **`diagnostic_only` remains necessary** pending the outstanding checkpoint-exposure/work-identity review.

## Accounting and plan disposition

Live allocation-level `sacct -X` matches all **17** recorded attempts, including failures and aggregation retries.

| Scope | Requested GPU-h | Allocated GPU-h |
|---|---:|---:|
| Production | 35.491667 | 47.322222 |
| All attempts | **36.672500** | **69.255556** |

The requested-GPU basis has **313.327500 GPU-h headroom below 350**. Allocated hours include four-GPU nodes assigned to CPU-only jobs; retry03 alone accounts for **12.261111 allocated GPU-h**. Other S1 costs are excluded, so this does not certify cumulative series compliance.

**For the owner:** the wave-2 retest worked and gives a usable answer. Adding this supply at the fixed training budget substantially improves the new-source diagnostic panel, but fails the preregistered legacy-performance requirement. Corrections provide a small primary-view benefit with limited breadth. This establishes neither a data floor nor a reason to abandon scaling. **B.6 is cleared; the S1 ladder remains unchanged.** Carry this result into the C.3 packet, then obtain **CP4B review 2** before the eight-cell launch, retaining the separate **120-hour series caps** and measured-cost requirements. [Plan](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/SIMPLIFICATION/SIMPLIFICATION_AND_LAUNCH_PLAN.md:33).

VERDICT: PASS CP4; interpretable retest, overall H7 refuted, seal04 remains diagnostic_only | BLOCKERS: 0 | HIGH: 0