# TRAIN_FULL_v1 — preparation record, 25 October 2026

**PREPARE ONLY. LAUNCH FIX READY, pending focused Astra re-review.** Current payload `0446ee734d2c867cda056973ce5052f917865f1f53ecc6c2b8301c99d437280f` (ID `0446ee734d2c867c`). No remote action was performed by Sol. The audited/prepared Gennadius population and original CUDA smoke remain unchanged and explicitly inherited through an exact operational-compatibility proof. See [LAUNCH_FIX.md](LAUNCH_FIX.md) and the current [relaunch commands](../../../out/TRAIN_FULL_v1/COMMANDS.md). The older preparation and pending-gate narrative below is retained as history.

The reviewable package is [package/](package/); owner commands are [out/TRAIN_FULL_v1/COMMANDS.md](../../../out/TRAIN_FULL_v1/COMMANDS.md). The verbatim assignment is [OWNER_BRIEF.md](OWNER_BRIEF.md). Preparation is not launch authorization.

## 23:08 launch failure — current state

Original [Astra prelaunch PASS](ASTRA_PRELAUNCH_REVIEW.md) covered payload294c3458c0d1fbbb and the completed005 preparation/smoke. The coordinator reports training segment3749193 failed123:0 before srun because an inherited `SLURM_TIME_FORMAT=relative` made its end time `Tomorr 10:05`; pending successors3749195/3749197 were cancelled. Their controls, claims and logs remain immutable. New controls use `controls/train-launchfix-001`; no dependency points to failed/cancelled parents.

The only behavior fix pins standard format on that squeue call. Artifact compatibility plumbing accepts the exact original runtime and smoke without rebinding; a new Astra review is still required for the new package. There is no recipe/data/library/runtime-environment change. Current population:793,227 train /16,350 dev /52,846 test; total862,423 unique crops; horizon198,312 with four checkpoint evaluations. Prepare3748345 and smoke3748974/3748976 completed. These remote outcomes are supported by retained local005 receipts; Sol did not rerun them remotely.

**81 offline tests pass**, including real wrapper execution with mocked scheduler/GNU-date responses for same day, `Tomorr 10:05`, and a far date; exact parent proof; mutation refusal; inherited smoke acceptance and rejection of stale Astra review. Original real-S1 CPU resume identity and mocked end-to-end rehearsal pass again. Approximate useful runtime including two historical continuation allowances is25.02974GPU-h; three12h reservations request36GPU-h. Queue, production iterator/replay and preemption tails remain uncertain. Only passing pytest scratch is removed.

## 21:53 prepare fix — historical state

Coordinator reports Gennadius audit **3748169 COMPLETED/0:0 PASS**, attempt `full-v1-004-genn`, parent payload `e3a023657d27bae8`: **862,423 unique crops** (train **793,227**, dev **16,350**, test **52,846**), **zero collisions**, **364,871/364,871 S1 input splits resolved and matching**, **three train/eval removals**. These are the coordinator's remote results; Sol did not inspect Clariden. The detailed source/class/S1-comparison tables remain in that SHA-bound `AUDIT.json`; the earlier PENDING tables and nominal projections below are historical, not replacement counts. Eval multiplicities remain retained as required.

Prepare **3748213 FAILED/1:0** after31m40s:497,554 harvest records,467,450 written,30,104 `unmapped_script_class` drops. Coordinator's join identifies numerics_tables: train24,889 /dev1,823 /test3,392. Those admitted rows must survive.

S1's deployed [MIX1 export.py](../../harvest/collect_v3_admission/mix1/export.py) explicitly reuses the wave2 label/class adapter “including nonletter -> furniture” and writes that `script_class` into its import feed. Its SHA `d7d368c63d9037a068fe8b00b90815acfdf4b64e0863c7c6e6cbc78281ee68ac` matches [DEPLOYMENT.json](../../harvest/collect_v3_admission/mix1/DEPLOYMENT.json). [encode_admissions](../../harvest/collect_v3_admission/mix1/wave2/deployed_e4_wave2.py) uses `tag(text) or 'furniture'`; [the frozen importer](../../harvest/collect_v3_admission/mix1/wave2/factory/src/import_real.rs) accepts `furniture`. The historical [full export receipt](../../harvest/collect_v3_admission/mix1/run_record/EXPORT_RECEIPT.json) records364,871/364,871 rows, zero drops and full validation/round-trip. `furniture` is an existing script-class metadata value, not a new codec atom or a primary_class remapping. The full old shards are remote; their exact nonletter count is not claimed locally. The next prepare reports observed v4 nonletter class counts directly from its SHA-verified S1 shards.

The fix sets `script_class='furniture'` only when the harvest label has no script under the frozen S1/factory tagger's exact ranges after NFD. Script-bearing records, labels, crop paths, splits, sources, codec and native binary are unchanged. `primary_class=numerics_tables` alone never forces a class: lines with letters still use the native classifier. Every v4 stored row is reused unchanged, including its original script_class. Local fixtures prove byte-for-byte row equality for a digit-only v4 row. Runtime diagnostics report nonletter classes/counts and the native factory receipt.

