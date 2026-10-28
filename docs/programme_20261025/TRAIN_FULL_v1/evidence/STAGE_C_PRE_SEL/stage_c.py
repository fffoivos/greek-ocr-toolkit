"""Stage C: three fresh independent full runs; owner invokes remote commands.

No B2, test-based selection, remote operations or scheduler submission at import.
"""
import argparse
import copy
import fcntl
import math
import os
from pathlib import Path
import signal
import statistics
import subprocess
import sys
import time
from common import atomic, bound, read, sha, spec
from stage_b import immutable

ROOT = Path(__file__).resolve().parent
PANELS = ('seal04_dev', 'seal04_test', 'harvest_dev', 'harvest_test')
WINNERS = ('w1-h13', 'w1.5-h14', 'w2-h04')
PARENT = '3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8'


def make_run(runtime, winner, *, smoke=False, fixture=False):
    if winner not in WINNERS:
        raise ValueError('unknown owner-adopted winner')
    source = read(ROOT / 'adopted' / (winner + '.json'))
    rt = read(runtime)
    par = dict(source['parameters'])
    real = rt.get('train_rows', 8)
    par.update(epochs=8, epoch_rows=2*real, seed=0)
    if smoke:
        par.update(epochs=2, epoch_rows=par['bs']*24)
    if fixture:
        par.update(epochs=2, epoch_rows=par['bs']*4)
    per_epoch = math.ceil(par['epoch_rows']/par['bs'])
    total = per_epoch*par['epochs']
    # Four points, at actual epoch boundaries: 2,4,6,8 (25/50/75/100%).
    cer = [per_epoch*e for e in range(2, par['epochs']+1, 2)]
    return dict(schema='TRAIN_FULL-stage-C-run-v1', payload_sha256=sha(ROOT/'PAYLOAD.json'),
        runtime=spec(runtime), adopted=spec(ROOT/'adopted'/(winner+'.json')),
        parameters=par, total_updates=total, target_drawn_lines=par['epoch_rows']*par['epochs'],
        cer_steps=cer, loss_every_drawn_lines=par['bs']*2 if (smoke or fixture) else 50000,
        loss_checkpoint_policy='every loss point including final; immutable model+codec+config; SHA in loss record',
        durable_every=2 if (smoke or fixture) else 20, smoke=smoke, fixture=fixture,
        instruments=list(PANELS), seed_reruns='SKIPPED by owner 2026-10-26; variance unmeasured',
        test_policy='report-only; no selection, stopping or parameter changes')


def build(runtime, out, *, smoke=False, fixture=False):
    from verify import verify, data_package_matches
    if not fixture:
        verify()
        if not data_package_matches(read(runtime).get('package_sha256'), runtime):
            raise ValueError('foreign prepared data')
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    entries = []
    for winner in WINNERS:
        config = make_run(runtime, winner, smoke=smoke, fixture=fixture)
        name = 'w%g' % config['parameters']['width_mult']
        roles = ('control', 'requeue') if smoke else ('full',)
        for role in roles:
            path = out/'configs'/(name+'-'+role+'.json')
            immutable(path, config)
            entries.append(dict(name=name+'-'+role, config=spec(path), output=str(out/'runs'/(name+'-'+role)),
                                signal_smoke=role=='requeue'))
    p = dict(schema='TRAIN_FULL-stage-C-plan-v1', payload_sha256=sha(ROOT/'PAYLOAD.json'),
        runtime=spec(runtime), smoke=smoke, fixture=fixture, runs=entries,
        resources='one non-exclusive 1-GPU job/run; 24 CPUs; 6 workers; no DDP',
        time_limit='23:00:00', warning_seconds=600)
    immutable(out/'PLAN.json', p)
    return p


def checked(path):
    from verify import verify, data_package_matches
    verify()
    if sha(ROOT/'stage_b_parent_payload.json') != PARENT:
        raise ValueError('Stage B parent identity changed')
    p = read(path)
    if p['fixture'] or p['payload_sha256'] != sha(ROOT/'PAYLOAD.json'):
        raise ValueError('foreign/fixture Stage C plan')
    runtime = bound(p['runtime'])
    if not data_package_matches(read(runtime).get('package_sha256'), runtime):
        raise ValueError('foreign prepared data')
    for e in p['runs']:
        c = read(bound(e['config']))
        if c['payload_sha256'] != p['payload_sha256'] or c['runtime'] != p['runtime']:
            raise ValueError('run/plan binding changed')
        source = read(bound(c['adopted']))
        if source['payload_sha256'] != PARENT:
            raise ValueError('foreign adopted trial')
        if c != make_run(runtime, Path(c['adopted']['path']).stem, smoke=p['smoke']):
            raise ValueError('Stage C recipe changed')
    return p


