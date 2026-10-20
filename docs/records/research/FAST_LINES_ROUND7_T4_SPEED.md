# Round 7 task 4: speed, cleanup and the r7 benchmark

**PARTIAL. The cleanup and repeated benchmark are complete; the speed target is not.** Default output is identical, item for item, to the Task 3 default on all 208 supplied pages. Two fresh final runs agree exactly. Corrections exceed one second on **20 pages in each pass**, reaching **2008.564 / 1998.657 ms**. Agreement-page added time is **60.570 / 63.194 ms median**, **547.714 / 537.945 ms p95**, **642.485 / 647.715 ms maximum**. These are not negligible overheads. No successful correction was deliberately dropped for speed.

Base: `1b097e9` on `astra/ff-merged`. Runtime/evidence source signature: `56680e258fe3a444087a21706fa9d1de94358315cc19fc6d3cae1d3919b18220`. Source snapshots and individual file hashes are in [source-r1.json](../../../.astra/fast_lines/out/stack/r7/source-r1.json) and `source-r2.json`. Commit/handoff status is recorded at the end. Rust data contracts, bindings and crate selection are **deferred by the owner**, following the final “Change to the sequence” in `.astra/F_round7.md`.

## The reviewable result

Detector JSON, two timing receipts per page, original Paddle evidence, numbered final/Paddle images and reading order are in **`.astra/fast_lines/out/stack/r7/`**.

- [208-page gallery](../../../.astra/fast_lines/out/stack/r7/index.html), [changed-page gallery](../../../.astra/fast_lines/out/stack/r7/changed.html): **zero changes against the current default**.
- [COMMENTS.md](../../../.astra/fast_lines/out/stack/r7/COMMENTS.md): all **104** entries, including every owner quote, historical numbered image, current output and explicit review basis.
- [ROWS.md](../../../.astra/fast_lines/out/stack/r7/ROWS.md): all **256** original keyed polygons, with native current/r7 context and historical R6 marked crops. The original 97 one / 159 two judgments are unchanged.
- [TIMING.md](../../../.astra/fast_lines/out/stack/r7/TIMING.md), [raw CSV](../../../.astra/fast_lines/out/stack/r7/timings.csv): every slow page, every stage, agreement/discrepancy groups, file-to-lines totals and paired historical R6/R5/current-default deltas.
- [Native retention ledger](../../../.astra/fast_lines/out/stack/r7/acceptance/pages.json), [receipt](../../../.astra/fast_lines/out/stack/r7/acceptance/receipt.json), [visual review scope](../../../.astra/fast_lines/out/stack/r7/acceptance/visual-review.json), [validation](../../../.astra/fast_lines/out/stack/r7/validation.json).

The primary evidence harness is `prototypes/fast_lines/evidence/`. Artifact-only timing and ledger finalization scripts are preserved in `r7/evidence-tools/`; they do not enter `Stack` or its measured path. No runtime page names, saved detector outputs, owner numbers or held-out pages are used. Production `greekocr/pages/` and its tests were not changed. No background jobs or push were used.

## What changed in the default

`Stack()('page.png')` retains Paddle v6 small and the accepted composition: Q8 → ink exclusions → edge scout and printed boundaries → early shared field selection → remaining local geometry/joins → type recovery → envelopes → faintness → conditional field reconciliation → native row splits → final duplicate ownership → changed-footprint faintness → native frame removals. Field-owned rows bypass replaced local paths. The second selection reuses the same proposals; it does not rerun Paddle. The default retains M15–M18 and all Task 3 removals.

The changes reduce repeated work without changing observed decisions:

1. `geometry_memo.py` caches box, minor-height and axis calculations within one composition. It holds polygon identities strongly, uses new identities after edits and clears the context on exit, including exceptions. No cache crosses pages. Standalone primitive calls remain uncached; mutable return arrays/lists are copied.
2. Field selection shares the native component labels/areas and per-polygon component counts between early and late reconciliation. Image identity and height bind the cache. Current exclusions and fixed-point retention are still evaluated against current segments.
3. The page mesh batches independent columns in its two refinement iterations. Outward displacement propagation, interpolation, lag grid and reduction order remain intact. The unused diagnostic edge walk and unused final unbent matrix are removed; native component certification was the decision gate.
4. Field-band separation nominates overlapping pairs with array operations before the same ordered pair edits. Component eligibility and label counts are vectorized. Shapely constructors receive the same ordered coordinates directly instead of rebuilding Python vertex lists.
5. `type_dot_runs.py` is the shared periodic-chain search used by leader and table-extent observations. It preserves seed order, first successor and missing-dot behavior. Residual recovery caches fixed original geometry once, while added-line state remains current. Large-initial eligibility is unchanged.
6. Native row fitting computes the Gaussian columns actually sampled by the fitter, with the same finite kernel, native coordinates and reflect border. This changes floating-point accumulation order, not the observation grid. Oracle tests bound numerical differences; the complete 208-page replay and both final passes are exact. This is an observed parity result, not a proof for unseen pages.
7. Final duplicate ownership precomputes spatial candidates and avoids photometry when an overlap contains no pixel dark enough to satisfy its existing inclusive-ink rule. It retains the existing native ink comparison and unique-ink clipping.
8. Blob detection now uses the native nomination followed by the native witness; the redundant reduced nomination is gone. Frame detection keeps only its accepted native route. All 59 Task 3 whole deletions survive exactly.

