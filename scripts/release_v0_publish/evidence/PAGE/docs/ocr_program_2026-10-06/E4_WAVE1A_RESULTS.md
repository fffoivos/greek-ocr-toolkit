# E4 wave 1a results

All 18 submitted runs completed eight epochs: six configurations × three seeds (0, 1, 2), on four instruments. The three grave runs were deferred. The raw aggregate remains `PARTIAL` and its report `complete=false` because historical failed allocations and the nominal 21-arm set remain visible; `recovery_readout.json` records `BASE_DONE`, `base_complete=true`, and 18 successful unique arms.

Readback verification: **FAIL** (189 passed checks, 4 failed checks). Mac/Clariden SHA256 mismatches: **0**. Verification failures remain explicit; completed training is separate from missing aggregate evidence.

Sources: [report.json](../../out/e4/wave1a/aggregate_retry2/report.json), [original RESULT_DIGEST.md](../../out/e4/wave1a/aggregate_retry2/RESULT_DIGEST.md), [recovery_readout.json](../../out/e4/wave1a/aggregate_retry2/recovery_readout.json), [verification.json](../../out/e4/wave1a_readback/verification.json).

## Binding and readout rule

Release: `v2-asis`, `af1ff90200e8ad897e246192da9a420a15fec2793fbc987649dbf2ff77d81621`; codec v1. The release and codec are bound transitively by each immutable run binding’s node-binding hash, the node’s release hash and input inventory, and `release.json`. All controls are fresh. E3 full has a different binding and appears only as a historical reference.

Metric copied from the report: **strict NFD codepoints; literal predictions unchanged**. All CER means/minima/maxima below are percentages; seed ranges and Δ are percentage points (pp). Means are arithmetic means over three model seeds. Δ = candidate mean − ctrl mean; negative is lower CER. **Beyond seed range = `abs(Δ) > max(range_arm, range_ctrl)`**, evaluated using unrounded report values; “yes” can describe either improvement or regression. This is the stated descriptive seed-range rule, not a confidence interval or the preregistered book-bootstrap/δ null-result test.

Geometry-clean v2_test secondary column: **skipped**; the requested local artifacts-calibrated list was absent. No geometry-clean or corrected-label score is inferred.

## Instrument totals

### v2_test

| Arm | Seeds | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ctrl | 3 | 1.367276 | 1.355708 | 1.376514 | 0.020806 | +0.000000 | no |
| syn40 | 3 | 1.356431 | 1.350848 | 1.365348 | 0.014500 | -0.010845 | no |
| syn60 | 3 | 1.409022 | 1.385833 | 1.444316 | 0.058483 | +0.041747 | no |
| w15 | 3 | 1.267984 | 1.250712 | 1.288388 | 0.037676 | -0.099292 | yes |
| w20 | 3 | 1.234177 | 1.216771 | 1.251355 | 0.034584 | -0.133099 | yes |
| m1 | 3 | 1.407469 | 1.391898 | 1.432306 | 0.040408 | +0.040194 | no |
| E3 full (different binding) | reference | 1.37 | — | — | — | — | not comparable |

### wikisource_human

| Arm | Seeds | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ctrl | 3 | 3.314621 | 3.300426 | 3.327526 | 0.027100 | +0.000000 | no |
| syn40 | 3 | 3.321074 | 3.300426 | 3.333333 | 0.032907 | +0.006452 | no |
| syn60 | 3 | 3.326881 | 3.286876 | 3.354626 | 0.067751 | +0.012260 | no |
| w15 | 3 | 3.257840 | 3.213318 | 3.292683 | 0.079365 | -0.056782 | no |
| w20 | 3 | 3.248161 | 3.224932 | 3.284940 | 0.060008 | -0.066460 | yes |
| m1 | 3 | 3.382372 | 3.323655 | 3.449477 | 0.125823 | +0.067751 | no |
| E3 full (different binding) | reference | 3.33 | — | — | — | — | not comparable |

### e1_real_test

| Arm | Seeds | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ctrl | 3 | 1.060950 | 1.041959 | 1.075260 | 0.033301 | +0.000000 | no |
| syn40 | 3 | 1.056938 | 1.029522 | 1.074859 | 0.045337 | -0.004012 | no |
| syn60 | 3 | 1.057607 | 1.043965 | 1.068038 | 0.024073 | -0.003343 | no |
| w15 | 3 | 1.057205 | 1.038348 | 1.074057 | 0.035708 | -0.003745 | no |
| w20 | 3 | 1.036877 | 1.029120 | 1.048379 | 0.019258 | -0.024073 | no |
| m1 | 3 | 0.976427 | 0.964123 | 0.993412 | 0.029289 | -0.084523 | yes |
| E3 full (different binding) | reference | 1.06 | — | — | — | — | not comparable |

### synthetic_heldout

| Arm | Seeds | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ctrl | 3 | 0.534846 | 0.519797 | 0.559004 | 0.039208 | +0.000000 | no |
| syn40 | 3 | 0.581974 | 0.557222 | 0.615439 | 0.058217 | +0.047128 | no |
| syn60 | 3 | 0.510886 | 0.495441 | 0.534054 | 0.038613 | -0.023960 | no |
| w15 | 3 | 0.423758 | 0.395640 | 0.446728 | 0.051089 | -0.111088 | yes |
| w20 | 3 | 0.399600 | 0.386135 | 0.411085 | 0.024950 | -0.135246 | yes |
| m1 | 3 | 0.546529 | 0.534054 | 0.558410 | 0.024356 | +0.011683 | no |
| E3 full (different binding) | reference | not provided | — | — | — | — | not comparable |

