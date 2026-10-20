"""Literal basename grep of the working tree; no git writes; output beside script."""
import pathlib,subprocess,json,collections,os
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];os.chdir(R)
paths=[p.decode() for p in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if p]
names={pathlib.PurePosixPath(p).name for p in paths}
common={n for n in names if '.' not in n};rare=names-common
pattern=O/'basename_patterns.txt';pattern.write_text('\n'.join(sorted(rare))+'\n')
lengths=sorted({len(n) for n in names});cache={};refs=collections.defaultdict(set)
cmd=['rg','--only-matching','--with-filename','--null','--no-heading','--no-line-number','--no-ignore','--hidden','--fixed-strings','--file',str(pattern),'--glob','!.git/**','--glob','!docs/cleanup_20261019/data_out/**','.']
p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
n=0
for raw in p.stdout:
 # rg's output uses NUL between filename and matched literal, newline per match.
 if b'\0' not in raw: continue
 filename,match=raw.rstrip(b'\n').split(b'\0',1)
 filename=filename.decode(errors='surrogateescape').removeprefix('./');match=match.decode(errors='surrogateescape')
 if match not in cache:
  # Recover nested basename matches omitted by rg's non-overlapping output.
  found=set()
  for start in range(len(match)):
   for length in lengths:
    if start+length>len(match):break
    candidate=match[start:start+length]
    if candidate in names:found.add(candidate)
  cache[match]=found
 for name in cache[match]: refs[name].add(filename)
 n+=1
 if n%1000000==0:print('reader matches',n,flush=True)
err=p.stderr.read().decode();rc=p.wait();assert rc in (0,1),(rc,err)
for name in sorted(common):
 q=subprocess.run(['rg','--files-with-matches','--null','--no-ignore','--hidden','--fixed-strings','--glob','!.git/**','--glob','!docs/cleanup_20261019/data_out/**','--',name,'.'],capture_output=True)
 assert q.returncode in (0,1),(name,q.stderr)
 refs[name].update(x.decode(errors='surrogateescape').removeprefix('./') for x in q.stdout.split(b'\0') if x)
print('common basename scans',len(common),flush=True)
(O/'readers.json').write_text(json.dumps({k:sorted(v) for k,v in refs.items()},separators=(',',':')))
(O/'reader_scan.json').write_text(json.dumps(dict(command=cmd,matches=n,names=len(names),matched_names=len(refs),stderr=err),indent=2))
print('readers complete',n,'matched names',len(refs),flush=True)
