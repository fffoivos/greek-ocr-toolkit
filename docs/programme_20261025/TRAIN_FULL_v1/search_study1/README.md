# Stage B search — study 1 (optimizer, per model width)

Quasi-random search over AdamW settings, run separately for each of the three model widths
(×1, ×1.5, ×2) before the full-length training runs. Plan and rationale:
[../STAGE_B.md](../STAGE_B.md). Execution log: [../EXECUTION_STATE.md](../EXECUTION_STATE.md).
Sealed code: [../package/](../package/) (payload `3c9e5d5f4fb8702e`).

**Status:** 2026-10-26 18:16 EET — study complete (51/51), collected. Single seed per trial.

## Algorithm

- **Sampler:** randomly shifted, scrambled Halton sequence (Bousquet et al. 2017), study seed
  **20261025**, 16 points: [package/study/quasi_random.py](../package/study/quasi_random.py).
- **Space** ([package/study/lr_space.json](../package/study/lr_space.json)):

  | Hyperparameter | Range | Scale |
  |---|---|---|
  | peak learning rate (AdamW, OneCycle) | 5e-5 … 5e-3 | log |
  | β1 | 0.80 … 0.98 | one-minus-log |
  | weight decay | 1e-3 … 0.3 | log |

- **Points:** [package/study/lr_trials.jsonl](../package/study/lr_trials.jsonl) (h00–h15). The
  **same 16 points** run at every width, with no batch scaling of the learning rate.
- **Control:** the inherited S1 recipe, lr 1e-4, β1 0.9, wd 0.05.
- **Fixed:** batch per width from Stage A (×1 256, ×1.5 256, ×2 64); β2 0.999; eps 1e-8; clip 5;
  OneCycle pct_start 0.075; 50% synthetic lines; model seed 0; data seed 20261015.
  Full list: [package/study/card.json](../package/study/card.json).
- **Length:** 1,269,164 drawn lines per trial = 10% of the full run (4,958 updates at batch 256,
  19,831 at batch 64).
- **Measured:** CTC loss on both dev sets (harvest_dev 16,350 lines, seal04_dev 437 lines) every
  50,000 drawn lines (26 checks); at the end, full dev scoring. **Objective:** pooled NFD-atom CER
  over both dev sets (sum of edits / sum of reference units). Test sets are never loaded.
- **Analysis:** [package/study/analyze_study.py](../package/study/analyze_study.py) (infeasible
  fraction, boundary, density, isolation table) once all trials are done.

## Files here

| File | Content |
|---|---|
| `summary.csv` | one row per trial: settings, status, last dev losses, final CER/WER/exact-line rate per dev set, pooled CER |
| `curves.csv` | dev CTC loss at every 50k-line check, per trial |
| `trials/*.json` | exact config of each trial as run |
| `runs/<trial>/` | `loss_eval.jsonl`, `train_log.csv`, `eval/step-*.json` (final scores), `COMPLETE.json` |
| `PLAN.json` | the sealed study plan (13 node groups, hashes of every binding) |
| `submit-controls/` | submission intents/receipts, retries and node-job logs |
| `sync_from_clariden.sh`, `summarize.py` | refresh these copies and rebuild the CSVs |

Not copied (on Clariden, under
`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-009-stage-b-h1/study/runs/<trial>/`):
checkpoints (`best.pt`, `last.pt`, `checkpoints/`) and per-line predictions
(`eval/*.predictions.jsonl`, about 2.7 MB per trial).

## Results (final; pooled dev CER at end of each 10%-length trial, single seed)

All 51 trials complete, 0 infeasible. Isolation check PASS after reconciling 26 killed-lane allocations with measured Slurm step ends (`analysis/RECONCILIATION_COLLECT.json`, `analysis/ISOLATION.json`). Analyzer output per width: `analysis/ANALYSIS-w*.txt`; collector results: `analysis/results-w*.jsonl`.

Analyzer boundary flags: ×1 and ×1.5 best learning rates sit near the HIGH edge of the range (5e-3); ×2 (batch 64) best β1 sits near the LOW edge (0.80). Extending a range would be a new study.

**×1**

