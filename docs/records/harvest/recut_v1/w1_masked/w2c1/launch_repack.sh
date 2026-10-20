#!/usr/bin/env bash
set -euo pipefail
D=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/w2c1
exec >> "$D/repack_run.log" 2>&1
run_one() {
  local before
  before=$("$D/launchers/limit_probe.sh" "launch_repack:$1/$2" | tail -1)
  echo "$before"
  python3 -B "$D/runtime.py" limit "$before" || return 8
  bash "$D/launchers/run_bed.sh" "$1" "$2"
}
run_one w2c1_nlg_poly1900_r2 c1
run_one w2c1_nlg_poly1900_r2 c2
run_one w2c1_nlg_greek_poly_r2 c1
run_one w2c1_gazette_modern_modern_scanned_r2 c2
