# S1 scaling results

**READY FOR S1 results.** All 24 runs completed eight epochs / 53,616 updates without early stopping; eight CELL_COMPLETE receipts bind the outputs. Aggregate retry **3721146 PASS** (193 seconds); CPU raw/cleaned scoring **3721578 COMPLETED / 0:0**, 430 seconds, with all 24 models and raw-score parity checks passing. Best checkpoints were selected by validation CER; predictions were reused without inference or retraining.

[Machine-readable scores and all class/book/facet slices](record/results02/rescore_3721578/outputs/report.json), [scoring receipt](record/results02/rescore_3721578/outputs/RESCORE_COMPLETE.json), [full scoring log](record/results02/rescore_3721578/rescore_3721578.log), [readback validation](record/results02/rescore_3721578/VALIDATION.json), [training curves](record/results02/rescore_3721578/TRAINING_READOUT.json).

Eight cells: ×1 / ×1.5 on ref_208k, ref_364871 and tgt_208k; ×2 on the two reference subsets only; seeds 0/1/2 in each. The prelaunch amendment removed ×2/tgt_208k. Subsets are nested where specified; the targeted arm is supply-limited and more balanced than reference, rather than an achieved benchmark mix. The recipe and optimizer draw horizon are fixed across this ladder. [Preregistration and amendments](PREREGISTRATION.md), [input identities](INPUTS.json), [accepted launch packet](REVIEW_INPUTS.md).

| Reference view | Rows | Reference policy |
|---|---:|---|
| v2 raw | 42,038 | Original saved instrument references (v1 reference codec/reserved split); original aggregate parity |
| v2 ADMIT raw | 39,434 | census_06 ADMIT population, immutable raw-parent labels before factory folds |
| v2 ADMIT-only corrected | 39,434 | Same ADMIT rows; 426 corrected labels; NFD references and unchanged literal hypotheses |
| seal04 test raw / overlay-only | 2,253 / 2,253 | Complete sealed panel; six overlaid labels; no row filtering |
| seal04 dev raw / overlay-only | 437 / 437 | Complete sealed dev panel; one overlaid label; no row filtering |

The v2 ADMIT-raw view separates the population/reference representation change from label correction. Raw→ADMIT raw is not a pure filtering effect because the original instrument passed through its reference codec; ADMIT raw→corrected holds population fixed. Seal04 overlays preserve the panel and its existing edits. These are the exact SHA-bound reference outputs of wave-2 job 3717948, reused with the scorer from e4w2v4 commit 14f1786. Corrected/overlaid comparisons are diagnostic_only. Seal04 itself remains diagnostic_only pending checkpoint exposure and work-identity review; it is not independent human gold.

CER values below are percentages; lower is better. Seal04 uses the unchanged scorer’s NFD atom metric; v2 uses the frozen E3 literal-hypothesis metric. Tests and dev remain separate.

## Ladder means across seeds

| Width | Subset | v2 raw CER % | v2 ADMIT raw CER % | v2 ADMIT corrected CER % | seal04 test raw CER % | seal04 test overlay-only CER % | seal04 dev raw CER % | seal04 dev overlay-only CER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ×1 | ref_208k | 1.674792 | 1.520574 | 1.508299 | 2.606827 | 2.600759 | 4.037638 | 4.030616 |
| ×1 | ref_364871 | 1.620835 | 1.467695 | 1.454666 | 2.485256 | 2.479189 | 3.983803 | 3.976781 |
| ×1 | tgt_208k | 1.808092 | 1.646691 | 1.634155 | 2.608684 | 2.601687 | 4.014231 | 4.007209 |
| ×1.5 | ref_208k | 1.527059 | 1.371959 | 1.359931 | 2.366005 | 2.361796 | 3.904220 | 3.906561 |
| ×1.5 | ref_364871 | 1.461708 | 1.308758 | 1.296375 | 2.232369 | 2.228626 | 3.686539 | 3.681858 |
| ×1.5 | tgt_208k | 1.621826 | 1.462862 | 1.451187 | 2.304291 | 2.299619 | 3.726330 | 3.719308 |
| ×2 | ref_208k | 1.472044 | 1.318510 | 1.307381 | 2.239793 | 2.234658 | 3.686539 | 3.686539 |
| ×2 | ref_364871 | 1.387051 | 1.234651 | 1.222669 | 2.098269 | 2.093135 | 3.560143 | 3.564825 |

