"""Small offline tests; no CUDA/data copies or scheduler invocation."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import reconcile as r

b = r.load_package(ROOT / 'package')


def record(job='123', start=100, end=200, host='nid001', restart='0', state='COMPLETED', tres='cpu=24,gres/gpu=1'):
    return dict(JobIDRaw=job, JobID=job, State=state, ExitCode='0:0', Start=start,
                End=end, ElapsedRaw=end-start, NodeList=host, Restarts=restart,
                ReqTRES='', AllocTRES=tres)


def write_accounting(path, records):
    path.write_text(''.join('|'.join(str(x[k]) for k in r.SACCT_FIELDS)+'\n' for x in records))
    return path


def setup(tmp_path, *, recovered=True, second_start=210., second_end=250.,
          second_host='nid001', second_gpu='GPU-1', second_cpu=0):
    runtime, stage_a = tmp_path/'runtime.json', tmp_path/'STAGE_A.json'
    b.atomic(runtime, {}); b.atomic(stage_a, {})
    groups = []
    for i in range(2):
        out = tmp_path/('run%d' % i)
        trial = b.make_trial(runtime, 1., b.points()[i])
        config = tmp_path/('trial%d.json' % i)
        b.atomic(config, trial)
        groups.append([dict(output=str(out), config=b.spec(config))])
        a = dict(trial=b.spec(config), fixture=False, physical_host='nid001' if i==0 else second_host,
                 gpu_uuid='GPU-1' if i==0 else second_gpu, job_id='123' if i==0 else '456',
                 restart_count=0, cuda_visible_devices='0', started_unix=101. if i==0 else second_start,
                 cpu_affinity=list(range(0 if i==0 else second_cpu, 24 if i==0 else second_cpu+24)))
        if i or not recovered:
            a['ended_unix'] = second_end if i else 200.
        ap = out/'ALLOCATION_1.json'
        b.atomic(ap, a)
        if not i and recovered:
            b.atomic(out/'RECOVERED_ALLOCATION_1.json', dict(prior=b.spec(ap),
                prior_physical_host='nid001', next_physical_host='nid002',
                next_job_id='789', next_restart_count=0, ended_upper_bound_unix=300.))
        b.atomic(out/'FAILURE_1.json', dict(error='synthetic final infeasibility'))
    plan = dict(fixture=False, smoke=False, groups=groups, payload_sha256=r.PAYLOAD_SHA,
                runtime=b.spec(runtime), stage_a=b.spec(stage_a),
                points=b.spec(b.ROOT/'study/lr_trials.jsonl'), space=b.spec(b.ROOT/'study/lr_space.json'))
    path = tmp_path/'PLAN.json'
    b.atomic(path, plan)
    sacct = write_accounting(tmp_path/'sacct.txt', [record(), record(job='123.0', restart='')])
    return path, plan, sacct


def audit(path, plan, sacct):
    return r.reconcile(b, plan, path, sacct, r.sha(sacct))


def test_real_copied_evidence_26_matches_18_overlaps_resolved():
    evidence = ROOT/'evidence/STAGE_B_COLLECT_ISOLATION'
    path = ROOT/'search_study1/PLAN.json'
    p = r.authenticate(b, path, r.STUDY_SHA, evidence)
    result = r.reconcile(b, p, path, evidence/'SACCT_ALL_STEPS_DUPLICATES.txt',
                         '8ae7b9c82a00f0b510ab881c75317e5be85f4423fd5a8567723da639fcfa56a2', evidence=evidence)
    assert result['status']=='PASS' and result['allocations']==151
    assert result['recovered_allocations']==26
    assert result['before']==dict(pairs=18, gpu=18, same_host_cpu=18)
    assert result['after']==dict(pairs=0, gpu=0, same_host_cpu=0)
    assert result['sealed_checker']['allocations']==151
    assert all(m['effective_end_unix']==m['step']['End'] for m in result['matches'])


def test_production_collect_and_internal_seeds_use_original_validation(tmp_path):
    path, p, sacct = setup(tmp_path)
    originals = {f:f.read_bytes() for f in tmp_path.glob('run*/*.json')}
    original_checker = b.isolation
    with pytest.raises(ValueError, match='overlapping GPU'):
        original_checker(p)
    report = tmp_path/'RECONCILIATION.json'
    with r.collection_adapter(b, {str(path):p}, r.sha(sacct), sacct, report):
        result = b.collect(path)  # real checked_plan + collect; no fixture=True
        assert all(t['status']=='failed' and t['val_error'] is None for t in result[1.])
        assert b.read(tmp_path/'ISOLATION.json')['reconciliation']==b.spec(report)
        # seeds() calls the same production collector internally. These are
        # intentionally infeasible trial fixtures, so selection must refuse.
        with pytest.raises(ValueError, match='no feasible trial'):
            b.seeds(path, tmp_path/'b2')
    assert b.isolation is original_checker
    assert all(f.read_bytes()==value for f,value in originals.items())


def test_seeds_success_reuses_sealed_selection_with_reconciled_isolation(tmp_path):
    path,p,sacct=setup(tmp_path)
    for width in (1.5,2.):
        config=tmp_path/('trial-w%g.json'%width)
        trial=b.make_trial(tmp_path/'runtime.json',width,b.points()[0])
        b.atomic(config,trial)
        out=tmp_path/('run-w%g'%width)
        p['groups'].append([dict(output=str(out),config=b.spec(config))])
        b.atomic(out/'ALLOCATION_1.json',dict(trial=b.spec(config),fixture=False,
            physical_host='nid%g'%width,gpu_uuid='GPU-%g'%width,job_id='789',restart_count=0,
            cuda_visible_devices='0',started_unix=150.,ended_unix=250.,cpu_affinity=list(range(24))))
    for group in p['groups']:
        t=group[0];out=Path(t['output']);trial=b.read(b.bound(t['config']))
        # Synthetic already-complete artifacts exercise the original collector's
        # byte/score validation, not training or a claimed real CUDA result.
        checkpoint=out/'segment.pt';checkpoint.write_bytes(b'synthetic-checkpoint')
        journal=out/'loss_eval.jsonl';journal.write_text('')
        final=out/'final.json'
        panels={name:dict(score=dict(cer=dict(nfd_atom=dict(edits=10,reference_units=100))))
                for name in ('seal04_dev','harvest_dev')}
        b.atomic(final,dict(instruments=panels))
        b.atomic(out/'COMPLETE.json',dict(binding=dict(trial=trial),test_instruments_opened=0,
            checkpoint=b.spec(checkpoint),loss_journal=b.spec(journal),loss_evaluations=[],
            evaluations=[b.spec(final)],pooled_dev=dict(edits=20,reference_units=200,rate=.1,
                mode='nfd_atom',pooling='sum edits / sum reference units across both dev panels')))
        (out/'train_log.csv').write_text('train_loss\n1.0\n')
    b.atomic(path,p)
    r.authenticate(b,path,r.sha(path))
    with r.collection_adapter(b,{str(path):p},r.sha(sacct),sacct,tmp_path/'REPORT.json'):
        result=b.seeds(path,tmp_path/'b2')
    assert result['parent_study']==b.spec(path)
    assert [len(g) for g in result['groups']]==[4,4,1]
    assert {(b.read(b.bound(t['config']))['parameters']['width_mult'],
             b.read(b.bound(t['config']))['parameters']['seed'])
            for g in result['groups'] for t in g}==set(r.itertools.product((1.,1.5,2.),(0,1,2)))


@pytest.mark.parametrize('field,value', [('Restarts','1'),('NodeList','nid-wrong'),('JobIDRaw','456')])
def test_parent_job_restart_host_required(tmp_path, field, value):
    path, p, sacct = setup(tmp_path)
    parent=record();parent[field]=value
    write_accounting(sacct, [parent, record(job='123.0', restart='')])
    with pytest.raises(ValueError, match='parent job/restart/host match is not unique'):
        audit(path,p,sacct)


@pytest.mark.parametrize('extra', [record(), record(job='123.1', restart='')])
def test_ambiguous_parent_or_step_refused(tmp_path, extra):
    path,p,sacct=setup(tmp_path)
    write_accounting(sacct,[record(),record(job='123.0', restart=''),extra])
    with pytest.raises(ValueError,match='not unique'):
        audit(path,p,sacct)


@pytest.mark.parametrize('step', [record(job='123.batch'), record(job='123.0', start=102),
                                 record(job='123.0',host='nid002'),record(job='123.0',end=100),
                                 record(job='123.0',tres='cpu=96,gres/gpu=4')])
def test_no_nearest_start_batch_or_wrong_lane_fallback(tmp_path,step):
    path,p,sacct=setup(tmp_path)
    write_accounting(sacct,[record(),step])
    with pytest.raises(ValueError,match='not unique|24-CPU/single-GPU'):
        audit(path,p,sacct)


def test_sacct_sha_and_recovery_sha_tampering_refused(tmp_path):
    path,p,sacct=setup(tmp_path)
    with pytest.raises(ValueError,match='sacct capture SHA'):
        r.reconcile(b,p,path,sacct,'0'*64)
    a=tmp_path/'run0/ALLOCATION_1.json'
    a.write_text(a.read_text()+'\n')
    with pytest.raises(ValueError,match='recovery binding/host'):
        audit(path,p,sacct)


def test_min_retains_tighter_original_upper_bound(tmp_path):
    path,p,sacct=setup(tmp_path)
    w=tmp_path/'run0/RECOVERED_ALLOCATION_1.json'
    b.atomic(w,dict(b.read(w),ended_upper_bound_unix=180.))
    result=audit(path,p,sacct)
    assert result['matches'][0]['effective_end_unix']==180.
    assert result['matches'][0]['measured_step_end_unix']==200


@pytest.mark.parametrize('host,gpu,cpu,kind', [('nid002','GPU-1',0,'GPU_GLOBAL'),
    ('nid001','GPU-2',0,'CPU_SAME_HOST')])
def test_real_overlaps_fail_with_both_pairs_and_no_collector_outputs(tmp_path,host,gpu,cpu,kind):
    path,p,sacct=setup(tmp_path,second_start=150.,second_host=host,second_gpu=gpu,second_cpu=cpu)
    result=audit(path,p,sacct)
    assert result['status']=='FAIL' and kind in result['remaining_conflicts'][0]['kinds']
    assert result['remaining_conflicts'][0]['left']['path'].endswith('run0/ALLOCATION_1.json')
    report=tmp_path/'REPORT.json'
    with r.collection_adapter(b,{str(path):p},r.sha(sacct),sacct,report):
        with pytest.raises(ValueError,match='remaining allocation overlap'):
            b.collect(path)
    assert b.read(report)['status']=='FAIL'
    assert not (tmp_path/'w1/results.jsonl').exists()


def test_distinct_hosts_cpu_reuse_and_exact_endpoint_pass(tmp_path):
    path,p,sacct=setup(tmp_path,second_start=150.,second_host='nid002',second_gpu='GPU-2')
    assert audit(path,p,sacct)['status']=='PASS'
    second=tmp_path/'run1/ALLOCATION_1.json'
    b.atomic(second,dict(b.read(second),physical_host='nid001',gpu_uuid='GPU-1',started_unix=200.))
    assert audit(path,p,sacct)['status']=='PASS'


def test_missing_recovery_and_nonfinite_end_refused(tmp_path):
    path,p,sacct=setup(tmp_path)
    a=tmp_path/'run1/ALLOCATION_1.json'
    # JSON parsers can encounter NaN despite the producer refusing it.
    a.write_text(json.dumps(dict(b.read(a),ended_unix=float('nan'))))
    with pytest.raises(ValueError,match='effective allocation interval'):
        audit(path,p,sacct)


def b2_setup(tmp_path):
    runtime,stage_a=tmp_path/'runtime.json',tmp_path/'STAGE_A.json'
    b.atomic(runtime,{});b.atomic(stage_a,{})
    trials=[]
    for width in b.ADOPTED:
        for seed in (0,1,2):
            path=tmp_path/('w%g-s%d.json'%(width,seed))
            b.atomic(path,b.make_trial(runtime,width,b.points()[0],seed=seed))
            trials.append(dict(config=b.spec(path),output=str(tmp_path/('runs-'+path.stem))))
    p=dict(fixture=False,smoke=False,b2=True,payload_sha256=r.PAYLOAD_SHA,
           runtime=b.spec(runtime),stage_a=b.spec(stage_a),points=b.spec(b.ROOT/'study/lr_trials.jsonl'),
           space=b.spec(b.ROOT/'study/lr_space.json'),groups=[trials[i:i+4] for i in range(0,9,4)])
    path=tmp_path/'PLAN.json';b.atomic(path,p)
    smoke=tmp_path/'SMOKE.json';b.atomic(smoke,dict(status='BIT_IDENTICAL',mock=False,
                package_sha256=r.PAYLOAD_SHA,runtime_sha256=b.sha(runtime)))
    review=tmp_path/'REVIEW.json';b.atomic(review,dict(status='PASS',plan_sha256=b.sha(path),
                package_sha256=r.PAYLOAD_SHA,smoke_sha256=b.sha(smoke)))
    return path,review,smoke


def test_submit8h_real_gates_drychecks_exact_commands_and_repeat_no_double_submit(tmp_path):
    path,review,smoke=b2_setup(tmp_path)
    calls=[]
    def command(cmd,**kwargs):
        calls.append(cmd)
        assert cmd[1]=='--time=08:00:00'
        return subprocess.CompletedProcess(cmd,0,stdout=str(9000+int(cmd[-1]))+'\n')
    r.submit_b2(b,path,review,smoke,command=command)
    assert len(calls)==6 and all('--test-only' in c for c in calls[:3])
    for i in range(3):
        receipt=b.read(tmp_path/'submit-controls/time-override'/('group-%03d.json'%i))
        assert receipt['effective_command']==calls[3+i]
        assert '--time=08:00:00' not in receipt['sealed_command']
    r.submit_b2(b,path,review,smoke,command=command)
    assert len(calls)==6


def test_submit8h_never_bypasses_review_or_changes_claims(tmp_path):
    path,review,smoke=b2_setup(tmp_path)
    b.atomic(review,dict(b.read(review),status='HOLD'))
    def command(*args,**kwargs):
        pytest.fail('scheduler must not be called')
    with pytest.raises(ValueError,match='focused Astra PASS'):
        r.submit_b2(b,path,review,smoke,command=command)


def test_authentication_and_offline_mode_do_not_admit_foreign_plan(tmp_path):
    path,p,sacct=setup(tmp_path)
    with pytest.raises(ValueError,match='plan SHA mismatch'):
        r.authenticate(b,path,r.STUDY_SHA)
    with pytest.raises(ValueError,match='restricted to the copied'):
        r.authenticate(b,path,r.sha(path),tmp_path)
