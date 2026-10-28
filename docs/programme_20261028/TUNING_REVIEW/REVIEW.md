# Tuning review — Greek OCR v0.6 (TRAIN_FULL_v1), 28 October 2026

This reviews how we tuned the three models (×1, ×1.5, ×2). It compares what we did with the Google
*Deep Learning Tuning Playbook* (PB), Karpathy's *A Recipe for Training Neural Networks*, and the
papers they rely on. It also asks what the `nn-tuning` skill told us and where that advice fell short.

- Sources: [refs/SOURCES.md](refs/SOURCES.md).
- Reading notes, with quotes and page numbers: [READING_NOTES_A](READING_NOTES_A_lr_stability.md) and
  [READING_NOTES_B](READING_NOTES_B_search_variance_batch.md).
- Raw curve extract used below: [data/w1_h13_vs_h14_loss.txt](data/w1_h13_vs_h14_loss.txt).
- Skill changes made after this review: [SKILL_CHANGES.md](SKILL_CHANGES.md).

## The short version

- **The method worked for two of three widths.** A 16-point search at 10 % length, then one full
  run, gave ×2 **1.011 %** and ×1.5 **1.037 %** pooled-dev CER. Both are clearly better than their best
  short trials (1.148 % and 1.252 %) and far better than the old recipe (control trials 1.325 % and
  1.922 % at 10 % length).
- **It failed for ×1,** and the cause is now well understood. We picked the ×1 winner (h13) at the
  **top edge of the learning-rate range**, out of a group of statistical ties. The short trial spent
  about 1,000 updates near peak LR; the full run, with the same schedule stretched 10×, spends about
  10,000. h13 blew up after about 2,100 updates near peak, and none of the cheap checks that would
  have caught this were run.
- **The skill's main gap.** It repeats the playbook's "keep the Round-1 LR and stretch the cosine"
  advice without saying that stretching also multiplies the time spent at peak LR. That is exactly
  where an LR chosen on short runs can stop being stable.
- **Smaller misses:**
  - seed reruns skipped, so ties were read as a ranking;
  - three hyperparameters tuned with 16 trials, where the playbook's tier is LR + β1;
  - a clipping threshold (5.0) that never fired;
  - weight decay not adjusted for the longer run;
  - a budget that ran 4.5× over its projection in Stage B because of preemption churn.

## 1. What we did

| Stage | What | Numbers | Record |
|---|---|---|---|
| A | Batch throughput sweep per width (64 → 1024), pick the largest batch with ≥5 % more lines/s | ×1 b256, ×1.5 b256, ×2 b64. Throughput almost flat (×1 395 → 426 lines/s); GPU only 35–64 % busy, so input/overhead bound | [STAGE_A.md](../../programme_20261025/TRAIN_FULL_v1/STAGE_A.md), ledger 26 Oct 00:49 |
| B | Per width: 16 scrambled-Halton points over peak LR (log), β1 (1−β1 log), weight decay (log) + 1 control; each trial 10 % of the final length; 1 seed; objective = pooled dev CER at the end | Best: ×1 h13 1.2686 %, ×1.5 h14 1.252 %, ×2 h04 1.1475 %. Analyzer flagged ×1/×1.5 best LR at the HIGH boundary and ×2 β1 at the LOW boundary | [search_study1/](../../programme_20261025/TRAIN_FULL_v1/search_study1/), [STAGE_B.md](../../programme_20261025/TRAIN_FULL_v1/STAGE_B.md) |
| B2 | Seed reruns of the best points | **Skipped** (owner, to save budget) | ledger 26 Oct 18:26 |
| C | One full run per width: same OneCycle shape (pct_start 0.075, cosine, no momentum cycling) stretched 10×, clip 5.0, best checkpoint = best of 8 epoch-end seal04_dev (437 lines) evaluations | ×2 1.011 %, ×1.5 1.037 %; ×1 h13 diverged, retired at 26 %, restarted with h14 | [STAGE_C.md](../../programme_20261025/TRAIN_FULL_v1/STAGE_C.md), ledger |
| Diagnosis | Frozen-model probes of the ×1 spike window | No bad batch; pre-spike gradient norm ≤ 1.21 (typical ≈ 0.1); after the spike, loss ≈ 4 on every batch | [spike_diag/READOUT_20261028.md](../../programme_20261025/TRAIN_FULL_v1/spike_diag/READOUT_20261028.md) |

