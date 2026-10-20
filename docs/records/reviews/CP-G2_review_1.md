# CP-G2 — independent certification

**HOLD — two HIGH findings require fixes before the next feature step.** Full evidence and reproductions are in [CP-G2_review_1.md](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/CP-G2/CP-G2_review_1.md).

## Findings

1. **HIGH — rejected histogram peak hides another valid neighbour.**  
   [baseline.py:265](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/glyphs/baseline.py:265): failing the three-vote check executes `break`, abandoning the entire side. An end-to-end image returns a neighbour at **baseline 9, votes 3**. Adding one separate glyph changes the result to **main only**, while the main band remains exactly **60–80**. Skipping the rejected peak in scratch restores baseline 9.  
   **Fix:** Continue searching other peaks; count accepted lines toward the output limit. [Raw reproduction](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/CP-G2/peak_probe_e2e.txt).

2. **HIGH — neighbour evaluation does not establish honest matching or false-line counts.**  
   [neighbour_eval.py:23](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/scripts/glyphs/eval/neighbour_eval.py:23): any same-side prediction counts as found, regardless of error. False counting ignores presence and unmatched predictions, and is never printed. Deliberately misplaced predictions produce **5/5 found, zero missed, zero false**, despite **2.768–3.420 x-height errors**.  
   The actual cohort has **192 predictions / 191 side hits**. One prediction corresponds to only **28 visible truth pixels**, below the evaluator’s 30-pixel presence threshold, yet its false counter stays zero.  
   **Fix:** Define geometric matching, assign predictions uniquely, print unmatched predictions, and distinguish conditional placement accuracy from unconditional recall. Correct [the page claim at line 87](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/scripts/glyphs/review_page.html:87).

3. **MEDIUM — two paper specks invent a neighbour.**  
   [baseline.py:250](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/glyphs/baseline.py:250): two **4×3** specks above ten main bodies generate **above −2.889, votes 3.6, visible 1.0**. Alternative hypotheses from the same fragments pass as sufficient support.  
   **Fix or explicitly defer:** Require independent/spatial support or expose uncertainty for sparse candidates; retain the negative regression.

4. **MEDIUM — “every neighbour” exceeds the implemented limits.**  
   [baseline.py:257](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/glyphs/baseline.py:257): visible neighbour baselines **50 and 84**, separated by **1.7 x-heights**, return **50 only**. Three neighbours at shifts **−5.4, −3.4, −1.4**, all inside the range and spaced two x-heights apart, return only two.  
   **Fix or explicitly defer:** Support additional/closer lines, or disclose the **two-per-side cap, 1.3–6 x-height range, 1.8 separation**, shared-shape assumption and ambiguous fragment placement.

5. **MEDIUM — superseded vanished count remains in the plan.**  
   [GLYPHS_PLAN.md:103](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/GLYPHS_PLAN.md:103) still says **717/7,595** vanish without warnings. Current PRINT truth gives **282 vanished: 253 missed, 23 under, 6 intact**; VISIBLE truth gives **328 vanished**.  
   **Fix:** Replace the stale count and distinguish disappearance from detection/warning coverage.

6. **LOW — singleton support reports zero visibility.**  
   [baseline.py:239](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/glyphs/baseline.py:239): **x0=x1=51** reports **visible 0.0**, although its guide body is fully inside at that column.  
   **Fix:** Include singleton intervals or use supported component extents.

## Claims re-derived

The ordinary, defect and neighbour outputs match the supplied evidence **exactly**.

| Claim | Independent result |
|---|---|
| Neighbours “found” | **191/199 = 95.98%**, meaning same-side coverage |
| Conditional placement median | **0.0556498 x-heights** |
| Within 0.25 / 0.5 | **141/191 = 73.82% / 166/191 = 86.91%** |
| Same shares including misses | **141/199 = 70.85% / 166/199 = 83.42%** |
| Reviewer-selected 0.5 matching gate | **166 TP, 33 FN, 26 unmatched predictions** |
| Committed tests | **34 passed** |
| Independent adversarial regressions | **5 failed, 1 warning** |
| Real double fixtures | **7/7 doubles, 0/20 singles, 2/17 partials** |
| Rendered doubles | **93 TP, 7 FN, 30 FP, 70 TN**; precision **75.61%** |

The remaining page facts reproduce: **98.74%** separate-accent recall, **95.22%** component precision, **97.12%** neighbour-ink recall, **0.217°** worst high-confidence skew error, and **34/100** bent-line failures. Its VISIBLE state-rate ranges are correctly rounded.

Batch 4 rebuilds **40 records from 408 unseen crops**, with IDs and order matching the manifest. Batch 3’s **40 current records** reconstruct successfully. **Published-page equivalence and historical “before” summaries remain unverified:** both URLs were inaccessible through available tools, and the original earlier-batch JSONs were unavailable.

## Cleared

- CP-G1c3 vanished/missed fix; both fade regressions pass.
- Neighbour truth follows rotation, bend and crop: **45 independent transform checks**.
- All **80 reconstructed records** preserve guide ordering; drawing code generates **732 guide paths**.
- line04, owner visibility/prior, skew and four-line b1ce regressions remain consistent.
- All **26 supplied legacy records** retain compared numerical/image fields.
- Repository remained read-only; **23 scoped hashes unchanged**. No background jobs started.

VERDICT: HOLD Fix rejected-peak termination and honest neighbour matching/counts before the next feature step; fix or explicitly defer remaining findings and verify published pages. | BLOCKERS: 0 | HIGH: 2