# Validation on the three-way Wikisource lines

Truth = the human Wikisource transcription; label = Google Document AI; reading = our recogniser (E3 `full` arm, seeds 0 and 1, same crops). A candidate is a Google word the model reads differently with a single allowed difference. `accepted` = the pipeline would rewrite the label. Outcome of an accepted correction: `= human` (correct), `Google right` (a false correction, the label was right), `human ≠ both` (the label was wrong but so is the correction).

LB95 = exact one-sided 95 % lower confidence bound on precision (Clopper–Pearson; 90/100 → 83.6 %, 99/100 → 95.3 %, 100/100 → 97.1 %). Net edits = Levenshtein edits removed minus edits introduced over accepted corrections (word cores, NFD codepoints). A rule is a **release candidate** only if LB95 ≥ 99 % AND net edits > 0 AND no regime has ≥ 2 false corrections; otherwise it is **proposal-only**.

Book separation: thresholds were set while inspecting lines of 3 books (dev): wikisource:8b6b0de9, wikisource:02a3a2a6, wikisource:2793d64c. "held-out" = all other books.

## Seed 0, lexicon policy `ratio`

Lines: 1264 (dev 598, held-out 666); Google = model on 947 lines (agreement control: of those, 351 still differ from the human text and are unreachable by this method); Google = human on 691; model = human on 673.

Candidates: 214; truth known for 211 (the human line could not be word-aligned for the rest).

### Per rule — all books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 51 | 13 | 0 | 37 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 72 | 18 | 0 | 50 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |
| subscript | 35 | 1 | 0 | 32 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| dialytika | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 11 | 4 | 0 | 7 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 28 | 4 | 9 | 0 | 15 | 14 | 0 | 1 | 93.3% | 72.1% | +14 |
| base_sub | 7 | 1 | 0 | 6 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 9 | 0 | 0 | 8 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 214 | 42 | 9 | 140 | 23 | 22 | 0 | 1 | 95.7% | 81.0% | +22 |

### Per rule — dev books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 8 | 4 | 0 | 4 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| accent | 23 | 4 | 0 | 17 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 21 | 0 | 0 | 19 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| marks_multi | 5 | 3 | 0 | 2 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 21 | 1 | 9 | 0 | 11 | 10 | 0 | 1 | 90.9% | 63.6% | +10 |
| base_sub | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| **all** | 80 | 12 | 9 | 44 | 15 | 14 | 0 | 1 | 93.3% | 72.1% | +14 |

### Per rule — held-out books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 43 | 9 | 0 | 33 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 49 | 14 | 0 | 33 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 14 | 1 | 0 | 13 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| dialytika | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 6 | 1 | 0 | 5 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 7 | 3 | 0 | 0 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |
| base_sub | 6 | 1 | 0 | 5 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 8 | 0 | 0 | 7 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 134 | 30 | 0 | 96 | 8 | 8 | 0 | 0 | 100.0% | 68.8% | +8 |

### Release-candidate verdicts (held-out books)

| rule | accepted | LB95 | net edits | systematic failure | verdict |
|---|---:|---:|---:|---|---|
| breathing | 1 | 5.0% | +1 | none | proposal-only |
| accent | 2 | 22.4% | +2 | none | proposal-only |
| subscript | 0 | 0.0% | +0 | none | proposal-only |
| dialytika | 0 | 0.0% | +0 | none | proposal-only |
| marks_multi | 0 | 0.0% | +0 | none | proposal-only |
| final_grave | 4 | 47.3% | +4 | none | proposal-only |
| base_sub | 0 | 0.0% | +0 | none | proposal-only |
| constraint | 1 | 5.0% | +1 | none | proposal-only |

### Ablations (all books; accepted = known-truth candidates passing the stage)

| rule | stage | accepted | = human | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|
| breathing | model_only | 38 | 20 | 52.6% | 38.2% | +4 |
| breathing | model+lexicon | 7 | 6 | 85.7% | 47.9% | +5 |
| breathing | model+ink | 11 | 9 | 81.8% | 53.0% | +7 |
| breathing | full | 1 | 1 | 100.0% | 5.0% | +1 |
| accent | model_only | 54 | 22 | 40.7% | 29.4% | -5 |
| accent | model+lexicon | 9 | 8 | 88.9% | 57.1% | +8 |
| accent | model+ink | 11 | 9 | 81.8% | 53.0% | +8 |
| accent | full | 4 | 4 | 100.0% | 47.3% | +4 |
| subscript | model_only | 33 | 20 | 60.6% | 44.8% | +11 |
| subscript | model+lexicon | 6 | 5 | 83.3% | 41.8% | +6 |
| subscript | model+ink | 6 | 5 | 83.3% | 41.8% | +4 |
| subscript | full | 2 | 2 | 100.0% | 22.4% | +2 |
| dialytika | model_only | 0 | 0 | - | 0.0% | +0 |
| dialytika | model+lexicon | 0 | 0 | - | 0.0% | +0 |
| dialytika | model+ink | 0 | 0 | - | 0.0% | +0 |
| dialytika | full | 0 | 0 | - | 0.0% | +0 |
| marks_multi | model_only | 7 | 1 | 14.3% | 0.7% | -5 |
| marks_multi | model+lexicon | 0 | 0 | - | 0.0% | +0 |
| marks_multi | model+ink | 2 | 0 | 0.0% | 0.0% | -1 |
| marks_multi | full | 0 | 0 | - | 0.0% | +0 |
| final_grave | model_only | 24 | 22 | 91.7% | 76.0% | +21 |
| final_grave | model+lexicon | 15 | 14 | 93.3% | 72.1% | +14 |
| final_grave | model+ink | 15 | 14 | 93.3% | 72.1% | +14 |
| final_grave | full | 15 | 14 | 93.3% | 72.1% | +14 |
| base_sub | model_only | 6 | 1 | 16.7% | 0.9% | -3 |
| base_sub | model+lexicon | 0 | 0 | - | 0.0% | +0 |
| base_sub | model+ink | 0 | 0 | - | 0.0% | +0 |
| base_sub | full | 0 | 0 | - | 0.0% | +0 |
| constraint | model_only | 8 | 8 | 100.0% | 68.8% | +12 |
| constraint | model+lexicon | 5 | 5 | 100.0% | 54.9% | +9 |
| constraint | model+ink | 1 | 1 | 100.0% | 5.0% | +1 |
| constraint | full | 1 | 1 | 100.0% | 5.0% | +1 |
| all | model_only | 170 | 94 | 55.3% | 48.7% | +35 |
| all | model+lexicon | 42 | 38 | 90.5% | 79.5% | +42 |
| all | model+ink | 46 | 38 | 82.6% | 70.8% | +33 |
| all | full | 23 | 22 | 95.7% | 81.0% | +22 |

### Agreement with the human text (mark rules with both verdicts; outcome known as model-right or Google-right)

| witness says "model" | n | model = human | Google = human | agreement |
|---|---:|---:|---:|---:|
| lexicon alone | 25 | 24 | 1 | 96.0% |
| ink alone | 29 | 24 | 5 | 82.8% |
| lexicon AND ink | 7 | 7 | 0 | 100.0% |
| neither (lexicon no, ink no) | 83 | 30 | 53 | 36.1% |

### Per-mark recovery (TP / FP / recall), all books

| rule (Google→human diff) | recoverable Google errors | recovered (TP) | FP (accepted, ≠ human) | recall | precision |
|---|---:|---:|---:|---:|---:|
| breathing | 45 | 2 | 0 | 4.4% | 100.0% |
| accent | 48 | 4 | 0 | 8.3% | 100.0% |
| subscript | 30 | 2 | 0 | 6.7% | 100.0% |
| dialytika | 1 | 0 | 0 | 0.0% | - |
| marks_multi | 16 | 0 | 0 | 0.0% | - |
| final_grave | 49 | 14 | 0 | 28.6% | 100.0% |
| base_sub | 4 | 0 | 0 | 0.0% | - |
| **all** | 193 | 22 | 0 | 11.4% | 100.0% |

### Reader-agreement strata (all candidates, by rule)

| rule | model = human | Google = human | all different | unknown | accepted: model = human | accepted: Google = human | accepted: all different |
|---|---:|---:|---:|---:|---:|---:|---:|
| breathing | 25 | 23 | 2 | 1 | 1 | 0 | 0 |
| accent | 25 | 38 | 9 | 0 | 4 | 0 | 0 |
| subscript | 20 | 12 | 2 | 1 | 2 | 0 | 0 |
| dialytika | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| marks_multi | 3 | 4 | 4 | 0 | 0 | 0 | 0 |
| final_grave | 25 | 2 | 1 | 0 | 14 | 0 | 1 |
| base_sub | 2 | 4 | 1 | 0 | 0 | 0 | 0 |
| constraint | 8 | 0 | 0 | 1 | 1 | 0 | 0 |

