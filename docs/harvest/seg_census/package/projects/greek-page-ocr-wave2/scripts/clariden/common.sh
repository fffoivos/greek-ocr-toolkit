#!/usr/bin/env bash
# Sourced by allocation entry points. Software was provisioned on the login node.
set -euo pipefail
export GIT_OPTIONAL_LOCKS=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export SLURM_EXPORT_ENV=ALL
export W="${W:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3}"
export E3_REHEARSAL_TAG="${E3_REHEARSAL_TAG:-rehearsal}"
[[ "$E3_REHEARSAL_TAG" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo 'invalid E3_REHEARSAL_TAG' >&2; exit 2; }
E3_REPO="$W/greek-page-ocr"
cd "$E3_REPO"
if [[ -f "$W/runtime.sh" ]]; then
  source "$W/runtime.sh"
else
  E3_PYTHON=("$W/venv/bin/python")
fi
E3_STARTED=$(date +%s)
E3_OUTPUT="$E3_REPO/${1:?output relative to repo required}"
mkdir -p "$E3_OUTPUT" "$W/logs"
e3_receipt() {
  local result=$?
  trap - EXIT
  local receipt_python=("${E3_PYTHON[@]}")
  if [[ "${receipt_python[0]}" == */* && ! -x "${receipt_python[0]}" ]]; then receipt_python=(python3); fi
  "${receipt_python[@]}" - "$E3_OUTPUT/receipt.json" "$E3_STARTED" "$result" <<'PY'
import json, os, socket, subprocess, sys, time
from pathlib import Path
path = Path(sys.argv[1])
receipt = dict(job_id=os.environ.get('SLURM_JOB_ID', 'login'), node=socket.gethostname(),
    partition=os.environ.get('SLURM_JOB_PARTITION', 'login'), account='a0140',
    git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    start=int(sys.argv[2]), end=int(time.time()), exit_code=int(sys.argv[3]))
tmp = path.with_suffix('.tmp'); tmp.write_text(json.dumps(receipt, indent=2)+'\n'); tmp.replace(path)
# Keep previous allocation receipts when a wave resumes.
archive = path.parent/'receipts'/('job_'+receipt['job_id']+'_'+sys.argv[2]+'.json')
archive.parent.mkdir(exist_ok=True); archive.write_text(path.read_text())
PY
  exit "$result"
}
trap e3_receipt EXIT
run_step() {
  srun -A a0140 --partition="${SLURM_JOB_PARTITION:?must run in a Slurm allocation}" \
    --cpu-bind=none --nodes=1 --ntasks=1 "$@"
}
