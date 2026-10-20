"""One-time guarded B deployment; no submissions, no writes to census05."""
from pathlib import Path
import hashlib,json,subprocess,shlex,sys,os
R=Path.cwd();D=R/'docs/harvest/census06';E=D/'b_evidence';S=R.parent/'greek-ocr-toolkit-census06-verify';SD=S/'docs/harvest/census06'
SSH=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','clariden']
def run(argv,*,data=None):
 p=subprocess.run(argv,input=data,capture_output=True);rec=dict(argv=argv,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode());history.append(rec)
 (E/'deployment_commands.json').write_text(json.dumps(history,indent=2)+'\n')
 if p.returncode:raise RuntimeError(rec)
 return p.stdout
history=[]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
commit=run(['git','--no-optional-locks','-C',str(S),'rev-parse','HEAD']).decode().strip();assert commit=='cf1db4dd48690544f4a88c208a082a0af4e5a4f7'
assert not run(['git','--no-optional-locks','-C',str(S),'status','--porcelain'])
pkg=json.loads((SD/'package_id.json').read_text());root=pkg['root'];assert root.endswith('/census_06_20261020/code/de597753a70a5d6d')
manifest=(SD/'DEPLOY_SHA256SUMS').read_text();entries=[line.split('  ',1) for line in manifest.splitlines()];assert len(entries)==180
for h,p in entries:
 assert sha(S/p)==h
 assert hashlib.sha256(subprocess.check_output(['git','-C',str(S),'show',f'{commit}:{p}'])).hexdigest()==h
# Do not store payload source contents in the command receipt.
history=[r for r in history if r['argv'][0]!='git' or 'show' not in r['argv']]
inputs=[r for r in json.loads((SD/'INPUTS.json').read_text()) if r['kind']!='pending_sf7']
assert len(inputs)==6
# Validate all destinations before any remote mutation.
check='set -eu; root='+shlex.quote(root)+'; if [ -e "$root" ]; then test -d "$root"; test -z "$(ls -A -- "$root")"; fi; '
for r in inputs:
 assert '/census_06_20261020/inputs/' in r['remote_path']
 check+='test ! -e '+shlex.quote(r['remote_path'])+'; '
run(SSH+[check+'printf "DESTINATIONS_EMPTY_OR_ABSENT\\n"'])
run([sys.executable,'-B',str(D/'restore_inputs.py')])
for r in inputs:assert sha(Path(r['local_path']))==r['sha256']
run(SSH+['mkdir -p -- '+shlex.quote(root)+' '+shlex.quote(str(Path(inputs[0]['remote_path']).parent))])
run(['rsync','-a','--ignore-existing','--files-from='+str(SD/'DEPLOY_PATHS.txt'),str(S)+'/', 'clariden:'+root+'/'])
for r in inputs:
 run(SSH+['test ! -e '+shlex.quote(r['remote_path'])])
 run(['rsync','-a','--ignore-existing',r['local_path'],'clariden:'+r['remote_path']])
# Actual per-file remote SHA table, compared to committed hashes.
raw=run(SSH+['cd '+shlex.quote(root)+' && sha256sum -- '+ ' '.join(shlex.quote(p) for _,p in entries)]).decode();(E/'payload_readback.sha256').write_text(raw)
actual={p:h for h,p in (line.split('  ',1) for line in raw.splitlines())};assert actual=={p:h for h,p in entries}
cyr=[r for r in json.loads((SD/'census06_config.json').read_text())['corrections'] if r['tool']=='cyrillic']
for name,rows in [('inputs',inputs),('cyrillic',cyr)]:
 paths=[r.get('remote_path',r.get('path')) for r in rows]
 raw=run(SSH+['sha256sum -- '+' '.join(map(shlex.quote,paths))]).decode();(E/(name+'_readback.sha256')).write_text(raw)
 actual={p:h for h,p in (line.split('  ',1) for line in raw.splitlines())};assert actual=={p:r['sha256'] for p,r in zip(paths,rows)}
run(SSH+['scontrol show partition debug'])
(E/'deployment_summary.json').write_text(json.dumps(dict(commit=commit,root=root,payload_ok=180,payload_total=180,inputs_ok=6,inputs_total=6,cyrillic_ok=5,inputs=inputs,allow_untracked=[],job_submitted=False),indent=2)+'\n')
print('DEPLOY_READBACK_OK 180/180 inputs 6/6 cyrillic 5/5',flush=True)
