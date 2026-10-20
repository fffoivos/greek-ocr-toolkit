200 rows; ADMIT 43 / HOLD 128 / DROP 29; admitted_train 43; gate exclusions 52; invariants PASS (15/15).

Published generation: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292`. Counts use exported dispositions and reasons only. Foreign-script gate reason is `unexpected_script` (the code name). Class is the ledger role, exactly summary.by_stratum.role; script is retained in by_stratum. all_reasons includes distinct reason names/strings from decisions, stages and routes, once per row; all_disposition_reasons contains only final disposition reasons. Held-out protection checks training admissions; dev/test ADMIT rows are evaluation passes. The protected crop list is the writer’s registered dev/test crops; protected editions are policy entries plus registered non-train editions. Root ledger is immutable input provenance, never a verdict source. Only compact identity indexes are retained in memory; JSONL payloads are streamed. Stage attribution uses serialized stages first, then known finish() call sites; missing producers are explicitly labeled. Failure counts in invariants are zero on PASS.

### Totals

Counted from: `decisions.jsonl`.

| disposition | rows |
| --- | --- |
| ADMIT | 43 |
| DROP | 29 |
| HOLD | 128 |

### Disposition reason occurrences

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| cell_status_unresolved | 38 |
| mixed_script_word | 2 |
| nonletter_fraction | 4 |
| segmentation | 11 |
| short_line | 5 |
| single_character_cell | 7 |
| split_or_edition_identity_unresolved | 90 |
| unexpected_script | 1 |

### Route statuses

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| content_repair:not_applicable | 43 |
| content_repair:not_run_due_to_prior_exclusion | 156 |
| content_repair:verified_no_change | 1 |
| cyrillic:not_applicable | 36 |
| cyrillic:not_run_due_to_prior_exclusion | 153 |
| cyrillic:verified_no_change | 11 |
| dashes:not_applicable | 38 |
| dashes:not_run_due_to_prior_exclusion | 138 |
| dashes:tag_only | 24 |
| numerics:not_applicable | 25 |
| numerics:not_run_due_to_prior_exclusion | 118 |
| numerics:verified_no_change | 57 |
| polytonic:not_applicable | 27 |
| polytonic:not_applied_out_of_scope | 77 |
| polytonic:not_run_due_to_prior_exclusion | 96 |

### Segmentation availability

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| measured | 148 |

### Gate totals

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| DROP | 14 |
| HOLD | 38 |
| cell_status_unresolved | 38 |
| mixed_script_word | 2 |
| short_line | 5 |
| single_character_cell | 7 |
| unexpected_script | 1 |

### V3 splits

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| dev | 0 |
| test | 0 |
| train | 0 |
| unassigned | 112 |

### Pending totals

Counted from: `pending_<tool>.jsonl`.

| value | rows |
| --- | --- |
| content_repair | 0 |
| cyrillic | 0 |
| numerics | 0 |
| polytonic | 0 |

### Pipeline versions

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| 0.3.2 | 200 |

### Admission export

Counted from: `admitted_train.jsonl`.

| rows |
| --- |
| 43 |

### Completeness

Counted from: `decisions.jsonl`, ledger binding.

| rows | input_rows | complete |
| --- | --- | --- |
| 200 | 200 | True |

### Invariants

Counted from: `decisions.jsonl`, `admitted_train.jsonl`, `summary.json`, ledger inventory.

| invariant | status | count |
| --- | --- | --- |
| admitted_train_equals_eligible | PASS | 0 |
| admitted_train_violations | PASS | 0 |
| bound_inventory_counts | PASS | 0 |
| dispositions_sum | PASS | 0 |
| duplicates | PASS | 0 |
| expect_rows | PASS | 0 |
| gate_route_violations | PASS | 0 |
| gate_segmentation_violations | PASS | 0 |
| heldout_leaks | PASS | 0 |
| missing_rows | PASS | 0 |
| no_reason | PASS | 0 |
| pipeline_version_mismatch | PASS | 0 |
| summary_by_stratum | PASS | 0 |
| summary_dispositions | PASS | 0 |
| unexpected_rows | PASS | 0 |

### all_disposition_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| cell_status_unresolved | collection-v2-dev | dev | HOLD | 2 |
| cell_status_unresolved | collection-v2-test | test | HOLD | 9 |
| cell_status_unresolved | collection-v2-train | train | HOLD | 27 |
| mixed_script_word | accepted-calibration-888 | train | DROP | 1 |
| mixed_script_word | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| nonletter_fraction | accepted-calibration-888 | train | DROP | 4 |
| segmentation | collect-v3-W2-20261018-0524 | unassigned | DROP | 5 |
| segmentation | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 6 |
| short_line | accepted-calibration-888 | train | DROP | 1 |
| short_line | accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| short_line | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| short_line | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| single_character_cell | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| single_character_cell | collect-v3-W2-20261018-0524 | unassigned | DROP | 4 |
| single_character_cell | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| single_character_cell | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| split_or_edition_identity_unresolved | collect-v3-W1-20261018-0524 | unassigned | HOLD | 23 |
| split_or_edition_identity_unresolved | collect-v3-W2-20261018-0524 | unassigned | HOLD | 31 |
| split_or_edition_identity_unresolved | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 31 |
| split_or_edition_identity_unresolved | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 5 |
| unexpected_script | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |

### all_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| cell_status_unresolved | collection-v2-dev | dev | HOLD | 2 |
| cell_status_unresolved | collection-v2-test | test | HOLD | 9 |
| cell_status_unresolved | collection-v2-train | train | HOLD | 27 |
| gate: second complete line | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| gate: too many whole neighbour words | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gate: too many whole neighbour words | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| length: OCR length matches; vertical padding is within the selected allowance. | accepted-calibration-888 | train | ADMIT | 34 |
| length: OCR length matches; vertical padding is within the selected allowance. | accepted-calibration-888 | train | DROP | 4 |
| length: OCR length matches; vertical padding is within the selected allowance. | accepted-calibration-888-mock-shard-1 | train | ADMIT | 9 |
| length: OCR length matches; vertical padding is within the selected allowance. | collect-v3-W1-20261018-0524 | unassigned | HOLD | 23 |
| length: OCR length matches; vertical padding is within the selected allowance. | collect-v3-W2-20261018-0524 | unassigned | HOLD | 31 |
| length: OCR length matches; vertical padding is within the selected allowance. | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 31 |
| length: OCR length matches; vertical padding is within the selected allowance. | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 5 |
| length: Too little OCR output for the text box after height normalisation. | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| length: Too much OCR output for the text box after height normalisation. | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| length: Too much OCR output for the text box after height normalisation. | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| mixed_script_word | accepted-calibration-888 | train | DROP | 1 |
| mixed_script_word | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| nonletter_fraction | accepted-calibration-888 | train | DROP | 4 |
| route out of scope for this release | accepted-calibration-888 | train | ADMIT | 14 |
| route out of scope for this release | accepted-calibration-888 | train | DROP | 4 |
| route out of scope for this release | accepted-calibration-888-mock-shard-1 | train | ADMIT | 2 |
| route out of scope for this release | collect-v3-W1-20261018-0524 | unassigned | HOLD | 11 |
| route out of scope for this release | collect-v3-W2-20261018-0524 | unassigned | HOLD | 22 |
| route out of scope for this release | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 22 |
| route out of scope for this release | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 2 |
| segmentation | collect-v3-W2-20261018-0524 | unassigned | DROP | 5 |
| segmentation | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 6 |
| short_line | accepted-calibration-888 | train | DROP | 1 |
| short_line | accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| short_line | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| short_line | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| single_character_cell | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| single_character_cell | collect-v3-W2-20261018-0524 | unassigned | DROP | 4 |
| single_character_cell | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| single_character_cell | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| split_or_edition_identity_unresolved | collect-v3-W1-20261018-0524 | unassigned | HOLD | 23 |
| split_or_edition_identity_unresolved | collect-v3-W2-20261018-0524 | unassigned | HOLD | 31 |
| split_or_edition_identity_unresolved | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 31 |
| split_or_edition_identity_unresolved | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 5 |
| unexpected_character | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| unexpected_character | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| unexpected_character | collection-v2-train | train | HOLD | 1 |
| unexpected_script | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |

### all_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

| reason | disposition | rows |
| --- | --- | --- |
| cell_status_unresolved | HOLD | 38 |
| gate: second complete line | DROP | 1 |
| gate: too many whole neighbour words | DROP | 2 |
| length: OCR length matches; vertical padding is within the selected allowance. | ADMIT | 43 |
| length: OCR length matches; vertical padding is within the selected allowance. | DROP | 4 |
| length: OCR length matches; vertical padding is within the selected allowance. | HOLD | 90 |
| length: Too little OCR output for the text box after height normalisation. | DROP | 1 |
| length: Too much OCR output for the text box after height normalisation. | DROP | 3 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | DROP | 4 |
| mixed_script_word | DROP | 2 |
| nonletter_fraction | DROP | 4 |
| route out of scope for this release | ADMIT | 16 |
| route out of scope for this release | DROP | 4 |
| route out of scope for this release | HOLD | 57 |
| segmentation | DROP | 11 |
| short_line | DROP | 5 |
| single_character_cell | DROP | 7 |
| split_or_edition_identity_unresolved | HOLD | 90 |
| unexpected_character | DROP | 1 |
| unexpected_character | HOLD | 2 |
| unexpected_script | DROP | 1 |

### by_stratum

Counted from: `decisions.jsonl` + ledger inventory.

| parent | split | source | role | script | disposition | rows |
| --- | --- | --- | --- | --- | --- | --- |
| accepted-calibration-888 | train | bsb_poly1850 | headings_caps | greek_mono | ADMIT | 1 |
| accepted-calibration-888 | train | bsb_poly1850 | latin | latin | ADMIT | 9 |
| accepted-calibration-888 | train | bsb_poly1850 | mixed_greek_latin | greek_latin_cs | ADMIT | 5 |
| accepted-calibration-888 | train | bsb_poly1850 | mixed_greek_latin | greek_latin_cs | DROP | 2 |
| accepted-calibration-888 | train | bsb_poly1850 | mixed_greek_latin | latin | ADMIT | 2 |
| accepted-calibration-888 | train | bsb_poly1850 | mixed_greek_latin | latin | DROP | 2 |
| accepted-calibration-888 | train | bsb_poly1850 | modern_scanned | greek_mono | ADMIT | 5 |
| accepted-calibration-888 | train | bsb_poly1850 | modern_scanned | greek_mono | DROP | 2 |
| accepted-calibration-888 | train | bsb_poly1850 | numerics_tables | nonletter | ADMIT | 11 |
| accepted-calibration-888 | train | bsb_poly1850 | poly1850 | greek_poly | ADMIT | 1 |
| accepted-calibration-888-mock-shard-1 | train | bsb_poly1850 | cyrillic | cyrillic | ADMIT | 7 |
| accepted-calibration-888-mock-shard-1 | train | bsb_poly1850 | nonletter | nonletter | DROP | 1 |
| accepted-calibration-888-mock-shard-1 | train | bsb_poly1850 | poly1900 | greek_poly | ADMIT | 2 |
| collect-v3-W1-20261018-0524 | unassigned | bsb_poly1850 | mixed_greek_latin | latin | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | elstat | numerics_tables | nonletter | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | dialogue_fiction | greek_mono | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | headings_caps | greek_mono | DROP | 1 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | modern_scanned | greek_mono | DROP | 1 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | modern_scanned | greek_mono | HOLD | 4 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | numerics_tables | nonletter | HOLD | 3 |
| collect-v3-W1-20261018-0524 | unassigned | ia_greek_latin | latin | latin | HOLD | 5 |
| collect-v3-W1-20261018-0524 | unassigned | ia_greek_latin | mixed_greek_latin | latin | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | ia_poly1850 | latin | latin | HOLD | 2 |
| collect-v3-W1-20261018-0524 | unassigned | ia_poly1850 | poly1850 | greek_poly | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | ia_russian | cyrillic | cyrillic | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | lekythos | nonletter | nonletter | DROP | 1 |
| collect-v3-W1-20261018-0524 | unassigned | lekythos | poly1900 | greek_poly | HOLD | 3 |
| collect-v3-W2-20261018-0524 | unassigned | bsb_poly1850 | latin | latin | HOLD | 2 |
| collect-v3-W2-20261018-0524 | unassigned | bsb_poly1850 | poly1850 | greek_poly | HOLD | 3 |
| collect-v3-W2-20261018-0524 | unassigned | elstat | latin | latin | DROP | 2 |
| collect-v3-W2-20261018-0524 | unassigned | elstat | numerics_tables | nonletter | HOLD | 3 |
| collect-v3-W2-20261018-0524 | unassigned | elstat | poly1900 | greek_poly | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | cyrillic | cyrillic | DROP | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | dialogue_fiction | greek_mono | HOLD | 2 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | headings_caps | greek_mono | HOLD | 6 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | latin | latin | DROP | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | modern_scanned | greek_mono | DROP | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | modern_scanned | greek_mono | HOLD | 7 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | nonletter | nonletter | DROP | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | numerics_tables | greek_mono | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | numerics_tables | nonletter | DROP | 3 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | numerics_tables | nonletter | HOLD | 4 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | poly1900 | greek_poly | HOLD | 2 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | gazette_modern | headings_caps | greek_mono | DROP | 2 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | gazette_modern | headings_caps | greek_mono | HOLD | 5 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | gazette_modern | modern_scanned | greek_mono | DROP | 3 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | gazette_modern | modern_scanned | greek_mono | HOLD | 10 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | gazette_modern | nonletter | nonletter | DROP | 1 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | gazette_modern | numerics_tables | nonletter | DROP | 1 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | gazette_modern | numerics_tables | nonletter | HOLD | 1 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | ia_poly1850 | latin | latin | DROP | 1 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | ia_poly1850 | latin | latin | HOLD | 7 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | ia_poly1850 | mixed_greek_latin | greek_latin_cs | DROP | 1 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | ia_poly1850 | mixed_greek_latin | greek_latin_cs | HOLD | 1 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | ia_poly1850 | numerics_tables | nonletter | HOLD | 1 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | ia_poly1850 | poly1850 | greek_poly | HOLD | 6 |
| collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | ia_poly1850 | poly1850 | greek_poly | HOLD | 1 |
| collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | nlg | nonletter | nonletter | DROP | 1 |
| collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | nlg | poly1900 | greek_poly | HOLD | 1 |
| collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | serbia | cyrillic | cyrillic | HOLD | 3 |
| collection-v2-dev | dev | anemi_mixed | latin | latin | HOLD | 1 |
| collection-v2-dev | dev | parliament_proceedings_1975_2000 | greek_mono | greek_mono | HOLD | 1 |
| collection-v2-test | test | anemi_round1 | greek_poly | greek_poly | HOLD | 1 |
| collection-v2-test | test | anemi_round2 | greek_poly | greek_poly | HOLD | 2 |
| collection-v2-test | test | openarchives_Dione | greek_mono | greek_mono | HOLD | 1 |
| collection-v2-test | test | openarchives_kallipos | greek_mono | greek_mono | HOLD | 1 |
| collection-v2-test | test | parliament_proceedings_1975_2000 | greek_mono | greek_mono | HOLD | 1 |
| collection-v2-test | test | parliament_proceedings_1975_2000 | greek_poly | greek_poly | HOLD | 1 |
| collection-v2-test | test | wikisource_el | greek_poly | greek_poly | HOLD | 1 |
| collection-v2-test | test | wikisource_ru | cyrillic | cyrillic | HOLD | 1 |
| collection-v2-train | train | anemi_mixed | greek_poly | greek_poly | HOLD | 2 |
| collection-v2-train | train | anemi_round1 | greek_poly | greek_poly | HOLD | 7 |
| collection-v2-train | train | anemi_round2 | greek_poly | greek_poly | HOLD | 7 |
| collection-v2-train | train | archive_AA9613308335D0B014B | cyrillic | cyrillic | HOLD | 1 |
| collection-v2-train | train | archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | cyrillic | HOLD | 1 |
| collection-v2-train | train | archive_izvestiianabul25192530bul | latin | latin | HOLD | 1 |
| collection-v2-train | train | openarchives_kallipos | greek_latin_cs | greek_latin_cs | HOLD | 1 |
| collection-v2-train | train | openarchives_kallipos | greek_mono | greek_mono | HOLD | 1 |
| collection-v2-train | train | parliament_proceedings_1975_2000 | greek_mono | greek_mono | HOLD | 4 |
| collection-v2-train | train | parliament_proceedings_1975_2000 | greek_poly | greek_poly | HOLD | 1 |
| collection-v2-train | train | vouli_parliament_1850s | greek_poly | greek_poly | HOLD | 1 |

### class

Counted from: `decisions.jsonl` + ledger inventory.

| role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| cyrillic | accepted-calibration-888-mock-shard-1 | train | ADMIT | 7 |
| cyrillic | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| cyrillic | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| cyrillic | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 3 |
| cyrillic | collection-v2-test | test | HOLD | 1 |
| cyrillic | collection-v2-train | train | HOLD | 2 |
| dialogue_fiction | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| dialogue_fiction | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| greek_latin_cs | collection-v2-train | train | HOLD | 1 |
| greek_mono | collection-v2-dev | dev | HOLD | 1 |
| greek_mono | collection-v2-test | test | HOLD | 3 |
| greek_mono | collection-v2-train | train | HOLD | 5 |
| greek_poly | collection-v2-test | test | HOLD | 5 |
| greek_poly | collection-v2-train | train | HOLD | 18 |
| headings_caps | accepted-calibration-888 | train | ADMIT | 1 |
| headings_caps | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| headings_caps | collect-v3-W2-20261018-0524 | unassigned | HOLD | 6 |
| headings_caps | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| headings_caps | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 5 |
| latin | accepted-calibration-888 | train | ADMIT | 9 |
| latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 7 |
| latin | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| latin | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 7 |
| latin | collection-v2-dev | dev | HOLD | 1 |
| latin | collection-v2-train | train | HOLD | 1 |
| mixed_greek_latin | accepted-calibration-888 | train | ADMIT | 7 |
| mixed_greek_latin | accepted-calibration-888 | train | DROP | 4 |
| mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 2 |
| mixed_greek_latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| mixed_greek_latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 1 |
| modern_scanned | accepted-calibration-888 | train | ADMIT | 5 |
| modern_scanned | accepted-calibration-888 | train | DROP | 2 |
| modern_scanned | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| modern_scanned | collect-v3-W1-20261018-0524 | unassigned | HOLD | 4 |
| modern_scanned | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| modern_scanned | collect-v3-W2-20261018-0524 | unassigned | HOLD | 7 |
| modern_scanned | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 3 |
| modern_scanned | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 10 |
| nonletter | accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| nonletter | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| nonletter | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| nonletter | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| nonletter | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| numerics_tables | accepted-calibration-888 | train | ADMIT | 11 |
| numerics_tables | collect-v3-W1-20261018-0524 | unassigned | HOLD | 4 |
| numerics_tables | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| numerics_tables | collect-v3-W2-20261018-0524 | unassigned | HOLD | 8 |
| numerics_tables | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| numerics_tables | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 2 |
| poly1850 | accepted-calibration-888 | train | ADMIT | 1 |
| poly1850 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| poly1850 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| poly1850 | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 6 |
| poly1850 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 1 |
| poly1900 | accepted-calibration-888-mock-shard-1 | train | ADMIT | 2 |
| poly1900 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 3 |
| poly1900 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| poly1900 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 1 |

### class_rates

Counted from: `decisions.jsonl` + ledger inventory.

| role | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| cyrillic | accepted-calibration-888-mock-shard-1 | train | 7 | 7 | 1.0 |
| cyrillic | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| cyrillic | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| cyrillic | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 3 | 0 | 0.0 |
| cyrillic | collection-v2-test | test | 1 | 0 | 0.0 |
| cyrillic | collection-v2-train | train | 2 | 0 | 0.0 |
| dialogue_fiction | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| dialogue_fiction | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| greek_latin_cs | collection-v2-train | train | 1 | 0 | 0.0 |
| greek_mono | collection-v2-dev | dev | 1 | 0 | 0.0 |
| greek_mono | collection-v2-test | test | 3 | 0 | 0.0 |
| greek_mono | collection-v2-train | train | 5 | 0 | 0.0 |
| greek_poly | collection-v2-test | test | 5 | 0 | 0.0 |
| greek_poly | collection-v2-train | train | 18 | 0 | 0.0 |
| headings_caps | accepted-calibration-888 | train | 1 | 1 | 1.0 |
| headings_caps | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| headings_caps | collect-v3-W2-20261018-0524 | unassigned | 6 | 0 | 0.0 |
| headings_caps | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 7 | 0 | 0.0 |
| latin | accepted-calibration-888 | train | 9 | 9 | 1.0 |
| latin | collect-v3-W1-20261018-0524 | unassigned | 7 | 0 | 0.0 |
| latin | collect-v3-W2-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 8 | 0 | 0.0 |
| latin | collection-v2-dev | dev | 1 | 0 | 0.0 |
| latin | collection-v2-train | train | 1 | 0 | 0.0 |
| mixed_greek_latin | accepted-calibration-888 | train | 11 | 7 | 0.6363636363636364 |
| mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| mixed_greek_latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 2 | 0 | 0.0 |
| modern_scanned | accepted-calibration-888 | train | 7 | 5 | 0.7142857142857143 |
| modern_scanned | collect-v3-W1-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| modern_scanned | collect-v3-W2-20261018-0524 | unassigned | 8 | 0 | 0.0 |
| modern_scanned | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 13 | 0 | 0.0 |
| nonletter | accepted-calibration-888-mock-shard-1 | train | 1 | 0 | 0.0 |
| nonletter | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| nonletter | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| nonletter | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 1 | 0 | 0.0 |
| nonletter | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 1 | 0 | 0.0 |
| numerics_tables | accepted-calibration-888 | train | 11 | 11 | 1.0 |
| numerics_tables | collect-v3-W1-20261018-0524 | unassigned | 4 | 0 | 0.0 |
| numerics_tables | collect-v3-W2-20261018-0524 | unassigned | 11 | 0 | 0.0 |
| numerics_tables | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 3 | 0 | 0.0 |
| poly1850 | accepted-calibration-888 | train | 1 | 1 | 1.0 |
| poly1850 | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| poly1850 | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| poly1850 | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 6 | 0 | 0.0 |
| poly1850 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 1 | 0 | 0.0 |
| poly1900 | accepted-calibration-888-mock-shard-1 | train | 2 | 2 | 1.0 |
| poly1900 | collect-v3-W1-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| poly1900 | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| poly1900 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 1 | 0 | 0.0 |

### class_totals

Counted from: `decisions.jsonl` + ledger inventory.

| role | split | disposition | rows |
| --- | --- | --- | --- |
| cyrillic | test | HOLD | 1 |
| cyrillic | train | ADMIT | 7 |
| cyrillic | train | HOLD | 2 |
| cyrillic | unassigned | DROP | 1 |
| cyrillic | unassigned | HOLD | 4 |
| dialogue_fiction | unassigned | HOLD | 3 |
| greek_latin_cs | train | HOLD | 1 |
| greek_mono | dev | HOLD | 1 |
| greek_mono | test | HOLD | 3 |
| greek_mono | train | HOLD | 5 |
| greek_poly | test | HOLD | 5 |
| greek_poly | train | HOLD | 18 |
| headings_caps | train | ADMIT | 1 |
| headings_caps | unassigned | DROP | 3 |
| headings_caps | unassigned | HOLD | 11 |
| latin | dev | HOLD | 1 |
| latin | train | ADMIT | 9 |
| latin | train | HOLD | 1 |
| latin | unassigned | DROP | 4 |
| latin | unassigned | HOLD | 16 |
| mixed_greek_latin | train | ADMIT | 7 |
| mixed_greek_latin | train | DROP | 4 |
| mixed_greek_latin | unassigned | DROP | 1 |
| mixed_greek_latin | unassigned | HOLD | 3 |
| modern_scanned | train | ADMIT | 5 |
| modern_scanned | train | DROP | 2 |
| modern_scanned | unassigned | DROP | 5 |
| modern_scanned | unassigned | HOLD | 21 |
| nonletter | train | DROP | 1 |
| nonletter | unassigned | DROP | 4 |
| numerics_tables | train | ADMIT | 11 |
| numerics_tables | unassigned | DROP | 4 |
| numerics_tables | unassigned | HOLD | 14 |
| poly1850 | train | ADMIT | 1 |
| poly1850 | unassigned | HOLD | 11 |
| poly1900 | train | ADMIT | 2 |
| poly1900 | unassigned | HOLD | 7 |

### class_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| role | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- |
| cyrillic | test | 1 | 0 | 0.0 |
| cyrillic | train | 9 | 7 | 0.7777777777777778 |
| cyrillic | unassigned | 5 | 0 | 0.0 |
| dialogue_fiction | unassigned | 3 | 0 | 0.0 |
| greek_latin_cs | train | 1 | 0 | 0.0 |
| greek_mono | dev | 1 | 0 | 0.0 |
| greek_mono | test | 3 | 0 | 0.0 |
| greek_mono | train | 5 | 0 | 0.0 |
| greek_poly | test | 5 | 0 | 0.0 |
| greek_poly | train | 18 | 0 | 0.0 |
| headings_caps | train | 1 | 1 | 1.0 |
| headings_caps | unassigned | 14 | 0 | 0.0 |
| latin | dev | 1 | 0 | 0.0 |
| latin | train | 10 | 9 | 0.9 |
| latin | unassigned | 20 | 0 | 0.0 |
| mixed_greek_latin | train | 11 | 7 | 0.6363636363636364 |
| mixed_greek_latin | unassigned | 4 | 0 | 0.0 |
| modern_scanned | train | 7 | 5 | 0.7142857142857143 |
| modern_scanned | unassigned | 26 | 0 | 0.0 |
| nonletter | train | 1 | 0 | 0.0 |
| nonletter | unassigned | 4 | 0 | 0.0 |
| numerics_tables | train | 11 | 11 | 1.0 |
| numerics_tables | unassigned | 18 | 0 | 0.0 |
| poly1850 | train | 1 | 1 | 1.0 |
| poly1850 | unassigned | 11 | 0 | 0.0 |
| poly1900 | train | 2 | 2 | 1.0 |
| poly1900 | unassigned | 7 | 0 | 0.0 |

### deciding_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | stage | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| cell_status_unresolved | content_gate | collection-v2-dev | dev | HOLD | 2 |
| cell_status_unresolved | content_gate | collection-v2-test | test | HOLD | 9 |
| cell_status_unresolved | content_gate | collection-v2-train | train | HOLD | 27 |
| mixed_script_word | content_gate | accepted-calibration-888 | train | DROP | 1 |
| mixed_script_word | content_gate | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| nonletter_fraction | final_eligibility | accepted-calibration-888 | train | DROP | 4 |
| segmentation | segmentation | collect-v3-W2-20261018-0524 | unassigned | DROP | 5 |
| segmentation | segmentation | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 6 |
| short_line | content_gate | accepted-calibration-888 | train | DROP | 1 |
| short_line | content_gate | accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| short_line | content_gate | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| short_line | content_gate | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| single_character_cell | content_gate | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| single_character_cell | content_gate | collect-v3-W2-20261018-0524 | unassigned | DROP | 4 |
| single_character_cell | content_gate | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| single_character_cell | content_gate | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| split_or_edition_identity_unresolved | split_admission | collect-v3-W1-20261018-0524 | unassigned | HOLD | 23 |
| split_or_edition_identity_unresolved | split_admission | collect-v3-W2-20261018-0524 | unassigned | HOLD | 31 |
| split_or_edition_identity_unresolved | split_admission | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 31 |
| split_or_edition_identity_unresolved | split_admission | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 5 |

### deciding_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

| reason | stage | disposition | rows |
| --- | --- | --- | --- |
| cell_status_unresolved | content_gate | HOLD | 38 |
| mixed_script_word | content_gate | DROP | 2 |
| nonletter_fraction | final_eligibility | DROP | 4 |
| segmentation | segmentation | DROP | 11 |
| short_line | content_gate | DROP | 5 |
| single_character_cell | content_gate | DROP | 7 |
| split_or_edition_identity_unresolved | split_admission | HOLD | 90 |

### decisions_by_parent_split

Counted from: `decisions.jsonl` + ledger inventory.

| parent | split | disposition | rows |
| --- | --- | --- | --- |
| accepted-calibration-888 | train | ADMIT | 34 |
| accepted-calibration-888 | train | DROP | 6 |
| accepted-calibration-888-mock-shard-1 | train | ADMIT | 9 |
| accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| collect-v3-W1-20261018-0524 | unassigned | DROP | 3 |
| collect-v3-W1-20261018-0524 | unassigned | HOLD | 23 |
| collect-v3-W2-20261018-0524 | unassigned | DROP | 9 |
| collect-v3-W2-20261018-0524 | unassigned | HOLD | 31 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 9 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 31 |
| collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 5 |
| collection-v2-dev | dev | HOLD | 2 |
| collection-v2-test | test | HOLD | 9 |
| collection-v2-train | train | HOLD | 27 |

### gate_by_class

Counted from: `decisions.jsonl` + ledger inventory.

| reason | role | split | disposition | rows |
| --- | --- | --- | --- | --- |
| cell_status_unresolved | cyrillic | test | HOLD | 1 |
| cell_status_unresolved | cyrillic | train | HOLD | 2 |
| cell_status_unresolved | greek_latin_cs | train | HOLD | 1 |
| cell_status_unresolved | greek_mono | dev | HOLD | 1 |
| cell_status_unresolved | greek_mono | test | HOLD | 3 |
| cell_status_unresolved | greek_mono | train | HOLD | 5 |
| cell_status_unresolved | greek_poly | test | HOLD | 5 |
| cell_status_unresolved | greek_poly | train | HOLD | 18 |
| cell_status_unresolved | latin | dev | HOLD | 1 |
| cell_status_unresolved | latin | train | HOLD | 1 |
| mixed_script_word | headings_caps | unassigned | DROP | 1 |
| mixed_script_word | mixed_greek_latin | train | DROP | 1 |
| short_line | latin | unassigned | DROP | 1 |
| short_line | mixed_greek_latin | train | DROP | 1 |
| short_line | modern_scanned | unassigned | DROP | 2 |
| short_line | nonletter | train | DROP | 1 |
| single_character_cell | nonletter | unassigned | DROP | 4 |
| single_character_cell | numerics_tables | unassigned | DROP | 3 |
| unexpected_script | headings_caps | unassigned | DROP | 1 |

### gate_by_parent

Counted from: `decisions.jsonl` + ledger inventory.

| reason | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| cell_status_unresolved | collection-v2-dev | dev | HOLD | 2 |
| cell_status_unresolved | collection-v2-test | test | HOLD | 9 |
| cell_status_unresolved | collection-v2-train | train | HOLD | 27 |
| mixed_script_word | accepted-calibration-888 | train | DROP | 1 |
| mixed_script_word | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| short_line | accepted-calibration-888 | train | DROP | 1 |
| short_line | accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| short_line | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| short_line | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| single_character_cell | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| single_character_cell | collect-v3-W2-20261018-0524 | unassigned | DROP | 4 |
| single_character_cell | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| single_character_cell | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| unexpected_script | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |

### gate_by_source

Counted from: `decisions.jsonl` + ledger inventory.

| reason | source | split | disposition | rows |
| --- | --- | --- | --- | --- |
| cell_status_unresolved | anemi_mixed | dev | HOLD | 1 |
| cell_status_unresolved | anemi_mixed | train | HOLD | 2 |
| cell_status_unresolved | anemi_round1 | test | HOLD | 1 |
| cell_status_unresolved | anemi_round1 | train | HOLD | 7 |
| cell_status_unresolved | anemi_round2 | test | HOLD | 2 |
| cell_status_unresolved | anemi_round2 | train | HOLD | 7 |
| cell_status_unresolved | archive_AA9613308335D0B014B | train | HOLD | 1 |
| cell_status_unresolved | archive_bub_gb_Cmg6AQAAIAAJ | train | HOLD | 1 |
| cell_status_unresolved | archive_izvestiianabul25192530bul | train | HOLD | 1 |
| cell_status_unresolved | openarchives_Dione | test | HOLD | 1 |
| cell_status_unresolved | openarchives_kallipos | test | HOLD | 1 |
| cell_status_unresolved | openarchives_kallipos | train | HOLD | 2 |
| cell_status_unresolved | parliament_proceedings_1975_2000 | dev | HOLD | 1 |
| cell_status_unresolved | parliament_proceedings_1975_2000 | test | HOLD | 2 |
| cell_status_unresolved | parliament_proceedings_1975_2000 | train | HOLD | 5 |
| cell_status_unresolved | vouli_parliament_1850s | train | HOLD | 1 |
| cell_status_unresolved | wikisource_el | test | HOLD | 1 |
| cell_status_unresolved | wikisource_ru | test | HOLD | 1 |
| mixed_script_word | bsb_poly1850 | train | DROP | 1 |
| mixed_script_word | gazette_modern | unassigned | DROP | 1 |
| short_line | bsb_poly1850 | train | DROP | 2 |
| short_line | gazette_modern | unassigned | DROP | 2 |
| short_line | ia_poly1850 | unassigned | DROP | 1 |
| single_character_cell | gazette_modern | unassigned | DROP | 5 |
| single_character_cell | lekythos | unassigned | DROP | 1 |
| single_character_cell | nlg | unassigned | DROP | 1 |
| unexpected_script | gazette_modern | unassigned | DROP | 1 |

### gate_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | source | role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- | --- |
| cell_status_unresolved | anemi_mixed | greek_poly | collection-v2-train | train | HOLD | 2 |
| cell_status_unresolved | anemi_mixed | latin | collection-v2-dev | dev | HOLD | 1 |
| cell_status_unresolved | anemi_round1 | greek_poly | collection-v2-test | test | HOLD | 1 |
| cell_status_unresolved | anemi_round1 | greek_poly | collection-v2-train | train | HOLD | 7 |
| cell_status_unresolved | anemi_round2 | greek_poly | collection-v2-test | test | HOLD | 2 |
| cell_status_unresolved | anemi_round2 | greek_poly | collection-v2-train | train | HOLD | 7 |
| cell_status_unresolved | archive_AA9613308335D0B014B | cyrillic | collection-v2-train | train | HOLD | 1 |
| cell_status_unresolved | archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | collection-v2-train | train | HOLD | 1 |
| cell_status_unresolved | archive_izvestiianabul25192530bul | latin | collection-v2-train | train | HOLD | 1 |
| cell_status_unresolved | openarchives_Dione | greek_mono | collection-v2-test | test | HOLD | 1 |
| cell_status_unresolved | openarchives_kallipos | greek_latin_cs | collection-v2-train | train | HOLD | 1 |
| cell_status_unresolved | openarchives_kallipos | greek_mono | collection-v2-test | test | HOLD | 1 |
| cell_status_unresolved | openarchives_kallipos | greek_mono | collection-v2-train | train | HOLD | 1 |
| cell_status_unresolved | parliament_proceedings_1975_2000 | greek_mono | collection-v2-dev | dev | HOLD | 1 |
| cell_status_unresolved | parliament_proceedings_1975_2000 | greek_mono | collection-v2-test | test | HOLD | 1 |
| cell_status_unresolved | parliament_proceedings_1975_2000 | greek_mono | collection-v2-train | train | HOLD | 4 |
| cell_status_unresolved | parliament_proceedings_1975_2000 | greek_poly | collection-v2-test | test | HOLD | 1 |
| cell_status_unresolved | parliament_proceedings_1975_2000 | greek_poly | collection-v2-train | train | HOLD | 1 |
| cell_status_unresolved | vouli_parliament_1850s | greek_poly | collection-v2-train | train | HOLD | 1 |
| cell_status_unresolved | wikisource_el | greek_poly | collection-v2-test | test | HOLD | 1 |
| cell_status_unresolved | wikisource_ru | cyrillic | collection-v2-test | test | HOLD | 1 |
| mixed_script_word | bsb_poly1850 | mixed_greek_latin | accepted-calibration-888 | train | DROP | 1 |
| mixed_script_word | gazette_modern | headings_caps | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| short_line | bsb_poly1850 | mixed_greek_latin | accepted-calibration-888 | train | DROP | 1 |
| short_line | bsb_poly1850 | nonletter | accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| short_line | gazette_modern | modern_scanned | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| short_line | gazette_modern | modern_scanned | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| short_line | ia_poly1850 | latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| single_character_cell | gazette_modern | nonletter | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| single_character_cell | gazette_modern | nonletter | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| single_character_cell | gazette_modern | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| single_character_cell | lekythos | nonletter | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| single_character_cell | nlg | nonletter | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| unexpected_script | gazette_modern | headings_caps | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |

### input_rows

Counted from: `ledger.sqlite` binding/observations.

| parent | rows | registered |
| --- | --- | --- |
| accepted-calibration-888 | 40 | 40 |
| accepted-calibration-888-mock-shard-1 | 10 | 10 |
| collect-v3-W1-20261018-0524 | 26 | 26 |
| collect-v3-W2-20261018-0524 | 40 | 40 |
| collect-v3-W2-20261018-0524-mock-shard-1 | 40 | 40 |
| collect-v3-W2-20261018-0524-mock-shard-2 | 6 | 6 |
| collection-v2-dev | 2 | 2 |
| collection-v2-test | 9 | 9 |
| collection-v2-train | 27 | 27 |

### input_splits

Counted from: `ledger.sqlite` binding/observations.

| parent | split | rows |
| --- | --- | --- |
| accepted-calibration-888 | train | 40 |
| accepted-calibration-888-mock-shard-1 | train | 10 |
| collect-v3-W1-20261018-0524 | unassigned | 26 |
| collect-v3-W2-20261018-0524 | unassigned | 40 |
| collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 40 |
| collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 6 |
| collection-v2-dev | dev | 2 |
| collection-v2-test | test | 9 |
| collection-v2-train | train | 27 |

### segmentation_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | verdict | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| gate: second complete line | DROP | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| gate: too many whole neighbour words | DROP | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gate: too many whole neighbour words | DROP | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | accepted-calibration-888 | train | ADMIT | 34 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | accepted-calibration-888 | train | DROP | 4 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | accepted-calibration-888-mock-shard-1 | train | ADMIT | 9 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collect-v3-W1-20261018-0524 | unassigned | HOLD | 23 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collect-v3-W2-20261018-0524 | unassigned | HOLD | 31 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 31 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 5 |
| length: Too little OCR output for the text box after height normalisation. | DROP | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| length: Too much OCR output for the text box after height normalisation. | DROP | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| length: Too much OCR output for the text box after height normalisation. | DROP | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | DROP | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | DROP | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |

### segmentation_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

| reason | verdict | disposition | rows |
| --- | --- | --- | --- |
| gate: second complete line | DROP | DROP | 1 |
| gate: too many whole neighbour words | DROP | DROP | 2 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | ADMIT | 43 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | DROP | 4 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | HOLD | 90 |
| length: Too little OCR output for the text box after height normalisation. | DROP | DROP | 1 |
| length: Too much OCR output for the text box after height normalisation. | DROP | DROP | 3 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | DROP | DROP | 4 |

### source

Counted from: `decisions.jsonl` + ledger inventory.

| source | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| anemi_mixed | collection-v2-dev | dev | HOLD | 1 |
| anemi_mixed | collection-v2-train | train | HOLD | 2 |
| anemi_round1 | collection-v2-test | test | HOLD | 1 |
| anemi_round1 | collection-v2-train | train | HOLD | 7 |
| anemi_round2 | collection-v2-test | test | HOLD | 2 |
| anemi_round2 | collection-v2-train | train | HOLD | 7 |
| archive_AA9613308335D0B014B | collection-v2-train | train | HOLD | 1 |
| archive_bub_gb_Cmg6AQAAIAAJ | collection-v2-train | train | HOLD | 1 |
| archive_izvestiianabul25192530bul | collection-v2-train | train | HOLD | 1 |
| bsb_poly1850 | accepted-calibration-888 | train | ADMIT | 34 |
| bsb_poly1850 | accepted-calibration-888 | train | DROP | 6 |
| bsb_poly1850 | accepted-calibration-888-mock-shard-1 | train | ADMIT | 9 |
| bsb_poly1850 | accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| bsb_poly1850 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| bsb_poly1850 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 5 |
| elstat | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| elstat | collect-v3-W2-20261018-0524 | unassigned | DROP | 2 |
| elstat | collect-v3-W2-20261018-0524 | unassigned | HOLD | 4 |
| gazette_modern | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| gazette_modern | collect-v3-W1-20261018-0524 | unassigned | HOLD | 8 |
| gazette_modern | collect-v3-W2-20261018-0524 | unassigned | DROP | 7 |
| gazette_modern | collect-v3-W2-20261018-0524 | unassigned | HOLD | 22 |
| gazette_modern | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 7 |
| gazette_modern | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 16 |
| ia_greek_latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 6 |
| ia_poly1850 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 3 |
| ia_poly1850 | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| ia_poly1850 | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 15 |
| ia_poly1850 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 1 |
| ia_russian | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| lekythos | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| lekythos | collect-v3-W1-20261018-0524 | unassigned | HOLD | 3 |
| nlg | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| nlg | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 1 |
| openarchives_Dione | collection-v2-test | test | HOLD | 1 |
| openarchives_kallipos | collection-v2-test | test | HOLD | 1 |
| openarchives_kallipos | collection-v2-train | train | HOLD | 2 |
| parliament_proceedings_1975_2000 | collection-v2-dev | dev | HOLD | 1 |
| parliament_proceedings_1975_2000 | collection-v2-test | test | HOLD | 2 |
| parliament_proceedings_1975_2000 | collection-v2-train | train | HOLD | 5 |
| serbia | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 3 |
| vouli_parliament_1850s | collection-v2-train | train | HOLD | 1 |
| wikisource_el | collection-v2-test | test | HOLD | 1 |
| wikisource_ru | collection-v2-test | test | HOLD | 1 |

### source_class

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| anemi_mixed | greek_poly | collection-v2-train | train | HOLD | 2 |
| anemi_mixed | latin | collection-v2-dev | dev | HOLD | 1 |
| anemi_round1 | greek_poly | collection-v2-test | test | HOLD | 1 |
| anemi_round1 | greek_poly | collection-v2-train | train | HOLD | 7 |
| anemi_round2 | greek_poly | collection-v2-test | test | HOLD | 2 |
| anemi_round2 | greek_poly | collection-v2-train | train | HOLD | 7 |
| archive_AA9613308335D0B014B | cyrillic | collection-v2-train | train | HOLD | 1 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | collection-v2-train | train | HOLD | 1 |
| archive_izvestiianabul25192530bul | latin | collection-v2-train | train | HOLD | 1 |
| bsb_poly1850 | cyrillic | accepted-calibration-888-mock-shard-1 | train | ADMIT | 7 |
| bsb_poly1850 | headings_caps | accepted-calibration-888 | train | ADMIT | 1 |
| bsb_poly1850 | latin | accepted-calibration-888 | train | ADMIT | 9 |
| bsb_poly1850 | latin | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| bsb_poly1850 | mixed_greek_latin | accepted-calibration-888 | train | ADMIT | 7 |
| bsb_poly1850 | mixed_greek_latin | accepted-calibration-888 | train | DROP | 4 |
| bsb_poly1850 | mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| bsb_poly1850 | modern_scanned | accepted-calibration-888 | train | ADMIT | 5 |
| bsb_poly1850 | modern_scanned | accepted-calibration-888 | train | DROP | 2 |
| bsb_poly1850 | nonletter | accepted-calibration-888-mock-shard-1 | train | DROP | 1 |
| bsb_poly1850 | numerics_tables | accepted-calibration-888 | train | ADMIT | 11 |
| bsb_poly1850 | poly1850 | accepted-calibration-888 | train | ADMIT | 1 |
| bsb_poly1850 | poly1850 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| bsb_poly1850 | poly1900 | accepted-calibration-888-mock-shard-1 | train | ADMIT | 2 |
| elstat | latin | collect-v3-W2-20261018-0524 | unassigned | DROP | 2 |
| elstat | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| elstat | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| elstat | poly1900 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| gazette_modern | cyrillic | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | dialogue_fiction | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| gazette_modern | dialogue_fiction | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| gazette_modern | headings_caps | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | headings_caps | collect-v3-W2-20261018-0524 | unassigned | HOLD | 6 |
| gazette_modern | headings_caps | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 2 |
| gazette_modern | headings_caps | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 5 |
| gazette_modern | latin | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | modern_scanned | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | modern_scanned | collect-v3-W1-20261018-0524 | unassigned | HOLD | 4 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524 | unassigned | HOLD | 7 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 3 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 10 |
| gazette_modern | nonletter | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | nonletter | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| gazette_modern | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | HOLD | 3 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | HOLD | 5 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 1 |
| gazette_modern | poly1900 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| ia_greek_latin | latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 5 |
| ia_greek_latin | mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| ia_poly1850 | latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 2 |
| ia_poly1850 | latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| ia_poly1850 | latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 7 |
| ia_poly1850 | mixed_greek_latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | DROP | 1 |
| ia_poly1850 | mixed_greek_latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 1 |
| ia_poly1850 | numerics_tables | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 1 |
| ia_poly1850 | poly1850 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| ia_poly1850 | poly1850 | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | HOLD | 6 |
| ia_poly1850 | poly1850 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 1 |
| ia_russian | cyrillic | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| lekythos | nonletter | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| lekythos | poly1900 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 3 |
| nlg | nonletter | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | DROP | 1 |
| nlg | poly1900 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 1 |
| openarchives_Dione | greek_mono | collection-v2-test | test | HOLD | 1 |
| openarchives_kallipos | greek_latin_cs | collection-v2-train | train | HOLD | 1 |
| openarchives_kallipos | greek_mono | collection-v2-test | test | HOLD | 1 |
| openarchives_kallipos | greek_mono | collection-v2-train | train | HOLD | 1 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-dev | dev | HOLD | 1 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-test | test | HOLD | 1 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-train | train | HOLD | 4 |
| parliament_proceedings_1975_2000 | greek_poly | collection-v2-test | test | HOLD | 1 |
| parliament_proceedings_1975_2000 | greek_poly | collection-v2-train | train | HOLD | 1 |
| serbia | cyrillic | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | HOLD | 3 |
| vouli_parliament_1850s | greek_poly | collection-v2-train | train | HOLD | 1 |
| wikisource_el | greek_poly | collection-v2-test | test | HOLD | 1 |
| wikisource_ru | cyrillic | collection-v2-test | test | HOLD | 1 |

### source_class_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- | --- |
| anemi_mixed | greek_poly | collection-v2-train | train | 2 | 0 | 0.0 |
| anemi_mixed | latin | collection-v2-dev | dev | 1 | 0 | 0.0 |
| anemi_round1 | greek_poly | collection-v2-test | test | 1 | 0 | 0.0 |
| anemi_round1 | greek_poly | collection-v2-train | train | 7 | 0 | 0.0 |
| anemi_round2 | greek_poly | collection-v2-test | test | 2 | 0 | 0.0 |
| anemi_round2 | greek_poly | collection-v2-train | train | 7 | 0 | 0.0 |
| archive_AA9613308335D0B014B | cyrillic | collection-v2-train | train | 1 | 0 | 0.0 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | collection-v2-train | train | 1 | 0 | 0.0 |
| archive_izvestiianabul25192530bul | latin | collection-v2-train | train | 1 | 0 | 0.0 |
| bsb_poly1850 | cyrillic | accepted-calibration-888-mock-shard-1 | train | 7 | 7 | 1.0 |
| bsb_poly1850 | headings_caps | accepted-calibration-888 | train | 1 | 1 | 1.0 |
| bsb_poly1850 | latin | accepted-calibration-888 | train | 9 | 9 | 1.0 |
| bsb_poly1850 | latin | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| bsb_poly1850 | mixed_greek_latin | accepted-calibration-888 | train | 11 | 7 | 0.6363636363636364 |
| bsb_poly1850 | mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| bsb_poly1850 | modern_scanned | accepted-calibration-888 | train | 7 | 5 | 0.7142857142857143 |
| bsb_poly1850 | nonletter | accepted-calibration-888-mock-shard-1 | train | 1 | 0 | 0.0 |
| bsb_poly1850 | numerics_tables | accepted-calibration-888 | train | 11 | 11 | 1.0 |
| bsb_poly1850 | poly1850 | accepted-calibration-888 | train | 1 | 1 | 1.0 |
| bsb_poly1850 | poly1850 | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| bsb_poly1850 | poly1900 | accepted-calibration-888-mock-shard-1 | train | 2 | 2 | 1.0 |
| elstat | latin | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| elstat | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| elstat | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| elstat | poly1900 | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | cyrillic | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | dialogue_fiction | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | dialogue_fiction | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| gazette_modern | headings_caps | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | headings_caps | collect-v3-W2-20261018-0524 | unassigned | 6 | 0 | 0.0 |
| gazette_modern | headings_caps | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 7 | 0 | 0.0 |
| gazette_modern | latin | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | modern_scanned | collect-v3-W1-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524 | unassigned | 8 | 0 | 0.0 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 13 | 0 | 0.0 |
| gazette_modern | nonletter | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | nonletter | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | 8 | 0 | 0.0 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 2 | 0 | 0.0 |
| gazette_modern | poly1900 | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| ia_greek_latin | latin | collect-v3-W1-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| ia_greek_latin | mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| ia_poly1850 | latin | collect-v3-W1-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| ia_poly1850 | latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 8 | 0 | 0.0 |
| ia_poly1850 | mixed_greek_latin | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 2 | 0 | 0.0 |
| ia_poly1850 | numerics_tables | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 1 | 0 | 0.0 |
| ia_poly1850 | poly1850 | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| ia_poly1850 | poly1850 | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 6 | 0 | 0.0 |
| ia_poly1850 | poly1850 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 1 | 0 | 0.0 |
| ia_russian | cyrillic | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| lekythos | nonletter | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| lekythos | poly1900 | collect-v3-W1-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| nlg | nonletter | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 1 | 0 | 0.0 |
| nlg | poly1900 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 1 | 0 | 0.0 |
| openarchives_Dione | greek_mono | collection-v2-test | test | 1 | 0 | 0.0 |
| openarchives_kallipos | greek_latin_cs | collection-v2-train | train | 1 | 0 | 0.0 |
| openarchives_kallipos | greek_mono | collection-v2-test | test | 1 | 0 | 0.0 |
| openarchives_kallipos | greek_mono | collection-v2-train | train | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-dev | dev | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-test | test | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-train | train | 4 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_poly | collection-v2-test | test | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_poly | collection-v2-train | train | 1 | 0 | 0.0 |
| serbia | cyrillic | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 3 | 0 | 0.0 |
| vouli_parliament_1850s | greek_poly | collection-v2-train | train | 1 | 0 | 0.0 |
| wikisource_el | greek_poly | collection-v2-test | test | 1 | 0 | 0.0 |
| wikisource_ru | cyrillic | collection-v2-test | test | 1 | 0 | 0.0 |

### source_class_totals

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | split | disposition | rows |
| --- | --- | --- | --- | --- |
| anemi_mixed | greek_poly | train | HOLD | 2 |
| anemi_mixed | latin | dev | HOLD | 1 |
| anemi_round1 | greek_poly | test | HOLD | 1 |
| anemi_round1 | greek_poly | train | HOLD | 7 |
| anemi_round2 | greek_poly | test | HOLD | 2 |
| anemi_round2 | greek_poly | train | HOLD | 7 |
| archive_AA9613308335D0B014B | cyrillic | train | HOLD | 1 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | train | HOLD | 1 |
| archive_izvestiianabul25192530bul | latin | train | HOLD | 1 |
| bsb_poly1850 | cyrillic | train | ADMIT | 7 |
| bsb_poly1850 | headings_caps | train | ADMIT | 1 |
| bsb_poly1850 | latin | train | ADMIT | 9 |
| bsb_poly1850 | latin | unassigned | HOLD | 2 |
| bsb_poly1850 | mixed_greek_latin | train | ADMIT | 7 |
| bsb_poly1850 | mixed_greek_latin | train | DROP | 4 |
| bsb_poly1850 | mixed_greek_latin | unassigned | HOLD | 1 |
| bsb_poly1850 | modern_scanned | train | ADMIT | 5 |
| bsb_poly1850 | modern_scanned | train | DROP | 2 |
| bsb_poly1850 | nonletter | train | DROP | 1 |
| bsb_poly1850 | numerics_tables | train | ADMIT | 11 |
| bsb_poly1850 | poly1850 | train | ADMIT | 1 |
| bsb_poly1850 | poly1850 | unassigned | HOLD | 3 |
| bsb_poly1850 | poly1900 | train | ADMIT | 2 |
| elstat | latin | unassigned | DROP | 2 |
| elstat | numerics_tables | unassigned | HOLD | 4 |
| elstat | poly1900 | unassigned | HOLD | 1 |
| gazette_modern | cyrillic | unassigned | DROP | 1 |
| gazette_modern | dialogue_fiction | unassigned | HOLD | 3 |
| gazette_modern | headings_caps | unassigned | DROP | 3 |
| gazette_modern | headings_caps | unassigned | HOLD | 11 |
| gazette_modern | latin | unassigned | DROP | 1 |
| gazette_modern | modern_scanned | unassigned | DROP | 5 |
| gazette_modern | modern_scanned | unassigned | HOLD | 21 |
| gazette_modern | nonletter | unassigned | DROP | 2 |
| gazette_modern | numerics_tables | unassigned | DROP | 4 |
| gazette_modern | numerics_tables | unassigned | HOLD | 9 |
| gazette_modern | poly1900 | unassigned | HOLD | 2 |
| ia_greek_latin | latin | unassigned | HOLD | 5 |
| ia_greek_latin | mixed_greek_latin | unassigned | HOLD | 1 |
| ia_poly1850 | latin | unassigned | DROP | 1 |
| ia_poly1850 | latin | unassigned | HOLD | 9 |
| ia_poly1850 | mixed_greek_latin | unassigned | DROP | 1 |
| ia_poly1850 | mixed_greek_latin | unassigned | HOLD | 1 |
| ia_poly1850 | numerics_tables | unassigned | HOLD | 1 |
| ia_poly1850 | poly1850 | unassigned | HOLD | 8 |
| ia_russian | cyrillic | unassigned | HOLD | 1 |
| lekythos | nonletter | unassigned | DROP | 1 |
| lekythos | poly1900 | unassigned | HOLD | 3 |
| nlg | nonletter | unassigned | DROP | 1 |
| nlg | poly1900 | unassigned | HOLD | 1 |
| openarchives_Dione | greek_mono | test | HOLD | 1 |
| openarchives_kallipos | greek_latin_cs | train | HOLD | 1 |
| openarchives_kallipos | greek_mono | test | HOLD | 1 |
| openarchives_kallipos | greek_mono | train | HOLD | 1 |
| parliament_proceedings_1975_2000 | greek_mono | dev | HOLD | 1 |
| parliament_proceedings_1975_2000 | greek_mono | test | HOLD | 1 |
| parliament_proceedings_1975_2000 | greek_mono | train | HOLD | 4 |
| parliament_proceedings_1975_2000 | greek_poly | test | HOLD | 1 |
| parliament_proceedings_1975_2000 | greek_poly | train | HOLD | 1 |
| serbia | cyrillic | unassigned | HOLD | 3 |
| vouli_parliament_1850s | greek_poly | train | HOLD | 1 |
| wikisource_el | greek_poly | test | HOLD | 1 |
| wikisource_ru | cyrillic | test | HOLD | 1 |

### source_class_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| anemi_mixed | greek_poly | train | 2 | 0 | 0.0 |
| anemi_mixed | latin | dev | 1 | 0 | 0.0 |
| anemi_round1 | greek_poly | test | 1 | 0 | 0.0 |
| anemi_round1 | greek_poly | train | 7 | 0 | 0.0 |
| anemi_round2 | greek_poly | test | 2 | 0 | 0.0 |
| anemi_round2 | greek_poly | train | 7 | 0 | 0.0 |
| archive_AA9613308335D0B014B | cyrillic | train | 1 | 0 | 0.0 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | train | 1 | 0 | 0.0 |
| archive_izvestiianabul25192530bul | latin | train | 1 | 0 | 0.0 |
| bsb_poly1850 | cyrillic | train | 7 | 7 | 1.0 |
| bsb_poly1850 | headings_caps | train | 1 | 1 | 1.0 |
| bsb_poly1850 | latin | train | 9 | 9 | 1.0 |
| bsb_poly1850 | latin | unassigned | 2 | 0 | 0.0 |
| bsb_poly1850 | mixed_greek_latin | train | 11 | 7 | 0.6363636363636364 |
| bsb_poly1850 | mixed_greek_latin | unassigned | 1 | 0 | 0.0 |
| bsb_poly1850 | modern_scanned | train | 7 | 5 | 0.7142857142857143 |
| bsb_poly1850 | nonletter | train | 1 | 0 | 0.0 |
| bsb_poly1850 | numerics_tables | train | 11 | 11 | 1.0 |
| bsb_poly1850 | poly1850 | train | 1 | 1 | 1.0 |
| bsb_poly1850 | poly1850 | unassigned | 3 | 0 | 0.0 |
| bsb_poly1850 | poly1900 | train | 2 | 2 | 1.0 |
| elstat | latin | unassigned | 2 | 0 | 0.0 |
| elstat | numerics_tables | unassigned | 4 | 0 | 0.0 |
| elstat | poly1900 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | cyrillic | unassigned | 1 | 0 | 0.0 |
| gazette_modern | dialogue_fiction | unassigned | 3 | 0 | 0.0 |
| gazette_modern | headings_caps | unassigned | 14 | 0 | 0.0 |
| gazette_modern | latin | unassigned | 1 | 0 | 0.0 |
| gazette_modern | modern_scanned | unassigned | 26 | 0 | 0.0 |
| gazette_modern | nonletter | unassigned | 2 | 0 | 0.0 |
| gazette_modern | numerics_tables | unassigned | 13 | 0 | 0.0 |
| gazette_modern | poly1900 | unassigned | 2 | 0 | 0.0 |
| ia_greek_latin | latin | unassigned | 5 | 0 | 0.0 |
| ia_greek_latin | mixed_greek_latin | unassigned | 1 | 0 | 0.0 |
| ia_poly1850 | latin | unassigned | 10 | 0 | 0.0 |
| ia_poly1850 | mixed_greek_latin | unassigned | 2 | 0 | 0.0 |
| ia_poly1850 | numerics_tables | unassigned | 1 | 0 | 0.0 |
| ia_poly1850 | poly1850 | unassigned | 8 | 0 | 0.0 |
| ia_russian | cyrillic | unassigned | 1 | 0 | 0.0 |
| lekythos | nonletter | unassigned | 1 | 0 | 0.0 |
| lekythos | poly1900 | unassigned | 3 | 0 | 0.0 |
| nlg | nonletter | unassigned | 1 | 0 | 0.0 |
| nlg | poly1900 | unassigned | 1 | 0 | 0.0 |
| openarchives_Dione | greek_mono | test | 1 | 0 | 0.0 |
| openarchives_kallipos | greek_latin_cs | train | 1 | 0 | 0.0 |
| openarchives_kallipos | greek_mono | test | 1 | 0 | 0.0 |
| openarchives_kallipos | greek_mono | train | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_mono | dev | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_mono | test | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_mono | train | 4 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_poly | test | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_poly | train | 1 | 0 | 0.0 |
| serbia | cyrillic | unassigned | 3 | 0 | 0.0 |
| vouli_parliament_1850s | greek_poly | train | 1 | 0 | 0.0 |
| wikisource_el | greek_poly | test | 1 | 0 | 0.0 |
| wikisource_ru | cyrillic | test | 1 | 0 | 0.0 |

### source_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| anemi_mixed | collection-v2-dev | dev | 1 | 0 | 0.0 |
| anemi_mixed | collection-v2-train | train | 2 | 0 | 0.0 |
| anemi_round1 | collection-v2-test | test | 1 | 0 | 0.0 |
| anemi_round1 | collection-v2-train | train | 7 | 0 | 0.0 |
| anemi_round2 | collection-v2-test | test | 2 | 0 | 0.0 |
| anemi_round2 | collection-v2-train | train | 7 | 0 | 0.0 |
| archive_AA9613308335D0B014B | collection-v2-train | train | 1 | 0 | 0.0 |
| archive_bub_gb_Cmg6AQAAIAAJ | collection-v2-train | train | 1 | 0 | 0.0 |
| archive_izvestiianabul25192530bul | collection-v2-train | train | 1 | 0 | 0.0 |
| bsb_poly1850 | accepted-calibration-888 | train | 40 | 34 | 0.85 |
| bsb_poly1850 | accepted-calibration-888-mock-shard-1 | train | 10 | 9 | 0.9 |
| bsb_poly1850 | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| bsb_poly1850 | collect-v3-W2-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| elstat | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| elstat | collect-v3-W2-20261018-0524 | unassigned | 6 | 0 | 0.0 |
| gazette_modern | collect-v3-W1-20261018-0524 | unassigned | 10 | 0 | 0.0 |
| gazette_modern | collect-v3-W2-20261018-0524 | unassigned | 29 | 0 | 0.0 |
| gazette_modern | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 23 | 0 | 0.0 |
| ia_greek_latin | collect-v3-W1-20261018-0524 | unassigned | 6 | 0 | 0.0 |
| ia_poly1850 | collect-v3-W1-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| ia_poly1850 | collect-v3-W2-20261018-0524-mock-shard-1 | unassigned | 17 | 0 | 0.0 |
| ia_poly1850 | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 1 | 0 | 0.0 |
| ia_russian | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| lekythos | collect-v3-W1-20261018-0524 | unassigned | 4 | 0 | 0.0 |
| nlg | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 2 | 0 | 0.0 |
| openarchives_Dione | collection-v2-test | test | 1 | 0 | 0.0 |
| openarchives_kallipos | collection-v2-test | test | 1 | 0 | 0.0 |
| openarchives_kallipos | collection-v2-train | train | 2 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | collection-v2-dev | dev | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | collection-v2-test | test | 2 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | collection-v2-train | train | 5 | 0 | 0.0 |
| serbia | collect-v3-W2-20261018-0524-mock-shard-2 | unassigned | 3 | 0 | 0.0 |
| vouli_parliament_1850s | collection-v2-train | train | 1 | 0 | 0.0 |
| wikisource_el | collection-v2-test | test | 1 | 0 | 0.0 |
| wikisource_ru | collection-v2-test | test | 1 | 0 | 0.0 |

### source_totals

Counted from: `decisions.jsonl` + ledger inventory.

| source | split | disposition | rows |
| --- | --- | --- | --- |
| anemi_mixed | dev | HOLD | 1 |
| anemi_mixed | train | HOLD | 2 |
| anemi_round1 | test | HOLD | 1 |
| anemi_round1 | train | HOLD | 7 |
| anemi_round2 | test | HOLD | 2 |
| anemi_round2 | train | HOLD | 7 |
| archive_AA9613308335D0B014B | train | HOLD | 1 |
| archive_bub_gb_Cmg6AQAAIAAJ | train | HOLD | 1 |
| archive_izvestiianabul25192530bul | train | HOLD | 1 |
| bsb_poly1850 | train | ADMIT | 43 |
| bsb_poly1850 | train | DROP | 7 |
| bsb_poly1850 | unassigned | HOLD | 6 |
| elstat | unassigned | DROP | 2 |
| elstat | unassigned | HOLD | 5 |
| gazette_modern | unassigned | DROP | 16 |
| gazette_modern | unassigned | HOLD | 46 |
| ia_greek_latin | unassigned | HOLD | 6 |
| ia_poly1850 | unassigned | DROP | 2 |
| ia_poly1850 | unassigned | HOLD | 19 |
| ia_russian | unassigned | HOLD | 1 |
| lekythos | unassigned | DROP | 1 |
| lekythos | unassigned | HOLD | 3 |
| nlg | unassigned | DROP | 1 |
| nlg | unassigned | HOLD | 1 |
| openarchives_Dione | test | HOLD | 1 |
| openarchives_kallipos | test | HOLD | 1 |
| openarchives_kallipos | train | HOLD | 2 |
| parliament_proceedings_1975_2000 | dev | HOLD | 1 |
| parliament_proceedings_1975_2000 | test | HOLD | 2 |
| parliament_proceedings_1975_2000 | train | HOLD | 5 |
| serbia | unassigned | HOLD | 3 |
| vouli_parliament_1850s | train | HOLD | 1 |
| wikisource_el | test | HOLD | 1 |
| wikisource_ru | test | HOLD | 1 |

### source_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- |
| anemi_mixed | dev | 1 | 0 | 0.0 |
| anemi_mixed | train | 2 | 0 | 0.0 |
| anemi_round1 | test | 1 | 0 | 0.0 |
| anemi_round1 | train | 7 | 0 | 0.0 |
| anemi_round2 | test | 2 | 0 | 0.0 |
| anemi_round2 | train | 7 | 0 | 0.0 |
| archive_AA9613308335D0B014B | train | 1 | 0 | 0.0 |
| archive_bub_gb_Cmg6AQAAIAAJ | train | 1 | 0 | 0.0 |
| archive_izvestiianabul25192530bul | train | 1 | 0 | 0.0 |
| bsb_poly1850 | train | 50 | 43 | 0.86 |
| bsb_poly1850 | unassigned | 6 | 0 | 0.0 |
| elstat | unassigned | 7 | 0 | 0.0 |
| gazette_modern | unassigned | 62 | 0 | 0.0 |
| ia_greek_latin | unassigned | 6 | 0 | 0.0 |
| ia_poly1850 | unassigned | 21 | 0 | 0.0 |
| ia_russian | unassigned | 1 | 0 | 0.0 |
| lekythos | unassigned | 4 | 0 | 0.0 |
| nlg | unassigned | 2 | 0 | 0.0 |
| openarchives_Dione | test | 1 | 0 | 0.0 |
| openarchives_kallipos | test | 1 | 0 | 0.0 |
| openarchives_kallipos | train | 2 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | dev | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | test | 2 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | train | 5 | 0 | 0.0 |
| serbia | unassigned | 3 | 0 | 0.0 |
| vouli_parliament_1850s | train | 1 | 0 | 0.0 |
| wikisource_el | test | 1 | 0 | 0.0 |
| wikisource_ru | test | 1 | 0 | 0.0 |

### toolchain_versions

Counted from: `decisions.jsonl` + ledger inventory.

| tool | version | rows |
| --- | --- | --- |
| census | 0.7 | 200 |
| composer | 0.3 | 200 |
| content_gate | 0.3 | 200 |
| content_repair | 0.2 | 200 |
| cyrillic | 0.3 | 200 |
| dashes | 0.1 | 200 |
| final_eligibility | 0.3 | 200 |
| inventory | 0.1 | 200 |
| numerics | 0.3 | 200 |
| polytonic | 0.7 | 200 |
| segmentation | 0.13 | 200 |

### Timing

Counted from: readout process wall clock.

| elapsed_seconds |
| --- |
| 0.05180811882019043 |

### Tool version binding

Counted from: `ledger.sqlite` run binding.

| path | sha256 | tools |
| --- | --- | --- |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json | ed81e3a1b7389c3dd4d29706e5e2ff2b6d0d34fa0648a9587388a25be2725831 | {'polytonic': {'version': '0.7', 'documented_iterations': ['S1', 'S2', 'S3', 'S4', 'S5', 'SF6', 'SF7'], 'iteration_count': 7, 'scope': 'SF7 A; existing detector/readers; exact release candidate_pre_audit', 'components': {'greek-ocr-toolkit-spellcheck/scripts/labelfix/release_gate_sf7.py': '2f7a777a91adae1af5238a9f2092c59326fc6cc7d83d6ad3bf115866455ec208'}, 'digest': 'de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5'}, 'cyrillic': {'version': '0.3', 'documented_iterations': ['ru1_v1', 'ru1_v2_train', 'ru1_v3_edits'], 'iteration_count': 3, 'scope': 'historical Russian ь→ъ only', 'components': {'greek-ocr-toolkit-secondary/scripts/secondary/ru1_decide.py': 'cc50121e27e90cb4555e0cb98f8ad091f5a4e00c7a410c553ae9d0c7b373d41a', 'greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v3_edits.jsonl': '4f1a51f5eb80788fb1cdc7a01220c90df028e79711cf0eeec2d0ace2ee42d1d0'}, 'digest': 'f63e1ba8696adb47dfc07b283c615fe83deb3f1d2fd28acbf0300de495235123'}, 'numerics': {'version': '0.3', 'documented_iterations': ['N1 automatic ink candidate (rejected 0/5)', 'N1 assisted two-reader and lead-pixel release', 'census_03 integration: digit/separator/digit adjacency for automatic candidate negatives'], 'iteration_count': 3, 'scope': 'assisted separator corrections; failed automatic candidate is disabled', 'components': {'greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_w1.jsonl': '94fb67c1aab9f2ec3bf5d47bc36508b7e700508cd27391f70ebfc26f8d73230e', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68'}, 'digest': 'f1b5c0aa990b76dac5f757af9fdf16bc0374dc3fc1dd98f64979c021b5bed2b9'}, 'dashes': {'version': '0.1', 'documented_iterations': ['dash tags; no general repair release'], 'iteration_count': 1, 'scope': 'tag only', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68'}, 'digest': 'a3c42b877f00e3798909213e43ef5f2f0682571b1fa04a33b284aa198ebef2fb'}, 'segmentation': {'version': '0.13', 'documented_iterations': ['29fa466 crop guides', '5d664bf font normalized', 'cad8709 target-box normalization', 'b2f8d95 whole-word tolerance', '405d4f1 padding 1.5 heights', '0.5 + row-frame text box', 'crop-only line inventory and cut-off gate before length', "owner's three rules; remove target-cut veto and taller-than-upright guard", 'every letter body >=95% visible for a whole neighbour word', 'every h > w crop turns 90 degrees right before all detection and measurement', 'main-row ink measured along its existing base curve', 'small segments use every ink component in the processed crop frame', "length band 0.30–2.00 (coordinator decision under the owner's end-to-end mandate, 19 Oct 21:34; fitted on owner marks, s5)"], 'iteration_count': 13, 'scope': '0.9-s5: one length band 0.30–2.00 for all rows; S4 measurement, small path, mode 2, padding 1.5 and gate unchanged', 'components': {'greek-ocr-toolkit-pipe032/greekocr/glyphs/components.py': 'ffe88b72ae758f49610a0ea0d14b799c147821a899a30abdfb61cf8734be7831', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_native.py': 'e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/segmentation-policy.js': '5888fe704e6170b51081d6fa4200a725d2b29f0c70301f238faf7b32088b5b99', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/crop-tools.py': '0adb60b62bebdb910dfa8cbba56eb64ae0325fe8f14290b4c72dbea866913b97', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/font-models.json': 'fb3f28f7d90c2b638bfe9c72ab42dcf060d59939a7ab410fc2e1cf6d898965de', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/service.mjs': '8a222c1c50550f9ade8250fc3de1e2972e56dae0ce3e6ab915caa0052161b32f', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py': '1dd618bc2d884cf2490498456653f49b0276944f3bde83d38e26e633031eb641', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py': '038bd46af4535e6de6af58e11c4b7496e03e0434094cc8cd6b48668e2199ad77'}, 'digest': '86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6', 'label': '0.9-s5'}, 'content_gate': {'version': '0.3', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'owner gate: mixed-script word drops, unexpected script holds, before segmentation; short ordinary lines excluded before segmentation (letters); cells and numeric lines exempt with more than one letter-or-digit'], 'iteration_count': 3, 'scope': 'existing toolkit primitives with new orchestration', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8'}, 'digest': '244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20'}, 'content_repair': {'version': '0.2', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports'], 'iteration_count': 2, 'scope': 'evidence-backed external repair interface; missing evidence holds', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8'}, 'digest': '244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20'}, 'composer': {'version': '0.3', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'PIPE032: declared routes_out_of_scope bypass correction lookup and automatic results; retain explicit non-success route evidence'], 'iteration_count': 3, 'scope': 'existing toolkit primitives with new orchestration', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8'}, 'digest': '244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20'}, 'final_eligibility': {'version': '0.3', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'cells: alnum > 1 is the only length/shape check, consistent with the gate'], 'iteration_count': 3, 'scope': 'existing toolkit primitives with new orchestration', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8'}, 'digest': '244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20'}, 'census': {'version': '0.7', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'bounded parallel native workers for CSCS', 'profiled CSCS throughput tuning with bounded queue lookahead and node-scale worker qualification', 'parent-confirmed collection-v2 legacy evaluation split aliases with retained lineage', 'census_03 integration: union configured heldout_crop_sha256 with observed held-out crops', 'PIPE032: bind release correction scope; export corrections_not_applied and count routed rows by tool and disposition'], 'iteration_count': 7, 'scope': 'existing toolkit primitives with new orchestration', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_sources.py': 'd84f024f755d23543bd0b0601f14e2e7adae5d1eaadbc325e636bff3d628788e', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_parallel.py': '52aef74eb01e17669dc068c8532c7008c251e8d1b5308f8e38790c613db0197e', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_native.py': 'e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_runtime.py': '8687f59c0986eff6a3f008c890385724a880c0e6356d6e059d61ec192386d483', 'greek-ocr-toolkit-pipe032/greekocr/harvest/geometry_observations.py': 'ba3ff4c9a6777f4c1c587eaf7ee1770d73ad0b5088d0ff3e333f09671f012570', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/worker.py': '8c8109606e50bf6b26f74d95436e555bc3bac0984ed5c584600fa2602b2ea5c7', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/bootstrap.py': '7ec4b9ddb4a7ad87631992f834ab9a0f52ce6a42e2f6226103ad9a839695dc18', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/filter_crop_paths.py': '04247e96e82db502c7da154f70360f8f4a17b2a9620bb26df9d8bca781ae7110', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/filter_worker.sbatch': '3b30cf18b1d72207000d0532afed44cfa9961982dc84dbd950d66de2b716153c', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/package.py': 'cd4b9d0ae23e405ed61c81abb1a37029ce43abf456390abd2167df5b9b613da5'}, 'digest': '03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3'}, 'inventory': {'version': '0.1', 'documented_iterations': ['first integrated graph implementation'], 'iteration_count': 1, 'scope': 'existing toolkit inventory primitives', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68'}, 'digest': 'a3c42b877f00e3798909213e43ef5f2f0682571b1fa04a33b284aa198ebef2fb'}} |

### Diagnostics (first 20 in file order)

Counted from: `decisions.jsonl`, `admitted_train.jsonl`, ledger inventory.

| issue | count | first20 |
| --- | --- | --- |
| admitted_train_equals_eligible | 0 | [] |
| admitted_train_violations | 0 | [] |
| duplicates | 0 | [] |
| gate_route_violations | 0 | [] |
| gate_segmentation_violations | 0 | [] |
| heldout_leaks | 0 | [] |
| missing_rows | 0 | [] |
| no_reason | 0 | [] |
| pipeline_version_mismatch | 0 | [] |
| unexpected_rows | 0 | [] |

### File provenance

Counted from: files named below (streamed SHA256).

| path | bytes | sha256 |
| --- | --- | --- |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/CURRENT.json | 486 | a2cc7f0a2c4e54deb2af075069957161da6697882e4a1effc54d9c3b418574d9 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/admission_records.jsonl | 2548483 | cf193f78979b8fceff649af636d4c819d089f179b4c9d42b6ad2c04930f9022f |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/admitted_train.jsonl | 611379 | 38096291c7b8771d9fc2195d3ee17ec7a50e9cd0f5e980eaf19e2b56a55503a3 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/decisions.jsonl | 2462935 | 32f707877c38d5ad7984abc2b0bb47e1ec8d9717f0d4f5f5c5aa7f259f5261b3 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/evaluation_diagnostics.jsonl | 2388910 | bab8534097cfb7e9d7dd3cc2074c0db2a2d7df57d7de9a007ee497282bd2dcb7 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/pending_content_repair.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/pending_cyrillic.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/pending_numerics.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/pending_polytonic.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/generations/g1-52d8f5f69ade46e68ef88936f7c87292/summary.json | 16848 | 1d112d42fa9d9964f4bdf452c928a11bdcf1280e6bf9d1b5c295ddf9c7c149f3 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/mock_batch/W/census_05_20261020/attempts/smoke-mode-i/ledger.sqlite | 6434816 | 4a981a7f3890e70440d0ba382ea5df318bc9f3d0469dea10f3eecb491461da98 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json | 12601 | ed81e3a1b7389c3dd4d29706e5e2ff2b6d0d34fa0648a9587388a25be2725831 |

No baseline supplied; no historical delta inferred. The handoff records 65,900 admissions.

CENSUS READOUT: rows 200 (complete yes); ADMIT 43 HOLD 128 DROP 29; admitted_train 43; gate DROP 14 HOLD 38 (mixed 2 foreign 1 short 5 cell1 7 num1 0 unresolved 38); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 15/15 PASS
