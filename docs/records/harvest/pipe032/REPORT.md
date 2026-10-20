# PIPE032 — pipeline 0.3.2

Implemented declared correction scope; all requested checks pass. Changes remain uncommitted for the coordinator. No live census, reader, network, Slurm, deployment or Git-metadata write was issued.

## Launch and scope

The provided writable checkout is `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-pipe032`, branch `cleanup/pipe032`, launch HEAD `4bf2e4cf37e69eb4a073308e8809ce4189c7182c`. Its initial `git status --porcelain` was empty. The requested main-next tree was also clean on `cleanup/20261019` at `1c5038626f202503e980d72b9cbdf562b7d5f3c6`; PIPE032 is its direct child with only the task brief added. Work stayed in the writable isolated checkout. No branch switch or commit was performed.

Read the requested routing/result/final-eligibility code, census binding/dedup/exports/verifier, builder/manifest/README, and segcensus HANDOFF_CENSUS05 blocking findings plus audit_runtime_contracts.py. Segcensus evidence was read only. The separate standing N1 version/digest incompatibility remains outside this task; passing this manifest verifier does not certify those ledgers or a census05 package.

## Changes

- Config `routes_out_of_scope` defaults to `[]`, validates against `TOOLS`, rejects `content_repair`, and is materialized in the config before the run binding hash. Pipeline receives a copied list beside its existing policy. Invalid scope fails even before reporting-only preflight or output creation.
- Needed out-of-scope tools return the exact requested `not_applied_out_of_scope` route record before any corrector/ledger lookup or automatic result. The status is outside `SUCCESS`, exempt only from unresolved-route HOLD, supplies no edits, skips candidate recheck, and is excluded from content-repair resolvers. In-scope missing/sparse results still HOLD. Gate/segmentation exclusions still retain prior-exclusion route records.
- Admission records always contain `corrections_not_applied`: sorted routed tool names, otherwise `[]`. The embedded decision supplies their `not_applied_out_of_scope` status. Summary `corrections_not_applied` maps each configured tool to counts by final disposition, including post-dedup changes. Compatibility admission `pipeline_version` now uses `PIPELINE_VERSION` instead of stale `0.3`.
- Manifest and requested README identify polytonic-out census05 as the **20 October coordinator decision under the owner's end-to-end mandate, never an owner ruling**; SF7 remains candidate_pre_audit and enters when its audit passes. Default scope remains empty.
- Segmentation becomes `0.13`, with extra display field `label="0.9-s5"`; no restrictive manifest property schema exists in the consumers, and the unchanged verifier accepts this field. Thirteen existing iterations remain thirteen. No segmentation method, thresholds or runtime verifier changed.
- Composer owns this orchestration change (its manifest components include `line_pipeline.py`); it adds iteration 3. Census adds iteration 7 for scope binding/admission exports/counts. Other versions do not move; shared-file component digests regenerate as required.
- README version/integration notes are synchronized with this HEAD. The sole existing-test edit updates the explicit pipeline-version expectation from 0.3.1 to 0.3.2; assertions and fixtures otherwise remain unchanged.

## Final eligibility and preserved rules

`greekocr/harvest/line_pipeline.py:337–380` is byte-identical to launch. Its signature reads row, composed text/inventory, expectations, codec and final policy; its body has no routes, polytonic-result or release-scope lookup. The unchanged call at lines 510–512 passes those same arguments. Scope only changes which correction obligations are scheduled/recorded at lines 446–477. Final eligibility reads nothing new.

`scope_guard.json` verifies unchanged function bytes for routes, automatic_result, validate_result, preserve_holds, final_eligibility, finish, the gate/length rules, merge_edits, deduplicate and verify_versions. Segmentation/native assets and source adapters also remain unchanged.

## Versions and direct verifier

| Tool | Version before → after | Iterations before → after | Invariant before → after |
|---|---|---|---|
| polytonic | 0.7 → 0.7 | 7 → 7 | PASS → PASS |
| cyrillic | 0.3 → 0.3 | 3 → 3 | PASS → PASS |
| numerics | 0.3 → 0.3 | 3 → 3 | PASS → PASS |
| dashes | 0.1 → 0.1 | 1 → 1 | PASS → PASS |
| segmentation | 0.9-s5 → 0.13 | 13 → 13 | FAIL → PASS |
| content_gate | 0.3 → 0.3 | 3 → 3 | PASS → PASS |
| content_repair | 0.2 → 0.2 | 2 → 2 | PASS → PASS |
| composer | 0.2 → 0.3 | 2 → 3 | PASS → PASS |
| final_eligibility | 0.3 → 0.3 | 3 → 3 | PASS → PASS |
| census | 0.6 → 0.7 | 6 → 7 | PASS → PASS |
| inventory | 0.1 → 0.1 | 1 → 1 | PASS → PASS |

