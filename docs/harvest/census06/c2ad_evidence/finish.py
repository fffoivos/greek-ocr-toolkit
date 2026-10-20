from pathlib import Path
import importlib.util,json,subprocess,hashlib,shutil,os
R=Path.cwd();D=R/'docs/harvest/census06';E=D/'c2ad_evidence';base=D/'c2ad-pytest-tmp'
spec=importlib.util.spec_from_file_location('c1',D/'test_timing_c1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=base/'explicit-print';p.mkdir()
r,calls=m.chain(p,override='06:00:00',args=('--account=a0140','--partition=normal','--test-only'))
assert r.returncode==0 and len(calls)==4
assert all(envlimit is None for argv,envlimit in calls)
assert [(' --time=06:00:00' in ' '+' '.join(argv)) for argv,_ in calls]==[False,False,True,False]
assert all('--test-only' in argv for argv,_ in calls)
(E/'override-isolation.json').write_text(json.dumps(dict(note='Local unchanged chain fixture; fake sbatch only; no remote calls or real binding',stdout=r.stdout,stderr=r.stderr,calls=calls),indent=2)+'\n')
(E/'override-isolation.log').write_text(r.stdout+r.stderr)
size=sum(x.stat().st_size for x in base.rglob('*') if x.is_file());shutil.rmtree(base)
(E/'cleanup.json').write_text(json.dumps(dict(deleted=[dict(path=str(base.relative_to(R)),bytes=size)],other_deletions=[],note='Only this run basetemp; pytest logs and XML retained'),indent=2)+'\n')
S=R.parent/'greek-ocr-toolkit-census06-verify-c2a'
status=subprocess.check_output(['git','-C',str(S),'status','--porcelain'],text=True);assert not status
(E/'source-final.json').write_text(json.dumps(dict(repo=str(S),commit=subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD'],text=True).strip(),porcelain=status,no_exemptions=True),indent=2)+'\n')
