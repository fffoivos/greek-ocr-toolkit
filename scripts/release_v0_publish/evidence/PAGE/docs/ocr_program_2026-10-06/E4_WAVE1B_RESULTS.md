# E4 wave 1b results

All **12/12** submitted runs completed eight epochs (four configurations × seeds 0/1/2). Preflight 3679494, training jobs 3679498/3679500/3679506/3679511 and aggregate 3679513 are COMPLETED, exit 0:0. Aggregate state is `DONE`; report `complete=true`. Grave remains deferred.

Readback verification: **PASS** (193 passed checks, 0 failed checks). Mac/Clariden SHA256 mismatches: **0** across 119 specifically requested artifacts, using fresh post-copy Clariden hashes. The broader synchronized inventory contains 526 files / 5,253,461,442 bytes, including pre-existing identical files.

Sources: [report.json](../../out/e4/wave1b/aggregate/report.json), [REPORT.md](../../out/e4/wave1b/aggregate/REPORT.md), [E4_AGGREGATE_COMPLETE.json](../../out/e4/wave1b/aggregate/E4_AGGREGATE_COMPLETE.json), [pinned_controls.json](../../out/e4/wave1b/aggregate/pinned_controls.json), [verification.json](../../out/e4/wave1b_readback/verification.json), [post-copy SHA256](../../out/e4/wave1b_readback/postcopy_sha256.json), and [wave-1a results](E4_WAVE1A_RESULTS.md). The wave-1b aggregate has no RESULT_DIGEST.md; its report.json is the numerical source.

## Binding, populations and decision rule

v_a/v_b/v_c use frozen **v2-codec** `ef64d8b70f5bc946201a0d082c8ca0b711f0abefe1c1b12b46c82473f840175d`; w30 and the pinned wave-1a ctrl/w15/w20 use **v2-asis** `af1ff90200e8ad897e246192da9a420a15fec2793fbc987649dbf2ff77d81621`. v_a is the concurrent control for both v_b and v_c in the totals tables; the H3 recovery contrast is separately B versus C. w30 uses the completed wave-1a ctrl. No cross-release control contrast is computed.

Every run binding hashes its immutable node binding, which binds both releases and the codec-v1 artifact inventory. This is the transitive af1ff902/v1 binding; it does not say every model uses v1. v_a and w30 use model codec v1 (247 atoms + blank); v_b/v_c use model codec v2 (254 atoms + blank). Model and reference codec hashes are checked separately in each prediction receipt.

Metric verbatim from report.json: **strict literal NFD codepoint CER; prediction vocabulary and reference vocabulary separately hash-bound**. Values below are arithmetic three-seed means of the report's instrument-level CER. CER mean/min/max are percentages; Δ and seed ranges are percentage points (pp). Δ = candidate mean − its named control mean. **Beyond seed range = `abs(Δ) > max(range_arm, range_ctrl)`**, computed before rounding; yes can mean improvement or regression. This descriptive rule does not establish equivalence, a paired book-bootstrap confidence bound, or the equally weighted book-level human-reference decision.

Common intersection retains the exact original references and prediction populations. Full coverage appends only native v2-recovered held-out rows. Full and common figures are never contrasted. The v1 control is scored against the same literal v2 full references as B/C; the references are not rewritten.

Geometry-clean secondary column: **skipped** — `Absent at intake; skipped secondary column`. No corrected-label/F1/S1 score is claimed.

| Instrument | View | Rows/seed | Reference NFD codepoints/seed |
| --- | --- | --- | --- |
| v2_test | common intersection | 42,038 | 2,489,622 |
| v2_test | full coverage | 43,883 | 2,586,133 |
| wikisource_human | common intersection | 1,392 | 51,660 |
| wikisource_human | full coverage | 1,527 | 56,719 |
| e1_real_test | common intersection | 3,600 | 249,242 |
| e1_real_test | full coverage | 3,600 | 249,242 |
| synthetic_heldout | common intersection | 2,399 | 168,335 |
| synthetic_heldout | full coverage | 2,399 | 168,335 |

## Instrument totals — original/common-intersection populations

Each table contains the four wave-1b configurations and three pinned wave-1a reference rows. Release/control columns define the valid contrast; equal denominators do not make different releases interchangeable. All rows contain three seeds.

### v2_test

| Arm | Release | Control | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | v2-codec | v_a | 1.368213 | 1.360206 | 1.374506 | 0.014299 | +0.000000 | no |
| v_b | v2-codec | v_a | 1.369913 | 1.368642 | 1.372297 | 0.003655 | +0.001700 | no |
| v_c | v2-codec | v_a | 1.370409 | 1.363661 | 1.376836 | 0.013175 | +0.002196 | no |
| w30 | v2-asis | wave1a ctrl | 1.194345 | 1.167607 | 1.219703 | 0.052096 | -0.172931 | yes |
| wave1a ctrl (pinned) | v2-asis | wave1a ctrl | 1.367276 | 1.355708 | 1.376514 | 0.020806 | +0.000000 | no |
| wave1a w15 (pinned) | v2-asis | wave1a ctrl | 1.267984 | 1.250712 | 1.288388 | 0.037676 | -0.099292 | yes |
| wave1a w20 (pinned) | v2-asis | wave1a ctrl | 1.234177 | 1.216771 | 1.251355 | 0.034584 | -0.133099 | yes |

### wikisource_human

| Arm | Release | Control | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | v2-codec | v_a | 3.325590 | 3.313976 | 3.333333 | 0.019357 | +0.000000 | no |
| v_b | v2-codec | v_a | 3.318493 | 3.290747 | 3.360434 | 0.069686 | -0.007098 | no |
| v_c | v2-codec | v_a | 3.317847 | 3.252033 | 3.358498 | 0.106465 | -0.007743 | no |
| w30 | v2-asis | wave1a ctrl | 3.167505 | 3.149439 | 3.201703 | 0.052265 | -0.147116 | yes |
| wave1a ctrl (pinned) | v2-asis | wave1a ctrl | 3.314621 | 3.300426 | 3.327526 | 0.027100 | +0.000000 | no |
| wave1a w15 (pinned) | v2-asis | wave1a ctrl | 3.257840 | 3.213318 | 3.292683 | 0.079365 | -0.056782 | no |
| wave1a w20 (pinned) | v2-asis | wave1a ctrl | 3.248161 | 3.224932 | 3.284940 | 0.060008 | -0.066460 | yes |

### e1_real_test

| Arm | Release | Control | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | v2-codec | v_a | 1.058543 | 1.037546 | 1.069643 | 0.032097 | +0.000000 | no |
| v_b | v2-codec | v_a | 1.053461 | 1.038348 | 1.072050 | 0.033702 | -0.005082 | no |
| v_c | v2-codec | v_a | 1.061485 | 1.051990 | 1.075260 | 0.023271 | +0.002942 | no |
| w30 | v2-asis | wave1a ctrl | 1.075528 | 1.021096 | 1.117388 | 0.096292 | +0.014578 | no |
| wave1a ctrl (pinned) | v2-asis | wave1a ctrl | 1.060950 | 1.041959 | 1.075260 | 0.033301 | +0.000000 | no |
| wave1a w15 (pinned) | v2-asis | wave1a ctrl | 1.057205 | 1.038348 | 1.074057 | 0.035708 | -0.003745 | no |
| wave1a w20 (pinned) | v2-asis | wave1a ctrl | 1.036877 | 1.029120 | 1.048379 | 0.019258 | -0.024073 | no |

