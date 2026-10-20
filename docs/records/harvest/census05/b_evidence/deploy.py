import pathlib,json,subprocess,hashlib,shlex,datetime
repo=pathlib.Path.cwd(); rel=pathlib.Path('docs/harvest/census05'); ev=rel/'b_evidence'; remote='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7'; inputs=json.loads((rel/'INPUTS.json').read_text()); records=[]
def run(argv,**kw):
 p=subprocess.run(argv,capture_output=True,**kw); records.append(dict(argv=argv,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode())); (ev/'deploy_commands.json').write_text(json.dumps(records,indent=2)); p.check_returncode(); return p.stdout
ssh=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','clariden']
for i in inputs:
 p=pathlib.Path(i['local_path']); assert p.stat().st_size==i['bytes']; assert hashlib.sha256(p.read_bytes()).hexdigest()==i['sha256']
manifest=(rel/'DEPLOY_SHA256SUMS').read_text(); assert hashlib.sha256(manifest.encode()).hexdigest().startswith('17b0eb1ca7fe81a7'); assert len(manifest.splitlines())==167
for line in manifest.splitlines():
 sha,p=line.split('  ',1); assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==sha
inp=str(pathlib.PurePosixPath(inputs[0]['remote_path']).parent)
run(ssh+[f"mkdir -p '{remote}'; test -z \"$(find '{remote}' -mindepth 1 -print -quit)\"; test ! -d '{inp}' || test -z \"$(find '{inp}' -mindepth 1 -print -quit)\""])
run(['rsync','-a','--files-from='+str(repo/rel/'DEPLOY_PATHS.txt'),str(repo)+'/', 'clariden:'+remote+'/'])
run(ssh+[f"cd '{remote}' && sha256sum --check --quiet -"],input=manifest.encode())
run(ssh+[f"mkdir -p '{inp}'"])
for i in inputs:
 run(ssh+["test ! -e "+shlex.quote(i['remote_path'])]); run(['rsync','-a',i['local_path'],'clariden:'+i['remote_path']]); run(ssh+['sha256sum --check --quiet -'],input=(i['sha256']+'  '+i['remote_path']+'\n').encode())
entries=[dict(kind='code',local_path=p,remote_path=remote+'/'+p,sha256=s) for s,p in [l.split('  ',1) for l in manifest.splitlines()]]
entries += [dict(i,kind='input') for i in inputs]
entries += [dict(kind='standing_cyrillic',local_path=None,remote_path=i['path'],sha256=i['sha256']) for i in json.loads((rel/'census05_config.json').read_text())['corrections'] if i['tool']=='cyrillic']
raw=run(ssh+['sha256sum -- '+shlex.join([i['remote_path'] for i in entries])]); (ev/'remote_sha256sum.txt').write_bytes(raw)
actual=dict((p,s) for s,p in [l.split('  ',1) for l in raw.decode().splitlines()])
for i in entries: i['remote_sha256']=actual[i['remote_path']]; i['match']=i['sha256']==i['remote_sha256']
(ev/'readback.json').write_text(json.dumps(entries,indent=2)); assert all(i['match'] for i in entries)
print('READBACK_OK',len(entries),'deployed 167 inputs 6 standing 5')
