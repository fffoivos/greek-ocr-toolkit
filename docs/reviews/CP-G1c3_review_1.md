# CP-G1c3 — independent fix certification

**HOLD — F2–F6 pass the reproduced probes; F1 still miscounts detected faint letters, and F7 remains partially corrected.**

## Findings

### [HIGH] F1: detected, visible letters are forced to `vanished->missed`

**Location:** [evaluate.py:132](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/glyphs/evaluate.py:132), lines 132–146 and 149–162.

Both truth modes use the **50% contrast mask** to declare letters vanished—even for the declared **25% visible truth**. That branch then supplies empty prediction hits without checking whether boxes actually detected those letters.

**Reproduction:** Didot, size 40, `degrade=False`, `ink_defects=[(.2,.6,'fade',.8)]`. Physical ink survives at 35.7% contrast, above the declared visible threshold.

| Measurement | Raw result |
|---|---:|
| Reliable truth letters | 54 |
| Detector boxes | 55: 34 intact, 21 faint |
| PRINT reports vanished / missed | 20 / 20 |
| VISIBLE reports vanished / missed | 20 / 20 |
| Those 20 actually visible and matched to faint boxes | **20 / 20** |

Example ε at `(283,49,299,68)`: **132 physical pixels, 132 visible(.25) pixels, zero midpoint pixels**, with a matching faint box. Both evaluations nevertheless record it as missed.

The independent regression fails in both modes: **`assert 20 == 0`**.

On the actual **N=150, seed-2** defect cohort, the reported **717 vanished / 717 missed** include:

- **435** letters meeting the physical-print area threshold.
- **389** meeting the declared quarter-contrast visibility threshold.
- **361** with matching detected boxes: **183 under**, **170 intact**, **8 merged**.

Thus “717 vanish without a per-letter warning” is not a measured outcome. The reference inputs are now detector-independent, but coverage and state confusion still discard real predictions.

**Fix:** Apply each truth definition consistently; separate visibility from detection coverage; match actual predictions without forcing empty hits from a visibility label. Retain this regression and rerun both cohorts before multi-line tracking.

### [MEDIUM] F7: documentation corrections are incomplete

**Locations:** [GLYPHS_PLAN.md:24](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/GLYPHS_PLAN.md:24), lines 24–26 and 86–92; `scripts/glyphs/review_page.html:89–93`.

- The plan retains owner visibility **0–6%** and angles **2.4° / 2.0°**. Live results are **31.6047–31.7894%** over the first 180 columns, with angles **2.209° / 1.820°** for priors 26/21.
- “State 16:05” omits PRINT broken recall: **157/636 = 24.69%** ordinary and **189/470 = 40.21%** with defects.
- The template still claims **84%→45%**, broken **82%/78%**, and merged **99.5%/74%**. The artifact is explicitly awaiting rebuilding; these claims remain stale.
- The reply claims a permanent combining-macron regression, but `test_glyphs.py:51–56` contains no macron case. The live functionality passes.

**Fix:** Correct the plan’s measurements and both truth summaries after F1; keep deferred artifact claims explicitly historical. Add the promised regression or correct that claim.

## Per-finding fix table

| Finding | Fixed? | Firsthand result |
|---|---|---|
| **F1 — truth independence and coverage** | **Not completely** | Moving the detector band outside, tripling its x-height, erasing ink, or erasing ink/labels/components preserves both truth counts. Neighbour erasure now reports **306/599 recall**, separately from **306/307 conditional classification**. False vanished/missed accounting remains above. |
| **F2 — unsupported combining marks** | **Fixed** | Didot `ἀ\u0304` returns `False: U+0304 is .notdef`; rendering raises `UnsupportedText`. |
| **F3 — middle-region pieces** | **Fixed** | With band fixed at **y=20–44**, arcs remain **2 pieces, broken, score −0.5**, including when connected only above the band. |
| **F4 — mixed-contrast body discarded** | **Fixed for reported failure** | Retains **340/388 pixels**, versus 96 previously; box **130–152**, contrast **0.186**, broken, score **−0.5**. **48 pixels** remain unrecovered. |
| **F5 — fully fused letters intact** | **Fixed** | Ten intact bodies become **8 intact + 1 unresolved merged box**, at **130–192**. Thick cohort: **n=271**, merged fraction **0.956**. |
| **F6 — defect votes leak between split boxes** | **Fixed** | Independent coordinate-bounded masks match `_box_map` throughout 150 lines. Restoring legacy whole-component voting changes **48 assignments** on the current cohort. |
| **F7 — documentation/provenance** | **Not completely** | README and fixture manifest improve reproducibility; remaining inaccuracies are listed above. |