## Source strata

Cells are three-seed mean CER %. Counts are instrument lines per seed and are identical across configurations. Source script classes use `by_source_script_class`; the report’s post-readout `per_script_class` separately distinguishes Cyrillic/Latin mixed-script lines.

### v2_test by source script class

| Stratum | Lines/seed | ctrl | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- |
| cyrillic | 1742 | 1.870719 | 1.681550 | 1.549656 | 1.890887 |
| greek_latin_cs | 849 | 1.508791 | 1.376356 | 1.358662 | 1.530237 |
| greek_mono | 10213 | 0.726718 | 0.665394 | 0.629544 | 0.756035 |
| greek_poly | 28549 | 1.562430 | 1.455144 | 1.427886 | 1.608338 |
| latin | 685 | 1.546741 | 1.448088 | 1.340627 | 1.579332 |

### v2_test by wave

| Stratum | Lines/seed | ctrl | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- |
| cyrillic | 346 | 1.165988 | 0.939084 | 0.982146 | 1.157706 |
| mixed | 2151 | 2.851921 | 2.738689 | 2.655006 | 2.885196 |
| openarchives | 4642 | 0.314023 | 0.277594 | 0.255294 | 0.322001 |
| parliament | 11936 | 1.116575 | 1.035551 | 0.999431 | 1.164866 |
| round1 | 8083 | 1.514234 | 1.384696 | 1.365127 | 1.541185 |
| round2 | 3651 | 1.511866 | 1.451056 | 1.411651 | 1.575935 |
| vouli | 1739 | 4.271215 | 3.911145 | 3.892825 | 4.401454 |
| wikisource | 9490 | 1.249675 | 1.154882 | 1.111706 | 1.288768 |

### wikisource_human by language

**Not reported.** `by_language` is absent from all 18 Wikisource result objects. Greek/Russian language CER cannot be copied from this report. Source script class is not substituted for language.

## Mark metrics and available pain breakdowns

The report supplies `marks`, `marks_by_class`, `per_script_class`, `by_category`, dimensional `by` (including polarity), and dynamic `pain_points` for all four instruments. It lacks the E3 driver’s explicit `pain_strata` field in all 72 result objects. The fixed overlapping “rows containing each mark” CER strata are therefore unavailable. Mark occurrence errors below are not row-stratum CER. No field is reconstructed from predictions.

Mark error = `(FP+FN)/GT occurrences`; precision and recall retain the report’s alignment semantics. Error, precision, and recall are arithmetic three-seed means, shown as percentages. An undefined metric in any seed is NA. Support is GT occurrences per seed.

### v2_test — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | ctrl | 3.321322 | 98.956741 | 97.708801 | 147361 |
| acute | syn40 | 3.279022 | 98.943051 | 97.765352 | 147361 |
| acute | syn60 | 3.424018 | 99.034349 | 97.526935 | 147361 |
| acute | w15 | 3.121133 | 98.892213 | 97.976398 | 147361 |
| acute | w20 | 3.000115 | 98.938024 | 98.052402 | 147361 |
| acute | m1 | 3.426280 | 98.989321 | 97.569913 | 147361 |
| grave | ctrl | 4.260866 | 97.428624 | 98.334438 | 61881 |
| grave | syn40 | 4.204845 | 97.538169 | 98.275723 | 61881 |
| grave | syn60 | 4.385299 | 97.245315 | 98.402310 | 61881 |
| grave | w15 | 3.980759 | 97.663536 | 98.372683 | 61881 |
| grave | w20 | 3.898343 | 97.847581 | 98.263333 | 61881 |
| grave | m1 | 4.377757 | 97.353277 | 98.294576 | 61881 |
| circumflex | ctrl | 4.611772 | 97.480595 | 97.918957 | 40028 |
| circumflex | syn40 | 4.598448 | 97.396255 | 98.022218 | 40028 |
| circumflex | syn60 | 4.686719 | 97.423767 | 97.902302 | 40028 |
| circumflex | w15 | 4.353619 | 97.578380 | 98.080510 | 40028 |
| circumflex | w20 | 4.211219 | 97.618562 | 98.184604 | 40028 |
| circumflex | m1 | 4.690883 | 97.433755 | 97.887312 | 40028 |
| smooth_breathing | ctrl | 4.443430 | 97.675907 | 97.885733 | 54755 |
| smooth_breathing | syn40 | 4.410556 | 97.712645 | 97.880863 | 54755 |
| smooth_breathing | syn60 | 4.646151 | 97.545852 | 97.815725 | 54755 |
| smooth_breathing | w15 | 4.005722 | 97.888703 | 98.110370 | 54755 |
| smooth_breathing | w20 | 3.793870 | 98.093699 | 98.112806 | 54755 |
| smooth_breathing | m1 | 4.643716 | 97.610320 | 97.749368 | 54755 |
| rough_breathing | ctrl | 7.514730 | 96.340538 | 96.137703 | 25572 |
| rough_breathing | syn40 | 7.474321 | 96.406847 | 96.107722 | 25572 |
| rough_breathing | syn60 | 7.870588 | 96.368154 | 95.738829 | 25572 |
| rough_breathing | w15 | 6.649200 | 96.708976 | 96.639554 | 25572 |
| rough_breathing | w20 | 6.335054 | 96.780595 | 96.888524 | 25572 |
| rough_breathing | m1 | 7.909693 | 96.286569 | 95.784452 | 25572 |
| iota_subscript | ctrl | 14.263660 | 93.189927 | 92.495637 | 4966 |
| iota_subscript | syn40 | 13.921332 | 93.010351 | 93.072896 | 4966 |
| iota_subscript | syn60 | 14.451604 | 93.067419 | 92.435226 | 4966 |
| iota_subscript | w15 | 13.310511 | 93.197263 | 93.515908 | 4966 |
| iota_subscript | w20 | 13.048731 | 92.709029 | 94.375084 | 4966 |
| iota_subscript | m1 | 14.525440 | 93.078575 | 92.341254 | 4966 |
| dialytika | ctrl | 15.907274 | 93.944614 | 89.888090 | 834 |
| dialytika | syn40 | 15.227818 | 94.691636 | 89.808153 | 834 |
| dialytika | syn60 | 16.746603 | 93.749994 | 89.208633 | 834 |
| dialytika | w15 | 13.669065 | 94.191448 | 92.006395 | 834 |
| dialytika | w20 | 13.029576 | 94.900820 | 91.926459 | 834 |
| dialytika | m1 | 15.747402 | 94.063167 | 89.928058 | 834 |

