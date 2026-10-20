# R2P reader preparation

Preparation package validated locally. **No job submitted or allocation requested.**
Production remains **PENDING the lead's complete R2C population and document-role binding**.
R2a stays off until its admitted card manifest is supplied. The owner alone refreshes
the certificate; only the coordinator submits. The current config deliberately fails
Stage A for missing population. No partial teacher population is silently substituted.

## Recipe disclosure

Binding: [3678928-A receipt](../clariden/R1_result_3678928/run_receipt.json).
Every configuration and derived-model field in its A record is disclosed here.

| Parameter | 3678928-A receipt | R2 production | Difference |
|---|---|---|---|
| embedding | True | True | none |
| left_heights | 1.5 | 1.5 | none |
| balanced | True | True | none |
| none_fraction | 0.4 | 0.4 | none |
| rare_min_fraction | 0.05 | 0.05 | none |
| epochs | 15 | 15 | none |
| batch_size | 512 | 512 | none |
| optimizer | AdamW | AdamW | none |
| lr | 0.001 | 0.001 | none |
| weight_decay | 0.01 | 0.01 | none |
| seed | 20261016 | BASE 20261017/18; R2a 20261016/17/18 | seed only |
| steps_limit | None | None | none |
| precision | bf16 | bf16 | none |
| validation | natural distribution, unweighted sum of four cross entropies | natural distribution, unweighted sum of four cross entropies | none |
| parameters | 1766571 | 1766571 | none |
| forward_flops | 111277568 | 111277568 | none |
| approximate_train_flops | 333832704 | 333832704 | none |
| convention | conv/linear multiply+add=2; backward about 2x forward | conv/linear multiply+add=2; backward about 2x forward | none |
| arm | A | A | none |
| sampler seed | implicit 20261016 + epoch | each run seed + epoch; default unchanged | seed only |
| embedding dimension | 64 (model code) | 64 | none |
| window / resize / channels | 1.5 left / 0.75 right font heights; full crop; 64×128; grey + span mask | identical R1 code | none |
| class weights | sqrt(N/max(count,1)), cap 10, mean normalised | same frozen-old-pool class weights, multiplied by provenance | manifest only |
| document split | 300 train / 16 validation documents | same frozen extraction/split | none |
| manifest | old C1 pool, weight 1 | BASE same; R2a bound overlay if supplied | manifest only |

| Receipt observation, not parameter | R1-A | R2 |
|---|---|---|
| best_validation_loss | 0.016111664267017545 | production not run |
| bounded_mock | False | production not run |
| completed_epochs | 15 | production not run |
| forward_backward_samples_per_second | 34987.272062572774 | production not run |
| loader_wait_seconds | 93.75451734988019 | production not run |
| steps | 56700 | production not run |
| total_training_samples | 29025240 | production not run |
| training_seconds | 829.5942578229588 | production not run |

The job trainer (`bb4ab38d…`) was retrieved read-only from Clariden and captured
beside the pre-edit current trainer. Their training paths are identical; the
current pre-edit version adds chosen-value confidence to prediction exports.
Tests compare the job trainer against the new trainer for the first **200 batches
/ 3,200 sampled indices**, all initial tensors, and two CPU optimiser updates.
An old-only manifest gives identical losses and best-checkpoint tensors.
Checkpoint container bytes and timing/receipts differ because bindings and
observations differ. Production GPU numerical identity has not been rerun.

Mock-only departures: CPU fp32, batch 16, zero workers, two Torch threads,
one update per run (five total), four synthetic extraction lines and two native
test crops for actual frozen recogniser + teacher inference. These are bounded
execution checks, not R2 configurations. Production retains the recipe above.
Teacher inference follows L1 fp32 / TF32 off, exact E3 checkpoint, codec and
preprocessing. The new provenance logging throughput is not yet GPU-qualified.

## Implementation and evidence

