# L1E — Ensemble gate (A∧B) + Clariden job for B/E inference and L1r recomposition (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head 0472a908 = SF2). No `.git` writes. Do not touch other
worktrees (R0a2 runs in `…-spellcheck-r0`). Local Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`,
`PYTHONPATH=$PWD`. Mac runs: mock only (≤ 200 lines). **DO NOT SUBMIT A JOB**: prepare, mock, deploy, sha-check, `sbatch --test-only`; the
coordinator submits. CSCS cert valid to 2026-10-17 19:18 — if ssh fails, STOP; never refresh. Read
`~/.claude/skills/optimize-apertus-cscs/SKILL.md` "Clariden operating rules". Have it READY by 10:00 Athens (read `date`).

## RESTART NOTE (01:53)
Attempt 1 stopped correctly at 01:51 on `Connection timed out during banner exchange` (see `L1E_REPORT.md`); its work is in the tree —
continue from it. SSH rule refined by the track lead: a transient transport error (banner-exchange/connect timeout, connection reset) may be
retried up to 3 times with 30–60 s backoff; STOP only on authentication/certificate errors or if 3 retries fail. Never refresh the cert.
Re-verify anything that was in flight when the connection dropped (re-hash deployed files) before using it.

## Coordinator ruling (17 Oct)
The L1r gate for the TRAINING waves is **ENSEMBLE_AB**: names from R1 arm A; a slot is ACCEPTED only when arm B predicts the identical mark
set; HOLD on: A/B disagreement, K1 impossible-by-rule flags, every SF2/C2-B01 uncertainty state (R1 UNKNOWN or uncertainty, missing
prediction, detector `localisation_unknown`, `segmentation_uncertain`, unnamed, relevant clipping), and the SF2 edit guard. The detector
contributes ONLY those localisation/segmentation states and apostrophes/quotes; its mark-KIND veto is dropped for this gate. PRESENCE and FULL
stay available; held-out reports PRESENCE and ENSEMBLE_AB side by side. The release manifest must state verbatim: **"A and B share training
data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent pixel signal. Precision
on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a pseudo-label
experiment."**

## Do
1. **Gate:** add ENSEMBLE_AB (and ENSEMBLE_AE as a diagnostic) to `greekocr/labelfix/release_gate.py` — the shared gate, one implementation
   for release, measurement and pages. Tests: A/B disagreement → HOLD; agreement + every uncertainty state → HOLD; agreement + clean →
   ACCEPT; detector kind disagreement alone does NOT hold; edit guard still applies; apostrophes from the detector.
2. **Held-out table:** run the 666 through the shared gate with saved predictions (`artifacts/labelfix_r1/output_3678928/{A,B,E}`
   heldout predictions — B/E held-out predictions exist) → PRESENCE / FULL / ENSEMBLE_AB / ENSEMBLE_AE: corrected / wrong / missed /
   HOLD / new / lines held, against print truth (same instrument as R1 RESULT).
3. **Clariden job `l1e_job.sbatch`** (debug, 1 node, a0140, ≤ 1 h), deployed beside L1-v0
   (`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/`): (a) verify L1-v0's detector shards (`output_3679313/detector/
   shard-*-{detector.jsonl.gz,samples.json,wide.npy}` + receipts) — every line's A windows are stored; if not, re-extract the missing ones
   with the unchanged L1 extraction; (b) arms B and E inference on the stored wide windows (GPU, fp32, the L1 `predictions()` path;
   checkpoints `labelfix_r1_20261016/output_3678928/{B,E}/best.pt`, assert arm ids and sha256); (c) L1r recomposition in-job with the SF2
   shared composer (`scripts/labelfix/clariden/l1r_recompose.py`), producing PRESENCE, FULL and ENSEMBLE_AB overlays + kept/ctrl-subset
   releases (`v2-corrected-presence-r`, `v2-corrected-full-r`, `v2-corrected-ensemble-ab-r`) with per-wave/per-source coverage, exclusion
   receipts, the verbatim caveat, and code/policy/checkpoint hashes; (d) per-step receipts so a timeout leaves results. L1-v0 is never
   modified. Runtime: venv_l1 (detector-free path may use the E3 venv; state which).
4. Mock on ≤ 200 lines (Mac CPU) with the exact entry points, including parity against step 2's held-out decisions for any held-out
   instrument lines used in verification mode. Deploy, `L1E_DEPLOY_SHA256.txt` remote vs local, `sbatch --test-only`.

## Deliverables
Code + tests (all labelfix green), `docs/records/labelfix/spellcheck/clariden/L1E_REPORT.md` (held-out table, mock, timings/estimate, deploy sha
list, test-only output, exact submit command), last line:
`L1E READY: gate ENSEMBLE_AB tests ok; held-out AB corrected …/80 wrong … new … lines held … (PRESENCE 48/2/5/50); mock ok (<n>, parity <k>/<k>); windows stored <all|missing n>; deploy sha256 <a>/<a>; test-only <output>; est <min> min`.
