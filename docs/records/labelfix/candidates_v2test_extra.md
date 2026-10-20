# Candidate run on a training sample

Sampled lines: 2400 (random, seed 20261016, admitted rows of `import_real_v2_train.jsonl`); Google = model on 17 lines; lines with at least one candidate: 2366; candidates: 2819; accepted: 442.

## Candidates per rule per wave

| rule | wave | sampled lines | candidates | accepted | abstained | rejected | excluded | accepted per 1000 lines | projected accepted in train wave |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | mixed | 184 | 48 | 3 | 0 | 43 | 2 | 16.3 | 36 |
| breathing | parliament | 689 | 67 | 4 | 0 | 56 | 7 | 5.8 | 69 |
| breathing | round1 | 922 | 286 | 12 | 0 | 257 | 17 | 13.0 | 106 |
| breathing | round2 | 331 | 81 | 5 | 0 | 72 | 4 | 15.1 | 56 |
| breathing | vouli | 269 | 75 | 3 | 0 | 69 | 3 | 11.2 | 19 |
| accent | mixed | 184 | 39 | 1 | 0 | 34 | 4 | 5.4 | 12 |
| accent | openarchives | 5 | 3 | 0 | 0 | 3 | 0 | 0.0 | 0 |
| accent | parliament | 689 | 247 | 11 | 0 | 221 | 15 | 16.0 | 191 |
| accent | round1 | 922 | 270 | 14 | 0 | 238 | 18 | 15.2 | 123 |
| accent | round2 | 331 | 70 | 5 | 0 | 59 | 6 | 15.1 | 56 |
| accent | vouli | 269 | 111 | 1 | 0 | 108 | 2 | 3.7 | 6 |
| subscript | mixed | 184 | 25 | 3 | 0 | 20 | 2 | 16.3 | 36 |
| subscript | parliament | 689 | 18 | 1 | 0 | 17 | 0 | 1.5 | 17 |
| subscript | round1 | 922 | 140 | 2 | 0 | 133 | 5 | 2.2 | 18 |
| subscript | round2 | 331 | 50 | 0 | 0 | 47 | 3 | 0.0 | 0 |
| subscript | vouli | 269 | 38 | 2 | 0 | 36 | 0 | 7.4 | 13 |
| dialytika | mixed | 184 | 2 | 0 | 0 | 1 | 1 | 0.0 | 0 |
| dialytika | openarchives | 5 | 1 | 0 | 0 | 1 | 0 | 0.0 | 0 |
| dialytika | parliament | 689 | 2 | 0 | 0 | 2 | 0 | 0.0 | 0 |
| dialytika | round1 | 922 | 6 | 0 | 0 | 6 | 0 | 0.0 | 0 |
| dialytika | round2 | 331 | 2 | 0 | 0 | 2 | 0 | 0.0 | 0 |
| marks_multi | mixed | 184 | 22 | 0 | 0 | 19 | 3 | 0.0 | 0 |
| marks_multi | parliament | 689 | 19 | 0 | 0 | 16 | 3 | 0.0 | 0 |
| marks_multi | round1 | 922 | 78 | 0 | 0 | 74 | 4 | 0.0 | 0 |
| marks_multi | round2 | 331 | 21 | 0 | 0 | 18 | 3 | 0.0 | 0 |
| marks_multi | vouli | 269 | 25 | 1 | 0 | 22 | 2 | 3.7 | 6 |
| final_grave | mixed | 184 | 56 | 32 | 18 | 5 | 1 | 173.9 | 383 |
| final_grave | parliament | 689 | 323 | 115 | 158 | 38 | 12 | 166.9 | 1993 |
| final_grave | round1 | 922 | 130 | 63 | 46 | 19 | 2 | 68.3 | 554 |
| final_grave | round2 | 331 | 121 | 71 | 41 | 7 | 2 | 214.5 | 791 |
| final_grave | vouli | 269 | 56 | 18 | 33 | 4 | 1 | 66.9 | 117 |
| base_sub | mixed | 184 | 23 | 1 | 0 | 22 | 0 | 5.4 | 12 |
| base_sub | openarchives | 5 | 7 | 0 | 0 | 7 | 0 | 0.0 | 0 |
| base_sub | parliament | 689 | 89 | 19 | 1 | 65 | 4 | 27.6 | 329 |
| base_sub | round1 | 922 | 114 | 8 | 6 | 98 | 2 | 8.7 | 70 |
| base_sub | round2 | 331 | 20 | 1 | 0 | 18 | 1 | 3.0 | 11 |
| base_sub | vouli | 269 | 19 | 1 | 0 | 18 | 0 | 3.7 | 6 |
| final_sigma | parliament | 689 | 1 | 1 | 0 | 0 | 0 | 1.5 | 17 |
| constraint | mixed | 184 | 7 | 5 | 0 | 2 | 0 | 27.2 | 60 |
| constraint | parliament | 689 | 41 | 12 | 0 | 29 | 0 | 17.4 | 208 |
| constraint | round1 | 922 | 41 | 19 | 0 | 22 | 0 | 20.6 | 167 |
| constraint | round2 | 331 | 16 | 6 | 0 | 10 | 0 | 18.1 | 67 |
| constraint | vouli | 269 | 9 | 2 | 0 | 7 | 0 | 7.4 | 13 |

