#!/usr/bin/env bash
# bake-off v4 with the CUDA CLLG worker (binding = what the Vouli stage will use), then the Vouli stage. Log ~/work/vouli2.log
set -u; export PATH=$HOME/.cargo/bin:$HOME/.local/bin:$PATH; cd ~/work/greek-page-ocr || exit 1
git reset -q --hard 628a57944cd13424b5ea8729ced7f908624b638e && echo "HEAD=$(git rev-parse --short HEAD)"
export PYTHON=~/venvs/ocr/bin/python CLLG_PYTHON=~/venvs/cllg-gpu/bin/python CLLG_ACCELERATOR=cuda GIT_OPTIONAL_LOCKS=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
python3 -c 'import json; p=json.load(open("/opt/e2-assets/e2d_config.json")); json.dump(p["vouli"],open("/opt/e2-assets/vouli.json","w"))'
echo "=== CONTRACT (cuda venv) $(date -u +%H:%M:%S)"; cp /opt/e2-assets/cllg/readme_contract.json /opt/e2-assets/cllg/readme_contract.cpu.json
$PYTHON -m bench.e2_cllg_contract --readme /opt/e2-assets/cllg/README.md --checkpoint /opt/e2-assets/cllg/ppocr_v6_tau090.safetensors --out /opt/e2-assets/cllg/readme_contract.json 2>&1 | tail -2 || { echo CONTRACT_FAILED; exit 3; }
echo "=== BAKEOFF v4 START $(date -u +%H:%M:%S)"; $PYTHON -u -m bench.e2_bakeoff --config out/e2d/bakeoff_config.json --e1 out/e1_run4 --out out/e2d/bakeoff_v4 > out/e2d/logs/bakeoff_v4.log 2>&1; echo "BAKEOFF_V4_EXIT=$?"
grep -E "^\| (f50_s0|cllg|kalchas) \| real_gold \| [0-9]" out/e2d/bakeoff_v4/BAKEOFF.md | cut -c1-140
R=$(python3 -c "import json;print(json.load(open('out/e2d/bakeoff_v4/teachers.json')).get('ready'))" 2>/dev/null); echo "ready=$R"; [ "$R" = "True" ] || { echo "TEACHERS_NOT_READY"; exit 4; }
echo "=== VOULI START $(date -u +%H:%M:%S)"
PYTHON=$PYTHON bash bench/e2_vouli.sh --e1 out/e1_run4 --config /opt/e2-assets/vouli.json --bakeoff out/e2d/bakeoff_v4 --out out/e2d/vouli_v4 > out/e2d/logs/vouli_v4.log 2>&1; echo "VOULI_EXIT=$?"
tail -3 out/e2d/logs/vouli_v4.log | cut -c1-200; python3 -c "import json;d=json.load(open('out/e2d/vouli_v4/vouli.json'));print({k:d[k] for k in d if not isinstance(d[k],(dict,list))})" 2>/dev/null | cut -c1-600
echo "VOULI_DONE $(date -u +%H:%M:%S)"
