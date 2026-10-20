#!/usr/bin/env bash
# REVIEW ONLY. NOT EXECUTED IN B. Coordinator authorization is required for jobs.
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PRE_ID=de597753a70a5d6d
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$PRE_ID/docs/harvest/census06"
export SF7_BINDINGS_FILE="$W/census_06_20261020/sf7-bindings.json"
export SF7_BIND_WORK="$W/census_06_20261020/binding/sf7-001" # must not exist
# Populate SF7_BINDINGS_FILE with actual per-parent full-result paths and SHA256s.
# bind_sf7.sbatch expands that JSON, in its four-CPU allocation, to exactly:
# "$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/bind_sf7.py" \
#   <collection-v2-train full-file> <sha256> \
#   <collection-v2-dev full-file> <sha256> \
#   <collection-v2-test full-file> <sha256> \
#   <collect-v3-W1-20261018-0524 full-file> <sha256> \
#   <collect-v3-W2-20261018-0524 full-file> <sha256> --work "$SF7_BIND_WORK"
mkdir -p "$W/census_06_20261020/attempts" "$W/census_06_20261020/logs"
BIND_JOB=$(sbatch --parsable --account=a0140 --partition=normal --time=00:30:00 \
  --chdir="$W/census_06_20261020" --output="$W/census_06_20261020/logs/binding-%j.log" \
  --export=ALL "$CENSUS06_BUNDLE/bind_sf7.sbatch")
printf 'binding=%s\n' "$BIND_JOB"
# STOP: wait for COMPLETED, review coverage, all five loader PASSes and elapsed time.
# The binder fills config/INPUTS, removes pending entries, rebuilds the package/id,
# deploys to NEW code/<BOUND_ID>/ and reads back every payload SHA. PRE_ID is immutable.
# Import stage config, INPUTS, binding report, package_id and manifests for lead commit.
# STOP: lead review/commit; clean verifier tree for that commit; re-readback code and
# inputs (including SF7), rehash cyrillic, unchanged verifier x4, test-only smoke/full
# x4 against BOUND_ID, then binding_state --submit and real SF7 head test.
# Do not continue on the strength of pre-binding B receipts.
BOUND_ID=$(python3 -B -c 'import json,os,pathlib; print(json.loads((pathlib.Path(os.environ["SF7_BIND_WORK"])/"stage/docs/harvest/census06/package_id.json").read_text())["package_id"])')
[[ "$BOUND_ID" != "$PRE_ID" ]]
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$BOUND_ID/docs/harvest/census06"
"$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/binding_state.py" --submit
# Run real-head loader test in the coordinator's CPU allocation, not on login:
# "$W/venv_l1/bin/python" -B -m pytest -q -p no:cacheprovider \
#   --basetemp="$SF7_BIND_WORK/head-test" "$CENSUS06_BUNDLE/test_pipeline_033.py::test_sf7_head_sample"
unset CENSUS06_RUN CENSUS06_READOUT_OUT CENSUS06_CONFIG CENSUS06_BASELINE
export CENSUS06_SPLIT_FILE="$W/census_06_20261020/inputs/row_split.jsonl.gz"
export CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS06_ATTEMPT=smoke-split-002 CENSUS06_EXPECT_ROWS=200
bash "$CENSUS06_BUNDLE/submit_chain.sh" --account=a0140 --partition=debug --time=00:30:00
# regression -> afterok parity -> afterok census -> afterok readout.
# STOP for coordinator review: pipeline 0.3.3, 200 rows, no INFRA_ERROR, all
# invariants PASS, no held-out leaks; inspect polytonic counts, reasons, edits,
# head/full-loader coverage and measured timing before authorizing full.
export E4_SMOKE=0 CENSUS06_ATTEMPT=full-split-002 CENSUS06_EXPECT_ROWS=592466
export CENSUS06_BASELINE="$W/census_05_20261020/attempts/full-split-001/summary.json"
bash "$CENSUS06_BUNDLE/submit_chain.sh" --account=a0140 --partition=normal
# Packaged time limits: regression/parity 00:05:00; census 04:00:00;
# readout 00:30:00. Same afterok chain. Record actual returned IDs.
# Readout is a sibling: attempts/full-split-002.readout/, outside the census run.
# jobs/readout.sbatch derives PIPELINE_VERSION from the bound package (=0.3.3),
# then runs the following inside its allocated afterok readout job (do not duplicate):
# srun -A a0140 --partition=normal --cpu-bind=none --nodes=1 --ntasks=1 \
#   "$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/readout/census_readout.py" \
#   --expect-pipeline-version 0.3.3 \
#   --run "$W/census_06_20261020/attempts/full-split-002" \
#   --out "$W/census_06_20261020/attempts/full-split-002.readout" \
#   --baseline "$CENSUS06_BASELINE" --expect-rows 592466
# Set from the actual chain output only:
: "${FULL_READOUT_JOB_ID:?set actual full readout job ID}"
sbatch --account=a0140 --partition=normal --time=00:30:00 \
  --dependency="afterok:$FULL_READOUT_JOB_ID" \
  --output="$W/census_06_20261020/logs/flips-%j.log" --export=ALL \
  "$CENSUS06_BUNDLE/flip_report.sbatch"
# flip_report compares completed census05/census06 and writes the sibling
# attempts/full-split-002.flips/flip_report.json; it never writes census05.
