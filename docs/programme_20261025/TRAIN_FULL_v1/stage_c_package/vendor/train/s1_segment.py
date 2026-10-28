"""Atomic, optimizer-boundary S1 continuation, independent of allocation identity."""
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import time


class Segment:
    def __init__(self, args, trainer, model, opt, sched, receipt):
        self.args,self.t,self.model,self.opt,self.sched=args,trainer,model,opt,sched
        self.path=Path(args.out_dir)/'segment.pt'
        self.requested=False
        self.previous=signal.signal(signal.SIGTERM,self.request_stop)
        self.started=time.monotonic()
        self.last_save=0
        self.saved=None
        self.trace=[]
        self.chain='0'*64
        self.draws=0
        self.binding={k:v for k,v in vars(args).items() if k not in ('out_dir','resume')}
        self.code_sha=trainer.sha256_file(__file__)
        self.trainer_sha=trainer.sha256_file(trainer.__file__)
        self.receipt=receipt
        if self.path.exists():
            ck=trainer.torch.load(self.path,map_location='cpu',weights_only=False)
            if (ck.get('state_sha256')!=trainer.checkpoint_state_sha256(ck)
                or ck.get('binding')!=self.binding or ck.get('segment_code_sha256')!=self.code_sha
                or ck.get('trainer_sha256')!=self.trainer_sha):
                raise trainer.MixError('S1 segment state/config/code mismatch')
            for key in ('mix_sha256','mix','resolved_mix','recipe_sha256s','training_schedule','validation','transfer'):
                if ck['receipt'].get(key)!=receipt.get(key):
                    raise trainer.MixError('S1 segment provenance mismatch: '+key)
            horizons=receipt['training_schedule']['epoch_batches']
            if (not 1<=ck['epoch']<=args.epochs+1 or ck['batch_position']<0
                or type(ck.get('iterator_created')) is not bool
                or ck['iterator_created'] != (ck['batch_position'] > 0)
                or len(ck['losses'])!=ck['batch_position']
                or ck['global_step']!=sum(horizons[:ck['epoch']-1])+ck['batch_position']
                or ck['global_step']!=ck['sched']['last_epoch']):
                raise trainer.MixError('S1 segment cursor mismatch')
            model.load_state_dict(ck['model'],strict=True)
            opt.load_state_dict(trainer.clone_state_tensors(ck['opt']))
            sched.load_state_dict(trainer.clone_state_tensors(ck['sched']))
            # Roll back ancillary epoch artifacts to the atomic segment commit,
            # including a kill between CSV/best.pt/last.pt and segment publication.
            for digest in ck['artifacts'].values():
                if digest and trainer.sha256_file(self.path.parent/'segment_artifacts'/digest)!=digest:
                    raise trainer.MixError('S1 segment artifact hash mismatch')
            for name,digest in ck['artifacts'].items():
                dest=self.path.parent/name
                if digest is None:
                    dest.unlink(missing_ok=True)
                else:
                    source=self.path.parent/'segment_artifacts'/digest
                    if trainer.sha256_file(source)!=digest:raise trainer.MixError('S1 segment artifact hash mismatch')
                    tmp=dest.with_suffix(dest.suffix+'.rollback')
                    shutil.copyfile(source,tmp);tmp.replace(dest)
            self.saved=ck
            self.trace=ck['trace'];self.chain=ck['draw_chain'];self.draws=ck['draw_position']
            self.restore_rng(ck['rng'])

    def request_stop(self,*_):
        self.requested=True

    def rng(self):
        t=self.t
        return dict(torch=t.torch.get_rng_state(),numpy=t.np.random.get_state(),python=t.random.getstate(),
                    cuda=t.torch.cuda.get_rng_state_all() if t.torch.cuda.is_available() else None)

    def restore_rng(self,rng):
        t=self.t
        t.torch.set_rng_state(rng['torch'].cpu());t.np.random.set_state(rng['numpy']);t.random.setstate(rng['python'])
        if rng['cuda'] is not None:t.torch.cuda.set_rng_state_all(rng['cuda'])

    def iterator(self,loader,epoch,cursor):
        iterator=iter(loader)
        if self.saved and epoch==self.saved['epoch']:
            for _ in range(cursor):next(iterator)
            if self.saved['iterator_created']:
                self.restore_rng(self.saved['rng'])
        return iterator

    def save(self,epoch,position,step,best,bad,losses,skipped,health,receipt,batch_plan_sha):
        t=self.t
        artifacts={}
        store=self.path.parent/'segment_artifacts';store.mkdir(parents=True,exist_ok=True)
        for name in ('best.pt','last.pt','best.safetensors','last.safetensors','checkpoint_meta.json','train_log.csv'):
            source=self.path.parent/name
            digest=t.sha256_file(source) if source.exists() else None
            artifacts[name]=digest
            if digest is not None and not (store/digest).exists():
                tmp=store/(digest+'.tmp');shutil.copyfile(source,tmp);tmp.replace(store/digest)
        ck=dict(artifacts=artifacts,state_hash_version=2,binding=self.binding,segment_code_sha256=self.code_sha,
            trainer_sha256=self.trainer_sha,model=self.model.state_dict(),opt=self.opt.state_dict(),
            sched=self.sched.state_dict(),rng=self.rng(),epoch=epoch,batch_position=position,
            iterator_created=position>0,
            global_step=step,best=best,bad_epochs=bad,losses=losses,skipped=skipped,
            health={**health.__dict__,'rare_ids':sorted(health.rare_ids)},receipt=copy.deepcopy(receipt),trace=self.trace,
            draw_chain=self.chain,draw_position=self.draws,batch_plan_sha256=batch_plan_sha)
        ck['state_sha256']=t.checkpoint_state_sha256(ck)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        candidate=self.path.with_suffix('.pt.tmp')
        with candidate.open('wb') as stream:
            t.torch.save(ck,stream);stream.flush();os.fsync(stream.fileno())
        candidate.replace(self.path)
        # Checkpoint is authoritative; separate trace is a reviewable witness.
        (self.path.parent/'SEGMENT_TRACE.json').write_text(json.dumps(dict(trace=self.trace,
            draw_chain=self.chain,draw_position=self.draws,global_step=step,epoch=epoch))+'\n')
        self.last_save=step

    def note(self,epoch,position,indices,rows,loss,step):
        ids=[(rows[i].get('line_id'),rows[i].get('_component'),rows[i].get('_pool_index')) for i in indices]
        self.chain=hashlib.sha256(bytes.fromhex(self.chain)+json.dumps(ids,separators=(',',':')).encode()).hexdigest()
        self.draws+=len(indices)
        if os.environ.get('S1_TRACE')=='1':
            self.trace.append(dict(epoch=epoch,batch=position,step=step,draws=ids,loss_hex=float(loss).hex()))

    def stop(self,step):
        forced=int(os.environ.get('S1_FORCE_SPLIT_STEP','0'))
        deadline=float(os.environ.get('S1_DEADLINE_EPOCH','inf'))
        return self.requested or (forced>0 and step>=forced) or time.time()>=deadline-300

    def close(self):
        signal.signal(signal.SIGTERM,self.previous)
