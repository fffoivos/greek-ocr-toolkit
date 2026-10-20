# R8-INK-02 iteration 1 — one authoritative glyph atlas and an honest ink handoff

Fresh worker, thread argument `-`, model `gpt-6.1-sol`, effort `high`, track `ff8-ink`. Worktree `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink`, branch `astra/ff-ink`. Start `<HEAD>` = checked `3605b9276c6885492550ab06777f19c5090b0329` plus the coordinator's FP8al docs merge. The coordinator fast-forwards this worktree from fb03df1 before launch; that head is an ancestor. Verify the supplied head and clean state; do not reset to the old ink worktree's runtime. Record the returned Sol thread ID for later resume. This is i1 of at most three INK iterations; no later prompt or worker launch is authorised here.

Read [SOL_WORKER_HANDOFF.md](../SOL_WORKER_HANDOFF.md). The new thread avoids importing the old ink worker's failed grouping/noise assumptions; its reports and counterexamples remain evidence. This first slot delivers a real atlas-input correction, with callers migrated and the ambiguous old interface removed. It does **not** promise a new source classifier, a frame solution or completed curved endings.

Owner, verbatim:

> Doesnt the correction mostly invovle removing things then? and building models that can help verify the existing mechanisms

> But the whole point of this generation of our model was so that we odnt have to have duplicate checks

> Don't be so pessimistic we are making progress. The only issue is that we should be working with a wider sample

## Read the checked inputs

FL = `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines`; STACK = `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack`. Read these whole checks and their relevant report/handoff records:

- `FL/review_r8/R8-RUST-02-i2_check.md`: current head, runtime equivalence, qualified H, native backend status and closed speed scope. RUST closes PARTIAL at 2/3; i3 is retired. Its profile is a negative speed result, not permission to change field resolution or inference passes.
- `FL/review_r8/R8-02-i2_check.md`, your worktree's `docs/records/research/round8/REPORT_R8-02-i2.md`, and `.astra/fast_lines/out/round8/R8-02-i2/{SUPPORT_HANDOFF,FRAME_PRESERVATION,CUTOFF_CALLERS,FEATURE_OWNERSHIP}` in their existing JSON/Markdown forms. M55's 14/57 explained removals are offline, not runtime providers.
- `FL/review_r8/R8-FONT-03-i2_check.md` for the bounded detached-mark debt and its corrected input-contract diagnosis. Use STACK's saved `R8-FONT-03-i2/FROZEN_22_CENSUS.json` and committed `features_geometry/font_guides_native.{json,npz}` as historical evidence; do not regenerate that 6.9 MB fixture.

Look up M06, M35 and M55 in `FAST_LINES_ROUND7_METHODOLOGY_REVIEW.md` and the mechanism JSON for the existing feature/consumer distinction. Historical `type_ink_*` copies and M06 neighbour propagation are already deleted: do not restore or count them again. No need to reread every old chat or recensus all mechanisms before implementing the concrete contract below.

Current runtime keeps the four R rows, the 3229 p2 B row, the recovered 8686 p5 body and H's supported-extent repair. Normal selectors remain `FAST_LINES_FIELD_BACKEND=python`, `final_export=False`, `bend=False`. The native field batch is a tested off-default experiment. General geometry/CURL are CLOSED PARTIAL; FONT's final slot is parked. No calibrated universal ink mask or measured universal body-height provider exists.

## 1. Builds on the existing code

### Primary implementation: remove the independently supplied atlas/preparation pair

In `shared/ink_photometry.py`, `glyph_atlas(atlas)` currently returns immutable vectors/aspects, but `match_glyphs(query, atlas, prepared=...)` can receive those arrays with a **different** ordered atlas. Matching indices refer to the prepared arrays; `ink_ownership.analyze(detail=True)` dereferences those indices in the separately supplied `atlas` for exemplar boxes. Same length does not establish the same glyphs, order, vectors, aspects or metadata. The current active caller appears to supply a matching pair; no natural false suppression caused by this bug has been demonstrated. Fix the unsafe contract without claiming it caused an observed page error.

Replace this two-source interface with one authoritative, invocation-local atlas observation whose matching arrays and index-to-exemplar data come from the same ordered census. Preserve owned immutable numerical arrays and bind the exemplar bbox/line metadata used in the detailed witness to that order. Prefer removing the possibility of supplying incompatible objects over scanning or hashing all glyph vectors again for every query. Choose the smallest existing-style representation that enforces this; no general page-context class, global registry or content cache.

