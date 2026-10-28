# ASTRA — prelaunch review of TRAIN_FULL_v1 (Gennadius variant), 25 Oct 22:57 Europe/Athens

You are the independent CERTIFIER (implementer = Sol; coordinator = claude-opus-5-5). Adversarial, firsthand, recompute numbers, report failing numbers raw. READ-ONLY except your final report; no network, SSH, jobs; no background jobs.

## What is being certified
Launch of one training run on Clariden: width ×2 S1 recipe (best S1 cell w2/ref_364871/s0) on v4 + harvest-with-Gennadius, 793,227 unique real train rows + equal synthetic draws, 8 full real passes = 198,312 updates, checkpoint + four-instrument (seal04 dev/test, harvest dev/test) CTC loss + CER every 50,000 updates and at the end; preemptable + requeue + exact resume; ~24.9 GPU-h projected. Owner 25 Oct: "a training run on the whole dataset (~800k?) with val loss, and test loss on checkpoints of 50k" and later "we go to training" — launch proceeds on your PASS.

## Read
- Brief and all RESUMEs: docs/ocr_program_2026-10-06/briefs/TRAIN_FULL_v1_brief.md
- PLAN + recipe table: docs/programme_20261025/TRAIN_FULL_v1/PLAN.md, package/recipe.json, package/ (code + tests), out/TRAIN_FULL_v1/COMMANDS.md
- Real receipts fetched from Clariden: out/TRAIN_FULL_v1/receipts_005/ (AUDIT.json, AUDIT_COMPLETE, AUDIT_REUSE, PREPARE_COMPLETE, runtime.json, OWNER_READOUT(+_BEFORE_SMOKE), SMOKE_IDENTITY.json = BIT_IDENTICAL, smoke slurm logs, sacct proofs: smoke 3748974 COMPLETED 428 s Restarts 0; 3748976 COMPLETED 293 s Restarts 1; prepare 3748345 COMPLETED 35m13s; audit 3748169 COMPLETED). Payload 294c3458c0d1fbbb… deployed and verified on both sides.

## Check (raw numbers)
1. Recipe table: every parameter vs S1 w2/ref_364871/s0; flagged changes are exactly: data population, epoch_rows/horizon (2× unique real train; 198,312 updates; OneCycle over that horizon), eval/checkpoint cadence, patience disabled, nonletter 'furniture' fallback applied to 30,104 harvest numerics lines (S1 had 13,767 furniture lines) — anything else changed silently is a BLOCKER.
2. Data: counts reconcile (audit unique 862,423; train 793,227 / dev 16,350 / test 52,846; S1 resolution 364,871/364,871; 3 train↔eval removals; prepare wrote 497,554/497,554, 0 drops); leakage controls real; synthetic fraction 1/2 and parliament cap 1/4 as in S1.
3. Evaluation: test numbers never select/stop; loss = same CTC as training; eval cannot perturb the training trajectory (RNG/mode restore); checkpoint archive at 50k/100k/150k/198,312.
4. Resume/requeue: smoke evidence really shows a scheduler requeue (restart count, same job id) and BIT_IDENTICAL state/trace — not mocked.
5. Launch command/segmenting: preemptable --requeue, 1 GPU, ≤24 h segments, no afterok on purged ids, budget statement honest (historical 118.995/350, not live).
6. Known open methodological point (do not block on it unless you judge it a defect of THIS package): LR 1e-4 / batch 64 were inherited from the O5 fine-tune recipe and never tuned for from-scratch or for width ×2; coordinator proposes a separate short LR screen in parallel.
## Disposition
BLOCKER/HIGH block launch until fixed; MEDIUM/LOW logged.
## Deliverable
Write docs/programme_20261025/TRAIN_FULL_v1/ASTRA_PRELAUNCH_REVIEW.md: header → one-line verdict → findings F1… ([BLOCKER]/[HIGH]/[MEDIUM]/[LOW], path/number, failure scenario, fix) → verified-good. Last line exactly: `VERDICT: <PASS|HOLD> | BLOCKERS: <n> | HIGH: <n>`
