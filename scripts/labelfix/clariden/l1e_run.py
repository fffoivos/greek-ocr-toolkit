"""L1E exact CPU-mock/GPU-job path. No scheduler submission capability."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import time
import numpy as np
import torch
from scripts.labelfix.clariden.l1_infer import predictions
from scripts.labelfix.clariden.r1_model import MarkReader
from scripts.labelfix.clariden.r1_common import ARMS, LETTERS, rows, sha256, write_json, write_rows
from scripts.labelfix.clariden.l1e_windows import audit,checked,shard_inputs
from greekocr.labelfix.release_gate import policy_binding, compose_runtime, MODES
from greekocr.labelfix.ctc_align import recognition_fields


def load_reader(checkpoint,arm,digest,device):
    checked(checkpoint,digest)
    ck=torch.load(checkpoint,map_location='cpu',weights_only=True)
    if ck['arm']!=arm:raise ValueError('checkpoint arm mismatch: '+arm)
    model=MarkReader(embedding=ARMS[arm]['embedding']).to(device,memory_format=torch.channels_last)
    model.load_state_dict(ck['model'],strict=True);model.eval()
    return model


def decision_record(runtime):
    """Comparable policy outcomes; probabilities are not acceptance thresholds."""
    return {m:dict(text=(r:=compose_runtime(runtime,m))['text'],hold_slots=r['hold_slots'],
        slots=[{k:s.get(k) for k in ('start','base','parts','label_status','hold_reasons','apostrophe')} for s in r['slots']]) for m in MODES}


def infer(historical,window_audit,checkpoints,out,code_hashes,device='cuda:0',batch_size=512):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    torch.set_num_threads(4 if device=='cpu' else 8)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    models={a:load_reader(p['path'],a,p['sha256'],device) for a,p in checkpoints.items() if a in ('B','E')}
    checked(checkpoints['A']['path'],checkpoints['A']['sha256'])
    ck=torch.load(checkpoints['A']['path'],map_location='cpu',weights_only=True)
    if ck['arm']!='A':raise ValueError('historical A checkpoint arm mismatch')
    historical=Path(historical);top=json.loads((historical/'run_receipt.json').read_text())
    if not top['complete']:raise ValueError('historical run incomplete')
    result=[]
    checkpoint_hashes={a:p['sha256'] for a,p in checkpoints.items()}
    for e in window_audit['entries']:
        number=e['shard'];paths=shard_inputs(historical/'detector',number)
        old=historical/'combined'/f'shard-{number:05d}-combined.jsonl.gz'
        op=old.with_name(old.name.replace('-combined.jsonl.gz','-receipt.json'))
        checked(op,top['step_receipts'][str(op.relative_to(historical))])
        old_receipt=json.loads(op.read_text());checked(old,old_receipt['output_sha256'])
        dest=out/old.name;rp=out/f'shard-{number:05d}-receipt.json'
        inputs=dict(historical_combined_sha256=sha256(old),window_receipt_sha256=e['receipt_sha256'],
                    checkpoint_sha256=checkpoint_hashes,code_sha256=code_hashes)
        if rp.exists():
            sr=json.loads(rp.read_text())
            if not sr.get('complete') or sr['inputs']!=inputs:raise ValueError('cannot reuse stale ensemble shard')
            checked(dest,sr['output_sha256'])
        else:
            tick=time.monotonic();samples=json.loads(paths['samples'].read_text())
            windows=np.load(e['wide'],mmap_mode='r',allow_pickle=False)
            records=list(rows(old));detector=list(rows(paths['detector']))
            if len(records)!=e['lines'] or [r['id'] for r in records]!=[r['id'] for r in detector]:raise ValueError('A/detector line mismatch')
            expected=[set() for _ in records]
            for s in samples:expected[s['line']].add((s['start'],LETTERS[s['letter']]))
            for i,r in enumerate(records):
                if r['detector']!=detector[i]['detector'] or r['coverage']!=detector[i]['coverage']:raise ValueError('A/detector evidence differs')
                actual=[(p['start'],p['base']) for p in r['r1_predictions']]
                if len(actual)!=len(set(actual)) or set(actual)!=expected[i]:raise ValueError('stored windows differ from A prediction slots')
            peer={a:predictions(m,samples,windows,device,batch_size) for a,m in models.items()}
            byline={a:[[] for _ in records] for a in models}
            for a in models:
                if len(peer[a])!=len(samples):raise ValueError('peer prediction count')
                for sample,p in zip(samples,peer[a]):byline[a][sample['line']].append(p)
            combined=[]
            for i,r in enumerate(records):
                rr={k:v for k,v in r.items() if k!='modes'}
                rr.update(recognition_fields(r))
                rr.update(peer_predictions={a:byline[a][i] for a in models},peer_coverage={a:r['coverage'] for a in models})
                combined.append(rr)
            partial=dest.with_name(dest.name.replace('.jsonl.gz','.partial.jsonl.gz'))
            write_rows(partial,combined);partial.replace(dest)
            sr=dict(schema='l1e-inference-shard-v1',complete=True,shard=number,lines=len(records),samples=len(samples),
                inputs=inputs,output=dest.name,output_sha256=sha256(dest),elapsed_seconds=time.monotonic()-tick)
            write_json(rp,sr)
        result.append(dict(receipt=rp.name,receipt_sha256=sha256(rp),lines=sr['lines'],samples=sr['samples']))
        print(f'L1E_SHARD {number} lines={sr["lines"]} seconds={sr["elapsed_seconds"]:.3f}',flush=True)
    receipt=dict(schema='l1e-inference-v1',complete=True,device=device,precision='fp32; TF32 off; no autocast',
        historical_run_receipt_sha256=sha256(historical/'run_receipt.json'),selection_sha256=window_audit['selection_sha256'],
        checkpoint_sha256=checkpoint_hashes,code_sha256=code_hashes,shards=result,
        lines=sum(r['lines'] for r in result),samples=sum(r['samples'] for r in result),elapsed_seconds=time.monotonic()-started)
    write_json(out/'r1e_receipt.json',receipt)
    return receipt


def run(config,out,*,mock=False):
    config=Path(config);cfg=json.loads(config.read_text());out=Path(out)
    historical=Path(cfg['historical_run']).resolve()
    if out.resolve()==historical or historical in out.resolve().parents:raise ValueError('L1-v0 is immutable; choose a separate output')
    out.mkdir(parents=True,exist_ok=True)
    if mock:
        if cfg['lines']>200 or not cfg.get('verification_only'):raise ValueError('mock must be <=200 verification-only lines')
        device='cpu'
    else:
        if not os.environ.get('SLURM_JOB_ID') or not torch.cuda.is_available():raise ValueError('GPU allocation required')
        device='cuda:0'
    started=time.monotonic();checked(cfg['historical_run']+'/run_receipt.json',cfg['historical_run_receipt_sha256'])
    original_binding=json.loads((Path(cfg['binding_dir'])/'binding.json').read_text())
    if cfg['checkpoints']['A']['sha256']!=original_binding['r1_sha256']:raise ValueError('A checkpoint differs from historical binding')
    for name,digest in cfg['unchanged_l1_code_sha256'].items():checked(name,digest)
    for name,digest in cfg['code_sha256'].items():checked(name,digest)
    wr=audit(Path(cfg['historical_run'])/'detector',cfg['selection'],out/'windows_receipt.json',workers=1 if mock else 16,
        repair=True,binding_dir=cfg['binding_dir'],crop_root=cfg.get('crop_root'),layout=cfg.get('layout','e3'))
    if wr['lines']!=cfg['lines']:raise ValueError('unexpected line population')
    ir=infer(cfg['historical_run'],wr,cfg['checkpoints'],out/'inference',cfg['code_sha256'],device,64 if mock else 512)
    if mock:
        expected={r['id']:r['decisions'] for r in rows(cfg['expected_decisions'])}
        actual={r['id']:decision_record(r) for p in sorted((out/'inference').glob('*-combined.jsonl.gz')) for r in rows(p)}
        differences=[i for i in expected if actual.get(i)!=expected[i]]
        pr=dict(verification_only=True,lines=len(actual),exact=len(expected)-len(differences),expected=len(expected),
            differences=differences,expected_sha256=sha256(cfg['expected_decisions']))
        write_json(out/'parity_receipt.json',pr)
        if differences or set(actual)!=set(expected):raise ValueError('held-out decision parity failed')
    from scripts.labelfix.clariden.l1r_recompose import recompose
    rr=recompose(cfg['historical_run'],cfg['selection'],cfg['binding_dir'],cfg['source'],out/'recomposition',
        out/'inference',workers=1 if mock else 16)
    result=dict(schema='l1e-run-v1',complete=True,mock=mock,verification_only=mock,lines=cfg['lines'],
        config_sha256=sha256(config),policy=policy_binding(),window_audit_sha256=sha256(out/'windows_receipt.json'),
        inference_receipt_sha256=sha256(out/'inference/r1e_receipt.json'),
        recomposition_receipt_sha256=sha256(out/'recomposition/receipt.json'),elapsed_seconds=time.monotonic()-started,
        checkpoints=ir['checkpoint_sha256'],counts=rr['counts'],original_labels_unchanged=True)
    write_json(out/'run_receipt.json',result)
    print('L1E_DONE '+json.dumps(result,ensure_ascii=False),flush=True)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mock',action='store_true')
    a=ap.parse_args();run(a.config,a.out,mock=a.mock)


if __name__=='__main__':main()
