"""E4 wave 1b: authorized as-is codec A/B/C plus width x3; E3 runner/readout."""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from bench import e3_driver as e3
from bench.e1_common import ROOT,atomic_json,check_files,files_binding,read_json,sha256
from bench.e1_runner import parameters,verify_done
from bench.e4_wave1a import digest,release_identity
from train.mix import validate,load_rows,assemble

CONFIGS=('v_a','v_b','v_c','w30')
SEEDS=(0,1,2)
ROWS=428872
JOBS={'job01':['v_a_s0','v_a_s1','v_a_s2','v_b_s0'],
      'job02':['v_b_s1','v_b_s2','v_c_s0','v_c_s1'],
      'job03':['v_c_s2'], 'job04':['w30_s0','w30_s1','w30_s2']}
ASIS='af1ff90200e8ad897e246192da9a420a15fec2793fbc987649dbf2ff77d81621'


def selected(value=None):
    names=[f'{c}_s{s}' for c in CONFIGS for s in SEEDS]
    if value is None:return names
    result=value.split(',')
    if not result or len(set(result))!=len(result) or set(result)-set(names):raise ValueError('invalid wave1b arms')
    return result


def code_files():
    return sorted(set(e3.code_files())|set(ROOT.glob('bench/e4*.py'))|
        set(ROOT.glob('scripts/clariden/e4_*wave1b*'))|set(ROOT.glob('bench/e4_bootstrap/*.py'))|
        {ROOT/'scripts/clariden/common.sh',ROOT/'bench/e1_eval.py',ROOT/'train/eval_cer.py'})


def load_release(a):
    path=a.campaign/'v2-codec/release.json';release=read_json(path)
    if (release['schema']!='e4-campaign1-release-v1' or release['tag']!='v2-codec'
            or release['status']!='frozen' or release['v2_asis']!=ASIS
            or release['F1']!='not-applicable: authorized as-is wave1b; no S1/label repair'):
        raise ValueError('wrong wave1b release')
    assets={}
    for key,spec in release['assets'].items():
        p=Path(spec['path'])
        if sha256(p)!=spec['sha256']:raise ValueError('release asset changed '+key)
        assets[key]=p
    check_files(release['input_inventory'])
    one,two=(read_json(assets[k]) for k in ('codec_v1','codec_v2'))
    if one['version']!='v1' or two['version']!='v2' or two['atoms'][:len(one['atoms'])]!=one['atoms']:
        raise ValueError('codec prefix mismatch')
    if read_json(assets['draw_v_a'])!=read_json(assets['draw_v_b']):raise ValueError('A/B draw mismatch')
    da,dc=(read_json(assets[k]) for k in ('draw_v_a','draw_v_c'))
    for epoch in map(str,range(1,9)):
        if da['epochs'][epoch]['class_source_counts']!=dc['epochs'][epoch]['class_source_counts']:
            raise ValueError('C quota mismatch')
    return release,assets,sha256(path)


def arm_table(a,release,assets,codec_sha,names):
    arms=[]
    for run in names:
        config,seed=run.rsplit('_s',1);p=parameters(a.out,50,int(seed),ROWS)
        mix_key={'v_a':'full_mix','v_b':'old_v2_mix','v_c':'recovered_mix'}
        codec='codec_v1' if config in ('v_a','w30') else 'codec_v2'
        mix=a.prep/'mixes/full.json' if config=='w30' else assets[mix_key[config]]
        val=a.prep/'mixes/val_mix.json' if config=='w30' else assets['val_v1' if config=='v_a' else 'val_v2']
        p.update(mix=str(mix),codec=str(assets[codec]),val_mix=str(val),transfer_mix=None,
            repeat_to_epoch_rows=True,width_mult=3. if config=='w30' else 1.)
        arms.append(dict(arm=config,run=run,seed=int(seed),initialization='from-scratch',height=48,patience=6,
            data_release='v2-asis' if config=='w30' else 'v2-codec',release_sha256=ASIS if config=='w30' else codec_sha,
            parameters=p,draw_contract=str(assets['draw_v_a' if config=='w30' else 'draw_'+config]),
            control='wave1a ctrl_s0/s1/s2' if config=='w30' else 'wave1b v_a_s0/s1/s2',depends_on=[]))
    return arms