Migrate the actual producer/consumer chain:

- `ink_ownership.analyze`: select current anchor glyphs, prepare once, match all current requested regions, and obtain detail witnesses from that same observation. A returned `direct_id`/`reflected_id` must identify exactly the exemplar whose vector/aspect was scored.
- `features_ink.pipeline.ink_run` calls that provider after separators. Do not substitute its standalone `run`, which applies separators again.
- `type_recovery.run` and `type_residual_recovery.recover` call the same `analyze` with their current `items` and requested regions; recovery's completion refresh can call it again on new geometry. `type_context.recover` and `type_extended.recover` transport exact native observations, not stale source decisions.
- Migrate other `match_glyphs`/`glyph_atlas` call sites found by repository search, including `features_ink/test_features.py`, `shared/test_r8_ink.py`, `shared/test_speed_observations.py` and `evidence/r8_ink_audit.py`. Offline callers may prepare at their own call boundary; they must not retain a second inconsistent interface. Keep source/vote policies in `analyze`, not in a matching bridge.

Delete the old mismatched `prepared=` route and replace the circular changed-membership test (which currently rebuilds preparation before checking it). Record the deleted signature/branches, migrated callers and net runtime lines. A small immutable observation can be architecturally justified even if line count rises; call it an input-authority removal, not removal of an ink/source policy or a reduction in the historical 6/9/9/7 definitions. Do not add a validator alongside two still-independent authoritative representations and call that consolidation.

### Carry the physical ink debt accurately; do not restart its failed models

After the contract repair, make a compact per-case readiness handoff from **existing** native evidence and current caller binding. Do not turn this into a fresh universal ink inventory or a second implementation target in this slot:

- M55 `ink_frame_field.render/chain/trace` measures repeated border units; `exclude_whole` still removes using observed body-bbox centres. The offline grouped-unit attempt explained 14 of 57 approved removals; of 43 returns, 19 fail on ≤10 unresolved pixels, seven on one pixel, only five on large residuals. Distinguish unexplained joined/corner units from unresolved specks. No unsupported speck waiver or `r8_frame_parts` import. State what existing physical witness could justify a later caller replacement and what is missing.
- M35 `ink_faintness.components/reference/classify/analyze` remains a photometric source proxy with a census-dependent pool. On 0ce9 it alone excludes the 15 ghosts formerly handled by propagation; #34/#36 contain faint forward-reading fragments. Deeper-leaf show-through is an inference, not a certified source label. Preserve those outputs and record the population, not a new calibration variant.
- The specific `ἐξόδων` breathing at native `[1776,1074,1779,1078]` on 8686 p5 is a bounded mark/body question. Compare its **input readiness** with the 22 FONT controls. FONT i2 proposed 11 correct owners across seven pages/four books, but its bodies-only adapter starved detached-accent evidence; a later export also created slivers. The λ fused-neck defect is real but secondary. The checker's “undisputed marks” probe is not a qualified provider. Do not import it, select an owner by every pixel's nearest phase, or reopen FONT/geometry in i1. Explicitly name any guide/row dependency that would prevent a later INK consumer.

Keep source attribution, attachment to a text row and crop extent as different questions. An answer to one does not certify the others. Existing mixed endpoints 93f8 #5 and 8686 p26 #9/#40 have unresolved tails; their crop repair remains geometry backlog, not an instruction to infer a source from darkness.

## 2. Inputs match what that code expects

`glyph_pixels` observes the immutable uint8 native image, its exact clipped ROI and threshold; its labels/stats and fixed normalised tiles are height-independent. Preserve that sharing contract. `glyphs` still makes fresh height/area/limit selections and caller-owned mutable records. `height` is the existing bbox-height engineering proxy, not a newly measured x-height.

An atlas belongs to **one selected ordered glyph census**. A snapshot remains stable when its source list, vectors, aspects, bbox or line metadata are later mutated; a new call with a changed census constructs a fresh snapshot. Reordering or same-length replacement must not reinterpret old score indices. Query order is independent and preserved. Keep the 22×22 normalisation, float dtypes, reflected orientation, aspect comparison, first-argmax ties, scores, margins and empty-input behaviour. No recalibration of `.70`, `.80`, `.08`, `.22`, anchor counts or vote thresholds to make a test pass.

Recompute B5 anchors/votes and M35's eight-row pool whenever their census changes. Share only native observations under identical image, ROI, scale, threshold and exclusion state; do not reuse field preparation made on an exclusion-filled copy as original-page ink. Prepared glyph metadata is not a row-ownership cache. A `suppress_indices` value indexes the requested regions, not necessarily the original items. Use each actual caller's coordinate frame and index space in receipts.

