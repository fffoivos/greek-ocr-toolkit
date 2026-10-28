"""S1 compute entry points, sharing E1 training and wave-2 evaluation functions.

All population reads are compute-only. This module never calls a scheduler.
"""
from __future__ import annotations
import argparse
from collections import Counter
import copy
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace
from bench import s1_scaling as s1
from bench.e1_common import ROOT,atomic_json,read_json,sha256,check_files,files_binding
from train.mix import validate,load_rows,assemble


_CPU_PREPARE_ROOT = None


@contextmanager
def cpu_rehearsal(folder):
    """CPU preparation, confined to one disposable deployed-package folder."""
    global _CPU_PREPARE_ROOT
    folder = Path(folder).resolve()
    if (_CPU_PREPARE_ROOT is not None
        or ROOT.parent != s1.W/'scaling_w3/train_pkg'
        or folder.parent != ROOT.resolve() or not folder.name.startswith('rehearsal_')):
        raise ValueError('S1_REHEARSAL_SCOPE')
    _CPU_PREPARE_ROOT = folder
    try:
        yield
    finally:
        _CPU_PREPARE_ROOT = None


def compute_only(*, cpu_prepare=False):
    if _CPU_PREPARE_ROOT is not None:
        if cpu_prepare: return
        raise ValueError('S1_REHEARSAL_TRAINING_FORBIDDEN')
    if not os.environ.get('SLURM_JOB_ID'): raise ValueError('COMPUTE_ALLOCATION_REQUIRED')


def assert_output(path):
    if (os.environ.get('S1_RUNTIME_QUALIFICATION')=='1'
        and ROOT.parent==s1.W/'scaling_w3/train_pkg'
        and Path(path).resolve().is_relative_to(ROOT/'runtime01')):
        return
    if _CPU_PREPARE_ROOT is not None:
        if not Path(path).resolve().is_relative_to(_CPU_PREPARE_ROOT):
            raise ValueError('S1_REHEARSAL_OUTPUT_SCOPE')
        return
    root=(s1.W/'scaling_w3/s1_run01').resolve()
    smoke=ROOT.resolve()/'smoke01'
    allowed=Path(path).resolve().is_relative_to(root)
    if os.environ.get('S1_SMOKE')=='1' and ROOT.parent==s1.W/'scaling_w3/train_pkg':
        allowed=allowed or Path(path).resolve().is_relative_to(smoke)
    if not allowed: raise ValueError('S1_OUTPUT_SCOPE')


def smoke_slice(source, target, split, requested):
    """At least one row per active component, with no other smoke enlargement."""
    from bench.e4_wave1c import slice_mix
    active = sum(c['fraction'] > 0 for c in read_json(source)['components'])
    budget = max(requested, active)
    path = slice_mix(source, target, split, budget)
    pools = load_rows(validate(path, role='train' if split == 'train' else 'val' if split == 'val' else 'eval'), split)
    counts = [len(pool) for pool in pools]
    atomic_json(Path(target).with_suffix('.slice.json'), dict(source=s1.spec(source),
        split=split, requested=requested, active_components=active, budget=budget,
        selected_rows=sum(counts), per_component=counts))
    return path


