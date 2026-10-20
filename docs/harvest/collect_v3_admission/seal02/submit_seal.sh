#!/usr/bin/env bash
# Coordinator only. No defaults for final list, bindings or attempt.
set -euo pipefail
B=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
CONFIG=${1:?absolute production bindings path}
CONFIG_SHA=${2:?production bindings sha256}
OUTPUT=${3:?absolute new attempt output}
[[ $# == 3 && "$CONFIG" == /* && "$OUTPUT" == "$W"/benchmark_0.2/* && ! -e "$OUTPUT" ]]
[[ $(sha256sum "$CONFIG" | cut -d' ' -f1) == "$CONFIG_SHA" ]]
unset SEAL02_PYTHON
bash "$B/VERIFY.sh" package
bash "$B/VERIFY.sh" inputs --bindings "$CONFIG" --require-complete
"$W/venv_l1/bin/python" -B -c 'import json,sys; c=json.load(open(sys.argv[1])); assert c.get("mock",False) is False; r=json.load(open(c["inputs"]["final_receipt"]["path"])); assert r["mock"] is False' "$CONFIG"
exec sbatch --parsable --export=NONE --output="${OUTPUT}.slurm-%j.log" "$B/seal02.sbatch" "$B" "$CONFIG" "$CONFIG_SHA" "$OUTPUT"