- Model/sampler seeds exposed; document splitting unchanged.
- Unique identity manifests retain old order, replace in place, reject duplicate
  modification/collisions, support removals, and quarantine a whole slot if ANY
  head is unknown. Weights old/native/pseudo/override = 1/1/0.5/1. Class weights
  are fixed from the frozen old training targets; provenance multiplies per-sample CE while retaining
  its original per-head class-weight denominator. Per-epoch logs include unique
  counts, realised draws and effective class×provenance mass by head/provenance.
- New native slots consume teacher recogniser alignments and unchanged R1
  extraction geometry; their targets come from the independent manifest.
- Teacher exports full four-head softmax, argmax, top probability and margin;
  checkpoint/code/codec/crop/population hashes and crop/locator diagnostics.
  Invalid windows retain probabilities and explicit validity states, not labels.
  Edge-ink clipping flags are conservative diagnostics, not manual ownership
  certification. Train and validation-reserve exports are physically separate.
- Raw union scoring preserves base case and ignores marks during base alignment;
  unmatched printed positives are FN, inserted predicted positives FP. It reports
  exact named confusion and per-value TP/FP/FN/TN, tuple accuracy, dialytika
  compounds, false additions per 1,000 negative opportunities, state counts,
  source/book micro and macro, and undefined macro-cell counts.
- Paired tuple/head gain-loss ledgers use document-cluster bootstrap intervals
  and original inclusion weights. Three predictions of one word are not treated
  as three truths. Sparse native class claims still require independent support.
- The unchanged R1 physical-slot instrument remains a separate continuity view.
  Tests exactly reproduce R1-A's raw/scored/fused/per-class/per-book summaries,
  including **206 apostrophe FNs** beside the four-head result.
- A second output runs the existing frozen whole-line correction policy on the
  same saved detector/recogniser/peer runtime for both checkpoints. It counts
  correct/incorrect head additions, substitutions and deletions, Google error
  recovery/regression, yield, abstention and subscript-addition precision. No
  pipeline metric is inferred when complete saved runtime is unavailable.
- Overlay v0/v1 is symmetric. The owner η correction is circumflex with breathing
  UNKNOWN, pending full-tuple re-adjudication. Known head results remain usable;
  unresolved tuples are excluded from composed accuracy. Frozen
  `print_truth_s0.json` is untouched.

[Input formats and commands](INPUT_FORMATS.md) document the role binding, full
population completeness check, manifests, optional native pool, scorer and R2a
switch. The lead owns eligibility, canonical aliases and deterministic stratified
10% document reservation. No admission audit, new truth or native pool is
certified here. Frozen physical truth is a continuity adapter; genuinely new
union truth still needs complete independently printed bases and ownership states.

## Validation

**1,447 labelfix tests passed**, with no existing test changed or weakened.
[Full log](evidence/all_tests_final.log). Initial full-suite failures came from an
absent 47,790-byte frozen SF5 fixture, restored inside this worktree's artifacts
from the sibling checkout. The suite passed with the original frozen files.

The exact entry point was `bash scripts/labelfix/clariden/r2_job.sbatch` with
`R2_MOCK=1`, the requested venv as `R2_PYTHON`, and `R2_CONFIG` / `R2_OUT` set to
`artifacts/labelfix_r2/mock_inputs_final/config.json` / `mock_run_final_checked`.
All **A–D completed**, including R2a: [mock log](evidence/mock_final.log),
[summary](evidence/mock_summary.json). Repeating that entry point resumed all
four stages without new inference or training: [resume log](evidence/mock_resume.log).
Atomic stage/chunk receipts bind code/configuration and verify output hashes.
Incomplete training is preserved under an interrupted name and rerun; resume is
at seed/stage boundaries, not mid-epoch optimiser-state continuation.

A scorer CLI smoke test wrote both views for v0/v1 using a synthetic witness:
[raw and continuity](evidence/scorer_smoke/raw_and_continuity.json),
[fixed pipeline](evidence/scorer_smoke/fixed_pipeline.json). This checks the
interface, not reader quality.

All **30 files under `greekocr/labelfix` are byte-identical**, and
`release_gate.policy_binding()` is unchanged:
`6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`.
[Before](evidence/frozen_before.json), [after](evidence/frozen_after.json).
No Git mutation, certificate refresh, real job submission or allocation request
was issued. No other worktree was written.

