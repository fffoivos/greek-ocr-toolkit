"""Re-release L1-v0 saved evidence under SF2. No detector or model execution.

Missing gate inputs cause HOLD. Old files are never written. A complete input
run, exact selection and all shard hashes must verify before release.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from greekocr.labelfix.release_gate import policy_binding
from scripts.labelfix.clariden.l1_common import release, rows, sha256, write_json


def recompose(input_run, selection, binding_dir, source, out, ensemble_run=None, workers=1):
    base,out=Path(input_run),Path(out)
    if out.resolve()==base.resolve() or base.resolve() in out.resolve().parents:
        raise ValueError('L1r output must be separate from historical run')
    run=json.loads((base/'run_receipt.json').read_text())
    if not run.get('complete'):raise ValueError('incomplete historical run')
    paths=sorted((base/'combined').glob('shard-*-combined.jsonl.gz'))
    if not paths:raise ValueError('no saved combined shards')
    inputs={str(selection):sha256(selection),str(source):sha256(source)}
    inputs[str(base/'run_receipt.json')]=sha256(base/'run_receipt.json')
    binding_path=Path(binding_dir)/'binding.json'
    if sha256(binding_path)!=run['binding_sha256']:raise ValueError('historical binding changed')
    inputs[str(binding_path)]=sha256(binding_path)
    for name,digest in run['step_receipts'].items():
        if sha256(base/name)!=digest:raise ValueError('historical step receipt changed: '+name)
        inputs[str(base/name)]=digest
    ids=[];missing=Counter();apostrophes=0
    for path in paths:
        receipt=json.loads(path.with_name(path.name.replace('-combined.jsonl.gz','-receipt.json')).read_text())
        if not receipt.get('complete') or receipt['output_sha256']!=sha256(path):raise ValueError('invalid shard '+str(path))
        inputs[str(path)]=sha256(path)
        for r in rows(path):
            ids.append(r['id'])
            for key in ('detector','r1_predictions','coverage','recogniser_text'):
                if key not in r:raise ValueError('missing line input '+key)
            for c in r['coverage']:
                for key in ('scored','evidence_state','uncertainty'):
                    if key not in c:missing['r1_'+key]+=1
            for s in r['detector']['slots']:
                if 'segmentation_uncertain' not in s:missing['detector_segmentation_state']+=1
                for k in ('clipped_top','clipped_bottom'):
                    if k not in s.get('evidence',{}):missing[k]+=1
                if s.get('apostrophe') and not s.get('evidence',{}).get('apostrophes'):apostrophes+=1
    selected=list(rows(selection))
    if len(ids)!=len(set(ids)) or set(ids)!={r['id'] for r in selected}:raise ValueError('runtime/selection mismatch')
    for v in ('presence','full'):
        manifest=json.loads((base/'release'/f'release_{v}.json').read_text())
        inputs[str(base/'release'/f'release_{v}.json')]=sha256(base/'release'/f'release_{v}.json')
        if manifest['source_sha256']!=sha256(source) or manifest['selection_sha256']!=sha256(selection):raise ValueError('source/selection changed')
        for name,key in [('overlay','overlay_sha256'),('kept_line_ids','kept_line_ids_sha256')]:
            if sha256(base/'release'/manifest[name])!=manifest[key]:raise ValueError('historical release hash mismatch')
            inputs[str(base/'release'/manifest[name])]=manifest[key]
        control=json.loads((base/'release'/f'release_ctrl_subset_{v}.json').read_text())
        if sha256(base/'release'/control['labels_file'])!=control['labels_sha256']:raise ValueError('historical control changed')
        inputs[str(base/'release'/control['labels_file'])]=control['labels_sha256']
    if missing:raise ValueError('saved evidence incomplete; regenerate missing fields: '+str(dict(missing)))
    runtime_paths=paths;ensemble=None
    if ensemble_run is not None:
        ensemble_run=Path(ensemble_run)
        ep=ensemble_run/'r1e_receipt.json';ensemble=json.loads(ep.read_text())
        if not ensemble.get('complete') or ensemble['historical_run_receipt_sha256']!=sha256(base/'run_receipt.json'):
            raise ValueError('ensemble not bound to completed historical run')
        if ensemble['selection_sha256']!=sha256(selection):raise ValueError('ensemble selection changed')
        inputs[str(ep)]=sha256(ep);runtime_paths=[]
        for entry in ensemble['shards']:
            rp=ensemble_run/entry['receipt'];sr=json.loads(rp.read_text())
            if sha256(rp)!=entry['receipt_sha256'] or not sr['complete']:raise ValueError('ensemble shard receipt changed')
            p=ensemble_run/sr['output']
            if sha256(p)!=sr['output_sha256']:raise ValueError('ensemble shard changed')
            inputs[str(rp)]=sha256(rp);inputs[str(p)]=sha256(p);runtime_paths.append(p)
        if len(runtime_paths)!=len(paths):raise ValueError('ensemble shards missing')
    out.mkdir(parents=True,exist_ok=False)
    binding=json.loads(binding_path.read_text())
    policy=policy_binding();binding['historical_policy_sha256']=binding['policy_sha256'];binding['policy_sha256']=policy['sha256']
    binding['code_commit']='uncommitted-SF2-source-bound'
    binding.update(policy_binding=policy,code_sha256=policy['sources'])
    if ensemble is not None:
        binding.update(checkpoint_sha256=ensemble['checkpoint_sha256'],code_commit='e48e06e8+L1E-source-bound',
                       code_sha256=ensemble['code_sha256'])
    inp=json.loads((base/'input_receipt.json').read_text())
    variants=('presence','full','ensemble_ab') if ensemble is not None else ('presence','full')
    counts=release(selection,runtime_paths,out/'release',binding,source,inp,variants,workers)
    changes={}
    for v in ('presence','full'):
        old={r['line_id']:r for r in rows(base/'release'/f'overlay_{v}.jsonl.gz')}
        delta=[]
        for r in rows(out/'release'/f'overlay_{v}.jsonl.gz'):
            a=old[r['line_id']]
            if (a['status'],a.get('label'))!=(r['status'],r.get('label')):
                delta.append(dict(line_id=r['line_id'],before=a['status'],after=r['status'],
                    reasons=sorted({s['detail'] for s in r['hold_slots']})))
        write_json(out/f'decision_changes_{v}.json',delta)
        changes[v]=dict(changed=len(delta),reasons=dict(Counter(z for d in delta for z in d['reasons'])))
    if any(sha256(Path(p))!=h for p,h in inputs.items()):raise ValueError('input changed during recomposition')
    receipt=dict(schema='l1r-recomposition-v1',complete=True,policy=policy,inputs=inputs,
        historical_run=str(base),counts=counts,changes=changes,evidence_sufficient=True,
        historical_apostrophe_boxes_missing=apostrophes,network=False,detector_runs=0,r1_runs=0,
        ensemble_receipt_sha256=inputs.get(str(Path(ensemble_run)/'r1e_receipt.json')) if ensemble_run else None,
        outputs={str(p.relative_to(out)):sha256(p) for p in sorted(out.rglob('*')) if p.is_file()})
    write_json(out/'receipt.json',receipt)
    return receipt


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ('input-run','selection','binding-dir','source','out'):ap.add_argument('--'+flag,type=Path,required=True)
    ap.add_argument('--ensemble-run',type=Path);ap.add_argument('--workers',type=int,default=1)
    a=ap.parse_args()
    r=recompose(a.input_run,a.selection,a.binding_dir,a.source,a.out,a.ensemble_run,a.workers)
    print(json.dumps({k:v for k,v in r.items() if k not in ('inputs','outputs')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
