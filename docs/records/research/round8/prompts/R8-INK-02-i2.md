# R8-INK-02 iteration 2 — audit what faintness actually removes

Resume Sol thread **01a13bcd-9d33-7572-b942-0c308fe17d06**, `gpt-6.1-sol`, effort `high`, track `ff8-ink`. Worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink`, branch `astra/ff-ink`. Start `<HEAD>` = checked **603fbf1076019a2aa15406f94d7415e7a595bf41** plus the coordinator's FP8am docs merge. Verify the supplied head and clean state. This is i2 of at most three INK iterations. Read [SOL_WORKER_HANDOFF.md](../SOL_WORKER_HANDOFF.md); do not write or launch i3.

Owner, verbatim:

> Doesnt the correction mostly invovle removing things then? and building models that can help verify the existing mechanisms

> But the whole point of this generation of our model was so that we odnt have to have duplicate checks

> Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample

**Primary deliverable: a native, per-removal account of all 153 M35 exclusions on 34 development pages.** Determine what is being removed and whether any is current-leaf text. The atlas input contract is retained and is useful verification infrastructure; it does not itself certify physical ink sources. Do not spend this slot on another atlas refactor or a new source classifier. A runtime source correction is conditional on a demonstrated loss and an already available, physically discriminating witness, as below.

## Read the checked inputs

FL = `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines`. Read **all** of `FL/review_r8/R8-INK-02-i1_check.md`, your `REPORT_R8-INK-02-i1.md`, and `.astra/fast_lines/out/round8/R8-INK-02-i1/` records `INK02_COHORT`, `PARITY208`, `CALLER_DELETION_MAP`, `PHYSICAL_DEBT_READINESS` and `ITERATION_HANDOFF` in their existing forms. Use the check's scratch `check_ink02_i1/` for the known disagreement and breathing-mask evidence. Read the earlier `R8-02-i1_check.md` / `R8-02-i2_check.md` where needed to bind 0ce9 #34/#36 and the 15 transferred exclusions by native coordinates, not by reused ordinal labels.

I1 is ACCEPT WITH NOTES at 603fbf1: 208/208 exports, 15,094 items, all masks/coverage/source exclusions unchanged; 421 passed / 15 strict xfails, bare 420 / one older skip / 15. Coordinator reports 44/44 private pages identical, correction median +0.7 ms against detector +0.9 ms: no speed claim. The contract removed independently supplied atlas/prepared authorities; historical physical definition counts remain 6/9/9/7 and DN policies 2/2.

Two corrections override older prose:

- **ἐξόδων's breathing is already correct in the default output**: all 20 native pixels at `[1776,1074,1779,1078]` are in 8686 p5 strip #33 and none in #35 above. Preserve it as a negative control; the unresolved ownership issue belongs only to withdrawn CURL B. Do not create an attachment task for it.
- **ἀποξήρανσίν on 8686 p5 must remain retained, not excluded.** The check's last recommendation accidentally groups this front word with exclusions. The 15 inherited 0ce9 ghost exclusions must remain excluded. Do not turn the earlier M20 word-loss counterexample into the opposite requirement.

## 1. Builds on the existing code

### Audit the real M35 consumer and compare its existing explicit observation

Use `shared/ink_faintness.py:components`, `reference`, `normal_run`, `classify`, `render`, `analyze` and `ink_faint_scout.render`. `stack/pipeline.compose` calls `relative_faintness` after `smooth_envelopes` on `shapes['items']`, records `removed` with `removal='relative faintness'`, then calls it on changed final footprints after `split_rows` / `reconcile_rows`. Its `refresh_export` also has a call, but that is off-default with `final_export=False`. Trace which actual invocation produced each exclusion. The final removal ledger is the population; repeated observations of one polygon are not extra removals.

M35 observes component tone, stroke, clipping and repeated normal adjacency relative to a sampled page pool. These are measurable ink features, but **faintness is not a certified front/back source**. `ownership_evidence` currently checks image size only; it does not reconcile B5 votes with M35. Report this interface honestly.

Use the native slow `components(..., route='slow')` on each removed footprint and its call's actual calibration strips, at the same supplied height, to inspect paper/ink, body eligibility and normal-run witnesses against the fast `route='localized'` observation. Record disagreements without retuning either. On the known B5-front conflict, any suspected front loss, and representative reflected/blank/retained-front controls, also run the existing full `render(..., route='slow')` on that invocation's complete item census. Its all-row reference differs from the fast eight-strip reference: distinguish observation error from population/reference change. Neither renderer is ground truth for which leaf the ink comes from. No replacement noise or calibration model.

### Use B5 as independent diagnostic evidence, not an automatic veto

Reuse `ink_ownership.analyze(..., regions=..., detail=True)` and the qualified `ink_photometry.glyph_atlas` / `match_glyphs` observation. Record original live B5 decisions where they bind the same footprint. Separately, batch an **offline** B5 observation for the removed ROIs using the actual current item pool at the responsible M35 call; label that diagnostic invocation, rather than pretending the pipeline had already consumed it. No per-removal atlas rebuild. Compare query glyphs with their returned ordinary/reflected native exemplars and keep uninformative/unknown results.

The known conflict is 0ce9 p1 `[1757,2644,2244,2697]`: B5 front 4 / back 0, yet M35 drops it. The checker could not read it and only tentatively associates it with #34/#36. Resolve that mapping from pixels. A forward-reading ghost from another leaf can also match ordinary glyphs; **B5 front does not prove current-leaf text**, and unknown does not prove blank paper. Do not restore all B5-front removals by fiat.

### Finish the small i1 contract and accounting notes

Reuse the existing `GlyphAtlas`, factory and native test fixture. Validate compatible array/metadata lengths and shapes once at construction (including the current empty representation); pin float32 vectors and float64 aspects; explicitly reject raw-list matcher input, including an empty list. Keep frozen owned metadata and expose read-only arrays through read-only views of their private base so ordinary `setflags(write=True)` cannot reopen them. Check that ordinary construction/replacement cannot introduce structurally mismatched parts. Preserve factory-only binding of array order to exemplar order; a same-length `dataclasses.replace` metadata edit is not a valid new observation. Use a small sealed construction interface if needed, not hashes or a second validator in every query. This is a normal API contract, not protection against arbitrary Python introspection.

Commit the dtype/rejection/structural tests and mutations through real matcher/detail consumers, retaining the original order/alias/build-count tests. All valid-call outputs and work counts must be unchanged. Record any deliberate-misuse limitation explicitly; it is not a reason to postpone the physical audit.

Correct the B5 caller map: `features_ink.pipeline.ink_run`, `type_recovery.run`, **both** `type_residual_recovery.recover` calls, and `compose.refresh_children` / `refresh_export`. The two i1 inventories both counted 254 but missed different atlas-0 calls (3229 p2 completion refresh versus 4959 p5 second residual). Match call identities, input pools, ROIs and evidence paths, not just totals. Keep off-default reach distinct. Add dated 603fbf1 commit/correction addenda to i1 report/handoff; preserve historical receipts.

## 2. Inputs match what that code expects

Use immutable original native uint8 grayscale, native polygon coordinates and the actual item dictionary, including `final_band` where present; `crop_mask` defines selected pixels. Do not substitute a bbox rectangle, an exclusion-filled field image, a contrast-enhanced display, or the final surviving items for the pre-removal census. `selected_indices` indexes the current M35 pool and narrows nominees; the reference still draws from that whole pool. Capture the supplied height, scout ordering, eight sampled indices/strips, component fields and selected-index mapping. Do not infer x-height from the engineering height proxy.

B5 `suppress_indices` indexes **requested regions**, not necessarily item indices. Preserve its route, anchor selection, thresholds, query order, 22×22 normalisation, float dtypes and tie semantics. A new census rebuilds anchors/atlas/votes; a changed M35 pool rebuilds its reference. Existing sharing stays restricted to unchanged image, exact ROI, scale/threshold and exclusion state. No source label is cached in glyph pixels or tiles.

Native and slow-render diagnostics use the same input contract and identify their different sampling/reference scopes. Contrast-stretched or reflected panels are display aids with labels; original pixels determine the finding. No OCR recognition, inferred transcription or template vote alone becomes a source label. Unreadable or mixed support remains explicitly uncertain.

## 3. Removal and verification scope

### Freeze the whole removal population before a source change

Create `M35_REMOVALS.json` from i1's accepted `candidate208` evidence, bound to 603fbf1 and the original `INK02_COHORT.json` 208-page inventory. Include **every** final `relative faintness` exclusion: expected 153 records on 34 pages. Preserve repeated-record multiplicity and separately identify any equal polygon masks; explain any count discrepancy before interpreting results. Each stable ID binds page/input hash, exact polygon and mask hash, removal index, originating call/stage and its pool/ROI/index contract. Do not select only s2 pages or only 0ce9; Anemi development cases in this inventory are allowed. Private44 and fieldview's mixed/private inventory are not.

Keep i1's 59-page atlas cohort and its role labels unchanged. Add the full M35 population as a separately frozen audit population, not a replacement or claimed held-out set. Include retained controls ἀποξήρανσίν, pale 1be6 p215, weak 31f40 p1, the breathing above, A/R/B/H gains and the 0ce9 21 removals (including the 15 inherited ghosts and #34/#36). Preserve the prior FRAME57 and FONT22 ledgers without mixing denominators or importing their unqualified models.

### Every removal gets native evidence and a reasoned disposition

Produce an indexed panel and machine-readable record for **153/153**, with native surrounding rows/page location; original and clearly labelled enhanced views; actual removed mask; B5 votes and native query/exemplar witnesses; and M35 reference, body/normal/strong/clipped counts, normal-run boxes, isolated-normal-ink/short-ambiguity fields and drop reason. Inspect the panels; a generated contact sheet alone is not adjudication. Zoom original pixels for conflicts and suspected text loss. No need to render all atlas exemplars or a new multi-gigabyte fixture pack.

Record independent axes: observed ordinary/reflected/unclear handedness, text/blank/mixed support, and current-leaf/non-front/unknown source with confidence and evidence. Summarise reflected corroborated, faint forward-reading, blank/noise, confirmed current-leaf text loss, **unknown and mixed**. Do not force every case into a confident class. Every B5-front/M35-drop conflict needs a disposition: demonstrated error, explained non-front evidence, or a bounded unresolved source question with the missing observation named. Uncertainty is not a resolved source label. Give exact page IDs and native support for every confirmed loss; distinguish “zero confirmed” from “proved zero”.

Use panels from the whole 34-page population, not only the known contradiction, to test any proposed physical discriminator. Same-page reference composition may explain a removal without proving its source. Include the retained faint-front controls to avoid validating a remover only on what it chose to drop.

### Runtime change is conditional, and must remove a wrong decision

First complete the census and physical adjudication. If a current-leaf loss is independently witnessed **and an existing physical witness already separates it from the negative controls**, a bounded replacement of that wrong M35 decision is within this iteration. State the falsified assumption, exact old branch displaced, actual current-census consumer and native counterexample before changing it. Use an existing decision/observation through its current valid contract; do not add a blanket B5-front guard, another source pipeline or a second full-page B5 pass to every page. The offline diagnostic is not a new mandatory runtime check.

Require final restoration of the witnessed whole text, no changed unrelated source/exclusion decision, and no new ghost, mark loss or crop regression on the full 208. Preserve all 15 inherited 0ce9 exclusions; faint forward-reading cases are mandatory adversarial controls. If the audit contradicts an inherited control label, document that conflict rather than forcing the label or changing its output without a qualified decision. If the available witness cannot separate the cases, keep M35 unchanged and deliver the audited uncertainty/counterexamples to Astra for i3. Do not invent a brightness/size/vote threshold or silently relax a negative to obtain a runtime gain. The audit can establish a real limitation without proving a replacement.

For a source change, commit small native tests at the actual analyze/classify → compose removal consumer with independently inspected expected support. Reinstating the old wrong decision must fail a returned-mask/text-preservation assertion; a always-preserve mutation must fail the witnessed exclusion control. Use current fixtures where possible, with a small justified addition if necessary, and verify tests run from a bare archive. Keep strict xfails unless the actual physical assertion now passes. Atlas hardening gets valid-call parity and the targeted surviving-mutant tests; it is not physical source progress.

### Qualify the final source without extra repeated work

Run the relevant and bare suites, then the final-source 208 comparison with polygons, actual crop masks/coverage, items, exclusions and non-clock decisions. Atlas-only changes require complete equality. Any qualified source change gets a complete exception ledger; everything else equals 603fbf1. Audit-only files must not be imported by runtime. Keep B5 atlas-build/glyph/CC/resize counts and current M35 work unchanged unless a measured replacement justifies a stated difference.

Use the established MacBook runner, sequentially, without profiling/render instrumentation in clocks. Prespecify both-order repetitions on affected pages plus no-atlas/unchanged controls and 0ce9; detector drift over 5% invalidates a timing claim. Report per-stage and per-page costs, repeat spans and any repeat in both orders; no rerun-until-pass or speed claim from noise. Do not benchmark the expensive offline panel/slow audit as default runtime. Require no reproducible introduced runtime regression; record inherited >1 s debt separately.

## 4. No new pipeline or page model

Stay in the existing M35/B5 providers, a small atlas-construction fix, their existing callers/tests, and offline evidence. No FONT restart, row/mark attachment algorithm, M55 frame-parts promotion, independent-noise recalibration, DN-floor tuning, M20 ablation, M06 neighbour propagation, seam/reconcile/curl work, Rust, or production `greekocr` edits. Paddle polygons never become `PixelPage.boxes`. M55 centre-only and unresolved tails remain recorded debt, not surprise second targets.

**Both owner questions remain pending and unallocated:** field-band crop/flat/binding-side work; and field-path resolution or pass changes for speed. Do not allocate or implement either. Exact density-domain and audit-list speed hypotheses stay backlog too. FONT is parked, RUST closed PARTIAL at 2/3 with i3 retired, general geometry closed PARTIAL. Keep default Python backend, `final_export=False`, `bend=False`.

## What counts as progress and what returns to the planner

I2's preset result is the complete, source-bound physical audit: 153/153 reviewed records/panels across 34 pages; every B5-front conflict explained or explicitly unresolved; confirmed loss count with actual native witnesses; retained-front/ghost controls; and honest separation of physical evidence, unknown source, contract hardening and any qualified text correction. Counts of panels alone are not physical certification. A documented source limitation is useful progress; it is not a text gain or a removed policy. A genuine retained correction is stronger progress, but is not required when the existing witnesses do not justify one.

Report per page and case, not just aggregate parity. Ask the independent checker to assess whether the physical source question narrowed, what evidence can be reused, what first assumption remains unsupported, and whether a non-empty safe correction population exists. No indefinite atlas-only work. Recommend one bounded i3 target from this audit, or early closure if none is justified; **Astra writes its prompt after the check**, and the maximum stays three. Do not pre-write it.

Deliver `REPORT_R8-INK-02-i2.md` and `.astra/fast_lines/out/round8/R8-INK-02-i2/`: `M35_REMOVALS.json/.md`, panel index, `SOURCE_DISAGREEMENTS.json/.md`, slow/fast input and observation comparison, caller-identity correction, atlas tests/mutations, per-page results and any deletion map, final source-bound 208 parity/exception ledger, raw timing and noise record, `ITERATION_HANDOFF.json/.md`. Preserve all unresolved owner ledgers; don't call them fixed through equality. Add dated corrections to i1 commit and breathing prose, not rewrites of archived evidence.

For any changed frozen runtime, coordinator alone compares **603fbf1 versus candidate on private44**: whole-page segmentation, **every actual line strip**, actual-mask **coverage maps** for both; text/support/source/exclusion identities and paired correction/stage/file-to-final cost. Review every changed crop, particularly restored text versus newly returned ghosts. Identical visuals may be reused with an equality receipt. Source-equivalent offline/tests-only work needs no private rerun. You receive aggregates, never those pages; owner exposure becomes development-retest. Private failures block promotion, not permission to tune on them.

Meter 15% reported; no 14 October daily cap. Honour standing 97% launch / 99% run safeguards and any live stop signal, checkpointing rather than bypassing. No background jobs, subagents, pushes or later launches. Commit only your scoped changes with the required repository trailer block. If staging is blocked, leave an executable, source/head/hash-bound fallback under `.astra/`, with a correct shebang and **bare invocation** (optional `--check`); the runner executes it directly. Record exact current commit status and append the runner's commit when known. Final: plain words, then `RESULT: <DONE|PARTIAL|NOT DONE> <one line>`.