### synthetic_heldout

| Arm | Release | Control | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | v2-codec | v_a | 0.534846 | 0.521579 | 0.554846 | 0.033267 | +0.000000 | no |
| v_b | v2-codec | v_a | 0.543559 | 0.532272 | 0.560192 | 0.027921 | +0.008713 | no |
| v_c | v2-codec | v_a | 0.546925 | 0.525143 | 0.563163 | 0.038019 | +0.012079 | no |
| w30 | v2-asis | wave1a ctrl | 0.325937 | 0.317819 | 0.337422 | 0.019604 | -0.208909 | yes |
| wave1a ctrl (pinned) | v2-asis | wave1a ctrl | 0.534846 | 0.519797 | 0.559004 | 0.039208 | +0.000000 | no |
| wave1a w15 (pinned) | v2-asis | wave1a ctrl | 0.423758 | 0.395640 | 0.446728 | 0.051089 | -0.111088 | yes |
| wave1a w20 (pinned) | v2-asis | wave1a ctrl | 0.399600 | 0.386135 | 0.411085 | 0.024950 | -0.135246 | yes |

## Codec full-coverage totals — separately scored populations

Only A/B/C have full-coverage readouts. w30 and pinned wave-1a widths have no full-coverage score. The e1_real_test and synthetic_heldout full views are identical to their common views and are included explicitly below. Each full table uses its own full-coverage v_a control.

### v2_test_full_coverage

| Arm | Seeds | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | 3 | 1.476477 | 1.466707 | 1.483721 | 0.017014 | +0.000000 | no |
| v_b | 3 | 1.478230 | 1.475639 | 1.481710 | 0.006071 | +0.001753 | no |
| v_c | 3 | 1.373853 | 1.365127 | 1.379395 | 0.014268 | -0.102624 | yes |

### wikisource_human_full_coverage

| Arm | Seeds | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | 3 | 3.521454 | 3.501472 | 3.536734 | 0.035262 | +0.000000 | no |
| v_b | 3 | 3.509700 | 3.476789 | 3.542023 | 0.065234 | -0.011754 | no |
| v_c | 3 | 3.168250 | 3.111832 | 3.205275 | 0.093443 | -0.353203 | yes |

### e1_real_test_full_coverage

| Arm | Seeds | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | 3 | 1.058543 | 1.037546 | 1.069643 | 0.032097 | +0.000000 | no |
| v_b | 3 | 1.053461 | 1.038348 | 1.072050 | 0.033702 | -0.005082 | no |
| v_c | 3 | 1.061485 | 1.051990 | 1.075260 | 0.023271 | +0.002942 | no |

### synthetic_heldout_full_coverage

| Arm | Seeds | Mean CER % | Min % | Max % | Range pp | Δ vs ctrl (mean), pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | 3 | 0.534846 | 0.521579 | 0.554846 | 0.033267 | +0.000000 | no |
| v_b | 3 | 0.543559 | 0.532272 | 0.560192 | 0.027921 | +0.008713 | no |
| v_c | 3 | 0.546925 | 0.525143 | 0.563163 | 0.038019 | +0.012079 | no |

## Script, source wave and language strata

### v2_test — common intersection by source script class

Source field: `by_source_script_class`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 | ctrl (pinned) | w20 (pinned) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cyrillic | 1742 | 82642 | 1.869106 | 1.901777 | 1.864669 | 1.373797 | 1.870719 | 1.549656 |
| greek_latin_cs | 849 | 62169 | 1.533991 | 1.562408 | 1.538280 | 1.231589 | 1.508791 | 1.358662 |
| greek_mono | 10213 | 607159 | 0.723424 | 0.727816 | 0.725894 | 0.620431 | 0.726718 | 0.629544 |
| greek_poly | 28549 | 1699809 | 1.563803 | 1.562293 | 1.565470 | 1.387097 | 1.562430 | 1.427886 |
| latin | 685 | 37843 | 1.561716 | 1.552907 | 1.594306 | 1.291300 | 1.546741 | 1.340627 |

### v2_test — common intersection by source wave

Source field: `by_wave`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 | ctrl (pinned) | w20 (pinned) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cyrillic | 346 | 20126 | 1.151082 | 1.146113 | 1.088145 | 0.847991 | 1.165988 | 0.982146 |
| mixed | 2151 | 134237 | 2.837519 | 2.838760 | 2.878491 | 2.617013 | 2.851921 | 2.655006 |
| openarchives | 4642 | 346790 | 0.310563 | 0.317579 | 0.317868 | 0.232706 | 0.314023 | 0.255294 |
| parliament | 11936 | 679220 | 1.125654 | 1.127764 | 1.125654 | 0.995357 | 1.116575 | 0.999431 |
| round1 | 8083 | 492262 | 1.508479 | 1.504687 | 1.513015 | 1.297886 | 1.514234 | 1.365127 |
| round2 | 3651 | 235162 | 1.499959 | 1.515693 | 1.507188 | 1.405839 | 1.511866 | 1.411651 |
| vouli | 1739 | 100073 | 4.272881 | 4.238906 | 4.230245 | 3.801891 | 4.271215 | 3.892825 |
| wikisource | 9490 | 481752 | 1.260192 | 1.264067 | 1.258185 | 1.034488 | 1.249675 | 1.111706 |

The `cyrillic` source-script row (1,742 common rows) is the H3 script question. The `cyrillic` source-wave row (346 common rows) is a different subset; it is not substituted for script class.

### v2_test — full coverage by source script class

Source field: `by_source_script_class`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| cyrillic | 3510 | 174607 | 3.171694 | 3.186203 | 1.632619 |
| greek_latin_cs | 854 | 62513 | 1.537813 | 1.568207 | 1.533014 |
| greek_mono | 10242 | 608773 | 0.730267 | 0.734866 | 0.730650 |
| greek_poly | 28587 | 1702161 | 1.564854 | 1.563483 | 1.566518 |
| latin | 690 | 38079 | 1.581799 | 1.572170 | 1.596681 |

### v2_test — full coverage by source wave

Source field: `by_wave`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| cyrillic | 644 | 39849 | 2.203318 | 2.197462 | 0.996261 |
| mixed | 2162 | 134942 | 2.832822 | 2.833316 | 2.865676 |
| openarchives | 4666 | 348056 | 0.323607 | 0.331077 | 0.327534 |
| parliament | 11936 | 679220 | 1.125605 | 1.127666 | 1.125703 |
| round1 | 8106 | 493906 | 1.510881 | 1.507439 | 1.515201 |
| round2 | 3653 | 235316 | 1.499969 | 1.516117 | 1.507193 |
| vouli | 1741 | 100194 | 4.268719 | 4.234785 | 4.228463 |
| wikisource | 10975 | 554650 | 1.702395 | 1.706001 | 1.300400 |

### wikisource_human — common intersection by language

Source field: `by_language`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| el | 1264 | 47558 | 3.408470 | 3.407068 | 3.409171 | 3.255674 |
| ru | 128 | 4102 | 2.364700 | 2.291565 | 2.259061 | 2.145295 |

### wikisource_human — full coverage by language

Source field: `by_language`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| el | 1264 | 47558 | 3.407769 | 3.406367 | 3.409171 |
| ru | 263 | 9161 | 4.111633 | 4.046138 | 1.917549 |

