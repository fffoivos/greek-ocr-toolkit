import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from unittest.mock import patch
import pytest
PKG=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PKG))
from common import atomic,bound,read,sha
from test_package import mock_runtime
from test_stage_b import digest_state
import stage_c as c


def test_adoption_exact_horizons_and_four_quarter_points(tmp_path):
    runtime=mock_runtime(tmp_path)
    r=read(runtime); r['train_rows']=793227; atomic(runtime,r)
    for winner,updates,cer in [('w1-h13',49584,[12396,24792,37188,49584]),
        ('w1.5-h14',49584,[12396,24792,37188,49584]),
        ('w2-h04',198312,[49578,99156,148734,198312])]:
        conf=c.make_run(runtime,winner)
        source=read(PKG/'adopted'/(winner+'.json'))
        for k in ('lr','beta1','wd','bs','width_mult','seed','workers'):
            assert conf['parameters'][k]==source['parameters'][k]
        assert conf['total_updates']==updates
        assert conf['target_drawn_lines']==12691632
        assert conf['cer_steps']==cer
        assert conf['durable_every']==20
        assert 12691632//50000+1==254
    assert read(PKG/'adopted/w2-h04.json')['parameters']['lr']==0.0003692322353070561


def spawn(config,out,extra=None):
    out.mkdir(exist_ok=True)
    with (out/'process.log').open('a') as log:
        return subprocess.Popen([sys.executable,'-B',str(PKG/'tests/stage_c_mock_worker.py'),
            '--config',str(config),'--out',str(out)],stdout=log,stderr=log,
            env={**os.environ,'SLURM_JOB_ID':'1234','SLURM_RESTART_COUNT':'0',
                'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1',
                'VECLIB_MAXIMUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1',**(extra or {})})


@pytest.mark.parametrize('winner',c.WINNERS)
def test_real_TERM_durable_resume_identity_and_fast_cursor(tmp_path,winner):
    runtime=mock_runtime(tmp_path)
    config=tmp_path/'config.json'
    atomic(config,c.make_run(runtime,winner,smoke=True,fixture=True))
    control,resumed=tmp_path/'control',tmp_path/'resumed'
    proc=spawn(config,control)
    assert proc.wait(timeout=50)==0,(control/'process.log').read_text()
    proc=spawn(config,resumed,{'TRAIN_FULL_TEST_PAUSE_LOSS_STEP':'2'})
    deadline=time.monotonic()+40
    while not (resumed/'TEST_PAUSED.json').exists() and proc.poll() is None and time.monotonic()<deadline:
        time.sleep(.02)
    if not (resumed/'TEST_PAUSED.json').exists():
        proc.kill();proc.wait()
        pytest.fail((resumed/'process.log').read_text())
    # Actual OS TERM reaches Segment while save/evaluation is running. It is
    # handled, never sent to an srun launcher. Controller path tested below.
    proc.send_signal(signal.SIGTERM)
    assert proc.wait(timeout=30)==75,(resumed/'process.log').read_text()
    yielded=read(next(resumed.glob('YIELD_*.json')))
    assert yielded['checkpoint']
    prefix=(resumed/'loss_eval.jsonl').read_bytes()
    proc=spawn(config,resumed,{'SLURM_RESTART_COUNT':'1'})
    assert proc.wait(timeout=50)==0,(resumed/'process.log').read_text()
    assert digest_state(control)[0]==digest_state(resumed)[0]
    assert (resumed/'loss_eval.jsonl').read_bytes().startswith(prefix)
    for step in (2,4,6,8):
        left,right=(read(folder/'loss_eval'/('step-%09d.json'%step)) for folder in (control,resumed))
        assert left['instruments']==right['instruments']
        assert set(left['instruments'])==set(c.PANELS)
    for step in read(config)['cer_steps']:
        assert read(control/'eval'/('step-%09d.json'%step))['instruments']==read(resumed/'eval'/('step-%09d.json'%step))['instruments']


def test_controller_warning_before_start_no_new_lane(tmp_path,monkeypatch):
    runtime=mock_runtime(tmp_path)
    p=c.build(runtime,tmp_path/'plan',smoke=True,fixture=True)
    monkeypatch.setattr(c,'checked',lambda _:p)
    stop=tmp_path/'stop';stop.write_text('TERM')
    monkeypatch.setenv('TF_C_STOP',str(stop))
    assert c.node(tmp_path/'plan/PLAN.json',0,popen=lambda _:pytest.fail('new lane after warning'))==75


