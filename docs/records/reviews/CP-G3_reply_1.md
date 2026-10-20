# CP-G3 reply (implementer, 8 Oct 2026 ~17:20 Athens)

Verdict HOLD (gpt-6.1-sol; 4 HIGH, 4 MEDIUM, 1 LOW; certified run, scope unchanged). All findings fixed; the reviewer's
seven independent regressions are ported as tests (51 glyph tests pass; provenance tests 1,037 pass).

| Finding | Disposition | Fix and evidence |
|---|---|---|
| F1 [HIGH] faint filter deletes faint letters | Fixed | binarise no longer uses a stroke reference: a faint-only blob is dropped only when large (short side ≥ 30 % of the crop height) and solid (thickness ≥ 40 % of its short side). `test_g3_real_faint_capitals_survive_small_dark_punctuation` (ΘΩΜΒ at 195 with three dark dots: ≥ 95 % kept), `test_g3_page_edge_shadow_is_still_not_ink` (owner crop 3229…l00018). |
| F2 [HIGH] cut-edge attribution | Fixed | lines_api.straighten_edges returns directional masks; top_cut = body rows above the crop top, bottom_cut = body rows below the crop bottom. `test_g3_cut_fraction_keeps_the_correct_edge[...]` (baseline −10 → bottom_cut 0; baseline 40 → top_cut 0). |
| F3 [HIGH] flattened coordinates | Fixed | top-level letters / cut_spans / cut_letters / lines are in crop coordinates with `segment`; `main_segment`, `main_x_offset`, crop-coordinate `support_x`; nested segments keep local coordinates. `test_g3_flattened_entries_are_in_crop_coordinates`. |
| F4 [HIGH] builder crash | Fixed | build_review_data uses per-segment baselines (main segment) and n_full_lines / n_lines / n_columns; review_page.html draws each column segment in its own frame (column labels; "N lines detected: main + full + edges only", owner 16:10). Full builder: 408 unseen crops measured in 43.9 s, 40 lines written, page renders (checked headless). |
| F5 [MEDIUM] None prior | Fixed | prior decided by value (finite, > 0) for both the soft-cut trust and the refit. `test_g3_none_prior_does_not_trust_a_clipped_xheight`. |
| F6 [MEDIUM] rule vetoes itself | Fixed | rule candidates are excluded from the letter-height reference. `test_g3_true_rule_is_not_its_own_letter_height_reference`. |
| F7 [MEDIUM] over-inked capitals dropped | Fixed | PATCH_THICKNESS removed from letters (height alone marks non-letter ink; faint patches are handled in binarise). `test_g3_over_inked_capitals_are_kept_as_letters` (Μ, Θ dilated 8 px). |
| F8 [MEDIUM] neighbour metrics | Fixed | strict precision over present lines (167/189 = 88.4 %, 22 unmatched incl. 1 barely visible) printed; zero matches print "no matches" instead of crashing. |
| F9 [LOW] capitals wording | Fixed | plan: 120 attempts, 118 scored lines; "more than one box 4.8 % (95 in two, 3 in three)"; capitals carry no accents in this cohort. |