## Throughput × draws forecast

| Stage | Work | Basis / forecast |
|---|---|---|
| A | input and extraction hash verification | I/O overhead, not measured on GH200 |
| C BASE | 2 × 15 × 1,935,016 = 58,050,480 draws | 34,987.27 draws/s → 27.65 GPU-min; parallel wall 13.83 min |
| D R2a | up to 3 × 15 × 1,939,016 = 87,255,720 draws | 41.57 GPU-min; parallel wall 13.86 min |
| C + D | two GPU waves, validation/checkpoint/export overhead | 30 min planning reference |
| B | new population of N lines: alignment → windows → teacher | historical upper reference 50 × N / 124,669 min |

Stage B CPU mock: 2 native lines / 36 slots; alignment 0.3404 s, windows 0.0184 s, teacher 0.1985 s. Export processing wall 0.5895 s (model startup excluded); whole Stage B 0.7660 s; 3.39 lines/s on this Mac. No GH200 throughput inference.

Conditional total **80 min** at N=124,669; Slurm limit **120 min** (×1.5).
The ALL-eligible N is still missing; this is not a population-bound final forecast.
`r2_prepare.py` recomputes `ceil(1.5 × (30 + 50 × N / 124669))` minutes after
population binding. Use that exact limit for test-only and real submission;
it supersedes the script's current planning default. R2a-off retains spare margin.
Stage A I/O and new logging costs must be read from the first job receipts before
scheduling more work. The two-line CPU mock cannot establish a GH200 scaling rate.

## Coordinator handoff

Only after owner certificate refresh and population/card binding, from the remote
package root:

```bash
# MINUTES = config/r2_job.json forecast.requested_minutes after population binding.
sbatch --test-only --time="${MINUTES}" scripts/labelfix/clariden/r2_job.sbatch
# Coordinator ONLY, after review and owner refresh:
sbatch --time="${MINUTES}" scripts/labelfix/clariden/r2_job.sbatch
```

Keep `manifest: null` for BASE + teacher only. To resume, point `R2_OUT` at the
prior output directory and retain identical code/config. Input changes require
a new output directory and an updated deployment checksum list.

Pull **receipts and exports only**:

```bash
rsync -av --include='*/' --include='*.json' --include='*train.jsonl.gz' \
  --include='*validation_reserve.jsonl.gz' --include='*alignments.jsonl.gz' \
  --include='*.csv' --include='DONE' --exclude='*' \
  clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_JOB/ \
  artifacts/labelfix_r2/output_JOB/
```

No `.pt`, `.npy`, crops or windows are included. Verify returned payload hashes
against stage/chunk receipts before use.

## Deployment

