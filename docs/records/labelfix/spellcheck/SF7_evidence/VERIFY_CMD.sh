#!/usr/bin/env bash
# Preregistration sha256: 64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d
# Run after the coordinator commits LEAD_COMMIT_PATHS.txt. Never submits.
set -euo pipefail
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1e/scripts/ops/verify_deploy.py \
  --repo "$PWD" --commit "$(git rev-parse HEAD)" \
  --sha-file SF7_DEPLOY_SHA256.txt \
  --remote-root /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017 \
  --sbatch scripts/labelfix/clariden/sf7_job.sbatch \
  --out docs/labelfix/spellcheck/SF7_evidence/verify_deploy.json
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B - <<'PY'
import json
from pathlib import Path
p=Path('docs/labelfix/spellcheck/SF7_evidence/verify_deploy.json')
r=json.loads(p.read_text())
r['preregistration_sha256']='64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d'
p.write_text(json.dumps(r,indent=2)+'\n')
PY
