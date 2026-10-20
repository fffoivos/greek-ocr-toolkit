# N1-C implementation and blocked rendering receipt

N1-C is **not ready for a reading run**. The renderer, exact symbol localiser, pack builder, closure adapter and answer mapper are implemented and fixture-tested. All 600 step1 geometry records have been produced, but all 600 crop regenerations failed the required byte hash check. No substitute crops were used. No real pack, approved-control file, reader run or classification was created.

The step1 results are **558 ok, 0 no_symbols, 42 misaligned**. Misalignment reasons: 28 digit boxes outside the crop, 13 label/text disagreements, and 1 reversed digit-box order. `crop_unavailable` is an independent flag and is true for all 600 slots, including the 558 with usable symbol geometry. Pixel measurements and rendered images consequently remain absent. These are geometry results, not printed-glyph judgments.

The localiser uses the W1 `docai_line_index` to select a line in its retained Google response, compares the anchored line exactly with W1 text/label, and uses single-character symbol anchors for the flanking digits. Page boxes are translated by `crop_bbox`; no approximate text matching or guessed digit boxes are used. Boundary gaps use the adjacent symbol on that same line, or the specified 1.5 digit-width extent. The line renderer preserves all original pixels and draws triangles entirely in added margins. Zooms have 30% digit-height white padding and 3× Lanczos scaling. The side record uses `greekocr.glyphs.components.line_glyphs` for intersecting ink components and keeps band-relative component measurements private.

Control selection used seed `20261017:N1C:ctrl` and excluded all step1 documents, reserved documents, and C1 line ids. The available pools under the existing numeric grammar were: 1,454 thousands dots, 30 decimal commas, **13 range hyphens**, 16 remaining inner hyphens and 17,627 empty inner gaps. The requested 24 range controls cannot be drawn from that pool without changing eligibility or grammar. An additional metadata-only adjacent-group range check found only 15 ascending pairs and was not used to change the existing grammar.

`artifacts/n1/controls/candidates.jsonl` contains **85 distinct metadata candidates**: 24 / 24 / 13 / 12 / 12 in the requested category order. They are not approved controls: 70 have ok geometry, 15 are misaligned, and all 85 have unavailable crops. Missing image paths and hashes are explicitly null. `controls/rejected.jsonl` records their failures. The 11-slot range shortfall is retained rather than filled with duplicates or another category.

The three C1 cards yield five separator reference slots. `elstat--c5f7ea1f26d39839--s000-l0367` is itself in the reserved line list; `assert_fit_rows` refused it, and it was never decoded or rendered. The four slots on the other two cards failed crop regeneration. Their reference-only status and failures are in `controls/c1_references.jsonl`; none entered the control census.

**Contact sheet paths: none produced.** The requested destination exists at `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/`. There are no real images to put on sheets. No rendered real slot was opened and no glyph was classified.

A representative byte mismatch is in `artifacts/n1/N1C_CROP_DIAGNOSTIC.json`: expected `7f183ddd4303f2868f3de8e2102e53c2e79250210948f875f5e327f9d4408e9b`, regenerated `108147b8f9b07d42f524dd70a5481e8314f9d836c173134db722603ed2fc786a`. The retained source hash passed. This does not establish the cause of the mismatch. Pillow is 10.4.0 and zlib is 1.2.12 in the prescribed x86 interpreter. Its default user-site SciPy is arm64; image work used `-s` to select the installed x86 SciPy 1.12.0. Neither environment nor collector inputs were modified.

The pack builder requires explicit `slot_id`/`truth` approvals, refuses reserved ids and missing renders, uses seed `20261017:N1-1`, distributes at most 86 bed slots plus about 10% controls per context, and writes only the four prompt fields. Options have all eight meanings, independently permuted onto A–H. Images are re-encoded as metadata-free RGB PNGs with content-hash filenames, without links. Keys are written under `artifacts/n1/keys/`; manifests are beside each `r1` folder. The existing `scripts/secondary/reading/scan_packs.py` was reused unchanged through `n1_pack_closure.py`, which adapts the two N1 image fields and validates the N1 public schema. No scanner was duplicated.

