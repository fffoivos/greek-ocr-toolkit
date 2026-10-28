# TRAIN_FULL_v1 — standard ×1 correction

**TRAIN_X1 READY for owner-run smoke; production launch awaits fresh ×1 CUDA BIT_IDENTICAL, focused Astra PASS and the owner's go.** Payload `385856ea2166d9314d65b67cb0380ba4449e80260101a7f787d95b97638faf16` (ID `385856ea2166d931`). Sol performed no remote command, Slurm action, deletion outside passing pytest scratch, commit, push or HF action. The cancelled ×2 chain 3749250/3749252/3749256 and its step-4,690 state remain evidence and must never resume. Current owner brief: [OWNER_X1_CORRECTION.md](OWNER_X1_CORRECTION.md). Earlier preparation history is preserved in [PLAN_BEFORE_X1.md](evidence/PLAN_BEFORE_X1.md).

Package: [package/](package/). Exact deploy → CPU cadence preflight → smoke → focused Astra → launch commands: [COMMANDS.md](../../../out/TRAIN_FULL_v1/COMMANDS.md). Exact source diff against `0446ee734d2c867c`: [X1_SOURCE.diff](evidence/X1_SOURCE.diff); [file inventory](evidence/X1_DIFF_INVENTORY.json).

## Bound S1 ×1 reference

S1 **w1/ref_364871/seed0**, width_mult=**1.0**, from scratch. [Seed-0 E1_RUN_COMPLETE](evidence/w1_ref_364871_s0_E1_RUN_COMPLETE.json), [CELL_COMPLETE](evidence/w1_CELL_COMPLETE.json), [original sbatch](evidence/s1_w1_ref_364871.sbatch), [completion-bound training log](evidence/w1_ref_364871_s0.csv). Cell node SHA `819f1c0d87e8d5712018df290ede956e089e95b008d235720b5c48a5d2e324bf`; completion/test checks verify the receipt and log hashes. S1 package `84351c178fddab61`, deployed commit `284df89b6e1c8a2cb9709eeae77b0730dfbbd899`, trainer commit `71e72bfb4f7a70c74d90bcd256b2c9efa70f4aff`. Its train mix SHA is the same `22b412dd…` as the prior ×2 cell: width changes no data population.

Every frozen vendor module, codec, native importer binding, audit/preparation/horizon module, sbatch time fix and runtime environment is byte-identical to `0446ee734d2c867c`. The vendor trainer still has only its previously reviewed one-line checkpoint-hook edit; `verify.py` reconstructs its original SHA. No scheduler, model architecture implementation, optimizer, loss, sampler or scorer code changed.

## Audited population and reuse

The locally retained [audit](../../../out/TRAIN_FULL_v1/receipts_005/data_manifest_AUDIT.json), SHA `4fa31b81b301d510c586e037249104e2f905075da43c1d2b6b840275b6006ab3`, and [prepared runtime](../../../out/TRAIN_FULL_v1/receipts_005/data_prepared_runtime.json), SHA `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`, bind the successful Gennadius variant. These are retained coordinator remote receipts; no new Clariden audit or smoke was executed by Sol. Audit3748169 and prepare3748345 are historical completed stages. The proof accepts only the exact original prepared005 runtime and verifies unchanged data-producing code, input registry/template, frozen vendor files, environment and data-relevant recipe. Width and new loss cadence are not used in data production. The horizon dictionary recomputes exactly unchanged. All pools are rehashed when consumed.

| Population | Train | Dev | Test | Meaning |
|---|---:|---:|---:|---|
| S1 v4 input | 364,871 | — | — | Exact S1 training membership before eval-wins removal |
| Retained v4 | 364,870 | — | — | One train crop matched eval and was removed with witness |
| Gennadius harvest input | 428,359 | 16,350 | 52,847 | All admitted instrument rows |
| Retained harvest | 428,357 | 16,350 | 52,847 | Two train/eval removals; all eval rows retained |
| Dataset unique crops | **793,227** | **16,350** | **52,846** | **862,423** unique total |
| Dataset retained observations | 793,227 | 16,350 | 52,847 | **862,424**, including one same-split test repeat |
| External seal04 instruments | — | 437 | 2,253 | Unchanged and separate from dataset population |

