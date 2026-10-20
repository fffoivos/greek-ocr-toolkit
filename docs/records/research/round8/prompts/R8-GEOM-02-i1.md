# R8-GEOM-02 iteration 1: consume finite column boundaries correctly

Resume thread `01a12688-cfa4-7952-8edb-f98e8818f1ad`, track `ff8-stack`.

Worktree: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`

Branch: `astra/ff-r8-stack`

Start from `<HEAD>` = independently checked `54cc8f9ead2809d3c7da11f5a8e9a87334d2df24` plus the coordinator's planning-docs merge. Verify that the runtime tree matches 54cc8f9 before editing. Do not merge or cherry-pick Rust candidate `953fc4ae5cd29d0dff54d5c0888d2690b3d58c19`. That pilot is parked on `astra/ff-rust`; its measurements are accepted, its implementation is not the geometry base. Set cwd explicitly and preserve uncommitted work.

This is iteration 1 of **at most 5** in the new geometry allocation. Implement and check the finite-boundary repair described below. This is not another inventory or an instruction to retry the rejected M33 migration with unchanged inputs. Repair the existing provider and its actual consumers. The whole geometry task also owes row identity, no-seed rows, whole-glyph attribution, valid body measurement and continuation consolidation; those do not all have to be completed in this iteration. The next prompt will be written after this result and the independent check, not selected in advance.

The owner's subsequent direct instruction authorises the coordinator's automatic loops under the revised PLAN. This task remains Python geometry. The new order after it is R8-RUST-02, then R8-INK-02, then audit; caps and the 97% runner limit are unchanged. The first iteration still repairs only the finite-boundary dependency and its live consumers. Do not broaden it into every geometry defect, a Python speed campaign or a Rust rewrite.

At handoff, describe this feature's native/explicit evidence, the input/coordinate/support contract, the decision actually removed, all migrated callers, and remaining counterexamples. Identify which computational interfaces are now understood well enough to port and which still depend on unresolved row/glyph attribution. This is a short addition to the existing handoff, not a new architecture framework or an instruction to port anything. A known physical defect may remain an explicit regression control; an undefined input contract may not be called stable. The planner chooses the next geometry iteration after the actual result/check. Rust will later select a substantial stable computation without requiring every ink/source case to be solved.

The owner's objectives, verbatim:

> basically the same code with roughly the same behaviour but more architectonically sound and we would expect it to be actually faster because of the fewer duplicate processes

> to actually try to build or use established tools we have built that are actually modelling features of a page that we can expect to generalize, and make sure that all the heuristics we use are grounded on tehse and not general statistical properties of the images we are processing.

> Doesnt the correction mostly invovle removing things then? and building models that can help verify the existing mechanisms

## Read first; reuse the existing evidence

Read the applicable AGENTS.md, current PLAN/ROSTER/RUST_COMPLETION_PLAN, the two R7 mechanism/methodology reviews, your R8-03-i2 and R8-04-i1 reports, and the following full independent checks:

- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-03-i2_check.md`
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-04-i1_check.md`
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r8/R8-RUST-01-i1_check.md`

Use your existing `.astra/fast_lines/out/round8/R8-03-i2/` DOMAIN_POPULATIONS, FAILURE_CLASSES, NO_SEED_ROWS and REUSE_RECEIPT, and R8-04-i1 runtime/profile evidence. Resolve the exact existing filenames rather than regenerating a general survey. The pilot report and receipts remain readable in `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-rust/`; do not edit that worktree. The coordinator subsequently accepted 953fc4a WITH NOTES and reports private 44/44 identical under both backends. Its report/handoff's pending-acceptance wording is historical.

The pilot measured 1.621× at M17, 2.83–4.01% less correction time and 2.16–3.03% less file-to-final time. It changes no physical result. Three implementations and a build-dependent test suite would complicate geometry work, so this task keeps the checked Python runtime. Rust reintegration, build/test portability and downstream timing diagnosis belong to R8-RUST-02. Do not charge their repair to this geometry allocation.

## 1. Builds on the existing code

The concrete defect is in `prototypes/fast_lines/shared/geometry_page_field.blocks`: accepted rule paths are reduced to median x and appended to the all-height cuts. Their y support is discarded. On c8 p36, the heading at native x 511–2305, y 688–783 spans both columns **above** the rule. The rule's path is roughly y 995–2740; its bilateral termination witnesses are roughly y 1087–2261. Neither supports a division through that heading.

Trace and repair this existing chain:

1. `stack.pipeline.compose` → `stack.geometry.cuts` → `geometry_columns.analyze`. `nominate`, `layout_barriers.fast.verify_rule` / `geometry_feature_rules.curved_rule`, `termination_witness` and `native_crossings` already record path, `y0/y1`, native crossings and bilateral endpoints. Reuse these observations; do not rerun column detection in a new provider. `geometry_columns.apply` already consults finite rule support, although its row-centre rule is not a proof of complete glyph ownership.
2. `geometry_field_detector.run` → M15 `geometry_page_field.render` → `blocks`, then `certify` / `invert_points`. Replace the all-height interpretation of a finite rule with its actual supported extent. Follow what the resulting region and coordinate contracts mean for the renderer; changing the returned rectangles without auditing their consumers is not a complete repair.
3. M17 `geometry_field_detector.unbend/displacement/native_bands/separate_bands`, mapping rectified rows back to native coordinates, and M18 `geometry_field_selection.apply`, called as both early and late `field_replace` in compose. Make the finite-boundary interpretation reach these consumers. Audit region overlap, duplicated proposals and rows meeting the boundary endpoints. Do not lose spanning text by treating each new domain fragment as an independent complete row.
4. Downstream `geometry_envelopes.guided/correct` (`smooth_envelopes` in compose), M20 `geometry_feature_correct.retention_ink/retention` and `geometry_envelopes.owned_retention`, residual recovery, `geometry_rows.native/confirmed_partition`, and `stack_ownership.reconcile`. Keep their useful accepted support while changing the domain input. M33's independent continuation is still required where no supported shared field exists.

Use native finite-rule paths and whole row/glyph crossings as the feature being modelled. Check them against existing `geometry_columns` explicit witnesses and the pixel-seeded slow detector's boundary and row construction. In `greekocr/pages/lines.py`, read `_discover`, `_pool_geometry`, `_assign`, `_make_lines`, `_boundaries`, with `boundaries.py`, `layout.py` and `font.py` where relevant. This is an **offline reference**, not the new live pipeline. Keep `greekocr/` unchanged. Use source/input-matched saved slow renders when available. The slow detector has known sliver rows, a misplaced 4959 row and a dropped Ψ; raw pixels decide discrepancies.

## 2. Inputs match what the code expects

| Consumer | Required input and validity |
|---|---|
| Existing rule/domain code | Native item dictionaries, `(W,H)`, engineering sampling height, and the existing `column_evidence` record. Rule path coordinates and `y0/y1` are native. Accepted means the existing witness accepted that **finite** boundary, not an infinite line. No-rule or rejected-rule pages are not licensed for a new cut. |
| M15 render | Currently consumes native rectangular regions and builds a mesh on them. If representing finite support needs a small extension to this existing contract, migrate all actual consumers together and document it. Do not silently feed polygons/masks into a rectangle API. Account for heading/body transitions, rows crossing endpoint bands and any overlap; do not turn rule endpoints into arbitrary horizontal text cuts. An insufficiently supported heading can remain without a field and retain its existing route. Do not manufacture extra rows to satisfy `len(seeds)` or box-count conditions. |
| M17 transforms | `unbend` returns a crop plus native offset. `native_bands` receives that crop and crop-coordinate rows. `separate_bands` receives its matching ink/labels/stats/owner map. Native y is phase plus `displacement`; native polygons are not rectified polygons. Mapped support must respect the same finite domain used to build its field. |
| M18 and retention | Current native polygons and matching labels; proposal indices are not original Paddle indices. Recompute replacement, ownership and union-retention decisions on changed regions/rows. Compare preservation against accepted **final** support, not just incoming boxes. Keep the NaN inverse and NaN-skipping `certify` consumer test. Missing/undefined fields mean unknown geometry, not blank paper or row 0. |
| Shared preparation | Reuse only the exact unchanged image/ROI/scale/threshold and, where applicable, height/exclusion contract. Recompute polygon membership, B5 anchors/votes, M35's eight-row pool and Footprints on changed rows. Immutable native labels may be shared under their existing contract; the old row census may not. |
| Slow reference | Unmodified `segment_page(gray)` / `prepare_pixels(gray)` supplies rough pixel regions and components. **Never place Paddle polygons in `PixelPage.boxes`**, including padded or regrouped tight line boxes. Slow component IDs and font classes do not become fast IDs by index matching. |

Residual/no-seed rows remain explicit obligations. Keep original Paddle localisations as fast inputs and allow the existing native/residual route to establish rows without original ancestry; never require `source_ids` merely to keep a physically established row. Track whether changed domains alter proposals 34/35 on 8686 p5 and their M18 rejection. Row 5 currently remains unmatched: the proposal spans two rows, the native refinement yielded no valley/piece, and M18 rejects it as unowned. Do not call that fixed because a domain is now finite. Rows 40/41 are present but curled endings partly clipped; p7 “ἀμπέλων” and row 40 already exist.

## 3. Removal and verification scope

