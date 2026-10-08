# Owner page reviews — notes that apply to a whole page

## p6 · table (Vouli s2-200e977f2dab5291c42c-p00035), 8 Oct 2026, ~23:40

Owner: "on the table page it is hard to judge from each segment by itself but basically all errors are that:
(1) column boundaries are violated; (2) on the first column where we have numbers 1–38 some are underlined with very
uneven lines while all of them are straight."

Checked:
- (2) confirmed. Each row number is its own text-layer box, 22–29 px wide with one or two digits, so the crop tools
  have 0–2 letters of evidence: the fitted line is arbitrary (e.g. +31° on "2", a default flat band on "1", "3", "6").
  Fix direction (owner's shared-geometry rule): a segment with too few letters to fit takes its line's geometry from
  its neighbours on the page (the row's other cells / the page's skew), never its own fit.
- (1) not yet pinned down: the table's vertical rules are short inside each row box and are not found by the crop
  rule test (it requires a rule ≥ 80 % of the crop height and 1.5 × the letters); to verify per row.
