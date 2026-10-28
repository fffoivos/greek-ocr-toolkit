"""Opt-in timing of the real S1 trainer; no alternate training recipe."""
import json
import os
from pathlib import Path
import time


class RuntimeTiming:
    def __init__(self, torch, device, out, start_step, started):
        self.torch,self.device,self.out=torch,device,Path(out)
        self.start_step,self.started=start_step,started
        self.samples=[];self.checkpoints=[];self.first_update=None
        self.sync();self.tick=time.perf_counter()

    def sync(self):
        if self.device.type=='cuda':self.torch.cuda.synchronize(self.device)

    def update(self,step):
        self.sync();now=time.perf_counter()
        self.samples.append(dict(step=step,seconds=now-self.tick))
        if self.first_update is None:self.first_update=now-self.started
        self.tick=now

    def checkpoint(self,seconds):
        self.checkpoints.append(seconds)
        self.tick=time.perf_counter()

    def finish(self,step,execution,validation=None,epoch_checkpoint_seconds=None):
        self.sync()
        record=dict(schema='s1-trainer-timing-v1',job_id=os.environ['SLURM_JOB_ID'],
            start_step=self.start_step,end_step=step,first_update_seconds=self.first_update,
            samples=self.samples,checkpoint_seconds=self.checkpoints,
            trainer_execution=execution,validation=validation,
            epoch_checkpoint_seconds=epoch_checkpoint_seconds,
            elapsed_seconds=time.perf_counter()-self.started)
        path=self.out/f'RUNTIME_TIMING_{self.start_step}.json'
        path.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
