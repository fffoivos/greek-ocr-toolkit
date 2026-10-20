200 rows; ADMIT 73 / HOLD 87 / DROP 40; admitted_train 63; gate exclusions 0; invariants PASS (14/14).

Published generation: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde`. Counts use exported dispositions and reasons only. Foreign-script gate reason is `unexpected_script` (the code name). Class is the ledger role, exactly summary.by_stratum.role; script is retained in by_stratum. all_reasons includes distinct reason names/strings from decisions, stages and routes, once per row; all_disposition_reasons contains only final disposition reasons. Held-out protection checks training admissions; dev/test ADMIT rows are evaluation passes. The protected crop list is the writer’s registered dev/test crops; protected editions are policy entries plus registered non-train editions. Root ledger is immutable input provenance, never a verdict source. Only compact identity indexes are retained in memory; JSONL payloads are streamed. Stage attribution uses serialized stages first, then known finish() call sites; missing producers are explicitly labeled. Failure counts in invariants are zero on PASS.

### Totals

Counted from: `decisions.jsonl`.

| disposition | rows |
| --- | --- |
| ADMIT | 73 |
| DROP | 40 |
| HOLD | 87 |

### Disposition reason occurrences

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| codec_unencodable | 1 |
| mixed_script_word | 1 |
| nonletter_fraction | 5 |
| numeric_shape | 3 |
| segmentation | 41 |
| short_line | 3 |
| split_or_edition_identity_unresolved | 74 |
| unexpected_character | 1 |

### Route statuses

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| content_repair:not_applicable | 73 |
| content_repair:not_run_due_to_prior_exclusion | 124 |
| content_repair:verified_no_change | 3 |
| cyrillic:not_applicable | 64 |
| cyrillic:not_run_due_to_prior_exclusion | 121 |
| cyrillic:verified_no_change | 15 |
| dashes:not_applicable | 58 |
| dashes:not_run_due_to_prior_exclusion | 111 |
| dashes:tag_only | 31 |
| numerics:not_applicable | 53 |
| numerics:not_run_due_to_prior_exclusion | 91 |
| numerics:verified_no_change | 56 |
| polytonic:not_applicable | 26 |
| polytonic:not_run_due_to_prior_exclusion | 75 |
| polytonic:verified_no_change | 99 |

### Segmentation availability

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| measured | 200 |

### Gate totals

Counted from: `decisions.jsonl`.

(zero rows)

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
| 0.3 | 200 |

### Admission export

Counted from: `admitted_train.jsonl`.

| rows |
| --- |
| 63 |

### Completeness

Counted from: `decisions.jsonl`, ledger binding.

| rows | input_rows | complete |
| --- | --- | --- |
| 200 | 200 | True |

### Invariants

Counted from: `decisions.jsonl`, `admitted_train.jsonl`, `summary.json`, ledger inventory.

| invariant | status | count |
| --- | --- | --- |
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
| codec_unencodable | collection-v2-train | train | DROP | 1 |
| mixed_script_word | accepted-calibration-888 | train | DROP | 1 |
| nonletter_fraction | accepted-calibration-888 | train | DROP | 5 |
| numeric_shape | accepted-calibration-888 | train | DROP | 3 |
| segmentation | accepted-calibration-888 | train | HOLD | 2 |
| segmentation | collect-v3-W1-20261018-0524 | unassigned | DROP | 6 |
| segmentation | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| segmentation | collect-v3-W2-20261018-0524 | unassigned | DROP | 21 |
| segmentation | collect-v3-W2-20261018-0524 | unassigned | HOLD | 10 |
| segmentation | collection-v2-test | test | DROP | 1 |
| short_line | accepted-calibration-888 | train | DROP | 3 |
| split_or_edition_identity_unresolved | collect-v3-W1-20261018-0524 | unassigned | HOLD | 19 |
| split_or_edition_identity_unresolved | collect-v3-W2-20261018-0524 | unassigned | HOLD | 55 |
| unexpected_character | collection-v2-train | train | DROP | 1 |

### all_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| codec_unencodable | collection-v2-train | train | DROP | 1 |
| gate: no main row found | accepted-calibration-888 | train | HOLD | 2 |
| gate: no main row found | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| gate: no main row found | collect-v3-W2-20261018-0524 | unassigned | HOLD | 4 |
| gate: reading direction unresolved | collect-v3-W2-20261018-0524 | unassigned | HOLD | 6 |
| gate: second complete line | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gate: second complete line | collection-v2-test | test | DROP | 1 |
| gate: too many whole neighbour words | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| gate: too many whole neighbour words | collect-v3-W2-20261018-0524 | unassigned | DROP | 2 |
| length: OCR length matches; vertical padding is within the selected allowance. | accepted-calibration-888 | train | ADMIT | 37 |
| length: OCR length matches; vertical padding is within the selected allowance. | accepted-calibration-888 | train | DROP | 11 |
| length: OCR length matches; vertical padding is within the selected allowance. | collect-v3-W1-20261018-0524 | unassigned | HOLD | 19 |
| length: OCR length matches; vertical padding is within the selected allowance. | collect-v3-W2-20261018-0524 | unassigned | HOLD | 55 |
| length: OCR length matches; vertical padding is within the selected allowance. | collection-v2-dev | dev | ADMIT | 2 |
| length: OCR length matches; vertical padding is within the selected allowance. | collection-v2-test | test | ADMIT | 8 |
| length: OCR length matches; vertical padding is within the selected allowance. | collection-v2-train | train | ADMIT | 26 |
| length: OCR length matches; vertical padding is within the selected allowance. | collection-v2-train | train | DROP | 1 |
| length: Too little OCR output for the text box after height normalisation. | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| length: Too little OCR output for the text box after height normalisation. | collect-v3-W2-20261018-0524 | unassigned | DROP | 5 |
| length: Too much OCR output for the text box after height normalisation. | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| length: Too much OCR output for the text box after height normalisation. | collect-v3-W2-20261018-0524 | unassigned | DROP | 10 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| mixed_script_word | accepted-calibration-888 | train | DROP | 1 |
| mixed_script_word | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| nonletter_fraction | accepted-calibration-888 | train | DROP | 5 |
| numeric_shape | accepted-calibration-888 | train | DROP | 3 |
| segmentation | accepted-calibration-888 | train | HOLD | 2 |
| segmentation | collect-v3-W1-20261018-0524 | unassigned | DROP | 6 |
| segmentation | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| segmentation | collect-v3-W2-20261018-0524 | unassigned | DROP | 21 |
| segmentation | collect-v3-W2-20261018-0524 | unassigned | HOLD | 10 |
| segmentation | collection-v2-test | test | DROP | 1 |
| short_line | accepted-calibration-888 | train | DROP | 3 |
| split_or_edition_identity_unresolved | collect-v3-W1-20261018-0524 | unassigned | HOLD | 19 |
| split_or_edition_identity_unresolved | collect-v3-W2-20261018-0524 | unassigned | HOLD | 55 |
| unexpected_character | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| unexpected_character | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| unexpected_character | collection-v2-train | train | DROP | 1 |
| unexpected_script | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |

### all_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

| reason | disposition | rows |
| --- | --- | --- |
| codec_unencodable | DROP | 1 |
| gate: no main row found | HOLD | 7 |
| gate: reading direction unresolved | HOLD | 6 |
| gate: second complete line | DROP | 2 |
| gate: too many whole neighbour words | DROP | 4 |
| length: OCR length matches; vertical padding is within the selected allowance. | ADMIT | 73 |
| length: OCR length matches; vertical padding is within the selected allowance. | DROP | 12 |
| length: OCR length matches; vertical padding is within the selected allowance. | HOLD | 74 |
| length: Too little OCR output for the text box after height normalisation. | DROP | 7 |
| length: Too much OCR output for the text box after height normalisation. | DROP | 12 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | DROP | 3 |
| mixed_script_word | DROP | 2 |
| nonletter_fraction | DROP | 5 |
| numeric_shape | DROP | 3 |
| segmentation | DROP | 28 |
| segmentation | HOLD | 13 |
| short_line | DROP | 3 |
| split_or_edition_identity_unresolved | HOLD | 74 |
| unexpected_character | DROP | 2 |
| unexpected_character | HOLD | 1 |
| unexpected_script | DROP | 1 |

### by_stratum

Counted from: `decisions.jsonl` + ledger inventory.

| parent | split | source | role | script | disposition | rows |
| --- | --- | --- | --- | --- | --- | --- |
| accepted-calibration-888 | train | bsb_poly1850 | cyrillic | cyrillic | ADMIT | 6 |
| accepted-calibration-888 | train | bsb_poly1850 | cyrillic | cyrillic | DROP | 1 |
| accepted-calibration-888 | train | bsb_poly1850 | headings_caps | greek_mono | ADMIT | 1 |
| accepted-calibration-888 | train | bsb_poly1850 | latin | latin | ADMIT | 9 |
| accepted-calibration-888 | train | bsb_poly1850 | mixed_greek_latin | greek_latin_cs | ADMIT | 5 |
| accepted-calibration-888 | train | bsb_poly1850 | mixed_greek_latin | greek_latin_cs | DROP | 2 |
| accepted-calibration-888 | train | bsb_poly1850 | mixed_greek_latin | latin | ADMIT | 2 |
| accepted-calibration-888 | train | bsb_poly1850 | mixed_greek_latin | latin | DROP | 2 |
| accepted-calibration-888 | train | bsb_poly1850 | modern_scanned | greek_mono | ADMIT | 4 |
| accepted-calibration-888 | train | bsb_poly1850 | modern_scanned | greek_mono | DROP | 3 |
| accepted-calibration-888 | train | bsb_poly1850 | nonletter | nonletter | HOLD | 1 |
| accepted-calibration-888 | train | bsb_poly1850 | numerics_tables | nonletter | ADMIT | 7 |
| accepted-calibration-888 | train | bsb_poly1850 | numerics_tables | nonletter | DROP | 3 |
| accepted-calibration-888 | train | bsb_poly1850 | numerics_tables | nonletter | HOLD | 1 |
| accepted-calibration-888 | train | bsb_poly1850 | poly1850 | greek_poly | ADMIT | 1 |
| accepted-calibration-888 | train | bsb_poly1850 | poly1900 | greek_poly | ADMIT | 2 |
| collect-v3-W1-20261018-0524 | unassigned | bsb_poly1850 | mixed_greek_latin | latin | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | elstat | numerics_tables | nonletter | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | dialogue_fiction | greek_mono | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | headings_caps | greek_mono | DROP | 1 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | modern_scanned | greek_mono | DROP | 1 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | modern_scanned | greek_mono | HOLD | 4 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | numerics_tables | nonletter | DROP | 2 |
| collect-v3-W1-20261018-0524 | unassigned | gazette_modern | numerics_tables | nonletter | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | ia_greek_latin | latin | latin | HOLD | 5 |
| collect-v3-W1-20261018-0524 | unassigned | ia_greek_latin | mixed_greek_latin | latin | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | ia_poly1850 | latin | latin | DROP | 1 |
| collect-v3-W1-20261018-0524 | unassigned | ia_poly1850 | latin | latin | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | ia_poly1850 | poly1850 | greek_poly | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | ia_russian | cyrillic | cyrillic | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | lekythos | nonletter | nonletter | HOLD | 1 |
| collect-v3-W1-20261018-0524 | unassigned | lekythos | poly1900 | greek_poly | DROP | 1 |
| collect-v3-W1-20261018-0524 | unassigned | lekythos | poly1900 | greek_poly | HOLD | 2 |
| collect-v3-W2-20261018-0524 | unassigned | bsb_poly1850 | latin | latin | HOLD | 2 |
| collect-v3-W2-20261018-0524 | unassigned | bsb_poly1850 | poly1850 | greek_poly | HOLD | 3 |
| collect-v3-W2-20261018-0524 | unassigned | elstat | latin | latin | DROP | 1 |
| collect-v3-W2-20261018-0524 | unassigned | elstat | latin | latin | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | elstat | numerics_tables | nonletter | DROP | 2 |
| collect-v3-W2-20261018-0524 | unassigned | elstat | numerics_tables | nonletter | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | elstat | poly1900 | greek_poly | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | cyrillic | cyrillic | DROP | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | dialogue_fiction | greek_mono | HOLD | 2 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | headings_caps | greek_mono | DROP | 5 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | headings_caps | greek_mono | HOLD | 8 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | latin | latin | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | modern_scanned | greek_mono | DROP | 6 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | modern_scanned | greek_mono | HOLD | 15 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | nonletter | nonletter | DROP | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | nonletter | nonletter | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | numerics_tables | greek_mono | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | numerics_tables | nonletter | DROP | 2 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | numerics_tables | nonletter | HOLD | 7 |
| collect-v3-W2-20261018-0524 | unassigned | gazette_modern | poly1900 | greek_poly | HOLD | 2 |
| collect-v3-W2-20261018-0524 | unassigned | ia_poly1850 | latin | latin | HOLD | 8 |
| collect-v3-W2-20261018-0524 | unassigned | ia_poly1850 | mixed_greek_latin | greek_latin_cs | DROP | 2 |
| collect-v3-W2-20261018-0524 | unassigned | ia_poly1850 | numerics_tables | nonletter | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | ia_poly1850 | poly1850 | greek_poly | DROP | 1 |
| collect-v3-W2-20261018-0524 | unassigned | ia_poly1850 | poly1850 | greek_poly | HOLD | 6 |
| collect-v3-W2-20261018-0524 | unassigned | nlg | nonletter | nonletter | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | nlg | poly1900 | greek_poly | HOLD | 1 |
| collect-v3-W2-20261018-0524 | unassigned | serbia | cyrillic | cyrillic | HOLD | 3 |
| collection-v2-dev | dev | anemi_mixed | latin | latin | ADMIT | 1 |
| collection-v2-dev | dev | parliament_proceedings_1975_2000 | greek_mono | greek_mono | ADMIT | 1 |
| collection-v2-test | test | anemi_round1 | greek_poly | greek_poly | ADMIT | 1 |
| collection-v2-test | test | anemi_round2 | greek_poly | greek_poly | ADMIT | 2 |
| collection-v2-test | test | openarchives_Dione | greek_mono | greek_mono | ADMIT | 1 |
| collection-v2-test | test | openarchives_kallipos | greek_mono | greek_mono | ADMIT | 1 |
| collection-v2-test | test | parliament_proceedings_1975_2000 | greek_mono | greek_mono | ADMIT | 1 |
| collection-v2-test | test | parliament_proceedings_1975_2000 | greek_poly | greek_poly | DROP | 1 |
| collection-v2-test | test | wikisource_el | greek_poly | greek_poly | ADMIT | 1 |
| collection-v2-test | test | wikisource_ru | cyrillic | cyrillic | ADMIT | 1 |
| collection-v2-train | train | anemi_mixed | greek_poly | greek_poly | ADMIT | 2 |
| collection-v2-train | train | anemi_round1 | greek_poly | greek_poly | ADMIT | 7 |
| collection-v2-train | train | anemi_round2 | greek_poly | greek_poly | ADMIT | 7 |
| collection-v2-train | train | archive_AA9613308335D0B014B | cyrillic | cyrillic | ADMIT | 1 |
| collection-v2-train | train | archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | cyrillic | DROP | 1 |
| collection-v2-train | train | archive_izvestiianabul25192530bul | latin | latin | ADMIT | 1 |
| collection-v2-train | train | openarchives_kallipos | greek_latin_cs | greek_latin_cs | ADMIT | 1 |
| collection-v2-train | train | openarchives_kallipos | greek_mono | greek_mono | ADMIT | 1 |
| collection-v2-train | train | parliament_proceedings_1975_2000 | greek_mono | greek_mono | ADMIT | 4 |
| collection-v2-train | train | parliament_proceedings_1975_2000 | greek_poly | greek_poly | ADMIT | 1 |
| collection-v2-train | train | vouli_parliament_1850s | greek_poly | greek_poly | ADMIT | 1 |

### class

Counted from: `decisions.jsonl` + ledger inventory.

| role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| cyrillic | accepted-calibration-888 | train | ADMIT | 6 |
| cyrillic | accepted-calibration-888 | train | DROP | 1 |
| cyrillic | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| cyrillic | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| cyrillic | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| cyrillic | collection-v2-test | test | ADMIT | 1 |
| cyrillic | collection-v2-train | train | ADMIT | 1 |
| cyrillic | collection-v2-train | train | DROP | 1 |
| dialogue_fiction | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| dialogue_fiction | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| greek_latin_cs | collection-v2-train | train | ADMIT | 1 |
| greek_mono | collection-v2-dev | dev | ADMIT | 1 |
| greek_mono | collection-v2-test | test | ADMIT | 3 |
| greek_mono | collection-v2-train | train | ADMIT | 5 |
| greek_poly | collection-v2-test | test | ADMIT | 4 |
| greek_poly | collection-v2-test | test | DROP | 1 |
| greek_poly | collection-v2-train | train | ADMIT | 18 |
| headings_caps | accepted-calibration-888 | train | ADMIT | 1 |
| headings_caps | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| headings_caps | collect-v3-W2-20261018-0524 | unassigned | DROP | 5 |
| headings_caps | collect-v3-W2-20261018-0524 | unassigned | HOLD | 8 |
| latin | accepted-calibration-888 | train | ADMIT | 9 |
| latin | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 6 |
| latin | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| latin | collect-v3-W2-20261018-0524 | unassigned | HOLD | 12 |
| latin | collection-v2-dev | dev | ADMIT | 1 |
| latin | collection-v2-train | train | ADMIT | 1 |
| mixed_greek_latin | accepted-calibration-888 | train | ADMIT | 7 |
| mixed_greek_latin | accepted-calibration-888 | train | DROP | 4 |
| mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 2 |
| mixed_greek_latin | collect-v3-W2-20261018-0524 | unassigned | DROP | 2 |
| modern_scanned | accepted-calibration-888 | train | ADMIT | 4 |
| modern_scanned | accepted-calibration-888 | train | DROP | 3 |
| modern_scanned | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| modern_scanned | collect-v3-W1-20261018-0524 | unassigned | HOLD | 4 |
| modern_scanned | collect-v3-W2-20261018-0524 | unassigned | DROP | 6 |
| modern_scanned | collect-v3-W2-20261018-0524 | unassigned | HOLD | 15 |
| nonletter | accepted-calibration-888 | train | HOLD | 1 |
| nonletter | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| nonletter | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| nonletter | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| numerics_tables | accepted-calibration-888 | train | ADMIT | 7 |
| numerics_tables | accepted-calibration-888 | train | DROP | 3 |
| numerics_tables | accepted-calibration-888 | train | HOLD | 1 |
| numerics_tables | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| numerics_tables | collect-v3-W1-20261018-0524 | unassigned | HOLD | 2 |
| numerics_tables | collect-v3-W2-20261018-0524 | unassigned | DROP | 4 |
| numerics_tables | collect-v3-W2-20261018-0524 | unassigned | HOLD | 10 |
| poly1850 | accepted-calibration-888 | train | ADMIT | 1 |
| poly1850 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| poly1850 | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| poly1850 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 9 |
| poly1900 | accepted-calibration-888 | train | ADMIT | 2 |
| poly1900 | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| poly1900 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 2 |
| poly1900 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 4 |

### class_rates

Counted from: `decisions.jsonl` + ledger inventory.

| role | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| cyrillic | accepted-calibration-888 | train | 7 | 6 | 0.8571428571428571 |
| cyrillic | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| cyrillic | collect-v3-W2-20261018-0524 | unassigned | 4 | 0 | 0.0 |
| cyrillic | collection-v2-test | test | 1 | 1 | 1.0 |
| cyrillic | collection-v2-train | train | 2 | 1 | 0.5 |
| dialogue_fiction | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| dialogue_fiction | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| greek_latin_cs | collection-v2-train | train | 1 | 1 | 1.0 |
| greek_mono | collection-v2-dev | dev | 1 | 1 | 1.0 |
| greek_mono | collection-v2-test | test | 3 | 3 | 1.0 |
| greek_mono | collection-v2-train | train | 5 | 5 | 1.0 |
| greek_poly | collection-v2-test | test | 5 | 4 | 0.8 |
| greek_poly | collection-v2-train | train | 18 | 18 | 1.0 |
| headings_caps | accepted-calibration-888 | train | 1 | 1 | 1.0 |
| headings_caps | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| headings_caps | collect-v3-W2-20261018-0524 | unassigned | 13 | 0 | 0.0 |
| latin | accepted-calibration-888 | train | 9 | 9 | 1.0 |
| latin | collect-v3-W1-20261018-0524 | unassigned | 7 | 0 | 0.0 |
| latin | collect-v3-W2-20261018-0524 | unassigned | 13 | 0 | 0.0 |
| latin | collection-v2-dev | dev | 1 | 1 | 1.0 |
| latin | collection-v2-train | train | 1 | 1 | 1.0 |
| mixed_greek_latin | accepted-calibration-888 | train | 11 | 7 | 0.6363636363636364 |
| mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| mixed_greek_latin | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| modern_scanned | accepted-calibration-888 | train | 7 | 4 | 0.5714285714285714 |
| modern_scanned | collect-v3-W1-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| modern_scanned | collect-v3-W2-20261018-0524 | unassigned | 21 | 0 | 0.0 |
| nonletter | accepted-calibration-888 | train | 1 | 0 | 0.0 |
| nonletter | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| nonletter | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| numerics_tables | accepted-calibration-888 | train | 11 | 7 | 0.6363636363636364 |
| numerics_tables | collect-v3-W1-20261018-0524 | unassigned | 4 | 0 | 0.0 |
| numerics_tables | collect-v3-W2-20261018-0524 | unassigned | 14 | 0 | 0.0 |
| poly1850 | accepted-calibration-888 | train | 1 | 1 | 1.0 |
| poly1850 | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| poly1850 | collect-v3-W2-20261018-0524 | unassigned | 10 | 0 | 0.0 |
| poly1900 | accepted-calibration-888 | train | 2 | 2 | 1.0 |
| poly1900 | collect-v3-W1-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| poly1900 | collect-v3-W2-20261018-0524 | unassigned | 4 | 0 | 0.0 |

### class_totals

Counted from: `decisions.jsonl` + ledger inventory.

| role | split | disposition | rows |
| --- | --- | --- | --- |
| cyrillic | test | ADMIT | 1 |
| cyrillic | train | ADMIT | 7 |
| cyrillic | train | DROP | 2 |
| cyrillic | unassigned | DROP | 1 |
| cyrillic | unassigned | HOLD | 4 |
| dialogue_fiction | unassigned | HOLD | 3 |
| greek_latin_cs | train | ADMIT | 1 |
| greek_mono | dev | ADMIT | 1 |
| greek_mono | test | ADMIT | 3 |
| greek_mono | train | ADMIT | 5 |
| greek_poly | test | ADMIT | 4 |
| greek_poly | test | DROP | 1 |
| greek_poly | train | ADMIT | 18 |
| headings_caps | train | ADMIT | 1 |
| headings_caps | unassigned | DROP | 6 |
| headings_caps | unassigned | HOLD | 8 |
| latin | dev | ADMIT | 1 |
| latin | train | ADMIT | 10 |
| latin | unassigned | DROP | 2 |
| latin | unassigned | HOLD | 18 |
| mixed_greek_latin | train | ADMIT | 7 |
| mixed_greek_latin | train | DROP | 4 |
| mixed_greek_latin | unassigned | DROP | 2 |
| mixed_greek_latin | unassigned | HOLD | 2 |
| modern_scanned | train | ADMIT | 4 |
| modern_scanned | train | DROP | 3 |
| modern_scanned | unassigned | DROP | 7 |
| modern_scanned | unassigned | HOLD | 19 |
| nonletter | train | HOLD | 1 |
| nonletter | unassigned | DROP | 1 |
| nonletter | unassigned | HOLD | 3 |
| numerics_tables | train | ADMIT | 7 |
| numerics_tables | train | DROP | 3 |
| numerics_tables | train | HOLD | 1 |
| numerics_tables | unassigned | DROP | 6 |
| numerics_tables | unassigned | HOLD | 12 |
| poly1850 | train | ADMIT | 1 |
| poly1850 | unassigned | DROP | 1 |
| poly1850 | unassigned | HOLD | 10 |
| poly1900 | train | ADMIT | 2 |
| poly1900 | unassigned | DROP | 1 |
| poly1900 | unassigned | HOLD | 6 |

### class_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| role | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- |
| cyrillic | test | 1 | 1 | 1.0 |
| cyrillic | train | 9 | 7 | 0.7777777777777778 |
| cyrillic | unassigned | 5 | 0 | 0.0 |
| dialogue_fiction | unassigned | 3 | 0 | 0.0 |
| greek_latin_cs | train | 1 | 1 | 1.0 |
| greek_mono | dev | 1 | 1 | 1.0 |
| greek_mono | test | 3 | 3 | 1.0 |
| greek_mono | train | 5 | 5 | 1.0 |
| greek_poly | test | 5 | 4 | 0.8 |
| greek_poly | train | 18 | 18 | 1.0 |
| headings_caps | train | 1 | 1 | 1.0 |
| headings_caps | unassigned | 14 | 0 | 0.0 |
| latin | dev | 1 | 1 | 1.0 |
| latin | train | 10 | 10 | 1.0 |
| latin | unassigned | 20 | 0 | 0.0 |
| mixed_greek_latin | train | 11 | 7 | 0.6363636363636364 |
| mixed_greek_latin | unassigned | 4 | 0 | 0.0 |
| modern_scanned | train | 7 | 4 | 0.5714285714285714 |
| modern_scanned | unassigned | 26 | 0 | 0.0 |
| nonletter | train | 1 | 0 | 0.0 |
| nonletter | unassigned | 4 | 0 | 0.0 |
| numerics_tables | train | 11 | 7 | 0.6363636363636364 |
| numerics_tables | unassigned | 18 | 0 | 0.0 |
| poly1850 | train | 1 | 1 | 1.0 |
| poly1850 | unassigned | 11 | 0 | 0.0 |
| poly1900 | train | 2 | 2 | 1.0 |
| poly1900 | unassigned | 7 | 0 | 0.0 |

### deciding_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | stage | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| mixed_script_word | final_eligibility | accepted-calibration-888 | train | DROP | 1 |
| nonletter_fraction | final_eligibility | accepted-calibration-888 | train | DROP | 4 |
| numeric_shape | final_eligibility | accepted-calibration-888 | train | DROP | 3 |
| segmentation | segmentation | accepted-calibration-888 | train | HOLD | 2 |
| segmentation | segmentation | collect-v3-W1-20261018-0524 | unassigned | DROP | 6 |
| segmentation | segmentation | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| segmentation | segmentation | collect-v3-W2-20261018-0524 | unassigned | DROP | 21 |
| segmentation | segmentation | collect-v3-W2-20261018-0524 | unassigned | HOLD | 10 |
| segmentation | segmentation | collection-v2-test | test | DROP | 1 |
| short_line | final_eligibility | accepted-calibration-888 | train | DROP | 3 |
| split_or_edition_identity_unresolved | split_admission | collect-v3-W1-20261018-0524 | unassigned | HOLD | 19 |
| split_or_edition_identity_unresolved | split_admission | collect-v3-W2-20261018-0524 | unassigned | HOLD | 55 |
| unexpected_character | final_eligibility | collection-v2-train | train | DROP | 1 |

### deciding_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

| reason | stage | disposition | rows |
| --- | --- | --- | --- |
| mixed_script_word | final_eligibility | DROP | 1 |
| nonletter_fraction | final_eligibility | DROP | 4 |
| numeric_shape | final_eligibility | DROP | 3 |
| segmentation | segmentation | DROP | 28 |
| segmentation | segmentation | HOLD | 13 |
| short_line | final_eligibility | DROP | 3 |
| split_or_edition_identity_unresolved | split_admission | HOLD | 74 |
| unexpected_character | final_eligibility | DROP | 1 |

### decisions_by_parent_split

Counted from: `decisions.jsonl` + ledger inventory.

| parent | split | disposition | rows |
| --- | --- | --- | --- |
| accepted-calibration-888 | train | ADMIT | 37 |
| accepted-calibration-888 | train | DROP | 11 |
| accepted-calibration-888 | train | HOLD | 2 |
| collect-v3-W1-20261018-0524 | unassigned | DROP | 6 |
| collect-v3-W1-20261018-0524 | unassigned | HOLD | 20 |
| collect-v3-W2-20261018-0524 | unassigned | DROP | 21 |
| collect-v3-W2-20261018-0524 | unassigned | HOLD | 65 |
| collection-v2-dev | dev | ADMIT | 2 |
| collection-v2-test | test | ADMIT | 8 |
| collection-v2-test | test | DROP | 1 |
| collection-v2-train | train | ADMIT | 26 |
| collection-v2-train | train | DROP | 1 |

### gate_by_class

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### gate_by_parent

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### gate_by_source

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### input_rows

Counted from: `ledger.sqlite` binding/observations.

| parent | rows | registered |
| --- | --- | --- |
| accepted-calibration-888 | 50 | 50 |
| collect-v3-W1-20261018-0524 | 26 | 26 |
| collect-v3-W2-20261018-0524 | 86 | 86 |
| collection-v2-dev | 2 | 2 |
| collection-v2-test | 9 | 9 |
| collection-v2-train | 27 | 27 |

### input_splits

Counted from: `ledger.sqlite` binding/observations.

| parent | split | rows |
| --- | --- | --- |
| accepted-calibration-888 | train | 50 |
| collect-v3-W1-20261018-0524 | unassigned | 26 |
| collect-v3-W2-20261018-0524 | unassigned | 86 |
| collection-v2-dev | dev | 2 |
| collection-v2-test | test | 9 |
| collection-v2-train | train | 27 |

### segmentation_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | verdict | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| gate: no main row found | UNCERTAIN | accepted-calibration-888 | train | HOLD | 2 |
| gate: no main row found | UNCERTAIN | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| gate: no main row found | UNCERTAIN | collect-v3-W2-20261018-0524 | unassigned | HOLD | 4 |
| gate: reading direction unresolved | UNCERTAIN | collect-v3-W2-20261018-0524 | unassigned | HOLD | 6 |
| gate: second complete line | DROP | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gate: second complete line | DROP | collection-v2-test | test | DROP | 1 |
| gate: too many whole neighbour words | DROP | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| gate: too many whole neighbour words | DROP | collect-v3-W2-20261018-0524 | unassigned | DROP | 2 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | accepted-calibration-888 | train | ADMIT | 37 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | accepted-calibration-888 | train | DROP | 11 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collect-v3-W1-20261018-0524 | unassigned | HOLD | 19 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collect-v3-W2-20261018-0524 | unassigned | HOLD | 55 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collection-v2-dev | dev | ADMIT | 2 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collection-v2-test | test | ADMIT | 8 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collection-v2-train | train | ADMIT | 26 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | collection-v2-train | train | DROP | 1 |
| length: Too little OCR output for the text box after height normalisation. | DROP | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| length: Too little OCR output for the text box after height normalisation. | DROP | collect-v3-W2-20261018-0524 | unassigned | DROP | 5 |
| length: Too much OCR output for the text box after height normalisation. | DROP | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| length: Too much OCR output for the text box after height normalisation. | DROP | collect-v3-W2-20261018-0524 | unassigned | DROP | 10 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | DROP | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |

### segmentation_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

| reason | verdict | disposition | rows |
| --- | --- | --- | --- |
| gate: no main row found | UNCERTAIN | HOLD | 7 |
| gate: reading direction unresolved | UNCERTAIN | HOLD | 6 |
| gate: second complete line | DROP | DROP | 2 |
| gate: too many whole neighbour words | DROP | DROP | 4 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | ADMIT | 73 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | DROP | 12 |
| length: OCR length matches; vertical padding is within the selected allowance. | KEEP | HOLD | 74 |
| length: Too little OCR output for the text box after height normalisation. | DROP | DROP | 7 |
| length: Too much OCR output for the text box after height normalisation. | DROP | DROP | 12 |
| length: Top and bottom padding together exceed 1.5 target-line heights. | DROP | DROP | 3 |

### source

Counted from: `decisions.jsonl` + ledger inventory.

| source | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| anemi_mixed | collection-v2-dev | dev | ADMIT | 1 |
| anemi_mixed | collection-v2-train | train | ADMIT | 2 |
| anemi_round1 | collection-v2-test | test | ADMIT | 1 |
| anemi_round1 | collection-v2-train | train | ADMIT | 7 |
| anemi_round2 | collection-v2-test | test | ADMIT | 2 |
| anemi_round2 | collection-v2-train | train | ADMIT | 7 |
| archive_AA9613308335D0B014B | collection-v2-train | train | ADMIT | 1 |
| archive_bub_gb_Cmg6AQAAIAAJ | collection-v2-train | train | DROP | 1 |
| archive_izvestiianabul25192530bul | collection-v2-train | train | ADMIT | 1 |
| bsb_poly1850 | accepted-calibration-888 | train | ADMIT | 37 |
| bsb_poly1850 | accepted-calibration-888 | train | DROP | 11 |
| bsb_poly1850 | accepted-calibration-888 | train | HOLD | 2 |
| bsb_poly1850 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| bsb_poly1850 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 5 |
| elstat | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| elstat | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| elstat | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| gazette_modern | collect-v3-W1-20261018-0524 | unassigned | DROP | 4 |
| gazette_modern | collect-v3-W1-20261018-0524 | unassigned | HOLD | 6 |
| gazette_modern | collect-v3-W2-20261018-0524 | unassigned | DROP | 15 |
| gazette_modern | collect-v3-W2-20261018-0524 | unassigned | HOLD | 37 |
| ia_greek_latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 6 |
| ia_poly1850 | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| ia_poly1850 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 2 |
| ia_poly1850 | collect-v3-W2-20261018-0524 | unassigned | DROP | 3 |
| ia_poly1850 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 15 |
| ia_russian | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| lekythos | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| lekythos | collect-v3-W1-20261018-0524 | unassigned | HOLD | 3 |
| nlg | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| openarchives_Dione | collection-v2-test | test | ADMIT | 1 |
| openarchives_kallipos | collection-v2-test | test | ADMIT | 1 |
| openarchives_kallipos | collection-v2-train | train | ADMIT | 2 |
| parliament_proceedings_1975_2000 | collection-v2-dev | dev | ADMIT | 1 |
| parliament_proceedings_1975_2000 | collection-v2-test | test | ADMIT | 1 |
| parliament_proceedings_1975_2000 | collection-v2-test | test | DROP | 1 |
| parliament_proceedings_1975_2000 | collection-v2-train | train | ADMIT | 5 |
| serbia | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| vouli_parliament_1850s | collection-v2-train | train | ADMIT | 1 |
| wikisource_el | collection-v2-test | test | ADMIT | 1 |
| wikisource_ru | collection-v2-test | test | ADMIT | 1 |

### source_class

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| anemi_mixed | greek_poly | collection-v2-train | train | ADMIT | 2 |
| anemi_mixed | latin | collection-v2-dev | dev | ADMIT | 1 |
| anemi_round1 | greek_poly | collection-v2-test | test | ADMIT | 1 |
| anemi_round1 | greek_poly | collection-v2-train | train | ADMIT | 7 |
| anemi_round2 | greek_poly | collection-v2-test | test | ADMIT | 2 |
| anemi_round2 | greek_poly | collection-v2-train | train | ADMIT | 7 |
| archive_AA9613308335D0B014B | cyrillic | collection-v2-train | train | ADMIT | 1 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | collection-v2-train | train | DROP | 1 |
| archive_izvestiianabul25192530bul | latin | collection-v2-train | train | ADMIT | 1 |
| bsb_poly1850 | cyrillic | accepted-calibration-888 | train | ADMIT | 6 |
| bsb_poly1850 | cyrillic | accepted-calibration-888 | train | DROP | 1 |
| bsb_poly1850 | headings_caps | accepted-calibration-888 | train | ADMIT | 1 |
| bsb_poly1850 | latin | accepted-calibration-888 | train | ADMIT | 9 |
| bsb_poly1850 | latin | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| bsb_poly1850 | mixed_greek_latin | accepted-calibration-888 | train | ADMIT | 7 |
| bsb_poly1850 | mixed_greek_latin | accepted-calibration-888 | train | DROP | 4 |
| bsb_poly1850 | mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| bsb_poly1850 | modern_scanned | accepted-calibration-888 | train | ADMIT | 4 |
| bsb_poly1850 | modern_scanned | accepted-calibration-888 | train | DROP | 3 |
| bsb_poly1850 | nonletter | accepted-calibration-888 | train | HOLD | 1 |
| bsb_poly1850 | numerics_tables | accepted-calibration-888 | train | ADMIT | 7 |
| bsb_poly1850 | numerics_tables | accepted-calibration-888 | train | DROP | 3 |
| bsb_poly1850 | numerics_tables | accepted-calibration-888 | train | HOLD | 1 |
| bsb_poly1850 | poly1850 | accepted-calibration-888 | train | ADMIT | 1 |
| bsb_poly1850 | poly1850 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| bsb_poly1850 | poly1900 | accepted-calibration-888 | train | ADMIT | 2 |
| elstat | latin | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| elstat | latin | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| elstat | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| elstat | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | DROP | 2 |
| elstat | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| elstat | poly1900 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| gazette_modern | cyrillic | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | dialogue_fiction | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| gazette_modern | dialogue_fiction | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| gazette_modern | headings_caps | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | headings_caps | collect-v3-W2-20261018-0524 | unassigned | DROP | 5 |
| gazette_modern | headings_caps | collect-v3-W2-20261018-0524 | unassigned | HOLD | 8 |
| gazette_modern | latin | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| gazette_modern | modern_scanned | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | modern_scanned | collect-v3-W1-20261018-0524 | unassigned | HOLD | 4 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524 | unassigned | DROP | 6 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524 | unassigned | HOLD | 15 |
| gazette_modern | nonletter | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| gazette_modern | nonletter | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| gazette_modern | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | DROP | 2 |
| gazette_modern | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | DROP | 2 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | HOLD | 8 |
| gazette_modern | poly1900 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 2 |
| ia_greek_latin | latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 5 |
| ia_greek_latin | mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| ia_poly1850 | latin | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| ia_poly1850 | latin | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| ia_poly1850 | latin | collect-v3-W2-20261018-0524 | unassigned | HOLD | 8 |
| ia_poly1850 | mixed_greek_latin | collect-v3-W2-20261018-0524 | unassigned | DROP | 2 |
| ia_poly1850 | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| ia_poly1850 | poly1850 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| ia_poly1850 | poly1850 | collect-v3-W2-20261018-0524 | unassigned | DROP | 1 |
| ia_poly1850 | poly1850 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 6 |
| ia_russian | cyrillic | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| lekythos | nonletter | collect-v3-W1-20261018-0524 | unassigned | HOLD | 1 |
| lekythos | poly1900 | collect-v3-W1-20261018-0524 | unassigned | DROP | 1 |
| lekythos | poly1900 | collect-v3-W1-20261018-0524 | unassigned | HOLD | 2 |
| nlg | nonletter | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| nlg | poly1900 | collect-v3-W2-20261018-0524 | unassigned | HOLD | 1 |
| openarchives_Dione | greek_mono | collection-v2-test | test | ADMIT | 1 |
| openarchives_kallipos | greek_latin_cs | collection-v2-train | train | ADMIT | 1 |
| openarchives_kallipos | greek_mono | collection-v2-test | test | ADMIT | 1 |
| openarchives_kallipos | greek_mono | collection-v2-train | train | ADMIT | 1 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-dev | dev | ADMIT | 1 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-test | test | ADMIT | 1 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-train | train | ADMIT | 4 |
| parliament_proceedings_1975_2000 | greek_poly | collection-v2-test | test | DROP | 1 |
| parliament_proceedings_1975_2000 | greek_poly | collection-v2-train | train | ADMIT | 1 |
| serbia | cyrillic | collect-v3-W2-20261018-0524 | unassigned | HOLD | 3 |
| vouli_parliament_1850s | greek_poly | collection-v2-train | train | ADMIT | 1 |
| wikisource_el | greek_poly | collection-v2-test | test | ADMIT | 1 |
| wikisource_ru | cyrillic | collection-v2-test | test | ADMIT | 1 |

### source_class_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- | --- |
| anemi_mixed | greek_poly | collection-v2-train | train | 2 | 2 | 1.0 |
| anemi_mixed | latin | collection-v2-dev | dev | 1 | 1 | 1.0 |
| anemi_round1 | greek_poly | collection-v2-test | test | 1 | 1 | 1.0 |
| anemi_round1 | greek_poly | collection-v2-train | train | 7 | 7 | 1.0 |
| anemi_round2 | greek_poly | collection-v2-test | test | 2 | 2 | 1.0 |
| anemi_round2 | greek_poly | collection-v2-train | train | 7 | 7 | 1.0 |
| archive_AA9613308335D0B014B | cyrillic | collection-v2-train | train | 1 | 1 | 1.0 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | collection-v2-train | train | 1 | 0 | 0.0 |
| archive_izvestiianabul25192530bul | latin | collection-v2-train | train | 1 | 1 | 1.0 |
| bsb_poly1850 | cyrillic | accepted-calibration-888 | train | 7 | 6 | 0.8571428571428571 |
| bsb_poly1850 | headings_caps | accepted-calibration-888 | train | 1 | 1 | 1.0 |
| bsb_poly1850 | latin | accepted-calibration-888 | train | 9 | 9 | 1.0 |
| bsb_poly1850 | latin | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| bsb_poly1850 | mixed_greek_latin | accepted-calibration-888 | train | 11 | 7 | 0.6363636363636364 |
| bsb_poly1850 | mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| bsb_poly1850 | modern_scanned | accepted-calibration-888 | train | 7 | 4 | 0.5714285714285714 |
| bsb_poly1850 | nonletter | accepted-calibration-888 | train | 1 | 0 | 0.0 |
| bsb_poly1850 | numerics_tables | accepted-calibration-888 | train | 11 | 7 | 0.6363636363636364 |
| bsb_poly1850 | poly1850 | accepted-calibration-888 | train | 1 | 1 | 1.0 |
| bsb_poly1850 | poly1850 | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| bsb_poly1850 | poly1900 | accepted-calibration-888 | train | 2 | 2 | 1.0 |
| elstat | latin | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| elstat | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| elstat | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| elstat | poly1900 | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | cyrillic | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | dialogue_fiction | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | dialogue_fiction | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| gazette_modern | headings_caps | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | headings_caps | collect-v3-W2-20261018-0524 | unassigned | 13 | 0 | 0.0 |
| gazette_modern | latin | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| gazette_modern | modern_scanned | collect-v3-W1-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| gazette_modern | modern_scanned | collect-v3-W2-20261018-0524 | unassigned | 21 | 0 | 0.0 |
| gazette_modern | nonletter | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| gazette_modern | numerics_tables | collect-v3-W1-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| gazette_modern | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | 10 | 0 | 0.0 |
| gazette_modern | poly1900 | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| ia_greek_latin | latin | collect-v3-W1-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| ia_greek_latin | mixed_greek_latin | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| ia_poly1850 | latin | collect-v3-W1-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| ia_poly1850 | latin | collect-v3-W2-20261018-0524 | unassigned | 8 | 0 | 0.0 |
| ia_poly1850 | mixed_greek_latin | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| ia_poly1850 | numerics_tables | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| ia_poly1850 | poly1850 | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| ia_poly1850 | poly1850 | collect-v3-W2-20261018-0524 | unassigned | 7 | 0 | 0.0 |
| ia_russian | cyrillic | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| lekythos | nonletter | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| lekythos | poly1900 | collect-v3-W1-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| nlg | nonletter | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| nlg | poly1900 | collect-v3-W2-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| openarchives_Dione | greek_mono | collection-v2-test | test | 1 | 1 | 1.0 |
| openarchives_kallipos | greek_latin_cs | collection-v2-train | train | 1 | 1 | 1.0 |
| openarchives_kallipos | greek_mono | collection-v2-test | test | 1 | 1 | 1.0 |
| openarchives_kallipos | greek_mono | collection-v2-train | train | 1 | 1 | 1.0 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-dev | dev | 1 | 1 | 1.0 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-test | test | 1 | 1 | 1.0 |
| parliament_proceedings_1975_2000 | greek_mono | collection-v2-train | train | 4 | 4 | 1.0 |
| parliament_proceedings_1975_2000 | greek_poly | collection-v2-test | test | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_poly | collection-v2-train | train | 1 | 1 | 1.0 |
| serbia | cyrillic | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| vouli_parliament_1850s | greek_poly | collection-v2-train | train | 1 | 1 | 1.0 |
| wikisource_el | greek_poly | collection-v2-test | test | 1 | 1 | 1.0 |
| wikisource_ru | cyrillic | collection-v2-test | test | 1 | 1 | 1.0 |

### source_class_totals

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | split | disposition | rows |
| --- | --- | --- | --- | --- |
| anemi_mixed | greek_poly | train | ADMIT | 2 |
| anemi_mixed | latin | dev | ADMIT | 1 |
| anemi_round1 | greek_poly | test | ADMIT | 1 |
| anemi_round1 | greek_poly | train | ADMIT | 7 |
| anemi_round2 | greek_poly | test | ADMIT | 2 |
| anemi_round2 | greek_poly | train | ADMIT | 7 |
| archive_AA9613308335D0B014B | cyrillic | train | ADMIT | 1 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | train | DROP | 1 |
| archive_izvestiianabul25192530bul | latin | train | ADMIT | 1 |
| bsb_poly1850 | cyrillic | train | ADMIT | 6 |
| bsb_poly1850 | cyrillic | train | DROP | 1 |
| bsb_poly1850 | headings_caps | train | ADMIT | 1 |
| bsb_poly1850 | latin | train | ADMIT | 9 |
| bsb_poly1850 | latin | unassigned | HOLD | 2 |
| bsb_poly1850 | mixed_greek_latin | train | ADMIT | 7 |
| bsb_poly1850 | mixed_greek_latin | train | DROP | 4 |
| bsb_poly1850 | mixed_greek_latin | unassigned | HOLD | 1 |
| bsb_poly1850 | modern_scanned | train | ADMIT | 4 |
| bsb_poly1850 | modern_scanned | train | DROP | 3 |
| bsb_poly1850 | nonletter | train | HOLD | 1 |
| bsb_poly1850 | numerics_tables | train | ADMIT | 7 |
| bsb_poly1850 | numerics_tables | train | DROP | 3 |
| bsb_poly1850 | numerics_tables | train | HOLD | 1 |
| bsb_poly1850 | poly1850 | train | ADMIT | 1 |
| bsb_poly1850 | poly1850 | unassigned | HOLD | 3 |
| bsb_poly1850 | poly1900 | train | ADMIT | 2 |
| elstat | latin | unassigned | DROP | 1 |
| elstat | latin | unassigned | HOLD | 1 |
| elstat | numerics_tables | unassigned | DROP | 2 |
| elstat | numerics_tables | unassigned | HOLD | 2 |
| elstat | poly1900 | unassigned | HOLD | 1 |
| gazette_modern | cyrillic | unassigned | DROP | 1 |
| gazette_modern | dialogue_fiction | unassigned | HOLD | 3 |
| gazette_modern | headings_caps | unassigned | DROP | 6 |
| gazette_modern | headings_caps | unassigned | HOLD | 8 |
| gazette_modern | latin | unassigned | HOLD | 1 |
| gazette_modern | modern_scanned | unassigned | DROP | 7 |
| gazette_modern | modern_scanned | unassigned | HOLD | 19 |
| gazette_modern | nonletter | unassigned | DROP | 1 |
| gazette_modern | nonletter | unassigned | HOLD | 1 |
| gazette_modern | numerics_tables | unassigned | DROP | 4 |
| gazette_modern | numerics_tables | unassigned | HOLD | 9 |
| gazette_modern | poly1900 | unassigned | HOLD | 2 |
| ia_greek_latin | latin | unassigned | HOLD | 5 |
| ia_greek_latin | mixed_greek_latin | unassigned | HOLD | 1 |
| ia_poly1850 | latin | unassigned | DROP | 1 |
| ia_poly1850 | latin | unassigned | HOLD | 9 |
| ia_poly1850 | mixed_greek_latin | unassigned | DROP | 2 |
| ia_poly1850 | numerics_tables | unassigned | HOLD | 1 |
| ia_poly1850 | poly1850 | unassigned | DROP | 1 |
| ia_poly1850 | poly1850 | unassigned | HOLD | 7 |
| ia_russian | cyrillic | unassigned | HOLD | 1 |
| lekythos | nonletter | unassigned | HOLD | 1 |
| lekythos | poly1900 | unassigned | DROP | 1 |
| lekythos | poly1900 | unassigned | HOLD | 2 |
| nlg | nonletter | unassigned | HOLD | 1 |
| nlg | poly1900 | unassigned | HOLD | 1 |
| openarchives_Dione | greek_mono | test | ADMIT | 1 |
| openarchives_kallipos | greek_latin_cs | train | ADMIT | 1 |
| openarchives_kallipos | greek_mono | test | ADMIT | 1 |
| openarchives_kallipos | greek_mono | train | ADMIT | 1 |
| parliament_proceedings_1975_2000 | greek_mono | dev | ADMIT | 1 |
| parliament_proceedings_1975_2000 | greek_mono | test | ADMIT | 1 |
| parliament_proceedings_1975_2000 | greek_mono | train | ADMIT | 4 |
| parliament_proceedings_1975_2000 | greek_poly | test | DROP | 1 |
| parliament_proceedings_1975_2000 | greek_poly | train | ADMIT | 1 |
| serbia | cyrillic | unassigned | HOLD | 3 |
| vouli_parliament_1850s | greek_poly | train | ADMIT | 1 |
| wikisource_el | greek_poly | test | ADMIT | 1 |
| wikisource_ru | cyrillic | test | ADMIT | 1 |

### source_class_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| anemi_mixed | greek_poly | train | 2 | 2 | 1.0 |
| anemi_mixed | latin | dev | 1 | 1 | 1.0 |
| anemi_round1 | greek_poly | test | 1 | 1 | 1.0 |
| anemi_round1 | greek_poly | train | 7 | 7 | 1.0 |
| anemi_round2 | greek_poly | test | 2 | 2 | 1.0 |
| anemi_round2 | greek_poly | train | 7 | 7 | 1.0 |
| archive_AA9613308335D0B014B | cyrillic | train | 1 | 1 | 1.0 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | train | 1 | 0 | 0.0 |
| archive_izvestiianabul25192530bul | latin | train | 1 | 1 | 1.0 |
| bsb_poly1850 | cyrillic | train | 7 | 6 | 0.8571428571428571 |
| bsb_poly1850 | headings_caps | train | 1 | 1 | 1.0 |
| bsb_poly1850 | latin | train | 9 | 9 | 1.0 |
| bsb_poly1850 | latin | unassigned | 2 | 0 | 0.0 |
| bsb_poly1850 | mixed_greek_latin | train | 11 | 7 | 0.6363636363636364 |
| bsb_poly1850 | mixed_greek_latin | unassigned | 1 | 0 | 0.0 |
| bsb_poly1850 | modern_scanned | train | 7 | 4 | 0.5714285714285714 |
| bsb_poly1850 | nonletter | train | 1 | 0 | 0.0 |
| bsb_poly1850 | numerics_tables | train | 11 | 7 | 0.6363636363636364 |
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
| openarchives_Dione | greek_mono | test | 1 | 1 | 1.0 |
| openarchives_kallipos | greek_latin_cs | train | 1 | 1 | 1.0 |
| openarchives_kallipos | greek_mono | test | 1 | 1 | 1.0 |
| openarchives_kallipos | greek_mono | train | 1 | 1 | 1.0 |
| parliament_proceedings_1975_2000 | greek_mono | dev | 1 | 1 | 1.0 |
| parliament_proceedings_1975_2000 | greek_mono | test | 1 | 1 | 1.0 |
| parliament_proceedings_1975_2000 | greek_mono | train | 4 | 4 | 1.0 |
| parliament_proceedings_1975_2000 | greek_poly | test | 1 | 0 | 0.0 |
| parliament_proceedings_1975_2000 | greek_poly | train | 1 | 1 | 1.0 |
| serbia | cyrillic | unassigned | 3 | 0 | 0.0 |
| vouli_parliament_1850s | greek_poly | train | 1 | 1 | 1.0 |
| wikisource_el | greek_poly | test | 1 | 1 | 1.0 |
| wikisource_ru | cyrillic | test | 1 | 1 | 1.0 |

### source_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| anemi_mixed | collection-v2-dev | dev | 1 | 1 | 1.0 |
| anemi_mixed | collection-v2-train | train | 2 | 2 | 1.0 |
| anemi_round1 | collection-v2-test | test | 1 | 1 | 1.0 |
| anemi_round1 | collection-v2-train | train | 7 | 7 | 1.0 |
| anemi_round2 | collection-v2-test | test | 2 | 2 | 1.0 |
| anemi_round2 | collection-v2-train | train | 7 | 7 | 1.0 |
| archive_AA9613308335D0B014B | collection-v2-train | train | 1 | 1 | 1.0 |
| archive_bub_gb_Cmg6AQAAIAAJ | collection-v2-train | train | 1 | 0 | 0.0 |
| archive_izvestiianabul25192530bul | collection-v2-train | train | 1 | 1 | 1.0 |
| bsb_poly1850 | accepted-calibration-888 | train | 50 | 37 | 0.74 |
| bsb_poly1850 | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| bsb_poly1850 | collect-v3-W2-20261018-0524 | unassigned | 5 | 0 | 0.0 |
| elstat | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| elstat | collect-v3-W2-20261018-0524 | unassigned | 6 | 0 | 0.0 |
| gazette_modern | collect-v3-W1-20261018-0524 | unassigned | 10 | 0 | 0.0 |
| gazette_modern | collect-v3-W2-20261018-0524 | unassigned | 52 | 0 | 0.0 |
| ia_greek_latin | collect-v3-W1-20261018-0524 | unassigned | 6 | 0 | 0.0 |
| ia_poly1850 | collect-v3-W1-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| ia_poly1850 | collect-v3-W2-20261018-0524 | unassigned | 18 | 0 | 0.0 |
| ia_russian | collect-v3-W1-20261018-0524 | unassigned | 1 | 0 | 0.0 |
| lekythos | collect-v3-W1-20261018-0524 | unassigned | 4 | 0 | 0.0 |
| nlg | collect-v3-W2-20261018-0524 | unassigned | 2 | 0 | 0.0 |
| openarchives_Dione | collection-v2-test | test | 1 | 1 | 1.0 |
| openarchives_kallipos | collection-v2-test | test | 1 | 1 | 1.0 |
| openarchives_kallipos | collection-v2-train | train | 2 | 2 | 1.0 |
| parliament_proceedings_1975_2000 | collection-v2-dev | dev | 1 | 1 | 1.0 |
| parliament_proceedings_1975_2000 | collection-v2-test | test | 2 | 1 | 0.5 |
| parliament_proceedings_1975_2000 | collection-v2-train | train | 5 | 5 | 1.0 |
| serbia | collect-v3-W2-20261018-0524 | unassigned | 3 | 0 | 0.0 |
| vouli_parliament_1850s | collection-v2-train | train | 1 | 1 | 1.0 |
| wikisource_el | collection-v2-test | test | 1 | 1 | 1.0 |
| wikisource_ru | collection-v2-test | test | 1 | 1 | 1.0 |

### source_totals

Counted from: `decisions.jsonl` + ledger inventory.

| source | split | disposition | rows |
| --- | --- | --- | --- |
| anemi_mixed | dev | ADMIT | 1 |
| anemi_mixed | train | ADMIT | 2 |
| anemi_round1 | test | ADMIT | 1 |
| anemi_round1 | train | ADMIT | 7 |
| anemi_round2 | test | ADMIT | 2 |
| anemi_round2 | train | ADMIT | 7 |
| archive_AA9613308335D0B014B | train | ADMIT | 1 |
| archive_bub_gb_Cmg6AQAAIAAJ | train | DROP | 1 |
| archive_izvestiianabul25192530bul | train | ADMIT | 1 |
| bsb_poly1850 | train | ADMIT | 37 |
| bsb_poly1850 | train | DROP | 11 |
| bsb_poly1850 | train | HOLD | 2 |
| bsb_poly1850 | unassigned | HOLD | 6 |
| elstat | unassigned | DROP | 3 |
| elstat | unassigned | HOLD | 4 |
| gazette_modern | unassigned | DROP | 19 |
| gazette_modern | unassigned | HOLD | 43 |
| ia_greek_latin | unassigned | HOLD | 6 |
| ia_poly1850 | unassigned | DROP | 4 |
| ia_poly1850 | unassigned | HOLD | 17 |
| ia_russian | unassigned | HOLD | 1 |
| lekythos | unassigned | DROP | 1 |
| lekythos | unassigned | HOLD | 3 |
| nlg | unassigned | HOLD | 2 |
| openarchives_Dione | test | ADMIT | 1 |
| openarchives_kallipos | test | ADMIT | 1 |
| openarchives_kallipos | train | ADMIT | 2 |
| parliament_proceedings_1975_2000 | dev | ADMIT | 1 |
| parliament_proceedings_1975_2000 | test | ADMIT | 1 |
| parliament_proceedings_1975_2000 | test | DROP | 1 |
| parliament_proceedings_1975_2000 | train | ADMIT | 5 |
| serbia | unassigned | HOLD | 3 |
| vouli_parliament_1850s | train | ADMIT | 1 |
| wikisource_el | test | ADMIT | 1 |
| wikisource_ru | test | ADMIT | 1 |

### source_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- |
| anemi_mixed | dev | 1 | 1 | 1.0 |
| anemi_mixed | train | 2 | 2 | 1.0 |
| anemi_round1 | test | 1 | 1 | 1.0 |
| anemi_round1 | train | 7 | 7 | 1.0 |
| anemi_round2 | test | 2 | 2 | 1.0 |
| anemi_round2 | train | 7 | 7 | 1.0 |
| archive_AA9613308335D0B014B | train | 1 | 1 | 1.0 |
| archive_bub_gb_Cmg6AQAAIAAJ | train | 1 | 0 | 0.0 |
| archive_izvestiianabul25192530bul | train | 1 | 1 | 1.0 |
| bsb_poly1850 | train | 50 | 37 | 0.74 |
| bsb_poly1850 | unassigned | 6 | 0 | 0.0 |
| elstat | unassigned | 7 | 0 | 0.0 |
| gazette_modern | unassigned | 62 | 0 | 0.0 |
| ia_greek_latin | unassigned | 6 | 0 | 0.0 |
| ia_poly1850 | unassigned | 21 | 0 | 0.0 |
| ia_russian | unassigned | 1 | 0 | 0.0 |
| lekythos | unassigned | 4 | 0 | 0.0 |
| nlg | unassigned | 2 | 0 | 0.0 |
| openarchives_Dione | test | 1 | 1 | 1.0 |
| openarchives_kallipos | test | 1 | 1 | 1.0 |
| openarchives_kallipos | train | 2 | 2 | 1.0 |
| parliament_proceedings_1975_2000 | dev | 1 | 1 | 1.0 |
| parliament_proceedings_1975_2000 | test | 2 | 1 | 0.5 |
| parliament_proceedings_1975_2000 | train | 5 | 5 | 1.0 |
| serbia | unassigned | 3 | 0 | 0.0 |
| vouli_parliament_1850s | train | 1 | 1 | 1.0 |
| wikisource_el | test | 1 | 1 | 1.0 |
| wikisource_ru | test | 1 | 1 | 1.0 |

### toolchain_versions

Counted from: `decisions.jsonl` + ledger inventory.

| tool | version | rows |
| --- | --- | --- |
| census | 0.5 | 200 |
| composer | 0.2 | 200 |
| content_gate | 0.2 | 200 |
| content_repair | 0.2 | 200 |
| cyrillic | 0.3 | 200 |
| dashes | 0.1 | 200 |
| final_eligibility | 0.2 | 200 |
| inventory | 0.1 | 200 |
| numerics | 0.2 | 200 |
| polytonic | 0.7 | 200 |
| segmentation | 0.8 | 200 |

### Timing

Counted from: readout process wall clock.

| elapsed_seconds |
| --- |
| 0.04872298240661621 |

### Tool version binding

Counted from: `ledger.sqlite` run binding.

| path | sha256 | tools |
| --- | --- | --- |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/docs/harvest/line_pipeline/tool_versions.json | bfaf961be0031d6e5b334801fce66f46aea1b48169a6861d180eb72ac7089ee0 | {'census': {'components': {'greek-ocr-toolkit-sol-recut/greekocr/harvest/geometry_observations.py': '524972373acb094384f48055dfb1189f799c648df81370c5a9d5952c7798c695', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py': 'f4e4b1d30836412f145a5f6557ff8432bed7867a1e8de9f03991f8af40fb0cbd', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py': '35aeec0d2587ea30ed270caf881b87af75c3b9696627dc18676b228ee3c29931', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_native.py': '47b7742ef6bae9274392838c070309f1e7d5c8fc389b52826a21ee1d1fa8515c', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_parallel.py': '52aef74eb01e17669dc068c8532c7008c251e8d1b5308f8e38790c613db0197e', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_runtime.py': '8687f59c0986eff6a3f008c890385724a880c0e6356d6e059d61ec192386d483', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_sources.py': 'd84f024f755d23543bd0b0601f14e2e7adae5d1eaadbc325e636bff3d628788e', 'greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/bootstrap.py': '7ec4b9ddb4a7ad87631992f834ab9a0f52ce6a42e2f6226103ad9a839695dc18', 'greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/filter_crop_paths.py': '04247e96e82db502c7da154f70360f8f4a17b2a9620bb26df9d8bca781ae7110', 'greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/filter_worker.sbatch': '3b30cf18b1d72207000d0532afed44cfa9961982dc84dbd950d66de2b716153c', 'greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/package.py': 'cd4b9d0ae23e405ed61c81abb1a37029ce43abf456390abd2167df5b9b613da5', 'greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/worker.py': '8c8109606e50bf6b26f74d95436e555bc3bac0984ed5c584600fa2602b2ea5c7', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py': 'f84aef028e465ac5c54aa394178adc3bcbcd3740aff5d9d6f59c99a1701b0e52', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/numeric_cells.py': 'd0cf6ce82ef2c34e044d911d69bf5d1aa7122fc701a7042e2011feab6bdc202b'}, 'digest': '670ad2e3ea7cfcb214d8c5f12bae30163fc57fb433f8137bcd5deaa6be7d4957', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'bounded parallel native workers for CSCS', 'profiled CSCS throughput tuning with bounded queue lookahead and node-scale worker qualification', 'parent-confirmed collection-v2 legacy evaluation split aliases with retained lineage'], 'iteration_count': 5, 'scope': 'existing toolkit primitives with new orchestration', 'version': '0.5'}, 'composer': {'components': {'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py': 'f4e4b1d30836412f145a5f6557ff8432bed7867a1e8de9f03991f8af40fb0cbd', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py': '35aeec0d2587ea30ed270caf881b87af75c3b9696627dc18676b228ee3c29931'}, 'digest': 'c56ad770599f7d3d0c399d10e0088855d39c1d07d6627ff261ff7889d0f55b0c', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports'], 'iteration_count': 2, 'scope': 'existing toolkit primitives with new orchestration', 'version': '0.2'}, 'content_gate': {'components': {'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py': 'f4e4b1d30836412f145a5f6557ff8432bed7867a1e8de9f03991f8af40fb0cbd', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py': '35aeec0d2587ea30ed270caf881b87af75c3b9696627dc18676b228ee3c29931'}, 'digest': 'c56ad770599f7d3d0c399d10e0088855d39c1d07d6627ff261ff7889d0f55b0c', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports'], 'iteration_count': 2, 'scope': 'existing toolkit primitives with new orchestration', 'version': '0.2'}, 'content_repair': {'components': {'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py': 'f4e4b1d30836412f145a5f6557ff8432bed7867a1e8de9f03991f8af40fb0cbd', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py': '35aeec0d2587ea30ed270caf881b87af75c3b9696627dc18676b228ee3c29931'}, 'digest': 'c56ad770599f7d3d0c399d10e0088855d39c1d07d6627ff261ff7889d0f55b0c', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports'], 'iteration_count': 2, 'scope': 'evidence-backed external repair interface; missing evidence holds', 'version': '0.2'}, 'cyrillic': {'components': {'greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v3_edits.jsonl': '4f1a51f5eb80788fb1cdc7a01220c90df028e79711cf0eeec2d0ace2ee42d1d0', 'greek-ocr-toolkit-secondary/scripts/secondary/ru1_decide.py': 'cc50121e27e90cb4555e0cb98f8ad091f5a4e00c7a410c553ae9d0c7b373d41a'}, 'digest': 'f63e1ba8696adb47dfc07b283c615fe83deb3f1d2fd28acbf0300de495235123', 'documented_iterations': ['ru1_v1', 'ru1_v2_train', 'ru1_v3_edits'], 'iteration_count': 3, 'scope': 'historical Russian ь→ъ only', 'version': '0.3'}, 'dashes': {'components': {'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py': 'f4e4b1d30836412f145a5f6557ff8432bed7867a1e8de9f03991f8af40fb0cbd'}, 'digest': '07a2c3f17d94f2467d70ea3c6af0b056c3f338707b0a45fefcab5eddccf4220c', 'documented_iterations': ['dash tags; no general repair release'], 'iteration_count': 1, 'scope': 'tag only', 'version': '0.1'}, 'final_eligibility': {'components': {'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py': 'f4e4b1d30836412f145a5f6557ff8432bed7867a1e8de9f03991f8af40fb0cbd', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py': '35aeec0d2587ea30ed270caf881b87af75c3b9696627dc18676b228ee3c29931'}, 'digest': 'c56ad770599f7d3d0c399d10e0088855d39c1d07d6627ff261ff7889d0f55b0c', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports'], 'iteration_count': 2, 'scope': 'existing toolkit primitives with new orchestration', 'version': '0.2'}, 'inventory': {'components': {'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py': 'f4e4b1d30836412f145a5f6557ff8432bed7867a1e8de9f03991f8af40fb0cbd'}, 'digest': '07a2c3f17d94f2467d70ea3c6af0b056c3f338707b0a45fefcab5eddccf4220c', 'documented_iterations': ['first integrated graph implementation'], 'iteration_count': 1, 'scope': 'existing toolkit inventory primitives', 'version': '0.1'}, 'numerics': {'components': {'greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_w1.jsonl': '94fb67c1aab9f2ec3bf5d47bc36508b7e700508cd27391f70ebfc26f8d73230e', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py': 'f4e4b1d30836412f145a5f6557ff8432bed7867a1e8de9f03991f8af40fb0cbd'}, 'digest': '7903c9ec8d1c52cefd8f4458879be1ea656b0b52874726c3169b7c7adc17a893', 'documented_iterations': ['N1 automatic ink candidate (rejected 0/5)', 'N1 assisted two-reader and lead-pixel release'], 'iteration_count': 2, 'scope': 'assisted separator corrections; failed automatic candidate is disabled; FP3 exact digit-separator-digit candidate-negative patch; no correction gate change', 'version': '0.2'}, 'polytonic': {'components': {'greek-ocr-toolkit-spellcheck/scripts/labelfix/release_gate_sf7.py': '2f7a777a91adae1af5238a9f2092c59326fc6cc7d83d6ad3bf115866455ec208'}, 'digest': 'de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5', 'documented_iterations': ['S1', 'S2', 'S3', 'S4', 'S5', 'SF6', 'SF7'], 'iteration_count': 7, 'scope': 'SF7 A; existing detector/readers; exact release candidate_pre_audit', 'version': '0.7'}, 'segmentation': {'version': '0.8', 'documented_iterations': ['29fa466 crop guides', '5d664bf font normalized', 'cad8709 target-box normalization', 'b2f8d95 whole-word tolerance', '405d4f1 padding 1.5 heights', '0.5 + row-frame text box', 'crop-only line inventory and cut-off gate before length', "owner's three rules; remove target-cut veto and taller-than-upright guard"], 'iteration_count': 8, 'scope': "0.8 exactly the owner's three rules: crop-only other-lines gate, unchanged 0.6 length and padding; cut evidence is diagnostics only; owner policy 2026-10-19", 'components': {'greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/segmentation-policy.js': 'e5b635ff9a04cc66f454a68e01ce9773229672e655b3ee08296ee5c0d149ee15', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/crop-tools.py': '921b79ad1450e1023518e4aa36280a0efea2fe83ae1739ca0166e98c14ede1af', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/font-models.json': 'fb3f28f7d90c2b638bfe9c72ab42dcf060d59939a7ab410fc2e1cf6d898965de', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/service.mjs': 'df1781fb469c92dfe3b7fe886b4297a7ca20878bb82006cf6825536ce537c911', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py': '1dd618bc2d884cf2490498456653f49b0276944f3bde83d38e26e633031eb641', 'greek-ocr-toolkit-sol-recut/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py': '038bd46af4535e6de6af58e11c4b7496e03e0434094cc8cd6b48668e2199ad77'}, 'digest': '512e362a691c6f2f425acc41e587b4b751dedbaadd10077d42309ed3f1f7bebd'}} |

### Diagnostics (first 20 in file order)

Counted from: `decisions.jsonl`, `admitted_train.jsonl`, ledger inventory.

| issue | count | first20 |
| --- | --- | --- |
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
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/CURRENT.json | 460 | 6503553aafcb4b5784b59127fe7569720072b09b3f739c47e588e890d741c89f |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/admission_records.jsonl | 3102236 | f1d57e8a6e3acba9bc495e9896a4b805bf0416846e4ff1eca629fd066e0261c7 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/admitted_train.jsonl | 994141 | 1f25f310ccffb77744bd1d407a33a552be8ae44be163a627003d99e7455b4bd7 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/decisions.jsonl | 3024463 | f7df50cb3f9ff7708087fed3eb7eb1bfeb46db2a9621bcbdeaca43f304f99e52 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/evaluation_diagnostics.jsonl | 2581026 | cc38da543270355f80b5b97451b00e32a0efda130638622384234f665002f728 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/pending_content_repair.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/pending_cyrillic.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/pending_numerics.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/pending_polytonic.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/generations/g1-4ba51f64d04c48cfa19741e84c232dde/summary.json | 16388 | b9f63edeb8192006bbb3e53f3fa2c2d2588d43f4929290234dc7f268ecd5d7b3 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/mock_batch/mode-i-removed/ledger.sqlite | 7483392 | d5cb7fbc2e2b673bfa60ffaa89c18e9363e3cfe38d7bd43533e7dbee6834da37 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/docs/harvest/line_pipeline/tool_versions.json | 11171 | bfaf961be0031d6e5b334801fce66f46aea1b48169a6861d180eb72ac7089ee0 |

No baseline supplied; no historical delta inferred. The handoff records 65,900 admissions.

CENSUS READOUT: rows 200 (complete yes); ADMIT 73 HOLD 87 DROP 40; admitted_train 63; gate DROP 0 HOLD 0 (mixed 0 foreign 0 short 0 cell1 0 num1 0 unresolved 0); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 14/14 PASS
