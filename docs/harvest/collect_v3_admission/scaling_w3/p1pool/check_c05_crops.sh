#!/usr/bin/env bash
# Authorized bounded login-node check: 20 crops, own temporary scratch, always removed.
set -euo pipefail
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PYTHON="$W/venv_l1/bin/python"
export CENSUS_PROJECTS="$W/census_05_20261020/code/997b7d2ab5a8775b/docs/harvest/census05/package/projects"
export CENSUS_CODE="$CENSUS_PROJECTS/greek-ocr-toolkit-pipe032"
export CENSUS_MANIFEST="$W/crops4_package/9a3b80c1/census05_DEPLOY_SHA256SUMS"
export PROJECTS_SUMS_ROOT="$W/census_05_20261020/code/997b7d2ab5a8775b"
export PROJECTS_SHA256=997b7d2ab5a8775b
# Full manifest hash, not its directory prefix.
PROJECTS_SHA256=$(sha256sum "$CENSUS_MANIFEST" | cut -d' ' -f1)
export PROJECTS_SHA256
export LD_PRELOAD="$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
source "$W/crops4_package/9a3b80c1/binding_checks.sh" >&2
"$PYTHON" -B - <<'PYTHON'
import hashlib,json,pathlib,subprocess,tempfile,os
from PIL import Image
from greekocr.harvest.line_pipeline_native import reconstructed_crop,valid_box
w=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
f=w/'census_05_20261020/attempts/full-split-001/generations/g1-6283e1bcdf124516b599f8028ad910be/pending_cyrillic.jsonl'
sample=subprocess.check_output(['head','-n','20',str(f)])
rows=[json.loads(l) for l in sample.splitlines()];assert len(rows)==20
# mkdtemp creates only this private new scratch tree; no persistent parent mkdir.
checks=[]
with tempfile.TemporaryDirectory(prefix='p1pool-cropcheck-',dir=w) as td:
 for i,r in enumerate(rows):
  page=pathlib.Path(r['crop_source_image'])
  assert hashlib.sha256(page.read_bytes()).hexdigest()==r['crop_source_sha256']
  with Image.open(page) as image:
   image.load();assert valid_box(r['crop_bbox'],image.size)
   crop,raw=reconstructed_crop(image,r['crop_bbox'],r.get('crop_color_mode','L'));crop.close()
  actual=hashlib.sha256(raw).hexdigest();assert actual==r['crop_sha256'],r['id']
  p=pathlib.Path(td)/(str(i)+'.png')
  with p.open('xb') as stream:stream.write(raw)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==r['crop_sha256']
  checks.append(dict(parent_id=r['parent_id'],row_id=r['id'],sha256=actual))
assert not pathlib.Path(td).exists()
print(json.dumps(dict(status='ok',byte_equal=len(checks),tested=len(rows),temp_removed=True,source=str(f),head_sha256=hashlib.sha256(sample).hexdigest(),checks=checks),sort_keys=True))
PYTHON
