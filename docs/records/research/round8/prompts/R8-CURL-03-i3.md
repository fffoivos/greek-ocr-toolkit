# R8-CURL-03 i3 — retain safe continuation when a local component is unresolved

Resume worker thread `01a13968-c97e-7191-8842-cb64b8b62789`, model `gpt-6.1-sol`, effort `high`, track `ff8-stack`. Worktree: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Start from `<HEAD>`: checked `fea451c5ec234e196076074cc1f9bd9233da41f3` plus the coordinator's FP8ai documentation merge. Verify the source; do not reset the branch. **This is CURL's third and last authorised iteration.**

Keep the recovered-row change A, the accepted R/B rows and source exclusions. Keep `final_export=False` and `bend=False`. Deliver a complete curved ending through the existing default route if it qualifies. If continuation fails, preserve A and close CURL PARTIAL; do not spend another slot or reopen general geometry.

The owner's curvature contract, verbatim:

> right but now the whole page bend should be global we dont need to check individual lines right?
>
> so if we know the bend and we have the text-lines' lines we can just follow them to the end of the page in a way
> that does not impose on the other liens
>
> Right our idea is mostly to target the edge of the page, where actual curvature presents due to book structure, and have a heuristic that actually detects it, if any

The reported page fault, verbatim:

> so in the site you have published I see that 8686 p5 doesnt deal with curvature well

The owner's latest direction remains:

> but the segments are not smooth to my eye despite what the reviewer says, and I hear it is very slow
>
> ok lets just normally continue with the rest of the tasks in the plan

And the architectural and sampling requirements:

> But the whole point of this generation of our model was so that we odnt have to have duplicate checks
>
> Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample

Read `SOL_WORKER_HANDOFF.md`, PLAN's FP8ai section, `REPORT_R8-CURL-03-i2.md` and its `ITERATION_HANDOFF`, then the **entire** independent check:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-CURL-03-i2_check.md`.
Its native witnesses/counterfactuals are in the neighbouring `check_curl03_i2/` directory. Use your saved i2 `continuation-source/`, `CONTINUATION41_LEDGER.json` and `prototypes/fast_lines/evidence/curl03_i2_continuation_withdrawn.patch` as evidence, not an accepted patch to apply wholesale.

I2 retained real text: one body row on 8686 p5, and the coordinator independently found another recovered body line on a private page. Development: 207/208 pages unchanged. Private: 43/44 unchanged. Report those separately; the check's “251/252” aggregate is inconsistent with two changed pages. The recovered 8686 body's 24 witnesses are whole, but several tails are clipped and risen `νων` is still absent. **No complete curved end has yet been retained.**

## 1. Builds on the existing code

### A. Preserve admission and close its narrow support-bound hole

The retained change is in `shared/type_barriers.py:protect`, called by `type_residual_recovery.recover`. An unverified vertical-run nomination becomes local unknown; exactly one side with independent existing `piece_support` survives. `verify_rule`, `clip_polygon`, witness support and the verified-rule/short-crossing/ink-beside-rule decisions remain the authorities. The `type_recovery.run` caller supplies no witnesses and stays unchanged.

The checker found a theoretical overhang: returning a piece from `protect` bypasses `recover`'s later `supported_extent(q)` fallback. No development occurrence was found. Harden **only the newly retained local-unknown side** when its proposal has valid existing `type_support_bounds`: reuse `type_residual_recovery.supported_extent`, then recheck the existing `piece_support` contract on the actual clipped piece before accepting it. Use a delayed import or a small shared placement if required by the existing imports; do not copy the bounds calculation. Do not clip all ordinary proposals or invent bounds for absent/invalid input.

This is an admission extent, not a permanent detector-box limit on later curvature search. A later continuation may extend it when new native support has been verified. Preserve A's recovered body, “τρου χωρητικότητος … ὀψίμως συλλεγομέ”, at approximately `[583,590.7,1939.5,679]` (review locator only). If this hardening cuts accepted true support, keep A unchanged and record the contract defect; do not sacrifice a checked text gain to land a theoretical fix.

`here` filtering in A is redundant because `piece_support` already filters witnesses inside each piece. Removing it is optional cleanup. M4 is an equivalent mutant, not a missing physical test; do not manufacture a test to distinguish equivalent implementations.

### B. Replace M33's whole-row refusal with local retreat

Work in the existing chain: `geometry_page_field.render/certify/invert_points` → `geometry_field_detector.run/displacement` → `stack/pipeline.compose` → `geometry_envelopes.guided/correct` (M33, imported as `smooth_envelopes`). Preserve M20 `geometry_feature_correct.retention_ink`/`owned_retention`, exclusions and the current final consumers. Use the field already built for the page/region; do not render or fit it again per row.

