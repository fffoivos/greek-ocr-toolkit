R2a admits 1,572 print-checked slots against the plan's 4,000; per-slice deficits recorded in B6_RESOLVE_REPORT.md; top-up reading paused by the owner (17 Oct)

# R2a digest — job 3683130

Job COMPLETED, exit 0:0; Slurm elapsed 23:29. The log ends with STAGE_DONE C and STAGE_DONE D. Readback finished 2026-10-17T14:32:46.461834+00:00. 160 files / 115957160 bytes verified; 153 stage-bound and seven remote-envelope-bound. No crops, arrays, windows or shards were pulled. The archived failed first run was not read or scored.

The branch is `opus/r2-prep`. Package verifier binds commit `ee9d7a9757fe8f9b9e2bf50ee299cb587c246c72`; current checkout HEAD is `5080db4a80b00d138e4ff333cae0d862b4ea61c4` (later lead history; `a0ec0c1f4` is the accepted VERIFY_OK receipt commit). No git writes, certificate refresh, inference or submission in this readback.

Scorer: R2S, inserted recogniser slots UNKNOWN. Overlay v1.1 is applied symmetrically; local regeneration reproduces all six held-out ledgers exactly. Saved DEV ledgers independently reproduce their score summaries. Six arms: R1-A s16, BASE s17/s18, R2a s16/s17/s18. “BASE” pooled below uses R1-A as the seed-16 baseline, not a newly trained BASE s16.

## (a) Timings

| Stage | Actual min | Forecast min | Actual − forecast min |
|---|---|---|---|
| A | 0.000 | 0 | not separately forecast |
| B | 0.931 | 15.9 | -14.969 |
| C | 19.437 | 17.5 | 1.937 |
| D | 1.756 | 20 | -18.244 |

Stage total 22.124 min; Slurm 23.483 min versus 53.4 min forecast (-29.917 min, 56.0% shorter). Stage A receipt times the post-validation closure (approximately zero), not complete startup/validation. Unattributed Slurm/startup overhead: 1.360 min. Forecast components are rounded (sum 53.4 min).

## (b) Target witnesses

Anchor target heads only, noncontrol T4 capitals / omicron_monotonic / subscript. Unknown truth or missing/ambiguous predictions remain excluded and counted. Pooled totals are seed-observations, not three times as many independent witnesses. Document resampling keeps all seeds for the same document together. Fifty thousand bootstrap replicates; fixed seed 20261017. Both absolute false-addition reduction and percentage reduction intervals are reported.

| Pair | Known / UNKNOWN | False additions BASE → R2a | Reduction % [95% CI] | Wrong BASE → R2a | False-addition count reduction CI | Net fewer wrong [95% CI] |
|---|---|---|---|---|---|---|
| 16 | 277 / 17 | 10 → 11 | -10.000 [-77.778, 38.462] | 33 → 18 | [-7.0, 4.0] | 15 [5.0, 25.0] |
| 17 | 277 / 17 | 6 → 4 | 33.333 [0.000, 100.000] | 32 → 12 | [0.0, 5.0] | 20 [12.0, 29.0] |
| 18 | 277 / 17 | 10 → 8 | 20.000 [-25.000, 50.000] | 39 → 12 | [-2.0, 6.0] | 27 [17.0, 37.0] |
| pooled | 831 / 51 | 26 → 23 | 11.538 [-16.667, 34.887] | 104 → 42 | [-3.0, 9.0] | 62 [39.0, 86.0] |

Per-slice negatives and positive exact-target recall:

| Pair | Slice | Negative / positive | False additions BASE → R2a | Positive correct BASE → R2a | Recall % BASE → R2a |
|---|---|---|---|---|---|
| 16 | subscript | 49 / 50 | 0 → 0 | 50 → 50 | 100.000 → 100.000 |
| 16 | capitals | 38 / 48 | 2 → 2 | 26 → 42 | 54.167 → 87.500 |
| 16 | omicron_monotonic | 48 / 44 | 8 → 9 | 43 → 43 | 97.727 → 97.727 |
| 17 | subscript | 49 / 50 | 0 → 0 | 49 → 50 | 98.000 → 100.000 |
| 17 | capitals | 38 / 48 | 1 → 1 | 23 → 40 | 47.917 → 83.333 |
| 17 | omicron_monotonic | 48 / 44 | 5 → 3 | 44 → 44 | 100.000 → 100.000 |
| 18 | subscript | 49 / 50 | 0 → 0 | 50 → 50 | 100.000 → 100.000 |
| 18 | capitals | 38 / 48 | 2 → 1 | 19 → 44 | 39.583 → 91.667 |
| 18 | omicron_monotonic | 48 / 44 | 8 → 7 | 44 → 44 | 100.000 → 100.000 |
| pooled | subscript | 147 / 150 | 0 → 0 | 149 → 150 | 99.333 → 100.000 |
| pooled | capitals | 114 / 144 | 5 → 4 | 68 → 126 | 47.222 → 87.500 |
| pooled | omicron_monotonic | 144 / 132 | 21 → 19 | 131 → 131 | 99.242 → 99.242 |

False-addition benefit occurs in 2/3 seeds; mean count reduction 1.000 per seed. Only seed 17 reaches the 30% threshold. Positive slice recall is nondecreasing in every seed: True; individual positive regressions remain in the paired ledger. Target verdict **FAIL**: pooled reduction is below 30%, and its interval includes no improvement. Net wrong-slot improvement alone does not pass the target criterion.

## (c) Common-class noninferiority

Exact named one-vs-rest head classes with ≥200 printed positive slots per seed. Paired document bootstrap, original weights retained. Basic one-sided bounds and null-centered bootstrap p-values, Holm step-down over all seed and pooled P/R endpoints in this family. P margin −0.20 pp; R margin −0.50 pp. Holm lower bounds are at the displayed step alpha; after a step fails, later steps cannot pass. FAIL requires a simultaneous Bonferroni upper bound at or below the margin; other unproven rows are INCONCLUSIVE. Bootstrap inference is approximate; undefined resampled denominators are excluded and recorded.

