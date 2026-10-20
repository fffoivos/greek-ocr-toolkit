from pathlib import Path
import importlib.util,json,subprocess,sys,difflib
D=Path('docs/harvest/census05').resolve();E=D/'c_evidence'
spec=importlib.util.spec_from_file_location('t',D/'readout/test_census_readout.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
results=[]
for name,n,held,empty in [('configured_crop_leak',1,['crop-0'],False),('unconfigured_crop',1,[],False),('missing_train_export',3,[],True)]:
 run=t.make_run(E/name,n=n,corrupt=False);t.republish(run,held=held,empty=empty);p,r=t.cli(run,E/(name+'.readout'),n);results.append(dict(witness=name,exit_code=p.returncode,stdout=p.stdout,heldout_leaks=r['problems']['heldout_leaks']['count'],invariants=r['invariants']))
(E/'witnesses.json').write_text(json.dumps(results,indent=2)+'\n')
for name in ['smoke-mode-i','smoke-mode-ii','full-mode-ii']:
 run=D/'mock_batch/W/census_05_20261020/attempts'/name
 p=subprocess.run([sys.executable,'-B',str(D/'readout/census_readout.py'),'--run',str(run),'--out',str(E/('mock-'+name)),'--expect-rows','200','--expect-pipeline-version','0.3.2'],capture_output=True,text=True);(E/('mock-'+name+'.log')).write_text(p.stdout+p.stderr);p.check_returncode();print(name+': '+p.stdout.strip())
patch=[]
for n in ['census_readout.py','test_census_readout.py','readout.sbatch']:
 path='docs/records/harvest/census05/readout/'+n
 old=subprocess.check_output(['git','show','3b4090bf9b15d2d2cac53ee55161e936157ec0e5:'+path]).decode();new=(D/'readout'/n).read_text();patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
(D/'readout_fix.patch').write_text(''.join(patch))