def execute(config, output, *, fixture=False):
    import run
    from horizon import verify_full_pass
    from loss_cadence import plan
    runtime_path = bound(config['runtime'])
    if not fixture:
        from verify import verify, data_package_matches
        verify()
        if (config['payload_sha256'] != sha(ROOT/'PAYLOAD.json')
                or not data_package_matches(read(runtime_path).get('package_sha256'), runtime_path)
                or config != make_run(runtime_path, Path(bound(config['adopted'])).stem, smoke=config['smoke'])):
            raise ValueError('foreign/changed Stage C run')
    trainer, rt = run.install(runtime_path)
    trainer._runtime()
    torch = trainer.torch
    if bool(rt.get('mock')) != fixture or config['fixture'] != fixture:
        raise ValueError('fixture/production mismatch')
    if not fixture:
        from stage_a_probe import THREAD_KEYS
        if (str(torch.__version__) != '2.11.0+cu128' or torch.version.cuda != '12.8'
                or torch.backends.cudnn.version() != 91900
                or torch.cuda.get_device_name(0) != 'NVIDIA GH200 120GB'
                or torch.cuda.device_count() != 1 or not os.environ.get('CUDA_VISIBLE_DEVICES')
                or len(os.sched_getaffinity(0)) < 24
                or any(os.environ.get(k) != '1' for k in THREAD_KEYS)):
            raise ValueError('S1 CUDA/thread/isolation profile changed')
        if not config['smoke']:
            verify_full_pass(rt['components'], {k:v['rows'] for k,v in rt['pools'].items()}, rt['train_rows'])
    opts = copy.deepcopy(read(ROOT/'recipe.json')['parameters'])
    opts.update(config['parameters'])
    opts.update(mix=str(runtime_path), val_mix=str(runtime_path), codec=str(ROOT/'vendor/codec/v2.1.json'),
                out_dir=str(Path(output).resolve()))
    if fixture:
        opts.update(device='cpu', workers=0, pin_memory=False)
    argv = []
    for k,v in opts.items():
        if v is True:
            argv.append('--'+k.replace('_','-'))
        elif v is not False and v is not None:
            argv.extend(['--'+k.replace('_','-'),str(v)])
    args = trainer.parse_args(argv)
    args.stage_c, args.full_smoke = True, config['smoke']
    args.full_every = config['total_updates']  # legacy fallback unused for C
    args.cer_steps, args.durable_every = config['cer_steps'], config['durable_every']
    args.loss_plan = plan(trainer,rt,trainer.full_pools,args.epochs,args.epoch_rows,args.bs,
                          config['loss_every_drawn_lines'])
    if (args.loss_plan['total_updates'] != config['total_updates']
            or args.loss_plan['total_drawn_lines'] != config['target_drawn_lines']):
        raise ValueError('actual sampler horizon changed')
    if not fixture and not config['smoke'] and args.loss_plan['count'] != 254:
        raise ValueError('full run must have exactly 254 loss points')
    trainer.PATIENCE = args.epochs+1
    output = Path(output)
    binding = dict(config=config, loss_plan=args.loss_plan, evaluation_steps=args.cer_steps)
    immutable(output/'RUN_BINDING.json',binding)
    atomic(output/'LOSS_CADENCE.json',args.loss_plan)
    # These rows and the epoch diagnostic are the inherited seal04 dev only;
    # neither held-out test panel participates in best/patience.
    status = trainer.train(args)
    if status:
        return status
    ck = torch.load(output/'segment.pt',map_location='cpu',weights_only=False)
    if ck['global_step'] != config['total_updates'] or ck['draw_position'] != config['target_drawn_lines']:
        raise ValueError('incomplete full horizon')
    from loss_journal import records
    events,torn = records(output/'loss_eval.jsonl')
    if torn is not None or [e['step'] for e in events] != args.loss_plan['steps']:
        raise ValueError('missing/duplicate loss points')
    for event,point in zip(events,args.loss_plan['points']):
        r = read(bound(event['record']))
        if (r['drawn_lines'] != point['drawn_lines'] or set(r['instruments']) != set(PANELS)
                or any(r['instruments'][n]['rows'] != rt['pools'][n]['rows'] for n in PANELS)):
            raise ValueError('loss coverage/draw mismatch')
        from loss_checkpoint import validate
        validate(r['checkpoint'],trainer,step=point['step'],drawn_lines=point['drawn_lines'],
            runtime_sha=rt['_sha256'],model_sha=r['model_sha256'])
        if event.get('checkpoint') != r['checkpoint']:
            raise ValueError('loss journal checkpoint binding changed')
    retained = [read(bound(e['record']))['checkpoint'] for e in events]
    if {Path(s['path']).name for s in retained} != {f.name for f in (output/'loss_checkpoints').glob('*.pt')}:
        raise ValueError('missing/extra retained loss checkpoints')
    evaluations = [spec(output/'eval'/('step-%09d.json'%s)) for s in args.cer_steps]
    for item in evaluations:
        r = read(bound(item))
        if set(r['instruments']) != set(PANELS):
            raise ValueError('CER panel coverage changed')
    atomic(output/'COMPLETE.json',dict(binding=binding,checkpoint=spec(output/'segment.pt'),
        evaluations=evaluations,loss_evaluations=[e['record'] for e in events],
        loss_checkpoints=retained,
        loss_journal=spec(output/'loss_eval.jsonl'),state_sha256=ck['state_sha256'],mock=fixture))
    return 0


