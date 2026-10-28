"""Offline scheduler boundary and exact operational-parent compatibility."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import atomic, read, sha, spec
import verify


def executable(path, text):
    path.write_text(text)
    path.chmod(0o755)


@pytest.mark.parametrize('standard,relative', [
    ('2026-10-25T23:59:00', '23:59'),
    ('2026-10-26T10:05:00', 'Tomorr 10:05'),
    ('2032-03-04T10:05:00', '2032-03-04')])
@pytest.mark.parametrize('wrapper', ['job.sbatch', 'stage_b.sbatch'])
def test_actual_job_wrapper_overrides_relative_time(tmp_path, standard, relative, wrapper):
    """Execute the real shell wrapper; scheduler and GNU date are local stubs."""
    package, bins = tmp_path / 'pkg', tmp_path / 'bin'
    package.mkdir()
    bins.mkdir()
    (package / 'runtime_env.sh').write_text('export PYTHONPATH="$TF_PACKAGE"\n')
    (package / 'verify.py').write_text('print("TRAIN_FULL_PAYLOAD_VERIFIED")\n')
    (package / 'segment.py').write_text(
        'import json, os\nfrom pathlib import Path\n'
        'Path(os.environ["RESULT"]).write_text(json.dumps(dict('
        'deadline=os.environ["S1_DEADLINE_EPOCH"], time_format=os.environ["SLURM_TIME_FORMAT"])))\n')
    (package / 'stage_b.py').write_text((package / 'segment.py').read_text())
    prefix = '#!' + sys.executable + '\n'
    executable(bins / 'squeue', prefix +
        'import json, os, sys\nfrom pathlib import Path\n'
        'assert sys.argv[1:]==["-h","-j","3749193","-o","%e"]\n'
        'Path(os.environ["SQUEUE_TRACE"]).write_text(os.environ["SLURM_TIME_FORMAT"])\n'
        'print(os.environ["STANDARD"] if os.environ["SLURM_TIME_FORMAT"]=="standard" else os.environ["RELATIVE"])\n')
    executable(bins / 'date', prefix +
        'import datetime, sys\nassert sys.argv[1]=="-d" and sys.argv[3]=="+%s"\n'
        'print(int(datetime.datetime.strptime(sys.argv[2], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()))\n')
    executable(bins / 'srun', '#!/usr/bin/env bash\nshift 3\nexec "$@"\n')
    result = tmp_path / 'result.json'
    trace = tmp_path / 'squeue.txt'
    env = {**os.environ, 'PATH': str(bins) + ':' + os.environ['PATH'],
        'TF_PACKAGE': str(package), 'TF_RUNTIME': str(tmp_path / 'runtime.json'),
        'TF_OUTPUT': str(tmp_path / 'output'), 'TF_PYTHON': sys.executable,
        'SLURM_JOB_ID': '3749193', 'SLURM_TIME_FORMAT': 'relative',
        'STANDARD': standard, 'RELATIVE': relative, 'RESULT': str(result), 'SQUEUE_TRACE': str(trace)}
    process = subprocess.run(['bash', str(PKG / wrapper), 'mock-plan.json', '0'], env=env, text=True, capture_output=True)
    assert process.returncode == 0, process.stdout + process.stderr
    expected = int(datetime.datetime.fromisoformat(standard).replace(tzinfo=datetime.timezone.utc).timestamp())
    assert read(result) == dict(deadline=str(expected), time_format='relative')
    assert trace.read_text() == 'standard'


def test_original_runtime_data_binds_but_x2_smoke_does_not():
    proof = verify.data_compatibility()
    assert proof['parent_sha256'] == verify.X2_SHA
    assert not verify.package_matches(verify.PARENT_SHA)
    assert not verify.package_matches(verify.X2_SHA)
    assert verify.package_matches(sha(PKG / 'PAYLOAD.json'))
    evidence = PKG.parents[3] / 'out/TRAIN_FULL_v1/receipts_005'
    runtime = evidence / 'data_prepared_runtime.json'
    assert verify.data_package_matches(read(runtime)['package_sha256'], runtime)
    rt = read(runtime)
    assert {n: rt['pools'][n]['rows'] for n in ('seal04_dev', 'seal04_test', 'harvest_dev', 'harvest_test')} == dict(
        seal04_dev=437, seal04_test=2253, harvest_dev=16350, harvest_test=52847)
    with pytest.raises(ValueError, match='exact prepared005'):
        verify.data_package_matches(verify.PARENT_SHA, evidence / 'SMOKE_IDENTITY.json')


@pytest.mark.parametrize('target', ['recipe.json', 'job.sbatch', 'common.py', 'horizon.py', 'manifest.py', 'prepare.py',
                                   'launch_parent_payload.json', 'x2_recipe.json'])
def test_compatibility_refuses_even_resealed_extra_changes(tmp_path, monkeypatch, target):
    root = tmp_path / 'package'
    shutil.copytree(PKG, root, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    monkeypatch.setattr(verify, 'ROOT', root)
    path = root / target
    path.write_text((path.read_text() if path.exists() else '') + '\n# undeclared change\n')
    payload = read(root / 'PAYLOAD.json')
    payload['files'][target] = dict(bytes=path.stat().st_size, sha256=sha(path))
    atomic(root / 'PAYLOAD.json', payload)
    with pytest.raises((ValueError, KeyError)):
        verify.data_compatibility()


def test_train_submission_requires_new_review_and_new_x1_smoke(tmp_path, monkeypatch):
    import chain
    runtime = tmp_path / 'runtime.json'
    atomic(runtime, dict(package_sha256=sha(PKG / 'PAYLOAD.json')))
    smoke = tmp_path / 'smoke.json'
    atomic(smoke, dict(status='BIT_IDENTICAL', mock=False, runtime_sha256=sha(runtime),
                      package_sha256=sha(PKG / 'PAYLOAD.json')))
    review = tmp_path / 'review.json'
    current = dict(verdict='PASS', package_sha256=sha(PKG / 'PAYLOAD.json'),
                   runtime_sha256=sha(runtime), smoke_identity=spec(smoke))
    args = argparse.Namespace(runtime=str(runtime), out=str(tmp_path / 'train'),
        controls=str(tmp_path / 'controls-new'), segment=1, prior=None, mode='train',
        review=str(review), owner_go=True)
    atomic(review, {**current, 'package_sha256': verify.PARENT_SHA})
    with pytest.raises(ValueError, match='Astra package'):
        chain.submit(args)
    atomic(review, current)
    s = read(smoke)
    atomic(smoke, dict(s, package_sha256=verify.PARENT_SHA))
    atomic(review, dict(current, smoke_identity=spec(smoke)))
    with pytest.raises(ValueError, match='another data population or package'):
        chain.submit(args)
    atomic(smoke, s)
    atomic(review, dict(current, smoke_identity=spec(smoke)))
    calls = []
    def command(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout='' if '--test-only' in argv else '999;cluster\n')
    assert chain.submit(args, command=command) == '999'
    assert len(calls) == 2 and '--test-only' in calls[0]
    assert [x for x in calls[0] if x != '--test-only'] == calls[1]
    with pytest.raises(ValueError, match='existing submission'):
        chain.submit(args, command=command)
