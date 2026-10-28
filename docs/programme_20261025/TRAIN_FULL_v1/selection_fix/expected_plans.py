"""Offline expected canonical remote plans, NOT proof of remote creation.

Uses the verified, already-local runtime receipt; never copies pools or contacts Slurm.
"""
from pathlib import Path
import json
import sys
BASE=Path(__file__).resolve().parents[1]
PKG=BASE/'stage_c_package'
sys.path.insert(0,str(PKG))
import stage_c
from common import sha,spec
from verify import verify


def main():
    verify()
    runtime=BASE.parents[2]/'out/TRAIN_FULL_v1/receipts_005/data_prepared_runtime.json'
    assert sha(runtime)=='21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4'
    payload=sha(PKG/'PAYLOAD.json')
    remote_pkg='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/pkg/'+payload[:16]
    remote_runtime='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared/runtime.json'
    work='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-013-stage-c-sel'
    out=BASE/'evidence/STAGE_C_SEL_BINDINGS'
    out.mkdir(exist_ok=True)
    def canonical(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    def relocate(x):
        if isinstance(x,dict): return {k:relocate(v) for k,v in x.items()}
        if isinstance(x,list): return [relocate(v) for v in x]
        if isinstance(x,str): return x.replace(str(PKG),remote_pkg).replace(str(runtime),remote_runtime)
        return x
    entries=[]
    for smoke in (True,False):
        name='smoke' if smoke else 'full';runs=[];d=out/name
        (d/'configs').mkdir(parents=True,exist_ok=True)
        for winner in stage_c.WINNERS:
            cfg=relocate(stage_c.make_run(runtime,winner,smoke=smoke))
            width='w%g'%cfg['parameters']['width_mult']
            for role in ('control','requeue') if smoke else ('full',):
                run=width+'-'+role;f=d/'configs'/(run+'.json');f.write_bytes(canonical(cfg))
                binding=spec(f);binding['path']=work+'/'+name+'/configs/'+f.name
                runs.append(dict(name=run,config=binding,output=work+'/'+name+'/runs/'+run,signal_smoke=role=='requeue'))
        plan=dict(schema='TRAIN_FULL-stage-C-plan-v1',payload_sha256=payload,runtime=relocate(spec(runtime)),
            smoke=smoke,fixture=False,runs=runs,resources='one non-exclusive 1-GPU job/run; 24 CPUs; 6 workers; no DDP',
            time_limit='23:00:00',warning_seconds=600)
        f=d/'PLAN.json';f.write_bytes(canonical(plan));binding=spec(f)
        binding['path']=work+'/'+name+'/PLAN.json';entries.append(binding)
    result=dict(status='OFFLINE_EXPECTED_BINDINGS_ONLY; remote plans not created by Sol',payload_sha256=payload,
        remote_package=remote_pkg,remote_work=work,runtime=relocate(spec(runtime)),plans=entries)
    (out/'EXPECTED.json').write_bytes(canonical(result))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
