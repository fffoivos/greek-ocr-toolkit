# L1C — HOLD-reason census readiness

17 October 2026. **READY: analysis only; prepared, mocked, deployed, hash-checked and scheduler-tested; no job submitted.** The first scheduler test reached the live debug-QoS submit limit; the retry passed after L1R completed. The census uses only completed L1R outputs and imports no gate, detector, reader or third-party libraries. SF4 remains `sf4-release-v1`.

Worktree: `greek-ocr-toolkit-spellcheck-l1r`, branch `opus/spellcheck-l1r`, actual HEAD `caf1568881e040f8360befbd0bf30fe8e0e0a49c` (the brief named `4e6d3e2c`). No Git metadata writes or edits in another worktree. All **322 pre-existing protected code/metadata files** retain their hashes; see [integrity check](L1C_evidence/protected_unchanged.json). The frozen gate hash remains `fc3dc4b3370e8b1a205fe1a2acf55634b189c1cb49f57536a61f44f31a52598a`. The existing shared Python environment was used only to execute tests from this worktree with bytecode/cache writes disabled.

The requested [CSCS skill](/Users/foivoskarounos-zamparloukos/.claude/skills/optimize-apertus-cscs/SKILL.md) was read. This is an experiment-owned analysis transform and a static CPU sbatch payload; no canonical lifecycle tooling was changed. The explicit Clariden-only network and no-other-worktree constraints exclude a canonical-repository fetch. No certificate refresh occurred. One SSH banner timeout was retried once successfully; no authentication/certificate error occurred.

## Entry point and counts

- [`l1c_census.py`](../../../../../scripts/labelfix/clariden/l1c_census.py), standard library only; multiprocessing over L1R shards.
- [`l1c_job.sbatch`](../../../../../scripts/labelfix/clariden/l1c_job.sbatch): `debug`, `a0140`, one node, one task, 16 CPUs/workers, **30 minutes**. No GPU/inference operation; CUDA visibility is empty.
- [`test_l1c.py`](../../../../../tests/labelfix/test_l1c.py): **30 passed** ([log](L1C_evidence/tests_l1c.log)). All labelfix: **665 passed in 7.93 s** ([log](L1C_evidence/tests_labelfix.log)).

For PRESENCE, FULL and ENSEMBLE_AB, JSON and Markdown include overall, each of the six requested waves, each source, and every observed wave × source. Absent requested waves have explicit zero rows; unexpected wave/source names remain visible.

Exact reasons are `hold_slots[].detail`; the broad `reason` aliases are deliberately ignored. Slots count once per `(line, start, letter, exact detail)`. Separate line-guard counts preserve blank-letter original-label edit guards without inventing glyph slots. Raw entry counts are also available for diagnosing duplicate entries. ALONE counts a line only if the union of **all** its exact reasons is that singleton. Reason sets are sorted exact strings, counted once per line. Full counters survive in shard partials; the aggregate ranks globally before retaining its top 10, with lexical tie-breaking.

Line-family counts deduplicate lines within each family and may overlap. `crop_UNSEEN:*` and explicit cuts map to clipping; detector location/segmentation/physical/unnamed holds map to localisation/segmentation; `K1:*` maps to K1 and known observation wrappers also tag their underlying family; `edit_guard:*`, `ensemble_ab_mark_set_disagreement`, `mark_kind_disagreement`/`mark_set_disagreement`, and `r1_*` map to edit-guard, A/B disagreement, kind disagreement and R1 uncertainty respectively. The R1 family includes missing, unsupported and unscored evidence. Unknown exact reasons remain under `other/unclassified` and in all exact-reason tables.

## Receipt and timeout behavior

Before counting, the entry point requires L1R's complete top/shard receipts, complete upstream verification receipt, SF4 policy digest and pinned frozen gate hash. It checks the upstream verification-map digest and input bindings, then hashes **every declared L1R aggregate/shard output**, including selections, overlays, manifests, controls and kept IDs. Release payload hashes and policy/input bindings must agree. It never reopens historical detector arrays, inference predictions, original corpora or checkpoints.

Each worker checks line IDs, original-label SHA, status/reason consistency and shard status totals before atomically publishing `partials/shard-NNNNN/counts.json` and `receipt.json`. Final aggregation checks all mode/wave/source status totals against L1R manifests, rehashes the input outputs, and binds the census code before writing a complete final receipt. A timeout leaves completed shard receipts; rerunning the entry point with **the same input, code, job ID and `--out` directory** reuses only exact-bound partials. The sbatch default output name includes its own job ID, so reuse across a replacement allocation requires passing that earlier output directory to the Python entry point explicitly.

Output directory:

```text
.../l1r_sf4/l1c/output_<L1R_JOB_ID>_<L1C_JOB_ID>/
  binding.json
  input_verification.json
  partials/shard-NNNNN/{counts.json,receipt.json}
  CENSUS.json
  CENSUS.md
  receipt.json
```

The final receipt hashes both census files, binding, input verification and every partial receipt; each partial receipt hashes its own counts. Only small deployment/evidence files are transferred. The population and large outputs stay on Clariden.

## Exact-entry-point mock and hand checks

The existing **64-line verification L1R release** at `artifacts/labelfix_l1r/mock_final` was read without alteration. Its HOLD counts match the census: **PRESENCE 49, FULL 53, ENSEMBLE_AB 43** (held glyph slots 179, 185, 142). No detector, reader or gate was run. The final mock completed in **0.139 s**; its aggregate JSON and Markdown are approximately 86 KiB and 28 KiB. This is mock timing, not a production throughput qualification.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/labelfix/clariden/l1c_census.py \
  --input-dir artifacts/labelfix_l1r/mock_final \
  --workers 2 --out artifacts/labelfix_l1c/mock64_final