For frame evidence, `render` takes polygon arrays and `exclude_whole` takes item dictionaries plus `FrameInk`; perimeter bands are not ownership of the frame interior. Do not use M35's selected body list as a complete ink census. For mark evidence, the old slow `font.evidence` expects the full owned component set in its own frame; body-only input is not that contract. `greekocr/` remains read-only, and Paddle polygons never become `PixelPage.boxes` for the slow reference.

## 3. Removal and verification scope

### Freeze a wider atlas-call cohort before editing

Use the 208 non-appendix page identities in STACK's `R8-RUST-02-i1/TIMING_PER_PAGE.json` and saved `.astra/fast_lines/out/round8/R8-RUST-02-i1/same-input/H/*.evidence.json`. Bind reuse to the accepted H-equivalent runtime; current source equivalence is documented in RUST i2. Freeze `INK02_COHORT.json`, with input/evidence hashes and group roles, by this rule:

1. Include **every** development page whose saved evidence contains a B5 observation (`version == 'B5'`) with `atlas_glyphs > 0`, at any ink, type, residual or completion-refresh caller. Record each JSON path and caller; do not assume the six historical reuse pages are the whole active population.
2. For each represented book, include its lexicographically first other development page with no active atlas, where available. Record books with no such negative, not substitutions.
3. Include the named controls already in the 208: 0ce9 p1; 93f8 p1; 8686 p5/p7/p26; 31f40 p1; 1be6 p215; 3229 p2; 4959 p5. Resolve exact IDs against that frozen inventory. Preserve the whole 208 denominator even where no atlas runs.

This is an exposed development cohort, not new held-out validation. Historical frame57, FONT22 and mixed-endpoint records are separate, immutable debt ledgers; do not merge their differing denominators. The frozen 22-page owner appendix from Rust remains a separate internal development parity check if the changed atlas has consumers there. Never read private 44 or fieldview's mixed/heldout inventory.

### Tests must fail on the real defect

Commit small tests through the actual factory → `match_glyphs` → `ink_ownership.analyze(detail=True)` consumer, including at least one native asymmetric-glyph fixture with independently identifiable exemplars. Reuse existing native fixtures where possible; no second large fixture pack and no tests dependent on ignored `.astra` captures.

Exercise same-length replacement, reordered membership, duplicate/symmetric exemplars and ties, vector/aspect mutation, bbox/line mutation, empty atlas/query and multiple requested regions. Prove both score identity and the actual returned native exemplar bbox. Check any internal line identity against the same ordered observation; preserve the external evidence schema, without requiring a new exported line field. A mutation that reintroduces independent old arrays/current metadata must fail these physical witness assertions; merely asserting arrays are read-only is insufficient. Restoring the old duplicate-array preparation inside the per-query loop must fail an operation-count test at the real B5 caller. Do not introduce a contrived classifier threshold to obtain a desired witness.

Build the atlas once per `analyze` invocation when used; preserve current fresh preparation after changed selection. Test producer immutability and no aliasing, including in-place changes to raw glyph dicts. If legacy input compatibility is required, normalise it once into the same single authority; do not keep the unsafe paired-input escape hatch. Native optional-extension collection must remain intact, but untouched Rust kernels need no new speed experiment.

Run the relevant suite and bare-checkout suite. Capture current B5 calls on the frozen cohort: fresh versus refactored arrays, scores, exemplar references, anchor identities, suspect populations, votes, classifications and suppressions must agree. On representative real direct/reflected/unknown cases, render native query/exemplar witnesses and compare against the existing dense `analyze(route='dense', detail=True)` observation. Dense uses a different sample budget, so record its disagreements rather than forcing equality or using it as ground truth. Agreement with itself does not validate source identity.

Then run the full 208 comparison at the final source, plus the separate owner22 appendix if runtime consumers occur there. This is a contract refactor: **no intended polygon/mask, source/exclusion or non-clock decision changes**. Investigate any difference; do not promote a newly changed source decision under this prompt. Preserve `ἀποξήρανσίν`, pale/weak front text, 0ce9 exclusions and the recovered A/R/B rows. Do not remove applicable strict xfails simply because exported crops are equal. Final `crop_mask` support, not only polygon vertices, establishes retained ink.

### Cost and scope

