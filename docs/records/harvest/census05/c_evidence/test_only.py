import pathlib,subprocess,json,shlex
D=pathlib.Path('docs/harvest/census05'); W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'; root=W+'/census_05_20261020'; bundle=root+'/code/997b7d2ab5a8775b/docs/harvest/census05'; records=[]
for smoke in (True,False):
 mode='smoke' if smoke else 'full'
 exports=dict(W=W,CENSUS05_BUNDLE=bundle,E4_SMOKE='1' if smoke else '0',CENSUS05_ATTEMPT=mode+'-split-001',CENSUS05_EXPECT_ROWS='200' if smoke else '592466',CENSUS05_SPLIT_FILE=root+'/inputs/row_split.jsonl.gz',CENSUS05_SPLIT_SHA256='7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82')
 if not smoke: exports['CENSUS05_BASELINE']=W+'/filter_pipeline_20261018/attempts/census_03/generations/g1-a21c3b465ca94eee80cb5bd34b336d69/summary.json'
 for kind in ('regression','parity','census','readout'):
  args=['sbatch','--test-only','--parsable']+(['--partition=debug','--time=00:30:00'] if smoke else [])+['--chdir='+root,'--export=ALL','--output='+root+'/logs/'+kind+'-%j.log',bundle+'/jobs/'+kind+'.sbatch']
  cmd='unset CENSUS05_RUN CENSUS05_READOUT_OUT CENSUS05_CONFIG CENSUS05_BASELINE; '+ ' '.join('export '+k+'='+shlex.quote(v)+';' for k,v in exports.items())+' '+shlex.join(args)
  assert '--test-only' in args
  p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','clariden',cmd],capture_output=True)
  records.append(dict(mode=mode,kind=kind,argv=args,remote_command=cmd,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()))
  (D/'c_evidence/test_only.json').write_text(json.dumps(records,indent=2)); print(mode,kind,p.returncode,p.stdout.decode(),p.stderr.decode(),flush=True); p.check_returncode()
