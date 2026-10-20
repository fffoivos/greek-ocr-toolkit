# SEG-DESKEW-1 hand-off

## Change

Implemented segmentation **0.6**, “0.5 + row-frame text box”, from worktree HEAD `602938bb54b728c3136c5e98493cac3fba651db7`. No network, Clariden, Slurm, OCR reader, policy tuning, predictor fitting, or push was used.

`NativeSegmenter.__call__` is this checkout’s segment entry point. It fits a straight line to every sample of the detected `side == "main"` row’s full `base` curve, using clockwise-positive image coordinates. Missing/flat main rows give 0°. A flatness guard covers only eight baseline ULPs of solver roundoff; there is no operational angle cutoff. The existing detector, refocus, roles, quarter-turn handling and neighbour reconciliation are unchanged.

`tight_box` rotates ink belonging to the existing TEXT_ROLES component IDs by −θ about `(crop_width/2, crop_height/2)`. It bounds continuous unit pixel cells analytically, without resampling, integer rounding, clipping or rotating component envelopes. `length` is the span along the row and `height` is the span normal to it. Corners are mapped back into the existing measurement-frame crop coordinates in row-frame top-left, top-right, bottom-right, bottom-left order. θ = 0 takes the original integer `tight_box` path.

The unchanged predictor receives `max(length,height)` and `min(length,height)`. The upright `box_evidence.bbox` remains available for drawing; only `box_evidence.row_frame = {angle_deg,length,height,corners}` is added. Padding now uses `(segment_height − upright_box_height) / row_frame.height`, and records `upright_box_height` and `row_frame_height`. Its unchanged 1.5 threshold therefore admits a crop height up to the upright envelope plus 1.5 row-normal heights. All nonmeasurement evidence differences seen in replay are itemized below and reproduced by the untouched adapter.

- Frozen policy SHA256: `8334dd4028822edbd740a1a96a0ead6367c7af953e545bad8bd60a911c65a819`.
- Segmentation component digest: `139d459850ccf51b8a16214530970e25548ced9c477ce67a38d4fef074c57603`.
- New complete toolchain digest (`digest(canonical(tool_versions["tools"]))`): `610c4d40d531c195c23f28d4da7ef7a1e7564cd0e97cc871d875c89f02350cf1`.
- `build_filter_versions.py` and its generated `tool_versions.json` were updated. Apart from segmentation 0.6, only the census component fingerprint/digest changes because it fingerprints `line_pipeline_native.py`; its version and behavior are unchanged.
- Scope proof: [source_changes.patch](source_changes.patch), [code_git_diff.patch](code_git_diff.patch), [scope_guard.json](scope_guard.json), [replay_validation.json](replay_validation.json). AST comparison permits only `NativeSegmenter.__call__`, `tight_box`, and `features_from_observation` in the two production code files. Policy, font coefficients and the entire predictor source/lock/config plus executable retain their initial hashes.

**Git limitation:** creating `sol/seg-deskew` in the requested worktree failed because its shared Git directory lies outside the writable sandbox. The exact error was `cannot lock ref ... /Projects/greek-ocr-toolkit/.git/refs/heads/sol/seg-deskew.lock: Operation not permitted`. The worktree remains on `sol/recut-v1`. A portable branch named `sol/seg-deskew`, rooted at the requested HEAD, is instead committed in an isolated writable Git directory and delivered in `SEGDESKEW1.bundle`. No shared Git ref/index was changed. The implementation commit below and a separate hand-off commit are in that bundle; the hand-off cites the implementation commit to avoid a self-referential commit hash.

The two production files, version builder and versions JSON already existed **untracked** at task start. Their initial bytes are retained in [baseline/](baseline/); the scoped patches compare against those exact bytes. Relative to HEAD, Git necessarily records those requested files as additions. Other pre-existing untracked runtime/dependency files were not staged or included. The bundle is a scoped worktree hand-off, not a standalone packaging of all pre-existing runtime inputs.

Initial and final tracked `git diff --stat` are identical; the five pre-existing edits were neither modified, staged, committed nor reverted:

