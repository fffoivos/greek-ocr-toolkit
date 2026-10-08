# Readability limits from OCR readers on calibrated synthetic strips

8 Oct 2026, owner request 16:40: "find empirically where the limits lie" for cut-offs (top and bottom separately) and
ink, using lines like the synthetic generator's, so real lines can be placed on the same scales.

## Design

- **Strips.** 40 polytonic lines (Gutenberg Greek text) rendered in Didot-like fonts (GFS Didot, Theano Didot, GFS
  Neohellenic, Old Standard, EB Garamond, Gentium, …; coverage-checked) at 30–40 px with the toolkit's scan model,
  each line under every condition below, one degradation at a time. Cut strips are cropped tightly like a page
  cutter, then cut by a controlled amount.
- **Conditions (v2, 44 per line, 1,760 strips).** clean; `accent_cut` 0.25–1.0 (share of the zone above the mean line
  — accents, breathings, tall-letter tops — removed by the top edge); `top_cut` 0.1–0.5 (share of the letter body
  removed from the top, after the whole accent zone); `tail_cut` 0.25–1.0 and `bottom_cut` 0.1–0.5 (the same from the
  bottom); `fade`, `thin`, `break`, `thick` 0.2–1.0; `skew` 0–5° (rotated, then tightly cropped).
  v1 (1,560 strips) cut from the mean line directly and left skew strips uncropped; both flaws were found in its
  results and fixed in v2.
