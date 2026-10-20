#!/usr/bin/env bash
set -euo pipefail
D=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/w2c1
exec >> "$D/run.log" 2>&1
run_one() {
  local before
  before=$("$D/launchers/limit_probe.sh" "launch_all:$1/$2" | tail -1)
  echo "$before"
  python3 -B "$D/runtime.py" limit "$before" || return 8
  bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh "$1" "$2"
}
run_one w2c1_bsb_poly1850_poly1850 c1
run_one w2c1_bsb_poly1850_poly1850 c2
run_one w2c1_ia_poly1850_poly1850 c1
run_one w2c1_ia_poly1850_poly1850 c2
run_one w2c1_nlg_poly1850 c1
run_one w2c1_nlg_poly1850 c2
run_one w2c1_nlg_poly1900 c1
run_one w2c1_nlg_poly1900 c2
run_one w2c1_nlg_greek_poly c1
run_one w2c1_nlg_greek_poly c2
run_one w2c1_serbia_cyrillic c1
run_one w2c1_serbia_cyrillic c2
run_one w2c1_elstat_numerics_tables c1
run_one w2c1_elstat_numerics_tables c2
run_one w2c1_gazette_modern_modern_scanned c1
run_one w2c1_gazette_modern_modern_scanned c2