```text
 .gitignore                                         |  5 +++
 .../collect_v3_admission/test_stage_crops.py       | 10 ++++-
 greekocr/harvest/geometry_observations.py          | 48 +++++++++++++---------
 greekocr/harvest/row_inclusion.py                  |  4 +-
 pyproject.toml                                     |  2 +
 5 files changed, 45 insertions(+), 24 deletions(-)
```

## Tests

Checks ran CP1 → CP2 → CP3, using `.venv/`. The existing offline test fixture blocks live network connections; replay scripts also reject Python network connect/DNS audit events.

CP1 command: `.venv/bin/python -m pytest tests/test_seg_deskew.py -q` (with all four native thread limits set to 1 and bytecode writes disabled).

```text
......                                                                   [100%]
6 passed in 1.21s
```

The six tests cover three real upright crops against saved census evidence to the digit (bbox, expected, padding, and all other evidence after stripping the additive fields), upright renders rotated +2° and −2° (height within 1 px, length within 1%), and a tall synthetic crop exercising the owner’s padding formula and the unchanged height-reject verdict. The initial two failures exposed flat-baseline floating residue and are preserved in `cp1_initial_roundoff_failure.log`; the guard fixed them before CP2.

Existing pipeline regression command: `.venv/bin/python -m pytest tests/test_line_pipeline.py -q`.

```text
........................................................................ [ 55%]
..........................................................               [100%]
130 passed in 1.80s
```

Total: **136 passed** (6 new + 130 existing). Readback validation independently reproduces all **1,038** stored new predictor outputs and policy verdicts/reasons exactly, verifies every padding formula, verifies version rebuild identity, and rechecks protected hashes. This is in addition to pytest, not counted as extra pytest tests.

## Parity

### CP2 — 150 unseen SEGEVAL-1 rows

All **150/150** byte-bound crops replayed through the native segmenter with no row failures (33.98 s). Before = original census evidence/frame; after = native 0.6 result, with sealed raw text/binding/script metadata and owner reader state. See [replay_segeval1.jsonl](replay_segeval1.jsonl), [cp2_summary.json](cp2_summary.json), and [cp2_verification.log](cp2_verification.log).

**θ = 0 parity: 11/11 exact** for bbox, expected and total padding. Mismatches: **none**. No θ = 0 verdict changes; all 100 original KEEP rows remain KEEP. Counts change from KEEP 100 / DROP 50 to KEEP 106 / DROP 39 / UNCERTAIN 5.

The coordinator’s baseline count is confirmed: **29** reader-fine rejects, **27** of them rejected for OCR length (15 too much, 12 too little). The five named skew examples all clear their length failures. Only two of those five become KEEP: three retain unresolved neighbour geometry and become UNCERTAIN. Overall **3** length-rule false positives become KEEP, **3** flagged rejects become KEEP, and **5** other flips are DROP → UNCERTAIN. The suggested ≥5 FP → KEEP expectation was not reached; no thresholds or geometry behavior were changed to force it.

Census-to-Mac drift outside the intended measurements occurred on 13 rows. The untouched 0.5 adapter reproduces **all 13** new nonmeasurement evidence payloads exactly and their frames exactly after removing elapsed `seconds`, and reproduces all saved verdicts and boxes. These are pre-existing runtime/platform differences, not extra edits. The original strict replay assertion exposed them and remains visible in `cp2_replay.log`; `cp2_verification.log` records the completed attribution check. Full witnesses: [baseline_drift_rows.jsonl](baseline_drift_rows.jsonl), [baseline_drift_summary.json](baseline_drift_summary.json).

