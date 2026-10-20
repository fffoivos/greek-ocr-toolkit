# R8-01b iteration 2 — real code deletion, body attribution still partial

The candidate removes **592 runtime lines net** against checked d5dc3e2, including six live ink implementation copies and the observation-cache machinery. One fresh final 208-page pass preserves all 15,093 detector-format items. The existing suite passes 256 tests, with one known strict xfail.

**G1b remains PARTIAL.** This iteration does not deliver the required physically valid body-height replacement in a real consumer, nor reduce the independently chosen physical mask/height policies. Complete native support and class-conditioned tools clarify the clipped and tall-component cases, but fail required quiet/negative/curved controls. Their runtime trial is rejected. The safe preparation/deletion candidate is recommended for independent review; acceptance, best-head selection and the next launch remain the coordinator's decisions.

## Source and scope

Assigned worktree `greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Checked runtime baseline: `d5dc3e2ec2b0477a5dd275e0471d7de907ba784e`; checkout HEAD `9ed3999` adds only planner documentation. No reset to ff-merged, rejected physical_page import, production edit, background job, additional agent, push, PDF-text reference or held-out access occurred.

The existing R7 reviews and R8c-01b independent check supply the mechanism inventory. This is not a repeated mechanism census. [FEATURE_OWNERSHIP](FEATURE_OWNERSHIP.md) gives current function/caller lineage; [CONSOLIDATION_DELTA](../../../../.astra/fast_lines/out/round8/R8-01b-i2/CONSOLIDATION_DELTA.md) and its JSON distinguish code from physical policy counts. Iteration 1 evidence is unchanged. All new evidence is under `.astra/fast_lines/out/round8/R8-01b-i2/`; [gallery](../../../../.astra/fast_lines/out/round8/R8-01b-i2/index.html).

## What is actually deleted

`shared.observations.ink` now implements paper-relative contrast once, as `(paper-gray) > threshold*max(paper,1)`. `type_profiles.measure_line`, `type_lattice.inspect_slot`, `type_residual.render` and `ink_scout` use it; the division mode and branch are deleted. All 65,536 uint8 paper/pixel pairs agree at the inherited .18 threshold, including exact/nearest boundary contacts. These callers obtain uint8 paper from closing, so the exhaustive check covers their arithmetic domain. The native208 replay separately checks actual callers.

The ordinary resize/paper/ink/CC functions remain, but `Observations`, `image_key`, `get`, `observe`, copied-observation handling, the observation scope/decorator, ContextVar and counters are gone. Zero-reuse resize, mean-paper, arithmetic, CC8 and extent wrappers are removed. The Stack-unreached type-strip wrapper is removed too. Faint component records and page counters no longer undergo deep copies. Histograms and closing use plain functions: four alternating cache/plain replays of actual request streams showed no consistent net benefit after key/counter costs. Quiet f9ec and weak31f40 were consistently slower with this cache;4959 was mixed within fractions of a millisecond. Raw results are `cache-cost.json`.

Identity resize now follows OpenCV's simple ownership contract: return a new array even at unchanged dimensions. This fixes the writable-input alias introduced in iteration 1. It adds 479 identity copies compared with that shortcut; those costs are charged. No generic read-only-array framework replaces it. The older R7 polygon geometry memo remains: one ContextVar/decorator with object-ID keys retaining polygon references. Explicit field/label dependency dictionaries also remain. They are separate mechanisms, not unreported observation-cache remnants.

The R7 review's six live `type_ink_*` snapshots are deleted. Five modules have 17 identical function bodies; the sixth ownership function differs only by the common provider's optional validated height and extra diagnostics. Type recovery/extension and its historical runner now import `ink_ownership`, `ink_photometry`, `ink_motif_gate`, `ink_motifs`, `ink_recurrence` and `ink_repeat_field`. No replacement logic was copied elsewhere. The common ownership provider adds `weak_indices` and `image_size` to type evidence;208 comparisons confirm equal default regions, suspects and suppression decisions after excluding timing and those new diagnostic fields. Different caller censuses remain different populations.

|Feature|Iteration 1|Candidate|Meaning|
|---|---:|---:|---|
|Height|6|6|No physical population/decision replaced.|
|Ink recipes|9|9|Arithmetic modes 3→2; windows, resolutions and populations remain distinct.|
|Ownership policies|9|9|Implementation copy removed; policy populations unchanged.|
|Bend/row paths|7|7|Unchanged;03 debt.|

Runtime diff: **+38/−630 = −592** against d5dc3e2; **+123/−520 = −397** against pre-iteration 1 caafbc5. This conservative Python count includes the historical type runner's one import substitution; treating that runner as offline changes additions/deletions by one each, not the net. Offline evidence, tests and metadata are listed separately in `lines-vs-*.json`. There is no minification or relocation of deleted runtime logic into an uncounted module. The new offline explicit tool imports existing pixel/font logic.

## Physical paper/contrast comparison

The 23 pinned pilot pages were compared at native resolution for the .06/.08 DN band, with the old dense native boundary renderer run independently of scouts, including 18 quiet pages. The 92 native probes are published; eight mask montages and the two changed finite-rule traces were individually inspected. This is not a claim that all 574 dense boundary nominations are real rules.

On 31f40, the .06-minus-.08 band contains both real weak front letter edges and ghost/background print. On strong quiet f9ec/77d1, numeric 7a2b and ordinary 4959 print it is largely stroke-edge sampling. Neither band certifies front bodies. In 93f8 p1 the reduced .06 scout nominates two traces, versus none at .08. One passes the current native stroke verifier, but the raw crop shows a background vertical trace rather than a front separator; the existing clear-flank test rejects all six proposed cuts. The explicit verifier is therefore not an infallible reference either.

M04's reduced, 3h-window finite-run nomination and M14's native, 4h-window component texture observation have different sampling/feature domains. That distinction does **not** derive 15.3 versus20.4 DN. I retain both as unresolved calibration, not as validated distinct physical floors. A common cutoff is not promoted from this sample.02 needs native paper/noise calibration and complete glyph/source dispositions;03 needs finite-boundary ownership. The remaining calibration debt is explicit in `mask-review.json`; no physical recipe-count reduction is claimed.

## Complete bodies and conditional guides

The first wrong stage on 4959 p1 is `type_residual_recovery.field`: request 3 is `[0,2552,1766,3067]`, and `render` extracts components from that crop **before** ownership masking. Eight of chain0's ten boxes begin at 2552. Native ο/ν bodies extend above it. A trial separates measurement support from nomination/ownership by preparing complete native components, while retaining ROI-local nomination. Its extent changes 14.5→23px; its four tested final exports remain unchanged. It also adds whole-page preparation and leaves 3229's tall/joined extent at 40 px. It is not a justified semantic body provider, so the trial code is not carried forward; source diff and four outputs remain in `rejected-full-native-runtime.diff` and `native-trial/`. No speed claim is made from that unrepeated trial.

`evidence/r8_i2_features.py` uses existing `pixels.prepare_pixels`, crop geometry, `font.evidence` and `fit_guides`. It records the starting crop scale/source, page prior, focus and baseline, complete component IDs/bounds, conditional saved-row IDs, class contacts and borrowed guides. All 23 corrected native montages and 88 probes were inspected. Pixel preparation cost 39.275 s, outside runtime. An initial offline run incorrectly used the crop scale as the page prior; it is preserved under `body-crop-prior-rejected/`, then corrected. Saved dependency hashes still match 182/182 files, but neither that match nor feeding one's own starting scale into font.evidence provides independent validation.

Useful physical findings:

- **4959p1 field3 chain0:** full support explains the lost top of small bodies. The wider inherited probe gives 24.815 px; a focused probe gives 23.647 px; saved conditional row scale 22.146 px. These are conditional estimates with visible support, not interchangeable truth. The heading meanline 32.576 px is explicitly borrowed, not observed small-letter height.
- **3229p6 field2 chain40:** complete small-body contacts give a candidate near 23.5 px; θ/β/λ and joined forms explain the old 40 px extent. Other fragmentary chains on the same page still have wrong bands.
- **31f40p1 field0 chain2:** joined/tall 57 px extent becomes a conditional class fit 24.559 px on visible small bodies. This corrects the previous report's wrong identity, “field2 chain0.” Weak chain0 still takes support from a real row at its right; a separate focused field2 chain0 fit at 14.263 px is rejected.

Required counterexamples remain:

- 8686p5/p7 guides leave the intended row at severe ends; complete components alone do not establish that row.
- 8314 dot leaders receive a 10 px “body” fit; its numeric chain and 7a2b chains cross finite cells. Numeric-only samples remain unknown as x-height.
- 77d1/4959 capital meanlines are borrowed through the existing capital ratio, not measured compatible-font small-body bands.
- e259's rule/blob can receive a 120 px fallback with no body evidence. Large Ψ is a separate large component, not an x-height sample; large E remains a separate retained initial.
- Weak31f40, sparse initials, mixed Greek/Arabic ffccc and damaged c8 print do not establish general class/row authority. Quiet f9ec is a useful positive control, not evidence resolving those failures.

The full page-by-page findings are in `BODY_REVIEW.md`/`body-review.json`. No new density/phase model, global component-height mode, page rule, body-count gate or ratio was introduced to conceal these failures. The existing crop fitter remains an explicit candidate tool, with its inherited thresholds documented by source. This iteration **does not satisfy the requested real-consumer body-height migration**. Legacy M30/M35 and field callers still use extent under body-related names; that is carried debt, not validation from `uncertain=True`. `scale-consumer-lines.json` and FEATURE_OWNERSHIP identify every `value_px`, `local_h`, `body_height` and `xheight` use and separate array/ROI dimensions from physical assumptions.

## Preservation and owner records

The final source-bound 208 pass preserves 15,093 items exactly against checked d5dc3e2. There are no changed final native crops, glyph losses or reassignments relative to that baseline. Full native-control renderings were freshly generated and inspected for eleven retained/recovery cases: Ψ, large E, narrow 32, weak τῆς, historical c0#118 and d83#108, wide-gap ending, finite separator and the known missing rows.

The Μαυρομιχάλης row on 3229 p4 and the old central recovery on 4959 p1 remain missing as proper separate crops; d83's next apparatus row remains missing. Current parity does not erase R5/R6 recovery losses. Existing severe curls, multirow/sliver crops and faint-front failure are open. All 104 comments and 256 marks retain exact quotes, page/polygon/historical-number identities and prior/current inherited verdicts in COMMENTS/ROWS JSON and Markdown. C01–C05 remain coordinator observations. No whole historical ledger is falsely claimed freshly adjudicated.

## Cost and actual work

|Final 208 group|n|Correction median ms|p95|max|
|---|---:|---:|---:|---:|
|All|208|194.902|1363.928|2097.281|
|Agreement|40|66.789|550.887|665.946|
|Discrepancy|101|213.693|1403.473|1943.355|

File-to-final median 333.813 ms, p95 1566.502 ms, max 2290.183 ms. Twenty-one pages exceed one second. Every page/stage is in [TIMING.md](../../../../.astra/fast_lines/out/round8/R8-01b-i2/TIMING.md); nested stage timers are not summed. The target remains unmet.

Two fresh 23-page uninstrumented comparisons use literal d5dc3e2 and final candidate on identical inputs/settings, baseline→candidate then candidate→baseline. Median paired differences are −41.637 ms and +8.922 ms; p95 +5.577/+54.154 ms, maxima +11.137/+59.267 ms. The first baseline block was markedly slower on several expensive stages; the sign reverses in repeat2. This does **not** establish a useful speed gain. No hardware-load measurement was captured to attribute that variation. The roughly stable overall full-page cost, exact operator/decision preservation and explicit cache replay support the cleanup, not a latency-success claim.

The baseline receipt contains 44,512 observation-cache requests; the candidate makes zero. It removes 1,304 component deep copies and 208 page-counter deep copies. Array work does not simply decrease: closings 2618→2748 and CC8 builds2638→2639, due to removing the small amount of cache reuse; identity resizes now copy. Candidate 34,902 histogram calls include formerly separate type histograms; baseline 32,940 requests/31,250 builds counted only B, so those totals must not be directly subtracted. `computation-delta.json` states the scopes. The six implementation copies are deleted, but different physical observations are still executed. No claim is made that code deletion means fewer masks or that a 2 ms fluctuation proves acceleration.

## Software checks and handoff

256 passed, one existing strict xfail for genuine fully faint front/blurred footnote print. Focused tests check owned identity-resize pixels, the complete uint8 relative-contrast boundary domain, distinct DN/relative semantics, and refusal to label connected extent as semantic body height. The current default imports no offline evidence tool and has no dangling `type_ink_*` imports. These checks establish software behavior, not physical correctness.

Prescribed venv and PYTHONDONTWRITEBYTECODE were used; pytest cache disabled. ONNX CPU is sequential, intra/inter 1; OpenCV requested 2 and reported 10 on macOS GCD. Full-pass timing includes lightweight offline call counters; paired timing is uninstrumented. Decode, first Paddle and all correction dependencies are charged; rendering/reference extraction and JSON serialization are excluded. Source/model/input hashes and commands accompany the receipts. The preliminary cache-only pass is retained, then superseded by the final pass after clone deletion.

The next useful repair is a complete native component/row-class attribution prerequisite that distinguishes measured small bodies, compatible-font borrowing and unknown before replacing M30/M35 body guards. The exact clipped, tall, dot, cell and weak-fragment probes now make that prerequisite reviewable. 02 inherits plain shared observations and common ink providers, plus unresolved DN/noise/source calibration; 03 inherits row/finite-domain/guide failures. No successor is self-launched and no private acceptance is claimed. Launch meter 64%; no later meter reading was available. The initial estimate is not the reason for this partial handoff.

Commit/fallback and exact final hashes are recorded in `ITERATION_HANDOFF.json` and `.md` in the iteration 2 evidence directory.

## Commit receipt

Git staging failed with `index.lock: Operation not permitted` in the assigned worktree. No commit or push was made. The validated `.astra/commit-F8-R8-01b-i2.patch` and executable `.astra/commit-F8-R8-01b-i2.sh` contain only this iteration's 28 task files, with the required trailers and guards for the checkout, staged state and exact candidate files. Validation applies the patch to an isolated archive of checkout HEAD and checks every resulting file/deletion. `ITERATION_HANDOFF.json` records the patch hash and explicitly leaves independent acceptance pending.

## Post-check addendum — iteration 3 launch

The coordinator committed this candidate as `051cc7ebcdbb23d6ef822a07484de1fc313ee011`. The independent R8c-01b-i2 check accepted it as the best checked head, replacing d5dc3e2; G1b remains PARTIAL. The preceding commit-block/fallback account records the worker's historical state, not the current branch status. Saved images, hashes and experimental receipts are unchanged. A structured post-check status is appended as `R8-01b-i2/POST_CHECK_STATUS.json`.