def prepare(a):
    release,assets,codec_sha=load_release(a)
    original=release_identity(a.prep)
    if original['binding_sha256']!=ASIS:raise ValueError('v2-asis changed')
    arms=arm_table(a,release,assets,codec_sha,selected(a.arms))
    paths=[a.campaign/'v2-codec/release.json',*assets.values(),*code_files(),
        ROOT/'out/e4/wave1a/aggregate_retry2/report.json',ROOT/'out/e4/wave1a/aggregate_retry2/aggregate_status.json']
    for seed in SEEDS:
        oldrun=ROOT/'out/e4/wave1a/job01/runs'/f'ctrl_s{seed}'
        verify_done(oldrun)
        paths.extend([oldrun/'E1_RUN_COMPLETE.json',oldrun/'run_binding.json'])
    paths.extend(Path(p) for p in release['input_inventory'])
    for key in ('manifests','shards','receipts','codec'):paths.extend(Path(p) for p in original[key])
    paths.extend(sorted((a.prep/'records').glob('*.jsonl')))
    for key in ('common_intersection','full_coverage'):
        for spec in read_json(assets[key])['instruments'].values():
            path=Path(spec['path']);paths.append(path)
            mix=validate(path,role='eval')
            for c in mix['components']:
                root=Path(c.get('build_dir',c.get('shard_dir')))
                paths.extend([root/'build_info.json',*sorted(root.rglob('shard-*.parquet'))])
    for arm in arms:
        config=arm['arm']
        key='v_a' if config=='w30' else config
        drawrows=a.campaign/'v2-codec'/f'draw_rows_{key}.jsonl.gz'
        manifest=a.out/'draw_manifests'/f"{arm['run']}.json"
        e3.immutable(manifest,dict(run=arm['run'],model_seed=arm['seed'],data_seed=20261015,
            ordered_row_format=['epoch','position','component','physical_pool_index','line_id'],
            ordered_draws=dict(path=str(drawrows),sha256=sha256(drawrows)),
            image_label_contract=dict(path=arm['draw_contract'],sha256=sha256(arm['draw_contract'])),
            epochs=8,draws_per_epoch=ROWS))
        arm['draw_manifest']=str(manifest);paths.append(manifest)
    node=dict(schema='e4-wave1b-node-v1',releases={'v2-codec':codec_sha,'v2-asis':ASIS},
        out=str(a.out),prep=str(a.prep),arms=arms,inputs=files_binding(paths))
    e3.immutable(a.out/'arms.json',arms);e3.immutable(a.out/'node_binding.json',node)
    (a.out/'logs').mkdir(exist_ok=True)
    print('E4_WAVE1B_PREPARED',codec_sha,','.join(r['run'] for r in arms),flush=True)


def verify(a):
    node=read_json(a.out/'node_binding.json')
    if node['schema']!='e4-wave1b-node-v1' or node['out']!=str(a.out) or node['prep']!=str(a.prep):raise ValueError('wave1b binding destination')
    if node['releases']['v2-asis']!=ASIS or node['releases']['v2-codec']!=sha256(a.campaign/'v2-codec/release.json'):raise ValueError('wave1b release changed')
    check_files(node['inputs'])
    if read_json(a.out/'arms.json')!=node['arms']:raise ValueError('wave1b arm table changed')
    return node


def child_command(a,*extra):
    return [sys.executable,'-u','-m','bench.e4_driver','--wave1b','--prep',str(a.prep),
        '--campaign',str(a.campaign),'--out',str(a.out),*extra]


