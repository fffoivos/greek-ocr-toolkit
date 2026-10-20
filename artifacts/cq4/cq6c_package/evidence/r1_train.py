"""One R1 arm. Refuses unreceipted extraction; checkpoint/log/predictions each epoch."""
from __future__ import annotations
import argparse
from collections import Counter, OrderedDict
import contextlib
import csv
import json
import math
import os
from pathlib import Path
import platform
import time
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader, Sampler

from scripts.labelfix.clariden.r1_common import (ARMS, HEADS, LETTERS, SEED, compose, rows,
    sha256, verify_receipt, write_json, write_rows)
from scripts.labelfix.clariden.r1_model import MarkReader, flop_estimate


class Shards(Dataset):
    def __init__(self,path,arm,split=None):
        self.path=Path(path);self.arm=arm;self.index=np.load(self.path/'index.npy',allow_pickle=False)
        if split is not None:self.index=self.index[self.index['validation']==(split=='validation')]
        self.cache=OrderedDict();self.view='narrow' if arm=='C' else 'wide'

    def __len__(self):return len(self.index)

    def __getitem__(self,i):
        r=self.index[i];shard=int(r['shard'])
        if shard not in self.cache:
            self.cache[shard]=np.load(self.path/f'shard-{shard:05d}-{self.view}.npy',mmap_mode='r',allow_pickle=False)
            if len(self.cache)>256:self.cache.popitem(last=False)
        # Float conversion/mask creation is vectorised on device, not per sample in workers.
        return np.array(self.cache[shard][r['offset']],copy=True),int(r['letter']),r['target'].astype(np.int64),r['mask'][int(self.arm=='C')].copy(),i


class ArmBatches(Sampler):
    def __init__(self,targets,batch_size,arm,seed):
        self.y=targets;self.bs=batch_size;self.arm=arm;self.seed=seed
        none=~targets.any(axis=1);self.none=np.flatnonzero(none);self.marked=np.flatnonzero(~none)
        self.natural=float(none.mean())
        self.pools=[np.flatnonzero(targets[:,h]==v) for h,choices in enumerate(HEADS.values()) for v in range(1,len(choices))]
        self.pools=[p for p in self.pools if len(p)]
        cs=[compose(y) for y in targets];counts=Counter(cs)
        self.rare=np.flatnonzero([bool(targets[i].any()) and (np.count_nonzero(targets[i])>=2 or counts[c]<1000) for i,c in enumerate(cs)])
        if arm!='D' and (not len(self.none) or not len(self.marked) or not len(self.rare)):
            raise ValueError('balancing requires none, marked and rare/compound samples')

    def __len__(self):return math.ceil(len(self.y)/self.bs)

    def __iter__(self):
        rng=np.random.default_rng(self.seed)
        if self.arm=='D':
            order=rng.permutation(len(self.y))
            for i in range(0,len(order),self.bs):yield order[i:i+self.bs].tolist()
            return
        fraction=self.natural if self.arm=='E' else .4
        for i in range(len(self)):
            n=min(self.bs,len(self.y)-i*self.bs)
            nnone=min(n-math.ceil(.05*n),round(fraction*n)); nrare=math.ceil(.05*n)
            batch=rng.choice(self.none,nnone,replace=True).tolist()+rng.choice(self.rare,nrare,replace=True).tolist()
            # Equal head/value allocation; each eligible positive head has a pool.
            for p in rng.integers(len(self.pools),size=n-len(batch)):
                batch.append(int(rng.choice(self.pools[p])))
            rng.shuffle(batch);yield batch


def batch_to_device(batch,device):
    grey,letter,y,mask,ids=batch
    grey=grey.to(device,non_blocking=True).float().div_(255)
    mask=mask.to(device,non_blocking=True)
    xx=torch.arange(128,device=device,dtype=torch.float32)[None,:]+.5
    span=((xx>=mask[:,0,None]) & (xx<mask[:,1,None])).float()[:,None,:].expand(-1,64,-1)
    x=torch.stack((grey,span),dim=1).contiguous(memory_format=torch.channels_last)
    return x,letter.to(device,non_blocking=True),y.to(device,non_blocking=True),ids


