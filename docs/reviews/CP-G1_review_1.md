# CP-G1 certification — scope and runs

Reviewed the specified glyph package, tests, fonts, evaluation/build scripts, and supplied artifact evidence. Repository files remained untouched; outputs went to scratch.

Ran `.venv/bin/python` from the repository root with `PYTHONDONTWRITEBYTECODE=1`:

- `pytest tests/glyphs -q -p no:cacheprovider`
- `eval_glyphs.py DIR 300 11 1`
- `skew_eval.py DIR`
- `ink_eval.py DIR` against a scratch copy because it writes `ink_coef.npy`
- `mark_stats.py DIR`, `xh_est.py DIR`
- Full artifact-data rebuild and comparison; independent probes of missing accents, font coverage, rendered truth, rotated boxes, clipping, ink measurement and JSON serialization.

**HOLD — the published numbers reproduce, but validation defects and two ink-detection failures prevent certification.**

## Findings

### F1 [HIGH] “Mark recall” ignores missing marks

**Location:** `greekocr/glyphs/evaluate.py:48–50,79–81`

The confusion matrix counts only components that the detector retained. An accent lost during binarisation never contributes a false negative.

**Failure:** An independently constructed line contained ten known accents. I deleted five from the observed image while preserving all ten in truth. The evaluator returned:

```text
detected accents: 5
confusion: letter->letter 10, mark->mark 5
marks_called_mark: 1.0
mark_precision: 1.0
actual accent recall: 5/10 = 0.5
```

Consequently, 99.07% measures classification among retained components, not the claimed percentage of accents found. The neighbour percentage has the same detection-conditioned denominator and counts components rather than ink pixels.

**Fix:** Match predictions against independently enumerated truth marks, including unmatched truth marks as false negatives. Report detection coverage separately from component classification. Add the five-missing-accents regression.

### F2 [HIGH] Synthetic “truth” fabricates ink and mislabels body differences as marks

**Location:** `greekocr/glyphs/synthetic.py:114–145,185–209`; `greekocr/glyphs/evaluate.py:49–56`

The stripped base and full accented grapheme can render different body positions or shapes. The generator nevertheless unions the base into the image and labels `full & ~base` as marks.

**Failures, size 48, degradation disabled:**

| Accepted font / glyph | Actual full-glyph ink pixels | Synthetic ink pixels | Fabricated pixels |
|---|---:|---:|---:|
| GFSBodoni-Regular.otf / `ἀ` | 263 | 329 | 66 |
| NotoSans-Bold.ttf / `Ἡ` | 618 | 1,058 | 440 |

For `ἀ`, 60 of the 101 purported mark pixels fall inside the base bounding rectangle.

Also, `docs/GLYPHS_PLAN.md:75` says marked capitals are excluded from mark scoring. The code excludes them only from letter-box scoring; component confusion still includes their unreliable mark truth.

Rotated boxes introduce another, smaller bias: independently rotating base masks on 100 seed-11 lines produced different boxes for **5,157/5,160 glyphs**, with maximum edge difference **2 px**. One-box detection changed from **4,823/4,991 = 96.63%** to **4,818/4,991 = 96.53%**.

**Fix:** Render the actual full grapheme without adding base pixels. Independently validate aligned body/mark masks; exclude unsupported marked-capital truth from both metrics. Derive final boxes from transformed masks. Re-run the affected evaluations.

### F3 [HIGH] Ink evaluation assigns the wrong defect type

**Location:** `scripts/glyphs/eval/ink_eval.py:24–29`; `greekocr/glyphs/synthetic.py:167–197`

The evaluator selects the first injected defect with the same sign, regardless of its location.

**Failure:** Seed-2 line 11 injects thinning at approximately 44–71% and fading at 3–21%. The box at **x=79–107** lies in the faded region but is labeled `thin`.

