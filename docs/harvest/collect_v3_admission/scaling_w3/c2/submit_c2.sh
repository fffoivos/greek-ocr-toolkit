#!/bin/bash
# Coordinator only. Never invoked during qualification/deployment.
set -euo pipefail
export C2_ROOT=$(cd -- "$(dirname -- "$0")" && pwd)
: "${C2_PYTHON:?Python with pyarrow}"
: "${C2_OUTPUT:?exact new attempt}"
export E4_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel3_20261020/code/27a49e51fa735e8f
"$C2_ROOT/VERIFY.sh" package
"$C2_ROOT/VERIFY.sh" inputs
"$C2_PYTHON" -B -c 'import json,pathlib,sys; p=pathlib.Path(sys.argv[1]); i=json.load(open(p/"IDENTITY.json")); expected="/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_runs/C2-"+i["sha8"]+"-001"; assert sys.argv[2]==expected and not pathlib.Path(expected).exists(), "output must be exact absent C2 attempt"' "$C2_ROOT" "$C2_OUTPUT"
exec sbatch --parsable --export=ALL "$C2_ROOT/c2.sbatch"
