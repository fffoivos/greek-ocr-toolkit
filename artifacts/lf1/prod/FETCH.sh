#!/usr/bin/env bash
# One SSH/tar stream, supplied subset TSV or full list. Run from worktree.
set -euo pipefail
LIST=${1:-artifacts/lf1/prod/fetch_list.tsv}
MANIFEST=${2:-artifacts/lf1/prod/crops.sha256}
CROPS=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_prod/crops
mkdir -p "$CROPS"
python3 -B - "$LIST" <<'PY' | ssh -o BatchMode=yes -o ConnectTimeout=20 clariden 'tar -C /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3 -cf - -T -' | tar -C "$CROPS" -xf -
import csv,sys
from pathlib import PurePosixPath
root=PurePosixPath('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
for r in csv.DictReader(open(sys.argv[1]),delimiter='\t'):
    print(PurePosixPath(r['remote_path']).relative_to(root))
PY
python3 -B - "$LIST" <<'PY' > "$MANIFEST"
import csv,hashlib,sys
from pathlib import Path
for r in csv.DictReader(open(sys.argv[1]),delimiter='\t'):
    p=Path(r['local_path'])
    print(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p))
PY
