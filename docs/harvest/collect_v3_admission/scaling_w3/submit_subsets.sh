#!/bin/bash
set -euo pipefail
PKG='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/bc009e90'
W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
[[ $# == 3 && "$1" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ && "$2" == /* && "$3" =~ ^[0-9a-f]{64}$ ]] || { echo 'usage: submit_subsets.sh ATTEMPT ABS_TAGS_RECEIPT TAGS_RECEIPT_SHA256' >&2; exit 2; }
[[ ! -e "$W/scaling_w3/subsets/$1" ]] || { echo 'attempt already exists' >&2; exit 2; }
"$PKG/VERIFY.sh" package
"$PKG/VERIFY.sh" inputs-subsets "$2" "$3"
mkdir -p "$W/scaling_w3/subsets"
exec sbatch "$PKG/subsets.sbatch" "$1" "$2" "$3"