Deployed to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/`.
**378/378 payload files SHA-256 verified** locally against the remote files.
[Deployment list](R2_DEPLOY_FILES.txt), [SHA-256 manifest](R2_DEPLOY_SHA256.txt),
[deployment receipt](evidence/deploy_receipt.json), [remote hash checks](evidence/remote_sha_check.txt).
The package contains code, codec, tests/fixtures, frozen R1 exclusions, pending
production config, overlay versions and input documentation. Existing R1 extraction
payloads and the frozen teacher/recogniser are referenced in place with bound hashes;
no checkpoint, crop or training-window bulk transfer was performed.

Remote imports and `policy_binding()` equality passed without model inference:
[import receipt](evidence/remote_import_check.txt). **`sbatch --test-only` exited 0**:
projected Job 3681340, normal, 288 processors, nid006737. This is the scheduler's
hypothetical plan, not a submitted job. [Exact output](evidence/sbatch_test_only.txt).
The certificate was used as-is and never refreshed. Deployment finished well before
18:30 Athens. Final code was rerun through A–D, resumed, and its source binding
checked against the deployed source manifest.

Pending handoff inputs: ALL eligible R2C lines + document roles, followed by the
optional admitted R2a manifest/inventory. The complete population is required even
when R2a is off. Rebind config, recompute the population-based forecast, rebuild
checksums and repeat test-only after those inputs arrive. The current test-only
success certifies the Slurm request, not availability of these missing data.

R2P READY: recipe identical to 3678928-A except seed/manifest yes; tests 1447 passed; mock stages A–D ok; deploy sha256 378/378; test-only exit 0 (hypothetical Job 3681340, normal); forecast 80 min


## R2P2 population binding

This section supersedes the original PENDING population status above. Bound and deployed on 17 October 2026; BASE + teacher only (`manifest: null`, `native: null`). No job submitted, certificate refreshed, Git metadata written, or other local worktree modified.

### Population and role firewall

All 42,731 R2C lines are retained with their frozen document roles (supervision → train; validation → validation_reserve), plus 4,398 Addendum A teacher-seen lines. Total **47,129 lines across 255 documents**: train 27,308 / validation_reserve 4,943 / witness 8,856 / calibration 6,022. R2C retains its 169 documents; the teacher-seen slice adds 86 train documents.

| Pool | Source | Teacher-seen | Train | Validation reserve | Witness | Calibration | Total |
|---|---|---|---:|---:|---:|---:|---:|
| W1 | bsb_poly1850 | false | 1604 | 854 | 973 | 520 | 3951 |
| W1 | ia_poly1850 | false | 1005 | 237 | 584 | 250 | 2076 |
| W1 | nlg | false | 966 | 170 | 119 | 154 | 1409 |
| v2 | mixed:anemi_mixed | true | 95 | 0 | 0 | 0 | 95 |
| v2 | mixed:archive_b28038630 | true | 26 | 0 | 0 | 0 | 26 |
| v2 | mixed:openarchives_mixed_Dione | false | 164 | 0 | 162 | 0 | 326 |
| v2 | mixed:openarchives_mixed_KEIED | false | 106 | 0 | 0 | 0 | 106 |
| v2 | mixed:openarchives_mixed_Pandemos | true | 5 | 0 | 0 | 0 | 5 |
| v2 | mixed:openarchives_mixed_anaktisis | false | 144 | 0 | 164 | 0 | 308 |
| v2 | mixed:openarchives_mixed_apothesis | false | 63 | 0 | 45 | 0 | 108 |
| v2 | mixed:openarchives_mixed_hellanicus | false | 52 | 0 | 0 | 0 | 52 |
| v2 | mixed:openarchives_mixed_kallipos | false | 18 | 0 | 0 | 0 | 18 |
| v2 | mixed:openarchives_mixed_ktisis | false | 82 | 0 | 16 | 0 | 98 |
| v2 | mixed:openarchives_mixed_nemertes | false | 44 | 0 | 0 | 0 | 44 |
| v2 | mixed:openarchives_mixed_ntua | true | 12 | 0 | 0 | 0 | 12 |
| v2 | openarchives:openarchives_Dione | false | 1365 | 0 | 0 | 318 | 1683 |
| v2 | openarchives:openarchives_KEIED | false | 1325 | 0 | 0 | 615 | 1940 |
| v2 | openarchives:openarchives_Pandemos | false | 1450 | 0 | 0 | 576 | 2026 |
| v2 | openarchives:openarchives_Pandemos | true | 65 | 0 | 0 | 0 | 65 |
| v2 | openarchives:openarchives_anaktisis | false | 794 | 255 | 440 | 408 | 1897 |
| v2 | openarchives:openarchives_apothesis | false | 551 | 0 | 160 | 734 | 1445 |
| v2 | openarchives:openarchives_hellanicus | false | 1380 | 0 | 312 | 150 | 1842 |
| v2 | openarchives:openarchives_kallipos | false | 887 | 199 | 266 | 0 | 1352 |
| v2 | openarchives:openarchives_ktisis | false | 1062 | 202 | 546 | 0 | 1810 |
| v2 | openarchives:openarchives_nemertes | false | 839 | 116 | 465 | 0 | 1420 |
| v2 | openarchives:openarchives_ntua | false | 1131 | 0 | 0 | 0 | 1131 |
| v2 | parliament:parliament_proceedings_1975_2000 | false | 7878 | 2910 | 4604 | 2297 | 17689 |
| v2 | parliament:parliament_proceedings_1975_2000 | true | 29 | 0 | 0 | 0 | 29 |
| v2 | round1:anemi_round1 | true | 2622 | 0 | 0 | 0 | 2622 |
| v2 | round2:anemi_round2 | true | 398 | 0 | 0 | 0 | 398 |
| v2 | vouli:vouli_parliament_1850s | true | 1146 | 0 | 0 | 0 | 1146 |

The population and role binding are `artifacts/labelfix_r2/population/population.jsonl` and `roles.json`; [machine-readable counts](../../../../../artifacts/labelfix_r2/population/counts.json) include every source/role. R2C input hashes were rechecked before binding. The exact original R1 extraction receipt independently confirms all 16 validation documents: [split check](evidence/r2p2_frozen_split_check.json).

Teacher exports now write four physically separate `chunk-*-ROLE.jsonl.gz` streams. Witness, calibration and validation-reserve rows cannot enter training: Stage A checks bound document roles even when a manifest omits a role, and ManifestPool refuses explicit non-train roles before add/remove/quarantine processing. Native extraction remains train-only. `teacher_seen_document` is carried into each teacher record and manifest entries; Stage A refuses a later manifest that drops a bound true flag. Frozen-old manifests retain their existing training membership.

### Sequential exclusions

The initial Addendum A slice is exactly 33,198 v2-train greek_poly lines in 312 C1 documents outside the 91,469 selected C1 line IDs. Whole-document S8 DEV, audit100, heldout and release evaluation exclusions use the same aliases and saved inputs as R2C. Quality release classes remain line-level, as in R2C.

| Rule | Removed at this step | Lines remaining | Documents remaining |
|---|---:|---:|---:|
| C1_validation | 2014 | 31184 | 296 |
| S8_DEV | 25559 | 5625 | 100 |
| audit100 | 1227 | 4398 | 86 |
| heldout666 | 0 | 4398 | 86 |
| release_locked_eval | 0 | 4398 | 86 |
| release_eval_only_dev | 0 | 4398 | 86 |
| release_locked_eval_ia_wikisource | 0 | 4398 | 86 |
| release_locked_eval_ib_wikisource | 0 | 4398 | 86 |
| release_separator_ambiguous | 0 | 4398 | 86 |
| release_rotated_crop | 0 | 4398 | 86 |

R2C’s previously applied exclusions are unchanged: W1 25,920 → 7,436 (18,484 outside requested Greek strata); v2 214,436 → 35,295 (sequentially 31,018 non-Greek, 34,496 C1-document, 108,403 S8 DEV-document, 5,224 audit100-document exclusions). The detailed independent overlap counts remain in R2C_REPORT.md. Its conservative saved heldout join excludes all 1,264 IDs, including the specified 666. Zero final population lines overlap any bound excluded line/document.

### Crop staging and hashes

All **39,693 v2 lines** found exact matching native crops in place under `collection_v2/crops/`; every file was read and SHA-256 compared with its local native bytes. No v2 crop upload was needed. W1’s 7,436 lines use **7,435 distinct uploaded crop files** (one identical-byte pair within the same witness document). Missing disposable crops were recreated only inside this worktree from retained grayscale page rasters with PNG compression level 3 and accepted only on original hash equality. R2C’s byte-identical retained crops were also reused read-only.

Crop payload: **262.376525 MB** (262,376,525 bytes). Rsync file bytes including the SHA manifest: 263,380,250; sent 264,371,583 bytes plus 163,618 bytes received, below 600 MB. Destination: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/crops/`. Remote `sha256sum --check CROPS_SHA256.txt`: **7,435/7,435 OK**.