The same 16 Halton points were used for every width. ×2 trials were 19,831 updates long (batch 64),
four times longer than ×1/×1.5 (4,958 updates, batch 256).

## 2. What went well

- **Order of decisions.** Batch first, then optimizer settings at that batch, then a fixed step
  budget with retrospective checkpoint selection. This is the playbook's dependency order (PB
  "Choosing the batch size", L358–374), and changing the batch reopened LR/β1/wd as it should.
- **Quasi-random search with a control.** Halton points on log scales (1−β1 on log scale, as
  Choi 2019 does) beat the old recipe by a wide margin at every width (×1: 1.27 % vs 2.54 %).
  The search space was wide enough: LR spanned 6.6e-5 to 4.9e-3, and no trial diverged.
- **Two-round shape.** Short trials, then long runs, is the playbook's compute-bound default
  (L1282–1285), and the long runs beat the short ones by 0.14–0.22 percentage points.
- **Test sets never chose anything.** Selection used seal04_dev only. harvest_test 0.53 %/0.56 % and
  seal04_test 1.65 %/1.76 % (×2/×1.5) are honest report-only numbers.
- **Fixed budget plus retrospective selection,** not early stopping (PB L1508–1527). This mattered:
  late in training dev CTC loss rose about 9 % from its minimum (×2 harvest_dev 0.0394 at 80 % →
  0.0431 at the end) while dev CER kept falling (1.044 → 1.011 %). Karpathy's "early stopping based on
  your measured validation loss" would have stopped too early here. PB defines problematic
  overfitting on validation *error*, not loss (L925).
- **The spike diagnosis.** Comparing the same batches across two runs, plus frozen-model probes,
  separated "bad data" from "optimizer divergence" cleanly. The literature has no ready-made recipe
  for this (notes A, Q3).
- **Requeues did not distort the curves.** The transient one-check jumps in ×1.5 (step 20,903) and
  ×2 (step 22,657) are not at restart points (restarts at 5,490 / 13,724 and 17,972 / 23,073), and
  resume was BIT_IDENTICAL in the smoke tests.

## 3. What went wrong, and why

### 3.1 ×1 h13 diverged in the full run (the main failure)

**What the curves show.** The h13 and h14 full runs drew identical batches, so the only difference is
the optimizer settings. Learning rates below come from the OneCycle formula with peak 4.92e-3 (h13)
and 1.56e-3 (h14).

| Step | LR h13 | h13 harvest_dev loss | LR h14 | h14 harvest_dev loss |
|---:|---:|---:|---:|---:|
| 782 | 6.9e-4 | 0.152 | 2.2e-4 | 0.360 |
| 1,759 | 2.4e-3 | **0.750** (bump) | 7.5e-4 | 0.256 (smaller bump, same batch) |
| 3,712 (peak) | 4.9e-3 | 0.112 | 1.6e-3 | 0.101 |
| 4,689 | 4.9e-3 | 0.096 | 1.6e-3 | **0.084** |
| 5,080 | 4.9e-3 | **4.010** (×44) | 1.55e-3 | (not reached yet) |
| 6,056–12,893 | 4.9 → 4.5e-3 | 0.10–0.86, repeated bumps, no net progress | — | — |

- **High LR learns faster early, then stalls.** h13 learns faster in the first ~1,000 updates, which
  is what a 10 %-length trial rewards. By the peak, h14 is already level, and after it h14 is ahead.
- **h13 never recovered.** After the spike it bounced for another 7,800 updates at ≥ 90 % of peak LR
  without improving. At 25 % its pooled dev CER was 1.70 %, against 1.31 % for ×1.5 and 1.23 % for ×2.

**Why a 10 % trial could not see it.**

