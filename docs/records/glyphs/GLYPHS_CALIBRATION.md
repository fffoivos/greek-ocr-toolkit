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
| accent / tall-letter zone cut | ≈ 0.3 | bins < 0.3: median CER ≤ 0.017; ≥ 0.3: 0.08–0.22, 57–93 % of strips out; the first adverse bin rests on 6 base texts |
| letter body cut at the top | ≈ 0.05 | every bin ≥ 0.05: median CER ≥ 0.18 (the accent zone is already gone); the first adverse bin rests on 6 base texts |
| tail zone cut | **no limit established** | no measured bin leaves the band: 0.6–0.7 / 0.7–0.8 / 0.8–1.0 median NFC 0.047 / 0.036 / 0.032 (n 23 / 5 / 20); only the injected tail_cut 1.0 reaches 0.051 NFC (0.040 NFD) |
| letter body cut at the bottom | ≈ 0.1 | 0.05–0.10: 0.050, 30 % out; 0.10–0.15: 0.070, 67 % out |
| skew | 4° is a **policy**, not a crossing | 3° in band; 5° at the band edge (NFC 0.050, NFD 0.041); 4° was not tested |
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

**Margin sweep (canonical NFD scoring).** Same 240 strips; cells = median NFD CER / median NFC CER / pooled accent
(mark) F1 from greekocr._vendor.bench.e1_readout.mark_metrics; last row means. Columns: original, straightened with
paper padding, and tight output cropped to its ink ± 0.5 / 0.3 / 0.2 x-heights.

| E1 f50_s0 | n | original | straight padded | tight m0.5 | tight m0.3 | tight m0.2 |
|---|---|---|---|---|---|---|
| clean ±2° (measured <1°) | 18 | 0.080 / 0.103 / 0.76 | 0.053 / 0.070 / 0.85 | 0.053 / 0.061 / 0.85 | 0.028 / 0.033 / 0.89 | 0.035 / 0.042 / 0.88 |
| clean ±2° (measured ≥1°) | 22 | 0.469 / 0.504 / 0.46 | 0.070 / 0.083 / 0.79 | 0.047 / 0.058 / 0.83 | 0.042 / 0.050 / 0.84 | 0.028 / 0.033 / 0.85 |
| rotated 0° | 40 | 0.028 / 0.033 / 0.87 | 0.069 / 0.083 / 0.81 | 0.066 / 0.083 / 0.83 | 0.041 / 0.051 / 0.86 | 0.028 / 0.033 / 0.86 |
| rotated 1° | 40 | 0.188 / 0.208 / 0.66 | 0.069 / 0.085 / 0.80 | 0.061 / 0.068 / 0.82 | 0.041 / 0.050 / 0.86 | 0.029 / 0.040 / 0.86 |
| rotated 2° | 40 | 0.514 / 0.533 / 0.40 | 0.071 / 0.097 / 0.80 | 0.056 / 0.064 / 0.82 | 0.041 / 0.050 / 0.85 | 0.028 / 0.033 / 0.86 |
| rotated 3° | 40 | 0.678 / 0.683 / 0.25 | 0.078 / 0.093 / 0.79 | 0.061 / 0.074 / 0.82 | 0.039 / 0.050 / 0.86 | 0.037 / 0.050 / 0.86 |
| rotated 5° | 40 | 0.860 / 0.846 / 0.11 | 0.071 / 0.097 / 0.76 | 0.065 / 0.085 / 0.80 | 0.043 / 0.053 / 0.82 | 0.042 / 0.058 / 0.84 |
| all 240 (mean) | 240 | 0.396 / 0.411 / 0.53 | 0.092 / 0.109 / 0.79 | 0.074 / 0.088 / 0.82 | 0.051 / 0.063 / 0.85 | 0.045 / 0.056 / 0.86 |

- **Level lines (rotated 0°, n = 40): tight m0.2 equals the original** — median NFD 0.028 vs 0.028; paired bootstrap
  (10,000 resamples) Δmedian 95 % CI [−0.011, +0.011], mean paired Δ +0.006 [−0.004, +0.017]; mark F1 0.87 → 0.86.
  The coordinator's bar (≤ +0.005 median NFD) is met.
- The earlier level-line cost was mostly the margin, not the resampling. (An earlier sentence here said the shift-only
  path reads identically; CP-G4 measured 10/40 level strips changed under E1 — retracted.)
- Every skew bin: tight m0.2 holds E1 at 0.028–0.042 median NFD (original 0.188 at 1° → 0.860 at 5°); mean over all
  240 strips 0.396 → 0.045, mark F1 0.53 → 0.86. CLLG median 0.000 in every bin and variant except the original (unstraightened) 5° bin (NFD 0.041).
- Decision: recogniser-facing output = `separate_lines(..., tight=True, margin=0.2, level_deg=0)` — the configuration
  actually scored. The shift-only path (`level_deg` > 0) is NOT qualified: it changes E1 readings on 10 of the 40 level
  strips (CP-G4 F5), so it is off by default. Margin stays a parameter; the padded form is for display.
- The level-line result is a passing **in-sample point estimate**, not an equivalence: the 95 % interval of Δmedian
  [−0.011, +0.011] allows a regression larger than the +0.005 bar; 12 strips worse, 10 better, 18 unchanged; the
  margin was chosen on the same 40 texts.

## E1 limits: none established

E1's clean band (median 0.22 + 2 × IQR 0.41 ≈ 1.05) is inflated by the renderer's ±2° skew, so no injected condition
leaves it and no E1 cut or skew limit follows from the rule. (Earlier versions exported E1 limits; retracted, CP-G4 F4.)
E1 needs level controls (frozen scan parameters, CP-G4 F6) before any E1 limit can be measured.

## Known gaps (CP-G4, 8 Oct)

- F3: calibration measured support-averaged crop-edge cuts per strip; production gates on edge-touching ink and
  applies the limits per x-position, with a 50 %-of-width verdict boundary that is policy, not calibrated. Not yet the
  same measurement.
- F2: from the crop alone, accents cut through a blank gap leave no evidence (false "readable"), and fragments of the
  line above at the top edge can be taken for the main line (false "unreadable").
- F6: cut conditions use one median baseline on strips that keep the renderer's random skew, so a nominal cut varies
  along the line; ink-defect renders consume an extra random draw, so fade/thin/break/thick strips differ from their
  clean controls in skew and scan noise.
- Direction (owner 8 Oct 18:05): recut each line from its page along its fitted geometry, so the crop edge no longer
  removes accents or tails and what a crop lost is measured directly.

## Real crops under the CLLG limits (444 crops: 400 parliament sample + 44 fixtures)

With `greekocr.glyphs.readability` (limits above; ink states reported but not used): 195 readable, 241 partly
readable (some x-range over a limit), 8 unreadable (half the width or more over); 247 crops have the accent /
tall-letter zone cut at the top somewhere (tight text-layer boxes), 36 the letter body; 81 crops have an ambiguous
target (more than one column or more than one full text line).

## Caveats

Synthetic Didot-like print, one text source, two readers; the limits describe these readers on this regime and are
measured, not derived. The cut measurements underestimate deep cuts (above about 0.4 of a zone) when no document
x-height is available. Ink-state measurements were not predictive of CLLG errors at the strengths tested.