```

See [mock log](L1C_evidence/mock64_final.log), [receipt](L1C_evidence/mock_receipt.json), [JSON](L1C_evidence/mock64_CENSUS.json), [table](L1C_evidence/mock64_CENSUS.md) and [two hand checks](L1C_evidence/hand_checks.json).

| PRESENCE line | Manual exact slot counts | Held glyph slots | Exact reason ALONE | Families (lines) |
|---|---|---:|---|---|
| `9c1dca9b-p000015-l0067` | `detector_clipped_top` 2; `detector_clipped_bottom` 2; `mark_kind_disagreement` 1 | 4 | none | clipping 1; kind disagreement 1 |
| `263438a3-p000001-l0008` | `mark_kind_disagreement` 2 | 2 | `mark_kind_disagreement` 1 | kind disagreement 1 |

The first line's slot at offset 11 has two exact reasons and is counted once in each reason column, once in held slots. The second line contributes two reason slots but one ALONE line. Synthetic tests also cover duplicate events, a line with only an edit guard, unknown families, corrupt payloads/receipts, receipt path escapes, incomplete L1R, ambiguous job-ID paths, cross-mode/group totals, interrupted final aggregation and corrupt partials. A global-ranking counterexample proves a set outside **both** shard top tens can still rank first globally.

## Deployment and scheduler test

Deployment is beside L1R at:

```text
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf4/l1c/
```

The deployed files sit directly in that directory, outside L1R's frozen `scripts/` tree, so adding L1C does not change L1R's code-source map. Both remote payloads passed `sha256sum --check L1C_DEPLOY_SHA256.txt`; remote Python parsed the exact entry point and `bash -n` passed. [Deployment/test-only transcript](L1C_evidence/deploy_test_only.log).

```text
4823f491c8b357a9a39e0ae683d45b12556e5a1182c2920b3919de1e800619bc  l1c_census.py
adf2878c818b239feb287bce710348c13ca7a565c5d1a13afab6f294071f7f3d  l1c_job.sbatch
```

`L1C_DEPLOY_SHA256.txt` itself: local `7912df1437122d3b3732dfc483fbe08f9280358b35febd23a7ce4c295f4fae23`; remote `7912df1437122d3b3732dfc483fbe08f9280358b35febd23a7ce4c295f4fae23`. [Manifest](L1C_evidence/L1C_DEPLOY_SHA256.txt).

Initial exact scheduler probe:

```bash
sbatch --test-only --dependency=afterok:3679725 l1c_job.sbatch 3679725
```

```text
sbatch: error: QOSMaxSubmitJobPerUserLimit
allocation failure: Job violates accounting/QOS policy (job submit limit, user's size and/or time limits)
```

The live debug partition has `debug-qos` MaxSubmitPU=2, MaxJobsPU=1; one debug job was running (L1R 3679725), another pending. No job was cancelled or changed. [Read-only quota evidence](L1C_evidence/quota_status.log). After L1R completed, the **same scheduler probe passed** at `2026-10-17T02:25:58+02:00` (Clariden host time):

```text
sbatch: Job 3679760 to start at 02:25:59 a using 288 processors on nodes nid007647 in partition debug
```

This is `--test-only` planning output, **not a submitted job**. The following `squeue -u fffoivos -n labelfix_L1C` returned only its header. The payload requests 16 CPUs and runs 16 workers; the partition's exclusive allocation accounts for the 288 processors in this scheduler estimate. Both deployed files passed SHA checks again before this successful probe. [Final test-only transcript](L1C_evidence/test_only_final.log).

## Coordinator command — not executed

The brief's output layout and the deployed L1R job differ. Live Slurm's L1R command writes to `.../l1e_20261017/l1r_sf4_<L1R_JOB_ID>/`, while the brief names `.../l1r_sf4/output_<L1R_JOB_ID>/`. `--l1r-job-id` checks both, accepts exactly one resolved directory, and refuses missing or ambiguous inputs. No glob chooses a different run. L1R **3679725 completed with exit `0:0` in 7 min 2 s**. The final receipt exists and its SHA-256 is `5178bd808547d5a9c0756acc18d721ad4d0bd62a03d75fd80111972d24dcdea6`. Its completion flags and the bound input-verification receipt were checked in place; see [completion metadata](L1C_evidence/l1r_completion.json). The full production-output SHA traversal and census are intentionally deferred to the allocated entry point. The L1R aggregate release is 1.7 GiB and was not transferred.

After L1R completes successfully, the coordinator may run the following with its job ID. **This command has not been executed.**

```bash
L1R_JOB_ID=3679725
L1C_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf4/l1c
cd "$L1C_ROOT"
sha256sum --check L1C_DEPLOY_SHA256.txt
sbatch --dependency=afterok:"$L1R_JOB_ID" l1c_job.sbatch "$L1R_JOB_ID"
```

Estimated census runtime: **15 minutes**, planning estimate from the small mock plus full-population hashing/JSON overhead; request is capped at 30 minutes. No full-population census has been run and no production runtime is claimed.

L1C READY: analysis-only; mock ok; deploy sha256 7912df1437122d3b3732dfc483fbe08f9280358b35febd23a7ce4c295f4fae23/7912df1437122d3b3732dfc483fbe08f9280358b35febd23a7ce4c295f4fae23; test-only sbatch: Job 3679760 to start at 02:25:59 a using 288 processors on nodes nid007647 in partition debug; est 15 min
