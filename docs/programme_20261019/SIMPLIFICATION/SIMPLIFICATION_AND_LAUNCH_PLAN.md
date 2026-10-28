# Simplification + launch plan — 21 Oct 2026, 10:50 Athens

Owner rules (21 Oct): I decide, Sol executes, Astra reviews; no other session. Reasonable, not perfect. Astra cut-reviews: `logs/simp_census_final.md` (CUT 17 / KEEP 16), `logs/simp_wave2_final.md` (CUT 5 / KEEP 12), `logs/simp_s1_final.md` (CUT 6 / KEEP 10) under `~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/`.

What stays everywhere: sha-verified deploy (deployed bytes = reviewed commit); no benchmark exposure (seal04) in any training set; one smoke before any production run; GPU-hour caps (wave 150 / series 120 requested); one Astra checkpoint before each production launch and one on results. Everything else below is cut.

## Cuts (from the three reviews)
- Census: no more verifier/scheduler reruns, no audits, no cross-session acceptance lists, no book-start/sstat narratives, no health/cache-warming probes, no flip_report, no new package. Finish the running ledger; the only repair is REL4b's stale tool-manifest pin (aa196462 → 04920d8f).
- Wave 2: one CPU preparation job (deploy + inputs builder + inventory04 + seal04 bind + verify) and one GPU smoke in the wave-1c environment; REVIEW_INPUTS = the smoke's own log + hashes; no separate production preflight.
- S1: one commit (keep H1, module-entry repair, environment, accounting, factory-asset repair; remove freshness clocks, broad path scans, separate witness/qualification roots); one deploy to /capstor (reuse the reconciled inputs); one GPU acceptance allocation = runtime check + 8-cell smoke + split witness + full-profile timing of the heaviest cell; one review packet.

## Launch sequences and checkpoints