[Crop receipt](evidence/r2p2_crop_receipt.json) binds the in-place probe, upload manifest and [remote SHA readback](evidence/r2p2_crop_sha_check.txt). Every population `image` is the exact verified Clariden native-crop path; Stage A independently rehashes all 47,129 references. Native byte duplicates retain their separate source line IDs and do not cross document roles.

### Rebinding, forecast, validation and deployment

`r2_prepare.py` ran with the complete population, role binding and frozen external hashes. The resulting config passed remote Stage A completeness, policy, extraction-receipt, input-hash, exclusion and native-crop checks: [preflight output](evidence/remote_import_check.txt). Preflight is read-only on the login node; production execution still requires a Slurm allocation.

`ceil(1.5 × (30 + 50 × 47,129 / 124,669)) = 74` minutes. Teacher reference 18.9016515734 min; training reference 30 min; total 48.9016515734 min before ×1.5. This is a planning forecast, not measured GH200 performance.

Rebuilt root and documentation SHA manifests and deployment file list: **386/386 payload files remotely verified**, including the population and role binding. [Deployment receipt](evidence/deploy_receipt.json), [file list](R2_DEPLOY_FILES.txt), [SHA manifest](R2_DEPLOY_SHA256.txt), [remote hash readback](evidence/remote_sha_check.txt).