On seal04 test, **9/10 raw comparisons** exceed the control seed range; the overlay-only view has **9/10**. Changed numerical decisions after the overlay: **none**. These counts are descriptive and retain the convergence and diagnostic-status limitations below.

On seal04 test and v2_test, all three larger-reference size contrasts and all five registered width contrasts exceed the control seed range in both raw and corrected/overlay views. The targeted intervention is mixed: ×1 does not clear the rule on seal04 test, while ×1.5 does; both targeted contrasts have negative mean gains on v2_test. These are within-ladder descriptive results under the stated instrument limitations.


## Every model

| Width | Subset | Seed | v2 raw CER % | v2 ADMIT raw CER % | v2 ADMIT corrected CER % | seal04 test raw CER % | seal04 test overlay-only CER % | seal04 dev raw CER % | seal04 dev overlay-only CER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ×1 | ref_208k | 0 | 1.687927 | 1.533633 | 1.521058 | 2.589195 | 2.582199 | 4.178077 | 4.171055 |
| ×1 | ref_208k | 1 | 1.667522 | 1.515071 | 1.503052 | 2.639308 | 2.632312 | 4.058704 | 4.051682 |
| ×1 | ref_208k | 2 | 1.668928 | 1.513018 | 1.500785 | 2.591979 | 2.587767 | 3.876132 | 3.869110 |
| ×1 | ref_364871 | 0 | 1.630127 | 1.479485 | 1.465885 | 2.455559 | 2.448565 | 4.142967 | 4.135946 |
| ×1 | ref_364871 | 1 | 1.607794 | 1.457886 | 1.445057 | 2.497320 | 2.490325 | 3.988484 | 3.981462 |
| ×1 | ref_364871 | 2 | 1.624584 | 1.465713 | 1.453055 | 2.502888 | 2.498678 | 3.819956 | 3.812934 |
| ×1 | tgt_208k | 0 | 1.792923 | 1.632434 | 1.619172 | 2.596155 | 2.589159 | 4.023594 | 4.016572 |
| ×1 | tgt_208k | 1 | 1.815737 | 1.653605 | 1.641027 | 2.561354 | 2.554358 | 3.988484 | 3.981462 |
| ×1 | tgt_208k | 2 | 1.815617 | 1.654033 | 1.642267 | 2.668541 | 2.661544 | 4.030616 | 4.023594 |
| ×1.5 | ref_208k | 0 | 1.525573 | 1.368067 | 1.355454 | 2.346980 | 2.339987 | 3.700583 | 3.707605 |
| ×1.5 | ref_208k | 1 | 1.536820 | 1.384406 | 1.372819 | 2.377605 | 2.376180 | 3.953374 | 3.960396 |
| ×1.5 | ref_208k | 2 | 1.518785 | 1.363405 | 1.351520 | 2.373429 | 2.369220 | 4.058704 | 4.051682 |
| ×1.5 | ref_364871 | 0 | 1.458936 | 1.306777 | 1.294294 | 2.319139 | 2.314931 | 3.693561 | 3.686539 |
| ×1.5 | ref_364871 | 1 | 1.468617 | 1.314433 | 1.301565 | 2.188287 | 2.184081 | 3.693561 | 3.686539 |
| ×1.5 | ref_364871 | 2 | 1.457571 | 1.305066 | 1.293267 | 2.189679 | 2.186865 | 3.672495 | 3.672495 |
| ×1.5 | tgt_208k | 0 | 1.638401 | 1.479229 | 1.467254 | 2.282946 | 2.275954 | 3.848044 | 3.841022 |
| ×1.5 | tgt_208k | 1 | 1.623218 | 1.463831 | 1.451472 | 2.340020 | 2.335811 | 3.637385 | 3.630363 |
| ×1.5 | tgt_208k | 2 | 1.603858 | 1.445525 | 1.434835 | 2.289906 | 2.287090 | 3.693561 | 3.686539 |
| ×2 | ref_208k | 0 | 1.466889 | 1.316785 | 1.305414 | 2.242577 | 2.235586 | 3.721649 | 3.714627 |
| ×2 | ref_208k | 1 | 1.473155 | 1.315502 | 1.305542 | 2.177151 | 2.172945 | 3.623341 | 3.623341 |
| ×2 | ref_208k | 2 | 1.476088 | 1.323243 | 1.311188 | 2.299651 | 2.295443 | 3.714627 | 3.721649 |
| ×2 | ref_364871 | 0 | 1.388685 | 1.235093 | 1.223125 | 2.114509 | 2.107520 | 3.525033 | 3.532055 |
| ×2 | ref_364871 | 1 | 1.383664 | 1.233296 | 1.221628 | 2.089453 | 2.085247 | 3.651429 | 3.651429 |
| ×2 | ref_364871 | 2 | 1.388805 | 1.235563 | 1.223253 | 2.090845 | 2.086639 | 3.503967 | 3.510989 |