### Accepted corrections by direction

| direction | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| add | subscript | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| add | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| change | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| change | accent | 4 | 4 | 0 | 100.0% | 47.3% | +4 |
| change | final_grave | 15 | 14 | 0 | 93.3% | 72.1% | +14 |

### Accepted corrections by regime

| regime | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| poly19 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| poly19 | accent | 4 | 4 | 0 | 100.0% | 47.3% | +4 |
| poly19 | subscript | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| poly19 | final_grave | 15 | 14 | 0 | 93.3% | 72.1% | +14 |
| poly19 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |

### Accepted corrections by book

| book | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| wikisource:02a3a2a6 | final_grave | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:2793d64c | subscript | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | final_grave | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:384c3f89 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:51fe7386 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:51fe7386 | final_grave | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:8b6b0de9 | accent | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:8b6b0de9 | subscript | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:8b6b0de9 | final_grave | 10 | 9 | 0 | 90.0% | 60.6% | +9 |

### Accepted corrections by line length (words)

| words | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| 4-7 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| 4-7 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| 4-7 | subscript | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| 4-7 | final_grave | 12 | 11 | 0 | 91.7% | 66.1% | +11 |
| 4-7 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| <=3 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| <=3 | final_grave | 3 | 3 | 0 | 100.0% | 36.8% | +3 |
| >=8 | accent | 2 | 2 | 0 | 100.0% | 22.4% | +2 |

### Abstention and rejection reasons (all candidates)

| reason | n | of which model = human | Google = human |
|---|---:|---:|---:|
| excluded:proper_name | 37 | 14 | 17 |
| model_form_unattested | 19 | 9 | 7 |
| model_form_unattested + abstain:localisation_uncertain | 12 | 0 | 11 |
| margin_below_20x | 9 | 8 | 1 |
| margin_below_20x + abstain:merged_marks | 9 | 4 | 4 |
| model_form_unattested + above_count | 9 | 3 | 5 |
| model_form_unattested + abstain:merged_marks | 9 | 0 | 9 |
| abstain:final_grave_before_punctuation | 7 | 7 | 0 |
| model_form_unattested + abstain:neighbouring_marks | 5 | 3 | 2 |
| model_form_unattested + abstain:needs_one_oblique | 5 | 0 | 5 |
| margin_below_20x + abstain:clipped_bottom | 5 | 3 | 1 |
| margin_below_20x + abstain:localisation_uncertain | 5 | 4 | 1 |
| model_form_unattested + abstain:clipped_bottom | 4 | 3 | 1 |
| abstain:localisation_uncertain | 4 | 3 | 1 |
| model_form_unattested + blob_below_but_model_has_none | 4 | 0 | 4 |
| model_form_unattested + abstain:removal_with_wide_blob | 4 | 1 | 3 |
| margin_below_20x + above_count | 4 | 1 | 2 |
| excluded:all_caps_marks | 4 | 1 | 1 |
| margin_below_20x + oblique_but_model_has_circumflex | 4 | 4 | 0 |
| above_count | 3 | 3 | 0 |
| margin_below_20x + abstain:removal_with_wide_blob | 3 | 0 | 1 |
| abstain:merged_marks | 3 | 3 | 0 |
| abstain:clipped_bottom | 2 | 1 | 0 |
| violates:C4:circumflex_before_penult + abstain:localisation_uncertain | 2 | 1 | 0 |
| abstain:neighbouring_marks | 2 | 2 | 0 |
| margin_below_20x + abstain:neighbouring_marks | 2 | 2 | 0 |
| violates:C1:missing_initial_breathing + abstain:neighbouring_marks | 2 | 2 | 0 |
| model_form_unattested + abstain:clipped_top_no_false_absence | 2 | 0 | 2 |
| violates:C1:breathing_after_consonant_start + abstain:removal_with_wide_blob | 1 | 1 | 0 |
| violates:C3:two_accents + abstain:localisation_uncertain | 1 | 1 | 0 |
| abstain:faint_mark | 1 | 0 | 1 |
| excluded:hyphen_line_end | 1 | 0 | 1 |
| margin_below_50x | 1 | 0 | 1 |
| violates:C1:missing_initial_breathing + abstain:merged_marks | 1 | 1 | 0 |
| model_form_unattested + no_blob_below | 1 | 0 | 1 |
| violates:C1:missing_initial_breathing + abstain:localisation_uncertain | 1 | 1 | 0 |
| oblique_but_model_has_circumflex | 1 | 1 | 0 |
| margin_below_20x + abstain:clipped_top_no_false_absence | 1 | 0 | 1 |
| abstain:removal_with_wide_blob | 1 | 0 | 0 |

### Physical controls (candidates on lines with the property)

| property | lines | candidates | accepted | = human | Google right (FP) |
|---|---:|---:|---:|---:|---:|
| clipped | 450 | 104 | 9 | 9 | 0 |
| specks | 71 | 10 | 0 | 0 | 0 |
| faint_ink | 40 | 6 | 0 | 0 | 0 |
| neighbour_ink | 207 | 43 | 3 | 3 | 0 |
| long | 432 | 86 | 7 | 7 | 0 |

### Ink-decisive variant (lexicon-neutral candidates; `markshape_model.json`, tau = 99 % held-out precision)

Lexicon-neutral mark candidates: 112; ink-decisive among them: 4.

| rule | lexicon-neutral | ink_decisive | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 23 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| accent | 37 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 15 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| dialytika | 1 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 7 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 26 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 3 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| all | 112 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |

Why lexicon-neutral candidates were not ink-decisive:  50, ink_conjunction:abstain:merged_marks 11, no_shape_model 8, ink_conjunction:above_count 7, ink_conjunction:abstain:clipped_bottom 6, ink_conjunction:abstain:neighbouring_marks 6, shape_below_tau 5, ink_conjunction:abstain:removal_with_wide_blob 4, ink_conjunction:oblique_but_model_has_circumflex 4, shape_predicts_psili 2, attached_breathing_not_decisive 1, model_marks_outside_scheme 1, ink_conjunction:blob_below_but_model_has_none 1, shape_predicts_acute 1, ink_conjunction:abstain:clipped_top_no_false_absence 1.

Recall of the 193 recoverable Google mark errors: rules 22 (11.4%); rules + ink_decisive 26 (13.5%).

### Ceiling analysis of the recoverable Google mark errors

| class | n | share |
|---|---:|---:|
| model wrong (unreachable without a better model) | 84 | 43.5% |
| model right, lexicon neutral, ink not decisive | 33 | 17.1% |
| model right, accepted by the rules | 22 | 11.4% |
| model right, ink conjunction fails | 17 | 8.8% |
| model right, excluded by a guard | 15 | 7.8% |
| model right, lexicon contradicts | 10 | 5.2% |
| model right, abstained (ink unreadable / regime) | 8 | 4.1% |
| model right, lexicon neutral, ink decisive | 4 | 2.1% |

### Policy defaults (3a line-initial capitals, 3b acute house style)

3a: line-initial capitalised words admitted (lower-cased model form attested ≥ 50, not in the proper-name list): 4 candidates, 1 accepted, 1 = human, 0 Google right.

3b: pages flagged as acute-everywhere (share of word-final acute > 0.8 over ≥ 10 accented final syllables in the Google text): 0 pages carrying 0 candidates; final_grave corrections suppressed on them: 0 (0 would have matched the human text, 0 would have been false).

### Orthographic constraints (polytonic-regime lines; `constraints.py`)

Google words checked: 6124; violating a hard constraint: 35 (0.6%); of those, the human form is itself impossible (constraint too strict or human error): 14; Google = human although "impossible": 14; the model's form is possible: 17, of which model = human: 14.

| violation | Google words | model possible | model = human | Google = human |
|---|---:|---:|---:|---:|
| C3:two_accents | 12 | 2 | 2 | 10 |
| C1:missing_initial_breathing | 11 | 9 | 7 | 0 |
| C4:accent_before_antepenult | 5 | 1 | 1 | 4 |
| C4:circumflex_before_penult | 4 | 3 | 2 | 0 |
| C1:several_breathings | 3 | 3 | 3 | 0 |
| C1:breathing_after_consonant_start | 2 | 1 | 1 | 1 |
| C4:grave_not_final | 1 | 0 | 0 | 0 |