| Line ID | Outside-measurement fields | Cause reproduced by untouched 0.5 |
| --- | --- | --- |
| elstat--07520765bc203a33--s000-l0134 | detected_rows | Two sampled ascender/descender coordinates differ by 0.001 px. |
| lekythos--a0c4e6327052acfc--s002-l0089 | frame | Orientation elapsed seconds; some guide diagnostic floats differ at machine precision. |
| elstat--0877c813a8512b56--s000-l0037 | neighbour_evidence, frame | One saved context-group left edge is 27 vs local 26; orientation timings/floats also differ. |
| elstat--0a2c92120843658d--s001-l0147 | frame | Orientation elapsed seconds; some guide diagnostic floats differ at machine precision. |
| elstat--24e6586813212fd1--s001-l0357 | detected_rows | Two sampled ascender/descender coordinates differ by 0.001 px. |
| gazette_modern--0089276875b132d9--s000-l0028 | frame | Orientation elapsed seconds; some guide diagnostic floats differ at machine precision. |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | frame | Orientation elapsed seconds; some guide diagnostic floats differ at machine precision. |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | frame | Orientation elapsed seconds; some guide diagnostic floats differ at machine precision. |
| gazette_modern--52ee6226bb7d4834--s000-l0122 | frame | Orientation elapsed seconds; some guide diagnostic floats differ at machine precision. |
| gazette_modern--65492f4d3675f146--s000-l0001 | detected_rows | One sampled descender coordinate differs by 0.001 px. |
| gazette_modern--6d6a6fe53e769b59--s000-l0009 | frame | Orientation elapsed seconds; some guide diagnostic floats differ at machine precision. |
| gazette_modern--82115ca04c55f5b7--s000-l0005 | frame | Orientation elapsed seconds; some guide diagnostic floats differ at machine precision. |
| gazette_modern--e1ffcad236d8706c--s000-l0266 | frame | Orientation diagnostic internal box/support differs; final orientation/box/verdict are unchanged. |

### CP3 — accepted 888 saved decisions and local crops

Ran the documented saved-metadata tool unchanged:

```sh
.venv/bin/python scripts/harvest/verify_filter_parity.py \
  --out docs/records/harvest/collect_v3_admission/segeval1/deskew/cp3_saved_metadata_parity.json
```

```text
{"status": "PASS", "frozen_policy_byte_identical": true, "decision_and_reason_parity": 888, "rust_prediction_rows": 888, "max_absolute_prediction_error": 1.4210854715202004e-13, "context_reconciliation_parity": 184, "native_images_processed": 0, "refitted": false}
```

It checks more than verdicts: **888 verdicts/reasons**, **888 predictions from saved long/short inputs** (max absolute error `1.4210854715202004e-13`), and **184 saved raw-context reconciliations**. It opens zero images and does **not** cover native box/baseline measurement or new row-frame evidence.

All **888/888 crops** are available in the local review site and were replayed. Crop orientation, glyph detector/refocus, baseline/labels, new box and padding run through the native adapter; page-context observations are the frozen raw observations already checked by `verify_filter_parity.py` and are re-reconciled by the unchanged service. Source-page detection is not rerun for this second cohort. Original text for 136 older rows came from hash-bound local population detail chunks; the first 704 completed results were retained when the remaining historical metadata was resolved. See [replay_calibration.jsonl](replay_calibration.jsonl), [cp3_calibration_summary.json](cp3_calibration_summary.json), and the two preserved initial metadata-lookup logs.

**16 historical-saved → native-0.6 verdict flips**: 3 DROP → KEEP, 5 KEEP → DROP, 2 UNCERTAIN → DROP, 5 DROP → UNCERTAIN, 1 KEEP → UNCERTAIN. Diagnostic replay with untouched 0.5 on all flips plus identity/box drift witnesses (33 unique rows) attributes **2 flips to pre-existing orientation handling** and confirms **14 of the 16 flips** between local 0.5 and 0.6. This is not a claim of calibration accuracy improvement. See [calibration_drift_summary.json](calibration_drift_summary.json).

There are **41 θ = 0 rows**, all with identical upright box/padding and no verdict flip. Against historical saved expected values, **30/41** match to the digit and **11/41** differ only by `4.44e-16`–`1.07e-14`. Every one of those eleven is reproduced identically by the untouched local 0.5 predictor, so this is pre-existing frozen predictor arithmetic, not a de-skew identity change. Every mismatch is listed here:

| Line ID | Saved expected | Local 0.5 = new 0.6 expected | Delta | Cause |
| --- | --- | --- | --- | --- |
| elstat--3b2d88122b3f037c--s001-l0145 | 6.330107272883208 | 6.33010727288321 | 1.7763568394002505e-15 | Pre-existing frozen predictor arithmetic |
| elstat--7f3a47a9bc42d5c3--s000-l0086 | 16.808546852988183 | 16.808546852988176 | -7.105427357601002e-15 | Pre-existing frozen predictor arithmetic |
| gazette_modern--affc069208f11f21--s000-l0014 | 3.7908470547980846 | 3.7908470547980837 | -8.881784197001252e-16 | Pre-existing frozen predictor arithmetic |
| elstat--ee37bc488988f1bd--s000-l0348 | 6.435880663809972 | 6.435880663809976 | 3.552713678800501e-15 | Pre-existing frozen predictor arithmetic |
| elstat--88112979c8a843cb--s001-l0170 | 2.0568112817024584 | 2.0568112817024593 | 8.881784197001252e-16 | Pre-existing frozen predictor arithmetic |
| elstat--0877c813a8512b56--s000-l0222 | 3.4202676628261033 | 3.420267662826104 | 8.881784197001252e-16 | Pre-existing frozen predictor arithmetic |
| serbia--1d48c39bca3c4249--s008-l0001 | 2.29346708462971 | 2.293467084629711 | 8.881784197001252e-16 | Pre-existing frozen predictor arithmetic |
| ia_russian--d558bd3e803e7865--s007-l0031 | 13.266936764295371 | 13.266936764295378 | 7.105427357601002e-15 | Pre-existing frozen predictor arithmetic |
| bsb_poly1850--fe51c7e60c92453d--s034-l0003 | 1.8064472400299834 | 1.806447240029983 | -4.440892098500626e-16 | Pre-existing frozen predictor arithmetic |
| elstat--df38bce62200e7db--s001-l0110 | 3.6638311174329905 | 3.6638311174329914 | 8.881784197001252e-16 | Pre-existing frozen predictor arithmetic |
| ia_greek_latin--e02bf39b0ef9974e--s000-l0005 | 17.2728504387709 | 17.272850438770888 | -1.0658141036401503e-14 | Pre-existing frozen predictor arithmetic |

Nine calibration upright boxes differ from historical measurement. Each is reproduced by unchanged local 0.5; all nine use different historic/current quarter-turn handling, including historical visual overrides that the generic native producer does not consume. No orientation code was changed for this task:

| Line ID | Saved bbox | Local bbox (0.5 = 0.6) | Frame cause |
| --- | --- | --- | --- |
| elstat--d3b9d73bb0fbd59e--s000-l0162 | [0, 0, 92, 21] | [0, 50, 140, 92] | 0° visual_review → 90° axis_preview_only |
| gazette_modern--104e152774c2805f--s000-l0073 | [1, 6, 445, 26] | [4, 0, 448, 20] | 270° visual_review → 90° axis_preview_only |
| gazette_modern--279b47524ddd0a32--s000-l0069 | [3, 8, 171, 25] | [6, 0, 174, 17] | 270° visual_review → 90° axis_preview_only |
| gazette_modern--363c5539ff24957e--s000-l0104 | [2, 0, 165, 15] | [2, 3, 165, 18] | 270° axis_preview_only → 90° axis_preview_only |
| gazette_modern--57e4032e7fd9fa48--s000-l0039 | [4, 4, 1948, 44] | [4, 2, 1948, 42] | 270° visual_review → 90° axis_preview_only |
| gazette_modern--67dfc161a690ff25--s000-l0038 | [40, 0, 382, 41] | [0, 81, 352, 122] | 270° visual_review → 90° axis_preview_only |
| gazette_modern--92fc6af88c8de766--s000-l0081 | [4, 0, 221, 30] | [3, 1, 220, 31] | 270° visual_review → 90° axis_preview_only |
| gazette_modern--a895f3d785bb13b6--s000-l0138 | [4, 0, 1792, 35] | [13, 0, 1801, 35] | 270° visual_review → 90° guide_supported |
| gazette_modern--a895f3d785bb13b6--s000-l0150 | [218, 224, 1998, 282] | [219, 187, 1999, 246] | 270° visual_review → 90° guide_supported |

## Flip tables

Ratios below use the **actual frozen policy ratio `(characters + 1) / (expected + 1)`**, not `characters / expected`. θ is clockwise positive. Heights are in pixels; displayed values are rounded here, full precision is retained in JSONL. `fine`/`flagged` come directly from the SEGEVAL-1 owner rows. Calibration owner values are saved owner ratings where present; `unrated` is not a reader judgment.