The shared mesh is useful. The old capped tangent makes far fewer risen end letters eligible. I2's new ownership signal nevertheless returned at the first contested component, again refusing the entire row. On src37, 119 off-row pixels in ten components rejected 16,857 own pixels. This ratio is explanatory evidence, **not** a permission to ignore those ten components.

Reuse only the sound parts of B:

- Store phase, field, observed anchor and finite domain in each row's own record; no stale `shared` from another row.
- Keep the current observed-map path, sampling and narrowing **inside the anchor**. Use the common field only for continuous continuation beyond it. Preserve 9ea1 p202's useful narrowing.
- Replace box±6h as the supported continuation's search limit with the existing finite field region along that row. Native page limits, actual column/rule evidence and unknown inverse domains still bind it. Stay in the connected finite interval containing the anchor; never interpolate across NaN holes.
- Use existing field phase plus actual row/body/mark support to identify own, neighbouring and unresolved native components. A legacy straight box covering a component is not an independent foreign-ownership vote. Monotone phase alone is not proof of an accent's owner or of a joined two-row component's identity.

**Do not bring back `material_band`.** It added a separate separator construction and crashed on empty grids on 4959 p5, c8 p36 and 9ea1 p202. Use M33's existing envelope representation. Do not retain that rejected branch by surrounding it with an empty-grid guard.

At `correct`'s `np.any(...)` → “new overlap with retained neighbor ink” decision, and B's corresponding `material_foreign` early return, replace the supported population's whole-row verdict with finite **local obstructions**. Collect the actual component extents and reasons. Walk outward from the observed anchor, keeping the safe supported continuation. Retreat the relevant boundary around a known foreign/unknown component using existing clipping and the existing .12h-style clearance where applicable. This is clearance around an obstruction, not tolerance to cut a glyph.

Only the affected stretch retains the old polygon where old support exists. Outside it, unresolved support stays unclaimed. If a safe connected envelope cannot pass an obstruction without cutting or taking another row's ink, stop that end there; keep the safe prefix, the other end and other rows. Do not hop across an unverified interval to claim an ending. Do not merge separated conflicts into one first-to-last old-box span. Do not reject all changed components of a row because one local content decision is unknown.

The new result must be the actual polygon consumed downstream and rendered into the OCR strip. A mask-only exception hidden behind an enclosing polygon is not a repair. Do not import experimental GEOM-04 legacy-interval machinery, add tabs/slivers or claim smoothness from a path overlay. Keep own whole glyphs/marks and existing exclusions; a touching two-row component remains unresolved locally, never assigned whole by majority or silently cut. No speck-size waiver, percentage threshold or weakened source decision.

Unsupported rows keep today's route. In the adopted population, remove the old whole-row legacy-box veto and matching first-error return; they must not run as second decisions after local retreat. If same-row end fragments still prevent one final crop, reuse `endpoint_pairs` only to nominate them; retire a fragment only after the final continued crop contains its whole same-row support. No general reconcile-priority change or new fragment tracker.

## 2. Inputs match what that code expects

Use original native pixels, initial Paddle maps/items, current row/source identities, prepared native components, the existing finite field and exclusions. Distinguish observed-map anchors, detector extents and physical row support. No independent per-line curve fit or assumed bend on a flat page.

Use the corrected versioned missing-row fixture from i2. Translate polygon, `type_witness_points` and `type_support_bounds` together, once, from `absolute_item`; its native origin is `[553,440]`. Keep existing native fixture data write-once. The new overhang test must feed an **unclipped** supported proposal through the real admission path: pre-calling `supported_extent` in the test setup would hide the bypass defect.

Field reuse requires the same image, region, scale, row phases and exclusion state. `invert_points` outside a monotone mesh stays NaN, never row zero or a clamped endpoint. Respect finite rule y ranges; do not create a full-height gutter from a rule's median x. Reuse existing column evidence, not a new gutter detector.

Share arrays only on exact unchanged image/ROI/scale/threshold/label contracts, passing them explicitly. Recompute decisions whose geometry or membership changes: B5 anchors/votes, M35 population, barriers and final source/ownership consumers. Do not rerun unchanged component preparation or paper estimation merely because a polygon gained blank paper. Reusing a page estimate in place of a regional estimate needs an actual contract proof; there is no calibrated universal ink mask.

The saved pixel-seeded slow `greekocr/pages/lines.py:_pool_geometry/_assign/_make_lines/_boundaries` is the explicit comparison for pooled curves and component-driven extent, not truth to copy blindly. `greekocr/` is read-only. **No Paddle polygons in `PixelPage.boxes` or `_discover`.** A's body was already discovered, so do not introduce new discovery to recover its remaining tail.