### v2_test — available pain categories and polarity

| Available stratum | Lines/seed | ctrl | syn40 | syn60 | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| category: all_caps | 559 | 3.812636 | 3.642595 | 3.937510 | 3.531006 | 3.071364 | 4.073011 |
| category: dotted_leaders | 256 | 3.134992 | 3.093400 | 3.088201 | 2.708675 | 2.646287 | 3.179183 |
| category: font_style_unknown | 42038 | 1.367276 | 1.356431 | 1.409022 | 1.267984 | 1.234177 | 1.407469 |
| category: footnote_size_unknown | 42038 | 1.367276 | 1.356431 | 1.409022 | 1.267984 | 1.234177 | 1.407469 |
| category: hyphenation | 6373 | 0.983203 | 0.994289 | 1.027295 | 0.923742 | 0.866129 | 1.021752 |
| category: long_lines | 1326 | 1.460948 | 1.450393 | 1.541601 | 1.344571 | 1.306951 | 1.522115 |
| category: mixed_script | 1133 | 1.626373 | 1.619274 | 1.692346 | 1.471043 | 1.452670 | 1.641822 |
| category: numerics | 221 | 2.482698 | 2.530301 | 2.724377 | 2.193416 | 2.145813 | 2.526640 |
| category: punctuation_heavy | 126 | 3.202431 | 3.218015 | 3.140097 | 2.945302 | 2.797257 | 3.241390 |
| readout script: cyrillic | 1652 | 1.848378 | 1.845339 | 1.971256 | 1.676436 | 1.527506 | 1.876167 |
| readout script: cyrillic_latin_cs | 90 | 2.162807 | 1.975477 | 2.162807 | 1.748411 | 1.839237 | 2.083333 |
| polarity: dark_on_light | 42000 | 1.362910 | 1.352315 | 1.404556 | 1.264014 | 1.230982 | 1.403310 |
| polarity: light_on_dark | 38 | 10.830430 | 10.278746 | 11.091754 | 9.872242 | 8.159117 | 10.423926 |

Dynamic `pain_points`: number of seeds flagged by the report (0–3); its threshold is twice that seed’s Greek-monotonic CER. These are report flags, not new hypotheses.

| Reported pain point | ctrl | syn40 | syn60 | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- | --- |
| class: cyrillic | 3 | 3 | 3 | 3 | 3 | 3 |
| class: cyrillic_latin_cs | 3 | 3 | 3 | 3 | 3 | 3 |
| class: greek_latin_cs | 3 | 3 | 3 | 3 | 3 | 2 |
| class: greek_poly | 3 | 3 | 3 | 3 | 3 | 3 |
| class: latin | 3 | 3 | 3 | 3 | 2 | 3 |
| mark: acute | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: circumflex | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: dialytika | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: grave | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: iota_subscript | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: rough_breathing | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: smooth_breathing | 3 | 3 | 3 | 3 | 3 | 3 |

