# TR2 — sf7-A v2_test/dev Clariden package

19 October 2026. Preparation only; no job submitted, allocation requested, model trained, label bound, or `.git` files written. Network use was restricted to Clariden. The production root is `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019`.

## Population and recipe

The package selects every `greek_poly` row from the matching raw import, including Wikisource: **28,620 test + 8,110 dev = 36,730 lines**. Exact sorted IDs are the TR1 inventories. The remote intake verifies the raw-parent hashes, IDs, duplicate/canonical line identities, crop paths, and test/dev/train document and line disjointness. Each split preserves its own raw parent and original label bytes; train exclusions are not repurposed as held-out exclusions.

| Split | Parent under `collection_v2/` | SHA-256 |
|---|---|---|
| test | `import_real_v2_test.jsonl` | `e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8` |
| dev | `import_real_v2_dev.jsonl` | `d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17` |

Production runs fresh C1 recognition/alignment (four workers, chunk 512, batch 16), archived L1 S6 detection/window extraction, archived reader-A inference, existing L1E window audit and B/E inference, GC1 SF7-A recomposition, then RB7 byte-patch conversion. Reader policy is **ENSEMBLE_AB**; E is retained only because the existing inference route executes B/E. No model code was written. The isolated legacy dependency files are verbatim copies from the saved train package, not new implementations.

The copied L1 detector and A-inference files match the remote train package byte-for-byte: detector SHA `e18a7dc8c84e29c8f681591a1dc3a5d694ede8cc18fdfc86ccac13c33857b922`, inference SHA `0710ca4c41c13b6804dcd8beacf16d0b7732cc76403c02a93abf1e40de2875ba`. The full legacy S6 dependency binding matches all frozen hashes ([comparison](TR2_evidence/legacy_s6_exact.json)). The reader model is byte-identical, and AST comparison proves recogniser forward/strip/span decoding unchanged except retention of frame scores, plus identical reader prediction code ([forward identity](TR2_evidence/forward_identity.json)). The C1 copy only admits a bounded CPU dry run; the recompose copy parameterises the population count and emits A. [Parameter diff](TR2_evidence/parameterisation.diff).

| Asset, same as train | SHA-256 |
|---|---|
| E3 recogniser `full_s0/best.pt` | `5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663` |
| Recogniser safetensors | `e468155d6130be4b7359d94ec197a357ad55b0dc7947104afc1336c352a6c6df` |
| Reader A, R1 job 3678928 | `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636` |
| Reader B | `f25f16e633966ec16037099e27ee75624b9a3600d96682dca654aeded9396d69` |
| Reader E | `330b43a04dc47425d3da977f06f28aaa54bee681700d81feef0bcb8ea1ed42c5` |

All checkpoint hashes and the L1F historical model/codec source hashes are checked remotely by intake. Full paths and bindings are in [recipe identity](TR2_evidence/recipe_identity.json) and [config](../../../config/tr2_job.json).

The original policy files, including the train-root `sf7_job.sbatch`, remain untouched. Policy is `sf7-release-v1`, addition variant **A**, digest **`f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047`**. Preregistration SHA is `64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d`.

Fresh frame confidences, alignments, line and regional scores are retained remotely. L1F's unchanged `make_record` constructs the separate score records from the already scored C1 forward, avoiding an unnecessary second recognition pass. The archived L1 detector omits the confidence fields in composer runtime, as train did. Newly measured scores are **not** promoted into SF7 deletion decisions. This preserves the train composer evidence contract while retaining new scores for inspection.

## Validation and deployment

The local mock runs the exact outer sbatch entry point and manifest checks, then the saved 64-line inference fixture through SF7-A and RB7. It exits 0, produces 13 edited rows / 15 edits, and verifies exact forward/reverse UTF-8 patch reconstruction. It does not run the models locally. [Mock receipt](TR2_evidence/mock_receipt.json), [log](TR2_evidence/mock_final.log).

The initial remote preflight exposed a missing vendored codec JSON in the GC1-derived payload. It was added to the manifest. The subsequent 500-line raw-parent/crop preflight exited 0. The first full CPU attempt completed 250 fresh test CTC alignments, then exposed missing S4/S5 detector JSON assets. Both assets were added and checked against the train copies. That failed attempt was stopped; the retry reuses only its complete, SHA-checked CTC alignment output under exact selection/checkpoint bindings. A deeper comparison then found that current S6 library/window code differs from the original L1 binding. Those intermediate overlays are not qualification evidence. The final package isolates the complete byte-frozen L1 source dependencies in `legacy_l1/`; a separate detector interpreter prepends that directory to its import path while the sbatch keeps `PYTHONPATH=root`. Every frozen source/asset hash is checked before inference. The final 500-line retry, `dryrun_500_legacy_v3`, reuses only the complete, SHA-checked fresh CTC alignments; it repeats detection, windows, readers, scoring, composition and conversion under the corrected recipe. The final dry run completed successfully, as detailed below.

