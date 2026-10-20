"""Static input-site review; no source or git writes. Used by build_v2.py."""
import ast
from pathlib import Path
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[3]
LIVE = ('greekocr', 'scripts', 'tests', 'worker', 'prototypes')
READ_NAMES = {'read', 'rows', 'read_jsonl', 'read_rows', 'load', 'load_json', 'load_jsonl', 'load_rows', 'sha', 'sha256', 'file_sha256', 'truth_lines', 'bind', 'read_gzip', 'json_rows', 'load_locks', 'read_lines'}
LOCAL_NAME = None
LOCAL_DEFS = {}
METHODS = {'read_text','read_bytes','exists','is_file','stat'}

@lru_cache(None)
def parsed(name):
    path=ROOT/name
    try: text=path.read_text(); tree=ast.parse(text)
    except (SyntaxError, UnicodeError, OSError): return None
    defs={}; imports={}
    # Module bindings only: local path names must not leak into other functions.
    for node in tree.body:
        if isinstance(node,(ast.Assign,ast.AnnAssign)):
            for target in node.targets if isinstance(node,ast.Assign) else [node.target]:
                if isinstance(target,ast.Name): defs[target.id]=node.value
        if isinstance(node,ast.ImportFrom) and node.module:
            for alias in node.names:
                module=node.module.replace('.','/')+'/'+alias.name+'.py'
                if (ROOT/module).is_file(): imports[alias.asname or alias.name]=(module,None)
                else: imports[alias.asname or alias.name]=(node.module.replace('.','/')+'.py',alias.name)
        if isinstance(node,ast.Import):
            for alias in node.names:
                if alias.asname: imports[alias.asname]=(alias.name.replace('.','/')+'.py',None)
    return text,tree,defs,imports

def values(node,name,seen=frozenset()):
    if node is None or len(seen)>24:return set()
    if isinstance(node,ast.Constant) and isinstance(node.value,(str,int)):return {node.value}
    if isinstance(node,ast.Name):
        if node.id=='__file__':return {str(ROOT/name)}
        local_key=(name,node.id,'local')
        if name==LOCAL_NAME and node.id in LOCAL_DEFS and local_key not in seen:
            return values(LOCAL_DEFS[node.id],name,seen|{local_key})
        key=(name,node.id)
        if key in seen:return set()
        data=parsed(name)
        if not data:return set()
        if node.id in data[2]:return values(data[2][node.id],name,seen|{key})
        if node.id in data[3] and data[3][node.id][1]:
            mod,var=data[3][node.id];return values(ast.Name(id=var),mod,seen|{key})
    if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Div,ast.Add)):
        a,b=values(node.left,name,seen),values(node.right,name,seen)
        if len(a)*len(b)>200:return set()
        try:return {str(Path(x)/str(y)) if isinstance(node.op,ast.Div) else x+y for x in a for y in b}
        except TypeError:return set()
    if isinstance(node,ast.Attribute):
        if isinstance(node.value,ast.Name):
            d=parsed(name)
            if d and node.value.id in d[3]:
                mod,var=d[3][node.value.id]
                if var is None:return values(ast.Name(id=node.attr),mod,seen)
        if node.attr=='parent':return {str(Path(x).parent) for x in values(node.value,name,seen)}
    if isinstance(node,ast.Subscript) and isinstance(node.value,ast.Attribute) and node.value.attr=='parents':
        ns=values(node.slice,name,seen)
        return {str(Path(x).parents[n]) for x in values(node.value.value,name,seen) for n in ns if isinstance(n,int) and n<len(Path(x).parents)}
    if isinstance(node,ast.Call):
        f=node.func
        if isinstance(f,ast.Name) and f.id in {'Path','str','_data_input','input_path'} and node.args:return values(node.args[0],name,seen)
        if isinstance(f,ast.Attribute):
            if f.attr in {'Path'} and node.args:return values(node.args[0],name,seen)
            if f.attr in {'resolve','absolute'}:return values(f.value,name,seen)
            if f.attr=='home':return {str(Path.home())}
            if f.attr=='with_name' and node.args:
                return {str(Path(x).with_name(y)) for x in values(f.value,name,seen) for y in values(node.args[0],name,seen) if isinstance(y,str) and '/' not in y}
    if isinstance(node,(ast.List,ast.Tuple,ast.Set)):
        return set().union(*(values(x,name,seen) for x in node.elts))
    return set()

def input_arg(node):
    if not isinstance(node,ast.Call):return None
    f=node.func
    if isinstance(f,ast.Attribute) and f.attr in METHODS:return f.value
    fn=f.id if isinstance(f,ast.Name) else f.attr if isinstance(f,ast.Attribute) else ''
    if fn=='open':
        receiver = isinstance(f,ast.Attribute) and not (isinstance(f.value,ast.Name) and f.value.id in {'gzip','Image','io','np','numpy','tarfile','zipfile'})
        mode_index=0 if receiver else 1
        mode=node.args[mode_index] if len(node.args)>mode_index else next((x.value for x in node.keywords if x.arg=='mode'),None)
        if mode is not None and (not isinstance(mode,ast.Constant) or not isinstance(mode.value,str) or any(c in mode.value for c in 'wax+')):return None
        if receiver:return f.value
        return node.args[0] if node.args else None
    if fn in READ_NAMES or fn in {'imread','loadtxt','genfromtxt'}:return node.args[0] if node.args else None
    return None

def scan(inventory):
    global LOCAL_NAME,LOCAL_DEFS
    sites=[]
    for prefix in LIVE:
        for p in sorted((ROOT/prefix).rglob('*.py')):
            if p.is_symlink() or any(x in {'.git','__pycache__','.venv','node_modules'} for x in p.parts):continue
            name=p.relative_to(ROOT).as_posix();d=parsed(name)
            if not d:continue
            text,tree,_,_=d
            parents={child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
            for node in ast.walk(tree):
                arg=input_arg(node)
                if arg is None:continue
                LOCAL_NAME=name;LOCAL_DEFS={}
                ancestor=node
                while ancestor in parents:
                    ancestor=parents[ancestor]
                    if isinstance(ancestor,(ast.FunctionDef,ast.AsyncFunctionDef)):
                        assigns=sorted((n for n in ast.walk(ancestor) if isinstance(n,(ast.Assign,ast.AnnAssign)) and n.lineno<node.lineno),key=lambda n:n.lineno)
                        for assign in assigns:
                            for target in assign.targets if isinstance(assign,ast.Assign) else [assign.target]:
                                if isinstance(target,ast.Name):LOCAL_DEFS[target.id]=assign.value
                        break
                hits=set()
                for v in values(arg,name):
                    if not isinstance(v,str):continue
                    q=Path(v)
                    if q.is_absolute():
                        try:v=q.relative_to(ROOT).as_posix()
                        except ValueError:continue
                    if v in inventory:hits.add(v)
                if hits:sites.append(dict(reader=name,line=node.lineno,paths=sorted(hits),expression=ast.get_source_segment(text,arg),start=[arg.lineno,arg.col_offset],end=[arg.end_lineno,arg.end_col_offset]))
    return sites

if __name__=='__main__':
    import csv,json
    csv.field_size_limit(100_000_000)
    rows={r['path']:r for r in csv.DictReader((ROOT/'docs/cleanup_20261019/data_out/MOVE_PLAN.tsv').open(),delimiter='\t')}
    sites=scan(rows)
    out=ROOT/'docs/cleanup_20261019/data_out/static_inputs_extra_v2.json';out.write_text(json.dumps(sites,indent=2)+'\n')
    print(len(sites),'static input sites',len({s['reader'] for s in sites}),'files')
