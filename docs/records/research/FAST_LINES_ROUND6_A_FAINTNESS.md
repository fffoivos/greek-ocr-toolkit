# Round 6 A: relative faintness of the final OCR segment

Task A starts at `11ef67a`. It adds **140 removals on 30 of the 208 supplied pages**, after the existing round-5 operators. Every surviving polygon is identical to round 5. Of the 40 agreement-page outputs, 39 are unchanged; `s2-d12a9a4feb23254f4080-p00012` loses one faint bottom smudge. All 256 owner-marked row segments are unchanged. This is a useful partial answer: blurred show-through and isolated watermark lettering now have a removal rule, but ambiguous dark fragments still protect some unwanted segments, and negligible cost on every clean page is not achieved.

The [208-page gallery](../../../.astra/fast_lines/out/round6/A_faintness/final/index.html), [verbatim owner comments and outcomes](../../../.astra/fast_lines/out/round6/A_faintness/final/COMMENTS.md), and [every owner-row record](../../../.astra/fast_lines/out/round6/A_faintness/final/owner-marks.json) are local artifacts outside git. The [artifact README](../../../.astra/fast_lines/out/round6/A_faintness/README.md) explains colours, indices, intermediate failures and commands. No held-out page was accessed. No production `greekocr/pages/` source or test was changed. Splitting and curvature are left for tasks B and C.

## What the rendering measures

The owner's distinction is the rule: a segment that has faint material is different from a segment whose observed letters are faint throughout. Faintness is contrast against this page's print; stroke width is a separate measurement. A thin dark letter can be normal, and a thick blurred ghost can be faint. Neither axis establishes a character's identity or semantic readability.

The slow rendering uses the actual final R5 polygon, with one letter-height of surrounding image for paper estimation. It finds local ink components, measures original stroke-core contrast, a protective 90th-percentile stroke contrast, and distance-transform stroke width. The rendered components are observed ink pieces, not recognized characters: accents can be separate, joined letters can remain joined, and damage can fragment a letter. Oversized or small components are also allowed to preserve normal ink; an unmodelled connected word must not silently disappear from the preservation decision.

The own-page reference starts from the median contrast of the upper half of letter-sized components, following the useful reference idea in `greekocr/pages/statistics.py`. Its spread is measured across the whole observed component population. A broad distribution makes the faint boundary conservative, preserving the pale front print on `an-1be60011c435-p000215`. Unlike the older box-level darkest-decile statistic, each segment exposes its normal-component count, total body count, normal share, supporting component locations, and faintness decision.

The lower normal boundary is the smaller of (a) reference contrast minus three robust deviations and (b) the midpoint between paper and the reference print in optical density. With reference contrast `c`, the latter is `1 - sqrt(max(1-c, 1/255))`. The one-DN interval prevents a saturated black reference from making every slightly grey letter faint. This is a model of proximity to paper versus print, not proof of front/back ownership. The spread term can only lower this boundary. Each component must remain below it after adding the measured noise margin; its original stroke peak protects thin dark strokes from a misleading pale ridge statistic.

A normal run is witnessed by a sufficiently complete normal component or neighbouring normal components. An unclipped component at least half the reference body height preserves the segment; a clipped one must reach the full reference height. A nearby pair can preserve shorter letters. Tiny pieces cut from a neighbouring row cannot alone count as a whole letter. The final rule requires faint letter-sized bodies, adequate page reference support, and no normal witness. It does not require every dark pixel to be faint: isolated dust and boundary fragments are explicitly distinguished from a normal run. Borderline cases are retained.

### Settings and their limits

No runtime setting depends on a page name. Lengths use the detector-derived height proxy `h`, which remains an imperfect scale estimate. Component bodies span `.25h–2h` vertically and `.07h–3h` horizontally; minimum retained area is `.006h²`, with a three-pixel discretization floor. Paper uses a `2h` closing window, floored by the surrounding ROI's 90th percentile so a solid black component cannot become its own black paper. Native median paper is used for the slow noise estimate. A 3×3, sigma .6 blur and local Otsu silhouette locate ink; noise uses bright adjacent-pixel differences divided by .954, at least one DN, with a three-noise margin. Stroke width is twice the distance-transform ridge radius of the component's half-peak silhouette. These numerical estimator/discretization choices are documented implementation settings, not universally validated physical constants.

The robust spread multiplier is 1.4826, its envelope multiplier is 3, and reference support must contain at least 12 upper-half bodies. Pair centres must lie within two reference body heights horizontally and half a body height vertically. These choices express component scale, local adjacency and conservative uncertainty; the visual falsification below is evidence for them on the supplied pages, not a held-out calibration claim.

