# CP-G1c2 certification — scope and runs

Reviewed the scoped glyph modules, tests, font fixtures, build/evaluation scripts, cycle-1 review/reply, and cycle-2 evidence. Repository files remained untouched; outputs went to scratch. Scoped file hashes remained unchanged during verification.

Ran from the repository root with `.venv/bin/python` and `PYTHONDONTWRITEBYTECODE=1`:

- `pytest tests/glyphs -q -p no:cacheprovider`
- `eval_glyphs.py DIR 300 11 1`
- `skew_eval.py DIR` — 100 straight and 100 bent lines
- `broken_eval.py DIR 150`, `double_eval.py DIR 200`, `mark_stats.py DIR 250`
- Attempted `ink_eval.py DIR`; the script is absent. Evaluated its cycle-2 replacement.
- Full 452-crop artifact rebuild, independent tracking ablation, cycle-1 probes, defect-label/coverage checks, and visual inspection of all 44 line fixtures.

**HOLD — the published metrics and artifact reproduce, but six HIGH correctness or validation failures remain.**

## Findings

### F1 [HIGH] Ink-state truth depends on the detector, and detection failures disappear from metrics

**Locations:** `greekocr/glyphs/evaluate.py:91–93,99–106,122–134`

Broken truth uses the detector’s ink mask, estimated band and x-height. Merged truth uses its component labels. These are not independent reference labels.

**Concrete failure:** Holding the rendered image and all 62 predicted boxes unchanged, moving only the detector’s band outside the image changes:

```text
broken counts before: tn=12, tp=29, fn=13
broken counts after:  tn=25, fp=29
```

The reference classification changes although the image and predictions being assessed do not.

Letters failing the own-ink threshold are also skipped before broken/merged scoring. The full seed-2 run contains **7,621 reliable truth letters**, but only **7,177 broken-state decisions**: **444 letters are unscored**.

Neighbour scoring still conditions its denominator on detected ink. After erasing alternating neighbour components:

```text
truth neighbour pixels: 114
detected/correctly classified pixels: 49
reported neighbour rate: 1.0
actual truth-pixel recall: 49/114 = 0.4298245614
```

Under the full injected-defect run, the reported neighbour rate is **96.20%**, while unconditional truth-pixel recall is **142,849/159,317 = 89.6634%**.

**Fix:** Define reference states independently of estimated bands, labels and segmentation. Enumerate every truth letter, including undetected ones, and report coverage explicitly. Separate neighbour detection recall from classification among detected pixels.

### F2 [HIGH] Coverage checking accepts unsupported combining marks

**Locations:** `greekocr/glyphs/synthetic.py:93–108,169–172,200–210`

The gate checks individual non-combining characters against `.notdef`, but skips combining characters. A supported breathing can make the whole grapheme differ from its stripped base even when another mark is unsupported.

**Failure with the supplied Didot fixture:**

```text
input: 'ἀ\u0304' — alpha with breathing plus combining macron
font_covers: (True, 'ok')
U+0304 renders identically to .notdef: True
render_truth_line: succeeds
truth glyph: reliable=True
MARK pixels: 319
```

Visual inspection confirms an alpha followed by a missing-glyph rectangle. The rectangle enters reliable mark truth.

The current evaluation corpus contains no remaining combining characters after NFC normalization, so these evaluations do not exercise this gap.

**Fix:** Verify every remaining combining character and required mark in a grapheme. Reject partial `.notdef` output at the rendering boundary. Add the combining-macron regression.

### F3 [HIGH] “Middle-region pieces” are actually whole-image components

**Locations:** `greekocr/glyphs/letters.py:47–54,73–79,125`; `greekocr/glyphs/ink.py:63–67`

`_mid` filters component evidence, but `pieces` ultimately counts original components rather than connected pieces inside the band.

**Failure:** A letter split into two vertical arcs is correctly called broken. Connecting those arcs **only above the band** changes it to intact:

```text
middle-region connected pieces: 2
before outside connection: pieces=2, state=broken
after outside connection:  pieces=1, state=intact
```

The failure remains when the band is explicitly fixed at **y=20–44**. Thus pixels outside the required measurement region change the ink state.

**Fix:** Label connected pieces after restricting ink to the per-column band. Perform grouping and piece counting on that representation, retaining mappings to original components.

### F4 [HIGH] A faint body attached to one dark stroke is discarded and called intact

**Locations:** `greekocr/glyphs/components.py:71–79`; `greekocr/glyphs/ink.py:45–51,61–71`

The faint channel adds a component only when it contains **no** Sauvola ink. One dark stroke therefore prevents recovery of the connected faint body.

**Failure:** On paper gray 235, one hollow letter has body gray 195 and a connected dark four-pixel-wide stroke:

```text
true letter ink pixels: 388
retained ink pixels:     96
lost pixels:            292
returned box:           x=130–134
state:                  intact
contrast:               1.0
```

