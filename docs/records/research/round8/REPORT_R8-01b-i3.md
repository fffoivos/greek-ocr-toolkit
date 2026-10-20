# R8-01b iteration 3 — explicit reuse, unresolved body authority

The candidate removes repeated array work and preserves all 15,093 checked output items on the 208 development pages. It does **not** establish one body-height authority or remove an independent physical decision. G1b and this iteration's three-part deliverable remain **PARTIAL**. Only the mechanical reuse changes are proposed for carry-forward.

Runtime starts at independently accepted `051cc7ebcdbb23d6ef822a07484de1fc313ee011`; checkout `ba0bc44` adds planner documentation only. Iteration2's commit status now has an explicit post-check addendum and `POST_CHECK_STATUS.json`; its original receipts/images remain unchanged. The imported planner-root `commit-FP8d-r8.sh` is removed. No rejected model, held-out material, production changes, background job, subagent or push was used.

Evidence: [iteration directory](../../../../.astra/fast_lines/out/round8/R8-01b-i3/), [gallery](../../../../.astra/fast_lines/out/round8/R8-01b-i3/index.html), [timing](../../../../.astra/fast_lines/out/round8/R8-01b-i3/TIMING.md), [body review](../../../../.astra/fast_lines/out/round8/R8-01b-i3/BODY_REVIEW.md), [consolidation delta](../../../../.astra/fast_lines/out/round8/R8-01b-i3/CONSOLIDATION_DELTA.json). Final detector JSON and per-page clocks are in `runtime/` there.

## Runtime work actually removed

| Mechanism | Producer → consumer | Repeated work removed in208 pages |
|---|---|---:|
| M25 dense slot | `type_extended.recover` → `type_context.recover` → `type_recovery.run` | 8 remaps, closings and CC8 builds;671,663 remapped pixels,7 pages |
| M06/M28/M30 tone samples | `Stack.compose` → `sample_boxes` → B and type/residual ownership | 2,841 sampled histograms;17,389,415 sampled pixels |
| M35 exact whole-footprint calibration | candidate components → calibration in the same `ink_faintness.analyze` call | 95 closings and CC8 builds;3,005,601 pixels, plus component photometry |
| M06 glyph tone percentiles | one `percentiles8(raw,[90,10])` → paper/core values | 1,462 separate percentile scans become731 histograms;96,724,142 scanned elements become48,362,071 |

Dense results include negative witnesses. The confirmation stage still checks exclusions, motifs, tables and current polygon ownership. A changed image object or any of the six measured slot geometry/scale values triggers measurement. Only8 dense witnesses were actually duplicated, including3 on the21 slow pages; this was not the main cost.

Tone observations contain the same immutable native image, clipped integer sampling rectangles and owned two-value arrays. Exact rectangles can survive a changed item census; calibration, anchors, atlas and classification are always rebuilt for that census. Changed rectangles or image objects are sampled anew. Returned arrays are independent. This is an explicit call-local handoff, with no global key/hash cache, memo decorator or ContextVar. The default does not mutate its gray raster. Matching, allocation and copies are included in the timing.

Faintness reuses a component record only when the central calibration strip is the exact candidate polygon. Separate strips, changed polygons and the final-footprint recheck retain fresh work. Calibration receives copied records before classification mutates the candidate records. No faintness decision or mask recipe changes. Glyph percentile sharing is one histogram of the exact same raw uint8 population, not one page histogram substituted for several local populations.

Atlases, changed-footprint calibration, geometry preparation and the other paper recipes remain. This is not a claim that nine ink or ownership definitions have become one.

## Comparable operation counts

Both literal051cc7e and the frozen candidate were run through the same offline cv2/NumPy instrumentation over208 pages, with a21-slow-page and37-control union breakdown. Each event records callers, content/transform hashes, shape, dtype and kernel; dense slots additionally record coordinates. There are no counters in the timed default. The first baseline scope without NumPy percentile calls is retained as `baseline-operations-v0` but is not used in the comparison.

