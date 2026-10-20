#!/usr/bin/env bash
#SBATCH --account=a0140
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --job-name=census06_sf7_bind
set -euo pipefail
: "${CENSUS06_BUNDLE:?}" "${SF7_BINDINGS_FILE:?}" "${SF7_BIND_WORK:?}"
W=${W:-/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3}
"${CENSUS06_PYTHON:-$W/venv_l1/bin/python}" -B - "$CENSUS06_BUNDLE" "$SF7_BINDINGS_FILE" "$SF7_BIND_WORK" <<'PY'
import json,subprocess,sys
from pathlib import Path
bundle,bindings,work=sys.argv[1:]
entries=json.loads(Path(bindings).read_text())
config=json.loads((Path(bundle)/'census06_config.json').read_text())
assert set(entries)=={p['id'] for p in config['parents']}
args=[x for parent in config['parents'] for x in (entries[parent['id']]['path'],entries[parent['id']]['sha256'])]
subprocess.run([sys.executable,'-B',str(Path(bundle)/'bind_sf7.py'),'--work',work,*args],check=True)
PY