### wikisource_human — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | ctrl | 2.134647 | 98.714223 | 99.157088 | 3045 |
| acute | syn40 | 2.178435 | 98.671059 | 99.157088 | 3045 |
| acute | syn60 | 2.079912 | 98.757516 | 99.168035 | 3045 |
| acute | w15 | 2.222222 | 98.617514 | 99.168035 | 3045 |
| acute | w20 | 2.320744 | 98.332064 | 99.365079 | 3045 |
| acute | m1 | 2.200328 | 98.702733 | 99.102354 | 3045 |
| grave | ctrl | 3.021719 | 98.466892 | 98.512748 | 1412 |
| grave | syn40 | 3.045326 | 98.649890 | 98.300283 | 1412 |
| grave | syn60 | 2.927290 | 98.444896 | 98.630784 | 1412 |
| grave | w15 | 2.927290 | 98.674917 | 98.394712 | 1412 |
| grave | w20 | 3.045326 | 98.857851 | 98.087819 | 1412 |
| grave | m1 | 3.305005 | 98.347650 | 98.347498 | 1412 |
| circumflex | ctrl | 6.189411 | 98.987659 | 94.780015 | 894 |
| circumflex | syn40 | 5.555556 | 98.994439 | 95.413870 | 894 |
| circumflex | syn60 | 5.070843 | 99.112455 | 95.786726 | 894 |
| circumflex | w15 | 4.697987 | 99.267865 | 96.010440 | 894 |
| circumflex | w20 | 5.033557 | 99.227755 | 95.712155 | 894 |
| circumflex | m1 | 5.816555 | 99.067047 | 95.078300 | 894 |
| smooth_breathing | ctrl | 3.275649 | 98.412331 | 98.310672 | 1618 |
| smooth_breathing | syn40 | 3.502266 | 98.308244 | 98.187062 | 1618 |
| smooth_breathing | syn60 | 3.419860 | 98.391099 | 98.187062 | 1618 |
| smooth_breathing | w15 | 3.090235 | 98.756294 | 98.145859 | 1618 |
| smooth_breathing | w20 | 2.822415 | 98.921475 | 98.248867 | 1618 |
| smooth_breathing | m1 | 3.831891 | 98.223539 | 97.939843 | 1618 |
| rough_breathing | ctrl | 7.014768 | 97.219696 | 95.727848 | 632 |
| rough_breathing | syn40 | 7.542194 | 96.847558 | 95.569620 | 632 |
| rough_breathing | syn60 | 7.331224 | 97.360479 | 95.253165 | 632 |
| rough_breathing | w15 | 6.381857 | 97.484657 | 96.097046 | 632 |
| rough_breathing | w20 | 5.696203 | 97.251351 | 97.046414 | 632 |
| rough_breathing | m1 | 8.122363 | 96.182634 | 95.675105 | 632 |
| iota_subscript | ctrl | 13.812155 | 97.757673 | 88.213628 | 181 |
| iota_subscript | syn40 | 12.707182 | 97.780109 | 89.318600 | 181 |
| iota_subscript | syn60 | 12.707182 | 97.973446 | 89.134438 | 181 |
| iota_subscript | w15 | 14.364641 | 97.743630 | 87.661142 | 181 |
| iota_subscript | w20 | 11.602210 | 98.192467 | 90.055249 | 181 |
| iota_subscript | m1 | 15.101289 | 97.919580 | 86.740331 | 181 |
| dialytika | ctrl | 25.925926 | 92.129630 | 81.481481 | 9 |
| dialytika | syn40 | 37.037037 | 92.592593 | 70.370370 | 9 |
| dialytika | syn60 | 40.740741 | 81.018519 | 77.777778 | 9 |
| dialytika | w15 | 25.925926 | 85.925926 | 88.888889 | 9 |
| dialytika | w20 | 22.222222 | 89.772727 | 88.888889 | 9 |
| dialytika | m1 | 37.037037 | 81.759259 | 81.481481 | 9 |

### wikisource_human — available pain categories and polarity

| Available stratum | Lines/seed | ctrl | syn40 | syn60 | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| category: all_caps | 65 | 5.983494 | 6.327373 | 6.350298 | 5.593764 | 5.318661 | 6.533700 |
| category: dotted_leaders | 6 | 6.461087 | 6.901615 | 6.461087 | 6.461087 | 5.873715 | 6.167401 |
| category: font_style_unknown | 1392 | 3.314621 | 3.321074 | 3.326881 | 3.257840 | 3.248161 | 3.382372 |
| category: footnote_size_unknown | 1392 | 3.314621 | 3.321074 | 3.326881 | 3.257840 | 3.248161 | 3.382372 |
| category: hyphenation | 13 | 5.897946 | 6.163022 | 7.223327 | 5.500331 | 5.632869 | 7.422134 |
| category: long_lines | 1 | 27.011494 | 29.310345 | 31.034483 | 35.057471 | 28.735632 | 30.459770 |
| category: punctuation_heavy | 31 | 14.701258 | 15.015723 | 14.897799 | 14.937107 | 14.622642 | 14.976415 |
| readout script: cyrillic | 128 | 2.194052 | 2.356574 | 2.364700 | 2.055908 | 2.145295 | 2.332196 |
| readout script: cyrillic_latin_cs | 0 | NA | NA | NA | NA | NA | NA |
| polarity: dark_on_light | 1390 | 3.298208 | 3.307893 | 3.313059 | 3.247198 | 3.239449 | 3.367943 |
| polarity: light_on_dark | 2 | 26.851852 | 22.222222 | 23.148148 | 18.518519 | 15.740741 | 24.074074 |

Dynamic `pain_points`: number of seeds flagged by the report (0–3); its threshold is twice that seed’s Greek-monotonic CER. These are report flags, not new hypotheses.

| Reported pain point | ctrl | syn40 | syn60 | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- | --- |
| class: greek_latin_cs | 2 | 1 | 2 | 3 | 3 | 3 |
| mark: dialytika | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: iota_subscript | 3 | 2 | 2 | 3 | 3 | 3 |