- **Readers** (run by the coordinator on the GPU node): CLLG (Kraken ppocr_v6_tau090, the strong polytonic reader)
  and E1 f50_s0 (the toolkit's own E2-root retrain, weaker on polytonic). Character error rate (CER) on NFC text; an
  empty reading counts as total failure.
- **Tools' measurements** (`greekocr.glyphs`): on every strip, the cut share of each zone from the four guide lines
  (counted only where ink reaches the edge), skew, ink contrast, broken / merged letter shares; clipped strips borrow
  the true x-height as real crops borrow the document's.
- **Limit rule.** The readable band is CER ≤ clean median + max(0.05, 2 × clean IQR); a limit is where the median
  CER of strips at a measured level leaves the band.

Data: `~/Projects/glossapi-ocr-local/experiments/glyphs_calib/strips_v{1,2}/` (manifest, measurements, predictions).

## Results — CLLG (clean median CER 0.000; band ≤ 0.050)

| condition (injected) | median CER by strength | first strength out of band |
|---|---|---|
| accent_cut 0.25 / 0.5 / 0.75 / 1.0 | 0.000 / 0.000 / 0.044 / 0.166 | 1.0 (0.75: 45 % of strips out) |
| top_cut 0.1 … 0.5 (accent zone gone) | 0.239 … 0.517 | 0.1 |
| tail_cut 0.25 / 0.5 / 0.75 / 1.0 | 0.000 / 0.000 / 0.000 / 0.051 | 1.0 |
| bottom_cut 0.1 … 0.5 (tail zone gone) | 0.083 … 0.383 | 0.1 |
| fade 0.2 … 1.0 | 0.000 throughout | none |
| thin 0.2 / 0.4 (1 px) ; 0.6+ | 0.093 ; 1.000 (letters vanish) | 0.2 |
| break 0.2 … 1.0 | 0.000 … 0.034 | none |
| thick 0.2 … 0.6 / 0.8 / 1.0 | 0.017 / 0.052 / 0.243 | 0.8 |
| skew 0 / 1 / 2 / 3 / 5° | 0.000 / 0.000 / 0.000 / 0.000 / 0.050 | 5° |

Against the tools' measurements (the scale used on real lines):

| measured quantity | readable up to | evidence |
|---|---|---|
| accent / tall-letter zone cut | ≈ 0.3 | bins < 0.3: median CER ≤ 0.017; ≥ 0.3: 0.08–0.22, 57–93 % of strips out |
| letter body cut at the top | ≈ 0.05 | every bin ≥ 0.05: median CER ≥ 0.18 (the accent zone is already gone) |
| tail zone cut | ≈ 0.6 | bins < 0.6: median CER ≤ 0.02; 0.6–1.0: 0.03–0.05, 20–43 % out |
| letter body cut at the bottom | ≈ 0.1 | 0.05–0.10: 0.050, 30 % out; 0.10–0.15: 0.070, 67 % out |
| skew | ≈ 4° | tightly cropped |
| ink contrast (paper − ink) | none found | CER 0 down to contrast < 30 |
| broken / merged letter shares | not predictive | CER does not follow them except at the extremes (letters vanished; ink 0.8+) |

Reading: for polytonic OCR the **top** edge is the critical one. Losing the accent zone loses characters (breathings
and accents are part of the text), and any cut into the letter body from the top is already fatal. The **bottom**
tolerates losing most tails; a cut into the body from below fails at about a tenth of it. Ink degradations matter
only at their extremes.

## Results — E1 f50_s0: skew is its main weakness

E1's CER on clean strips is high (median 0.22), but those strips carry the renderer's random ±2° skew. Grouped by
the tools' measured skew, E1's median CER on clean strips is 0.075 (< 0.5°), 0.139 (0.5–1°), 0.370 (1–1.5°),
0.533 (1.5–2°); at exactly 0° on tight crops it is 0.033 (skew 1° → 0.21, 2° → 0.53, 5° → 0.85). CLLG is 0.000 in
every bin. E1 also degrades steadily with every cut and with fading (contrast < 45: CER 0.42–0.54).

**Straightening removes it.** The same 240 clean and skew strips, straightened by
`greekocr.glyphs.lines_api.separate_lines` (baseline flattened) and read again; "padded" = height-normalised with paper
padding (1.9 x-heights above, 1.0 below the baseline), "tight" = then cropped to its own ink ± 0.3 x-heights (the
calibration crops' margin). Median CER per bin (NFC scoring), mean in the last row:

| strips | n | E1 original | E1 straightened (padded) | E1 straightened (tight) | CLLG original | CLLG tight |
|---|---|---|---|---|---|---|
| clean, measured skew < 0.5° | 6 | 0.075 | 0.067 | 0.058 | 0.000 | 0.000 |
| clean, measured skew 0.5–1° | 12 | 0.139 | 0.070 | 0.032 | 0.000 | 0.000 |
| clean, measured skew 1–1.5° | 3 | 0.370 | 0.067 | 0.017 | 0.000 | 0.000 |
| clean, measured skew 1.5–2° | 19 | 0.533 | 0.083 | 0.050 | 0.000 | 0.000 |
| rotated 0° | 40 | 0.033 | 0.083 | 0.051 | 0.000 | 0.000 |
| rotated 1° | 40 | 0.208 | 0.085 | 0.050 | 0.000 | 0.000 |
| rotated 2° | 40 | 0.533 | 0.097 | 0.050 | 0.000 | 0.000 |
| rotated 3° | 40 | 0.683 | 0.093 | 0.050 | 0.000 | 0.000 |
| rotated 5° | 40 | 0.846 | 0.097 | 0.053 | 0.050 | 0.000 |
| all 240, median | 240 | 0.408 | 0.084 | 0.050 | 0.000 | 0.000 |
| all 240, mean | 240 | 0.411 | 0.109 | 0.063 | 0.016 | 0.006 |

Reading: straightening makes E1 nearly skew-invariant (≈ 0.05 at every skew up to 5°; mean 0.411 → 0.063 tight).
The padded form costs level lines (0.033 → 0.083); the tight form mostly recovers it but not fully under this NFC
scoring (0.033 → 0.051 on exactly level tight crops; the coordinator's NFD scoring gives 0.041). The "level lines do
not regress" bar is therefore not yet cleared for E1; the remaining gap is likely margin / height normalisation and
is the next thing to test. CLLG is unharmed (5° 0.050 → 0.000). Recogniser-facing output uses tight=True; the padded
form is for display.

## Real crops under the CLLG limits (444 crops: 400 parliament sample + 44 fixtures)

With `greekocr.glyphs.readability` (limits above; ink states reported but not used): 195 readable, 241 partly
readable (some x-range over a limit), 8 unreadable (half the width or more over); 247 crops have the accent /
tall-letter zone cut at the top somewhere (tight text-layer boxes), 36 the letter body; 81 crops have an ambiguous
target (more than one column or more than one full text line).

## Caveats

Synthetic Didot-like print, one text source, two readers; the limits describe these readers on this regime and are
measured, not derived. The cut measurements underestimate deep cuts (above about 0.4 of a zone) when no document
x-height is available. Ink-state measurements were not predictive of CLLG errors at the strengths tested.
