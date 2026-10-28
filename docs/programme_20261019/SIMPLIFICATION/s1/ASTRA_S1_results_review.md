# ASTRA-S1 — independent final results certification

**PASS — the fixed-budget ladder results are trustworthy: wider models and more reference data improve accuracy within the approved v3/census05 experiment.**

Reviewed `4f94133` on 22 October 2026. Actual HEAD `624adb1` adds only the review brief. All checks were read-only; no files written, jobs submitted, or background jobs started.

**Findings — most severe first**

1. **MEDIUM — S1’s training scope and its comparison with wave-2 need explicit separation.**

   S1 uses **364,871 v3/census05 rows**, without wave-2’s v4 `add_corr` training treatment. Correcting evaluation references does not turn these models into a corrected-training experiment. This is the scope accepted at prelaunch. [Preregistration](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/PREREGISTRATION.md:12).

   The **1.620835% S1 ×1/full versus 1.273781% wave-2 add** gap cannot be explained by different raw-test codecs or splits. My direct join found:

   - The same **42,038 row IDs**, with **zero reference-label differences**.
   - The same v1 reference codec, reserved split, instrument manifest and **2,489,622 reference atoms**.
   - The same v2.1 prediction codec.

   Wave-2 add uses **×2**. S1’s corresponding width scores **1.387051%**, leaving a **0.113270 pp** raw-test gap. Training population, component sampling, shared-data preparation and deterministic CPU-CTC execution differ; their individual contributions are not isolated.

   Reference choice nevertheless matters: S1 ×2/full scores **1.222669%** on ADMIT-only corrected v2, versus wave-2 add’s **1.290858%**, reversing their numerical ordering. Among the retained v2 rows, **2,791/39,434** immutable raw-parent labels differ from the original factory references, before the **426 corrections**. Thus raw→ADMIT-raw combines filtering and reference representation changes. The two experiments provide comparable measurements on their shared instruments, but do not form a controlled width, data or correction ablation. [Execution/population differences](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/PARITY.md:3), [wave-2 reference results](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/RESULTS_CLEANED_REFS.md:1).

2. **MEDIUM — The packet omits ADMIT-only corrected seal04, but this does not block the ladder conclusions.**

   I independently scored the saved hypotheses against the SHA-verified overlays, retaining **2,232 ADMIT test rows** and excluding **21 HOLD rows**. All **437 dev rows** are ADMIT.

   **None of the ten overall test decisions changes:** nine pass the numerical rule; ×1 targeting remains unresolved. Dev exactly reproduces overlay-only scoring. The additional test means appear below.

   One mean changes sign without becoming decided: ×1 targeting moves from **−0.001856 pp** on raw seal04 to **+0.002792 pp** on admitted-corrected seal04, against a **0.043277 pp** control range. The missing view should be added to the packet, but its omission does not invalidate these results.

3. **MEDIUM — Convergence-qualified hypothesis confirmation remains pending.**

   All runs completed the prescribed horizon. However, **20/24** validation curves still improve between epochs 7 and 8; changes range from **−0.0091 to +0.0240 pp**. No preregistered flatness qualification has been completed.

   The report correctly labels its passes as numerical, descriptive decisions. They support an accuracy comparison at this training budget, without establishing converged optima. The **1.7542×** data increase also cannot establish the required two-doubling scaling floor. [Declared limitations](/Users/foivoskarounous-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/S1_RESULTS.md:70).

**Cleared — arithmetic and decision rules**

I independently recomputed the means and contrasts from all **240 original result entries** across ten instruments. All **400 supported comparisons** match; **20 zero-support comparisons** correctly remain pending.

For the final reference views, all **56 cell means**, **70 overall contrasts**, and **1,120 supported overall/slice comparisons** match. All **434 checked printed values/decisions** agree with exact arithmetic. I also independently recomputed all **168 reported run/view CERs directly from the 72 saved prediction files**; every integer numerator and denominator matches.

