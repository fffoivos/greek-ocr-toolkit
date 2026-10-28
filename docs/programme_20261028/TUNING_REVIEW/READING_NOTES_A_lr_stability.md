# Reading notes A — LR transfer, warmup, instability, clipping (subagent report, 28 Oct 2026)

Sources: refs/txt/{smith2017,smith2018,goyal2017,gilmer2021,wortsman2023,wu2018,loshchilov2017,hoffer2017} and the playbook (PB). Page numbers = PDF page breaks. [Inference] = reader's own reasoning, not the sources'.

## Q1 Short→long LR transfer
- PB compute-bound: "there is always a risk that our conclusions at this time limit [~10%] will not apply to experiments at 20% of the production length, let alone 100%." Round 1: "no guarantee that good hyperparameters found in short, incomplete training are still good choices when training length is significantly increased"; optimizer HPs "loosely" transfer; LR schedule "unlikely to transfer perfectly"; warmup/init "very likely".
- PB Round 2 (speculative): "Use the extra steps to extend the period of training at a high learning rate… For cosine decay, just keep the base lr from Round 1 and extend max_train_steps" — exactly what we did; no stability caveat.
- Wu 2018 p1: short horizons bias toward small step sizes; Fig. 2 p2: when followed by decay, curves "favor higher learning rates".
- Smith 2017 §3 p3: LR range test results independent of 5k/20k/100k iterations. Smith 2018 §3 p4: well-set HPs perform well throughout.
- Loshchilov §1 p2: optimal weight decay shrinks with longer runs; App B.1: normalized λ = λ_norm·√(b/(BT)) makes short-run optima transfer.
- [Inference] Our short trials were fully annealed, so Wu's small-LR bias mostly doesn't apply; the failure was instability at high LR held long. Under √ scaling wd tuned at 10 % length would be ~3.2× too big at full length.

## Q2 Fixed-fraction warmup, stretched horizon
- PB warmup: sized in steps, sweep orders of magnitude, largest feasible ≤10 % of max_train_steps; >5 % → lengthen training. Warmup "very likely to transfer".
- Gilmer Fig. 3 p6: "progressive sharpening until the curvature fluctuates around the bound 2/η"; panel D: a model "diverging despite starting out in the 'stable' region". Wortsman §4 p10: same mechanism.
- No source frames *time at peak* as a risk; PB Round 2 and Hoffer recommend more time at high LR.
- [Inference] Stretching made warmup 10× gentler but the time at ≥90 % peak 10× longer (≈10k vs ≈1k updates) — time for progressive sharpening; a short run that decays right after peak can't reveal it.

## Q3 Divergence diagnostics
- Gilmer §4 p4: training succeeds only when λ1 ≤ 2/η; divergent models leave that region before diverging (Lanczos). §7: Adam analogue unclear. Wortsman §4 p10: Adam preconditioned sharpness ≈ 38/LR (β1 0.9); large β2 → fast spikes; lowering β2 helps.
- Wortsman §3.1: attention-logit growth / output-logit divergence (slow divergence, mostly late).
- PB: plot train loss for LRs just above lr*; log full-gradient L2 norm every step; ~500 steps at 2× lr evaluating every step; Fig. 7b rerun at 5–10× LR looking for a sudden rise.
- Wortsman §2.2: LR sensitivity metric = deviation of final val loss from optimum across 3 orders of magnitude of LR.
- Gilmer §6: optimal LR always next to the largest non-divergent LR → curvature is the limit (warning sign).
- No paper gives a bad-data vs optimizer rule. [Inference] Our probe pattern (no culprit batch, uniform degradation, gradient outlier) = optimizer/parameter-space divergence.

## Q4 Clipping
- PB: "The ideal clip thresholds are just above the 'typical' gradient norm"; "Choose a gradient clipping threshold based on the 90th percentile of gradient norms… 90% is a good starting point"; >50 % clipped = "extremely aggressive… might as well reduce the learning rate"; "Sometimes longer warmup periods can correct instabilities that clipping does not."
- Gilmer fn 3 p7: clipping reduces step size in high-curvature regions. No source says clipping reliably prevents curvature divergence under Adam; Wortsman clips at 1 and still sees instabilities.
- [Inference] 5.0 vs typical 0.1 ≈ 50× → effectively off. Under Adam, gradient clipping is partly normalised away by m/√v.

## Q5 Mitigations
- Lower LR: PB "last resort" (framed as unlocking higher LR). No numeric safety margin prescribed anywhere.
- Longer warmup: PB, Gilmer §5 (warmup pushes params to lower λ1), Wortsman Fig. 5 (longer warmup reduces LR sensitivity; total steps fixed).
- z-loss (Wortsman §3.1.2, coeff 1e-4); qk-layernorm (attention only); normalisation inside residual (PB).
- AdamW ε (Wortsman §3.4) — [Inference] not binding here.
- Independent (decoupled) weight decay reduces LR sensitivity (Wortsman §3.2.2); PyTorch AdamW default is coupled to LR.
- Lower β2 resolves fast spikes (Wortsman p11); decreasing momentum while LR rises stabilises (Smith 2018 §4.3) — we had cycle_momentum off; [Inference] higher β1 changes Adam's stability threshold.
- Wortsman abstract: instabilities appear in small models at high LR and the same mitigations work → small-scale LR-sensitivity sweeps are informative.

## Q6 Wu 2018
- Noisy ill-conditioned quadratic: greedy schedules decay LR too fast; stochasticity required; deterministic lookahead picked too-large LR → instability (§3.3). MNIST: decay exponent differs >100× between 100- and 20k-step horizons. "any meta-objective which does not correct for short-horizon bias will probably fail when run for a much longer time horizon" (p2).
- [Inference] Annealed short trials remove most of the greedy bias; schedule shape still doesn't transfer; Wu says nothing about stability under stretching.

## Q7 Dev loss up, error down
- No source addresses it directly. PB: problematic overfitting = validation *error* rising; best-over-training validation objective; retrospective checkpoint selection. Smith 2018 Fig. 13: accuracy easier to interpret than loss.

## Q8 Other
- PB: never tune max_train_steps inside a study; multiple rounds with increasing step limits, double-checking conclusions; Round i→i+1's biggest question is LR decay; run the best trial N times for trial variance; "Selecting the best trial… might favor 'bad' values"; Adam budget: 10–25 trials → LR and β1 only.
- [Inference] proposals: stretched-schedule stability check before the one long run; derate peak LR unless LR sensitivity is flat; 90th-percentile clipping; log grad norm and update/param ratio every step; automatic rollback on loss jumps.
