# REL0-S1 — Sol: model error analysis + speed benchmark for Greek OCR v0.n (×1, ×1.5, ×2), 28 Oct 2026 Europe/Athens

Plan: docs/programme_20261028/RELEASE_v0/PLAN.md rev 2, step 1 (read §4 selection contract and §7). Owner brief: docs/programme_20261028/RELEASE_v0/OWNER_BRIEF.md.
You write code + tests + a COMMANDS.md only. You have no SSH/network; the coordinator runs everything on Clariden. The Mac is not a processing worker: local tests use tiny fixtures only.

## Objective
One analysis tool and one speed benchmark, parameterised by a run list, so ×1.5/×2 run now and ×1 later with the same code.

## Inputs on Clariden (read-only; never write inside run or data directories)
- Runs: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-013-stage-c-sel/full/runs/{w1.5-full,w2-full}` and (later) `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-014-w1-h14/full/runs/w1-full` (publish label `w1h14-full`; the retired 013 `w1-full` is excluded).
  Each has `eval/step-<N>-<instrument>.predictions.jsonl` (`{"id","hyp"}`) and `eval/step-<N>.json` (aggregate scores per instrument, scorer "unchanged S1 SEAL02 o1-metrics/v1 aggregate; literal per-codepoint NFD"), `best.pt`/`best.safetensors`, `checkpoint_meta.json`, `train_log.csv` (epoch-end seal04_dev val_cer), `checkpoints/step-*.pt`, `RUN_BINDING.json`, `CLAIM.json`.
- References: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared/{harvest_dev,harvest_test,seal04_dev,seal04_test}/part-*.parquet` with columns `image_png,width,gt_nfd,gt_nfc,label_ids,codec_version,script_class,split,severity,applied_ops,font,polarity,bg_type,accent_survival,reuse_index,line_id,source_dataset,source_doc_id,license` (ignore `license`).
- Scorer and model code: sealed packages `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/7e8a497f21527b90` (013) and `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/e808f6ffe1363bd0` (014); local copy of 7e8a at `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/` (see `vendor/train/{cer.py,eval_cer.py,model.py,ckpt_io.py}`, `vendor/codec/v2.1.json`). Import them read-only; do not edit sealed packages.
- Python: `/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python` (torch, pyarrow available). Account a0140.

## Analysis (CPU)
For each run, at the **selected checkpoint** (trainer best.pt = strict-improvement best of the 8 epoch-end seal04_dev evaluations; determine its step from checkpoint_meta/train_log and confirm by weight SHA which saved predictions belong to it — if none exactly matches, report that and stop, do not substitute), and also at each of the four CER steps for the trajectory table:
1. Reproduce the stored aggregate NFD-atom / NFC / accent-blind CER and exact-line rate per instrument from the predictions using the sealed scorer. Mismatch = fail loudly.
2. Breakdowns per instrument: by `source_dataset` (and the id prefix), `script_class`, line-length bucket, digits-only / letters / mixed, polytonic (Greek NFD breathing/perispomeni/subscript/grave), all-caps; each with lines, reference units, edits, CER, exact-line rate.
3. Error types: substitutions / insertions / deletions; top 50 character confusions (NFD atoms, with counts and examples by id); accent/diacritic-only errors vs base-letter errors.
4. Cross-model: per line correct/incorrect for each run; overlap table (wrong in all / some / one); lines wrong in all three listed by id (dev only list for decisions; test as descriptive counts).
5. Paired bootstrap between every pair of runs on **dev** (harvest_dev, seal04_dev, pooled dev = both): CER difference with 95 % CI, 10,000 resamples over lines, seed fixed and recorded.
Rule: anything that could drive a decision is computed on dev; test-set breakdowns are reported in a separate section labelled "report only". Nothing reads test numbers to choose a checkpoint, threshold or model.

## Speed benchmark
Load the selected weights per width through the sealed package's model code (exact width multiplier, codec, input height/normalisation as the trainer uses). Measure ms/line and lines/s on (a) CPU with 1 thread and with 8 threads, batch 1 and 32; (b) one GPU (bf16 and fp32 if the trainer supports it), batch 1, 32, 256. Use 2,000 lines from harvest_dev in a fixed order, warm-up excluded, median of 5 repeats; record hardware, torch version, threads. Also report parameter counts and safetensors sizes.

## Deliverables
- `scripts/release_v0/analyze_models.py`, `scripts/release_v0/bench_speed.py`, sbatch wrappers (`analyze.sbatch` CPU: partition/time/cpus as parameters, default preemptable 16 CPU 2 h, `--no-requeue`; `bench.sbatch`: 1 GPU, preemptable, 1 h), `scripts/release_v0/COMMANDS.md` (exact coordinator commands incl. deploy + sha comparison, the run list for now and for ×1 later, output dir under `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/analysis/<date>/`).
- Outputs per run: `analysis_<run>.json`, `REPORT.md` (tables: trajectory, breakdowns, confusions, overlap, bootstrap, speed), plus a combined `SUMMARY.json`.
- Tests: `tests/release_v0/test_analyze_models.py` with tiny fixtures (scorer reproduction, bootstrap determinism, breakdown sums equal totals, selected-checkpoint resolution failing loudly on mismatch). Run them locally; delete the pytest basetemp after passing.
- A one-line report at the end: result, files, tests, blockers.

If you find a documentation or provenance gap, add it to docs/programme_20261028/RELEASE_v0/GAPS.md (what / where / impact / fix); don't fix it here.
Write scope: `scripts/release_v0/`, `tests/release_v0/`, and appending to that GAPS.md only. No git operations.