def prepare_cell(cfg, proof_spec, subset, width, out, *, smoke=False):
    """Identical prepare path for production and smoke, except explicit slicing."""
    from bench.e1_runner import parameters
    compute_only(cpu_prepare=True);assert_output(out)
    proof=read_json(s1.bound(proof_spec))
    if proof['input_sha256']!=s1.digest_json(cfg) or not all(proof['checks'].get(k) for k in 'abcde'):
        raise ValueError('S1_INPUT_PROOF_MISMATCH')
    s1.require_cache(proof['cache'],cfg['census05'],s1.load_subset(cfg['subsets'][subset]))
    out=Path(out);out.mkdir(parents=True,exist_ok=True);(out/'logs').mkdir(exist_ok=True)
    source=read_json(s1.bound(cfg['shared_mix']))['components'][0]
    rows=s1.load_subset(cfg['subsets'][subset]);parl=sum(r['source']=='parliament_proceedings_1975_2000' for r in rows)
    share=min(parl/len(rows),.25)
    components=[dict(source,source='non_parliament',fraction=.5*(1-share))]
    if parl: components.append(dict(source,source='parliament',fraction=.5*share))
    syn=Path(cfg['synthetic']['path']);info=read_json(syn/'build_info.json')
    components.append(dict(kind='synthetic',build_dir=str(syn),recipe_sha256=info['recipe_sha256'],fraction=.5))
    mix=dict(schema_version=1,seed=20261015,codec_version='v2.1',created_by='S1',notes='raw shared rows; exact subset membership; assemble',
        components=components,s1_selection=dict(subset={k:cfg['subsets'][subset][k] for k in ('path','sha256','rows')},provenance=proof['provenance_spec']))
    mixpath=out/'mix.json';atomic_json(mixpath,mix)
    groups=load_rows(validate(mixpath),'train')
    if sum(len(g) for g,c in zip(groups,components) if c['kind']=='real')!=s1.SIZES[subset]: raise ValueError('S1_CELL_SUPPORT')
    if smoke:
        # Slice losslessly after running the production membership/label prepare.
        mixpath=smoke_slice(mixpath,out/'smoke_mix.json','train',8)
        # slice_mix materializes selected pools; remove the already-applied selector.
        sliced=read_json(mixpath);sliced.pop('s1_selection',None);atomic_json(mixpath,sliced)
        groups=load_rows(validate(mixpath),'train');components=sliced['components']
    distinct=set();stats={};total=0
    for epoch in range(1,(1 if smoke else 8)+1):
        drawn,counts=assemble(groups,[c['fraction'] for c in components],20261015,epoch,256 if smoke else s1.D,exact_rows=True)
        real=[r for r in drawn if components[r['_component']]['kind']=='real']
        unique={(r['_component'],r['_pool_index']) for r in drawn};distinct.update(unique);total+=len(drawn)
        parliament=sum(r.get('source_dataset')=='parliament_proceedings_1975_2000' for r in real)
        if len(real)*2!=len(drawn) or parliament*4>len(real): raise ValueError('S1_DRAW_POLICY')
        stats[str(epoch)]=dict(draws=len(drawn),real=len(real),synthetic=len(drawn)-len(real),parliament=parliament,
            distinct=len(unique),repeats=len(drawn)-len(unique),distinct_real=len({r['line_id'] for r in real}))
    atomic_json(out/'EXPOSURE_AND_SUPPORT.json',dict(exposure=proof['exposure'][subset],pool_rows=s1.SIZES[subset],
        epochs=stats,distinct_support=len(distinct),repeats=total-len(distinct)))
    val=proof['validation'];instruments=proof['instruments']
    if smoke:
        val=str(smoke_slice(val,out/'smoke_val.json','val',4))
        # The literal seal04 scorer requires every panel row. Continuity views
        # may be sliced; the two benchmark panels must remain complete.
        instruments={k:(v if k.startswith('benchmark_v02_') else
            str(smoke_slice(v,out/('smoke_'+k+'.json'),'reserved',4))) for k,v in instruments.items()}
    arms=[]
    for seed in ([0] if smoke else range(3)):
        name=f'w{width:g}_{subset}';p=parameters(out,50,seed,s1.D)
        p.update(mix=str(mixpath),codec=str(ROOT/'codec/v2.1.json'),val_mix=val,transfer_mix=None,
            repeat_to_epoch_rows=True,width_mult=width,epochs=1 if smoke else 8,epoch_rows=256 if smoke else s1.D)
        p['segment']=True
        if smoke:p['workers']=0
        arms.append(dict(arm=name,run=name+f'_s{seed}',seed=seed,initialization='from-scratch',parameters=p))
    from bench.e3_driver import immutable
    immutable(out/'arms.json',arms)
    node=dict(schema='s1-node-v1',mode='SMOKE' if smoke else 'PRODUCTION',arms=arms,instruments=instruments,
        input_sha256=s1.digest_json(cfg),proof=proof_spec,subset=subset,width=width,
        inputs=files_binding([mixpath,proof_spec['path'],proof['provenance_spec']['path'],proof['cache']['path'],
            val,*instruments.values()]))
    immutable(out/'node_binding.json',node)
    return node