**1,467 labelfix tests passed**, with no existing test edited or weakened: [final suite log](evidence/r2p2_all_tests_final.log). New regressions cover all non-train roles (add/remove/unknown), separate role files, teacher-seen export provenance, bound-role manifest refusal, and dropped provenance refusal. All 30 `greekocr/labelfix` files and the frozen release policy remain byte-identical: [check](evidence/r2p2_frozen_check.json).

The exact sbatch shell entry point completed A–D on **five real-population-schema native lines**, one per role plus a teacher-seen train line, with local hash-identical native paths. It ran real frozen recognizer/teacher inference and two bounded CPU BASE updates over synthetic old-pool windows; D was correctly skipped with no R2a manifest. This verifies execution and schema, not reader quality or GPU speed. [Final mock log](evidence/r2p2_mock_final.log), [stage receipts](evidence/r2p2_mock_summary.json).

Scheduler check (no submission):

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
sbatch: Job 3681394 to start at 10:27:16 a using 288 processors on nodes nid006590 in partition normal
```

Exact coordinator submit command, after reviewing this package:

```bash
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/
sbatch --time=74 scripts/labelfix/clariden/r2_job.sbatch
```

R2P2 READY: population N=47129 (train 27308 incl. teacher-seen 4398 / validation_reserve 4943 / witness 8856 / calibration 6022); crops staged 47129 (uploaded 262.38 MB); time 74 min; deploy sha256 386/386; test-only exit 0 (hypothetical scheduler plan; no submission)

### R2CU custody correction (17 October 2026)

The prior note incorrectly called the four population artifacts “gitignored,
hash-bound” and claimed that a follow-up test commit covered the deployment.
The population files were untracked **and not ignored**; a manifest hash alone
did not provide the required committed or explicitly ignored-and-hash-listed
custody. The test file was committed, but that did not close the population gap.

The four files remain in place, unchanged and committable. The lead must commit
them together with this custody correction and `.gitignore`. No Git metadata was
written by R2CU. The audit starts from `c3868706a`, the brief commit on
`opus/r2-prep`. Both local SHA manifests agree. Fresh read-only SSH `sha256sum`
confirms all four population files equal their deployed copies and manifest entries:
[remote output](evidence/r2cu_population_remote_sha.txt).

| Deployed population file (under `artifacts/labelfix_r2/population/`) | SHA-256 (local = remote = manifest) | Disposition |
|---|---|---|
| `counts.json` | `5a464bb2e159cb1816366d2da90e6b463dacf2b879e49121bde6561e539ef126` | Untracked, not ignored; lead commit required |
| `crop_staging.json` | `54d71d305ffd4fb35a52c2955d7f9599bbef8c7b1206e5a365994f9117d6bc13` | Untracked, not ignored; lead commit required |
| `population.jsonl` | `1db6a029e83e4a775ffea80781b8053a72b55a1cb6231a2a99632fed903a9ac9` | Untracked, not ignored; lead commit required |
| `roles.json` | `13760d92bc25b6c4b30893a6ed17800de06767b1242ce8802c4f38e15a703b5c` | Untracked, not ignored; lead commit required |

All 386 deployed paths are inventoried per file in the
[custody audit](evidence/r2cu_custody_audit.json). Currently 382/386 are tracked
and equal their HEAD blobs; four await the lead commit. After that commit,
386/386 will be tracked; [untracked exception list](DEPLOY_UNTRACKED_HASHED.txt)
contains **zero exceptions**. No deployed path is ignored. Of the 382 tracked
paths, only 381 also equal the deployment manifest: the scorer differs below.

Twelve precise, repo-root-anchored ignore entries cover upload/recreated staging,
recursive unstaged/local-crop/probe JSONL, mock and pytest scratch (including the
base `mock_run/` and `pytest/` directories), and the job readback. The readback's
`artifacts/labelfix_r2/output_3681404/READBACK_RECEIPT.json` remains its custody
record. `artifacts/labelfix_sf6/` contains only the three restored frozen SF5
Python fixture files; `scripts/labelfix/sf6_measure.py` references this test copy.
It is ignored and absent from the deployment inventory. Files were not removed.

#### Additional deployment blocker

`14902a546` deliberately fixed compound truth handling in
`scripts/labelfix/r2_score.py`. Its current committed/local SHA is
`fa88fa445c8fa8b7328db80552de74ddd486a90127debbf205a98bb31278a9e4`,
whereas the deployment manifest binds
`da69c5f8b25a2fa32fac351db1904e7b8265fdf121cf926cd952c92856643b64`.
Committing the population files cannot resolve this separate manifest mismatch.
The deployment and scorer were preserved. The lead/coordinator must explicitly
resolve this source/deployment version choice before a full VERIFY_OK is possible;
R2CU has no redeployment authority. The manifest was not rewritten to conceal it.

#### Coordinator verifier

The tool is reachable locally at `greek-page-ocr/scripts/ops/verify_deploy.py`,
branch `sol/ops1-verify-deploy`, commit `cf7b844`. Its documented CLI has **no
dry-run flag**: it always runs remote SHA checks and `sbatch --test-only`, plus
local commit/dirty-tree checks and certificate inspection. The R2CU network scope
permits Clariden SHA checks only. Therefore R2CU uses the tool's injectable runner
for actual local/certificate/remote SHA diagnostics and explicitly refuses the
scheduler invocation. This guarded diagnostic is not a full VERIFY_OK receipt:
[JSON](evidence/r2cu_verify_deploy_guarded.json),
[complete output](evidence/r2cu_verify_deploy_output.txt).
The actual guarded output was:

```text
VERIFY_FAIL: tracked-but-uncommitted: .gitignore; local artifacts/labelfix_r2/population/counts.json: absent from commit (no allowed gitignored exemption); local artifacts/labelfix_r2/population/crop_staging.json: absent from commit (no allowed gitignored exemption); local artifacts/labelfix_r2/population/population.jsonl: absent from commit (no allowed gitignored exemption); local artifacts/labelfix_r2/population/roles.json: absent from commit (no allowed gitignored exemption); local scripts/labelfix/r2_score.py: manifest hash mismatch; sbatch --test-only exit 125
```

Remote SHA counts: 386 OK, 0 missing, 0 mismatched, 0 unknown. Certificate
inspection passed at this check (valid until 2026-10-17 16:18:52 UTC, more than
two hours remaining). The report edit followed this diagnostic snapshot and is
also now a tracked uncommitted path.

Commit-dependent checks are the four absent commit blobs and the tracked dirty
`.gitignore`/report. The lead must commit the four population files and all R2CU
tracked edits, then rerun against that resolved commit with a clean tracked tree.
The scorer manifest mismatch requires separate resolution. A full coordinator
run must also execute the scheduler test under its own authorization and pass
the live certificate validity checks. Submission is gated on a new **VERIFY_OK**;
this correction does not authorize submission. No redeployment, submission or
certificate refresh was performed.