Across the full seed-2 run, **177 qualifying boxes with a single defect type were mislabeled**. Correcting only type assignment, while retaining the existing coordinate convention and excluding four mixed-type boxes, gives:

| Defect | Original count / AUC | Corrected count / AUC |
|---|---:|---:|
| Fade | 301 / 0.932286 | 356 / 0.970932 |
| Thin | 273 / 0.953606 | 178 / 0.944578 |
| Break | 458 / 0.834124 | 496 / 0.820976 |
| Thick | 363 / 0.976121 | 361 / 0.976040 |

Additionally, `ink_truth` remains unrotated while the image rotates. A Didot size-40 probe, seed 2, rotation **−1.633660850°**, mislabels defect membership for **4/8,417 main-line truth pixels**.

**Fix:** Preserve defect kind and intensity spatially, apply the image’s rotation/crop to that truth, and assign box labels from its actual region. Handle mixed defects explicitly.

### F4 [HIGH] Ink features violate the required band restriction

**Location:** `greekocr/glyphs/ink.py:48–64`; owner constraint at `docs/GLYPHS_PLAN.md:44`

Features use the entire letter rectangle rather than restricting measurement to the meanline–baseline band. Density divides that unrestricted ink count by band area.

**Failure:** Ten identical hollow bodies have band **y=20–44**, x-height **24**. Adding a connected tail entirely below the band, **y=44–72**, leaves the body and fitted band unchanged but changes:

```text
density: 0.3333333333 → 1.3833333333
ink score: −0.042 → +0.3033
```

The unchanged body becomes “over-inked” solely because of pixels outside the required measurement region.

**Fix:** Restrict feature measurements to the per-column band, including consistent treatment of stroke measurements and fragments. Add an outside-band invariance regression and recalibrate the changed features.

### F5 [HIGH] Faint letters disappear without a localized under-ink warning

**Location:** `greekocr/glyphs/components.py:44–57`; `greekocr/glyphs/ink.py:79–89`

The binarizer’s claim that faint strokes remain available for separate darkness measurement does not hold.

**Failure:** On paper gray **235**, ten identical bodies retain all **3,520 ink pixels** at ink gray **180**, but retain **zero** at ink gray **195**.

With the first five letters at gray 195 and the remaining five at gray 20:

```text
faint-region pixels retained: 0 / 1,760
remaining letter profiles: 5
remaining scores: all −0.042
under-ink warnings: 0
```

The faint start receives no letter scores. The artifact acknowledges vanished thinned letters, but this also affects fading. `ink_eval.py` evaluates surviving detected boxes, so its AUC does not measure this failure.

**Fix:** Retain faint strokes with suitable paper/noise controls, or emit explicit localized insufficient-ink evidence. Include truth-letter coverage in ink evaluation. Add this mixed faint/normal regression.

### F6 [HIGH] Font coverage checking does not cover every required input

**Location:** `greekocr/glyphs/synthetic.py:26,59–71,96–97`

The fixed probe does not check all characters actually rendered, and the public renderer does not enforce coverage.

**Failures:**

- `GFSElpis-Regular.otf` passes the gate, but required spacing breathing **`᾿` U+1FBF** renders identically to `.notdef`.
- The full seed-11 evaluation actually selects this font with neighbour text containing **`᾿Ιορδάνης`**, at line index **185**.
- XCharter correctly fails the gate, yet `render_truth_line('ἀἁἄἅ', XCharter, degrade=False)` silently produces an image.

**Fix:** Check the actual main and neighbour graphemes before rendering, with cached checks if needed. Enforce rejection at the rendering API boundary.

### F7 [MEDIUM] The calibration script censors data using its calibrated classifier

**Location:** `scripts/glyphs/eval/mark_stats.py:15–21`

Only predicted `mark`/`punct` components enter gap statistics. Components already classified as neighbours are excluded using the very thresholds being justified.

**Failure:** The current seed-5 run reports neighbour gap percentiles:

```text
above: [0.06, 0.24, 0.31, 0.35, 0.39]
below: [−0.38, −0.16, 0.16, 0.24, 0.29]
```

These are censored misclassification distributions, not evidence for the stated neighbour separation of ≥0.63 above / ≥0.36 below.

**Fix:** Collect candidates independently of predicted role and publish uncensored calibration statistics and threshold-selection evidence. Seed separation alone does not resolve this circularity.

### F8 [MEDIUM] “JSON-ready” records contain non-finite values

**Location:** `greekocr/glyphs/baseline.py:101,124`; `greekocr/glyphs/report.py:90–91`

**Failure:** A valid blank 320×60 image produces `residual_px = nan`. Strict serialization fails:

```text
json.dumps(record, allow_nan=False)
ValueError: Out of range float values are not JSON compliant
```

The existing test uses permissive `json.dumps`, which misses this failure.

**Fix:** Represent unavailable residuals as `None` and require strict JSON serialization in the contract test.

## Claims re-derived

| Claim | My number | Holds? |
|---|---|---|
| 13 offline tests | **13 passed**, 3.92 s | Yes; inadequate regression coverage |
| 31 accepted evaluation fonts | **31** | Count yes; coverage guarantee fails F6 |
| Mark recall 99.07% | **99.07%** | Reproduced; not actual recall, F1/F2 |
| Mark precision 97.51% | **97.51%** | Reproduced; truth compromised, F2 |
| Neighbour ink 98.70% | **98.70%** | Reproduced conditional component rate, F1 |
| Letters in one box 96.42% | **96.42%** | Reproduced; truth-box bias, F2 |
| Lost 0.95%; merged 1.67% | **0.95%; 1.67%** | Reproduced under existing truth |
| Skew median/p90/p99 | **0.010° / 0.064° / 0.368°** | Yes |
| Skew >0.25°: 3.0% | **3.0%**, maximum **0.544°** | Yes |
| Ink over/under AUC | **0.976 / 0.894**, 6,729 boxes | Reproduced; surviving-box evaluation |
| Fade/thin/break AUC | **0.932 / 0.954 / 0.834** | Reproduced; defect-type claims fail F3 |
| Normal fitted-score p5/p50/p95 | **−0.223 / −0.037 / 0.129** | Yes under existing instrument |
| Plain x-height median error 7.1% | **7.1%** | Yes |
| line04 rises ~40 px; exits top x≈1079 | Trail **−39.57 px**; crossing **x=1079** | Yes |
| Owner prior 26 px; re-cut estimate 21 px | **26 / 21 px** | Yes |
| Owner angle ~2.4° / ~2.0° with those priors | **2.365° / 1.919°** | Approximate |
| Artifact has 20 matching records | **20/20 identical**, excluding build timestamp | Yes |

## Cleared items

- No PDF text-layer or OCR-reader reference/gate was found in scoped analysis/build code or artifact data.
- The published HTML embeds the supplied JSON exactly and matches the current template plus that JSON.
- The page explicitly discloses straight-only validation and the inaccurate extrapolation in the owner example.
- Independent clipping probes recover x-height **24**, visibility **0.75** for top clipping and **0.50** for bottom clipping, with ten cut letters and the correct remaining-edge evidence. Skew/trail and tested crossing signs are consistent.
- The re-cut owner crop activates `substantial_letters` and estimates **21 px**. Document-prior use is reproduced.
- Both fixture fonts are byte-identical to their declared local source copies.
- Ink coefficients fitted on seed 1 reproduce the installed rounded weights and bias; evaluation uses seed 2. The scripts use distinct calibration/evaluation seeds.
- Outputs are localized along x. The 13 passing tests cover basic rendering, splitting, skew and selected injected defects, but would not catch the failures above.

VERDICT: HOLD Fix the six HIGH findings before commit or P2; fix or explicitly defer both MEDIUM findings. | BLOCKERS: 0 | HIGH: 6