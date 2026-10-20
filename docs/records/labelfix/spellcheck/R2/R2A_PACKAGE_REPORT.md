# R2J3 R2a + DEV package

Status: **DEPLOYED; remote SHA and test-only passed; LEAD COMMIT NEEDED before coordinator verifier.** No submission, certificate refresh, or `.git` writes. Network is used only for deploy, remote SHA and test-only.

The promised copied inputs were absent in this worktree. Preparation copied them read-only from R2cards and verified the requested manifest SHA `3dda20644c17b44e1a1c9f69781a9f1dd18657f6dc8b8b7e9cd14d8dd30a7667`. The original v1 had 1,573 slots (1,150 negative / 423 positive); active v2 has 1,572 (1,149 negative / 423 positive), all new identities, zero replacements. The T4 file has 791 witness cards. Crop staging binds 691 training lines, 747 witness lines, 600 DEV lines, 2,038 native crop files, 56,176,559 bytes. DEV truth SHA is `bbfba1509215d60517ab651324a44323f6a5cedd8378c97fdcadab48bc78a3ec`: 600 census lines / 1,793 items. Copied inputs and source roles remain separate from outputs.

## Width-gate resolution and accepted deviation

The lead ruled that the frozen R1 extractor gate stands with no exception path. V2 drops crop SHA `82e8f64cbca6e513163d4452641a51a215a0e744b8c4a338a6dc0fdf7ec740e8`, NFD start `46`, line `ia_poly1850--3773a91327e98bc0--s001-l0005`. This is a **negative subscript** slot: negative count decreases from 1,150 to **1,149**, positive remains **423**. The active manifest has **1,572** all-new identities, zero replacements. The slot is in `artifacts/r2a_manifest/quarantined.jsonl` with reason `frozen_extractor_width_gate`; original diagnostic reason is `width_outside_0.2_2.0_median_ctc`. Quarantine total is 259 (258 prior + this slot).

- V1, unchanged: `artifacts/r2a_manifest/r2a_slots.jsonl`, SHA256 `3dda20644c17b44e1a1c9f69781a9f1dd18657f6dc8b8b7e9cd14d8dd30a7667`.
- V2, active: `artifacts/r2a_manifest/r2a_slots_v2.jsonl`, SHA256 `20b24e0fa6831487568d3bf00bac928e0fcd94831db566c520535a8216a855e1`.

R2a admits 1,572 print-checked slots against the plan's 4,000; per-slice deficits recorded in B6_RESOLVE_REPORT.md; top-up reading paused by the owner (17 Oct)

This coordinator-accepted deviation is bound in the manifest receipt, config, custody record, and `r2_readback_verify.py` readback receipt template. [B6 slice table](B6_RESOLVE_REPORT.md) records v2 deficits. [Real-input preflight](evidence/r2a/r2j3_native_preflight.json) confirms **1,572/1,572** retained slots pass the unchanged frozen confidence/width gate. A regression test confirms the quarantined slot still fails the actual frozen extractor. The line remains staged because its other admitted slots survive.

## Recipe disclosure

