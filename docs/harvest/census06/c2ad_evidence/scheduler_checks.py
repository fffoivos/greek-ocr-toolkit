from pathlib import Path
import subprocess,json,shlex,os
R=Path.cwd(); D=R/'docs/harvest/census06'; E=D/'c2ad_evidence'; W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'; runroot=W+'/census_06_20261020'; root=runroot+'/code/fb0194d597f20655'; bundle=root+'/docs/harvest/census06'; py=W+'/venv_l1/bin/python'
ssh=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','clariden']; records=[]
def run(label,command,expected=0,input=None):
 p=subprocess.run(ssh+[command],input=input,capture_output=True,text=True,timeout=120)
 r=dict(label=label,command=command,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr);records.append(r);(E/'scheduler_commands.json').write_text(json.dumps(records,indent=2)+'\n');(E/(label+'.log')).write_text(p.stdout+p.stderr);print(label,p.returncode,p.stdout.strip(),p.stderr[-180:],flush=True);assert p.returncode==expected,r;return p.stdout
run('partition-limits','scontrol show partition normal; scontrol show partition debug')
base=f'ALL,W={W},CENSUS06_BUNDLE={bundle},CENSUS06_SPLIT_FILE={runroot}/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82'
for mode in ['smoke','full']:
 for kind,limit in [('regression','00:05:00'),('parity','00:05:00'),('census','04:00:00'),('readout','00:30:00')]:
  partition='debug' if mode=='smoke' else 'normal';time='00:30:00' if mode=='smoke' else limit
  cmd=f'env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition={partition} --time={time} --chdir={runroot} --export={base},E4_SMOKE={int(mode=="smoke")},CENSUS06_ATTEMPT=c2ad-test-only-{mode},CENSUS06_EXPECT_ROWS={200 if mode=="smoke" else 592466} {bundle}/jobs/{kind}.sbatch'
  run('test-only-'+mode+'-'+kind,f"printf '%s\\n' '{kind} effective --time={time}'; "+cmd)
cmd=f'SBATCH_TIMELIMIT=06:00:00; export SBATCH_TIMELIMIT; printf "census effective --time=%s\\n" "$SBATCH_TIMELIMIT"; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=normal --time="$SBATCH_TIMELIMIT" --chdir={runroot} --export={base},E4_SMOKE=0,CENSUS06_ATTEMPT=c2ad-test-only-override,CENSUS06_EXPECT_ROWS=592466 {bundle}/jobs/census.sbatch'
run('test-only-override',cmd)
placeholder=runroot+'/scratchpad/c2ad-test-only-bindings.json'
parents=[p['id'] for p in json.loads((D/'census06_config.json').read_text())['parents']]
entries={p:dict(path='PENDING-test-only-NOT-A-REAL-BINDING',sha256='0'*64) for p in parents}
run('placeholder-create',f"{py} -B -c "+shlex.quote('from pathlib import Path; import sys; p=Path('+repr(placeholder)+'); p.parent.mkdir(parents=True,exist_ok=True); f=p.open("x"); f.write(sys.stdin.read()); f.close(); print(p)'),input=json.dumps(entries,indent=2)+'\n')
run('test-only-bind',f'env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=normal --time=00:30:00 --cpus-per-task=4 --chdir={runroot} --export={base},SF7_BINDINGS_FILE={placeholder},SF7_BIND_WORK={runroot}/binding/sf7-001 {bundle}/bind_sf7.sbatch')
state=run('binding-state',f'{py} -B {bundle}/binding_state.py');assert 'PENDING' in state and all(x in state for x in parents)
run('submit-pending',f'env W={W} CENSUS06_BUNDLE={bundle} CENSUS06_ATTEMPT=c2ad-pending-refusal E4_SMOKE=1 bash {bundle}/submit_chain.sh',expected=1)
run('bind-pending',f'{py} -B {bundle}/bind_sf7.py --check-only --work {runroot}/binding/c2ad-no-files',expected=2)
run('no-binding-work',f'test ! -e {runroot}/binding/sf7-001 && test ! -e {runroot}/binding/c2ad-no-files && echo BIND_WORK_ABSENT')