def preflight_worker(a,run):
    import torch
    from bench.e4_width_probe import training_runtime
    from train.data import ManifestDataset,make_loader,collate_strips
    from train.model import build_model,masked_forward,amp_dtype_for,autocast_ctx,count_params
    from bench.e1_eval import inference_checkpoint
    from train.eval_cer import load_checkpoint,evaluate
    from train.cer import load_codec
    trainer=training_runtime();trainer.set_seeds(0);torch.set_num_threads(8)
    arm=next(r for r in read_json(a.out/'arms.json') if r['run']==run);p=arm['parameters']
    mix=validate(p['mix']);pools=load_rows(mix,'train')
    rows,counts=assemble(pools,[c['fraction'] for c in mix['components']],mix['seed'],1,ROWS,
        exact_rows=True,replay=mix.get('matched_replay'),recovery=mix.get('codec_recovery'))
    del pools
    model,codec=build_model(codec_path=Path(p['codec']),width_mult=p['width_mult'],verbose=False)
    model.cuda().train();ds=ManifestDataset(rows,codec.version,codec.n_classes-1,'train')
    loader,sampler=make_loader(ds,64,seed=mix['seed'],shuffle=True,num_workers=6,pin_memory=True,pack_bucket_tails=True)
    sampler.set_epoch(1)
    widest=max(list(iter(sampler)),key=lambda b:len(b)*max(rows[i]['width'] for i in b))
    batch=collate_strips([ds[i] for i in widest])
    opt=torch.optim.AdamW(trainer.no_decay_param_groups(model,.05),lr=1e-4,weight_decay=.05)
    sched=torch.optim.lr_scheduler.OneCycleLR(opt,max_lr=1e-4,total_steps=8*len(sampler),pct_start=trainer.PCT_START,cycle_momentum=False)
    torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize();start=time.perf_counter()
    lens=batch['input_lengths'].cuda()
    with autocast_ctx(torch.device('cuda'),amp_dtype_for(torch.device('cuda'))):output=masked_forward(model,batch['images'].cuda(),lens)
    loss=torch.nn.CTCLoss(blank=0,zero_infinity=True)(output.float().transpose(0,1),batch['targets'].cuda(),lens,batch['target_lengths'].cuda())
    if not torch.isfinite(loss):raise ValueError('nonfinite CTC preflight')
    loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),trainer.GRAD_CLIP);opt.step();sched.step()
    torch.cuda.synchronize();seconds=time.perf_counter()-start;peak=torch.cuda.max_memory_allocated()
    temp=a.out/'preflight'/f'{run}.pt';temp.parent.mkdir(exist_ok=True)
    torch.save(inference_checkpoint(dict(model=model.state_dict(),arch='compact',head='nfd',codec_version=codec.version,
        n_classes=codec.n_classes,width_mult=p['width_mult'])),temp)
    restored,_=load_checkpoint(str(temp),codec,torch.device('cpu'))
    if count_params(restored)!=count_params(model):raise ValueError('inference geometry mismatch')
    temp.unlink()
    # Exercise different model/reference vocabularies on actual held-out data.
    full=read_json(a.campaign/'v2-codec/full_coverage.json')['instruments']['v2_test']['path']
    refs=load_codec(str(ROOT/'codec/v2.json'));evalrows=load_rows(validate(full,role='eval'),'reserved')[0]
    sample=[next(r for r in evalrows if max(r['label_ids'])>247)]
    eds=ManifestDataset(sample,refs.version,refs.n_classes-1,'reserved');el,_=make_loader(eds,1,shuffle=False,num_workers=0)
    result=evaluate(model,el,codec,torch.device('cuda'),amp_dtype=amp_dtype_for(torch.device('cuda')),reference_codec=refs)
    if result['n_lines']!=1:raise ValueError('full coverage smoke failed')
    distinct=len({(r['_component'],r['_pool_index']) for r in rows})
    atomic_json(a.out/'preflight'/f'{run}.json',dict(state='DONE',configuration=arm['arm'],steps=1,loss=loss.item(),
        parameters=count_params(model),epoch_batches=len(sampler),step_seconds=seconds,steps_per_second=1/seconds,
        max_memory_allocated=peak,GiB=peak/2**30,batch_shape=list(batch['images'].shape),
        batch_selection='widest batch by batch_size * max physical width in actual epoch-1 sampler',timing_boundary='single cold update; transfer/forward/backward/clip/AdamW/OneCycle; excludes loader and model creation; not steady-state throughput',
        component_draws=counts,distinct_draws=distinct,repeats=ROWS-distinct,releases=read_json(a.out/'node_binding.json')['releases'],
        inference_roundtrip='DONE',different_reference_vocabulary='DONE',job_id=os.environ['SLURM_JOB_ID']))
    print('E4_PREFLIGHT_STEP_DONE',run,flush=True)


