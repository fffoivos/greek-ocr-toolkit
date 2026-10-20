"""Patch extra static input sites found through function-local path bindings."""
import ast,collections,csv,difflib,hashlib,json
from pathlib import Path
from scan_live_v2 import input_arg,parsed
O=Path(__file__).resolve().parent;R=O.parents[2]
csv.field_size_limit(100_000_000)
move={r['path'] for r in csv.DictReader((O/'MOVE_PLAN_v2.tsv').open(),delimiter='\t') if r['decision']=='MOVE'}
changes=json.loads((O/'reader_changes_v2.json').read_text());by={c['path']:c for c in changes};details=json.loads((O/'reader_sites_v2.json').read_text())
loaders={(d['reader'],d['function']) for d in details if d['mode']=='shared input loader'}
extra=json.loads((O/'extra_input_review_v2.json').read_text());patches=collections.defaultdict(set)
for s in extra:
    paths=[p for p in s['paths'] if p in move]
    if not paths:continue
    name=s['reader'];d=parsed(name);text,tree,_,imports=d
    node=next((n for n in ast.walk(tree) if isinstance(n,ast.Call) and n.lineno==s['line'] and input_arg(n) is not None and [input_arg(n).lineno,input_arg(n).col_offset]==s['start'] and [input_arg(n).end_lineno,input_arg(n).end_col_offset]==s['end']),None)
    provider=None
    if node:
        f=node.func
        if isinstance(f,ast.Name):provider=imports.get(f.id,(name,f.id))
        elif isinstance(f,ast.Attribute) and isinstance(f.value,ast.Name) and f.value.id in imports:
            mod,var=imports[f.value.id]
            if var is None:provider=(mod,f.attr)
    covered=provider in loaders
    details.append(dict(reader=name,line=s['line'],mode='extra shared loader' if covered else 'extra tests handoff' if name.startswith('tests/') else 'extra direct input',paths=paths,provider=provider))
    if not covered:patches[name].add((*s['start'],*s['end']))
new_test=[]
for name,ranges in sorted(patches.items()):
    original=(R/name).read_text();lines=original.splitlines(True);data=original.encode()
    def off(a,b):return sum(len(l.encode()) for l in lines[:a-1])+b
    offsets={(off(a,b),off(c,d)) for a,b,c,d in ranges}
    offsets=[(a,b) for a,b in offsets if not any(c<=a and b<=d and (a,b)!=(c,d) for c,d in offsets)]
    for a,b in sorted(offsets,reverse=True):data=data[:a]+b'_data_input('+data[a:b]+b')'+data[b:]
    new=data.decode();imp='from greekocr.ops.data_root import input_path as _data_input\n'
    if imp not in new:
        tree=ast.parse(new);insert=0
        if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str):insert=tree.body[0].end_lineno
        for n in tree.body:
            if isinstance(n,ast.ImportFrom) and n.module=='__future__':insert=n.end_lineno
            if n.lineno<100 and not isinstance(n,(ast.FunctionDef,ast.ClassDef)) and any(isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and c.func.attr in {'append','insert'} and ast.unparse(c.func.value)=='sys.path' for c in ast.walk(n)):insert=max(insert,n.end_lineno)
        nl=new.splitlines(True)
        if insert==0:
            while insert<len(nl) and (nl[insert].startswith('#') or not nl[insert].strip()):insert+=1
        nl.insert(insert,imp);new=''.join(nl)
    ast.parse(new)
    if name.startswith('tests/'):
        new_test.append(''.join(difflib.unified_diff(original.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name)))
    else:
        if name not in by:
            backup=O/'reader_before_v2'/name;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_text(original)
            c=dict(path=name,bytes=0,input_sites=0,sha256_before=hashlib.sha256(original.encode()).hexdigest(),sha256_after='');changes.append(c);by[name]=c
        by[name]['input_sites']+=len(offsets)
        (R/name).write_text(new)
with (O/'CLEAN4T_READER_HANDOFF_v2.diff').open('a') as f:f.write(''.join(new_test))
for c in changes:
    p=R/c['path'];c['bytes']=p.stat().st_size;c['sha256_after']=hashlib.sha256(p.read_bytes()).hexdigest()
(O/'reader_changes_v2.json').write_text(json.dumps(changes,indent=2)+'\n');(O/'reader_sites_v2.json').write_text(json.dumps(details,indent=2)+'\n')
diffs=[]
for c in changes:
    old=(O/'reader_before_v2'/c['path']).read_text();new=(R/c['path']).read_text();diffs.append(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+c['path'],tofile='b/'+c['path'])))
(O/'LIVE_READER_PATCHES_v2.diff').write_text(''.join(diffs))
print('total patched source files',len(changes),'extra test diff sections',len(new_test))