### e1_real_test — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | ctrl | 0.020744 | 99.990571 | 99.988685 | 17676 |
| acute | syn40 | 0.024515 | 99.990570 | 99.984914 | 17676 |
| acute | syn60 | 0.026401 | 99.984914 | 99.988685 | 17676 |
| acute | w15 | 0.013201 | 99.988686 | 99.998114 | 17676 |
| acute | w20 | 0.020744 | 99.981146 | 99.998114 | 17676 |
| acute | m1 | 0.018858 | 99.994342 | 99.986799 | 17676 |
| grave | ctrl | NA | NA | NA | 0 |
| grave | syn40 | NA | NA | NA | 0 |
| grave | syn60 | NA | NA | NA | 0 |
| grave | w15 | NA | NA | NA | 0 |
| grave | w20 | NA | NA | NA | 0 |
| grave | m1 | NA | NA | NA | 0 |
| circumflex | ctrl | NA | NA | NA | 0 |
| circumflex | syn40 | NA | NA | NA | 0 |
| circumflex | syn60 | NA | NA | NA | 0 |
| circumflex | w15 | NA | NA | NA | 0 |
| circumflex | w20 | NA | NA | NA | 0 |
| circumflex | m1 | NA | NA | NA | 0 |
| smooth_breathing | ctrl | NA | NA | NA | 0 |
| smooth_breathing | syn40 | NA | NA | NA | 0 |
| smooth_breathing | syn60 | NA | NA | NA | 0 |
| smooth_breathing | w15 | NA | NA | NA | 0 |
| smooth_breathing | w20 | NA | NA | NA | 0 |
| smooth_breathing | m1 | NA | NA | NA | 0 |
| rough_breathing | ctrl | NA | NA | NA | 0 |
| rough_breathing | syn40 | NA | NA | NA | 0 |
| rough_breathing | syn60 | NA | NA | NA | 0 |
| rough_breathing | w15 | NA | NA | NA | 0 |
| rough_breathing | w20 | NA | NA | NA | 0 |
| rough_breathing | m1 | NA | NA | NA | 0 |
| iota_subscript | ctrl | NA | NA | NA | 0 |
| iota_subscript | syn40 | NA | NA | NA | 0 |
| iota_subscript | syn60 | NA | NA | NA | 0 |
| iota_subscript | w15 | NA | NA | NA | 0 |
| iota_subscript | w20 | NA | NA | NA | 0 |
| iota_subscript | m1 | NA | NA | NA | 0 |
| dialytika | ctrl | 3.508772 | 99.279258 | 97.192982 | 95 |
| dialytika | syn40 | 2.456140 | 100.000000 | 97.543860 | 95 |
| dialytika | syn60 | 2.456140 | 100.000000 | 97.543860 | 95 |
| dialytika | w15 | 2.105263 | 100.000000 | 97.894737 | 95 |
| dialytika | w20 | 0.701754 | 100.000000 | 99.298246 | 95 |
| dialytika | m1 | 1.403509 | 100.000000 | 98.596491 | 95 |

### e1_real_test — available pain categories and polarity

| Available stratum | Lines/seed | ctrl | syn40 | syn60 | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| category: all_caps | 60 | 8.867585 | 6.810465 | 8.887557 | 9.167166 | 7.769123 | 5.292590 |
| category: dotted_leaders | 29 | 10.138067 | 9.309665 | 9.993425 | 10.124918 | 8.284024 | 3.918475 |
| category: font_style_unknown | 3600 | 1.060950 | 1.056938 | 1.057607 | 1.057205 | 1.036877 | 0.976427 |
| category: footnote_size_unknown | 3600 | 1.060950 | 1.056938 | 1.057607 | 1.057205 | 1.036877 | 0.976427 |
| category: hyphenation | 147 | 0.366557 | 0.349895 | 0.349895 | 0.346563 | 0.299910 | 0.329901 |
| category: long_lines | 522 | 4.163894 | 4.100122 | 4.161814 | 4.157655 | 4.068236 | 3.913658 |
| category: mixed_script | 494 | 1.512228 | 1.424949 | 1.507635 | 1.514066 | 1.449755 | 1.393712 |
| category: numerics | 69 | 0.842967 | 0.855010 | 0.879094 | 0.818882 | 0.746628 | 0.758671 |
| category: punctuation_heavy | 82 | 6.057738 | 5.608140 | 6.010412 | 6.065625 | 4.929800 | 2.705474 |
| readout script: cyrillic | 0 | NA | NA | NA | NA | NA | NA |
| readout script: cyrillic_latin_cs | 0 | NA | NA | NA | NA | NA | NA |
| polarity: dark_on_light | 3600 | 1.060950 | 1.056938 | 1.057607 | 1.057205 | 1.036877 | 0.976427 |

Dynamic `pain_points`: number of seeds flagged by the report (0–3); its threshold is twice that seed’s Greek-monotonic CER. These are report flags, not new hypotheses.

| Reported pain point | ctrl | syn40 | syn60 | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- | --- |
| mark: dialytika | 2 | 3 | 3 | 2 | 1 | 1 |