### Every flip on the 150 unseen rows

| Line ID | θ° | Upright h → row h | Policy ratio before → after | Verdict before → after | Reader state |
| --- | --- | --- | --- | --- | --- |
| gazette_modern--9701a3a500ecbd85--s000-l0139 | -1.515039 | 46 → 31.069697 | 1.770936 → 1.220464 | DROP → KEEP | fine |
| gazette_modern--086f9d1e5320e673--s000-l0144 | +0.673229 | 44 → 40.754020 | 1.504623 → 1.398610 | DROP → KEEP | flagged |
| gazette_modern--37ed2e85ffdd5592--s000-l0161 | +1.586912 | 42 → 25.911150 | 1.573236 → 0.986247 | DROP → KEEP | flagged |
| gazette_modern--3aa75c333f199302--s000-l0043 | -0.915231 | 46 → 41.122332 | 1.649266 → 1.482839 | DROP → KEEP | fine |
| gazette_modern--e85649b67a7af9ab--s000-l0078 | +27.108123 | 58 → 60.042616 | 1.504940 → 1.458360 | DROP → KEEP | flagged |
| c82ac45f-p000087-l0021 | -2.272471 | 49 → 25.543432 | 1.521363 → 0.819536 | DROP → KEEP | fine |
| 00c322b3ee04b419d1979f22-p000028-l0002 | +2.100128 | 49 → 30.067106 | 1.507478 → 0.939238 | DROP → UNCERTAIN | fine |
| 43de3c6e6a7113a4e661bb7d-p000100-l0023 | +1.957944 | 44 → 33.398823 | 1.518452 → 1.162641 | DROP → UNCERTAIN | fine |
| 66112e132fd96ac8e30e5328-p000159-l0079 | +1.737148 | 40 → 34.992232 | 1.537036 → 1.349667 | DROP → UNCERTAIN | fine |
| 847e1ec1-p000015-l0035 | +1.235017 | 77 → 82.864135 | 0.473045 → 0.507725 | DROP → UNCERTAIN | fine |
| b8b6779da9a68fbed0ccdb5b-p000011-l0018 | -1.750525 | 52 → 30.297718 | 1.575743 → 0.934772 | DROP → UNCERTAIN | flagged |

Every before/after reason, full evidence payload, frame and reader state is in `replay_segeval1.jsonl`. All five new UNCERTAIN verdicts have reason “The complete neighbouring-word count or line extent is unresolved.”; their context was already unavailable in the saved census evidence.

### Every historical-saved flip on the 888 calibration crops