Pinned wave-1a ctrl/w20 have no `by_language` field. Their Greek/Russian means cannot be copied; source script class is not used as a substitute. Wave 1b does provide `by_language` for its v2_test and Wikisource views.

## H2, H3 and width continuation contrasts

| View | B/C stratum | B mean % | C mean % | Δ C−B, pp | Larger seed range, pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- |
| v2_test | overall B→C | 1.369913 | 1.370409 | +0.000495 | 0.013175 | no |
| v2_test | by_source_script_class:cyrillic | 1.901777 | 1.864669 | -0.037108 | 0.070182 | no |
| v2_test | by_source_script_class:greek_mono | 0.727816 | 0.725894 | -0.001922 | 0.016635 | no |
| v2_test | by_source_script_class:greek_poly | 1.562293 | 1.565470 | +0.003177 | 0.018296 | no |
| v2_test | by_source_script_class:greek_latin_cs | 1.562408 | 1.538280 | -0.024128 | 0.054690 | no |
| v2_test | by_language:el | 1.129070 | 1.127390 | -0.001680 | 0.007202 | no |
| wikisource_human | overall B→C | 3.318493 | 3.317847 | -0.000645 | 0.106465 | no |
| wikisource_human | by_source_script_class:cyrillic | 2.291565 | 2.259061 | -0.032504 | 0.609459 | no |
| wikisource_human | by_source_script_class:greek_mono | 5.609990 | 5.244957 | -0.365034 | 1.037464 | no |
| wikisource_human | by_source_script_class:greek_poly | 3.304349 | 3.316030 | +0.011681 | 0.089800 | no |
| wikisource_human | by_source_script_class:greek_latin_cs | 11.428571 | 12.698413 | +1.269841 | 4.761905 | no |
| wikisource_human | by_language:el | 3.407068 | 3.409171 | +0.002103 | 0.130367 | no |
| v2_test_full_coverage | overall B→C | 1.478230 | 1.373853 | -0.104377 | 0.014268 | yes |
| v2_test_full_coverage | by_source_script_class:cyrillic | 3.186203 | 1.632619 | -1.553584 | 0.153488 | yes |
| v2_test_full_coverage | by_source_script_class:greek_mono | 0.734866 | 0.730650 | -0.004216 | 0.015934 | no |
| v2_test_full_coverage | by_source_script_class:greek_poly | 1.563483 | 1.566518 | +0.003035 | 0.017860 | no |
| v2_test_full_coverage | by_source_script_class:greek_latin_cs | 1.568207 | 1.533014 | -0.035193 | 0.051189 | no |
| v2_test_full_coverage | by_language:el | 1.131912 | 1.129674 | -0.002238 | 0.007193 | no |
| wikisource_human_full_coverage | overall B→C | 3.509700 | 3.168250 | -0.341449 | 0.093443 | yes |
| wikisource_human_full_coverage | by_source_script_class:cyrillic | 4.046138 | 1.917549 | -2.128589 | 0.240148 | yes |
| wikisource_human_full_coverage | by_source_script_class:greek_mono | 5.609990 | 5.225744 | -0.384246 | 1.037464 | no |
| wikisource_human_full_coverage | by_source_script_class:greek_poly | 3.303619 | 3.316760 | +0.013141 | 0.087610 | no |
| wikisource_human_full_coverage | by_source_script_class:greek_latin_cs | 11.428571 | 12.698413 | +1.269841 | 4.761905 | no |
| wikisource_human_full_coverage | by_language:el | 3.406367 | 3.409171 | +0.002804 | 0.126162 | no |

| Original instrument | Pinned comparator | Comparator mean % | w30 mean % | Δ w30−comparator, pp | Larger seed range, pp | beyond seed range |
| --- | --- | --- | --- | --- | --- | --- |
| v2_test | wave1a ctrl | 1.367276 | 1.194345 | -0.172931 | 0.052096 | yes |
| v2_test | wave1a w15 | 1.267984 | 1.194345 | -0.073639 | 0.052096 | yes |
| v2_test | wave1a w20 | 1.234177 | 1.194345 | -0.039832 | 0.052096 | no |
| wikisource_human | wave1a ctrl | 3.314621 | 3.167505 | -0.147116 | 0.052265 | yes |
| wikisource_human | wave1a w15 | 3.257840 | 3.167505 | -0.090334 | 0.079365 | yes |
| wikisource_human | wave1a w20 | 3.248161 | 3.167505 | -0.080656 | 0.060008 | yes |
| e1_real_test | wave1a ctrl | 1.060950 | 1.075528 | +0.014578 | 0.096292 | no |
| e1_real_test | wave1a w15 | 1.057205 | 1.075528 | +0.018322 | 0.096292 | no |
| e1_real_test | wave1a w20 | 1.036877 | 1.075528 | +0.038651 | 0.096292 | no |
| synthetic_heldout | wave1a ctrl | 0.534846 | 0.325937 | -0.208909 | 0.039208 | yes |
| synthetic_heldout | wave1a w15 | 0.423758 | 0.325937 | -0.097821 | 0.051089 | yes |
| synthetic_heldout | wave1a w20 | 0.399600 | 0.325937 | -0.073663 | 0.024950 | yes |

## Mark metrics and pain strata

The aggregate contains `marks`, `marks_by_class`, `per_script_class`, `by_category`, dimensional `by` (including polarity), and dynamic `pain_points` on all four original instruments and on the codec full views. Fixed overlapping `pain_strata` for the seven marks are present only for v2_test and wikisource_human (common and full); they are absent for e1_real_test/synthetic_heldout. Explicit `pain_strata.Cyrillic` and `pain_strata.mixed_script` are absent; script-class/category tables carry those separate populations. Pinned wave-1a results lack fixed `pain_strata` throughout. No missing field is reconstructed from predictions.

Mark error = (FP+FN)/GT occurrences, with the report's alignment semantics. Error, precision and recall are arithmetic three-seed means, in %. NA means an undefined metric in at least one seed. GT support is occurrences per seed. Pain-stratum CER measures complete rows containing the named mark; it is not the mark occurrence error. `font_style_unknown` and `footnote_size_unknown` do not measure bold/condensed or small-footnote performance.