| Parameter | BASE, job 3681404 | R2a | Difference |
|---|---|---|---|
| Frozen data | `labelfix_r1_20261016/output_3678928/data`, 300 train / 16 validation documents | Same exact data path and receipt | None |
| Training identities | 1,935,016 | 1,936,588 | +1,572 print-checked identities |
| Overlay | None | Hash-bound `artifacts/r2a_manifest/r2a_slots_v2.jsonl`; all heads known, native_print weight 1 | Only scientific intervention |
| Replacement semantics | Old pool | Identity keyed by crop SHA + recogniser NFD start; corrections replace in place; new identities append once | Explicit zero-overlap and cardinality assertions |
| Initial weights | Fresh MarkReader, random model seed; arm A, letter embedding, 1,766,571 parameters | Same | None; no teacher warm-start |
| Pixel contract | Original full height; 1.5 font-height left / 0.75 right; bilinear 64×128; wide view and span mask | Same on native overlay | New images only; frozen width gate preserved |
| Class weights | From frozen old train targets: sqrt(N/max(count,1)), cap 10, normalise each head to mean 1 | Same old-target arrays, unchanged computation | None; never recomputed on overlay |
| Per-sample weight / loss | Old=1; sum of four weighted cross-entropies | Old=1, native_print=1; existing ManifestPool weighted-loss code | Provenance accounting and overlay rows only |
| Epochs / step limit | 15 / no explicit limit | 15 / no explicit limit | None |
| Steps / epoch | ceil(1,935,016/512)=3,780 | ceil(1,936,588/512)=3,783 | +3 per epoch; 56,700 → 56,745 total updates |
| Epoch sample draws | 1,935,016 | 1,936,588 | +1,572; +23,580 over 15 epochs |
| Optimiser | AdamW; LR 0.001; weight decay 0.01; torch default betas (0.9,0.999), eps 1e-8, amsgrad false | Same exact trainer | None |
| LR schedule / clipping | Constant LR; no scheduler or gradient clipping | Same | None |
| Batch / loader | 512, workers 4, threads 8 per run | Same | None |
| Sampler | With replacement; 40% none, at least 5% rare/compound, remaining draws equal allocation across positive head/value pools; random shuffle | Same algorithm on combined target array | Pool membership and natural class counts change because of overlay |
| Rare rule | ≥2 nonzero heads OR composed class count <1,000 | Same, on combined targets | Overlay may change composed-class counts and rare membership |
| Seeds | Model and sampler 20261017/18; saved R1-A=20261016 | Model and sampler 20261016/17/18; sampler seed + epoch | Three R2a runs; BASE outputs read-only |
| Augmentation | None | None | None |
| Precision / runtime | CUDA bf16 autocast; TF32 runtime inherited from torch; channels_last; cudnn benchmark true | Same trainer | None |
| Evaluation / checkpoint | Natural old validation, unweighted sum of four cross-entropies each epoch; save minimum validation loss; held-out predictions on every improved best | Same | None |
| Parallelism | Two BASE seeds on two GPUs | Three R2a seeds on three GPUs, one exclusive four-GPU node | Third seed; one concurrent training wave |
| Time | Measured B=15.875 min, C=17.482 min | Forecast below | Additional cohort inference and scoring |

The mock uses explicit synthetic old/native pixels and a deterministic mock reader checkpoint, CPU fp32, batch 16, workers 0, threads 2, and one optimiser step per seed. Its A16/BASE fixture checkpoints deliberately share mock weights; it tests orchestration and schema, not scientific seed effects or GH200 performance.

## Job and scoring layout

`r2a_job.sbatch` is the exact local-mock / cluster entry point. A validates all hashes, crops, R2C roles, document separation and all-new identities. B extracts the native pool, witness pool and exact DEV census; native and DEV reuse saved alignments, while the witness cohort runs one shared recogniser alignment stage. C runs the frozen `r1_train.py` recipe for three seeds. D runs inference for A16, BASEs17, BASEs18 and R2a s16/s17/s18 on the same held-out, witness and DEV extraction.

Held-out scoring uses the job-1 666 non-DEV S4 lines, physical continuity instrument and symmetric v1.1 four-head overlay. Slot predictions, extraction/checkpoint hashes, raw and continuity scores, paired comparisons vs A16 and matching BASE seeds are saved. T4 emits one ledger row for every printed letter supplied by the 791 cards; unsupported, ambiguous or missing reader slots remain explicit UNKNOWN/unscored. Target witness comparisons retain capital/omicron/subscript anchor negatives, positive regressions/recoveries and document-cluster intervals. DEV retains all 1,793 item states, controls, original inclusion weights, waves, UNKNOWN exclusions and word-range starts; only resolved noncontrol cards enter metrics. No UNKNOWN labels become negative targets.

A-D stage receipts have the same `stage`, `binding`, `complete`, `elapsed_seconds`, `result`, `sha256` fields used by B2. The readback verifier adds an optional `--remote` metadata argument; its existing receipt schema and default job-1 behaviour remain unchanged.

## Forecast

Measured job-1 B (47,129-line teacher export) = 15.9 min; C (parallel BASE seeds) = 17.5 min. Conservatively budget 15.9 min for this much smaller staging/extraction stage, including 747 new witness alignments; 17.5 min for three simultaneous R2a seeds (sample count +0.0813%); 20 min provisional reserve for six-arm, three-cohort inference and scoring. Total **53.4 min**. 1.5× = 80.1 min; request **81 min** (`#SBATCH --time=01:21:00` and `--time=81`). The 20-minute inference reserve is a forecast, not a measured qualification; no run is launched locally to establish production timing.

