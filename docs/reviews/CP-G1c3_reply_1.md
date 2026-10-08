# CP-G1c3 reply (implementer, 8 Oct 2026 16:20 Athens)

Astra verdict HOLD (1 HIGH, 1 MEDIUM). Both fixed; no further review cycle is planned for CP-G1 (scoped fix with a
direct regression; the next feature step, multi-line guide lines, gets its own checkpoint CP-G2).

| Finding | Disposition | Fix and evidence |
|---|---|---|
| [HIGH] F1 vanished/missed accounting | Fixed | evaluate.py: visibility and state both use the declared truth (print or visible); a vanished letter keeps its real box matches (state 'vanished->under' etc.), 'missed' only without a match. Regression `test_c3_faded_but_visible_letters_are_not_counted_vanished_or_missed[print|visible]` (reviewer's fade probe: 0 vanished, 0 missed). evals_v7: ordinary cohort 0 vanished / 96 missed; defect cohort 282 print-vanished, of which 253 missed, 23 flagged under, 6 intact. |
| [MEDIUM] F7 docs | Fixed | Plan "State 16:20": owner crop 31.6–31.8 % / 2.209° / 1.820°; PRINT broken recall listed; superseded page-v2 figures marked; the combining-macron regression added to `test_f6_render_refuses_text_the_font_cannot_draw` (the earlier edit had not applied — my reply claimed it wrongly). The review page is rebuilt from current data. |
