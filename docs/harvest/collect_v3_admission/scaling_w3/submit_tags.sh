#!/bin/bash
set -euo pipefail
PKG='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/bc009e90'
W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
[[ $# == 1 && "$1" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]] || { echo 'usage: submit_tags.sh ATTEMPT' >&2; exit 2; }
[[ ! -e "$W/scaling_w3/tags/$1" ]] || { echo 'attempt already exists' >&2; exit 2; }
"$PKG/VERIFY.sh" package
"$PKG/VERIFY.sh" inputs-tags
mkdir -p "$W/scaling_w3/tags"
exec sbatch "$PKG/tags.sbatch" "$1"