Keep the accepted preparation and fixed-tile savings. Show actual atlas builds and glyph/CC/resize work per caller before/after; there must be no per-query full-atlas hashing, rebuilding or new image pass. Pair the affected cohort in both orders with fixed repetitions and unchanged detector controls on the established MacBook runner, sequentially. Include unchanged/no-atlas pages and 0ce9. Require no reproducible affected-stage/page regression; report bounds of timing noise honestly. Full 208-page census timing remains descriptive if load invalidates a paired claim. A correct input contract is progress even without a speed gain, but added repeated work needs repair before retention.

The old mean-paper/bright-neighbour independent-noise estimator was falsified on structured blank regions; no renamed retry, tuned floor, speck-count allowance or size/brightness exception. DN floors remain unresolved. M20 retention ablation lost `ἀποξήρανσίν`; do not retry or restore M06 neighbour propagation. No arbitrary collapse of source, faintness and text membership into a single brightness measurement.

## 4. No new pipeline or page model

Use the existing shared ink provider and its current callers. No new source-separation pipeline, font model, row detector, field-band crop, curvature gate, seam/reconcile repair, Rust port, production `greekocr` change or broad repository reorganisation. The atlas observation is a local value with one lifetime, not a common-page framework or another source authority.

Two owner decisions are pending and **not allocated here**: field-band crop construction/flat/binding-side work; and whether to authorise field-path algorithm changes such as lower working resolution or fewer passes for speed, with separate quality gates. No owner answer has arrived. Do not change resolution, inference requests or passes, or quietly implement the exact-density-domain/list-conversion speed backlog. Those items belong to AUDIT's recorded backlog pending a future implementation allocation. The Rust unused slot is retired, not yours. FONT remains parked.

## What counts as progress and the handoff

Preset i1 completion is **the atlas contract**, not the whole INK task: the inconsistent paired interface is gone, all live and offline callers are migrated, adversarial real-consumer tests discriminate it, correct-call outputs and current text/source decisions are preserved, and preparation remains once per current census with acceptable cost. Report it as retained architectural/correctness progress. No natural text improvement or physically validated source policy should be claimed from equality alone.

For each frozen cohort page show caller reach, witnessed native feature, unchanged/changed/unknown decisions and cost. For the inherited frame57, FONT22, mixed endpoints and CURL mark, report the existing explicit observation, first missing physical fact and the current actual consumer separately. Reuse already inspected evidence; add a new native check only where current inputs differ or the specific missing fact can be resolved. If a promising mark still requires unqualified guides or geometry export, say so without reopening the parked task. This handoff lets Astra choose one bounded physical target for i2 from evidence; it does not pre-authorise it.

Deliver `REPORT_R8-INK-02-i1.md` and `.astra/fast_lines/out/round8/R8-INK-02-i1/` with `INK02_COHORT.json`, input/atlas contract, caller/deletion map, committed-fixture provenance and mutations, per-case native witness comparisons, source-bound 208/appendix parity, raw both-order timing, `PHYSICAL_DEBT_READINESS.json/.md` and `ITERATION_HANDOFF.json/.md`. Keep O08/O09/O11/O12/O17–O24 and row marks open unless an actual independently checked fix exists. Update historical commit status only with dated addenda; do not rewrite receipts.

If runtime changes, coordinator alone compares checked3605b92 and the frozen candidate on all private 44: **whole-page segmentation, every actual line strip and actual-mask coverage maps for both**, source/row/exclusion identities, lost/foreign/duplicated ink and paired stage/correction/file-to-final cost. Retain the recovered private body. Identical exports may reuse their visuals with an equality receipt. No private rerun is needed for source-equivalent docs/tests-only results. Worker sees aggregates, never private pages; owner-exposed cases are development-retest. Private disagreement blocks this candidate; no tuning on those pages.

After result and full independent check, Astra writes i2 or closes early if appropriate. Maximum remains three; at the cap carry the best checked compatible subset to AUDIT and name every unresolved source/frame/mark dependency. Do not self-launch or pre-write i2. Meter 15% reported, no 14 October daily cap, standing 97% launch/99% run safeguards remain. No background jobs or subagents. Use the established MacBook runner for authorised development qualification only.

Commit scoped changes with the required single trailer block. If Git is blocked, leave an executable `.astra/commit-F8-R8-INK-02-i1.sh` with a correct shebang, source/hash validation and a **bare invocation that commits**; optional `--check` validates only. The coordinator now executes an executable fallback directly, but prefer a simple shell wrapper to avoid runner ambiguity. No push. Finish in plain words, then `RESULT: <DONE|PARTIAL|NOT DONE> <one line>`.