The native real-import appearance/length checks and aggregate `audit_ok` are explicitly **report-only**. S1 export checks the drop ledger, not `audit_ok`. The accidental aggregate-audit gate is removed; exact feed SHA, zero drops, exact ID/count coverage, frozen shard hashes, labels and split integrity remain required. Reported `length_distribution` long_fraction0.0057 and158+4 lines≥120 need no action: no new length filter, no data removal, no recipe change.

`reuse_audit.py` retains the successful004 audit only if the parent seal is exactly `e3a02365…`, the new seal changes only existing `prepare.py`, the listed new helper/test files are the only additions, and all data config/manifest/input/diagnostic hashes bind. Audit logic, registry, horizon, recipe, codec, sampler, trainer and scorer must be unchanged. Fresh `full-v1-005-genn` keeps an `AUDIT_REUSE.json` linking the old completion/audit/manifest, writes current-package receipts, and references old large manifest files in place. The original004 files/package remain immutable and required. It is inherited clearance, not a new scan. Preparation rechecks all model-input shards and admitted harvest crops. If compatibility refuses, re-audit the intended population; never override the proof. The failed import is not a valid complete stage and is rebuilt; original v4/synthetic/seal04 tensors and completed audit are reused.

For the reported audited **U=793,227**, epoch_rows=**1,586,454**, steps/epoch=**24,789**, eight epochs = **198,312 updates**; **12,691,632 mixed draws**, **6,345,816 real draws**. Four archived checkpoint evaluations at **50,000 /100,000 /150,000 /198,312**, each on all four instruments (16 instrument records). OneCycle total_steps=198,312. The 53,616-update S1-literal alternative remains unchanged. Longer12-epoch option:297,468 updates, six checkpoint evaluations. Historical S1 timing projects **23.78h optimizer /24.76h including rolling checkpoint/startup/epoch validation +4E/3600** for default, **6.76h +2E/3600** for literal, **37.12h +6E/3600** for longer; E awaits real full-instrument smoke. These exclude queue/preemption tails. See [forecast](evidence/GENN_FORECAST_PREPARE_FIX.json). Default still needs at least three12h segments before measured evaluation/tail adjustments; refresh live budget before launch.

**68 tests pass**, including the exact `139` digit shape, decimal/table and punctuation-only labels, all three harvest splits, digit-only v4 row equality, report-only length audit, original CPU resume identity tests, compatibility refusal on changed config/rows/input/mode/package/audit code, and a reused-audit→mocked-factory→real S1 CPU training-loop/evaluation rehearsal. Native factory/model are mocked locally; actual Clariden prepare/CUDA/six-worker forced requeue remain pending. [TESTS_PREPARE_FIX.xml](evidence/TESTS_PREPARE_FIX.xml) and [PREPARE_FIX.json](evidence/PREPARE_FIX.json) bind the evidence and package. Fresh commands are first in [COMMANDS.md](../../../out/TRAIN_FULL_v1/COMMANDS.md): deploy/readback → inherited audit proof → CPU prepare → smoke → Astra prelaunch PASS → conditional owner-authorized launch. No GPU job is submitted by this fix.

## Historical audit fix 2 record

**20:36 audit fix 2:** coordinator reports the complete scan in job **3747871** (`full-v1-002`, payload `becab5e065f057c9`) found 853,419 input rows, 204,417 unresolved v4 train rows and 9 crop issues. Reported dataset-unique 850,725 (train782,149 /dev16,349 /test52,227) remains **UNQUALIFIED**, not a final run population. Both prior attempts remain evidence; Sol has not inspected Clariden. Fresh `full-v1-003` commands use payload **`e3a023657d27bae8ec219afe25289ba7a14fdaee2af35b510131a028efa5079b`**, ID `e3a023657d27bae8`.

The registry builder's `aliases()` records `parliament:55062aa4` under **v2_book_id**, with `line_id_prefix=55062aa4`; the resolver had consulted neither that namespace nor the legacy `-pNNNNNN-lNNNN` form. Restored identity joins: `v2_book_id`, full `pdf_sha256`, and the exact registry prefix parser; global uniqueness remains mandatory. Collection/search URLs and page-PDF hashes remain metadata only. Registry split roles `seal04_dev/test` compare as dev/test. `harvest_protection` applies to new harvest, while the SHA-bound S1 population follows the adopted registry TRAIN assignment (see registry README's split/protection distinction). No split is reassigned. Every S1 row is resolved/compared BEFORE any train dedupe; AUDIT and MANIFEST expose `s1_resolution`, and PASS requires no unresolved/mismatched input row. Local evidence covers all 214,436 rows in the collection-v2 train authority plus all 1,359 editions in the exact S1 split2 map (SHA `1cf086f3…`, 1,159 train /52 dev /148 test), all with zero resolution/split failures, and all assigned typed v2/hash aliases; the full 364,871-row S1 subset remains a fresh remote-audit proof obligation.