| Rank | Trial | lr | β1 | wd | Pooled dev CER | harvest_dev CER | seal04_dev CER | last harvest_dev loss |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | w1-h13 | 4.92e-03 | 0.844 | 8.09e-02 | 1.269% | 1.215% | 4.297% | 0.0657 |
| 2 | w1-h05 | 3.69e-03 | 0.926 | 3.87e-03 | 1.270% | 1.214% | 4.382% | 0.0663 |
| 3 | w1-h14 | 1.56e-03 | 0.928 | 2.59e-02 | 1.280% | 1.221% | 4.592% | 0.0630 |
| 4 | w1-h02 | 3.31e-03 | 0.895 | 1.24e-03 | 1.293% | 1.234% | 4.606% | 0.0632 |
| 5 | w1-h06 | 1.17e-03 | 0.942 | 2.40e-02 | 1.336% | 1.279% | 4.550% | 0.0676 |
| 6 | w1-h00 | 1.05e-03 | 0.951 | 4.87e-03 | 1.348% | 1.291% | 4.543% | 0.0691 |
| 7 | w1-h10 | 2.08e-03 | 0.979 | 7.68e-03 | 1.386% | 1.324% | 4.859% | 0.0718 |
| 8 | w1-h08 | 6.57e-04 | 0.876 | 2.35e-01 | 1.395% | 1.333% | 4.901% | 0.0727 |
| 9 | w1-h12 | 4.92e-04 | 0.966 | 2.53e-01 | 1.477% | 1.409% | 5.295% | 0.0762 |
| 10 | w1-h04 | 3.69e-04 | 0.840 | 3.79e-02 | 1.536% | 1.469% | 5.274% | 0.0821 |
| 11 | w1-h03 | 3.31e-04 | 0.965 | 1.19e-01 | 1.593% | 1.522% | 5.589% | 0.0830 |
| 12 | w1-h11 | 2.08e-04 | 0.904 | 8.26e-03 | 1.815% | 1.734% | 6.348% | 0.0954 |
| 13 | w1-h15 | 1.56e-04 | 0.944 | 2.64e-03 | 2.058% | 1.970% | 6.994% | 0.1077 |
| 14 | w1-h07 | 1.17e-04 | 0.973 | 2.46e-03 | 2.422% | 2.324% | 7.949% | 0.1217 |
| 15 | w1-control | 1.00e-04 | 0.900 | 5.00e-02 | 2.543% | 2.440% | 8.328% | 0.1269 |
| 16 | w1-h01 | 1.05e-04 | 0.977 | 1.21e-02 | 2.690% | 2.580% | 8.897% | 0.1332 |
| 17 | w1-h09 | 6.57e-05 | 0.955 | 7.52e-02 | 3.484% | 3.349% | 11.010% | 0.1694 |

**×1.5**

| Rank | Trial | lr | β1 | wd | Pooled dev CER | harvest_dev CER | seal04_dev CER | last harvest_dev loss |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | w1.5-h14 | 1.56e-03 | 0.928 | 2.59e-02 | 1.252% | 1.198% | 4.276% | 0.0618 |
| 2 | w1.5-h06 | 1.17e-03 | 0.942 | 2.40e-02 | 1.259% | 1.207% | 4.171% | 0.0587 |
| 3 | w1.5-h05 | 3.69e-03 | 0.926 | 3.87e-03 | 1.279% | 1.219% | 4.642% | 0.0666 |
| 4 | w1.5-h02 | 3.31e-03 | 0.895 | 1.24e-03 | 1.291% | 1.231% | 4.677% | 0.0683 |
| 5 | w1.5-h13 | 4.92e-03 | 0.844 | 8.09e-02 | 1.291% | 1.234% | 4.529% | 0.0671 |
| 6 | w1.5-h00 | 1.05e-03 | 0.951 | 4.87e-03 | 1.292% | 1.237% | 4.375% | 0.0625 |
| 7 | w1.5-h10 | 2.08e-03 | 0.979 | 7.68e-03 | 1.314% | 1.251% | 4.845% | 0.0686 |
| 8 | w1.5-h12 | 4.92e-04 | 0.966 | 2.53e-01 | 1.330% | 1.272% | 4.578% | 0.0682 |
| 9 | w1.5-h08 | 6.57e-04 | 0.876 | 2.35e-01 | 1.339% | 1.284% | 4.438% | 0.0671 |
| 10 | w1.5-h03 | 3.31e-04 | 0.965 | 1.19e-01 | 1.378% | 1.317% | 4.789% | 0.0701 |
| 11 | w1.5-h04 | 3.69e-04 | 0.840 | 3.79e-02 | 1.400% | 1.341% | 4.747% | 0.0702 |
| 12 | w1.5-h11 | 2.08e-04 | 0.904 | 8.26e-03 | 1.539% | 1.473% | 5.210% | 0.0799 |
| 13 | w1.5-h15 | 1.56e-04 | 0.944 | 2.64e-03 | 1.659% | 1.587% | 5.702% | 0.0864 |
| 14 | w1.5-h07 | 1.17e-04 | 0.973 | 2.46e-03 | 1.814% | 1.737% | 6.123% | 0.0939 |
| 15 | w1.5-h01 | 1.05e-04 | 0.977 | 1.21e-02 | 1.901% | 1.820% | 6.411% | 0.0965 |
| 16 | w1.5-control | 1.00e-04 | 0.900 | 5.00e-02 | 1.922% | 1.839% | 6.552% | 0.0982 |
| 17 | w1.5-h09 | 6.57e-05 | 0.955 | 7.52e-02 | 2.348% | 2.253% | 7.696% | 0.1174 |