def preflight(a):
    node=verify(a)
    if not os.environ.get('SLURM_JOB_ID'):raise ValueError('preflight requires Slurm')
    processes=[]
    for gpu,arm in enumerate(node['arms']):
        log=(a.out/'logs'/f'preflight_{arm["run"]}.log').open('w')
        processes.append((subprocess.Popen(child_command(a,'--preflight-worker',arm['run']),cwd=ROOT,
            env=e3.pinned_env(str(gpu)),stdout=log,stderr=log),log,arm['run']))
    errors=[]
    for proc,log,run in processes:
        if proc.wait():errors.append(run)
        log.close()
    if errors:raise ValueError('preflight failed '+','.join(errors))
    verify(a)
    atomic_json(a.out/'PREFLIGHT_DONE.json',dict(state='DONE',releases=node['releases'],
        runs=[r['run'] for r in node['arms']],steps_per_configuration=1,job_id=os.environ['SLURM_JOB_ID']))


def instruments(a,arm):
    base={name:a.prep/'mixes'/f'{name}_mix.json' for name in e3.INSTRUMENTS}
    if arm['arm']!='w30':
        full=read_json(a.campaign/'v2-codec/full_coverage.json')
        for name in e3.INSTRUMENTS[:2]:base[name+'_full_coverage']=Path(full['instruments'][name]['path'])
    return base


def evaluate_arm(a,arm):
    from bench.e1_eval import evaluate_run
    from bench import e1_common
    dest=a.out/'runs'/arm['run'];verify_done(dest)
    original=e1_common.runtime_binding
    e1_common.runtime_binding=lambda device:e3.allocation_runtime(original(device))
    try:
        for instrument,mixpath in instruments(a,arm).items():
            version=read_json(mixpath)['codec_version']
            evaluate_run(a.out,arm['run'],instrument,mixpath,codec_path=arm['parameters']['codec'],
                reference_codec_path=ROOT/'codec'/f'{version}.json')
    finally:e1_common.runtime_binding=original


def worker(a,gpu):
    node=verify(a);arms={r['run']:r for r in node['arms']}
    while (job:=e3.claim(a.out,gpu,os.getpid())) is not None:
        arm=arms[job['run']];error=None
        e3.progress(a.out,f'ARM_START arm={arm["arm"]} seed={arm["seed"]} gpu={gpu}')
        try:e3.run_arm(a,arm,gpu);evaluate_arm(a,arm)
        except Exception as exc:
            error=str(exc)
            import traceback;traceback.print_exc()
        e3.settle(a.out,arm['run'],error)
        e3.progress(a.out,f'ARM_{"DONE" if error is None else "FAILED"} arm={arm["arm"]} seed={arm["seed"]} gpu={gpu} error={error}')


def wave(a):
    node=verify(a);pre=read_json(a.campaign/'preflight/PREFLIGHT_DONE.json')
    if pre['state']!='DONE' or pre['releases']!=node['releases']:raise ValueError('successful bound preflight required')
    if not os.environ.get('SLURM_JOB_ID') or len(node['arms'])>4:raise ValueError('wave needs Slurm; at most four arms')
    # Width x3 is isolated as one seed per GPU on its dedicated node.
    if any(r['arm']=='w30' for r in node['arms']) and any(r['arm']!='w30' for r in node['arms']):raise ValueError('w30 requires dedicated node')
    gpus=e3.visible_gpus('0,1,2,3');e3.init_queue(a.out,node['arms'],gpus)
    with (a.out/'logs/workers.log').open('a') as log:
        def launch(gpu):return subprocess.Popen(child_command(a,'--worker',gpu),cwd=ROOT,env=e3.pinned_env(gpu),stdout=log,stderr=log,start_new_session=True)
        queue=e3.supervise_queue(a.out,gpus,launch)
    verify(a);complete=[r['run'] for r in queue if r['status']=='done']
    atomic_json(a.out/'runs_summary.json',dict(queue=queue,failed=[r['run'] for r in queue if r['status']!='done']))
    if complete:report(a,{r:a.out for r in complete})
    outputs=[a.out/'queue.json',a.out/'runs_summary.json']
    if complete:outputs.extend([a.out/'report.json',a.out/'REPORT.md'])
    atomic_json(a.out/'E4_COMPLETE.json',dict(schema='e4-wave1b-complete-v1',arms=complete,complete=len(complete)==len(node['arms']),
        node_binding_sha256=sha256(a.out/'node_binding.json'),outputs=files_binding(outputs),
        predictions=files_binding(p for p in (a.out/'predictions').glob('*') if p.is_file())))
    if len(complete)!=len(node['arms']):raise ValueError('some wave1b arms failed')