The outer [sbatch](../../../scripts/labelfix/clariden/tr2_job.sbatch) changes to its own root, checks `TR2_DEPLOY_SHA256.txt` there, and exports `PYTHONPATH=root`. Production requires a Slurm allocation with four GPUs. The login dry-run branch uses no `srun` or GPU allocation. Requested resources: account `a0140`, partition `normal`, one exclusive four-GH200 node, 64 task CPUs, **`01:00:00` (60 minutes)**. The scheduler's exclusive-node accounting reports 288 processors.

Deployment has **687/687 payload SHA matches**, plus the SHA-manifest envelope. Manifest SHA: `134c03d6b68a9f24d163976e60b5559633c1c6c56c09be57e9aa76fd27a60395`. `sbatch --test-only scripts/labelfix/clariden/tr2_job.sbatch` exits 0. Its printed prospective job number is not a submission. [Original TR2 deployment and debug scheduler evidence](TR2_evidence/deploy_test_only.log); current TR2b validation is recorded below.

Final real-input run: **exit 0; 500/500 lines**, all CPU, under `dryrun_500_legacy_v3/`. The 250 test and 250 dev IDs are the first eligible rows in each matching raw parent. Both fresh CTC alignment files were reused from the earlier CPU attempts after selection, checkpoint, completion and output-SHA checks. The final frozen S6/windows/readers/scoring/composer/converter pass took **310.06 seconds**, excluding those earlier CTC passes and preparation. This is a correctness check, not GPU throughput qualification. The intake receipt's pending-stage fields describe the pre-inference snapshot; final `inference_executed: true`, complete output receipts and recorded process exit 0 establish completion.

| Final CPU slice | Composed corrected | Unchanged | HOLD | Edits-only rows | Edits | Score/alignment identities matched |
|---|---:|---:|---:|---:|---:|---:|
| test | 3 | 16 | 231 | 2 | 2 | 250/250 |
| dev | 7 | 70 | 173 | 7 | 7 | 250/250 |

One test composer correction is normalization-only and is explicitly omitted from the byte-patch release. Independent readback exits 0 and verifies every released patch forward and backward against the raw parent, output hashes, exact selected membership, overlay/control membership, and all 500 score identities. These candidate edits are not an accuracy audit. [Independent readback](TR2_evidence/real_input_readback.json), [verifier](TR2_evidence/readback_dryrun.py), [complete final log, starting with recorded exit code](TR2_evidence/real_input_final.log). No GPU was needed for this bounded validation; production remains allocation-only with four GPUs. The final run was launched with an exit-code file so a transport timeout could not hide its status.

## Outputs, forecast and handoff

Each eventual `output_<JOB>/{test,dev}/` contains its independent selection, pixel inventory, fresh alignments and frame scores, S6/window shards, A/B/E runtime, SF7-A overlay and controls, and separate edits-only release and receipt:

- `test/release_edits_only_test_A.jsonl` + `test/RELEASE_RECEIPT_test.json`;
- `dev/release_edits_only_dev_A.jsonl` + `dev/RELEASE_RECEIPT_dev.json`.

Both carry release ID **`sf7_rc1_test_edits_A`**, `parent: google_raw_v2_import`, matching parent SHA, future actual Slurm source job, split, policy digest, per-edit provenance and byte patches. Receipts remain `candidate_pre_audit`, `bound: false`. Conversion rejects unselected/duplicate IDs, changed raw labels, missing coverage and unchanged output rows; it reconstructs both directions from byte spans and reads the written output back. Composer-only normalization rows are explicitly excluded.

Forecast remains **40 minutes after allocation**, excluding queue delay, **2.67 allocated GPU-hours**; requested limit is forecast × 1.5 = **60 minutes**. It is the conservative TR1 historical estimate, not a new GPU throughput measurement. All substantial inputs and outputs stay on Clariden. Deployment streamed about 20 MB of existing code/fixtures directly to the remote root; no checkpoints, raw imports, crops, production arrays or full overlays were downloaded to the Mac.

The coordinator must commit [LEAD_COMMIT_PATHS.txt](TR2_evidence/LEAD_COMMIT_PATHS.txt), then run [VERIFY_CMD.sh](TR2_evidence/VERIFY_CMD.sh), which invokes the existing `greek-page-ocr-wave1e/scripts/ops/verify_deploy.py`. Existing ignored mock fixtures are explicitly hashed and admitted by its `--allow-untracked` option. The committed-source verifier is prepared, not claimed passed against uncommitted files. No staging or commit was performed.

