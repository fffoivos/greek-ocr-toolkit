#!/usr/bin/env bash
# Intentionally prepared only. The lead launches the two independent contexts.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
exec > >(tee -a "$D/run.log") 2>&1
"$D/launchers/run_bed.sh" segcp7_a r1
"$D/launchers/run_bed.sh" segcp7_b r1
