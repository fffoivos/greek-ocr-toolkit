# R8-GEOM-03 iteration 2 — retain the repair and reach the wider cohort

**Resume** worker thread `01a1348b-aa90-7f91-b368-d8e9cd032401`, model `gpt-6.1-sol`, effort `high`, track `ff8-stack`. Worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Start at **`<HEAD>`**, expected `f2dbd106971197c75ae6e9f6eb44bde903614920` plus this planning-docs merge. This is iteration **2 of 3**, not a new allocation. Runtime at f2dbd10 is identical to db899f1/0474bf8; your corrected code remains archived. Verify actual source/configuration and keep the existing thread.

Owner words since iteration 1, verbatim, in order:

> ok I dont want you to use more than 20% of limit today

> Ok what does Astra say? Are we making progress though?

> Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample

**Yes, there is progress to build on:** the raster defect is solved, six mutations discriminate, cost fell about 35–45 ms, and the wider cases now have named callers. No runtime gain is retained yet. This iteration first qualifies the solved request repair, then brings its whole-component construction into the existing multirow partition caller on other books. A second replay of the same four rows is not the whole iteration.

Read the full independent check, including “Working on a wider sample”:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-03-i1_check.md`.
Read the updated `SOL_WORKER_HANDOFF.md`, `GEOM03_GATE.md` and unchanged `GEOM03_COHORT.json`. Your report/evidence are `docs/records/research/round8/REPORT_R8-GEOM-03-i1.md` and `.astra/fast_lines/out/round8/R8-GEOM-03-i1/`. Reuse `experimental-source/` (detector SHA256 `fe4058ef3d7521cfbad5928f8442a7ab866e8a67a23c2b4ca72dffe9c1e83079`), `FINAL_EXACT_EQUIVALENCE.json`, `PHASE26_CORRECTED.json`, `first_consumer_witness.py`, saved cohorts/replays and source manifests. The check gives its exact scratch root for raw `timing/` and `natural/` samples. No broad chat reread or new corpus collection.

## 1. Builds on the existing code

### First retain population R, without re-solving it

Adopt the corrected i1 `experimental-source/` by a scoped diff against this head, preserving its request-height mark bounds, endpoint widening, half-pixel certificate and exact work removals. Do not adopt `timed-source/`'s old per-row mark-height bug or replace the current tree with an archive. The live chain is `stack.pipeline.compose` → `type_extended.recover` → `type_residual_recovery.recover(version=11)` → restored `type_completion.complete_request` → `geometry_field_detector.native_bands/separate_bands` → `corridor_hulls`.

Re-time this exact corrected source using the drift protocol below, then run the fresh enabled/disabled 208 comparison and inspect every changed crop/exclusion. Qualify and checkpoint the four right rows as an independently retainable default improvement before experimental population-B changes. This is expected to be a short first step (the checker estimates about 30 minutes including review), not the whole iteration or a hard time limit. If valid cost remains over 100 ms, exact vectorisation of `native_bands` envelope/audit loops may create margin; prove equivalence on the 20 captured native batches and26 phases, not just four hulls. Required source/motif/rule refreshes stay.

**Correct the cost diagnosis.** The `competing_axis` conversion hoist is already done. The check withdraws its claim that motif/rule refresh cost is mainly vertex repetition: `geometry_joinbarriers.inspect` uses bounds, and `ink_recurrence.render`/motif use bbox and axis. Their extra image work on changed geometry is required. The remaining largest computation is `native_bands` (~50 ms, including ~22 ms separator and ~19 ms envelope/audit loops). Do not delete required refreshes or keep searching for the already removed vertex conversion.

### Then reach population B in the original-crop caller

The actual route is `stack.pipeline.compose` → imported `split_rows` = `geometry_rows.analyze` → `native(route='slow')` → `confirmed_partition` → `partition`, followed by `reconcile_rows`, footprint change detection, final faintness and frame/exclusion processing. `partition` currently slices the original Paddle polygon along accepted valleys; its union deliberately contains no recovered ink. Replace that extent construction **after an already accepted valley**, retaining the existing discovery, window gate, tracks and body-run acceptance.

Capture real calls first, using the i1 `first_consumer_witness.py` pattern (one stack run per page). Confirm item ancestry/native coordinates, `analyze` call index, the full `native` record, accepted valley and the first wrong output. The following are nominations, not proven row identity or a guarantee that every listed mark contains two complete rows:

| Population B page | Marks | Use |
|---|---|---|
| `s2-3229200bf47ca465a42d-p00002` | 5, 6, 7, 8, 10 | Working; existing skew preserved. |
| `an-a73d22211479-p000301` | 55, 57, 61 | Working; ruled layout. |
| `s2-c3ccfa3cea1347d7ad54-p00002` | 1, 2 | Original validation split, now development-retest; score after working-candidate freeze. |

Keep the accepted valley as the proposal. Reuse the solved certificate/refinement and tight whole-component hull construction on **this caller's own pixels, labels and transform**. Refine only a demonstrated crossing within the existing supported inter-row corridor; keep the original row identities. Assign each admitted component whole to one child, preserve detached-mark/body bridges, and verify the final raster has neither clipped members nor duplicate/foreign ink. Reuse or factor the small common primitives; do not call the whole residual recovery pipeline or copy a third separator implementation.

If a captured case does not have the alleged accepted valley, correct its population record and preserve its baseline. Do not bypass the window gate to make the nomination true. Saved native crops of 3229 m5 and a73d m55 already show why a mark/index lookup alone is insufficient. One complete row plus neighbouring slivers is a trimming problem, not permission to invent two rows.

## 2. Inputs match what the code expects

- `geometry_rows.native` uses its own rectified strip (`strip`/`to_page`), interpolated image, Gaussian/Otsu ink, CC8 labels/stats, `h*scale`, tracks, word runs, bridges and verified rules. Those are **not** M17's mean-mask labels or the residual-closing chains. Preserve their source identities and use their own rule/mark contracts; do not substitute M17's threshold or request-height selection.
- The existing `native` return record discards its strip/labels/transform and `partition(item,record)` receives no image. Pass a minimal optional prepared context explicitly from that same `native` call to the partition consumer, or an equivalent internal adapter. Do not reconstruct a different mask, relabel unnecessarily, stash arrays in globals, or serialize large runtime arrays in ordinary evidence. Keep public diagnostics/legacy calls compatible; record the new input contract and its lifetime.
- Page-space valley paths must map correctly to strip coordinates and back using the actual slope, origin and scale. `route='slow'` scale1 still uses remapping; rectified-pixel success is not proof of original-page conservation. Verify final page-space polygons through actual `rint`/inclusive fill against original native ink and the rectified membership. A half-pixel clearance is in the raster's units, not an unconverted page-space constant.
- `native`'s old crossing list uses pixels inside the original mask. That is insufficient for newly completed glyphs: check full relevant CC support, not just the masked fragment. A component cut by the strip ROI boundary cannot be certified whole. Row bodies establish identity, but filtering to body-sized components must not drop accents, initials or punctuation.
- One accepted internal valley does not certify both outer edges of every resulting row. The padded strip includes neighbouring rows. Use existing finite track/body/bridge evidence and compatible outer support to establish unique membership; do not allocate every component above/below the valley to the two children. Do not accept a tight hull merely because it preserves the wrong assigned set. Unsupported outer extent, attached rule ink, competing rows or ambiguous marks keep the existing slice. Preserve successful legacy pieces as an atomic parent partition if a replacement would break completeness/order or duplicate ink across siblings.
- The existing `confirmed_partition` requirement that every child has a whole horizontal body run remains. Do not relax its body/word criteria, fit new row axes, widen tolerances or impose a page-specific mark list on runtime. Refinement/hull success replaces the old vector extent in that qualified population; failure uses the established vector partition, or the same existing no-split result if it already failed. Do not replace a successful old split by an unsplit parent just because the new hull is unknown.
- `compose` currently assumes row splitting only partitions surviving polygons and cannot restore excluded ink. A hull can extend beyond its parent, so explicitly pass/check existing `removed`/forbidden regions at this consumer and preserve `source_ids`, `row_parent_index`/polygon, child ordering and cleared parent centreline. This is an input-contract repair, not permission to restore suppressed regions. Required ownership, source/motif/rule decisions for newly included support must be refreshed where they apply; footprint tokens, `reconcile_rows` and final faintness must see the new geometry. Final faintness alone is not every upstream source check.
- Keep page-field M17's default contract unchanged at identical inputs and preserve the already solved request-mode26-case contract. Residual/no-seed rows keep the existing admission route; 8686 row 5 cannot be fixed by a completion function it never reaches. `greekocr/pages/lines.py` and font tools remain pixel-seeded offline comparisons only; **no Paddle polygons in `PixelPage.boxes`**.

## 3. Removal and verification scope

The owner's scope remains, verbatim:

> Doesnt the correction mostly invovle removing things then? and building models that can help verify the existing mechanisms

Keep both useful gains independently reviewable: R default completion, then B whole-component extent in place of raw-box slicing where the current split is already accepted. Record old decision → common primitive → caller migration → deleted duplicate computation/path. The old vector partition remains a single explicit fallback for unsupported cases; do not add another competing vote. Sharing a certificate is not removal of all row or bend authorities.

### Preset timing protocol: measure the corrected source under stable controls

The100 ms limit does not change. The i1 worker's final baseline/detector were about 15%/13% slow; quiet corrected-source 10-sample order medians were85.5–97.5 ms. That is a near-threshold result, not a proved failure or a new runtime acceptance tolerance.

Before inspecting candidate deltas, record the source/config hash, warm-up count, thread settings and absolute baseline/detector reference. Use the same harness and compare reference controls with i1/checker quiet receipts; investigate a materially slower reference rather than blessing a new slow baseline. Predeclare **10 warm pairs for each order and each genuine window**, in two 5-pair blocks; use every valid sample in the prespecified 10-sample median for that order/window. Preserve sub-block medians too. Do not average orders together, subtract detector drift, borrow timed-source clocks, or keep only passing samples.

A block is drift-invalid if its unchanged detector median differs by **more than5%** from the reference; also flag baseline-only controls moving materially in the same direction. Decide invalidity from controls, not the candidate delta. Retain the entire invalid block in the receipt and rerun the block after controls settle, whether its delta passed or failed. If a new reference is necessary, restart the complete comparison with the reason recorded. At most one replacement per invalid block in this iteration; persistent drift means cost inconclusive, not algorithm failure and not qualification by repetition. No long blocking waits or unbounded repeated timing.

Both per-order medians must be ≤100 ms for each affected request, including natural request census and required refreshed decisions. Apply the same control checks there; the two canonical windows alone cannot hide another slow request. Group B uses the full affected page as the unit, with the unchanged ≤100 ms added-page ceiling against f2dbd10/db899f1 including combined R+B work and final decisions. Attribute B's additional cost against the separately qualified R checkpoint too. Clean pages gain no processing pass or reproducible regression beyond controls. Full208 speed remains a separate reported result, not a claim that the inherited global<1s gate is solved.

### Wider evidence and per-case scoring

Freeze source/configuration after working-page changes. Score **all 25 marks**, all seven 4959 rows, missing 8686 row 5, c8/e259 and all seven negatives: **42 case rows** in JSON plus a readable table. Keep the original cohort and first-validation receipt; validation was already exposed in i1 and is now **development-retest**, not fresh untouched validation. Score c3cc after freezing the working candidate. Do not replace those cases or inflate the sample with lattice phases.

For every case report: page/book; original split and current validation exposure; nominated population **and actual captured consumer/call index**; native source coordinates/ancestry; first failing check; before/after status (pass/partial/unknown/fail); complete text/mark coverage and neighbour/rule exclusion; before/after crop paths; regression flag; default/experimental/legacy-fallback state; source/config hash. An unchanged legacy fallback is not a fix and not automatically a regression. Include actual pipeline reachability, not a lookup using a final item index. Summarise positive gains by book/layout and R/M/B/A/F; list negative outcomes separately.

Group A's 15 marks mostly stop at the two-word-run gate; only 2cfe m19 is a confirmed one-row-plus-slivers witness so far. Group F uses page-field/domain consumers. R-left and M-admission remain distinct. Do not force those into B or expand i2 into row discovery, trimming, domains and all missing rows. Capturing their actual failed caller and preserving them is sufficient this iteration. Optionally classify the 48 safe-unknown requests from the existing audits after the main work; no new broad audit run is needed.

Tests must call the real native/partition/analyze/final consumers. Use captured B fixtures from both working books, then the c3cc retest, with 13-origin perturbations where that fixture's actual grid permits them; include transformed/skewed export and mark-bridge/forbidden-region checks. Restoring vector slicing must fail an actual native completeness or contamination assertion on a repaired B case; restoring the old certificate must fail a physical raster assertion. A test demanding a different polygon shape is insufficient. Keep R's26-case and six-mutation evidence; distinguish fixture-only mutations from page-level differences. Never change strict xfails on unrelated default contracts just to make the suite green.

For the final combined source, run the fresh 208 route comparison: both repairs disabled reproduce f2dbd10's exports/non-clock evidence; R-only checkpoint is source-qualified; enabled R+B changes are all reviewed at native scale, including exclusions and previously complete rows. At identical inputs default page-field M17 remains unchanged; downstream aggregate inputs may legitimately differ. Preserve gate controls (“ἀποξήρανσίν”, M33 endings/narrowings, weak/pale text, initials/numbers and 0ce9 #34/#36). The coordinator alone runs private44. Do not transfer R-only 208/timing to a later B source without verifying what changed.

## 4. No new pipeline or page model

Reuse the solved local raster/whole-component construction in existing callers. No new row finder, source/ink calibration, global font/bend/gutter model, Rust work, default slow-pipeline call, blanket gate loosening or corpus-selected runtime case list. Keep current skew/curvature proposals; this is complete extent after an existing accepted split, not shared page-edge curl detection. Do not port residual support chains into `native` or treat every owner “two-line” mark as two complete word rows.

If a B case fails because its accepted valley/outer identity is wrong, preserve the old qualified behaviour, show the first native counterexample, and return that evidence. Later trimming/domain/axis work needs the next planner-written prompt. Shared primitives may be factored when both current callers and regressions substantiate their common contract; avoid another permanent duplicate geometry engine.

## What counts as progress and how to finish

**Iteration target:** retain the qualified four-row request repair, and retain at least one physical B correction on **each of the two working books** if compatible native evidence permits it; evaluate both c3cc B retest marks and every other frozen case honestly. The first target alone is valuable PARTIAL, and a sound one-book B subset also survives; the wider target is not an all-or-nothing retention rule. Whole-task COMPLETE still requires `GEOM03_GATE.md`, including unsolved left/missing/layout targets.

Report retained physical/output gain, retained mechanism/deletion, experimental progress, cost confidence and remaining first failure separately, per front. Do not call the whole iteration “failure” merely because G3 is incomplete. Positive source-bound evidence must support optimism: another all-unknown table without a new consumer is diagnosis only.

After R qualifies, do not withdraw it because a later B trial fails. Keep independent checkpoints, revert only the failed trial, and use final quality/cost evidence on the retained head. If unstable timing prevents qualification, say cost inconclusive and preserve the experiment; do not spend the entire iteration chasing clocks instead of the broader caller. Never retain a crop regression or weaken the cost bound. Only iteration 3 remains after this; return the result and full independent check to the Astra planner, who writes its prompt. Do not write or launch it yourself.

Deliver `docs/records/research/round8/REPORT_R8-GEOM-03-i2.md` and `.astra/fast_lines/out/round8/R8-GEOM-03-i2/`: source-bound R checkpoint, corrected timing controls/raw samples, captured B input contracts, actual-consumer/mutation/native fixtures, `COHORT_CASES.json`/`.md` (all 42), first-failure/validation exposure records, changed 208/exclusion review, updated133-mark/missing-page ledger, cost/deletion receipts and `ITERATION_HANDOFF.json`/`.md`. Preserve first-validation history. Add a dated f2dbd10 addendum to the i1 report/handoff correcting the categorical cost-failure claim and old commit state; cite the independent check rather than erasing the earlier measurements.

Ask the reviewer: which dependency is now solved in retained code; which additional books/layouts gain; what the actual caller evidence proves; whether fallback stayed safe; whether control drift was handled without cherry-picking; what remains for A/F/M/R-left; and which exact next step can reuse the accepted work. Keep the progress verdict per front.

**Today's resources:** owner cap 20% of the meter, coordinator reports2% now. The coordinator reports new-launch stop 18% and emergency kill 21%; **21% is not permission to exceed20%**. Checkpoint and stop before the owner's cap, and verify the effective daily guard before launch; the old 97/99 weekly guard alone is insufficient. No reset or launch route may bypass today's cap. Pause/resume unfinished work under the same iteration identity when authorised capacity returns. Use only the established authorised MacBook runner; no concurrent benchmarks, extra agents, held-out access, production edits, background jobs or push. `greekocr/` and other worktrees stay read-only.

Commit on `astra/ff-r8-stack`; if blocked leave `.astra/commit-F8-R8-GEOM-03-i2.sh` with validated hashes and required repository trailers. Finish in plain words, then `RESULT: DONE|PARTIAL|NOT DONE` with this iteration, commit/fallback, retained case gains and recommended checked head.
