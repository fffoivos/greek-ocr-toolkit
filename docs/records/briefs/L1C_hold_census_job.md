# L1C — Per-wave HOLD-reason census of the L1R releases: analysis job (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-l1r`, branch `opus/spellcheck-l1r`, head 4e6d3e2c). No `.git` writes. Do not touch
other worktrees. **Analysis only**: no gate/detector/reader code changes (the gate is frozen at sf4-release-v1); this job only reads L1R's
outputs. **DO NOT SUBMIT**: prepare, mock, deploy, sha-check, `sbatch --test-only`; the coordinator submits after L1R (job 3679725) completes.
SSH transient errors retry ≤ 3; auth/cert error STOP; never refresh the cert (valid to 19:18). Read `~/.claude/skills/optimize-apertus-cscs/SKILL.md`.

## Job (debug, a0140, CPU, one node, ≤ 30 min)
Read L1R's output directory (`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf4/output_<L1R jobid>/` — take the job id as a
parameter; verify its receipts/hashes first) and, for each release mode (PRESENCE, FULL, ENSEMBLE_AB) × wave (round1, round2, parliament,
vouli, mixed, openarchives) and per source: (a) slot counts per exact hold reason; (b) lines held for each exact reason ALONE; (c) top-10 exact
reason sets with line counts; (d) lines held per reason family (localisation/segmentation, clipping, K1, edit-guard, A/B disagreement, kind
disagreement, R1 uncertainty). Multiprocess over shards; per-shard partial receipts so a timeout leaves results. Output a small aggregate
directory (JSON + a `CENSUS.md` table), hashes in a receipt; nothing large leaves Clariden.

## Before submission
Mock on the 64-line verification runtime outputs (or a small synthetic L1R-shaped fixture) with the exact entry point; hand-check two lines'
counts; tests (`tests/labelfix/test_l1c.py`, all labelfix green); deploy beside L1R (`…/l1r_sf4/l1c/`), `L1C_DEPLOY_SHA256.txt`, `sbatch --test-only`.

## Deliverables
`docs/records/labelfix/spellcheck/clariden/L1C_REPORT.md` (mock, deploy sha list, test-only output, submit command taking the L1R job id), last line:
`L1C READY: analysis-only; mock ok; deploy sha256 <a>/<a>; test-only <output>; est <min> min`.
