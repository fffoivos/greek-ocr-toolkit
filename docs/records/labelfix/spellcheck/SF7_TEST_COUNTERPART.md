# SF7 test/dev counterpart — TR1

18 October 2026. **Saved outputs are missing for the complete requested population. Branch 2b applies: estimate and package outline only.** No inference, mock, recomposition, allocation, deployment or scheduler test was run; no job was submitted and no `.git` writes were made. Clariden was accessed read-only. Nothing is bound before audit.

The requested identity remains package `opus/spellcheck 69a00ca13`, policy `sf7-release-v1`, addition variant **A**, reader mode **ENSEMBLE_AB**, policy digest `f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047`. The reference is [the train release receipt](../../../../artifacts/sf7_rc1/RELEASE_RECEIPT.json), whose status is `candidate_pre_audit`, `bound: false`. Preregistration SHA-256 is `64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d`. No policy tuning or new label binding is proposed.

## Eligible population and raw parents

Apply the train intake rule to each matching **raw import**: every row with `script_class == "greek_poly"`, preserving its exact ID and original label bytes. This includes Wikisource; it does not mean only lines already carrying a particular visible mark. Exact sorted IDs are in [test_eligible_ids.txt](TR1_evidence/test_eligible_ids.txt) and [dev_eligible_ids.txt](TR1_evidence/dev_eligible_ids.txt). These are locally generated inventories, not downloaded overlays.

| Split | All raw rows | Eligible lines | Eligible documents | Other-script rows |
|---|---:|---:|---:|---:|
| v2_test | 44,029 | **28,620** | 60 | 15,409 |
| dev | 13,522 | **8,110** | 19 | 5,412 |
| Total | 57,551 | **36,730** | 79 | 20,821 |

| Wave | Test eligible | Dev eligible |
|---|---:|---:|
| round1 | 7,774 | 3,012 |
| round2 | 3,492 | 574 |
| parliament | 6,350 | 1,987 |
| vouli | 1,660 | 1,430 |
| mixed | 1,652 | 263 |
| wikisource | 7,692 | 844 |

Local raw parents, read without copying:

- Test: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl`; SHA-256 **`e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8`**.
- Dev: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_dev.jsonl`; SHA-256 **`d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17`**.

Both already exist on Clariden under `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2/` with the same basenames. **Both remote hashes and eligible counts equal the local values.** [Local source receipt](TR1_evidence/raw_imports.json); [remote probe receipt](TR1_evidence/remote_inventory.json), observed at 05:06 UTC. Eligible-ID file hashes are `e060a7eb032ebf8017483a2d83f9f3133a6268b291d423772f56a3b53ef42ff4` (test) and `e6af352548a41c318a263bfefcf99d3003e2dc8ce0ce562ce4d06a581600cdca` (dev).

The historical L1 exclusion receipt distinguishes the 44,029-row raw test import from an older 42,038-row recogniser `v2_test` prediction population. The former is the parent here; those populations must not be silently substituted.

## Saved-output finding

