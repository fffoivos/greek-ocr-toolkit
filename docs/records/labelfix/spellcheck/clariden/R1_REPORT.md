# R1 — purpose-built mark reader: prepared and deployed

Prepared in `greek-ocr-toolkit-spellcheck-r1` for `opus/spellcheck-r1`, 16 October 2026. **No job submitted; no `.git` writes; other worktrees untouched.** This is readiness evidence and a bounded CPU mock, not a trained-reader quality claim.

## Owner rule and extraction

The restart rule supersedes the outline’s column ownership filter. There is no gap, column-profile, or connected-component acceptance test. `r1_pixels.py` estimates letter height from per-letter 5th–95th percentiles of dark-pixel row mass, then takes the median, preferring short lowercase bodies α/ε/ο/σ/π/ν/ω/υ (at least three measurements); otherwise all alphabetic spans. A blank line falls back to median CTC width / 0.6. Otsu is clamped to [40,220]. No `ink.py`, SciPy, x-height fitting model, Google letters, or recogniser forward pass enters extraction/training/inference.

A vowel/ρ slot passes when recogniser line confidence is ≥0.5, its CTC width is within **[0.2,2.0] × the line median alphabetic CTC span width**, and within **[0.1,2.0] × the pixel letter height**. The second range binds width to the actual font size. Neither range depends on letter separation. The complete rule is in both extraction receipts. Training additionally requires exact NFD word-core agreement including case and marks, with supported four-head labels.

The window includes the full original vertical crop and all its available mark zone. Horizontal margins are 1.5 pixel letter heights left and 0.75 right; C uses 0.75 left. White padding preserves this geometry at image edges. Each grey view is resized to 64×128; a separate mask marks the recogniser span. Wide and C views are stored independently as uint8 so C does not inherit a second resize. This costs about **34 GB for 2.06 M samples (about 17 GB per view)**, rather than the outline’s single-view 17 GB estimate. No crops are copied to Clariden.

| held-out extraction | count |
|---|---:|
| lines / books | 666 / 14 |
| recogniser vowel/ρ slots | 11,347 |
| usable slots | 11,329 |
| coverage | 99.8414% |
| outside median CTC width range | 5 |
| outside pixel-height width range | 13 |
| low-confidence slots | 0 |
| fused vowel/ρ slots | 477 |
| fused slots retained | 473 |
| frozen-text alignment transfers | 10 lines |
| extraction errors | 0 |
| stored held-out payload | 187,039,646 bytes |

Fused is a diagnostic: 8-connected Otsu components at least 0.45 pixel-letter-height tall, with more than one recogniser character assigned by greatest horizontal overlap. It never changes eligibility. Diagnostic counts are not manual fusion adjudications. Pixel heights have min/median/max 15/28/73 px; median CTC widths have min/median/max 14.0/28.1/75.7 px. The 10 cached-text differences use the same matched/nearest-neighbour span transfer as S4’s `ctc_align.transfer_alignment`, verified by a unit test. All samples use the frozen recogniser text and its NFD start positions.

Final shard: [heldout_font/extraction_receipt.json](../../../../../artifacts/labelfix_r1/heldout_font/extraction_receipt.json), [heldout_font/lines.jsonl.gz](../../../../../artifacts/labelfix_r1/heldout_font/lines.jsonl.gz). The stopped `artifacts/labelfix_r1/heldout/` column-filter output is obsolete and explicitly marked rejected. It was not deployed.

## Verified disjointness

All 91,469 C1 rows and 316 document IDs were checked against actual exclusion IDs. Human document/line suffixes are canonicalised. The 300 train / 16 validation document split is frozen with seed 20261016. The extraction receipt prints the counts and refuses any nonzero intersection or selection outside the frozen C1 rows.

| exclusion set | excluded docs | excluded lines | C1 doc intersection | C1 line intersection |
|---|---:|---:|---:|---:|
| heldout_14 | 14 | 666 | 0 | 0 |
| DEV_3 | 3 | 598 | 0 | 0 |
| summary_heldout_27 | 27 | 666 | 0 | 0 |
| import_real_v2_test | 92 | 44029 | 0 | 0 |
| v2_test | 92 | 42038 | 0 | 0 |
| wikisource_human | 25 | 1392 | 0 | 0 |
| e1_real_test | 36 | 3600 | 0 | 0 |

The exclusion binding includes SHA-256 of `C1_selection.summary.json`, frozen S4 lines, `import_real_v2_test.jsonl`, and E3’s `full_s0_v2_test`, `full_s0_wikisource_human`, and `full_s0_e1_real_test`. See [exclusions.json](../../../../../artifacts/labelfix_r1/binding/exclusions.json) and [disjointness.json](../../../../../artifacts/labelfix_r1/binding/disjointness.json). The deployment also includes `document_split.json`. No extra training or alignment job is permitted by these entry points.