Pipeline constant: **0.3.1 → 0.3.2**. `build_filter_versions.py` ran normally; a fresh in-memory build equals saved JSON. `version-build-fallbacks.json` is `[]`. Direct `verify_versions(after["tools"])` succeeds for all tools, checking version/history, every component file hash, and every component digest. See `version_verification.json`, `version_build.log` and `version_verifier.log`.

## Tests and native replay

Verbatim final suite count: **`260 passed in 4.65s`** — **0 failed / 0 errors / 0 skipped**. The S4 command's current equivalent includes the seven S5 integration files plus `tests/test_routes_out_of_scope.py` (12 PIPE032 cases). Exact command, cwd, copied-file hashes and interpreter are in `tests_command.txt` and `tests_receipt.json`.

The suite uses a temporary view because this isolated worktree lacks the ignored CLEAN4L alias file, predictor and some relocated evidence. Production/test Python copies are byte-identical; missing support/evidence is linked from existing local custody. `prepare_view.py` and `view_receipt.json` identify the view and supplements. No source or fixture from another worktree was modified. The initial collection failure and initial monotonic fixture mistake were fixed before the final full passing run; no tool rule was relaxed.

Fresh native replay: **150/150 segeval1 + 888/888 calibration** verdicts and reasons equal the exact saved S5 `after` results, in 61.138s. Every crop SHA was rechecked; calibration uses the unchanged saved-context workflow. Differing rows: **none (`[]`)**. `native_replay.jsonl`, script/log and receipt retain every comparison and source/predictor hashes. This verifies native parity under the segmentation version relabel; no reader was run.

## Whole-pipeline mock

| Mock split mode | ADMIT / HOLD / DROP before | After polytonic out | Empty-config differing rows | Movers |
|---|---|---|---:|---:|
| mode-i | 42/117/41 | 42/117/41 | 0 | 0 |
| mode-ii | 106/46/48 | 106/46/48 | 0 | 0 |

These are fresh 0.3.1 versus 0.3.2 runs of the unchanged relocated census04 `mock_batch.py::build` 200-real-row slice and census04 split/diagnostic wrapper, with native observations injected and synthetic qualified no-change corrections preserved. Both modes execute registration, correction imports/validation, routing/composition, final checks, dedup and durable export. No shell job, srun or live census executes. Native saved observation version metadata is relabeled to the bound version; verdicts and evidence are unchanged.

To isolate behavior, both sides use the exact original 0.3.1 manifest/correction binding. Every complete decision is equal after removing only `pipeline_version` and `run_binding_sha256`, whose changes are intentional; no reason, route, text, edit, stage or diagnostic field is removed. All raw decisions are saved as mode-*-{before,empty,polytonic-out}.jsonl. The regenerated production manifest is independently accepted by the direct verifier.

Empty-config differing rows, mode-i: `[]`; mode-ii: `[]`. Polytonic-out movers, mode-i: `[]`; mode-ii: `[]`. The harness supplies qualified synthetic polytonic no-change records for every row, so disabling those records cannot recover missing-SF7 HOLDs in this fixture. Every-mover requirement is satisfied with zero movers; no population recovery is inferred. The focused cases separately prove polytonic-only unresolved HOLD → ADMIT and polytonic+missing-numerics remains HOLD. The mode-ii counts are used in the readiness line.

| Mode | Routed out-of-scope polytonic ADMIT / HOLD / DROP |
|---|---|
| mode-i | 16/45/4 |
| mode-ii | 56/1/8 |

The archived original mock result (73/87/40 mode-i; 133/14/53 mode-ii, expressed ADMIT/HOLD/DROP) used an older package. It is not the 0.3.1 control: the control above runs launch 0.3.1 source with the current gate/final rules and its original manifest.

## Scope guard and receipt

Source changes (complete diffs in `scope_guard.diff`):

- `docs/harvest/line_pipeline/README.md`
- `docs/harvest/line_pipeline/tool_versions.json`
- `greekocr/harvest/line_pipeline.py`
- `greekocr/harvest/line_pipeline_census.py`
- `scripts/harvest/build_filter_versions.py`
- `tests/test_content_gate.py`
- `tests/test_routes_out_of_scope.py`

All additional artifacts are inside `docs/records/harvest/pipe032/`. `scope_guard.json` records the allowed/actual change set, empty index changes and unchanged function hashes. `receipt.json` records path, bytes and SHA256 for source/output artifacts and read-only input evidence; producing state is uncommitted on the launch commit, awaiting coordinator commit. No file exceeds 5,000,000 bytes.

PIPE032 READY: routes_out_of_scope ok; in-scope missing still HOLD ok; admission field ok; empty-config regression 150/888 150/888 mock 200 identical yes; polytonic-out mock ADMIT/HOLD/DROP 106/46/48 → 106/46/48; segmentation version 0.13 (label 0.9-s5) verifier ok; pipeline 0.3.2; versions moved composer 0.2→0.3, census 0.6→0.7, segmentation 0.9-s5→0.13; fallbacks 0; suite 260 passed 0 failed 0 errors
