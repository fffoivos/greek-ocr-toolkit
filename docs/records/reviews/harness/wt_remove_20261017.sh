#!/usr/bin/env bash
# Lead-executed, offline only. No default authorization: the lead supplies WT1_RULING.json.
set -euo pipefail
set -E
trap 'rc=$?; printf "FAIL line %s (exit %s)\n" "$LINENO" "$rc" >&2; exit "$rc"' ERR
export GIT_OPTIONAL_LOCKS=0 GIT_NO_REPLACE_OBJECTS=1 PYTHONDONTWRITEBYTECODE=1
export PYTHONOPTIMIZE=
MODE=${1:---dry-run}
[[ $# -eq 0 ]] || shift
[[ $MODE == --dry-run || $MODE == --execute ]] || { echo 'invalid mode' >&2; exit 2; }
RULING=
if [[ $# -gt 0 ]]; then
 [[ $MODE == --dry-run && $# -eq 2 && $1 == --ruling ]] || { echo 'usage: wt_remove_20261017.sh [--dry-run [--ruling placeholder.json]|--execute]' >&2; exit 2; }
 RULING=$2
fi
MAIN=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck
PAD=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad
mkdir -p "$PAD"
LOG=$(mktemp "$PAD/wt_remove_$(date -u +%Y%m%dT%H%M%SZ).XXXXXX")
printf 'LOG %s\n' "$LOG"
exec >> "$LOG" 2>&1
printf 'MODE %s LOG %s\n' "$MODE" "$LOG"
python3 - "$MAIN" "$MODE" "$RULING" <<'PY_HELPER'
import datetime, hashlib, json, os, pathlib, re, shutil, subprocess, sys
NAMES='align l1 l1f l1r l1r2 l1r3 r0 s8'.split()
def require(ok,message):
    if not ok: raise RuntimeError(message)
def git(root,*args):
    return subprocess.check_output(['git','-c','core.hooksPath=/dev/null','-C',str(root),*args])
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def inventory(root):
    result=[]
    for ignored in (False,True):
        args=['ls-files','--others','--exclude-standard','-z']
        if ignored: args.insert(2,'--ignored')
        for name in git(root,*args).split(b'\0'):
            if name:
                rel=os.fsdecode(name); p=root/rel
                result.append(dict(path=rel,bytes=p.lstat().st_size,symlink=p.is_symlink(),cache=any(x in ('__pycache__','.pytest_cache') for x in pathlib.Path(rel).parts)))
    return sorted(result,key=lambda x:x['path'])
def processes(root):
    r=subprocess.run(['lsof','-a','-d','cwd','-Fpcn'],capture_output=True,text=True)
    require(r.returncode in (0,1) and not r.stderr,'cannot inventory process cwd: '+r.stderr)
    for line in r.stdout.splitlines():
        if line.startswith('n'):
            cwd=pathlib.Path(line[1:]).resolve()
            require(cwd!=root and root not in cwd.parents,'running process cwd: '+str(cwd))
def guard(main,row,ruling):
    root=pathlib.Path(row['path'])
    require(row['name'] in [main.name+'-'+n for n in NAMES],'outside candidate allowlist')
    require(root==main.parent/row['name'] and root.resolve()==root and not root.is_symlink(),'unsafe worktree path')
    require((root/'.git').is_file(),'not a linked worktree')
    require(git(root,'rev-parse','--path-format=absolute','--git-common-dir')==git(main,'rev-parse','--path-format=absolute','--git-common-dir'),'different repository')
    records=git(main,'worktree','list','--porcelain').decode().split('\n\n')
    require(any(('worktree '+str(root)) in b.splitlines() for b in records),'unregistered worktree')
    require(git(root,'rev-parse','HEAD').decode().strip()==row['tip']==ruling['tip'],'tip drift')
    require(git(root,'symbolic-ref','--short','HEAD').decode().strip()==row['branch']==ruling['branch'],'branch drift')
    r=subprocess.run(['git','-C',str(main),'merge-base','--is-ancestor',row['tip'],'opus/spellcheck'])
    require(r.returncode==0,'not merged')
    require(not git(root,'status','--porcelain','--untracked-files=no'),'tracked modifications')
    processes(root)
    expected=sorted(row['untracked']+row['ignored'],key=lambda x:x['path'])
    require(inventory(root)==expected,'untracked/ignored inventory drift; refresh census')
    return root

def custody(main,root,row,execute):
    dest=main/'artifacts/worktree_custody'/row['name']
    require(not dest.exists(),'custody destination exists; inspect it, do not overwrite')
    files=[x for x in row['untracked']+row['ignored'] if not x['cache']]
    manifest=[]
    for item in files:
        rel=pathlib.Path(item['path']); src=root/rel
        require(not rel.is_absolute() and '..' not in rel.parts,'unsafe relative path')
        require(src.parent.resolve().is_relative_to(root),'symlinked source parent')
        require(src.is_file() or src.is_symlink(),'custody source is not a regular file or symlink')
        if src.is_symlink():
            link=os.readlink(src)
            manifest.append(dict(path=str(rel),bytes=src.lstat().st_size,type='symlink',target=link,sha256=hashlib.sha256(os.fsencode(link)).hexdigest()))
        else:
            manifest.append(dict(path=str(rel),bytes=src.stat().st_size,type='file',sha256=sha(src)))
    print('CUSTODY',len(files),'files ->',dest,flush=True)
    if execute:
        dest.mkdir(parents=True,exist_ok=False)
        for item in manifest:
            src=root/item['path']; target=dest/item['path']
            target.parent.mkdir(parents=True,exist_ok=True)
            if item['type']=='symlink':
                require(os.readlink(src)==item['target'],'source symlink drift')
                target.symlink_to(item['target'])
                require(hashlib.sha256(os.fsencode(os.readlink(target))).hexdigest()==item['sha256'],'custody link sha mismatch')
            else:
                shutil.copy2(src,target)
                require(sha(src)==item['sha256']==sha(target),'custody sha mismatch')
        receipt=dest.parent/(row['name']+'.sha256.json')
        require(not receipt.exists(),'custody manifest already exists')
        with receipt.open('x') as f: json.dump(dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=manifest,excluded_caches=row['cache_exclusions']),f,indent=2)
        print('VERIFIED manifest',receipt,flush=True)
    # Originals deliberately remain. Git decides whether removal is clean.

def repointed(main,row,census):
    for hit in row['citations']:
        require(bool(hit['targets']),'citation has no verifiable file target: '+hit['file'])
        text=pathlib.Path(hit['file']).read_text()
        for target in hit['targets']:
            require(target['byte_identical'] and target['sha256'],'no byte-identical replacement: '+target['old'])
            dest=pathlib.Path(target['replacement'])
            require(dest.is_file() and sha(dest)==target['sha256'],'replacement bytes drift')
            require(target['old'] not in text and str(dest) in text,'citation not repointed: '+hit['file'])
    # Re-scan the entire original scope, including newly added citations. WT1 audit
    # artifacts are historical evidence, never runtime dependencies.
    cmd=['rg','-l','-I','--hidden','--no-ignore','-g','!.git','-g','!__pycache__','-g','!.pytest_cache','-g','!**/artifacts/wt1/**','-g','!WT1_CENSUS.md','-g','!WT1_RULING.json','-e',re.escape(row['path'])+r"(/|[\s\"'`:,;\]\)}]|$)", '-e',re.escape('~/Projects/'+row['name'])+r"(/|[\s\"'`:,;\]\)}]|$)",*census['citation_roots']]
    r=subprocess.run(cmd,capture_output=True,text=True)
    require(r.returncode==1 and not r.stderr,'remaining citations or scan failure: '+r.stdout+r.stderr)

def run(main,mode,ruling_path=None):
    main=pathlib.Path(main)
    require(not ruling_path or mode=='--dry-run','alternate ruling allowed only in dry-run')
    ruling=json.loads((pathlib.Path(ruling_path) if ruling_path else main/'docs/reviews/harness/WT1_RULING.json').read_text())
    census_path=main/'artifacts/wt1/census.json'
    require(ruling['census_sha256']==sha(census_path),'census hash differs from ruling')
    census=json.loads(census_path.read_text())
    require(git(main,'symbolic-ref','--short','HEAD').decode().strip()=='opus/spellcheck','main branch changed')
    require(git(main,'rev-parse','opus/spellcheck').decode().strip()==ruling['main_tip']==census['main_tip'],'main tip drift')
    rows={r['name']:r for r in census['candidates']}; seen=set()
    for decision in ruling['worktrees']:
        name=decision['name']; require(name not in seen,'duplicate ruling'); seen.add(name)
        require(name in rows,'unknown worktree')
        require(decision['action'] in ('KEEP','REMOVE'),'invalid action')
        if decision['action']=='KEEP': print('KEEP',name); continue
        row=rows[name]; require('KEEP' not in row['proposal'],'census says KEEP')
        root=guard(main,row,decision)
        needs_custody=bool([x for x in row['untracked']+row['ignored'] if not x['cache']])
        require(decision.get('custody',False)==needs_custody,'custody ruling mismatch')
        require(decision.get('repoint',False)==bool(row['citations']),'repoint ruling mismatch')
        if needs_custody: custody(main,root,row,mode=='--execute')
        repointed(main,row,census)
        print('CMD git worktree remove',str(root),flush=True)
        if mode=='--execute':
            # Revalidate after copying; a refusal terminates without retry.
            guard(main,row,decision)
            subprocess.run(['git','-c','core.hooksPath=/dev/null','-C',str(main),'worktree','remove',str(root)],check=True)
    print('DONE',mode,flush=True)
if __name__=='__main__': run(sys.argv[1],sys.argv[2],sys.argv[3] or None)
PY_HELPER
