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
        scale=71887/16787
        if measured:
            new=next(r for r in measured['costs'] if r['width_mult']==w)
            training=new['projected_train_hours']*3600
            loss=new['loss_seconds_mean']; full=new['cer_seconds_mean'];ck=new['checkpoint_seconds']
            archive_seconds=new['loss_checkpoint_seconds_mean']
            archive_bytes=new['loss_checkpoint_bytes_max']
            selection=new['selection_seconds_mean']
            full_bytes=new['full_state_bytes']
        else:
            training=stage_a_train
            loss=v['loss_eval_seconds_mean']*scale
            full=v['final_dev_cer_seconds']*scale
            ck=.15  # unmeasured assumption, replaced by CUDA smoke
            archive_seconds=1.  # scratch serialize+fsync+SHA+reload; unmeasured sensitivity
            # FP32 state tensor payload rounded up + codec/config/ZIP allowance.
            archive_bytes={1.:20_000_000,1.5:41_000_000,2.:70_000_000}[w]
            selection=full*437/71887  # provisional; fresh C smoke must time actual epoch loader
            full_bytes={1.:60_000_000,1.5:115_000_000,2.:195_000_000}[w]
        eval_s=254*loss+4*full+8*selection
        durable_saves_upper=math.ceil(updates/20)+254+4+8
        checkpoint_s=durable_saves_upper*ck+254*archive_seconds
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
            # Count 23h segment renewals explicitly. Preemptions reset the
            # warning timer; counting against aggregate run time is conservative.
            usable_hours=23-600/3600
            renewals=0
            for _ in range(100):
                count=max(0,math.ceil(total/usable_hours)-1)
                if count==renewals:
                    break
                renewals=count
                total=(base+(1+renewals)*startup/3600+renewals*ck/3600)/(1-fraction)
            else:
                raise ValueError('segment renewal forecast did not converge')
            yields=math.ceil(hazard*total)+renewals
            cases[name]=dict(segment_renewals=renewals,segment_usable_hours=usable_hours,
                renewal_startup_GPU_h=renewals*startup/3600,
                retained_yield_inodes_assumed=yields,
                retained_yield_bytes_estimate=yields*full_bytes,
                storage_bytes_estimate=254*archive_bytes+(7+yields)*full_bytes+1_000_000_000,
                GPU_hours=total,wall_hours_excluding_queue=total,
                expected_interruptions=hazard*total,restart_seconds_assumed=startup,
                lost_seconds_per_interruption_assumed=lost,hazard_per_hour=hazard)
        costs.append(dict(width_mult=w,batch=batch,updates=updates,training_GPU_h=training/3600,
            selection_rows=437,selection_epoch_evaluations=8,selection_seconds=selection,
            selection_GPU_h=8*selection/3600,full_state_bytes_estimate=full_bytes,
            loss_eval_seconds=loss,loss_eval_GPU_h=254*loss/3600,CER_GPU_h=4*full/3600,
            checkpoint_GPU_h=checkpoint_s/3600,eval_over_training=eval_s/training,
            retained_loss_checkpoints=254,loss_checkpoint_bytes_estimate=archive_bytes,
            loss_checkpoint_total_bytes_estimate=254*archive_bytes,
            loss_checkpoint_seconds=archive_seconds,loss_checkpoint_GPU_h=254*archive_seconds/3600,
            durable_saves_upper_bound=durable_saves_upper,
            eval_share_active=(eval_s/(training+eval_s)),exceeds_25_percent=eval_s/training>.25,
            scenarios=cases))
    result=dict(schema='TRAIN_FULL-stage-C-forecast-v1',status='MEASURED_SMOKE_PLUS_MODEL' if measured else 'PROVISIONAL_EXTRAPOLATION',
        evidence=dict(accounting=spec(capture),budget_capture=spec(evidence/'SACCT_D_SINCE_20261022.txt'),
            stage_b_smoke=spec(parent_pkg/'adopted/STAGE_B_SMOKE.json'),stage_c_smoke=spec(smoke) if smoke else None),
        observed=dict(parent_allocations=len(parents),requested_GPU_h_capture=hours,
            exposure_node_hours=exposure,preemptions=len(preempt),node_failures=len(nodefail),
            interruptions_per_allocated_node_hour=rate,median_interrupted_seconds=statistics.median(allocation_seconds),
            max_restart=max(int(r[8]) for r in parents),failed_parent_allocations=sum(r[2]=='FAILED' for r in parents)),
        budget=dict(historical_cap_GPU_h=350,used_GPU_h_owner_verified_before_C=437.63,already_over_historical_cap_GPU_h=87.63,
            owner_stage_C_authority_GPU_h=82,authority='owner 2026-10-27: 82 GPU-h all three; smoke/accounting tracked separately'),
        costs=costs,totals={k:sum(c['scenarios'][k]['GPU_hours'] for c in costs) for k in ('low','expected','high')},
        assumptions=['Stage A training rates; Stage B dev-only timings scaled by all-panel row ratio until real C smoke',
            'row-count scaling does not measure test width/length/CPU-CTC cost; refresh mandatory',
            'expected hazard=observed PREEMPTED+NODE_FAIL / parent allocation node-hours; high=2x; low=no interruption',
            'startup 30/120/600 seconds and checkpoint .15 seconds are sensitivity assumptions until C smoke',
            '254 retained model archives: provisional 1 second each; bytes rounded estimates; refresh from new-seal smoke',
            'same node hazard applied to non-exclusive single-GPU jobs is unqualified; queue delay excluded',
            'eight seal04-dev437 epoch selection CER passes explicitly included; fresh smoke measures the actual loader',
            '23h minus 600s usable segments; ceil(total/usable)-1 conservative renewals include startup+yield save; preemptions reset actual timer',
            'yield hardlinks retain old full-state inodes after rolling replacement; assume every forecast interruption yields (conservative)',
            'storage estimate includes 254 models + four CER full states + best/last/rolling + all forecast yields + 1GB logs margin; no bound on arbitrary requeues',
            'late-run archive verification and full-size sampler startup remain unmeasured; high is not a bound'],
        options_if_over_25_percent=['keep full cadence and approve measured cost',
            'owner can authorize a coarser loss cadence in a new bound plan',
            'optimize identical full-coverage evaluator then repeat qualification; no silent subsampling'])
    atomic(out,result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence',required=True);p.add_argument('--out',required=True);p.add_argument('--smoke')
    a=p.parse_args();forecast(a.evidence,a.out,a.smoke)