## Claims re-derived

Scoped files match **`7f61e32`**; reviewed diff **`6df1fca..7f61e32`**. Repository remained untouched. All Python runs used its `.venv`, `PYTHONDONTWRITEBYTECODE=1`; pytest used `-p no:cacheprovider`. No background jobs were started.

- Committed tests: **30 passed in 15.19 s**.
- Independent faint-visibility regressions: **2 failed in 0.57 s**.
- `eval_glyphs.py DIR 300 11 1`: output exactly matches its `evals_v6.txt` section.
- `broken_eval.py DIR 150`: unchanged script executed through an observation wrapper; output exactly matches its evidence section.

These reproduce the instrument, subject to the HIGH finding:

| Cohort / truth | Broken recall | Under precision | Merged recall | Merged precision |
|---|---:|---:|---:|---:|
| Ordinary, PRINT | **157/636 — 24.69%** | 157/327 — 48.01% | 66/78 — 84.62% | **66/1,835 — 3.60%** |
| Ordinary, VISIBLE | 135/253 — 53.36% | 135/327 — 41.28% | 1,599/2,487 — 64.29% | 1,599/1,835 — 87.14% |
| Defects, PRINT | **189/470 — 40.21%** | 189/279 — 67.74% | 382/388 — 98.45% | **382/1,414 — 27.02%** |
| Defects, VISIBLE | 182/290 — 62.76% | 182/279 — 65.23% | 1,197/1,501 — 79.75% | 1,197/1,414 — 84.65% |

Ordinary cohort: **15,067 truth letters**, reported **327 missed / 231 vanished**. Defect cohort: **7,595**, reported **717 missed / 717 vanished**; the latter are demonstrably incorrect detection counts.

Marks: **3,624**, separate accents found **98.74%**, all accents **75.44%**, precision **95.22%**. Neighbour recall: **97.12%**.

Definitions were fixed before this rerun and use renderer inputs. Historical absence of tuning is not independently established; the reply documents revising the v5 reference after inspecting results. The concrete remaining problem is inconsistent application of the declared definitions.

## Cleared

- **Truth independence:** both state truth counts withstand detector mutations; neighbour recall has an independent denominator.
- **Skew:** 100 straight lines reproduce median **0.009°**, p99 **0.982°**, maximum **4.552°**; 95 high-confidence fits have maximum **0.217°**. Bent failures reproduce **34/100**.
- **line04:** x-height **27**, support begins **x=16**, baseline at x=120 **40.7069**, top crossing **x=981.5185**; double flag false.
- **Document prior:** independently rederived **26 px from 3 qualifying crops**; recut measures **21 px**, `substantial_letters`.
- **Artifact/JSON:** line04 and both owner records match supplied generated fields; strict JSON serialization passes, including the committed blank-crop test.
- **Fixtures:** **7/7 doubles**, **0/20 singles**, **2/17 partials**, **9/44 total**, with in-sample calibration disclosed.

[Full report and reproduction files](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/CP-G1c3/CP-G1c3_review_1.md).

VERDICT: HOLD Fix false vanished/missed accounting before multi-line tracking; correct or explicitly defer remaining documentation issues. | BLOCKERS: 0 | HIGH: 1