Owner-only future submission command, **not executed**:

```bash
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019 && sha256sum --check TR2_DEPLOY_SHA256.txt && sbatch --parsable scripts/labelfix/clariden/tr2_job.sbatch
```

## Original TR2 Codex meter

The requested launcher was invoked at start and after mock, preflight and deployment. Its child `codex exec` cannot initialise inside this sandbox; its empty-session parser incorrectly prints a stale 28% value. Those printed values are invalid. Fresh telemetry from this exact TR2 session provides the fallback readings: **29% at start and early gates; 30% after the final mock**, below the 60% stop threshold. Raw launcher errors and timestamped telemetry receipts are retained in `TR2_evidence/budget_*`.

Observed meter change: **1 weekly percentage point (29% → 30%) and 0.000000 paid credits** (balance `59974.7137450000` unchanged). The meter exposes no task-specific point counter or conversion tariff; an exact total in “Codex points” cannot be truthfully inferred from these rounded quota readings. The final post-dry-run reading is **30%**, versus **29%** at start: **1 account-wide weekly percentage point observed**, with **0.000000 paid credits debited**. Exact TR2-attributable points are unavailable; concurrent account use and rounded quota readings cannot provide a task-specific charge. [Final meter receipt](TR2_evidence/budget_dryrun_final.json).


## TR2b partition correction and validation

Only `#SBATCH --partition=debug` changed to `#SBATCH --partition=normal` in `scripts/labelfix/clariden/tr2_job.sbatch`. All other sbatch bytes are identical, including `--time=01:00:00`, account, node, GPU and CPU directives. The forecast remains 40 minutes × 1.5 = 60 minutes.

`ssh clariden true` exited 0; no certificate refresh or re-sign was attempted. Before editing, local and remote sbatch SHA-256 both equalled `3cd8e918074f352d4723ea13627edd95bebdeecf8b1712fb0eff3b94d2b4e6db`. After editing, both equal `4ca588f514313390f7ec197801a22611a785121f0fd4235c6a614ef2a77927e6`.

The same original TR2 tool, `python3 -B /private/tmp/tr2_manifest.py`, regenerated the deployment manifests. Exactly one of the 687 SHA entries changed. `TR2_DEPLOY_FILES.txt` stayed byte-identical, SHA `75b28d0789d7abcf66f6eaee46facea68e7fe6538cc839ebc7775e8146c934c8`; it contains paths only and does not embed the SHA manifest. Only the sbatch and `TR2_DEPLOY_SHA256.txt` were transferred to the remote root. Full remote `sha256sum --check TR2_DEPLOY_SHA256.txt` exited 0 with **687/687 lines OK**, and the remote manifest SHA matched the local manifest SHA shown above.

From the remote root, `sbatch --test-only scripts/labelfix/clariden/tr2_job.sbatch` exited 0 and printed:

```text
sbatch: Job 3702820 to start at Tomorr 01:52 a using 288 processors on nodes nid006273 in partition normal
```

This is scheduler validation only; no submission was made. Local `bash -n scripts/labelfix/clariden/tr2_job.sbatch` passed. The local mock was not rerun: the partition directive is a Bash comment when the exact entry point `bash scripts/labelfix/clariden/tr2_job.sbatch --mock ...` runs, so it cannot affect mock execution. Every local payload hash was verified before editing; regeneration changed only the sbatch hash.

Expected production outputs remain `output_<JOB>/test/release_edits_only_test_A.jsonl`, `output_<JOB>/test/RELEASE_RECEIPT_test.json`, `output_<JOB>/dev/release_edits_only_dev_A.jsonl`, and `output_<JOB>/dev/RELEASE_RECEIPT_dev.json`. Receipts remain `candidate_pre_audit`, `bound: false`.

Codex weekly readings **before: unavailable; after: unavailable**. `artifacts/tr2/launchers/limit_probe.sh` was inspected but cannot run under this task's sandbox/network restrictions: it launches a child Codex service call outside the Clariden-only network allowance and writes probe/session artifacts. No weekly reading or task debit is inferred from the historical TR2 meter above.

Changed local paths are the sbatch, SHA manifest, this report, and `TR2_evidence/LEAD_COMMIT_PATHS.txt`. The lead list preserves the original TR2 paths and puts these four first. The coordinator must commit those paths and then run `VERIFY_CMD.sh`; committed-source verification is not claimed passed before that commit. No `.git` writes, production execution, or job submission occurred.

TR2b READY: partition normal; time 01:00:00; remote sha 687/687; test-only ok; manifest 134c03d6b68a9f24d163976e60b5559633c1c6c56c09be57e9aa76fd27a60395