| Operator | Baseline | Candidate | Difference |
|---|---:|---:|---:|
| Morphology calls |4,414|4,311|−103 closings|
| CC8 builds |12,751|12,648|−103|
| Remaps |14,296|14,288|−8|
| Tone histogram calls |34,902|32,697|−2,205 net|
| NumPy percentile calls |31,471|29,363|−2,108|
| NumPy quantile calls |1,360|1,344|−16|
| Resize / box filter |26,500 /4,936|26,500 /4,936|0|

Closing/CC inputs shrink by3,677,264 pixels each. Their nominal kernel-support product shrinks by25,999,300,920; this is not an instruction-count estimate for optimized OpenCV. Remap savings are671,663 **output** pixels; the76 million fewer input-array elements in traces are not76 million processed pixels. Histograms now also replace glyph percentile scans, so histogram input elements increase27,967,055 while percentile input elements decrease96,893,420. Combined scanned sample elements decrease68,926,365. Fewer calls are backed by fewer scanned pixels, not merely moved wrappers. On the21 slow pages,13 closings/CC builds and3 remaps disappear. Full caller/population records are in `operation-counts.json`, `measurement-operation-counts.json` and `dense-operation-traces.json`.

No runtime body preparation is added. The rejected offline experiment's field-preparation clocks are separate and exclude crop fitting/rendering; they are not a speed result.

## Body measurement attempt and first wrong stages

`evidence/r8_i3_body.py` is an offline explicit tool, imported by no runtime module. It prepares a native field with the closing operator's complete border halo, follows selected components beyond the residual request edge, and records local native IDs, transform, operator ROIs, incomplete edge IDs and nomination-to-measurement membership. It does not make those pixels available for recovery. A request rectangle is an engineering region, not a leaf or cell boundary. The tool does not certify finite domains.

The crop/contact fitter and `font.evidence` remain conditional on row assignment, starting baseline and starting scale. Same-component top/bottom pairing avoids taking a scalar from an extrapolated fitted guide; it cannot establish glyph class. Three preserved diagnostic states distinguish two implementation corrections: the initial crop-as-page prior hid capital handling; the separate saved pixel prior corrects that misuse; exact mapped-ID attribution then excludes neighboring components the crop fitter had opportunistically selected. Saved priors are offline inputs only, never runtime page lookups. No compatible-font donor is established.

64 probes on17 pages were freshly inspected; the six quiet/non-residual controls reuse source-matched iteration2 explicit evidence rather than inventing a residual chain. The final tool emits57 conditional candidates and7 unknowns. **Zero** are accepted runtime measurements or borrows. No output crop changes.

- **4959 p1 field3 chain0:** full small-letter support above y2552 is recovered for measurement. Visible ο/ν-like pairs give24 px rather than the clipped14.5. Saved22.15 is a comparison, not a fitted constant. This is useful local evidence, not general validation of the provider. Heading meanline becomes unknown after supplying the distinct pixel prior.
- **3229 p6 field2 chain40:** after exact chain-ID attribution, the earlier plausible26 disappears; the remaining31 px contact includes the η descender. Its small-body class is wrong. Chain7 gives22 on more complete support, but that does not establish the sagging row baseline or validate the whole page.
- **31f40 p1 field0 chain2:** the old57 px joined extent is complete, but after exact attribution the remaining33 px contact is a tall form, not a body. The earlier26.5 had borrowed non-chain support. Chain0 still measures weak fragments below a blank start; field3 chain8 becomes unknown when neighboring-row support is excluded; the “Κ.Ρώμας” probe still measures ghost support below the capitals. The first error is row/source/component attribution before the scalar estimate.
- **8314 leaders and numeric cells:**11 px dots and45 px numerals remain falsely eligible as body classes. **7a2b**6 px weak header fragments and cross-cell numeric chains are not x-height. No capital ratio or numeric extent is promoted as an observation.
- **8686 p5/p7:** some interior pairs are plausible, but severe ends still lack correct continuous row/guide attribution. **e259** rule/blob, **77d1** capitals, quiet **f9ec**, Ψ and largeE retain their prior explicit unknown/compatible-typography distinctions and fresh output controls where applicable. They were not forced into a common body scale.