Coordinator decision: eval crop identity wins. Every train row matching ANY dev/test/seal04 crop SHA is excluded, regardless of text/book difference, with full row + eval witness in SHA-bound `train_eval_removals.jsonl`. Every eval row survives. Repeated eval crops (including the Serbia dev↔seal04-test boilerplate and same-split oa_uoi `συγχώρησις μᾶς`) are retained in `eval_crop_repeats.jsonl`, with literal labels and equality diagnostics; they are not blocking crop errors. Independent line/book/edition/provider cross-split assignments still block, even on removed train rows. Train-only conflicting labels/book identities still block. The prior nine crop errors include repeated directional reports and do not establish the number of removed train rows. Exact counts/horizon are recomputed after exclusion.

**48 tests pass.** Tests/evidence: [TESTS_FIX2.xml](evidence/TESTS_FIX2.xml), [FIX2.json](evidence/FIX2.json), [IDENTITY_QUALIFICATION_FIX2.json](evidence/IDENTITY_QUALIFICATION_FIX2.json). Real audit, real CUDA requeue smoke, Astra and owner launch go remain pending. No training recipe/horizon/runtime source changed in this fix.

## Bound S1 reference

Use the specified **width ×2 / ref_364871 / seed 0**, from scratch. The deployed package is `84351c178fddab61`, manifest `84351c178fddab61d8b8c8c624db5a164fb0e8481ad0e207694064a6b2b9e004`, deployed source commit `284df89b6e1c8a2cb9709eeae77b0730dfbbd899`. The last commit modifying the trainer is `71e72bfb4f7a70c74d90bcd256b2c9efa70f4aff`.

Evidence copied without alteration: [CELL_COMPLETE](evidence/CELL_COMPLETE.json) (final job 3716977, node SHA `77e39337…`), [seed-0 completion and every explicit parameter](evidence/w2_ref_364871_s0_E1_RUN_COMPLETE.json), [deployment](evidence/DEPLOY_RECEIPT.json), [original sbatch](evidence/s1_w2_ref_364871.sbatch), [INPUTS](evidence/INPUTS.json), [scaling/assembly source](evidence/s1_jobs.py), and [qualification](evidence/QUALIFIED.json). Historical files retain their original paths and status. The direct wheel interpreter `/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python` is evidenced by [S1_SUBMISSION.json](evidence/S1_SUBMISSION.json), and library isolation by [s1_runtime_env.sh](evidence/s1_runtime_env.sh); no GPU uenv view is entered. The copied POLICY contains superseded caps; the shared 350 requested-GPU-h cap in S1_RESULTS governs this task.

Original trainer SHA: `dd0652856e2c46acb63d7b139566f2849fbcbb6afd81b66fda771b80457482f2`; original continuation SHA: `b0d4bfb0cfa40d1c506fdb130b6b00fa363365f25177f2ebdaa51c9406bb6edc`. `vendor/UPSTREAM.json` pins every copied S1 source. `verify.py` reverses and verifies the **one-line trainer change** (also checkpoint at the new cadence). Model, codec, loss, optimizer, scheduler, data assembly, width sampler, original epoch validation and Segment math remain frozen. The population/provenance adapter and checkpoint-evaluation subclass are new and explicitly require real-runtime qualification.

## Population, counts and leakage

The S1 reference is **364,871 train rows**, not 364,871 rows spread across train/dev/test. SCALE1's bound SHA is `0cf865f094ff3f951b5f2bae6a5a0190d0e4209ae71407e94451a2f35be966b3`; HF `fffoivos/greek-ocr-lines`, `staging-v4`, `8ee9cb2e` is the coordinator's release identity. No HF action or independent Hub equivalence check occurred. Training uses S1's exact Clariden subset and shared tensors, rather than reconstructing them from HF.

| Population | Train | Dev | Test | True unique after v4/harvest union |
|---|---:|---:|---:|---|
| S1 ref_364871 real pool | 364,871 | — | — | Existing S1 membership bound; union not yet audited |
| External seal04 instruments | 0 | 437 | 2,253 | Retain every panel row; separate from dataset population |
| Completed final harvest, all eight waves | 417,280 | 16,350 | 52,228 | Receipt counts verified locally; cross-release crop/identity audit pending |
| Training union | PENDING | 0 used for training | 0 used for training | PENDING `MANIFEST.json.train_unique` |
| Dataset union, all splits | PENDING | PENDING | PENDING | PENDING `MANIFEST.json.dataset_unique_crops` |

The fetched [harvest receipt](evidence/HARVEST_RELEASE_RECEIPT.json), SHA `986fd8d09c0e277af4efa344957a087d2c17af2c08c305d2e3dcd930850f4b01`, reports **485,858 rows**. Its [fetch verification](evidence/HARVEST_FETCH_VERIFIED.json) binds TRANSFER SHA `3125e5e209b7299fd9ac32f9d9bdc91172d2aa26df11c713d77ce29e5e7d6f5a`. Local hashes match these receipts; this is not a new remote-byte audit. Nominal union: **850,729 rows**, including **782,151 train** before cross-release dedupe. Neither is a verified unique count. The 412-row review sample confirms the schema; its hash and field types are recorded in [HARVEST_LOCAL_INPUTS](evidence/HARVEST_LOCAL_INPUTS.json), and it is never extrapolated to population counts.

