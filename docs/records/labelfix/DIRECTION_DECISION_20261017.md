# Direction decision, 17 Oct 2026: the second signal for corrected labels on the training waves

Status: decided by the coordinator, 17 Oct ~01:35 Athens. This note is input for ASTRA-SC1 cycle 3 and for the training track.

## Evidence

### 1. L1-v0 (Clariden job 3679313, S6 detector, PRESENCE gate)

On the 124,669 greek_poly training lines, 83.8% of lines are HOLD (FULL: 85.0%).

| Wave | HOLD |
|---|---:|
| parliament | 95.5% |
| vouli | 86.1% |
| mixed | 79.9% |
| round1 | 79.3% |
| round2 | 77.2% |

For comparison, the 666 Wikisource held-out lines hold 7.5%, and the M2 new-source cards hold 77.6%.

HOLD reasons, counted in slots:

| Reason | Slots |
|---|---:|
| detector/R1 mark-kind disagreement | 298,710 |
| detector localisation_unknown | 196,481 |
| recogniser letter problem | 26,592 |
| K1 flag | 12,343 |

These numbers come from the permissive L1-v0 gate. The SF2 gate also holds the C2-B01 uncertainty states, so it holds more.

### 2. Who is right in the kind disagreements

The sample is 200 seeded held lines, 40 per wave. The proxy is Google's marks, used only where Google's letters equal the recogniser's. The proxy is biased toward R1, because R1 was trained on Google=recogniser agreement.

Of 647 kind-disagreement slots, R1 matches the proxy in 624 (96.4%) and the detector in 10 (1.5%).
- 466 slots are zone-presence disagreements: the detector misses or invents ink.
- 181 slots are kind-only disagreements.
- The detector is right in at most 3 slots in any wave.

Conclusion: the S6 detector is not a usable second signal on the training fonts.

### 3. Alternatives already measured on the 666 held-out lines

These were scored against print truth over 80 Google mark errors.

| Gate | Corrected | Wrong | New errors | HOLD lines |
|---|---:|---:|---:|---:|
| PRESENCE | 48 | 2 | 5 | 50 |
| ZONE | 58 | 1 | 14 | 33 |
| ZONE+LEXICON | 44 | 1 | 6 | 57 |
| A alone | 66 | 5 | 23 | 8 |
| A∧B | 61 | 2 | 7 | 55 |
| A∧E | 61 | 3 | 10 | 45 |
| A∧B∧C | 57 | 2 | 5 | 84 |

On the 200 training lines, A∧B holds 21 of 200 lines, against PRESENCE's 198 of 200.

### 4. S7

None of the toolkit geometry substitutions qualified. Cycle 2 found adapter gaps (C2-M03), so this is not a final verdict on the toolkit approach.

## Decision (coordinator)

1. **Training-wave DEV with print truth.** Draw 150 lines each from parliament and vouli, then 100 each from round1, round2 and mixed, seeded, from L1_input_documents and outside the locked strata. Settle them with two blind readers, at least 8% planted controls, using the S2 method. This set replaces the Google proxy everywhere.
2. **Reader-ensemble gate, with no training.** On the training waves, L1r uses ENSEMBLE_AB:
   - Names come from arm A.
   - A slot is accepted only when arm B predicts the identical mark set.
   - HOLD on K1 flags and on every SF2/C2-B01 uncertainty state.
   - The detector contributes only localisation_unknown, segmentation_uncertain, apostrophes and quotes. Its kind veto is dropped.

   On held-out, PRESENCE and ENSEMBLE_AB are reported side by side. The release manifest carries this caveat verbatim: "A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label experiment."
3. **S8: retune S6 presence and localisation on the step-1 DEV.** Parliament and vouli first. It is judged on presence P/R and on the localisation_unknown rate per wave, and is limited to one iteration using the existing tools.
4. **If step 2 is not enough, R1b:** a second reader with a different seed, window and data order, trained after the cert is renewed. Its outline goes to the coordinator first.

## Deferred cycle-1/2 items and their owners

| Item | Owner |
|---|---|
| M01: correlated supervision and truth provenance | R0 |
| M02: character-indexed fused/unmapped evaluation | R0 |
| M10: straightened, font-normalised R1 view | R2 |
| N02: controlled arm ablation | R2 |
| C2-M03: S7 adapter contract gaps; the adapters stay off | a future S-iteration after the training-wave DEV exists |