All page-specific adjudications, raw/native pair crops, IDs, old/new operands and source bindings are in `BODY_REVIEW.md`, `body-review.json`, `body-fields-mapped/` and `body-source-binding.json`. Earlier diagnostic crops remain under `body-fields/` and `body-fields-page-prior/`. The `guard_candidate` values are offline counterfactuals only, not a runtime consumer; they change none of the64 saved span eligibility results.

### Why no M30 or second-policy replacement is carried

M30 `type_residual.render` still computes the contact-chain component extent for `ptp(x)*sx < 4*local_h`. In recovery, the free/support span uses the row's height; the regional detector sizing and safety checks use the eligible-height pool. The separate multirow veto is `type_residual_recovery.py`'s `minAreaRect(...) > 3.5*local_h`. A better scalar alone would not make that a row-count model. No consumer is claimed migrated to physical body height.

The selected second consolidation target was **M35** `ink_faintness.reference`: `component_extent` over the stronger half of a photometric calibration pool feeds `classify`'s edge-fragment threshold and row/short-ambiguity tests, and `normal_run`'s body length, center corridor and adjacency spacing. It assumes compatible typography from a strength-selected population. The candidate cannot replace it: it still accepts dots, numerals, tall forms and wrong-source fragments, and has no checked compatible donor for sparse calibration strips. Substitution could change exclusions using an unsupported height. The old policy remains counted.

M17 `geometry_page_field.render`'s extent also remains: its component-height admission and phase smoothing/peak spacing are not interchangeable with baseline-to-meanline height. The alternative .06/.08 DN masks remain uncalibrated; iteration2 native evidence contains both front edges and show-through and a93f8 background trace. Equalizing constants would remove a spelling while concealing a physical ambiguity. That branch was not promoted or newly claimed tested here.

The next repair is explicit complete-component assignment to a local row and class, with independently checked starting guides and finite domains, before a scalar can replace M30/M35. No added confidence ratio, page exception or fallback relabeling is proposed. 02 inherits the M35/local-source and paper/noise calibration debt;03 inherits row/cell/leaf and crop attribution. This is an unresolved deliverable, not claimed completion by offline plotting.

## Preservation and cost

Fresh candidate208 uninstrumented pass and both source-bound instrumented passes reproduce all15,093 checked items. Both reversed paired timing repeats also have no item differences. Eleven fresh raw/current native control crops were inspected: Ψ, largeE, weak τῆς, narrow32, c0#118, d83#108 and the prior ending/boundary controls survive. Μαυρομιχάλης on3229p4, the4959 central recovery and the next d83 apparatus row remain unresolved exactly as before. The known fully faint genuine-front test remains a strict expected failure.

All104 owner comments and256 marks retain exact quotes, page/polygon/historical-number identities and previous dispositions in `COMMENTS`/`ROWS` JSON/Markdown. Current equal-output status is appended, not substituted for their words. These inherited records are not claimed freshly re-reviewed wholesale. C01–C05 remain coordinator observations. No changed native output glyph/crop needs adjudication; all changed experimental support is separately reviewed.

Full candidate correction median/p95/max: **199.595 /1,319.137 /2,126.584ms**. Agreement40: **67.549 /542.169 /665.737ms**. There are **21 pages over1s**, all listed in `TIMING.md`. File-to-output median/p95/max: **340.361 /1,527.826 /2,321.348ms**. Per-stage receipts include all preparation and do not sum nested clocks.

