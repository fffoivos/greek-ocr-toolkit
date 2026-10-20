from pathlib import Path
import subprocess,json,hashlib,shlex,sys,os
R=Path.cwd(); D=R/'docs/harvest/census06'; E=D/'c2ad_evidence'; S=R.parent/'greek-ocr-toolkit-census06-verify-c2a'; SD=S/'docs/harvest/census06'
W='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'; root=W+'/census_06_20261020/code/fb0194d597f20655'; bundle=root+'/docs/harvest/census06'
ssh=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','clariden']; commands=[]
def run(label,argv,input=None,expected=0):
 p=subprocess.run(argv,input=input,capture_output=True,text=True,timeout=180,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','PYTHONDONTWRITEBYTECODE':'1'})
 rec=dict(label=label,argv=argv,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr); commands.append(rec); (E/'commands.json').write_text(json.dumps(commands,indent=2)+'\n'); (E/(label+'.log')).write_text(p.stdout+p.stderr)
 print(label,p.returncode,p.stdout[-800:],flush=True)
 assert p.returncode==expected,rec
 return p.stdout
assert subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD'],text=True).strip()=='0cc5710bf1029189ab5957f429ed9c1f95622088'
assert not subprocess.check_output(['git','-C',str(S),'status','--porcelain'],text=True)
manifest=(SD/'DEPLOY_SHA256SUMS').read_text(); paths=(SD/'DEPLOY_PATHS.txt').read_text().splitlines(); entries={line[66:]:line[:64] for line in manifest.splitlines()}
assert set(paths)==set(entries) and len(entries)==182
for path,sha in entries.items():
 assert hashlib.sha256((S/path).read_bytes()).hexdigest()==sha
 assert hashlib.sha256(subprocess.check_output(['git','-C',str(S),'show','HEAD:'+path])).hexdigest()==sha
run('destination-guard',ssh+[f"set -eu; d={root}; if [ -e \"$d\" ]; then test -d \"$d\"; test -z \"$(find \"$d\" -mindepth 1 -print -quit)\"; fi; test ! -e {W}/census_06_20261020/binding/sf7-001; mkdir -p \"$d\"; echo NEW_EMPTY_DESTINATION"])
run('rsync', ['rsync','-av','--ignore-existing','--files-from='+str(SD/'DEPLOY_PATHS.txt'),str(S)+'/', 'clariden:'+root+'/'])
raw=run('payload-readback',ssh+[f'cd {root} && sha256sum '+ ' '.join(shlex.quote(x) for x in paths)])
actual={line[66:]:line[:64] for line in raw.splitlines()}; assert actual==entries
inputs=[x for x in json.loads((SD/'INPUTS.json').read_text()) if x.get('remote_path')]
cyr=[x for x in json.loads((SD/'census06_config.json').read_text())['corrections'] if x['tool']=='cyrillic']
checks=[dict(path=x['remote_path'],sha256=x['sha256'],kind=x['kind']) for x in inputs]+[dict(path=x['path'],sha256=x['sha256'],kind='standing_cyrillic') for x in cyr]
raw=run('inputs-rehash',ssh+['sha256sum '+' '.join(shlex.quote(x['path']) for x in checks)])
actual={line[66:]:line[:64] for line in raw.splitlines()}
for x in checks: x['actual_sha256']=actual[x['path']]; assert x['sha256']==x['actual_sha256']
(E/'readback.json').write_text(json.dumps(dict(payload_ok=len(entries),payload_total=len(entries),inputs=checks,inputs_ok=len(inputs),cyrillic_ok=len(cyr)),indent=2)+'\n')
verifier=R.parent/'greek-page-ocr-wave2/scripts/ops/verify_deploy.py'; (E/'verifier_identity.json').write_text(json.dumps(dict(path=str(verifier),sha256=hashlib.sha256(verifier.read_bytes()).hexdigest()),indent=2)+'\n')
for kind in ['regression','parity','census','readout']:
 run('verify-'+kind,[sys.executable,'-B',str(verifier),'--repo',str(S),'--commit','0cc5710bf','--sha-file','docs/harvest/census06/DEPLOY_SHA256SUMS','--remote-root',root,'--sbatch','docs/harvest/census06/jobs/'+kind+'.sbatch','--sbatch-args=--account=a0140 --partition=normal --time='+dict(regression='00:05:00',parity='00:05:00',census='04:00:00',readout='00:30:00')[kind]+' --export=ALL,W='+W+',CENSUS06_BUNDLE='+bundle+',E4_SMOKE=1,CENSUS06_ATTEMPT=verify-smoke,CENSUS06_EXPECT_ROWS=200','--out',str(E/('verify-'+kind+'.json'))])
assert not subprocess.check_output(['git','-C',str(S),'status','--porcelain'],text=True)