**Count correction to the latest brief:** harvest test has **52,847 observations /52,846 unique crops** in both the actual prepared pool and reference map. Both loss and CER evaluate **all 52,847 rows**, retaining the duplicate under the coordinator's explicit eval-retention decision. Using52,846 as the instrument denominator would silently filter an eval row. All four instruments therefore total **71,887 evaluated rows per point**. Their logged row counts come from the actual complete pools. This is a documented denominator correction, not new filtering or admission.

Audit PASS: zero collisions; all 364,871 S1 rows resolve to their original splits; three witnessed train/eval crop removals; zero train-only duplicate removals in this Gennadius audit. Registry v2 authority is commit `e1d67490f`; collection/search URLs remain metadata only. Train data excludes dev/test; book/edition/provider/line leakage blocks. Existing dev/test repeats remain report-only. Nonletter lines keep S1's `furniture` fallback; v4 tensors are reused byte-for-byte. Length-distribution `audit_ok=false` remains report-only; no newly admitted row is dropped. Audit/prepare files and old runtime are read in place; no rebind or factory run is necessary. The single harvest-root switch remains available for future separately audited populations, including the Gennadius variant; this package uses the audited005 binding.

### Counts by source and split, versus S1

Distinct crop attribution and S1 input baseline below are aggregated directly from the audit. Train delta includes the witnessed v4 eval-wins removal. Dev/test unique counts are diagnostic crop counts; instruments retain all observations.

| source | S1 train input | Unique full train | Dev unique | Test unique | Train delta |
|---|---:|---:|---:|---:|---:|
| anemi_mixed | 14,244 | 14,244 | 0 | 0 | +0 |
| anemi_round1 | 46,172 | 46,172 | 0 | 0 | +0 |
| anemi_round2 | 18,421 | 18,421 | 0 | 0 | +0 |
| archive_AA9613308335D0B014B | 1,459 | 1,459 | 0 | 0 | +0 |
| archive_b24878935 | 20 | 20 | 0 | 0 | +0 |
| archive_b28038630 | 9,432 | 9,432 | 0 | 0 | +0 |
| archive_bub_gb_Cmg6AQAAIAAJ | 660 | 660 | 0 | 0 | +0 |
| archive_bub_gb_mG0mAQAAIAAJ | 1,113 | 1,113 | 0 | 0 | +0 |
| archive_izvestiianabul25192530bul | 32 | 32 | 0 | 0 | +0 |
| archive_izvestiianabulga610193138bulg | 55 | 55 | 0 | 0 | +0 |
| archive_izvestiianatsars12192829tsar | 57 | 57 | 0 | 0 | +0 |
| archive_izvestiianatsars1516194243tsar | 18 | 18 | 0 | 0 | +0 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 1,509 | 1,509 | 0 | 0 | +0 |
| bsb | 0 | 10,281 | 526 | 1,120 | +10,281 |
| bsb_poly1850 | 18,327 | 18,327 | 0 | 0 | +0 |
| elia | 0 | 3,576 | 0 | 736 | +3,576 |
| elstat | 4,403 | 4,403 | 0 | 0 | +0 |
| gazette_modern | 84,078 | 84,078 | 0 | 0 | +0 |
| gennadius | 0 | 11,079 | 0 | 619 | +11,079 |
| ia_greek_1950_1980 | 0 | 76,460 | 3,863 | 18,788 | +76,460 |
| ia_greek_latin | 7,361 | 7,361 | 0 | 0 | +0 |
| ia_poly1850 | 26,969 | 60,241 | 1,331 | 4,222 | +33,272 |
| ia_poly1900 | 0 | 49,036 | 6,420 | 7,608 | +49,036 |
| iep | 0 | 9,957 | 459 | 1,313 | +9,957 |
| kosmopolis | 4,220 | 4,220 | 0 | 0 | +0 |
| lekythos | 10,657 | 10,657 | 0 | 0 | +0 |
| mytilene | 0 | 3,429 | 0 | 432 | +3,429 |
| nlg | 9,396 | 211,356 | 3,219 | 6,270 | +201,960 |
| oa_uoi | 0 | 11,815 | 174 | 11,307 | +11,815 |
| openarchives_Dione | 1,910 | 1,910 | 0 | 0 | +0 |
| openarchives_KEIED | 1,941 | 1,941 | 0 | 0 | +0 |
| openarchives_Pandemos | 2,370 | 2,370 | 0 | 0 | +0 |
| openarchives_anaktisis | 1,961 | 1,961 | 0 | 0 | +0 |
| openarchives_apothesis | 1,580 | 1,580 | 0 | 0 | +0 |
| openarchives_hellanicus | 1,905 | 1,905 | 0 | 0 | +0 |
| openarchives_kallipos | 2,070 | 2,070 | 0 | 0 | +0 |
| openarchives_ktisis | 1,868 | 1,868 | 0 | 0 | +0 |
| openarchives_mixed_Dione | 411 | 411 | 0 | 0 | +0 |
| openarchives_mixed_KEIED | 404 | 404 | 0 | 0 | +0 |
| openarchives_mixed_Pandemos | 58 | 58 | 0 | 0 | +0 |
| openarchives_mixed_anaktisis | 407 | 407 | 0 | 0 | +0 |
| openarchives_mixed_apothesis | 584 | 584 | 0 | 0 | +0 |
| openarchives_mixed_hellanicus | 273 | 273 | 0 | 0 | +0 |
| openarchives_mixed_kallipos | 23 | 23 | 0 | 0 | +0 |
| openarchives_mixed_ktisis | 527 | 527 | 0 | 0 | +0 |
| openarchives_mixed_nemertes | 41 | 41 | 0 | 0 | +0 |
| openarchives_mixed_ntua | 30 | 30 | 0 | 0 | +0 |
| openarchives_nemertes | 1,482 | 1,482 | 0 | 0 | +0 |
| openarchives_ntua | 1,342 | 1,342 | 0 | 0 | +0 |
| parliament_proceedings_1975_2000 | 57,251 | 57,251 | 0 | 0 | +0 |
| serbia | 3,226 | 11,742 | 358 | 431 | +8,516 |
| uoi | 0 | 8,975 | 0 | 0 | +8,975 |
| vouli_parliament_1850s | 24,604 | 24,604 | 0 | 0 | +0 |

