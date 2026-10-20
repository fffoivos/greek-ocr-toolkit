"""Validate the rejected Phase 0 handoff; never interpret it as qualification."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
R=BASE/'receipts'


def read(name):
    return json.loads((R/name).read_text())


def main(write=False):
    for p in BASE.glob('*.py'):
        ast.parse(p.read_text(),filename=str(p))
    for p in R.rglob('*.json'):
        json.loads(p.read_text())
    for p in R.rglob('*.jsonl'):
        for line in p.read_text().splitlines():
            json.loads(line)
    pop,remote,mock=read('local_population.json'),read('remote_population.json'),read('mock_comparison.json')
    assert (pop['train']['lines'],pop['test']['lines'],pop['pages'],pop['page_bytes'])==(214436,44029,5585,16168304605)
    assert remote['full_count_match'] and remote['full_id_set_match']
    assert remote['sample_crops_hashed']==2000 and not remote['sample_mismatches']
    for split in ('train','test'):
        assert pop[split]==remote[split]
    assert read('venv_l1_imports.json')['ok'] and read('detector_comparison.json')['byte_equal']
    assert mock['crops']==50 and mock['byte_identical']==19 and len(mock['differences'])==31 and not mock['all_equal']
    assert all(set(d['differences'])=={'output_sha256'} for d in mock['differences'])
    assert read('mock_verify.json')['ok'] and read('mock_verify_mac.json')['ok']
    assert read('phase0_status.json')['phase1_started'] is False
    for item in read('frozen_sources.json'):
        path=ROOT/item['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
        assert path.read_bytes()==subprocess.check_output(['git','show','63c640a3:'+item['path']],cwd=ROOT)
    w=read('byte_mismatch_witness/comparison.json')
    assert w['pixels_equal'] and w['mac']['sha256']!=w['clariden']['sha256']
    for name in ('mac','clariden'):
        assert hashlib.sha256((R/'byte_mismatch_witness'/(name+'.png')).read_bytes()).hexdigest()==w[name]['sha256']
    for host in ('mac','remote'):
        rows=[json.loads(l) for l in (R/f'mock_{host}_records.jsonl').read_text().splitlines()]
        assert len(rows)==len({r['id'] for r in rows})==50
        assert sum(r['changed'] for r in rows)==31
        assert sum(r['original_sha256']==r['output_sha256'] for r in rows)==19
        assert all(r['host'] and r['code_tree_sha']==pop['code_tree_sha'] for r in rows)
    for target in re.findall(r'\]\(([^)]+)\)',(BASE/'README.md').read_text()):
        assert (BASE/target).is_file() or target=='commit-inputs.json',target
    readme_lines=(BASE/'README.md').read_text().splitlines()
    assert any(line.startswith('T6f: stopped at phase 0: byte-identity gate failed') for line in readme_lines)
    if readme_lines[-1].startswith('T6f2:'):
        from t6f2_validate import main as validate_retry
        validate_retry()
    else:
        assert readme_lines[-1].startswith('T6f: stopped at phase 0: byte-identity gate failed')
    assert subprocess.run(['git','diff','--exit-code','HEAD','--','greekocr','docs/harvest/recut_v1/v2_test','docs/harvest/recut_v1/w1_masked/run.py'],cwd=ROOT,capture_output=True).returncode==0
    value=dict(artifact_validation_passed=True,scientific_qualification_passed=False,
               reason='byte-identity gate failed: 31/50 PNG SHA256 mismatches',
               checked=['Python syntax','JSON/JSONL parse','population/full IDs/manifest SHA','2000 crop hashes',
                        'frozen sources versus 63c640a3','detector one-page row byte identity','50-crop comparison',
                        '50 originals and outputs rehashed per host','PNG counterexample','host/tree provenance',
                        'README links and terminal status','frozen tracked source isolation'])
    if write:
        (BASE/'validation.json').write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(value))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();main(a.write)