## Validation and package custody

Mock **pass**: [exact entry-point log](evidence/r2a/r2j3_mock.log), `artifacts/labelfix_r2a/r2j3_mock/mock_receipt.json`. It covers A→B→C→D, replacement rather than append, native/witness/DEV extraction, six-arm predictions/scoring and recursive receipt/hash validation. Automated integration also invokes the exact sbatch script.

Tests: **65 passed** in [test log](evidence/r2a/r2j3_tests.log). Existing `test_r2.py`, `test_r2_population.py`, `test_r2_readback_digest.py`, frozen-policy tests, plus `test_r2a_package.py`. New tests cover all-new overlay loading, duplicate/existing-identity rejection, replace-not-append, document leakage, saved-text mismatch, native/source receipts, DEV controls/UNKNOWN/weights, ambiguous witness alignment, target comparisons and complete sbatch receipts.

Frozen check: 41 distinct files across `greekocr/labelfix` and the 16 policy paths compare byte-for-byte to HEAD. Policy digest remains `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`. [Receipt](evidence/r2a/r2j3_frozen_check.json).

Package payload count and SHA envelope are recorded in [package receipt](evidence/r2a/package_receipt.json) and `R2A_DEPLOY_SHA256.txt`. Every deployed payload path is SHA-bound, including `R2A_DEPLOY_FILES.txt`. Exact files requiring the lead's commit, plus the report and handoff evidence, are listed in [LEAD_COMMIT_PATHS.txt](evidence/r2a/LEAD_COMMIT_PATHS.txt). No git index or repository metadata mutation was performed.

Verifier prerequisite checked **before deployment** by reading `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1e/scripts/ops/verify_deploy.py`: it rejects tracked-but-uncommitted paths and requires each payload hash to match the specified commit, absent an explicitly permitted ignored-file exemption. No exemption is requested. **LEAD COMMIT NEEDED**; verifier is deferred until after the lead commits. Remote SHA binds the same payload bytes that the lead will commit.

```sh
git add --pathspec-from-file=docs/records/labelfix/spellcheck/R2/evidence/r2a/LEAD_COMMIT_PATHS.txt
```

## Deployment and commands

Remote SHA comparison: **2,454/2,454 payload files match**, plus separately verified `R2A_DEPLOY_SHA256.txt` envelope (2,455 transferred files including that envelope). [Remote SHA output](evidence/r2a/remote_sha.txt), [manifest envelope](evidence/r2a/remote_manifest_sha.txt), [deploy receipt](evidence/r2a/deploy_receipt.json). `sbatch --test-only --time=81`: **OK**, return code 0; [output](evidence/r2a/test_only.txt). Coordinator verifier: **LEAD COMMIT NEEDED**, not run because its committed-file prerequisite was confirmed before deployment. Job 1's root is untouched. No job was submitted, no certificate refreshed, and no `.git` writes performed. Final local rehash confirms that all payload bytes still equal the remotely checked package.

Local package build: `PYTHONPATH=. /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B -m scripts.labelfix.clariden.r2a_deploy`. Authorised deploy/SHA/test-only: same command with `--deploy`. The deploy uses only listed files, validates every remote hash and the SHA manifest envelope, and invokes only `sbatch --test-only --time=81`. Any authentication/certificate error means STOP, never refresh. Certificate deadline: 17 Oct 19:18 Athens.

Coordinator verifier invocation after lead commit (saved verbatim in [VERIFY_CMD.sh](evidence/r2a/VERIFY_CMD.sh); run `sh docs/records/labelfix/spellcheck/R2/evidence/r2a/VERIFY_CMD.sh`):

```sh
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1e/scripts/ops/verify_deploy.py \
  --repo "$PWD" --commit "$(git rev-parse HEAD)" \
  --sha-file R2A_DEPLOY_SHA256.txt --remote-root /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017 \
  --sbatch scripts/labelfix/clariden/r2a_job.sbatch --sbatch-args=--time=81 \
  --out docs/records/labelfix/spellcheck/R2/evidence/r2a/verify_deploy.json
```

