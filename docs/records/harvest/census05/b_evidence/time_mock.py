import os,sys,pathlib,hashlib,subprocess,time,json
D=pathlib.Path('docs/harvest/census05').resolve(); ev=D/'b_evidence'; mock=D/'mock_batch'; split=mock/'split.jsonl'
env=dict(os.environ,PATH=str(mock/'bin')+os.pathsep+os.environ['PATH'],W=str(ev/'timed_mock/W'),CENSUS05_BUNDLE=str(D),CENSUS05_PYTHON=sys.executable,CENSUS05_CONFIG=str(mock/'source_config.json'),SLURM_JOB_PARTITION='debug',CENSUS05_EXPECT_ROWS='200',MOCK_SRUN_LOG=str(ev/'timed_mock_srun.jsonl'),MOCK_OBSERVATIONS=str(mock/'observations.jsonl'),MOCK_BATCH_SCRIPT=str(D/'mock_batch.py'),E4_SMOKE='1',CENSUS05_ATTEMPT='smoke-timing',CENSUS05_SPLIT_FILE=str(split),CENSUS05_SPLIT_SHA256=hashlib.sha256(split.read_bytes()).hexdigest(),PYTHONDONTWRITEBYTECODE='1')
start=time.monotonic()
with (ev/'timed_mock.log').open('w') as log: p=subprocess.run(['bash',str(mock/'slurm-spool/census.sbatch')],cwd='/private/tmp',env=env,stdout=log,stderr=subprocess.STDOUT)
seconds=time.monotonic()-start;p.check_returncode(); run=ev/'timed_mock/W/census_05_20261020/attempts/smoke-timing'; summary=json.loads((run/'summary.json').read_text()); assert summary['complete'] and summary['input_rows']==200
r=dict(rows=200,elapsed_seconds=seconds,rows_per_second=200/seconds,smoke_time='00:10:00',basis='600 seconds exceeds measured mock duration; saved native observations and synthetic corrections, not remote throughput qualification',job_exit=p.returncode)
(ev/'smoke_timing.json').write_text(json.dumps(r,indent=2)); print(r)
