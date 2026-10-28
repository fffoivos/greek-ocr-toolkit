#!/bin/bash
# REVIEW ONLY: do not run until the owner authorizes HF repository creation/upload.
# Phase 1 does not execute this file. No credentials are stored in it.
set -euo pipefail
set +x

TASK_REPO="/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next"
MAC_HF_STAGE="${MAC_HF_STAGE:-$HOME/Projects/hf-staging/greek-ocr-lines}"
cd "$TASK_REPO"

# Current restricted session packaged at /private/tmp/hf-staging/greek-ocr-lines.
# Later durable relocation, on the same filesystem, before publication:
# mkdir -p "$HOME/Projects/hf-staging"
# test ! -e "$HOME/Projects/hf-staging/greek-ocr-lines"
# mv /private/tmp/hf-staging/greek-ocr-lines "$HOME/Projects/hf-staging/"
# mv /private/tmp/hf-staging/greek-ocr-lines.receipts "$HOME/Projects/hf-staging/"
# This script does not move/delete source data or stage Git metadata.

# Offline full readback first. This checks the manifest, all embedded payloads,
# all closed shard sizes/SHA256s and the three source joins before any HF call.
python3 scripts/line_registry/validate_mac_package.py \
  --root "$MAC_HF_STAGE" \
  --remote out/runner4/HF_PHASE1_REMOTE_JOINS.json \
  --legacy-representation out/runner4/RESPONSE_REPRESENTATION_PROBE.json \
  --receipt out/runner4/HF_PHASE1_PREUPLOAD_READBACK.json

# Locally verified huggingface_hub CLI 1.1.6 syntax. Recheck on the upload host.
hf version
HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)" \
  hf repo create fffoivos/greek-ocr-lines --repo-type dataset --private --exist-ok

# --private does not change an existing public repository. Fail if not private.
# HfApi uses the command's ephemeral HF_TOKEN environment; never login/persist it.
HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)" \
  python3 - <<'PY'
from huggingface_hub import HfApi
info = HfApi().repo_info('fffoivos/greek-ocr-lines', repo_type='dataset')
if info.private is not True:
    raise SystemExit('STOP: fffoivos/greek-ocr-lines is not verified private')
print('Verified private dataset: fffoivos/greek-ocr-lines')
PY

HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)" \
  hf repo branch create fffoivos/greek-ocr-lines staging-v4 \
  --repo-type dataset --exist-ok

# Serialize this origin before the later, separately authorized Clariden upload.
# Root contains only manifest-listed payloads. Do not tag this partial revision v4.
HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)" \
  hf upload-large-folder fffoivos/greek-ocr-lines "$MAC_HF_STAGE" \
  --repo-type dataset --revision staging-v4 --num-workers 2

# Resolve immutable upload commit; record only public identifiers, no token.
HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)" \
  python3 - <<'PY'
from datetime import datetime, timezone
from huggingface_hub import HfApi
import json
from pathlib import Path
info = HfApi().repo_info('fffoivos/greek-ocr-lines',repo_type='dataset',revision='staging-v4')
assert info.private is True
receipt = dict(repo_id='fffoivos/greek-ocr-lines',repo_type='dataset',private=True,
    revision='staging-v4',commit=info.sha,at=datetime.now(timezone.utc).isoformat(),
    state='Mac upload only; remote artifact/payload readback and Clariden handoff still required')
Path('out/runner4/HF_MAC_UPLOAD_COMMIT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
PY
# Stop here. No Clariden download/build, release seal or tag in this script.