## Predict, test, inspect cycles

The intermediate images and JSON remain under `out/round6/A_faintness/`; failed versions are not final corrections.

| Cycle | Prediction and inspected result | Consequence |
|---|---|---|
| Native v1 | A local maximum would estimate paper under weak ink. Texture joined through letters on the pale-front page; only seven body reference components survived. | Rejected that rendering. |
| Native v2 | Median paper would stop the texture bridges. Paper improved, but the low noise threshold still joined whole words. Ignoring oversized components falsely endangered real table entries. | All observed ink can now preserve a segment; body filters only define reference/counting support. |
| Native v3 | Local Otsu silhouettes plus native stroke cores would separate attenuation from narrow strokes. Inspected `8686…p26`, `8314…p42`, `0ce9…p1`, `ef481…p150`, pale `1be6…p215` and seal controls. | Obtained a usable component rendering. Blurred bottom numbers on `8314…p42` became explicit faint bodies. |
| Native v4, all 208 | Polygon-edge fragments would explain ghost boxes protected by a neighbouring line. The census also exposed solid-black/local-paper failure and a zero-MAD black print mode. | Mark actual polygon clipping; fix the paper estimate and the normal boundary. |
| v5–v7 | Original stroke peaks preserve thin punctuation; optical-density midpoint prevents the saturated print mode from calling slightly grey front letters faint. All-page native and reduced renderings generated. | Kept the native measurements. Reduced resolution remains a separate failed route. |
| Fast v7 → v8 | Review all 154 provisional removal crops, including the nine parked-page proposals. Found a real short `οι` on new `an-466cffad2cba-p000242` and a handwritten note on `an-778126cc8c2b-p000017` protected by a short normal stroke. | Whole unclipped half-height bodies preserve the segment. Both controls are retained; two ambiguous right-margin ghosts and a dark dash are conservatively retained too. |
| Fast v9 | Exact negative bounds can avoid calibration without changing decisions. Batched strip sampling should reproduce scalar sampling. | All 15,271 strip records match after fixing floating endpoint rounding. All 208 fast decisions match v8 and the final native classification. |

All final native page overviews were inspected, as were all provisional removal crops and full pages for ambiguous front/back text. This is visual feature review, not exhaustive transcription of every glyph. The final comparison reclassifies unchanged v7 native measurements with the final preservation predicate; the JSON explicitly records that derivation. Its extraction times are historical diagnostic measurements, not fresh final-stack timing.

## Both fast routes against the rendering

**Route 1, reduced explicit rendering:** sampling at 24 pixels per height made components cheaper but changed small strokes and the reference population. Across 15,271 segments it proposes 136 removals against 149 native proposals: 18 native-only and five reduced-only decisions, on nine pages. For example, it loses the faint contrast distinction on `s2-93f807…p1` and `s2-31f40…p1`, while endangered clipped/short ink appears on `8686…p5/p26`, `d83e…p115`, `db97…p103` and `ef481…p150`. It is **not installed as a removal rule**.

**Route 1, localized native rendering, installed:** keep native pixels, replace the costly native median paper noise field with a local median, and measure only nominated segments plus up to eight reference strips. The reference strips span the observed weak-to-strong distribution; each has length at most `16h` and is intersected with the actual polygon. A negative proof can avoid even those reference measurements: the minimum native intensity bounds the strongest possible calibrated normal boundary. A sufficiently large normal component that survives that bound guarantees preservation. This proof changes cost only, not acceptance.

**Route 2, longitudinal heuristic:** divide each segment into approximately `h`-wide blocks; sample 8×8 native positions across the central half-height. Compare block contrast with the own-page distribution. Two adjacent normal blocks preserve the scout hypothesis; a single-block segment needs its one normal block. It nominates 297 segments versus the native rendering's 149. It would over-remove if used by itself, so it only requests route 1. Its per-block rendering and every false nomination remain visible.

An already-paid R5 ownership census is optionally reused to skip a page with no weaker box cores. This is explicitly a **lossy page nomination**, not a certificate that every final polygon is normal. It skipped 49 pages in the executed stack without losing an unparked positive; the offline diagnostic counted 50, including the parked orientation control. The complete installed stack agrees with the slow final decision on every unparked segment. Nine slow/native positives are on the sideways page and remain parked. Per-page, per-segment records, including negative cases, are in `comparison/*.segments.json`; there are no native/localized decision differences in this cohort. Agreement with a renderer is not by itself correctness, hence the crop inspection and retained counterexamples.

## What actually changes