37 slow/feature/quiet controls were timed baseline→candidate and then candidate→baseline in reverse page order. Paired candidate-minus-baseline medians are **−16.416 /−1.880ms**; aggregate differences **−722.563 /−189.965ms**. Individual tails change sign. This is real reduced array work without a robust wall-clock improvement claim; the charter target is still missed. Iteration2's194.9ms median is historical, not paired evidence of a regression or gain.

Software checks: **259 passed,1 known xfailed** (`python -m pytest prototypes/fast_lines -q -p no:cacheprovider`). New checks cover changed-image/ROI invalidation, independently owned tone arrays, negative dense evidence, changed geometry and current-polygon ownership. Model startup is outside per-page timing; decode/first Paddle/all correction dependencies are inside their stated clocks. The same pinned model, input hashes, CPU sequential ORT intra/inter1 and OpenCV1 thread are recorded in each receipt. Instrumentation/hash clocks are never quoted as performance.

## Accounting and iteration4 criteria

Independent definitions remain **height6 / ink9 / ownership9 / bend7**. Two arithmetic modes remain, versus three at iteration1; no new independent policy reduction is claimed. The earlier cache deletion, owned identity-resize contract and six ink-copy removals remain intact.

Runtime against051cc7e: **+59/−24 =+35 lines**. Against iteration1d5dc3e2: **+97/−654 =−557**. Againstcaafbc5: **+182/−544 =−362**. This iteration itself does not meet a net-deletion target; explicit handoff plumbing adds35 lines while removing measured repeated work. Offline evidence, tests and documentation are accounted separately in `source-line-delta.json`; no code relocation is counted as runtime simplification.

| Unchanged iteration4 criterion | Current evidence/status |
|---|---|
| Independent physical definition/policy reduction beyond arithmetic | **Not met**; counts unchanged |
| Zero-reuse cache deletion and lower redundant execution | **Met as worker evidence**; inherited deletion plus103 fewer closings/CC builds and tone/slot scan savings; cumulative runtime−557 |
| Complete checked body attribution reaching a consumer, or accepted ink alternative | **Not met**; local clipping repaired offline, tall/joined/row/source classes still fail; no runtime body consumer |
| Native preservation, source-bound208, honest stable/improved cost | **Worker checks pass preservation**; independent acceptance pending. Real work reduction; noisy wall time,21 slow pages remain |

No self-launch or permission to advance is asserted. The coordinator chooses the best checked head after independent source/visual/private evaluation. `ITERATION_HANDOFF` records the exact candidate/fallback state and dependencies.

## ROI trace and remaining repeated atlas work

A separate37-control replay traces native sampling rectangles, image identity, slot coordinates, height/threshold/limit, current ownership census, anchor indices and atlas sizes for both sources. `baseline-roi-trace/`, `candidate-roi-trace/` and `roi-trace-summary.json` supplement the kernel/content traces; their clocks are not used for timing. Tone requests fall6,761→5,127; faint component requests296→278; slot inspections202→197. Ownership analyses remain59 and glyph extraction calls174. Twelve identical glyph extractions remain in this control union; these are a concrete next reuse opportunity, not a claimed consolidation. Their atlas/classification consumers need fresh ownership metadata even if immutable glyph observations are handed through.

## Commit receipt

Real-index staging failed: `index.lock: Operation not permitted` for this worktree. No commit or push was made. `.astra/commit-F8-R8-01b-i3.sh` and its validated patch/receipt contain only the17 task files and the required trailers. The patch is applied to an isolated archive of checkout HEAD and every resulting file/deletion is checked. Exact patch/source hashes and review status are in `ITERATION_HANDOFF.json`. The accepted best head remains051cc7e until coordinator review; candidate carry-forward is a recommendation only.

## Post-check addendum — 12 October 2026

The coordinator committed the validated candidate as `17e884598463afad8e4d97fc01a60a3e691d9b7a`. The independent R8c-01b-i3 check accepted it as the best checked head, with G1b PARTIAL. The staging failure above describes the worker's original sandbox attempt; it does not describe the current repository state. No prior image, source hash or experimental receipt is replaced.