| Pair/class or slice | Metric | Support | BASE % | R2a % | Δ pp | Holm lower pp | Simultaneous upper pp | Holm p | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 16/breathing/psili | P | 966 | 98.256 | 99.272 | 1.015 | -17.481 | 1.970 | 1.000 | INCONCLUSIVE |
| 16/breathing/psili | R | 966 | 99.172 | 98.758 | -0.414 | -4.532 | 5.638 | 1.000 | INCONCLUSIVE |
| 16/breathing/dasia | P | 356 | 98.592 | 98.045 | -0.547 | -5.996 | 11.810 | 1.000 | INCONCLUSIVE |
| 16/breathing/dasia | R | 356 | 98.315 | 98.596 | 0.281 | -1.133 | 0.562 | 1.000 | INCONCLUSIVE |
| 16/accent/acute | P | 1794 | 99.498 | 99.332 | -0.166 | -0.612 | -0.029 | 1.000 | INCONCLUSIVE |
| 16/accent/acute | R | 1794 | 99.498 | 99.443 | -0.056 | -0.111 | 1.815 | 0.001 | PASS |
| 16/accent/grave | P | 679 | 98.394 | 98.684 | 0.290 | -4.267 | 0.580 | 1.000 | INCONCLUSIVE |
| 16/accent/grave | R | 679 | 99.264 | 99.411 | 0.147 | -0.143 | 0.295 | 0.001 | PASS |
| 16/accent/circumflex | P | 404 | 98.997 | 98.263 | -0.734 | -1.469 | 3.009 | 1.000 | INCONCLUSIVE |
| 16/accent/circumflex | R | 404 | 97.772 | 98.020 | 0.248 | 0.107 | 0.495 | 0.001 | PASS |
| 17/breathing/psili | P | 966 | 99.373 | 98.966 | -0.407 | -1.072 | 1.913 | 1.000 | INCONCLUSIVE |
| 17/breathing/psili | R | 966 | 98.447 | 99.068 | 0.621 | -7.169 | 1.242 | 1.000 | INCONCLUSIVE |
| 17/breathing/dasia | P | 356 | 96.712 | 96.685 | -0.027 | -8.642 | 8.699 | 1.000 | INCONCLUSIVE |
| 17/breathing/dasia | R | 356 | 99.157 | 98.315 | -0.843 | -1.685 | 6.209 | 1.000 | INCONCLUSIVE |
| 17/accent/acute | P | 1794 | 99.220 | 98.510 | -0.711 | -3.564 | -0.303 | 1.000 | FAIL |
| 17/accent/acute | R | 1794 | 99.331 | 99.498 | 0.167 | -2.197 | 0.334 | 1.000 | INCONCLUSIVE |
| 17/accent/grave | P | 679 | 98.675 | 98.825 | 0.151 | -0.122 | 5.010 | 0.001 | PASS |
| 17/accent/grave | R | 679 | 98.675 | 99.116 | 0.442 | -4.863 | 0.884 | 1.000 | INCONCLUSIVE |
| 17/accent/circumflex | P | 404 | 98.972 | 99.213 | 0.241 | -3.118 | 0.529 | 1.000 | INCONCLUSIVE |
| 17/accent/circumflex | R | 404 | 95.297 | 93.564 | -1.733 | -3.465 | -0.752 | 1.000 | FAIL |
| 18/breathing/psili | P | 966 | 98.356 | 98.657 | 0.301 | -4.813 | 5.370 | 1.000 | INCONCLUSIVE |
| 18/breathing/psili | R | 966 | 99.068 | 98.861 | -0.207 | -1.087 | 5.040 | 1.000 | INCONCLUSIVE |
| 18/breathing/dasia | P | 356 | 98.028 | 97.746 | -0.282 | -8.256 | 5.478 | 1.000 | INCONCLUSIVE |
| 18/breathing/dasia | R | 356 | 97.753 | 97.472 | -0.281 | -0.562 | 7.131 | 1.000 | INCONCLUSIVE |
| 18/accent/acute | P | 1794 | 99.387 | 99.553 | 0.166 | -1.339 | 2.737 | 0.985 | INCONCLUSIVE |
| 18/accent/acute | R | 1794 | 99.443 | 99.331 | -0.111 | -0.223 | 6.110 | 0.001 | PASS |
| 18/accent/grave | P | 679 | 98.246 | 98.392 | 0.146 | -7.547 | 2.298 | 1.000 | INCONCLUSIVE |
| 18/accent/grave | R | 679 | 98.969 | 99.116 | 0.147 | -2.736 | 4.550 | 1.000 | INCONCLUSIVE |
| 18/accent/circumflex | P | 404 | 98.985 | 97.531 | -1.454 | -2.899 | 6.896 | 1.000 | INCONCLUSIVE |
| 18/accent/circumflex | R | 404 | 96.535 | 97.772 | 1.238 | -8.940 | 6.010 | 1.000 | INCONCLUSIVE |
| pooled/breathing/psili | P | 2898 | 98.657 | 98.964 | 0.307 | -7.850 | 1.792 | 1.000 | INCONCLUSIVE |
| pooled/breathing/psili | R | 2898 | 98.896 | 98.896 | 0.000 | -3.960 | 3.401 | 1.000 | INCONCLUSIVE |
| pooled/breathing/dasia | P | 1068 | 97.767 | 97.488 | -0.279 | -4.337 | 5.310 | 1.000 | INCONCLUSIVE |
| pooled/breathing/dasia | R | 1068 | 98.408 | 98.127 | -0.281 | -0.562 | 2.717 | 1.000 | INCONCLUSIVE |
| pooled/accent/acute | P | 5382 | 99.369 | 99.129 | -0.239 | -1.523 | -0.038 | 1.000 | INCONCLUSIVE |
| pooled/accent/acute | R | 5382 | 99.424 | 99.424 | 0.000 | -0.496 | 1.968 | 0.048 | PASS |
| pooled/accent/grave | P | 2037 | 98.438 | 98.633 | 0.196 | -2.833 | 0.934 | 1.000 | INCONCLUSIVE |
| pooled/accent/grave | R | 2037 | 98.969 | 99.215 | 0.245 | -1.790 | 1.200 | 1.000 | INCONCLUSIVE |
| pooled/accent/circumflex | P | 1212 | 98.985 | 98.318 | -0.667 | -1.226 | 2.020 | 1.000 | INCONCLUSIVE |
| pooled/accent/circumflex | R | 1212 | 96.535 | 96.452 | -0.083 | -3.674 | 1.013 | 1.000 | INCONCLUSIVE |

