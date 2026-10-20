"""CSCS-bound inventory and same-input native qualification, not a submitter."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from copy import deepcopy

TOOLKIT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(TOOLKIT))
sys.path.insert(0,str(Path(__file__).parent))
from filter_crop_paths import rewrite_crop, physical_crop
from greekocr.harvest.line_pipeline import canonical, digest
from greekocr.harvest.line_pipeline_census import records, run, verify_versions, atomic_json
from greekocr.harvest.line_pipeline_native import file_sha
from greekocr.harvest.line_pipeline_sources import canonicalize
from greekocr.harvest.line_pipeline_runtime import capture, validate
from greekocr.harvest.line_pipeline_parallel import MAX_PENDING_OBSERVATIONS


def worker_guard():
    if not os.environ.get('SLURM_JOB_ID') or platform.system()!='Linux':
        raise RuntimeError('native qualification/inventory requires a Linux Slurm worker')


def environment(root):
    node=json.loads((root/'runtime/node.json').read_text())
    os.environ['PATH']=str(Path(node['node']).parent)+os.pathsep+os.environ['PATH']
    if file_sha(node['node'])!=node['node_sha256']:raise ValueError('Node runtime changed')
    versions=json.loads((TOOLKIT/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
    verify_versions(versions)
    import cv2,numpy,PIL,scipy
    cv2.setNumThreads(0)
    if cv2.getNumThreads()!=1:raise RuntimeError('OpenCV single-thread contract unavailable')
    return dict(host=socket.gethostname(),job_id=os.environ['SLURM_JOB_ID'],partition=os.environ.get('SLURM_JOB_PARTITION'),
        python=sys.version,architecture=platform.machine(),node=node,affinity_cpus=len(os.sched_getaffinity(0)),
        packages={n:importlib.metadata.version(n) for n in ['numpy','Pillow','scipy','opencv-python-headless','pytest']},
        predictor_sha256=file_sha(root/'runtime/rust-target/release/greekocr-frozen-font-predict'))


def inputs(root):
    base=root.parent/'collection_v2'
    result=[dict(id='collection-v2-'+split,format='collection-v2',path=str(base/f'import_real_v2_{split}.jsonl'),split=split)
        for split in ['train','dev','test']]
    for name in ['W1','W2']:
        result.append(dict(id='collect-v3-'+name+'-20261018-0524',format='collect-v3-features',
            path=str(root/'inputs/collect-v3-data/snapshots'/f'{name}_features_20261018_0524.jsonl'),
            path_map={'/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data':str(root/'inputs/collect-v3-data')}))
    return result


def old_crop(record,root):
    # Preserve the ORIGINAL collection root; never consult masked/recut pools.
    spelling=rewrite_crop(record['crop'],record['wave'])
    return physical_crop(root.parent/'collection_v2/crops',spelling,'node')[0]


def sample(root,out,n,stratified=False):
    rows=[]
    for parent in [inputs(root)[0],*inputs(root)[3:]]:
        selected=None
        if stratified:
            import heapq
            # Deterministic hash sample of the complete parent, not a prefix.
            selected=heapq.nsmallest(n,records(parent['path']),key=lambda pair:digest(parent['id']+'\0'+pair[1]['id']))
        chosen=0
        for _,record in selected if selected is not None else records(parent['path']):
            if parent['format']=='collection-v2':
                path=old_crop(record,root)
                if not path.is_file():continue
                r=dict(record,parent_id=parent['id'],book_id=record['doc'],page_id=record['id'].rsplit('-l',1)[0],
                    edition_id='unresolved:'+record['doc'],edition_identity_status='unresolved',raw_text=record['label'],
                    crop_path=str(path),crop_sha256=file_sha(path))
            else:
                r=canonicalize(record,parent,{})
                # Bound native source pages, including neighbour context, are
                # required in this selected new-data qualification sample.
                if not Path(r['crop_source_image']).is_file():continue
            r['qualification_source_parent']=parent['id']
            rows.append(r);chosen+=1
            if chosen==n:break
        if chosen!=n:raise RuntimeError('not enough bound sample images for '+parent['id'])
    target=out/'sample.jsonl';target.write_text(''.join(canonical(r)+'\n' for r in rows))
    return target,len(rows)


def scientific_decision(decision):
    """Retain every scientific field; omit only run identity and observed clock."""
    result=deepcopy(decision);result.pop('run_binding_sha256',None)
    for stage in result.get('stages',[]):
        if stage['stage']=='segmentation':
            orientation=stage['result'].get('frame',{}).get('orientation',{})
            timing=orientation.get('evidence',{}) if isinstance(orientation,dict) else None
            if isinstance(timing,dict):timing.pop('seconds',None)
    return result


def qualify(root,out,n,counts,stratified=False,prefetch_factors=None):
    if type(n) is not int or n<1:raise ValueError('per-parent sample size must be positive')
    if not counts or counts[0]!=1 or len(set(counts))!=len(counts) or any(type(v) is not int or not 1<=v<=256 for v in counts):
        raise ValueError('worker counts must be unique, in 1..256, with serial 1 first')
    if prefetch_factors is None:prefetch_factors=[2]
    if not prefetch_factors or prefetch_factors[0]!=2 or len(set(prefetch_factors))!=len(prefetch_factors) or any(type(f) is not int or not 1<=f<=64 for f in prefetch_factors):
        raise ValueError('prefetch factors must be unique, in 1..64, with default 2 first')
    if any(w*f>MAX_PENDING_OBSERVATIONS for w in counts for f in ([2] if w==1 else prefetch_factors)):
        raise ValueError('qualification worker/prefetch combinations must be at most 4096 pending observations')
    worker_guard();env=environment(root);out.mkdir(parents=True,exist_ok=False)
    atomic_json(out/'environment.json',env)
    runtime_path=out/'native-runtime.json'
    atomic_json(runtime_path,capture(dict(node=env['node']['node'],
        predictor=root/'runtime/rust-target/release/greekocr-frozen-font-predict')) if env else {})
    if env:validate(runtime_path)
    parent,count=sample(root,out,n,True) if stratified else sample(root,out,n)
    metadata=out/'metadata.json';atomic_json(metadata,{})
    baseline=None;timings=[]
    for workers,prefetch in [(w,f) for w in counts for f in ([2] if w==1 else prefetch_factors)]:
        case=f'w{workers}' if prefetch==2 else f'w{workers}_pf{prefetch}'
        config=dict(versions=str(TOOLKIT/'docs/harvest/line_pipeline/tool_versions.json'),metadata=str(metadata),
            predictor=str(root/'runtime/rust-target/release/greekocr-frozen-font-predict'),native_workers=workers,
            native_prefetch_factor=prefetch,
            runtime_manifest=str(runtime_path) if env else None,
            row_timeout_seconds=120,parents=[dict(id='bound-native-qualification',format='canonical',path=str(parent),sha256=file_sha(parent),rows=count)],corrections=[])
        atomic_json(out/f'config_{case}.json',config)
        started=time.monotonic();directory=out/case
        if directory.exists():raise RuntimeError('qualification measurement cache must be fresh')
        summary=run(config,directory,execute=True)
        seconds=time.monotonic()-started
        runtime=json.loads((directory/'runtime.json').read_text())
        if not summary['complete'] or summary['dispositions'].get('INFRA_ERROR'):
            raise RuntimeError('native qualification incomplete or infrastructure failure; inspect '+str(directory))
        if runtime['native_attempts']!=count or any(runtime.get(k) for k in ['cached_measurements','invalid_cache_entries','unavailable','cleanup_errors']):
            raise RuntimeError('qualification requires fresh successful measurement of every sample row')
        decisions=[r for _,r in records(directory/'decisions.jsonl')]
        scientific=[];verdicts=Counter();measured_parents=Counter()
        for d in decisions:
            scientific.append(scientific_decision(d))
            for stage in d.get('stages',[]):
                if stage['stage']=='segmentation':
                    verdicts[stage['result']['verdict']]+=1
                    measured_parents[d['binding']['parent_id']]+=stage['result'].get('availability')!='unavailable'
        if sum(measured_parents.values())!=count or not verdicts['KEEP']:
            raise RuntimeError('native qualification lacks full measurement/positive KEEP evidence')
        if baseline is None:baseline=scientific
        elif scientific!=baseline:raise RuntimeError('parallel execution changed ordered decisions')
        entry=dict(workers=workers,prefetch_factor=prefetch,rows=count,wall_seconds=seconds,rows_per_second=count/seconds,segmentation_verdicts=dict(verdicts),
            dispositions=summary['dispositions'],decision_digest=digest(canonical(scientific)),runtime=runtime)
        timings.append(entry);atomic_json(out/'timings.partial.json',timings);print(canonical(entry),flush=True)
    atomic_json(out/'qualification.json',dict(status='PASS',scope='selected bound native rows, not corpus accuracy or population throughput',
        selection='deterministic SHA priority across each complete parent' if stratified else 'first bound rows per parent',
        sample_sha256=file_sha(parent),sample_rows=count,ordered_decisions_equal=True,segmentation_policy_unchanged=True,timings=timings,
        equality_exclusions=['run_binding_sha256','segmentation result.frame.orientation.evidence.seconds (elapsed diagnostic clock only)'],
        max_measured_speedup=max(timings[0]['wall_seconds']/v['wall_seconds'] for v in timings),environment=env))


def prepare(root,out,workers):
    """Bind every original crop/source and stage a diagnostic (not training) census."""
    worker_guard();env=environment(root);out.mkdir(parents=True,exist_ok=False)
    inventory(root,out/'inventory')
    checked=json.loads((out/'inventory/inventory.json').read_text())
    if checked['source_pages_missing']:raise RuntimeError('source pages missing; inspect inventory')
    metadata={'crops':{}};missing=[]
    with ThreadPoolExecutor(max_workers=16) as pool:
        for parent in inputs(root)[:3]:
            def bind(record):
                path=old_crop(record,root)
                if not path.is_file():return record['id'],None
                return record['id'],dict(path=str(path),sha256=file_sha(path))
            iterator=(r for _,r in records(parent['path']));done=0
            while batch:=list(islice(iterator,1000)):
                for row_id,binding in pool.map(bind,batch):
                    done+=1
                    if binding is None:missing.append(dict(parent_id=parent['id'],id=row_id))
                    else:metadata['crops'][canonical([parent['id'],row_id])]=binding
                atomic_json(out/'progress.json',dict(stage='original_crop_binding',parent=parent['id'],processed=done,missing=len(missing)))
    atomic_json(out/'missing_original_crops.json',missing)
    if missing:raise RuntimeError('original crops missing; no run config issued')
    metadata_path=out/'metadata.json';atomic_json(metadata_path,metadata)
    runtime_path=out/'native-runtime.json'
    atomic_json(runtime_path,capture(dict(node=env['node']['node'],predictor=root/'runtime/rust-target/release/greekocr-frozen-font-predict')))
    validate(runtime_path)
    parents=json.loads((out/'inventory/parents.json').read_text())
    releases=[]
    for tool,parent_id,relative,status in [
        ('polytonic','collection-v2-train','greek-ocr-toolkit-spellcheck/artifacts/sf7_rc1/release_edits_only_A.jsonl','candidate_pre_audit'),
        ('cyrillic','collection-v2-train','greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v3_edits.jsonl','released'),
        ('numerics','collect-v3-W1-20261018-0524','greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_w1.jsonl','released')]:
        path=TOOLKIT.parent/relative
        releases.append(dict(tool=tool,parent_id=parent_id,parent_manifest_sha256=next(p['sha256'] for p in parents if p['id']==parent_id),
            path=str(path),sha256=file_sha(path),status=status))
    config=dict(versions=str(TOOLKIT/'docs/harvest/line_pipeline/tool_versions.json'),metadata=str(metadata_path),runtime_manifest=str(runtime_path),
        predictor=str(root/'runtime/rust-target/release/greekocr-frozen-font-predict'),native_workers=workers,row_timeout_seconds=120,
        parents=parents,corrections=releases)
    atomic_json(out/'config.json',config)
    atomic_json(out/'readiness.json',dict(status='bound diagnostic census inputs; training admission remains evidence-gated',rows=checked['rows'],
        original_crop_bindings=len(metadata['crops']),source_pages_verified=checked['source_pages_verified'],native_workers=workers,
        config_sha256=file_sha(out/'config.json'),metadata_sha256=file_sha(metadata_path),runtime_sha256=file_sha(runtime_path),
        unresolved=['canonical edition identity','new-data split assignment','book/page orthography where source policy is insufficient',
            'full applicable corrective coverage and SF7 release audit'],segmentation_policy_unchanged=True))


def inventory(root,out):
    worker_guard();out.mkdir(parents=True,exist_ok=False)
    asset_map={};books={};parents=[];counts=Counter()
    snapshots=root/'inputs/collect-v3-data/snapshots'
    wanted=dict(line.split()[::-1] for line in (snapshots/'SHA256_20261018_0524.txt').read_text().splitlines())
    for parent in inputs(root):
        actual=file_sha(parent['path'])
        if parent['format']=='collect-v3-features' and actual!=wanted[Path(parent['path']).name]:raise ValueError('frozen snapshot SHA mismatch')
        n=0
        for _,r in records(parent['path']):
            n+=1;counts[parent['id']]+=1
            book=r['doc'] if parent['format']=='collection-v2' else r['page_id'].rsplit('--s',1)[0]
            b=books.setdefault(book,dict(source=r['source'],item=r.get('item'),source_url=r.get('source_url'),rows=0,splits=set(),parents=set()))
            b['rows']+=1;b['splits'].add(r.get('split','unassigned'));b['parents'].add(parent['id'])
            if r.get('crop_source_image'):
                path=r['crop_source_image'];sha=r['crop_source_sha256']
                if path in asset_map and asset_map[path]['sha256']!=sha:raise ValueError('source path has conflicting hashes')
                mapped=canonicalize(r,parent,{})['crop_source_image']
                asset_map[path]=dict(local_path=path,worker_path=mapped,sha256=sha)
        parents.append(dict(parent,sha256=actual,rows=n))
        print(canonical(dict(parent=parent['id'],rows=n,sha256=actual)),flush=True)
    for b in books.values():b['splits']=sorted(b['splits']);b['parents']=sorted(b['parents'])
    missing=[];verified=0
    for asset in asset_map.values():
        path=Path(asset['worker_path'])
        if path.is_file():
            if file_sha(path)!=asset['sha256']:raise ValueError('staged source page hash mismatch')
            verified+=1
        else:missing.append(asset)
    (out/'missing_source_assets.jsonl').write_text(''.join(canonical(v)+'\n' for v in missing))
    atomic_json(out/'parents.json',parents);atomic_json(out/'books_observed.json',books)
    atomic_json(out/'inventory.json',dict(status='PASS inventory; data readiness depends on missing assets and metadata bindings',parents=parents,rows=sum(counts.values()),
        source_pages=len(asset_map),source_pages_verified=verified,source_pages_missing=len(missing),books=len(books),
        complete_correction_coverage=False,full_native_census_executed=False))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['qualify','inventory','prepare','census','census-preflight'])
    p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--per-parent',type=int,default=16);p.add_argument('--workers',type=int,nargs='+',default=[1,4,8]);p.add_argument('--stratified',action='store_true')
    p.add_argument('--prefetch-factors',type=int,nargs='+',default=[2])
    p.add_argument('--config',type=Path);p.add_argument('--retry-errors',action='store_true');p.add_argument('--retry-holds',action='store_true');args=p.parse_args()
    if args.mode=='qualify':qualify(args.root,args.out,args.per_parent,args.workers,args.stratified,args.prefetch_factors)
    elif args.mode=='prepare':prepare(args.root,args.out,args.workers[-1])
    elif args.mode=='inventory':inventory(args.root,args.out)
    else:
        worker_guard();environment(args.root)
        if not args.config:raise ValueError('census requires --config')
        result=run(json.loads(args.config.read_text()),args.out,execute=True,retry_errors=args.retry_errors,retry_holds=args.retry_holds,
                   validate_inputs_only=args.mode=='census-preflight')
        if not result.get('preflight_complete' if args.mode=='census-preflight' else 'complete'):
            raise RuntimeError('incomplete census/preflight; inspect summary')


if __name__=='__main__':main()