def loader(ds,bs,workers,sampler=None):
    kw=dict(num_workers=workers,pin_memory=torch.cuda.is_available(),persistent_workers=workers>0)
    if sampler is not None:return DataLoader(ds,batch_sampler=sampler,**kw)
    return DataLoader(ds,batch_size=bs,shuffle=False,**kw)


def class_weights(y,arm,device):
    weights=[]
    for h,choices in enumerate(HEADS.values()):
        counts=np.bincount(y[:,h],minlength=len(choices))
        w=np.sqrt(max(1,len(y))/np.maximum(counts,1));w=np.minimum(w,10);w/=w.mean()
        weights.append(torch.tensor(np.ones(len(choices)) if arm=='D' else w,dtype=torch.float32,device=device))
    return weights


def loss_fn(logits,y,weights=None):
    return sum(nn.functional.cross_entropy(z,y[:,h],weight=weights[h] if weights else None) for h,z in enumerate(logits))


def predict(model,dataset,out,device,bs,workers,checkpoint,arm):
    model.eval(); metadata={l['line']:l for l in rows(dataset.path/'lines.jsonl.gz')}
    predictions=[]
    with torch.no_grad():
        for batch in loader(dataset,bs,workers):
            x,letter,_,ids=batch_to_device(batch,device)
            with torch.autocast('cuda',dtype=torch.bfloat16) if device.type=='cuda' else contextlib.nullcontext():
                logits=model(x,letter)
            prob=[z.float().softmax(1).cpu() for z in logits]
            values=torch.stack([z.argmax(1) for z in prob],1).tolist()
            for batch_i,(i,values_i) in enumerate(zip(ids.tolist(),values)):
                r=dataset.index[i];line=metadata[int(r['line'])]
                predictions.append(dict(sample_id=f'{line["id"]}:{int(r["start"])}',line_id=line['id'],
                    start=int(r['start']),base=LETTERS[int(r['letter'])],factors=values_i,cls=compose(values_i),
                    mark_probabilities={choices[v]:float(prob[j][batch_i,v]) for j,(choices,v) in enumerate(zip(HEADS.values(),values_i)) if v},
                    support_provenance='reader_head_softmax_uncalibrated'))
    write_rows(out,predictions)
    write_json(out.with_suffix('.receipt.json'),dict(schema='r1-predictions-v1',arm=arm,samples=len(predictions),
        prediction_sha256=sha256(out),checkpoint_sha256=sha256(checkpoint),
        extraction_receipt_sha256=sha256(dataset.path/'extraction_receipt.json'),
        input_index_sha256=sha256(dataset.path/'index.npy'),ctc_forward_passes=0))


