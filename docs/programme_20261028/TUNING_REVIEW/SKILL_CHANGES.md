# nn-tuning skill — changes after the v0.6 tuning review, 28 October 2026

- **Backup of the previous version:** `~/.claude/skills/nn-tuning.bak-20261028/`. It is an exact copy
  and shows up in the skill list as "nn-tuning.bak-20261028".
- **Edited in place:** `~/.claude/skills/nn-tuning/`. `diff -r` between the two folders shows every
  change.
- **What each change rests on:** a source (with its location; quotes are in the reading notes),
  campaign evidence from [REVIEW.md](REVIEW.md), or both. Inferences are labelled as such in the
  skill text. No new hard thresholds were invented; the one number added (≈25–30 % plateau for the
  stability probe) is offered as a default.

| # | File / section | Change | Why | Source |
|---|---|---|---|---|
| 1 | `SKILL.md` "Expensive models" | After the playbook's Round-2 rule ("keep the base LR, stretch the cosine"), added: it is speculation and has no stability caveat; stretching multiplies near-peak updates; a short trial that never diverged proves nothing about the long run's high-LR stretch | The ×1 argmax diverged after ~2,150 near-peak updates, against ~1,017 in its whole trial | PB Round 2 (marked "Speculation"); Gilmer 2021 Fig. 3; Wortsman 2023 §4; REVIEW §3.1 |
| 2 | `SKILL.md` "Expensive models" | New 6-step pre-commit list: ties are ties (seed-rerun the top 2–3, break ties toward stability); don't adopt a boundary winner; stretch-safety check; decide warmup in steps; rescale weight decay; hedge with ≥2 long runs or a packaged runner-up | Each step would have prevented or shortened the ×1 failure | PB L1057–1110 (retrain variance), L800–842 (boundary), L1838–1840 (2× LR probe), L1282–1285 ("very few long runs"); Loshchilov App. B.1; REVIEW §3.1, §3.3, §3.4 |
| 3 | `SKILL.md` Adam budget table | 10–25 trials row notes that weight decay is a third HP and belongs above 25 trials | We tuned LR + β1 + wd with 16 trials | PB Adam FAQ L1645–1661; REVIEW §3.2 |
| 4 | `SKILL.md` "sources disagree" table, Stopping row | Select on the task metric, not the loss; problematic overfitting is defined on error; val-loss early stopping would have stopped the OCR runs too early | Dev CTC loss rose ~9 % late while CER fell to the last checkpoint | PB L925, L1508–1527; Karpathy "early stopping"; REVIEW §2 |
| 5 | `references/training_length.md` Compute-bound | New block "Stretching has a cost the playbook doesn't mention: time at peak LR", with near-peak-update arithmetic and a 6-item checklist (exposure ratio, pick for robustness, stability probe, warmup in steps, weight-decay rescale, ≥2 long runs + automatic rollback) | Same as 1–2, with detail | PB Round 1/2; Shallue 2018 p. 25; Gilmer §5–6; Wortsman Fig. 5; Loshchilov App. B.1; REVIEW §3.1, §6 |
| 6 | `references/training_length.md` | Paragraph reconciling Wu 2018 (short horizons favour *small* LR) with our case (fully annealed short trials favoured the *highest* LR): both mean short-trial LR rankings are not long-run rankings | The skill cited Wu's direction only, which could mislead in the opposite case | Wu 2018 abstract and Fig. 2; READING_NOTES_A Q1/Q6; REVIEW §3.1 |
| 7 | `references/training_length.md` | New "Selecting the checkpoint" section: select on the metric retrospectively; loss↑ with error↓ is not overfitting; best-at-end is expected with an annealed schedule; use the largest selection set affordable | 437-line selection set; loss-vs-CER divergence | PB L925, L1196–1207, L1474–1506; Karpathy "add significant digits to your eval"; Bergstra 2012 p. 302; REVIEW §3.8 |
| 8 | `references/stability.md` | New section "Mid-training divergence under a high LR": the progressive-sharpening mechanism; fast vs slow spikes (lower β2 for fast spikes); a practical bad-data vs optimizer test (same batches across runs + frozen-checkpoint probes); the LR-sensitivity probe; other mitigations (LR-independent wd, z-loss, qk-layernorm, momentum decrease during ramp) | The skill had no mechanism or diagnosis for mid-run divergence beyond "log the gradient norm" | Gilmer 2021 Fig. 3, §5–7; Wortsman 2023 abstract, §2.2, §3.2, §4; Smith 2018 §4.3; spike-diag readout; REVIEW §2, §3.1 |
| 9 | `references/stability.md` clipping | Calibrate before the long run (an inherited threshold that never fires is off); log the unclipped norm every step; under Adam clipping is weaker than under SGD and no source says it prevents curvature divergence | Clip 5.0 vs typical norm ≈ 0.1; norms never logged | PB "Gradient clipping" (90th percentile); Gilmer fn. 3; Wortsman §2.1; REVIEW §3.5 |
| 10 | `references/tuning_loop.md` §6.1 | Boundary rule: if a rerun with an expanded space is unaffordable, don't adopt the boundary point; "no trial diverged" only holds at that length | We adopted the LR-boundary argmax despite the analyzer's flag | PB L800–842; REVIEW §3.1 |
| 11 | `references/tuning_loop.md` §8 | Retrain variance: the papers use 5 seeds; new paragraph "Choosing one point for an expensive run" (seed-rerun the top 2–3, ties → stability, Bergstra's probability-weighted reporting, record skipped seeds on the study card) | Top four ×1 trials within 0.025 points, one seed each | PB L1057–1110; Nado 2021; Choi 2019 App. C; Bergstra 2012 §2.1; REVIEW §3.1 |
| 12 | `references/tuning_loop.md` §5 | New "Compute budget on preemptable hardware": count requeued segments (`sacct -D`); forecast with a measured churn multiplier; rehearse the deadline/preemption signal path | Stage B cost 255 GPU-h against 56.6 projected; spend was undercounted until `sacct -D` | No source covers preemption (gap in the literature); Bergstra 2012 p. 302 (trials must survive interruption); REVIEW §3.6 |
| 13 | `references/initial_config.md` §3.3 | Batch: if throughput is nearly flat, a larger batch buys little speed but forces a full re-tune; profile first, as step 3 already said | ×1 went 395 → 426 lines/s for 4× the batch; GPU 35–64 % busy | PB L245–251, L283–285, L358–374; REVIEW §3.7 |
| 14 | `references/evidence.md` | Added entries for Smith 2017/2018, Goyal 2017, Gilmer 2021, Wortsman 2023, Loshchilov & Hutter, Zhang 2019, Nado 2021, plus a "Campaign evidence" entry with the OCR numbers and their limits (one run per width, no seeds) | The new rules cite these | Full texts in `refs/`; reading notes A and B |
| 15 | `scripts/analyze_study.py` | The boundary message now adds: "if you cannot [expand], do not adopt this point, take the best interior one" | The old message only said "expand", which was skipped under budget pressure | Same as 10 |

## Not changed, deliberately

- **No numeric LR derating factor** (such as "×0.7"). No source prescribes a margin.
- **No switch to a different schedule family** (warmup + constant + linear decay). It is an open
  question in REVIEW §7, not an evidence-backed rule.
- **No minimum seed count beyond "2–3 top points".** The playbook leaves N open, and the papers'
  5 is a practice, not a requirement.
- **Karpathy's steps and the playbook's phase order are unchanged.** The review found that the
  order was followed; the failures were in steps the skill already named (seeds, boundary) or in
  stretching, which it did not cover.

## Source availability

- **Karpathy's backprop post (Medium):** blocked by a bot check.
- **Recht's argmin post:** now a "Page not found" page.

Both are summarised in the existing `evidence.md` and the playbook footnote; see
[refs/SOURCES.md](refs/SOURCES.md).
