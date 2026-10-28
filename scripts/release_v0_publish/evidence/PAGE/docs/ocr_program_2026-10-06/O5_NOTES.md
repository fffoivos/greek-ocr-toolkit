# O5 preparation and offline paired real-image runner

Updated 2026-10-07 after CP-O5prep review 1 and the binding coordinator correction.
**PROVISIONAL** machine-admitted O1d labels, not human-verified. The owner-sealed O2 set gates publishable claims later. Full GPU training and full synthetic rendering have not been launched here.

Question: Does training on REAL line images move the recogniser more than factory renders of the SAME text?
Frozen arms: base (no training), synth (factory renders), real (real crops). Incumbent: `out/prime_checkpoints/t1_compact_nfd_s2/best.pt`, compact/NFD/v1, SHA256 `512553499587306769cac792baf9de7b52399e1aac8374618c24ab0adccaa976`. Full paired seeds 0,1,2. Strict NFD CER is the unchanged `train/eval_cer.py::evaluate`, overall/per-script with `label_ids` reference. Unchanged `out/transfer_dev_v4/reserved` is the font-OOD do-no-harm instrument.

## Pre-registered rule (verbatim)

per seed, Δ = CER(synth) − CER(real) on the real test slice. Verdict "real images are the lever" iff Δ > 0 for all 3 seeds and mean Δ ≥ 0.005 absolute. Verdict "text/label distribution is the lever" iff both arms improve over base by ≥ 0.005 but |mean Δ| < 0.005. Verdict "neither" iff neither arm improves over base by ≥ 0.005. Report the raw per-seed numbers whatever the verdict.

“Both/neither arms improve” uses mean arm CER across the three seeds. Uncovered outcomes are explicitly `inconclusive`; one-seed smoke is `incomplete`. Raw per-seed values remain reported.

## Selection and stopping — binding coordinator correction

Training uses `--val-dir out/o5/<arm>/val` **without `--transfer-dev`**. Best checkpoint and patience use only DEV `val_cer`, on each arm's corresponding images of the paired DEV labels. TEST and font-OOD are evaluated only once on each final `best.pt` and the base; hash-bound eval receipts are reused on retries.

Full budget remains eight epochs, bs64, accum1, lr1e-4, wd0.05, no-decay-norm-bias, no-cycle-momentum; trainer patience remains six. Identical paired widths imply identical width-bucket update budgets. DEV early stopping is accepted and terminal: the runner records actual epochs/updates and `early_stopped` in `O5_COMPLETE.json`, then evaluates/reports. REPORT.md/JSON call this **equal budget, early-stopped** when any arm stops short of eight. They do not claim equal realized updates in that case. No trainer stopping behavior was changed.

## Preparation, exclusion and realized counts

Read all 628,468 certified native record rows; 358,471 admitted; 351,262 eligible before caps. Codec normalization exactly follows Rust: NFD, enumerated folds, whitespace collapse/trim; reject unknown atoms and lengths outside 3–140 normalized NFD codepoints. Eligibility and strip-floor drops affect both arms.

Seed 20261007; sort document IDs then shuffle independently of line sampling. Zero-based every fifth doc (0,5,…,175) supplies 36 TEST docs; first nine remaining are DEV; last 132 are TRAIN. Uniform seeded caps: TEST100/doc, DEV40/doc, TRAIN150/doc then 20,000 overall. RNG consumption remains reserved → val → train, with no refill after exclusions. Smoke samples 500 train, 80 dev, 160 test before exclusion.

After those document-disjoint draws, subtract every TRAIN/DEV row whose **NFC, whitespace-collapsed codec-label text** equals a TEST label. The same selected manifests supply real strips and synthetic input. Full subtraction: **28 rows (27 TRAIN + 1 DEV), covering 15 distinct texts**. TEST stays 3,600 rows. `exclusions_test.txt` has 3,595 unique normalized TEST texts, one per line, plus two `#` header lines documenting normalization and the absence of DOC/TEXT/TAB fields. Factory loads raw lines through its codec normalizer; header lines merely add harmless exclusion entries. Existing recipe exclusions are retained and this manifest is appended.

