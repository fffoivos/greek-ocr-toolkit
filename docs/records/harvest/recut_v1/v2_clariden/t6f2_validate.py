"""Read-only validation of T6f2 receipts and the unchanged scientific sources."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
R = BASE / 'receipts/t6f2'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((R / name).read_text())


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    for p in BASE.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    for p in R.glob('*.json'):
        json.loads(p.read_text())
    for p in R.glob('*.jsonl'):
        rows(p)
    v = read('venv_verification.json')
    assert v['ok'] and v['shared_venv_unchanged'] and not v['non_numpy_changed']
    assert v['shared_before_sha256'] == v['shared_after_sha256']
    if v.get('resumed_existing'):
        assert v['initial_shared_sha256'] == v['shared_before_sha256']
    else:
        assert v['copy_before_sha256'] == v['shared_before_sha256']
    assert v['numpy_pin'] == v['imports']['numpy'] == '2.4.6'
    assert sha(R / 'venv_np246.lock') == v['lock_sha256']
    assert sha(R / 'venv_l1.before.lock') == v['source_lock_sha256']
    assert (R / 'venv_l1.before.lock').read_bytes() == (R / 'venv_l1.after.lock').read_bytes()
    before = set((R / 'venv_l1.before.lock').read_text().splitlines())
    after = set((R / 'venv_np246.lock').read_text().splitlines())
    assert before - after == {'numpy==2.5.4'} and after - before == {'numpy==2.4.6'}
    assert (R / 'numpy_np246_wheel.sha256').read_text().split()[0] == v['wheel_sha256']
    inputs = read('input_verification.json')
    assert inputs['ok'] and inputs['pages_rehashed'] == 50
    assert inputs['selection_sha256'] == sha(BASE / 'receipts/mock_selection_remote.json')
    assert inputs['mac_records_sha256'] == sha(BASE / 'receipts/mock_mac_records.jsonl')
    mac = {r['id']: r for r in rows(BASE / 'receipts/mock_mac_records.jsonl')}
    remote_rows = rows(R / 'mock_records.jsonl')
    remote = {r['id']: r for r in remote_rows}
    assert len(remote_rows) == len(remote) == len(mac) == 50 and set(remote) == set(mac)
    assert len(rows(R / 'mock_pages.jsonl')) == 50
    for k, r in remote.items():
        assert r['host'] and r['numpy_pin'] == '2.4.6' and r['venv_lock_sha256'] == v['lock_sha256']
        assert r['code_tree_sha'] == '63c640a3aa4abe08d200258cf24d235dfa4a1625'
        assert r['original_sha256'] == mac[k]['original_sha256'] and r['wave'] != 'parliament'
    comparison = read('mock_comparison.json')
    equal = sum(r['output_sha256'] == mac[k]['output_sha256'] for k, r in remote.items())
    assert comparison['byte_identical'] == equal and comparison['gate_passed'] == (equal == 50)
    differences = []
    for k in sorted(remote):
        diff = {f: dict(mac=mac[k].get(f), remote=remote[k].get(f))
                for f in comparison['compared_fields'] if mac[k].get(f) != remote[k].get(f)}
        if diff:
            differences.append(dict(id=k, wave=remote[k]['wave'], differences=diff))
    assert differences == comparison['differences']
    execution, verification = read('mock_execution.json'), read('mock_verify.json')
    assert execution['ok'] and execution['crops'] == execution['pages'] == 50
    assert all(r['exit_code'] == 0 for r in execution['results'])
    assert verification['ok'] and verification['originals_rehashed'] == verification['outputs_rehashed'] == 50
    assert not verification['mismatches']
    for item in json.loads((BASE / 'receipts/frozen_sources.json').read_text()):
        p = ROOT / item['path']
        assert sha(p) == item['sha256']
        assert p.read_bytes() == subprocess.check_output(['git', 'show', '63c640a3:' + item['path']], cwd=ROOT)
    status = read('status.json')
    assert status['mock_50_identical'] == equal and status['numpy_pin'] == '2.4.6'
    if equal != 50:
        assert status['phase1_started'] is False and status['production_pages_uploaded'] == 0
        assert status['real_job_submitted'] is False and status['test_only'] == 'not run'
        assert not any(read('stop_boundary.json')['production_paths'].values())
    text = (BASE / 'README.md').read_text()
    for link in re.findall(r'\]\(([^)]+)\)', text):
        assert (BASE / link).is_file(), link
    assert text.splitlines()[-1] == status['terminal_line']
    result = dict(artifact_validation_passed=True, byte_gate_passed=equal == 50,
        byte_identical=equal, checked=['all receipt syntax', 'verified venv copy', 'shared venv preservation',
        'numpy-only freeze difference', 'wheel and lock hashes', 'original selection and Mac records',
        'all 50 record identities and provenance', 'independent gate recomputation',
        'remote rehash of 50 originals and 50 outputs', 'frozen scientific source bytes',
        'README links and exact terminal status'])
    print(json.dumps(result))


if __name__ == '__main__':
    main()