### Counts by primary class and split, versus S1

Classes retain each release's original vocabulary; no new reclassification or equivalence between differently named classes is assumed. Full joint source×split×class tables, input/retained/unique counts and collision witnesses remain in the SHA-bound audit.

| primary_class | S1 train input | Unique full train | Dev unique | Test unique | Train delta |
|---|---:|---:|---:|---:|---:|
| None | 277 | 277 | 0 | 0 | +0 |
| caps_headings | 10,179 | 10,179 | 0 | 0 | +0 |
| curved_skewed | 13,661 | 13,661 | 0 | 0 | +0 |
| cyrillic | 0 | 8,225 | 336 | 420 | +8,225 |
| degraded | 5,728 | 5,728 | 0 | 0 | +0 |
| dialogue_fiction | 0 | 22,355 | 1,231 | 3,128 | +22,355 |
| font_extremes | 75,407 | 75,406 | 0 | 0 | -1 |
| greek_latin | 5,455 | 5,455 | 0 | 0 | +0 |
| greek_mono | 0 | 17,505 | 278 | 1,368 | +17,505 |
| greek_poly | 0 | 87,821 | 7,326 | 28,190 | +87,821 |
| headings_caps | 0 | 8,889 | 206 | 1,017 | +8,889 |
| historical_russian | 1,525 | 1,525 | 0 | 0 | +0 |
| latin | 10,438 | 10,438 | 0 | 0 | +0 |
| leaders_dashes | 54,105 | 54,105 | 0 | 0 | +0 |
| leaders_indices | 0 | 2 | 0 | 0 | +2 |
| long | 46,927 | 46,927 | 0 | 0 | +0 |
| mixed_greek_latin | 0 | 9,250 | 289 | 872 | +9,250 |
| modern_cyrillic | 2,896 | 2,896 | 0 | 0 | +0 |
| modern_scanned | 0 | 588 | 0 | 222 | +588 |
| monotonic | 42,018 | 42,018 | 0 | 0 | +0 |
| numeric_cells | 6,607 | 6,607 | 0 | 0 | +0 |
| numerics_tables | 0 | 25,812 | 1,834 | 3,672 | +25,812 |
| poly1850 | 0 | 171,273 | 2,925 | 6,658 | +171,273 |
| poly1900 | 0 | 76,637 | 1,925 | 7,299 | +76,637 |
| poly_dictionary_journal | 11,355 | 11,355 | 0 | 0 | +0 |
| polytonic | 70,691 | 70,691 | 0 | 0 | +0 |
| short | 1,648 | 1,648 | 0 | 0 | +0 |
| vertical_turned | 5,954 | 5,954 | 0 | 0 | +0 |