`--calibration` builds exactly one controls-only context (maximum 100), with the same checks. Calibration **mode** passes fixture testing; no actual calibration or prompt qualification took place. Normal and calibration builds require an empty output root, so they must use separate roots when both are retained. The normal CLI uses the requested scratchpad `sol_packs/n1` root. It was not run on the real bed. Existing bad geometry or unavailable crops make the real build fail closed.

The mapper returns option meanings joined with geometry, measurement reference and Google glyph, counts control errors, and marks every result in a context `VOID` above one control error. Missing, duplicate and invalid answers remain unresolved; unreadable stays a distinct meaning. Unexpected answer ids are reported.

Validation: **45 tests passed** (16 new tests plus 29 existing tokenizer/lock tests). The new tests comprise 7 localiser/lock tests, 3 mapper tests and 6 renderer/builder tests. Thus builder/renderer plus mapper: **9 passed**. Tests include a 30-fake-bed-slot pack with planted fixture controls and successful reused closure scan, a rejected injected extra file, calibration-only closure, metadata stripping, preserved original pixels under both markers, crop mismatch refusal, reserved-id refusal and missing-render refusal. `artifacts/n1/N1C_TESTS.json` records exact commands and results. Pure-text tests used `python3 -m pytest --noconftest -q`; image tests used the prescribed x86 Python with `-B -s` and appended the pure-Python pytest package path after system packages.

No network, `.git` writes, `run.lock` access, collector-root writes, reader runs, prompt edits or locked-eval rendering occurred. Frame/lock inputs remain unchanged; hashes and all deliverables are bound in `artifacts/n1/N1C_RECEIPT.json`. No live usage probe was run under network OFF.

To finish real rendering, the lead needs a crop-regeneration environment/recipe that reproduces the frozen hashes, a decision on the range-control pool shortfall, and an eligible replacement or explicit resolution of the reserved C1 reference conflict. This report does not authorize changing any lock, frame, crop hash or collector input.


## N1-Cb

**Ready for lead control review: 558/558 usable step1 slots rendered, 0 crop_unavailable; 94 rendered control candidates on eight sheets plus one C1 reference sheet.** All 623 unique line crops matched their frozen SHA256s. Crop checks include the original 85 control candidates (even the 15 dropped for geometry), selected replacements and the two eligible C1 cards. `controls/crop_checks_v2.jsonl` lists every check; the unavailable list is empty. `ensure_crop` always received a shallow row copy whose `crop` pointed into scratchpad `n1_cache/crops/`; no substitute bytes or hashes were used.

Collector invocation: `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, arm64, Python 3.11.3, Pillow 12.3.0. Its resolved `sys.executable` is `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Rendering/measurement: `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -s`, Python 3.11.3, Pillow 10.4.0. Both interpreter records are in the receipt. Rendering consumed only verified crop bytes.

The **42 misaligned step1 slots were dropped without replacement**: **28 digit boxes outside the crop**, 13 line-text/label disagreements, and 1 reversed digit-box order. All ids and reasons are in `artifacts/n1/step1_dropped_misaligned_v2.jsonl`. The 28 crop-outside cases are separately listed in `artifacts/n1/step1_crop_outside_v2.jsonl` for clipped-crop review. `artifacts/n1/step1_rendered_v2.jsonl` contains all 558 usable slots with line/zoom paths and hashes, exact geometry, and private raw digit-band/component measurements. The original frame and geometry artifact are unchanged. The existing component helper emitted nonfatal poorly-conditioned curve-fit warnings; these remain raw measurements, without a fitted rule or glyph judgment.

`artifacts/n1/controls/candidates_v2.jsonl` has **24 thousands dots, 24 decimal commas, 22 range hyphens, 12 inner hyphens, and 12 empty inner gaps**. Version 1 is retained unchanged. All 15 misaligned v1 controls were dropped; 13 replacements came from the same category pools with the replayed `20261017:N1C:ctrl` shuffle stream. Three further misaligned replacement proposals were skipped. Every rejected id, category, stage and reason is in `controls/rejected_v2.jsonl`. All 70 geometry-ok v1 controls were retained.

