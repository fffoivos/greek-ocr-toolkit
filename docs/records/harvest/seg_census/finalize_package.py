"""Refresh package fingerprints and both SHA manifests, without any Git write."""
import hashlib
import json
from pathlib import Path
import subprocess

D = Path(__file__).resolve().parent
REPO = D.parents[2]
P = D/'package/projects'
B = D/'census03_baseline/projects'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finalize():
    versions_path = P/'greek-ocr-toolkit-sol-recut/docs/harvest/line_pipeline/tool_versions.json'
    versions = json.loads(versions_path.read_text())
    for name, tool in versions['tools'].items():
        for component in tool['components']:
            tool['components'][component] = sha(P/component)
        if name == 'census':
            for rel in ('greekocr/harvest/line_pipeline_census04.py', 'greekocr/harvest/numeric_cells.py'):
                component = 'greek-ocr-toolkit-sol-recut/'+rel
                tool['components'][component] = sha(P/component)
        tool['digest'] = hashlib.sha256(json.dumps(tool['components'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    versions_path.write_text(json.dumps(versions, ensure_ascii=False, indent=2)+'\n')
    for rel in ('greekocr/harvest/line_pipeline_native.py', 'greekocr/harvest/filtering_assets/crop-tools.py',
                'greekocr/harvest/filtering_assets/segmentation-policy.js'):
        assert (P/'greek-ocr-toolkit-sol-recut'/rel).read_bytes() == subprocess.check_output(['git', '-C', str(REPO), 'show', '410f4566:'+rel])
    assert versions['tools']['segmentation']['digest'] == '512e362a691c6f2f425acc41e587b4b751dedbaadd10077d42309ed3f1f7bebd'
    baseline = {}
    for line in (B/'SHA256SUMS').read_text().splitlines():
        h, rel = line.split('  ', 1)
        baseline[rel] = h
        assert sha(B/rel) == h
    files = sorted(f for f in P.rglob('*') if f.is_file() and f.name!='SHA256SUMS'
                   and (str(f.relative_to(P)) in baseline or not any(part in {'__pycache__', '.pytest_cache'} for part in f.parts)))
    current = {str(f.relative_to(P)): sha(f) for f in files}
    changed = sorted(rel for rel, h in baseline.items() if current[rel]!=h)
    expected = sorted('greek-ocr-toolkit-sol-recut/'+rel for rel in (
        'greekocr/harvest/line_pipeline_native.py', 'greekocr/harvest/filtering_assets/crop-tools.py',
        'greekocr/harvest/filtering_assets/segmentation-policy.js', 'docs/harvest/line_pipeline/tool_versions.json'))
    assert changed == expected, changed
    (P/'SHA256SUMS').write_text(''.join(f'{h}  {rel}\n' for rel, h in sorted(current.items())))
    composition = dict(baseline_files=len(baseline), baseline_manifest_sha256=sha(B/'SHA256SUMS'),
        changed_files=changed, added_files=sorted(set(current)-set(baseline)), tools=versions['tools'])
    (D/'package_composition.json').write_text(json.dumps(composition, indent=2)+'\n')
    payload = files+[P/'SHA256SUMS', D/'census04_config.json', D/'prepare_config.py', D/'parity_check.py',
                     D/'parity_inputs.jsonl.gz', D/'split_input.schema.json', D/'tests/test_census04.py', *sorted((D/'jobs').glob('*'))]
    raw = ''.join(f'{sha(f)}  {f.relative_to(REPO)}\n' for f in sorted(payload))
    (D/'DEPLOY_SHA256SUMS').write_text(raw)
    package_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
    (D/'package_id.json').write_text(json.dumps(dict(package_hash=package_hash, deploy_manifest_sha256=hashlib.sha256(raw.encode()).hexdigest(),
        deploy_files=len(payload), manifest='docs/harvest/seg_census/DEPLOY_SHA256SUMS'), indent=2)+'\n')
    print(package_hash, len(payload), 'deploy files;', len(current), 'package files; baseline differences:', len(changed))


if __name__ == '__main__':
    finalize()
