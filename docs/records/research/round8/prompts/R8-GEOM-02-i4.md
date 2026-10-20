# R8-GEOM-02 iteration 4: finite neighbours and faithful native seams

Resume thread `01a12688-cfa4-7952-8edb-f98e8818f1ad`, track `ff8-stack`, worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`.

Start at `<HEAD>` = `0474bf86bf1ff677dcf0c6d596e2aa515cff81b2` plus the coordinator's planning-docs merge. This is the accepted i3 audit/tests head. **Its outputs equal 54cc8f9; its source does not.** One runtime file gained the support audit, net +23 lines. Keep 0474bf8 as the source/timing baseline and 54cc8f9 as the historical output reference. No Rust import. This is iteration **4 of at most 5**.

Read the full independent check `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i3_check.md`, your i3 report and `.astra/fast_lines/out/round8/R8-GEOM-02-i3/` archived `complete_request`, `trial-capture`, native sheets, all-row verdicts and timings. Read the current PLAN/ROSTER/LOOP_HANDOFF and applicable AGENTS.md. Use those captures rather than restarting discovery or an inventory.

The owner now says, verbatim:

> ok keep going with the task, dont just say failure from now on. You have to ask the reviewer more about the process, as in is there progress towards the solution even if the task didnt complete.

> We will do a reset don't worry about it

The cap remains five. The meter no longer truncates the plan: the coordinator pauses at the 97% launch refusal or 99% running guard and resumes after the reset. Do not bypass guards, reset anything yourself or launch a successor. Record coherent work if interrupted; no hidden extra worker iteration.

## What this iteration must establish

I3 completed **0 of 7 rows**; its output equality and proposal-order equality do not prove successful completion. Its audit is useful evidence on page-field M17, but residual recovery does not call it and no decision consumes it. Do not count more such bookkeeping as physical progress.

The checker identified four bounded corrections to the archived trial. Implement these and nothing broader:

1. Assemble same-line observed fragments into the proper finite neighbour on each side, separated at the accepted column rule and excluding the target's own chain.
2. Calculate and verify a neighbour's seam only on the x-support that neighbour actually has.
3. Preserve the native per-pixel valley path in the **actual clipping boundary**, so simplification cannot turn a valid 3-pixel corridor into a glyph cut.
4. Preserve lateral extent as the union of the admitted box and native owned bodies, subject to its existing column side; never use owned bodies alone to discard unassigned initial letters.

This is local repair of the existing request/row/separator representation, not a new detector. Keep each correction separately attributable and independently retainable when its live caller, native evidence and regression checks qualify it. Do not require the entire geometry task to pass before retaining a safe seam-construction fix.

## 1. Builds on the existing code

Providers are in `prototypes/fast_lines/shared/`. The live chain is `stack/pipeline.py:compose` → `type_extended.recover` → `type_residual_recovery.recover(version=11)` → native field/scout, regional localization, column/physical separator splitting and admitted pieces. The archived i3 `type_completion.complete_request` carries `type_support_chains`, groups admitted pieces per request and calls `geometry_field_detector.native_bands` once. Reuse this scaffold, not another wrapper with a different algorithm. It remains rejected until its corrections pass.

Use existing `type_residual.render` body contacts/chain identities, `type_lattice.point_ownership`, the accepted `geometry_columns` rule evidence and existing clipping primitives. In `complete_request`, replace the loop that treats each leftover fragment as an independent full-row neighbour. Retain original chain/component provenance. A fitted centre of an old two-row box is not a valid replacement.

Use `native_bands` and `separate_bands`, with `geometry_rows.valley_grid/valley_path`. Remove the trial's `verify_final` union-span extrapolation and its owned-only `complete=True` x extent. Replace the destructive 0.25h seam decimation where the actual geometry is constructed. Checking the dense path but still exporting/clipping with the old simplified path is **not a fix**. Prefer the already computed dense path; any later simplification must preserve the same native partition and cannot cut a component.

The owner's step (4), verbatim:

> (4) you can draw a new segment simply by finding the middle between the bottom and top lines from neightbouring lines, and by extending left and right along the curve until you find a boundary

The explicit feature here is finite support for the neighbouring text rows and the native separating corridor. The fast construction is checked against the unsimplified native path and whole components, not against another fitted-box statistic. This is not a claim that four font guides are measured. Pixel-seeded `greekocr/pages/lines.py` remains an offline comparison with known local errors; do not modify it or treat its wrong apostrophe assignment as truth.

## 2. Inputs match what the code expects

- `data['rows']` contains finite lower-contact chains, not complete lines. Assemble compatible fragments using their observed body-chain y support/contact continuity on the same column side. Show the native evidence for each merge; do not merge tall bounding boxes merely because they overlap in y. Retain supported x intervals and genuine uncertainty between them. Exclude shared target-chain members before forming distinct neighbours. Different fragments of the target's own line must not become competitors or steal its glyphs.
- Apply the accepted rule at its actual path and y support before grouping neighbours. Preserve whole-body provenance on either side; an object crossing the rule remains unresolved, not chopped into two certified glyphs. `geometry_columns.apply` contains a **6h inset test for splitting wide line polygons**. Feeding short fragment boxes to it does not guarantee they will split. Use its accepted rule representation and the compatible `layout_barriers.fast.clip_polygon` primitive, or a small explicit adapter for whole chain support; do not invent new gutter detection or ignore this input mismatch.
- Preserve request/filtered-body/native-label identities and native↔crop transforms. M17 mean-mask labels differ from residual closing-mask bodies. Engineering height is not letter height. Do not tune height, darkness or mark-distance thresholds to force the named components through.
- `separate_bands` needs row axes **and their finite support** in the crop's coordinates. Seam checks apply to observed shared support, not the union of two bounding boxes. A short fragment cannot certify an axis or rejection at the far end of another row. Where several supported intervals cover a row side, retain their identities and coverage; absence of a crossing check outside support is not evidence that the full side is safe.
- Use the native-resolution path to split the actual row shape and inspect the final polygon after clipping, interpolation, any simplification and export. Verify the gap between whole components, including their edge pixels. Do not widen crossing tolerances or erode strokes to pass the 3-pixel example. Components genuinely touching both sides stay unresolved.
- Preserve the admitted box's lateral support plus whole attributable bodies. Respect its accepted column side before union; do not union full cross-column proposals. Retaining unknown ink inside a segment does not assign its letter or print source. Keep shared/partial/unknown support explicit.
- Retain one batched call per exact request preparation. Use a fixed post-completion candidate set in the later checks too: i3's `others` included previously updated pieces and would become order-dependent once a row completed. Recompute affected source/motif/barrier/duplicate decisions on changed geometry; refresh B5 membership/votes, M35's row pool and Footprints as applicable. Do not cache old row-census decisions.
- No Paddle polygons in `PixelPage.boxes`; use unmodified rough pixel-region inputs for offline slow comparisons. Keep the real scout and varying requests active. Saved windows are tests, never runtime constants.

## 3. Removal and verification scope

**First prove each correction on the source-bound captures and a discriminating consumer test.** Use the following native witnesses (IDs are local to window 0; map by native support in window 1, never hard-code them in runtime):

| Witness | Required result |
|---|---|
| #109 lower edge: own φ 754, x2928–2954/y2716–2760; next-row β 906 begins y2763 | Keep the φ wholly inside and β outside using the existing per-pixel corridor; the actual final seam must follow it. |
| #109 upper edge: preceding-row descender 588 and fragments 10/14/16/17/18 | Form the supported preceding neighbour; 588 stays outside, target glyphs 736/757/721/738 stay inside. No fragment-axis extrapolation over unsupported x. |
| #109 apostrophe and lower-body witnesses | Retain the native apostrophe and full lower body in both real windows; no positive semantic/source claim follows from containment. |
| “τος,”: fragment 21 and initial components 1433/1466/1420 | Do not treat target-line or cross-rule fragments as neighbours. Preserve the whole “το” and the existing column boundary. |

Add compact checked-in regressions through the **actual** changed `separate_bands`/clipping consumer and residual `recover` chain. The seam fixture must fail when the old 0.25h decimation is restored, not merely when an audit key is absent. The finite-span/grouping fixture must fail on i3's union-span/leftover-fragment representation. The lateral fixture must fail with owned-only extent. Retain i3's ambiguity fixture as a pin of existing M17 behaviour; do not call it a discriminating residual test. Both corrected residual xfails must continue to reach their physical assertions. Bind each mutation to the exact source/test and verify the intended call executed.

Then run the **two genuine detector windows** (y2576–3080 and y2583–3079) through the real corrected residual caller. Require #109 to complete on both sides, with native row/support agreement across windows. Check canonical geometry without rejecting harmless floating representation as text loss or quantizing a physical disagreement away. “τος,” must retain its initial components. Review all seven additions so a target improvement cannot hide a lost row, “θέσ”/“δὲν ἴδε” absorption or rule crossing. Repeat with candidate/neighbour order permuted. Record proposed, completed, later-rejected and final counts; an all-unknown return is not completion.

**Limit this attempt.** If #109's separators still fail after the finite-neighbour, support-range and dense-path corrections, identify the first remaining physical counterexample and stop expanding the geometry design in this iteration. Do not add a new font/glyph model, discovery pass, guessed row, global grouping rule or guard. Preserve independently qualified separator/lateral corrections and their actual callers. The coordinator returns the check to the planner; absent a demonstrated reusable repair that materially closes a dependency, the next decision is to close geometry PARTIAL and move to Rust, not spend i5 repeating the same assumption.

For retained runtime changes, run the full prototype suite and one fresh 208-page pass. Inspect every changed crop/exclusion and preserve the existing M33, curled-ending, small-number, initial, weak/pale and source controls, including “ἀποξήρανσίν”, 0ce9 #34/#36 and the faint-front xfail. P5 row 5 and other open owner cases remain open unless newly evidenced. A correct local completion can coexist with legacy unresolved rows, but no row may get worse. The coordinator alone runs the private44.

Use paired uninstrumented timings in both orders against 0474bf8 on the existing affected/quiet/slow cohort, charging the full caller, final seam verification and recomputed decisions. Report actual one-call batching, pair/path work and full208 median/p95/max/slow-page list. No nested full-request repetition. The rejected i3 +95–132 ms is a comparison experiment, not a shipped baseline or saving. If only evidence/tests survive, rebind matching source evidence and label it honestly. No Python tuning campaign or Rust work here.

## 4. No new pipeline or page model

A local grouping of already observed fragments on an established column side is allowed to repair the input contract. It must not create new rows from density peaks, fit a new page bend, or replace the page model. Keep the current pipeline and native providers. No finite-domain reconstruction or M33 migration this iteration. No nearest-mark distance variant, additional ink calibration, semantic classifier or restored M06 propagation. M55, DN floors and M35 source uncertainty remain separate debt.

Do not expand `support_accounting` as a substitute for the fix. Its 230 substantial partial records on 29 pages are unadjudicated candidate evidence, not 230 proven final errors. Trace the particular records relevant to a retained seam correction through M18 and final crops if useful; a new corpus-wide audit of all 230 is outside this iteration. The audit is not part of a future Rust numeric port contract.

## What counts as progress, even if G3 stays PARTIAL

Report completion and progress separately. Give the reviewer the following evidence:

- **Retained physical progress:** #109, “τος,” or another independently defined affected population has a genuinely better final native crop through the real caller, without losses elsewhere, and the superseded construction is removed in that scope. Wider G3 may remain partial.
- **Retained mechanism progress:** a live seam-construction or finite-support correction now preserves the native partition it previously cut, with a real counterexample, discriminating old-behaviour mutation and compatible callers. It can count even if a later independent check still prevents final residual adoption. State that no final crop improved if that is the case; a dormant/offline provider is not retained mechanism progress.
- **Experimental process progress:** a corrected upstream representation or one separator now demonstrably passes on the actual captures and real caller, and the remaining failure is separately pinned. Preserve reusable code/fixtures and show which previously failing dependency is removed. This can be useful process progress without being a runtime gain; do not describe it as accepted physical improvement. Equality of unchanged “unknown” fallbacks does not qualify.
- **Still stalled physically:** all populations remain unknown or regress, no meaningful live correction is kept, and the only additions are counters, more audit records or another description. New counterexamples may improve diagnosis; identify that separately instead of calling the entire iteration simply failure or simply progress.

The coordinator's independent reviewer must answer: which earlier witness now passes and why; which code/fixture is reusable without redoing this iteration; whether the blocker narrowed in location **and scope**; whether the next step fits existing callers; and whether the claimed improvement generalizes beyond the named page. It should recommend i5 or task closure based on that evidence, with separate completion, retained-output and process verdicts. The owner requested this process assessment, not a relaxed text-preservation gate.

## Deliverables and handoff

Write `docs/records/research/round8/REPORT_R8-GEOM-02-i4.md` and `.astra/fast_lines/out/round8/R8-GEOM-02-i4/` with source/input/settings identities, per-correction counterfactuals, native views of both sides of #109 and “τος,”, all-seven-row decisions, tests/mutations, timings, policy/line accounting and structured ITERATION_HANDOFF. Keep original owner ledger fields and inherited versus fresh review distinct. Correct i3's handoff by dated addendum: runner 0474bf8, independent ACCEPT WITH NOTES, 0/7 final completions, audit-only retained change, and the checker's seam/fragments findings. Keep the original record.

Best head at launch is 0474bf8, including its safe audit. Keep valid independently reviewed changes; otherwise retain that runtime and attach the bounded counterexample. Full G3 still requires its other row/curl/domain/ownership obligations. No automatic i5 and no prewritten successor prompt.

Use this MacBook's established authorised runner, no concurrent benchmarks. No held-out access, PDF-text truth, orientation work, extra agents, background jobs, production edits or pushes. Anemi material stays internal. `greekocr/` and other worktrees are read-only.

Commit scoped work on `astra/ff-r8-stack`; if staging is blocked, leave `.astra/commit-F8-R8-GEOM-02-i4.sh` with a validated source-bound fallback. Required trailers:

    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01X3VU3zMmUxSHRDvYfQMczm

Finish in plain words, then `RESULT: DONE|PARTIAL|NOT DONE` naming R8-GEOM-02-i4, commit/fallback, retained changes, G3 status, progress category and recommended best head. Do not launch or write the next iteration.
