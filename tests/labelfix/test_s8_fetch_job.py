"""S8a3 resume, custody, failure checkpoints and compute-only boundary."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.labelfix import s8_fetch_job as job
from scripts.labelfix import s8_fetch_l1m as l1m


@pytest.fixture
def fixture_job(tmp_path):
    config = job.make_mock(tmp_path / 'fixture')
    config['workers'] = 2
    return config


@pytest.mark.skipif(os.environ.get('CODEX_SANDBOX') == 'seatbelt',
                    reason='macOS seatbelt sandbox timeout: spawn Pool(16).terminate() hangs in worker join (stdlib-only reproduction); S8 subprocess exceeds 45s')
def test_exact_job_entrypoint_mock(tmp_path):
    receipt = tmp_path / 'mock.json'
    proc = subprocess.run([sys.executable, '-B', 'scripts/labelfix/s8_fetch_job.py',
                           'mock', '--receipt', str(receipt)], capture_output=True, text=True, timeout=45)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(receipt.read_text())
    assert result['mock_ok'] and result['completed_resume_ok'] and result['input_hashes_unchanged']
    assert result['initial']['BE'] == 1
    assert result['final']['BE'] == result['final']['A'] == 3
    assert result['final']['alignments'] == 2 and result['final']['merged_alignments'] == 3
    assert result['inference_runs'] == result['input_writes'] == 0


@pytest.mark.parametrize('mutation', ['request', 'checkpoint', 'cache'])
def test_mismatched_custody_rejected_without_checkpoint_write(fixture_job, mutation):
    config = fixture_job
    out = Path(config['out'])
    if mutation == 'request':
        path = out / 'request.json'
        data = json.loads(path.read_text())
        data['ids'].append('wrong')
        job.atomic_json(path, data)
    elif mutation == 'checkpoint':
        path = out / 'partial.json.gz'
        data = job.read_gzip(path)
        data['request_sha256'] = '0' * 64
        job.atomic_json(path, data, compressed=True)
    else:
        config['local_alignment_sha256'] = '0' * 64
    before = job.sha(out / 'partial.json.gz')
    with pytest.raises(ValueError, match='SHA mismatch'):
        job.run(config, mock=True)
    assert job.sha(out / 'partial.json.gz') == before
    assert not (out / 'remote.json.gz').exists()


def test_mid_shard_checkpoint_is_reconciled(fixture_job):
    config = fixture_job
    out = Path(config['out'])
    data = job.read_gzip(out / 'partial.json.gz')
    path = Path(config['base']) / 'l1e_20261017/output_3679545/inference/shard-00001-combined.jsonl.gz'
    result = l1m.s8_read_shard(('BE', str(path), {'two'}, {}))
    data['runtime'].update(result[2])  # S8a2 timeout before appending BE_done.
    job.atomic_json(out / 'partial.json.gz', data, compressed=True)
    assert job.run(config, mock=True)['complete']


def test_A_mismatch_saves_partial_and_is_resumable(fixture_job):
    config = fixture_job
    out = Path(config['out'])
    path = Path(config['base']) / 'output_3679313/combined/shard-00001-combined.jsonl.gz'
    original = path.read_bytes()
    rows = [json.loads(line) for line in gzip.decompress(original).splitlines()]
    rows[-1]['coverage'] = []
    path.write_bytes(gzip.compress(('\n'.join(json.dumps(row) for row in rows) + '\n').encode()))
    with pytest.raises(ValueError, match='historical A mismatch'):
        job.run(config, mock=True)
    data = job.read_gzip(out / 'partial.json.gz')
    assert len(data['BE_done']) == 3
    assert 'shard-00001-combined.jsonl.gz' not in data['A_done']
    assert not data['runtime']['two'].get('historical_A_verified')
    assert not json.loads((out / 'receipt.json').read_text())['complete']
    assert not (out / 'remote.json.gz').exists()
    path.write_bytes(original)
    assert job.run(config, mock=True)['complete']


def test_deadline_keeps_checkpoint(fixture_job):
    config = dict(fixture_job, budget_seconds=0)
    with pytest.raises(TimeoutError, match='budget exhausted'):
        job.run(config, mock=True)
    out = Path(config['out'])
    assert job.read_gzip(out / 'partial.json.gz')['BE_done'] == ['shard-00000-combined.jsonl.gz']
    assert not json.loads((out / 'receipt.json').read_text())['complete']
    assert not (out / 'remote.json.gz').exists()


@pytest.mark.skipif(os.environ.get('CODEX_SANDBOX') == 'seatbelt',
                    reason='macOS seatbelt sandbox timeout: spawn Pool(16).terminate() hangs in worker join (stdlib-only reproduction); S8 subprocess exceeds 30s')
def test_deadline_terminates_inflight_pool(fixture_job):
    config = dict(fixture_job, budget_seconds=0.02, workers=16)
    # A subprocess timeout makes a shutdown regression fail instead of hanging
    # the whole detector/reader suite after its native runtimes have loaded.
    code = 'import json,sys; from scripts.labelfix.s8_fetch_job import run; run(json.loads(sys.argv[1]), mock=True)'
    proc = subprocess.run([sys.executable, '-B', '-c', code, json.dumps(config)],
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode != 0 and 'budget exhausted' in proc.stderr
    out = Path(config['out'])
    assert not json.loads((out / 'receipt.json').read_text())['complete']
    assert not (out / 'remote.json.gz').exists()


def test_login_and_output_input_overlap_rejected(fixture_job, monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID', raising=False)
    with pytest.raises(ValueError, match='debug compute allocation'):
        job.allocation_guard(dict(fixture_job, base=str(job.BASE), out=str(job.OUT)))
    with pytest.raises(ValueError, match='dedicated'):
        job.load_resume(dict(fixture_job, out=str(Path(fixture_job['base']) / 'output_3679313')))


def test_sbatch_guard_never_invokes_srun_on_login():
    env = {k: v for k, v in os.environ.items() if not k.startswith('SLURM_')}
    proc = subprocess.run(['bash', 'scripts/labelfix/clariden/s8_fetch_job.sbatch'],
                          env=env, capture_output=True, text=True)
    assert proc.returncode == 2
    assert 'never run on login node' in proc.stderr


def test_selected_fields_and_crop_key_join(fixture_job):
    config = fixture_job
    job.run(config, mock=True)
    final = job.read_gzip(Path(config['out']) / 'remote.json.gz')
    assert set(final['runtime']) == set(final['alignments']) == {'one', 'two', 'three'}
    assert all('detector' not in row and row['historical_A_verified'] for row in final['runtime'].values())
    assert all(row['peer_predictions'] == {'B': [], 'E': []} for row in final['runtime'].values())
    assert final['alignments']['two']['crop'].startswith('/old/worktree/')
    assert all('receipt_sha256' in p for p in final['provenance'] if p['kind'] in ('A', 'BE'))