## Recipe table — every explicit parameter versus S1 w1/ref_364871/s0

| Parameter | S1 ×1 seed0 | Current run | Changed? | Reason |
|---|---|---|---|---|
| `mix` | `"…/scaling_w3/s1_run01/w1_ref_364871/mix.json"` | `"prepared005/runtime.json, expanded unique train pools"` | Yes | Whole admitted population, SHA-bound adapter. |
| `transfer_mix` | `null` | `null` | No | Exact S1 ×1 seed-0 parameter. |
| `selection_metric` | `"val_cer"` | `"val_cer"` | No | Exact S1 ×1 seed-0 parameter. |
| `transfer_final_only` | `true` | `true` | No | Exact S1 ×1 seed-0 parameter. |
| `codec` | `"…/scaling_w3/train_pkg/84351c178fddab61/codec/v2.1.json"` | `"vendor/codec/v2.1.json, identical SHA"` | Path only | Same codec atom IDs and folds. |
| `arch` | `"compact"` | `"compact"` | No | Exact S1 ×1 seed-0 parameter. |
| `head` | `"nfd"` | `"nfd"` | No | Exact S1 ×1 seed-0 parameter. |
| `epochs` | `8` | `8` | No | Exact S1 ×1 seed-0 parameter. |
| `bs` | `64` | `64` | No | Exact S1 ×1 seed-0 parameter. |
| `accum` | `1` | `1` | No | Exact S1 ×1 seed-0 parameter. |
| `lr` | `0.0001` | `0.0001` | No | Exact S1 ×1 seed-0 parameter. |
| `wd` | `0.05` | `0.05` | No | Exact S1 ×1 seed-0 parameter. |
| `no_decay_norm_bias` | `true` | `true` | No | Exact S1 ×1 seed-0 parameter. |
| `no_cycle_momentum` | `true` | `true` | No | Exact S1 ×1 seed-0 parameter. |
| `seed` | `0` | `0` | No | Exact S1 ×1 seed-0 parameter. |
| `workers` | `6` | `6` | No | Exact S1 ×1 seed-0 parameter. |
| `pin_memory` | `true` | `true` | No | Exact S1 ×1 seed-0 parameter. |
| `device` | `"cuda"` | `"cuda"` | No | Exact S1 ×1 seed-0 parameter. |
| `epoch_rows` | `428872` | `"1,586,454 = 2 × 793,227"` | CHANGED | owner checkpoint cadence + 2.1× pool; eight real passes. |
| `pack_bucket_tails` | `true` | `true` | No | Exact S1 ×1 seed-0 parameter. |
| `val_mix` | `"…/scaling_w3/train_pkg/84351c178fddab61/runtime01/preflight/validation/mix.json"` | `"S1 shared validation pool, identical tensors"` | Path/adapter | Preserve S1 epoch validation and best selection. |
| `repeat_to_epoch_rows` | `true` | `true` | No | Exact S1 ×1 seed-0 parameter. |
| `width_mult` | `1.0` | `1.0` | No | Exact S1 ×1 seed-0 parameter. |
| `segment` | `true` | `true` | No | Exact S1 ×1 seed-0 parameter. |