The localized score reports no problem despite losing most of the letter.

The original five-faint/five-normal probe passes, but it does not cover contrast variation within a letter.

**Fix:** Recover plausible weak strokes connected to strong ink, with paper/noise controls. Add this mixed-contrast letter regression and measure truth-letter coverage under fading.

### F5 [HIGH] Fully fused letters receive an intact score

**Locations:** `greekocr/glyphs/letters.py:113–125`; `greekocr/glyphs/ink.py:68–71`; `tests/glyphs/test_glyphs.py:157–172`

Merged status is assigned only when a thin bridge permits splitting. A fully fused blob without such a bridge falls through to `merged=1`, hence intact.

**Failure:** Ten solid 22×24 bodies are initially ten intact boxes. Filling the gap between two bodies produces:

```text
boxes before: 10
boxes after:   9
fused box:     x=130–192
pieces=1, merged=1, state=intact, score=0.0
```

This is a concrete over-inking failure.

The thick regression passes with only **4/23 affected boxes flagged**, versus **12/112 unaffected boxes**. Its factor-1.3 comparison permits **19/23 affected boxes to be missed**.

**Fix:** Separate merged detection from successful splitting. A demonstrably fused multi-letter blob must retain a positive state or explicit unresolved-merge warning even when individual cuts cannot be recovered.

### F6 [HIGH] Defect labels still leak across split boxes

**Locations:** `scripts/glyphs/eval/broken_eval.py:22–25`; `tests/glyphs/test_glyphs.py:165–167`

`own` selects every pixel of a box’s component IDs across the entire image. Split boxes share those IDs, so each receives defect votes from the complete merged blob.

**Firsthand seed-2 results:** Restricting votes to the actual box changes **44 defect assignments**.

At line index **24**, `LibertinusSerif-Regular.otf`:

```text
shared component truth:
  no defect: 83 pixels
  thick:    405 pixels

box x=511–518:
  actual box truth: 21 pixels, all no defect
  current label: thick

box x=518–527:
  actual box truth: 38 pixels, all no defect
  current label: thick
```

The transformed defect maps are correct; their spatial assignment to boxes remains wrong.

**Fix:** Restrict component membership to each box’s bounds, preferably matching to truth glyph IDs. Apply the correction to the evaluator and regression test, then rerun per-defect results.

### F7 [MEDIUM] Instructions and benchmark provenance do not describe the current package

**Locations:** `scripts/glyphs/eval/README.md:12–17`; `docs/GLYPHS_PLAN.md:89–94`; `scripts/glyphs/review_page.html:90,228`

Several assertions cannot be followed or reproduced as stated:

- `ink_eval.py` and `xh_est.py` are absent. The documented seed-1 weight fit no longer describes the rewritten state model.
- The owner crop currently gives **31.60–31.79% visibility** over its first 180 columns, rather than the documented **0–6%**. Its angles are **2.209° with prior 26**, and **1.820° with prior 21**.
- Disabling only current tracking/model selection gives **78/100 → 45/100** bent-line failures, not **84 → 45**. The historical 84% baseline lacks a reproducible bound revision/run here.
- The plan says validation is straight-only, although the current skew evaluator includes bent lines.
- No explicit fixture-label manifest identifies the claimed seven doubles and twenty singles. The current implementation flags **9/44 fixtures**; this does not establish the quoted subset result.

**Fix:** Update instructions and owner-case measurements; bind historical comparisons to code/data/seed receipts; publish the provisional fixture labels and exclusions. Explicitly describe the owner’s unsupported leading extrapolation and distinguish ordinary-render merged metrics from injected-defect metrics.

## Cycle-1 findings rechecked

| Original finding | Fixed? | Firsthand result |
|---|---|---|
| F1 — detection-conditioned recall | **Not fixed completely** | Accent deletion now gives **6/12 = 0.5**. Neighbour deletion still gives **1.0 instead of 49/114**; see current F1. |
| F2 — fabricated ink, capitals, rotated boxes | **Fixed for the original failures** | Bodoni `ἀ`: **263 actual = 263 synthetic**, zero fabricated; **226 LETTER + 37 MARK**. NotoSans-Bold `Ἡ`: **618 IGNORE**, unreliable. Independently rotated boxes: **0/55 mismatches**. |
| F3 — wrong defect type/unrotated truth | **Not fixed completely** | Independently rotated kind/intensity maps match. **44 box-local defect assignments remain wrong**, current F6. |
| F4 — outside-band measurement | **Not fixed completely** | Original tail probe returns ten unchanged zero scores. An outside-only connection still changes broken to intact, current F3. |
| F5 — faint letters vanish | **Not fixed completely** | Original probe returns ten letters, five faint. Mixed-contrast body loses **292/388 pixels** and reads intact, current F4. |
| F6 — incomplete font gate | **Not fixed completely** | Elpis spacing breathing and XCharter probes now reject. Unsupported combining macron still passes, current F2. |
| F7 — censored calibration | **Fixed** | Live seed-5 script includes small candidates regardless of predicted role. Its output exactly reproduces supplied `mark_stats.txt`. |
| F8 — non-finite JSON | **Fixed** | Blank record serializes with `allow_nan=False`; residual is `None`, confidence low. Full artifact rebuild also uses strict serialization. |