def complete(output, config):
    c = read(Path(output)/'COMPLETE.json')
    if c['binding']['config'] != config:
        raise ValueError('completed binding changed')
    for s in [c['checkpoint'],c['loss_journal'],*c['evaluations'],*c['loss_evaluations'],*c['loss_checkpoints']]:
        bound(s)
    from loss_journal import records
    events,torn = records(bound(c['loss_journal']))
    if torn is not None or [e['record'] for e in events] != c['loss_evaluations']:
        raise ValueError('completed loss journal changed')
    if [e.get('checkpoint') for e in events] != c['loss_checkpoints']:
        raise ValueError('completed checkpoint list changed')
    for event in events:
        r=read(bound(event['record']))
        if r['checkpoint'] != event['checkpoint']:
            raise ValueError('completed loss checkpoint binding changed')
    return c


def lane(path, output, *, fixture=False):
    from stage_b_trial import physical_host
    config = read(path)
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    with (output/'RUN.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        immutable(output/'CLAIM.json',config)
        if (output/'COMPLETE.json').exists():
            complete(output,config)
            return 0
        job, restart = os.environ['SLURM_JOB_ID'],int(os.environ.get('SLURM_RESTART_COUNT','0'))
        info = dict(job_id=job,restart_count=restart,step_id=os.environ.get('SLURM_STEP_ID'),
            physical_host=physical_host(),started_unix=time.time(),trial=spec(path),fixture=fixture,
            cpu_affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else [],
            cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'))
        os.environ['TF_C_STARTED_UNIX'] = str(info['started_unix'])
        if not fixture:
            import torch
            from stage_a_probe import gpu_uuid
            if not info['step_id'] or torch.cuda.device_count()!=1:
                raise ValueError('attested single-GPU srun step required')
            torch.empty(1,device='cuda')
            info['gpu_uuid']=gpu_uuid()
        allocation=output/('ALLOCATION_%s_%s_%d.json'%(job,restart,time.time_ns()))
        atomic(allocation,info)
        # Never forward signals to srun. The batch-owned request persists during
        # Python/torch/data startup and is polled by the Segment boundary hook.
        os.environ['S1_TRACE']='1' if config['smoke'] else '0'
        os.environ.pop('S1_FORCE_SPLIT_STEP',None)
        try:
            stop=os.environ.get('TF_C_STOP')
            if stop and Path(stop).exists() and not (output/'segment.pt').exists():
                status=75
                atomic(output/('NOT_STARTED_%d.json'%time.time_ns()),dict(allocation=spec(allocation),reason='warning before training'))
            else:
                status=execute(config,output,fixture=fixture)
            if status==75:
                checkpoint=None
                if (output/'segment.pt').exists():
                    archive=output/'yields'/('%s-%s-%d.pt'%(job,restart,time.time_ns()))
                    archive.parent.mkdir(exist_ok=True)
                    # Atomic rolling saves always replace the inode. A hardlink
                    # retains the exact yield without copying a model file.
                    os.link(output/'segment.pt',archive)
                    checkpoint=spec(archive)
                atomic(output/('YIELD_%d.json'%time.time_ns()),dict(job_id=job,restart_count=restart,
                    checkpoint=checkpoint,stop_request=spec(stop) if stop and Path(stop).exists() else None))
            info['exit_code']=status
            return status
        except Exception as e:
            info['exit_code']=1
            atomic(output/('FAILURE_%d.json'%time.time_ns()),dict(error=repr(e),config=config))
            raise
        finally:
            info['ended_unix']=time.time()  # measured worker end, never controller upper bound
            atomic(allocation,info)


def node(plan_path,index,*,popen=subprocess.Popen,command=subprocess.run):
    p=checked(plan_path)
    e=p['runs'][index]
    output=Path(e['output'])
    output.mkdir(parents=True,exist_ok=True)
    stop=Path(os.environ['TF_C_STOP'])
    # A signal before controller startup is already present; no new step starts.
    if stop.exists():
        atomic(output/('CONTROLLER_NOT_STARTED_%d.json'%time.time_ns()),dict(stop_request=spec(stop)))
        return 75
    with (output/'CONTROLLER.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        requested=[False]
        def warning(*_):
            requested[0]=True
            atomic(stop,dict(job_id=os.environ['SLURM_JOB_ID'],
                restart_count=int(os.environ.get('SLURM_RESTART_COUNT','0')),requested_unix=time.time()))
        old=signal.signal(signal.SIGTERM,warning)
        try:
            if stop.exists() or requested[0]:
                return 75
            cmd=['srun','--exact','--nodes=1','--ntasks=1','--gpus-per-node=1',
                '--gpus-per-task=1','--cpus-per-task=24','--cpu-bind=cores','--gpu-bind=single:1',
                '--open-mode=append','--output='+str(output/'srun-%j.log'),
                sys.executable,'-B',str(ROOT/'stage_c.py'),'lane','--config',str(bound(e['config'])),
                '--out',str(output)]
            proc=popen(cmd)
            sent=False
            restart=int(os.environ.get('SLURM_RESTART_COUNT','0'))
            while proc.poll() is None:
                live=output/'LIVE.json'
                if p['smoke'] and e['signal_smoke'] and restart==0 and not sent and live.exists():
                    r=read(live)
                    if r['job_id']==os.environ['SLURM_JOB_ID'] and r['step']>=3:
                        sc=['scancel','--batch','--signal=TERM',os.environ['SLURM_JOB_ID']]
                        command(sc,check=True)
                        atomic(output/'REAL_SIGNAL_SENT.json',dict(command=sc,live=r,
                            observed_step=r['step'],sent_unix=time.time(),job_id=r['job_id']))
                        sent=True
                time.sleep(.05)
            code=proc.wait()
            if code not in (0,75):
                raise RuntimeError('unexpected lane exit; preserved logs: '+str(code))
            if code==0:
                complete(output,read(bound(e['config'])))
            elif not list(output.glob('YIELD_*.json')):
                raise ValueError('lane yielded without durable receipt')
            return code
        finally:
            signal.signal(signal.SIGTERM,old)


def submit(plan_path,review=None,smoke_report=None,*,command=subprocess.run):
    p=checked(plan_path)
    if not p['smoke']:
        r,s=read(review),read(smoke_report)
        if (r.get('status')!='PASS' or r.get('plan_sha256')!=sha(plan_path)
                or r.get('package_sha256')!=p['payload_sha256'] or r.get('smoke_sha256')!=sha(smoke_report)
                or s.get('status')!='BIT_IDENTICAL' or s.get('mock') is not False
                or s.get('package_sha256')!=p['payload_sha256'] or s.get('runtime_sha256')!=p['runtime']['sha256']):
            raise ValueError('focused Astra PASS binding this PLAN + real signal CUDA smoke required')
        if r.get('budget_extension_owner_go') is not True:
            raise ValueError('owner go covering exceeded 350 GPU-h cap required')
    controls=Path(plan_path).parent/'submit-controls'
    controls.mkdir(exist_ok=True)
    with (controls/'SUBMIT.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        commands=[]
        for i,e in enumerate(p['runs']):
            cmd=['sbatch','--parsable','--export=ALL','--time='+('01:20:00' if p['smoke'] else p['time_limit']),
                '--output='+str(controls/(e['name']+'-%j.log')),str(ROOT/'stage_c.sbatch'),str(Path(plan_path).resolve()),str(i)]
            commands.append(cmd)
            if not (controls/(e['name']+'.json')).exists():
                command([cmd[0],'--test-only',*cmd[1:]],check=True,capture_output=True,text=True)
        for e,cmd in zip(p['runs'],commands):
            receipt=controls/(e['name']+'.json')
            if receipt.exists():
                prior=read(receipt)
                if prior['plan_sha256']!=sha(plan_path) or prior['command']!=cmd:
                    raise ValueError('submission claim changed')
                continue
            intent=controls/(e['name']+'.INTENT.json')
            if intent.exists():
                raise ValueError('unreceipted submission intent; reconcile scheduler')
            atomic(intent,dict(command=cmd,plan_sha256=sha(plan_path)))
            done=command(cmd,check=True,capture_output=True,text=True)
            job=done.stdout.strip().split(';')[0]
            if not job.isdigit():
                raise ValueError('unparseable job id; reconcile intent')
            atomic(receipt,dict(job_id=job,command=cmd,plan_sha256=sha(plan_path)))
            print(e['name'],job)


def smoke_readout(plan_path,out,sacct=None,sacct_sha=None):
    p=checked(plan_path)
    if not p['smoke'] or len(p['runs'])!=6:
        raise ValueError('six jobs: control + real-signal requeue for every width required')
    import torch
    sys.path.insert(0,str(ROOT/'vendor'))
    from train import train as trainer
    from compare import FIELDS
    from stage_c_isolation import reconcile
    trainer._runtime()
    costs=[]
    for width in (1.,1.5,2.):
        pair=[next(e for e in p['runs'] if e['name']=='w%g-%s'%(width,role)) for role in ('control','requeue')]
        checks=[]
        completions=[]
        for e in pair:
            cfg=read(bound(e['config']))
            c=complete(e['output'],cfg)
            ck=torch.load(bound(c['checkpoint']),map_location='cpu',weights_only=False)
            if (ck['state_sha256']!=trainer.checkpoint_state_sha256(ck) or c['mock']
                    or ck['binding']['device']!='cuda' or ck['binding']['workers']!=6):
                raise ValueError('invalid real CUDA checkpoint')
            checks.append(trainer.checkpoint_state_sha256({k:ck[k] for k in FIELDS}))
            completions.append(c)
        if checks[0]!=checks[1]:
            raise ValueError('real-signal continuation not BIT_IDENTICAL')
        resumed=Path(pair[1]['output'])
        signal_proof=read(resumed/'REAL_SIGNAL_SENT.json')
        alloc=[read(f) for f in resumed.glob('ALLOCATION_*.json')]
        yields=[read(f) for f in resumed.glob('YIELD_*.json')]
        if not any(a['job_id']==signal_proof['job_id'] and a['restart_count']>0 for a in alloc):
            raise ValueError('actual Slurm requeue missing')
        if not any(y['job_id']==signal_proof['job_id'] and y['restart_count']==0 and y['checkpoint'] and y['stop_request'] for y in yields):
            raise ValueError('real TERM durable yield missing')
        first=next(y for y in yields if y['job_id']==signal_proof['job_id'] and y['restart_count']==0 and y['checkpoint'])
        state=torch.load(bound(first['checkpoint']),map_location='cpu',weights_only=False)
        bound(first['stop_request'])
        if state['state_sha256']!=trainer.checkpoint_state_sha256(state):
            raise ValueError('real TERM yield state invalid')
        if not any(s<=state['global_step'] for s in completions[0]['binding']['loss_plan']['steps']) or not any(
                s>state['global_step'] for s in completions[0]['binding']['loss_plan']['steps']):
            raise ValueError('loss points do not straddle requeue')
        steps=completions[0]['binding']['loss_plan']['steps']
        if len(steps)<3 or completions[1]['binding']['loss_plan']['steps']!=steps:
            raise ValueError('loss cadence changed')
        for step in steps:
            values=[read(Path(e['output'])/'loss_eval'/('step-%09d.json'%step)) for e in pair]
            if any(values[0][k]!=values[1][k] for k in ('step','drawn_lines','thresholds','model_sha256','instruments')):
                raise ValueError('loss differs after real TERM')
            from loss_checkpoint import validate
            for value in values:
                validate(value['checkpoint'],trainer,step=step,drawn_lines=value['drawn_lines'],
                    runtime_sha=value['runtime_sha256'],model_sha=value['model_sha256'])
        for a,b in zip(completions[0]['evaluations'],completions[1]['evaluations']):
            if read(bound(a))['instruments']!=read(bound(b))['instruments']:
                raise ValueError('CER differs after real TERM')
        loss=[read(bound(s))['elapsed_seconds'] for s in completions[0]['loss_evaluations']]
        full=[read(bound(s))['elapsed_seconds'] for s in completions[0]['evaluations']]
        timing=[read(f) for f in Path(pair[0]['output']).glob('BATCH_TIMING_*.json')]
        if not sum(t['samples'] for t in timing):
            raise ValueError('training update timing missing')
        mean=sum(t['seconds'] for t in timing)/sum(t['samples'] for t in timing)
        batch=read(bound(pair[0]['config']))['parameters']['bs']
        train=8*math.ceil(1586454/batch)*mean
        eval_seconds=254*statistics.mean(loss)+4*statistics.mean(full)
        checkpoint=read(Path(pair[0]['output'])/'CHECKPOINT_COST.json')
        loss_records=[read(bound(s)) for s in completions[0]['loss_evaluations']]
        saves=[r['checkpoint_save']['seconds'] for r in loss_records if r['checkpoint_save']['created']]
        if len(saves)!=len(loss_records):
            raise ValueError('uninterrupted control must measure every archive creation')
        archive_bytes=max(r['checkpoint']['bytes'] for r in loss_records)
        # Startup includes Python/data/model construction until first update.
        starts=[read(f)['seconds'] for f in resumed.glob('STARTUP_*.json') if read(f)['first_step']>1]
        if not starts:
            raise ValueError('measured resume startup missing')
        costs.append(dict(width_mult=width,loss_seconds_mean=statistics.mean(loss),loss_seconds_max=max(loss),
            cer_seconds_mean=statistics.mean(full),update_seconds=mean,checkpoint_seconds=checkpoint['seconds'],
            loss_checkpoint_seconds_mean=statistics.mean(saves),loss_checkpoint_seconds_max=max(saves),
            loss_checkpoint_bytes_max=archive_bytes,projected_loss_checkpoint_GPU_h=254*statistics.mean(saves)/3600,
            projected_loss_checkpoint_bytes=254*archive_bytes,
            projected_train_hours=train/3600,projected_eval_hours=eval_seconds/3600,
            eval_over_training=eval_seconds/train,exceeds_25_percent=eval_seconds/train>.25,
            restart_startup_seconds_mean=statistics.mean(starts),restart_startup_seconds_max=max(starts)))
    report=dict(status='BIT_IDENTICAL',mock=False,package_sha256=p['payload_sha256'],
        runtime_sha256=p['runtime']['sha256'],plan=spec(plan_path),costs=costs,
        isolation=reconcile(plan_path,sacct,sacct_sha),
        signal='actual scancel --batch --signal=TERM -> persistent request -> optimizer boundary -> 75 -> scontrol requeue')
    atomic(out,report)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('plan','node','lane','submit','smoke-readout'))
    p.add_argument('--runtime'); p.add_argument('--out'); p.add_argument('--plan'); p.add_argument('--index',type=int)
    p.add_argument('--config'); p.add_argument('--smoke',action='store_true'); p.add_argument('--review'); p.add_argument('--smoke-report')
    p.add_argument('--sacct'); p.add_argument('--sacct-sha')
    a=p.parse_args()
    if a.command=='plan': build(a.runtime,a.out,smoke=a.smoke)
    elif a.command=='node': raise SystemExit(node(a.plan,a.index))
    elif a.command=='lane': raise SystemExit(lane(a.config,a.out))
    elif a.command=='submit': submit(a.plan,a.review,a.smoke_report)
    else: smoke_readout(a.plan,a.out,a.sacct,a.sacct_sha)
