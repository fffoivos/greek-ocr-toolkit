# Sourced by the two sbatch jobs; all paths are independent of the submit directory.
set -euo pipefail
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CENSUS= OUT= CANDIDATES=
while (($#)); do
 case "$1" in
  --census-dir) CENSUS="$2"; shift 2;;
  --output-dir) OUT="$2"; shift 2;;
  --candidates) CANDIDATES="$2"; shift 2;;
  *) echo "Unknown argument: $1" >&2; exit 2;;
 esac
done
case "$CENSUS" in /*) ;; *) echo '--census-dir must be absolute' >&2; exit 2;; esac
case "$OUT" in /iopsstor/scratch/*) ;; *) echo '--output-dir must be an absolute scratch path' >&2; exit 2;; esac
mkdir -p "$OUT"
python=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python
export PYTHONDONTWRITEBYTECODE=1