## Preregistered within-ladder contrasts

The primary descriptive instrument is seal04 test; dev and v2 continuity instruments remain separate. For exactly seeds 0/1/2, compute CER as the exact rational edits/reference-codepoints (seal04: NFD atoms), then Δ = mean(control) − mean(candidate) and R = max(control) − min(control). The registered numerical criterion is **Δ > R**, strictly; equality fails. Positive Δ favours the candidate. Missing seeds or zero reference support are PENDING. The tables report this numerical criterion, not a significance test or independent validation. New reference views reuse the rule diagnostically.

All runs reached the full horizon and none stopped by patience. Flatness of the final two validation epochs has not been formally qualified here; hypothesis confirmation conditional on convergence remains pending. A seed-range PASS alone does not establish convergence or a scaling floor. Full training logs and their completion-bound hashes are provided above.

Registered contrasts are size 208k→364,871 at each width; reference→targeted at ×1/×1.5; and ×1→×1.5 or ×2 at fixed subset. There is no omitted ×2-target comparison and no newly selected ×1.5→×2 contrast. Supported primary-class/slice outcomes and integer denominators are retained in report.json; no class/panel/book was removed.

### v2 raw

| Control → candidate | Mean gain, pp | Control range, pp | Δ > R |
|---|---:|---:|---|
| w1_ref_208k -> w1_ref_364871 | 0.053957 | 0.020405 | PASS |
| w1_ref_208k -> w1_tgt_208k | -0.133300 | 0.020405 | FAIL |
| w1.5_ref_208k -> w1.5_ref_364871 | 0.065351 | 0.018035 | PASS |
| w1.5_ref_208k -> w1.5_tgt_208k | -0.094767 | 0.018035 | FAIL |
| w2_ref_208k -> w2_ref_364871 | 0.084993 | 0.009198 | PASS |
| w1_ref_208k -> w1.5_ref_208k | 0.147733 | 0.020405 | PASS |
| w1_ref_208k -> w2_ref_208k | 0.202748 | 0.020405 | PASS |
| w1_ref_364871 -> w1.5_ref_364871 | 0.159127 | 0.022333 | PASS |
| w1_ref_364871 -> w2_ref_364871 | 0.233784 | 0.022333 | PASS |
| w1_tgt_208k -> w1.5_tgt_208k | 0.186267 | 0.022815 | PASS |

### v2 ADMIT raw