### v2_test — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | v_a | 3.355478 | 98.933708 | 97.697491 | 147361 |
| acute | v_b | 3.329918 | 98.944974 | 97.711968 | 147361 |
| acute | v_c | 3.321322 | 98.967501 | 97.697944 | 147361 |
| acute | w30 | 2.889050 | 99.134869 | 97.965993 | 147361 |
| grave | v_a | 4.279720 | 97.425620 | 98.318278 | 61881 |
| grave | v_b | 4.275949 | 97.411542 | 98.337131 | 61881 |
| grave | v_c | 4.228008 | 97.447763 | 98.347904 | 61881 |
| grave | w30 | 3.748593 | 97.690380 | 98.582225 | 61881 |
| circumflex | v_a | 4.627594 | 97.473904 | 97.909796 | 40028 |
| circumflex | v_b | 4.569301 | 97.486407 | 97.956430 | 40028 |
| circumflex | v_c | 4.637587 | 97.476064 | 97.897305 | 40028 |
| circumflex | w30 | 4.139602 | 97.583645 | 98.294527 | 40028 |
| smooth_breathing | v_a | 4.507351 | 97.619922 | 97.879037 | 54755 |
| smooth_breathing | v_b | 4.485435 | 97.650539 | 97.869297 | 54755 |
| smooth_breathing | v_c | 4.551791 | 97.706061 | 97.743281 | 54755 |
| smooth_breathing | w30 | 3.661766 | 98.130320 | 98.209600 | 54755 |
| rough_breathing | v_a | 7.543407 | 96.411709 | 96.030815 | 25572 |
| rough_breathing | v_b | 7.522551 | 96.383228 | 96.082955 | 25572 |
| rough_breathing | v_c | 7.659419 | 96.260936 | 96.072527 | 25572 |
| rough_breathing | w30 | 5.987017 | 96.963522 | 97.052766 | 25572 |
| iota_subscript | v_a | 14.330783 | 93.103607 | 92.522486 | 4966 |
| iota_subscript | v_b | 14.156263 | 93.314545 | 92.468788 | 4966 |
| iota_subscript | v_c | 14.142838 | 93.286501 | 92.515774 | 4966 |
| iota_subscript | w30 | 12.491610 | 93.002528 | 94.630152 | 4966 |
| dialytika | v_a | 15.667466 | 93.853314 | 90.247802 | 834 |
| dialytika | v_b | 15.107914 | 94.325858 | 90.327738 | 834 |
| dialytika | v_c | 16.386890 | 93.659533 | 89.688249 | 834 |
| dialytika | w30 | 13.069544 | 94.820136 | 91.966427 | 834 |

### v2_test — fixed overlapping mark-containing row strata

Source field: `pain_strata`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| acute | 38829 | 2349017 | 1.337978 | 1.338886 | 1.341143 | 1.181260 |
| circumflex | 21264 | 1309934 | 1.528321 | 1.527125 | 1.532927 | 1.351620 |
| dialytika | 812 | 51770 | 1.887193 | 1.841478 | 1.892344 | 1.647029 |
| grave | 25190 | 1545873 | 1.521298 | 1.523584 | 1.529449 | 1.352397 |
| iota_subscript | 3778 | 241920 | 1.695740 | 1.688299 | 1.686921 | 1.481619 |
| rough_breathing | 16614 | 1043522 | 1.516403 | 1.515988 | 1.518927 | 1.325415 |
| smooth_breathing | 25000 | 1531128 | 1.536645 | 1.538561 | 1.540629 | 1.361328 |

### v2_test — available pain categories

Source field: `by_category`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| all_caps | 559 | 12546 | 3.910941 | 3.905627 | 3.804665 | 2.656889 |
| dotted_leaders | 256 | 12823 | 3.064805 | 3.070004 | 3.103798 | 2.469521 |
| font_style_unknown | 42038 | 2489622 | 1.368213 | 1.369913 | 1.370409 | 1.194345 |
| footnote_size_unknown | 42038 | 2489622 | 1.368213 | 1.369913 | 1.370409 | 1.194345 |
| hyphenation | 6373 | 396900 | 0.998404 | 0.994373 | 0.989082 | 0.837659 |
| long_lines | 1326 | 123162 | 1.465279 | 1.480435 | 1.488554 | 1.242808 |
| mixed_script | 1133 | 79830 | 1.636394 | 1.651008 | 1.633054 | 1.311119 |
| numerics | 221 | 9103 | 2.552272 | 2.479036 | 2.504669 | 1.995679 |
| punctuation_heavy | 126 | 4278 | 3.334892 | 3.358267 | 3.031011 | 2.516752 |

### v2_test — polarity

| Polarity | Rows/seed | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| dark_on_light | 42000 | 2488474 | 1.363567 | 1.365509 | 1.366112 | 1.191266 |
| light_on_dark | 38 | 1148 | 11.440186 | 10.917538 | 10.685250 | 7.868757 |

### wikisource_human — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | v_a | 2.364532 | 98.530862 | 99.113300 | 3045 |
| acute | v_b | 2.134647 | 98.692820 | 99.178982 | 3045 |
| acute | v_c | 2.266010 | 98.638198 | 99.102354 | 3045 |
| acute | w30 | 1.981390 | 98.716612 | 99.310345 | 3045 |
| grave | v_a | 3.163362 | 98.487536 | 98.347498 | 1412 |
| grave | v_b | 2.903683 | 98.605918 | 98.489141 | 1412 |
| grave | v_c | 3.068933 | 98.557349 | 98.371105 | 1412 |
| grave | w30 | 2.998111 | 98.928522 | 98.064212 | 1412 |
| circumflex | v_a | 5.965697 | 98.951854 | 95.041014 | 894 |
| circumflex | v_b | 5.891126 | 99.104813 | 94.966443 | 894 |
| circumflex | v_c | 5.779269 | 99.106082 | 95.078300 | 894 |
| circumflex | w30 | 3.653990 | 99.275998 | 97.054437 | 894 |
| smooth_breathing | v_a | 3.481665 | 98.409471 | 98.104656 | 1618 |
| smooth_breathing | v_b | 3.522868 | 98.307710 | 98.166461 | 1618 |
| smooth_breathing | v_c | 3.543469 | 98.448940 | 98.001648 | 1618 |
| smooth_breathing | w30 | 2.698805 | 98.922802 | 98.372476 | 1618 |
| rough_breathing | v_a | 7.647679 | 96.751858 | 95.569620 | 632 |
| rough_breathing | v_b | 7.911392 | 96.744605 | 95.305907 | 632 |
| rough_breathing | v_c | 7.805907 | 96.739540 | 95.411392 | 632 |
| rough_breathing | w30 | 5.327004 | 97.868604 | 96.782700 | 632 |
| iota_subscript | v_a | 13.627993 | 97.955651 | 88.213628 | 181 |
| iota_subscript | v_b | 14.548803 | 97.544631 | 87.661142 | 181 |
| iota_subscript | v_c | 12.523020 | 97.594597 | 89.686924 | 181 |
| iota_subscript | w30 | 11.418048 | 98.195985 | 90.239411 | 181 |
| dialytika | v_a | 29.629630 | 88.425926 | 81.481481 | 9 |
| dialytika | v_b | 40.740741 | 83.664021 | 74.074074 | 9 |
| dialytika | v_c | 48.148148 | 73.105413 | 85.185185 | 9 |
| dialytika | w30 | 25.925926 | 88.888889 | 88.888889 | 9 |

### wikisource_human — fixed overlapping mark-containing row strata

Source field: `pain_strata`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| acute | 1169 | 45155 | 3.332964 | 3.324844 | 3.344775 | 3.214114 |
| circumflex | 665 | 26555 | 3.327685 | 3.328940 | 3.360321 | 3.175799 |
| dialytika | 9 | 334 | 3.393214 | 3.393214 | 3.393214 | 3.193613 |
| grave | 848 | 33036 | 3.175324 | 3.148081 | 3.153126 | 3.016911 |
| iota_subscript | 166 | 7041 | 3.323392 | 3.332860 | 3.238176 | 3.086683 |
| rough_breathing | 499 | 20774 | 3.239626 | 3.231604 | 3.220372 | 3.096820 |
| smooth_breathing | 904 | 36825 | 3.202535 | 3.194388 | 3.206155 | 3.073093 |

### wikisource_human — available pain categories

