"""Run the identical T6f 50-crop mock with the verified numpy-only venv copy.

No masking code changes. A failed byte gate writes receipts and stops here.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

E = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
W = E / 'recut_1d_20261017'
R = W / 't6f2'
OUT = R / 'mock_50'
TREE = '63c640a3aa4abe08d200258cf24d235dfa4a1625'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    assert sys.prefix == str(W / 'venv_np246')
    import numpy
    assert numpy.__version__ == '2.4.6'
    venv = read(R / 'venv_verification.json')
    assert venv['ok'] and venv['shared_venv_unchanged'] and not venv['non_numpy_changed']
    assert sha(W / 'venv_np246.lock') == venv['lock_sha256']
    ledger = W / 'PHASE0_DEPLOY_SHA256.txt'
    assert sha(ledger) == '3075914ef77ae69a83b76e6f0f5f020529d3b43e607aab70447e9f67f9c2f052'
    checked = []
    for line in ledger.read_text().splitlines():
        expected, relative = line.split('  ', 1)
        if relative.startswith('code/') or relative in (
                'phase0/phase0_mask.py', 'phase0/phase0_launch.py', 'phase0/phase0_verify.py'):
            assert sha(W / relative) == expected, relative
            checked.append(relative)
    assert all('phase0/' + n in checked for n in ('phase0_mask.py', 'phase0_launch.py', 'phase0_verify.py'))
    selection_path = W / 'phase0/mock_50/selection.json'
    assert sha(selection_path) == '9fded4f0ab46202c4df88121c81ed6365b833290942051a2da7883fdf1c2f738'
    assert sha(R / 'mock_mac_records.jsonl') == 'c9bf83b077d3893e34d7eced2d2dd66826c9f98557a9d093f9f8e58b11cd0c4d'
    selection = read(selection_path)
    expected = {r['id']: r for r in map(json.loads, (R / 'mock_mac_records.jsonl').read_text().splitlines())}
    assert len(selection) == len(expected) == 50
    for page in selection:
        assert page['wave'] != 'parliament' and len(page['lines']) == 1
        assert Path(page['raster']).is_relative_to(W / 'mock_pages')
        assert sha(Path(page['raster'])) == page['scan']['sha']
        assert page['lines'][0]['id'] in expected
    OUT.mkdir(exist_ok=False)
    (OUT / 'selection.json').write_bytes(selection_path.read_bytes())
    (R / 'input_verification.json').write_text(json.dumps(dict(
        ok=True, host=socket.gethostname(), source_files_rehashed=checked,
        pages_rehashed=50, page_bytes=sum(p['scan']['bytes'] for p in selection),
        selection_sha256=sha(selection_path), mac_records_sha256=sha(R / 'mock_mac_records.jsonl'),
        numpy_pin='2.4.6', lock_sha256=venv['lock_sha256']), indent=2) + '\n')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(R / 'tmp'),
               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    with (R / 'mock_execution.log').open('xb') as log:
        subprocess.run([sys.executable, '-B', str(W / 'phase0/phase0_launch.py'),
            '--adapter', str(W / 'phase0/phase0_mask.py'), '--code', str(W / 'code'),
            '--harvest', str(E), '--out', str(OUT), '--workers', '2'],
            env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    subprocess.run([sys.executable, '-B', str(W / 'phase0/phase0_verify.py'),
        '--out', str(OUT), '--receipt', str(R / 'mock_verify.json')], env=env, check=True)
    records = {}
    for path in sorted((OUT / 'page-lines').glob('*.guarded.jsonl')):
        for line in path.read_text().splitlines():
            r = json.loads(line)
            assert r['id'] not in records and r['code_tree_sha'] == TREE and r['host']
            assert r['original_sha256'] == expected[r['id']]['original_sha256']
            r.update(numpy_pin='2.4.6', venv=str(W / 'venv_np246'),
                     venv_lockfile=str(W / 'venv_np246.lock'), venv_lock_sha256=venv['lock_sha256'])
            records[r['id']] = r
    assert set(records) == set(expected)
    (R / 'mock_records.jsonl').write_text(''.join(json.dumps(records[k], sort_keys=True) + '\n' for k in sorted(records)))
    (R / 'mock_pages.jsonl').write_text(''.join(json.dumps(read(p), sort_keys=True) + '\n'
        for p in sorted((OUT / 'pages').glob('*.json'))))
    fields = ('output_sha256', 'guard_status', 'match_status', 'wrong_line_risk',
              'masked_pixel_count', 'masked_component_count')
    differences = []
    for k in sorted(records):
        diff = {f: dict(mac=expected[k].get(f), remote=records[k].get(f))
                for f in fields if expected[k].get(f) != records[k].get(f)}
        if diff:
            differences.append(dict(id=k, wave=records[k]['wave'], differences=diff))
    equal = sum(records[k]['output_sha256'] == expected[k]['output_sha256'] for k in records)
    result = dict(seed=20261017, crops=50, pages=50, numpy_pin='2.4.6',
        byte_identical=equal, gate_passed=equal == 50, all_compared_fields_equal=not differences,
        compared_fields=fields, differences=differences, host=socket.gethostname(),
        worker_hosts=sorted({r['host'] for r in records.values()}),
        code_tree_sha=TREE, lock_sha256=venv['lock_sha256'],
        execution=read(OUT / 'execution.json'), verify=read(R / 'mock_verify.json'),
        phase1_started=False, real_job_submitted=False)
    (R / 'mock_comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print('T6f2: ' + ('gate passed ' if equal == 50 else 'gate failed ') + str(equal) + '/50', flush=True)


if __name__ == '__main__':
    main()
