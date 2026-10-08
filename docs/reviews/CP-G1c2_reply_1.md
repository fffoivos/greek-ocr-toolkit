# CP-G1c2 reply (implementer, 8 Oct 2026 16:05 Athens)

Cycle-2 verdict HOLD (gpt-6.1-sol; 6 HIGH, 1 MEDIUM). Second consecutive HOLD → structural diagnosis before any
further cycle (checkpoint policy): the evaluator kept borrowing the detector's own outputs (band, ink mask, component
ids) as truth, and each review found one more edge case by probing. Structural fixes: (1) letter-state truth now comes
from the renderer alone; (2) every reviewer probe is a permanent regression test; (3) a scoped final verification
(Astra) instead of a third full Sol cycle.

| Finding | Disposition | Fix and evidence (raw outputs: review_scratch/CP-G1c3-evidence/) |
|---|---|---|
| F1 [HIGH] state truth depends on the detector; unscored letters; conditional neighbour rate | Fixed | Truth uses only the renderer: letter-id map, true baseline/x-height, and either the physical print (`print_ink`: clean ink after defects, before blur/gain/noise) or the noise-free scan at a visibility threshold (`visible(.25)`); both reported. Every reliable truth letter is scored: vanished / missed included (letters_true 15,067; missed 327 of which 231 vanished). Neighbour: `neighbour_recall` over all visible truth pixels + `neighbour_classified_of_detected` separately. Regressions `test_f1c2_letter_truth_does_not_depend_on_the_detector` (moving the detector band does not change the true-state counts) and `test_f1c2_neighbour_recall_counts_erased_neighbour_ink`. A first attempt used the midpoint of the blurred scan as truth: it cut hairlines and made 17 % of undamaged letters 'broken' (evals_v5.txt) — rejected, kept for visibility of marks/neighbours only. |
| F2 [HIGH] combining marks unchecked | Fixed | Every code point of NFC and NFD is checked against .notdef. `font_covers(Didot, 'ἀ̄')` → False ('U+0304 is .notdef'); render refused. Regression in `test_f6_render_refuses_text_the_font_cannot_draw`. |
| F3 [HIGH] pieces = whole components | Fixed | letters.py labels connected pieces of the ink restricted to the middle region, then groups pieces; components are kept only as parents. `test_f3c2_pieces_are_counted_inside_the_middle_region_only` (arcs joined above the band → broken, 2 pieces). |
| F4 [HIGH] faint body attached to a dark stroke lost | Fixed | Faint ink more than 2 px from strong ink is added as its own pieces (≥ 24 px); faint-only blobs never feed the band or x-height (a first version let paper smudges pull line04's band 12 px — caught by the line04 regression and fixed). Probe: 340/388 px kept, letter flagged. `test_f4c2_faint_body_attached_to_a_dark_stroke_is_kept_and_flagged`. |
| F5 [HIGH] fully fused letters intact | Fixed | A single middle-region piece ≥ 1.8 typical letters wide without a thin bridge stays one box, merged and unresolved (wide single letters stay below 1.8). `test_f5c2_fully_fused_letters_are_flagged_merged`; thick test now requires ≥ 40 % of affected boxes merged and > 3× the unaffected rate (measured on seed 2: thick → merged 95.6 %). |
| F6 [HIGH] defect votes leak across split boxes | Fixed | Votes use each box's component pixels inside its own bounds (broken_eval.py, evaluate._box_map, thick/break regression). |
| F7 [MEDIUM] docs/provenance | Fixed | scripts/glyphs/eval/README.md rewritten (removed scripts named, seeds listed); provisional fixture labels published in docs/glyphs_fixture_labels.json with scripts/glyphs/eval/fixture_double.py (7/7 double, 0/20 single, 2/17 partial, 9/44 flagged); plan numbers re-derived from evals_v5/v6; historical 84 % claim replaced by the reproducible current figures. |

Measured now (evals_v5/v6, seeds as in README): skew high-confidence max 0.217° (95/100), all straight p99 0.98°;
bent lines with any column > 0.25 xh off 34 %. Marks: separate accents found 98.7 %, precision 95.2 %; neighbour
recall 97.1 %. Letter states — PRINT truth: merged precision 3.6 % (undamaged) / 27 % (defects), broken recall
25 % / 40 %; VISIBLE truth: merged precision 87 % / 85 %, recall 64 % / 80 %; broken recall 53 % / 63 %, under
precision 41 % / 65 %. Reading: 'merged' measures letters visibly touching in the scan (blur included), not proof of
over-inking in print; 'broken' is moderate. Vanished letters (faded below visibility) get no per-letter warning yet.