Source field: `by_category`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| all_caps | 65 | 1454 | 6.121045 | 6.281522 | 5.777166 | 4.493352 |
| dotted_leaders | 6 | 227 | 6.754772 | 6.314244 | 6.461087 | 6.461087 |
| font_style_unknown | 1392 | 51660 | 3.325590 | 3.318493 | 3.317847 | 3.167505 |
| footnote_size_unknown | 1392 | 51660 | 3.325590 | 3.318493 | 3.317847 | 3.167505 |
| hyphenation | 13 | 503 | 5.897946 | 6.096753 | 6.361829 | 4.970179 |
| long_lines | 1 | 58 | 27.586207 | 31.609195 | 30.459770 | 24.137931 |
| punctuation_heavy | 31 | 848 | 14.976415 | 14.701258 | 14.897799 | 14.740566 |

### wikisource_human — polarity

| Polarity | Rows/seed | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| dark_on_light | 1390 | 51624 | 3.305956 | 3.300790 | 3.302727 | 3.155509 |
| light_on_dark | 2 | 36 | 31.481481 | 28.703704 | 25.000000 | 20.370370 |

### e1_real_test — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | v_a | 0.032059 | 99.981144 | 99.986799 | 17676 |
| acute | v_b | 0.028287 | 99.986800 | 99.984914 | 17676 |
| acute | v_c | 0.030173 | 99.984914 | 99.984914 | 17676 |
| acute | w30 | 0.009429 | 99.992457 | 99.998114 | 17676 |
| grave | v_a | NA | NA | NA | 0 |
| grave | v_b | NA | NA | NA | 0 |
| grave | v_c | NA | NA | NA | 0 |
| grave | w30 | NA | NA | NA | 0 |
| circumflex | v_a | NA | NA | NA | 0 |
| circumflex | v_b | NA | NA | NA | 0 |
| circumflex | v_c | NA | NA | NA | 0 |
| circumflex | w30 | NA | NA | NA | 0 |
| smooth_breathing | v_a | NA | NA | NA | 0 |
| smooth_breathing | v_b | NA | NA | NA | 0 |
| smooth_breathing | v_c | NA | NA | NA | 0 |
| smooth_breathing | w30 | NA | NA | NA | 0 |
| rough_breathing | v_a | NA | NA | NA | 0 |
| rough_breathing | v_b | NA | NA | NA | 0 |
| rough_breathing | v_c | NA | NA | NA | 0 |
| rough_breathing | w30 | NA | NA | NA | 0 |
| iota_subscript | v_a | NA | NA | NA | 0 |
| iota_subscript | v_b | NA | NA | NA | 0 |
| iota_subscript | v_c | NA | NA | NA | 0 |
| iota_subscript | w30 | NA | NA | NA | 0 |
| dialytika | v_a | 2.807018 | 99.641577 | 97.543860 | 95 |
| dialytika | v_b | 2.807018 | 99.645390 | 97.543860 | 95 |
| dialytika | v_c | 2.105263 | 100.000000 | 97.894737 | 95 |
| dialytika | w30 | 0.701754 | 100.000000 | 99.298246 | 95 |

Fixed overlapping mark-containing `pain_strata`: **not reported** for this instrument.

### e1_real_test — available pain categories

Source field: `by_category`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| all_caps | 60 | 1669 | 9.207110 | 9.386858 | 10.724985 | 8.707809 |
| dotted_leaders | 29 | 2535 | 10.046022 | 9.335963 | 9.940828 | 12.189349 |
| font_style_unknown | 3600 | 249242 | 1.058543 | 1.053461 | 1.061485 | 1.075528 |
| footnote_size_unknown | 3600 | 249242 | 1.058543 | 1.053461 | 1.061485 | 1.075528 |
| hyphenation | 147 | 10003 | 0.356560 | 0.349895 | 0.369889 | 0.333233 |
| long_lines | 522 | 48088 | 4.141019 | 4.147258 | 4.168746 | 4.196473 |
| mixed_script | 494 | 36282 | 1.552652 | 1.566433 | 1.576539 | 1.480991 |
| numerics | 69 | 2768 | 0.734586 | 0.770713 | 0.782755 | 0.794798 |
| punctuation_heavy | 82 | 4226 | 5.978861 | 5.552926 | 5.947310 | 7.296103 |

### e1_real_test — polarity

| Polarity | Rows/seed | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| dark_on_light | 3600 | 249242 | 1.058543 | 1.053461 | 1.061485 | 1.075528 |

### synthetic_heldout — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | v_a | 0.804074 | 99.624600 | 99.571161 | 11193 |
| acute | v_b | 0.810030 | 99.603854 | 99.586051 | 11193 |
| acute | v_c | 0.839811 | 99.597818 | 99.562226 | 11193 |
| acute | w30 | 0.407993 | 99.859873 | 99.731975 | 11193 |
| grave | v_a | 2.435897 | 99.033250 | 98.525641 | 520 |
| grave | v_b | 2.179487 | 99.099827 | 98.717949 | 520 |
| grave | v_c | 3.012821 | 98.774588 | 98.205128 | 520 |
| grave | w30 | 1.666667 | 99.104638 | 99.230769 | 520 |
| circumflex | v_a | 2.380952 | 99.187189 | 98.425817 | 1694 |
| circumflex | v_b | 2.459662 | 99.246328 | 98.288076 | 1694 |
| circumflex | v_c | 2.361275 | 99.363326 | 98.268398 | 1694 |
| circumflex | w30 | 1.475797 | 99.447099 | 99.075167 | 1694 |
| smooth_breathing | v_a | 2.465398 | 98.958456 | 98.572664 | 2312 |
| smooth_breathing | v_b | 2.436563 | 99.000723 | 98.558247 | 2312 |
| smooth_breathing | v_c | 2.523068 | 98.900736 | 98.572664 | 2312 |
| smooth_breathing | w30 | 1.398501 | 99.436457 | 99.163783 | 2312 |
| rough_breathing | v_a | 3.968254 | 97.973490 | 98.059965 | 1134 |
| rough_breathing | v_b | 4.115226 | 97.858080 | 98.030570 | 1134 |
| rough_breathing | v_c | 4.115226 | 97.998812 | 97.883598 | 1134 |
| rough_breathing | w30 | 2.322163 | 98.710081 | 98.971193 | 1134 |
| iota_subscript | v_a | 12.549020 | 93.726189 | 93.725490 | 85 |
| iota_subscript | v_b | 9.019608 | 94.965276 | 96.078431 | 85 |
| iota_subscript | v_c | 9.803922 | 94.577679 | 95.686275 | 85 |
| iota_subscript | w30 | 8.627451 | 94.304226 | 97.254902 | 85 |
| dialytika | v_a | 5.922166 | 97.780106 | 96.277496 | 197 |
| dialytika | v_b | 6.937394 | 96.925586 | 96.108291 | 197 |
| dialytika | v_c | 6.429780 | 97.433990 | 96.108291 | 197 |
| dialytika | w30 | 3.214890 | 98.971716 | 97.800338 | 197 |

Fixed overlapping mark-containing `pain_strata`: **not reported** for this instrument.

### synthetic_heldout — available pain categories