| Control → candidate | Mean gain, pp | Control range, pp | Δ > R |
|---|---:|---:|---|
| w1_ref_208k -> w1_ref_364871 | 0.052879 | 0.020616 | PASS |
| w1_ref_208k -> w1_tgt_208k | -0.126117 | 0.020616 | FAIL |
| w1.5_ref_208k -> w1.5_ref_364871 | 0.063201 | 0.021000 | PASS |
| w1.5_ref_208k -> w1.5_tgt_208k | -0.090902 | 0.021000 | FAIL |
| w2_ref_208k -> w2_ref_364871 | 0.083859 | 0.007742 | PASS |
| w1_ref_208k -> w1.5_ref_208k | 0.148614 | 0.020616 | PASS |
| w1_ref_208k -> w2_ref_208k | 0.202064 | 0.020616 | PASS |
| w1_ref_364871 -> w1.5_ref_364871 | 0.158936 | 0.021599 | PASS |
| w1_ref_364871 -> w2_ref_364871 | 0.233044 | 0.021599 | PASS |
| w1_tgt_208k -> w1.5_tgt_208k | 0.183829 | 0.021599 | PASS |

### v2 ADMIT corrected

| Control → candidate | Mean gain, pp | Control range, pp | Δ > R |
|---|---:|---:|---|
| w1_ref_208k -> w1_ref_364871 | 0.053633 | 0.020273 | PASS |
| w1_ref_208k -> w1_tgt_208k | -0.125857 | 0.020273 | FAIL |
| w1.5_ref_208k -> w1.5_ref_364871 | 0.063556 | 0.021299 | PASS |
| w1.5_ref_208k -> w1.5_tgt_208k | -0.091256 | 0.021299 | FAIL |
| w2_ref_208k -> w2_ref_364871 | 0.084712 | 0.005774 | PASS |
| w1_ref_208k -> w1.5_ref_208k | 0.148368 | 0.020273 | PASS |
| w1_ref_208k -> w2_ref_208k | 0.200917 | 0.020273 | PASS |
| w1_ref_364871 -> w1.5_ref_364871 | 0.158290 | 0.020829 | PASS |
| w1_ref_364871 -> w2_ref_364871 | 0.231997 | 0.020829 | PASS |
| w1_tgt_208k -> w1.5_tgt_208k | 0.182968 | 0.023096 | PASS |

### seal04 test raw

| Control → candidate | Mean gain, pp | Control range, pp | Δ > R |
|---|---:|---:|---|
| w1_ref_208k -> w1_ref_364871 | 0.121572 | 0.050113 | PASS |
| w1_ref_208k -> w1_tgt_208k | -0.001856 | 0.050113 | FAIL |
| w1.5_ref_208k -> w1.5_ref_364871 | 0.133636 | 0.030625 | PASS |
| w1.5_ref_208k -> w1.5_tgt_208k | 0.061714 | 0.030625 | PASS |
| w2_ref_208k -> w2_ref_364871 | 0.141524 | 0.122500 | PASS |
| w1_ref_208k -> w1.5_ref_208k | 0.240823 | 0.050113 | PASS |
| w1_ref_208k -> w2_ref_208k | 0.367035 | 0.050113 | PASS |
| w1_ref_364871 -> w1.5_ref_364871 | 0.252887 | 0.047329 | PASS |
| w1_ref_364871 -> w2_ref_364871 | 0.386987 | 0.047329 | PASS |
| w1_tgt_208k -> w1.5_tgt_208k | 0.304393 | 0.107187 | PASS |

### seal04 test overlay-only

