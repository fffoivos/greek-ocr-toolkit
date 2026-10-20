# R8-GEOM-04 iteration 2 — final-page shared export

You are the implementation worker. **Resume** thread `01a136ac-ed6b-7773-a1e6-ff484d531820`, model `gpt-6.1-sol`, effort `high`, track `ff8-stack`, worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`. Start at **<HEAD>**, the coordinator's docs merge onto accepted **9e8a196208528747ce82c808975134a05ab91ebe**. Confirm ancestry and a clean scoped tree. This is one additional authorised iteration, i2; no later iteration is prewritten or automatically allocated. Do the work in this turn; no agents or launches.

Read `SOL_WORKER_HANDOFF.md`, current `FONT_GEOMETRY_REPLAN.md`, your i1 report and **the full check** `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-04-i1_check.md`. Its scratch is `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/f1db7209-77e0-476f-b75b-886a69c81def/scratchpad/check_geom04_i1/`; use `overlap_sample.json`, `tools/overlap.py`, `outer_clearance_probe.png` and `free_outer*.json` as source-bound evidence, not runtime implementations. Inspect more history only for a specific contract.

Owner, verbatim:

> Our goal now is smooth clear lines for segmentation, without overlap. If the lines are tight as normal on the page, the segments should then tesselate the plane

> I want to see whole page segmentation, and teh lines it produces.

> (1) create a smooth line around the selected letters, by broading a little the boundary around the central line of the text
>
> (2) make sure there is no overlap with other lines by finding the middle line

> But the whole point of this generation of our model was so that we odnt have to have duplicate checks

**Build on the gain, widen the actual consumer.** I1 retained smooth complete rows 107/105 and their exactly tiled pair on 4959 p5, half-open masks through real consumers, and four changed R polygons. The outer rows remain ragged; B stays unchanged. Only 4/15, 093 development items migrated. Private 44 exports were identical, with no migrated item; 40/44 pages still have multiply claimed pixels (coordinator median about 4.8%). That is evidence of insufficient reach, not private-page input for this worker. Committed tests are **323 passed / 11 xfailed**, not 332; nine physical tests are ignored and do not protect a checkout. Correct that first.

## 1. Builds on the existing code

Implement **one final export authority**, `shared/geometry_bands.tessellate`, reached by `stack.pipeline.compose` at the final-item boundary immediately after `frame_exclude`, before final identity serialization/return. Consider **every final ordinary text item**, independent of whether it originated from Paddle, clipped/terminated Paddle, page_field, native B, R or a residue. Do not extend only same-request R qualification or require another row detector first.

Reuse the retained `smooth_band`, `shared_separator`, `band_polygon`, `polygon_mask` and `crop_mask`. Reuse existing finite centreline/axis evidence, `geometry.line_axis/robust_fit`, column/rule evidence, selected component receipts and `stack_ownership.reconcile/_pass` observations. `line_axis` currently estimates from polygon edge vertices; it is an initial nomination, not a reliable text path in a box holding two rows. Where needed, use existing robust fitting on the row's unambiguous body support, retaining finite domains; do not fit a new independent page bend.

Pass the reconciler's already computed native ink preparation explicitly, with its exact image/scale/threshold/height contract. It currently returns no reusable ink array and may return before preparing one; expose an ephemeral context or reuse the same existing preparation when absent. Label that unchanged native ink once, not once per item. Keep label spaces and arrays out of serialized diagnostics. The reconciler's relative `.08` contrast mask and request M17's absolute 20.4 DN mask are different observations, not interchangeable component IDs or a universal ink provider.

Move the adopted smooth-boundary responsibility out of `type_completion.corridor_hulls`/`geometry_rows.whole_children` into this shared final export for migrated populations; retain their row-discovery/membership evidence. Upstream proposal geometry may still be needed for existing selection, but do not smooth it and then smooth it again. Replace the final overlapping extent/duplicate clipping in the adopted scope rather than add a competing ownership vote. Report old calls/decisions → new consumer → deleted/redundant work; if an earlier operation still has a real use, name it. A globally safe fallback may remain for unresolved groups, never two competing final exports.

Original `greekocr/pages/lines.py:_boundaries` is the read-only explicit band/shared-boundary reference; `_assign/_make_lines` show the separate component/path responsibilities. Use saved pixel-seeded evidence where helpful; no tight Paddle polygons in `PixelPage.boxes`, no full slow detector on the runtime route. The existing central paths suffice to test this export hypothesis.

## 2. Inputs match what that code expects

### Whole-component ownership before boundary construction

Freeze the incoming final items, native ink components, source/exclusion records, existing finite paths/row identities and column evidence. Distinguish **current mask coverage** (often duplicated) from **intended physical row ownership**. Requiring every incoming mask to retain every pixel it already covers would preserve row 22's contamination and defeat this task. Preserve all genuine unique text support and total accepted text coverage while removing duplicate claims.

Use the existing whole-row/component receipts where available. Unique complete containment is a useful seed for ordinary single-row items, but a mixed-row or straddling box is not made correct by being the only current container. Build a deterministic finite row/component assignment using the already supported row paths and body support. Shared body components may be assigned by distance to those finite text paths when the competing rows are distinguishable, as in 103 versus 22; anchor paths on unambiguous bodies and record the candidates/distances. Do not recenter a box on its contamination and certify that same assignment. Ties, crossings and demonstrably mixed-row items stay unresolved with their first failure recorded. Row/input ordering must not decide the result.

**Do not copy the checker's blanket nearest-body rule for detached marks.** The FONT checks proved it can send a lower accent to an upper descender. Reuse existing unambiguous same-row attachment/whole-component support; preserve contested marks as unknown unless the same finite row evidence establishes their side. A comprehensive FONT model is not required. A mark with candidates on both rows must not be forced to an owner by a new distance/area cutoff.

**Whole-component closure is now allowed.** A proposed band must never take only part of an otherwise unowned observed component. In the same finite row/word/column support, include it whole when that row is its sole supported owner and no other row, removed footprint, frame/rule or unresolved source claim competes. Otherwise exclude it whole or keep the affected group unchanged. Lack of another full containment alone is not a text/source certificate. Account for partial claims too. This explicitly supersedes i1's blanket no-new-attachment restriction and must test **κατ’**, native label 32 (59 mapped pixels; separately count its original-page component). Exclude the real zero-parent strip-edge fragment of ')' from the preceding row and preserve speck controls; no blanket take-every-unowned-mark rule.

These are changes in the existing final geometric ownership decision, not a new font/source classifier. Freeze before/after per-component owner receipts. Audit native accepted ink union, each known true row, unresolved components and all additions; never make an aggregate overlap score improve by dropping text or hiding items.

### Final placement does not automatically preserve previous decisions

I accept the final-item placement, **not** the claim that unchanged component IDs alone preserve faintness/frame decisions. `ink_faintness.components` depends on ROI, mask-selected histogram and paper; `ink_frame_field.exclude_whole` uses glyph centres/geometry; `Footprints.stamp` includes polygons and raster convention. Removing duplicated ink or recovering an apostrophe also changes support. Trace these dependencies through `compose` before promoting the final output.

Treat tessellation as a proposal committed transactionally: preserve source/removal decisions whose actual inputs are identical; refresh the existing affected decisions where masks, support, calibration membership or source changes. Reuse the current hooks/measurements and batch changed items; do not bolt on a second general quality checker or rerun the entire stack. Update final footprint identity for adopted polygons. No removed ghost/frame/ornament may return. If validation changes a participating item set, rebuild only its affected neighbour group from the surviving supported items, or retain the incoming group and name the missing contract; do not serialize stale seams or repeatedly iterate classifiers until they agree. A final caller cannot bypass validation because the drawing looks right.

### Neighbours, edges and raster

Use the final supported row order in existing columns/rule domains; pair adjacent rows over finite common x with no intervening row and a real paper gap. Do not revive `geometry_page_field.blocks`' full-height median-x rule cut. The checker's50%-overlap/2.5h neighbour and 1.6 h outer-reach values are probes, not qualified universal geometry. Freeze any needed scale parameters before scoring and show endpoints, short lines, headings, columns and skew. Tables, figures and leaders remain outside ordinary text tessellation **using existing semantic evidence**, with unchanged outputs and counted coverage; do not exclude whole hard pages or all field/clipped items to lower the overlap denominator.

Reuse `shared_separator` on both items. For an exposed outer edge, use a **one-sided clearance** against relevant non-owned ink on that side, capped by ordinary padding. It needs no completed row identity for every obstacle; it is an avoidance envelope, not a shared pair or a new attachment. Keep the inner shared edge fixed. Replace inherited tight-edge/corridor clipping where it creates the demonstrated slope spikes, while preserving true finite column/rule/exclusion barriers. Empty obstacle support means ordinary bounded padding, not a fabricated neighbour.

Every exported shared edge uses `EDGE_CONVENTION`/`crop_mask`: geometric interiors disjoint, common edge allowed, boundary pixels assigned once. Preserve the wired mask consumers and legacy behaviour on untouched items. Non-x-monotone residues need the existing scanline path checked against the fixture's true mask; do not fill holes/concavities into text. No downstream OCR claim for unmodified `greekocr`, which still lacks this raster flag. The actual prototype strips and all coverage measurements must use it.

## 3. Removal and verification scope

Start with small **committed** fixtures and the actual final caller, then expand to the frozen pages. Copy only the minimal real crops/labels, paths, pair metadata and hashes required from i1's4.3 GB captures; no absolute `.astra` or `/private/tmp` dependency, no whole-page-model download, and no test that skips because ignored exports are absent. Reuse the write-once `font_guides_native.npz`/`whole_children_native.npz`; never regenerate the 6.9 MB pack. Fixtures containing derived labels must also bind original pixels and their observation contract.

Port i1's real physical assertions into `features_geometry` and prove that disabling smooth export fails the committed suite. Replace historical exact-gap 61/384 pins with success assertions where repaired; retain the old numbers as a failure receipt, not the desired outcome. Tests must call final compose/export (using frozen upstream outputs for a small fixture is acceptable), not merely a copied formula or a handcrafted final polygon. Assert the actual returned masks and OCR strips.

**First full-chain witnesses:**

- 4959 p5 right-column items 23/109/107/105/103/22/20, bound by source geometry/ancestry: all normal neighbouring pair domains covered exactly once; outer 109/103 smooth; zero duplicated owned text; all four R rows complete; row 22 no longer contains row 103's letters. Preserve row 22's own text and row 23's descender (the unclipped probe absorbed 33 pixels). Inner 107/105 gain must remain.
- 44b5 p1 ordinary Paddle neighbours: whole-column coverage, no duplicated text/cut letters, no junk residual items. This is required default reach beyond R/B.
- 3229 p2: preserve the clean lower B row and its 57 members; close κατ’ whole in the physically correct final row without resurrecting the preceding ')' fragment or changing ownership of neighbour accents. Record whether upper straddling/field selection still blocks a usable row; do not claim a missing mark solved only inside an unused B child.
- a73d p47 and c3cc p2: reach clipped-Paddle and field/Paddle boundaries, count every refusal and review foreign rows/rules. A 73 dp 301 item 54 remains a distinct straddling-row control, not the p47 working page.

Fallback is atomic over all affected adjacent items, not independent overlapping pair patches: a row belongs to two pairs. Keep already safe compatible seams where possible, but rerun the **global final overlap/loss audit including every legacy neighbour**. Unsupported pairs are unresolved, remain in the fixed all-page denominator, and do not count as tiled. No new row detector/row-count repair is required here; no empty/sliver item may be discarded merely for size. A duplicate-only item can retire only with all its genuine support proved whole elsewhere, with provenance and a real test.

Required mutations in the committed test suite: bypass final tessellation or limit it to R/B (4959/44b5 global pair assertions fail); inclusive raster fill (double claims); one-sided shared application (gap/overlap); disabled outer clearance (raggedness/foreign descender); disabled whole-component closure (κατ’ cut/missing); a changed membership/mask without final decision refresh (stale-input assertion). Preserve i1's phase/coarse/tight and existing whole-member regressions with honest targeted failures. Input/item-order permutation must not alter physical ownership or seams. Old nearest-box assignment must not be installed to make ambiguous controls pass.

Then fresh **208** baseline 9e8a196 versus candidate, with disabled new final stage reproducing the accepted source including R's gain. Review every changed final crop, removed item and source decision. Record overlap twice: geometric area and actual half-open pixel multiplicity; separate all covered pixels and native ink, absolute counts and fractions. Count each multiply covered pixel once in the headline totals; pair-attributed sums are separate and may double-count triples. Count gaps only inside frozen supported inter-row domains, never all page background. Retain all 42 GEOM cases, 22 FONT cases, 133 owner marks/nine missing-row pages, and preserve negative/weak print, initials, rules, M 33 endings and “ἀποξήρανσίν”.

**Cost:** final export must not add a second native preparation per row. Report preparation reuse/build counts, time of ownership/bands/validation/raster work, full corrections and file-to-final. Use the established MacBook runner sequentially, fixed actual thread settings, paired both orders with repeated unchanged detector/reference controls. For primary pages use 10 warmed pairs/order in two 5-pair blocks, the declared 5% drift rule and at most one replacement for an invalid block; keep all samples, no favourable pooling/control subtraction. Target neutral/low overhead; retain the≤100 ms incremental page ceiling versus 9e8a196 as a resource gate and disclose cumulative cost versus 3e92e98/db899f1, including inherited 4959 excess. Report global median/p95/max/over1s; do not compare different 208/private44 populations. If cost alone blocks broad adoption, preserve the correct frozen experiment and measured bottleneck for review, not an all-unknown claim.

## 4. No new pipeline or page model

This is the final export of the existing item set with one explicit geometric owner per supported component and one shared boundary authority. No new detector, universal font/ink/noise model, independent curl fit, global persistent cache, extra correction vote, Rust port, orientation or production work. `greekocr/` and other worktrees read-only; no PDF-text/OCR truth, private-page access, background jobs, agents or pushes. Do not change ink thresholds to eliminate overlap or restore neighbour-row back-print propagation.

A scoped fallback for physically unresolved inputs is allowed; origin-kind gating that again limits the construction to R/B is not. If ownership remains the first blocker, name the actual component/row ambiguity across the page rather than growing a new set of guards. Keep valid output and verification gains, and return the result/check before any i3.

## What counts as progress — frozen whole-page sample

Before edits, freeze source/input/call hashes, baseline final item mapping, every ordinary-row pair/domain, existing semantic exclusions and ownership witnesses on these **12 development pages** (the checker's sample):

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

Work first on 1–4 and 7. Score the remaining seven after candidate freeze, as development-retest (all were previously observed, not new unseen data). Keep the original result if later repair uses them. Also preserve GEOM-03's exact seven negative pages/two layout pages, table/leader controls and all existing case ledgers. The near-zero db97 overlap is 606 pixels/7 ink in the checker's JSON, not literally zero; recompute with the real crop mask. No favourable sample replacement or candidate-selected domain shrinkage.

Per page and pair report baseline→candidate: items by origin; rows considered/migrated/excluded/unresolved; shared/doubled pixels and ink in **all final items**; gaps in the fixed domains; complete/cut/lost/recovered components and actual owner; slope/vertices; empty/residue counts; downstream-decision refresh; cost; first failure. Show native before/after whole-page overlays, coverage maps and **every line strip**, including unchanged/refused/excluded items. Separate safe accepted text from source-unknown pixels; no tally alone is ground truth.

**I2 target:** both primary complete-column witnesses (4959 right, 44b5 p1) have every ordinary adjacent pair tiled, with whole single-row text and no duplicated ink; default final construction reaches Paddle, clipped and field populations on the frozen sample; outer edges and the named apostrophe are assessed through final consumers; source-bound committed tests protect the gain. Whole-page overlap/gaps improve on multiple books, with no new physical regression or hidden denominator change. All ordinary items must be considered, even when individual groups cannot migrate. A verified whole-page success is a stronger claim than a completed column; report them separately.

**Useful partial progress:** safe default non-R/B final export on multiple books with measured lower all-page overlap/gaps, conserved text, committed tests and real displaced work, even if mixed-row/domain cases remain. Test-only protection and one-sided outer-edge repair are valuable but do not solve whole-page reach. A lower overlap fraction obtained by lost letters, excluding hard origins/pages or enlarging blank coverage is not progress. Report retained physical/architecture, experiments and narrowed blockers separately. Full geometry remains open while required row/column/missing-row dependencies fail.

## Coordinator held-out evaluation and deliverables

Freeze source/configuration and raster convention before coordinator evaluation. The coordinator alone runs baseline **9e8a196** and candidate on the same private 44, sequential paired timing. On **every page in both versions**, present whole-page segmentation, **every produced line strip** in reading order with stable mappings/native detail, and coverage maps showing 0/1/2+ claims inside fixed text domains, separate ink duplication and outside-domain exclusions. Include unchanged pages, missing/extra/sliver rows, excluded types, and failed groups. Use actual `crop_mask`/half-open metadata; no generic inclusive fill or display-only smoothing. Keep an owner-visible comparison to 3e92e98 where useful so tiny incremental gains do not obscure remaining overlap.

The coordinator inspects text loss, wrong owners, cropped marks, column/rule intrusion and overall smoothness, plus paired cost; report overlap for all 44 and comparable per-page denominators. Do not require a favourable held-out result to be reported as unchanged. Worker/planner never see private inputs/images. Owner-disclosed cases become exposed development-retest; repeated 44 evaluation is not a fresh untouched sample, and a fresh coordinator reserve is used for final confirmation if available.

Write `REPORT_R8-GEOM-04-i2.md`; evidence `.astra/fast_lines/out/round8/R8-GEOM-04-i2/`: frozen cohort/pair/owner manifests, actual source/refresh contracts, all-page before/after overlap-and-gap census, all case ledgers, exported page/every-strip index, **committed fixture/test paths and hashes**, mutation receipts, changed 208 review, raw timing/preparation counts, caller/deletion map and `ITERATION_HANDOFF.json/.md`. Add a dated i1 correction: committed 323 versus ignored 9 tests; runner commit 9e8a196 exists; outer-edge refusal was a scope restriction, not physical impossibility; private 44 unchanged and broad overlaps remain. Preserve historical receipts and update the responsibility/test documentation with the actual final consumer.

Meter 7% reported on 14 October. The 13 October daily 17/20 cap expired; **no daily cap is set today**. Honour the coordinator's standing weekly 97% launch refusal/99% run guard and stop signal; do not change or bypass them. Commit with one required trailer block, or leave one scoped source/hash-validated fallback under `.astra/` if blocked. No new worker launch. Final: plain words, then `RESULT: <DONE|PARTIAL|NOT DONE> <one line>`.