| Implicit / operational parameter | S1 ×1 | Current run | Changed? | Reason |
|---|---|---|---|---|
| Initialization | From scratch | From scratch, standard ×1 | No | Never load or resume the cancelled ×2 model |
| Epoch/update horizon | 428,872 mixed draws/epoch;53,616 updates total | 1,586,454 mixed draws/epoch;198,312 updates total | **CHANGED** | owner checkpoint cadence + 2.1× pool; coordinator full-pass horizon retained |
| OneCycle | pct_start=.075, cycle_momentum=false,53,616 steps | Same settings;198,312 total steps from initialization | **CHANGED** | Same full-pass horizon decision |
| AdamW | betas/eps defaults; wd=.05; norm/bias no decay | Identical implementation/runtime | No | Preserve S1 |
| CTC / precision | blank0, zero_infinity=true, mean; fp32 CPU CTC; CUDA bf16 model | Identical training and reporting loss; sample-weighted dataset mean | No | Loss uses frozen codec targets |
| Gradient clip | Global norm5 | 5 | No | Preserve S1 |
| Determinism | Deterministic algorithms/cuDNN; benchmark=false | Identical effective flags/runtime | No | Original trainer flags, not parent launcher defaults |
| Runtime | Torch2.11.0+cu128, CUDA12.8, cuDNN91900, GH200 | Same direct wheel runtime required | No | New ×1 smoke must prove continuation |
| Synthetic draws | 1/2; frozen MIX1D prep/A12 source | 1/2;190,486-row frozen pool, same hashes | No | Disclosed source; no new synthesis |
| Real draws | Natural shares; parliament≤1/4 real | Same rule;735,976 non-parliament +57,251 parliament per epoch | Population consequence | Full-pass quotas verified without class upsampling |
| Data seed / assembly | 20261015; largest remainder; shuffled cycles | Identical | No | Every real row once each full epoch |
| Preprocessing | Frozen factory, grayscale48px, Lanczos3, own-bg halo, codec folds | Identical; v4 tensors unchanged | No | No image/label recipe change |
| Nonletter script / length audit | `tag(text) or furniture`; length/appearance reports only | Same admitted-digit fallback and diagnostic flags | No S1 semantic change | Keep all admitted numeric/punctuation rows; no new filters |
| Width batches | 128px buckets, packed tails, shuffled batches | Identical; partial batch may occur within epoch | No | Actual rows, not step×64, drive loss cadence |
| Epoch validation / selection | S1 shared13,088-row validation CER; best by val_cer | Identical epoch validation and best selection | No | Report instruments never select a checkpoint |
| Patience | 6; no S1 run stopped early | Disabled via patience=epochs+1 | Yes, inherited full-run change | Guarantee eight complete real passes |
| Regular loss reports | No per 50k-line hook | **Every50,000 actual mixed drawn lines + final**, all four complete instruments, loss only | **Yes** | Owner correction; no argmax, decoding, CER or predictions at these points |
| Archived full reports | Epoch best/last; final readout | **50k/100k/150k/198,312 updates**, full four-instrument loss+CER | Yes, retained requested sparse checkpoints | Unchanged S1 scorer; archive full-state checkpoint |
| Eval trajectory isolation | Original epoch validation | New hooks save/restore Python/NumPy/Torch/CUDA RNG and model mode | Operational extension | Test numbers report-only; loss eval cannot affect training |
| Rolling recovery | Full model, opt, scheduler, RNG, draw/iterator cursor; every 100 updates/stop/deadline/epoch | Identical, plus saves before loss/full eval | Cadence extension | Incomplete eval resumes before next draw;≤99 updates replay after hard kill |
| Partitions / segments | normal, a0140 | preemptable, a0140,--requeue;12h segments≤24h | Required inherited change | Owner-supplied normal blockage; no normal/debug fallback |
| Resources | Three concurrent S1 seeds/GPU allocations | One seed, one GPU,24 CPUs, exclusive node | Required operational choice | Six workers retained; single-run throughput requires smoke |
| Environment | Direct wheel runtime; no GPU uenv | Same; four thread keys=1, PYTHONPATH=pkg+vendor, HUGETLB_ELFMAP=no | Inherited operational binding | Re-export after view; clear LD_LIBRARY_PATH/PRELOAD; CUBLAS=:4096:8 |
| Deadline / chaining | Historical S1 continuation | `SLURM_TIME_FORMAT=standard` on squeue; predecessor sacct proof; fresh claims | Inherited fix | No relative-date parsing or afterok on purged COMPLETED IDs |
| Smoke timing | S1 timing qualifier synchronizes GPU | Sync before smoke-only timing samples; production remains original asynchronous execution | Diagnostic only | Measure completed update time without folding eval into it |

