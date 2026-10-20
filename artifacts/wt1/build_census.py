import os, pathlib, subprocess, json, collections, datetime, hashlib, re
M=pathlib.Path.cwd(); names='align l1 l1f l1r l1r2 l1r3 r0 s8'.split()
def git(p,*a): return subprocess.check_output(['git','-C',str(p),*a])
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def inv(p,ignored=False):
 a=['ls-files','--others','--exclude-standard','-z']
 if ignored:a.insert(2,'--ignored')
 out=[]
 for x in git(p,*a).split(b'\0'):
  if not x:continue
  r=os.fsdecode(x);f=p/r;s=f.lstat();cache=any(z in ('__pycache__','.pytest_cache') for z in pathlib.Path(r).parts)
  out.append(dict(path=r,bytes=s.st_size,symlink=f.is_symlink(),cache=cache))
 return out
roots=[M,M.parent/(M.name+'-r2prep'),M.parent/(M.name+'-r2cards'),M.parent/'greek-ocr-toolkit-cleanup',M.parent/(M.name+'-r1'),M.parent/'greek-ocr-toolkit-secondary/docs/labelfix/lqb']
patterns=[]
for n in names:
 p=str(M)+'-'+n
 patterns+=['-e',p,'-e','~/Projects/'+M.name+'-'+n]
cmd=['rg','--json','-n','-I','--hidden','--no-ignore','-g','!.git','-g','!__pycache__','-g','!.pytest_cache','-g','!**/artifacts/wt1/**','-g','!WT1_CENSUS.md',*patterns,*map(str,roots)]
r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode in (0,1),r.stderr
hits={n:[] for n in names}
for l in r.stdout.splitlines():
 d=json.loads(l)
 if d['type']!='match':continue
 d=d['data'];line=d['lines']['text'].rstrip('\n');file=d['path']['text']
 for n in names:
  prefix=str(M)+'-'+n; alt='~/Projects/'+M.name+'-'+n
  if not any(re.search(re.escape(x)+r'(?=/|[\s\"\x27`:,;\]\)}]|$)',line) for x in (prefix,alt)):continue
  targets=[]
  for match in re.finditer('(?:'+re.escape(prefix)+'|'+re.escape(alt)+r')(/[^\s\"\x27`<>\]\)},;]*)?',line):
   # Reject e.g. l1 matching l1r.
   end=match.end()
   if end<len(line) and line[end] not in '/ \t\"\x27`:,;])}':continue
   rel=(match.group(1) or '').lstrip('/');src=pathlib.Path(prefix)/rel;dst=M/rel
   identical=bool(rel and src.is_file() and dst.is_file() and sha(src)==sha(dst))
   targets.append(dict(old=match.group(0),replacement=str(dst),relative_path=rel,byte_identical=identical,sha256=sha(src) if identical else None))
  hits[n].append(dict(file=file,line=d['line_number'],text=line,targets=targets))
lsof=subprocess.run(['lsof','-a','-d','cwd','-Fpcn'],capture_output=True,text=True);assert lsof.returncode in (0,1) and not lsof.stderr,lsof.stderr
processes=[];pid=command=None
for l in lsof.stdout.splitlines():
 if l.startswith('p'):pid=l[1:]
 elif l.startswith('c'):command=l[1:]
 elif l.startswith('n'):processes.append(dict(pid=pid,command=command,cwd=l[1:]))
data=dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),main=str(M),main_tip=git(M,'rev-parse','opus/spellcheck').decode().strip(),citation_roots=list(map(str,roots)),citation_scan_stderr=r.stderr,lsof_command=['lsof','-a','-d','cwd','-Fpcn'],lsof_scope='Processes visible to this user; snapshot, recheck at execution.',candidates=[])
for n in names:
 p=pathlib.Path(str(M)+'-'+n);u=inv(p);i=inv(p,True)
 status=git(p,'status','--porcelain=v1','-z','--untracked-files=no').decode().split('\0');status=[x for x in status if x]
 merged=subprocess.run(['git','-C',str(M),'merge-base','--is-ancestor',git(p,'rev-parse','HEAD').decode().strip(),'opus/spellcheck']).returncode;assert merged in (0,1)
 live=[x for x in processes if x['cwd']==str(p) or x['cwd'].startswith(str(p)+'/')]
 keep=not merged==0 or bool(live) or bool(status)
 custody=[x for x in u+i if not x['cache']]
 proposal=['KEEP'] if keep else (['CUSTODY-THEN-REMOVE'] if custody else [])+(['REPOINT-THEN-REMOVE'] if hits[n] else [])
 if not proposal:proposal=['REMOVE-CLEAN']
 row=dict(name=p.name,path=str(p),branch=git(p,'symbolic-ref','--short','HEAD').decode().strip(),tip=git(p,'rev-parse','HEAD').decode().strip(),merged=merged==0,tracked_modifications=len(status),tracked_status=status,untracked=u,ignored=i,untracked_count=len(u),untracked_bytes=sum(x['bytes'] for x in u),ignored_count=len(i),ignored_bytes=sum(x['bytes'] for x in i),untracked_top_dirs=dict(collections.Counter(x['path'].split('/')[0] for x in u)),citations=hits[n],processes=live,proposal=proposal,custody_destination=str(M/'artifacts/worktree_custody'/p.name),custody_count=len(custody),custody_bytes=sum(x['bytes'] for x in custody),cache_exclusions=[x['path'] for x in u+i if x['cache']])
 data['candidates'].append(row)
 print(n,row['merged'],len(status),len(u),len(i),len(hits[n]),len(live),proposal,flush=True)
rel='docs/labelfix/spellcheck/S8_DEV/evidence/dev_truth.jsonl.gz';src=pathlib.Path(str(M)+'-s8')/rel;dst=M/rel
data['s8_known_evidence']=dict(relative_path=rel,s8_exists=src.exists(),main_exists=dst.exists(),s8_tracked=bool(git(pathlib.Path(str(M)+'-s8'),'ls-files','--',rel)),main_tracked=bool(git(M,'ls-files','--',rel)),byte_identical=src.is_file() and dst.is_file() and sha(src)==sha(dst),s8_sha256=sha(src) if src.is_file() else None,main_sha256=sha(dst) if dst.is_file() else None)
(M/'artifacts/wt1/census.json').write_text(json.dumps(data,indent=2)+'\n')
