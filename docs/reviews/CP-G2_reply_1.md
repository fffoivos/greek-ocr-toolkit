# CP-G2 reply (implementer, 8 Oct 2026 ~16:55 Athens)

Verdict HOLD (gpt-6.1-sol; 2 HIGH, 3 MEDIUM, 1 LOW). The harness also flagged the review NOT certified because I edited
docs/GLYPHS_PLAN.md (the owner's 16:40 direction) during it — my error; the findings are independent of that edit and
are all addressed. Plan/doc files will not be edited while a review is in flight.

| Finding | Disposition | Fix and evidence |
|---|---|---|
| F1 [HIGH] rejected peak ends the side search | Fixed | text_lines drops a rejected peak's votes and keeps searching (≤ 4 × max_per_side attempts; accepted lines count toward max_per_side = 3). `test_g2_rejected_peak_does_not_end_the_side_search` (reviewer probe with and without the distractor: above line at baseline 9 both times). |
| F2 [HIGH] neighbour eval not honest | Fixed | neighbour_eval.py: geometric one-to-one matching (median error ≤ 0.5 x-heights), unmatched predictions counted and printed, recall over present lines, precision over predictions, placement error over matches. Seed 71, N 150: 167/199 matched (recall 83.9 %), 32 missed, 21 unmatched predictions (precision 88.9 %), median error 0.047 x-heights, ≤ 0.25 for 88.0 % of matches / 73.9 % of present lines. Page claim corrected. |
| F3 [MEDIUM] two specks invent a line | Fixed | a peak needs ≥ MIN_PIECES = 3 distinct components. `test_g2_two_specks_do_not_invent_a_line_and_three_lines_are_found`. |
| F4 [MEDIUM] limits | Fixed / disclosed | max 3 lines per side; search ±6 x-heights (two line pitches); separation 1.8; nearest neighbour ≥ LINE_MIN 1.7 x-heights (real pitch ≥ 2.2; nearer ink is the main line's — this also removed two false 'neighbours' on the owner's clipped crop). Lines 1.7 apart (reviewer's tight case) are below the limit and disclosed; the three-line test uses a realistic 2.3 pitch and asserts the third line at 6.9 is out of range. |
| F5 [MEDIUM] stale vanished count | Fixed | plan updated (282 print-vanished: 253 missed / 23 under / 6 intact). |
| F6 [LOW] singleton visibility | Fixed | visibility averaged over x0..x1 inclusive. |
| Page equivalence | Noted | published pages are rebuilt from current data in this step; earlier-batch JSONs are kept in the session scratch and summarised per line ("before → now"). |

Also in this step (owner, 8 Oct 16:15–16:40): letters bounded by their line (LINE_HEIGHT 2.6, PATCH_THICKNESS 1.2 x-heights;
faint ink must be stroke-like) with the owner's 3229…l00018 crop as a regression; column split at vertical rules (must
out-tower the letters) and at unaligned gaps > 3 x-heights (only with a trusted x-height; ≥ 6 x-heights each side;
columns share one type size); per-column records; lines API (separate_lines, straighten). 43 glyph tests.
