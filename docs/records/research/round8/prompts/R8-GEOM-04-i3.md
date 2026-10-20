# R8-GEOM-04 i3 — construct the page first, repair exceptions locally

Resume thread `01a136ac-ed6b-7773-a1e6-ff484d531820`, `gpt-6.1-sol`, effort `high`, track `ff8-stack`. Worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Start at **<HEAD>**, the coordinator's documentation merge onto checked **3b7c57db2ecc8fb1c728b3bdf08dddf9d07ea080**. Confirm source ancestry and scoped tree state. This is one additional authorised iteration, i3; no i4 or other task is launched here.

Read the compact `docs/records/research/round8/SOL_WORKER_HANDOFF.md`, your i2 report and the **full** independent check:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-04-i2_check.md`.

Read the checker's actual diagnostic code and results in:
`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/f1db7209-77e0-476f-b75b-886a69c81def/scratchpad/check_geom04_i2/`:
`tools/literal.py`, `tools/litdiag.py`, `literal12.json`, `litdiag.json`, and the named native overlays/strips. Hash these inputs; they are an experimental reference, not installed providers or physical ground truth. If scratch has disappeared, ask the coordinator to restore this exact saved evidence; do not reinvent an unseen prototype.

Owner, verbatim:

> (1) create a smooth line around the selected letters, by broading a little the boundary around the central line of the text
>
> (2) make sure there is no overlap with other lines by finding the middle line

> Our goal now is smooth clear lines for segmentation, without overlap. If the lines are tight as normal on the page, the segments should then tesselate the plane

> Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample

> I want to see whole page segmentation, and teh lines it produces.

**The plan changes, not just a threshold.** I2's committed tests, final caller, explicit ink preparation and half-open masks are useful. Its default output remains i1. The ownership gate refuses roughly 94% of items and the chain audit spreads each refusal. The literal construction removes about 95% of overlap on the same 12 pages before exception repairs. Build that construction in the existing slot, measure it first, then fix the named local faults. Do not add another qualification layer before measuring it. My i2 instruction to fall back across connected groups is superseded.

## 1. Builds on the existing code

Keep `Stack(final_export=True)` → `stack.pipeline.compose(use_final_export=True)` → `geometry_bands.tessellate` after `frame_exclude`, before final identity/export. Preserve `final_export=False` as the checked default while this new candidate is qualified. Replace the *experimental* implementation in this slot; do not retain both i2's qualification engine and a rival literal engine with a choosing vote. The old source remains recoverable from Git.

Reuse `stack_ownership.prepare`, the exact ephemeral `prepared` observation, `geometry.robust_fit`, `geometry_bands._slope_majorant`, existing min/max/Gaussian filtering, `band_polygon`, `polygon_mask`, `crop_mask`, finite column/rule evidence and final footprint plumbing. `geometry_final_support.observe` should prepare measurements efficiently, not veto rows before construction. Delete its every-anchor-bbox fit requirement and the `unknown` → `fail.setdefault` row rejection in `tessellate`. Remove the whole-chain transaction/rejection policy and the second all-groups rollback. Keep physical audits, with local application described below.

Adapt the checker's literal steps to the real caller:

1. **Centre path.** From each incoming item's own masked ink, bin x and fit median y robustly. Use the existing robust linear/quadratic fit and finite support; quadratic is a local description where the observed line bends, not a new common page-curl detector. Outliers affect the fit through residuals, not an all-bodies-inside veto. Existing reliable R/B paths may seed this same representation. No new requirement that every component have a body/mark class first.
2. **Whole-component owner.** Assign each ordinary observed CC8 component to the nearest eligible finite centre path. Candidates include touching items and nearby supported paths, so letters outside a tight incoming box are not automatically excluded. This is nearest *row path*, not the falsified nearest-body-box attachment. Measure the FONT controls before accepting it. A contested pixel is an assignment question or a local exception, not grounds to refuse a row.
3. **Neighbours and middle line.** Determine adjacent rows at each x within existing column domains. Begin with their centre-path midpoint. Smooth that one separator and bend it only where whole assigned components require clearance; both rows use precisely the same edge. Loose rows retain ordinary padding capped by the midpoint; do not tile paragraph whitespace. Same-row duplicates are not vertical neighbours.
4. **Outer edges and ends.** Ordinary paper padding around the row, bounded by neighbouring support and finite columns/rules. Use the one-sided clearance already proved. The desired outline follows the line as a whole, not each letter's top/bottom. Draw the centre path, unconstrained midpoint and actual separator together so unnecessary glyph-scale waves are visible. Keep the retained R letters and clean B row; exact old vertices are not the target.
5. **Actual raster.** Keep the half-open convention through final polygons, `crop_mask` and every OCR strip. Shared mathematical edges are fine; pixels belong once. Handle local patches with the existing concavity-capable raster, without filling gaps or holes into text.

First reproduce the **unrepaired literal** table from fixed input items inside the real experimental final caller. Save that source and output before repairs. Do this before fitting any additional exception thresholds or installing new eligibility checks. The diagnostic constants (including .3 h padding, 1.8 line-height tight pitch, .5 same-row nomination and existing smoothing radii) are initial parameters to freeze and test, not universal page laws. Distinguish component-height proxy `h` from mask line-height `L`; do not silently substitute one for the other. No page/book/item selectors.

Read-only slow reference: `greekocr/pages/lines.py:_boundaries` for a common midpoint constrained by whole components, `_assign/_make_lines` for path ownership and extent. Use saved pixel-seeded evidence only as needed. No Paddle polygons in `PixelPage.boxes`, no full slow runtime, no new discovery stage.

## 2. Inputs match what that code expects

### Observations, ownership and validation

Keep the existing final items and all their origins, current exclusions, native grayscale image, exact ROI/scale/threshold and finite path coordinates. Label the reconciler's relative `.08` ink once and pass arrays explicitly. R's absolute 20.4 DN and B's Gaussian/Otsu observations remain distinct namespaces. Retain their original-pixel witnesses for tests; do not treat matching integer labels as matching components. Current crop coverage often duplicates another row; it is not immutable physical ownership.

Use vectorised/grouped claim and component calculations. Replace the Python per-component/per-row decision-dictionary work on the hot path; bind detailed diagnostic receipts only when requested. Do not add a persistent cache or repeat native preparation per row. Ensure `final_export=False` does not build new support/labels or pay experimental ownership cost; verify this, rather than infer cost neutrality from equal polygons.

**Separate accepted content from its export background.** If a row's owned native components and content provenance are unchanged, do not rerun motif/source/frame decisions merely because its paper envelope or polygon hash changed. Carry their content receipts into the final export; the footprint/raster identity still changes. This replaces i2's unconditional `refresh_export` cascade (`candidate_motif`, `rule_contacts`, B5/M35 and frame on every changed crop). It is not permission to claim arbitrary changed-ROI computations are numerically identical. Make the content decision's input support explicit and test its reuse; do not accidentally feed the new background ROI back as new content evidence.

When real content membership changes—such as assigning a formerly duplicated glyph, recovering an outside-box mark, entering a removed footprint, or retiring a duplicate—trace the existing affected source decision and refresh only that dependency with compatible content inputs. Reuse measurements where identical; if a true calibration pool changes, rebuild that pool once, not per crop. Existing exclusions are barriers; do not restore ghosts/rules/ornaments. A validation change is reported and handled only on its affected content/interval; it must not become a generic batch veto. Keep old content/source evidence for a locally unresolved interval. No new source/noise/font model.

### Decisions on the local exceptions

Implement and measure these **after** the literal first table. Every exception records its native witness, affected items, x-interval and consequence. The neighbourhood needed to splice a smooth seam may extend the interval by the filter's actual support; it must not spread through a row chain. Both sides of a shared edge use the same local patch. A failed patch reuses the legacy masks only there; surviving seams elsewhere remain. Audit seams at patch joins and keep legacy overlap in the totals.

| Exception | Action in i3 |
|---|---|
| Same-row duplicates / boxes containing two rows | Use existing `stack_ownership.reconcile/_pass` overlap/provenance evidence and the observed paths to distinguish duplicated same-row support from real adjacent rows. Reuse a single row identity for exact duplicates only when every genuine component remains in its correct surviving row. Do not globally prefer the smaller/larger crop. Where a mixed item cannot yet be resolved, restore only its conflicting x-interval, with all other intervals constructed. No new row detector. Inspect 44b5 ΦΙΛΗΜΩΝ / “τριῶν μηνῶν”, 4959 “θα τοιοῦτοι”, 3229 “γίαν τῶν μαθητῶν”, and the separate a73d p301 item 54 witness. |
| Gutter, rule and line ends | Use existing accepted column/rule paths over their actual y spans. Keep rule components out of ordinary row ownership and preserve their legacy/exclusion treatment. Do not use a full-height median-x cut or invent a gutter. Extend endpoint candidates to whole observed letters within the supported column, not just the original box: pin 4959 initial δ and 3229 initial Σ. If a span crosses an unresolved domain, keep that local span legacy. |
| Touching descender/ascender components | Try whole-component assignment to the nearer row path and bend the seam around it. A connected component may actually contain letters from two rows: do not call moving both to one row correct merely because the component stays whole. If whole, correct-row preservation and the smooth seam are incompatible, preserve that interlock interval and name the fused/touching dependency. Never average crossing constraints into a seam that cuts the component, as `literal.py` currently does when low>high. No tiny-pixel waiver. |
| Tables, figures, leaders and oversized rule/blob components | Keep existing semantic treatment and legacy ownership; do not drop the prototype's oversized unassigned components (the 246 lost Otsu pixels). Where a component has multiple legacy claims or no physical text owner, preserve/report that local non-text support rather than force a text owner. No entire ordinary page excluded because it has a figure, rule or large initial. Large initials are text controls, not automatic blobs. |
| Detached marks with nearly equal path distance | Test all 22 FONT cases and the 11 reviewed correct proposals. Start with nearest row path; for a distance margin below one native pixel, preserve an established old owner, or legacy claims locally if no unique old owner exists. The 1-pixel margin is the checker's starting hypothesis, not proof of attribution. If the census falsifies it—including a high-margin wrong owner—freeze the exact counterexample and restrict only that mark's local interval; do not refuse the row or stack a new guard. The true lower-row marks must not become upper-row marks. Keep the speck and real-crossing negatives. |

The 4959 one-pixel component 9114 cannot sink 103/22 or 109/107/105. Row 23's component 8106, wholly in 25, cannot sink that column either. Count their final local treatment explicitly. Unknown paper/source pixels stay visible in the audit, without becoming page eligibility rules.

## 3. Removal and verification scope

Replace the failed policies, not just add `literal_mode`: the every-anchor fit test, any-contested-component row veto, atomic-chain rollback and unchanged-content validation cascade. Keep one final experimental algorithm. Show old decision → replacement caller → deletion, plus native and timing evidence. Preserve useful observation transport, committed tests and raster code.

**Freeze and reuse the exact 12 pages**, no favourable substitution. I2 already exposed all twelve; they are development-retest, not unseen validation:

1. `s2-49598b2e848ab1f0ee1e-p00005`
2. `s2-3229200bf47ca465a42d-p00002`
3. `s2-44b5cf9e0d680b361091-p00001`
4. `an-a73d22211479-p000047`
5. `s2-86865c33eef5932c013b-p00005`
6. `an-7792a3301892-p000059`
7. `s2-c3ccfa3cea1347d7ad54-p00002`
8. `an-1ba3fdb1436b-p000009`
9. `an-9ea1564fcf4f-p000013`
10. `s2-74cdb23a34ca4a6cd01e-p00002`
11. `an-db97e3dd59ca-p000042`
12. `an-466cffad2cba-p000206`

Bind `GEOM04_I2_COHORT.json`, accepted input exports and native pixels to hashes. Preserve the unchanged GEOM-03 42 cases, FONT 22, all 133 owner marks/nine missing pages and existing negative/layout/table/weak-print controls. The five retained R/B rows must remain whole and clean; they are regression witnesses, not the performance denominator.

**First measure per page, before repair and after it:** doubled pixels, doubled ink, pair-domain gaps, cut components, foreign-row ink and lost ink, plus covered area, item/row count and local-exception extent. Compare accepted 9e8a196 (= current default), unchanged i2 experiment, unrepaired literal and repaired i3. The checker's twelve-page reference totals are:

| Metric | Accepted | Literal diagnostic |
|---|---:|---:|
| Doubled pixels |8,257,000|378,374|
| Doubled Otsu ink |534,622|46,034|
| Gaps in centre-path pair domains |3,759,119|1,307|
| Cut components under its definition |2,246|1,163|
| Foreign-row ink under its nominated owners |708,127|40,081|
| Lost Otsu ink |0|246|

Reproduce its definitions for comparison **and** report the actual complete final export. Relative ink and Otsu are separate observations. The prototype excludes oversized components from its cut count, skips discounted items and uses a first-claim `bown` image for some diagnostics/strips; do not copy those omissions into the real audit. Independently rasterise every exported item's actual mask and every strip, so overlap cannot disappear merely because the display gave a pixel to the first item. Count all items and large/non-text support separately as well as in totals. Use one frozen centre-path pair-domain set for all versions, alongside the historical nomination domains; never let the candidate shrink its gap denominator.

Nearest-path “foreign ink” is a diagnostic under an inferred owner, not proof that the owner is correct. Bind original-page own-row witnesses, accents and line-start letters independently. A smaller cut count is insufficient if new letters are cut on a73d or c3cc. List newly cut/shifted/lost components per page and review them. Record local legacy regions and their residual overlap; do not label a page tessellated when those remain.

**Committed tests through the real final caller:** extend the compact `features_geometry/test_final_bands.py` fixtures, preserving write-once existing packs. No `.astra` requirement or skip-if-missing for new protection. Replace the passing assertion that R is *not adopted* with actual positive column assertions when fixed; remove/rename the ineffective bypass test. Required controls/mutations:

- 4959 column and 44b5 ordinary Paddle neighbours: real compose → final masks/strips, shared smooth seams, complete true-row ink; 103/22 separate; a one-pixel contested component affects only its local interval. Disabling construction or restoring the row/chain veto fails meaningful broad-reach assertions.
- 3229 κατ’ whole in the actual final row (mapped and original-page observations separately), initial Σ preserved and the preceding ')' fragment excluded. Closure-off or original tight-boundary mutation must fail the returned-crop assertion.
- FONT census lower-row accents and speck/crossing controls, item-order ties, interlock local fallback, finite rule endpoints/initial δ, large-support conservation, patch joins and half-open masks. Restoring low>high averaging must expose a real cut, not simply change metadata.
- Same-content paper-envelope change does **not** invoke motif/source/frame again; changed actual content invokes the necessary existing decision and cannot reuse a stale receipt. Count real callbacks; do not mirror implementation in an assertion.
- Removing local fallback must fail the appropriate physical witness; injecting one bad interval must leave unrelated valid seams intact. Keep prior R smooth, vector-return and raster phase protections.

Then freeze a candidate and run the **fresh 208** both default-off and revised experimental-on. Review every changed page's whole segmentation/coverage and every produced strip, with detailed native review of all newly cut, shifted, lost, recovered or re-owned text and every exception class. Bind review coverage honestly. Keep all 15093 incoming items in the baseline ledger; justified duplicate retirement is mapped, never hidden as an item-count gain. Review source removals, faint front, 0ce9 ghosts, initials, useful M33 endings, “ἀποξήρανσίν”, missing rows and tables. No PDF/OCR truth or private-page tuning.

**Cost is a separate measured result, not an excuse to restore row gates.** Remove expensive refusal loops and unconditional revalidation first. On 44b5 the targets are 183 ms in `observe` and 168 ms/289 template calls in motif refresh. Profile actual preparation, fit/assignment, seam/raster, local repair and content refresh. Time accepted 9e8a196, current 3b7c57d default-off, and revised candidate under identical observed thread settings, so default-off's reported 278→297 ms is investigated too. Use the established MacBook runner, sequential work with no reviewer/worker benchmark overlap; confirm the coordinator's quiet window before timing. Ten warmed pairs per order, two five-pair blocks, unchanged detector/reference controls, the existing 5% drift rule and at most one replacement; preserve all samples. If no valid block survives, say unqualified and keep the physical result. Do not subtract detector drift or quote prototype 0.1–1.0 s as a forecast. Report global median/p95/max/>1 s and the existing≤100 ms incremental-page gate versus accepted 9e8a196, including cumulative 4959 debt. No default speed claim from invalid timings.

## 4. No new pipeline or page model

This replaces the final construction of existing items inside the current stack. No new detector, universal font/ink/noise provider, independent common curl model, production/Rust work, global cache, second quality-vote pipeline or new orientation mode. Quadratic centre paths describe observed local rows only; they do not complete CURL's shared-page task. Use source-bound existing observations and finite domains. `greekocr/`, other worktrees and private pages remain read-only/unseen. No background jobs, agents, pushes or self-launches.

Do not turn the **current i2** export on by default. Keep the revised i3 switch explicit and default-off for the frozen review; use tests and experimental-on outputs to prove reach. A safe revised route can be recommended for default adoption only after the independent check and coordinator's private evaluation. An opt-in physical result is still real progress; label its status. Do not keep both old/new experimental algorithms live, or make failed literal rows silently fall back to the full i2 qualification engine.

## What counts as progress and how this iteration ends

The first target is the literal construction's **whole-page scale of improvement**, not a larger count of isolated safe crops. Aim to match or improve the twelve-page diagnostic's overlap/gap reductions while repairing its text-loss and local attribution faults. Report every per-page delta; explain any regression against either accepted output or the literal benchmark. The observed 95%/91% reductions are a comparison target, not ground truth or a threshold that licenses text damage.

Strong i3 progress is a reproducible real-caller candidate that reaches ordinary full lines across the twelve books, removes most existing overlap/gaps, keeps known true-row letters/marks, confines unresolved failures to named intervals, deletes the failed gates and avoids the revalidation cost. Both required columns and κατ’ remain explicit physical targets. If a few interlock/duplicate/domain intervals remain, preserve the broad candidate and its safe portions, with exact open witnesses, rather than withdraw all page geometry. Whole-column/page completion is claimed only where every required interval qualifies.

Test/receipt improvements alone are not whole-page progress. Reduced overlap through dropped content, hidden legacy groups, smaller denominators, first-claim display masking or tighter letter outlines is not success. Distinguish default retained, experimental physical, architecture, timing-qualified and unresolved results. Full geometry remains open for required discovery/domain/reconcile dependencies; i3 does not spend FONT/CURL slots or authorise i4.

Coordinator evaluation: after source/configuration freeze, the coordinator alone compares accepted **9e8a196 / 3b7c57d default-off** with **revised i3 experimental-on** on the same private 44; verify off parity separately. Show **every whole page, every actual line strip and coverage maps for both versions**, including unchanged items, ordinary text, exclusions and local fallback intervals. Use real half-open masks, 0/1/2+ claims, separate ink duplication and fixed-domain gaps, stable row/retirement mappings and native detail. Inspect smoothness as well as text, not only a tessellation count. No simultaneous reviewer timing. Private inputs/images never go to planner/worker; disclosed cases become development-retest and repeated 44 is not a new untouched sample.

Deliver `REPORT_R8-GEOM-04-i3.md` and `.astra/fast_lines/out/round8/R8-GEOM-04-i3/`: source-bound unrepaired/repaired twelve-page tables, fixed metric/domain definitions, whole-page/every-strip/coverage index, local-exception/component ledger, actual callback/preparation counts, fresh 208/default-off results, raw timings, committed fixture/mutation receipts, caller/deletion map and compact `ITERATION_HANDOFF.json/.md`. Add dated i2 report/handoff corrections naming runner commit 3b7c57d, the archive suite 343+1 skip/13 xfails, the true gate failures, invalid costs and diagnostic limits. Preserve original receipts.

Meter 8% reported, no 14 October daily cap. Honour weekly 97% launch refusal/99% run guard and the stop signal; do not change them. Commit with one required trailer block or leave one source/hash-validated fallback under `.astra/` if protected Git staging fails. Return the full result to the coordinator and Astra for the next exact prompt. Final: plain words, then `RESULT: <DONE|PARTIAL|NOT DONE> <one line>`.
