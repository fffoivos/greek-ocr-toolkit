# SS9 removals

Only owner gate 0.3 part 2 + supplied gate failures; no other admission rules. Raw Google text; dimensions width_px/height_px. No normalization, crop reading or new judgments. Gate failures are counted separately; single-character removal totals below exclude gate failures.

| gate_failed — Only owner gate 0.3 part 2 + supplied gate failures; no other admission rules | reason | n |
| --- | --- | --- |
| False | — | 47594 |
| False | single_character_cell | 10702 |
| False | numeric_shape | 0 |
| False | short_line | 0 |
| False | cell_status_unresolved | 0 |
| True | — | 554 |
| True | single_character_cell | 152 |
| True | numeric_shape | 0 |
| True | short_line | 0 |
| True | cell_status_unresolved | 0 |


| measure — Only owner gate 0.3 part 2 + supplied gate failures; no other admission rules | original (SS1/SS2) | gate-removed (SS8) | admitted + gate |
| --- | --- | --- | --- |
| /by_alnum/0 | — | — | 3332 |
| /by_alnum/1 | — | — | 7370 |
| /by_output_type/mixed | — | — | 64 |
| /by_output_type/nonnumeric | — | — | 4499 |
| /by_output_type/numeric | — | — | 6139 |
| /by_primary_class/cyrillic | — | — | 20 |
| /by_primary_class/greek_mono | — | — | 101 |
| /by_primary_class/latin | — | — | 1188 |
| /by_primary_class/modern_scanned | — | — | 301 |
| /by_primary_class/nonletter | — | — | 4428 |
| /by_primary_class/numerics_tables | — | — | 4654 |
| /by_primary_class/poly1850 | — | — | 8 |
| /by_primary_class/poly1900 | — | — | 2 |
| /by_source/bsb_poly1850 | — | — | 510 |
| /by_source/elstat | — | — | 1191 |
| /by_source/gazette_modern | — | — | 6414 |
| /by_source/ia_greek_latin | — | — | 348 |
| /by_source/ia_poly1850 | — | — | 1495 |
| /by_source/ia_russian | — | — | 130 |
| /by_source/kosmopolis | — | — | 51 |
| /by_source/lekythos | — | — | 90 |
| /by_source/nlg | — | — | 312 |
| /by_source/serbia | — | — | 161 |
| /n | — | — | 10702 |
| /numeric | — | — | 6139 |
| /text | — | — | 4563 |


Removed rows in the 417 bed (non-gate only):

| measure — Only owner gate 0.3 part 2 + supplied gate failures; no other admission rules | original (SS1/SS2) | gate-removed (SS8) | admitted + gate |
| --- | --- | --- | --- |
| /by_final_class/legit_text | — | — | 9 |
| /by_final_class/non_text | — | — | 7 |
| /by_final_class/printed_nonletter | — | — | 36 |
| /by_final_class/segmentation_fault | — | — | 5 |
| /by_final_type/cut_fragment | — | — | 2 |
| /by_final_type/figure_ornament | — | — | 2 |
| /by_final_type/handwriting | — | — | 1 |
| /by_final_type/marker | — | — | 9 |
| /by_final_type/noise | — | — | 4 |
| /by_final_type/punctuation | — | — | 39 |
| /n | — | — | 57 |


**Estimate:** each class share among removed bed rows × removed population nonnumeric/mixed count. This is a sample projection, not observed population labels.

| final_class — Only owner gate 0.3 part 2 + supplied gate failures; no other admission rules | sample_n | removed_sample_share | estimated_rows |
| --- | --- | --- | --- |
| legit_text | 9 | 0.157895 | 720.473684 |
| printed_nonletter | 36 | 0.631579 | 2881.894737 |
| non_text | 7 | 0.122807 | 560.368421 |
| out_of_scope_script | 0 | 0 | 0 |
| segmentation_fault | 5 | 0.087719 | 400.263158 |
| other | 0 | 0 | 0 |


Diagnostics:

| measure — Only owner gate 0.3 part 2 + supplied gate failures; no other admission rules | original (SS1/SS2) | gate-removed (SS8) | admitted + gate |
| --- | --- | --- | --- |
| /census_by_reason/admitted | — | — | 578109 |
| /census_by_reason/numeric_shape | — | — | 4 |
| /census_by_reason/short_line | — | — | 3463 |
| /census_by_reason/single_character_cell | — | — | 10890 |
| /census_numeric_grammar_disagrees_with_is_numeric_output | — | — | 536 |
| /small_NFC_admission_reason_changes | — | — | 0 |