def train(data,heldout,out,arm,device='cpu',epochs=15,batch_size=512,workers=4,steps=None,threads=8,
          owner_extra=None,source_commit='TRACK_LEAD_FILL_SOURCE_COMMIT',seed=SEED,sampler_seed=SEED,
          manifest=None,inventory=None,native_pool=None):
    torch.set_num_threads(threads);torch.manual_seed(seed);np.random.seed(seed)
    receipt=verify_receipt(data); verify_receipt(heldout)
    if owner_extra:verify_receipt(owner_extra)
    if steps is not None and steps<1:raise ValueError('steps must be positive')
    if receipt['mode']!='c1' or not receipt['disjointness']:raise ValueError('C1 disjointness receipt required')
    device=torch.device(device);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    if device.type=='cuda':torch.cuda.set_device(device);torch.backends.cudnn.benchmark=True
    trainset=Shards(data,arm,'train');val=Shards(data,arm,'validation')
    if not len(trainset) or not len(val):raise ValueError('empty document train/validation split')
    old_targets=trainset.index['target']
    if manifest:
        from scripts.labelfix.clariden.r2_manifest import ManifestPool
        if inventory is None: raise ValueError('manifest requires crop inventory')
        trainset=ManifestPool(trainset,manifest,inventory,lambda p:Shards(p,arm,'train'),native_pool=native_pool)
        if not len(trainset): raise ValueError('empty manifest pool')
    model=MarkReader(ARMS[arm]['embedding']).to(device,memory_format=torch.channels_last)
    recipe=dict(ARMS[arm],epochs=epochs,batch_size=batch_size,optimizer='AdamW',lr=.001,weight_decay=.01,
        seed=seed,sampler_seed=sampler_seed,steps_limit=steps,precision='bf16' if device.type=='cuda' else 'fp32 CPU mock',
        validation='natural distribution, unweighted sum of four cross entropies',**flop_estimate(MarkReader(ARMS[arm]['embedding'])))
    bound=dict(schema='r1-run-binding-v1',source_commit=source_commit,parameters=recipe,
        runtime=dict(torch=torch.__version__,python=platform.python_version(),device=str(device),
                     gpu=torch.cuda.get_device_name(device) if device.type=='cuda' else None,
                     job_id=os.environ.get('SLURM_JOB_ID'),cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES')),
        file_sha256={str(p):sha256(p) for p in sorted(Path('scripts/labelfix/clariden').glob('r1_*')) if p.is_file()},
        heldout_shard_sha256=verify_receipt(heldout)['sha256'],
        heldout_extraction_receipt_sha256=sha256(Path(heldout)/'extraction_receipt.json'),
        extraction_receipt_sha256=sha256(Path(data)/'extraction_receipt.json'),shard_sha256=receipt['sha256'])
    if manifest: bound['manifest']=trainset.binding
    write_json(out/'run_binding.json',bound)
    write_json(out/'data_provenance.json',dict(schema_version=1,source='C1 only; exact NFD agreement labels',
        document_split=receipt['document_split'],disjointness=receipt['disjointness'],
        training_samples=len(trainset),validation_samples=len(val),
        extraction_receipt_sha256=bound['extraction_receipt_sha256'],shard_sha256=receipt['sha256'],
        heldout_inference_only=True,recipe=recipe))
    opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.01)
    weights=class_weights(old_targets,arm,device)
    weight_cpu=[w.detach().cpu().numpy() for w in weights]
    provenance_array=np.asarray(trainset.provenances,dtype=object) if manifest else None
    best=float('inf'); total_steps=0; nforward=0;train_seconds=0;load_seconds=0
    train_loader=None
    with (out/'train_log.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['epoch','steps','train_loss','validation_loss','best','samples','train_seconds','samples_per_second','loader_wait_seconds'])
        writer.writeheader();f.flush()
        for epoch in range(1,epochs+1):
            model.train(); batch_sampler=ArmBatches(trainset.index['target'],batch_size,arm,sampler_seed+epoch)
            if train_loader is None:train_loader=loader(trainset,batch_size,workers,batch_sampler)
            else:train_loader.batch_sampler.seed=sampler_seed+epoch
            exposure={p:dict(draws=0,heads={h:dict(draws=0,effective_loss_mass=0.) for h in HEADS}) for p in ('old','native_print','pseudo','override')}
            loss_sum=0.;count=0;epoch_started=time.monotonic();epoch_load=0.;tic=time.monotonic()
            for batch in train_loader:
                epoch_load+=time.monotonic()-tic
                x,letter,y,ids=batch_to_device(batch,device);opt.zero_grad(set_to_none=True)
                with torch.autocast('cuda',dtype=torch.bfloat16) if device.type=='cuda' else contextlib.nullcontext():
                    logits=model(x,letter)
                    if manifest and not trainset.identity:
                        pw=torch.as_tensor(trainset.loss_weights[ids.numpy()],device=device)
                        loss=sum((nn.functional.cross_entropy(z,y[:,h],weight=weights[h],reduction='none')*pw).sum()/weights[h][y[:,h]].sum() for h,z in enumerate(logits))
                    else: loss=loss_fn(logits,y,weights)
                # Aggregate realised exposure on CPU; never synchronize per GPU sample.
                batch_ids=ids.numpy(); batch_y=batch[2].numpy()
                provs=provenance_array[batch_ids] if manifest else np.full(len(batch_ids),'old')
                pweights=trainset.loss_weights[batch_ids] if manifest else np.ones(len(batch_ids))
                for prov in exposure:
                    select=provs==prov; n=int(select.sum());exposure[prov]['draws']+=n
                    for h,name in enumerate(HEADS):
                        cell=exposure[prov]['heads'][name];cell['draws']+=n
                        cell['effective_loss_mass']+=float((weight_cpu[h][batch_y[select,h]]*pweights[select]).sum())
                loss.backward();opt.step()
                loss_sum+=float(loss.detach())*len(x);count+=len(x);total_steps+=1;tic=time.monotonic()
                if steps is not None and total_steps>=steps:break
            if device.type=='cuda':torch.cuda.synchronize()
            elapsed=time.monotonic()-epoch_started;nforward+=count;train_seconds+=elapsed;load_seconds+=epoch_load
            model.eval();vsum=0.;vn=0
            with torch.no_grad():
                for batch in loader(val,batch_size,workers):
                    x,letter,y,_=batch_to_device(batch,device)
                    with torch.autocast('cuda',dtype=torch.bfloat16) if device.type=='cuda' else contextlib.nullcontext():
                        vloss=loss_fn(model(x,letter),y)
                    vsum+=float(vloss)*len(x);vn+=len(x)
            vloss=vsum/vn
            if not math.isfinite(vloss):raise ValueError('non-finite validation loss')
            improved=vloss<best
            if improved:
                best=vloss
                temp=out/'best.pt.tmp'
                torch.save(dict(model=model.state_dict(),epoch=epoch,validation_loss=best,arm=arm,recipe=recipe,
                                run_binding_sha256=sha256(out/'run_binding.json')),temp)
                temp.replace(out/'best.pt')
            row=dict(epoch=epoch,steps=total_steps,train_loss=loss_sum/count,validation_loss=vloss,best=best,
                     samples=count,train_seconds=elapsed,samples_per_second=count/elapsed,loader_wait_seconds=epoch_load)
            unique=Counter(trainset.provenances) if manifest else Counter(old=len(trainset))
            write_json(out/f'exposure_epoch_{epoch:02d}.json',dict(class_weight_source='frozen old training extraction',
                class_weights={h:w.tolist() for h,w in zip(HEADS,weight_cpu)},unique_counts=dict(unique),
                unique_per_head={p:{h:unique[p] for h in HEADS} for p in exposure},provenance=exposure))
            writer.writerow(row);f.flush();os.fsync(f.fileno());print('TRAIN '+arm+' '+json.dumps(row),flush=True)
            # Predictions accompany every improved best, so timeout leaves a usable result.
            if improved:
                predict(model,Shards(heldout,arm),out/'heldout_predictions.jsonl',device,batch_size,workers,out/'best.pt',arm)
                if owner_extra:predict(model,Shards(owner_extra,arm),out/'owner_predictions.jsonl',device,batch_size,workers,out/'best.pt',arm)
            if steps is not None and total_steps>=steps:break
    result=dict(recipe,arm=arm,steps=total_steps,best_validation_loss=best,
                forward_backward_samples_per_second=nforward/train_seconds,loader_wait_seconds=load_seconds,
                total_training_samples=nforward,training_seconds=train_seconds)
    # Keep requested epochs distinct from completed epochs in timeout/readout accounting.
    result['completed_epochs']=epoch
    result['bounded_mock']=steps is not None
    if manifest:
        result['manifest']=trainset.binding
    write_json(out/'training_receipt.json',result)
    write_json(out/'DONE',dict(arm=arm,completed_epochs=epoch,steps=total_steps,best_sha256=sha256(out/'best.pt'),
               predictions_sha256=sha256(out/'heldout_predictions.jsonl')))
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ('data','heldout','out'):ap.add_argument('--'+n,type=Path,required=True)
    ap.add_argument('--owner-extra',type=Path);ap.add_argument('--arm',choices=list(ARMS),required=True)
    ap.add_argument('--device',default='cuda');ap.add_argument('--epochs',type=int,default=15)
    ap.add_argument('--batch-size',type=int,default=512);ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--steps',type=int);ap.add_argument('--threads',type=int,default=8)
    ap.add_argument('--source-commit',default='TRACK_LEAD_FILL_SOURCE_COMMIT')
    ap.add_argument('--seed',type=int,default=SEED);ap.add_argument('--sampler-seed',type=int,default=SEED)
    ap.add_argument('--manifest',type=Path);ap.add_argument('--inventory',type=Path);ap.add_argument('--native-pool',type=Path)
    a=ap.parse_args();train(**vars(a))


if __name__=='__main__':main()
