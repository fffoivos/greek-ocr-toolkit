#!/usr/bin/env bash
set -u; export PATH=$HOME/.cargo/bin:$HOME/.local/bin:$PATH; cd ~/work/greek-page-ocr || exit 1
git reset -q --hard 0bb9a5cc85a3717cd5ee0dbedd8bd457f5b2e164 && echo "HEAD=$(git rev-parse --short HEAD)"
echo "=== CLLG ENV START $(date -u +%H:%M:%S)"; uv python install 3.11 >/dev/null 2>&1; PY311=$(uv python find 3.11); echo "py311=$PY311"
[ -x ~/venvs/cllg/bin/python ] || CLLG_BASE_PYTHON="$PY311" bash scripts/fetch/r2_cllg_env.sh 2>&1 | tail -3
export CLLG_PYTHON=~/venvs/cllg/bin/python; $CLLG_PYTHON -c "import kraken, importlib.metadata as m; print('cllg venv kraken', m.version('kraken'))" || { echo "CLLG_ENV_FAILED"; exit 2; }
export PYTHON=~/venvs/ocr/bin/python GIT_OPTIONAL_LOCKS=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
echo "=== CONTRACT $(date -u +%H:%M:%S)"; $PYTHON -m bench.e2_cllg_contract --readme /opt/e2-assets/cllg/README.md --checkpoint /opt/e2-assets/cllg/ppocr_v6_tau090.safetensors --out /opt/e2-assets/cllg/readme_contract.json 2>&1 | tail -3; [ -f /opt/e2-assets/cllg/readme_contract.json ] || { echo "CONTRACT_FAILED"; exit 3; }
echo "=== BAKEOFF v3 START $(date -u +%H:%M:%S)"; $PYTHON -u -m bench.e2_bakeoff --config out/e2d/bakeoff_config.json --e1 out/e1_run4 --out out/e2d/bakeoff_v3 > out/e2d/logs/bakeoff_v3.log 2>&1; echo "BAKEOFF_V3_EXIT=$?"
grep -E "^\| (f50_s0|f75_s0|kalchas|cllg) \| real_gold" out/e2d/bakeoff_v3/BAKEOFF.md 2>/dev/null | cut -c1-160; python3 -c "import json;print('ready', json.load(open('out/e2d/bakeoff_v3/teachers.json')).get('ready'))" 2>/dev/null
echo "CLLG_BAKEOFF_DONE $(date -u +%H:%M:%S)"