## Exact job-entry mock and tests

The mock entered through `bash scripts/labelfix/clariden/r1_job.sbatch` with `R1_MOCK=1`, then the same `r1_run.py`, `r1_extract.py`, `r1_train.py`, and `r1_score.py` CLI entry points used for the job and readout. Only selection size, CPU device, worker/batch sizes and the 50-step bound differ. Local image decoding was limited to the 192 C1 crops and the 666 held-out crops. No local DEV owner crops were decoded.

```bash
R1_MOCK=1 \
R1_PYTHON=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
R1_OUT=artifacts/labelfix_r1/mock_font \
R1_CROP_ROOT=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit \
bash scripts/labelfix/clariden/r1_job.sbatch
```

192/192 lines decoded without error; 4,410 vowel/ρ slots → 4,169 labelled samples (3,638 train, 531 validation). Losses: 238 non-agreement-word slots and 3 implausible CTC widths. Training and validation documents are disjoint; validation uses natural frequencies and unweighted loss.

| arm | steps | training occurrences | CPU forward+backward samples/s |
|---|---:|---:|---:|
| A | 50 | 800 | 205.53 |
| B | 50 | 800 | 201.25 |
| C | 50 | 800 | 261.79 |
| D | 50 | 800 | 261.69 |
| E | 50 | 800 | 208.31 |

All five arms produced best checkpoints, CSV epoch logs, training receipts, 11,329 held-out predictions each with a receipt, and `DONE` markers. Mock elapsed time including held-out inference and scoring: 203.19 seconds. [R1_mock.log](R1_mock.log), [run_receipt.json](../../../../../artifacts/labelfix_r1/mock_font/run_receipt.json), [filled mock RESULT.md](../../../../../artifacts/labelfix_r1/mock_font/score/RESULT.md). The six critical extraction/training/model source files match their current SHA-256 across every arm’s binding.

**133 labelfix tests passed**, including 8 new R1 tests: agreeing/non-agreeing labels with case/mark distinctions, compound factors, full-height font-based window geometry and spacing invariance, fused-letter acceptance, planted document and line overlaps, exact S4 span-transfer parity, unscored-none truth preservation, and A–E balancing. [R1_pytest_labelfix.log](R1_pytest_labelfix.log). No existing tests were changed or deselected.

## Compute decision and five arms

Arm A: **205.53 samples/s** on the Mac CPU, fp32, batch 16, four threads, real 2×64×128 input. This includes forward, backward, optimizer, and loader fetch time, excluding validation/inference. Actual model size: 1,766,571 parameters, stages 32/64/128/192 with two residual blocks per stage and a 64-d letter embedding. Estimated forward cost is 111,277,568 FLOPs/sample; forward+backward is approximately 333,832,704 FLOPs/sample (multiply+add counted as two).

The forecast assumes 15k samples/s/GPU: 15 × 2,057,665 samples / 15k ≈ **34.29 minutes/arm**, with A→E taking about **68.59 compute minutes** on GPU 0. That rate requires **5.01 TFLOPs/s**, about 1.0% of an explicitly assumed conservative 500-TFLOPs/s dense bf16 ceiling, and 73× this four-thread CPU rate. The CPU’s batch-fetch wait total implies about 29,039 samples/s on the small warm mock (0.71% of training time); it is not a measurement of full-shard I/O or GPU feeding. This does not establish a >3× error in the GPU assumption, so **15 epochs are retained**. No live GPU throughput qualification is claimed. Allowing extraction, validation, checkpointing and inference gives a planning estimate of roughly 105 node-minutes, within the 180-minute request; actual GPU throughput remains unmeasured. Machine-readable reasoning: [R1_compute_check.json](R1_compute_check.json).

| arm | letter embedding | left font heights | sampling | GPU |
|---|---|---:|---|---:|
| A | 64-d, case kept | 1.5 | balanced positive head/value pools; rare/compound ≥5%; none ≈40% | 0 first |
| B | absent | 1.5 | A sampling | 1 |
| C | 64-d | 0.75 | A sampling | 2 |
| D | 64-d | 1.5 | natural permutation, no class weighting | 3 |
| E | 64-d | 1.5 | balanced positive head/value pools; rare/compound ≥5%; none at its natural train frequency | 0 after A |

Balanced arms use capped square-root inverse-frequency head weights and explicit none/rare batch quotas; integer batch rounding is recorded in the sampler code. Mock E’s natural none fraction is 59.813%. All arms use AdamW, lr=0.001, weight decay=0.01, seed 20261016. Production batch=512, CUDA bf16 autocast. Every epoch appends/fsyncs `train_log.csv`, atomically saves an improved best checkpoint by natural validation loss, and writes best-checkpoint predictions. A per-arm `DONE` is written only at completion. A timeout can leave a best checkpoint and epoch log without `DONE`; it is not reported as completion.

## Print-truth scoring and limits