The builder includes W3, W4, W3b-1, W3b-2, W3c-1 and W5-1/2/3; a missing wave refuses. A single `bind_config.py --harvest-root` switch selects any completed compatible release, including `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_with_gennadius_cached_v4`. It receives fresh receipt/TRANSFER hashes, audit, preparation and smoke; no estimated Gennadius gain enters the default count. No HOLD is promoted here.

**First remote job: [audit.sbatch](package/audit.sbatch)**, a0140/preemptable, zero GPUs, 8 CPUs, 80 minutes, `--requeue`. It reads both releases in place without importing the native factory or materializing images. Root metadata is checked against the exact `data/{train,dev,test}/metadata.jsonl` views and TRANSFER hashes. All actual crop bytes, labels and registry identities are verified. It emits `manifest/AUDIT.json`, before/after source × split × class tables, distinct-crop tables by split/source/class, S1-versus-full source/class deltas, `duplicates.jsonl` and `collisions.jsonl`. Every detected registry-row/crop/line/book/edition/provider collision is retained, not only the first. Conflicted counts are labelled UNQUALIFIED and no training manifest is published. Path/SHA/schema failures write a durable `AUDIT_FAILED_*.json`; they cannot clear leakage.

On PASS it seals `rows.jsonl`, train-only `train.jsonl`, `MANIFEST.json` and `AUDIT_COMPLETE.json`. On requeue an unfinished attempt is preserved under `.interrupted-*` and the deterministic scan restarts; a complete stage is reused only under identical config/package/output hashes. Factory preparation requires the exact audit PASS and reuses its manifest. Exact counts/horizon are therefore produced by the CPU audit before any GPU request.

`manifest.py` SHA-checks the S1 subset, shared records/build info, registry v2 (`e1d67490f`, exact adopted gzip SHA in config), sealed suite/panels, harvest receipt/TRANSFER, exported registry, metadata, exact labels and every crop. The final release's adopted registry can add books/aliases; any changed existing v2 assignment, conflict, protected NEW-harvest training book, ambiguous identity alias or contradictory identity fails. Non-identity aliases remain many-to-one metadata and never participate in resolution. Rows resolve through canonical book, edition aliases and provider-item aliases. Book/edition/provider and line identities are checked across **all** input rows; crop checks apply the coordinator's eval-wins train exclusion and preserve eval repeats. A conflict refuses the whole build; it is never resolved by moving a held-out row into train.

After witnessed train↔eval crop exclusion, deterministic train dedupe retains v4 first, then harvest release order; equal crop/line observations with equal exact labels and consistent canonical book identity retain one training row. Conflicting labels/pixels or conflicting books refuse. Dev/test multiplicity is preserved for unchanged instruments, while `dataset_unique_crops` separately counts distinct physical crops in the release union. `rows.jsonl` includes four instruments; `train.jsonl` contains train only. Counts before/after by release × split × source × primary class and duplicate witnesses are in `MANIFEST.json`; external seal04 is reported separately. S1's 277 unclassified rows are retained.

Relocations are explicit exact prefixes and rehash the destination bytes; there is no basename search or native Mac-path fallback. `bind_config.py` moves only S1's known scaling assets into their actual capstor custody namespace and verifies their SHA on use. It does not mask the current harvest's iopsstor namespace. Crop relocation mappings must be supplied by the owner from the actual staged crop inventory. Missing mappings/crops fail with the exact path. The frozen S1 factory is reused by SHA; any new harvest row dropped by its codec/shape/appearance import stops preparation for inspection instead of silently shrinking the dataset. No new normalization rule or admission decision is introduced.

The new `prepare.py` joins v4 rows to the original stored tensors by exact line, source, edition and decoded-label identity; it imports only harvest through the frozen linefactory. Validation for checkpoint selection remains S1's SHA-bound shared validation mix (`f7c1da0b…`), separate from the four requested report instruments. Test results are report-only.

### S1 population by parent

| Parent | Train rows |
|---|---:|
| collect-v3-W1-20261018-0524 | 50,736 |
| collect-v3-W2-20261018-0524 | 117,901 |
| collection-v2-train | 196,234 |

### Source and primary-class baseline

These are exact receipt counts, not remeasured dataset bytes. The full-run comparison column is generated in `MANIFEST.json.after`; no harvest split/source/class counts are invented.

| Primary class | S1 train rows | Full union |
|---|---:|---|
| caps_headings | 10,179 | PENDING |
| curved_skewed | 13,661 | PENDING |
| degraded | 5,728 | PENDING |
| font_extremes | 75,407 | PENDING |
| greek_latin | 5,455 | PENDING |
| historical_russian | 1,525 | PENDING |
| latin | 10,438 | PENDING |
| leaders_dashes | 54,105 | PENDING |
| long | 46,927 | PENDING |
| modern_cyrillic | 2,896 | PENDING |
| monotonic | 42,018 | PENDING |
| numeric_cells | 6,607 | PENDING |
| poly_dictionary_journal | 11,355 | PENDING |
| polytonic | 70,691 | PENDING |
| short | 1,648 | PENDING |
| unclassified | 277 | PENDING |
| vertical_turned | 5,954 | PENDING |

