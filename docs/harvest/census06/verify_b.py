"""CENSUS06-B only: unchanged verifier, external receipts, then binding check.

Requires the lead's real commit and clean tracked tree. Not executed in A.
"""
from pathlib import Path
import argparse,subprocess,json,sys
D=Path(__file__).resolve().parent;R=D.parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve()
 if out.is_relative_to(R):p.error('receipts must be outside the repository during all four invocations')
 out.mkdir(parents=True,exist_ok=True);package=json.loads((D/'package_id.json').read_text());remote=package['root'];commit=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip();W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
 for kind in ['regression','parity','census','readout']:
  args=[sys.executable,'-B',str(R.parent/'greek-page-ocr-wave2/scripts/ops/verify_deploy.py'),'--repo',str(R),'--commit',commit,'--sha-file','docs/harvest/census06/DEPLOY_SHA256SUMS','--remote-root',remote,'--sbatch','docs/harvest/census06/jobs/'+kind+'.sbatch','--sbatch-args=--export=ALL,W='+W+',CENSUS06_BUNDLE='+remote+'/docs/harvest/census06,E4_SMOKE=1,CENSUS06_ATTEMPT=verify-smoke,CENSUS06_EXPECT_ROWS=200','--out',str(out/('verify-'+kind+'.json'))]
  proc=subprocess.run(args,cwd=R,capture_output=True,text=True);(out/('verify-'+kind+'.log')).write_text(proc.stdout+proc.stderr);print(kind,proc.returncode,proc.stdout.strip())
  if proc.returncode:raise SystemExit(proc.returncode)
 subprocess.run([sys.executable,'-B',str(D/'binding_state.py')],check=True)
if __name__=='__main__':main()
