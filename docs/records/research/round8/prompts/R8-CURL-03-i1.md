# R8-CURL-03 iteration 1 — shared edge curl and text beyond detector boxes

Fresh thread (`-`), **gpt-6.1-sol / high**, track `ff8-stack`. Worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Start `<HEAD>`: coordinator fills the full hash of **0b620be070cf2a1f16e84a41089e9058d391cd4d plus FP8ag planning docs**. Do not reset to ff-merged or merge the Rust pilot. CURL has three iterations total; only this first iteration is issued. No self-launch or assumed-success later prompt.

Read `docs/records/research/round8/SOL_WORKER_HANDOFF.md`, then the **full** independent check:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-04-i3_check.md`.
Read its source-bound report `docs/records/research/round8/REPORT_R8-GEOM-04-i3.md` and the task-specific inputs below. Do not consume every historical chat before starting.

## Owner direction and this iteration's target

The owner told the planner directly:

> ok lets just normally continue with the rest of the tasks in the plan

GEOM-04 is CLOSED PARTIAL at3/3; **this is CURL i1, not geometry i4**. Keep `Stack(final_export=False)` and the accepted R/B gains. The experimental whole-page export is not an entry requirement or an accepted algorithm to extend.

The owner's original curvature contract, verbatim (also in `FL/round8/OWNER_IDEAS.md`):

> right but now the whole page bend should be global we dont need to check individual lines right?

> so if we know the bend and we have the text-lines' lines we can just follow them to the end of the page in a way
> that does not impose on the other liens

Later clarification, verbatim:

> if we can build a model of the blank page, and its geometry in space,
>
> then we could be able to simulate how we would be seeing parallel lines drawn on that page any way we like.
>
> If we do this, then simply knowing the line passing through line of text, would predict how it would bend on the page

> Right our idea is mostly to target the edge of the page, where actual curvature presents due to book structure, and have a heuristic that actually detects it, if any

The latest concrete fault:

> so in the site you have published I see that 8686 p5 doesnt deal with curvature well

Standing methodology and sampling:

> But the whole point of this generation of our model was so that we odnt have to have duplicate checks

> Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample

**I1 target:** make the existing shared geometry represent and deliver a supported curved ending outside the initial box, through one existing live caller, beginning with8686p5 and checking the other three established curled pages. A global/page-column field predicts the family of paths; each row supplies its position and verified ink extent, not its own competing bend model. Distinguish curvature detection, continuation, missing-row discovery, final crop shape and cost. This iteration does not have to complete the entire three-slot CURL task or general segmentation.

The i3 check is positive about reach: literal experimental export reduced doubled pixels~71/70/80% on12/208/coordinator44. Its exceptions and cost remain unqualified. Inside accepted boxes it works much better than outside: only5.2% of outside text-sized ink reached;8686p5 only1.4% of~78kpx,53% at risen ends. Those size-derived counts are observations, not front-text labels. The fixed export representation, outside admission and wholly missing rows are separate first-failure candidates. A new polynomial alone does not address them.

## 1. Builds on the existing code

Trace these **actual default callers** on the four positives before selecting the single replacement. Read their contracts, not just their names:

- `stack/pipeline.py:compose`: `edge_scout`; `geometry_cuts`; `field_proposals` alias for `geometry_field_detector.run`; `field_replace` alias for `geometry_field_selection.apply`; `geometry_run`; `type_extended.recover`; `smooth_envelopes` alias for `geometry_envelopes.correct`; subsequent source, split, reconcile and footprint decisions.
- `shared/geometry_page_field.py:blocks/render/certify/invert_points`: M15 shared displacement mesh, component observations, finite inverse domain and row phases. Existing NaN-phase tests stay. A phase or component density is not a semantic baseline or a front-ink certificate.
- `shared/geometry_field_detector.py:displacement/unbend/run/native_bands/separate_bands`: M17's shared rectification and mapping back. `shared/geometry_field_selection.py:apply` is M18 selection. Record whether a good curved proposal is lost here or later. Do not build another regional detector.
- `shared/geometry_envelopes.py:guided/correct/owned_retention`: M33 currently constructs a capped straight tangent beyond observed map support, then contacts and envelopes. `compose` calls it as `smooth_envelopes`; it skips `page_field` rows. M20's `geometry_feature_correct.retention_ink` is still needed. On a field-owned row, editing M33 cannot fix the observed failure: follow M17/M18 instead.
- `shared/geometry_contacts.py:prepare/trace/render_contacts` and `geometry_feature_paths.bands`: existing native observations and finite observed map paths. Inspect sample/coordinate contracts; reuse the observations, not an unbounded independent walk for each line.
- For the missing-row sub-scope: `type_extended.recover` → `type_residual_recovery.recover/field/requests/piece_support`, plus existing M17 proposals/M18 admission. The residual route must be allowed to report ink with no original seed; an empty seed list is not evidence of blank paper.

**Explicit slow comparison:** read the original pixel-seeded `greekocr/pages/lines.py:segment_page` → `_discover/_pool_geometry/_assign/_make_lines/_boundaries`, and `font.py:fit_guides` where relevant. `_pool_geometry` pools row contacts; `_assign` considers page components beyond seed boxes; `_make_lines` follows their extent and barriers. First use the saved unmodified R8-01 slow renders in `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/slow/`. They already recover many8686,3229,4959 endings. Keep native pixels as the authority: the slow detector has known local sliver/initial/offset errors. No copying its complete pipeline or treating it as ground truth.

Read `FAST_LINES_ROUND7_T2C_BEND.md` for the failed M37 experiment before borrowing `geometry_bend.scout/offset/phase` or `geometry_bend_edits`. Its fixed bend nomination, independent row placement, source thresholds and transactional rebuild were not accepted. `Stack(bend=True)` replaces more than one default stage; do not silently enable it. It is historical evidence, not a spare working provider.

**First action after freezing inputs:** save the four positive pages' existing paths, shared field, candidate mapped bands and final native crops in one caller trace. On8686 separate (a) already detected main row with missing end; (b) end-word boxes belonging to the same observed row; (c) a genuinely unseeded row. Locate the first loss, and compare that stage to the saved slow construction. Then make one real implementation attempt in that identified existing authority. Prefer reuse of the current shared mesh through the firing caller over creating a second bend representation.

## 2. Inputs match what that code expects

Keep the full native grayscale page, native coordinates, original Paddle map/items and source IDs, finite reliable row observations, existing column/rule paths, accepted/excluded components, and explicit scale/origin metadata. The module operates after initial detection, not on tight row crops alone. Do not wait for universal font classification or perfect segmentation.

- The slow reference takes `segment_page(native_page)` with its own `prepare_pixels`/rough regions. **Never put Paddle line polygons or their boxes into `PixelPage.boxes` or `_discover`**. That already failed: cropped components were excluded and seedless rows vanished. Paddle items are inputs to the existing *fast* field/envelope callers only.
- Native → reduced sample → local/rectified → native mappings must include scale, offset and pixel-centre conventions. Whole native support and original-page masks must survive the round trip; a remapped rectangle is not a physical certificate. No clamping an unknown field phase to row0.
- A shared displacement may vary smoothly with page position; it must remain one coherent, non-crossing page/column correspondence with finite supported domain. Render virtual parallel paths **between** measured rows, not just lines fitted over existing ink. Show curl onset and displacement relative to the interior skew. Return evidenced curl, evidenced no-curl or unknown; absence of observations is not no-curl. A full3D surface reconstruction is not required.
- For steep ends use the existing field mapping/local tangent-normal coordinates where needed to measure support and construct the band, mapping it back once. Do not merely raise the `geometry_bands` slope limit, bend every straight line globally, or add independent per-row curves. First demonstrate which representation actually fails in the default route. An existing y-displacement can be sufficient; a new local frame is justified only by the observed mapping/crop failure.
- Respect finite `column_evidence` rule paths and y ranges. `blocks` currently extends median-x cuts to full height; that known bug is not a new column provider. Restrict a CURL domain to observed valid support or repair only its demonstrated contract if essential for the target. Do not reopen the withdrawn general finite-domain rebuild or invent gutters on pages without evidence.
- Share prepared arrays only with identical image/ROI/scale/kernel/threshold and observation contract. Passing a prepared result explicitly is preferred to a cache. Changing row membership requires fresh B5 anchors/votes, M35 population and relevant motifs/rules; identical native photometry need not be computed twice if its contract is truly unchanged. Do not pass a regional-paper result as a page-paper result by assertion.
- Newly reached components are not front text just because they are near a predicted path. Use existing native source/exclusion observations, assign a complete component only with a unique physical row witness, and keep disputed cases local/unknown. Accents, large initials, faint front print and touching two-row components require the existing physical controls. Do not add a universal ink threshold, noise estimator or nearest-box mark rule.

## 3. Removal and verification scope

**Replace one decision; do not stack a corrective pass.** For non-field rows with supported shared bend, the intended replacement is M33's capped tangent/independent continuation in `guided`, consumed by `correct`. For field-owned rows, use the actual first loss found in M17's mapping or M18's selection; M33 is not their consumer. Choose the firing path from the saved trace, name it before editing, and report why it was chosen. Do not build both replacements speculatively. The accepted route must use one authority for the adopted population; delete the displaced calculation there and retain the old route only for its separate unsupported population. Report actual migrated callers, decisions removed, repeated preparation removed and runtime lines added/deleted; helpers and observations alone are not consolidation.

Start with a supported8686 ending, then apply the same physical construction to the full frozen positives/negatives. Do not use page IDs, benchmark membership or manual end labels in runtime. Existing same-row end fragments may be joined only when shared phase and native support prove the same identity; do not broadly change `reconcile` priority or give every mixed box a new row. Use the existing crop/envelope/shared-separator construction on mapped support, preserving complete letters and neighbours. Keep `geometry_bands.tessellate` experimental and `final_export=False`. General legacy-interval repairs, heading tabs, a73d item54 and whole-page tiling are not CURL work.

The reviewer's windowed outside tracker is a **falsified approach**: piecewise fitting increased overlap, unconstrained continuation took7,940noise components on74cd, and experimental masks then undid steep ends. Do not retry it with renamed bins or looser guards. The independent R7 bend family and R8 from-scratch row model are not accepted shortcuts either. Use the successful slow contact/pooled geometry to understand and test the existing fast correspondence instead.

**8686 missing row — explicit separate deliverable.** Trace the row identified by the checker as “τρου γεωργικότητος … συλλεγομένων” from native support through the existing default field/residual proposals to its first dropped/mixed/admission decision. The quoted text identifies the visual witness, not OCR ground truth. Bind the exact native rectangle/components and determine whether it is the earlier p5 row5 witness; do not assume identities from numbering. Record proposal existence, row identity, source/column evidence and final output. If the same corrected coordinate/support contract directly repairs its existing consumer, test and report that separately. Otherwise leave this sub-scope open with its first cause and a real failing consumer fixture; do not invent a row from pitch or expand i1 into a new discovery model. CURL's remaining slots can address that bounded dependency after review; unresolved at3 carries as explicit discovery debt toAUDIT.

### Frozen wider sample and measurements

Before changes, create `CURL03_COHORT.json` with input/export/evidence SHA256, full page IDs, caller/category and exposure status. Fixed membership:

1. **All28 entries** of `d_curl` in `FL/cases/cases.json`: all4 confirmed positives, all4 unconfirmed candidates, all14 flat and all6 skewed negatives. Preserve those labels; a candidate is not a confirmed curl. Positives are `s2-3229200bf47ca465a42d-p00005`, `s2-49598b2e848ab1f0ee1e-p00004`, `s2-86865c33eef5932c013b-p00005`, `s2-86865c33eef5932c013b-p00007`.
2. The exact12 pages in `prompts/R8-GEOM-04-i3.md`, bound to saved `GEOM04_I2_COHORT.json`, with no favourable substitutions. This includes noisy74cdp2, retained4959p5 and3229p2, columns and large headings.
3. Explicit table/leader controls `s2-831443dc5e6f1ccfbaf5-p00020` and `s2-831443dc5e6f1ccfbaf5-p00039`; retain the existing geometry42/FONT22/owner marks and weak-print controls when their inputs are affected.

`FL` = `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines`. Deduplicate exact page IDs only, keeping all category labels. All named pages are development-retest; do not call them unused validation. After source freeze run all208, with the remaining development pages reported separately. No private44 access or replacement cohort.

Report per page, not only a pooled success count:

- Shared bend/no-curl/unknown, onset, reliable spans and native residuals; observed versus predicted paths, non-crossing and finite-domain checks. Straight/skewed controls distinguish skew from book-edge bend.
- Baseline and candidate from the **same initial detections**, final native masks/strips and full-page overlays; text recovered beyond the original mask, clipped components, neighbour/wrong-row ink, duplicates, gaps and source exclusions. Freeze baseline inside/outside masks and gap domains so the candidate cannot change its denominator. Relative ink and Otsu are separate diagnostics; inspect actual letters and marks.
- Missing row, separate end boxes and continued row ends as distinct outcomes. Score every owner curl comment, the positive pages and unchanged negatives; no “fixed” from a path overlay alone.
- Smooth crop shape separately from ownership. Curves cannot borrow someone else's accent. Preserve4959p5's four R rows and3229p2's retained B row, `ἀποξήρανσίν` (8686p5#19), Γ. Μαυρομιχάλης, pale1be6, weak31f40,0ce9#34/#36 and the strict faint-front xfail. Preserve M33's existing useful endings/narrowings on466,7792,c8,9ea,dbd,d323.

### Tests and cost

Commit small native fixtures and real-caller tests; no `.astra` dependency, skip-if-missing replacement or multi-GB capture requirement. Pin the selected shared-field→continuation→actual final crop chain. Mutations must make the physical assertions fail: restoring the old clamped/capped continuation; discarding outside native support; breaking the mapping/phase domain; and crossing the adjacent row. Include no-curl/skew, finite rule and noisy74cd cases. If the22FONT marks are newly considered, inspect the **final exports**, not just proposal pieces; preserve known ambiguous marks and real crossings. Keep existing fixtures write-once.

Use the established authorised MacBook development runner, sequentially, with the coordinator's quiet timing window; no background jobs or parallel benchmark. A frozen candidate requires fresh208 comparison plus relevant tests before default adoption is proposed. Review every changed final crop and all lost ink. Run paired orders with unchanged reference/detector control and existing5% drift rule, at most one replacement block, all samples retained. Report median/p95/max/pages>1s, per-positive-page and clean-negative cost, plus the affected stage counts. Keep the inherited≤100ms incremental-page criterion and charter negligible-clean/under1s total corrections targets visible; existing baseline breaches are debt, not a licence to add another full-page pass. Do not substitute the reviewer's300–500ms estimate or an invalid timing block for a passed gate. If output improves but cost is unqualified, retain source-bound experimental evidence and the checked default, with separate physical/runtime verdicts.

## 4. No new pipeline or page model

Work only in the current fast prototype and its tests/evidence. `greekocr/` stays read-only. No fresh detector, new page ownership model, second font pipeline, new source calibration, additional independent bend voter, Rust/production work or broad repo reorganisation. The shared page/column geometry is the existing authority being repaired and consumed; a small local-coordinate adapter is not permission to rebuild everything. Do not restore deleted M06 propagation or silently activate M37. No private pages, OCR-based tuning, page selectors, background tasks, pushes or self-launched workers.

One failed assumption gets its native counterexample and a bounded revision, not a third renamed variant with guards. Preserve good checked changes and report a partial result when a separate dependency blocks adoption. Do not spend the iteration just producing a wider diagnosis if the trace identifies a testable existing consumer; make the concrete attempt and retain/reject it on native output.

## What counts as progress, deliverables and next check

**Retained physical progress:** at least one previously clipped curved end becomes complete in its correct final row through the replaced existing consumer, with neighbouring text/source preserved and the same algorithm assessed on every frozen positive and negative. State the exact rows/books and limitation; one page is not general curl completion.

**Valid partial progress:** a tested shared mapping/consumer repair removes a previously demonstrated failure, or a frozen native experiment reaches a complete final end but is blocked by an independently measured downstream/cost dependency. Keep the concrete source/fixture and first failure so i2 builds on it. A better-looking field with unchanged clipped final text is measurement/diagnostic progress only; a source trace or test count alone is not physical gain. The missing-row trace is useful dependency evidence, not recovered text.

Deliver `docs/records/research/round8/REPORT_R8-CURL-03-i1.md` and evidence `.astra/fast_lines/out/round8/R8-CURL-03-i1/`: cohort hashes; default caller/deletion map; common-field/virtual-parallel-line renderings; slow-reference/native comparison; inside/outside and per-case final-output ledger; separate missing-row trace; committed fixture/mutation receipts; fresh208/source-bound diff and paired timings; compact `ITERATION_HANDOFF.json/.md`. Record accepted versus withdrawn runtime and update stale worker-commit notes with a dated addendum naming0b620be. Keep original evidence.

Coordinator check: ask what earlier failure now passes, what was actually deleted/replaced, which native gain survives final export, whether the wider sample supports it, and whether the remaining blocker narrowed. The coordinator alone renders **whole-page segmentation, every actual line strip and actual-mask coverage maps for baseline and frozen candidate on all44 private pages**, including unchanged pages and row ends, plus per-page text/overlap/gap/cost. Distinguish default from any diagnostic experiment; the repeatedly used44 is regression evidence, not untouched validation. Any owner-disclosed page is development-retest. Workers/planner never see those inputs or images.

Return result and full check to Astra for i2; do not prewrite it. At CURL's third slot close complete/partial honestly and proceed toRUST on its best checked compatible head. Meter10% reported, no14October daily cap; weekly97%launch/99%run guard and stop signal remain. Commit with the repository's required single trailer block; if protected staging fails, leave a source/hash-bound fallback under `.astra/`, no repeated unguarded git attempts. Final: plain words, then `RESULT: <DONE|PARTIAL|NOT DONE> <one line>`.