Rule `constraint` (single allowed mark difference, Google impossible, model possible, ink agrees): candidates 9, accepted 1, = human 1, Google right 0, human ≠ both 0, precision 100.0%, LB95 5.0%, net edits +1; overlap with the lexicon rules: 0 of the 1 accepted would also pass the lexicon (the other 1 are corrections the lexicon alone could not make).

Accepted by underlying mark category: breathing 1.

### Accepted corrections that do not match the human text (1)

| rule | book | Google | proposed | human | crop |
|---|---|---|---|---|---|
| final_grave | wikisource:8b6b0de9 | φωλεά | φωλεὰ | φωλέα | `docs/records/harvest/harvest_big/wikisource/crops/8b6b0de9/p000016-l0013.png` |

## Seed 0, lexicon policy `strict`

Lines: 1264 (dev 598, held-out 666); Google = model on 947 lines (agreement control: of those, 351 still differ from the human text and are unreachable by this method); Google = human on 691; model = human on 673.

Candidates: 214; truth known for 211 (the human line could not be word-aligned for the rest).

### Per rule — all books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 51 | 13 | 0 | 37 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 72 | 18 | 0 | 50 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |
| subscript | 35 | 1 | 0 | 32 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| dialytika | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 11 | 4 | 0 | 7 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 28 | 4 | 9 | 0 | 15 | 14 | 0 | 1 | 93.3% | 72.1% | +14 |
| base_sub | 7 | 1 | 0 | 6 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 9 | 0 | 0 | 8 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 214 | 42 | 9 | 140 | 23 | 22 | 0 | 1 | 95.7% | 81.0% | +22 |

### Per rule — dev books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 8 | 4 | 0 | 4 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| accent | 23 | 4 | 0 | 17 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 21 | 0 | 0 | 19 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| marks_multi | 5 | 3 | 0 | 2 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 21 | 1 | 9 | 0 | 11 | 10 | 0 | 1 | 90.9% | 63.6% | +10 |
| base_sub | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| **all** | 80 | 12 | 9 | 44 | 15 | 14 | 0 | 1 | 93.3% | 72.1% | +14 |

### Per rule — held-out books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 43 | 9 | 0 | 33 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 49 | 14 | 0 | 33 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 14 | 1 | 0 | 13 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| dialytika | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 6 | 1 | 0 | 5 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 7 | 3 | 0 | 0 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |
| base_sub | 6 | 1 | 0 | 5 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 8 | 0 | 0 | 7 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 134 | 30 | 0 | 96 | 8 | 8 | 0 | 0 | 100.0% | 68.8% | +8 |

### Release-candidate verdicts (held-out books)

| rule | accepted | LB95 | net edits | systematic failure | verdict |
|---|---:|---:|---:|---|---|
| breathing | 1 | 5.0% | +1 | none | proposal-only |
| accent | 2 | 22.4% | +2 | none | proposal-only |
| subscript | 0 | 0.0% | +0 | none | proposal-only |
| dialytika | 0 | 0.0% | +0 | none | proposal-only |
| marks_multi | 0 | 0.0% | +0 | none | proposal-only |
| final_grave | 4 | 47.3% | +4 | none | proposal-only |
| base_sub | 0 | 0.0% | +0 | none | proposal-only |
| constraint | 1 | 5.0% | +1 | none | proposal-only |

### Ablations (all books; accepted = known-truth candidates passing the stage)

| rule | stage | accepted | = human | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|
| breathing | model_only | 38 | 20 | 52.6% | 38.2% | +4 |
| breathing | model+lexicon | 7 | 6 | 85.7% | 47.9% | +5 |
| breathing | model+ink | 11 | 9 | 81.8% | 53.0% | +7 |
| breathing | full | 1 | 1 | 100.0% | 5.0% | +1 |
| accent | model_only | 54 | 22 | 40.7% | 29.4% | -5 |
| accent | model+lexicon | 9 | 8 | 88.9% | 57.1% | +8 |
| accent | model+ink | 11 | 9 | 81.8% | 53.0% | +8 |
| accent | full | 4 | 4 | 100.0% | 47.3% | +4 |
| subscript | model_only | 33 | 20 | 60.6% | 44.8% | +11 |
| subscript | model+lexicon | 6 | 5 | 83.3% | 41.8% | +6 |
| subscript | model+ink | 6 | 5 | 83.3% | 41.8% | +4 |
| subscript | full | 2 | 2 | 100.0% | 22.4% | +2 |
| dialytika | model_only | 0 | 0 | - | 0.0% | +0 |
| dialytika | model+lexicon | 0 | 0 | - | 0.0% | +0 |
| dialytika | model+ink | 0 | 0 | - | 0.0% | +0 |
| dialytika | full | 0 | 0 | - | 0.0% | +0 |
| marks_multi | model_only | 7 | 1 | 14.3% | 0.7% | -5 |
| marks_multi | model+lexicon | 0 | 0 | - | 0.0% | +0 |
| marks_multi | model+ink | 2 | 0 | 0.0% | 0.0% | -1 |
| marks_multi | full | 0 | 0 | - | 0.0% | +0 |
| final_grave | model_only | 24 | 22 | 91.7% | 76.0% | +21 |
| final_grave | model+lexicon | 15 | 14 | 93.3% | 72.1% | +14 |
| final_grave | model+ink | 15 | 14 | 93.3% | 72.1% | +14 |
| final_grave | full | 15 | 14 | 93.3% | 72.1% | +14 |
| base_sub | model_only | 6 | 1 | 16.7% | 0.9% | -3 |
| base_sub | model+lexicon | 0 | 0 | - | 0.0% | +0 |
| base_sub | model+ink | 0 | 0 | - | 0.0% | +0 |
| base_sub | full | 0 | 0 | - | 0.0% | +0 |
| constraint | model_only | 8 | 8 | 100.0% | 68.8% | +12 |
| constraint | model+lexicon | 5 | 5 | 100.0% | 54.9% | +9 |
| constraint | model+ink | 1 | 1 | 100.0% | 5.0% | +1 |
| constraint | full | 1 | 1 | 100.0% | 5.0% | +1 |
| all | model_only | 170 | 94 | 55.3% | 48.7% | +35 |
| all | model+lexicon | 42 | 38 | 90.5% | 79.5% | +42 |
| all | model+ink | 46 | 38 | 82.6% | 70.8% | +33 |
| all | full | 23 | 22 | 95.7% | 81.0% | +22 |

### Agreement with the human text (mark rules with both verdicts; outcome known as model-right or Google-right)

| witness says "model" | n | model = human | Google = human | agreement |
|---|---:|---:|---:|---:|
| lexicon alone | 25 | 24 | 1 | 96.0% |
| ink alone | 29 | 24 | 5 | 82.8% |
| lexicon AND ink | 7 | 7 | 0 | 100.0% |
| neither (lexicon no, ink no) | 83 | 30 | 53 | 36.1% |

### Per-mark recovery (TP / FP / recall), all books

| rule (Google→human diff) | recoverable Google errors | recovered (TP) | FP (accepted, ≠ human) | recall | precision |
|---|---:|---:|---:|---:|---:|
| breathing | 45 | 2 | 0 | 4.4% | 100.0% |
| accent | 48 | 4 | 0 | 8.3% | 100.0% |
| subscript | 30 | 2 | 0 | 6.7% | 100.0% |
| dialytika | 1 | 0 | 0 | 0.0% | - |
| marks_multi | 16 | 0 | 0 | 0.0% | - |
| final_grave | 49 | 14 | 0 | 28.6% | 100.0% |
| base_sub | 4 | 0 | 0 | 0.0% | - |
| **all** | 193 | 22 | 0 | 11.4% | 100.0% |

### Reader-agreement strata (all candidates, by rule)

| rule | model = human | Google = human | all different | unknown | accepted: model = human | accepted: Google = human | accepted: all different |
|---|---:|---:|---:|---:|---:|---:|---:|
| breathing | 25 | 23 | 2 | 1 | 1 | 0 | 0 |
| accent | 25 | 38 | 9 | 0 | 4 | 0 | 0 |
| subscript | 20 | 12 | 2 | 1 | 2 | 0 | 0 |
| dialytika | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| marks_multi | 3 | 4 | 4 | 0 | 0 | 0 | 0 |
| final_grave | 25 | 2 | 1 | 0 | 14 | 0 | 1 |
| base_sub | 2 | 4 | 1 | 0 | 0 | 0 | 0 |
| constraint | 8 | 0 | 0 | 1 | 1 | 0 | 0 |

