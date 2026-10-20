#!/usr/bin/env bash
# Coordinator only. Package creation never invokes this file.
set -euo pipefail
B="$(cd "$(dirname "$0")" && pwd)"
: "${REL4_CONFIG:?}" "${ATTEMPT:?}" "${CENSUS_CODE:?}" "${CENSUS_MANIFEST:?}" "${PROJECTS_SUMS_ROOT:?}" "${PROJECTS_SHA256:?}"
[[ "$ATTEMPT" =~ ^[A-Za-z0-9_-]+$ ]]
export P1POOL_PACKAGE="$B"
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
[[ ! -e "$W/scaling_w3/p1pool_attempts/$ATTEMPT" && ! -e "$W/p1pool_crops/$ATTEMPT" ]]
bash "$B/VERIFY.sh" inputs --rel4-config "$REL4_CONFIG"
"$W/venv_l1/bin/python" -B -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["tests"]["real_head_parents"]==r["tests"]["required_parents"]==5, "required real five-parent tests pending"' "$B/P1POOL_RECEIPT.json"
mkdir -p "$W/scaling_w3/p1pool_logs"
select_job=$(sbatch --parsable --export=ALL --output="$W/scaling_w3/p1pool_logs/$ATTEMPT-select-%j.log" "$B/select.sbatch")
[[ "$select_job" =~ ^[0-9]+$ ]]
crops_job=$(sbatch --parsable --export=ALL --dependency="afterok:$select_job" --output="$W/scaling_w3/p1pool_logs/$ATTEMPT-crops-%j.log" "$B/crops.sbatch")
printf 'select %s crops %s dependency afterok:%s\n' "$select_job" "$crops_job" "$select_job"
