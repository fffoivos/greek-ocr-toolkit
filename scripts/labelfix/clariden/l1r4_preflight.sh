#!/usr/bin/env bash
# Clariden-only login preflight. Hash receipts; never decode production frames.
set -euo pipefail
L1R4_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R4_ROOT="$L1R4_BASE/l1r_sf6f"
L1R4_PYTHON=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
cd "$L1R4_ROOT"
mkdir -p preflight logs
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$L1R4_ROOT"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=''
sha256sum --check L1R4_DEPLOY_SHA256.txt > preflight/deploy_before.log
sha256sum --check L1R4_EXTERNAL_SHA256.txt > preflight/external_verify.log
(cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1; sha256sum --check --quiet "$L1R4_BASE/runtime/L1_scipy_SHA256.txt")
# Metadata + sealed shard SHA checks only; actual line reconstruction is Job 1.
"$L1R4_PYTHON" -B -u - <<'PY'
from pathlib import Path
from scripts.labelfix.clariden.l1r4_join import verify_receipt
from scripts.labelfix.clariden.l1r_recompose_ext import load, atomic_json, code_sources
from greekocr.labelfix.release_gate import policy_binding
cfg=load('config/l1r4_job.json')
r=verify_receipt(cfg['l1f'])
for k in ('final','plan','upstream'): r.pop(k)
atomic_json('preflight/l1f_final_verification.json',r)
atomic_json('preflight/policy.json',policy_binding())
atomic_json('preflight/code_sources.json',code_sources())
for kind,key in (('release_root','release_receipt_sha256'),('census_root','census_receipt_sha256')):
 from scripts.labelfix.clariden.l1c_census import sha256
 assert sha256(Path(cfg['baseline'][kind])/'receipt.json')==cfg['baseline'][key]
PY
"$L1R4_PYTHON" -B -u scripts/labelfix/clariden/l1r_recompose_ext.py \
  --config config/l1r4_job.json --verify-only --workers 4 \
  --out preflight/input_verification.json > preflight/input_verification.log
bash -n scripts/labelfix/clariden/l1r4_job.sbatch
bash -n scripts/labelfix/clariden/l1r4_census_job.sbatch
sinfo -p debug -o '%P %a %l %D' > preflight/debug_partition.txt
# Preserve the exact dependency in both scheduler simulations. Job 2 uses the
# completed baseline Job 1 only as a job-shaped stand-in, never as a submission.
set +e
sbatch --test-only --dependency=afterok:3680752 scripts/labelfix/clariden/l1r4_job.sbatch > preflight/job1_test_only.log 2>&1
L1R4_J1=$?
sbatch --test-only --dependency=afterok:3680729 scripts/labelfix/clariden/l1r4_census_job.sbatch 3680729 > preflight/job2_test_only.log 2>&1
L1R4_J2=$?
set -e
printf '{"job1_dependency_exit":%s,"job2_dependency_exit":%s,"submitted_jobs":[]}\n' "$L1R4_J1" "$L1R4_J2" > preflight/test_only_status.json
if [[ "$L1R4_J1" != 0 ]] && grep -Eiq 'dependenc|invalid job id' preflight/job1_test_only.log; then
  sbatch --test-only scripts/labelfix/clariden/l1r4_job.sbatch > preflight/job1_resource_test_only.log 2>&1
  L1R4_J1=0
fi
if [[ "$L1R4_J2" != 0 ]] && grep -Eiq 'dependenc|invalid job id' preflight/job2_test_only.log; then
  sbatch --test-only scripts/labelfix/clariden/l1r4_census_job.sbatch 3680729 > preflight/job2_resource_test_only.log 2>&1
  L1R4_J2=0
fi
sha256sum --check L1R4_DEPLOY_SHA256.txt > preflight/deploy_after.log
squeue -u fffoivos > preflight/squeue_after.txt
# Any dependency-only scheduler refusal is retained verbatim for the report.
# Other errors remain failures and may not be represented as READY.
[[ "$L1R4_J1" == 0 && "$L1R4_J2" == 0 ]]