| Page | Task-A change and what remains |
|---|---|
| `s2-831443dc5e6f1ccfbaf5-p00042` | Removes 36 blurred bottom numeric boxes. Normal front table cells and punctuation survive. No mirrored-glyph vote is needed. |
| `s2-831443dc5e6f1ccfbaf5-p00039` | Removes the faint bottom band. |
| `s2-86865c33eef5932c013b-p00026` | Removes three R5 segments, indices 17, 29, 35. Other ghost segments containing normal-strength fragments remain; this owner comment is only partly addressed. |
| `s2-0ce9d1025b3f23c7119e-p00001` | Removes six further faint bands, R5 indices 0–4 and 38. Index 28 retains a dark short component; removal is incomplete. |
| `an-ef481610a820-p000150/151` | Removes four and eight faint segments respectively. Full-page inspection identifies the right-margin p151 initials as mirrored show-through; front left initials survive. Some ambiguous ghosts remain. |
| `an-1be60011c435-p000215` | All 54 R5 segments retained, including pale front print. The uncertain central watermark is not solved. |
| `an-466cffad2cba-p000242` | Removes the watermark segment, retains the real short word `οι`. This is the caught v7 false-positive control. |
| `an-e74539ae215c-p000338` | Removes another faint seal word, preserves dark front print crossing the stamp. No circle-interior mask is created. |
| `an-00f143ecce59-p000192`, `an-c153f2c605b3-p000040`, `an-d6fd2cf2f618-p000047` | Removes two, one and one watermark segments. The missing-row part of the first comment is unchanged. |
| `an-ffccc97c07de-p000152`, `s2-d12a9a4feb23254f4080-p00012` | Removes one faint stain/smudge each incidentally. This is not a general stain or image classifier. |
| New `an-7792a3301892-p000154` | Removes 25 faint ghost fragments. The actual dark decorative boundary remains; its owner comment is not fixed. |
| New `s2-44b5cf9e0d680b361091-p00005` | No faintness removal: the owner's indicated faint defect remains. |

All other changes have exact R5 polygons and zero-based item indices in the per-page delta files. Review labels use a separate one-based reading order, with an explicit `*.order.json` mapping; R4 comment numbers are not silently reinterpreted. Owner row marks use **zero-based R5 measurement indices**, independently verified against `rows_r5.json`. All 318 supplied measurement records, including the 256 marked and 62 null/control records, retain their polygons unchanged. No task-B row count is claimed fixed.

### Existing three removal rules

All three remain independent and unchanged: **keep reflected back-print**, **keep seal-rim**, **keep repeated ornaments**. Relative faintness covers additional examples of their purpose but does not replace their witnesses: a dark mirrored row or dark decorative motif need not be relatively faint. Conversely, blurred faint numbers and isolated watermark words need neither a legible mirror witness nor an enclosing rim. Runtime applies faintness to the final OCR segments after cuts, recovery and shaping. Its exact rejected polygons are appended to the permanent removal ledger with reason `relative faintness`; downstream tasks must preserve those footprints. It never excludes a stamp disk, a bbox annulus, or a whole page region.

## Timing and validation

All values below are **milliseconds**, first / second fresh repeat. Raw per-page receipts and stage timings are linked from the gallery.

| Population / measured cost | Median | p95 | Maximum |
|---|---:|---:|---:|
| 40 agreement pages / added faintness | 0.955 / 0.961 | 26.636 / 25.468 | 29.896 / 28.090 |
| 40 agreement pages / complete correction stack | 22.775 / 20.992 | 57.706 / 60.540 | 73.917 / 79.308 |
| 101 discrepancy pages / added faintness | 1.452 / 1.467 | 36.865 / 35.929 | 69.221 / 68.345 |
| 101 discrepancy pages / complete correction stack | 115.152 / 112.174 | 594.867 / 576.197 | 1011.482 / 927.163 |
| All 208 pages / added faintness | 1.062 / 1.074 | 37.645 / 36.356 | 75.927 / 75.888 |
| All 208 pages / complete correction stack | 78.646 / 75.215 | 468.059 / 465.314 | 1019.722 / 1017.188 |

The new stage’s clean tail is `s2-922e617957fca8dfafd0-p00001`: a dark blob and a short heading nominate native checking, then eight reference strips establish normal print. Its 29.896 / 28.090 ms is not negligible. The clean scout alone is 0.802 / 0.763 ms median, 1.075 / 1.085 ms p95 and 1.239 / 1.950 ms maximum. Most clean pages avoid native calibration, but the strict clean-page target remains unmet.