**Coordinator-only future submit command; never executed here:**

```sh
ssh clariden 'cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017 && sbatch --time=81 scripts/labelfix/clariden/r2a_job.sbatch'
```

Readback after the coordinator's job finishes (replace the numeric ID):

```sh
R2A_JOB=REPLACE_WITH_JOB_ID
mkdir -p artifacts/labelfix_r2a/readback
date -u +%FT%TZ > artifacts/labelfix_r2a/readback/start.txt
ssh clariden "cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017/output_$R2A_JOB && find . -type f -printf '%P\0' | sort -z | xargs -0 sha256sum" > artifacts/labelfix_r2a/readback/envelope.sha256
rsync -a "clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017/output_$R2A_JOB/" "artifacts/labelfix_r2a/readback/output_$R2A_JOB/"
PYTHONPATH=. /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B scripts/labelfix/r2_readback_verify.py \
  "artifacts/labelfix_r2a/readback/output_$R2A_JOB" artifacts/labelfix_r2a/readback/envelope.sha256 \
  artifacts/labelfix_r2a/readback/start.txt --remote "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017/output_$R2A_JOB/"
rsync -a "clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017/logs/R2a_$R2A_JOB.log" artifacts/labelfix_r2a/readback/
```


R2J3 READY: slots 1572 (neg 1149/pos 423); manifest v2 sha 20b24e0fa683; mock pass; tests 65; deployed 2454 files sha match 2454/2454; test-only ok; lead commit list docs/records/labelfix/spellcheck/R2/evidence/r2a/LEAD_COMMIT_PATHS.txt; verify cmd docs/records/labelfix/spellcheck/R2/evidence/r2a/VERIFY_CMD.sh

## Root resolution check (lead, 17 Oct; the wave-1e lesson: test-only cannot catch a wrong working root)

`scripts/labelfix/clariden/r2a_job.sbatch`, non-mock path, lines 18–23:
- sets `R2_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017` and `cd "$R2_ROOT"`;
- runs `sha256sum --check R2A_DEPLOY_SHA256.txt` inside that root before any work;
- exports `PYTHONPATH="$R2_ROOT"`;
- runs the absolute interpreter `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python` on the relative script
  `scripts/labelfix/clariden/r2a_run.py`.

The training subprocess (`r2a_run.py` line 228) uses `sys.executable` with a relative script path, so it inherits that working
directory and PYTHONPATH.

Every module `r2a_run.py` imports is in `R2A_DEPLOY_FILES.txt`:
- `r1_common`, `r2_util`, `r2_run`, `r2_teacher`, `r1_extract`, `r1_train`;
- `greekocr/__init__.py` and `greekocr/labelfix/__init__.py`.

`scripts/` is imported as a namespace package (no `__init__.py`), the same as job 1 (3681404), which ran from its own root.

## R2J4 — preserve BASE duplicates and verify real stage A+B

Job 3682401 failed in stage B after extracting 691 native, 747 witness and 600 DEV lines: the previous `ManifestPool` assumed old identities were unique. BASE job 3681404 instead read this exact frozen pool through `r1_train.Shards`, preserving duplicates. The failed directory was renamed, without deletion, from `output_3682401` to `failed_output_3682401`; the [failure log tail and rename readback](evidence/r2a/r2j4_failed_log_tail.txt) preserve the failure.

The read-only login-node [full old-pool audit](evidence/r2a/old_pool_duplicates.json) found **1,935,016 old rows, 1,935,011 unique keys, five repeated keys and ten participating duplicate rows** (five excess rows). All five groups are class **a**, identical crop bytes under different crop paths/line IDs; classes **b/c/d are 0/0/0**. Actual crop bytes at the inventory's remote `path` were SHA-verified for every duplicate group, rather than relying only on the inventory digest. Every group's targets are identical. There are only five duplicate groups, so the requested ten distinct examples do not exist: all five groups, with all ten rows, are included. The reproducible audit is `scripts/labelfix/clariden/r2a_diagnose.py`.