Source field: `by_category`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| all_caps | 52 | 1077 | 1.114206 | 1.207057 | 1.083256 | 0.835655 |
| dotted_leaders | 17 | 1027 | 0.941253 | 1.006167 | 1.135995 | 0.778968 |
| footnote_size_unknown | 2399 | 168335 | 0.534846 | 0.543559 | 0.546925 | 0.325937 |
| hyphenation | 104 | 9581 | 0.626239 | 0.601886 | 0.598407 | 0.382702 |
| long_lines | 897 | 97436 | 0.483736 | 0.495026 | 0.481342 | 0.280868 |
| mixed_script | 265 | 24573 | 0.941413 | 0.954978 | 0.944126 | 0.653834 |
| numerics | 19 | 559 | 0.000000 | 0.059630 | 0.059630 | 0.000000 |
| punctuation_heavy | 24 | 467 | 1.498929 | 1.498929 | 1.570307 | 0.785153 |

### synthetic_heldout — polarity

| Polarity | Rows/seed | Reference atoms | v_a | v_b | v_c | w30 |
| --- | --- | --- | --- | --- | --- | --- |
| dark_on_light | 2362 | 165815 | 0.514630 | 0.520259 | 0.522671 | 0.315211 |
| light_on_dark | 37 | 2520 | 1.865079 | 2.076720 | 2.142857 | 1.031746 |

### v2_test_full_coverage — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | v_a | 3.353495 | 98.933890 | 97.699312 | 147637 |
| acute | v_b | 3.328660 | 98.945350 | 97.712859 | 147637 |
| acute | v_c | 3.319403 | 98.968516 | 97.698860 | 147637 |
| grave | v_a | 4.274594 | 97.428476 | 98.320503 | 61963 |
| grave | v_b | 4.270828 | 97.413408 | 98.340407 | 61963 |
| grave | v_c | 4.221874 | 97.452133 | 98.349553 | 61963 |
| circumflex | v_a | 4.624941 | 97.475143 | 97.911210 | 40087 |
| circumflex | v_b | 4.568397 | 97.486801 | 97.956944 | 40087 |
| circumflex | v_c | 4.630761 | 97.478975 | 97.901231 | 40087 |
| smooth_breathing | v_a | 4.503831 | 97.622116 | 97.880336 | 54820 |
| smooth_breathing | v_b | 4.482549 | 97.650951 | 97.871823 | 54820 |
| smooth_breathing | v_c | 4.549435 | 97.705232 | 97.746565 | 54820 |
| rough_breathing | v_a | 7.538846 | 96.417335 | 96.029515 | 25614 |
| rough_breathing | v_b | 7.519325 | 96.388848 | 96.080269 | 25614 |
| rough_breathing | v_c | 7.657271 | 96.267899 | 96.067255 | 25614 |
| iota_subscript | v_a | 14.313489 | 93.111982 | 92.531510 | 4972 |
| iota_subscript | v_b | 14.152588 | 93.321773 | 92.464468 | 4972 |
| iota_subscript | v_c | 14.132475 | 93.294220 | 92.518101 | 4972 |
| dialytika | v_a | 16.348449 | 93.199392 | 90.254574 | 838 |
| dialytika | v_b | 15.751790 | 93.687947 | 90.334129 | 838 |
| dialytika | v_c | 16.507558 | 93.568535 | 89.657916 | 838 |

### v2_test_full_coverage — fixed overlapping mark-containing row strata

Source field: `pain_strata`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| acute | 38900 | 2353293 | 1.340448 | 1.341553 | 1.342813 |
| circumflex | 21296 | 1312046 | 1.529697 | 1.528478 | 1.534143 |
| dialytika | 816 | 51985 | 1.903754 | 1.858228 | 1.894136 |
| grave | 25225 | 1548213 | 1.522443 | 1.524704 | 1.530431 |
| iota_subscript | 3782 | 242190 | 1.697015 | 1.689307 | 1.688344 |
| rough_breathing | 16640 | 1045255 | 1.517620 | 1.517206 | 1.520044 |
| smooth_breathing | 25031 | 1533229 | 1.537583 | 1.539670 | 1.541583 |

### v2_test_full_coverage — available pain categories

Source field: `by_category`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| all_caps | 559 | 12546 | 3.910941 | 3.900314 | 3.807322 |
| dotted_leaders | 285 | 13991 | 3.249708 | 3.275915 | 3.056727 |
| font_style_unknown | 43883 | 2586133 | 1.476477 | 1.478230 | 1.373853 |
| footnote_size_unknown | 43883 | 2586133 | 1.476477 | 1.478230 | 1.373853 |
| hyphenation | 6965 | 429697 | 1.241573 | 1.237849 | 1.022581 |
| long_lines | 1332 | 123602 | 1.491346 | 1.507797 | 1.510224 |
| mixed_script | 1225 | 86203 | 1.814709 | 1.831723 | 1.649981 |
| numerics | 221 | 9103 | 2.552272 | 2.471713 | 2.501007 |
| punctuation_heavy | 129 | 4402 | 3.369680 | 3.422687 | 2.991065 |

### v2_test_full_coverage — polarity

| Polarity | Rows/seed | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| dark_on_light | 43845 | 2584985 | 1.472052 | 1.474038 | 1.369705 |
| light_on_dark | 38 | 1148 | 11.440186 | 10.917538 | 10.714286 |

### wikisource_human_full_coverage — marks

| Mark | Arm | Error % | Precision % | Recall % | GT support/seed |
| --- | --- | --- | --- | --- | --- |
| acute | v_a | 2.364532 | 98.530862 | 99.113300 | 3045 |
| acute | v_b | 2.134647 | 98.692820 | 99.178982 | 3045 |
| acute | v_c | 2.266010 | 98.638198 | 99.102354 | 3045 |
| grave | v_a | 3.163362 | 98.487536 | 98.347498 | 1412 |
| grave | v_b | 2.903683 | 98.605918 | 98.489141 | 1412 |
| grave | v_c | 3.068933 | 98.557349 | 98.371105 | 1412 |
| circumflex | v_a | 5.928412 | 98.952263 | 95.078300 | 894 |
| circumflex | v_b | 5.891126 | 99.104813 | 94.966443 | 894 |
| circumflex | v_c | 5.816555 | 99.105634 | 95.041014 | 894 |
| smooth_breathing | v_a | 3.481665 | 98.409471 | 98.104656 | 1618 |
| smooth_breathing | v_b | 3.502266 | 98.308053 | 98.187062 | 1618 |
| smooth_breathing | v_c | 3.543469 | 98.448940 | 98.001648 | 1618 |
| rough_breathing | v_a | 7.647679 | 96.751858 | 95.569620 | 632 |
| rough_breathing | v_b | 7.858650 | 96.796728 | 95.305907 | 632 |
| rough_breathing | v_c | 7.805907 | 96.739540 | 95.411392 | 632 |
| iota_subscript | v_a | 13.812155 | 97.950664 | 88.029466 | 181 |
| iota_subscript | v_b | 14.548803 | 97.544631 | 87.661142 | 181 |
| iota_subscript | v_c | 12.523020 | 97.594597 | 89.686924 | 181 |
| dialytika | v_a | 25.925926 | 92.592593 | 81.481481 | 9 |
| dialytika | v_b | 40.740741 | 83.664021 | 74.074074 | 9 |
| dialytika | v_c | 48.148148 | 73.105413 | 85.185185 | 9 |

### wikisource_human_full_coverage — fixed overlapping mark-containing row strata

