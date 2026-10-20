#!/usr/bin/env bash
# Coordinator: run after committing LEAD_COMMIT_PATHS.txt. Never submits.
set -euo pipefail
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
 /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1e/scripts/ops/verify_deploy.py \
 --repo "$PWD" --commit "$(git rev-parse HEAD)" \
 --sha-file TR2_DEPLOY_SHA256.txt \
 --remote-root /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019 \
 --sbatch scripts/labelfix/clariden/tr2_job.sbatch \
 --allow-untracked 'artifacts/labelfix_l1e/*' \
 --out docs/labelfix/spellcheck/TR2_evidence/verify_deploy.json
