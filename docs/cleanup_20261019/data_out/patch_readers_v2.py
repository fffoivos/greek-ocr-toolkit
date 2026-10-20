"""Apply narrow input adapters; never edits existing tests or historical docs.

The saved patch and per-site report make this run's exact source edits reviewable.
"""
import ast,collections,csv,difflib,json
from pathlib import Path
from scan_live_v2 import parsed, input_arg, READ_NAMES
O=Path(__file__).resolve().parent;R=O.parents[2]
csv.field_size_limit(100_000_000)
rows=list(csv.DictReader((O/'MOVE_PLAN_v2.tsv').open(),delimiter='\t'))
move={r['path']:r for r in rows if r['decision']=='MOVE'}
refs=collections.defaultdict(set)
for p,r in move.items():
    if Path(p).name in {'docs','artifacts'}:continue
    for reader in r['readers'].split('; '):
        if reader.startswith(('greekocr/','scripts/','tests/','worker/','prototypes/')) and reader.endswith('.py') and (R/reader).is_file():refs[reader].add(p)
sites=json.loads((O/'static_inputs_v2.json').read_text())
for s in sites:
    if any(p in move for p in s['paths']):refs[s['reader']].update(p for p in s['paths'] if p in move)
# Providers of imported JSONL/hash readers also require the adapter: generic
# loaders need not themselves contain the filename literal used by their callers.
providers=set(refs)
for name in list(refs):
    d=parsed(name)
    if d:
        for alias,(mod,var) in d[3].items():
            if var in READ_NAMES and (R/mod).is_file() and mod.startswith(('greekocr/','scripts/','worker/','prototypes/')):providers.add(mod)
loader_names=READ_NAMES|{'_read_jsonl','read_json','_read','_rows','file_hash','digest','sha_file','_sha'}
patches=collections.defaultdict(list);loaders={};details=[]
# Add the adapter at the low-level read inside reusable loader functions.
for name in sorted(providers):
    if name.startswith('tests/'):continue
    d=parsed(name)
    if not d:continue
    text,tree,_,_=d
    for fn in tree.body:
        if not isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef)) or fn.name not in loader_names:continue
        low=[]
        for node in ast.walk(fn):
            if not isinstance(node,ast.Call):continue
            arg=input_arg(node)
            # Conditional gzip.open/open is a common compact loader idiom.
            if isinstance(node.func,ast.IfExp) and node.args:
                mode=node.args[1] if len(node.args)>1 else None
                if isinstance(mode,ast.Constant) and isinstance(mode.value,str) and mode.value.startswith('r'):arg=node.args[0]
            if arg is None:continue
            f=node.func
            # Do not wrap custom readers here, only actual filesystem readers.
            method=f.attr if isinstance(f,ast.Attribute) else f.id if isinstance(f,ast.Name) else ''
            if method not in {'open','read_text','read_bytes','load','imread'} and not isinstance(f,ast.IfExp):continue
            low.append(arg)
        if low:
            loaders[(name,fn.name)]=True
            for arg in low:
                patches[name].append((arg.lineno,arg.col_offset,arg.end_lineno,arg.end_col_offset))
                details.append(dict(reader=name,line=arg.lineno,mode='shared input loader',function=fn.name,paths=sorted(refs.get(name,[]))))
# Static inputs that are not already handled by a patched local/imported loader.
for site in sites:
    paths=[p for p in site['paths'] if p in move]
    name=site['reader']
    if not paths:continue
    d=parsed(name);text,tree,_,imports=d
    parent_call=None
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and node.lineno==site['line']:
            arg=input_arg(node)
            if arg is not None and [arg.lineno,arg.col_offset]==site['start'] and [arg.end_lineno,arg.end_col_offset]==site['end']:parent_call=node;break
    provider=None
    if parent_call:
        f=parent_call.func
        if isinstance(f,ast.Name):
            provider=(name,f.id)
            if f.id in imports and imports[f.id][1]:provider=imports[f.id]
        elif isinstance(f,ast.Attribute) and isinstance(f.value,ast.Name) and f.value.id in imports:
            mod,var=imports[f.value.id]
            if var is None:provider=(mod,f.attr)
    covered=provider in loaders
    details.append(dict(reader=name,line=site['line'],mode='existing tests: CLEAN4T handoff' if name.startswith('tests/') else 'shared loader' if covered else 'direct input',paths=paths,provider=provider))
    if not covered:patches[name].append((*site['start'],*site['end']))
