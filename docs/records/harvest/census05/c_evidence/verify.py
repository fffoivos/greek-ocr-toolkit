from pathlib import Path
import subprocess,json
D=Path('docs/harvest/census05');R=Path.cwd();p=json.loads((D/'package_id.json').read_text());W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3';remote=W+'/census_05_20261020/code/'+p['package_id'];commit=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()
for kind in ['regression','parity','census','readout']:
 args=['/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python','-B',str(R/'../greek-page-ocr-wave2/scripts/ops/verify_deploy.py'),'--repo',str(R),'--commit',commit,'--sha-file',str(D/'DEPLOY_SHA256SUMS'),'--remote-root',remote,'--sbatch',str(D/'jobs'/ (kind+'.sbatch')),'--sbatch-args=--export=ALL,W='+W+',CENSUS05_BUNDLE='+remote+'/'+str(D)+',E4_SMOKE=1,CENSUS05_ATTEMPT=verify-smoke,CENSUS05_EXPECT_ROWS=200','--out',str(D/'c_evidence'/('verify-'+kind+'.json'))]
 proc=subprocess.run(args,capture_output=True,text=True);(D/'c_evidence'/('verify-'+kind+'.log')).write_text(proc.stdout+proc.stderr);print(kind,proc.returncode,proc.stdout.strip(),flush=True)
 # Owner-gated authentication failures end all further work immediately.
 if any(x in (proc.stdout+proc.stderr).lower() for x in ['permission denied','authentication failed','certificate invalid']): raise SystemExit('SSH/authentication failed: stop')