### synthetic_heldout — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | ctrl | 0.807052 | 99.633427 | 99.559248 | 11193 |
| acute | syn40 | 0.869591 | 99.588825 | 99.541380 | 11193 |
| acute | syn60 | 0.774293 | 99.612869 | 99.612853 | 11193 |
| acute | w15 | 0.628369 | 99.681405 | 99.690283 | 11193 |
| acute | w20 | 0.595610 | 99.722981 | 99.681348 | 11193 |
| acute | m1 | 0.860657 | 99.609598 | 99.529468 | 11193 |
| grave | ctrl | 2.051282 | 99.100337 | 98.846154 | 520 |
| grave | syn40 | 3.076923 | 98.906182 | 98.012821 | 520 |
| grave | syn60 | 2.307692 | 98.915335 | 98.782051 | 520 |
| grave | w15 | 1.730769 | 99.422558 | 98.846154 | 520 |
| grave | w20 | 2.115385 | 99.038196 | 98.846154 | 520 |
| grave | m1 | 2.628205 | 98.720135 | 98.653846 | 520 |
| circumflex | ctrl | 2.617080 | 99.185693 | 98.189689 | 1694 |
| circumflex | syn40 | 2.597403 | 99.224450 | 98.170012 | 1694 |
| circumflex | syn60 | 2.066116 | 99.345826 | 98.583235 | 1694 |
| circumflex | w15 | 1.869343 | 99.445326 | 98.681621 | 1694 |
| circumflex | w20 | 1.790634 | 99.367324 | 98.839040 | 1694 |
| circumflex | m1 | 2.538371 | 99.224924 | 98.229044 | 1694 |
| smooth_breathing | ctrl | 2.436563 | 98.986546 | 98.572664 | 2312 |
| smooth_breathing | syn40 | 2.667243 | 98.772108 | 98.558247 | 2312 |
| smooth_breathing | syn60 | 2.465398 | 98.816721 | 98.716840 | 2312 |
| smooth_breathing | w15 | 1.859862 | 99.190704 | 98.947520 | 2312 |
| smooth_breathing | w20 | 1.931949 | 99.161681 | 98.904268 | 2312 |
| smooth_breathing | m1 | 2.609573 | 98.716345 | 98.673587 | 2312 |
| rough_breathing | ctrl | 3.880071 | 97.947246 | 98.177543 | 1134 |
| rough_breathing | syn40 | 4.115226 | 97.915740 | 97.971781 | 1134 |
| rough_breathing | syn60 | 3.380364 | 98.353400 | 98.265726 | 1134 |
| rough_breathing | w15 | 3.262787 | 98.298779 | 98.442093 | 1134 |
| rough_breathing | w20 | 3.380364 | 98.324225 | 98.295121 | 1134 |
| rough_breathing | m1 | 4.115226 | 98.283845 | 97.589653 | 1134 |
| iota_subscript | ctrl | 10.196078 | 94.220661 | 95.686275 | 85 |
| iota_subscript | syn40 | 12.156863 | 94.097759 | 93.725490 | 85 |
| iota_subscript | syn60 | 10.588235 | 93.517067 | 96.078431 | 85 |
| iota_subscript | w15 | 10.980392 | 93.825180 | 95.294118 | 85 |
| iota_subscript | w20 | 7.058824 | 96.114492 | 96.862745 | 85 |
| iota_subscript | m1 | 8.235294 | 96.806039 | 94.901961 | 85 |
| dialytika | ctrl | 6.598985 | 97.254110 | 96.108291 | 197 |
| dialytika | syn40 | 7.275804 | 97.079038 | 95.600677 | 197 |
| dialytika | syn60 | 4.906937 | 98.285256 | 96.785110 | 197 |
| dialytika | w15 | 4.399323 | 99.303690 | 96.277496 | 197 |
| dialytika | w20 | 3.045685 | 99.654577 | 97.292724 | 197 |
| dialytika | m1 | 6.768190 | 96.484314 | 96.785110 | 197 |

### synthetic_heldout — available pain categories and polarity

| Available stratum | Lines/seed | ctrl | syn40 | syn60 | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| category: all_caps | 52 | 1.299907 | 1.268957 | 1.702259 | 1.207057 | 1.052306 | 1.702259 |
| category: dotted_leaders | 17 | 0.811425 | 1.038624 | 1.038624 | 0.876339 | 0.649140 | 1.135995 |
| category: footnote_size_unknown | 2399 | 0.534846 | 0.581974 | 0.510886 | 0.423758 | 0.399600 | 0.546529 |
| category: hyphenation | 104 | 0.598407 | 0.591448 | 0.584490 | 0.455763 | 0.452284 | 0.598407 |
| category: long_lines | 897 | 0.485105 | 0.519315 | 0.440973 | 0.367763 | 0.345526 | 0.493315 |
| category: mixed_script | 265 | 0.930561 | 0.984821 | 0.918352 | 0.820684 | 0.756928 | 0.984821 |
| category: numerics | 19 | 0.000000 | 0.059630 | 0.000000 | 0.000000 | 0.000000 | 0.059630 |
| category: punctuation_heavy | 24 | 1.142041 | 1.784440 | 1.142041 | 1.070664 | 0.713776 | 1.284797 |
| readout script: cyrillic | 360 | 0.529101 | 0.591348 | 0.506869 | 0.412017 | 0.410535 | 0.545403 |
| readout script: cyrillic_latin_cs | 0 | NA | NA | NA | NA | NA | NA |
| polarity: dark_on_light | 2362 | 0.514429 | 0.555840 | 0.489903 | 0.407281 | 0.384967 | 0.525686 |
| polarity: light_on_dark | 37 | 1.878307 | 2.301587 | 1.891534 | 1.507937 | 1.362434 | 1.917989 |

