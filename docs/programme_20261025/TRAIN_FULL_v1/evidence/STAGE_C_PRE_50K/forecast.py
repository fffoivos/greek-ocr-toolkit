"""Small offline accounting forecast. All extrapolations are labelled assumptions."""
import argparse
import json
import math
from pathlib import Path
import re
import statistics
from common import atomic, read, sha, spec


def forecast(evidence, out, smoke=None):
    evidence=Path(evidence)
    capture=evidence/'STAGE_B_COLLECT_ISOLATION/SACCT_ALL_STEPS_DUPLICATES.txt'
    rows=[line.split('|') for line in capture.read_text().splitlines()]
    parents=[r for r in rows if r[0].isdigit()]
    if any(len(r)!=11 for r in rows):
        raise ValueError('accounting schema changed')
    hours=sum(int(r[6])*int(re.search(r'gres/gpu=(\d+)',r[9])[1]) for r in parents)/3600
    preempt=[r for r in parents if r[2]=='PREEMPTED']
    nodefail=[r for r in parents if r[2]=='NODE_FAIL']
    # Per-node hazard equals per-single-GPU-job hazard only as an assumption:
    # Slurm placement/preemption differs with smaller requests. Exclude deadline
    # FAILED jobs from the hazard count, but keep their charged exposure.
    exposure=sum(int(r[6]) for r in parents)/3600
    rate=(len(preempt)+len(nodefail))/exposure
    allocation_seconds=[int(r[6]) for r in preempt+nodefail]
    parent_pkg=Path(__file__).resolve().parent
    old=read(parent_pkg/'adopted/STAGE_B_SMOKE.json')
    measured=read(smoke) if smoke else None
    costs=[]
    for v in old['costs']:
        w=v['width_mult'];batch=64 if w==2 else 256
        updates=8*math.ceil(1586454/batch)
        stage_a_train=10*v['trial_training_seconds_stage_a']
        scale=71886/16787
        if measured:
            new=next(r for r in measured['costs'] if r['width_mult']==w)
            training=new['projected_train_hours']*3600
            loss=new['loss_seconds_mean']; full=new['cer_seconds_mean'];ck=new['checkpoint_seconds']
        else:
            training=stage_a_train
            loss=v['loss_eval_seconds_mean']*scale
            full=v['final_dev_cer_seconds']*scale
            ck=.15  # unmeasured assumption, replaced by CUDA smoke
        eval_s=254*loss+4*full
        checkpoint_s=math.ceil(updates/20)*ck
        base=(training+eval_s+checkpoint_s)/3600
        # Expected lost work: half checkpoint interval plus half current eval;
        # higher bound: full interval + full eval. Startup is a sensitivity
        # input until C smoke/restart receipts measure it (not claimed measured).
        update_s=training/updates
        startup_mean = new['restart_startup_seconds_mean'] if measured else 120.
        startup_high = max(new['restart_startup_seconds_max'],2*startup_mean) if measured else 600.
        losses={'low':(0.,startup_mean if measured else 30.,0.),
                'expected':(rate,startup_mean,10*update_s+.5*loss),
                'high':(2*rate,startup_high,20*update_s+loss)}
        cases={}
        for name,(hazard,startup,lost) in losses.items():
            fraction=hazard*(startup+lost)/3600
            if fraction>=1:
                raise ValueError('restart process unstable; no finite forecast')
            total=(base+startup/3600)/(1-fraction)
            cases[name]=dict(GPU_hours=total,wall_hours_excluding_queue=total,
                expected_interruptions=hazard*total,restart_seconds_assumed=startup,
                lost_seconds_per_interruption_assumed=lost,hazard_per_hour=hazard)
        costs.append(dict(width_mult=w,batch=batch,updates=updates,training_GPU_h=training/3600,
            loss_eval_seconds=loss,loss_eval_GPU_h=254*loss/3600,CER_GPU_h=4*full/3600,
            checkpoint_GPU_h=checkpoint_s/3600,eval_over_training=eval_s/training,
            eval_share_active=(eval_s/(training+eval_s)),exceeds_25_percent=eval_s/training>.25,
            scenarios=cases))
    result=dict(schema='TRAIN_FULL-stage-C-forecast-v1',status='MEASURED_SMOKE_PLUS_MODEL' if measured else 'PROVISIONAL_EXTRAPOLATION',
        evidence=dict(accounting=spec(capture),budget_capture=spec(evidence/'SACCT_D_SINCE_20261022.txt'),
            stage_b_smoke=spec(parent_pkg/'adopted/STAGE_B_SMOKE.json'),stage_c_smoke=spec(smoke) if smoke else None),
        observed=dict(parent_allocations=len(parents),requested_GPU_h_capture=hours,
            exposure_node_hours=exposure,preemptions=len(preempt),node_failures=len(nodefail),
            interruptions_per_allocated_node_hour=rate,median_interrupted_seconds=statistics.median(allocation_seconds),
            max_restart=max(int(r[8]) for r in parents),failed_parent_allocations=sum(r[2]=='FAILED' for r in parents)),
        budget=dict(owner_cap_GPU_h=350,used_GPU_h_owner_verified=437.63,already_over_cap_GPU_h=87.63),
        costs=costs,totals={k:sum(c['scenarios'][k]['GPU_hours'] for c in costs) for k in ('low','expected','high')},
        assumptions=['Stage A training rates; Stage B dev-only timings scaled by all-panel row ratio until real C smoke',
            'row-count scaling does not measure test width/length/CPU-CTC cost; refresh mandatory',
            'expected hazard=observed PREEMPTED+NODE_FAIL / parent allocation node-hours; high=2x; low=no interruption',
            'startup 30/120/600 seconds and checkpoint .15 seconds are sensitivity assumptions until C smoke',
            'same node hazard applied to non-exclusive single-GPU jobs is unqualified; queue delay excluded',
            'full 23h allocation warning yields after all work is durable; additional starts beyond time limit not budget-free'],
        options_if_over_25_percent=['keep full cadence and approve measured cost',
            'owner can authorize a coarser loss cadence in a new bound plan',
            'optimize identical full-coverage evaluator then repeat qualification; no silent subsampling'])
    atomic(out,result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence',required=True);p.add_argument('--out',required=True);p.add_argument('--smoke')
    a=p.parse_args();forecast(a.evidence,a.out,a.smoke)