**Replace one located wrong policy in the live route:** a finite accepted rule must no longer cut an entire page-height domain. Delete the unconditional median-x/full-height interpretation and its displaced handling; do not retain it as a hidden fallback, add another competing domain detector, or place a new percentage/count guard around it. Reuse the existing rectangular representation where adequate; any necessary contract extension belongs to this provider, not a new page model. Trace all callers, including explicit-region callers, so unsupported domain semantics cannot silently re-enter downstream.

Make a live implementation attempt, run it on the native counterexample and controls, and revise the first concrete contract failure if needed. Do not stop after another description of the already-known bug. Do not force the unruled 9ea/e259 spread or absent-field pages into this repair: those need different observations and remain named debt. Preserve their accepted output. A rule extent is not a new empty-gutter detector.

The later shared continuation must follow the owner's idea, verbatim:

> right but now the whole page bend should be global we dont need to check individual lines right?
>
> so if we know the bend and we have the text-lines' lines we can just follow them to the end of the page in a way
> that does not impose on the other liens

The owner's procedure remains:

> (1) get the line segments as an input
> (2) draw the curves/skew lines and 4 lines for each line in the segment; you then give them the coordinates to seperate their identities
> (3) after you have the curves you have the 4 lines for each text-line you forget the initial line segments completely
> (4) you can draw a new segment simply by finding the middle between the bottom and top lines from neightbouring lines, and by extending left and right along the curve until you find a boundary

A supported page/column domain is a prerequisite to that replacement. This iteration does **not** have to remove M33 globally. Do not repeat its failed migration while 466/d323/dbd have no M15 field, or while 9ea still combines multiple physical domains. Report whether a domain subpolicy was removed separately from the unchanged seven bend authorities. Do not rename a field phase or median component extent as a measured body line.

Required native regression controls, matched by source/polygon lineage rather than mutable final indices:

- c8 p36 spanning “ΚΥΡΙΑΚΗ” heading and its isolated right tick (#87); show the actual finite rule and domains above, within and below it. Retain the tick without inventing its identity.
- 466 p277 #0: retain the accepted “πό-” ending support. The earlier check found the hyphen at the crop edge; do not claim it was already complete.
- 7792 p138 #40: retain terminal punctuation and left-edge support.
- 9ea p202 #131, dbd p359 #25, d323 p138 #23: retain M33's exclusions of the preceding row/letter bottoms. Their incoming boxes are wider and are an inadequate preservation baseline.
- 8686 p5 row 5, rows 40/41 and “ἀποξήρανσίν”; p7 “ἀμπέλων”/row 40 and curled ends. Present, clipped and absent are distinct states.
- All affected finite-rule pages, short headings/numbers, columns/tables, quiet flat/skew pages and two-leaf controls in the existing 23 pilots. Include the known e259 leaf split, 7a2b “32”, Ψ initial and 31f40 weak text as preservation/open-case controls when comparing the slow reference.

Build meaningful tests of the real `blocks`→render/consumer chain: a spanning heading above a finite rule, spanning text below its end, body rows within it, endpoint-crossing support, rejected/no rules and multiple finite rules. Keep supported side-by-side body rows separate while preserving the heading's full support; merely getting the region count right is insufficient. Assert geometry/retention consequences, not your chosen list layout. Demonstrate that restoring the old full-height-cut interpretation makes the targeted test fail. Use a lightweight detector stub for a consumer fixture if appropriate; do not hide the real domain producer behind a stub. Existing NaN and faint-front tests retain their meaning.

For the fast-versus-explicit comparison, overlay the input rule path/y extent, native row/glyph witnesses, slow finite boundary/assigned row and candidate domain/path on the same native crop. Measure false cuts through text outside the rule, crossings within its supported span, support lost/duplicated and unknown geometry. Use pixels to adjudicate; average overlap and final-output equality alone do not establish a physically correct domain. Intended repairs may change polygons. If final output stays unchanged, say whether the real consumer's domain got fixed and leave the owner's crop status unchanged.

## 4. No new pipeline or page model

Use the current default compose route and its existing observations. No from-scratch contact-density model, separate gutter model, universal font/ink provider, new context/cache framework, runtime slow detector, Rust work or production integration. No third renamed variant of a failed assumption, no speck tolerance or new statistical guard to excuse native loss. Focused changes inside the existing domain provider are authorised; replacing the whole detector is not.

Preserve the R8-04 exact work reductions. Keep M06 back-print propagation deleted. M55's centre-only decision, the two DN floors and M35's population-dependent source decision remain G2 debt. Do not import `r8_frame_parts` or its rejected frame caller, revive the falsified local-paper/noise calibration, or claim a universal body-height measurement. Preserve pale 1be6 p215, weak 31f40, 0ce9 ghosts including ambiguous #34/#36 and the strict faint-front xfail. A better crop does not establish the source of 93f8 #5 or 8686 #9/#40 tails. The 0ce9 +200 ms debt remains for target-route consolidation.

## Deliverables and independent check

1. A live finite-boundary provider/consumer repair with the old all-height rule policy removed, or a source-bound rejected implementation and its first failing physical/input assumption. List all migrated callers, exact policy/definition counts and runtime lines added/deleted/net against 54cc8f9 and d5dc3e2. Use existing FEATURE_OWNERSHIP/CONSOLIDATION_DELTA records. Do not call seven bend authorities consolidated because one bug is repaired.
2. Native before/after evidence for c8 and every changed/regression control, with explicit-reference comparison and actual downstream dispositions. Update the existing NO_SEED_ROWS and owner ledgers without dropping original comments/marks or claiming inherited recoveries. Separate the finite-rule repair from remaining missing-field, leaf-domain, row/body and M33 work.
3. The consumer regression/mutation tests and full relevant prototype suite. Run a fresh source-bound 208-page candidate pass once coherent; inspect the 23 pilots and every changed native crop, including changes in exclusions, ownership or source calibration. Record and adjudicate all new text losses/extra rows. The coordinator alone runs the private 44. If no runtime change survives, bind to checked 54cc8f9 receipts instead of rerunning identical OCR.
4. Per-page paired timing in both orders on affected/regression/quiet/slow controls, with full-pass median/p95/max and over-one-second page list. Charge new regions, field construction, rectification, model requests and downstream recomputation. Use this MacBook and the established authorised round-8 runner, same settings and no concurrent benchmarks. The checked Python full pass was 199.421/1287.272/2007.555 ms, 22/208 above 1 s; the parked Rust clocks are not this candidate's baseline. No Python speed target must be met before a valid physical repair, but unexplained cost stays visible.
5. `docs/records/research/round8/REPORT_R8-GEOM-02-i1.md` and `.astra/fast_lines/out/round8/R8-GEOM-02-i1/`, with ITERATION_HANDOFF JSON/Markdown, pinned sources/inputs/model/settings, accepted versus rejected changes, proposed best head, open owner cases, tests/timings, elapsed time and supplied meter. Give the next planner the earliest remaining causal failure, not a self-authored successor prompt. Keep the actual commit/fallback state current and append dated acceptance notes when the coordinator commits a fallback.

The coordinator checks deletion and compatible inputs, actual rule support/whole-text preservation, native overlays, mutation effectiveness, 208 evidence and cost, and conducts its independent review/private44. A useful finite-domain repair can be accepted while **G3 remains PARTIAL**. Full geometry completion still requires its owner row/curl/glyph obligations and displaced-policy removals. If a regression cannot be resolved, withdraw that change, retain any independently valid fix and recommend the best checked head; if none survives, keep 54cc8f9. Do not hide the failure with a crop-specific fallback or declare the entire new allocation failed after one iteration. Remaining authorisation is decided within the five-iteration maximum and the live resource limit.

## Authorisation, resource limit and handoff

The owner, relayed 12 October about 10:40 Athens:

> OK talk with the planner we have adjusted the plan to keep pushing on some of the work
>
> ask them adjust the plan for the latest results, and also to give you the iterations allowed for each of the tasks.
>
> These are the max iterations each of the tasks will have this time.
>
> You coordinate the calles from now on.
>
> Make sure astra planner produces the prompt for every task iteration.

The binding maximum is five geometry iterations, not a forecast or transferable allowance. R8-RUST-01 closed after i1; its unused i2 is retired. About 85% of the weekly meter was reported before this planner turn; check the coordinator's current supplied value. The runner refuses launches at 97%, superseding INFRA's older 95% limit. Reserve roughly two points for closure and reassess around 95% or earlier. There is no arbitrary wall-clock cap, automatic extension or weekly rollover. Budget closure may come before geometry's cap. After your result and independent check, the planner writes the next prompt; do not launch it yourself.

Only the 208 development pages. Never locate, open, run or request the private 44 or their outputs. No PDF-text truth, orientation work, new agents, background jobs, pushes or production edits. Anemi material stays internal. Modify only task prototype/tests/docs/evidence in this worktree; leave `greekocr/` and other worktrees unchanged. Use the established Python environment at `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, with `PYTHONDONTWRITEBYTECODE=1` and pytest cache disabled as needed.

Commit scoped work on `astra/ff-r8-stack`; if staging is blocked, leave `.astra/commit-F8-R8-GEOM-02-i1.sh` with a validated source-bound fallback, not a root-level script. Required trailers:

    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01X3VU3zMmUxSHRDvYfQMczm

Finish in plain words, then `RESULT: DONE|PARTIAL|NOT DONE` naming R8-GEOM-02-i1, commit/fallback, retained repair/deletion, G3 status and best-head recommendation. A complete scoped repair is not a claim that G3 has passed.
