# SCALE1 record: scaling wave 3 part 1 unique-row subsets (20 Oct 2026)

**COMPLETED.** Clariden job 3705111, submitted by the coordinator, status ok. Package `scaling_w3/data_pkg/bc009e90` (SCALE1 + B + C). Attempt `$W/scaling_w3/subsets/scale1-c05-003/`.
- `SUBSETS_RECEIPT.json` is copied here: sha256 `467566a7877a6abb18af855d166ebd45597c984d5ad15f595a5f2f0d1a4414e2`, equal to the coordinator's value and to Clariden.
- Tags input: `scale1-c05-002/train_tags.jsonl.gz` `4a2f4ccb…`, receipt `e4a155eb…` (job 3705068).
- Classifier: bench02 `aa950a88…`, unchanged. Plan: `subsets_plan.json` `8258d776…`. Nesting: ref_208k ⊂ ref_364871 asserted (`nesting: true`).

## Design (coordinator ruling B; see `../README.md`)
- **Universe** = release v3 (W1/W2, 168,637) ∪ census_05-admitted v_c (collection-v2-train, 196,234) = 364,871.
  - DATA_PLAN §4.1's strict reading (reference = v_c only) collapses the ladder. The programme §5 line "sized from release v3" therefore governs.
- **Reference arm:** natural frequency, as seeded prefixes of one permutation. The 364,871 point is the **actual maximum** (420k exceeds the universe). At that point, targeted = reference at full universe.
- **Targeted arm:** 208k only.
  - Target shares are the benchmark 0.2 test-quota shares, assigned by the unchanged bench02 precedence classifier.
  - Within each class: a seeded source → edition rotation, with no caps.
  - A class whose supply is short contributes all its rows; its surplus is redistributed proportionally over the rest. There are 4 redistribution rounds and 0 unclassified fill.
- The parliament 25% draw cap and the synthetic 50% belong to the trainer's draw contract, not to unique-row selection.

## Subsets and exposure audit (asserted per subset in the job)
| Subset | Rows | sha256 | W1 | W2 | v_c | Crops re-hashed | Benchmark keys | Benchmark crop shas | Dev/test editions | v2 dev/test docs |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ref_208k | 208,000 | `6aa2f40cb225f114…` | 29,065 | 67,199 | 111,736 | 208,000 | 0 | 0 | 0 | 0 |
| ref_364871 | 364,871 | `0cf865f094ff3f95…` | 50,736 | 117,901 | 196,234 | 364,871 | 0 | 0 | 0 | 0 |
| tgt_208k | 208,000 | `fd02f3bd9e7e95d6…` | 40,068 | 77,061 | 90,871 | 208,000 | 0 | 0 | 0 | 0 |

The crops come from:
- W1/W2: the CROPS4 originals, via REL3 `crop_relative_path`, each sha checked against the census binding;
- v_c: the census `crop_path`.

Every crop was re-hashed by the job.

## Primary class per subset, and the targeted arm against the benchmark test-quota shares
| Class | ref_208k | ref_364871 | tgt_208k | Benchmark test share | tgt_208k share | tgt − bench (pp) |
|---|---:|---:|---:|---:|---:|---:|
| caps_headings | 5,811 | 10,179 | 10,179 | 4.88% | 4.89% | +0.02 |
| curved_skewed | 7,844 | 13,661 | 13,661 | 4.07% | 6.57% | +2.50 |
| degraded | 3,256 | 5,728 | 5,728 | 4.07% | 2.75% | -1.31 |
| font_extremes | 42,873 | 75,407 | 13,808 | 4.07% | 6.64% | +2.57 |
| greek_latin | 3,157 | 5,455 | 5,455 | 6.50% | 2.62% | -3.88 |
| historical_russian | 859 | 1,525 | 1,525 | 4.88% | 0.73% | -4.14 |
| latin | 5,945 | 10,438 | 10,438 | 6.50% | 5.02% | -1.49 |
| leaders_dashes | 30,847 | 54,105 | 13,808 | 4.07% | 6.64% | +2.57 |
| long | 26,776 | 46,927 | 22,092 | 6.50% | 10.62% | +4.12 |
| modern_cyrillic | 1,683 | 2,896 | 2,896 | 6.50% | 1.39% | -5.11 |
| monotonic | 23,919 | 42,018 | 33,138 | 9.76% | 15.93% | +6.18 |
| numeric_cells | 3,721 | 6,607 | 6,607 | 8.13% | 3.18% | -4.95 |
| poly_dictionary_journal | 6,491 | 11,355 | 11,355 | 6.50% | 5.46% | -1.04 |
| polytonic | 40,362 | 70,691 | 49,708 | 14.63% | 23.90% | +9.26 |
| short | 933 | 1,648 | 1,648 | 4.88% | 0.79% | -4.09 |
| unclassified | 162 | 277 | 0 | — | 0.00% | — |
| vertical_turned | 3,361 | 5,954 | 5,954 | 4.07% | 2.86% | -1.20 |