Common-class verdict **FAIL**.

Sparse classes remain **unestablished**, including after seed pooling. Exact-name errors count FP + FN; a wrong-name substitution can count twice. Every changed paired slot, including each head regression, is in [paired ledgers](evidence/r2a/r2rb2_paired_slots.json).

| Pair | Class | Support/seed | Errors BASE → R2a | Status |
|---|---|---|---|---|
| 16 | dialytika/dialytika | 4 | 0.0 → 0.0 | unestablished |
| 16 | subscript/subscript | 94 | 7.0 → 6.0 | unestablished |
| 17 | dialytika/dialytika | 4 | 0.0 → 1.0 | unestablished |
| 17 | subscript/subscript | 94 | 10.0 → 8.0 | unestablished |
| 18 | dialytika/dialytika | 4 | 0.0 → 0.0 | unestablished |
| 18 | subscript/subscript | 94 | 5.0 → 6.0 | unestablished |
| pooled | dialytika/dialytika | 4 | 0.0 → 1.0 | unestablished |
| pooled | subscript/subscript | 94 | 22.0 → 20.0 | unestablished |

Every sparse-class paired regression (exact-name correctness lost; no waiver):

| Seed | Class | Line / slot | Truth | BASE → R2a |
|---|---|---|---|---|
| 16 | subscript/subscript | 384c3f89-p000053-l0021:s8 | [0, 0, 0, 0] | [0, 0, 0, 0] → [0, 0, 0, 1] |
| 17 | subscript/subscript | 177b717d-p000054-l0004:s4 | [1, 3, 0, 0] | [1, 3, 0, 0] → [1, 3, 0, 1] |
| 17 | dialytika/dialytika | 177b717d-p000017-l0012:s24 | [0, 3, 0, 0] | [0, 3, 0, 0] → [0, 3, 1, 0] |
| 18 | subscript/subscript | 22fda82b-p000063-l0039:s10 | [0, 3, 0, 1] | [0, 3, 0, 1] → [0, 3, 0, 0] |

Sparse protection verdict **FAIL**; no adoption from sparse evidence.

## (d) Non-target and owner protection

Random, specks and exact_names T4 slices: exact named-head micro P/R, paired by physical slot within each slice (overlapping cards deduplicated). Same margins; one Holm family over the three slices × four comparisons × two metrics. Original per-seed positive supports are only 114, 144 and 171; these slices remain unestablished despite larger pooled observation counts. Full churn and every paired regression are retained, including regressions that a net count would hide.