| Schedule | Updates | Peak at | Updates at ≥ 90 % of peak LR |
|---|---:|---:|---:|
| Stage B ×1 trial | 4,958 | 371 | ≈ 1,017 |
| Full ×1 run | 49,584 | 3,718 | ≈ 10,173 |
| Stage B ×2 trial | 19,831 | 1,486 | ≈ 4,068 |
| Full ×2 run | 198,312 | 14,872 | ≈ 40,686 |

- **Exposure needed to diverge.** h13's full run diverged after about 2,150 updates at ≥ 90 % of
  peak, roughly twice the near-peak exposure of its whole short trial. The short trial ended at step
  4,958, before the step where the full run blew up.
- **The mechanism in the literature.** Under a high learning rate, the loss surface "sharpens"
  progressively until it crosses the stability limit (≈ 2/η for SGD; a preconditioned analogue for
  Adam). A model can therefore diverge "despite starting out in the 'stable' region" (Gilmer et al.
  2021, Fig. 3; Wortsman et al. 2023 §4). The more updates spent near peak, the more room for this.

**How we picked h13.**

| ×1 trial | Peak LR | β1 | wd | Pooled dev CER (10 % trial) |
|---|---:|---:|---:|---:|
| h13 | 4.92e-3 (top of the range) | 0.844 | 0.081 | 1.2686 % |
| h05 | 3.69e-3 | 0.926 | 0.004 | 1.2700 % |
| h14 | 1.56e-3 | 0.928 | 0.026 | 1.2803 % |
| h02 | 3.31e-3 | 0.895 | 0.001 | 1.2935 % |

- **Statistical ties.** The top four are within 0.025 points of each other, a 3× spread in LR, with one
  seed each. The playbook asks for N reruns of the best trial before adopting it (L1057–1110);
  Nado 2021 and Choi 2019 use 5 seeds. Without them, 0.011 points between h13 and h14 is a tie.
- **The edge point.** Among the ties we took the riskiest point: the one at the edge of the search
  range. Our own analyzer printed "near HIGH boundary: expand the range"; we neither expanded nor
  stepped back.
- **A known pattern.** Shallue 2018 (p. 25) warns that the fastest settings "are typically on the edge
  of the feasible region… small changes… might make training diverge". Gilmer 2021 (§6) notes that an
  optimal LR next to the divergence edge is a warning sign.

**What the playbook and the skill said.**
- **Round 2 rule.** PB Round 2 says "For cosine decay, just keep the base lr from Round 1 and extend
  max_train_steps". It is labelled *speculation* and carries no stability caveat. The skill copied
  it as its default.
- **Transfer warning ignored.** PB also says optimizer hyperparameters only "loosely" transfer from
  short to long runs, and "there is always a risk that our conclusions at this time limit will not
  apply to… 20%… let alone 100%". The skill states this too, but did not turn it into a check before
  the single long run.

**Cheap checks that would likely have caught it:**
1. **Treat ties as ties** and pick the interior point (h14 or h05), not the boundary one.
2. **Use the playbook's own early-instability probe:** about 500 steps at 2× the chosen LR,
   evaluating every step (PB L1838–1840). Better still for a stretched schedule: run the
   candidate's long schedule through its high-LR plateau (the first ~25–30 % of the long run),
   or rerun the top 2–3 trials at 20–30 % length.
3. **Hedge with two long runs:** the playbook says "very few long runs on good hyperparameter
   points" (plural). We ran exactly one per width.

### 3.2 Three hyperparameters with 16 trials

- **The playbook's tier.** The Adam FAQ says "If 10–25 trials, tune learning rate and β1" (L1645–1661);
  weight decay is not in that tier.
- **What we did.** We tuned LR, β1 and wd with 16 points, reused the same 16 points at every width,
  and fixed ε and β2. Choi 2019 says "the onus is on empirical studies that fix ε = 10⁻⁸ to defend
  that choice".
- **Impact.** The result is still a clear win over the control. The cost is that each best point is
  less well pinned down, which feeds 3.1.

### 3.3 Weight decay tuned at 10 % length

