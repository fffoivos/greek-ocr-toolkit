# Candidate run on a training sample

Sampled lines: 5000 (random, seed 20261016, admitted rows of `import_real_v2_train.jsonl`); Google = model on 3510 lines; lines with at least one candidate: 502; candidates: 564; accepted: 76.

## Candidates per rule per wave

| rule | wave | sampled lines | candidates | accepted | abstained | rejected | excluded | accepted per 1000 lines | projected accepted in train wave |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | mixed | 615 | 13 | 1 | 0 | 7 | 5 | 1.6 | 45 |
| breathing | parliament | 1501 | 22 | 1 | 0 | 9 | 12 | 0.7 | 43 |
| breathing | round1 | 1075 | 40 | 1 | 0 | 32 | 7 | 0.9 | 44 |
| breathing | round2 | 470 | 10 | 0 | 0 | 9 | 1 | 0.0 | 0 |
| breathing | vouli | 562 | 21 | 1 | 0 | 13 | 7 | 1.8 | 44 |
| accent | mixed | 615 | 23 | 4 | 0 | 13 | 6 | 6.5 | 179 |
| accent | openarchives | 492 | 1 | 0 | 0 | 1 | 0 | 0.0 | 0 |
| accent | parliament | 1501 | 70 | 4 | 0 | 44 | 22 | 2.7 | 172 |
| accent | round1 | 1075 | 65 | 2 | 0 | 51 | 12 | 1.9 | 87 |
| accent | round2 | 470 | 23 | 1 | 0 | 15 | 7 | 2.1 | 40 |
| accent | vouli | 562 | 28 | 2 | 0 | 21 | 5 | 3.6 | 89 |
| subscript | mixed | 615 | 4 | 1 | 0 | 2 | 1 | 1.6 | 45 |
| subscript | parliament | 1501 | 4 | 0 | 0 | 4 | 0 | 0.0 | 0 |
| subscript | round1 | 1075 | 18 | 1 | 0 | 13 | 4 | 0.9 | 44 |
| subscript | round2 | 470 | 6 | 0 | 0 | 6 | 0 | 0.0 | 0 |
| subscript | vouli | 562 | 8 | 0 | 0 | 8 | 0 | 0.0 | 0 |
| marks_multi | mixed | 615 | 6 | 0 | 0 | 6 | 0 | 0.0 | 0 |
| marks_multi | parliament | 1501 | 3 | 0 | 0 | 0 | 3 | 0.0 | 0 |
| marks_multi | round1 | 1075 | 8 | 0 | 0 | 5 | 3 | 0.0 | 0 |
| marks_multi | round2 | 470 | 2 | 0 | 0 | 2 | 0 | 0.0 | 0 |
| marks_multi | vouli | 562 | 7 | 0 | 0 | 5 | 2 | 0.0 | 0 |
| final_grave | mixed | 615 | 8 | 1 | 4 | 1 | 2 | 1.6 | 45 |
| final_grave | parliament | 1501 | 49 | 19 | 12 | 5 | 13 | 12.7 | 817 |
| final_grave | round1 | 1075 | 33 | 17 | 7 | 2 | 7 | 15.8 | 743 |
| final_grave | round2 | 470 | 7 | 4 | 1 | 0 | 2 | 8.5 | 160 |
| final_grave | vouli | 562 | 15 | 3 | 8 | 0 | 4 | 5.3 | 133 |
| base_sub | mixed | 615 | 4 | 1 | 0 | 3 | 0 | 1.6 | 45 |
| base_sub | openarchives | 492 | 1 | 0 | 0 | 1 | 0 | 0.0 | 0 |
| base_sub | parliament | 1501 | 20 | 2 | 0 | 13 | 5 | 1.3 | 86 |
| base_sub | round1 | 1075 | 14 | 1 | 1 | 8 | 4 | 0.9 | 44 |
| base_sub | round2 | 470 | 4 | 0 | 0 | 2 | 2 | 0.0 | 0 |
| base_sub | vouli | 562 | 3 | 0 | 0 | 1 | 2 | 0.0 | 0 |
| constraint | mixed | 615 | 9 | 4 | 0 | 5 | 0 | 6.5 | 179 |
| constraint | parliament | 1501 | 5 | 1 | 0 | 4 | 0 | 0.7 | 43 |
| constraint | round1 | 1075 | 3 | 1 | 0 | 2 | 0 | 0.9 | 44 |
| constraint | round2 | 470 | 4 | 2 | 0 | 2 | 0 | 4.3 | 80 |
| constraint | vouli | 562 | 3 | 1 | 0 | 2 | 0 | 1.8 | 44 |

## Projection to the training set

Train records: 214436 admitted rows (207,851 after codec per E3_RESULTS; the projection uses per-wave rates × admitted rows per wave, then scales by 207851/214436).