def preflight(cfg, out, prep, campaign, factory, *, population_proof=None):
    from bench.e4_wave2_r3 import prepare_benchmark
    from bench.e4_wave2 import validation_v21
    from bench.e4_wave1c import instruments
    compute_only(cpu_prepare=True);assert_output(out);out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    if population_proof is None:
        cache=s1.build_cache(cfg['census05'],out/'CENSUS_CACHE.json')
        proof=s1.validate_inputs(cfg,cache)
        provenance=proof.pop('provenance');atomic_json(out/'PROVENANCE.json',provenance)
        proof['provenance_spec']=s1.spec(out/'PROVENANCE.json');proof['cache']=cache
    else:
        from scripts.ops.s1_verify import inputs
        inputs(cfg,population_proof)
        proof=copy.deepcopy(read_json(s1.bound(population_proof)))
        proof['population_predecessor']=population_proof
    a=SimpleNamespace(prep=prep,campaign=campaign)
    inst=instruments(a);inst.update(prepare_benchmark(cfg,out/'benchmark',factory,ROOT/'codec/v2.1.json'))
    proof['instruments']={k:str(v) for k,v in inst.items()}
    # Frozen validation from the wave1b release; no wave2 root is written.
    release=read_json(campaign/'v2-codec/release.json');val=release['assets']['val_v2']
    s1.bound(val)
    proof['validation']=str(validation_v21(val['path'],out/'validation'))
    proof['seven_row_reconciliation']=s1.verify_seven_rows(cfg)
    proof['seven_rows']=proof['seven_row_reconciliation']['additions']
    (out/'SEVEN_ROWS.json').write_bytes(s1.seven_rows_bytes(proof['seven_rows']))
    proof['elapsed_seconds']=time.monotonic()-start
    atomic_json(out/'INPUT_PROOF.json',proof)
    return proof


def smoke(cfg, out, prep, campaign, factory, population_proof):
    """One node, all eight cells, four optimizer steps each, full seal04 scores."""
    compute_only();assert_output(out)
    if os.environ.get('S1_SMOKE')!='1' or len(os.environ.get('CUDA_VISIBLE_DEVICES','').split(','))!=1:
        raise ValueError('SMOKE_ONE_GPU_REQUIRED')
    out.mkdir(parents=True,exist_ok=False)
    preflight(cfg,out/'preflight',prep,campaign,factory,population_proof=population_proof)
    proof=s1.spec(out/'preflight/INPUT_PROOF.json');completed=[]
    for width,subset in s1.active_cells():
        cell=f'w{width:g}_{subset}';folder=out/cell
        tick=time.monotonic()
        node=prepare_cell(cfg,proof,subset,width,folder,smoke=True)
        prepare_seconds=time.monotonic()-tick;tick=time.monotonic()
        train_eval(cfg,node,folder,smoke=True)
        # Refuse a success marker unless training and both literal-panel
        # scorers produced their actual completion artifacts.
        from bench.e1_runner import verify_done
        run=node['arms'][0]['run'];done=verify_done(folder/'runs'/run)
        if done['epoch']!=1 or done['global_step']!=4:raise ValueError('SMOKE_STEP_COUNT')
        scores={name:s1.spec(folder/'predictions'/f'{run}_{name}.score.json')
                for name in cfg['benchmark_0_2']['panels']}
        completed.append(dict(cell=cell,prepare_seconds=prepare_seconds,
            train_eval_seconds=time.monotonic()-tick,completion=s1.spec(folder/'runs'/run/'E1_RUN_COMPLETE.json'),scores=scores))
        atomic_json(out/'SMOKE_PROGRESS.json',completed)
    from bench.s1_resume import forced_split
    split=forced_split(read_json(out/'w1_ref_208k/arms.json')[0]['parameters'],out/'forced_split')
    if split['state']!='BIT_IDENTICAL':raise ValueError('S1_SPLIT_PROOF_REQUIRED')
    result=dict(forced_split=split,state='SMOKE_OK',scope='smoke_only_not_CP4B',cells=completed,
        population_proof=population_proof,proof=proof,job_id=os.environ['SLURM_JOB_ID'])
    atomic_json(out/'SMOKE_DONE.json',result)
    return result