| Source | S1 train rows | Full union |
|---|---:|---|
| anemi_mixed | 14,244 | PENDING |
| anemi_round1 | 46,172 | PENDING |
| anemi_round2 | 18,421 | PENDING |
| archive_AA9613308335D0B014B | 1,459 | PENDING |
| archive_b24878935 | 20 | PENDING |
| archive_b28038630 | 9,432 | PENDING |
| archive_bub_gb_Cmg6AQAAIAAJ | 660 | PENDING |
| archive_bub_gb_mG0mAQAAIAAJ | 1,113 | PENDING |
| archive_izvestiianabul25192530bul | 32 | PENDING |
| archive_izvestiianabulga610193138bulg | 55 | PENDING |
| archive_izvestiianatsars12192829tsar | 57 | PENDING |
| archive_izvestiianatsars1516194243tsar | 18 | PENDING |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 1,509 | PENDING |
| bsb_poly1850 | 18,327 | PENDING |
| elstat | 4,403 | PENDING |
| gazette_modern | 84,078 | PENDING |
| ia_greek_latin | 7,361 | PENDING |
| ia_poly1850 | 26,969 | PENDING |
| kosmopolis | 4,220 | PENDING |
| lekythos | 10,657 | PENDING |
| nlg | 9,396 | PENDING |
| openarchives_Dione | 1,910 | PENDING |
| openarchives_KEIED | 1,941 | PENDING |
| openarchives_Pandemos | 2,370 | PENDING |
| openarchives_anaktisis | 1,961 | PENDING |
| openarchives_apothesis | 1,580 | PENDING |
| openarchives_hellanicus | 1,905 | PENDING |
| openarchives_kallipos | 2,070 | PENDING |
| openarchives_ktisis | 1,868 | PENDING |
| openarchives_mixed_Dione | 411 | PENDING |
| openarchives_mixed_KEIED | 404 | PENDING |
| openarchives_mixed_Pandemos | 58 | PENDING |
| openarchives_mixed_anaktisis | 407 | PENDING |
| openarchives_mixed_apothesis | 584 | PENDING |
| openarchives_mixed_hellanicus | 273 | PENDING |
| openarchives_mixed_kallipos | 23 | PENDING |
| openarchives_mixed_ktisis | 527 | PENDING |
| openarchives_mixed_nemertes | 41 | PENDING |
| openarchives_mixed_ntua | 30 | PENDING |
| openarchives_nemertes | 1,482 | PENDING |
| openarchives_ntua | 1,342 | PENDING |
| parliament_proceedings_1975_2000 | 57,251 | PENDING |
| serbia | 3,226 | PENDING |
| vouli_parliament_1850s | 24,604 | PENDING |

## Recipe table

Every explicit seed-0 completion parameter is included below. The population adapter replaces the old factory-mix provenance format with a SHA-bound runtime/pool format; the training tensors and numerical recipe follow the bindings described above.

| Parameter | S1 seed-0 value | This run | Changed? | Reason |
|---|---|---|---|---|
| `mix` | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/s1_run01/w2_ref_364871/mix.json"` | prepared/runtime.json: unique v4 + harvest train pools, same source-share rule | Yes | Requested whole population; SHA-bound pool adapter |
| `transfer_mix` | `null` | null | No | Exact specified S1 recipe |
| `selection_metric` | `"val_cer"` | "val_cer" | No | Exact specified S1 recipe |
| `transfer_final_only` | `true` | true | No | Exact specified S1 recipe |
| `codec` | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/train_pkg/84351c178fddab61/codec/v2.1.json"` | package/vendor/codec/v2.1.json, same SHA | Path only | Portable copy; exact atom IDs |
| `arch` | `"compact"` | "compact" | No | Exact specified S1 recipe |
| `head` | `"nfd"` | "nfd" | No | Exact specified S1 recipe |
| `epochs` | `8` | 8 | No | Exact specified S1 recipe |
| `bs` | `64` | 64 | No | Exact specified S1 recipe |
| `accum` | `1` | 1 | No | Exact specified S1 recipe |
| `lr` | `0.0001` | 0.0001 | No | Exact specified S1 recipe |
| `wd` | `0.05` | 0.05 | No | Exact specified S1 recipe |
| `no_decay_norm_bias` | `true` | true | No | Exact specified S1 recipe |
| `no_cycle_momentum` | `true` | true | No | Exact specified S1 recipe |
| `seed` | `0` | 0 | No | Exact specified S1 recipe |
| `workers` | `6` | 6 | No | Exact specified S1 recipe |
| `pin_memory` | `true` | true | No | Exact specified S1 recipe |
| `device` | `"cuda"` | "cuda" | No | Exact specified S1 recipe |
| `epoch_rows` | `428872` | `2 × U`, U = audited unique real TRAIN | **Yes** | owner checkpoint cadence + 2.1× pool |
| `pack_bucket_tails` | `true` | true | No | Exact specified S1 recipe |
| `val_mix` | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/train_pkg/84351c178fddab61/runtime01/preflight/validation/mix.json"` | S1 shared validation tensors, unchanged SHA, in prepared runtime | Path/adapter only | Preserve S1 validation CER selection |
| `repeat_to_epoch_rows` | `true` | true | No | Exact specified S1 recipe |
| `width_mult` | `2.0` | 2.0 | No | Exact specified S1 recipe |
| `segment` | `true` | true | No | Exact specified S1 recipe |