No model, first detector inference, DB postprocess, letter-height definition, ownership threshold, photometric threshold or accepted geometry route was weakened for timing. `Stack(bend=True)` remains opt-in and is not invoked by the default. Its physical-region primitive was moved, not copied, into `geometry_regions.py`.

## Profiling and rejected speed changes

Profiling preceded optimization. Diagnostic profiles and trial receipts are under `.astra/fast_lines/out/round7/T4_speed/`; instrumented cProfile times are not the final benchmark numbers. The largest costs remain field mesh/proposal generation, regional inference, native ownership and recovery. Saved per-stage totals below compare final r7 with historical Task 3 receipts on this Mac; they are **not controlled simultaneous ablations**.

| Scope, total seconds over 208 pages | T3 pass 1 / 2 | r7 pass 1 / 2 |
|---|---:|---:|
| Complete corrections | 78.179 / 79.005 | 72.815 / 73.321 |
| Field proposal | 27.166 / 27.497 | 26.596 / 26.710 |
| Early field ownership | 4.051 / 4.126 | 4.226 / 4.292 |
| Remaining local geometry | 3.653 / 3.618 | 3.174 / 3.154 |
| Type recovery | 12.255 / 12.422 | 11.347 / 11.364 |
| Native row splitting | 4.360 / 4.438 | 3.717 / 3.721 |
| Final duplicate ownership | 8.414 / 8.401 | 7.939 / 7.967 |
| Initial ink | 6.027 / 6.169 | 5.667 / 5.839 |
| Final frame removal | 0.914 / 0.932 | 0.910 / 0.909 |

Early field ownership is slightly slower in these saved comparisons; caching does not justify claiming every stage became faster. Complete correction totals decrease by 5.364 / 5.684 seconds over the cohort. Saved Task 3 had 22 / 24 slow pages, versus 20 / 20 now.

The requested field dispatch/column optimization is **not delivered**:

- A reduced native field scout skipped 46 of the 73 nominated pages but missed **14 pages with accepted field bands**, including 8686 p7/p26/p29. It was rejected (`T4_speed/field-scout/`).
- A conservative native end test requiring all nominated rows to be near-affine skipped **zero of 73** and added roughly 20–70 ms of diagnostic work. It was rejected (`affine-scout/`).
- Restricting reruns to observed curved columns changed **13/208** pages. All 13 comparison galleries and loss contexts were rendered. Native inspection found a real clipped **rho descender on `an-c8b96a901917-p000036`**, 207 missing grey<200 pixels in loss context 42. This trial was withdrawn in full; it was not accepted based on mostly harmless separator/background differences. Other inspected contexts include c8 p36 context 90, d1ed p1 context 191, dfcc p1 context 149, e259 p198 context 89, d12 p8 context 34 and 9ea1 p218 context 16. Inspection did not cover every generated trial crop. Evidence: `columns-1/review/`.
- A guarded column variant reproduced **208/208** outputs by restoring the original domain where native body ink might be clipped, but erased the speed benefit and added work (`guarded-columns/`). It was not promoted.
- Simplifying field rectangles to four vertices changed a downstream 4959 p1 polygon. The unqualified ~70 ms probe was reverted. A DFT filter trial preserved nine probed outputs but was slower, so it too was rejected.

The physical reason this remains difficult is that the nominally flat interior and the region's curled endpoints do not have the same support. A column crop also changes the second detector's border and resize context. The observed old field's successful descendants cannot be assumed to survive merely because the interior looks affine. There is no new page-specific exception or naive flat-page skip in the default.

## Complete timing against the target

Each final pass is a fresh Python process/session; pass 2 reverses all 208 pages. The image file is decoded inside each timed call. First inference and DB postprocess are included in detector time; all subsequent dependencies, allocation and assembly are included in corrections. Rendering and serialization are excluded. Startup is reported separately: **17.117 / 16.748 ms**. ONNX remains single-threaded; OpenCV reports **10** GCD workers despite requesting a positive cap of two. These are not two-worker measurements.

All triplets below are **median / p95 / maximum milliseconds**.