| Control → candidate | Mean gain, pp | Control range, pp | Δ > R |
|---|---:|---:|---|
| w1_ref_208k -> w1_ref_364871 | 0.121570 | 0.050113 | PASS |
| w1_ref_208k -> w1_tgt_208k | -0.000928 | 0.050113 | FAIL |
| w1.5_ref_208k -> w1.5_ref_364871 | 0.133170 | 0.036193 | PASS |
| w1.5_ref_208k -> w1.5_tgt_208k | 0.062177 | 0.036193 | PASS |
| w2_ref_208k -> w2_ref_364871 | 0.141522 | 0.122498 | PASS |
| w1_ref_208k -> w1.5_ref_208k | 0.238964 | 0.050113 | PASS |
| w1_ref_208k -> w2_ref_208k | 0.366102 | 0.050113 | PASS |
| w1_ref_364871 -> w1.5_ref_364871 | 0.250564 | 0.050113 | PASS |
| w1_ref_364871 -> w2_ref_364871 | 0.386054 | 0.050113 | PASS |
| w1_tgt_208k -> w1.5_tgt_208k | 0.302069 | 0.107186 | PASS |

### seal04 dev raw

| Control → candidate | Mean gain, pp | Control range, pp | Δ > R |
|---|---:|---:|---|
| w1_ref_208k -> w1_ref_364871 | 0.053835 | 0.301945 | FAIL |
| w1_ref_208k -> w1_tgt_208k | 0.023407 | 0.301945 | FAIL |
| w1.5_ref_208k -> w1.5_ref_364871 | 0.217681 | 0.358121 | FAIL |
| w1.5_ref_208k -> w1.5_tgt_208k | 0.177890 | 0.358121 | FAIL |
| w2_ref_208k -> w2_ref_364871 | 0.126396 | 0.098308 | PASS |
| w1_ref_208k -> w1.5_ref_208k | 0.133418 | 0.301945 | FAIL |
| w1_ref_208k -> w2_ref_208k | 0.351099 | 0.301945 | PASS |
| w1_ref_364871 -> w1.5_ref_364871 | 0.297264 | 0.323011 | FAIL |
| w1_ref_364871 -> w2_ref_364871 | 0.423659 | 0.323011 | PASS |
| w1_tgt_208k -> w1.5_tgt_208k | 0.287901 | 0.042132 | PASS |

### seal04 dev overlay-only

| Control → candidate | Mean gain, pp | Control range, pp | Δ > R |
|---|---:|---:|---|
| w1_ref_208k -> w1_ref_364871 | 0.053835 | 0.301945 | FAIL |
| w1_ref_208k -> w1_tgt_208k | 0.023407 | 0.301945 | FAIL |
| w1.5_ref_208k -> w1.5_ref_364871 | 0.224703 | 0.344077 | FAIL |
| w1.5_ref_208k -> w1.5_tgt_208k | 0.187253 | 0.344077 | FAIL |
| w2_ref_208k -> w2_ref_364871 | 0.121714 | 0.098308 | PASS |
| w1_ref_208k -> w1.5_ref_208k | 0.124055 | 0.301945 | FAIL |
| w1_ref_208k -> w2_ref_208k | 0.344077 | 0.301945 | PASS |
| w1_ref_364871 -> w1.5_ref_364871 | 0.294923 | 0.323011 | FAIL |
| w1_ref_364871 -> w2_ref_364871 | 0.411956 | 0.323011 | PASS |
| w1_tgt_208k -> w1.5_tgt_208k | 0.287901 | 0.042132 | PASS |

## Final validation epochs

The following values come from the 24 SHA-verified train_log.csv files bound by E1_RUN_COMPLETE. Positive epoch-7 minus epoch-8 change means validation CER was still improving. These are observed changes, without an added post hoc flatness threshold.