Dynamic `pain_points`: number of seeds flagged by the report (0–3); its threshold is twice that seed’s Greek-monotonic CER. These are report flags, not new hypotheses.

| Reported pain point | ctrl | syn40 | syn60 | w15 | w20 | m1 |
| --- | --- | --- | --- | --- | --- | --- |
| class: greek_latin_cs | 3 | 3 | 3 | 3 | 3 | 3 |
| class: latin | 3 | 3 | 2 | 2 | 3 | 3 |
| mark: acute | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: circumflex | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: dialytika | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: grave | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: iota_subscript | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: rough_breathing | 3 | 3 | 3 | 3 | 3 | 3 |
| mark: smooth_breathing | 3 | 3 | 3 | 3 | 3 | 3 |

## Training and deployment cost

CSV wall time is each epoch’s training loop plus validation; summing its eight `wall_s` rows gives the recorded per-run total. It excludes initial dataset/model setup, checkpoint writes after the CSV timestamp, four-instrument readout and aggregate work; it is not full allocation elapsed time. The six-arm summary averages the three seed totals and the three per-seed epoch means.

CPU latency comes from [width_probe.md](../../out/e4prep/width_probe.md): ARM GH200 batch-node CPU, **one** intraop and one interop thread actually recorded, fp32, batch 1, 20 warmups, 1,000 common crops. It measures forward + masked attention + log_softmax, excluding PNG decode, normalization, collation/padding and CTC text decoding. Rounded p50 values are 129 / 169 / 220 ms/line (unrounded: 128.938 / 169.200 / 219.657). This is the requested deployment-cost proxy; it does not qualify the Docling deployment CPU.

| Arm | Width | Parameters | Mean wall s/epoch | Mean CSV wall s/run (8 epochs) | CPU p50 ms/line |
| --- | --- | --- | --- | --- | --- |
| ctrl | ×1.0 | 3.77 M | 519.02 | 4152.13 | 129 |
| syn40 | ×1.0 | 3.77 M | 507.67 | 4061.37 | 129 |
| syn60 | ×1.0 | 3.77 M | 533.58 | 4268.67 | 129 |
| w15 | ×1.5 | 8.39 M | 722.50 | 5779.97 | 169 |
| w20 | ×2.0 | 14.8 M | 816.57 | 6532.53 | 220 |
| m1 | ×1.0 | 3.77 M | 540.43 | 4323.40 | 129 |

Per-seed completion, checkpoint selection, and CSV wall time:

| Run | Source job | Epochs | Best epoch (val_cer) | Mean wall s/epoch | CSV wall s/run |
| --- | --- | --- | --- | --- | --- |
| ctrl_s0 | job01 | 8 | 8 | 517.27 | 4138.2 |
| ctrl_s1 | job01 | 8 | 8 | 519.26 | 4154.1 |
| ctrl_s2 | job01 | 8 | 8 | 520.51 | 4164.1 |
| m1_s0 | job08 | 8 | 8 | 547.54 | 4380.3 |
| m1_s1 | job08 | 8 | 8 | 546.90 | 4375.2 |
| m1_s2 | job08 | 8 | 8 | 526.84 | 4214.7 |
| syn40_s0 | job01 | 8 | 7 | 512.89 | 4103.1 |
| syn40_s1 | job02 | 8 | 8 | 505.24 | 4041.9 |
| syn40_s2 | job02 | 8 | 7 | 504.89 | 4039.1 |
| syn60_s0 | job02 | 8 | 8 | 514.89 | 4119.1 |
| syn60_s1 | job02 | 8 | 8 | 514.26 | 4114.1 |
| syn60_s2 | job03 | 8 | 7 | 571.60 | 4572.8 |
| w15_s0 | job03 | 8 | 8 | 723.21 | 5785.7 |
| w15_s1 | job03 | 8 | 8 | 721.39 | 5771.1 |
| w15_s2 | job03 | 8 | 8 | 722.89 | 5783.1 |
| w20_s0 | job04 | 8 | 7 | 815.31 | 6522.5 |
| w20_s1 | job04 | 8 | 5 | 818.49 | 6547.9 |
| w20_s2 | job04 | 8 | 5 | 815.90 | 6527.2 |

## H1–H10 hypothesis map

“Tested” names the contrast actually present in wave 1a on v2-asis; it does not assert that the repaired-release campaign or confidence-bound decision rule was completed. Verdicts apply only the stated numerical rules.