| Slice | Documents | Lines | greek_mono | greek_poly | greek_latin_cs | latin | cyrillic |
|---|---:|---:|---:|---:|---:|---:|---:|
| full train | 132 | 19657 | 14712 | 104 | 3121 | 1709 | 11 |
| full val | 9 | 359 | 304 | 1 | 42 | 12 | 0 |
| full reserved | 36 | 3600 | 2660 | 0 | 494 | 446 | 0 |
| smoke-fix train | 130 | 500 | 390 | 5 | 67 | 38 | 0 |
| smoke-fix val | 9 | 80 | 62 | 0 | 12 | 6 | 0 |
| smoke-fix reserved | 36 | 160 | 120 | 0 | 24 | 16 | 0 |

Full counts precede factory-pair filtering. Zero provisional test polytonic/Cyrillic rows means no test claim for those classes.

| Drop / selection trim | Full | Reduced smoke |
|---|---:|---:|
| length_outside_3_140_nfd | 27 | 27 |
| nonrepresentable_atom | 7176 | 7176 |
| not_admitted | 269997 | 269997 |
| reserved_document_cap | 63175 | 63175 |
| reserved_smoke_cap | 0 | 3440 |
| train_document_cap | 245487 | 245487 |
| train_pool_cap_20000 | 0 | 0 |
| train_smoke_cap | 0 | 19184 |
| train_test_text_exclusion | 27 | 0 |
| unmapped_script_class | 6 | 6 |
| val_document_cap | 18956 | 18956 |
| val_smoke_cap | 0 | 280 |
| val_test_text_exclusion | 1 | 0 |

`build_info.json` records all source/crop/codec/recipe/shard hashes, occurrence-level removed-row ledger, document assignments and counts. `preparation_hashes` binds the complete train/dev/test manifests, synthetic corpus and TEST exclusions; driver verification, scheduling and restamping reject a changed manifest/corpus/exclusion file. Full regeneration was staged in clean `out/o5_full_fix_stage` before publishing the authoritative files into `out/o5`, to keep historical smoke shards outside the full preparation hash list.

Crop → grayscale uint8, aspect-preserving height48 LANCZOS resize; width64..2560, own-background right padding, vertical letterbox for over-wide crops, 14px floor, never squeeze/clip. At most4096 rows/shard, exact contract Arrow types. Stable O1 occurrence IDs preserve repeated TRAIN/DEV text in different documents. Real provenance: severity0, applied_ops[], font/bg_type real, dark_on_light, accent_survival1, reuse_index0, source_dataset o1d_real, research-only.

## Factory scheduling and pairing

Recipe of record `factory/recipe.v1.json` SHA256 `03c132afd4bd8198161b206884f7d601b764ac5de045bd51ab6671643a03214e`. O5 scheduling changes only target_total (20,016 full jobs), combined selected TRAIN/DEV content marginals, reuse.max_per_line1, and appended TEST exclusion manifest. All visual settings/defaults/fonts/ink/distortions/backgrounds are inherited. Stock ingest now uses that exclusion-bound scheduling recipe and retains its audit; authoritative `factory_pool.o5.jsonl` pins selected document splits and occurrence IDs before rendering. Factory build is complete at the selected scale, never truncated by factory `--smoke`. TEST docs/texts are absent, including the verso/neighbor bank.

Restamp discloses corrected O1 split/class/document/line_id/license; provenance `o1d_real_factory_render`. Pixels/visual metadata stay intact. Missing/excluded or label-changing renders are dropped symmetrically. Each pair gets own-background right padding to its shared maximum width so width buckets and update budgets match. Immutable unpaired snapshot + staged restamp is retryable. Scheduler, raw-render guard, real-source guard and final pair checker all reject TEST transcripts. Final checker verifies both arms' TRAIN and DEV text-disjointness from TEST, document separation, exact identity/labels/class/split/width, image dimensions and shard hashes.

No certified source tool, factory codec/recipe, transfer-dev or strips_v4a/v5 was changed for this fix. The existing train.py init-from addition remains 37 added/zero removed lines against HEAD; O5-fix adds no trainer changes.

## Checkpoints and recovery

`--init-from` strictly loads compact/NFD/v1 model weights; optimizer/scheduler/step/RNG start fresh at the paired seed. It is incompatible with resume and records the source hash. Existing trusted full-state O5 resumes preserve optimizer, scheduler and RNG.