The ×1 model width itself is **unchanged versus the newly selected S1 baseline**. Relative to the cancelled package it changes2→1. Untested operational judgments are limited to expanded-data performance, one-GPU/24-CPU throughput and new evaluator/recovery overhead; the fresh CUDA smoke and focused Astra review must qualify them. LR/batch remain the owner's exact S1 values, not newly tuned values.

## Exact horizon and two evaluation cadences

For U=793,227 unique real train rows, epoch_rows=**1,586,454**, steps/epoch=**ceil(1,586,454/64)=24,789**, eight epochs=**198,312 updates**, **12,691,632 mixed drawn lines**, **6,345,816 real draws** and the same synthetic count. Width does not enter this arithmetic. OneCycle is initialized over198,312 steps. S1's original epoch was a fixed exposure budget428,872 mixed draws for every subset; it was not a full real-pool traversal.

Loss reports trigger at the first completed optimizer batch whose cumulative **actual** draw count crosses50,000×k. There are**253 thresholds**,50,000 through12,650,000, plus a final point at12,691,632 draws: **254 unique loss-evaluation steps**. Batch64 gives nominal781.25updates between thresholds, but the22-row partial batch is shuffled within each epoch. Global_step×64 is therefore wrong. `loss_cadence.py` replays the exact unchanged assembler and packed sampler with private seeded RNGs; it emits every exact step, drawn_lines and crossed threshold before training. The owner-run CPU `run.py --plan-only` writes that **254-entry step list** from actual prepared widths. It cannot be numerically enumerated on this Mac because those full tensors remain on Clariden. The count and final horizon are known exactly from retained receipts. `RUN_BINDING.json` and `LOSS_CADENCE.json` bind the list; the training hook verifies each actual draw count against it.

Sparse archived full loss+CER points remain **[50,000,100,000,150,000,198,312] updates** (four points, sixteen instrument results). Full predictions and unchanged S1 NFD-atom scorer outputs are retained. The final loss-only point also exists; full and loss logs have separate roles, without extra intermediate archives at every 50k drawn lines.

Loss uses `CTCLoss(blank=0,zero_infinity=True,reduction=mean)` on fp32 CPU, identical to training. Model is in eval mode; all rows are evaluated once per instrument and losses are sample-weighted across batches. No decoding, greedy argmax, scoring or predictions occur in the loss-only path. The append-only `loss_eval.jsonl` contains step, actual drawn_lines, per-instrument loss and row count, plus the SHA-bound immutable `loss_eval/step-*.json` record. A durable full-state segment precedes each report. Startup finishes any pending current report and reconciles a missing journal append from its immutable record. Torn index appends are preserved and witnessed, never truncated. Duplicate/changed or missing historical points refuse; COMPLETE requires the exact full list. RNG and mode restore even on an evaluation exception. Test values never choose, stop or tune anything.

Alternative only: **S1-literal**,53,616 updates,3,430,976 draws,**69 loss points**, full CER50k/end. Longer option only: **12 full passes**,297,468 updates,19,037,448 draws,**381 loss points**, six full CER points. Neither is default; either requires its own initialization/config/smoke/review, never an in-place OneCycle extension.

## Cost and scheduling

The bound **×1** S1 log totals**5,580.0seconds /53,616 updates =0.1040734109seconds/update**, including per-epoch work but excluding initial startup and end-epoch checkpoint writes. Linear projection to198,312 gives**5.7331h** (historical three-concurrent-seed widths, not a current GH200 measurement). Longer horizon8.5997h; S1-literal1.55h. The cancelled ×2 run's≈0.21seconds/update is coordinator evidence only and is not a ×1 qualification. Old width2 p90=.431689s is no longer the default optimizer estimate. The [timing source](package/s1_w1_timing.json) and completion-bound CSV identify the actual ×1 measurement.