The original 13 range candidates include two misaligned slots (one crop-outside, one label disagreement). Applying the explicit misaligned-drop ruling retains **11 of 13**. The entire W1 range pool after the same step1-document, reserved-document and C1 exclusions contains **24 slots total**, including those two invalid ones. The **11 additional slots** were drawn with `20261017:N1C:ctrl:range`. All 22 usable range slots were taken; the two-control shortfall is explicit. Selection origin and source are recorded per candidate.

The reserved C1 card `elstat--c5f7ea1f26d39839--s000-l0367` was refused by the lock guard and excluded. The other two cards' four slots are reference-only records in `controls/c1_references_v2.jsonl`, on one separate sheet labelled **C1 reference**, absent from the candidate census and any pack.

Eight control sheets contain at most 12 cells each (12/12/12/12/12/12/12/10). Each has a large zoom panel, a small whole-line panel, the cell number and Google's glyph. The cell-to-slot mapping, with reference status, is in:

- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/sheets_index.json`

Control sheets:

- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_controls_01.png`
- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_controls_02.png`
- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_controls_03.png`
- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_controls_04.png`
- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_controls_05.png`
- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_controls_06.png`
- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_controls_07.png`
- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_controls_08.png`

Separate reference sheet:

- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cb_c1_reference.png`

Exactly two sheets were opened for layout only: control sheet 01 and the C1 reference sheet. Small native zooms initially left excess white space; all sheets were regenerated with zooms enlarged to fit the large panel. No additional sheet views or glyph classifications followed. The renderer's original 3× zoom files are unchanged; this enlargement is sheet presentation only.

**50 tests passed**: the original 45 plus five artifact checks for exact bed/drop partitioning, control exclusions/replacements, sheet-index/reference isolation, input/output custody and interpreter identity, and verified crops/private measurements. Exact commands and results are in `artifacts/n1/N1Cb_TESTS.json`. Renderer/builder/mapper fixture tests, including marker pixel preservation, lock refusal and calibration mode, passed again; tests built fixture packs only.

No real pack or calibration pack was built; controls await lead approval. No reader run, glyph classification, prompt edit, network access, `.git` write, collector-root write, `run.lock` access or locked-evaluation rendering occurred. Prior N1-C inputs and outputs were hash-checked unchanged before this authorized report append. Full hashes, interpreters, crop failures (empty), drop lists, counts and layout-check scope are in `artifacts/n1/N1Cb_RECEIPT.json`. No live usage probe was run under network OFF.


## N1-Cc

**Rendering complete; approval sealing pending a C1 document-exclusion ruling.** All 640 previously rendered zooms were regenerated (558 step1 and 82 reviewed controls), plus 2 new candidate zooms. The renderer adds two 7-pixel-wide mid-grey triangles in new 12-pixel white margins after 3× scaling. Every prior zoom remains under its old hash; each new zoom has a new hash. All 640 zoom interiors are pixel-identical to their prior versions, all line hashes match, and all 640 recomputed side measurement records match after JSON serialization. `step1_rendered_v3.jsonl` contains the new step1 image references; `zoom_measurement_checks_cc.jsonl` records comparisons.

The review maps to exactly 82 distinct slots: 21 baseline dots, 23 commas, 27 hyphens/dashes, 7 nothing, 4 raised dots. No rejected cell is included. The cell mapping was taken from the existing `sheets_index.json`. **Conflict:** the four C1 controls are in document `elstat:GRESYE_01_0001_00090`, which occurs in step1. Their lines are outside the frame and reserved set, but their document fails the requested document exclusion. The other 78 controls pass both document exclusions. The explicit C1 control approval therefore needs to be reconciled with the document-level constraint. `controls/approved.jsonl` has not been written while that question is pending. The complete 82-row proposal with new renders is `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_cache/n1cc_approved_proposed.jsonl`. No C1 line was admitted to the candidate pool.