The **0.75 Didot letter floor** and **2/4 double-line FP ceiling** are honestly disclosed but weak guards. Actual letter rates are **1,064/1,356 = 78.47%** without neighbours and **1,147/1,356 = 84.59%** with neighbours. The double test yields **4/4 TP and 2/4 FP**. Neither guard establishes general accuracy. The thick factor-1.3 test specifically hides the substantial merged-detection failure documented in F5.

## Claims re-derived

“Reproduces” below means the current instrument returns the number; it does not clear its validation defects.

| Claim | My number | Holds? |
|---|---|---|
| 25 offline tests | **25 passed, 13.87 s** | Yes; passing tests miss the HIGH failures |
| Separate accents found 97.95% | **97.95%; all-accent found rate 73.09%** | Reproduces the stated separate-accent rate |
| Accents detected 99.97%; fused 25.4% | **99.97%; 25.38%; 3,984 truth marks** | Reproduces |
| Mark component precision 96.1% | **96.06%** | Reproduces |
| Neighbour ink pixels 97.3% | **97.26% among detected truth pixels** | Conditional number reproduces; not detection recall |
| Letters one box 92.8%; lost 1.0% | **92.75%; 0.99%** | Reproduces |
| Straight skew median 0.009° | **0.009°** | Yes |
| 95 high-confidence fits; maximum 0.515° | **95/100; 0.515°** | Yes |
| Large medium/low misses ≈3.8°, 10.4° | **3.75°, 10.38°** | Yes |
| Bent failures 84% → 45% | **Current tracking ablation: 78% → 45%** | Final 45% holds; historical 84% not re-derived |
| Straight fits unaffected by tracking | **0/100 changed maximum errors** | Yes on this cohort |
| Broken recall 82%; precision 78% | **82.21%; 77.68%; TP=268, FP=77, FN=58, TN=6,774** | Reproduces; detector-dependent truth and omitted letters invalidate independent certification |
| Merged precision 99.5%; recall 74% | **Seed 11: 99.53%; 73.70%** | Reproduces on ordinary renders |
| Merged performance under injected defects | **Seed 2: precision 99.80%; recall 61.28%** | Different cohort; must be distinguished |
| Faint letters detected and flagged | Original probe passes; mixed-contrast probe retains **96/388**, calls intact | Not generally |
| Rendered doubles: recall 95%, precision 74% | **TP=95, FN=5, FP=33, TN=67; 95.0%, 74.21875%** | Yes |
| Real doubles 7/7, singles 0/20 | **9/44 flags; claimed label subset unavailable** | Not independently established |
| Seed-5 threshold evidence | Above 0.40: **0.25% own ink rejected, 0.27% neighbours kept**; below 0.30: **0%, 0.59%** | Live script/evidence agree |
| Owner prior 26 px; re-cut 21 px | **26 / 21 px**, re-cut source `substantial_letters` | Yes |
| Artifact from 452 crops matches code | **452 rebuilt; all 26 records identical**, excluding timestamp | Yes |
| Published page embeds supplied data | Exact template-plus-JSON match | Yes |
| `ink_eval.py`, seed-1 weights/AUC workflow | Script absent; weighted model replaced | No longer applicable |

## Cleared items

- No PDF text-layer or OCR-reader reference/gate was found in scoped analysis/build code or non-image artifact data.
- Outputs are localized along x: bands, visibility, cut spans, letter states and second-band curves.
- Independent clipping probes recover x-height **24**, top visibility **0.75**, bottom visibility **0.50**, ten cut letters, and the appropriate remaining-edge evidence. Tested angle/trail and crossing directions are consistent.
- Document-prior use and the `substantial_letters` switch reproduce. Tracking improves the measured bent cohort while preserving this straight cohort.
- Fixture fonts are byte-identical to their declared source copies. Original fabricated-pixel and rotated-box failures are repaired.
- The page discloses disjoint-text fit failures, partial-second-line limitations and uniformly faint-line self-comparison. Its artifact data is reproducible; documentation needs the corrections in F7.
- Neighbour calibration uses seed 5, measurement uses seed 11, and injected-state evaluation uses seed 2. The former seed-1 learned-weight claim applies to the removed model.

VERDICT: HOLD Fix all six HIGH findings before commit or P2; fix or explicitly defer F7 in the reply. | BLOCKERS: 0 | HIGH: 6