| Hypothesis | Preregistered contrast | Tested in wave 1a | Verdict / scope |
| --- | --- | --- | --- |
| H1 | Label geometry explains ≥0.2 pp scanned CER (S1) | no | No geometry intervention; geometry-clean secondary readout skipped. |
| H2 | Larger output vocabulary alone has no measurable cost (V A/B) | no | Codec v1 unchanged. |
| H3 | Recovered Cyrillic rows help Cyrillic without hurting Greek (V B/C) | no | No recovered-row/codec contrast. |
| H4 | 10% matched born-digital replay lowers e1_real_test ≥0.1 pp without scanned regression (M1) | yes | M1 lowers e1_real_test by 0.084523 pp, beyond seed range, below the preregistered ≥0.1 pp target. Its v2_test mean rises 0.040194 pp, within the larger seed range (0.040408 pp). The joint H4 signature is not met. |
| H5 | Corrected labels raise human-referenced mark recall (S2) | no | No corrected training-label contrast. |
| H6 | Synthetic 40/50/60 is flat within δ (M2) | yes | Neither syn40 nor syn60 differs from ctrl beyond the larger seed range on any of the four instruments. This does not establish equivalence/flatness within δ. |
| H7 | Width ×1.5 beats ×1 at 208k rows by more than δ (C1) | yes | Width ×1.5 lowers v2_test by 0.099292 pp and ×2 by 0.133099 pp; both exceed the larger seed range and the 0.05 pp scanned threshold. This tests width on the unchanged pool, not the width × data-size cross. CPU deployment qualification remains absent. |
| H8 | 6% Cyrillic draws help human Russian lines (M3) | no | No Cyrillic-draw reweighting contrast. |
| H9 | Caps-without-marks/display faces lower all-caps CER (G) | no | No such generator arm. |
| H10 | 5% light-on-dark lowers the 38-line polarity slice without other cost (G) | no | No polarity-training contrast; slice metrics alone are not a test. |

### Grave — deferred

Reason verbatim from the launch HANDOFF:

Full build **3678545** reached paired qualification, which FAILED: 86,969
ordered identity comparisons did not match, and three compared targeted rows
changed font. That ordered mismatch count is not a count of distinct bad source
rows. Factory appearance-audit promotion does not establish the wave's paired
identity/style contract. **No grave mix, training binding or training job was
published.** The candidate, exception ledger, samples and failed qualification
remain on Clariden; see grave/DO_NOT_TRAIN.md and grave/qualification.json.
No gate was relaxed to fill the nominal 21-arm table.

## Failed allocations and custody

| Job ID | Role / diagnosis | Slurm state | Exit | Elapsed |
| --- | --- | --- | --- | --- |
| 3678463 | job04: m1_s0 failed startup (missing bench import, two attempts); w20_s0/s1/s2 trained eight epochs and completed all four readouts before the final wave check raised. | FAILED | 1:0 | 02:02:24 |
| 3678467 | job05: original m1_s1/s2 startup failed before model setup or optimizer updates. | FAILED | 1:0 | 00:03:48 |
| 3678509 | job06: first recovery startup failed on train/train.py versus train-package import collision; no optimizer updates. | FAILED | 1:0 | 00:03:44 |
| 3678521 | Initial strict grave build failed before rendering on inherited supply deficits. | FAILED | 1:0 | 00:00:18 |
| 3678545 | Full grave build failed paired qualification; candidate not promoted. | FAILED | 1:0 | 00:01:34 |

The successful aggregate takes w20_s0/s1/s2 from **job04 / 3678463** and m1_s0/s1/s2 from **job08 / 3678554**. [recovery_readout.json](../../out/e4/wave1a/aggregate_retry2/recovery_readout.json) retains job04/05/06 as failed allocations and identifies the complete 18-arm base set. `aggregate_status.json` binds each source `E4_COMPLETE.json`/node receipt; those receipts name the completed runs, and the aggregate per-run result objects exactly equal their source fragments. Failed M1 directories retain only `allocation_history.json` and `run_binding.json`; their scientific parameters match the successful job08 replacements.

**Custody paragraph unavailable:** `aggregate_retry2/REPORT.md` contains no `Custody:` paragraph. The requested verbatim quotation cannot be supplied; this is a failed verification check. The source-fragment chain described above is a readback observation, not a replacement quotation.

**Aggregate hash-receipt gap:** `aggregate_retry2/receipt.json` contains job ID, node, partition, account, source head, start/end and exit code, but no report/markdown hashes. The aggregate’s source-fragment hashes validate; Mac/Clariden report hashes match. Neither fact establishes equality to an absent aggregate report-hash field. Check (d) fails. No receipt was amended.

Source diagnosis: the explicit `--wave1a` dispatch in `bench/e3_driver.py` uses `bench.e4_wave1a.report/aggregate`, bypassing the ordinary E3 `write_report/aggregate_jobs` path. The wave adapter does not emit `by_language`, fixed `pain_strata`, a custody paragraph, or an aggregate report-hash completion receipt. `scripts/clariden/common.sh` emits only scheduler execution fields in `receipt.json`. These omissions are recorded without changing the source or regenerating the readout.

All failed verification checks:

- `d.aggregate_receipt_report_hashes`: Aggregate receipt.json records scheduler execution only; it contains no report/markdown hashes. Mac/Clariden equality is a separate transfer check.
- `custody.verbatim_paragraph_available`: No Custody paragraph exists in aggregate_retry2/REPORT.md; none can be quoted verbatim.
- `results.requested_wikisource_language_breakdown`: report.json has no by_language field for any Wikisource run; the requested language table cannot be copied. Source script class is not a language substitute.
- `scope.protected_tracked_files_and_head_unchanged`: Protected tracked file bytes are unchanged; local HEAD advanced externally from 93adc7b to d670254 via unrelated sourcing-document commits.

Local HEAD advanced externally from `93adc7b` to `d670254` through two unrelated sourcing-document commits during this readback. The protected tracked source bytes match intake. This task performed no Git writes and preserved those external changes; [observation](../../out/e4/wave1a_readback/external_head_change.json).

No Slurm job was submitted or resubmitted. Clariden artifacts remain in place. This task changed no plans or recommendations.