The rule is applied exactly as registered:

`Δ = mean(control CER) − mean(candidate CER)`  
`R = max(control CER) − min(control CER)`  
**Numerical pass requires strictly Δ > R**, using seeds 0/1/2 and exact fractions. This is not a significance test. No ×2-targeted cell or additional ×1.5→×2 contrast was silently introduced. [Original aggregate](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/record/results01/aggregate_3721146/REPORT.json), [final scores](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/record/results02/rescore_3721578/outputs/report.json).

Selected recomputed means, in CER percent; brackets show the three-seed minimum–maximum:

| Width / subset | v2 ADMIT corrected | Seal04 test raw [seed span] | Seal04 ADMIT corrected — my recount |
|---|---:|---:|---:|
| ×1 / ref_208k | 1.508299 | 2.606827 [2.589195–2.639308] | 2.533318 |
| ×1 / ref_364871 | 1.454666 | 2.485256 [2.455559–2.502888] | 2.407211 |
| ×1 / tgt_208k | 1.634155 | 2.608684 [2.561354–2.668541] | 2.530526 |
| ×1.5 / ref_208k | 1.359931 | 2.366005 [2.346980–2.377605] | 2.296925 |
| ×1.5 / ref_364871 | 1.296375 | 2.232369 [2.188287–2.319139] | 2.161511 |
| ×1.5 / tgt_208k | 1.451187 | 2.304291 [2.282946–2.340020] | 2.234569 |
| ×2 / ref_208k | 1.307381 | 2.239793 [2.177151–2.299651] | 2.168025 |
| ×2 / ref_364871 | 1.222669 | 2.098269 [2.089453–2.114509] | 2.024700 |

All ten registered contrasts are below. Each numerical entry is **gain Δ / control range R**, in percentage points. “Full” means 364,871 reference rows.

| Contrast | Seal04 test raw Δ / R | v2 ADMIT corrected Δ / R | Numerical decision: seal / v2 |
|---|---:|---:|---|
| Data, ×1: 208k→full | 0.121572 / 0.050113 | 0.053633 / 0.020273 | Pass / Pass |
| Data, ×1.5: 208k→full | 0.133636 / 0.030625 | 0.063556 / 0.021299 | Pass / Pass |
| Data, ×2: 208k→full | 0.141524 / 0.122500 | 0.084712 / 0.005774 | Pass / Pass |
| Width, ref_208k: ×1→×1.5 | 0.240823 / 0.050113 | 0.148368 / 0.020273 | Pass / Pass |
| Width, ref_208k: ×1→×2 | 0.367035 / 0.050113 | 0.200917 / 0.020273 | Pass / Pass |
| Width, full: ×1→×1.5 | 0.252887 / 0.047329 | 0.158290 / 0.020829 | Pass / Pass |
| Width, full: ×1→×2 | 0.386987 / 0.047329 | 0.231997 / 0.020829 | Pass / Pass |
| Width, targeted: ×1→×1.5 | 0.304393 / 0.107187 | 0.182968 / 0.023096 | Pass / Pass |
| Targeting, ×1 | −0.001856 / 0.050113 | −0.125857 / 0.020273 | Fail / Fail |
| Targeting, ×1.5 | 0.061714 / 0.030625 | −0.091256 / 0.021299 | Pass / Fail |

Plain interpretation:

- **Width:** all five registered contrasts pass on v2 and seal04 test. The observed benefit is larger than the data-size benefit for these tested changes.
- **Data:** all three size contrasts pass. The ×2 seal04 result has the narrowest margin: **0.141524 > 0.122500 pp**.
- **Targeting:** ×1 seal04 is within seed variation. ×1.5 improves seal04, but both widths consistently worsen v2 across all three seeds. This is a trade-off, not a general accuracy improvement.

**Cleared — consistency, with limits**

No overall ladder decision flips between v2 raw, ADMIT raw and ADMIT corrected, or between seal04 raw, overlay-only and my admitted-corrected recount.