| Model | Epoch 7 val CER % | Epoch 8 val CER % | 7 − 8, pp |
|---|---:|---:|---:|
| w1.5_ref_208k_s0 | 1.559800 | 1.558900 | 0.000900 |
| w1.5_ref_208k_s1 | 1.583600 | 1.590400 | -0.006800 |
| w1.5_ref_208k_s2 | 1.555800 | 1.553100 | 0.002700 |
| w1.5_ref_364871_s0 | 1.485600 | 1.465400 | 0.020200 |
| w1.5_ref_364871_s1 | 1.486800 | 1.473900 | 0.012900 |
| w1.5_ref_364871_s2 | 1.497900 | 1.473900 | 0.024000 |
| w1.5_tgt_208k_s0 | 1.633600 | 1.610900 | 0.022700 |
| w1.5_tgt_208k_s1 | 1.624600 | 1.603400 | 0.021200 |
| w1.5_tgt_208k_s2 | 1.631900 | 1.615500 | 0.016400 |
| w1_ref_208k_s0 | 1.669100 | 1.673500 | -0.004400 |
| w1_ref_208k_s1 | 1.692800 | 1.682500 | 0.010300 |
| w1_ref_208k_s2 | 1.691200 | 1.679900 | 0.011300 |
| w1_ref_364871_s0 | 1.640600 | 1.628400 | 0.012200 |
| w1_ref_364871_s1 | 1.646900 | 1.628500 | 0.018400 |
| w1_ref_364871_s2 | 1.648200 | 1.634400 | 0.013800 |
| w1_tgt_208k_s0 | 1.739600 | 1.727800 | 0.011800 |
| w1_tgt_208k_s1 | 1.789100 | 1.774200 | 0.014900 |
| w1_tgt_208k_s2 | 1.749100 | 1.727200 | 0.021900 |
| w2_ref_208k_s0 | 1.507100 | 1.511700 | -0.004600 |
| w2_ref_208k_s1 | 1.524300 | 1.533400 | -0.009100 |
| w2_ref_208k_s2 | 1.540100 | 1.530700 | 0.009400 |
| w2_ref_364871_s0 | 1.415600 | 1.395600 | 0.020000 |
| w2_ref_364871_s1 | 1.413400 | 1.405600 | 0.007800 |
| w2_ref_364871_s2 | 1.422300 | 1.411600 | 0.010700 |

## Limits on interpretation

The original floor rule requires a book-paired bootstrap with 95% upper gain bounds below δ=0.05 pp on v2_test and δ=0.10 pp on the human-referenced instrument family for two consecutive doublings, the width ladder also below threshold, and qualified convergence. Intervals straddling δ permit one extension to five seeds, then parking. This experiment supplies only one 208,000→364,871 sub-doubling (1.7542×), so **a floor is not identifiable** regardless of the observed gains. No 840k launch or target-CPU deployment suitability follows from this packet. [Original decision rules](PREREGISTRATION.md).

H1 retains the accepted local six-worker iterator boundary/mid-epoch state equality and GPU split BIT_IDENTICAL evidence. The native full-trainer six-worker boundary case was skipped; production first segments completed normally, so these runs do not newly test TERM/deadline yields. [H1 evidence](record/H1_LOCAL.json), [production outcome and continuation-boundary records](LAUNCH_OUTCOME.md).

## Cumulative allocation accounting

Parent-only sacct captured **2026-10-22T13:43:45.283342+00:00**. Elapsed seconds × requested GPUs / 3600 determines the authoritative spent cost. CPU-only allocations request zero GPUs but occupy a four-GPU node; allocated/node cost is shown separately. Failed/retried jobs, the original aggregate TIMEOUT 3716978 and the successful retry are included; Slurm steps are not counted twice.

| Scope | Parent allocations | Requested GPU-h | Node GPU-h |
|---|---:|---:|---:|
| S1 | 58 | 74.553611 | 130.758889 |
| wave2 | 25 | 44.441389 | 81.453333 |
| Shared | 83 | **118.995000** | **212.212222** |

Sole cap: **350 requested GPU-h**, leaving **231.005000 GPU-h** at capture. No separate series caps apply. Completed series A/B production totals are **47.295000 / 20.050833 requested GPU-h**. CPU scoring 3721578 adds **0 requested / 0.477778 node GPU-h**. Active scoped jobs at capture: **[]**; future unsubmitted work is excluded. All S1 work requested here is terminal; no additional job is proposed.

[Raw parent sacct](record/results02/rescore_3721578/SACCT.txt), [exact parsed accounting](record/results02/rescore_3721578/ACCOUNTING.json), [shared accounting history](ACCOUNTING.md).