@pytest.mark.parametrize('code',[0,75,137,1])
def test_controller_warning_during_step_creation_never_signals_srun(tmp_path,monkeypatch,code):
    runtime=mock_runtime(tmp_path)
    p=c.build(runtime,tmp_path/'plan',smoke=True,fixture=True)
    monkeypatch.setattr(c,'checked',lambda _:p)
    monkeypatch.setattr(c,'complete',lambda *args: {})
    stop=tmp_path/'stop'
    monkeypatch.setenv('TF_C_STOP',str(stop));monkeypatch.setenv('SLURM_JOB_ID','123')
    output=Path(p['runs'][0]['output'])
    atomic(output/'YIELD_1.json',dict(checkpoint=None))
    class Proc:
        def poll(self): return code
        def wait(self): return code
        def send_signal(self,*_): pytest.fail('srun signalled')
        def terminate(self): pytest.fail('srun terminated')
    def launch(cmd):
        assert '--gpus-per-node=1' in cmd and '--cpus-per-task=24' in cmd
        # Signal just as srun begins step creation, repeat it too.
        signal.raise_signal(signal.SIGTERM);signal.raise_signal(signal.SIGTERM)
        assert stop.exists()
        return Proc()
    if code in (0,75):
        assert c.node(tmp_path/'plan/PLAN.json',0,popen=launch)==code
    else:
        with pytest.raises(RuntimeError,match='unexpected lane'):
            c.node(tmp_path/'plan/PLAN.json',0,popen=launch)


def test_shared_stop_file_is_consumed_at_optimizer_boundary(tmp_path):
    from full_hook import segment_class
    class Base:
        requested=False
        def request_stop(self): self.requested=True
        def stop(self,step): return self.requested
    cls=segment_class(Base,{}, {})
    obj=object.__new__(cls)
    from types import SimpleNamespace
    obj.args=SimpleNamespace(stage_c=True)
    stop=tmp_path/'stop'
    with patch.dict(os.environ,TF_C_STOP=str(stop)):
        assert not obj.stop(1)
        stop.write_text('TERM')
        assert obj.stop(2)


def test_actual_batch_shell_repeated_TERM_waits_then_requeues_once(tmp_path):
    # Execute the real .sbatch wrapper with tiny stand-ins for Python/Slurm.
    pkg=tmp_path/'pkg';pkg.mkdir()
    script=tmp_path/'python'
    script.write_text('''#!/usr/bin/env python3
import os,sys,time
from pathlib import Path
if sys.argv[-1].endswith('verify.py'): raise SystemExit(0)
p=Path(os.environ['TF_C_STOP'])
Path(os.environ['STARTED']).write_text('started')
while not p.exists(): time.sleep(.01)
time.sleep(.25)
Path(os.environ['DURABLE']).write_text('checkpoint closed')
raise SystemExit(75)
''');script.chmod(0o755)
    (pkg/'runtime_env.sh').write_text('export TF_PYTHON="'+str(script)+'"\n')
    squeue=tmp_path/'squeue'
    squeue.write_text('#!/bin/bash\ntest "$SLURM_TIME_FORMAT" = standard || exit 1\necho 1793100000\n');squeue.chmod(0o755)
    date=tmp_path/'date';date.write_text('#!/bin/bash\necho 1793100000\n');date.chmod(0o755)
    scontrol=tmp_path/'scontrol'
    scontrol.write_text('#!/bin/bash\ntest -f "$DURABLE" || exit 3\necho "$*" >> "$REQUEUES"\n');scontrol.chmod(0o755)
    env={**os.environ,'TF_PACKAGE':str(pkg),'SLURM_JOB_ID':'777','SLURM_RESTART_COUNT':'0',
        'PATH':str(tmp_path)+':'+os.environ['PATH'],'SLURM_TIME_FORMAT':'relative',
        'STARTED':str(tmp_path/'started'),'DURABLE':str(tmp_path/'durable'),'REQUEUES':str(tmp_path/'requeues')}
    proc=subprocess.Popen(['bash',str(PKG/'stage_c.sbatch'),str(tmp_path/'PLAN.json'),'0'],env=env)
    deadline=time.monotonic()+8
    while not (tmp_path/'started').exists() and proc.poll() is None and time.monotonic()<deadline: time.sleep(.02)
    assert (tmp_path/'started').exists()
    proc.send_signal(signal.SIGTERM);time.sleep(.05);proc.send_signal(signal.SIGTERM)
    assert proc.wait(timeout=10)==0
    assert (tmp_path/'requeues').read_text().splitlines()==['requeue 777']


