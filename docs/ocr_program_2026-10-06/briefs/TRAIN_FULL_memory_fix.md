# Sol task — Stage C host-memory growth: diagnose, fix, resume (27 Oct, coordinator)

## What happened (raw evidence; re-derive it yourself)
Full runs (seal 7e8a497f21527b90, attempt /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-013-stage-c-sel, jobs w1-full 3761269, w1.5-full 3761270, w2-full 3761274, all on nid007398, started 03:41 CET / 04:41 EET) ran for ~3 h.
- w1-full 3761269 FAILED 1:0 at 03:01:52 elapsed. srun-3761269.log ends `[2026-10-27T06:42:49.661] error: Detected 2 oom_kill events in StepId=3761269.0`. LIVE step 6000 / 1,535,766 lines; CHECKPOINT_COST.json step 6001 written 06:42 (57,468,963 B segment.pt); SEGMENT_TRACE global_step 6001, draw_position 1,536,022, epoch 1 (6198 updates/epoch).
- MEMORY_3761269_*.json (PSS, sampled): root process 0.6 → 11.5 (9 min) → 15.1 (34) → 17.1 (60) → 18.9 (103) → 19.2 GB (181); each of the 6 persistent DataLoader workers 6.3 (9 min) → 9.7 (34) → 12.5 (60) → 15.8 (103) → 16.4 GB (181). Tree PSS 55 GB at 13 min, 113 GB at 101 min, flat ~116–117.5 GB from 114 min (the 110 GiB = 118,111,600,640 B cgroup limit). w1.5 and w2 show the same shape (w2 lower: 98 GB at 183 min).
- From ~114 min all three lanes crawled at ~1/40 of the normal update rate (w1.5 5260→5375 steps, w2 17120→17349 in ~70 min; BATCH_TIMING mean 0.82 s/update before).
- The selection smoke (receipts out/TRAIN_FULL_v1/receipts_stage_c_sel_smoke/, peak 42.5 GB) was too short to show the growth.
- Node nid007398: RealMemory 870,000 MB, 288 CPUs, 4 GPUs.
- At 06:47 CET the coordinator sent the reviewed durable yield (`scancel --signal=TERM --batch`) to 3761270 and 3761274 (STOP files signal-controls/3761270-0.stop, 3761274-0.stop); their outcome (exit 75 → requeue, or failure) will be appended to docs/programme_20261025/TRAIN_FULL_v1/EXECUTION_STATE.md.

**Outcome of the yields (all three lanes are now FAILED; no GPU is in use):**
- w1.5-full 3761270: log shows `[segment] durable checkpoint; planned yield exit 75` then `[2026-10-27T06:47:39.671] error: Detected 1 oom_kill event` → FAILED 1:0 (no requeue). SEGMENT_TRACE global_step 5489, draw_position 1,404,950; CHECKPOINT_COST step 5489 (112,882,467 B).
- w2-full 3761274: FAILED 1:0 at 03:08:06 elapsed (see its srun log / SEGMENT_TRACE in the local copy).
- So the OOM also hits at/after a durable checkpoint during the planned yield exit: the resume procedure must cover FAILED lanes with a completed durable checkpoint, and the exit path itself must not OOM.

**Local copies (you have no network):** out/TRAIN_FULL_v1/receipts_stage_c_full_oom/ — runs/<lane>/ (every run file under 3 MB: MEMORY_*.json sample series, LIVE, SEGMENT_TRACE, CHECKPOINT_COST, BATCH_TIMING, loss_eval.jsonl, loss_checkpoints/ and loss_eval/ listings, RUN_BINDING, CLAIM, srun logs; segment.pt / data_provenance.json excluded), signal-controls/, submit-controls/, PLAN.json, SACCT_AT_INCIDENT.txt, NODE_nid007398.txt. The sealed package source is docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/. If something you need is only on Clariden, list the exact read-only command for the coordinator in your report.

## Tasks
1. **Root cause from the code** (stage_c_package/, vendor/train/data.py, full_hook.py, stage_c.py, loss/eval loaders). Is this copy-on-write unsharing of Python-object data in forked persistent workers (bounded by the parent's heap) or an unbounded leak (root or workers)? Name the objects and the lines. Explain the root growth 11.5 → 19.2 GB too.
2. **Steady-state bound per width**, with the evidence/argument, across a whole run (8 epochs, loss evals every 50k lines, CER evals at 25/50/75/100%, yields/resumes). If the receipts and code cannot bound it, design the cheapest measurement that can (e.g. a CPU-only loader soak over ≥1 full epoch with the real data and worker count) as a ready-to-run script + COMMANDS block; the coordinator runs it.
3. **Fix — preference order:**
   (A) No change to the sealed package or to training semantics: resubmit/requeue with a larger `--mem` (sbatch CLI override and/or `scontrol update` of a pending job), sized from (2) with margin, keeping three lanes plus headroom within the 870 GB node. State exactly what changes versus the reviewed PLAN and why existing durable state remains valid.
   (B) Only if (A) is unsafe (unbounded growth): a minimal package change that removes the growth without changing what is drawn or computed (same draw chain, same batches, same math), with a proof/test that batches are identical, and a statement of whether the existing runs can resume under it.
4. **Resume the three lanes, never restart from zero unless resume is impossible.** w1-full is FAILED (OOM at the instant of/after the step-6001 segment write): verify from the run dir whether its latest durable state is complete and consistent (segment.pt vs SEGMENT_TRACE vs loss journal vs loss_checkpoints), and give the exact resubmission procedure for that lane against the same attempt (claims/locks/INTENT/submit-controls handling as the code requires). Same for w1.5/w2 if their yield fails. Provide a helper script (same style as the k13_*.sh helpers: env header + COMMANDS block) and add the block(s) to out/TRAIN_FULL_v1/COMMANDS.md.
5. **Tests:** mock/fixture tests for the resubmission path and for whatever (A)/(B) changes; full existing test suite must still pass.
6. **Accounting:** GPU-h spent so far in Stage C (smokes + these ~3 h × 3), and the updated forecast to completion vs the owner's 82 GPU-h approval (low/expected/high). Flag clearly if the expected or high total exceeds 82.

## Deliverables
docs/programme_20261025/TRAIN_FULL_v1/STAGE_C_MEMORY_FIX.md (root cause, bound, chosen fix, resume procedure, accounting, open risks), helper script(s), COMMANDS.md block(s), tests. No remote writes, no submissions, no rm, do not touch the uncommitted unrelated files in the repo. End with "MEMORY FIX READY".