| Pair/class or slice | Metric | Support | BASE % | R2a % | Δ pp | Holm lower pp | Simultaneous upper pp | Holm p | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 16/exact_names | P | 114 | 94.783 | 93.913 | -0.870 | -4.848 | 6.443 | 1.000 | INCONCLUSIVE |
| 16/exact_names | R | 114 | 95.614 | 94.737 | -0.877 | -3.917 | 4.394 | 1.000 | INCONCLUSIVE |
| 16/random | P | 144 | 93.289 | 92.715 | -0.573 | -4.002 | 2.860 | 1.000 | INCONCLUSIVE |
| 16/random | R | 144 | 96.528 | 97.222 | 0.694 | -1.683 | 1.389 | 1.000 | INCONCLUSIVE |
| 16/specks | P | 171 | 89.247 | 90.860 | 1.613 | -2.212 | 5.529 | 1.000 | INCONCLUSIVE |
| 16/specks | R | 171 | 97.076 | 98.830 | 1.754 | -1.157 | 3.509 | 0.288 | INCONCLUSIVE |
| 17/exact_names | P | 114 | 94.737 | 95.652 | 0.915 | -2.353 | 1.956 | 1.000 | INCONCLUSIVE |
| 17/exact_names | R | 114 | 94.737 | 96.491 | 1.754 | -3.085 | 6.570 | 1.000 | INCONCLUSIVE |
| 17/random | P | 144 | 95.890 | 97.279 | 1.389 | -2.933 | 5.474 | 1.000 | INCONCLUSIVE |
| 17/random | R | 144 | 97.222 | 99.306 | 2.083 | -1.345 | 4.167 | 0.320 | INCONCLUSIVE |
| 17/specks | P | 171 | 93.220 | 94.915 | 1.695 | -2.173 | 5.936 | 1.000 | INCONCLUSIVE |
| 17/specks | R | 171 | 96.491 | 98.246 | 1.754 | -3.094 | 6.350 | 1.000 | INCONCLUSIVE |
| 18/exact_names | P | 114 | 96.522 | 95.614 | -0.908 | -1.815 | 1.316 | 1.000 | INCONCLUSIVE |
| 18/exact_names | R | 114 | 97.368 | 95.614 | -1.754 | -3.509 | 2.325 | 1.000 | INCONCLUSIVE |
| 18/random | P | 144 | 93.333 | 97.279 | 3.946 | -5.441 | 10.484 | 1.000 | INCONCLUSIVE |
| 18/random | R | 144 | 97.222 | 99.306 | 2.083 | -4.104 | 7.244 | 1.000 | INCONCLUSIVE |
| 18/specks | P | 171 | 92.737 | 94.915 | 2.178 | -2.949 | 6.564 | 1.000 | INCONCLUSIVE |
| 18/specks | R | 171 | 97.076 | 98.246 | 1.170 | -2.367 | 4.300 | 1.000 | INCONCLUSIVE |
| pooled/exact_names | P | 342 | 95.349 | 95.058 | -0.291 | -1.910 | 2.108 | 1.000 | INCONCLUSIVE |
| pooled/exact_names | R | 342 | 95.906 | 95.614 | -0.292 | -1.759 | 1.754 | 1.000 | INCONCLUSIVE |
| pooled/random | P | 432 | 94.157 | 95.730 | 1.573 | -2.376 | 4.841 | 1.000 | INCONCLUSIVE |
| pooled/random | R | 432 | 96.991 | 98.611 | 1.620 | -1.412 | 3.950 | 0.465 | INCONCLUSIVE |
| pooled/specks | P | 513 | 91.697 | 93.519 | 1.821 | -1.281 | 4.667 | 0.613 | INCONCLUSIVE |
| pooled/specks | R | 513 | 96.881 | 98.441 | 1.559 | -1.620 | 4.390 | 0.636 | INCONCLUSIVE |

Non-target margin verdict **INCONCLUSIVE**.

Owner-note protection verdict **FAIL**. Conservative scope: every known held-out slot on any owner-note line from seven frozen note files, rather than only the named owner slots. Every paired regression on that superset is shown below, including a head lost while another head improves. Disposition: observed regression retained, not waived; no new print adjudication. The FAIL is supported by the explicitly named preserved slot `602cc72e-p000167-l0027:s10`: seed 18 changes correct grave-only to psili+grave. Other regressions in the broader line scope are also retained. Missing owner lines remain unestablished; see [owner ledger](evidence/r2a/r2rb2_owner_regressions.json).

