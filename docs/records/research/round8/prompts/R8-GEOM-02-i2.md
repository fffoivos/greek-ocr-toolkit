# R8-GEOM-02 iteration 2: finish residual glyphs before retrying finite domains

Resume thread `01a12688-cfa4-7952-8edb-f98e8818f1ad`, track `ff8-stack`.

Worktree: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`

Branch: `astra/ff-r8-stack`

Start from `<HEAD>` = `09b74cfe7f3f4badd9f5807877e831cc2c48a0ce` plus the coordinator's planning-docs merge. That commit adds checked tests/docs/offline evidence; its runtime is exactly accepted `54cc8f9ead2809d3c7da11f5a8e9a87334d2df24`. Keep both identities in receipts. Verify runtime identity before editing, preserve uncommitted work, and do not import parked Rust candidate 953fc4a. This is iteration **2 of at most 5**, not authorisation to consume all remaining slots regardless of the meter.

Read the full independent check at `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i1_check.md`, your REPORT_R8-GEOM-02-i1 and `.astra/fast_lines/out/round8/R8-GEOM-02-i1/` handoff, FAILURE_TRACE, rejected diffs, finite-domain tests, native images, DOMAIN_WORK and TIMING. Read the current PLAN/ROSTER/LOOP_HANDOFF and applicable AGENTS.md. Reuse these records; do not produce another general inventory.

**Continue geometry because the checker identified a concrete cause, not because the last trial was nearly accepted.** On 4959 p5, regional Paddle on request y2576–3080 finds the target at y2683–2759; request y2583–3079 finds it at y2691–2757 and misses the preceding row. The shift persists with local_h 40 or 48. After column splitting the target becomes approximately y2702–2757.6 versus y2707–2753.7. The raw localization therefore controls the new row's final extent. Both accepted and rejected images clip real glyphs; the rejected trial loses an additional 1,032 diagnostic pixels. That count is neither a glyph certificate nor an allowable-loss threshold.

First repair this residual extent policy. Only after its native and two-window tests pass, retry finite domains with a cheaper mask and a transition between complete rows. Keep the residual repair separately reviewable so that a later finite-domain failure does not erase a valid physical improvement. No Rust work this iteration.

The owner, verbatim:

> Doesnt the correction mostly invovle removing things then? and building models that can help verify the existing mechanisms

> (1) get the line segments as an input
> (2) draw the curves/skew lines and 4 lines for each line in the segment; you then give them the coordinates to seperate their identities
> (3) after you have the curves you have the 4 lines for each text-line you forget the initial line segments completely
> (4) you can draw a new segment simply by finding the middle between the bottom and top lines from neightbouring lines, and by extending left and right along the curve until you find a boundary

This task uses native row/glyph support to stop a localization box deciding which parts of its letters survive. It does not claim the four font guides or a universal body-height provider have already been measured.

## 1. Builds on the existing code

The providers named below are in `prototypes/fast_lines/shared/`; compose is in `prototypes/fast_lines/stack/pipeline.py`, and the finite-domain tests are in `prototypes/fast_lines/features_geometry/test_finite_domains.py`. Read the current implementations before migrating a caller.

The primary live chain is `stack.pipeline.compose` → `type_extended.recover` → `type_residual_recovery.recover(version=11)` → `type_residual.ink_scout`, `requests`/`contracts.merge_requests`, `field`/`type_residual.render`, regional `detector.infer`/`postprocess`, `supported_extent`, `geometry_columns.apply`, `type_barriers.protect`, `piece_support`, and `added.append(piece)`. It then passes through M33/M20 and final row ownership. Name the actual changed callers in your report.

`recover` currently retains `type_witness_points` but carries proposals as `(q, local_h)`; request-local `data['bodies']` and row chains are not a complete downstream glyph-ownership record. `snap_components` runs only for `version<2`. M20 cannot restore a never-emitted descender on a new row by comparing old and new polygons.

Reuse `type_completion.snap_components`' native component/envelope machinery and the body/mark attachment already in `geometry_field_detector.native_bands` where their inputs are compatible. **Attachment is in `native_bands`; `separate_bands` supplies neighbouring-band separation.** Do not copy either whole algorithm into another independent residual implementation. A focused extension/refactor of the existing provider to accept explicit assigned support is allowed, with its existing callers preserved or migrated.

Simply enabling `snap_components` for v11 is not a sufficient design: it selects intersected components by overlap and starts its envelope from the original covered polygon, so it can retain crop-window differences and miss wholly detached marks. `data['bodies']` is a filtered body list, not all native labels or accents. Inspect these actual limitations before using either helper. Derive one row's extent from its supported bodies and attached marks, with neighbouring rows and finite barriers constraining ownership. Remove the residual policy that treats the DB polygon as the final glyph envelope.

The conditional second chain is the existing finite-rule path: `geometry_columns.analyze` and its bilateral/native witnesses → `geometry_page_field.blocks/render/certify` → M17 `unbend/run/native_bands/separate_bands` → M18 `geometry_field_selection.apply` at compose's early and late `field_replace`. Use the rejected i1 diff as a recorded attempt, not an accepted provider. M33 `geometry_envelopes.guided/correct` and M20 `geometry_feature_correct.retention_ink/retention` remain until their useful endings/narrowings have a validated replacement.

Check physical support against native pixels and the unmodified pixel-seeded slow reference: `greekocr/pages/lines.py` `_discover`, `_pool_geometry`, `_assign`, `_make_lines`, `_boundaries`, with existing font/boundary tools as needed. The slow construction is an offline comparison with known failures, not runtime or ground truth. Preserve `greekocr/` unchanged.

## 2. Inputs match what the code expects

| Boundary | Contract to preserve or explicitly migrate |
|---|---|
| Residual localization | Keep `ink_scout` observing currently unowned ink. Requests legitimately change with the census. Do not freeze the pre-field census, request boxes, side, local_h or detector polygons to make a regression disappear. Two fixed requests are test interventions only. |
| Witness identity | `field` shifts body bboxes/centres and row paths to native coordinates; indices in `rows[].components/free` address that request's filtered body list. Carry the correct request/row/body relationship through proposal and piece processing. Do not use the loop's last `data`, match a different request's index, or collapse several supported row chains into one envelope. `type_witness_points` is evidence, not a complete label map. |
| Native completion | `snap_components` takes native gray, a native polygon, engineering height and native competing items. Any reusable labels/stats must come from the exact same image, ROI, origin, scale, threshold and preparation. Expose compatible native preparation explicitly if needed; do not invent native IDs from filtered-body positions or silently treat unlisted marks as absent. Request-edge fragments need native continuation before being called whole components. |
| M17 reuse | `native_bands` expects a crop and rows in that crop's coordinates; `separate_bands` additionally needs the matching ink/stats/labels/owner map. Native residual polygons cannot be passed as rectified rows. An extracted attachment helper must retain explicit origins, row identities and neighbouring owners. Do not copy the parked Rust bridge. |
| Piece ownership | After separator/column splitting, a witness on one side cannot authorise the other side. Complete each accepted piece from its own supported chain. Recheck existing neighbour, exclusion, rule and duplicate obligations on the completed geometry. A newly included mark is not authorised just because it is small or nearby. Keep source ancestry optional for genuine no-seed rows. |
| Field support | The existing mesh is a displacement inside a native rectangle; any finite-domain polygon/mask must retain its actual transform. NaN inverse phases stay unknown, and `certify` must skip them. A printed rule endpoint and a computational transition between rows are different observations. Do not move the measured rule or extend its physical barrier claim to fill the page. |
| After changed geometry | Recompute polygon memberships, replacement/retention decisions, B5 selections/anchors/votes, M35's eight-row population and Footprints. Reuse immutable preparation only on exact unchanged contracts. No cached row-census decisions. |
| Slow reference | Use unmodified `segment_page(gray)` / `prepare_pixels(gray)` with their rough pixel regions. **No Paddle polygons in `PixelPage.boxes`**, including padded/regrouped polygons. Slow and fast label identities are not interchangeable. |

## 3. Removal and verification scope

### First: complete residual rows from native support

Reproduce and pin the checker's two-window counterfactual on 4959 p5. The target is the row containing “ὅπως δι' ἑνὸς …”, accepted final #109 at 54cc8f9, not a current array index or a runtime page special case. Show the clipped accepted descenders as well as the trial's additional damage.

After `piece_support` identifies a valid row piece, complete its body strokes and owned detached marks, then enforce the existing neighbour/barrier/source obligations on the completed piece. Paddle remains the localization input; its roof/floor no longer determines the final text support for these recovered rows. Use the existing component and attachment tools, with a limited compatible contract extension if necessary. Whole component assignment must exclude neighbouring rows and distinguish an unknown joined object from a certified glyph. Do not grow a rectangle, union two historical outputs, weaken a retention mask, or add another percentage guard. Do not preserve old clipping merely to retain exact output.

**Primary acceptance:** both request windows produce the same completed native target polygon under a canonical vertex ordering, retaining the full descenders and breathing/accent marks, while excluding the neighbouring rows and respecting the finite column rule. Pin the body/mark ownership as well as the polygon. Equality alone fails if both results still clip. Report the naturally derived heights; the checker's 40/48 intervention isolates localization from height and must not become a hard-coded runtime value. Do not quantize away a disagreement or substitute an IoU tolerance for identical completed support.

Add a real `recover` consumer regression: exercise both crop windows, the actual support-to-piece-to-completion chain and at least one competing row. Record the two genuine regional detector results and native input hashes for replay; a model-free test may supply these recorded localizations while running real downstream code. Supplement with a compact checked-in synthetic fixture that fails on the old direct-DB-extent route and covers clipped descenders, detached marks, competing-row marks and separated pieces. Do not stub the completion/ownership stage being tested. If the real image fixture stays in local evidence, label that part as a replay, not a checked-in test. Removing/bypassing the completion call must make the relevant test fail. Run the actual two-window detector replay on the established development runner as well.

### Then: retry finite domains only with the dependency fixed

If the residual acceptance and its native controls pass, reapply the finite-domain change with these corrections:

- Use a native raster domain mask made once per field, for example with existing `cv2.fillPoly` machinery, and pass it explicitly to consumers/remapping. Remove per-remapped-pixel Shapely `intersects_xy`. Retain mask origin/grid and boundary-inclusion conventions; remap categorical support appropriately and verify fractional/sloped edges and whole glyphs. Sparse component/polygon geometry checks may remain where useful. The checker's roughly 5.1 s estimate is an attribution hypothesis, not your measured saving: measure the changed work.
- Place the computational transition at an observed inter-row corridor beyond the endpoint-touching row's complete body/mark support. Raw rule y≈995 cuts c8's first-row accents and initial Ὅ and is not an acceptable horizontal row boundary. Keep the measured rule path/y interval unchanged. Use existing row/contact and bilateral endpoint observations; do not add a new gutter or row-density model. If no supported transition exists, retain unknown support explicitly rather than inventing an empty corridor. A visually convenient global y line is not enough on skewed/curved rows.
- Preserve the spanning heading above the rule, the complete first/last body rows and the correct within-rule column split. Do not assume columns reconnect into one wide curved field beyond the rule. Outside-rule reconnection remains unknown unless actually evidenced.
- Adjudicate **all** i1 trial changes before recommending finite domains: especially 4959 p1's 122→119 items, old #117/#119–121 unmatched, and 44b5 p1/p2 unmatched rows. Determine complete text ownership by native support, not one-to-one IoU or item totals. No unreviewed row disappearance is a pass.

Upgrade `features_geometry/test_finite_domains.py` to physical invariants. Remove the assertion that outside-rule fields must always have no mesh/rows; it hard-codes the discarded implementation choice. Keep the spanning-text, finite-path and no-overlap obligations. Add **non-empty** M18 proposals exercising endpoint-crossing rejection/retention and valid within-domain replacement, plus a real `native_bands`/neighbour-separation case with glyphs touching the endpoint. Assert the relevant consumer decision was reached; an early return on no proposals is not coverage. Pin that a raw endpoint through accents fails, and that the accepted native mask includes the required support without crossing the rule. Remove strict xfail markers only for defects the retained runtime actually fixes; keep the inherited faint-front xfail and NaN consumer tests intact. Bind any mutation receipt to the exact committed test/source, not a different trial test file.

The owner's continuation requirement still stands, verbatim:

> so if we know the bend and we have the text-lines' lines we can just follow them to the end of the page in a way
> that does not impose on the other liens

This iteration repairs its support/extent prerequisite. It does not require an M33 migration on pages where no valid shared field exists, or introduce new four-guide claims.

### Native controls and meaningful accounting

Besides 4959 p5 and c8, preserve all six rejected M33 controls: 466 p277 ending, 7792 p138 punctuation, c8 tick, and neighbour exclusions on 9ea p202, dbd p359 and d323 p138. Preserve “ἀποξήρανσίν”, 8686 p5 rows 40/41 and p7 “ἀμπέλων”/row 40. Row 5 on p5 is still unmatched; distinguish absent, present and clipped. Include affected residual recoveries, short numbers, large initials, faint text and nearby accents. Retain 3229/4959 historical recoveries, weak 31f40, pale 1be6 p215, 0ce9 #34/#36 and the current strict faint-front failure as explicit controls/debt. Source certainty is not inferred from newly completed geometry.

Record separately the v11 raw-DB-extent policy replaced, the finite-rule full-height policy removed or still present, actual callers migrated and lines added/deleted. The previous counts 6/9/9/7 and cumulative runtime −475 against d5dc3e2 are inherited. A completion helper with no live consumer is not a deletion; a residual-only repair is useful physical progress even if all seven bend authorities remain.

## 4. No new pipeline or page model

Keep the default compose route. No global glyph/ownership/page-model rebuild, new universal ink threshold, font-height fitter, second gutter detector, Rust port, new cache framework or production changes. Do not freeze requests/census, retain the failed full-height interpretation under a new name, or use the older output as a runtime fallback. This iteration changes the identified causal input contract, which justifies a new finite-domain test; it is not another guarded version of the same failed assumption.

Keep M06 propagation deleted. M55, the two DN floors and M35's population-dependent source classification remain ink debt. Do not import rejected frame/noise providers, waive unresolved specks or reclassify faint rows to make geometry pass. Source checks affected by completed polygons must be rerun; whole-glyph completion does not certify front versus deeper-leaf print. The parked Rust code stays unchanged.

## Deliverables, acceptance and next handoff

1. **An independently reviewable residual completion change**, with exact two-window detector/recovery replay, matching native output and body/mark evidence, real caller/mutation regression tests, and before/after crops including previously clipped accepted support. Then a separately attributable finite-domain retry if the prerequisite passes. If finite domains regress, withdraw that part and keep the residual repair if independently valid. If neither is safe, retain 09b74cf with its 54cc8f9 runtime and report the first failing assumption. Do not erase valid progress by restoring everything automatically.
2. **Source-bound native review and removal accounting.** Use existing evidence tools; update FEATURE_OWNERSHIP/CONSOLIDATION_DELTA, NO_SEED_ROWS and original owner ledgers without dropping any fields. Review the 23 pilots and every changed crop/exclusion/ownership case. Account for the 4959 p1 and 44b5 disappearances, not only #109. Preserve 104 comments/256 marks and identify inherited review separately from fresh decisions.
3. **Meaningful software and integration validation.** Run the relevant completion/residual/domain/retention tests and full prototype suite. Once the retained runtime is coherent, run a fresh source-bound 208-page pass. If restored exactly, rebind checked evidence and say no new full pass was run. The coordinator alone runs the private 44. Whole-text preservation, including improvements to the old clipping, is required; unchanged polygon totals are not the gate.
4. **Cost with causal attribution.** Time baseline versus residual-only work on the two-window and affected controls. If finite domains survive, distinguish their incremental mask/field cost from residual completion and inference. Use paired uninstrumented runs in both orders on the existing 80 controls (or an explicitly justified updated affected/quiet/slow union), plus final full-pass median/p95/max and slow-page names. Record mask builds/sampled pixels, component preparation, regional calls/tensor work and downstream stages; charge all work. Avoid repeating a full pass for each transient variant. Use this MacBook's established authorised runner, same inputs/model/thread settings, no concurrent benchmark. The rejected +4.63/+4.14 s is not a baseline improvement to claim; accepted runtime clocks remain 199.421/1287.272/2007.555 ms with 22/208 over 1 s. Confirm that per-pixel geometry cost was actually removed before attributing savings to masks. Keep the 0ce9 debt visible.
5. **Report and structured handoff:** `docs/records/research/round8/REPORT_R8-GEOM-02-i2.md` and `.astra/fast_lines/out/round8/R8-GEOM-02-i2/`, including ITERATION_HANDOFF JSON/Markdown, source/input/model/settings identities, test and native verdicts, candidate versus recommended best head, unresolved assumptions and measured time/meter. Identify stable computational contracts for the next Rust task without declaring the rejected domain contract ready. Append a dated note to i1's report/handoff naming runner commit 09b74cf, ACCEPT WITH NOTES, unchanged runtime and no new private44 run; correct the unresolved-cause wording with the checker's counterfactual while preserving the original record.

The coordinator checks the primary two-window result, actual old-policy displacement, complete native glyph support and neighbour exclusions, nontrivial consumer tests, all changed-row adjudications and measured cost. Residual-only acceptance leaves G3 PARTIAL. Finite-domain acceptance also leaves G3 PARTIAL while its other row/curl/ownership obligations remain. A third geometry prompt is not automatic: after this check the planner weighs a concrete remaining repair against moving to the stable Rust task and the live budget.

## Authorisation and resource boundary

The owner's latest direct instruction is:

> ok re arrange your plan as you see fit, and I ll leave you to the autoamtic loops workings next

The coordinator additionally relays “ok keep going”. No routine owner confirmation is needed. Geometry's maximum remains five, with i1 already consumed. The reported meter is **88%**, leaving roughly seven points before the planned closing reserve begins at 95%; the runner refuses launches at **97%**. Recent workers cost about 1–2 points, with planner/review overhead also charged. Expect this iteration, then a substantive Rust iteration and closing audit; another geometry iteration is conditional, and ink is not a promised launch on this meter. No arbitrary clock cap, hidden extra iteration or automatic rollover. Preserve a coherent handoff if the actual resource limit intervenes.

Only the 208 development pages. Never locate, open, run or request the private 44 or their outputs. No PDF-text truth, orientation work, background jobs, additional agents, pushes or production edits. Anemi material stays internal. Modify task prototypes/tests/docs/evidence only in this worktree; leave `greekocr/` and other worktrees unchanged. Use the established Python environment and source-bound runner.

Commit scoped work on `astra/ff-r8-stack`; if staging is blocked, leave `.astra/commit-F8-R8-GEOM-02-i2.sh` with the validated source-bound fallback. Required trailers:

    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01X3VU3zMmUxSHRDvYfQMczm

Finish in plain words, then `RESULT: DONE|PARTIAL|NOT DONE` naming R8-GEOM-02-i2, commit/fallback, retained residual/domain changes, G3 status and best-head recommendation. Do not write or launch a successor prompt.
