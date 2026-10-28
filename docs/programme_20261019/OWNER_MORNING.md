# Owner summary — updated 2026-10-22 17:00 Athens — ALL THREE TASKS CLOSED

## The three things
1. **Repo cleanup:** done. Public repo https://github.com/fffoivos/greek-ocr-toolkit; branches merged and deleted.
2. **Row filtering + correcting:** done. Census_06 over 592,466 lines (456,967 admitted / 84,754 held / 50,745 dropped; 16/16 invariants). Release v4 = 167,946 clean lines (W1 50,622 / W2 117,324), raw labels, 904 polytonic corrections as the registered overlay, 207,243 crops byte-exact, zero crop gaps. Sol xhigh acceptance: ACCEPT (two single-row quality notes). Path: /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/rel4_c06_full_01.
3. **Experiments:**
   - **Wave 2 on v4 — DONE, Astra CP4 PASS.** Nine runs (ctrl / add / add_corr × 3 seeds; 36.7 requested GPU-h). Internal test CER: ctrl 1.236 / add 1.274 / add_corr 1.269 % → the preregistered "add" hypothesis is refuted (−0.04 pp). Benchmark seal04 test CER: ctrl 4.03 / add 2.32 / add_corr 2.28 % → adding the v4 rows nearly halves the benchmark error. Corrections: +0.04 pp test, −0.05 pp dev. Astra: interpretable; seal04 stays diagnostic_only. Results + reviews: docs/programme_20261019/SIMPLIFICATION/wave2/.
   - **Task 2 (value of the correction tools) — DONE, Astra PASS (2026-10-22 15:46).** Old recipe on the old model (wave 1c, 211,451 rows, raw labels) vs the same data under the new filtering (196,227 rows) vs filtered + corrected (167 corrections), all scored on raw AND corrected+filtered references (benchmark 2,232 admitted lines with the correction overlay; internal test 39,434 admitted lines with corrected labels). Result: no measurable improvement from filtering or correcting the initial recipe's own data (benchmark CER 3.66 / 3.66 / 3.66; internal 1.28 / 1.28 / 1.29; differences inside seed noise). Reason: only 167 of 1,071 corrections touch the initial recipe's rows; the 904 accent corrections are on the newly harvested rows. With those rows in training (extra arms), corrections give a small consistent gain (2.08 → 2.05) and the new data itself gives the large one (3.66 → 2.08). Report + reviews: docs/programme_20261019/SIMPLIFICATION/task2/. Cost 44.4 requested GPU-h.
   - **Scaling ladder S1 — DONE, Astra PASS (2026-10-22 17:00).** 8 cells × 3 seeds, all 24 runs complete (74.6 GPU-h). Benchmark CER (seal04 test, raw): ×1 2.61 / 2.49, ×1.5 2.37 / 2.23, ×2 2.24 / 2.10 (208k / 365k rows). Width ×1→×2 = −15.6% relative; nearly doubling the data = another 0.12–0.14 pp at each width; both together 2.61 → 2.10 (−19.5%). Targeted subset: no reliable gain. Same ordering on the cleaned internal test. Astra's next step: measure ×1.5 and ×2 inference latency on the deployment CPU before choosing the production width. Scope: S1 trained on the v3 population (364,871 rows), not v4; 20/24 runs still improving at epoch 8 (no convergence floor claimed). Results + reviews: docs/programme_20261019/SIMPLIFICATION/s1/.

## Method since 21 Oct 10:40
Owner rule: I decide, Sol executes, Astra reviews; no other session. Plan + cut-reviews: docs/programme_20261019/SIMPLIFICATION/. Checkpoints used: CP3B (1 BLOCK → fixed → PASS), CP4 PASS, CP4B review 2 PASS; Sol xhigh pre-checks on v4 and the S1 packet.

## Budget
Wave cap 350 requested GPU-h (owner, 21 Oct). Spent so far ≈ 42 requested GPU-h (wave 2 + S1 preparation); S1 forecast 209 more.

## Needs you
Nothing. Next report: S1 results (after the aggregate) with the results review.
