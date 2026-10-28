"""Focused checks outside the seal: only a Slurm memory directive changes."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

BASE = Path(__file__).resolve().parents[2]
PKG = BASE/'stage_c_package'
sys.path.insert(0, str(BASE/'memory_fix'))
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(PKG/'tests'))
import carry_smoke as carry


def old_package(tmp_path):
    root = tmp_path/'old-package'
    root.mkdir()
    payload = carry.read(BASE/'evidence/STAGE_C_PRE_MEMORY_PAYLOAD.json')
    for name in payload['files']:
        dest = root/name
        dest.parent.mkdir(exist_ok=True, parents=True)
        if name == 'stage_c.sbatch':
            dest.write_bytes((BASE/'evidence/STAGE_C_PRE_MEMORY.sbatch').read_bytes())
        else:
            # No bulk fixture/cache; same source bytes in a disposable directory.
            dest.write_bytes((PKG/name).read_bytes())
    (root/'PAYLOAD.json').write_bytes((BASE/'evidence/STAGE_C_PRE_MEMORY_PAYLOAD.json').read_bytes())
    return root


def test_exact_operational_diff_and_byte_identical_training(tmp_path):
    old = old_package(tmp_path)
    proof = carry.delta(old, PKG)
    assert proof['changed'] == ['stage_c.sbatch']
    text = (PKG/'stage_c.sbatch').read_text()
    assert '#SBATCH --mem=110G\n' in text
    assert '#SBATCH --exclusive' not in text
    assert 4*110 <= 450
    (old/'stage_c.py').write_text('changed')
    with pytest.raises(ValueError, match='payload mismatch'):
        carry.delta(old, PKG)


def test_memory_only_rejects_different_directive_even_with_resealed_manifest(tmp_path, monkeypatch):
    old = old_package(tmp_path)
    new = tmp_path/'different'
    new.mkdir()
    before = carry.seal(old, carry.OLD_SHA)
    after = copy.deepcopy(before)
    after['files']['stage_c.sbatch'] = dict(bytes=999, sha256='different')
    (new/'stage_c.sbatch').write_text((old/'stage_c.sbatch').read_text()+'\n#SBATCH --exclusive\n')
    monkeypatch.setattr(carry, 'seal', lambda root, _: before if Path(root) == old else after)
    with pytest.raises(ValueError, match='shell diff'):
        carry.delta(old, new)
    after['files']['stage_c.py'] = dict(bytes=999, sha256='different')
    with pytest.raises(ValueError, match='exceeds memory-only'):
        carry.delta(old, new)


@pytest.mark.parametrize('value,expected', [('1048576K', 1024**3), ('20G',20*1024**3),
                                         ('1.5T',1.5*1024**4), ('100',100)])
def test_slurm_RSS_units(value, expected):
    assert carry.rss_bytes(value) == expected


def memory_fixture(tmp_path):
    runs=[]
    lines=[]
    for i,name in enumerate(('w1-control','w1-requeue','w1.5-control','w1.5-requeue','w2-control','w2-requeue')):
        out=tmp_path/name;out.mkdir()
        config=out/'config.json';config.write_text(json.dumps(dict(parameters=dict(workers=6))))
        (out/'ALLOCATION_1.json').write_text(json.dumps(dict(job_id=str(i+1),step_id='0')))
        runs.append(dict(name=name,output=str(out),config=carry.spec(config)))
        lines.append(f'{i+1}.0|{i+1}.0|COMPLETED|nid1|20000000K|0|nid1|450Gn|cpu=24,mem=450G,gres/gpu=1|1')
    capture=tmp_path/'rss.txt';capture.write_text('\n'.join(lines)+'\n')
    return dict(runs=runs),capture


def test_memory_evidence_covers_six_lanes_and_keeps_accounting_limitations(tmp_path):
    plan,capture=memory_fixture(tmp_path)
    report=carry.memory_report(plan,capture,carry.sha(capture))
    assert len(report['per_lane'])==6
    assert all(r['headroom_bytes']>0 for r in report['per_lane'])
    assert 'all six workers' in report['limitation']
    with pytest.raises(ValueError,match='SHA'):
        carry.memory_report(plan,capture,'wrong')
    capture.write_text(capture.read_text().replace('20000000K','120G'))
    with pytest.raises(ValueError,match='exceeds 110G'):
        carry.memory_report(plan,capture,carry.sha(capture))


def test_missing_RSS_cannot_be_claimed_as_memory_qualification(tmp_path):
    plan,capture=memory_fixture(tmp_path)
    capture.write_text(capture.read_text().replace('20000000K',''))
    with pytest.raises(ValueError,match='no measured'):
        carry.memory_report(plan,capture,carry.sha(capture))


def test_old_real_readout_is_revalidated_and_original_attempt_is_untouched(tmp_path,monkeypatch):
    old=old_package(tmp_path)
    smoke_plan=tmp_path/'old-attempt/smoke/PLAN.json'
    smoke_plan.parent.mkdir(parents=True)
    original_plan,rss=memory_fixture(tmp_path)
    smoke_plan.write_text(json.dumps(original_plan))
    full=tmp_path/'new-attempt/full/PLAN.json';full.parent.mkdir(parents=True)
    full.write_text(json.dumps(dict(smoke=False,fixture=False,runs=[{}, {}, {}],runtime=dict(sha256='runtime'))))
    capture=tmp_path/'sacct.txt';capture.write_text('captured')
    snapshot={str(f):f.read_bytes() for f in smoke_plan.parent.parent.rglob('*') if f.is_file()}
    calls=[]
    def command(cmd,**kwargs):
        calls.append(cmd)
        if 'smoke-readout' in cmd:
            dest=Path(cmd[cmd.index('--out')+1])
            dest.write_text(json.dumps(dict(status='BIT_IDENTICAL',mock=False,
                package_sha256=carry.OLD_SHA,runtime_sha256='runtime',plan=carry.spec(smoke_plan),
                isolation=dict(status='PASS'))))
        return subprocess.CompletedProcess(cmd,0)
    monkeypatch.setattr(carry.subprocess,'run',command)
    path=carry.carry(old,PKG,smoke_plan,full,capture,carry.sha(capture),rss,carry.sha(rss),tmp_path/'compat')
    result=carry.read(path)
    assert len(calls)==2 and 'smoke-readout' in calls[1]
    assert result['source_package_sha256']==carry.OLD_SHA
    assert result['package_sha256']==carry.NEW_SHA
    assert carry.read(carry.bound(result['memory_only_compatibility']['original_smoke']))['package_sha256']==carry.OLD_SHA
    assert snapshot=={str(f):f.read_bytes() for f in smoke_plan.parent.parent.rglob('*') if f.is_file()}
    with pytest.raises(ValueError,match='outside'):
        carry.carry(old,PKG,smoke_plan,full,capture,carry.sha(capture),rss,carry.sha(rss),smoke_plan.parent/'bad')


@pytest.mark.parametrize('winner', ['w1-h13','w1.5-h14','w2-h04'])
def test_eight_worsening_dev_epochs_never_stop_and_keep_all_archives(tmp_path,monkeypatch,winner):
    # Real frozen trainer/CTC/optimizer, toy stochastic model. Every dev CER is
    # worse; four-panel test results are extreme. No early exit or selection.
    from common import atomic,read
    from test_package import mock_runtime
    import stage_c
    import mock_worker
    from train import train as trainer_module  # installs frozen flat module path
    import s1_segment
    monkeypatch.setattr(s1_segment,'Segment',s1_segment.Segment)
    runtime=mock_runtime(tmp_path)
    config=stage_c.make_run(runtime,winner,fixture=True)
    config['parameters'].update(epochs=8)
    config.update(total_updates=32,target_drawn_lines=config['parameters']['epoch_rows']*8,
                  cer_steps=[8,16,24,32])
    dev_calls=[]
    original=mock_worker.mock_install
    def install(*args,**kwargs):
        trainer,rt=original(*args,**kwargs)
        def dev_eval(*values,**options):
            dev_calls.append(len(dev_calls)+1)
            return dict(cer=float(len(dev_calls)),blank_rate=0.)
        import eval_cer
        monkeypatch.setattr(eval_cer,'evaluate',dev_eval)
        return trainer,rt
    monkeypatch.setattr(mock_worker.run,'install',install)
    monkeypatch.setenv('SLURM_JOB_ID','999')
    monkeypatch.setenv('SLURM_RESTART_COUNT','0')
    for key in ('TF_C_STOP','S1_DEADLINE_EPOCH','S1_FORCE_SPLIT_STEP','S1_FORCE_SPLIT_EPOCH'):
        monkeypatch.delenv(key,raising=False)
    # Mutate only test references. Training/selection must remain the same.
    rt=read(runtime)
    for name in ('seal04_test','harvest_test'):
        rt['references'][name]={k:'Z'*100 for k in rt['references'][name]}
    atomic(runtime,rt)
    config['runtime']=carry.spec(runtime)
    output=tmp_path/'full'
    assert stage_c.execute(config,output,fixture=True)==0
    assert len(dev_calls)==8
    import torch
    state=torch.load(output/'segment.pt',map_location='cpu',weights_only=False)
    assert state['global_step']==32 and state['draw_position']==config['target_drawn_lines']
    assert state['bad_epochs']==7 and state['best']['epoch']==1
    for step in config['cer_steps']:
        assert (output/'checkpoints'/('step-%09d.pt'%step)).exists()
    assert (output/'last.pt').exists() and (output/'COMPLETE.json').exists()
