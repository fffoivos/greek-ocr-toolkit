#!/bin/bash
#SBATCH --job-name=bench02-extract
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
# Required: submit_job.sh supplies sbatch --output="$OUT/extract-%j.log".
: "${BENCH02_DIR:?submit with submit_job.sh or export the absolute deployed bench02 directory}"
source "$BENCH02_DIR/job_common.sh"
srun "$python" -B "$B/bench02_draw.py" extract \
 --decisions "$CENSUS/decisions.jsonl" \
 --diagnostics "$CENSUS/evaluation_diagnostics.jsonl" \
 --output-dir "$OUT"