def test_submit_nonexclusive_one_GPU_and_owner_budget_go(tmp_path,monkeypatch):
    runtime=mock_runtime(tmp_path)
    plan=tmp_path/'full/PLAN.json'
    p=c.build(runtime,plan.parent,fixture=True)
    monkeypatch.setattr(c,'checked',lambda _:p)
    review,smoke=tmp_path/'REVIEW.json',tmp_path/'SMOKE.json'
    atomic(smoke,dict(status='BIT_IDENTICAL',mock=False,package_sha256=p['payload_sha256'],runtime_sha256=p['runtime']['sha256']))
    r=dict(status='PASS',plan_sha256=sha(plan),package_sha256=p['payload_sha256'],smoke_sha256=sha(smoke))
    atomic(review,r)
    with pytest.raises(ValueError,match='350 GPU-h'): c.submit(plan,review,smoke)
    atomic(review,dict(r,budget_extension_owner_go=True))
    calls=[]
    def command(cmd,**kw):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd,0,stdout='9876\n')
    c.submit(plan,review,smoke,command=command)
    assert len(calls)==6 and all('--time=23:00:00' in x for x in calls)
    c.submit(plan,review,smoke,command=command)
    assert len(calls)==6
    shell=(PKG/'stage_c.sbatch').read_text()
    assert '#SBATCH --exclusive' not in shell
    assert '#SBATCH --gpus-per-node=1' in shell


def test_fast_resume_skips_decoding_consumed_prefix(tmp_path):
    import torch
    from types import SimpleNamespace
    from full_hook import segment_class
    class Dataset(torch.utils.data.Dataset):
        def __init__(self): self.seen=[]
        def __len__(self): return 8
        def __getitem__(self,i): self.seen.append(i); return i
    ds=Dataset();loader=torch.utils.data.DataLoader(ds,batch_sampler=[[0,1],[2,3],[4,5],[6,7]])
    cls=segment_class(object,{}, {})
    obj=object.__new__(cls)
    obj.args=SimpleNamespace(stage_c=True);obj.saved=None
    assert [r.tolist() for r in obj.iterator(loader,1,2)]==[[4,5],[6,7]]
    assert ds.seen==[4,5,6,7]


def test_killed_allocations_require_unique_measured_step_and_keep_global_GPU_checks(tmp_path,monkeypatch):
    import stage_c_isolation as iso
    out=tmp_path/'run';out.mkdir()
    a=dict(physical_host='nid1',step_id='0',gpu_uuid='GPU1',cpu_affinity=list(range(24)),
        cuda_visible_devices='0',started_unix=101.5,job_id='123',restart_count=1)
    atomic(out/'ALLOCATION_1.json',a)
    p=dict(runs=[dict(output=str(out))]);path=tmp_path/'PLAN.json';atomic(path,p)
    monkeypatch.setattr(c,'checked',lambda _:p)
    capture=tmp_path/'sacct.txt'
    text='123|123|PREEMPTED|0:0|100|200|100|nid1|1|cpu=24,gres/gpu=1|cpu=24,gres/gpu=1\n123.0|123.0|CANCELLED|0:9|101|180|79|nid1|||cpu=24,gres/gpu=1\n'
    capture.write_text(text)
    report=iso.reconcile(path,capture,sha(capture))
    assert report['measured_recoveries'][0]['measured_end_unix']==180
    assert 'ended_unix' not in read(out/'ALLOCATION_1.json')
    with pytest.raises(ValueError,match='SHA'):iso.reconcile(path,capture,'wrong')
    capture.write_text(text+text.splitlines()[1]+'\n')
    with pytest.raises(ValueError,match='nonunique'):iso.reconcile(path,capture,sha(capture))
    capture.write_text(text)
    atomic(out/'ALLOCATION_2.json',dict(a,physical_host='nid2',started_unix=170.,ended_unix=190.))
    with pytest.raises(ValueError,match='GPU_GLOBAL'):iso.reconcile(path,capture,sha(capture))
    atomic(out/'ALLOCATION_2.json',dict(a,gpu_uuid='GPU2',started_unix=170.,ended_unix=190.))
    with pytest.raises(ValueError,match='CPU_SAME_HOST'):iso.reconcile(path,capture,sha(capture))