**Reading the targeted arm.** 11 of the 16 classes are **supply-exhausted** in the universe, so tgt_208k contains all their rows:
- caps_headings, curved_skewed, degraded, greek_latin, historical_russian, latin;
- modern_cyrillic, numeric_cells, poly_dictionary_journal, short, vertical_turned.

Their surplus went proportionally to polytonic, monotonic, long, font_extremes and leaders_dashes. The targeted arm is therefore **more balanced than the reference arm but not at the benchmark shares**. The largest gaps:

| Class | tgt_208k share | Benchmark share |
|---|---:|---:|
| modern_cyrillic | 1.39% | 6.50% |
| numeric_cells | 3.18% | 8.13% |
| historical_russian | 0.73% | 4.88% |
| short | 0.79% | 4.88% |
| polytonic | 23.9% | 14.6% |

Two further constraints on the targeted arm:
- v_c rows cannot carry the numeric_cells, short or degraded classes, because their bbox and DocAI confidence are unavailable. Those classes come from W1/W2 only.
- `unclassified` rows (277 in the universe) are not used.

## Per source
| Source | ref_208k | ref_364871 | tgt_208k |
|---|---:|---:|---:|
| gazette_modern | 47,984 | 84,078 | 50,918 |
| parliament_proceedings_1975_2000 | 32,466 | 57,251 | 13,112 |
| anemi_round1 | 26,318 | 46,172 | 15,275 |
| ia_poly1850 | 15,451 | 26,969 | 15,592 |
| vouli_parliament_1850s | 13,998 | 24,604 | 15,344 |
| anemi_round2 | 10,513 | 18,421 | 12,449 |
| bsb_poly1850 | 10,462 | 18,327 | 14,920 |
| anemi_mixed | 8,198 | 14,244 | 10,112 |
| lekythos | 6,089 | 10,657 | 8,978 |
| archive_b28038630 | 5,395 | 9,432 | 2,044 |
| nlg | 5,303 | 9,396 | 8,090 |
| ia_greek_latin | 4,234 | 7,361 | 7,019 |
| elstat | 2,487 | 4,403 | 4,170 |
| kosmopolis | 2,399 | 4,220 | 4,220 |
| serbia | 1,855 | 3,226 | 3,222 |
| openarchives_Pandemos | 1,358 | 2,370 | 1,606 |
| openarchives_kallipos | 1,158 | 2,070 | 1,509 |
| openarchives_anaktisis | 1,103 | 1,961 | 1,491 |
| openarchives_KEIED | 1,123 | 1,941 | 1,639 |
| openarchives_Dione | 1,108 | 1,910 | 1,512 |
| openarchives_hellanicus | 1,086 | 1,905 | 1,442 |
| openarchives_ktisis | 1,060 | 1,868 | 1,410 |
| openarchives_apothesis | 921 | 1,580 | 1,479 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 857 | 1,509 | 1,509 |
| openarchives_nemertes | 838 | 1,482 | 1,425 |
| archive_AA9613308335D0B014B | 835 | 1,459 | 1,459 |
| openarchives_ntua | 751 | 1,342 | 1,341 |
| archive_bub_gb_mG0mAQAAIAAJ | 612 | 1,113 | 1,113 |
| archive_bub_gb_Cmg6AQAAIAAJ | 387 | 660 | 660 |
| openarchives_mixed_apothesis | 338 | 584 | 584 |
| openarchives_mixed_ktisis | 299 | 527 | 527 |
| openarchives_mixed_Dione | 229 | 411 | 411 |
| openarchives_mixed_anaktisis | 238 | 407 | 407 |
| openarchives_mixed_KEIED | 227 | 404 | 404 |
| openarchives_mixed_hellanicus | 142 | 273 | 273 |
| openarchives_mixed_Pandemos | 26 | 58 | 58 |
| archive_izvestiianatsars12192829tsar | 28 | 57 | 57 |
| archive_izvestiianabulga610193138bulg | 33 | 55 | 55 |
| openarchives_mixed_nemertes | 21 | 41 | 41 |
| archive_izvestiianabul25192530bul | 20 | 32 | 32 |
| openarchives_mixed_ntua | 16 | 30 | 30 |
| openarchives_mixed_kallipos | 13 | 23 | 23 |
| archive_b24878935 | 11 | 20 | 20 |
| archive_izvestiianatsars1516194243tsar | 10 | 18 | 18 |