## 3. Removal and verification scope

Target the specific failed decision, not another geometry pipeline. Report policies removed in the adopted population, migrated callers, exact preparation reused and runtime additions/deletions. A new helper with the old veto still active is not simplification. Keep A and any qualified continuation subset independently reviewable; one failed end must not erase the recovered row.

### Physical targets and committed tests

Before editing, freeze original-page masks/coordinates for src37's `ἐξόδων πη-`, the χο/μέ/ἀμέ end components, A's witnessed body and its remaining `νων`. Bind them to source/input hashes. Text/component IDs locate test witnesses only; no OCR scoring or page-specific runtime decisions. Count final whole endings and whole end letters separately from path eligibility or row acceptance.

Extend `features_geometry/test_curl_consumer.py` and small committed native fixtures. Tests must run from a bare archive without `.astra`, optional fixture skips or a multi-GB capture pack. Exercise real `guided` → `correct` → final compose/export, not just candidate metadata. Required assertions/mutations:

- A remains a final recovered body. The new overhang case exercises real `protect`/`recover` and loses unsafe paper/unsupported extent without cutting its body; native/local versions agree. Bypassing the support-bound clipping must fail the returned-raster assertion. Existing absent/balanced support, verified-rule, multiple nominations and 93f8 abstention controls remain.
- A continued positive contains a complete formerly clipped end in its own **final** strip. Restoring the whole-row veto must lose it and fail. Suppressing all local obstructions must take a real neighbouring component and fail. Several separated conflicts may not become a first-to-last row-wide fallback. Own glyphs cannot be partly retained as a way of passing.
- Correct per-row phases survive batch permutation and mixed supported/unsupported rows. In-anchor support/narrowing stays unchanged. Restoring the capped tangent/domain must fail a real end assertion; preserve finite/NaN/rule controls. Empty/short domains cause neither a crash nor a newly accepted unsupported row.
- Lower-row accents competing with upper-row descenders stay with their demonstrated owners. For affected cases, use the 22 FONT census witnesses on actual final crops, not a nearest-phase assertion. Existing strict class/ownership xfails remain unless the real physical defect is fixed.
- The actual final masks conserve existing own print and acquire no new other-row component. Record inherited duplication under adjacent legacy boxes separately. Do not turn a positive completion target into a passing “still refused” test. Any optional fragment retirement needs a whole-text conservation and wrong-row counterexample.

A local retreat can legitimately leave an obstruction unknown. Passing that safety control is not a completed end. Keep mutation receipts with the production edit, expected failed physical assertion and observed result; do not count M4 as a failure of coverage.

### Frozen cohort, full development pass and cost

Reuse the unchanged 41-page manifest:
`.astra/fast_lines/out/round8/R8-CURL-03-i1/CURL03_COHORT.json`, SHA256
`377df97a07b0428b8591783f2dd093d11e0c78fb56ea4c7511aa4a7ed998a766`.
These are development-retest pages: 28 curl cases, the exact 12 geometry pages and both 8314 controls, deduplicated. Keep categories and hashes. Do not relabel a negative to accept a change.

Score **each page**, then run the established 208-page comparison on the exact retained source. All four confirmed positives matter: 8686 p5/p7, 4959 p4 and 3229 p5. Preserve the 20 flat/skew negatives and both 8314 pages export-identically. Include noisy 74cd p2, correct 93f8 p1 abstention, 9ea1 p202 narrowing and crash controls 4959 p5/c8 p36/9ea1 p202. Keep the four R rows, the 3229 p2 B row, `ἀποξήρανσίν`, Γ. Μαυρομιχάλης, pale 1be6, weak 31f40, 0ce9 #34/#36 and the useful 466/7792/c8/9ea/dbd/d323 M33 extents.

For each page report baseline versus candidate: accepted M33 rows on the same source identities; whole end letters and complete endings; recovered body/tails/νων; own/foreign/unknown components; native cuts/lost ink/duplicates/gaps; local retreat spans/reasons; source exclusions and final row count. Freeze the same baseline inside/outside and pair domains. Inspect **every changed final crop plus its neighbours**. Show the continued intermediate crop and final export so a later retirement cannot masquerade as success.

The 8686 new body's duplication is mostly its own descenders under an unchanged lower legacy box (687 of 708 inspected Otsu pixels); the remaining small residue is not all its own. Keep these defects visible. Do not resurrect a whole-row box veto, waive new wrong-row inclusion, or claim non-overlap is solved. Otsu/relative-mask counts are observations, not semantic text ownership.