def report(a,roots):
    from bench.common import read_rows
    from bench.e1_readout import summarize,clean_row,metric,mark_metrics,MARKS,table
    results={};data={}
    for run,root in roots.items():
        arm=next(r for r in read_json(root/'arms.json') if r['run']==run)
        for instrument in instruments(a,arm):
            pred=root/'predictions'/f'{run}_{instrument}.jsonl';receipt=read_json(pred.with_suffix('.receipt.json'))
            if sha256(pred)!=receipt['predictions_sha256']:raise ValueError('prediction changed')
            check_files(receipt['crop_hashes']);raw=list(read_rows(pred))
            if len(raw)!=receipt['result']['n_lines'] or not raw or any(r['arm']!=arm['arm'] or r['seed']!=arm['seed'] or r['instrument']!=instrument for r in raw):raise ValueError('prediction identity/count mismatch')
            base=instrument.removesuffix('_full_coverage')
            rows=e3.joined_rows(raw,a.prep,base) if base in e3.INSTRUMENTS[:2] else [clean_row(r) for r in raw]
            result=summarize(rows)
            for field in ('source_script_class','wave','language') if base in e3.INSTRUMENTS[:2] else ():
                result['by_'+field]={k:metric([r for r in rows if r[field]==k]) for k in sorted({r[field] for r in rows})}
            if base in e3.INSTRUMENTS[:2]:
                result['marks']=mark_metrics(rows)
                result['pain_strata']={k:metric([r for r in rows if any(c in r['gt'] for c in chars)]) for k,chars in MARKS.items()}
            results[run+'/'+instrument]=result;data[run+'/'+instrument]=rows
            if arm['arm']!='w30' and instrument in e3.INSTRUMENTS:
                results[run+'/'+instrument+'_common_intersection']=result
                if instrument not in e3.INSTRUMENTS[:2]:results[run+'/'+instrument+'_full_coverage']=result
    aggregates={}
    for key,result in results.items():
        run,instrument=key.split('/');config,seed=run.rsplit('_s',1)
        aggregates.setdefault(instrument,{}).setdefault(config,{})[seed]=result['overall']['cer']
    aggregate={i:{c:dict(seeds=v,n_seeds=len(v),complete=len(v)==3,mean=sum(v.values())/len(v),min=min(v.values()),max=max(v.values()),range=max(v.values())-min(v.values())) for c,v in groups.items()} for i,groups in aggregates.items()}
    missing=sorted(set(selected())-set(roots))
    obj=dict(schema='e4-wave1b-report-v1',releases=read_json(a.campaign/'preflight/node_binding.json')['releases'],
        metric='strict literal NFD codepoint CER; prediction vocabulary and reference vocabulary separately hash-bound',
        arms=list(roots),missing_arms=missing,results=results,aggregate=aggregate,complete=not missing,
        common_intersection='Original four instrument populations and labels; views reuse the exact base predictions',
        full_coverage='Adds only native v2-recovered held-out rows; e1/synthetic unchanged; v1 is scored literally against v2 references',
        geometry_clean='Absent at intake; skipped secondary column',
        verdict_rule='Seed mean/min/max/range descriptive; beyond seed range is not equivalence. H2 no-measurable-cost needs confidence bound; H3 Cyrillic plus Greek strata; H7 compare pinned wave1a controls/widths.')
    atomic_json(a.out/'report.json',obj)
    md=['# E4 wave 1b','',obj['metric'],'',
        'Custody: every prediction file, crop, node binding, completed run and source fragment is hash-checked; the aggregate completion receipt hashes this report and Markdown. Common-intersection views reuse identical base predictions; no literal reference is rewritten.','']
    for instrument,summaries in aggregate.items():
        md+=['## '+instrument,'']+table(['arm','seeds','mean CER','min','max','range'],[(k,len(v['seeds']),v['mean'],v['min'],v['max'],v['range']) for k,v in summaries.items()])
    md+=['Missing arms: '+', '.join(missing),'',obj['verdict_rule'],'']
    (a.out/'REPORT.md').write_text('\n'.join(md)+'\n')