| Seed | Line id / slot | Truth | BASE → R2a | Head regressions | Named owner slot | Disposition |
|---|---|---|---|---|---|---|
| 16 | 384c3f89-p000050-l0027:s3 | [2, 0, 0, 0] | [2, 0, 0, 0] → [1, 3, 0, 0] | breathing,accent | False | retained; not waived |
| 16 | 384c3f89-p000053-l0021:s8 | [0, 0, 0, 0] | [0, 0, 0, 0] → [0, 0, 0, 1] | subscript | False | retained; not waived |
| 16 | 9c1dca9b-p000005-l0017:s14 | [0, 1, 0, 0] | [1, 1, 0, 0] → [0, 3, 0, 0] | accent | False | retained; not waived |
| 16 | 384c3f89-p000091-l0014:s10 | [1, 3, 0, 0] | [1, 3, 0, 0] → [0, 3, 0, 0] | breathing | False | retained; not waived |
| 17 | 384c3f89-p000030-l0029:s12 | [0, 3, 0, 0] | [0, 3, 0, 0] → [0, 1, 0, 0] | accent | False | retained; not waived |
| 17 | 177b717d-p000017-l0012:s24 | [0, 3, 0, 0] | [0, 3, 0, 0] → [0, 3, 1, 0] | dialytika | False | retained; not waived |
| 17 | 384c3f89-p000059-l0027:s1 | [2, 3, 0, 0] | [2, 3, 0, 0] → [2, 0, 0, 0] | accent | False | retained; not waived |
| 18 | 9c1dca9b-p000015-l0067:s13 | [0, 3, 0, 1] | [0, 3, 0, 1] → [0, 2, 0, 1] | accent | False | retained; not waived |
| 18 | 602cc72e-p000113-l0009:s10 | [2, 0, 0, 0] | [2, 0, 0, 0] → [1, 1, 0, 0] | breathing,accent | False | retained; not waived |
| 18 | 602cc72e-p000167-l0027:s10 | [0, 2, 0, 0] | [0, 2, 0, 0] → [1, 2, 0, 0] | breathing | True | retained; not waived |
| 18 | 384c3f89-p000091-l0039:s1 | [1, 0, 0, 0] | [1, 0, 0, 0] → [1, 3, 0, 0] | accent | False | retained; not waived |
| 18 | 384c3f89-p000030-l0029:s12 | [0, 3, 0, 0] | [0, 3, 0, 0] → [2, 1, 0, 0] | breathing,accent | False | retained; not waived |

## (e) DEV

S8 census: 600 lines, 1,793 items. Controls and unresolved truth excluded from accuracy, with all item states retained. “Item accuracy” means all known union slots correct for a resolved noncontrol item; UNKNOWN slots are excluded, so this is mark accuracy conditional on known aligned truth, not whole OCR transcription accuracy. Weighted figures retain S8 inclusion weights.

| Arm | Correct / scored items | Item accuracy % | Weighted item % | Weighted slot % | Exclusions |
|---|---|---|---|---|---|
| A16 | 913 / 968 | 94.318 | 96.623 | 99.325 | {'scored': 968, 'excluded_control': 144, 'unscored': 8, 'excluded_unresolved': 673} |
| BASEs17 | 915 / 968 | 94.525 | 96.320 | 99.285 | {'scored': 968, 'excluded_control': 144, 'unscored': 8, 'excluded_unresolved': 673} |
| BASEs18 | 918 / 968 | 94.835 | 96.839 | 99.385 | {'scored': 968, 'excluded_control': 144, 'unscored': 8, 'excluded_unresolved': 673} |
| R2a20261016 | 919 / 968 | 94.938 | 96.667 | 99.348 | {'scored': 968, 'excluded_control': 144, 'unscored': 8, 'excluded_unresolved': 673} |
| R2a20261017 | 923 / 968 | 95.351 | 97.162 | 99.443 | {'scored': 968, 'excluded_control': 144, 'unscored': 8, 'excluded_unresolved': 673} |
| R2a20261018 | 919 / 968 | 94.938 | 96.484 | 99.313 | {'scored': 968, 'excluded_control': 144, 'unscored': 8, 'excluded_unresolved': 673} |

Paired item results (R2a − baseline), clustered by original document:

| Seed | Recoveries / regressions | Weighted Δ pp | 95% CI pp |
|---|---|---|---|
| 16 | 14 / 8 | 0.044 | [-0.9919, 0.8356] |
| 17 | 14 / 6 | 0.842 | [0.1589, 1.8109] |
| 18 | 11 / 10 | -0.356 | [-1.3821, 0.3843] |

The closing DEV figure is the mean weighted item accuracy across the three paired seeds (96.594% → 96.771%). All 1,793 per-arm item states, wave counts and paired per-item changes are in [DEV items](evidence/r2a/r2rb2_dev_items.json) and [DEV summary](evidence/r2a/r2rb2_dev_summary.json). No prospective DEV noninferiority margin was specified, so DEV is descriptive and does not independently authorize adoption.

## (f) Seed spread and churn

| Arm | Held-out P % | R % | F1 % |
|---|---|---|---|
| A16 | 98.907 | 98.999 | 98.953 |
| BASEs17 | 98.947 | 98.418 | 98.682 |
| BASEs18 | 98.836 | 98.767 | 98.801 |
| R2a20261016 | 98.999 | 98.976 | 98.988 |
| R2a20261017 | 98.557 | 98.534 | 98.545 |
| R2a20261018 | 98.836 | 98.767 | 98.801 |

| Metric | R2a max−min pp | Job-1 BASE spread pp |
|---|---|---|
| P | 0.442 | 0.13 |
| R | 0.442 | 0.54 |
| F1 | 0.442 | 0.35 |

The comparison is observed range across three R2a seeds, not a confidence interval or causal variance estimate. Job-1 reference ranges (P 0.13, R 0.54, F1 0.35 pp) are the supplied reference figures; the table above also exposes all baseline metrics under the current R2S/v1.1 instrument.

| Seed | Slice | Changed physical slots |
|---|---|---|
| 16 | capitals | 35 |
| 16 | exact_names | 10 |
| 16 | omicron_monotonic | 7 |
| 16 | random | 11 |
| 16 | specks | 14 |
| 16 | subscript | 0 |
| 17 | capitals | 28 |
| 17 | exact_names | 5 |
| 17 | omicron_monotonic | 3 |
| 17 | random | 6 |
| 17 | specks | 11 |
| 17 | subscript | 4 |
| 18 | capitals | 34 |
| 18 | exact_names | 4 |
| 18 | omicron_monotonic | 9 |
| 18 | random | 8 |
| 18 | specks | 10 |
| 18 | subscript | 0 |

Churn counts any prediction tuple change, including UNKNOWN truth; overlapping T4 cards are deduplicated within slice. Held-out and DEV churn and full old/new tuples are in [spread/churn](evidence/r2a/r2rb2_spread_churn.json) and [paired slots](evidence/r2a/r2rb2_paired_slots.json).

## (g) Verdict

| Check | Verdict |
|---|---|
| R2a target benefit | FAIL |
| Common-class noninferiority | FAIL |
| Sparse exact-name protection | FAIL |
| Non-target witness margins | INCONCLUSIVE |
| Preserved owner witness protection | FAIL |
| DEV | INCONCLUSIVE (descriptive; no adoption margin) |
| Overall R2a adoption | FAIL |

R2a does not meet the target false-addition criterion. Protection results are limited to their table rows; an INCONCLUSIVE result does not adopt. Overall **FAIL**.

Validation: **76 passed in 24.08s** (R2, population, readback, package, digest and frozen-policy suites); results in `evidence/r2a/r2rb2_tests.log`. Readback receipt: `artifacts/labelfix_r2/output_3683130/READBACK_RECEIPT.json`.

R2RB2 READY: readback 160 sha ok; R2a target false additions BASE 26 → R2a 23 (11.538%, CI -16.667..34.887%); seeds benefit 2/3; noninferiority common FAIL, sparse FAIL, non-target INCONCLUSIVE, owner FAIL; DEV 96.594%→96.771%; verdict FAIL
