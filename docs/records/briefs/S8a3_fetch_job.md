# S8a3 — Package the DEV evidence extraction as a Clariden debug job (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace/rules: as S8a/S8a2 (read both). Head c4734407. **DO NOT SUBMIT** and do NOT run the extraction on the login node (the login-node
budget is exhausted; the STOP marker stays). Prepare only: commit-ready scripts, mock, deploy, sha check, `sbatch --test-only`. SSH transient
errors retry ≤ 3 with backoff (transport is flaky tonight: Ela read timeouts, banner timeouts); auth/cert error STOP; never refresh the cert.

## Job
Wrap `scripts/labelfix/s8_fetch_l1m.py` as a one-node CPU debug job (a0140, ≤ 20 min, 16–32 workers over shards), **resuming from the existing
checkpoint** `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/partial.json.gz` (B/E done for 863/973 shards,
runtime 527/600; A 0, alignments 0/166) — verify its request sha against `request.json` before resuming. Output: complete `remote.json.gz`
+ receipt in that same folder (never inside L1/L1E/L1R outputs). Read-only on all inputs; no inference. Runtime: venv_l1 python or the system
python3 if the helper is stdlib-only (state which).

## Before submission
Mock: run the job's entry point locally on a tiny synthetic shard set shaped like the real inputs, including resume-from-checkpoint; tests
(`tests/labelfix/test_s8_fetch_job.py`; all labelfix green); deploy to `…/labelfix_l1_20261017/s8_dev_extract/job/`, `S8F_DEPLOY_SHA256.txt`
remote vs local; `sbatch --test-only`.

## Deliverables
`docs/records/labelfix/spellcheck/S8a3_REPORT.md` with the exact coordinator submit command and the pull command for `remote.json.gz`; last line:
`S8a3 READY: resume from <n>/973 B/E; mock ok; deploy sha256 <a>/<a>; test-only <output>; est <min> min`.