Raised-dot eligibility used the union of nonempty inner separators in 4+-digit tokens on the supplied ambiguous rows and Google `·`/`-` grammar-thousands slots in 4+-digit tokens on any W1 elstat/gazette row, with exact geometry required. After step1/reserved document and C1 line exclusions, the pool is **2 slots in 2 rows and 2 documents**; 1 further slot failed geometry. Both eligible slots were selected with seed `20261017:N1Cc:raised`, below the three-per-document cap. These are candidates for the lead, without any new printed-glyph truth labels. Full pool, selected records and geometry rejection are in `controls/raised_pool_cc.jsonl`, `controls/raised_candidates_cc.jsonl` and `controls/raised_rejected_geometry_cc.jsonl`.

Candidate sheet: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cc_raised_01.png` (cells 101–102, Google glyph shown). Index: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/sheets_index_cc.json`. Sample sheet: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/n1cc_zoom_check.png` (12 reviewed controls, cells 84, 87, 89, 90, 91, 92 and 94 first). Only the sample sheet was viewed, for layout; no glyphs were classified.

Both newly requested candidate line crops passed frozen SHA256 checks through the collector's arm64 Python 3.11.3/Pillow 12.3.0 using redirected shallow row copies. Rendering and measurements used x86 Python 3.11.3/Pillow 10.4.0 with `-B -s`; existing verified crops were rehashed. Existing component-helper poorly-conditioned fit warnings were nonfatal and measurement equality passed.

**58 tests passed**: 44 existing text/artifact checks, 8 image/builder fixtures (including zoom interior preservation and two crop-boundary marker tests), and 6 new approval-proposal/census/custody checks. Approval tests currently verify the proposal and explicitly record the four C1 document conflicts; they do not certify unconditional document exclusion. Commands and outputs are in `N1Cc_TESTS.json`.

All prior persistent N1 artifacts and earlier rendered images were rehashed unchanged before this report append. No real or calibration pack, reading run, network access, `.git` write, collector-root write, `run.lock` access, prompt edit or locked-evaluation rendering occurred. The receipt status remains `PENDING_C1_DOCUMENT_RULING`, rather than READY.


## N1-Cd


**READY for operator-invoked calibration and glyph reading; no real reading or limit probe was invoked.** The 17 October lead ruling resolves the C1 document conflict recorded in N1-Cc. All 82 proposal rows are sealed in `artifacts/n1/controls/approved.jsonl` with the ruling and source hash in each row’s provenance. The four C1 raised-dot slots are control-only evidence: their lines are outside every step1 line and the reserved set, and N1 never fits on them. Their shared step1 document is explicitly allowed; the other 78 controls retain the document exclusions.

Sealed SHA256: `f0ef2f86e432b828ba634e8f512132589a3a513e208c6449b054962fafcafc00`. Cell 101 is a spaced hyphen duplicating approved hyphen cell 58; the existing cell-58 approval is retained once, with no new control. Cell 102 is a baseline dot under a dotted leader and is excluded. No new raised-dot controls were added.

Seed `20261017:N1-1` controls bed order, control order, item order and per-item option permutations. Calibration is `sol_packs/n1cal/cal01/r1/`, with all 82 controls and private key `artifacts/n1/keys/cal01.json`. Glyph packs are `sol_packs/n1/ctx01/r1/` through `ctx07/r1/`, with 558 distinct rendered step1 slots exactly once and 63 control appearances. Every context has nine distinct controls: one raised dot plus two from each other approved truth class, allocated round-robin within each class. The four raised slots appear 2/2/2/1 times across contexts. Every source line/zoom hash was reverified; pack PNG hashes equal the v3 source hashes. No images were rerendered or glyph truths inferred.

Bed counts below are existing grammar candidate classes, not printed-glyph truths; `range/thousands` preserves the alternative-label combination. Control counts are approved printed truths.
| Context | Items | Bed | Controls | Raised dot | Baseline dot | Comma | Hyphen/dash | Nothing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cal01 | 82 | 0 | 82 | 4 | 21 | 23 | 27 | 7 |
| ctx01 | 89 | 80 | 9 | 1 | 2 | 2 | 2 | 2 |
| ctx02 | 89 | 80 | 9 | 1 | 2 | 2 | 2 | 2 |
| ctx03 | 89 | 80 | 9 | 1 | 2 | 2 | 2 | 2 |
| ctx04 | 89 | 80 | 9 | 1 | 2 | 2 | 2 | 2 |
| ctx05 | 89 | 80 | 9 | 1 | 2 | 2 | 2 | 2 |
| ctx06 | 88 | 79 | 9 | 1 | 2 | 2 | 2 | 2 |
| ctx07 | 88 | 79 | 9 | 1 | 2 | 2 | 2 | 2 |


| Context | Other | Range | Thousands | Decimal | Range/thousands | Table boundary |
|---|---:|---:|---:|---:|---:|---:|
| cal01 | 0 | 0 | 0 | 0 | 0 | 0 |
| ctx01 | 51 | 9 | 7 | 8 | 2 | 3 |
| ctx02 | 43 | 15 | 11 | 7 | 3 | 1 |
| ctx03 | 47 | 9 | 10 | 5 | 8 | 1 |
| ctx04 | 48 | 10 | 9 | 5 | 6 | 2 |
| ctx05 | 50 | 8 | 10 | 4 | 6 | 2 |
| ctx06 | 52 | 12 | 6 | 4 | 5 | 0 |
| ctx07 | 51 | 9 | 7 | 6 | 5 | 1 |



All **8/8 contexts passed closure**, including a final independent rerun. Reader folders contain only `items.jsonl` and hash-named, metadata-free PNGs in `img/`; manifests sit beside `r1`. Keys, geometry, source ids, measurements, approvals and truths stay outside every reader folder. Each context has at most 89 items. `N1Cd_RECEIPT.json` binds keys, item lists, manifests, scripts, tests and every unchanged prior N1 artifact.

`scripts/secondary/reading/run_n1.sh <n1|n1cal> <ctx> [reader]` is prepared for r1 (the only reader packs built). It probes usage before and after an attempted read, refuses weekly usage ≥78%, reuses `run_read.sh` with `sep.md` at medium effort, requires `gpt-6.1-sol`, runs the unchanged v4 `scan_rollout.py` against the exact reader folder, then uses `n1_map_answers.py`. Existing reading helpers are unchanged: their shell bodies are reused with only their hardcoded RU1 log-root assignment redirected in memory to `artifacts/n1`. All original network-disabled and web-disabled model settings are preserved. Existing attempts are never overwritten.

Answers, run receipts, scans and mapped results go to `artifacts/n1/answers/<ctx>.<reader>.*`; measured usage goes to `artifacts/n1/usage_ledger.json`, currently an empty array. Calibration additionally writes `<ctx>.<reader>.calibration.json` with per-class accuracy, a truth-row/prediction-column confusion matrix and disagreements carrying slot and item ids. Missing/duplicate/invalid responses are counted as unresolved errors. More than one control error marks a context VOID; unresolved answers, unexpected ids, reader failures and scan failures return failure.

**72 tests passed**. `N1Cd_TESTS.json` records exact commands and outputs. New tests validate real-pack coverage and v3 image custody; deterministic seven-context allocation and raised-dot rotation; the production CLI’s missing-raised refusal; calibration disagreements and missing answers; and fake-reader launcher success, pre/post usage threshold refusal, v4 leak rejection, reader failure, missing answers, overwrite refusal, shell syntax, and unchanged helper bodies. Both n1 and n1cal launch paths were exercised solely with isolated fake readers/probes. Python syntax and launcher shell syntax also passed.

Image packing, closure and image fixtures used x86 Python 3.11.3/Pillow 10.4.0 with `-B -s`; text tests used `python3 -B -m pytest --noconftest`. No network, `.git` writes, real reader/probe, collector-root writes, `run.lock` access, locked-evaluation rendering, prompt edits or new glyph classification occurred. All previous frame/lock/artifact hashes remain unchanged.
