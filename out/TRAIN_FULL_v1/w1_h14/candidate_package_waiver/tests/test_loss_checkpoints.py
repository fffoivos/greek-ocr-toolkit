"""Real trainer, stochastic tiny model: retention crash windows and custody."""
import os
from pathlib import Path
import signal
import sys
import time
import pytest

PKG=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PKG))
from common import atomic,bound,read,sha,spec
from test_package import mock_runtime
from test_stage_c import spawn
from test_stage_b import digest_state
import stage_c as c


@pytest.mark.parametrize('winner',c.WINNERS)
@pytest.mark.parametrize('window',('ARCHIVE','LOSS'))
def test_kill_after_archive_or_loss_never_replaces_or_skips_checkpoint(tmp_path,winner,window):
    runtime=mock_runtime(tmp_path)
    config=tmp_path/'config.json'
    atomic(config,c.make_run(runtime,winner,smoke=True,fixture=True))
    control,resumed=tmp_path/'control',tmp_path/'resumed'
    proc=spawn(config,control)
    assert proc.wait(timeout=50)==0,(control/'process.log').read_text()
    proc=spawn(config,resumed,{f'TRAIN_FULL_TEST_PAUSE_{window}_STEP':'2'})
    deadline=time.monotonic()+40
    while not (resumed/'TEST_PAUSED.json').exists() and proc.poll() is None and time.monotonic()<deadline:
        time.sleep(.02)
    if not (resumed/'TEST_PAUSED.json').exists():
        proc.kill();proc.wait()
        pytest.fail((resumed/'process.log').read_text())
    target=resumed/'loss_checkpoints/step-000000002.pt'
    before=(sha(target),target.stat().st_mtime_ns,target.stat().st_ino)
    proc.kill();assert proc.wait(timeout=10)==-signal.SIGKILL
    proc=spawn(config,resumed,{'SLURM_RESTART_COUNT':'1'})
    assert proc.wait(timeout=50)==0,(resumed/'process.log').read_text()
    assert (sha(target),target.stat().st_mtime_ns,target.stat().st_ino)==before
    assert digest_state(control)[0]==digest_state(resumed)[0]
    from loss_journal import records
    from loss_checkpoint import validate
    from train import train as trainer
    trainer._runtime()
    for out in (control,resumed):
        done=c.complete(out,read(config))
        events,torn=records(out/'loss_eval.jsonl')
        assert torn is None and [r['step'] for r in events]==[2,4,6,8]
        assert len(list((out/'loss_checkpoints').glob('*.pt')))==4
        assert len(done['loss_checkpoints'])==4
        for event in events:
            r=read(bound(event['record']))
            assert event['checkpoint']==r['checkpoint']
            ck=validate(r['checkpoint'],trainer,step=r['step'],drawn_lines=r['drawn_lines'],
                runtime_sha=r['runtime_sha256'],model_sha=r['model_sha256'])
            assert all(k not in ck for k in ('opt','sched','rng'))
            assert ck['codec_json'] and ck['config']['width_mult']==read(config)['parameters']['width_mult']
            # Same weights-only wrapper is accepted by the frozen loader.
            from train.ckpt_io import load_model_weights
            state,meta=load_model_weights(str(bound(r['checkpoint'])))
            assert trainer.checkpoint_state_sha256(state)==r['model_sha256']
            assert meta['width_mult']==ck['width_mult']
        for s in done['binding']['evaluation_steps']:
            assert (out/'checkpoints'/('step-%09d.pt'%s)).exists()
        assert (out/'last.pt').exists()
    # Every archive has the same model as its uninterrupted twin.
    for a,b in zip(read(control/'COMPLETE.json')['loss_evaluations'],read(resumed/'COMPLETE.json')['loss_evaluations']):
        assert read(bound(a))['model_sha256']==read(bound(b))['model_sha256']
    target.write_bytes(b'corrupt retained checkpoint')
    with pytest.raises(ValueError,match='SHA'): c.complete(resumed,read(config))


def test_atomic_archive_interrupted_before_rename_is_not_published(tmp_path,monkeypatch):
    import torch
    from types import SimpleNamespace
    from train import train as trainer
    from loss_checkpoint import retain
    trainer._runtime()
    model=torch.nn.Linear(2,3)
    segment=SimpleNamespace(path=tmp_path/'segment.pt',t=trainer,model=model,draws=128,
        binding=dict(width_mult=1.),args=SimpleNamespace(codec=str(PKG/'vendor/codec/v2.1.json'),
            arch='compact',width_mult=1.,head='nfd',seed=0))
    model_sha=trainer.checkpoint_state_sha256(model.state_dict())
    original=torch.save
    def interrupted(value,stream):
        stream.write(b'torn archive')
        raise RuntimeError('interrupted write')
    monkeypatch.setattr(torch,'save',interrupted)
    with pytest.raises(RuntimeError,match='interrupted'):retain(segment,2,'runtime',model_sha)
    target=tmp_path/'loss_checkpoints/step-000000002.pt'
    assert not target.exists()
    monkeypatch.setattr(torch,'save',original)
    entry,cost=retain(segment,2,'runtime',model_sha)
    assert bound(entry)==target and cost['created']
    before=(sha(target),target.stat().st_mtime_ns)
    entry,cost=retain(segment,2,'runtime',model_sha)
    assert not cost['created'] and (sha(target),target.stat().st_mtime_ns)==before
    segment.draws=129
    with pytest.raises(ValueError,match='binding'): retain(segment,2,'runtime',model_sha)


def test_forecast_includes_retention_and_durable_save_upper_bound(tmp_path):
    from forecast import forecast
    evidence=PKG.parent/'evidence'
    report=forecast(evidence,tmp_path/'forecast.json')
    for row in report['costs']:
        assert row['retained_loss_checkpoints']==254
        assert row['loss_checkpoint_total_bytes_estimate']==254*row['loss_checkpoint_bytes_estimate']
        assert row['loss_checkpoint_GPU_h']==254/3600
        assert row['checkpoint_GPU_h']>row['loss_checkpoint_GPU_h']
        assert row['durable_saves_upper_bound']>=row['updates']//20+254