`r1_score.py` verified exact frozen S4 parity: 18,229 known / 2,647 UNKNOWN physical slots; TP=3,726, FP=261, FN=327. It maps prediction `(line_id,NFD start)` through frozen `reading.recogniser_slots` component mappings, never through Google letters. `mark_set`, `score_slots` and the frozen slot truths are unchanged. It produces both required tables: mapped scored slots, and all frozen slots with unscored predictions counted as none; plus fused strata, capital detection/naming, exact composed classes, per-book scores, Google-disagreement print confirmation, and all 56/59/33 owner-check records.

**Coverage is not truth availability.** 10,614 of the 11,329 scoreable reader samples map to the older physical-slot instrument (10,046 have known truth); 715 do not map. The fused diagnostic reaches 346 unique frozen physical slots, only 16 with known truth and 330 UNKNOWN. It does not invent per-letter truth inside a fused component or award an arbitrary component owner. Raw fusion counts remain 477 slots / 473 retained. Scores on those few known fused truths cannot establish general fused-letter accuracy.

The four heads do not name apostrophes or quotes. Reader-only tables leave them absent, and owner punctuation clauses explicitly remain unresolved for detector follow-up. Missing DEV inference in the mock is counted, not filled from S4. Production extracts the 32 additional owner lines on the node for inference only. All original owner notes, truth files, S4/S5 instruments and artifacts are preserved. Ambiguous owner wording remains unresolved. Mock metrics are smoke-test outputs, not an arm selection or a replacement decision.

**S5 artifacts were absent in this worktree.** The table has a pending S5 column; `--s5-lines` accepts a track-lead-supplied frozen S5 file and verifies the same 666 line IDs and slot truth before scoring. No S5 worktree was read or modified. A complete S4/S5/R1 quality comparison waits for the trained predictions and that S5 artifact.

Prepared [run_binding.json](../../../../../artifacts/labelfix_r1/run_binding.json), [data_provenance.json](../../../../../artifacts/labelfix_r1/data_provenance.json), and [RESULT.md template](../../../../../artifacts/labelfix_r1/RESULT.md) are deployed. Runtime creates per-arm bindings/provenance, extraction shard hashes, prediction receipts, CSVs and completion markers under `output_${SLURM_JOB_ID}`. Nothing needed for scoring is retained only in a log.

After retrieving the output directory, the track lead can run locally (substitute its job/output path; omit `--s5-lines` while unavailable):

```bash
PYTHONPATH="$PWD" /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
  scripts/labelfix/clariden/r1_score.py \
  --runs artifacts/labelfix_r1/output_JOBID \
  --heldout artifacts/labelfix_r1/heldout_font \
  --out artifacts/labelfix_r1/score_JOBID \
  --s5-lines docs/records/labelfix/spellcheck/S5_lines.jsonl.gz
```

## Deployment and scheduler test

Deployed to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/`. All **127/127 files match** local and remote SHA-256; the complete comparison is [R1_DEPLOY_SHA256.txt](R1_DEPLOY_SHA256.txt). Deployment includes scripts/code, C1 selection/alignment/inventory, exclusion/split bindings, cached owner alignments, held-out uint8 shards and prepared receipts/template. No line crops or OCR checkpoints were transferred.

All **91,469/91,469 existing C1 crops** match inventory paths, sizes and SHA-256: 3,293,623,314 bytes, zero missing/mismatches. All 32 node-only owner crops are present. [R1_crop_verification.json](R1_crop_verification.json). Inventory checking decoded no images and launched no allocation.

Certificate inspected with `ssh-keygen -Lf ~/.ssh/cscs-key-cert.pub | grep Valid`: valid 2026-10-16 19:17:52 to 2026-10-17 19:18:52. SSH succeeded; no certificate refresh or package installation occurred. E3 runtime import check confirmed torch 2.11.0+cu128 / CUDA 12.8, NumPy 2.5.4, Pillow 12.3.0, with neither ink nor SciPy imported by extraction/training. [R1_remote_runtime.txt](R1_remote_runtime.txt) also contains the empty R1 queue readback.

Exact scheduler test (exit 0; **test-only, no submission**):

```text
sbatch --test-only --parsable scripts/labelfix/clariden/r1_job.sbatch
sbatch: Job 3678889 to start at 22:34:55 a using 288 processors on nodes nid007148 in partition normal
```

The displayed job number/start/nodes are Slurm’s test prediction, not an allocated or submitted R1 job. Full output, including the SSH transport warning, is [R1_sbatch_test_only.txt](R1_sbatch_test_only.txt). The script requests account a0140, normal, one node, four GPUs, exclusive, 03:00:00. Source hashes are checked in the prologue; extraction completes with its own hashed receipt before training begins, and training refuses incomplete/unverified extraction.

Exact submit command for the coordinator, **not executed here**. Replace the literal source-commit placeholder with the track lead’s final commit; runtime `run_binding.json` records that value. If payload bytes change, regenerate/deploy the manifest and repeat SHA/test-only checks.

```bash
ssh clariden 'cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016 && \
  sha256sum --check DEPLOY_SHA256.txt && \
  sbatch --parsable --export=ALL,R1_SOURCE_COMMIT=TRACK_LEAD_FILL_SOURCE_COMMIT \
    scripts/labelfix/clariden/r1_job.sbatch'
