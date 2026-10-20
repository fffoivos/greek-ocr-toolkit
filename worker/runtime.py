"""Shared worker paths. Environment/config paths are never dumped."""
import os
from pathlib import Path
from collect_v3.config import config

ROOT=Path(__file__).resolve().parents[1]
PYTHON_VERSION=(3,11,3)

def settings():
    out=Path(os.environ.get('COLLECT_V3_OUTPUT_ROOT',ROOT/'worker/run')).resolve()
    c=config(os.environ.get('COLLECT_V3_CONFIG'),output_root=str(out),cache=str(out/'cache'),
             limiter_root=str(Path(os.environ.get('COLLECT_V3_LIMITER_ROOT',ROOT/'worker/limiter')).resolve()),
             execution_host='worker',network_enabled=False)
    return c