Source field: `pain_strata`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| acute | 1169 | 45155 | 3.332226 | 3.324106 | 3.344775 |
| circumflex | 665 | 26555 | 3.326429 | 3.327685 | 3.361577 |
| dialytika | 9 | 334 | 3.393214 | 3.393214 | 3.393214 |
| grave | 848 | 33036 | 3.175324 | 3.147072 | 3.151108 |
| iota_subscript | 166 | 7041 | 3.328126 | 3.328126 | 3.242911 |
| rough_breathing | 499 | 20774 | 3.241231 | 3.231604 | 3.218767 |
| smooth_breathing | 904 | 36825 | 3.202535 | 3.193483 | 3.207060 |

### wikisource_human_full_coverage — available pain categories

Source field: `by_category`. Cells are arithmetic three-seed mean CER %; counts are per seed.

| Stratum | Rows | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| all_caps | 65 | 1454 | 6.121045 | 6.281522 | 5.777166 |
| dotted_leaders | 6 | 227 | 6.754772 | 6.314244 | 6.461087 |
| font_style_unknown | 1527 | 56719 | 3.521454 | 3.509700 | 3.168250 |
| footnote_size_unknown | 1527 | 56719 | 3.521454 | 3.509700 | 3.168250 |
| hyphenation | 19 | 721 | 5.871475 | 5.963939 | 5.409154 |
| long_lines | 1 | 58 | 27.586207 | 31.609195 | 30.459770 |
| punctuation_heavy | 31 | 848 | 14.976415 | 14.701258 | 14.897799 |

### wikisource_human_full_coverage — polarity

| Polarity | Rows/seed | Reference atoms | v_a | v_b | v_c |
| --- | --- | --- | --- | --- | --- |
| dark_on_light | 1525 | 56683 | 3.503696 | 3.493699 | 3.154385 |
| light_on_dark | 2 | 36 | 31.481481 | 28.703704 | 25.000000 |

## Training and deployment cost

Parameters: ×1/v1 **3,771,192 (3.77 M)**; ×1/v2 **3,772,991 (3.77 M)**; ×3/v1 **33,155,000 (33.2 M)**. Pinned ×1.5 **8,386,904 (8.39 M)** and ×2 **14,822,776 (14.8 M)**. Counts come from checkpoint metadata/launch and the width probe; no model is instantiated for this readback.

Training wall time is each train_log.csv `wall_s`: epoch training plus validation, ending before checkpoint writes. Total/arm below is the sum of eight epoch values. It excludes setup before the epoch loop, checkpoint writes after the timer, instrument readout and aggregation; allocation elapsed time is listed separately. All timings are observations of these runs, not a controlled width speed comparison.

Deployment-cost column: [width_probe.md](../../out/e4prep/width_probe.md), ARM GH200 batch-node CPU, **one intraop and one interop thread actually recorded**, fp32, batch 1, 20 warmups and 1,000 identical seeded crops. p50 = **129 / 169 / 220 ms/line** for ×1/×1.5/×2 (unrounded 128.938 / 169.200 / 219.657). Boundary: forward + masked attention + log_softmax, excluding PNG decode, normalization, collation/padding and CTC text decoding. ×1/v2 reuses the width-×1 proxy; codec v2 itself was not CPU-probed. **×3 has no CPU probe; no extrapolation.** The Docling target CPU remains unqualified. The eight-thread wording in the unchanged planning paragraph conflicts with the probe's actual one-thread records; this digest uses the recorded configuration.

| Arm | Width/model codec | Parameters | Epoch mean s | Epoch min–max s | Eight-epoch total mean s/seed | Total min–max s/seed | CPU p50 deployment-cost proxy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v_a | 1/v1 | 3,771,192 | 520.8 | 497.6–633.8 | 4166.7 | 4160.0–4176.7 | 129 ms (×1 proxy) |
| v_b | 1/v2 | 3,772,991 | 581.4 | 484.0–1063.4 | 4651.3 | 4158.0–4905.0 | 129 ms (×1 proxy) |
| v_c | 1/v2 | 3,772,991 | 573.2 | 474.0–1064.7 | 4586.0 | 3972.5–4905.4 | 129 ms (×1 proxy) |
| w30 | 3/v1 | 33,155,000 | 1194.8 | 1159.9–1340.6 | 9558.3 | 9534.0–9592.4 | no CPU probe |
| wave1a ctrl (pinned) | 1/v1 | 3,771,192 | 519.0 | 490.8–638.3 | 4152.1 | 4138.2–4164.1 | 129 ms |
| wave1a w15 (pinned) | 1.5/v1 | 8,386,904 | 722.5 | 649.4–1096.6 | 5780.0 | 5771.1–5785.7 | 169 ms |
| wave1a w20 (pinned) | 2/v1 | 14,822,776 | 816.6 | 791.5–928.4 | 6532.5 | 6522.5–6547.9 | 220 ms |

| Run | Best epoch | Epoch 1 s | Epoch 2 s | Epoch 3 s | Epoch 4 s | Epoch 5 s | Epoch 6 s | Epoch 7 s | Epoch 8 s | Total/arm s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v_a_s0 | 8 | 627.2 | 516.0 | 503.6 | 503.0 | 498.6 | 511.9 | 501.6 | 501.4 | 4163.3 |
| v_a_s1 | 8 | 628.1 | 522.2 | 506.3 | 501.4 | 497.6 | 504.2 | 499.5 | 500.7 | 4160.0 |
| v_a_s2 | 8 | 633.8 | 519.4 | 509.1 | 500.0 | 498.7 | 507.2 | 504.5 | 504.0 | 4176.7 |
| v_b_s0 | 8 | 627.8 | 515.9 | 508.1 | 507.4 | 498.1 | 504.4 | 499.3 | 497.0 | 4158.0 |
| v_b_s1 | 8 | 1063.4 | 645.4 | 515.1 | 695.7 | 499.3 | 506.9 | 492.4 | 486.8 | 4905.0 |
| v_b_s2 | 8 | 1063.4 | 645.2 | 515.0 | 696.1 | 500.0 | 493.7 | 493.6 | 484.0 | 4891.0 |
| v_c_s0 | 8 | 1054.6 | 636.9 | 514.7 | 705.4 | 496.2 | 502.3 | 486.0 | 483.9 | 4880.0 |
| v_c_s1 | 8 | 1064.7 | 654.9 | 532.0 | 680.1 | 493.6 | 497.7 | 492.4 | 490.0 | 4905.4 |
| v_c_s2 | 8 | 606.2 | 478.8 | 484.0 | 475.5 | 474.0 | 482.7 | 486.1 | 485.2 | 3972.5 |
| w30_s0 | 5 | 1335.5 | 1187.1 | 1167.2 | 1177.6 | 1174.9 | 1174.1 | 1169.2 | 1162.9 | 9548.5 |
| w30_s1 | 6 | 1332.8 | 1184.0 | 1168.4 | 1168.5 | 1172.1 | 1177.0 | 1171.3 | 1159.9 | 9534.0 |
| w30_s2 | 5 | 1340.6 | 1188.7 | 1173.6 | 1181.1 | 1178.2 | 1180.5 | 1180.2 | 1169.5 | 9592.4 |

## H1–H10 hypothesis map

“Tested in wave 1b” identifies the intervention/continuation present here, on the authorized as-is releases. It does not mark the preregistered repaired-release campaign complete. Prior wave-1a fraction/M1/width verdicts are carried explicitly as prior results; no new fraction or M1 run is implied.