### Accepted corrections by direction

| direction | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| add | subscript | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| add | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| change | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| change | accent | 4 | 4 | 0 | 100.0% | 47.3% | +4 |
| change | final_grave | 15 | 14 | 0 | 93.3% | 72.1% | +14 |

### Accepted corrections by regime

| regime | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| poly19 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| poly19 | accent | 4 | 4 | 0 | 100.0% | 47.3% | +4 |
| poly19 | subscript | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| poly19 | final_grave | 15 | 14 | 0 | 93.3% | 72.1% | +14 |
| poly19 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |

### Accepted corrections by book

| book | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| wikisource:02a3a2a6 | final_grave | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:2793d64c | subscript | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | final_grave | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:384c3f89 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:51fe7386 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:51fe7386 | final_grave | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:8b6b0de9 | accent | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:8b6b0de9 | subscript | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:8b6b0de9 | final_grave | 10 | 9 | 0 | 90.0% | 60.6% | +9 |

### Accepted corrections by line length (words)

| words | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| 4-7 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| 4-7 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| 4-7 | subscript | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| 4-7 | final_grave | 12 | 11 | 0 | 91.7% | 66.1% | +11 |
| 4-7 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| <=3 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| <=3 | final_grave | 3 | 3 | 0 | 100.0% | 36.8% | +3 |
| >=8 | accent | 2 | 2 | 0 | 100.0% | 22.4% | +2 |

### Abstention and rejection reasons (all candidates)

| reason | n | of which model = human | Google = human |
|---|---:|---:|---:|
| excluded:proper_name | 37 | 14 | 17 |
| model_form_unattested | 19 | 9 | 7 |
| model_form_unattested + abstain:localisation_uncertain | 12 | 0 | 11 |
| model_form_unattested + above_count | 9 | 3 | 5 |
| model_form_unattested + abstain:merged_marks | 9 | 0 | 9 |
| both_attested + abstain:merged_marks | 8 | 4 | 4 |
| abstain:final_grave_before_punctuation | 7 | 7 | 0 |
| both_attested | 6 | 4 | 2 |
| model_form_unattested + abstain:neighbouring_marks | 5 | 3 | 2 |
| model_form_unattested + abstain:needs_one_oblique | 5 | 0 | 5 |
| both_attested + abstain:localisation_uncertain | 5 | 4 | 1 |
| model_form_unattested + abstain:clipped_bottom | 4 | 3 | 1 |
| abstain:localisation_uncertain | 4 | 3 | 1 |
| model_form_unattested + blob_below_but_model_has_none | 4 | 0 | 4 |
| margin_below_20x | 4 | 4 | 0 |
| model_form_unattested + abstain:removal_with_wide_blob | 4 | 1 | 3 |
| both_attested + above_count | 4 | 1 | 2 |
| excluded:all_caps_marks | 4 | 1 | 1 |
| both_attested + oblique_but_model_has_circumflex | 4 | 4 | 0 |
| both_attested + abstain:clipped_bottom | 3 | 2 | 1 |
| above_count | 3 | 3 | 0 |
| both_attested + abstain:removal_with_wide_blob | 3 | 0 | 1 |
| abstain:merged_marks | 3 | 3 | 0 |
| abstain:clipped_bottom | 2 | 1 | 0 |
| margin_below_20x + abstain:clipped_bottom | 2 | 1 | 0 |
| violates:C4:circumflex_before_penult + abstain:localisation_uncertain | 2 | 1 | 0 |
| abstain:neighbouring_marks | 2 | 2 | 0 |
| both_attested + abstain:neighbouring_marks | 2 | 2 | 0 |
| violates:C1:missing_initial_breathing + abstain:neighbouring_marks | 2 | 2 | 0 |
| model_form_unattested + abstain:clipped_top_no_false_absence | 2 | 0 | 2 |
| violates:C1:breathing_after_consonant_start + abstain:removal_with_wide_blob | 1 | 1 | 0 |
| margin_below_20x + abstain:merged_marks | 1 | 0 | 0 |
| violates:C3:two_accents + abstain:localisation_uncertain | 1 | 1 | 0 |
| abstain:faint_mark | 1 | 0 | 1 |
| excluded:hyphen_line_end | 1 | 0 | 1 |
| violates:C1:missing_initial_breathing + abstain:merged_marks | 1 | 1 | 0 |
| model_form_unattested + no_blob_below | 1 | 0 | 1 |
| violates:C1:missing_initial_breathing + abstain:localisation_uncertain | 1 | 1 | 0 |
| oblique_but_model_has_circumflex | 1 | 1 | 0 |
| both_attested + abstain:clipped_top_no_false_absence | 1 | 0 | 1 |
| abstain:removal_with_wide_blob | 1 | 0 | 0 |

### Physical controls (candidates on lines with the property)

| property | lines | candidates | accepted | = human | Google right (FP) |
|---|---:|---:|---:|---:|---:|
| clipped | 450 | 104 | 9 | 9 | 0 |
| specks | 71 | 10 | 0 | 0 | 0 |
| faint_ink | 40 | 6 | 0 | 0 | 0 |
| neighbour_ink | 207 | 43 | 3 | 3 | 0 |
| long | 432 | 86 | 7 | 7 | 0 |

### Ink-decisive variant (lexicon-neutral candidates; `markshape_model.json`, tau = 99 % held-out precision)

Lexicon-neutral mark candidates: 112; ink-decisive among them: 4.

| rule | lexicon-neutral | ink_decisive | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 23 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| accent | 37 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 15 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| dialytika | 1 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 7 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 26 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 3 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| all | 112 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |

Why lexicon-neutral candidates were not ink-decisive:  50, ink_conjunction:abstain:merged_marks 11, no_shape_model 8, ink_conjunction:above_count 7, ink_conjunction:abstain:clipped_bottom 6, ink_conjunction:abstain:neighbouring_marks 6, shape_below_tau 5, ink_conjunction:abstain:removal_with_wide_blob 4, ink_conjunction:oblique_but_model_has_circumflex 4, shape_predicts_psili 2, attached_breathing_not_decisive 1, model_marks_outside_scheme 1, ink_conjunction:blob_below_but_model_has_none 1, shape_predicts_acute 1, ink_conjunction:abstain:clipped_top_no_false_absence 1.

Recall of the 193 recoverable Google mark errors: rules 22 (11.4%); rules + ink_decisive 26 (13.5%).

### Ceiling analysis of the recoverable Google mark errors

| class | n | share |
|---|---:|---:|
| model wrong (unreachable without a better model) | 84 | 43.5% |
| model right, lexicon neutral, ink not decisive | 33 | 17.1% |
| model right, accepted by the rules | 22 | 11.4% |
| model right, ink conjunction fails | 17 | 8.8% |
| model right, excluded by a guard | 15 | 7.8% |
| model right, lexicon contradicts | 10 | 5.2% |
| model right, abstained (ink unreadable / regime) | 8 | 4.1% |
| model right, lexicon neutral, ink decisive | 4 | 2.1% |

### Policy defaults (3a line-initial capitals, 3b acute house style)

3a: line-initial capitalised words admitted (lower-cased model form attested ≥ 50, not in the proper-name list): 4 candidates, 1 accepted, 1 = human, 0 Google right.

3b: pages flagged as acute-everywhere (share of word-final acute > 0.8 over ≥ 10 accented final syllables in the Google text): 0 pages carrying 0 candidates; final_grave corrections suppressed on them: 0 (0 would have matched the human text, 0 would have been false).

### Orthographic constraints (polytonic-regime lines; `constraints.py`)

Google words checked: 6124; violating a hard constraint: 35 (0.6%); of those, the human form is itself impossible (constraint too strict or human error): 14; Google = human although "impossible": 14; the model's form is possible: 17, of which model = human: 14.

| violation | Google words | model possible | model = human | Google = human |
|---|---:|---:|---:|---:|
| C3:two_accents | 12 | 2 | 2 | 10 |
| C1:missing_initial_breathing | 11 | 9 | 7 | 0 |
| C4:accent_before_antepenult | 5 | 1 | 1 | 4 |
| C4:circumflex_before_penult | 4 | 3 | 2 | 0 |
| C1:several_breathings | 3 | 3 | 3 | 0 |
| C1:breathing_after_consonant_start | 2 | 1 | 1 | 1 |
| C4:grave_not_final | 1 | 0 | 0 | 0 |