The worst new-stage page is new `s2-44b5…p5`, 75.927 / 75.888 ms, with no accepted removal. Complete corrections exceed one second on `s2-49598…p1` in both repeats (1019.722 / 1017.188 ms), and `s2-6f045…p1` in the first (1011.482 / 927.163 ms). Thus **three of 416 measured correction calls exceed the target**. The new feature itself remains below 76 ms; that does not make the combined stack subsecond. File-to-segments all-page median is 227.368 / 227.331 ms and maximum 1243.891 / 1214.718 ms.

The two measured passes are fresh public `Stack()(image_path)` runs in forward and reverse cohort order. One detector warm-up precedes each run; model initialization and review-image export are outside latency. File reading, inference, all R5 dependencies, height estimation, the new scout, native evidence and output assembly are included in the recorded file-to-segments path. Final decisions match exactly between passes and the reviewed pilot. Do not substitute the earlier pilot latency: it overlapped slow diagnostic work. OpenCV's existing GCD build does not enforce the requested two-worker setting; these are observed Mac timings, not bounded-worker or unseen-page guarantees.

The prototype suite passes **190/190 tests**, including 11 new faintness tests: all-faint removal, a dark speck, mixed normal/faint words, thin dark print, grey front print, uniformly pale own-page print, width/faintness separation, empty inputs, evidence-size binding, illumination scaling and actual-polygon exclusion of a neighbouring dark row. The stack composition test checks that the new stage receives the final geometry and existing ownership evidence. The [export audit](../../../.astra/fast_lines/out/round6/A_faintness/final/validation.json) passes 82,749 checks across all 208 pages and 416 fresh runs: exact survivor polygons and order, unchanged old operator counts, input/source hashes, detector-format bounds, exclusion ancestry, per-segment route agreement, numbering, owner records and links. These are not extra pytest tests. The [visual-review receipt](../../../.astra/fast_lines/out/round6/A_faintness/final/visual-review.json) records the 35 native and 35 final overview sheets and all 154 provisional raw crops inspected.

## Interface and handoff

`prototypes/fast_lines/shared/ink_faintness.py` provides `render(gray, items, height=None, route='slow'|'explicit')` for full diagnostics and `analyze(gray, items, height=None, detail=False, ownership_evidence=None)` for conditional native evidence. `prototypes/fast_lines/shared/ink_faint_scout.py::render(gray, items, height)` exposes the strip nominations. Results include reference, per-region components, `suppress_indices`, scout seconds and total seconds. Supplied ownership must describe the same pixels; image size is checked, pixel identity is the caller's responsibility. The old and final item lists may differ intentionally. No image ownership is inferred from absent evidence.

Reused R5 pieces are live imports: height/ROI/contracts, ink ownership, final shape output and the numbered review renderer. No private A/C module copy was made. The final hook is in `prototypes/fast_lines/stack/pipeline.py`. The new modules and tests are ready for the prototype stack; they are not a production pages-model replacement.

Remaining work is explicit: distinguish real normal ink from adjacent-row fragments without losing short words; resolve a fully faint genuine front row among dark print; improve sampling/reference calibration without reducing that preservation margin; and reduce conditional clean-page cost. The bright-paper approximation can be imperfect under strong shading, joined scripts do not map one component to one letter, and the optical model cannot identify watermarks by itself. The 44 held-out pages remain the appropriate later generalization test. Tasks B/C may clarify fragment ownership, but are not implemented here.


## Commit handoff

The runtime source signature for both fresh passes is `cfc1f8fbdcfd6c120a1a1076270f461fda6c6ffb49f8e4df373b1ef6769ebbd9`. On this 208-page cohort, the retained operators still remove 61 reflected back-print segments, 16 ornaments and 22 seal-rim segments; these counts include the newly supplied originals and must not be compared directly with the earlier 200-page totals.

Git staging was blocked by the filesystem sandbox at `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.git/worktrees/greek-ocr-toolkit-fl-falsepos/index.lock`. No commit or push was made. The fallback [patch](../../../.astra/commit-FA_faintness-r6.patch), [commit script](../../../.astra/commit-FA_faintness-r6.sh) and [validation receipt](../../../.astra/commit-FA_faintness-r6.validation.json) carry the nine code/document files, base identity, file hashes and required trailers. Forward application, exact resulting bytes, reverse application and shell syntax are validated separately from the experiment. Outputs stay outside git.


Integration correction (11 October): the original handoff described the staging failure at that time. The coordinator subsequently committed task A as `1625031` and merged it at `cd1e52f`; both commits are present in the merged branch. No push is claimed.
