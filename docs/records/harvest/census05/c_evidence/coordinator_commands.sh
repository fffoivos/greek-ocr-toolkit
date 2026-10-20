# C COORDINATOR COMMANDS — NOT EXECUTED; REQUIRE VERIFY_OK AND REVIEW
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export CENSUS05_BUNDLE="$W/census_05_20261020/code/997b7d2ab5a8775b/docs/harvest/census05"
RUN_ROOT="$W/census_05_20261020"
mkdir -p "$RUN_ROOT/attempts" "$RUN_ROOT/logs"
submit_census05() {
  local regression parity census readout
  regression=$(sbatch --parsable "$@" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/regression-%j.log" "$CENSUS05_BUNDLE/jobs/regression.sbatch")
  parity=$(sbatch --parsable "$@" --dependency="afterok:$regression" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/parity-%j.log" "$CENSUS05_BUNDLE/jobs/parity.sbatch")
  census=$(sbatch --parsable "$@" --dependency="afterok:$parity" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/census-%j.log" "$CENSUS05_BUNDLE/jobs/census.sbatch")
  readout=$(sbatch --parsable "$@" --dependency="afterok:$census" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/readout-%j.log" "$CENSUS05_BUNDLE/jobs/readout.sbatch")
  printf 'regression=%s parity=%s census=%s readout=%s\n' "$regression" "$parity" "$census" "$readout"
}
unset CENSUS05_RUN CENSUS05_READOUT_OUT CENSUS05_CONFIG CENSUS05_BASELINE
export CENSUS05_SPLIT_FILE="$W/census_05_20261020/inputs/row_split.jsonl.gz"
export CENSUS05_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS05_ATTEMPT=smoke-split-001 CENSUS05_EXPECT_ROWS=200
submit_census05 --partition=debug --time=00:30:00

# Separate coordinator action, only after smoke review and P3's gates pass.
# This uses the normal partition and each script's original production time.
export E4_SMOKE=0 CENSUS05_ATTEMPT=full-split-001 CENSUS05_EXPECT_ROWS=592466
# Optional real census_03 summary supplies the readout's baseline delta table.
export CENSUS05_BASELINE="$W/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json"
submit_census05