def qualification_deployment(out):
    """Qualification writes only into a fresh attempt under this package."""
    import re
    out=Path(out).resolve();root=ROOT.resolve()
    if out.parent != root or not re.fullmatch(r'qualification[0-9]{2}',out.name):
        raise ValueError('QUALIFICATION_OUTPUT_SCOPE')
    deployment=read_json(root/'DEPLOY_RECEIPT.json')
    if (deployment['state'] != 'DEPLOYED' or deployment['root'] != str(root)
        or deployment.get('source_state') != 'WORKTREE_SNAPSHOT'
        or deployment['manifest_sha256'] != sha256(root/deployment['manifest_path'])
        or deployment['manifest_sha256'][:16] != root.name):
        raise ValueError('QUALIFICATION_DEPLOYMENT_IDENTITY')
    snapshot=read_json(s1.bound(deployment['source_snapshot']))
    if snapshot['base_commit'] != deployment['commit']:
        raise ValueError('QUALIFICATION_SOURCE_IDENTITY')
    return deployment


def qualify_population(cfg, out):
    """Package-tested population stages; sbatch contains argument plumbing only."""
    from bench.e4_wave2_r3 import split2_ledgers
    compute_only();qualification_deployment(out)
    loads=read_json(out/'QUALIFICATION_LOAD.json')
    if not loads or any(r['errors'] or r['state'] != 'LOAD_OK' for r in loads):
        raise ValueError('QUALIFICATION_LOAD_FAIL')
    started=time.monotonic();timings={}
    def stage(name, fn):
        tick=time.monotonic();result=fn();timings[name]=time.monotonic()-tick
        print(json.dumps(dict(stage=name,seconds=timings[name])),flush=True)
        return result
    cache=stage('census_cache',lambda:s1.build_cache(cfg['census05'],out/'CENSUS_CACHE.json'))
    proof=stage('population_abcde',lambda:s1.validate_inputs(cfg,cache))
    atomic_json(out/'PROVENANCE.json',proof.pop('provenance'))
    proof['provenance_spec']=s1.spec(out/'PROVENANCE.json');proof['cache']=cache
    oldcfg=read_json(s1.DOC/'record/WAVE2_INPUTS.json')
    for key in ('split2','editions','heldout_editions'):
        if oldcfg[key] != cfg[key]:raise ValueError('SPLIT2_INPUT_IDENTITY_MISMATCH:'+key)
    def check_split2():
        mapping,heldout=split2_ledgers(oldcfg)
        return dict(row_count=len(mapping),heldout_editions=len(heldout))
    proof['split2_ledger']=stage('split2_ledgers',check_split2)
    proof['seven_row_reconciliation']=stage('seven_rows',lambda:s1.verify_seven_rows(cfg))
    proof['seven_rows']=proof['seven_row_reconciliation']['additions']
    (out/'SEVEN_ROWS.json').write_bytes(s1.seven_rows_bytes(proof['seven_rows']))
    proof['elapsed_seconds']=time.monotonic()-started;proof['stage_seconds']=timings
    proof['scope']='population_inputs_only; no benchmark preparation, training, smoke or measured-limit qualification'
    atomic_json(out/'INPUT_PROOF.json',proof)
    atomic_json(out/'POPULATION_TIMINGS.json',dict(stage_seconds=timings,elapsed_seconds=proof['elapsed_seconds']))
    return proof


