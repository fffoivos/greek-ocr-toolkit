#!/usr/bin/env bash
# Intentionally prepared only. The lead launches the two independent contexts.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
exec > >(tee -a "$D/run_r2.log") 2>&1
"$D/r2/launchers/run_bed.sh" segcp7r2_a r1
"$D/r2/launchers/run_bed.sh" segcp7r2_b r1