Use the established authorised MacBook runner, sequentially in a quiet window, no background/concurrent benchmarks. Pair the exact final source against fea451c in both orders: ten warmed pairs, five-pair blocks, unchanged detector/reference controls and the existing 5% drift rule, with at most one replacement block and invalid samples retained. Also report cumulative affected-page increment against pre-CURL 0b620be, including A's +35/+38 ms on 8686 p5. **The existing ≤100 ms affected-page increment must hold cumulatively as well as for i3 alone.** No scope reset to hide inherited new cost. Report correction/file-to-final median, p95, maximum and pages over one second; the charter's global speed debt stays open.

Source qualification must cover the subset actually retained: hardening-only if continuation fails, combined if both qualify. A useful physical gain that fails cost remains experimental, not promoted by this prompt. No final_export activation or post-hoc relaxation.

## 4. No new pipeline or page model

Existing prototype consumers and their physical tests only. No new detector, per-line bend estimator, mesh/knot redesign, universal font/ink provider, Rust port, production work, repo reorganisation or general tessellation/reconcile repair. Do not stack another qualification layer before the same whole-row rejection. No private44 input/image access, OCR tuning, pushes, spawned workers, self-launch or background jobs. Preserve accepted source and evidence. Use the remaining slot on this named mechanism; after a falsified revision, archive the first remaining assumption rather than inventing a renamed variant.

## What counts as progress, and how CURL closes

**Preset i3 target:** src37's `ἐξόδων πη-` is complete in its own final crop; χο/μέ/ἀμέ gain whole end components, without newly acquiring another row's ink. Count complete ends on the other three positives too. Aim to move 8686 p5 from 0/30 useful M33 acceptances to a majority of those same baseline rows, but treat that as reach evidence, not a runtime rule or substitute for complete text. A newly admitted A row does not inflate that denominator.

**A retained partial gain** is at least one complete formerly clipped ending, through final compose, with preservation/controls/cost qualified. Other endings may remain open. An intermediate correct end blocked downstream is experimental physical progress; scope/tests alone are mechanism progress. The support-bound hardening is correctness progress, not a curved-end gain. Do not call diagnosis “no progress”, but do not label it recovered text. Ask the independent reviewer which previous native counterexample now passes, which blocker moved, and what is retained versus experimental across the whole cohort.

Write `docs/records/research/round8/REPORT_R8-CURL-03-i3.md` and `.astra/fast_lines/out/round8/R8-CURL-03-i3/` with source hashes, the unchanged cohort, per-case/208 ledgers, all changed native strips and whole-page/coverage views, caller/deletion map, support-bound and local-retreat tests/mutations, valid/invalid timing samples, and `ITERATION_HANDOFF.json/.md`. Add a dated i2 report/handoff addendum naming delivered fea451c, correcting the aggregate page count and distinguishing witnessed body from clipped tails. Preserve historical receipts and withdrawn sources.

For a changed frozen candidate the **coordinator alone** evaluates private44 against fea451c: **whole-page segmentation, every actual line strip, and actual-mask coverage maps for both versions on every page**, including unchanged pages and the previously recovered private body. Quantify missing/extra rows, whole ends, cuts/foreign/lost ink, duplicated coverage/gaps and paired cost with detector control. Coordinator sees the pages; planner/worker receive aggregate checks only. Repeated44 is regression evidence, not fresh validation; owner-disclosed cases become development-retest. Identical runtime needs no redundant private rerun.

**Close CURL at 3/3.** Declare complete only if the original shared-curl contract and required multi-page owner targets are actually met. Otherwise close PARTIAL, retaining A plus any independently qualified i3 subset. If no complete ending passes, keep fea451c (or safe hardening/tests) and archive the withdrawn experiment with exact first failures. No fourth CURL slot, no GEOM reopening and no default promotion to satisfy the cap.

Backlog assignment: unfinished risen ends/νων and measured field-edge residuals stay explicit CURL debt; crop-floor clipping, inherited overlap and reconcile stay geometry debt; source ambiguities remain INK-02 debt. RUST-02 follows on stable checked runtime and owns speed, not repair or porting of withdrawn B/material_band. AUDIT-02 records the outstanding witnesses, tests and quality/cost limits. FONT remains parked. Return the result/full check to Astra for the next task's first prompt; do not write or launch it yourself.

Meter is 12% as reported; no 14 October daily cap. Existing 97% launch/99% run safeguards and stop signal remain. Commit with the repository's single required trailer block. If staging fails, leave one source/hash-validated fallback under `.astra/` that **executes when invoked bare**; the runner supplies no `--execute` flag. Optional `--check` validates only. Keep the final report/commit state current; no unguarded staging retries. Final response: plain words, then `RESULT: <DONE|PARTIAL|NOT DONE> <one line>`.