| Cohort | Pass 1 | Pass 2 |
|---|---:|---:|
| All 208, corrections | 187.222 / 1296.210 / 2008.564 | 193.793 / 1301.813 / 1998.657 |
| Agreement 40, added correction time | 60.570 / 547.714 / 642.485 | 63.194 / 537.945 / 647.715 |
| All 155 original non-agreement pages | 215.400 / 1434.912 / 2008.564 | 220.417 / 1422.617 / 1998.657 |
| Additional supplied 13 | 570.328 / 1373.742 / 1747.437 | 560.678 / 1365.158 / 1712.927 |
| All 208, image file to final lines | 329.194 / 1500.619 / 2202.131 | 338.448 / 1510.478 / 2191.604 |

The maximum is 4959 p1 in both passes. Its first-pass field proposal is 862.748 ms, type recovery 557.528 ms and early field ownership 166.910 ms; total corrections are 2008.564 ms. On p5 the corresponding largest costs are field 554.103 ms, type 514.287 ms and row splitting 326.709 ms. Every one of the 20 slow pages is listed by full name in `TIMING.md`, not hidden behind a percentile.

The field still fires on **73/208**, with **35 empty outcomes**. All field scopes cost **32.202 / 32.433 seconds**; empty outcomes alone cost **6.831 / 6.941 seconds**, median **166.396 / 168.574 ms**, maximum **420.576 / 427.964 ms**. Thus the central requested dispatch improvement remains open. The agreement tail is e259 p198, where field proposal alone costs 465.415 / 467.621 ms. The old an-778 p11 motif-enumeration tail is not the present cause: ink is 16.061 / 17.579 ms there, whole correction 53.067 / 47.411 ms.

Historical R6 corrections reached 2393.061 / 2379.603 ms, and agreement medians were 62.336 / 61.808 ms. Paired r7-minus-R6 agreement median deltas are -2.827 / -2.938 ms; paired r7-minus-R5 are +39.562 / +39.678 ms. R5 had only 200 supplied pages, so its full paired comparison uses those common pages. These saved timing differences do not establish a fresh causal speedup by themselves. The two fresh r7 measurements independently establish failure of the target.

## Retention, comments and visual findings

P0 compares native grey<200 inside the **old** final crop union, excluding only the old baseline's removal polygons. New exclusions cannot excuse a loss automatically. Against the current Task 3 default: **208/208 exact items, zero new missing pixels, zero missing prior exclusions, zero new excluded-ink intrusions, exact printed-column changes**. This also covers partial/connected glyphs instead of checking component centers only.

Against R6, **327,500 found-ink pixels** leave the crop union on seven pages. These are precisely Task 3's 59 whole non-text deletions. All 14 inherited native loss sheets were re-inspected in task 4: flower borders on 7792 p59/p104/p107/p138/p154 (5/10/16/2/24 segments), the 922e p1 solid blob, and the 44b5 p5 mirrored bottom head. The loss ledger records their individual prior indices and visual verdicts. These observed non-text removals are not new geometry losses. Some nearby retained boxes still include frame decoration: the frame comments remain **partly**, not fixed. The blob and the specific mirrored head are **fixed**.

Native context for protected c0 p10 #118, d83 p99 #108 and 3229 p6 #26 was inspected; the accepted recovered text is unchanged. The separate newly questioned line below d83 #108 remains unboxed. Earlier R5 omissions inherited through R6 on 3229 p4 and 4959 p1 are still open; exact parity with the current default cannot repair them.

All 256 mark contexts were rendered and linked to historical R6 crops. Their detailed prior native dispositions are explicitly **inherited**, not represented as a new visual review of every unchanged row. They remain: **97 retained, 25 fixed, 45 partly, 88 not fixed, one outside this round**. No owner-one or fixed portion changes in this speed patch. Full-page equality also preserves every unresolved boundary, endpoint, missing-line and multirow case. Owner O25's `6,7,` remains unresolved intent; orientation O26/R4-01 stays outside this round.

The five faint-front controls were rerendered and inspected. Grey rubric, light grey, light italic and blurred small front footnote are still wrongly removed; red-rubric luminance survives. These are explicit synthetic controls, **not** a passing real-page faint-front control. The strict expected failure stays. Other inherited failures include short faint pieces on ef481 p150/p151, faint endpoints on 93f8 p1 and 8686 p26, c99 p25 upper ivy, severe curled endpoints, broad/multirow crops and the 4959 p5 sliver. Each owner-specific case is retained in `COMMENTS.md`/`ROWS.md`; the inherited R6 recovery and boundary-pixel limitations are not relabeled as fixed.

## Cleanup and tests

Deleted: `row_model=True`, `compose_rows`, residual-parent branches, `geometry_row_context`, `geometry_row_model`, `geometry_row_surface`, `geometry_page_rows`; their unused obstacle/median helpers and tests; the unconsumed old field-correction/child-only ownership alternative; geometry `round7*` and ink `round7*` studies/duplicate runners, including the page-keyed ink study; old curvature study entry points that depended on the removed alternative; reduced frame/blob decision routes; unused normal-ink growth helpers and dead page-ink adapter arguments. Sources and SHA-256s are recorded in [evidence/retired.json](../../../prototypes/fast_lines/evidence/retired.json), with local archives and original commit `1b097e9` for reproducibility. Historical reports remain historical.