Before reuse/resume, the runner loads last.pt AND best.pt; checks configuration/init hash, best epoch and checkpoint_meta's best hash, full-state fields and CSV commit epoch/step. It checks checkpoint hashes against available `O5_EPOCH_COMMIT.json` and `O5_COMPLETE.json`. Valid interrupted states trim trailing uncommitted CSV rows. A truncated archive, hash mismatch, absent surviving archive or inconsistent best/last/meta/CSV state is archived under `runs/<arm>/recovery/attempt-NNN`; checkpoint/safetensors/CSV/metadata/completion artifacts are removed from the live arm and the same seed restarts from `--init-from`. The second retry cannot load the corrupt path again.

The trainer still writes directly: this O5 runner uses the explicitly permitted clean-restart fallback, rather than promising a preserved previous epoch. Epoch commit/completion receipts are atomically written when the runner validates a terminal trainer state. A valid DEV-early-stopped checkpoint is terminal and never resumes additional epochs. Code/config/data changes fail closed; use a fresh O5_OUT for changed training.

## Validation and reduced CPU smoke

Existing `.venv/bin/python` (Python3.11.3, torch2.13.0 CPU), no installs/network/GPU/sub-agents/commits. Current smoke: `out/o5/smoke_fix_1`; old `out/o5/smoke` is historical and predates the exclusion/DEV-selection correction.

```bash
.venv/bin/python -u bench/o5_prepare.py --out out/o5_full_fix_stage > out/o5_fix_prepare_staged.log 2>&1
# Publish only the new full real/test shards, manifests, corpus, exclusions and build_info;
# preserve the historical smoke directories. Then bind the full scheduling recipe:
.venv/bin/python bench/o5_pair.py schedule --out out/o5
O5_SMOKE=1 O5_SMOKE_ROWS=500 O5_OUT="$PWD/out/o5/smoke_fix_1" \
  OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHON="$PWD/.venv/bin/python" \
  bash bench/o5_run.sh > out/o5_fix_smoke.log 2>&1
OMP_NUM_THREADS=2 .venv/bin/python -m pytest -q \
  bench/tests/test_o5.py bench/tests/test_o5_init.py bench/tests/test_o5_recovery.py
```

Pytest: **27 passed in 1.93s**. Includes cross-document repeated NFC/whitespace labels, symmetric exclusion, scheduling custody, manifest-class tampering, partial ZIP last/best, loadable committed-hash mismatch, two-retry clean restart, valid CSV rollback, DEV early stopping, standalone report disclosure, and TEST-text rejection in each arm/split. Shell syntax/Python compilation pass.

Reviewer probes rerun from copies under `out/o5/review_fix_1` (original scratch unchanged). `probe_adaptations.diff` documents only new smoke paths/expected update receipts, independent TEST-text subtraction and reversed restart expectation. `audit_data.py` independently reconstructed all628,468 inputs, source hashes, seeded selected IDs/order and the entire updated drop ledger; zero train/dev/corpus overlap. `audit_probes.py` used the reviewer's existing actual-Rust codec harness: **50/50** codec/label matches, **50/50** independent resize pixel matches, seven full shard schemas. Restart/eval evidence and the completed smoke tail follow below.

## Exact coordinator commands on the A100 node

Provide certified native records/crops (repository suffix paths), assets/fonts/watermarks, factory files, codec/v1.json, base checkpoint and unchanged transfer_dev_v4 locally. Transfer only full `real/`, `test/`, manifests, `synth_corpus.jsonl`, `exclusions_test.txt`, and top-level `build_info.json`; generated scheduling files are regenerated on node with relocated paths. Or prepare in a clean out/o5 directory on node. Activate the already-provided Python3.12 venv:

```bash
cd /path/to/greek-page-ocr
export PYTHON="${VIRTUAL_ENV:?activate the existing Python 3.12 venv}/bin/python"
"$PYTHON" -c 'import sys,torch,pyarrow,numpy,PIL; print(sys.version, torch.__version__, torch.cuda.is_available())'
"$PYTHON" -u bench/o5_prepare.py --out out/o5  # omit for verified transferred preparation
O5_SMOKE=0 O5_OUT="$PWD/out/o5" bash bench/o5_run.sh > out/o5_node.log 2>&1
tail -20 out/o5_node.log
```