| Hypothesis | Preregistered contrast | Tested in wave 1b | Verdict / scope |
| --- | --- | --- | --- |
| H1 | Label geometry explains ≥0.2 pp scanned CER (S1) | no | No geometry/label repair; geometry-clean column skipped. |
| H2 | Larger output vocabulary alone costs nothing measurable (V A/B) | yes | A/B common-intersection differences do not exceed the larger seed range on any original instrument. This does not prove no measurable cost: the confidence-bound/equivalence test is absent. |
| H3 | Recovered Cyrillic rows help Cyrillic without hurting Greek (V B/C) | yes | On common v2_test, Cyrillic is B 1.901777% → C 1.864669% (−0.037108 pp), within the larger 0.070182 pp seed range. Full-coverage Cyrillic is 3.186203% → 1.632619% (−1.553584 pp), beyond the larger 0.153488 pp range; full Wikisource Russian is 4.046138% → 1.917549%, also beyond range. The greek_mono/greek_poly classes and el-language means have no increase exceeding 0.05 pp scanned / 0.10 pp human (common greek_poly +0.003177 / +0.011681 pp). The two-row, 105-codepoint human greek_latin_cs slice rises 11.428571% → 12.698413% (+1.269841 pp): above the 0.10 pp tolerance but within its 4.761905 pp seed range; it is not hidden by the aggregate Greek mean. Full-coverage Cyrillic recovery is beyond seed range; the common Cyrillic contrast is unresolved by that rule, and a broad no-harm H3 verdict is not established. No repaired-label or confidence-bound result is claimed. |
| H4 | 10% matched born-digital replay lowers e1_real_test ≥0.1 pp without scanned regression (M1) | no | Prior wave 1a M1: e1_real_test −0.084523 pp, beyond seed range, below the ≥0.1 pp target; v2_test +0.040194 pp within the 0.040408 pp range. The joint H4 signature was not met. No new M1 training in wave 1b. |
| H5 | Corrected labels raise human-referenced mark recall (S2) | no | No corrected training-label contrast; mark metrics alone are not an S2 test. |
| H6 | Synthetic 40/50/60 is flat within δ (M2) | no | Prior wave 1a synthetic 40%/60%: neither differs from ctrl beyond the larger seed range on any original instrument. Flatness/equivalence within δ was not established. Fractions are unchanged in wave 1b. |
| H7 | Width ×1.5 beats ×1 at 208k rows by more than δ (C1) | yes | This continuation tests ×3 against pinned widths on v2-asis. w30 v2_test is 1.194345% versus pinned ctrl 1.367276% (−0.172931 pp, beyond range) and w20 1.234177% (−0.039832 pp, within the larger 0.052096 pp range). Pinned wave-1a ×1.5/×2 lowered v2_test by 0.099292/0.133099 pp, both beyond seed range and the 0.05 pp scanned threshold. No width × data-size cross or ×3 CPU qualification is present. |
| H8 | Cyrillic real share 6% helps human Russian lines (M3) | no | C recovers rows within fixed original class/source quotas; it does not test a 6% Cyrillic quota. |
| H9 | Caps-without-marks/display faces lower all-caps CER (G) | no | No such generator intervention. |
| H10 | 5% light-on-dark lowers the 38-line polarity slice without other cost (G) | no | No polarity-training intervention; polarity readouts alone are not that contrast. |

### Grave — deferred again

Verbatim deferral from [grave/DEFERRED.md](../../out/e4/wave1b/grave/DEFERRED.md):

The wave-1a candidate remains unchanged and is not submitted for training.
The diagnosis ran only after all twelve main arms were submitted, within the
optional one-hour effort limit. Its hash checks confirm both original and
candidate shard inventories and factory receipts match the retained failed
wave-1a qualification.

The 86,969 ordered identity mismatches cannot be treated as purely an ordering
artefact. Joining by `(split, line_id, reuse_index)` finds **2 missing and 2
added identity occurrences**, plus **7 font changes among unambiguous matched
rows**. Examples include GFSGalatea-Regular → GFSDidot_Classic and FiraSans-Regular
→ FiraSans-Italic on targeted grave rows. Merely sorting the output cannot repair
these immutable-style and population differences.

There are also **3,314 duplicate identity occurrences in each build** under that
join key. These are present in the baseline as well; they are a limitation of a
simple identity-only reorder, not evidence of a newly introduced duplicate bug.
The seven reported font witnesses come only from identities unique in both
builds. `identity_diagnosis.json` preserves counts by split, matched-column
changes, source hashes and example texts.

This metadata diagnosis does not establish unaffected-pixel parity, and it does
not replace or relax the original physical paired gate. A style/pairing repair
and a fresh complete qualification would still be needed. No source policy,
candidate shard, recipe, exclusion or gate was edited to force a pass; no grave
release/mix/training binding was published in wave 1b.

## Allocations and custody

All wave-1b job states below are fresh sacct readbacks in UTC; each final Slurm log and the training worker/run logs were read. **Failed wave-1b allocations: none.** No resubmission or Slurm submission was made.

| Role | Job ID | State | Exit | Elapsed | Affected arms |
| --- | --- | --- | --- | --- | --- |
| preflight | 3679494 | COMPLETED | 0:0 | 00:01:34 | diagnostic update only |
| job01 | 3679498 | COMPLETED | 0:0 | 01:28:37 | v_a_s0, v_a_s1, v_a_s2, v_b_s0 |
| job02 | 3679500 | COMPLETED | 0:0 | 01:40:54 | v_b_s1, v_b_s2, v_c_s0, v_c_s1 |
| job03 | 3679506 | COMPLETED | 0:0 | 01:21:19 | v_c_s2 |
| job04 | 3679511 | COMPLETED | 0:0 | 02:53:32 | w30_s0, w30_s1, w30_s2 |
| aggregate | 3679513 | COMPLETED | 0:0 | 00:15:47 | v_a_s0, v_a_s1, v_a_s2, v_b_s0, v_b_s1, v_b_s2, v_c_s0, v_c_s1, v_c_s2, w30_s0, w30_s1, w30_s2 |

Historical failed allocations retained with the pinned wave-1a provenance (copied from its results digest; not wave-1b failures or a new sacct audit):

| Wave-1a job ID | Recorded failure / affected arms |
| --- | --- |
| 3678463 | job04 M1 s0 startup failed; w20 s0/s1/s2 completed eight epochs and four readouts in this FAILED allocation; these are the pinned w20 runs. |
| 3678467 | job05 M1 s1/s2 startup failed before optimizer updates. |
| 3678509 | job06 first M1 recovery startup failed on train-package import collision; no optimizer updates. |
| 3678521 | Initial grave build failed on inherited supply deficits before rendering; no grave arm trained. |
| 3678545 | Full grave build failed paired qualification; no grave arm trained. |

Custody paragraph copied verbatim from the wave-1b aggregate REPORT.md:

Custody: every prediction file, crop, node binding, completed run and source fragment is hash-checked; the aggregate completion receipt hashes this report and Markdown. Common-intersection views reuse identical base predictions; no literal reference is rewritten.

Readback scope: retained artifacts were compared against Clariden SHA256; excluded crops, shards and last.pt were left on Clariden. The quoted remote aggregate custody statement is not a new local pixel audit. The pinned wave-1a report matches the hash in pinned_controls.json; its earlier verification remains FAIL (189 pass, 4 fail), including its historical missing aggregate receipt/custody evidence. Pinning the report does not remove those recorded gaps.

Failed readback checks: none.