| Implicit/operational parameter | S1 | This run | Changed? | Reason |
|---|---|---|---|---|
| Initialization | from scratch | from scratch | No | No donor weights |
| AdamW betas/eps/implementation | Torch 2.11 defaults | Same defaults/runtime | No | Preserve S1 |
| Update horizon | 53,616 | `8 × ceil(2U/64)`; nominal 195,544 | **Yes** | owner checkpoint cadence + 2.1× pool |
| OneCycle schedule | pct_start .075; cycle_momentum false; 53,616 total steps | Same shape/settings; `8 × ceil(2U/64)` total steps from initialization | **Yes** | owner checkpoint cadence + 2.1× pool |
| Gradient clip | global norm 5.0 | 5.0 | No | Preserve S1 |
| CTC | blank 0; zero_infinity true; fp32 CPU in segment mode; reduction mean | Same | No | Deterministic differentiable CPU CTC |
| Effective execution | deterministic algorithms + cuDNN deterministic; benchmark false | Same | No | Parent runtime flags in receipt are not effective trainer flags |
| AMP | CUDA bf16; fp32 CTC | Same | No | Preserve S1 |
| Torch/CUDA/cuDNN/GPU | 2.11.0+cu128 / 12.8 / 91900 / GH200 | Same runtime required; CUDA smoke pending | No intended change | Runtime drift requires review |
| Data seed | 20261015 | 20261015 | No | Largest-remainder quotas; fresh seeded pool permutations each epoch |
| Synthetic fraction | 1/2 of all draws | 1/2 | No | Exact S1 mixture |
| Synthetic source | frozen MIX1D export `prep/A12` | same build_info SHA `e81aa95b…`, exact shards | No | No synthesis or new source |
| Real source distribution | natural within non-parliament/parliament; parliament ≤1/4 of real draws | Same rule on expanded unique pool | Population consequence | Natural shares change with the population; no class upsampling |
| Nonletter harvest script metadata | S1 export supplies `tag(text) or furniture` | Explicit `furniture` only for scriptless labels; v4 shards unchanged | Yes: repair TRAIN_FULL adapter; No S1 semantic change | Restore S1 import handling of admitted digits/punctuation; do not map all numerics_tables rows |
| Real-import audit gate | appearance/length report-only; zero drops and exact membership required | Same; `audit_ok` retained as diagnostic | Yes: remove accidental TRAIN_FULL gate; No S1 semantic change | Frozen admission includes long lines; report-only flags cannot filter |
| Strip/preprocessing | frozen linefactory; grayscale height48; width64–2560; Lanczos3; codec folds; own-bg halo | Same | No | v4 tensors reused exactly; harvest imported by same binary |
| Width batches/padding | 128px buckets; packed tails; own background, masked pad frames | Same | No | Exact sampler/collator/model code |
| Epoch validation | shared real validation CER; best selected by val CER | Same; preserve each epoch | No | Test numbers have no selection role |
| Early-stop patience | 6 in trainer (none of 24 S1 runs stopped) | Disabled by patience=epochs+1 | Yes, explicit necessary change | Guarantee coordinator's fixed 8-epoch horizon; not controlled by test |
| Rolling recovery | optimizer-boundary `segment.pt` every100 updates, stop/deadline, epoch boundary | Same, plus exact evaluation cadence | Cadence extension | Preserve full-state resume and at most99 updates replay after hard kill |
| Archival checkpoints/eval | epoch best/last; final readout | archive every50,000 updates and final; full loss+CER on four instruments | Yes | Owner's checkpoint request |
| Evaluator mode/RNG | original epoch eval | New checkpoint eval saves/restores RNG and mode | New operational code | Eval cannot alter training trajectory |
| Partition/account | normal / a0140 | preemptable / a0140; --requeue | Yes, required | Supplied normal blockage; no normal fallback |
| GPUs | three independent seeds on three requested GPUs/node | one seed on one requested GPU; exclusive node | Yes, required | Only seed0 requested; no data parallelism change |
| CPU/time | whole exclusive S1 cell; 12h +37m continuation | 24 CPUs /12h segments; smoke80m | Untested operational judgment | Six workers, deterministic CPU CTC; qualified throughput came from 3 concurrent seeds |
| Thread environment | historical wheel runtime; not all four keys bound in completion | OMP/OPENBLAS/MKL/VECLIB =1 after runtime | Yes, required operational change | Coordinator's native-runtime lesson; CUDA smoke qualifies timing/identity |
| Runtime environment | direct wheel runtime, no GPU uenv view; HUGETLB=no; package PYTHONPATH | Same; re-export after runtime/view | No intended change | Clear LD_LIBRARY_PATH/PRELOAD; retain CUBLAS_WORKSPACE_CONFIG=:4096:8 |

