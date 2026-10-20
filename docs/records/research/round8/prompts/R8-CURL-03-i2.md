# R8-CURL-03 iteration 2 — repair the existing continuation consumers

**Resume** thread `01a13968-c97e-7191-8842-cb64b8b62789`, model `gpt-6.1-sol`, effort `high`, track `ff8-stack`. Worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Start `<HEAD>` = coordinator-filled full hash of **034bff94b0072d88f69cda4e88af112cd32bd5ba plus FP8ah docs**. The coordinator reports ff-merged a86821b has the same runtime; do not reset the worker branch to it. CURL has3 slots total, i1 used; this is i2, not a new allocation. I3 comes from Astra after result and independent check.

Read `docs/records/research/round8/SOL_WORKER_HANDOFF.md` and the **full** independent check:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-CURL-03-i1_check.md`.
Then read your i1 report and the named code/evidence against that correction. The check's scratch is
`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/f1db7209-77e0-476f-b75b-886a69c81def/scratchpad/check_curl03_i1/`:
`meshcmp.py`, `endresid.py`, `elig.py`, `tree_fix/`, `tree_q3/`, `protect_local.py`, `vetoclass.py`, and the native images. Hash any scratch sources used; they are diagnostic counterfactuals, not runtime providers. If missing, obtain the exact evidence via the coordinator rather than claim to have reproduced it.

## Owner contract and corrected starting point

Owner, verbatim:

> right but now the whole page bend should be global we dont need to check individual lines right?

> so if we know the bend and we have the text-lines' lines we can just follow them to the end of the page in a way
> that does not impose on the other liens

> Right our idea is mostly to target the edge of the page, where actual curvature presents due to book structure, and have a heuristic that actually detects it, if any

> so in the site you have published I see that 8686 p5 doesnt deal with curvature well

> But the whole point of this generation of our model was so that we odnt have to have duplicate checks

> Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample

Latest direct instruction:

> but the segments are not smooth to my eye despite what the reviewer says, and I hear it is very slow

> ok lets just normally continue with the rest of the tasks in the plan

Keep `Stack(final_export=False)`, accepted R/B rows, source exclusions and geometry's CLOSED PARTIAL status. This is a bounded continuation/admission repair, not GEOMi4, a mesh rebuild, or general final-export smoothing. Do not present the experimental page bands as accepted smooth/fast output.

Your i1 source is accepted as evidence/tests only: runtime byte-identical to0b620be, bare archive357 passed/1 old skip/14 xfailed, no retained physical gain. No new private44 run was needed. **Correct the diagnosis before implementing:**

- The current mesh predicts the bend. Median last-letter baseline residuals are roughly−6px on8686p5,0 onp7,−1.8 on4959p4,+2.3 on3229p5. The path makes533/569 sampled end letters eligible versus199/569 for the capped tangent. These eligibility samples are diagnostic, not native final ownership proof. The last10–20px error on some top rows is a possible refinement after consumption works.
- I1's material-envelope loop used the prior loop's last `shared`. This was a coding bug, not proof that sharing contacts harms p7. The one-line scope repair restores p7/c8 parity. 9ea's remaining lost narrowing is caused by replacing the **in-anchor** map path.
- On8686p5, even the old path accepts0/30 M33 rows:27 fail the legacy-polygon overlap veto. Offenders include17,144px under adjacent rows' straight boxes versus613 under same-row end fragments. The src37 path also stops at box+6h, aroundx1935, before the last letters.
- The seedless row is already discovered and proposed. The supposed rule `[1943,440,1955,726]` is stacked curved text, not a verified rule. `verify_rule` correctly returns unknown; `protect` wrongly discards the whole witnessed proposal. Native print is **χωρητικότητος**, not the earlier γεωργικότητος witness string.

Reusing the mesh after correcting those failures is not a third renamed variant of a falsified model. Do not repeat the buggy archived diff as an experiment or cite its passing rejection test as evidence against continuation.

## 1. Builds on the existing code

Make the two repairs independently reviewable, in this order. **Retain a qualified separator gain even if the continuation repair remains partial.** Preserve a source-bound intermediate checkpoint so the final208 can qualify exactly the kept subset.

### A. Local unknown separator — first deliverable

Existing chain: `stack.pipeline.compose` → `type_extended.recover` → `type_residual_recovery.recover` → `type_barriers.protect` → `layout_barriers.fast.verify_rule/clip_polygon`; returned pieces then pass `piece_support`, competing-axis/rule-contact checks, completion and final compose consumers.

Replace `protect`'s whole-proposal `return []` **when a nominated vertical run is unverified** with the checker's local-unknown construction. Keep the side supported by this proposal's own `type_witness_points`, bounded outside the nominated run using existing clipping/clearance conventions. Leave the run unresolved; do not call it a verified separator or prove that all such runs are text. No witnesses or ambiguous/balanced ownership still abstains. An unsupported majority count alone must not silently discard an independently supported body chain: inspect both sides and use the existing downstream `piece_support` contract. Do not add a new ratio/count guard to make the prototype pass.

Keep verified-rule, `ink beside rule` and `short text crosses rule` decisions unchanged. With multiple nominations, evaluate witnesses in the surviving piece/domain, so a removed side cannot vote again. No crossing exclusions or clipping an admitted whole body merely to manufacture a surviving piece. The local unknown can leave unresolved terminal ink outside; name it rather than claiming the full line recovered.

Reproduce the native missing-row fixture and real final page. Preset witnessed body target: final crop approximately`[583,591,1939,679]`, the row identified by “τρου χωρητικότητος … ὀψίμως συλλεγομέ”. Use these coordinates as a review locator, not runtime constants or a box-equality acceptance test. The risen `νων` is a separate continuation target. The scratch prototype's seven unchanged controls and correct final body make this worth landing, but it still needs the41/208 checks.

### B. M33 continuation — replace the failing consumer

Existing chain: `geometry_page_field.render/certify/invert_points` (M15) → `geometry_field_detector.run/displacement` (M17's shared evidence) → `compose` → `geometry_envelopes.guided/correct` as `smooth_envelopes` (M33). Preserve M20 `geometry_feature_correct.retention_ink`, `owned_retention` and current exclusions. Reuse the field already measured for this image/region; do not call `render` again per row or introduce a second field.

1. **Per-row state.** Store/read field identity, phase and continuation support from the current row record. Fix the stale-variable assumption if reusing any archived code. Mixed supported/unsupported rows and iteration order must not leak the last row's phase into another envelope. Avoid computing native extrema only to throw them away and replace them with the material envelope.
2. **Keep the observed map path.** Preserve the existing in-anchor computation, including its normal sampling/filtering and current narrowing decisions. Use the common field only **beyond the observed map anchor**, with a continuous endpoint correspondence. A detector bounding box and a reliable map span are not interchangeable. Do not perturb all in-box contacts to fix an end;9ea1p202's useful narrowing is a required control.
3. **Finite extent.** For a supported shared row, replace the box±6h continuation limit with the existing field's actual finite support along that row, clipped by native page boundaries, finite column/rule evidence and unknown inverse domains. Sampling farther is a search domain, not permission to emit a ribbon to the page edge: the final extent still follows verified native components. Do not join finite runs across NaN holes or let `np.interp` clamp through an unknown domain.
4. **Replace the veto in its supported population.** Today `correct` treats newly covered ink as foreign when it lies under any other legacy polygon: `new & ~old & other & ~mine & ink`. For the rows with supported shared geometry, use the existing field's material phase and current row/body witnesses to decide the native component's row instead of that legacy-box claim. Map support with `invert_points`; compare it with this row and the actual neighbouring witnessed phases. Preserve body contacts already known to belong to a neighbour. The old rectangle's containment is not a second ownership vote. Unsupported rows keep today's route.

This last step is the highest-value experiment and **was not prototyped by the checker**. A monotone mesh supplies ordered virtual paths, not correct row identities, accent owners or a guarantee that two printed rows are separate components. Inspect complete component support, not only centroids/corners, where the decision depends on a crossing. Use existing component/mark evidence; do not reassign a detached accent under a descender just because its phase is slightly closer. Unknown/folded phases, conflicting body witnesses and touching two-row components remain locally unresolved. They are not automatically foreign and must not restore a whole-row legacy veto. Retain supported continuation where a local unresolved extent can safely stay unchanged; report exactly what still blocks a complete end.

Construct the continued envelope in the existing native/material path representation, preserve own whole letters/marks and exclude genuinely neighbouring ink using the shared between-row correspondence and existing envelope primitives. Do not obtain acceptance by deleting all neighbour checks, changing the relative-ink threshold, enlarging every crop or activating experimental `tessellate`. Keep source/motif/frame decisions on their correct actual inputs. Avoid making a new general page ownership layer just to feed M33.

### C. Same-row end fragments — only after B reaches the end

These are a minority of the observed veto pixels. Reuse `geometry_envelopes.endpoint_pairs` to nominate fully owned endpoint fragments; then check their shared phase and native support. Its current code tests owned contacts/path distance; it does **not** already prove0.25h material-phase agreement. Do not invent that threshold as a law.

Join/retire a fragment only if the actual resulting crop contains all of its own text in the same physical row, with no independent other-row/source identity lost. Preserve provenance/source IDs and refresh affected consumers. A component with two rows is not a fragment to merge. If the continuation already yields the required unique final row, no extra merge mechanism is needed. No global reconcile-priority rewrite, general mixed-box repair or a73d item54 work.

**Mesh boundary/knot refinement is deferred out of i2.** If these consumer repairs reach all but a last letter, record its measured native residual for the i3 decision. Do not spend this iteration changing8h knots, smoothing modes or fitting independent curves first.

## 2. Inputs match what that code expects

Use the original native page and immutable initial Paddle map/items, plus current fast row observations, source IDs, finite shared field, prepared components and exclusion/column evidence. Row phase is a body-support/material coordinate, not a baseline class or foreground decision. `correct` still skips field-owned rows; do not force M33 onto every M17 row.

**Fix the fixture contract first.** In `features_geometry/curl_missing_row_native.json`, `item.polygon` is local but `type_support_bounds=[574.25,1995.75]` and `type_witness_points` remain native. Its origin is`[553,440]`. Create a versioned corrected sidecar/adapter from `absolute_item`, translating **every** spatial field exactly once; preserve the original write-once native NPZ and evidence. Assert native↔local equivalence and correct support bounds before calling real `supported_extent`, `protect` and `piece_support`. A passing test with mismatched frames is not evidence. Do not fix only the bounds and leave the witnesses outside the crop.

For M33, bind each row's identity/observed span to the same field image/region/scale. Retain finite NaN semantics of `invert_points`, no row0 clamp and no bridging holes. Respect rule y ranges; a median-x full-height split is not a valid newly invented boundary. Do not rebuild general column domains in this task. A single shared field governs all supported continuation paths; the row provides its anchor/phase.

Pass already measured field/native data explicitly. Shared arrays require identical image, ROI, resolution, kernel/threshold, label identity and exclusion state. Do not reuse changed-row B5 anchors/votes or M35 calibration populations; compute needed changed decisions once on current rows. Unchanged component photometry can be reused only under its actual input contract, not by renaming a regional paper estimate as a page estimate. Source uncertainty remains source uncertainty; no new universal foreground/noise estimator.

The saved slow pixel-seeded `greekocr/pages/lines.py:_pool_geometry/_assign/_make_lines/_boundaries` and original native reference are read-only comparison mechanisms, not row-ownership truth. If needed, `segment_page(native_page)` retains its own pixel preparation/rough regions. **No Paddle polygons in `PixelPage.boxes` or `_discover`.** Do not reinterpret the missing row as undiscovered: the live residual chain already has its24 own body witnesses.

## 3. Removal and verification scope

The deletions/replacements are explicit: whole-proposal rejection for an unverified local nomination; capped tangent/domain for the adopted supported continuation; and legacy-box containment as foreign-row authority in that same population. Do not preserve these as parallel vetoes after the new decision, and do not add another qualifier in front of them. Unsupported physical populations keep their existing route, named separately. Report actual callers migrated, decisions displaced, native preparation reused and runtime lines added/deleted. A new helper alone is not architectural simplification.

First bind exact positive native masks from the check's four-page examples: src37's `ἐξόδων πη-`, and the χο/μέ/ἀμέ endings on8686p5; separate missing-row body and its `νων`. Use component IDs with input hashes/coordinates as **test witnesses only**. Treat quoted text as review identification, not OCR scoring. Do not use page IDs, crop IDs, count thresholds or manual ownership in runtime.

### Committed tests through real consumers

Extend/repair `features_geometry/test_curl_consumer.py` with small committed fixtures, no `.astra` dependency, new skip-if-missing or ignored multi-GB pack. Keep the existing seedless `field` test. Replace the passing assertion that the real missing row is dropped, and remove its strict xfail only when the real repair makes the positive physical assertion pass. Keep all unrelated strict xfails.

Required protection:

- The corrected native fixture exercises `supported_extent`/`protect`/`piece_support`, and the real recovery→compose path emits the witnessed body without a rule or other-row letter cut. Restoring whole-proposal abstention fails that returned-raster assertion. Cover absent/balanced support, successive nominations, a genuine printed rule, `ink beside rule`, `short text crosses rule` and the table/leader/noise controls.
- Real `guided`→`correct` and final compose consume the same current row record. A two-phase mixed supported/unsupported batch, permuted and with diagnostic detail on/off, produces corresponding same crops. Restoring stale `shared` leakage must fail; do not merely assert metadata presence.
- The observed-anchor path and9ea1p202 narrowing remain; the positive end contains all its own native witnesses. Restoring tangent/box+6h or discarding outside contacts must fail the end assertion. Replacing in-anchor support must fail its own regression assertion.
- A true neighbouring body/accent remains in its own row while own text under an overlapping legacy box is admitted. Restoring the legacy-box veto must lose a correct end and fail the test; bypassing all foreign support protection must wrongly acquire a neighbour and also fail. Correct phase ordering alone is not the assertion.
- NaN/fold/finite-rule/domain controls reach the live consumer; no unknown-to-row0, no crop across the rule, no finite intervals joined across a hole. Same-row fragment retirement, if implemented, must conserve its whole text and fail on a wrong-row fragment.

Archive the old buggy replay as historical evidence with an explicit corrected interpretation; stop using `test_withdrawn_shared_consumer_still_fails_the_native_final_crop` as a shared-continuation quality test. Prefer the new real positive/control assertions to repeatedly loading a known-buggy patch. Test mutations must alter the production decision and fail the intended physical assertion.

### Same41 pages, then208

Reuse the immutable `.astra/fast_lines/out/round8/R8-CURL-03-i1/CURL03_COHORT.json`, SHA256
`377df97a07b0428b8591783f2dd093d11e0c78fb56ea4c7511aa4a7ed998a766`.
It has41 deduplicated pages: the28 curl cases, exact12 geometry pages and both8314 table/leader controls. Preserve original input hashes/categories; all are development-retest. Do not reset the cohort or replace a hard negative. The20 flat/skew negatives must retain their accepted outputs; any unexpected change is reviewed as a regression, not relabelled curl to pass. All4 positives, unconfirmed candidates, noisy74cdp2 and the saved42GEOM/22FONT cases remain visible. I1's “evidenced curl” on nominal negatives is a diagnostic disagreement, not permission to drop the negative.

Use the same initial detections for baseline and each source-bound checkpoint. Report per page: accepted/rejected separator nominations and retained side; measured/current field versus anchor continuation; new whole end letters and remaining missing text; final row identity; cuts, wrong-row/duplicated ink, gaps and source exclusions; fragment retirement and unknown local spans. Freeze baseline inside/outside masks and pair domains. Relative ink and Otsu observations are separate, not semantic ownership truth. Inspect every changed final crop plus neighbours; when22FONT marks change, check actual final exports, not archived proposals alone.

Preserve the four4959p5 R rows,3229p2 B row,8686p5 `ἀποξήρανσίν`, Γ. Μαυρομιχάλης, faint1be6/weak31f40/0ce9#34/#36, and useful M33 endings/narrowings on466,7792,c8,9ea,dbd,d323. Separately review c8p36 and9ea1p202 outside the41 because i1 found collateral there. The entire208 pass covers every unverified separator occurrence; enumerate each changed nomination/page and inspect native output, not just the eight scratch pages.

The new missing-row crop can overlap an unchanged legacy box that already intrudes into its physical row. Quantify this and inspect both strips; do not automatically reject a correct recovered body by resurrecting the old rectangle veto, and do not hide the resulting duplicated ink or declare non-overlap solved. No newly misassigned letters/marks or new foreign row in a continued crop. Remaining unchanged legacy coverage is named geometry debt; if a change introduces a real wrong-row inclusion, repair/reject that change. The goal is supported continuation without intruding on neighbours, not a prettier path overlay.

### Cost and retention

Run established authorised MacBook development work sequentially; arrange the coordinator's quiet window for paired timing, no background/concurrent benchmarks. Reuse the frozen same-input baseline034bff9, and measure the source actually retained: separator-only if continuation fails, combined if both qualify. Fresh208 exports, relevant committed suite and every changed crop must correspond to that exact source. Use both orders, ten warmed pairs with five-pair blocks, unchanged detector/reference controls, existing5% drift rule and at most one replacement block; keep invalid samples. Report affected preparation/field/contact/source/reconcile stages, correction/file-to-final median/p95/max/>1s, clean-negative costs and per-positive increments. Existing≤100ms incremental-page criterion and negligible-clean/under1s charter goals remain; inherited breaches are explicit debt. No post-hoc cost relaxation or speed claim from an unqualified clock.

**Do not make the two repairs an all-or-nothing batch.** A source-qualified, physically safe separator improvement can become the default while the M33 experiment is withdrawn. Preserve that intermediate source/evidence; do not roll the gain back solely because the iteration's full target is incomplete. Conversely withdraw harmful continuation even if other rows improve. An unqualified costly candidate stays explicit/off-default, not silently accepted. No `final_export` promotion.

## 4. No new pipeline or page model

All work is in the existing fast prototype/callers and committed tests/evidence. `greekocr/` is read-only reference. No new detector, row/page model, per-row bend fit, windowed unclaimed-component tracker, M37 activation, universal font/ink provider, Rust/production work or repo reorganisation. No general tessellation/reconcile/gutter rebuild. Two demonstrated consumer decisions are in scope; no stack of new guards around them. One bounded revision of an exposed assumption, then retain the best qualified subset and report the remaining first failure rather than invent a renamed variant.

No private44 inputs/images, OCR tuning, pushes, background jobs, spawned workers or self-launch. Existing source/owner ledgers stay accurate; no page-specific runtime exceptions. Keep accepted runtime and source identity reproducible.

## What counts as progress and the handoff

**I2 preset physical target:** the missing row's witnessed body survives final compose, and src37's end plus the identified χο/μέ/ἀμέ ends become whole in their correct final rows, with negative/layout/faint controls preserved. Report the remaining `νων` separately. Score every frozen case, not only8686. No assertion that this completes CURL globally.

**A valuable retained partial result** is either independent repair producing real, preserved final text after41/208 qualification, with its old decision removed for that population. A demonstrated complete end through M33 blocked later by a named final consumer is experimental physical progress; keep its exact source and witness. Correcting the stale variable/tests or field measurements alone is mechanism/diagnostic progress, not recovered text. Ask the reviewer which earlier failure is now solved, what is retained versus experimental, whether the blocker narrowed, and what i3 no longer needs to redo.

Write `docs/records/research/round8/REPORT_R8-CURL-03-i2.md` and `.astra/fast_lines/out/round8/R8-CURL-03-i2/`: unchanged cohort hash; source-bound separate/combined checkpoints; actual caller/deletion map; per-case41 and208 nomination/final-raster ledgers; native whole-page/strip/coverage views; field/row/mark attribution witnesses; fixture/mutation receipts; timings and exact `ITERATION_HANDOFF.json/.md`. Add dated corrections to i1 report/handoff/test comments: adequate mesh, stale variable and in-anchor bug, real M33 veto/domain, correct χωρητικότητος text, fixture frames, and delivered034bff9 commit. Preserve historical patches/receipts; do not rewrite the old claimed experiment as successful.

For any retained changed runtime the **coordinator alone** runs private44: accepted baseline and frozen candidate **whole-page segmentation, every actual line strip and actual-mask coverage maps on all44**, including unchanged pages, curved ends, lost/extra rows, cuts, ownership/duplicates/gaps and cost with detector control. Default/experiment are labelled. Repeated44 is regression evaluation, not fresh untouched validation; any owner-exposed page becomes development-retest. Workers/planner never see private inputs or images.

Meter11% reported, no14October daily cap; existing97% launch/99% run guard and stop signal remain. Commit with the repository's single required trailer block. If staging fails, leave one source/hash-validated fallback under `.astra/` that **executes when invoked bare**, because the runner calls it without arguments. No required `--execute` flag; optional `--check` may validate only. Keep report/commit state current; no unguarded retries. Return result/check to Astra for i3. Final: plain words, then `RESULT: <DONE|PARTIAL|NOT DONE> <one line>`.