Rule `constraint` (single allowed mark difference, Google impossible, model possible, ink agrees): candidates 9, accepted 1, = human 1, Google right 0, human ≠ both 0, precision 100.0%, LB95 5.0%, net edits +1; overlap with the lexicon rules: 0 of the 1 accepted would also pass the lexicon (the other 1 are corrections the lexicon alone could not make).

Accepted by underlying mark category: breathing 1.

### Accepted corrections that do not match the human text (1)

| rule | book | Google | proposed | human | crop |
|---|---|---|---|---|---|
| final_grave | wikisource:8b6b0de9 | φωλεά | φωλεὰ | φωλέα | `docs/records/harvest/harvest_big/wikisource/crops/8b6b0de9/p000016-l0013.png` |

## Seed 1, lexicon policy `ratio`

Lines: 1264 (dev 598, held-out 666); Google = model on 961 lines (agreement control: of those, 353 still differ from the human text and are unreachable by this method); Google = human on 691; model = human on 673.

Candidates: 197; truth known for 193 (the human line could not be word-aligned for the rest).

### Per rule — all books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 44 | 14 | 0 | 29 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 60 | 10 | 0 | 46 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |
| subscript | 29 | 1 | 0 | 28 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 17 | 6 | 0 | 11 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 33 | 6 | 11 | 0 | 16 | 15 | 0 | 1 | 93.8% | 73.6% | +15 |
| base_sub | 7 | 1 | 0 | 6 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 7 | 0 | 0 | 6 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 197 | 38 | 11 | 126 | 22 | 21 | 0 | 1 | 95.5% | 80.2% | +21 |

### Per rule — dev books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 10 | 5 | 0 | 5 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| accent | 22 | 5 | 0 | 15 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 13 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 6 | 4 | 0 | 2 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 23 | 2 | 8 | 0 | 13 | 12 | 0 | 1 | 92.3% | 68.4% | +12 |
| constraint | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| **all** | 75 | 16 | 8 | 36 | 15 | 14 | 0 | 1 | 93.3% | 72.1% | +14 |

### Per rule — held-out books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 34 | 9 | 0 | 24 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 38 | 5 | 0 | 31 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 16 | 1 | 0 | 15 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 11 | 2 | 0 | 9 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 10 | 4 | 3 | 0 | 3 | 3 | 0 | 0 | 100.0% | 36.8% | +3 |
| base_sub | 7 | 1 | 0 | 6 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 6 | 0 | 0 | 5 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 122 | 22 | 3 | 90 | 7 | 7 | 0 | 0 | 100.0% | 65.2% | +7 |

### Release-candidate verdicts (held-out books)

| rule | accepted | LB95 | net edits | systematic failure | verdict |
|---|---:|---:|---:|---|---|
| breathing | 1 | 5.0% | +1 | none | proposal-only |
| accent | 2 | 22.4% | +2 | none | proposal-only |
| subscript | 0 | 0.0% | +0 | none | proposal-only |
| marks_multi | 0 | 0.0% | +0 | none | proposal-only |
| final_grave | 3 | 36.8% | +3 | none | proposal-only |
| base_sub | 0 | 0.0% | +0 | none | proposal-only |
| constraint | 1 | 5.0% | +1 | none | proposal-only |

### Ablations (all books; accepted = known-truth candidates passing the stage)

| rule | stage | accepted | = human | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|
| breathing | model_only | 30 | 12 | 40.0% | 25.0% | -4 |
| breathing | model+lexicon | 4 | 4 | 100.0% | 47.3% | +4 |
| breathing | model+ink | 10 | 6 | 60.0% | 30.4% | +2 |
| breathing | full | 1 | 1 | 100.0% | 5.0% | +1 |
| accent | model_only | 50 | 16 | 32.0% | 21.2% | -11 |
| accent | model+lexicon | 10 | 10 | 100.0% | 74.1% | +10 |
| accent | model+ink | 11 | 9 | 81.8% | 53.0% | +7 |
| accent | full | 4 | 4 | 100.0% | 47.3% | +4 |
| subscript | model_only | 27 | 15 | 55.6% | 38.2% | +5 |
| subscript | model+lexicon | 4 | 3 | 75.0% | 24.9% | +4 |
| subscript | model+ink | 1 | 1 | 100.0% | 5.0% | +1 |
| subscript | full | 0 | 0 | - | 0.0% | +0 |
| marks_multi | model_only | 11 | 2 | 18.2% | 3.3% | +0 |
| marks_multi | model+lexicon | 1 | 1 | 100.0% | 5.0% | +2 |
| marks_multi | model+ink | 1 | 0 | 0.0% | 0.0% | -1 |
| marks_multi | full | 0 | 0 | - | 0.0% | +0 |
| final_grave | model_only | 27 | 26 | 96.3% | 83.6% | +26 |
| final_grave | model+lexicon | 16 | 15 | 93.8% | 73.6% | +15 |
| final_grave | model+ink | 16 | 15 | 93.8% | 73.6% | +15 |
| final_grave | full | 16 | 15 | 93.8% | 73.6% | +15 |
| base_sub | model_only | 6 | 2 | 33.3% | 6.3% | -2 |
| base_sub | model+lexicon | 0 | 0 | - | 0.0% | +0 |
| base_sub | model+ink | 0 | 0 | - | 0.0% | +0 |
| base_sub | full | 0 | 0 | - | 0.0% | +0 |
| constraint | model_only | 7 | 5 | 71.4% | 34.1% | +8 |
| constraint | model+lexicon | 2 | 2 | 100.0% | 22.4% | +3 |
| constraint | model+ink | 1 | 1 | 100.0% | 5.0% | +1 |
| constraint | full | 1 | 1 | 100.0% | 5.0% | +1 |
| all | model_only | 158 | 78 | 49.4% | 42.6% | +22 |
| all | model+lexicon | 37 | 35 | 94.6% | 83.9% | +38 |
| all | model+ink | 40 | 32 | 80.0% | 66.8% | +25 |
| all | full | 22 | 21 | 95.5% | 80.2% | +21 |

### Agreement with the human text (mark rules with both verdicts; outcome known as model-right or Google-right)

| witness says "model" | n | model = human | Google = human | agreement |
|---|---:|---:|---:|---:|
| lexicon alone | 20 | 20 | 0 | 100.0% |
| ink alone | 24 | 17 | 7 | 70.8% |
| lexicon AND ink | 5 | 5 | 0 | 100.0% |
| neither (lexicon no, ink no) | 69 | 18 | 51 | 26.1% |

### Per-mark recovery (TP / FP / recall), all books

| rule (Google→human diff) | recoverable Google errors | recovered (TP) | FP (accepted, ≠ human) | recall | precision |
|---|---:|---:|---:|---:|---:|
| breathing | 45 | 2 | 0 | 4.4% | 100.0% |
| accent | 48 | 4 | 0 | 8.3% | 100.0% |
| subscript | 30 | 0 | 0 | 0.0% | - |
| dialytika | 1 | 0 | 0 | 0.0% | - |
| marks_multi | 16 | 0 | 0 | 0.0% | - |
| final_grave | 49 | 15 | 0 | 30.6% | 100.0% |
| base_sub | 4 | 0 | 0 | 0.0% | - |
| **all** | 193 | 21 | 0 | 10.9% | 100.0% |

### Reader-agreement strata (all candidates, by rule)

| rule | model = human | Google = human | all different | unknown | accepted: model = human | accepted: Google = human | accepted: all different |
|---|---:|---:|---:|---:|---:|---:|---:|
| breathing | 16 | 23 | 4 | 1 | 1 | 0 | 0 |
| accent | 19 | 31 | 9 | 1 | 4 | 0 | 0 |
| subscript | 15 | 12 | 1 | 1 | 0 | 0 | 0 |
| marks_multi | 5 | 5 | 6 | 1 | 0 | 0 | 0 |
| final_grave | 30 | 2 | 1 | 0 | 15 | 0 | 1 |
| base_sub | 3 | 4 | 0 | 0 | 0 | 0 | 0 |
| constraint | 5 | 0 | 2 | 0 | 1 | 0 | 0 |

### Accepted corrections by direction

| direction | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| add | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| change | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| change | accent | 4 | 4 | 0 | 100.0% | 47.3% | +4 |
| change | final_grave | 16 | 15 | 0 | 93.8% | 73.6% | +15 |

### Accepted corrections by regime

| regime | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| poly19 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| poly19 | accent | 4 | 4 | 0 | 100.0% | 47.3% | +4 |
| poly19 | final_grave | 16 | 15 | 0 | 93.8% | 73.6% | +15 |
| poly19 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |

### Accepted corrections by book

| book | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| wikisource:02a3a2a6 | final_grave | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | final_grave | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:51fe7386 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:51fe7386 | final_grave | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:8b6b0de9 | accent | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:8b6b0de9 | final_grave | 12 | 11 | 0 | 91.7% | 66.1% | +11 |

### Accepted corrections by line length (words)

| words | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| 4-7 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| 4-7 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| 4-7 | final_grave | 11 | 10 | 0 | 90.9% | 63.6% | +10 |
| 4-7 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| <=3 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| <=3 | final_grave | 5 | 5 | 0 | 100.0% | 54.9% | +5 |
| >=8 | accent | 2 | 2 | 0 | 100.0% | 22.4% | +2 |

### Abstention and rejection reasons (all candidates)

| reason | n | of which model = human | Google = human |
|---|---:|---:|---:|
| excluded:proper_name | 34 | 14 | 14 |
| model_form_unattested | 14 | 6 | 8 |
| model_form_unattested + abstain:merged_marks | 14 | 0 | 12 |
| margin_below_20x | 10 | 7 | 3 |
| model_form_unattested + above_count | 10 | 1 | 8 |
| model_form_unattested + abstain:localisation_uncertain | 8 | 1 | 5 |
| margin_below_20x + abstain:merged_marks | 6 | 2 | 3 |
| abstain:final_grave_before_punctuation | 6 | 6 | 0 |
| margin_below_20x + abstain:clipped_bottom | 6 | 3 | 2 |
| model_form_unattested + abstain:clipped_bottom | 6 | 4 | 2 |
| model_form_unattested + abstain:removal_with_wide_blob | 5 | 1 | 3 |
| abstain:merged_marks | 4 | 4 | 0 |
| model_form_unattested + abstain:neighbouring_marks | 4 | 2 | 1 |
| abstain:localisation_uncertain | 4 | 4 | 0 |
| excluded:all_caps_marks | 4 | 1 | 1 |
| abstain:clipped_bottom | 3 | 2 | 0 |
| model_form_unattested + abstain:needs_one_oblique | 3 | 0 | 3 |
| above_count | 3 | 3 | 0 |
| margin_below_20x + abstain:localisation_uncertain | 3 | 0 | 1 |
| margin_below_20x + abstain:neighbouring_marks | 2 | 1 | 1 |
| abstain:needs_one_oblique | 2 | 2 | 0 |
| margin_below_20x + above_count | 2 | 1 | 1 |
| model_form_unattested + blob_below_but_model_has_none | 2 | 0 | 2 |
| margin_below_20x + slope_disagrees | 2 | 0 | 0 |
| oblique_but_model_has_circumflex | 2 | 2 | 0 |
| margin_below_20x + abstain:removal_with_wide_blob | 2 | 0 | 1 |
| violates:C1:breathing_after_consonant_start + abstain:removal_with_wide_blob | 1 | 1 | 0 |
| violates:C3:two_accents + abstain:localisation_uncertain | 1 | 1 | 0 |
| margin_below_20x + blob_below_but_model_has_none | 1 | 0 | 1 |
| margin_below_20x + abstain:needs_one_oblique | 1 | 0 | 1 |
| rejected:polytonic_mark_in_monotonic_regime | 1 | 0 | 0 |
| violates:C1:missing_initial_breathing + abstain:merged_marks | 1 | 0 | 0 |
| abstain:neighbouring_marks | 1 | 1 | 0 |
| model_form_unattested + abstain:faint_mark | 1 | 0 | 1 |
| model_form_unattested + abstain:clipped_top | 1 | 0 | 1 |
| margin_below_20x + abstain:faint_mark | 1 | 0 | 1 |
| violates:C1:missing_initial_breathing + abstain:removal_with_wide_blob | 1 | 0 | 0 |
| violates:C1:missing_initial_breathing + abstain:neighbouring_marks | 1 | 1 | 0 |
| violates:C4:circumflex_before_penult + above_count | 1 | 1 | 0 |
| margin_below_20x + abstain:clipped_top_no_false_absence | 1 | 0 | 1 |

### Physical controls (candidates on lines with the property)

| property | lines | candidates | accepted | = human | Google right (FP) |
|---|---:|---:|---:|---:|---:|
| clipped | 450 | 106 | 9 | 9 | 0 |
| specks | 71 | 12 | 0 | 0 | 0 |
| faint_ink | 40 | 6 | 0 | 0 | 0 |
| neighbour_ink | 207 | 42 | 3 | 3 | 0 |
| long | 432 | 83 | 6 | 6 | 0 |

### Ink-decisive variant (lexicon-neutral candidates; `markshape_model.json`, tau = 99 % held-out precision)

Lexicon-neutral mark candidates: 117; ink-decisive among them: 4.

| rule | lexicon-neutral | ink_decisive | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 21 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| accent | 36 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 16 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 10 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 30 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 4 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| all | 117 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |

Why lexicon-neutral candidates were not ink-decisive:  50, ink_conjunction:abstain:merged_marks 14, ink_conjunction:abstain:clipped_bottom 10, ink_conjunction:above_count 7, ink_conjunction:abstain:neighbouring_marks 6, ink_conjunction:abstain:removal_with_wide_blob 6, shape_below_tau 5, no_shape_model 4, ink_conjunction:abstain:needs_one_oblique 3, ink_conjunction:slope_disagrees 2, ink_conjunction:abstain:faint_mark 2, attached_breathing_not_decisive 1, shape_predicts_dasia 1, ink_conjunction:blob_below_but_model_has_none 1, ink_conjunction:abstain:clipped_top_no_false_absence 1.

Recall of the 193 recoverable Google mark errors: rules 21 (10.9%); rules + ink_decisive 25 (13.0%).

### Ceiling analysis of the recoverable Google mark errors

| class | n | share |
|---|---:|---:|
| model wrong (unreachable without a better model) | 100 | 51.8% |
| model right, accepted by the rules | 21 | 10.9% |
| model right, lexicon neutral, ink not decisive | 21 | 10.9% |
| model right, excluded by a guard | 15 | 7.8% |
| model right, ink conjunction fails | 14 | 7.3% |
| model right, abstained (ink unreadable / regime) | 11 | 5.7% |
| model right, lexicon contradicts | 7 | 3.6% |
| model right, lexicon neutral, ink decisive | 4 | 2.1% |

### Policy defaults (3a line-initial capitals, 3b acute house style)

3a: line-initial capitalised words admitted (lower-cased model form attested ≥ 50, not in the proper-name list): 3 candidates, 1 accepted, 1 = human, 0 Google right.

3b: pages flagged as acute-everywhere (share of word-final acute > 0.8 over ≥ 10 accented final syllables in the Google text): 0 pages carrying 0 candidates; final_grave corrections suppressed on them: 0 (0 would have matched the human text, 0 would have been false).

### Orthographic constraints (polytonic-regime lines; `constraints.py`)

Google words checked: 6124; violating a hard constraint: 35 (0.6%); of those, the human form is itself impossible (constraint too strict or human error): 14; Google = human although "impossible": 14; the model's form is possible: 16, of which model = human: 11.

| violation | Google words | model possible | model = human | Google = human |
|---|---:|---:|---:|---:|
| C3:two_accents | 12 | 2 | 1 | 10 |
| C1:missing_initial_breathing | 11 | 8 | 4 | 0 |
| C4:accent_before_antepenult | 5 | 1 | 1 | 4 |
| C4:circumflex_before_penult | 4 | 3 | 2 | 0 |
| C1:several_breathings | 3 | 3 | 2 | 0 |
| C1:breathing_after_consonant_start | 2 | 1 | 1 | 1 |
| C4:grave_not_final | 1 | 0 | 0 | 0 |

Rule `constraint` (single allowed mark difference, Google impossible, model possible, ink agrees): candidates 7, accepted 1, = human 1, Google right 0, human ≠ both 0, precision 100.0%, LB95 5.0%, net edits +1; overlap with the lexicon rules: 0 of the 1 accepted would also pass the lexicon (the other 1 are corrections the lexicon alone could not make).

Accepted by underlying mark category: breathing 1.

### Accepted corrections that do not match the human text (1)

| rule | book | Google | proposed | human | crop |
|---|---|---|---|---|---|
| final_grave | wikisource:8b6b0de9 | φωλεά | φωλεὰ | φωλέα | `docs/records/harvest/harvest_big/wikisource/crops/8b6b0de9/p000016-l0013.png` |