## Projection to the training set

Train records: 44029 admitted rows (207,851 after codec per E3_RESULTS; the projection uses per-wave rates × admitted rows per wave, then scales by 207851/44029).

| rule | accepted in sample | projected accepted (full train) |
|---|---:|---:|
| breathing | 27 | 1350 |
| accent | 32 | 1832 |
| subscript | 8 | 396 |
| dialytika | 0 | 0 |
| marks_multi | 1 | 31 |
| final_grave | 299 | 18122 |
| base_sub | 30 | 2027 |
| final_sigma | 1 | 82 |
| constraint | 44 | 2431 |
| **all** | 442 | 26269 |

## Policy defaults

3a line-initial capitalised words admitted: 4 candidates, 1 accepted. 3b acute-everywhere pages: 1 of 402 sampled pages (note: a sampled page usually has few lines, so the ≥ 10 accented-word floor rarely triggers here); final_grave suppressed on them: 0.


Ink-decisive variant (lexicon-neutral + mark-shape classifier at tau): 34 candidates (accent 28, subscript 3, breathing 3); not folded into accepted.


## Outcomes by rule (all waves)

| rule | candidates | accepted | abstained | rejected | excluded |
|---|---:|---:|---:|---:|---:|
| breathing | 557 | 27 | 0 | 497 | 33 |
| accent | 740 | 32 | 0 | 663 | 45 |
| subscript | 271 | 8 | 0 | 253 | 10 |
| dialytika | 13 | 0 | 0 | 12 | 1 |
| marks_multi | 165 | 1 | 0 | 149 | 15 |
| final_grave | 686 | 299 | 296 | 73 | 18 |
| base_sub | 272 | 30 | 7 | 228 | 7 |
| final_sigma | 1 | 1 | 0 | 0 | 0 |
| constraint | 114 | 44 | 0 | 70 | 0 |

## Abstention / rejection reasons

