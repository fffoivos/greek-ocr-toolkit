# Collection v2 (cleaned pool)

Built by `scripts/harvest/apply_clean.py` from pool v1 (293,439 lines) and the compiled analysis decisions ([DECISIONS.md](../../analysis/DECISIONS.md), rules.json, impact.json) at git `f273cc0bf4be233df2d51b50250e4a9b2bb42c7b`. Variant **strict**; lexicon moved wholly to train.

## Totals

| Step | Lines |
| --- | --- |
| Pool v1 | 293,439 |
| Dropped by rules (strict) | 21,449 |
| Kept back vs the spec variant (weak R3/R13 hits) | 9,936 |
| Relabelled (label_v1 kept on the row) | 10,313 |
| Lexicon lines moved dev/test → train | 2,868 |
| Rejected by global label hold-out after relabel | 3 |
| **Admitted v2** | **271,987** |

## Drops by rule (a line may carry several)

| Rule | Lines |
| --- | --- |
| DROP_BOOK | 2,783 |
| R1 | 92 |
| R2 | 5,274 |
| R3 | 2,948 |
| R4 | 592 |
| R5 | 2,435 |
| R6 | 175 |
| R7 | 7,397 |
| R9 | 127 |
| R10 | 394 |
| R12 | 765 |
| R13 | 1,976 |
| R14 | 155 |
| R15 | 2,860 |

## Relabels by rule

| Rule | Lines |
| --- | --- |
| R15 | 364 |
| R6 | 9,853 |
| R8 | 112 |

## Class × split before

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 137756 | 8987 | 31366 | 178109 |
| greek_mono | 60803 | 4302 | 10748 | 75853 |
| greek_latin_cs | 6019 | 661 | 1370 | 8050 |
| latin | 11598 | 1272 | 2331 | 15201 |
| cyrillic | 12269 | 424 | 3533 | 16226 |
| furniture | 0 | 0 | 0 | 0 |

## Class × split after

| Class | Train | Dev | Test | Total |
| --- | --- | --- | --- | --- |
| greek_poly | 124669 | 8110 | 28620 | 161399 |
| greek_mono | 58749 | 4076 | 10249 | 73074 |
| greek_latin_cs | 6380 | 380 | 861 | 7621 |
| latin | 13107 | 545 | 773 | 14425 |
| cyrillic | 11531 | 411 | 3526 | 15468 |
| furniture | 0 | 0 | 0 | 0 |

## Checks

- Books present in more than one split: 0
- Crop sample checked: 2,804 rows, missing files: 0
- Reserved Wikisource human labels honoured: 3,114
- Pool v1, wave files and crops unchanged; no network or Google calls.

Files: admitted_all_v2.jsonl (git-ignored, reproducible), manifest_v2_{train,dev,test}.json, import_real_v2_{all,train,dev,test}.jsonl (git-ignored), dropped_v2.jsonl, relabels_v2.jsonl, rejected_global_v2.jsonl, split_moves_v2.json, validation_v2.json (tracked).
CLEAN_V2: done | variant: strict | pool_v1: 293439 | dropped: 21449 | relabelled: 10313 | moved: 2868 | rejected: 3 | admitted_v2: 271987 | train: 214436 | dev: 13522 | test: 44029 | poly: 161399 | mono: 73074 | cs: 7621 | latin: 14425 | cyr: 15468
