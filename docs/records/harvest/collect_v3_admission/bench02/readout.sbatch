#!/bin/bash
#SBATCH --job-name=bench02-readout
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
# Required: submit_job.sh supplies sbatch --output="$OUT/readout-%j.log".
: "${BENCH02_DIR:?submit with submit_job.sh or export the absolute deployed bench02 directory}"
source "$BENCH02_DIR/job_common.sh"
case "$CANDIDATES" in /*) ;; *) echo '--candidates must be absolute' >&2; exit 2;; esac
srun "$python" -B "$B/bench02_draw.py" readout \
 --candidates "$CANDIDATES" --census-dir "$CENSUS" --output-dir "$OUT"