## Seed 1, lexicon policy `strict`

Lines: 1264 (dev 598, held-out 666); Google = model on 961 lines (agreement control: of those, 353 still differ from the human text and are unreachable by this method); Google = human on 691; model = human on 673.

Candidates: 197; truth known for 193 (the human line could not be word-aligned for the rest).

### Per rule — all books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 44 | 14 | 0 | 29 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 60 | 10 | 0 | 46 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |
| subscript | 29 | 1 | 0 | 28 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 17 | 6 | 0 | 11 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 33 | 6 | 11 | 0 | 16 | 15 | 0 | 1 | 93.8% | 73.6% | +15 |
| base_sub | 7 | 1 | 0 | 6 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 7 | 0 | 0 | 6 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 197 | 38 | 11 | 126 | 22 | 21 | 0 | 1 | 95.5% | 80.2% | +21 |

### Per rule — dev books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 10 | 5 | 0 | 5 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| accent | 22 | 5 | 0 | 15 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 13 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 6 | 4 | 0 | 2 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 23 | 2 | 8 | 0 | 13 | 12 | 0 | 1 | 92.3% | 68.4% | +12 |
| constraint | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| **all** | 75 | 16 | 8 | 36 | 15 | 14 | 0 | 1 | 93.3% | 72.1% | +14 |

### Per rule — held-out books

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 34 | 9 | 0 | 24 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 38 | 5 | 0 | 31 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 16 | 1 | 0 | 15 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 11 | 2 | 0 | 9 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 10 | 4 | 3 | 0 | 3 | 3 | 0 | 0 | 100.0% | 36.8% | +3 |
| base_sub | 7 | 1 | 0 | 6 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 6 | 0 | 0 | 5 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 122 | 22 | 3 | 90 | 7 | 7 | 0 | 0 | 100.0% | 65.2% | +7 |

### Release-candidate verdicts (held-out books)

| rule | accepted | LB95 | net edits | systematic failure | verdict |
|---|---:|---:|---:|---|---|
| breathing | 1 | 5.0% | +1 | none | proposal-only |
| accent | 2 | 22.4% | +2 | none | proposal-only |
| subscript | 0 | 0.0% | +0 | none | proposal-only |
| marks_multi | 0 | 0.0% | +0 | none | proposal-only |
| final_grave | 3 | 36.8% | +3 | none | proposal-only |
| base_sub | 0 | 0.0% | +0 | none | proposal-only |
| constraint | 1 | 5.0% | +1 | none | proposal-only |

### Ablations (all books; accepted = known-truth candidates passing the stage)

| rule | stage | accepted | = human | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|
| breathing | model_only | 30 | 12 | 40.0% | 25.0% | -4 |
| breathing | model+lexicon | 4 | 4 | 100.0% | 47.3% | +4 |
| breathing | model+ink | 10 | 6 | 60.0% | 30.4% | +2 |
| breathing | full | 1 | 1 | 100.0% | 5.0% | +1 |
| accent | model_only | 50 | 16 | 32.0% | 21.2% | -11 |
| accent | model+lexicon | 9 | 9 | 100.0% | 71.7% | +9 |
| accent | model+ink | 11 | 9 | 81.8% | 53.0% | +7 |
| accent | full | 4 | 4 | 100.0% | 47.3% | +4 |
| subscript | model_only | 27 | 15 | 55.6% | 38.2% | +5 |
| subscript | model+lexicon | 4 | 3 | 75.0% | 24.9% | +4 |
| subscript | model+ink | 1 | 1 | 100.0% | 5.0% | +1 |
| subscript | full | 0 | 0 | - | 0.0% | +0 |
| marks_multi | model_only | 11 | 2 | 18.2% | 3.3% | +0 |
| marks_multi | model+lexicon | 1 | 1 | 100.0% | 5.0% | +2 |
| marks_multi | model+ink | 1 | 0 | 0.0% | 0.0% | -1 |
| marks_multi | full | 0 | 0 | - | 0.0% | +0 |
| final_grave | model_only | 27 | 26 | 96.3% | 83.6% | +26 |
| final_grave | model+lexicon | 16 | 15 | 93.8% | 73.6% | +15 |
| final_grave | model+ink | 16 | 15 | 93.8% | 73.6% | +15 |
| final_grave | full | 16 | 15 | 93.8% | 73.6% | +15 |
| base_sub | model_only | 6 | 2 | 33.3% | 6.3% | -2 |
| base_sub | model+lexicon | 0 | 0 | - | 0.0% | +0 |
| base_sub | model+ink | 0 | 0 | - | 0.0% | +0 |
| base_sub | full | 0 | 0 | - | 0.0% | +0 |
| constraint | model_only | 7 | 5 | 71.4% | 34.1% | +8 |
| constraint | model+lexicon | 2 | 2 | 100.0% | 22.4% | +3 |
| constraint | model+ink | 1 | 1 | 100.0% | 5.0% | +1 |
| constraint | full | 1 | 1 | 100.0% | 5.0% | +1 |
| all | model_only | 158 | 78 | 49.4% | 42.6% | +22 |
| all | model+lexicon | 36 | 34 | 94.4% | 83.5% | +37 |
| all | model+ink | 40 | 32 | 80.0% | 66.8% | +25 |
| all | full | 22 | 21 | 95.5% | 80.2% | +21 |

### Agreement with the human text (mark rules with both verdicts; outcome known as model-right or Google-right)

| witness says "model" | n | model = human | Google = human | agreement |
|---|---:|---:|---:|---:|
| lexicon alone | 19 | 19 | 0 | 100.0% |
| ink alone | 24 | 17 | 7 | 70.8% |
| lexicon AND ink | 5 | 5 | 0 | 100.0% |
| neither (lexicon no, ink no) | 70 | 19 | 51 | 27.1% |

### Per-mark recovery (TP / FP / recall), all books

| rule (Google→human diff) | recoverable Google errors | recovered (TP) | FP (accepted, ≠ human) | recall | precision |
|---|---:|---:|---:|---:|---:|
| breathing | 45 | 2 | 0 | 4.4% | 100.0% |
| accent | 48 | 4 | 0 | 8.3% | 100.0% |
| subscript | 30 | 0 | 0 | 0.0% | - |
| dialytika | 1 | 0 | 0 | 0.0% | - |
| marks_multi | 16 | 0 | 0 | 0.0% | - |
| final_grave | 49 | 15 | 0 | 30.6% | 100.0% |
| base_sub | 4 | 0 | 0 | 0.0% | - |
| **all** | 193 | 21 | 0 | 10.9% | 100.0% |

### Reader-agreement strata (all candidates, by rule)

| rule | model = human | Google = human | all different | unknown | accepted: model = human | accepted: Google = human | accepted: all different |
|---|---:|---:|---:|---:|---:|---:|---:|
| breathing | 16 | 23 | 4 | 1 | 1 | 0 | 0 |
| accent | 19 | 31 | 9 | 1 | 4 | 0 | 0 |
| subscript | 15 | 12 | 1 | 1 | 0 | 0 | 0 |
| marks_multi | 5 | 5 | 6 | 1 | 0 | 0 | 0 |
| final_grave | 30 | 2 | 1 | 0 | 15 | 0 | 1 |
| base_sub | 3 | 4 | 0 | 0 | 0 | 0 | 0 |
| constraint | 5 | 0 | 2 | 0 | 1 | 0 | 0 |

### Accepted corrections by direction

| direction | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| add | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| change | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| change | accent | 4 | 4 | 0 | 100.0% | 47.3% | +4 |
| change | final_grave | 16 | 15 | 0 | 93.8% | 73.6% | +15 |

### Accepted corrections by regime

| regime | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| poly19 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| poly19 | accent | 4 | 4 | 0 | 100.0% | 47.3% | +4 |
| poly19 | final_grave | 16 | 15 | 0 | 93.8% | 73.6% | +15 |
| poly19 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |

### Accepted corrections by book

| book | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| wikisource:02a3a2a6 | final_grave | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | final_grave | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:384c3f89 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:51fe7386 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| wikisource:51fe7386 | final_grave | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:8b6b0de9 | accent | 2 | 2 | 0 | 100.0% | 22.4% | +2 |
| wikisource:8b6b0de9 | final_grave | 12 | 11 | 0 | 91.7% | 66.1% | +11 |

### Accepted corrections by line length (words)