The 19:46 decision changes only epoch_rows/horizon/schedule relative to the earlier prepared recipe. All other S1 numerical settings and previously disclosed operational changes remain as recorded above. Untested judgments include the adapter, one-GPU/24-CPU request and runtime/thread/operational extensions; the real-runtime smoke must qualify them. The population-relative epoch is an explicit coordinator decision, not an inferred S1 convention.

## Horizon and checkpoints

S1 used `428872` mixed draws per epoch even for the 208k subsets, with `repeat_to_epoch_rows=True`. Its half-synthetic mixture, largest-remainder component quotas and seeded shuffled cycles give `ceil(428872/64)=6702` updates per epoch, hence **53,616 updates**, **3,430,976 mixed draws** and **1,715,488 real draws** over eight epochs. That original epoch is an exposure budget, not a real-pool traversal.

**Default now:** let **U = MANIFEST.json.train_unique**, after cross-release dedupe and successful leakage audit. Each epoch has **2U mixed draws = U real + U synthetic**, eight epochs, batch64, accum1, packed tails. Updates per epoch are **ceil(2U/64)** and the exact OneCycle horizon is **T = 8 × ceil(2U/64)**. The immutable audit receipt records U, epoch_rows, steps/epoch, total draws, T and every checkpoint step. Preparation and run startup independently recompute and bind these values; stale nominal counts cannot launch.

At the **pre-dedupe projection only**, U=782,151 gives epoch_rows=1,564,302, 24,443 updates/epoch, **195,544 updates**, 12,514,416 mixed draws and 6,257,208 real draws. Archived checkpoints/evaluations: **50,000; 100,000; 150,000; 195,544** — four checkpoint evaluations, 16 instrument records. These are exact arithmetic conditional on no cross-release duplicates, not a measured unique horizon. After dedupe the final checkpoint changes automatically. In general there are `ceil(T/50000)` evaluations, without duplicating the final point when divisible by50k.

The unchanged S1 source-quota rule gives one shuffled permutation of every real row when parliament remains ≤1/4 of real support. Preparation checks the exact frozen largest-remainder quotas, and every training epoch verifies that each real pool index occurs exactly once. If the cap would prevent a full real pass, preparation explicitly reports the incompatibility instead of changing the source rule or claiming coverage. The base S1 parliament pool is 57,251 rows, while the fetched harvest source counts contain no `parliament_proceedings_1975_2000`; that implies a nominal7.32% share before dedupe, subject to the actual union audit.

At each checkpoint `eval/step-XXXXXXXXX.json` binds the full-state checkpoint, sample-weighted CTC loss, integer CER denominators, literal predictions and elapsed evaluation time. Instruments remain separate: **seal04 dev, seal04 test, harvest dev, harvest test**. The frozen S1 `bench.score.aggregate` computes CER with literal per-codepoint NFD and preserved emitted atom order; no new hypothesis cleanup, label overlay or panel filtering. Test values remain report-only; they never select, stop or tune a run. Epoch validation/best selection continues using S1's unchanged shared validation CER.

Loss is training-equivalent fp32 CPU `CTCLoss(blank=0,zero_infinity=True,reduction=mean)`, sample-weighted over batches. Targets retain the factory codec representation; CER retains the literal reference text. Incomplete evaluation never publishes a completion log. Checkpoint evaluation restores RNG/model mode so it cannot perturb training.

**Alternative: S1-literal**, selected explicitly with `bind_config.py --horizon s1-literal`: eight fixed428,872-draw epochs, **53,616 updates**, evaluations **50,000 and53,616**. **Longer option only**, `--horizon longer`:12 full-pass epochs (×1.5), nominal **293,316 updates**, evaluations **50k,100k,150k,200k,250k,293,316**. Each alternative needs its own config/manifest/runtime/smoke/Astra/owner binding from initialization; no in-place horizon extension of OneCycle. S1's20/24 runs still improving at epoch8 motivates disclosing the longer cost without enabling it.

## Cost and queue plan

[QUALIFIED.json](evidence/QUALIFIED.json), training job3713868 and CPU readout3714223, measured the width2/ref_364871 profile with three concurrent independent seeds: p90 update bound **0.431688694s**, checkpoint **1.606005696s**, epoch-validation **19.770273582s**, startup **175.890160326s**, restart **233.372017675s**. These are historical measured profile bounds, not measurements of the enlarged width distribution. The old full readout bound3515.09s included its own instrument suite; it is not a validated harvest-evaluation estimate.

Let **E** be seconds for one complete new four-instrument checkpoint evaluation, measured by the real smoke on the final manifest. Expected requested GPU-hours equal one-GPU wall hours, excluding queue wait:

| Option | Updates | Training alone | Including rolling checkpoints, startup and epoch validation | New checkpoint evals | Requested allocation |
|---|---:|---:|---:|---:|---|
| Default8 full-pass epochs, nominal U | 195,544 | 23.45h | ≈24.42h +4E/3600 | 4 | At least three1GPU ×12h segments before evaluation/tail adjustments |
| S1-literal alternative | 53,616 | 6.43h | ≈6.76h +2E/3600 | 2 | One12h segment if measured eval cost fits |
| Longer12 full-pass epochs, nominal U | 293,316 | 35.17h | ≈36.60h +6E/3600 | 6 | At least four12h segments before evaluation/tail adjustments |
| Control +requeue smokes | 4updates each | Negligible vs full eval/startup | Measure E twice per trajectory; one extra restart | ≥2 each | Two1GPU ×80m =2.667 requested GPU-h |

These numerical projections use the **upper pre-dedupe train count**, not an audited U. `readout.py` recomputes all three from the true count, then adds the real smoke's maximum measured E. For context only, substituting the old3515.09s CPU readout allowance gives **28.32h/default**, **8.72h/literal** or **42.46h/longer**; that historical instrument suite is not a harvest-evaluation measurement. Queue wait, factory CPU work, staging and preemption are separate. A hard kill replays at most99 updates from the rolling checkpoint; each restart adds a historical233.37s bound plus any incomplete evaluation recomputation. Repeated preemptions have no finite wall-clock upper bound. Measure new widths/evaluation before the launch estimate is accepted.

The user's supplied partition constraints select preemptable, max1day, requeue. The prepared segment request is12h, safely below24h; forecasts exceeding24h use multiple chained12h segments over the same full-state output. `chain.py --prior` obtains and retains fresh exact-parent sacct proof. COMPLETED/0:0 predecessors omit the dependency (no afterok on purged IDs); active predecessors retain afterok. Failed/unknown predecessors refuse. Deadline yields publish a checkpoint/yield receipt then exit0, allowing a chain to continue. Scheduler preemption requeues the same job. A lock prevents overlapping trainers and submission intents prevent blind duplicate submits. Existing completed runs do not allocate again.

Historical accounting in [S1_RESULTS](../../programme_20261019/SIMPLIFICATION/s1/S1_RESULTS.md) is **118.995 requested GPU-h spent /350**, leaving231.005 at22October's capture. The supplied119 is consistent rounding. This is not live accounting. The nominal default needs at least three12h allocation requests plus two80m smokes: **38.667 requested GPU-h**, leaving **192.338** against that historical balance before other work, extra continuations or requeues. Useful runtime may be less than reservations; preserve actual scoped accounting. The longer four-segment option plus smokes requests50.667 GPU-h. Each extra12h segment adds12 requested GPU-h. An exclusive four-GPU node requested with oneGPU occupies up to4× the requested GPU-hours in node capacity; report both where applicable. Refresh scoped parent-only sacct including failed/retried/active jobs before Astra/owner launch review.

## Validation and next gates

**38 tests passed** on the alias-fixed sealed package (14.46 seconds; previous 23-test evidence retained); shell syntax, Python AST parsing, payload SHA verification and the single-line S1 trainer-diff check also passed. Local tests include default/alternative/longer horizon resolution, exact real-row coverage under the unchanged sampler, CPU audit PASS/reuse and collision diagnostics, split metadata view equivalence, cross-release duplicate handling, crop/line/book/edition/provider leakage rejection, registry authority conflicts, SHA relocation, exact cadence/final checkpoint, frozen scorer order behavior, real S1-loop CPU hard-kill continuation identity, test-metric isolation, a complete tiny release-layout→factory-adapter→training rehearsal, and scheduler dependency mocks. Model/native-factory mocks are explicitly identified in evidence. The exact current test counts and identities are in [TESTS.xml](evidence/TESTS.xml), [REHEARSAL.json](evidence/REHEARSAL.json), and [RESUME_IDENTITY_2.json](evidence/RESUME_IDENTITY_2.json)/[RESUME_IDENTITY_4.json](evidence/RESUME_IDENTITY_4.json). Basetemp is removed only after a passing run; failure evidence is preserved. New local scratch stays below1GB; no dataset/image materialization occurs on this Mac.

Required remote smoke: final production population and runtime, actual width2 model/CUDA/six workers, unchanged scorer on all four complete instruments, tiny cadence2 with evals at2 and4, one actual forced scheduler requeue, then BIT_IDENTICAL comparison of full scientific state/draw/loss traces against uninterrupted control. No mock result may satisfy that gate. The sbatch source/runtime must pass deployed SHA readback and exact sbatch --test-only first. The package and tests can be reviewed now; Astra's prelaunch PASS must also bind the real smoke and exact final package/data identity. Owner go is separately required.

Pending execution gates and risks: full release bytes remain remote; unknown cross-release overlap and registry alias conflicts; unknown exact crop relocation map; factory may reject admitted harvest labels/geometry; unknown new evaluation time and width distribution; S1 instruments remain diagnostic_only pending historical exposure/work-identity audit; six-worker GH200 requeue identity is pending; live budget/partition availability is unverified. No production launch follows from local tests.

**PREPARE FIX READY (pending real prepare, CUDA smoke and Astra prelaunch PASS).** Audit PASS is coordinator-reported and reused only after its identity proof succeeds; no remote execution, smoke, review PASS or launch is claimed by Sol.