All remote paths below are relative to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/`.

| Saved source | Verified scope / finding | Requested coverage |
|---|---|---|
| `labelfix_l1_20261017/artifacts/labelfix_l1/binding/selection.jsonl` | 124,669 training IDs; SHA `ee6c51bdeb9131fd65361d060fd34b77823c1321d3a77849581cfaa577bd3eec` | **0 test / 0 dev** exact-ID intersections |
| `labelfix_l1_20261017/output_3679313/` | S6 detector/windows, reader A and recogniser alignment; complete train receipt SHA `2042fd48b6250636e7847d3b6a1cd6f8a3111dd31575af30c198e63e4d6062bc` | Train population only |
| `labelfix_l1_20261017/l1e_20261017/output_3679545/inference/` | B/E combined evidence; 124,669 lines, same selection SHA; receipt SHA `f9af3fb24cecf1e5559b202d014c1dd697411656764840a5ee001c101bad8ee6` | Train population only |
| `labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729/` | L1R3 recomposition of the same saved train population | No separate test/dev population |
| `labelfix_l1_20261017/l1f_3680752/` | Recogniser scores, 124,669 train lines; receipt SHA `54fc6d2847088a8f938e1e0de9fd61d95b3f9b2c34232b01c8bb1fc71f51dbaf` | Train population only |
| `labelfix_l1_20261017/s8_dev_extract/` | Analysis sample called “dev”: 600 runtime/alignment IDs; auxiliary cached alignments have 434 IDs | **0 test / 0 dev** in either cache |
| `labelfix_r1_20261016/output_3678928/{A,B}/heldout_predictions.jsonl` | Each has 11,329 slot predictions over 664 IDs | **601 test / 0 dev** IDs per reader; partial discrete predictions, without the complete requested runtime/score contract |
| `labelfix_r1_20261016/output_3678928/{A,B}/owner_predictions.jsonl` | Each has 343 slot predictions over 32 IDs | **31 test / 0 dev** IDs per reader; partial discrete predictions |

The R1 held-out/owner counts are separate intersections, not an asserted disjoint union. Their saved records have `sample_id`, `line_id`, `start`, `base`, `factors`, `cls`; they do not contain reader probabilities. Their receipts explicitly report zero CTC forward passes. They are insufficient for a complete 36,730-line sf7 counterpart.

The [remote inventory](TR1_evidence/remote_inventory.json) inventories metadata under both requested roots, including L1R3 and small held-out fixtures; the [partial-coverage receipt](TR1_evidence/partial_coverage.json) resolves the misleading “dev” cache and R1 exceptions. This is a finding about the specified saved L1/R1 sources, not a claim that no isolated test prediction exists anywhere on scratch. Large production shards were not bulk-decoded on a login node or transferred to the Mac.

## Inference and resource estimate

Plan recognition/alignment, S6 detector/window extraction and reader A/B for all **36,730** eligible lines. Existing R1 fragments receive no subtraction until their geometry, slot completeness and provenance qualify. The conservative reuse route includes E because the existing L1E entry point executes **B and E**; E is overhead of that route, not a change from the frozen ENSEMBLE_AB decision rule. Include an L1F-style scoring pass to retain the requested recogniser scores separately.

Measured receipts were read remotely and hashed. Historical scheduler accounting was queried read-only; [coverage_details.json](TR1_evidence/coverage_details.json) retains the exact `sacct` output and live partition response.

| Historical completed job | Lines | Elapsed | Allocated GPU-h | Allocated CPU-h | Consumed CPU-h (`TotalCPU`) |
|---|---:|---:|---:|---:|---:|
| L1 `3679313` | 124,669 | 1,810 s | 2.011 | 144.8 | 2.724 |
| L1E `3679545` | 124,669 | 2,920 s | 3.244 | 233.6 | 1.498 |
| L1F `3680752` | 124,669 | 660 s | 0.733 | 52.8 | 0.281 |

Each job reserved one exclusive node: **4 GH200 GPUs / 288 allocated CPUs**. Allocated GPU-hours include idle devices and I/O; they are not GPU kernel time. Scaling all three jobs by `36,730 / 124,669 = 0.294620` gives **26.47 minutes, 1.764 allocated GPU-h, 127.04 allocated CPU-h**, and approximately **1.327 consumed CPU-h**. The L1 base job reused 91,469 old alignments, so this scaling alone underestimates a fresh alignment workload.

A separate stage calculation accounts for fresh alignments: C1 measured 93.241 s for 91,469 lines and L1 measured 36.806 s for 33,200 more, both with four workers. For the target, the two-population rate predicts **38.3 s** fresh alignment. The same scaling gives **40.8 s** detector/window elapsed, **387.4 s** A plus composition/I/O, **411.3 s** B/E plus I/O, and **189.8 s** scored recognition plus checks/I/O. S6's summed CPU work predicts **0.548 CPU-h** detection plus **0.062 CPU-h** window extraction. These are planning extrapolations; score extraction, compression, crop validation and startup are material costs. Stage totals omit outer verification/recomposition work, so they do not replace the complete-job forecast.

**Budget one 40-minute run, range 35–45 minutes after allocation, excluding queue delay; request a 60-minute limit on `debug`, account `a0140`, one exclusive four-GH200 node.** This budgets **2.67 allocated GPU-h and 192 allocated CPU-h** centrally; the range is 2.33–3.00 GPU-h / 168–216 allocated CPU-h, with a 4 GPU-h / 288 CPU-h limit. Consumed CPU work is roughly 1.3–2 CPU-h, not 192 CPU-h. Live `debug` was UP with a 90-minute maximum. No throughput qualification or queue-time promise is implied. Test and dev have different text/crop distributions from train, especially Wikisource; the reserve also covers that uncertainty.

**Codex build allowance: ~80 pts, broad range 60–120 pts** for adapting selection/exclusions, composing the existing stages, parameterizing the converter, and validating/deploying the future package. This is an uncalibrated engineering estimate: no points tariff or measured task-cost receipt is available. It excludes new policy research, manual label audit and avoidable model/runner rewrites. [Machine-readable calculation](TR1_evidence/estimate.json).

## Package outline for the coordinator's decision — not built or deployed

1. **Bind split-specific inputs.** Under proposed root `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261018`, create independent test/dev selections from the hashed raw parents and inventory their remote crops before GPU work. Validate exact and canonical line/document identity, duplicates, split overlap and completeness. Keep the frozen train exclusion files intact: their explicit test exclusions cannot be reused unchanged for this test correction task. Record a new test/dev-purpose intake binding; no training on these lines.
2. **Reuse frozen assets.** Use `venv_l1`, E3 `full_s0/best.pt` (SHA `5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663`) and the A/B/E checkpoints already pinned in `config/sf7_job.json`. Reuse existing C1, `l1_detect.py`, `l1_infer.py`, L1E and L1F stage implementations with new input bindings. Save recogniser text, alignments, frame/region scores, native S6 ownership evidence, window receipts and reader outputs remotely. Reject missing/duplicate IDs and failed crop/alignment joins.
3. **Preserve the train evidence contract.** Generate scored evidence as requested, but keep it separately identified. The train sf7 release consumes the L1/L1E runtime contract, which omits some recogniser certification fields; attaching new confidence fields can change deletion outcomes. Do not silently promote newly scored fields into the frozen composer input. Audit any intended difference explicitly before binding results.
4. **Compose variant A using the original sf7 policy bytes.** Retain all paths in the policy digest. In particular, `sf7_job.sbatch` itself is policy-hashed and hardcodes the train root: changing its root would change the requested digest. Use a new outer test/dev sbatch wrapper to invoke the unchanged `sf7_recompose.py` with split-specific configs, root/PYTHONPATH and manifests. Do not point new configs at the train L1R3 baseline receipt; the optional train-baseline equality check has no corresponding held-out baseline. New selection and evidence receipts must establish the new population instead.
5. **Parameterize RB7 conversion after composition.** Reuse the byte-patch logic in `artifacts/sf7_rc1/convert_rb7.py`; its current main/imports and provenance hardcode the train parent and job `3687228`, so it cannot be run unchanged. Pass each matching raw parent, selection, actual future source job and `release_id: sf7_rc1_test_edits_A`. Produce separate `release_edits_only_test_A.jsonl` and `release_edits_only_dev_A.jsonl`, each with its own receipt, parent SHA and split. Preserve `parent: google_raw_v2_import`, exact untouched UTF-8 bytes, changed-only rows, policy digest and per-edit provenance. Verify selected membership, no unchanged rows, forward/reverse byte reconstruction, unique IDs and output readback. Receipts remain `candidate_pre_audit`, `bound: false`.
6. **Preparation gates, only in the later authorized build.** Run a bounded mock through the new exact wrapper; perform a bounded real saved-input login dry run only after inference exists; deploy small code/configuration with remote SHA checks; run `sbatch --test-only`; produce `LEAD_COMMIT_PATHS.txt` and `VERIFY_CMD.sh`. The actual inference and recomposition stay inside a subsequently authorized allocation. Scheduler submission remains coordinator-controlled.
7. **Disk discipline and handoff.** Keep crops, arrays, alignments, frame scores, runtime shards and full overlays on Clariden. Return only the two final edits-only files, receipts and logs. Hash and remove any temporary local transfer copies. This investigation copied no raw imports, crops, tarballs or full overlays; its local additions are ID inventories, metadata receipts, the read-only probe and this report (MB-scale). Disk was 7.1 GiB free at intake. Crop coverage and the future wrapper/converter still require validation during package construction.

TR1 READY: saved outputs missing; test lines 28620 dev lines 8110; estimate: 2.67 GPU-h, 40 min wall, Codex ~80 pts
