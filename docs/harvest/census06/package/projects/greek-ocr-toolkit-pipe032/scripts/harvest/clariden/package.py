"""Archive the small source/evidence closure, never the corpus or local binaries."""
import hashlib
import io
import json
from pathlib import Path
import tarfile

TOOLKIT=Path(__file__).resolve().parents[3];PROJECTS=TOOLKIT.parent
paths=set()
for p in (TOOLKIT/'greekocr').rglob('*'):
    if p.is_file() and p.suffix in {'.py','.json','.js','.mjs','.rs','.toml','.lock','.sh','.yml'}:paths.add(p)
for directory in ['scripts/harvest/clariden','scripts/harvest/filter_runtime/src']:
    paths.update(p for p in (TOOLKIT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for name in ['pyproject.toml','scripts/harvest/filter_runtime/Cargo.toml','scripts/harvest/filter_runtime/Cargo.lock',
    'scripts/harvest/verify_filter_parity.py','scripts/harvest/build_filter_versions.py',
    'tests/test_line_pipeline.py','docs/harvest/line_pipeline/tool_versions.json','docs/harvest/line_pipeline/README.md']:
    paths.add(TOOLKIT/name)
versions=json.loads((TOOLKIT/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
for tool in versions.values():paths.update(PROJECTS/relative for relative in tool['components'])
paths.add(PROJECTS/'greek-ocr-toolkit-spellcheck/artifacts/sf7_rc1/release_edits_only_A.jsonl')
paths.add(PROJECTS/'greek-page-ocr-wave2/scripts/clariden/common.sh')
site=PROJECTS/'ocr-review-sites-20261018'
for name in ['review-data/box-length-experiment.json','worker/box-length-policy.js',
    'qa/word-tolerance/context-evidence.json','qa/word-tolerance/reconciled-evidence.json',
    'review-data/font-normalized-experiment.json','review-data/font-normalized/predicted-rows.json.gz']:
    paths.add(site/name)
manifest=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(PROJECTS))+'\n' for p in sorted(paths))
sha=hashlib.sha256(manifest.encode()).hexdigest()
archive=Path('/private/tmp')/f'greekocr-filter-source-{sha[:16]}.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for p in sorted(paths):tar.add(p,arcname=str(p.relative_to(PROJECTS)),recursive=False)
    raw=manifest.encode();info=tarfile.TarInfo('SHA256SUMS');info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
receipt=dict(archive=str(archive),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),manifest_sha256=sha,
    files=len(paths),bytes=archive.stat().st_size,remote_projects='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/'+sha[:16]+'/projects')
(TOOLKIT/'docs/harvest/line_pipeline/clariden/deployment-source.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