| reason | n |
|---|---:|
| model_form_unattested | 361 |
| model_form_unattested + abstain:localisation_uncertain | 170 |
| abstain:localisation_uncertain | 166 |
| both_attested | 158 |
| model_form_unattested + above_count | 116 |
| excluded:proper_name | 104 |
| both_attested + abstain:merged_marks | 103 |
| both_attested + abstain:localisation_uncertain | 102 |
| model_form_unattested + abstain:merged_marks | 94 |
| model_form_unattested + abstain:neighbouring_marks | 80 |
| both_attested + above_count | 79 |
| abstain:needs_one_oblique | 77 |
| slope_disagrees | 73 |
| model_form_unattested + abstain:removal_with_wide_blob | 54 |
| both_attested + abstain:neighbouring_marks | 54 |
| model_form_unattested + abstain:clipped_top_no_false_absence | 53 |
| abstain:final_grave_before_punctuation | 45 |
| both_attested + abstain:clipped_top_no_false_absence | 31 |
| model_form_unattested + abstain:clipped_bottom | 30 |
| abstain:faint_mark | 29 |
| model_form_unattested + abstain:faint_mark | 28 |
| both_attested + abstain:faint_mark | 26 |
| both_attested + abstain:removal_with_wide_blob | 25 |
| model_form_unattested + blob_below_but_model_has_none | 22 |
| abstain:merged_marks | 22 |
| above_count | 22 |
| excluded:hyphen_line_end | 18 |
| both_attested + abstain:clipped_bottom | 17 |
| model_form_unattested + abstain:clipped_top | 16 |
| model_form_unattested + abstain:needs_one_oblique | 14 |
| violates:C1:missing_initial_breathing + abstain:localisation_uncertain | 14 |
| both_attested + abstain:needs_one_oblique | 13 |
| both_attested + no_blob_below | 10 |
| model_form_unattested + no_blob_below | 9 |
| violates:C1:missing_initial_breathing + above_count | 9 |
| no_blob_below | 7 |
| abstain:google_letters_attested_with_other_marks | 7 |
| margin_below_20x | 7 |
| abstain:neighbouring_marks | 6 |
| oblique_but_model_has_circumflex | 6 |
| both_attested + blob_below_but_model_has_none | 6 |
| violates:C1:missing_initial_breathing + abstain:merged_marks | 6 |
| excluded:all_caps_marks | 5 |
| violates:C1:missing_initial_breathing + abstain:faint_mark | 5 |
| violates:C3:two_accents + abstain:removal_with_wide_blob | 5 |
| rejected:polytonic_mark_in_monotonic_regime | 5 |
| violates:C3:two_accents + above_count | 4 |
| model_form_unattested + oblique_but_model_has_circumflex | 4 |
| abstain:clipped_bottom | 4 |
| blob_below_but_model_has_none | 4 |
| violates:C1:missing_initial_breathing+C3:two_accents + abstain:faint_mark | 4 |
| margin_below_20x + no_blob_below | 3 |
| violates:C1:missing_initial_breathing + abstain:neighbouring_marks | 3 |
| margin_below_20x + abstain:clipped_bottom | 3 |
| violates:C4:circumflex_before_penult + abstain:localisation_uncertain | 3 |
| both_attested + abstain:clipped_top | 3 |
| violates:C1:missing_initial_breathing + abstain:clipped_top | 2 |
| violates:C3:two_accents + abstain:clipped_top_no_false_absence | 2 |
| excluded:abbreviation | 2 |
| margin_below_20x + abstain:localisation_uncertain | 2 |
| violates:C1:missing_initial_breathing+C3:two_accents + above_count | 2 |
| violates:C1:missing_initial_breathing+C3:two_accents + abstain:localisation_uncertain | 2 |
| margin_below_20x + oblique_but_model_has_circumflex | 1 |
| violates:C3:two_accents+C4:circumflex_before_penult + abstain:removal_with_wide_blob | 1 |
| abstain:removal_with_wide_blob | 1 |
| violates:C1:several_breathings + abstain:neighbouring_marks | 1 |
| margin_below_20x + above_count | 1 |
| margin_below_20x + abstain:faint_mark | 1 |
| violates:C3:two_accents + abstain:faint_mark | 1 |
| margin_below_50x | 1 |
| violates:C4:grave_not_final + oblique_but_model_has_circumflex | 1 |
| abstain:clipped_top | 1 |
| margin_below_20x + abstain:neighbouring_marks | 1 |
| margin_below_20x + abstain:merged_marks | 1 |
| both_attested + oblique_but_model_has_circumflex | 1 |
| violates:C4:circumflex_before_penult + abstain:neighbouring_marks | 1 |
| violates:C3:two_accents + abstain:merged_marks | 1 |
| margin_below_20x + abstain:clipped_top | 1 |
| model_form_unattested + no_two_dots | 1 |
| margin_below_20x + abstain:clipped_top_no_false_absence | 1 |
| violates:C4:circumflex_before_penult + above_count | 1 |
| violates:C4:circumflex_before_penult + abstain:needs_one_oblique | 1 |
| violates:C3:two_accents + abstain:localisation_uncertain | 1 |