def aggregate(a):
    if not a.inputs:raise ValueError('--inputs required')
    inputs=[Path(p).resolve() for p in a.inputs.split(',')]
    if len(set(inputs))!=len(inputs) or a.out in inputs:raise ValueError('aggregate inputs must be distinct')
    roots={};failures={};sources={};common=None
    for root in inputs:
        if not (root/'E4_COMPLETE.json').exists():failures[str(root)]='no completion receipt';continue
        node=read_json(root/'node_binding.json');done=read_json(root/'E4_COMPLETE.json')
        if common is not None and node['releases']!=common:raise ValueError('aggregate release mismatch')
        common=node['releases'];check_files(node['inputs'])
        if done['node_binding_sha256']!=sha256(root/'node_binding.json'):raise ValueError('completion binding mismatch')
        check_files(done['outputs']);check_files(done['predictions'])
        for run in done['arms']:
            if run in roots:raise ValueError('duplicate aggregate arm')
            verify_done(root/'runs'/run);roots[run]=root
        if not done['complete']:failures[str(root)]='partial training/readout'
        sources[str(root)]=files_binding([root/'node_binding.json',root/'E4_COMPLETE.json'])
    a.out.mkdir(parents=True,exist_ok=True)
    if roots:report(a,roots)
    # Bring the already completed original controls/widths into the comparison,
    # bound to their immutable readback report; never rebind or retrain them.
    control_path=ROOT/'out/e4/wave1a/aggregate_retry2/report.json'
    controls=read_json(control_path)
    if controls['release_sha256']!=ASIS:raise ValueError('pinned wave1a control release differs')
    comparison=dict(wave1a_report_sha256=sha256(control_path),wave1a_release=ASIS,
        pinned={i:{c:v for c,v in groups.items() if c in ('ctrl','w15','w20')} for i,groups in controls['aggregate'].items()})
    atomic_json(a.out/'pinned_controls.json',comparison)
    reports=[a.out/'pinned_controls.json']+([a.out/'report.json',a.out/'REPORT.md'] if roots else [])
    atomic_json(a.out/'aggregate_status.json',dict(state='DONE' if not failures and len(roots)==12 else 'PARTIAL',arms=list(roots),failures=failures,sources=sources))
    atomic_json(a.out/'E4_AGGREGATE_COMPLETE.json',dict(state='DONE' if not failures and len(roots)==12 else 'PARTIAL',
        outputs=files_binding([*reports,a.out/'aggregate_status.json']),sources=sources,job_id=os.environ.get('SLURM_JOB_ID')))
    print('E4_WAVE1B_AGGREGATE_DONE',len(roots),flush=True)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--wave1b',action='store_true')
    ap.add_argument('--prep',type=Path,default=Path('out/e3'));ap.add_argument('--campaign',type=Path,default=Path('out/e4/wave1b'))
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--arms');ap.add_argument('--prepare',action='store_true')
    ap.add_argument('--stage',choices=('preflight','runs','aggregate'));ap.add_argument('--worker');ap.add_argument('--preflight-worker');ap.add_argument('--inputs')
    a=ap.parse_args(argv)
    for key in ('prep','campaign','out'):setattr(a,key,getattr(a,key).resolve())
    if a.prepare:return prepare(a)
    if a.preflight_worker:return preflight_worker(a,a.preflight_worker)
    if a.worker:return worker(a,a.worker)
    if a.stage=='preflight':return preflight(a)
    if a.stage=='runs':return wave(a)
    if a.stage=='aggregate':return aggregate(a)
    ap.error('choose --prepare or --stage')
if __name__=='__main__':main()
