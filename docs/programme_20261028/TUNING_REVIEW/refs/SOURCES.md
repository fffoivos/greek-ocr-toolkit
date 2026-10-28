# Sources for the tuning review (downloaded 2026-10-28, Europe/Athens)

Text extractions of every PDF/HTML are in `txt/` (pdftotext -layout).

## The two primary sources
| File | URL | What it is |
|---|---|---|
| tuning_playbook_README.md | https://raw.githubusercontent.com/google-research/tuning_playbook/main/README.md | Godbole, Dahl, Gilmer, Shallue, Nado — *Deep Learning Tuning Playbook* (Google Research, 2023), full text |
| karpathy_recipe_2019.html | https://karpathy.github.io/2019/04/25/recipe/ | Karpathy — *A Recipe for Training Neural Networks* (2019) |

## References cited by the playbook
| File | URL | What it is |
|---|---|---|
| shallue2018_1811.03600.pdf | https://arxiv.org/abs/1811.03600 | Shallue et al. 2018 — Measuring the effects of data parallelism on NN training (batch size) |
| choi2019_1910.05446.pdf | https://arxiv.org/abs/1910.05446 | Choi et al. 2019 — On empirical comparisons of optimizers for deep learning (tuning protocols) |
| hoffmann2022_chinchilla_2203.15556.pdf | https://arxiv.org/abs/2203.15556 | Hoffmann et al. 2022 — Training compute-optimal LLMs (cosine cycle length vs training length) |
| gelbart2014_1403.5607.pdf | https://arxiv.org/abs/1403.5607 | Gelbart et al. 2014 — Bayesian optimization with unknown constraints (infeasible trials) |
| hoffer2017_1705.08741.pdf | https://arxiv.org/abs/1705.08741 | Hoffer et al. 2017 — Train longer, generalize better (large batch, regime adaptation) |
| bachlechner2020_rezero_2003.04887.pdf | https://arxiv.org/abs/2003.04887 | Bachlechner et al. 2020 — ReZero (residual init for stability) |
| wu2018_shorthorizon_1803.02021.pdf | https://arxiv.org/abs/1803.02021 | Wu et al. 2018 — Understanding short-horizon bias in stochastic meta-optimization |
| bousquet2017_quasirandom_1706.03200.pdf | https://arxiv.org/abs/1706.03200 | Bousquet et al. 2017 — Critical hyper-parameters: no random, no cry (quasi-random search) |
| li2017_hyperband_jmlr16-558.pdf | https://jmlr.org/papers/volume18/16-558/16-558.pdf | Li et al. 2017 — Hyperband |
| bergstra2012_randomsearch_jmlr.pdf | https://www.jmlr.org/papers/v13/bergstra12a.html | Bergstra & Bengio 2012 — Random search for hyper-parameter optimization |
| recht2016_argmin_hypertuning.html | http://www.argmin.net/2016/06/20/hypertuning/ | **Not retrieved**: the URL now redirects to a "Page not found" page. Its point (2×-budget random search is a strong baseline) survives only via the playbook footnote (README L1739–1749). |

## References cited by Karpathy's recipe
| File | URL | What it is |
|---|---|---|
| hinton2015_distillation_1503.02531.pdf | https://arxiv.org/abs/1503.02531 | Hinton et al. 2015 — Distilling the knowledge in a neural network |
| li2018_dropout_bn_1801.05134.pdf | https://arxiv.org/abs/1801.05134 | Li et al. 2018 — Disharmony between dropout and batch normalization |
| dwibedi2017_cutpaste_1708.01642.pdf | https://arxiv.org/abs/1708.01642 | Dwibedi et al. 2017 — Cut, paste and learn (synthetic data) |
| (same as above) bergstra2012 | http://jmlr.csail.mit.edu/papers/volume13/bergstra12a/bergstra12a.pdf | random over grid search |
| karpathy_backprop_post.html | https://medium.com/@karpathy/yes-you-should-understand-backprop-e2f06eab496b | **Not retrieved**: Medium returned a bot-check page (5 KB). Content already summarised in the skill's evidence.md. |

## Additional context (not cited by either source; added because they bear directly on what went wrong)
| File | URL | Why |
|---|---|---|
| smith2017_onecycle_superconvergence_1708.07120.pdf | https://arxiv.org/abs/1708.07120 | Smith & Topin — super-convergence / the OneCycle policy we used |
| smith2018_disciplined_1803.09820.pdf | https://arxiv.org/abs/1803.09820 | Smith — A disciplined approach to NN hyper-parameters (LR range test, OneCycle) |
| goyal2017_warmup_1706.02677.pdf | https://arxiv.org/abs/1706.02677 | Goyal et al. — large-minibatch SGD, linear scaling + warmup |
| gilmer2021_curvature_instability_2110.04369.pdf | https://arxiv.org/abs/2110.04369 | Gilmer et al. — loss-curvature view of training instability (authors of the playbook) |
| wortsman2023_smallscale_instabilities_2309.14322.pdf | https://arxiv.org/abs/2309.14322 | Wortsman et al. — small-scale proxies for large-scale instabilities (LR sensitivity) |
| loshchilov2017_adamw_1711.05101.pdf | https://arxiv.org/abs/1711.05101 | Loshchilov & Hutter — decoupled weight decay (AdamW) |
| zhang2019_batchsize_1907.04164.pdf | https://arxiv.org/abs/1907.04164 | Zhang et al. — which algorithmic choices matter at which batch sizes |
| nado2021_largebatch_2102.06356.pdf | https://arxiv.org/abs/2102.06356 | Nado et al. — a large-batch optimizer reality check (playbook co-author) |
