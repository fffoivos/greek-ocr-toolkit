"""Re-run both M2 scripts for each S7 candidate, preserving original M2 files."""
import os
from pathlib import Path
import subprocess
import sys
from greekocr.labelfix.reading import QUALIFIED_GEOMETRY


def main():
    root=Path(__file__).resolve().parents[2]
    evidence=root/'docs/records/labelfix/spellcheck/S7_evidence'
    env=dict(os.environ,PYTHONPATH=str(root),PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',
             VECLIB_MAXIMUM_THREADS='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for label,substitutions in [('scope_only',[]),('S1',['S1']),('S2',['S2']),('S3',['S3']),('accepted',sorted(QUALIFIED_GEOMETRY))]:
        out=evidence/('m2_'+label);out.mkdir(parents=True,exist_ok=True)
        with (out/'run.log').open('w') as log:
            subprocess.run([sys.executable,'-m','scripts.labelfix.m2_run','--replay-detector',*substitutions,
                '--output-dir',str(out),'--script-classes',str(evidence/'m2_script_classes.jsonl')],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        with (out/'score.log').open('w') as log:
            subprocess.run([sys.executable,'-m','scripts.labelfix.m2_score','--output-dir',str(out),'--no-spotcheck-queue'],
                cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        print('M2 replay and score complete:',label,flush=True)


if __name__=='__main__':main()