| Line ID | θ° | Upright h → row h | Policy ratio before → after | Verdict before → after | Saved owner rating | Attribution |
| --- | --- | --- | --- | --- | --- | --- |
| ia_russian--06528548147a3a3d--s002-l0005 | -0.226445 | 36 → 36.240803 | 0.497476 → 0.500350 | DROP → KEEP | unrated | 0.5 → 0.6 measurement |
| ia_poly1850--bd7bfada1d31d9e4--s031-l0023 | +27.426285 | 75 → 94.102089 | 1.313467 → 1.625689 | KEEP → DROP | unrated | 0.5 → 0.6 measurement |
| gazette_modern--c49eeee35f4153a9--s000-l0131 | -0.782780 | 40 → 37.523507 | 1.541167 → 1.450830 | DROP → KEEP | unrated | 0.5 → 0.6 measurement |
| ia_greek_latin--2b4cfc7c6d70fd98--s000-l0053 | -7.630130 | 35 → 54.341192 | 1.059396 → 1.626874 | KEEP → DROP | unrated | 0.5 → 0.6 measurement |
| ia_poly1850--61d0e23d1e93ae02--s031-l0002 | -0.396097 | 51 → 49.238734 | 0.504671 → 0.488106 | KEEP → DROP | unrated | 0.5 → 0.6 measurement |
| gazette_modern--8757f64ef1908c90--s000-l0009 | -1.038289 | 37 → 41.157343 | 1.375576 → 1.521821 | KEEP → DROP | unrated | 0.5 → 0.6 measurement |
| bsb_poly1850--2032df1e3e983f1d--s005-l0009 | -9.608115 | 78 → 48.111434 | 0.591306 → 0.374618 | UNCERTAIN → DROP | DROP | 0.5 → 0.6 measurement |
| elstat--d3b9d73bb0fbd59e--s000-l0162 | -0.266479 | 21 → 42.032102 | 0.593324 → 0.760379 | DROP → UNCERTAIN | DROP | Inherited local 0.5 orientation change |
| gazette_modern--279b47524ddd0a32--s000-l0069 | +2.226612 | 17 → 17.097585 | 1.460044 → 1.466465 | KEEP → UNCERTAIN | KEEP | Inherited local 0.5 orientation change |
| gazette_modern--57e4032e7fd9fa48--s000-l0039 | +0.785889 | 40 → 16.257444 | 2.945044 → 1.254316 | DROP → UNCERTAIN | DROP | 0.5 → 0.6 measurement |
| ia_greek_latin--5f5319037ff4b70f--s000-l0028 | +5.218543 | 101 → 89.848681 | 1.562421 → 1.364979 | DROP → UNCERTAIN | DROP | 0.5 → 0.6 measurement |
| ia_russian--61f76a57b26f9b13--s001-l0001 | +9.882548 | 182 → 58.050991 | 1.129193 → 0.411426 | UNCERTAIN → DROP | KEEP | 0.5 → 0.6 measurement |
| lekythos--456def1ccfc2283e--s001-l0177 | -0.638834 | 20 → 18.497090 | 0.500885 → 0.465356 | KEEP → DROP | DROP | 0.5 → 0.6 measurement |
| serbia--3ab59a8d4ee49339--s005-l0014 | +5.156627 | 20 → 32.915023 | 0.351838 → 0.551793 | DROP → KEEP | KEEP | 0.5 → 0.6 measurement |
| bsb_poly1850--e2115ba0deaf6a07--s004-l0033 | +1.759029 | 77 → 49.437180 | 1.820480 → 1.200383 | DROP → UNCERTAIN | unrated | 0.5 → 0.6 measurement |
| gazette_modern--eb53bdc9a40bd912--s000-l0118 | -1.869885 | 66 → 19.834019 | 2.846635 → 0.890520 | DROP → UNCERTAIN | unrated | 0.5 → 0.6 measurement |

## Open issues

1. **Worktree branch/commit publication is sandbox-blocked.** The actual current worktree branch remains `sol/recut-v1`; only the isolated commit bundle carries `sol/seg-deskew`. Importing that branch into the shared repository requires its Git directory to be writable. No push was attempted. The implementation commit is `58978481c669a21068a5192c9c3022dcd31320af`.
2. **Height wording on non-elongated glyphs:** one θ = 0 calibration glyph (`bsb_poly1850--fe51c7e60c92453d--s034-l0003`) has a box taller than wide. Sorting sides for padding would violate the explicit θ = 0 identity requirement. This implementation preserves row-normal `height` for padding, while sorting the two sides only for the predictor. There is also one nonzero-angle near-square row on the 150 and two more nonzero-angle calibration rows where row-normal height exceeds along-row length. An optional owner clarification was requested; absent a reply, exact identity takes precedence. No role, orientation or detector workaround was introduced.
3. **Coverage is bounded:** three named skew false positives become UNCERTAIN because source context is absent; the patch does not invent that evidence. Large fitted main-row angles (including +27° examples) are used as detected, with no new rejection/capping heuristic. The calibration replay includes five KEEP → DROP measurement flips and two UNCERTAIN → DROP measurement flips; these remain reviewable counterexamples, not a generalization claim.
4. Historical calibration orientation overrides and frozen predictor float differences remain distinct from de-skew. The native 888 replay reuses saved raw page context and does not qualify new source-page geometry. This does not alter the saved-metadata parity PASS or the digit-exact 150-row θ = 0 result.

SEGDESKEW1: done | parity theta0: 11/11 | flips on 150: FP->KEEP 3, flagged->KEEP 3, other 5 | 888: covered flips 16 | tests: 136 passed | commit: 58978481c669a21068a5192c9c3022dcd31320af