Loshchilov & Hutter (AdamW, App. B.1) show that the optimal weight decay shrinks as training gets
longer. Their normalised rule is λ ∝ √(1/T), which would make a value tuned at 10 % length about
3.2× too large at full length. PyTorch's AdamW also couples decay to LR (θ ← θ − η·λ·θ). We did not
test this, so it is a **hypothesis**, not a cause. Worth one ablation next time.

### 3.4 Warmup changed silently

The playbook treats warmup as a number of *steps* and says it transfers well from short to long runs.
OneCycle's `pct_start = 0.075` is a fraction of training, so stretching the run turned 372 warmup
steps into 3,719. Longer warmup is usually safer (Gilmer §5; Wortsman Fig. 5), so this probably did
not hurt. It was a change we did not decide on, and it changed the "very likely to transfer" setting.

### 3.5 Clipping that never fired

- **The playbook rule:** "Choose a gradient clipping threshold based on the 90th percentile of
  gradient norms… ideal clip thresholds are just above the 'typical' gradient norm."
- **What we had.** We inherited 5.0, while typical norms are ≈ 0.1 and the largest pre-spike norm was
  1.21, so clipping never fired. The trainer also discards the norm returned by `clip_grad_norm_`, so
  per-step norms were never logged.
- **Would it have helped?** Uncertain. Under Adam, clipping the gradient changes the update less than
  under SGD, and no source claims clipping reliably prevents curvature-driven divergence. Still, a
  calibrated clip plus a logged norm is cheap and would have shown the 12× outlier before step 5,080.

### 3.6 Budget: Stage B cost 4.5× its projection

- **The overrun.** Stage B was projected at 56.6 GPU-h and cost **255.1 GPU-h**. The campaign reached
  437.6 requested GPU-h against a 350 cap.
- **Causes:**
  - preemption churn, with up to 7 restarts per job;
  - a deadline-warning signal that killed lanes instead of yielding (fixed for Stage C);
  - accounting that missed requeue duplicates until `sacct -D` was used.
- **The sources are silent.** None of them covers preemption cost; they count trials as feasible
  completed trials. This is a gap in the skill, not a misreading of it.

### 3.7 Batch size: right order, little gain

- **The rule we used.** Batch was picked by throughput (≥ 5 % gain), which the playbook allows as a
  gate. The playbook's real criterion for minimum training time is "the largest batch size that still
  provides a reduction in the number of training steps required" (L283–285), and that side was never
  checked.
- **Little gain.** Throughput was almost flat (×1: 395 → 426 lines/s, GPU 35–64 % busy). The larger
  batch bought about 8 % speed and forced a full re-tune.
- **Width and batch confounded.** The ×2 search ran at batch 64 and 4× more updates, and its best LR
  came out 4–13× lower (3.7e-4, against 1.6e-3 to 4.9e-3 for the ×1 front-runners). That fits "longer horizons need lower peak LR", but we cannot
  separate width, batch and horizon in this design.

### 3.8 Selecting on a 437-line dev set

- **Selection optimism.** Best-of-8 on 437 lines is optimistic: Bergstra 2012 (p. 302) notes that with
  a small validation set, model-selection uncertainty can exceed test-measurement uncertainty.
  Karpathy says "add significant digits to your eval". Both final checkpoints were the last epoch, as
  expected with a schedule that anneals to ~0, so selection did little harm here.
- **Rare test points.** Test points are rare: CER at 4 checkpoints, and 8 epoch-end selection
  evaluations. They are too coarse to catch instability. The 50k-line loss checks are what showed the
  ×1 spike.

## 4. Did the short-run ranking predict the full-run outcome?

We ran one long run per width, so the ranking can only be tested on ×1.

| Width | Short-run rank of the run we trained | Short CER | Full-run CER | Note |
|---|---|---:|---:|---|
| ×2 | 1st (h04) | 1.148 % | **1.011 %** | Fine |
| ×1.5 | 1st (h14) | 1.252 % | **1.037 %** | Fine |
| ×1 | 1st (h13) | 1.269 % | diverged (1.70 % at 25 %) | Retired |
| ×1 | 3rd (h14) | 1.280 % | running, stable through the peak (harvest_dev 0.084 at step 4,689) | Replacement |