Rerun the same final command to resume/recover; keep budget/seed/data unchanged. Uses existing `factory/target/release/linefactory`, or cached offline `cargo build --offline --release --manifest-path factory/Cargo.toml` before fingerprinting.

Equivalent fresh full training command, ARM∈synth/real, SEED∈0/1/2:

```bash
"$PYTHON" train/train.py --init-from out/prime_checkpoints/t1_compact_nfd_s2/best.pt \
  --arch compact --head nfd --codec codec/v1.json \
  --train-dir out/o5/ARM/train --val-dir out/o5/ARM/val \
  --epochs 8 --bs 64 --accum 1 --lr 1e-4 --wd 0.05 \
  --no-decay-norm-bias --no-cycle-momentum --seed SEED --workers 6 \
  --pin-memory --device cuda --out-dir out/o5/runs/ARM_sSEED
```

Final evaluation, for base and every final best.pt:

```bash
"$PYTHON" bench/o5_eval.py --ckpt CHECKPOINT --data-dir out/o5/test/reserved \
  --device cuda --bs 64 --out out/o5/eval/NAME_real.json
"$PYTHON" bench/o5_eval.py --ckpt CHECKPOINT --data-dir out/transfer_dev_v4/reserved \
  --device cuda --bs 64 --out out/o5/eval/NAME_ood.json
"$PYTHON" bench/o5_report.py --out out/o5
```

## Completed smoke and review evidence

Factory audit passed; 580/580 renders, zero symmetric drops. Final paired TRAIN500/DEV80; own-background right-padding real230/synth350. Both arms completed epoch1 with **27 optimizer updates**, selected on DEV val_cer. Fresh independent evaluation matched all six saved metrics and weights exactly. Four-byte truncated-last fault injection reached clean same-seed `--init-from` on both retries; no subprocess/training ran in that probe. Full manifest tampering is rejected by verification and scheduling. Runner retry reused both trained arms and all six hash-matched eval receipts without compute.

| Arm | TEST strict NFD CER | Font-OOD CER |
|---|---:|---:|
| base | 0.099266 | 0.056473 |
| synth | 0.107411 | 0.059722 |
| real | 0.098013 | 0.062094 |

Actual tail of `out/o5_fix_smoke.log`:

```text
O5_EVAL: synth_s0_real.json CER=0.107411 lines=160
+ /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/.venv/bin/python -u /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/o5_eval.py --ckpt /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1/runs/synth_s0/best.pt --data-dir /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/transfer_dev_v4/reserved --device cpu --bs 32 --out /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1/eval/synth_s0_ood.json --limit 128
[model] arch=compact: n_classes=248, params=3,771,192 (3.77M)
[model] arch=compact: n_classes=248, params=3,771,192 (3.77M)
O5_EVAL: synth_s0_ood.json CER=0.059722 lines=128
+ /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/.venv/bin/python -u /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/o5_eval.py --ckpt /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1/runs/real_s0/best.pt --data-dir /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1/test/reserved --device cpu --bs 32 --out /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1/eval/real_s0_real.json
[model] arch=compact: n_classes=248, params=3,771,192 (3.77M)
[model] arch=compact: n_classes=248, params=3,771,192 (3.77M)
O5_EVAL: real_s0_real.json CER=0.098013 lines=160
+ /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/.venv/bin/python -u /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/o5_eval.py --ckpt /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1/runs/real_s0/best.pt --data-dir /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/transfer_dev_v4/reserved --device cpu --bs 32 --out /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1/eval/real_s0_ood.json --limit 128
[model] arch=compact: n_classes=248, params=3,771,192 (3.77M)
[model] arch=compact: n_classes=248, params=3,771,192 (3.77M)
O5_EVAL: real_s0_ood.json CER=0.062094 lines=128
+ /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/.venv/bin/python /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/o5_report.py --out /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1 --smoke
O5_VERDICT: incomplete | meanΔ=0.009398 | seeds_positive=1/3
O5_COMPLETE: /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/smoke_fix_1 (SMOKE ONLY; not the three-seed experiment)
```

Finding → fix → evidence for H01/H02/M01/L01 is in `reviews/CP-O5prep_reply_1.md`; none deferred. Fresh evidence replaces the historical smoke for current preparation/selection behavior. Full three-seed scientific verdict remains unmeasured.