| rule | accepted in sample | projected accepted (full train) |
|---|---:|---:|
| breathing | 4 | 170 |
| accent | 13 | 550 |
| subscript | 2 | 86 |
| dialytika | 0 | 0 |
| marks_multi | 0 | 0 |
| final_grave | 44 | 1839 |
| base_sub | 4 | 169 |
| final_sigma | 0 | 0 |
| constraint | 9 | 378 |
| **all** | 76 | 3193 |

## Policy defaults

3a line-initial capitalised words admitted: 4 candidates, 0 accepted. 3b acute-everywhere pages: 7 of 2693 sampled pages (note: a sampled page usually has few lines, so the ≥ 10 accented-word floor rarely triggers here); final_grave suppressed on them: 0.


Ink-decisive variant (lexicon-neutral + mark-shape classifier at tau): 9 candidates (accent 7, breathing 2); not folded into accepted.


## Outcomes by rule (all waves)

| rule | candidates | accepted | abstained | rejected | excluded |
|---|---:|---:|---:|---:|---:|
| breathing | 106 | 4 | 0 | 70 | 32 |
| accent | 210 | 13 | 0 | 145 | 52 |
| subscript | 40 | 2 | 0 | 33 | 5 |
| marks_multi | 26 | 0 | 0 | 18 | 8 |
| final_grave | 112 | 44 | 32 | 8 | 28 |
| base_sub | 46 | 4 | 1 | 28 | 13 |
| constraint | 24 | 9 | 0 | 15 | 0 |

## Abstention / rejection reasons

| reason | n |
|---|---:|
| excluded:proper_name | 106 |
| model_form_unattested | 59 |
| model_form_unattested + abstain:localisation_uncertain | 32 |
| both_attested | 31 |
| excluded:hyphen_line_end | 24 |
| both_attested + above_count | 23 |
| abstain:localisation_uncertain | 20 |
| both_attested + abstain:localisation_uncertain | 18 |
| model_form_unattested + abstain:clipped_top_no_false_absence | 14 |
| both_attested + abstain:merged_marks | 11 |
| model_form_unattested + abstain:merged_marks | 10 |
| model_form_unattested + above_count | 10 |
| abstain:needs_one_oblique | 9 |
| model_form_unattested + abstain:neighbouring_marks | 8 |
| slope_disagrees | 8 |
| both_attested + abstain:clipped_top_no_false_absence | 8 |
| model_form_unattested + abstain:removal_with_wide_blob | 6 |
| abstain:final_grave_before_punctuation | 6 |
| both_attested + abstain:neighbouring_marks | 6 |
| both_attested + abstain:needs_one_oblique | 5 |
| model_form_unattested + abstain:clipped_bottom | 5 |
| abstain:faint_mark | 5 |
| excluded:all_caps_marks | 5 |
| model_form_unattested + abstain:faint_mark | 4 |
| above_count | 4 |
| both_attested + abstain:removal_with_wide_blob | 4 |
| model_form_unattested + blob_below_but_model_has_none | 3 |
| both_attested + abstain:clipped_bottom | 3 |
| violates:C1:missing_initial_breathing + abstain:localisation_uncertain | 2 |
| rejected:polytonic_mark_in_monotonic_regime | 2 |
| both_attested + oblique_but_model_has_circumflex | 2 |
| model_form_unattested + abstain:clipped_top | 2 |
| violates:C1:missing_initial_breathing + above_count | 2 |
| both_attested + blob_below_but_model_has_none | 2 |
| model_form_unattested + abstain:needs_one_oblique | 2 |
| excluded:abbreviation | 2 |
| violates:C3:two_accents + abstain:removal_with_wide_blob | 2 |
| both_attested + slope_disagrees | 2 |
| violates:C1:missing_initial_breathing + abstain:merged_marks | 2 |
| abstain:merged_marks | 1 |
| violates:C4:circumflex_before_penult + above_count | 1 |
| model_form_unattested + slope_disagrees | 1 |
| abstain:google_letters_attested_with_other_marks | 1 |
| excluded:latin_or_digit | 1 |
| both_attested + abstain:clipped_top | 1 |
| violates:C1:missing_initial_breathing + abstain:faint_mark | 1 |
| violates:C3:two_accents+C4:circumflex_before_penult + abstain:removal_with_wide_blob | 1 |
| violates:C3:two_accents + abstain:localisation_uncertain | 1 |
| abstain:clipped_bottom | 1 |
| model_form_unattested + no_blob_below | 1 |
| violates:C1:breathing_after_consonant_start + abstain:merged_marks | 1 |
| margin_below_20x + abstain:merged_marks | 1 |
| both_attested + no_blob_below | 1 |
| oblique_but_model_has_circumflex | 1 |
| margin_below_20x + abstain:clipped_bottom | 1 |
| margin_below_20x | 1 |
| violates:C1:missing_initial_breathing + abstain:neighbouring_marks | 1 |
| violates:C3:two_accents + abstain:merged_marks | 1 |