def qualification_receipt(cfg, out):
    compute_only();deployment=qualification_deployment(out)
    proof=read_json(out/'INPUT_PROOF.json')
    if (out/'VERIFY_INPUTS.log').read_text().strip() != 'VERIFY_INPUTS_OK':
        raise ValueError('VERIFY_INPUTS_RECEIPT_MISSING')
    if sha256(out/'INPUT_PROOF.json') != os.environ['S1_PROOF_SHA256']:
        raise ValueError('INPUT_PROOF_CHANGED')
    if proof['input_sha256'] != s1.digest_json(cfg) or not all(proof['checks'].get(k) is True for k in 'abcde'):
        raise ValueError('POPULATION_CHECK_FAILED')
    recon=proof['seven_row_reconciliation']
    if (recon['predecessor_ids'] != 364864 or recon['current_ids'] != 364871
        or recon['shared_record_ids'] != 364871 or recon['shared_shard_ids'] != 364871
        or len(recon['additions']) != 7):
        raise ValueError('SEVEN_ROWS_RECEIPT_MISMATCH')
    pinned=s1.bound(recon['pinned']).read_bytes()
    if (sha256(out/'SEVEN_ROWS.json') != s1.SEVEN_ROWS_SHA256
        or (out/'SEVEN_ROWS.json').read_bytes() != pinned
        or s1.seven_rows_bytes(recon['additions']) != pinned):
        raise ValueError('S1_SEVEN_ROWS_PIN_MISMATCH')
    for binding in (proof['cache'],proof['provenance_spec'],recon['predecessor']):s1.bound(binding)
    receipt=dict(state='VERIFY_OK',scope='population_inputs_only',package_id=ROOT.name,
        source_commit=deployment['commit'],source_state=deployment['source_state'],
        manifest_sha256=deployment['manifest_sha256'],source_snapshot=deployment['source_snapshot'],
        job_id=os.environ['SLURM_JOB_ID'],deployment=s1.spec(ROOT/'DEPLOY_RECEIPT.json'),
        input_sha256=proof['input_sha256'],input_proof=s1.spec(out/'INPUT_PROOF.json'),cache=proof['cache'],
        seven_rows=s1.spec(out/'SEVEN_ROWS.json'),predecessor=recon['predecessor'],
        provenance=proof['provenance_spec'],pinned_seven_rows=recon['pinned'],
        timings=s1.spec(out/'POPULATION_TIMINGS.json'),
        remaining=['measured preparation/train/eval stage limits x1.5','three-width debug smoke',
                   'CP4B prior accounting/cap reservation'])
    atomic_json(out/'QUALIFICATION_RECEIPT.json',receipt)
    return receipt


def check_qualification_receipt(out, expected_manifest, expected_commit):
    deployment=qualification_deployment(out);r=read_json(out/'QUALIFICATION_RECEIPT.json')
    if (r['state'] != 'VERIFY_OK' or r['scope'] != 'population_inputs_only'
        or r['package_id'] != ROOT.name or r['source_commit'] != expected_commit
        or r.get('source_state') != 'WORKTREE_SNAPSHOT' or r['manifest_sha256'] != expected_manifest
        or deployment['manifest_sha256'] != expected_manifest or deployment['commit'] != expected_commit):
        raise ValueError('QUALIFICATION_RECEIPT_INVALID')
    for key in ('deployment','source_snapshot','input_proof','cache','seven_rows','timings','predecessor','provenance','pinned_seven_rows'):
        s1.bound(r[key])
    if s1.bound(r['seven_rows']).read_bytes() != s1.bound(r['pinned_seven_rows']).read_bytes():
        raise ValueError('S1_SEVEN_ROWS_PIN_MISMATCH')
    print('VERIFY_OK',sha256(out/'QUALIFICATION_RECEIPT.json'),flush=True)
    return r


