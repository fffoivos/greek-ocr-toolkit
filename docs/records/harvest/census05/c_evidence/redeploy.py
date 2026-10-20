from pathlib import Path
import json,subprocess,hashlib,shlex
D=Path('docs/harvest/census05');E=D/'c_evidence';R=Path.cwd();p=json.loads((D/'package_id.json').read_text());remote='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/'+p['package_id'];records=[]
ssh=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','clariden']
def run(argv,**kw):
 p=subprocess.run(argv,capture_output=True,**kw);records.append(dict(argv=argv,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()));(E/'deploy_commands.json').write_text(json.dumps(records,indent=2)+'\n');p.check_returncode();return p.stdout
manifest=(D/'DEPLOY_SHA256SUMS').read_text()
for h,path in [l.split('  ',1) for l in manifest.splitlines()]:assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
run(ssh+[f"mkdir -p '{remote}' && test -z \"$(find '{remote}' -mindepth 1 -print -quit)\""])
run(['rsync','-a','--files-from='+str(R/D/'DEPLOY_PATHS.txt'),str(R)+'/', 'clariden:'+remote+'/'])
run(ssh+[f"cd '{remote}' && sha256sum --check --quiet -"],input=manifest.encode())
entries=[dict(kind='code',local_path=path,remote_path=remote+'/'+path,sha256=h) for h,path in [l.split('  ',1) for l in manifest.splitlines()]]
entries += [dict(i,kind='input') for i in json.loads((D/'INPUTS.json').read_text())]
entries += [dict(kind='standing_cyrillic',remote_path=i['path'],sha256=i['sha256']) for i in json.loads((D/'census05_config.json').read_text())['corrections'] if i['tool']=='cyrillic']
raw=run(ssh+['sha256sum -- '+shlex.join([i['remote_path'] for i in entries])]);(E/'remote_sha256sum.txt').write_bytes(raw)
actual=dict((p,h) for h,p in [l.split('  ',1) for l in raw.decode().splitlines()])
for i in entries:i['remote_sha256']=actual[i['remote_path']];i['match']=i['sha256']==i['remote_sha256']
(E/'readback.json').write_text(json.dumps(entries,indent=2)+'\n');assert all(i['match'] for i in entries)
print('READBACK_OK',len(entries),'code',p['deploy_files'],'inputs 6 standing 5')