### A. Census → release v4 (RUNNER1, Sol; brief `RUNNER1_v4_simplified.md`)
1. 3711087 terminal → read accounting/log/ledger counts; confirm no writer alive.
2. If UNPROCESSED > 0: plain-execute resume in the same ledger (same attempt, same config). Do not re-run submit_chain.
3. If INFRA_ERROR > 0 after that: external retry driver (test-only, then execute). Skip if 0.
4. One final readout (--expect-pipeline-version 0.3.3): 592,466 rows, invariants PASS, INFRA_ERROR 0.
5. CROPS4C smoke → full, bound to the final generation.
6. REL4b: fix the stale manifest pin (one scoped commit in sol-recut), bind census + sf7 + crop receipts, run; handoff receipt.
7. **Checkpoint CP3B-v4** (Astra, folded into B's CP3B): release counts vs census, exclusions, seal04 protection, zero crop gaps, spot-check of crop / raw label / sf7 examples.
Timeout rule: if 3711087 hits 12:50 with UNPROCESSED > 0 → step 2. Never accept a partial v4.

### B. Wave 2 on v4 (RUNNER2, Sol; brief `RUNNER2_wave2_simplified.md` in greek-page-ocr-e4w2v4)
0. Now (before v4): port the wave-1c environment (S1-N style: no LD_LIBRARY_PATH/LD_PRELOAD, venv python as runtime.sh; sbatch `--account=a0140`, whole-minute limits), remove the separate production preflight and the receipt-age rules from the scripts, keep the inputs builder; commit.
1. v4 exists → one CPU preparation job: deploy into one fresh root (sha of the committed tree), build linefactory, inputs builder (ctrl / add / add_corr), inventory04, seal04 bind + exposure recount, input verification; counts recorded.
2. One GPU smoke (debug, ≤ 30 min): runtime check, then native import → training → checkpoint → evaluation → aggregation; log = REVIEW_INPUTS.
3. **Checkpoint CP3B** (Astra): package + smoke + v4 release acceptance (A.7) in one review.
4. Launch the three arm allocations (seeds 0/1/2 each); submission receipts; sacct costs.
5. Aggregate when all three succeed.
6. **Checkpoint CP4** (Astra): nine runs + preregistered contrasts; diagnostic_only label of seal04 stays.

### C. Scaling ladder S1 (RUNNER3, Sol; brief `RUNNER3_s1_simplified.md` in greek-page-ocr-s1)
0. Now: one commit that keeps H1, module-entry repair, environment, accounting, factory-asset repair and removes the cut gates; adapters bound to the reviewed source.
1. One deploy to /capstor (archive source; reuse the reconciled inputs; build in the final root; factory exercised with its own assets).
2. One GPU acceptance allocation: runtime check → 8-cell smoke + split witness → full-profile timing/checkpoint/resume/evaluation of the heaviest cell (bounded).
3. One review packet: measurements, limits, segment plan, local H1 evidence, cumulative accounting, + wave-2 CP4 PASS when it exists.
4. **Checkpoint CP4B review 2** (Astra), after B's CP4.
5. Launch the 8-cell graph; account at continuation boundaries. If measured costs exceed a cap, launch stays blocked (no dropping cells, no raising caps).
Cluster jobs for C run after B's smoke is in, so B keeps the debug slots.

## Who does what
- Sol runners execute every step; each STOPs at a submit point with `NEXT_SUBMIT.sh` (ssh-wrapped, detached for chains) and a 5-line `STATUS.md`; I submit, commit the runner's files, relaunch with a `RESUME:` line.
- Astra: CP3B (B.3, includes v4 acceptance), CP4 (B.6), CP4B review 2 (C.4). Nothing else.
- Owner: nothing, unless a cap is exceeded.

## Reviewer assignment (owner, 21 Oct 11:15)
- Intermediate checkpoints = **Sol xhigh** (read-only review run): v4 release acceptance (A.7, before wave-2 prep uses v4); wave-2 smoke readiness (B.2 → before CP3B); S1 review packet pre-check (C.3).
- Prelaunch checkpoints and final-results reviews = **Astra xhigh**: CP3B (before the 9 wave-2 runs), CP4B review 2 (before the 8 S1 cells), CP4 (wave-2 results).

## Amendment 21 Oct 17:15 (owner question "simplified enough?")
- The Sol xhigh wave-2 smoke-readiness check (B.2 → CP3B) is DROPPED: Astra CP3B reads the same smoke log. Sequence is smoke → CP3B → runs → CP4.
- The detached-chain launch wrapper stays (SSH drops are real), but no new wrapper features; failures in it are fixed in one pass.

## Budget amendment 21 Oct 18:31 (owner): wave cap 150 → **350 requested GPU-h** (+200); series caps 120 unchanged.

## Section B rewritten (owner, 22 Oct 10:30) — task 2 as defined by the owner
Task 2 = "correct and filter the data of the initial recipe to test if there is improvement with the model" (the value of the correction tools). The arms must be:
1. **as-is** — the initial recipe exactly as last run (wave 1c): its full training data, unfiltered, raw labels. Baseline. Use the existing wave-1c checkpoints if they are three seeds of the exact recipe; otherwise retrain as is (3 seeds, ~12 GPU-h).
2. **filtered** — the same data with the census_06 filtering only (= the arm previously called "add").
3. **filtered + corrected** — the same with the corrections applied to the labels (= "add_corr").
Every arm is scored on two variants of every reference: **raw** (as sealed) and **cleaned** (benchmark seal04 with the correction overlay applied to its labels; internal test = census-admitted rows with corrected labels). The "ctrl" arm (filtered old data without the release rows) is reported as an extra, not as the baseline.
Deliverable: one table as-is / filtered / filtered+corrected × raw / cleaned references, Astra-reviewed (xhigh), then the report to the owner. The earlier wave-2 RESULTS.md and CP4 stand as the data-quantity ablation; they do not answer task 2 by themselves.
Task 3 (S1 ladder on filtered + corrected rows) is unchanged; its 24 models are scored on both reference variants as well.

### Section B, data facts established 22 Oct 10:50
- The initial recipe (wave 1c) trained on **211,451 old-admitted rows** (collection v2 train, earlier admission), raw labels, seeds 0/1/2 — not on the release rows. Its checkpoints exist and are scored as the **as-is** baseline (no retrain).
- Therefore the strict task-2 arms are: **as-is** (wave 1c) → **filtered** = ctrl (196,227 census_06 ADMIT rows, raw labels; already trained) → **filtered + corrected** = **ctrl_corr** (the ctrl rows with the corrections overlay; new arm, 3 seeds, ~12 GPU-h).
- add / add_corr (with the release rows) remain in the table as the data-quantity extras.
- References: raw and cleaned (v2_test cleaned = 39,434 ADMIT rows with 426 corrected labels, numerics slice 175 of the 221; seal04 overlay changes 6 test + 1 dev labels).