Let s=measured ×1 synchronized mean update seconds in the smoke, L=max measured full-instrument loss-only seconds, C=max measured full-instrument CER+loss seconds. `readout.py` reports**198312s/3600 optimizer hours**,**254L/3600 loss hours**,**4C/3600 sparse full-eval hours**, their combined overhead fraction, and12h segment count. It separately keeps the historical ×1 projection. Startup175.89s, restart233.37s, checkpoint1.606s and epoch validation19.77s remain explicitly historical width2 allowances, not new ×1 measurements; the existing rolling-save count plus a conservative extra allowance per loss point is included. Add queue, actual restart/preemption and production epoch assembly/cadence-planning tails. Tiny smoke widths/sample count may not represent the whole pool. Update the forecast during production; the cancelled ×2 speed does not certify ×1 throughput.

All254 loss points evaluate18,259,298 rows in total. Loss alone exceeds25% of the historical optimizer projection if L exceeds≈20.31 seconds; full CER lowers that threshold further. The real smoke must measure rather than assume this cost. If combined evaluation exceeds25%, the readout explicitly reports options: retain the exact cadence and reserve its cost; owner-approved larger drawn-line interval with reseal/review; or qualify a faster complete-instrument loss evaluator against exact loss parity. **No silent row subsampling or changed cadence.** The historical ×2 full-eval124.91s is not substituted for an unknown ×1 loss-only L.

Two 80 min 1 GPU smokes reserve**2.667 requested GPU-h**. Production reservesN×12requested GPU-h, where N comes from the measured forecast; each extra12h segment requests12more. Useful GPU time differs from reserved/requested time. An exclusive4GPU node can occupy4× requested GPU-hours in node capacity. The historical118.995/350GPU-h ledger is stale: refresh scoped accounting including all failed/cancelled smokes and the cancelled ×2 chain before launch. No budget or wallclock bound is asserted from that old balance. Preemption repeats have no finite wallclock bound.

Every segment uses preemptable,--requeue,12 h ≤ 24 h, and the same fresh ×1 output. Active parents get afterok; alreadyCOMPLETED/0:0 parents use retained sacct proof and authenticated yield without a purged-ID dependency. Failed/unknown parents refuse. Old failed/cancelled claims remain in place; new controls cannot overwrite them. Never pass a cancelled ×2 job as --prior. Native thread/runtime bindings and format-independent deadline handling are unchanged.

## Local evidence and remaining gates

The full sealed-package suite is recorded in [TESTS_X1_RELEASE.xml](evidence/TESTS_X1_RELEASE.xml). It covers literal S1 ×1 parameter/receipt/log identity, unchanged horizon, data-only reuse, old ×2 smoke refusal, actual shuffled-partial-batch cadence, no-decode/full-loss parity, report-only metrics, append-only/torn journal recovery, hard kills before/after loss/full publication, unfinished evaluation recovery, RNG/mode isolation, whole scientific state resume identity, source/crop/edition leakage and dedupe, offline release→factory→real S1 CPU trainer rehearsal, and relative/far-date Slurm wrapper mocks. Model/native factory are explicitly mocked locally; CTC, optimizer, scheduler, real S1 trainer and frozen scorer execute on CPU. Passing pytest basetemp is removed after saving evidence; failed collection scratch is preserved. Local scratch remains below1GB.

Fresh CUDA smoke: actual standard ×1/GH200/bf16/S1 runtime, six workers, production pools and all complete instruments; two192-draw epochs, six updates; loss at**2/4/6** (128/256/384 draws), full CER at**3/6**; forced durable scheduler requeue after step 3. Compare uninterrupted versus requeued model, optimizer, scheduler, RNG, iterator cursor, draw/loss traces, best/patience/health and all metrics for BIT_IDENTICAL. Require actual restart_count≥1, the first allocation's yield SHA matching the immutable step-3 archive, and measured loss/full/update times. Old ×2 CUDA smoke and Astra review cannot clear this gate. Run focused Astra on this exact seal plus current smoke/test/readout; launch only with its PASS and owner go. All remote execution remains for the coordinator.

TRAIN_X1 READY (pending fresh ×1 CUDA smoke, focused Astra PASS and owner go).