**h14 shows up twice.** The ×1.5 winner is the same Halton point (lr 1.56e-3, β1 0.928, wd 0.026) that
replaced h13 for ×1. It has now been stable at two widths, which weakly supports picking robust
interior points.

## 5. What the sources recommend that we did not do

| Recommendation | Source | Status |
|---|---|---|
| Rerun the best trial N times; adopt only beyond retrain variance | PB L1057–1110; Nado (5 seeds); Choi (5 reruns) | Skipped |
| Expand the space when the best is at a boundary | PB L800–842; skill `tuning_loop.md` §6 | Flagged, not done |
| Check LRs just above lr*; ~500 steps at 2× LR, evaluate every step | PB L1823–1840 | Not done |
| Clip at the 90th-percentile gradient norm; log the unclipped norm every step | PB "Gradient clipping" | Not done |
| 10–25 trials → tune LR + β1 only | PB Adam FAQ | We tuned 3 |
| Round 2 = "very few long runs" (plural) on good points | PB L1282–1285 | One run per width |
| Refined space + final Bayesian study before exploitation | PB L1111–1147 | Not done (budget) |
| Scale weight decay with run length | Loshchilov & Hutter App. B.1 | Not done |
| Measure LR sensitivity at small scale; longer warmup lowers it | Wortsman 2023 §2.2, §3.2 | Not done |
| Use the largest eval set you can for selection | Karpathy; PB L1474–1506 | 437 lines |

## 6. Changes for next time (checklist)

1. **Before committing to one long run from a short study:**
   - Seed-rerun the top 2–3 trials (or at least the top 2).
   - Treat differences smaller than the seed spread as ties.
   - Break ties toward the more stable point: lower LR, away from boundaries and from any infeasible
     region.
2. **If the best LR sits at the top of the range,** either expand the range or do not adopt that point.
   "No trial diverged at 10 %" is not evidence of stability at 100 %.
3. **Stretch-safety check:** before the long run, run the chosen point's long schedule through its
   high-LR plateau (≈ the first quarter), or the playbook's 2×-LR probe. Count the updates spent at
   ≥ 90 % of peak in the short trial and in the long run. If the long run spends several times more,
   the short trial says nothing about that stretch.
4. **Decide warmup in steps,** deliberately, when stretching. With OneCycle, `pct_start` silently
   rescales it.
5. **Calibrate clipping** from logged gradient norms (90th percentile), and log the unclipped norm
   every step. Also consider logging the update-to-weight ratio.
6. **Run k ≥ 2 long runs per width** if they can be afforded (top two distinct points), or at least
   prepare the runner-up so the switch is immediate. Switching to h14 needed a new package, two Astra review cycles and about 16 h in the queue.
7. **Tune at most LR + β1 with ≤ 25 trials,** or raise the trial count. Consider rescaling weight decay
   for run length, and test it once.
8. **Budget preemptable studies with a churn multiplier** measured from earlier restarts. Count
   requested GPU-h with requeue duplicates (`sacct -D`) from day one.
9. **Select on the metric (CER), not loss,** with retrospective selection. Never early-stop on dev
   loss for this task. Use the largest dev set the eval budget allows.

## 7. Open questions to discuss

- Should the next generation's short study use **20–30 % length** instead of 10 %? That is about 2–3×
  the cost per trial, and it would expose ~2,000–3,000 near-peak updates.
- Is it worth one **weight-decay rescaling ablation** (√(1/T)) at ×1?
- Should we switch from OneCycle to **warmup + constant + linear decay**? With that schedule the
  playbook's Round-2 advice (keep the decay length, extend the constant phase) maps cleanly, and the
  time at peak is an explicit, chosen number instead of a side effect of `pct_start`.
- For the **dev set**, can we pool harvest_dev (16,350 lines) into checkpoint selection, as Stage B's
  objective already did? This needs care, because harvest_dev also drove Stage B choices.
