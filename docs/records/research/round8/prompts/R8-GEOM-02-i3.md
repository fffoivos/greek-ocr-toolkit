# R8-GEOM-02 iteration 3: complete residual rows together between verified separators

Resume `01a12688-cfa4-7952-8edb-f98e8818f1ad`, track `ff8-stack`, worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`.

Start at `<HEAD>`: accepted tests/docs/evidence commit `0d4dc503145662fc9fcbf234b3e2ee664dae6641` plus the coordinator's planning-docs merge. Its runtime is still `54cc8f9ead2809d3c7da11f5a8e9a87334d2df24`. Preserve both identities in receipts. This is iteration **3 of at most 5**, subject to the live meter and closing reserve. Do not import the parked Rust pilot.

Read the **full** independent check `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i2_check.md`, your i2 report, and `.astra/fast_lines/out/round8/R8-GEOM-02-i2/` rejected source, actual row outputs, native images, replay and timing receipts. Read current PLAN/ROSTER/LOOP_HANDOFF and applicable AGENTS.md. Do not repeat a general inventory.

The owner has directly said:

> ok keep doing that then

This follows the discussion of making specific, cumulative repairs. The planner chooses one more geometry iteration within the existing cap, despite the checker's recommendation to move to Rust because unreliable neighbours make a one-iteration repair uncertain and threaten the remaining budget. The coordinator must still check the actual meter before launch. No later iteration or Rust launch is promised by this prompt.

**Correct the i2 diagnosis before proceeding.** It was not one apostrophe away from acceptance. The owned-only hull omitted an unassigned apostrophe; the old smooth band retains it but also reaches the next row. Other completed pieces lost whole rows, crossed the column rule or absorbed “θέσ” and “δὲν ἴδε” from neighbours. Sequential completion against `items+added` and x-only chain selection make those neighbours unreliable. Seven calls to whole-request M17 account for most of the added 383–415 ms. The checker also found a float-tie test failure masquerading as a physical regression. None of these is solved by tuning mark distance or engineering height.

**One implementation objective:** replace per-piece, owned-only residual completion with a simultaneous request-level use of the existing row-band/separator machinery. Preserve whole native ink on the appropriate side of verified neighbouring separators without requiring a semantic letter owner for every detached mark. This iteration does **not** retry finite-domain construction or M33 continuation.

The owner's method, verbatim:

> Doesnt the correction mostly invovle removing things then? and building models that can help verify the existing mechanisms

> (1) get the line segments as an input
> (2) draw the curves/skew lines and 4 lines for each line in the segment; you then give them the coordinates to seperate their identities
> (3) after you have the curves you have the 4 lines for each text-line you forget the initial line segments completely
> (4) you can draw a new segment simply by finding the middle between the bottom and top lines from neightbouring lines, and by extending left and right along the curve until you find a boundary

Here the existing native whitespace corridor is the explicit separating feature. It is not a claim that four font guides have been measured, or that every component's letter identity is known.

## 1. Builds on the existing code

Work inside `prototypes/fast_lines/shared/`. The live chain is `stack/pipeline.py:compose` → `type_extended.recover` → `type_residual_recovery.recover(version=11)` → native scouting, regional localization, `geometry_columns.apply`, `type_barriers.protect`, `piece_support`, neighbouring/source checks and accepted additions.

Reuse `geometry_field_detector.native_bands` and `separate_bands`, including `geometry_rows.valley_grid/valley_path` and their native crossing check. The unmodified `native_bands` makes a smooth band; the rejected i2 `support_rows` branch instead makes a per-column hull of dilated owned labels. **Delete that draft branch if reusing the archived implementation.** Neither an owned-label hull nor an unconstrained smooth band is the required output. Use the existing smooth envelope bounded by evidenced separators on both sides and the actual lateral column/rule support.

The i2 `type_completion.component_pixels`, `raster_envelope` and `complete_supported` extensions are archived candidates, not accepted providers. Reuse only compatible preparation and transformations after reading them; do not copy their failed ownership assumptions into another module. Preserve `snap_components`' other live callers when extracting shared preparation. Do not relabel removal of rejected code as a deletion from the accepted runtime.

Collect eligible residual pieces and their request/chain identities before completion. Supply the pieces together to one `native_bands` computation per exact request preparation, against a fixed, valid neighbourhood. Completion must not depend on which candidate was appended first. Keep existing source/duplicate admission rules explicit and re-evaluate affected decisions after completion; do not silently change them while batching. Duplicate or competing candidates cannot certify one another as distinct rows.

Existing neighbours can themselves span two rows or cross a rule. Their box midline is not a trusted physical row axis. Check them against the existing native body chains and separators. X-range alone must not select another row's chain. Where the available observations cannot establish distinct row support, retain an explicit unknown result for that piece; do not add a guessed centre, ratio or gutter model. Do not force every piece through a successful completion status.

Use unmodified pixel-seeded `greekocr/pages/lines.py` and existing font/boundary tools only as offline comparisons against native pixels. `_assign` also gives this apostrophe to the preceding row, so it cannot certify the answer here. No `greekocr/` edits.

## 2. Inputs match what the code expects

- Keep the real, census-dependent scout and regional requests. Do not freeze the i1 request windows in runtime. The two saved windows are controlled replay interventions only.
- Preserve `(request, chain, component, piece)` identity. Residual `data['bodies']` indices are filtered-list positions, not native CC labels. Keep origins/transforms explicit. No use of the last loop's request data or x-only merging of different chains.
- `native_bands` takes one crop and rows/axes in that crop's coordinates. Any shared labels/stats/ink must correspond to that exact crop, ROI, halo, scale, threshold and operator. Sharing preparation does not make the closing-relative mask a calibrated replacement for M17's mean-mask recipe; name and retain each actual contract. Engineering height is not a measured letter body.
- Build a stable candidate/neighbour set for the request, with explicit original-to-batched identity. Permuting proposal processing order must not change matched final rows or decisions. Rebuild affected decisions if membership changes; do not solve order dependence by caching `items+added` from one preferred order. Charge any justified rebuilds, and record cross-request overlapping support explicitly.
- A valid separator needs native support, not just a low sampled valley cost. `separate_bands` currently skips some pairs and extends/simplifies accepted paths beyond their sampled overlap. Those extensions do not certify unsampled regions. Validate the **final** polygon/seam against whole components and finite barriers; a path that cuts a component or lacks coverage remains unknown. Do not widen numerical tolerances to turn an ink crossing into a pass.
- Distinguish **segment containment**, **row/letter ownership**, and **print source**. Unowned marks safely inside a verified row corridor may remain in its crop and be recorded as unresolved. They must not supply positive row/body/source evidence. If two crops cover the same unknown mark, record shared uncertainty and withhold a unique-completion claim; do not silently duplicate or discard it. An unassigned component is not background.
- Where verified corridors establish unique row membership, the old nearest-body choice must not override that evidence. Update the row-membership record while leaving semantic letter attachment unknown if necessary; remove the old distance decision from that migrated population. A mark that is uniquely inside a segment is not thereby a certified accent of a particular letter, nor evidence that its print source is front-side.
- Completed geometry invalidates affected source/motif/barrier and duplicate decisions, B5 membership/anchors/votes, M35's pool and final Footprints. Recompute on the actual new polygons. A later M35 run does not retroactively validate earlier source decisions on old polygons.
- No Paddle polygons in `PixelPage.boxes`. Slow and fast component IDs are not interchangeable. Rows without initial Paddle ancestry remain valid candidates under the existing native evidence rules.

## 3. Removal and verification scope

The proposed replacement is the existing regional DB roof/floor **only where native row support and separators justify completion**. Elsewhere retain the accepted route with explicit unresolved status; that is an incomplete migration, not a new success fallback. An unknown status must not make a formerly accepted row disappear. Report exactly which populations use the replacement and where the old policy remains. Do not claim global definition reduction for a partial migration.

First encode the rejected failure, then repair the shared caller. In `features_type/test_residual_completion.py`, fix the separated fixture's 3e-13 px float tie using a documented subpixel comparison or, preferably, native ink across the rule. This is numerical equality handling, not physical loss tolerance. Verify its intended clipping assertion is reached. Correct xfail descriptions to the defects they actually test.

Add a compact checked-in consumer fixture where a target-row detached mark lies nearer by box distance to the preceding row's descender. It must reproduce the omitted mark under i2's owned-only hull. Include competing row ink, a finite column rule, and proposal-order permutations. Exercise real completion and separation, not a mocked ownership answer. Bind the regression and mutations to the exact tested source; confirm the intended consumer call executes. A test passing only on widely separated easy marks does not cover this failure. Keep the existing meaningful finite-domain/M18 and NaN tests; do not change the finite-domain producer this iteration.

**Primary native acceptance: both genuine 4959 p5 request windows, all recovered rows.** Render every accepted addition from baseline and candidate side by side and match rows by native content/support, not array index:

1. Target #109 retains the apostrophe (the recorded 88-pixel component) and full lower-body support (424-pixel annotation), with no preceding descender. These counts locate the witnesses; native glyphs and antialiased margins decide completeness.
2. All seven baseline recovered rows remain present in both windows, including “τος, ὑπεβάλλετε … στρα-” and “ἐκλογέων μας … σκέ-”. No loss disguised as a competing-row veto. No absorption of “θέσ” or “δὲν ἴδε”, and no native ink crosses the column rule.
3. Compare every matched row across both windows, not only #109, and permute candidate processing order. Full success requires the same canonical completed polygons and support dispositions for all seven. If some retain unresolved legacy extents, report their window dependence and keep overall acceptance PARTIAL; do not hide it behind the target's equality.
4. Preserve every component's disposition: assigned, uniquely contained but unowned, shared/unknown, excluded with inherited source evidence, or outside the affected support. The audit must expose missing and multiply contained ink. It must not count only assigned labels and announce completeness.

The actual native ambiguity replay must be reproducible. If its image stays local, identify it as replay evidence and keep the representative synthetic consumer fixture checked in. Do not assert that the synthetic fixture is the real image. Supplement with varied existing accent, punctuation and descender controls so the repair is not an elision-mark special case.

Preserve the six M33 controls (466 ending, 7792 punctuation, c8 tick, 9ea/dbd/d323 neighbour exclusions), “ἀποξήρανσίν”, 8686 p5/p7 recoveries, weak 31f40, pale 1be6, 0ce9 #34/#36 and the strict faint-front failure. P5 row 5, clipped ends and i1's unmatched 4959 p1/44b5 rows remain explicit debt. Adjudicate every changed final crop and exclusion before recommending runtime acceptance. No owner case is fixed merely because a software test passes.

**Measure cost against accepted runtime, not against the rejected trial.** The review estimates one batched request at roughly 60–80 ms, versus seven repeated 50–68 ms calls; this is a hypothesis to test. Record actual preparation, batch calls, pair/seam work, changed memberships and fallback counts. On the named two-window replay aim for no more than about +100 ms per request over accepted runtime; explain any excess and attempt the demonstrated duplicate-work removal before recommending it. This is a local engineering budget, not a new whole-page speed gate. Include callbacks and post-completion checks. No claim of a speedup just because i2's rejected +383–415 ms was reduced.

## 4. No new pipeline or page model

Use existing row observations and separators. No global ownership rewrite, new font classifier, universal ink model, nearest-distance variant, punctuation recognition exception, semantic language model, second gutter detector, new cache framework or Rust port. Keep M06 propagation deleted; M55, both DN floors and source uncertainty remain ink debt. No finite-domain retry in this iteration. The physical feature here is an evidenced separator between native rows, not an assumption that every component already has a correct semantic owner.

If wrong upstream rows prevent completion, identify the first invalid row/support input and the exact caller. A limited correction of how this caller represents an already observed row is in scope; another whole-page discovery model is not. Preserve independently safe caller/audit improvements if they pass their own native and integration checks, even if the full seven-row replacement stays partial. Tests/evidence alone remain tests/evidence, not runtime consolidation.

## Deliverables and close rule

- A coherent candidate in the existing providers/callers, with separate accounting for retained runtime changes, rejected code, policy migration and test-only work. No dormant second algorithm beside the old one. Source-bind the whole batch, component identities, separators and uncertainty record.
- `docs/records/research/round8/REPORT_R8-GEOM-02-i3.md` and `.astra/fast_lines/out/round8/R8-GEOM-02-i3/`, including native all-row comparisons, corrected/mutated consumer tests, WORK/TIMING, source identities, CONSOLIDATION_DELTA and structured ITERATION_HANDOFF. Preserve all owner ledger fields. Add a dated correction to i2's report/handoff naming runner commit 0d4dc50 and the independent findings: hull-induced omission, lost/absorbed rows, float-tie fixture, and repeated M17 cost.
- Focused tests, full prototype suite, genuine two-window replays and proposal-order counterfactuals. Run the 208 development pages on coherent retained runtime, reviewing changed output natively and using paired timing in both orders on the affected/quiet/slow controls. If all runtime edits are withdrawn, rebind exact source-matched evidence instead of claiming a fresh full pass. The coordinator alone owns the private44.
- State separately whether the shared-call refactor, unresolved-support accounting and seven-row physical repair passed. A safe partial caller repair may survive a failed broader completion; do not restore everything automatically. Conversely, the existence of a useful test does not justify shipping a text loss. If no runtime change is safe, retain 0d4dc50's 54cc8f9 runtime and give the next exact counterexample.

The coordinator checks all seven rows, not just the apostrophe; actual separator/ownership evidence and order independence; no false-completeness audit; meaningful tests and their failure reasons; no hidden source-policy changes; final output and paired cost. G3 remains PARTIAL while wider geometry obligations remain. No automatic i4 follows: the next result and independent check return to the planner.

## Resources and handoff

The last relayed meter was 88% **at i2 launch**, and i2 plus its review have since run. Do not present 88% as current. The coordinator checks the live meter and allows for this iteration, its review and roughly two points of closing reserve. No launch at/above 97%; start closure around 95% or earlier if the next iteration cannot leave that reserve. This further geometry iteration takes priority under the owner's latest instruction; a substantive Rust iteration is now conditional, and renewed ink is unlikely this meter. Caps stay geometry 5 / Rust 3 / ink 3 / audit 1, with no transferred slots, extra iterations or automatic rollover. There is no arbitrary wall-clock cap within an authorised iteration.

Use this MacBook's established development runner and Python environment, no concurrent benchmarks. No held-out access, PDF-text truth, orientation work, background jobs, additional agents, production edits or pushes. Anemi material stays internal. Modify task prototypes/tests/docs/evidence only in the assigned worktree; `greekocr/` remains read-only.

Commit scoped work on `astra/ff-r8-stack`; if staging is blocked, leave a validated `.astra/commit-F8-R8-GEOM-02-i3.sh`. Include:

    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01X3VU3zMmUxSHRDvYfQMczm

Finish in plain words, then `RESULT: DONE|PARTIAL|NOT DONE` naming R8-GEOM-02-i3, commit/fallback, retained changes, G3 status and best-head recommendation. Do not write or launch a successor prompt.
