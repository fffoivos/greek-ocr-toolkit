# R8-GEOM-02 iteration 5: verified separators, then tight component hulls

Resume thread `01a12688-cfa4-7952-8edb-f98e8818f1ad`, track `ff8-stack`, worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`, branch `astra/ff-r8-stack`.

Start at `<HEAD>` = `b96cd9de78b425146a6573ee4ba31a47a5ce2f64` plus the coordinator's planning-docs merge. I4 is independently ACCEPT WITH NOTES. Its runtime equals 0474bf8; it adds the native-seam tests, not a physical repair. Use b96cd9d as the source/test baseline, 0474bf8 as the identical runtime baseline, and 54cc8f9 only as the historical output reference. This is **iteration 5 of 5**, the last authorised geometry iteration. No Rust import or successor launch.

Read the full independent check `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-GEOM-02-i4_check.md`, your i4 report, current PLAN/ROSTER and applicable AGENTS.md. Reuse `.astra/fast_lines/out/round8/R8-GEOM-02-i4/` archived trial, genuine-window `replay.py`, order replay, isolation regressions and native witnesses. The checker's read-only counterfactuals are at `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/f1db7209-77e0-476f-b75b-886a69c81def/scratchpad/check_geom02_i4/`: `trialfix/`, `run/cf_*`, `cf_109_both_windows.png`, `cf_right_column.png`. They are design sketches, not qualified runtime code; preserve the relevant source-bound evidence in your own handoff rather than relying permanently on a temporary directory. Inspect i2's `window-0-whole-row.png` and the other window too.

## Decision and the owner's preferred result

The owner, looking at i2's #109, says verbatim:

> bro, I am not sure I fllow. iteration 2 is quite good

The owner is right about its tight per-word outline and restored descenders. Preserve that advantage. Its rejection concerned incomplete/wrong component membership: a dropped apostrophe on #109 and absorbed words or lost rows elsewhere. It was not a rejection of the shape. **First establish membership between verified separators; then build the tight hull around exactly those whole components.** Do not restore the owned-only hull or output a broad smooth band merely because it passes an internal check.

The standing instructions remain:

> ok keep going with the task, dont just say failure from now on. You have to ask the reviewer more about the process, as in is there progress towards the solution even if the task didnt complete.

> We will do a reset don't worry about it

The independent i4 process verdict is **CONVERGING for the right column, STALLED upstream for the left**. Three right-column rows complete in both windows in the checker's real-caller counterfactual. #109 still fails on four pixels of component 622. No runtime repair survived i4. Spend this iteration on the identified right-column dependency, not a new seven-row reconstruction. The three left-column rows remain unknown on their existing route, not dropped.

## 1. Builds on the existing code

Use `prototypes/fast_lines/shared/` and the current call chain: `stack/pipeline.py:compose` → `type_extended.recover` → `type_residual_recovery.recover(version=11)`. Reuse the archived i4 `type_completion.request_neighbours`/`complete_request`, its fixed request census and **one** `geometry_field_detector.native_bands` call. It supplies finite observed chains from `type_residual.render`, `type_lattice.point_ownership` and accepted `geometry_columns` evidence. Keep those input identities, the fixed subsequent `others` set and proposal-order independence.

Change `geometry_field_detector.separate_bands` and its compatible `native_bands` interface only through an explicit keyword mode selected **solely by `complete_request`**. Default `geometry_field_detector.run`/page-field M17 callers must retain their existing behaviour. The shared strict-crossing/finite-support changes tried in i4 regressed default M17/M18 on 4959 p4/p5; do not promote them globally again. Reuse the common preparation and solver primitives rather than copying M17 into another implementation. Thread support/rule inputs explicitly; the checker's global `RULE_IDS` and environment monkeypatches are not an implementation to adopt.

There are three separator/support repairs and one output construction:

1. Refine `geometry_rows.valley_grid/valley_path`'s coarse proposal at **actual native pixel resolution on undilated M17 ink**, in a bounded band between the existing row axes. Validate the final separator against whole components with zero crossing tolerance.
2. Use the existing accepted column rule's **ink edge** as a finite barrier for both support intervals and output polygons. Its centreline is not the edge of its ink.
3. For neighbours as well as targets, support is observed fragment spans **union the whole owned bodies**. Cover interval endpoints consistently through clipping and rasterisation.
4. Once the separator corridor admits complete components, reuse i2 `type_completion.raster_envelope` (in the archived `rejected-source/`) to make the tight output around that admitted set, including the apostrophe. Replace its old owned-label selection with verified corridor membership. Recheck the exported hull; smoothing, padding or simplification must not change the component partition.

The owner's construction step remains, verbatim:

> (4) you can draw a new segment simply by finding the middle between the bottom and top lines from neightbouring lines, and by extending left and right along the curve until you find a boundary

The physical features being verified are the inter-row paper corridor, finite rule ink and whole component support. The dense undilated native rendering checks the fast/coarse proposal; the final native crop checks the hull. No claim of measured four font guides follows. `greekocr/pages/lines.py` remains only the pixel-seeded offline reference with known local errors, not a replacement pipeline or an apostrophe oracle.

## 2. Inputs match what the code expects

**Correct the earlier premise.** There is no hidden per-pixel path for i4 to recover by removing decimation. The solver samples about one column per 13 px and one row per 4 px over a 5×5-dilated mask. Its interpolated output is still a coarse-grid solution. Removing decimation alone did not fix it. In window 0 the lattice hits a tiny opening; `int(y1.min())` shifts window 1's lattice and its path falls through β/λ. I3's apparently valid path touched φ and passed only through the old ±2 px tolerance. Do not repeat that assumption under a new name.

- Keep the existing M17 native mask/CC8 preparation and its exact image, ROI, scale and threshold contract. Undilated here means the existing M17 ink **before the extra separator dilation**, not a new ink estimator. Preserve residual-closing versus M17-label provenance; diagnostic component IDs from different masks/windows are not interchangeable. Engineering height remains engineering height.
- Coarse samples propose a search, not a certificate. Refine only the needed supported corridor, including its endpoints, at native resolution. A band around the wrong coarse path must not exclude the real φ/β corridor. Derive its allowed range from the existing neighbour geometry/support; record the range and any no-path result. Reuse work within the one request. Do not adopt the checker's full-plane Python DP, which roughly doubled request time, or add a page-specific lattice-phase correction.
- A valid separator crosses no text ink and places every relevant component wholly on one side. Pixel-centre, interval endpoint and polygon raster conventions must agree. Zero tolerance means no ±2 px crossing allowance and no “only four pixels” exception. Resolve #109's component 622 endpoint defect by representing its full support, not ignoring it. Recheck actual exported geometry, not only the path array.
- Clip support and polygons to the appropriate **physical edge of an already accepted rule** over its observed y range. The native rule here is x1553–1570; the failed right supports start x1557–1561 inside it. These numbers are test witnesses, never runtime coordinates. Use existing accepted rule/path/component evidence to locate the edge. Merely excluding the rule ID from the crossing audit while leaving its bar in the crop is not a fix. Text joined to a rule or an unsupported endpoint remains unresolved; do not classify arbitrary vertical ink as a rule or cut a joined glyph. Respect `geometry_columns.apply`'s wide-box preconditions; short supports need the compatible existing clipping primitive/input adapter.
- `data['rows']` contains finite contact chains, not complete semantic text lines. Keep i4's successful same-line fragment grouping and rule-side provenance. Neighbour spans omit bodies 622/707 in the gap x1974–2247; include their whole x support without treating every unobserved gap as a full-width trusted axis. The target's own chain cannot become its neighbour. Do not repair the left column's erroneous row axes this iteration.
- A side with **any** accepted interval is not automatically verified across its whole retained support. Account for all intervals relevant to the candidate's components and both boundaries. Keep the existing whole-component check as an actual consumer; an empty check or ignored interval cannot certify a row. Whole unassigned marks lying within the verified corridor can be retained without assigning a semantic class or front/back source. Do not use nearest-body ownership alone to discard them.
- Construct the hull from admitted whole components, then verify it still includes their full native ink, excludes neighbouring components and rule ink, and stays inside the verified corridor. Preserve the admitted box's lateral search support plus bodies before membership selection, so “το” is not lost again. A tight final hull may remove empty paper; it must not remove a weak native stroke missed by an intermediate mask. Inspect grayscale crops as well as labels. Record unresolved support rather than tuning darkness to fit the example.
- The two genuine detector requests remain y2576–3080 and y2583–3079 in the replay, with their genuine saved inference maps. Do not freeze runtime requests to a favourable window. No Paddle polygons in `PixelPage.boxes`; offline slow discovery still takes rough pixel regions. Residual/no-seed rows continue through the current scout/localisation route, with unchanged fallback for unverified completion.
- Recompute affected B5 membership/anchors/votes, M35 row-pool decisions, exclusions, duplicate checks and final footprints when polygons change. Only unchanged image/ROI/scale/threshold preparation may be shared; old row decisions may not be carried across the new geometry.

## 3. Removal and verification scope

Within the qualified request-completion population, replace raw crop-window-sensitive detector extent and the rejected owned-only hull with separator-admitted component extent. Remove the displaced trial construction there, not merely add another vote or unchecked fallback after it. The normal page-field separator stays unchanged outside this scope. State the conditional removal honestly: this is not removal of M33, all seven bend authorities, or all raw residual extents.

**First prove the bounded repairs through real consumers.** Use compact native fixtures and call `separate_bands` in the new request mode, `complete_request`, and residual `recover(version=11)` with genuine saved detector maps. Verify those functions were actually reached with non-empty rows. Keep the archived counterfactual reproducible; do not rerun a corpus inventory first.

| Native control (window-0 IDs; map by native support in window 1) | Required result |
|---|---|
| #109 lower φ 754, last ink y2759; next-row β 906/915 begins y2763, λ 923 | Whole φ inside; whole β/λ outside in both lattice phases. Use the real 3 px undilated corridor; touching φ is failure. |
| #109 upper neighbour 588/607; own 736/757/721/738/754 | 588 outside (0/401); all target components whole, including apostrophe 757. |
| Upper-neighbour bodies 622 and 707 in the span gap | Complete support represented; no partly included neighbour, including the four endpoint pixels currently blocking #109. |
| Column rule 51/52 | A physical barrier outside every completed right-column crop, not merely removed from an audit list. |
| “τος,” initial components 1433/1466/1420 | Retain all 180/69/303 pixels and the complete row. |
| Left “ἐκλογέων”, “ψεων”, “θέσις” | Stay unknown with existing crops preserved; no attempted repair of λ689/ς1131 axes or absorbed “θέσ”. |

Add discriminating tests: restoring the coarse/dilated path or tolerance must break the real two-phase φ/β test; restoring rule-centre-only support must break the barrier test; removing owned-body support must break the gap/endpoint test; reverting to owned-only hull membership must lose the apostrophe. Test the **final hull consumer**, not a duplicated formula. I4's decimation-only mutation passes and is not discriminating. Keep its valid on-seam/finite-support witnesses, scope corrected-mode assertions to that mode, and preserve strict xfails for still-unfixed default/left defects. Add order permutation and default-keyword parity controls without changing unrelated tests merely to make the suite green.

**Preset scoped success:** #109 and “καὶ τακτοποιήση”, “πάτε”, “τος,” complete in both windows through the real recover caller, with tight hulls, whole descenders/marks, no neighbour words or rule bar, and unchanged candidate-order result. All seven baseline rows survive. The three left rows remain uncompleted. No rule, page ID, component ID or “right column” special case may select the runtime population: it is selected by the existing finite support and valid-separator contract.

The checker's 39/18/4/33-pixel window differences are diagnostic, not an acceptance tolerance. Aim for i2's repeatable hulls. Compare native component membership and final raster across both windows; inspect and explain every remaining difference. A harmless boundary difference in blank paper is distinct from text loss, and neither rounding nor a high IoU may hide changed glyph/mark membership.

**Default-route isolation and corpus verification:** preserve existing page-field M17 outputs byte-for-byte on a fresh 208-page pass at the same inputs. The new mode is called only from request completion; add call evidence and a default-argument differential test. Check both the legacy/default configuration and the integrated residual-completion candidate. With completion disabled, all final exports/evidence must equal b96cd9d. With completion enabled, the intended residual changes are allowed and must be reviewed; the existing page-field route must still be unchanged. Do not demand identical final exports as proof of a crop improvement. If the candidate remains opt-in only, say so: an off-default result is not shipped default physical progress.

Inspect **every changed final crop/exclusion** on the enabled 208, not only these witnesses. Preserve the earlier M33 endings/narrowings (466 “πό-”, 7792 punctuation, c8 tick, 9ea/dbd/d323 neighbour exclusions), 4959 p4 row105 and p5 “πάτε”, curled ends, small numbers/initials, weak/pale text, “ἀποξήρανσίν”, 0ce9 #34/#36 and the strict faint-front failure. Native quality remains the criterion; default equality preserves known defects. The coordinator alone runs private44 when runtime changes.

Measure full requests in alternating paired orders against b96cd9d/0474bf8, including preparation, the one batch call, path refinement, hull verification and refreshed downstream decisions. **Added cost must be ≤100 ms per affected request** on repeated paired measurements of both genuine windows and the changed-request controls; report the distribution and worst paired request, not a corpus median hiding a slow target. Diagnose load with unchanged detector work. No repeated whole-request completion or benchmark-only omission. Report source-bound full208 clocks and slow pages as well. The checker's slow prototype is not a new baseline.

If these repairs cannot retain a regression-free population, or cost remains over the bound, stop design expansion and close geometry PARTIAL. Keep independently qualified live corrections only if their actual consumers and native/cost checks pass; otherwise retain b96cd9d runtime and preserve the specific last counterexample and reusable experiment. No new permissive guard, left-column project or sixth iteration.

## 4. No new pipeline or page model

Repair the existing request-local separator representation and output hull. Do not add row discovery, a page/column bend model, a gutter detector, font/class/ink calibration, semantic mark classification or another recovery pipeline. No finite-domain retry or M33 migration this iteration. Keep M06 propagation deleted; M55, M35 source uncertainty and both DN floors stay explicit debt. No broad audit of the 230 support-accounting records, and no Rust/production work. Do not port the audit as part of a numerical contract.

## What counts as progress and how this task closes

Report **iteration completion, retained output/mechanism progress, and experimental process progress separately**:

- Full scoped iteration success is the four right rows above in both windows plus default isolation, no corpus text regression and the request cost bound. Broader G3 remains PARTIAL unless its separately required domain/curl/row/policy obligations have actually passed; four good rows cannot close those historical debts.
- Partial retained physical progress is a non-empty, physically defined subset with better final crops and a real live consumer, no losses elsewhere and measured cost. Do not make all four rows a condition for retaining an independently sound fix. Name incomplete targets and whether the consumer is default or opt-in.
- Retained mechanism progress is a verified separator/support/hull correction used by an actual consumer, with the old defective construction removed in that scope, even if a distinct later decision still prevents final adoption. State that no final crop improved when applicable.
- Experimental progress is a previously failing real-caller witness now passing in reusable code with a separately pinned remaining blocker. Distinguish this from accepted runtime changes. Another all-unknown replay or added audit records alone is not physical progress.

Ask the independent reviewer which earlier witnesses now pass and why; what survives in actual output versus offline experiments; whether the blocker narrowed in location **and scope**; what control supports generalization; whether any native text or cost regressed; and which checked head/contracts should pass to Rust. Preserve i4's CONVERGING-right/STALLED-left verdict as the previous state, not a retrospective claim of shipped improvement.

**After this result and check, geometry closes at its cap.** Keep the best independently checked head, even if that is b96cd9d with tests only, and carry G3's open obligations forward. The coordinator returns both to the planner for R8-RUST-02 i1; you do not write or launch it. No automatic extension or transfer of the retired pilot slot. The owner-authorised reset removes meter-based plan closure, not caps: coordinator pauses at 97% launch refusal/99% run guard and resumes unfinished work after reset under the same iteration identity.

## Deliverables and handoff

Write `docs/records/research/round8/REPORT_R8-GEOM-02-i5.md` and `.astra/fast_lines/out/round8/R8-GEOM-02-i5/` with source/input hashes, changed API/caller contracts, each repair's counterfactual, both-window corridor/whole-component/hull images, all-seven-row decisions, full changed-crop review, consumer/mutation tests, default isolation receipts and paired request/full-page timings. Record runtime additions/deletions and exactly which policy scope was displaced. Keep original owner ledger fields; no owner case is newly fixed merely by a nicer crop.

Add dated corrections to i4's report/handoff: runner commit b96cd9d, ACCEPT WITH NOTES, no retained runtime repair, the coarse-lattice/dilation finding, and the right/left progress split. Preserve the original account while withdrawing the earlier “per-pixel path lost by decimation” explanation. Put the actual final commit/fallback state in your own handoff; the runner's later commit needs a dated addendum if staging is blocked.

The structured `ITERATION_HANDOFF` must give the best head, activated versus experimental APIs, Rust compatibility/fixtures, left-axis and finite-domain/M33 debt, remaining owner cases, source/ink recomputation requirements, timing debt, and final geometry COMPLETE/PARTIAL status distinct from scoped i5 success. Stable default M17 and the qualified request-only mode are separate contracts; do not require Rust to port an unqualified trial or the audit.

Use the established authorised MacBook development runner, no overlapping benchmarks. No held-out access, PDF-text truth, orientation work, extra agents, background jobs, production edits or pushes. Anemi material remains internal. `greekocr/` and other worktrees are read-only.

Commit scoped work on `astra/ff-r8-stack`; if staging is blocked, leave `.astra/commit-F8-R8-GEOM-02-i5.sh` with a validated source-bound fallback. Required trailers:

    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01X3VU3zMmUxSHRDvYfQMczm

Finish in plain words, then `RESULT: DONE|PARTIAL|NOT DONE` naming R8-GEOM-02-i5, commit/fallback, retained changes, G3/task closure status, progress category and recommended best head.