Kept because consumed: `NormalInk` and the calibration/following machinery used by opt-in bend, `smooth_corridor` and `finite_rules`. Opt-in bend is isolated. The current generic benchmark/review/acceptance tools live under `evidence/`; historical round5/6 render utilities still supply offline rendering primitives and are never imported by `Stack`. This is not a claim that every historical research file was deleted.

**252 tests passed; one inherited strict xfail (253 collected).** Retired experiment-only tests were removed with their mechanisms, not used to inflate success. New tests exercise cache scope/exception cleanup, changed polygon identity, dot-chain gaps, Gaussian oracle parity and runtime import isolation. The old child-only ownership test now targets the active global ownership mechanism and checks preservation of the unique lower row and zero lost native ink, rather than requiring a known duplicate upper child to survive. Final artifact validation passed **51,122 checks**. The separate [cleanup receipt](../../../.astra/fast_lines/out/stack/r7/cleanup.json) verifies 36 reused module hashes, 30 archived sources, no dangling deleted-module imports, no evidence/bend imports in the default, and 1,048 gallery links. These checks do not prove OCR correctness or the speed target.

## Checklist disposition

The source for each completed implementation is this task-4 change set on `1b097e9`, identified by the frozen source signature above and the commit/fallback receipt below. No deferred Rust work is counted as done.

| Item | Status | Evidence / remaining failure |
|---|---|---|
| **4-01** detector/decode shell | **closed for speed/cleanup scope**; Rust binding contract **deferred by owner** | First Paddle outputs exact on 208, two fresh process receipts, unchanged model/postprocess, actual 10-worker OpenCV setting recorded; `source-r*.json`, per-page receipts. |
| **4-02** scale/image/contact consolidation | **not closed**; Rust representation **deferred by owner** | Call-local geometry and field-label reuse are implemented and exact. Incompatible photometry/component censuses remain separate; a single native census has not been proved equivalent for every consumer. |
| **4-03** boundaries/tables/leaders/exclusions | **not closed** | Shared dot-chain search and exact column/exclusion replay pass. There is still no single boundary service for all consumers, and inherited finite-rule/header failures such as c8 p155 remain. |
| **4-04** cost follows need | **not closed** | Field still fires 73 times with 35 empty results. Column skip loses the c8 p36 rho; conservative fallback removes savings. Native scout trials failed as documented. |
| **4-05** recovery consolidation | **not closed** | Cached residual context and shared chains preserve the three protected recoveries and all final items. Type remains up to 591.313 / 578.544 ms; missed bottom/short/wide-gap rows remain (ffccc p354, ef481 p181, 00f143 p258, 1ba3 p35). Large-initial rule was not widened. |
| **4-06** local geometry/joining/smoothing | **not closed** | Safe repeated work removed and native sparse convolution qualified on all 208. The field and still-needed residual local paths both remain on unresolved domains. Smooth complete crops/severe curls are unresolved; redesign is reserved for the owner's next review. |
| **4-07** offline evidence / dead experiments | **closed for requested cleanup scope** | Failed routes/switches and named studies removed, current harness consolidated, `Stack` import isolation test, retired-source manifest, 104 comments/256 marks and native retention ledger. Historical renderer utilities remain offline; no broader redesign claimed. |
| **4-08** r7 benchmark / readiness | **not closed**; Rust contracts/crate list **deferred by owner** | Full repeated benchmark, renderings, validation and reports delivered; 20/20 pages still over 1s, agreement overhead still large, inherited owner failures remain. |

P0–P5 pass **preservation of the current accepted output**, with the explicit R6-to-Task3 non-text removal verdicts and existing correctness failures above. They are not evidence that all owner obligations are solved. P7 fails. The cleanup primitives can be reused, but the complete stack remains a research prototype, not ready for production promotion.

## Commit / handoff

No commit was made in this task. Normal `git add` failed with `Unable to create .../.git/worktrees/greek-ocr-toolkit-ff-merged/index.lock: Operation not permitted`. No alternate index or metadata bypass was attempted. The handoff is `.astra/commit-FT4-r7.patch`, `.astra/commit-FT4-r7.files.json`, `.astra/commit-FT4-r7.validation.json` and executable `.astra/commit-FT4-r7.sh`. The script checks the exact base, branch, empty staged index and every file hash before staging only the validated paths and committing with the requested trailers. Its `--check` mode performs no staging or commit. The patch is validated by reverse-apply checks and reconstruction against the original base bytes. No push was performed.
