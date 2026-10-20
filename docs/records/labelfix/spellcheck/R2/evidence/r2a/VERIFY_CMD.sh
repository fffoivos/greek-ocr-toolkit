#!/bin/sh
set -eu
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r2prep
export GIT_OPTIONAL_LOCKS=0
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1e/scripts/ops/verify_deploy.py \
  --repo "$PWD" --commit "$(git rev-parse HEAD)" \
  --sha-file R2A_DEPLOY_SHA256.txt --remote-root /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017 \
  --sbatch scripts/labelfix/clariden/r2a_job.sbatch --sbatch-args=--time=81 \
  --out docs/labelfix/spellcheck/R2/evidence/r2a/verify_deploy.json