| words | rule | accepted | = human | FP | precision | LB95 | net edits |
|---|---|---:|---:|---:|---:|---:|---:|
| 4-7 | breathing | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| 4-7 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| 4-7 | final_grave | 11 | 10 | 0 | 90.9% | 63.6% | +10 |
| 4-7 | constraint | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| <=3 | accent | 1 | 1 | 0 | 100.0% | 5.0% | +1 |
| <=3 | final_grave | 5 | 5 | 0 | 100.0% | 54.9% | +5 |
| >=8 | accent | 2 | 2 | 0 | 100.0% | 22.4% | +2 |

### Abstention and rejection reasons (all candidates)

| reason | n | of which model = human | Google = human |
|---|---:|---:|---:|
| excluded:proper_name | 34 | 14 | 14 |
| model_form_unattested | 14 | 6 | 8 |
| model_form_unattested + abstain:merged_marks | 14 | 0 | 12 |
| model_form_unattested + above_count | 10 | 1 | 8 |
| model_form_unattested + abstain:localisation_uncertain | 8 | 1 | 5 |
| both_attested | 7 | 4 | 3 |
| both_attested + abstain:merged_marks | 6 | 2 | 3 |
| abstain:final_grave_before_punctuation | 6 | 6 | 0 |
| model_form_unattested + abstain:clipped_bottom | 6 | 4 | 2 |
| both_attested + abstain:clipped_bottom | 5 | 3 | 2 |
| model_form_unattested + abstain:removal_with_wide_blob | 5 | 1 | 3 |
| abstain:merged_marks | 4 | 4 | 0 |
| model_form_unattested + abstain:neighbouring_marks | 4 | 2 | 1 |
| abstain:localisation_uncertain | 4 | 4 | 0 |
| excluded:all_caps_marks | 4 | 1 | 1 |
| abstain:clipped_bottom | 3 | 2 | 0 |
| margin_below_20x | 3 | 3 | 0 |
| both_attested + above_count | 3 | 2 | 1 |
| model_form_unattested + abstain:needs_one_oblique | 3 | 0 | 3 |
| both_attested + abstain:localisation_uncertain | 3 | 0 | 1 |
| both_attested + abstain:neighbouring_marks | 2 | 1 | 1 |
| abstain:needs_one_oblique | 2 | 2 | 0 |
| model_form_unattested + blob_below_but_model_has_none | 2 | 0 | 2 |
| above_count | 2 | 2 | 0 |
| both_attested + slope_disagrees | 2 | 0 | 0 |
| oblique_but_model_has_circumflex | 2 | 2 | 0 |
| both_attested + abstain:removal_with_wide_blob | 2 | 0 | 1 |
| violates:C1:breathing_after_consonant_start + abstain:removal_with_wide_blob | 1 | 1 | 0 |
| violates:C3:two_accents + abstain:localisation_uncertain | 1 | 1 | 0 |
| both_attested + blob_below_but_model_has_none | 1 | 0 | 1 |
| both_attested + abstain:needs_one_oblique | 1 | 0 | 1 |
| margin_below_20x + abstain:clipped_bottom | 1 | 0 | 0 |
| rejected:polytonic_mark_in_monotonic_regime | 1 | 0 | 0 |
| violates:C1:missing_initial_breathing + abstain:merged_marks | 1 | 0 | 0 |
| abstain:neighbouring_marks | 1 | 1 | 0 |
| model_form_unattested + abstain:faint_mark | 1 | 0 | 1 |
| model_form_unattested + abstain:clipped_top | 1 | 0 | 1 |
| both_attested + abstain:faint_mark | 1 | 0 | 1 |
| violates:C1:missing_initial_breathing + abstain:removal_with_wide_blob | 1 | 0 | 0 |
| violates:C1:missing_initial_breathing + abstain:neighbouring_marks | 1 | 1 | 0 |
| violates:C4:circumflex_before_penult + above_count | 1 | 1 | 0 |
| both_attested + abstain:clipped_top_no_false_absence | 1 | 0 | 1 |

### Physical controls (candidates on lines with the property)

| property | lines | candidates | accepted | = human | Google right (FP) |
|---|---:|---:|---:|---:|---:|
| clipped | 450 | 106 | 9 | 9 | 0 |
| specks | 71 | 12 | 0 | 0 | 0 |
| faint_ink | 40 | 6 | 0 | 0 | 0 |
| neighbour_ink | 207 | 42 | 3 | 3 | 0 |
| long | 432 | 83 | 6 | 6 | 0 |

### Ink-decisive variant (lexicon-neutral candidates; `markshape_model.json`, tau = 99 % held-out precision)

Lexicon-neutral mark candidates: 117; ink-decisive among them: 4.

| rule | lexicon-neutral | ink_decisive | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 21 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| accent | 36 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| subscript | 16 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 10 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 30 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 4 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| all | 117 | 4 | 4 | 0 | 0 | 100.0% | 47.3% | +4 |

Why lexicon-neutral candidates were not ink-decisive:  50, ink_conjunction:abstain:merged_marks 14, ink_conjunction:abstain:clipped_bottom 10, ink_conjunction:above_count 7, ink_conjunction:abstain:neighbouring_marks 6, ink_conjunction:abstain:removal_with_wide_blob 6, shape_below_tau 5, no_shape_model 4, ink_conjunction:abstain:needs_one_oblique 3, ink_conjunction:slope_disagrees 2, ink_conjunction:abstain:faint_mark 2, attached_breathing_not_decisive 1, shape_predicts_dasia 1, ink_conjunction:blob_below_but_model_has_none 1, ink_conjunction:abstain:clipped_top_no_false_absence 1.

Recall of the 193 recoverable Google mark errors: rules 21 (10.9%); rules + ink_decisive 25 (13.0%).

### Ceiling analysis of the recoverable Google mark errors

| class | n | share |
|---|---:|---:|
| model wrong (unreachable without a better model) | 100 | 51.8% |
| model right, accepted by the rules | 21 | 10.9% |
| model right, lexicon neutral, ink not decisive | 21 | 10.9% |
| model right, excluded by a guard | 15 | 7.8% |
| model right, ink conjunction fails | 14 | 7.3% |
| model right, abstained (ink unreadable / regime) | 11 | 5.7% |
| model right, lexicon contradicts | 7 | 3.6% |
| model right, lexicon neutral, ink decisive | 4 | 2.1% |

### Policy defaults (3a line-initial capitals, 3b acute house style)

3a: line-initial capitalised words admitted (lower-cased model form attested ≥ 50, not in the proper-name list): 3 candidates, 1 accepted, 1 = human, 0 Google right.

3b: pages flagged as acute-everywhere (share of word-final acute > 0.8 over ≥ 10 accented final syllables in the Google text): 0 pages carrying 0 candidates; final_grave corrections suppressed on them: 0 (0 would have matched the human text, 0 would have been false).

### Orthographic constraints (polytonic-regime lines; `constraints.py`)

Google words checked: 6124; violating a hard constraint: 35 (0.6%); of those, the human form is itself impossible (constraint too strict or human error): 14; Google = human although "impossible": 14; the model's form is possible: 16, of which model = human: 11.

| violation | Google words | model possible | model = human | Google = human |
|---|---:|---:|---:|---:|
| C3:two_accents | 12 | 2 | 1 | 10 |
| C1:missing_initial_breathing | 11 | 8 | 4 | 0 |
| C4:accent_before_antepenult | 5 | 1 | 1 | 4 |
| C4:circumflex_before_penult | 4 | 3 | 2 | 0 |
| C1:several_breathings | 3 | 3 | 2 | 0 |
| C1:breathing_after_consonant_start | 2 | 1 | 1 | 1 |
| C4:grave_not_final | 1 | 0 | 0 | 0 |

Rule `constraint` (single allowed mark difference, Google impossible, model possible, ink agrees): candidates 7, accepted 1, = human 1, Google right 0, human ≠ both 0, precision 100.0%, LB95 5.0%, net edits +1; overlap with the lexicon rules: 0 of the 1 accepted would also pass the lexicon (the other 1 are corrections the lexicon alone could not make).

Accepted by underlying mark category: breathing 1.

### Accepted corrections that do not match the human text (1)

| rule | book | Google | proposed | human | crop |
|---|---|---|---|---|---|
| final_grave | wikisource:8b6b0de9 | φωλεά | φωλεὰ | φωλέα | `docs/records/harvest/harvest_big/wikisource/crops/8b6b0de9/p000016-l0013.png` |

## Typeface class

Not derivable: the prediction records carry `font_style_unknown` for every real line; the only per-line grouping available is the book (above). All lines are from the `wikisource` wave.