Dev is less decisive: **4/10** comparisons pass under both reported variants—×2’s data increase, ×1→×2 on both reference subsets, and ×1→×1.5 on targeted data. The other six do not exceed their control ranges.

The “no flips” statement must remain restricted to overall decisions. Slice decisions do change. For example:

- Seal04-test **degraded**, ×1.5 targeting: raw **0.407498 > 0.366748 pp**, but overlay **0.434664 < 0.448248 pp**.
- v2 **Cyrillic**, ×1 data increase: ADMIT raw fails; corrected passes.

Other continuity instruments also provide weaker support: Wikisource has **7/10** numerical passes, E1 real test **2/10**, and synthetic heldout **7/10**. The result is not universal improvement on every instrument or class.

**Cleared — identity, nesting and exposure**

Live verification established:

- **699 base-package entries and 38 declared overlay files**, with zero unexpected hash mismatches; operational manifest `95b361468a695a578dc5ece75dd125500bc742d1473c66ff580428edd733fd07`.
- **Eight CELL_COMPLETE receipts, 24 completion/run bindings, 24 training logs and 240 prediction-receipt bindings**.
- Every run: from scratch, eight epochs, **53,616 updates**, no early stopping, validation-CER checkpoint selection, and the deployed trainer/segment hashes.
- Fixed **428,872 draws per epoch**, half real and half synthetic. Increasing the pool changes available distinct support and repetition, while retaining the update budget.

I rehashed and recounted **all three subsets**:

| Subset | Rows / unique keys | Seal04 key / recorded crop / recorded edition overlaps |
|---|---:|---:|
| ref_208k | 208,000 / 208,000 | 0 / 0 / 0 |
| ref_364871 | 364,871 / 364,871 | 0 / 0 / 0 |
| tgt_208k | 208,000 / 208,000 | 0 / 0 / 0 |

`ref_208k` is an exact ordered prefix of `ref_364871`; targeted rows outside the full universe: **zero**. The original iopsstor ref_208k bytes match capstor. These checks establish no recorded S1 training overlap with seal04; canonical-work and historical checkpoint exposure remain unresolved, so **diagnostic_only** is retained.

**Cleared — accounting**

Independent parsing of the saved parent-allocation ledger reproduces:

| Scope | Parents | Requested GPU-h | Node GPU-h |
|---|---:|---:|---:|
| S1 | 58 | 74.553611 | 130.758889 |
| Wave-2 | 25 | 44.441389 | 81.453333 |
| **Shared** | **83** | **118.995000** | **212.212222** |

At the packet’s **13:43:45 UTC** capture, headroom was **231.005000 requested GPU-h below 350**, with no active scoped jobs. Failed attempts, aggregate timeout **3716978**, retry **3721146** and scoring **3721578** are included; steps are not double-counted. The retry completed in **193 seconds**. No separate series cap applies. [Parent ledger](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-s1/docs/ocr_program_2026-10-06/s1_scaling/record/results02/rescore_3721578/SACCT.txt).

**For the owner**

For this approved corpus and fixed training budget, both capacity and additional reference data buy accuracy. Width produces the larger observed gain: at the full pool, ×1→×2 reduces seal04 raw CER from **2.485% to 2.098%**, a **15.6% relative reduction**. Increasing reference data buys another **0.12–0.14 pp** at each width. Combining both changes improves **2.607% to 2.098%**, about **19.5% relatively**. Targeting is less reliable because its seal04 benefit at ×1.5 comes with worse v2 performance. I would carry the full reference pool forward and take one next step: **measure ×1.5 and ×2 latency on the actual deployment CPU before choosing the production width**. These results establish useful fixed-budget gains; they do not establish a data floor or settle the corrected-v4 training question.

VERDICT: PASS — fixed-budget v3/census05 ladder verified; width and reference-data gains hold, with nonblocking scope and convergence limitations | BLOCKERS: 0 | HIGH: 0