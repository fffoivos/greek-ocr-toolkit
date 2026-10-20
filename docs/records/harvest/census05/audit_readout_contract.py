"""Reproduce the unchanged readout's rejection of actual CODE_SHA pipeline output.

Only native I/O is doubled, using CODE_SHA's existing test fixture. No decision,
reason, disposition, export or readout code is changed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

D = Path(__file__).resolve().parent
R = D.parents[2]
P = D / 'package/projects/greek-ocr-toolkit-pipe032'
sys.path[:0] = [str(P/'tests'), str(P)]
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
from greekocr.harvest.line_pipeline import PIPELINE_VERSION, canonical
from greekocr.harvest.line_pipeline_census import run, verify_versions
from test_line_pipeline import row, census_config, segment


def file_sha(p):
    with Path(p).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--witness-dir', type=Path, default=D/'readout_contract_witness')
    root = parser.parse_args().witness_dir.resolve()
    if D.resolve() not in root.parents:
        raise ValueError('witness directory must stay inside census05')
    if root.exists():
        raise FileExistsError('preserve prior witness; refuse overwrite')
    root.mkdir()
    r = row('1234')
    r.update(primary_class='numerics_tables', script_class='nonletter')
    config = census_config(root, [r])
    config.update(versions=str(P/'docs/harvest/line_pipeline/tool_versions.json'),
        codec=str(P/'greekocr/_vendor/codec/v2.json'), routes_out_of_scope=['polytonic'])
    manifest = json.loads(Path(config['versions']).read_text())['tools']
    roots = {p.name: str(p) for p in P.parent.iterdir() if p.is_dir()}
    config['component_roots'] = roots
    verify_versions(manifest, roots)
    version = manifest['segmentation']['version']
    def observe(record):
        return dict(segment(record), tool_version=version)
    result = run(config, root/'attempt', execute=True, segmenter_factory=lambda: observe)
    assert result['complete'] and result['input_rows'] == 1
    decision = json.loads((root/'attempt/decisions.jsonl').read_text())
    assert decision['pipeline_version'] == PIPELINE_VERSION == '0.3.2'
    assert decision['disposition'] == 'ADMIT'
    script = D/'readout/census_readout.py'
    before = file_sha(script)
    command = [sys.executable, '-B', str(script), '--run', str(root/'attempt'),
               '--out', str(root/'reports'), '--expect-rows', '1']
    proc = subprocess.run(command, text=True, capture_output=True)
    (root/'readout.stdout').write_text(proc.stdout)
    (root/'readout.stderr').write_text(proc.stderr)
    report = json.loads((root/'reports/readout.json').read_text())
    failures = {k: v for k,v in report['invariants'].items() if v['status'] != 'PASS'}
    assert proc.returncode == 1
    assert failures == {'pipeline_version_mismatch': {'status': 'FAIL', 'count': 1}}, failures
    inside = subprocess.run([sys.executable, '-B', str(script), '--run', str(root/'attempt'),
        '--out', str(root/'attempt/readout')], text=True, capture_output=True)
    assert inside.returncode != 0 and 'output must be outside the read-only run directory' in inside.stderr
    (root/'inside_attempt.stderr').write_text(inside.stderr)
    assert before == file_sha(script)
    receipt = dict(status='BLOCKED_UNCHANGED_READOUT_CONTRACT', code_sha='3b4090bf9b15d2d2cac53ee55161e936157ec0e5',
        pipeline_version=PIPELINE_VERSION, tool_manifest_valid=True, rows=1, disposition=decision['disposition'],
        mock_boundary='native I/O only: existing CODE_SHA test_line_pipeline.segment fixture; no readers',
        config=config, readout_script=str(script.relative_to(R)), readout_sha256=before,
        readout_unmodified=True, argv=command, exit_code=proc.returncode,
        failures=failures, invariants=report['invariants'], last_line=proc.stdout.strip(),
        inside_attempt_output_refused=True,
        not_qualification='one-row compatibility witness; not the requested 200-real-row batch mock')
    (D/'readout_contract_audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','pipeline_version','exit_code','failures','last_line')},indent=2))

if __name__ == '__main__':
    main()