def train_eval(cfg, node, out, *, smoke=False):
    from bench import e3_driver as e3
    from bench.e1_eval import evaluate_run
    from bench.e4_wave2_r3 import score_benchmark
    from bench import e1_common
    compute_only();check_files(node['inputs']);s1.bound(node['proof'])
    a=SimpleNamespace(out=out)
    original=e1_common.runtime_binding
    e1_common.runtime_binding=lambda device:e3.allocation_runtime(original(device))
    try:
        for arm in node['arms']:
            from bench.s1_resume import run_arm
            run_arm(out,arm)
            for name,path in node['instruments'].items():
                codec=ROOT/'codec'/f"{read_json(path)['codec_version']}.json"
                evaluate_run(out,arm['run'],name,Path(path),codec_path=arm['parameters']['codec'],reference_codec_path=codec)
            score_benchmark(cfg,out,arm['run'],smoke)
    finally:e1_common.runtime_binding=original


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=('preflight','cell','smoke','worker','qualification','qualification-receipt','qualification-check'),required=True)
    p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seed',type=int,choices=(0,1,2));p.add_argument('--gpu');
    p.add_argument('--proof',type=Path);p.add_argument('--proof-sha256')
    p.add_argument('--width',type=float,choices=s1.WIDTHS);p.add_argument('--subset',choices=s1.SIZES)
    p.add_argument('--prep',type=Path);p.add_argument('--campaign',type=Path)
    p.add_argument('--factory',type=Path,default=ROOT/'factory/target/release/linefactory')
    p.add_argument('--expected-manifest');p.add_argument('--expected-commit')
    a=p.parse_args(argv)
    if a.stage=='qualification-check':
        if not a.expected_manifest or not a.expected_commit:p.error('expected manifest and commit required')
        check_qualification_receipt(a.out,a.expected_manifest,a.expected_commit);return
    if a.stage in ('qualification','qualification-receipt'):
        cfg=read_json(a.inputs)
        (qualify_population if a.stage=='qualification' else qualification_receipt)(cfg,a.out);return
    compute_only();assert_output(a.out)
    cfg=read_json(a.inputs)
    if a.stage=='worker':
        node=read_json(a.out/'node_binding.json');node['arms']=[r for r in node['arms'] if r['seed']==a.seed]
        if len(node['arms'])!=1 or a.gpu!=os.environ.get('CUDA_VISIBLE_DEVICES'):raise ValueError('WORKER_IDENTITY')
        train_eval(cfg,node,a.out)
    elif a.stage=='preflight':
        if not a.prep or not a.campaign:p.error('--prep and --campaign required')
        preflight(cfg,a.out,a.prep,a.campaign,a.factory)
    elif a.stage=='smoke':
        if not a.prep or not a.campaign or not a.proof or not a.proof_sha256:
            p.error('smoke requires prep, campaign and hash-bound qualification proof')
        smoke(cfg,a.out,a.prep,a.campaign,a.factory,dict(path=str(a.proof),sha256=a.proof_sha256))
    else:
        if not a.proof or not a.proof_sha256:p.error('hash-bound --proof required')
        proof=dict(path=str(a.proof),sha256=a.proof_sha256)
        widths=s1.WIDTHS if a.stage=='smoke' else [a.width]
        if None in widths or not a.subset:p.error('--width and --subset required')
        for width in widths:
            out=a.out/f'w{width:g}' if a.stage=='smoke' else a.out
            node=read_json(out/'node_binding.json') if (out/'node_binding.json').exists() else prepare_cell(cfg,proof,a.subset,width,out,smoke=False)
            if node['width']!=width or node['subset']!=a.subset or node['input_sha256']!=s1.digest_json(cfg):
                raise ValueError('S1_RESUME_NODE_IDENTITY')
            if a.stage=='smoke':
                if len(os.environ.get('CUDA_VISIBLE_DEVICES','').split(','))!=1:raise ValueError('SMOKE_ONE_GPU_REQUIRED')
                train_eval(cfg,node,out,smoke=True)
            else:
                devices=os.environ.get('CUDA_VISIBLE_DEVICES','').split(',')
                if len(devices)!=3 or len(set(devices))!=3:raise ValueError('S1_THREE_DISTINCT_GPUS_REQUIRED')
                children=[]
                for seed,gpu in enumerate(devices):
                    cmd=[sys.executable,'-B','-m','bench.s1_jobs','--stage','worker','--inputs',str(a.inputs),'--out',str(out),'--seed',str(seed),'--gpu',gpu]
                    children.append(subprocess.Popen(cmd,env={**os.environ,'CUDA_VISIBLE_DEVICES':gpu}))
                import signal
                previous=signal.signal(signal.SIGTERM,lambda *_:[c.send_signal(signal.SIGTERM) for c in children if c.poll() is None])
                try:statuses=[child.wait() for child in children]
                finally:signal.signal(signal.SIGTERM,previous)
                if any(s not in (0,75) for s in statuses):raise ValueError('S1_WORKER_FAILED:'+repr(statuses))
                if any(s==75 for s in statuses):raise SystemExit(75)
                from bench.s1_resume import finish_cell
                finish_cell(out)


if __name__=='__main__':main()