The lead ruling is implemented without deduplication: old rows have index handles, identity maps to a list of old indices, and old order, targets, sample weights and pixel/index fields remain intact. An overlay key, `replaces`, or `removes` resolving to multiple old indices stops with `ambiguous old identity for replacement`. New overlay keys remain unique and absent from the old key set. All 1,572 active overlay slots are new, with **zero hits on any old key, including duplicated old keys**. Manifest and runtime overlay receipts record `old_rows`, `old_unique_keys`, `old_duplicate_rows`, `old_excess_rows`, `old_duplicate_groups` and `overlay_hits_on_duplicated_keys`. Here “duplicate rows” means every participating row, not only excess occurrences. The scientific intervention remains the overlay alone.

An EMPTY-manifest fixture with duplicated old keys reproduces the `Shards` index/target array and the complete `ArmBatches` sample sequence for seed 20261017. Every sampled item, including its returned index, targets and pixels, is compared; old weights remain one. Additional regressions cover all three ambiguous-key operations and the preservation of duplicate old rows when adding new overlay slots. [Tests](evidence/r2a/r2j4_tests.log): **71 passed**. [Exact sbatch-entry mock](evidence/r2a/r2j4_mock.log): **R2A_MOCK_PASS**, A→D. [Frozen-code check](evidence/r2a/r2j4_frozen_check.json) confirms no changes to `greekocr/labelfix`; frozen-policy tests pass.

The package verify step now runs `r2a_run.py --dry-run-ab` on the login node after remote SHA verification and before test-only. This mode refuses an existing allocation, confines real output to the remote root's `dryrun/`, hides CUDA devices, uses two torch threads and one extraction worker, and returns after writing stage B's overlay receipt. It validates all real inputs in A, extracts all 691 native lines so every overlay slot is exercised, and uses fixed first-two-line witness/DEV slices. The witness slice uses the failed run's saved real recogniser alignments, whose SHA enters the dry-run binding; it performs no new recognition or GPU work. Crucially, B constructs `ManifestPool` over the **full 1,935,016-row old pool and full 1,572-slot overlay**, then checks every old row's sequence, target and weight. No training or stage C/D is reachable in this mode.

Real-input dry run: **exit 0**, `STAGE_DONE A`, `STAGE_DONE B`, `REAL_INPUT_AB_DRY_RUN_PASS`; [full stdout/stderr and command](evidence/r2a/dryrun_stageAB.txt), [remote overlay and dry-run receipt readback](evidence/r2a/r2j4_real_receipts.txt). Output: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017/dryrun/r2j4_20261017T123303Z/`. The resulting training pool has **1,936,588 rows** (1,936,583 distinct keys); `old_sequence_assertion=pass`, no quarantine, and all old/new counts match the diagnosis. The runtime receipt's `old_pool_identity=false` correctly describes a pool with appended overlay rows; the separate old-sequence assertion passes.

Redeployment completed **17 October 2026, 15:36 Athens**, to the same remote root: **2,455/2,455 payload SHAs match**, with the SHA-manifest envelope separately verified. [Deploy log](evidence/r2a/r2j4_deploy.log), [deploy receipt](evidence/r2a/deploy_receipt.json), [remote payload hashes](evidence/r2a/remote_sha.txt), [envelope](evidence/r2a/remote_manifest_sha.txt), [test-only output](evidence/r2a/test_only.txt). `sbatch --test-only --time=81` returned **0**; its printed hypothetical job/start estimate is a test-only result, not a submission. The complete mock and tests passed before redeployment.

The coordinator verifier invocation in [VERIFY_CMD.sh](evidence/r2a/VERIFY_CMD.sh) remains the same and requires the lead's commit; no `.git` writes, certificate refresh, allocation or job submission are performed here.

Standalone package real-input verification (login node only, no submission): `PYTHONPATH=. /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B -m scripts.labelfix.clariden.r2a_deploy --verify-dry-run`. Normal `--deploy` runs this check automatically between SHA verification and test-only.

R2J4 READY: old rows 1935016, unique keys 1935011, duplicate rows 10 (classes a/b/c/d 5/0/0/0 groups); overlay hits on duplicated keys 0; equivalence test pass; real-input A+B dry run exit 0; deployed 2455 sha match 2455/2455; test-only ok; lead commit list docs/records/labelfix/spellcheck/R2/evidence/r2a/LEAD_COMMIT_PATHS.txt
