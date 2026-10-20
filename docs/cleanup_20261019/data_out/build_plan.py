"""Read-only CLEAN3A inventory; writes only beside this script. No moves or git writes."""
import concurrent.futures as cf
import collections, csv, hashlib, json, os, pathlib, re, subprocess, time
R=pathlib.Path(__file__).resolve().parents[3]
O=pathlib.Path(__file__).resolve().parent
os.chdir(R)
def git(*args): return subprocess.check_output(['git',*args])
def emit(s): print(s,flush=True)
def tsv(name,header,rows):
 with (O/name).open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(header);w.writerows(rows)
head=git('show','-s','--format=%H %D','HEAD').decode().strip()
index_before=hashlib.sha256((R/'.git').read_bytes()).hexdigest() if (R/'.git').is_file() else None
entries=[x.split(b'\t',1) for x in git('ls-files','-s','-z').split(b'\0') if x]
paths=[p.decode() for _,p in entries]
meta=[x.decode().split() for x,_ in entries]
checks=subprocess.run(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)'],input=''.join('HEAD:'+p+'\n' for p in paths),text=True,capture_output=True,check=True).stdout.splitlines()
rows=[]
for p,m,c in zip(paths,meta,checks):
 oid,typ,n=c.split(); assert typ=='blob' and oid==m[1],(p,c,m)
 rows.append(dict(path=p,bytes=int(n),oid=oid,mode=m[0]))
assert len(rows)==len(paths)
# Conservative coverage: all HEAD paths, including source siblings, so no interpretation
# of recursive directory membership can omit a required artifact.
# Qualifying directories are recorded both directly and recursively, excluding '.' only.
direct=collections.defaultdict(lambda:[0,0,0]); rec=collections.defaultdict(lambda:[0,0,0])
for x in rows:
 p=pathlib.PurePosixPath(x['path']); c=int(str(p).lower().endswith(('.png','.jpg','.jsonl','.jsonl.gz','.html')))
 for d in [str(p.parent)]:
  direct[d][0]+=1;direct[d][1]+=x['bytes'];direct[d][2]+=c
 for d in p.parents:
  if str(d)!='.': rec[str(d)][0]+=1;rec[str(d)][1]+=x['bytes'];rec[str(d)][2]+=c
bulk={d:v for d,v in rec.items() if v[1]>20_000_000 or v[2]>=50}
tsv('BULK_DIRECTORIES.tsv',['directory','direct_files','direct_bytes','direct_matching_extensions','recursive_files','recursive_bytes','recursive_matching_extensions','qualifies_directly'],[(d,*direct[d],*v,str(direct[d][1]>20_000_000 or direct[d][2]>=50)) for d,v in sorted(bulk.items())])
stat_before={}
def hashrow(x):
 p=R/x['path']; st=p.lstat();stat_before[x['path']]=(st.st_size,st.st_mtime_ns,st.st_mode)
 h=hashlib.sha256();g=hashlib.sha1(b'blob '+str(x['bytes']).encode()+b'\0')
 if x['mode']=='120000':
  b=os.fsencode(os.readlink(p));h.update(b);g.update(b); n=len(b)
 else:
  n=0
  with p.open('rb') as f:
   while b:=f.read(1024*1024):h.update(b);g.update(b);n+=len(b)
 assert n==x['bytes'] and g.hexdigest()==x['oid'],('working bytes differ from HEAD',x['path'])
 x['sha256']=h.hexdigest()
 return x

def producer(x):
 x['producing_commit']=git('log','-1','--format=%h','--',x['path']).decode().strip()
 assert x['producing_commit'],x['path']
 return x
emit(f'HEAD {head}; paths={len(rows)} bytes={sum(x["bytes"] for x in rows)}')
# Start exact path-limited history queries while hashing; results are cached to permit
# report-only re-rendering without re-running the expensive read-only collection.
with cf.ThreadPoolExecutor(max_workers=6) as pool:
 futures=[pool.submit(producer,x) for x in rows]
 with cf.ThreadPoolExecutor(max_workers=2) as hp:
  for i,x in enumerate(hp.map(hashrow,rows),1):
   if i%10000==0:emit(f'hashed {i}/{len(rows)}')
 emit('hashes verified against HEAD; collecting exact producing commits')
 for i,f in enumerate(futures,1):
  f.result()
  if i%5000==0:emit(f'path logs {i}/{len(rows)}')
(O/'snapshot.json').write_text(json.dumps(dict(head=head,rows=rows,stats=stat_before),separators=(',',':')))
emit('snapshot complete')