# Explicit CLI input reads and the geometry cache's dynamic file names.
manual={
 'greekocr/labelfix/spellcheck_validate.py':[('a.samples=a.samples.resolve()','a.samples=_data_input(a.samples).resolve()')],
}
geo='greekocr/harvest/geometry_observations.py'
text=parsed(geo)[0]
for node in ast.walk(parsed(geo)[1]):
    if not isinstance(node,ast.Call):continue
    arg=input_arg(node)
    if arg is not None:
        snippet=ast.get_source_segment(text,arg)
        if snippet in {"cache/'detector.json.gz'","cache/'ink.png'","cache/'labels.npz'"}:
            patches[geo].append((arg.lineno,arg.col_offset,arg.end_lineno,arg.end_col_offset))
# Byte offsets from AST use UTF-8 columns, not Python Unicode columns.
def offset(lines,line,column):return sum(len(s.encode()) for s in lines[:line-1])+column
changes=[];test_diffs=[]
for name in sorted(set(patches)|set(manual)):
    original=(R/name).read_text();data=original.encode();lines=original.splitlines(keepends=True)
    ranges=sorted({(offset(lines,a,b),offset(lines,c,d)) for a,b,c,d in patches[name]})
    # If both a call and its argument were selected, the outer adapter suffices.
    ranges=[(a,b) for a,b in ranges if not any(c<=a and b<=d and (a,b)!=(c,d) for c,d in ranges)]
    for a,b in reversed(ranges):data=data[:a]+b'_data_input('+data[a:b]+b')'+data[b:]
    new=data.decode()
    for old,replacement in manual.get(name,[]):
        assert new.count(old)==1,(name,old);new=new.replace(old,replacement)
    if new==original:continue
    tree=ast.parse(new);insert=0
    if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str):insert=tree.body[0].end_lineno
    for node in tree.body:
        if isinstance(node,ast.ImportFrom) and node.module=='__future__':insert=node.end_lineno
    newlines=new.splitlines(keepends=True)
    # Preserve standalone shebang/encoding before the import.
    if insert==0:
        while insert<len(newlines) and (newlines[insert].startswith('#') or not newlines[insert].strip()):insert+=1
    newlines.insert(insert,'from greekocr.ops.data_root import input_path as _data_input\n')
    new=''.join(newlines);ast.parse(new)
    diff=''.join(difflib.unified_diff(original.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    if name.startswith('tests/'):
        test_diffs.append(diff)
    else:
        (R/name).write_text(new);changes.append(dict(path=name,bytes=len(new.encode()),input_sites=len(ranges),sha256_before=__import__('hashlib').sha256(original.encode()).hexdigest(),sha256_after=__import__('hashlib').sha256(new.encode()).hexdigest()))
        (O/'reader_before_v2').mkdir(exist_ok=True)
        backup=O/'reader_before_v2'/name;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_text(original)
        changes[-1]['diff']=diff
(O/'LIVE_READER_PATCHES_v2.diff').write_text(''.join(x.pop('diff') for x in changes))
(O/'CLEAN4T_READER_HANDOFF_v2.diff').write_text(''.join(test_diffs))
(O/'reader_changes_v2.json').write_text(json.dumps(changes,indent=2)+'\n')
(O/'reader_sites_v2.json').write_text(json.dumps(details,indent=2)+'\n')
print('patched',len(changes),'source files; tests handoff',len(test_diffs),'files; source input sites',sum(x['input_sites'] for x in changes))
