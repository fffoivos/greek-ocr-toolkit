"""Unchanged verifier against clean lead worktree; scheduler test-only; pending guards."""
from pathlib import Path
import subprocess,sys,json,shlex,hashlib,os
R=Path.cwd();D=R/'docs/harvest/census06';E=D/'b_evidence';S=R.parent/'greek-ocr-toolkit-census06-verify';SD=S/'docs/harvest/census06';W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3';root=json.loads((SD/'package_id.json').read_text())['root'];bundle=root+'/docs/harvest/census06';verifier=R.parent/'greek-page-ocr-wave2/scripts/ops/verify_deploy.py';SSH=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','clariden'];records=[]
def run(label,argv,expected=0):
 p=subprocess.run(argv,capture_output=True,text=True);(E/(label+'.log')).write_text(p.stdout+p.stderr)
 rec=dict(label=label,argv=argv,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr);records.append(rec);(E/'verification_commands.json').write_text(json.dumps(records,indent=2)+'\n');print(label,p.returncode,(p.stdout+p.stderr)[-500:],flush=True)
 if expected is None:assert p.returncode!=0
 else:assert p.returncode==expected
 return rec
for kind in ['regression','parity','census','readout']:
 run('verify-'+kind,[sys.executable,'-B',str(verifier),'--repo',str(S),'--commit','cf1db4dd48690544f4a88c208a082a0af4e5a4f7','--sha-file','docs/harvest/census06/DEPLOY_SHA256SUMS','--remote-root',root,'--sbatch','docs/harvest/census06/jobs/'+kind+'.sbatch','--sbatch-args=--export=ALL,W='+W+',CENSUS06_BUNDLE='+bundle+',E4_SMOKE=1,CENSUS06_ATTEMPT=verify-smoke,CENSUS06_EXPECT_ROWS=200','--out',str(E/('verify-'+kind+'.json'))])
 receipt=json.loads((E/('verify-'+kind+'.json')).read_text());assert receipt['verdict']=='VERIFY_OK';assert not receipt['steps']['local']['allowed_untracked']
for mode in ['smoke','full']:
 for kind in ['regression','parity','census','readout']:
  script=SD/'jobs'/(kind+'.sbatch');lines=script.read_text().splitlines()
  assert '#SBATCH --account=a0140' in lines and '#SBATCH --partition=normal' in lines
  time=next(l.split('=',1)[1] for l in lines if l.startswith('#SBATCH --time='));assert time==dict(regression='00:05:00',parity='00:05:00',census='04:00:00',readout='00:30:00')[kind]
  export='ALL,W='+W+',CENSUS06_BUNDLE='+bundle+',E4_SMOKE='+('1' if mode=='smoke' else '0')+',CENSUS06_ATTEMPT=test-only-'+mode+',CENSUS06_EXPECT_ROWS='+('200' if mode=='smoke' else '592466')+',CENSUS06_SPLIT_FILE='+W+'/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82'
  argv=['sbatch','--test-only','--account=a0140','--partition='+('debug' if mode=='smoke' else 'normal'),'--time='+('00:30:00' if mode=='smoke' else time),'--chdir='+W+'/census_06_20261020','--export='+export,bundle+'/jobs/'+kind+'.sbatch']
  run('test-only-'+mode+'-'+kind,SSH+['cd '+shlex.quote(root)+' && '+shlex.join(argv)])
# nargs+ refusal in --check-only mode, without any per-parent files: no work is made.
run('bind-pending',SSH+[shlex.join([W+'/venv_l1/bin/python','-B',bundle+'/bind_sf7.py','--check-only','--work',W+'/census_06_20261020/binding/b-pending-dry-run'])],expected=None)
# Guard executes before mkdir or sbatch. This shell never invokes any sbatch.
env=['env','W='+W,'CENSUS06_BUNDLE='+bundle,'CENSUS06_ATTEMPT=b-pending-dry-run','E4_SMOKE=1','bash',bundle+'/submit_chain.sh']
r=run('submit-pending',SSH+[shlex.join(env)],expected=None);assert 'sf7-binding PENDING' in r['stdout']+r['stderr']
run('binding-state',SSH+[shlex.join([W+'/venv_l1/bin/python','-B',bundle+'/binding_state.py'])])
assert not subprocess.check_output(['git','--no-optional-locks','-C',str(S),'status','--porcelain'])
(E/'verifier_identity.json').write_text(json.dumps(dict(path=str(verifier),sha256=hashlib.sha256(verifier.read_bytes()).hexdigest(),source=str(S),commit='cf1db4dd48690544f4a88c208a082a0af4e5a4f7',clean_after=True,allow_untracked=[],job_submitted=False),indent=2)+'\n')
