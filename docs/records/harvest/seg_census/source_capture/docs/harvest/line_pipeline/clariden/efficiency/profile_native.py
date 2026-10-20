"""Bounded CSCS diagnostic profiling; never a processing entrypoint on the Mac."""
import argparse,cProfile,hashlib,json,os
from pathlib import Path
import pstats,shutil,sys,time
p=argparse.ArgumentParser();p.add_argument('--projects',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--bound',action='store_true');a=p.parse_args()
if not os.environ.get('SLURM_JOB_ID') or sys.platform!='linux':raise RuntimeError('Slurm Linux worker required')
if not a.bound:
    node=json.loads((a.root/'runtime/node.json').read_text());codec=json.loads((a.root/'runtime/png-codec.json').read_text())
    assert hashlib.sha256(Path(codec['library']).read_bytes()).hexdigest()==codec['sha256']
    env=dict(os.environ,LD_PRELOAD=codec['library'],PATH=str(Path(node['node']).parent)+os.pathsep+os.environ['PATH'])
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):env[key]='1'
    os.execvpe(sys.executable,[sys.executable,'-B',__file__,*sys.argv[1:],'--bound'],env)
sys.path.insert(0,str(a.projects/'greek-ocr-toolkit-sol-recut'))
from greekocr.harvest.line_pipeline_native import NativeSegmenter
from greekocr.harvest.line_pipeline_runtime import validate
from greekocr.harvest.line_pipeline_census import run,records,atomic_json
q=a.root/'attempts/qual_08/qualify';config=json.loads((q/'config_w16.json').read_text())
validate(config['runtime_manifest'],dict(node=shutil.which('node'),predictor=config['predictor']))
a.out.mkdir(parents=True,exist_ok=False)
def stats(prof,name):
    prof.dump_stats(str(a.out/(name+'.prof')));s=pstats.Stats(prof)
    def pack(item):
        (filename,line,function),(primitive,calls,internal,cumulative,callers)=item
        return dict(file=filename,line=line,function=function,calls=calls,internal_seconds=internal,cumulative_seconds=cumulative)
    result=dict(total_calls=s.total_calls,total_seconds=s.total_tt,
        cumulative=[pack(v) for v in sorted(s.stats.items(),key=lambda v:v[1][3],reverse=True)[:45]],
        internal=[pack(v) for v in sorted(s.stats.items(),key=lambda v:v[1][2],reverse=True)[:45]])
    atomic_json(a.out/(name+'.json'),result)
coordinator=cProfile.Profile();started=time.monotonic();coordinator.enable()
summary=run(config,a.out/'census16',execute=True)
coordinator.disable();stats(coordinator,'coordinator');wall=time.monotonic()-started
native=NativeSegmenter(json.loads(Path(config['versions']).read_text())['tools'],config['predictor'],node=shutil.which('node'))
prof=cProfile.Profile();observations=[]
try:
    for _,row in records(q/'sample.jsonl'):
        started=time.monotonic();cpu=time.process_time();prof.enable()
        try:
            result=native(row);error=None
        except Exception as exc:result={};error=dict(type=type(exc).__name__,message=str(exc))
        finally:prof.disable()
        observations.append(dict(id=row['id'],source=row['source'],parent=row.get('qualification_source_parent'),
            seconds=time.monotonic()-started,cpu_seconds=time.process_time()-cpu,verdict=result.get('verdict'),error=error))
finally:native.close()
stats(prof,'native')
atomic_json(a.out/'profile.json',dict(job=os.environ['SLURM_JOB_ID'],cpus=os.cpu_count(),affinity=sorted(os.sched_getaffinity(0)),
    coordinator_wall_seconds=wall,complete=summary['complete'],rows=len(observations),native_cpu_seconds=sum(v['cpu_seconds'] for v in observations),
    native_wall_seconds=sum(v['seconds'] for v in observations),observations=observations))
print(json.dumps(dict(status='profiled',rows=len(observations),affinity_cpus=len(os.sched_getaffinity(0)),out=str(a.out))),flush=True)