```

## Deployed file SHA-256 list

Manifest SHA-256: `0a91ce25b346dabcb48b4cb35584a875b4ad93c7af899b6edb3cdfb740ec5447`. Remote/local digests agree for every row below.

| file | SHA-256 |
|---|---|
| `.cache/labelfix/align_s0.jsonl` | `722e7b6c7b301dfbcb2070baa089f146639ea68d483651d0f743afe4e137f902` |
| `.cache/labelfix/clariden/C1_alignments.jsonl.gz` | `951122655bd25af553f48951af986bcd2be4f3a57f184beaf2a5923de08bb398` |
| `.cache/labelfix/clariden/C1_crop_inventory.jsonl.gz` | `4dfb7e8e72675c7b0fa415d43a55d082d04b05cd7d6f79f95c6f7bcf51c3da88` |
| `.cache/labelfix/clariden/C1_selection.jsonl` | `bd0f740258bcf64688323d3a79eb8f1ee78518bc7a8c2a491adc7766dd8adbc3` |
| `artifacts/labelfix_r1/RESULT.md` | `12a400a1c0eaf7af6e0d0bc708dec6d7cd27de6bdb6cd8506d3d2da6dda3ad5b` |
| `artifacts/labelfix_r1/binding/disjointness.json` | `ff5003fd49ee84751b2e602e0971cd6cf860e1bbcd9187978ca529f6509482d1` |
| `artifacts/labelfix_r1/binding/document_split.json` | `3a1ecae1141e6b6bb6ff3c4c87b2d629ad8bdce0e96ad48b8f0a094adb407d53` |
| `artifacts/labelfix_r1/binding/exclusions.json` | `1f0c7b67eaa0f6300bbd24dec93f2c02f90a669de346202d0b6200bb1ec1eeaf` |
| `artifacts/labelfix_r1/binding/heldout_lines.jsonl.gz` | `ee874a22763b47df714ac398a756c306ee289847fad4f7668191229e9ea0c7ec` |
| `artifacts/labelfix_r1/binding/mock_selection.jsonl` | `35d1ce8eb21b473211e6e8d9b6034c710d59db1674b216f06d10dc5f085e07d9` |
| `artifacts/labelfix_r1/binding/owner_extra_lines.jsonl.gz` | `71e28c4c1bcb4382db77648ac5d19844ecf86b41039511323bd6a55fffc87e49` |
| `artifacts/labelfix_r1/binding/prepare_receipt.json` | `838e24bccbeede67dd88f34699b3bac5cdabd19cb69c2e5e6d51dac583d17aa4` |
| `artifacts/labelfix_r1/data_provenance.json` | `f16fd2f6c17e89c0488ea8c1549f313777b734686b16754fcf7fb577faf86e3a` |
| `artifacts/labelfix_r1/heldout_font/extraction_receipt.json` | `84d3a259a5280a4c18b19e83961755ed1cf4931f288ff82bc9b241bc613a7277` |
| `artifacts/labelfix_r1/heldout_font/index.npy` | `ff63ff6b89b4e3025d3ee605534da301dc2734b61d5b7d3f69e8c3f92c4b950b` |
| `artifacts/labelfix_r1/heldout_font/lines.jsonl.gz` | `d290010f13f3633be81459dacc7d85af124f63b5228bad406d78d675f521a61f` |
| `artifacts/labelfix_r1/heldout_font/shard-00000-index.npy` | `66258e7554cc15340682f7386c4dde58bb345f36a9c7e513d1fc5a4d323c684f` |
| `artifacts/labelfix_r1/heldout_font/shard-00000-lines.jsonl.gz` | `1895db0cb5aeca633fcfd8613a51e3f53a36bc31d6854706f21f4dc6e0bf7688` |
| `artifacts/labelfix_r1/heldout_font/shard-00000-narrow.npy` | `9d6ca767f5641afa939204cde014e4dcca5c46996049f44b4c2376d76232d920` |
| `artifacts/labelfix_r1/heldout_font/shard-00000-wide.npy` | `06a8000c3422a43305f188207ac88bc99e5d8625ff7f5f0cc44302ea56a00a08` |
| `artifacts/labelfix_r1/heldout_font/shard-00001-index.npy` | `047288b5b88abb448d774fc880db74d5bf4944dc479bbb33760a977e2d9befea` |
| `artifacts/labelfix_r1/heldout_font/shard-00001-lines.jsonl.gz` | `7c8ec730a7acb2b9feb9c09a3f80612e87985d065b3fd253bbcbbad54dca6e43` |
| `artifacts/labelfix_r1/heldout_font/shard-00001-narrow.npy` | `33584bccebe2e25334de8eaa72d717736615095405ebc75f42e0e42c0dcbb5ee` |
| `artifacts/labelfix_r1/heldout_font/shard-00001-wide.npy` | `8ca0f9543324346677b83d734059f81e06b8433a68a7e313a3787b195fc93a2e` |
| `artifacts/labelfix_r1/heldout_font/shard-00002-index.npy` | `e70204b0f96f69be12a676574750c6a0a05824b51962593290eb61667fc8b1be` |
| `artifacts/labelfix_r1/heldout_font/shard-00002-lines.jsonl.gz` | `3d823f671f4f5894ff379b84d225a4180f6e09646d28ad7e96f2d402fc351e23` |
| `artifacts/labelfix_r1/heldout_font/shard-00002-narrow.npy` | `fcb9ccdd4a4e1d502cb14506bc48dccf95ad2450e820afcc2d4f882c283f0b29` |
| `artifacts/labelfix_r1/heldout_font/shard-00002-wide.npy` | `306089b5387ab2e1aa1ad4ea7ff4668c10268a80d398ee4d4e19835f65acc10f` |
| `artifacts/labelfix_r1/heldout_font/shard-00003-index.npy` | `19366882787d01ed32c1f6f134a2921f03ec76479ac0f6ed090d3fc2a999e366` |
| `artifacts/labelfix_r1/heldout_font/shard-00003-lines.jsonl.gz` | `4f43185ad1e902d3f99ead661d8e55dcafb64daa6e9b67bf4c8e925db570435c` |
| `artifacts/labelfix_r1/heldout_font/shard-00003-narrow.npy` | `641316a04b8f195db3aa80c4067d60f95e957ccc39b9ca456244e75f30e5a3ed` |
| `artifacts/labelfix_r1/heldout_font/shard-00003-wide.npy` | `299569aee7016b0be5be194d3f715afd699146e15616f69f335695027905e114` |
| `artifacts/labelfix_r1/heldout_font/shard-00004-index.npy` | `5ebb833e7873220e7a01908b13c3565ba19395d766583613b8061385978eda67` |
| `artifacts/labelfix_r1/heldout_font/shard-00004-lines.jsonl.gz` | `4da22b2a9a325811eea69cf22dd7b01d5560bde00695d868be81033ca68060eb` |
| `artifacts/labelfix_r1/heldout_font/shard-00004-narrow.npy` | `df4ec193e523bf4ec20589f283bf5aac7be1f9e8363726945ad69b92ca01f521` |
| `artifacts/labelfix_r1/heldout_font/shard-00004-wide.npy` | `48c8f9a7e26513e0c8ad2f63c11e3eb38e97a8e5b83dd0f47e267cc658004323` |
| `artifacts/labelfix_r1/heldout_font/shard-00005-index.npy` | `c7c05d2e24cefdf1a71488d44af9c41ffb3026ecc0b803a33ead71ebb4b33566` |
| `artifacts/labelfix_r1/heldout_font/shard-00005-lines.jsonl.gz` | `4e9355b6fbe0f48a98544bf5b1e19e5d9cd015b59350f917d2efc82f15d00b4b` |
| `artifacts/labelfix_r1/heldout_font/shard-00005-narrow.npy` | `7b57a696ed812d158cd4daa87a957277e2e200db7757e424fc6d6c02fd10c538` |
| `artifacts/labelfix_r1/heldout_font/shard-00005-wide.npy` | `13063320c9543b70c9a78a49ec35775a6ce41b283a5afbc947fa64f1a4f74284` |
| `artifacts/labelfix_r1/heldout_font/shard-00006-index.npy` | `d238ef409c5d97f4a4d3f753b6b5c2128bf0020d0d7032268a4ae388a89278ca` |
| `artifacts/labelfix_r1/heldout_font/shard-00006-lines.jsonl.gz` | `c770d6f76d0fc2693505b831f83b5569699c28a913045333ce0f46e02faab73a` |
| `artifacts/labelfix_r1/heldout_font/shard-00006-narrow.npy` | `4561b398c5f18df2993c184f03c73596119312322c90d8771ed8a9c8dc420a1e` |
| `artifacts/labelfix_r1/heldout_font/shard-00006-wide.npy` | `430a49d3e565877a4c3c716fa317617c8aa960df06f6e5103d92f002735e9b70` |
| `artifacts/labelfix_r1/heldout_font/shard-00007-index.npy` | `656c89bd3a01a36c52391a46b4bdd8413513d0c73dcbf38fabdb3dafff825273` |
| `artifacts/labelfix_r1/heldout_font/shard-00007-lines.jsonl.gz` | `634583223fe3bad09e85b3fc8d832c27da7f8ca366cb847911743dc3540e5207` |
| `artifacts/labelfix_r1/heldout_font/shard-00007-narrow.npy` | `68bdc6e8e0764fa8b4db3a0522a1a896874605683808f710743a5eb90afa6443` |
| `artifacts/labelfix_r1/heldout_font/shard-00007-wide.npy` | `42defeff331022c0115bb28852b5f482e88ac962e40a3d865a92d962694728c5` |
| `artifacts/labelfix_r1/heldout_font/shard-00008-index.npy` | `db0256b797fee58a84d5506a4b2232dcc8e71782dadd811f056bb4b5c309eb47` |
| `artifacts/labelfix_r1/heldout_font/shard-00008-lines.jsonl.gz` | `bcb08df27af41b0edb2d4ad95d143d3ad3f80083d10feb910e0464fce9a565fc` |
| `artifacts/labelfix_r1/heldout_font/shard-00008-narrow.npy` | `67c14197df2ebb49e22e7085dbcdbd762d2906ee92e3a41d5d6d87e90d672993` |
| `artifacts/labelfix_r1/heldout_font/shard-00008-wide.npy` | `6754462daf44c23295e5e6fddb040dc1fc64a2dc047302d59ffc6e0cab19fb18` |
| `artifacts/labelfix_r1/heldout_font/shard-00009-index.npy` | `d42f66c2aabcdd665987981790768b45dc3e4112ea36e685e0e60ae40501f9f6` |
| `artifacts/labelfix_r1/heldout_font/shard-00009-lines.jsonl.gz` | `7aab6dc921c0855348f8594507a861a23e8cd4bea7b5498d7eb05bbb41254362` |
| `artifacts/labelfix_r1/heldout_font/shard-00009-narrow.npy` | `16ae5d38b876e4641a6891415529879a3048b51735db320d94a6552e1b4ff003` |
| `artifacts/labelfix_r1/heldout_font/shard-00009-wide.npy` | `587bb5a4fcd5af24b3c561f275a813122624dd34be7f3081b8d6e0c9c5fd6d8b` |
| `artifacts/labelfix_r1/heldout_font/shard-00010-index.npy` | `d929510ea27bb326a3e2c195ffea1cda1fe068308eb5f388ae37fb80c62e21b9` |
| `artifacts/labelfix_r1/heldout_font/shard-00010-lines.jsonl.gz` | `e7e2cf2eee9ce63cf2b97b5bbbc69bb67d1c6d07da8895c62d52b7c5724c819c` |
| `artifacts/labelfix_r1/heldout_font/shard-00010-narrow.npy` | `5a1473d31bf10132fe328dae6892b82ef09e0462ea9c620f6173046dfb7b33a2` |
| `artifacts/labelfix_r1/heldout_font/shard-00010-wide.npy` | `8b4dd36ae757afa6222d8b6a0ccd91d30946ab1d8ef11b10de7616cacee88856` |
| `artifacts/labelfix_r1/run_binding.json` | `5fc2b40dfd0501fdcde7ab2cc6953afd18a059a46c11f4372d5165839dfe2527` |
| `docs/records/labelfix/spellcheck/clariden/C1_selection.summary.json` | `df4ea0cc0926464719f310fe1a940a3a19602fc78126a5be15c6c2ee0d7b9711` |
| `docs/records/labelfix/spellcheck/clariden/R1_mark_reader_outline.md` | `50ba911995ea9c431ec0ce836e740d4b60dc5cb3ec03fdb9529a1b91ec79bbe2` |
| `greekocr/__init__.py` | `71b967226af60f9e9d88a54374340925ecc47cbf96a5e64753d3fbe7a54f672e` |
| `greekocr/glyphs/__init__.py` | `1fd4e9e2b357cd8f244b508b639f8e07c60176bfaec3bb7b556d90211701d372` |
| `greekocr/glyphs/baseline.py` | `09e92755ccdd8fd748db1d6469f74adb5e6b6ef9789f746b0ee9f675f56d6606` |
| `greekocr/glyphs/boundary_evidence.py` | `b3412d8943e2d2513b9fe64bd879f93941719d88984ca7b522e27e29154e8545` |
| `greekocr/glyphs/columns.py` | `c3408cd43637d1110fb1d0ad5d96f17670dd7d684ed51933c68d311621a4f7b2` |
| `greekocr/glyphs/components.py` | `649b33d8c715f175421579ecbbb193594c027c6dfc3db7ec6a8dc76b6f3a88fb` |
| `greekocr/glyphs/evaluate.py` | `2ac4beca05cca4ebe4c18af89d8a9904c22930dcf19d1e32ef2659c7e1619590` |
| `greekocr/glyphs/ink.py` | `52097165b2f5180ceaa9e20982c5d0547d96bed889a84670984bca61075089f5` |
| `greekocr/glyphs/letters.py` | `2bdbcf72cd04eb43c1c7c40141481963cab6e6d7aca617edece33e52563db676` |
| `greekocr/glyphs/line_structure.py` | `d684dd8be3ce55746955fcf4cece15093ab78e35f9f0e98c6c4812548b16be38` |
| `greekocr/glyphs/lines_api.py` | `3574baa492029aaf026e2b890235f4d52a3dbced77a2ed160963cbf2f519877e` |
| `greekocr/glyphs/orientation.py` | `5abebf4d70f3bb2a6e325cf15391543748a7e20ed8c6b2d169eb59a4503ec9ec` |
| `greekocr/glyphs/orientation_guides.py` | `a180f07936ebff21d6b548c329ed2c3697a86696c5fd61a15bc471b3fe4338e5` |
| `greekocr/glyphs/orientation_regions.py` | `021f24744a48e5ca63d45ca4e624f307e8ab90ffe02b7f3ecbaac06b2e6f71a1` |
| `greekocr/glyphs/oriented_page.py` | `59d733b8f8a855911caffb226c0e45fe51110fa7b44a47a0caea735c2ce79dfe` |
| `greekocr/glyphs/page_font.py` | `edfb5484f15af62f7bbcad91bec9524e29fc411ad15dde2b12782cc4901d1060` |
| `greekocr/glyphs/page_lines.py` | `7aad8a99997136970d4394615cc1d1550efff887e8fe2787db5ed4dad5b1a674` |
| `greekocr/glyphs/page_text_lines.py` | `00bcb968c32942f6d6aee63f7d23b097c6a2df5b2effbb7e645d7124b0ed5bc8` |
| `greekocr/glyphs/pixel_segments.py` | `1ac994e4dc26ffb58c110978294f128586153a792c239cb8faee9a4b230757cd` |
| `greekocr/glyphs/readability.py` | `f506cafb7d26e5d658599eb27b234b0ee9d802440f55a3f233db110d8b747c59` |
| `greekocr/glyphs/recut.py` | `6da0255c3854448e991f110711fea4d2cd9f1202ffdcc36bb2c3485dc72ac01b` |
| `greekocr/glyphs/report.py` | `cd1bd5732b94448e19fef432e70fbb3cfb9c09757aab16a0383a9308cb21014d` |
| `greekocr/glyphs/statistics.py` | `9cf06d390c230d207fbe845473b7b28e1e6905008102e6004b4c6eb5dd7e649b` |
| `greekocr/glyphs/synthetic.py` | `3a58a763877d2d1b66fda9e44c16af842cc957b75ed7392e07087981683f32a3` |
| `greekocr/glyphs/table_lines.py` | `4055cb32eb96e598479731f46db4ea80704b8ea73ee10afbaa352d810a4d4fd1` |
| `greekocr/labelfix/__init__.py` | `17211c5aa6cdac87c2f59503e30a1126806d4f2ff0a4799a8fada9a1bce25105` |
| `greekocr/labelfix/build_lexicon.py` | `2b970cddf7c6904e3e27fe3ce6dc66d2e2a97a65b8dce991e1529a014af55e1f` |
| `greekocr/labelfix/candidates.py` | `3b2629f3d67047f751db79368d89e4cf4c9103ee4cc33137b172814ed0293b19` |
| `greekocr/labelfix/constraints.py` | `cb543bc0ffd4b78ce75c623a93fccdc5b9aaf55b0261ca0101ba3fbac0363cb3` |
| `greekocr/labelfix/ctc_align.py` | `1a753b3002f2068607206dada0dbb9cf93f13206eca2fe526150ab3a8056d9bb` |
| `greekocr/labelfix/deck.py` | `d8913e33a5252905c8a6863e9a547fd0899ae70e522cc6ab88447b6a3a040610` |
| `greekocr/labelfix/deck_serve.py` | `c9ce3e4f8001757688ec1b6c1775eb9ac326d1468293d14d76e27a087090cc70` |
| `greekocr/labelfix/ingest_decisions.py` | `a6800048624c8c7ad2dadc8ffb0e25650d33276b23a7271f8ba00964f79a52a9` |
| `greekocr/labelfix/ink.py` | `ff376e20cb5ad3c1e5aa24cbb3407dca14bd01a245f9b9cbfddbc24539d931ea` |
| `greekocr/labelfix/lexicon.py` | `7e4abee13c6059b5c1865604210840f9eff7a784a26a8cc2d26a336356fc2b39` |
| `greekocr/labelfix/linemetric.py` | `881c5ce3618b367df0df457408b606f5598396ffa028a87464b2e002e1e1a431` |
| `greekocr/labelfix/markshape.py` | `9efbb9a5c22a150cac4e96874ef74f8c3ea64fcb1b76c056c85a0fa8a58a945e` |
| `greekocr/labelfix/markshape_train.py` | `5e46ce79b69ad3bcc79d2fc382d9defd941d5b6641c7df47d6cf75a996afd638` |
| `greekocr/labelfix/owner_slots.py` | `0323dc8b8ef282a74e3a37bda4330dd01916626de3f519cab89be21d03175804` |
| `greekocr/labelfix/pull_firefox.py` | `61129f54d097368d6f98b80b47657b042d52e809a2b6722c3792a3ebd8124904` |
| `greekocr/labelfix/reach.py` | `8801be88357d2361a8fa4c2199f734570ef083be0c7e2d43eeb008bcdc5459bc` |
| `greekocr/labelfix/reading.py` | `2efa10e85fb9cf5cb3cef632fd9f2b5666bf61bc473ddcbc746fe2ed2beda7ac` |
| `greekocr/labelfix/rules.py` | `f789b714c29c618db47e7a811bc499c00da73fe30d2e0df7604f83fb4a6b4e6e` |
| `greekocr/labelfix/sample.py` | `ca3a32abc4318c9760e220e7722a184332debb218c87317b013848b595f44df0` |
| `greekocr/labelfix/sheet.py` | `0c95d461a01bf6c029b5b873caf0f441f7fe4c0632c476a387093c696eb49ac4` |
| `greekocr/labelfix/spellcheck_validate.py` | `b68c3317eadaf033643d8882bff54d247a204fae4c78c5474a8cf358cea09c80` |
| `greekocr/labelfix/spellink.py` | `cf5bc00b00ec7a7fb023291b42294b8139c1aa799c88a2b91357641e805d07ea` |
| `greekocr/labelfix/tei_extract.py` | `b32e5bfd31724b4d07a51158f82b1678b435ffc2eb7372485a142eef0cc9efa3` |
| `greekocr/labelfix/text.py` | `68311aadf00b371a463e5df97a80a80e226185c9e77a01dbb2663304d1af85a1` |
| `greekocr/labelfix/textstage.py` | `21c9c29f2d2b9d20c8524cd8df095b49f91ae4e87220897fc1a416f01d877649` |
| `greekocr/labelfix/validate.py` | `b23416e12970907010ba6f921974e8d8dc9b2afae7ef4bac000a06a83a1f612c` |
| `scripts/labelfix/clariden/c1_common.py` | `7716cd905b923b87e3034b4f29f727fb1b358a647fd14299ad0af0fdd3c6422d` |
| `scripts/labelfix/clariden/r1_common.py` | `45aff9154f33a193f55c494e0473caad8eed3236bbeba564171a841a0a047cb6` |
| `scripts/labelfix/clariden/r1_deploy_check.py` | `2a3654dc1751be8e181a4f8cafe367656b0e6ffc8495fea572aa725e3c54a1d1` |
| `scripts/labelfix/clariden/r1_extract.py` | `ba7f28eecd012e5d746765f67a797c9e3f677d9b5d382290539294e81de0265a` |
| `scripts/labelfix/clariden/r1_job.sbatch` | `aa486d2cd1f2373b8061c6af4b6ffb7baa76d3cb7220c6c5c7f4c212394f55b2` |
| `scripts/labelfix/clariden/r1_model.py` | `6e38deb9c26c83a3f0b2b8cdcbd0a2f349d71018bee31606d82b9d857e39f62e` |
| `scripts/labelfix/clariden/r1_owner.py` | `67b69a66d522c450dbf83c8c4b12888f8d52e89852257eab499b099036382623` |
| `scripts/labelfix/clariden/r1_pixels.py` | `ee516375fb7447720d8efbb67a1cabf05e0861f48ee1b20a192000445137d3d6` |
| `scripts/labelfix/clariden/r1_prepare.py` | `4a2fbb3c6539889f7257f7991845453eaa866acc0f0703b978a92db38ffaa3af` |
| `scripts/labelfix/clariden/r1_run.py` | `c3d374256a5381c052af1788bcae49df40691849045122306373c3e22eb1f0b1` |
| `scripts/labelfix/clariden/r1_score.py` | `7b9683bc03a07580380fa70a1cb10c6ced0ea1b7837314bd2da40fde547b8d7f` |
| `scripts/labelfix/clariden/r1_train.py` | `bb4ab38d0af510da9dd117322d9bea25eee121f9cb30ed595806f43d69ac9281` |
| `tests/labelfix/test_r1.py` | `39bf8c103e9418834910860fbdb662b4c3a9c4e4c8ad55df3ea9cb3b67068bfd` |

R1 READY: mock ok (192 crops, 205.53 samples/s CPU); coverage 99.8414% of held-out vowel/ρ slots; disjointness all 0; deploy sha256 127/127 match; test-only sbatch: Job 3678889 to start at 22:34:55 a using 288 processors on nodes nid007148 in partition normal; epochs 15
