#!/usr/bin/env bash
# Run on the Linux worker. Installs no models and launches no OCR/training.
set -euo pipefail
if [[ "$(uname -s)" != Linux ]]; then
    echo 'Run this environment setup on a Linux node.' >&2
    exit 2
fi
cllg_python="${CLLG_BASE_PYTHON:-python3.11}"
cllg_venv="${CLLG_VENV:-$HOME/venvs/cllg}"
"$cllg_python" -c 'import sys; assert sys.version_info[:2] == (3, 11), "Use Python 3.11"'
"$cllg_python" -m venv "$cllg_venv"
cllg_pip=("$cllg_venv/bin/python" -m pip)
if [[ -n "${CLLG_WHEELHOUSE:-}" ]]; then
    # Use this path on restricted/offline nodes with pre-staged CPU wheels.
    echo "82faba07d9fa4746cb822c669e822570f8a8c42a9ac1570ad187326cedbd48e4  $CLLG_WHEELHOUSE/kraken-7.1.1-py3-none-any.whl" | sha256sum --check --status
    "${cllg_pip[@]}" install --no-index --find-links "$CLLG_WHEELHOUSE" \
        'torch==2.9.0+cpu' 'torchvision==0.24.0+cpu' \
        'kraken==7.1.1' 'safetensors==0.7.0' 'lightning==2.6.1' 'Pillow==11.3.0'
else
    # CPU wheel index avoids downloading multi-GB CUDA/NVIDIA dependencies.
    "${cllg_pip[@]}" install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        'torch==2.9.0+cpu' 'torchvision==0.24.0+cpu'
    cllg_wheel="$(mktemp --suffix=.whl)"
    trap 'rm -f "$cllg_wheel"' EXIT
    curl --fail --location --max-time 120 --max-filesize 5079921 \
        'https://files.pythonhosted.org/packages/69/e0/0f1205e32788602a219017bb9ccf53ae705ec0588c510c76bc0d6a1af380/kraken-7.1.1-py3-none-any.whl' \
        -o "$cllg_wheel"
    echo "82faba07d9fa4746cb822c669e822570f8a8c42a9ac1570ad187326cedbd48e4  $cllg_wheel" | sha256sum --check --status
    # pip requires the distribution/version/tags in the wheel's basename.
    cllg_wheel_dir="$(mktemp -d)"
    trap 'rm -f "$cllg_wheel"; rm -rf "$cllg_wheel_dir"' EXIT
    mv "$cllg_wheel" "$cllg_wheel_dir/kraken-7.1.1-py3-none-any.whl"
    "${cllg_pip[@]}" install --no-cache-dir "$cllg_wheel_dir/kraken-7.1.1-py3-none-any.whl" \
        'safetensors==0.7.0' 'lightning==2.6.1' 'Pillow==11.3.0'
fi
"${cllg_pip[@]}" check
"$cllg_venv/bin/python" - <<'PY'
import importlib.metadata as m
from kraken.models import load_safetensors
from kraken.lib.ppocr import PPOCRv6Model
from kraken.tasks import RecognitionTaskModel
assert m.version('kraken') == '7.1.1'
print({name: m.version(name) for name in ('kraken', 'torch', 'torchvision', 'safetensors', 'lightning', 'Pillow')})
PY
"${cllg_pip[@]}" freeze > "$cllg_venv/R2_INSTALLED.txt"
echo "CLLG_PYTHON=$cllg_venv/bin/python"