**×2**

| Rank | Trial | lr | β1 | wd | Pooled dev CER | harvest_dev CER | seal04_dev CER | last harvest_dev loss |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | w2-h04 | 3.69e-04 | 0.840 | 3.79e-02 | 1.148% | 1.098% | 3.925% | 0.0514 |
| 2 | w2-h08 | 6.57e-04 | 0.876 | 2.35e-01 | 1.159% | 1.111% | 3.827% | 0.0532 |
| 3 | w2-h12 | 4.92e-04 | 0.966 | 2.53e-01 | 1.168% | 1.121% | 3.806% | 0.0542 |
| 4 | w2-h03 | 3.31e-04 | 0.965 | 1.19e-01 | 1.200% | 1.152% | 3.918% | 0.0541 |
| 5 | w2-h11 | 2.08e-04 | 0.904 | 8.26e-03 | 1.208% | 1.159% | 3.939% | 0.0604 |
| 6 | w2-h06 | 1.17e-03 | 0.942 | 2.40e-02 | 1.216% | 1.164% | 4.122% | 0.0590 |
| 7 | w2-h00 | 1.05e-03 | 0.951 | 4.87e-03 | 1.233% | 1.180% | 4.206% | 0.0575 |
| 8 | w2-h14 | 1.56e-03 | 0.928 | 2.59e-02 | 1.233% | 1.179% | 4.283% | 0.0615 |
| 9 | w2-h15 | 1.56e-04 | 0.944 | 2.64e-03 | 1.249% | 1.196% | 4.213% | 0.0628 |
| 10 | w2-h10 | 2.08e-03 | 0.979 | 7.68e-03 | 1.269% | 1.213% | 4.431% | 0.0645 |
| 11 | w2-h07 | 1.17e-04 | 0.973 | 2.46e-03 | 1.304% | 1.253% | 4.192% | 0.0658 |
| 12 | w2-h13 | 4.92e-03 | 0.844 | 8.09e-02 | 1.307% | 1.250% | 4.494% | 0.0688 |
| 13 | w2-control | 1.00e-04 | 0.900 | 5.00e-02 | 1.325% | 1.270% | 4.382% | 0.0692 |
| 14 | w2-h01 | 1.05e-04 | 0.977 | 1.21e-02 | 1.327% | 1.272% | 4.389% | 0.0671 |
| 15 | w2-h05 | 3.69e-03 | 0.926 | 3.87e-03 | 1.372% | 1.307% | 5.007% | 0.0765 |
| 16 | w2-h02 | 3.31e-03 | 0.895 | 1.24e-03 | 1.398% | 1.330% | 5.196% | 0.0771 |
| 17 | w2-h09 | 6.57e-05 | 0.955 | 7.52e-02 | 1.430% | 1.371% | 4.733% | 0.0735 |
